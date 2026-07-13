# Seeking Nomination — Vetting Status

## Completed Assessments
| Handle | Classification | Date | Key Stats |
|---|---|---|---|
| @Papillon | ESTABLISHED | 2026-07-11 | 151 sales (41.28 ETH), 151 collectors, SuperRare photographer |
| @sonyart | ESTABLISHED | 2026-07-11 | 58 sales (11.36 ETH), 9 contracts, 77 collectors, 218 SN posts |
| @MahsaAli | LIKELY REAL | 2026-07-11 | 57 sales (4.40 ETH), 5 years, hand-made digital paintings |
| @Jpearlking | LIKELY REAL w/ concerns | 2026-07-13 | 25 sales (2.34 ETH), SuperRarer 56x [Chonkly, NOT SuperRare], 5 contracts, 14 collectors, 2yr sales gap |
| @Chumwizards | LIKELY REAL | 2026-07-11 | 61 sales (0.50 ETH), 48 collectors, 5 social links, 180-day wallet |
| @Superno | LIKELY REAL | 2026-07-12 | 490 mints, 20 contracts, ~7 real collectors, 4 sales (0.29 ETH), 289-day wallet |
| @Shakirastract | LIKELY REAL (newcomer) | 2026-07-11 | Base chain only, hand-made StarDust art, 7 mints, 1 sale |
| @no_t_body | UNCLEAR | 2026-07-12 | 224 mints, 1 sale (0.01 ETH), 1 collector, conceptual art, 50K rep |
| @MisoM | UNCLEAR | 2026-07-11 | Collector profile, self-purchase, 215 mints/2 collectors, no original art |
| @BITUA | SUSPICIOUS | 2026-07-11 | 5 real sales (0.24 ETH), circular ETH, AI artist, 240-day wallet |
| @blake69 | ESTABLISHED | 2026-07-12 | 50 sales (10.50 ETH), 627-day wallet, pepe.wtf artist, 10 6529 community collectors |
| @bicasso | ESTABLISHED | 2026-07-12 | 247 sales (18.14 ETH), 1489-day wallet, self-buying between own wallets, 673 non-sale ETH transfers |

## Skipped
| Handle | Reason |
|---|---|
| @EMOJI | No wallet linked, empty profile — no on-chain data |

## Cross-Profile Analyses
| Profiles | Question | Conclusion | Date |
|---|---|---|---|
| blake69 ↔ bicasso | Same person? | On-chain evidence SUPPORTS same-person. Direct ETH round-trips (min apart, near-equal), 4 shared personal EOAs, 36 shared counterparties | 2026-07-12 |
| kiramoto ↔ Metpenfaul | Same person / coordinated? | SUSPICIOUS. Bridge wallet 0xdcf17058 connects them. Simultaneous profile creation. Metpenfaul has 25K MemesNominee from previous identity (deconsolidation). Unverifiable collector claims. | 2026-07-13 |

## Additional Assessments (non-SN)
| Handle | Classification | Date | Key Stats |
|---|---|---|---|
| @kiramoto | NEW w/ suspicious connection | 2026-07-13 | 2 OpenSea sales (0.20 ETH, Mar 2023), 6 mints, 0 contracts, 3.3yr wallet, dive bar active, bridge wallet to @Metpenfaul |

## All Seeking Nomination profiles assessed ✅

## Script Fixes Applied (2026-07-11/12/13)
1. Social links: `get_cic_statements()` returns flat dict, not nested under "socials"
2. False sales: Only count ETH as sale if marketplace contract or NFT recipient
3. Internal transactions: Added `txlistinternal` fetch for marketplace payouts
4. Profile data: Use `/identities/{handle}` not `/profiles/{handle}`
5. Posts: Use `/v2/waves/{wave_id}/drops` filtered by author, not `/profiles/{handle}/posts`
6. Blockscout 403: Added User-Agent header
7. Collector count: Exclude marketplace contracts and burn address from `unique_collectors`
8. Sales categorization (2026-07-13): Contract-routed ETH from artist's OWN contracts (SuperRarer, Manifold) = sales. Only exchange withdrawals excluded. Jpearlking corrected from 8 sales/2.02 ETH to 25 sales/2.34 ETH.
9. SuperRarer ≠ SuperRare (2026-07-13, CRITICAL): "SuperRarer" (0xc360ceca, symbol SRR) is a Chonkly platform contract, NOT SuperRare (0x41A322, symbol SUPR) or SuperRareV2 (0xB932a7). Deployed by chonkly.eth. NOT indexed on OpenSea. Jpearlking and Beam assessments corrected — both had zero real SuperRare transfers. Papillon uses real SuperRareV2 (confirmed legitimate).
10. Community wave check (2026-07-13): Always check maybe's dive bar for engagement before reporting "zero 6529 engagement"
11. Rep categories API (2026-07-13): `GET /profiles/{id}/rep/categories` reveals rep contributors and detects deconsolidation/reconsolidation

## Cross-Profile Methodology (added 2026-07-12)
- Blockscout v2 with filter params returns 422 — use v1 API (`txlist` + `txlistinternal`)
- 6529 `/identities/{handle}` wallets array uses key `wallet` not `address`
- Check: direct round-trips, shared personal EOAs, shared exchange deposits, timing analysis, shared contract interactions
- Scripts: cross_ref_blake_bicasso.py, cross_ref_timing.py, cross_ref_deep.py

## Issues Still Open
- **Collector count inflated by marketplace escrow** — fix applied for Superno but all profiles may need re-run with corrected counts
- Artwork image URLs returning "?" for all profiles (IPFS fetching needs fixing)
- Rep breakdown endpoint not returning data (using total from identity instead)
- Assessment thresholds may need tightening (BITUA scored ESTABLISHED before manual review)
- blake69: 498 non-sale ETH transfers not investigated
- bicasso: 673 non-sale ETH transfers not investigated