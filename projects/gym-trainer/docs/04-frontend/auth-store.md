---
project: fitness-app
tags:
  - fitness-app
  - docs
  - frontend
  - auth-store
---

# Auth Store

## Estado
- `user`
- `role`
- `loading`
- `error`

## Acciones
- `initAuthListener`
- `login`
- `register`
- `createClientUser`
- `logout`

## Responsabilidades
- Mantener contexto de sesión.
- Coordinar sync multi-tab.
- Reaccionar a refresh y revocación de sesión.
