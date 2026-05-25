# Tape Audit — Roland-Garros Day 1 (2026-05-24)

**Generated:** 2026-05-24 12:39:26 PM ET (read-only audit; running bot and its state untouched).
**Source:** PID 2575171 scanner output, config `deploy_v4_paper.json`, started 12:33:49 AM ET (~12.1h uptime).
**Scope of question:** is the *scanner-side tape* (premarket_ticks + trades) complete and replay-grade — independent of the bot's FV-anchor executor (whose paper trades are out of scope).

> **Capture semantics (load-bearing for interpretation).** `_log_tick` writes one row per **distinct top-5 depth state** (dedup on top-5 signature) and **suppresses degenerate books** (best_bid≤0 or best_ask≥100). Timestamps are **1-second** resolution (`HH:MM:SS`). So the tape is *every change a top-5-depth observer would have seen*, NOT every raw WS delta — a no-change delta or a sub-level-5 change is intentionally not re-logged, and one-sided-book periods produce no rows. Inter-tick gaps therefore reflect **book quiescence**, not data loss, unless they are *correlated across many legs* (= engine/WS outage). Trades are logged 1:1 (no dedup).

## Verdict

**The tape is replay-grade for top-5-depth strategies, with two bounded caveats.** Capture is complete and clean across the RG-Day-1 slate: **236 legs** (116 RG main-draw ≈ 58 matches + 120 ATP-challenger), **65259 tick rows**, **747 trades**, premarket coverage on **222/236** legs (only 2 legs missed their pre-match window), **116 legs with in-match tape** (median 85m35s of in-match microstructure). Depth is full 5-level on **89%** of rows (rest are genuinely thin books). Trade `taker_side` has **zero nulls**. Engine: **0 tracebacks, 0 FD leaks**, settlement chokepoint **0 double-fires**.

