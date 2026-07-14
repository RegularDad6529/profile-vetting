# 6529 API Artist Credentials — CHECK FIRST

**CRITICAL lesson from @arsonic review (2026-07-13)**: The initial review concluded "NOT an artist — collector/trader only" based on on-chain wallet analysis showing 4,900 NFT transfers but zero distributions from his own deployed contracts. This was **completely wrong**. Arsonic is a recognized artist: 2x Main Stage winner ("Pepe X", "AUTONOMY.EXE"), artist of Meme Card #37, and co-creator of Pebbles (NextGen 6529) as half of @zeeblocks.

## Root Cause

Dived into on-chain wallet analysis without first checking the 6529 API fields that DIRECTLY establish artist credentials. The API already knows who is an artist — just wasn't reading those fields.

## MANDATORY FIRST STEP

Before any on-chain wallet analysis, check these fields from `GET /identities/{handle}`:

1. **`artist_of_prevote_cards`**: Array of Meme Card numbers the profile created. If non-empty, they are a recognized 6529 artist. Example: arsonic has `[37]`.
2. **`winner_main_stage_drop_ids`**: Array of Main Stage drop IDs they won. If non-empty, they are an ESTABLISHED 6529 artist. Fetch each drop via `GET /drops/{id}` to get the title and details. Example: arsonic has 2 wins — "Pepe X" (serial 52390) and "AUTONOMY.EXE" (serial 848053).
3. **`is_wave_creator`**: Boolean — they run a curation wave, indicating community leadership.
4. **`active_main_stage_submission_ids`**: Current active Main Stage submissions.

**If any of these are non-empty, the profile IS an artist.** On-chain wallet analysis is then SUPPLEMENTARY — it adds context about collector activity, marketplace revenue, and platform presence, but does not override the 6529 API's artist designation.

## Why On-Chain Wallet Analysis Alone Is Insufficient

The on-chain picture may be incomplete due to:
- **Collaborative wallets not consolidated in the profile** (see below)
- **Art deployed on 6529's own contracts** (The Memes, NextGen) rather than personal contracts
- **Blockscout not indexing proxy contracts** — arsonic's ARSC/ARSE/ARSxTW contracts show 0 transfers on Blockscout but may have art on them
- **Artist work on other platforms** (Art Blocks, Solana) under a different name/wallet
- **Main Stage wins minted on The Memes contract** — these are 6529 ecosystem NFTs, not personal contract deployments

## Collaborative / Duo Wallet Pattern

Artist duos may deploy their collaborative work under a SEPARATE wallet that is NOT consolidated in either artist's 6529 profile. On-chain analysis of only the consolidated wallets will miss their collaborative artistic output.

### Case Study: @arsonic + @zeeblocks
- arsonic's 6529 profile consolidates: arsonic.eth, sgtpepeworld.eth
- Pebbles (NextGen 6529, collection 1, supply 1000) is deployed by ze-blocks.eth (0xb033daedca) — NOT in arsonic's consolidated wallets
- ze-blocks.eth is the Zeeblocks duo wallet — arsonic is "half of @zeeblocks"
- ETH flows between arsonic.eth and ze-blocks.eth confirm the collaboration (revenue sharing: arsonic sends 590+314+904 ETH to ze-blocks, ze-blocks sends 12,101 ETH back)
- ze-blocks.eth has NO 6529 profile

### How to detect collaborative wallets
1. Check 6529 profile bio, CIC statements, and wave posts for mentions of a duo/collaboration
2. Look for ETH transfers between the profile's wallets and other EOAs that suggest revenue sharing (large round-trip transfers)
3. Check if the collaborative wallet deployed any contracts or is the artist on NextGen/Art Blocks collections
4. The collaborative wallet may not have a 6529 profile at all

## NextGen 6529 Contract

The NextGen 6529 contract (`0x45882f9bc325e14fbb298a1df930c43a874b83ae`) allows artists to deploy generative art collections on 6529's own infrastructure. This is a significant artist credential.

### How to check if a profile is a NextGen artist
1. Get the profile's NextGen token IDs from their NFT transfer history
2. Call `viewColIDforTokenID(uint256 tokenId)` to get the collection ID
3. Call `retrieveArtistAddress(uint256 collectionId)` to get the artist wallet
4. Compare the artist wallet to the profile's wallets AND any collaborative wallets
5. Call `retrieveCollectionInfo(uint256 collectionId)` to get collection name, description, website

### Contract function selectors (keccak256 first 4 bytes)
- `viewColIDforTokenID(uint256)`: 0xfa92668a
- `retrieveArtistAddress(uint256)`: 0xb9902968
- `totalSupplyOfCollection(uint256)`: 0xf18332dd
- `retrieveCollectionInfo(uint256)`: 0xd0950271
- `newCollectionIndex()`: total collection count
- Call via: `POST https://eth.blockscout.com/api/eth-rpc` with `eth_call` method

### Case Study: Pebbles (NextGen collection 1)
- Artist: ze-blocks.eth (0xb033daedca) — the Zeeblocks duo, includes arsonic
- Supply: 1000
- Description: "Generative art collection that captures the organic diversity of stones..."
- Website: https://zeblocks.com/
- License: CC0
- This is the ONLY NextGen collection on 6529 (total collections: 2, but collection 2 is empty)

## Collector vs Artist Classification (CORRECTED)

A profile can be BOTH a heavy collector AND an artist. Do NOT classify someone as "not an artist" just because they have thousands of collector NFT transfers. Check 6529 API artist fields and collaborative wallets FIRST.

