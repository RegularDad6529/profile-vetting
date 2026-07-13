#!/usr/bin/env python3
import json, urllib.request, time, re, sys, unicodedata, os
from collections import Counter

sys.path.insert(0, "/home/prenode/.hermes/profiles/themanager/scripts")
from seeking_nomination_vetting import (
    api_get, get_cic_statements, get_nft_history_multichain,
    get_artwork_from_minted_collections, analyze_artwork,
    is_marketplace_contract, load_token
)

TOKEN = load_token()
BASE = "https://api.6529.io/api"

handle = sys.argv[1] if len(sys.argv) > 1 else "EMOJI"

print(f"=== Assessment: @{handle} ===\n")

# 1. Profile
print("--- 1. 6529 Profile ---")
# Get profile data - try both endpoints
p_raw = api_get(f"/profiles/{handle}", TOKEN)

# The profiles endpoint returns nested: {profile: {...}, consolidation: {...}, ...}
profile_data = p_raw.get("profile", p_raw)
wallet = p_raw.get("consolidation", {}).get("wallet", "")
consolidation = p_raw.get("consolidation", {})

primary_wallet = wallet or profile_data.get("wallet", "")
all_wallets = []

# Try identities endpoint for consolidated wallets
try:
    ident = api_get(f"/identities/{handle}", TOKEN)
    ident_wallets = ident.get("wallets", [])
    for w in ident_wallets:
        if isinstance(w, dict):
            all_wallets.append(w.get("wallet", w.get("address", "")))
        elif isinstance(w, str):
            all_wallets.append(w)
except:
    pass

if not all_wallets and primary_wallet:
    all_wallets = [primary_wallet]
all_wallets = [w for w in all_wallets if w]

rep = profile_data.get("rep", 0) or p_raw.get("rep", 0)
tdh = profile_data.get("tdh", 0) or p_raw.get("tdh", 0) or consolidation.get("tdh", 0)
xtdh = profile_data.get("xtdh", 0) or p_raw.get("xtdh", 0)
level = profile_data.get("level", 0) or p_raw.get("level", 0)
cic = p_raw.get("cic", {}) or profile_data.get("cic", {})
profile_id = profile_data.get("id", "")

print(f"Handle: @{handle}")
print(f"Wallet: {primary_wallet}")
print(f"Wallets (consolidated): {len(all_wallets)}")
for w in all_wallets:
    print(f"  {w}")
cic_str = f"rating={cic.get('cic_rating', '?')}, contributors={cic.get('contributor_count', '?')}" if isinstance(cic, dict) else str(cic)
print(f"Rep: {rep:,} | TDH: {tdh:,} | xTDH: {xtdh:,} | Level: {level} | CIC: {cic_str}")
print(f"Profile ID: {profile_id}")

# 2. Post activity — fetch from Seeking Nomination wave and filter by author
print("\n--- 2. Post Activity ---")
import re as _re
with open(f"/home/prenode/.hermes/profiles/themanager/scripts/seeking_nomination_vetting.py") as _f:
    _m = _re.search(r'SEEKING_NOMINATION_WAVE\s*=\s*"([^"]+)"', _f.read())
    SN_WAVE = _m.group(1) if _m else "0ecb95d0-d8f2-48e8-8137-bfa71ee8593c"

posts = []
try:
    wave_data = api_get(f"/v2/waves/{SN_WAVE}/drops?limit=200", TOKEN)
    all_drops = wave_data.get("drops", wave_data.get("data", []))
    # Filter to this author only
    posts = [d for d in all_drops if (d.get("author") or {}).get("handle", "").lower() == handle.lower()]
except:
    pass

# Also fetch from profile wave if available
ident_data = api_get(f"/identities/{handle}", TOKEN)
pwid = ident_data.get("profile_wave_id", "")
if pwid:
    try:
        pw_data = api_get(f"/v2/waves/{pwid}/drops?limit=200", TOKEN)
        pw_drops = pw_data.get("drops", pw_data.get("data", []))
        posts.extend(pw_drops)
    except:
        pass

