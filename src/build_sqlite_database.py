"""Create a local SQLite analytics database from the project outputs."""
from __future__ import annotations
import sqlite3
import pandas as pd
from src.config import DATABASE_PATH, DATA_PROCESSED, CLAIMS_CLEAN, GARAGES_CLEAN, OUTPUTS


def build_database() -> str:
    claims = pd.read_csv(CLAIMS_CLEAN, parse_dates=["AccidentDate"])
    garages = pd.read_csv(GARAGES_CLEAN)
    routing_path = OUTPUTS / "garage_routing_recommendations.csv"
    holdout_path = OUTPUTS / "holdout_repair_cost_predictions.csv"
    scored_path = OUTPUTS / "claims_cost_scored_demo.csv"
    routing = pd.read_csv(routing_path)
    holdout = pd.read_csv(holdout_path)
    scored = pd.read_csv(scored_path)

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        claims.to_sql("telematics_claims", conn, if_exists="replace", index=False)
        garages.to_sql("partner_garages", conn, if_exists="replace", index=False)
        routing.to_sql("garage_routing", conn, if_exists="replace", index=False)
        holdout.to_sql("holdout_predictions", conn, if_exists="replace", index=False)
        scored.to_sql("claims_cost_scored_demo", conn, if_exists="replace", index=False)
        conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_claims_vehicle ON telematics_claims(VehicleID);
            CREATE INDEX IF NOT EXISTS idx_claims_brand ON telematics_claims(Vehicle_Brand);
            CREATE INDEX IF NOT EXISTS idx_claims_date ON telematics_claims(AccidentDate);
            CREATE INDEX IF NOT EXISTS idx_garages_brand ON partner_garages(Brand_Specialization);
            CREATE INDEX IF NOT EXISTS idx_routing_claim ON garage_routing(ClaimID);
        """)
    return str(DATABASE_PATH)


if __name__ == "__main__":
    print(f"SQLite database built: {build_database()}")
