"""
QUANTP1 v3.1 - Main Trading System Orchestrator

Semi-automatic trading system for EURUSD M15
Strategy: Mean Reversion + ML
"""
import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional

# Core components
from utils.logger_setup import setup_logger
from utils.time_utils import (
    is_trading_time,
    seconds_until_trading_start,
    format_time_remaining,
    get_current_time
)
from config.paths_config import STATE_FILE, STATE_BACKUP
from config.risk_config import ACCOUNT_SIZE
from core.state_manager import StateManager
from core.api_circuit_breaker import APICircuitBreaker
from core.time_synchronizer import TimeSynchronizer
from core.health_monitor import HealthMonitor

# Data pipeline
from data_pipeline.feed import DataFeed

# Strategy
from src.strategy.indicators import calculate_all_indicators
from src.strategy.signal_generator import SignalGenerator
from src.strategy.limit_order_calculator import LimitOrderCalculator

# ML
from src.ml.predictor import Predictor

# Risk management
from src.risk.calculator import RiskCalculator
from src.risk.manual_trade_tracker import ManualTradeTracker
from src.risk.risk_gate import RiskGate

# Notifications
from src.notifications.interactive_telegram import InteractiveTelegramBot
from src.notifications.system_alerts import SystemAlerts
from src.notifications.heartbeat import Heartbeat

# Setup logger
logger = setup_logger("quantp1")


