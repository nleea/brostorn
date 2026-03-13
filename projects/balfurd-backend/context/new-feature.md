# Context Template: New Feature — Balfurd ERP

## When to Use
Use when adding new endpoints, models, Celery tasks, or AI tools to balfurd-erp_backend.

## Classify First — Which Layer?

| Type | App | Pattern to Follow |
|------|-----|-------------------|
| New model + CRUD endpoint | Appropriate domain app | Existing ViewSet in same app |
| New Celery task | Same app as related model | `apps/erp/tasks/*.py` |
| New AI tool | `apps/IA/tools/` | `apps/IA/tools/proposal_tools.py` |
| New integration | New or existing integration app | `apps/quickbook/` or `apps/helcim/` |
| Shared utility | `apps/default/` | `apps/default/utils.py` |

## New Model Checklist

```python
# 1. Create model file: apps/<app>/models/<model_name>.py
from apps.default.models.base_model import BaseModel

class MyModel(BaseModel):
    # UUID PK, timestamps, is_active, is_staff from BaseModel
    name = models.CharField(max_length=255)
    lead = models.ForeignKey('crm.Lead', on_delete=models.CASCADE)
    # ...

    class Meta:
        db_table = 'my_model'
```

```bash
# 2. Create and apply migrations
python manage.py makemigrations <app>
python manage.py migrate
```

```python
# 3. Create serializer: apps/<app>/serializers/<model>_serializer.py
from rest_framework import serializers
from apps.<app>.models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

```python
# 4. Create ViewSet: apps/<app>/views/<model>_views.py
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from apps.permissions.permission import RBACPermission
from apps.default.utils import audit_log, get_query_data

class MyModelViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin):
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    def get_queryset(self):
        return get_query_data(MyModel, self.request.query_params)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        audit_log(
            table_name="MyModel",
            row_id=str(instance.id),
            operation="INSERT",
            new_data=serializer.data,
            user=self.request.user
        )
```

```python
# 5. Register URL: apps/<app>/urls.py
from rest_framework.routers import DefaultRouter
from apps.<app>.views import MyModelViewSet

router = DefaultRouter()
router.register(r'my-models', MyModelViewSet, basename='my-model')
urlpatterns = router.urls
```

```python
# 6. Include in root URLs: balfurd_erp/urls.py
path('', include('apps.<app>.urls')),
```

```python
# 7. Add RBAC — register ViewSet name in admin/shell
from apps.permissions.models import SavedViewSet
SavedViewSet.objects.get_or_create(name='MyModelViewSet')
# Then assign to relevant Role.write_views / Role.read_views
```

## New Celery Task Checklist
```python
# apps/<app>/tasks/my_task.py
from celery import shared_task
from apps.default.utils import audit_log

@shared_task(queue='default')  # or 'high' / 'low'
def my_task(record_id: str):
    try:
        # ... logic ...
        audit_log(table_name="MyModel", row_id=record_id, operation="PROCESS")
    except Exception as e:
        audit_log(table_name="MyModel", row_id=record_id, operation="ERROR",
                  message=str(e))
        raise
```

For periodic tasks: register in `apps/erp/periodic_tasks.py` using `django-celery-beat`.

## New AI Tool Checklist
```python
# apps/IA/tools/my_tools.py
from langchain.tools import tool
from apps.IA.core.client import APIClient

@tool
def my_tool(client: APIClient, param: str) -> dict:
    """
    Clear description for LLM to know when to call this tool.
    Args:
        client: APIClient instance for internal API calls
        param: description of param
    """
    response = client.get(f"/my-models/?filter={param}")
    return response.json()
```

Then register in `apps/IA/agent/agent.py` `build_agent()`:
```python
tools = [search_leads, get_lead_detail, ..., my_tool]
```

## Quality Checklist Before Committing
- [ ] Model inherits BaseModel (UUID PK, timestamps, is_active)
- [ ] Migration created and applied
- [ ] Serializer covers required fields
- [ ] ViewSet uses `get_query_data()` for list
- [ ] `audit_log()` called on create/update/delete
- [ ] URL registered in app's `urls.py`
- [ ] `SavedViewSet` entry created for RBAC
- [ ] Tests written in `apps/<app>/tests/`
- [ ] Cache invalidation added if relevant cached data changes
