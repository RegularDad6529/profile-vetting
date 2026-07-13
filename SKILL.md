---
name: 6529-artist-vetting
description: Vet artists on the 6529 Seeking Nomination wave — fetch profile, socials, on-chain NFT history (multichain), artwork, and produce a complete assessment with SUSPICIOUS/LIKELY_REAL/ESTABLISHED classification.
---

# 6529 Artist Vetting

Vetting process for artists on the 6529 Seeking Nomination wave. Produces a complete assessment covering profile data, social links, on-chain NFT history (multichain), artwork analysis, and rep received.

## Runner Script

Location: `scripts/run_assessment.py` (in themanager profile dir)
Vetting library: `scripts/seeking_nomination_vetting.py`

Run: `python3 scripts/run_assessment.py <HANDLE>`

## Assessment Sections (in order)

### 1. 6529 Profile
- Fetch from `GET /identities/{handle}` (NOT `/profiles/{handle}` — that returns nested objects)
- Extract: handle, primary_wallet, wallets array, rep, level, tdh, xtdh, cic, profile_wave_id

### 2. Post Activity
- Fetch from `GET /v2/waves/{SEEKING_NOMINATION_WAVE}/drops?limit=200`
- Filter drops by `author.handle` matching the target handle (case-insensitive)
- Also fetch from profile wave if `profile_wave_id` exists: `GET /v2/waves/{profile_wave_id}/drops?limit=200`
- Count: total posts, reactions received, SN posts, posts with media
- SN_WAVE ID: `0ecb95d0-d8f2-48e8-8137-bfa71ee8593c`

### 2b. Community Wave Engagement (MANDATORY — DO NOT SKIP)
**PITFALL (2026-07-13)**: In the @kiramoto assessment, I reported "zero 6529 engagement" based on 0 SN posts and no profile wave. This was WRONG — kiramoto was actively posting in maybe's dive bar (~20 messages on his first day, recognized by existing collectors). Reporting "zero engagement" when the artist is actively participating in a community wave is a significant false negative.

**Always check these community waves for the artist's activity:**
- **Maybe's dive bar** (`b38288e6-ca9d-45ce-8323-3dc5e094f04e`): `GET /waves/{wave_id}/drops?limit=200` — filter by author handle. This is where new and returning members introduce themselves and build community. Many newcomers post here before submitting to SN.
- **Meme Club** (`d23af421-203d-4e37-abc1-4d9df840026c`): Check for participation, voting, submissions.
- **Karen Army**: Check if the artist is a wave subscriber (indicates community commitment).

**For each community wave, report:**
- Number of posts by the artist
- Content summary (what they're posting about — introductions, art discussion, community engagement)
- Whether existing community members recognized/welcomed them (strong signal for returning artists)
- Any mentions of their artwork, collectors, or prior art scene activity

**Context from community wave posts can reveal:**
- Personal background (location, family, health) that humanizes the profile
- How they found 6529 ("pointed by some folks")
- Prior art scene activity not visible on-chain ("was in the art scene since 2022")
- Existing relationships with 6529 members (collectors, collaborators)
- Self-described art style and influences

### 3. Profile Wave
- Posts from the user's profile wave (if profile_wave_id exists)

### 4. Social Links
- Fetch from `GET /profiles/{handle}/cic/statements`
- Returns a LIST of statement objects, NOT a dict
- Each statement: `statement_type` (X, BIO, OPENSEA, SUPER_RARE, FOUNDATION, MANIFOLD, INSTAGRAM, etc.) and `statement_value`
- `get_cic_statements()` returns a flat dict: `{"bio": "...", "x": "https://...", "opensea": "..."}`
- **BUG FIXED**: Do NOT look for `cic.get("socials", {})` — the function returns flat keys directly
- Display: pop "bio" first, then iterate remaining keys for social platforms

### 5. NFT On-Chain History (Multichain)
- Scan 6 chains: Ethereum, Base, Polygon, Arbitrum, Optimism, Zora
- Blockscout API instances per chain (see vetting script for URLs)
- For each consolidated wallet, call `get_nft_history_multichain(wallet, max_pages=10)`
- Merge results across multiple wallets
- **Sales detection (CRITICAL FIX)**:
  - Only count ETH as a "sale" if the sender is a marketplace contract OR the sender wallet received an NFT from the artist
  - Pure ETH transfers between wallets with no NFT movement are NOT sales (prevents circular wash trading false positives)
  - Check `is_marketplace_contract(sender)` for marketplace payouts
  - Check if sender is in `nft_recipients` set (wallets that received NFTs from artist)
- **Internal transactions**: Fetch via Blockscout v1 API `?module=account&action=txlistinternal` — marketplace payouts (TL Auction House, Foundation, OpenSea) come as internal txs, not regular txs. Without these, real sales are missed.
- **L2 activity is weaker signal than L1** — note but don't count as strength
- Report: total transfers, mints, sales (NFT-verified), verified ETH, unique collectors, deployed contracts, wallet age
- Per-chain breakdown
- Collection list with mint/sent/collector counts
- Artist activities (deployed_contract, sold_on_marketplace, listed_on_marketplace, minted_on_platform, configured_drop)
- Sale sources with date, ETH amount, marketplace name, sender address
- Non-sale ETH transfers (correctly excluded)

### 6. Artwork Analysis
- `get_artwork_from_minted_collections()` fetches on-chain artwork from artist's own collections
- Uses IPFS gateways: dweb.link, cloudflare-ipfs.com, gateway.pinata.cloud (ipfs.io returns 403)
- `analyze_artwork()` checks if artwork is AI-generated using Gemini API
- Priority: 1) On-chain minted artwork, 2) Profile wave media, 3) SN post media
- Skip obvious spam tokens (cakesv4.finance etc.)

### 7. Rep Received
- Try `GET /profiles/{handle}/rep-categories` for detailed breakdown
- Fallback: use total rep from identity data

## Assessment Classification

- **ESTABLISHED**: Strong on-chain sales history (many sales, reasonable ETH amounts), deployed contracts, verified socials, original artwork, active community
- **LIKELY_REAL**: Some sales, real artwork, social links present, but concerns exist (low sales volume, few collectors, etc.)
- **UNCLEAR**: Mixed signals, insufficient data
- **NEW**: New account with no track record
- **SUSPICIOUS**: Fake sales (circular ETH), self-buying with circular ETH flow, AI art without disclosure, no socials, wash trading
- **BORDERLINE**: Real person with genuine socials/artwork but credentials significantly inflated by deceptive platform dynamics (brand-mimicking contract names, operator-funded micro-sales presented as marketplace traction). Not suspicious enough to flag as sybil, but not strong enough for LIKELY_REAL.
- **Collector profile is NOT suspicious by itself** — collectors transitioning to creation are valid Seeking Nomination candidates. Only flag specific deceptive patterns, not the collector nature of the profile.
- **Low sales ≠ suspicious** — an artist who hasn't found market traction but has real socials, real artwork, and no deceptive patterns is UNCLEAR, not SUSPICIOUS.
- **Network context overrides individual assessment** — a profile that looks LIKELY_REAL in isolation (real socials, own contracts, marketplace sales) must be upgraded to SUSPICIOUS if found to be part of a coordinated multi-profile network (simultaneous creation, shared buyer, wash-trading cycles). See "Shared Contract Network Detection" below.

## Key Rules

- **Bot assessment**: Just state "Appears human" — do NOT explain why
- **Wallet age ≠ authenticity**: People can create wallets for deceptive reasons. Real signals: verified socials, hand-made artwork, sales to distinct verifiable buyers, collector quality, organic patterns
- **Long wallet age + low sales = concern** (not neutral)
- **L2 activity**: Note but don't count as strength. L1 Ethereum mainnet is primary
- **ERC-1155 same token ID round-tripping**: Track but do NOT assume wash trading (no penalty). ERC-721 same-token round-tripping = wash trading (-2)
- **NFT ownership ≠ purchase**: Many NFTs are airdropped
- **Sales must be NFT-verified**: ETH payment + NFT transfer to same buyer. Pure ETH transfers = not a sale.
- **Contract-routed ETH = sales**: ETH payments routed through the artist's own contracts (e.g., SuperRarer, Manifold ERC1155LazyPayableClaim) or platform contracts ARE sales — the contract forwards sale proceeds to the artist when a buyer purchases. Do NOT exclude these. Only exclude exchange hot wallet withdrawals (Binance/Coinbase) as non-sales. For other EOAs sending ETH with no NFT transfer, investigate the relationship (could be commission, gift, or off-platform purchase).
- **External collectors = neutral**: Collectors outside 6529 are neither a strength nor a concern — they are neutral and "something to consider." The artist could potentially bring them into 6529, but this is speculative. Do not frame as positive or negative.
- **Micro-transactions** (<0.001 ETH avg) = suspicious
- **Rep concentration**: >70% from 1-2 givers = weaker
- **Remove "artist keyword" check** from analysis
- **Artwork**: use on-chain artwork from artist's own collections, not collected NFTs

## Common Bugs Fixed

