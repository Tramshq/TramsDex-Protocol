import urllib.request
import json
import eth_abi
from web3 import Web3

url = "https://ethereum-rpc.publicnode.com"
uniswap_factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
migrator_addr = "0x44ac01c8c7359d7262c159ea9ca33f05282a5f3e"

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

def eth_call(to, sig, arg_bytes=b""):
    sel = "0x" + Web3.keccak(text=sig)[:4].hex()
    try:
        res = rpc_call("eth_call", [{"to": to, "data": sel + arg_bytes.hex()}, "latest"])
        return bytes.fromhex(res[2:])
    except:
        return None

# Load tokens from tramsList.json
with open("tramsList.json", "r") as f:
    trams_data = json.load(f)
    tokens = trams_data["tokens"]

# Define PIDs
pid_lps = {
    "0xbbb26dd2110f5fc0e69ffd3fa3d5f840147a706d": 0,
    "0x7e28895e2234394f21e931565007793c7446c4eb": 1,
    "0xd3bf876c1497a2b1285bbf881f0f3bcdc4c5b4fc": 2,
    "0x96d80118fe08d6d63cdf4bdd91bd56934f0e9d24": 3,
    "0xff4a27201f6d9975d19fe4c539fc6c0048da06c4": 4,
    "0x22a665e4abe0930d4d7f9241b101fc2f7d776b40": 5,
    "0xbe88e94e3e3f97f5d173f55aefc656d874e0c2a9": 6,
    "0x6d437d658bfa33342d48f2c234e7ed9e8154f3f8": 7,
    "0xc225eb41f7cb8fd9e826b8558eadc14995970ba0": 8,
    "0xfc3e97dd4c4bc06329fded000a7605c372250f6d": 9,
    "0x3b7ab9c3af6950137eb17a5af4101e7cbe31782d": 10,
    "0x5be84cc0b59b50ede98265008ab8665c4b70bbc5": 11,
    "0x30f5c59099c90bd90f764eacfbee807d29955c82": 12,
    "0xc17f51a8213c1017e502abd61bb31be228a9f383": 13,
    "0xf82e6314e66a79fe8af89818ea2dfed7ea309b43": 14
}

weth_addr = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

# Pair WETH with all 400+ tokens in tramsList.json
# Using ThreadPoolExecutor to make it extremely fast!
import concurrent.futures

def check_token(t):
    t_addr = t["address"]
    if t_addr.lower() == weth_addr.lower():
        return None
    
    # getPair(WETH, Token)
    arg = eth_abi.encode(['address', 'address'], [weth_addr, t_addr])
    res = eth_call(uniswap_factory, "getPair(address,address)", arg)
    if not res:
        return None
        
    pair_addr = eth_abi.decode(['address'], res)[0]
    if pair_addr == "0x0000000000000000000000000000000000000000":
        return None
        
    # Query migrator
    arg_mig = eth_abi.encode(['address'], [pair_addr])
    res_mig = eth_call(migrator_addr, "newTokens(address)", arg_mig)
    if not res_mig:
        return None
        
    new_token_addr = eth_abi.decode(['address'], res_mig)[0]
    if new_token_addr.lower() in pid_lps:
        pid = pid_lps[new_token_addr.lower()]
        return pid, t["symbol"], t_addr, pair_addr, new_token_addr

print("Scanning tokens pairing with WETH...")
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    results = executor.map(check_token, tokens)
    for r in results:
        if r:
            pid, sym, t_addr, pair_addr, new_token_addr = r
            print(f"🎯 MATCH FOUND: PID {pid} is WETH-{sym} LP ({pair_addr}) -> mTRAMS ({new_token_addr})")
