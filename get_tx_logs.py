import urllib.request
import json

tx_hash = "0x5ff90db49c560ef12f8e4c20d6c9d9e4a153fc9eeac6e64a41c383e32b31522f"
url = f"https://eth.blockscout.com/api/v2/transactions/{tx_hash}/logs"

print(f"Fetching logs of tx {tx_hash}:")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        items = data.get('items', [])
        print(f"Found {len(items)} logs.")
        for i, item in enumerate(items):
            print(f"Log {i}:")
            print(f"  Address: {item['address']['hash']}")
            topics = [t for t in item.get('topics', [])]
            print(f"  Topics: {topics}")
            print(f"  Data: {item.get('data')}")
except Exception as e:
    print(f"Failed: {e}")
