# INDEPENDENT AUDIT — WINDOW-1 T2 CAUSAL-DIVOT PRE-RUN @ 87ac9382 — RULING: PASS (score-free, claims fenced)

**PASS. Every headline number was independently reproduced twice over: first by recounting the raw committed gz ledgers row-by-row (never the summary receipts), then by two clean full regenerations from the hash-verified frozen private inputs, both byte-identical to all 83 committed regenerable artifacts, with my own freeze stage reproducing the remaining 2 freeze receipts byte-for-byte (85/85). All eight candidates conserve D=804; all 6,432 streams are score-free with every metric null; chronology is strictly causal at every audited stage with zero violations across 176,435 recurrences, 140 actions, and 81 fill-evidence receipts; the Window-1 law is intact in code and in data; and the 12/10/4/8 mechanism manifest verifies exactly, with the claim fences stated below. This audit does not score, rank, tune, or authorize execution.**

Date: 2026-07-28 · Branch: `audit/window1-independent` · Additions-only child of exactly `02c838ba2827842152a0c46bad9b8bb0b6b8c76c` · Auditor: independent CC session
Under audit: `codex/window1-definition` @ `87ac9382c23b586f536cf457883c507ebf366ba3`, parent exactly `d710ba0606084f67625e255e87ebad1cd016bf6a`.

## 1. Lineage and containment — PASS

Both commits typed via `cat-file`; parent link exact from the commit object; remote tip equals 87ac9382; diff = **89 files, all additions, zero modifications/deletions** (85 package artifacts + instrument + builder + candidate spec + test file); inherited tree byte-identical. Import chain of both new modules is stdlib + previously audited window1 analysis modules only — **no scorer, results, ranking, selection, live engine (`live_v4`), network, orders, positions, exits, settlement, DCA, Window-2, or holdout surface is imported or reachable**; `subprocess` is used only for git hashing. The builder hard-fails if any event date is in `SEALED_HOLDOUT_DATES` (2026-07-24/25/26). All 805 private inputs (events ledger + 804 guarded-cache event files under `OMI-Window1-private`) verify byte-exactly against `SOURCE_HASH_MANIFEST.json`; all 8 committed sources verify; all 84 artifact-manifest rows verify (self-excluded).

## 2. Immutable Window-1 law — PASS

- **D:** the frozen events ledger contains exactly 804 events spanning exactly 2026-07-12…20 (156/114/99/64/42/50/62/121/96); overlays conserve 804×8 = 6,432 with per-date×8 conservation.
- **C/PC law:** LOT=5 both legs; the only pair gate in `_lawful_candidate` is `strict_combined_negative: d1+d2+fee<0` — combined pair delta, not both-negative. **Positive sibling delta is lawful** whenever `d2 ≤ b2_max` (first-leg headroom) keeps the combined integer-cent result strictly negative — verified in code, in fixtures, and in data (38,061 lawful positive-d2 targets; 54 actually exposed).
- **No PC→IC tightening; IC and S never gate** (spec `IC_gate:false, S_gate:false`; no code path consults them). **Zero combined-zero admissions** — independently recomputed over all 2,996,560 lawful targets in the sibling-X ledgers: 0 rows with d1+d2+fee ≥ 0, 0 maker-law violations, 0 b2_max violations.
- **No simultaneous-leg requirement:** legs replay asynchronously; T2 acts only on the post-first-fill sibling inside the corridor; completion is asynchronous opportunity across Window 1.
- **Five no-BBO events** (JUL19KRUCAS, JUL20CREMAT, JUL13TAUTOM, JUL14PUTJEA, JUL20KUDKOR) remain D-members in all 8 candidates with **zero fabricated orders and zero substituted prices** (40 proof rows; baseline placements 0; overlays present).

## 3. Time-axis and causal-divot mechanics — PASS (all eight counts reproduced exactly from raw ledgers)

