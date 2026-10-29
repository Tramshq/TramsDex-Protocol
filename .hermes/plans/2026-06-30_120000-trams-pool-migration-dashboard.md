# Trams Pool Migration Dashboard Implementation Plan

> **For Hermes:** Use the subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a gorgeous, self-contained, interactive single-page dashboard (`dashboard.html`) to visualize all 15 on-chain Trams pools and track their liquidity migration status.

**Architecture:** A static, single-file HTML5 interface built with **Tailwind CSS** (for beautiful dark-themed styling) and **Ethers.js** (for live on-chain queries via public RPC). The page will pre-cache the on-chain results we fetched for instant load, and allow users to toggle "Live Mode" to query live mainnet data.

**Tech Stack:** HTML5, Tailwind CSS (via CDN), FontAwesome icons (via CDN), Ethers.js v5 (via CDN), Python `http.server` (for local hosting).

---

### Task 1: Create Dashboard HTML Skeleton & CDNs

**Objective:** Set up the basic file structure with dark theme configurations, required CDNs, and core container layout.

**Files:**
- Create: `dashboard.html`

**Step 1: Create the skeleton file**
Write the following template into `dashboard.html`:

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TramsDex Pool Migration Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        trams: {
                            50: '#fff1f2',
                            100: '#ffe4e6',
                            500: '#f43f5e',
                            600: '#e11d48',
                            700: '#be123c',
                            900: '#881337',
                            950: '#4c0519',
                        }
                    }
                }
            }
        }
    </script>
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Ethers.js -->
    <script src="https://cdn.ethers.io/lib/ethers-5.7.2.umd.min.js" type="application/javascript"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen font-sans antialiased selection:bg-trams-500 selection:text-white">
    <div id="app" class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <!-- Content will go here -->
    </div>
</body>
</html>
```

**Step 2: Verify Skeleton loads**
Run: `python3 -m http.server 8000 --bind 127.0.0.1` and open `http://localhost:8000/dashboard.html` in browser to confirm the dark background and styling are active.

**Step 3: Commit**
```bash
git add dashboard.html
git commit -m "feat: setup dashboard skeleton with Tailwind and Ethers.js CDNs"
```

---

### Task 2: Embed Pre-cached Pool Data

**Objective:** Embed the retrieved on-chain pool configurations as a local fallback database for instant load and offline usability.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write static script in `dashboard.html`**
Directly under the script block, define the exact list of 15 pools queried from the mainnet:

