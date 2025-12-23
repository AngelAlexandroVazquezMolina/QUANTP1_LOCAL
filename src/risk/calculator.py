"""QUANTP1 v3.1 - Risk Calculator"""
from typing import Dict, Any
from utils.logger_setup import get_logger
from config.risk_config import (
    ACCOUNT_SIZE,
    MAX_DAILY_LOSS_AMOUNT,
    MAX_LOSS_PER_TRADE,
    DEFAULT_RISK_PCT,
    MIN_LOT_SIZE,
    MAX_LOT_SIZE,
    RISK_BUFFER_AMOUNT
)

logger = get_logger()


class RiskCalculator:
    """Calculate risk metrics for prop firm rules"""
    
    def __init__(self, starting_balance: float = ACCOUNT_SIZE):
        """
        Initialize risk calculator
        
        Args:
            starting_balance: Starting balance for the day
        """
        self.starting_balance = starting_balance
        self.max_daily_loss = MAX_DAILY_LOSS_AMOUNT
        self.max_loss_per_trade = MAX_LOSS_PER_TRADE
        self.risk_buffer = RISK_BUFFER_AMOUNT
    
    def calculate_remaining_risk(
        self,
        closed_pnl: float = 0.0,
        floating_pnl: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate remaining risk for the day
        
        Args:
            closed_pnl: Realized P&L (negative for losses)
            floating_pnl: Unrealized P&L from open positions
            
        Returns:
            dict: Risk metrics
        """
        # Calculate total losses (only negative P&L)
        closed_loss = abs(min(closed_pnl, 0))
        floating_loss = abs(min(floating_pnl, 0))
        total_loss = closed_loss + floating_loss
        
        # Calculate remaining risk with buffer
        remaining = self.max_daily_loss - total_loss - self.risk_buffer
        remaining = max(remaining, 0)  # Can't be negative
        
        # Calculate percentage used
        pct_used = (total_loss / self.max_daily_loss) * 100 if self.max_daily_loss > 0 else 0
        
        # Determine status
        if total_loss >= self.max_daily_loss:
            status = "LIMIT_REACHED"
        elif remaining < self.max_loss_per_trade:
            status = "INSUFFICIENT"
        else:
            status = "OK"
        
        metrics = {
            'remaining_risk': remaining,
            'total_loss': total_loss,
            'max_daily_loss': self.max_daily_loss,
            'pct_used': pct_used,
            'status': status,
            'can_trade': status == "OK"
        }
        
        logger.debug(f"Risk: ${remaining:.2f} remaining, {pct_used:.1f}% used, status={status}")
        
        return metrics
    
    def calculate_trade_risk(
        self,
        entry_price: float,
        stop_loss: float,
        lot_size: float
    ) -> float:
        """
        Calculate risk amount for a trade
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            lot_size: Position size in lots
            
        Returns:
            float: Risk amount in dollars
        """
        pip_risk = abs(entry_price - stop_loss) / 0.0001  # For EURUSD
        risk_amount = pip_risk * 10 * lot_size  # $10 per pip per lot
        
        logger.debug(f"Trade risk: {pip_risk:.1f} pips * {lot_size} lots = ${risk_amount:.2f}")
        
        return risk_amount
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_amount: float = None,
        risk_pct: float = DEFAULT_RISK_PCT
    ) -> float:
        """
        Calculate optimal position size
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_amount: Fixed risk amount (overrides risk_pct)
            risk_pct: Risk as percentage of balance
            
        Returns:
            float: Position size in lots
        """
        # Determine risk amount
        if risk_amount is None:
            risk_amount = self.starting_balance * risk_pct
        
        # Cap at max loss per trade
        risk_amount = min(risk_amount, self.max_loss_per_trade)
        
        # Calculate pip risk
        pip_risk = abs(entry_price - stop_loss) / 0.0001
        
        if pip_risk == 0:
            logger.error("Invalid pip risk: 0")
            return MIN_LOT_SIZE
        
        # Calculate lots ($10 per pip per lot)
        lots = risk_amount / (pip_risk * 10)
        
        # Apply limits
        lots = max(MIN_LOT_SIZE, min(lots, MAX_LOT_SIZE))
        
        # Round to 2 decimals
        lots = round(lots, 2)
        
        logger.info(f"Position size: {lots} lots (risk: ${risk_amount:.2f})")
        
        return lots
    
    def validate_trade(
        self,
        entry_price: float,
        stop_loss: float,
        lot_size: float,
        remaining_risk: float
    ) -> tuple[bool, str]:
        """
        Validate if trade is within risk limits
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            lot_size: Position size
            remaining_risk: Remaining risk available
            
        Returns:
            tuple: (is_valid, reason)
        """
        # Calculate trade risk
        trade_risk = self.calculate_trade_risk(entry_price, stop_loss, lot_size)
        
        # Check against max loss per trade
        if trade_risk > self.max_loss_per_trade:
            return False, f"Trade risk ${trade_risk:.2f} exceeds max ${self.max_loss_per_trade:.2f}"
        
        # Check against remaining risk
        if trade_risk > remaining_risk:
            return False, f"Trade risk ${trade_risk:.2f} exceeds remaining ${remaining_risk:.2f}"
        
        return True, "Trade validated"


if __name__ == "__main__":
    # Test risk calculator
    calc = RiskCalculator()
    
    print("Testing risk calculator...\n")
    
    # Test remaining risk
    metrics = calc.calculate_remaining_risk(closed_pnl=-100, floating_pnl=-50)
    print(f"Remaining Risk: ${metrics['remaining_risk']:.2f}")
    print(f"Total Loss: ${metrics['total_loss']:.2f}")
    print(f"Used: {metrics['pct_used']:.1f}%")
    print(f"Status: {metrics['status']}")
    print(f"Can Trade: {metrics['can_trade']}")
    
    # Test position sizing
    print("\nPosition Sizing:")
    lots = calc.calculate_position_size(1.08500, 1.08300)
    print(f"  Lots: {lots}")
    
    # Test trade validation
    print("\nTrade Validation:")
    valid, reason = calc.validate_trade(1.08500, 1.08300, lots, metrics['remaining_risk'])
    print(f"  Valid: {valid}")
    print(f"  Reason: {reason}")
    
    print("\n✅ Risk calculator test completed")
