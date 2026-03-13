---
project: fitness-app
tags:
  - fitness-app
  - docs
  - backend
  - api-patterns
---

# API Patterns

## Patrones observados
- Routers delgados con services dedicados.
- Repositories para encapsular SQL.
- DTOs y schemas separados del modelo persistido.
- Endpoints de upsert cuando la UX requiere idempotencia.

## Ejemplos
- `POST /training-logs` hace upsert por día.
- `POST /meal-logs/upsert` hace upsert por comida.
- `POST /auth/refresh` rota refresh token.

## Diseño
- Los cálculos agregados viven en backend.
- Los templates se diferencian de las copias asignadas con campos explícitos.