| quantity | committed | independently recounted |
|---|---|---|
| parent-exposure preservation receipts | 1,172,973 | **1,172,973** (= 1,162,210 HOLD decisions + 10,763 non-displacing HOLD receipts) |
| evidence-decay replacements | 274 | **274** (all with named authority — 128 LIVEAIM_SOURCE_MAPPING, 146 CAUSAL_PAIR_HEADROOM — condition, and source receipts; 0 unnamed) |
| receipt-backed PARK exits | 6,963 | **6,963** (all `COMBINED_BUDGET_OR_MAKER_LAW_INVALIDATED`; 0 unnamed) |
| recognized divots | 166,644 | **166,644** |
| later independent recurrences | 176,435 | **176,435** (0 duplicate-receipt recurrences; all strictly later than recognition) |
| later divot actions | 140 | **140** (69 macro_hold + 71 macro_micro full-stack only; every one strictly after recognition AND after first fill; 0 violations) |
| still-later independent fill-evidence receipts | 81 | **81** (40+41; every fill strictly later than its action, distinct receipts; 0 violations) |
| lawfully exposed positive-d2 targets | 54 | **54** (all source `NATIVE_MACRO_TARGET`; 24 PLACE + 30 REPRICE; never a preference — bid+1 is last in fixed authority order) |

Decision conservation: HOLD 1,162,210 + NO_CALL 3,401,933 + PARK 6,963 + REPRICE 274 + PLACE 5,414 = **4,576,794** = the target-surface row count exactly. Chronology laws verified in code and data: first fill arms event-specific `d1`/`b2_max`; every divot decision consumes its own contemporaneous BBO/print (`_lawful_bbo` at trigger time; surfaces record `BBO_receipt`); same-second ordering processes books before prints in preserved receipt order so decisions see the newest lawful same-second book (the amended VUKBRO-class law); **no global-first-X censor exists** — episode decisions run per event, per leg, on every receipt; the corridor is bounded by `first_fill_ts < t ≤ base_horizon` (no post-right evidence); prints are never substituted for BBO authority (print-reach context is excluded from target selection); `run()` hard-fails on any pre-first-fill T2 action or same-receipt action/fill (0 in data); recurrences are genuinely independent receipts; and **nothing displaces a still-lawful exposed order without a named cause** — the non-displacing guard refuses undocumented reprices (10,763 HOLD receipts), REPRICE requires a named decay permit, and PARK requires receipt-backed invalidation.

## 4. Macro × micro meaning — PASS with one honest non-combination

The two regimes differ **only** through the frozen `liveaim_enabled = "__macro_micro__"` switch (macro_hold = ATLAS macro target held; macro_micro = + LIVE-AIM flow-state mapping and GUIDEBOOK deep-tier repricing). The four stacks differ only through the frozen 5-switch matrix (verified against spec, code constants, and per-candidate behavior: divot actions appear only in full-stack; decays only in decay/full; controls emit zero T2 decisions and are semantically identical to the passed parents — 1,608 rows, 0 mismatches, with the 3 former cross-surface boundary artifacts (PASKRU ×2, FEAWAL ×1) disappearing under the identical admission surface as documented). What the candidates actually combine: historical/tradebook macrostructure (ATLAS — BOUND), regime (the macro/micro switch), first-fill sibling response, event-specific headroom, causal print evolution, bid/ask chain with top-5 lawful depth, volume/cadence as stored evidence, and independent per-leg timing/divots. **Not combined: orientation** (ORIENT_V1 is hash-bound but unconsumed — PROXIED), full depth beyond top-5 (ABSENT), and volume/pressure as *gates* (stored, never gating). No simultaneous-posting requirement exists anywhere.

## 5. Mechanism manifest — PASS: 12 BOUND / 10 PROXIED / 4 ABSENT / 8 RETRACTED, each independently verified

