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
- `GET /identities/{handle}/activity` — 365-day daily drop count array (pitfall #31, pitfall #80). **MANDATORY for profile age verification** — `created_at` resets on deconsolidation, this is the only reliable timeline.
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

### 71. Seeking Nomination wave drops API — v2 returns {drops: [...]}, not {items: [...]} (2026-07-16)
The v2 wave drops endpoint `GET /v2/waves/{wave_id}/drops?limit=200` returns a dict with key `drops` (NOT `items` or `data`). The drops array contains full drop objects with `author.handle`, `content`, `media`, `drop_type`, `serial_no`, `created_at` (milliseconds since epoch). Pagination uses `next_page_params` dict (same as pitfall #53). The v1 endpoint `GET /waves/{wave_id}/drops` returns an empty dict `{}` — always use v2. The Seeking Nomination wave ID is `0ecb95d0-d8f2-48e8-8137-bfa71ee8593c`. Note: the wave does NOT appear in the `GET /waves` list (only 20 waves returned) but is accessible directly by ID. The `author_handle` query param on `GET /drops` is still broken (pitfall #31) — scan wave drops locally to find specific authors.

### 72. Blockscout v2 token-transfers endpoint — use bare URL, no filter param (2026-07-16)
`GET /v2/addresses/{addr}/token-transfers?filter=to%7Cfrom` returns HTTP 422 Unprocessable Entity. The `filter` query param is not supported. Use the bare URL `GET /v2/addresses/{addr}/token-transfers` (no filter) — it returns both incoming and outgoing transfers. The `?type=ERC-721` filter on `/tokens` endpoint works but `filter` on `/token-transfers` does not.

### 75. Solana activity claims are unverifiable from this environment (2026-07-16)
Some nominees claim Solana activity (e.g., kiramoto: "been at it in sol since 2022"). This environment has no Solana on-chain data access — no Solana RPC, no Solscan/Helius API key, no Solana FM. State this gap explicitly in the assessment: "Claims Solana background since [year] — cannot verify from this environment." Do NOT classify as suspicious based on unverifiable claims alone, but do note the gap as a limitation of the assessment. If the profile has minimal ETH activity AND claims Solana activity, the Solana claim becomes the critical verification path — flag it for RD to check manually or provide a Solana wallet address.

### 75b. Minimal profiles with deployed contracts but no market traction (2026-07-16)
kiramoto pattern: Level 17, TDH 0, 2 deployed ERC-721 contracts with only 7 total NFTs minted, ~0.38 ETH art revenue (2 Foundation sales in 2023), zero collector activity (no purchases, no 6529 ecosystem holdings), 2.5-year ETH dormancy, primary wallet created 2 days before nomination, no social links, no ENS, 0 rep on nomination post. Classification: SUSPICIOUS. Key signals: TDH 0 (no 6529 network engagement), wallet created just before nomination (timing suggests nomination-driven setup), long dormancy after initial contract deployment (no ongoing artist practice), zero collector activity (not embedded in NFT community). When a profile has deployed contracts but everything else is minimal/dormant, the contracts alone don't establish legitimacy — assess whether the art practice is ongoing or was a one-time event.

### 74. Nifty Gateway NiftyBuilderInstance contracts — custom metadata, tokenURI reverts (2026-07-16)
Nifty Gateway contracts (named `NiftyBuilderInstance`) have a custom metadata architecture that differs from standard ERC-721:

- **`tokenURI(uint256)` reverts** even for existing tokens — `_baseURI` is set to a bare IPFS hash (no `ipfs://` prefix, no `/{tokenId}` suffix), so the constructed URI is invalid and the call may revert
- **`tokenIPFSHash(uint256)` is the working metadata function** — returns the IPFS hash of the artwork image directly (NOT a metadata JSON with `attributes` array). The hash points to a raw image file (GIF, PNG, etc.)
- **`tokenName(uint256)` may return empty string** even when the token exists
- **Token ID encoding**: `tokenId = niftyType * topLevelMultiplier + edition * midLevelMultiplier + build`. Read `topLevelMultiplier()` and `midLevelMultiplier()` to decode. Example: type=1, edition=1, build=1 → tokenId = 171000100001
- **Finding valid token IDs**: Use `ownerOf(uint256)` (selector `0x6352211e`) with encoded IDs to find which tokens exist. `tokenName`/`tokenIPFSHash` both call `_exists()` internally, so they revert if the token doesn't exist — but `ownerOf` is the reliable existence check
- **`_typeCount()`** returns the number of NFT types in the contract. Open editions typically have 1 type
- **No traits/attributes on-chain**: The contract has no `attributes` mapping. All tokens in an open edition share the same IPFS hash. There is no metadata JSON to fetch — the IPFS hash IS the image
- **Getting the ABI**: Use Blockscout v1 API `GET /api?module=contract&action=getsourcecode&address={addr}` — returns full ABI and source code. The source shows the custom function implementations
- **Custom event signature**: Nifty Gateway uses event `0xdeaa91b6...` instead of standard `Transfer(address,address,uint256)` for minting. Standard `eth_getLogs` with Transfer topic returns 0 results. Use the custom event topic or check `ownerOf` to find minted tokens

Example: XCOPY "MAX PAIN AND FRENS OPEN EDITION" (0xd1169e5349d1cB9941F3DCbA135C8A4b9eACFDDE) — all tokens share IPFS hash `QmTcTzTPgCyvF933oeFvB4GkPgaXtF6dKuQgvg32qqLYGF` (4.5MB GIF). No traits exist anywhere.

### 76. Nifty Gateway burn/redeem companion contracts (2026-07-16)
Nifty Gateway open editions (NiftyBuilderInstance) may have a SEPARATE companion "burns" contract where holders burn original tokens to redeem different characters. Example: XCOPY "MAX PAIN AND FRENS OPEN EDITION" (0xd1169e...) has a companion "MAX PAIN AND FRENS OPEN EDITION BURNS BY XCOPY" (0x3696cd00618a08c8793208385ae526677c889d4a) with 3 types (21+34+33 tokens), each a different character GIF. The burn contract uses the same NiftyBuilderInstance pattern with `_typeCount > 1`.

**How to discover burn/redeem contracts:**
1. Search SearXNG (localhost:8888) for `"{contract name keywords}" burn redeem XCOPY` — verse.works and outposts.io often index them
2. Check the Nifty Gateway deployer bot (0x7f58c5daf1612d0ac114752cd8fe61a51332e1a8) — it calls `setNiftyIPFSHash` on ALL Nifty Gateway contracts. Fetch its txlist, extract unique `to` addresses, and call `name()` on each to find companion contracts with "BURNS" in the name
3. verse.works pages show token names even when on-chain `tokenName` is empty — search `site:verse.works "{contract address}"` or fetch verse.works artwork pages directly. The page title and og:title contain the character name (e.g., "GUZZLER #10/21 by XCOPY")
4. xcopy.art lists artist series — useful for XCOPY-specific burns (DAMAGE CONTROL series uses Manifold contracts, NOT Nifty Gateway)

**Key insight for assessments:** When an artist deployed a Nifty Gateway open edition, check for burn/redeem mechanics. The burns contract reveals additional character names and artwork that aren't visible on the original contract. The on-chain `tokenName` is typically empty — names come from off-chain sources (verse.works, Nifty Gateway UI, artist website).

**XCOPY DAMAGE CONTROL series** (separate from Nifty Gateway burns, uses Manifold contracts, 2023-24): 10 characters — OBLIVION (450), BANG_BANG (249), SIDEWAYZ (388), CHURN (151), CRAWLER (257), XOMBO (150), SH_MASH_MA (99), BOT_ROT (84), REIGN (63), HEAVY (44). Burns ended Dec 31, 2024. Source: xcopy.art/series/damage-control

### 77. Use SearXNG (localhost:8888) for contract and collection research (2026-07-16)
The self-hosted SearXNG instance at `http://localhost:8888/search?q={query}&format=json` is a powerful tool for NFT contract research when on-chain data is insufficient. Use cases:
- Finding companion/burn contracts by searching contract name + "burn" + "redeem"
- Finding token/character names that are empty on-chain (verse.works, CoinMarketCap, outposts.io index them)
- Finding artist series pages (e.g., xcopy.art/series/damage-control)
- Discovering contract addresses from marketplace pages (verse.works HTML contains full 0x addresses in the page source — fetch and regex `0x[a-fA-F0-9]{40}`)

Note: SearXNG returns mixed quality results — filter by checking if the result content contains relevant keywords. URL-encode spaces in queries. The `format=json` param is required for API access.

### 73. ENS subgraph may return 403 Forbidden (2026-07-16)
The ENS subgraph at `api.thegraph.com/subgraphs/name/ensdomains/ens` may return HTTP 403 Forbidden for queries that worked previously. This blocks both owner-based lookups (`{ domains(where: {owner: \"...\"}) }`) and name-based lookups (`{ domains(where: {labelName: \"...\"}) }`). When the subgraph is 403, fall back to: (a) Blockscout address endpoint `GET /v2/addresses/{addr}` which returns `ens_domain_name` if set, (b) check if the handle matches an ENS name pattern and skip ENS discovery. Note that Blockscout only returns the primary ENS name, not subdomains.

### 78. xcopy.art Next.js RSC flight data extraction (2026-07-16, UPDATED)
xcopy.art is a Next.js App Router site. Work pages (`/works/{slug}`) contain contract addresses, edition counts, and media filenames in RSC flight data — not in standard HTML or JSON. The MAIN page (`https://xcopy.art/`) flight data contains ALL works — extract `/works/` paths from the `<script>` flight data chunks, not from raw HTML links (which only show ~28). The `/explore` page is incomplete. See `references/xcopy-art-extraction.md` for full extraction code and the complete 153-works catalog. Useful for cross-referencing XCOPY contract addresses, finding companion burns contracts, and verifying edition counts. Some works (damage-control, laws, saint) return 404 as individual pages but appear in the main page flight data.
```python
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
raw = ''.join(chunks)
contracts = re.findall(r'contractAddress[^,]*([0-9a-fA-Fx]{42})', raw)
editions = re.findall(r'numberInEdition[^,]*"?(\d+)"?', raw)
media = re.findall(r'cdn\.xcopy\.art/media/original_images/([^"\\]+)', raw)
```
153 works listed as of July 2026 — fetch the MAIN page (`https://xcopy.art/`) flight data, NOT `/explore` (which only shows ~28). Full extraction patterns and complete 153-works catalog in `references/xcopy-art-extraction.md`. Useful for cross-referencing XCOPY contract addresses, finding companion burns contracts, and verifying edition counts. Some works (damage-control, laws, saint) return 404 — the DAMAGE CONTROL series page doesn't exist but the series info is on the main page.

### 80. Deconsolidation resets created_at — use activity API for real timeline (2026-07-19, CRITICAL)
`created_at` on `/identities/{handle}` and `/profiles/{handle}` reflects the LAST deconsolidation event, NOT the profile's original creation date. When a user removes a wallet from their consolidation group, the identity gets a new `consolidation_key` (just their own address, no dash) and `created_at` updates to the split date. This makes long-time users look brand new.

**Consolidation mechanics** (from `6529seize-backend/src/consolidation-tools.ts`):
- `consolidation_key` = all wallet addresses sorted alphabetically, joined with `-`. Single wallet = no dash. Two wallets = `0xaaa-0xbbb`. Three = `0xaaa-0xbbb-0xccc`.
- Deconsolidation = REVOKE event in the consolidations table. The consolidation_key changes and `created_at` resets.
- After deconsolidation, the drops API (`?author_handle=`) may only return drops from the new consolidation_key — older drops posted under the consolidated identity may not appear.

**How to find the real timeline**: Use `GET /identities/{id}/activity` — returns `{last_date, date_samples}` with a 365-element array of daily drop counts. Non-zero entries = active days. This data survives deconsolidation and shows the true activity history. A profile with `created_at: today` but activity samples going back 8 months was deconsolidated, not created today.

**Red flag pattern**: Profile shows `created_at: today` but has high rep (50K+) and level (19+). These numbers were earned over months/years — the profile is NOT new. Always cross-check `created_at` against the activity API before stating when a profile was created.

Example: @parisa showed `created_at: 2026-07-19` (today) but activity samples showed ~240 days of activity. Her drops API only returned 10 drops from today (deconsolidation truncated the history), but her rep of 51K and level 19 were earned over 8 months. RD caught: "The wallet and profile is older today, you fell for another portal."

### 81. Foundation marketplace internal ETH = bid escrow, NOT confirmed sales (2026-07-19)
The Foundation marketplace contract (`0xcda72070e455bb31c7690a170224ce43623d0b6f`) routes ETH through internal transactions. These internal txs can be:
- **Bid escrow releases** — ETH returned to a bidder who was outbid (NOT a sale)
- **Auction payouts** — ETH sent to the seller after a successful auction (IS a sale)
- **Failed auction refunds** — ETH returned when an auction doesn't complete (NOT a sale)

You CANNOT distinguish these without checking the individual transaction context (the tx method, the NFT involved, and the auction state). Do NOT claim "artist sold X ETH of art" based on summing internal txs from Foundation's marketplace contract. This is the same error class as pitfall #9 (Foundation bid escrow inflates gross flows) but applies to the Alchemy `alchemy_getAssetTransfers` internal category specifically.

**Correct approach**: Match Foundation internal ETH transfers to specific NFT transfers (token mints from `0x3b3ee1931dc30c1957379fac9aba94d1c48a5405` or NFT transfers to/from the Foundation proxy) in the same block. Only count ETH paired with an NFT transfer TO a buyer as a sale. Unmatched internal ETH = bid escrow/refund.

RD corrected: "I think you made the mistake you made before with Foundations bid mechanics."

### 82. Exchange intermediary wallets — don't assume peer-to-peer (2026-07-19)
When tracing funding trails, large exchanges (Binance, Coinbase) operate MANY hot/cold wallets that shuffle ETH between each other. A funding chain like `0x28c6c062... (Binance 14) → 0x56eddb7a... → target wallet` may look like the intermediary is a peer, but `0x56eddb7a...` is likely ALSO a Binance wallet. 50,000 ETH transfers between wallets are exchange internal operations, not peer-to-peer transfers.

**How to verify**: Check if the intermediary wallet has patterns consistent with an exchange hot wallet: (a) very high ETH throughput (thousands of ETH), (b) funded by a known exchange address, (c) sends to many different wallets (exchange withdrawal pattern). If the intermediary was funded by Binance and sends to many wallets, treat the entire chain as exchange-funded.

RD corrected on @parisa: "I suspect the intermediary wallet with 50,000 eth is also a Binance wallet."

### 79. Nifty Gateway deployer bot — discover all contracts by same platform (2026-07-16)
The Nifty Gateway deployer bot (`0x7f58c5daf1612d0ac114752cd8fe61a51332e1a8`) calls `setNiftyIPFSHash` on every Nifty Gateway contract. To find companion/burn contracts for a given collection:
1. Fetch the deployer's txlist: `GET /api?module=account&action=txlist&address=0x7f58c5...&page=1&offset=200&sort=asc`
2. Extract all unique `to` addresses (these are Nifty Gateway contracts)
3. Call `name()` (selector `0x06fdde03`) on each via eth_call to get the contract name
4. Filter for related names (e.g., "BURNS" for burn contracts, "XCOPY" for XCOPY collections)

The deployer has 129+ unique contracts across multiple pages. This technique found the "MAX PAIN AND FRENS OPEN EDITION BURNS BY XCOPY" companion contract (0x3696...) by scanning all Nifty Gateway contracts for "XCOPY" in the name.

### 83. Iran geo-block cluster — shared Binance sub-distribution wallet (2026-07-19)
When two 6529 members are funded by the SAME Binance sub-distribution wallet, they're in the same Iranian community withdrawal cluster. `0x8d56f551b44a6da6072a9608d63d664ce67681a5` funds both @sariture AND @sepicaso — both have zero OpenSea, both are established 6529 members. This shared-wallet signal is STRONGER than individual Persian name signals. When you identify one Iran geo-block member, trace their funding wallet and check if it funds other 6529 members — this discovers the cluster.

### 84. Deconsolidation can wipe the ENTIRE activity chart (2026-07-19)
Pitfall #80 noted that deconsolidation resets `created_at`. Worse: the `/identities/{id}/activity` endpoint can return ALL ZEROS (every day = 0) after a recent deconsolidation — not just a reset timestamp. When this happens, rep + level are the ONLY reliable indicators of prior history. L23 + 91K rep + zero activity = deconsolidated, NOT new. Don't conclude "new account" from zero activity alone. Cross-check with rep/level and counterparty relationships.

### 85. Drops API author_handle filter is broken (2026-07-19, CONFIRMED)
`GET /api/drops?author_handle=X` returns drops from OTHER people on the profile wave, not the author's own drops. V2 drops API (`/api/v2/drops?author_handle=X`) returns HTTP 400. Use `parent_drop_id` (profile wave ID) instead via `GET /api/drops?parent_drop_id={id}`, but that still returns ALL drops on the wave — filter by author handle client-side. Related to pitfall #31 (same issue, confirmed again during sepicaso investigation).

### 86. ENS display field shortcut in identity API (2026-07-19)
The `GET /identities/by-wallet/{wallet}` response includes a `display` field that may contain the ENS name (e.g., "sepicaso.eth") even when the on-chain ENS reverse registrar (0x084b1c3c...) returns no result. Check this field FIRST as a shortcut before doing on-chain ENS lookups. The `wallets` array also has per-wallet `display` fields with ENS names.

### 87. Profile bio is NOT in the identity endpoint (2026-07-19)
The identity endpoint (`GET /identities/by-wallet/{wallet}`) does not include bio, x_link, or other social fields. These are in the nested `profile` object of `GET /profiles/{handle}` (response key `profile.bio`, `profile.x_link`). Use BOTH endpoints for a complete picture: identity endpoint for rep/level/wallets/ENS, profiles endpoint for bio/socials/classification.

### 88. Gnosis Safe is cold storage — not an OpenSea-blocked wallet (2026-07-19)
A Gnosis Safe (SafeProxy) is a multi-sig cold storage vault. You don't log into OpenSea with it. Lack of OpenSea activity on a Safe does NOT mean it's blocked. When assessing OpenSea blocking, only count wallets the user would actually log in with (EOAs, smart contract wallets like EIP-7702 delegated EOAs). Don't count Gnosis Safes as evidence of blocking. RD corrected: "If it's a gnosis safe, it wouldn't be connected to anything as a way to keep the assets safe, I wouldn't assume that it's blocked by OS."

### 89. alchemy_getAssetTransfers misses OpenSea atomic matches — scan tx receipts (2026-07-20, CRITICAL)
The `alchemy_getAssetTransfers` API only tracks direct token transfers to/from addresses. OpenSea Wyvern/Seaport uses atomic matching — the NFT goes directly from seller to buyer (not through the exchange contract), and ETH goes directly from buyer to seller. These transfers do NOT appear when querying `fromAddress`/`toAddress` = exchange address. To find OpenSea sales, you MUST scan transaction receipts: get all tx hashes from the wallet, fetch each receipt via `eth_getTransactionReceipt`, and check if `receipt.to` equals an exchange address.
- Wyvern: `0x7f268357A8c2552623316e2562D90e642bB538E5`
- Seaport 1.1: `0x0000000000000068F116a894984e2DB1123eB395`
- Seaport 1.4: `0x00000000000000AdC04C56bF30aC9D3C0aAF14Dc`
- The old address `0x7f268357a8d2554763e816641b1f5b947a1c2d8a` is WRONG — don't use it.
Case: mintface.eth appeared to have 0 OpenSea interactions via getAssetTransfers, but receipt scanning revealed 279 Wyvern transactions. RD caught: "He has sold on OpenSea."

### 90. Don't assume "not geo-blocked" without a region signal (2026-07-20)
A non-Persian ENS and non-Persian art themes do NOT rule out geo-blocking. OFAC sanctions cover Cuba, North Korea, Syria, Crimea, Donetsk/Luhansk — not just Iran. When a wallet has zero OpenSea interactions and uses Foundation exclusively, geo-blocking is possible regardless of cultural signals. Without a clear regional indicator, classify as "block reason uncertain" rather than "not geo-blocked." Over-claiming "not geo-blocked" was wrong for mintface.eth — he's Australian and was an active OpenSea seller (279 Wyvern txs) whose activity was invisible to getAssetTransfers (see pitfall #89). The correct assessment requires ruling out the API blind spot FIRST before concluding geo-block.

### 91. Alchemy getNFTs is UNRELIABLE for ERC1155 holdings — use on-chain balanceOfBatch (2026-07-20, CRITICAL)
Alchemy's `getNFTs` API returned 0 ERC1155 tokens for meysvm despite the wallet holding 14 6529 Memes on-chain (verified via `balanceOfBatch` on the Memes contract `0x33FD426905F149f8376e227d0C9D3340AaD17aF1`). Alchemy's indexing of ERC1155 tokens for active traders (who move most holdings) is incomplete/stale. ALWAYS verify ERC1155 holdings via on-chain `balanceOfBatch` calls — never trust Alchemy getNFTs for ERC1155 counts. If TDH > 0 but Alchemy shows 0 NFTs, Alchemy is wrong, not the TDH. This affects Memes, Karen Army, and any other ERC1155 collection verification.

### 92. Alchemy getNFTs contract naming can be misleading — verify recipient address (2026-07-20)
Alchemy's `getNFTs` labels transfers with collection names that can be wrong. "OpenSea Shared Storefront" NFTs in outgoing transfer lists were actually sent TO Foundation (the proxy contract), not OpenSea. Always verify by checking the actual recipient contract address against the known addresses list (pitfall #55), not Alchemy's label. Misleading labels cause incorrect marketplace classification.

### 93. Deconsolidated profiles retain drops from before deconsolidation (2026-07-20)
Pitfall #80 noted that deconsolidation resets `created_at` and pitfall #84 noted the activity chart can zero out. Additionally: deconsolidated profiles may RETAIN drops posted while consolidated. The L5 @MintFace profile had 10 drops (in Intrepid Chat/Real Time Votes) that stayed after deconsolidation from @mintface.eth (L62). The deconsolidated wallet had 0 nonce — it was never used independently, only as a consolidation target. When assessing a low-level profile with drops but a zero-nonce wallet, check whether it was recently deconsolidated from a higher-level profile (same person, different identity). Don't treat it as a separate active user.

### 111. Bulk-rep API ADDS, not overwrites (2026-07-31, CRITICAL CORRECTION)
Previous pitfalls and documentation claimed the bulk-rep proxy token OVERWRITES existing rep. This is WRONG. Verified 2026-07-31: Mistershot had 29K MemesNominee rep, was given 10K via bulk-rep, and ended up with 39K (29K + 10K = additive, not overwrite). The give_nomination_rep.py script should send just the `amount` to add, NOT `current_rep + amount`. Sending `current_rep + amount` would DOUBLE the existing rep.

### 112. Proxy credit is limited — large rep gifts may fail (2026-07-31)
The bulk-rep proxy token has a finite credit budget. On 2026-07-07, 300K rep was distributed (10K × 30 artists). By 2026-07-31, only ~10K credit remained. Requests for 21K, 20K, and even 5K all failed with "Not enough proxy credit left to rate." Only 10K succeeded. When the proxy credit is low, give smaller amounts or wait for credit replenishment. Test with progressively smaller amounts if large ones fail.

### 113. No wave notifications on Seeking Nomination (2026-07-31, RD DIRECTIVE)
Do NOT post notification replies to the Seeking Nomination wave when giving rep. RD directive: "skip any posts in seeking nomination wave so that we don't spam it." The rep-giving script (`give_nomination_rep.py`) does not post wave replies. The cron agent reports results to Telegram only.

### 114. Rep categories endpoint is paginated (2026-07-31)
The correct endpoint for MemesNominee rep is `GET /profiles/{pid}/rep/categories?page=N` — returns `{data: [...], next: bool}`. Each category object has `category`, `total_rep`, `contributor_count`, `top_contributors`. The old endpoint `/profiles/{pid}/rep` returns 404. To find RD's contribution, scan `top_contributors` array for `profile.handle == "regulardad"`. Multiple pages may be needed — loop until `next` is false.

### 115. Data archiving for vetting reports (2026-07-31)
The data collection script saves two types of archive:
- **Dated reports**: `seen/vetting_reports/vetting_{date}.json` — full candidate report from each run
- **Per-profile**: `seen/vetting_reports/profiles/{handle}.json` — latest data per artist, overwritten each scan

This allows answering "what do we have on @artist?" without re-running the full script. To retrieve: `read_file(seen/vetting_reports/profiles/{handle}.json)`. The per-profile file includes `last_scanned` date and full on-chain + API data.

### 116a. run_assessment.py has broken imports — 4 functions missing (2026-08-02, CRITICAL)
The `run_assessment.py` script imports `get_cic_statements`, `get_nft_history_multichain`, `get_artwork_from_minted_collections`, and `analyze_artwork` from `seeking_nomination_vetting.py`, but these functions did not exist in the module. Subagents during the 2026-08-02 vetting session implemented them to fix the issue. If the script fails with ImportError, check whether these functions are present in the vetting library and implement them if missing. The functions should:
- `get_cic_statements(handle, token)` — fetch CIC statements from the identities CIC endpoint
- `get_nft_history_multichain(wallet, alchemy_key)` — fetch NFT transfers across ETH/Base/Polygon/Arbitrum/Optimism/Zora using Alchemy
- `get_artwork_from_minted_collections(wallet, token)` — extract artwork metadata from minted collections
- `analyze_artwork(artwork_list)` — basic artwork analysis (AI detection, perceptual hash)

### 116b. Alchemy getAssetTransfers returns identical cached results for different wallets (2026-08-02)
When querying `alchemy_getAssetTransfers` with `category: ["internal"]` for different wallet addresses in rapid succession, the API returned IDENTICAL transfer data (same block numbers, same ETH amounts, same from addresses) for completely different wallets. This was observed for Soliiiart (0x3afa...) and Superno (0xed61...) — both returned the same 6.0 ETH from 0x109c4f2ccc82c4... at blocks 0xc3bf/0xc3c5/0xc477. The blocks are very early (2015 era), which is impossible for wallets first active in 2021/2022. This is a caching bug in Alchemy's API.

**Fix**: When internal transfer results look suspicious (very early blocks, identical data across different wallets), fall back to Blockscout v1 API (`txlistinternal`) or Etherscan v2 for verification. Do NOT trust Alchemy internal transfer data without cross-checking against another source.

### 116c. Subagent vetting timeouts — use 300s timeout and prioritize key data (2026-08-02)
When delegating artist vetting to subagents via `delegate_task`, the 600s default timeout is insufficient for artists with complex on-chain history. 3 out of 10 subagents timed out during the 2026-08-02 session (HELLia x2, Soliiiart x2, Superno x1). Root causes: Blockscout API 429 rate limiting, Alchemy API timeouts, and subagents reading large skill files (pitfalls.md is 118KB).

**Best practices for subagent vetting**:
1. Set terminal timeout to 300s (not 600s) for the assessment script
2. Instruct subagents to prioritize: profile data → artist fields → wallet history → sales → social links. Skip deep Blockscout queries if slow.
3. If the script fails, gather data manually via 6529 API calls
4. For subagents that time out, the parent agent can complete the assessment manually using the partial data collected
5. Run max 3 subagents in parallel — more causes API rate limiting across all of them

### 117. Alchemy getNFTs may be fully unsupported on some API keys (2026-08-02)
`alchemy_getNFTs` returned "Unsupported method: alchemy_getNFTs" (error code -32600) on the current Alchemy key during the 2026-08-02 session. This is different from pitfall #91 (ERC1155 unreliability) — the method itself was rejected entirely, for both ERC721 and ERC1155.

**Fix**: Use `alchemy_getAssetTransfers` with `category: ["erc721", "erc1155"]` and `{from: wallet}` / `{to: wallet}` to enumerate NFT transfers. Group by `rawContract.address` to get collection-level holdings. For current holdings, compute net: (transfers TO wallet) - (transfers FROM wallet) per contract. This is less precise than getNFTs (no token-level metadata) but works reliably.

**Also**: `alchemy_getContractMetadata` also returned HTTP 400 for all contracts tested. Use `alchemy_getNFTMetadata` (for individual tokens) or on-chain `name()`/`symbol()` calls via `eth_call` instead.

### 118. Maybe's Dive Bar has no pagination — only returns ~50 recent drops (2026-08-02)
`GET /v2/waves/b38288e6-ca9d-45ce-8323-3dc5e094f04e/drops?limit=50` returns ~50 drops all from today, with `next_page_params: null` (no pagination). This means the Dive Bar is only useful for discovering TODAY's active community members, not historical posters. For historical candidate discovery, use the Seeking Nomination wave with `limit=200` instead.

### 119. Pre-filter SN wave candidates to exclude collectors (2026-08-02)
Not everyone who posts on the Seeking Nomination wave is an artist seeking nomination. Collectors and community members post there too. Before vetting, check each candidate's identity fields:

**SKIP if ALL true**: `active_main_stage_submission_ids` is empty AND `winner_main_stage_drop_ids` is empty AND `artist_of_prevote_cards` is empty AND rep categories show zero MemesNominee rep. They're a collector/community member.

**Case**: Piano (L38, TDH 198,112, 1 SN post) — high TDH and level suggested importance, but zero MS submissions, zero artist fields, rep only from "memes ftw" and "AOS" community categories. Wasted a subagent timeout (600s) before being identified as a collector.

### 120. Same person, multiple 6529 profiles — wallet funding as the link (2026-08-02, CONFIRMED CASE)
Related to pitfall #22. farnaz_dashti (L0, Rep 11, wallet 0xdbcc500d...) and FarnazDashti (L0, Rep 20, wallet funded by farnaz_dashti) are the same person. farnaz_dashti's wallet funded FarnazDashti's wallet. Both vetted separately in the same session before the link was discovered.

**Detection**: When two handles share a name fragment (farnaz_dashti / FarnazDashti), check if one wallet funded the other via `alchemy_getAssetTransfers` with `{from: wallet_A, to: wallet_B, category: ["external"]}`. If ETH transfers exist between them, they're likely the same person. Report both profiles in the same assessment.

### 121. Subagent vetting — 600s timeout insufficient for high-tx wallets (2026-08-02, UPDATED)
Pitfall #116c noted 600s subagent timeouts. This session confirmed: Piano (2,280 txs) and JMVPHOTOGRAPHY (4,128 txs) both timed out at 600s. The run_assessment.py script's multichain NFT history fetch is the bottleneck.

**Updated best practices**:
1. Pre-filter candidates (pitfall #119) to avoid wasting subagents on collectors
2. For wallets with >2000 txs, skip the assessment script entirely and gather data manually via targeted API calls
3. Run assessment script with `timeout 300` — if it doesn't finish, fall back to manual
4. Max 3 subagents in parallel — more causes Blockscout 429 rate limiting across all
5. Parent agent can complete timed-out assessments faster than subagents by making targeted calls instead of running the full script

### 122. Artist may mint from unconsolidated wallet — check artist_of_prevote_cards FIRST (2026-08-02, CRITICAL)
An artist's 6529 primary wallet may show ZERO mints, sales, or deployed contracts on-chain because they mint from a **different, unconsolidated wallet**. The vetting script will classify them as "collector, not artist" — wrong.

**Case:** @Bombadil has Meme Card #231 and posts artwork in their profile wave, but their 6529 primary wallet (`0x01e2fe`) showed zero on-chain activity. Their minting wallet is separate and not consolidated.

**Fix (3 layers):**
1. **Script**: Fetch `/identities/by-wallet/{address}` and check `artist_of_prevote_cards` — if non-empty, the candidate IS an established artist regardless of on-chain data on their 6529 primary wallet.
2. **Cron prompt**: Instruct the agent to check `artist_of_prevote_cards` FIRST before on-chain analysis. Also read ALL drop content (not just first 500 chars of first drop) for external art links — artists often post SuperRare/Foundation links in their profile wave.
3. **Skill**: This pitfall.

**Key insight**: The 6529 API has `artist_of_prevote_cards`, `active_main_stage_submission_ids`, `winner_main_stage_drop_ids`, and `is_wave_creator` fields that detect artists regardless of which wallet they mint from. These fields come from the 6529 backend and are the authoritative source. On-chain analysis of the 6529 primary wallet is supplementary.

**However**: These fields only catch 6529 Meme cards and Main Stage submissions. An artist with ONLY external platform work (SuperRare, Foundation) and no 6529 card will still show empty arrays. In that case, the agent must read the drop content for external art links and verify them by fetching the linked pages.

### 123. Vetting script counts ENS-linked self-transfers as sales (2026-08-03, CRITICAL)
The automated vetting script (`seeking_nomination_vetting.py`) reports "sales" by counting ETH transfers to the primary wallet without checking if the sender is a self-wallet. When an unconsolidated wallet shares an ENS root with a consolidated wallet (e.g., `seizar.eth` 0x421c05b4 → `vault.seizar.eth` 0x0e81a8a4), the script counts these self-transfers as sales. Case: seizar was reported with 14 "sales" / 0.9428 ETH — all were self-transfers between seizar's own wallets.

**Fix**: After the script runs, manually verify any reported sales by checking if the sender wallet's ENS name shares a root with the profile's wallet ENS names (e.g., `X.eth` and `sub.X.eth` are the same person). Query `GET /v2/addresses/{sender}` for the `ens_domain_name` field and compare against all profile wallet ENS names. If they share a root, reclassify as self-transfer, not sale. Related to pitfall #3 (exclude self-transfers) and pitfall #8 (find unconsolidated wallets via ENS), but this is the specific script failure mode where the unconsolidated wallet isn't in the profile's wallet list.

### 124. OpenSea SeaDrop factory contracts return 404 on OpenSea v2 API (2026-08-05)
SeaDrop is OpenSea's own drop mechanism, but collections created via `ERC721SeaDropCloneFactory` / `ERC1155SeaDropCloneFactory` return HTTP 404 on the OpenSea v2 stats endpoint (`/api/v2/collections/chain/ethereum/{addr}/stats`) and the bare collection endpoint. The NFTs exist on-chain (verifiable via Blockscout token instances and holder counts) but are invisible to the OpenSea API. Do NOT conclude "not on OpenSea" or "zero market traction" from the 404 — these are OpenSea-hosted drops with real sales (SeaDrop primary + Seaport secondary). Use on-chain data (Blockscout token transfers, holder counts, Seaport tx methods) to assess sales and collector base instead.

Case: @Tuskss has 6 collections on SeaDrop (Prix 181 holders, Dynamic Signals 1,046 holders, etc.) — all return 404 on OpenSea API despite being OpenSea products.

### 125. Vetting script inflates ETH revenue with bridge and swap router transfers (2026-08-05, CONFIRMED)
Related to pitfalls #5 and #68. The automated `seeking_nomination_vetting.py` script counts cross-chain bridge and swap router ETH transfers as sales, in addition to the exchange hot wallets already in pitfall #68. For @Tuskss, the script reported 4.74 ETH but real marketplace revenue was ~1.92 ETH — 2.82 ETH was inflated by non-sale transfers.

**Non-sale inflators to exclude** (beyond pitfall #68 exchange addresses):
- `spender` / MetaSwap (swap router): 0.518 ETH
- `MayanSwift` (cross-chain bridge): 0.249 ETH
- `RelayRouterV3` (gas relay/router): 0.204 ETH
- `Bridgers` (cross-chain bridge): 0.067 ETH
- WETH wrap/unwrap (0x0 sender or WETH contract): 0.039 ETH

**Fix**: After the script runs, categorize every incoming ETH transfer by source. Only count ETH from: SeaDrop drop proceeds, Seaport internal txs, marketplace contracts (Foundation, Manifold), and direct EOA payments paired with NFT transfers. Exclude all exchange, bridge, router, and WETH-wrap transfers.

### 126. Alchemy getNFTsForOwner totalCount counts ALL contracts, not just filtered contract (2026-08-07, CRITICAL)
Alchemy's `getNFTsForOwner` API returns a `totalCount` that represents the wallet's total NFTs across ALL contracts, even when `contractAddresses` filter is provided. For the ENTROPY collection editor wallet (0x2c3b3fea), Alchemy reported totalCount=626, but on-chain `balanceOf` for the specific contract returned only 11. The 626 was the wallet's total NFT holdings across all contracts, not just ENTROPY.

**Fix**: Always verify NFT holdings for a specific contract via on-chain `balanceOf(address)` (ERC721) or `balanceOfBatch` (ERC1155). Never trust Alchemy's `totalCount` or `ownedNfts.length` as the count for a specific contract — Alchemy's `contractAddresses` filter does not reliably scope the `totalCount` field. This is distinct from pitfall #91 (ERC1155 unreliability) and #117 (method unsupported) — here the method works but returns misleading aggregate counts.

### 127. OpenSea v2 events API requires API key — instant key available (2026-08-07, UPDATED)
The OpenSea v2 events endpoint (`/api/v2/events/collection/{slug}`) returns HTTP 401 without an API key, unlike the collection stats endpoint which works without a key.

**Instant API key**: POST to `https://api.opensea.io/api/v2/auth/keys` with no authentication required. Returns a free-tier API key valid for 7 days, rate-limited to 600 requests/hour. Save the key to `.opensea_key` in the profile directory. This eliminates the need to request keys in advance — create one on-demand when secondary market tracing is needed.

```python
import requests, json
resp = requests.post('https://api.opensea.io/api/v2/auth/keys', 
    headers={'Content-Type': 'application/json'})
key_data = resp.json()
# key_data contains 'api_key' and 'expires_at'
```

Alternatively, use the Alchemy key with `eth_getLogs` in 10-block chunks (Alchemy free tier limit) and paginate through the full block range — slow but functional. For a quick ownership check, scrape the OpenSea activity page HTML for wallet address frequency, but this gives only recent activity, not full history.

### 128. Vet identity pitfalls apply to ALL wallet analysis, not just formal vetting (2026-08-07, CRITICAL)
The identity verification pitfalls (#1 check 6529 API first, #8 find unconsolidated wallets, #22 multiple profiles, #33b delegated wallets) apply to ANY wallet identity analysis — not just formal Seeking Nomination vetting sessions. When investigating a collection or analyzing on-chain data and needing to identify who owns a wallet, the SAME verification chain applies:
1. Check `GET /identities/by-wallet/{address}` on the 6529 API FIRST
2. Check the `display` field for ENS name
3. Check delegations via `GET /delegations/{wallet}`
4. Check ENS subgraph for related wallets
5. Verify wallet links with ETH transfer evidence (pitfall #22 WARNING about false certainty)

**Case**: During ENTROPY collection analysis, a wallet holding 76 tokens was found and claimed as "mendezmendez's wallet" without checking the 6529 API. The 6529 API showed the wallet was `art-vault-mendez.eth` (L7, PSEUDONYM, no handle) — linked to but separate from the primary `mendezmendez.eth` (L23) wallet. RD corrected: "Are you using the profile vetting pitfalls to prevent these errors?" The pitfalls WERE in the skill but were not consulted because the task wasn't framed as "vetting."

**Fix**: Before claiming any wallet belongs to a specific person, run the 6529 API identity lookup. The `display` field gives the ENS name. Cross-reference with the person's known wallets. Never assume wallet ownership from holding patterns alone.

### 129. OpenSea events API can return massive datasets — stream to disk (2026-08-07)
The OpenSea v2 events API paginates at 100 events per page with cursor-based pagination. For actively traded collections, the total event count can be enormous — the ENTROPY collection (1,820 tokens, 4 days old) had 358,000+ sale events across 3,580+ pages. Holding all events in memory caused the script to consume 1.6GB RAM and timeout at 600s.

**Fix**: Stream events to a JSONL file as they're fetched. Keep only aggregate statistics (per-wallet buy/sell counts, price arrays) in memory. Write the raw events to `/tmp/{collection}_sales_stream.jsonl` for later re-analysis without re-fetching. Use `flush=True` on print statements for progress monitoring. Run as a background process with `notify_on_complete=True` for collections with >10,000 expected events.

**Pagination pattern**:
```python
next_cursor = None
while True:
    params = {'event_type': 'sale', 'limit': 100}
    if next_cursor:
        params['cursor'] = next_cursor
    resp = requests.get(url, params=params, headers=hdrs)
    events = resp.json().get('asset_events', [])
    for e in events:
        out_file.write(json.dumps(record) + '\n')
    next_cursor = resp.json().get('next')
    if not next_cursor:
        break
    time.sleep(0.15)  # Rate limit: 600/hr
```

### 131. OpenSea events API pagination CYCLES — dedup or waste hours (2026-08-07, CRITICAL)
The OpenSea v2 events API cursor-based pagination can CYCLE — returning the same events in an infinite loop. For the ENTROPY collection, the API returned 360,000+ "sale events" across 3,600+ pages, but there were only ~100 unique sales. The cursor never returns `null` — it loops back to the beginning. This wasted over 30 minutes of compute and 1.6GB RAM chasing duplicates.

**Fix**: ALWAYS dedup by a composite key `(token_id, timestamp, buyer, seller, transaction_hash)` as you paginate. Stop when a page returns 0 new unique records. Track `seen_keys` as a set and compare `new_count` per page — if `new_count == 0`, break immediately. Example detection: page 2 returned 100 events but 0 were new → duplicate cycle confirmed → stop.

```python
seen_keys = set()
while True:
    # ... fetch page ...
    new_count = 0
    for e in events:
        key = (token_id, timestamp, buyer, seller, tx_hash)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        # process new record
        new_count += 1
    if new_count == 0:
        break  # duplicate cycle
```

**The `events/collection/{slug}` endpoint cursor is fundamentally broken — it returns the SAME cursor every time, cycling the same 100 events.** The `occurred_before`/`occurred_after` timestamp filters also don't help — they return the same 100 most recent events regardless of the timestamp range.

**Working workaround — `events/accounts/{wallet}` endpoint**: This endpoint has a DIFFERENT cursor that actually paginates forward. To collect ALL sales for a collection:
1. Get the initial 100 sales from `events/collection/{slug}` (page 1)
2. Extract all unique buyer/seller wallet addresses
3. For each wallet, call `GET /api/v2/events/accounts/{wallet}?event_type=sale&collection={slug}` with cursor pagination — this endpoint's cursor works correctly and returns different pages
4. Dedup across all wallets by composite key
5. For each unique sale, fetch the NFT metadata to get the "Revealed" trait (only ~50% of token IDs will have trait data via the NFT endpoint — the rest need individual `GET /api/v2/chain/ethereum/contract/{addr}/nfts/{tokenId}` calls)

This approach found 7,662 unique sales for ENTROPY vs the 100 returned by the broken collection cursor.

### 132. OpenSea events API field names and price parsing (2026-08-07)
The OpenSea v2 events API uses different field names than expected:
- **Buyer/seller**: `s.get('buyer', '')` and `s.get('seller', '')` — NOT `to_address`/`from_address` (those return `'?'` or empty strings)
- **Token ID**: `nft.get('identifier', '?')` — NOT `token_id`
- **Revealed trait**: Check `nft.get('traits', [])` for `trait_type == 'Revealed'`, value `'Yes'` or `'No'`
- **Price**: `payment = s.get('payment', {})`, then `price = int(payment['quantity']) / (10 ** int(payment.get('decimals', 18)))`. The `quantity` field is a wei string (e.g., `'63000000000000000'` = 0.063 ETH). Payment may be in ETH (`token_address` = `0x000...000`) or WETH (`token_address` = `0xC02aaA39...`).
- **Event keys**: `['event_type', 'event_timestamp', 'transaction', 'order_hash', 'protocol_address', 'chain', 'payment', 'closing_date', 'seller', 'buyer', 'quantity', 'nft']`

### 130. OpenSea NFT holdings count is stale vs on-chain balanceOf (2026-08-07)
The OpenSea v2 API `GET /api/v2/chain/ethereum/account/{wallet}/nfts?collection={slug}` returns NFTs the wallet has HELD, not necessarily currently holds. For the ENTROPY vault wallet (0x35a9), OpenSea returned 980 NFTs but on-chain `balanceOf` returned 76. The OpenSea API caches historical holdings and does not reflect transfers/sales that occurred off OpenSea or after indexing lag.

**Fix**: Always verify current holdings via on-chain `balanceOf(address)` (ERC-721) or `balanceOfBatch` (ERC-1155) using an RPC call. Never trust OpenSea's NFT count as the current holdings count — it is an upper bound that includes sold/transferred tokens. Related to pitfall #126 (Alchemy totalCount) but distinct — here the API returns stale holdings data, not aggregate counts.

### 133. Vetting script can misattribute another candidate's drops to the current candidate (2026-08-08, CRITICAL)
The `seeking_nomination_vetting.py` data collection script can populate `winner_ms_drop_ids` and `active_ms_submission_ids` for a candidate using data from a DIFFERENT candidate. Case: @acxlitch's report showed `winner_ms_drop_ids: ['3f60d391...']` and `active_ms_submission_ids: ['c26de106...']` with `is_wave_creator: true`, but the identity API (`GET /identities/{handle}`) returned empty arrays for all three fields — the drops actually belonged to @tito (already vetted the prior day). The misattributed drop IDs also return 404 on `GET /drops/{id}` and `GET /identities/{profile_id}` because they belong to a different profile.

**Fix**: After the vetting script runs, ALWAYS cross-check `winner_ms_drop_ids`, `active_ms_submission_ids`, `is_wave_creator`, and `artist_of_prevote_cards` against the live identity API (`GET /identities/{handle}`) before using them to classify the candidate or decide whether to skip rep. If the script's fields show non-empty but the API returns empty (or the drop IDs 404), the script misattributed — trust the API, not the script output. Do NOT skip a candidate as "already an MS winner" based solely on the script's `winner_ms_drop_ids` without verifying via the identity API.

### 134. give_nomination_rep.py was sending current_rep + amount despite bulk-rep ADDING (2026-08-11, CRITICAL)
Pitfall #111 documented that the bulk-rep API ADDS rep, not overwrites. However, the `give_nomination_rep.py` script still contained the old logic: `rep_to_send = current_rep + amount_to_send`. Since the API adds, this caused every rep gift to DOUBLE the intended amount — the script sent `current + 10K`, the API added that to the existing `current`, resulting in `current + current + 10K` instead of `current + 10K`.

**Damage**: Loop was sent 50K (intended 10K) — went from 40K to 90K MemesNominee (40K overpaid). acxlitch was sent 30K (intended 10K) — went from 20K to 40K (10K overpaid). The Aug 9 vetting report incorrectly stated "10K (40K → 50K)" and "10K (20K → 30K)" — the agent trusted the script's `amount` field in the JSON input, not the `rep_to_send` value the script actually sent. The Aug 10 daily review also missed this, reporting "10K rep given" when 30K was actually sent.

**Fix applied**: Changed `rep_to_send = current_rep + amount_to_send` to `rep_to_send = amount_to_send` in `give_nomination_rep.py`. Also updated the docstring and `vetting-cron-architecture.md` reference. The state file's `amount` field now records the amount sent (not current+amount), making future audits accurate.

**Lesson**: When a pitfall documents a behavioral change in an API, verify that ALL scripts and documentation that reference the old behavior are updated — not just the pitfalls file. The pitfall was added on 2026-07-31 but the script was never fixed. Always grep for the old pattern after documenting a correction.

### 135. Vetting script can produce phantom addresses from internal transaction parsing (2026-08-09)
The `seeking_nomination_vetting.py` script reported address `0xab48082d` as a micro-transaction sale source for BOTH @Loop and @acxlitch (sub-0.001 ETH amounts in Aug 2026). On-chain checks via Blockscout showed this address has zero transactions and zero balance — it's not a real wallet. The address likely appeared due to internal transaction parsing artifacts (trace data producing addresses that don't correspond to actual EOAs or contracts).

**Fix**: When a sale source address appears for multiple unrelated candidates, or when the ETH amounts are suspiciously tiny (sub-0.001 ETH), verify the address exists on-chain via `GET /v2/addresses/{addr}` before treating it as a real counterparty. If the address returns zero transactions/balance, exclude it from the assessment as a parsing artifact. Do NOT use phantom shared addresses as evidence of a connection between candidates.

### 136. SuperRare Sovereign contracts are legitimate SuperRare (2026-08-11, CRITICAL)
SuperRare operates a "Sovereign" NFT system (`SovereignNFTContractFactory`) where each artist gets personal ERC-721 contracts deployed via SuperRare's factory. These are NOT the SuperRare V1 (0x41A322) or V2 (0xB932a7) contracts from pitfall #7 — they are separate, artist-specific contracts. Sales revenue comes from the "SuperRare Payments" contract, not the V1/V2 marketplace contracts.

**Do NOT dismiss Sovereign contracts as "not SuperRare"** just because transfers don't appear on V1/V2. The artist IS on SuperRare — verify by checking: (a) contract was deployed via `SovereignNFTContractFactory`, (b) revenue comes from a "Payments" contract (not the NFT contract itself), (c) artist posted a superrare.com/{handle} link in their profile wave. This is distinct from the Chonkly SuperRarer knockoff (pitfall #7) — Sovereign is the real SuperRare platform.

Case: @flostitanarum had 3 Sovereign collections (Amerta, LOVE, VITA) with 6.11 ETH revenue from SuperRare Payments — all legitimate SuperRare sales, zero transfers on V1/V2.

### 137. Vetting script can return EMPTY artist fields when API calls fail mid-run (2026-08-11, CRITICAL)
Related to pitfall #133 (script misattributing another candidate's data) but the OPPOSITE failure mode: the script returns EMPTY arrays for `active_ms_submission_ids`, `winner_ms_drop_ids`, and `is_wave_creator: false` when the 6529 API returns errors (404, expired token, rate limit) during the data collection phase. This makes a real artist look like a non-artist, risking incorrect SUSPICIOUS classification or skipping artist verification.

Case: @flostitanarum's script output showed all artist fields empty (`active_ms_submission_ids: []`, `is_wave_creator: false`), but the live API returned `active_main_stage_submission_ids: ["bf4bba14..."]` and `is_wave_creator: true`. A 404 error during the script run caused partial data collection.

**Fix**: After the script runs, ALWAYS cross-check `active_ms_submission_ids`, `winner_ms_drop_ids`, `is_wave_creator`, and `artist_of_prevote_cards` against the live identity API (`GET /identities/{handle}`) before classification — same fix as pitfall #133, but now covering both directions (script over-reporting AND under-reporting). If the script shows empty but the API shows non-empty, the API is authoritative. Do NOT classify a candidate as "not an artist" based solely on the script's empty artist fields.

### 138. run_assessment.py times out for high-activity wallets (2026-08-13)
The `run_assessment.py` script times out (300s+) for wallets with 1,000+ ETH transactions and 900+ NFT transfers. The Blockscout API pagination (10+ pages of 100 txs each, with 0.3-0.5s delays) makes the script take 5+ minutes for established artists with long on-chain histories. Case: @Choen (1,073 ETH txs, 991 NFT transfers, 306 internal txs) — the script timed out at 300s, 280s, and 240s, producing zero output. The agent had to fall back to manual direct API calls.

**Fix**: For candidates where the script times out, run the assessment manually via direct Blockscout API calls. Prioritize: (1) ETH transaction list (first page for wallet age, deployment count), (2) NFT transfer list (mints/sent/received counts, unique contracts), (3) Internal transactions (revenue by sender). Use `timeout 120` for each API call batch. Consider adding a `--max-pages` flag to the script to limit pagination for high-activity wallets.

### 139. Artist collections may be deployed by platform factory contracts, not the artist's own wallet (2026-08-13)
An artist's own NFT collections may be deployed by platform factory contracts (Manifold, KnownOrigin, etc.) rather than the artist's primary wallet. Checking `creator_address_hash` on Blockscout will return the factory address, not the artist. Case: @Choen has 9 Choen-named collections, but only 4 were deployed by Choen's wallet (0x0b2095ed). The other 5 were deployed by factory addresses: 0x3B612a5B49 (Choen, OBSIDIAN), 0xf3CD1E9326 (CLITSR, ChoenLeeMoon), 0x61b98ACbfc (Choen Lee's Dream World), 0x4B7A8Ce7d0 (ChoenLeeKO). The artist is still the creator — they minted from these contracts (34 mints from the main "Choen" contract).

**Fix**: Do NOT conclude "not the artist's own collection" just because `creator_address_hash` doesn't match the profile's primary wallet. Platform factory contracts (Manifold ERC721LazyPayableClaim, KnownOrigin, etc.) deploy on behalf of artists. Verify artist ownership by checking: (a) the artist minted tokens from the contract (NFT transfers with `from=0x0` to the artist's wallet), (b) the artist sent tokens from the contract to marketplaces (Foundation, OpenSea), (c) the collection name matches the artist's handle/brand. Related to pitfall #136 (SuperRare Sovereign) but applies to all platform factory contracts, not just SuperRare.

### 140. MemesNominee rep is spread across multiple category names — threshold check must sum all Meme-related categories (2026-08-13)
The 6529 rep categories API (`GET /profiles/{id}/rep/categories`) returns rep broken down by category name, and there are MULTIPLE Meme-related category names that all count toward the MemesNominee threshold. Case: @Choen had rep in 5 Meme-related categories: "Meme Artist" (36,553), "The Memes Artist" (5,342), "MemesNominee" (4,000), "Meme artist" (500), "Meme Artist SZN 7" (420) — total 46,815. The "MemesNominee" category alone was only 4,000. If the vetting script's `memes_nominee_rep` field only captures the "MemesNominee" category, it would severely undercount and give rep to artists who are actually over the 50K threshold.

**Fix**: When checking the 50K MemesNominee threshold, sum ALL Meme-related rep categories from the API, not just the one named "MemesNominee". Known Meme-related category names include: "MemesNominee", "Meme Artist", "Meme artist", "The Memes Artist", "Meme Artist SZN 7", and potentially others. Query `GET /profiles/{id}/rep/categories` and filter for categories where the name contains "meme" (case-insensitive). Sum their `total_rep` values and compare against the 50,000 threshold.

### 141. run_assessment.py xTDH extraction misses consolidation/identity endpoint fallback (2026-08-15)
The `run_assessment.py` script extracts xTDH via `profile_data.get("xtdh")` and `p_raw.get("xtdh")` but does NOT check `consolidation.get("xtdh")` or the identities endpoint (`GET /identities/{handle}`). TDH has a consolidation fallback (`tdh = profile_data.get("tdh", 0) or p_raw.get("tdh", 0) or consolidation.get("tdh", 0)`), but xTDH does not. Case: @thegameworld's script output showed `xTDH: 0`, but the identities endpoint returned `xTDH: 112.73`. This makes a candidate look like they have zero cross-wallet TDH when they actually have meaningful xTDH.

**Fix**: After the script runs, cross-check xTDH against `GET /identities/{handle}` if the script reports xTDH: 0 but the candidate has non-zero TDH or a high level. Alternatively, patch `run_assessment.py` to add `consolidation.get("xtdh", 0)` as a fallback, mirroring the TDH extraction pattern.

### 142. DEX-routed NFT sales produce 0 unique collectors — buyers are invisible (2026-08-15)
When an artist sells NFTs through DEX aggregator routers (MetaMaskSwapRouter, AggregationRouterV6, RainbowRouter), the `is_marketplace_contract` function correctly classifies the router as a marketplace and excludes it from the collector list. However, the NFT goes artist→router→buyer, and the script only tracks the first hop (artist→router). The actual buyer's wallet never appears in `collector_wallets` because the router is excluded and the second hop (router→buyer) is not in the artist's transfer list. Result: `Unique collectors: 0` even when the artist has 14+ sales. Case: @thegameworld had 14 sales (0.4961 ETH) through MetaMaskSwapRouter, AggregationRouterV6, and RainbowRouter, but `Unique collectors: 0`.

**Fix**: When `Unique collectors: 0` but `Sales (NFT-verified)` is non-zero, check whether sales are routed through DEX aggregators. If so, the 0-collector count is a script limitation, not evidence of fake sales. Note this in the assessment — the sales are real (ETH received matches NFT transfers out), but the buyer identities are obscured by the router layer. Do NOT cite "0 collectors" as a suspicious signal when DEX-routed sales explain it.

### 143. Manual WETH spot-checks massively undercount sales — always run the full multichain script (2026-08-15, CRITICAL)
Manually checking a small sample of recent WETH transfers (e.g., 50 transfers) can undercount total sales by 100x+. Case: @arsonic — manual WETH lookup showed ~11.5 ETH across both wallets, but the full multichain assessment script revealed **1,826 verified sales totaling 1,632.63 ETH** across Ethereum (955), Base (10), Arbitrum (9), and Optimism (2). Deployed contracts were also undercounted: 2 (manual) vs 5 (script — 3 Ethereum, 2 Base). NFT transfers: 272 (manual) vs 1,120 (script across 5 chains, 600 mints).

**Fix**: NEVER report sales figures from manual WETH transfer spot-checks. Always run the full multichain assessment script (`run_assessment.py` or `seeking_nomination_vetting.py`) which fetches ALL NFT transfers and verified sales across Ethereum, Base, Arbitrum, Optimism, Polygon, and Zora. Manual spot-checks miss: (a) historical sales beyond the recent window, (b) sales on L2 chains (Base, Arbitrum, Optimism), (c) sales paid via internal txs or ERC-1155 lazy claim contracts, (d) the full count of deployed contracts across chains. If the script times out (pitfall #138), fall back to direct multichain API calls, NOT to recent-transfer sampling. Related to pitfall #4 (fetch ALL pages) but distinct — this is about chain coverage and temporal coverage, not just pagination.