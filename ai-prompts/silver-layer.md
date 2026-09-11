# AI Prompts — Silver Layer (Phase 4)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 08 — Phase 4 Silver implementation

**PROMPT SENT:**

```text
Phase 4 — SILVER LAYER only.

Read: data-quality-strategy.md, BRONZE_LAYER_NOTES.md, design-notes.md

Create:
- src/silver/silver_common.py
- src/silver/01_quality_completeness.py
- src/silver/02_quality_uniqueness.py
- src/silver/03_quality_type_validation.py
- src/silver/04_quality_referential_integrity.py
- src/silver/05_quality_business_logic.py
- src/silver/06_write_dq_results.py
- src/silver/create_silver_tables.py (run_silver_pipeline)
- src/silver/test_silver_helpers.py
- src/silver/SILVER_LAYER_NOTES.md
- ai-prompts/silver-layer.md

Outputs: silver_customers, silver_products, silver_orders, silver_quarantine_records, silver_dq_summary
Catalog: de_c1_coding_evaluation, schema: silver
5 DQ categories per data-quality-strategy.md

Do NOT build Gold yet.
Run: python src/silver/test_silver_helpers.py
```

**AI RESPONSE SUMMARY:**

Created 11 Silver files under `src/silver/`. Five modular DQ scripts (completeness → uniqueness → type validation → business logic → referential integrity) feed `06_write_dq_results.py` for quarantine/summary persistence. `create_silver_tables.py` exposes `run_silver_pipeline` for Databricks notebook `02_run_silver`. STRING identifiers (`CUST0001`, `PROD0001`, `OL000001`) preserved per `data-model.md`. Quarantine/summary schemas match `data-quality-strategy.md`.

**YOUR EVALUATION:**

✓ Accepted — local helper tests passed; Databricks Silver DQ validation **8/8 PASS** (2026-09-10).

**FINAL DECISION:**

Phase 4 complete. Silver pipeline validated on Databricks Serverless; curated tables, quarantine, and `silver_dq_summary` (13 rows) behave as designed.
