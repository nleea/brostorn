---
project: fitness-app
tags:
  - fitness-app
  - docs
  - backend
  - background-jobs
---

# Background Jobs

## Job actual
- Reporte mensual PDF.

## Flujo
1. Scheduler ejecuta la tarea al cierre de mes.
2. Se agregan datos del cliente.
3. `ReportLab` genera el PDF.
4. El archivo se sube a R2.
5. Se registra en `monthly_reports`.

## Estado
- El patrón actual es scheduler local.
- No hay evidencia de cola distribuida ni worker dedicado en la documentación raíz.
