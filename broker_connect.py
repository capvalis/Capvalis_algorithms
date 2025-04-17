import requests
import pyotp
import os
from fyers_apiv3 import fyersModel
from config import (
    FY_ID, APP_ID, APP_TYPE, PIN, TOTP_KEY, REDIRECT_URI, SECRET_KEY,
    URL_SEND_LOGIN_OTP, URL_VERIFY_TOTP, URL_VERIFY_PIN, TOKEN_FILE
)
from logger import logger
import json
from datetime import datetime
from typing import Optional

class FyersConnection:
    def __init__(self):
        self.token = None
        self.fyers = None
        self.client_id = f"{APP_ID}-{APP_TYPE}"
    
    def get_stored_token(self):
        """Retrieve stored token from file"""
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as f:
                    token = f.read().strip()
                    if token:
                        return token
        except Exception as e:
            logger.error(f"Error reading token: {e}")
        return None
    
    def is_token_valid(self, token):
        """Check if the token is valid"""
        try:
            fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=token,
                is_async=False,
                log_path=""
            )
            profile = fyers.get_profile()
            return 's' in profile and profile['s'] == 'ok'
        except:
            return False
    
    def send_login_otp(self):
        """Send login OTP to user"""
        payload = {"fy_id": FY_ID, "app_id": "2"}
        res = requests.post(url=URL_SEND_LOGIN_OTP, json=payload)
        if res.status_code != 200:
            logger.error(f"Failed to send OTP: {res.text}")
            return None
        return res.json()["request_key"]
    
    def generate_totp(self):
        """Generate TOTP for authentication"""
        try:
            return pyotp.TOTP(TOTP_KEY).now()
        except Exception as e:
            logger.error(f"Failed to generate TOTP: {e}")
            return None
    
    def verify_totp(self, request_key, totp):
        """Verify TOTP"""
        payload = {"request_key": request_key, "otp": totp}
        res = requests.post(url=URL_VERIFY_TOTP, json=payload)
        if res.status_code != 200:
            logger.error(f"Failed to verify TOTP: {res.text}")
            return None
        return res.json()["request_key"]
    
    def verify_pin(self, request_key):
        """Verify PIN"""
        payload = {
            "request_key": request_key,
            "identity_type": "pin",
            "identifier": PIN
        }
        res = requests.post(url=URL_VERIFY_PIN, json=payload)
        if res.status_code != 200:
            logger.error(f"Failed to verify PIN: {res.text}")
            return None
        return res.json()["data"]["access_token"]
    
    def generate_final_access_token(self, pin_token):
        """Generate final access token"""
        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=SECRET_KEY,
            redirect_uri=REDIRECT_URI,
            response_type="code",
            grant_type="authorization_code",
            state="sample_state"
        )
        
        auth_url = session.generate_authcode()
        logger.info(f"\nPlease visit this URL to authorize the application:\n{auth_url}")
        
        auth_code = input("\nPlease enter the auth code from the redirect URL: ")
        logger.info(f"Using auth code: {auth_code}")
        
        session.set_token(auth_code)
        response = session.generate_token()
        
        if isinstance(response, dict):
            if "access_token" in response:
                return response["access_token"]
            elif "token" in response:
                return response["token"]
            else:
                logger.error(f"Available keys in response: {response.keys()}")
                raise Exception("No token found in response")
        else:
            logger.error(f"Response type: {type(response)}")
            raise Exception("Invalid response format")
    
    def connect(self):
        """Establish connection with Fyers API"""
        # First check if we have a stored token
        stored_token = self.get_stored_token()
        if stored_token and self.is_token_valid(stored_token):
            logger.info("✅ Using existing token")
            self.token = stored_token
            self.fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=stored_token,
                is_async=False,
                log_path=""
            )
            return True
        
        logger.info("Getting new token...")
        
        # Step 1: OTP
        request_key = self.send_login_otp()
        if not request_key:
            return False
        logger.info("✅ OTP sent")
        
        # Step 2: TOTP
        totp = self.generate_totp()
        if not totp:
            return False
        logger.info("✅ TOTP generated")
        
        # Step 3: Verify TOTP
        new_request_key = self.verify_totp(request_key, totp)
        if not new_request_key:
            return False
        logger.info("✅ TOTP verified")
        
        # Step 4: PIN
        pin_token = self.verify_pin(new_request_key)
        if not pin_token:
            return False
        logger.info("✅ PIN verified")
        
        # Step 5: Get final API token
        access_token = self.generate_final_access_token(pin_token)
        logger.info("✅ Final Access Token generated")
        
        # Save token
        with open(TOKEN_FILE, "w") as f:
            f.write(access_token)
            logger.info("✅ Token saved")
        
        self.token = access_token
        self.fyers = fyersModel.FyersModel(
            client_id=self.client_id,
            token=access_token,
            is_async=False,
            log_path=""
        )
        return True
    
    def get_profile(self):
        """Get user profile"""
        if not self.fyers:
            logger.error("Not connected to Fyers API")
            return None
        return self.fyers.get_profile()
    
    def get_historical_data(self, symbol, start_date, end_date, interval=5):
        """Get historical data for a symbol"""
        if not self.fyers:
            logger.error("Not connected to Fyers API")
            return None
            
        data = {
            "symbol": symbol,
            "resolution": str(interval),
            "date_format": "1",
            "range_from": start_date,
            "range_to": end_date,
            "cont_flag": "1"
        }
        
        return self.fyers.history(data=data)

class BrokerConnection:
    def __init__(self, user_id: str, api_key: str, api_secret: str, access_token: str):
        self.user_id = user_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = "https://api.broker.com/v1"  # Replace with actual broker API URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "X-API-Secret": api_secret,
            "Authorization": f"Bearer {access_token}"
        })

    def validate_credentials(self) -> bool:
        """Validate the broker credentials by making a test API call"""
        try:
            response = self.session.get(f"{self.base_url}/user/profile")
            return response.status_code == 200
        except requests.RequestException:
            return False

def connect_to_broker(fy_id: str, app_id: str, app_type: str, pin: str, totp_key: str, redirect_uri: str) -> bool:
    """
    Attempt to connect to the Fyers broker using the provided credentials
    
    Args:
        fy_id (str): The Fyers ID
        app_id (str): The application ID
        app_type (str): The application type
        pin (str): The PIN for authentication
        totp_key (str): The TOTP key for 2FA
        redirect_uri (str): The redirect URI for OAuth
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        connection = FyersConnection()
        return connection.connect()
    except Exception as e:
        logger.error(f"Error connecting to Fyers: {e}")
        return False 