# OMQS — P1: TRUE-TAPE-ONSET RE-ANCHOR (2026-07-01, Plex precondition)

**Question:** is the scheduled-start clock (which contaminates every tts@fill downstream, §0A) a constant offset from true tape activity (→ surfaces can SHIFT) or wide/multimodal (→ surfaces need RE-DERIVATION)?

## Onset definitions (stated per Plex)
Two computed, both = the start of the first run of **≥5 consecutive active minutes** on the L1 recorder:
- **ONSET-Q** (operator's literal spec): a minute is active if **two-sided book present** (≥60% of ticks bid>0 & ask>0) **AND quote-update rate ≥ 3/min AND median spread ≤ 10¢**.
- **ONSET-T** (trade-burst / match-live proxy): a minute is active if **≥3 trades** (last_trade changes) printed.

## Offset distribution (tape-onset − scheduled start, minutes; + = onset AFTER sched)
15 stratified events, Jun 24 (3 each: ATP_MAIN, WTA_MAIN, ATP_CHALL, ITF_M, ITF_W):
| definition | n | median | IQR | range | **>15min tails** |
|---|--:|--:|--:|--:|--:|
| **ONSET-Q** | 15 | **+24 min** | [+8, +53] | −168 … +105 | **10/15 = 67%** |
| **ONSET-T** | 7 | **+81 min** | [+13, +98] | +9 … +159 | 5/7 = 71% |

(ITF often had no detectable trade-burst → ONSET-T n/a for 8/15 — thin markets never sustain a trade regime.)

## Decision — RE-DERIVATION required (NOT a shift)
The offset is **not tight and not unimodal:** median +24 min, IQR spanning +8 to +53, a −168 min outlier (an ITF market active 2.8 h *before* its scheduled start), and **67% of events beyond ±15 min.** Per Plex's criterion (`mode <±5min tight → shift; wide/multimodal >15min tails → re-derive`), this is unambiguously the **RE-DERIVATION branch.**

**Consequences:**
- The scheduled-start clock is a **wide, multimodal, heavy-tailed error**, not a constant — so dip_timing / dip_surface / W1-corridor-W2 boundaries indexed to scheduled start are **non-uniformly contaminated** and cannot be fixed by a constant shift.
- **The surfaces must be rebuilt on tape-relative time** (onset-anchored). ITF is worst (schedule least reliable; no trade-burst signal at all).
- **Job-2 (ii) window-reachability is BLOCKED** until this re-derivation lands.

Method: `p1.py`. Scheduled starts from `schedule_match` log events (1,950 events); L1 tape `analysis/premarket_ticks`.
