# @blake69 ↔ @bicasso — Cross-Profile Identity Analysis (2026-07-12)

## Question
Are blake69 and bicasso the same person? Community speculation based on both being pepe.wtf artists.

## Wallets
- **blake69**: 0x0f274ecd2ce987912f757175e753651d63d2a178 (blake69.eth)
- **bicasso**: 0x2a2d672a4eb7ddf5791bc91511078ce18ddedad5 (billynfteesvault.eth) + 0x66f377542600304ea500228481bc1ae740ca943f (billynftees.eth)

## All Direct ETH Transfers Between blake69 and Bicasso Wallets: 7 total

**53 total ETH transfers** between all wallets in this investigation:
- 7 between blake69 ↔ Bicasso wallets (cross-person)
- 47 between Bicasso's own two wallets (billynftees ↔ billynfteesvault, self-management)

### Cross-Person Transfers (blake69 ↔ Bicasso): 7

#### Round-Trips (2 — STRONGEST signal)

**Jan 25, 2024:**
- 18:24 — blake69 → billynfteesvault.eth: 0.002260 ETH
- 18:28 — billynfteesvault.eth → blake69: 0.002970 ETH
- **4 minutes apart, near-equal amounts**

**Mar 26, 2023:**
- 20:42 — blake69 → billynftees.eth: 0.003381 ETH
- 21:13 — billynftees.eth → blake69: 0.003400 ETH
- **31 minutes apart, near-equal amounts**

#### One-Way Transfers (3, spanning Feb 2023 → Feb 2024)

| Date | Direction | Amount | Notes |
|---|---|---|---|
| Feb 13, 2023 | billynftees → blake69 | 0.125000 ETH | Largest one-way |
| Oct 4, 2023 | blake69 → billynftees | 0.010000 ETH | |
| Feb 13, 2024 | blake69 → billynftees | 0.005750 ETH | Anniversary of Feb 13 transfer? |

#### Summary

Small amounts over a year+ (Feb 2023 → Feb 2024). Round-trips are strongest signal — sending ETH and getting it back within minutes is hard to explain as arm's-length. One-way transfers could be payments, gas funding, or splitting auction proceeds.

### Bicasso Self-Transfers (billynftees ↔ billynfteesvault): 47

Bicasso moving ETH between his own two wallets — normal self-management:
- Large consolidations: 1.700 ETH (Aug 2023), 1.054 ETH (Nov 2023), 0.210 ETH (Oct 2023), 0.140 ETH (Sep 2023)
- Small round-trips: 0.007→0.002 (9 min), 0.007→0.003 (24 min), 0.011→0.220 (61 min), 0.001→0.0006 (2 min)
- Continuing through 2025 into 2026 — most recent May 15, 2026

**METHODOLOGY NOTE**: When checking transfers between profiles, always distinguish cross-person transfers from self-transfers between one profile's own wallets. Report both counts separately. The full transfer inventory (not just round-trips) provides context on the nature of the relationship.

## Shared Intermediary EOAs (personal wallets, NOT exchanges)

### @696969 (0xcc797ecd)
- 6529 profile exists
- 19 unique recipients total (personal wallet)
- Sends to BOTH blake69 and billynftees.eth
- Active: Jul 2022 → May 2024 (2 years of overlapping payments)
- Pattern: alternates sending small amounts (0.003–0.04 ETH) to both

### 0x440538cb (no ENS)
- 36 unique recipients
- Sends to ALL THREE wallets: blake69, billynfteesvault, billynftees
- bicasso sent to this wallet repeatedly in Jan–Feb 2023

### memeablesbtc.eth (0xc16ea8)
- 112 recipients, 68 ETH outgoing
- Sends to both profiles

### memeablesauctions.eth (0x6d2645)
- 44 recipients, 5 ETH outgoing
- Sends to both profiles

## Shared Exchange Addresses
- Coinbase (0xdfd5293d): blake69 recv 1.22 ETH, bicasso recv 2.40 ETH
- Binance (0x28c6c062): both received
- Binance (0x9696f59e): blake69 recv 3.94 ETH, bicasso recv 0.52 ETH
- Binance (0x56eddb7a): both received
- Binance (0x4976a4a0): both received
- Binance Old (0x21a31ee): both received

## Shared Contract Interactions (both sent ETH to)
- Seaport (6 contract variants)
- WETH9 (0xc02aaa39)
- UniversalRouter (Uniswap)
- Foundation (0x00000000adc0)
- ERC1155LazyPayableClaim (Manifold)
- ERC721LazyPayableClaim (Manifold)
- ERC1155BurnRedeem / ERC721BurnRedeem
- SeaDrop
- ETHRegistrarController (ENS)
- 0x3a3548e060be (Manifold Minting Wallet on 6529)

## 36 Total Shared Counterparties

