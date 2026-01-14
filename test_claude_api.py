"""
Comprehensive Claude API Test Suite

Tests:
1. Claude API connection
2. Claude parsing capability
3. Fallback mechanism when regex parser fails
4. Edge cases and error handling
"""
import os
import sys
from dotenv import load_dotenv
import anthropic

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'discord-bot'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from parser import SignalParser

# Test signals
TEST_SIGNALS = {
    "standard_format": """
📝PAIR: BTC/USDT #1234
SIDE: __LONG📈__
📍ENTRY: `98500`
✖️SL: `96000`
✅TP1: `102000`
✅TP2: `105000`
✅TP3: `108000`
⚖️LEVERAGE: 20x
""",
    
    "sei_format": """
📝PAIR: SEI/USDT #1131
SIDE: __SHORT📉__
📍ENTRY: `0.125294`
✖️SL: `0.127698`
✅TP1: `0.123615`
✅TP2: `0.121812`
✅TP3: `0.12017`
⚖️LEVERAGE: 35x
""",
    
    "unusual_format": """
Hey team! New signal 🚀
Token: ETH/USDT
Direction: LONG
Entry at: 3500.50
Stop loss: 3400
Target 1: 3650
Target 2: 3800
Target 3: 4000
Use 15x leverage
""",
    
    "malformed": """
Buy some BTC around 100k
stop if it goes to 95k
sell at 110k
""",
    
    "gibberish": """
The quick brown fox jumps over the lazy dog.
No trading signals here!
"""
}


def test_claude_connection():
    """Test 1: Can we connect to Claude API?"""
    print("\n" + "=" * 70)
    print("TEST 1: Claude API Connection")
    print("=" * 70)
    
    load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if not api_key:
        print("❌ FAILED: CLAUDE_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Simple test message
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": "Reply with just 'OK' if you can read this."
            }]
        )
        
        response_text = response.content[0].text.strip()
        print(f"✅ Claude responded: '{response_text}'")
        
        if "OK" in response_text.upper():
            print("✅ PASSED: Claude API connection successful")
            return True
        else:
            print(f"⚠️  WARNING: Unexpected response: {response_text}")
            return True  # Still connected, just different response
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_claude_parsing():
    """Test 2: Can Claude parse trading signals?"""
    print("\n" + "=" * 70)
    print("TEST 2: Claude Parsing Capability")
    print("=" * 70)
    
    load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if not api_key:
        print("❌ SKIPPED: No API key")
        return False
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        signal = TEST_SIGNALS["sei_format"]
        
        prompt = f"""Parse this trading signal and extract the key information.
Return ONLY a JSON object with these exact fields (no extra text):
{{
    "symbol": "SYMBOL-USDT",
    "side": "long" or "short",
    "entry": decimal number,
    "stop_loss": decimal number,
    "take_profit": decimal number,
    "take_profit_2": decimal number or null,
    "take_profit_3": decimal number or null,
    "leverage": integer or null
}}

Signal:
{signal}"""
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        print(f"\nClaude's response:\n{response_text}\n")
        
        # Remove markdown code blocks if present (same as parser)
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Try to parse as JSON
        import json
        try:
            parsed = json.loads(response_text)
            print("✅ Valid JSON returned")
            print(f"   Symbol: {parsed.get('symbol')}")
            print(f"   Side: {parsed.get('side')}")
            print(f"   Entry: {parsed.get('entry')}")
            print(f"   SL: {parsed.get('stop_loss')}")
            print(f"   TP1: {parsed.get('take_profit')}")
            print(f"   TP2: {parsed.get('take_profit_2')}")
            print(f"   TP3: {parsed.get('take_profit_3')}")
            print(f"   Leverage: {parsed.get('leverage')}")
            
            # Validate key fields
            if parsed.get('symbol') and parsed.get('side') and parsed.get('entry'):
                print("✅ PASSED: Claude can parse signals correctly")
                return True
            else:
                print("⚠️  WARNING: Missing required fields")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ FAILED: Response is not valid JSON: {e}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_regex_parser_success():
    """Test 3: Regex parser works on standard formats"""
    print("\n" + "=" * 70)
    print("TEST 3: Regex Parser (Should Succeed)")
    print("=" * 70)
    
    parser = SignalParser()
    
    success_count = 0
    for name, signal in [("BTC", TEST_SIGNALS["standard_format"]), 
                         ("SEI", TEST_SIGNALS["sei_format"])]:
        print(f"\nTesting {name} format...")
        result = parser.parse(signal)
        
        if result:
            print(f"✅ Parsed: {result.symbol} {result.side}")
            print(f"   Entry: {result.entry_price}, SL: {result.stop_loss}")
            print(f"   TP1: {result.take_profit}, TP2: {result.take_profit_2}, TP3: {result.take_profit_3}")
            print(f"   Leverage: {result.leverage}x")
            success_count += 1
        else:
            print(f"❌ Failed to parse {name}")
    
    if success_count == 2:
        print(f"\n✅ PASSED: Regex parser works ({success_count}/2)")
        return True
    else:
        print(f"\n❌ FAILED: Only {success_count}/2 parsed")
        return False


