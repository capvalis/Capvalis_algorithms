import json
import os
from config import USER_DATA_FILE
from logger import logger

class UserManager:
    def __init__(self):
        self.users = {}
        self.load_users()
    
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r') as f:
                    self.users = json.load(f)
                logger.info("User data loaded successfully")
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
                # Create empty users file
                with open(USER_DATA_FILE, 'w') as f:
                    json.dump({}, f)
                logger.info("Created new user data file")
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            self.users = {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(self.users, f, indent=4)
            logger.info("User data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False
    
    def add_user(self, user_id, user_data):
        """
        Add a new user
        
        Args:
            user_id (str): Unique user identifier
            user_data (dict): User data including preferences
            
        Returns:
            bool: True if user added successfully, False otherwise
        """
        try:
            if user_id in self.users:
                logger.warning(f"User {user_id} already exists")
                return False
            
            self.users[user_id] = {
                'preferences': {
                    'position_size': user_data.get('position_size', 30),
                    'risk_per_trade': user_data.get('risk_per_trade', 1.0),
                    'max_trades_per_day': user_data.get('max_trades_per_day', 2),
                    'notification_enabled': user_data.get('notification_enabled', True),
                    'telegram_chat_id': user_data.get('telegram_chat_id', None)
                },
                'trading_history': [],
                'created_at': user_data.get('created_at', None),
                'last_active': user_data.get('last_active', None)
            }
            
            return self.save_users()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def update_user(self, user_id, user_data):
        """
        Update user data
        
        Args:
            user_id (str): User identifier
            user_data (dict): Updated user data
            
        Returns:
            bool: True if user updated successfully, False otherwise
        """
        try:
            if user_id not in self.users:
                logger.warning(f"User {user_id} not found")
                return False
            
            # Update preferences
            if 'preferences' in user_data:
                self.users[user_id]['preferences'].update(user_data['preferences'])
            
            # Update other fields
            for key, value in user_data.items():
                if key != 'preferences':
                    self.users[user_id][key] = value
            
            return self.save_users()
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def get_user(self, user_id):
        """
        Get user data
        
        Args:
            user_id (str): User identifier
            
        Returns:
            dict: User data or None if not found
        """
        return self.users.get(user_id)
    
    def delete_user(self, user_id):
        """
        Delete a user
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if user deleted successfully, False otherwise
        """
        try:
            if user_id not in self.users:
                logger.warning(f"User {user_id} not found")
                return False
            
            del self.users[user_id]
            return self.save_users()
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def add_trade_history(self, user_id, trade_data):
        """
        Add trade to user's history
        
        Args:
            user_id (str): User identifier
            trade_data (dict): Trade details
            
        Returns:
            bool: True if trade added successfully, False otherwise
        """
        try:
            if user_id not in self.users:
                logger.warning(f"User {user_id} not found")
                return False
            
            self.users[user_id]['trading_history'].append({
                **trade_data,
                'timestamp': trade_data.get('timestamp', None)
            })
            
            return self.save_users()
        except Exception as e:
            logger.error(f"Error adding trade history: {e}")
            return False
    
    def get_trade_history(self, user_id, start_date=None, end_date=None):
        """
        Get user's trade history
        
        Args:
            user_id (str): User identifier
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            list: List of trades within the date range
        """
        try:
            if user_id not in self.users:
                logger.warning(f"User {user_id} not found")
                return []
            
            trades = self.users[user_id]['trading_history']
            
            if start_date or end_date:
                filtered_trades = []
                for trade in trades:
                    trade_date = trade.get('timestamp', '').split(' ')[0]
                    if start_date and trade_date < start_date:
                        continue
                    if end_date and trade_date > end_date:
                        continue
                    filtered_trades.append(trade)
                return filtered_trades
            
            return trades
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return [] 