# Chonkly Platform Investigation (2026-07-13)

## Platform Overview

**chonkly.com** is a small NFT art marketplace built with Next.js + Convex backend.

### Contracts
- **SuperRarer** (0xc360ceca69988e39be18ddb89e69afcc33a3833a): 1,732 holders, 16,678 tokens. Main art collection. Mint fee: 0.001 ETH. 5% transaction fee.
- **Chonkly** (0x235f18021160bcd312c65496df1caf2b9ce5904d): 152 holders, 2,208 tokens. Secondary collection. Free minting. 5% transaction fee.
- **Both deployed by chonkly.eth (0x05df3e4b689124697b24e95be2f5604eb24791e7)**

### Technology Stack
- Frontend: Next.js (React SSR)
- Backend: Convex (prestigious-terrier-297.convex.cloud)
- Metadata storage: Convex cloud storage (`prestigious-terrier-297.convex.cloud/api/storage/{uuid}`)
- Token metadata: served from `chonkly.com/api/metadata/{token_id}` (Chonkly contract)

### Site Structure
- `/` — Landing page with "What's New" feed
- `/feed` — Artwork feed
- `/artists` — Artist directory (SPA, loads via JS)
- `/artwork/{slug}` — Individual artwork pages
- `/profile/{artist_name}` — Artist profiles (SPA)
- `/playground` — CHONK interactive art creation tool
- `/editorials` — Vibe coding articles
- `/birthplace-of-vibe-coding` — Backstory page
- `/chonk` — "What is a CHONK?" explainer
- `/about` — Mission statement
- `/contact` — Contact info (noah@chonkly.com)

### Social Presence
- **No Discord** — no link on any page
- **No Telegram** — no link on any page
- **No Farcaster/Lens** active channel
- **No Linktree** — linktr.ee/chonkly returns 404
- **Twitter @chonkly** = YULIARTO CHONKLY, Jakarta, Indonesia. 1 follower, 0 following, joined Oct 2011. Dormant — not an active platform account.
- **Contact**: noah@chonkly.com
- **Warpcast**: /chonkly returns 200 but content is generic Farcaster shell — no active channel

### Persona
- "Built with real cowboy code by Big Dingus"
- "Dingus-grade Security™"
- "Birthplace of Vibe Coding" mythology
- CHONK = "Concatenated HTML Open Network Kernel"

### Community
The community lives entirely on chonkly.com (profiles, feed, marketplace) and on adjacent communities like 6529.io. No dedicated external chat. The 13 6529 artists use the 6529 dive bar as their social layer.

## SuperRarer Holder Distribution Analysis

This is the key analysis that distinguishes a real platform from a sybil ring.

### Distribution (all 1,732 holders)
- **1 token**: 769 holders (44%)
- **2-3 tokens**: 431 holders (25%)
- **4-10 tokens**: 281 holders (16%)
- **11-50 tokens**: 210 holders (12%)
- **51-100 tokens**: 18 holders
- **101-500 tokens**: 20 holders
- **500+ tokens**: 3 holders

**Median: 2 tokens. Mean: 9.6 tokens.** This is a genuine long-tail — mostly people who minted 1-2 pieces and stayed. Not a wash-trading pattern (concentrated balances would indicate circular activity).

### Top Holders
1. chonkly.eth (0x05df): 2,306 tokens (13.8%)
2. 0xF977814e90dA44: 1,283 tokens (7.7%) — **Binance hot wallet** (tokens custodied on exchange)
3. 0xEED964966: 503 tokens
4. 0xFc10BA6a: 411 tokens
5. 0x0000...dead: 401 tokens (burned)
6. 0x7566eFeB: 265 tokens
7. 0xAB665A70: 243 tokens
8. 0x7B3f9b51: 218 tokens
9. 0x71ba127F: 212 tokens
10. ooakosimo.eth: 202 tokens

**Top 10 own 36.2% of all tokens** — moderately concentrated but not extreme for a small platform.

## chonkly.eth — Platform Operator Purchase Pattern

### Buy-and-Hold (NOT Pass-Through)

**Key question investigated**: Is chonkly.eth buying and reselling (pass-through) or accumulating?

**Answer: Accumulator.** chonkly.eth:
- Received 772 SuperRarer tokens from 74 unique sellers
- Sent back only 89 (12% return rate)
- Also minted 265 tokens directly (from 0x0 address)
- Current balance: 2,306 tokens (net accumulation)

If it were a pass-through, OUT flows would match IN flows and tokens would distribute to many end-buyers. They don't — chonkly.eth holds.

### Purchase Method

