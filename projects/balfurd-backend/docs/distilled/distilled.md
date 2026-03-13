# Distilled Context — Balfurd ERP Backend

## One-Line Summary
Django DRF ERP/CRM backend: leads → proposals → deliveries → invoices, with Celery async ops, LangChain AI agent, RFID tracking, and integrations (QuickBooks, Helcim, Slack, S3).

## Critical Facts (load before working on any task)

**BaseModel**: Every model has UUID PK, created_at, updated_at, is_active (soft delete), is_staff.

**Soft deletes**: NEVER hard delete. Set `is_active=False`. Filter `is_active=True` in querysets.

**URL structure**: All endpoints flat at root (`/leads/`, `/deliveries/`). Exception: `/ia/` prefix for AI agent.

**Auth**: JWT, 12h access / 1d refresh with rotation. Custom User model `users.User`. Email-based login.

**RBAC**: `User → Role → [write_views, read_views] → SavedViewSet`. View-level permissions only.

**DI Container**: Use `dependency_container.get_user_service()`, never `UserServiceImpl()` directly.

**Cache**: Always use `apps/default/cache_keys.py` keys + `cache_service.py` wrapper. Prefix: `balfurd`.

**Audit**: Call `audit_log()` / `audit_step()` from `apps/default/utils.py` on every state change.

**Celery queues**: `high` (invoices, financial), `default` (standard), `low` (scraper).

**AI Tools**: Add to `apps/IA/tools/`, register in `build_agent()`. Tools call API via `APIClient`.

**Dynamic queries**: Use `get_query_data()` from `apps/default/utils.py` for list endpoints.

**Storage**: Never use local paths directly. Always `django.core.cache` / `default_storage`. Toggle via `USE_S3`.

---

## Domain Model in One View
```
Lead → Order (→ OrderItem → Item)
     → Proposal (→ Order)
     → Contract
     → Delivery (→ Invoice → Credit)
                (→ DeliveryItem → ItemStatus)

User → SalesRep → Lead (associated_salesRep)
User → Role → [SavedViewSet] (RBAC)
User → ChatSession → ChatMessage (AI agent)
```

---

## App → Responsibility Quick Reference
| App | Main Models | Main Tasks |
|-----|------------|-----------|
| `crm` | Lead, Contact, Order, Proposal, Contract | Sales lifecycle |
| `erp` | Delivery, Invoice, Credit, WorkOrder | Fulfillment + billing |
| `sku` | Item, ItemStatus | Product catalog |
| `operations` | Route, RouteName, Cart | Logistics |
| `reporting` | RfidMovement, RfidEndpointLog | Analytics + RFID |
| `IA` | ChatSession, ChatMessage | AI agent |
| `users` | User, SalesRep, Company | Auth + people |
| `permissions` | Role, SavedViewSet | Access control |
| `default` | BaseModel, AuditLog | Shared utils |
| `quickbook` | QuickBook, JournalEntry | QB sync |
| `helcim` | (webhooks only) | Payment processing |

---

## Key File Locations
```
apps/default/utils.py           → audit_log, get_query_data, build_dynamic_q
apps/default/cache_keys.py      → All cache key constants
apps/default/cache_service.py   → Cache get/set/delete wrapper
apps/default/models/base_model.py → BaseModel
apps/default/models/auditLog.py → AuditLog model
dependency_injection/di_container.py → DI singleton
apps/IA/agent/agent.py          → build_agent(), LangGraph setup
apps/IA/core/client.py          → APIClient for tool API calls
apps/erp/periodic_tasks.py      → Scheduled Celery tasks
balfurd_erp/settings.py         → All configuration
balfurd_erp/urls.py             → Root URL config
```

---

## New Feature Checklist
- [ ] Create model in `apps/<app>/models/<model>.py` inheriting BaseModel
- [ ] Add `makemigrations` + `migrate`
- [ ] Create serializer in `apps/<app>/serializers/`
- [ ] Create ViewSet in `apps/<app>/views/`
- [ ] Register in `apps/<app>/urls.py` router
- [ ] Add audit_log calls in create/update/delete
- [ ] Add RBAC: create SavedViewSet entry for new ViewSet name
- [ ] Add tests in `apps/<app>/tests/`

## Debugging Checklist
- [ ] Check `is_active=True` filter not missing
- [ ] Check JWT token expiry (12h access)
- [ ] Check Celery worker is running for async ops
- [ ] Check Redis connection for cache misses
- [ ] Check AuditLog for operation history
- [ ] Check RfidEndpointLog for API call trace
- [ ] Check Celery queue — task might be in wrong queue (high/default/low)
