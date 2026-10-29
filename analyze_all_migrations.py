import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"

# Successful migrate transactions from TramsMaster history
migrate_txs = [
    ("PID 14", "0x5a6f346209809907f623665bc6208773f94d6b5b1c94dd1f50ce4fea005764cc"),
    ("PID 13", "0xb647e6e4607e2640f132adc6d356650e0b9f7c75a333d872e04d73ad7ee0d2d3"),
    ("PID 12", "0xe3bcc5158a30d14c5414082854b40d22adc7f19021163382605cd27158075422"),
    ("PID 11", "0x8c607f6f72c9f5d6c0415b9ef9ae0d4c427412f584b8d9983a097f0abe5c0fa8"),
    ("PID 10", "0xfafc6ceff3e9897febcbb9334a57b4e0357653a4d220d746cda0af2237e3a02d"),
    ("PID 9", "0x9286343a2f77f5189c98a3556d27fd1ef64e6eea71118ca04702958a036e74ee"),
    ("PID 8", "0x9e3fbd581118b52c9fa6fae577cd172ba12fda5c63fd56f9e10dec8fcfe589d5"),
    ("PID 7", "0x3d9aecec5f0635b833d6dee207bc632604a9ae6081ee2fd381168eb14e388fc6"),
    ("PID 6", "0x0a8a8f444c89486fbc53fe89c98a9d668a412be7eb34eb385a3d86ebb835aa49"),
    ("PID 0", "0xab4b702dfb0215848afb5a8ba1e428b4b3bb2b8e53b0bc71e13813ab4c6b0f0c")
]

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

def eth_call(to, sig):
    sel = "0x" + Web3.keccak(text=sig)[:4].hex()
    try:
        res = rpc_call("eth_call", [{"to": to, "data": sel}, "latest"])
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

for label, tx_hash in migrate_txs:
    print(f"\nAnalyzing {label} (Tx: {tx_hash}):")
    logs_url = f"https://eth.blockscout.com/api/v2/transactions/{tx_hash}/logs"
    try:
        req = urllib.request.Request(logs_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('items', [])
            
            original_lp = None
            new_lp = None
            underlying = []
            
            for item in items:
                addr = item['address']['hash']
                topics = item.get('topics', [])
                if topics and topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                    f_from = "0x" + topics[1][-40:] if len(topics) > 1 else ""
                    t_to = "0x" + topics[2][-40:] if len(topics) > 2 else ""
                    
                    # If from is TramsMaster (0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0) -> this is the original LP being transferred
                    if f_from.lower() == "0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0":
                        original_lp = addr
                    # If to is TramsMaster -> this is the new LP being received
                    elif t_to.lower() == "0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0":
                        new_lp = addr
                    # If from is original LP contract -> this is underlying token redeem transfer
                    elif original_lp and f_from.lower() == original_lp.lower():
                        if addr.lower() not in [u.lower() for u in underlying]:
                            underlying.append(addr)
            
            # Print results
            orig_sym = get_symbol(original_lp) if original_lp else "?"
            new_sym = get_symbol(new_lp) if new_lp else "?"
            und_syms = [get_symbol(u) for u in underlying]
            
            print(f"  Original LP: {original_lp} ({orig_sym})")
            print(f"  New LP:      {new_lp} ({new_sym})")
            print(f"  Underlying:  {und_syms} ({underlying})")
            
    except Exception as e:
        print(f"  Failed to analyze {label}: {e}")
