-- Pipeline Validation Script — DE_C1_Coding_Evaluation (Nikhil Kr. Nirmal)
-- Catalog: de_c1_coding_evaluation
-- Execute on Databricks Serverless after Bronze → Silver → Gold pipelines have run.
-- Notebook: databricks/notebooks/04_run_validation
--
-- Output columns per check: check_name, expected, actual, status (PASS | FAIL)
-- Target: 26 checks
--
-- Local alternatives (no Databricks):
--   python src/bronze/ingest_all.py --dry-run
--   python src/silver/test_silver_helpers.py

-- =============================================================================
-- A. BRONZE VALIDATION (4 checks)
-- =============================================================================

-- A1. Bronze row counts match seed-42 CSV expectations
SELECT
    'bronze_row_counts' AS check_name,
    'customers=1006; products=206; orders=5163' AS expected,
    CONCAT(
        'customers=', CAST(c.cnt AS STRING),
        '; products=', CAST(p.cnt AS STRING),
        '; orders=', CAST(o.cnt AS STRING)
    ) AS actual,
    CASE
        WHEN c.cnt = 1006 AND p.cnt = 206 AND o.cnt = 5163 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.bronze.bronze_customers) c
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.bronze.bronze_products) p
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.bronze.bronze_orders) o;

-- A2. Bronze customers — required business columns present
SELECT
    'bronze_customers_columns' AS check_name,
    '7 business columns' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 7 THEN 'PASS' ELSE 'FAIL' END AS status
FROM system.information_schema.columns
WHERE table_catalog = 'de_c1_coding_evaluation'
  AND table_schema = 'bronze'
  AND table_name = 'bronze_customers'
  AND column_name IN (
      'customer_id', 'customer_name', 'email', 'country',
      'signup_date', 'customer_segment', 'lifetime_value'
  );

-- A3. Intentional RI defect preserved — orphan customer_id in Bronze orders
SELECT
    'bronze_orphan_customer_ids' AS check_name,
    '>= 1 (CUST9999)' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) >= 1 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.bronze.bronze_orders
WHERE customer_id = 'CUST9999';

-- A4. Intentional RI defect preserved — orphan product_id in Bronze orders
SELECT
    'bronze_orphan_product_ids' AS check_name,
    '>= 1 (PROD9999)' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) >= 1 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.bronze.bronze_orders
WHERE product_id = 'PROD9999';

-- =============================================================================
-- B. SILVER DATA QUALITY (8 checks)
-- =============================================================================

-- B1. Curated Silver row counts are strictly less than Bronze (defects quarantined)
SELECT
    'silver_curated_less_than_bronze' AS check_name,
    'silver < bronze for all three entities' AS expected,
    CONCAT(
        'customers=', CAST(c.cnt AS STRING), '/1006',
        '; products=', CAST(p.cnt AS STRING), '/206',
        '; orders=', CAST(o.cnt AS STRING), '/5163'
    ) AS actual,
    CASE
        WHEN c.cnt < 1006 AND p.cnt < 206 AND o.cnt < 5163
         AND c.cnt > 0 AND p.cnt > 0 AND o.cnt > 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.silver.silver_customers) c
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.silver.silver_products) p
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.silver.silver_orders) o;

-- B2. DQ summary table populated (13 category rows: 3+3+3+1+3)
SELECT
    'silver_dq_summary_rows' AS check_name,
    '13' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 13 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_dq_summary;

-- B3. Referential integrity failures detected for orders (intentional orphans)
SELECT
    'silver_ri_orders_failed' AS check_name,
    '> 0 (CUST9999/PROD9999 orphans expected)' AS expected,
    CAST(failed_records AS STRING) AS actual,
    CASE WHEN failed_records > 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_dq_summary
WHERE entity = 'orders' AND check_category = 'referential_integrity';

-- B4. Completeness failures detected for customers (intentional blanks)
SELECT
    'silver_completeness_customers_failed' AS check_name,
    '> 0' AS expected,
    CAST(failed_records AS STRING) AS actual,
    CASE WHEN failed_records > 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_dq_summary
WHERE entity = 'customers' AND check_category = 'completeness';

