# Architecture — Balfurd ERP Backend

## Directory Layout
```
balfurd_erp/              # Django project config
  settings.py             # All settings (env-driven)
  urls.py                 # Root URL config
  celery.py               # Celery app setup (autodiscover)
  wsgi.py / asgi.py

apps/                     # All Django applications
  authentication/
  users/
  crm/
  sku/
  erp/
  operations/
  reporting/
  permissions/
  IA/
  quickbook/
  helcim/
  subscriptions/
  assets/
  slack/
  scrapper/
  default/                # Shared base classes and utilities

dependency_injection/     # DI container
  di_container.py         # Singleton DependencyContainer
  interface.py            # Abstract base classes
  services.py             # Implementations

docker/                   # Docker + docker-compose
```

## App Internal Convention (all apps follow this)
```
<app>/
  models/         # One model concern per file
  views/          # DRF ViewSets
  serializers/    # DRF serializers
  urls.py         # Router registration
  tests/          # TestCase / TransactionTestCase
  utils.py        # App-level helpers
  tasks/          # Celery tasks (where applicable)
```

## URL Registration
All app URLs are included **flat at root** (no per-app prefix):
```python
# balfurd_erp/urls.py
path('', include('apps.crm.urls'))      # e.g. /leads/, /proposals/
path('', include('apps.erp.urls'))      # e.g. /deliveries/, /invoices/
path('ia/', include('apps.IA.api.urls')) # /ia/chat, /ia/sessions, etc.
```

## Authentication Layer
- **JWT** (djangorestframework-simplejwt)
- Access token: **12 hours**
- Refresh token: **1 day** with rotation + blacklist
- Custom User model: `users.User` (AbstractUser + BaseModel)
- Email-based login

## RBAC Permissions
```
User → Role → [write_views: [SavedViewSet], read_views: [SavedViewSet]]
```
- `SavedViewSet` represents a named viewset/resource (not field-level)
- Custom permission class in `apps/permissions/permission.py`
- Company filter mixin for multi-tenancy on CRM views

## Celery Architecture
```
Redis (broker) → Celery Workers → Redis (result backend)
                 ├─ high queue   (invoice creation, critical ops)
                 ├─ default queue
                 └─ low queue    (scraper, non-critical)

Celery Beat → Periodic tasks (apps/erp/periodic_tasks.py)
```
- Three separate processes in Docker: app, celery-worker, celery-beat
- Tasks autodiscovered from all installed apps

## Caching Strategy
- Redis via `django.core.cache.backends.redis.RedisCache`
- KEY_PREFIX: `'balfurd'`
- Default timeout: 300s
- Centralized cache keys in `apps/default/cache_keys.py`
- Cache wrapper in `apps/default/cache_service.py`

## AI Agent Architecture
```
User → /ia/chat → LangGraph React Agent
                    ├─ GPT-4o (OpenAI)
                    ├─ Tools (lead_tools, item_tools, order_tools, proposal_tools)
                    │    └─ APIClient → internal REST API (authenticated)
                    └─ ChatMessage DB (session history, last 50 messages)
```

## Audit Trail
Every significant operation creates an `AuditLog` entry:
- Operations: INSERT / UPDATE / DELETE / PROCESS / STEP / ERROR
- Stored: table_name, row_id, old_data, new_data (JSON), user, process_run_id
- Functions: `audit_log()`, `audit_step()` in `apps/default/utils.py`

## RFID Tracking
- Custom middleware: `RfidEndpointLoggingMiddleware`
- Logs all API calls to `RfidEndpointLog` table
- Max response size: 10KB, request: 5KB, retention: 90 days
- Configurable endpoint exclusions via settings

## Storage
- Toggle via `USE_S3=True/False` in .env
- S3: `django-storages` + boto3 + AWS credentials
- Local fallback: `/media/` directory

## Deployment
- **CI/CD**: GitHub Actions on push to `release` branch
- **Strategy**: Blue/Green on AWS EC2 with Nginx traffic switching
- **Migrations**: Run automatically during deploy
- **Rollback**: Automatic on `/health/` check failure
- **Health check** verifies: DB + Redis + Celery connectivity
