# REGRESSION KNIFE + TWO-WAY-STREET ATTRIBUTION — @17ed8291

License: LAW_INDEX @ 17ed8291, sha256 41784e6a… · L8 L11 L18 L20 L22 · welds.
Seat: CC verification. Data: miss_census_20.json · miss_census_strat.json (in-file below).

## 1 — The ruling filed (F-VS-122, verbatim)

THE TWO-WAY STREET — "there are as many measurements to partial failure as there is to partial success… if the data isn't serving a conviction answer for the market that is in focus now that's 1 issue, OR the market we're in isn't making use of the data we have stored that would be able to contribute to a proper trade."
Attribution classes: **DATA-GAP** (no store could serve it) · **DATA-UNCONSUMED** (serving store + rows named — it existed, unconsulted or unweighted) · **MISREAD** (consumed, arithmetic step named). Unattributed misses are unfinished forensics.

## 2 — Verification

| item | verdict |
|---|---|
| −20 bias table | RE-GRADED IN FULL against TARGET_PRINTS_5: 3,173 graded / 56 hits vs receipt 3,179/59 (6 boundary ties, 2 realized-low ties); **median −20 CONFIRMED**. The gate's own `moved_toward_zero: false` and `named_step_failures` are honest. Note: PAL supplies 2,826 of 3,173 graded rows — the −20 headline is PAL's median; per leg BAR −3, PRA −5, LAJ −5, URS −5, GIU −7, DAN −16, SVA −18, PAL −20 |
| Re-arm | latency receipt `every_qualified_action_same_receipt: true`; atomic rows 861 replacements + 4 fail-loud; per-leg latency 0 on all four legs that placed (PAL/URS/DAN/PRA) — **and `latency_seconds: null` on BAR/GIU/LAJ/SVA because those legs never placed at all this build** (fill_count 0). "permanent_silence: 0" is true only in the sense that no leg was cancelled-and-abandoned; four legs were silent from the start |
| DANPRA stamp | F-VS-121 HONORED, not closed: LAWFUL_INCOMPLETE_RECEIPT now carries the arithmetic proof (`59+41=100; max(0,99-100)=0`, truth receipt cited) but stamps **UNSTAMPED_INCOMPLETE** with `rest_at_floor_proven: false` — and all four games carry the same unstamped verdict with `unstamped_abstention_scores_zero: true`. Correct and honest: no rest stood at any floor, so no abstain can be proven |
| Determinism | 2 runs, same frozen inputs, same policy bytes, outcome vectors equal, PASS |
| Custody | 3/3 externally custodied artifacts present on disk with matching bytes and sha256 (ATOMIC_REARM 114,592,405 / 40f5c7ff…; ENVELOPE_PLACEMENT 89,204,403 / 0f5633ff…; TRACE 157,545,252 / e2e0b367…) |

## 3 — A-term autopsy, with attribution

**Ordered**: expected future low = causal own seen low + conditioned expected (strict-future-low − seen-low) **at the same window phase**.
**Implemented**: the same shape, but the served A-term is a deep-tail draw, not the conditioned central estimate.

The library's own population (63,260 phase-labelled path points, its own bytes):

| window phase | n | q25 | **q50** | q75 |
|---|---:|---:|---:|---:|
| 0.0–0.1 | 18,945 | −11 | **−4** | 0 |
| 0.1–0.3 | 3,767 | −8 | **−3** | +1 |
| 0.3–0.5 | 2,948 | −6 | **−2** | +1 |
| 0.5–0.7 | 2,870 | −6 | **−1** | +2 |
| 0.7–0.9 | 5,543 | −8 | **0** | +3 |
| 0.9–1.0 | 29,187 | −1 | **+4** | +11 |
| ALL | 63,260 | −6 | **0** | +5 |

Served A-term (prediction − own low), and its empirical quantile rank inside its own phase×category population:

| leg | served median | rank |
|---|---:|---:|
| PAL | −17 | **0.085** |
| SVA | −14 | 0.123 |
| GIU | −10 | 0.162 |
| LAJ | −10 | 0.173 |
| PRA | −12 | 0.199 |
| DAN | −2 | 0.373 |
| BAR | −2 | 0.434 |
| URS | −1 | 0.473 |
| ALL | — | **0.105** |