```html
<script>
    const TRAMS_MASTER_ADDRESS = "0xb099f783452810eb6436bc6d8e3b5ea5db9f76c0";
    const TRAMS_TOKEN_ADDRESS = "0x7afa2bbc06dad88487b5171ea2bcdf938a6b7ff9";
    const PUBLIC_RPC_URL = "https://ethereum-rpc.publicnode.com";

    // Pre-fetched fallback dataset for instant rendering
    const PRE_CACHED_POOLS = [
        { pid: 0, lpToken: "0xbbb26dd2110f5fc0e69ffd3fa3d5f840147a706d", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 30000, lastRewardBlock: 12059703, accTramsPerShare: "706696251211733" },
        { pid: 1, lpToken: "0x7e28895e2234394f21e931565007793c7446c4eb", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 0, lastRewardBlock: 11384627, accTramsPerShare: "38576960723680165313" },
        { pid: 2, lpToken: "0xd3bf876c1497a2b1285bbf881f0f3bcdc4c5b4fc", name: "Trams LP Token", symbol: "TLP (DAI-TRAMS)", isMigrated: false, sourcePair: "Direct Pool Deposit", targetPair: "TramsDex LP Pair", allocPoint: 0, lastRewardBlock: 11384627, accTramsPerShare: "56542234464585" },
        { pid: 3, lpToken: "0x96d80118fe08d6d63cdf4bdd91bd56934f0e9d24", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 0, lastRewardBlock: 11384627, accTramsPerShare: "175333242456299" },
        { pid: 4, lpToken: "0xff4a27201f6d9975d19fe4c539fc6c0048da06c4", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 0, lastRewardBlock: 11384627, accTramsPerShare: "639675696355429887576" },
        { pid: 5, lpToken: "0x22a665e4abe0930d4d7f9241b101fc2f7d776b40", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 0, lastRewardBlock: 11384627, accTramsPerShare: "26487637051700" },
        { pid: 6, lpToken: "0xbe88e94e3e3f97f5d173f55aefc656d874e0c2a9", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 200, lastRewardBlock: 11871722, accTramsPerShare: "6381656513601808257674" },
        { pid: 7, lpToken: "0x6d437d658bfa33342d48f2c234e7ed9e8154f3f8", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 220, lastRewardBlock: 11885839, accTramsPerShare: "5213488683817766" },
        { pid: 8, lpToken: "0xc225eb41f7cb8fd9e826b8558eadc14995970ba0", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 100, lastRewardBlock: 11871768, accTramsPerShare: "76164851001724527" },
        { pid: 9, lpToken: "0xfc3e97dd4c4bc06329fded000a7605c372250f6d", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 200, lastRewardBlock: 11871792, accTramsPerShare: "14065364417185604" },
        { pid: 10, lpToken: "0x3b7ab9c3af6950137eb17a5af4101e7cbe31782d", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 100, lastRewardBlock: 11871809, accTramsPerShare: "22640805735282552" },
        { pid: 11, lpToken: "0x5be84cc0b59b50ede98265008ab8665c4b70bbc5", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 100, lastRewardBlock: 11886110, accTramsPerShare: "2959894392429202" },
        { pid: 12, lpToken: "0x30f5c59099c90bd90f764eacfbee807d29955c82", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 200, lastRewardBlock: 11871840, accTramsPerShare: "2666773904658684403797398" },
        { pid: 13, lpToken: "0xc17f51a8213c1017e502abd61bb31be228a9f383", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 80, lastRewardBlock: 11891494, accTramsPerShare: "29406037757957508" },
        { pid: 14, lpToken: "0xf82e6314e66a79fe8af89818ea2dfed7ea309b43", name: "MigratedToken", symbol: "mTRAMS", isMigrated: true, sourcePair: "Uniswap V2 LP", targetPair: "TramsDex mTRAMS Pool", allocPoint: 100, lastRewardBlock: 11871855, accTramsPerShare: "42690594097848799609281343038" }
    ];

    let currentPools = JSON.parse(JSON.stringify(PRE_CACHED_POOLS));
    let isLiveMode = false;
</script>
```

**Step 2: Commit**
```bash
git add dashboard.html
git commit -m "feat: embed pre-cached pool dataset in dashboard scripts"
```

---

### Task 3: Build Header, Protocol Stats Cards & Visual Theme

