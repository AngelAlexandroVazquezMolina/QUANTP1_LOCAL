"""QUANTP1 v3.1 - ML Model Loader"""
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import json
from utils.logger_setup import get_logger
from config.ml_config import MODEL_PATH, MAX_MODEL_AGE_DAYS, MODEL_METADATA_FILE

logger = get_logger()


class ModelLoader:
    """Load and validate ML models"""
    
    def __init__(self, model_path: Path = MODEL_PATH):
        """
        Initialize model loader
        
        Args:
            model_path: Path to model file
        """
        self.model_path = model_path
        self.model = None
        self.metadata = None
    
    def load_model(self) -> Optional[Any]:
        """
        Load ML model from disk
        
        Returns:
            Model object or None
        """
        if not self.model_path.exists():
            logger.error(f"Model file not found: {self.model_path}")
            return None
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            
            # Load metadata if available
            self._load_metadata()
            
            # Validate model age
            if not self._validate_model_age():
                logger.warning(f"Model is older than {MAX_MODEL_AGE_DAYS} days, consider retraining")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    def _load_metadata(self):
        """Load model metadata"""
        metadata_path = MODEL_METADATA_FILE
        
        if not metadata_path.exists():
            logger.debug("No model metadata found")
            return
        
        try:
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            logger.debug(f"Model metadata loaded: {self.metadata}")
            
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
    
    def _validate_model_age(self) -> bool:
        """
        Validate model is not too old
        
        Returns:
            bool: True if model age is acceptable
        """
        if not self.metadata or 'trained_at' not in self.metadata:
            # If no metadata, check file modification time
            mod_time = datetime.fromtimestamp(self.model_path.stat().st_mtime)
            age_days = (datetime.now() - mod_time).days
        else:
            trained_at = datetime.fromisoformat(self.metadata['trained_at'])
            age_days = (datetime.now() - trained_at).days
        
        logger.info(f"Model age: {age_days} days")
        
        return age_days <= MAX_MODEL_AGE_DAYS
    
    def get_model(self) -> Optional[Any]:
        """Get loaded model"""
        return self.model
    
    def get_metadata(self) -> Optional[dict]:
        """Get model metadata"""
        return self.metadata
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None


if __name__ == "__main__":
    # Test model loader
    loader = ModelLoader()
    
    model = loader.load_model()
    if model:
        print("✅ Model loaded successfully")
        print(f"Model type: {type(model).__name__}")
        
        if loader.metadata:
            print(f"Metadata: {loader.metadata}")
    else:
        print("❌ Failed to load model")
        print("Run: python research/create_dummy_model.py")
