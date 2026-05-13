# Bot V5 Shell Architecture

**Status:** Draft v0.1  
**Scope:** Forward-looking shell architecture for the post-T37-Phase-3 live bot, using deployable cells derived from the T37 per-minute universe and T38 forward depth corpus.  
**Posture:** Conviction spec. This document is intended to be implementable once T37 Phase 3 lands and downstream cell-derivation queries identify deployable cells.

## 1. Purpose

V5 replaces the legacy live bot foundation with a cell-routed, data-driven execution shell. The old architecture chose trades from static bucketized cell lookups and embedded risk, routing, execution, logging, and schedule matching inside one large process; V5 separates those concerns and makes the cell definition the canonical decision object.

The unit of decision must match the unit of analysis. SIMONS_MODE explicitly locks that principle, and T38 extends rather than replaces T37 by keeping `(ticker, minute_ts)` join compatibility while adding actual depth and reconstruction support.

V5 is therefore not `live_v3.py` with better parameters. It is a new shell that salvages infrastructure from `live_v3.py` where foundation-agnostic, while deprecating logic tied to the old bucket/cell foundation and any architecture that assumes the wrong observation grain.

## 2. Design stance

The old live bot proved that several production concerns were real and needed: authenticated Kalshi API wrapping, rate limiting, WebSocket book maintenance, paper trading, JSONL telemetry, schedule reconciliation, and operational durability under imperfect feeds. The old live bot did **not** prove that its celling, state model, or embedded policy logic should survive as the control architecture.

V5 centers on four ideas:

1. **Routing is empirical, not heuristic.** The router reads a derived cell-config artifact and returns either a specific routed cell or `skip`; it does not infer strategy from mid-price buckets alone.
2. **Execution is a service, not the brain.** Maker/taker choice, order management, fill handling, and adverse-selection response belong in a dedicated execution layer, not scattered across the main bot loop.
3. **Risk is separate.** Exposure limits, kill switches, and authorization gates must not be buried inside policy or transport code.
4. **Paper mode is default.** V5 launches in paper mode unless explicitly authorized otherwise; this is a gating rule, not a convenience flag.

## 3. Keep vs discard inventory

### 3.1 live_v3.py summary

`live_v3.py` is a monolith with a usable infrastructure core and a deprecated decision core. The infrastructure pieces are worth salvaging because they solve generic live-bot problems; the decision pieces are tightly coupled to the old foundation: static category/direction/mid buckets, embedded order lifecycle assumptions, and live strategy logic interwoven with transport and state management.

The key split is:

- **Salvage:** transport, auth, rate limiting, local book maintenance, logging pattern, paper-mode scaffolding, some schedule mapping utilities.
- **Replace:** cell lookup, position lifecycle semantics, sizing logic, hard-coded entry/exit/DCA rules, and any logic that assumes the old deploy config is the decision authority.

### 3.2 KEEP AS-IS — foundation-agnostic infrastructure

These symbols are structurally reusable with minimal or no semantic change in V5:

#### Module-level constants / paths
- `BASE_URL`, `WS_URL`, `WS_PATH` — Kalshi endpoint wiring remains foundational infrastructure.
- `MAX_RPS`, `WS_PING_INTERVAL`, `WS_SUBSCRIBE_BATCH` — still valid as transport-layer knobs, though final values may be tuned later.
- `STATE_DIR`, `LOG_DIR` — generic runtime persistence locations remain useful.

#### Auth / API utilities
- `load_credentials()` — still the correct boundary for env/pem loading.
- `sign_request()` — direct Kalshi auth primitive, fully reusable.
- `auth_headers()` — direct Kalshi auth header constructor, fully reusable.

#### Rate limiting / raw HTTP
- `RateLimiter` — keep as-is conceptually and likely nearly verbatim in implementation.
- `_real_api_get()`, `_real_api_post()`, `_real_api_delete()` — generic resilient API wrappers with retry/backoff are reusable as the base of the V5 execution/data clients.

#### Book representation
- `Book` — local orderbook container remains the right low-level primitive.
- `recalc_bbo()` — keep as-is.

