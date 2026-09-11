# Bronze Layer Notes

**Candidate:** Nikhil Kr. Nirmal  
**Phase:** 3 — Bronze ingestion only  
**Catalog:** `de_c1_coding_evaluation`  
**Schema:** `bronze`

## Purpose

Land raw CSV data from `data/` into Delta Bronze tables with **no data quality checks**. All business values remain STRING so intentional defects from Phase 2 are preserved for Silver DQ.

## Tables

| Source CSV | Bronze table | Expected rows |
|------------|--------------|---------------|
| `customers.csv` | `de_c1_coding_evaluation.bronze.bronze_customers` | 1006 |
| `products.csv` | `de_c1_coding_evaluation.bronze.bronze_products` | 206 |
| `orders.csv` | `de_c1_coding_evaluation.bronze.bronze_orders` | 5163 |

## Schema rules

- All source columns are stored as **STRING**
- Two metadata columns are appended on ingest:
  - `_ingestion_timestamp` — set at write time
  - `_source_file` — source CSV filename (for example `customers.csv`)
- Write mode: **Delta overwrite** (full reload)
- No trimming, casting, deduplication, or quarantine in Bronze

## Scripts

| Script | Entity |
|--------|--------|
| `bronze_common.py` | Shared config, validation, Spark ingest helpers |
| `01_ingest_customers.py` | Customers only |
| `02_ingest_orders.py` | Orders only |
| `03_ingest_products.py` | Products only |
| `ingest_all.py` | Runs all three in order |

## Local validation (dry run)

Run from project root:

```text
python src/bronze/ingest_all.py --dry-run
```

Dry run checks:

- CSV files exist under `data/`
- Headers match `data-model.md`
- Row counts match `DATA_GENERATION_NOTES.md`
- Reports target Unity Catalog table names and Bronze column list

Dry run does **not** require PySpark.

## Databricks execution

1. Run `databricks/notebooks/00_setup_catalog` to create catalog and schemas
2. Upload project to workspace (see `databricks/DATABRICKS_SETUP.md`)
3. Run `databricks/notebooks/01_run_bronze`

The notebook imports `BronzeConfig` and `run_ingestion` from `src/bronze/` and writes Delta tables with overwrite mode.

## Out of scope (later phases)

- Silver typing, cleansing, and 5 DQ categories
- Gold aggregates and dashboard SQL
- Validation report (`26/26` checks)
