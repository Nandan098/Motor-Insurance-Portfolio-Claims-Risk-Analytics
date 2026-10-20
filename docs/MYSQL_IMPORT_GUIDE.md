# MySQL 8 Import and Query Guide

The complete pipeline uses SQLite so it runs locally without a server. A MySQL 8 schema and translated SQL query bank are included for practice with an enterprise database.

## Option A: SQLite (recommended first)

Run the full workflow with `python -m src.run_pipeline`. The SQLite file is created at `data/processed/auto_insurance_analytics.sqlite`. Open it with DB Browser for SQLite or use Python's sqlite3 module.

## Option B: MySQL Workbench

1. Start MySQL 8 and open MySQL Workbench.
2. Run `sql/mysql8_schema.sql` to create the `auto_insurance_analytics` schema and tables.
3. Import `data/raw/telematics_claims.csv` into `telematics_claims` and `data/raw/partner_garages.csv` into `partner_garages` using **Table Data Import Wizard**. Match CSV column names to the schema and review date/boolean type conversion.
4. After the Python pipeline runs, import `outputs/garage_routing_recommendations.csv` into `garage_routing`, and `outputs/holdout_repair_cost_predictions.csv` into `holdout_predictions`.
5. Open `sql/analytics_questions_mysql8.sql` and run individual questions to understand each output.

The SQLite query bank is the reference that was actually executed against this repository's dataset. MySQL 8 versions are generated translations; review them in Workbench, particularly date/time expressions and data-type casts, before running in a production schema.

## Schema caveat

No real claim system, insurer database, or actual garage network is included. All tables are based on synthetic records created for this project.