1. **Social links not showing**: `get_cic_statements()` returns flat dict, not nested under "socials". Access keys directly — do NOT look for `cic.get("socials", {})`.
2. **False sales from circular ETH**: Only count ETH as sale if marketplace contract or NFT recipient. BITUA had 24 fake "sales" from circular micro-transfers.
3. **Missing marketplace payouts**: Internal transactions (txlistinternal) needed for TL Auction House, Foundation, OpenSea payouts. Without them, some real sales are missed.
4. **Internal tx overcorrection — CRITICAL (2026-07-12, UPDATED 2026-07-13)**: The internal tx fix that added marketplace payouts can OVERCOUNT sales by including exchange withdrawals. Jpearlking case: initial run said 0.37 ETH (missing internal txs), fix said 2.34 ETH/27 sales (overcorrected with exchange withdrawals), manual analysis showed real number is 2.34 ETH/25 sales. **CORRECTION (2026-07-13)**: Contract-routed ETH from the artist's OWN contracts (SuperRarer, Manifold ERC1155LazyPayableClaim) ARE sales — the contract forwards sale proceeds when a buyer purchases. Do NOT exclude these. Only exclude exchange hot wallet withdrawals (Binance/Coinbase) as non-sales. **Rule**: After fetching internal txs, categorize EVERY incoming ETH transaction by sender type: (a) marketplace contract (OpenSea/Seaport/Wyvern = real sale), (b) artist's OWN contract (SuperRarer, Manifold claim = real sale, contract forwards purchase funds), (c) exchange hot wallet (Binance/Coinbase = withdrawal, NOT sale), (d) EOA that received NFTs (direct sale), (e) other EOA with no NFT transfer (unclear — could be commission, gift, or off-platform sale). Count (a), (b), and (d) as sales. Exclude only (c). For (e), note as "non-sale ETH transfer" and investigate. Use `smart_contracts/{addr}` endpoint on Blockscout v2 to identify contract names.
4. **Profile data**: Use `/identities/{handle}` not `/profiles/{handle}` — the latter returns nested objects.
5. **Posts endpoint**: `/profiles/{handle}/posts` returns 404. Use `/v2/waves/{wave_id}/drops` and filter by author.
6. **Blockscout 403 errors**: Add `User-Agent: Mozilla/5.0` header to all Blockscout API requests.
7. **Collector count inflated**: Marketplace escrow contracts (TL Auction House, Foundation, Seaport) were counted as "collectors" — now excluded via `is_marketplace_contract()` check. Superno's "40 collectors" was actually ~6-7 real people; 99 NFTs went to TL Auction House (listings), 58 to burn address (minting).
7. **Collector count inflated by marketplace escrow (CRITICAL, UNFIXED in script)**: NFTs sent to TL Auction House, Seaport, Foundation contracts for listing are counted as "sent to collectors". Superno showed "40 collectors, 214 sent" but reality was 37 outgoing: 21 to TL Auction House (listings), 7 to burn address, only ~7 to real EOAs. The `get_nft_history_multichain()` function must exclude known marketplace contract addresses from `collector_wallets` and `unique_collectors` counts. Also exclude the zero address (burn/mint). This inflates collector counts for all artists who list on TL Auction House.
8. **"Sent" count inflated by marketplace listings**: Same root cause as #7. NFTs transferred to marketplace escrow for listing are not distributions — they're still owned by the artist, just listed for sale.
9. **Placeholder reference files**: When saving reviews as reference files, always include full on-chain data, not just "see session transcript". Context compaction destroys earlier session data — the reference file IS the durable record.
10. **Blockscout v2 422 error**: `?filter=to%20%7C%20from` param on v2 `/addresses/{addr}/transactions` returns 422. Use bare endpoint (no filter) or v1 API (`?module=account&action=txlist`) instead.
11. **6529 wallets array key**: `/identities/{handle}` returns `wallets` array with key `wallet` (NOT `address`). Using `w.get("address")` silently returns empty wallet list.
12. **Cross-profile analysis requires intermediary checking**: Direct wallet-to-wallet transfers alone miss the most common linkage patterns. Must check shared intermediary EOAs, exchange relay patterns, and ETH round-trip timing. Initial blake69/bicasso analysis found "no connection" — wrong, because it only checked direct links.
13. **Garbage Unicode in on-chain data (OUTPUT FORMATTING)**: Blockscout token transfer API returns scam/spam token names with non-Latin Unicode characters (Cyrillic, CJK, combining diacritics). Examples: fake "USDC" tokens with Cyrillic letters, "ETH" with combining marks. These are unreadable to the user and make the output unusable. **RULE**: When presenting on-chain token data, filter or transliterate any token name containing non-ASCII characters. Replace with `[filtered-scam-token]` or strip to ASCII-only. User explicitly said "I can't read it" when raw scam token names came through in output. This applies to ALL on-chain data presentation, not just vetting scripts.
14. **Contract name mimicry — SuperRarer is NOT SuperRare (2026-07-13, CRITICAL)**: When the vetting script reports "SuperRare mints" or "SuperRare sales," VERIFY the actual contract address. Chonkly's `SuperRarer` contract (0xc360ceca, name "SuperRarer", symbol "SRR") is a DELIBERATE near-clone of the real SuperRare platform (0x41A322b, name "SupeRare", symbol "SUPR"). One extra 'r' in the name. The @beam assessment initially reported "55 SuperRare mints" — ALL were on the knockoff contract, not real SuperRare. This inflated the artist's perceived credentials. **RULE**: Before reporting any NFT platform activity, cross-check the contract address against known platform addresses:
    - Real SuperRare v1: `0x41A322b28D0fF354040e2CbC676f0320d8c8850d` (name: "SupeRare", symbol: "SUPR")
    - Real SuperRare v2: `0xB932a7A1a7c1521A5F199CA0F4D58bD1eA0E8Ee7`
    - Chonkly knockoff: `0xc360CECA69988E39BE18Ddb89E69AFcc33A3833a` (name: "SuperRarer", symbol: "SRR")
    - Also check Foundation, Zora, Rarible, OpenSea (Seaport) addresses
    - If the contract was deployed by the same wallet that buys all the art (platform operator), the "sales" are operator-funded bootstrap purchases, not real market demand. Note this explicitly in the assessment.
    - **Classification impact**: An artist whose entire "established" on-chain history is on a knockoff contract with micro-priced sales to the platform operator should be BORDERLINE at best, not LIKELY_REAL, even if they have real socials and a self-deployed contract. Total lifetime ETH revenue is the real signal, not the mint count.

## Cross-Profile Identity Verification

When asked whether two profiles might be the same person (e.g., "are @X and @Y the same?"), do NOT just check direct wallet-to-wallet transfers. That misses the most common linkage patterns.

**PITFALL**: In the blake69/bicasso case, the initial analysis checked only direct wallet connections and NFT transfers, concluded "no connection." This was WRONG. The user asked about exchange deposit/withdrawal patterns, which revealed 36 shared counterparties including direct ETH round-trips between their wallets within minutes. Always run the full 5-step methodology below, not just step 1.

### Methodology (check ALL of these)

1. **Direct ETH transfers — FULL inventory** — fetch all ETH transactions for each profile's wallets, find ALL transfers between ANY wallet in profile A's set and ANY wallet in profile B's set. Report separately: (a) cross-person transfers (A's wallets ↔ B's wallets), (b) self-transfers (A's own wallets ↔ each other, B's own wallets ↔ each other). Within cross-person transfers, distinguish round-trips (sent + returned within minutes/hours, near-equal amounts = strongest signal) from one-way transfers (payments, gas funding, auction splits). Do NOT only report round-trips — one-way transfers spanning months also matter.

2. **Shared intermediary EOAs** — find personal wallets (NOT exchange addresses, NOT marketplace contracts) that send ETH to BOTH profiles. Filter by:
   - `is_contract == False` on Blockscout
   - Small unique recipient count (<50 = personal wallet, >500 = likely exchange)
   - Has 6529 profile handle (e.g., @696969)
   - Sends to both profiles over overlapping timeframes
   - **PITFALL**: Community auction wallets (e.g., memeablesbtc.eth, memeablesauctions.eth) have 40-110 recipients and send to many 6529 members — these are shared infrastructure, NOT personal wallets. Only treat as linkage signal if the wallet sends to BOTH profiles AND has a very small recipient count (<25). Auction wallets with 100+ recipients are community infrastructure.

3. **Shared exchange deposit/withdrawal addresses** — check if both profiles received ETH from the same Coinbase (0xdfd5293d...), Binance (0x28c6c062..., 0x9696f59e..., 0x56eddb7a...), or other known exchange addresses. Both withdrawing from the same exchange wallet is normal (exchanges use shared hot wallets), but combined with other signals it strengthens the case. **PITFALL**: Do NOT stop at just checking shared exchange addresses — also check the reciprocal pattern: Profile A deposits to exchange X, Profile B withdraws from the same exchange X within days. This requires checking both `sent_to` and `received_from` for each profile against exchange addresses.

4. **Timing analysis** — for each shared intermediary EOA, list all transactions to/from both profiles sorted by timestamp. Look for:
   - Profile A deposits to X, Profile B withdraws from X within days
   - Alternating pattern: X sends to blake, then X sends to bicasso, then back to blake

5. **Shared contract interactions** — both sending ETH to the same NFT mint contracts, same marketplace contracts, same ENS registrar. This alone is weak (common in same community), but combined with ETH flow patterns = stronger.

### Implementation Notes

- Use Blockscout **v1 API** (`?module=account&action=txlist&address={wallet}`) for ETH transactions. The v2 endpoint with filter params (`?filter=to%20%7C%20from`) returns **422 Unprocessable Entity**.
- Also fetch internal txs: `?module=account&action=txlistinternal&address={wallet}`
- 6529 API: `/identities/{handle}` returns wallets array with key `wallet` (NOT `address`).
- Scripts: `scripts/cross_ref_blake_bicasso.py` (counterparty extraction + 4-pattern cross-ref), `scripts/cross_ref_timing.py` (timing analysis for shared EOAs), `scripts/cross_ref_deep.py` (direct transfers + intermediary profiling).

### Case Study: blake69 ↔ bicasso

- **Direct round-trips found**: Jan 25 2024 (blake→bicasso 0.002260 ETH, bicasso→blake 0.002970 ETH, 4 min apart); Mar 26 2023 (blake→bicasso 0.003381, bicasso→blake 0.003400, 31 min apart)
- **Shared personal EOAs**: @696969 (19 recipients, sends to both over 2 years), 0x440538cb (36 recipients, sends to all 3 wallets), memeablesbtc.eth (112 recipients), memeablesauctions.eth (44 recipients)
- **Shared exchange withdrawals**: Coinbase, multiple Binance wallets
- **36 total shared counterparties**
- **Conclusion**: On-chain evidence SUPPORTS same-person speculation. Initial analysis that found "no connection" was wrong — it only checked direct wallet links, missing intermediary relay patterns.
- **Full reference**: `references/blake69-bicasso-crossref.md`

### Multi-Profile Network Analysis (3+ profiles)

When given a LIST of profiles suspected to be the same person (e.g., ZODL, ZODLZO, ZODLZOD, ...), scale the pairwise methodology to N profiles:

1. **Fetch all wallets for all profiles** via `/identities/{handle}` — some profiles may have multiple wallets, some may share wallets (rare but check).
2. **Fetch ALL ETH txs for ALL wallets** (v1 API, both txlist + txlistinternal, up to 20 pages each).
3. **Cross-wallet transfers**: Check direct ETH transfers between ANY pair of wallets in the network. For N profiles, this is N×(N-1)/2 pairs. Sort by timestamp to identify hub-and-spoke patterns.
4. **Discover additional profiles**: For each shared counterparty address, check `/identities/{address}` on 6529 API — if it has a handle that contains a pattern matching the suspected network (e.g., "zodl" substring), it's likely an undiscovered profile in the same network. Also check ENS names for matching patterns.
5. **Shared counterparty analysis**: Same as pairwise — find addresses that interact with 2+ profiles in the network. Filter contracts vs EOAs, check for 6529 profiles.
6. **ENS subdomain patterns**: Shared ENS subdomains (e.g., memeticobjects.eth, play.memeticobjects.eth, neom.memeticobjects.eth) are strong identity linkage signals.

**PITFALL**: The v1 API `txlist` for high-activity wallets may hit the 10,000 transaction cap (Blockscout limits to 10K results). For wallets with more txs, some transfers will be missed. Note this limitation in the analysis.

**PITFALL — Airdrop false positives**: When checking shared counterparties between profiles, addresses with 500+ recipients that send micro-amounts (0.0001–0.003 ETH) TO both profiles are airdrops/staking reward distributions, NOT exchange deposit/withdrawal addresses. Both profiles RECEIVING from the same address is not a linkage signal — only one depositing and the other withdrawing is. Filter these out by checking: (a) both interactions are "received" direction, (b) amounts are micro, (c) recipient count is 500+. Excluded profiles EzMonet and grubnot both shared 4 airdrop addresses with ZODL — none were exchange relays.

**PITFALL — Exchange hot wallet false positives**: Both profiles receiving ETH from the same Binance/Coinbase address (400-600+ recipients) is NOT a linkage signal — exchanges use shared hot wallets for all withdrawals. This only becomes meaningful when combined with timing overlap (both withdrawing from the same address within the same period) AND other linkage signals. In the andi_p vs ZODL check, both received from Binance/Coinbase but ZODL's withdrawals were all in 2021 while andi_p's started in late 2022 — no temporal overlap, so excluded.

**PITFALL — Script reuse**: The cross-reference scripts (`ezmonet_zodl_exchange.py`, `arsonic_gpebbles_check.py`) have hardcoded wallet addresses at the top. When reusing for a new profile, you MUST update the wallet array — `sed` replacing the profile name is not enough; it only changes labels, not the addresses being queried. Always fetch the new profile's wallets via `/identities/{handle}` first, then update the wallet array in the script.

**Synchronized minting as identity signal**: When 3+ profiles mint the same NFT contract within minutes of each other, this is a strong multi-wallet identity signal. In the ZODL case, 5 profiles all sent 0.000777 ETH to the same ERC721DropProxy within 3 minutes (01:31–01:34). No legitimate reason for 5 "different" people to mint the same contract in that window.

