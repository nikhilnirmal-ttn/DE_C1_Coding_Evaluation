# AI Prompts — Validation (Phase 7)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 11 — Phase 7 validation + project closure

**PROMPT SENT:**

```text
Phase 7 — PIPELINE VALIDATION + PROJECT CLOSURE.

Read: all layer notes, design-notes.md, data-quality-strategy.md

Create:
- src/validation/pipeline_validation.sql (end-to-end checks: Bronze, Silver DQ, Gold, reconciliation)
- VALIDATION_REPORT.md
- ai-prompts/validation.md
- reflection.md
- final-ai-usage-summary.md
- debugging-notes.md
- database/schema.sql
- database/seed-data-notes.md
- database/setup-notes.md
- ai-prompts/database.md
- Update candidate-info.md — mark ALL steps Complete
- Update README.md — final status

Target: validation checks with PASS/FAIL status columns.
Bronze expected: customers=1006, products=206, orders=5163.

Do NOT fabricate Databricks results — mark validation as "pending Databricks run" until executed.
```

**AI RESPONSE SUMMARY:**

Created `src/validation/pipeline_validation.sql` with **26 checks** across five sections (Bronze 4, Silver 8, Gold 6, reconciliation 6, dashboard 2). Each check returns `check_name`, `expected`, `actual`, and `status` (PASS/FAIL). Checks use this project's schema: STRING business keys (`CUST9999`/`PROD9999` orphans), `silver_dq_summary.entity` + `failed_records` (11 summary rows), Gold `period_type` daily/weekly, segment-level `gold_customer_segmentation`.

Added closure artifacts: `VALIDATION_REPORT.md`, `reflection.md`, `final-ai-usage-summary.md`, `debugging-notes.md`, `database/` schema and setup docs, `ai-prompts/database.md`. Updated `candidate-info.md` and `README.md` to final Complete status. Databricks validation later recorded as **26/26 PASS** (2026-09-10).

**YOUR EVALUATION:**

✓ Accepted — Databricks run recorded in `VALIDATION_REPORT.md`: **26/26 PASS** (2026-09-10, Serverless).

**FINAL DECISION:**

Phase 7 complete. Unified `pipeline_validation.sql` validated end-to-end; closure docs and database schema finalized. Submission-ready.
