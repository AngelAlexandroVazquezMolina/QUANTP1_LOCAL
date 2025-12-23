"""QUANTP1 v3.1 - API Response Validator"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger_setup import get_logger

logger = get_logger()


class ResponseValidator:
    """Validate API responses for completeness and correctness"""
    
    @staticmethod
    def validate_price(data: Any) -> bool:
        """
        Validate price response
        
        Args:
            data: API response data
            
        Returns:
            bool: True if valid
        """
        try:
            if not isinstance(data, dict):
                return False
            
            if 'price' not in data:
                logger.error("Price field missing from response")
                return False
            
            price = float(data['price'])
            if price <= 0:
                logger.error(f"Invalid price: {price}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Price validation failed: {e}")
            return False
    
    @staticmethod
    def validate_quote(data: Dict[str, Any]) -> bool:
        """
        Validate quote response
        
        Args:
            data: Quote data
            
        Returns:
            bool: True if valid
        """
        required_fields = ['symbol', 'open', 'high', 'low', 'close', 'volume']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Required field '{field}' missing from quote")
                return False
        
        try:
            # Validate numeric fields
            open_price = float(data['open'])
            high = float(data['high'])
            low = float(data['low'])
            close = float(data['close'])
            volume = float(data['volume'])
            
            # Basic sanity checks
            if not (low <= open_price <= high):
                logger.error(f"Invalid OHLC: open={open_price} not in range [{low}, {high}]")
                return False
            
            if not (low <= close <= high):
                logger.error(f"Invalid OHLC: close={close} not in range [{low}, {high}]")
                return False
            
            if volume < 0:
                logger.error(f"Invalid volume: {volume}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Quote validation failed: {e}")
            return False
    
    @staticmethod
    def validate_candle(candle: Dict[str, Any]) -> bool:
        """
        Validate single candle data
        
        Args:
            candle: Candle dictionary
            
        Returns:
            bool: True if valid
        """
        required_fields = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        
        for field in required_fields:
            if field not in candle:
                logger.error(f"Required field '{field}' missing from candle")
                return False
        
        try:
            # Validate OHLC
            open_price = float(candle['open'])
            high = float(candle['high'])
            low = float(candle['low'])
            close = float(candle['close'])
            volume = float(candle['volume'])
            
            # Validate datetime
            datetime.fromisoformat(candle['datetime'].replace('Z', '+00:00'))
            
            # OHLC sanity checks
            if high < low:
                logger.error(f"Invalid candle: high={high} < low={low}")
                return False
            
            if not (low <= open_price <= high):
                logger.error(f"Invalid candle: open={open_price} not in range [{low}, {high}]")
                return False
            
            if not (low <= close <= high):
                logger.error(f"Invalid candle: close={close} not in range [{low}, {high}]")
                return False
            
            if volume < 0:
                logger.error(f"Invalid volume: {volume}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Candle validation failed: {e}")
            return False
    
    @staticmethod
    def validate_time_series(candles: List[Dict[str, Any]]) -> bool:
        """
        Validate time series data
        
        Args:
            candles: List of candle dictionaries
            
        Returns:
            bool: True if valid
        """
        if not isinstance(candles, list):
            logger.error("Time series is not a list")
            return False
        
        if len(candles) == 0:
            logger.error("Time series is empty")
            return False
        
        # Validate each candle
        for i, candle in enumerate(candles):
            if not ResponseValidator.validate_candle(candle):
                logger.error(f"Candle {i} validation failed")
                return False
        
        return True


if __name__ == "__main__":
    # Test validator
    validator = ResponseValidator()
    
    # Test price
    valid_price = {'price': '1.08500'}
    invalid_price = {'price': '-1.0'}
    
    print("Testing price validation:")
    print(f"  Valid price: {validator.validate_price(valid_price)}")
    print(f"  Invalid price: {validator.validate_price(invalid_price)}")
    
    # Test candle
    valid_candle = {
        'datetime': '2023-12-23 10:00:00',
        'open': '1.08400',
        'high': '1.08600',
        'low': '1.08300',
        'close': '1.08500',
        'volume': '1000'
    }
    
    print("\nTesting candle validation:")
    print(f"  Valid candle: {validator.validate_candle(valid_candle)}")
    
    print("\n✅ Response validator test completed")
