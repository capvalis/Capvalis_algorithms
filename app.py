from flask import Flask, render_template, request, flash, redirect, url_for
import os
from broker_connect import connect_to_broker
from config import (
    FY_ID, APP_ID, APP_TYPE, PIN, TOTP_KEY, REDIRECT_URI, SECRET_KEY,
    URL_SEND_LOGIN_OTP, URL_VERIFY_TOTP, URL_VERIFY_PIN, TOKEN_FILE
)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    broker = request.form.get('broker')
    
    if broker == 'fyers':
        # Get Fyers-specific credentials
        fy_id = request.form.get('fy_id')
        app_id = request.form.get('app_id')
        app_type = request.form.get('app_type')
        pin = request.form.get('pin')
        totp_key = request.form.get('totp_key')
        redirect_uri = request.form.get('redirect_uri')
        base_url = request.form.get('base_url')

        if not all([fy_id, app_id, app_type, pin, totp_key, redirect_uri, base_url]):
            flash('All fields are required for Fyers connection', 'danger')
            return redirect(url_for('index'))

        # Update config with new values
        try:
            with open('config.py', 'w') as f:
                f.write(f'''# Fyers API Configuration
FY_ID = "{fy_id}"
APP_ID = "{app_id}"
APP_TYPE = "{app_type}"
PIN = "{pin}"
TOTP_KEY = "{totp_key}"
REDIRECT_URI = "{redirect_uri}"
SECRET_KEY = "{SECRET_KEY}"  # Keep existing secret key

# API URLs
URL_SEND_LOGIN_OTP = "{base_url}/api/v3/send-login-otp"
URL_VERIFY_TOTP = "{base_url}/api/v3/verify-totp"
URL_VERIFY_PIN = "{base_url}/api/v3/verify-pin"

# File paths
TOKEN_FILE = "data/token.txt"
''')
            flash('Configuration updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating configuration: {str(e)}', 'danger')
            return redirect(url_for('index'))

        # Attempt to connect
        success = connect_to_broker(fy_id, app_id, app_type, pin, totp_key, redirect_uri)
        
        if success:
            flash('Successfully connected to Fyers!', 'success')
        else:
            flash('Failed to connect to Fyers. Please check your credentials.', 'danger')
    
    elif broker == 'angel':
        flash('Angel One integration is coming soon!', 'info')
    else:
        flash('Please select a broker', 'warning')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True) 