# FLIP REQUEST — `per_match_clock: true` (config-only, nothing bundled) — C46 TWO-LANE DOC → Plex re-gate

**Candidate:** config-only diff on the running `0acd67e` build (code ce38ca8c lineage, source RATIFIED by
`PLEX_PART1_SOURCE_RULING.md`). Flip = ONE key: `per_match_clock: true`. Scale-gun consumer NOT included
(separate future arm per the ruling). Rollback = one config flip back through the gate.

## Prior art (C45)
Ruling: PLEX_PART1_SOURCE_RULING.md (source ratified; widening dict ratified; shadow-first conditions).
Facts pre-established and accepted by the ruling itself: T51/C32/OSOWAL/ROADMAP coarse-placeholder;
C-KALSHI-OCC June wide-envelope design; CLOCK_AUDIT 135-event tape-gun join (+4..9min median, 75% ±30min).
Spec: PART1_SPEC.md. Evidence: PART1_GATE_EVIDENCE.md, SHADOW_GRADUATION.md (graded), EXHIBIT_A_PASCOP.md.

## LANE 1 — MECHANISM (primary)
**What the flip changes, deterministically:** the entry-window clock resolves HONEST (per-match TE/ESPN,
legacy edges) or FALLBACK (today's placeholder + the ratified per-cat widening). Nothing else — exit,
cancels, completion, meter, liveness/abandon, latch_tape_override all keep the legacy clock (source-ratified
scope, grep-proof).
- **Windows that would exist vs do exist (tonight's live shadow, n=115 honest joins):** ITF_W legacy windows
  open a median **+360 min late** (n=32; the window opens ~2h AFTER the true start — no premarket exists on
  the legacy clock); ITF_M +360 (n=7); ATP_CHALL +180 (n=49); WTA_CHALL +160 (n=19); mains mixed small-n
  (−180..+180, n=8) — where the ratified 8h fallback envelope + the untouched tape latch govern.
- **Replay evidence (147-game box, PROOF_PASS.md):** the half_timing leak (fader divots passing before
  bounds exist) is this clock error wearing a leak costume (night-1: 8 events/~131¢; full-tape: ITF_W
  7ev/147¢ + ITF_M 4/66¢). The honest-clock completion-recovery channel graded conservatively (+1 pair
  recovered, 10/14 candidates refuted by tape) — the flip's Lane-1 case is CORRECTNESS of window
  construction, exactly as the source ruling frames it: entering the windows where the money demonstrably
  trades (CHALL best moments T−1..−5m; ITF premarket = pre-T-4h on the card clock).
- **Shadow wiring-proof (the ruling's stated purpose): PROVEN** — see SHADOW_GRADUATION.md: coverage
  213/213 (100% vs ≥95%), sched_fresh 100% (vs ≥90%), per-cat deltas match the audit's offsets, resolver
  joins via direct_6char, category-mislabel wart handled per spec (bot's own category used throughout).
- Fallback safety: FILE-STALE/ENTRY-MISSING → today's exact clock + ratified widening; a table/join miss can
  never lock a window the legacy path would have opened (fallback ≡ status quo + widening).

## LANE 2 — SETTLEMENT P&L (secondary, honestly flagged)
+$1.00 on the 147-game replay (**n=1 settlement — LUCK-POLLUTED, stated**). Lane 2 cannot and does not carry
this flip; Lane 1 correctness + the ruling's own pre-established facts do. Post-flip, the nightly pass grades
both lanes on live slates (the ≤97/half_timing channels are the expected movers).

## THE ASK (operator's words)
The shadow's job was wiring-proof; **the wiring is proven** (graded scoreboard attached). The
US-daytime-slate condition's PURPOSE — all-category coverage — is met by the audit's 135-event join plus
tonight's live confirmation across all six categories (213 events). **Rule the flip now, or name the
specific missing evidence.** Known-open item, honestly stated: G4 (MAIN legacy-fires-shadow-suppresses
cases) has no overnight evidence — quiet-hour baselines are zero so the scaled bar sits at the floor — but
G4 gates the SCALE-GUN consumer, which is not part of this flip and keeps collecting regardless.

*On ratification: `per_match_clock: true` (one key), full four-bar gate, one restart, monitor validating;
MAIN widen X retune continues shadow-informed per the ruling's caveat.*
