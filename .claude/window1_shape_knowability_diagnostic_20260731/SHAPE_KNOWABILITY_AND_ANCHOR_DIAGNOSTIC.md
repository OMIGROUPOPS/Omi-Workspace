# Window-1 shape knowability and anchor-placement diagnostic

Status: descriptive only. The quiet-book anchor is frozen and unchanged. No strategy, runtime, scorer, or candidate was modified or executed.

Population: the same 804 July 12–20 development/backwalk events, 1,608 legs. Every table is hard-partitioned by tournament category and the frozen current-bid price region. `UNAVAILABLE` is retained; it is not pooled. A cell with `n < 10` is `THIN`.

Raw timing source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_shape_knowability_diagnostic_20260731/SHAPE_KNOWABILITY_BY_CATEGORY_PRICE_REGION.json

Full per-leg receipt ledger:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_shape_knowability_diagnostic_20260731/LEG_SHAPE_TIMING_LEDGER.json

## 1. When the print-derived band becomes knowable

The frozen band fit uses only traded-price `(anchor, net, dip)`. A first lawful positive-size true print makes a provisional nearest-centroid band arithmetically callable. It does not prove that the call will remain stable. `Stable prints` below is the earliest print after which every later cumulative assignment through the guarded right edge equals the final assignment. That is an ex-post diagnostic, not knowledge available at that timestamp.

`First med/p90` are minutes after the discovery gate, defined as the first lawful positive-size non-crossed BBO at or after the Window-1 left edge. `Stable med` is minutes after that same gate. Quantiles use the frozen drift-surface rule: sorted value at `floor(p*n)`.

| Category | Price region | Legs | No print | First print ≤30m | First print ≤60m | First med | First p90 | First call = final | Stable prints med | Stable prints p90 | Stable lag med |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | le25 | 148 | 18 | 46 | 68 | 56.048m | 240.805m | 96.9% | 1 | 1 | 60.737m |
| ATP_CHALL | 26_50 | 256 | 9 | 74 | 127 | 58.439m | 230.490m | 95.5% | 1 | 1 | 63.909m |
| ATP_CHALL | 51_75 | 238 | 1 | 113 | 159 | 31.719m | 137.272m | 92.4% | 1 | 1 | 40.748m |
| ATP_CHALL | ge76 | 92 | 2 | 33 | 49 | 53.787m | 125.166m | 97.8% | 1 | 1 | 56.125m |
| ATP_CHALL | UNAVAILABLE | 4 | 4 | 0 | 0 | — | — | — | — | — | — |
| ATP_MAIN | le25 | 43 | 0 | 25 | 27 | 16.950m | 363.136m | 86.0% | 1 | 153 | 35.883m |
| ATP_MAIN | 26_50 | 107 | 2 | 62 | 75 | 19.255m | 163.898m | 95.2% | 1 | 1 | 25.763m |
| ATP_MAIN | 51_75 | 107 | 0 | 79 | 88 | 6.090m | 123.105m | 92.5% | 1 | 1 | 6.889m |
| ATP_MAIN | ge76 | 25 | 0 | 17 | 21 | 6.553m | 93.161m | 100.0% | 1 | 1 | 6.553m |
| ATP_MAIN | UNAVAILABLE | 12 | 12 | 0 | 0 | — | — | — | — | — | — |
| WTA_CHALL | le25 | 48 | 3 | 15 | 22 | 60.314m | 234.271m | 88.9% | 1 | 862 | 82.470m |
| WTA_CHALL | 26_50 | 95 | 1 | 30 | 45 | 65.362m | 264.766m | 70.2% | 1 | 676 | 166.868m |
| WTA_CHALL | 51_75 | 89 | 0 | 37 | 50 | 43.705m | 164.550m | 80.9% | 1 | 215 | 67.628m |
| WTA_CHALL | ge76 | 40 | 0 | 14 | 22 | 55.309m | 184.130m | 85.0% | 1 | 327 | 62.809m |
| WTA_MAIN | le25 | 60 | 2 | 32 | 39 | 23.972m | 233.116m | 100.0% | 1 | 1 | 23.972m |
| WTA_MAIN | 26_50 | 85 | 3 | 42 | 55 | 29.107m | 149.805m | 96.3% | 1 | 1 | 30.941m |
| WTA_MAIN | 51_75 | 87 | 3 | 67 | 72 | 5.445m | 94.648m | 97.6% | 1 | 1 | 6.586m |
| WTA_MAIN | ge76 | 50 | 1 | 31 | 39 | 8.586m | 122.483m | 100.0% | 1 | 1 | 8.586m |
| WTA_MAIN | UNAVAILABLE | 22 | 18 | 0 | 0 | — | — | 100.0% of the four printed legs | 1 | 1 | — |

