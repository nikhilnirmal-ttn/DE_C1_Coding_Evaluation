# Final AI Usage Summary

**Candidate:** Nikhil Kr. Nirmal  
**Project:** `DE_C1_Coding_Evaluation-Nikhil` — Databricks medallion pipeline  
**AI Tool:** Cursor  
**Assessment:** 09/09/2026 – 10/09/2026

Detailed prompt history lives in `ai-prompts/`. This file is the evaluator-facing index.

**Databricks validation:** `src/validation/pipeline_validation.sql` — **26/26 PASS** (2026-09-10, Serverless).

---

## 1. AI tools used

| Evidence | Finding |
|----------|---------|
| `tool-workflow.md`, `candidate-info.md` | **Cursor** documented as primary AI tool |
| `ai-prompts/*.md` | Per-phase prompt artifacts with evaluation sections |
| `CURSOR_START_PROMPT.md` | Incremental phase build instructions |

---

## 2. Purpose of AI usage

| Area | Role |
|------|------|
| Foundation | Requirements, design, data model, DQ strategy |
| Data generation | `generate_sample_data.py`, intentional defects, CSV output |
| Bronze | STRING ingest, dry-run validation, Databricks notebooks |
| Silver | Five DQ categories, quarantine, DQ summary, orchestration |
| Gold | Four SQL aggregates, `run_gold_pipeline` |
| Dashboard | Gold-only SQL, usage guide |
| Validation + closure | `pipeline_validation.sql`, reports, reflection, database docs |

Human review recorded in each `ai-prompts/<phase>.md` **YOUR EVALUATION** / **FINAL DECISION** section.

---

## 3. Prompt history index

| File | Phase | Content |
|------|-------|---------|
| `documentation.md` | 1 | Assessment setup, foundation docs, Databricks notebooks |
| `data-generation.md` | 2 | Sample data generator |
| `bronze-layer.md` | 3 | Bronze ingestion |
| `silver-layer.md` | 4 | Silver DQ pipeline |
| `gold-layer.md` | 5 | Gold aggregates |
| `dashboard.md` | 6 | Dashboard SQL + guide |
| `validation.md` | 7 | Pipeline validation SQL + report |
| `database.md` | 7 | Source schema documentation |

---

## 4. AI-generated / AI-assisted artifacts

| Path | Source prompt |
|------|---------------|
| `requirements-analysis.md`, `design-notes.md`, `data-model.md`, `data-quality-strategy.md`, `tool-workflow.md` | `documentation.md` |
| `src/data_generation/`, `data/*.csv` | `data-generation.md` |
| `src/bronze/` | `bronze-layer.md` |
| `src/silver/` | `silver-layer.md` |
| `src/gold/` | `gold-layer.md` |
| `src/dashboard/` | `dashboard.md` |
| `src/validation/pipeline_validation.sql`, `VALIDATION_REPORT.md` | `validation.md` |
| `database/` | `database.md` |
| `databricks/notebooks/` | `documentation.md` |
| Closure docs (`reflection.md`, this file, `debugging-notes.md`) | Phase 7 |

---

## 5. Validation approach

| Check type | Tool | Status |
|------------|------|--------|
| Bronze CSV | `ingest_all.py --dry-run` | Complete (1006/206/5163) |
| Silver helpers | `test_silver_helpers.py` | Complete |
| End-to-end | `pipeline_validation.sql` via `04_run_validation` | **26/26 PASS** (2026-09-10) |
| Dashboard SQL | Static review (Gold-only) | Complete |

Databricks results recorded in `VALIDATION_REPORT.md` after notebook 04 execution.

---

## 6. Rules followed

- No secrets or credentials in repository
- Original work in `DE_C1_Coding_Evaluation-Nikhil` (not copied submission)
- Incremental phases with `ai-prompts/` provenance
- Delta Lake + Unity Catalog on Databricks
- Line-item order grain throughout
