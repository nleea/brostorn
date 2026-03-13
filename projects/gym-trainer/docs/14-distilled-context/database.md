---
type: distilled-context
module: database
project: fitness-app
status: active
updated: 2026-03-11
tags:
  - database
  - postgres
  - migrations
  - schema
---

# Database Distilled Context

## Purpose
The database layer stores application state, user data, plans, logs, metrics, and supporting entities.

## Core Flow
- The backend reads and writes through repository/service layers.
- Schema evolves through Alembic migrations.
- Async database access is handled through SQLModel/SQLAlchemy async patterns.

## Source of Truth
- SQLModel models
- repository layer
- Alembic migrations
- database configuration

## Key Contracts
- Schema changes must be migration-safe.
- Async DB access patterns must remain consistent.
- Queries should respect the existing service/repository architecture.

## Known Pitfalls
- Drift between models and migrations
- legacy naming inconsistencies
- incorrect async session usage
- derived data assumptions not reflected in schema

## Relevant Files
- `models/...`
- `repositories/...`
- `alembic/...`

## Related Notes
- [[05-database/schema]]
- [[05-database/migrations]]
- [[03-backend/index]]