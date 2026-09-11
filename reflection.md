# Reflection

**Candidate:** Nikhil Kr. Nirmal  
**Project:** DE_C1_Coding_Evaluation — Databricks medallion pipeline  
**Assessment:** 09/09/2026 – 10/09/2026

Evidence-based reflection. Databricks validation executed **26/26 PASS** on 2026-09-10 (Serverless); results recorded in `VALIDATION_REPORT.md`.

---

## What I Built

An end-to-end **medallion analytics pipeline** on Databricks Unity Catalog (`de_c1_coding_evaluation`):

1. **Data generation** — reproducible CSVs (`customers`, `products`, order line items) with intentional defects for Silver DQ (seed 42; Bronze counts 1006 / 206 / 5163).
2. **Bronze** — STRING-schema CSV ingestion to Delta with metadata columns; `--dry-run` for local validation.
3. **Silver** — five DQ categories, `silver_quarantine_records`, `silver_dq_summary` (11 category rows), curated typed tables.
4. **Gold** — four analytical tables from Silver only (`line_revenue = quantity * unit_price`).
5. **Dashboard** — Gold-only SQL (`dashboard_queries.sql`, 21 queries, 3 pages) and `DASHBOARD_GUIDE.md`.
6. **Validation** — unified `pipeline_validation.sql` (26 checks with PASS/FAIL columns); **26/26 PASS** on Databricks (2026-09-10).

Prompt provenance: `ai-prompts/`, `final-ai-usage-summary.md`.

---

## How I Used AI (Cursor)

Following `tool-workflow.md`, each phase used a focused Cursor prompt with a matching `ai-prompts/<phase>.md` artifact:

| Phase | Prompt file | Outcome |
|-------|-------------|---------|
| 1 Foundation | `documentation.md` | Requirements, design, data model, DQ strategy |
| 2 Data | `data-generation.md` | Generator + CSVs with defects |
| 3 Bronze | `bronze-layer.md` | Ingest scripts + dry-run |
| 4 Silver | `silver-layer.md` | 5 DQ modules + orchestration |
| 5 Gold | `gold-layer.md` | 4 SQL aggregates + orchestrator |
| 6 Dashboard | `dashboard.md` | Dashboard SQL + guide |
| 7 Validation | `validation.md`, `database.md` | Validation SQL + closure docs |

Each artifact uses: **PROMPT SENT → AI RESPONSE → YOUR EVALUATION → FINAL DECISION**.

---

## What AI Helped With Most

- **Scaffolding** — modular Bronze/Silver Python, Gold SQL, layer notes, Databricks notebooks.
- **Silver DQ design** — five check modules aligned to `data-quality-strategy.md`.
- **Validation suite** — end-to-end SQL checks with reconciliation across Gold tables.
- **Documentation** — README, candidate info, database schema as documentary DDL.

---

## What Required Human Judgment

- Choosing STRING identifiers (`CUST0001`, `OL000001`) vs numeric IDs in source schema docs.
- Reviewing AI output before acceptance (especially Silver DQ order: business logic before referential integrity).
- Building an original project in `DE_C1_Coding_Evaluation-Nikhil`.
- Running Databricks notebooks and recording real validation results (completed 2026-09-10; see `VALIDATION_REPORT.md`).

---

## How I Validated AI Output

| Layer | Method | Status |
|-------|--------|--------|
| Data generation | Row counts, defect matrix in `DATA_GENERATION_NOTES.md` | Complete |
| Bronze | `ingest_all.py --dry-run` | Documented; re-run before submission |
| Silver | `test_silver_helpers.py` | Documented; re-run before submission |
| Gold | SQL contract review (Silver-only joins) | Complete (static) |
| Dashboard | Gold-only grep on `dashboard_queries.sql` | Complete (static) |
| End-to-end | `pipeline_validation.sql` on Databricks | **26/26 PASS** (2026-09-10) |

---

## What I Would Do Differently

- Run the full Databricks notebook sequence earlier to capture validation evidence before closure docs.
- Add Spark integration tests for Silver DQ modules (currently helper-only local tests).
- Save dashboard screenshots to `src/dashboard/screenshots/` after Gold pipeline runs.

---

## Key Learnings

- **Preserve defects in Bronze** (STRING ingest) so Silver DQ has realistic failure scenarios.
- **Reconciliation checks** across Gold tables catch grain and join errors better than row-count alone.
- **Document validation explicitly** — record real Databricks results in `VALIDATION_REPORT.md` rather than fabricating PASS outcomes.
