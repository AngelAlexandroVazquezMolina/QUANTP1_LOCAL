"""QUANTP1 v3.1 - Get Telegram Chat ID"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_chat_id():
    """Get Telegram chat ID from bot updates"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return
    
    print("🤖 Fetching Telegram updates...\n")
    print("📱 Send a message to your bot now (e.g., /start)")
    print("   Waiting for updates...\n")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ API error: {data}")
            return
        
        updates = data.get('result', [])
        
        if not updates:
            print("⚠️  No updates found")
            print("\n📝 Make sure to:")
            print("   1. Open Telegram")
            print("   2. Search for your bot")
            print("   3. Send /start message")
            print("   4. Run this script again")
            return
        
        # Get latest update
        latest = updates[-1]
        
        if 'message' in latest:
            chat_id = latest['message']['chat']['id']
            username = latest['message']['chat'].get('username', 'N/A')
            first_name = latest['message']['chat'].get('first_name', 'N/A')
            
            print("✅ Chat ID found!\n")
            print(f"👤 User: {first_name} (@{username})")
            print(f"🆔 Chat ID: {chat_id}")
            print()
            print("📝 Add this to your .env file:")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
            print()
        else:
            print("⚠️  No message found in updates")
            print(f"Updates: {updates}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("   QUANTP1 v3.1 - Get Telegram Chat ID")
    print("=" * 50)
    print()
    
    get_chat_id()
