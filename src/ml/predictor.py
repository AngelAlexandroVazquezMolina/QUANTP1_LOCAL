"""QUANTP1 v3.1 - ML Predictor"""
from typing import Dict, Any, Optional
import numpy as np
from utils.logger_setup import get_logger
from src.ml.model_loader import ModelLoader
from src.ml.feature_engineer import FeatureEngineer
from config.ml_config import MIN_CONFIDENCE_THRESHOLD

logger = get_logger()


class Predictor:
    """Make predictions using ML model"""
    
    def __init__(self):
        """Initialize predictor"""
        self.loader = ModelLoader()
        self.engineer = FeatureEngineer()
        self.model = None
    
    def load(self) -> bool:
        """
        Load ML model
        
        Returns:
            bool: True if successful
        """
        self.model = self.loader.load_model()
        return self.model is not None
    
    def predict(self, indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make prediction
        
        Args:
            indicators: Technical indicators
            
        Returns:
            dict: Prediction with confidence and direction, or None
        """
        if self.model is None:
            logger.error("Model not loaded")
            return None
        
        try:
            # Prepare features
            features = self.engineer.prepare_features(indicators)
            
            # Validate features
            if not self.engineer.validate_features(features):
                logger.error("Feature validation failed")
                return None
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Get confidence (max probability)
            confidence = float(np.max(probabilities))
            
            # Determine direction (0 = SHORT, 1 = LONG)
            direction = 'LONG' if prediction == 1 else 'SHORT'
            
            result = {
                'direction': direction,
                'confidence': confidence,
                'probabilities': {
                    'SHORT': float(probabilities[0]),
                    'LONG': float(probabilities[1])
                },
                'meets_threshold': confidence >= MIN_CONFIDENCE_THRESHOLD
            }
            
            logger.info(f"ML Prediction: {direction} ({confidence:.1%} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None
    
    def is_ready(self) -> bool:
        """Check if predictor is ready"""
        return self.model is not None


if __name__ == "__main__":
    # Test predictor
    predictor = Predictor()
    
    print("Loading model...")
    if not predictor.load():
        print("❌ Failed to load model")
        print("Run: python research/create_dummy_model.py")
        exit(1)
    
    print("✅ Model loaded\n")
    
    # Test LONG scenario
    long_indicators = {
        'z_score': -2.5,
        'adx': 25,
        'rsi': 35,
        'bb_width': 0.02,
        'bb_percent_b': 0.15
    }
    
    print("Testing LONG scenario:")
    prediction = predictor.predict(long_indicators)
    if prediction:
        print(f"  Direction: {prediction['direction']}")
        print(f"  Confidence: {prediction['confidence']:.1%}")
        print(f"  Meets threshold: {prediction['meets_threshold']}")
        print(f"  Probabilities: {prediction['probabilities']}")
    
    # Test SHORT scenario
    short_indicators = {
        'z_score': 2.3,
        'adx': 22,
        'rsi': 65,
        'bb_width': 0.018,
        'bb_percent_b': 0.85
    }
    
    print("\nTesting SHORT scenario:")
    prediction = predictor.predict(short_indicators)
    if prediction:
        print(f"  Direction: {prediction['direction']}")
        print(f"  Confidence: {prediction['confidence']:.1%}")
        print(f"  Meets threshold: {prediction['meets_threshold']}")
        print(f"  Probabilities: {prediction['probabilities']}")
    
    print("\n✅ Predictor test completed")
