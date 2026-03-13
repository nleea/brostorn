# Code Patterns — Balfurd ERP

## 1. BaseModel Pattern
All models inherit from `BaseModel`. Never use Django's Model directly.

```python
# apps/default/models/base_model.py
class BaseModel(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    class Meta:
        abstract = True
```

**Soft delete**: set `is_active=False` instead of deleting records.
Filter active records: `queryset.filter(is_active=True)`.

---

## 2. Audit Log Pattern
Use for all significant state changes. Two helper functions:

```python
from apps.default.utils import audit_log, audit_step

# Single operation
audit_log(
    table_name="Delivery",
    row_id=str(delivery.id),
    operation="UPDATE",   # INSERT / UPDATE / DELETE / PROCESS / ERROR
    old_data=old_data,
    new_data=new_data,
    user=request.user
)

# Multi-step process (groups steps with process_run_id)
audit_step(
    process_run_id=run_id,
    step="invoice_creation",
    message="Invoice created successfully",
    table_name="Invoice",
    row_id=str(invoice.id)
)
```

---

## 3. Dynamic Query Builder
Used in ViewSet list actions for flexible filtering from query params:

```python
from apps.default.utils import get_query_data

queryset = get_query_data(
    Lead,
    request.query_params,
    prefetch=['contacts', 'orders__items'],
    select_related=['associated_salesRep']
)
```

`build_dynamic_q()` converts URL params → Django Q objects with support for:
- Range filters (`?field__gte=val&field__lte=val`)
- `__in` lookups (`?status__in=sql,mql`)
- Standard operators (exact, icontains, etc.)

---

## 4. Dependency Injection Pattern
Access services via the DI container, never instantiate directly:

```python
from dependency_injection.di_container import dependency_container

user_service = dependency_container.get_user_service()
user = user_service.create_user(data)
```

Singleton container caches service instances in `self.services` dict.
To add a new service: implement interface in `services.py`, register in `di_container.py`.

---

## 5. ViewSet Pattern (DRF)
All endpoints use DRF ViewSets. Standard structure:

```python
class LeadViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):
    queryset = Lead.objects.filter(is_active=True)
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
```

URL registration always uses DefaultRouter, included flat at root.

---

## 6. RBAC Permission Check
Custom permission class reads user's Role → checks write_views or read_views against the requested ViewSet name.

```python
# apps/permissions/permission.py
class RBACPermission(BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        viewset_name = view.__class__.__name__
        if request.method in SAFE_METHODS:
            return viewset_name in user_role.read_views.values_list('name', flat=True)
        return viewset_name in user_role.write_views.values_list('name', flat=True)
```

---

## 7. Celery Task Pattern
```python
from celery import shared_task
from apps.default.utils import audit_log

@shared_task(queue='high')
def settled_deliveries_method(delivery_ids: list):
    for delivery_id in delivery_ids:
        # ... process ...
        audit_log(table_name="Invoice", operation="INSERT", ...)
```

Task queues: `'high'` for critical ops, `'default'` for standard, `'low'` for non-urgent (scraper).

---

## 8. Cache Pattern
```python
from apps.default.cache_service import cache_service
from apps.default.cache_keys import LEADS_LIST_KEY

# Get
data = cache_service.get(LEADS_LIST_KEY)

# Set with timeout
cache_service.set(LEADS_LIST_KEY, serialized_data, timeout=300)

# Delete on model change
cache_service.delete(LEADS_LIST_KEY)
```

Always define cache keys in `apps/default/cache_keys.py`, never hardcode strings.

---

## 9. AI Agent Tool Pattern
New tools follow this template:

```python
# apps/IA/tools/my_tools.py
from langchain.tools import tool
from apps.IA.core.client import APIClient

@tool
def get_something(client: APIClient, param: str) -> dict:
    """Tool description for LLM to understand when to use it."""
    response = client.get(f"/endpoint/?param={param}")
    return response.json()
```

Then register in `apps/IA/agent/agent.py` in the `build_agent()` tools list.

---

## 10. Multi-tenancy / Company Filtering
CRM views apply `CompanyFilterMixin` to scope querysets:

```python
class CompanyFilterMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            company=self.request.user.company
        )
```

Always ensure CRM ViewSets extend this mixin.

---

## 11. AccumulatedModel (RFID)
For models that need RFID tracking, inherit from `AccumulatedModel`:
```python
class AccumulatedModel(BaseModel):
    rfid_code = models.CharField(...)
    class Meta:
        abstract = True
```

---

## Anti-patterns to Avoid
- Do NOT instantiate services directly — use DI container
- Do NOT delete records — set `is_active=False`
- Do NOT hardcode cache keys — use `cache_keys.py`
- Do NOT skip audit logging on state-changing operations
- Do NOT use `objects.all()` without filtering — always add `is_active=True` where applicable
