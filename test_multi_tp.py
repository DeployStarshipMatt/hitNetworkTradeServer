#!/usr/bin/env python3
"""Test multi-TP parsing and execution"""

import sys
from pathlib import Path

# Add parent to path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "discord-bot"))

from parser import SignalParser
import json

# Test signal with multiple TPs
test_signal = """**TRADING SIGNAL ALERT**

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

**⚖️LEVERAGE:** 16x"""

parser = SignalParser()
signal = parser.parse(test_signal)

if signal:
    print("✅ Signal parsed successfully!")
    print(json.dumps(signal.to_dict(), indent=2))
    
    # Check TPs
    print(f"\n📊 Take Profits:")
    print(f"  TP1: {signal.take_profit}")
    print(f"  TP2: {signal.take_profit_2}")
    print(f"  TP3: {signal.take_profit_3}")
else:
    print("❌ Failed to parse signal")
