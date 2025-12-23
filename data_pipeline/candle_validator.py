"""QUANTP1 v3.1 - Candle Validator (Anti-Repainting)"""
from datetime import datetime, timedelta
from typing import Dict, Any
from utils.logger_setup import get_logger
from config.trading_config import TIMEFRAME_MINUTES

logger = get_logger()


class CandleValidator:
    """Validate candles to prevent repainting"""
    
    @staticmethod
    def is_candle_closed(candle_time: datetime, current_time: datetime, timeframe_minutes: int = TIMEFRAME_MINUTES) -> bool:
        """
        Check if candle is fully closed
        
        Args:
            candle_time: Candle timestamp
            current_time: Current time
            timeframe_minutes: Timeframe in minutes
            
        Returns:
            bool: True if candle is closed
        """
        # Candle is closed if current time is past the candle's end time
        candle_end = candle_time + timedelta(minutes=timeframe_minutes)
        return current_time >= candle_end
    
    @staticmethod
    def parse_candle_time(time_str: str) -> datetime:
        """
        Parse candle datetime string
        
        Args:
            time_str: Datetime string from API
            
        Returns:
            datetime: Parsed datetime
        """
        try:
            # Handle different formats
            time_str = time_str.replace('Z', '+00:00')
            return datetime.fromisoformat(time_str)
        except ValueError as e:
            logger.error(f"Failed to parse candle time '{time_str}': {e}")
            raise
    
    @staticmethod
    def validate_closed_candle(candle: Dict[str, Any], current_time: datetime, timeframe_minutes: int = TIMEFRAME_MINUTES) -> bool:
        """
        Validate that candle is closed (anti-repainting)
        
        Args:
            candle: Candle dictionary
            current_time: Current time
            timeframe_minutes: Timeframe in minutes
            
        Returns:
            bool: True if candle is closed and valid
        """
        try:
            candle_time = CandleValidator.parse_candle_time(candle['datetime'])
            
            if not CandleValidator.is_candle_closed(candle_time, current_time, timeframe_minutes):
                logger.warning(f"Candle not yet closed: {candle['datetime']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Candle validation failed: {e}")
            return False
    
    @staticmethod
    def get_closed_candles(candles: list, current_time: datetime, timeframe_minutes: int = TIMEFRAME_MINUTES) -> list:
        """
        Filter only closed candles from list
        
        Args:
            candles: List of candle dictionaries
            current_time: Current time
            timeframe_minutes: Timeframe in minutes
            
        Returns:
            list: Filtered list of closed candles
        """
        closed_candles = []
        
        for candle in candles:
            if CandleValidator.validate_closed_candle(candle, current_time, timeframe_minutes):
                closed_candles.append(candle)
        
        logger.debug(f"Filtered {len(closed_candles)}/{len(candles)} closed candles")
        return closed_candles


if __name__ == "__main__":
    from datetime import timezone
    
    # Test candle validator
    current = datetime.now(timezone.utc)
    
    # Closed candle (1 hour ago)
    closed_time = current - timedelta(hours=1)
    closed_candle = {
        'datetime': closed_time.isoformat(),
        'open': '1.08400',
        'high': '1.08600',
        'low': '1.08300',
        'close': '1.08500',
        'volume': '1000'
    }
    
    # Open candle (current)
    open_candle = {
        'datetime': current.isoformat(),
        'open': '1.08500',
        'high': '1.08600',
        'low': '1.08400',
        'close': '1.08550',
        'volume': '500'
    }
    
    validator = CandleValidator()
    
    print("Testing candle validator:")
    print(f"  Closed candle valid: {validator.validate_closed_candle(closed_candle, current)}")
    print(f"  Open candle valid: {validator.validate_closed_candle(open_candle, current)}")
    
    candles = [closed_candle, open_candle]
    closed = validator.get_closed_candles(candles, current)
    print(f"  Closed candles: {len(closed)}/2")
    
    print("\n✅ Candle validator test completed")
