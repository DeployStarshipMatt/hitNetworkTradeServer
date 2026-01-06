# Test Signal Examples

Use these examples to test the parser and system functionality.

## ✅ Valid Signals (Should Parse Successfully)

### Your Trading Signal Alert Format

```
**TRADING SIGNAL ALERT**

**📝PAIR:** TIA/USDT __(LOW RISK)__🟢

**TYPE:** __SWING 🚀__
**SIZE: 1-4%**
**SIDE:** __SHORT📉__

**📍ENTRY:** `0.566409`
**✖️SL:** `0.578367`

**💰TAKE PROFIT TARGETS:**
**TP1:** `0.560457`
**TP2:** `0.55628`
**TP3:** `0.531816`

**⚖️LEVERAGE:** 16x
```

```
**TRADING SIGNAL ALERT**
**📝PAIR:** BTC/USDT
**SIDE:** __LONG📈__
**📍ENTRY:** `60000`
**✖️SL:** `58000`
**TP1:** `65000`
```

### Standard Format

```
🚨 LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01
```

```
SHORT ETH-USDT Entry: 3500 SL: 3600 TP: 3200 Size: 0.05
```

```
BUY BTC-USDT Entry: 50000 SL: 48000 TP: 55000
```

```
SELL SOL-USDT Entry: 100 SL: 105 TP: 90
```

### Without Entry Price (Market Order)

```
LONG BTC-USDT SL: 58000 TP: 65000 Size: 0.01
```

```
SHORT ETH-USDT SL: 3600 TP: 3200
```

### Compact Format

```
LONG BTCUSDT 60000/58000/65000
```

```
SHORT ETHUSDT 3500/3600/3200
```

### Emoji Format

```
📈 BTC-USDT 💰 60000 🛑 58000 🎯 65000
```

```
📉 ETH-USDT 💰 3500 🛑 3600 🎯 3200
```

### Minimal Format

```
LONG BTC-USDT
```

```
SHORT ETH-USDT 3500
```

### With Signal Indicators

```
🚨 SIGNAL 🚨
LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000
```

```
💎 TRADE ALERT 💎
SHORT ETH-USDT Entry: 3500 SL: 3600 TP: 3200 Size: 0.1
```

## ❌ Invalid Signals (Should Fail Validation)

### Missing Symbol

```
LONG Entry: 60000 SL: 58000
```

### Missing Side

```
BTC-USDT Entry: 60000 SL: 58000
```

### Invalid Stop Loss (Long - SL Above Entry)

```
LONG BTC-USDT Entry: 60000 SL: 62000 TP: 65000
```

### Invalid Take Profit (Long - TP Below Entry)

```
LONG BTC-USDT Entry: 60000 SL: 58000 TP: 59000
```

### Invalid Stop Loss (Short - SL Below Entry)

```
SHORT ETH-USDT Entry: 3500 SL: 3400 TP: 3200
```

### Invalid Take Profit (Short - TP Above Entry)

```
SHORT ETH-USDT Entry: 3500 SL: 3600 TP: 3600
```

### Negative Values

```
LONG BTC-USDT Entry: -60000 SL: 58000 TP: 65000
```

### Zero Size

```
LONG BTC-USDT Entry: 60000 Size: 0
```

## 🧪 Testing with Discord Bot

### Test Parser Command

In your Discord channel:

```
!test LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000
```

Expected response:
```
✅ Parsed Successfully
Symbol: BTC-USDT
Side: long
Entry: 60000
SL: 58000
TP: 65000
```

### Test Invalid Format

```
!test This is just a random message
```

Expected response:
```
❌ Could not parse message as a trade signal
```

## 🧪 Testing Parser Locally

Run the parser test script:

```powershell
cd discord-bot
.\venv\Scripts\Activate.ps1
python parser.py
```

This will test all built-in patterns and show results.

## 🧪 Testing Trading Server

