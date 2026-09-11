-- Gold: customer-level revenue aggregates (Silver only)
CREATE OR REPLACE TABLE de_c1_coding_evaluation.gold.gold_revenue_by_customer
AS
SELECT
    c.customer_id,
    c.customer_name,
    c.country,
    c.customer_segment,
    SUM(o.quantity * o.unit_price) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.quantity) AS total_quantity_purchased,
    COUNT(*) AS line_item_count
FROM de_c1_coding_evaluation.silver.silver_orders AS o
INNER JOIN de_c1_coding_evaluation.silver.silver_customers AS c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.country,
    c.customer_segment
