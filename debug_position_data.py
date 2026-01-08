import sys
sys.path.insert(0, 'trading-server')
from blofin_client import BloFinClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = BloFinClient(
    os.getenv('BLOFIN_API_KEY'),
    os.getenv('BLOFIN_SECRET_KEY'),
    os.getenv('BLOFIN_PASSPHRASE')
)

positions = client.get_positions()

for pos in positions:
    if float(pos.get('positions', 0)) != 0:
        print(f"\n{pos['instId']} Position Data:")
        print(json.dumps(pos, indent=2))
