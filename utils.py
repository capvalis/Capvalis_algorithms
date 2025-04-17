import pandas as pd
from datetime import datetime, timedelta
from logger import logger

def format_datetime(dt):
    """
    Format datetime to string
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(dt_str):
    """
    Parse datetime string to datetime object
    
    Args:
        dt_str (str): Datetime string
        
    Returns:
        datetime: Datetime object
    """
    try:
        return pd.to_datetime(dt_str)
    except Exception as e:
        logger.error(f"Error parsing datetime: {e}")
        return None

def calculate_profit(entry_price, exit_price, position_type, quantity):
    """
    Calculate profit/loss for a trade
    
    Args:
        entry_price (float): Entry price
        exit_price (float): Exit price
        position_type (str): 'LONG' or 'SHORT'
        quantity (int): Position quantity
        
    Returns:
        float: Profit/loss amount
    """
    try:
        if position_type == 'LONG':
            return (exit_price - entry_price) * quantity
        else:  # SHORT
            return (entry_price - exit_price) * quantity
    except Exception as e:
        logger.error(f"Error calculating profit: {e}")
        return 0.0

def calculate_risk_reward(entry_price, stop_loss, target, position_type):
    """
    Calculate risk-reward ratio
    
    Args:
        entry_price (float): Entry price
        stop_loss (float): Stop loss price
        target (float): Target price
        position_type (str): 'LONG' or 'SHORT'
        
    Returns:
        float: Risk-reward ratio
    """
    try:
        if position_type == 'LONG':
            risk = entry_price - stop_loss
            reward = target - entry_price
        else:  # SHORT
            risk = stop_loss - entry_price
            reward = entry_price - target
            
        if risk == 0:
            return 0
            
        return reward / risk
    except Exception as e:
        logger.error(f"Error calculating risk-reward: {e}")
        return 0.0

def calculate_drawdown(equity_curve):
    """
    Calculate maximum drawdown from equity curve
    
    Args:
        equity_curve (list): List of equity values
        
    Returns:
        float: Maximum drawdown percentage
    """
    try:
        if not equity_curve:
            return 0.0
            
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            max_dd = max(max_dd, dd)
            
        return max_dd
    except Exception as e:
        logger.error(f"Error calculating drawdown: {e}")
        return 0.0

def calculate_win_rate(trades):
    """
    Calculate win rate from trades
    
    Args:
        trades (list): List of trade dictionaries
        
    Returns:
        float: Win rate percentage
    """
    try:
        if not trades:
            return 0.0
            
        winning_trades = sum(1 for trade in trades if trade['result'] == 'WIN')
        return (winning_trades / len(trades)) * 100
    except Exception as e:
        logger.error(f"Error calculating win rate: {e}")
        return 0.0

def calculate_average_profit(trades):
    """
    Calculate average profit per trade
    
    Args:
        trades (list): List of trade dictionaries
        
    Returns:
        float: Average profit
    """
    try:
        if not trades:
            return 0.0
            
        total_profit = sum(
            calculate_profit(
                trade['entry_price'],
                trade['exit_price'],
                trade['type'],
                trade['quantity']
            )
            for trade in trades
        )
        
        return total_profit / len(trades)
    except Exception as e:
        logger.error(f"Error calculating average profit: {e}")
        return 0.0

def is_trading_time():
    """
    Check if current time is within trading hours
    
    Returns:
        bool: True if within trading hours, False otherwise
    """
    try:
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
            
        # Convert to time
        current_time = now.time()
        
        # Market hours: 9:15 AM to 3:30 PM
        market_start = datetime.strptime('09:15:00', '%H:%M:%S').time()
        market_end = datetime.strptime('15:30:00', '%H:%M:%S').time()
        
        return market_start <= current_time <= market_end
    except Exception as e:
        logger.error(f"Error checking trading time: {e}")
        return False

def get_next_trading_day():
    """
    Get the next trading day
    
    Returns:
        datetime: Next trading day
    """
    try:
        next_day = datetime.now() + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
            
        return next_day
    except Exception as e:
        logger.error(f"Error getting next trading day: {e}")
        return None 