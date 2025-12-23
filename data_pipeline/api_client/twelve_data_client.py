"""QUANTP1 v3.1 - Twelve Data API Client"""
import requests
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from utils.logger_setup import get_logger
from config.api_config import (
    TWELVE_DATA_KEY,
    ENDPOINT_TIME_SERIES,
    ENDPOINT_QUOTE,
    ENDPOINT_PRICE,
    MAX_RETRIES,
    RETRY_DELAY,
    BACKOFF_MULTIPLIER,
    CONNECTION_TIMEOUT,
    READ_TIMEOUT
)

logger = get_logger()


class TwelveDataClient:
    """Client for Twelve Data API with rate limiting and retry logic"""
    
    def __init__(self, api_key: str = TWELVE_DATA_KEY):
        """
        Initialize API client
        
        Args:
            api_key: Twelve Data API key
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QUANTP1/3.1',
            'Accept': 'application/json'
        })
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            dict: API response
        """
        params['apikey'] = self.api_key
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    wait_time = RETRY_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                # Check for API errors
                if 'code' in data and data['code'] != 200:
                    raise ValueError(f"API error: {data.get('message', 'Unknown error')}")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (BACKOFF_MULTIPLIER ** attempt))
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for symbol
        
        Args:
            symbol: Trading symbol (e.g., "EUR/USD")
            
        Returns:
            float: Current price or None
        """
        try:
            params = {'symbol': symbol}
            data = self._make_request(ENDPOINT_PRICE, params)
            
            price = float(data.get('price', 0))
            logger.debug(f"Price fetched for {symbol}: {price}")
            return price
            
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed quote for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: Quote data or None
        """
        try:
            params = {'symbol': symbol}
            data = self._make_request(ENDPOINT_QUOTE, params)
            
            logger.debug(f"Quote fetched for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return None
    
    def get_time_series(
        self,
        symbol: str,
        interval: str = "15min",
        outputsize: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical time series data
        
        Args:
            symbol: Trading symbol
            interval: Time interval (e.g., "15min")
            outputsize: Number of candles to fetch
            
        Returns:
            list: List of candle dictionaries or None
        """
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize
            }
            data = self._make_request(ENDPOINT_TIME_SERIES, params)
            
            if 'values' not in data:
                logger.error(f"No values in time series response: {data}")
                return None
            
            candles = data['values']
            logger.info(f"Fetched {len(candles)} candles for {symbol} ({interval})")
            return candles
            
        except Exception as e:
            logger.error(f"Failed to get time series for {symbol}: {e}")
            return None
    
    def close(self):
        """Close session"""
        self.session.close()


if __name__ == "__main__":
    # Test API client
    client = TwelveDataClient()
    
    print("Testing Twelve Data API...\n")
    
    # Test price
    price = client.get_price("EUR/USD")
    if price:
        print(f"EUR/USD Price: {price}")
    
    # Test quote
    quote = client.get_quote("EUR/USD")
    if quote:
        print(f"\nQuote:")
        for key, value in list(quote.items())[:5]:
            print(f"  {key}: {value}")
    
    # Test time series
    candles = client.get_time_series("EUR/USD", "15min", 5)
    if candles:
        print(f"\nLatest 3 candles:")
        for candle in candles[:3]:
            print(f"  {candle['datetime']}: O={candle['open']}, C={candle['close']}")
    
    client.close()
    print("\n✅ API client test completed")