**Objective:** Implement the UI Header containing TramsDex branding, active system metadata, and beautiful, glowing metric cards.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write HTML template for stats & header inside the `#app` container**
```html
<!-- Header -->
<header class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-800 pb-6 mb-8 gap-4">
    <div>
        <div class="flex items-center gap-3">
            <div class="bg-gradient-to-tr from-trams-600 to-rose-400 p-2.5 rounded-xl shadow-lg shadow-trams-900/30">
                <i class="fa-solid fa-layer-group text-2xl text-white"></i>
            </div>
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-white bg-clip-text bg-gradient-to-r from-white to-gray-300">
                    TramsDex Protocol <span class="text-trams-500 text-2xl">M</span>
                </h1>
                <p class="text-sm text-gray-400">Yield Farm Pool Explorer & Migration Tracker</p>
            </div>
        </div>
    </div>
    <div class="flex items-center gap-3 bg-gray-900 border border-gray-800 px-4 py-2.5 rounded-xl">
        <span class="relative flex h-3 w-3">
            <span id="status-ping" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span id="status-dot" class="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
        </span>
        <span id="network-text" class="text-sm font-semibold text-gray-300">Offline / Static Cache</span>
        <button id="toggle-live-btn" onclick="toggleLiveMode()" class="ml-2 px-3 py-1 bg-trams-600 hover:bg-trams-500 active:scale-95 transition text-xs font-bold rounded-lg text-white">
            Go Live
        </button>
    </div>
</header>

<!-- Metrics Overview Grid -->
<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div class="bg-gray-900 border border-gray-800 p-5 rounded-2xl relative overflow-hidden group hover:border-gray-700 transition">
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Pools</div>
        <div class="text-4xl font-extrabold text-white mt-1">15</div>
        <div class="absolute right-4 bottom-4 text-gray-800 group-hover:text-trams-900/30 transition text-5xl"><i class="fa-solid fa-cubes"></i></div>
    </div>
    <div class="bg-gray-900 border border-gray-800 p-5 rounded-2xl relative overflow-hidden group hover:border-gray-700 transition">
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Alloc Points</div>
        <div class="text-4xl font-extrabold text-trams-500 mt-1">31,300</div>
        <div class="absolute right-4 bottom-4 text-gray-800 group-hover:text-trams-900/30 transition text-5xl"><i class="fa-solid fa-chart-line"></i></div>
    </div>
    <div class="bg-gray-900 border border-gray-800 p-5 rounded-2xl relative overflow-hidden group hover:border-gray-700 transition">
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Migrated Pools</div>
        <div class="text-4xl font-extrabold text-emerald-400 mt-1">14 <span class="text-xs font-normal text-gray-400">/ 15</span></div>
        <div class="absolute right-4 bottom-4 text-gray-800 group-hover:text-trams-900/30 transition text-5xl"><i class="fa-solid fa-truck-ramp-box"></i></div>
    </div>
    <div class="bg-gray-900 border border-gray-800 p-5 rounded-2xl relative overflow-hidden group hover:border-gray-700 transition">
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Reward Pools</div>
        <div class="text-4xl font-extrabold text-blue-400 mt-1">10 <span class="text-xs font-normal text-gray-400">/ 15</span></div>
        <div class="absolute right-4 bottom-4 text-gray-800 group-hover:text-trams-900/30 transition text-5xl"><i class="fa-solid fa-circle-dollar-to-slot"></i></div>
    </div>
</div>
```

**Step 2: Commit**
```bash
git add dashboard.html
git commit -m "feat: design dashboard metrics and header UI components"
```

---

### Task 4: Implement Interactive Filtering & Search Bar

**Objective:** Build clean client-side filters (All, Active, Migrated, Inactive) and text searching, updating the visible card grid in real-time.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write Filter & Search Controls HTML**
Insert the control bar HTML block into `dashboard.html` directly below the metrics grid:

```html
<div class="flex flex-col md:flex-row gap-4 justify-between items-center bg-gray-900/50 border border-gray-800/80 p-4 rounded-2xl mb-8">
    <div class="relative w-full md:w-96">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
            <i class="fa-solid fa-magnifying-glass"></i>
        </span>
        <input type="text" id="search-input" onkeyup="renderPools()" placeholder="Search by PID, address, name, or symbol..." class="w-full bg-gray-950 border border-gray-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-trams-500/50 focus:border-trams-500 transition">
    </div>
    <div class="flex flex-wrap gap-2 w-full md:w-auto">
        <button onclick="setFilter('all')" id="filter-all" class="px-4 py-2 bg-trams-600 text-white text-xs font-bold rounded-xl transition">All Pools</button>
        <button onclick="setFilter('active')" id="filter-active" class="px-4 py-2 bg-gray-950 hover:bg-gray-800 border border-gray-800 text-gray-400 text-xs font-bold rounded-xl transition">Active Rewards</button>
        <button onclick="setFilter('migrated')" id="filter-migrated" class="px-4 py-2 bg-gray-950 hover:bg-gray-800 border border-gray-800 text-gray-400 text-xs font-bold rounded-xl transition">Migrated</button>
        <button onclick="setFilter('inactive')" id="filter-inactive" class="px-4 py-2 bg-gray-950 hover:bg-gray-800 border border-gray-800 text-gray-400 text-xs font-bold rounded-xl transition">Zero Reward</button>
    </div>
</div>

<!-- Main Pool Grid container -->
<div id="pools-grid" class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Rendered Pool Cards will land here -->
</div>
```

