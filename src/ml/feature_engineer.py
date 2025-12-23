"""QUANTP1 v3.1 - Feature Engineer"""
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from utils.logger_setup import get_logger
from config.ml_config import FEATURE_NAMES, NUM_FEATURES

logger = get_logger()


class FeatureEngineer:
    """Prepare features for ML model"""
    
    @staticmethod
    def prepare_features(indicators: Dict[str, Any], timestamp: datetime = None) -> np.ndarray:
        """
        Prepare feature vector for ML model
        
        Features: z_score, adx, rsi, bb_width, bb_percent_b, hour, day_of_week
        
        Args:
            indicators: Dictionary of technical indicators
            timestamp: Timestamp for time features (default: now)
            
        Returns:
            np.ndarray: Feature vector
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        features = []
        
        # Technical indicators
        features.append(indicators.get('z_score', 0.0))
        features.append(indicators.get('adx', 0.0))
        features.append(indicators.get('rsi', 50.0))
        features.append(indicators.get('bb_width', 0.0))
        features.append(indicators.get('bb_percent_b', 0.5))
        
        # Time features
        features.append(timestamp.hour)
        features.append(timestamp.weekday())
        
        feature_array = np.array(features).reshape(1, -1)
        
        logger.debug(f"Features prepared: {FEATURE_NAMES}")
        logger.debug(f"Values: {features}")
        
        return feature_array
    
    @staticmethod
    def validate_features(features: np.ndarray) -> bool:
        """
        Validate feature vector
        
        Args:
            features: Feature array
            
        Returns:
            bool: True if valid
        """
        if features.shape[1] != NUM_FEATURES:
            logger.error(f"Invalid feature count: {features.shape[1]} (expected {NUM_FEATURES})")
            return False
        
        # Check for NaN or Inf
        if np.isnan(features).any():
            logger.error("Features contain NaN values")
            return False
        
        if np.isinf(features).any():
            logger.error("Features contain Inf values")
            return False
        
        return True
    
    @staticmethod
    def get_feature_names() -> List[str]:
        """Get list of feature names"""
        return FEATURE_NAMES.copy()


if __name__ == "__main__":
    # Test feature engineer
    engineer = FeatureEngineer()
    
    # Sample indicators
    indicators = {
        'z_score': -2.3,
        'adx': 25.5,
        'rsi': 38.2,
        'bb_width': 0.015,
        'bb_percent_b': 0.2
    }
    
    print("Testing feature engineering...\n")
    
    features = engineer.prepare_features(indicators)
    print(f"Feature shape: {features.shape}")
    print(f"Features: {features[0]}")
    
    is_valid = engineer.validate_features(features)
    print(f"\nFeatures valid: {is_valid}")
    
    print(f"\nFeature names:")
    for i, name in enumerate(engineer.get_feature_names()):
        print(f"  {i}: {name} = {features[0][i]}")
    
    print("\n✅ Feature engineer test completed")
