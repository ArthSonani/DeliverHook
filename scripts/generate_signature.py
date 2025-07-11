import hmac
import hashlib
import json
import sys
import ast

def generate_signature(payload: dict, secret_key: str) -> str:
    # Convert payload to bytes with sorted keys for consistent hashing
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Format as "sha256=hexdigest"
    return f"sha256={signature}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  Windows PowerShell:")
        print('    python scripts/generate_signature.py "your_secret_key" \'{"event":"order.created","data":{"order_id":"123"}}\'')
        print("  Linux/Mac:")
        print('    python scripts/generate_signature.py "your_secret_key" \'{"event":"order.created","data":{"order_id":"123"}}\'')
        sys.exit(1)
    
    secret_key = sys.argv[1]
    payload_str = sys.argv[2]
    
    try:
        # Try parsing as JSON first
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, try using ast.literal_eval
            payload = ast.literal_eval(payload_str)
        
        signature = generate_signature(payload, secret_key)
        print("\nSignature generated successfully!")
        print(f"Signature: {signature}")
        print(f"Header: X-Hub-Signature-256: {signature}")
        print("\nExample curl command:")
        print(f'curl -X POST http://localhost:8000/ingest/1 \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -H "X-Hub-Signature-256: {signature}" \\')
        print(f'  -H "X-Event-Type: order.created" \\')
        print(f'  -d \'{json.dumps(payload)}\'')
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure to properly escape the JSON payload:")
        print("Windows PowerShell example:")
        print('python scripts/generate_signature.py "test_secret_key" \'{"event":"order.created","data":{"order_id":"123"}}\'')
        sys.exit(1) 