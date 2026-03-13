---
project: fitness-app
tags:
  - fitness-app
  - docs
  - architecture
  - service-architecture
---

# Service Architecture

## Backend layering
- `routers/`: transporte HTTP y validación de entrada.
- `services/`: reglas de negocio, agregaciones y permisos.
- `repositories/interface`: contratos.
- `repositories/implementations/postgres`: acceso real a Postgres.

## Frontend layering
- `views/`: pantallas.
- `stores/`: estado y coordinación.
- `repo/`: llamadas HTTP y mapeos.
- `composables/`: utilidades de UI y comportamiento.

## Ventajas
- Routers delgados.
- Reglas de negocio centralizadas.
- Persistencia desacoplada.
- Menos duplicación entre vistas.
