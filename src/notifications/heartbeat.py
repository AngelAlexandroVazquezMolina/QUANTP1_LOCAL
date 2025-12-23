"""QUANTP1 v3.1 - Heartbeat (Every 30 min)"""
import os
from datetime import datetime
from typing import Dict, Any
from utils.logger_setup import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


class Heartbeat:
    """Send periodic heartbeat to confirm system is alive"""
    
    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        """
        Initialize heartbeat
        
        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        self.last_heartbeat = None
        
        if not self.enabled:
            logger.warning("Heartbeat disabled (missing Telegram credentials)")
    
    async def send_heartbeat(self, status: Dict[str, Any]):
        """
        Send heartbeat message
        
        Args:
            status: System status dictionary
        """
        if not self.enabled:
            logger.debug("Heartbeat not sent (disabled)")
            return
        
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        message = f"""
💓 **System Heartbeat**

🕐 Time: {timestamp}
🟢 Status: {status.get('system_status', 'RUNNING')}
📊 API Calls: {status.get('api_calls', 0)}/{status.get('max_api_calls', 740)}
💰 Balance: ${status.get('current_balance', 0):.2f}
📈 Daily P&L: ${status.get('daily_pnl', 0):.2f}
🎯 Trades Today: {status.get('trades_today', 0)}
🔓 Open Positions: {status.get('open_positions', 0)}
"""
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.last_heartbeat = datetime.utcnow()
            logger.info("Heartbeat sent")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
    
    def get_last_heartbeat(self):
        """Get timestamp of last heartbeat"""
        return self.last_heartbeat


if __name__ == "__main__":
    import asyncio
    
    async def test_heartbeat():
        heartbeat = Heartbeat()
        
        status = {
            'system_status': 'RUNNING',
            'api_calls': 50,
            'max_api_calls': 740,
            'current_balance': 5150.50,
            'daily_pnl': 150.50,
            'trades_today': 3,
            'open_positions': 1
        }
        
        print("Testing heartbeat...\n")
        await heartbeat.send_heartbeat(status)
        
        print(f"Last heartbeat: {heartbeat.get_last_heartbeat()}")
        print("\n✅ Heartbeat test completed")
    
    asyncio.run(test_heartbeat())
