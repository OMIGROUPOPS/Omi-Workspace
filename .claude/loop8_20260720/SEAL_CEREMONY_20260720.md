# THE JUNE CEREMONY, HELD 2026-07-20 — SPLIT-GAUGE SEAL: **NO MEMBERS**

The operator's 07-20 ruling split the gauges per pair class and ordered the
ceremony for what clears. The week widen (P1, `WEEK_WIDEN.md`, commit
`cf9980e5`) is the gate record: **nothing cleared its own bar.** The ceremony
is held anyway, because the June form requires the outcome written even when
the table seats no one — an empty seal ON THE RECORD is what keeps a later
seal honest.

## The verdicts that gate this ceremony (per class, its own bar)
- **FLAT-FLAT dual-divot (the Vukic/Gea crop)** vs the 75% both-legs-negative
  bar: **BELOW — UNSEALED.** 7 duals / 50 pairs, both-neg 14%; virgin days
  0/3. The 24-hour exam's 40% carrier was small-n. The catch tables DO buy
  the cheap tiers (6/7 duals ≤93) — priced, on the shelf, not sealed.
- **MIRROR (the seesaw crop)** vs the combined gauge (pair combined-delta ≤ 0
  / sub-par combined cost; loop-5 frame, PASS = duals ≥ 10 AND median pair
  delta < 0): **FAIL — UNSEALED.** 66 duals, combD≤0 14% vs loop-5's 73%,
  medPairD +11, 59/66 over par. The weakening leg's destination cast
  (net_med + 2¢, not-too-deep as ruled) fills 131/131 at medD +14 — too
  shallow out-of-sample; the violent-faller REFUSE law's knife cuts from the
  shallow side too.
- **Riser divot-during-climb**: best per-leg arm of the campaign again
  (72 fills, neg 58%, medD −7.5) — a LEG truth, not a PAIR truth; no per-leg
  seal exists in this ceremony's charter.

## What seals: NOTHING. What stands, unchanged:
- `state/entry_tables_sealed_v1.json` sha256 `c0c29e54…` (Stage-5 amendment,
  07-18): SEALED 2 / REFUSE 5 / silent 29 — **untouched by this ceremony.**
- The violent-faller REFUSE law · floor 1,500 · W1-only · holdout discipline.
- **WHEN-FLAT: NOT EXERCISED.** No steering config flips in this ceremony.
  The only engine deltas riding this gate are read-side (the cascade) and
  safety (the teeth) — neither touches an aim, an offset, or a cast.

## Input lineage (hashes at ceremony, VPS state/)
- divot_tables_v2.json     `56b3bb469b7030ea…` (loop-8 P2 build, 8,173 legs /
  25 bands both sides, corpus-deep store)
- band_map_v1.json         `caf255a283bbb32f…` (Stage 1, unchanged since seal)
- drift_surfaces_v1.json   `aeac847d26c1421c…` (Stage 2 P1, unchanged)
- entry_tables_sealed_v1.json `c0c29e54792e2f49…` (Stage-5 amended seal, stands)
- Campaign lineage: LOOP 5 (delta frame, holdout-pass 73%) → LOOP 6 (schedules,
  honest negative) → LOOP 7 (destination frame, honest negative) → LOOP 8
  (divot v2 + 24h exam, 5 laps) → **WEEK WIDEN (split gauges, honest negative
  both classes)**. Five frames, one wall: the pair mirror's arithmetic.

## The wire that DOES go live (read-side only, the ⑮ precedent)
`_band_cascade_pass` (live_v4.py, 60s cadence, `band_cascade_read`
config-gated, default on):
- **band_call at birth** — ≤60s after conception (sampled cadence, named in
  the line); features = (anchor = window-open ref | first-seen, net, dip)
  from the live tape; recognition h6 cell at purity ≥ 0.5, else the default
  flat band — the loop-5 convention, verbatim.
- **band_recall** — whenever the unfolding window changes the call (cap 12
  lines per leg).
- **pair_class_read** — flat_flat / mirror / neither at the lap-5 ±5¢ net
  crossings, once per class change per event, each line naming the gauge
  that WOULD judge it and the law: *read-side only; nothing sealed 07-20*.
Aims, offsets, casts, refusals: untouched. The cascade is the instrument the
next campaign reads — it steers nothing until a class clears its bar and a
ceremony with members is held.

## Acceptance walk
One real game, entered by the engine under standing (unchanged) policy, with
the cascade's lines printed — band named at birth, class named, both legs'
reasoning — appended below after the gate deploy.

## Countersign
Seat: CC (Fable 5), split-gauge dispatch P2 C50. The operator's read of this
document is the countersign; an objection reopens nothing silently — the next
seal needs a class that clears and a new ceremony.

## AMENDMENT — THE COMBINED-PRIMARY RULING (2026-07-20 PM, same ceremony, the table seats its member)

The operator re-ruled the gauges: **combined-vs-par is the pass/fail gauge for
BOTH classes** (sub-par ≤97 = pass; tiers ≤93/≤95/≤97 reported; 98–100 and
>100 reported apart); **dual-negative demotes to the standing MASTERY METER**
— reported per class/band nightly, never pass/fail — the measure of judging
both sides vs riding one. Re-scored from the banked week
(`WEEK_RESCORE_COMBINED.md`):

- **FLAT-FLAT DUAL-DIVOT: CLEARS — SEALED.** 7/7 duals sub-par (6 ≤93,
  1 ≤95), 100% in both eras and every cat with duals, medPairD −10.
  Completion 14% of class pairs. Mastery meter reads 14% dual-neg — the
  drill gap, on the record, not a bar.
