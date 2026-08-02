# Window-1 entry decision-surface inventory

This is a read-only curation of the entry decision tree at parent
`823a739daed7af6073e48ec037cff05db8f3d494`. It changes no behavior, runs no
replay, and grants no new surface authority.

The essential distinction is between two different systems:

- **PRODUCTION** is `live_v4.py` with the frozen `deploy_v5_live.json` switches.
  Its initial price signer is ATLAS.
- **V11 RESEARCH** is the quote-shape elimination replay. Its shape, pair,
  ordinal, and persistence surfaces are not loaded by `live_v4.py` and are not
  deployed.

Production source and switch provenance for every production-state statement:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/live_v4.py

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/config/deploy_v5_live.json

## Status vocabulary

- `LIVE_SIGNER`: can set the submitted production price.
- `LIVE_GATE`: can permit, refuse, clamp, cancel, or reprice production action.
- `LIVE_CONTEXT`: computed in production but cannot sign price at that point.
- `SHADOW`: evaluated/logged but not enforced.
- `OVERWRITTEN`: returns an answer that a later authority replaces or ignores.
- `DEAD`: disabled, stubbed, or explicitly retired.
- `V11_REPLAY_AUTHORITY`: acts only in the development replay.
- `DIAGNOSTIC`: report/census only.

## Surface catalogue

| Surface | Fit population, date, and reference | Honest-clock era | Question it actually answers | Current authority |
|---|---|---|---|---|
| Raw BBO / print tape | Unfitted causal observations. Same-receipt bid, ask, size, spread, last-trade identity, timestamp, and source ordinal. | N/A | What was observable now? | Source evidence in both systems. |
| Guard / schedule sources | Not a statistical fit. Frozen schedule, observed-start, gun, and guarded Window-1 evidence. | Mixed source history; current guarded evaluator is post-migration. | Is an action inside the lawful entry corridor? | `LIVE_GATE`. |
| `ATLAS_V1` | Built 2026-07-15 from G9 minute candles before 2026-07-10 plus live-era local tape. Anchor = first-hour median at discovery; target = deepest pre-onset `price_low` below that anchor. | **PRE** 2026-07-17 migration. | How deep did the old path go below its first-hour-median anchor? | Production `LIVE_SIGNER` for initial aim. |
| `ORIENT_V1` | Built 2026-07-15. First-hour drift/range/flow; truth = pre-onset drift at least 2 cents. Book-spread asymmetry was absent. | **PRE** | Which leg is directional under the old candle/onset frame? | One input to production orientation; not a price signer. |
| `LIBRARY_V1` / LIVE_AIM | Built 2026-07-15. Category × price cell × first-hour print-volume band; dip = at least 3 cents below discovery; onset clock expressly mis-anchored. | **PRE** | Historical dip/cash-window context under the old clock. | Production shadow/no-opinion path. |
| Legacy regime/per-cell entry tables | May 23 and June 5 fits; regime or one-cent cell offsets optimized on the then-current entry/PnL frame. | **PRE** | A fixed offset from a reconstructed current-price basis. | Loaded; used by legacy/repost branches, but ATLAS supersedes the current initial signer. |
| Cohort surface | 6,119 `range_spectrum_v1` rows; 42 category × fav/dog × price cells, floor n=30; built and armed 2026-07-17 after the honest-clock migration. Reference is the spectrum anchor and subsequent dip/reach. | **POST** | Historical dip/reach and sanctioned-walk rate for the cohort cell. | `LIVE_CONTEXT`; faller steer can alter a preliminary target, but ATLAS still owns the initial chokepoint. |
| Band map B1–B8 | 12,170 legs; per-category k-means on standardized full-path `(anchor, net, dip)`; deterministic seed 20260717; published 2026-07-17 23:05 ET. | **POST** | Which ex-post print-derived trajectory cluster contained the completed leg? | Production read/cascade; not initial price authority. |
| Drift surfaces | Same 12,170-leg band population; movement/reach/low timing by ex-post band and clock bin; published 2026-07-18 01:30 ET. | **POST** | What historically happened inside an already known band? | Production read-side/context. |
| Sealed entry table | Band-depth/ROC stages, published after band/drift. Only two rows sealed; five refused; most rows explicitly `FAILED-HOLDOUT`. | **POST** | Whether a band-depth proposal survived its historical drill. | `_price_authority` can name it, but `pair_class_steer_enabled=false`; therefore `OVERWRITTEN` on initial entry. |
| Sealed pair policy | Band-pair classes and historical divot depths; sealed 2026-07-20. | **POST** | Historical pair-class depth under the band representation. | Loaded, but production steer is disabled; `SHADOW/OVERWRITTEN`. |
| Quote-shape library | 681 fit events / 1,343 fit legs after excluding five exact-start games; 16 category × first-formed-book-bid regions; 94 exact ask-path topology classes; first published 2026-07-31. Full-path features are ask net/dip/peak, dwell, spread, cadence, displayed volume, and top-five depth. | **POST** | Which quote-path topologies remain compatible with the prefix observed so far? | `V11_REPLAY_AUTHORITY`; absent from production. |
| Quote-shape pair tuples | Empirical two-leg shape pairs from the same 1,343-leg library, plus explicitly marked n=0 inverse structural closure. | **POST** | Which joint shape combinations remain possible? | `V11_REPLAY_AUTHORITY`; absent from production. |
| Descent ordinal | Within each quote-shape class, the upper median count of new-low ask descents at which the final 10-second/exact-five qualifying ask low first appears; fitted 2026-08-01. | **POST** | After a descent is observed, how many qualified new-low descents normally precede the final qualified low? | `V11_REPLAY_AUTHORITY` for 62 of 94 classes. |
| V11 persistence survival | 1,343 fit legs; 6,499 qualified-low episodes (2,287 followed by a later qualified lower episode; 4,212 terminal); 332 category × price region × shape × descent-ordinal cells; fitted 2026-08-02. Leave-one-leg-out upper-median wait to a later qualified lower ask. | **POST** | Has the fitted wait for another qualified lower ask been exhausted at this exact state? | Narrow `V11_REPLAY_AUTHORITY`; absent from production. |
| Shelf census | One-time worksheet dated 2026-07-17 00:49 ET. It explicitly says nothing arms from the dispatch. | **PRE**, but not a fit | Which older projects were ready, dark, merged, or buried on that date? | `DIAGNOSTIC`; never authority. |

