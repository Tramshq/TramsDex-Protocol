import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"

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
    except:
        return None

def get_symbol(token):
    res = eth_call(token, "symbol()")
    if res:
        try:
            return eth_abi.decode(['string'], res)[0]
        except:
            return "?"
    return "?"

# Original LP tokens for PID 1, 3, 4
lp_tokens = {
    "PID 1": "0xd66EBAb572E2B711Da516ED27bB38eaD28bE6034",
    "PID 3": "0xc91055133BCb0817D14109d53D493d6c39F47402",
    "PID 4": "0xfF9f9adBe1dDeafDf810fDc9FA8E83F0dE46EaA3"
}

for label, lp in lp_tokens.items():
    print(f"\n{label} original LP {lp}:")
    t0_bytes = eth_call(lp, "token0()")
    t1_bytes = eth_call(lp, "token1()")
    if t0_bytes and t1_bytes:
        t0 = eth_abi.decode(['address'], t0_bytes)[0]
        t1 = eth_abi.decode(['address'], t1_bytes)[0]
        print(f"  token0: {t0} ({get_symbol(t0)})")
        print(f"  token1: {t1} ({get_symbol(t1)})")
    else:
        print("  Not a standard LP pair")

# Let's inspect PID 5 logs
tx_hash = "0xc2b0be6008e9ca5004b78f3f8369a712e559370c85a30ebbe8fa72a10c66bf55"
print(f"\nLogs of PID 5 (Tx: {tx_hash}):")
logs_url = f"https://eth.blockscout.com/api/v2/transactions/{tx_hash}/logs"
try:
    req = urllib.request.Request(logs_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        items = data.get('items', [])
        for i, item in enumerate(items):
            addr = item['address']['hash']
            topics = item.get('topics', [])
            if topics and topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                f_from = "0x" + topics[1][-40:] if len(topics) > 1 else ""
                t_to = "0x" + topics[2][-40:] if len(topics) > 2 else ""
                print(f"  Transfer:")
                print(f"    Token Contract: {addr} ({get_symbol(addr)})")
                print(f"    From: {f_from}")
                print(f"    To: {t_to}")
except Exception as e:
    print(f"Failed to fetch PID 5 logs: {e}")
