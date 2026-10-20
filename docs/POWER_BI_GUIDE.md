# Power BI Dashboard Build Guide

## Recommended model

Import the following CSVs / tables into Power BI Desktop:

- `outputs/telematics_claims_optimized.csv` (main Claims table for descriptive and routing views)
- `data/raw/partner_garages.csv` (Garages dimension)
- `outputs/holdout_repair_cost_predictions.csv` (holdout-only Model Evaluation table)
- `reports/brand_claim_cost_summary.csv`
- `reports/monthly_claim_trends.csv`
- `reports/garage_coverage_summary.csv`
- `reports/routing_summary_by_brand.csv`

Create relationships from `Claims[Recommended_GarageID]` to `Garages[GarageID]` if you want garage details on claim pages. If your imported optimized claims file uses `Recommended_GarageID`, that field should have one recommended garage per claim in the current sample.

## Suggested report pages

### Page 1 — Executive Claims Overview
- KPI cards: claim count, total repair cost, average / median repair cost, number of distinct vehicles.
- Line chart: monthly claim count and total repair cost.
- Bar chart: total and average repair cost by vehicle brand.
- Slicers: accident date, brand, crash area, impact point.

### Page 2 — Crash Severity and Repair Cost
- Scatter plot: impact speed vs repair cost; size/color by airbag deployment or brand.
- Box/column-style view: average repair cost by speed band and impact point.
- Matrix: brand × impact-point count and average cost.
- Add a text note saying patterns come from synthetic data and are not causal conclusions.

### Page 3 — Garage Routing & Network Coverage
- KPI cards: routed claims, average recommendation distance, average estimated cycle hours, preferred-partner fallback rate.
- Bar chart: claim assignments by recommended garage.
- Matrix: vehicle brand × number of eligible in-stock garages.
- Scatter/bar view: mean route distance and turnaround by brand/area.
- Highlight fallback claims for operations review.

### Page 4 — Model Monitoring
- Use only `holdout_repair_cost_predictions.csv` for evaluation visuals.
- Compare actual vs predicted cost, show absolute error distribution and MAE by brand/speed band.
- Avoid using full-sample demo predictions to show model performance.

## Example DAX measures

```DAX
Claim Count = DISTINCTCOUNT(Claims_Optimized[ClaimID])

Distinct Vehicles = DISTINCTCOUNT(Claims_Optimized[VehicleID])

Total Repair Cost INR = SUM(Claims_Optimized[Actual_Repair_Cost_INR])

Average Repair Cost INR = AVERAGE(Claims_Optimized[Actual_Repair_Cost_INR])

Median Repair Cost INR = MEDIAN(Claims_Optimized[Actual_Repair_Cost_INR])

Average Impact Speed = AVERAGE(Claims_Optimized[Speed_At_Impact_kmh])

Airbag Deployment Rate = AVERAGE(Claims_Optimized[Airbag_Deployed])

Routed Claim Count = CALCULATE(DISTINCTCOUNT(Claims_Optimized[ClaimID]), NOT(ISBLANK(Claims_Optimized[Recommended_GarageID])))

Average Route Distance KM = AVERAGE(Claims_Optimized[Recommended_Garage_Distance_km])

Average Estimated Cycle Hours = AVERAGE(Claims_Optimized[Recommended_Garage_Est_Cycle_Hours])

Preferred Fallback Rate = AVERAGE(Claims_Optimized[Preferred_Fallback_Used])

Holdout MAE INR = AVERAGE(Holdout_Evaluation[Absolute_Error_INR])
```

## Visual QA checklist

- Confirm numbers respond correctly to slicers.
- Check brand totals against the CSV summaries.
- Use currency formatting for INR and 1–2 decimals for distance.
- Keep holdout metrics isolated from all-sample scoring output.
- Include a page footer: “Synthetic portfolio for educational demonstration; not actual insurer data or operational recommendations.”
