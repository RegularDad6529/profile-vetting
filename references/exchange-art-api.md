# Exchange.art API Reference

Exchange.art is a Solana-based NFT marketplace. No public API documentation exists. This was reverse-engineered from the frontend JS bundle on 2026-07-13.

## Search for Artist Profile

```
GET https://api.exchange.art/v2/profile?q={name}&from=0&limit=10&mode=search
```

**Parameters:**
- `q` (string, required): artist name or display name
- `from` (int): pagination offset, default 0
- `limit` (int): max results, default 10
- `mode` (string, required): must be lowercase `search`

**Valid modes**: `byDisplayName, byDisplayNameOnly, bySlug, byEmail, byWallets, admin, search`

**Gotchas:**
- Controller path is `profile` (SINGULAR), not `profiles` — `/v2/profiles` is a different endpoint requiring `ids` (wallet addresses)
- `mode` must be lowercase — `SEARCH` returns 400
- `q` must be a string, not an array — `q[]=value` returns 400
- No authentication required for search

## Response Format

```json
{
  "count": 1,
  "profiles": [{
    "profileType": "artist",
    "metadata": {
      "createdAt": "2022-05-20T16:01:49.799Z",
      "displayName": "kiramoto",
      "slug": "kiramoto",
      "description": "draws cool stuff.",
      "lastUpdatedAt": "2024-07-15T00:12:52.449Z",
      "userId": "LPc5Q9L2bbfhkNlbyFwawwuEXy82"
    },
    "social": {
      "website": "https://lynkfire.com/kiramoto"
    },
    "twitter": {
      "handle": "kiramotosan",
      "profileImage": "https://pbs.twimg.com/..."
    },
    "wallets": [
      "ANME95tDDTEKrrLzPHwZnsgZJwS7Z1PPqLJgRexjZDJs",  // Solana
      "0x86c0716633b9b78e377880bca3a404c2efcc178c"      // Ethereum
    ],
    "totalSalesUsd": 36679,
    "numFollowers": 381
  }]
}
```

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `profileType` | string | "artist" or "collector" |
| `metadata.createdAt` | ISO date | When the Exchange.art profile was created |
| `metadata.displayName` | string | Display name |
| `metadata.slug` | string | URL slug (exchange.art/profile/{slug}) |
| `metadata.description` | string | Artist bio |
| `social.website` | string | Artist website |
| `twitter.handle` | string | Twitter handle (without @) |
| `wallets` | array | Both Solana and Ethereum wallet addresses |
| `totalSalesUsd` | number | Lifetime USD sales volume on Exchange.art |
| `numFollowers` | number | Follower count |

## Cross-Referencing with 6529

The `wallets` array may contain an Ethereum address that matches the artist's 6529 consolidated wallet. This confirms the Exchange.art profile and the 6529 profile are the same person.

## How the API Was Found

1. The frontend at exchange.art is an Angular SPA — no server-rendered content
2. The JS bundle is at `https://cdn.exchange.art/production/main.{hash}.js`
3. Search the bundle for `profilesController` — its value is `"profile"` (singular)
4. The `getProfiles` method calls `apiV2.get(`${profilesController}?${stringify(params)}`)` 
5. The API base is `https://api.exchange.art/v2`
6. Full endpoint: `https://api.exchange.art/v2/profile?q={name}&mode=search`

## NFT Catalog Endpoints

### Get NFT IDs Created by Artist

```
GET https://api.exchange.art/v2/nft/ids/_createdBy?wallets={sol_wallet},{eth_wallet}
```

Returns `{"nftIds": ["mint1", "mint2", ...]}`. Solana mints are base58 strings, Ethereum NFTs are `0x{contract}-{tokenId}` format. No auth required.

### Get NFT IDs Owned by Artist

```
GET https://api.exchange.art/v2/nft/ids/_ownedBy?wallets={sol_wallet},{eth_wallet}
```

Same format. Compare created vs owned to determine sell-through rate.

### Get NFT Summaries

```
GET https://api.exchange.art/v2/nft/summary/_byNftIds?nftIds={id1},{id2},...
```

Returns `{"nfts": [{image, title, id, blockchain, tokenType}]}`. Batch up to 20 IDs per call. `blockchain` is "solana" or "ethereum". `tokenType` is "MasterEditionV2" (Solana) or "ERC721" (Ethereum).

