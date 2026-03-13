# Context Template: Debugging — Balfurd ERP

## When to Use
Use this template when investigating unexpected behavior, bugs, or errors in the balfurd-erp_backend.

## Investigation Order

### Step 1 — Identify Symptom
- What endpoint or operation is failing?
- What is the expected vs actual behavior?
- Is it a 4xx (client/permission) or 5xx (server) error? Or silent wrong data?

### Step 2 — Check Common Causes First
```
□ is_active=True filter missing → records not showing or wrong queryset
□ JWT expired (12h access token) → 401 Unauthorized
□ RBAC permission denied → 403 Forbidden (check Role → SavedViewSet)
□ Celery worker down → async task not executing (check with /health/)
□ Redis down → cache miss + Celery broker failure
□ Wrong Celery queue → task queued but not processed
□ S3 credentials expired → file upload/download failures
□ Migration not applied → column missing or model mismatch
```

### Step 3 — Check Audit Trail
```python
from apps.default.models.auditLog import AuditLog

# Find recent operations on a model
AuditLog.objects.filter(
    table_name="Delivery",
    row_id="<uuid>"
).order_by('-created_at')[:20]

# Find errors in a process
AuditLog.objects.filter(
    operation="ERROR",
    created_at__gte=some_datetime
).order_by('-created_at')
```

### Step 4 — Check Endpoint Logs
```python
from apps.reporting.models import RfidEndpointLog

# Find API call trace
RfidEndpointLog.objects.filter(
    created_at__gte=some_datetime
).order_by('-created_at')[:50]
```

### Step 5 — Check Celery Tasks
```bash
# Check worker is running
curl http://localhost:8000/health/

# Check pending tasks (in Django shell)
from celery.app.control import Control
from balfurd_erp.celery import app
inspect = app.control.inspect()
inspect.active()   # currently running
inspect.reserved() # queued
```

### Step 6 — Check Relevant Model Data
```python
# Always check is_active!
Lead.objects.filter(id=lead_id)  # might return empty if is_active=False
Lead.objects.filter(id=lead_id, is_active=False)  # check soft-deleted records
```

## Common Bug Patterns

### Bug: Records Not Appearing in List
- Root cause: `is_active=False` (soft deleted) or wrong company filter (multi-tenancy)
- Fix: Check `is_active` flag, check `CompanyFilterMixin` scope

### Bug: Async Operation Not Completing
- Root cause: Celery worker not running, wrong queue, or Redis broker down
- Fix: Check `/health/` endpoint, restart worker, check queue assignment

### Bug: Permission Denied (403) on Known User
- Root cause: User's Role doesn't have the ViewSet in write_views/read_views
- Fix: Check `Role.write_views.all()` / `Role.read_views.all()` for user's role, add SavedViewSet entry

### Bug: Invoice Not Created After Delivery Settled
- Root cause: `settled_deliveries_method` task (high queue) not running
- Fix: Check Celery high queue, check AuditLog for ERROR entries

### Bug: AI Agent Tool Call Failing
- Root cause: APIClient authentication token expired, or internal API returning error
- Fix: Check `apps/IA/core/client.py` auth setup, check target endpoint directly

### Bug: Cache Returning Stale Data
- Root cause: Cache invalidation not triggered after model update
- Fix: Find where `cache_service.set()` is called, ensure `cache_service.delete()` is in update path

## Files to Always Check
```
apps/default/utils.py         → audit_log, get_query_data
apps/default/models/auditLog  → AuditLog entries
apps/permissions/permission.py → RBAC logic
apps/<app>/views/             → ViewSet logic
apps/<app>/tasks/             → Celery task implementation
balfurd_erp/settings.py       → Config values
```
