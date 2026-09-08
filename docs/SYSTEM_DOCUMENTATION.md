# Book Store POS System Documentation

## 1. Introduction

The Book Store POS system is a web-based point-of-sale application for managing bookstore sales, stock, customers, returns, receipts, reports, company branches, and staff access. The system is built with a Django REST API backend and a Vite React frontend.

## 2. Purpose

The purpose of the system is to help a bookstore process sales accurately, track inventory levels, manage cashiers and branches, handle returns, and generate useful operational reports.

## 3. Scope

The system supports these core areas:

- Company onboarding and POS identity setup
- Owner, administrator, manager, cashier, and inventory manager roles
- Branch and cashier management
- Product and category management
- Inventory tracking and stock adjustments
- Customer records
- Sale processing and receipt creation
- Payment recording
- Return processing and refund recording
- Sales, stock balance, and stock value reports

## 4. Technology Stack

Backend:

- Python
- Django
- Django REST Framework
- SQLite database for local development
- Pandas and NumPy for report data processing
- ReportLab for PDF report generation

Frontend:

- React
- Vite
- Axios
- React Router
- TanStack Query
- React Hook Form
- Zod
- Recharts
- Tailwind CSS
- Lucide React icons

## 5. System Architecture

The application follows a client-server architecture.

The frontend is a React single-page application that sends HTTP requests to the backend API. The backend exposes REST endpoints under `/api/`, validates requests, applies business rules, persists data in the database, and returns JSON responses or downloadable report files.

Main backend modules:

- `accounts`: users, roles, sessions, companies, branches, cashier login
- `inventory`: products, categories, stock levels, inventory adjustments
- `sales`: customers, sales, sale items, sale processing
- `payments`: payment methods and payment records
- `returns`: return records, returned items, refund methods, refunds
- `reports`: receipts and sales/stock reports
- `common`: API root and audit logging

Main frontend responsibilities:

- Authenticate owners, administrators, and cashiers
- Manage products and inventory
- Process customer checkout
- Display receipts
- Handle product returns
- Generate and export reports

## 6. User Roles

The system defines the following roles:

- `OWNER`: owns and configures the company account
- `ADMIN`: manages company settings, branches, cashiers, products, and reports
- `MANAGER`: supervises sales, stock, customers, and reports
- `CASHIER`: processes sales, customers, receipts, and returns
- `INVENTORY_MANAGER`: manages products, categories, inventory, and stock reports

Role-based API permissions are enforced in the backend through `RolePermission`.

## 7. Key Functional Requirements

### 7.1 Account And Company Management

- Users can sign up and create a company profile.
- A main branch is created automatically during company signup.
- Users can log in by username or email.
- Cashiers can log in using username and PIN.
- Owners and administrators can update company settings.
- Owners and administrators can create branches.
- Owners and administrators can create and update cashier accounts.

### 7.2 Product And Category Management

- Authorized users can create, update, list, and delete products.
- Products are grouped by categories.
- Products include bookstore-specific fields such as author, edition, publisher, ISBN, publication date, language, and page count.
- Product images can be uploaded.
- Each product has pricing, cost, tax rate, SKU, and optional barcode details.

### 7.3 Inventory Management

- Inventory is created when a product is created.
- Inventory records track quantity on hand, reorder level, reorder quantity, branch, and last update time.
- Authorized users can adjust stock manually.
- Authorized users can set exact stock levels.
- Every inventory adjustment records the responsible user, adjustment type, quantity change, reason, and optional reference number.
- Inventory changes are audit logged for manual adjustments.

### 7.4 Sales Processing

- Cashiers can process sales through `/api/sales/process/`.
- A sale can include one or more sale items.
- The system checks that each item has a valid SKU and positive quantity.
- The system prevents selling more stock than is available.
- Product tax and discounts are calculated during checkout.
- Inventory is reduced when a sale is completed.
- A completed sale creates:
  - A `Sale`
  - One or more `SaleItem` records
  - A completed `Payment`
  - A sale `Receipt`
  - Inventory adjustment records