### Search Collections/Series

```
GET https://api.exchange.art/v2/search/series?sayt={name}&from=0&size=50
```

Returns `{"total": N, "collections": [{id, name, totalSalesUsd, artistProfile: {md: {slug}}}]}`. Filter results by `artistProfile.md.slug == target_slug` to find the artist's collections.

### Get Profile Sales Stats

```
GET https://api.exchange.art/v2/activities/stats/profiles?profileIds={userId}
```

Returns `[{"volumeCollectedUsd": N, "volumeSoldUsd": N}]`. The `userId` comes from the profile search response (`metadata.userId`). No auth required. This is the most reliable sales volume figure.

### Get NFTs by Series ID

```
GET https://api.exchange.art/v2/nft/ids/_bySeriesId?seriesIds={seriesId}
```

Returns a LIST of `{"nftId": "...", "seriesId": "..."}` objects (NOT a dict — code must handle list type).

## Sell-Through Rate Analysis

1. Fetch created NFT IDs via `_createdBy`
2. Fetch owned NFT IDs via `_ownedBy`
3. `sold = created - owned` (set difference)
4. Get summaries for sold NFTs to see titles, blockchains, token types
5. High sell-through (e.g., 138/140 = 98.5%) is notable — could mean strong demand or low pricing

**Case Study: kiramoto**
- 140 NFTs created: blue (47 editions), cinema (44), peach (36), plus 13 unique pieces
- 138 sold (98.5%), 2 still held
- $44,648 total volume sold (from stats endpoint), $5,985 collected
- One collection found: "kiramoto and friends" ($223 sales, 32 NFTs, collaborations)
- Most NFTs sold individually outside collections

## Solana On-Chain Sale Verification

### RPC Endpoints (rate-limited, use multiple)

```
https://api.mainnet-beta.solana.com      (main, aggressive 429 rate limiting)
https://solana-rpc.publicnode.com         (alternative)
https://rpc.ankr.com/solana               (alternative)
```

### Get Transaction Signatures

```json
{"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": ["{wallet}", {"limit": 1000}]}
```

Returns up to 1000 signatures. **Capped at 1000** — artists active since 2022 will have incomplete history. The oldest txs in the window show the start of visible activity, not the wallet's first ever tx.

### Check SOL Balance Change (Sale Detection)

For each signature, fetch the full transaction:
```json
{"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": ["{sig}", {"maxSupportedTransactionVersion": 0}]}
```

Check `meta.preBalances` vs `meta.postBalances` for the artist's wallet index. SOL incoming > 0.05 = likely sale. Check `preTokenBalances`/`postTokenBalances` for NFT transfers.

### Exchange.art Program

Most Exchange.art sales go through their escrow program (address starts with `exAuv` or `EXBuY`). The SOL may come from the program, not directly from the buyer. Payer wallets in the transaction won't always be the actual buyer.

### Current NFT Owner Check

```json
{"jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts", "params": ["{mint}"]}
```

Get the largest token account address, then:
```json
{"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo", "params": ["{token_account}", {"encoding": "jsonParsed"}]}
```

The `data.parsed.info.owner` field is the current NFT owner's wallet. Heavily rate-limited — add 2+ second delays between calls.

## Broken / Auth-Required Endpoints

- `GET /v2/activities/?userId={id}&type=sale` — returns 500 Internal Server Error (as of July 2026)
- `GET /v2/activities/nftHolders` — returns 401 JWT missing
- `GET /v2/series/{id}` — returns 405 Method Not Allowed (use POST or search endpoint)
- `GET /v2/nft` — returns 405 Method Not Allowed (use specific sub-endpoints)

## Controller Paths (from JS bundle)

```
profilesController = "profile"        (singular, NOT "profiles")
nftsController = "nft"               (singular)
seriesController = "series"
activitiesController = "activities"
stockController = "stock"
```

## When to Check Exchange.art

- Artist's Ethereum on-chain activity is very low but they claim to be established
- Artist is from Southeast Asia (Solana NFT culture is strong there)
- Artist mentions Exchange.art or Solana in posts/bio
- Artist's Twitter references Solana or SOL
- 6529 profile has an Ethereum wallet but artist claims sales not visible on Ethereum
- Artist's CIC statements mention Exchange.art