The high one-print stability rate is not proof that the market's semantic shape is known. The k-means distance is heavily anchored by price region, and its band label can remain constant while signed travel becomes large. WTA_CHALL is the visible counterexample in the table: the median is still one print, but the p90 stability count ranges from 215 to 862 prints by region.

### NIKVRB

| Leg | Discovery (T−sched / T−bell) | First print (T−sched / T−bell) | Lag | Provisional band | Final band | Stable point |
|---|---|---|---:|---|---|---|
| NIK | 375.450 / 379.450 | 361.971 / 365.971 | 13.479m | ATP_CHALL-B1 | ATP_CHALL-B4 (`flat`) | print 38, T−80.651 / T−84.651; 294.799m after discovery |
| VRB | 375.450 / 379.450 | 316.064 / 320.064 | 59.386m | ATP_CHALL-B6 | ATP_CHALL-B6 (`flat`) | print 1, same timestamp |

NIK's first call was wrong. VRB had no print-derived shape for 59.386 minutes after discovery. Its first centroid call remained stable, but B6 still calls a path with final signed net `+13¢` flat; NIK's final B4 call labels `−14¢` flat. For this specimen, formal centroid stability is not semantic riser/faller understanding.

## 2. What is knowable before prints

Raw quote-only source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_shape_knowability_diagnostic_20260731/QUOTE_ONLY_PREPRINT_DIAGNOSTIC.json

The first 30-minute quote window preserves bid, ask, last traded, spread, ask dwell, quote cadence, and top-five depth as one observation stream. The diagnostic fingerprint uses only the existing anchor/net/dip bins applied to the ask path; no new threshold was fitted. A leave-one-event-out cell is callable only at the existing `n≥10` and `purity≥60%` bars. `Baseline` is the leave-one-event-out category+region majority band. These are development/backwalk descriptions, not validated predictive performance.

| Category | Region | Eligible n | Callable n | Quote-cell accuracy | Baseline | Lift |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | le25 | 130 | 97 | 98.97% | 86.15% | +12.82pp |
| ATP_CHALL | 26_50 | 247 | 242 | 70.66% | 70.45% | +0.22pp |
| ATP_CHALL | 51_75 | 237 | 12 | 100.00% | 56.54% | +43.46pp; 225 no-calls |
| ATP_CHALL | ge76 | 90 | 88 | 97.73% | 97.78% | −0.05pp |
| ATP_MAIN | le25 | 43 | 26 | 100.00% | 76.74% | +23.26pp |
| ATP_MAIN | 26_50 | 105 | 98 | 87.76% | 84.76% | +3.00pp |
| ATP_MAIN | 51_75 | 107 | 98 | 84.69% | 77.57% | +7.12pp |
| ATP_MAIN | ge76 | 25 | 25 | 100.00% | 100.00% | +0.00pp |
| WTA_CHALL | le25 | 45 | 41 | 87.80% | 86.67% | +1.14pp |
| WTA_CHALL | 26_50 | 94 | 89 | 71.91% | 69.15% | +2.76pp |
| WTA_CHALL | 51_75 | 89 | 85 | 71.76% | 69.66% | +2.10pp |
| WTA_CHALL | ge76 | 40 | 40 | 85.00% | 85.00% | +0.00pp |
| WTA_MAIN | le25 | 58 | 52 | 100.00% | 100.00% | +0.00pp |
| WTA_MAIN | 26_50 | 82 | 75 | 66.67% | 68.29% | −1.63pp |
| WTA_MAIN | 51_75 | 84 | 31 | 0.00% | 53.57% | −53.57pp; threshold-instability failure |
| WTA_MAIN | ge76 | 49 | 48 | 100.00% | 100.00% | +0.00pp |