ATLAS lineage and the exact pre-migration finding:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_initial_aim_constant_audit_20260731/ATLAS_P75_LINEAGE_RECEIPT.json

Band and drift source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/entrysurface_20260717/BAND_MAP.md

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/entrysurface_20260717/DRIFT_SURFACES.md

Quote-shape and V11 source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/persistence_floor_v11_fit_20260802/PERSISTENCE_SURVIVAL_LIBRARY_V11.json

Shelf source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/shelf/SHELF_CENSUS.md

Complete raw source panel for the remaining catalogued surfaces:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/trendpath/ATLAS_V1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/vps_inputs_20260729/state/cohort_surface_v1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/vps_inputs_20260729/state/entry_tables_sealed_v1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/vps_inputs_20260729/state/pair_policies_sealed_v1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/vps_inputs_20260729/trendpath/LIBRARY_V1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/vps_inputs_20260729/trendpath/ORIENT_V1.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/docs/policy/per_regime_offsets_v2.csv

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/docs/policy/entry_table_percell_conservative.csv

## Complete decision-point inventory

| ID | Level | What it decides | Consulted surface / operation | Does the fit answer the question? | State and winning path |
|---|---|---|---|---|---|
| 01 | Source | Event/ticker identity and two-leg membership | Catalog match, schedule join, `discover_markets` | Yes as identity; not a fit. | `LIVE_GATE`. Bad or absent identity prevents later entry reasoning. |
| 02 | Source | Whether conception is inside the lawful horizon | `_entry_lead_cap`, `_horizon_state`, Window-1 phase, guarded start/gun evidence | Yes as boundary evidence; not a price fit. | `LIVE_GATE`. |
| 03 | Source | Whether the market is already REAL-START/in-play | P0 gun/start state and entry-start gate | Yes as a safety classification; not a target fit. | `LIVE_GATE`; exits are a separate path. |
| 04 | Source | Whether a BBO is lawful enough to consume | Positive external bid/ask size, non-crossed book, preserved time/order | Yes; it answers observability, not future price. | Source gate in both paths. |
| 05 | Source | Whether the V11 quote book is “formed” | First lawful one-tick spread; its best bid selects the price region | **No fitted threshold.** A one-cent spread is a structural admission convention, not a learned definition of shape readiness. | `V11_REPLAY_AUTHORITY`; production does not load this library. |
| 06 | Source | Whether discovery liquidity is adequate | Discovery floor 1,500 shares; shelf also records a 2,500 proposal from the July 2–9 never-wake census | The 2,500 proposal answered dead-book economics; production still uses 1,500. Neither estimates the current ask floor. | 1,500 is `LIVE_GATE`; 2,500 is shelf-only/unarmed. |
| 07 | Source | Which current price may anchor an initial aim | Fresh last trade; tight-mid/BBO fallbacks in `_v4_entry_anchor` | The observation answers current price. It does not itself answer future dip. | `LIVE_CONTEXT` feeding the signer. |
| 08 | Source | Whether direct FV anchor placement is allowed | `fv_anchor_placement=false` | No fit at this switch. OFF routes to legacy deep-offset/ATLAS placement; ON would use the freshest non-zero trade-tape FV, clamped maker-safe. | `LIVE_GATE`; OFF in frozen config. |
| 09 | Source | Whether external sharp books can vote | Pinnacle + Betfair Exchange EU + Matchbook, all fresh within 60 minutes; no-vig average | Suitable for macro orientation/FV context; not fitted to a Window-1 ask floor. | `LIVE_CONTEXT`; direct FV pricing disabled. |
| 10 | Source | Whether last trade is causal rather than carried | Trade receipt identity and source time | Yes; evidence law. | Source gate. Carried values without identity cannot create V11 shape evidence. |
| 11 | Source | Whether the current target has displayed support | Same-tick top ask size and top-five ask depth | Yes as current capacity/context. Depth is not a scalar shape by itself. | Raw input; production depth governor and V11 micro layers consume different projections. |
| 12 | Source | Exact order quantity | Frozen five-contract entry size | **Unfitted constant.** It is the task size, not an empirical capacity threshold. | `LIVE_GATE` and V11 micro-micro gate. |
| 13 | Macro shape | Which leg is riser/faller | `_orientation_prior`: old ORIENT chain, sharp FV, cohort rose rate, incumbent fav/dog role | Mixed. ORIENT is pre-migration and candle/onset based; FV/cohort can support direction. None fits an entry price. | `LIVE_CONTEXT`; changes shallow/deep role, not the current production signer. |
| 14 | Macro shape | Historical cohort direction/dip context | Cohort category × role × price region | Only partially. It answers a spectrum-anchor dip/reach question, not “depth below the current quote.” | Faller steer can alter preliminary aim; ATLAS remains final initial signer. |
| 15 | Macro shape | Legacy B1–B8 class | Full-path print-derived `(anchor, net, dip)` k-means | **Wrong question for a causal quote-path call.** The eventual net/dip is unavailable early; the scorecard found 656/913 calls non-flat while every measured native call was FLAT. | Production cascade/read only. |
| 16 | Macro shape | Historical movement conditional on B1–B8 | Drift/reach/low timing surfaces | Answers “what happened after membership in an ex-post band,” not “which live prefix is this?” The recognition table is counted, not a signing fit. | `LIVE_CONTEXT`. |
| 17 | Macro shape | Initial V11 quote-shape candidate set | Category + first formed-book bid region → all exact topology classes | Yes for the intended quote-path universe, subject to coverage defects below. | `V11_REPLAY_AUTHORITY`. |
| 18 | Macro shape | Which quote shapes survive this tick | Minimum distance on ask net/dip first; spread/cadence/dwell/volume/depth only break ties | Mostly yes: it consumes causal quote-prefix observables. Exact-minimum selection has no uncertainty band and can over-collapse. | `V11_REPLAY_AUTHORITY`. |
| 19 | Macro shape | Whether a stale class must reopen | Observed new-low descent versus each surviving class’s fitted maximum ordinal | Yes when that behavior exists in training. No when a zero-descent class encounters an out-of-support descent. | `V11_REPLAY_AUTHORITY`; this is the dynamic re-narrow seam. |
| 20 | Macro shape | Resolved direction | Direction encoded in the remaining shape IDs | It is a derived label, not a separate fit. | V11 macro output; production does not consume it. |
| 21 | Pair micro | Whether current two-leg exposure respects the production pair limit | `_pair_seesaw_state`; sibling current BBO plus fitted/deep aim against combined goal 97 | It answers a cap/refusal question, not optimal sequencing or floor timing. | `LIVE_GATE`; can refuse, not jointly optimize. |
| 22 | Pair micro | Whether a sealed pair class can steer the target | Sealed pair policy / band pair class | Its fit answers a band-pair historical question, but the live switch is OFF. | `OVERWRITTEN`; `_price_authority` may name it while ATLAS submits another price. |
| 23 | Pair micro | Which V11 empirical pair shapes survive | Pair-tuple counts from fitted quote-shape assignments | Yes for observed tuple membership; sparse at pair grain. | `V11_REPLAY_AUTHORITY`. |
| 24 | Pair micro | Whether a missing empirical tuple may be admitted | Inverse-direction structural closure with support `n=0` | **Not fitted.** It is an algebraic completion of the 100-sum inverse relation, not evidence that the tuple occurred. | V11 proxy authority, explicitly distinguishable from empirical tuples. |
| 25 | Pair micro | Whether the sibling independently resolves the inverse | Sibling direction plus an observed move in that direction | Yes as causal proof; no statistical threshold. | `V11_REPLAY_AUTHORITY`. |
| 26 | Pair micro | Whether one surviving tuple plus sibling micro evidence is enough | Single inverse tuple + sibling’s own transition/stable-receipt proof | Partly. Empirical tuple is fit; “single tuple is resolution” is a deterministic gate. | `V11_REPLAY_AUTHORITY`. |
| 27 | Pair micro | Post-first-fill sibling budget | `combined_goal - realized first-leg basis` / event-specific headroom | Yes as arithmetic legality; not a prediction of a sibling floor. | Production `LIVE_GATE` after fill. It arrives too late to solve pre-fill sequencing. |
| 28 | Pair micro | Whether both legs have a named disposition | Shelf-origin pair-completeness invariant | It checks bookkeeping completeness, not market opportunity. | Live alarm only; no price authority. |
| 29 | Micro position | Initial production depth below anchor | ATLAS page p50 (or page statistic selected by path) | **No. Canonical wrong-question use:** fit = depth below first-hour median; consultation = depth below current last trade/tight mid. It is also pre-migration. | Production `LIVE_SIGNER`. |
| 30 | Micro position | Legacy fixed offset from current reconstructed basis | Per-regime/per-cell entry tables | Only for the old optimization frame. It does not condition on current ask path, dwell, or current quote-shape state. | Live in legacy/repost branches; superseded by ATLAS for current initial placement. |
| 31 | Micro position | Named sealed “fish” price | Sealed entry table | The few sealed rows answer their own staged ROC question; most rows failed. It does not answer a live prefix outside that band frame. | `OVERWRITTEN` when pair steer is OFF. |
| 32 | Micro position | Guidebook/LIVE_AIM price opinion | `LIBRARY_V1`, confidence floor 0.1 | Wrong clock and old first-hour print-volume key; not a quote-prefix floor fit. | `SHADOW`; NIKVRB returned `NO-OPINION`. |
| 33 | Micro position | TRADE versus DROP | Contention selector / ATLAS tier comparison | The scorecard found it inverted: DROP contained more good targets than TRADE. | `OVERWRITTEN`; `contention_drop_enforced=false`. |
| 34 | Micro position | Estimated probability a deep target is reached | Reach law using quiet/active flow buckets | Wrong calibration for the current reach law: 2,019 rows averaged 28.57% predicted versus 3.2% actual. | Context/shadow; cannot sign. |
| 35 | Micro position | FLOOR versus LOWER from shape path | Current progress-bin value of the surviving shape medoid | It answers one medoid’s raw future minimum, not the within-class distribution. The distinction between raw ask and qualified ask also creates internal contradictions. | `V11_REPLAY_AUTHORITY`, subordinate to ordinal/persistence adjustments. |
| 36 | Micro position | FLOOR versus LOWER after a descent | Fitted descent ordinal for exact category × region × topology | It asks the right qualified-ask question, but 32/94 classes have no positive-descent support and 49/94 fitted classes contain multiple ordinal outcomes. | `V11_REPLAY_AUTHORITY` where present. |
| 37 | Micro position | Whether no-ordinal LOWER has exhausted a later-low wait | V11 leave-one-leg-out persistence cell | It asks the right wait-to-lower question at exact state grain. Its incremental V11 result was 13 new actions and one additional execution-floor pair pass; it is not production authority. | Narrow `V11_REPLAY_AUTHORITY`. |
| 38 | Micro position | Whether a stable same-price ask is allowed to sign | Persistent unchanged size, pulse beyond spread and return, or inverse-sibling transition | **Unfitted logical predicates.** They were constructed from named specimens, not fitted population thresholds. | V11 gate. |
| 39 | Micro position | Candidate action price | Current observed ask when all upstream gates agree and it is the observed low | No price model: it is direct take-side placement in the research replay. | V11 action authority. Production remains maker-only. |
| 40 | Micro-micro timing | Whether ask evidence has dwelled long enough | `ask_dwell_seconds >= 10` | **Unfitted inherited constant.** | V11 gate. |
| 41 | Micro-micro timing | Whether five contracts are displayed | `top_ask_size >= 5` | **Unfitted task-quantity equality.** | V11 gate. |
| 42 | Micro-micro timing | Whether this is still the lowest ask observed | `current ask == observed ask low` | **Unfitted exact comparison.** | V11 gate. |
| 43 | Micro-micro timing | Whether evidence is causally new | Fresh own receipt and, for stable confirmation, a strictly later same-price receipt | **Unfitted chronology law.** | V11 gate; prevents a recognition receipt from proving itself later. |
| 44 | Micro-micro timing | Whether a production target would cross | Maker-only clamp to `ask - 1`; marketable target cannot lift the ask | Not fitted; execution doctrine. | Production `LIVE_GATE`. This differs materially from V11’s ask-priced action. |
| 45 | Micro-micro timing | Where a live join sits in displayed depth | Depth-aware join with 50-share wall floor | The 50-share constant was sized from an earlier filled-versus-starved/wall study, not fitted to the current quote-shape floor question. | Production `LIVE_SIGNER/GATE` on join branches. |
| 46 | Micro-micro timing | Whether a resting order follows a changed touch | Best-bid mismatch, maker clamp, depth governor, or legacy 5-cent mid deadband depending posture | Mixed and path-dependent. These are execution-maintenance rules, not one fitted price surface. | Production `LIVE_GATE`; later branches can overwrite the initial target. |
| 47 | Micro-micro timing | Whether quiet staircase preserves queue | Five-print trailing burst distinguishes quiet hold from volatile trail | The five-print burst is inherited, not fitted to ask recurrence/floor timing. | Production `LIVE_GATE`; quote-shape V11 does not use it. |
| 48 | Micro-micro timing | Late fallback behavior | T−20 minutes; maker clamp enabled | The 20-minute time is inherited configuration, not fitted to current shape. | Production `LIVE_GATE`. |
| 49 | Micro-micro timing | Four-signal round-5 immediate cross | `round5_detector_fire` | No surface is consulted: the function is an explicit `return False` stub. | `DEAD`. |