### Checking a Candidate Profile Against an Existing Network

When you have an identified multi-profile network (e.g., ZODL) and want to check if a new profile belongs:

1. **Fetch candidate's wallets** via `/identities/{handle}` (key: `wallet`, not `address`)
2. **Direct transfers**: Fetch ALL ETH txs for candidate's wallets. Check for ANY transfer to/from ANY wallet in the network. Zero direct transfers = strong exclusion signal.
3. **Exchange relay**: Check if candidate deposits to an exchange that network members withdraw from (or vice versa). Must find the reciprocal pattern (A deposits, B withdraws from same address) — not just both receiving from the same exchange hot wallet.
4. **Shared personal EOAs**: Check for addresses (is_contract=False, <50 recipients) that interact with both candidate and network. Zero shared personal EOAs = strong exclusion.
5. **ENS naming**: Check if candidate's ENS matches the network's naming pattern (e.g., memeticobjects.eth subdomains).

If ALL five checks come back negative (no direct transfers, no exchange relay, no shared personal EOAs, no ENS overlap), the candidate does NOT belong to the network. Shared contract interactions (Seaport, Manifold, ENS Registrar) are expected between any active 6529 members and are NOT linkage signals.

**Case Study: EzMonet, grubnot, andi_p vs ZODL**
- EzMonet (Level 84, 3 wallets): Zero direct transfers, zero shared personal EOAs, zero exchange relay, no ENS overlap. 26 shared addresses all contracts/airdrops. **Excluded.**
- grubnot (Level 68, 3 wallets): Zero direct transfers, zero shared personal EOAs, zero exchange relay, no ENS overlap. 22 shared addresses all contracts/airdrops. **Excluded.**
- andi_p (Level 36, 2 wallets): Zero direct transfers. Exchange overlap with ZODL via Binance/Coinbase hot wallets but no timing overlap (ZODL 2021, andi_p 2022+). 1 shared personal EOA (@hexum, 18 recipients) with different directions (no round-trip). **Excluded.**
- Script: `scripts/ezmonet_zodl_exchange.py` (adaptable for any candidate-vs-network check — just change the wallet addresses at top)

### On-Chain Real-World Identity Investigation

When asked to identify the real person behind a profile based on chain activity:

**What on-chain data CAN reveal:**
- Wallet connections to other 6529 profiles
- ENS names and subdomain patterns (sometimes self-doxing — e.g., "john.smith.eth")
- Exchange deposit/withdrawal addresses (leads to KYC'd accounts, but you can't see the KYC data)
- NFT collections, marketplace activity, minting patterns
- Financial relationships with specific community members

**What on-chain data CANNOT reveal:**
- Real name, location, or physical identity — unless the person self-doxed
- Social media accounts — unless linked in CIC statements or ENS
- KYC information at exchanges (you see the exchange address, not who owns the account)

**Methodology:**
1. Fetch profile via `/identities/{handle}` — check classification, level, wallets, ENS names
2. Check CIC statements for social links (`GET /profiles/{handle}/cic/statements`)
3. **Check ALL wave drops for self-doxing links** — profile wave (`GET /waves/{profile_wave_id}/drops`), Meme Club wave, and any other waves the profile has posted on. Scan all drop content for `x.com/`, `twitter.com/`, `instagram.com/`, personal website URLs. Users often share their social handles in wave posts even when CIC statements are empty. **This step is MANDATORY** — skipping it caused a false "cannot identify" conclusion in the blocknoob case. The self-doxing link may be in the profile wave OR in Meme Club OR in any other wave the user posted on — check all of them.
4. Fetch ALL ETH transactions (v1 API, both txlist + txlistinternal) for all wallets
5. Identify ALL counterparties — check each on Blockscout for ENS, contract status, and on 6529 for profile handle
6. Flag any self-doxing ENS names (real names, locations)
7. Flag any exchange deposit addresses (Coinbase, Binance, Kraken) — these are the trail to real identity but the trail stops at the exchange
8. Check Meme Club activity (see below)

