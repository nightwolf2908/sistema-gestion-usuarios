import json
import os
from contextlib import asynccontextmanager

import redis
from fastapi import Depends, FastAPI, HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User
from .schemas import UserCreate, UserResponse

password_hasher = PasswordHash.recommended()

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
        password_hash=password_hasher.hash(
            payload.password
        ),
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
def list_users(db: Session = Depends(get_db)):
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
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
