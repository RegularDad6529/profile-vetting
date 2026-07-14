# Sale Price Matching Methodology

How to accurately match ETH prices to NFT purchases and sales. This consolidates pitfalls #32, #46, #47, #52 into a single workflow reference.

## Purchase Price Matching

1. Find NFT incoming transfers (`to = wallet`, `from != wallet`, `from != 0x0`)
2. For each, find ETH outgoing txs in the same block (`from = wallet`, `value > 0`)
3. If multiple NFTs were bought in the same block, **divide total ETH by NFT count** (pitfall #46)
4. Also check WETH outgoing in the same block (some marketplaces accept WETH)
5. Match price = ETH (or WETH) out / NFT count

## Sale Price Matching

1. Find NFT outgoing transfers (`from = wallet`, `to != wallet`, `to != 0x0`)
2. For each, check ETH incoming in the same block:
   - **Regular txs** (`txlist`): `to = wallet`, `value > 0`
   - **Internal txs** (`txlistinternal`): `to = wallet`, `value > 0` — Seaport pays via internal txs (pitfall #47)
   - **WETH token transfers** (`tokentx` with WETH contract): `to = wallet` — Seaport can pay in WETH (pitfall #52)
3. If no ETH/WETH found in same block, check **OTTC payments** ±48h from recipient (pitfall #42 Part B)
4. If still nothing → classify as transfer/gift, NOT a sale (pitfall #43)
5. If multiple NFTs sold in same block, **divide total ETH by NFT count** (pitfall #46)

## Mint Cost Matching

1. Find NFT mints (`from = 0x0`, `to = wallet`)
2. Find ETH outgoing in the same block
3. If multiple NFTs minted in same block from same contract, **divide total ETH by mint count** (pitfall #46)
4. If no ETH out → free mint (0 cost)
5. Any non-zero ETH = paid mint. Do NOT call low-cost mints "free mints" (pitfall #51)

## WETH Token Transfer Query

```
GET https://eth.blockscout.com/api/v1?module=account&action=tokentx&address={wallet}&contractaddress=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2&sort=asc
```

WETH contract: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
Also look for WETH unwrap internal txs: internal txs FROM the WETH contract to the wallet (seller unwraps WETH→ETH after receiving it).

## Key Contracts

| Contract | Address | Notes |
|----------|---------|-------|
| Seaport 1.6 | 0x00000000000000ADc04C56Bf30aC9D3c0aAF14dC | Current, matchAdvancedOrders |
| Seaport 1.5 | 0x0000000000000068F116a894984e2DB1123eB395 | Legacy |
| Seaport 1.4 | 0x00000000000001adF28D0aCDeB0B5b31601b3b0d | Oldest |
| WETH | 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 | Wrapped Ether ERC-20 |

## Assessment Script Pattern

When building an assessment script, always fetch these 4 data streams per wallet:
1. `tokennfttx` — NFT transfers
2. `txlist` — regular ETH txs
3. `txlistinternal` — internal ETH txs (Seaport payments)
4. `tokentx` (filtered to WETH contract) — WETH token transfers

Build block-indexed lookups for each:
```python
weth_in_by_block = defaultdict(float)
for tx in all_weth:
    if tx['to'].lower() in WALLET_SET:
        weth_in_by_block[tx['blockNumber']] += int(tx['value']) / 1e18
```

Then when matching sales, check all three sources: regular ETH, internal ETH, WETH.