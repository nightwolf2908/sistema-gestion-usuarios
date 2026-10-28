import json
import os
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Security

from .schemas import UserLogin, TokenResponse
from .security import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
)

import redis
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User
from .schemas import UserCreate, UserResponse


cache = redis.Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
)

CACHE_KEY = "users:list"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización temporal para esta primera versión.
    # Después utilizaremos migraciones con Alembic.
    Base.metadata.create_all(bind=engine)
    yield
    cache.close()
    engine.dispose()


app = FastAPI(
    title="UserHub API",
    description="API REST para gestión de usuarios",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        cache.ping()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable",
        )

    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
    }


@app.post(
    "/api/v1/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    user = User(
        name=payload.name.strip(),
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    db.refresh(user)

    # Invalidar caché tras registrar un usuario.
    try:
        cache.delete(CACHE_KEY)
    except redis.RedisError:
        pass

    return user


@app.get(
    "/api/v1/users",
    response_model=list[UserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
    ):
    try:
        cached = cache.get(CACHE_KEY)
        if cached:
            return json.loads(cached)
    except redis.RedisError:
        pass

    users = db.scalars(
        select(User).order_by(User.id.desc()).limit(100)
    ).all()

    result = [
        UserResponse.model_validate(user).model_dump(
            mode="json"
        )
        for user in users
    ]

    try:
        cache.setex(
            CACHE_KEY,
            60,
            json.dumps(result),
        )
    except redis.RedisError:
        pass

    return result


@app.get(
    "/api/v1/users/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.email == str(credentials.email).lower()
        )
    )

    if user is None or not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)

    return TokenResponse(access_token=token)
