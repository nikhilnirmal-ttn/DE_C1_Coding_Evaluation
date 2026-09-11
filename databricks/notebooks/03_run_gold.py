# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Gold Pipeline

# COMMAND ----------

import importlib.util
import sys
from pathlib import Path

REPO = Path("/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evaluation")
gold_dir = REPO / "src/gold"

spec = importlib.util.spec_from_file_location(
    "create_gold_tables", gold_dir / "create_gold_tables.py"
)
create_gold_tables = importlib.util.module_from_spec(spec)
sys.modules["create_gold_tables"] = create_gold_tables
spec.loader.exec_module(create_gold_tables)

result = create_gold_tables.run_gold_pipeline(spark=spark, sql_dir=gold_dir)
print("Gold pipeline complete.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'gold_sales_by_product' AS table_name, COUNT(*) AS row_count
# MAGIC FROM de_c1_coding_evaluation.gold.gold_sales_by_product
# MAGIC UNION ALL
# MAGIC SELECT 'gold_revenue_by_customer', COUNT(*) FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer
# MAGIC UNION ALL
# MAGIC SELECT 'gold_daily_weekly_trends', COUNT(*) FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
# MAGIC UNION ALL
# MAGIC SELECT 'gold_customer_segmentation', COUNT(*) FROM de_c1_coding_evaluation.gold.gold_customer_segmentation;
