---
project: fitness-app
tags:
  - fitness-app
  - docs
  - database
  - migrations
---

# Migrations

## Herramienta
- Alembic.

## Secuencia observada
- `001` esquema inicial.
- `002` ejercicios y ajustes de training logs.
- `003` expansión de métricas.
- `004` macros de nutrición.
- `005` user configs.
- `006` weekly checkins.
- `007` catálogo ExerciseDB y favoritos.
- `008` template/copy plans.
- `009` evidencias.
- `010` unificación de evidencias.
- `011` reportes mensuales.
- `012` `user_sessions`.

## Comandos
```bash
alembic upgrade head
alembic current
alembic history
```
