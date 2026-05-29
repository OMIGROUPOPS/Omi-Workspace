# v3 Exit Floor — Deployment Handoff (2026-05-29)

## TL;DR
The live executor now trades off `version_c_blueprint_v3.py`, a clean-slate
blueprint that **replaces `version_b_blueprint.py`**. Every TRADE cell is gated
on **own-tape realized EV > 0** (the binding floor). `maker_bid_offset = 0`
(taker entry) is the **intentional conservative floor** — Part 2 (entry
discount) layers on top later and only loosens exit requirements / lifts EV.

Ready for tomorrow's games.

## Why version_b was replaced (not extended)
`version_b_blueprint.py` was built on the pre-late-May-2026 broken foundation.
Validated wrong: **40/41 cells had the wrong `exit_target`**, 12 cells held
that should have exited, 12 were wrongly skipped. The foundation was only fixed
in late May 2026, so the old blueprint is retired entirely.

## What changed in the wiring
- `tennis_v5.py` line ~54: import switched
  `from version_b_blueprint import (...)` → `from version_c_blueprint_v3 import (...)`.
  Same three symbols: `DEPLOYMENT`, `get_strategy`, `use_blended_target`.
- `version_c_blueprint_v3.py` is a true **drop-in**: same `(CATEGORY, direction, lo, hi)`
  key schema, same `get_strategy(category, side, entry_price)` and
  `use_blended_target(...)` API the bot already calls.
- Every cell now also carries `in_sample_daily_pnl` (mapped to `own_ev`) so the
  dual-mode primary-side tiebreaker in `tennis_v5.py` works unchanged — the
  stronger side wins primary by its true own-tape edge.
- `use_blended_target` returns **False** for all cells on the floor: the
  blended-average auto-sell is an entry-side (Part 2) enhancement; the exit
  floor never assumes it.

## The blueprint
- **56 cells: 51 TRADE / 5 SKIP** (4 categories × 14 tiers).
- **24 re-opened** (v3 profitable on own tape, old blueprint had skipped).
- **2 closed** — own-tape negative even at best exit:
  - `('ATP_CHALL','leader',80,84)` own_ev = -0.46 (96–97% hit, but +1c capture
    doesn't cover the 1c Kalshi fee + occasional upset)
  - `('WTA_CHALL','leader',60,64)` own_ev = -0.37
- All 5 SKIP cells are expensive challenger favorites — non-profitable
  standalone, but flagged for "grab at discount" in Part 2.

### Per-cell fields the bot reads
`entry_lo/hi, dca_drop, exit_target` (auto-sell at entry+X; `None` = hold to
settle), `entry_size` (0 = SKIP), `dca_size, mode` (leader=favorite /
underdog=longshot), `maker_bid_offset` (0 = taker, the floor).

### Context fields (not acted on, for analysis)
`own_ev / own_hit / own_n` = the BINDING floor (own band's own tapes).
`pooled_band_ev / pooled_hit` = pooled-surface context (mapping only — pooling
can enrich the map but can NEVER flip an own-tape-negative band into a trade).
`source = 'v3_own_tape_floor_2026-05-29'`.

## Regeneration
`python3 analysis/gen_deployment_v3.py` → rewrites `version_c_blueprint_v3.py`.
Generator gates viability on `own_tape_best(df, lo, hi)` (sweeps exit X over the
band's own tapes, argmax realized EV/N). Viable = own_ev > 0. `exit_target` =
own-tape argmax X (or `None` if hold-to-settle beats every early exit).

## Validation run (all green)
- Imports OK, 56 cells, correct 4-tuple key schema, all required fields present.
- **0 own-tape-negative TRADE cells.**
- Deep underdog exits hold: WTA_CHALL underdog 10–14 = +7.41 EV/N (exit 83),
  WTA_MAIN underdog 15–19 = +7.25 EV/N (exit 79).
- `tennis_v5.py` full runtime import OK; `get_strategy` resolves correctly.

## Deploy notes
- CC-on-Cursor: codebase picks this up from `main` (push below).
- CC-on-app handles the VPS deploy.
- `BABY_SIZING_MODE = True` is still set in `tennis_v5.py` (10/5 sizing,
  bounded-risk validation on real matches). Flip to `False` for full blueprint
  sizing after live validation — unchanged from before, your call.

## Next (Part 2 — entries / discount)
Set `maker_bid_offset` per cell from T-4h→T-20 drift data. Every dollar of entry
discount lifts EV and loosens the exit requirement vs this floor.