**BOUND (12, each verified at its code site):** positive_size_true_print (`positive_print`: positive public print + receipt required, self-evidence excluded); nonself_BBO_top5 (own-order-fingerprint exclusion, top-5 chains); Trendpath_ATLAS_discovery (ATLAS pages → frozen macro target); LIVE_AIM_mapping (`liveaim_mapping` over causal flow state); GUIDEBOOK_deep_tier (`depth_p25_of_w1s` deep targets); positive_print_microdivot (`_detect_divot` on admitted prints); causal_divot_later_recurrence (T2 recognition→recurrence→action→fill chain); pair_combined_headroom (d1/b2_max armed at first fill, strict combined law); timestamped_policy_clock (anchor/left/horizon in every stream); external_ask_maker_safety (X<ask check); non_displacing_target_completeness (guarded `_place_or_reprice`); causal_evidence_decay_exit (named decay receipts + PARK).

**PROXIED (10) — intended organ → what T2 actually consumes → the causal claim the gap prevents → effect:**
1. **carried_last_trade** — live engine's carried last-trade memory → provenance-tagged context (`CARRIED_UNKNOWN` vs `VERIFIED_PRINT_TIMESTAMP`), excluded from target selection → no claim about carried-last-trade-keyed live decisions → interpretation limit only.
2. **standalone_volume_direction** — VOLUME_LEDGER direction dial → executed volume + cadence stored, never gating (`unsourced_volume_direction_gate=False`) → no claim about volume-direction-gated behavior → limit.
3. **top5_pressure_sign** — live pressure-sign gate → depth recorded, gate off (`top5_pressure_sign_gate=False`) → no pressure-gated claims → limit.
4. **close_keyed_recut** — recut close-keyed cells → observed-not-consumed (own-close projection would be future information) → no close-keyed targeting claims; consuming it would be lookahead → lawful refusal, limit.
5. **taker_reach_probability** — takerreach/LAW.json → loaded and hash-bound, never consumed → no reach-probability claims → limit.
6. **drift_surfaces** — fitted drift bands → hash-bound, NO_CALL ("requires future net/dip path components") → no drift-band claims → lawful refusal, limit.
7. **band_map** — fitted band map → same as drift → limit.
8. **divot_tables** — historical divot tables → substituted by **native causal microdivot detection from admitted prints** → no historical-table-keyed claims; the *named causal-divot mechanism itself is the native one and fully BOUND* → limit only, does **not** invalidate the causal-divot families.
9. **LIBRARY_timing** — LIBRARY_V1 timing axis → not consumed (0k axis marked misanchored) → no library-timing claims → limit.
10. **ORIENT_frozen_consumer** — ORIENT_V1 orientation → hash-bound, not consumed (no separately frozen pair-tell mapping) → **no orientation-conditioned claims; "orientation" is not combined into any candidate** → limit; fences §4.

**ABSENT (4):** Pinnacle and authoritative_bookmaker_FV (no sharp-line/FV surface exists in the inputs — zero tokens anywhere; no FV-relative claims possible); full_depth_beyond_top5 (guarded cache preserves top-5 only; depth conclusions are top-5-bounded); independent_shape_mapping (no independent shape surface). **None of the 10 PROXIED or 4 ABSENT mechanisms makes the named causal-divot mechanism non-reproducible or any candidate label false** — every label names admission/completeness/decay/divot mechanisms, all BOUND. T2 therefore does **not** bind the complete live conception/dial pipeline, and its future scores must be read as: *completion behavior of the causal print/BBO/ATLAS/LIVE-AIM stack, silent on orientation-, FV-, deep-book-, and direction-gated organs.*

**RETRACTED (8) — all verified deliberate lawful removals, none hiding missing behavior:** moving_bid_edge and last_trade_direction_gate and pressure_taker_direction_gate carry explicit negative attestations on live action receipts (`moving_bid_minus_edge_used=False`, `last_trade_direction_gate=False`, `top5_pressure_sign_gate=False`, `isolated_taker_side_direction_gate=False` — 4 sites in v1 + 4 in T2); universal_50_split and borrowed_sealed_pair_shape have zero tokens anywhere in the instrument chain (removed in the audited Range-Attack lineage; sealed-pair borrowing is a holdout-integrity law); T1_unconditional_persistence is retracted by spec and by policy (`lawful_persistence: False`) and replaced with receipt-backed preservation (census `unconditional_persistence: false`) — motivated by the audited T1 result that unconditional persistence *cost* PC; T1_inert_response_only_label retracted as behaviorally inert (proven a no-op in the T1 results audit); automatic_positive_d2_bid_plus_one_preference retracted after 0/82 fills, with live `t2_inherited_bid_plus_one_not_selected` receipts at every trigger and bid+1 demoted to last authority.

