# BloFin POST Trade Fix Summary

## Problem
POST requests to BloFin API were failing with "Signature verification failed" (error 152409), while GET requests worked fine.

## Root Causes

### 1. Missing Required Field
The `positionSide` field is **REQUIRED** for all order placements:
- For One-way Mode: use `"net"`  
- For Hedge Mode: use `"long"` or `"short"`

### 2. JSON Key Ordering in Signature
BloFin's HMAC signature requires the **exact JSON string** used in the signature to match the JSON sent in the HTTP body. Using `requests.post(json=dict)` re-serializes the dictionary, potentially changing key order and breaking the signature.

## Solution

### Required Code Changes

1. **Add `positionSide` to all order payloads:**
```python
payload = {
    "instId": symbol,
    "marginMode": trade_mode,
    "positionSide": "net",  # REQUIRED
    "side": api_side,
    "orderType": "market",
    "size": str(size)
}
```

2. **Use `data=` instead of `json=` in requests.post():**
```python
# Generate signature with ordered JSON
body_str = json.dumps(sorted_body, separators=(',', ':'))
signature = generate_signature(..., body_str)

# Send request with same pre-serialized JSON
response = requests.post(url, headers=headers, data=body_str)  # NOT json=body
```

3. **Maintain consistent key order:**
```python
doc_order = ["instId", "marginMode", "positionSide", "side", "orderType", "price", "size"]
sorted_body = {k: body[k] for k in doc_order if k in body}
```

## Verification
- **Test Result**: Order ID `8000003539811` successfully placed
- **GET requests**: Still working (balance, margin-mode, etc.)
- **POST requests**: Now working with proper signature

## Files Modified
- `trading-server/blofin_client.py`: Updated `_request()` method to use `data=` parameter
- `trading-server/blofin_auth.py`: Added `positionSide` to key order list
- `test_blofin_trade.py`: Added `positionSide` field to test payload

## Key Takeaways
1. Always use `data=json_string` for APIs that sign the request body
2. BloFin requires exact JSON string match between signature and request
3. Python dict key order is preserved (Python 3.7+) but `requests.json=` may reorder
4. All BloFin order endpoints require `positionSide` field

---
**Date**: 2024-12-31  
**Status**: ✅ RESOLVED
