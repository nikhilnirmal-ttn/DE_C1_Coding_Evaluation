"""Shared utilities for Bronze layer CSV ingestion."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CATALOG_NAME = "de_c1_coding_evaluation"
SCHEMA_NAME = "bronze"
METADATA_COLUMNS = ("_ingestion_timestamp", "_source_file")

ENTITY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "customers": {
        "source_file": "customers.csv",
        "table_name": "bronze_customers",
        "columns": [
            "customer_id",
            "customer_name",
            "email",
            "country",
            "signup_date",
            "customer_segment",
            "lifetime_value",
        ],
        "expected_row_count": 1006,
    },
    "products": {
        "source_file": "products.csv",
        "table_name": "bronze_products",
        "columns": ["product_id", "product_name", "category", "unit_price"],
        "expected_row_count": 206,
    },
    "orders": {
        "source_file": "orders.csv",
        "table_name": "bronze_orders",
        "columns": [
            "order_line_id",
            "order_id",
            "customer_id",
            "product_id",
            "order_date",
            "quantity",
            "unit_price",
        ],
        "expected_row_count": 5163,
    },
}

INGESTION_ORDER = ("customers", "products", "orders")


@dataclass
class BronzeConfig:
    data_dir: Path
    catalog_name: str = CATALOG_NAME
    schema_name: str = SCHEMA_NAME
    write_mode: str = "overwrite"

    def source_path(self, entity: str) -> Path:
        return self.data_dir / ENTITY_DEFINITIONS[entity]["source_file"]

    def table_fqn(self, entity: str) -> str:
        table_name = ENTITY_DEFINITIONS[entity]["table_name"]
        return f"{self.catalog_name}.{self.schema_name}.{table_name}"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config() -> BronzeConfig:
    return BronzeConfig(data_dir=project_root() / "data")


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {csv_path}")
        headers = list(reader.fieldnames)
        rows = [
            {column: "" if value is None else str(value) for column, value in row.items()}
            for row in reader
        ]
    return headers, rows


def validate_source_csv(entity: str, config: BronzeConfig) -> dict[str, Any]:
    """Validate a source CSV for Bronze ingestion without writing to Delta."""
    definition = ENTITY_DEFINITIONS[entity]
    csv_path = config.source_path(entity)

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing source file: {csv_path}")

    headers, rows = read_csv_rows(csv_path)
    expected_columns = definition["columns"]

    if headers != expected_columns:
        raise ValueError(
            f"{entity}: column mismatch.\n"
            f"  Expected: {expected_columns}\n"
            f"  Found:    {headers}"
        )

    row_count = len(rows)
    expected_row_count = definition["expected_row_count"]
    if row_count != expected_row_count:
        raise ValueError(
            f"{entity}: expected {expected_row_count} rows, found {row_count}"
        )

    return {
        "entity": entity,
        "source_file": str(csv_path),
        "row_count": row_count,
        "bronze_columns": list(expected_columns) + list(METADATA_COLUMNS),
        "target_table": config.table_fqn(entity),
        "write_mode": config.write_mode,
        "dry_run": True,
    }


def ingest_entity_to_bronze(
    entity: str,
    config: BronzeConfig,
    *,
    spark=None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Ingest one entity into Bronze, or validate locally when dry_run=True."""
    if dry_run:
        return validate_source_csv(entity, config)

    if spark is None:
        raise RuntimeError(
            "Spark session is required for live Bronze ingestion. "
            "Use --dry-run for local CSV validation."
        )

    from pyspark.sql import functions as F

    definition = ENTITY_DEFINITIONS[entity]
    csv_path = config.source_path(entity)
    source_file_name = definition["source_file"]

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing source file: {csv_path}")

    dataframe = (
        spark.read.option("header", True)
        .option("inferSchema", False)
        .csv(str(csv_path))
    )

    for column_name in definition["columns"]:
        if column_name not in dataframe.columns:
            raise ValueError(f"{entity}: missing column '{column_name}' in {csv_path.name}")
        dataframe = dataframe.withColumn(column_name, F.col(column_name).cast("string"))

    dataframe = dataframe.withColumn("_ingestion_timestamp", F.current_timestamp())
    dataframe = dataframe.withColumn("_source_file", F.lit(source_file_name))

    select_columns = list(definition["columns"]) + list(METADATA_COLUMNS)
    dataframe = dataframe.select(*select_columns)

    target_table = config.table_fqn(entity)
    (
        dataframe.write.format("delta")
        .mode(config.write_mode)
        .saveAsTable(target_table)
    )

    return {
        "entity": entity,
        "source_file": str(csv_path),
        "row_count": dataframe.count(),
        "bronze_columns": select_columns,
        "target_table": target_table,
        "write_mode": config.write_mode,
        "dry_run": False,
    }


def run_ingestion(
    config: BronzeConfig,
    *,
    spark=None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Run Bronze ingestion for customers, products, and orders."""
    return [
        ingest_entity_to_bronze(entity, config, spark=spark, dry_run=dry_run)
        for entity in INGESTION_ORDER
    ]


def format_dry_run_report(results: list[dict[str, Any]]) -> str:
    lines = ["Bronze dry-run validation passed.", ""]
    for result in results:
        lines.extend(
            [
                f"[{result['entity']}]",
                f"  source:   {result['source_file']}",
                f"  target:   {result['target_table']}",
                f"  rows:     {result['row_count']}",
                f"  mode:     {result['write_mode']} (Delta)",
                f"  columns:  {', '.join(result['bronze_columns'])} (all STRING + metadata)",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