print(f"Posts (SN + profile wave): {len(posts)}")

# Count reactions (drops use "reactions" field)
reactions = 0
for p in posts:
    reacts = p.get("reactions", [])
    if isinstance(reacts, list):
        reactions += len(reacts)
print(f"Reactions received: {reactions}")

# Wave distribution
waves = Counter()
for p in posts:
    w = p.get("wave", {})
    waves[w.get("name", "unknown")] += 1
if waves:
    print(f"Most active waves: {waves.most_common(5)}")

# SN posts — since we fetched from SN wave, posts without profile_wave are SN
sn_posts = [p for p in posts if not p.get("wave", {}).get("name", "").lower().startswith("profile")]
print(f"Seeking Nomination posts: {len(sn_posts)}")
media_posts = [p for p in sn_posts if p.get("media", [])]
print(f"SN posts with media: {len(media_posts)}")

# 3. Profile wave
profile_wave = [p for p in posts if "profile" in (p.get("wave", {}).get("name", "")).lower()]
print(f"\n--- 3. Profile Wave ---")
print(f"Profile wave posts: {len(profile_wave)}")

# 4. Social links
print(f"\n--- 4. Social Links ---")
cic = get_cic_statements(handle, TOKEN)
if cic:
    bio = cic.pop("bio", None)
    print(f"Bio: {bio or 'None'}")
    for platform, val in cic.items():
        if val:
            print(f"  {platform}: {val}")
    if not any(cic.values()):
        print("  (No social links found)")
else:
    print("No CIC statements found")

# 5. NFT On-Chain History (multichain)
print(f"\n--- 5. NFT On-Chain History (Multichain) ---")
merged_nft = None
for wi, w in enumerate(all_wallets):
    print(f"\nFetching multichain NFT history for wallet {wi+1}/{len(all_wallets)}: {w[:20]}...")
    nft = get_nft_history_multichain(w, max_pages=10)
    if nft:
        if merged_nft is None:
            merged_nft = nft
        else:
            # Merge second wallet's results into first
            for k in ["total_nft_transfers", "mints", "burns", "sent_to_others", "received_from_others",
                       "sales_count", "verified_sales", "exchange_sales", "deployed_contracts", "nft_purchases"]:
                merged_nft[k] = merged_nft.get(k, 0) + nft.get(k, 0)
            merged_nft["exchange_eth"] = round(merged_nft.get("exchange_eth", 0) + nft.get("exchange_eth", 0), 4)
            merged_nft["verified_eth"] = round(merged_nft.get("verified_eth", 0) + nft.get("verified_eth", 0), 4)
            merged_nft["eth_received"] = round(merged_nft.get("eth_received", 0) + nft.get("eth_received", 0), 4)
            merged_nft["eth_sent"] = round(merged_nft.get("eth_sent", 0) + nft.get("eth_sent", 0), 4)
            merged_nft["collector_wallets"] = list(set(merged_nft.get("collector_wallets", []) + nft.get("collector_wallets", [])))
            merged_nft["sender_wallets"] = list(set(merged_nft.get("sender_wallets", []) + nft.get("sender_wallets", [])))
            merged_nft["raw_transfers"] = merged_nft.get("raw_transfers", []) + nft.get("raw_transfers", [])
            merged_nft["sale_sources"] = merged_nft.get("sale_sources", []) + nft.get("sale_sources", [])
            for c_addr, c_info in nft.get("contracts", {}).items():
                if c_addr in merged_nft.get("contracts", {}):
                    for kk in ["mint", "sent", "recv", "burn"]:
                        merged_nft["contracts"][c_addr][kk] = merged_nft["contracts"][c_addr].get(kk, 0) + c_info.get(kk, 0)
                else:
                    merged_nft.setdefault("contracts", {})[c_addr] = c_info
            for cat, items in nft.get("artist_activities", {}).items():
                merged_nft.setdefault("artist_activities", {}).setdefault(cat, []).extend(items)
            for ck, cv in nft.get("per_chain", {}).items():
                merged_nft.setdefault("per_chain", {})[ck] = cv
            if nft.get("wallet_age_days", 0) > merged_nft.get("wallet_age_days", 0):
                merged_nft["wallet_age_days"] = nft["wallet_age_days"]
                merged_nft["first_transfer"] = nft.get("first_transfer", "")
    time.sleep(0.5)

