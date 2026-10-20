# System Architecture

## Objective
Demonstrate a complete insurance analytics workflow that estimates crash repair costs, recommends a brand-compatible garage with relevant parts in stock, and exports reporting outputs. All source records are synthetic and realistic-style; the project is a learning prototype, not a production claims system.

## Components

1. **Input layer** — `data/raw/telematics_claims.csv` (3,000 synthetic claims) and `data/raw/partner_garages.csv` (100 synthetic garages).
2. **Validation layer** — `src/data_validation.py` checks schemas, required fields, keys, numerical ranges, dates, and whether each vehicle brand has in-stock garage coverage.
3. **Feature layer** — `src/feature_engineering.py` derives vehicle age, time features, and an explainable severity index. The target variable is never used as an input feature.
4. **Prediction layer** — `src/train_repair_cost_model.py` trains a Random Forest regression pipeline. Evaluation uses an 80/20 chronological holdout so later-dated claims do not train the reported evaluation model.
5. **Routing layer** — `src/garage_routing.py` uses Haversine distance and filters eligible garages by vehicle brand and parts availability. It prioritizes eligible preferred partners when present and falls back to any compatible in-stock partner if necessary.
6. **Analytics layer** — SQLite holds claims, garage, routing, scored-claims, and holdout-prediction tables. 55 SQL questions generate reproducible CSV answer tables.
7. **Reporting layer** — business insight reports, PNG charts, an Excel workbook and Power BI dashboard guidance.

## Data flow

```text
Raw synthetic CSVs
   -> schema / data-quality validation
   -> engineered features
   -> chronological train/test split
   -> Random Forest regression evaluation
   -> full-sample model for illustrative all-row scoring
   -> garage routing (brand + stock + partner + distance / turnaround / capacity)
   -> CSV exports + SQLite
   -> 55 SQL query result tables
   -> business insights + Excel / Power BI
```

## Routing logic

1. Normalize make names and filter garages to matching `Brand_Specialization` and `Parts_Available = true`.
2. If any of these are preferred partners, the policy score only considers those preferred candidates. Otherwise, it falls back to all brand-compatible in-stock garages and flags `Preferred_Fallback_Used`.
3. Compute Haversine distance in km, then estimated travel minutes using an explicit average urban speed assumption (25 km/h).
4. Compute a demonstrative routing score from normalized candidate values: distance 60%, turnaround duration 30%, and capacity preference 10%. Lowest score becomes the balanced recommendation. `Nearest_Eligible_GarageID` is retained for comparison.

The weights and assumed travel speed are prototypes. They have not been calibrated to real traffic, repair queue data, contractual rules, or measured cycle times.

## Modeling governance

- Target: `Actual_Repair_Cost_INR`.
- Features: impact speed, G-force, airbag status, braking, age, time and categorical accident context / vehicle make.
- Holdout: chronological final 20% of records.
- Reported metrics: MAE, RMSE, R², WAPE and a training-period median baseline.
- The separate `claims_cost_scored_demo.csv` uses a model fitted on all sample rows, so its predictions are in-sample; do not calculate test metrics from that output.
- Strong model scores only show that a model learned the simulation-generated target relationship. No real insurance accuracy or savings are established.
