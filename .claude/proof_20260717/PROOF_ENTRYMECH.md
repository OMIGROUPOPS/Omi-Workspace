# PROOF_PASS — ENTRY MECHANICS (six parts), candidate SHA `34ca4715`

**Prior art (C45):** C-CONCEPTION-HORIZON (map edge, untouched), C-EARLY-UNLOCK
/ C-EARLY-CANVAS-2 (staged window-wideners, subsumed), C-BESTBID-REPOST +
C-DEPTH-GOVERNOR + C-WALL-SKIP (staged hands, armed here), C-JOIN-TRIAL
(join_queue telemetry re-keyed), C-FV-OBSERVE-SHIP (blend → voice),
ORIENT_V1 oriented-tells shadow (one voice in the prior). Delta: no prior
build parked both legs at discovery, keyed the park role on a multi-voice
prior, or forbade timer reposts.

## LANE 1 — MECHANISM (per-game, deterministic, luck-free)

Replay basis: the Jul 15–17 slate's own log record (2,018 placements, 1,911
join_queue reads, 754 two-leg events; machinery
`analysis/entrymech_census.py`, full table
`.claude/entrymech_20260717/ENTRYMECH_CENSUS.md`).

- **P1 discovery-hour**: under `34ca4715` the 1,417/2,018 placements (70%)
  that waited >4h after their event was on the tape would have parked at
  discovery — the median 300 shares (p75 2,176) queued ahead at the
  fitted-hour join is the queue the change buys back on every one of those
  legs. Construction-lane only: earlier resting cannot worsen any leg's
  price (same aim tables, same caps, same floors — only the clock moved);
  the horizon, buffer, quality, floor, and gun gates all still govern.
- **P1 orientation**: the leader-rises role assumption was WRONG on 368/484
  determinable events (76%) on this slate. The prior stamps every dossier;
  the park swap is bounded (conviction ≥ 0.7, n ≥ 2) and with today's thin
  voices fires rarely — the change is strictly information-adding at
  conception, with the swap's exposure gated behind two agreeing evidence
  voices.
- **P2 evidence-only reposts**: 2,839 v4_move_repost on 07-17 (123 legs; top
  legs 40–53/leg/hr; TAU 78 binds/79 reaims, KRE 73/74). Replayed under the
  gate: every deep-cast repost whose regime did not change and every timer
  pass dies to a single `repost_no_evidence_hold`; touch reposts on real bb
  moves survive (the DAEVAS strand class stays fixed). Queue priority is the
  direct win; the KREZHE churn×buy-guard race class loses its cause.
- **P3 birth clock**: 1,584/1,911 join_queue reads (83%) reported an
  order-age latency less than half the true wait; median under-read 40.7×
  (145s vs 5,896s). The dual-clock emit corrects every future read; no
  behavior keys on the corrected field yet (instrumentation-lane).
- **P4 arms**: wall_skip_enforce is pair-aware BY CONSTRUCTION (whole event
  or nothing — it cannot manufacture a naked single); depth_aware_join and
  best_bid_aware_repost were already live in config; `arm_evidence` lines
  make every threshold auditable at boot.
- **P6**: panel-only (grades/keys); no trading-path change. The day-key fix
  is verified against the misfile mechanism (fills.day = entry-buy day) read
  directly from the code; settlements sweep warms from the next
  fund_tracker restart with last-fill fallback until then.
- **Guard misfires: none introduced** — lint PASS, local suite PASS (one
  pre-existing red `leg2_walk_guarded`, named in the vault), all changes
  additive or gate-removals bounded by standing outer guards.

**Lane-1 verdict: construction improves on every measured axis — 70% of
placements gain hours of queue, the churn engine loses its trigger, the
flow meter stops lying 40× — and no lawful behavior is refused.**

## LANE 2 — SETTLEMENT P&L (secondary, sanity)

No settlement claim is made: the changes move WHEN legs rest, WHY they
repost, and what the record says — not prices or exits. FLAGGED
LUCK-POLLUTED at any n until the early-parked cohort accrues; the
OPEN_LEDGER watch (early-parked cohort fill rates vs standard) is the
pre-registered scoreboard.

## Gate lanes

- lint: PASS (deploy/lint_gate.py at `34ca4715`)
- smoke: runs on the box at deploy ([2/3])
- outcome proof: THIS DOC — cites candidate SHA `34ca4715`; doc-only
  commits after it, no code delta.

## ADDENDUM (same dispatch, close-out scope) — proven SHA `7ef19c62`

(a) **THE CUTOFF IS LAW**: `state/new_law_epoch.json` persisted at the first
new-law boot (recorded on the box: **1784314698.0 = 02:58:18 PM ET 07-17**);
TODAY_SHEET splits fills/reposts old-era vs new-era at the epoch — the day
reads as a before/after experiment. Read-only meter change; no trading path.
(b) **MIGRATION PASS** (`_migration_pass`, one-shot per bid, 90s book-warm
delay): every PRE-EPOCH resting entry bid re-judged once under the
orientation prior — ENDORSE (hold; queue an asset, the DEFAULT and the
verdict whenever the prior lacks swap-grade conviction) / RE-AIM (cancel +
free; the router re-parks at the prior's level under the new mechanics) /
RETREAT (refuse-class → pair-level withdrawal, never one leg). Lane-1
construction: no blanket cancels by design; the endorsed majority keeps its
queue; every verdict carries the voices' numbers (`migration_verdict`) and
the tally lands in the close-out (`migration_summary`). `migration_judged`
persists so restarts never re-judge. Lane 2: n/a (no price/exit change);
the migration tally itself is the acceptance record.

- lint: PASS at `7ef19c62`; local suite PASS (same one pre-existing red).
- doc-only commits after `7ef19c62`; no code delta.
