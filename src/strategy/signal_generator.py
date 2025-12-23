"""QUANTP1 v3.1 - Signal Generator"""
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger_setup import get_logger
from config.trading_config import (
    Z_SCORE_LONG_THRESHOLD,
    Z_SCORE_SHORT_THRESHOLD,
    ADX_MAX_THRESHOLD,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
    ML_CONFIDENCE_THRESHOLD
)

logger = get_logger()


class SignalGenerator:
    """Generate trading signals based on strategy rules"""
    
    def __init__(self):
        """Initialize signal generator"""
        self.last_signal_id = 0
    
    def generate_signal(
        self,
        indicators: Dict[str, Any],
        ml_prediction: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate trading signal based on indicators and ML
        
        Strategy Rules:
        - LONG: Z-Score <= -2.0 AND ADX < 30 AND RSI < 40 AND ML confidence >= 65%
        - SHORT: Z-Score >= 2.0 AND ADX < 30 AND RSI > 60 AND ML confidence >= 65%
        
        Args:
            indicators: Technical indicators
            ml_prediction: ML prediction (optional)
            
        Returns:
            dict: Signal data or None
        """
        if not indicators:
            logger.warning("No indicators provided")
            return None
        
        z_score = indicators.get('z_score', 0)
        adx = indicators.get('adx', 100)
        rsi = indicators.get('rsi', 50)
        current_price = indicators.get('current_price', 0)
        
        # Check ML confidence (if available)
        ml_confidence = 0.0
        ml_direction = None
        if ml_prediction:
            ml_confidence = ml_prediction.get('confidence', 0.0)
            ml_direction = ml_prediction.get('direction', None)
        
        logger.debug(f"Signal check: Z={z_score:.2f}, ADX={adx:.2f}, RSI={rsi:.2f}, ML={ml_confidence:.2%}")
        
        # Check LONG conditions
        if (z_score <= Z_SCORE_LONG_THRESHOLD and
            adx < ADX_MAX_THRESHOLD and
            rsi < RSI_OVERSOLD and
            ml_confidence >= ML_CONFIDENCE_THRESHOLD and
            (ml_direction == 'LONG' or ml_direction is None)):
            
            self.last_signal_id += 1
            signal = {
                'signal_id': self.last_signal_id,
                'direction': 'LONG',
                'timestamp': datetime.utcnow().isoformat(),
                'entry_price': current_price,
                'indicators': {
                    'z_score': z_score,
                    'adx': adx,
                    'rsi': rsi
                },
                'ml_confidence': ml_confidence,
                'reason': f"Mean reversion LONG: Z={z_score:.2f}, ADX={adx:.1f}, RSI={rsi:.1f}, ML={ml_confidence:.1%}"
            }
            
            logger.info(f"🎯 LONG signal generated: {signal['reason']}")
            return signal
        
        # Check SHORT conditions
        if (z_score >= Z_SCORE_SHORT_THRESHOLD and
            adx < ADX_MAX_THRESHOLD and
            rsi > RSI_OVERBOUGHT and
            ml_confidence >= ML_CONFIDENCE_THRESHOLD and
            (ml_direction == 'SHORT' or ml_direction is None)):
            
            self.last_signal_id += 1
            signal = {
                'signal_id': self.last_signal_id,
                'direction': 'SHORT',
                'timestamp': datetime.utcnow().isoformat(),
                'entry_price': current_price,
                'indicators': {
                    'z_score': z_score,
                    'adx': adx,
                    'rsi': rsi
                },
                'ml_confidence': ml_confidence,
                'reason': f"Mean reversion SHORT: Z={z_score:.2f}, ADX={adx:.1f}, RSI={rsi:.1f}, ML={ml_confidence:.1%}"
            }
            
            logger.info(f"🎯 SHORT signal generated: {signal['reason']}")
            return signal
        
        # No signal
        logger.debug("No signal conditions met")
        return None
    
    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate signal before processing
        
        Args:
            signal: Signal dictionary
            
        Returns:
            bool: True if valid
        """
        required_fields = ['signal_id', 'direction', 'entry_price', 'ml_confidence']
        
        for field in required_fields:
            if field not in signal:
                logger.error(f"Signal missing required field: {field}")
                return False
        
        if signal['direction'] not in ['LONG', 'SHORT']:
            logger.error(f"Invalid signal direction: {signal['direction']}")
            return False
        
        if signal['entry_price'] <= 0:
            logger.error(f"Invalid entry price: {signal['entry_price']}")
            return False
        
        return True


if __name__ == "__main__":
    # Test signal generator
    generator = SignalGenerator()
    
    # Test LONG signal
    long_indicators = {
        'z_score': -2.5,
        'adx': 25,
        'rsi': 35,
        'current_price': 1.08400
    }
    long_ml = {
        'confidence': 0.72,
        'direction': 'LONG'
    }
    
    print("Testing LONG signal:")
    signal = generator.generate_signal(long_indicators, long_ml)
    if signal:
        print(f"  Direction: {signal['direction']}")
        print(f"  Confidence: {signal['ml_confidence']:.1%}")
        print(f"  Reason: {signal['reason']}")
    
    # Test SHORT signal
    short_indicators = {
        'z_score': 2.3,
        'adx': 22,
        'rsi': 65,
        'current_price': 1.08600
    }
    short_ml = {
        'confidence': 0.68,
        'direction': 'SHORT'
    }
    
    print("\nTesting SHORT signal:")
    signal = generator.generate_signal(short_indicators, short_ml)
    if signal:
        print(f"  Direction: {signal['direction']}")
        print(f"  Confidence: {signal['ml_confidence']:.1%}")
        print(f"  Reason: {signal['reason']}")
    
    # Test no signal
    no_signal_indicators = {
        'z_score': 0.5,
        'adx': 45,
        'rsi': 50,
        'current_price': 1.08500
    }
    
    print("\nTesting no signal conditions:")
    signal = generator.generate_signal(no_signal_indicators, long_ml)
    print(f"  Signal: {signal}")
    
    print("\n✅ Signal generator test completed")
