# Requirements Analysis

**Candidate:** Nikhil Kr. Nirmal | **Assessment:** 09/09/2026 – 10/09/2026

## Problem Statement

Build an e-commerce sales analytics pipeline on Databricks using the **medallion architecture**. Ingest sample data for **customers**, **orders**, and **products**, land in Bronze, cleanse and validate in Silver, aggregate in Gold, and expose for dashboard analytics.

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Medallion flow: Raw → Bronze → Silver → Gold → Dashboard |
| FR-02 | Generate sample CSVs in `data/` |
| FR-03 | Bronze: per-entity ingestion, minimal transformation |
| FR-04 | Silver: 5 DQ categories + quarantine + DQ summary |
| FR-05 | Gold: 4 analytical tables |
| FR-06 | Dashboard: SQL queries over Gold only |
| FR-07 | Validation: end-to-end checks on Databricks |
| FR-08 | Document AI prompts in `ai-prompts/` per phase |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Unity Catalog: `de_c1_coding_evaluation` |
| NFR-02 | Delta Lake table format |
| NFR-03 | No hardcoded secrets |
| NFR-04 | Reproducible data (seed 42) |
| NFR-05 | Incremental phase delivery |

## Phase Deliverables

| Phase | Deliverables | Status |
|-------|--------------|--------|
| 1 Foundation | Docs (this file + design, model, DQ, workflow) | **Complete** |
| 2 Data generation | `generate_sample_data.py`, `data/*.csv` | **Complete** |
| 3 Bronze | Ingest scripts, `ingest_all.py` | **Complete** |
| 4 Silver | 5 DQ modules + orchestration | **Complete** |
| 5 Gold | 4 SQL files + orchestrator | **Complete** |
| 6 Dashboard | `dashboard_queries.sql`, guide | **Complete** |
| 7 Validation | `pipeline_validation.sql`, report, closure docs | **Complete** (26/26 PASS on Databricks — 10/09/2026) |

## Assumptions

- Sample data is generated locally, not from production
- Order grain = **line item** (one row per product line in an order)
- Single currency, batch processing
- Developer reviews all AI-generated code before acceptance