- **MIRROR: REFUSE.** 0/66 sub-par, both eras. The named miss is the fader
  leg's destination read (the too-shallow class; 131/131 fills @ medD +14
  the exhibit). **The continuing drill behind the seal targets exactly this
  read; its progress is graded on the mastery meter.**
- **NEITHER: REFUSE.** 9/26 (35%); counted apart, class unnamed by the
  ruling; the WTA_MAIN band-pair life filed as intake.

### The sealed object (new member)
- `state/pair_policies_sealed_v1.json`
  sha256 `b2f0b670f70aabe3fbfef9092c0b227334e00da2ecbd51e9235204158daf7c44`
- 25 band rows (big-4, depth = divot-v2 dip_p90, frozen at seal), consumed
  ONLY where the cascade reads the pair FLAT_FLAT; mirror/neither carry
  REFUSE receipts inside the object itself.
- Frame note, named: the engine's aim machinery prices offsets against the
  last-traded anchor; the catch tables price against the rolling 30-min
  median. For a flat-classed leg (|net| < 5 by construction) anchor ≈ median;
  the repost machinery re-anchors on evidence. The approximation is declared,
  not hidden.

### WHEN-FLAT — EXERCISED at this amendment
- `pair_class_steer_enabled: true` + `band_cascade_read: true` in
  `config/deploy_v5_live.json`; consumer = the DUAL-DIVOT steer in
  `_v4_entry_anchor` (`dual_divot_steer` log line, cell label
  `DUAL-DIVOT:<band>`). `expiration_wire_enabled` stays FALSE — dark until
  the tennis retest verdict, unchanged.
- Rides its own full gate deploy (lint + smoke + outcome proof + two-file
  law), sequenced after the P2+P3 deploy.

### Standing drills named at the seal
1. **The fader destination read** (mirror class): refit the cast depth
   against realized terminals (loop-7 net-quantile family vs the net_med+2
   shallow rendering) — graded on the MASTERY METER per class/band nightly.
2. **Completion rate** (volume drill): sub-par duals per slate — week
   baseline 16/200 = 8.0% (≤93: 4.5%) — the number to drill up without
   surrendering the sub-par law.

## THE ACCEPTANCE WALK — Noguchi vs Shick (ATP Challenger, 2026-07-20), walked live under the seal

**The game, in the operator's language:** Rio Noguchi against Braden Shick,
Challenger draw. The engine took the Noguchi side at 11:27 AM under standing
law — resting buy 5 @49¢, `path_aim`, conviction voice 0.53 — and the Shick
leg filled earlier and rides its band exit at 59¢. Real game, real book, real
positions.

**The cascade's reasoning, printed from the lines (first pass after the seal
boot, 02:52:29 PM ET):**
- `band_call` at birth, Noguchi leg: **band ATP_CHALL-B4, direction FLAT,
  recognition TRUE** (purity ≥ 0.5 — a genuine recognition, not the default),
  anchor 55¢, net 0, dip 0.
- `band_call` at birth, Shick leg: **band ATP_CHALL-B4, FLAT, recognition
  TRUE**, anchor 47¢, net 0, dip 0.
- `pair_class_read`: **FLAT_FLAT — the sealed class.** Neither leg has
  crossed ±5¢ of its anchor; the pair is the Vukic/Gea shape the ceremony
  seats.
- The sealed row this class consults: `ATP_CHALL-B4 depth_p90 = 10¢`
  (1,694 windows behind it). The fish, when the steer prices the next aim
  event on these legs: Noguchi ≈ 45¢, Shick ≈ 37¢ — combined ≈ 82,
  **sub-par by construction** if both catch. Cell label on the line:
  `DUAL-DIVOT:ATP_CHALL-B4`.
- Judged, per the ruling, on **combined-vs-par** (sub-par ≤97 = pass);
  dual-negative reported on the mastery meter, never as a bar.

**Named defect, filed not hidden:** the `pair_class_read` log line still
stamps flat_flat's gauge as `75pct-both-neg` — a frame superseded by the
PM ruling. One-line label fix rides the next gate (BOARD rider); the
policy consumer reads the sealed object, not the label.

**Watch:** the first `dual_divot_steer` line (fires on the next
conception/repost of a flat-flat-classed leg) — count vs flat-flat
conceptions is the standing coverage watch.

## WALK AMENDMENT — THE SHICK HOLD, GRADED AS THE MISS IT IS (operator defect dispatch, 07-20 PM)

The walk above presented the sealed fish (Shick ≈37¢) and OMITTED that the
book already HELD the Shick leg — 5 shares at 48¢, placed by the legacy
`path_aim` authority at 09:59 AM (orientation_park_swap 09:58, knob
`orientation_swap_min_conviction`), filled 01:29 PM via `manage_cancel_race`
— a weakening leg coming down through a reference-priced bid. **Basis 48 vs
sealed fish 37 = +11¢ overpay per share, graded F on the sealed class's own
number.** Both placement and fill pre-date the seal boot (03:08 PM) — the
seal was not violated in time; the walk was defective in FORM: it presented
a game without reconciling its positions.

The book-wide reconciliation (`SEAL_BOOK_RECON.md`) names all three
overpays (Shick +11¢ · Ilagan +10¢ · Trotter +3¢, panel-flagged red) and
the eight LEGACY-owned legs. The two laws this defect founded —
ONE-AUTHORITY and WALK-RECONCILES-THE-BOOK — are vaulted verbatim at
`.claude/rulings/RULING_ONE_AUTHORITY.md` and enforced in code at the
chokepoint + the 60s audit, this same gate.
