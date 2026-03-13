---
project: fitness-app
tags:
  - fitness-app
  - docs
  - architecture
  - auth-flow
---

# Auth Flow

1. El frontend envía `POST /auth/login`.
2. El backend crea una fila en `user_sessions`.
3. Retorna `access_token`, `refresh_token`, `session_id` y `user`.
4. El frontend guarda la sesión en `localStorage`.
5. `vue/api.ts` agrega `Authorization: Bearer <token>` a cada request.
6. Ante `401`, intenta `POST /auth/refresh`.
7. El refresh usa rotación de `jti` y `sid`.
8. Si el refresh falla, limpia sesión y redirige a `/#/auth/login`.

## Coordinación multi-tab
- `BroadcastChannel` y evento `storage` sincronizan estado.
- `auth_refresh_lock` evita refresh concurrente entre pestañas.

## Gestión multi-device
- `GET /auth/sessions`
- `DELETE /auth/sessions/{session_id}`
- `POST /auth/logout`
- `POST /auth/logout-all`
