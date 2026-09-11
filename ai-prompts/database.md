# AI Prompts — Database (Phase 7)

**Candidate:** Nikhil Kr. Nirmal

---

## Prompt 12 — Source database schema documentation

**PROMPT SENT:**

Included in Phase 7 closure request — create `database/schema.sql`, `seed-data-notes.md`, `setup-notes.md`, and `ai-prompts/database.md` documenting the source relational model aligned to committed CSVs.

**AI RESPONSE SUMMARY:**

Created `database/` with portable PostgreSQL-compatible DDL using **VARCHAR** business keys (`CUST0001`, `PROD0001`, `OL000001`) matching Bronze STRING ingest. Documented 1,006 / 206 / 5,163 row counts, seed 42, intentional defects (including `CUST9999`/`PROD9999` orphans), and optional local load steps. Clarified that external RDBMS deployment is **not claimed** — Databricks medallion pipeline is the validated path.

**YOUR EVALUATION:**

✓ Accepted — schema aligns to committed CSVs; documentary only; no PostgreSQL load required.

**FINAL DECISION:**

Phase 7 complete. Source RDBMS schema documented; Databricks medallion pipeline remains the validated path.
