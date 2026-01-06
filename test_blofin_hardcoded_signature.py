import hmac
import hashlib
import base64
import json

# Hardcoded test values (replace with your real values or doc sample)
api_key = "test_api_key"
secret_key = "test_secret_key"
passphrase = "test_passphrase"
method = "GET"
path = "/api/v1/account/margin-mode"
timestamp = "1700000000000"  # Example fixed timestamp
nonce = "123e4567-e89b-12d3-a456-426614174000"  # Example UUID
body = ""  # GET request, so body is empty

# Prehash string as per docs
prehash = f"{path}{method}{timestamp}{nonce}{body}"

# Signature: HMAC-SHA256, hex, then base64
hex_signature = hmac.new(
    secret_key.encode("utf-8"),
    prehash.encode("utf-8"),
    hashlib.sha256
).hexdigest().encode("utf-8")
signature_hex = base64.b64encode(hex_signature).decode("utf-8")

# Signature: HMAC-SHA256, raw digest, then base64
raw_signature = hmac.new(
    secret_key.encode("utf-8"),
    prehash.encode("utf-8"),
    hashlib.sha256
).digest()
signature_raw = base64.b64encode(raw_signature).decode("utf-8")

print("\n=== Hardcoded Signature Debug ===")
print(f"API Key: {api_key}")
print(f"Secret Key: {secret_key}")
print(f"Passphrase: {passphrase}")
print(f"Method: {method}")
print(f"Path: {path}")
print(f"Timestamp: {timestamp}")
print(f"Nonce: {nonce}")
print(f"Body: '{body}'")
print(f"Prehash: '{prehash}'")
print(f"Signature (base64-hex): {signature_hex}")
print(f"Signature (base64-raw): {signature_raw}")
print("Headers (hex):")
print(f"  ACCESS-KEY: {api_key}")
print(f"  ACCESS-SIGN: {signature_hex}")
print(f"  ACCESS-TIMESTAMP: {timestamp}")
print(f"  ACCESS-NONCE: {nonce}")
print(f"  ACCESS-PASSPHRASE: {passphrase}")
print(f"  Content-Type: application/json")
print("Headers (raw):")
print(f"  ACCESS-KEY: {api_key}")
print(f"  ACCESS-SIGN: {signature_raw}")
print(f"  ACCESS-TIMESTAMP: {timestamp}")
print(f"  ACCESS-NONCE: {nonce}")
print(f"  ACCESS-PASSPHRASE: {passphrase}")
print(f"  Content-Type: application/json")
print("=== END DEBUG BLOCK ===\n")
