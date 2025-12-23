"""QUANTP1 v3.1 - Limit Order Calculator"""
from typing import Dict, Any
from utils.logger_setup import get_logger
from config.trading_config import (
    DEFAULT_TP_PIPS,
    DEFAULT_SL_PIPS,
    LIMIT_OFFSET_PIPS,
    PIP_VALUE
)

logger = get_logger()


class LimitOrderCalculator:
    """Calculate limit order prices (Entry, SL, TP)"""
    
    @staticmethod
    def calculate_limit_order(
        direction: str,
        current_price: float,
        tp_pips: float = DEFAULT_TP_PIPS,
        sl_pips: float = DEFAULT_SL_PIPS,
        offset_pips: float = LIMIT_OFFSET_PIPS
    ) -> Dict[str, float]:
        """
        Calculate limit order prices
        
        Args:
            direction: 'LONG' or 'SHORT'
            current_price: Current market price
            tp_pips: Take profit in pips
            sl_pips: Stop loss in pips
            offset_pips: Entry offset in pips
            
        Returns:
            dict: Entry, SL, TP prices
        """
        if direction == 'LONG':
            # For LONG: Entry below current, SL below entry, TP above entry
            entry = current_price - (offset_pips * PIP_VALUE)
            stop_loss = entry - (sl_pips * PIP_VALUE)
            take_profit = entry + (tp_pips * PIP_VALUE)
            
        elif direction == 'SHORT':
            # For SHORT: Entry above current, SL above entry, TP below entry
            entry = current_price + (offset_pips * PIP_VALUE)
            stop_loss = entry + (sl_pips * PIP_VALUE)
            take_profit = entry - (tp_pips * PIP_VALUE)
            
        else:
            logger.error(f"Invalid direction: {direction}")
            return None
        
        order = {
            'entry': round(entry, 5),
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'risk_reward_ratio': tp_pips / sl_pips if sl_pips > 0 else 0
        }
        
        logger.debug(f"{direction} order: Entry={order['entry']}, SL={order['stop_loss']}, TP={order['take_profit']}")
        
        return order
    
    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_amount: float,
        entry_price: float,
        stop_loss: float,
        contract_size: float = 100000
    ) -> float:
        """
        Calculate position size in lots
        
        Args:
            account_balance: Account balance
            risk_amount: Amount willing to risk
            entry_price: Entry price
            stop_loss: Stop loss price
            contract_size: Standard lot size (100,000 for forex)
            
        Returns:
            float: Position size in lots
        """
        # Calculate pip risk
        pip_risk = abs(entry_price - stop_loss) / PIP_VALUE
        
        if pip_risk == 0:
            logger.error("Invalid pip risk: 0")
            return 0.0
        
        # Calculate pip value per lot
        pip_value_per_lot = PIP_VALUE * contract_size
        
        # Calculate lots
        lots = risk_amount / (pip_risk * pip_value_per_lot)
        
        # Round to 2 decimal places (0.01 lot increments)
        lots = round(lots, 2)
        
        logger.debug(f"Position size: {lots} lots for ${risk_amount:.2f} risk")
        
        return lots


if __name__ == "__main__":
    # Test limit order calculator
    calc = LimitOrderCalculator()
    
    current = 1.08500
    
    print("Testing LONG order:")
    long_order = calc.calculate_limit_order('LONG', current)
    print(f"  Entry: {long_order['entry']}")
    print(f"  SL: {long_order['stop_loss']}")
    print(f"  TP: {long_order['take_profit']}")
    print(f"  R:R: {long_order['risk_reward_ratio']:.2f}")
    
    print("\nTesting SHORT order:")
    short_order = calc.calculate_limit_order('SHORT', current)
    print(f"  Entry: {short_order['entry']}")
    print(f"  SL: {short_order['stop_loss']}")
    print(f"  TP: {short_order['take_profit']}")
    print(f"  R:R: {short_order['risk_reward_ratio']:.2f}")
    
    print("\nTesting position sizing:")
    lots = calc.calculate_position_size(5000, 100, long_order['entry'], long_order['stop_loss'])
    print(f"  Lots: {lots}")
    
    print("\n✅ Limit order calculator test completed")
