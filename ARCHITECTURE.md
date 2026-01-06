# HIT Network Automation - System Architecture

## Overview

Microservices-based automated trading system with complete separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Discord Channel                          │
│                    (Trade Signals Posted)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Monitor
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DISCORD BOT SERVICE                       │
│                      (Signal Listener)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   bot.py     │───▶│  parser.py   │───▶│ trading_client  │   │
│  │ (main loop)  │    │  (extract)   │    │ (HTTP client)   │   │
│  └──────────────┘    └──────────────┘    └─────────────────┘   │
│                                                    │              │
│  Features:                                         │              │
│  • Monitors specific channel                       │              │
│  • Multi-format signal parsing                     │              │
│  • User/role filtering                             │              │
│  • Retry logic                                     │              │
│  • NO trading logic                                │              │
│  • NO API keys                                     │              │
└────────────────────────────────────────────────────┼──────────────┘
                                                     │
                                   REST API          │
                              (JSON over HTTPS)      │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRADING SERVER SERVICE                      │
│                       (Order Executor)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │  server.py   │───▶│blofin_client │───▶│  blofin_auth    │   │
│  │ (FastAPI)    │    │ (trading)    │    │  (HMAC sign)    │   │
│  └──────────────┘    └──────────────┘    └─────────────────┘   │
│                                                    │              │
│  Features:                                         │              │
│  • REST API endpoints                              │              │
│  • Order execution                                 │              │
│  • Stop loss / Take profit                         │              │
│  • Risk management                                 │              │
│  • Position sizing                                 │              │
│  • Health monitoring                               │              │
└────────────────────────────────────────────────────┼──────────────┘
                                                     │
                                         BloFin API  │
                                    (Authenticated)  │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BLOFIN EXCHANGE                          │
│                      (Order Execution)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Signal Detection
```
Discord Message → Bot Listener → Parser → TradeSignal Object
```

### 2. Signal Transmission
```
TradeSignal → HTTP POST → Trading Server → Validation
```

### 3. Order Execution
```
Validated Signal → BloFin Client → Authentication → API Request → Order Placed
```

### 4. Confirmation
```
Order Response → Trading Server → HTTP Response → Discord Bot → Message Reply
```

## Component Details

### Discord Bot (`/discord-bot`)

**Responsibility:** Listen and parse trade signals

**Files:**
- `bot.py` - Main Discord bot logic
- `parser.py` - Signal parsing with regex patterns
- `trading_client.py` - HTTP client for Trading Server
- `.env` - Configuration (bot token, channel ID)

**Dependencies:**
- `discord.py` - Discord API
- `requests` - HTTP client
- No exchange dependencies

**Can be modified without affecting:** Trading Server

### Trading Server (`/trading-server`)

**Responsibility:** Execute trades on BloFin

**Files:**
- `server.py` - FastAPI application
- `blofin_client.py` - BloFin API integration
- `blofin_auth.py` - HMAC-SHA256 authentication
- `.env` - Configuration (BloFin keys, risk settings)

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- No Discord dependencies

**Can be modified without affecting:** Discord Bot

### Shared (`/shared`)

**Responsibility:** Common data models

**Files:**
- `models.py` - Data classes (TradeSignal, TradeResponse)
- `__init__.py` - Package exports

**Used by:** Both services

**Changes here affect:** Both services (this is the contract)

## Communication Protocol

### REST API Endpoint

**URL:** `POST /api/v1/trade`

**Headers:**
```
Content-Type: application/json
X-API-Key: <shared_secret>
```

**Request Body:**
```json
{
  "symbol": "BTC-USDT",
  "side": "long",
  "entry_price": 60000,
  "stop_loss": 58000,
  "take_profit": 65000,
  "size": 0.01,
  "signal_id": "123456789",
  "timestamp": "2025-12-07T12:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "signal_id": "123456789",
  "order_id": "blofin_order_12345",
  "message": "Trade executed successfully",
  "status": "executed",
  "executed_at": "2025-12-07T12:00:01Z"
}
```

## Microservices Benefits

### 1. **Independence**
- Each service can be developed, tested, and deployed separately
- No shared code except data models
- Services communicate via well-defined API

### 2. **Scalability**
- Can run multiple Discord bots feeding one Trading Server
- Can add other signal sources (Telegram, webhooks) easily
- Trading Server can handle multiple concurrent requests

### 3. **Security**
- Discord Bot has no access to exchange credentials
- Trading Server can run on secure VPS with firewall
- API key authentication between services

### 4. **Maintainability**
- Changes to parsing logic don't affect trading
- Can switch exchanges by only modifying Trading Server
- Easy to add features to one service

### 5. **Testing**
- Services can be tested independently
- Mock Trading Server for bot testing
- Mock signal sender for server testing

## Deployment Options

### Option 1: Both Local
```
Local Machine
├── Discord Bot (port N/A)
└── Trading Server (port 8000)
```

### Option 2: Bot Local, Server Remote
```
Local Machine                  VPS (Secure)
├── Discord Bot ─────────────> Trading Server
                  Internet     (Firewall: only bot IP)
```

### Option 3: Both Remote
```
VPS 1                          VPS 2 (Secure)
├── Discord Bot ─────────────> Trading Server
                  VPN/Private  (Firewall: only VPS1)
```

## Extension Points

### Adding New Signal Sources

Create new listener service following same pattern:
```
New Source → Parser → HTTP POST → Trading Server
```

### Adding New Exchanges

Replace `blofin_client.py` with new exchange client:
- Implement same methods (place_order, set_stop_loss, etc.)
- Update `server.py` imports
- No changes needed to Discord Bot

### Adding Features

**Signal validation rules:**
- Modify `shared/models.py` → `TradeSignal.validate()`

**New signal formats:**
- Modify `discord-bot/parser.py` → Add to `PATTERNS`

**Risk management:**
- Modify `trading-server/server.py` → Add checks before execution

**Notifications:**
- Add webhook calls in `trading-server/server.py`

## State Management

### Discord Bot
- **Stateless** - no persistent state
- Statistics in memory (reset on restart)
- Logs to file

### Trading Server
- **Stateless** - no persistent state
- Statistics in memory
- Can add database for trade history (optional)

### Future: Shared Database (Optional)
```
Discord Bot ──┐
              ├──> Database <──> Trading Server
Other Source ─┘
```

## Monitoring

### Health Checks

**Trading Server:**
```bash
GET /health
Response: {"status": "healthy", "service": "trading-server"}
```

**Discord Bot:**
- Discord command: `!health`
- Checks Trading Server connectivity

### Logs

**Structured logging:**
- Timestamp
- Level (INFO, WARNING, ERROR)
- Component
- Message

**Log files:**
- `discord-bot/discord_bot.log`
- `trading-server/trading_server.log`

### Metrics (via API)

**Trading Server:**
```bash
GET /api/v1/stats
Response: {
  "orders_placed": 42,
  "orders_failed": 1,
  "api_calls": 100
}
```

**Discord Bot:**
Discord command: `!stats`

---

## Quick Reference

**Start Everything:**
```powershell
.\run.ps1
```

**Test Parser:**
```powershell
cd discord-bot
python parser.py
```

**Test Server:**
```powershell
curl http://localhost:8000/health
```

**Add Signal Format:**
Edit `discord-bot/parser.py`

**Change Exchange:**
Edit `trading-server/blofin_client.py`

**Modify Risk Rules:**
Edit `trading-server/server.py`
