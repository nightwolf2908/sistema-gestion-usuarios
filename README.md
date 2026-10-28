# UserHub

**UserHub** es una aplicación web para el registro, autenticación y consulta de usuarios. Se desarrolló como proyecto académico y se ejecuta mediante contenedores Docker, con una arquitectura que separa frontend, API, base de datos y servicios de monitoreo. (Se agrego una segunda rama donde poder probar mas funcionalidades, y en un futuro hacer un merge con pull request)

## Funcionalidades

- Registro de usuarios mediante formulario web.
- Inicio de sesión con autenticación JWT.
- Consulta de usuarios registrados para sesiones autenticadas.
- Almacenamiento persistente de usuarios en PostgreSQL.
- Contraseñas protegidas mediante hash Argon2.
- Métricas HTTP y panel de monitoreo.

> **Alcance de seguridad:** esta versión es una demostración académica para uso local. Antes de publicarla en Internet se deben revisar los permisos de consulta de usuarios, la exposición de servicios, HTTPS y la gestión de secretos.

## Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | React, TypeScript, Vite, Nginx |
| Backend | Python, FastAPI, SQLAlchemy |
| Base de datos | PostgreSQL 17 |
| Caché | Redis 7 |
| Migraciones | Alembic |
| Autenticación | JWT y Argon2 |
| Contenedores | Docker y Docker Compose |
| Proxy inverso | Traefik |
| Métricas | Prometheus |
| Dashboards | Grafana |
| Github Actions | 

## Arquitectura

```text
Navegador
   |
   v
Traefik (http://userhub.localhost)
   |
   v
Nginx + React
   |
   +-- /api/ --> FastAPI --> PostgreSQL
                       |--> Redis
                       |--> /metrics
                               |
                               v
                           Prometheus --> Grafana
```

## Requisitos

- Docker Engine y Docker Compose.
- Git para clonar el repositorio.
- Un archivo `.env` con las variables de configuración que utiliza `docker-compose.yaml`.

## Instalación local

1. Clona el repositorio y entra en su carpeta:

   ```bash
   git clone https://
   cd userhub
   ```

2. Configura el archivo `.env` con las variables requeridas por `docker-compose.yaml` y el backend, checa .env.example, puedes generar contraseñas con openssl rand -hex 64. Para Grafana, incluye `GRAFANA_ADMIN_PASSWORD` con una contraseña segura.

3. Comprueba la configuración e inicia los servicios:

   ```bash
   docker compose config --quiet
   docker compose up -d --build
   ```

4. Comprueba el estado:

   ```bash
   docker compose ps
   ```

> Si tu entorno no resuelve automáticamente `userhub.localhost`, revisa la resolución local de ese nombre. Los puertos publicados en `127.0.0.1` solo son accesibles desde la propia computadora. Tambien, espera un minuto a que los contenedores se levanten del todo.

## Accesos locales

| Servicio | Dirección |
| --- | --- |
| Aplicación web mediante Traefik | http://userhub.localhost |
| Frontend directo | http://127.0.0.1:8080 |
| API directa | http://127.0.0.1:8000 |
| Métricas de FastAPI | http://127.0.0.1:8000/metrics |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |
> Para acceder a grafana pones admin y tu contraseña que pusiste en el archivo .env.
## API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/api/v1/users` | Registrar un usuario |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener un token |
| `GET` | `/api/v1/users` | Consultar usuarios (requiere JWT) |
| `GET` | `/api/v1/users/{id}` | Consultar un usuario (requiere JWT) |
| `GET` | `/metrics` | Métricas para Prometheus |

## Monitoreo

Prometheus consulta `backend:8000/metrics` cada 15 segundos mediante la red interna de Docker. En Grafana se creó el dashboard **Userhub -API Monitoring**, con estos paneles:

- Solicitudes HTTP por segundo.
- Respuestas HTTP 4xx y 5xx.
- Latencia HTTP P95.

**Estado actual:** el dashboard se creó desde la interfaz de Grafana y se exportó a `monitoring/grafana/dashboards/userhub-dashboard.json`. Su aprovisionamiento automático quedó pendiente; en una instalación nueva puede ser necesario importar el JSON y configurar la fuente de datos Prometheus (`http://prometheus:9090`) desde Grafana.

## Migraciones de base de datos

El proyecto utiliza Alembic para administrar el esquema de la base de datos:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
```

No ejecutes comandos que eliminen volúmenes si deseas conservar los usuarios registrados y los datos de monitoreo.

## GitHub Actions

El flujo `.github/workflows/ci.yml` se ejecuta en cada `push` y *pull request* y comprueba que los archivos Python del backend no tengan errores de sintaxis. Es una verificación básica: **no sustituye pruebas unitarias ni de integración**.

## Estructura principal

```text
userhub/
├── backend/
│   ├── app/
│   └── alembic/
├── frontend/
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
│           └── userhub-dashboard.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yaml
└── README.md
```

## Pendientes y mejoras futuras

- Aprovisionar automáticamente Grafana y su fuente de datos.
- Incorporar pruebas automatizadas del backend y frontend.
- Revisar autorización y privacidad en la consulta de usuarios.
- Preparar HTTPS y controles de seguridad para un despliegue público.
- Elaborar el informe académico y el video demostrativo del proyecto.

## Propósito

Proyecto académico orientado a demostrar el desarrollo de una aplicación web funcional y la integración de herramientas de contenedorización, proxy inverso y observabilidad.
