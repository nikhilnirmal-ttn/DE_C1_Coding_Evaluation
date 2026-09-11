# Silver Layer Notes

**Candidate:** Nikhil Kr. Nirmal  
**Phase:** 4 — Silver DQ and curated tables  
**Catalog:** `de_c1_coding_evaluation`  
**Schema:** `silver`

## Purpose

Transform Bronze STRING tables into typed, curated Silver tables with five DQ categories. Invalid rows route to `silver_quarantine_records`; per-run metrics land in `silver_dq_summary`.

## Tables

| Table | Source | Write mode |
|-------|--------|------------|
| `silver_customers` | `bronze_customers` (1,006 rows) | Delta overwrite |
| `silver_products` | `bronze_products` (206 rows) | Delta overwrite |
| `silver_orders` | `bronze_orders` (5,163 rows) | Delta overwrite |
| `silver_quarantine_records` | All DQ failures | Delta overwrite |
| `silver_dq_summary` | Per-category metrics | Delta overwrite |

## Execution flow

```text
Bronze (STRING)
  → trim + safe type parsing
  → 01 completeness
  → 02 uniqueness (deterministic first-occurrence canonical)
  → 03 type validation
  → 05 business logic (customers, products)
  → 04 referential integrity (orders vs curated-eligible parents)
  → 06 quarantine + DQ summary
  → curated silver_customers / silver_products / silver_orders
```

Referential integrity runs **after** business logic so parent keys match the same population written to curated dimension tables.

## Silver output types

| Entity | Typed columns |
|--------|---------------|
| customers | `signup_date` DATE, `lifetime_value` DECIMAL(12,2) |
| products | `unit_price` DECIMAL(10,2) |
| orders | `order_date` DATE, `quantity` INT, `unit_price` DECIMAL(10,2) |

Identifier columns (`customer_id`, `product_id`, `order_line_id`, `order_id`) remain STRING (e.g. `CUST0001`, `PROD0001`, `OL000001`).

## Five DQ categories

Per `data-quality-strategy.md`:

1. **Completeness** — required fields non-null/non-blank
2. **Uniqueness** — PK uniqueness; duplicates quarantined (first valid occurrence kept)
3. **Type validation** — ISO dates, numeric fields, email format
4. **Referential integrity** — `orders.customer_id` / `orders.product_id` → curated parents
5. **Business logic** — future dates, positive quantity, non-negative price, valid segment, catalog price match (quarantine only)

## Quarantine schema

`silver_quarantine_records`: `entity`, `record_key`, `check_category`, `check_name`, `failure_reason`, `raw_values`, `run_timestamp`

## DQ summary schema

`silver_dq_summary`: `entity`, `check_category`, `total_records`, `failed_records`, `pass_pct`, `run_timestamp`

Summary `failed_records` = distinct `record_key` count per category (row-oriented, not failure-record count).

## Scripts

| Script | Role |
|--------|------|
| `silver_common.py` | Config, helpers, Spark utilities |
| `01_quality_completeness.py` | Completeness checks |
| `02_quality_uniqueness.py` | PK uniqueness |
| `03_quality_type_validation.py` | Date/numeric/email validation |
| `04_quality_referential_integrity.py` | Order FK checks |
| `05_quality_business_logic.py` | Domain rules |
| `06_write_dq_results.py` | Quarantine + summary writes |
| `create_silver_tables.py` | `run_silver_pipeline` orchestrator |
| `test_silver_helpers.py` | Local helper unit tests (no Spark) |

## Local validation

```text
python src/silver/test_silver_helpers.py
```

## Databricks execution

1. Run `databricks/notebooks/00_setup_catalog`
2. Run `databricks/notebooks/01_run_bronze`
3. Run `databricks/notebooks/02_run_silver`

The notebook imports `run_silver_pipeline` from `create_silver_tables.py`.

## Out of scope (later phases)

- Gold aggregates and dashboard SQL
- Validation report (`26/26` checks)
