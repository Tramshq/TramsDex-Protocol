import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"
addr = "0xbbb26dd2110f5fc0e69ffd3fa3d5f840147a706d"

def eth_call(to, sig):
    sel = "0x" + Web3.keccak(text=sig)[:4].hex()
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": to, "data": sel}, "latest"]
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))['result']
            return bytes.fromhex(res[2:])
    except Exception as e:
        return None

sigs = [
    "underlying()",
    "token()",
    "lpToken()",
    "factory()",
    "migrator()",
    "asset()",
    "pool()",
    "owner()"
]

for sig in sigs:
    res = eth_call(addr, sig)
    if res and len(res) >= 32:
        try:
            val = eth_abi.decode(['address'], res[:32])[0]
            print(f"{sig} -> {val}")
        except:
            try:
                val = eth_abi.decode(['string'], res)[0]
                print(f"{sig} -> {val}")
            except:
                print(f"{sig} -> {res.hex()}")
    elif res:
         print(f"{sig} -> {res.hex()}")
    else:
         print(f"{sig} -> failed")