chonkly.eth calls `buyToken()` directly on the SuperRarer contract:
- Method ID `0x6a627842` = `mint(address)` — artists minting their own work (free, 0 ETH value)
- chonkly.eth transactions to the contract include ETH value (0.005-0.015 ETH per purchase)
- NFT transfer events fire from the artist's wallet to chonkly.eth

**ALL recent SuperRarer contract transactions are mint calls** — 99 of 100 in the last batch were `0x6a627842` (mint), 1 was `0x23b872dd` (transferFrom). This confirms artists are actively minting new work.

### Purchase Prices
Micro-prices: 0.000 to 0.015 ETH per piece. This is a bootstrap liquidity pattern — the operator buys at very low prices to give artists sale history.

### Seller Diversity
74 unique wallets sold to chonkly.eth. The 13 6529 artists are a small subset:
- 0x71ba127F: 62 tokens sold (non-6529 artist)
- 0x3b176566: 47 tokens sold (non-6529 artist)
- CnNymphs (0x5dea037): 36 tokens sold
- StarWalkar (0x395785ab): 29 tokens sold
- 0x2c3ef1f3 (ooakosimo.eth): 24 tokens sold (non-6529)
- 0x9ec05fa3: 24 tokens sold (non-6529)
- Bubblezzz (0x829a5a3): 22 tokens sold
- 0xb85110fa: 17 tokens sold (non-6529)
- Beam (0xf3a78c34): 11 tokens sold

### Chonkly Contract Holdings
chonkly.eth holds 409 Chonkly tokens (18.5% of 2,208 total). Same buy-and-hold pattern on the secondary collection.

## Method ID Reference for Contract Analysis

When analyzing NFT contract transactions via Blockscout:
- `0x6a627842` = `mint(address)` — artists minting (usually 0 ETH value)
- `0xa223e05d` = `listToken(uint256,uint256)` — artist listing for sale
- `0x4a8c3b34` = `buyToken(uint256)` — buyer purchasing a listed token
- `0x2eb2a065` = `unlistToken(uint256)` — artist removing listing
- `0x23b872dd` = `transferFrom(address,address,uint256)` — direct transfer
- `0x42842e0e` = `safeTransferFrom(address,address,uint256)` — safe transfer
- `0xf24d1b82` = `safeTransferFrom` (ERC-1155 variant)

## How to Trace Whether a Buyer Is Pass-Through or Accumulator

1. **Fetch all NFT transfers for the buyer wallet**: `GET https://eth.blockscout.com/api/v1?module=account&action=tokennfttx&address={buyer}&sort=desc` (multiple pages, 100 per page)
2. **Separate IN vs OUT**: `to == buyer` = received (bought), `from == buyer` = sent (resold/returned)
3. **Calculate return rate**: OUT / IN. <15% = accumulator. >80% = pass-through.
4. **Check unique sellers**: How many different wallets sold TO the buyer? If 74 sellers, it's a platform pattern. If only the 13 suspected profiles, it could be a ring.
5. **Check transaction method**: Look at `txlist` for the contract — are buyer transactions calling `buyToken()` with ETH value, or are they direct `transferFrom` calls with 0 ETH?
6. **Check if buyer = contract deployer**: If the deployer is also the sole buyer, it's a platform operator bootstrap pattern.

## How to Analyze Holder Distribution

1. **Fetch all holders**: `GET https://eth.blockscout.com/api/v1?module=token&action=getTokenHolders&contractaddress={contract}&page=1&offset=100` (iterate pages until empty)
2. **Bucket by balance**: 1 token / 2-3 / 4-10 / 11-50 / 51-100 / 101-500 / 500+
3. **Check median and mean**: Median of 2 with 44% holding exactly 1 token = genuine long-tail platform. Median of 50+ with all holders having 100+ = possible ring.
4. **Identify exchange hot wallets in top holders**: Check top 5-10 holders on Blockscout v2 (`/api/v2/addresses/{addr}`) — look for known exchange addresses (Binance 0xF977814, 0x28c6c062; Coinbase 0xdfd5293d). Exchange-held tokens are custodied for users, not owned by the exchange.

## 6529 Profiles on Chonkly

13 6529.io profiles also mint on the Chonkly/SuperRarer contracts. They are independent platform users who found 6529 at different times over 14+ months.

### Chonkly Artist Names (on-chain metadata)
| 6529 Handle | Chonkly Artist Name | Sample Artwork |
|---|---|---|
| @Beam | Beam | "Treasure in Wasteland" |
| @Bubblezzz | ItBubblezzz | "In Bloom" |
| @Ordinaryartist | OrdinaryArtist | "GAME ON" |
| @CnNymphs | CnNymphs | "Electric Coordinates" |
| @StarWalkar | Coach_Ambiguous | "GG (Get Glazed) Vaxxine Dream" |
| @Niniola4u | NiNiOLA | "When the Night Listens" |
| @XON | Xon | "Catch The Sun" |
| @Rueby | Rueby | "Eternal State of Bloom" |
| @9GreenRats | 9GreenRats | "I Surrender (Interactive Particle Animation)" |
| @Temi | Temi | "Between Us" |
| @Tejiri | Tejiri5 | "Beauty of galaxy" |
| @Bahar_psh | Bahar | "Sweet dreams in a cup" |

