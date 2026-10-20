"""Input loading and repeatable quality checks for the two source tables."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from src.config import CLAIMS_RAW, GARAGES_RAW, REPORTS

CLAIM_REQUIRED = {
    "ClaimID", "AccidentDate", "VehicleID", "Vehicle_Brand", "Model_Year",
    "Speed_At_Impact_kmh", "G_Force_Impact", "Airbag_Deployed",
    "Braking_Duration_Seconds", "Impact_Point", "Weather_Condition", "Road_Type",
    "Crash_Area", "Vehicle_Latitude", "Vehicle_Longitude", "Actual_Repair_Cost_INR",
}
GARAGE_REQUIRED = {
    "GarageID", "Garage_Name", "Area", "Latitude", "Longitude",
    "Brand_Specialization", "Parts_Available", "Preferred_Partner",
    "Daily_Service_Capacity", "Avg_Repair_Turnaround_Days", "Labor_Rate_INR_Per_Hour",
}


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load claims and garage CSVs and standardize key data types."""
    if not CLAIMS_RAW.exists() or not GARAGES_RAW.exists():
        raise FileNotFoundError(
            "Source CSVs not found. Expected data/raw/telematics_claims.csv and "
            "data/raw/partner_garages.csv."
        )
    claims = pd.read_csv(CLAIMS_RAW)
    garages = pd.read_csv(GARAGES_RAW)
    missing_claim = CLAIM_REQUIRED - set(claims.columns)
    missing_garage = GARAGE_REQUIRED - set(garages.columns)
    if missing_claim:
        raise ValueError(f"Claims file is missing columns: {sorted(missing_claim)}")
    if missing_garage:
        raise ValueError(f"Garage file is missing columns: {sorted(missing_garage)}")

    claims["AccidentDate"] = pd.to_datetime(claims["AccidentDate"], errors="coerce")
    numeric_claim_cols = [
        "Model_Year", "Speed_At_Impact_kmh", "G_Force_Impact", "Airbag_Deployed",
        "Braking_Duration_Seconds", "Vehicle_Latitude", "Vehicle_Longitude",
        "Actual_Repair_Cost_INR",
    ]
    for col in numeric_claim_cols:
        claims[col] = pd.to_numeric(claims[col], errors="coerce")
    for col in ["Latitude", "Longitude", "Daily_Service_Capacity",
                "Avg_Repair_Turnaround_Days", "Labor_Rate_INR_Per_Hour"]:
        garages[col] = pd.to_numeric(garages[col], errors="coerce")
    for col in ["Parts_Available", "Preferred_Partner"]:
        if garages[col].dtype != bool:
            normalized = garages[col].astype(str).str.strip().str.lower()
            garages[col] = normalized.isin(["true", "1", "yes", "y"])
    return claims, garages


def validate_inputs(claims: pd.DataFrame, garages: pd.DataFrame) -> dict:
    """Run checks without silently dropping source rows."""
    checks = {}
    checks["claims_rows_3000"] = len(claims) == 3000
    checks["garages_rows_100"] = len(garages) == 100
    checks["claim_ids_unique"] = claims["ClaimID"].is_unique
    checks["garage_ids_unique"] = garages["GarageID"].is_unique
    checks["required_claim_fields_non_null"] = bool(
        claims[list(CLAIM_REQUIRED)].notna().all().all()
    )
    checks["repair_costs_positive"] = bool((claims["Actual_Repair_Cost_INR"] > 0).all())
    checks["speeds_nonnegative"] = bool((claims["Speed_At_Impact_kmh"] >= 0).all())
    checks["g_force_positive"] = bool((claims["G_Force_Impact"] > 0).all())
    checks["claim_coordinates_in_valid_range"] = bool(
        claims["Vehicle_Latitude"].between(-90, 90).all()
        and claims["Vehicle_Longitude"].between(-180, 180).all()
    )
    checks["garage_coordinates_in_valid_range"] = bool(
        garages["Latitude"].between(-90, 90).all()
        and garages["Longitude"].between(-180, 180).all()
    )
    checks["garage_capacity_positive"] = bool((garages["Daily_Service_Capacity"] > 0).all())
    brands = set(claims["Vehicle_Brand"].str.casefold())
    garage_brands = set(garages["Brand_Specialization"].str.casefold())
    checks["all_claim_brands_have_garage_specialization"] = brands.issubset(garage_brands)
    eligible_brands = set(
        garages.loc[garages["Parts_Available"], "Brand_Specialization"].str.casefold()
    )
    checks["all_claim_brands_have_in_stock_garage"] = brands.issubset(eligible_brands)
    checks["accident_dates_parse"] = bool(claims["AccidentDate"].notna().all())
    checks["vehicle_model_year_not_after_accident_year"] = bool(
        (claims["Model_Year"] <= claims["AccidentDate"].dt.year).all()
    )
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "claims_rows": int(len(claims)),
        "garage_rows": int(len(garages)),
        "claims_duplicate_id_count": int(claims["ClaimID"].duplicated().sum()),
        "garages_duplicate_id_count": int(garages["GarageID"].duplicated().sum()),
        "claims_missing_cell_count": int(claims.isna().sum().sum()),
        "garages_missing_cell_count": int(garages.isna().sum().sum()),
        "checks": checks,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "data_quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not all(checks.values()):
        raise ValueError(f"Dataset validation failed: {report['failed_checks']}")
    return report