There is quote information, but no general quote-shape result. Several cells merely reproduce a dominant anchor-region band; several add almost nothing; ATP_CHALL 51_75 is high accuracy on only 12 of 237 legs; WTA_MAIN 51_75 fails under leave-one-event-out thresholding. The raw file separately publishes cadence, spread, dwell, and top-five depth distributions by final band so none are hidden by the compact table.

For NIKVRB, both legs produce the same first-30-minute quote fingerprint, `a95|dn10|d10`. That exact ATP_CHALL/le25 cell is `n=16`: B1=5, B4=5, B6=6, purity 37.5%. It fails the frozen recognition bar. Quote behavior did not distinguish the two legs in this specification.

### What the existing corpus actually fits on quotes

- `band_taxonomy.py`: no quote inputs; k-means uses standardized traded-price `(anchor, net, dip)` only.
- `range_spectrum_build.py`: stores spread regime, wake time, and full bid/ask/last paths, but those fields do not enter band assignment.
- `drift_surfaces.py`: publishes bid/ask/traded movement after conditioning on the ex-post print-derived band; it is not a pre-print quote classifier.
- `window1_quote_reachability_census.py`: measures ask-side dwell floors and quote episodes; it does not assign a band.
- The down-and-resume census is quote-episode geometry, not a print-free shape taxonomy.

Therefore no already-bound executable organ classifies eventual shape from pre-print cadence, spread, dwell, or depth. The table above is the first descriptive recut, and it is unvalidated.

## 3. Whether the printed sibling constrains a silent leg

Raw sibling source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_shape_knowability_diagnostic_20260731/SIBLING_SILENT_LEG_DIAGNOSTIC.json

The diagnostic retains only cases where exactly one leg has a lawful print during the first 30 minutes after discovery. It asks whether that printed leg's provisional band describes the silent sibling's eventual band. It does not treat bid/ask prices as exact complements and does not invent simultaneous evidence.

| Category | Silent region | n | Callable | Sibling accuracy | Baseline | Lift/status |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | le25 | 25 | 24 | 95.83% | 92.00% | +3.83pp |
| ATP_CHALL | 26_50 | 74 | 74 | 87.84% | 64.86% | +22.97pp |
| ATP_CHALL | 51_75 | 23 | 15 | 100.00% | 65.22% | +34.78pp |
| ATP_CHALL | ge76 | 18 | 18 | 100.00% | 100.00% | +0.00pp |
| ATP_MAIN | le25 | 7 | 0 | — | 100.00% | THIN |
| ATP_MAIN | 26_50 | 25 | 21 | 100.00% | 84.00% | +16.00pp |
| ATP_MAIN | 51_75 | 10 | 0 | — | 70.00% | no callable cell |
| ATP_MAIN | ge76 | 1 | 0 | — | — | THIN |
| WTA_CHALL | le25 | 7 | 0 | — | 100.00% | THIN |
| WTA_CHALL | 26_50 | 21 | 19 | 73.68% | 66.67% | +7.02pp |
| WTA_CHALL | 51_75 | 6 | 0 | — | 66.67% | THIN |
| WTA_CHALL | ge76 | 7 | 0 | — | 100.00% | THIN |
| WTA_MAIN | le25 | 11 | 11 | 100.00% | 100.00% | +0.00pp |
| WTA_MAIN | 26_50 | 28 | 28 | 96.43% | 60.71% | +35.71pp |
| WTA_MAIN | 51_75 | 4 | 0 | — | 75.00% | THIN |
| WTA_MAIN | ge76 | 8 | 0 | — | 100.00% | THIN |

