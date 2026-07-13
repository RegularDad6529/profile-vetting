# 6529 Artist Vetting — Pitfalls & Lessons Learned

## Critical Errors (avoid repeating)

### 1. Check 6529 API artist fields FIRST (2026-07-13)
Before any on-chain wallet analysis, check the 6529 profile for:
- `artist_of_prevote_cards`: Array of Meme Card numbers → recognized 6529 artist
- `winner_main_stage_drop_ids`: Array of Main Stage drop IDs → ESTABLISHED artist. Fetch each via `GET /drops/{id}` for title/ratings
- `is_wave_creator`: Boolean → community leadership
- `active_main_stage_submission_ids`: Current submissions

If ANY are non-empty, the profile is a confirmed artist. On-chain wallet analysis is supplementary, not the primary source. Example: @arsonic was initially misclassified as "not an artist" because the on-chain review only looked at personal wallet NFT transfers and missed collaborative wallets. The 6529 API showed 2 Main Stage wins and Meme Card #37.

### 2. Check collaborative wallets (2026-07-13)
Artists may deploy work from collaborative wallets (e.g., @zeeblocks uses ze-blocks.eth for Pebbles on NextGen 6529). If an artist mentions a duo or collective, search for the collaborative wallet and check ETH transfers between wallets for revenue sharing patterns.

### 3. Exclude self-transfers from ETH revenue (2026-07-13)
Before counting "incoming ETH", check whether the sender wallet is one of the artist's own consolidated wallets (same ENS root, same 6529 identity, or known self-wallets). Self-transfers between own wallets inflate gross ETH flows dramatically. Always calculate NET art revenue = (incoming from marketplaces + incoming from independent buyers) - (self-transfers + exchange withdrawals).

### 4. Fetch ALL transaction pages (2026-07-13)
Blockscout API paginates at 100 txs/page. Wallets with high activity can have 1,000+ txs (RD example: 1,808 txs across 18 pages). Only fetching page 1 massively undercounts ETH flows. ALWAYS loop through all pages until a page returns < 100 results. This applies to both `txlist` (ETH transfers), `txlistinternal` (internal txs), and `tokennfttx` (NFT transfers).

### 5. Never report gross incoming ETH as headline (2026-07-13)
Gross incoming ETH includes exchange withdrawals, self-transfers, and personal funds — all meaningless for artist assessment. ONLY report ETH from marketplace contracts (OpenSea/Seaport, Foundation, Manifold, SuperRare) and verified direct art sales. Categorize every incoming tx by source before reporting anything. Example: RD's gross incoming was 128K ETH but art marketplace revenue was 0 ETH — the 128K was just years of exchange withdrawals.

### 6. Separate artist sales from collector resales on Foundation (2026-07-13)
Foundation v1 proxy pays out both primary artist sales AND secondary market resales. A single 21K ETH payout may be a collector flipping someone else's art (e.g., Sebastiao Salgado photography), not artist revenue. Track which NFTs were sent to Foundation and whether they returned (unsold listing) or stayed (sold). Cross-reference with mint patterns: if the artist minted the collection from 0x0, it's their art; if they received it from another wallet or contract, it's a collected piece being resold. Always label Foundation revenue as "mix of artist sales and collector resales" when both are present.

### 7. SuperRarer ≠ SuperRare (2026-07-13, CRITICAL)
"SuperRarer" (0xc360ceca, symbol SRR) is a Chonkly platform contract, NOT SuperRare (0x41A322, symbol SUPR) or SuperRareV2 (0xB932a7). Deployed by chonkly.eth. NOT indexed on OpenSea. Always verify contract ADDRESSES, not just names. This caused Beam and Jpearlking assessments to incorrectly credit "SuperRare mints" when all transfers were on the Chonkly knockoff.

