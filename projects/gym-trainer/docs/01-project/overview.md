---
project: fitness-app
tags:
  - fitness-app
  - docs
  - project
  - overview
---

# My Gym Trainer — Overview

Aplicación de entrenamiento personal con dos piezas principales:
- `gym-trainer-client`: frontend web en Vue 3 + Pinia + Vite.
- `trainerGM/backend`: API FastAPI con PostgreSQL.

## Roles
- `trainer`: gestiona clientes, planes, reportes y evidencias.
- `client`: sigue planes, registra entrenamientos, nutrición, métricas y check-ins.

## Estado actual
- Backend funcional con patrón `router -> service -> repository`.
- Frontend funcional por roles con navegación protegida.
- Integraciones activas con ExerciseDB, Cloudflare R2 y reportes PDF.
- Existen restos legacy como `metricts` y `data.ts`.

## Stack
- Frontend: Vue 3, TypeScript, Pinia, Vue Router, Vite, PWA.
- Backend: FastAPI, SQLModel, SQLAlchemy async, asyncpg, Alembic.
- Infraestructura: PostgreSQL 16, Cloudflare R2, Docker Compose.

## Related
- [[02-architecture/system-overview]]
- [[03-backend/index]]
- [[04-frontend/index]]
- [[10-deployment/docker]]
