# The anatomy map, amended — every decision site at the dial level

Analysis seat only. Read-only. Enumerated against **V47's actual code path** (`fb74c8b8`:
`window1_v47_same_tick_arm.js` → v45 → v43 → v41+v42 → v36 → v32/v35). The July expression audit walked **12**
sites; the code path confirms those and adds **6** — **18 dial-level sites**. This completes the July
**C-EVERY-SITE dispatch that was drafted and never sent** — its lineage is `truth/archive/tape_20260714`
("PART 1 — WHERE THE READING STOPS: every decision site from discovery to fill"); no C-EVERY-SITE artifact
exists anywhere in the tree (grep-clean), consistent with drafted-unsent. Machine list:
`THE_ANATOMY_MAP_DIALS.json`.

Legend — outcome layer: READ (a state), LEVEL (a price), PERMISSION (a gate), ACTION (place/reprice/cancel/hold),
CREDIT (a fill). Resolution: RECEIPT (per book receipt), TRAIL (trailing window), EVENT (once per event).

## The 18 sites

**S1 · quote-path read** (v32.quotePathState) — job: direction from the latest trailing directional evidence.
READ / TRAIL(300 s). Consults: quote/print direction evidence rows. Should also: forward-horizon truth
calibration (12d67c8a). Levers: `LOOKBACK_SECONDS=300` (receipt: V32 build). CANON: Jul-6 doctrine. Defect:
none direct; feeds S3.

**S2 · pressure read** (v32.pressureState) — job: direction from top-5 depth ratio. READ / RECEIPT. Consults:
depth_ratio only. Should also: hidden-book inside-print pressure (`6bc169bf`, +4-6 pt lead) — currently ignored.
Levers: `PRESSURE_RISING_MIN=0.60`, `PRESSURE_FALLING_MAX=0.40` (V32 build). CANON: Jul-6 depth doctrine.
Defect: thresholds never re-fit since Jul-6.

**S3 · state combiner** (v32.combineState) — job: fuse S1/S2; quote primary, pressure only when quote SETTLED.
READ / RECEIPT. Consults: S1, S2. Should also: the mirror (sibling read) and the disagreement flag it itself
emits. Levers: primacy order (fixed). CANON: TRAILING_300S_QUOTE_PATH_PRIMARY. **Defects: `disagreement` is
computed on every receipt and consumed by NOTHING (no defer rule — see conflict table); FALLING calls invert
26% forward (12d67c8a), the one dangerous quadrant.**

**S4 · persistence-join qualification** (v43.persistenceJoinUpdate, C1) — job: arm the riser join. PERMISSION /
TRAIL(residency ≥300 s; C1 first-observation arm when clause on). Consults: state, bid, residency. Should also:
dip-supply evidence (`9ee14bf5`: 69% of unfilled risers arm with no fill path). Levers:
`PERSISTENT_LEVEL_SECONDS=300` (V41 build), `arm_at_first_evidence` clause (receipt: `9ddfe8c6` +219¢ →
V43-C1). CANON: trigger frontier `084df125`. Defect: arms without any dip/fill-path evidence.

**S5 · same-tick arm atomicity** (v47.decideReceipt) — job: join qualification + placement in one receipt-local
call. ACTION-ordering / RECEIPT. Levers: `scheduler_latency_after_qualification=0` (receipt: `8877c2d5` SURECH).
CANON: V47 control binding. Defect: none known.

