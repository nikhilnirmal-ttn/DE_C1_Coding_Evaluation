"""Silver data quality — referential integrity checks."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_REFERENTIAL_INTEGRITY,
    SilverConfig,
    build_failures_from_rules,
    col_is_blank,
    curated_eligible_parent_keys_df,
    notebook_spark_if_defined,
    prepare_entity_dataframe,
    read_bronze_table,
    require_pyspark,
    resolve_spark,
)


def _load_module(stem: str) -> ModuleType:
    module_path = Path(__file__).resolve().parent / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prerequisite_dq_results(spark, config: SilverConfig) -> dict:
    completeness = _load_module("01_quality_completeness").run_completeness_all(spark, config)
    uniqueness = _load_module("02_quality_uniqueness").run_uniqueness_all(spark, config)
    type_validation = _load_module("03_quality_type_validation").run_type_validation_all(
        spark, config
    )
    business_logic = _load_module("05_quality_business_logic").run_business_logic_all(
        spark, config
    )
    return {
        "completeness": completeness,
        "uniqueness": uniqueness,
        "type_validation": type_validation,
        "business_logic": business_logic,
    }


def check_referential_integrity(
    orders_df,
    customer_parent_keys_df,
    product_parent_keys_df,
    config: SilverConfig,
    spark,
):
    """Flag order rows whose FKs do not resolve to curated-eligible parents."""
    from pyspark.sql import functions as F

    customer_keys = customer_parent_keys_df.withColumn("_customer_parent_ok", F.lit(True))
    product_keys = product_parent_keys_df.withColumn("_product_parent_ok", F.lit(True))

    orders_marked = (
        orders_df.join(customer_keys, on="customer_id", how="left")
        .join(product_keys, on="product_id", how="left")
    )

    orphan_customer = ~col_is_blank("customer_id") & F.col("_customer_parent_ok").isNull()
    orphan_product = ~col_is_blank("product_id") & F.col("_product_parent_ok").isNull()

    failures = build_failures_from_rules(
        orders_marked,
        "orders",
        config,
        CHECK_REFERENTIAL_INTEGRITY,
        [
            (
                orphan_customer,
                "Foreign key 'customer_id' does not resolve to a valid customer",
                "customer_id",
            ),
            (
                orphan_product,
                "Foreign key 'product_id' does not resolve to a valid product",
                "product_id",
            ),
        ],
        spark=spark,
    )
    return orders_marked, failures


def run_referential_integrity_all(
    spark,
    config: SilverConfig | None = None,
    dq_results: dict | None = None,
) -> dict:
    config = config or SilverConfig()
    if dq_results is None:
        dq_results = _prerequisite_dq_results(spark, config)

    customer_parent_keys = curated_eligible_parent_keys_df(
        dq_results["business_logic"]["customers"]["prepared_df"],
        "customers",
        dq_results,
    )
    product_parent_keys = curated_eligible_parent_keys_df(
        dq_results["business_logic"]["products"]["prepared_df"],
        "products",
        dq_results,
    )

    orders_bronze = read_bronze_table(spark, config, "orders")
    orders_prepared = prepare_entity_dataframe(orders_bronze, "orders")

    orders_marked, failures = check_referential_integrity(
        orders_prepared,
        customer_parent_keys,
        product_parent_keys,
        config,
        spark,
    )

    return {
        "orders": {
            "prepared_df": orders_marked,
            "failures_df": failures,
        }
    }


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — Referential integrity checks")
    results = run_referential_integrity_all(spark, config)
    failures = results["orders"]["failures_df"]
    print(f"[referential_integrity] orders: {failures.count()} failure record(s)")


if __name__ == "__main__":
    main()
