# OMQS — WEEK-VALIDATION GATE: monotonic in-match downside-cut (Jun 24–30)

Source: Kalshi REST (settlements/fills) + /markets/trades tick-tape (800 tickers, ~1.44M trades), 710 settled filled legs Jun 24–30 (170 losers, −$990.67). Gun = tape volume-onset (sustained ≥5 trades/min — i.e. the future `gun_detected_for_cut` predicate). Rule: cut at `fill−10¢` if, in the first N min after the gun, the leg falls to fill−10 **without ever printing above fill** (past-only, no look-ahead). MEASUREMENT ONLY — no code/cancel touched. Bisect (restart 15:46:04 ET) untouched.

---

## GATE (a) — total NET positive across the full week ✓ PASS

Per-day NET$ (X=10¢) at each N:
| date | n | day loss$ | N=15 | N=30 | N=45 | N=60 |
|---|---:|---:|---:|---:|---:|---:|
| 2026-06-24 | 153 | −466 | +16.77 | +25.93 | +26.98 | +29.30 |
| 2026-06-25 | 32 | −137 | +76.56 | +75.09 | +77.32 | +77.32 |
| 2026-06-26 | 26 | −78 | −0.07 | +2.01 | +2.01 | +2.01 |
| 2026-06-27 | 44 | −10 | −2.40 | +1.80 | +3.20 | +4.65 |
| 2026-06-28 | 96 | −30 | +1.05 | +1.10 | +1.10 | +4.90 |
| 2026-06-29 | 254 | −223 | +97.68 | +98.91 | +19.12 | +17.42 |
| 2026-06-30 | 105 | −46 | +7.42 | +9.38 | +13.02 | +14.65 |
| **WEEK TOTAL** | 710 | | **+197.01** | **+214.22** | **+142.76** | **+150.25** |

**Jun 24–29 held-out (excludes today): N=30 → +$204.84** (fires 92). **Positive on every single day at N=30** (worst day Jun 28 +$1.10). The +$26 is NOT today-specific — today is only +$9.38 of the +$214 week total; Jun 24 (+$26) and Jun 29 (+$99) carry it. **PASS.**

## GATE (b) — N-window robustness ✓ PASS (with a known shape)

Jun 24–29 NET by N: **N=15 +$189.59 · N=30 +$204.84 (peak) · N=45 +$129.74 · N=60 +$135.60.**
- **Positive across the entire N=15–60 range ($130–205)** — no N makes it negative, so it is not a knife-edge operating point.
- Plateau at **N=15–30** (+$190–205); peak N=30. N=45/60 weaker because a longer monotonic window disqualifies legs that have a **late dead-cat bounce** (a loser that bounces above fill at min ~35 but still rides to 0 is excluded at N=45, so its save is missed — most visible Jun 29: +$99 at N=30 → +$19 at N=45). The signal lives in the first 15–30 min post-gun. **N=30 is robust, not fragile.**

---

## WARNING 1 (Plex) — CONFIRMED and DOMINANT: this is a SUBSET fix

Of the 170 week losers (−$990.67):
| class | legs | loss |
|---|---:|---:|
| **MONOTONIC** (never printed above fill post-gun — cuttable) | 69 | −$236.74 |
| **ERHROD-class** (peaked ABOVE fill, then reversed, rode to 0 — **UNCUT**) | 95 | **−$648.06** |
| no gun | 6 | — |

**The monotonic cut addresses the 35%-of-loss slice (−$237) and nets +$205 by cutting it at −10¢. The ERHROD-class peak-then-reverse — 65% of the loss (−$648) — remains entirely UNCUT.** (ERHROD: entry 70, peaked 84 = +14 above fill, reversed, rode to 0 — the §5 two-trade-proof canonical bleed; the monotonic filter never fires on it.) **The cut is +EV on its slice; it does NOT close §4.** The peak-then-reverse residual is the next §4 iteration (post-peak-monotonic-down / reversal-magnitude discriminator).

## WARNING 2 (Plex) — locked for the build (NOT executed here)

The validation used a tape-onset gun predicate. The build MUST introduce a NEW `gun_detected_for_cut` (tape-onset, trades_in_window ≥ N from /markets/trades) that drives ONLY the cut window. **Do NOT fix `match_live_detected`** — that moves the stale-buffer cancel from too-early (protective, M2) to on-time, re-opening the −$25 entry-fill loss that nets the +$26 cut to +$1. Two signals, two uses, decoupled. The cancel path stays untouched. (No code was modified in this measurement.)

---

## GATE VERDICT: PASS

NET positive across the week (+$205 held-out, +$214 full), positive every day at N=30, robust across N=15–60. The monotonic in-match cut is a real +EV rule — **on the monotonic slice (35% of the loss).** Proceed to the decoupled build (Plex sequence step 2: two-signal architecture, `gun_detected_for_cut` new, cancel untouched), with Warning 1 explicit: this is a partial §4 fix; the −$648 peak-then-reverse class is the larger, still-open problem.
