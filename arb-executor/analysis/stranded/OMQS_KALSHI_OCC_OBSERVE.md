# OMQS — C-KALSHI-OCC OBSERVE (read-only) — 2026-07-02

**What & why.** The gated coarse-start fallback already coded in `live_v4.py` (`[C-KALSHI-OCC]`): when ESPN + Odds-API can't resolve a Kalshi event, use Kalshi's own `occurrence_datetime` as a **coarse** schedule; the tape volume-burst latch still finds the real start; the coarse clock never gates entry (wide envelope, +90 min tail). Config-gated `kalshi_occurrence_fallback`, **default-OFF**.

**Arming decision.** The flag's only arm is a **live-entry** arm (no observe-only form), and the bot is holding/exiting live positions. Per the operator's "**do NOT let it place orders this session**," the flag was **NOT flipped** and the bot was **NOT restarted**. Instead this is a **read-only observe measurement** (`kalshi_occ_observe.py`) of exactly what the fallback *would* resolve, plus the never-touched census. Box = Jun 30 15:46 → now. Bot untouched (PID 501822).

## (a) Resolvability — schedule_gap events the occ-fallback would resolve
| | count | by category |
|---|--:|---|
| schedule_gap events (never posted) | **82** | — |
| **→ book-bearing (Kalshi listed + real tape ⇒ occ-resolvable)** | **57** | **ITF_W 33 · ITF_M 18 · ATP_CHALL 6** |
| → thin/phantom (no real book ⇒ correctly excused) | 25 | — |
| historically occ-resolved live | **0** | confirms the flag was OFF the whole box |

The occ-fallback would give **57** currently-hard-skipped events a coarse start (the tape latch then finds the true start). Resolvability proxy = Kalshi listed the market with a substantial recorded tape (≥200 KB) — which is precisely the `occurrence_datetime`-bearing condition the fallback reads. The `_kalshi_occ_start` guard (real-future only, ≤36 h) would additionally drop any whose occurrence was stale/past at decision time — not separable from the historical tape here; a forward armed-observe run would log it per-event.

## (b) Loop-lag + the removable schedule_gap load
- **loop_lag (current):** 21,568 samples · mean **1.91 s** · p50 1.64 s · p95 **4.26 s** · **max 19.16 s** · lags >5 s: 577 · >2 s: 8,084.
- **schedule_gap skip-logs (current): 122,280.**
- **The 57 occ-resolvable events account for 112,591 = 92 % of all the gap-spam.**
- **BEFORE:** 82 unmatched events re-scanned every ~1 s loop → 122 k skip-logs, dragging the loop (max 19 s).
- **AFTER (estimate):** 57 resolve off the coarse clock → their per-cycle re-eval + **92 % of the skip-spam drop out** → the lag tail shrinks. Exact after-lag needs the armed observe run (deferred per HOLD). Direction is unambiguous: the schedule_gap storm *is* the loop-lag driver, and 92 % of it is removable.

## (c) Byte-identical on already-resolved events — code-gate proof
**1,027** events resolved via a real source (ESPN/TE / `odds_api_commence_time`) this box. In `live_v4.py` the occ-fallback is **"Fallback 2" inside the `else` reached ONLY when the primary sources miss**; a resolved event takes the `odds_api_commence_time` `schedule_match` branch *above* it and never enters the else. Inside the else, `kts = _kalshi_occ_start(...) if getattr(self,"kalshi_occurrence_fallback",False) else None` — **the flag is consulted only on a primary-miss.** Therefore for every resolved event the flag on/off code path is **byte-identical** (the branch is never taken). ⚠ 11 of the 57 book_gap events *also* eventually resolved via a primary source (gap-skipped early, resolved late) — for those the occ-fallback would only have helped in the **pre-resolution window**; they are not double-counted as pure occ wins.

## CENSUS — what the never-touched slate offered (the headline)
Book-bearing schedule_gap-skipped events, by tier, with **achievable combined** = sum of each leg's best-fillable (size-backed) price — the pair we could have locked and **never looked at**:

| tier | n | w/ combined | **≤97** | <100 | median achievable |
|---|--:|--:|--:|--:|--:|
| ATP_CHALL | 6 | 6 | **6** | 6 | 60 |
| ITF_M | 18 | 15 | **14** | 14 | 76 |
| ITF_W | 33 | 30 | **28** | 28 | 76 |
| **TOTAL** | **57** | **51** | **48** | **48** | **72** |

**48 of 51 (94 %) computable book-bearing skipped events offered an achievable combined ≤97 — median 72.** These are the deep sub-par pairs the entire operation is chasing (Vault §0A: "fill both sides at combined ≤97"), **forfeited entirely because schedule_gap skipped the event.** This is the single largest pool of un-captured ≤97 entries surfaced to date, and it argues directly for arming C-KALSHI-OCC (in a true observe form / on the next slate, operator's call).

**Top forfeited (lowest achievable combined, never touched):** KHODEL (ITF_M) 19+1=**20** · KOBMAX (ITF_W) 8+13=**21** · WOLHAR (ATP_CHALL) 8+14=**22** · DUPPOP (ITF_W) 3+21=**24** · SCOBRO 29 · MAXNGO 33 · KALMAX/WALFER 34 · DEKFIT 35 · … through LIUJOH 62 / WATTUN 65.

⚠ **Caveat (same as the grade card):** the extreme-low combineds (<30: KHODEL 20, KOBMAX 21, WOLHAR 22) lean on a single size-backed low print and are partly the depth-recorder low-print artifact — a lopsided-favorite dog at 1–3 ¢ may not have offered a real 5-lot. The **robust** signal is the aggregate (48/51 ≤97, median 72) and the mid-range names (48–65), which are far less artifact-prone. Even discounting the sub-30 tail, the never-touched slate was rich with genuine sub-97 pairs.

## HOLD
Per the operator: reports delivered, **no further fixes** until the operator sees the error ledger (ITEM 2) and this. Nothing armed, nothing restarted, bot untouched. Artifacts: `kalshi_occ_observe.py`, `occ_observe_output.txt`, `OMQS_KALSHI_OCC_OBSERVE.json`.
