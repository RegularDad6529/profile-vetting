#!/usr/bin/env python3
"""
Artist Vetting Scanner — Seeking Nomination Wave

Daily scanner that:
1. Fetches all unique authors from the Seeking Nomination wave
2. Checks on-chain tx count (Ankr RPC), 6529 profile data, social links, artwork
3. Fetches MemesNominee rep balance — skips anyone already at 50K+
4. Detects rep-givers (people posting to give rep, not seek it) — skips them
5. Requires asking for rep OR posting artwork in the wave — skips pure GMeme posts
6. Classifies as ESTABLISHED / LIKELY_REAL / UNCLEAR / SUSPICIOUS / NEW_EMPTY
7. Gives 10,000 MemesNominee rep (via proxy) to qualified LIKELY_REAL+ who are under 50K
8. Posts notification reply when rep is given
9. Posts threaded replies to UNCLEAR/SUSPICIOUS asking them to add socials + post artwork

Dedup: maintains a state file of wallets that already received rep.
"""

import json, urllib.request, time, re, os, sys, io, base64, hashlib
from collections import defaultdict
from PIL import Image

# Add scripts dir for audit_log
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_log import audited_post_drop, log_6529_action

# ============ CONFIG ============
SEEKING_NOMINATION_WAVE = "0ecb95d0-d8f2-48e8-8137-bfa71ee8593c"
TOKEN_FILE = "/home/prenode/.hermes/profiles/themanager/6529_tokens.json"
WALLET_KEY_FILE = "/home/prenode/.hermes/profiles/themanager/wallet_key.secure"
STATE_FILE = "/home/prenode/.hermes/profiles/themanager/seen/seeking_nomination_vetted.json"
RPC_URL = "https://rpc.ankr.com/eth"
WALLET_ADDRESS = "0xf409b9678bf48a9196fb85b9a7541e442ce3d8d4"  # TheManager's wallet
RD_PROFILE_ID = "0f8321c5-87b4-11ee-9d82-029a0e4b6159"  # RegularDad's profile ID
REP_AMOUNT = 10000
REP_CATEGORY = "MemesNominee"  # no underscores allowed
MEMES_NOMINEE_THRESHOLD = 50000

# Ignore list (from memory)
IGNORE_HANDLES = {"gray", "karen_intern", "anon_wave_bot", "regulardad", "themanager"}

API_BASE = "https://api.6529.io/api"

# ============ HELPERS ============

def load_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)["token"]

def api_get(path, token=None):
    url = f"{API_BASE}{path}"
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read())
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise

