# live_v4 registry — v1 close (every candidate walked)

Analysis seat only. Descriptive. Read-only. Closes the v0 draft (b40cb540): all
442 `THRESHOLD_CANDIDATE` literals are walked to a terminal tag with a reason each,
and the borderline config owners get PROPOSED fates. Rows in
`LIVE_V4_REGISTRY_V1.csv`; summary in `LIVE_V4_REGISTRY_V1_SUMMARY.json`. The v0
summary carries the `SUPERSEDED_BY` stamp.

## Method

Each candidate literal was classified by reading its `live_v4.py` line and
neighbors through ordered, auditable rules: docstring/comment prose → NON_DECISION;
mechanics (index, range, pages, version, ttl, retry, unit-conversion) →
NON_DECISION; existence/sign guards (compare to 0) → NON_DECISION; structural
Kalshi price-domain bounds (1..99/100) → NON_DECISION; Plex staircase / par /
five-contract context → KEEP+AUTHORIZED; entry-pricing keywords (aim, cohort,
depth, verdict, sibling, staircase-entry, fav/dog, the `_pa9`/`_cp9` ATLAS aim
vars) → SUPERSEDED_BY_PRICER; residual → KEEP+ORPHAN. **Every row carries its
reason** — this is an automated first pass, operator-auditable via the reason
column, not a hand ruling of all 800.

## Conservation — 800 rows, zero CANDIDATE

| terminal tag | rows |
|---|---:|
| NON_DECISION | 443 |
| SUPERSEDED_BY_PRICER | 143 |
| BOOT_GATE | 77 |
| **KEEP+ORPHAN** | **71** |
| KEEP (execution flags, not thresholds) | 64 |
| KEEP+AUTHORIZED | 2 |
| **TOTAL** | **800** |

**THRESHOLD_CANDIDATE remaining: 0.** The 442 walk landed as: **NON_DECISION 331 ·
KEEP+ORPHAN 67 · SUPERSEDED_BY_PRICER 43 · KEEP+AUTHORIZED 1** (the other tag rows
are the 191 config knobs + 52 loaders + hand rows from v0).

## KEEP+ORPHAN — 71 findings (tuned live-execution numbers, no ruling)

The standing findings list. Representative literals (all live-execution thresholds
with no located ruling):

| site | literal | line |
|---|---|---|
| `live_v4.py:144` | `> 20` | `DEAD_SPREAD_THRESHOLD = 20  # don't post if spread > 20c` |
| `live_v4.py:10965` / `:10972` / `:14205` | `<= 2` | book-quality spread gate (`spread <= 2`) |
| `live_v4.py:10924` | `> 2` | last-trade-vs-mid divergence gate (2c) |
| `live_v4.py:12434` | `<= -8` | delta gate (−8c) |
| `live_v4.py:10950` | `< 600` | book-age staleness (600s) |
| `live_v4.py:14203` | `955..965` | anchor clock window (10s wide) |
| `live_v4.py:10107` | `5..95` | tradable-ask margin (5/95, not the structural 1/99) |
| `live_v4.py:14650` / `:16665` | `>= 2` | reentry/cycle-count gates |
| `live_v4.py:14937` / `:15043` / `:16552` | `>= 1.0` / `< 1.0` | hold-rule / coverage thresholds |

Plus the 4 hand-verified constants carried from v0: `exit_rule_for` fallback
`(15,"exit")`, `gun_divergence_move_cents=10`, `reality_divergence_cents=25`,
`ROUTING_SWEEP_INTERVAL=60`. **The book-quality `spread<=2` gate and the named
`DEAD_SPREAD_THRESHOLD=20` are the most consequential — they decide whether the
engine posts at all — and neither has a ruling.**

## SUPERSEDED_BY_PRICER — 143 (43 newly walked)

Entry-pricing literals the pricer's floor/verdict/anchor/sibling surface replaces:
the ATLAS aim clamps (`_pa9 < 5`, `> 95`, `>= 50` fav/dog regime splits), cohort
thinness (`n < 8`), depth-trend, join/held level checks, `combined_goal - entry <
5`, and the reaim/repost paths. Replacing surface: the pricer registry (3ff1b038)
rows for FLOOR / VERDICT / ANCHOR / SIBLING_PAIR.

## KEEP+AUTHORIZED — 2

`combined_goal=97` (par law) and the one literal par check that survived the
price-domain filter. Most 97/99/100 literals are structural price bounds
(NON_DECISION), not the tunable par goal.

## Borderline owners — PROPOSED fates (operator to confirm)

| knob | proposed fate |
|---|---|
| `completion_reprice`, `completion_live_enabled`, `completion_all_cells` | **SUPERSEDED_BY_PRICER** — the L9 completion layer the pricer owns |
| `completion_combined_ceiling` | **KEEP+AUTHORIZED** — par-law 100 execution guard |
| `completion_cells_path` | **BOOT_GATE** — loader; table superseded by the pricer completion surface |
| `complete_cross_enabled`, `completion_shadow_enabled` | **KEEP** — emergency cross / shadow, execution safety |
| `window_truth_live` | **SUPERSEDED_BY_PRICER** — window-truth reaim is an entry-aim organ |
| shadow organs (`aim_shadow`, `live_aim_shadow_enabled`, `os_shadow_enabled`, `composer/guidebook/trendpath_shadow_enabled`, `per_match_clock_shadow`, `scale_gun_shadow`, `percat_gun_shadow_enabled`) | **KEEP** — inert observability |

All 17 marked PROPOSED in the CSV, pending operator confirmation of surface
ownership post-cutover.

## Reading

The cutover checklist is now concrete: **143 SUPERSEDED** knobs the pricer retires,
**77 BOOT_GATE** rows (led by the exit-surface default → superseded spike-map),
**71 KEEP+ORPHAN** tuned execution numbers to ratify or replace, and **443
NON_DECISION** literals set aside with a stated reason. The single most actionable
pair remains the exit surface (BOOT_GATE) and its ORPHAN 15c fallback; the newest
finding is the un-ruled book-quality spread gates (`spread<=2`, `>20`) that gate
posting itself. Every classification is auditable in the reason column; the
automated pass is a first draft the operator can demote or promote row by row.

## Artifacts

`LIVE_V4_REGISTRY_V1.csv` (800 rows, 0 candidates, reason per row) and
`LIVE_V4_REGISTRY_V1_SUMMARY.json`. Supersede-stamp on `LIVE_V4_REGISTRY_SUMMARY.json` (v0).
