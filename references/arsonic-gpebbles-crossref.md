# Arsonic vs gpebbles — Pairwise Cross-Reference

## Date
July 12, 2026

## Subject
Check if @Arsonic and @gpebbles are the same person.

---

## Profiles

| Profile | Level | Wallets | ENS |
|---|---|---|---|
| @Arsonic | 84 | 0x7c8f0720... (sgtpepeworld.eth), 0x9f6ae037... (arsonic.eth) | arsonic.eth, sgtpepeworld.eth |
| @gpebbles | 100 | 0x562acb18... (gpebblesequilibrium.eth), 0x7d88f221... (gpebbles.eth), 0x86ae3785... (gpebbles6529ftw.eth) | gpebbles.eth family |

## Transaction Volume
- Arsonic: 250 + 2,442 = 2,692 ETH value transfers
- gpebbles: 2 + 3,049 + 22 = 3,073 ETH value transfers

## 1. Direct ETH Transfers: 1

| Date | Direction | Amount | Type |
|---|---|---|---|
| 2025-09-12 22:25 | gpebbles → Arsonic | 1.000000 ETH | regular |

One-way, no return. Looks like a payment or gift, not wallet cycling.

## 2. Shared Counterparties: 35 — All Infrastructure

Every shared address is a smart contract:
- Seaport (3 variants): both heavy NFT traders
- SuperRareBazaar: gpebbles 231 txs, Arsonic 2 txs
- Manifold Minting Wallet: both mint via Manifold
- ERC1155LazyPayableClaim / ERC721LazyPayableClaim: both mint 6529 drops
- WETH9, UniversalRouter, MetaSwap: both wrap/swap ETH
- RelayReceiver / RelayDepository: both bridge ETH
- 6529 GnosisSafe (seize.6529.eth): both participate in 6529
- BlurSwap, Foundation, TLStacks: both sell on marketplaces
- Lumens: both minted same day (Jul 22, 2025)

## 3. Exchange Relay: None

Only one "high-volume" shared address (0xf70da978, 63+ recipients) — both SEND to it (bridge), not one depositing and the other withdrawing.

## 4. Personal EOA Overlap: 1 (trivial)

0x9f6abe94 — 2 recipients, 0 ETH value for both. Zero-value transactions (likely NFT contract calls).

## 5. ENS Naming: No overlap

Arsonic: arsonic.eth, sgtpepeworld.eth
gpebbles: gpebbles.eth, gpebblesequilibrium.eth, gpebbles6529ftw.eth

## Assessment

**NOT the same person.** One 1 ETH transfer (one-way, no return), zero exchange relay, zero shared personal wallets, no ENS overlap. 35 shared addresses are all marketplace infrastructure. Both are heavy NFT traders in the same ecosystem but no on-chain evidence of shared identity.

## Methodology

Script: `scripts/arsonic_gpebbles_check.py` — standalone pairwise analysis with direct transfers, shared counterparty categorization (contracts/exchange-like/personal EOAs), and ENS check.