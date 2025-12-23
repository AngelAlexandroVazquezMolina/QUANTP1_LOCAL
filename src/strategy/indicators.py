"""QUANTP1 v3.1 - Technical Indicators"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from utils.logger_setup import get_logger
from config.trading_config import (
    MA_PERIOD,
    BOLLINGER_PERIOD,
    BOLLINGER_STD,
    RSI_PERIOD,
    ADX_PERIOD
)

logger = get_logger()


def calculate_z_score(prices: np.ndarray, period: int = MA_PERIOD) -> float:
    """
    Calculate Z-Score for mean reversion
    
    Args:
        prices: Array of prices
        period: Moving average period
        
    Returns:
        float: Z-Score value
    """
    if len(prices) < period:
        logger.warning(f"Insufficient data for Z-Score: {len(prices)} < {period}")
        return 0.0
    
    mean = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    
    if std == 0:
        return 0.0
    
    current_price = prices[-1]
    z_score = (current_price - mean) / std
    
    return z_score


def calculate_bollinger_bands(prices: np.ndarray, period: int = BOLLINGER_PERIOD, std_dev: float = BOLLINGER_STD) -> Dict[str, float]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Array of prices
        period: Period for moving average
        std_dev: Standard deviation multiplier
        
    Returns:
        dict: Upper, middle, lower bands and metrics
    """
    if len(prices) < period:
        logger.warning(f"Insufficient data for Bollinger Bands: {len(prices)} < {period}")
        return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0, 'percent_b': 0}
    
    middle = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    # Width (normalized)
    width = (upper - lower) / middle if middle != 0 else 0
    
    # %B indicator (position within bands)
    current_price = prices[-1]
    if upper != lower:
        percent_b = (current_price - lower) / (upper - lower)
    else:
        percent_b = 0.5
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower,
        'width': width,
        'percent_b': percent_b
    }


def calculate_rsi(prices: np.ndarray, period: int = RSI_PERIOD) -> float:
    """
    Calculate RSI (Relative Strength Index)
    
    Args:
        prices: Array of prices
        period: RSI period
        
    Returns:
        float: RSI value (0-100)
    """
    if len(prices) < period + 1:
        logger.warning(f"Insufficient data for RSI: {len(prices)} < {period + 1}")
        return 50.0
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gain and loss
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_adx(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ADX_PERIOD) -> float:
    """
    Calculate ADX (Average Directional Index)
    
    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of close prices
        period: ADX period
        
    Returns:
        float: ADX value (0-100)
    """
    if len(high) < period + 1:
        logger.warning(f"Insufficient data for ADX: {len(high)} < {period + 1}")
        return 0.0
    
    # Calculate True Range
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    
    # Calculate Directional Movement
    dm_plus = np.where((high[1:] - high[:-1]) > (low[:-1] - low[1:]), 
                       np.maximum(high[1:] - high[:-1], 0), 0)
    dm_minus = np.where((low[:-1] - low[1:]) > (high[1:] - high[:-1]), 
                        np.maximum(low[:-1] - low[1:], 0), 0)
    
    # Smooth with EMA
    tr_smooth = pd.Series(tr).ewm(span=period, adjust=False).mean().values
    dm_plus_smooth = pd.Series(dm_plus).ewm(span=period, adjust=False).mean().values
    dm_minus_smooth = pd.Series(dm_minus).ewm(span=period, adjust=False).mean().values
    
    # Calculate DI
    di_plus = 100 * dm_plus_smooth / tr_smooth
    di_minus = 100 * dm_minus_smooth / tr_smooth
    
    # Calculate DX
    dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
    
    # Calculate ADX
    adx = pd.Series(dx).ewm(span=period, adjust=False).mean().values[-1]
    
    return adx


def calculate_all_indicators(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate all indicators from candle data
    
    Args:
        candles: List of candle dictionaries
        
    Returns:
        dict: All calculated indicators
    """
    if not candles or len(candles) < 20:
        logger.error(f"Insufficient candles for indicators: {len(candles) if candles else 0}")
        return None
    
    # Convert to arrays
    closes = np.array([float(c['close']) for c in candles])
    highs = np.array([float(c['high']) for c in candles])
    lows = np.array([float(c['low']) for c in candles])
    
    # Calculate indicators
    z_score = calculate_z_score(closes)
    bollinger = calculate_bollinger_bands(closes)
    rsi = calculate_rsi(closes)
    adx = calculate_adx(highs, lows, closes)
    
    indicators = {
        'z_score': z_score,
        'rsi': rsi,
        'adx': adx,
        'bb_upper': bollinger['upper'],
        'bb_middle': bollinger['middle'],
        'bb_lower': bollinger['lower'],
        'bb_width': bollinger['width'],
        'bb_percent_b': bollinger['percent_b'],
        'current_price': closes[-1]
    }
    
    logger.debug(f"Indicators: Z={z_score:.2f}, RSI={rsi:.2f}, ADX={adx:.2f}")
    
    return indicators


if __name__ == "__main__":
    # Test indicators with sample data
    np.random.seed(42)
    prices = 1.08 + np.random.randn(100) * 0.001
    
    print("Testing indicators...\n")
    
    z = calculate_z_score(prices)
    print(f"Z-Score: {z:.4f}")
    
    bb = calculate_bollinger_bands(prices)
    print(f"\nBollinger Bands:")
    print(f"  Upper: {bb['upper']:.5f}")
    print(f"  Middle: {bb['middle']:.5f}")
    print(f"  Lower: {bb['lower']:.5f}")
    print(f"  Width: {bb['width']:.5f}")
    print(f"  %B: {bb['percent_b']:.3f}")
    
    rsi = calculate_rsi(prices)
    print(f"\nRSI: {rsi:.2f}")
    
    highs = prices + 0.0005
    lows = prices - 0.0005
    adx = calculate_adx(highs, lows, prices)
    print(f"ADX: {adx:.2f}")
    
    print("\n✅ Indicators test completed")
