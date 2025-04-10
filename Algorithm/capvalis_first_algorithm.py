from SmartApi import SmartConnect
import pyotp
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def capvalis_first_algorithm():
    # API Credentials
    api_key = 'sP2JGPi3'
    username = 'A61994896'
    pwd = '3298'

    # Initialize SmartAPI
    smartApi = SmartConnect(api_key)

    # Strategy Parameters
    MAX_TRADES_PER_DAY = 2
    RISK_PER_TRADE = 0.02  # 2% risk per trade

    # Define stop loss and target points based on price ranges
    def get_stop_loss_target(price):
        if 5000 <= price <= 10000:
            return 15, 45
        elif 10001 <= price <= 15000:
            return 20, 60
        elif 15001 <= price <= 20000:
            return 30, 90
        elif 20001 <= price <= 25000:
            return 50, 150
        elif 25000 <= price <= 30000:
            return 60, 180
        else:
            return 50, 150  # Default values if price is outside ranges

    try:
        token = "FPELUPA7BHMESI3BPT34PAEPSY"
        totp = pyotp.TOTP(token).now()
    except Exception as e:
        raise e

    # Authenticate the session
    try:
        data = smartApi.generateSession(username, pwd, totp)
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        raise e

    # Define date range for iteration
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    # Initialize lists to store trade results and performance metrics
    trade_results = []
    daily_metrics = []

    # Loop through each day in the specified date range
    current_date = start_date

    print(f"\nStarting backtest from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
            
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Processing date: {date_str}")
        
        from_date = f"{date_str} 09:15"
        to_date = f"{date_str} 09:45"

        trades_taken = 0
        daily_trades = []

        try:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": "99926000",  # Nifty 50 token
                "interval": "FIFTEEN_MINUTE",
                "fromdate": from_date,
                "todate": to_date
            }

            # Fetch the historical data
            data = smartApi.getCandleData(historicParam)
            
            # Skip if no data is available (holiday or non-trading day)
            if not isinstance(data, dict) or data.get('status') != True or not data.get('data'):
                print(f"No data available for {date_str} - skipping")
                current_date += timedelta(days=1)
                continue
                
            candles = data['data']
            if len(candles) < 2:
                print(f"Insufficient data for {date_str} - skipping")
                current_date += timedelta(days=1)
                continue

            range_high = max(candles[0][2], candles[1][2])
            range_low = min(candles[0][3], candles[1][3])
            range_size = range_high - range_low
            
            # Validate range size
            if range_size < 20:  # Minimum range size check
                current_date += timedelta(days=1)
                continue

            from_date = f"{date_str} 09:45"
            to_date = f"{date_str} 15:30"
            historicParam["fromdate"] = from_date
            historicParam["todate"] = to_date
            data = smartApi.getCandleData(historicParam)
            
            if isinstance(data, dict) and data.get('status') == True:
                last_candle = None  # Store the last candle for 3:00 PM exit
                
                for candle in data['data']:
                    close_price = candle[4]
                    timestamp = candle[0]
                    high_price = candle[2]
                    low_price = candle[3]
                    last_candle = candle  # Update last candle

                    if trades_taken < MAX_TRADES_PER_DAY:
                        # Check for BUY condition
                        if close_price > range_high and not any(t['action'] == 'BUY' for t in daily_trades):
                            # Get stop loss and target points based on price
                            stop_loss_points, target_points = get_stop_loss_target(close_price)
                            stop_loss = range_high - stop_loss_points
                            risk_amount = range_high - stop_loss
                            position_size = 75  # Fixed position size of 75
                            
                            trade = {
                                'date': date_str,
                                'time': timestamp,
                                'action': 'BUY',
                                'entry': range_high,  # Using range high as entry
                                'stop_loss': stop_loss,
                                'target': range_high + target_points,
                                'range_high': range_high,
                                'range_low': range_low,
                                'position_size': position_size,
                                'status': 'OPEN'
                            }
                            trade_results.append(trade)
                            daily_trades.append(trade)
                            trades_taken += 1
                        
                        # Check for SELL condition
                        elif close_price < range_low and not any(t['action'] == 'SELL' for t in daily_trades):
                            # Get stop loss and target points based on price
                            stop_loss_points, target_points = get_stop_loss_target(close_price)
                            stop_loss = range_low + stop_loss_points
                            risk_amount = stop_loss - range_low
                            position_size = 75  # Fixed position size of 75
                            
                            trade = {
                                'date': date_str,
                                'time': timestamp,
                                'action': 'SELL',
                                'entry': range_low,  # Using range low as entry
                                'stop_loss': stop_loss,
                                'target': range_low - target_points,
                                'range_high': range_high,
                                'range_low': range_low,
                                'position_size': position_size,
                                'status': 'OPEN'
                            }
                            trade_results.append(trade)
                            daily_trades.append(trade)
                            trades_taken += 1

                    # Check for trade exit conditions
                    for trade in daily_trades:
                        if trade['status'] == 'OPEN':
                            if trade['action'] == 'BUY':
                                # Calculate the 1:2 level (2/3 of the way to target)
                                two_thirds_target = trade['entry'] + ((trade['target'] - trade['entry']) * 2/3)
                                
                                # If price reaches 1:2 level, update stop loss to entry price
                                if high_price >= two_thirds_target and trade.get('trailing_stop_updated', False) == False:
                                    trade['stop_loss'] = trade['entry']  # Move stop loss to entry
                                    trade['trailing_stop_updated'] = True  # Mark that we've updated the trailing stop
                                
                                if high_price >= trade['target']:
                                    trade['exit_price'] = trade['target']
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'TARGET_HIT'
                                    trade['pnl'] = (trade['exit_price'] - trade['entry']) * trade['position_size']
                                elif low_price <= trade['stop_loss']:
                                    trade['exit_price'] = trade['stop_loss']
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'STOP_LOSS_HIT'
                                    trade['pnl'] = (trade['exit_price'] - trade['entry']) * trade['position_size']
                            else:  # SELL trade
                                # Calculate the 1:2 level (2/3 of the way to target)
                                two_thirds_target = trade['entry'] - ((trade['entry'] - trade['target']) * 2/3)
                                
                                # If price reaches 1:2 level, update stop loss to entry price
                                if low_price <= two_thirds_target and trade.get('trailing_stop_updated', False) == False:
                                    trade['stop_loss'] = trade['entry']  # Move stop loss to entry
                                    trade['trailing_stop_updated'] = True  # Mark that we've updated the trailing stop
                                
                                if low_price <= trade['target']:
                                    trade['exit_price'] = trade['target']
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'TARGET_HIT'
                                    trade['pnl'] = (trade['entry'] - trade['exit_price']) * trade['position_size']
                                elif high_price >= trade['stop_loss']:
                                    trade['exit_price'] = trade['stop_loss']
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'STOP_LOSS_HIT'
                                    trade['pnl'] = (trade['entry'] - trade['exit_price']) * trade['position_size']
                    
                    # Check if this is the 2:45 PM candle
                    if timestamp and '14:45' in timestamp:
                        close_price = candle[4]
                        for trade in daily_trades:
                            if trade['status'] == 'OPEN':
                                if trade['action'] == 'BUY':
                                    trade['exit_price'] = close_price
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'MARKET_CLOSE'
                                    trade['pnl'] = (trade['exit_price'] - trade['entry']) * trade['position_size']
                                else:  # SELL trade
                                    trade['exit_price'] = close_price
                                    trade['exit_time'] = timestamp
                                    trade['status'] = 'MARKET_CLOSE'
                                    trade['pnl'] = (trade['entry'] - trade['exit_price']) * trade['position_size']

            else:
                current_date += timedelta(days=1)
                continue
        except Exception as e:
            current_date += timedelta(days=1)
            continue
        
        # Calculate daily metrics
        if daily_trades:
            daily_pnl = sum(trade.get('pnl', 0) for trade in daily_trades)
            winning_trades = len([t for t in daily_trades if t.get('pnl', 0) > 0])
            losing_trades = len([t for t in daily_trades if t.get('pnl', 0) < 0])
            
            daily_metrics.append({
                'date': date_str,
                'total_trades': len(daily_trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': winning_trades / len(daily_trades) if daily_trades else 0,
                'daily_pnl': daily_pnl
            })
        
        current_date += timedelta(days=1)
    
    return trade_results, daily_metrics, RISK_PER_TRADE, MAX_TRADES_PER_DAY