# Update counts after merge
if merged_nft:
    merged_nft["unique_collectors"] = len(merged_nft.get("collector_wallets", []))
    merged_nft["unique_senders"] = len(merged_nft.get("sender_wallets", []))
    merged_nft["unique_nft_contracts"] = len(merged_nft.get("contracts", {}))

if merged_nft:
    print(f"\nCombined stats:")
    print(f"  Total NFT transfers: {merged_nft.get('total_nft_transfers', 0)}")
    print(f"  Mints: {merged_nft.get('mints', 0)}")
    print(f"  Sales (NFT-verified): {merged_nft.get('sales_count', 0)}")
    print(f"  Verified sales: {merged_nft.get('verified_sales', 0)} ({merged_nft.get('verified_eth', 0):.4f} ETH)")
    print(f"  Exchange sales: {merged_nft.get('exchange_sales', 0)} ({merged_nft.get('exchange_eth', 0):.4f} ETH)")
    print(f"  Total ETH received: {merged_nft.get('eth_received', 0):.4f}")
    print(f"  Unique collectors: {merged_nft.get('unique_collectors', 0)}")
    print(f"  Deployed contracts: {merged_nft.get('deployed_contracts', 0)}")
    print(f"  Wallet age: {merged_nft.get('wallet_age_days', 0)} days")

    per_chain = merged_nft.get("per_chain", {})
    if per_chain:
        print(f"\n  Per-chain:")
        for chain, data in per_chain.items():
            print(f"    {chain}: {data.get('transfers', 0)} transfers, {data.get('mints', 0)} mints, {data.get('sales', 0)} sales")

    contracts = merged_nft.get("contracts", {})
    if contracts:
        print(f"\n  Collections ({len(contracts)}):")
        for addr, info in sorted(contracts.items(), key=lambda x: x[1].get("mint", 0) if isinstance(x[1], dict) else 0, reverse=True)[:10]:
            if isinstance(info, dict):
                coll = info.get("collectors", set())
                coll_count = len(coll) if isinstance(coll, (set, list)) else coll
                print(f"    {info.get('name', '?')}: {info.get('mint', 0)} mints, {info.get('sent', 0)} sent, {coll_count} collectors")

    activities = merged_nft.get("artist_activities", {})
    if activities:
        print(f"\n  Artist activities:")
        for cat, items in activities.items():
            if items:
                print(f"    {cat}: {len(items)} ({Counter(items).most_common(3)})")

    print(f"\n  Sale sources (NFT-verified):")
    for s in merged_nft.get("sale_sources", []):
        if s.get("nft_transfer"):
            is_mkt, mkt_name = is_marketplace_contract(s["from"])
            tag = f"marketplace: {mkt_name}" if is_mkt else "direct buyer"
            print(f"    {s['date']} | {s['eth']:.4f} ETH | {tag} | from: {s['from'][:20]}")

    non_sales = [s for s in merged_nft.get("sale_sources", []) if not s.get("nft_transfer")]
    if non_sales:
        print(f"\n  Non-sale ETH transfers: {len(non_sales)}")
        for s in non_sales[:5]:
            print(f"    {s['date']} | {s['eth']:.4f} ETH | from: {s['from'][:20]}")
        if len(non_sales) > 5:
            print(f"    ... and {len(non_sales)-5} more")

    # Wallet overlap - use collector_wallets list
    print(f"\n  Wallet overlap analysis:")
    wl = primary_wallet.lower()
    collector_list = merged_nft.get("collector_wallets", [])
    for collector in collector_list:
        is_mkt, _ = is_marketplace_contract(collector)
        if is_mkt:
            continue
        sent_nfts = sum(1 for t in merged_nft.get("raw_transfers", [])
                       if (t.get("from") or {}).get("hash", "").lower() == collector
                       and (t.get("to") or {}).get("hash", "").lower() == wl)
        if sent_nfts > 0:
            recv_nfts = sum(1 for t in merged_nft.get("raw_transfers", [])
                           if (t.get("to") or {}).get("hash", "").lower() == collector
                           and (t.get("from") or {}).get("hash", "").lower() == wl)
            print(f"    {collector[:20]}: recv={recv_nfts} NFTs, sent_back={sent_nfts} NFTs (ROUND-TRIP)")

    # Collectors with 6529 profiles
    print(f"\n  Collector 6529 profiles:")
    for collector in collector_list[:15]:
        is_mkt, mkt_name = is_marketplace_contract(collector)
        if is_mkt:
            print(f"    {collector[:20]}: marketplace ({mkt_name})")
            continue
        try:
            ident = api_get(f"/identities/{collector}", TOKEN)
            h = ident.get("handle", "")
            if h and not h.startswith("id-"):
                prof = api_get(f"/profiles/{h}", TOKEN)
                prof_data = prof.get("profile", prof)
                lvl = prof_data.get("level", 0)
                rep = prof_data.get("rep", 0)
                print(f"    {collector[:20]}: @{h} (L{lvl}, rep {rep:,})")
            else:
                print(f"    {collector[:20]}: no 6529 profile")
        except:
            print(f"    {collector[:20]}: no 6529 profile")
        time.sleep(0.2)