def get_proxy_token():
    """Generate a proxy token for bulk-rep calls using RD's profile ID."""
    nonce_url = f"{API_BASE}/auth/nonce?signer_address={WALLET_ADDRESS}&short_nonce=true"
    req = urllib.request.Request(nonce_url, headers={"Accept": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)
    nonce_data = json.loads(resp.read())

    from eth_account import Account
    from eth_account.messages import encode_defunct

    with open(WALLET_KEY_FILE) as f:
        private_key = f.read().strip().replace("0x", "")

    account = Account.from_key(private_key)
    signed = account.sign_message(encode_defunct(text=nonce_data["nonce"]))
    client_sig = "0x" + signed.signature.hex()

    login_body = json.dumps({
        "server_signature": nonce_data["server_signature"],
        "client_signature": client_sig,
        "role": RD_PROFILE_ID,
    }).encode()
    login_req = urllib.request.Request(
        f"{API_BASE}/auth/login",
        data=login_body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    login_resp = urllib.request.urlopen(login_req, timeout=15)
    login_data = json.loads(login_resp.read())
    return login_data["token"]

def assign_rep(proxy_token, address, amount, category):
    """Call bulk-rep for a single target."""
    body = json.dumps({"targets": [{"address": address, "category": category, "amount": amount}]}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/bulk-rep",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "Authorization": f"Bearer {proxy_token}"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return True, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return False, f"HTTP {e.code}: {error_body[:300]}"
    except Exception as e:
        return False, str(e)

def get_tx_count(wallet):
    """Get on-chain tx count via Ankr RPC."""
    if not wallet:
        return -1
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [wallet, "latest"],
            "id": 1
        }).encode()
        req = urllib.request.Request(RPC_URL, data=payload,
                                     headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        return int(data.get("result", "0x0"), 16)
    except:
        return -1

# Known exchange hot wallet addresses (lowercase)
# These are widely documented and stable. Sales FROM these addresses are dubious
# because the artist could be withdrawing from their own exchange account.
EXCHANGE_ADDRESSES = {
    "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance 14
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549",   # Binance 15
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",   # Gemini
    "0x564286362092d8e7936969369532c424a2e4eb34",   # Binance 8
    # Add more as discovered via vetting runs
}

STABLECOIN_ADDRS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT (Tether)
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
}

def is_exchange_address(addr):
    """Check if an address is a known exchange hot wallet."""
    if not addr:
        return False
    return addr.lower() in EXCHANGE_ADDRESSES

# Known NFT marketplace escrow/proxy contracts
MARKETPLACE_CONTRACTS = {
    "0xcda72070e455bb31c7690a170224ce43623d0b6f",  # Foundation NFTMarket proxy
    "0x495f947276749ce646f68ac8c248420045cb7b5e",  # OpenSea Shared Storefront
    "0x00000000000000adc04c56bf30ac9d3c0aaf14dc",  # Seaport
    "0x7f268357a8d255c205fccc681f46c5b39c3a31c5",  # OpenSea Old Exchange
    "0x59728544b08cbc078c3d6f56a77cad5f80b8b7a3",  # OpenSea Seaport 1.5
    "0xff7ca10af37abc39e1e6f291f88e5f3a0673e249",  # Foundation treasury
}

def is_marketplace_contract(addr):
    """Check if an address is a known NFT marketplace escrow/proxy contract.
    Also checks Blockscout to see if it's a smart contract (not an EOA)."""
    if not addr:
        return False, ""
    if addr.lower() in MARKETPLACE_CONTRACTS:
        return True, "Known marketplace contract"
    try:
        BLOCKSCOUT = "https://eth.blockscout.com/api/v2"
        url = f"{BLOCKSCOUT}/addresses/{addr}"
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("is_contract", False):
            name = data.get("name", "") or ""
            impl = data.get("implementations", [])
            impl_name = impl[0].get("name", "") if impl else ""
            label = name or impl_name or "smart contract"
            return True, label
        return False, ""
    except:
        return False, ""

def is_single_collection_wallet(addr):
    """Check if a wallet only interacts with one NFT collection.
    Real collectors typically interact with multiple collections.
    Returns (is_single, collection_name) tuple."""
    if not addr:
        return False, ""
    try:
        BLOCKSCOUT = "https://eth.blockscout.com/api/v2"
        url = f"{BLOCKSCOUT}/addresses/{addr}/token-transfers"
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        items = data.get("items", [])
        
        import unicodedata
        collections = set()
        for item in items:
            token = item.get("token", {})
            if "ERC-721" in token.get("type", "") or "ERC-1155" in token.get("type", ""):
                name = unicodedata.normalize("NFKC", token.get("name", "") or "")
                if name:
                    collections.add(name)
        
        if len(items) >= 10 and len(collections) == 1:
            return True, list(collections)[0]
        return False, ""
    except:
        return False, ""

def is_likely_exchange_wallet(addr):
    """Heuristic: check if a wallet looks like an exchange/OTC desk based on tx volume.
    Exchange hot wallets typically have high tx count and large USDT/stablecoin volume.
    Only call this for buyer wallets not in the known list."""
    if not addr or is_exchange_address(addr):
        return is_exchange_address(addr)
    try:
        BLOCKSCOUT = "https://eth.blockscout.com/api/v2"
        url = f"{BLOCKSCOUT}/addresses/{addr}/token-transfers"
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        items = data.get("items", [])
        if len(items) >= 30:
            # Count stablecoin transfers — exchanges move huge volumes
            # Token names from Blockscout can contain unicode characters
            # so we normalize by removing non-ASCII chars and checking for USDT/USDC/DAI
            import unicodedata
            stable_count = 0
            for i in items:
                token = i.get("token", {})
                # Try address first
                addr_lower = (token.get("address", "") or "").lower()
                if addr_lower in STABLECOIN_ADDRS:
                    stable_count += 1
                    continue
                # Fall back to normalized name/symbol
                name = token.get("name", "") or ""
                symbol = token.get("symbol", "") or ""
                # Strip non-ASCII (Blockscout uses special unicode chars in token names)
                name_norm = unicodedata.normalize("NFKC", name).encode("ascii", "ignore").decode()
                symbol_norm = unicodedata.normalize("NFKC", symbol).encode("ascii", "ignore").decode()
                if any(s in name_norm.upper() or s in symbol_norm.upper() for s in ["USDT", "TETHER", "USDC", "USD COIN", "DAI"]):
                    stable_count += 1
            if stable_count >= 15:
                return True
        return False
    except:
        return False

def get_nft_history(wallet, max_pages=10, chain="ethereum"):
    """Fetch NFT transfer + transaction history for a wallet via Blockscout API.
    Categorizes transfers to distinguish real sales from mints/burns/wash trading.
    
    Chain can be: "ethereum", "base", "polygon", "arbitrum", "optimism", "zora"
    
    Returns dict with:
      - raw counts: total_transfers, mints, burns, self_transfers, received_from_others, sent_to_others
      - quality signals: unique_collectors, unique_senders, sales_count, eth_received, has_marketplace_sales
      - contract signals: deployed_contracts, unique_nft_contracts, contracts (name→breakdown)
      - timing: first_transfer, last_transfer, wallet_age_days
      - chain: which chain this data is from
    Returns None on error."""
    if not wallet:
        return None
    CHAIN_URLS = {
        "ethereum": "https://eth.blockscout.com/api/v2",
        "base": "https://base.blockscout.com/api/v2",
        "polygon": "https://polygon.blockscout.com/api/v2",
        "arbitrum": "https://arbitrum.blockscout.com/api/v2",
        "optimism": "https://optimism.blockscout.com/api/v2",
        "zora": "https://explorer.zora.energy/api/v2",
    }
    BLOCKSCOUT = CHAIN_URLS.get(chain, CHAIN_URLS["ethereum"])
    wl = wallet.lower()
    ZERO_ADDR = "0x0000000000000000000000000000000000000000"
    
    # --- Fetch NFT token transfers ---
    all_items = []
    next_params = None
    for page in range(max_pages):
        if next_params:
            params = "&".join(f"{k}={v}" for k, v in next_params.items())
            url = f"{BLOCKSCOUT}/addresses/{wallet}/token-transfers?{params}"
        else:
            url = f"{BLOCKSCOUT}/addresses/{wallet}/token-transfers"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            all_items.extend(data.get("items", []))
            next_params = data.get("next_page_params")
            if not next_params:
                break
            time.sleep(0.3)
        except:
            break
    
    nft_items = [i for i in all_items
                 if "ERC-721" in i.get("token", {}).get("type", "")
                 or "ERC-1155" in i.get("token", {}).get("type", "")]
    
    # --- Fetch regular + internal transactions (for ETH value + marketplace methods) ---
    # Regular transactions
    all_txs = []
    next_params = None
    for page in range(max_pages):
        if next_params:
            params = "&".join(f"{k}={v}" for k, v in next_params.items())
            url = f"{BLOCKSCOUT}/addresses/{wallet}/transactions?{params}"
        else:
            url = f"{BLOCKSCOUT}/addresses/{wallet}/transactions"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            all_txs.extend(data.get("items", []))
            next_params = data.get("next_page_params")
            if not next_params:
                break
            time.sleep(0.3)
        except:
            break
    
    # Internal transactions (marketplace payouts, contract-to-wallet ETH transfers)
    # These are critical for detecting real sales — marketplaces like TL Auction House
    # pay artists via internal transactions, not regular transactions
    # Uses v1 API since v2 internal-txs endpoint returns 400
    BS_V1 = BLOCKSCOUT.replace("/api/v2", "/api")
    for page in range(1, max_pages + 1):
        try:
            url = f"{BS_V1}?module=account&action=txlistinternal&address={wallet}&page={page}&offset=100&sort=desc"
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            internal_items = data.get("result", [])
            if not internal_items:
                break
            # Transform v1 internal txs to match v2 format
            for itx in internal_items:
                from_addr_raw = itx.get("from", "")
                to_addr_raw = itx.get("to", "")
                # v1 uses unix timestamps, convert to ISO
                ts = itx.get("timeStamp", "")
                if ts and ts.isdigit():
                    from datetime import datetime
                    ts = datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
                transformed = {
                    "from": {"hash": from_addr_raw},
                    "to": {"hash": to_addr_raw},
                    "value": itx.get("value", "0"),
                    "method": "",
                    "timestamp": ts,
                    "_internal": True,
                }
                all_txs.append(transformed)
            if len(internal_items) < 100:
                break
            time.sleep(0.3)
        except:
            break
    
    # --- Categorize NFT transfers ---
    mints = 0
    burns = 0
    self_transfers = 0
    received_from_others = 0
    sent_to_others = 0
    unique_collectors = set()  # wallets that received NFTs from this artist
    unique_senders = set()     # wallets that sent NFTs to this artist
    contracts = {}
    wallet_tokens = defaultdict(lambda: {"sent": set(), "received": set()})  # wallet -> token IDs sent/received
    
    for t in nft_items:
        token = t.get("token", {})
        addr = token.get("address", "").lower()
        name = token.get("name", "Unknown")
        from_addr = (t.get("from") or {}).get("hash", "").lower()
        to_addr = (t.get("to") or {}).get("hash", "").lower()
        total = t.get("total") or {}
        token_id = str(total.get("token_id", ""))
        token_type = token.get("type", "")  # ERC-721 (unique) vs ERC-1155 (fungible)
        
        if addr not in contracts:
            contracts[addr] = {"name": name, "mint": 0, "burn": 0, "recv": 0, "sent": 0,
                               "collectors": set(), "senders": set()}
        
        if from_addr == ZERO_ADDR:
            mints += 1
            contracts[addr]["mint"] += 1
        elif to_addr == ZERO_ADDR:
            burns += 1
            contracts[addr]["burn"] += 1
        elif from_addr == to_addr:
            self_transfers += 1
        elif to_addr == wl:
            received_from_others += 1
            unique_senders.add(from_addr)
            contracts[addr]["recv"] += 1
            contracts[addr]["senders"].add(from_addr)
            if token_id:
                wallet_tokens[from_addr]["sent"].add(f"{addr}:{token_id}:{token_type}")
        elif from_addr == wl:
            sent_to_others += 1
            # Don't count marketplace contracts as collectors — they're escrow for listings
            is_mkt_to, mkt_name_to = is_marketplace_contract(to_addr)
            if not is_mkt_to:
                unique_collectors.add(to_addr)
            contracts[addr]["sent"] += 1
            if not is_mkt_to:
                contracts[addr]["collectors"].add(to_addr)
            if token_id:
                wallet_tokens[to_addr]["received"].add(f"{addr}:{token_id}:{token_type}")
    
    # Build set of wallets that received NFTs from this artist (actual NFT buyers)
    # Also build timestamp-indexed lookup for matching ETH payments to NFT transfers
    nft_recipients = set()  # wallets that received NFTs from artist
    nft_recipient_txs = {}  # tx_hash -> recipient address (for matching)
    for t in nft_items:
        from_addr = (t.get("from") or {}).get("hash", "").lower()
        to_addr = (t.get("to") or {}).get("hash", "").lower()
        if from_addr == wl and to_addr not in (ZERO_ADDR, wl):
            nft_recipients.add(to_addr)
    
    # Also check for marketplace-mediated sales: NFT sent FROM marketplace TO buyer
    # means the artist sold through the marketplace and the marketplace distributed
    for t in nft_items:
        from_addr = (t.get("from") or {}).get("hash", "").lower()
        to_addr = (t.get("to") or {}).get("hash", "").lower()
        is_mkt, _ = is_marketplace_contract(from_addr)
        if is_mkt and to_addr not in (ZERO_ADDR, wl):
            nft_recipients.add(to_addr)  # buyer who got NFT from marketplace
    
    # --- Analyze transactions for sales + marketplace activity ---
    eth_received = 0.0
    eth_sent = 0.0
    eth_spent_on_nfts = 0.0  # ETH spent buying NFTs (outgoing ETH with NFT-related methods)
    nft_purchases = 0  # number of NFT purchases
    sales_count = 0  # incoming ETH with corresponding NFT transfer = real sale
    exchange_sales = 0  # sales from known exchange hot wallets (dubious)
    verified_sales = 0  # sales from unique non-exchange wallets (trustworthy)
    exchange_eth = 0.0
    verified_eth = 0.0
    sale_sources = []  # detail for report
    deployed_contracts = 0
    marketplace_methods = set()
    
    # Track what the artist DID in human-readable terms
    # Group: "sold on marketplace", "listed on marketplace", "minted on platform",
    # "deployed own contract", "configured royalty/drop"
    artist_activities = {
        "sold_on_marketplace": [],   # (marketplace_name, method)
        "listed_on_marketplace": [], # (marketplace_name, method)
        "minted_on_platform": [],    # (platform_name, method)
        "deployed_contract": [],     # (contract_name)
        "configured_drop": [],       # (platform_name, method)
        "bought_on_marketplace": [], # (marketplace_name, method)
    }
    
    # Map contract names to friendly platform names
    PLATFORM_NAMES = {
        "superrarer": "SuperRare",
        "seadrop": "SeaDrop (by Zora)",
        "tlauctionhouse": "TL Auction House",
        "tlstacks1155": "TL Stacks",
        "tluniversaldeployer": "TL Universal Deployer",
        "adminupgradeabilityproxy": "Auction contract",
        "transparentupgradeableproxy": "NFT minting contract",
    }
    
    def friendly_platform(contract_name, contract_addr):
        if not contract_name:
            return f"Unknown contract ({contract_addr[:10]}...)" if contract_addr else "Unknown"
        key = contract_name.lower().replace(" ", "")
        return PLATFORM_NAMES.get(key, contract_name)
    
    # Known marketplace/sale method names that indicate real sales
    SALE_METHODS = {
        "fulfillBasicOrder", "fulfillAdvancedOrder", "fulfillOrder",
        "finalizeReserveAuction", "buyToken", "commit",
        "createReserveAuction", "createLimitedEditionCollectionAndFixedPriceSale",
    }
    MARKETPLACE_METHODS = {
        "upsertListing", "upsertListingV2", "list", "setBuyPrice",
        "cancel", "cancelAuction", "cancelBuyPrice",
        "setApprovalForAll", "setApprovedMintContracts",
        "createReserveAuction", "createLimitedEditionCollectionAndFixedPriceSale",
        "fulfillBasicOrder", "fulfillAdvancedOrder", "fulfillOrder",
        "finalizeReserveAuction", "buyToken", "commit",
        "upsertListingV2",
    }
    ARTIST_METHODS = {
        "deploy", "createToken", "createNFTCollection", "configureDrop",
        "setRoyalties", "registerExtension", "mintSigned", "mintBatch",
        "mintBaseNew", "mintAndApprove", "mintByETH", "mint",
        "setName", "register", "registerWithConfig", "initializeClaim",
        "updateClaim", "selfDestruct",
    }
    
    # Human-readable method descriptions
    METHOD_LABELS = {
        "fulfillBasicOrder": "sold NFT via marketplace order",
        "fulfillAdvancedOrder": "sold NFT via marketplace order",
        "fulfillOrder": "sold NFT via marketplace order",
        "finalizeReserveAuction": "sold NFT via auction",
        "buyToken": "bought NFT",
        "commit": "bid on auction",
        "upsertListing": "listed NFT for sale",
        "upsertListingV2": "listed NFT for sale",
        "list": "listed NFT for sale",
        "setBuyPrice": "set buy-now price",
        "cancel": "cancelled listing",
        "cancelAuction": "cancelled auction",
        "cancelBuyPrice": "cancelled buy-now price",
        "setApprovalForAll": "approved marketplace to sell their NFTs",
        "setApprovedMintContracts": "approved minting contracts",
        "createReserveAuction": "created auction",
        "createLimitedEditionCollectionAndFixedPriceSale": "created fixed-price sale",
        "deploy": "deployed own NFT contract",
        "createToken": "created new NFT token",
        "createNFTCollection": "created NFT collection",
        "configureDrop": "configured NFT drop",
        "setRoyalties": "set royalties",
        "registerExtension": "registered extension",
        "mintSigned": "minted NFT (signed)",
        "mintBatch": "minted batch of NFTs",
        "mintBaseNew": "minted new NFT",
        "mintAndApprove": "minted and approved NFT",
        "mintByETH": "minted NFT (paid ETH)",
        "mint": "minted NFT",
        "setName": "set name",
        "register": "registered",
        "registerWithConfig": "registered with config",
        "initializeClaim": "initialized claim",
        "updateClaim": "updated claim",
        "selfDestruct": "burned NFT",
    }
    
    for tx in all_txs:
        from_addr = (tx.get("from") or {}).get("hash", "").lower()
        to_addr = (tx.get("to") or {}).get("hash", "").lower()
        value = tx.get("value", "0")
        method = tx.get("method", "") or ""
        to_obj = tx.get("to") or {}
        to_name = to_obj.get("name", "") or ""
        to_hash = to_obj.get("hash", "") or ""
        
        try:
            eth_value = int(value) / 1e18
        except:
            eth_value = 0.0
        
        # Incoming ETH = sale revenue — BUT only count as sale if sender actually received an NFT
        # This prevents false "sales" from circular ETH transfers between wallets
        if to_addr == wl and eth_value > 0:
            # Check if this sender is a known marketplace contract (marketplace sends ETH to artist after sale)
            is_mkt_sender, mkt_name_sender = is_marketplace_contract(from_addr)
            # Check if sender received an NFT from this artist (direct transfer)
            sent_nft_to_sender = from_addr in nft_recipients
            
            if is_mkt_sender or sent_nft_to_sender:
                # This is a real sale — marketplace payout or direct NFT sale
                eth_received += eth_value
                sales_count += 1
                is_exch = is_exchange_address(from_addr)
                if not is_exch:
                    is_exch = is_likely_exchange_wallet(from_addr)
                if is_exch:
                    exchange_sales += 1
                    exchange_eth += eth_value
                else:
                    verified_sales += 1
                    verified_eth += eth_value
                sale_sources.append({
                    "from": from_addr,
                    "eth": round(eth_value, 6),
                    "date": tx.get("timestamp", "")[:10],
                    "exchange": is_exch,
                    "method": method,
                    "nft_transfer": True,
                })
            else:
                # ETH received but no NFT transferred to this wallet — not a sale
                # Could be: circular transfer, refund, payment for something else
                sale_sources.append({
                    "from": from_addr,
                    "eth": round(eth_value, 6),
                    "date": tx.get("timestamp", "")[:10],
                    "exchange": False,
                    "method": method,
                    "nft_transfer": False,
                })
        elif from_addr == wl and eth_value > 0:
            eth_sent += eth_value
            # Track if this was an NFT purchase
            if method in ("buyToken", "fulfillBasicOrder", "fulfillAdvancedOrder", "fulfillOrder", "finalizeReserveAuction", "commit", "mintByETH"):
                eth_spent_on_nfts += eth_value
                nft_purchases += 1
        
        # Contract deployment
        if method == "deploy" or (to_addr is not None and method == "createNFTCollection"):
            deployed_contracts += 1
            platform = friendly_platform(to_name, to_hash)
            artist_activities["deployed_contract"].append(platform)
        
        # Track marketplace + artist methods + human-readable activities
        if method in SALE_METHODS:
            marketplace_methods.add(method)
        if method in MARKETPLACE_METHODS:
            marketplace_methods.add(method)
        if method in ARTIST_METHODS:
            marketplace_methods.add(method)
        
        # Categorize into human-readable activities
        platform = friendly_platform(to_name, to_hash)
        if method in ("fulfillBasicOrder", "fulfillAdvancedOrder", "fulfillOrder", "finalizeReserveAuction"):
            # These could be buying or selling — check direction
            if from_addr == wl:
                artist_activities["sold_on_marketplace"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
            else:
                artist_activities["bought_on_marketplace"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
        elif method in ("upsertListing", "upsertListingV2", "list", "setBuyPrice", "createReserveAuction", "createLimitedEditionCollectionAndFixedPriceSale"):
            artist_activities["listed_on_marketplace"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
        elif method in ("mint", "mintSigned", "mintBatch", "mintBaseNew", "mintAndApprove", "mintByETH"):
            artist_activities["minted_on_platform"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
        elif method in ("configureDrop", "setRoyalties", "createToken", "createNFTCollection", "setApprovedMintContracts", "registerExtension", "register", "registerWithConfig"):
            artist_activities["configured_drop"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
        elif method == "buyToken":
            artist_activities["bought_on_marketplace"].append(f"{METHOD_LABELS.get(method, method)} on {platform}")
    
    # --- Timing ---
    all_ts = [t.get("timestamp", "") for t in nft_items if t.get("timestamp")]
    first_transfer = min(all_ts) if all_ts else None
    last_transfer = max(all_ts) if all_ts else None
    wallet_age_days = 0
    if first_transfer:
        try:
            from datetime import datetime, timezone
            first_dt = datetime.fromisoformat(first_transfer.replace("Z", "+00:00"))
            wallet_age_days = (datetime.now(timezone.utc) - first_dt).days
        except:
            pass
    
    # Convert contract sets to counts for JSON serialization
    contracts_summary = {}
    for addr, info in contracts.items():
        contracts_summary[addr] = {
            "name": info["name"],
            "mint": info["mint"],
            "burn": info["burn"],
            "recv": info["recv"],
            "sent": info["sent"],
            "collectors": len(info["collectors"]),
            "senders": len(info["senders"]),
        }
    
    has_marketplace_sales = bool(marketplace_methods & SALE_METHODS)
    
    return {
        # Raw counts
        "total_nft_transfers": len(nft_items),
        "mints": mints,
        "burns": burns,
        "self_transfers": self_transfers,
        "received_from_others": received_from_others,
        "sent_to_others": sent_to_others,
        # Quality signals
        "unique_collectors": len(unique_collectors),
        "unique_senders": len(unique_senders),
        "sales_count": sales_count,
        "exchange_sales": exchange_sales,
        "verified_sales": verified_sales,
        "exchange_eth": round(exchange_eth, 4),
        "verified_eth": round(verified_eth, 4),
        "sale_sources": sale_sources,
        "eth_received": round(eth_received, 4),
        "eth_sent": round(eth_sent, 4),
        "eth_spent_on_nfts": round(eth_spent_on_nfts, 4),
        "nft_purchases": nft_purchases,
        "has_marketplace_sales": has_marketplace_sales,
        "marketplace_methods": sorted(list(marketplace_methods)),
        "artist_activities": artist_activities,
        # Contract signals
        "deployed_contracts": deployed_contracts,
        "unique_nft_contracts": len(contracts),
        "contracts": contracts_summary,
        # Wallet sets for overlap analysis
        "collector_wallets": list(unique_collectors),
        "sender_wallets": list(unique_senders),
        "wallet_tokens": {w: {"sent": list(v["sent"]), "received": list(v["received"])} for w, v in wallet_tokens.items()},
        "raw_transfers": [{**t, "_chain": chain} for t in nft_items],  # For artwork extraction, tagged with chain
        # Timing
        "first_transfer": first_transfer,
        "last_transfer": last_transfer,
        "wallet_age_days": wallet_age_days,
        "chain": chain,
    }

SUPPORTED_CHAINS = ["ethereum", "base", "polygon", "arbitrum", "optimism", "zora"]

def get_nft_history_multichain(wallet, max_pages=10, chains=None):
    """Fetch NFT history across multiple chains. Returns merged dict with per-chain breakdown."""
    if chains is None:
        chains = SUPPORTED_CHAINS
    
    per_chain = {}
    merged = None
    
    for chain in chains:
        try:
            nft = get_nft_history(wallet, max_pages=max_pages, chain=chain)
            if nft and nft.get("total_nft_transfers", 0) > 0:
                per_chain[chain] = {
                    "transfers": nft["total_nft_transfers"],
                    "mints": nft["mints"],
                    "sales": nft["sales_count"],
                    "collectors": nft["unique_collectors"],
                    "eth_received": nft["eth_received"],
                    "contracts": nft["unique_nft_contracts"],
                }
                if merged is None:
                    merged = nft
                else:
                    # Merge into combined result
                    merged["total_nft_transfers"] += nft["total_nft_transfers"]
                    merged["mints"] += nft["mints"]
                    merged["burns"] += nft["burns"]
                    merged["sent_to_others"] += nft["sent_to_others"]
                    merged["received_from_others"] += nft["received_from_others"]
                    merged["sales_count"] += nft["sales_count"]
                    merged["exchange_sales"] += nft["exchange_sales"]
                    merged["verified_sales"] += nft["verified_sales"]
                    merged["exchange_eth"] = round(merged["exchange_eth"] + nft["exchange_eth"], 4)
                    merged["verified_eth"] = round(merged["verified_eth"] + nft["verified_eth"], 4)
                    merged["eth_received"] = round(merged["eth_received"] + nft["eth_received"], 4)
                    merged["eth_spent_on_nfts"] = round(merged["eth_spent_on_nfts"] + nft["eth_spent_on_nfts"], 4)
                    merged["nft_purchases"] += nft["nft_purchases"]
                    merged["deployed_contracts"] += nft["deployed_contracts"]
                    merged["sale_sources"].extend(nft["sale_sources"])
                    merged["collector_wallets"] = list(set(merged["collector_wallets"] + nft["collector_wallets"]))
                    merged["sender_wallets"] = list(set(merged["sender_wallets"] + nft["sender_wallets"]))
                    merged["raw_transfers"] = merged.get("raw_transfers", []) + nft.get("raw_transfers", [])
                    for c_addr, c_info in nft.get("contracts", {}).items():
                        if c_addr in merged["contracts"]:
                            for k in ["mint", "sent", "recv", "burn", "collectors"]:
                                merged["contracts"][c_addr][k] += c_info.get(k, 0)
                        else:
                            merged["contracts"][c_addr] = c_info
                    for cat, items in nft.get("artist_activities", {}).items():
                        merged["artist_activities"].setdefault(cat, []).extend(items)
                    for w_addr, w_tokens in nft.get("wallet_tokens", {}).items():
                        if w_addr in merged.get("wallet_tokens", {}):
                            merged["wallet_tokens"][w_addr]["sent"] = list(set(merged["wallet_tokens"][w_addr]["sent"] + w_tokens.get("sent", [])))
                            merged["wallet_tokens"][w_addr]["received"] = list(set(merged["wallet_tokens"][w_addr]["received"] + w_tokens.get("received", [])))
                        else:
                            merged.setdefault("wallet_tokens", {})[w_addr] = w_tokens
                    # Use earliest first_transfer and latest last_transfer
                    if nft.get("first_transfer") and (not merged.get("first_transfer") or nft["first_transfer"] < merged["first_transfer"]):
                        merged["first_transfer"] = nft["first_transfer"]
                    if nft.get("last_transfer") and (not merged.get("last_transfer") or nft["last_transfer"] > merged["last_transfer"]):
                        merged["last_transfer"] = nft["last_transfer"]
        except:
            pass
        time.sleep(0.3)
    
    if merged:
        merged["unique_collectors"] = len(merged["collector_wallets"])
        merged["unique_senders"] = len(merged["sender_wallets"])
        merged["unique_nft_contracts"] = len(merged["contracts"])
        merged["per_chain"] = per_chain
        merged["chains_active"] = list(per_chain.keys())
    
    return merged

def get_memes_nominee_rep(profile_id, token):
    """Fetch MemesNominee rep for a profile. Checks both 'MemesNominee' and 'Memes Nominee' categories."""
    if not profile_id:
        return 0
    try:
        data = api_get(f"/profiles/{profile_id}/rep/categories", token)
        total = 0
        for cat in data.get("data", []):
            cat_name = cat.get("category", "").lower().replace(" ", "")
            if "memesnominee" in cat_name:
                total += cat.get("total_rep", 0)
        return total
    except:
        return 0

def get_cic_statements(handle, token):
    """Fetch CIC statements (social links, bio) from the 6529 API.
    Endpoint: GET /profiles/{handle}/cic/statements
    Returns dict: {platform: url, 'bio': text} or empty dict on error.
    """
    try:
        data = api_get(f"/profiles/{handle.lower()}/cic/statements", token)
        result = {}
        for stmt in data:
            st_type = stmt.get("statement_type", "").upper()
            st_value = stmt.get("statement_value", "")
            if st_type == "BIO":
                result["bio"] = st_value
            elif st_type in ("X", "TWITTER"):
                result["x"] = st_value
            elif st_type == "OPENSEA":
                result["opensea"] = st_value
            elif st_type == "SUPER_RARE":
                result["superrare"] = st_value
            elif st_type == "FOUNDATION":
                result["foundation"] = st_value
            elif st_type == "MANIFOLD":
                result["manifold"] = st_value
            elif st_type == "INSTAGRAM":
                result["instagram"] = st_value
            elif st_type == "YOUTUBE":
                result["youtube"] = st_value
            elif st_type == "DISCORD":
                result["discord"] = st_value
            elif st_type == "TELEGRAM":
                result["telegram"] = st_value
            elif st_type == "EMAIL":
                result["email"] = st_value
            elif st_value and st_value.startswith("http"):
                result[st_type.lower()] = st_value
        return result
    except:
        return {}

def extract_social_links(content):
    """Extract social/NFT platform links from text."""
    links = []
    x_links = re.findall(r'https?://(?:x\.com|twitter\.com)/\w+', content)
    ig_links = re.findall(r'https?://(?:instagram\.com|instagr\.am)/\w+', content)
    nft_links = re.findall(r'https?://(?:objkt\.com|transient\.xyz|manifold\.xyz|opensea\.io|foundation\.app|superrare\.com|rarible\.com)\S+', content)
    links.extend(x_links + ig_links + nft_links)
    return links

def verify_social_links(links):
    """Verify social links exist and check if profile is an artist.
    Returns dict with verified links + artist signals."""
    result = {"verified": [], "failed": [], "artist_signals": 0}
    for link in links:
        # Extract platform + handle
        x_match = re.search(r'(?:x\.com|twitter\.com)/(\w+)', link)
        if x_match:
            handle = x_match.group(1)
            if handle.lower() == "i":
                # https://x.com/i/... is a redirect, not a profile
                continue
            try:
                req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
                resp = urllib.request.urlopen(req, timeout=10)
                html = resp.read().decode("utf-8", errors="ignore")
                og_title = re.search(r'og:title["\s]+content="([^"]+)"', html)
                og_desc = re.search(r'og:description["\s]+content="([^"]+)"', html)
                if og_title:
                    desc = og_desc.group(1).lower() if og_desc else ""
                    # Check for artist signals in bio
                    artist_keywords = ["artist", "art", "nft", "digital art", "photographer",
                                       "illustrator", "painter", "creative", "designer",
                                       "memes", "6529", "collection", "gallery", "museum"]
                    is_artist = any(kw in desc for kw in artist_keywords)
                    if is_artist:
                        result["artist_signals"] += 1
                    result["verified"].append({
                        "platform": "x",
                        "handle": handle,
                        "title": og_title.group(1),
                        "is_artist": is_artist,
                        "bio": og_desc.group(1)[:100] if og_desc else "",
                    })
                else:
                    result["failed"].append({"link": link, "reason": "No og:title"})
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    result["failed"].append({"link": link, "reason": "Profile not found (404)"})
                else:
                    result["failed"].append({"link": link, "reason": f"HTTP {e.code}"})
            except Exception as e:
                result["failed"].append({"link": link, "reason": str(e)[:50]})
            time.sleep(0.3)
        # Manifold profiles are verifiable
        elif "manifold.xyz" in link:
            try:
                req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
                resp = urllib.request.urlopen(req, timeout=10)
                html = resp.read().decode("utf-8", errors="ignore")
                og_title = re.search(r'og:title["\s]+content="([^"]+)"', html)
                if og_title:
                    result["verified"].append({
                        "platform": "manifold",
                        "title": og_title.group(1),
                        "is_artist": True,  # Manifold profiles are artist pages
                        "bio": "",
                    })
                    result["artist_signals"] += 1
            except:
                pass
            time.sleep(0.3)
        # Instagram and other JS-rendered platforms — can't verify reliably
        else:
            result["failed"].append({"link": link, "reason": "Platform not verifiable (JS-rendered)"})
    return result

def compute_phash(img_data):
    """Compute perceptual hash from image bytes for duplicate detection."""
    try:
        img = Image.open(io.BytesIO(img_data)).convert("L").resize((8, 8))
        pixels = list(img.get_flattened_data())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p > avg else "0" for p in pixels)
        return int(bits, 16)
    except:
        return None

def gemini_artwork_analysis(img_data):
    """Use Gemini to check if artwork is AI-generated or original.
    Returns dict with: is_ai_suspected (bool), analysis (str)."""
    api_key = ""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(env_path):
        env_path = "/home/prenode/.hermes/profiles/themanager/.env"
    try:
        with open(env_path) as f:
            for line in f:
                if "GOOGLE_API_KEY" in line and "=" in line and not line.strip().startswith("#"):
                    api_key = line.split("=", 1)[1].strip()
                    break
    except:
        pass
    if not api_key:
        return {"is_ai_suspected": False, "analysis": "No API key for Gemini"}
    try:
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        if max(img.size) > 512:
            img = img.resize((512, int(512 * img.size[1] / img.size[0])), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
        body = {
            "contents": [{"parts": [
                {"text": "Analyze this artwork briefly. 1) AI-generated or hand-made? 2) Style/medium? 3) Any AI indicators (unnatural textures, garbled text, inconsistent lighting)? Answer in 2-3 sentences."},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 150}
        }
        req = urllib.request.Request(gemini_url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
        is_ai = False
        analysis_lower = analysis.lower()
        # Check for explicit AI suspicion — must say it IS ai-generated, not that it ISN'T
        ai_positive = any(kw in analysis_lower for kw in [
            "likely ai-generated", "appears to be ai", "is ai-generated", 
            "machine-generated", "ai-generated image", "ai generated image",
            "appears ai-generated", "seems to be ai", "likely ai generated"
        ])
        # Explicit "not ai-generated" means it's fine
        if "not ai-generated" in analysis_lower or "not ai generated" in analysis_lower or "not machine-generated" in analysis_lower:
            ai_positive = False
        is_ai = ai_positive
        return {"is_ai_suspected": is_ai, "analysis": analysis.strip()}
    except Exception as e:
        return {"is_ai_suspected": False, "analysis": f"Gemini error: {str(e)[:50]}"}

def analyze_artwork(media_url):
    """Download and analyze a single artwork image.
    Returns dict with phash, md5, ai_analysis."""
    try:
        req = urllib.request.Request(media_url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        img_data = resp.read()
    except:
        return {"phash": None, "md5": None, "ai_analysis": None, "error": "download failed"}

    md5 = hashlib.md5(img_data).hexdigest()
    phash = compute_phash(img_data)
    ai = gemini_artwork_analysis(img_data)
    return {"phash": phash, "md5": md5, "ai_analysis": ai}

def is_rep_giver(posts):
    """Detect if someone is posting to GIVE rep rather than seek it.
    Signals: mentions giving/adding rep to others, high level (88+), no artwork posts."""
    all_content = " ".join(p["content"] for p in posts).lower()
    giver_signals = 0
    # Check for rep-giving language
    for phrase in ["added rep", "gave you rep", "here's some rep", "rep to ", "added some rep",
                   "giving rep", "you need 50k", "50k memesnominee", "need 50k rep",
                   "rep incoming", "sent rep", "boom rep", "mega rep"]:
        if phrase in all_content:
            giver_signals += 1
    # Check if they mention other handles a lot (rep-givers tag recipients)
    mention_count = all_content.count("@")
    if mention_count >= 3:
        giver_signals += 1
    return giver_signals >= 2

def is_seeking_nomination(posts):
    """Check if someone is actually seeking nomination — asking for rep OR posting artwork.
    Returns False for pure GMeme posts with no artwork and no rep requests."""
    has_artwork = any(p["has_media"] for p in posts)
    all_content = " ".join(p["content"] for p in posts).lower()

    # Asking for rep / nomination
    seeking_phrases = ["rep", "nominate", "nomination", "seeking", "submit", "main stage",
                       "50k", "50000", "memesnominee", "please", "help me", "my art",
                       "my work", "my artwork", "artist", "art", "portfolio", "collection"]
    asking = any(phrase in all_content for phrase in seeking_phrases)

    # Substantive post (>30 chars, not just greeting)
    has_substantive = any(len(p["content"].strip()) > 30 for p in posts)

    return has_artwork or (asking and has_substantive)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"rep_given": {}, "replies_posted": {}}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"rep_given": {}, "replies_posted": {}}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============ MAIN ============

def main():
    token = load_token()
    state = load_state()

    # 1. Fetch wave drops (up to 200)
    print("Fetching Seeking Nomination wave drops...")
    wave_data = api_get(f"/v2/waves/{SEEKING_NOMINATION_WAVE}/drops?limit=200", token)
    drops = wave_data.get("drops", [])
    print(f"  Got {len(drops)} drops")

    # 2. Extract unique authors
    author_posts = defaultdict(list)
    author_info = {}
    for d in drops:
        author = d.get("author", {})
        handle = author.get("handle", "unknown")
        if handle.lower() in IGNORE_HANDLES:
            continue
        content = d.get("content", "") or ""
        media = d.get("media", [])
        drop_id = d.get("id", "")
        author_posts[handle].append({"content": content, "has_media": bool(media), "drop_id": drop_id, "media_urls": [m.get("url", "") for m in media] if media else []})
        if handle not in author_info:
            author_info[handle] = {
                "display": author.get("display", ""),
                "level": author.get("level", 0),
                "rep": author.get("rep", 0),
                "profile_id": author.get("id", ""),
            }

    print(f"  {len(author_posts)} unique authors (after ignore list)")

    # 3. Fetch full profiles
    print("Fetching identity profiles...")
    profiles = {}
    for handle in author_posts:
        try:
            p = api_get(f"/identities/{handle}", token)
            profiles[handle] = {
                "handle": handle,
                "profile_id": p.get("id", ""),
                "wallet": p.get("primary_wallet", ""),
                "rep": p.get("rep", 0),
                "level": p.get("level", 0),
                "tdh": p.get("tdh", 0),
                "cic": p.get("cic", 0),
                "profile_wave_id": p.get("profile_wave_id", ""),
                "active_ms_submissions": p.get("active_main_stage_submission_ids", []),
                "ms_winner_ids": p.get("winner_main_stage_drop_ids", []),
            }
            time.sleep(0.3)
        except Exception as e:
            profiles[handle] = {"handle": handle, "error": str(e), "wallet": ""}

    # 4. On-chain checks: tx count + NFT history via Blockscout
    print("Checking on-chain activity (tx count + NFT history)...")
    for handle, p in profiles.items():
        if p.get("error") or not p.get("wallet"):
            p["tx_count"] = -1
            p["nft_history"] = None
            continue
        p["tx_count"] = get_tx_count(p["wallet"])
        
        # Get all consolidated wallets for this profile
        all_wallets = [p["wallet"]]
        try:
            id_data = api_get(f"/identities/{handle}", token)
            for w in id_data.get("wallets", []):
                w_addr = w.get("wallet", "")
                if w_addr and w_addr.lower() not in [x.lower() for x in all_wallets]:
                    all_wallets.append(w_addr)
            p["all_wallets"] = all_wallets
        except:
            p["all_wallets"] = all_wallets
        
        # Fetch NFT history for ALL consolidated wallets across ALL chains
        merged_nft = None
        for wi, w in enumerate(all_wallets):
            nft = get_nft_history_multichain(w, max_pages=10)
            if not nft:
                continue
            if merged_nft is None:
                merged_nft = nft
            else:
                # Merge across wallets
                merged_nft["total_nft_transfers"] += nft["total_nft_transfers"]
                merged_nft["mints"] += nft["mints"]
                merged_nft["burns"] += nft["burns"]
                merged_nft["sent_to_others"] += nft["sent_to_others"]
                merged_nft["received_from_others"] += nft["received_from_others"]
                merged_nft["sales_count"] += nft["sales_count"]
                merged_nft["exchange_sales"] += nft["exchange_sales"]
                merged_nft["verified_sales"] += nft["verified_sales"]
                merged_nft["exchange_eth"] = round(merged_nft["exchange_eth"] + nft["exchange_eth"], 4)
                merged_nft["verified_eth"] = round(merged_nft["verified_eth"] + nft["verified_eth"], 4)
                merged_nft["eth_received"] = round(merged_nft["eth_received"] + nft["eth_received"], 4)
                merged_nft["eth_spent_on_nfts"] = round(merged_nft["eth_spent_on_nfts"] + nft["eth_spent_on_nfts"], 4)
                merged_nft["nft_purchases"] += nft["nft_purchases"]
                merged_nft["deployed_contracts"] += nft["deployed_contracts"]
                merged_nft["sale_sources"].extend(nft["sale_sources"])
                merged_nft["collector_wallets"] = list(set(merged_nft["collector_wallets"] + nft["collector_wallets"]))
                merged_nft["sender_wallets"] = list(set(merged_nft["sender_wallets"] + nft["sender_wallets"]))
                merged_nft["raw_transfers"] = merged_nft.get("raw_transfers", []) + nft.get("raw_transfers", [])
                for c_addr, c_info in nft.get("contracts", {}).items():
                    if c_addr in merged_nft["contracts"]:
                        for k in ["mint", "sent", "recv", "burn", "collectors"]:
                            merged_nft["contracts"][c_addr][k] += c_info.get(k, 0)
                    else:
                        merged_nft["contracts"][c_addr] = c_info
                for cat, items in nft.get("artist_activities", {}).items():
                    merged_nft["artist_activities"].setdefault(cat, []).extend(items)
                for w_addr, w_tokens in nft.get("wallet_tokens", {}).items():
                    if w_addr in merged_nft.get("wallet_tokens", {}):
                        merged_nft["wallet_tokens"][w_addr]["sent"] = list(set(merged_nft["wallet_tokens"][w_addr]["sent"] + w_tokens.get("sent", [])))
                        merged_nft["wallet_tokens"][w_addr]["received"] = list(set(merged_nft["wallet_tokens"][w_addr]["received"] + w_tokens.get("received", [])))
                    else:
                        merged_nft.setdefault("wallet_tokens", {})[w_addr] = w_tokens
                if nft.get("first_transfer") and (not merged_nft.get("first_transfer") or nft["first_transfer"] < merged_nft["first_transfer"]):
                    merged_nft["first_transfer"] = nft["first_transfer"]
                if nft.get("last_transfer") and (not merged_nft.get("last_transfer") or nft["last_transfer"] > merged_nft["last_transfer"]):
                    merged_nft["last_transfer"] = nft["last_transfer"]
                # Merge per-chain data
                for chain, info in nft.get("per_chain", {}).items():
                    if chain not in merged_nft.get("per_chain", {}):
                        merged_nft.setdefault("per_chain", {})[chain] = info
                    else:
                        merged_nft["per_chain"][chain]["transfers"] += info["transfers"]
                        merged_nft["per_chain"][chain]["mints"] += info["mints"]
                        merged_nft["per_chain"][chain]["sales"] += info["sales"]
                        merged_nft["per_chain"][chain]["collectors"] += info["collectors"]
                        merged_nft["per_chain"][chain]["eth_received"] = round(merged_nft["per_chain"][chain]["eth_received"] + info["eth_received"], 4)
                        merged_nft["per_chain"][chain]["contracts"] += info["contracts"]
            time.sleep(0.3)
        
        if merged_nft:
            merged_nft["unique_collectors"] = len(merged_nft["collector_wallets"])
            merged_nft["unique_senders"] = len(merged_nft["sender_wallets"])
            merged_nft["unique_nft_contracts"] = len(merged_nft["contracts"])
            merged_nft["chains_active"] = list(merged_nft.get("per_chain", {}).keys())
        p["nft_history"] = merged_nft

    # 5. Profile wave drops (media check + social links)
    print("Checking profile waves for artwork + social links...")
    for handle, p in profiles.items():
        if p.get("error"):
            p["pw_has_media"] = False
            p["pw_drop_count"] = 0
            p["social_links"] = []
            continue
        pw_id = p.get("profile_wave_id", "")
        p["pw_has_media"] = False
        p["pw_drop_count"] = 0
        p["social_links"] = []
        p["cic_statements"] = {}
        
        # Primary source: CIC statements API (profile social links)
        cic = get_cic_statements(handle, token)
        p["cic_statements"] = cic
        if cic:
            # Convert CIC statements to social links for verification
            for platform, url in cic.items():
                if platform == "bio":
                    continue
                p["social_links"].append(url)
        
        # Also search social links from wave posts (fallback/supplement)
        for post in author_posts.get(handle, []):
            p["social_links"].extend(extract_social_links(post["content"]))

        # Also search social links from ALL waves where the artist posted
        # Uses profile-logs to find waves, then fetches drop content
        try:
            logs = api_get(f"/profile-logs?profile={handle}&log_type=DROP_CREATED&page_size=200", token)
            wave_ids_seen = set()
            for log_entry in logs.get("data", []):
                wid = log_entry.get("additional_data_2", "")
                if wid and wid != "CHAT" and wid not in wave_ids_seen:
                    wave_ids_seen.add(wid)
            # Fetch drops from up to 10 waves to find social links
            for wid in list(wave_ids_seen)[:10]:
                try:
                    w_data = api_get(f"/waves/{wid}/drops?limit=200", token)
                    w_drops = w_data.get("drops", [])
                    for d in w_drops:
                        if d.get("author", {}).get("handle", "").lower() == handle.lower():
                            parts = d.get("parts", [])
                            for part in parts:
                                content = part.get("content", "") or ""
                                p["social_links"].extend(extract_social_links(content))
                    time.sleep(0.2)
                except:
                    pass
        except:
            pass

        if not pw_id:
            continue
        try:
            pw_data = api_get(f"/v2/waves/{pw_id}/drops?limit=20", token)
            pw_drops = pw_data.get("drops", [])
            p["pw_drop_count"] = len(pw_drops)
            for d in pw_drops:
                if d.get("media"):
                    p["pw_has_media"] = True
                content = d.get("content", "") or ""
                p["social_links"].extend(extract_social_links(content))
            time.sleep(0.3)
        except:
            pass

        p["social_links"] = list(set(p["social_links"]))[:5]

    # 5b. Verify social links (X/Twitter + Manifold)
    print("Verifying social links...")
    for handle, p in profiles.items():
        if p.get("error") or not p.get("social_links"):
            p["social_verified"] = {"verified": [], "failed": [], "artist_signals": 0}
            continue
        p["social_verified"] = verify_social_links(p["social_links"])
        time.sleep(0.2)

def get_artwork_from_minted_collections(wallet, nft_data, max_images=3, all_wallets=None):
    """Fetch artwork image URLs from NFT collections the artist actually minted (from zero address).
    Uses Blockscout token instance metadata to get image URLs.
    Tries multiple chains (ethereum, base, polygon, etc.) for each token.
    all_wallets: list of all consolidated wallets (for checking which transfers are mints)
    Returns list of dicts: {collection, token_id, name, image, chain}"""
    CHAIN_URLS = {
        "ethereum": "https://eth.blockscout.com/api/v2",
        "base": "https://base.blockscout.com/api/v2",
        "polygon": "https://polygon.blockscout.com/api/v2",
        "arbitrum": "https://arbitrum.blockscout.com/api/v2",
        "optimism": "https://optimism.blockscout.com/api/v2",
        "zora": "https://explorer.zora.energy/api/v2",
    }
    ZERO_ADDR = "0x0000000000000000000000000000000000000000"
    
    # Build set of all artist wallets for checking
    artist_wallets = set()
    if all_wallets:
        for w in all_wallets:
            artist_wallets.add(w.lower())
    artist_wallets.add(wallet.lower())
    
    # Find minted tokens from nft_data (merged across wallets and chains)
    # Track which chain each mint came from
    minted_contracts = {}
    for t in nft_data.get("raw_transfers", []):
        from_a = (t.get("from") or {}).get("hash", "").lower() if t.get("from") else ""
        to_a = (t.get("to") or {}).get("hash", "").lower() if t.get("to") else ""
        token = t.get("token", {})
        chain = t.get("_chain", "ethereum")
        if "ERC-721" in token.get("type", "") and from_a == ZERO_ADDR and to_a in artist_wallets:
            addr = token.get("address_hash", "").lower()
            name = token.get("name", "")
            token_id = (t.get("total") or {}).get("token_id", "")
            if addr and token_id:
                if addr not in minted_contracts:
                    minted_contracts[addr] = {"name": name, "token_ids": set(), "chains": set()}
                minted_contracts[addr]["token_ids"].add(token_id)
                minted_contracts[addr]["chains"].add(chain)
    
    # Fetch token instance metadata for images - try each chain that had activity
    artwork = []
    for addr, info in minted_contracts.items():
        for tid in list(info["token_ids"])[:5]:
            if len(artwork) >= max_images:
                break
            chains_to_try = list(info["chains"]) if info["chains"] else ["ethereum"]
            for chain in chains_to_try:
                if len(artwork) >= max_images:
                    break
                try:
                    bs_url = CHAIN_URLS.get(chain, CHAIN_URLS["ethereum"])
                    url = f"{bs_url}/tokens/{addr}/instances/{tid}"
                    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
                    resp = urllib.request.urlopen(req, timeout=15)
                    inst = json.loads(resp.read())
                    metadata = inst.get("metadata", {}) or {}
                    image = metadata.get("image", "")
                    name = metadata.get("name", "")
                    if image:
                        if image.startswith("ipfs://"):
                            cid = image.replace("ipfs://", "")
                            image = f"https://gateway.pinata.cloud/ipfs/{cid}"
                        artwork.append({"collection": info["name"], "token_id": tid, "name": name, "image": image, "chain": chain})
                        break
                    time.sleep(0.3)
                except:
                    continue
        if len(artwork) >= max_images:
            break
    
    return artwork

    # 5c. Artwork analysis (Gemini AI detection + perceptual hash for dupes)
    print("Analyzing artwork (AI detection + dupe hashing)...")
    all_phashes = {}  # phash → list of handles
    for handle, p in profiles.items():
        p["artwork_analysis"] = []
        if p.get("error"):
            continue
        # Collect media URLs for artwork analysis
        # Priority: 1) On-chain minted artwork 2) Profile wave media 3) Seeking Nomination post media
        media_urls = []
        artwork_source = "none"
        
        # 1. On-chain artwork from minted collections
        if p.get("nft_data"):
            onchain_art = get_artwork_from_minted_collections(p["wallet"], p["nft_data"], max_images=3, all_wallets=p.get("all_wallets"))
            if onchain_art:
                artwork_source = "on-chain"
                p["onchain_artwork"] = onchain_art
                for art in onchain_art:
                    media_urls.append(art["image"])
        
        # 2. Profile wave media
        if not media_urls:
            pw_id = p.get("profile_wave_id", "")
            if pw_id:
                try:
                    pw_data = api_get(f"/v2/waves/{pw_id}/drops?limit=5", token)
                    for d in pw_data.get("drops", []):
                        for m in d.get("media", []) or []:
                            media_urls.append(m.get("url", ""))
                    if media_urls:
                        artwork_source = "profile wave"
                    time.sleep(0.2)
                except:
                    pass
        
        # 3. Seeking Nomination post media
        if not media_urls:
            for post in author_posts.get(handle, []):
                if post.get("has_media") and post.get("media_urls"):
                    media_urls.extend(post.get("media_urls", [])[:2])
            if media_urls:
                artwork_source = "seeking nomination"

        # Analyze up to 3 images per artist (to stay within API limits)
        for url in media_urls[:3]:
            if not url:
                continue
            result = analyze_artwork(url)
            p["artwork_analysis"].append(result)
            if result.get("phash") is not None:
                phash_key = f"{result['phash']:016x}"
                if phash_key not in all_phashes:
                    all_phashes[phash_key] = []
                all_phashes[phash_key].append(handle)
            time.sleep(0.5)

    # Flag duplicate artwork across artists
    dupe_hashes = {h: artists for h, artists in all_phashes.items() if len(artists) > 1}
    if dupe_hashes:
        print(f"  ⚠️ Found {len(dupe_hashes)} duplicate artwork hashes across artists!")
        for h, artists in dupe_hashes.items():
            print(f"    Hash {h}: {artists}")
    for handle, p in profiles.items():
        p["has_duplicate_artwork"] = False
        for a in p.get("artwork_analysis", []):
            if a.get("phash") is not None:
                phash_key = f"{a['phash']:016x}"
                if phash_key in dupe_hashes:
                    p["has_duplicate_artwork"] = True
        time.sleep(0.2)

    # 6. Content analysis
    for handle, p in profiles.items():
        posts = author_posts.get(handle, [])
        p["post_count"] = len(posts)
        p["has_media_in_sn"] = any(post["has_media"] for post in posts)
        p["is_rep_giver"] = is_rep_giver(posts)
        p["is_seeking"] = is_seeking_nomination(posts)
        substantive = [post for post in posts if len(post["content"].strip()) > 50 and "gmeme" not in post["content"].lower()[:10]]
        p["has_substantive"] = len(substantive) > 0
        gmeme_count = sum(1 for post in posts if len(post["content"].strip().lower().replace("!", "").replace(".", "").replace("\U0001f64f", "").strip()) < 15 and "gm" in post["content"].lower())
        p["gmeme_only"] = gmeme_count == len(posts) and len(posts) > 0

    # Generate overall assessment for a profile
    def generate_assessment(p, nft_data):
        """Generate a narrative overall assessment from all collected signals."""
        strengths = []
        concerns = []
        
        if not nft_data:
            return {"verdict": "NEW — no on-chain activity", "strengths": [], "concerns": ["No NFT history found"]}
        
        # Artist activity
        activities = nft_data.get("artist_activities", {})
        deployed = nft_data.get("deployed_contracts", 0)
        mints = nft_data.get("mints", 0)
        marketplace_methods = nft_data.get("marketplace_methods", [])
        
        if deployed > 0:
            strengths.append(f"Deployed {deployed} own NFT contract(s)")
        if mints > 10:
            strengths.append(f"Minted {mints} NFTs on established platforms")
        if activities.get("sold_on_marketplace"):
            strengths.append("Has sold NFTs via marketplace")
        if activities.get("configured_drop"):
            strengths.append("Configured own NFT drops")
        
        # Social verification
        cic = p.get("cic_statements", {})
        sv = p.get("social_verified", {})
        if cic and cic.get("bio"):
            strengths.append(f"Profile bio: \"{cic['bio'][:80]}\"")
        if sv.get("verified"):
            verified_platforms = [v.get("platform", "?") for v in sv["verified"]]
            strengths.append(f"Verified social: {', '.join(verified_platforms)}")
            for v in sv["verified"]:
                if v.get("is_artist"):
                    strengths.append(f"Artist bio on {v['platform']}")
                    break
        elif not p.get("social_links"):
            concerns.append("No social links found")
        else:
            # Has links but none verified
            concerns.append("Social links present but unverified")
        
        # Artwork
        artwork = p.get("artwork_analysis", [])
        ai_flags = sum(1 for a in artwork if a.get("ai_analysis", {}).get("is_ai_suspected"))
        if artwork and ai_flags == 0:
            strengths.append("Artwork confirmed hand-made (not AI-generated)")
        if ai_flags > 0:
            concerns.append(f"AI-suspected artwork ({ai_flags}/{len(artwork)} images)")
        if p.get("has_duplicate_artwork"):
            concerns.append("Duplicate artwork detected across artists")
        
        # Community engagement
        post_count = p.get("post_count", 0)
        if post_count > 50:
            strengths.append(f"Active 6529 community member ({post_count} posts)")
        elif post_count < 5:
            concerns.append(f"Very low post count ({post_count})")
        
        # Rep diversity
        rep_data = p.get("rep_categories", [])
        rep_sources = sum(1 for cat in rep_data if cat.get("total_rep", 0) > 0)
        if rep_sources >= 3:
            strengths.append(f"Rep from {rep_sources} different community members")
        elif rep_sources == 1:
            concerns.append("Rep from only one source")
        
        # Sales analysis
        sales = nft_data.get("sales_count", 0)
        exchange_sales = nft_data.get("exchange_sales", 0)
        verified_sales = nft_data.get("verified_sales", 0)
        
        if sales > 0 and exchange_sales == sales:
            concerns.append(f"All {sales} sales from exchange wallets — no verifiable real collectors")
        elif verified_sales > 0:
            strengths.append(f"{verified_sales} verified sales from real buyers")
        
        # Burn rate
        burns = nft_data.get("burns", 0)
        sent = nft_data.get("sent_to_others", 0)
        if sent > 0 and burns / max(sent + burns, 1) > 0.5:
            concerns.append(f"High burn rate ({burns}/{sent+burns} = {burns*100//(sent+burns)}%)")
        
        # Wallet overlap — two-way transfer analysis
        collectors = set(nft_data.get("collector_wallets", []))
        senders = set(nft_data.get("sender_wallets", []))
        both = collectors & senders
        wallet_tokens = nft_data.get("wallet_tokens", {})
        wash_flags = []
        collector_swaps = []
        for addr in both:
            is_mkt, _ = is_marketplace_contract(addr)
            if is_mkt:
                continue  # marketplace escrow, skip
            # Check if same token IDs went back and forth
            wt = wallet_tokens.get(addr, {})
            sent_ids = set(wt.get("sent", []))
            recv_ids = set(wt.get("received", []))
            same_tokens = sent_ids & recv_ids
            
            # ERC-721 same-ID = likely wash trading, ERC-1155 same-ID = may be normal (fungible)
            erc721_same = [t for t in same_tokens if "ERC-721" in t]
            erc1155_same = [t for t in same_tokens if "ERC-1155" in t]
            
            is_single, coll = is_single_collection_wallet(addr)
            if erc721_same:
                wash_flags.append(f"wash trading: same ERC-721 token(s) round-tripped with {addr[:14]}")
            elif is_single:
                wash_flags.append(f"suspicious single-collection wallet ({coll})")
            else:
                collector_swaps.append(f"collector swap: different tokens exchanged with {addr[:14]}")
        if wash_flags:
            concerns.append(f"Two-way NFT transfer with {', '.join(wash_flags)}")
        # Collector swaps are NOT a concern — normal trading behavior
        
        # Seller/rep overlap
        if p.get("seller_rep_overlap"):
            concerns.append(f"Seller/Rep overlap: {p['seller_rep_overlap']}")
        
        # Collector quality
        if nft_data.get("unique_collectors", 0) > 0 and exchange_sales == sales and sales > 0:
            concerns.append("Collectors are mostly no-profile, low-level wallets")
        
        # Wallet age
        age = nft_data.get("wallet_age_days", 0)
        if age > 365:
            strengths.append(f"Wallet active {age} days")
        elif age < 30 and age > 0:
            concerns.append(f"Wallet very new ({age} days)")
        
        # Profile wave
        if not p.get("profile_wave_id"):
            concerns.append("No profile wave set up")
        
        # Determine verdict
        category = p.get("category", "UNCLEAR")
        if category == "ESTABLISHED":
            verdict = "ESTABLISHED — strong on-chain and community presence"
        elif category == "LIKELY_REAL":
            if len(concerns) > len(strengths):
                verdict = "LIKELY REAL with significant concerns"
            else:
                verdict = "LIKELY REAL"
        elif category == "SUSPICIOUS":
            verdict = "SUSPICIOUS"
        elif category == "NEW_EMPTY":
            verdict = "NEW — minimal activity"
        else:
            verdict = "UNCLEAR — insufficient signals"
        
        return {"verdict": verdict, "strengths": strengths, "concerns": concerns}

    # 7. Fetch MemesNominee rep balance
    print("Checking MemesNominee rep balances...")
    for handle, p in profiles.items():
        if p.get("error"):
            p["memes_nominee_rep"] = 0
            continue
        p["memes_nominee_rep"] = get_memes_nominee_rep(p.get("profile_id", ""), token)
        time.sleep(0.3)

    # 8. Classify
    for handle, p in profiles.items():
        if p.get("error"):
            p["category"] = "SUSPICIOUS"
            p["signals"] = ["Profile fetch error"]
            continue

        score = 0
        signals = []

        if p.get("ms_winner_ids"):
            score += 4; signals.append(f"MS winner ({len(p['ms_winner_ids'])})")
        if p.get("active_ms_submissions"):
            score += 3; signals.append(f"MS submissions ({len(p['active_ms_submissions'])})")
        if p.get("pw_has_media"):
            score += 3; signals.append("Profile wave with artwork")
        elif p.get("pw_drop_count", 0) > 5:
            score += 1; signals.append(f"Profile wave ({p['pw_drop_count']} drops, no media)")
        if p.get("social_links"):
            score += 1; signals.append(f"Social links: {p['social_links'][:2]}")
        # Verified social links with artist bio — stronger signal
        sv = p.get("social_verified", {})
        if sv.get("verified"):
            for v in sv["verified"]:
                if v.get("is_artist"):
                    score += 2; signals.append(f"Verified {v['platform']} artist: @{v.get('handle', '?')} — {v.get('bio', '')[:50]}")
                    break
            else:
                score += 1; signals.append(f"Verified social: {sv['verified'][0].get('platform')} @{sv['verified'][0].get('handle', '?')}")
        if sv.get("failed"):
            for f in sv["failed"]:
                if "404" in f.get("reason", ""):
                    signals.append(f"Dead social link: {f['link']}")
                    break
        if p.get("rep", 0) > 100000:
            score += 2; signals.append(f"High rep ({p['rep']:,})")
        elif p.get("rep", 0) > 50000:
            score += 1; signals.append(f"Rep {p['rep']:,}")
        if p.get("tdh", 0) > 1000:
            score += 1; signals.append(f"TDH {p['tdh']:,}")
        if p.get("has_substantive"):
            score += 1; signals.append("Substantive posts")
        if p.get("tx_count", 0) == 0:
            signals.append("Zero on-chain tx")
        if not p.get("profile_wave_id"):
            signals.append("No profile wave")
        if p.get("rep", 0) < 1000:
            signals.append(f"Very low rep ({p['rep']})")

        # NFT on-chain history (Blockscout) — quality-based scoring
        nft = p.get("nft_history")
        if nft:
            collectors = nft.get("unique_collectors", 0)
            senders = nft.get("unique_senders", 0)
            sales = nft.get("sales_count", 0)
            exchange_sales = nft.get("exchange_sales", 0)
            verified_sales = nft.get("verified_sales", 0)
            exchange_eth = nft.get("exchange_eth", 0)
            verified_eth = nft.get("verified_eth", 0)
            eth_recv = nft.get("eth_received", 0)
            has_sales = nft.get("has_marketplace_sales", False)
            deployed = nft.get("deployed_contracts", 0)
            mints = nft.get("mints", 0)
            burns = nft.get("burns", 0)
            age_days = nft.get("wallet_age_days", 0)
            methods = nft.get("marketplace_methods", [])
            real_transfers = nft.get("received_from_others", 0) + nft.get("sent_to_others", 0)

            # 1. Sales — weighted by source quality
            # Verified sales (from unique non-exchange wallets) = real buyers
            # Exchange sales (from Binance/Gemini hot wallets) = dubious, could be self-buying
            if verified_sales >= 3:
                score += 4; signals.append(f"💰 {verified_sales} verified sales ({verified_eth} ETH from unique wallets)")
            elif verified_sales >= 1:
                score += 2; signals.append(f"💰 {verified_sales} verified sale(s), {verified_eth} ETH")
            
            if exchange_sales > 0:
                if exchange_sales == sales:
                    # ALL sales are from exchanges — highly dubious
                    signals.append(f"⚠️ All {exchange_sales} sales from exchange wallets (possible self-buying)")
                else:
                    signals.append(f"⚠️ {exchange_sales}/{sales} sales from exchange wallets (dubious)")
            
            # Total sales still counts weakly if there are some verified
            if verified_sales == 0 and exchange_sales >= 3:
                # Only exchange sales, no verified — don't count as positive signal
                pass
            elif verified_sales == 0 and exchange_sales >= 1:
                score += 1; signals.append(f"Received {eth_recv} ETH (exchange sources only)")

            # 2. Marketplace sale methods (Seaport, auctions, etc.)
            if has_sales:
                sale_methods = [m for m in methods if m in (
                    "fulfillBasicOrder", "fulfillAdvancedOrder", "fulfillOrder",
                    "finalizeReserveAuction", "buyToken", "commit"
                )]
                if sale_methods:
                    score += 2; signals.append(f"Marketplace sales: {', '.join(sale_methods[:3])}")

            # 3. Collector diversity — unique wallets that received/bought
            if collectors >= 10:
                score += 3; signals.append(f"👥 {collectors} unique collectors")
            elif collectors >= 5:
                score += 2; signals.append(f"👥 {collectors} unique collectors")
            elif collectors >= 1:
                score += 1; signals.append(f"{collectors} collector(s)")

            # 4. Contract deployment — real artist signal
            if deployed > 0:
                score += 2; signals.append(f"🎨 Deployed {deployed} NFT contract(s)")

            # 5. Real transfers (excluding mints/burns/self)
            if real_transfers > 0:
                signals.append(f"Real transfers: {real_transfers} (excluding {mints} mints, {burns} burns)")
            elif mints > 0 and collectors == 0 and sales == 0:
                score -= 1; signals.append(f"⚠️ {mints} mints but no sales or collectors (possible fake activity)")

            # 6. Wallet age
            if age_days > 365:
                score += 1; signals.append(f"Wallet active {age_days} days")
            elif age_days > 90:
                signals.append(f"Wallet active {age_days} days")
            elif age_days < 7 and age_days > 0:
                signals.append(f"⚠️ Wallet very new ({age_days} days)")

            # 7. Artist methods (setRoyalties, configureDrop, etc.)
            artist_methods = [m for m in methods if m in (
                "setRoyalties", "configureDrop", "createNFTCollection", "createToken",
                "registerExtension", "mintSigned", "mintBatch", "mintBaseNew"
            )]
            if artist_methods:
                score += 1; signals.append(f"Artist activity: {', '.join(artist_methods[:3])}")

            # 8. Wash trading flag — high mints + high self-transfers + no sales
            self_tf = nft.get("self_transfers", 0)
            if self_tf > 5 and sales == 0:
                score -= 2; signals.append(f"🚨 {self_tf} self-transfers, no sales (possible wash trading)")

            # 8b. Two-way transfer analysis (collector also sent NFTs back)
            # Check if same token IDs went back and forth (actual wash trading)
            # vs different tokens from same/different collections (normal collector trading)
            collector_addrs = set(nft.get("collector_wallets", []))
            sender_addrs = set(nft.get("sender_wallets", []))
            both_direction = collector_addrs & sender_addrs
            wallet_tokens_data = nft.get("wallet_tokens", {})
            if both_direction:
                for bd_addr in both_direction:
                    is_mkt, mkt_label = is_marketplace_contract(bd_addr)
                    if is_mkt:
                        signals.append(f"  {bd_addr[:12]}... two-way transfer but is {mkt_label} (marketplace escrow, not wash trading)")
                        continue
                    # Check if same token IDs went back and forth
                    wt = wallet_tokens_data.get(bd_addr, {})
                    sent_ids = set(wt.get("sent", []))
                    recv_ids = set(wt.get("received", []))
                    same_tokens = sent_ids & recv_ids
                    
                    # Split by token type: ERC-721 same-ID = likely wash trading, ERC-1155 same-ID = may be normal (fungible)
                    erc721_same = [t for t in same_tokens if "ERC-721" in t]
                    erc1155_same = [t for t in same_tokens if "ERC-1155" in t]
                    
                    is_single, coll_name = is_single_collection_wallet(bd_addr)
                    if erc721_same:
                        score -= 2
                        signals.append(f"🚨 {bd_addr[:12]}... same ERC-721 token(s) round-tripped (wash trading)")
                    elif erc1155_same:
                        signals.append(f"  {bd_addr[:12]}... same ERC-1155 token ID(s) transferred back and forth (may be normal for fungible tokens)")
                    elif is_single:
                        score -= 1
                        signals.append(f"⚠️ {bd_addr[:12]}... sent AND received NFTs, only interacts with {coll_name} (suspicious single-collection wallet)")
                    else:
                        signals.append(f"  {bd_addr[:12]}... two-way transfer with different tokens (collector trading)")

            # 9. List notable collections
            for addr, info in list(nft.get("contracts", {}).items())[:3]:
                if info["name"] != "Unknown":
                    signals.append(f"  Collection: {info['name']} (mints={info['mint']}, sent={info['sent']}, collectors={info['collectors']})")
        else:
            signals.append("No NFT history (new or empty wallet)")

        # Artwork analysis signals
        artwork = p.get("artwork_analysis", [])
        if artwork:
            ai_flags = sum(1 for a in artwork if a.get("ai_analysis", {}).get("is_ai_suspected"))
            if ai_flags > 0:
                score -= 2; signals.append(f"⚠️ AI-suspected artwork ({ai_flags}/{len(artwork)} images)")
            else:
                score += 1; signals.append(f"Artwork checked: {len(artwork)} images, no AI indicators")
            # Show brief Gemini analysis for first image
            first_ai = artwork[0].get("ai_analysis", {})
            if first_ai.get("analysis") and "error" not in first_ai.get("analysis", "").lower():
                signals.append(f"  Art style: {first_ai['analysis'][:80]}")
        if p.get("has_duplicate_artwork"):
            score -= 3; signals.append("🚨 DUPLICATE artwork detected across artists")

        # MemesNominee rep status
        mn_rep = p.get("memes_nominee_rep", 0)
        signals.append(f"MemesNominee rep: {mn_rep:,}")

        if score >= 6:
            p["category"] = "ESTABLISHED"
        elif score >= 4:
            p["category"] = "LIKELY_REAL"
        elif score >= 2:
            p["category"] = "UNCLEAR"
        elif p.get("rep", 0) < 1000:
            p["category"] = "NEW_EMPTY"
        else:
            p["category"] = "SUSPICIOUS"
        p["signals"] = signals
        p["score"] = score

        # Generate overall assessment
        p["assessment"] = generate_assessment(p, nft)

    # 9. Determine who gets rep
    # Rules:
    #   - Must be ESTABLISHED or LIKELY_REAL
    #   - Must NOT have active MS submissions (already passed 50K threshold)
    #   - Must have < 50K MemesNominee rep
    #   - Must NOT be a rep-giver
    #   - Must be seeking nomination (asking for rep OR posting artwork)
    #   - Must not have already received rep from us (dedup)
    rep_given = []
    rep_skipped = []
    rep_failed = []
    proxy_token = None

    rep_notification_text = (
        "You've been given MemesNominee rep to help you reach the 50K threshold for Main Stage submissions. "
        "You're now at {current:,} / 50,000. "
        "Keep posting artwork and engaging with the community. Good luck! \U0001f44a"
    )

    for handle, p in profiles.items():
        if p.get("error"):
            continue
        wallet = p.get("wallet", "")
        if not wallet:
            continue
        if p["category"] not in ("ESTABLISHED", "LIKELY_REAL"):
            continue
        if wallet.lower() in state.get("rep_given", {}):
            continue  # already gave rep

        # Skip MS winners — they've already won, don't need nomination rep
        if p.get("ms_winner_ids"):
            rep_skipped.append({"handle": handle, "reason": "MS winner (already established)"})
            continue

        # Skip if artwork flagged as AI-suspected or duplicate
        if p.get("has_duplicate_artwork"):
            rep_skipped.append({"handle": handle, "reason": "Duplicate artwork detected"})
            continue
        ai_flags = sum(1 for a in p.get("artwork_analysis", []) if a.get("ai_analysis", {}).get("is_ai_suspected"))
        if ai_flags > 0:
            rep_skipped.append({"handle": handle, "reason": f"AI-suspected artwork ({ai_flags} images)"})
            continue

        # Skip if already has >= 50K MemesNominee rep
        mn_rep = p.get("memes_nominee_rep", 0)
        if mn_rep >= MEMES_NOMINEE_THRESHOLD:
            rep_skipped.append({"handle": handle, "reason": f"Already has {mn_rep:,} MemesNominee rep"})
            continue

        # Secondary safety: ONLY if state file is missing or empty.
        # If we have no record of who we've given to, and they already have
        # >= our amount, they likely already got rep from us. Skip to avoid loops.
        # But if state file exists and they're NOT in it, they got rep from others — give them ours.
        state_rep_given = state.get("rep_given", {})
        if not state_rep_given and mn_rep >= REP_AMOUNT:
            rep_skipped.append({"handle": handle, "reason": f"State file empty and already has {mn_rep:,} MemesNominee rep (likely already given by us)"})
            continue

        # CRITICAL: bulk-rep API OVERWRITES, not adds.
        # If someone already has MemesNominee rep (from RD or others), we must
        # send (current + amount) to avoid destroying their existing rep.
        # See incident 2026-07-07: Gsen/Papillon/johndoe8891 had rep overwritten.
        rep_to_send = mn_rep + REP_AMOUNT
        if mn_rep > 0:
            print(f"  NOTE: @{handle} already has {mn_rep:,} MemesNominee rep — sending {rep_to_send:,} to preserve existing")

        # Skip if they're a rep-giver, not a seeker
        if p.get("is_rep_giver"):
            rep_skipped.append({"handle": handle, "reason": "Rep-giver, not seeking nomination"})
            continue

        # Skip if not seeking nomination (no artwork, no rep requests)
        if not p.get("is_seeking"):
            rep_skipped.append({"handle": handle, "reason": "Not seeking nomination (GMeme-only, no artwork)"})
            continue

        # Get proxy token lazily
        if proxy_token is None:
            print("Getting proxy token for rep assignment...")
            try:
                proxy_token = get_proxy_token()
            except Exception as e:
                print(f"ERROR getting proxy token: {e}")
                rep_failed.append({"handle": handle, "error": str(e)})
                break

        print(f"  Giving {rep_to_send:,} rep to @{handle} ({p['category']}, currently {mn_rep:,} MemesNominee rep)...")
        success, error = assign_rep(proxy_token, wallet, rep_to_send, REP_CATEGORY)
        if success:
            state.setdefault("rep_given", {})[wallet.lower()] = {
                "handle": handle,
                "category": p["category"],
                "date": time.strftime("%Y-%m-%d"),
                "amount": rep_to_send,
                "prior_rep": mn_rep,
            }
            rep_given.append({"handle": handle, "wallet": wallet, "category": p["category"], "prior_rep": mn_rep, "sent": rep_to_send})
            print(f"    OK (was {mn_rep:,}, now ~{rep_to_send:,})")

            # Post notification reply
            posts = author_posts.get(handle, [])
            if posts:
                target_drop_id = posts[-1]["drop_id"]
                notif_text = rep_notification_text.format(current=rep_to_send)
                body = {
                    "wave_id": SEEKING_NOMINATION_WAVE,
                    "parts": [{"content": notif_text}],
                    "reply_to": {"drop_id": target_drop_id, "drop_part_id": 1},
                }
                print(f"    Posting notification reply...")
                n_success, n_result, n_error = audited_post_drop(
                    token, SEEKING_NOMINATION_WAVE, body, source="seeking_nomination_vetting")
                if n_success:
                    print(f"    Notification posted (drop #{n_result.get('serial_no', '?')})")
                else:
                    print(f"    Notification FAILED: {n_error}")
        else:
            rep_failed.append({"handle": handle, "error": error})
            print(f"    FAILED: {error}")

    # 10. Post replies to UNCLEAR/SUSPICIOUS/NEW_EMPTY (once per handle)
    replies_posted = []
    replies_failed = []

    reply_text = (
        "Welcome to the Seeking Nomination wave! \U0001f30a\n\n"
        "I'm an automated scanner checking if artists are real. "
        "I couldn't find enough signals to verify you yet. To help me confirm you're a genuine artist:\n\n"
        "1. **Link your socials** \u2014 Post your Twitter/X, Instagram, or other art portfolio links\n"
        "2. **Post artwork samples** \u2014 Share images of your work in your profile wave or here\n"
        "3. **Tell us about your art** \u2014 What kind of artist are you? What's your medium?\n\n"
        "Once I can verify your social presence and see your artwork, you'll receive MemesNominee rep "
        "to help you reach the 50K threshold for Main Stage submissions."
    )

    for handle, p in profiles.items():
        if p.get("error"):
            continue
        if p["category"] not in ("UNCLEAR", "SUSPICIOUS", "NEW_EMPTY"):
            continue
        if handle.lower() in state.get("replies_posted", {}):
            continue

        # Skip rep-givers — they don't need a "verify yourself" message
        if p.get("is_rep_giver"):
            continue

        posts = author_posts.get(handle, [])
        if not posts:
            continue
        target_drop_id = posts[-1]["drop_id"]

        print(f"  Posting reply to @{handle} ({p['category']})...")
        body = {
            "wave_id": SEEKING_NOMINATION_WAVE,
            "parts": [{"content": reply_text}],
            "reply_to": {"drop_id": target_drop_id, "drop_part_id": 1},
        }
        success, result, error = audited_post_drop(token, SEEKING_NOMINATION_WAVE, body, source="seeking_nomination_vetting")
        if success:
            state.setdefault("replies_posted", {})[handle.lower()] = {
                "drop_id": target_drop_id,
                "category": p["category"],
                "date": time.strftime("%Y-%m-%d")
            }
            replies_posted.append({"handle": handle, "category": p["category"], "replied_to": target_drop_id})
            print(f"    OK (drop #{result.get('serial_no', '?')})")
        else:
            replies_failed.append({"handle": handle, "error": str(error)})
            print(f"    FAILED: {error}")

    # 11. Save state
    save_state(state)

    # 12. Output summary
    summary = {
        "total_authors": len(profiles),
        "categories": {},
        "rep_given": rep_given,
        "rep_skipped": rep_skipped,
        "rep_failed": rep_failed,
        "replies_posted": replies_posted,
        "replies_failed": replies_failed,
        "already_vetted": len(state.get("rep_given", {})),
    }
    for cat in ["ESTABLISHED", "LIKELY_REAL", "UNCLEAR", "SUSPICIOUS", "NEW_EMPTY"]:
        summary["categories"][cat] = [
            {"handle": h, "signals": p.get("signals", []),
             "memes_nominee_rep": p.get("memes_nominee_rep", 0),
             "is_rep_giver": p.get("is_rep_giver", False),
             "is_seeking": p.get("is_seeking", False)}
            for h, p in profiles.items() if p.get("category") == cat and not p.get("error")
        ]

    print("\n" + json.dumps(summary, indent=2))
    print("\nVETTING_COMPLETE:" + json.dumps(summary))


if __name__ == "__main__":
    main()