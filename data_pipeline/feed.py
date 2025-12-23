"""QUANTP1 v3.1 - Data Feed Orchestrator"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.logger_setup import get_logger
from data_pipeline.api_client.twelve_data_client import TwelveDataClient
from data_pipeline.api_client.response_validator import ResponseValidator
from data_pipeline.candle_validator import CandleValidator
from core.api_circuit_breaker import APICircuitBreaker
from config.trading_config import TWELVE_DATA_SYMBOL, TIMEFRAME, LOOKBACK_PERIODS

logger = get_logger()


class DataFeed:
    """Main data feed orchestrator"""
    
    def __init__(self, circuit_breaker: Optional[APICircuitBreaker] = None):
        """
        Initialize data feed
        
        Args:
            circuit_breaker: Optional circuit breaker instance
        """
        self.client = TwelveDataClient()
        self.validator = ResponseValidator()
        self.candle_validator = CandleValidator()
        self.circuit_breaker = circuit_breaker or APICircuitBreaker()
    
    def get_current_price(self, symbol: str = TWELVE_DATA_SYMBOL) -> Optional[float]:
        """
        Get current market price
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Current price or None
        """
        # Check circuit breaker
        allowed, reason = self.circuit_breaker.can_make_call()
        if not allowed:
            logger.error(f"API call blocked: {reason}")
            return None
        
        try:
            # Make API call
            self.circuit_breaker.record_call()
            price_data = self.client.get_price(symbol)
            
            if price_data is None:
                self.circuit_breaker.record_failure("Price data is None")
                return None
            
            # Validate response
            if not self.validator.validate_price({'price': str(price_data)}):
                self.circuit_breaker.record_failure("Price validation failed")
                return None
            
            self.circuit_breaker.record_success()
            return price_data
            
        except Exception as e:
            logger.error(f"Failed to get current price: {e}")
            self.circuit_breaker.record_failure(str(e))
            return None
    
    def get_historical_candles(
        self,
        symbol: str = TWELVE_DATA_SYMBOL,
        interval: str = TIMEFRAME,
        count: int = LOOKBACK_PERIODS
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical candles (only closed candles)
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            count: Number of candles
            
        Returns:
            list: List of closed candles or None
        """
        # Check circuit breaker
        allowed, reason = self.circuit_breaker.can_make_call()
        if not allowed:
            logger.error(f"API call blocked: {reason}")
            return None
        
        try:
            # Make API call
            self.circuit_breaker.record_call()
            candles = self.client.get_time_series(symbol, interval, count)
            
            if candles is None:
                self.circuit_breaker.record_failure("Candles data is None")
                return None
            
            # Validate response
            if not self.validator.validate_time_series(candles):
                self.circuit_breaker.record_failure("Candles validation failed")
                return None
            
            # Filter only closed candles (anti-repainting)
            current_time = datetime.utcnow()
            closed_candles = self.candle_validator.get_closed_candles(candles, current_time)
            
            if not closed_candles:
                logger.warning("No closed candles available")
                self.circuit_breaker.record_failure("No closed candles")
                return None
            
            self.circuit_breaker.record_success()
            return closed_candles
            
        except Exception as e:
            logger.error(f"Failed to get historical candles: {e}")
            self.circuit_breaker.record_failure(str(e))
            return None
    
    def get_market_data(self) -> Optional[Dict[str, Any]]:
        """
        Get complete market data (price + candles)
        
        Returns:
            dict: Market data or None
        """
        price = self.get_current_price()
        if price is None:
            return None
        
        candles = self.get_historical_candles()
        if candles is None:
            return None
        
        return {
            'current_price': price,
            'candles': candles,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def close(self):
        """Close client connection"""
        self.client.close()


if __name__ == "__main__":
    # Test data feed
    feed = DataFeed()
    
    print("Testing data feed...\n")
    
    # Get price
    price = feed.get_current_price()
    if price:
        print(f"Current Price: {price}")
    
    # Get candles
    candles = feed.get_historical_candles(count=5)
    if candles:
        print(f"\nFetched {len(candles)} closed candles")
        print("Latest candle:")
        print(f"  {candles[0]}")
    
    # Get full market data
    data = feed.get_market_data()
    if data:
        print(f"\nMarket Data:")
        print(f"  Price: {data['current_price']}")
        print(f"  Candles: {len(data['candles'])}")
        print(f"  Timestamp: {data['timestamp']}")
    
    feed.close()
    print("\n✅ Data feed test completed")