**Step 2: Add dynamic Javascript filter definitions**
Define filter properties and render rules in the script block:
```javascript
let activeFilter = 'all';

function setFilter(filter) {
    activeFilter = filter;
    ['all', 'active', 'migrated', 'inactive'].forEach(f => {
        const btn = document.getElementById(`filter-${f}`);
        if (f === filter) {
            btn.className = "px-4 py-2 bg-trams-600 text-white text-xs font-bold rounded-xl transition";
        } else {
            btn.className = "px-4 py-2 bg-gray-950 hover:bg-gray-800 border border-gray-800 text-gray-400 text-xs font-bold rounded-xl transition";
        }
    });
    renderPools();
}
```

**Step 3: Commit**
```bash
git add dashboard.html
git commit -m "feat: implement real-time search & pool filtering UI and scripts"
```

---

### Task 5: Build Interactive Pool Cards and Render Script

**Objective:** Write the Javascript render function to generate beautiful interactive pool cards. Highlight migration state and reward allocations.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write dynamic HTML generation inside script block**
```javascript
function renderPools() {
    const query = document.getElementById('search-input').value.toLowerCase().trim();
    const grid = document.getElementById('pools-grid');
    grid.innerHTML = '';

    const totalAlloc = currentPools.reduce((acc, p) => acc + p.allocPoint, 0);

    const filtered = currentPools.filter(pool => {
        // Apply Filter
        if (activeFilter === 'active' && pool.allocPoint === 0) return false;
        if (activeFilter === 'inactive' && pool.allocPoint > 0) return false;
        if (activeFilter === 'migrated' && !pool.isMigrated) return false;

        // Apply Search Query
        if (query) {
            const matchesPid = pool.pid.toString() === query;
            const matchesSymbol = pool.symbol.toLowerCase().includes(query);
            const matchesName = pool.name.toLowerCase().includes(query);
            const matchesAddr = pool.lpToken.toLowerCase().includes(query);
            return matchesPid || matchesSymbol || matchesName || matchesAddr;
        }
        return true;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center text-gray-500 bg-gray-900/20 border border-gray-900 border-dashed rounded-2xl">
                <i class="fa-regular fa-folder-open text-4xl mb-3"></i>
                <p>No matching pools found</p>
            </div>
        `;
        return;
    }

    filtered.forEach(pool => {
        const pct = totalAlloc > 0 ? (pool.allocPoint / totalAlloc * 100).toFixed(2) : '0.00';
        const cardClass = pool.allocPoint > 0 ? 'border-trams-900/40 hover:border-trams-500/50' : 'border-gray-900 hover:border-gray-800';
        
        const cardHtml = `
            <div onclick="openModal(${pool.pid})" class="bg-gray-900/40 backdrop-blur border ${cardClass} rounded-2xl p-6 transition duration-300 cursor-pointer hover:-translate-y-1 hover:shadow-lg hover:shadow-black/40 flex flex-col justify-between h-72">
                <div>
                    <!-- Badge & PID -->
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-xs font-semibold text-gray-400 bg-gray-950 px-3 py-1 rounded-full border border-gray-800">PID ${pool.pid}</span>
                        ${pool.allocPoint > 0 ? 
                            `<span class="text-[10px] font-bold text-trams-500 bg-trams-950/40 border border-trams-900 px-2 py-0.5 rounded-full uppercase tracking-wider animate-pulse">Earning</span>` :
                            `<span class="text-[10px] font-bold text-gray-500 bg-gray-950 border border-gray-900 px-2 py-0.5 rounded-full uppercase tracking-wider">Inactive</span>`
                        }
                    </div>

                    <!-- Title -->
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-ticket ${pool.allocPoint > 0 ? 'text-trams-500' : 'text-gray-500'}"></i>
                        ${pool.symbol}
                    </h3>
                    <p class="text-xs text-gray-400 mt-1">${pool.name}</p>

                    <!-- Stats -->
                    <div class="grid grid-cols-2 gap-4 mt-6">
                        <div>
                            <span class="text-[10px] uppercase font-bold text-gray-500 block">Alloc Points</span>
                            <span class="text-md font-bold text-gray-200">${pool.allocPoint.toLocaleString()} (${pct}%)</span>
                        </div>
                        <div>
                            <span class="text-[10px] uppercase font-bold text-gray-500 block">Reward Block</span>
                            <span class="text-md font-bold text-gray-200">${pool.lastRewardBlock.toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                <!-- Footer Status (Migration Track) -->
                <div class="border-t border-gray-800/80 pt-4 mt-6 flex justify-between items-center">
                    <span class="text-xs text-gray-400 flex items-center gap-1.5">
                        <i class="fa-solid fa-circle-info text-gray-500"></i>
                        ${pool.isMigrated ? 'Migrated successfully' : 'Native pair'}
                    </span>
                    <i class="fa-solid fa-arrow-right text-gray-500 text-xs"></i>
                </div>
            </div>
        `;
        grid.innerHTML += cardHtml;
    });
}

