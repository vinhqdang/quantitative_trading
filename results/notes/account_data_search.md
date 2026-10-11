# Search for public account-level trade / order datasets

Date of search: 2026-10-11. Goal: real data with a per-account identifier so that a coordination test on account-level order flow can be run on real accounts (labelled wash-trading / manipulation cases preferred, unlabelled real data acceptable for false-alarm calibration).

Everything below was checked by actually requesting the URL from this environment. Where I could only read a description and did not open the data, it says so. No download exceeded the budget: about 230 MB were transferred in total. Large sources were sampled with HTTP range requests (first rows, or one parquet row group with only the needed columns). Samples live under `$SCRATCH/acct_data/<name>/` (SCRATCH is the session scratch directory), one directory per source. All parsing used `python3 -I`; nothing from the downloads was executed (the Zenodo `read_data.py` and the notebooks were only read as text or not opened at all).

Account addresses below are shown truncated (first 8 hex digits). Usernames, pseudonyms and bios present in some sources are omitted.

## 0. Host reachability from this environment

| Host | Result |
|---|---|
| zenodo.org (API and file content, range requests work) | reachable |
| huggingface.co (hub API, resolve/ with range requests) and datasets-server.huggingface.co | reachable |
| www.kaggle.com public API (search, view, anonymous download, per-file download with range) | reachable, no credentials needed or present (`~/.kaggle` absent; the kaggle CLI is not installed) |
| dataverse.harvard.edu, figshare.com, data.mendeley.com, osf.io, arxiv.org | reachable (only Dataverse was queried in depth) |
| data-api.polymarket.com, gamma-api.polymarket.com | reachable |
| api.hyperliquid.xyz/info | reachable (recentTrades returns the two counterparty addresses per trade) |
| api.elections.kalshi.com | reachable (trades have no account field, see section 6) |
| indexer.dydx.trade | reachable (trades have no account field) |
| raw.githubusercontent.com | reachable for a public repo (HTTP 200 on a README) |
| api.github.com | only repository-scoped endpoints for the session repo; search and third-party repos refused (403) |
| github.com and codeload.github.com via curl | 403/400; the GitHub MCP tools refuse any repo other than the session repo. WebFetch could read a github.com page |
| www.openicpsr.org | 403 (blocked, not retried) |
| dune.com | 403 (blocked) |
| hyperliquid-archive.s3.amazonaws.com (the official requester-pays archive) | 403, not usable |
| api.thegraph.com, api.goldsky.com | 404 on the root path, not tested further |

Consequence: I could not open the GitHub code repository that accompanies Victor and Weintraud (2021), nor any of the GitHub-hosted NFT wash-trade repositories, so claims about those come only from Zenodo/Kaggle metadata or from a WebFetch summary and are marked as such.

---

## 1. Sources that fit the test (per-account time series with side)

### 1.1 Zenodo 18184441: "An Open Book: Level 4 Order Book Data from the Hyperliquid Exchange" (best fit)

