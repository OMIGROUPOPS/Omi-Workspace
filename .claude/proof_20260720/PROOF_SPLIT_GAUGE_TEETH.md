# OUTCOME PROOF — SPLIT-GAUGE DISPATCH P2+P3 (cascade read-side + safety teeth)
Candidate: `a146f9d4` (P3 teeth; includes P2 cascade `ebec0368`, P1 verdict `cf9980e5`).
C46 two-lane, judged separately.

## LANE 1 — MECHANISM (primary, luck-free)

### Construction delta: ZERO by scope
The full code delta since the last deployed state touches four sites, none of
them an aim, offset, cell, cast, or refusal path:
1. `place_order` payload — `expiration_ts` attach behind
   `expiration_wire_enabled` (**default false — DARK**; entry buys only). With
   the flag off the payload is byte-identical.
2. Audit exempt-file loader — mtime-reload (read hardening; same set
   semantics, plus reload on change).
3. `reconcile()` — `_naked_tooth_scan` on the pos/ord maps the pass already
   fetches: DETECTION lines + heal that fires ONLY on defect states (a clean
   book produces zero lines and zero actions). Grade distribution, ≤97
   completion, delta-aim, pair completion, FV-capture: all unreachable from
   this code.
4. Steady loop — `_band_cascade_pass` (read-side logging only; `band_call` /
   `band_recall` / `pair_class_read`; no consumer).
The smoke replay at this gate is the runtime proof both new passes run clean
on a recorded slate hour.

### Would-have replay — the 2026-07-20 morning, deterministic from the
### exchange lifecycle in `.claude/vanished_exit_20260720/VANISHED_EXIT_TRACE.md`
- **GNI (SKOGNI-GNI), the 53-minute unbooked fill:** sibling_repost placed
  09:22:31 by the running process, filled 09:28:41, UNBOOKED while
  check_fills lived (per-order poll starvation — the root this gate reads).
  The tooth's 60s bulk pass names `unbooked_fill_defect` by **09:29:41**
  (cycle 1) and confirms naked at cycle 2 by **09:30:41** → heal reposts the
  band exit ≈ **09:31** — nine minutes before the sweep's 09:39:54 restore,
  ~ten before the operator's eyes (~09:40). The owed-tooth claim in the
  ledger ("would have flagged at ~09:29") is now the code's measured line.
- **HAN (BRUHAN-HAN):** Kalshi determination-cancel 09:37:03, settlement
  stamp ~66s later. Market status `determined` → the settlement_pending
  carve-out keeps the tooth QUIET — no false naked line where standing down
  was correct (the MASDUT lesson, preserved).
- **JAG (HEJJAG-JAG), boot-gap orphan (zero engine lines ever):**
  `naked_leg_defect` ORPHAN-labeled at the first post-boot cycle (~09:02)
  instead of discovery by hand at ~09:40. Detection never silent; adoption
  stays guarded (unchanged policy).
- **GNI cycle-2 phantom (10:21:40 kept_position on already-sold shares —
  the SWEEP×ENGINE double-ownership residual):** exchange shows no position
  while the market is live → `phantom_position_defect` at ~10:22, dropped at
  ~10:23 (2 confirmed cycles + market-status check). The in-memory phantom
  dies in two minutes instead of surviving to the next boot.

### Cascade (P2) mechanism value
Zero construction delta (no consumer); its Lane-1 value is instrument
coverage: a `band_call` on every big-4 conception ≤60s after birth, the
re-call stream, and the pair-class read the next campaign scores against the
split gauges. Coverage watch is on the BOARD.

## LANE 2 — SETTLEMENT P&L (secondary)
No settlement cohort exists for detection/logging tooling and none is
claimed: **INSUFFICIENT SETTLEMENTS / NOT APPLICABLE by design** (C46: Lane-2
is never the sole verdict; there is no Lane-2 claim here to pollute).

## Verdict
Lane 1: the teeth convert the morning's three by-hand catches into ≤2-minute
typed detections with bounded, defect-state-only heals; the cascade adds the
named instrument at zero construction cost. Lane 2: no claim. DEPLOY.
