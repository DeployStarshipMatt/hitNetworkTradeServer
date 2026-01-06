# Testing Your Signal Format

Your Discord channel sends signals in this format:

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
```

## ✅ Parser Updated!

The parser has been updated to handle your exact format. It will:

1. Extract **PAIR** (e.g., TIA/USDT → TIA-USDT)
2. Extract **SIDE** (LONG or SHORT)
3. Extract **ENTRY** price
4. Extract **SL** (stop loss)
5. Extract **TP1** (first take profit target)

## 🧪 Test Locally

Before running the full system, test the parser:

```powershell
cd discord-bot
python test_your_format.py
```

**Expected output:**
```
✅ SUCCESSFULLY PARSED!
Symbol: TIA-USDT
Side: short
Entry: 0.566409
Stop Loss: 0.578367
Take Profit: 0.560457
✅ VALIDATION PASSED - Ready to send to Trading Server!
```

## 📝 Important Notes

### What Gets Extracted:
- **Symbol:** Converted from TIA/USDT to TIA-USDT (BloFin format)
- **Side:** SHORT becomes "short", LONG becomes "long"
- **Entry:** The entry price
- **Stop Loss:** The SL price
- **Take Profit:** Uses TP1 (the first target)

### What's Ignored (for now):
- TP2, TP3 (only TP1 is used)
- Leverage (you can configure default in trading-server/.env)
- SIZE percentage (you can configure fixed size in trading-server/.env)
- Risk level indicators
- R:R ratios

### Why TP1 Only?

The system currently places **one take profit order** at TP1. If you want to use multiple TPs:

**Option 1:** Set TP to TP3 (the final target) and manage intermediate exits manually

**Option 2:** Modify the parser to extract all TPs and update the trading server to place multiple TP orders (more advanced)

## 🎯 Next Steps

1. **Test the parser** (run `test_your_format.py`)
2. **Run setup** (`.\setup.ps1` from root)
3. **Configure .env files**
4. **Start services** (`.\run.ps1` from root)
5. **Post a signal** in your Discord channel
6. **Check the bot reaction** (⏳ → ✅ or ❌)

## 🔧 Configuration

In `trading-server\.env`, you can set:

```env
# Default size for all trades (in contracts)
DEFAULT_SIZE=0.01

# Or calculate size based on risk
RISK_PER_TRADE_PERCENT=1

# Default leverage (if not using signal's leverage)
DEFAULT_LEVERAGE=10
```

## 🚨 Testing Checklist

Before going live:

- [ ] Parser extracts all fields correctly
- [ ] Symbol converts TIA/USDT → TIA-USDT
- [ ] Side SHORT → "short", LONG → "long"
- [ ] Entry, SL, and TP1 are numbers
- [ ] Validation passes (SL below entry for long, above for short)
- [ ] Bot reacts to message in Discord
- [ ] Order executes on BloFin demo
- [ ] Stop loss is set correctly
- [ ] Take profit is set correctly

## 🐛 Troubleshooting

**Parser fails:**
- Check the exact format in Discord (copy-paste it)
- Test with `test_your_format.py`
- The regex pattern is in `parser.py` under `'trading_signal_alert'`

**Validation fails:**
- For SHORT: SL should be ABOVE entry, TP should be BELOW entry
- For LONG: SL should be BELOW entry, TP should be ABOVE entry
- Check that prices are positive numbers

**Bot doesn't react:**
- Verify `DISCORD_CHANNEL_ID` is correct
- Bot must have permissions in channel
- Check bot is online in Discord

## 📊 Example Test

1. Start services: `.\run.ps1`
2. In Discord, use command:
   ```
   !test **PAIR:** TIA/USDT **SIDE:** SHORT **ENTRY:** `0.566` **SL:** `0.578` **TP1:** `0.560`
   ```
3. Bot should reply with parsed values
4. Then post a real signal and it will execute!

---

**Your format is now supported!** 🎉
