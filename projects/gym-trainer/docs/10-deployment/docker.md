---
project: fitness-app
tags:
  - fitness-app
  - docs
  - deployment
  - docker
---

# Docker

## Infraestructura documentada
- `trainerGM/backend/docker-compose.yml`
- Servicios: `postgres`, `fastapi`, `nginx`

## Backend
```bash
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend
```bash
npm install
npm run build
npm run preview
```
