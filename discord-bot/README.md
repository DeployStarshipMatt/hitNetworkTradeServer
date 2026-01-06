# Discord Bot Service

Monitors Discord channel for trade signals and forwards them to the Trading Server.

## Features

- ✅ **Multi-format parser** - Supports various signal formats
- ✅ **Real-time monitoring** - Instant signal detection
- ✅ **Retry logic** - Handles network failures gracefully
- ✅ **User filtering** - Optional user/role restrictions
- ✅ **Statistics tracking** - Monitor bot performance
- ✅ **Commands** - `!stats`, `!health`, `!test`

## Self-Contained Design

This service is **completely independent**:
- No trading logic or API keys
- Can be modified without affecting Trading Server
- Pluggable parser - add new formats easily
- Switchable communication layer (REST/Queue/DB)

## Setup

### 1. Install Dependencies

```powershell
cd discord-bot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=1234567890
TRADING_SERVER_URL=http://localhost:8000
TRADING_SERVER_API_KEY=shared_secret
```

**Get Discord Bot Token:**
1. Go to https://discord.com/developers
2. Select your application (Client ID: 1451666641728307211)
3. Bot section → Reset Token → Copy
4. Invite bot to server using this URL:
   ```
   https://discord.com/oauth2/authorize?client_id=1451666641728307211&permissions=66560&integration_type=0&scope=bot
   ```
5. Bot will have permissions: Read Messages, Send Messages, Add Reactions

**Get Channel ID:**
1. Enable Developer Mode in Discord settings
2. Right-click channel → Copy ID

### 3. Run Bot

```powershell
.\venv\Scripts\Activate.ps1
python bot.py
```

## Architecture

```
bot.py (main)
├── parser.py (signal extraction)
├── trading_client.py (server communication)
└── shared/models.py (data contracts)
```

### Adding New Signal Formats

Edit `parser.py` → Add to `PATTERNS` dictionary:

```python
PATTERNS = {
    'your_format': re.compile(
        r'your_regex_pattern',
        re.IGNORECASE
    )
}
```

### Testing Parser

```powershell
python parser.py
```

## Discord Commands

- `!stats` - Show bot statistics
- `!health` - Check Trading Server connection
- `!test <message>` - Test parser with a message

## Logs

- Console output for real-time monitoring
- `discord_bot.log` for persistent logs

## Troubleshooting

**Bot not responding:**
- Check bot has correct permissions in channel
- Verify `DISCORD_CHANNEL_ID` is correct
- Check bot is online in Discord

**Signals not parsing:**
- Use `!test` command to test format
- Check parser.py for supported patterns
- Add custom pattern if needed

**Server connection failed:**
- Verify Trading Server is running
- Check `TRADING_SERVER_URL` and `TRADING_SERVER_API_KEY`
- Use `!health` command to diagnose
