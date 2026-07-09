# OUTCOME PROOF (C46, two-lane) — C-INFLIGHT-LOCK (BOARD −1, the GORSTE same-tick race; order-path, deliberately alone in its deploy)

**Candidate SHA: `330266c7`** (live_v4.py only — the place_order wrapper + INFLIGHT_LOCK_TIMEOUT_SEC constant; nothing else rides).

## Prior art (C45)
- **MASTER 07-09 (~12:15 pm vault entry)** — the exhibit: GORSTE-GOR ×2 buys @62¢, 11:41:42 AM ET, **104.6 ms apart** (log epochs 1783611702.8943 / .9989); contained by direct-API surgery 11:51:35, re-audit PASS 11:54:46. TANCHE lineage (the 06-xx race class).
- **C-BUY-POSITION-GUARD 07-07** — the exchange-truth outer wall this lock completes: the guard `await`s two per-ticker API reads before the POST, so a same-tick sibling coroutine passes the same guard on the same stale truth — the 103 ms window the wall cannot see. The wall STAYS; the lock closes the window.
- **C-BAND-CLAMP make-it-stick lesson + the per-leg-patchwork lesson** — one lock at THE chokepoint every placement path flows through (conception, DCA, repost/walk, completion, re-entry cycle-2); no path-specific patches.
- **OS BUILD (07-09)** — this lock is named os_active precondition #2 of five; satisfied by this deploy.
- **C-ORDER-V2 (fac74b5)** — the 15s aiohttp ack timeout the lock bound derives from (20s = 15s + margin).

## LANE 1 — MECHANISM (harness on the VPS against the real deployed wrapper, `_place_order_unlocked` stubbed as the exchange leg; /tmp/til.py, 4/4 PASS)
1. **GORSTE replay** — second identical buy fired 104.6 ms into the first's exchange leg: first places, second **REFUSED in-process** — `inflight_lock_refused {action: buy, price: 62, count: 5, held_ms: 105.3}` on KXITFWMATCH-26JUL09GORSTE-GOR. Under the old code both reached the exchange (observed live 11:41:42 AM).
2. **Synthetic same-tick double-fire** (0 ms apart, same event-loop tick): exactly one places, one refused — the acquire is synchronous (no await between check and set), so same-tick siblings cannot both pass.
3. **Crash-safety** — a lock seeded 25 s stale (> the 20 s ack bound): `inflight_lock_forced_release` logged LOUDLY, the placement proceeds, the lock map is clean after ack. A stuck lock can never orphan a ticker.
4. **Non-interference** — same-ticker sell + a different ticker fly concurrently, zero lock events. Key = (ticker, action).
- **Structure guarantees coverage:** the original body (every existing guard intact, byte-identical) became `_place_order_unlocked`, entered ONLY via the wrapper's try/finally — every placement path and every return releases by construction. Sole caller verified.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The lock refuses duplicate placements; it changes no price, size, or target.

## Regression watches
`inflight_lock_refused` per night — should be RARE and named (each is a caught race) · `inflight_lock_forced_release` — should be ZERO (any occurrence = an ack path exceeding 20 s, investigate) · `buy_stack` audit failures stay 0 · placement throughput unchanged (lock is per ticker+direction, free in the uncontended path).
