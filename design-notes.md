# Design Notes

**Candidate:** Nikhil Kr. Nirmal

## Architecture

```text
data/*.csv  →  Bronze (STRING, raw)  →  Silver (typed + DQ)  →  Gold (analytics)  →  Dashboard
```

## Layer Responsibilities

| Layer | Schema | Responsibility |
|-------|--------|----------------|
| Bronze | `bronze` | Raw CSV ingest, all columns STRING, metadata columns added |
| Silver | `silver` | Type casting, cleansing, 5 DQ checks, quarantine bad rows |
| Gold | `gold` | Pre-computed aggregates for analytics |
| Dashboard | — | SQL visualizations reading Gold only |

## Unity Catalog

- **Catalog:** `de_c1_coding_evaluation`
- **Bronze tables:** `bronze_customers`, `bronze_products`, `bronze_orders`
- **Silver tables:** `silver_customers`, `silver_products`, `silver_orders`, `silver_quarantine_records`, `silver_dq_summary`
- **Gold tables:** `gold_sales_by_product`, `gold_revenue_by_customer`, `gold_daily_weekly_trends`, `gold_customer_segmentation`

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bronze column types | STRING | Preserve intentional defects for Silver DQ |
| Bronze write mode | overwrite | Simple full reload for assessment |
| Silver DQ | 5 categories | Per assessment requirements |
| Quarantine | Single table | Traceability for all failed records |
| Gold inputs | Silver only | Trusted layer pattern |
| Revenue metric | `quantity * unit_price` | Line-item grain |

## Execution Order (Silver)

1. Read Bronze + trim strings
2. Completeness → Uniqueness → Type validation
3. Canonical valid parents (customers, products)
4. Referential integrity (orders)
5. Business logic (all entities)
6. Write curated Silver + quarantine + DQ summary