else:
    print("No NFT history found")

# 6. Artwork analysis
print(f"\n--- 6. Artwork Analysis ---")
if merged_nft:
    artworks = get_artwork_from_minted_collections(primary_wallet, merged_nft, max_images=3, all_wallets=all_wallets)
    if artworks:
        for aw in artworks:
            print(f"\n  Artwork: {aw.get('name', '?')}")
            print(f"  Collection: {aw.get('collection', '?')}")
            print(f"  Token ID: {aw.get('token_id', '?')}")
            print(f"  Image URL: {aw.get('image_url', '?')[:80]}")
            analysis = analyze_artwork(aw.get("image_url", ""))
            if analysis:
                print(f"  AI: {analysis.get('ai', '?')}")
                print(f"  Description: {analysis.get('description', '?')[:200]}")
            else:
                print(f"  Analysis failed")
    else:
        print("No on-chain artwork found")

# 7. Rep — try identities endpoint which has rep breakdown
print(f"\n--- 7. Rep Received ---")
rep_cats = []
try:
    # Try the rep categories endpoint
    rep_data = api_get(f"/profiles/{handle}/rep-categories", TOKEN)
    if isinstance(rep_data, dict):
        rep_cats = rep_data.get("items", rep_data.get("data", rep_data.get("categories", [])))
    elif isinstance(rep_data, list):
        rep_cats = rep_data
except:
    pass

if not rep_cats:
    # Fallback: use identity data we already have
    print(f"  Total rep from identity: {rep:,}")
    print(f"  (Detailed rep breakdown not available from API)")
else:
    total_rep = sum(r.get("rep", 0) for r in rep_cats)
    print(f"Total rep: {total_rep:,}")
    for r in rep_cats[:10]:
        cat = r.get("category", "?")
        cat_rep = r.get("rep", 0)
        givers = r.get("givers", [])
        giver_str = ", ".join([f"@{g.get('handle', '?')} (L{g.get('level', 0)}) {g.get('rep', 0)//1000}K" for g in givers[:3]])
        print(f"  {cat}: {cat_rep:,} — {giver_str}")

print("\n=== DONE ===")