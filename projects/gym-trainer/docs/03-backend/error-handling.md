---
project: fitness-app
tags:
  - fitness-app
  - docs
  - backend
  - error-handling
---

# Error Handling

## Backend
- Uso de `HTTPException` con códigos `401`, `403`, `404`, `409`, `422`.
- Mensajes de dominio en auth, ownership y validaciones.

## Frontend consumer
- Los repos y stores capturan errores y exponen `loading` y `error`.
- `vue/api.ts` fuerza logout al detectar ciertos `401`.

## Riesgos conocidos
- Naming inconsistente entre snake_case y camelCase.
- Algunos errores dependen de mapeos manuales en repos.