- URL: https://zenodo.org/records/18184441 (DOI 10.5281/zenodo.18184441), published 2026-03-25, authors Albers, Cucuringu, Howison, Shestopaloff.
- License: CC BY 4.0 (from the Zenodo record).
- Size: about 195 GB in total (the record lists 15 files). Order statuses (accepted) BTC 19.3 GB, ETH 12.1 GB, SOL 6.3 GB as tar.xz; rejected orders BTC 46.0 GB, ETH 24.1 GB, SOL 8.5 GB; raw book diffs 49.6 GB; trades Oct 2025 10.0 GB, Nov 8.8 GB, Dec 6.7 GB, Jan 2026 3.8 GB; `mapdir.tar.xz` 10 MB (lookup tables, includes `users.csv`); `SCHEMA.md`, `read_data.py`, `README.md`.
- Time span: order statuses and book diffs 2025-12-01 to 2025-12-31 (744 hourly files per archive, "no gaps" per README). Trades 2025-10 to 2026-01 with some gaps (README table: Oct 29/31 complete days, Nov 25/30, Dec 31/31, Jan 30/31).
- Accounts: `users.csv` has 328,456 entries (per SCHEMA.md; I did not download it). In the 1,008,183-record sample (first ~24 minutes of SOL, 2025-12-01) there are 1,909 distinct userIds.
- Record layout (SCHEMA.md): 54-byte binary records: `ts` (uint64 ns), `userId` (uint32, maps to an Ethereum address), `statusId` (open, canceled, filled, many rejection codes), `isAsk`, `limitPx`, `sz`, `oid`, `timestampDiff` (ms since submission), `orderTypeId`, `tifId`, `reduceOnly`, `origSz`, trigger fields. About 880 million records per day over BTC, ETH, SOL. Rejected orders (about 89% of all submissions according to SCHEMA.md) are in the separate `*_rejected` archives.
- Sample rows (userId is a dataset-internal integer, no address involved; px/sz are the dataset's packed encoding):

  | ts (ns) | userId | statusId | isAsk | limitPx (encoded) | sz (encoded) | oid | tifId |
  |---|---|---|---|---|---|---|---|
  | 1764547199867476878 | 78 | 1 (open) | 1 | 1073755167 | 1073750117 | 253900069284 | 0 (Alo) |
  | 1764547199867476878 | 78 | 1 (open) | 1 | 1073755166 | 1073750118 | 253900069285 | 0 (Alo) |
  | 1764547199867476878 | 114 | 1 (open) | 1 | 1073755166 | 1073744270 | 253900069330 | 0 (Alo) |

- Sample statistics (from `sol_orders_202512.tar.xz`, first 10 MB of the xz stream, first member `20251201/sol_00.data.gz`, truncated): 1,008,183 events from 2025-11-30T23:59:59.867 to 2025-12-01T00:23:36.526 UTC; 577,918 distinct oids; status counts open 431,615, canceled 415,896, perpMarginRejected 98,969, iocCancelRejected 43,761, filled 16,265; isAsk 515,715 vs bid 492,468; heaviest user 75,741 events, i.e. extremely skewed activity.
- Labels: none. No wash-trade or manipulation labels. The paper's own topic is "pervasive, weakly interacting order flow", not manipulation.
- Timestamp resolution: nanoseconds (exchange block / event time). Receive timestamps are batched per block, so many events share an identical ts.
- Sidedness: every record has `isAsk`, so each submission has a side. Maker/taker is recoverable for fills: the order carries tif (Alo, Ioc, Gtc) and the Trades files give an aggressor side and both counterparties (`side_info[].user`, `oid`).
- Suitability: yes, the only source found that gives the actual per-account time series of order submissions (including rejected submissions and cancellations) with side, at nanosecond resolution, on a live venue with real accounts. Unlabelled, so it serves false-alarm calibration and "who looks coordinated" screening, not detection power. A user is a pseudonymous address, not a person, and one operator can run many addresses.

### 1.2 Hyperliquid per-fill tables on Hugging Face (account address, side, taker flag, ms timestamps)

Both are third-party mirrors of data derived from the Hyperliquid node. Neither declares a license on the dataset card (no license tag, README missing or empty). I could not verify the terms under which the original node data may be redistributed.

**(a) craftify2221/hyperliquid-fills-raw**
- URL: https://huggingface.co/datasets/craftify2221/hyperliquid-fills-raw (files `fills/fills_raw_YYYY-MM-DD.parquet`; every day also appears under the repo root as `fills_raw_YYYY-MM-DD.parquet`, so the 371 GB repo total is roughly double counted).
- Size: about 0.5 to 1.25 GB per day; 348 daily files, 2025-07-28 to 2026-08-19. One checked day (2026-06-05) has 18,904,651 fills in 19 row groups.
- Columns: coin, dex, asset_class, price, size, side, timestamp (ms, UTC), direction, realized_pnl, tx_hash, order_id, trade_id, fee, address, crossed, start_position, client_order_id, builder, twap_id, is_liquidation, and others.
- Sample (row group 0 of 2026-06-05, read via range requests with column projection, 1,048,576 fills, 00:00:00.043 to 01:31:25.999 UTC): 17,574 distinct addresses; crossed True 526,408 / False 522,168 (each trade appears as two rows, one per counterparty); side buy 527,279 / sell 521,297; 412 coins; top address 29,286 fills in 91 minutes, median 3 fills.
- 3 sample rows (address truncated):

  | coin | price | size | side | timestamp | direction | order_id | trade_id | address | crossed |
  |---|---|---|---|---|---|---|---|---|---|
  | PURR/USDC | 0.098141 | 115 | buy | 2026-06-05 00:00:00.043Z | Buy | 458107747653 | 164019334428409 | 0x246f07.. | False |
  | PURR/USDC | 0.098141 | 115 | sell | 2026-06-05 00:00:00.043Z | Sell | 458107764533 | 164019334428409 | 0xeeeeee.. | True |
  | PURR/USDC | 0.098141 | 0.75785 | sell | 2026-06-05 00:00:00.043Z | Spot Dust Conversion | 458107764533 | 0 | 0x02fb3e.. | True |

- Labels: none (the repo also holds some research scripts and JSON files of a third party; I did not open them).
- Timestamp resolution: milliseconds (the node reports block time; fills in one block share it).
- One-sided per account: yes, each row is one account's side of a fill, with `crossed` giving taker (True) vs maker (False).
- Suitability: yes for trade-level flow per account with side and taker flag over a year; no submissions or cancellations (fills only). Best option for long, recent, multi-coin real data. Fetch whole days only if disk and budget allow.

**(b) gionuibk/hyperliquid-node-fills-by-block** (also `gionuibk/hyperliquid-node-trades`)
- URL: https://huggingface.co/datasets/gionuibk/hyperliquid-node-fills-by-block
- Size: 113.8 GB, 140,973,012 rows (blocks), 1,076 parquet files; file names cover 2025-07-27 to 2025-10-10. `hyperliquid-node-trades` is 37 GB, 292,422,184 trades from 2025-03-22 with `side_info` (user, oid, twap_id) per trade.
- Format: one row per block with a JSON string `events` of `[address, fill]` pairs; fill keys include coin, px, sz, side, dir, closedPnl, crossed, oid, tid, time (ms), twapId, cloid, builder.
- Sample (hourly files `node_fills_by_block_hourly_20250727_8.parquet` 2.2 MB and `..._20250806_23.parquet` 13.9 MB): 17,516 fills / 887 users in 10 minutes; 109,086 fills / 2,924 users in one hour; crossed split exactly 50/50 because both counterparties are listed; no tid with the same user on both sides in either sample.
- 3 sample rows (address truncated): `2025-07-27T08:50:10.273 676607012 0x7839e2.. BTC 118136.0 0.00009 B Close Short crossed=False oid=121670079265`; `... 0xdb84f0.. BTC 118136.0 0.00009 A Close Long crossed=True oid=121639440355`; `... 0x8706af.. BTC 118137.0 0.00044 B Close Short crossed=True oid=121554386472`.
- Labels: none. License: none declared. Timestamp: block time with sub-millisecond digits, plus block_number.
- Suitability: yes (fills with side and taker flag per account), but (a) is easier to read.

### 1.3 Victor and Weintraud (2021) replication data, Zenodo 4540223 (the only source with documented wash trading by account)

- URL: https://zenodo.org/records/4540223 (DOI via Zenodo), files `IDEXTrades.csv`, `EtherDeltaTrades.csv`, `EtherDollarPrice.csv`, `token_decimals.json`. Published 2021-02-13. License CC BY 4.0.
- Size: `IDEXTrades.csv` 2,098,100,246 bytes; `EtherDeltaTrades.csv` 1,051,981,252 bytes. Row counts not read in full; from bytes per row in the first 3 MB I estimate about 5.5 million IDEX and 3.6 million EtherDelta trades (estimate, not counted).
- Time span, checked at the head and tail of each file: IDEX 2017-09-27 to 2020-05-04 (block about 10.0M); EtherDelta 2017-02-09 to 2020-05-04.
- Accounts: from the first 3 MB only: IDEX 7,810 rows, 264 makers, 313 takers, 428 distinct accounts; EtherDelta 10,408 rows, 895 distinct `get`, 1,123 distinct `give`, 1,480 distinct accounts. Full-file account counts not computed (would need the full 3 GB).
- Columns IDEX: transaction_hash, status, block_number, gas, gas_price, timestamp, amountBuy, amountSell, expires, nonce, amount, tradeNonce, feeMake, feeTake, tokenBuy, tokenSell, maker, taker. Columns EtherDelta: transaction_hash, block_number, timestamp, tokenGet, amountGet, tokenGive, amountGive, get, give.
- Sample rows (IDEX, addresses and hashes truncated):

  | block_number | timestamp | tokenBuy | tokenSell | amount | maker | taker |
  |---|---|---|---|---|---|---|
  | 4317409 | 1506553069 | 0x000000.. | 0x744d70.. | 100000000000000000 | 0x034767.. | 0x034767.. |
  | 4317416 | 1506553483 | 0x000000.. | 0x744d70.. | 495350000000000 | 0x74719d.. | 0x034767.. |
  | 4317434 | 1506554023 | 0x000000.. | 0x744d70.. | 10000000000000000 | 0x034767.. | 0x034767.. |

  EtherDelta rows (`get` = maker side as filled, `give` = taker side): `3154485 1486684605 tokenGet=0xac709f.. amountGet=7.26e20 tokenGive=0x000000.. get=0xd8eeda.. give=0x1ed014..`, and similar.
- Labels: the files contain no label column. The paper defines wash trading with an on-chain structure rule (accounts whose trades form closed cycles with no net position change, including self-trades) and the original code lives in a GitHub repository I could not open. The abstract states a lower bound of wash-trading accounts and structures and about USD 159 million volume. Indicative signal in the data itself: in the IDEX head sample 5,868 of 7,810 trades (75%) have maker equal to taker, and in the EtherDelta sample 718 of 10,408 (7%) have get equal to give, so self-trades can be identified directly from the columns without the original code.
- Timestamp resolution: Unix seconds plus block number (block-level, about 15 s granularity; in the samples every block has one distinct timestamp).
- One-sided per account: matched trades only. Each row names both counterparties (IDEX `maker`/`taker`, EtherDelta `get`/`give`), so maker vs taker is known, but the data are executed trades, not order submissions. The buy/sell direction follows from tokenBuy/tokenSell (and tokenGet/tokenGive) relative to the zero-address ETH token.
- Suitability: yes for a test on executed trades per account with documented, structurally defined wash accounts (labels have to be rebuilt from the rule); no for submissions. Ethereum order-book DEX 2017 to 2020, a small number of heavy wash accounts, gives an actual positive class for power checks.

### 1.4 Polymarket live Data API (public, no key), and static Polymarket dumps

**Live API** `https://data-api.polymarket.com/trades`
- Reachable, no key. Returns `proxyWallet`, `side`, `size`, `price`, `timestamp` (Unix seconds), `conditionId`, `asset`, `outcome`, `transactionHash`, plus profile fields (name, pseudonym, bio, image) that should be dropped. Supports `limit` (10,000 worked), `offset` (hard cap: an offset above 10,000 returns "max historical trades offset of 10000 exceeded"), `market` (conditionId) and `user` filters; `takerOnly=false` is accepted. A `user=` query returned 2,000 trades going back 8 days for a heavy wallet.
- Sample taken: latest 10,000 trades at 2026-10-11 01:13 to 01:25 UTC: 2,302 distinct wallets, 1,167 markets, BUY 8,665 vs SELL 1,335, only 470 distinct second-level timestamps for 10,000 rows (sub-second clustering from batched settlement).
- 3 sample rows (profile fields omitted, wallet truncated): `0xc69bd556.. BUY size=5 price=0.002 ts=1791682143 outcomeIndex=999`; `0x3cbe3e9b.. BUY size=6.2625 price=0.8 ts=1791682143`; `0xc69bd556.. BUY size=5 price=0.002 ts=1791682143`.
- Labels: none. License/terms: not verified (Polymarket terms not read).
- Whether each row is the taker or maker: the default feed is taker fills; the maker side is only included when `takerOnly=false` and I did not verify how makers are flagged in that mode.
- Suitability: usable for per-wallet trade streams with side and second resolution; deep history requires per-market or per-user queries because of the offset cap; no orders.

**Hugging Face AiYa1729/polymarket-transactions** (https://huggingface.co/datasets/AiYa1729/polymarket-transactions)
- MIT license (card). One 4.1 GB parquet, 45,555,994 fills, 173 row groups, inception to about 2025-03-23 (row group statistics: first group 2022-11-21 to 2024-02-06, last group 2025-03-19 to 2025-03-23; the file is not globally time sorted).
- Columns include blockNumber, transactionHash, timeStamp (seconds), taker, taker_side, maker, maker_side, fill_price, volume, market, taker_pnl, maker_pnl and a large set of derived features.
- Sample (row group 0 read with 12 columns: 263,329 rows): 11,219 distinct takers, 3,301 distinct makers; taker_side values 1 (57,643) and 0 (205,686); taker equals maker in 716 rows (0.27%); 175,889 distinct timestamps/blocks.
- 3 sample rows (addresses truncated): `block 35896869 2022-11-21 19:50:09 taker=0xEA5981CA.. taker_side=1 maker=0xEA5981CA.. maker_side=0 fill_price=0.5 volume=100`; next two rows the same pair, prices 0.6 and 0.5, volumes 100 and 10 (a same-address buy and sell, a wash-like pattern in a very early market).
- Labels: none. Both maker and taker are named and each has a side, so this one is two-sided and maker/taker aware. Suitability: yes for executed trades per account with maker/taker; second-level time.

**Kaggle rngrng/polymarket-crypto-updown-markets-trade-tape** (https://www.kaggle.com/datasets/rngrng/polymarket-crypto-updown-markets-trade-tape)
- CC0. 1.7 GB, 9,627,085 fills, 2026-07-12 to 2026-08-03 (5m tape 2026-07-23 to 08-03). Columns: asset, window_open_ts, condition_id, trade_ts, side, outcome, price, size, wallet, pseudonym, winning_outcome.
- Sample (first 3 MB of `trades_5m.csv`): 17,035 rows, 2,222 distinct wallets, 5 markets, 2026-07-23 18:52 to 20:16 UTC, BUY 15,342 / SELL 1,693, 498 distinct second timestamps. Matched counterparties appear as separate rows (no maker/taker flag).
- 3 sample rows: `btc 1784832600 trade_ts=1784832949 SELL Down 0.999 size=25 wallet=0x2bad08..`; `... BUY Down 0.999 25 0x7b8400..`; `... trade_ts=1784832946 SELL Down 0.999 700 0xef244c..`.
- Labels: market outcomes only, no manipulation labels. Rows are in as-crawled order (sort by trade_ts). Useful as a dense short-horizon market (many wallets in one 5-minute window).

**Kaggle madrading/polymarket-2026-fifa-world-cup-order-book** (https://www.kaggle.com/datasets/madrading/polymarket-2026-fifa-world-cup-order-book)
- License "Other (specified in description)", mixed with a CC BY 4.0 part. `trades_onchain.parquet`: 1.04 GB, 19,556,012 fills, 20 row groups; schema verified through the parquet footer: ts_ms, ts_iso, condition_id, token_id, price, size, side, outcome, outcome_index, proxy_wallet, transaction_hash, ingest_route, source. Per the card "dense through 2026, sparse in 2025". I did not sample rows from it (to stay in budget), so wallet counts are not verified.

**Kaggle ligengxin96/polymarket-smart-money-trades-sample** (https://www.kaggle.com/datasets/ligengxin96/polymarket-smart-money-trades-sample)
- CC BY 4.0, 2.9 MB zip, one day (2026-10-08) of on-chain `OrderFilled` logs for traders ranked 901 to 1000 by 30-day profit. Selected, not representative: wallets are profit-selected.
- Sample (full file): 32,444 fills, 55 distinct wallets (card says 76 traders, 134 wallets; my count of the `wallet` column is 55), role maker 20,865 / taker 11,579, BUY 31,659 / SELL 785, 17,952 distinct second timestamps; columns ts, block, txHash, logIndex, exchange, side, role, tokenId, price, shares, usdc, fee, wallet, entityId, rank.
- 3 sample rows (hashes and tokenIds omitted, wallet truncated): `2026-10-08 00:00:04 block 95141603 pm_ctf_v2 BUY maker price=0.999 shares=28000000 wallet=0x3884ac..`; `2026-10-08 00:00:07 block 95141605 BUY maker price=0.31 shares=6086954 wallet=0xae68447..`. Has an explicit maker/taker `role`. Too small for a population test, fine for a smoke test.

---

## 2. Labelled data that exists but is weak, synthetic, aggregated, or unsuitable

| Source | What it is | Verdict |
|---|---|---|
| Kaggle vayuindexing/uniswap-wojak-weth-labeled-swaps, https://www.kaggle.com/datasets/vayuindexing/uniswap-wojak-weth-labeled-swaps, CC BY-SA 4.0, 15 MB zip | Real on-chain swaps of one Uniswap V2 pool: 152,487 swaps, 18,816 traders, 2026-01-26 to 2026-06-02, `trader` (tx sender) and `side` (Buy/Sell), block-level timestamps (100,663 distinct blocks). Columns: block_number, timestamp, datetime_utc, tx_hash, log_index, side, trader, token_amount_wojak, weth_amount, volume_usd, price_usd, price_impact, reserves, eth_price_usd, trader_class, is_mm_wash. | Real accounts with side. Labels are heuristic and circular for any flow-balance test: `mm_wash` = n_trades >= 20 and total volume >= USD 4,000 and balance ratio min(buy,sell)/max(buy,sell) >= 0.6 (380 wallets, 46,258 swaps, 30% of swaps). A test that uses buy/sell balance would re-discover its own label. Usable only for calibration or with a different label. Sample rows: `24321343 1769458751 Buy trader=0xe5c305.. volume_usd=0.9978 retail`; `24321348 1769458811 Buy 0xcd2726.. 61.2115 retail`. |
| Kaggle nikih94uni/ethereum-nfts-flagged-for-suspected-wash-trading, https://www.kaggle.com/datasets/nikih94uni/ethereum-nfts-flagged-for-suspected-wash-trading, CC BY 4.0, 20 MB zip | NFT ownership traces from the paper "Beyond the Surface: Advanced Wash Trading Detection in Decentralized NFT Markets" (arXiv 2312.16603), 11 collections up to 2022-05-01. `nft_ownership_traces/*.csv`: collection_address, collection_name, token_id, from, to, block_no, timestamp, price_usd, price_eth. | 534,488 transfer rows, 123,605 distinct addresses, price known on only a subset (azuki file: 33,636 of 48,246 rows have a price). Labels are per token (`flagged_trades` count per token_id; 28,219 tokens with at least one flagged trade, 60,916 flagged trades in total), produced by the authors' own detector, not ground truth, and not per account or per trade. NFT transfers are one-off sales with no order flow. Not suitable for submission time series; could serve as an account-pair graph. |
| Zenodo 8017995 Linkability networks of Ethereum accounts in NFT trading (cc-by-4.0, 8.9 GB graph data + 61 MB transfers) | Source data of the same research group. Not downloaded; description read only. | Same limits as above. Not verified in detail. |
| Zenodo 17830944 "A Midsummer Meme's Dream" code and data (cc-by-4.0, 26 MB zip) | Opened the CSVs inside via range read. `dune_data_on_potential_wash_trading_makers_HP_coins.csv` (64,621 rows): per maker and day buy_volume, sell_volume, token, platform, volume_percentage, is_both_buyer_seller. `wash_trading_detected.csv` (1,043 rows): platform, token address, day, unique_maker_count. | Daily aggregates only, per maker address; flagged by heuristics. Day resolution rules out timing tests. Useful for labels of which tokens were wash traded, not for account series. |
| Kaggle sergionefedov/crypto-exchange-fraud-and-wash-trading-detection (CC0, 57 MB zip) | 500,000 transactions, 8,000 wallets, explicit `manipulation_type`. | SYNTHETIC. The data dictionary says "simulated, 180-day span", "price fully simulated". Not real accounts. Do not use for calibration. |
| Kaggle quailmodel/crypto-dex-v1-sample (CC BY-NC-SA 4.0) | Swaps with exact labels (wash_trading, pump_and_dump, sandwich) and `trader`. | SYNTHETIC by the card ("Fully synthetic data", "No third-party data was used"). Only useful as a generator-side reference. |
| Zenodo 21379106 YoBit trading history | 6,933 trades of one account, anonymised. | One account, no other participants. Not suitable. (The record lists no data files in the API response.) |
| Harvard Dataverse "ERC-20 Trading 2015..2019" (CC0; e.g. doi:10.7910/DVN/REODCK for 2015, DVN/APVWMK for 2017) | Monthly gzip TSVs of ERC-20 token transfers (block_id, transaction_hash, time, token_address, sender, recipient, value, token_name, token_symbol, decimals). Opened `201512.tsv.gz`. | Transfers, not buy/sell trades: there is no side or price. The sample also contained repeated rows. Not suitable without joining to DEX events. 2017 files alone are roughly 1.5 GB compressed. |
| Harvard Dataverse doi:10.7910/DVN/BS0G74 (Hamrick et al., pump-and-dump ecosystem, CC0) | Telegram/Discord pump announcements (`all_telegram_12052019.tab` 2.4 MB, manual Discord file), no trade or account data. | Gives event times and targeted coins of documented pump-and-dump rings. Could be paired with market-level trade data, but contains no per-account orders. Not opened beyond the file listing. |
| Zenodo 18759046 Hyperliquid 2025-10-07 to 2025-10-15 (cc-by-4.0, 7.9 GB: raw_jsonl 4.2 GB, l2_csv 1.3 GB, fills_by_coin 0.7 GB, l2book 1.6 GB) | Raw on-chain fills and L2 around the 2025-10-10 liquidation cascade (a documented stress event). Not downloaded, not inspected; description only. | Candidate for a stress-event window; the contents of `fills_by_coin` (account field) are unverified. |
| Zenodo 23119136 Polymarket "Ghost-Filled Orders" (cc-by-4.0, 2.35 GB zip) | 1,890,105 reverted Polymarket settlement transactions with the orders of each reverted settlement, 2025-08-31 to 2026-08-31. Description only. | Not opened. Account fields unverified. |

## 3. Sources I could not find or reach

- Mt. Gox leaked trade logs (about 14 to 18 million trades, internal numeric user IDs, April 2011 to November 2013; used by Gandal, Hamrick, Moore and Oberman, and by Aloosh and Li). Searched Zenodo ("mtgox", "Mt. Gox trades"), Hugging Face and Kaggle: no copy found. The web search returned only papers and slides, no download link. Not verified and not reachable. Authors would have to be asked, and the data contain user-level records of a hacked exchange.
- Stock or futures datasets with trader, broker or account IDs (Taiwan, Korea, India, China, Finland, Spain, Italy, Japan). Searches on Zenodo, Harvard Dataverse and the web found no public deposit with account or member identifiers for a stock or futures exchange. Web sources agree that such data (Tokyo Stock Exchange anonymised trader labels, Nasdaq OMX, E-mini member IDs, Chinese buyer and seller account IDs) are proprietary or restricted. openICPSR was blocked (403) so I could not search it. Hugging Face `venvoo/china-a-share-l2-level2-limit-order-book-tick-data` appears in search results (78,497 downloads) but I did not inspect it; Chinese L2 tick feeds normally have no account IDs, so I expect none (unverified).
- Kalshi public trades (`/trade-api/v2/markets/trades`) have no account field (fields: trade_id, ticker, prices, count, taker_side, created_time). dYdX v4 indexer trades (`/v4/trades/perpetualMarket/BTC-USD`) have no account field. Neither is usable.
- Official Hyperliquid archive on S3 (`hyperliquid-archive`) returns 403 (requester pays). The Hugging Face mirrors in 1.2 are the practical route.
- GitHub repositories with NFT wash-trading code and data (for example the LooksRare/Meebits repo that WebFetch summarised: 14,186 sales, 5,948 wallets, MIT, no ground-truth labels, detector outputs only). Not downloadable here (github.com 403 via curl, MCP restricted to the session repo; raw.githubusercontent.com does answer for individual files if the exact path is known). Marked unverified beyond the WebFetch summary.
- Bitcoin/other CEX trade logs with user IDs other than Mt. Gox: none found.

## 4. Comparison table

| Source | Real accounts | Order submissions | Trades with side | Taker/maker | Labels | Time resolution | Size | License |
|---|---|---|---|---|---|---|---|---|
| Zenodo 18184441 Hyperliquid L4 | yes (328,456 users) | yes (incl. rejected, cancels) | via orders and Trades files | yes (tif, aggressor, counterparties) | none | ns | about 195 GB | CC BY 4.0 |
| HF craftify2221 hyperliquid-fills-raw | yes (17.6k addresses in 91 min) | no | yes | yes (`crossed`) | none | ms | 0.5-1.25 GB per day | not declared |
| HF gionuibk node-fills-by-block | yes | no | yes | yes (`crossed`) | none | ms | 114 GB | not declared |
| Zenodo 4540223 IDEX/EtherDelta | yes (about 0.4k to 1.5k in 3 MB heads) | no | yes (tokens imply side) | yes (maker/taker, get/give) | rule-based, labels not shipped; self-trades visible | block (s) | 3.1 GB | CC BY 4.0 |
| Polymarket Data API | yes | no | yes | taker feed by default | none | s | capped at 10k offset per query | terms not verified |
| HF AiYa1729 polymarket-transactions | yes | no | yes | yes (maker and taker both named) | none | s (block) | 4.1 GB, 45.6M fills | MIT |
| Kaggle rngrng Polymarket up/down | yes | no | yes | no flag | outcomes only | s | 1.7 GB, 9.6M fills | CC0 |
| Kaggle ligengxin96 Polymarket sample | yes (55 wallets in the file) | no | yes | yes (`role`) | none | s | 2.9 MB | CC BY 4.0 |
| Kaggle vayuindexing WOJAK swaps | yes | no | yes (Buy/Sell) | no | heuristic, circular | block | 15 MB | CC BY-SA 4.0 |
| Kaggle nikih94uni NFT | yes | no | transfers only | no | per token, detector output | block | 20 MB | CC BY 4.0 |
| Synthetic sets (sergionefedov, quailmodel) | no | no | simulated | no | exact but synthetic | s | small | CC0 / CC BY-NC-SA |

## 5. Caveats that matter for a coordination test

1. No source ships ground-truth coordinated-manipulation labels at the account level for real flow. The only account-level wash-trading definition with a published rule is Victor and Weintraud, but the labels have to be rebuilt (self-trades can be read off directly: maker equals taker).
2. Hyperliquid and Polymarket addresses are pseudonymous. One operator can control many addresses, and Polymarket `proxyWallet` is a smart-contract proxy tied to one user. Accounts that look coordinated may be one entity (market-maker vaults, builder/relayer addresses, sub-accounts).
3. Timestamps on Hyperliquid and Polymarket are block time, so many events inside one block are exactly simultaneous. A test that depends on within-block ordering has no information to use there; use `oid` or `tid` ordering instead on Hyperliquid, `logIndex` on Polymarket CTF logs.
4. The Polymarket Data API and the Kaggle Polymarket tapes list both counterparties of a fill as separate rows without a reliable maker flag in the public feed (except the ligengxin96 sample and AiYa1729 set).
5. License terms are unverified for the two Hyperliquid Hugging Face mirrors and for Polymarket API terms.

## 6. Ranked summary: top 3 sources and commands to fetch samples

Ranking criterion: per-account time series of order submissions or trades with side on real accounts, with the most direct way to calibrate false alarms and, if possible, some positive cases.

1. **Zenodo 18184441, Hyperliquid L4 order statuses (CC BY 4.0).** The only source with per-account order submissions (accepts, rejects, cancels), side and nanosecond time. Unlabelled, so use it for false-alarm calibration and for planting known coordination into real flow. Start with SOL (smallest) and one hour.
2. **Hyperliquid per-fill tables on Hugging Face (craftify2221/hyperliquid-fills-raw first).** A year of ms-resolution fills with account address, side and taker flag, same venue as 1, so order and fill series can be cross-checked. License is undeclared.
3. **Victor and Weintraud, Zenodo 4540223 (CC BY 4.0).** The only real data with documented wash-trading accounts (self-trades and multi-account cycles on IDEX and EtherDelta). Executed trades only, block-level time; the labelling code is on GitHub, which I could not open, but self-trades are directly visible.

Runners-up: AiYa1729/polymarket-transactions (MIT, maker and taker named, 45.6M fills) as a second real venue; Polymarket Data API for fresh data.

### Commands (these are what produced the samples I analysed)

Zenodo Hyperliquid L4, first 10 MB of the SOL accepted-orders archive, then decompress the truncated xz stream and parse the first hourly member (needs only python3 with numpy; reads bytes, executes nothing from the file):

```bash
D=$SCRATCH/acct_data/zenodo_hl_l4_sample
mkdir -p "$D"
curl -sS -L -r 0-9999999 -o "$D/sol_orders_head.tar.xz" \
  "https://zenodo.org/api/records/18184441/files/sol_orders_202512.tar.xz/content"
# docs: README.md, SCHEMA.md; lookup tables (users.csv etc.): mapdir.tar.xz (10 MB)
for f in README.md SCHEMA.md; do curl -sS -L -o "$D/$f" "https://zenodo.org/api/records/18184441/files/$f/content"; done
# decode with python3 -I: lzma.LZMADecompressor().decompress(bytes) -> tar header (name at 0:100, octal size at 124:136)
# -> zlib.decompressobj(31) on the member -> numpy.frombuffer with the 54-byte dtype from SCHEMA.md
```

(A reusable script that does exactly this is `$SCRATCH/l4.py`; call it as `python3 -I l4.py <head.tar.xz> <out.bin>`.)

Hyperliquid fills (Hugging Face), one row group and only the needed columns via HTTP range requests (script at `.../scratchpad/rangepq.py`, usage `python3 -I rangepq.py <url> <out.parquet> <comma-separated columns>`):

```bash
S=$SCRATCH
D=$S/acct_data/hl_fills_raw_sample; mkdir -p "$D"
python3 -I $S/rangepq.py \
  "https://huggingface.co/datasets/craftify2221/hyperliquid-fills-raw/resolve/main/fills/fills_raw_2026-06-05.parquet" \
  "$D/rg0.parquet" coin,price,size,side,timestamp,direction,order_id,trade_id,address,crossed,twap_id,is_liquidation
# small whole-file alternative from the other mirror (2.2 MB and 13.9 MB):
curl -sS -L -o "$D/hr.parquet" \
  "https://huggingface.co/datasets/gionuibk/hyperliquid-node-fills-by-block/resolve/main/data/node_fills_by_block_hourly_20250806_23.parquet"
```

Victor and Weintraud, first 3 MB of each file (complete lines only; drop the last partial line):

```bash
D=$SCRATCH/acct_data/vw_idex
mkdir -p "$D"
curl -sS -r 0-3000000 -o "$D/IDEXTrades_head.csv" \
  "https://zenodo.org/api/records/4540223/files/IDEXTrades.csv/content"
curl -sS -r 0-3000000 -o "$D/EtherDeltaTrades_head.csv" \
  "https://zenodo.org/api/records/4540223/files/EtherDeltaTrades.csv/content"
# full files: IDEX 2.1 GB, EtherDelta 1.05 GB (about 3.1 GB total, outside the 300 MB budget)
```

Polymarket (optional extras):

```bash
curl -sS "https://data-api.polymarket.com/trades?limit=10000" -o polymarket_latest10000.json
# per market: ...?market=<conditionId>&limit=10000   per wallet: ...?user=<0xaddress>&limit=2000   (offset capped at 10000)
# AiYa1729 (MIT): range-read one row group of
#   https://huggingface.co/datasets/AiYa1729/polymarket-transactions/resolve/main/polymarket-transactions-including-negrisk-prepped-for-ml.parquet
#   columns blockNumber,transactionHash,timeStamp,taker,taker_side,maker,maker_side,fill_price,volume,market
```

Disk use of the samples: about 480 MB extracted, of which the Kaggle synthetic sets (sergionefedov, 205 MB) can be deleted; network transfer was about 230 MB.
