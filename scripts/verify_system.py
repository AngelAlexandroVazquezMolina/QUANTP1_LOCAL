"""QUANTP1 v3.1 - System Verification Script"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import requests

load_dotenv()

def check_environment_variables():
    """Check required environment variables"""
    print("1️⃣ Checking environment variables...")
    
    required_vars = [
        'TWELVE_DATA_KEY',
        'TELEGRAM_BOT_TOKEN',
        'ACCOUNT_SIZE',
        'MAX_DAILY_LOSS_PCT',
        'MAX_LOSS_PER_TRADE'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"   ❌ {var}: MISSING")
        else:
            if 'KEY' in var or 'TOKEN' in var:
                print(f"   ✅ {var}: {value[:10]}...")
            else:
                print(f"   ✅ {var}: {value}")
    
    if missing:
        print(f"\n   ⚠️  Missing variables: {', '.join(missing)}")
        return False
    
    print("   ✅ All environment variables present\n")
    return True


def check_directories():
    """Check required directories exist"""
    print("2️⃣ Checking directories...")
    
    from config.paths_config import (
        CONFIG_DIR, CORE_DIR, DATA_PIPELINE_DIR, SRC_DIR,
        MODELS_DIR, STATE_DIR, LOGS_DIR, SCRIPTS_DIR,
        UTILS_DIR, RESEARCH_DIR
    )
    
    directories = [
        CONFIG_DIR, CORE_DIR, DATA_PIPELINE_DIR, SRC_DIR,
        MODELS_DIR, STATE_DIR, LOGS_DIR, SCRIPTS_DIR,
        UTILS_DIR, RESEARCH_DIR
    ]
    
    all_exist = True
    for directory in directories:
        if directory.exists():
            print(f"   ✅ {directory.name}/")
        else:
            print(f"   ❌ {directory.name}/ (MISSING)")
            all_exist = False
    
    if all_exist:
        print("   ✅ All directories exist\n")
    else:
        print("   ⚠️  Some directories missing\n")
    
    return all_exist


def check_ml_model():
    """Check ML model exists"""
    print("3️⃣ Checking ML model...")
    
    from config.paths_config import DEFAULT_MODEL_FILE
    
    if DEFAULT_MODEL_FILE.exists():
        size_mb = DEFAULT_MODEL_FILE.stat().st_size / (1024 * 1024)
        print(f"   ✅ Model found: {DEFAULT_MODEL_FILE.name} ({size_mb:.2f} MB)")
        
        # Try loading
        try:
            from src.ml.model_loader import ModelLoader
            loader = ModelLoader()
            model = loader.load_model()
            if model:
                print(f"   ✅ Model loaded successfully")
                print()
                return True
            else:
                print(f"   ❌ Model failed to load")
                print()
                return False
        except Exception as e:
            print(f"   ❌ Model load error: {e}")
            print()
            return False
    else:
        print(f"   ❌ Model not found: {DEFAULT_MODEL_FILE}")
        print(f"   💡 Run: python research/create_dummy_model.py")
        print()
        return False


def check_api_connection():
    """Check Twelve Data API connection"""
    print("4️⃣ Checking API connection...")
    
    api_key = os.getenv('TWELVE_DATA_KEY')
    
    if not api_key:
        print("   ❌ API key not configured")
        print()
        return False
    
    try:
        url = "https://api.twelvedata.com/price"
        params = {
            'symbol': 'EUR/USD',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'price' in data:
            price = data['price']
            print(f"   ✅ API connected")
            print(f"   📊 EUR/USD: {price}")
            print()
            return True
        else:
            print(f"   ❌ Invalid API response: {data}")
            print()
            return False
    
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        print()
        return False


def check_telegram_connection():
    """Check Telegram bot connection"""
    print("5️⃣ Checking Telegram connection...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("   ❌ Bot token not configured")
        print()
        return False
    
    if not chat_id:
        print("   ⚠️  Chat ID not configured")
        print("   💡 Run: python scripts/get_chat_id.py")
        print()
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"   ✅ Bot connected: @{bot_info['username']}")
            print(f"   👤 Chat ID: {chat_id}")
            print()
            return True
        else:
            print(f"   ❌ Invalid bot response: {data}")
            print()
            return False
    
    except Exception as e:
        print(f"   ❌ Telegram connection failed: {e}")
        print()
        return False


def main():
    """Run all verification checks"""
    print("=" * 50)
    print("   QUANTP1 v3.1 - System Verification")
    print("=" * 50)
    print()
    
    results = []
    
    results.append(check_environment_variables())
    results.append(check_directories())
    results.append(check_ml_model())
    results.append(check_api_connection())
    results.append(check_telegram_connection())
    
    print("=" * 50)
    if all(results):
        print("✅ SYSTEM READY FOR TRADING")
    else:
        print("⚠️  SYSTEM NOT READY - Fix issues above")
    print("=" * 50)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
