-- Gold: product-level sales aggregates (Silver only)
CREATE OR REPLACE TABLE de_c1_coding_evaluation.gold.gold_sales_by_product
AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS total_quantity_sold,
    SUM(o.quantity * o.unit_price) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(*) AS line_item_count
FROM de_c1_coding_evaluation.silver.silver_orders AS o
INNER JOIN de_c1_coding_evaluation.silver.silver_products AS p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