## 6. Dataset boundaries — PASS (with one recorded obligation)

Fit slice July 12–17 (525 events ×8 = 4,200 rows) and post-fit July 18–20 (279 ×8 = 2,232 rows) are both present and per-date conserved; every overlay row carries `event_date`, so the split is fully recoverable. The July 24–26 holdout is excluded by a hard builder gate and appears nowhere in the inputs. **Obligation recorded:** the PRE-RUN itself does not pre-encode a fit/post-fit reporting partition (lawful — it is score-free and aggregates nothing); the future scoring package MUST report fit and post-fit separately and no aggregate may conceal the distinction.

## 7. Future scoring law — RECORDED, NOT SCORED

The scoring package that follows this PRE-RUN must encode, and be independently audited for, the completion–discount frontier for every candidate: completion at combined cost ≤93, ≤95, ≤97, <100, and completion-at-any-price as the fillability ceiling, each with per-leg individual-delta splits; the objective is frontier maximization at <100; PC/D ≥ 603/804 is the floor, not the summit; PC must never be reduced to one scalar headline; fit (Jul 12–17) and post-fit (Jul 18–20) reported separately. This law is not yet encoded anywhere in the frozen package — it binds the next stage, before any execution authorization.

## 8. Determinism and conservation — PASS

22/22 focused tests pass (pytest). Two clean full regenerations from the hash-verified private inputs: **build A and build B each byte-identical to all 83 committed regenerable artifacts; my freeze stage over my own two builds reproduces the 2 committed freeze receipts byte-for-byte — 85/85 total.** All hashes recomputed: 84 artifact rows + 8 committed sources + 805 private inputs, 0 mismatches. D=804 × 8 candidates; exactly 6,432 score-free streams; every metric/performance field null across all ledgers and overlays (verified row-by-row); every terminal decision class conserves to the surface total; first-fill budget receipts = 4,176 (522 armed events × 8); zero candidate-specific hardcoding in the instrument (the only event-ID literals in the builder document the three disclosed boundary artifacts inside a receipt block); zero forbidden data access.

## Discrepancy table

| class | entries |
|---|---|
| Measurement defect | **None found.** All committed numbers reproduce exactly from raw ledgers and from clean regenerations. |
| Evidence limitation | Top-5 depth only; no Pinnacle/FV surface; drift/band/recut/LIBRARY surfaces lawfully unconsumable without future components; ORIENT unconsumed without a frozen pair-tell mapping. These bound interpretation, not correctness. |
| Candidate-family limitation | Divot recall acts only in full-stack candidates (by design); all 140 divot actions selected negative-d2 targets — the recurrence mechanism as frozen never expressed a positive-d2 exposure; positive-d2 exposure flows exclusively through NATIVE_MACRO_TARGET (54). TON_SPI capacity remains an uncredited claim per the migration table. |
| Genuine observed market behavior | Of 166,644 recognized divots, 176,435 later independent recurrences exist, but only 140 became lawful actions and 81 produced still-later fill evidence — recurrence-at-X is common; recurrence surviving the combined-budget/maker/authority law at action time is rare. 6,963 PARKs are all budget/maker invalidations: the market moving away from the armed budget, not instrument attrition. |

## RULING

**PASS** — truthfully partial score-free instrument with claims fenced as above. Nothing here scores, ranks, tunes, deploys, or touches live/holdout state.

**Single lawful next instruction:** construct the frozen T2 scoring package on this PRE-RUN (parent = 87ac9382), encoding verbatim the §7 frontier-reporting law (≤93/≤95/≤97/<100/any-price tiers with per-leg delta splits, fit Jul 12–17 vs post-fit Jul 18–20 reported separately, frontier maximization at <100 as the objective, PC/D ≥ 603/804 as floor), and submit it for independent audit before any scoring execution is authorized.
