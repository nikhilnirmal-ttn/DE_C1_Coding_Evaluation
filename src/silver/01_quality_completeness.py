"""Silver data quality — completeness checks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_COMPLETENESS,
    ENTITY_CONFIG,
    SilverConfig,
    build_failures_from_rules,
    col_is_blank,
    notebook_spark_if_defined,
    prepare_entity_dataframe,
    read_bronze_table,
    require_pyspark,
    resolve_spark,
)


def check_completeness(df, entity_key: str, config: SilverConfig, spark):
    """Check required fields for NULL/blank values. Returns (input_df, failures_df)."""
    entity = ENTITY_CONFIG[entity_key]
    rules = [
        (
            col_is_blank(column),
            f"Required field '{column}' is NULL or blank",
            column,
        )
        for column in entity["required_fields"]
        if column in df.columns
    ]
    failures = build_failures_from_rules(
        df,
        entity_key,
        config,
        CHECK_COMPLETENESS,
        rules,
        spark=spark,
    )
    return df, failures


def run_completeness_for_entity(
    spark, entity_key: str, config: SilverConfig | None = None
):
    config = config or SilverConfig()
    bronze_df = read_bronze_table(spark, config, entity_key)
    prepared = prepare_entity_dataframe(bronze_df, entity_key)
    return check_completeness(prepared, entity_key, config, spark)


def run_completeness_all(spark, config: SilverConfig | None = None) -> dict:
    config = config or SilverConfig()
    results = {}
    for entity_key in ("customers", "products", "orders"):
        prepared, failures = run_completeness_for_entity(spark, entity_key, config)
        results[entity_key] = {"prepared_df": prepared, "failures_df": failures}
    return results


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — Completeness checks")
    for entity_key in ("customers", "products", "orders"):
        _, failures = run_completeness_for_entity(spark, entity_key, config)
        print(f"[completeness] {entity_key}: {failures.count()} failure record(s)")


if __name__ == "__main__":
    main()
