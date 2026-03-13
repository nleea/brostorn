---
project: fitness-app
tags:
  - fitness-app
  - docs
  - decisions
  - adr
  - routing
---

# ADR-004 Routing

## Status
Accepted

## Decision
Usar Vue Router con `createWebHashHistory` y guards por auth/rol.

## Why
- Compatibilidad con el despliegue actual del frontend.
- Simplifica acceso directo en entorno estático/PWA.

## Consequence
- URLs con `#/`.
- Persisten rutas legacy que conviene corregir gradualmente.
