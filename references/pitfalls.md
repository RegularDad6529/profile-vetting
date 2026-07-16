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

### 4. Fetch ALL transaction pages (2026-07-13, UPDATED)
Blockscout API paginates at 100 txs/page. Wallets with high activity can have 1,000+ txs (RD example: 1,808 txs across 18 pages). Only fetching page 1 massively undercounts ETH flows. ALWAYS loop through all pages until a page returns < 100 results. This applies to `txlist` (ETH transfers), `txlistinternal` (internal txs), `tokennfttx` (NFT transfers), AND `tokentx` with `contractaddress=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` (WETH token transfers — see pitfall #52). WETH transfers are required because Seaport can pay sellers in WETH instead of raw ETH.

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
- Foundation NFT transfer proxy: 0xcda72070e455bb31c7690a170224ce43623d0b6f (NFT transfers in/out — discovered empirically 2026-07-15, see pitfall #55)
- Foundation v1 admin proxy: 0xcda72070e454bb84c756f75bb72993fbe416b69b (AdminUpgradeabilityProxy, Jan 2021)
- Foundation v2: 0x3B3ee1931dc30F20fFa2dF07F88F93C1B0b94FC0
- Manifold ERC1155: 0x44e94034afce2dd3cd5eb62528f239686fc8f162
- Manifold ERC721: 0x7581871e1c11f85ec7f02382632b8574fad11b22
- SuperRare v1: 0x41A322b28D0fF354040e2CbC676f0320d8c8850d
- SuperRare v2: 0xB932a70A57673d89f4acffBE830e8ed7f75fb9e0
- Seaport 1.6: 0x00000000000000ADc04C56Bf30aC9D3c0aAF14dC
- Seaport 1.5: 0x0000000000000068F116a894984e2DB1123eB395
- Seaport 1.4: 0x00000000000001adF28D0aCDeB0B5b31601b3b0d
- WETH (Wrapped Ether): 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
- OpenSea Wyvern: 0x7be8076f4ea4b96b62c43e4a9c3a3b87e2f7c1f2
- Chonkly SuperRarer (NOT SuperRare): 0xc360ceca69988e39be18ddb89e69afcc33a3833a
- Chonkly: 0x235f18021160bcd312c65496df1caf2b9ce5904d
- Art Blocks main (GenArt721Core): 0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270
- Art Blocks Explorations: 0x942bc2d3e7a589fe5bd4a5c6ef9727dfd82f5c8a

## Key 6529 API Endpoints
- `GET /identities/{handle}` — profile with artist fields, wallets, rep
- `GET /identities/{handle}/activity` — 365-day daily drop count array (pitfall #31)
- `GET /delegations/{wallet}` — all delegations for a wallet (PATH param, not query — pitfall #33b). Use cases: 1=primary, 2=sub-delegation, 3=consolidation, 998=custom
- `GET /drops/{id}` — individual drop details (title, author, ratings, winning_context)
- `GET /drops?drop_type=PREVOTE` — prevote card drops
- `GET /waves/{wave_id}/drops` — drops on a specific wave (returns ALL drops incl replies — more than `/drops?wave_id=`)
- `GET /profiles/{id}/rep/categories` — rep breakdown by category

### 6529 Backend Source Code
- GitHub: `6529-Collections/6529seize-backend` (TypeScript, open source)
- Delegation routes: `src/api-serverless/src/delegations/delegations.routes.ts` — `GET /:wallet` and `GET /minting/:wallet`
- Delegation contract: `6529-Collections/nftdelegation` (Solidity)

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

### 33. Check linked wallets for 6529 profiles (2026-07-13, UPDATED)
If a linked/unconsolidated wallet has its own 6529 profile, include that profile (handle, level, classification, relationship) in the assessment. 6529 caps at 3 wallets per profile — delegated wallets may have separate profiles.

### 33b. Delegated wallets should be assessed as if consolidated (2026-07-13, UPDATED)
6529 allows wallet delegation — a wallet can delegate its TDH/NFTs to a profile without being in the 3-wallet cap. These delegated wallets may or may not have ENS names, subdomains, or separate 6529 profiles. For vetting purposes, treat delegated wallets as if they were consolidated into the profile — include their on-chain activity, NFT holdings, sales, and mints in the assessment.

**Discovery via 6529 API**: `GET /api/delegations/{wallet}` — takes wallet as a PATH parameter (not query param). Returns all delegations for that wallet with `from_address`, `to_address`, `collection`, `use_case`, `all_tokens`, `expiry`. Query this for each of the profile's 3 wallets to find all delegated wallets in the graph. Use cases: 1=primary address, 2=sub-delegation, 3=consolidation, 998=custom.

Note: The `/api/delegations` endpoint WITHOUT a wallet path param returns global paginated data and does NOT support `from_address`/`to_address` query filters (broken, same as drops `author_handle`). Always use the path param form: `/api/delegations/{wallet}`.

Additional discovery: ENS subdomain search via subgraph (`name_ends_with: ".<primary_ens>.eth"` and `owner: "<profile_wallet>"`) can find subdomain wallets. But delegated wallets may have no ENS at all — the API path is primary.

Example: RegularDad's profile has 3 wallets. `GET /api/delegations/0x4220132c...` (memes.regulardad.eth) returned 4 delegations including hot.regulardad.eth (0xbe3471f8...) delegating TO it with use_case 2. hot.regulardad.eth is not in the 3-wallet cap but should be assessed as RD's wallet.

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

### 39b. Don't label collectors as "pure" anything (2026-07-13)
Never say "pure 6529 ecosystem" or "exclusively X" — collectors hold broadly across many ecosystems. RD holds CUBIQUE, mfers variants, Art Blocks, DANKBOTS, Decal series, XCOPY works, KnownOrigin, MakersPlace, and many others alongside 6529 items. Report ecosystem holdings factually in their own section, and list notable non-ecosystem holdings separately. Let the reader draw conclusions.

### 39c. Ecosystem keyword matching is too broad — Regulars are NOT 6529 ecosystem (2026-07-13)
The keyword list for 6529 ecosystem matching (`['6529', 'meme', 'karen', 'gradient', 'nextgen', 'seize', 'seizer', 'dweller', 'complaint', 'regular']`) is too broad. "Regular" matches "Regulars", "Regular Dad: This Is Me", and "Regular Jobs" — these are NOT 6529 ecosystem collections. They are community/personal collections. Only count as 6529 ecosystem: 6529 Gradient, NextGen 6529, Karen Army, dwellers, 6529er Collection, The Memes, Seize And Share, SeizerDAO, 6529Complaints, Meme Open Edition, Jake Memes, Gray Guard of Memes, 6529 Holiday Cards, Sandscapes cc0 Specials, Community Member Memes. Remove "regular" and "meme" as standalone keywords — only match specific 6529 collection names. When in doubt, check if the collection is deployed by the 6529 team or on the 6529 platform.

### 40. The Biggest L — worst NFT trade by P&L (2026-07-13)
Every collector activity section must include "The Biggest L": the single NFT trade where the wallet lost the most ETH. Calculate by matching buy price (ETH out + NFT in, same block) and sell price (ETH in + NFT out, same block) for the same (contract, tokenID). P&L = sell_price - buy_price. Report the biggest loss with: collection name, token ID, buy price, sell price, P&L, and dates. Example: grubnot's biggest L = CryptoFish #733, bought 1.04 ETH → sold 0.07 ETH = -0.97 ETH. Also note if one collection dominates the losses.

### 41. Failure to Transact — failed tx gas costs (2026-07-13)
Every assessment must include "Failure to Transact": count of transactions that failed (isError='1' or txreceipt_status='0' in Blockscout v1 API) and total ETH lost to gas on those failed txs. Calculate gas lost = gasUsed × gasPrice / 1e18 for each failed tx. Report as: "X failed transactions, Y ETH lost to gas on failed txs." Example: grubnot had 19 failed txs costing 0.008 ETH. This shows how careful/sloppy a trader is with transaction construction.

### 42. Minted: LOL — paid mints with no market (2026-07-13, UPDATED)
Every assessment must include "Minted: LOL" with two parts:

**Part A — Still holding the bag**: NFTs currently held where the collection has had NO transfer activity (in or out of the wallet) in 90+ days. Calculate by: for each collection the wallet still holds, find the last transfer timestamp in their NFT history. If >90 days → dead market, no offers likely. Report: count of dead collections, total NFTs held in dead collections, and which ones they PAID to mint (mint_cost > 0.005 ETH). These are the funniest — they paid to mint something nobody will buy.

**IMPORTANT — shared-contract platforms**: Some platforms like Art Blocks use a single contract for hundreds of projects. The contract is alive (active transfers) but the wallet's specific tokens may be unmoved for years. Do NOT call Art Blocks "dead" — instead, break down by project within the contract. Art Blocks token IDs encode the project: project = tokenId // 1000000. Look up project names via the Art Blocks API or known mappings. Report as "tokens unmoved X days, platform actively traded" with the specific project names and artists (e.g. "Fidenza by Tyler Hobbs, 2 held — actively traded on secondary, wallet just hasn't sold"). Note which projects are genuinely dead vs actively traded — Fidenza is very liquid, lesser-known projects may not be.

**IMPORTANT — "dead" means no MARKET activity, not just no wallet activity**: The current approach checks if the wallet's own tokens have moved recently. That's wrong for the LOL metric — what matters is whether the COLLECTION has a market. Without an OpenSea/Reservoir API key, we cannot check actual offer/sale activity per collection. For well-known collections (Art Blocks, VeeFriends), use general knowledge. For unknown collections, if there are zero transfers across ALL wallets (not just the assessed wallet) in 90+ days, it's likely dead. Note this limitation in the assessment.

**Part B — Already dumped for dust**: NFTs that were minted (from 0x0, including paid mints) and later sold for <0.005 ETH. For each candidate: (1) check mint_cost (ETH paid in same block as mint), (2) check for OTC payments within ±48h from the NFT recipient to the wallet, (3) only count as LOL if NO OTC payment found. Report paid-mint LOLs and free-mint LOLs separately, total ETH spent, total received.

Example: grubnot holds 130 NFTs across 96 dead collections (78% of holdings). 4 NFTs they paid 0.34 ETH to mint are in dead collections (SlicesOfTIMECovers dead 1609 days). Additionally, 33 paid-mint NFTs were dumped for 0 ETH (2.78 ETH lost), and 33 free mints dumped for dust.

### 43. NFTs sent out with no ETH received = transfers, not sales (2026-07-13)
When calculating P&L and sales, distinguish between actual sales (ETH received) and transfers/gifts (no ETH). For each outgoing NFT transfer, check: (a) ETH incoming in the same block (regular + internal txs), (b) OTC payment from recipient within ±48h. If NO ETH found → it's a transfer/gift/airdrop, NOT a sale. Do not count it in P&L calculations or "most flipped" lists. RD had 149 NFTs sent out with zero ETH received — these are gifts/transfers, not sales. Report the count separately so the reader understands the difference between sales and transfers.

### 44. ETH amounts are in ETH, not USD — don't confuse units (2026-07-13)
When reporting P&L losses, state the ETH amount clearly. Do not convert to cents/dollars in the same line unless explicitly asked. 0.035 ETH is not "3.5 cents" — it's 0.035 ETH (~$100 at current prices). The ETH amount is the unit of record on-chain. If a USD equivalent is needed, calculate it at current ETH price and label it clearly as approximate.

### 45. Foundation: zero transfers may mean post-shutdown, not never-used (2026-07-13)
Foundation shut down its platform. If a wallet shows 0 Foundation transfers, it could mean: (a) never used Foundation, OR (b) used Foundation before shutdown and the contract data is no longer indexed. Do not assert "never used Foundation" — state "0 Foundation transfers (never used or post-shutdown not indexed)." The Foundation v1/v2 contract addresses may still appear in historical data but current API access may be limited.

### 46. Multi-mint cost splitting — divide ETH by NFTs minted in same block (2026-07-13)
When matching ETH out to NFT mints in the same block, if multiple NFTs were minted in the same transaction/block, divide the total ETH by the number of NFTs to get the per-mint cost. This is common — people mint 2, 3, 5, 10+ at once. Without splitting, the mint cost is inflated by the number of mints.

Calculate: count all NFT transfers from 0x0 to the wallet in the same (blockNumber, contractAddress) pair. Divide the max ETH out in that block by that count. Same applies to purchases and sales — if multiple NFTs were bought/sold in the same block, split the ETH accordingly.

Example: RegularDad minted 3 BUILDINGS // NYC (#783, #784, #785) in one block for 0.0477 ETH total. Per-mint cost = 0.0159 ETH, not 0.0477 ETH. Without splitting, the Biggest L showed -0.035 ETH; with splitting it's -0.003 ETH. Same for On-Chain All-Stars: 3 minted for 0.06 ETH = 0.02 each. Also affected Biggest Wins: gristle buddeez 3 minted for 0.14 ETH = 0.047 each, making the win +0.23 ETH instead of +0.13 ETH.

### 47. Seaport pays ETH via internal txs, not regular transfers (2026-07-13)
When matching sale prices (ETH incoming for NFT outgoing), Seaport marketplace sales often pay the seller via an INTERNAL transaction, not a regular ETH transfer. The internal tx comes from the Seaport contract address (e.g. 0x0000000000000068f1... for Seaport 1.5). If you only check `txlist` (regular txs) for incoming ETH in the sale block, you'll miss the payment and incorrectly classify the sale as a transfer/gift. ALWAYS check `txlistinternal` in addition to `txlist` for sale matching. This is why pitfall #32 says "regular txlist + internal txlistinternal" — both are required.

Example: RegularDad's BUILDINGS // NYC #785 sale — the 0.0129 ETH payment came as an internal tx from 0x0000000000000068f116a894984e2db1123eb395 (Seaport 1.5). The regular `txlist` showed zero ETH incoming in that block. Without checking internal txs, the sale was missed entirely and the P&L was wrong.

**See also pitfall #52**: Seaport may also pay in WETH (ERC-20), not just ETH internal txs. Check WETH token transfers when no ETH internal tx is found.

### 48. Etherscan v1 API is deprecated — use v2 (2026-07-13)
Etherscan v1 endpoints (`api.etherscan.io/api?module=...`) return "You are using a deprecated V1 endpoint". Use v2: `api.etherscan.io/v2/api?chainid=1&module=...`. The v2 API requires `chainid=1` for Ethereum mainnet. All other params are the same as v1. An API key is still required for reliable access — set via ETHERSCAN_API_KEY env var.

### 49. Art Blocks API is down — use known project ID mappings (2026-07-13)
The Art Blocks token API (`token.artblocks.io/project/{id}` and `token.artblocks.io/token/{id}`) returns 400 for all requests as of July 2026. The v2 API (`api.artblocks.io`) also returns 500. When looking up Art Blocks project names and artists, use known mappings instead. Art Blocks token IDs encode the project: `project = tokenId // 1000000`. See `references/art-blocks-projects.md` for a lookup table of known project IDs to names and artists.

### 50. No subjective commentary on Biggest L / Biggest Wins (2026-07-13)
Report the numbers only for Biggest L and Biggest Wins. Do not add editorializing like "moderate, not catastrophic" or "relatively disciplined" — what's a big loss for one person is nothing for another. Just show the ETH amounts and let the reader judge.

### 51. Do not call low-cost mints "free mints" (2026-07-13)
A mint that cost 0.007 ETH is a PAID mint, not a free mint. Free mint = 0 ETH cost. Any non-zero ETH paid to mint is a paid mint, regardless of how small the amount. Do not label purchases as "free mint flips" when ETH was paid.

### 52. Seaport can pay in WETH, not just ETH — check WETH token transfers (2026-07-13)
Seaport 1.6 (0x00000000000000ADc04C56Bf30aC9D3c0aAF14dC) and Seaport 1.5 (0x0000000000000068F116a894984e2DB1123eB395) can pay sellers in WETH (ERC-20 token) instead of raw ETH. WETH payments show up as ERC-20 token transfers, NOT as ETH internal transactions. If a sale goes through Seaport but no ETH internal tx is found, check for WETH (contract 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2) token transfers to the seller's wallet in the same block. The seller may also unwrap WETH to ETH via the WETH contract (0xc02aaa39...) in a subsequent tx — look for internal txs FROM the WETH contract. Without checking WETH, sale proceeds are understated and Biggest L is overstated.

### 53. Blockscout v2 pagination uses next_page_params dict, NOT cursor (2026-07-15, CRITICAL)
Blockscout v2 API `/addresses/{addr}/token-transfers` returns `next_page_params` as a dict with keys like `index` and `block_number`, NOT a `cursor` string. If you try `next_page_params.get("cursor")` you get None and stop after page 1, fetching only 50 transfers. This caused hugofaz assessment to show 270 transfers instead of 3,559. Correct approach: pass the entire `next_page_params` dict as URL query params using `urllib.parse.urlencode(page_params)`. Also applies to `/addresses/{addr}/transactions` endpoint.

Example fix:
```python
page_params = data.get("next_page_params")  # dict like {"index": 88, "block_number": 24833916}
if page_params:
    url += "?" + urllib.parse.urlencode(page_params)
```

### 54. Blockscout v2 token fields: address_hash and total.token_id (2026-07-15)
Blockscout v2 token-transfers response has different field paths than expected:
- Contract address: `token.address_hash` (NOT `token.address`)
- Token ID: `total.token_id` (NOT `token.id`)
- Token name: `token.name`
- Token type: `token_type` at top level (NOT `token.type`)
- From/to addresses: `from.hash` / `to.hash` (nested in address objects)
- Value: `total.value` for ERC-1155 quantities
Using wrong field names results in empty contract/token_id strings and zero held NFTs.

### 55. Foundation has multiple contract addresses — discover marketplace activity empirically (2026-07-15)
Foundation operates through multiple contracts: the NFT transfer proxy (`0xcda72070e455bb31c7690a170224ce43623d0b6f`) is DIFFERENT from the payment/admin proxy listed in the known addresses section (`0xcda72070e454bb84c756f75bb72993fbe416b69b`). They share the `0xcda72070e45` prefix but diverge. If you hardcode only one Foundation address, you'll miss NFT transfers handled by the other.

**Fix**: After fetching all NFT transfers, empirically discover marketplace activity by counting the most frequent external `from`/`to` addresses. The top external senders are usually marketplaces (Foundation, OpenSea, Seaport) or known counterparties. Match these against the known addresses list, and if a top address isn't in the list but appears frequently, investigate it — it may be a marketplace contract variant.

Example: hugofaz initially showed 0 Foundation transfers because the script used garbled Foundation addresses. Empirical discovery found `0xcda72070e455bb31c7690a170224ce43623d0b6f` with 35 incoming NFT transfers — the actual Foundation NFT proxy.

**Updated Foundation addresses**:
- Foundation NFT transfer proxy: `0xcda72070e455bb31c7690a170224ce43623d0b6f`
- Foundation v1 admin proxy: `0xcda72070e454bb84c756f75bb72993fbe416b69b`
- Foundation v2: `0x3B3ee1931dc30F20fFa2dF07F88F93C1B0b94FC0`
All three should be checked when counting Foundation buys/sells.

### 56. Previous assessments may be understated due to pagination bug (2026-07-15)
Pitfall #53 (Blockscout v2 pagination) means ALL assessments run before 2026-07-15 that used the Blockscout v2 API likely fetched only 50 transfers per wallet instead of the full history. hugofaz went from 270 → 3,559 transfers (13x increase). Other assessments (blocknoob, deeze, madacollects, giopetto, etc.) may similarly undercount transfers, holdings, collections, and mints. Re-running these assessments with the fixed pagination will produce significantly different numbers. Prioritize re-running assessments for profiles with known high activity (high TDH, many wallets).

### 57. Artist creation section is mandatory — don't skip it for collector metrics (2026-07-15, CRITICAL)
The first hugofaz re-assessment had full collector metrics (3,559 transfers, top buys/sales, Biggest L, etc.) but ZERO artist creation content — no deployed contracts, no MS win descriptions, no Foundation sales breakdown by own-art vs collector-flips, no practice narrative. RD caught this: "You didn't include any of his artist creations."

Every assessment of a confirmed artist MUST include an **Artist Work** section BEFORE the Collector Activity section, containing:

1. **MS wins with descriptions**: Fetch each drop via `GET /drops/{id}`. Extract `title`, `metadata` (description field), `raters_count`, `rating`, `winning_context.place`, `winning_context.decision_time`. Include the full artist description text — it reveals medium, collaboration, and intent.
2. **Deployed contracts table**: For each contract minted from 0x0, check `GET /v2/addresses/{contract}` for `creator_address_hash` — only include contracts where the creator is one of the profile's wallets. Report: collection name, symbol, type (ERC-721/ERC-1155), mints, sold, holders. Group by deploying wallet.
3. **Foundation sales breakdown**: Separate into (a) own-art sales, (b) collector flips (other artists' work), (c) own-art buybacks. Match Foundation transfer collection names against deployed contract names to classify.
4. **Practice narrative**: Describe the artist's medium, themes, and series. Group collections into series (e.g., "photography-focused: nudes, portraits, performance art"). Note collaborative works and gallery/organization profiles.
5. **Casa NUA / gallery context**: If the artist operates a physical gallery or organization profile (ORGANIZATION classification), describe it — location, exhibitions, community role.

### 58. Blockscout v2 contract-creations endpoint returns 400 (2026-07-15)
`GET /v2/addresses/{addr}/contract-creations` returns HTTP 400. To find contracts deployed by a wallet, use the alternative approach:
1. Collect all unique contracts where the wallet minted from 0x0 (from token-transfers data)
2. For each contract, query `GET /v2/addresses/{contract}` and check `creator_address_hash`
3. If `creator_address_hash` matches one of the profile's wallets → it's their own deployed contract

This is slower but reliable. Batch with 0.15s delays to avoid rate limiting.

### 59. Art sales revenue must include ETH values, not just mint/hold counts (2026-07-15, CRITICAL)
RD caught the hugofaz assessment having contract tables with mints/sold/holders columns but NO revenue figures: "You didn't include any of the sales volume or top sales for any of those contracts." Every Artist Work section MUST include:

1. **Art Sales Revenue subsection** with total ETH figure
2. **Per-collection revenue** with ETH totals and number of paid sales
3. **Top individual art sales** ranked by ETH price, with collection name, token ID, price, date, and buyer/method
4. **Seaport sales**: ETH value is in the tx `value` field directly (method=`fulfillBasicOrder_efficient_6GL6yc` or `fulfillAvailableAdvancedOrders`)
5. **Foundation sales**: NFT transfer txs show 0 ETH — revenue comes as WETH from buyer wallets or Foundation auction payouts (see pitfall #60)

### 60. Foundation escrow pattern — NFT transfer txs show 0 ETH (2026-07-15)
Foundation sales use a proxy escrow mechanism that splits the NFT transfer from the payment:
- The artist's NFT transfer tx (method=`safeTransferFrom` or `createReserveAuctionV2`) shows **0 ETH** in tx value
- Payment comes separately as **incoming WETH** from the buyer's wallet or from Foundation auction payout contracts
- Multiple auction payouts can arrive on the same day from different buyer addresses (e.g., casanua received 9 WETH transfers on Mar 31, 2023 from 9 different addresses — Live modeling sessions auction)

**How to verify Foundation art revenue:**
1. Fetch all incoming WETH transfers to the wallet (Blockscout `/addresses/{addr}/token-transfers?token={WETH}`)
2. Exclude WETH from `0x0000...0000` (that's ETH wrapping, not a sale)
3. Exclude WETH from own wallets (cross-wallet transfers, not sales)
4. For each remaining incoming WETH transfer, note the `from` address — this is the buyer
5. Cross-reference with Foundation NFT transfers (to/from `0xcda72070e455bb31`) to match sale timing
6. Sum all external WETH incoming = approximate Foundation art revenue

**Note**: Some incoming WETH may be collector flip proceeds (selling other artists' work bought on Foundation), not own-art revenue. Cross-reference with deployed contract names to classify.

### 61. Blockscout rate limiting on sequential tx lookups (2026-07-15)
Fetching `/transactions/{tx_hash}` for 30+ transfers in rapid succession triggers HTTP 429 (Too Many Requests). This happens when verifying Seaport sale prices or checking tx methods. Mitigation:
- Use **2-second delays** between tx lookup calls
- On 429, wait 30-60 seconds and retry
- Batch contract address lookups (`/addresses/{contract}`) at 0.15-0.3s delays (these are lighter)
- For large wallets (100+ outgoing transfers), consider running as a background process with `notify_on_complete=True` to avoid blocking the conversation

### 62. Blockscout v2 internal-txs endpoint unreliable (2026-07-15)
`GET /v2/addresses/{addr}/internal-txs` returns 0 items for some wallets despite confirmed internal transactions existing (verified via Etherscan). This affects Seaport payment verification. If the internal-txs endpoint returns empty:
1. Check WETH token transfers instead (Seaport often pays in WETH — pitfall #52)
2. Check the tx-level internal-txs endpoint: `GET /v2/transactions/{tx_hash}/internal-txs` (this sometimes works when the wallet-level endpoint doesn't)
3. Check incoming ETH in regular txs as a fallback (some sales pay directly)
4. For Seaport sales specifically, the tx `value` field often contains the ETH amount directly (method=`fulfillBasicOrder_*`)

### 63. Keep artist and collector sections COMBINED in one file (2026-07-15)
RD confirmed: artist and collector reviews should be in a single combined assessment file, NOT split into separate artist-facing and collector documents. The collector side (trading patterns, holdings, ecosystem engagement) is evidence of authenticity — splitting them loses that context. "It helps to determine if they are real." The combined file should have `## Artist Work` followed by `## Collector Activity` sections. (Note: pitfall #35 about clean/feedback versions still applies — the shareable version for artists should still strip technical details, but the internal assessment stays combined.)

### 64. safeTransferFrom = direct transfer, not marketplace sale (2026-07-15)
When checking NFT outgoing transfers, the tx method reveals the sale mechanism:
- `safeTransferFrom` — direct transfer (gift, OTC, or Foundation escrow deposit). Payment is NOT in this tx.
- `fulfillBasicOrder_efficient_6GL6yc` / `fulfillAvailableAdvancedOrders` — Seaport sale. ETH value is in the tx `value` field.
- `createReserveAuctionV2` — Foundation auction listing (not a sale yet)
- `batchListFromCollectionV2` — Foundation batch listing (not a sale yet)
- `upsertListing` / `upsertListingV2` / `setBuyPrice` — listing/price setting (not a sale)
- `fulfillAdvancedOrder` — Seaport sale (may pay in WETH)

For `safeTransferFrom` transfers, check for incoming WETH/ETH within ±48h to determine if it was an OTC sale or a gift. If no payment found, classify as transfer/gift.

### 65. Blockscout v2 /transactions/{hash} can return 400 for valid tx hashes (2026-07-15)
The Blockscout v2 transaction detail endpoint sometimes returns HTTP 400 Bad Request for valid, confirmed tx hashes. This is different from 429 rate limiting. The 400 appears intermittent — retrying after a delay sometimes works. If persistent, alternative approaches:
- Use the tx-level internal-txs endpoint (may work when the tx detail endpoint doesn't)
- Use the tx-level token-transfers endpoint
- Check if the tx hash is complete (66 chars including 0x prefix) — truncated hashes will always 400

### 67. Shared/factory contract mints ≠ own deployed contracts (2026-07-15, CRITICAL)
Jpearlking was assessed as having "5 deployed contracts" — WRONG. Only 2 were directly deployed (Lumière, unnamed ERC-1155). The other 3 (Safe Haven, Rare, Rare II, TL Universal Deployers) were created by OTHER addresses. Jpearlking minted ON those contracts but did NOT deploy them. The old assessment confused "minted tokens from 0x0 on this contract" with "deployed this contract."

**Fix**: For every contract where the wallet minted from 0x0, check `GET /v2/addresses/{contract}` and verify `creator_address_hash` matches one of the profile's wallets. Only contracts where the creator IS the profile wallet count as "deployed." All others are shared/factory contracts — the wallet is a minter/user, not the deployer.

This is related to pitfall #28 (free mint farming ≠ artist output) but different: #28 is about minting from many public contracts as a collector. This is about incorrectly claiming shared contracts as own deployments in the artist output section. Also check for factory/proxy patterns — Transient Labs Universal Deployer creates contracts where the factory is the on-chain creator, not the artist's wallet.

### 68. Known exchange hot wallet addresses — exclude from sales (2026-07-15)
When categorizing incoming ETH, these addresses are exchange hot wallets (withdrawals, NOT sales):
- `0x28C6c06298d514Db089934071355E5743bf21d60` — Binance 14
- `0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549` — Binance 15
- `0xDFd5293D8e347dFe59E90eFd55b2956a1343963d` — Binance 8
- `0x4976A4A02f38326660D17bf34b431dC6e2eb2327` — Coinbase
- `0x9696f59E4d72E237BE84fFD425DCaD154Bf96976` — Coinbase 2

ETH from these addresses to the wallet = exchange withdrawals (user withdrawing their own funds from an exchange). Always exclude from sales revenue. The old Jpearlking assessment correctly identified 0.29 ETH of exchange withdrawals but the new automated script initially counted them as direct sales.

### 69. OpenSea gross (tx value) vs net (internal tx) — don't double-count (2026-07-15)
OpenSea/Seaport sale prices appear in TWO places:
1. **Gross**: The tx `value` field contains the full sale price (what the buyer paid)
2. **Net**: The internal tx from the marketplace contract contains the seller's proceeds (gross minus marketplace fee)

OpenSea's standard fee is 12.5% — verified: 0.0600 ETH gross → 0.0525 ETH net (87.5% = 1 - 12.5%). When reconciling sales:
- Use NET (internal tx) figures for revenue reporting — this is what the artist actually received
- Do NOT add both gross and net — they're the same sale
- If you find a tx with `value=0.06` on 2022-07-18 AND an internal tx of `0.0525` on the same date, that's ONE sale, not two
- The gross/net split also helps verify legitimacy — if gross × 0.875 ≈ net, it's a standard OpenSea sale

### 66. Double-check date math — don't misstate timeframes (2026-07-15)
When reporting wallet age or activity duration, always calculate the difference between the first tx date and today's date carefully. A wallet first active in July 2025 is ~1 year old as of July 2026, not "2 weeks old." RD caught this error on the babla99 assessment: said "2 weeks ago" for July 31, 2025, when it was actually a year ago. Before writing any timeframe statement, mentally verify: "2025-07-31 to 2026-07-15 = ~1 year." Wrong timeframes change the entire read of a profile — a 1-year-old dormant wallet is very different from a 2-week-old fresh wallet.

### 70. Seaport purchases: NFT transfer `from` shows seller's wallet, not marketplace (2026-07-15)
When buying on Seaport, the NFT transfer `from` field shows the SELLER's wallet address, not the Seaport marketplace contract. You cannot identify a Seaport purchase by checking if the `from` address is a marketplace contract. Instead, identify purchases by checking the tx method (`fulfillBasicOrder_*` or `fulfillAdvancedOrder`) or by matching ETH/WETH outgoing in the same block. This is the inverse of pitfall #47 (sales show marketplace as source via internal tx) — purchases show the peer, not the marketplace.