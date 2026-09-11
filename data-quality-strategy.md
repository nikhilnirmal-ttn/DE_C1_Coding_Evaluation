# Data Quality Strategy

**Candidate:** Nikhil Kr. Nirmal

Silver layer enforces five DQ categories. Invalid records go to `silver_quarantine_records`; per-run summary in `silver_dq_summary`.

## Category 1 — Completeness

Required fields must not be null or blank.

| Entity | Required fields |
|--------|-----------------|
| customers | customer_id, customer_name, email, country, signup_date, customer_segment, lifetime_value |
| products | product_id, product_name, category, unit_price |
| orders | order_line_id, order_id, customer_id, product_id, order_date, quantity, unit_price |

## Category 2 — Uniqueness

| Entity | Unique key |
|--------|------------|
| customers | customer_id |
| products | product_id |
| orders | order_line_id |

Duplicate PKs → quarantine (keep first valid occurrence).

## Category 3 — Type Validation

| Field | Rule |
|-------|------|
| signup_date, order_date | Parseable as DATE |
| lifetime_value, unit_price, quantity | Parseable as numeric |
| email | Basic email format |

## Category 4 — Referential Integrity

| FK | Parent |
|----|--------|
| orders.customer_id | silver_customers.customer_id |
| orders.product_id | silver_products.product_id |

Orphan FKs → quarantine.

## Category 5 — Business Logic

| Rule | Description |
|------|-------------|
| Future dates | order_date, signup_date ≤ current_date |
| Positive quantity | quantity > 0 |
| Non-negative price | unit_price ≥ 0 |
| Valid segment | customer_segment in (Premium, Standard, Basic) |
| Catalog price match | orders.unit_price matches products.unit_price (quarantine only, no auto-fix) |

## Quarantine Schema

`silver_quarantine_records`: entity, record_key, check_category, check_name, failure_reason, raw_values, run_timestamp

## DQ Summary Schema

`silver_dq_summary`: entity, check_category, total_records, failed_records, pass_pct, run_timestamp
