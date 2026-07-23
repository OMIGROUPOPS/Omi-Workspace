# Window-1 Source-Recovery & Real-Start Truth — Update (CC)

Read-only. Corrects the depth/prints verdict in AUDIT_REPORT.md and answers
"normalization failure vs genuine raw-data absence." No raw identities/account
data/credentials committed. Spaces queried read-only (creds from .env, never printed).

## CORRECTION to prior verdict
My prior report concluded the depth-pressure enhancement was "unsubstantiable —
order-book microstructure data does not exist for Window-1." **That is wrong.** It
was based on the frozen normalized dir (`books.jsonl=0`, `prints.jsonl=0`) and local
disk only. **The raw data exists in DO Spaces (`omi-tick-archive`).**

## 1. Normalization failure vs genuine absence — ANSWER: NORMALIZATION FAILURE

| Source | Local root / volume | DO Spaces (Jul 12–20) | Verdict |
|---|---|---|---|
| BBO + full 5-level depth (with sizes) | rotated off (500 MB cap / disk pressure) | **`ticks/` present** — CSV cols: `bid_1..5(+sz), ask_1..5(+sz), mid, bid_depth_5, ask_depth_5, depth_ratio, last_trade` | recoverable |
| Sized prints (price, count, taker_side) | rotated off | **`trades/` present** | recoverable |
| Raw WS depth (orderbook_delta) | only ~30 recent hrs | **`ws_depth/` present** (215 window objects) | recoverable |

`books_rows=0` because the normalizer read rotated-off **local** disk, not Spaces.
`prints_rows=0` because the normalizer required an **exchange-receipt identity** the
WS-derived prints lack — a strictness choice, not data absence. Sample leg
(`…26JUL12ALVVAN-ALV`): **71,985 depth snapshots** + sized prints recovered.

## 2. Event-by-event coverage table (804 games)
- Depth-tick CSV present for **1608/1608 leg-tickers = 100%**; **804/804 games have BOTH legs covered.**
- Trade/prints CSV present for **1569/1608 legs = 97.6%** (the 39 missing are zero-trade markets → legitimately no prints).
- Spaces totals: ticks 28,739 objects, trades 26,812, ws_depth 698; bucket 56,249 objects / 20.3 GiB.

## 3. Recovery (BBO + real-sized prints; full depth not required)
Demonstrated recoverable per leg: 5-level BBO+depth ticks and sized prints
(`px, ct, taker_side`). No full-depth requirement needed — BBO+sized-prints alone
are present at ≥97.6% and enable imbalance/absorption/depletion/executable-5-depth
tests the prior normalization omitted.

## 4. Real-start reconstruction & schedule-substitution quantification
- Benchmark used a **verified start for only 40/804** → **764 schedule-only substitutions.**
- `observed_starts.first_inplay_at` (a real-start table) is **sparse**: 69 rows total,
  14 in-window, stops at 2026-07-14 — insufficient alone.
- `live_scores` covers 417 distinct in-window tickers (leg-keyed, needs mapping).
- **The recoverable depth-tick `last_trade` onset + `trades/` prints (100%/97.6% coverage)
  reconstruct real start for effectively all 804 games** → the 764 substitutions are largely
  a **normalization gap**, not forced by absence. (A full 804-game reconstruction was not
  completed here; the data and method are proven.)

## 5. Mayo/Michelsen (KXATPCHALLENGERMATCH-26JUL21MICMAY)
- Both legs' **depth-tick CSVs exist in Spaces** (`…MICMAY-MAY.csv.gz`, `…-MIC.csv.gz`;
  676 objects for 26JUL21). The trades CSV is absent for this event (a Jul-21 trades-sync
  gap), but the depth ticks carry `last_trade`, enabling real-start reconstruction against
  the false ~22:00 ET schedule and the P0-established ~19:00 ET real start. Data recoverable;
  exact-timing recompute pending (large-file parse).

## 6. Metric labels (corrected per operator: D/C/P/N/I/X; P/N/I ⊂ C)
The prior table mislabeled capture as `C` and computed a rate over all of D. Corrected
framing: `D=804` (immutable); `X` = games outside the committed/covered set; `C` = committed
games; `P/N/I` (pass/nonfill/indeterminate) are **subsets of C**. The capture rate must be
computed within `C` using **receipt-based fills bounded by reconstructed real-start windows**,
not over raw D with schedule windows.

## 7. Retraction of the 4.9–17% figure
The prior **4.9–17%** dual-capture figure is **retracted as a ceiling / policy result.** It was
computed over all of D with schedule-derived evaluation windows and with depth/prints absent
from normalization. With recovered 5-level depth + sized prints + reconstructed real starts,
fill/nonfill window boundaries change and capture must be recomputed within C. Do not cite
4.9–17% as an outcome.
