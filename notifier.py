import requests
from config import NOTIFICATION_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from logger import logger

class Notifier:
    def __init__(self):
        self.enabled = NOTIFICATION_ENABLED
        self.telegram_bot_token = TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
    
    def send_telegram_message(self, message):
        """
        Send a message via Telegram
        
        Args:
            message (str): Message to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.enabled or not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram notifications not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data)
            response.raise_for_status()
            logger.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def notify_trade_signal(self, signal):
        """
        Send notification for a trade signal
        
        Args:
            signal (dict): Trade signal details
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = (
            f"🔔 <b>Trade Signal</b>\n\n"
            f"Symbol: {signal['symbol']}\n"
            f"Action: {signal['action']}\n"
            f"Type: {signal['type']}\n"
            f"Price: {signal['price']}\n"
            f"Quantity: {signal['quantity']}\n"
            f"Stop Loss: {signal.get('stop_loss', 'N/A')}\n"
            f"Target: {signal.get('target', 'N/A')}\n"
        )
        return self.send_telegram_message(message)
    
    def notify_order_status(self, order):
        """
        Send notification for order status update
        
        Args:
            order (dict): Order details
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = (
            f"📊 <b>Order Update</b>\n\n"
            f"Order ID: {order['id']}\n"
            f"Symbol: {order['symbol']}\n"
            f"Status: {order['status']}\n"
            f"Type: {order['type']}\n"
            f"Side: {order['side']}\n"
            f"Quantity: {order['quantity']}\n"
            f"Price: {order.get('price', 'N/A')}\n"
        )
        return self.send_telegram_message(message)
    
    def notify_error(self, error):
        """
        Send notification for an error
        
        Args:
            error (str): Error message
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = f"⚠️ <b>Error</b>\n\n{error}"
        return self.send_telegram_message(message)
    
    def notify_system_status(self, status):
        """
        Send notification for system status update
        
        Args:
            status (dict): System status details
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = (
            f"🔄 <b>System Status</b>\n\n"
            f"Status: {status['status']}\n"
            f"Connected: {status['connected']}\n"
            f"Active Orders: {status['active_orders']}\n"
            f"Open Positions: {status['open_positions']}\n"
            f"Last Update: {status['last_update']}\n"
        )
        return self.send_telegram_message(message) 