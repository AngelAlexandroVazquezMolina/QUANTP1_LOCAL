"""QUANTP1 v3.1 - Paths Configuration"""
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Main directories
CONFIG_DIR = PROJECT_ROOT / "config"
CORE_DIR = PROJECT_ROOT / "core"
DATA_PIPELINE_DIR = PROJECT_ROOT / "data_pipeline"
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
STATE_DIR = PROJECT_ROOT / "state"
LOGS_DIR = PROJECT_ROOT / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
UTILS_DIR = PROJECT_ROOT / "utils"
RESEARCH_DIR = PROJECT_ROOT / "research"

# State files
STATE_FILE = STATE_DIR / "trading_state.json"
STATE_BACKUP = STATE_DIR / "trading_state.backup.json"

# Log files
SYSTEM_LOG = LOGS_DIR / "system.log"
ERROR_LOG = LOGS_DIR / "error.log"
TRADING_LOG = LOGS_DIR / "trading.log"

# Model files
DEFAULT_MODEL_FILE = MODELS_DIR / "brain_eurusd_m15_v1.pkl"
MODEL_METADATA_FILE = MODELS_DIR / "model_metadata.json"


def ensure_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        CONFIG_DIR, CORE_DIR, DATA_PIPELINE_DIR, SRC_DIR,
        MODELS_DIR, STATE_DIR, LOGS_DIR, SCRIPTS_DIR,
        UTILS_DIR, RESEARCH_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_directories()
    print("✅ All directories created successfully")
