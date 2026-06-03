# T51 hardening spec — live-match detection for quiet/flat-line matches

**Status:** DESIGN (read-only). Implement AFTER RUN-7 baseline lands; it is the **gate for RUN-8** (buffer relaxation). Do not implement as a port — this is a design task (LESSONS 514 / A-T51).

## Problem
`_is_match_live(et)` (live_v4.py:2050) latches live on an **absolute** trade-burst: `≥ LIVE_TRADE_BURST(10)` prints across the event's legs within `LIVE_DETECT_WINDOW_SEC(60)`. Two gaps:
1. **Quiet/flat-line live matches never trip it.** A thin even-line match (TIAARN 2026-06-01, flat 50-51¢) trades < 10 prints/60s in-play → never latches → the bot would enter/hold into live play. The absolute floor is blind to low-volume live.
2. **No reliable status backstop.** Kalshi exposes no live-start field (`occurrence_datetime`/`expected_expiration_time` are frozen noon-UTC placeholders). ESPN start-times are wrong and drift (TIAARN 16:00→16:30Z). And `event_start_time` is **locked on first estimate** (set-once guard at live_v4.py:1953), freezing a drifting ESPN time → `match_start_ts` (2370) and the T-15m buffer fire at the wrong wall-clock.

Relaxing the entry buffer (RUN-8) makes this acute: bids live closer to start → higher chance of filling into an **undetected** live match. Hence T51 hardening gates RUN-8.

## Design — three pillars

### Pillar A — acceleration-based latch (primary; no external dependency)
Replace the absolute-only test with **rate-of-change vs the pre-match baseline**. A quiet book has a near-zero pre-match baseline, so even 3-5 in-play prints is a large acceleration.

Data (already present): `self._trade_times: Dict[ticker, deque]` retains ~600s (line 1007); a separate 30-min structure exists (line 1010) — use a 30-min deque per leg for the baseline. Populate at the existing trade-ingest site (line 1500).

New constants:
```
LIVE_DETECT_WINDOW_SEC   = 60     # (existing) recent window
LIVE_TRADE_BURST         = 10     # (existing) absolute fast-path, keep
LIVE_BASELINE_WINDOW_SEC = 1800   # 30-min pre-match baseline lookback
LIVE_BASELINE_LAG_SEC    = 120    # exclude the most-recent 2m from the baseline (don't contaminate baseline with the onset)
LIVE_ACCEL_MULT          = 5      # recent rate >= K x baseline rate => accelerating
LIVE_ACCEL_MIN_ABS       = 3      # AND >= this many recent prints (don't latch off 1 print on a dead book)
LIVE_ACCEL_PERSIST       = 2      # require the condition true on >=2 consecutive evaluations (anti-single-spike)
```

`_is_match_live(et)` logic (latched; pure-helper-extractable for unit test):
```
if et in self._events_live: return True
now = time()
recent  = prints across legs in [now-60, now]
baseline_prints = prints across legs in [now-1800, now-120]
baseline_rate   = baseline_prints / ((1800-120)/60)          # prints per minute, ~0 pre-match
recent_rate     = recent / (60/60)                            # prints per minute
accel = (recent >= LIVE_ACCEL_MIN_ABS) and (recent_rate >= LIVE_ACCEL_MULT * max(baseline_rate, eps))
burst = (recent >= LIVE_TRADE_BURST)                          # existing fast-path
if burst or (accel persisted LIVE_ACCEL_PERSIST evals): latch live
```
- `eps` (e.g. 0.1/min) floors the baseline so a genuinely-zero baseline + a few prints still trips (0 baseline → any flow is "infinite" acceleration; the MIN_ABS=3 floor is what gates it).
- **Persistence** (`LIVE_ACCEL_PERSIST`) guards against a single pre-match block-trade spuriously latching — track a per-event consecutive-true counter.
- Latched: never un-latches (a match does not un-start). Existing `_events_live` set.

**Catches TIAARN:** baseline ~0, in-play 3-5 prints/60s → accel true, persists → latched. **Does not false-trip** a genuinely thin pre-match book: needs ≥3 prints AND a sustained acceleration, which sparse pre-match flow (median 0-3 prints over the whole window per the corpus) won't produce.

### Pillar B — ESPN match-STATE confirmer (corroboration / dead-book backstop)
Kalshi has no usable field; ESPN's **state** (in-progress / scheduled / final) is more reliable than its **time**. Use the state, not the start time.
- At the existing ESPN/TE fetch (1953-1970), additionally fetch + cache the event's match **state**; refresh it on a cadence for events inside their entry window.
- Latch live if `espn_state == "in_progress"` (independent sufficiency with Pillar A).
- **One-way only:** a stale ESPN "scheduled"/"final" must NEVER un-latch a match already flagged live by Pillar A (latched stays latched). ESPN is a confirmer/backstop, not a veto.
- Reliability caveat (LESSONS 514): the TE `live_scores` feed historically emitted only scheduled/finished and the live match was sometimes absent — so ESPN-state is the *secondary* signal; Pillar A (volume-acceleration, no external dep) is primary.

### Pillar C — unlock the frozen start estimate
`event_start_time` is set-once (1953 `if et not in self.event_start_time`) → freezes a drifting ESPN time → wrong `match_start_ts`/buffer timing.
- **Refresh, don't lock:** update `event_start_time[et]` when a newer estimate differs materially (> a few min), bounded by the existing ±12h date-sanity check (1147). 
- **Decouple live-detection from the start estimate:** the live decision rides on Pillar A+B, NOT on `match_start_ts`. A wrong start time then cannot blind the live guard (it only mis-times the entry-window scheduling, a softer failure). This is the key safety property for RUN-8.

## Integration points (all route through `_is_match_live`)
- live_v4.py:2981 — placement: skip entry if live.
- live_v4.py:3470 — manage/fallback: skip fallback if live.
- live_v4.py:3502 — T52: do not fallback-cross if live.

Hardening `_is_match_live` covers all three. No call-site changes needed beyond the function + the start-time refresh (C).

## Test plan (must pass before RUN-8)
1. **TIAARN flat-line:** baseline ~0, 4 prints/60s in-play → latches via Pillar A. (The exact case the absolute-10 missed.)
2. **Thin pre-match no-op:** sparse sub-3 prints, no sustained acceleration → does NOT latch (no false-positive that would block legitimate pre-match entry).
3. **Absolute fast-path:** ≥10 prints/60s → latches (regression — unchanged behavior).
4. **Single pre-match block trade:** 1 large print → does NOT latch (MIN_ABS=3 + persistence).
5. **ESPN in-progress, dead book:** latches via Pillar B.
6. **Latch persistence:** once live, stale ESPN "scheduled" or a volume lull does NOT un-latch.
7. **Pure-predicate unit test:** extract the accel decision (like `_resting_cancel_reason`/`_reprice_target`) and assert the matrix above; plus a flags-off path that reproduces the current absolute-10 behavior byte-identically for clean rollback.

## Gating
T51 hardening is a **hard prerequisite for RUN-8** (buffer relaxation). Build + test it AFTER RUN-7's baseline is confirmed; do not relax the buffer until the TIAARN flat-line case (#1) passes live-verified.
