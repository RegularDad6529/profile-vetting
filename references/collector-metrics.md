# Collector Activity — Five Signature Metrics (ALL REQUIRED)

Every collector activity section must include ALL five metrics. See `templates/assessment-template.md` for the full output format.

## 1. Top 3 Purchases + Top 3 Sales
- Match ETH to NFT by block number (pitfall #29, #32)
- Include artist names where possible (pitfall #30c) — e.g. "Fidenza #797 by Tyler Hobbs"
- Format: `Collection #ID by Artist Name — X.XX ETH — Date`
- **Multi-mint cost splitting** (pitfall #46) — if multiple NFTs bought/minted/sold in same block, divide total ETH by count
- **Seaport internal txs** (pitfall #47) — sale payments often come via internal tx from Seaport, always check `txlistinternal`

## 2. The Biggest L + Biggest Wins
- Worst NFT trade by P&L (pitfall #40)
- Match buy price (ETH out + NFT in, same block) and sell price (ETH in + NFT out, same block) for same (contract, tokenID)
- Report: collection, token ID, buy price, sell price, P&L, dates
- Note if one collection dominates the losses
- Also report Biggest Wins (top 3-5 positive P&L trades) for balance
- **NO subjective commentary** (pitfall #50) — do not add "moderate", "catastrophic", "relatively disciplined". Just report numbers. What's big for one person is nothing for another.
- **Multi-mint cost splitting** (pitfall #46) — if multiple NFTs minted/bought/sold in same block, divide ETH by count for per-unit cost
- **Seaport internal txs** (pitfall #47) — sale payments often come via internal tx from Seaport contract, check `txlistinternal` not just `txlist`

## 3. Failure to Transact
- Count failed txs (isError='1' or txreceipt_status='0' in Blockscout v1 API) (pitfall #41)
- Total gas lost = gasUsed × gasPrice / 1e18 for each failed tx
- Format: "X failed transactions, Y ETH lost to gas on failed txs"

## 4. Minted: LOL — Two Parts (pitfall #42)

### Part A — Still holding the bag
- NFTs currently held where collection has had NO transfer activity in 90+ days
- For each held collection, find last transfer timestamp in NFT history
- If >90 days → dead market, no offers likely
- Report: count of dead collections, total NFTs held, which ones they PAID to mint (mint_cost > 0.005 ETH)
- These are the funniest — they paid to mint something nobody will buy
- **Shared-contract platforms** (pitfall #42): Art Blocks uses one contract for hundreds of projects. Do NOT call Art Blocks "dead" — break down by project (tokenId//1000000), list project name + artist. Note which projects are actively traded vs genuinely dead. See `references/art-blocks-projects.md`.
- **"Dead" = no MARKET activity** (pitfall #42): check if the collection has a market, not just if the wallet's tokens moved. Without OpenSea/Reservoir API key, use general knowledge for well-known collections. Note the limitation.

### Part B — Already dumped for dust
- NFTs minted (from 0x0, including paid mints) and later sold for <0.005 ETH
- For each candidate: (1) check mint_cost, (2) check OTC payments within ±48h from recipient, (3) only count as LOL if NO OTC payment found
- Report paid-mint LOLs and free-mint LOLs separately, total ETH spent, total received
- **Free mint = 0 ETH cost** (pitfall #51) — any non-zero ETH paid is a PAID mint, no matter how small (0.007 ETH is NOT a free mint)

## 5. Most Flipped + Foundation/SuperRare Lines
- Most flipped: actual sales only, exclude burns (pitfall #30)
- Foundation: NFT counts only, never gross ETH (pitfall #9)
- SuperRare: "SuperRare" NOT "SuperRarer" (pitfall #38). Format: `SuperRare: X bought, Y sold, Z held`

## Additional Required Elements
- Per-wallet first ETH tx dates for wallet age (pitfall #30b)
- Mint breakdown: game mechanics vs collecting, top 10 with artist names (pitfall #30c)
- 6529 ecosystem checklist includes 6529Complaints (pitfall #37)
- Do NOT say "minimal ecosystem engagement" if TDH is significant (pitfall #39)
- Always produce clean feedback version (pitfall #35)