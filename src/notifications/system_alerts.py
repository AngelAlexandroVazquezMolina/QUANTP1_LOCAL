"""QUANTP1 v3.1 - System Alerts"""
import os
from typing import Optional
from utils.logger_setup import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


class SystemAlerts:
    """Send system alerts to Telegram"""
    
    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        """
        Initialize system alerts
        
        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if not self.enabled:
            logger.warning("System alerts disabled (missing Telegram credentials)")
    
    async def send_alert(self, message: str, level: str = "INFO"):
        """
        Send alert message
        
        Args:
            message: Alert message
            level: Alert level (INFO, WARNING, ERROR, CRITICAL)
        """
        if not self.enabled:
            logger.debug(f"Alert not sent (disabled): {message}")
            return
        
        # Add emoji based on level
        emoji_map = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨',
            'EMERGENCY': '🆘'
        }
        
        emoji = emoji_map.get(level, 'ℹ️')
        formatted_message = f"{emoji} **{level}**\n\n{message}"
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': formatted_message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.debug(f"Alert sent: {level}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def warning(self, message: str):
        """Send warning alert"""
        await self.send_alert(message, "WARNING")
    
    async def error(self, message: str):
        """Send error alert"""
        await self.send_alert(message, "ERROR")
    
    async def critical(self, message: str):
        """Send critical alert"""
        await self.send_alert(message, "CRITICAL")
    
    async def emergency(self, message: str):
        """Send emergency alert"""
        await self.send_alert(message, "EMERGENCY")
    
    async def info(self, message: str):
        """Send info alert"""
        await self.send_alert(message, "INFO")


if __name__ == "__main__":
    import asyncio
    
    async def test_alerts():
        alerts = SystemAlerts()
        
        print("Testing system alerts...\n")
        
        await alerts.info("Test info message")
        await asyncio.sleep(2)
        
        await alerts.warning("Test warning message")
        await asyncio.sleep(2)
        
        await alerts.error("Test error message")
        await asyncio.sleep(2)
        
        await alerts.critical("Test critical message")
        
        print("\n✅ System alerts test completed")
    
    asyncio.run(test_alerts())