-- B5. No orphan product FKs in curated Silver orders
SELECT
    'silver_orphan_product_fks' AS check_name,
    '0' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_orders o
LEFT JOIN de_c1_coding_evaluation.silver.silver_products p
    ON o.product_id = p.product_id
WHERE p.product_id IS NULL;

-- B6. No orphan customer FKs in curated Silver orders
SELECT
    'silver_orphan_customer_fks' AS check_name,
    '0' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_orders o
LEFT JOIN de_c1_coding_evaluation.silver.silver_customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- B7. Quarantine table captures intentional defects
SELECT
    'silver_quarantine_non_empty' AS check_name,
    '> 0' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.silver.silver_quarantine_records;

-- B8. Curated customers — no duplicate customer_id
SELECT
    'silver_customers_pk_unique' AS check_name,
    '0 duplicate customer_id' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT customer_id
    FROM de_c1_coding_evaluation.silver.silver_customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) dups;

-- =============================================================================
-- C. GOLD VALIDATION (6 checks)
-- =============================================================================

-- C1. All four Gold tables populated
SELECT
    'gold_tables_non_empty' AS check_name,
    'all four tables > 0 rows' AS expected,
    CONCAT(
        'sales=', CAST(s.cnt AS STRING),
        '; customer=', CAST(c.cnt AS STRING),
        '; trends=', CAST(t.cnt AS STRING),
        '; segmentation=', CAST(g.cnt AS STRING)
    ) AS actual,
    CASE
        WHEN s.cnt > 0 AND c.cnt > 0 AND t.cnt > 0 AND g.cnt > 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.gold.gold_sales_by_product) s
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer) c
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends) t
CROSS JOIN (SELECT COUNT(*) AS cnt FROM de_c1_coding_evaluation.gold.gold_customer_segmentation) g;

-- C2. Gold sales-by-product — one row per product_id
SELECT
    'gold_sales_by_product_unique_grain' AS check_name,
    '0 duplicate product_id' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT product_id
    FROM de_c1_coding_evaluation.gold.gold_sales_by_product
    GROUP BY product_id
    HAVING COUNT(*) > 1
) dups;

-- C3. Gold revenue-by-customer — one row per customer_id
SELECT
    'gold_revenue_by_customer_unique_grain' AS check_name,
    '0 duplicate customer_id' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT customer_id
    FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) dups;

-- C4. Gold trends — daily and weekly period types both present
SELECT
    'gold_trend_period_types' AS check_name,
    'daily > 0 AND weekly > 0' AS expected,
    CONCAT(
        'daily=', CAST(SUM(CASE WHEN period_type = 'daily' THEN 1 ELSE 0 END) AS STRING),
        '; weekly=', CAST(SUM(CASE WHEN period_type = 'weekly' THEN 1 ELSE 0 END) AS STRING)
    ) AS actual,
    CASE
        WHEN SUM(CASE WHEN period_type = 'daily' THEN 1 ELSE 0 END) > 0
         AND SUM(CASE WHEN period_type = 'weekly' THEN 1 ELSE 0 END) > 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends;

-- C5. Gold customer segmentation — three master-data segments
SELECT
    'gold_segmentation_three_segments' AS check_name,
    'Premium, Standard, Basic (3 rows)' AS expected,
    CONCAT(
        'rows=', CAST(COUNT(*) AS STRING),
        '; segments=', CAST(COUNT(DISTINCT customer_segment) AS STRING)
    ) AS actual,
    CASE
        WHEN COUNT(*) = 3
         AND COUNT(DISTINCT customer_segment) = 3
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM de_c1_coding_evaluation.gold.gold_customer_segmentation
WHERE customer_segment IN ('Premium', 'Standard', 'Basic');

-- C6. Gold sales products are subset of Silver products catalog
SELECT
    'gold_sales_products_in_silver_catalog' AS check_name,
    '0 products outside silver_products' AS expected,
    CAST(COUNT(*) AS STRING) AS actual,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM de_c1_coding_evaluation.gold.gold_sales_by_product g