### 7.5 Payment Processing

- Payments are linked to sales.
- Payment methods include cash, credit card, debit card, gift card, mobile payment, and store credit.
- Non-cash payment methods can require a reference number.
- Cash payments validate that the tendered amount is at least the sale total.
- The system calculates customer change for cash payments.

### 7.6 Return And Refund Processing

- Returns are processed against an existing sale receipt.
- Only completed sales can be returned.
- Returned items must belong to the original sale.
- Return quantity cannot exceed the quantity originally sold after previous returns are considered.
- Inventory is increased when a return is completed.
- A completed return creates:
  - A `Return`
  - One or more `ReturnItem` records
  - A completed `Refund`
  - A return `Receipt`
  - Inventory adjustment records

### 7.7 Reports

The system supports these report types:

- `sales`: sales rows and totals for a date range
- `stock_balance`: current stock quantities and stock movements
- `stock_value`: inventory valuation using unit price and quantity

Reports can be returned as:

- JSON
- CSV
- PDF

Reports can be filtered by date range and product name.

## 8. Main API Endpoints

Authentication and account endpoints:

- `POST /api/auth/signup/`
- `POST /api/auth/login/`
- `POST /api/auth/cashier-login/`
- `GET /api/auth/client/`
- `POST /api/auth/client/`
- `PATCH /api/auth/client/`
- `GET /api/auth/branches/`
- `POST /api/auth/branches/`
- `GET /api/auth/cashiers/`
- `POST /api/auth/cashiers/`
- `PATCH /api/auth/cashiers/<user_id>/`

Resource endpoints:

- `/api/categories/`
- `/api/products/`
- `/api/inventory/`
- `/api/inventory-adjustments/`
- `/api/customers/`
- `/api/sales/`
- `/api/sale-items/`
- `/api/payment-methods/`
- `/api/payments/`
- `/api/returns/`
- `/api/refunds/`
- `/api/receipts/`

Workflow endpoints:

- `POST /api/sales/process/`
- `POST /api/inventory/adjust/`
- `POST /api/inventory/set-level/`
- `POST /api/returns/process/`
- `GET /api/reports/`
- `GET /api/reports/sales/`

## 9. Database Design

The system uses UUID primary keys for all concrete application tables. Most records include `created_at` and `updated_at` timestamps through the shared `UUIDModel`.

Main entities:

- `Client`
- `Branch`
- `Role`
- `Permission`
- `User`
- `SessionToken`
- `Category`
- `Product`
- `Inventory`
- `InventoryAdjustment`
- `Customer`
- `Sale`
- `SaleItem`
- `PaymentMethod`
- `Payment`
- `Return`
- `ReturnItem`
- `RefundMethod`
- `Refund`
- `Receipt`
- `AuditLog`

The full ER diagram is available here:

- [ER Diagram](ER_DIAGRAM.md)

## 10. Important Business Rules

- A cashier must belong to a company before processing a sale.
- A sale must contain at least one item.
- A sale item must use an active product SKU belonging to the cashier's company.
- Stock cannot go below zero during sales or manual adjustments.
- Cash tendered must be greater than or equal to the sale total.
- A return must reference a completed sale receipt.
- Returned quantity cannot exceed the available returnable quantity from the original sale item.
- Product, customer, sale, report, and inventory queries are scoped to the authenticated user's company.
- Branch-aware inventory operations use the request branch header when present.

## 11. Local Setup

Backend:

```bash
cd backend
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev -- --host 127.0.0.1
```

The frontend proxies `/api` requests to `http://127.0.0.1:8000`.

## 12. Future Improvements

Recommended improvements for future iterations:

- Add full API documentation with request and response examples.
- Add printable PDF export for the ER diagram and system documentation.
- Add stronger database constraints for multi-branch inventory where needed.
- Add more automated tests around sale processing, return processing, and role permissions.
- Add report previews in the frontend before export.
- Add audit logs for product, cashier, branch, and company setting changes.
