# Trading Server Service

REST API that receives trade signals and executes them on BloFin exchange.

## Features

- ✅ **REST API** - Clean HTTP endpoints
- ✅ **BloFin integration** - Full order management
- ✅ **Authentication** - API key security
- ✅ **Risk management** - Position sizing and limits
- ✅ **Stop loss / Take profit** - Automated risk controls
- ✅ **Health monitoring** - Service status endpoints
- ✅ **Demo mode** - Test without real money

## Self-Contained Design

This service is **completely independent**:
- Standalone trading logic
- No knowledge of Discord
- Can handle multiple signal sources
- Easy to swap exchanges (just modify blofin_client.py)

## Setup

### 1. Install Dependencies

```powershell
cd trading-server
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```env
API_KEY=your_secure_random_key
BLOFIN_API_KEY=your_blofin_key
BLOFIN_SECRET_KEY=your_blofin_secret
BLOFIN_PASSPHRASE=your_passphrase
BLOFIN_BASE_URL=https://demo-trading-openapi.blofin.com
```

**Get BloFin API Keys:**
1. Go to https://www.blofin.com
2. Profile → API Management → Create API Key
3. Set permissions: ✅ Trade, ❌ Withdraw
4. Save: API Key, Secret Key, Passphrase
5. **Use demo URL for testing!**

### 3. Run Server

```powershell
.\venv\Scripts\Activate.ps1
python server.py
```

Server runs on `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### Execute Trade
```bash
POST /api/v1/trade
Content-Type: application/json
X-API-Key: your_api_key

{
  "symbol": "BTC-USDT",
  "side": "long",
  "entry_price": 60000,
  "stop_loss": 58000,
  "take_profit": 65000,
  "size": 0.01
}
```

### Get Statistics
```bash
GET /api/v1/stats
X-API-Key: your_api_key
```

### Get Balance
```bash
GET /api/v1/balance
X-API-Key: your_api_key
```

### Get Positions
```bash
GET /api/v1/positions
X-API-Key: your_api_key
```

## Architecture

```
server.py (FastAPI app)
├── blofin_client.py (exchange API)
├── blofin_auth.py (HMAC signing)
└── shared/models.py (data contracts)
```

### Switching Exchanges

To use a different exchange:
1. Copy `blofin_client.py` to `new_exchange_client.py`
2. Implement same methods with new API
3. Update `server.py` imports
4. No other changes needed!

## Testing with cURL

Test server directly:

```powershell
# Health check
curl http://localhost:8000/health

# Send test signal
curl -X POST http://localhost:8000/api/v1/trade `
  -H "Content-Type: application/json" `
  -H "X-API-Key: your_api_key" `
  -d '{\"symbol\":\"BTC-USDT\",\"side\":\"long\",\"entry_price\":60000,\"size\":0.01}'
```

## Configuration

Edit `.env` for:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `API_KEY` | Auth key | required |
| `BLOFIN_BASE_URL` | API endpoint | demo URL |
| `DEFAULT_TRADE_MODE` | cross/isolated | cross |
| `MAX_POSITION_SIZE_USD` | Max position | 1000 |

## Logs

- Console output
- `trading_server.log` file

## Security

- ✅ API key authentication
- ✅ Never expose secret keys
- ✅ Use demo environment for testing
- ✅ Enable IP whitelisting on BloFin
- ✅ Set proper file permissions for `.env`

## Troubleshooting

**BloFin authentication failed:**
- Verify API keys in `.env`
- Check passphrase is correct
- Ensure API key has Trade permission
- Try demo environment first

**Orders rejected:**
- Check symbol format (e.g., BTC-USDT not BTCUSDT)
- Verify sufficient balance
- Check position size limits
- Review BloFin error code in logs

**Server won't start:**
- Check port 8000 is available
- Verify all dependencies installed
- Check `.env` file exists and is valid
