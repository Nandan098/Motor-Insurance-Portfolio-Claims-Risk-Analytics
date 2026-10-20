"""Brand-compatible, in-stock garage routing with distance and cycle-time scoring."""
from __future__ import annotations
import math
import pandas as pd
import numpy as np

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2, lon2) -> np.ndarray | float:
    """Great-circle distance in kilometres. lat2/lon2 can be scalars or arrays."""
    lat1_rad, lon1_rad = np.radians(float(lat1)), np.radians(float(lon1))
    lat2_rad, lon2_rad = np.radians(np.asarray(lat2, dtype=float)), np.radians(np.asarray(lon2, dtype=float))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    a = np.clip(a, 0.0, 1.0)
    result = 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))
    return float(result) if np.ndim(result) == 0 else result


def _minmax(series: pd.Series) -> pd.Series:
    span = series.max() - series.min()
    if pd.isna(span) or span == 0:
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / span


def recommend_garage(
    vehicle_latitude: float,
    vehicle_longitude: float,
    vehicle_brand: str,
    garages: pd.DataFrame,
    average_urban_speed_kmph: float = 25.0,
) -> dict:
    """Return nearest eligible garage and balanced recommendation.

    Eligibility requires matching brand specialization and parts in stock. When at
    least one eligible preferred partner exists, scoring is restricted to preferred
    partners. Otherwise the function falls back to eligible non-preferred partners
    and records that fallback. The balanced score weights normalized distance 60%,
    turnaround 30%, and capacity preference 10%; it is a demonstrative heuristic.
    """
    brand = str(vehicle_brand).strip().casefold()
    g = garages.copy()
    normalized_brand = g["Brand_Specialization"].astype(str).str.strip().str.casefold()
    parts = g["Parts_Available"].astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"])
    g = g.loc[(normalized_brand == brand) & parts].copy()
    if g.empty:
        raise ValueError(f"No in-stock garage found for vehicle brand {vehicle_brand!r}.")

    preferred = g["Preferred_Partner"].astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"])
    fallback_used = not bool(preferred.any())
    if preferred.any():
        candidates = g.loc[preferred].copy()
        candidate_policy = "Preferred partner + brand match + parts in stock"
    else:
        candidates = g.copy()
        candidate_policy = "Fallback: any brand-matched in-stock partner"

    candidates["Distance_km"] = haversine_km(
        vehicle_latitude, vehicle_longitude,
        candidates["Latitude"].to_numpy(), candidates["Longitude"].to_numpy(),
    )
    candidates["Estimated_Travel_Minutes"] = candidates["Distance_km"] / max(average_urban_speed_kmph, 1.0) * 60
    candidates["Estimated_Repair_Turnaround_Hours"] = candidates["Avg_Repair_Turnaround_Days"] * 24
    candidates["Estimated_Cycle_Hours"] = candidates["Estimated_Travel_Minutes"] / 60 + candidates["Estimated_Repair_Turnaround_Hours"]
    candidates["Distance_Normalized"] = _minmax(candidates["Distance_km"])
    candidates["Turnaround_Normalized"] = _minmax(candidates["Avg_Repair_Turnaround_Days"])
    candidates["Capacity_Normalized"] = _minmax(candidates["Daily_Service_Capacity"])
    candidates["Routing_Score"] = (
        0.60 * candidates["Distance_Normalized"]
        + 0.30 * candidates["Turnaround_Normalized"]
        + 0.10 * (1 - candidates["Capacity_Normalized"])
    )
    nearest = candidates.sort_values(["Distance_km", "Avg_Repair_Turnaround_Days"]).iloc[0]
    recommended = candidates.sort_values(["Routing_Score", "Distance_km"]).iloc[0]

    return {
        "Recommended_GarageID": recommended["GarageID"],
        "Recommended_Garage_Name": recommended["Garage_Name"],
        "Recommended_Garage_Area": recommended["Area"],
        "Recommended_Garage_Distance_km": round(float(recommended["Distance_km"]), 3),
        "Recommended_Garage_Travel_Minutes": round(float(recommended["Estimated_Travel_Minutes"]), 1),
        "Recommended_Garage_Turnaround_Days": float(recommended["Avg_Repair_Turnaround_Days"]),
        "Recommended_Garage_Est_Cycle_Hours": round(float(recommended["Estimated_Cycle_Hours"]), 2),
        "Recommended_Garage_Routing_Score": round(float(recommended["Routing_Score"]), 4),
        "Nearest_Eligible_GarageID": nearest["GarageID"],
        "Nearest_Eligible_Garage_Distance_km": round(float(nearest["Distance_km"]), 3),
        "Eligible_Garages_Considered": int(len(candidates)),
        "Preferred_Fallback_Used": bool(fallback_used),
        "Candidate_Policy": candidate_policy,
    }


def route_all_claims(claims: pd.DataFrame, garages: pd.DataFrame) -> pd.DataFrame:
    """Route every crash record and retain the source claim fields."""
    outputs = []
    for row in claims.itertuples(index=False):
        result = recommend_garage(
            vehicle_latitude=float(row.Vehicle_Latitude),
            vehicle_longitude=float(row.Vehicle_Longitude),
            vehicle_brand=str(row.Vehicle_Brand),
            garages=garages,
        )
        result["ClaimID"] = row.ClaimID
        result["Vehicle_Brand"] = row.Vehicle_Brand
        result["Crash_Area"] = row.Crash_Area
        outputs.append(result)
    route_df = pd.DataFrame(outputs)
    return claims[["ClaimID", "VehicleID", "AccidentDate", "Vehicle_Brand", "Crash_Area", "Actual_Repair_Cost_INR"]].merge(
        route_df, on=["ClaimID", "Vehicle_Brand", "Crash_Area"], how="left", validate="one_to_one"
    )