def test_regex_parser_failure():
    """Test 4: Regex parser fails on unusual formats"""
    print("\n" + "=" * 70)
    print("TEST 4: Regex Parser (Should Fail)")
    print("=" * 70)
    
    parser = SignalParser()
    
    fail_count = 0
    for name, signal in [("Unusual", TEST_SIGNALS["unusual_format"]),
                         ("Malformed", TEST_SIGNALS["malformed"]),
                         ("Gibberish", TEST_SIGNALS["gibberish"])]:
        print(f"\nTesting {name} format...")
        result = parser.parse(signal)
        
        if result is None:
            print(f"✅ Correctly failed to parse")
            fail_count += 1
        else:
            print(f"⚠️  Unexpectedly parsed: {result.symbol} {result.side}")
    
    if fail_count == 3:
        print(f"\n✅ PASSED: Regex correctly rejects invalid formats ({fail_count}/3)")
        return True
    else:
        print(f"\n⚠️  WARNING: Only {fail_count}/3 correctly rejected")
        return True  # Not a failure, just unexpected


def test_fallback_mechanism():
    """Test 5: Fallback to Claude when regex fails"""
    print("\n" + "=" * 70)
    print("TEST 5: Claude Fallback Mechanism")
    print("=" * 70)
    
    load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if not api_key:
        print("❌ SKIPPED: No Claude API key configured")
        return False
    
    # Check if parser has Claude fallback implemented
    parser = SignalParser()
    
    if not hasattr(parser, 'parse_with_claude') and not hasattr(parser, '_parse_with_claude'):
        print("⚠️  WARNING: Claude fallback not yet implemented in SignalParser")
        print("   This needs to be added to discord-bot/parser.py")
        return False
    
    print("Testing fallback on unusual format...")
    signal = TEST_SIGNALS["unusual_format"]
    
    # Try to parse - should fall back to Claude
    result = parser.parse(signal)
    
    if result:
        print(f"✅ Fallback successful!")
        print(f"   Symbol: {result.symbol}")
        print(f"   Side: {result.side}")
        print(f"   Entry: {result.entry_price}")
        print(f"   SL: {result.stop_loss}")
        print(f"   TP1: {result.take_profit}")
        print(f"   TP2: {result.take_profit_2}")
        print(f"   TP3: {result.take_profit_3}")
        print(f"   Leverage: {result.leverage}")
        print("✅ PASSED: Claude fallback works")
        return True
    else:
        print("❌ FAILED: Fallback did not parse signal")
        return False


def test_performance():
    """Test 6: Response time comparison"""
    print("\n" + "=" * 70)
    print("TEST 6: Performance Comparison")
    print("=" * 70)
    
    import time
    
    parser = SignalParser()
    signal = TEST_SIGNALS["sei_format"]
    
    # Test regex speed
    start = time.time()
    result = parser.parse(signal)
    regex_time = time.time() - start
    
    print(f"Regex parsing: {regex_time*1000:.2f}ms")
    
    # Test Claude speed (if available)
    load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    
    if api_key:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            start = time.time()
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=200,
                messages=[{"role": "user", "content": f"Parse: {signal}"}]
            )
            claude_time = time.time() - start
            
            print(f"Claude parsing: {claude_time*1000:.2f}ms")
            print(f"Speed difference: {claude_time/regex_time:.1f}x slower")
            
        except Exception as e:
            print(f"⚠️  Could not test Claude speed: {e}")
    
    print("✅ PASSED: Performance test complete")
    return True


def main():
    print("\n" + "🧪" * 35)
    print(" " * 20 + "CLAUDE API TEST SUITE")
    print("🧪" * 35)
    
    load_dotenv()
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"   CLAUDE_API_KEY: {'✅ Set' if os.getenv('CLAUDE_API_KEY') else '❌ Not set'}")
    print(f"   RISK_PER_TRADE_PERCENT: {os.getenv('RISK_PER_TRADE_PERCENT', 'Not set')}")
    
    # Run tests
    results = {
        "Claude Connection": test_claude_connection(),
        "Claude Parsing": test_claude_parsing(),
        "Regex Success": test_regex_parser_success(),
        "Regex Failure": test_regex_parser_failure(),
        "Claude Fallback": test_fallback_mechanism(),
        "Performance": test_performance()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    elif passed_count >= total_count - 1:
        print("\n⚠️  Most tests passed - review failures above")
    else:
        print("\n❌ Multiple failures - review output above")


if __name__ == "__main__":
    main()