#### Paper-mode base objects
- `PaperOrder` — keep structurally; it already captures posted order state and telemetry useful for simulated execution analysis.
- `PaperPosition` — keep structurally as a paper-position state object.
- `PaperFillSimulator` — keep as the nucleus of paper fills against local book/trade events, though behavior will expand under adaptation elsewhere.
- `PaperApi` — keep as the main paper harness shell because it already intercepts order CRUD and emits simulation telemetry.
- `api_get()`, `api_post()`, `api_delete()` — the dispatch pattern between real and paper paths is sound and should carry forward.

#### Logging / persistence helpers
- `LiveV3._log()` — the JSONL logging pattern is directly worth carrying into V5.
- `LiveV3._load_processed()` / `LiveV3._save_processed()` — the pattern of durable restart-safe state tracking is reusable, though the exact processed object changes in V5.
- Tick/trade file handles and flush discipline inside `LiveV3` are operationally useful even if the exact schemas change.

### 3.3 KEEP WITH ADAPTATION — sound structure, new foundation required

These symbols or symbol families are worth preserving in spirit, but need nontrivial adaptation.

#### Discovery / market metadata
- `_parse_ticker_date()` — keep with adaptation; still useful for event/ticker timing guards, but V5 should not hardwire series/date assumptions as routing logic.
- `_entry_lead_cap()` and `ENTRY_MAX_LEAD_SEC_BY_SERIES` — keep with adaptation; lead-cap logic should become policy/config data rather than static module logic.
- `SERIES_MAP`, `ALL_SERIES`, `get_category()` — keep with adaptation; category/series tags remain useful, but V5 needs richer regime tags and must not confuse series/category with the deployable cell itself.

#### Book / microstructure logging
- `_extract_depth()`, `_depth_signature()`, `_log_tick()`, `_log_trade()`, `apply_trade()` — keep with adaptation; these are useful local telemetry utilities, but the schemas should align with T38 semantics and use `ct` terminology plus `yes/no` taker-side semantics consistently.
- `VolumeTracker` — keep with adaptation; useful for rolling trade-volume context, but its internal conversion from Kalshi `yes/no` into `buy/sell` reflects legacy semantics and must be normalized around canonical `yes/no` taker-side framing in V5.

#### Schedule reconciliation
- `_load_schedule()` — keep with adaptation; V5 still needs producer-fed schedule context.
- `_match_event_to_schedule()` — keep with adaptation; matching Kalshi events to schedule data remains necessary, but it should be moved into a dedicated metadata/schedule service rather than living inside the live bot shell.

#### Fair-value anchor integration
- `_get_side_fv()` — keep with adaptation; the concept of side-specific anchor retrieval is still valuable, but the anchor source must shift from legacy `fv` helpers to the new foundation data access layer that reads T37/T38-derived runtime views.

#### Position / order lifecycle structures
- `Position` — keep with adaptation; V5 still needs per-ticker lifecycle state, but the fields should be rebuilt around routed cell ID, vector tag, phase_state, cluster membership, execution mode, and policy state rather than entry/DCA/legacy play-type assumptions.
- `LiveV3.positions`, `pending_entries`, `inflight_orders` — keep with adaptation; these are real orchestration needs, but the state machine must be redefined around routed cells and policy executor outputs.

#### Main bot shell
- `LiveV3` as a class boundary — keep with adaptation only as a shell/composition root. The class should survive as a coordinator or service container, but its current responsibilities must be split into routing, policy, execution, risk, and data-access components.

### 3.4 DEPRECATE — tied to broken foundation or replaced by V5 architecture

These symbols are either directly wrong for V5 or represent roles that move into new components.

#### Celling / deploy config
- `CONFIG_PATH` override behavior is not itself the problem, but the current config target `deploy_v4.json` and the assumptions around `active_cells` / `disabled_cells` are deprecated. V5 replaces this with a new cell-config schema whose canonical unit is a deployable empirical cell with vector tag, policy, sizing, execution mode, cluster membership, and activation status.
- `cell_lookup()` is deprecated. It currently maps `(category, direction, entry_mid)` into a static 5-cent bucket cell name, which is exactly the old foundation that V5 is replacing.  
  **Role it played:** old router.  
  **What replaces it:** `CellRoutingEngine.route(state) -> routed_cell | skip` reading the new cell-config artifact.

