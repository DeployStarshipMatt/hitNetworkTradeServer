# HIT Network Automation - Discord to BloFin Trading System

🤖 Microservices-based automated trading system that monitors Discord channels for trade signals and executes them on BloFin exchange.

## ✨ Features

- ✅ **Multi-format signal parsing** - Supports various Discord message formats
- ✅ **Microservices architecture** - Completely independent components
- ✅ **Real-time execution** - Instant order placement on signal detection
- ✅ **Risk management** - Stop loss and take profit automation
- ✅ **Secure** - Credentials isolated to Trading Server
- ✅ **Demo mode** - Test with paper trading before going live
- ✅ **Monitoring** - Built-in health checks and statistics
- ✅ **Extensible** - Easy to add new signal sources or exchanges

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│  Discord Bot    │────────>│  Trading Server  │────────>│   BloFin    │
│   (Listener)    │  REST   │   (Executor)     │   API   │  Exchange   │
└─────────────────┘         └──────────────────┘         └─────────────┘
```

**Key Design Principles:**
- Each service is self-contained and can be modified independently
- No shared dependencies except data models
- Communication via well-defined REST API
- Security through separation of concerns

[See full architecture documentation →](ARCHITECTURE.md)

## 📁 Project Structure

```
hitNetworkAutomation/
├── discord-bot/              # Discord listener service
│   ├── bot.py               # Main bot application
│   ├── parser.py            # Signal parsing logic
│   ├── trading_client.py    # HTTP client for Trading Server
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Configuration template
│   └── README.md            # Service documentation
│
├── trading-server/           # Order execution service
│   ├── server.py            # FastAPI application
│   ├── blofin_client.py     # BloFin API integration
│   ├── blofin_auth.py       # HMAC-SHA256 authentication
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Configuration template
│   └── README.md            # Service documentation
│
├── shared/                   # Common data models
│   ├── models.py            # TradeSignal, TradeResponse, etc.
│   └── __init__.py          # Package exports
│
├── setup.ps1                # Automated setup script
├── run.ps1                  # Start both services
├── QUICKSTART.md            # Quick start guide
├── ARCHITECTURE.md          # Architecture details
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Run Setup

```powershell
.\setup.ps1
```

This will:
- Create virtual environments for both services
- Install all dependencies
- Create `.env` files from templates

### 2. Configure Services

**Get Discord Bot Token:**
1. Visit https://discord.com/developers/applications
2. Create New Application → Bot section → Reset Token
3. Copy token to `discord-bot\.env`

**Get BloFin API Keys:**
1. Visit https://www.blofin.com
2. API Management → Create API Key
3. Permissions: ✅ Trade, ❌ Withdraw
4. Copy keys to `trading-server\.env`

**Use demo environment for testing:**
```env
BLOFIN_BASE_URL=https://demo-trading-openapi.blofin.com
```

[See detailed setup instructions →](QUICKSTART.md)

### 3. Start Services

```powershell
.\run.ps1
```

This opens two windows:
- Trading Server (http://localhost:8000)
- Discord Bot

### 4. Test

Post a signal in your Discord channel:
```
🚨 LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000
```

The bot will:
1. ✅ Parse the signal
2. ✅ Send to Trading Server
3. ✅ Execute on BloFin
4. ✅ Reply with confirmation

## 📊 Supported Signal Formats

### Standard Format
```
LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01
SHORT ETH-USDT Entry: 3500 SL: 3600 TP: 3200
```

### Compact Format
```
LONG BTCUSDT 60000/58000/65000
```

### Emoji Format
```
📈 BTC-USDT 💰 60000 🛑 58000 🎯 65000
```

**Add your own format** by editing `discord-bot/parser.py`

## 🎮 Discord Commands

- `!test <message>` - Test parser with a message
- `!stats` - Show bot statistics
- `!health` - Check Trading Server connection

## 🔧 Configuration

### Trading Server (`.env`)
```env
API_KEY=shared_secret_with_bot
BLOFIN_API_KEY=your_api_key
BLOFIN_SECRET_KEY=your_secret
BLOFIN_PASSPHRASE=your_passphrase
BLOFIN_BASE_URL=https://demo-trading-openapi.blofin.com
DEFAULT_TRADE_MODE=cross
MAX_POSITION_SIZE_USD=1000
```

### Discord Bot (`.env`)
```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=1234567890
TRADING_SERVER_URL=http://localhost:8000
TRADING_SERVER_API_KEY=same_as_server
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Complete setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and data flow
- [discord-bot/README.md](discord-bot/README.md) - Discord Bot service
- [trading-server/README.md](trading-server/README.md) - Trading Server service

## 🔐 Security

- ✅ Never commit `.env` files
- ✅ Use demo environment for testing
- ✅ Never enable Withdraw permission
- ✅ Whitelist IP addresses on BloFin
- ✅ Use strong API keys
- ✅ Start with small position sizes

## 🛠️ Extending the System

### Add New Signal Format
Edit `discord-bot/parser.py` and add to `PATTERNS` dictionary.

### Switch to Different Exchange
Replace `trading-server/blofin_client.py` with new exchange client.

### Add Another Signal Source
Create new service following Discord Bot pattern.

### Add Database for Trade History
Modify `trading-server/server.py` to log to database.

**Everything is modular - change one part without affecting others!**

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Statistics
```bash
curl http://localhost:8000/api/v1/stats -H "X-API-Key: your_key"
```

### Logs
- `discord-bot/discord_bot.log`
- `trading-server/trading_server.log`

## ⚠️ Important Notes

1. **Always test on demo first** - Use BloFin demo environment before live trading
2. **Start small** - Use minimal position sizes initially
3. **Monitor regularly** - Check logs and statistics daily
4. **Risk management** - Set appropriate stop losses and position limits
5. **Never share credentials** - Keep `.env` files secure

## 🐛 Troubleshooting

**Bot not responding:**
- Check bot is online in Discord
- Verify channel ID is correct
- Check bot permissions

**Signals not parsing:**
- Use `!test` command
- Check logs for parsing attempts
- Verify signal format matches patterns

**Trading Server errors:**
- Check BloFin API credentials
- Verify demo/production URL is correct
- Check account balance

**Connection issues:**
- Ensure Trading Server is running
- Verify API keys match between services
- Check firewall settings

## 📝 Development Status

**Completed:**
- ✅ Microservices architecture
- ✅ Discord Bot with multi-format parser
- ✅ Trading Server with BloFin integration
- ✅ REST API communication
- ✅ Logging and monitoring
- ✅ Setup and run scripts
- ✅ Comprehensive documentation

**Ready for:**
- ✅ Testing on BloFin demo
- ✅ Live deployment

## 📄 License

This project is for personal/educational use. Trade at your own risk.

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your needs!
