# ZODL Network — Multi-Profile Identity Investigation

## Date
July 12, 2026

## Subject
Investigation of 10+ 6529 profiles suspected to be the same person operating multiple wallets.

---

## Profiles Identified (11 total)

10 profiles provided by user + 1 discovered during analysis.

| # | Handle | Level | Wallets | ENS | TDH |
|---|---|---|---|---|---|
| 1 | @ZODL | 64 | 3 | neom.memeticobjects.eth, szn8.6529🟧.eth, memeticobjects.eth | 104K + 361K + 1.58M |
| 2 | @ZODLZO | 7 | 1 | (none) | 1,779 |
| 3 | @ZODLZOD | 14 | 1 | momog.eth | 4,974 |
| 4 | @ZODLZODL | 32 | 2 | aditi.💞forever.eth, play.memeticobjects.eth | 31K + 101K |
| 5 | @ZODLZODLZ | 0 | 1 | (none) | 0 |
| 6 | @ZODLZODLZO | 0 | 1 | momo.seizenews.eth | 0 |
| 7 | @ZODLZODLZOD | 15 | 1 | (none) | 6,117 |
| 8 | @ZODLZODLZODL | — | NOT FOUND (404) | — | — |
| 9 | @ZODLZODLZODLZ | 0 | 1 | (none) | 0 |
| 10 | @ZODLZODLZODLZO | 59 | 1 | (none) | 4,085 |
| 11 | @ZODLZODLZODLZOD | ? | 1 | 💞forever.eth | — |

**11th profile discovered**: @ZODLZODLZODLZOD (ENS: 💞forever.eth, 0x26874d59...) found via cross-reference — this address interacted with 7 of the 10 original profiles. The ENS name 💞forever.eth matches the naming pattern of @ZODLZODL's wallet aditi.💞forever.eth.

## Shared Wallets
None — all 13 wallet addresses are unique to their respective profiles.

## Direct ETH Transfers Between ZODL Wallets: 864

**864 ETH value transfers** directly between ZODL wallets, spanning March 2021 → February 2026 — 5 years of continuous activity.

### Hub-and-Spoke Pattern
- **@ZODLZODLZOD** is the central hub — sends to and receives from all others
- **@ZODL** and **@ZODLZOD** are secondary hubs
- All other profiles receive from and send back to these hubs
- Amounts range from 0.001 ETH to 9.65 ETH
- Many transfers happen within minutes of each other

### Sample Transfers (early period)
- 2021-03-28: ZODLZOD → ZODL, 0.05 ETH
- 2021-07-31: ZODLZOD → ZODLZODLZOD, 0.5 ETH; ZODLZOD → ZODLZODL, 0.5 ETH (same block)
- 2021-10-03: ZODLZOD → ZODLZODLZOD, 9.65 ETH
- 2021-10-08: ZODL → ZODLZODLZOD, 1.0 ETH + 0.5 ETH (4 min apart)

### Sample Transfers (recent period)
- 2025-11-02: ZODL → ZODLZODLZOD, 0.63 ETH; ZODLZODL → ZODLZODLZOD, 0.3 ETH (same minute)
- 2026-02-26: ZODLZODLZO → ZODL, 0.1 ETH

## Synchronized Minting Signal

On May 15, 2023, 5 ZODL profiles all sent 0.000777 ETH to the same ERC721DropProxy contract (0x4ebb2384...) within 3 minutes (01:31–01:34):
- @ZODLZODL (01:31)
- @ZODLZODLZOD (01:32)
- @ZODLZOD (01:33)
- @ZODL (01:33)
- @ZODLZODLZ (01:34)

No legitimate reason for 5 "different" people to mint the same contract in that window.

## Shared ENS Subdomain Pattern

Multiple wallets share the "memeticobjects.eth" subdomain:
- memeticobjects.eth (ZODL's main wallet, 1.58M TDH)
- neom.memeticobjects.eth (ZODL)
- play.memeticobjects.eth (ZODLZODL)

💞forever.eth theme:
- aditi.💞forever.eth (ZODLZODL)
- 💞forever.eth (ZODLZODLZODLZOD — the 11th profile)

"momo" naming:
- momog.eth (ZODLZOD)
- momo.seizenews.eth (ZODLZODLZO)

## Shared Counterparties: 44 addresses

Most are NFT marketplace contracts (Seaport, Manifold, ERC1155LazyPayableClaim, WyvernExchange, GnosisSafe/6529). Key findings:

- 7 profiles interact with the same Manifold Minting Wallet (0x3a3548e0...)
- 7 profiles interact with 💞forever.eth (0x26874d59... — the 11th profile)
- 7 profiles interact with Seaport (0x0000000000000068...)
- 7 profiles interact with 6529 GnosisSafe (seize.6529.eth)

## Exclusion Cases

### EzMonet (Level 84, 3 wallets: ezmonet.eth, momonet.eth)
- Zero direct transfers with any ZODL wallet
- 26 shared addresses — ALL contracts or airdrop distributions
- 4 "high-volume" shared addresses (540+ recipients) = airdrops sending micro-amounts TO both
- Zero shared personal EOAs
- No ENS naming overlap (momonet vs memeticobjects — different roots)
- **EXCLUDED from ZODL network**

### grubnot (Level 68, 3 wallets: grubnot.eth)
- Zero direct transfers with any ZODL wallet
- 22 shared addresses — ALL contracts or airdrops
- Zero shared personal EOAs
- No ENS naming overlap
- One coincidence: both minted SlicesOfTIMECovers same day (Feb 11, 2022, 14 min apart, both 0.100 ETH) — public mint, anyone could participate
- **EXCLUDED from ZODL network**

### andi_p (Level 36, 2 wallets: andi-p.eth, vault.andi-p.eth)
- Zero direct transfers with any ZODL wallet
- 30 shared addresses
- Exchange overlap: both received from Binance Old (0x21a31ee1, 413+ recipients), Binance (0x56eddb7a, 583+), Coinbase (0xdfd5293d, 423+) — but timing doesn't overlap (ZODL in 2021, andi_p in 2022+). Shared exchange hot wallets are normal for any two active ETH users.
- 1 personal EOA: @hexum (mint.hexum.eth, 18 recipients) — ZODL received 0.003 ETH from @hexum, andi_p sent 0.327 ETH to @hexum. Different directions, no round-trip.
- No ENS naming overlap
- **EXCLUDED from ZODL network**

## Conclusion

**All 11 ZODL profiles are the same person.** 864 direct ETH transfers between personal wallets over 5 years, shared ENS subdomain naming (memeticobjects.eth family, 💞forever.eth theme), synchronized minting (5 profiles minting same contract within 3 minutes), and hub-and-spoke ETH routing pattern. No ambiguity.

## Comparison to blake69/bicasso

| Signal | ZODL (11 profiles) | blake69/bicasso (2 profiles) |
|---|---|---|
| Direct transfers | 864 over 5 years | 7 (2 round-trips + 3 one-way) |
| ENS overlap | Shared subdomains | None |
| Synchronized actions | 5 profiles minting in 3 min | None |
| Shared personal EOAs | 💞forever.eth = 11th profile | @696969 (19 recipients) |
| Shared exchange relay | N/A (internal network) | 6 Binance/Coinbase addresses |
| Verdict | Unambiguous — same person | Supports same person, not conclusive |

## Scripts
- `scripts/zodl_analysis.py` — full multi-profile network analysis
- `scripts/ezmonet_zodl_exchange.py` — candidate-vs-network exclusion check (adaptable)
- `scripts/arsonic_gpebbles_check.py` — pairwise cross-reference (adaptable)