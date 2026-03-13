---
project: fitness-app
tags:
  - fitness-app
  - docs
  - debugging
  - db-deadlock
---

# DB Deadlock

## Sospechas iniciales
- Upserts concurrentes sobre las mismas claves lógicas.
- Operaciones de sesión concurrentes en auth.
- Migraciones a medio aplicar.

## Revisar
- consultas por `client_id + date`
- locks transaccionales
- índices faltantes
- estado de Alembic
