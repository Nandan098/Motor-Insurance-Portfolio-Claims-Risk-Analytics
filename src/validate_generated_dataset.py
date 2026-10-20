"""Validate the generated auto-insurance dataset before modeling."""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
claims = pd.read_csv(ROOT / "data/raw/telematics_claims.csv", parse_dates=["AccidentDate"])
garages = pd.read_csv(ROOT / "data/raw/partner_garages.csv")

checks = {
    "exactly_3000_claims": len(claims) == 3000,
    "exactly_100_garages": len(garages) == 100,
    "claim_ids_unique": claims["ClaimID"].is_unique,
    "no_null_claim_values": not claims.isna().any().any(),
    "no_null_garage_values": not garages.isna().any().any(),
    "claim_cost_positive": (claims["Actual_Repair_Cost_INR"] > 0).all(),
    "speed_in_expected_range": claims["Speed_At_Impact_kmh"].between(0, 143).all(),
    "gforce_positive": (claims["G_Force_Impact"] > 0).all(),
    "incident_years_2023_to_2025": claims["AccidentDate"].dt.year.between(2023, 2025).all(),
    "garage_coordinates_valid": garages["Latitude"].between(-90, 90).all() and garages["Longitude"].between(-180, 180).all(),
    "each_brand_has_parts_available_garage": all(
        ((garages["Brand_Specialization"] == brand) & garages["Parts_Available"].astype(bool)).any()
        for brand in claims["Vehicle_Brand"].unique()
    ),
}

result = {
    "passed": sum(bool(v) for v in checks.values()),
    "total": len(checks),
    "checks": {k: bool(v) for k, v in checks.items()},
    "claims_rows": int(len(claims)),
    "garage_rows": int(len(garages)),
}
output = ROOT / "reports" / "validation_run.json"
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit("Dataset validation failed. Review checks above.")
