# @handle — Profile Overview

## 6529 Community
- Level X | Rep X | CIC X | TDH X
- CLASSIFICATION
- Wallet active since MONTH YEAR (~X years) — per-wallet first ETH tx dates (pitfall #30b)
- X MS wins, X prevote cards, wave creator: yes/no

## Wallets (N, all in 6529 profile)
- **ens.eth** (0x...) — first tx MONTH YEAR (X days) — TDH X
- Additional ENS names resolving to this wallet

### Linked wallets (not in 6529 profile)
- If any found via ENS subgraph, list here with 6529 profile if exists (pitfall #33)
- Also search by ENS name directly: {domains(where:{name:"handle.eth"})} (pitfall #34)
- **Delegated wallets** (pitfall #33b): treat as consolidated — include their on-chain activity, NFT holdings, sales, and mints. May have no ENS at all. Discovery: ENS subdomain search, linked wallet 6529 profile check, community knowledge.
- Do NOT claim identity links based on transactions alone (pitfall #22)

## Artist Work
- X deployed contracts, X NFTs minted from own contracts
- MS wins, prevote cards, wave creator
- Collaborative wallets if applicable (pitfall #2)

## Wave Activity
- X active days out of 365 (via activity API, pitfall #31)
- Recent activity samples
- Profile wave if exists

## Collector Activity
- X NFT transfers, ~X held, X collections

### Top 3 Purchases (pitfall #32, #46)
1. Collection #ID by Artist Name — X.XX ETH — Date
2. Collection #ID by Artist Name — X.XX ETH — Date
3. Collection #ID by Artist Name — X.XX ETH — Date
- Match ETH out to NFT in by block number. Split cost if multiple NFTs bought/minted in same block (pitfall #46)

### Top 3 Sales (pitfall #32, #46)
1. Collection #ID by Artist Name — X.XX ETH — Date
2. Collection #ID by Artist Name — X.XX ETH — Date
3. Collection #ID by Artist Name — X.XX ETH — Date
- Match ETH in (regular + internal txs) to NFT out by block number. Split if multiple sold in same block.

### The Biggest L (pitfall #40, #50)
- Collection #ID: bought X.XX ETH → sold X.XX ETH = -X.XX ETH (Date)
- Note if one collection dominates the losses
- NO subjective commentary — do not add "moderate", "catastrophic", "relatively disciplined". Just report numbers.

### Biggest Wins (pitfall #50)
- Collection #ID: bought/minted X.XX ETH → sold X.XX ETH = +X.XX ETH
- Show top 3-5 wins alongside the losses for balance
- NO subjective commentary — let the numbers speak

### Failure to Transact (pitfall #41)
- X failed transactions, X.XXX ETH lost to gas on failed txs

### Minted: LOL (pitfall #42)
**Part A — Still holding the bag**:
- X NFTs across Y collections with no transfer activity in 90+ days (Z% of holdings are dead)
- N NFTs they PAID to mint are in dead collections — X.XX ETH spent, current value ~0 ETH
- List worst offenders (highest mint cost, longest dead period)
- Shared-contract platforms (Art Blocks): contract alive but tokens unmoved — break down by project (tokenId//1000000), list project name + artist, do NOT call the contract "dead"

**Part B — Already dumped for dust**:
- X NFTs they PAID to mint, then sold/transferred for <0.005 ETH (no OTC payment within ±48h)
- Total spent minting: X.XX ETH. Total received: 0.00 ETH. Net loss: X.XX ETH
- Worst offenders (highest mint cost → 0 ETH sale)
- Note if one collection dominates
- Separate count of free-mint LOLs if significant
- Free mint = 0 ETH cost. Any non-zero ETH paid is a PAID mint, no matter how small (pitfall #51)
- Exclude OTC deals (payment in separate tx within ±48h)

### Mints from Public Contracts (when > 50)
- Game mechanic mints (DNT etc.): X
- Actual collecting mints: X across Y collections
- Top 10 minted collections with counts (pitfall #30c)
- Include artist names where possible (pitfall #30c)

### Notable collections (by net held)
- Collection (N held), Collection (N held)...
- 6529 ecosystem: NextGen (N), Gradient (N), Karen Army (N), 6529Complaints (N) (pitfall #37)
- Art/established: Art Blocks (N)...

### Foundation (pitfall #9)
- NFT counts only, never gross ETH

### SuperRare (pitfall #38)
- SuperRare: X bought, Y sold, Z held (NOT "SuperRarer")

### Most flipped (actual sales, exclude burns — pitfall #30)
- Collection (N sold), Collection (N sold)...
- Exclude transfers/gifts (no ETH received) — report separately (pitfall #43)

### Transfers (not sales)
- X NFTs sent out with no ETH received (gifts/airdrops/community operations)

## 6529 Ecosystem
- List all ecosystem holdings: Gradient, NextGen, Karen Army, dwellers, 6529er Collection, The Memes, Seize And Share, SeizerDAO, 6529Complaints (pitfall #37)
- Do NOT say "minimal ecosystem engagement" if TDH is significant (pitfall #39)
- Do NOT label as "pure 6529 ecosystem" (pitfall #39b)
- Use specific collection names, not broad keywords like "regular" or "meme" (pitfall #39c)

## Notable Non-6529 Holdings
- List top non-ecosystem collections by count held
- Broad collectors hold across many ecosystems — report factually, let reader draw conclusions

## On-Chain Notes
- Suspicious patterns or lack thereof
- Key observations

## Review Date
YYYY-MM-DD

---
## Clean/Feedback Version (pitfall #35)
Produce a second file `references/{handle}-feedback.md` for sharing with the artist:
- No raw contract addresses or hex values
- No "pitfall #X" references or framework terminology
- No internal on-chain analysis details
- Same data, cleaner presentation
- Do this proactively — don't wait for RD to ask