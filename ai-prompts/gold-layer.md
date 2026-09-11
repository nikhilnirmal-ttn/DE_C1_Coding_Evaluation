# AI Prompts — Gold Layer (Phase 5)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 09 — Phase 5 Gold implementation

**PROMPT SENT:**

```text
Phase 5 — GOLD LAYER only.

Read: SILVER_LAYER_NOTES.md, design-notes.md, data-model.md

Create:
- src/gold/01_sales_by_product.sql
- src/gold/02_revenue_by_customer.sql
- src/gold/03_daily_weekly_trends.sql
- src/gold/04_customer_segmentation.sql
- src/gold/create_gold_tables.py (run_gold_pipeline)
- src/gold/GOLD_LAYER_NOTES.md
- ai-prompts/gold-layer.md

Rules:
- Gold reads ONLY from Silver tables (de_c1_coding_evaluation.silver.*)
- line_revenue = quantity * unit_price
- order_count = count(distinct order_id)
- Do NOT read Bronze or quarantine tables

Do NOT build Dashboard yet.
```

**AI RESPONSE SUMMARY:**

Created 7 Gold files under `src/gold/` plus this prompt artifact. Four SQL scripts build Delta tables via `CREATE OR REPLACE TABLE`, joining only `silver_orders` with `silver_products` / `silver_customers`. Revenue uses `quantity * unit_price`; order volume uses `COUNT(DISTINCT order_id)`. `create_gold_tables.py` exposes `run_gold_pipeline` for Databricks notebook `03_run_gold`.

**YOUR EVALUATION:**

✓ Accepted — Gold tables built from Silver only; Databricks Gold validation **6/6 PASS** (2026-09-10).

**FINAL DECISION:**

Phase 5 complete. Four Gold tables populated with correct grains and reconciliation to Silver (`gold_sales_by_product` 199, `gold_revenue_by_customer` 932, `gold_daily_weekly_trends` 1001, `gold_customer_segmentation` 3).
