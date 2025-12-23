"""QUANTP1 v3.1 - Time Utilities"""
from datetime import datetime, time, timedelta
import pytz
from config.trading_config import TRADING_START_HOUR, TRADING_END_HOUR, TIMEZONE, TIMEFRAME_MINUTES


def get_current_time(timezone=TIMEZONE):
    """Get current time in specified timezone"""
    return datetime.now(timezone)


def is_trading_time(current_time=None):
    """
    Check if current time is within trading hours
    
    Args:
        current_time: Optional datetime to check, defaults to now
        
    Returns:
        bool: True if within trading hours
    """
    if current_time is None:
        current_time = get_current_time()
    
    # Ensure timezone aware
    if current_time.tzinfo is None:
        current_time = TIMEZONE.localize(current_time)
    else:
        current_time = current_time.astimezone(TIMEZONE)
    
    trading_start = time(TRADING_START_HOUR, 0)
    trading_end = time(TRADING_END_HOUR, 0)
    current_time_only = current_time.time()
    
    # Check if we're in trading window
    is_trading = trading_start <= current_time_only < trading_end
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = current_time.weekday() < 5
    
    return is_trading and is_weekday


def seconds_until_trading_start(current_time=None):
    """
    Calculate seconds until trading starts
    
    Args:
        current_time: Optional datetime to check, defaults to now
        
    Returns:
        int: Seconds until trading starts, 0 if already trading
    """
    if current_time is None:
        current_time = get_current_time()
    
    # Ensure timezone aware
    if current_time.tzinfo is None:
        current_time = TIMEZONE.localize(current_time)
    else:
        current_time = current_time.astimezone(TIMEZONE)
    
    # If already trading time, return 0
    if is_trading_time(current_time):
        return 0
    
    # Calculate next trading start
    trading_start = current_time.replace(
        hour=TRADING_START_HOUR,
        minute=0,
        second=0,
        microsecond=0
    )
    
    # If past trading start today, move to tomorrow
    if current_time.time() >= time(TRADING_START_HOUR, 0):
        trading_start += timedelta(days=1)
    
    # Skip weekend
    while trading_start.weekday() >= 5:  # Saturday or Sunday
        trading_start += timedelta(days=1)
    
    delta = trading_start - current_time
    return int(delta.total_seconds())


def is_candle_time(timeframe_minutes=TIMEFRAME_MINUTES, current_time=None):
    """
    Check if current time aligns with candle close time
    
    Args:
        timeframe_minutes: Timeframe in minutes
        current_time: Optional datetime to check, defaults to now
        
    Returns:
        bool: True if it's candle close time
    """
    if current_time is None:
        current_time = get_current_time()
    
    # Check if minutes align with timeframe
    return current_time.minute % timeframe_minutes == 0


def get_next_candle_time(timeframe_minutes=TIMEFRAME_MINUTES, current_time=None):
    """
    Get the time of the next candle close
    
    Args:
        timeframe_minutes: Timeframe in minutes
        current_time: Optional datetime to check, defaults to now
        
    Returns:
        datetime: Next candle close time
    """
    if current_time is None:
        current_time = get_current_time()
    
    # Calculate minutes until next candle
    current_minutes = current_time.minute
    minutes_in_current_candle = current_minutes % timeframe_minutes
    minutes_until_next = timeframe_minutes - minutes_in_current_candle
    
    next_candle = current_time + timedelta(minutes=minutes_until_next)
    next_candle = next_candle.replace(second=0, microsecond=0)
    
    return next_candle


def format_time_remaining(seconds):
    """
    Format seconds into human-readable string
    
    Args:
        seconds: Number of seconds
        
    Returns:
        str: Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 0:
        return "Now"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


if __name__ == "__main__":
    now = get_current_time()
    print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Is Trading Time: {is_trading_time()}")
    print(f"Seconds Until Trading: {seconds_until_trading_start()}")
    print(f"Time Until Trading: {format_time_remaining(seconds_until_trading_start())}")
    print(f"Is Candle Time: {is_candle_time()}")
    print(f"Next Candle: {get_next_candle_time().strftime('%Y-%m-%d %H:%M:%S')}")
