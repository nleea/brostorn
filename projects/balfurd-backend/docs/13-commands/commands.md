# Commands Reference — Balfurd ERP

## Project Root
```
/Users/nelsonborrego/Desktop/CO/NS/balfurd-erp_backend
```

## Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (ask another developer for values)
cp .env.example .env
```

## Database
```bash
# Apply all pending migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations crm

# Create superadmin user
python manage.py createsuperadmin
```

## Development Server
```bash
# Run development server (default port 8000)
python manage.py runserver

# API docs available at:
# http://localhost:8000/swagger/
# http://localhost:8000/admin/
# http://localhost:8000/health/
```

## Celery (run each in separate terminal)
```bash
# Start worker (all queues)
celery -A balfurd_erp worker -l info --pool=solo -Q high,default,low --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Testing
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test apps.erp
python manage.py test apps.crm

# Run specific test file
python manage.py test apps.crm.tests.test_leads

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # generates htmlcov/ directory
```

## Docker
```bash
# Start all services
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f app
docker compose -f docker/docker-compose.yml logs -f celery-worker

# Rebuild after code changes
docker compose -f docker/docker-compose.yml up -d --build

# Stop all services
docker compose -f docker/docker-compose.yml down
```

## Common Django Shell Operations
```bash
python manage.py shell

# Example: check a lead
from apps.crm.models import Lead
lead = Lead.objects.get(account='ACC-001')
print(lead.status, lead.agreed_value)

# Example: check celery tasks
from django_celery_beat.models import PeriodicTask
PeriodicTask.objects.all().values('name', 'enabled')
```

## Static Files (production)
```bash
python manage.py collectstatic --noinput
```

## Cache Management
```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```
