#!/usr/bin/env python3
"""
Fetch artist creation data for a 6529 profile:
- MS win drop details (title, description, raters, rating)
- Deployed contracts (verified via creator_address_hash)
- Foundation sales breakdown (own-art vs collector flips vs buybacks)

Usage: python3 fetch_artist_creations.py <HANDLE> [HANDLE2 ...]
Example: python3 fetch_artist_creations.py hugofaz casanua

Prerequisites:
- 6529 token at /home/prenode/.hermes/profiles/themanager/6529_tokens.json
- Outputs JSON to stdout

Key lessons (see pitfalls #53-58):
- Blockscout v2 pagination uses next_page_params DICT, not cursor
- Token fields: token.address_hash, total.token_id, token_type at top level
- contract-creations endpoint returns 400 — use /addresses/{contract} + creator_address_hash
- Foundation has multiple contract addresses — check all three
"""
import json, urllib.request, urllib.parse, time, sys

with open("/home/prenode/.hermes/profiles/themanager/6529_tokens.json") as f:
    TOKEN = json.load(f)["token"]

API_6529 = "https://api.6529.io/api"
BLOCKSCOUT = "https://eth.blockscout.com/api/v2"

# Foundation contracts (pitfall #55)
FOUNDATION_CONTRACTS = {
    "0xcda72070e455bb31c7690a170224ce43623d0b6f",  # NFT transfer proxy
    "0xcda72070e454bb84c756f75bb72993fbe416b69b",  # v1 admin proxy
    "0x3b3ee1931dc30f20ffa2df07f88f93c1b0b94fc0",  # v2
}

