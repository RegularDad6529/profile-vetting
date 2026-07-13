# @Superno — Assessment (2026-07-12)

## Classification: LIKELY REAL — prolific newcomer, low sales but strong artistic output

## Profile
- Wallet: 0xed618bcdb0a85d7166d85c712e2a74be4c2c0a2d
- Rep: 50,101 | TDH: 0 | xTDH: 0 | Level: 19 | CIC: rating=0, contributors=100

## Social Links
- Bio: "Portuguese digital artist exploring abstract art, glitch art, collage. Uses P5.js, Photoshop, Illustrator..."
- Manifold, Linktree, OpenSea, Instagram, X, Transient (7 platforms)

## On-Chain (Multichain — 4 chains)
- L1: 488 transfers, 249 mints, 3 sales
- Base: 393 transfers, 217 mints, 0 sales
- Optimism: 17 transfers, 4 mints, 0 sales
- Zora: 27 transfers, 20 mints, 1 sale
- Combined: 925 transfers, 490 mints, 4 sales (0.29 ETH), 40 collectors (SCRIPT BUG — see below)
- 20 deployed contracts (16 TL Universal Deployer, 4 NFT minting)
- Wallet age: 289 days

## CORRECTION: Actual collector count
- Script reported "40 collectors, 214 sent" — INFLATED by marketplace escrow
- Actual outgoing transfers: 37 (not 214)
  - 21 to TL Auction House (marketplace listings, not collectors)
  - 7 to burn address (minting mechanics)
  - ~9 to real EOA wallets (actual distributions)
- Unique actual recipients: ~7 (not 40)
- Collections actually distributed: Passage Through the Unreal (7), ORBStract (7), 2026 Gallery (5), VÍCIO SINTÉTICO (5), Beyond Time (4)

## Collector Count CORRECTION
- Script reported "40 collectors, 214 sent" — INFLATED
- Actual breakdown of 256 outgoing NFT transfers:
  - 99 to TL Auction House (marketplace escrow = listings, NOT collectors)
  - 58 to burn address (minting mechanics)
  - 26 to TransparentUpgradeableProxy (OpenSea listing proxy)
  - 18 to TransparentUpgradeableProxy on Base (marketplace listing)
  - 16 to Foundation (AdminUpgradeabilityProxy = listing)
  - ~5 to other contracts
  - ~13 to 6-7 real EOA wallets (1-2 NFTs each)
- **Real collectors: ~6-7 people**
- Bug fixed in vetting script: marketplace contracts now excluded from collector count

## Collection
- "2026 Gallery" / "Passage Through the Unreal"
- Artwork: "The Silence Between Worlds", "After Leaving Reality", "Silent Journey"
- Also: ORBStract, VÍCIO SINTÉTICO, Beyond Time, Subconscious, Lost Lines

## Sales
- 2022-09-22: 0.095 ETH (Foundation)
- 2024-03-30: 0.095 ETH (Foundation)
- 2024-05-22: 0.0004 ETH (ProtocolRewards - royalty)
- 2026-04-23: 0.0975 ETH (TL Auction House)
- 67 non-sale micro-transfers (0.0002-0.0009 ETH)

## Artist Activities
- 286 listings (185 NFT minting contract, 101 TL Auction House)
- 99 platform mints, 60 configured drops

## Strengths
- 7 social platforms, detailed bio (Portuguese, glitch art, P5.js)
- 20 deployed contracts — most among newcomers
- 490 mints, 286 listings, 60 drops — prolific output
- Multiple named collections
- No deceptive patterns

## Concerns
- Only 4 sales (0.29 ETH) despite 490 mints and 286 listings
- Only ~6-7 real collectors (not 40)
- 289-day wallet
- 67 non-sale micro-transactions
- CIC rating=0
- L2-heavy activity
- Most "sent" NFTs are marketplace listings, not actual distributions