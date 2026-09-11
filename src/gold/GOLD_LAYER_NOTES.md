# Gold Layer Notes

**Candidate:** Nikhil Kr. Nirmal  
**Phase:** 5 — Analytical aggregates  
**Catalog:** `de_c1_coding_evaluation`  
**Schema:** `gold`

## Purpose

Build pre-computed analytics tables from curated Silver entities. Gold reads **only** from `silver.silver_customers`, `silver.silver_products`, and `silver.silver_orders` — never Bronze or quarantine tables.

## Revenue rule

```text
line_revenue = quantity * unit_price
order_count  = COUNT(DISTINCT order_id)
```

## Tables

| Table | Grain | Key metrics |
|-------|-------|-------------|
| `gold_sales_by_product` | Product | `total_quantity_sold`, `total_revenue`, `order_count`, `line_item_count` |
| `gold_revenue_by_customer` | Customer | `total_revenue`, `order_count`, `total_quantity_purchased`, `line_item_count` |
| `gold_daily_weekly_trends` | Daily / weekly period | `total_revenue`, `order_count`, `line_item_count` |
| `gold_customer_segmentation` | Customer segment | `customer_count`, `order_count`, `total_revenue`, `avg_revenue_per_customer` |

All Gold tables use Delta `CREATE OR REPLACE TABLE` (full overwrite per run).

## Execution flow

```text
silver_customers ──┐
silver_products  ──┼── SQL aggregates (01–04)
silver_orders    ──┘
        ↓
gold_sales_by_product
gold_revenue_by_customer
gold_daily_weekly_trends
gold_customer_segmentation
```

## Scripts

| Script | Role |
|--------|------|
| `01_sales_by_product.sql` | Product-level sales and revenue |
| `02_revenue_by_customer.sql` | Customer-level revenue |
| `03_daily_weekly_trends.sql` | Daily + weekly time-series |
| `04_customer_segmentation.sql` | Segment rollups (includes customers with zero orders) |
| `create_gold_tables.py` | `run_gold_pipeline` orchestrator |

## Databricks execution

1. Run `databricks/notebooks/00_setup_catalog`
2. Run `databricks/notebooks/01_run_bronze`
3. Run `databricks/notebooks/02_run_silver`
4. Run `databricks/notebooks/03_run_gold`

The notebook imports `run_gold_pipeline` from `create_gold_tables.py` and passes `sql_dir=src/gold`.

## Out of scope (later phases)

- Dashboard SQL (`dashboard_queries.sql`)
- End-to-end validation report (`26/26` checks)
