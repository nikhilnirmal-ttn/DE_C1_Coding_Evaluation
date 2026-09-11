# DE_C1_Coding_Evaluation — Nikhil Kr. Nirmal

Databricks **Medallion Pipeline** (Bronze → Silver → Gold) for e-commerce data: **customers**, **orders**, **products**.

Built with **Cursor** for the AI Capability Assessment (C1).

## Your details

| Field | Value |
|-------|-------|
| Name | Nikhil Kr. Nirmal |
| Role | SE |
| Start | 09/09/2026 |
| Submission | 10/09/2026 |
| Databricks | `nikhil.nirmal@tothenew.com` |

## Project status

| Phase | Status |
|-------|--------|
| Phase 1: Foundation docs | **Complete** |
| Phase 2: Data generation | **Complete** |
| Phase 3: Bronze | **Complete** (expected 1006/206/5163) |
| Phase 4: Silver | **Complete** (5 DQ categories + quarantine) |
| Phase 5: Gold | **Complete** (4 analytical tables) |
| Phase 6: Dashboard | **Complete** (21 queries, 3 pages) |
| Phase 7: Validation + closure | **Complete** (26-check SQL + closure docs) |
| Databricks validation run | **Complete** — **26/26 PASS** (2026-09-10, Serverless) |

## How to run on Databricks

Upload this folder to:

```text
/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evalution
```

Run notebooks **in order**:

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | `databricks/notebooks/00_setup_catalog` | Create catalog + schemas |
| 2 | `databricks/notebooks/01_run_bronze` | Ingest CSVs |
| 3 | `databricks/notebooks/02_run_silver` | Data quality + Silver tables |
| 4 | `databricks/notebooks/03_run_gold` | Gold analytics |
| 5 | `databricks/notebooks/04_run_validation` | 26/26 validation |

Full steps: `databricks/DATABRICKS_SETUP.md`

## Local validation (no Databricks)

```text
python src/bronze/ingest_all.py --dry-run
python src/silver/test_silver_helpers.py
```

Record Databricks results in `VALIDATION_REPORT.md` after notebook 04 runs.

## Architecture

```text
data/*.csv  →  Bronze  →  Silver (+ DQ)  →  Gold  →  Dashboard / Validation
```

Catalog: `de_c1_coding_evaluation` — schemas: `bronze`, `silver`, `gold`

## Closure artifacts

| Document | Purpose |
|----------|---------|
| `VALIDATION_REPORT.md` | End-to-end validation inventory |
| `reflection.md` | Project reflection |
| `final-ai-usage-summary.md` | AI usage index for evaluators |
| `debugging-notes.md` | Issue log |
| `database/` | Source schema documentation |
| `ai-prompts/` | Cursor prompt history per phase |

## AI-assisted development

Prompt history: `ai-prompts/` (Phases 1–7). Incremental build: `CURSOR_START_PROMPT.md`.
