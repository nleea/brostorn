---
project: fitness-app
tags:
  - fitness-app
  - docs
  - backend
  - fastapi
---

# FastAPI Backend

## Estructura principal
- `main.py`: arranque, CORS, routers y lifespan.
- `scheduler.py`: jobs mensuales.
- `models/`: entidades SQLModel.
- `schemas/`: contratos request/response.
- `routers/`: endpoints.
- `services/`: lógica de negocio.
- `repositories/`: contratos e implementaciones.

## Routers principales
- `/auth`
- `/clients`
- `/training-plans`
- `/nutrition-plans`
- `/training-logs`
- `/meal-logs`
- `/metrics`
- `/attendance`

## Características
- Async end-to-end con `AsyncSession`.
- JWT con access/refresh tokens.
- Sesiones persistidas por dispositivo.
