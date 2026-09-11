# Debugging Notes

**Candidate:** Nikhil Kr. Nirmal  
Concise log of non-trivial issues during DE_C1_Coding_Evaluation. Detailed prompt history: `ai-prompts/<phase>.md`.

---

## 1. Foundation — wrong folder open (Phase 1)

| Field | Detail |
|-------|--------|
| **Issue** | Cursor created docs in wrong workspace folder |
| **Symptom** | Files landed in reference folder instead of `-Nikhil` project |
| **Resolution** | Manually recreated foundation docs in correct project directory |
| **Prompt** | Prompt 05 in `ai-prompts/documentation.md` |

---

## 2. Bronze — dry-run without PySpark (Phase 3)

| Field | Detail |
|-------|--------|
| **Issue** | Local `--dry-run` should not require Spark |
| **Resolution** | CSV validation separated from Spark write path in `bronze_common.py` |
| **Validation** | `python src/bronze/ingest_all.py --dry-run` |
| **Prompt** | `ai-prompts/bronze-layer.md` |

---

## 3. Bronze — Databricks subprocess vs notebook Spark (Phase 3)

| Field | Detail |
|-------|--------|
| **Issue** | Subprocess ingest lacks notebook `spark` session |
| **Resolution** | `resolve_spark()`, pass `spark` from notebook; see `DATABRICKS_SETUP.md` |
| **Files** | `bronze_common.py`, `databricks/notebooks/01_run_bronze` |

---

## 4. Silver — STRING identifier preservation (Phase 4)

| Field | Detail |
|-------|--------|
| **Issue** | Risk of casting `customer_id` / `order_line_id` to numeric |
| **Resolution** | Identifiers remain STRING per `data-model.md`; typed columns only where documented |
| **Files** | `silver_common.py`, `create_silver_tables.py` |

---

## 5. Silver — DQ execution order (Phase 4)

| Field | Detail |
|-------|--------|
| **Issue** | Referential integrity must use curated-eligible parent keys |
| **Resolution** | Business logic (05) before referential integrity (04) in orchestrator |
| **Files** | `06_write_dq_results.py`, `create_silver_tables.py`, `SILVER_LAYER_NOTES.md` |

---

## 6. Gold — Silver-only joins (Phase 5)

| Field | Detail |
|-------|--------|
| **Issue** | Gold must not read Bronze or quarantine |
| **Resolution** | All four SQL files join only `silver_*` tables; verified by static review |
| **Files** | `src/gold/*.sql`, `GOLD_LAYER_NOTES.md` |

---

## 7. Dashboard — Gold-only contract (Phase 6)

| Field | Detail |
|-------|--------|
| **Issue** | Dashboard queries must not join Silver/Bronze |
| **Resolution** | All 21 queries use `de_c1_coding_evaluation.gold.*` only |
| **Validation** | Static grep review — **PASS** |

---

## 8. Validation SQL — schema alignment (Phase 7)

| Field | Detail |
|-------|--------|
| **Issue** | Reference validation scripts use different column names (`table_name`, `rows_failed`, numeric orphan IDs) |
| **Resolution** | Adapted checks to this project: `entity`, `failed_records`, `CUST9999`/`PROD9999`, `period_type`, 11 DQ summary rows |
| **Files** | `src/validation/pipeline_validation.sql` |
| **Status** | **26/26 PASS** on Databricks (2026-09-10) — see `VALIDATION_REPORT.md` |

---

## 9. Operator actions (completed)

| Action | Status |
|--------|--------|
| Run Databricks notebooks 00–04 | **Complete** — catalog populated, validation executed |
| Update `VALIDATION_REPORT.md` | **Complete** — 26/26 PASS recorded (2026-09-10) |
| Optional: dashboard screenshots | Not required — SQL + guide submitted |
