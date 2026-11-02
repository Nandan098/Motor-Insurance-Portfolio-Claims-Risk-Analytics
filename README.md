# Auto Insurance Telematics & Garage Routing Optimization Engine

## 1. Business problem

Auto insurers need to estimate repair severity early and route vehicles to suitable repair partners. This project demonstrates two connected decision-support capabilities:

1. **Repair-cost prediction:** estimate a repair cost from simulated crash severity, vehicle make/age, impact point and incident context.
2. **Garage recommendation:** find brand-compatible garages with relevant parts in stock, calculate geographic distance, and rank eligible locations by a transparent heuristic involving distance, turnaround time and service capacity.

This is an analytics prototype, not a live claims-settlement or dispatch system.

## 2. What is included

- 3,000 telematics claim records and 100 partner garage records, plus the reproducible synthetic dataset generator.
- Reusable Python modules for data checks, feature engineering, chronological model evaluation, Haversine distance, garage routing, SQLite creation, SQL-answer generation and reporting.
- A Random Forest regression model and metrics: MAE, RMSE, R², WAPE, plus a simple median baseline.
- A chronological holdout file that is separate from the all-sample demonstration-scoring export.
- **55 SQL business questions**, query answers, and a CSV output for each question.
- SQLite database for immediate local querying and a MySQL 8 schema/query file for additional SQL practice.
- Business-insights report, model report, charts, Power BI build guide, DAX examples, tests, interview guide and Excel deliverable.

## 3. Folder structure

```text
EXL_Auto_Insurance_Telematics_Optimization_Project/
├── data/
│   ├── raw/                         # Source synthetic CSVs
│   ├── processed/                   # Canonical validated copies + SQLite DB
│   └── auto_insurance_telematics_dataset.xlsx
├── src/
│   ├── generate_dataset.py           # Rebuild source data using fixed seed
│   ├── data_validation.py            # Schema and quality checks
│   ├── feature_engineering.py        # Leakage-aware feature creation
│   ├── train_repair_cost_model.py    # Chronological holdout + final demo model
│   ├── garage_routing.py             # Haversine and eligible-garage ranking
│   ├── build_sqlite_database.py      # Materialize tables in SQLite
│   ├── sql_catalog.py                # 55 documented SQL questions
│   ├── run_sql_questions.py          # Execute queries and export result tables
│   ├── insight_reports.py            # Business insight summaries and charts
│   ├── export_excel_report.py        # Excel report built with artifact_tool
│   └── run_pipeline.py               # End-to-end orchestration
├── sql/                              # SQLite query bank + MySQL 8 schema and query bank
├── tests/                            # Unit and data-invariant tests
├── models/                            # Final model artifact
├── outputs/                           # Predictions, garage routes, combined CSV and Excel
├── reports/                           # Evaluations, SQL results, insights and run manifests
├── visuals/                           # Data and model charts
├── docs/                               # Data dictionary, architecture, Power BI and interview guides
└── requirements.txt
```

## 4. Setup

Use Python 3.10+ (Python 3.11 is a sensible default). From the project root:

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Run the complete pipeline

From the project root, run:

```bash
python -m src.run_pipeline
```

The pipeline will:

1. Load and validate both source CSV files.
2. Save clean typed copies under `data/processed/`.
3. Train the Random Forest regressor, using an 80/20 **chronological holdout**.
4. Save test-set predictions and metrics that were not trained on those test rows.
5. Fit a final demonstration model on all 3,000 records and generate an all-row scored CSV. Those all-row predictions are in-sample and **must not be used for reported model metrics**.
6. Route each claim to an eligible garage and export the routing details.
7. Create a local SQLite database containing claims, garages, routing, holdout predictions and all-row demo scores.
8. Execute the 55 SQL questions and export separate result CSVs.
9. Write insights, metrics, charts and the Excel reporting workbook.

The workbook in `outputs/telematics_claims_optimized.xlsx` is included as a completed deliverable. Re-generating the workbook uses OpenAI's `artifact_tool` workbook package in the creation environment; if it is unavailable in another local Python environment, all CSV, SQLite and Markdown outputs can still be regenerated, and the shipped workbook remains available.

## 6. Run unit tests

```bash
pytest -q
```

## 7. Key output files