The 913 band calls, 656 non-flat outcomes, 2,019 reach rows, 28.57% versus
3.2%, and the other scorecard values in rows 15, 33, and 34 come from:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_organ_scorecard_20260731/ORGAN_SCORECARD.json

The V11 “13 new actions / one pair pass” result comes from:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/FUNNEL_AND_FIVE_CEILINGS.json

## Duplicates and conflicts

| Question | Coexisting answers | Authoritative answer now |
|---|---|---|
| What is the initial price? | Legacy regime/per-cell offset; cohort p50 dip; ATLAS depth; sealed band fish; LIVE_AIM guidebook; direct FV anchor; V11 current ask | **Production:** ATLAS, because `interim_entry_aim_mode=ATLAS`, `fv_anchor_placement=false`, and `pair_class_steer_enabled=false`. **V11 research:** current ask only after the quote-shape chain clears. No cross-system authority promotion is implied. |
| What shape is this? | ORIENT first-hour direction; cohort rose/fall rates; B1–B8 band; pair-class label; quote-shape topology | **Production:** orientation is role context and band is read-side; no macro shape signs initial price. **V11:** quote-shape survivor set is authoritative. |
| Is the current ask the floor? | ATLAS old path bottom; band drift/low timing; static quote medoid; descent ordinal; V11 persistence | **V11 order:** medoid base → descent ordinal where fitted → narrow persistence only in its frozen no-ordinal/exhaustion seam. ATLAS timing is rejected due clock mismatch; band drift is context. |
| What does the sibling imply? | Production seesaw/97 cap; sealed pair class; empirical quote pair tuple; n=0 inverse closure; post-fill headroom | **Production:** seesaw/cap before fill, headroom after fill. **V11:** empirical tuple first, explicitly proxied inverse closure only where the pair table is absent. |
| Is it time to act now? | Production touch/repost/fallback constants; V11 transition/stable signer; dwell/capacity/fresh receipt | There is no shared fitted timing authority. Production uses its execution rules; V11 uses unfitted micro-micro predicates after fitted macro/micro gates. |
| What did the shelf authorize? | AIM_V2, window truth, expression, chain proof, reach recal, discovery floor proposals | Nothing. The shelf says it is a disposable worksheet and nothing arms from it. Later code/commits, not the shelf, determine current state. |

