import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"
trams_master = "0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0"

def rpc_call(method, params):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))['result']

start_block = 11141087
end_block = 11141150

print(f"Scanning blocks {start_block} to {end_block} for transactions to TramsMaster...")
for b in range(start_block, end_block + 1):
    block = rpc_call("eth_getBlockByNumber", [hex(b), True])
    if block and block.get("transactions"):
        for tx in block["transactions"]:
            to = tx.get("to")
            if to and to.lower() == trams_master.lower():
                print(f"Block {b} Tx {tx['hash']}:")
                print(f"  From: {tx['from']}")
                inp = tx.get("input")
                print(f"  Input: {inp[:138]}")
                # If it's add(uint256,address,bool)
                # Selector of add is Web3.keccak(text="add(uint256,address,bool)")[:4].hex()
                # Wait, in MasterChef it's add(uint256,address,bool)
                # Let's decode if it starts with 0xfb34b526 or 0xdd2e2692 or similar
                # Let's check selector of add(uint256,address,bool) -> 0x4ffc206d or similar?
                # Actually, let's print the first 10 characters (selector) and the rest
