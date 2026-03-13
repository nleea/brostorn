---
project: fitness-app
tags:
  - fitness-app
  - docs
  - patterns
  - async-patterns
---

# Async Patterns

## Backend
- FastAPI async.
- SQLAlchemy async con `AsyncSession`.
- Acceso Postgres mediante `asyncpg`.

## Frontend
- Fetch centralizado en `vue/api.ts`.
- Refresh coordinado para evitar carreras entre pestañas.

## Scheduler
- Tareas diferidas con `APScheduler`, no con cola distribuida documentada.
