# Database Setup Notes — Source Schema Artifact

**Candidate:** Nikhil Kr. Nirmal

How reviewers should interpret and optionally use `database/schema.sql` with the committed seed CSVs.

---

## What this directory is

| Artifact | Role |
|----------|------|
| `schema.sql` | Documentary DDL for the **source** relational model |
| `seed-data-notes.md` | Provenance of `data/*.csv` and defect strategy |
| `setup-notes.md` | This file — setup flow and limitations |

**Implemented:** schema + seed/setup **documentation**  
**Not claimed:** provisioning of an external PostgreSQL/MySQL instance

The **validated analytics pipeline** runs on **Databricks Serverless** (Unity Catalog `de_c1_coding_evaluation`).

---

## Distinctions

| Layer | Technology | Evidence |
|-------|------------|----------|
| Source schema (this directory) | Portable DDL + CSV files | `database/`, `data/` |
| Bronze / Silver / Gold | Databricks Delta Lake | `src/bronze/`, `src/silver/`, `src/gold/` |
| Dashboard | Databricks SQL | `src/dashboard/` |
| End-to-end validation | `pipeline_validation.sql` | **26/26 PASS** (2026-09-10) |

Do not conflate loading CSVs into a local RDBMS with executing the medallion pipeline on Databricks.

---

## Intended review flow

1. Read `database/schema.sql` — source tables and line-item grain.
2. Read `database/seed-data-notes.md` — row counts, seed 42, defects.
3. Inspect `data/*.csv` headers and sample rows.
4. Trace pipeline docs: `BRONZE_LAYER_NOTES.md` → `SILVER_LAYER_NOTES.md` → `GOLD_LAYER_NOTES.md`.
5. Run Databricks notebooks 00–04; results recorded in `VALIDATION_REPORT.md` (26/26 PASS).

---

## Optional: load CSVs into PostgreSQL

Not required for Databricks pipeline execution.

```sql
\i database/schema.sql
```

```bash
\copy source.customers FROM 'data/customers.csv' WITH (FORMAT csv, HEADER true);
\copy source.products  FROM 'data/products.csv'  WITH (FORMAT csv, HEADER true);
\copy source.orders    FROM 'data/orders.csv'    WITH (FORMAT csv, HEADER true);
```

```sql
SELECT 'customers' AS tbl, COUNT(*) FROM source.customers
UNION ALL SELECT 'products', COUNT(*) FROM source.products
UNION ALL SELECT 'orders', COUNT(*) FROM source.orders;
-- Expected: 1006, 206, 5163
```

### Loading notes

- Foreign keys are **not enforced** in `schema.sql` (intentional orphan keys).
- Strict DATE/DECIMAL parsing may fail on defect rows; Bronze ingests everything as STRING for that reason.
- Do not modify committed `data/*.csv` to make loads succeed.

---

## Connection to Bronze

Bronze reads CSVs directly (not via this RDBMS):

```text
python src/bronze/ingest_all.py --dry-run
```

Databricks: `databricks/notebooks/01_run_bronze`

Bronze tables: `bronze.bronze_customers`, `bronze.bronze_products`, `bronze.bronze_orders` — all STRING.

---

## Validation performed (artifact-level)

| Check | Result |
|-------|--------|
| `schema.sql` columns match CSV headers | **PASS** |
| Primary keys documented | **PASS** |
| Order grain = line item | **PASS** |
| Defect strategy documented | **PASS** |
| External DB deployment | **Not executed / not claimed** |
| Databricks pipeline validation | **26/26 PASS** (2026-09-10) |
