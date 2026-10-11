# Vietnam calibration

What the simulator takes from the Vietnamese market, where each number comes from, and what could not be
calibrated. Facts were collected on 2026-10-09 from broker rule summaries and press reports. The HOSE and HNX
rulebooks themselves could not be fetched, so every rule below is **SECONDARY** and should be checked against the
exchange notices before it is relied on. Tags: SECONDARY (secondary source), DERIVED (computed from other rows),
UNVERIFIED (single weak source), NOT FOUND.

## Mapping from the market to simulator units

| Simulator | Market | Basis |
|---|---|---|
| 1 price tick | 1 HOSE tick | tick table below |
| reference price 500 ticks | a 25,000 VND stock: 50 VND tick, relative tick 0.2% (20 bps) | DERIVED from the tick table |
| 1 quantity unit | one round lot, 100 shares | lot size below |
| 1 step | about one trading minute | assumption (VN30F1M has a median of 4,937 ticks per day) |
| 240 steps per day | about 225 minutes of continuous matching plus auctions | assumption |
| daily band 7% (`Policy.band`) | HOSE daily price limit | band table below |
| block of 3000 lots | 300,000 shares held before a campaign and sold off-book | assumption; HOSE negotiated trades start at 20,000 shares |

The default simulator (price 10,000 ticks) has a relative tick of 1 bp, which is 20 times finer than a typical HOSE
mid-cap. `marketsim.vietnam.vn_config()` uses the 500-tick preset.

## Rules used