### 8. Find unconsolidated wallets via ENS subgraph (2026-07-13, CRITICAL)
6529 profiles cap at 3 wallets, but users often have more. Query the ENS subgraph for all domains owned by each known wallet:
```
POST https://api.thegraph.com/subgraphs/name/ensdomains/ens
{"query": "{ domains(where: {owner: \"<wallet>\"}) { name resolvedAddress { id } } }"}
```
This finds ENS names resolving to additional wallets not in the profile. Examples:
- blocknoob: 6529 profile has 3 wallets, ENS subgraph found 8 total (blocknoob.eth with 1,692 NFT transfers was missing)
- david: ENS subgraph found 5244.eth (900 NFT transfers) owned by 0xfb4 wallet, not in profile

Always run ENS subgraph lookup as a separate step AFTER fetching the 6529 profile.

### 9. Foundation bid escrow inflates gross flows (2026-07-13)
Foundation's bidding mechanism locks ETH when a bid is placed and returns it if outbid. This creates huge bidirectional flows that aren't real purchases/sales. NEVER show gross ETH figures for Foundation. Only show:
- NFT counts (bought, sold, still held)
- Net position (positive = net seller, negative = net buyer)

Example: blocknoob appeared to have 191K ETH "revenue" from Foundation and 270K ETH "sent to" Foundation. Both numbers are inflated by bid escrow. The real picture: 150 bought, 84 sold, 66 held, net negative.

### 10. Marketplace flow is bidirectional — always report NET (2026-07-13)
Never report only the incoming side of marketplace ETH flow. Calculate NET = (received from marketplace) - (sent to marketplace). Reporting only incoming creates false "revenue" figures.

Same error class as RegularDad's gross ETH: only looking at one direction of a two-way flow.

### 11. Collector collection selection — be comprehensive (2026-07-13)
When listing collector activity across ALL wallets, include:
- Total NFT transfers and unique collection count
- Notable collections by volume OR significance (not just transfer count)
- 6529 ecosystem collections separately (dwellers, 6529 Gradient, Karen Army, NextGen 6529)
- Established art platforms (Art Blocks, SuperRare, Foundation, BrainDrops)
- ENS holdings if significant
- Any collection with >10 transfers
- Real SuperRare vs SuperRarer/Chonkly explicitly stated

### 12. Manifold EIP1167 proxy contracts (2026-07-13)
Artists may mint via Manifold proxy factories (EIP1167 minimal proxy pattern). These show up as:
- Contract type "eip1167" on Blockscout
- No creator address (proxy deployed by factory, not artist)
- NFT mints from 0x0 to artist wallet
- 0 NFT transfers visible on Blockscout for the contract itself

Do NOT conclude "zero artist output" because the proxy has 0 indexed transfers. The artist's mint pattern (from 0x0) IS the evidence of creation. Example: david's "death and taxes: citizens/evaders" (172 minted via Manifold proxies, 86 distributed via direct transfer).

### 13. Check OpenSea indexing status (2026-07-13)
Contracts returning 404 on OpenSea v2 API are invisible to the standard NFT market. No collection pages, no price history, no resale liquidity. This affects how "sales" on unindexed platforms should be weighted. Always check: `https://api.opensea.io/api/v2/asset_contract/{address}/`

## Tone & Format Rules

### 14. Social links are neutral data (2026-07-13)
List social links (X, Instagram, email) as "present" without assessing authenticity or scoring +/-. Do not write "may be fake" or "matching the artist persona" — just state what exists. The vetting framework cannot verify social authenticity.

### 15. No judgmental language about community rep (2026-07-13)
Report rep facts (concentration, source) without speculating about community members' motives. Do not write "rep from community being nice without research." Just state: "86% from one supporter, narrow support base." Let RD draw conclusions.

### 16. Feedback docs: no raw contract addresses (2026-07-13)
Artist-facing feedback documents should not contain hex contract addresses, internal marketplace contract references, or framework terminology. Say "Chonkly platform" not "contract 0xc360ceca." Say "not indexed on OpenSea" not "returns 404 on OpenSea v2 API." The internal assessment file can have technical details; the feedback doc is for the artist.

## Technical Workarounds

