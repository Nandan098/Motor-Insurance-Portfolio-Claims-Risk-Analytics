# EXL Interview Preparation Guide — Auto Insurance Analytics

## 60-second project pitch

“I built an end-to-end synthetic auto-insurance analytics prototype. It validates telematics and garage-network tables, engineers severity features, estimates repair cost with a Random Forest regressor, and recommends an eligible garage using brand compatibility, parts availability, Haversine distance, turnaround and capacity. I evaluated the regressor with a chronological holdout and a median baseline, then loaded the source and result tables into SQLite to answer 55 business questions and prepare Power BI reporting. I documented clearly that the data and costs are synthetic, so the metrics demonstrate pipeline behavior rather than real insurer performance.”

## Questions you should be able to answer

### 1. Why did you use a chronological split?
A random split can allow records from the future into training and produce an optimistic estimate when timestamps encode operational patterns. A chronological split trains on earlier crash records and tests on later records, closer to a deployment scenario.

### 2. Why Random Forest regression?
Repair cost is nonlinear and depends on interactions among speed, G-force, airbag deployment, impact zone, vehicle make and age. Random Forest handles nonlinearities and category interactions after one-hot encoding, requires limited scaling, and provides a tree-based feature-importance ranking. It is a baseline, not necessarily the best production model.

### 3. What does MAE tell you?
Mean Absolute Error is the average absolute difference between predicted and actual costs in INR, and is interpretable in the target's units. RMSE penalizes large residuals more heavily. R² describes the fraction of test-set variance explained relative to predicting the test mean. WAPE scales total absolute error by total actual cost.

### 4. Why compare against a baseline?
A model should outperform a simple approach such as predicting the median repair cost from training data. A model with an impressive R² may still have poor business utility if it does not beat a trivial baseline or has severe segment-specific errors.

### 5. Why not use actual repair cost as a model feature?
That is the target itself. Including it in predictors would leak the answer into the model and invalidate the evaluation.

### 6. What is Haversine distance?
It calculates great-circle distance between two latitude/longitude points on a spherical Earth. It provides a geographic straight-line proxy, not road distance or live travel time.

### 7. How does your garage policy work?
First filter garages to an exact brand specialization and available parts. If an eligible preferred garage exists, rank preferred candidates; otherwise flag a fallback to any matching in-stock garage. Retain nearest eligible garage for a transparent distance baseline and score candidates on distance, turnaround and capacity.

### 8. Does the score prove cycle time is minimized?
No. The weights, assumed urban travel speed and turnaround/capacity fields are simulated assumptions. The score is a heuristic. Real optimization would need route-level traffic, garage queue, repair complexity, parts replenishment and contractual constraints.

### 9. What does feature importance mean?
It shows how the trained Random Forest used inputs to reduce prediction error in this synthetic sample. It does not prove causality and can distribute importance across correlated variables.

### 10. Is this ready for real claim settlement?
No. It is an educational prototype. Deployment would require real and governed repair invoices, data privacy controls, calibrated travel times, garage integrations, out-of-time monitoring, uncertainty estimates, human review, and testing across makes, locations and claim types.

## Interview-friendly business insight examples

Use actual figures from `reports/Business_Insights.md` and `reports/Model_Evaluation.md`; do not memorize unverified numbers. Explain one finding with four parts: observation, supporting metric, business implication, and limitation.

## Common mistakes to avoid

- Never call synthetic records actual insurer claim history.
- Never call predicted repair cost a final approved claim amount.
- Do not say distance equals travel time.
- Do not present all-sample prediction errors as holdout metrics.
- Do not say a feature causes repair cost based on correlation/feature importance.
- Do not use the model to auto-deny claims or make final coverage decisions.