// Initial render
window.addEventListener('DOMContentLoaded', () => {
    renderPools();
});
```

**Step 2: Commit**
```bash
git add dashboard.html
git commit -m "feat: build active JS rendering grid and card markup generators"
```

---

### Task 6: Implement Migration Detail Flow Modal

**Objective:** Design a modal showcasing an interactive visual flowchart tracing how legacy Uniswap LP assets migrate into native Trams pools.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write Modal HTML**
Insert the Modal template at the bottom of the body:

```html
<!-- Detail Modal -->
<div id="pool-modal" class="hidden fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm transition-all duration-300">
    <div class="bg-gray-900 border border-gray-800 rounded-3xl max-w-lg w-full overflow-hidden shadow-2xl relative transform transition-all scale-95 duration-300">
        <!-- Close button -->
        <button onclick="closeModal()" class="absolute right-5 top-5 text-gray-400 hover:text-white transition">
            <i class="fa-solid fa-xmark text-xl"></i>
        </button>

        <!-- Modal Body Content -->
        <div class="p-8">
            <span class="text-xs font-bold text-trams-500 uppercase tracking-wider block mb-1" id="modal-subtitle">Pool Profile</span>
            <h2 class="text-3xl font-extrabold text-white flex items-center gap-2 mb-6" id="modal-title">
                mTRAMS
            </h2>

            <!-- Flowchart / Diagram of Migration -->
            <div class="bg-gray-950 border border-gray-850 p-5 rounded-2xl mb-6">
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-4 text-center">Migration Visual Path</span>
                <div class="flex flex-col items-center gap-3">
                    <div class="w-full bg-gray-900 border border-gray-800 p-3 rounded-xl text-center">
                        <span class="text-[9px] uppercase font-bold text-trams-500">Source Pool</span>
                        <div class="font-bold text-sm text-gray-300 mt-0.5" id="modal-src">Uniswap V2 LP Pool</div>
                    </div>
                    <div class="text-trams-500 animate-bounce py-1">
                        <i class="fa-solid fa-circle-arrow-down text-xl"></i>
                    </div>
                    <div class="w-full bg-trams-950/20 border border-trams-900/60 p-3 rounded-xl text-center">
                        <span class="text-[9px] uppercase font-bold text-emerald-400">Target Pool</span>
                        <div class="font-bold text-sm text-white mt-0.5" id="modal-dst">TramsDex Native mTRAMS</div>
                    </div>
                </div>
            </div>

            <!-- Parameters -->
            <div class="space-y-4">
                <div class="flex justify-between items-center border-b border-gray-800/80 pb-2.5">
                    <span class="text-xs text-gray-400">LP Token Address</span>
                    <span class="text-xs font-mono text-gray-300 bg-gray-950 px-2.5 py-1 rounded border border-gray-850 cursor-pointer hover:bg-gray-900 transition flex items-center gap-1" id="modal-lp-addr" onclick="copyAddress()">
                        0x... <i class="fa-regular fa-copy text-[10px]"></i>
                    </span>
                </div>
                <div class="flex justify-between items-center border-b border-gray-800/80 pb-2.5">
                    <span class="text-xs text-gray-400">Governance Weight</span>
                    <span class="text-xs font-bold text-gray-200" id="modal-alloc">30,000 AP</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-400">On-Chain explorer</span>
                    <a href="#" target="_blank" id="modal-etherscan-link" class="text-xs font-bold text-trams-500 hover:underline flex items-center gap-1">
                        View on Etherscan <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Step 2: Add dynamic Open/Close Modal Javascript triggers**