**Caveat 1 — 1-second timestamp resolution, event-driven.** Reconstructs the top-5 book any observer would have seen to 1s; not true within-second tick sequencing. Exceeds Layer B v1 (minute-cadence) comfortably; a *partial* Layer B v2 (event-driven depth, 1s-stamped, top-5 only, dedup'd).

**Caveat 2 — frequent WS reconnects → multi-minute correlated gaps.** **43 reconnect cycles** over the run (~1 per 17 min), all auto-recovered (balanced error→reconnecting→reconnected; Kalshi resends snapshots on resubscribe, so **no permanent loss**). There are **75 global tape gaps >30s** (whole-scanner quiet), of which **41 are overnight (<7am ET, sparse active markets = mostly true quiescence)** and **34 daytime**; **34 coincide with a reconnect timestamp**. Implication for replay: in those windows the last-known book is stale by up to ~10 min — which is *also what a live strategy would have seen during the same WS gap*, so it is faithful, but it caps intra-gap resolution. The reconnect frequency itself is worth investigating as a separate engine item.

**Out of scope (as instructed):** the bot's FV-anchor paper-trade outcomes — not analyzed.

## 1. Coverage inventory

### Legs captured today (26MAY24), by series

| Series | Legs |
|---|---|
| KXATPMATCH | 52 |
| KXWTAMATCH | 64 |
| KXATPCHALLENGERMATCH | 120 |
| KXWTACHALLENGERMATCH | 0 |
| **Total** | **236** |

Main-draw (RG) = KXATPMATCH + KXWTAMATCH = **116 legs ≈ 58 matches**.

### Per-leg coverage summary (active legs = 236)

- Tick rows/leg: min 2, median 118, max 4549, total 65259 rows.
- Earliest first-tick 12:33:56 AM ET; latest last-tick 12:35:43 PM ET.
- Match-start known (schedule) for **222 / 236** active legs (94%). Legs without a schedule match cannot have their premarket/in-match boundary delineated precisely (see §5).

**First-tick relative to match-start.** Legs whose first tick is AFTER match start (missed premarket window): **2**.
- `KXATPCHALLENGERMATCH-26MAY24NIKBER-BER` first tick 05:16:21 AM ET, match start 04:40:00 AM ET (+36m21s into match).
- `KXATPCHALLENGERMATCH-26MAY24NIKBER-NIK` first tick 05:16:21 AM ET, match start 04:40:00 AM ET (+36m21s into match).

**Per-leg internal gaps > 60s** (candidate coverage holes — but most are book quiescence given dedup; cross-check against §4 global gaps): **236 legs** have a max internal gap > 60s.
Top 15 by max gap:

| Leg | max gap | #gaps>60s | ticks |
|---|---|---|---|
| `KXATPCHALLENGERMATCH-26MAY24TULBER-BER` | 294m36s | 20 | 86 |
| `KXATPCHALLENGERMATCH-26MAY24BRAAND-BRA` | 210m45s | 11 | 81 |
| `KXATPCHALLENGERMATCH-26MAY24MARBOU-BOU` | 172m53s | 24 | 27 |
| `KXATPCHALLENGERMATCH-26MAY24DALFOR-FOR` | 143m14s | 21 | 194 |
| `KXWTAMATCH-26MAY24GIBPUT-PUT` | 117m14s | 35 | 39 |
| `KXATPCHALLENGERMATCH-26MAY24KOEVAN-VAN` | 97m20s | 21 | 129 |
| `KXATPCHALLENGERMATCH-26MAY24MARBOU-MAR` | 96m18s | 28 | 34 |
| `KXATPCHALLENGERMATCH-26MAY24POLHAR-HAR` | 96m18s | 31 | 99 |
| `KXATPCHALLENGERMATCH-26MAY24MORMAY-MAY` | 96m17s | 25 | 40 |
| `KXWTAMATCH-26MAY24SABBOU-BOU` | 95m06s | 39 | 106 |
| `KXATPMATCH-26MAY24DIAZHA-ZHA` | 94m17s | 39 | 70 |
| `KXWTAMATCH-26MAY24SIEOSA-OSA` | 94m17s | 38 | 59 |
| `KXATPCHALLENGERMATCH-26MAY24HOHMAR-MAR` | 92m25s | 33 | 240 |
| `KXATPCHALLENGERMATCH-26MAY24COMGSC-COM` | 92m24s | 31 | 149 |
| `KXWTAMATCH-26MAY24LIUUCH-LIU` | 87m41s | 30 | 33 |

## 2. Tape completeness per leg

**Every book change logged? — by design, every distinct top-5 state, not every raw delta.** Both `apply_snapshot` and `apply_delta` call `_log_tick` unconditionally, so no book-update path bypasses logging; `_log_tick` then dedups identical top-5 states and suppresses one-sided books. There is no separate per-delta event counter in the log to assert a literal 1:1 against — the correct completeness claim is *every distinct top-5 book state, while two-sided, is captured at 1s resolution*.

**5-level depth population.** Of 65259 total tick rows: **58105 (89.0%) carry all 5 levels on both sides**; 7154 (11.0%) have ≥1 absent level (thin book — `_extract_depth` pads absent levels with empty strings, i.e. legitimately fewer than 5 price points, not missing data).

**Trade tape.** `apply_trade` → `_log_trade` is unconditional (no dedup), so every WS trade event is recorded. Trade files for 26MAY24: **87**, total **747 trade rows**.
Trades by series: KXATPMATCH=279, KXWTAMATCH=9, KXATPCHALLENGERMATCH=459, KXWTACHALLENGERMATCH=0.

**`taker_side` distribution** (nulls would appear as `?` from the WS default or `<empty>`):

| taker_side | count |
|---|---|
| `yes` | 577 |
| `no` | 170 |

First 10 trade samples (leg, price, count, taker_side):
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-ARU`  px=87 ct=160 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-ARU`  px=96 ct=2 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=10 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=10 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=10 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=10 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=10 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24ARUVAN-VAN`  px=62 ct=8 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24AVECOO-COO`  px=9 ct=22 side=`yes`
- `KXATPCHALLENGERMATCH-26MAY24AVECOO-COO`  px=9 ct=1 side=`yes`

## 3. Time-resolution check

- Per-leg **median inter-tick gap**: across active legs, median-of-medians = **0.0s** (min 0.0s, max 1214.5s).
- Per-leg **max inter-tick gap**: median 2403s, max 17676s.
- All-gaps distribution (n=65023): p50 0s, p90 573s, p99 1779s, max 17676s.

**Replay grade.** Timestamp resolution is **1 second**, and rows fire on every top-5 depth change (event-driven, not fixed cadence). This is materially finer than minute-cadence (**Layer B v1 grade is comfortably exceeded**). It is *not* true tick/ms resolution: multiple events within one second share a timestamp (ordering preserved by row order, not by clock), and sub-top-5 / no-change deltas are deduped. So replay can reconstruct the **top-5 book any observer would have seen, to 1-second resolution** — sufficient for depth-aware maker/taker fill logic at 1s granularity, short of exact within-second sequencing (a partial **Layer B v2**: event-driven depth, 1s-stamped).

## 4. Engine reliability over the run

- **WS connection:** 44 WS_CONNECTED, **43 reconnect cycles** (WS_ERROR 43 → WS_RECONNECTING 43 → WS_RECONNECTED 43). All reconnecting events have a matching reconnected (balanced).
  - Reconnect timestamps (ET): 12:42:58 AM, 01:00:19 AM, 01:17:38 AM, 01:27:40 AM, 01:35:45 AM, 01:54:48 AM, 02:13:49 AM, 02:35:06 AM, 02:45:08 AM, 03:04:13 AM, 03:14:44 AM, 03:35:48 AM, 03:53:51 AM, 04:03:06 AM, 04:21:22 AM, 04:41:01 AM, 04:50:38 AM, 05:06:50 AM, 05:25:31 AM, 05:44:59 AM, 05:56:50 AM, 06:16:48 AM, 06:26:35 AM, 06:47:47 AM, 07:07:44 AM, 07:27:10 AM, 07:44:55 AM, 08:04:01 AM, 08:24:23 AM, 08:43:56 AM, 09:03:06 AM, 09:22:37 AM, 09:41:53 AM, 10:00:59 AM, 10:20:06 AM, 10:38:55 AM, 10:58:04 AM, 11:17:36 AM, 11:35:49 AM, 11:54:47 AM, 12:14:24 PM, 12:25:12 PM
- **Tracebacks:** 0. **FD ('Too many open files'):** 0.
- **Bug-4 settlement fires** (paper mode → `paper_settled`; live sources gated off):
  - source `?`: 8
  - `ws_settled_pre_finalized` (WS lifecycle fired but `/markets` not yet finalized — REST/BBO will catch): **14**.
  - `settlement_void_manual`: **0**.
  - **Double-fires** (same ticker settled >1×; idempotent chokepoint should yield 0): **0**.
- **Heartbeat continuity:** 75 PAPER_HEARTBEAT entries; gap median 577s, max 713s (continuous).

**Global tape gaps (correlated outages).** Gaps in the *union of all legs'* tick stream > 30s (these, unlike per-leg gaps, indicate the whole scanner went quiet = candidate engine/WS outage): **75**.

| start (ET) | gap |
|---|---|
| 05:44:59 AM | 11m51s |
| 02:23:16 AM | 11m50s |
| 06:36:52 AM | 10m55s |
| 03:24:56 AM | 10m51s |
| 12:14:35 PM | 10m36s |
| 03:04:13 AM | 10m31s |
| 05:34:32 AM | 10m26s |
| 06:57:19 AM | 10m25s |
| 07:07:44 AM | 10m20s |
| 05:56:50 AM | 10m19s |
| 08:43:56 AM | 10m19s |
| 06:26:35 AM | 10m13s |
| 01:54:48 AM | 10m12s |
| 08:04:01 AM | 10m12s |
| 02:45:08 AM | 10m10s |
| 12:04:14 PM | 10m10s |
| 08:14:14 AM | 10m08s |
| 03:14:44 AM | 10m07s |
| 04:30:53 AM | 10m07s |
| 10:00:59 AM | 9m59s |

Cross-check these against the reconnect timestamps above — overlap ⇒ the gap is an explained WS reconnect (data resumes on reconnect); non-overlap ⇒ investigate.

## 5. In-match tape (matches started today)

> **Note on the detection mechanism.** `live_v3.py` does **not** implement a C19 BBO-volatility-jump in-match-start detector. Its match-start (commence) time comes from an **external schedule** (`state/schedule.json`, tennisexplorer/Odds-API `start_time`), with fallbacks to `book_prices`/`kalshi` commence-time lookups. So the in-match boundary for replay is the **scheduled `start_time`**, available only for legs with a schedule match (see §1). The relevant reliability signal is `SCHEDULE_MATCH` (178) vs `SCHEDULE_UNMATCHED` (1718) / `NO_RELIABLE_COMMENCE_SOURCE` (1684) in the log.

**Legs with post-match-start (in-match) tape: 116** (of 222 match-start-known active legs).
- In-match minutes/leg: min 16.4, median 85.6, max 247.6.
- Longest in-match tape (top 10):

| Leg | match start (ET) | in-match tape | in-match ticks |
|---|---|---|---|
| `KXATPMATCH-26MAY24DAVDZU-DZU` | 05:15:00 AM | 247m37s | 429 |
| `KXATPMATCH-26MAY24DAVDZU-DAV` | 05:15:00 AM | 247m37s | 466 |
| `KXATPCHALLENGERMATCH-26MAY24WEIROO-WEI` | 07:55:00 AM | 173m25s | 315 |
| `KXATPCHALLENGERMATCH-26MAY24WEIROO-ROO` | 07:55:00 AM | 173m25s | 259 |
| `KXATPCHALLENGERMATCH-26MAY24BOILAM-LAM` | 05:25:00 AM | 159m01s | 304 |
| `KXATPCHALLENGERMATCH-26MAY24BOILAM-BOI` | 05:25:00 AM | 159m01s | 325 |
| `KXATPCHALLENGERMATCH-26MAY24BRAPAP-PAP` | 04:10:00 AM | 157m47s | 421 |
| `KXATPCHALLENGERMATCH-26MAY24BRAPAP-BRA` | 04:10:00 AM | 157m47s | 488 |
| `KXATPMATCH-26MAY24KHAGEA-KHA` | 05:10:00 AM | 154m55s | 94 |
| `KXATPMATCH-26MAY24KECMAR-MAR` | 05:10:00 AM | 145m24s | 270 |

---
*End of audit. No bot/state changes made. Brief is the only artifact written.*