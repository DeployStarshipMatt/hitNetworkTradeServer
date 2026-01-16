#!/usr/bin/env python3
"""Emergency script to close BTC position with market sell order"""

import os
import sys
import requests
import hmac
import hashlib
import base64
import json
from datetime import datetime

# Add parent directory to path
sys.path.append('/opt/hitNetworkAutomation')

def get_signature(timestamp, method, request_path, body=''):
    """Generate signature for BloFin API"""
    api_secret = os.getenv('BLOFIN_API_SECRET')
    if not api_secret:
        raise ValueError("BLOFIN_API_SECRET not found in environment")
    
    message = timestamp + method + request_path + body
    mac = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

def close_position():
    """Close BTC position with market sell order"""
    api_key = os.getenv('BLOFIN_API_KEY')
    passphrase = os.getenv('BLOFIN_PASSPHRASE')
    
    if not api_key or not passphrase:
        raise ValueError("Missing BloFin API credentials")
    
    # Market sell order to close LONG position
    order_data = {
        "instId": "BTC-USDT",
        "marginMode": "cross",
        "positionSide": "net",
        "side": "sell",
        "orderType": "market",
        "size": "5.2"
    }
    
    endpoint = '/api/v1/copytrading/trade/place-order'
    base_url = 'https://openapi.blofin.com'
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    body = json.dumps(order_data)
    
    signature = get_signature(timestamp, 'POST', endpoint, body)
    
    headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    
    print(f"🚨 EMERGENCY CLOSE: Selling 5.2 BTC-USDT contracts to close position")
    print(f"POST URL: {base_url}{endpoint}")
    print(f"Payload: {body}")
    
    response = requests.post(f"{base_url}{endpoint}", headers=headers, data=body)
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == '0':
            order_id = result.get('data', {}).get('orderId')
            print(f"✅ Position closed successfully! Order ID: {order_id}")
            return True
        else:
            print(f"❌ API Error: {result}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        close_position()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
