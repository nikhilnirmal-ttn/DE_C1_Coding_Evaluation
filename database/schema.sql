-- =============================================================================
-- DE_C1_Coding_Evaluation — Source relational schema (documentary)
-- Candidate: Nikhil Kr. Nirmal
-- =============================================================================
--
-- Purpose:
--   Logical source data model matching committed CSV files under data/.
--
-- Dialect:
--   Portable ANSI-style DDL with PostgreSQL-compatible syntax.
--   No external RDBMS deployment is evidenced; documents the source contract.
--
-- Grain:
--   orders = ORDER LINE ITEMS (one row per order_line_id).
--
-- Identifier types:
--   Business keys are STRING in CSV/Bronze (e.g. CUST0001, PROD0042, OL000001).
--   This DDL uses VARCHAR for keys to match the committed files.
--
-- Intentional defects:
--   Seed CSVs include documented defects (see DATA_GENERATION_NOTES.md).
--   Foreign keys are documented logically but NOT enforced below.
--
-- Pipeline:
--   CSV -> Bronze (STRING) -> Silver (DQ) -> Gold -> Dashboard
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS source;

-- -----------------------------------------------------------------------------
-- customers — dimension (data/customers.csv, 1,006 rows)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS source.customers (
    customer_id       VARCHAR(20)    NOT NULL,
    customer_name     VARCHAR(255)   NOT NULL,
    email             VARCHAR(320)   NOT NULL,
    country           VARCHAR(100)   NOT NULL,
    signup_date       DATE           NOT NULL,
    customer_segment  VARCHAR(20)    NOT NULL,  -- Premium | Standard | Basic
    lifetime_value    DECIMAL(12, 2) NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id)
);

COMMENT ON TABLE source.customers IS
    'Customer dimension. Source: data/customers.csv (1,006 rows, seed 42).';

-- -----------------------------------------------------------------------------
-- products — dimension (data/products.csv, 206 rows)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS source.products (
    product_id    VARCHAR(20)    NOT NULL,
    product_name  VARCHAR(255)   NOT NULL,
    category      VARCHAR(100)   NOT NULL,
    unit_price    DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_products PRIMARY KEY (product_id)
);

COMMENT ON TABLE source.products IS
    'Product dimension. Source: data/products.csv (206 rows, seed 42).';

-- -----------------------------------------------------------------------------
-- orders — order LINE ITEMS (data/orders.csv, 5,163 rows)
-- -----------------------------------------------------------------------------
-- Logical relationships (NOT enforced — intentional orphan FKs in seed):
--   orders.customer_id -> customers.customer_id  (CUST9999 orphan rows)
--   orders.product_id  -> products.product_id   (PROD9999 orphan rows)
CREATE TABLE IF NOT EXISTS source.orders (
    order_line_id  VARCHAR(20)    NOT NULL,
    order_id       VARCHAR(20)    NOT NULL,
    customer_id    VARCHAR(20)    NOT NULL,
    product_id     VARCHAR(20)    NOT NULL,
    order_date     DATE           NOT NULL,
    quantity       INTEGER        NOT NULL,
    unit_price     DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (order_line_id)
);

COMMENT ON TABLE source.orders IS
    'Order line-item fact. Source: data/orders.csv (5,163 rows, seed 42). '
    'Revenue derived as quantity * unit_price in Gold.';

COMMENT ON COLUMN source.orders.order_line_id IS 'Primary key — one row per line item.';
COMMENT ON COLUMN source.orders.order_id IS 'Groups 1–3 line items per customer order.';

-- -----------------------------------------------------------------------------
-- Column inventory (CSV header order)
-- -----------------------------------------------------------------------------
-- customers:  customer_id, customer_name, email, country, signup_date,
--             customer_segment, lifetime_value
-- products:   product_id, product_name, category, unit_price
-- orders:     order_line_id, order_id, customer_id, product_id, order_date,
--             quantity, unit_price
