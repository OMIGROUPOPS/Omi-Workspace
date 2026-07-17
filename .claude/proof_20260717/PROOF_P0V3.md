# PROOF_PASS — P0 v3 (six fixes + census), candidate SHA `b88a4347`

**Prior art (C45):** C-CORRIDOR-TRUTH 07-16 (render-side bell clamp ≥ sched;
BELL-BEFORE-SCHED class founded) — this build moves the clamp into the engine
fire path. C-TAPE-BELL Part 2 07-15 (w2_fill_violation zero-tolerance emitter
— the defect sheet's source). C-GRACE-KILL + C-DAILY-STANDARD Part 0 (grace
machinery, retired here). C-BELL-SCOPE 07-13 (sanctioned-walk constant, now
flagged for retirement). ⑮ P5 07-17 (the join arm, sealed by the print-backed
seam). C-FREEZE-AT-GUN (4c) — kept as the law-collision founding wire.
Delta: no prior build bound the FIRE to the schedule, ordered the sweep ahead
of the fill window, or tested rises for print-backing. Staged-never-armed
prior art: none on these seams.

## LANE 1 — MECHANISM (per-game, deterministic, luck-free)

Replay basis: the 18 w2_fill_violation events on FORENSIC_w2_fill.md
(11:50:31 AM ET 07-17 sheet), replayed against each event's own gun_fired
line (its tts stamps give the schedule floor the clamp would have used) and
the leg's own churn/bind/repost rows. Full per-game table:
`.claude/p0v3_20260717/CENSUS_OF_18.md` (machinery
`analysis/census_of_18.py`, read-only over logs/live_v3_20260715..17.jsonl).

Per-game construction verdicts under `b88a4347`:

- **9 PHANTOM fires die at the clamp** (fired 42.5–231.1 min before their own
  floor: GALCOP-COP 93.2 / BASCAR-BAS 209.2 / KOIFIT-FIT 231.1 / NIJDEN-NIJ
  212.1 / NIJDEN-DEN 212.1 / HALSHE-HAL 42.5 / KUMBOO-KUM 56.6 / KUMBOO-BOO
  56.6 / BURMER-MER 58.3). All 5 self_fill fires carry condition
  `exceeds_sanctioned_walk` — the bot's own ⑮ join churn, NOT print-backed:
  under fix (3) the churn never happens (quote-only rises bind and HOLD), so
  the alarm input itself vanishes; under fix (1) any residual pre-sched fire
  is VOID. 4 of 9 fills also landed pre-floor → **W1 RELABEL** (the W2
  charge was manufactured by the phantom label). The 4 percat_fitted fires
  re-fire sched_clamped AT the floor — no W2 label before the floor, sweep
  leads at the floor.
- **9 TRUE post-bell fills are swept earlier**: booking sources on the sheet
  are reconcile_adoption ×4, cancel-race ×2 (manage/match_live),
  v4_resting_maker ×2, v4_engagement_join ×1 — every one a resting bid that
  survived into W2 because grace armed/held it (BYNLON class: graced
  01:00:47, filled 16:18 the day prior) or because the cancel raced the fill.
  Under fix (2) the sweep fires AT the stamp (task-spawned) and the manage
  pass cancels instantly (grace retired) — the resting window that produced
  these fills is structurally gone; the cancel-race window shrinks to the
  exchange round-trip minimum.
- **The churn mechanism dies measurably**: on the sheet's own legs the
  ⑮×clamp cycle ran 12–81 cancel/reposts each (TAU 78 binds/79 reaims,
  KRE 73/74, VAL 65/67, RIE 61/63, MER 41/42…) — 1,311 binds Jul 15–17,
  ≥352 on print-backed rises (undercounted proxy). Under fix (3) every
  quote-only cycle is a single `window_truth_bind` HOLD (queue preserved);
  print-backed joins execute ONCE with caps yielding.
- **Pair kills answered**: KREZHE-ZHE died in the churn's cancel/re-place
  racing the exchange-truth buy guard (`repost_place_failed recovered=false`)
  — no churn, no race. TAUBEJ-BEJ = true absence (conception gap, invariant
  fired; filed as follow-on, out of this build's scope, named honestly).
- **Guard misfires: none introduced.** The clamp voids only fires whose EVERY
  clock says pre-start (conservative min-side, C-ANCHOR doctrine); lying-long
  clock fires (percat class) re-fire at the floor, cost = label-latency never
  existence. Local suite: test_grace_kill / test_sustained_flow /
  test_latch_walkcap (incl. new void→refire case) / test_sf_obs / test_fd_limit
  ALL PASS; 3 pre-existing HEAD reds named in the vault entry, untouched.

**Lane-1 verdict: the construction improves on every one of the 18 — 9 labels
were manufactured (die at the clamp), 9 resting-into-live windows were
grace-held (die at the sweep), and the churn that fabricated the self_fill
alarms becomes a hold. No lawful W1 behavior is refused (print-backed joins
still execute; post-floor bells still fire and sweep).**

## LANE 2 — SETTLEMENT P&L (secondary, sanity)

The 18's exited legs realized **+390¢ true-F / +425¢ phantom-class** on the
day (per-leg rows in the census) — the W2 fills were PROFITABLE today.
FLAGGED LUCK-POLLUTED: n=16 exited legs, one day, in-play buys carry
knife-edge risk the day's sample never priced (the 07-15 morning's 75-W2
sheet billed −3,159¢ settled on the same class). The law is risk-shaped;
Lane 1 is the verdict lane per the gate's own doctrine. No invented fills,
subtractive accounting only.

## Gate lanes

- lint: PASS (deploy/lint_gate.py, local run at `b88a4347`)
- smoke: runs on the box at deploy ([2/3])
- outcome proof: THIS DOC — cites candidate SHA `b88a4347`; doc-only commits
  after it, no code delta.
