---
project: fitness-app
tags:
  - fitness-app
  - docs
  - frontend
  - logout-flow
---

# Logout Flow

1. El usuario ejecuta logout desde la UI.
2. El store limpia de inmediato `access_token`, `refresh_token`, `auth_user` y `auth_refresh_lock`.
3. Se notifica a otras pestañas por `BroadcastChannel` y `storage`.
4. El router navega con `replace` a `/#/auth/login`.
5. En paralelo, el frontend intenta revocar la sesión actual en backend con `POST /auth/logout` si todavía tiene token utilizable.

## Problemas típicos
- Lock de refresh stale.
- Broadcast no propagado.
- Estado residual en `localStorage` si la limpieza no ocurre antes de navegar.
