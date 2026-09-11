-- =============================================================================
-- DE_C1 Coding Evaluation — Dashboard Queries (Gold Layer Only)
-- Candidate: Nikhil Kr. Nirmal
-- Catalog: de_c1_coding_evaluation | Schema: gold
--
-- Source tables (read-only):
--   gold_sales_by_product
--   gold_revenue_by_customer
--   gold_daily_weekly_trends
--   gold_customer_segmentation
--
-- Do NOT join Bronze, Silver, quarantine, or raw CSV files.
-- =============================================================================


-- =============================================================================
-- PAGE 1: EXECUTIVE OVERVIEW
-- KPIs, daily trends, weekly trends
-- =============================================================================

-- Q1.1 — KPI: Total Revenue (counter / single-value visualization)
SELECT
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily';


-- Q1.2 — KPI: Total Order Count (counter)
SELECT
    SUM(order_count) AS total_order_count
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily';


-- Q1.3 — KPI: Total Customer Count (counter; includes zero-order customers)
SELECT
    SUM(customer_count) AS total_customer_count
FROM de_c1_coding_evaluation.gold.gold_customer_segmentation;


-- Q1.4 — KPI: Average Order Value (counter)
SELECT
    ROUND(
        SUM(total_revenue) / NULLIF(SUM(order_count), 0),
        2
    ) AS avg_order_value
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily';


-- Q1.5 — Daily Revenue Trend (line chart: x = date, y = revenue)
SELECT
    period_start_date AS order_date,
    ROUND(total_revenue, 2) AS total_revenue
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily'
ORDER BY period_start_date;


-- Q1.6 — Daily Order Volume Trend (line chart: x = date, y = orders)
SELECT
    period_start_date AS order_date,
    order_count
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily'
ORDER BY period_start_date;


-- Q1.7 — Weekly Revenue Trend (bar or line chart)
SELECT
    period_start_date AS week_start,
    period_end_date AS week_end,
    ROUND(total_revenue, 2) AS total_revenue
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'weekly'
ORDER BY period_start_date;


-- Q1.8 — Weekly Order Volume Trend (bar chart)
SELECT
    period_start_date AS week_start,
    period_end_date AS week_end,
    order_count
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'weekly'
ORDER BY period_start_date;


-- Q1.9 — Executive Summary Table (table visualization: daily KPI snapshot)
SELECT
    period_start_date AS order_date,
    ROUND(total_revenue, 2) AS total_revenue,
    order_count,
    line_item_count,
    ROUND(total_revenue / NULLIF(order_count, 0), 2) AS avg_order_value
FROM de_c1_coding_evaluation.gold.gold_daily_weekly_trends
WHERE period_type = 'daily'
ORDER BY period_start_date DESC;


-- =============================================================================
-- PAGE 2: PRODUCT PERFORMANCE
-- Top products, category breakdowns
-- =============================================================================

-- Q2.1 — Top 10 Products by Revenue (horizontal bar chart)
SELECT
    product_name,
    category,
    ROUND(total_revenue, 2) AS total_revenue,
    total_quantity_sold,
    order_count
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;


-- Q2.2 — Revenue by Category (pie or bar chart)
SELECT
    category,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    SUM(total_quantity_sold) AS total_quantity_sold,
    SUM(order_count) AS order_count
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
GROUP BY category
ORDER BY total_revenue DESC;


-- Q2.3 — Quantity Sold by Category (bar chart)
SELECT
    category,
    SUM(total_quantity_sold) AS total_quantity_sold
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
GROUP BY category
ORDER BY total_quantity_sold DESC;


-- Q2.4 — Top 10 Products by Quantity Sold (bar chart)
SELECT
    product_name,
    category,
    total_quantity_sold,
    ROUND(total_revenue, 2) AS total_revenue
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
ORDER BY total_quantity_sold DESC
LIMIT 10;


-- Q2.5 — Category Performance Summary (table)
SELECT
    category,
    COUNT(*) AS product_count,
    SUM(total_quantity_sold) AS total_quantity_sold,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(AVG(total_revenue), 2) AS avg_revenue_per_product,
    SUM(order_count) AS order_count
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
GROUP BY category
ORDER BY total_revenue DESC;


-- Q2.6 — Product Revenue Distribution (scatter: quantity vs revenue)
SELECT
    product_name,
    category,
    total_quantity_sold,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_revenue / NULLIF(total_quantity_sold, 0), 2) AS avg_unit_revenue
FROM de_c1_coding_evaluation.gold.gold_sales_by_product
ORDER BY total_revenue DESC;


-- =============================================================================
-- PAGE 3: CUSTOMER INSIGHTS
-- Top customers, segmentation, geography
-- =============================================================================

-- Q3.1 — Top 10 Customers by Spend (horizontal bar chart)
SELECT
    customer_name,
    customer_segment,
    country,
    ROUND(total_revenue, 2) AS total_revenue,
    order_count,
    total_quantity_purchased
FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer
ORDER BY total_revenue DESC
LIMIT 10;


-- Q3.2 — Customer Segmentation: Revenue Breakdown (pie or bar chart)
SELECT
    customer_segment,
    ROUND(total_revenue, 2) AS total_revenue,
    order_count,
    ROUND(avg_revenue_per_customer, 2) AS avg_revenue_per_customer
FROM de_c1_coding_evaluation.gold.gold_customer_segmentation
ORDER BY total_revenue DESC;


-- Q3.3 — Customer Segmentation: Customer Count (pie or bar chart)
SELECT
    customer_segment,
    customer_count,
    ROUND(
        100.0 * customer_count / SUM(customer_count) OVER (),
        1
    ) AS pct_of_customers
FROM de_c1_coding_evaluation.gold.gold_customer_segmentation
ORDER BY customer_count DESC;


-- Q3.4 — Revenue by Country (bar or map visualization)
SELECT
    country,
    COUNT(*) AS active_customer_count,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    SUM(order_count) AS order_count,
    ROUND(AVG(total_revenue), 2) AS avg_revenue_per_customer
FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer
GROUP BY country
ORDER BY total_revenue DESC;


-- Q3.5 — Customer Segment × Country Heatmap Data (pivot-ready table)
SELECT
    country,
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM de_c1_coding_evaluation.gold.gold_revenue_by_customer
GROUP BY country, customer_segment
ORDER BY country, customer_segment;


-- Q3.6 — Segmentation Summary Table (table visualization)
SELECT
    customer_segment,
    customer_count,
    order_count,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(avg_revenue_per_customer, 2) AS avg_revenue_per_customer,
    ROUND(
        100.0 * total_revenue / SUM(total_revenue) OVER (),
        1
    ) AS pct_of_total_revenue
FROM de_c1_coding_evaluation.gold.gold_customer_segmentation
ORDER BY total_revenue DESC;
