-- Gold: daily and weekly revenue trends (Silver only)
CREATE OR REPLACE TABLE de_c1_coding_evaluation.gold.gold_daily_weekly_trends
AS
WITH order_lines AS (
    SELECT
        order_id,
        order_date,
        quantity * unit_price AS line_revenue
    FROM de_c1_coding_evaluation.silver.silver_orders
),
daily AS (
    SELECT
        'daily' AS period_type,
        order_date AS period_start_date,
        CAST(NULL AS DATE) AS period_end_date,
        SUM(line_revenue) AS total_revenue,
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(*) AS line_item_count
    FROM order_lines
    GROUP BY order_date
),
weekly AS (
    SELECT
        'weekly' AS period_type,
        CAST(DATE_TRUNC('week', order_date) AS DATE) AS period_start_date,
        CAST(DATE_ADD(DATE_TRUNC('week', order_date), 6) AS DATE) AS period_end_date,
        SUM(line_revenue) AS total_revenue,
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(*) AS line_item_count
    FROM order_lines
    GROUP BY DATE_TRUNC('week', order_date)
)
SELECT
    period_type,
    period_start_date,
    period_end_date,
    total_revenue,
    order_count,
    line_item_count
FROM daily
UNION ALL
SELECT
    period_type,
    period_start_date,
    period_end_date,
    total_revenue,
    order_count,
    line_item_count
FROM weekly