```javascript
function openModal(pid) {
    const pool = currentPools.find(p => p.pid === pid);
    if (!pool) return;

    document.getElementById('modal-title').innerHTML = `<i class="fa-solid fa-ticket text-trams-500"></i> ${pool.symbol}`;
    document.getElementById('modal-subtitle').innerText = `Pool PID ${pool.pid} Details`;
    
    // Migration Path
    document.getElementById('modal-src').innerText = pool.sourcePair;
    document.getElementById('modal-dst').innerText = pool.targetPair;
    
    // Address & Link
    const shortAddr = pool.lpToken.slice(0, 6) + '...' + pool.lpToken.slice(-4);
    document.getElementById('modal-lp-addr').innerHTML = `${shortAddr} <i class="fa-regular fa-copy text-[10px]"></i>`;
    document.getElementById('modal-lp-addr').dataset.address = pool.lpToken;
    document.getElementById('modal-etherscan-link').href = `https://etherscan.io/address/${pool.lpToken}`;
    
    // Allocation
    document.getElementById('modal-alloc').innerText = `${pool.allocPoint.toLocaleString()} AP`;

    const modal = document.getElementById('pool-modal');
    modal.classList.remove('hidden');
    modal.querySelector('.transform').classList.remove('scale-95');
    modal.querySelector('.transform').classList.add('scale-100');
}

function closeModal() {
    const modal = document.getElementById('pool-modal');
    modal.querySelector('.transform').classList.remove('scale-100');
    modal.querySelector('.transform').classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 150);
}

function copyAddress() {
    const addr = document.getElementById('modal-lp-addr').dataset.address;
    navigator.clipboard.writeText(addr);
    alert('LP Token Address copied to clipboard!');
}
```

**Step 3: Commit**
```bash
git add dashboard.html
git commit -m "feat: implement interactive modal and flow path tracker"
```

---

### Task 7: Implement Real-Time Syncing via public RPC

**Objective:** Integrate standard Web3 RPC polling inside `dashboard.html` using the Ethers.js CDN provider to update pool properties live when "Go Live" is active.

**Files:**
- Modify: `dashboard.html`

**Step 1: Write Live Mode syncing code**
```javascript
const TRAMS_MASTER_ABI = [
    "function poolLength() view returns (uint256)",
    "function poolInfo(uint256) view returns (address, uint256, uint256, uint256)",
    "function totalAllocPoint() view returns (uint256)"
];

