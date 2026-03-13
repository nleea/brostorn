# Database Models — Balfurd ERP

## Base Pattern
**All models** inherit from `BaseModel` (`apps/default/models/base_model.py`):
```
id          UUID (PK, auto-generated)
created_at  DateTimeField (auto)
updated_at  DateTimeField (auto)
is_active   BooleanField (soft-delete flag)
is_staff    BooleanField
```

---

## users

### User (AbstractUser + BaseModel)
Email-based auth. Custom user replacing Django's default.
```
email           (unique, login field)
role            FK → Role
phone_number
title
avatar          ImageField
```

### SalesRep (BaseModel)
```
user              OneToOne → User
assigned_zip_codes CharField (multiple codes stored as string)
```

### Company (BaseModel)
```
name
users           M2M → User
```

---

## permissions

### Role (BaseModel)
```
name        (unique)
description
write_views M2M → SavedViewSet
read_views  M2M → SavedViewSet
```

### SavedViewSet (BaseModel)
```
name  (unique) — represents a UI viewset/resource name
```

---

## crm

### Lead (BaseModel) — Core entity
```
name, telephone, email
social_network      ArrayField
address             ArrayField
status              choice: prospect/awareness/lead_capture/mql/sql/opportunities/closed
substatus           CharField
billing_name, billing_state, billing_address, billing_city, billing_zip_code
contract_start_date, contract_expiration
current_provider
happiness, rating   (satisfaction metrics)
status_cart         choice: bulk/individual
agreed_value        Decimal
associated_salesRep FK → SalesRep
subtype             (required)
invoice_type        choice: amount/weight
cold_call, date_cold_call, cold_drop, date_cold_drop  (cold prospecting)
account             (unique account number for invoice generation)
```

### Contact (BaseModel)
```
lead            FK → Lead
name, email (unique), mobile, note
address         ArrayField
role
primary_contact BooleanField
```

### Order (BaseModel)
```
items           M2M → Item (through OrderItem)
frequency       choice: daily/weekly/twice_a_month/once_a_month/...
first_pre_bill  (day of week)
created_by      FK → User
```

### OrderItem (BaseModel) — Through model for Order↔Item
```
order               FK → Order
item                FK → Item
quantity
price               Decimal
requirement_percentage  0-100
frequency, twice_selected, once_selected
mon/tue/wed/thu/fri/sat/sun  BooleanFields (delivery days)
billing_item
wearer
```

### Proposal (BaseModel)
```
value               Decimal
lead                FK → Lead
order               OneToOne → Order
created_by          FK → User
code, commission    Decimal
monthly_promotion, deal_bounty, lead_RSR, competitor_deal, redline
full_cam, full_fts  BooleanFields
fts                 Decimal
dust_revenue_20, industrial_uniforms_80, tier1, core_item_deal, item_variety  BooleanFields
billing_percentage  Decimal
wearer, multiplier  (int)
year
```

### Contract (BaseModel)
```
status
description
contract_start_date, contract_expiration_date
renewal_frequency
agreed_value        Decimal
payment_terms
```

### Supporting CRM models
- `Activity` — Lead activities/notes
- `LeadHistory` — Lead status change history
- `LeadComment` — Comments on leads
- `PoundsRecord` — Weight records
- `ContractValueHistory` — Historical contract values

---

## sku

### Item (BaseModel)
```
item_code           (unique)
item_description
purchase_price, tier_1, tier_2, tier_3  Decimal (pricing tiers)
supergroups         choice field
vendor_item_code
revenue_class       choice field
cam_percentage      Decimal
cam_exempt          BooleanField
auto_replacement_percentage Decimal
weight              Decimal
barcode             CharField
pack_size           int (1-1000)
core                BooleanField
tax_exempt          BooleanField
wearer              CharField
created_by          FK → User
```

### ItemStatus (BaseModel)
Tracks inventory status per item instance.

---

## erp

### Delivery (BaseModel) — Fulfillment record
```
items               M2M → ItemStatus (through DeliveryItem)
items_from_sku      M2M → Item (through DeliveryItemFromItem)
status              choice: packing/picked_up/delivered
settled             BooleanField
locked              BooleanField
sub_total, cam, taxes, total    Decimal
subtotal_taxable, local_taxes, fts, card_feed  Decimal
type_payment        choice: CREDIT_CARD/CHECK/...
check_number
amount              Decimal
lead                FK → Lead
contract            FK → Contract
sales_rep           FK → SalesRep
created_by          FK → User
address, city, state_abbreviation, zipcode
signature           FileField
photo               FileField
pre_invoice_pdf_url
total_weight        Decimal
order               int (sequence number)
```

### Invoice (BaseModel) — Billing document
```
delivery            OneToOne → Delivery
due_date
invoice_number      (unique)
status              choice: DUE/PAID/OVERDUE/...
type_payment        choice field
total, total_helcim, total_collected  Decimal
delivery_date, payment_date
invoice_start, invoice_end
credit              M2M → Credit
created_by          FK → User
url
late_fee_invoice_sources  JSONField
```

### Supporting ERP models
- `DeliveryItem` — Through model (ItemStatus → Delivery)
- `DeliveryItemFromItem` — Through model (Item → Delivery)
- `Credit` — Credit notes
- `CollectedMoney` — Cash/check collections
- `Transit` — In-transit tracking
- `Hub` — Distribution hubs
- `WorkOrder` — Service work orders
- `Payroll` — Payroll records
- `LocalTax` — Local tax rates
- `ApplyPayments` — Payment application records
- `CustomerComment` — Customer notes
- `RentedCustomer` — Rented item customer tracking

---

## operations

### Route (BaseModel)
```
name
date
driver          FK → User
status
is_out          BooleanField
distance, hours Decimal
```

### RouteName (BaseModel)
```
name
driver          FK → User
is_active       BooleanField
```

Supporting: `RouteSchedule`, `Headquarter`, `Cart`, `DailyItems`

---

## reporting

### RfidMovement (BaseModel)
```
rfid_code
status
location
timestamps
```

Supporting: `RfidCustomer`, `RfidHistory`, `RfidBlacklist`, `RfidEndpointLog`, `Capital`, `Cost`, `FrequencyCodes`

---

## IA

### ChatSession (BaseModel)
```
user    FK → User
title
```

### ChatMessage (BaseModel)
```
session         FK → ChatSession
role            choice: human/ai/tool
content         TextField
tool_name       CharField (nullable)
tool_call_id    CharField (nullable)
tool_calls      JSONField (nullable)
```

---

## AuditLog (default app)
```
table_name      CharField
row_id          CharField (UUID of affected record)
operation       choice: INSERT/UPDATE/DELETE/PROCESS/STEP/ERROR
old_data        JSONField
new_data        JSONField
user            FK → User (nullable)
customer        CharField (nullable)
call_method     CharField
message         TextField
step            CharField
process_run_id  CharField (groups related steps)
```

---

## Relationships Overview
```
User ──────────────── SalesRep
  │                      │
  └── Role               │
       └── SavedViewSet  │
                         │
Lead ─────────────────── associated_salesRep
  │
  ├── Contact (M)
  ├── Order ──── OrderItem ──── Item (SKU)
  │     └── Proposal
  ├── Contract
  └── Delivery ─── Invoice
                      └── Credit
```
