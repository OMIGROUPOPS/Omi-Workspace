# C-STAIRCASE SHIP-2 — caller contract for the ATP_MAIN staircase (Path A, FINAL)

**Status:** propose-only (scratch). Plex ratified **Path A** (compute D live; Path B — read CSV
`D@T-*` — rejected). Bot stays live on its prior code; no commit, no restart until ratified.

## Path A caller (`_staircase_bid`, ATP_MAIN ONLY)
1. Read `final_target` (int) for the leg's cell from the sealed `docs/policy/range_final_ATP_MAIN.csv`.
2. Read `frac2(t)` from the sealed `docs/policy/range_final_walk_schedule.json` via `_frac2`, whose
   body is **copied byte-for-byte from `abort_validation.py:20-22`** (the `min(c, key=lambda x: x[0])`
   held-step lookup — the only float-precision surface; not rewritten).
3. `D = max(1, int(round(1 + (final_target − 1) · frac2(t))))` — `int(round(...))` is the **ONE and
   ONLY** rounding site, == `abort_validation.py:58`.
4. Pass `(anchor, D, best_ask)` as ints to `_staircase_target` (Ship 1, 77fd9fa); use its returned bid.
5. **NEVER read/write the CSV `D@T-*` columns** (not the validated walk — see seal §7 addendum).
6. **ATP_MAIN ONLY.** WTA_MAIN / ATP_CHALL / WTA_CHALL failed their bars → stay on `_join_target`
   (degenerate join), byte-identical. Gate is `if cat == "ATP_MAIN"` at the placement site (4553).
   Engagement (`engagement_wave1`), completion (`_reprice_target`), fallback — untouched.

## FULL WALK (Plex ruled A) — the recast walks D up the knots against a FIXED anchor
The per-cycle re-quote in `_v4_move_repost` IS wired for staircase legs (7 Plex risks):
1. **Recast gate on `staircase_ref` change**, not the 5c mid-move gate: `live = staircase_anchor − D(t)`;
   `if live == staircase_ref: return`. Fires iff D crossed a knot (~8 reposts/leg max).
2. **Anchor immutable:** `target = pos.staircase_anchor − D(t)`, never `current_price − D(t)`.
3. **Cell immutable:** `final_target` keyed on `pos.staircase_cell`, never `regime_lookup(current_price)`.
4. **D:** `max(1, int(round(1 + (final_target−1)·frac2(t))))`, `frac2` byte-for-byte from
   abort_validation.py:20-22, passed to `_staircase_target` (77fd9fa).
5. **`reference_source="staircase"`** routed BEFORE the join_bid branch; `intended_join=False`.
6. **Restart survival:** `staircase_anchor`/`cell`/`ref` serialized sparse-when-set in save (5077+) +
   load (Position ctor), matching the da9f6ac C-JOIN-TRIAL pattern.
7. **New `Position` fields:** `staircase_anchor`, `staircase_cell`, `staircase_ref`, set once at placement.

Tests prove it walks: D monotone non-increasing as t→0; D **constant within each knot interval**
(held-step, not interpolated — `D(195)==D(205)`); recast target moves **only** on a knot cross, never
on a mid move; save→load preserves the 3 fields and a restored leg recomputes the identical target.

## Tests (gates)
- GATE 1: seal §7 addendum (this doc's ruling, atomic).
- GATE 2: this contract; mirrored in `_staircase_bid` docstring.
- GATE 3: `tests/test_staircase_ship2.py` — held-between-knots parity, 5 boundary t.
- GATE 4: `tests/test_dat_guard.py` — no `D@T` in `*.py` outside `build_range_final.py`.