#### Embedded strategy rules
- All hard-coded entry/exit/DCA parameters and series-specific heuristics as strategy authority are deprecated: `MIN_VOLUME`, `MAX_HOURS_TO_EXPIRY`, `ENTRY_BUFFER_SEC`, `UNMATCHED_SKIP_CYCLES`, `UNMATCHED_SKIP_AGE`, `BOOK_STALENESS_SEC`, `DEAD_SPREAD_THRESHOLD`, `STALE_BUY_DELTA`, `PENDING_TIMEOUT_SEC`, `STALE_CHECK_INTERVAL`, `EXIT_PRICE_CAP`, and legacy fill-floor / baby-size assumptions.  
  **Role they played:** ad hoc policy control.  
  **What replaces them:** per-cell policy fields plus separate risk/execution configuration in V5.

#### Legacy position semantics
- `Position` fields tied to old play structure — `dca_price`, `dca_order_id`, `dca_qty`, `dca_filled`, `play_type`, `layered_exit_price`, `cell_exit_order_id`, `cell_exit_price`, `legacy`, `anchor_source` as currently used, and `routed_cell` as a free-form string — are deprecated in their current form.  
  **Role they played:** encoded the V3/V4 tactical logic.  
  **What replaces them:** explicit cell-lifecycle state under the cell policy executor.

#### Monolithic orchestration methods
- `discover_markets()` in its current form is keep-with-heavy-adaptation at best, but the monolithic discovery-plus-routing-plus-entry staging behavior is deprecated.
- The rest of the large `LiveV3` decision loop that performs discovery, evaluates eligibility, computes anchors, places entries, manages exits, and settles inside one class is deprecated as architecture.  
  **Role it played:** all-in-one live bot brain.  
  **What replaces it:** modular services — routing engine, policy executor, execution layer, risk manager, data access layer, and separate producer contracts.

### 3.5 Symbol notes by load-bearing area

#### Most reusable areas in live_v3.py
- Auth and transport utility layer near `load_credentials()`, `sign_request()`, `auth_headers()`, `RateLimiter`, and `_real_api_*` are the cleanest salvage candidates.
- Paper-mode machinery around `PaperOrder`, `PaperPosition`, `PaperFillSimulator`, `PaperApi`, and the module-level API dispatchers is the strongest reusable simulation core.
- The `Book` object and trade/book telemetry helpers are worth keeping once semantics are updated.

#### Least reusable areas in live_v3.py
- `cell_lookup()` is directly obsolete under the new foundation.
- The old position lifecycle with entry/DCA/exit assumptions is too strategy-specific to survive intact.
- Any logic deriving action directly from category + direction + entry-mid bucket should be treated as deprecated, even when embedded in otherwise useful methods.

## 4. executor_core.py and other root files

### 4.1 executor_core.py status

`executor_core.py` is overwhelmingly **DEPRECATED** for V5 because it is architected around a dual-venue hedged arbitrage model involving Kalshi and a separate PM leg, explicit hedge coherence checks, PM intent switching, unwind logic, and post-trade dual-leg verification.

That said, a few ideas are still intellectually useful:

- `TradeResult` is salvageable as a pattern, not as-is. V5 still needs a structured execution result object, but fields specific to PM hedging, unwind legs, opposite-side hedges, and combined-cost arbitrage are obsolete.
- `_log_kalshi_error()` is a useful pattern for persistent execution-failure logging.
- `diagnose_nofill()` is conceptually interesting because it enforces root-cause classification for no-fills; V5 should adopt the same discipline for Kalshi maker/taker no-fill and adverse-selection diagnostics, but the PM-specific logic is obsolete.

Everything else in `executor_core.py` is either off-path or actively misleading for V5:

- `TRADE_PARAMS`, `_check_hedge_coherence()`, `_verify_both_legs()`, `post_trade_audit()`, `_unwind_pm_position()`, PM intent mappings, and dual-venue exposure bookkeeping are deprecated.
- `calculate_optimal_size()` and `safe_to_trade()` may contain reusable ideas, but because they were built under the old two-venue arb/risk model they should be treated as design references, not direct salvage.

### 4.2 swing_ladder.py status

`swing_ladder.py` was not present at the expected repo paths during inspection, so there is no current code basis to classify. Unless a local-only copy exists outside the main tree, V5 should proceed assuming no live-bot dependency on `swing_ladder.py`.

### 4.3 Other root files with direct relevance

The strongest architectural references outside code are:

