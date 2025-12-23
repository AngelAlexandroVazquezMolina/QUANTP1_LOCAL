"""QUANTP1 v3.1 - Interactive Telegram Bot"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Any
from utils.logger_setup import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


class InteractiveTelegramBot:
    """Interactive Telegram bot with buttons"""
    
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        """
        Initialize Telegram bot
        
        Args:
            token: Bot token
            chat_id: Target chat ID
        """
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.pending_signals: Dict[int, Dict[str, Any]] = {}
        
        # Callbacks for user actions
        self.on_executed_callback = None
        self.on_rejected_callback = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 QUANTP1 v3.1 Trading Bot\n\n"
            "Commands:\n"
            "/start - Initialize bot\n"
            "/status - Trading status\n"
            "/trades - Open trades\n"
            "/balance - Balance and risk\n"
            "/help - Help"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # This would be populated by main system
        await update.message.reply_text("📊 Status command - implement in main.py")
    
    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        await update.message.reply_text("📈 Trades command - implement in main.py")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        await update.message.reply_text("💰 Balance command - implement in main.py")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 QUANTP1 Help

**Commands:**
/start - Initialize bot
/status - Current trading status
/trades - View open trades
/balance - Balance and risk info
/help - This message

**Signal Actions:**
When you receive a signal:
1. Press ✅ Executed if you took the trade
2. Press ❌ Rejected if you skipped it
3. Press ⏳ Pending if deciding

**Execution Format:**
After pressing Executed, send:
`EXEC <signal_id> <price> <lots>`

Example: `EXEC 1 1.08500 0.05`
"""
        await update.message.reply_text(help_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        parts = data.split('_')
        action = parts[0]
        signal_id = int(parts[1])
        
        if action == 'executed':
            await query.edit_message_text(
                f"✅ Signal #{signal_id} marked as EXECUTED\n\n"
                f"Please send execution details:\n"
                f"`EXEC {signal_id} <price> <lots>`\n\n"
                f"Example: `EXEC {signal_id} 1.08500 0.05`"
            )
            
            if self.on_executed_callback:
                await self.on_executed_callback(signal_id)
        
        elif action == 'rejected':
            await query.edit_message_text(f"❌ Signal #{signal_id} REJECTED")
            
            if self.on_rejected_callback:
                await self.on_rejected_callback(signal_id)
        
        elif action == 'pending':
            await query.edit_message_text(f"⏳ Signal #{signal_id} PENDING - Decide soon!")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (execution reports)"""
        text = update.message.text.strip().upper()
        
        if text.startswith('EXEC'):
            parts = text.split()
            if len(parts) >= 4:
                try:
                    signal_id = int(parts[1])
                    price = float(parts[2])
                    lots = float(parts[3])
                    
                    await update.message.reply_text(
                        f"✅ Execution recorded:\n"
                        f"Signal: #{signal_id}\n"
                        f"Price: {price}\n"
                        f"Lots: {lots}"
                    )
                except ValueError:
                    await update.message.reply_text("❌ Invalid format. Use: EXEC <id> <price> <lots>")
            else:
                await update.message.reply_text("❌ Invalid format. Use: EXEC <id> <price> <lots>")
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("trades", self.trades_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def send_signal(self, signal: Dict[str, Any], order: Dict[str, Any], trade_details: Dict[str, Any]):
        """
        Send trading signal with interactive buttons
        
        Args:
            signal: Signal data
            order: Order prices
            trade_details: Trade details
        """
        direction_emoji = "🟢" if signal['direction'] == 'LONG' else "🔴"
        
        message = f"""
{direction_emoji} **SEÑAL EURUSD - {signal['direction']}**

```
EURUSD {signal['direction']}
ENTRY: {order['entry']:.5f}
SL: {order['stop_loss']:.5f}
TP: {order['take_profit']:.5f}
LOTS: {trade_details['lots']:.2f}
```

💡 Confianza ML: {signal['ml_confidence']:.1%}
📊 Riesgo: ${trade_details['risk_amount']:.2f}
⚖️ R:R: {order['risk_reward_ratio']:.2f}

📉 Indicadores:
  Z-Score: {signal['indicators']['z_score']:.2f}
  ADX: {signal['indicators']['adx']:.1f}
  RSI: {signal['indicators']['rsi']:.1f}
"""
        
        # Create buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Ejecutada", callback_data=f"executed_{signal['signal_id']}"),
                InlineKeyboardButton("❌ Rechazada", callback_data=f"rejected_{signal['signal_id']}"),
                InlineKeyboardButton("⏳ Pendiente", callback_data=f"pending_{signal['signal_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Signal #{signal['signal_id']} sent to Telegram")
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
    
    async def send_message(self, message: str):
        """Send plain text message"""
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def initialize(self):
        """Initialize bot application"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        await self.application.initialize()
        await self.application.start()
        logger.info("Telegram bot initialized")
    
    async def shutdown(self):
        """Shutdown bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot shutdown")


if __name__ == "__main__":
    import asyncio
    
    async def test_bot():
        bot = InteractiveTelegramBot()
        await bot.initialize()
        
        # Test signal
        signal = {
            'signal_id': 1,
            'direction': 'LONG',
            'ml_confidence': 0.72,
            'indicators': {
                'z_score': -2.3,
                'adx': 25,
                'rsi': 38
            }
        }
        
        order = {
            'entry': 1.08450,
            'stop_loss': 1.08250,
            'take_profit': 1.08850,
            'risk_reward_ratio': 2.0
        }
        
        trade_details = {
            'lots': 0.05,
            'risk_amount': 100.0
        }
        
        await bot.send_signal(signal, order, trade_details)
        
        # Keep running for 30 seconds
        await asyncio.sleep(30)
        
        await bot.shutdown()
    
    print("Testing Telegram bot...")
    asyncio.run(test_bot())
    print("✅ Bot test completed")
