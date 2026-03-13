# Backend Reference — Balfurd ERP

## API Endpoints Summary

All routes registered flat at root (`/`) except IA (`/ia/`).

### Authentication
| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/auth/login/` | JWT login |
| POST | `/auth/token/refresh/` | Token refresh |

### Users
| ViewSet | Resource |
|---------|---------|
| UserViewSet | `/users/` |
| SalesRepViewSet | `/sales-reps/` |
| CompanyViewSet | `/companies/` |

### CRM
| ViewSet | Resource |
|---------|---------|
| LeadViewSet | `/leads/` |
| ContactViewSet | `/contacts/` |
| ContractViewSet | `/contracts/` |
| OrderViewSet | `/orders/` |
| ProposalViewSet | `/proposals/` |
| ActivityViewSet | `/activities/` |
| LeadCommentViewSet | `/lead-comments/` |
| MetricsViewSet | `/metrics/` |
| CrmHomeViewSet | `/crm-home/` |

### ERP
| ViewSet | Resource |
|---------|---------|
| DeliveryViewset | `/deliveries/` |
| InvoiceViewSet | `/invoices/` |
| CreditViewSet | `/credits/` |
| WorkOrderViewSet | `/work-orders/` |
| PayrollViewSet | `/payroll/` |
| CollectedMoneyViewSet | `/collected-money/` |
| ApplyPaymentsViewSet | `/apply-payments/` |
| LocalTaxViewset | `/local-taxes/` |
| HubViewSet | `/hubs/` |
| TransitViewSet | `/transits/` |

### SKU
| ViewSet | Resource |
|---------|---------|
| ItemViewSet | `/items/` |
| ItemStatusViewSet | `/item-status/` |

### Operations
| ViewSet | Resource |
|---------|---------|
| RouteViewSet | `/routes/` |
| RouteNameViewSet | `/route-names/` |
| HeadquarterViewSet | `/headquarters/` |
| CartViewSet | `/carts/` |
| PackoutViewSet | `/packout/` |

### Reporting
| ViewSet | Resource |
|---------|---------|
| AnalysisViewSet | `/analysis/` |
| RFIDViewSet | `/rfid/` |
| RfidEndpointLogViewSet | `/rfid-logs/` |
| CapitalViewSet | `/capital/` |
| CostViewSet | `/costs/` |
| StatementReportClassViewSet | `/statements/` |

### AI Agent (prefix: /ia/)
| Endpoint | Action |
|----------|--------|
| POST `/ia/chat` | Send message to AI agent |
| POST `/ia/reset` | Reset session |
| GET `/ia/sessions` | List sessions |
| GET `/ia/session_messages` | Get messages in session |
| DELETE `/ia/session_delete` | Delete session |

### Integrations
| Endpoint | Purpose |
|----------|---------|
| `/helcim/` | Helcim payment init |
| `POST /helcim/webhook/` | Helcim webhook handler |
| `/quickbook/` | QuickBooks operations |
| POST `/slack/lead-notification/` | Slack notification |
| GET `/swagger/` | API documentation |
| GET `/health/` | Health check |

---

## Key DRF Patterns

### ViewSet Pattern
```python
class LeadViewSet(viewsets.GenericViewSet, ...):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, CustomRBACPermission]
```

### Dynamic Query Builder
All list endpoints typically use `get_query_data()` from `apps/default/utils.py`:
```python
# Supports filters, prefetch, select_related, annotations from request params
queryset = get_query_data(Lead, request.query_params, prefetch=['contacts'])
```

### Multi-tenancy
CRM views use `CompanyFilterMixin` to scope queries to user's company.

### Audit Logging in Views
```python
audit_log(
    table_name="Lead",
    row_id=lead.id,
    operation="UPDATE",
    new_data=serializer.data,
    user=request.user
)
```

---

## AI Agent Tools

Located in `apps/IA/tools/`:

| Tool | Function |
|------|---------|
| `lead_tools.py` | `search_leads`, `get_lead_detail` |
| `item_tools.py` | `search_items` |
| `order_tools.py` | `create_order`, `update_order`, `get_order`, `update_requirements` |
| `proposal_tools.py` | `create_proposal`, `update_proposal`, `get_proposal`, `list_proposals`, `delete_proposal`, `get_proposals_by_lead` |

Tools call the internal API via `apps/IA/core/client.py` (`APIClient`) using authenticated requests.

---

## Celery Tasks Reference

| Task | Queue | Purpose |
|------|-------|---------|
| `settled_deliveries_method` | high | Create invoices for settled deliveries |
| `delete_deliveries` | default | Bulk delete deliveries with audit log |
| `run_spider_task` | low | Scrapy LinkedIn/Google scraper |
| `send_email` | default | Invoice email via SendGrid |
| `cache_refresh_tasks` | default | Redis cache invalidation |
| `rfid_packout_check` | default | RFID validation on packout |
| `create_journal_credits` | default | QuickBooks journal credits |

Periodic tasks defined in `apps/erp/periodic_tasks.py` using `django-celery-beat`.
