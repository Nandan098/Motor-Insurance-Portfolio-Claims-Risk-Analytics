"""Generate a realistic-style synthetic auto-insurance telematics dataset.

All records are simulated for portfolio/learning purposes. They are not real
policyholders, crashes, claim payments, repair facilities, or live inventory.
Reproducible with a fixed random seed; distributions are intentionally uneven.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

SEED = 20261020
N_CLAIMS = 3000
N_GARAGES = 100
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"
for p in (RAW, PROCESSED, DOCS, REPORTS):
    p.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

# Uneven vehicle-brand mix: mass market brands dominate; premium brands are rare.
BRANDS = [
    "Maruti Suzuki", "Hyundai", "Tata", "Mahindra", "Honda", "Kia",
    "Toyota", "Renault", "Volkswagen", "Skoda", "BMW", "Mercedes-Benz"
]
BRAND_P = np.array([.27, .18, .15, .11, .09, .07, .05, .025, .025, .015, .008, .007])
BRAND_P = BRAND_P / BRAND_P.sum()
BRAND_COST_MULT = {
    "Maruti Suzuki": 0.82, "Hyundai": 0.92, "Tata": 0.94, "Mahindra": 1.03,
    "Honda": 1.02, "Kia": 1.02, "Toyota": 1.12, "Renault": 0.96,
    "Volkswagen": 1.28, "Skoda": 1.30, "BMW": 2.15, "Mercedes-Benz": 2.30,
}
BRAND_PARTS_AVAIL_P = {
    "Maruti Suzuki": .88, "Hyundai": .85, "Tata": .84, "Mahindra": .80,
    "Honda": .78, "Kia": .76, "Toyota": .70, "Renault": .67,
    "Volkswagen": .62, "Skoda": .60, "BMW": .48, "Mercedes-Benz": .46,
}

# Delhi NCR centers are approximate spatial clusters for simulated routing, not garage addresses.
AREAS = {
    "Delhi": (28.6139, 77.2090),
    "Gurugram": (28.4595, 77.0266),
    "Noida": (28.5355, 77.3910),
    "Faridabad": (28.4089, 77.3178),
    "Ghaziabad": (28.6692, 77.4538),
}
AREA_CLAIM_P = np.array([.40, .22, .19, .10, .09])
AREA_GARAGE_WEIGHTS = np.array([.37, .24, .18, .11, .10])
AREA_NAMES = list(AREAS)

# 1) Claims / telematics
# Sample dates with a modest weekday uplift rather than uniform frequency.
all_days = pd.date_range("2023-01-01", "2025-12-31", freq="D")
day_weights = np.where(all_days.dayofweek < 5, 1.08, 0.86).astype(float)
day_weights /= day_weights.sum()
incident_dates = pd.to_datetime(rng.choice(all_days.to_numpy(), size=N_CLAIMS, p=day_weights)).normalize()
# Crash frequency varies by weekday and hour, not uniformly.
hour_weights = np.array([.005,.003,.002,.002,.003,.008,.025,.055,.070,.060,.052,.050,
                         .053,.055,.060,.065,.072,.078,.078,.070,.055,.035,.020,.010])
hour_weights /= hour_weights.sum()
incident_hour = rng.choice(np.arange(24), size=N_CLAIMS, p=hour_weights)
incident_dates = incident_dates + pd.to_timedelta(incident_hour, unit="h") + pd.to_timedelta(rng.integers(0, 60, N_CLAIMS), unit="m")

brands = rng.choice(BRANDS, size=N_CLAIMS, p=BRAND_P)
area_for_claim = rng.choice(AREA_NAMES, size=N_CLAIMS, p=AREA_CLAIM_P)
lat = np.empty(N_CLAIMS); lon = np.empty(N_CLAIMS)
for area in AREA_NAMES:
    mask = area_for_claim == area
    center_lat, center_lon = AREAS[area]
    # Dense city-level clustering with a minority of wider-area trips.
    wide = rng.random(mask.sum()) < .14
    lat_noise = rng.normal(0, .020, mask.sum())
    lon_noise = rng.normal(0, .023, mask.sum())
    lat_noise[wide] = rng.normal(0, .060, wide.sum())
    lon_noise[wide] = rng.normal(0, .070, wide.sum())
    lat[mask] = center_lat + lat_noise
    lon[mask] = center_lon + lon_noise

# Severity mix is strongly imbalanced: most crash impacts are lower-severity.
severity = rng.choice(["Minor", "Moderate", "Severe", "Very Severe"],
                      size=N_CLAIMS, p=[.58, .29, .105, .025])
speed = np.zeros(N_CLAIMS)
for label, lo, scale in [
    ("Minor", 1, 34), ("Moderate", 22, 43), ("Severe", 52, 47), ("Very Severe", 78, 65)
]:
    mask = severity == label
    # Beta distribution keeps impact speeds inside plausible ranges with uneven densities.
    if label == "Minor": vals = lo + rng.beta(2.0, 4.8, mask.sum()) * scale
    elif label == "Moderate": vals = lo + rng.beta(2.1, 2.5, mask.sum()) * scale
    elif label == "Severe": vals = lo + rng.beta(2.2, 2.0, mask.sum()) * scale
    else: vals = lo + rng.beta(2.2, 1.7, mask.sum()) * scale
    speed[mask] = vals
speed = np.clip(speed, 0, 143)

g_force = 0.45 + 0.018 * speed + 0.00023 * speed**2 + rng.normal(0, .42, N_CLAIMS)
g_force = np.clip(g_force, .25, 13.5)
impact_point = rng.choice(["Front", "Rear", "Side"], size=N_CLAIMS, p=[.49, .235, .275])
front_bonus = (impact_point == "Front") * .45
side_bonus = (impact_point == "Side") * .15
# Airbag likelihood increases with impact speed and g-force; not balanced.
logit = -5.1 + .032 * speed + .32 * g_force + front_bonus + side_bonus
p_airbag = 1 / (1 + np.exp(-logit))
airbag = rng.binomial(1, p_airbag, N_CLAIMS)
# Braking data: many short/no recorded braking events, fewer long pre-impact braking intervals.
braking = np.where(rng.random(N_CLAIMS) < .27, 0,
                   rng.lognormal(mean=-.28 + .004 * speed, sigma=.62, size=N_CLAIMS))
braking = np.clip(braking, 0, 5.5)

# Vehicle ages skew toward newer vehicles, but older cars are present.
crash_year = incident_dates.year.to_numpy()
vehicle_age = np.clip(rng.gamma(shape=2.2, scale=2.0, size=N_CLAIMS).round().astype(int), 0, 20)
model_year = np.maximum(2005, crash_year - vehicle_age)

weather = rng.choice(["Clear", "Light Rain", "Heavy Rain", "Fog"],
                     size=N_CLAIMS, p=[.72, .17, .075, .035])
road_type = rng.choice(["Urban Arterial", "Residential", "Highway", "Service Road"],
                       size=N_CLAIMS, p=[.39, .28, .19, .14])
# Generate correlated claim costs with multiplicative noise: a long right tail is expected.
impact_factor = np.select([impact_point == "Front", impact_point == "Side", impact_point == "Rear"],
                          [1.22, 1.12, .91], default=1.0)
airbag_factor = np.where(airbag == 1, rng.normal(1.63, .13, N_CLAIMS), 1.0)
vehicle_age_factor = 1.13 - np.minimum(vehicle_age, 15) * .018
weather_factor = np.select([weather == "Heavy Rain", weather == "Fog", weather == "Light Rain"],
                            [1.07, 1.04, 1.02], default=1.0)
brand_factor = np.array([BRAND_COST_MULT[b] for b in brands])
base_damage = 2600 + 29.0 * np.power(np.maximum(speed, 1), 1.62) + 2050 * np.maximum(g_force - 1, 0)
noise = rng.lognormal(mean=-0.5 * .34**2, sigma=.34, size=N_CLAIMS)
repair_cost = base_damage * impact_factor * airbag_factor * vehicle_age_factor * weather_factor * brand_factor * noise
# Small chance of a high-cost secondary repair (not a fixed 10x injected anomaly).
secondary_repair = rng.random(N_CLAIMS) < .012
repair_cost[secondary_repair] *= rng.uniform(1.25, 2.0, secondary_repair.sum())
repair_cost = np.maximum(1800, np.round(repair_cost / 100) * 100).astype(int)

# Mostly unique vehicles, with a few vehicles experiencing another recorded incident.
vehicle_ids = np.array([f"VEH{n:06d}" for n in range(1, N_CLAIMS + 1)], dtype=object)
repeats = rng.choice(np.arange(60, N_CLAIMS), size=115, replace=False)
prior_vehicle_idxs = rng.choice(np.arange(0, 60), size=len(repeats), replace=True)
for idx, prior in zip(repeats, prior_vehicle_idxs):
    vehicle_ids[idx] = vehicle_ids[prior]

claim_ids = np.array([f"CLM{n:07d}" for n in range(1, N_CLAIMS + 1)])
claims = pd.DataFrame({
    "ClaimID": claim_ids,
    "AccidentDate": incident_dates,
    "VehicleID": vehicle_ids,
    "Vehicle_Brand": brands,
    "Model_Year": model_year.astype(int),
    "Speed_At_Impact_kmh": np.round(speed, 1),
    "G_Force_Impact": np.round(g_force, 2),
    "Airbag_Deployed": airbag.astype(int),
    "Braking_Duration_Seconds": np.round(braking, 2),
    "Impact_Point": impact_point,
    "Weather_Condition": weather,
    "Road_Type": road_type,
    "Crash_Area": area_for_claim,
    "Vehicle_Latitude": np.round(lat, 6),
    "Vehicle_Longitude": np.round(lon, 6),
    "Actual_Repair_Cost_INR": repair_cost,
})

# 2) Partner garages: 100 facilities clustered unevenly across Delhi NCR.
# Use a floor per brand, with remaining specialization slots allocated unevenly.
min_per_brand = 3
remaining = N_GARAGES - min_per_brand * len(BRANDS)
extra_counts = rng.multinomial(remaining, BRAND_P)
brand_counts = {brand: min_per_brand + int(extra_counts[i]) for i, brand in enumerate(BRANDS)}
garage_brands = np.concatenate([[b] * brand_counts[b] for b in BRANDS])
rng.shuffle(garage_brands)
garage_areas = rng.choice(AREA_NAMES, size=N_GARAGES, p=AREA_GARAGE_WEIGHTS)
g_lat = np.zeros(N_GARAGES); g_lon = np.zeros(N_GARAGES)
for area in AREA_NAMES:
    mask = garage_areas == area
    center_lat, center_lon = AREAS[area]
    g_lat[mask] = center_lat + rng.normal(0, .024, mask.sum())
    g_lon[mask] = center_lon + rng.normal(0, .027, mask.sum())
parts_available = np.array([
    rng.random() < BRAND_PARTS_AVAIL_P[b] for b in garage_brands
])
# Guarantee enough eligible options per make so routing can be demonstrated; these are still simulated.
for brand in BRANDS:
    indices = np.where(garage_brands == brand)[0]
    if parts_available[indices].sum() < 2:
        choose = rng.choice(indices, size=min(2, len(indices)), replace=False)
        parts_available[choose] = True
preferred_partner = rng.random(N_GARAGES) < np.where(
    np.isin(garage_areas, ["Delhi", "Gurugram", "Noida"]), .68, .49
)
service_capacity = np.clip(rng.lognormal(mean=2.7, sigma=.42, size=N_GARAGES).round().astype(int), 5, 45)
turnaround = np.clip(rng.gamma(shape=2.2, scale=1.4, size=N_GARAGES), .5, 12)
labor_rate = np.array([{"Delhi": 900, "Gurugram": 1050, "Noida": 930, "Faridabad": 800, "Ghaziabad": 780}[a]
                       for a in garage_areas], dtype=float) * rng.lognormal(0, .12, N_GARAGES)

garages = pd.DataFrame({
    "GarageID": [f"GAR{n:04d}" for n in range(1, N_GARAGES + 1)],
    "Garage_Name": [f"{a} Auto Service Centre {i:03d}" for i, a in enumerate(garage_areas, start=1)],
    "Area": garage_areas,
    "Latitude": np.round(g_lat, 6),
    "Longitude": np.round(g_lon, 6),
    "Brand_Specialization": garage_brands,
    "Parts_Available": parts_available.astype(bool),
    "Preferred_Partner": preferred_partner.astype(bool),
    "Daily_Service_Capacity": service_capacity,
    "Avg_Repair_Turnaround_Days": np.round(turnaround, 1),
    "Labor_Rate_INR_Per_Hour": np.round(labor_rate).astype(int),
})

# 3) Data dictionaries and metadata
claims.to_csv(RAW / "telematics_claims.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
garages.to_csv(RAW / "partner_garages.csv", index=False)
# Also persist processed copies (currently identical, canonical clean input tables).
claims.to_csv(PROCESSED / "telematics_claims_clean.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
garages.to_csv(PROCESSED / "partner_garages_clean.csv", index=False)

brand_mix = claims["Vehicle_Brand"].value_counts(normalize=True).rename_axis("Vehicle_Brand").reset_index(name="Share")
severity_bins = pd.cut(claims["Speed_At_Impact_kmh"], [-1, 25, 50, 80, 150], labels=["Low (<=25)", "Moderate (25-50)", "High (50-80)", "Very high (>80)"])
speed_mix = severity_bins.value_counts(normalize=True, sort=False).rename_axis("Speed_Band").reset_index(name="Share")
parts_summary = garages.groupby("Brand_Specialization", as_index=False).agg(
    Garage_Count=("GarageID", "count"),
    Eligible_Garages=("Parts_Available", "sum"),
    Preferred_Garages=("Preferred_Partner", "sum"),
)
parts_summary["Eligible_Share"] = parts_summary["Eligible_Garages"] / parts_summary["Garage_Count"]
claims["AccidentMonth"] = pd.to_datetime(claims["AccidentDate"]).dt.to_period("M").astype(str)
monthly = claims.groupby("AccidentMonth", as_index=False).agg(Claims=("ClaimID", "count"), Mean_Repair_Cost_INR=("Actual_Repair_Cost_INR", "mean"))

metadata = {
    "dataset_name": "Auto Insurance Telematics & Garage Routing Optimization",
    "data_type": "Synthetic, realistic-style demonstration data; not real customer or claims data",
    "random_seed": SEED,
    "claims_rows": int(len(claims)),
    "garage_rows": int(len(garages)),
    "date_range_start": str(claims["AccidentDate"].min()),
    "date_range_end": str(claims["AccidentDate"].max()),
    "brand_distribution_is_uniform": False,
    "crash_severity_distribution_is_uniform": False,
    "repair_cost_is_right_skewed": True,
    "geography": "Simulated clusters around Delhi NCR city centers; coordinates are generated and do not identify real crashes or garage addresses",
    "limitations": [
        "Repair costs are simulated from severity-related drivers with noise, not sourced from real insurer invoices.",
        "Vehicle and garage records are fictional.",
        "Parts availability and repair turnaround are simulated snapshots, not live inventory or operational measurements.",
        "Results should not be presented as real-world insurance performance."
    ],
}
with open(DOCS / "dataset_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)
brand_mix.to_csv(REPORTS / "vehicle_brand_distribution.csv", index=False)
speed_mix.to_csv(REPORTS / "impact_speed_distribution.csv", index=False)
parts_summary.to_csv(REPORTS / "garage_coverage_by_brand.csv", index=False)
monthly.to_csv(REPORTS / "claims_by_month.csv", index=False)

# Data quality checks and compact report.
checks = {
    "claims_row_count_is_3000": len(claims) == N_CLAIMS,
    "garage_row_count_is_100": len(garages) == N_GARAGES,
    "claim_ids_unique": claims["ClaimID"].is_unique,
    "no_missing_claim_values": int(claims.isna().sum().sum()) == 0,
    "no_missing_garage_values": int(garages.isna().sum().sum()) == 0,
    "repair_cost_positive": bool((claims["Actual_Repair_Cost_INR"] > 0).all()),
    "speeds_non_negative": bool((claims["Speed_At_Impact_kmh"] >= 0).all()),
    "gforce_positive": bool((claims["G_Force_Impact"] > 0).all()),
    "garage_coordinates_in_valid_ranges": bool(garages["Latitude"].between(-90,90).all() and garages["Longitude"].between(-180,180).all()),
    "all_brands_have_eligible_garages": bool((parts_summary["Eligible_Garages"] >= 1).all()),
}
quality = {
    "checks": checks,
    "passed": int(sum(checks.values())),
    "total": len(checks),
    "claims": {
        "rows": len(claims), "unique_vehicle_ids": int(claims["VehicleID"].nunique()),
        "airbag_deployment_rate": round(float(claims["Airbag_Deployed"].mean()), 4),
        "repair_cost_median_inr": int(claims["Actual_Repair_Cost_INR"].median()),
        "repair_cost_p90_inr": int(claims["Actual_Repair_Cost_INR"].quantile(.9)),
        "repair_cost_p99_inr": int(claims["Actual_Repair_Cost_INR"].quantile(.99)),
        "mean_speed_kmh": round(float(claims["Speed_At_Impact_kmh"].mean()), 2),
        "share_speed_over_80_kmh": round(float((claims["Speed_At_Impact_kmh"] > 80).mean()), 4),
    },
    "garages": {
        "rows": len(garages), "parts_available_share": round(float(garages["Parts_Available"].mean()), 4),
        "preferred_partner_share": round(float(garages["Preferred_Partner"].mean()), 4),
    }
}
with open(REPORTS / "data_quality_report.json", "w", encoding="utf-8") as f:
    json.dump(quality, f, indent=2)

# Data dictionary
claims_dict = [
    ("ClaimID", "string", "Unique synthetic claim identifier", "Unique; primary key"),
    ("AccidentDate", "datetime", "Simulated incident timestamp, 2023-2025", "Varies across weekdays/hours"),
    ("VehicleID", "string", "Synthetic vehicle identifier; a small subset repeats across claims", "Not unique by design"),
    ("Vehicle_Brand", "category", "Vehicle manufacturer / make", "Uneven make distribution"),
    ("Model_Year", "integer", "Vehicle model year, no later than incident year", "Older vehicles are less common"),
    ("Speed_At_Impact_kmh", "float", "Simulated impact speed in km/h", "Most incidents lower-speed; severe impacts rarer"),
    ("G_Force_Impact", "float", "Simulated peak impact acceleration, expressed in g", "Positively related to speed with noise"),
    ("Airbag_Deployed", "integer", "1 if simulated airbag deployment, else 0", "Probability increases with impact severity"),
    ("Braking_Duration_Seconds", "float", "Simulated pre-impact braking duration", "Many zero/short values; right-skewed positive values"),
    ("Impact_Point", "category", "Primary impact zone: Front, Rear or Side", "Uneven category frequencies"),
    ("Weather_Condition", "category", "Simulated weather at incident", "Clear dominates; rain/fog less common"),
    ("Road_Type", "category", "Simulated road class", "Uneven category frequencies"),
    ("Crash_Area", "category", "Simulated Delhi NCR city cluster", "Uneven city distribution"),
    ("Vehicle_Latitude", "float", "Generated latitude for simulated crash location", "Approximate cluster around city center"),
    ("Vehicle_Longitude", "float", "Generated longitude for simulated crash location", "Approximate cluster around city center"),
    ("Actual_Repair_Cost_INR", "integer", "Simulated repair cost used as regression target", "Right-skewed and correlated with impact, airbag and make"),
]
garage_dict = [
    ("GarageID", "string", "Unique synthetic garage identifier", "Primary key"),
    ("Garage_Name", "string", "Fictional garage name", "Not a real business"),
    ("Area", "category", "Simulated Delhi NCR area cluster", "Uneven city distribution"),
    ("Latitude", "float", "Generated garage latitude", "Synthetic coordinates"),
    ("Longitude", "float", "Generated garage longitude", "Synthetic coordinates"),
    ("Brand_Specialization", "category", "Primary brand specialization", "Uneven by brand; at least three facilities per make"),
    ("Parts_Available", "boolean", "Simulated snapshot flag for relevant parts in stock", "Availability probability varies by make"),
    ("Preferred_Partner", "boolean", "Simulated preferred-network indicator", "Not equally distributed"),
    ("Daily_Service_Capacity", "integer", "Approximate simulated repair intake capacity/day", "Skewed, bounded"),
    ("Avg_Repair_Turnaround_Days", "float", "Simulated average repair turnaround estimate", "Variable across facilities"),
    ("Labor_Rate_INR_Per_Hour", "integer", "Simulated labor charge per hour", "Varies by area and facility"),
]
with open(DOCS / "DATA_DICTIONARY.md", "w", encoding="utf-8") as f:
    f.write("# Data dictionary and design notes\n\n")
    f.write("**Dataset status:** All rows are synthetic and generated for learning. The distribution shapes are designed to be realistic-style, not to represent measured real-world frequencies. Do not describe them as actual insurer data.\n\n")
    f.write("## Telematics claims\n\n| Column | Type | Meaning | Notes |\n|---|---|---|---|\n")
    for row in claims_dict:
        f.write("| " + " | ".join(row) + " |\n")
    f.write("\n## Partner garages\n\n| Column | Type | Meaning | Notes |\n|---|---|---|---|\n")
    for row in garage_dict:
        f.write("| " + " | ".join(row) + " |\n")
    f.write("\n## Design choices to avoid artificial balance\n\n")
    f.write("- Vehicle make share is weighted toward common mass-market brands; premium brands are rare.\n")
    f.write("- Crash severities are imbalanced: lower-impact collisions are common and very severe impacts are rare.\n")
    f.write("- Airbag deployment probability increases with speed, g-force, and collision zone, with stochastic variation.\n")
    f.write("- Repair costs use a heavy-tailed multiplicative-noise model and respond to impact speed, g-force, airbag deployment, impact zone, vehicle age, weather, and brand cost multiplier.\n")
    f.write("- Crash and garage locations cluster unevenly around Delhi NCR area centroids; coordinates are simulated.\n")
    f.write("- Garage part availability depends on specialization and is not 50/50 for all brands. At least one eligible garage is retained for each brand to support routing exercises.\n")
    f.write("- No fixed 50/50 target labels are provided because this dataset is for cost regression and routing, not fraud classification.\n")

print(json.dumps(quality, indent=2))
