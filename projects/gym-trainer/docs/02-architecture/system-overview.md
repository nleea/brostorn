---
project: fitness-app
tags:
  - fitness-app
  - docs
  - architecture
  - system-overview
---

# System Overview

```text
[Vue 3 PWA]
    |
    | HTTP REST + JWT + X-Timezone
    v
[FastAPI]
    |
    | Async repositories
    v
[PostgreSQL]

[FastAPI] -> [Cloudflare R2]
[APScheduler] -> [PDF reports] -> [R2 + monthly_reports]
```

## Frontend
- Vistas por rol.
- Stores Pinia por dominio.
- Capa repo en `vue/repo/*`.

## Backend
- Routers por bounded context.
- Services para reglas de negocio.
- Repositories Postgres para acceso a datos.

## Principios
- Las agregaciones viven en backend.
- Los templates se copian al asignar.
- El timezone del cliente se propaga por header.