def api_get_6529(path):
    url = f"{API_6529}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def blockscout_get(path):
    url = f"{BLOCKSCOUT}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def fetch_all_transfers(addr):
    """Fetch all NFT transfers with correct pagination (pitfall #53)."""
    results = []
    page_params = None
    pages = 0
    while True:
        url = f"{BLOCKSCOUT}/addresses/{addr}/token-transfers"
        if page_params:
            url += "?" + urllib.parse.urlencode(page_params)
        try:
            data = blockscout_get(url.replace(BLOCKSCOUT, ""))
            # Actually build URL properly
            req_url = f"{BLOCKSCOUT}/addresses/{addr}/token-transfers"
            if page_params:
                req_url += "?" + urllib.parse.urlencode(page_params)
            req = urllib.request.Request(req_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            data = json.loads(urllib.request.urlopen(req, timeout=30).read())
            items = data.get("items", [])
            for t in items:
                token = t.get("token", {})
                total = t.get("total", {})
                token_type = t.get("token_type", "")
                if token_type not in ("ERC-721", "ERC-1155"):
                    continue
                results.append({
                    "contract": token.get("address_hash", ""),
                    "name": token.get("name", ""),
                    "symbol": token.get("symbol", ""),
                    "type": token_type,
                    "token_id": str(total.get("token_id", "")),
                    "from": t.get("from", {}).get("hash", "") if isinstance(t.get("from"), dict) else "",
                    "to": t.get("to", {}).get("hash", "") if isinstance(t.get("to"), dict) else "",
                    "timestamp": t.get("timestamp", ""),
                })
            page_params = data.get("next_page_params")
            pages += 1
            if not page_params or not items or pages > 100:
                break
            time.sleep(0.2)
        except Exception as e:
            print(f"  Error page {pages}: {e}", file=sys.stderr)
            break
    return results

def get_ms_win_details(drop_id):
    """Fetch MS win drop details including description and ratings."""
    d = api_get_6529(f"/drops/{drop_id}")
    metadata = d.get("metadata", [])
    description = ""
    for m in metadata:
        if m.get("data_key") == "description":
            description = m.get("data_value", "")
            break
    parts = d.get("parts", [])
    if parts and not description:
        description = parts[0].get("content", "")
    return {
        "title": d.get("title", ""),
        "description": description[:500],
        "raters_count": d.get("raters_count", 0),
        "rating": d.get("rating", 0),
        "serial_no": d.get("serial_no", 0),
        "winning_place": d.get("winning_context", {}).get("place", 0),
        "is_additional_action_promised": d.get("is_additional_action_promised", False),
    }

def find_deployed_contracts(wallets, all_transfers):
    """Find contracts deployed by profile wallets (pitfall #58)."""
    wallet_set = {w.lower() for w in wallets}
    minted_contracts = set()
    for t in all_transfers:
        if t["from"].lower() == "0x0000000000000000000000000000000000000000":
            minted_contracts.add(t["contract"])
    
    own = []
    for contract in minted_contracts:
        try:
            data = blockscout_get(f"/addresses/{contract}")
            creator = data.get("creator_address_hash", "")
            token = data.get("token", {})
            if creator.lower() in wallet_set:
                mint_count = sum(1 for t in all_transfers if t["contract"] == contract and t["from"].lower() == "0x0000000000000000000000000000000000000000")
                sold_count = sum(1 for t in all_transfers if t["contract"] == contract and t["from"].lower() in wallet_set and t["to"].lower() not in wallet_set and t["to"].lower() != "0x0000000000000000000000000000000000000000")
                own.append({
                    "name": token.get("name", ""),
                    "symbol": token.get("symbol", ""),
                    "type": token.get("type", ""),
                    "contract": contract,
                    "holders": token.get("holders_count", 0),
                    "mints": mint_count,
                    "sold": sold_count,
                    "creator": creator,
                })
            time.sleep(0.15)
        except:
            pass
    return own

def categorize_foundation(all_transfers, own_contract_names):
    """Categorize Foundation transfers as own-art, collector flips, or buybacks."""
    own_names_lower = {n.lower() for n in own_contract_names if n}
    
    sells = [t for t in all_transfers if t["to"].lower() in FOUNDATION_CONTRACTS]
    buys = [t for t in all_transfers if t["from"].lower() in FOUNDATION_CONTRACTS]
    
    own_sells = [t for t in sells if t["name"].lower() in own_names_lower]
    flip_sells = [t for t in sells if t["name"].lower() not in own_names_lower]
    own_buys = [t for t in buys if t["name"].lower() in own_names_lower]
    other_buys = [t for t in buys if t["name"].lower() not in own_names_lower]
    
    return {
        "own_art_sold": len(own_sells),
        "collector_flips_sold": len(flip_sells),
        "own_art_buybacks": len(own_buys),
        "other_artists_collected": len(other_buys),
        "total_sold": len(sells),
        "total_bought": len(buys),
    }

# Main
handles = sys.argv[1:] or ["hugofaz"]
results = {}

for handle in handles:
    print(f"Processing {handle}...", file=sys.stderr)
    profile = api_get_6529(f"/identities/{handle}")
    
    # Get MS wins
    ms_ids = profile.get("winner_main_stage_drop_ids", [])
    ms_wins = [get_ms_win_details(did) for did in ms_ids]
    
    # Get meme cards
    meme_cards = profile.get("artist_of_prevote_cards", [])
    
    # Get all wallets
    wallets = [w.get("wallet", w.get("address_hash", "")) if isinstance(w, dict) else w for w in profile.get("wallets", [])]
    wallets = [w for w in wallets if w]
    wallet_set = {w.lower() for w in wallets}
    
    # Fetch all transfers
    all_transfers = []
    for addr in wallets:
        all_transfers.extend(fetch_all_transfers(addr))
    
    # Find deployed contracts
    own_contracts = find_deployed_contracts(wallets, all_transfers)
    own_names = [c["name"] for c in own_contracts if c["name"]]
    
    # Categorize Foundation
    foundation = categorize_foundation(all_transfers, own_names)
    
    results[handle] = {
        "level": profile.get("level"),
        "rep": profile.get("rep"),
        "tdh": profile.get("tdh"),
        "classification": profile.get("classification"),
        "ms_wins": ms_wins,
        "meme_cards": meme_cards,
        "wallets": wallets,
        "deployed_contracts": own_contracts,
        "foundation_breakdown": foundation,
        "total_nft_transfers": len(all_transfers),
    }

print(json.dumps(results, indent=2, default=str))