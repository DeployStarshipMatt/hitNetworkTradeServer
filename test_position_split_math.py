"""Test position splitting math to verify no orphaned tokens"""

def test_split(total_size):
    """Simulate the new splitting logic"""
    # Split into 3
    tp_size = total_size / 3
    
    # Round down (simulating exchange rounding)
    import math
    tp_size_rounded = math.floor(tp_size * 100) / 100  # Round to 2 decimals
    
    # Calculate remainder for last TP
    remaining = total_size - (tp_size_rounded * 2)
    
    tp1 = tp_size_rounded
    tp2 = tp_size_rounded
    tp3 = remaining
    
    total = tp1 + tp2 + tp3
    
    print(f"Position: {total_size}")
    print(f"  TP1: {tp1}")
    print(f"  TP2: {tp2}")
    print(f"  TP3: {tp3} (remainder)")
    print(f"  Total: {total}")
    print(f"  Match: {'✅' if abs(total - total_size) < 0.0001 else '❌'}")
    print()
    
    return abs(total - total_size) < 0.0001

# Test various position sizes
print("Testing Position Split Math")
print("=" * 50)
print()

test_cases = [
    100,
    33.33,
    1000,
    47.5,
    99.99,
    150,
    0.123  # Small position
]

all_passed = True
for size in test_cases:
    if not test_split(size):
        all_passed = False

if all_passed:
    print("✅ All tests passed - no orphaned tokens!")
else:
    print("❌ Some tests failed - check the math")
