"""One-command end-to-end build for data validation, ML, routing, SQL and reporting."""
from __future__ import annotations
import json
import pandas as pd
from src.config import CLAIMS_CLEAN, GARAGES_CLEAN, OUTPUTS, REPORTS
from src.data_validation import load_inputs, validate_inputs
from src.train_repair_cost_model import train_and_score
from src.garage_routing import route_all_claims
from src.build_sqlite_database import build_database
from src.run_sql_questions import run_questions
from src.insight_reports import generate_insights


def run_pipeline() -> dict:
    claims, garages = load_inputs()
    # Write canonical typed-clean copies used by downstream modules.
    CLAIMS_CLEAN.parent.mkdir(parents=True, exist_ok=True)
    claims.to_csv(CLAIMS_CLEAN, index=False, date_format="%Y-%m-%d %H:%M:%S")
    garages.to_csv(GARAGES_CLEAN, index=False)

    quality = validate_inputs(claims, garages)
    print(f"[1/7] Input validation: {quality['passed_count']}/{quality['check_count']} checks passed")

    holdout, scored, model_metrics = train_and_score()
    print(f"[2/7] Repair-cost model trained; chronological holdout R2={model_metrics['R2']:.3f}, MAE=INR {model_metrics['MAE_INR']:,.0f}")

    routing = route_all_claims(claims, garages)
    routing_path = OUTPUTS / "garage_routing_recommendations.csv"
    routing.to_csv(routing_path, index=False)
    route_cols = [c for c in routing.columns if c not in {"VehicleID", "AccidentDate", "Vehicle_Brand", "Crash_Area", "Actual_Repair_Cost_INR"}]
    optimized = scored.merge(routing[route_cols], on="ClaimID", how="left", validate="one_to_one")
    optimized.to_csv(OUTPUTS / "telematics_claims_optimized.csv", index=False)
    routing_summary = {
        "claims_routed": int(routing["Recommended_GarageID"].notna().sum()),
        "average_recommended_distance_km": round(float(routing["Recommended_Garage_Distance_km"].mean()), 3),
        "preferred_fallback_claims": int(routing["Preferred_Fallback_Used"].astype(bool).sum()),
    }
    (REPORTS / "routing_run_summary.json").write_text(json.dumps(routing_summary, indent=2), encoding="utf-8")
    print(f"[3/7] Routed {routing_summary['claims_routed']:,}/{len(claims):,} claims")

    database_path = build_database()
    print(f"[4/7] SQLite database built: {database_path}")

    query_results, sql_success = run_questions()
    print(f"[5/7] SQL business questions executed: {sql_success}/{len(query_results)}")

    insights = generate_insights()
    print("[6/7] Business-insight reports and charts generated")

    workbook_path = None
    try:
        from src.export_excel_report import build_workbook
        workbook_path = build_workbook()
        print(f"[7/7] Excel workbook exported: {workbook_path}")
    except ImportError as exc:
        # The completed workbook is included in the bundle. artifact_tool may not
        # be installed in a normal local Python environment; all CSV/SQL reports
        # remain fully reproducible without it.
        print(f"[7/7] Skipped workbook regeneration (artifact_tool unavailable): {exc}")

    summary = {
        "status": "PASS" if sql_success == len(query_results) and quality["status"] == "PASS" else "CHECK",
        "data_quality_checks_passed": quality["passed_count"],
        "data_quality_check_count": quality["check_count"],
        "sql_questions_passed": sql_success,
        "sql_questions_total": len(query_results),
        "model_metrics": model_metrics,
        "routing_summary": routing_summary,
        "database_path": database_path,
        "optimized_csv_path": str(OUTPUTS / "telematics_claims_optimized.csv"),
        "excel_workbook_path": str(workbook_path) if workbook_path else str(OUTPUTS / "telematics_claims_optimized.xlsx") + " (included prebuilt; not regenerated in this environment)",
        "notice": "All records are synthetic and generated; model metrics describe the simulated target only.",
    }
    (REPORTS / "pipeline_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if sql_success != len(query_results):
        failures = [(q["id"], q.get("error")) for q in query_results if q["status"] != "PASS"]
        raise RuntimeError(f"Some SQL questions failed: {failures}")
    print("Pipeline complete.")
    return summary


if __name__ == "__main__":
    run_pipeline()
