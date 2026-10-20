"""Central project paths and modeling settings."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"
REPORTS = PROJECT_ROOT / "reports"
SQL_RESULTS = REPORTS / "sql_results"
MODELS = PROJECT_ROOT / "models"
VISUALS = PROJECT_ROOT / "visuals"

CLAIMS_RAW = DATA_RAW / "telematics_claims.csv"
GARAGES_RAW = DATA_RAW / "partner_garages.csv"
CLAIMS_CLEAN = DATA_PROCESSED / "telematics_claims_clean.csv"
GARAGES_CLEAN = DATA_PROCESSED / "partner_garages_clean.csv"
DATABASE_PATH = DATA_PROCESSED / "auto_insurance_analytics.sqlite"

RANDOM_STATE = 42
TEST_FRACTION = 0.20
AVERAGE_URBAN_SPEED_KMPH = 25.0  # Explicit simulation assumption; not live traffic.