| Item | Value | Tag | Source |
|---|---|---|---|
| HOSE tick | 10 VND below 10,000 VND; 50 VND for 10,000-49,950; 100 VND from 50,000; ETFs and covered warrants 10 VND | SECONDARY | [FPTS HOSE trading rules](https://fpts.com.vn/customer-service/securities-trading/stock-trading-guide/trading-regulations/hose-trading-regulations/) |
| HOSE tick tiers since | 2016-09-12 | SECONDARY | [Vo and Doan, PLOS ONE 2023](https://ideas.repec.org/a/plo/pone00/0285821.html) |
| HNX and UPCoM tick | 100 VND for matched orders | SECONDARY | [HNX rules (VBSE PDF)](https://www.vbse.vn/wp-content/uploads/2025/08/KRX_2.Quy-dinh-giao-dich-chung-khoan-tai-HNX.pdf) |
| Daily band | HOSE +/-7%, HNX +/-10%, UPCoM +/-15% | SECONDARY | FPTS and VBSE links above |
| Round lot | 100 shares (HOSE, HNX); odd lots 1-99 on HOSE limit orders | SECONDARY | FPTS link |
| Sessions (HOSE) | ATO 09:00-09:15, continuous 09:15-11:30 and 13:00-14:30, ATC 14:30-14:45 | SECONDARY | FPTS link |
| KRX system | live since 2025-05-05; ATO/ATC lose priority over earlier limit orders; order amendment allowed, only a volume decrease keeps queue position; unfilled orders expire at session end | SECONDARY | [VnEconomy](https://vneconomy.vn/10-thay-doi-quan-trong-cua-he-thong-giao-dich-moi-nha-dau-tu-nen-nam-ro.htm), [Vietstock](https://en.vietstock.vn/2025/05/krx-system-operates-smoothly-on-its-first-trading-day-36-611694.htm) |
| Settlement | T+2; short selling and T+0 on cash equities not permitted | SECONDARY | [Luat Viet Nam](https://luatvietnam.vn/tin-van-ban-moi/chinh-sach-moi-co-hieu-luc-29-8-2022-186-91169-article.html), [24hmoney](https://24hmoney.vn/news/nghien-cuu-cho-phep-ban-khong-chung-khoan-som-nhat-tu-nam-sau-c1a2680830.html) |
| Under study (announced 2026-10-06, no decision) | cross-lunch trading, a wider daily band, removing periodic auctions, a shorter settlement cycle | SECONDARY | [Thoi bao Tai chinh](https://thoibaotaichinhvietnam.vn/chuyen-toan-bo-co-phieu-hnx-sang-hose-trong-nam-2026-nghien-cuu-giao-dich-xuyen-trua-va-noi-bien-do-204943.html) |
| HNX stocks move to HOSE | last HNX trading day 2026-12-23, HOSE trading from 2026-12-28 | SECONDARY | [Thi truong Tai chinh Tien te](https://thitruongtaichinhtiente.vn/toan-bo-co-phieu-niem-yet-se-giao-dich-tai-hose-tu-cuoi-thang-12-2026-85954.html) |
| Negotiated (off-book) trades | HOSE from 20,000 shares, HNX from 5,000 shares | SECONDARY | FPTS and VBSE links |

## Participant mix and activity

| Item | Value | Tag | Source |
|---|---|---|---|
| Retail share of trading value | above 80% in 2024; 82% on HOSE in Feb 2025; 75-80% in another 2025 estimate; ministry target about 70% in five years | SECONDARY | [VietnamNews](https://vietnamnews.vn/economy/1690395/retail-investors-net-buy-over-3-billion-on-stock-market-last-year.html) |
| Foreign share of HOSE value | 12.8% (Dec 2025), 15.6% (Sep 2026) | SECONDARY | [Tap chi Kinh te Tai chinh](https://tapchikinhtetaichinh.vn/thang-9-2026-giao-dich-chung-chi-quy-etf-tren-hose-tang-hon-15-168770.html) |
| Domestic institutions | not published; about 5-8% by subtraction | UNVERIFIED | derived |
| Trading accounts | 13.65 million at end of July 2026, of which 52,406 foreign | SECONDARY | [Tuoi Tre](https://news.tuoitre.vn/vietnam-adds-nearly-18-million-stock-trading-accounts-in-january-july-103260807164634054.htm) |
| HOSE 2025 daily average | 1.1 billion shares and 26,582 billion VND | SECONDARY | [VnEconomy](https://vneconomy.vn/hose-nam-2025-vn-index-chinh-phuc-moc-1784-diem-von-hoa-thi-truong-dat-tren-72-gdp.htm) |
| Amendments and cancellations as share of orders | 31.76% in Dec 2020 (4.4 million of 13.9 million); pre-KRX | SECONDARY | [VIR](https://vir.com.vn/hose-considers-suspending-amendment-and-cancellation-orders-while-trading-82982.html) |
| Margin balance | about 446 trillion VND at end of June 2026; initial margin not below 50%, maintenance not below 30%, set by each broker | SECONDARY | [VnEconomy](https://vneconomy.vn/du-no-margin-ky-luc-hon-446-nghin-ty-dong-phan-lon-tap-trung-vao-hoat-dong-cho-vay-theo-deal-rieng.htm), [Decision 87/QD-UBCK](https://dulieuphapluat.vn/van-ban/chung-khoan-van-ban/decision-no-87qd-ubck-dated-january-25-2017-on-the-promulgation-of-the-regulation-guiding-the-margin-trading-1111650.html) |

Moments matched by `marketsim.calibrate`: retail share 0.80, cancel share 0.3176, relative tick 20 bps, daily volatility 1.16% (measured, see below).

## Enforcement facts behind the policy experiments

| Item | Value | Tag | Source |
|---|---|---|---|
| Administrative fine cap | 5 times the illegal gain for individuals, 10 times for organisations (Decree 156/2020 as amended) | SECONDARY | [LSVN](https://lsvn.vn/du-kien-tang-muc-xu-phat-voi-vi-pham-hanh-chinh-linh-vuc-chung-khoan-a155365.html) |
| Listed manipulation acts | continuous buying and selling through own or others' accounts or collusion; wash trades; dominating volume at open or close; collusive or induced orders that move price | SECONDARY | [LSVN](https://lsvn.vn/nhung-hanh-vi-bi-coi-la-thao-tung-thi-truong-chung-khoan-tu-ngay-01-01-2025-a151870.html) |
| Cases: SJS (26 accounts), FIR (76 accounts) | 1.5 billion VND fines, 2-year trading bans | SECONDARY | [VnEconomy](https://vneconomy.vn/thao-tung-co-phieu-sjs-hai-ca-nhan-bi-phat-15-ty-dong-va-bi-cam-giao-dich-trong-2-nam.htm), [The Investor](https://theinvestor.vn/individual-fined-for-using-76-accounts-to-manipulate-stock-price-d7374.html) |
| Pattern across prosecuted cases | multi-account collusive trading dominates; no spoofing or layering prosecution found | SECONDARY | [VJOL](https://vjol.vista.gov.vn/HVNH-KHDAOTAONH/article/view/90100) |
| 2025 statistics (to 30 Nov) | 488 administrative decisions; 3 manipulation penalty cases; 83 exchange alert reports reviewed; 17 investor-trading inspection teams | SECONDARY | [Doanh nghiep Hoi nhap](https://doanhnghiephoinhap.vn/11-thang-nam-2025-uy-ban-chung-khoan-nha-nuoc-xu-phat-gan-60-ty-dong-124379.html) |

## Measured on real data

Computed by `experiments/real_data_stats.py` (output in `results/real_data_stats.md`) from two public Kaggle datasets, downloaded
without an account. Neither has account identifiers or order-level events; raw files are not stored here.

| Item | Value | Source |
|---|---|---|
| VN30 daily return sd | 1.16% (2023 onward), 1.19% (2012-2025); excess kurtosis 4.7; autocorrelation of absolute returns 0.20 at lag 1 | [keithvo/vnstockdata](https://www.kaggle.com/datasets/keithvo/vnstockdata) (ODbL) |
| VN-Index daily return sd | 1.09% (2023 onward), 1.44% (2000-2025); excess kurtosis 3.6; autocorrelation of absolute returns 0.46 | same |
| VN30 30-minute bars | 10 per day; 30-minute return sd 0.30% | same |
| VN30F1M spread | 1 tick in 73% of quote-bearing ticks, 2 ticks 16%, 3 ticks 6%; mean 1.1 bp | [khimduong/vn30-market-making](https://www.kaggle.com/datasets/khimduong/vn30-market-making) (licence not stated, provenance of ticks not documented) |
| VN30F1M activity | median 4,937 ticks per day, median gap 2.1 s; one-minute return sd 0.054% with excess kurtosis 42; daily sd 1.16% | same |

These are index and futures data, not single-stock order books. They fix the daily volatility target (1.16%) and show that the
real minimum spread is reached most of the time, which the simulator does not reproduce.

Other datasets found but not downloaded: an OHLC history of Vietnamese stocks to 2023
([vuthinh](https://www.kaggle.com/datasets/vuthinh/vietnam-stock-market-ohlc-price-data), 171 MB),
HOSE-HNX-UPCoM stock prices ([hoanganh4511](https://www.kaggle.com/datasets/hoanganh4511/stock-dataset-hose-hnx-upcom), 69 MB),
VN30F1M 1-minute data on [HuggingFace](https://huggingface.co/datasets/smtrading/VN30F1M). One Kaggle upload
(`graycie/stock-vn30-in-one-month`) is a Python pickle and was not opened, because loading a pickle can run arbitrary code.
`vnstock` on PyPI is flagged as quarantined and was not installed. The Vietnamese broker price APIs (SSI, TCBS, VNDirect) were
not reachable from this environment.

## Families of calibrated markets (ensemble)

A single calibrated market is one draw from many that fit the same moments, so policy conclusions are reported over a family
(`experiments/run_vn_ensemble.py`): market parameters (noise and fundamental traders, market-maker activity and depth
sensitivity, latent-value volatility, momentum activity) are drawn at random and kept when cancel share is 0.27-0.37, retail
share 0.66-0.85 and daily volatility lies in the target band. Two bands are used: index level (0.9-1.4%, the VN30 index at 1.16%)
and stock level (1.8-2.8%; the median HOSE stock has 2.46% since 2022 and the stocks in the enforcement cases had a median of
1.75% in the year before the manipulation; `results/case_stats.md`). The spread is not matched in either family. A third family (`--tag _acf`) adds the lag-1 autocorrelation of daily returns (at most 0.2 in absolute value, measured on four honest episodes) and a wider prior on the number of fundamental traders (80-220), with the retail-share tolerance widened to 0.55-0.85; it has four markets. Re-measured over 16 episodes (`results/calib_markets.csv`), some accepted markets of the first two families lie outside the tolerance box, because acceptance used two episodes.

## Public-data checks that are not calibration targets

* HOSE tick reform of 12 September 2016, difference-in-differences against HNX and UPCoM stocks (`results/tick_reform.md`). The
  old tick could not be established, so the simulator is compared through simulated tick cuts of 2, 5 and 10 times
  (`results/tick_sim.md`); the real zero-return and spread effects are of the order of a halving. Tick bands per
  Vo and Doan (2023), via the paper's reference list.
* Case stocks (`data/cases.csv`, `results/case_stats.md`): ordinary HOSE stocks that reached the daily ceiling on a median of five
  days in the manipulation period, one stock for 12 days in a row. The simulated ring's displacement (about 0.5%) never reaches the band.
* Telegram pump events (701 events, `results/pump_events.md`): volume and buy imbalance profile before and after the announcement.

## Not found, so not calibrated

Account-level order data (not public anywhere); order-to-trade ratios after KRX; published counts of surveillance alerts per day;
the share of manipulation cases that involve many accounts; spreads and depth of single stocks. The simulator's minimum spread is
2 ticks against 1 tick for VN30F1M, and it does not reproduce the measured tail heaviness (excess kurtosis 4-5 daily, 40 at one
minute) or the near-zero serial correlation of daily returns: simulated daily returns of the first accepted markets have lag-1 autocorrelation 0.49 (index level) and 0.60 (stock level) against -0.03 for VN30 and 0.03 on average for HOSE stocks.

## Plugging in real data

`marketsim.calibrate.moments_from_events` takes order-level events in the schema of `exchange.EVENT_COLUMNS`
(`t, kind, agent, oid, side, price, qty, mid, cpty, aggr`, with kinds 0 limit order, 1 market order, 2 cancel,
3 trade) plus a mid-price series, and returns the same moments as for simulated episodes.
`marketsim.coordination.scan_episode` needs only the order submissions (time, account, side) and runs unchanged on real
data converted to that schema.
