# Paste this entire prompt in a NEW Cursor chat tab

Open folder: `DE_C1_Coding_Evaluation-Nikhil` in Cursor, then paste below.

---

```text
You are my Lead Data Engineer. Build the DE_C1 Coding Evaluation medallion pipeline in THIS folder.

Candidate: Nikhil Kr. Nirmal, SE, Assessment 09/09/2026–10/09/2026
Databricks: nikhil.nirmal@tothenew.com
Catalog: de_c1_coding_evaluation
GitHub: nikhilnirmal-ttn/DE_C1_Coding_Evaluation

Build incrementally. After EACH phase, update ai-prompts/<phase>.md with PROMPT SENT / AI RESPONSE / YOUR EVALUATION / FINAL DECISION.

Phase 1 — Foundation docs: requirements-analysis.md, design-notes.md, data-model.md, data-quality-strategy.md, tool-workflow.md, update README.md

Phase 2 — Data generation: src/data_generation/generate_sample_data.py, DATA_GENERATION_NOTES.md, data/*.csv (seed 42, intentional defects for Silver DQ)

Phase 3 — Bronze: src/bronze/ (STRING schema, Delta, ingest_all.py, --dry-run), BRONZE_LAYER_NOTES.md, ai-prompts/bronze-layer.md

Phase 4 — Silver: 5 DQ categories, quarantine, DQ summary, create_silver_tables.py, SILVER_LAYER_NOTES.md, ai-prompts/silver-layer.md

Phase 5 — Gold: 4 SQL files + create_gold_tables.py, GOLD_LAYER_NOTES.md, ai-prompts/gold-layer.md

Phase 6 — Dashboard: dashboard_queries.sql, DASHBOARD_GUIDE.md, ai-prompts/dashboard.md

Phase 7 — Validation: src/validation/pipeline_validation.sql, VALIDATION_REPORT.md, ai-prompts/validation.md

Phase 8 — Closure: reflection.md, final-ai-usage-summary.md, debugging-notes.md, update candidate-info.md all Complete

Rules: no secrets, Delta on Databricks, line-item orders, document everything, do not skip ai-prompts.

Start with Phase 1 now.
```
