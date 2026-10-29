import urllib.request
import json

addrs = [
    "0x7e28895e2234394f21e931565007793c7446c4eb",
    "0x96d80118fe08d6d63cdf4bdd91bd56934f0e9d24",
    "0xff4a27201f6d9975d19fe4c539fc6c0048da06c4",
    "0x22a665e4abe0930d4d7f9241b101fc2f7d776b40"
]

for addr in addrs:
    url = f"https://eth.blockscout.com/api/v2/addresses/{addr}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Address {addr}:")
            print(f"  Name: {data.get('name')}")
            print(f"  Creation Tx: {data.get('creation_transaction_hash')}")
            print(f"  Creator: {data.get('creator_address_hash')}")
            print("-" * 30)
    except Exception as e:
        print(f"Failed for {addr}: {e}")
