# ENS Subgraph — Wallet Discovery for 6529 Profiles

## Problem
6529 profiles cap at 3 consolidated wallets. Users often have 4-10+ wallets (ENS names, side wallets, project wallets, organizational wallets). Missing unconsolidated wallets can hide the majority of on-chain activity.

## Solution
Query the ENS subgraph for all domains owned by each known wallet address.

## API
```
POST https://api.thegraph.com/subgraphs/name/ensdomains/ens
Content-Type: application/json
```

### Query all ENS names owned by a wallet
```json
{
  "query": "{ domains(where: {owner: \"<WALLET_ADDRESS>\"}) { name resolvedAddress { id } } }"
}
```

### Response
Returns array of domains with:
- `name` — ENS name (e.g., "blocknoob.eth", "6529complaints.eth")
- `resolvedAddress.id` — the address this ENS name resolves to (may differ from owner — points to another wallet)

### Workflow
1. Get all wallets from 6529 profile (`GET /identities/{handle}`)
2. For each wallet, query ENS subgraph for owned domains
3. For each domain's `resolvedAddress`, check if it's a NEW wallet not in the profile
4. For each new wallet, fetch NFT transfers, tx history, deployed contracts
5. Aggregate all collections and activity across ALL wallets

## Examples from 2026-07-13 session

### blocknoob
- 6529 profile: 3 wallets (vault.blocknoob.eth, memes.blocknoob.eth, noobmuseum.eth)
- ENS subgraph found 13 ENS names across 8 wallets:
  - blocknoob.eth (original, Jan 2021) — 1,692 NFT transfers, NOT in profile
  - 6529complaints.eth — community operations wallet
  - crypt.blocknoob.eth — separate collection wallet
  - giveaways.6529complaints.eth, rememes.6529complaints.eth — subdomain wallets
  - 6529arcade.eth, nftcomplaints.eth, fortune40under40.eth, etc. — resolve to blocknoob.eth
- Total across all 8 wallets: 2,667 NFT transfers, 307 unique collections
- Profile-only view: ~359 transfers — missed 87% of activity

### david
- 6529 profile: 3 wallets (0x2050fae0, punk8164.eth, 0xfb47b2ca)
- ENS subgraph found 5244.eth (owned by 0xfb4 wallet)
- 5244.eth has 900 NFT transfers — not in profile
- Total across 4 wallets: 4,790 NFT transfers, 568 unique collections

## ENS subgraph limitations
- Only finds ENS names owned by the queried address
- Does not find non-ENS wallets (raw addresses without ENS names)
- Does not find wallets on other chains (Base, Arbitrum, etc.)
- Some ENS names may have expired (no resolver set)
- Blockscout's eth-rpc does NOT resolve ENS names reliably — use the Graph API instead

## Primary: 6529 Delegations API (pitfall #33b)
The MOST RELIABLE way to discover delegated wallets is the 6529 API:
```
GET /api/delegations/{wallet}
```
- Takes wallet as a PATH parameter (not query — query filters are broken)
- Returns all delegations with `from_address`, `to_address`, `collection`, `use_case`, `all_tokens`, `expiry`
- Use cases: 1=primary address, 2=sub-delegation, 3=consolidation, 998=custom
- Delegated wallets should be treated as consolidated for assessment purposes
- Delegated wallets may have NO ENS name at all — the API is the only way to find them

Example: RegularDad's profile has 3 wallets. `GET /api/delegations/0xd0b53c87...` (safe.regulardad.eth) returned 2 wallets with use_case 998 that had no ENS names.

Example: Giopetto had 3 profile wallets, no delegations found, but ENS subgraph found 🇷🇸3.eth (owned by hot.giopetto.eth wallet, resolves to separate address).

## Discovery Priority
1. **6529 API `/api/delegations/{wallet}`** — primary method, finds delegated wallets even without ENS
2. **ENS subgraph owner lookup** — finds ENS names owned by profile wallets
3. **ENS subgraph name lookup** — if handle matches ENS pattern, search by name directly (pitfall #34)
4. **ENS subgraph subdomain search** — `name_ends_with: ".<ens>.eth"` for subdomains

## Alternative: Blockscout ETH recipient analysis
For non-ENS wallets, analyze top ETH recipients from the primary wallet:
- Frequent bidirectional ETH flows suggest self-wallets
- ENS names on recipient wallets confirm ownership
- Contract recipients (WETH, OpenSea, Foundation) are marketplaces, not self-wallets