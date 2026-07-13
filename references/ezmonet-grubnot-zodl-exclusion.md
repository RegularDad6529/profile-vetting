# ZODL Network Exclusion Cases

## Date
July 12, 2026

## Context
After identifying the ZODL network (11 profiles, 864 direct ETH transfers), three candidate profiles were checked against the network to determine if they belonged.

## EzMonet — EXCLUDED
- **Level**: 84, 3 wallets
- **Direct transfers to ZODL**: Zero
- **Shared counterparties**: 26 — ALL smart contracts (Seaport, Manifold, ERC1155LazyPayableClaim, WETH9, GnosisSafe, WyvernExchange)
- **Exchange relay**: None — no deposit/withdrawal reciprocal pattern
- **Shared personal EOAs**: Zero (no addresses under 50 recipients shared)
- **ENS overlap**: None (ezmonet.eth, momonet.eth vs memeticobjects.eth family)
- **Airdrop false positives**: 4 high-volume addresses (540-569+ recipients) sending micro-amounts TO both EzMonet and ZODL — these are airdrops, not exchange relays
- **Conclusion**: Not part of ZODL network

## grubnot — EXCLUDED
- **Level**: 68, 3 wallets (grubnot.eth, 0x883b..., 0xff4f...)
- **Direct transfers to ZODL**: Zero
- **Shared counterparties**: 22 — all contracts and airdrops
- **Exchange relay**: None
- **Shared personal EOAs**: Zero
- **ENS overlap**: None
- **One coincidence**: Both grubnot and ZODL minted "SlicesOfTIMECovers" on same day (Feb 11, 2022, 14 min apart, both 0.100 ETH) — public mint, anyone could participate
- **Conclusion**: Not part of ZODL network

## andi_p — EXCLUDED
- **Level**: 36, 2 wallets (andi-p.eth, vault.andi-p.eth)
- **Direct transfers to ZODL**: Zero
- **Shared counterparties**: 30
- **Exchange overlap**: Both received from same Binance (0x56eddb7a, 583+ recipients) and Coinbase (0xdfd5293d, 423+ recipients) and Binance Old (0x21a31ee1, 413+ recipients) addresses
  - BUT: ZODL withdrawals all in mid-2021, andi_p's start late 2021 and continue through 2025 — NO temporal overlap
  - Exchange hot wallets are shared by thousands of users — not a linkage signal without timing overlap
- **Shared personal EOAs**: 1 — @hexum (mint.hexum.eth, 18 recipients)
  - ZODL received 0.003 ETH from @hexum (Feb 2024)
  - andi_p SENT 0.327 ETH to @hexum (Aug 2024)
  - Different directions, no round-trip — @hexum is a mutual community contact, not a relay
- **ENS overlap**: None (andi-p.eth vs memeticobjects.eth family)
- **Conclusion**: Not part of ZODL network

## arsonic vs gpebbles — NOT SAME PERSON (separate pairwise check)
- **Arsonic**: Level 84, 2 wallets (arsonic.eth, sgtpepeworld.eth), 2,692 txs
- **gpebbles**: Level 100, 3 wallets (gpebbles.eth, gpebblesequilibrium.eth, gpebbles6529ftw.eth), 3,073 txs
- **Direct transfers**: 1 — gpebbles → Arsonic, 1.0 ETH (Sep 2025, one-way, no return)
- **Shared counterparties**: 35 — ALL marketplace contracts (Seaport, SuperRare, Blur, Foundation, Manifold, etc.)
- **Exchange relay**: None
- **Shared personal EOAs**: 1 trivial (0x9f6abe94, 2 recipients, 0 ETH value)
- **ENS overlap**: None
- **Conclusion**: Not same person — one one-way transfer over years of activity, no linkage signals

## Script
`scripts/ezmonet_zodl_exchange.py` — adaptable for any candidate-vs-network check. **PITFALL**: Must update the wallet address array at the top of the script, not just sed-replace the profile name. Fetch wallets via `/identities/{handle}` first.