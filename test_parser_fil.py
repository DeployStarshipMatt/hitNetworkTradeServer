import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from discord_bot.parser import SignalParser

# Your exact message
message = """TRADING SIGNAL ALERT

📝PAIR: FIL/USDT (MEDIUM RISK)🟡

TYPE: SWING 🚀
SIZE: 1-4%
SIDE: LONG📈

📍ENTRY: 1.295222
✖️SL: 1.220152          (-82.72%)

💰TAKE PROFIT TARGETS:

TP1: 1.337893          (46.12%)
TP2: 1.374898          (86.12%)
TP3: 1.528733          (254.39%)

⚖️LEVERAGE: 14x

TP1: 0.56 R:R
TP2: 1.04 R:R
TP3: 3.08 R:R

⚠️PROTECT YOUR CAPITAL, MANAGE RISK, LETS PRINT!"""

parser = SignalParser()
result = parser.parse(message, message_id="test123")

if result:
    print(f"✅ PARSED SUCCESSFULLY!")
    print(f"Symbol: {result.symbol}")
    print(f"Side: {result.side}")
    print(f"Entry: {result.entry_price}")
    print(f"SL: {result.stop_loss}")
    print(f"TP: {result.take_profit}")
else:
    print("❌ FAILED TO PARSE")
    print("Parser did not match the message")