- `SIMONS_MODE.md` for "unit of analysis = unit of decision" and Problem 1 vs Problem 2 separation.
- `per_minute_universe_spec.md` (T37) for the canonical per-minute grain and join keys.
- `t38_books_daemon_spec.md` for forward depth, additive schema alignment, and `get_book_at` capability.
- `layer_b_v2_spec.md` and `forensic_replay_v1_spec.md` for tick-level semantics and fill/replay discipline that should inform V5 execution telemetry and paper validation.
- `LESSONS.md`, especially F-category durability/reconciliation lessons, as the source of operational guardrails.
- `ROADMAP.md` for T-item sequencing and gating context.

## 5. V5 shell architecture

### 5.1 Component map

V5 should be composed from nine top-level components:

1. **Cell routing engine**
2. **Cell policy executor**
3. **Execution layer**
4. **Risk manager**
5. **Paper mode harness**
6. **Foundation data access layer**
7. **Cell config schema + artifact loader**
8. **Logging / telemetry extension layer**
9. **Producer coordination contract**

The shell process should orchestrate these components, not subsume them. The main runtime loop becomes: refresh runtime state → fetch foundation features → route cell → check risk → execute or skip → monitor lifecycle → log.

### 5.2 Cell routing engine

**Responsibility**  
Replace `cell_lookup()`. Input is current runtime state for a market: `(ticker, event_ticker, current minute, current T37-compatible features, phase_state, paired-leg state, spread/depth state, freshness state)`. Output is either a routed cell ID or `skip`.

**Inputs**
- T37-aligned runtime minute features.
- T38-derived current depth / reconstruction fields where required.
- Phase-state classification, including the queued four-state amendment once landed.
- Pair/paired-leg state where the cell definition requires it.
- Cell-config artifact.

**Outputs**
- `route_decision = {cell_id, vector_tag, cluster_id, execution_mode, policy_ref, confidence, skip_reason?}`

**Dependencies**
- Foundation data access layer
- Cell-config loader
- Metadata/schedule service
- Risk manager only for admissibility overlays, not routing itself

**Notes**  
This engine must be deterministic and side-effect free. It should not place orders, mutate positions, or hide policy logic. It is a router, not a trader.

### 5.3 Cell policy executor

**Responsibility**  
Translate a routed cell into a concrete action plan: whether to place, where to place, how long to rest, what exit behavior to use, what sizing regime applies, and how the position lifecycle should be managed from entry through exit.

**Inputs**
- Routed cell decision
- Current microstructure state
- Current position state
- Risk allowances
- Execution feedback

**Outputs**
- `order_intent` objects: place, cancel, reprice, hold, exit, skip
- lifecycle state updates

**Dependencies**
- Cell config schema
- Risk manager
- Execution layer
- Position store

**Notes**  
This replaces the old embedded logic in `LiveV3` where entry, DCA, and exit decisions were interwoven with bot state. In V5, the policy executor owns lifecycle semantics.

### 5.4 Execution layer

**Responsibility**  
Wrap Kalshi order transport and execution mechanics. This is where the salvage from `live_v3.py` belongs: signed requests, rate limiting, order CRUD, WebSocket book state, fill polling/confirmation, and maker-vs-taker regime logic.

**Inputs**
- `order_intent`
- current local book
- execution mode from routed cell
- risk approvals

**Outputs**
- `execution_result`
- fill events
- cancel events
- adverse-selection flags
- book/latency telemetry

**Dependencies**
- `load_credentials()`, `sign_request()`, `auth_headers()`, `RateLimiter`, `_real_api_*`, `Book`, local book maintenance salvage from `live_v3.py`.

**Maker-vs-taker decision**
- V5 must make execution mode explicit per cell: `maker_dominant`, `taker_dominant`, or `skip`.
- The execution layer can override within a bounded policy envelope when market state invalidates the preferred mode, but it must log the override and reason.

**Adverse selection**
- Adverse-selection detection belongs here because it is execution telemetry, not strategy. Signals include: fill after quote decay, fill immediately followed by spread blowout, fill against collapsing anchor, or repeated fill-at-worst-state patterns.

### 5.5 Risk manager

**Responsibility**  
Independent gatekeeper for exposure and safety. It should not discover cells or send orders; it approves, rejects, or throttles intents and can issue kill switches.

