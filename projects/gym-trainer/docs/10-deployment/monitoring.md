---
project: fitness-app
tags:
  - fitness-app
  - docs
  - deployment
  - monitoring
---

# Monitoring

No hay stack de monitoreo explícito documentado en los `.md` raíz.

## Señales operativas actuales
- Validar `monthly_reports` para confirmar jobs.
- Revisar fallas de auth desde `user_sessions`.
- Corroborar estado de migraciones con `alembic current`.

## Gap
Falta documentación específica de logs centralizados, métricas y alertas.
