"""QUANTP1 v3.1 - Risk Gate (Pre-Signal Validation)"""
from typing import Dict, Any, Optional, Tuple
from utils.logger_setup import get_logger
from src.risk.calculator import RiskCalculator
from src.risk.manual_trade_tracker import ManualTradeTracker
from config.risk_config import MAX_OPEN_POSITIONS, MAX_DAILY_TRADES

logger = get_logger()


class RiskGate:
    """Final risk validation before sending signals"""
    
    def __init__(self, calculator: RiskCalculator, tracker: ManualTradeTracker):
        """
        Initialize risk gate
        
        Args:
            calculator: Risk calculator instance
            tracker: Trade tracker instance
        """
        self.calculator = calculator
        self.tracker = tracker
    
    def validate_signal(
        self,
        signal: Dict[str, Any],
        order: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate signal against all risk rules
        
        Args:
            signal: Trading signal
            order: Limit order details
            
        Returns:
            tuple: (approved, reason, trade_details)
        """
        # Check max open positions
        open_trades = self.tracker.get_open_trades()
        if len(open_trades) >= MAX_OPEN_POSITIONS:
            return False, f"Max open positions reached ({MAX_OPEN_POSITIONS})", None
        
        # Check max daily trades
        stats = self.tracker.get_statistics()
        if stats['total_trades'] >= MAX_DAILY_TRADES:
            return False, f"Max daily trades reached ({MAX_DAILY_TRADES})", None
        
        # Calculate current risk metrics
        pnl = self.tracker.get_total_pnl()
        risk_metrics = self.calculator.calculate_remaining_risk(
            closed_pnl=pnl['closed_pnl'],
            floating_pnl=pnl['floating_pnl']
        )
        
        # Check if can trade
        if not risk_metrics['can_trade']:
            return False, f"Risk limit reached: {risk_metrics['status']}", None
        
        # Calculate position size
        lots = self.calculator.calculate_position_size(
            entry_price=order['entry'],
            stop_loss=order['stop_loss']
        )
        
        # Validate trade
        is_valid, reason = self.calculator.validate_trade(
            entry_price=order['entry'],
            stop_loss=order['stop_loss'],
            lot_size=lots,
            remaining_risk=risk_metrics['remaining_risk']
        )
        
        if not is_valid:
            return False, reason, None
        
        # Calculate trade risk
        trade_risk = self.calculator.calculate_trade_risk(
            entry_price=order['entry'],
            stop_loss=order['stop_loss'],
            lot_size=lots
        )
        
        # Prepare trade details
        trade_details = {
            'signal_id': signal['signal_id'],
            'direction': signal['direction'],
            'entry': order['entry'],
            'stop_loss': order['stop_loss'],
            'take_profit': order['take_profit'],
            'lots': lots,
            'risk_amount': trade_risk,
            'risk_reward_ratio': order['risk_reward_ratio'],
            'ml_confidence': signal['ml_confidence'],
            'remaining_risk': risk_metrics['remaining_risk'],
            'risk_pct_used': risk_metrics['pct_used']
        }
        
        logger.info(f"✅ Signal validated: {signal['direction']} {lots} lots, risk ${trade_risk:.2f}")
        
        return True, "Signal approved", trade_details
    
    def get_risk_status(self) -> Dict[str, Any]:
        """Get current risk status"""
        pnl = self.tracker.get_total_pnl()
        risk_metrics = self.calculator.calculate_remaining_risk(
            closed_pnl=pnl['closed_pnl'],
            floating_pnl=pnl['floating_pnl']
        )
        
        open_trades = self.tracker.get_open_trades()
        stats = self.tracker.get_statistics()
        
        return {
            'can_trade': risk_metrics['can_trade'],
            'remaining_risk': risk_metrics['remaining_risk'],
            'pct_used': risk_metrics['pct_used'],
            'open_positions': len(open_trades),
            'max_open_positions': MAX_OPEN_POSITIONS,
            'daily_trades': stats['total_trades'],
            'max_daily_trades': MAX_DAILY_TRADES,
            'closed_pnl': pnl['closed_pnl'],
            'floating_pnl': pnl['floating_pnl'],
            'total_pnl': pnl['total_pnl']
        }


if __name__ == "__main__":
    # Test risk gate
    calc = RiskCalculator()
    tracker = ManualTradeTracker()
    gate = RiskGate(calc, tracker)
    
    # Test signal
    signal = {
        'signal_id': 1,
        'direction': 'LONG',
        'entry_price': 1.08500,
        'ml_confidence': 0.72
    }
    
    order = {
        'entry': 1.08450,
        'stop_loss': 1.08250,
        'take_profit': 1.08850,
        'risk_reward_ratio': 2.0
    }
    
    print("Testing risk gate...\n")
    
    approved, reason, details = gate.validate_signal(signal, order)
    print(f"Approved: {approved}")
    print(f"Reason: {reason}")
    
    if details:
        print(f"\nTrade Details:")
        for key, value in details.items():
            print(f"  {key}: {value}")
    
    # Get status
    print("\nRisk Status:")
    status = gate.get_risk_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Risk gate test completed")
