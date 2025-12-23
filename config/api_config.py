"""QUANTP1 v3.1 - API Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# Twelve Data API
TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY", "")
TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"

# API Endpoints
ENDPOINT_TIME_SERIES = f"{TWELVE_DATA_BASE_URL}/time_series"
ENDPOINT_QUOTE = f"{TWELVE_DATA_BASE_URL}/quote"
ENDPOINT_PRICE = f"{TWELVE_DATA_BASE_URL}/price"

# Rate Limits
MAX_CALLS_PER_DAY = 740  # Reserve 60 for emergencies (800 - 60)
MAX_CALLS_PER_MINUTE = 8
RATE_LIMIT_WINDOW = 60  # seconds

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
BACKOFF_MULTIPLIER = 2

# Timeouts
CONNECTION_TIMEOUT = 10  # seconds
READ_TIMEOUT = 30  # seconds

# Circuit Breaker Settings
CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening
CIRCUIT_BREAKER_TIMEOUT = 300  # seconds (5 min)
CIRCUIT_BREAKER_HALF_OPEN_CALLS = 3  # test calls in half-open state


def validate_api_config():
    """Validate API configuration"""
    if not TWELVE_DATA_KEY:
        raise ValueError("TWELVE_DATA_KEY not found in environment variables")
    return True


if __name__ == "__main__":
    try:
        validate_api_config()
        print("✅ API configuration valid")
        print(f"API Key: {TWELVE_DATA_KEY[:10]}...")
    except ValueError as e:
        print(f"❌ {e}")
