"""Generate business-oriented insight reports and exploratory charts."""
from __future__ import annotations
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.config import DATA_PROCESSED, OUTPUTS, REPORTS, VISUALS


def generate_insights() -> dict:
    claims = pd.read_csv(DATA_PROCESSED / "telematics_claims_clean.csv", parse_dates=["AccidentDate"])
    garages = pd.read_csv(DATA_PROCESSED / "partner_garages_clean.csv")
    routing = pd.read_csv(OUTPUTS / "garage_routing_recommendations.csv")
    holdout = pd.read_csv(OUTPUTS / "holdout_repair_cost_predictions.csv")
    metrics = json.loads((REPORTS / "model_evaluation.json").read_text(encoding="utf-8"))

    brand_summary = claims.groupby("Vehicle_Brand", as_index=False).agg(
        Claim_Count=("ClaimID", "count"),
        Average_Repair_Cost_INR=("Actual_Repair_Cost_INR", "mean"),
        Total_Repair_Cost_INR=("Actual_Repair_Cost_INR", "sum"),
        Average_Impact_Speed_kmh=("Speed_At_Impact_kmh", "mean"),
        Airbag_Rate=("Airbag_Deployed", "mean"),
    ).sort_values("Average_Repair_Cost_INR", ascending=False)
    brand_summary.to_csv(REPORTS / "brand_claim_cost_summary.csv", index=False)

    monthly = claims.assign(AccidentMonth=claims["AccidentDate"].dt.to_period("M").astype(str)).groupby("AccidentMonth", as_index=False).agg(
        Claim_Count=("ClaimID", "count"), Total_Repair_Cost_INR=("Actual_Repair_Cost_INR", "sum"),
        Average_Repair_Cost_INR=("Actual_Repair_Cost_INR", "mean"))
    monthly.to_csv(REPORTS / "monthly_claim_trends.csv", index=False)

    speed_band = pd.cut(
        claims["Speed_At_Impact_kmh"], bins=[-0.01, 25, 50, 80, np.inf],
        labels=["Low (<25)", "Moderate (25-49)", "High (50-79)", "Very high (80+)"], right=False,
    )
    speed_summary = claims.assign(Speed_Band=speed_band).groupby("Speed_Band", observed=False).agg(
        Claim_Count=("ClaimID", "count"), Average_Repair_Cost_INR=("Actual_Repair_Cost_INR", "mean"),
        Average_G_Force=("G_Force_Impact", "mean"), Airbag_Rate=("Airbag_Deployed", "mean"),
    ).reset_index()
    speed_summary.to_csv(REPORTS / "speed_severity_summary.csv", index=False)

    garage_summary = garages.groupby("Brand_Specialization", as_index=False).agg(
        Garage_Count=("GarageID", "count"),
        In_Stock_Garages=("Parts_Available", "sum"),
        Preferred_Garages=("Preferred_Partner", "sum"),
        Preferred_In_Stock_Garages=("Preferred_Partner", lambda s: int((s & garages.loc[s.index, "Parts_Available"]).sum())),
        Average_Turnaround_Days=("Avg_Repair_Turnaround_Days", "mean"),
    )
    demand = claims.groupby("Vehicle_Brand").size().rename("Claim_Count")
    garage_summary = garage_summary.join(demand, on="Brand_Specialization")
    garage_summary["Claims_Per_In_Stock_Garage"] = garage_summary["Claim_Count"] / garage_summary["In_Stock_Garages"].replace(0, np.nan)
    garage_summary.to_csv(REPORTS / "garage_coverage_summary.csv", index=False)

    routing_summary = routing.groupby("Vehicle_Brand", as_index=False).agg(
        Routed_Claims=("ClaimID", "count"), Average_Distance_km=("Recommended_Garage_Distance_km", "mean"),
        Average_Travel_Minutes=("Recommended_Garage_Travel_Minutes", "mean"),
        Average_Turnaround_Days=("Recommended_Garage_Turnaround_Days", "mean"),
        Average_Estimated_Cycle_Hours=("Recommended_Garage_Est_Cycle_Hours", "mean"),
        Preferred_Fallback_Rate=("Preferred_Fallback_Used", "mean"),
    )
    routing_summary.to_csv(REPORTS / "routing_summary_by_brand.csv", index=False)

    airbag = claims.groupby("Airbag_Deployed")["Actual_Repair_Cost_INR"].mean().to_dict()
    corr_speed_cost = float(claims["Speed_At_Impact_kmh"].corr(claims["Actual_Repair_Cost_INR"]))
    corr_g_cost = float(claims["G_Force_Impact"].corr(claims["Actual_Repair_Cost_INR"]))
    total_cost = float(claims["Actual_Repair_Cost_INR"].sum())
    top_brand = brand_summary.iloc[0]
    bottom_brand = brand_summary.iloc[-1]
    preferred_fallback_count = int(routing["Preferred_Fallback_Used"].astype(bool).sum())
    report = {
        "data_status": "Synthetic, realistic-style demonstration data. No values describe real customers, garages, routes, costs, or insurer operations.",
        "claim_count": int(len(claims)),
        "garage_count": int(len(garages)),
        "unique_vehicles": int(claims["VehicleID"].nunique()),
        "date_min": str(claims["AccidentDate"].min()),
        "date_max": str(claims["AccidentDate"].max()),
        "total_simulated_repair_cost_inr": round(total_cost, 2),
        "average_simulated_repair_cost_inr": round(float(claims["Actual_Repair_Cost_INR"].mean()), 2),
        "median_simulated_repair_cost_inr": round(float(claims["Actual_Repair_Cost_INR"].median()), 2),
        "p95_simulated_repair_cost_inr": round(float(claims["Actual_Repair_Cost_INR"].quantile(0.95)), 2),
        "speed_repair_cost_pearson_correlation": round(corr_speed_cost, 4),
        "gforce_repair_cost_pearson_correlation": round(corr_g_cost, 4),
        "mean_cost_airbag_deployed_inr": round(float(airbag.get(1, np.nan)), 2),
        "mean_cost_no_airbag_inr": round(float(airbag.get(0, np.nan)), 2),
        "highest_average_cost_brand_in_sample": str(top_brand["Vehicle_Brand"]),
        "highest_average_cost_brand_mean_inr": round(float(top_brand["Average_Repair_Cost_INR"]), 2),
        "lowest_average_cost_brand_in_sample": str(bottom_brand["Vehicle_Brand"]),
        "lowest_average_cost_brand_mean_inr": round(float(bottom_brand["Average_Repair_Cost_INR"]), 2),
        "claims_with_routing_recommendation": int(routing["Recommended_GarageID"].notna().sum()),
        "average_recommended_distance_km": round(float(routing["Recommended_Garage_Distance_km"].mean()), 3),
        "average_estimated_cycle_hours": round(float(routing["Recommended_Garage_Est_Cycle_Hours"].mean()), 2),
        "preferred_partner_fallback_claims": preferred_fallback_count,
        "preferred_partner_fallback_rate_pct": round(100 * preferred_fallback_count / max(len(routing), 1), 2),
        "holdout_metrics": metrics,
    }
    (REPORTS / "business_insights.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    model_report_lines = [
        "# Repair-Cost Model Evaluation", "",
        "> **Synthetic-data warning:** The target is generated by a simulation formula. These metrics demonstrate pipeline behavior on generated data; they are not evidence of real-world insurer performance.", "",
        "## Evaluation design", "",
        f"- Model: **{metrics['model']}**.",
        f"- Target: `{metrics['target']}`.",
        f"- Training rows: **{metrics['training_rows']:,}**, from {metrics['training_start']} through {metrics['training_end']}.",
        f"- Chronological holdout rows: **{metrics['holdout_rows']:,}**, from {metrics['holdout_start']} through {metrics['holdout_end']}.",
        "- Predictors exclude the target column. The final all-sample demo scores are not used for holdout metrics.",
        "", "## Holdout metrics", "",
        "| Metric | Result | Interpretation |",
        "|---|---:|---|",
        f"| MAE | ₹{metrics['MAE_INR']:,.2f} | Average absolute prediction error in INR |",
        f"| RMSE | ₹{metrics['RMSE_INR']:,.2f} | Penalizes larger residuals more than MAE |",
        f"| R² | {metrics['R2']:.4f} | Variance explained relative to a test-mean baseline |",
        f"| WAPE | {metrics['WAPE_PERCENT']:.2f}% | Sum of absolute error divided by sum of actual costs |",
        f"| Median baseline MAE | ₹{metrics['Baseline_Median_MAE_INR']:,.2f} | Baseline always predicts training-period median |",
        f"| Median baseline RMSE | ₹{metrics['Baseline_Median_RMSE_INR']:,.2f} | Baseline RMSE |",
        "", f"Model MAE beats the median baseline: **{metrics['holdout_beats_baseline_on_MAE']}**.",
        "", "## Feature-importance interpretation", "",
        "See `feature_importance.csv` for the Random Forest importance ranking. Importance is predictive association within the synthetic sample, not causality. Correlated inputs may share or redistribute importance.",
        "", "## Caveats and next steps", "",
        "1. The target generation formula uses impact speed, G-force, airbag status, impact point, vehicle make/age and incident context; this makes those relationships learnable by design.",
        "2. Holdout is chronological, which is more deployment-like than a random split, but the entire dataset still comes from one fixed simulator.",
        "3. Real insurer use would require claim invoices, robust external validation, uncertainty estimates, segment monitoring, human review and governance.",
        "4. Do not use all-sample predictions from `claims_cost_scored_demo.csv` to calculate model evaluation metrics; that model was fitted on those rows.",
    ]
    (REPORTS / "Model_Evaluation.md").write_text("\n".join(model_report_lines) + "\n", encoding="utf-8")

    # Charts use default Matplotlib styling and explicitly identify the data as simulated.
    VISUALS.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.hist(claims["Actual_Repair_Cost_INR"], bins=45)
    plt.xlabel("Simulated repair cost (INR)")
    plt.ylabel("Claim count")
    plt.title("Simulated repair-cost distribution (synthetic data)")
    plt.tight_layout()
    plt.savefig(VISUALS / "repair_cost_distribution.png", dpi=150)
    plt.close()

    plot_brand = brand_summary.sort_values("Average_Repair_Cost_INR", ascending=True)
    plt.figure(figsize=(10, 6))
    plt.barh(plot_brand["Vehicle_Brand"], plot_brand["Average_Repair_Cost_INR"])
    plt.xlabel("Average simulated repair cost (INR)")
    plt.title("Average repair cost by vehicle make (synthetic data)")
    plt.tight_layout()
    plt.savefig(VISUALS / "average_cost_by_brand.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(monthly["AccidentMonth"], monthly["Claim_Count"], marker="o", markersize=2)
    plt.xlabel("Accident month")
    plt.ylabel("Claim count")
    plt.title("Monthly claim frequency (synthetic data)")
    plt.xticks(rotation=75)
    plt.tight_layout()
    plt.savefig(VISUALS / "monthly_claim_frequency.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(speed_summary["Speed_Band"].astype(str), speed_summary["Average_Repair_Cost_INR"])
    plt.xlabel("Impact speed band (km/h)")
    plt.ylabel("Average simulated repair cost (INR)")
    plt.title("Average cost by impact speed (synthetic data)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(VISUALS / "cost_by_speed_band.png", dpi=150)
    plt.close()

    # Human-readable business interpretation with measured values.
    def inr(value: float) -> str:
        return f"₹{value:,.0f}"
    lines = [
        "# Business Insights and Recommendations", "",
        "> **Data caveat:** All claims, costs, telematics and garage values are synthetic. The observations below demonstrate how to interpret analytics and must not be described as real insurer findings.", "",
        "## Portfolio overview", "",
        f"- The dataset contains **{len(claims):,} claims** and **{claims['VehicleID'].nunique():,} distinct vehicle identifiers**, spanning {claims['AccidentDate'].min().date()} to {claims['AccidentDate'].max().date()}.",
        f"- Total simulated repair spend is **{inr(total_cost)}**; the mean is **{inr(claims['Actual_Repair_Cost_INR'].mean())}**, while the median is **{inr(claims['Actual_Repair_Cost_INR'].median())}**.",
        f"- The 95th percentile simulated claim cost is **{inr(claims['Actual_Repair_Cost_INR'].quantile(.95))}**, indicating that upper-tail claims deserve separate severity reporting.",
        "", "## Severity and cost drivers", "",
        f"- Pearson correlation between impact speed and simulated repair cost is **{corr_speed_cost:.3f}**; between G-force and cost it is **{corr_g_cost:.3f}**. Correlation is descriptive and is not evidence of causation.",
        f"- Average cost with airbag deployment is **{inr(airbag.get(1, np.nan))}**, versus **{inr(airbag.get(0, np.nan))}** without deployment. Airbag deployment is a severity marker in this simulation, not an independent causal factor.",
        f"- {top_brand['Vehicle_Brand']} has the highest average repair cost in this generated sample ({inr(top_brand['Average_Repair_Cost_INR'])}); {bottom_brand['Vehicle_Brand']} has the lowest ({inr(bottom_brand['Average_Repair_Cost_INR'])}). Make mix and generated cost multipliers contribute to this pattern.",
        "", "## Garage routing", "",
        f"- A garage recommendation was generated for **{routing['Recommended_GarageID'].notna().sum():,} of {len(routing):,} claims** using brand compatibility and in-stock parts constraints.",
        f"- Mean recommended garage distance is **{routing['Recommended_Garage_Distance_km'].mean():.2f} km**. Mean estimated travel plus turnaround cycle is **{routing['Recommended_Garage_Est_Cycle_Hours'].mean():.1f} hours**; travel-time and cycle assumptions are synthetic.",
        f"- **{preferred_fallback_count:,} claims ({100*preferred_fallback_count/len(routing):.1f}%)** used a fallback because the brand had no eligible preferred partner with parts in stock. Consider increasing stock at preferred garages for these brands.",
        "- The routing score is a heuristic: normalized distance (60%), turnaround days (30%), and capacity preference (10%). It is not an optimization proven to minimize real-world settlement time.",
        "", "## Predictive model", "",
        f"- The Random Forest was evaluated on a **chronological holdout**: {metrics['training_rows']:,} earlier claims for training and {metrics['holdout_rows']:,} later claims for testing.",
        f"- Holdout MAE: **{inr(metrics['MAE_INR'])}**; RMSE: **{inr(metrics['RMSE_INR'])}**; R²: **{metrics['R2']:.3f}**; WAPE: **{metrics['WAPE_PERCENT']:.1f}%**.",
        f"- Median baseline MAE: **{inr(metrics['Baseline_Median_MAE_INR'])}**. Model MAE beats this simple baseline: **{metrics['holdout_beats_baseline_on_MAE']}**.",
        "- Because the target is created by a simulation formula using severity-related factors, good scores demonstrate learning the generated pattern, not production-ready insurance cost prediction.",
        "", "## Recommended business actions (demonstration) ", "",
        "1. **Claims triage:** show predicted cost with an uncertainty/error context and route high-severity cases to human review; do not automate coverage or claim denials.",
        "2. **Network planning:** compare claims per eligible in-stock garage by brand, then test additional preferred-partner stock or capacity in constrained segments.",
        "3. **Routing policy test:** compare nearest-eligible and balanced-score policies on distance and estimated cycle-time assumptions before choosing operational weights.",
        "4. **Model governance:** monitor error by brand and severity, compare against a baseline, and retrain only with appropriately governed real claim data in a real deployment.",
    ]
    (REPORTS / "Business_Insights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