**The exact step producing −20**: the seven-member own-tape-weighted estimate lands at the **10th percentile** of the conditioned distribution the store actually holds, and that tail value is then subtracted from the seen low as if it were the central expectation. Counterfactual on the same rows, same store, same phase+category conditioning, central estimate instead of the tail: **bias −20 → −4, hits 59/3,179 (1.9%) → 3,028/3,179 (95.3%)**.

Three legs vs the same stages @46b35969 (matched by receipt epoch):

| leg | matched stages | @46b35969 delta / err / hits | @17ed8291 delta / err / hits |
|---|---:|---|---|
| PAL | 2,739 | 0 / −3 / 332 | −17 / −20 / **0** |
| GIU | 48 | 0 / +3 / 42 | −10 / −7 / **0** |
| LAJ | 68 | 0 / +3 / 50 | −10 / −5 / 14 |

The prior build predicted the seen low itself (delta 0) and hit; this build subtracts a tail draw and stops hitting. Example, PAL first matched stage 1784004251: own low 37 in both; prediction **37 → 5**; realized 39.

**VERDICT — MISREAD.** The store was consulted, its rows are named in every sentence, and it contains the correct central estimate; the arithmetic step named above converts it into a tail. Not a data gap: the conditioned distribution's median at every phase is within a few cents of truth.

## 4 — The LAJ exhibit, with attribution

The [62,62] exhibit **does not reproduce at @17ed8291** — the A-term repair flipped its sign. Same stage (1784059613, receipt LAJ.csv.gz#row-6963), truth floor 51 @1784060123.2:

| build | floor-moment belief | vs truth |
|---|---|---|
| @46b35969 | envelope [62,62], rest None | **11¢ above** |
| @17ed8291 | predicted 48, envelope null, rest None, live bid **51**, ask 54, reader 54, own low 53 | **3¢ below** |

Does any store hold evidence licensing ~51, consulted properly? **Yes — two, and neither is a gap:**
1. **The future-low library itself** (consulted; its rows cited in the sentence): at LAJ's phase 0.735 the conditioned population is n=2,094, q25 −6, **q50 0**, q75 +3. Central estimate ⇒ prediction = own low 53 + 0 = **53**, which is ≥ the realized 51 — it hits, and a rest at 53 is exactly the certified baseline's LAJ 53 capture. The build served −5 (rank 0.173) ⇒ 48. → **MISREAD**.
2. **The leg's own live touch at that receipt**: bid = **51** = the floor, in the belief inputs, on the cited book row. Nothing needed inferring — the floor was the touch. It was not placed because the envelope was null / coherence absent at that stage. → **DATA-UNCONSUMED** (store and row named: LAJSVA-LAJ.csv.gz#row-6963, `live_bid_cents: 51`).
3. The V3 cell consulted (ATP_CHALL|51, n=78, edge_p50 7) points to 44 — deeper than the floor; it is the one consulted store that does not license 51.

Street named: **not a data gap on either side.** The conviction answer existed in the served store (central estimate 53) and in the live book (51); the market-side failure is that the engine consumed the store at its tail and left the touch unused.

## 5 — Miss census seed (first measured split)

Rule (reproducible): for a graded miss (realized low > prediction), let *needed delta* = realized − own low. If the phase×category **median** delta would have reached it → MISREAD. Else if any value in that conditioned population reaches it → DATA-UNCONSUMED. Else → DATA-GAP.

- **Sha256-drawn 20 of 3,120 graded misses**: **MISREAD 9 · DATA-UNCONSUMED 11 · DATA-GAP 0**. (Sample is PAL-heavy — PAL is 2,826 of 3,120 misses.)
- **Stratified, 3 per leg (24)**: **MISREAD 11 · DATA-UNCONSUMED 13 · DATA-GAP 0**.

Both draws: **zero DATA-GAP**. Every sampled failure is a consumption or weighting failure against stores we already hold — the second half of the operator's street, not the first.
