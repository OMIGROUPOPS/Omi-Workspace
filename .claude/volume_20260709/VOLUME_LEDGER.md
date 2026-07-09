# VOLUME LEDGER + FLOW CALIBRATION — findings (2026-07-09 ~1:05 am ET; read-only corpus, 2,448 pairs)

**Findings only. The gauge threshold change ships as its own gated config deploy after operator read** (granularity law: the macro corpus fits, the micro instrument reads). Raw: `aggregate.json`, `recut_cells_volume.json`, `volume_ledger.py`; per-pair rows on the VPS (`/root/volume_ledger_20260709/`). Forward field live since the 12:36 am boot (`gun_fired.vol_prints_30m`; scorecard column wired).

## PART 1 — THE LEDGER
- **Per-match W1 traded volume (contracts, both legs), med per cat:** ITF_M 5,961 · ITF_W 6,252 · ATP_CHALL 5,907 · WTA_CHALL 4,033 · ATP_MAIN 11,176 · WTA_MAIN 9,425 (p10–p90 spans ~1k–47k — volume is a per-match variable, never a cat constant).
- **recut_cells volume augmentation:** every one of the 538 cell rows now carries `vol_w1_med` + `thin_tape` (med W1 vol < 200 contracts); **only 2/538 cells flag thin** — the corpus edges are NOT thin-tape artifacts at the cell level (the FERCER-class contamination lives in per-match tails, which the per-row vol column now exposes at refit). Consumers wired: gun scorecard vol30@fire column (live), nightly per-cat W1-volume trend (rides the scorecard cron).

## PART 2a — FILL RATE | VOLUME (P(a print ≥3¢ below current fillable arrives within 30 min), per cat × cell-zone × trailing-30m print band)

| cat | zone | V1 (1-5 prints/30m) | V2 (6-15) | V3 (16+) |
|---|---|---|---|---|
| ITF_M | <50 | 16.1% | 30.8% | **50.0%** |
| ITF_M | 50-74 | 13.8% | 25.6% | 36.3% |
| ITF_M | 75-94 | 12.5% | 20.6% | 28.5% |
| ITF_W | <50 | 14.2% | 26.5% | **45.5%** |
| ITF_W | 50-74 | 9.2% | 21.5% | 34.7% |
| ITF_W | 75-94 | 11.4% | 19.3% | 31.8% |
| ATP_CHALL | <50 | 5.6% | 11.9% | 30.5% |
| ATP_CHALL | 50-74 | 4.4% | 6.7% | 16.6% |
| ATP_CHALL | 75-94 | 5.9% | 12.2% | 23.3% |
| WTA_CHALL | (all zones, n small) | 3-9% | 9-15% | 11-48% |
| ATP_MAIN | ALL zones | **1.0–1.5%** | **0.4–1.0%** | **0.2–1.4%** |
| WTA_MAIN | ALL zones | 0.3–1.5% | 0.4–2.0% | 1.8–2.6% |

- **Does a dead book EVER pay a patient bid? NO, structurally:** at V0 (zero prints in 30 min) there is no fillable reference at all under the prints convention — the event cannot occur without the book first WAKING; V0 rows are empty by construction and the spread table shows what V0 is (6¢ opinions, below).
- **The inflection: fill probability ~doubles per volume band in ITF** (16→31→50% in the <50 zone) — participation is the fill machine. CHALL inflects late (real probability only at V3). **MAINS: FLAT ~1% at EVERY volume state — volume does not open mains; the par-lock is participation-independent.** The cleanest hypothesis kill of the pass.

## PART 2b — SPREAD STUBBORNNESS (fav-leg lattice vs prints/min; P(tighten ≥2¢ in 15 min) + median spread)

| cat | V0 dead | V1 | V2 | V3 |
|---|---|---|---|---|
| ITF_M | 6¢ / 20.3% | 4¢ / 21.6% | 3¢ / 32.0% | **2¢ / 35.5%** |
| ITF_W | 6¢ / 20.5% | 4¢ / 21.9% | 3¢ / 29.6% | **2¢ / 33.6%** |
| ATP_CHALL | 2¢ / 3.5% | 2¢ / 3.5% | 2¢ / 7.8% | 1¢ / 12.7% |
| WTA_CHALL | 2¢ / 1.0% | 2¢ / 2.5% | 1¢ / 3.8% | 1¢ / 8.4% |
| mains | 1¢ / <1% | 1¢ / <1% | 1¢ / <1% | 1¢ / ~1% |

**Dead-book quotes are opinions, confirmed with numbers:** the ITF V0 lattice sits 6¢ wide and tightens only ~20% of the time in 15 minutes; convergence is monotone with participation (6→4→3→2¢). CHALL is pre-converged at 2¢ (its stubbornness is priced-ness, not width); mains never had anything to converge.

## THE DELIVERABLE — QUIET/WAKING/OPEN as FILL-PROBABILITY states (per cat; proposed, ships only on operator read)

| cat | QUIET (fill ≈ 0) | WAKING | OPEN |
|---|---|---|---|
| ITF_M / ITF_W | 0 prints/30m (no fillable reference; 6¢ opinion lattice) | **1–5 prints/30m** (fill 9–16%, spread 4¢) | **≥6 prints/30m (≥0.2/min)**: fill 20–50%, spread ≤3¢; ≥16/30m = deep-open (29–50%) |
| ATP_CHALL / WTA_CHALL | ≤5 prints/30m (fill 3–6% — CHALL's quiet extends into V1) | 6–15/30m (fill 7–12%) | **≥16 prints/30m (≥0.53/min)**: fill 17–30% |
| mains | ALWAYS (fill ~1% at any volume) | — | **never — the gauge stays OFF for mains** (EARLY_CANVAS exclusion confirmed on fill probability itself) |

**Calibration note vs the provisional thresholds:** EARLY_CANVAS's provisional WAKING ≥0.2 prints/min is, on fill probability, actually the ITF **OPEN** line (fill crosses ~21–31% there); its provisional OPEN 0.4–0.6/min is deep-open. The re-fit shifts the state boundaries DOWN for ITF and UP for CHALL — exactly what "fitted, not decreed" was for. Findings only; the config deploy waits on the operator.
