# @BITUA — Assessment (2026-07-11)

## Classification: SUSPICIOUS

## Profile
- Wallet: 0xc9f1c6bf13375790959b798e4e6d2a82b2be6601
- Rep: 67,992 | Level: 20 | CIC: 200
- Self-described "AI Artist" (X bio)

## Social Links
- X: @bitua388_bitua (verified) — bio says "AI Artist / Illustrator & Painter"
- SuperRare, Manifold, Instagram, Transient, Link

## On-Chain (L1 only matters)
- 82 L1 transfers, 37 mints, 24 sales totaling 0.0085 ETH (micro-transactions, avg 0.00035 ETH/sale)
- Wallet only 240 days old (Nov 2025)
- VIBES collection: 13 tokens, all sent to TL Auction House (listing)
- Only 2 real collectors: TL Auction House escrow + @Darbles (L6, 2 NFTs)

## Sales Verification (Critical Finding)
- **24 "sales" were FALSE** — pure ETH transfers between BITUA and buyer wallet 0x9298cb8d... with NO NFT transfers
- After fix: 5 real sales (0.2390 ETH) from TL Auction House and TLStacks contracts
- Circular ETH flow: buyer sends 0.0019 ETH, BITUA sends 0.0030 ETH back (BITUA pays buyer)

## Buyer Wallet Network
- 0x9298cb8d... — plain EOA, no 6529 profile, zero ETH balance
- No NFT transfers between buyer and BITUA
- 0x6d7c4477... (buyer's main counterparty) = SuperRareBazaar marketplace contract (NOT suspicious — normal listing/delisting)
- Buyer mints own NFTs (TEXTURED, Daughters of Eternal Flame) — separate from BITUA

## Rep
- 67,992 total. @gpebbles (L100) ~30.5K (45%), @johndoe8891 (L88) 30K
- 4 categories but concentration from 2 givers

## Key Concerns
- Self-described AI artist
- Circular ETH flow with empty buyer wallet
- Fake sales count (24 → 5 real)
- 240-day wallet
- Only 2 real collectors
- No profile wave