# Business Insights and Recommendations

> **Data caveat:** All claims, costs, telematics and garage values are synthetic. The observations below demonstrate how to interpret analytics and must not be described as real insurer findings.

## Portfolio overview

- The dataset contains **3,000 claims** and **2,885 distinct vehicle identifiers**, spanning 2023-01-03 to 2025-12-31.
- Total simulated repair spend is **₹53,783,500**; the mean is **₹17,928**, while the median is **₹7,600**.
- The 95th percentile simulated claim cost is **₹63,410**, indicating that upper-tail claims deserve separate severity reporting.

## Severity and cost drivers

- Pearson correlation between impact speed and simulated repair cost is **0.788**; between G-force and cost it is **0.799**. Correlation is descriptive and is not evidence of causation.
- Average cost with airbag deployment is **₹85,045**, versus **₹13,846** without deployment. Airbag deployment is a severity marker in this simulation, not an independent causal factor.
- Mercedes-Benz has the highest average repair cost in this generated sample (₹54,350); Maruti Suzuki has the lowest (₹13,943). Make mix and generated cost multipliers contribute to this pattern.

## Garage routing

- A garage recommendation was generated for **3,000 of 3,000 claims** using brand compatibility and in-stock parts constraints.
- Mean recommended garage distance is **7.09 km**. Mean estimated travel plus turnaround cycle is **51.9 hours**; travel-time and cycle assumptions are synthetic.
- **35 claims (1.2%)** used a fallback because the brand had no eligible preferred partner with parts in stock. Consider increasing stock at preferred garages for these brands.
- The routing score is a heuristic: normalized distance (60%), turnaround days (30%), and capacity preference (10%). It is not an optimization proven to minimize real-world settlement time.

## Predictive model

- The Random Forest was evaluated on a **chronological holdout**: 2,400 earlier claims for training and 600 later claims for testing.
- Holdout MAE: **₹4,517**; RMSE: **₹9,065**; R²: **0.769**; WAPE: **30.6%**.
- Median baseline MAE: **₹10,653**. Model MAE beats this simple baseline: **True**.
- Because the target is created by a simulation formula using severity-related factors, good scores demonstrate learning the generated pattern, not production-ready insurance cost prediction.

## Recommended business actions (demonstration) 

1. **Claims triage:** show predicted cost with an uncertainty/error context and route high-severity cases to human review; do not automate coverage or claim denials.
2. **Network planning:** compare claims per eligible in-stock garage by brand, then test additional preferred-partner stock or capacity in constrained segments.
3. **Routing policy test:** compare nearest-eligible and balanced-score policies on distance and estimated cycle-time assumptions before choosing operational weights.
4. **Model governance:** monitor error by brand and severity, compare against a baseline, and retrain only with appropriately governed real claim data in a real deployment.
