# AI Prompts — Bronze Layer (Phase 3)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 07 — Phase 3 Bronze implementation

**PROMPT SENT:**

```text
Phase 3 — BRONZE LAYER only.

Read: data-model.md, DATA_GENERATION_NOTES.md, design-notes.md, data/*.csv

Create:
- src/bronze/bronze_common.py
- src/bronze/01_ingest_customers.py
- src/bronze/02_ingest_orders.py
- src/bronze/03_ingest_products.py
- src/bronze/ingest_all.py
- src/bronze/BRONZE_LAYER_NOTES.md

Rules:
- All columns STRING in Bronze
- Metadata: _ingestion_timestamp, _source_file
- Delta overwrite, catalog de_c1_coding_evaluation, schema bronze
- --dry-run for local validation
- No DQ in Bronze
- Do NOT build Silver/Gold yet

Run: python src/bronze/ingest_all.py --dry-run
```

**AI RESPONSE SUMMARY:**

Created 6 Bronze files under `src/bronze/`. Orchestrator `ingest_all.py` runs customers → products → orders. STRING schema with metadata columns. Supports `--dry-run` for local CSV validation.

**YOUR EVALUATION:**

✓ Accepted — dry-run passed locally.

**FINAL DECISION:**

Phase 3 complete. Local validation results:
- bronze_customers: 1006 rows
- bronze_products: 206 rows
- bronze_orders: 5163 rows
