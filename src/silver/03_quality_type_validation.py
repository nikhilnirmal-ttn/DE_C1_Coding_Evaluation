"""Silver data quality — type validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_TYPE_VALIDATION,
    ENTITY_CONFIG,
    SilverConfig,
    build_failures_from_rules,
    col_is_blank,
    col_is_valid_email,
    col_is_valid_iso_date,
    notebook_spark_if_defined,
    prepare_entity_dataframe,
    read_bronze_table,
    require_pyspark,
    resolve_spark,
)


def _non_empty_source(column_name: str):
    return ~col_is_blank(column_name)


def check_type_validation(df, entity_key: str, config: SilverConfig, spark):
    """Validate dates, numerics, and email format. Returns (input_df, failures_df)."""
    from pyspark.sql import functions as F

    entity = ENTITY_CONFIG[entity_key]
    rules: list[tuple] = []

    for column in entity["email_columns"]:
        rules.append(
            (
                _non_empty_source(column) & ~col_is_valid_email(column),
                f"Email '{column}' has invalid format",
                column,
            )
        )

    for column in entity["date_columns"]:
        typed_col = f"{column}_typed"
        rules.append(
            (
                _non_empty_source(column)
                & (~col_is_valid_iso_date(column) | F.col(typed_col).isNull()),
                f"Date '{column}' is not a valid ISO date (YYYY-MM-DD)",
                column,
            )
        )

    for column in entity["int_columns"]:
        typed_col = f"{column}_typed"
        rules.append(
            (
                _non_empty_source(column) & F.col(typed_col).isNull(),
                f"Integer '{column}' is not parseable",
                column,
            )
        )

    for column, _precision, _scale in entity["decimal_columns"]:
        typed_col = f"{column}_typed"
        rules.append(
            (
                _non_empty_source(column) & F.col(typed_col).isNull(),
                f"Decimal '{column}' is not parseable",
                column,
            )
        )

    failures = build_failures_from_rules(
        df,
        entity_key,
        config,
        CHECK_TYPE_VALIDATION,
        rules,
        spark=spark,
    )
    return df, failures


def run_type_validation_for_entity(
    spark, entity_key: str, config: SilverConfig | None = None
):
    config = config or SilverConfig()
    bronze_df = read_bronze_table(spark, config, entity_key)
    prepared = prepare_entity_dataframe(bronze_df, entity_key)
    return check_type_validation(prepared, entity_key, config, spark)


def run_type_validation_all(spark, config: SilverConfig | None = None) -> dict:
    config = config or SilverConfig()
    results = {}
    for entity_key in ("customers", "products", "orders"):
        prepared, failures = run_type_validation_for_entity(spark, entity_key, config)
        results[entity_key] = {"prepared_df": prepared, "failures_df": failures}
    return results


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — Type validation checks")
    for entity_key in ("customers", "products", "orders"):
        _, failures = run_type_validation_for_entity(spark, entity_key, config)
        print(f"[type_validation] {entity_key}: {failures.count()} failure record(s)")


if __name__ == "__main__":
    main()
