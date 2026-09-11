# Final Validation Report — DE_C1_Coding_Evaluation

**Candidate:** Nikhil Kr. Nirmal  
**Date:** 2026-09-10  
**Scope:** End-to-end medallion pipeline (Bronze → Silver → Gold → Dashboard)  
**Validation artifact:** `src/validation/pipeline_validation.sql` (26 checks)  
**Databricks notebook:** `databricks/notebooks/04_run_validation`  
**Databricks user:** `nikhil.nirmal@tothenew.com`  
**Catalog:** `de_c1_coding_evaluation`

---

## Executive summary

| Item | Status |
|------|--------|
| Validation SQL authored | **Complete** (26 checks with `check_name`, `expected`, `actual`, `status`) |
| Databricks execution | **26 / 26 PASS** (2026-09-10, Serverless) |
| Local Bronze dry-run | Available — `python src/bronze/ingest_all.py --dry-run` |
| Local Silver helper tests | Available — `python src/silver/test_silver_helpers.py` |
| GitHub repository | `https://github.com/nikhilnirmal-ttn/DE_C1_Coding_Evaluation` |

**Final validation status: 26 / 26 PASS**

---

## 1. Repository structure reviewed

| Area | Path | Status |
|------|------|--------|
| Foundation docs | `requirements-analysis.md`, `design-notes.md`, `data-model.md`, `data-quality-strategy.md`, `tool-workflow.md` | Present |
| Data generation | `src/data_generation/`, `data/*.csv` | Complete |
| Bronze | `src/bronze/`, `BRONZE_LAYER_NOTES.md` | Complete |
| Silver | `src/silver/`, `SILVER_LAYER_NOTES.md`, 5 DQ modules | Complete |
| Gold | `src/gold/*.sql`, `create_gold_tables.py`, `GOLD_LAYER_NOTES.md` | Complete |
| Dashboard | `src/dashboard/dashboard_queries.sql`, `DASHBOARD_GUIDE.md` | Complete |
| Validation | `src/validation/pipeline_validation.sql` | **Complete (Phase 7)** |
| Closure | `reflection.md`, `final-ai-usage-summary.md`, `debugging-notes.md` | **Complete (Phase 7)** |
| Database docs | `database/schema.sql`, seed/setup notes | **Complete (Phase 7)** |
| AI prompt history | `ai-prompts/*.md` | Present per phase |

---

## 2. Validation check inventory (26 checks)

| # | Section | check_name | Expected (summary) | Databricks status |
|---|---------|------------|-------------------|-------------------|
| 1 | A | `bronze_row_counts` | customers=1006; products=206; orders=5163 | **PASS** |
| 2 | A | `bronze_customers_columns` | 7 business columns | **PASS** |
| 3 | A | `bronze_orphan_customer_ids` | >= 1 (CUST9999) | **PASS** |
| 4 | A | `bronze_orphan_product_ids` | >= 1 (PROD9999) | **PASS** |
| 5 | B | `silver_curated_less_than_bronze` | silver < bronze; all > 0 | **PASS** |
| 6 | B | `silver_dq_summary_rows` | 13 | **PASS** |
| 7 | B | `silver_ri_orders_failed` | > 0 | **PASS** |
| 8 | B | `silver_completeness_customers_failed` | > 0 | **PASS** |
| 9 | B | `silver_orphan_product_fks` | 0 | **PASS** |
| 10 | B | `silver_orphan_customer_fks` | 0 | **PASS** |
| 11 | B | `silver_quarantine_non_empty` | > 0 | **PASS** |
| 12 | B | `silver_customers_pk_unique` | 0 duplicates | **PASS** |
| 13 | C | `gold_tables_non_empty` | all four Gold tables > 0 | **PASS** |
| 14 | C | `gold_sales_by_product_unique_grain` | 0 duplicate product_id | **PASS** |
| 15 | C | `gold_revenue_by_customer_unique_grain` | 0 duplicate customer_id | **PASS** |
| 16 | C | `gold_trend_period_types` | daily > 0 AND weekly > 0 | **PASS** |
| 17 | C | `gold_segmentation_three_segments` | 3 segments (Premium/Standard/Basic) | **PASS** |
| 18 | C | `gold_sales_products_in_silver_catalog` | 0 orphan products | **PASS** |
| 19 | D | `gold_revenue_reconciliation` | sales = customer = segmentation = daily = weekly | **PASS** |
| 20 | D | `gold_line_items_match_silver_orders` | gold line items = silver order count | **PASS** |
| 21 | D | `gold_order_count_reconciliation` | silver distinct = daily sum = weekly sum | **PASS** |
| 22 | D | `gold_weekly_order_count_matches_daily` | weekly sum = daily sum | **PASS** |
| 23 | D | `gold_segmentation_customer_count` | segmentation sum = silver_customers | **PASS** |
| 24 | D | `silver_to_gold_revenue_reconciliation` | SUM(qty×price) silver = gold sales | **PASS** |
| 25 | E | `dashboard_top10_revenue_sort` | 10 rows; descending | **PASS** |
| 26 | E | `dashboard_top10_quantity_sort` | 10 rows; descending | **PASS** |

