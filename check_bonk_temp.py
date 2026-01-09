import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'trading-server'))

from blofin_client import BloFinClient
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

# Check position history
result = client._request('GET', '/api/v1/account/positions-history', params={'instType': 'SWAP'})
print('Position History:')
if result and 'data' in result:
    bonk_found = False
    for pos in result['data']:
        if 'BONK' in pos.get('instId', ''):
            bonk_found = True
            print(json.dumps(pos, indent=2))
    if not bonk_found:
        print('No BONK positions found in history')
        print(f'Total positions in history: {len(result["data"])}')
else:
    print('No history or error:', result)
