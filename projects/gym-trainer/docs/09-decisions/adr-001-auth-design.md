---
project: fitness-app
tags:
  - fitness-app
  - docs
  - decisions
  - adr
  - auth-design
---

# ADR-001 Auth Design

## Status
Accepted

## Decision
Usar access token + refresh token con sesión persistida en `user_sessions`.

## Why
- Permite multi-device.
- Permite revocación selectiva.
- Soporta refresh rotatorio con `sid` y `jti`.

## Consequences
- Más complejidad en frontend para refresh coordinado.
- Requiere migraciones y limpieza correcta de sesión.
