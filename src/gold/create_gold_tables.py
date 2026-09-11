"""Gold layer orchestration — Silver curated tables → analytical Gold tables."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

DEFAULT_CATALOG = "de_c1_coding_evaluation"
DEFAULT_SILVER_SCHEMA = "silver"
DEFAULT_GOLD_SCHEMA = "gold"

GOLD_SQL_FILES: tuple[tuple[str, str], ...] = (
    ("01_sales_by_product.sql", "gold_sales_by_product"),
    ("02_revenue_by_customer.sql", "gold_revenue_by_customer"),
    ("03_daily_weekly_trends.sql", "gold_daily_weekly_trends"),
    ("04_customer_segmentation.sql", "gold_customer_segmentation"),
)


@dataclass
class GoldConfig:
    """Runtime configuration for Gold processing."""

    catalog_name: str = DEFAULT_CATALOG
    silver_schema: str = DEFAULT_SILVER_SCHEMA
    gold_schema: str = DEFAULT_GOLD_SCHEMA
    run_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def qualified_schema(config: GoldConfig, schema: str) -> str:
    return f"{config.catalog_name}.{schema}"


def gold_table_name(config: GoldConfig, table: str) -> str:
    return f"{qualified_schema(config, config.gold_schema)}.{table}"


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


def require_pyspark() -> None:
    try:
        import pyspark  # noqa: F401
    except ImportError as exc:
        print("PySpark is not installed.", file=sys.stderr)
        raise SystemExit(1) from exc


def ensure_gold_schema_exists(spark: SparkSession, config: GoldConfig) -> str:
    schema = qualified_schema(config, config.gold_schema)
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    return schema


def _strip_sql_comments(sql_text: str) -> str:
    lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def load_sql_statement(sql_path: Path) -> str:
    if not sql_path.is_file():
        raise FileNotFoundError(f"Gold SQL file not found: {sql_path}")
    return _strip_sql_comments(sql_path.read_text(encoding="utf-8"))


def execute_gold_sql(spark: SparkSession, sql_text: str) -> None:
    statement = sql_text.strip().rstrip(";")
    if not statement:
        raise ValueError("Gold SQL file is empty after comment stripping.")
    spark.sql(statement)


def run_gold_pipeline(
    spark: SparkSession | None = None,
    sql_dir: Path | str | None = None,
    config: GoldConfig | None = None,
) -> dict:
    """
    Execute Gold SQL scripts in order.

    Reads only from ``de_c1_coding_evaluation.silver.*`` (defined in SQL files).
    Writes Delta tables to ``de_c1_coding_evaluation.gold.*``.
    """
    config = config or GoldConfig()
    spark = resolve_spark(spark)
    base_dir = Path(sql_dir) if sql_dir is not None else Path(__file__).resolve().parent

    schema = ensure_gold_schema_exists(spark, config)

    tables: dict[str, str] = {}
    row_counts: dict[str, int] = {}

    for filename, table_name in GOLD_SQL_FILES:
        sql_path = base_dir / filename
        sql_text = load_sql_statement(sql_path)
        execute_gold_sql(spark, sql_text)

        target = gold_table_name(config, table_name)
        tables[table_name] = target
        row_counts[table_name] = spark.table(target).count()

    return {
        "config": config,
        "schema": schema,
        "sql_dir": str(base_dir),
        "tables": tables,
        "row_counts": row_counts,
    }


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = GoldConfig()

    print("Gold — Full pipeline")
    result = run_gold_pipeline(spark, config=config)

    for table_name, target in result["tables"].items():
        count = result["row_counts"][table_name]
        print(f"[{table_name}] wrote {count} row(s) to {target}")


if __name__ == "__main__":
    main()
