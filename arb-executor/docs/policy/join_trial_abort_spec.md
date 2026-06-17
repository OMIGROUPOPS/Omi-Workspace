# C-JOIN-TRIAL — Pre-Registered Degraded-Deploy Abort Spec (LOCKED)

**STATUS: pre-registered before the trial runs. Bars are falsifiable magnitudes, committed at
`8cc9ff1`+trial-patch. Mirrors the C-ABORT-SEAL discipline. The live bot (PID 3240515) is
untouched; nothing deploys until you + Plex + operator countersign the trial.**

## Why a trial, not a deploy

The join-the-bid + per-minute-walk edge (+2.6–3.9c/attempt, bilateral 2× EV) was validated with a
**price-touch fill rule (`yes_bid_low ≤ L`)** — an **UPPER BOUND**. Real Kalshi is **price-time
priority**, and the walk re-posts **~26.9×/leg vs 5.5× static**, resetting queue position ~5× more.
G2 median-499 shows MMs rest deep at exactly the mid-book levels joins land on. So **live
queue-conditional fill probability is unmeasured** — it could be a fraction of the modeled ~99%, and
bilateral 2× EV degrades if the legs' fills are correlated. The trial **measures** the missing
number; the abort **kills** it if queue starvation is real.

## Trial configuration (operator-set in `config/deploy_v5_live.json`)

| param | trial value | note |
|---|---|---|
| `join_trial_mode` | `true` | arms the telemetry-counted abort (default `false` = dormant) |
| entry size | small (5-share / ~5¢ notional) | degraded; bounded loss |
| scope | first slate only | operator stops after slate 1; the abort can stop it sooner |
| `fallback_maker_clamp` / `maker_only_entry` | as configured | join is maker-only |

## Telemetry (logged per join leg, `join_queue` event — unconditional)

- `depth_at_post` — queue-depth-ahead (`book.bids[L]`) at the (re-)post
- `depth_now` — queue-depth-ahead at fill-or-cancel
- `fill_latency_sec` — time from last (re-)post to resolution
- `reposts` — re-post count for the leg
- `outcome` — `fill` | `cancel`

This is exactly the queue-conditional-fill data the `bid_low ≤ L` validation could not produce.

## The abort rule (LOCKED — falsifiable)

Over the **first `JOIN_TRIAL_MIN_RESOLVED = 10`** join attempts that reach fill-or-cancel, compute:

- `mean_reposts = trial_reposts / trial_resolved`
- `fill_rate    = trial_fills   / trial_resolved`

> **ABORT iff `mean_reposts > 20.0` AND `fill_rate < 0.60`.**

Both must trip — high churn *with* starved fills = the queue-priority failure mode the validation
could not see. (High churn with healthy fills = fine; low churn = fine.) On abort: set
`join_trial_aborted`, log `join_trial_abort` with the realized magnitudes, and **halt all new join
entries** (filled positions ride to their exits; no new placements). The operator then reviews the
`join_queue` ledger before any re-attempt.

### What proves / kills the question

- **Survives** (no abort, `fill_rate ≥ 0.60` at modeled re-post rates) → queue-conditional fill is
  acceptable; the +2.6–3.9c edge is real on live priority; proceed to a wider trial.
- **Killed** (abort trips) → the walk churns queue position faster than fills arrive; the price-touch
  validation was the upper bound it was feared to be. Next step is the dwell-time dampener (Plex's
  180s hysteresis caps walks ~9/leg) **measured against this ledger**, not a blind re-deploy.

Bars are pre-committed so the trial answers the queue-survival question with a number, not
"fills looked OK."
