# OMQS — P3a: WINDOW-MAP RE-DERIVATION, tier-partitioned (2026-07-01)

**Task:** re-derive W1/corridor/W2 per event on TRUE tape time (ONSET-Q from P1), tier-partitioned; report ATP_MAIN offset SEPARATELY from ITF; flag the ITF W1-extension class. Current defs (`OMQS_WINDOW_MAP`): **W1 = fill→scheduled_start, CORRIDOR = scheduled→gun, W2 = gun→settle** — W1's boundary is the stale scheduled clock.

Re-anchor: **W1_start = ONSET-Q** (market activation), **W2_start (gun) = ONSET-T** (match-live burst), **corridor = [gun−20m, gun]**. Per-event table: `window_boundaries_reanchored.csv` (n=134). Sample: 30/cat, paired + scheduled + tape-covered.

## Per-tier ONSET-Q offset vs scheduled start (min; + = onset AFTER sched)
| tier | n | median | IQR | range | >15min tails |
|---|--:|--:|--:|--:|--:|
| ATP_MAIN | 28 | **+54** | [+10, +122] | −1711 … +225 | 64% |
| WTA_MAIN | 30 | +98 | [+10, +120] | −1022 … +205 | 77% |
| ATP_CHALL | 22 | +34 | [+11, +118] | −877 … +1140 | 82% |
| ITF_M | 26 | +55 | [+16, +93] | −168 … +177 | 88% |
| ITF_W | 28 | +40 | [+10, +90] | −556 … +115 | 86% |
| **MAIN pooled** | 80 | **+62** | — | — | **74%** |
| **ITF pooled** | 54 | **+49** | — | — | **87%** |

**⚠ HONEST CORRECTION — ATP_MAIN is NOT tighter than ITF.** The hypothesis ("the +24min P1 median is ITF-inflated; main may be tighter") is **not supported at n=134**: MAIN median offset is **+62 min vs ITF +49 min** — main is *comparably wide or wider*. The P1 +24min (n=15) was small-sample. Both tiers are wide and heavy-tailed (74-87% beyond ±15 min), with large outliers (an ATP_MAIN event active 28 h before its scheduled start = a scheduled-start data-quality artifact). **Re-derivation is required in EVERY tier; there is no clean "main" tier to shortcut.**

## W1 re-anchor classification (EXTEND = market active before old sched−4h lookback)
| tier | EXTEND | trim | W2-undetectable (no trade-burst) | n |
|---|--:|--:|--:|--:|
| ATP_MAIN | 3 | 25 | 6 | 30 |
| WTA_MAIN | 1 | 29 | 8 | 30 |
| ATP_CHALL | 3 | 19 | 3 | 30 |
| ITF_M | 0 | 26 | **18 (60%)** | 30 |
| ITF_W | 3 | 25 | **15 (50%)** | 30 |

- **Dominant re-anchor move is TRIM, not EXTEND.** In 24-29/30 events per tier the market activates *later* than sched−4h, so the old W1 includes dead pre-activation lead that must be trimmed. The **EXTEND class (the −168min "ITF W1 must cover tape-onset" case) is REAL but RARE** (0-3/tier, driven by the early-active outliers). So W1 re-anchoring both trims (common) and extends (rare) — anchoring on ONSET-Q handles both.
- **⚠ ITF W2/gun is UNDETECTABLE 50-60% of the time** (no sustained trade-burst — thin markets never fire ONSET-T). So for half of ITF events the corridor/W2 boundary **cannot be tape-derived.** ITF's W1 is anchorable (ONSET-Q), but its gun/W2 is not — the ITF shadow can rest on re-anchored W1 but its in-match window remains unanchored for ~half the tier. Main is far better (10-27% undetectable).

## Unblocks / gates
- **Job-2 (ii) window-reachability** can now be scored on tape-relative W1 for the events with detectable boundaries (per-event CSV).
- **ITF-simultaneous shadow (P4):** licensed on re-anchored **W1** (ONSET-Q), but must treat the **W2/gun as undetectable for ~50-60% of ITF** — either fall back or restrict the shadow's in-match logic to the detectable subset. Flag to Plex.

Method: `p3a.py`; boundary table `window_boundaries_reanchored.csv`.