| File | Purpose |
|---|---|
| `outputs/telematics_claims_optimized.xlsx` | Executive report and claims/routing/reporting tabs |
| `outputs/telematics_claims_optimized.csv` | Combined all-claim cost prediction demo + garage recommendation |
| `outputs/garage_routing_recommendations.csv` | One route recommendation per claim, eligibility policy and distance/cycle estimates |
| `outputs/holdout_repair_cost_predictions.csv` | Honest later-period test predictions and residuals |
| `outputs/claims_cost_scored_demo.csv` | Prediction from a model fitted on all sample records; illustrative only |
| `reports/model_evaluation.json` | Chronological holdout metrics and baseline comparison |
| `reports/Business_Insights.md` | Numeric observations and action ideas, with simulation caveats |
| `reports/SQL_Questions_and_Answers.md` | All 55 questions, executed SQL and result previews |
| `reports/sql_results/` | One CSV of executed results per query |
| `data/processed/auto_insurance_analytics.sqlite` | Local SQL database |
| `models/repair_cost_random_forest.joblib` | Final all-data model artifact for demonstration scoring |

## 8. SQL practice

- Query bank: `sql/analytics_questions_sqlite.sql` (executed against the included SQLite DB).
- MySQL 8 schema: `sql/mysql8_schema.sql`.
- MySQL 8 query bank: `sql/analytics_questions_mysql8.sql`.
- Import guidance: `docs/MYSQL_IMPORT_GUIDE.md`.
- Answer guide: `reports/SQL_Questions_and_Answers.md`.

Start by opening the SQLite file with DB Browser for SQLite, or use the Python `sqlite3` module. Questions cover claims mix, repair-cost severity, temporal patterns, vehicle repeats, cost outliers, parts/garage coverage, routing distance, model error, and network-capacity prioritization.

## 9. Garage-routing policy

- Candidate eligibility: `Brand_Specialization` matches the vehicle brand and `Parts_Available = true`.
- Preferred policy: if any eligible preferred garage exists, score only those. If none exists, fallback to any brand-compatible in-stock garage and flag the fallback.
- Haversine distance is the great-circle distance from crash coordinates to garage coordinates.
- Approximate driving minutes use an explicit 25 km/h urban average speed assumption; this is **not live traffic or road distance**.
- Balanced recommendation score: normalized distance (60%) + normalized turnaround days (30%) + inverse normalized capacity (10%). Lower is better. The nearest eligible garage is also retained to compare distance-only and balanced routing.

## 10. Main model decisions

- Target: `Actual_Repair_Cost_INR`.
- Predictors: impact speed, G-force, airbag status, braking duration, model year / calculated vehicle age, accident hour/weekday/month, make, impact point, weather, road type and area.
- Target is never included in features.
- Training sample: earliest 80% of sorted records; test sample: latest 20% chronologically.
- Evaluation: MAE, RMSE, R² and WAPE; baseline: training-period median cost.
- Feature importance is descriptive, not causal.

## 11. Interpretation and ethical use

- Data is synthetic. It is intended to showcase analytical workflows and should be labeled that way in a resume or interview.
- Target cost is simulated from known severity-related factors. Good evaluation scores are expected to reflect the generated formula, not real-world insurer generalization.
- Garage coordinates, parts status, partner status, capacity and turnaround time are simulated. No route output should be used to dispatch a real vehicle.
- Model estimates should support human review, not automatically approve, deny, or settle insurance claims.
- A real deployment would require governed real claim invoices, calibration, uncertainty and fairness tests, data-privacy controls, actual traffic/repair-time data, business rules, and ongoing monitoring.

## 12. Suggested build order for learning

1. Review `docs/DATA_DICTIONARY.md` and `src/data_validation.py`.
2. Run the pipeline once and open `reports/data_quality_report.json`.
3. Read `reports/SQL_Questions_and_Answers.md`; run Q01–Q10 yourself.
4. Study `src/feature_engineering.py` and `src/train_repair_cost_model.py`.
5. Compare model metrics with the median baseline in `reports/Model_Evaluation.md`.
6. Walk through `src/garage_routing.py` and manually recompute one Haversine distance.
7. Review the business insights and then build the report pages using `docs/POWER_BI_GUIDE.md`.
8. Prepare an interview explanation from `docs/INTERVIEW_GUIDE.md`.
