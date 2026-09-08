# Book Store POS ER Diagram

This ER diagram is generated from the Django models in `backend/apps/*/models.py`.
All concrete models inherit `UUIDModel`, so each table includes:

- `id` UUID primary key
- `created_at` timestamp
- `updated_at` timestamp

```mermaid
erDiagram
    CLIENT ||--o{ BRANCH : has
    CLIENT |o--o{ USER : owns
    CLIENT |o--o{ CATEGORY : owns
    CLIENT |o--o{ PRODUCT : owns
    CLIENT |o--o{ CUSTOMER : owns

    ROLE ||--o{ USER : assigns
    BRANCH |o--o{ USER : staffs
    USER ||--o{ SESSION_TOKEN : authenticates
    USER ||--o{ AUDIT_LOG : writes
    USER ||--o{ INVENTORY_ADJUSTMENT : performs
    USER ||--o{ SALE : cashiers
    USER ||--o{ RETURN_RECORD : handles

    USER ||--o{ USER_PERMISSION : has
    PERMISSION ||--o{ USER_PERMISSION : grants

    CATEGORY |o--o{ CATEGORY : parents
    CATEGORY ||--o{ PRODUCT : classifies
    PRODUCT ||--|| INVENTORY : tracks
    BRANCH |o--o{ INVENTORY : stocks
    INVENTORY ||--o{ INVENTORY_ADJUSTMENT : records

    CUSTOMER |o--o{ SALE : makes
    SALE ||--o{ SALE_ITEM : contains
    PRODUCT ||--o{ SALE_ITEM : sold_as
    SALE ||--o{ PAYMENT : paid_by
    PAYMENT_METHOD ||--o{ PAYMENT : used_for

    SALE ||--o{ RETURN_RECORD : returned_against
    CUSTOMER |o--o{ RETURN_RECORD : requests
    RETURN_RECORD ||--o{ RETURN_ITEM : contains
    SALE_ITEM ||--o{ RETURN_ITEM : reverses
    PRODUCT ||--o{ RETURN_ITEM : returned_as
    RETURN_RECORD ||--o{ REFUND : refunded_by
    REFUND_METHOD ||--o{ REFUND : used_for

    SALE |o--o| RECEIPT : issues
    RETURN_RECORD |o--o| RECEIPT : issues

    CLIENT {
        uuid id PK
        varchar name
        varchar pos_name
        varchar primary_color
        varchar secondary_color
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    BRANCH {
        uuid id PK
        uuid client_id FK
        varchar name
        varchar code
        varchar address
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ROLE {
        uuid id PK
        varchar name UK
        text description
        datetime created_at
        datetime updated_at
    }

    PERMISSION {
        uuid id PK
        varchar name UK
        text description
        datetime created_at
        datetime updated_at
    }

    USER {
        uuid id PK
        varchar username UK
        varchar password_hash
        varchar full_name
        varchar email UK
        uuid role_id FK
        uuid client_id FK
        uuid branch_id FK
        boolean is_active
        varchar pin_hash
        datetime last_login
        datetime created_at
        datetime updated_at
    }

    USER_PERMISSION {
        uuid user_id FK
        uuid permission_id FK
    }

    SESSION_TOKEN {
        uuid id PK
        uuid user_id FK
        varchar key UK
        datetime last_used_at
        datetime created_at
        datetime updated_at
    }

    CATEGORY {
        uuid id PK
        uuid client_id FK
        varchar name UK
        text description
        uuid parent_id FK
        datetime created_at
        datetime updated_at
    }

    PRODUCT {
        uuid id PK
        uuid client_id FK
        varchar sku UK
        varchar name
        varchar author
        varchar edition
        varchar publisher
        varchar isbn
        date publication_date
        varchar language
        int page_count
        text description
        uuid category_id FK
        decimal unit_price
        decimal cost_price
        decimal tax_rate
        varchar barcode UK
        image image
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    INVENTORY {
        uuid id PK
        uuid product_id FK "one-to-one"
        uuid branch_id FK
        decimal quantity_on_hand
        decimal reorder_level
        decimal reorder_quantity
        datetime last_updated
        datetime created_at
        datetime updated_at
    }

    INVENTORY_ADJUSTMENT {
        uuid id PK
        uuid inventory_id FK
        uuid adjusted_by_id FK
        varchar adjustment_type
        decimal quantity_change
        varchar reason
        varchar reference_number
        datetime adjustment_date
        datetime created_at
        datetime updated_at
    }

    CUSTOMER {
        uuid id PK
        uuid client_id FK
        varchar first_name
        varchar last_name
        varchar phone
        varchar email
        text address
        decimal loyalty_points
        datetime created_at
        datetime updated_at
    }

    SALE {
        uuid id PK
        varchar sale_number UK
        datetime sale_date
        uuid customer_id FK
        uuid cashier_id FK
        decimal subtotal
        decimal discount_amount
        decimal tax_amount
        decimal total_amount
        varchar status
        datetime created_at
        datetime updated_at
    }

    SALE_ITEM {
        uuid id PK
        uuid sale_id FK
        uuid product_id FK
        decimal quantity
        decimal unit_price
        decimal discount_amount
        decimal tax_amount
        decimal line_total
        datetime created_at
        datetime updated_at
    }

    PAYMENT_METHOD {
        uuid id PK
        varchar name
        varchar type UK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PAYMENT {
        uuid id PK
        uuid sale_id FK
        uuid payment_method_id FK
        decimal amount
        varchar reference_number
        varchar status
        datetime payment_date
        datetime created_at
        datetime updated_at
    }

    RETURN_RECORD {
        uuid id PK
        varchar return_number UK
        uuid sale_id FK
        uuid customer_id FK
        uuid cashier_id FK
        datetime return_date
        decimal total_refund_amount
        text return_reason
        varchar status
        datetime created_at
        datetime updated_at
    }

    RETURN_ITEM {
        uuid id PK
        uuid return_record_id FK
        uuid sale_item_id FK
        uuid product_id FK
        decimal quantity
        decimal unit_price
        varchar reason
        decimal line_total
        datetime created_at
        datetime updated_at
    }

    REFUND_METHOD {
        uuid id PK
        varchar name
        varchar type UK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    REFUND {
        uuid id PK
        uuid return_record_id FK
        uuid refund_method_id FK
        decimal amount
        varchar reference_number
        varchar status
        datetime refund_date
        datetime created_at
        datetime updated_at
    }

    RECEIPT {
        uuid id PK
        uuid sale_id FK
        uuid return_record_id FK
        varchar receipt_number UK
        datetime receipt_date
        decimal total_amount
        boolean printed
        boolean emailed
        datetime created_at
        datetime updated_at
    }

    AUDIT_LOG {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar entity_type
        uuid entity_id
        json details
        ip_address ip_address
        datetime created_at
        datetime updated_at
    }
```

## Notes

- `USER_PERMISSION` represents Django's implicit many-to-many join table for `User.permissions`.
- `RETURN_RECORD` represents the Django model named `Return`; the diagram avoids using `RETURN` as an entity name because it can be confused with a keyword.
- `Receipt.sale` and `Receipt.return_record` are nullable one-to-one relationships, allowing receipts for either sales or returns.
- `Branch` has a unique constraint on `(client, code)`.
