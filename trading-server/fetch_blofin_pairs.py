"""
Fetch and cache BloFin supported trading pairs
"""
import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add to path
sys.path.append(os.path.dirname(__file__))

from blofin_client import BloFinClient
from blofin_auth import BloFinAuth

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

PAIRS_FILE = os.path.join(os.path.dirname(__file__), 'blofin_pairs.json')

def fetch_supported_pairs():
    """Fetch all supported trading pairs from BloFin"""
    api_key = os.getenv('BLOFIN_API_KEY')
    secret_key = os.getenv('BLOFIN_SECRET_KEY')
    passphrase = os.getenv('BLOFIN_PASSPHRASE')
    base_url = os.getenv('BLOFIN_BASE_URL', 'https://openapi.blofin.com')
    
    client = BloFinClient(api_key, secret_key, passphrase, base_url)
    
    try:
        # Fetch instruments from BloFin API
        logger.info("Fetching trading pairs from BloFin...")
        response = client._request("GET", "/api/v1/market/instruments", None)
        
        logger.info(f"API Response type: {type(response)}")
        
        # Check if response is a list (direct instrument list)
        if isinstance(response, list):
            instruments = response
        elif isinstance(response, dict) and 'data' in response:
            instruments = response.get('data', [])
        else:
            logger.error(f"Unexpected response format: {response}")
            return []
        
        # Extract trading pairs (instId)
        pairs = []
        for instrument in instruments:
            inst_type = instrument.get('instType', '')
            # BloFin uses uppercase SWAP, not lowercase
            if inst_type.upper() == 'SWAP':  # Perpetual futures
                inst_id = instrument.get('instId', '')
                if inst_id:
                    pairs.append(inst_id)
        
        logger.info(f"✅ Found {len(pairs)} supported trading pairs")
        return pairs
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch pairs: {e}")
        return []

def save_pairs(pairs):
    """Save pairs to JSON file with timestamp"""
    data = {
        'updated_at': datetime.utcnow().isoformat(),
        'pairs': sorted(pairs),
        'count': len(pairs)
    }
    
    with open(PAIRS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"💾 Saved {len(pairs)} pairs to {PAIRS_FILE}")

def load_pairs():
    """Load pairs from JSON file"""
    if not os.path.exists(PAIRS_FILE):
        return []
    
    try:
        with open(PAIRS_FILE, 'r') as f:
            data = json.load(f)
        return data.get('pairs', [])
    except Exception as e:
        logger.error(f"Failed to load pairs: {e}")
        return []

if __name__ == "__main__":
    pairs = fetch_supported_pairs()
    if pairs:
        save_pairs(pairs)
        print(f"\nSuccessfully cached {len(pairs)} trading pairs")
        print(f"Sample pairs: {', '.join(pairs[:10])}")
    else:
        print("\nFailed to fetch pairs")
        sys.exit(1)
