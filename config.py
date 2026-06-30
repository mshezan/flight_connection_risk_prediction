from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PIPELINE_VERSION = 3

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FEATURE_DIR = BASE_DIR / "data" / f"features_v{PIPELINE_VERSION}"
MODEL_DIR = BASE_DIR / "model"

MODEL_PATH = MODEL_DIR / f"pipeline_v{PIPELINE_VERSION}.joblib"

for directory in [
    RAW_DIR,
    PROCESSED_DIR,
    FEATURE_DIR,
    MODEL_DIR,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )