# Deployment — Balfurd ERP

## Environments

| Env | Database | Trigger |
|-----|---------|---------|
| DEVELOPMENT | Local PostgreSQL (`DB_DEVELOP_*` vars) | `ENVIRONMENT=DEVELOPMENT` |
| RENDER | Render.com managed DB | `ENVIRONMENT=RENDER` |
| PRODUCTION | AWS RDS PostgreSQL (`DB_*` vars or `DATABASE_URL`) | `ENVIRONMENT=PRODUCTION` |

## CI/CD Pipeline
- **Trigger**: Push to `release` branch
- **Platform**: GitHub Actions
- **Strategy**: Blue/Green deployment on AWS EC2
- **Traffic switch**: Nginx upstream swap after health check passes
- **Rollback**: Automatic if `/health/` fails after deploy
- **Migrations**: Run automatically during deploy (`python manage.py migrate`)

## Health Check
`GET /health/` — Returns 200 only when all pass:
- PostgreSQL DB connection
- Redis connection
- Celery worker availability

## Docker
```
docker/
  Dockerfile
  docker-compose.yml
  .env             # environment config
```

Services in compose:
- `app` — Django application (gunicorn)
- `celery-worker` — Celery worker (all queues)
- `celery-beat` — Celery scheduler (periodic tasks)
- `redis` — Broker + cache
- `db` — PostgreSQL (dev only; prod uses RDS)

## Required Environment Variables
```bash
# Core
SECRET_KEY=
DEBUG=False
ENVIRONMENT=PRODUCTION
ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=

# Database
DATABASE_URL=           # or individual DB_* vars
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Redis
REDIS_URL=

# Storage
USE_S3=True
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# AI
OPENAI_API_KEY=

# Email
SENDGRID_API_KEY=

# Payments
HELCIM_API_TOKEN=
STRIPE_SECRET_KEY=

# Integrations
GOOGLE_MAPS_API_KEY=
SLACK_WEBHOOK_URL=
QUICKBOOKS_CLIENT_ID=
QUICKBOOKS_CLIENT_SECRET=
```

## Production Server
- **Compute**: AWS EC2
- **Web server**: Nginx (reverse proxy) → gunicorn
- **Database**: AWS RDS PostgreSQL
- **Cache/Broker**: Redis (managed or EC2)
- **Storage**: AWS S3

## Build Script
`build.sh` handles:
1. Pull latest code
2. Install dependencies (`pip install -r requirements.txt`)
3. Run migrations
4. Collect static files
5. Restart gunicorn

## Gunicorn Command
```bash
gunicorn balfurd_erp.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

## Celery Workers
```bash
# Worker (all queues)
celery -A balfurd_erp worker -Q high,default,low --loglevel=info

# Beat scheduler
celery -A balfurd_erp beat --loglevel=info
```
