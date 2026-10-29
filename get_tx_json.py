import urllib.request
import json

tx_hash = "0x5ff90db49c560ef12f8e4c20d6c9d9e4a153fc9eeac6e64a41c383e32b31522f"
url = f"https://eth.blockscout.com/api/v2/transactions/{tx_hash}"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Failed: {e}")
