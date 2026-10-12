# External data used by the experiments (not redistributed)

Set `MARKETSIM_DATA` to a directory laid out as below; every download should go in its own empty directory and be read as data only
(never unpickle or execute anything from a download).

| purpose | source | expected path under `$MARKETSIM_DATA` |
|---|---|---|
| daily prices of 1,551 stocks (cases, tick reform, calibration) | Kaggle `vuthinh/vietnam-stock-market-ohlc-price-data` | `data/x_vuthinh_vietnam-stock-market-ohlc-price-data/ohlcv_dataset_1d_1m/1D/*.parquet` |
| VN30, VN-Index, VN100 bars | Kaggle `keithvo/vnstockdata` | `data/x_keithvo_vnstockdata/HOSEVN301D.csv` etc. |
| VN30F1M ticks (spread) | Kaggle `khimduong/vn30-market-making` | `data/x_khimduong_vn30-market-making/` |
| exchange of each ticker | Hugging Face `kjhq/Vietnam-Stock-Symbols-and-Metadata` | `data/raw/vn_symbols.csv` (columns `ticker`, `market`) |
| Telegram pump events (cryptocurrency) | Hugging Face `Go3x3/pump_and_dump_dataset` (MIT) | see `experiments/run_pump_events.py` |
| real order submissions with account ids | Zenodo 18184441, `sol_orders_202512.tar.xz` (CC BY 4.0), first member decoded to 54-byte records | `acct_data/zenodo_hl_l4_sample/first_member.bin` |
| real fills with account addresses | Hugging Face `craftify2221/hyperliquid-fills-raw`, one row group of `fills/fills_raw_2026-06-05.parquet` (no licence declared) | `acct_data/hl_fills_raw_sample/rg0.parquet` |

Kaggle datasets can be fetched anonymously with the public API (`/api/v1/datasets/download/<owner>/<dataset>`); the Zenodo file can be
read in part with an HTTP range request (`Range: bytes=0-9999999`) and decoded with the record layout of `experiments/run_real_accounts.py`
(`L4_DT`). Licences of the Kaggle and Hugging Face mirrors were not verified; check them before redistributing any file.
