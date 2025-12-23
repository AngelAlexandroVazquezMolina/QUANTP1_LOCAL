"""QUANTP1 v3.1 - Create Dummy ML Model"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pickle
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from config.paths_config import DEFAULT_MODEL_FILE, MODEL_METADATA_FILE
from config.ml_config import FEATURE_NAMES, MODEL_PARAMS


def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic training data
    
    Returns:
        X: Features
        y: Labels (0=SHORT, 1=LONG)
    """
    print(f"Generating {n_samples} synthetic samples...")
    
    np.random.seed(42)
    
    # Generate features
    z_score = np.random.randn(n_samples) * 2  # Mean 0, std 2
    adx = np.random.uniform(10, 50, n_samples)
    rsi = np.random.uniform(20, 80, n_samples)
    bb_width = np.random.uniform(0.01, 0.03, n_samples)
    bb_percent_b = np.random.uniform(0, 1, n_samples)
    hour = np.random.randint(0, 24, n_samples)
    day_of_week = np.random.randint(0, 7, n_samples)
    
    X = np.column_stack([
        z_score,
        adx,
        rsi,
        bb_width,
        bb_percent_b,
        hour,
        day_of_week
    ])
    
    # Generate labels based on strategy rules (with noise)
    y = np.zeros(n_samples)
    
    for i in range(n_samples):
        # LONG conditions (with 70% accuracy)
        if z_score[i] < -1.5 and adx[i] < 35 and rsi[i] < 45:
            y[i] = 1 if np.random.random() > 0.3 else 0
        # SHORT conditions (with 70% accuracy)
        elif z_score[i] > 1.5 and adx[i] < 35 and rsi[i] > 55:
            y[i] = 0 if np.random.random() > 0.3 else 1
        # Neutral (random)
        else:
            y[i] = np.random.randint(0, 2)
    
    print(f"  Features shape: {X.shape}")
    print(f"  Labels shape: {y.shape}")
    print(f"  LONG signals: {np.sum(y == 1)}")
    print(f"  SHORT signals: {np.sum(y == 0)}")
    
    return X, y


def train_model(X, y):
    """
    Train RandomForest model
    
    Args:
        X: Features
        y: Labels
        
    Returns:
        model: Trained model
        score: Accuracy score
    """
    print("\nTraining model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Create and train model
    model = RandomForestClassifier(**MODEL_PARAMS)
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"  Train accuracy: {train_score:.2%}")
    print(f"  Test accuracy: {test_score:.2%}")
    
    return model, test_score


def save_model(model, score):
    """
    Save model and metadata
    
    Args:
        model: Trained model
        score: Model accuracy
    """
    print("\nSaving model...")
    
    # Ensure directory exists
    DEFAULT_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    with open(DEFAULT_MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"  ✅ Model saved: {DEFAULT_MODEL_FILE}")
    
    # Save metadata
    metadata = {
        'version': 'v1',
        'model_type': 'RandomForestClassifier',
        'feature_names': FEATURE_NAMES,
        'n_features': len(FEATURE_NAMES),
        'accuracy': score,
        'trained_at': datetime.utcnow().isoformat(),
        'training_samples': 1000,
        'model_params': MODEL_PARAMS
    }
    
    with open(MODEL_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  ✅ Metadata saved: {MODEL_METADATA_FILE}")


def main():
    """Create and save dummy model"""
    print("=" * 50)
    print("   QUANTP1 v3.1 - Create Dummy ML Model")
    print("=" * 50)
    print()
    
    # Generate data
    X, y = generate_synthetic_data(n_samples=1000)
    
    # Train model
    model, score = train_model(X, y)
    
    # Save model
    save_model(model, score)
    
    print()
    print("=" * 50)
    print("✅ Model created successfully!")
    print("=" * 50)
    print()
    print("⚠️  Note: This is a DUMMY model for testing only")
    print("   Train a real model with historical data before live trading")
    print()


if __name__ == "__main__":
    main()
