---
project: fitness-app
tags:
  - fitness-app
  - docs
  - frontend
  - router
---

# Router

## Base
- Vue Router con `createWebHashHistory`.

## Rutas
- Auth: `/auth/login`, `/auth/register`
- Trainer: `/trainer/*`
- Client: `/client/*`
- Compartidas: `/exercises`

## Guards
- Uso de `meta.requiresAuth`.
- Restricción por `meta.role`.
- Redirección a login cuando no hay sesión válida.

## Nota
Existe un typo legacy en la ruta `/client/metricts`.
