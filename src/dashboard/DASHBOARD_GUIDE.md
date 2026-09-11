# Dashboard Guide

**Candidate:** Nikhil Kr. Nirmal  
**Phase:** 6 — Dashboard  
**Catalog:** `de_c1_coding_evaluation`  
**Schema:** `gold` (read-only)

## Purpose

Build a Databricks SQL Dashboard that visualizes pre-computed Gold analytics. All queries in `dashboard_queries.sql` read **only** from Gold tables — never Bronze, Silver, quarantine, or raw CSV files.

## Prerequisites

1. Gold pipeline has run successfully (`databricks/notebooks/03_run_gold`).
2. These tables exist and contain data:

| Table | Use |
|-------|-----|
| `gold_sales_by_product` | Product and category performance |
| `gold_revenue_by_customer` | Customer spend and geography |
| `gold_daily_weekly_trends` | Time-series KPIs (daily + weekly) |
| `gold_customer_segmentation` | Segment rollups (includes zero-order customers) |

Verify in a SQL query:

```sql
SHOW TABLES IN de_c1_coding_evaluation.gold;
```

## Create the Dashboard in Databricks SQL

### Step 1 — Open SQL

1. Log in to your Databricks workspace.
2. In the left sidebar, click **SQL** (or **SQL Editor**).
3. Confirm the warehouse is running (start it if stopped).

### Step 2 — Create queries

For each visualization, create a **Query** from `dashboard_queries.sql`:

1. Click **Create** → **Query**.
2. Paste one query block (e.g. Q1.1 — Total Revenue).
3. Set **Catalog** to `de_c1_coding_evaluation` and **Schema** to `gold` (or use fully qualified names as in the file).
4. Click **Run** to validate results.
5. Click **Save** and name the query (e.g. `Q1.1 - Total Revenue`).

Repeat for every visualization you want on the dashboard. You can reuse the same query with different chart types.

### Step 3 — Create the dashboard

1. Click **Dashboards** in the left sidebar.
2. Click **Create Dashboard**.
3. Name it: `DE_C1 Sales Analytics — Nikhil Kr. Nirmal`.
4. Click **Add** → **Visualization** (or **Add from query**).
5. Select a saved query and choose a chart type (see layout below).
6. Arrange widgets on each page; resize and title each visualization.
7. Click **Publish** when ready.

### Step 4 — Organize pages

Create three dashboard pages matching the SQL file sections:

| Page | Focus | Suggested widgets |
|------|--------|-------------------|
| **Executive Overview** | KPIs + trends | 4 counters (Q1.1–Q1.4), 2 line charts (Q1.5–Q1.6), 2 bar charts (Q1.7–Q1.8), summary table (Q1.9) |
| **Product Performance** | Products & categories | Bar charts (Q2.1, Q2.3, Q2.4), pie/bar by category (Q2.2), tables (Q2.5–Q2.6) |
| **Customer Insights** | Spend & segments | Bar chart top customers (Q3.1), pie charts (Q3.2–Q3.3), country bar (Q3.4), tables (Q3.5–Q3.6) |

### Step 5 — Chart type mapping

| Query | Recommended visualization |
|-------|---------------------------|
| Q1.1 – Q1.4 | **Counter** (single value) |
| Q1.5 – Q1.6 | **Line** (x: date, y: metric) |
| Q1.7 – Q1.8 | **Bar** (x: week, y: metric) |
| Q1.9 | **Table** |
| Q2.1, Q2.4, Q3.1 | **Bar** (horizontal, sorted descending) |
| Q2.2, Q2.3, Q3.2, Q3.3, Q3.4 | **Pie** or **Bar** |
| Q2.5, Q2.6, Q3.5, Q3.6 | **Table** |

### Step 6 — Refresh

Gold tables are overwritten on each Gold pipeline run. After re-running `03_run_gold`:

- Open the dashboard and click **Refresh**, or
- Set a refresh schedule under dashboard settings (optional).

## Screenshots

Save dashboard screenshots for submission and documentation:

```text
src/dashboard/screenshots/
```

Suggested files:

| File | Content |
|------|---------|
| `executive_overview.png` | Page 1 — KPIs and trends |
| `product_performance.png` | Page 2 — products and categories |
| `customer_insights.png` | Page 3 — customers and segmentation |

**How to capture:**

1. Open the published dashboard in Databricks.
2. Navigate to each page.
3. Use your browser screenshot tool or Databricks export (if available).
4. Save PNG files into `src/dashboard/screenshots/`.

## Query inventory

`dashboard_queries.sql` contains **21** visualization-ready `SELECT` statements:

| Section | Queries | Count |
|---------|---------|-------|
| Page 1 — Executive Overview | Q1.1 – Q1.9 | 9 |
| Page 2 — Product Performance | Q2.1 – Q2.6 | 6 |
| Page 3 — Customer Insights | Q3.1 – Q3.6 | 6 |

## Design rules (enforced)

- **Gold only** — no Bronze/Silver/quarantine/CSV joins.
- **Revenue** — already computed in Gold as `quantity * unit_price` at line-item grain.
- **Customer count (KPI)** — use `gold_customer_segmentation` so zero-order customers are included.
- **Order/revenue totals** — aggregate from `gold_daily_weekly_trends` with `period_type = 'daily'` to avoid double-counting weekly rows.

## Troubleshooting

| Issue | Action |
|-------|--------|
| Table not found | Run `00_setup_catalog` then Bronze → Silver → Gold notebooks in order |
| Empty results | Confirm Silver DQ passed and Gold scripts completed without error |
| KPI mismatch | Ensure daily filter on trends table; do not sum daily + weekly together |
| Warehouse timeout | Use a larger SQL warehouse or reduce date range in custom filters |

## Related files

| File | Role |
|------|------|
| `dashboard_queries.sql` | All dashboard SQL |
| `../gold/GOLD_LAYER_NOTES.md` | Gold table definitions and pipeline |
| `../../design-notes.md` | Medallion architecture |
| `../../data-model.md` | Entity and revenue rules |

## Out of scope (Phase 7)

- End-to-end validation (`pipeline_validation.sql`, `26/26` checks)
- Automated dashboard deployment via API
