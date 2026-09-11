# AI Prompts — Dashboard (Phase 6)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 10 — Phase 6 Dashboard implementation

**PROMPT SENT:**

```text
Phase 6 — DASHBOARD only.

Read: GOLD_LAYER_NOTES.md, design-notes.md, data-model.md

Create:
- src/dashboard/dashboard_queries.sql
- src/dashboard/DASHBOARD_GUIDE.md
- ai-prompts/dashboard.md

Requirements:
- Read ONLY from Gold tables in de_c1_coding_evaluation.gold.*
- Do NOT join Bronze, Silver, quarantine, or raw CSV files
- Gold tables available:
  - gold_sales_by_product
  - gold_revenue_by_customer
  - gold_daily_weekly_trends
  - gold_customer_segmentation

Build SQL for 3 dashboard pages:
1. Executive Overview — KPIs (total revenue, order count, customer count), daily/weekly trends
2. Product Performance — top products by revenue, sales by category
3. Customer Insights — top customers by spend, customer segmentation breakdown

Include:
- At least 10-15 visualization-ready SELECT queries
- Section headers in SQL file (comment blocks per page)
- Usage guide: how to create dashboard in Databricks SQL
- Where to save screenshots: src/dashboard/screenshots/

Do NOT build validation yet.
```

**AI RESPONSE SUMMARY:**

Created Phase 6 dashboard deliverables under `src/dashboard/` plus this prompt artifact. `dashboard_queries.sql` contains 21 Gold-only `SELECT` queries across three comment-sectioned pages: Executive Overview (9 queries — KPIs, daily/weekly trends, summary table), Product Performance (6 queries — top products, category revenue/quantity), and Customer Insights (6 queries — top customers, segmentation, country breakdown). All queries use fully qualified `de_c1_coding_evaluation.gold.*` tables with no Bronze/Silver joins. `DASHBOARD_GUIDE.md` documents Databricks SQL dashboard creation, page layout, chart mapping, and screenshot path `src/dashboard/screenshots/`.

**YOUR EVALUATION:**

✓ Accepted — 21 Gold-only queries; dashboard logic validation **2/2 PASS** (2026-09-10).

**FINAL DECISION:**

Phase 6 complete. `dashboard_queries.sql` and `DASHBOARD_GUIDE.md` ready for Databricks SQL dashboard creation; screenshots optional in `src/dashboard/screenshots/`.
