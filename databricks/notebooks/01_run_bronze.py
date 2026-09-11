# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Bronze Ingestion
# MAGIC Expected: customers=1006, products=206, orders=5163

# COMMAND ----------

import sys
from pathlib import Path

REPO = Path("/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evaluation")

sys.path.insert(0, str(REPO / "src/bronze"))

from bronze_common import BronzeConfig
from ingest_all import run_ingestion

config = BronzeConfig(
    data_dir=REPO / "data",
    catalog_name="de_c1_coding_evaluation",
    schema_name="bronze",
    write_mode="overwrite",
)

run_ingestion(config, spark=spark)
print("Bronze ingestion complete.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'bronze_customers' AS table_name, COUNT(*) AS row_count
# MAGIC FROM de_c1_coding_evaluation.bronze.bronze_customers
# MAGIC UNION ALL
# MAGIC SELECT 'bronze_products', COUNT(*) FROM de_c1_coding_evaluation.bronze.bronze_products
# MAGIC UNION ALL
# MAGIC SELECT 'bronze_orders', COUNT(*) FROM de_c1_coding_evaluation.bronze.bronze_orders;
