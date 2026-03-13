---
project: fitness-app
tags:
  - fitness-app
  - docs
  - decisions
  - adr
  - vector-db
---

# ADR-002 Vector DB

## Status
Not adopted in current docs

## Decision
La documentación raíz no muestra una base vectorial activa ni `pgvector`.

## Current alternative
PostgreSQL relacional con índices convencionales y columnas JSON.

## Consequence
No se deben asumir embeddings, búsqueda semántica o consultas vectoriales hasta que exista evidencia en código o notas fuente.
