# The live_v4 registry + cutover first draft

Analysis seat only. Descriptive. Read-only; **no live mutation**. The live engine's
own decision surface — the counterpart to the pricer registry at 3ff1b038. Machine
rows in `LIVE_V4_REGISTRY.csv`; summary in `LIVE_V4_REGISTRY_SUMMARY.json`.

## Sweep method (stated)

Every `self.config.get(key, default)` call; every numeric literal in a comparison
operator (`>= <= == != > <`); every fitted/corpus table loader in `live_v4.py`
(18,052 lines). Each row: `site file:line | meaning | inputs | value/default |
cutover tag | authorizing ruling or ORPHAN`. **Per-row tags are a heuristic FIRST
DRAFT** (keyword-based, made while in the file); the headline rows are hand-verified
with line numbers.

## Conservation

**800 total rows** — swept: **191 `config.get` · 554 comparison literals · 52
loaders** (plus hand-verified headline rows).

| cutover tag | rows |
|---|---:|
| THRESHOLD_CANDIDATE (numeric literal, not yet ruling-checked) | 442 |
| NON_DECISION (index / page / version / ttl literal) | 112 |
| SUPERSEDED_BY_PRICER | 100 |
| BOOT_GATE | 78 |
| KEEP | 68 |
| **TOTAL** | **800** |

**ORPHAN (hand-verified tuned numbers with no ruling): 4.**

## Cutover tags

- **SUPERSEDED_BY_PRICER (100)** — the entry/aim/floor/verdict/anchor/sibling/
  staircase decision surface the shape-pricer registry (3ff1b038) replaces:
  `orientation_live`, `cohort_steer_*`, `pair_class_steer_enabled`,
  `selector_drop_enforce`, `depth_aware_floor*`, `discovery_floor*`,
  `sanctioned_walk_fitted`, `window_truth_live`, `staircase_hold_*`,
  `premarket_walk_cap*`, `aim_*`, `entry_table_*`, `completion_*`, and the shadow
  organs. These are the knobs the pricer's floor/verdict/sibling gates make moot.
- **BOOT_GATE (78)** — restart-checklist implicated: the exit-table loader and its
  fallback, config `get` defaults, corpus/table loaders, and anything exposed to
  the VPS's uncommitted source/config drift.
- **KEEP (68)** — live-execution machinery the pricer does not replace: order
  transport, fill poll (`fills_bulk_*`, `positions_max_pages`, `gun_poll_sec`),
  exit stamping, clocks (`per_match_clock`, `atlas_clock_contract_v2`,
  `min_minutes_before_start`), the gun, admission (`itf_min_recent_vol_usd`).

## Headline findings (hand-verified)

| site | knob | value | tag | ruling |
|---|---|---|---|---|
| `live_v4.py:5130` | **exit_table_dir** | default `"data/durable/spike_volatility_map/"` | **BOOT_GATE** | **SUPERSEDED** — BAND_AUTHORITY_RECEIPT (e59aa4cc) retires spike_volatility_map for gated-optima, yet the live default still loads the **retired** exit surface unless config overrides. Restart / VPS-drift hazard. |
| `live_v4.py:5478` | **exit_rule_for fallback** | `(band_x=15, "exit")` | **BOOT_GATE** | **ORPHAN** — a 15-cent fallback exit, tuned, no ruling; hit whenever the exit table lacks a cell (a coverage gap). |
| `live_v4.py:1610` | gun_divergence_move_cents | default 10 | KEEP | **ORPHAN** — 10c gun trigger, unruled. |
| `live_v4.py:14904` | reality_divergence_cents | default 25 | KEEP | **ORPHAN** — 25c telemetry bound, unruled. |
| `live_v4.py:150` | ROUTING_SWEEP_INTERVAL | 60 s | KEEP | **ORPHAN** — 60s backstop cadence, unruled (low-risk). |
| `live_v4.py:1797` | combined_goal | default 97 | KEEP | **AUTHORIZED** — par law (≤97 pass). |
| `live_v4.py:183` | STAIRCASE_ABORT_WINDOW | 20 | SUPERSEDED | **AUTHORIZED** — Plex-ratified staircase BAR gates; staircase entry is replaced by the pricer. |

**The load-bearing finding is the exit surface: the live engine still defaults to
the superseded spike-map exit bands (BOOT_GATE), and its fallback exit is an ORPHAN
15c.** Both belong at the top of the restart checklist. The other three ORPHAN
constants are low-risk execution numbers.

## What this draft does NOT yet do

The 442 `THRESHOLD_CANDIDATE` literals are swept and line-located but **not
individually ruling-checked** — that per-literal audit is the v1 close. Only 4
tuned constants are hand-verified as ORPHAN so far; the true count is a lower bound
until the 442 are walked. The per-row cutover tags on config knobs are a keyword
first draft: several SUPERSEDED_BY_PRICER vs KEEP calls (e.g. `completion_*`,
`window_truth_live`, the shadow organs) need the operator's confirmation of which
surface owns them post-cutover. Untagged findings did not appear only because the
heuristic assigned every config key a provisional fate — those assignments are the
cutover's proposal, not its ruling.

## Supersede discipline

This registry does not modify or delete any prior artifact; it references the
pricer registry (3ff1b038) as the replacement surface for the SUPERSEDED_BY_PRICER
rows and the BAND_AUTHORITY_RECEIPT for the exit-surface supersession.

## Artifacts

`LIVE_V4_REGISTRY.csv` (800 rows: kind, site file:line, knob, meaning, inputs,
value/default, cutover tag, ruling/ORPHAN) and `LIVE_V4_REGISTRY_SUMMARY.json`
(sweep method, conservation, headline findings, tag legend).
