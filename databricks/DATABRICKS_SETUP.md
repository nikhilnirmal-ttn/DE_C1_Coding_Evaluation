# Databricks Setup — Nikhil Kr. Nirmal

Workspace folder:

```text
/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evalution
```

## Before Databricks

1. Open `DE_C1_Coding_Evaluation-Nikhil` in Cursor
2. Run `CURSOR_START_PROMPT.md` in a new chat until `src/` and `data/` exist
3. Then upload to Databricks

## Upload

1. Databricks → Workspace → Users → nikhil.nirmal@tothenew.com → DE_C1_Coding_Evalution
2. **Create → Import** → upload entire `DE_C1_Coding_Evaluation-Nikhil` folder

Must include after build:

- `data/customers.csv`, `data/products.csv`, `data/orders.csv`
- `src/bronze/`, `src/silver/`, `src/gold/`, `src/validation/`
- `databricks/notebooks/`

## Run order

| Step | Notebook |
|------|----------|
| 1 | `00_setup_catalog` |
| 2 | `01_run_bronze` |
| 3 | `02_run_silver` |
| 4 | `03_run_gold` |
| 5 | `04_run_validation` |

Use **Serverless** compute.

## Expected Bronze counts

| Table | Rows |
|-------|------|
| bronze_customers | 1006 |
| bronze_products | 206 |
| bronze_orders | 5163 |

Target validation: **26/26 PASS**