LEFT JOIN de_c1_coding_evaluation.silver.silver_products p
    ON g.product_id = p.product_id
WHERE p.product_id IS NULL;

-- =============================================================================
-- D. RECONCILIATION (6 checks)
-- =============================================================================

-- D1. Total revenue reconciles across Gold entity tables (tolerance 0.01)
WITH totals AS (
    SELECT
        (SELECT SUM(total_revenue) FROM de_c1_coding_evaluation.gold.gold_sales_by_product) AS sales_revenue,
        (SELECT SUM(total_revenue) FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer) AS customer_revenue,
        (SELECT SUM(total_revenue) FROM de_c1_coding_evaluation.gold.gold_customer_segmentation) AS segmentation_revenue,
        (SELECT SUM(total_revenue) FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends WHERE period_type = 'daily') AS daily_revenue,
        (SELECT SUM(total_revenue) FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends WHERE period_type = 'weekly') AS weekly_revenue
)
SELECT
    'gold_revenue_reconciliation' AS check_name,
    'sales = customer = segmentation = daily = weekly (±0.01)' AS expected,
    CONCAT(
        'sales=', CAST(ROUND(sales_revenue, 2) AS STRING),
        '; customer=', CAST(ROUND(customer_revenue, 2) AS STRING),
        '; segmentation=', CAST(ROUND(segmentation_revenue, 2) AS STRING),
        '; daily=', CAST(ROUND(daily_revenue, 2) AS STRING),
        '; weekly=', CAST(ROUND(weekly_revenue, 2) AS STRING)
    ) AS actual,
    CASE
        WHEN ABS(sales_revenue - customer_revenue) < 0.01
         AND ABS(customer_revenue - segmentation_revenue) < 0.01
         AND ABS(sales_revenue - daily_revenue) < 0.01
         AND ABS(sales_revenue - weekly_revenue) < 0.01
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM totals;

-- D2. Line-item count in Gold sales equals curated Silver orders
SELECT
    'gold_line_items_match_silver_orders' AS check_name,
    'gold line_item_count sum = silver_orders count' AS expected,
    CONCAT(
        'gold=', CAST(g.total_lines AS STRING),
        '; silver=', CAST(s.silver_lines AS STRING)
    ) AS actual,
    CASE WHEN g.total_lines = s.silver_lines THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(line_item_count) AS total_lines
    FROM de_c1_coding_evaluation.gold.gold_sales_by_product
) g
CROSS JOIN (
    SELECT COUNT(*) AS silver_lines
    FROM de_c1_coding_evaluation.silver.silver_orders
) s;

-- D3. Distinct order counts reconcile (silver vs gold daily/weekly trends)
-- Note: SUM(order_count) per product in gold_sales_by_product double-counts multi-product
-- orders, so reconciliation uses silver distinct order_id vs trend grain totals.
SELECT
    'gold_order_count_reconciliation' AS check_name,
    'silver distinct = daily sum = weekly sum' AS expected,
    CONCAT(
        'silver=', CAST(s.silver_orders AS STRING),
        '; daily=', CAST(d.daily_orders AS STRING),
        '; weekly=', CAST(w.weekly_orders AS STRING)
    ) AS actual,
    CASE
        WHEN s.silver_orders = d.daily_orders
         AND s.silver_orders = w.weekly_orders
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT COUNT(DISTINCT order_id) AS silver_orders
    FROM de_c1_coding_evaluation.silver.silver_orders
) s
CROSS JOIN (
    SELECT SUM(order_count) AS daily_orders
    FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
    WHERE period_type = 'daily'
) d
CROSS JOIN (
    SELECT SUM(order_count) AS weekly_orders
    FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
    WHERE period_type = 'weekly'
) w;

-- D4. Weekly trend order totals match daily (same underlying orders)
SELECT
    'gold_weekly_order_count_matches_daily' AS check_name,
    'weekly sum = daily sum' AS expected,
    CONCAT(
        'daily=', CAST(d.daily_orders AS STRING),
        '; weekly=', CAST(w.weekly_orders AS STRING)
    ) AS actual,
    CASE WHEN d.daily_orders = w.weekly_orders THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(order_count) AS daily_orders
    FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
    WHERE period_type = 'daily'
) d
CROSS JOIN (
    SELECT SUM(order_count) AS weekly_orders
    FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
    WHERE period_type = 'weekly'
) w;

