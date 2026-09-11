# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Setup Unity Catalog
# MAGIC Candidate: Nikhil Kr. Nirmal

# COMMAND ----------

spark.sql("CREATE CATALOG IF NOT EXISTS de_c1_coding_evaluation")
spark.sql("CREATE SCHEMA IF NOT EXISTS de_c1_coding_evaluation.bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS de_c1_coding_evaluation.silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS de_c1_coding_evaluation.gold")

print("Catalog and schemas ready.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN de_c1_coding_evaluation;