### `created_at` vs Real Timeline
The `created_at` field on all 13 profiles showed a 4.5-second window (12:19:20-12:19:34 UTC on July 13, 2026). This was a **batch system event** (deconsolidation/migration), not actual profile creation.

Real timeline from CIC statement dates:
- Rueby: May 2025 (14 months before `created_at`)
- XON, StarWalkar: Jun 2025 (13 months)
- 9GreenRats: Sep 2025 (10 months)
- Niniola4u: Jan 2026 (6 months)
- Bubblezzz, Ordinaryartist, Temi, CnNymphs, Tejiri, Bahar_psh: Feb 2026 (5 months)
- Curtisforfun: Jul 4, 2026 (9 days)
- Beam: Jul 10, 2026 (3 days)

## chonkly.eth — Platform Operator Details

- **Address**: 0x05df3e4b689124697b24e95be2f5604eb24791e7
- **ENS**: chonkly.eth
- **Role**: Deployed both contracts, is the primary buyer for all artists
- **Funded by**: 0x80cccd71 (old wallet from April 2019, separate from all artists)
- **6529 profile**: Auto-ID only (L0, no handle)
- **Pattern**: Buys SuperRarer and Chonkly NFTs from all platform artists at micro-prices (0.005-0.015 ETH). Accumulates (holds 89% of purchases). Some NFTs flow back to artists (12% return rate).

## Investigation Methods Used

### Finding the platform website
1. Fetch contract source code: `GET https://eth.blockscout.com/api/v2/smart-contracts/{contract}`
2. Search for base URI in source: `_baseTokenURI = "https://chonkly.com/api/metadata/"`
3. Visit the URL — confirmed live marketplace

### Checking platform scale
1. `GET https://eth.blockscout.com/api/v2/tokens/{contract}` → `holders_count` = 1,732
2. Fetch all holders via v1 API, bucket by balance, check distribution
3. Sample random token metadata to confirm many different artists
4. Check for artist profile pages, feed, marketplace functionality

### Checking for external community
1. Scrape all site pages for Discord/Telegram/social links
2. Check `/contact`, `/about`, footer
3. Try common paths: `/community`, `/discord`, `/telegram`, `/chat`
4. Check Linktree (linktr.ee/{name}), Farcast (warpcast.com/{name})
5. Search for Twitter account from meta tags (twitter:creator)

### Verifying artist identity on platform
1. Fetch token metadata: `GET https://eth.blockscout.com/api/v2/tokens/{contract}/instances/{token_id}`
2. Check `metadata.attributes` for `Artist` trait — gives platform username
3. Try `chonkly.com/profile/{artist_name}` — confirms profile exists

### Tracing purchase mechanics
1. Fetch buyer's NFT transfer history (tokennfttx, multiple pages)
2. For each transfer IN, get the transaction hash
3. Fetch transaction details: `GET /api/v2/transactions/{hash}`
4. Check if `to` address = contract address (direct buyToken call) or different (intermediary)
5. Check ETH value sent — non-zero = purchase, zero = free transfer
6. Fetch contract txlist to see method IDs: `GET /api/v1?module=account&action=txlist&address={contract}`

### Checking for Convex backend API
- Chonkly uses Convex (prestigious-terrier-297.convex.cloud)
- Convex query API: POST to `/api/query` with `{"path": "functionName", "args": {}}`
- Function names are not publicly documented and error messages are generic ("Server Error")
- The Next.js JS bundles may contain function names but they're minified
- In practice, the on-chain metadata is more reliable than trying to reverse-engineer the Convex API

## Key Takeaway

When a shared NFT contract appears across multiple 6529 profiles:
1. Check holder count — 1,732 = platform, 13 = possible ring
2. Check holder distribution — long-tail (44% with 1 token, median 2) = real platform. Concentrated = possible ring.
3. Check for website — live marketplace = real platform
4. Check if deployer = buyer — platform operator bootstrap pattern
5. Check purchase pattern — accumulator (holds 88%+) = operator supporting artists. Pass-through (resells 80%+) = possible money laundering.
6. Check seller diversity — 74 unique sellers = real platform. Only 13 = possible ring.
7. NEVER assert "batch creation" from `created_at` alone — cross-check with CIC dates
8. A single buyer for all artists on a small platform is operator behavior, not sybil