# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Pipeline Validation (target 26/26 PASS)

# COMMAND ----------

import re
from pathlib import Path

REPO = Path("/Workspace/Users/nikhil.nirmal@tothenew.com/DE_C1_Coding_Evaluation")
sql_text = (REPO / "src/validation/pipeline_validation.sql").read_text(encoding="utf-8")

# One block per check comment: -- A1., -- B2., -- E1., etc.
markers = list(re.finditer(r"^-- ([A-E]\d+\..*)$", sql_text, re.MULTILINE))

rows = []
for i, marker in enumerate(markers):
    end = markers[i + 1].start() if i + 1 < len(markers) else len(sql_text)
    block = sql_text[marker.start() : end]
    upper = block.upper()
    with_idx = upper.find("WITH")
    select_idx = upper.find("SELECT")

    if with_idx >= 0 and (select_idx < 0 or with_idx < select_idx):
        stmt = block[with_idx:].strip()
    elif select_idx >= 0:
        stmt = block[select_idx:].strip()
    else:
        continue

    stmt = stmt.rstrip(";").strip()
    row = spark.sql(stmt).collect()[0]
    rows.append((row["check_name"], row["status"]))

summary = spark.createDataFrame(rows, ["check_name", "status"])
pass_count = summary.filter("status = 'PASS'").count()
total = summary.count()

print("=" * 50)
print(f"VALIDATION SUMMARY: {pass_count}/{total} PASS")
print("=" * 50)
display(summary.orderBy("check_name"))