The three generations are therefore not an ensemble. ATLAS is a production
signer built for an old anchor/clock question. Band/drift is a later descriptive
print taxonomy. Quote-shape/ordinal/persistence is a still later development
decision tree. Averaging or voting them would mix incompatible target variables.

## Empty layers and unfitted constants

Micro-micro has no fitted surface. It consults direct evidence plus inherited
constants. Every such decision is listed here; “logical” means required for
causal identity, not empirically calibrated.

| Constant/predicate | Value | Provenance | Status |
|---|---:|---|---|
| Formed-book spread | exactly 1 cent | Quote-library construction convention, first published 2026-07-31 | Unfitted admission constant. |
| Ask dwell | at least 10 seconds | Inherited reachability convention used by the organ scorecard and quote library | Unfitted timing constant. |
| Displayed capacity | at least 5 contracts | Frozen order quantity/exact-five law | Unfitted task-size constant. |
| Ask position | current ask equals observed low | Exact logical comparison | Unfitted. |
| Same-price confirmation | receipt timestamp strictly later | Causal no-self-proof law | Unfitted. |
| Fresh action receipt | action must use the current own-book receipt | Causal no-stale-action law | Unfitted. |
| Stable-size support | top ask size never changed | Stable-signer specimen rule | Unfitted boolean. |
| Pulse support | ask peak exceeds contemporaneous spread and returns | Stable-signer specimen rule | Unfitted comparison. |
| Inverse-sibling support | sibling moved in resolved inverse direction | Pair wiring logic | Unfitted boolean once direction is resolved. |
| Maker clamp | target at most ask minus 1 | Production maker-only doctrine | Unfitted execution rule. |
| Depth wall | 50 shares | Earlier offline wall/perch study; configured `depth_aware_floor=50` | Borrowed, not fitted to current floor timing. |
| Best-bid follow gap | at most 15 cents | Production configuration | Inherited/unfitted for this question. |
| Staircase burst | 5 recent prints | Production configuration | Inherited/unfitted. |
| Fallback clock | 20 minutes before start | Production configuration | Inherited/unfitted. |
| Combined goal | 97 cents | Production pair policy | Policy constant, not fitted micro timing. |

