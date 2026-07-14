# On-Chain Analysis Pitfalls (Updated 2026-07-13)

## ETH Flow Analysis

### Never report gross ETH
- Gross incoming ETH is meaningless — includes exchange withdrawals, DeFi trading, WETH wraps, DEX swaps
- Only report ETH from marketplace contracts and verified direct art sales
- RegularDad example: 128K ETH gross included FTX/Kraken withdrawals, WETH wraps, DEX swaps — 0 ETH art marketplace revenue

### Marketplace flow is bidirectional
- Always report NET (payouts received minus ETH sent to marketplace)
- Gross payout alone is misleading
- blocknoob example: 191K ETH received from Foundation but 270K ETH sent TO Foundation — net -79K ETH (net buyer, not net seller)

### Foundation bid escrow inflates gross flows
- ETH is locked when bidding and returned if outbid
- Never show gross ETH figures for Foundation
- Only show NFT counts (bought/sold/held) and net position

### Self-transfers inflate ETH revenue
- Check whether sender wallet is one of the artist's own consolidated wallets (same ENS root, same 6529 identity)
- Exclude self-transfers from ETH revenue calculations

### Full pagination required
- Blockscout API paginates at 100 txs/page
- Fetch ALL pages — loop until a page returns <100 results
- Applies to both ETH txs and NFT transfers
- RegularDad example: 1,808 transactions across 18 pages — only page 1 was fetched initially

## NFT Collection Analysis

### NET HELD methodology (CRITICAL)
- Raw transfer counts are inflated by self-moves, sales, and burns
- Formula: `net_held = IN - OUT_to_self_wallets - OUT_to_others - OUT_to_burn`
- Report collections by net held, not by transfer event count
- david example: ENS showed 238 transfers but only 20 held. CloneX showed 78 transfers but 0 held (sold all).

### Top 3 most expensive purchases + sales (2026-07-13)
Every collector activity section must include:
- **Top 3 purchases**: Match ETH outgoing txs to NFT incoming txs by block number. Sort by ETH value, take top 3.
- **Top 3 sales**: Match ETH incoming (regular + internal txs) to NFT outgoing txs by block number. Sort by ETH value, take top 3.
- Include: collection name, token ID, ETH price, date
- Example: deeze top purchase = Skulls of Luci #45 at 62 ETH, top sale = Moonbirds #7237 at 38.56 ETH

### Collector collection selection criteria
- Comprehensive list sorted by net held
- Include 6529 ecosystem separately
- Include established art platforms (Art Blocks, SuperRare, Foundation, BrainDrops)
- Any collection with 10+ net held
- Show "most flipped" (bought then sold to others) separately

### Self-transfers in NFT counts
- Exclude transfers between subject's own wallets when reporting "held" or "sold"
- blocknoob example: 84 Foundation NFTs "sent out" but 66 were to his own wallets — only 18 actually sold

### Burns ≠ sales
- NFTs sent to 0x0000000000000000000000000000000000000000 are BURNED, not sold
- Check recipient address before classifying as "sold"
- david example: 85 death and taxes citizens were burned (game mechanic: burn citizen → mint evader at same timestamp), not sold

## Contract Verification

### Minting from 0x0 ≠ creating the contract
- Check who DEPLOYED the contract, not just who minted from 0x0
- Always verify contract creator address via Blockscout v2: `GET /api/v2/addresses/{contract}` → `creator_address_hash`
- david example: minted 172 "death and taxes" NFTs from 0x0 but the contract was created by a separate factory (0x3b3B425b...) — he's a collector, not the artist
- deeze example: "Burnt Boy by Deeze x Goonz" had deeze's name but contract was deployed by Goonz (0x19D38600...)

### Blockscout v2 /creator endpoint returns 404
- Use `GET /api/v2/addresses/{address}` instead — returns `creator_address_hash` directly
- The `/api/v2/smart-contracts/{address}/creator` endpoint 404s for many contracts

### SuperRarer ≠ SuperRare
- SuperRarer (0xc360ceca, SRR) is a Chonkly knockoff with deliberate brand mimicry (one extra 'r')
- SuperRare v1 (0x41A322, SUPR) is the real contract
- SuperRareV2 (0xB932a70A) is the real v2 contract
- Always verify contract ADDRESSES, not just names

### OpenSea indexing check
- Contracts returning 404 on OpenSea v2 API are invisible to standard market
- Both Chonkly contracts (SuperRarer, Chonkly) are NOT indexed on OpenSea

## Wallet Discovery

### ENS subgraph for unconsolidated wallets
- 6529 profiles cap at 3 wallets, but users often have more
- Query ENS subgraph: `api.thegraph.com/subgraphs/name/ensdomains/ens`
- Search by each known wallet address as owner
- Check `resolvedAddress` for each domain — some ENS names resolve to different wallets
- blocknoob example: 6529 profile shows 3 wallets but actually has 8+ (found via ENS subgraph)

### Check each linked wallet for a 6529 profile
- After discovering wallets via ENS subgraph, check each via `GET /identities/{address}`
- If a linked wallet has its own 6529 profile, include it: handle, level, classification
- Do NOT speculate on identity links between profiles based on transactions alone
- blocknoob example: blocknoob.eth has separate profile @famous (L6)

## 6529 API Issues

### Drops API author_handle filter is BROKEN
- `author_handle` and `identity_id` params on `GET /drops` do NOT filter by author
- They return global recent drops from random people
- Do NOT use them to find an artist's wave posts

### Correct method for wave activity: activity API
- `GET /identities/{handle}/activity` returns `{last_date, date_samples}`
- `date_samples` is a 365-element array of daily drop counts
- Non-zero entries = active days
- Example: deeze showed 0 active days out of 365 — zero wave activity

### Other broken API endpoints
- `?search=`, `?type=`, `?classification=` return 400
- Blockscout v2 holdings API pagination broken (max 50 tokens, cursor doesn't work)
- Blockscout v2 `/smart-contracts/{addr}/creator` returns 404 — use `/v2/addresses/{addr}` instead

## Known Marketplace Contract Addresses
- Foundation v1: 0xcda72070e455bb31c7690a170224ce43623d0b6f (AdminUpgradeabilityProxy, Jan 2021)
- Foundation v2: 0x3B3ee1931DC30F20fFA2dF07F88F93C1B0b94FC0
- Manifold ERC1155: 0x44e94034afce2dd3cd5eb62528f239686fc8f162
- Manifold ERC721: 0x7581871e1c11f85ec7f02382632b8574fad11b22
- SuperRare v1: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d
- SuperRareV2: 0xB932a70A4aE49c32c3e8Bd39B71aE8F4eEAC8d44
- Seaport: 0x00000000000001adF28D8d34C5Ded8e3BC9D1Acd
- OpenSea Wyvern: 0x7be8076f4ea4b96b62c43e4a9c3a3b87e2f7c1f2
- Chonkly SuperRarer (NOT SuperRare): 0xc360ceca69988e39be18ddb89e69afcc33a3833a
- Chonkly: 0x235f18021160bcd312c65496df1caf2b9ce5904d