# live_v3.py → Path B v4 deployable spec — capability build map for CC

**Date:** 2026-05-24 · **Read-only static analysis.** live_v3.py (deployed, post-Bug-4 commit `366d8aa`) vs `docs/bid_laying_policy_v1.md` Sections 2–7 (v4 deployable spec).
**Status legend:** PRESENT (works as v4 needs) · PARTIAL (infra exists, must adapt) · MISSING (build fresh).
**Risk flags:** 🟥 touches Bug 4 / settlement state · 🟧 touches paper-mode · 🟦 large routing rewrite.
Line refs are against the deployed live_v3.py and are ±a few lines.

> **Naming caution:** `deploy_v4_paper.json` is a *config generation* label, unrelated to "Path B v4". The deployed executor is the **FV-anchor A/B/C scenario** strategy, not v4.

---

## Summary table

| # | Capability (v4 spec) | Status | live_v3 location | What CC changes | Risk |
|---|---|---|---|---|---|
| 1 | T-4h / per-cell placement trigger | **PARTIAL** | `ENTRY_MAX_LEAD_SEC_BY_SERIES` 71–82; intel-window gate `routing_tick` ~2208 (`recommended_window_seconds`) | Add clock-based placement at the cell's `placement_minute` (T-240…T-60) relative to match-start; today it fires in a short pre-match intel window, not at a fixed pre-start offset | — |
| 2 | Cell = current Kalshi yes-price (NOT FV) | **PARTIAL** | `cell_lookup` 1095 (price→5c band, source-agnostic); fed by FV via `_resolve_anchor` 2122 → `routing_tick` ~2257 | Keep `cell_lookup`; swap its input from FV `anchor_value` to current Kalshi price read off the book at decision time | — |
| 3 | Load `per_regime_offsets_v2.csv` at startup | **MISSING** | none (0 refs); config `active_cells` read at 1100/940 | Add CSV→`dict[(category,regime)]→(placement_minute,offset)` at init. Map 10c regimes (`r05_14`…) onto the 5c `cell_lookup` bands (5c is finer — works) | — |
| 4 | `target_bid = current_price − regime_offset` (≥1c) | **MISSING** | entry price is `best_bid`/`best_ask` via scenarios 2286–2303 | Add the offset arithmetic + clamp. **Reusable: tennis_v5.py `maker_bid_offset` (636)** — same offset-applied-to-maker-bid shape | — |
| 5 | Posting branch: taker if `bid≥ask` else resting maker | **PARTIAL** | scenario branch 2284–2303 (`B_take`→ask, `A/C`→bid); `place_order` 1212 (`post_only`) | Replace FV-delta scenario selection with the spec's branch: `target_bid ≥ current_ask` → marketable taker (pay 1c); else resting maker at `target_bid`. `place_order`/`post_only` reusable | 🟦 |
| 6a | Resting bid refresh / cancel-repost | **PARTIAL** | `validate_resting_buys` 2469 (60s cadence cancel/repost + reprice to best_bid) | Adapt to maintain `target_bid` (not mid/anchor freshness). Cadence machinery reusable | — |
| 6b | Round-5 2-of-4 composite detector (vol burst + bilateral taker + BBO velocity + distortion) | **MISSING** | none in live_v3 | Build fresh. **Reusable components:** distortion/combined-price calc **arb_executor_ws.py ~628**; depth/BBO-velocity from **tennis_stb.py `capture_depth_snapshot` 854+**; volume/taker-flow from live_v3 `VolumeTracker` 370 + `book.last_trade`. No file has the assembled 2-of-4 — assemble from these | — |
| 6c | Pathological-spread guard (detector fires & `ask>target+5` → don't cross) | **MISSING** | none | Build with 6b | — |
| 7 | T-20m taker fallback (= atlas baseline) | **PARTIAL** | `validate_resting_buys` deadline-force-take ~2335 (currently T-16m) | Change deadline T-16m → **T-20m**; cross at current ask. Mechanism reusable | — |
| 8a | Atlas exit lookup `cell_id→descriptive_1c` | **MISSING** | bot uses config `exit_cents` (1786, 1811, 2798) | Load `{cat}_descriptive_1c.parquet`; lookup `best_exit_X` by `cell_id=round(anchor×100)`. (exit_cents→best_exit_X swap) | 🟥 |
| 8b | "exit at +X" with ≥250ct depth | **PARTIAL** | resting sell posted at `fill+exit_cents` 1786/1811; no depth gate | Use `best_exit_X`; optional ≥250ct depth qual. **Reusable: tennis_stb.py `capture_depth_snapshot`** | 🟥 |
| 8c | "hold to settlement" cells (51 cells; 26/90 in WTA_CHALL) | **MISSING** | `check_fills` 1682 **always** posts exit (1786/1811) | Add `rule=="hold"` skip → post NO exit, let Bug 4 settle. **Verify the held position is in a state `check_settlements`/`process_settlement` will close** | 🟥 |
| 9 | Paired-leg posting, both legs independent (B23) | **PRESENT (confirm)** | `identify_sides` 1528; per-ticker routing → each leg own `Position` | Architecture already treats legs as independent tickers (own resting→fallback→exit). Confirm both legs post; no atomic pairing/sizing coordination (atlas treats legs independently — acceptable) | — |
| 10 | Disable FV-anchor A/B/C routing | **REMOVE/flag** | `routing_tick` scenarios 2284–2303; `_resolve_anchor` 2122 (FV-sourced) | Retire scenarios behind a config flag (`executor_mode: v4` vs `fv_scenario`); replace anchor source per #2. Largest single change | 🟦 |
| 11 | Bug 4 settlement detection | **PRESENT** (`366d8aa`) | `_handle_ws_settlement` ~1404, `poll_settlements_rest` ~1929, `process_settlement` ~1973, `check_settlements` ~2062 | No change. **Caveat:** #8c hold-cells depend on Bug 4 to close — ensure hold-skip leaves position settleable | 🟥 |
| 12 | Paper-mode infra | **PRESENT** | `PaperApi` 520, `PaperFillSimulator` 427, `PaperPosition` 331, `dump/load_state` 771/784, `_PAPER_API` dispatch | Validate v5 against paper before live. Reconcile `PaperFillSimulator` fill semantics (book-cross + trade-print) with v4's marketable/resting/depth logic | 🟧 |
| 13 | Don't-break inventory | **PRESENT — preserve** | WS reconnect `_ws_reconnect` ~1354; tick/trade file writers (FD-leak history — watch); schedule `_load_schedule` 985 / `_match_event_to_schedule` 1004; REST safety-net `poll_settlements_rest` 1929; idempotent `process_settlement` 1973; persistence `_load_processed`/`_save_processed` 974/981 + `dump/load_state` | Rewrite must not disturb these | 🟥🟧 |

---

## Notes per capability

**1 / 7 — timing.** The bot already has match-start (schedule.json / premarket `match_start_ts`) and a deadline-take, but placement is *intel-window-gated*, not anchored to a per-cell `placement_minute`. **tennis_v5.py is the cleanest reuse**: `gate_open = est_start − ENTRY_BEFORE_START`, `gate_close = est_start + ENTRY_AFTER_START`, `earliest_entry_ts`/`latest_entry_ts` (lines 930–937, 1035–1050) — a clock-based maker-bid window. CC can lift that gating directly and set `gate_open = match_start − placement_minute·60`, fallback at T-20m.

**2 / 3 / 4 — cell + offset.** The deployable cell is the live Kalshi price bucket; `cell_lookup` already buckets any price to a 5c band, so only the input source changes (FV→Kalshi). The v2 CSV's 10c regimes map cleanly onto 5c bands. The offset arithmetic is new but trivial; tennis_v5's `maker_bid_offset` (636) is the same idea (an offset applied to a maker bid, negative for underdog deflation).

**6 — Round-5 detector is the biggest greenfield build.** It does **not** exist anywhere in live_v3, and `arb_executor_ws.py`'s "signals" are an **external OMI Edge API**, not the microstructure composite. Assemble the 2-of-4 from: volume-burst (VolumeTracker rolling counts), bilateral taker flow (taker_side mix), BBO velocity (Δmid over window — tennis_stb depth snapshots), distortion (combined yes+no >$1, arb_executor_ws ~628). Gate: fire & `ask≤target+5` → cross; fire & `ask>target+5` → hold (pathological-spread guard).

**8 — exit rewrite is the highest-risk (🟥) area.** The exit mechanism already posts `entry+X` (just sourced from config `exit_cents`), so 8a is a source swap. 8c (hold-to-settlement) is the real gap: `check_fills` has no "post no exit" path, and getting it wrong means a hold-cell position either (a) gets an unwanted exit order, or (b) never closes. The hold path **must** hand off cleanly to Bug 4 (`check_settlements`/`process_settlement`) — test this explicitly in paper mode. 51 cells need it, concentrated in WTA_CHALL (26/90).

**10 — the rewrite's structural core (🟦).** routing_tick's A/B/C scenario block + `_resolve_anchor` (FV) are what v4 replaces. Put them behind `executor_mode` so the proven FV path remains revertable. This is where #1/#2/#4/#5 all land.

**11 / 12 / 13 — preserve (🟥🟧).** Bug 4, paper infra, WS/schedule/persistence are validated and load-bearing. The rewrite is an *executor* swap; the scanner + settlement + paper scaffolding stay. Validate the whole v5 in paper mode (config `paper_mode:true`) before any live cutover, and confirm the hold-cell→Bug-4 handoff and the FD-leak-free tick logging both survive.

---

## Reusable-pattern index (so CC pulls rather than rebuilds)
- **Clock placement window** (#1, #7): `tennis_v5.py` lines 930–937, 1035–1050 (`gate_open`/`gate_close`, `earliest/latest_entry_ts`).
- **Maker bid offset arithmetic** (#4): `tennis_v5.py` line 636 (`maker_bid_offset`).
- **Depth snapshot / ≥250ct + BBO velocity** (#6b, #8b): `tennis_stb.py` `capture_depth_snapshot` (854, 924, 957, 1299, 1508).
- **Distortion / combined-price signal** (#6b): `arb_executor_ws.py` ~628 (combined yes+no, `profit = 100 − combined`).
- **Volume / taker-flow tracking** (#6b): live_v3 `VolumeTracker` line 370.
- **Order placement + post_only branch** (#5): live_v3 `place_order` 1212.
- **Deadline-take → T-20m fallback** (#7): live_v3 `validate_resting_buys` ~2335.

---
*Read-only static analysis. No code changes. Written to docs/handoffs/ (uncommitted — operator reviews/commits).*
