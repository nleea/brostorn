---
project: fitness-app
tags:
  - fitness-app
  - docs
  - debugging
  - logout-not-redirecting
---

# Logout Not Redirecting

## Síntoma
- El usuario presiona logout y queda en una vista protegida o rebota al dashboard al intentar ir a login.
- Después de logout, un login inmediato puede comportarse de forma inconsistente por estado residual.

## Causa raíz
- El store `auth.logout()` era asíncrono y limpiaba `localStorage` solo después de esperar `POST /auth/logout`.
- Los layouts disparaban `logout()` sin `await` y navegaban enseguida a `/auth/login`.
- El guard del router decidía autenticación leyendo solo `auth_user` desde `localStorage`, sin exigir `access_token`.
- Durante esa carrera, el router veía `auth_user` todavía presente y redirigía otra vez a `/trainer` o `/client`.

## Fix aplicado
- Logout local optimista: se limpia estado y tokens primero para cortar la sesión del lado cliente sin esperar red.
- Revocación backend en segundo plano con `revokeCurrentSession()` usando el token capturado si sigue disponible.
- Los layouts ahora hacen `await logout()` y luego `router.replace('/auth/login')`.
- El guard del router valida sesión real con `access_token + auth_user`, no solo con `auth_user`.
- El login exitoso usa `router.replace(...)` para no dejar la ruta de auth en el historial.

## Checklist
- Confirmar que se limpió `localStorage`.
- Verificar `BroadcastChannel` y evento `storage`.
- Revisar si quedó `auth_refresh_lock` stale.
- Confirmar que el router usa sesión válida (`access_token` + `auth_user`) antes de permitir rutas protegidas.
- Confirmar que logout navega con `replace` a `/#/auth/login`.

## Archivos del fix
- `gym-trainer-client/vue/stores/auth.ts`
- `gym-trainer-client/vue/api.ts`
- `gym-trainer-client/vue/router/index.ts`
- `gym-trainer-client/vue/layouts/TrainerLayout.vue`
- `gym-trainer-client/vue/layouts/ClientLayout.vue`
- `gym-trainer-client/vue/views/auth/LoginView.vue`
