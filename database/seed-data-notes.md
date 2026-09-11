# Seed Data Notes — Source CSV Datasets

**Candidate:** Nikhil Kr. Nirmal

Documents the **seed / sample source data** for `DE_C1_Coding_Evaluation` and how it relates to `database/schema.sql`.

---

## Purpose

Committed CSV files under `data/` are the **authoritative seed datasets**. They feed the medallion pipeline:

```text
CSV seed data (data/)
    -> Bronze raw ingest (STRING columns, defects preserved)
    -> Silver validation / DQ
    -> Gold analytics
    -> Dashboard (Gold-only)
```

The `database/` directory documents the **source-side contract**. It does not replace Bronze, Silver, or Gold on Databricks.

---

## Seed files

| File | Role | Rows |
|------|------|------|
| `data/customers.csv` | Customer dimension | **1,006** |
| `data/products.csv` | Product dimension | **206** |
| `data/orders.csv` | Order **line items** | **5,163** |

Bronze validation expects exactly these counts (`pipeline_validation.sql` check `bronze_row_counts`).

---

## Generator

| Item | Location |
|------|----------|
| Script | `src/data_generation/generate_sample_data.py` |
| Design notes | `src/data_generation/DATA_GENERATION_NOTES.md` |
| Prompt history | `ai-prompts/data-generation.md` |

Stdlib-only Python. Default seed **42** reproduces committed volumes (1,000 + 6 defect customers, etc.).

---

## Schema alignment

| Dataset | Primary key | Grain | ID format |
|---------|-------------|-------|-----------|
| customers | `customer_id` | One row per customer | `CUST0001` … |
| products | `product_id` | One row per product | `PROD0001` … |
| orders | `order_line_id` | One row per line item | `OL000001` … |

Logical foreign keys on orders:

- `customer_id` → `customers.customer_id`
- `product_id` → `products.product_id`

---

## Intentional defects (for Silver DQ)

Seed data is **not clean by design**. Defects are appended after valid rows so Silver can keep the first valid PK occurrence.

Categories (see `DATA_GENERATION_NOTES.md`):

| Category | Examples |
|----------|----------|
| Completeness | Blank required fields |
| Uniqueness | Duplicate `CUST0001`, `PROD0001`, first `order_line_id` |
| Type validation | Invalid email, dates, numerics |
| Referential integrity | `CUST9999`, `PROD9999` orphan FKs (5 rows each in orders) |
| Business logic | Future dates, qty ≤ 0, negative prices, invalid segment, catalog price mismatch |

Bronze preserves all defects as STRING. Silver quarantines failures per `data-quality-strategy.md`.

---

## Reproducibility

```text
python src/data_generation/generate_sample_data.py
```

Run from project root. Overwrites `data/*.csv` with seed-42 output.

---

## What is NOT in seed data

- `total_amount` or order-header table (line-item grain only)
- Derived metrics stored in CSV (`line_revenue` computed in Gold)
- Clean production-quality data (defects are intentional)
