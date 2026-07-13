# Profile Vetting Skill

On-chain artist evaluation methodology for the 6529 ecosystem. Developed for vetting Seeking Nomination wave artists, but applicable to any profile evaluation that requires verifying on-chain activity, sales history, wallet networks, and marketplace presence.

## What This Does

Evaluates artists by examining:
- **On-chain sales history** — verified ETH/NFT transfers, not just balance changes
- **Wallet network analysis** — bridge wallets, consolidation patterns, counterparty mapping
- **Marketplace presence** — SuperRare, Foundation, OpenSea, Exchange.art (Solana), Manifold, Transient Labs
- **Multi-chain scanning** — Ethereum, Base, Polygon, Arbitrum, Optimism, Zora
- **Wash trading detection** — ERC-721 same-token round-tripping, circular ETH flows, marketplace escrow filtering
- **Artwork verification** — on-chain IPFS artwork from artist's own contracts, multi-gateway fallback
- **Rep/TDH/CIC analysis** — 6529 reputation categories, contributor breakdown, deconsolidation detection
- **Social verification** — CIC statements, Exchange.art profiles, Twitter cross-referencing

## Key Principles

- **No fabricated data** — every claim backed by real API output
- **Sales must be NFT-verified** — pure ETH transfers without NFT movement are NOT sales
- **Internal transactions matter** — marketplace payouts (SuperRare, Seaport, TL Auction House) come via internal txs
- **L2 activity is weaker signal** — Ethereum mainnet matters most for art
- **Wallet age doesn't prove authenticity** — real signals are verified socials, hand-made artwork, distinct buyers
- **English only** — filter Unicode scam token names from on-chain data

## Contents

- `SKILL.md` — Full methodology, API endpoints, rules, pitfalls
- `scripts/seeking_nomination_vetting.py` — Main vetting engine (1998 lines)
- `scripts/run_assessment.py` — Standalone runner for individual profile assessments (312 lines)
- `references/` — 24 case studies and reference documents

## API Endpoints Used

- **6529.io**: Profiles, identities, wallets, CIC statements, rep categories, drops, waves
- **Blockscout** (v1 + v2): Transactions, internal txs, NFT transfers, token holdings (6 chains)
- **Exchange.art**: Profile search, NFT creation/ownership, sales stats, series/collections
- **IPFS gateways**: dweb.link, cloudflare-ipfs.com, gateway.pinata.cloud

## Case Studies

24 reference files covering:
- 10 Seeking Nomination artist assessments
- Cross-profile investigations (blake69/bicasso, ZODL network, kiramoto/metpenfaul)
- Methodology notes (Exchange.art API, wash trading detection, sale verification)

## License

MIT