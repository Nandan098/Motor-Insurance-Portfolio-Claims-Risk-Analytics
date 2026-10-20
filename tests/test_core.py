"""Fast tests for the project’s key data and routing invariants."""
from pathlib import Path
import pandas as pd
import pytest

from src.config import CLAIMS_RAW, GARAGES_RAW
from src.data_validation import load_inputs, validate_inputs
from src.feature_engineering import add_features, NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET
from src.garage_routing import haversine_km, recommend_garage


def test_input_data_quality_passes():
    claims, garages = load_inputs()
    report = validate_inputs(claims, garages)
    assert report["status"] == "PASS"
    assert report["passed_count"] == report["check_count"]
    assert len(claims) == 3000
    assert len(garages) == 100


def test_haversine_distance_is_zero_for_same_point():
    assert haversine_km(28.6139, 77.2090, 28.6139, 77.2090) == pytest.approx(0.0, abs=1e-8)


def test_haversine_delhi_to_gurugram_is_plausible_straight_line_distance():
    distance = haversine_km(28.6139, 77.2090, 28.4595, 77.0266)
    assert 15 < distance < 35


def test_features_do_not_include_target_as_predictor():
    claims, _ = load_inputs()
    featured = add_features(claims.head(25))
    assert "Vehicle_Age_Years" in featured.columns
    assert "Impact_Severity_Index" in featured.columns
    assert TARGET not in NUMERIC_FEATURES
    assert TARGET not in CATEGORICAL_FEATURES


def test_routing_returns_brand_compatible_in_stock_garage():
    claims, garages = load_inputs()
    claim = claims.iloc[0]
    result = recommend_garage(
        float(claim["Vehicle_Latitude"]),
        float(claim["Vehicle_Longitude"]),
        claim["Vehicle_Brand"],
        garages,
    )
    selected = garages.loc[garages["GarageID"] == result["Recommended_GarageID"]].iloc[0]
    assert selected["Brand_Specialization"].casefold() == str(claim["Vehicle_Brand"]).casefold()
    assert bool(selected["Parts_Available"] is True or str(selected["Parts_Available"]).lower() == "true")
    assert result["Recommended_Garage_Distance_km"] >= 0
    assert result["Eligible_Garages_Considered"] >= 1


def test_routing_fails_clearly_when_no_brand_match_with_stock():
    _, garages = load_inputs()
    unavailable = garages.copy()
    unavailable["Parts_Available"] = False
    with pytest.raises(ValueError, match="No in-stock garage"):
        recommend_garage(28.6, 77.2, "Maruti Suzuki", unavailable)
