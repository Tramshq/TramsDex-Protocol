import urllib.request
import json

creator = "0x63Cd21d15eD355bB4c4840210f5680bf317cF26b"
url = f"https://eth.blockscout.com/api/v2/addresses/{creator}/transactions"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        items = data.get('items', [])
        print(f"Found {len(items)} transactions for creator.")
        for tx in items:
            to = tx.get('to') or {}
            to_hash = to.get('hash')
            print(f"Tx: {tx['hash']}")
            print(f"  To: {to_hash}")
            print(f"  Method: {tx.get('method')}")
            print(f"  Status: {tx.get('status')}")
            # print raw_input or decoded_input
            inp = tx.get('raw_input', '')
            if inp:
                print(f"  Input: {inp[:100]}...")
            print("-" * 30)
except Exception as e:
    print(f"Failed: {e}")
