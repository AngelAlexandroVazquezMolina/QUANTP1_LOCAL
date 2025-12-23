"""QUANTP1 v3.1 - Trading Configuration"""
import pytz

# Trading Instrument
SYMBOL = "EUR/USD"
TWELVE_DATA_SYMBOL = "EUR/USD"  # Twelve Data format
TIMEFRAME = "15min"
TIMEFRAME_MINUTES = 15

# Trading Hours (UTC)
TRADING_START_HOUR = 9  # 09:00 UTC
TRADING_END_HOUR = 14   # 14:00 UTC
TIMEZONE = pytz.UTC

# Indicator Periods
MA_PERIOD = 20
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2.0
RSI_PERIOD = 14
ADX_PERIOD = 14

# Historical Data
LOOKBACK_PERIODS = 100  # Number of candles to fetch for calculations

# Signal Thresholds
Z_SCORE_LONG_THRESHOLD = -2.0
Z_SCORE_SHORT_THRESHOLD = 2.0
ADX_MAX_THRESHOLD = 30  # Max ADX for mean reversion
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60
ML_CONFIDENCE_THRESHOLD = 0.65  # 65% minimum

# Limit Order Settings
LIMIT_OFFSET_PIPS = 5  # Offset from current price for limit orders
PIP_VALUE = 0.0001  # For EURUSD

# Take Profit / Stop Loss (in pips)
DEFAULT_TP_PIPS = 40
DEFAULT_SL_PIPS = 20

# Risk/Reward Ratio
MIN_RISK_REWARD_RATIO = 1.5  # Minimum 1.5:1


def is_valid_trading_config():
    """Validate trading configuration"""
    if TRADING_END_HOUR <= TRADING_START_HOUR:
        return False
    if MIN_RISK_REWARD_RATIO < 1.0:
        return False
    return True


if __name__ == "__main__":
    if is_valid_trading_config():
        print("✅ Trading configuration valid")
        print(f"Symbol: {SYMBOL}")
        print(f"Timeframe: {TIMEFRAME}")
        print(f"Trading Hours: {TRADING_START_HOUR:02d}:00 - {TRADING_END_HOUR:02d}:00 UTC")
    else:
        print("❌ Invalid trading configuration")
