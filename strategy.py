import pandas as pd
from datetime import datetime, timedelta
from config import DEFAULT_POSITION_SIZE, MIN_RANGE_SIZE
from logger import logger

class RangeBreakoutStrategy:
    def __init__(self, broker_connection):
        self.broker = broker_connection
    
    def get_data_for_date_range(self, symbol, start_date, end_date, interval=5):
        """
        Fetch OHLC data for a date range
        
        Args:
            symbol (str): Symbol in format "NSE:SYMBOL-EQ" for stocks or "NSE:INDEX-INDEX" for indices
            start_date (str): Start date in format "YYYY-MM-DD"
            end_date (str): End date in format "YYYY-MM-DD"
            interval (int): Time interval in minutes (1, 5, 15, 30, 60)
            
        Returns:
            pandas.DataFrame: DataFrame with OHLC data indexed by datetime
        """
        try:
            # Convert string dates to datetime objects
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Calculate the number of days between start and end dates
            days_diff = (end_dt - start_dt).days
            
            # If the date range is more than 100 days, we need to fetch data in chunks
            if days_diff > 100:
                logger.info(f"Date range is {days_diff} days. Fetching data in chunks of 100 days or less...")
                
                # Initialize an empty DataFrame to store all data
                all_data = pd.DataFrame()
                
                # Calculate the number of chunks needed
                num_chunks = (days_diff // 100) + 1
                
                # Fetch data in chunks
                for i in range(num_chunks):
                    # Calculate the start and end dates for this chunk
                    chunk_start = start_dt + pd.Timedelta(days=i*100)
                    chunk_end = min(chunk_start + pd.Timedelta(days=99), end_dt)
                    
                    # Format dates as strings
                    chunk_start_str = chunk_start.strftime('%Y-%m-%d')
                    chunk_end_str = chunk_end.strftime('%Y-%m-%d')
                    
                    logger.info(f"Fetching chunk {i+1}/{num_chunks}: {chunk_start_str} to {chunk_end_str}")
                    
                    # Fetch data for this chunk
                    response = self.broker.get_historical_data(
                        symbol=symbol,
                        start_date=chunk_start_str,
                        end_date=chunk_end_str,
                        interval=interval
                    )
                    
                    if response['s'] == 'ok':
                        df = pd.DataFrame.from_dict(response['candles'])
                        cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
                        df.columns = cols
                        df['datetime'] = pd.to_datetime(df['datetime'], unit="s")
                        df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
                        df['datetime'] = df['datetime'].dt.tz_localize(None)
                        df = df.set_index('datetime')
                        df = df.drop('volume', axis=1)
                        
                        # Append this chunk to the combined DataFrame
                        all_data = pd.concat([all_data, df])
                        logger.info(f"Fetched {len(df)} candles for this chunk")
                    else:
                        logger.error(f"Error fetching data for chunk {i+1}: {response}")
                
                # Sort the combined DataFrame by datetime
                all_data = all_data.sort_index()
                
                # Remove any duplicate rows
                all_data = all_data[~all_data.index.duplicated(keep='first')]
                
                logger.info(f"Total candles fetched: {len(all_data)}")
                return all_data
            else:
                # If the date range is 100 days or less, fetch data in one go
                response = self.broker.get_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval
                )
                
                if response['s'] == 'ok':
                    df = pd.DataFrame.from_dict(response['candles'])
                    cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
                    df.columns = cols
                    df['datetime'] = pd.to_datetime(df['datetime'], unit="s")
                    df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
                    df['datetime'] = df['datetime'].dt.tz_localize(None)
                    df = df.set_index('datetime')
                    df = df.drop('volume', axis=1)
                    return df
                else:
                    logger.error(f"Error fetching data: {response}")
                    return None
        except Exception as e:
            logger.error(f"Error in get_data_for_date_range: {e}")
            return None
    
    def get_stop_loss_target(self, price):
        """
        Get stop loss and target points based on price ranges
        
        Args:
            price (float): Current price
            
        Returns:
            tuple: (stop_loss_points, target_points)
        """
        if 55000 <= price <= 80000:
            return 150, 900
        elif 40000 <= price <= 55000:
            return 120, 720
        elif 25000 <= price <= 40000:
            return 100, 600
        else:
            return 90, 540
    
    def calculate_range(self, day_data):
        """
        Calculate the range for a given day's data
        
        Args:
            day_data (pandas.DataFrame): DataFrame with OHLC data for a single day
            
        Returns:
            tuple: (range_high, range_low, range_size) or None if invalid
        """
        if len(day_data) < 9:
            return None
            
        # Get the range candles (7th, 8th, and 9th candles in 5-min timeframe)
        range_candles = day_data.iloc[6:9]  # 7th, 8th, and 9th candles (9:45-10:00)
        range_high = range_candles['high'].max()
        range_low = range_candles['low'].min()
        range_size = range_high - range_low
        
        if range_size < MIN_RANGE_SIZE:
            return None
            
        return range_high, range_low, range_size
    
    def generate_signals(self, df, position_size=DEFAULT_POSITION_SIZE):
        """
        Generate trading signals based on range breakout strategy
        
        Args:
            df (pandas.DataFrame): DataFrame with OHLC data
            position_size (int): Position size in lots
            
        Returns:
            dict: Dictionary containing signals and trade details
        """
        signals = {
            'trades': [],
            'daily_metrics': [],
            'skipped_days': [],
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'max_drawdown': 0
        }
        
        # Group data by date
        df['date'] = df.index.date
        grouped = df.groupby('date')
        
        previous_day_target_hit = False
        skip_today = False
        skip_next_day = False
        is_third_day = False
        is_fifth_day = False
        third_day_profitable = False
        
        for date, day_data in grouped:
            # Skip if not enough data
            if len(day_data) < 9:
                signals['skipped_days'].append({
                    'date': date,
                    'reason': 'Insufficient data (less than 9 candles)',
                    'what_if_result': 'N/A'
                })
                continue
            
            # Check if we need to skip this day
            if skip_today:
                signals['skipped_days'].append({
                    'date': date,
                    'reason': 'Skipped as per trading rules',
                    'what_if_result': self.calculate_what_if_result(day_data, position_size)
                })
                skip_today = False
                
                if previous_day_target_hit:
                    is_third_day = True
                    previous_day_target_hit = False
                elif third_day_profitable:
                    is_fifth_day = True
                    third_day_profitable = False
                
                continue
            
            # Calculate range
            range_result = self.calculate_range(day_data)
            if not range_result:
                signals['skipped_days'].append({
                    'date': date,
                    'reason': 'Invalid range',
                    'what_if_result': 'N/A'
                })
                continue
                
            range_high, range_low, range_size = range_result
            
            # Process trades for the day
            trades_taken = 0
            current_position = None
            daily_trades = []
            target_hit = False
            
            # Process each candle after the range formation
            for idx, candle in day_data.iloc[9:].iterrows():
                if trades_taken >= 2:  # Maximum 2 trades per day
                    break
                    
                if current_position is None:  # No position
                    if candle['high'] > range_high:  # Long entry
                        current_position = {
                            'type': 'LONG',
                            'entry_price': range_high,
                            'entry_time': idx,
                            'stop_loss': range_high - self.get_stop_loss_target(range_high)[0],
                            'target': range_high + self.get_stop_loss_target(range_high)[1]
                        }
                        trades_taken += 1
                    elif candle['low'] < range_low:  # Short entry
                        current_position = {
                            'type': 'SHORT',
                            'entry_price': range_low,
                            'entry_time': idx,
                            'stop_loss': range_low + self.get_stop_loss_target(range_low)[0],
                            'target': range_low - self.get_stop_loss_target(range_low)[1]
                        }
                        trades_taken += 1
                else:  # Have position
                    if current_position['type'] == 'LONG':
                        if candle['low'] <= current_position['stop_loss']:
                            # Stop loss hit
                            current_position['exit_price'] = current_position['stop_loss']
                            current_position['exit_time'] = idx
                            current_position['result'] = 'LOSS'
                            daily_trades.append(current_position)
                            current_position = None
                        elif candle['high'] >= current_position['target']:
                            # Target hit
                            current_position['exit_price'] = current_position['target']
                            current_position['exit_time'] = idx
                            current_position['result'] = 'WIN'
                            daily_trades.append(current_position)
                            current_position = None
                            target_hit = True
                    else:  # SHORT position
                        if candle['high'] >= current_position['stop_loss']:
                            # Stop loss hit
                            current_position['exit_price'] = current_position['stop_loss']
                            current_position['exit_time'] = idx
                            current_position['result'] = 'LOSS'
                            daily_trades.append(current_position)
                            current_position = None
                        elif candle['low'] <= current_position['target']:
                            # Target hit
                            current_position['exit_price'] = current_position['target']
                            current_position['exit_time'] = idx
                            current_position['result'] = 'WIN'
                            daily_trades.append(current_position)
                            current_position = None
                            target_hit = True
            
            # Close any open position at end of day
            if current_position:
                current_position['exit_price'] = day_data.iloc[-1]['close']
                current_position['exit_time'] = day_data.index[-1]
                current_position['result'] = 'LOSS'  # Unclosed position is considered loss
                daily_trades.append(current_position)
            
            # Update signals with daily trades
            signals['trades'].extend(daily_trades)
            signals['total_trades'] += len(daily_trades)
            
            # Calculate daily metrics
            daily_profit = sum(
                (t['exit_price'] - t['entry_price']) if t['type'] == 'LONG'
                else (t['entry_price'] - t['exit_price'])
                for t in daily_trades
            )
            
            signals['daily_metrics'].append({
                'date': date,
                'trades': len(daily_trades),
                'profit': daily_profit,
                'target_hit': target_hit
            })
            
            # Update overall metrics
            signals['total_profit'] += daily_profit
            signals['winning_trades'] += sum(1 for t in daily_trades if t['result'] == 'WIN')
            signals['losing_trades'] += sum(1 for t in daily_trades if t['result'] == 'LOSS')
            
            # Update trading rules for next day
            if target_hit:
                previous_day_target_hit = True
                skip_today = True
            elif is_third_day:
                if daily_profit > 0:
                    third_day_profitable = True
                is_third_day = False
            elif is_fifth_day:
                skip_next_day = True
                is_fifth_day = False
        
        return signals
    
    def calculate_what_if_result(self, day_data, position_size):
        """
        Calculate what would have happened if we traded on a skipped day
        
        Args:
            day_data (pandas.DataFrame): DataFrame with OHLC data for a single day
            position_size (int): Position size in lots
            
        Returns:
            dict: Dictionary with what-if analysis results
        """
        range_result = self.calculate_range(day_data)
        if not range_result:
            return {'profit': 0, 'trades': 0, 'reason': 'Invalid range'}
            
        range_high, range_low, range_size = range_result
        
        trades = []
        current_position = None
        
        # Process each candle after the range formation
        for idx, candle in day_data.iloc[9:].iterrows():
            if current_position is None:  # No position
                if candle['high'] > range_high:  # Long entry
                    current_position = {
                        'type': 'LONG',
                        'entry_price': range_high,
                        'entry_time': idx,
                        'stop_loss': range_high - self.get_stop_loss_target(range_high)[0],
                        'target': range_high + self.get_stop_loss_target(range_high)[1]
                    }
                elif candle['low'] < range_low:  # Short entry
                    current_position = {
                        'type': 'SHORT',
                        'entry_price': range_low,
                        'entry_time': idx,
                        'stop_loss': range_low + self.get_stop_loss_target(range_low)[0],
                        'target': range_low - self.get_stop_loss_target(range_low)[1]
                    }
            else:  # Have position
                if current_position['type'] == 'LONG':
                    if candle['low'] <= current_position['stop_loss']:
                        # Stop loss hit
                        current_position['exit_price'] = current_position['stop_loss']
                        current_position['exit_time'] = idx
                        current_position['result'] = 'LOSS'
                        trades.append(current_position)
                        current_position = None
                    elif candle['high'] >= current_position['target']:
                        # Target hit
                        current_position['exit_price'] = current_position['target']
                        current_position['exit_time'] = idx
                        current_position['result'] = 'WIN'
                        trades.append(current_position)
                        current_position = None
                else:  # SHORT position
                    if candle['high'] >= current_position['stop_loss']:
                        # Stop loss hit
                        current_position['exit_price'] = current_position['stop_loss']
                        current_position['exit_time'] = idx
                        current_position['result'] = 'LOSS'
                        trades.append(current_position)
                        current_position = None
                    elif candle['low'] <= current_position['target']:
                        # Target hit
                        current_position['exit_price'] = current_position['target']
                        current_position['exit_time'] = idx
                        current_position['result'] = 'WIN'
                        trades.append(current_position)
                        current_position = None
        
        # Close any open position at end of day
        if current_position:
            current_position['exit_price'] = day_data.iloc[-1]['close']
            current_position['exit_time'] = day_data.index[-1]
            current_position['result'] = 'LOSS'  # Unclosed position is considered loss
            trades.append(current_position)
        
        # Calculate total profit
        total_profit = sum(
            (t['exit_price'] - t['entry_price']) if t['type'] == 'LONG'
            else (t['entry_price'] - t['exit_price'])
            for t in trades
        )
        
        return {
            'profit': total_profit,
            'trades': len(trades),
            'winning_trades': sum(1 for t in trades if t['result'] == 'WIN'),
            'losing_trades': sum(1 for t in trades if t['result'] == 'LOSS')
        } 