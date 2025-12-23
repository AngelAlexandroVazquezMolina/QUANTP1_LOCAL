"""QUANTP1 v3.1 - Risk Management Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# Account Settings
ACCOUNT_SIZE = float(os.getenv("ACCOUNT_SIZE", "5000"))
STARTING_BALANCE = ACCOUNT_SIZE  # Reset daily

# Prop Firm Rules
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", "0.05"))  # 5%
MAX_LOSS_PER_TRADE = float(os.getenv("MAX_LOSS_PER_TRADE", "250"))  # $250

# Risk per Trade
DEFAULT_RISK_PCT = 0.02  # 2% of account per trade
MIN_RISK_PCT = 0.01  # 1% minimum
MAX_RISK_PCT = 0.03  # 3% maximum

# Position Sizing
MIN_LOT_SIZE = 0.01
MAX_LOT_SIZE = 1.0
LOT_SIZE_STEP = 0.01

# Safety Buffers
RISK_BUFFER_PCT = 0.20  # 20% buffer on daily loss limit
EMERGENCY_STOP_PCT = 0.90  # Stop all trading at 90% of daily limit

# Maximum Open Positions
MAX_OPEN_POSITIONS = 3
MAX_DAILY_TRADES = 10

# Calculations
MAX_DAILY_LOSS_AMOUNT = ACCOUNT_SIZE * MAX_DAILY_LOSS_PCT
RISK_BUFFER_AMOUNT = MAX_DAILY_LOSS_AMOUNT * RISK_BUFFER_PCT
EMERGENCY_STOP_AMOUNT = MAX_DAILY_LOSS_AMOUNT * EMERGENCY_STOP_PCT


def validate_risk_config():
    """Validate risk configuration"""
    if ACCOUNT_SIZE <= 0:
        raise ValueError("ACCOUNT_SIZE must be positive")
    if MAX_DAILY_LOSS_PCT <= 0 or MAX_DAILY_LOSS_PCT > 0.1:
        raise ValueError("MAX_DAILY_LOSS_PCT must be between 0 and 0.1")
    if MAX_LOSS_PER_TRADE <= 0:
        raise ValueError("MAX_LOSS_PER_TRADE must be positive")
    if MAX_LOSS_PER_TRADE > MAX_DAILY_LOSS_AMOUNT:
        raise ValueError("MAX_LOSS_PER_TRADE cannot exceed MAX_DAILY_LOSS_AMOUNT")
    return True


if __name__ == "__main__":
    try:
        validate_risk_config()
        print("✅ Risk configuration valid")
        print(f"Account Size: ${ACCOUNT_SIZE:,.2f}")
        print(f"Max Daily Loss: ${MAX_DAILY_LOSS_AMOUNT:,.2f} ({MAX_DAILY_LOSS_PCT*100}%)")
        print(f"Max Loss per Trade: ${MAX_LOSS_PER_TRADE:,.2f}")
    except ValueError as e:
        print(f"❌ {e}")
