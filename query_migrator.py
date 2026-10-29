import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"
trams_master_address = "0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0"

def eth_call(to, sig):
    sel = "0x" + Web3.keccak(text=sig)[:4].hex()
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": to, "data": sel}, "latest"]
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))['result']
            return bytes.fromhex(res[2:])
    except Exception as e:
        return None

res = eth_call(trams_master_address, "migrator()")
if res:
    val = eth_abi.decode(['address'], res)[0]
    print(f"Migrator: {val}")
else:
    print("Migrator call failed")
