"""Silver data quality — uniqueness checks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_UNIQUENESS,
    ENTITY_CONFIG,
    SilverConfig,
    build_failures_from_rules,
    deterministic_rank_order_columns,
    notebook_spark_if_defined,
    prepare_entity_dataframe,
    read_bronze_table,
    require_pyspark,
    resolve_spark,
)


def check_uniqueness(df, entity_key: str, config: SilverConfig, spark):
    """Flag duplicate business keys; keep first canonical row deterministically."""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    entity = ENTITY_CONFIG[entity_key]
    business_key = entity["business_key"]

    order_cols = deterministic_rank_order_columns(df, entity_key, business_key)
    window = Window.partitionBy(F.col(business_key)).orderBy(*order_cols)
    ranked = df.withColumn("_dup_rank", F.row_number().over(window))

    duplicate_condition = F.col("_dup_rank") > F.lit(1)
    failures = build_failures_from_rules(
        ranked,
        entity_key,
        config,
        CHECK_UNIQUENESS,
        [
            (
                duplicate_condition,
                f"Duplicate business key '{business_key}' (non-canonical occurrence)",
                business_key,
            )
        ],
        spark=spark,
    )
    return ranked, failures


def run_uniqueness_for_entity(spark, entity_key: str, config: SilverConfig | None = None):
    config = config or SilverConfig()
    bronze_df = read_bronze_table(spark, config, entity_key)
    prepared = prepare_entity_dataframe(bronze_df, entity_key)
    return check_uniqueness(prepared, entity_key, config, spark)


def run_uniqueness_all(spark, config: SilverConfig | None = None) -> dict:
    config = config or SilverConfig()
    results = {}
    for entity_key in ("customers", "products", "orders"):
        ranked, failures = run_uniqueness_for_entity(spark, entity_key, config)
        results[entity_key] = {"ranked_df": ranked, "failures_df": failures}
    return results


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — Uniqueness checks")
    for entity_key in ("customers", "products", "orders"):
        _, failures = run_uniqueness_for_entity(spark, entity_key, config)
        print(f"[uniqueness] {entity_key}: {failures.count()} failure record(s)")


if __name__ == "__main__":
    main()
