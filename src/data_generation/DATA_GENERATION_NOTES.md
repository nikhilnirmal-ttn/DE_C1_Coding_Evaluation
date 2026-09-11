# Data Generation Notes

**Candidate:** Nikhil Kr. Nirmal  
**Phase:** 2 — Data generation only  
**Script:** `src/data_generation/generate_sample_data.py`

## How to regenerate

```text
python src/data_generation/generate_sample_data.py
```

Run from the project root. Output files overwrite `data/*.csv`.

## Constraints

| Rule | Implementation |
|------|----------------|
| Reproducible | `random.seed(42)` before any random draws |
| Grain | `orders.csv` is **one row per order line** (`order_line_id` PK; `order_id` groups 1–3 lines) |
| Library | Python **stdlib only** (`csv`, `random`, `datetime`, `pathlib`) |
| Types | All CSV values are strings so Bronze can land as STRING and preserve defects |
| Scope | No Bronze / Silver / Gold code in this phase |

## Volumes (matches Databricks expected Bronze counts)

| File | Valid rows | Intentional defect rows | Total |
|------|------------|-------------------------|-------|
| `data/customers.csv` | 1000 | 6 | **1006** |
| `data/products.csv` | 200 | 6 | **206** |
| `data/orders.csv` | 5100 | 63 | **5163** |

Valid order lines use `random.randint(1, 3)` lines per `order_id`. Valid `order_date` is on/after the customer's `signup_date` and on/before `2026-09-01`. Valid `orders.unit_price` is copied from the catalog product.

## Schema (line-item grain)

See `data-model.md`. Columns written:

- **customers:** `customer_id`, `customer_name`, `email`, `country`, `signup_date`, `customer_segment`, `lifetime_value`
- **products:** `product_id`, `product_name`, `category`, `unit_price`
- **orders:** `order_line_id`, `order_id`, `customer_id`, `product_id`, `order_date`, `quantity`, `unit_price`

## Intentional defects (for Silver DQ)

Defects are **appended after** valid rows so Silver can keep the first valid PK occurrence.

### Completeness (null / blank required fields)

- Customers: blank `customer_name`; blank `country`
- Products: blank `product_name`; blank `category`; blank `product_id`
- Orders: one blank for each required column (`order_line_id` through `unit_price`)

### Uniqueness (duplicate PKs)

- Customers: extra copy of `CUST0001`
- Products: extra copy of `PROD0001`
- Orders: two extra copies of the first valid `order_line_id`

### Type validation

- Customers: `email` = `not-an-email`; `lifetime_value` = `not-a-number`; `signup_date` = `31/02/2024`
- Products: `unit_price` = `free`
- Orders: `order_date` = `not-a-date` / `2024-13-40`; `quantity` = `two`; `unit_price` = `abc`

### Referential integrity (orphan FKs)

- Orders with `customer_id` = `CUST9999` (not in customers)
- Orders with `product_id` = `PROD9999` (not in products)

### Business logic

- Future dates: customer `signup_date` `2099-01-15`; order `order_date` `2099-12-31` and `2030-01-01`
- Quantity: `0` and negative (`-3`, `-1`)
- Negative prices: product `unit_price` `-15.00`; order `unit_price` `-25.50`
- Invalid segment: `VIP` (not in Premium / Standard / Basic)
- Catalog price mismatch: order `unit_price` = catalog price + `50.00` (quarantine only; no auto-fix)

## What this phase does not do

Does not create Bronze ingest, Silver DQ modules, Gold aggregates, or Databricks table writes. Defects stay in the CSVs so Bronze can ingest them as raw STRING.
