import urllib.request
import json

addr = "0x44ac01c8c7359d7262c159ea9ca33f05282a5f3e"
url = f"https://eth.blockscout.com/api/v2/addresses/{addr}/transactions?limit=50"

print(f"Fetching transactions of LpToTokenMigrator ({addr}):")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        items = data.get('items', [])
        print(f"Found {len(items)} transactions.")
        for i, tx in enumerate(items):
            print(f"Tx {i}: {tx['hash']}")
            print(f"  From: {tx['from']['hash']}")
            print(f"  To: {tx.get('to') or {}}")
            print(f"  Method: {tx.get('method')}")
            print(f"  Status: {tx.get('status')}")
except Exception as e:
    print(f"Failed: {e}")