**Case Study: Blocknoob identity investigation**
- Level 86, PSEUDONYM classification, 3 wallets (vault.blocknoob.eth, memes.blocknoob.eth, noobmuseum.eth)
- No social links in CIC, no self-doxing ENS names
- 49 counterparties, all 6529 community members or NFT contracts — no exchange deposits
- Significant financial relationships: @6529complaints (12 ETH), @lol (11 ETH), @famous (6.4 ETH, holds the blocknoob.eth ENS)
- @6529Deployer sent 7 ETH (platform payments)
- 2x Main Stage winner, wave creator ("The Three Keys" curation group)
- **Self-dox found in profile wave drops**: Blocknoob posted `https://x.com/blocknoob_/status/2074627670885716004` in his "The Three Keys" profile wave — revealing his X handle as **@blocknoob_** (display name "blocknoob 🦇🔊⌐🆇-🆇", Twitter ID 1366325647421952002)
- **Initial conclusion was WRONG**: First analysis said "Cannot identify real person — fully pseudonymous with no on-chain self-doxing." This was incorrect because I only checked CIC statements and ENS names for self-doxing — I did NOT check the profile wave drops for self-posted links. The user said "you missed the tag in Meme Club" — this referred to a 6529.io wave URL. The self-doxing X link was actually in the profile wave, not Meme Club. The lesson: check ALL wave drops for a profile (profile wave, Meme Club, any other waves they've posted on) for self-doxing links.
- **Lesson**: ALWAYS check profile wave drops (`GET /waves/{profile_wave_id}/drops`) for self-doxing links — X/Twitter URLs, Instagram, personal websites. Users often share their social links in wave posts even when CIC statements are empty.
- **Full reference**: `references/blocknoob-identity-analysis.md`
- **Script**: `scripts/blocknoob_identity.py`

### NFT Platform Investigation (2026-07-13)

When a shared NFT contract appears across multiple artist assessments, determine whether it's a **public platform** (many independent users) or a **private ring** (one operator running multiple personas). This distinction changes the classification.

**Investigation steps:**

1. **Check contract holder count** — `GET https://eth.blockscout.com/api/v2/tokens/{contract}` → `holders_count`. Large holder count (1,000+) = public platform. Small count (13-50) = could be private ring.
2. **Check for a website** — The contract source code may contain a base URI (e.g., `https://chonkly.com/api/metadata/`). Visit the site. Is it a live marketplace with a feed, profiles, and artist pages? Or a dead placeholder?
3. **Check the contract deployer** — `GET https://eth.blockscout.com/api/v2/addresses/{contract}` → `creator_address_hash`. Is the deployer also the primary buyer for all artists? If yes, this is a **platform operator bootstrap pattern** — the operator buys from artists to create marketplace liquidity. This is common for small NFT platforms and is NOT the same as one person running fake artist profiles.
4. **Check for external community** — Does the platform have Discord, Telegram, Twitter, or any social presence? Search the site footer, about page, contact page for social links. Some platforms (like Chonkly) have no external community — users interact on the platform itself and on adjacent communities (like 6529.io).
5. **Check platform scale** — How many total tokens exist? The Chonkly case: SuperRarer had 15,000+ tokens from 1,732 holders. This is a real platform with many users, not a 13-person ring.
6. **Sample token metadata** — `GET https://eth.blockscout.com/api/v2/tokens/{contract}/instances/{token_id}` → check `metadata.attributes` for artist names. Are there many different artists, or just the 13 suspected profiles?
7. **Check contact info** — The platform's contact page may reveal the operator's identity (e.g., noah@chonkly.com).

**Deeper analysis — pass-through vs accumulator (2026-07-13):**
When the operator-buyer pattern is confirmed, determine whether the buyer is **accumulating** (holding, supporting artists) or **passing through** (reselling to other wallets = money laundering or wash trading).
1. Fetch all NFT transfers for the buyer wallet (tokennfttx, multiple pages).
2. Separate IN (purchases) vs OUT (resales). Calculate return rate: OUT/IN.
   - <15% return = accumulator (operator supporting artists — Chonkly: 89 returned of 772 = 12%)
   - >80% return = pass-through (possible laundering)
3. Check unique seller count — 74 unique sellers = real platform with many users. Only the suspected profiles = possible ring.
4. Check purchase method — buyer calling `buyToken()` with ETH value = real marketplace purchases. Direct `transferFrom` with 0 ETH = free transfers (weaker signal).
5. Check purchase prices — micro-prices (0.005-0.015 ETH) = bootstrap pattern, not real market demand.

**Holder distribution analysis (2026-07-13):**
Fetch ALL token holders (`?module=token&action=getTokenHolders`, iterate pages) and bucket by balance:
- 1 token / 2-3 / 4-10 / 11-50 / 51-100 / 101-500 / 500+
- Long-tail distribution (44% with 1 token, median 2) = genuine platform with many casual users
- Concentrated distribution (most holders have 100+ tokens) = possible ring
- Check top 10 holders for exchange hot wallets (Binance 0xF977814, Coinbase 0xdfd5293d) — exchange-custodied tokens are held for users, not owned by the exchange
- Top 10 owning <40% of total = reasonably distributed. >70% = concentrated.

**Method ID reference for contract transaction analysis:**
- `0x6a627842` = `mint(address)` — artists minting (usually 0 ETH value)
- `0xa223e05d` = `listToken(uint256,uint256)` — listing for sale
- `0x4a8c3b34` = `buyToken(uint256)` — buyer purchasing
- `0x2eb2a065` = `unlistToken(uint256)` — removing listing
- `0x23b872dd` = `transferFrom(address,address,uint256)` — direct transfer
- `0x42842e0e` = `safeTransferFrom` — safe transfer
- Fetch via: `GET /api/v1?module=account&action=txlist&address={contract}&sort=desc`
- Count method frequency to understand platform activity: 99% mint calls = active creation platform

**Classification guidance:**
- **Public platform + operator buys from all artists + accumulator pattern + long-tail holders** = LIKELY_REAL for individual artists. The single-buyer concentration is a platform dynamic, not a sybil signal. Note it as a concern but do NOT upgrade to SUSPICIOUS solely on this basis.
- **BUT — brand mimicry downgrades to BORDERLINE**: If the platform's contract name deliberately mimics a major platform (e.g., "SuperRarer" vs "SuperRare"), artists' "platform participation" is inflated. An artist whose entire on-chain history is on a knockoff contract with micro-priced operator sales should be BORDERLINE, not LIKELY_REAL — even with real socials and a self-deployed contract. The key signal is total lifetime ETH revenue from real third-party buyers, not mint counts on a brand-squatting contract.
- **Private contract + one buyer + batch-created profiles** = SUSPICIOUS. But verify "batch-created" via CIC dates, not just `created_at`.
- **Pass-through pattern** (buyer resells 80%+ to other wallets) = SUSPICIOUS even if platform looks real.
- **Key distinction**: 1,732 holders with long-tail distribution on a live website = platform. 13 holders with no website = private ring.

**Case Study: Chonkly Platform Investigation**
- chonkly.com is a live Next.js NFT marketplace with Convex backend
- SuperRarer contract: 1,732 holders, 15,000+ tokens — real platform
- Chonkly contract: 152 holders — secondary collection
- Both deployed by chonkly.eth (0x05df3e4b) — the platform operator
- chonkly.eth is the primary buyer for all 13 6529 artists on the platform
- No Discord/Telegram — community lives on chonkly.com + 6529 dive bar
- Contact: noah@chonkly.com
- Twitter @chonkly = YULIARTO CHONKLY, Jakarta (1 follower — dormant)
- "Built by Big Dingus" persona
- **Conclusion**: Small-platform bootstrap pattern. The operator buys from artists to create sale history. Artists are real platform users who found 6529 independently over 14+ months.
- **How to find platform website**: Check contract source code for base URI string. Chonkly contract had `_baseTokenURI = "https://chonkly.com/api/metadata/"`. SuperRarer had `"https://your-api.com/metadata/"` (placeholder, updated on-chain). Use Blockscout v2 smart-contracts endpoint to get source code.
- **BRAND MIMICRY (2026-07-13)**: The SuperRarer contract name is a deliberate near-clone of SuperRare (real platform: "SupeRare" 0x41A322b, knockoff: "SuperRarer" 0xc360ceca — one extra 'r'). This inflates artists' perceived credentials when they or others say "I sell on SuperRare." ALWAYS verify the actual contract address when a vetting script reports SuperRare activity. The @beam assessment initially reported "55 SuperRare mints" — all were on the knockoff, zero on real SuperRare. This contributed to a LIKELY_REAL classification that should have been BORDERLINE. See bug #14 above.
- **VERIFIED ACROSS ALL 13 PROFILES (2026-07-13)**: Systematic check confirmed ZERO real SuperRare transfers across all 13 Chonkly-connected 6529 profiles. 12 of 13 have SuperRarer tokens only. Any previous assessment attributing "SuperRare mints" to any Chonkly artist was wrong.
- **Full platform reference**: `references/chonkly-platform.md` (platform details, contract info, investigation methods, artist mapping, `created_at` vs real timeline)

### Scripts Inventory

Cross-profile and identity analysis scripts (all in `scripts/` under themanager profile dir):
- `seeking_nomination_vetting.py` — main vetting library (multichain NFT, sales, wash trading, artwork)
- `run_assessment.py` — standalone runner for individual profile assessments
- `cross_ref_blake_bicasso.py` — counterparty extraction + 4-pattern cross-ref
- `cross_ref_timing.py` — timing analysis for shared EOAs
- `cross_ref_deep.py` — direct transfers + intermediary profiling
- `zodl_analysis.py` — multi-profile network analysis (N profiles)
- `ezmonet_zodl_exchange.py` — candidate-vs-network exclusion check (adaptable)
- `arsonic_gpebbles_check.py` — pairwise cross-reference (adaptable)
- `blocknoob_identity.py` — on-chain identity investigation with counterparty profiling
- `analyze_memeables.py` / `analyze_memeables_full.py` — community auction wallet analysis

### Meme Club as Investigation Surface

Meme Club is the public signal layer for The Memes Main Stage. It contains useful identity signals:

**Meme Club Wave ID**: `d23af421-203d-4e37-abc1-4d9df840026c`

**API endpoints:**
- Drops: `GET /waves/{MC_WAVE}/drops?sort_direction=DESC&limit=100`
- Individual drop: `GET /v2/drops/{drop_id}`
- Votes on a submission: `GET /v2/drops/{drop_id}/votes` — returns voter handle, level, and vote amount

**What Meme Club reveals about a profile:**
- **Main Stage wins** (`winner_main_stage_drop_ids` in identity data) — shows creative output
- **Participation stats** — TheManager posts periodic stats ranking voters by TDH multiple
- **Participatory drops** — TheManager auto-adds submissions when MC members vote 2.5M+ TDH on Main Stage, tagging all voting members
- **Drop types**: CHAT (conversations), PARTICIPATORY (auto-added submissions), SUBMISSION (Main Stage entries)
- **Profile wave**: If `is_wave_creator: True`, the profile runs a curation wave — shows community role

**PITFALL — Meme Club API pagination**: The `page` parameter does NOT work — fetching page 2 returns the same 100 drops as page 1. The `offset` parameter also returns duplicates. Only the first 100 drops (newest) are reliably accessible. To get older drops, use serial_no ranges or specific drop IDs.

**PITFALL — memeclub.6529.io not accessible from API server**: The leaderboard at memeclub.6529.io does not resolve from the Hermes server (DNS failure). Only the API endpoints work.

**PITFALL — Frontend-only content**: Some Meme Club features (leaderboard, profile tags) may be visible on the 6529.io frontend but not accessible via the API. If a user references something on the frontend that you can't find via API, ask them to clarify — don't assume it doesn't exist.

**PITFALL — Meme Club participation stats mentions are text-only**: TheManager's periodic participation stats posts list voter handles in the content text but do NOT populate the `mentioned_users` array. When searching for a handle in Meme Club drops, search the content text, not just the mentions field.

**PITFALL —Votes endpoint**: `GET /v2/drops/{drop_id}/votes` returns a paginated list with `data` key containing voter objects (handle, level, vote amount). This is the reliable way to check who voted on a specific submission. The `top_raters` field on the drop object may be incomplete or empty.

**Case Study: Arsonic vs gpebbles (pairwise, NOT same person)**
- 1 direct transfer: gpebbles → Arsonic, 1.0 ETH (one-way, Sep 2025, no return)
- 35 shared counterparties — ALL marketplace contracts (Seaport, SuperRare, Manifold, Foundation, etc.)
- Zero exchange relay, zero shared personal EOAs, no ENS overlap
- Both heavy NFT traders (2,692 + 3,073 ETH value transfers) in same ecosystem but no identity linkage
- Script: `scripts/arsonic_gpebbles_check.py` (adaptable for any pairwise check)
- **Full reference**: `references/arsonic-gpebbles-crossref.md`

**Case Study: ZODL Network (11 profiles)**
- 864 direct ETH transfers between ZODL wallets over 5 years (2021-2026)
- Hub-and-spoke pattern: ZODLZODLZOD central hub, ZODL and ZODLZOD secondary
- Shared ENS subdomains: memeticobjects.eth family, 💞forever.eth theme
- 11th profile (@ZODLZODLZODLZOD) discovered via ENS "💞forever.eth" appearing as counterparty to 7 of 10 profiles
- Conclusion: Unambiguous — all 11 profiles are the same person
- **Full reference**: `references/zodl-network.md` (11 profiles, 864 transfers, ENS patterns, synchronized minting)
- **Exclusion case studies** (EzMonet, grubnot, andi_p checked against ZODL, all excluded): `references/ezmonet-grubnot-zodl-exclusion.md`

## Feedback Documents for Artists

When RD asks for a review to share with an artist as feedback, write it as a standalone `references/{handle}-feedback.md` file. Format:
- Overview (who they are, wallet age)
- Social Presence (all verified links)
- On-Chain Activity (per-chain breakdown)
- Incoming ETH Analysis (categorize EVERY tx by sender type — marketplace sale vs own-contract payout vs exchange withdrawal vs direct)
- Verified Sales Summary (only real sales, with timeline)
- Artistic Output (collections, platforms, artwork examples)
- Collector Analysis (how many, 6529 overlap)
- Strengths (numbered)
- Concerns (numbered)
- Bottom Line (classification + key takeaway)

**Do NOT include internal analysis details** (script names, API endpoints, debugging notes). The feedback document is for the artist to read.

**Tone (RD directive 2026-07-13)**: Feedback documents must be nonjudgmental. State facts, not opinions about motives. Do NOT say "community members gave rep without researching" or "social links may be fake." Present what exists and what doesn't — let the reader draw conclusions. Social links are noted as present, not scored. Rep concentration is stated as a percentage, not characterized as "narrow" or "unresearched."

Example: `references/Jpearlking-feedback.md`

## Newcomer / Returning Artist Assessment

### Community Wave Engagement Lesson (2026-07-13)

The @kiramoto case exposed a critical gap in the assessment workflow:

- **What happened**: @kiramoto was assessed as having "zero 6529 engagement" based on 0 SN posts, no profile wave, no reactions. This was reported to RD.
- **What RD found**: Kiramoto was actively posting in maybe's dive bar — ~20 messages on his first day, introducing himself, sharing his art background, being recognized by @Metpenfaul (L14) who confirmed collecting his work.
- **Root cause**: The assessment only checked SN posts and profile wave. It did NOT check community waves (dive bar, Meme Club, Karen Army).
- **Impact**: The assessment was misleading — it understated the artist's community engagement and missed existing collector relationships.

**MANDATORY STEP**: Before reporting "zero 6529 engagement," ALWAYS check maybe's dive bar (`b38288e6-ca9d-45ce-8323-3dc5e094f04e`) for posts by the artist. This is where newcomers and returning artists engage first.

### Non-Sale ETH Transfer Investigation

When an ETH transfer has no associated NFT transfer (sender received 0 NFTs from the artist), do NOT automatically dismiss it. Investigate:

1. **Check the sender's 6529 profile** — `GET /identities/{address}`. If they're an established member (high level, GOVERNMENT_NAME classification), the payment is likely legitimate (commission, direct purchase, support).
2. **Check for NFT transfers via marketplace** — The buyer may have purchased through OpenSea/Seaport, meaning the NFT went to marketplace escrow, not directly from the artist.
3. **Check community waves** — The sender may be a known collector who posted about owning the artist's work (e.g., @Metpenfaul confirming in dive bar: "I still have my piece collected from you").
4. **Check reverse direction** — Did the artist send any ETH back? One-way transfers from established members are typically legitimate. Round-trips are suspicious.

**Case Study: @dylanwade → @kiramoto (0.28 ETH, May 2023)**
- Plain ETH transfer, no NFT received, no round-trip
- Dylanwade: L22, GOVERNMENT_NAME (real name), filmmaker
- Zero shared counterparties, no wash trading pattern
- Most likely: direct purchase, commission, or support payment
- Context: kiramoto had 2 OpenSea sales 2 months prior, was an active artist at the time

### Dive Bar Wave Details
- **Wave ID**: `b38288e6-ca9d-45ce-8323-3dc5e094f04e`
- **API**: `GET /waves/{wave_id}/drops?limit=200` (v1 endpoint works, v2 may return empty)
- **Filter by author**: `drop.get('author', {}).get('handle', '').lower() == target_handle`
- **Content field**: `drop.get('parts', [{}])[0].get('content', '')`

### Profile-Logs API (Handle History, Rep Sources, Activity Timeline)

**Endpoint**: `GET /api/profile-logs?target_profile_id={profile_id}&limit=100`

Returns activity logs for a profile — drops created, reactions, rating edits (rep grants), handle edits, classification edits, PFP/banner changes. Use for:

1. **Handle change detection**: Filter for `type: HANDLE_EDIT` — shows `old_value` and `new_value`. If a profile recently changed its handle, this reveals the previous name.
2. **Rep source analysis**: Filter for `type: RATING_EDIT` — shows `profile_handle` (who gave rep), `new_rating`, `old_rating`, `rating_matter` (REP/CIC), `rating_category`, and `change_reason` (USER_EDIT, HELP_BOT_AUTOMATIC_GRANT). This reveals whether rep came from community members, bots, or bulk grants.
3. **Activity timeline**: Earliest log timestamp shows when the profile (or its wallet) first became active on 6529. If all logs are from one day but rep is high, the rep was granted that day (not accrued over months).
4. **Profile creation check**: `type: PROFILE_CREATED` logs show when the profile was actually set up (vs wallet just existing).

**PITFALL**: The `handle` parameter is ignored — the API returns the *authenticated caller's* logs. MUST use `target_profile_id` parameter with the profile's UUID (from `/identities/{handle}` → `id` field).

**PITFALL**: `profile_id` parameter (without `target_` prefix) also returns the caller's own logs, not the target's. Always use `target_profile_id`.

**PITFALL — Profile-logs flooded by drop activity (2026-07-13)**: For active new users who post and react heavily on their first day, the profile-logs API (`limit=100`) can be dominated by DROP_CREATED and DROP_REACTED entries, pushing RATING_EDIT entries beyond the 100-result cap. In the @beam case: 310 DROP_CREATED + 163 DROP_REACTED in a 1-hour window meant only 23 RATING_EDIT entries were visible — and Sherie_Margaret's 1,200 MemesNominee rep grant was NOT in the logs. The profile-logs showed 220 rep received, but the rep-categories endpoint showed 1,950 total. **Rule**: Always cross-check rep totals from profile-logs against the rep-categories endpoint (`GET /profiles/{profile_id}/rep/categories`). The rep-categories endpoint is the source of truth for total rep and contributor breakdown; profile-logs is supplementary for timing and change reasons.

**Key learning (2026-07-13)**: Wallets can accrue rep WITHOUT a 6529 profile being set up. Rep attaches to the wallet address. A profile created today may show months of pre-existing rep. However, the profile-logs API will show whether the rep was actually accrued over time or granted in bulk on the same day. In the @Metpenfaul case, all 501 logs (including 59 RATING_EDIT entries) were from a single 2-hour window — confirming the rep was not accrued over months but granted today.

### Deconsolidation / Reconsolidation Detection

**What it is**: A wallet can be unconsolidated from one 6529 identity and re-consolidated under a NEW identity (different handle, different profile ID). The rep attached to the wallet FOLLOWS it to the new identity. The previous identity's handle and history become invisible — the profile-logs API only shows the current identity's logs.

**When to check**: A profile that was created very recently (today/this week) but has significant rep (10K+) from established community members. The rep couldn't have been earned in that time — it came from a previous identity.

**Detection method**:
1. Check `created_at` on the profile (`GET /profiles/{handle}`) — if it's today but rep is 10K+, investigate
2. Check profile-logs (`GET /api/profile-logs?target_profile_id={id}`) — if ALL logs are from today but rep is high, the rep was NOT accrued today — it followed the wallet from a previous identity
3. **Check rep categories** (`GET /profiles/{profile_id}/rep/categories`) — this reveals WHO gave the rep and WHEN. If top contributors are established members (L50+) who gave rep months ago, but the profile was created today, the wallet was previously consolidated under a different identity
4. The previous identity's handle is LOST — there's no HANDLE_EDIT in the logs because it's not a rename, it's a deconsolidation/reconsolidation

**Why it matters for vetting**:
- Deconsolidation/reconsolidation is rare, especially for newcomers
- It obscures the previous identity's posting history, community interactions, and any red flags
- When combined with bridge wallet connections to another profile created the same day, it's a strong coordination signal
- The previous identity may have been flagged or excluded — the reconsolidation could be an attempt to start fresh with carried-over rep

**Case Study: @beam & the Chonkly Network (buyer = contract deployer → small-platform bootstrap, NOT sybil)**
- INITIAL assessment: chonkly.eth (0x05df) was beam's sole SuperRare buyer AND deployed the Chonkly contract beam mints on. Flagged as LIKELY_REAL.
- RD flagged suspicion about the Chonkly contract recurring across assessments. Deeper investigation found 13 6529 profiles all minting on the Chonkly contract, all selling to chonkly.eth. Some NFTs flow back from chonkly.eth to artists (wash-trading-like pattern). Ordinaryartist directly funded Bubblezzz.
- INITIAL conclusion: "coordinated 13-profile network, all created within 4.5 seconds" → SUSPICIOUS. **THIS WAS WRONG.** The 4.5-second `created_at` window was a batch system event (deconsolidation/migration), NOT actual profile creation. Cross-checking CIC statement dates showed the 13 profiles joined over 14+ months (Rueby May 2025, Curtisforfun Jul 2026). They are NOT coordinated batch creation.
- **CORRECTED conclusion**: Chonkly is a small NFT platform (chonkly.com, SuperRarer contract with 1,732 holders). chonkly.eth is the platform operator who buys from all artists to bootstrap marketplace liquidity — a common small-platform pattern, NOT a single person running 13 fake profiles. The Ordinaryartist↔Bubblezzz direct ETH link is a genuine connection between two platform users, not evidence of sybil coordination.
- **FURTHER CORRECTION (SuperRarer ≠ SuperRare)**: The initial LIKELY_REAL classification was STILL WRONG. The SuperRarer contract is a deliberate name clone of SuperRare (one extra 'r'). Beam has ZERO real SuperRare transfers — all "SuperRare mints" were on the knockoff. Classification revised to **BORDERLINE**: genuine socials and own TTA contract, but zero real marketplace presence, micro-priced sales to platform operator on a brand-mimicking contract, ~$877 total career revenue.
- **Lesson 1**: When a shared contract/buyer appears across multiple profiles, investigate the full network — but do NOT assume batch creation from `created_at` timestamps alone. ALWAYS cross-check with CIC statement dates or earliest wave drops.
- **Lesson 2**: A single buyer for all artists on a small NFT platform is a bootstrap liquidity pattern, not automatically sybil. Check whether the buyer is the platform deployer (operator) vs a single user running multiple personas.
- **Lesson 3**: Before asserting "coordinated network" or "simultaneous creation," verify the claim against multiple data sources. The 4.5-second claim was repeated in the SKILL.md, beam.md reference, and memory — all wrong. RD caught the contradiction.
- **Full reference**: `references/beam.md` (updated with corrected analysis)
- **Network detection methodology**: see "Shared Contract Network Detection" below

### Shared Contract Network Detection (2026-07-13)

When RD flags a recurring contract or buyer pattern across multiple artist assessments, or when the same NFT contract appears in 2+ assessments, investigate whether multiple 6529 profiles are part of a coordinated network.

**Detection methodology (check ALL steps):**

1. **Fetch all transactions on the shared contract** — `GET https://eth.blockscout.com/api/v1?module=account&action=txlist&address={contract}&sort=asc` (may need multiple pages — 4,829 txs in the Chonkly case)
2. **Identify all minters** — addresses that sent transactions TO the contract. Build a frequency table.
3. **Check each minter for a 6529 profile** — `GET /identities/{address}` for each. Filter to those with real handles (not `id-0x...` auto-IDs). In the Chonkly case: 164 minters, 13 with real 6529 handles.
4. **Compare profile creation timestamps** — `GET /profiles/{handle}` and check `created_at`. If multiple profiles were created within seconds of each other, that's a STRONG coordination signal. The Chonkly 13 were all created in a 4.5-second window.
5. **Check NFT transfers between the profiles** — `GET ?module=account&action=tokennfttx&address={wallet}` for each. Look for: (a) shared buyer (all send NFTs to the same address), (b) NFT round-trips (artist → buyer → back to artist = wash trading), (c) direct NFT transfers between profiles.
6. **Check direct ETH transfers between profiles** — fetch `txlist` for each wallet, filter for transfers to/from other known wallets in the set. Direct ETH links (like Ordinaryartist → Bubblezzz with 16 transfers) confirm coordination.
7. **Identify the contract deployer** — `GET https://eth.blockscout.com/api/v2/addresses/{contract}` → `creator_address_hash`. Check if the deployer is also the primary buyer (chonkly.eth both deployed Chonkly AND bought from all 13 artists).

**Classification impact**: When a profile is found to be part of a coordinated network with simultaneous creation and shared buyer/wash-trading patterns, upgrade classification to SUSPICIOUS regardless of individual profile strength. The individual profile may look legitimate in isolation (real socials, own contracts, marketplace sales) — the network context is what reveals the coordination.

**BUT — verify "simultaneous creation" before asserting it**: The `created_at` timestamp can reflect batch system events (deconsolidation, migration, schema update), NOT actual profile creation. In the Chonkly case, 13 profiles appeared to have been "created within 4.5 seconds" — this was WRONG. Cross-checking CIC statement dates showed they joined over 14+ months. ALWAYS verify `created_at` claims against:
1. CIC statement dates (`GET /profiles/{handle}/cic/statements` — earliest statement date)
2. Earliest wave drops by the profile's wallet
3. Profile-logs for PROFILE_CREATED entries

If the `created_at` window is tight but CIC dates span months, the `created_at` is a system artifact, not coordinated creation.

**Platform operator vs sybil operator**: When one address (e.g., chonkly.eth) is the primary buyer for all artists on a shared contract, check whether that address is the CONTRACT DEPLOYER. If the deployer is also the sole buyer, this is a small NFT platform bootstrap pattern — the operator buys from artists to create marketplace history and attract users. This is NOT the same as one person running multiple artist personas. Check:
1. How many total holders does the contract have? (1,732 holders = real platform with many users; 13 holders = possibly a private ring)
2. Does the platform have a website? (chonkly.com is a live marketplace)
3. Does the platform have external users outside the suspected network?

**PITFALL**: Assessing each profile in isolation misses the network. The initial beam assessment was LIKELY_REAL — real socials, own TTA contract, SuperRare mints, 1 ETH in sales. Only when the Chonkly contract was investigated across all 13 profiles did the shared-buyer pattern become visible. When RD expresses suspicion about a recurring pattern, follow the trail across ALL profiles, not just the one being assessed.

**PITFALL — `created_at` false batch creation (2026-07-13, CRITICAL)**: The Chonkly case initially reported "13 profiles created within 4.5 seconds" as evidence of coordinated batch creation. This was WRONG. The `created_at` field reflected a batch system event (likely deconsolidation/migration), not actual profile creation. Real timeline from CIC statement dates: profiles joined over 14+ months (Rueby May 2025, XON Jun 2025, Curtisforfun Jul 2026). This reinforces the earlier pitfall about `created_at` not reflecting first appearance. **The corrected lesson**: shared `created_at` timestamps across multiple profiles do NOT prove coordination — they may be a system artifact. Always cross-check with CIC dates and wave drops before asserting "simultaneous creation."

### Marketplace Contract Identification via Internal Transactions (2026-07-13)

When categorizing internal ETH transactions (txlistinternal), identify the source contract to determine if a payment is a marketplace sale. Common contracts that appear as internal tx senders:

- **Foundation v1 proxy** (0xcda72070e455bb31c7690a170224ce43623d0b6f): `AdminUpgradeabilityProxy`, created Jan 2021. Distributes NFTs to buyers and pays ETH to artists. If an artist's own-contract tokens went here, they were listed on Foundation.
- **Manifold ERC1155LazyPayableClaim** (0x44e94034afce2dd3cd5eb62528f239686fc8f162): Manifold edition drops. Artists mint paid editions, contract forwards proceeds.
- **Manifold ERC721LazyPayableClaim** (0x7581871e1c11f85ec7f02382632b8574fad11b22): Same pattern for ERC721 editions.
- **WETH** (0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2): Wrapped ETH unwrap, not a sale.
- **RelayRouterV3** (0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f): Gas relay router, not a sale.

**How to identify**: `GET https://eth.blockscout.com/api/v2/smart-contracts/{address}` → check `name` field. Verified contracts show their name directly.

**Case Study: @beam revenue breakdown**
- 0x44e94034 (Manifold ERC1155LazyPayableClaim): 0.475 ETH — 25+ small edition sales (Jan-Feb 2023)
- 0xcda72070 (Foundation v1 proxy): 0.276 ETH — 1 real sale to blamekato.eth (Feb-Apr 2023)
- 0x7581871e (Manifold ERC721LazyPayableClaim): 0.070 ETH — 7 edition sales (Apr 2023)
- 0xc360ceca (SuperRarer/Chonkly): 0.139 ETH — micro-priced sales (Feb-May 2026)
- Total: ~1.09 ETH, with ~0.82 ETH from real platforms (Manifold + Foundation)

### OpenSea Unindexed Contracts (2026-07-13)

**PITFALL**: Contracts not indexed on OpenSea make thousands of NFTs invisible on wallet profiles. chonkly.eth holds 2,200+ NFTs on-chain but shows only 9 on OpenSea because both SuperRarer and Chonkly contracts return 404 on OpenSea's API.

**Rule**: When a wallet shows very few NFTs on OpenSea but has thousands of transfers on Blockscout, check whether the contracts are indexed on OpenSea:
- `GET https://api.opensea.io/api/v2/collections/chain/ethereum/{contract}/stats` → 404 = not indexed
- OpenSea v1 API is permanently removed (410) — use v2 only (requires API key for most endpoints)
- Unindexed contracts are invisible to the broader NFT ecosystem — tokens exist only on their native platform and block explorers
- This is a signal: if an artist's entire portfolio is on unindexed contracts, their work is invisible to the major marketplace

**Case Study: Chonkly contracts**
- SuperRarer (0xc360ceca): 404 on OpenSea, 1,732 holders, 16,678 tokens on-chain
- Chonkly (0x235f1802): 404 on OpenSea, 152 holders, 2,208 tokens on-chain
- chonkly.eth: 2,200+ tokens on-chain, 9 visible on OpenSea

### Contract Name Verification (2026-07-13, CRITICAL)

**PITFALL**: Always verify contract ADDRESSES, not just names. A contract named "SuperRarer" (one extra 'r') was mistaken for "SuperRare" (the major curated platform) in the @beam assessment. This inflated the artist's perceived credentials — "55 SuperRare mints" was actually 36 mints on a Chonkly knockoff contract with micro-priced sales to the platform operator.

**Rule**: When reporting NFT platform participation, ALWAYS cross-check the contract address against the real platform's known address:
- SuperRare v1: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d (name: "SupeRare", symbol: SUPR) — 1,195 holders
- SuperRare v2: 0xB932a70A57673d89f4acFFBE830e8ED7f75fb9e0 (name: "SuperRareV2") — Papillon confirmed using this
- Foundation v1 marketplace proxy: 0xcda72070E455bb31C7690a170224cE43623D0B6f (name: "AdminUpgradeabilityProxy", created Jan 2021) — receives NFTs from artists for listing, distributes to buyers, pays sellers via internal transactions. NOT a collector.
- Foundation v2: 0x3B3ee1931Dc30F20FFA2Df07F88f93C1B0b94fC0
- OpenSea (Seaport): 0x00000000000001adF28eF1c7D0186488931B0b94fC0
- Foundation: 0x3B3ee1931Dc30F20FFA2Df07F88f93C1B0b94fC0
- OpenSea (Seaport): 0x00000000000001adF28eF1c7D0186488931B0b94fC0

If a contract name is a near-clone of a known platform (extra letter, similar spelling), flag it as brand mimicry and do NOT count it as participation in the real platform.

**Systematic cross-check rule (2026-07-13)**: When contract name mimicry is discovered for one profile, IMMEDIATELY check ALL profiles known to be on that contract. In the Chonkly case, discovering SuperRarer ≠ SuperRare for @beam led to checking all 13 Chonkly-connected profiles — ALL 12 with SuperRarer tokens had zero real SuperRare. @Jpearlking's assessment also said "SuperRare: 56 mints" — all were SuperRarer. One discovery should trigger a sweep of all affected assessments.

**Case Study: @beam SuperRarer confusion**
- Initial assessment: "55 SuperRare mints" → LIKELY_REAL
- Reality: Zero SuperRare transfers. All 36 mints on "SuperRarer" (0xc360ceca), a Chonkly contract named to mimic SuperRare
- Impact: Classification downgraded from LIKELY_REAL to BORDERLINE
- Lesson: The extra 'r' in "SuperRarer" vs "SuperRare" was the difference between "established artist on major platform" and "artist on unknown micro-platform with brand-squatting contract name"

**Case Study: @Jpearlking SuperRarer confusion (2026-07-13)**
- Assessment said "SuperRare: 56 mints (primary platform)" and listed "Multi-platform: SuperRare, Foundation, OpenSea, TL" as a strength
- Reality: Zero real SuperRare transfers. All 56 mints on SuperRarer (0xc360ceca). Contract deployed by chonkly.eth, NOT by Jpearlking.
- Assessment also said SuperRarer was "artist's own deployed contract" — WRONG. chonkly.eth deployed it.
- Impact: Multi-platform strength weakened. 14 SuperRarer sales (0.25 ETH) recontextualized as Chonkly operator micro-sales, not SuperRare sales.
- Lesson: Same misattribution can affect multiple profiles on the same contract. Always sweep.

**Case Study: @Papillon — confirmed REAL SuperRare (2026-07-13)**
- Assessment said "SuperRare photographer" with superrare.com profile link
- Verification: Papillon mints on SuperRareV2 (0xB932a7) — the REAL SuperRare v2 contract. 20 transfers confirmed.
- Lesson: The contract address check works both ways — it confirms real platform participation too, not just catching knockoffs. Papillon's SuperRare references are legitimate.

### OpenSea Indexing Check (2026-07-13, CRITICAL)

**PITFALL**: Always check whether NFT contracts are indexed on OpenSea. A contract can be verified on Blockscout but completely invisible on OpenSea — meaning the tokens have no presence in the standard NFT market ecosystem. This dramatically reduces the value of "sales" on that contract.

**How to check**: `GET https://api.opensea.io/api/v2/collections/chain/ethereum/{contract_address}/stats` — returns 404 if OpenSea doesn't index the contract. Also check the wallet's OpenSea profile — if on-chain holdings show thousands of NFTs but OpenSea shows only a handful, the unindexed contracts are hidden.

**Red flags**:
- Contract returns 404 on OpenSea v2 API = not indexed, tokens invisible
- Wallet holds 2,200+ NFTs on-chain but only 9 visible on OpenSea = most contracts unindexed
- Platform operator wallet has near-zero ETH balance (0.0015 ETH) despite buying from 74 artists = funds swept out, not retained
- Brand-mimicking contract name (SuperRarer vs SuperRare) + unindexed on OpenSea = the platform operates entirely outside the standard NFT infrastructure

**Case Study: Chonkly/SuperRarer OpenSea invisibility**
- chonkly.eth holds ~2,200+ NFTs on-chain (SuperRarer: 1,804, Chonkly: 409)
- OpenSea shows only 9 tokens (the 4 real SuperRare + a few others from indexed collections)
- Both SuperRarer (0xc360ceca) and Chonkly (0x235f1802) return 404 on OpenSea v2 API
- Impact: "Sales" on these contracts have no external market visibility. No OpenSea collection page, no price history, no resale liquidity through the primary marketplace.
- This further diminished the @beam assessment — Chonkly sales are not just micro-priced and single-buyer, they're also invisible to the entire OpenSea ecosystem

**Case Study: @Metpenfaul**

When tracing ETH payments to artists, identify the sender contract to determine if it's a real marketplace payout:

- **SuperRare v1**: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d (name: "SupeRare", symbol: SUPR)
- **SuperRare v2**: 0xB932a7A1a7c1521A5F199CA0F (name: "SuperRareV2")
- **Foundation v1 proxy**: 0xcDA72070E455bb31C7690a170224cE43623D0B6f (AdminUpgradeabilityProxy, created Jan 2021). Receives NFTs from artists for listing, distributes to buyers. Internal ETH payouts from this address = Foundation sale proceeds.
- **Foundation v2**: 0x3B3ee1931Dc30F20FFA2Df07F88f93C1B0b94fC0
- **OpenSea (Seaport)**: 0x0000000000000068F116a894984e2DB1123eB395
- **Manifold ERC1155LazyPayableClaim**: 0x44e94034Afce2dD3Cd5Eb62528F239686FC8F162 — forwards edition drop sale proceeds to artist
- **Manifold ERC721LazyPayableClaim**: 0x7581871e1C11f85eC7F02382632b8574FAD11b22 — forwards ERC721 claim proceeds to artist
- **WETH**: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 — unwrapping WETH is NOT a sale

**Technique: Always investigate the buyer wallet, not just the sale.** When an artist has NFT transfers to a contract, identify the contract type:
1. Check `GET /api/v2/addresses/{addr}` — is it a contract? What's the balance?
2. Check `GET /api/v2/smart-contracts/{addr}` — what's the contract name? (e.g., "AdminUpgradeabilityProxy" = proxy pattern, "ERC1155LazyPayableClaim" = Manifold)
3. Check NFT flow: are NFTs going IN then OUT to many buyers? (marketplace escrow) Or accumulating? (collector)
4. Check if NFTs return to the artist: if 7 of 9 tokens sent to a contract come back, it was a listing that didn't sell, not 9 sales.
5. Check the end buyer: if a token does go to a real EOA, verify that EOA has no links to the artist or any suspect network.
6. **Exclude self-transfers from ETH revenue**: Before counting "incoming ETH", check whether the sender wallet is one of the artist's own consolidated wallets (same ENS root, same 6529 identity, or known self-wallets). Self-transfers between own wallets inflate gross ETH flows dramatically. Always calculate NET art revenue = (incoming from marketplaces + incoming from independent buyers) - (self-transfers + exchange withdrawals).
7. **Fetch ALL transaction pages** (2026-07-13, CRITICAL): Blockscout API paginates at 100 txs/page. Wallets with high activity can have 1,000+ txs (RD example: 1,808 txs across 18 pages). Only fetching page 1 massively undercounts ETH flows. ALWAYS loop through all pages until a page returns < 100 results. This applies to both `txlist` (ETH transfers) and `tokennfttx` (NFT transfers).
8. **Never report gross incoming ETH as a headline number** (2026-07-13): Gross incoming ETH includes exchange withdrawals, self-transfers, and personal funds — all meaningless for artist assessment. ONLY report ETH from marketplace contracts (OpenSea/Seaport, Foundation, Manifold, SuperRare) and verified direct art sales. Categorize every incoming tx by source before reporting anything. Exchange withdrawals and self-transfers should be counted separately and excluded from art revenue. Example: RD's gross incoming was 128K ETH but art marketplace revenue was 0 ETH — the 128K was just years of exchange withdrawals.

**Known marketplace contract addresses (for buyer wallet identification):**
- Foundation v1 proxy: 0xcda72070E455bb31C7690a170224cE43623D0B6f (AdminUpgradeabilityProxy, created Jan 2021) — escrows NFTs for listing, pays sellers via internal txs
- Foundation v2: 0x3B3ee1931Dc30F20FFA2Df07F88f93C1B0b94fC0
- Manifold ERC1155LazyPayableClaim: 0x44e94034afce2dd3cd5eb62528f239686fc8f162 — pays artists for edition drops
- Manifold ERC721LazyPayableClaim: 0x7581871e1c11f85ec7f02382632b8574fad11b22 — pays artists for ERC721 drops
- SuperRare v1: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d (name: "SupeRare", symbol: SUPR) — the REAL SuperRare, NOT to be confused with Chonkly's "SuperRarer"
- SuperRare v2: 0xB932a70A57673d89f4acFFBE830e8ED7f75fb9e0 (name: "SuperRareV2") — also real SuperRare
- Seaport (OpenSea): 0x00000000000001adF28eF1c7D0186488931B0b94fC0

### Social Links in Assessments (2026-07-13, CRITICAL)

**RD directive**: Social links (X, Instagram, email) should be noted as present in the assessment — that's it. Do NOT frame them as positive (verified, matching persona) or negative (unverified, possibly fake). We cannot verify social link authenticity from the server, so they are neutral information, not a signal in either direction.

**Rule**: When listing social links in an assessment:
- Note what links exist (platform, handle)
- Do NOT add "verified" or "unverified" or "may be fake"
- Do NOT count social links as a strength or a concern
- Do NOT include them in the "Why LIKELY_REAL" or "Why SUSPICIOUS" reasoning
- They are factual profile data, like the wallet address — present but not scored

### Single-Buyer Concentration (2026-07-13, REINFORCED)

**RD directive**: All sales going to one wallet is suspicious, even if that wallet is a platform operator. Do not dismiss single-buyer concentration as "just a platform bootstrap pattern" without investigating the buyer thoroughly.

**Rule**: When all or nearly all of an artist's sales go to one wallet:
1. Identify the wallet — is it a contract (marketplace) or EOA (person)?
2. If EOA: is it the platform deployer? Check contract creation.
3. Check if NFTs flow back to the artist (wash-trading cycle).
4. Check the buyer's relationship to other artists on the same platform.
5. Even if the buyer is a platform operator, flag this as a significant concern — it means the artist has zero independent market demand.

**Case Study: @Metpenfaul**
- Profile created 2026-07-13, but has 25,000 MemesNominee rep from @DarrenSRS (15K, L77) and @johndoe8891 (10K, L88)
- All 501 profile-logs are from 2026-07-12/13 — rep was NOT accrued today
- Rep categories show the 25K was given ~3 months ago under a previous identity
- Both wallets (0x63e80d active since Oct 2024, 0x8795d1 active since Jun 2026) consolidated under the new "Metpenfaul" identity today
- Previous identity handle: unknown (no HANDLE_EDIT found)
- Bridge wallet 0xdcf17058 connects to @kiramoto (whose profile was also created today)
- Both appeared in maybe's dive bar the same day, Metpenfaul claiming to be a previous collector

- **Full reference**: `references/kiramoto-metpenfaul-investigation.md` (kiramoto + metpenfaul connection, bridge wallet, hacked wallet verification, deconsolidation detection, riverryanvault.eth analysis, mintface.eth check)

### Rep Categories API

**Endpoint**: `GET /profiles/{profile_id}/rep/categories`

Also works with handle or wallet address as the path parameter.

Returns array of rep categories, each with:
- `category`: name (e.g., "MemesNominee", "Help6529 Credits", "Welcome to the Bar")
- `total_rep`: total rep in that category
- `contributor_count`: number of unique contributors
- `top_contributors`: array with `contribution` amount and full `profile` object (handle, level, rep, cic, tdh, classification)

**Use cases**:
1. **Detect rep from previous identities** — if contributors gave rep months ago but profile was created today, the wallet was previously consolidated under a different identity
2. **Rep concentration analysis** — if >70% of total rep comes from 1-2 contributors, the profile's support is narrow
3. **Identify who vouched for the artist** — top contributors' levels and classifications indicate whether established community members support them
4. **Check for MemesNominee rep** — the vetting cron gives 10K MemesNominee; if an artist already has 50K+ in that category, they don't need more

**PITFALL**: The rep categories endpoint works with wallet address too — `GET /profiles/0x.../rep/categories` returns the same data as by handle or profile_id. This is useful when the wallet had a previous identity (the rep follows the wallet).

### Bridge Wallet Methodology (Intermediary Connection Detection)

When checking if two profiles are connected, direct wallet-to-wallet transfers may not exist. A **bridge wallet** — a third EOA that receives funds from Profile A and later sends funds to Profile B — creates an on-chain link without direct transfers.

**Detection method**:
1. Fetch ALL incoming AND outgoing ETH transactions for both profiles' wallets
2. For each counterparty EOA of Profile A, check if that EOA also appears as a counterparty of Profile B
3. Specifically look for the pattern: Profile A → bridge wallet → Profile B (one-way funding chain)
4. Check timing: Did Profile A send to the bridge before the bridge sent to Profile B?

**Case Study: kiramoto ↔ Metpenfaul (bridge wallet 0xdcf17058)**
- Kiramoto sent 0.50 ETH to 0xdcf17058 (Jun 2023) and 0.04 ETH (Dec 2023)
- 0xdcf17058 sent 0.10 ETH back to kiramoto (Aug 2023) — partial round-trip
- 0xdcf17058 funded Metpenfaul's first wallet with 0.05 ETH (Oct 2024) — first tx ever for that wallet
- 0xdcf17058 funded Metpenfaul's second wallet with 0.08 ETH (Jul 2026) — 10 days before both profiles appeared in dive bar
- No direct ETH or NFT transfers between kiramoto and Metpenfaul wallets
- 0xdcf17058 has no 6529 profile, 8 unique recipients — personal wallet, not exchange
- Both profiles appeared in dive bar on the same day, both created 6529 profiles within hours
- Metpenfaul claimed to be a previous collector of kiramoto's work

**Assessment**: Bridge wallet pattern + simultaneous profile creation + claimed prior relationship = strong suspicion of coordination or same-person operation. Not conclusive alone, but combined with simultaneous appearance and the funding chain, it warrants flagging.

### Profile Creation Timestamp Artifacts (2026-07-13)

**PITFALL**: The `created_at` timestamp on a 6529 profile may reflect the most recent deconsolidation/reconsolidation event, NOT the date the user first appeared on 6529. A profile that "was created today" may have been posting on waves for days before that timestamp was set.

**Case Study: @Metpenfaul**
- Profile `created_at`: July 13, 2026 at 01:28 UTC
- But first dive bar post: July 9, 2026 (4 days earlier)
- The `created_at` was updated during the deconsolidation/reconsolidation process — switching old wallet out, new wallet in, getting the new "Metpenfaul" handle
- The profile-logs API confirmed all 501 logs started July 12-13 — but drops from July 9-11 are retroactively attributed to @Metpenfaul in the drops API

**Rule**: When reporting "profile created today," ALWAYS cross-check with the drops API (`GET /v2/waves/{wave_id}/drops?author={wallet}`) to see if the wallet was posting earlier. Do NOT say "both profiles created today, hours apart" if one of them has been posting for days. This creates a false impression of simultaneous arrival.

### Bridge Wallet Counterparty Deep-Dive (2026-07-13)

When investigating a bridge wallet, check ALL its counterparties — not just the two profiles being connected. Other counterparties can reveal:
- Additional funding sources (exchanges, other personal wallets)
- ENS names that may identify the bridge wallet owner or their associates
- Cross-chain bridge usage (LiFiDiamond, MayanSwift) indicating multi-chain activity
- Whether the bridge wallet is truly personal (small recipient count) or could be an exchange/shared wallet

**Case Study: Bridge wallet 0xdcf17058**
- 10 unique counterparties total
- Funded by: kiramoto (0.55 ETH), riverryanvault.eth (0.60 ETH), exchange hot wallet 0x4976a4a (0.2491 ETH, 23K ETH balance), 0x331d9a (0.1798 ETH)
- Used LiFiDiamond (cross-chain swap) and MayanSwift (cross-chain bridge) — indicating the owner is active across chains
- riverryanvault.eth: ENS-named NFT trader, 1,320 txs since Dec 2021, no 6529 identity — only sent 0.60 ETH to bridge once (Sep 2023)
- mintface.eth (0xd40B63bF04a44e43fBFE5784bCf22ACaAB34a180): Checked against all wallets in this investigation — NO interaction found. 4,055 txs, active NFT trader since Sep 2021.

### ENS Name Resolution via Blockscout (2026-07-13)

To resolve an ENS name to an address using Blockscout:
```
GET https://eth.blockscout.com/api/v2/search?q=mintface.eth
```
Returns `items[].address_hash` and `ens_info.name`. Works for any ENS name.

To search for a name fragment:
```
GET https://eth.blockscout.com/api/v2/search?q=mintface
```
Returns both ENS results and token/contract matches.

### Solana / Non-EVM Marketplace Checking (2026-07-13, UPDATED 2026-07-13)

**CRITICAL GAP**: The vetting script only scans Ethereum L1 + L2s (Base, Polygon, Arbitrum, Optimism, Zora) via Blockscout. Artists — especially from Southeast Asia — may have their primary art career on **Solana**, which is a completely separate blockchain ecosystem with its own NFT marketplaces (Exchange.art, Magic Eden, Tensor). Ethereum-only scanning will show near-zero sales for a Solana-established artist, producing a false "NEW" or "UNCLEAR" classification.

**PITFALL (user correction 2026-07-13)**: Do NOT judge an artist's activity level based on Ethereum alone. If ETH shows minimal sales but the artist claims to be established, CHECK SOLANA FIRST. Kiramoto appeared to have only 2 sales (0.20 ETH) on Ethereum — but had $44,648 in Exchange.art sales, 381 followers, and 140 NFTs on Solana. The ETH-only picture was misleadingly negative. That said, for 6529 nomination purposes, ETH L1 activity IS the most important signal — Solana activity is real but it's a different ecosystem. Note the gap but flag that ETH presence matters most for 6529.

**Case Study: @kiramoto**
- Ethereum scan: 2 OpenSea sales (0.20 ETH, March 2023). Looked like a dormant artist with minimal traction.
- Exchange.art (Solana): $36,679 USD total sales, 381 followers, profile created May 2022 (4+ years ago). Active art career on Solana.
- The artist's Ethereum wallet (0x86c0716633b9b78e377880bca3a404c2efcc178c) was linked to BOTH Exchange.art and 6529, confirming same person.
- Without checking Solana, the assessment would have been "LIKELY REAL with concerns about low sales" — the real picture is an established artist with meaningful revenue.

**Exchange.art API (reverse-engineered 2026-07-13)**

Exchange.art has no documented public API. The frontend is a JavaScript SPA (Angular). To search for artist profiles:

1. **Search by name/display name**:
   ```
   GET https://api.exchange.art/v2/profile?q={name}&from=0&limit=10&mode=search
   ```
   Returns `{count, profiles: [{profileType, metadata: {displayName, slug, description, createdAt, lastUpdatedAt, userId}, social: {website}, twitter: {handle, profileImage}, wallets: [solana_addr, eth_addr], totalSalesUsd, numFollowers}]}`

2. **Key gotchas**:
   - Controller path is `profile` (SINGULAR), not `profiles` — `/v2/profiles` is a different endpoint that requires `ids` (wallet addresses)
   - `mode` must be lowercase: `search` (not `SEARCH`)
   - Valid modes: `byDisplayName, byDisplayNameOnly, bySlug, byEmail, byWallets, admin, search`
   - `q` must be a string, not an array
   - The API returns both Solana and Ethereum wallet addresses in the `wallets` array
   - `totalSalesUsd` is the lifetime USD sales volume on Exchange.art
   - Cross-reference the Ethereum wallet with the 6529 consolidated wallet to confirm identity

3. **Get NFT IDs created by the artist**:
   ```
   GET https://api.exchange.art/v2/nft/ids/_createdBy?wallets={sol_wallet},{eth_wallet}
   ```
   Returns `{"nftIds": ["mint1", "mint2", ...]}`. Solana mints are base58 strings, Ethereum NFTs are `0x{contract}-{tokenId}` format.

4. **Get NFT IDs currently owned by the artist**:
   ```
   GET https://api.exchange.art/v2/nft/ids/_ownedBy?wallets={sol_wallet},{eth_wallet}
   ```
   Same format. Compare created vs owned to determine sell-through rate.

5. **Get NFT summaries (title, blockchain, token type, image)**:
   ```
   GET https://api.exchange.art/v2/nft/summary/_byNftIds?nftIds={id1},{id2},...
   ```
   Returns `{"nfts": [{image, title, id, blockchain, tokenType}]}`. Batch up to 20 IDs per call.

6. **Search for artist's collections/series**:
   ```
   GET https://api.exchange.art/v2/search/series?sayt={name}&from=0&size=50
   ```
   Returns `{"total": N, "collections": [{id, name, totalSalesUsd, artistProfile: {md: {slug}}}]}`.

7. **Get profile sales stats**:
   ```
   GET https://api.exchange.art/v2/activities/stats/profiles?profileIds={userId}
   ```
   Returns `[{"volumeCollectedUsd": N, "volumeSoldUsd": N}]`. The `userId` comes from the profile search response (`metadata.userId`).

8. **Get NFTs by series ID**:
   ```
   GET https://api.exchange.art/v2/nft/ids/_bySeriesId?seriesIds={seriesId}
   ```
   Returns a LIST of `{"nftId": "...", "seriesId": "..."}` objects (not a dict).

9. **Key analysis: sell-through rate**:
   - `created_ids - owned_ids = sold_ids` (NFTs created but no longer held = sold)
   - In the kiramoto case: 140 created, 138 sold (98.5% sell-through), 2 still held
   - High sell-through is notable — could mean strong demand OR low pricing

10. **Solana on-chain sale verification (via Solana RPC)**:
    - `getSignaturesForAddress` with `limit=1000` returns up to 1000 recent tx signatures (capped — older txs may be missed for active wallets)
    - `getTransaction` for each signature, check `meta.preBalances` vs `meta.postBalances` for the artist's wallet index
    - SOL incoming > 0.05 = likely a sale (filter out dust/mint fees)
    - **Rate limiting**: public Solana RPC (`api.mainnet-beta.solana.com`) aggressively rate limits (429). Use multiple RPC endpoints: `solana-rpc.publicnode.com`, `rpc.ankr.com/solana`
    - **Exchange.art program**: Most Exchange.art sales go through their escrow program (address starts with `exAuv` or `EXBuY`). The SOL may come from the program, not directly from the buyer — so checking payer wallets in the transaction won't always reveal the actual buyer
    - **Current NFT owner check**: `getTokenLargestAccounts` → `getAccountInfo` with `jsonParsed` encoding reveals the current token account owner. This is how to verify buyer diversity but is heavily rate-limited on public RPC
    - **Limitation**: The 1000-tx cap means artists active since 2022 will have incomplete history. The Exchange.art `totalSalesUsd` stat is cumulative and more reliable than on-chain sampling

11. **Activities endpoint is broken**: `GET /v2/activities/?userId={id}&type=sale` returns 500 Internal Server Error (as of July 2026). Cannot be used for sale-by-sale verification. Use the stats endpoint + sell-through calculation instead.

12. **Series endpoint requires POST**: `GET /v2/series/{id}` returns 405 Method Not Allowed. The series search (`/v2/search/series`) works with GET.

13. **NFT holder endpoint requires auth**: `GET /v2/activities/nftHolders` returns 401 JWT missing. Cannot check NFT holders via API — must use Solana RPC `getTokenLargestAccounts` + `getAccountInfo`.

**How the API was found**: The JS bundle at `https://cdn.exchange.art/production/main.{hash}.js` contains Angular service code. Search for `profilesController` to find the controller path (`"profile"`), then look for `getProfiles` method to find the HTTP call pattern. Search for `nftsController` (= `"nft"`, singular) to find NFT-related endpoints. The API base is `https://api.exchange.art/v2`.
- **Full reference**: `references/exchange-art-api.md` (API endpoints, response format, reverse-engineering method, NFT catalog endpoints, Solana RPC verification)
- **Solana on-chain verification**: `references/solana-onchain-verification.md` (RPC endpoints, rate-limiting strategy, sale detection, buyer identification, NFT owner tracking, sampling methodology)

**When to check Solana marketplaces**:
- Artist's Ethereum on-chain activity is very low (few sales, few mints) but they claim to be an established artist
- Artist is from Southeast Asia (Solana NFT culture is strong there)
- Artist mentions "Exchange.art" or other Solana marketplaces in their posts or bio
- Artist's Twitter bio references Solana or SOL
- The 6529 profile has an Ethereum wallet but the artist claims sales that don't appear on Ethereum

**Other Solana marketplaces to check** (not yet reverse-engineered):
- Magic Eden (magiceden.io) — largest Solana NFT marketplace
- Tensor (tensor.xyz) — Solana NFT trading platform
- OKX NFT (okx.com/nft) — multi-chain including Solana

### Output Formatting: English Only (REINFORCED 2026-07-13)

**PITFALL (user correction #2)**: User said "Please stay in English" when on-chain token names with non-ASCII characters (Cyrillic, CJK, combining diacritics from scam tokens) appeared in output. This was already flagged as bug #13 but the error recurred. 

**RULE**: This is a HARD output formatting rule, not a suggestion. Before presenting ANY on-chain data to the user:
1. Filter out token names containing non-ASCII characters entirely — replace with `[filtered]`
2. Do NOT include raw scam token names in any output format
3. This applies to terminal output, summaries, tables, and prose
4. When in doubt, strip to ASCII-only or omit

### Assessment Tone and Neutrality (2026-07-13, RD CORRECTIONS)

**PITFALL**: RD corrected two judgmental framings in the @beam assessment:

1. **Social links**: Do NOT frame social links as positive ("matching the artist persona") or negative ("may be fake", "unverified"). Social links are NEUTRAL DATA — note their presence, nothing more. We cannot verify authenticity from the server, so we should not score them in either direction. State: "Social links present (X, Instagram, email) — noted but not assessed for authenticity."

2. **Community rep motives**: Do NOT characterize why community members gave rep. Saying "rep from community being nice without researching" is judgmental on our part — we don't know why people gave rep. State the facts only: "86% from one supporter" or "narrow support base." Do not speculate about community members' research process or motives.

**RULE**: Assessments should be factual and non-judgmental. Report what is observable (rep concentration percentages, social link existence) without speculating about motives, research depth, or authenticity that we can't verify. Leave conclusions to RD.

### Self-Contradiction Pitfall (2026-07-13)

**PITFALL**: I reported "both profiles were created today, hours apart" while ALSO reporting that metpenfaul had been posting on 6529 waves since July 9 (4 days before the `created_at` timestamp). The user caught this contradiction: "Why do you say that both profiles were created today a few hours apart when you also say @metpenfaul showed up 3 days ago?"

**Root cause**: I treated the `created_at` timestamp as the date of first appearance without cross-checking against actual posting history. The `created_at` was updated during deconsolidation/reconsolidation, not the actual start of activity.

**Rule**: When reporting "profile created on X date," ALWAYS cross-check:
1. Fetch drops by the profile's wallet from all waves — are there posts before `created_at`?
2. If yes, report the EARLIEST post date as "first appeared on" and note that `created_at` reflects a profile update, not first activity
3. Do NOT use `created_at` as the sole basis for statements about when a profile "showed up" or "arrived"
4. **NEVER contradict yourself in the same report** by saying "profile created today" while also reporting activity from days earlier. The user WILL catch this. If a profile was posting on July 9 but `created_at` says July 13, say "first appeared July 9, profile timestamp updated July 13" — not "created today."

### Verifying Claimed Wallet Compromise (2026-07-13)

When a profile claims their old wallet was "compromised" or "hacked" (typically posted on 6529 Tech Feedback wave, `e933d8d6-0c78-4e8f-aa12-f67d8c11b4dc`), DO NOT take the claim at face value. Verify by checking the old wallet's on-chain activity AFTER the claimed compromise date.

**Methodology:**
1. Find the tech feedback post — search the Tech Feedback wave for drops by the profile's wallet. The post typically says "my old wallet was compromised X months ago" and asks how to link a new primary wallet.
2. Note the claimed compromise date (e.g., "2 months ago" from a July 9 post = ~May 2026).
3. Fetch ALL transactions for the old wallet via Blockscout v1 API (`?module=account&action=txlist&address={wallet}&sort=asc`).
4. Filter for transactions AFTER the claimed compromise date.
5. Categorize post-claim activity:
   - **NFT transfers out** (method `0x42842e0e` = `safeTransferFrom`, `0xf242432a` = ERC-1155 batch transfer) — could be hacker draining OR owner relocating
   - **`transferOwnership` calls** (method `0xf2fde38b`) on NFT contracts — deliberate owner action, unlikely a hacker would transfer contract ownership to the same owner's other address
   - **6529 delegation contract interactions** (`DelegationManagementContract` at `0x2202cb9c00487e7e8ef21e6d8e914b32e709f43d`, method `0x2a243ce7`) — the wallet is still being used for 6529 operations
   - **Current ETH balance** — if the wallet still holds ETH, it wasn't fully drained

**IMPORTANT (user correction 2026-07-13)**: Do NOT conclude "not hacked" just because the wallet has post-hack activity. A compromised wallet does not always mean total loss of access. The owner may still control the wallet after a partial compromise (e.g., phishing of a specific approval, shared key). Moving remaining NFTs, calling `transferOwnership`, and interacting with 6529 contracts after a hack is CONSISTENT with the owner salvaging what they can. Present the evidence factually — let RD draw the conclusion.

**Evidence to report (without drawing conclusions):**
- Wallet activity timeline after claimed compromise date
- Types of transactions (NFT transfers, contract interactions, ETH movements)
- Whether `transferOwnership` targets the same person's other wallets
- Current ETH balance
- Whether 6529 delegation/consolidation contracts were called

**Case Study: @Metpenfaul "hacked wallet" (0x63e80d)**
- Tech feedback post (SN 1186448, July 9): "My old wallet that is tied to my 6529 was compromised 2 months ago"
- Claimed compromise: ~May 2026
- Post-claim activity: May (massive NFT transfers out), June (NFT transfers to 3 contracts + `transferOwnership` on "1 of 1 Originals" to the new wallet 0x8795d1), July 10 (two calls to 6529's `DelegationManagementContract`)
- Current balance: 0.0098 ETH
- The `transferOwnership` on June 15 transferred contract ownership directly to Metpenfaul's new primary wallet (0x8795d1) — the same person's other wallet
- **Assessment**: Present as evidence. The owner appears to still have control of the wallet. RD's perspective: "The original wallet owner still has the ability to move what's left in a wallet." Do NOT conclude the hack didn't happen.

**6529 Tech Feedback Wave** (`e933d8d6-0c78-4e8f-aa12-f67d8c11b4dc`): Users post here when they have wallet/profile issues. Checking this wave for a profile's posts can reveal:
- Claims of wallet compromise (and the claimed date)
- Requests to change primary wallet
- Consolidation/deconsolidation guidance from RD or dev team
- The actual procedure used to migrate identities
- **RD himself may respond** with consolidation instructions (as he did for metpenfaul, SN 1186652)

## Newcomer Context

These are NEW people to 6529 — they may not have any rep, CIC, or TDH. The vetting should focus on:
1. Do they have an ETH wallet linked?
2. On-chain history — real activity? Existing NFT collections, sales to multiple buyers?
3. Social presence — real online footprint showing their work?
4. Profile wave content — actual artwork or just "GMeme" text?
5. Artwork originality — reverse image search, AI detection

Consolidation becomes relevant as people get more active and collecting. For newcomers, check social and ETH wallets for signs of being real.

**RD clarification (2026-07-12)**: Newcomers may not have rep, CIC, or TDH — those metrics aren't useful for vetting them. The purpose of the wave is for new people to earn enough rep to submit. Focus on: ETH wallet on-chain history, social presence, and whether posted artwork is original. Consolidation analysis becomes relevant later as people get more active.