## Shared Marketplace Contracts (expected for same-community artists)
- TL Universal Deployer (both deployed contracts via it)
- Foundation marketplace
- Seaport
- Manifold mint contracts

## Differences
- Different ENS names (blake69.eth vs billynftees.eth/billynfteesvault.eth)
- Different X handles (@_blake69 vs @BillyNFTees)
- Different wallet ages (627 days vs 1,489 days)
- blake69: 634K rep, Level 53; bicasso: 108K rep, Level 26
- bicasso has self-buying between own wallets; blake69 does not

## Conclusion
**On-chain evidence SUPPORTS same-person speculation.** Direct ETH round-trips between their wallets (within minutes, near-equal amounts) are the strongest signal. Shared personal intermediary wallets (@696969 with only 19 recipients) that send to both over 2 years cannot be explained by community overlap alone. Initial analysis that found "no connection" was incorrect — it only checked direct wallet links, missing the intermediary relay patterns.

## Memeables Auction Wallets

### memeablesbtc.eth (0xc16ea8)
- EOA, active Sep 2023 → Apr 2024 (223 days)
- 111 recipients, 33.9 ETH in / 34.4 ETH out — pass-through
- 30+ 6529 members receive payouts: @guruG (3.65 ETH), @RareScrilla (1.32), @nft_lady_007 (0.99), @SASHA_CHUDO (0.75), @Bicasso (0.68), @Kero (0.52), @blake69 (0.12), @Viva_la_Vandal, @BASQKEK, @normancomics, @VSTRVL, @JonathanLittle, @Wyn, @c0rnh0li0, @ojovivo, @arlekin_julia, @GOD_ALMIGHTY, @Ndhoz_dotule, @Coriot, @Visionquest, @Zoku, @CostaJpeg, @PONPOP, @fabianospeziari, @3panelcrimes, @cloudnake, @Farnaz, @Robapuros, @Elispri, @Rodro, @MAB
- Top senders: @guruG (7.35 ETH), 0xgazpacho.eth (5.06), axecapital.eth (2.77), @RareScrilla (0.78), @Kero (0.61), @Bicasso (0.58), @blake69 (0.086)

### memeablesauctions.eth (0x6d2645)
- EOA, active Mar 2024 → Oct 2024 (212 days) — started as memeablesbtc wound down
- 43 recipients, 2.55 ETH in / 2.50 ETH out
- 6529 members receiving: @Bicasso (0.26), @Kero (0.13), @SASHA_CHUDO (0.09), @blake69 (0.03), @cloudnake, @Zoku, @normancomics, @Anaphoraen, @KinKinetic, @Rodro, @Farnaz, @696969
- Senders: @Kero (0.34), @Bicasso (0.20), @blake69 (0.077), @Visionquest, @c0rnh0li0, @Zoku, @Robapuros, @MAB, @cloudnake, @nft_lady_007, @JonathanLittle, @SASHA_CHUDO

### Role
These are **manual community auction payout wallets** for a meme art auction group. Members bid, sell, and get paid through them. 30+ 6529 community members participate. Both blake69 and Bicasso are active participants. These wallets alone do NOT prove same-person — they're shared infrastructure. But combined with direct wallet round-trips and @696969's small personal wallet pattern, the overall case strengthens.

## @696969 Full Recipient Breakdown (18 recipients)
- **6529 members**: @blake69 (0.244 ETH), @Bicasso (0.020 ETH)
- **Contracts**: UniversalRouter (1.51 ETH), Seaport, ERC1967Proxy, SatoshiSkulls, SomethingIsComing, Proxy, Simpepen
- **Unknown EOAs**: 0xf80e6bb2 (1.01 ETH), 0x5e809a85 (0.245, likely exchange — 788 recipients), 0x612a10c2 (0.157), 0xaa0147ee (0.058), 0x0ec68f15 (0.047), 0xb8cd35ab (0.010), 0x91fe0ec7 (0.010)
- **Senders to @696969**: @blake69 (0.505 ETH, biggest), 0x5e809a85 (0.430), 0xf80e6bb2 (0.290), 0x0ec68f15 (0.102), @Bicasso (0.020), Binance (0.026+0.010), memeablesauctions (0.009)

## Methodology Notes
- Use Blockscout v1 API for ETH txs (v2 with filter params returns 422)
- 6529 `/identities/{handle}` wallets array uses key `wallet` not `address`
- Must check internal txs too (`txlistinternal`)
- Scripts: cross_ref_blake_bicasso.py, cross_ref_timing.py, cross_ref_deep.py, analyze_memeables_full.py
- To check if a wallet address has a 6529 profile: `GET /identities/{address}` — if `handle` exists and doesn't start with `id-`, it's a real profile
- To classify shared counterparties: check `is_contract` on Blockscout v2, recipient count (small = personal, large = exchange), ENS name, and 6529 profile lookup