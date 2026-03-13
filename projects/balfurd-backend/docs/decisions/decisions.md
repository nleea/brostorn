# Architecture Decisions — Balfurd ERP

## ADR-001: UUID Primary Keys
**Decision**: All models use UUID PKs via BaseModel.
**Reason**: Prevents ID enumeration attacks, allows safe cross-environment ID sharing (dev→staging→prod), avoids integer PK collisions in distributed inserts.
**Impact**: Never reference records by integer ID in code or URLs.

## ADR-002: Flat URL Registration
**Decision**: All app URLs included at root path with no prefix.
**Reason**: Keeps API URLs clean and predictable (e.g., `/leads/` not `/crm/leads/`).
**Impact**: ViewSet names must be globally unique to avoid URL conflicts between apps.

## ADR-003: Email-Based Authentication
**Decision**: `USERNAME_FIELD = 'email'` on custom User model.
**Reason**: Email is more user-friendly and universally unique compared to username.
**Impact**: Authentication requests use `email` field, not `username`.

## ADR-004: View-Level RBAC (not field-level)
**Decision**: Permissions are granted per SavedViewSet (resource), not per field.
**Reason**: Simpler to manage, sufficient for current business needs. Field-level would add significant complexity.
**Impact**: All users with write access to a ViewSet can modify any field in that resource.

## ADR-005: Soft Deletes
**Decision**: `is_active=False` instead of hard deletes.
**Reason**: Preserve audit history, allow recovery, prevent FK constraint issues.
**Impact**: All querysets should filter `is_active=True` unless intentionally viewing inactive records.

## ADR-006: Three Celery Queues
**Decision**: `high`, `default`, `low` priority queues.
**Reason**: Invoice creation and critical financial ops must not be delayed by long-running scraper tasks.
**Impact**: When adding new tasks, explicitly choose queue. Default to `default`; use `high` only for financial/critical ops.

## ADR-007: Dependency Injection Container
**Decision**: Singleton `DependencyContainer` for service instantiation.
**Reason**: Testability (can inject mocks), single instantiation point, avoid circular imports.
**Impact**: Always use `dependency_container.get_X()` rather than `XImpl()` directly.

## ADR-008: Redis for Cache + Broker
**Decision**: Single Redis instance serves both Django cache and Celery broker.
**Reason**: Reduces infrastructure complexity. Separate DBs can be configured if performance demands it.
**Impact**: Redis outage affects both caching and async task processing simultaneously.

## ADR-009: S3 Toggle via USE_S3
**Decision**: Storage backend toggled via environment variable.
**Reason**: Local dev doesn't need S3; production always uses S3 for scalability and durability.
**Impact**: Never reference local file paths in code. Always use Django's `default_storage` abstraction.

## ADR-010: LangGraph React Agent for AI
**Decision**: React agent pattern with GPT-4o over simpler approaches.
**Reason**: Multi-step reasoning needed for sales operations (search → create → confirm). React handles tool chaining naturally.
**Impact**: Adding capabilities = adding LangChain tools, not rewriting agent logic.

## ADR-011: Chat History Limited to 50 Messages
**Decision**: AI agent only loads last 50 messages per session.
**Reason**: Context window management and token cost control.
**Impact**: Very long conversations may lose early context. Sessions should be reset periodically.

## ADR-012: RFID Middleware Logging
**Decision**: Custom middleware logs all API requests/responses to `RfidEndpointLog`.
**Reason**: Full audit trail for RFID tracking operations. Regulatory and operational requirement.
**Impact**: Performance overhead on every request. Excluded endpoints configured in settings. Max response size capped at 10KB.

## ADR-013: Blue/Green Deployment
**Decision**: AWS EC2 Blue/Green with Nginx traffic switching.
**Reason**: Zero-downtime deployments. Automatic rollback on health check failure.
**Impact**: `release` branch triggers deploy. `/health/` endpoint must always return 200 for DB + Redis + Celery.
