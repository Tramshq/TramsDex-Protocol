import urllib.request
import json

addrs = [
    "0xbbb26dd2110f5fc0e69ffd3fa3d5f840147a706d",
    "0x7e28895e2234394f21e931565007793c7446c4eb",
    "0x96d80118fe08d6d63cdf4bdd91bd56934f0e9d24",
    "0x44ac01c8c7359d7262c159ea9ca33f05282a5f3e"
]

for addr in addrs:
    print(f"Querying Blockscout for {addr}:")
    url = f"https://eth.blockscout.com/api/v2/addresses/{addr}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"  Name: {data.get('name')}")
            print(f"  Is Contract: {data.get('is_contract')}")
            print(f"  Coin Balance: {data.get('coin_balance')}")
            # print creation transaction
            print(f"  Creator: {data.get('creator_address_hash')}")
            print(f"  Creation Tx: {data.get('creation_tx_hash')}")
    except Exception as e:
        print(f"  Failed: {e}")
