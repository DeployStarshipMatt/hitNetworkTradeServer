"""
Test the parser with your exact signal format
"""
import sys
sys.path.append('..')
from parser import SignalParser

test_signal = """**TRADING SIGNAL ALERT**

**📝PAIR:** TIA/USDT __(LOW RISK)__🟢

**TYPE:** __SWING 🚀__
**SIZE: 1-4%**
**SIDE:** __SHORT📉__

**📍ENTRY:** `0.566409`
**✖️SL:** `0.578367`          (-36.73%)

**💰TAKE PROFIT TARGETS:**

**TP1:** `0.560457`          (16.81%)
**TP2:** `0.55628`          (28.61%)
**TP3:** `0.531816`          (100.42%)

**⚖️LEVERAGE:** 16x

**TP1:** 0.46 R:R
**TP2:** 0.78 R:R
**TP3:** 2.73 R:R

**⚠️PROTECT YOUR CAPITAL, MANAGE RISK, LETS PRINT!**"""

parser = SignalParser()
signal = parser.parse(test_signal)

if signal:
    print('✅ SUCCESSFULLY PARSED!')
    print(f'Symbol: {signal.symbol}')
    print(f'Side: {signal.side}')
    print(f'Entry: {signal.entry_price}')
    print(f'Stop Loss: {signal.stop_loss}')
    print(f'Take Profit: {signal.take_profit}')
    print(f'Size: {signal.size}')
    print(f'\nFull signal object:')
    print(signal.to_dict())
    
    is_valid, error = signal.validate()
    if is_valid:
        print('\n✅ VALIDATION PASSED - Ready to send to Trading Server!')
    else:
        print(f'\n❌ VALIDATION FAILED: {error}')
else:
    print('❌ FAILED TO PARSE')
    print(f'\nParser stats: {parser.get_stats()}')
