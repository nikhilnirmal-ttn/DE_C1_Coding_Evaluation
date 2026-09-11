# Data Model

**Candidate:** Nikhil Kr. Nirmal | **Grain:** Order line items

## Entities

### customers

| Column | Type | Notes |
|--------|------|-------|
| customer_id | STRING | PK |
| customer_name | STRING | Required |
| email | STRING | Required |
| country | STRING | Required |
| signup_date | STRING | Required (parsed in Silver) |
| customer_segment | STRING | Premium / Standard / Basic |
| lifetime_value | STRING | Numeric string |

### products

| Column | Type | Notes |
|--------|------|-------|
| product_id | STRING | PK |
| product_name | STRING | Required |
| category | STRING | Required |
| unit_price | STRING | Numeric string |

### orders (line items)

| Column | Type | Notes |
|--------|------|-------|
| order_line_id | STRING | PK — unique per row |
| order_id | STRING | Groups 1–3 lines per order |
| customer_id | STRING | FK → customers |
| product_id | STRING | FK → products |
| order_date | STRING | Required |
| quantity | STRING | Integer string |
| unit_price | STRING | Price at time of order |

## Relationships

```text
customers (1) ──< orders (many)
products  (1) ──< orders (many)
order_id groups multiple order_line_id rows
```

## Revenue

```text
line_revenue = quantity × unit_price  (computed in Gold)
```