---

## 3. Local validation (no Databricks)

| Check | Command | Status |
|-------|---------|--------|
| Bronze CSV validation | `python src/bronze/ingest_all.py --dry-run` | Available (not required for Databricks PASS) |
| Silver helper unit tests | `python src/silver/test_silver_helpers.py` | Available (not required for Databricks PASS) |
| Dashboard Gold-only SQL | Static grep — only `de_c1_coding_evaluation.gold.*` | **PASS** (static review) |

---

## 4. Databricks execution

1. Repo path: `/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evaluation`
2. Notebooks run in order: `00_setup_catalog` → `01_run_bronze` → `02_run_silver` → `03_run_gold` → `04_run_validation`
3. Validation executed via marker-based parsing in `04_run_validation` (reads `pipeline_validation.sql`)
4. **Result: VALIDATION SUMMARY: 26/26 PASS** (2026-09-10)

**Bronze baseline confirmed:** customers **1006**, products **206**, orders **5163**.

**Gold table row counts (post-run):** `gold_sales_by_product` 199, `gold_revenue_by_customer` 932, `gold_daily_weekly_trends` 1001, `gold_customer_segmentation` 3 (segment-level grain).

---

## 5. Layer validation design

### Bronze (4 checks)

Row counts match seed-42 CSVs; customers schema present; intentional RI defects (`CUST9999`, `PROD9999`) preserved in raw Bronze.

### Silver DQ (8 checks)

Curated tables smaller than Bronze; `silver_dq_summary` has **13** rows (3+3+3+1+3 per `06_write_dq_results.py`); RI and completeness failures detected; quarantine populated; **zero** orphan FKs in curated orders; PK uniqueness.

### Gold (6 checks)

Four tables populated; unique grains; daily + weekly trends (`period_type` = `daily` / `weekly`); three master segments; products traceable to Silver catalog.

### Reconciliation (6 checks)

Revenue and order metrics reconcile across Gold tables and back to Silver `quantity * unit_price`. Order-count check compares `COUNT(DISTINCT order_id)` in Silver to `SUM(order_count)` in daily and weekly Gold trends.

### Dashboard logic (2 checks)

Top-10 sort order validation for revenue and quantity queries used in `dashboard_queries.sql`.

---

## 6. Fixes applied during validation

| Issue | Resolution |
|-------|--------------|
| `gold_order_count_reconciliation` FAIL | Updated D3 to compare silver distinct orders vs daily/weekly trend sums (not per-product `order_count` sum) |
| `silver_dq_summary_rows` FAIL | Corrected expected row count from 11 to **13** |
| Gold tables missing | Fixed REPO path typo (`Evalution` → `Evaluation`) in notebooks 01–04 |
| `time_grain` column error | Gold trends use `period_type` (`daily` / `weekly`), not `time_grain` |

---

## 7. Summary decision

| Layer | Validation status |
|-------|-------------------|
| Bronze | **PASS** (4/4) |
| Silver DQ | **PASS** (8/8) |
| Gold | **PASS** (6/6) |
| Reconciliation | **PASS** (6/6) |
| Dashboard logic | **PASS** (2/2) |
| Unified SQL (`pipeline_validation.sql`) | **26 / 26 PASS** |

**Overall: Submission-ready.** All pipeline layers validated on Databricks Serverless (2026-09-10).