class TradingSystem:
    """Main trading system orchestrator"""
    
    def __init__(self):
        """Initialize trading system"""
        self.running = False
        self.shutdown_requested = False
        
        # Core components
        self.state_manager = StateManager(STATE_FILE, STATE_BACKUP)
        self.circuit_breaker = APICircuitBreaker()
        self.time_sync = TimeSynchronizer()
        self.health_monitor = HealthMonitor()
        
        # Data
        self.data_feed = DataFeed(self.circuit_breaker)
        
        # Strategy
        self.signal_generator = SignalGenerator()
        self.order_calculator = LimitOrderCalculator()
        
        # ML
        self.predictor = Predictor()
        
        # Risk
        self.risk_calculator = RiskCalculator(ACCOUNT_SIZE)
        self.trade_tracker = ManualTradeTracker()
        self.risk_gate = RiskGate(self.risk_calculator, self.trade_tracker)
        
        # Notifications
        self.telegram_bot = None
        self.system_alerts = SystemAlerts()
        self.heartbeat = Heartbeat()
        
        # State
        self.last_heartbeat = None
        self.last_health_check = None
    
    async def startup_checks(self) -> bool:
        """
        Perform startup checks
        
        Returns:
            bool: True if all checks passed
        """
        logger.info("=" * 60)
        logger.info("QUANTP1 v3.1 - Trading System Starting")
        logger.info("=" * 60)
        
        # 1. Sync time
        logger.info("1️⃣ Synchronizing time...")
        if self.time_sync.sync_time():
            logger.info("   ✅ Time synchronized")
        else:
            logger.warning("   ⚠️ Time sync failed, using system time")
        
        # 2. Load ML model
        logger.info("2️⃣ Loading ML model...")
        if self.predictor.load():
            logger.info("   ✅ ML model loaded")
        else:
            logger.error("   ❌ ML model failed to load")
            await self.system_alerts.critical("ML model failed to load")
            return False
        
        # 3. Check API
        logger.info("3️⃣ Testing API connection...")
        price = self.data_feed.get_current_price()
        if price:
            logger.info(f"   ✅ API connected (EUR/USD: {price})")
        else:
            logger.error("   ❌ API connection failed")
            await self.system_alerts.critical("API connection failed")
            return False
        
        # 4. Initialize Telegram
        logger.info("4️⃣ Initializing Telegram bot...")
        try:
            self.telegram_bot = InteractiveTelegramBot()
            await self.telegram_bot.initialize()
            await self.telegram_bot.send_message("🚀 QUANTP1 v3.1 started")
            logger.info("   ✅ Telegram bot initialized")
        except Exception as e:
            logger.error(f"   ❌ Telegram initialization failed: {e}")
            return False
        
        # 5. Health check
        logger.info("5️⃣ System health check...")
        if self.health_monitor.is_healthy():
            logger.info("   ✅ System healthy")
        else:
            warnings = self.health_monitor.get_warnings()
            logger.warning(f"   ⚠️ System warnings: {warnings}")
        
        # 6. Load state
        logger.info("6️⃣ Loading system state...")
        state = self.state_manager.load_state()
        self.state_manager.update_state({
            'starting_balance': ACCOUNT_SIZE,
            'current_balance': ACCOUNT_SIZE,
            'daily_pnl': 0.0
        })
        logger.info("   ✅ State loaded")
        
        logger.info("=" * 60)
        logger.info("✅ All startup checks passed")
        logger.info("=" * 60)
        
        return True
    
    async def wait_for_trading_time(self):
        """Wait until trading hours"""
        if is_trading_time():
            logger.info("🟢 Within trading hours, starting immediately")
            return
        
        seconds = seconds_until_trading_start()
        time_str = format_time_remaining(seconds)
        
        logger.info(f"⏰ Outside trading hours")
        logger.info(f"   Time until trading: {time_str}")
        logger.info(f"   Waiting...")
        
        await self.telegram_bot.send_message(
            f"⏰ Waiting for trading hours\n"
            f"Time remaining: {time_str}"
        )
        
        # Wait with periodic updates
        while seconds > 0 and not self.shutdown_requested:
            await asyncio.sleep(min(60, seconds))
            seconds = seconds_until_trading_start()
            
            if seconds > 0 and seconds % 3600 == 0:  # Update every hour
                time_str = format_time_remaining(seconds)
                logger.info(f"   Time remaining: {time_str}")
        
        logger.info("🟢 Trading hours started!")
        await self.telegram_bot.send_message("🟢 Trading hours started!")
    
    async def process_market_data(self):
        """Process market data and generate signals"""
        # Get market data
        logger.debug("Fetching market data...")
        market_data = self.data_feed.get_market_data()
        
        if not market_data:
            logger.error("Failed to fetch market data")
            return
        
        current_price = market_data['current_price']
        candles = market_data['candles']
        
        logger.info(f"💹 EUR/USD: {current_price}")
        
        # Update P&L for open trades
        for trade in self.trade_tracker.get_open_trades():
            self.trade_tracker.update_trade_pnl(trade['signal_id'], current_price)
            
            # Check for exit
            exit_reason = self.trade_tracker.check_exit(trade['signal_id'], current_price)
            if exit_reason:
                self.trade_tracker.close_trade(trade['signal_id'], exit_reason, current_price)
                await self.telegram_bot.send_message(
                    f"🔔 Trade #{trade['signal_id']} closed: {exit_reason}\n"
                    f"P&L: ${trade['pnl']:.2f}"
                )
        
        # Calculate indicators
        logger.debug("Calculating indicators...")
        indicators = calculate_all_indicators(candles)
        
        if not indicators:
            logger.error("Failed to calculate indicators")
            return
        
        logger.info(f"📊 Z-Score: {indicators['z_score']:.2f}, "
                   f"ADX: {indicators['adx']:.1f}, "
                   f"RSI: {indicators['rsi']:.1f}")
        
        # Get ML prediction
        logger.debug("Getting ML prediction...")
        ml_prediction = self.predictor.predict(indicators)
        
        if ml_prediction:
            logger.info(f"🤖 ML: {ml_prediction['direction']} "
                       f"({ml_prediction['confidence']:.1%} confidence)")
        
        # Generate signal
        logger.debug("Generating signal...")
        signal = self.signal_generator.generate_signal(indicators, ml_prediction)
        
        if not signal:
            logger.debug("No signal generated")
            return
        
        # Calculate limit order
        order = self.order_calculator.calculate_limit_order(
            direction=signal['direction'],
            current_price=current_price
        )
        
        # Validate with risk gate
        approved, reason, trade_details = self.risk_gate.validate_signal(signal, order)
        
        if not approved:
            logger.warning(f"❌ Signal rejected: {reason}")
            await self.system_alerts.warning(f"Signal rejected: {reason}")
            return
        
        # Send to Telegram
        logger.info(f"📤 Sending signal to Telegram...")
        await self.telegram_bot.send_signal(signal, order, trade_details)
        
        # Update state
        self.state_manager.set_value('last_signal_id', signal['signal_id'])
    
    async def send_heartbeat(self):
        """Send periodic heartbeat"""
        state = self.state_manager.load_state()
        pnl = self.trade_tracker.get_total_pnl()
        breaker_status = self.circuit_breaker.get_status()
        
        status = {
            'system_status': 'RUNNING',
            'api_calls': breaker_status['daily_calls'],
            'max_api_calls': breaker_status['max_daily_calls'],
            'current_balance': state.get('current_balance', ACCOUNT_SIZE),
            'daily_pnl': pnl['total_pnl'],
            'trades_today': len(self.trade_tracker.get_closed_trades()),
            'open_positions': len(self.trade_tracker.get_open_trades())
        }
        
        await self.heartbeat.send_heartbeat(status)
        self.last_heartbeat = datetime.utcnow()
    
    async def main_loop(self):
        """Main trading loop"""
        logger.info("🔄 Starting main trading loop...")
        
        iteration = 0
        
        while self.running and not self.shutdown_requested:
            try:
                iteration += 1
                logger.info(f"{'='*60}")
                logger.info(f"Iteration #{iteration} - {get_current_time().strftime('%H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # Check if still trading time
                if not is_trading_time():
                    logger.info("⏰ Outside trading hours, stopping...")
                    break
                
                # Process market data
                await self.process_market_data()
                
                # Send heartbeat (every 30 minutes)
                if (self.last_heartbeat is None or
                    (datetime.utcnow() - self.last_heartbeat).total_seconds() >= 1800):
                    await self.send_heartbeat()
                
                # Health check (every hour)
                if (self.last_health_check is None or
                    (datetime.utcnow() - self.last_health_check).total_seconds() >= 3600):
                    health = self.health_monitor.full_health_check()
                    logger.info(f"💊 Health check: {health}")
                    self.last_health_check = datetime.utcnow()
                
                # Wait 15 minutes (900 seconds) before next iteration
                logger.info("⏳ Waiting 15 minutes until next check...")
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await self.system_alerts.error(f"Main loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
        
        logger.info("🛑 Main loop stopped")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("=" * 60)
        logger.info("Shutting down trading system...")
        logger.info("=" * 60)
        
        # Send daily summary
        stats = self.trade_tracker.get_statistics()
        pnl = self.trade_tracker.get_total_pnl()
        
        summary = f"""
📊 **Daily Summary**

💰 Total P&L: ${pnl['total_pnl']:.2f}
📈 Closed P&L: ${pnl['closed_pnl']:.2f}
📉 Floating P&L: ${pnl['floating_pnl']:.2f}

🎯 Total Trades: {stats['total_trades']}
✅ Wins: {stats['wins']}
❌ Losses: {stats['losses']}
📊 Win Rate: {stats['win_rate']:.1f}%

🟢 Open Positions: {len(self.trade_tracker.get_open_trades())}
"""
        
        await self.telegram_bot.send_message(summary)
        await self.telegram_bot.send_message("🛑 QUANTP1 v3.1 stopped")
        
        # Save final state
        self.state_manager.update_state({
            'closed_trades': self.trade_tracker.get_closed_trades(),
            'open_trades': self.trade_tracker.get_open_trades(),
            'daily_pnl': pnl['total_pnl']
        })
        
        # Close connections
        self.data_feed.close()
        if self.telegram_bot:
            await self.telegram_bot.shutdown()
        
        logger.info("✅ Shutdown complete")
    
    async def run(self):
        """Main entry point"""
        try:
            # Startup checks
            if not await self.startup_checks():
                logger.error("Startup checks failed, exiting")
                return
            
            self.running = True
            
            # Wait for trading time
            await self.wait_for_trading_time()
            
            # Run main loop
            await self.main_loop()
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            await self.system_alerts.emergency(f"Fatal error: {e}")
        finally:
            self.running = False
            await self.shutdown()


def handle_signal(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    sys.exit(0)


async def main():
    """Application entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Create and run system
    system = TradingSystem()
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
