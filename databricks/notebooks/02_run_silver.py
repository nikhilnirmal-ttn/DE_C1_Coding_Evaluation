# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Silver Pipeline

# COMMAND ----------

import sys
from pathlib import Path

REPO = Path("/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evaluation")

sys.path.insert(0, str(REPO / "src/silver"))

from create_silver_tables import run_silver_pipeline
from silver_common import SilverConfig

config = SilverConfig(catalog_name="de_c1_coding_evaluation")
result = run_silver_pipeline(spark, config)

for entity_key in ("customers", "products", "orders"):
    count = result["curated"][entity_key].count()
    print(f"[silver_{entity_key}] {count} row(s) -> {result['curated_tables'][entity_key]}")

print("Silver pipeline complete.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'silver_customers' AS table_name, COUNT(*) AS row_count
# MAGIC FROM de_c1_coding_evaluation.silver.silver_customers
# MAGIC UNION ALL
# MAGIC SELECT 'silver_products', COUNT(*) FROM de_c1_coding_evaluation.silver.silver_products
# MAGIC UNION ALL
# MAGIC SELECT 'silver_orders', COUNT(*) FROM de_c1_coding_evaluation.silver.silver_orders;
