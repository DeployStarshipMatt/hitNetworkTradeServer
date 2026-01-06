# Quick Start Guide

## Overview

This system automatically trades on BloFin based on signals posted in a Discord channel.

**Architecture:** Discord Bot (listener) → Trading Server (executor) → BloFin Exchange

## Installation

### 1. Run Setup Script

```powershell
.\setup.ps1
```

This creates virtual environments and installs all dependencies.

### 2. Get Discord Bot Token

1. Visit https://discord.com/developers/applications
2. Select your application (Client ID: 1451666641728307211)
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Invite bot to your server using this URL:
   ```
   https://discord.com/oauth2/authorize?client_id=1451666641728307211&permissions=66560&integration_type=0&scope=bot
   ```
   (Bot will have permissions: Read Messages, Send Messages, Add Reactions)
6. Enable Developer Mode in Discord (Settings → Advanced)
7. Right-click your channel → Copy ID

### 3. Get BloFin API Keys

1. Visit https://www.blofin.com and log in
2. Profile → API Management → Create API Key
3. Name it (e.g., "Discord Trading Bot")
4. Permissions: ✅ Trade, ❌ Withdraw (NEVER enable withdraw!)
5. Set a passphrase (save it!)
6. Complete 2FA
7. Copy: API Key, Secret Key, Passphrase

**For testing, use demo environment:**
- Demo URL: `https://demo-trading-openapi.blofin.com`
- Register at https://www.blofin.com to get demo account

### 4. Configure Services

**Trading Server** (`trading-server\.env`):
```env
API_KEY=generate_random_string_here
BLOFIN_API_KEY=your_blofin_api_key
BLOFIN_SECRET_KEY=your_blofin_secret_key
BLOFIN_PASSPHRASE=your_passphrase
BLOFIN_BASE_URL=https://demo-trading-openapi.blofin.com
```

**Discord Bot** (`discord-bot\.env`):
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=1234567890123456789
TRADING_SERVER_URL=http://localhost:8000
TRADING_SERVER_API_KEY=same_as_trading_server_api_key
```

**Important:** `TRADING_SERVER_API_KEY` must match `API_KEY` in trading-server!

### 5. Run Services

```powershell
.\run.ps1
```

This opens two windows:
- Window 1: Trading Server (port 8000)
- Window 2: Discord Bot

## Signal Format

The bot supports multiple formats:

### Standard Format
```
🚨 LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01
SHORT ETH-USDT Entry: 3500 SL: 3600 TP: 3200
```

### Compact Format
```
LONG BTCUSDT 60000/58000/65000
SHORT ETH-USDT 3500/3600/3200
```

### Emoji Format
```
📈 BTC-USDT 💰 60000 🛑 58000 🎯 65000
📉 ETH-USDT 💰 3500 🛑 3600 🎯 3200
```

**Required:**
- Side: `LONG`, `SHORT`, `BUY`, `SELL`, or emojis (📈📉)
- Symbol: `BTC-USDT`, `ETH-USDT`, etc.

**Optional:**
- Entry price (if omitted, uses market order)
- Stop loss
- Take profit
- Size (defaults to 0.01)

## Discord Commands

In the monitored channel:

- `!test <message>` - Test parser with a message
- `!stats` - Show bot statistics
- `!health` - Check Trading Server connection

## Testing

### 1. Test Parser Locally

```powershell
cd discord-bot
.\venv\Scripts\Activate.ps1
python parser.py
```

### 2. Test Trading Server

```powershell
# Check health
curl http://localhost:8000/health

# Test trade (won't execute without valid BloFin keys)
curl -X POST http://localhost:8000/api/v1/trade -H "Content-Type: application/json" -H "X-API-Key: your_api_key" -d "{\"symbol\":\"BTC-USDT\",\"side\":\"long\",\"size\":0.01}"
```

### 3. Test in Discord

Use `!test` command:
```
!test LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000
```

## Monitoring

### Check Logs

**Trading Server:**
- Console: Real-time in the server window
- File: `trading-server\trading_server.log`

**Discord Bot:**
- Console: Real-time in the bot window
- File: `discord-bot\discord_bot.log`

### View Statistics

In Discord: `!stats`

Via API:
```powershell
curl http://localhost:8000/api/v1/stats -H "X-API-Key: your_api_key"
```

## Troubleshooting

### Bot not responding
- ✅ Check bot is online in Discord
- ✅ Verify correct channel ID
- ✅ Bot has permissions (Read Messages, Send Messages)

### Signals not parsing
- ✅ Use `!test` command to verify format
- ✅ Check console logs for parsing attempts
- ✅ Add custom pattern in `parser.py` if needed

### Trading Server unreachable
- ✅ Check server window for errors
- ✅ Verify port 8000 is not in use
- ✅ Check `TRADING_SERVER_URL` in bot .env

### BloFin authentication failed
- ✅ Verify API keys are correct
- ✅ Check passphrase matches
- ✅ Ensure API key has Trade permission
- ✅ Try demo environment first

### Orders rejected
- ✅ Check BloFin demo account has balance
- ✅ Verify symbol format (BTC-USDT not BTCUSDT)
- ✅ Check position size is valid
- ✅ Review error code in logs

## Security Best Practices

1. ✅ **Never share** your `.env` files
2. ✅ **Use demo environment** for testing
3. ✅ **Never enable** Withdraw permission on API keys
4. ✅ **Whitelist IP addresses** on BloFin if possible
5. ✅ **Start with small sizes** when going live
6. ✅ **Monitor regularly** - check logs daily
7. ✅ **Set position limits** in trading-server .env

## Adding Custom Signal Formats

Edit `discord-bot\parser.py`:

```python
PATTERNS = {
    # Add your custom pattern
    'my_format': re.compile(
        r'(?P<side>long|short)\s+'
        r'(?P<symbol>[A-Z]+-[A-Z]+)\s+'
        r'@\s*(?P<entry>[\d.]+)',
        re.IGNORECASE
    )
}
```

Test it:
```powershell
python parser.py
```

## Production Deployment

### For Trading Server (Secure VPS):
1. Deploy to VPS (AWS, DigitalOcean, etc.)
2. Use production BloFin URL
3. Enable IP whitelisting on BloFin
4. Set up systemd/supervisor for auto-restart
5. Configure firewall (only allow bot IP)
6. Use strong API key
7. Enable HTTPS if exposing to internet

### For Discord Bot (Can Run Anywhere):
1. Can run on local machine or separate server
2. Point to production Trading Server URL
3. Use secure channel for communication (VPN/SSH tunnel)
4. Set up auto-restart (systemd/PM2/screen)

## Support

For issues:
1. Check logs first
2. Test components individually
3. Verify configurations
4. Review README in each service folder

---

**Remember:** Always test on demo environment before using real funds!
