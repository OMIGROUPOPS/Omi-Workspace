import time
import base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

API_KEY = 'c9121f7f-c56f-4940-95b2-f604ffb0a23f'
PRIVATE_KEY = open('kalshi.pem').read()

pk = serialization.load_pem_private_key(PRIVATE_KEY.encode(), password=None, backend=default_backend())

ts = str(int(time.time() * 1000))
method = 'GET'
path = '/trade-api/v2/portfolio/balance'
msg = f'{ts}{method}{path}'.encode('utf-8')

sig = base64.b64encode(pk.sign(
    msg,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH
    ),
    hashes.SHA256()
)).decode('utf-8')

headers = {
    'KALSHI-ACCESS-KEY': API_KEY,
    'KALSHI-ACCESS-SIGNATURE': sig,
    'KALSHI-ACCESS-TIMESTAMP': ts
}

r = requests.get(f'https://api.elections.kalshi.com{path}', headers=headers)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f"SUCCESS! Balance: ${data.get('balance', 0) / 100:.2f}")
else:
    print(f'FAILED: {r.json()}')