### Test Health Endpoint

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "service": "trading-server",
  "status": "healthy",
  "timestamp": "2025-12-07T12:00:00Z",
  "details": {
    "blofin": "connected"
  }
}
```

### Test Trade Endpoint (with Mock Data)

```powershell
curl -X POST http://localhost:8000/api/v1/trade `
  -H "Content-Type: application/json" `
  -H "X-API-Key: your_api_key" `
  -d '{
    "symbol": "BTC-USDT",
    "side": "long",
    "entry_price": 60000,
    "stop_loss": 58000,
    "take_profit": 65000,
    "size": 0.01
  }'
```

## 📝 Creating Your Own Test Cases

### Python Script

Create `test_parser.py`:

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from parser import parse_signal

test_cases = [
    "LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000",
    "SHORT ETH-USDT 3500/3600/3200",
    "📈 SOL-USDT 💰 100 🛑 95 🎯 110"
]

for msg in test_cases:
    print(f"\nTesting: {msg}")
    signal = parse_signal(msg)
    if signal:
        print(f"✅ Symbol: {signal.symbol}, Side: {signal.side}")
        print(f"   Entry: {signal.entry_price}, SL: {signal.stop_loss}, TP: {signal.take_profit}")
    else:
        print("❌ Failed to parse")
```

Run it:
```powershell
python test_parser.py
```

## 🎯 End-to-End Test Workflow

1. **Start Services**
   ```powershell
   .\run.ps1
   ```

2. **Check Health**
   ```
   !health
   ```
   Should show "✅ Trading Server is healthy"

3. **Test Parser**
   ```
   !test LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000
   ```
   Should show parsed values

4. **Post Real Signal** (on demo!)
   ```
   LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01
   ```
   Bot should:
   - React with ⏳ (processing)
   - Change to ✅ (success) or ❌ (failed)
   - Reply with execution details

5. **Check Statistics**
   ```
   !stats
   ```
   Should show message count, signals detected, etc.

6. **Check Logs**
   - `discord-bot/discord_bot.log`
   - `trading-server/trading_server.log`

## 🔍 What to Look For

### Successful Execution
- Bot reacts with ✅
- Reply message shows order ID
- Trading Server log shows "✅ Order placed successfully"
- BloFin shows order in demo account

### Failed Execution
- Bot reacts with ❌
- Reply message shows error
- Trading Server log shows error details
- Check error code for troubleshooting

### Common Issues

**"Authentication failed"**
- Check BloFin API keys in trading-server/.env
- Verify passphrase is correct

**"Invalid signal format"**
- Use !test to verify format
- Check parser patterns in parser.py

**"Trading Server unreachable"**
- Verify server is running on port 8000
- Check TRADING_SERVER_URL in discord-bot/.env

**"Insufficient balance"**
- Check BloFin demo account has funds
- Reduce position size

## 📊 Expected Behavior

### Parser Statistics
After testing several signals:
```
Total Parsed: 10
Successful: 8
Failed: 2
By Pattern:
  standard: 6
  compact: 1
  emoji: 1
```

### Trading Server Statistics
After executing trades:
```
Orders Placed: 5
Orders Failed: 1
API Calls: 15
API Errors: 1
```

### Discord Bot Statistics
```
Messages Seen: 50
Signals Detected: 8
Signals Sent: 7
Signals Failed: 1
```

## 🚀 Production Testing Checklist

Before going live:

- [ ] Test all signal formats on demo
- [ ] Verify stop loss is set correctly
- [ ] Verify take profit is set correctly
- [ ] Test with invalid signals (should reject)
- [ ] Test with various position sizes
- [ ] Check order execution speed
- [ ] Verify error handling works
- [ ] Test with Trading Server restart
- [ ] Test with Discord Bot restart
- [ ] Monitor for 24 hours on demo
- [ ] Start with minimum size on production

## 📝 Notes

- Always test on BloFin demo first
- Use small sizes initially (0.01 or less)
- Monitor logs closely during testing
- Keep test signals in a separate channel
- Document any custom formats you add

---

**Remember:** Paper trade on demo until you're confident everything works!
