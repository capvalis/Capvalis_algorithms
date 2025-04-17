import os
import time
from datetime import datetime, timedelta
from broker_connect import FyersConnection
from strategy import RangeBreakoutStrategy
from order_executor import OrderExecutor
from user_manager import UserManager
from notifier import Notifier
from logger import logger
from utils import (
    format_datetime, parse_datetime, is_trading_time,
    get_next_trading_day, calculate_profit, calculate_win_rate
)

class AlgoEngine:
    def __init__(self):
        """Initialize the algo trading engine"""
        # Initialize components
        self.broker = FyersConnection()
        self.strategy = RangeBreakoutStrategy(self.broker)
        self.order_executor = OrderExecutor(self.broker)
        self.user_manager = UserManager()
        self.notifier = Notifier()
        
        # Trading state
        self.is_running = False
        self.current_positions = {}
        self.active_orders = {}
    
    def start(self):
        """Start the algo trading engine"""
        try:
            logger.info("Starting algo trading engine...")
            
            # Connect to broker
            if not self.broker.connect():
                logger.error("Failed to connect to broker")
                return False
            
            self.is_running = True
            logger.info("Algo trading engine started successfully")
            
            # Send system status notification
            self.notifier.notify_system_status({
                'status': 'STARTED',
                'connected': True,
                'active_orders': len(self.active_orders),
                'open_positions': len(self.current_positions),
                'last_update': format_datetime(datetime.now())
            })
            
            return True
        except Exception as e:
            logger.error(f"Error starting algo engine: {e}")
            self.notifier.notify_error(str(e))
            return False
    
    def stop(self):
        """Stop the algo trading engine"""
        try:
            logger.info("Stopping algo trading engine...")
            
            # Close all positions
            self.close_all_positions()
            
            self.is_running = False
            logger.info("Algo trading engine stopped successfully")
            
            # Send system status notification
            self.notifier.notify_system_status({
                'status': 'STOPPED',
                'connected': False,
                'active_orders': 0,
                'open_positions': 0,
                'last_update': format_datetime(datetime.now())
            })
            
            return True
        except Exception as e:
            logger.error(f"Error stopping algo engine: {e}")
            self.notifier.notify_error(str(e))
            return False
    
    def run(self):
        """Main trading loop"""
        while self.is_running:
            try:
                # Check if it's trading time
                if not is_trading_time():
                    logger.info("Outside trading hours. Waiting...")
                    time.sleep(60)  # Check every minute
                    continue
                
                # Get current positions and orders
                self.update_positions()
                self.update_orders()
                
                # Generate and process signals
                self.process_signals()
                
                # Update system status
                self.update_system_status()
                
                # Sleep for a short interval
                time.sleep(5)  # 5-second delay between iterations
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.notifier.notify_error(str(e))
                time.sleep(60)  # Wait longer on error
    
    def update_positions(self):
        """Update current positions"""
        try:
            positions = self.order_executor.get_positions()
            if positions and 'netPositions' in positions:
                self.current_positions = {
                    pos['symbol']: pos
                    for pos in positions['netPositions']
                    if float(pos['netQty']) != 0
                }
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def update_orders(self):
        """Update active orders"""
        try:
            # Get all orders
            orders = self.order_executor.get_order_status()
            if orders:
                self.active_orders = {
                    order['id']: order
                    for order in orders
                    if order['status'] in ['NEW', 'PARTIALLY_FILLED']
                }
        except Exception as e:
            logger.error(f"Error updating orders: {e}")
    
    def process_signals(self):
        """Process trading signals"""
        try:
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)  # Last 5 days
            
            df = self.strategy.get_data_for_date_range(
                symbol="NSE:NIFTYBANK-INDEX",
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                interval=5
            )
            
            if df is None or df.empty:
                logger.warning("No data available for signal generation")
                return
            
            # Generate signals
            signals = self.strategy.generate_signals(df)
            
            # Process each signal
            for signal in signals['trades']:
                # Check if we already have a position
                if signal['symbol'] in self.current_positions:
                    continue
                
                # Check if we have too many active orders
                if len(self.active_orders) >= 2:  # Maximum 2 active orders
                    continue
                
                # Place order
                order_params = {
                    'symbol': signal['symbol'],
                    'qty': signal['quantity'],
                    'type': 1,  # Market order
                    'side': 1 if signal['type'] == 'LONG' else -1,
                    'order_source': 1
                }
                
                response = self.order_executor.place_order(order_params)
                if response and 'id' in response:
                    # Send notification
                    self.notifier.notify_trade_signal(signal)
                    
                    # Add to active orders
                    self.active_orders[response['id']] = {
                        'id': response['id'],
                        'symbol': signal['symbol'],
                        'type': signal['type'],
                        'quantity': signal['quantity'],
                        'entry_price': signal['entry_price'],
                        'stop_loss': signal['stop_loss'],
                        'target': signal['target']
                    }
        except Exception as e:
            logger.error(f"Error processing signals: {e}")
    
    def close_all_positions(self):
        """Close all open positions"""
        try:
            for symbol, position in self.current_positions.items():
                # Create closing order
                order_params = {
                    'symbol': symbol,
                    'qty': abs(float(position['netQty'])),
                    'type': 1,  # Market order
                    'side': -1 if float(position['netQty']) > 0 else 1,
                    'order_source': 1
                }
                
                # Place order
                response = self.order_executor.place_order(order_params)
                if response:
                    logger.info(f"Closed position for {symbol}")
                    
                    # Send notification
                    self.notifier.notify_order_status({
                        'id': response['id'],
                        'symbol': symbol,
                        'status': 'CLOSED',
                        'type': 'MARKET',
                        'side': order_params['side'],
                        'quantity': order_params['qty']
                    })
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
    
    def update_system_status(self):
        """Update and notify system status"""
        try:
            status = {
                'status': 'RUNNING',
                'connected': self.broker.fyers is not None,
                'active_orders': len(self.active_orders),
                'open_positions': len(self.current_positions),
                'last_update': format_datetime(datetime.now())
            }
            
            self.notifier.notify_system_status(status)
        except Exception as e:
            logger.error(f"Error updating system status: {e}")

def main():
    """Main entry point"""
    try:
        # Create and start algo engine
        engine = AlgoEngine()
        if engine.start():
            # Run the engine
            engine.run()
        else:
            logger.error("Failed to start algo engine")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Ensure engine is stopped
        if 'engine' in locals():
            engine.stop()

if __name__ == "__main__":
    main() 