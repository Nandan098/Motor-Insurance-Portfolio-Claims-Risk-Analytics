"""Train and evaluate a repair-cost regressor with a chronological holdout."""
from __future__ import annotations
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import CLAIMS_RAW, MODELS, OUTPUTS, REPORTS, RANDOM_STATE, TEST_FRACTION
from src.data_validation import load_inputs
from src.feature_engineering import add_features, NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET


def _build_model() -> Pipeline:
    numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC_FEATURES),
        ("categorical", categorical_pipe, CATEGORICAL_FEATURES),
    ])
    regressor = RandomForestRegressor(
        n_estimators=350,
        min_samples_leaf=2,
        max_features=0.9,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return Pipeline([("preprocessor", preprocessor), ("regressor", regressor)])


def _metrics(y_true: pd.Series, y_pred: np.ndarray, baseline_pred: np.ndarray) -> dict:
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)
    denominator = np.sum(np.abs(y_true_arr))
    return {
        "MAE_INR": float(mean_absolute_error(y_true_arr, y_pred_arr)),
        "RMSE_INR": float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr))),
        "R2": float(r2_score(y_true_arr, y_pred_arr)),
        "WAPE_PERCENT": float(np.sum(np.abs(y_true_arr - y_pred_arr)) / denominator * 100) if denominator else None,
        "Baseline_Median_MAE_INR": float(mean_absolute_error(y_true_arr, baseline_pred)),
        "Baseline_Median_RMSE_INR": float(np.sqrt(mean_squared_error(y_true_arr, baseline_pred))),
    }


def train_and_score() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Create honest holdout metrics plus an all-row demo scoring export.

    Test performance is evaluated only on later records held out chronologically.
    The all-row prediction export is created by a final model fitted on all available
    synthetic examples; those all-row predictions are in-sample and are not used to
    report model performance.
    """
    claims, _ = load_inputs()
    featured = add_features(claims).sort_values(["AccidentDate", "ClaimID"]).reset_index(drop=True)
    split_at = int(len(featured) * (1 - TEST_FRACTION))
    if split_at <= 0 or split_at >= len(featured):
        raise ValueError("Not enough rows for the configured chronological split.")
    train = featured.iloc[:split_at].copy()
    test = featured.iloc[split_at:].copy()
    X_train = train[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = train[TARGET].astype(float)
    X_test = test[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_test = test[TARGET].astype(float)

    holdout_model = _build_model()
    holdout_model.fit(X_train, y_train)
    test_pred = np.maximum(0, holdout_model.predict(X_test))
    median_baseline = np.full(len(test), float(y_train.median()))
    metrics = _metrics(y_test, test_pred, median_baseline)
    metrics.update({
        "model": "RandomForestRegressor",
        "target": TARGET,
        "training_rows": int(len(train)),
        "holdout_rows": int(len(test)),
        "training_start": str(train["AccidentDate"].min()),
        "training_end": str(train["AccidentDate"].max()),
        "holdout_start": str(test["AccidentDate"].min()),
        "holdout_end": str(test["AccidentDate"].max()),
        "split_strategy": "chronological 80/20 holdout by accident timestamp and ClaimID",
        "baseline": "constant median repair cost calculated from training period",
        "data_status": "synthetic demonstration data; metrics measure ability to learn simulated target",
        "holdout_beats_baseline_on_MAE": bool(metrics["MAE_INR"] < metrics["Baseline_Median_MAE_INR"]),
    })

    holdout = test[["ClaimID", "AccidentDate", "Vehicle_Brand", "Model_Year", "Speed_At_Impact_kmh",
                    "G_Force_Impact", "Airbag_Deployed", "Impact_Point", TARGET]].copy()
    holdout["Predicted_Repair_Cost_INR"] = np.round(test_pred, 2)
    holdout["Absolute_Error_INR"] = np.round(np.abs(holdout[TARGET] - holdout["Predicted_Repair_Cost_INR"]), 2)
    holdout["Signed_Error_INR"] = np.round(holdout["Predicted_Repair_Cost_INR"] - holdout[TARGET], 2)

    # Save test predictions from the model that did not train on these rows.
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)
    holdout.to_csv(OUTPUTS / "holdout_repair_cost_predictions.csv", index=False)
    (REPORTS / "model_evaluation.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Feature importance from holdout model: usable for explanatory discussion, not causality.
    preprocessor = holdout_model.named_steps["preprocessor"]
    names = preprocessor.get_feature_names_out()
    importance = holdout_model.named_steps["regressor"].feature_importances_
    importance_df = pd.DataFrame({"Feature": names, "Importance": importance}).sort_values("Importance", ascending=False)
    importance_df.to_csv(REPORTS / "feature_importance.csv", index=False)

    # Fit a final version on all rows for the end-to-end demo export only.
    full_model = _build_model()
    full_model.fit(featured[NUMERIC_FEATURES + CATEGORICAL_FEATURES], featured[TARGET].astype(float))
    joblib.dump(full_model, MODELS / "repair_cost_random_forest.joblib")
    all_pred = np.maximum(0, full_model.predict(featured[NUMERIC_FEATURES + CATEGORICAL_FEATURES]))
    scored = claims.copy()
    scored["Predicted_Repair_Cost_INR"] = np.round(all_pred, 2)
    scored["Prediction_Scope"] = "Illustrative all-data fit; not an out-of-sample estimate"
    scored.to_csv(OUTPUTS / "claims_cost_scored_demo.csv", index=False)

    return holdout, scored, metrics


if __name__ == "__main__":
    _, _, result = train_and_score()
    print(json.dumps(result, indent=2))
