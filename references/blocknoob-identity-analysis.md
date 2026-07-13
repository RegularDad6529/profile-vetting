# Blocknoob — On-Chain Identity Investigation

## Date
July 12, 2026

## Profile
- **Handle**: @blocknoob
- **Level**: 86
- **Classification**: PSEUDONYM
- **Rep**: 2,390,996
- **TDH**: 8,624,717
- **xTDH**: 268,389
- **CIC**: 361,220 (100 contributors)

## Wallets
| Wallet | ENS | Type | Txs |
|---|---|---|---|
| 0x3df7131fbd4f6b27be8317c69e41817498e1bc0c | vault.blocknoob.eth | Contract (Safe) | 4 |
| 0x52cc2c8db59411310e130b47d478472d9f7e4597 | memes.blocknoob.eth | EOA | 217 |
| 0x564a8e13d7dd23d5525160d204165bdbcb69b4db | noobmuseum.eth | Contract | 5 |

## Self-Doxing Discovery (CRITICAL FINDING)

**X/Twitter handle: @blocknoob_**
- Display name: "blocknoob 🦇🔊⌐🆇-🆇"
- Twitter ID: 1366325647421952002
- PFP: https://pbs.twimg.com/profile_images/1762421602719866880/ao2YPOh4_200x200.jpg
- Banner: https://pbs.twimg.com/profile_banners/1366325647421952002/1697509768

**How found**: Blocknoob posted `https://x.com/blocknoob_/status/2074627670885716004` directly in his profile wave "The Three Keys" (wave ID: ffee87fb-2a7e-4be5-82c2-d96ff4385930). This was a regular CHAT drop, not a CIC statement — CIC statements returned empty for socials.

**LESSON**: Profile wave drops MUST be checked for self-doxing links. CIC statements alone are insufficient. The initial analysis concluded "Cannot identify real person" — this was wrong. The user pointed out the missed tag.

## On-Chain Counterparties (49 total, top 10 by volume)

| Address | ENS/Name | 6529 Profile | ETH Total | Direction |
|---|---|---|---|---|
| 0xcaac2b43... | seize.6529.eth (GnosisSafe) | — | 17.30 | Sent (6529 main) |
| 0x8930d2d2... | rememes.6529complaints.eth | @6529complaints | 12.05 | Both (3.57 sent, 8.47 recv) |
| 0xfdbced08... | — | @lol | 11.25 | Both (3.92 sent, 7.33 recv) |
| 0x6d7c4477... | SuperRareBazaar | — | 9.44 | Sent (marketplace) |
| 0x9458e297... | ReserveAuctionFindersEth | — | 7.48 | Sent (marketplace) |
| 0x4b76837f... | — | @6529Deployer | 7.05 | Received (platform payments) |
| 0xbdc4a5c0... | blocknoob.eth | @famous | 6.44 | Both (3.13 sent, 3.31 recv) |
| 0xc02aaa39... | WETH9 | — | 3.52 | Sent (DEX) |
| 0x26bbea78... | ERC1155LazyPayableClaim | — | 3.32 | Sent (minting) |
| 0x2638c0c7... | justkidding.eth | — | 2.93 | Both (1.82 sent, 1.11 recv) |

## Key Findings

### Community Role
- **2x Main Stage winner**: "Memetic Curator" (interactive HTML game, 71.8M votes, 1st place) and "Let This Meme IN" (video, 51.9M votes, 1st place)
- **Wave creator**: Runs "The Three Keys" — a curation group that got 9/16 submissions into the 6529 Network Museum
- **Curated with guest curators**: Rep'd @JustinAversanoV, @cathsimard, @davekrugman (300K each) and @aida_studios (100K) for curation help
- **Active Meme Club voter**: Ranked #26 in participation stats (0.12x TDH multiple, 1 drop voted)

### Financial Relationships
- @6529complaints: 12 ETH across 12 txs over 2+ years (largest personal relationship)
- @lol: 11 ETH across 24 txs over 2+ years
- @famous: 6.4 ETH — holds the original blocknoob.eth ENS name (different person)
- @6529Deployer: 7 ETH received (platform payments, Dec 2025 + Jun 2026)

### ENS Notes
- vault.blocknoob.eth and memes.blocknoob.eth are subdomains of blocknoob.eth
- blocknoob.eth (parent) is owned by @famous, NOT @blocknoob
- noobmuseum.eth is a separate ENS name (smart contract wallet)

### No Exchange Deposits
- No Coinbase, Binance, or Kraken addresses in transaction history
- All counterparties are 6529 community members or NFT marketplace contracts
- Trail to real-world identity goes through X account, not through exchange KYC

## Meme Club Activity
- **Meme Club Wave ID**: d23af421-203d-4e37-abc1-4d9df840026c
- Posted in Meme Club: replied to @gpebbles' suggestion about auto-adding submissions ("This is such a good feature")
- Tagged in @TheManager's participatory drops as a Main Stage voter
- Appears in participation stats posts (ranked #26, 0.12x TDH multiple, 1 drop voted)
- **Self-doxing X link was found in profile wave drops, NOT Meme Club** — the user initially said "you missed the tag in Meme Club" referring to the 6529.io wave URL, but the actual self-doxing link (`https://x.com/blocknoob_/status/...`) was posted in blocknoob's own profile wave "The Three Keys", not in Meme Club. Always check ALL wave drops for a profile, not just Meme Club.