"""Silver data quality — quarantine and DQ summary persistence."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_BUSINESS_LOGIC,
    CHECK_COMPLETENESS,
    CHECK_REFERENTIAL_INTEGRITY,
    CHECK_TYPE_VALIDATION,
    CHECK_UNIQUENESS,
    DQ_SUMMARY_COLUMNS,
    DQ_SUMMARY_TABLE_NAME,
    ENTITY_KEYS,
    QUARANTINE_COLUMNS,
    QUARANTINE_TABLE_NAME,
    SilverConfig,
    calculate_summary_metrics,
    ensure_silver_schema_exists,
    notebook_spark_if_defined,
    require_pyspark,
    resolve_spark,
    silver_table_name,
    union_failures,
    write_delta_table,
)


def _load_module(stem: str) -> ModuleType:
    module_path = Path(__file__).resolve().parent / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_all_dq_checks(spark, config: SilverConfig | None = None) -> dict:
    """Run all five DQ modules with a shared SilverConfig / run_timestamp."""
    config = config or SilverConfig()

    completeness = _load_module("01_quality_completeness").run_completeness_all(spark, config)
    uniqueness = _load_module("02_quality_uniqueness").run_uniqueness_all(spark, config)
    type_validation = _load_module("03_quality_type_validation").run_type_validation_all(
        spark, config
    )
    business_logic = _load_module("05_quality_business_logic").run_business_logic_all(
        spark, config
    )
    dq_before_ri = {
        "completeness": completeness,
        "uniqueness": uniqueness,
        "type_validation": type_validation,
        "business_logic": business_logic,
    }
    referential_integrity = _load_module(
        "04_quality_referential_integrity"
    ).run_referential_integrity_all(spark, config, dq_results=dq_before_ri)

    return {
        "completeness": completeness,
        "uniqueness": uniqueness,
        "type_validation": type_validation,
        "referential_integrity": referential_integrity,
        "business_logic": business_logic,
    }


def count_distinct_failed_rows(failures_df) -> int:
    if failures_df is None:
        return 0
    return failures_df.select("record_key").distinct().count()


def build_category_summary_record(
    check_category: str,
    entity: str,
    tested_df,
    failures_df,
    config: SilverConfig,
) -> dict:
    rows_tested = tested_df.count()
    rows_failed = count_distinct_failed_rows(failures_df)
    metrics = calculate_summary_metrics(rows_tested, rows_failed)

    return {
        "entity": entity,
        "check_category": check_category,
        "total_records": metrics["rows_tested"],
        "failed_records": metrics["rows_failed"],
        "pass_pct": metrics["pass_percentage"],
        "run_timestamp": config.run_timestamp,
    }


def build_dq_summary_records(dq_results: dict, config: SilverConfig) -> list[dict]:
    records: list[dict] = []

    for entity_key in ENTITY_KEYS:
        completeness = dq_results["completeness"][entity_key]
        records.append(
            build_category_summary_record(
                CHECK_COMPLETENESS,
                entity_key,
                completeness["prepared_df"],
                completeness["failures_df"],
                config,
            )
        )

    for entity_key in ENTITY_KEYS:
        uniqueness = dq_results["uniqueness"][entity_key]
        records.append(
            build_category_summary_record(
                CHECK_UNIQUENESS,
                entity_key,
                uniqueness["ranked_df"],
                uniqueness["failures_df"],
                config,
            )
        )

    for entity_key in ENTITY_KEYS:
        type_validation = dq_results["type_validation"][entity_key]
        records.append(
            build_category_summary_record(
                CHECK_TYPE_VALIDATION,
                entity_key,
                type_validation["prepared_df"],
                type_validation["failures_df"],
                config,
            )
        )

    ri = dq_results["referential_integrity"]["orders"]
    records.append(
        build_category_summary_record(
            CHECK_REFERENTIAL_INTEGRITY,
            "orders",
            ri["prepared_df"],
            ri["failures_df"],
            config,
        )
    )

    for entity_key in ENTITY_KEYS:
        business_logic = dq_results["business_logic"][entity_key]
        records.append(
            build_category_summary_record(
                CHECK_BUSINESS_LOGIC,
                entity_key,
                business_logic["prepared_df"],
                business_logic["failures_df"],
                config,
            )
        )

    return records


def build_dq_summary_df(spark, dq_results: dict, config: SilverConfig):
    from pyspark.sql import Row

    records = build_dq_summary_records(dq_results, config)
    if not records:
        return spark.createDataFrame([], schema=_dq_summary_spark_schema())

    rows = [Row(**record) for record in records]
    return spark.createDataFrame(rows).select(*DQ_SUMMARY_COLUMNS)


def _dq_summary_spark_schema():
    from pyspark.sql.types import (
        DoubleType,
        LongType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )

    return StructType(
        [
            StructField("entity", StringType(), False),
            StructField("check_category", StringType(), False),
            StructField("total_records", LongType(), False),
            StructField("failed_records", LongType(), False),
            StructField("pass_pct", DoubleType(), True),
            StructField("run_timestamp", TimestampType(), False),
        ]
    )


def collect_all_quarantine_failures(spark, dq_results: dict):
    frames = []

    for entity_key in ENTITY_KEYS:
        frames.append(dq_results["completeness"][entity_key]["failures_df"])
        frames.append(dq_results["uniqueness"][entity_key]["failures_df"])
        frames.append(dq_results["type_validation"][entity_key]["failures_df"])
        frames.append(dq_results["business_logic"][entity_key]["failures_df"])

    frames.append(dq_results["referential_integrity"]["orders"]["failures_df"])

    return union_failures(spark, *frames).select(*QUARANTINE_COLUMNS)


def write_quarantine_records(
    spark,
    config: SilverConfig,
    failures_df,
    *,
    ensure_schema: bool = True,
) -> str:
    if ensure_schema:
        ensure_silver_schema_exists(spark, config)

    target = silver_table_name(config, QUARANTINE_TABLE_NAME)
    output = failures_df.select(*QUARANTINE_COLUMNS)
    write_delta_table(output, target)
    return target


def write_dq_summary(
    spark,
    config: SilverConfig,
    summary_df,
    *,
    ensure_schema: bool = True,
) -> str:
    if ensure_schema:
        ensure_silver_schema_exists(spark, config)

    target = silver_table_name(config, DQ_SUMMARY_TABLE_NAME)
    write_delta_table(summary_df, target, columns=DQ_SUMMARY_COLUMNS)
    return target


def run_dq_persistence(
    spark,
    config: SilverConfig | None = None,
    *,
    dq_results: dict | None = None,
) -> dict:
    config = config or SilverConfig()
    ensure_silver_schema_exists(spark, config)

    if dq_results is None:
        dq_results = run_all_dq_checks(spark, config)

    quarantine_df = collect_all_quarantine_failures(spark, dq_results)
    summary_df = build_dq_summary_df(spark, dq_results, config)

    quarantine_table = write_quarantine_records(
        spark, config, quarantine_df, ensure_schema=False
    )
    summary_table = write_dq_summary(spark, config, summary_df, ensure_schema=False)

    return {
        "config": config,
        "dq_results": dq_results,
        "quarantine_df": quarantine_df,
        "summary_df": summary_df,
        "quarantine_table": quarantine_table,
        "summary_table": summary_table,
    }


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — DQ persistence")
    result = run_dq_persistence(spark, config)
    print(
        f"[quarantine] wrote {result['quarantine_df'].count()} failure record(s) "
        f"to {result['quarantine_table']}"
    )
    print(
        f"[dq_summary] wrote {result['summary_df'].count()} summary row(s) "
        f"to {result['summary_table']}"
    )


if __name__ == "__main__":
    main()
