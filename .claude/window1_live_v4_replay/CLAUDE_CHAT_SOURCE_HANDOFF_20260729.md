# Claude Chat source handoff — Window 1 live-v4 replay

This is the public source index for the Window 1 work. The links below point at
the public `codex/window1-recognition-laps` branch. The operator handoff message
also supplies immutable links pinned to the commit containing this file.

## Raw files

- live OS: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/live_v4.py
- live configuration: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/config/deploy_v5_live.json
- trendpath builder: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/trendpath_build.py
- delta objective: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/window1_delta_objective.py
- five-game delta replay report builder: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/window1_five_game_delta_replay_report.py
- T2 target laps: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/window1_t2_target_laps.py
- unchanged-live-v4 replay shell: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/window1_live_v4_replay.py
- actual-bell refit builder: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/analysis/window1_actual_bell_refit.py
- actual-bell refit JSON, including all 48 cohort cells: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json
- delta ladder JSON: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/WINDOW1_DELTA_LADDER.json
- 804-game grid JSON: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_t2_iteration_history/WINDOW1_T2_GAME_GRID.json
- four-defect replay comparison: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/live_defects_20260729/LIVE_DEFECT_REPLAY.json
- HURBIG narrative: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/narratives/KXATPCHALLENGERMATCH-26JUL19HURBIG.md
- NIKVRB narrative: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/narratives/KXATPCHALLENGERMATCH-26JUL19NIKVRB.md
- LAJVAN narrative: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/narratives/KXATPMATCH-26JUL12LAJVAN.md
- BRAVED narrative: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/narratives/KXWTACHALLENGERMATCH-26JUL16BRAVED.md
- KORJIM narrative: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/delta_objective_20260729/narratives/KXWTAMATCH-26JUL20KORJIM.md
- Living Vault: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/docs/LIVING_VAULT.md
- Board: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/BOARD.md
- Model Registry: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/arb-executor/docs/MODEL_REGISTRY.md
- Shelf Census: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/shelf/SHELF_CENSUS.md
- observed-start database: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/vps_inputs_20260729/db/observed_starts.db
- VPS input manifest: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/vps_inputs_20260729/VPS_INPUT_MANIFEST.json
- tennis snapshot/writer report: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/vps_inputs_20260729/TENNIS_SNAPSHOT_AND_WRITER_REPORT.md
- tennis snapshot receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-recognition-laps/.claude/window1_live_v4_replay/vps_inputs_20260729/TENNIS_SNAPSHOT_RECEIPT.json

## Where the requested live paths actually live

There are not separate authority, selector, or fill-reconciliation modules.
They are methods of the live OS in `arb-executor/live_v4.py`. The builder only
fits the trendpath surfaces.

| Requested path | Actual source |
|---|---|
| Trendpath builder | `arb-executor/analysis/trendpath_build.py`; `contention_of` begins at line 298 |
| Live selector/contention read | `live_v4.py`; `_selector_verdict` begins at line 2884 |
| Authority chooser | `live_v4.py`; `_price_authority` begins at line 3954 |
| Authority enforcement when an order is placed | `live_v4.py`; the one-authority gate begins around line 5817 |
| Contention placement veto | `live_v4.py`; the `contention_drop_enforced` gate begins at line 11544 |
| Authority order-field contract and reconciliation sweep | `live_v4.py`; canonical `order_id`/`price` reads begin at line 14933 |
| Re-anchor path | `live_v4.py`; mismatch detection and `authority_reanchor` begin around line 15061 |
| Account fill-receipt poll | `live_v4.py`; `_poll_entry_fills_bulk` begins at line 9761 |
| Per-order fill fallback | `live_v4.py`; `check_fills` begins at line 9851 |
| Naked-fill adoption | `live_v4.py`; `_v4_reconcile_naked` begins at line 13767 |
| Full account reconciliation | `live_v4.py`; `reconcile` begins at line 15132 |

The four live repairs are controlled by these
`arb-executor/config/deploy_v5_live.json` keys:
`timing_axis_onset_relative`, `authority_order_contract_v2`,
`contention_drop_enforced`, and `bulk_fill_poll_enabled`. The comparison JSON
records the control, four single-repair profiles, and their combination on the
same five selected games.

## Result shapes

- `ACTUAL_BELL_REFIT.json` has 48 entries in `by_cohort_cell`, including every
  thin cell; 17 entries in `by_atlas_cell`; four category aggregates; and 466
  exact-bell leg rows. Its category/cell timing axis is T-minus actual bell.
- `WINDOW1_DELTA_LADDER.json` has the 804-game population contract, independent
  and strict-sequential ladders, 622 strict-sequential event rows, and the five
  selected events.
- `WINDOW1_T2_GAME_GRID.json` has exactly 804 rows in `games`, plus input
  receipts, units, scope, and view definitions.
- `LIVE_DEFECT_REPLAY.json` has the same five events under the control, each
  single live repair, and the combined repair profile.
- The five Markdown files in `narratives/` are the chronological readable
  replays for the five events selected by the delta ladder.

## Private/oversize database exclusion

`tennis.db` and its online snapshot are not in Git:

- source copy: 17,423,802,368 bytes
- verified online snapshot: 17,434,673,152 bytes
- snapshot SHA-256:
  `ade09fdc101267ac282c8194700ba188cd60aac4c554e4f38da02d14b5e8602c`

They exceed GitHub's file limit by two orders of magnitude and include live
account-state tables, so both files and their WAL/SHM companions remain
ignored. The public receipt and writer report above preserve the hash, source
mtime, snapshot mtime, free-space guard, WAL observations, and backup method.

The private snapshot contains these tables and field meanings:

- `kalshi_price_snapshots`: chronological market observations keyed by
  `(polled_at, ticker)`; `bid_cents`, `ask_cents`, and `last_cents` are prices;
  `event_ticker` joins pair legs; `commence_time` is the catalog schedule
  visible at that poll. Repeated rows can expose schedule changes, but this is
  not a purpose-built schedule-revision ledger.
- `observed_starts`: one first-in-play notice per Tennis Explorer match;
  `first_inplay_at` is when the collector first observed in-play, not a claimed
  official bell; `inserted_at` is persistence time; `kalshi_ticker` is the
  market join.
- `live_scores`: latest observed set/game/status state by Tennis Explorer match,
  with `last_updated`; it is observation state, not a transaction ledger.
- `book_prices`, `bookmaker_odds`, `betexplorer_staging`, and `edge_scores`:
  bookmaker/FV observations, source timestamps, odds/probabilities, and Kalshi
  joins used by dossier/fair-value reads.
- `historical_events`: event-level first/min/max/last summaries and time bounds;
  it is compressed history, not the tick-by-tick replay tape.
- `active_positions`, `matches`, and `dca_truth`: live position, completed
  trading, settlement, and DCA-accounting records. These are the principal
  privacy reason the full database is not public.
- `players` and `name_cache`: player metadata and cross-source name mappings.

The smaller `observed_starts.db` is public at the raw URL above. Its complete
schema is:

```sql
CREATE TABLE observed_starts (
    te_match_id TEXT PRIMARY KEY,
    player1 TEXT,
    player2 TEXT,
    kalshi_ticker TEXT,
    first_inplay_at TEXT,
    inserted_at TEXT
);
```

`first_inplay_at` means “the feed was first noticed in-play.” It must not be
silently relabeled as official actual start. `inserted_at` records when that
notice was written. The actual-bell refit keeps proxy-clock rows separate from
its exact-evidence fit population.