### How to distinguish collector revenue from artist revenue
1. **Artist revenue**: ETH from selling own-created NFTs (own contracts, 6529 contracts, platform mints where they're the artist)
2. **Collector revenue**: ETH from reselling NFTs they bought from other artists (marketplace payouts for pieces they collected)
3. **Mixed profiles**: Many 6529 artists are also serious collectors. Report both activities separately. Do not let the collector activity overshadow the artist credentials.

### Case Study: @arsonic (CORRECTED)
- 6529 API: 2x Main Stage winner, Meme Card #37 artist, wave creator → IS an artist
- Collaborative: Pebbles on NextGen 6529 via ze-blocks.eth (with @zeeblocks)
- Collector activity: 4,900 NFT transfers (Asterix, Checks, Pepe, Art Blocks collecting)
- Collector revenue: 2,209 ETH from Foundation = resale of Inevitable Rise #6 (collector flip, NOT artist revenue)
- Artist revenue: Revenue from Main Stage wins + Pebbles (via ze-blocks wallet, shared with duo partner)
- Deployed contracts: 7 (ARSC, ARSE, ARSxTW, ERC721) — proxy contracts, Blockscout shows 0 transfers but may not index them
- Art Blocks: 38 mints as collector (OnChainChain, Fernweh, Cryptoblots, Chromie Squiggle) — not his artist work
- **Classification**: ESTABLISHED artist AND collector. Both activities are real.
- **Lesson**: The initial "NOT an artist" conclusion was wrong because I didn't check 6529 API fields first, didn't check for collaborative wallets, and didn't check NextGen 6529 contract. On-chain wallet analysis alone is insufficient — the 6529 API is the primary source for artist credentials.

## Organization-Owned Artist Profiles

An artist may operate through both an individual profile AND an organization profile. The organization profile can have its own Main Stage wins, wallets, and deployed contracts.

### Case Study: @hugofaz + @casanua
- hugofaz: Level 86, GOVERNMENT_NAME (real name), 2x MS winner (Crypto Atlas, Flipped), Meme Card #30 artist
- casanua: Level 66, ORGANIZATION, 3x MS winner (Formosa 6529, 6529 Memes at the Boys' Club, PEBBLES at Domínio PúbliCC0)
- 5 combined MS wins — among the most decorated 6529 artists
- 3 wallets each (vault/social/primary), linked by 15 ETH transfers between hugofaz and casanua wallets
- hugofaz: 13 deployed contracts (HF*Ed, HFAZ*, HFCryptoArtEd), photography practice (100 Nude Shoots of Hugo, SOMBRA, Portraits, The World Today)
- casanua: 3 deployed contracts (NUALM, GMNUA), Formosa 6529 collection (30 mints distributed)
- hugofaz Foundation revenue: 25,759 ETH — BUT includes massive collector resales (Sebastiao Salgado "Amazonia" ~21K ETH, Bruce Gilden photography)
- casanua Foundation revenue: 153 ETH (single payout, Oct 2021)
- hugofaz Manifold revenue: 166 ETH (artist edition drops)
- Both: zero SuperRare, zero SuperRarer/Chonkly

**Lesson**: When a profile owns or is linked to an organization profile, check BOTH for artist credentials. The organization may have more MS wins than the individual. Use ETH transfers between the wallets to confirm the ownership link.

## Pure Collector with MS Wins

A profile can have Main Stage wins (artist credential) AND zero on-chain artist revenue (pure collector on-chain). The artist output lives on 6529's own contracts (The Memes), not personal contracts or external marketplaces.

### Case Study: @blocknoob
- Level 86, PSEUDONYM, 2x MS winner (Memetic Curator, Let This Meme IN), wave creator
- 4 wallets: blocknoob.eth (original, Jan 2021), vault.blocknoob.eth, memes.blocknoob.eth, noobmuseum.eth
- 0 NFTs minted from own contracts, 0 marketplace revenue as artist
- 2 deployed contracts (noobgm, ERC1155Creator) — both 0 NFT transfers (unused)
- 1,692 NFT transfers on original wallet — massive collector
- Foundation: 234 tokens bought, 84 resold — 191K ETH in Foundation payouts (ALL collector resales, 0 artist mints)
- Real SuperRare: 4 tokens (collecting)
- Zero SuperRarer/Chonkly
- 64 Foundation NFTs bulk-transferred from noobmuseum to blocknoob.eth (self-transfer)

**Lesson**: MS wins alone confirm artist status — do NOT require external marketplace revenue to classify as an artist. Some 6529 artists create exclusively for The Memes ecosystem and have no external art sales. Collector activity (even massive) does not negate artist credentials.

## Corrected Assessment Workflow Order

1. **6529 API artist fields** — `artist_of_prevote_cards`, `winner_main_stage_drop_ids`, `is_wave_creator`, `active_main_stage_submission_ids`
2. **Fetch Main Stage drop details** — titles, ratings, raters count for each win
3. **Profile bio / CIC statements** — look for collaboration mentions, platform references
4. **Collaborative wallet detection** — check ETH transfers for revenue-sharing patterns
5. **NextGen 6529 check** — scan all collections for the profile's wallets
6. **On-chain wallet analysis** — NFT transfers, marketplace revenue, contract deployments
7. **Distinguish artist vs collector revenue** — categorize all ETH by source
8. **Classification** — synthesize API credentials + on-chain data + community engagement