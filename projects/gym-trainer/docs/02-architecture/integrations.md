---
project: fitness-app
tags:
  - fitness-app
  - docs
  - architecture
  - integrations
---

# Integrations

## Cloudflare R2
- Almacena fotos, evidencias y PDFs.
- Se usa tanto con URL firmada como con upload vía backend.

## ExerciseDB
- Se sincroniza al catálogo local `exercises`.
- Reduce dependencia directa del proveedor externo en tiempo real.

## ReportLab
- Genera PDFs mensuales.

## APScheduler
- Ejecuta la tarea mensual de reportes.

## Nota
No hay evidencia de Celery, pgvector, MCP server de negocio ni WebSockets dentro del código documentado en `docs` raíz.