async function toggleLiveMode() {
    if (isLiveMode) {
        // Switch back to offline cache
        isLiveMode = false;
        currentPools = JSON.parse(JSON.stringify(PRE_CACHED_POOLS));
        updateStatusIndicator(false);
        renderPools();
        return;
    }

    try {
        updateStatusText("Connecting...", "amber");
        const provider = new ethers.providers.JsonRpcProvider(PUBLIC_RPC_URL);
        const contract = new ethers.Contract(TRAMS_MASTER_ADDRESS, TRAMS_MASTER_ABI, provider);

        const length = await contract.poolLength();
        const totalAlloc = await contract.totalAllocPoint();
        const numPools = length.toNumber();

        updateStatusText("Syncing Pools...", "amber");
        
        const poolPromises = [];
        for (let i = 0; i < numPools; i++) {
            poolPromises.push(contract.poolInfo(i));
        }
        
        const infos = await Promise.all(poolPromises);
        
        // Map back to currentPools
        for (let i = 0; i < numPools; i++) {
            const info = infos[i];
            const lpToken = info[0].toLowerCase();
            const allocPoint = info[1].toNumber();
            const lastRewardBlock = info[2].toNumber();
            const accTramsPerShare = info[3].toString();

            // Find match or insert new
            const cachedMatch = currentPools.find(p => p.pid === i);
            if (cachedMatch) {
                cachedMatch.allocPoint = allocPoint;
                cachedMatch.lastRewardBlock = lastRewardBlock;
                cachedMatch.accTramsPerShare = accTramsPerShare;
            } else {
                currentPools.push({
                    pid: i,
                    lpToken: lpToken,
                    name: "Unknown",
                    symbol: "mTRAMS",
                    isMigrated: true,
                    sourcePair: "Uniswap V2 LP",
                    targetPair: "TramsDex Pool",
                    allocPoint: allocPoint,
                    lastRewardBlock: lastRewardBlock,
                    accTramsPerShare: accTramsPerShare
                });
            }
        }

        isLiveMode = true;
        updateStatusIndicator(true, `Live (Mainnet Block)`);
        renderPools();
    } catch (err) {
        console.error(err);
        alert(`Failed to sync with Mainnet RPC: ${err.message}`);
        updateStatusIndicator(false);
    }
}

function updateStatusText(text, color) {
    document.getElementById('network-text').innerText = text;
}

function updateStatusIndicator(live, customText = "") {
    const ping = document.getElementById('status-ping');
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('network-text');
    const btn = document.getElementById('toggle-live-btn');

    if (live) {
        ping.className = "animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75";
        dot.className = "relative inline-flex rounded-full h-3 w-3 bg-emerald-500";
        text.innerText = customText || "Live Mainnet";
        btn.innerText = "Disconnect";
        btn.className = "ml-2 px-3 py-1 bg-gray-800 hover:bg-gray-700 active:scale-95 transition text-xs font-bold rounded-lg text-white";
    } else {
        ping.className = "animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75";
        dot.className = "relative inline-flex rounded-full h-3 w-3 bg-amber-500";
        text.innerText = "Offline / Static Cache";
        btn.innerText = "Go Live";
        btn.className = "ml-2 px-3 py-1 bg-trams-600 hover:bg-trams-500 active:scale-95 transition text-xs font-bold rounded-lg text-white";
    }
}
```

**Step 2: Verify and Test**
Load the page, click "Go Live", and verify the dashboard successfully resolves the live on-chain values and turns Green.

**Step 3: Commit**
```bash
git add dashboard.html
git commit -m "feat: complete real-time mainnet sync via Ethers.js public RPC"
```

---

## Verification & Testing Guide

Once the files are saved, run Python's built-in HTTP server to run the frontend locally:

```bash
# Start server
python3 -m http.server 8000 --bind 127.0.0.1
```

1. Open your browser and navigate to `http://localhost:8000/dashboard.html`.
2. Confirm the 15 pools render instantly under "Offline / Static Cache" mode.
3. Test searching "mTRAMS", "DAI", and "0" — verifying instant filtering.
4. Click on **PID 0** and verify the Modal opens showing the visual migration flowchart mapping the flow.
5. Click the **Go Live** button, watch it load, and confirm it blinks green with on-chain connection success.