**Inputs**
- proposed order intent
- current positions
- exposure by ticker/event/category/cluster/total
- freshness and health metrics
- authorization state

**Outputs**
- `approve`, `reject`, `throttle`, `kill`
- updated allowed size / cap

**Risk dimensions**
- Per ticker
- Per event
- Per category / series
- Per cell cluster
- Total gross / net exposure
- stale-data / producer-health kills
- paper-mode-only enforcement unless live authorized

**Notes**  
This separation is non-optional. The old architecture embedded too much strategy/risk coupling into the live loop; V5 should make risk auditable and independently testable.

### 5.6 Paper mode harness

**Responsibility**  
Default execution substrate until live authorization is granted. V5 should reuse the current paper-mode harness from `live_v3.py` and extend it rather than starting over.

**Reused pieces**
- `PaperOrder`
- `PaperPosition`
- `PaperFillSimulator`
- `PaperApi`
- API dispatch pattern (`api_get/api_post/api_delete`)

**Required extensions**
- Partial-fill realism
- maker queue-position assumptions where possible
- T38-informed depth-aware fill simulation
- policy lifecycle simulation at the cell level
- richer telemetry for no-fills, adverse selection, cancel/repost churn, and time-to-fill distributions

**Safety rule**
- New bot is paper-mode-by-default.
- Live mode requires explicit authorization flag plus risk-manager live enable plus successful validation gates.

### 5.7 Foundation data access layer

**Responsibility**  
Provide all runtime and config-update data reads from the new foundation. This is a new component and one of the first things to build.

**Runtime queries**
- Latest T37-aligned per-minute features for `(ticker, minute_ts)`.
- Latest phase_state and amended state fields once landed.
- Latest T38 minute snapshot for aligned depth fields.
- `get_book_at(ticker, ts)` / near-now reconstruction for execution and paper analysis where needed.
- Data freshness / completeness / provenance flags.

**Config-update-time queries**
- Cell derivation queries over T37 history
- Cell validation / deployability queries
- Regime clustering queries
- Execution-mode estimation by cell / cluster
- Sizing calibration by cell
- Exit rule estimation by cell

**Interface design**
- Runtime side should expose low-latency typed reads.
- Research/config side can be slower and batch-oriented.
- The bot should never read raw parquet directly in the hot path; use precomputed/runtime-ready artifacts or a lightweight query service.

### 5.8 New cell config schema

**Responsibility**  
Replace `deploy_v4.json` with a schema whose canonical row is a deployable empirical cell.

**Minimum fields**
- `cell_id`
- `vector_tag`
- `cell_cluster`
- `activation_status`
- feature predicates / routing signature
- entry rule
- exit rule
- sizing rule
- execution mode
- confidence / sample support metadata
- provenance metadata (which derivation run produced it)

**Notes**  
The schema is not just a lookup table; it is the contract between offline derivation and live routing/policy execution.

### 5.9 Logging extensions

V5 should retain the JSONL pattern from `live_v3.py` and extend it. Required new fields include:

- `cell_id`
- `vector_tag`
- `cell_cluster`
- `phase_state_at_entry`
- `phase_state_at_exit`
- `anchor_confidence`
- `routing_confidence`
- `execution_mode_requested`
- `execution_mode_actual`
- `producer_freshness`
- `t37_minute_ts`
- `t38_snapshot_source`
- `skip_reason`
- `risk_gate_reason`
- `adverse_selection_flag`
- `cancel_reprice_count`

This logging layer should produce machine-auditable traces for paper validation and post-live forensic review.

### 5.10 Coordination with producers

V5 depends on two producer classes:

- **T37 producer:** periodic, minute-grain refresh of canonical universe features.
- **T38 producer:** continuous book capture and reconstruction support.

**Freshness contract**
- Routing cannot use stale T37 beyond a configured tolerance.
- Maker execution cannot rely on stale T38 / local-book state.
- If freshness fails, risk manager returns `kill` or `skip`.
- Provenance flags from T38 (`snapshot_complete_bool`, `sequence_gap_flag`, source markers) should be visible to the bot and eligible as gating signals.

## 6. Concrete component responsibilities

### 6.1 Runtime flow

1. Producer health check
2. Read latest runtime state from foundation data access layer
3. Build routing state
4. `CellRoutingEngine.route()` → cell or skip
5. Risk pre-check
6. `CellPolicyExecutor.plan()` → order intent or hold/skip
7. `ExecutionLayer.execute()`
8. Position lifecycle update
9. Logging emit
10. Repeat / monitor / exit / cancel / settle paths

