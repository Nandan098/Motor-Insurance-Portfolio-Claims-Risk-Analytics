"""Feature engineering helpers shared by training and scoring."""
from __future__ import annotations
import numpy as np
import pandas as pd

TARGET = "Actual_Repair_Cost_INR"
NUMERIC_FEATURES = [
    "Model_Year", "Vehicle_Age_Years", "Speed_At_Impact_kmh", "G_Force_Impact",
    "Airbag_Deployed", "Braking_Duration_Seconds", "Accident_Hour",
    "Accident_Weekday", "Is_Weekend", "Accident_Month", "Impact_Severity_Index",
]
CATEGORICAL_FEATURES = [
    "Vehicle_Brand", "Impact_Point", "Weather_Condition", "Road_Type", "Crash_Area",
]


def add_features(claims: pd.DataFrame) -> pd.DataFrame:
    """Create interpretable predictors without referencing repair-cost target."""
    df = claims.copy()
    df["AccidentDate"] = pd.to_datetime(df["AccidentDate"], errors="coerce")
    df["Vehicle_Age_Years"] = (
        df["AccidentDate"].dt.year - pd.to_numeric(df["Model_Year"], errors="coerce")
    ).clip(lower=0, upper=40)
    df["Accident_Hour"] = df["AccidentDate"].dt.hour
    df["Accident_Weekday"] = df["AccidentDate"].dt.dayofweek
    df["Is_Weekend"] = (df["Accident_Weekday"] >= 5).astype(int)
    df["Accident_Month"] = df["AccidentDate"].dt.month
    # Explainable combined severity marker; not a target-derived feature.
    speed_scaled = df["Speed_At_Impact_kmh"].clip(0, 150) / 150
    g_scaled = df["G_Force_Impact"].clip(0, 15) / 15
    df["Impact_Severity_Index"] = 0.55 * speed_scaled + 0.35 * g_scaled + 0.10 * df["Airbag_Deployed"].clip(0, 1)
    return df