So the sibling is descriptively informative in some category+region cells, especially ATP_CHALL 26_50/51_75, ATP_MAIN 26_50, and WTA_MAIN 26_50. It is not universally informative and has not been validated outside this development/backwalk population.

NIKVRB is not evidence for a causal sibling rule. NIK printed once in the first 30 minutes and provisionally called B1 while VRB was silent; the exact 804 early-B1 → silent-B6 cell is `n=1`, therefore THIN. The older full-corpus final-band mirror contains favorite B6 / dog B1 `n=1,129`, but that is final-to-final hindsight, not an early-to-silent causal mapping. It cannot lawfully be promoted into an entry rule from this specimen.

## 4. LAJ, JIM, VED placement book state

Raw placement source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_shape_knowability_diagnostic_20260731/ANCHOR_PLACEMENT_DIAGNOSTIC.json

Bid, ask, last traded, spread, and ask dwell below are one contemporaneous guarded-cache observation. Times are `T−scheduled / T−frozen-bell`, in minutes.

| Leg | Time | Rule | Bid / ask / last / spread / ask dwell | Order before → after | One-cent gate |
|---|---|---|---|---|---|
| LAJ | 474.183 / 1794.183 | QUIET_BOOK_ANCHOR | 49 / 50 / 49 / 1 / 1,441s | ∅ → 49 | enforced |
| LAJ | 457.067 / 1777.067 | PER_TICK_ASK_BREATHING | 49 / 51 / 50 / 2 / 16s | 49 → 50 | not applicable; this is the fill-leading placement |
| VED | 479.850 / 529.850 | QUIET_BOOK_ANCHOR | 59 / 60 / 60 / 1 / 16,392s | ∅ → 59 | enforced |
| VED | 211.033 / 261.033 | PER_TICK_ASK_BREATHING | 60 / 61 / 60 / 1 / 5,247s | 59 → 60 | not applicable |
| VED | 179.517 / 229.517 | ORIENTATION_CONDITIONED_INITIAL_TREE | 60 / 61 / 61 / 1 / 5,247s | 60 → 60 | not applicable; fill-leading hold |
| JIM | 79.983 / 1659.983 | QUIET_BOOK_ANCHOR | 39 / 40 / 40 / 1 / 1,579s | ∅ → 39 | enforced; fill-leading placement |

The one-cent gate was enforced on every `QUIET_BOOK_ANCHOR` call. It did not govern later `PER_TICK_ASK_BREATHING` or orientation calls. LAJ's credited 50 originated from the breathing path at a two-cent spread, so the one-cent anchor gate did not protect that final placement.

## 5. BIG, VAN, BRA, KOR versus the lowest ask held ten seconds

The 10-second ask floor is ask-side only. It proves a Window-1 ask residency, not overlap with the final resting interval and not five-contract capacity.

| Leg | Resting history | Final rest | Lowest ask held ≥10s | Final rest − ask floor | Accounting |
|---|---|---:|---:|---:|---|
| BIG | 54 → 53 | 53 | 55 | −2¢ | NOT_FILLED |
| VAN | 49 → 49 → 50 | 50 | 50 | 0¢ | NOT_FILLED |
| BRA | 39 → 33 | 33 | 40 | −7¢ | NOT_FILLED |
| KOR | 59 → 60 → 57 | 57 | 60 | −3¢ | NOT_FILLED |

The exact action timestamps, both clocks, joint BBO/last observations, ask dwell, and source receipts for every resting transition are in the raw placement diagnostic.

## Containment

The 804 population was read only. No scoring, tuning, holdout, live, production, network, order, or position access occurred. The quiet-book anchor change remains held pending the operator's decision.