### 17. Blockscout doesn't index proxy contract NFT transfers (2026-07-13)
Many artist-deployed contracts (especially proxy patterns) show 0 NFT transfers on Blockscout even when they have real activity. Verify artist output via: (a) mint patterns — tokens appearing from 0x0 to the artist wallet, (b) Foundation/OpenSea listing activity, (c) the 6529 API artist fields. Do not conclude "zero artist output" just because Blockscout shows 0 transfers for a contract.

### 18. Use eth_call to read NextGen 6529 contract metadata (2026-07-13)
The NextGen contract (0x45882f9bc325e14fbb298a1df930c43a874b83ae) has view functions for collection data. Use eth_call via Blockscout RPC (https://eth.blockscout.com/api/eth-rpc) with keccak256 selectors:
- `retrieveArtistAddress(uint256 collectionId)` — returns artist wallet
- `retrieveCollectionInfo(uint256 collectionId)` — returns name, description, website, license (decode ASCII from raw hex)
- `totalSupplyOfCollection(uint256 collectionId)` — returns mint count
- `viewColIDforTokenID(uint256 tokenId)` — returns collection ID for a token
- `newCollectionIndex()` — returns total collection count

Example: Pebbles (collection 1) = ze-blocks.eth, 1000 supply, CC0, zeblocks.com

### 19. Use eth_call to read 6529 profile wave metadata
Profile wave drops can be fetched via `GET /waves/{profile_wave_id}/drops` to see what the artist has posted on their own wave.

## Known Marketplace Contract Addresses
- Foundation v1 proxy: 0xcda72070e455bb31c7690a170224ce43623d0b6f (AdminUpgradeabilityProxy, Jan 2021)
- Foundation v2: 0x3B3ee1931dc30F20fFa2dF07F88F93C1B0b94FC0
- Manifold ERC1155: 0x44e94034afce2dd3cd5eb62528f239686fc8f162
- Manifold ERC721: 0x7581871e1c11f85ec7f02382632b8574fad11b22
- SuperRare v1: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d
- SuperRare v2: 0xB932a70A57673d89f4acffBE830e8ed7f75fb9e0
- Seaport: 0x00000000000001adf28ef1c7d0186488931b0b94fc0
- OpenSea Wyvern: 0x7be8076f4ea4b96b62c43e4a9c3a3b87e2f7c1f2
- Chonkly SuperRarer (NOT SuperRare): 0xc360ceca69988e39be18ddb89e69afcc33a3833a
- Chonkly: 0x235f18021160bcd312c65496df1caf2b9ce5904d

## Key 6529 API Endpoints
- `GET /identities/{handle}` — profile with artist fields, wallets, rep
- `GET /drops/{id}` — individual drop details (title, author, ratings, winning_context)
- `GET /drops?drop_type=PREVOTE` — prevote card drops
- `GET /waves/{wave_id}/drops` — drops on a specific wave
- `GET /profiles/{id}/rep/categories` — rep breakdown by category

### 20. Burns (to 0x0) are NOT sales (2026-07-13)
NFTs sent to 0x0000000000000000000000000000000000000000 are burned/destroyed, not sold. Always check the recipient address before classifying a transfer as a sale. Game mechanics (e.g., death and taxes: burn citizen → mint evader at same timestamp) produce burn+mint pairs that look like sales if you only count outgoing transfers. Cross-check: if NFTs go to 0x0, check whether new NFTs were minted to the same wallet at the same timestamp — that's a game mechanic, not a flip. Example: david's death and taxes: citizens — 85 burned to 0x0, 85 evaders minted at matching timestamps. NOT sales.

### 21. Collector collections: report NET HELD, never raw transfer counts (2026-07-13)
Raw transfer counts are massively inflated by self-moves between wallets and items later sold. Always compute: `net_held = received_from_others - sent_to_self - sent_to_others`. The "most flipped" list should only include items actually sold to external addresses (not burned). Example: david's ENS showed 238 raw transfers but only 20 actually held (registered 129, sold/released 109). CloneX showed 78 transfers but 0 held (sold all 39). Artist feedback: "the notable collections that we pulled is wrong" — because raw counts included sold items and self-moves.

### 22. Multiple 6529 profiles for same person (2026-07-13, CRITICAL)
A single person may have multiple 6529 profiles — a main profile, a trading profile using an older wallet, a doxxing profile with GOVERNMENT_NAME classification (real name), and community/meme profiles. To find them: check ALL known wallets via `GET /identities/{address}` (direct wallet lookup returns the 6529 profile linked to that address). Profiles with `classification: GOVERNMENT_NAME` reveal real identity. Example: blocknoob has @famous (L6, trading with original wallet), @Karen (L0), @6529complaints (L0). Artist confirmed: "he also owns blockalpha.eth, justkidding.eth, and has two more profiles on 6529. One that doxs him and another that is for trading."

**WARNING: Do NOT claim identity links between profiles based on a single NFT transfer or ETH transfer.** A transaction between two wallets is just a transaction — it could be a sale, gift, or marketplace interaction between strangers. blocknoob was incorrectly linked to @Rakesh (GOVERNMENT_NAME, L63) based on one CyberKongz NFT transfer. RD corrected: "that is wrong, careful with your certainty." Only state profile connections as confirmed when the artist explicitly confirms them, or when there is overwhelming evidence (same ENS ownership, same consolidation key, direct wallet funding pattern). When unconfirmed, say "doxxing profile has not been identified with certainty."

### 23. Wave Creator field may be inaccurate (2026-07-13)
API `is_wave_creator: true` may not reflect reality. blocknoob says he is NOT the creator of the PSEUDONYM wave despite the API flag. Don't state "Wave Creator" as fact in artist-facing documents unless confirmed by the artist.

### 24. 6529 API search endpoints broken (2026-07-13)
`?search=`, `?type=`, `?classification=` query params all return 400. Direct handle lookup `GET /identities/{handle}` works. Direct wallet lookup `GET /identities/{address}` works. No working search API — must know exact handle or wallet address.

### 25. Blockscout v2 holdings API pagination broken (2026-07-13)
`GET /v2/addresses/{addr}/tokens?type=ERC-721` returns max 50 tokens and cursor-based pagination doesn't work with page=N. Use transfer-based approach (v1 API `?module=account&action=tokennfttx`) with net held calculation instead.

### 26. ENS subgraph finds wallets AND their ENS names (2026-07-13)
When querying ENS subgraph by owner, also check the `resolvedAddress` for each domain — some ENS names resolve to different wallets than the owner. Example: blocknoob.eth (0xbdc4a5c0) owns 13 ENS names, some resolve to other wallets (6529complaints.eth → 0x005b40bc, crypt.blocknoob.eth → 0x5fdb5fdb). Each resolved address may have its own 6529 profile. Also: crypt.blocknoob.eth wallet (0x5fdb5fdb) separately owns blockalpha.eth, ameeraadmi.eth, and noobmuseum.eth — wallets can own ENS names that resolve to other wallets.

### 27. Verify contract creator via Blockscout v2 address endpoint (2026-07-13)
The `/v2/smart-contracts/{address}/creator` endpoint returns 404 for many contracts. Instead, use `GET /v2/addresses/{address}` which returns `creator_address_hash` directly on the address object. Example: Burnt Boy by Deeze x Goonz contract — `/creator` endpoint 404'd, but `/v2/addresses/{address}` returned `creator_address_hash: 0x19D38600...` (Goonz, not deeze). This confirmed deeze did NOT deploy the contract despite his name being in the collection title.

### 28. Free mint farming ≠ artist output (2026-07-13)
Minting from 0x0 does not always mean artist activity. If a wallet mints from 537 different public contracts (1,437 total mints), they are a free/public mint collector, not an artist. Distinguish: (a) artist mints = wallet mints from contracts IT deployed (check `creator_address_hash`), (b) collector mints = wallet mints from public contracts deployed by others. Only (a) counts as artist output. Example: @deeze minted 1,437 NFTs from 537 contracts but deployed 0 contracts himself — all collector/free mint activity, zero artist output. The "Burnt Boy by Deeze x Goonz" collaboration had deeze's name but was deployed by Goonz.

### 29. Collector activity: top 3 most expensive purchases + sales (2026-07-13)
Every collector activity section must include:
- **Top 3 most expensive purchases**: NFT collection name, token ID, ETH price, date. Find these by checking ETH transfers paired with NFT incoming transfers around the same timestamp.
- **Top 3 most expensive sales**: NFT collection name, token ID, ETH price, date. Find these by checking ETH incoming paired with NFT outgoing transfers.
- **Waves active in**: Check 6529 community waves for the artist's posts/submissions. Report which waves they participate in and post count. Key waves to check: maybe's dive bar, Meme Club, Seeking Nomination, and any profile wave.

### 30. Game mechanics can look like sales (2026-07-13, UPDATED)
NFTs sent to 0x0 (burn address) are NOT sales — they may be game mechanics. death and taxes: citizens are burned and converted to evaders (1:1, same block) — NOT sold. Always check: (a) is the destination 0x0? (b) is there a corresponding mint from 0x0 in the same block? If yes → game mechanic, not sale. Exclude from "most flipped" lists. Also check: NFTs sent to a linked wallet (same ENS family) are transfers, not sales. gpebbles example: 128 citizens sent to gpebbleshooligans.eth wallet — transfer, not sale. Always identify the destination wallet's ENS name to determine if it's linked.

### 30b. Report wallet age by FIRST ETH TX, not first NFT tx (2026-07-13)
NFT transfer history may not start at wallet creation. gpebbles: first NFT tx was Feb 2026, but first ETH tx was Jan 2023 (BAYC purchase). Always use `GET /txlist?sort=asc&page=1&offset=1` to get the oldest transaction for true wallet age. Report per-wallet first tx dates when multiple wallets exist.

### 30c. Mint breakdown must be specific (2026-07-13, UPDATED)
"1,000+ mints from public contracts" is meaningless. Break down: (a) how many are game mechanics (DNT citizens→evaders), (b) how many are actual collecting mints, (c) list top 10 minted collections with counts. Verify ALL minted contract creators — if 0 contracts deployed by the wallet, ALL mints are from public contracts. Group mints by purpose (game mechanic vs collecting) not just total count. **Include artist names where possible** — look up the collection creator and identify the artist behind each notable collection (e.g. "NOKORI by Andrew Mitchell" not just "NOKORI", "Bears by noper" not just "Bears"). For collections that already include the artist name in the title, keep it. For others, check the contract creator's ENS name or look up the collection on OpenSea/Foundation to find the artist.

### 31. Drops API author_handle filter is BROKEN — use activity API (2026-07-13, CORRECTED)
The `author_handle` and `identity_id` params on `GET /drops` do NOT filter by author — they return global recent drops from random people. Do NOT use them to find an artist's wave posts.

**Correct method**: Use `GET /identities/{handle}/activity` which returns `{last_date, date_samples}` — a 365-element array of daily drop counts. Non-zero entries = active days. This confirms whether the artist has ANY wave activity in the past year. Example: deeze showed 0 active days out of 365 — zero wave activity despite the broken `author_handle` filter falsely returning 10 "drops."

For specific wave post counts, manually scan wave drops and filter by author handle locally (but note: wave pagination may be limited — maybe's dive bar has 373K+ drops).

### 32. Matching ETH prices to NFT purchases/sales (2026-07-13)
To find the ETH price of NFT purchases/sales, match by block number:
- **Purchases**: ETH outgoing txs where `from = wallet` and `value > 0`, matched to NFT incoming txs where `to = wallet` in the same block
- **Sales**: ETH incoming txs (regular `txlist` + internal `txlistinternal`) where `to = wallet` and `value > 0`, matched to NFT outgoing txs where `from = wallet` in the same block
- Sort all matches by ETH value descending, take top 3 for each
- Example: deeze's top purchase = Skulls of Luci #45 at 62 ETH (May 2023), top sale = Moonbirds #7237 at 38.56 ETH (Apr 2022)

### 33. Linked wallets with separate 6529 profiles (2026-07-13)
When discovering unconsolidated wallets via ENS subgraph, ALWAYS check each wallet for a 6529 profile via `GET /identities/{address}`. If a linked wallet has its own 6529 profile, include it in the assessment with: handle, level, classification, and relationship to the main profile. Do NOT speculate on identity links between profiles based on transactions alone (see pitfall #22). Example: blocknoob's original wallet (blocknoob.eth) has a separate profile @famous (Level 6) — included in assessment. ranagade.eth and lilblnde.eth (deeze's linked wallets) returned Level 0 profiles with no handle — noted but not prominent.

### 34. ENS subgraph may miss wallets — search by ENS name directly (2026-07-13)
The ENS subgraph query `{ domains(where: {owner: "<wallet>"}) }` only finds ENS names OWNED by a wallet. It will NOT find a wallet that owns an ENS name if you don't already know that wallet exists. amtwo.eth was owned by 0xa1697786... (the oldest and most active wallet, Dec 2021) but was NOT found via the subgraph because none of the 2 profile wallets owned amtwo.eth. Solution: if the handle matches an ENS name pattern (e.g., `amtwo` → `amtwo.eth`), query the subgraph by name: `{ domains(where: {name: "amtwo.eth"}) { owner { id } resolvedAddress { id } } }` to find the owning wallet. Always do a name-based lookup in addition to the owner-based lookup.

### 35. Always produce a clean/feedback version for sharing (2026-07-13)
RD asks for a "clean version to share" after reviewing the internal assessment. The clean version: no raw contract addresses, no internal on-chain analysis details, no "pitfall #X" references, no framework terminology. Save as `references/{handle}-feedback.md`. The internal assessment stays as `references/{handle}.md`. Produce both proactively — don't wait for RD to ask.

### 36. Free mint farming: single-day burst pattern (2026-07-13)
Some wallets mint hundreds of NFTs from a single public contract on a single day at zero cost. amtwo: 200 BitmapPunks mints on Jan 1, 2025, all free (0 ETH spent). This is the largest holding by count but has zero financial value. When a single collection dominates holdings by count but was entirely free-minted, call it out explicitly as "free mint farm" and exclude from the notable collections assessment. The mint breakdown section (pitfall #30c) should separate these from actual collecting mints.

### 37. 6529Complaints counts as 6529 ecosystem (2026-07-13)
The 6529 ecosystem checklist must include: 6529 Gradient, NextGen 6529, Karen Army, dwellers, 6529er Collection, The Memes, Seize And Share, SeizerDAO, AND 6529Complaints (The Manager's Complaint Report). Search NFT transfer history for "complaint" in tokenName. A holder with 6529Complaints NFTs is engaged in the 6529 ecosystem even if they don't hold Gradients.

### 38. SuperRare line format (2026-07-13)
In the collector activity section, include a line for SuperRare (NOT "SuperRarer") alongside Foundation. Format: `SuperRare: X bought, Y sold, Z held`. Verify tokens are on the real SuperRareV2 contract (0xb932a70a57673d89f4acffbe830e8ed7f75fb9e0). Do NOT call it "SuperRarer" — the collection is "SuperRare" and the contract is "SuperRareV2". Foundation and SuperRare are the two key art marketplace lines to include.

### 39. Don't contradict TDH with ecosystem assessment (2026-07-13)
If a profile has significant TDH (e.g. grubnot at 1.84M TDH), do NOT say "minimal 6529 ecosystem engagement" just because they hold few 6529-specific NFTs. TDH reflects broader network activity — a high-TDH holder is deeply engaged in the 6529 ecosystem even with minimal Gradient/NextGen holdings. Report what they hold factually (e.g. "3 ecosystem items: 6529er Collection, Karen Army, 6529Complaints") and let the TDH number speak for itself.