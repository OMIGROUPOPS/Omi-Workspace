# CLOCK CROSS-CALIBRATION CENSUS — BOARD −1b1 (2026-07-10, read-only; artifacts: /tmp/census_out.json → `.claude/census_20260710/census_out.json`, script `census_script.py`)

## Overlap windows, stated explicitly
The archive file (`data/match_facts_v3.csv`, 2,714 matches) covers **2026-03-20 → 2026-04-10** and shares **zero matches** with the live sources (gun era Jul 8+, TE bank Jul 6+). Therefore the census cross-calibrates the **DETECTOR**, not the file: the mid-jump detector (JUMP_CENTS=3, JUMP_WINDOW_SEC=30, SUSTAIN_WINDOWS=2, re-implemented on a 30s grid from `build_match_facts_v3.py`) was re-run on live-era `analysis/premarket_ticks/` for every Jul-08→10 event carrying a gun fire or TE row. Counts: **257 gun events · 223 mid-jump detections · 33 TE joins (both-leg matcher) · 842 our-fill events (contamination flag = entry_filled since Jul 6)**.

## Part 1 — pairwise deltas per category (minutes; Δ = first source − second; category law: no aggregate)

### mid-jump vs gun (the load-bearing table, n=219)
| cat | split | n | med | p10 | p90 | ±5 | ±15 | ±30 |
|---|---|---|---|---|---|---|---|---|
| ATP_CHALL | all | 40 | **−0.6** | −17.0 | +55.8 | 35% | 53% | **68%** |
| ATP_CHALL | ours | 27 | +0.5 | −2.6 | +55.8 | 44% | 59% | 67% |
| ATP_CHALL | clean | 13 | −12.8 | −20.8 | +54.1 | 15% | 39% | 69% |
| ITF_M | all | 91 | **−119.2** | −811.7 | −10.7 | 1% | 6% | **8%** |
| ITF_M | ours | 64 | −118.5 | −811.7 | −37.5 | 0% | 5% | 5% |
| ITF_M | clean | 27 | −185.6 | −834.2 | +7.9 | 4% | 7% | 15% |
| ITF_W | all | 67 | **−118.1** | −796.0 | +0.3 | 4% | 13% | **18%** |
| ITF_W | ours | 52 | −120.2 | −805.0 | −5.3 | 6% | 17% | 19% |
| ITF_W | clean | 15 | −73.2 | −700.4 | +710.9 | 0% | 0% | 13% |
| WTA_CHALL | all | 19 | +10.2 | −32.3 | +740.3 | 21% | 53% | 58% |
| WTA_MAIN | all | 2 | +35.0 | — | — | — | — | (unevaluable n) |

### vs TE (both tables): **n too small to certify anything** — TE joins 33, per-cat overlap 1–7; deltas scattered to ±1,000+ min. The one clean signal: gun_vs_te ATP_CHALL clean 2/2 within ±5 min. TE coverage, not agreement, is the binding constraint.

## Part 2 — the fallback tail, counted (archive file; `pregame_detection_method`)
| cat | jump | fallback (80%-of-lifetime class) | **no_bbo_data (NO clock)** | fallback share | no-clock share |
|---|---|---|---|---|---|
| ATP_CHALL | 1,387 | 31 | 314 | 1.8% | **18.1%** |
| ATP_MAIN | 388 | 22 | 46 | 4.8% | 10.1% |
| WTA_CHALL | 117 | 5 | 40 | 3.0% | **24.7%** |
| WTA_MAIN | 302 | 18 | 44 | 4.9% | 12.1% |
| **ITF_M / ITF_W** | **0** | **0** | **0** | — | **ABSENT: the archive has no ITF rows at all** |

Clustering: fallback matches are **thin books** — median volume 119k vs 274k for jump-method (p10 17k vs 49k). The weak clocks cluster exactly where clocks are hardest.

## Part 3 — self-contamination: **REFUTED as the explanation**
If our fills corrupted the tape clock, clean books would agree better than ours. The data says the opposite or no difference: ATP_CHALL **clean is WORSE** (med −12.8 vs ours +0.5; ±5 15% vs 44%); ITF ours/clean are equally broken (−118 vs −186 med). This morning's scorecard suspect wall is **not self-inflicted** — it is structural: thin-book premarket repricing satisfies flow/jump conventions long before the match (the mid-jump p10 of −800 min = the detector firing on premarket churn 13 hours early).

## Caveats, named
(1) Live `premarket_ticks` coverage begins at bot subscription (up to T−8h since the unlock) — broader premarket exposure than the April `bbo_log_v4` window, so premature-fire RATES may differ by era; the mechanism finding (mid-jump fires on thin-book premarket repricing) stands regardless. (2) The detector is a faithful 30s-grid re-implementation, not the original binary. (3) Gun timestamps are the fused gun's — itself pending certification (bar unchanged; this census is calibration context, not certification).

## Part 4 — VERDICT (one paragraph)
**No global re-stamp — a scoped exclusion instead, and one hard prohibition.** (i) **ITF: the archive carries no clock at all** (categories absent from match_facts_v3), and the census proves the mid-jump detector is structurally unfit for thin ITF books (median −2h, p10 −13h vs the gun) — so the OS's historical layer must treat **live-era data (gun/tape, Jul 8+) as the ONLY admissible ITF clock**; any ITF T-relative fitting on archive-era assumptions is prohibited, and nothing exists to re-stamp. (ii) **CHALL, jump-method slice: trust at ±30 min tolerance** (ATP_CHALL med −0.6 min, 68% within ±30 vs the gun) — usable for coarse T-relative ranges, not for timing triggers (GRANULARITY LAW already binds). (iii) **Exclude, do not re-stamp, the weak slices**: fallback_no_jump (76 matches) and no_bbo_data (444 matches, 10–25% per cat) carry no honest clock and no data to re-derive one — the OS rulebook must drop them from any T-relative fit. (iv) **Mains stay convicted** (CLOCK_AUDIT; census n=2 adds nothing). (v) Self-contamination is refuted as the suspect-wall cause — the CERT-NIGHT-3 forensic should look at slate/source starvation, not our own fills. Feeds PLEX_REANCHOR (slot open) + the aim-surface refit: the refit may use CHALL-jump archive slices at ±30m tolerance and must source ITF exclusively from the live era.
