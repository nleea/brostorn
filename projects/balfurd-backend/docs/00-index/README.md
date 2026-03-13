# Balfurd ERP Backend — Index

## What is this?
CRM/ERP backend for Balfurd. Django REST Framework application managing the full lifecycle: leads → proposals → contracts → deliveries → invoices → payments. Includes AI agent for sales operations, RFID tracking, and integrations with QuickBooks, Helcim, Slack, and AWS S3.

## Workspace
- **Repo**: `/Users/nelsonborrego/Desktop/CO/NS/balfurd-erp_backend`
- **Stack**: Django 4.2+, PostgreSQL, Redis, Celery, LangChain/LangGraph, GPT-4o
- **API Docs**: `/swagger/` (dev only)
- **Health**: `/health/` (DB + Redis + Celery)

## Documentation Map

| Doc | Content |
|-----|---------|
| `01-project/overview.md` | Project overview, apps, tech stack |
| `02-architecture/architecture.md` | System architecture, flows, layers |
| `03-backend/backend.md` | Apps, ViewSets, Serializers, URLs |
| `05-database/models.md` | All models with key fields |
| `06-features/features.md` | Key features per domain |
| `07-patterns/patterns.md` | Code patterns (BaseModel, audit, DI, queries) |
| `09-decisions/decisions.md` | Architecture decisions and rationale |
| `10-deployment/deployment.md` | CI/CD, Docker, AWS, environments |
| `13-commands/commands.md` | Dev commands reference |
| `14-distilled-context/distilled.md` | Compressed context for MCP |

## Context Templates
| Template | Use When |
|----------|---------|
| `context/debugging.md` | Investigating bugs or unexpected behavior |
| `context/new-feature.md` | Adding new endpoints or modules |