This ordering keeps the empirical foundation upstream of policy and keeps execution downstream of policy.

### 6.2 Position model in V5

Position state should be recast as:

- identity: `ticker`, `event_ticker`, `cell_id`, `vector_tag`, `cluster_id`
- entry context: `entry_minute_ts`, `phase_state_entry`, `entry_anchor`, `anchor_confidence`
- execution context: `execution_mode`, `rest_count`, `reprice_count`, `partial_fill_state`
- size context: `target_ct`, `filled_ct`, `remaining_ct`
- lifecycle context: `status = pending|live|exiting|closed|cancelled|killed`
- exit context: `exit_policy_id`, `timeout_ts`, `actual_exit_mode`
- provenance: `t37_data_version`, `t38_data_version`, freshness flags

This replaces the old DCA- and play-type-centered `Position` shape.

## 7. Cell config schema proposal

### 7.1 Schema shape

YAML is more human-reviewable than JSON for the authoring artifact, but the runtime loader can compile it into JSON if desired.

```yaml
schema_version: "v5.cell_config.1"
generated_at_utc: "2026-05-13T18:00:00Z"
source_artifact: "t37_phase3_cell_derivation_run_2026_05_13"
default_policy_refs:
  execution_defaults:
    max_reprice_count: 2
    cancel_on_stale_t38_sec: 10
    cancel_on_anchor_break_cents: 2.0

cells:
  - cell_id: "WTA_MAIN.phase_2_stable.vol_high_tier_3.spread_tight_tier_2.no_pair_gap_caution.vectorB"
    active: true
    vector_tag: "vectorB"
    cluster_id: "cluster_exec_regime_07"
    category: "WTA_MAIN"

    routing_signature:
      phase_state: "phase_2_stable"
      vol_bucket: "high_tier_3"
      spread_bucket: "tight_tier_2"
      pair_gap_state: "no_pair_gap_caution"
      required_feature_flags:
        - "t37_available"
        - "t38_available"
      skip_if:
        - "producer_freshness_fail"
        - "sequence_gap_flag=true"

    empirical_support:
      train_sample_n: 842
      validation_sample_n: 211
      realized_edge_bps: 148
      confidence_score: 0.81
      anchor_confidence_model: "anchor_conf_v2"

    entry_rule:
      rule_id: "entry_rule_041"
      reference: "best_yes_bid"
      placement_mode: "maker"
      placement_offset_cents: 0
      max_anchor_deviation_cents: 1.5
      require_spread_lte_cents: 2
      require_depth_top10_yes_gte_ct: 120
      require_depth_imbalance_top5_between: [0.42, 0.63]

    exit_rule:
      rule_id: "exit_rule_041"
      mode: "maker_then_taker_timeout"
      target_reference: "entry_fill_plus_edge_capture"
      target_offset_cents: 2
      max_hold_sec: 420
      timeout_fallback_mode: "taker"
      cancel_if_anchor_reverses_cents: 2.0

    sizing:
      rule_id: "size_rule_041"
      mode: "fixed_fraction_of_risk_cap"
      base_ct: 15
      max_ct: 30
      scale_up_if_confidence_gte: 0.85
      scale_down_if_depth_top10_yes_lt_ct: 150

    execution:
      mode: "maker_dominant"
      allow_taker_override: true
      taker_override_conditions:
        - "timeout_near_expiry"
        - "anchor_confidence_drop"
      adverse_selection_guard:
        post_fill_spread_blowout_cents: 3
        immediate_reversal_anchor_cents: 2

    lifecycle:
      position_state_model: "single_entry_single_exit_v1"
      allow_reentry_same_minute: false
      max_reprices: 2

    provenance:
      derived_from:
        - "T37 Phase 3"
        - "T38 overlap calibration"
      derivation_run_id: "derive_cells_2026_05_13_b"
      notes: "Cluster assigned from regime-level execution clustering bundle 2"
```

### 7.2 Schema principles

- A cell row must be deployable by itself.
- Routing predicates and policy are coupled in the same object.
- Cluster membership is explicit because execution clustering matters at the regime layer, not just per-cell.
- Provenance is mandatory so deploy decisions can be audited later.