V11 micro-micro code provenance:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/analysis/window1_quote_shape_micro_position_v2.js

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/analysis/window1_quote_shape_pair_wiring_v3.js

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/analysis/window1_quote_shape_stable_signer_v4.js

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/analysis/window1_quote_shape_descent_verdict_v10.js

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/arb-executor/analysis/window1_quote_shape_persistence_floor_v11.js

## Shape-library coverage ruling

The quote library has **94** classes. **32** have no positive-descent ordinal;
they are exactly `FLAT_UNMOVED` and `UP_CONTINUATION` in each of the 16
category × starting-price regions. **72** classes have fewer than 20 members.
Only 22 meet n≥20. **49** contain more than one observed qualified-descent
ordinal, so a single median cannot express every member path. **16** have an
even sharper definition conflict: the class has no qualified-descent ordinal,
yet its selected medoid says a lower raw ask remains at one or more progress
bins. The raw-ask future and the 10-second/exact-five qualified future are not
the same target variable.

All five counts and every class identity are enumerated in:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json

The compact category × price-region enumeration is frozen beside this report in
`SHAPE_LIBRARY_COVERAGE_GAPS.md`.

## Curation conclusion

The current tree has no single coherent fit lineage. Its production price is
signed by a pre-honest-clock surface answering “depth below the first-hour
median,” while the newest quote-native representation is development-only and
does not span descent behavior in 32 classes. The empty micro-micro layer then
turns the surviving macro/micro answer into action using inherited constants.

This is an inventory finding only. It does not select a repair, promote V11,
change a switch, run a replay, or alter an order path.
