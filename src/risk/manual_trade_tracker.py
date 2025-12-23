"""QUANTP1 v3.1 - Manual Trade Tracker"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger_setup import get_logger

logger = get_logger()


class ManualTradeTracker:
    """Track manually executed trades"""
    
    def __init__(self):
        """Initialize trade tracker"""
        self.open_trades: List[Dict[str, Any]] = []
        self.closed_trades: List[Dict[str, Any]] = []
    
    def add_trade(self, trade: Dict[str, Any]):
        """
        Add manually executed trade
        
        Args:
            trade: Trade dictionary with signal_id, entry, sl, tp, lots, direction
        """
        trade['status'] = 'OPEN'
        trade['opened_at'] = datetime.utcnow().isoformat()
        trade['pnl'] = 0.0
        
        self.open_trades.append(trade)
        logger.info(f"Trade added: {trade['direction']} {trade['lots']} lots @ {trade['entry']}")
    
    def update_trade_pnl(self, signal_id: int, current_price: float):
        """
        Update P&L for open trade
        
        Args:
            signal_id: Signal ID
            current_price: Current market price
        """
        for trade in self.open_trades:
            if trade['signal_id'] == signal_id:
                entry = trade['entry']
                lots = trade['lots']
                
                # Calculate P&L
                if trade['direction'] == 'LONG':
                    pnl = (current_price - entry) / 0.0001 * 10 * lots
                else:  # SHORT
                    pnl = (entry - current_price) / 0.0001 * 10 * lots
                
                trade['pnl'] = pnl
                trade['current_price'] = current_price
                
                logger.debug(f"Trade {signal_id} P&L updated: ${pnl:.2f}")
                return
    
    def check_exit(self, signal_id: int, current_price: float) -> Optional[str]:
        """
        Check if trade should be closed (SL/TP hit)
        
        Args:
            signal_id: Signal ID
            current_price: Current market price
            
        Returns:
            str: Exit reason ('SL', 'TP', or None)
        """
        for trade in self.open_trades:
            if trade['signal_id'] == signal_id:
                direction = trade['direction']
                sl = trade['stop_loss']
                tp = trade['take_profit']
                
                if direction == 'LONG':
                    if current_price <= sl:
                        return 'SL'
                    elif current_price >= tp:
                        return 'TP'
                else:  # SHORT
                    if current_price >= sl:
                        return 'SL'
                    elif current_price <= tp:
                        return 'TP'
        
        return None
    
    def close_trade(self, signal_id: int, exit_reason: str, exit_price: float):
        """
        Close a trade
        
        Args:
            signal_id: Signal ID
            exit_reason: Reason for exit ('SL', 'TP', 'MANUAL')
            exit_price: Exit price
        """
        for i, trade in enumerate(self.open_trades):
            if trade['signal_id'] == signal_id:
                # Calculate final P&L
                entry = trade['entry']
                lots = trade['lots']
                
                if trade['direction'] == 'LONG':
                    pnl = (exit_price - entry) / 0.0001 * 10 * lots
                else:  # SHORT
                    pnl = (entry - exit_price) / 0.0001 * 10 * lots
                
                trade['status'] = 'CLOSED'
                trade['exit_reason'] = exit_reason
                trade['exit_price'] = exit_price
                trade['pnl'] = pnl
                trade['closed_at'] = datetime.utcnow().isoformat()
                
                # Move to closed trades
                self.closed_trades.append(trade)
                self.open_trades.pop(i)
                
                logger.info(f"Trade {signal_id} closed: {exit_reason} @ {exit_price}, P&L: ${pnl:.2f}")
                return
    
    def get_open_trades(self) -> List[Dict[str, Any]]:
        """Get all open trades"""
        return self.open_trades.copy()
    
    def get_closed_trades(self) -> List[Dict[str, Any]]:
        """Get all closed trades"""
        return self.closed_trades.copy()
    
    def get_total_pnl(self) -> Dict[str, float]:
        """
        Calculate total P&L
        
        Returns:
            dict: Closed and floating P&L
        """
        closed_pnl = sum(trade['pnl'] for trade in self.closed_trades)
        floating_pnl = sum(trade['pnl'] for trade in self.open_trades)
        
        return {
            'closed_pnl': closed_pnl,
            'floating_pnl': floating_pnl,
            'total_pnl': closed_pnl + floating_pnl
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get trading statistics"""
        total_trades = len(self.closed_trades)
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0
            }
        
        wins = len([t for t in self.closed_trades if t['pnl'] > 0])
        losses = len([t for t in self.closed_trades if t['pnl'] <= 0])
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        
        pnl = self.get_total_pnl()
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'closed_pnl': pnl['closed_pnl'],
            'floating_pnl': pnl['floating_pnl'],
            'total_pnl': pnl['total_pnl']
        }


if __name__ == "__main__":
    # Test trade tracker
    tracker = ManualTradeTracker()
    
    # Add trade
    trade = {
        'signal_id': 1,
        'direction': 'LONG',
        'entry': 1.08500,
        'stop_loss': 1.08300,
        'take_profit': 1.08900,
        'lots': 0.05
    }
    tracker.add_trade(trade)
    
    # Update P&L
    tracker.update_trade_pnl(1, 1.08600)
    
    # Check exit
    exit_reason = tracker.check_exit(1, 1.08900)
    print(f"Exit reason: {exit_reason}")
    
    if exit_reason:
        tracker.close_trade(1, exit_reason, 1.08900)
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Trade tracker test completed")
