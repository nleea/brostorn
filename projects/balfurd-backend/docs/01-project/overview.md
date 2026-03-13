# Project Overview — Balfurd ERP Backend

## Purpose
Full-stack ERP/CRM for managing the Balfurd business operations. Covers the complete sales and fulfillment lifecycle:
- Lead acquisition and tracking (CRM)
- Proposal generation with AI agent assistance
- Contract and order management
- Delivery scheduling and RFID inventory tracking
- Invoice generation and payment processing (Helcim)
- Reporting, analytics, and QuickBooks sync

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2+ / Django REST Framework |
| Language | Python 3.11+ |
| Database | PostgreSQL (AWS RDS in prod) |
| Cache / Broker | Redis |
| Task Queue | Celery (3 queues: high, default, low) |
| AI Agent | LangChain + LangGraph + GPT-4o |
| Storage | AWS S3 (toggle via USE_S3) or local |
| Email | SendGrid |
| Payments | Helcim |
| Auth | JWT via djangorestframework-simplejwt |
| API Docs | drf-yasg (Swagger at /swagger/) |
| Deployment | AWS EC2 + Nginx, Blue/Green via GitHub Actions |

## Django Apps (17 custom)

| App | Responsibility |
|-----|---------------|
| `authentication` | JWT login, token refresh |
| `users` | User, SalesRep, Company models |
| `permissions` | RBAC: Role → SavedViewSet (view-level access) |
| `crm` | Lead, Contact, Order, OrderItem, Proposal, Contract, Activity |
| `sku` | Item (SKU catalog), ItemStatus |
| `erp` | Delivery, Invoice, Credit, WorkOrder, Payroll, LocalTax |
| `operations` | Route, RouteName, RouteSchedule, Headquarter, Cart |
| `reporting` | Analytics, RFID tracking (RfidMovement, RfidEndpointLog) |
| `IA` | AI agent: ChatSession, ChatMessage, LangGraph tools |
| `quickbook` | QuickBooks sync (journal entries, credits, collections) |
| `helcim` | Helcim payment processing + webhook |
| `subscriptions` | Subscription management |
| `assets` | Fixed asset tracking and depreciation |
| `slack` | Slack lead notifications |
| `scrapper` | LinkedIn/Google scraping (Scrapy-based, low queue) |
| `default` | BaseModel, AuditLog, cache helpers, dynamic query builder |
| `dependency_injection` | DI container (currently: UserService) |

## Business Domain Flow
```
Lead (CRM) → Proposal → Contract → Order → Delivery → Invoice → Payment
                 ↑                    ↑
            AI Agent              RFID Tracking
              (IA)              (reporting/operations)
```

## Environments
- **DEVELOPMENT**: local DB via `DB_DEVELOP_*` env vars
- **RENDER**: Render.com staging
- **PRODUCTION**: AWS RDS via `DB_*` env vars or `DATABASE_URL`

Selected automatically via `ENVIRONMENT` env var.
