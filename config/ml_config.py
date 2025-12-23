"""QUANTP1 v3.1 - Machine Learning Configuration"""
from config.paths_config import DEFAULT_MODEL_FILE

# Model Settings
MODEL_VERSION = "v1"
MODEL_NAME = "brain_eurusd_m15_v1.pkl"
MODEL_PATH = DEFAULT_MODEL_FILE

# Feature Configuration
FEATURE_NAMES = [
    "z_score",
    "adx",
    "rsi",
    "bb_width",
    "bb_percent_b",
    "hour",
    "day_of_week"
]

NUM_FEATURES = len(FEATURE_NAMES)

# Prediction Thresholds
MIN_CONFIDENCE_THRESHOLD = 0.65  # 65% minimum confidence
HIGH_CONFIDENCE_THRESHOLD = 0.80  # 80% high confidence
VERY_HIGH_CONFIDENCE_THRESHOLD = 0.90  # 90% very high confidence

# Model Validation
MAX_MODEL_AGE_DAYS = 90  # Retrain if model older than 90 days
MIN_PREDICTION_PROBABILITY = 0.50  # Below this, model is uncertain

# Feature Scaling (if needed)
FEATURE_SCALING = True
SCALER_TYPE = "standard"  # or "minmax"

# Model Type
MODEL_TYPE = "RandomForestClassifier"
MODEL_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
}


def validate_ml_config():
    """Validate ML configuration"""
    if MIN_CONFIDENCE_THRESHOLD < 0.5 or MIN_CONFIDENCE_THRESHOLD > 1.0:
        raise ValueError("MIN_CONFIDENCE_THRESHOLD must be between 0.5 and 1.0")
    if NUM_FEATURES != 7:
        raise ValueError("Expected 7 features for the model")
    return True


if __name__ == "__main__":
    try:
        validate_ml_config()
        print("✅ ML configuration valid")
        print(f"Model: {MODEL_NAME}")
        print(f"Features: {NUM_FEATURES}")
        print(f"Min Confidence: {MIN_CONFIDENCE_THRESHOLD*100}%")
    except ValueError as e:
        print(f"❌ {e}")
