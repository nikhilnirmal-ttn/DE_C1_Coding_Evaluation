# AI Prompts — Phase 2 Data Generation

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 06 — Phase 2 data generation

### PROMPT SENT

```text
Phase 2 — DATA GENERATION only.

Read: requirements-analysis.md, design-notes.md, data-model.md, data-quality-strategy.md

Create:
- src/data_generation/generate_sample_data.py
- src/data_generation/DATA_GENERATION_NOTES.md
- data/customers.csv, data/products.csv, data/orders.csv

Rules:
- seed 42, reproducible
- orders at LINE-ITEM grain
- intentional defects for Silver DQ (nulls, duplicates, bad dates, orphan FKs, negative prices)
- Python stdlib only
- Do NOT build Bronze/Silver/Gold yet

After done, run: python src/data_generation/generate_sample_data.py
```

### AI RESPONSE SUMMARY

Created the generator (stdlib, `random.seed(42)`), notes, and CSVs. Orders are line-item grain (`order_line_id` PK, 1–3 lines per `order_id`). Defects cover the five Silver DQ categories. Row counts match Databricks expected Bronze sizes: 1006 / 206 / 5163. Script executed successfully.

### YOUR EVALUATION

✓ Accepted

### FINAL DECISION

Keep generator + CSVs as source of truth for later Bronze ingest. Do not start Bronze/Silver/Gold in this phase.
