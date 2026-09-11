-- Gold: customer-segment analytics (Silver only)
CREATE OR REPLACE TABLE de_c1_coding_evaluation.gold.gold_customer_segmentation
AS
WITH customer_orders AS (
    SELECT
        c.customer_segment,
        c.customer_id,
        o.order_id,
        o.quantity * o.unit_price AS line_revenue
    FROM de_c1_coding_evaluation.silver.silver_customers AS c
    LEFT JOIN de_c1_coding_evaluation.silver.silver_orders AS o
        ON c.customer_id = o.customer_id
)
SELECT
    customer_segment,
    COUNT(DISTINCT customer_id) AS customer_count,
    COUNT(DISTINCT order_id) AS order_count,
    COALESCE(SUM(line_revenue), 0) AS total_revenue,
    ROUND(
        COALESCE(SUM(line_revenue), 0) / COUNT(DISTINCT customer_id),
        2
    ) AS avg_revenue_per_customer
FROM customer_orders
GROUP BY customer_segment
