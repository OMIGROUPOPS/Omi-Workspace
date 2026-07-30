# ATLAS key mismatch, interim aim, monitor, and retention

**Finding:** live ATLAS is semantically mis-keyed. It was fitted on the
first-hour-median discovery price, but `live_v4` selects the page from the
fresh price at the later order consultation. The safest interim aim in both
tests is table-free **JOIN (rest at best bid)**. It is not activated in the
deployed config; ATLAS remains configured, sealed authority remains disabled,
and `live_v4` remains stopped.

## 1. Key displacement across the 804

The unchanged live decision path was replayed until both legs first consulted
ATLAS. Population: 1,608 legs = 1,512 signed, 46 consulted but did not sign,
26 never consulted, and 24 with no positive replay interval. A retained live
consultation price and a frozen first-hour discovery price existed for 1,408
legs; the other 200 are not silently imputed.

Across the 1,408 measurable legs:

- signed orders: 1,367;
- absolute discovery-to-consultation movement: median 0c, p90 1c, maximum
  63c;
- one-cent cell displacement: median 0 cells, p90 1 cell, range -18 to +63;
- the broad live ATLAS page changed on 31 legs;
- ATLAS depth changed by -7c to +8c on page-crossers, but median and p90 were
  both 0c because most price movement stayed inside the same broad page;
- implied aim error was -18c to +55c, median 0c, p90 +1c.

| Category | n | signed | absolute move median / p90 / max | page changes | depth error min / p90 / max | implied aim error min / p90 / max |
|---|---:|---:|---:|---:|---:|---:|
| ATP Challenger | 655 | 630 | 0 / 1 / 19c | 12 | -2 / 0 / +1c | -18 / +1 / +19c |
| ATP Main | 263 | 260 | 0 / 1 / 63c | 11 | -7 / 0 / +8c | -16 / +1 / +55c |
| WTA Challenger | 236 | 229 | 0 / 1 / 12c | 2 | 0 / 0 / +1c | -2 / +0.5 / +12c |
| WTA Main | 254 | 248 | 0 / 1 / 7.5c | 6 | -4 / 0 / +2c | -7.5 / +0.5 / +5c |

The JSON contains `by_fit_one_cent_cell` and `by_live_one_cent_cell` with n
and the complete displacement/depth distributions for every observed cell.

### ALVVAN reconciliation

The reported ALV `28c -> 2c` swing belongs to the separate one-cent
`recut_cells` surface, not the table the live order path reads.

- ALV: fitted discovery 78.5c, live consultation 79c. Both select
  `ATP_CHALL|leader|ge75`; live ATLAS depth is 5c on both keys. Implied aim
  error: +0.5c.
- VAN: fitted discovery 22c, live consultation 26c. The page changes from
  `underdog|le25` to `underdog|26_50`; depth changes 3c -> 4c. Implied aim
  error: +3c.

This does not make ATLAS lawful. It shows that its actual broad-page
implementation dampens most one-cent key movement while leaving large,
unbounded tail failures at page/role crossings.

## 2. Interim aim comparison

Fill model: **we rest an order; a later true trade or opposite BBO touches or
passes it; it fills. No depth proof and no five-contract gate.**

The wider comparison uses the same first consultation and full guarded
Window 1. The 111 evaluator-invalid games remain unmeasurable.

| Authority | both-leg target available | legs filled | pairs completed | negative combined-delta completions | both legs below own close |
|---|---:|---:|---:|---:|---:|
| ATLAS | 547 | 163 | 8 | 7 | 4 |
| JOIN | 515 | 520 | **51** | **46** | **26** |
| touch-1 | 513 | 374 | 30 | 29 | 21 |
| 1x spread below mid | 511 | 365 | 27 | 26 | 20 |

In the exact full-OS replay of the same five selected games:

| Authority | legs filled | pairs completed | negative combined-delta pairs |
|---|---:|---:|---:|
| ATLAS | 4 | 0 | 0 |
| JOIN | **6** | **1** | **1** |
| touch-1 | 5 | 1 | 1 |
| 1x spread below mid | 5 | 1 | 1 |

**Interim answer: JOIN.** It uses only the synchronous best bid, has no fitted
surface or key contract to violate, and beats ATLAS on reach and negative
close-delta value in both comparisons. Missing/crossed BBO returns
`NO_DENOMINATOR`; it never falls back to an absolute-cent line.

## 3. Observe-only wrongness monitor

The monitor is installed on the VPS with
`wrongness_monitor_mode=observe_only`. It cannot veto, reprice, place, cancel,
or mutate an order.

Volume during the corrected 804 replay:

| Alarm | invocations | games affected |
|---|---:|---:|
| ATLAS fit/consult key mismatch | 8,072 | 785 |
| consulted surface has no machine-readable fit contract | 8,072 | 785 |
| computed verdict ignored by downstream effect | 942 | 761 |
| fitted row n < 20 | 15 | 10 |

These are dossier-invocation counts, not unique legs. `live_v4` is stopped, so
there is no live-order alarm volume yet. Deployed state was rechecked:
ATLAS configured, sealed/one-authority false, recorder running.

## 4. Retention burn-down

Pre-fix observation: 6.218 hours, 550 tennis leg tickers, 6,695,262 book
deltas, and 59,837 trades produced **zero** lawful anchors. The recorder was
reading obsolete message fields:

- snapshots: expected `yes`/`no`; feed sends
  `yes_dollars_fp`/`no_dollars_fp`;
- deltas: expected `price`/`delta`; feed sends
  `price_dollars`/`delta_fp`.

Raw frames were retained, but every derived BBO was null. There was no n=20
date under that contract: all 540 category/cell rows were unprojectable.

The parser was repaired, tested, deployed, and only the read-only recorder was
restarted. A real post-repair snapshot immediately emitted
`yes_bid=27`, `yes_ask=28`, `denominator_status=AVAILABLE`.

Post-fix provisional observation (44.6 minutes):

- 548 distinct tennis leg tickers observed;
- 143 distinct leg-days already carry a trade price plus two-sided BBO,
  receive timestamps, provider timestamps, and raw hashes within 30 minutes;
- current captured coverage: 143 / 548 = 26.1%;
- acquisition pace during this initial partial session: 192.18 new lawful
  leg anchors/hour. This is reported separately and is **not** multiplied by
  24 because the initial snapshot burst is not a stationary daily rate.

| Category | retained anchors | cells with any n | largest cell n | cells already n>=20 | cells with no projected date |
|---|---:|---:|---:|---:|---:|
| ATP Challenger | 19 | 17 | 2 | 0 | 73 |
| ATP Main | 12 | 9 | 3 | 0 | 81 |
| ITF Men | 42 | 31 | 3 | 0 | 59 |
| ITF Women | 53 | 44 | 2 | 0 | 46 |
| WTA Challenger | 8 | 7 | 2 | 0 | 83 |
| WTA Main | 9 | 9 | 1 | 0 | 81 |

No cell is n=20 yet. Among cells that have appeared, the slowest straight-line
date is 2026-08-18 (about three weeks). But 46-83 cells per category have not
appeared at all and therefore have **no date**. It is not honest to claim that
an entire category clears in weeks at the present observed coverage.

## 5. Deployed state

- `live_v4.py`: stopped.
- wrongness monitor: installed, observe-only.
- configured interim authority: still `ATLAS` (JOIN recommendation not
  activated).
- sealed/one-authority action: `false`.
- recorder: running with current Kalshi fixed-point field contract.
- free VPS space after installation: 24 GB.
- focused regression set: 25/25 passed.