**S6 · RISING placement** (v41.placementTarget branch 1) — job: rest at the armed join level. LEVEL / RECEIPT.
Consults: join level. Should also: the sibling cap *feasibility of its own future cap* (S16's richness organ).
Levers: none beyond S4's. CANON: P2-over-P1 (`cca7c6c1`). Defect: none direct.

**S7 · FALLING placement** (v32.fallingRestTarget) — job: bid−1, monotone down, never chase up. LEVEL / RECEIPT.
Consults: bid, previousTarget, cap. Should also: gap-credit walk evidence (S16b) — the strict-ask freeze
(`aa884cc5`, 50 legs). Levers: no-chase monotonicity (V32 build). CANON: V36 FALLING no-chase. Defect: the
freeze class; PANFAL·PAN's genuine L5.

**S8 · SETTLED placement** (v35.livingRestTarget) — job: bid−1 re-anchored every receipt. LEVEL / RECEIPT.
Levers: none. CANON: V35 living rest. Defect: none direct.

**S9 · WTA inverse-falling hold** (v41.placementTarget branch 2) — job: when WTA and the other expression reads
FALLING, hold min(pulse floor, causal reach low). LEVEL / RECEIPT. **Defect: this is LAW-B-class logic still
live in the executable while the doctrine was declined (`e177c2fb`) — a dial without a ratified doctrine;
consults the superseded pulse floor (S15).**

**S10 · C3 loosen** (v43.placementTarget) — job: tracking rests bid at the bid (not bid−1). LEVEL / RECEIPT.
Levers: `loosen_one_cent` clause (receipt: `52275c9d` +51¢, only-the-first-cent). CANON: V43-C3. Defect: none —
correctly excludes join/WTA authorities.

**S11 · post-only sanity bound** (v41.postOnlyBound) — job: target ≤ min(ask−1, cap). LEVEL-clamp / RECEIPT.
CANON: rest<ask law. Defect: the SALIBR 1¢ wall (a 15 h dwelled ask at P is unreachable by ≤ask−1; L6 verdict).

**S12 · deep-gap feasibility guard** (v42/v43-C2) — job: withhold a target whose implied sibling cap sits
>10¢ under the sibling's ask. PERMISSION / RECEIPT. Consults: target, siblingBestAsk. Should: **be replaced**
— dry-sibling maturity form (`b503e4ed`, reopened as V44b). Levers: `DEEP_GAP_TOLERANCE_CENTS=10` (receipt:
`645e035b` T-sweep). **Defect: COMPOSITION_STALE; in composition it blocked 17 feasible completions to save
+27¢ (`639e8b19`).**

**S13 · incumbent-rest adjudication under withhold** (v42.decide tail) — job: keep a feasible incumbent rest /
cancel an infeasible one / hold-no-order for withheld new placements. ACTION / RECEIPT. CANON: V42 comment law.
Defect: none known.

**S14 · guard release at sibling credit** (v45.decide) — job: terminate guard authority once the sibling is
credited. PERMISSION-override / EVENT. Levers: `release_guard_on_sibling_credit` (receipt: `3bda0a54`, +1 pair).
Defect: scope too narrow — releases only on credit, not on the guard's own staleness.

**S15 · trailing pulse floor** (v41.trailingPulseFloor) — job: deepest ask level revisited ≥2× in 300 s. LEVEL
(consulted by S9 only) / TRAIL. Levers: `LOOKBACK_SECONDS=300`, `PULSE_REVISIT_MIN=2` (receipt: V38
PULSE_FLOOR_BINDING ← `d1ac9497`). **Defect: the substitution audit's trailing-myopia (`bc0ce289` #5) — the
census doctrine is session-scale recurrence; the dial implements a 5-minute memory.**

**S16 · lazy first-fill pair cap** (runner) — job: cap = 99 − first entry once one leg credits. LEVEL-clamp /
EVENT. Consults: first entry only. Should also: the first leg's own achievable floor — **the richness organ:
31/45 sealed cap-kills self-inflicted (`a20e1a85`), the ranked-#1 shelved lever.** Levers: the 99 constant
(CANON pair law). Defect: as stated.

**S16b · gap-credit instrumentation** (V47 ledger `gap_credit_*` fields) — job: count single-tick ≥3¢ ask-gap
walk opportunities. TELEMETRY only — **the V46 clause is BLOCKED, not operative**; fields record refusals.
Defect: the 50-leg freeze it measures remains unfixed.

**S17 · hard pre-bell edge** (runner) — job: the evidence/fill window's right edge. PERMISSION / EVENT. CANON:
V36 span law, unchanged since. Defect: 12 stand-too-late legs arm at/after the record's end (`aa1cc301`) — the
edge law never checks whether a rest ever stood inside the record.

**S18 · credit law** (runner scoring; v41.tradedAtLevel under the V48 ruling) — job: credit any true trade
at-or-below a standing rest, strictly after stood; quote touch never credits; strictPrintCross = build
verification only. CREDIT / RECEIPT. Levers: none (law). CANON: trades-as-truth `e073c606`. **Defect: the
FANBIG through-bid print not admitted (`653b7f13`) — one proven candidate crediting defect.**

## The conflict table — two sites, one leg, one receipt

| conflict | current resolution | defer rule | status |
|---|---|---|---|
| S1 vs S2 (reads disagree) | S3: quote primary unless quote SETTLED | fixed primacy | **flag: `disagreement` emitted, consumed by nothing — a computed conflict signal with no consumer** |
| S4 arm vs S6 placement | S5 same-tick: one receipt-local call | qualification then placement, atomic | resolved (V47's fix) |
| S6 join vs S10 loosen | S10 checks authority; join/WTA excluded from loosen | loosen defers to non-tracking authorities | resolved |
| S6 join vs S9 WTA hold | placementTarget order: join branch first | WTA hold defers to an armed join | resolved, but S9 itself is doctrine-less |
| S12 guard vs S6/S7/S10 target | guard adjudicates *after* the target (S13: keep-feasible / cancel-infeasible / hold) | placement proposes, guard disposes | resolved; guard itself stale |
| S12 guard vs S14 release | sibling credit terminates guard authority | release wins | resolved |
| S11 sanity vs any target | min-clamp last | sanity always wins | resolved |
| S16 cap vs any target | min-clamp inside S11 | cap always wins | resolved — but no rule lets *anything* argue the cap down (the richness defect has no forum) |
| S15 pulse vs S4 join (both propose riser levels) | pulse reaches placement only via S9 | join wins outside WTA | resolved by accident of branch order — **no explicit defer rule written** |
| S18 credit vs S7 freeze (trade below a frozen rest) | uncredited (rest wasn't there) | none — **missing rule: a strict-ask-frozen rest has no path to the flow S18 would credit (the 50-leg freeze)** | **missing** |
| S3 read vs sibling's S3 read (mirror incoherence, 69%) | none — each leg reads alone | none | **missing — the one-eyed/coherence instrument (`b26cf548`) has no arbitration hook** |

## Conservation

18 sites, each exactly once (the July audit's 12 = S1-S4, S6-S8, S10-S12, S16-S17 under its coarser organ
names; extensions = S5, S9, S13, S14, S15, S16b/S18 split). 11 conflicts tabled: 8 resolved, 1 resolved-by-
accident (S15/S4, no written rule), 2 missing (S18/S7 freeze path; mirror arbitration) + the unconsumed
`disagreement` flag. Dispatch lineage: `truth/archive/tape_20260714` (drafted; C-EVERY-SITE never sent —
grep-clean). Ruler: fb74c8b8 source chain v47→v45→v43→v41+v42→v36→v32/v35 + runner laws; defects cite
12d67c8a, 9ee14bf5, aa1cc301, b503e4ed, 639e8b19, a20e1a85, e177c2fb, bc0ce289, 653b7f13, 6bc169bf, aa884cc5.
