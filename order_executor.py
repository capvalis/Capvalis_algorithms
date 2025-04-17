from logger import logger

class OrderExecutor:
    def __init__(self, broker_connection):
        self.broker = broker_connection
    
    def place_order(self, order_params):
        """
        Place an order with the broker
        
        Args:
            order_params (dict): Order parameters including:
                - symbol: Trading symbol
                - qty: Quantity
                - type: Order type (1: Market, 2: Limit)
                - side: Buy/Sell (1: Buy, -1: Sell)
                - price: Price for limit orders
                - stop_price: Stop price for stop orders
                - order_source: Order source (default: 1)
                
        Returns:
            dict: Order response from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.place_order(order_params)
            logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def modify_order(self, order_id, order_params):
        """
        Modify an existing order
        
        Args:
            order_id (str): Order ID to modify
            order_params (dict): New order parameters
            
        Returns:
            dict: Modification response from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.modify_order(order_id, order_params)
            logger.info(f"Order modified: {response}")
            return response
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel an existing order
        
        Args:
            order_id (str): Order ID to cancel
            
        Returns:
            dict: Cancellation response from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.cancel_order(order_id)
            logger.info(f"Order cancelled: {response}")
            return response
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    
    def get_order_status(self, order_id):
        """
        Get the status of an order
        
        Args:
            order_id (str): Order ID to check
            
        Returns:
            dict: Order status from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.order_status(order_id)
            logger.info(f"Order status: {response}")
            return response
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    
    def get_positions(self):
        """
        Get current positions
        
        Returns:
            dict: Positions from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.positions()
            logger.info(f"Positions: {response}")
            return response
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None
    
    def get_holdings(self):
        """
        Get current holdings
        
        Returns:
            dict: Holdings from broker
        """
        try:
            if not self.broker.fyers:
                logger.error("Not connected to broker")
                return None
            
            response = self.broker.fyers.holdings()
            logger.info(f"Holdings: {response}")
            return response
        except Exception as e:
            logger.error(f"Error getting holdings: {e}")
            return None 