## 8. Implementation sequencing

### 8.1 Build order

1. **Foundation data access layer**
2. **Cell config schema + loader/compiler**
3. **Cell routing engine**
4. **Cell policy executor**
5. **Execution layer port from `live_v3.py` salvage**
6. **Risk manager**
7. **Logging schema extensions**
8. **Paper-mode validation harness extension**
9. **End-to-end paper bot shell**
10. **Live authorization gate**

This order matters because routing and policy must sit on correct data contracts before execution plumbing is attached.

### 8.2 Where salvaged `live_v3.py` pieces get ported

#### Port first
- auth and transport primitives
- `RateLimiter`
- raw API wrappers
- `Book` and local-book maintenance helpers
- JSONL logging pattern
- paper API dispatch pattern

#### Port second
- schedule matching / market metadata reconciliation
- depth/trade telemetry helpers
- `PaperFillSimulator` extensions

#### Do not port directly
- `cell_lookup()`
- old `Position` schema
- entry/DCA/exit tactical logic
- any direct dependence on `deploy_v4.json`
- embedded strategy constants that should become policy/risk config

### 8.3 Paper-mode validation timing

Paper-mode validation happens **before** any live authorization and gates it.

**Paper validation should require:**
- successful routing against real runtime T37/T38 inputs
- no stale-data violations under realistic producer timing
- stable position lifecycle handling
- fill/no-fill telemetry with interpretable diagnostics
- acceptable cancel/reprice churn
- adverse-selection metrics within tolerance
- calibration checks against T38 overlap windows where appropriate

### 8.4 Live authorization

Live authorization should be granted only when all of the following are true:

1. T37 Phase 3 is landed and validated.
2. Deployable cells are identified by downstream derivation queries.
3. T38 runtime depth data is available with acceptable freshness/quality.
4. Paper mode shows stable performance and operational safety.
5. Risk manager thresholds and kill switches are tested.
6. Operator explicitly enables live mode.

No implicit live enable from config presence alone.

## 9. Open questions

These need resolution before implementation begins in earnest:

1. **Exact runtime feature surface:** Which T37-derived fields are required in the hot path versus only in offline derivation?
2. **Phase-state amendment landing:** The queued four-state `phase_state` amendment affects routing and config shape; V5 should not freeze the router interface before that lands.
3. **Yes/No asymmetry features:** These queued T37 amendments may materially alter cell derivation and routing predicates.
4. **Anchor definition:** What is the canonical runtime anchor — T37-derived, T38-derived, or a blended reconstruction?
5. **Execution clustering granularity:** How coarse should `cluster_id` be for regime-level execution control?
6. **Maker queue modeling in paper mode:** How realistic can the simulator be before T38-based reconstruction support is fully integrated?
7. **Position lifecycle variants:** Will all deployable cells share one lifecycle model, or do some require alternate state machines?
8. **Freshness tolerances:** What exact producer-lag thresholds trigger `skip` vs `kill`?
9. **Config deployment path:** Will cell configs be file-based, database-backed, or served via a lightweight config endpoint?
10. **Authorization chain:** Who flips live authorization, and how is that persisted and audited?

## 10. Cross-references

- `SIMONS_MODE.md` — foundational principle: unit of analysis must equal unit of decision; Problem 1 vs Problem 2 separation.
- `LESSONS.md` — especially F-category durability, reconciliation, and canonical-source discipline.
- `ROADMAP.md` — T-item sequencing and gating context.
- `per_minute_universe_spec.md` — T37 canonical per-minute universe and schema contract.
- `t38_books_daemon_spec.md` — T38 minute/tick depth layer, additive schema alignment, and `get_book_at` reconstruction primitive.
- `layer_b_v2_spec.md` — execution and replay semantics relevant to fill modeling and consumer locking.
- `forensic_replay_v1_spec.md` — tick-grain replay architecture for validation and fill semantics.

## 11. Final stance

The correct V5 move is **not** to "upgrade `live_v3.py` until it works." The correct move is to salvage its production-grade infrastructure and discard its foundation-coupled decision architecture.

The most important implementation decision is to make the **cell config artifact** the contract between offline empirical derivation and live runtime action. Once that contract exists, the rest of the V5 shell becomes modular, testable, and aligned with the T37/T38 foundation.
