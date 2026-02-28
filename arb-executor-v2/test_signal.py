import requests
import json
import time
import hmac
import hashlib

API_SECRET = "23c584339763ccd46668868bc1094fa28b42f6a84112d2be749e379e4772def1"
WEBHOOK_URL = "https://unexceptional-unpersonalised-winnie.ngrok-free.dev/signal"

signal = {
    'action': 'execute',
    'arb': {
        'sport': 'NBA',
        'game': 'TEST',
        'team': 'TEST',
        'direction': 'BUY_PM_SELL_K',
        'k_bid': 55,
        'k_ask': 56,
        'pm_bid': 50,
        'pm_ask': 51,
        'size': 0,  # Zero size = won't actually trade
        'pm_token_id': 'test123',
        'kalshi_ticker': 'test'
    },
    'kalshi_executed': {
        'success': True,
        'fill_price': 55,
        'fill_size': 0,  # Zero = PM side will reject safely
        'order_id': 'TEST-123'
    }
}

payload = json.dumps(signal)
ts = str(int(time.time() * 1000))
sig = hmac.new(API_SECRET.encode(), f"{ts}{payload}".encode(), hashlib.sha256).hexdigest()

r = requests.post(WEBHOOK_URL, data=payload, headers={
    'Content-Type': 'application/json',
    'X-Timestamp': ts,
    'X-Signature': sig
})

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")