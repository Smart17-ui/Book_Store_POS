#POS Frontend

Vite + React frontend for the Bookstore POS API.

## System design

- [ER diagram](../docs/ER_DIAGRAM.md)

## Run locally

```bash
cd frontend
npm install
cp .env.example .env
npm run dev -- --host 127.0.0.1
```

The Vite proxy sends `/api` requests to `http://127.0.0.1:8000`. Start Django separately:

```bash
cd backend
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

Set `VITE_CASHIER_ID` to an active backend `User` UUID to enable checkout and inventory adjustments. The frontend uses the backend authentication endpoints for account signup, owner onboarding, administrator login, and cashier PIN login.

## Implemented API workflows

- Product/category catalogue and stock-aware POS search
- Persistent cart with quantity controls
- Customer selection and creation
- Transactional sale checkout through `/api/sales/process/`
- Receipt result with print layout
- Returns through `/api/returns/process/`
- Inventory adjustments through `/api/inventory/adjust/`
- Sales reports with JSON, CSV, and PDF exports
- Company onboarding with POS identity, branches, and owner-linked accounts

## Build

```bash
npm run build
```
