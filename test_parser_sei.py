"""Test parser with SEI signal"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'discord-bot'))

from parser import SignalParser

# Exact signal from Discord
signal_text = """**TRADING SIGNAL ALERT** 

**📝PAIR:** SEI/USDT #1131
__(MEDIUM RISK)__🟡

**TYPE:** __POSITION__
**SIZE: 1-4%**
**SIDE:** __SHORT📉__

**📍ENTRY:** `0.125294`
**✖️SL:** `0.127698`          (-72.52%)

**💰TAKE PROFIT TARGETS:**

**TP1:** `0.123615`      (46.9%)
**TP2:** `0.121812`      (97.27%)
**TP3:** `0.12017`      (148.16%)

**⚖️LEVERAGE:** 35x

**TP1:** 0.65 R:R
**TP2:** 1.34 R:R
**TP3:** 2.04 R:R

**⚠️PROTECT YOUR CAPITAL, MANAGE RISK, LETS PRINT!**

<@&1440803074686976153>"""

parser = SignalParser()
signal = parser.parse(signal_text, message_id="test_1131")

if signal:
    print("✅ Successfully parsed signal:")
    print(f"   Symbol: {signal.symbol}")
    print(f"   Side: {signal.side}")
    print(f"   Entry: {signal.entry_price}")
    print(f"   Stop Loss: {signal.stop_loss}")
    print(f"   Take Profit: {signal.take_profit}")
    print(f"   Size: {signal.size}")
else:
    print("❌ Failed to parse signal")
