---
project: fitness-app
tags:
  - fitness-app
  - docs
  - database
  - indexing-strategy
---

# Indexing Strategy

## Índices observados
- `users.email` único.
- `clients.user_id` único y `clients.trainer_id` indexado.
- Índices por `trainer_id`, `client_id` e `is_template` en planes.
- Índices por `client_id`, fechas y claves lógicas en logs.
- `weekly_checkins` tiene índice y unique por `(client_id, week_start)`.
- `user_sessions.refresh_jti` es único.

## Propósito
- Resolver consultas por cliente, trainer, semana y sesión.
- Hacer viable el patrón upsert sin escanear tablas completas.
