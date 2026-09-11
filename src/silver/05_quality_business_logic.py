"""Silver data quality — business logic checks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    CHECK_BUSINESS_LOGIC,
    SilverConfig,
    build_failures_from_rules,
    col_is_blank,
    col_is_valid_customer_segment,
    notebook_spark_if_defined,
    prepare_canonical_entity_df,
    prepare_entity_dataframe,
    read_bronze_table,
    require_pyspark,
    resolve_spark,
)


def check_customer_business_logic(df, config: SilverConfig, spark):
    from pyspark.sql import functions as F

    rules = [
        (
            F.col("signup_date_typed").isNotNull()
            & (F.col("signup_date_typed") > F.current_date()),
            "Signup date is in the future",
            "signup_date",
        ),
        (
            ~col_is_blank("customer_segment")
            & ~col_is_valid_customer_segment("customer_segment"),
            "Customer segment is not one of Premium, Standard, Basic",
            "customer_segment",
        ),
    ]
    failures = build_failures_from_rules(
        df, "customers", config, CHECK_BUSINESS_LOGIC, rules, spark=spark
    )
    return df, failures


def check_product_business_logic(df, config: SilverConfig, spark):
    from pyspark.sql import functions as F

    rules = [
        (
            F.col("unit_price_typed").isNotNull() & (F.col("unit_price_typed") < F.lit(0)),
            "Product unit price must be non-negative",
            "unit_price",
        ),
    ]
    failures = build_failures_from_rules(
        df, "products", config, CHECK_BUSINESS_LOGIC, rules, spark=spark
    )
    return df, failures


def check_order_business_logic(df, canonical_products_df, config: SilverConfig, spark):
    from pyspark.sql import functions as F

    catalog_prices = canonical_products_df.select(
        F.col("product_id"),
        F.col("unit_price_typed").alias("_catalog_unit_price_typed"),
    )
    orders_marked = df.join(catalog_prices, on="product_id", how="left")

    rules = [
        (
            F.col("quantity_typed").isNotNull() & (F.col("quantity_typed") <= F.lit(0)),
            "Order quantity must be greater than zero",
            "quantity",
        ),
        (
            F.col("order_date_typed").isNotNull()
            & (F.col("order_date_typed") > F.current_date()),
            "Order date is in the future",
            "order_date",
        ),
        (
            F.col("unit_price_typed").isNotNull()
            & F.col("_catalog_unit_price_typed").isNotNull()
            & (F.col("unit_price_typed") != F.col("_catalog_unit_price_typed")),
            "Order unit price does not match product catalog price",
            "unit_price",
        ),
    ]
    failures = build_failures_from_rules(
        orders_marked, "orders", config, CHECK_BUSINESS_LOGIC, rules, spark=spark
    )
    return orders_marked, failures


def run_business_logic_for_entity(
    spark, entity_key: str, config: SilverConfig | None = None, canonical_products_df=None
):
    config = config or SilverConfig()
    bronze_df = read_bronze_table(spark, config, entity_key)
    prepared = prepare_entity_dataframe(bronze_df, entity_key)

    if entity_key == "customers":
        return check_customer_business_logic(prepared, config, spark)
    if entity_key == "products":
        return check_product_business_logic(prepared, config, spark)
    if entity_key == "orders":
        if canonical_products_df is None:
            _, canonical_products_df = prepare_canonical_entity_df(spark, config, "products")
        return check_order_business_logic(prepared, canonical_products_df, config, spark)
    raise ValueError(f"Unsupported entity_key: {entity_key}")


def run_business_logic_all(spark, config: SilverConfig | None = None) -> dict:
    config = config or SilverConfig()
    _, canonical_products = prepare_canonical_entity_df(spark, config, "products")

    results = {}
    for entity_key in ("customers", "products", "orders"):
        if entity_key == "orders":
            prepared, failures = run_business_logic_for_entity(
                spark, entity_key, config, canonical_products_df=canonical_products
            )
        else:
            prepared, failures = run_business_logic_for_entity(spark, entity_key, config)
        results[entity_key] = {"prepared_df": prepared, "failures_df": failures}
    return results


def main() -> None:
    require_pyspark()
    spark = resolve_spark(notebook_spark_if_defined())
    config = SilverConfig()

    print("Silver — Business logic checks")
    results = run_business_logic_all(spark, config)
    for entity_key in ("customers", "products", "orders"):
        failures = results[entity_key]["failures_df"]
        print(f"[business_logic] {entity_key}: {failures.count()} failure record(s)")


if __name__ == "__main__":
    main()
