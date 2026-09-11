"""Shared configuration and utilities for the Silver layer."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession

DEFAULT_CATALOG = "de_c1_coding_evaluation"
DEFAULT_BRONZE_SCHEMA = "bronze"
DEFAULT_SILVER_SCHEMA = "silver"

BRONZE_METADATA_COLUMNS = ("_ingestion_timestamp", "_source_file")

CUSTOMER_STRING_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "country",
    "signup_date",
    "customer_segment",
    "lifetime_value",
]

PRODUCT_STRING_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "unit_price",
]

ORDER_STRING_COLUMNS = [
    "order_line_id",
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
]

ENTITY_CONFIG: dict[str, dict[str, Any]] = {
    "customers": {
        "bronze_table": "bronze_customers",
        "business_key": "customer_id",
        "string_columns": CUSTOMER_STRING_COLUMNS,
        "required_fields": CUSTOMER_STRING_COLUMNS,
        "date_columns": ["signup_date"],
        "decimal_columns": [("lifetime_value", 12, 2)],
        "int_columns": [],
        "email_columns": ["email"],
    },
    "products": {
        "bronze_table": "bronze_products",
        "business_key": "product_id",
        "string_columns": PRODUCT_STRING_COLUMNS,
        "required_fields": PRODUCT_STRING_COLUMNS,
        "date_columns": [],
        "decimal_columns": [("unit_price", 10, 2)],
        "int_columns": [],
        "email_columns": [],
    },
    "orders": {
        "bronze_table": "bronze_orders",
        "business_key": "order_line_id",
        "string_columns": ORDER_STRING_COLUMNS,
        "required_fields": ORDER_STRING_COLUMNS,
        "date_columns": ["order_date"],
        "decimal_columns": [("unit_price", 10, 2)],
        "int_columns": ["quantity"],
        "email_columns": [],
    },
}

CHECK_COMPLETENESS = "completeness"
CHECK_UNIQUENESS = "uniqueness"
CHECK_TYPE_VALIDATION = "type_validation"
CHECK_REFERENTIAL_INTEGRITY = "referential_integrity"
CHECK_BUSINESS_LOGIC = "business_logic"

VALID_CUSTOMER_SEGMENTS = ("Premium", "Standard", "Basic")

QUARANTINE_COLUMNS = [
    "entity",
    "record_key",
    "check_category",
    "check_name",
    "failure_reason",
    "raw_values",
    "run_timestamp",
]

QUARANTINE_TABLE_NAME = "silver_quarantine_records"
DQ_SUMMARY_TABLE_NAME = "silver_dq_summary"

SILVER_CUSTOMERS_TABLE_NAME = "silver_customers"
SILVER_PRODUCTS_TABLE_NAME = "silver_products"
SILVER_ORDERS_TABLE_NAME = "silver_orders"

DQ_SUMMARY_COLUMNS = [
    "entity",
    "check_category",
    "total_records",
    "failed_records",
    "pass_pct",
    "run_timestamp",
]

ENTITY_KEYS = ("customers", "products", "orders")


def entity_dq_categories(entity_key: str) -> tuple[str, ...]:
    """DQ categories applied to an entity for curated-table eligibility."""
    categories = (
        CHECK_COMPLETENESS,
        CHECK_UNIQUENESS,
        CHECK_TYPE_VALIDATION,
        CHECK_BUSINESS_LOGIC,
    )
    if entity_key == "orders":
        return categories[:3] + (CHECK_REFERENTIAL_INTEGRITY,) + categories[3:]
    return categories


@dataclass
class SilverConfig:
    """Runtime configuration for Silver processing."""

    catalog_name: str = DEFAULT_CATALOG
    bronze_schema: str = DEFAULT_BRONZE_SCHEMA
    silver_schema: str = DEFAULT_SILVER_SCHEMA
    run_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def qualified_table(config: SilverConfig, schema: str, table: str) -> str:
    return f"{config.catalog_name}.{schema}.{table}"


def bronze_table_name(config: SilverConfig, entity_key: str) -> str:
    table = ENTITY_CONFIG[entity_key]["bronze_table"]
    return qualified_table(config, config.bronze_schema, table)


def resolve_spark(explicit: SparkSession | None = None) -> SparkSession:
    if explicit is not None:
        return explicit

    from pyspark.sql import SparkSession

    active = SparkSession.getActiveSession()
    if active is not None:
        return active

    import __main__ as main_module

    notebook_spark = getattr(main_module, "spark", None)
    if notebook_spark is not None and hasattr(notebook_spark, "read"):
        return notebook_spark

    import os

    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):
        raise RuntimeError(
            "No active Spark session on Databricks. Pass spark=spark from the notebook."
        )

    return SparkSession.builder.getOrCreate()


def notebook_spark_if_defined() -> SparkSession | None:
    try:
        candidate = spark  # type: ignore[name-defined]  # noqa: F821
    except NameError:
        return None
    if candidate is not None and hasattr(candidate, "read"):
        return candidate
    return None


def read_bronze_table(spark: SparkSession, config: SilverConfig, entity_key: str) -> DataFrame:
    table = bronze_table_name(config, entity_key)
    return spark.table(table)


def require_pyspark() -> None:
    try:
        import pyspark  # noqa: F401
    except ImportError as exc:
        print("PySpark is not installed.", file=sys.stderr)
        raise SystemExit(1) from exc


# ---------------------------------------------------------------------------
# Pure-Python validation helpers (testable without Spark)
# ---------------------------------------------------------------------------

_NUMERIC_ID_PATTERN = re.compile(r"^-?\d+$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_blank(value: str | None) -> bool:
    return value is None or str(value).strip() == ""


def is_numeric_identifier(value: str | None) -> bool:
    if is_blank(value):
        return False
    return _NUMERIC_ID_PATTERN.match(str(value).strip()) is not None


def is_valid_email_format(value: str | None) -> bool:
    if is_blank(value):
        return False
    return _EMAIL_PATTERN.match(str(value).strip()) is not None


def is_valid_iso_date_string(value: str | None) -> bool:
    if is_blank(value):
        return False
    text = str(value).strip()
    if not _ISO_DATE_PATTERN.match(text):
        return False
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def parse_decimal_string(value: str | None) -> float | None:
    if is_blank(value):
        return None
    text = str(value).strip()
    if text.upper() == "INVALID":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int_string(value: str | None) -> int | None:
    if is_blank(value):
        return None
    text = str(value).strip()
    try:
        return int(text)
    except ValueError:
        return None


def is_valid_customer_segment(value: str | None) -> bool:
    return not is_blank(value) and str(value).strip() in VALID_CUSTOMER_SEGMENTS


def col_is_valid_customer_segment(column_name: str) -> Column:
    from pyspark.sql import functions as F

    trimmed = F.trim(F.col(column_name))
    return trimmed.isin(list(VALID_CUSTOMER_SEGMENTS))


def trim_string_columns(df: DataFrame, columns: Sequence[str]) -> DataFrame:
    from pyspark.sql import functions as F

    result = df
    for column in columns:
        if column in result.columns:
            result = result.withColumn(column, F.trim(F.col(column)))
    return result


def col_is_blank(column_name: str) -> Column:
    from pyspark.sql import functions as F

    return F.col(column_name).isNull() | (F.trim(F.col(column_name)) == F.lit(""))


def col_is_valid_email(column_name: str) -> Column:
    from pyspark.sql import functions as F

    trimmed = F.trim(F.col(column_name))
    return trimmed.rlike(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _safe_try_to_date(column_name: str) -> Column:
    from pyspark.sql import functions as F

    return F.expr(f"try_to_date(trim(`{column_name}`), 'yyyy-MM-dd')")


def col_is_valid_iso_date(column_name: str) -> Column:
    from pyspark.sql import functions as F

    trimmed = F.trim(F.col(column_name))
    parsed = _safe_try_to_date(column_name)
    return parsed.isNotNull() & trimmed.rlike(r"^\d{4}-\d{2}-\d{2}$")


def add_typed_columns(df: DataFrame, entity_key: str) -> DataFrame:
    """Trim strings and add safely parsed typed companion columns."""
    from pyspark.sql import functions as F

    config = ENTITY_CONFIG[entity_key]
    result = trim_string_columns(df, config["string_columns"])

    for column in config["date_columns"]:
        result = result.withColumn(f"{column}_typed", _safe_try_to_date(column))

    for column in config["int_columns"]:
        trimmed = F.trim(F.col(column))
        result = result.withColumn(
            f"{column}_typed",
            F.when(trimmed.rlike(r"^-?\d+$"), trimmed.cast("int")).otherwise(F.lit(None)),
        )

    for column, precision, scale in config["decimal_columns"]:
        trimmed = F.trim(F.col(column))
        result = result.withColumn(
            f"{column}_typed",
            F.when(
                trimmed.rlike(r"^-?\d+(\.\d+)?$"),
                trimmed.cast(f"decimal({precision},{scale})"),
            ).otherwise(F.lit(None)),
        )

    return result


def business_columns(entity_key: str) -> list[str]:
    return list(ENTITY_CONFIG[entity_key]["string_columns"])


def run_timestamp_col(config: SilverConfig) -> Column:
    from pyspark.sql import functions as F

    return F.to_timestamp(F.lit(config.run_timestamp.strftime("%Y-%m-%d %H:%M:%S")))


def bronze_source_json_expr(entity_key: str) -> Column:
    from pyspark.sql import functions as F

    fields = business_columns(entity_key)
    return F.to_json(F.struct(*[F.col(name).alias(name) for name in fields]))


def empty_failures_df(spark: SparkSession):
    return spark.sql(
        """
        SELECT
            CAST(NULL AS STRING) AS entity,
            CAST(NULL AS STRING) AS record_key,
            CAST(NULL AS STRING) AS check_category,
            CAST(NULL AS STRING) AS check_name,
            CAST(NULL AS STRING) AS failure_reason,
            CAST(NULL AS STRING) AS raw_values,
            CAST(NULL AS TIMESTAMP) AS run_timestamp
        WHERE 1 = 0
        """
    )


def build_failure_df(
    source_df: DataFrame,
    entity_key: str,
    config: SilverConfig,
    check_category: str,
    condition: Column,
    failure_reason: str,
    check_name: str,
) -> DataFrame:
    from pyspark.sql import functions as F

    entity = ENTITY_CONFIG[entity_key]
    business_key = entity["business_key"]

    return source_df.filter(condition).select(
        F.lit(entity_key).alias("entity"),
        F.col(business_key).alias("record_key"),
        F.lit(check_category).alias("check_category"),
        F.lit(check_name).alias("check_name"),
        F.lit(failure_reason).alias("failure_reason"),
        bronze_source_json_expr(entity_key).alias("raw_values"),
        run_timestamp_col(config).alias("run_timestamp"),
    )


def build_failures_from_rules(
    source_df: DataFrame,
    entity_key: str,
    config: SilverConfig,
    check_category: str,
    rules: Sequence[tuple[Any, str, str]],
    spark: SparkSession | None = None,
) -> DataFrame:
    if not rules:
        if spark is None:
            raise ValueError("spark is required when no failure rules are provided")
        return empty_failures_df(spark)

    if spark is None:
        raise ValueError("spark is required when failure rules are provided")

    frames = [
        build_failure_df(source_df, entity_key, config, check_category, condition, reason, check_name)
        for condition, reason, check_name in rules
    ]
    return union_failures(spark, *frames)


def union_failures(spark: SparkSession, *frames: DataFrame) -> DataFrame:
    result: DataFrame | None = None
    for frame in frames:
        if frame is None:
            continue
        result = frame if result is None else result.unionByName(frame)
    return result if result is not None else empty_failures_df(spark)


def deterministic_tiebreaker_columns(df: DataFrame, entity_key: str, business_key: str) -> list[str]:
    excluded = {business_key, "_dup_rank"}
    excluded.update(BRONZE_METADATA_COLUMNS)
    return sorted(c for c in df.columns if c not in excluded)


def deterministic_rank_order_columns(df: DataFrame, entity_key: str, business_key: str) -> list:
    from pyspark.sql import functions as F

    order_cols = [
        F.col(c).asc_nulls_last()
        for c in deterministic_tiebreaker_columns(df, entity_key, business_key)
    ]
    hash_cols = sorted(c for c in df.columns if c not in {business_key, "_dup_rank"})
    if hash_cols:
        order_cols.append(F.hash(*[F.col(c) for c in hash_cols]).asc())
    return order_cols


def add_duplicate_rank(df: DataFrame, entity_key: str) -> DataFrame:
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    business_key = ENTITY_CONFIG[entity_key]["business_key"]
    order_cols = deterministic_rank_order_columns(df, entity_key, business_key)
    window = Window.partitionBy(F.col(business_key)).orderBy(*order_cols)
    return df.withColumn("_dup_rank", F.row_number().over(window))


def row_fails_completeness(entity_key: str) -> Column:
    from functools import reduce
    from operator import or_

    from pyspark.sql import functions as F

    entity = ENTITY_CONFIG[entity_key]
    conditions = [col_is_blank(column) for column in entity["required_fields"]]
    if not conditions:
        return F.lit(False)
    return reduce(or_, conditions)


def row_fails_type_validation(entity_key: str) -> Column:
    from functools import reduce
    from operator import or_

    from pyspark.sql import functions as F

    entity = ENTITY_CONFIG[entity_key]
    conditions: list[Column] = []

    for column in entity["email_columns"]:
        conditions.append(~col_is_blank(column) & ~col_is_valid_email(column))
    for column in entity["date_columns"]:
        typed_col = f"{column}_typed"
        conditions.append(
            ~col_is_blank(column)
            & (~col_is_valid_iso_date(column) | F.col(typed_col).isNull())
        )
    for column in entity["int_columns"]:
        typed_col = f"{column}_typed"
        conditions.append(~col_is_blank(column) & F.col(typed_col).isNull())
    for column, _precision, _scale in entity["decimal_columns"]:
        typed_col = f"{column}_typed"
        conditions.append(~col_is_blank(column) & F.col(typed_col).isNull())

    if not conditions:
        return F.lit(False)
    return reduce(or_, conditions)


def canonical_valid_filter(entity_key: str) -> Column:
    from pyspark.sql import functions as F

    return (
        (F.col("_dup_rank") == F.lit(1))
        & ~row_fails_completeness(entity_key)
        & ~row_fails_type_validation(entity_key)
    )


def prepare_canonical_entity_df(
    spark: SparkSession, config: SilverConfig, entity_key: str
) -> tuple[DataFrame, DataFrame]:
    bronze_df = read_bronze_table(spark, config, entity_key)
    prepared = prepare_entity_dataframe(bronze_df, entity_key)
    ranked = add_duplicate_rank(prepared, entity_key)
    canonical = ranked.filter(canonical_valid_filter(entity_key))
    return ranked, canonical


def canonical_parent_keys_df(canonical_df: DataFrame, entity_key: str) -> DataFrame:
    from pyspark.sql import functions as F

    business_key = ENTITY_CONFIG[entity_key]["business_key"]
    return canonical_df.select(F.col(business_key)).distinct()


def prepare_entity_dataframe(df: DataFrame, entity_key: str) -> DataFrame:
    return add_typed_columns(df, entity_key)


def failures_for_category(dq_results: dict, category: str, entity_key: str) -> DataFrame:
    if category == CHECK_REFERENTIAL_INTEGRITY:
        return dq_results["referential_integrity"]["orders"]["failures_df"]
    return dq_results[category][entity_key]["failures_df"]


def filter_valid_rows(df: DataFrame, entity_key: str, dq_results: dict) -> DataFrame:
    from pyspark.sql import functions as F

    business_key = ENTITY_CONFIG[entity_key]["business_key"]
    valid_df = df

    for category in entity_dq_categories(entity_key):
        failures_df = failures_for_category(dq_results, category, entity_key)
        failed_keys = failures_df.select(F.col("record_key").alias(business_key)).distinct()
        valid_df = valid_df.join(failed_keys, on=business_key, how="left_anti")

    return valid_df


def curated_eligible_parent_keys_df(
    prepared_df: DataFrame,
    entity_key: str,
    dq_results: dict,
) -> DataFrame:
    valid_df = filter_valid_rows(prepared_df, entity_key, dq_results)
    return canonical_parent_keys_df(valid_df, entity_key)


def silver_table_name(config: SilverConfig, table: str) -> str:
    return qualified_table(config, config.silver_schema, table)


def ensure_silver_schema_exists(spark: SparkSession, config: SilverConfig) -> None:
    qualified = f"{config.catalog_name}.{config.silver_schema}"
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {qualified}")


def calculate_pass_percentage(rows_tested: int, rows_passed: int) -> float | None:
    if rows_tested <= 0:
        return None
    return rows_passed / rows_tested * 100.0


def calculate_summary_metrics(rows_tested: int, rows_failed: int) -> dict[str, int | float | None]:
    failed = max(0, min(rows_failed, rows_tested))
    passed = max(0, rows_tested - failed)
    return {
        "rows_tested": rows_tested,
        "rows_passed": passed,
        "rows_failed": failed,
        "pass_percentage": calculate_pass_percentage(rows_tested, passed),
    }


def write_delta_table(
    df: DataFrame,
    qualified_table_name: str,
    columns: Sequence[str] | None = None,
) -> None:
    output = df.select(*columns) if columns is not None else df
    (
        output.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(qualified_table_name)
    )
