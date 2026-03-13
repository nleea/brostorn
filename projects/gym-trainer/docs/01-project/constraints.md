---
project: fitness-app
tags:
  - fitness-app
  - docs
  - project
  - constraints
---

# Project Constraints

## Infraestructura
- El despliegue objetivo corre en Orange Pi 5 ARM64.
- El stack debe seguir siendo compatible con Docker Compose.
- PostgreSQL 16 y Cloudflare R2 son piezas actuales del sistema.

## Backend
- API async basada en FastAPI.
- Persistencia con SQLModel + SQLAlchemy async.

## Frontend
- Vue 3 + Pinia + Vue Router.
- `hash history` para navegación actual.

## Legado
- Hay naming inconsistente (`metricts`, `nutritionplan`, `metricsrepo`).
- Existen flujos legacy en `data.ts`.
- La refactorización debe ser gradual para no romper compatibilidad.
