# Pre-deploy execution-bug verification checklist — v4 bot, live ~9am ET 2026-05-25

**Compiled read-only** from LESSONS.md (207 entries, execution-side filtered), `git log --all` bug-fix commits, `docs/handoffs/*`, `bug4_brief.md` §11 risk register, and today's `live_v3_v4_inventory` + `tape_audit`. Each row = one execution-side bug class the v4 bot must demonstrate it handles during paper validation **before** live cutover.

**Tiers:** P0 = cannot deploy without paper-validated pass · P1 = deploy at own risk, monitor · P2 = known operational, accept.

> **v4-specific framing:** the deploy is an *executor* swap on a preserved scanner + Bug-4 settlement + paper scaffolding (per `live_v3_v4_inventory`). The highest-risk new interaction is the **hold-to-settlement skip (51 cells) handing off to Bug 4's chokepoint** — most P0s cluster there.

---

## P0 — cannot deploy without verification

| Bug class | Root cause | Fix commit | Verification test (paper, pass/fail unambiguous) |
|---|---|---|---|
| **Bug-4 settlement under v4 hold-skip** | Hold cells (51) post NO exit and rely solely on Bug 4 to close; a broken handoff = position never closes (phantom). | `366d8aa` (+brief `bf60e65`) | In paper, drive a hold-cell N (e.g. WTA_CHALL r25_34) through entry→match-end; verify **no exit order is posted**, the WS-lifecycle `settled`→`/markets` hop fires, `process_settlement` closes it, `paper_settled` emits with correct `realized_pnl_cents`, and the position leaves `paper_positions` net-open set. FAIL if any hold-cell position is still net-open after its settlement event. |
| **REST settlements poll gated OFF in paper** | `poll_settlements_rest` on real-account history would falsely settle paper positions. | `366d8aa` (bug4_brief §6.3, decision; B4-T9) | In paper, run a full main-loop tick window; assert `api_get` is **never** called with `/portfolio/settlements` and zero `settle_source==rest_poll` events. FAIL on any rest_poll in paper. |
| **Idempotent `process_settlement` / no double-fire** | WS + REST + BBO can all fire for one ticker; non-idempotent close double-books PnL. | `366d8aa` (B4-T2; tape_audit 0 double-fires) | Feed the same ticker a WS settle then a BBO threshold cross; assert exactly **one** `settled`/`paper_settled` event and one PnL booking. FAIL on ≥2. |
| **Hold-cell exit-skip wiring** | `check_fills` historically *always* posts exit at `fill+exit_cents`; v4 must skip for `rule=="hold"`. | NEW in v4 (inventory #8c, 🟥) | For a hold-cell fill, assert **no** `exit_posted`/`cell_exit_order_id` is set; for an exit-cell fill, assert exit posted at `entry+best_exit_X`. FAIL if a hold cell posts an exit or an exit cell doesn't. |
| **Fee accounting per execution mode** | 1¢ taker fee on marketable_taker + miss_fallback, **0 on resting maker**; misapplied fee corrupts net PnL. | `366d8aa`/bug4_brief §6.4; LESSONS A41 | Run one of each mode in paper; assert fee = 1¢/ct on marketable + fallback entries, 0 on resting fills. FAIL on fee charged to a resting maker fill or omitted on a taker. |
| **Partial-exit realized-PnL (double-entry)** | Partial sell then settle: incremental formula undercounts (buy10@40, sell5@50, settle5@99 → must be 345 not 295). | bug4_brief v3 §6.4 (in `366d8aa`); B4-T8b/T11 | Replay the worked fixture in paper; assert `realized_pnl_cents==345` and that it **round-trips through dump/load_state**. FAIL on 295 or drift after restart. |
| **Paper-vs-live fill-semantics parity** | If `PaperFillSimulator` (book-cross + trade-print) diverges from v4's marketable/resting/depth logic, paper validation is meaningless. | PaperApi/PaperFillSimulator (live_v3:427/520) | Drive identical book sequences; assert paper marketable-taker triggers iff `target_bid≥ask` at placement and resting fills iff a `taker_side=="no"` print ≤ bid. FAIL if paper fills where live wouldn't (or vice-versa) on the same tape. |
| **Cell-id / regime boundary classification** | Cell = `round(anchor×100)`; wrong bucket → wrong exit-X/offset (A10/A11: cell disagrees fill-vs-bucket). Divergent-X neighbors (37/38) must not collapse. | LESSONS A10/A11; adaptive-banding 37/38 split | Feed anchors at band edges (e.g. 34/35, 37/38); assert the looked-up exit-X matches the per-cell table and that 37/38-type divergent neighbors get their own X. FAIL on a boundary mis-bucket. |

---

## P1 — deploy at own risk, monitor live

| Bug class | Root cause | Fix commit | Verification test |
|---|---|---|---|
| **WS reconnect during resting-bid mgmt** | 43 reconnects/10h today, all auto-recovered — but never tested with v4's resting bids mid-management. | `_ws_reconnect` (live_v3:1354); no bug-fix commit | In paper, force a WS drop while a resting bid is live; on resubscribe assert the bid/position state machine resumes without double-posting or stranded orders, and Kalshi snapshot re-pull restores book. Monitor reconnect count live. |
| **FD exhaustion** | Historical `Too many open files: state/live_v3_processed.json` on the old paper bot; **no fix commit landed**. | none (open operational) | Run paper ≥12h; monitor `lsof` FD count for the bot PID — must stay flat, not climb. Today's fresh session: 0 so far. |
| **Premarket-window miss / late discovery** | NIKBER +36min late (2/236 today); leg discovered after its placement window. | — (tape_audit) | Verify a late-discovered leg falls back to the T-20m taker (atlas baseline), not a stranded/garbage entry. Bounded risk (worst case = baseline). |
| **Schedule.json staleness / commence detection** | Lifecycle ts don't track match start (C19); tier-3 commence calibration defect (F35); `NO_RELIABLE_COMMENCE_SOURCE` frequent in logs. | C19; F35 (`19fdd5a`); A35 | Verify match-start used is the schedule `start_time` (freshness-checked), and a leg with no reliable commence is skipped/baseline-only, not mis-windowed. Monitor schedule age. |
| **Timestamp parse (RFC3339 / epoch / µs)** | Recurring class: µs-vs-ns gives 1000× error / silent-1970; Bug4 parses RFC3339 `settled_time` + epoch `settled_ts`. | `43ae049`, `4c100f7`, `a722193` | Assert settled_time parses to correct epoch (not 1970, not 1000×); monitor `ws_settle_value_unparseable` / `rest_settlement_unknown_result` = 0. |
| **Order-state staleness (filled, unnoticed)** | Resting bid fills but bot's poll misses it → acts on stale state. | `check_fills` (live_v3:1682) | Verify `check_fills` reconciles a filled resting order within one cadence and `reconcile` posts the exit for any naked filled position. |
| **Partial entry fill (10ct fills 7ct)** | Real Kalshi can partially fill; `count_fp` = actual qty (A30). **No dedicated fix commit** for partial *entry* fill (only partial *exit* P&L). | A30 (related) | Verify a 7/10 entry fill records `entry_qty=7`, sizes the exit to 7, and doesn't re-post the missing 3 as a duplicate. **Flagged: no historical fix — verify behavior fresh.** |
| **Paired-leg coordination** | Legs traded independently by design (B23/B24); one leg fills, partner doesn't → unhedged single leg. | identify_sides (live_v3:1528); inventory #9 | Verify one-leg-fill / partner-miss leaves a single-leg position that still applies its own atlas exit (acceptable per design), not an error/stranded order. **Flagged: by-design independent, not a fixed bug.** |
| **REST rate-limit under heavy poll** | Settlements/markets polls can hit limits; failed poll returns None. | RateLimiter (live_v3); bug4_brief §11 | Assert a throttled/None poll is non-fatal (next poll catches up), no crash, no missed permanent settlement. |
| **Void settlement handling** | A `void` must NOT auto-settle at 50¢; skip + log for manual reconciliation. | bug4_brief decision b / §6.3 | Feed a `market_result==void`; assert `settlement_void_manual` logged, position NOT auto-closed. Monitor the void queue. |
| **Adversarial / one-sided / degenerate book** | One-sided book makes spread/mid a lie (B17); fast cancel-replace. | B17; `validate_resting_buys` degenerate_cancel (spread>2 / bid≤0 / ask≥100) | Feed a one-sided book (bid→5¢, ask stable 80¢); assert no entry on phantom spread and degenerate_cancel fires. |

---

## P2 — known operational, accept (monitor only)

| Bug class | Root cause | Fix commit | Verification / note |
|---|---|---|---|
| **Phantom-active accumulation** | The condition Bug 4 fixes the *source* of; residual phantoms cleared by first wide REST poll (live) / settlement. | `366d8aa` (bug4_brief §7) | Burn-in metric: phantom-active count trends → 0 over 24h. Accept short-term residue. |
| **Paper `self.positions` mirror growth** | Mirror would stay "active" forever; silent short-circuit handles. | bug4_brief §2.5 (`366d8aa`) | Confirm settled tickers get `self.positions[tk].settled=True` quiet write; no telemetry expected. |
| **`/markets` value field name** (`settlement_value` vs `_dollars`) | Field name unconfirmed against live; v4 reads `_dollars` with fallback. | bug4_brief §13 Q1 | First live settlement confirms; field divergence logs (non-fatal), not crash. |

---

## Anti-hallucination cross-check (per request)

### Bug classes found in repo NOT in the operator's expected list — surfaced for inclusion
- **Timestamp-parse class (µs-vs-ns / RFC3339 / silent-1970)** — recurring, 3+ fix commits (`43ae049`, `4c100f7`, `a722193`), and **live-relevant** because Bug 4 parses `settled_time`/`settled_ts`. Added as P1.
- **Partial-EXIT P&L double-entry** — distinct from the operator's "partial *entry* fill"; a real, documented, fixed bug (bug4_brief v3) that lives in the v4 exit/settlement path. Added as P0.
- **Void settlement mis-accounting** — bug4 decision b; not in the list. Added as P1.
- **Cell-classification-at-fill-vs-bucket (A10/A11)** — folds into the operator's "cell-bucket boundary errors" but the *fill-time vs bucket-time disagreement* is the sharper framing. Folded into the P0 cell-id row.

### Operator-listed items with WEAK/no dedicated fix-commit evidence — flag for review (may be remembered, not historically fixed)
- **Partial entry fill (10ct→7ct):** no fix commit found for *entry-side* partial fills; only the partial-*exit* P&L fix exists. Treat as a **fresh verification**, not a regression check.
- **Paired-leg coordination failure:** the bot is **by-design** independent per-leg (B23/B24); there is no "coordination" code or fix to regress against. Verify the independent-leg behavior is *acceptable*, don't assume a coordination layer exists.
- **WS reconnect:** existing `_ws_reconnect` logic, **no bug-fix commit** — it's battle-tested in prod (auto-recovers) but never exercised against v4's resting-bid state machine.
- **FD exhaustion:** observed leak, **no fix commit ever landed** — it's an open operational risk, not a fixed bug; monitor, don't assume resolved.

All 17 operator-listed classes have at least some repo evidence; none appear invented. The four above are real but lack a *fix* to verify against — they are forward verifications.

---

## Deploy gate summary
- **8 P0 items** must show an unambiguous paper pass before 9am ET cutover. The cluster of risk is the **hold-cell → Bug-4 handoff** (3 of the 8) — exercise at least one hold-cell N end-to-end in paper.
- **11 P1 items** — deploy is permissible with these monitored; FD count, reconnect count, void queue, and `ws_settle_value_unparseable` are the live dashboards.
- **3 P2 items** — accept and watch the phantom-active→0 burn-in.

*Read-only compile. No code/config changes. Single deliverable; uncommitted for operator review.*