-- D5. Segmentation customer_count sums to all Silver customers (includes zero-order)
SELECT
    'gold_segmentation_customer_count' AS check_name,
    'segmentation customer_count sum = silver_customers count' AS expected,
    CONCAT(
        'segmentation=', CAST(g.total_customers AS STRING),
        '; silver=', CAST(s.silver_customers AS STRING)
    ) AS actual,
    CASE WHEN g.total_customers = s.silver_customers THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(customer_count) AS total_customers
    FROM de_c1_coding_evaluation.gold.gold_customer_segmentation
) g
CROSS JOIN (
    SELECT COUNT(*) AS silver_customers
    FROM de_c1_coding_evaluation.silver.silver_customers
) s;

-- D6. Silver order revenue equals Gold sales revenue (line_revenue rule)
SELECT
    'silver_to_gold_revenue_reconciliation' AS check_name,
    'SUM(qty*price) silver = SUM(total_revenue) gold sales (±0.01)' AS expected,
    CONCAT(
        'silver=', CAST(ROUND(s.silver_revenue, 2) AS STRING),
        '; gold=', CAST(ROUND(g.gold_revenue, 2) AS STRING)
    ) AS actual,
    CASE WHEN ABS(s.silver_revenue - g.gold_revenue) < 0.01 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT SUM(quantity * unit_price) AS silver_revenue
    FROM de_c1_coding_evaluation.silver.silver_orders
) s
CROSS JOIN (
    SELECT SUM(total_revenue) AS gold_revenue
    FROM de_c1_coding_evaluation.gold.gold_sales_by_product
) g;

-- =============================================================================
-- E. DASHBOARD VALIDATION (2 checks — Gold-source logic for dashboard queries)
-- =============================================================================

-- E1. Top 10 products by revenue — sorted descending
WITH top10 AS (
    SELECT total_revenue
    FROM de_c1_coding_evaluation.gold.gold_sales_by_product
    ORDER BY total_revenue DESC, product_id
    LIMIT 10
),
ordered AS (
    SELECT
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY total_revenue DESC) AS prev_revenue
    FROM top10
)
SELECT
    'dashboard_top10_revenue_sort' AS check_name,
    '10 rows; each <= previous' AS expected,
    CONCAT(
        'rows=', CAST((SELECT COUNT(*) FROM top10) AS STRING),
        '; violations=', CAST((SELECT COUNT(*) FROM ordered WHERE prev_revenue IS NOT NULL AND total_revenue > prev_revenue) AS STRING)
    ) AS actual,
    CASE
        WHEN (SELECT COUNT(*) FROM top10) = 10
         AND (SELECT COUNT(*) FROM ordered WHERE prev_revenue IS NOT NULL AND total_revenue > prev_revenue) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status;

-- E2. Top 10 products by quantity — sorted descending
WITH top10 AS (
    SELECT total_quantity_sold
    FROM de_c1_coding_evaluation.gold.gold_sales_by_product
    ORDER BY total_quantity_sold DESC, product_id
    LIMIT 10
),
ordered AS (
    SELECT
        total_quantity_sold,
        LAG(total_quantity_sold) OVER (ORDER BY total_quantity_sold DESC) AS prev_qty
    FROM top10
)
SELECT
    'dashboard_top10_quantity_sort' AS check_name,
    '10 rows; each <= previous' AS expected,
    CONCAT(
        'rows=', CAST((SELECT COUNT(*) FROM top10) AS STRING),
        '; violations=', CAST((SELECT COUNT(*) FROM ordered WHERE prev_qty IS NOT NULL AND total_quantity_sold > prev_qty) AS STRING)
    ) AS actual,
    CASE
        WHEN (SELECT COUNT(*) FROM top10) = 10
         AND (SELECT COUNT(*) FROM ordered WHERE prev_qty IS NOT NULL AND total_quantity_sold > prev_qty) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status;
