# Solana On-Chain Sale Verification

Supplements the Exchange.art API reference. Use when you need to verify actual SOL payments to an artist's wallet, check buyer diversity, or look for wash trading patterns on Solana.

## RPC Endpoints

```
https://api.mainnet-beta.solana.com      (main, aggressive 429 rate limiting)
https://solana-rpc.publicnode.com         (alternative, sometimes works better)
https://rpc.ankr.com/solana               (alternative)
```

**Rate limiting strategy**: Rotate between multiple RPC endpoints. Add 1-2 second delays between calls. Public RPCs return HTTP 429 after ~10-20 rapid requests. For full scans of 800+ transactions, expect significant throttling.

## Get Transaction History

```json
{"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": ["{wallet}", {"limit": 1000}]}
```

Returns up to 1000 signatures (newest first). **Capped at 1000** — artists active since 2022 will have incomplete history. The oldest tx in the window is NOT the wallet's first ever tx.

Filter: `success = [s for s in sigs if not s.get('err')]` — failed transactions have `err` set.

Common error codes:
- `{"InstructionError": [2, {"Custom": 6001}]}` = "AllEditionsMinted" (Exchange.art mint attempts where editions sold out)
- `{"InsufficientFundsForRent": ...}` = not enough SOL for account rent

## Detect Sales (SOL Incoming)

For each signature, fetch the full transaction:

```json
{"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": ["{sig}", {"maxSupportedTransactionVersion": 0}]}
```

Check `meta.preBalances` vs `meta.postBalances` for the artist's wallet index:

```python
accounts = tx['transaction']['message']['accountKeys']
our_idx = accounts.index(SOL_WALLET)
sol_change = (post_balances[our_idx] - pre_balances[our_idx]) / 1e9
```

- `sol_change > 0.05` = likely sale (filter out dust/mint fees)
- `sol_change > 0.01` = possible sale (lower threshold catches more but adds noise)

## Exchange.art Program Payments

Most Exchange.art sales go through their escrow program. The program address starts with `exAuv` or `EXBuY`. When a sale happens:
1. Buyer pays SOL to Exchange.art program
2. Program holds escrow
3. Program sends SOL to artist
4. NFT goes to buyer

The SOL may appear to come FROM the program, not from the buyer directly. The "payer" wallet in the transaction (the account that lost SOL) won't always be the actual buyer — it could be the program itself.

## Check Token (NFT) Transfers

```python
pre_tokens = tx['meta']['preTokenBalances']
post_tokens = tx['meta']['postTokenBalances']

for ptb in post_tokens:
    owner = ptb.get('owner', '')
    mint = ptb.get('mint', '')
    post_amt = float(ptb.get('uiTokenAmount', {}).get('uiAmount', 0) or 0)
    pre_amt = 0
    for prtb in pre_tokens:
        if prtb.get('mint') == mint and prtb.get('owner') == owner:
            pre_amt = float(prtb.get('uiTokenAmount', {}).get('uiAmount', 0) or 0)
    change = post_amt - pre_amt
    # change < 0 = token left this wallet (sold/transferred)
    # change > 0 = token arrived (bought/minted/received)
```

## Identify Buyer Wallets

For each account in the transaction that lost SOL (`post_balances[j] - pre_balances[j] < -0.05`), that account is likely the buyer. Check:
1. Does the buyer wallet have an Exchange.art profile? (`GET /v2/profile?q={addr}&mode=byWallets`)
2. Does the buyer own NFTs on Exchange.art? (`GET /v2/nft/ids/_ownedBy?wallets={addr}`)
3. How many transactions does the buyer wallet have? (`getSignaturesForAddress`)

**Red flags for wash trading on Solana**:
- Buyer wallet has 0 Exchange.art profile and 0 owned NFTs
- Buyer wallet has very few transactions
- Buyer wallet has near-zero SOL balance
- Same buyer wallet appears in multiple sales

## Check Current NFT Owner (Buyer Diversity)

To verify who currently owns a sold NFT:

```json
{"jsonrpc": "2.0", "id": 1, "method": "getTokenLargestAccounts", "params": ["{mint}"]}
```

Get the largest token account address, then:

```json
{"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo", "params": ["{token_account}", {"encoding": "jsonParsed"}]}
```

The `data.parsed.info.owner` field is the current NFT owner's wallet. **Heavily rate-limited** — add 2+ second delays between calls. Only feasible for small samples (10-20 NFTs).

## Sampling Strategy

For wallets with 800+ transactions, scanning every transaction is impractical due to rate limiting. Use sampling:

1. Sample every Nth transaction (e.g., every 10th = ~88 txs for 882 total)
2. Focus on SOL balance changes > 0.05 (filters out mints/dust)
3. Extrapolate: `total_sales ≈ sample_sales × (total_txs / sample_size)`
4. The Exchange.art `totalSalesUsd` stat is more reliable than on-chain extrapolation — use it as the primary sales figure

## Sell-Through Rate (from Exchange.art API)

More reliable than on-chain sampling:

1. `GET /v2/nft/ids/_createdBy?wallets={sol},{eth}` → created_ids
2. `GET /v2/nft/ids/_ownedBy?wallets={sol},{eth}` → owned_ids
3. `sold = created_ids - owned_ids` (set difference)
4. High sell-through (>90%) is notable — could mean strong demand or low pricing

## Case Study: kiramoto Solana Verification

- 882 successful transactions (capped at 1000, active since May 2024 visible)
- Sampling every 10th tx: found 2 sales >0.05 SOL in 88 sampled
  - 1.42 SOL from FAM2AHFL... (Oct 2024) — buyer wallet has 61 txs, no Exchange.art profile, 0 NFTs (questionable)
  - 0.052 SOL from 4tMGYXmK... (Jun 2024)
- Background scan of first 250 txs: 35 sales found (>0.01 SOL threshold)
- First 100 transactions (2025-2026): 0 sales — aligns with health break claim
- Exchange.art reports $44,648 total sales — most sales likely occurred 2022-2023 (outside 1000-tx window)
- 138 of 140 NFTs sold (98.5% sell-through)
- Could not verify buyer diversity due to Solana RPC rate limiting
- One buyer wallet (FAM2AHFL) is a slight question mark but not conclusive wash trading evidence