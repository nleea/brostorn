# Features — Balfurd ERP

## CRM Module
**Lead lifecycle management** from cold prospecting to closed deal:
- Lead status progression: `prospect → awareness → lead_capture → mql → sql → opportunities → closed`
- Cold prospecting tracking: `cold_call`, `cold_drop` with timestamps
- Multiple billing fields per lead (name, address, city, state, zip)
- Happiness/rating metrics, agreed_value
- Social network ArrayField (multiple platforms)
- Sales rep assignment

**Contact Management**
- Multiple contacts per lead
- Primary contact flag
- Role categorization

**Orders & Proposals**
- Frequency-based ordering: daily, weekly, twice_a_month, once_a_month, etc.
- Day-of-week scheduling per OrderItem (mon-sun booleans)
- Proposals with deal attributes: promotions, bounties, competitor deals, redlines
- Commission tracking, billing percentage, multipliers
- CAM/FTS pricing flags

**Contracts**
- Start/expiration dates with renewal frequency
- Agreed value and payment terms

## ERP Module
**Delivery Management**
- Status tracking: packing → picked_up → delivered
- Settled and locked flags
- Full financial breakdown: subtotal, CAM, taxes, local taxes, FTS, card feed
- Payment type tracking (credit card, check, etc.)
- Signature and photo capture
- RFID-tracked items via ItemStatus M2M
- Pre-invoice PDF generation

**Invoice Generation**
- Auto-linked to delivery (OneToOne)
- Status: DUE / PAID / OVERDUE
- Unique invoice number
- Total, Helcim total, collected total tracking
- Credit application (M2M)
- Late fee tracking (JSONField)
- Celery task: `settled_deliveries_method` (high queue)

**Payment Processing**
- Helcim integration for card payments
- Webhook handling for payment confirmation
- Credit notes (Credit model)
- CollectedMoney for cash/check
- ApplyPayments for payment reconciliation

**Work Orders & Payroll**
- Service work order tracking
- Payroll record management

## SKU / Inventory
- Item catalog with 3 pricing tiers (tier_1, tier_2, tier_3)
- CAM percentage with exempt flag
- Auto-replacement percentage
- Weight tracking for invoice_type=weight leads
- Pack size (1-1000 units)
- Core item flag
- Barcode support
- Revenue class categorization

## Operations
**Route Management**
- Named route templates (RouteName)
- Daily route instances with driver assignment
- Distance and hours tracking
- Route status and is_out flag for real-time tracking

**RFID & Inventory Tracking**
- RFID tag movement tracking
- Packout validation via Celery task
- RFID endpoint logging middleware (all API calls logged)
- Blacklist management for lost/damaged tags
- Station reset functionality

## AI Agent (apps/IA)
**Capabilities**:
- Natural language interface for sales operations
- Create and update orders and proposals from chat
- Search leads and items
- Maintains session history (last 50 messages per session)
- React agent pattern with GPT-4o

**User Workflow**:
1. Sales rep opens chat
2. Describes what they need ("Create a proposal for lead XYZ with weekly service")
3. Agent searches relevant data via tools
4. Agent creates/updates records via authenticated API calls
5. Confirms action to user

## Reporting & Analytics
- Revenue by lead, revenue class analysis
- Capital and cost tracking
- Statement reports and payment class analysis
- RFID movement analytics
- Log viewer for endpoint activity

## Integrations
| Integration | Purpose |
|-------------|---------|
| QuickBooks | Journal entries, credits, collections sync |
| Helcim | Card payment processing + webhooks |
| SendGrid | Invoice emails and notifications |
| Slack | Lead notifications to sales team |
| Google Maps | Address validation and routing |
| AWS S3 | Document and image storage |
| Scrapy | LinkedIn/Google lead prospecting |
| Stripe | Subscription billing |
| OpenAI/GPT-4o | AI agent backbone |

## Subscriptions
- User-level subscription management
- Stripe integration

## Asset Management
- Fixed asset tracking
- Straight-line depreciation calculation
- Asset cost and useful life tracking

## Security & Compliance
- JWT token rotation with blacklisting
- RBAC: view-level access control per role
- Full audit trail for all state-changing operations
- RFID endpoint logging for all API activity
- Soft deletes (is_active=False) preserving history
- CSRF protection, CORS headers configured
