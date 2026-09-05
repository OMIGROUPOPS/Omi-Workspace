# Window-1 Watch face fields

tape.<LEG>[].t <- CSV ts_et parsed as America/New_York, converted to epoch seconds, minus altgas.json bell.first_stage_epoch, divided by 3600
tape.<LEG>[].bid <- CSV bid_1
tape.<LEG>[].ask <- CSV ask_1
tape.<LEG>[].last <- CSV last_trade; stored 0 becomes null
tape.<LEG> change compression <- emit the first row and each later change in CSV (bid_1, ask_1, last_trade)
os[].t <- stages[].timestamp_epoch or others[].timestamp_epoch or others[].fill_event_receipt.context.fill_timestamp_epoch, minus bell.first_stage_epoch, divided by 3600
os[].receipt <- stages[].receipt, others[].receipt, or others[].fill_event_receipt.captured_at_receipt
os[].kind <- stages[].kind or others[].kind
os[].legs.<LEG>.bid <- stages[].books.<LEG>.bid_cents
os[].legs.<LEG>.ask <- stages[].books.<LEG>.ask_cents
os[].legs.<LEG>.running_low <- stages[].lows_travel.<LEG>.observed_traded_low_cents
os[].legs.<LEG>.survivors <- stages[].macro.survivor_shapes.legs.<LEG>.survivor_shapes.length; stages[].shape_survival.<LEG> stores no survivor IDs or count
os[].legs.<LEG>.member_count <- stages[].derivations[leg_id=<LEG>].overlap_membership.member_count (fallback: derivation membership_count)
os[].legs.<LEG>.weight_sum <- stages[].derivations[leg_id=<LEG>].overlap_membership.weight_sum (fallback: derivation membership_weight_sum)
os[].legs.<LEG>.member_remaining_dip_zero_weighted_share <- sum stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].conditioning_weight where member_remaining_dip = 0, divided by the sum of all positive finite posterior conditioning_weight; null when there is no weighted posterior
os[].legs.<LEG>.candidate_level_q10_cents <- lower-bound cumulative weighted q10 of stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].candidate_level_cents using positive finite conditioning_weight; no interpolation
os[].legs.<LEG>.candidate_level_q25_cents <- lower-bound cumulative weighted q25 of stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].candidate_level_cents using positive finite conditioning_weight; no interpolation
os[].legs.<LEG>.candidate_level_q50_cents <- lower-bound cumulative weighted q50 of stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].candidate_level_cents using positive finite conditioning_weight; no interpolation
os[].legs.<LEG>.candidate_level_q75_cents <- lower-bound cumulative weighted q75 of stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].candidate_level_cents using positive finite conditioning_weight; no interpolation
os[].legs.<LEG>.candidate_level_q90_cents <- lower-bound cumulative weighted q90 of stages[].derivations[leg_id=<LEG>].derivation.pricing_authority.true_conditioning.posterior_rows[].candidate_level_cents using positive finite conditioning_weight; no interpolation
os[].legs.<LEG>.sentence.status <- stages[].micro.beliefs.<LEG>.status
os[].legs.<LEG>.sentence.P <- stages[].micro.beliefs.<LEG>.belief_price_cents
os[].legs.<LEG>.sentence.Q <- stages[].micro.beliefs.<LEG>.predicted_cents
os[].legs.<LEG>.sentence.X <- stages[].micro.beliefs.<LEG>.phase_projection_telemetry_cents
os[].legs.<LEG>.sentence.q_author <- stages[].micro.beliefs.<LEG>.q_author
os[].legs.<LEG>.sentence.x_author <- stages[].micro.beliefs.<LEG>.x_author
os[].legs.<LEG>.sentence.plain_sentence <- stages[].micro.beliefs.<LEG>.plain_sentence
os[].legs.<LEG>.action.name <- stages[].derivations[leg_id=<LEG>].action.action
os[].legs.<LEG>.action.target_cents <- stages[].derivations[leg_id=<LEG>].action.target_cents
os[].legs.<LEG>.action.reason <- stages[].derivations[leg_id=<LEG>].action.reason
os[].legs.<LEG>.rest.action <- stages[].derivations[leg_id=<LEG>].action.action when PLACE_REST or REPRICE_REST
os[].legs.<LEG>.rest.cents <- stages[].derivations[leg_id=<LEG>].action.target_cents when PLACE_REST or REPRICE_REST
os[].legs.<LEG>.rest.lane <- stages[].derivations[leg_id=<LEG>].layered_dual_belief.envelope_placement.writer_lane
os[].legs.<LEG>.rest.mode <- stages[].derivations[leg_id=<LEG>].layered_dual_belief.envelope_placement.mode
os[].legs.<LEG>.print.cents <- others[kind=FLOOR_PRINT_DECISION_INSTANT].print_price_cents for others[].leg_id=<LEG>
os[].legs.<LEG>.fill.cents <- others[kind=FILL_EVENT].fill_event_receipt.context.entry_cents for context.leg_id=<LEG>
bell.t <- altgas.json bell.hours_to_truth_bell_at_first_stage
bell.timestamp_epoch <- altgas.json bell.first_stage_epoch + bell.hours_to_truth_bell_at_first_stage * 3600
bell.source <- altgas.json bell.bell_source
provenance.event_id <- altgas.json provenance.event_id
provenance.trace_sha256 <- altgas.json provenance.trace_sha256
provenance.os_sha256 <- custody-bound PRINT_PRICED_RESIDUE_SWEEP source_files entry for window1_v54_dual_belief_os.js, only when the same run's EXTERNAL_CUSTODY_MANIFEST binds this exact trace SHA; alternatively FACE_RUN_PROVENANCE with matching before/after OS hashes and trace hash. Never hash today's OS to label an old trace. Absent binding -> null / STORE SILENT.
build_face_data.mjs --trace <trace> --tape-dir <dir> <- streams the trace and projects the same face fields without materializing altgas.json; provenance.trace_sha256 hashes that trace
shell/public/data/altgas.face.json <- npm run face:data copies data/altgas.face.json through shell/scripts/copy-face-data.mjs
stand-down/pull action series <- STORE SILENT; exported action names are HOLD_REST, PLACE_REST, and REPRICE_REST

## FACE v2 — TUNE TEST

`rerun_game.ps1 -Event <id> [-Custody <directory-or-trace>] [-Bench <file-or-none>]`
uses the current worktree. Explicit custody never runs or modifies the engine. Automatic discovery
checks the event's saved trace, then existing C:\tmp v54 custody traces. A missing event invokes
the existing builder with rerun_altgas's frozen private/cache/walk/foundation arguments.
The operator authorized a temporary same-line stories append for this fallback only;
the original builder bytes are restored in `finally`. No OS module is changed.
When substituting a different extra, the saved ALTGAS extra is removed from that same line
before the requested event is appended; the four bed stories remain, not an accumulating sixth story.
Fresh fallback outputs live in this folder's ignored `.runtime/` directory.

The exporter `--manifest-only` is a streaming census/index, not a replacement stage format.
The face builder streams the complete source itself and writes one lazy receipt per matched row.
The main and lazy JSON resources have lossless `.json.gz` storage/HTTP representations;
`shell/scripts/face-data-plugin.mjs` serves the requested `.json` URLs with Content-Encoding gzip.
`npm run face:data` mirrors the resources into shell/public/data; dev serves canonical data directly.
The 2 MiB transfer guard applies to the compressed main resource, never to an inspector row.
Grok tokens, fonts and original chart components are retained. TUNE TEST is the default route;
legacy components remain on disk, but do not author TUNE TEST values.

### Provenance and catalog

| Key | Source / derivation |
|---|---|
| version | Contract version 2; not a market observation |
| category | First DECISION_STAGE reads.category.value.category |
| formation_end_epoch | First stage micro belief own_evidence.formation_end_epoch |
| provenance.trace_path | Exact input custody trace path |
| provenance.os_hash_source | The custody source-hash receipt actually used |
| provenance.custody_manifest_sha256 | SHA256 of the matching custody manifest or FACE_RUN_PROVENANCE |
| provenance.os_receipt_sha256 | SHA256 of PRINT_PRICED_RESIDUE_SWEEP when used |
| provenance.bench_sha256 / bench_label | Hash / stored label of TUNE_BENCH_NAMED_CHECKS, only if an event_id matches |
| first_tick.epoch / mtb_first / source / receipt | Earliest stored decision where BOTH legs' true_trade_count > 0; epoch = first-stage epoch + t*3600, mtb = (trace bell - epoch)/60; raw receipt and rule named. If unavailable, a named bench's first true tick epoch can be mapped to the TRACE bell, never its different clock. If neither exists, fail loudly. |
| bench.present / label / source | Whether named checks contain this exact event, their stored label, source filename |
| bench.bell_epoch | Named first_tick.epoch + named first_tick.mtb_first*60 |
| bench.clock_delta_seconds | Bench bell epoch minus trace bell epoch |
| bench.clock_status | ALIGNED only if bell epochs round to the same epoch second; otherwise CLOCK_MISMATCH_STORE_SILENT. No bench => STORE_SILENT. This is a join check, not a model threshold. |
| data/index.json games[] | Every event with a face resource, duplicate aliases consolidated in favor of version 2 |
| games[].event/category/os_sha/trace_sha/bench_sha/bell/first_tick/version | Corresponding stored face keys, unchanged |
| games[].url | Relative JSON resource URL for that file |

### Receipt rows and the full inspector

`data/<event>.stages/<receipt_id>.json` is the logical lazy resource; its on-disk gzip
contains `{source, inspector, row}`. `row` is the WHOLE parsed original trace row:
all lanes, eligibility, winners, authority, seats, ladder/clip, coherence, statuses,
and any unknown/future fields survive. Nothing is whitelisted out of this row.
The tree mounts collapsed branches on demand; there is no array cap or truncation.

| Key | Source / derivation |
|---|---|
| source.event_id / receipt / trace_row | Matched event, raw receipt, physical nonblank source row number |
| os[].receipt_id | SHA256(kind + NUL + raw receipt + NUL + source row number), collision-safe filesystem name |
| os[].detail_url | Logical `/data/<event>.stages/<receipt_id>.json` |
| os[].index | Stable chronological receipt ordinal; equal timestamps retain source projection order |
| os[].minutesToBell / clock_label | (bell.t - os.t)*60, and that value formatted to 2 decimals plus `m to bell` |
| os[].statuses | Original layers.<macro/micro/micro_micro>.context.status |
| os[].standing.<leg> | Only credited, entry_cents, standing_target_cents from reads.half_pair_state.value.legs; full state stays in the inspector |
| os[].legs.<leg>.last / true_trade_count | reads.books.value.<leg>.last_trade_cents / reads.lows_travel.value.<leg>.true_trade_count |
| os[].legs.<leg>.sentence.family | Stored micro belief family; not a new classification |
| os[].legs.<leg>.sentence.predicted_minutes_to_bell | Stored micro belief value; full deadline object stays in the inspector |
| os[].legs.<leg>.sentence.authority_source | derivations[leg].derivation.pricing_authority.authority_source |
| inspector.statuses / coherence / seats_before | Original layer statuses, row.coherence, reads.half_pair_state.value |
| inspector.legs[].leg_id / action | Original derivation leg_id / action |
| inspector.legs[].placement | Stored envelope_placement mode, writer_lane, chosen_target_cents, may_originate_rest |
| inspector.legs[].lanes_and_winner | Complete layered_dual_belief.decision_arbitration |
| inspector.legs[].seat | Stored layered_dual_belief.prediction_seat |
| inspector.legs[].authority_target / authority_source | Stored derivation.pricing_authority.target_cents / authority_source |
| inspector.legs[].derivation_keys | Original derivation object's keys, as a navigation index |

### Builder-authored replay and HUD values

All the following are produced by `face_contract.mjs`. The browser only decodes, selects,
formats units, draws geometry, and navigates; it does not sum prices, infer roles, count
members, update rests, construct sentences, or recompute a clock.

| Key | Source / derivation |
|---|---|
| os[].display.legs.<leg>.current_rest / rest_label | Latest PLACE_REST/REPRICE_REST target, cleared by that leg's FILL_EVENT or explicit PULL_REST/CANCEL_REST. Label is stored cents + unit, or `none` only when the state is known. |
| rest_known | Whether a prior decision/standing state has been observed; unknown is not zero |
| last_fill | Last stored FILL_EVENT entry_cents for this leg |
| member_count / member_label | Stored overlap membership count; no fallback to shape count |
| member_percent | Count / maximum stored count for that leg in this replay ×100, display scale only; null if unavailable |
| sentence | Most recent stage plain_sentence, else its recorded status, else STORE SILENT |
| belief | Stored status, P, Q, X with labels; X retains the legacy phase_projection_telemetry_cents meaning, not a silently substituted deadline |
| authors | q_author, x_author, authority_source with labels |
| family | Most recent stored micro belief family |
| band / q10 / band_line | Existing weighted q25/q75 pair, q10, and weighted no-further-dip share formatted as percent; no numeric fallback |
| action / lane / hand_line | Current row action; stored placement writer_lane, or active rest's previously stored lane; target and lane labeled explicitly |
| saw | Most recent stage's bid, ask, last, running_low; never substitute the tape snapshot into what the OS saw |
| display.pair_sum | For each side use credited fill entry if present, otherwise active rest; sum ONLY if both exist |
| pair_label / pair_percent / above_par | Stored pair sum against operator-requested par 100; gauge width clamped to 100, red iff sum >100 |
| display.fills | Cumulative recorded fill events with leg, cents and trace-clock label |
| os[].title | Recorded PLACE/REPRICE/non-HOLD action or fill, otherwise literal row kind with spaces |
| os[].bench_checkpoint | Last completed checkpoint ordinal, not a future bench row |

### Charts, checkpoints and bench joins

| Key | Source / derivation |
|---|---|
| render.columns / ticks | Columnar frame matrix. Columns decode directly; no client numeric derivations |
| ticks.minutesToBell / hours / clock_label | Source time projected onto the trace bell clock / first-stage clock / preformatted label |
| ticks.receipt_index / checkpoint_index | Latest receipt and completed checkpoint at or before that instant |
| ticks.firstLast/Bid/Ask, secondLast/Bid/Ask | As-of (never nearest/future) tape row on face.legs[0]/[1] |
| ticks.firstRest / secondRest | Builder-replayed current rests |
| ticks.firstBand/firstQ10, secondBand/secondQ10 | Builder-carried stage bands; missing => null, never interpolate a missing series |
| render.axis.start_minutes_to_bell / end_minutes_to_bell | Stored first real pair tick mapped to trace bell / bell zero |
| axis.ticks | First real pair tick, in-window operator-requested gates, bell |
| axis.price_domain / price_ticks | Min/max and selected order statistics of actually stored plotted values, display scale only; no invented price anchors |
| render.checkpoints[].minutesToBell / label / position_percent | Operator-requested gate, label, position on the stored first-tick-to-bell axis |
| checkpoints[].frame / receipt_index | Existing frame at that exact gate / latest stored OS receipt at that instant |
| checkpoints[].bench | Named row by event_id and gate, ONLY on aligned trace/bench clocks; absent or mismatch => null |
| bench.minutes_to_bell / status / roles | Original named gate clock/status/recognition.<favorite/underdog>.current_role mapped by named first_tick leg ids |
| bench.validity.status/share/ess | Original validity status/weighted_share/ess |
| bench.validity.label / meter_percent | Stored share formatted as percent; meter lights only for status OK and ESS>=10. Low ESS remains explicitly labeled telemetry, not a forecast call |
| bench.rules.<rule>.ess/label/status | Original raw pool ESS, formatted label, status; all rules retained, none silently selected as the OS author |
| bench.rules.<rule>.sides.<leg>.status/ess/family | Original per-side status/usable ESS; family top only when side status OK, otherwise null |
| render.fill_events[] | Every stored FILL_EVENT: leg, minutesToBell, entry cents, label, receipt_index |
| render.misses[] | Remaining unfilled rest at bell. `never_returned` iff all finite subsequent pre-bell tape last values exceed rest; no following prints => null. Label distinguishes unfilled from tape-never-returned. Not a maker-fill simulation. |
| render.total_frames / receipt_count | Lengths of stored frame / receipt arrays, for diagnostics |
| render.verification.<leg>.first_rest/first_fill | First recorded rest/fill row, receipt/id/url, t, minutes_to_bell, cents, lane, authority_source |

`dictionary` and `{$ref: ordinal}` losslessly intern repeated os strings/objects. `face_encoding.mjs`
unpacks them; the browser's decoder performs the same reference lookup. No value changes.
The inspector keeps the original row without dictionary encoding. Prices and numeric nulls
remain exact. HTTP gzip and this dictionary are storage encoding, not data sources.

Missing overlap count/bands in old traces stay STORE SILENT even when a shape survivor count
exists. Missing actions are not relabeled HOLD; missing authority is not inferred from lane.
Bench roles/families remain separate from the OS's stored sentence/family and carry the bench label.

### Pre-first-tick inspection is not replay

`render.ticks[].pre_first_tick` is the builder comparison of that frame's trace-clock time
with the first real pair tick. `render.play_start_frame` points at the first playable frame.
Play and the replay scrubber start there; pre-first-tick inspection disables Play.
`render.inspection_axis` has the same fields as axis, but begins at the first stored OS row.
Earlier requested gates are available only as labeled inspection buttons, with
`checkpoints[].playable=false` and `position_percent=null`; they do not extend the playable level.
`first_tick.clock_label` is the first tick's stored trace-clock value formatted to two decimals.
Normal axis price bounds/order statistics use only playable frames; inspection axis bounds
include pre-first-tick observations. Earlier out-of-play spreads do not squash the replay chart.
`ticks.plot_remaining` is minutes-to-bell divided by that frame's playable/inspection
axis span, clamped to [0,1]; `plot_progress` is its complement. These are display
coordinates, not predictions. Static SVG paths are clipped at this stored position;
hover and click refuse future frames. Prices use step-after holds, so an unseen later
print cannot influence the visible curve through spline interpolation. This avoids
rebuilding all chart geometry on every receipt; Grok's tokens and line weights remain.
Fill `plot_progress` / `inspection_progress` are its normalized time positions on
those two axes; `plot_price` / `inspection_price` are (axis high − fill cents) /
(axis high − axis low), or null for a degenerate axis. The browser applies these
stored coordinates to chart pixels. Fill markers appear only after their receipt
ordinal, including when several actions share a timestamp.
`os[].legs.<leg>.action.lane` is the current derivation's envelope_placement.writer_lane;
the hand line prefers this explicit current lane over the active rest's previous lane.
`os[].trace_row` preserves the original nonblank JSONL row ordinal. Replay sorts by time,
then this ordinal, so equal-time decisions, prints and fills keep custody-file order.
Legacy exports without row ordinals retain stable projection order at equal times.
Distinct receipts at an identical clock time each retain their own frame and rest
state. Receipt stepping selects that receipt's frame; a gate selects the last receipt
already stored at its exact instant. Zero-duration states are not stretched in time.
The no-argument/`--input` build retains the original unencoded `os[]` contract for
`rerun_altgas.ps1` and the legacy page. FACE v2 requires `--trace` so that every
inspector can retain its complete original row; `rerun_game.ps1` always supplies it.

For the requested ab2345de URSPAL trace, 480m is BEFORE the first real pair tick.
Also its stored bench bell differs from its trace bell. The 480 inspection must not
be presented as a playable checkpoint or as an aligned bench evaluation.

## Recorded floors — RULER — NOT AN OS INPUT

`recorded_truth.mjs` reads only the git blob at
`c0056976c446afcb4d9603796a2e06c068ee94d6:.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.csv`.
It never reads the working-tree version or substitutes a tape/trace/bench minimum.
The actual CSV column names are `legA_floor_c` / `legB_floor_c` and
`legA_floor_epoch` / `legB_floor_epoch`; the normalized per-side output calls them
`floor_cents` and `floor_epoch`. Join is exact `event_id` plus `legA`/`legB` id.

| Key under top-level `truth` | Meaning / derivation |
|---|---|
| role | Literal `RULER — NOT AN OS INPUT`; retrospective, never a prediction or a fill credit |
| event_id / table_commit / table_path / table_sha256 | Exact join id, full pinned git commit, path, SHA256 of the full git-blob bytes |
| row_sha256 / row_number / row_csv | SHA256 of the exact UTF-8 CSV record excluding only its terminating CR/LF; one-based CSV record ordinal including the header; original record retained for independent verification (quotes/spacing unchanged) |
| verified_span / status / reason | Original span status; only `OK` licenses floors. UNKNOWN / NO_FORMATION / EMPTY and missing rows remain STORE SILENT with the literal status/reason |
| span_start_epoch / span_end_epoch | Original verified span bounds; missing bounds or a floor outside them cannot license a marker |
| bell_epoch / bell_source | Existing game's `face.bell.timestamp_epoch`, the explicit clock conversion input, not a replacement truth-table bell |
| table_bell_epoch / table_bell_source / table_bell_delta_seconds | Original table bell and source, and table bell minus face bell; preserve any clock disagreement |
| legs[leg].source_columns / anchor_cents | Exact CSV column names and that side's `open_postformation_c`; used only for favorite/underdog display order |
| legs[leg].floor_cents / floor_epoch | Recorded verified-span floor and its original epoch; null if unverified/missing |
| legs[leg].minutes_to_bell | `(face.bell.timestamp_epoch - floor_epoch) / 60`; never use the expected approximate time from a prompt |
| legs[leg].status / reason / line / marker_label | Leg-level availability/reason and builder-formatted floor, time (two decimals), and ruler label |
| favorite_leg / underdog_leg | Higher/lower recorded postformation open; equal or missing opens do not invent an orientation |
| pair.sum_cents / discount_cents | Favorite floor + underdog floor, and `100 - sum`; only when both floors and orientation are available |
| pair.line / discount_line / reason | `best capturable = <fav floor> + <dog floor> = <sum>¢`, `<discount>¢ under par`, or explicit STORE SILENT reason. This is a hindsight ruler, not a claim our orders could fill there |
| legs[leg].markers.play / inspection | Builder-authored normalized time `progress` and downward price `price` coordinates on the corresponding chart axis |

Marker `display_progress` clamps the display coordinate to the visible axis only.
If outside, `boundary`, `glyph` and `label` explicitly identify an edge flag before
or after the visible span; the original floor epoch/minutes are never clamped.
For a flat price axis, marker `price=0.5` means its visual midpoint, not a new price.
PAL's table epoch is 0.037s before this trace's first pair tick, so its normal-play
flag is explicitly an edge flag; its inspection-axis flag is at the exact time.

Recorded horizontal lines and time flags are deliberately visible across replay,
including before the floor was observed, and separately labeled as the ruler.
They do not enter `os`, receipt stepping, rests, fills, sentences, membership or bench
metrics. Display-only axis bounds can expand to include a recorded floor; fill
marker pixel coordinates are then reprojected without changing fill cents/time.

`build_face_data.mjs` adds the ruler after OS/trace projection. To update existing
faces without a replay or rewriting inspector rows:
`node window1-watch/refresh_recorded_truth.mjs <event_id> [<event_id> ...]`.
The refresh changes only top-level truth and any necessary display geometry.

Pinned-source discrepancy: ALTGAS is 58¢ at **3362.5583333333334m**, 38¢ at
**425.5383333325386m** on the existing game's bell, not approximately 3940/330m.
URSPAL keeps the existing trace bell; its table bell is 2853 seconds later.

## Visible ruler, bid-action markers and fill cards

`chart_actions.mjs` is a face-only receipt projection, invoked by the trace-backed
`build_face_data.mjs` after the ruler is attached. For existing faces, run
`node window1-watch/refresh_chart_actions.mjs <event_id> [<event_id> ...]`, then
`npm run face:data` in `window1-watch/shell`. This reads the existing full stage
`.json.gz` receipts, verifies their event/trace-row binding, and preserves the OS
dictionary, tape, bench and provenance. It neither executes nor imports the OS.

### Token gloss table

Raw tokens are always displayed next to these exact operator-supplied glosses.
Matching is exact except the three explicitly licensed prefixes. Unknown or
absent tokens have gloss `STORE SILENT`. A lane gloss is never substituted for an
unknown `action.reason` gloss, and no token is inferred from another field.

| Raw token / prefix | Plain-English gloss |
|---|---|
| INSUFFICIENT_AUTHORITY_NO_WRITER | no organ wrote this; the library prior was executed |
| LADDER_SHRINK_Q_CLIP_WRITER | a cheap ending died; bid stepped to the ladder |
| PREDICTION_SEAT_IMMUNE | frozen by the seat until its deadline |
| IMMUNITY_HOLD | frozen by the seat until its deadline |
| FLOOR_CAPABLE_WRITER | the two internal views disagreed; posted anyway |
| PAL_ATOMIC_* / GIU_* / LAJSVA_* | named hand (bed-only branch) |
| DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT | views disagree; no bid |
| BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE | STORE SILENT |
| Q_MOVE_LICENSED_BY_CANDIDATE_FINAL_FLOOR_LADDER_SHRINK | STORE SILENT |
| Any other or absent token | STORE SILENT |

The last two named rows are observed ALTGAS action reasons, not new interpretations.
Other encountered URSPAL reasons include
`COHERENT_LIVE_DEADLINE_PREDICTION_SEATED_AT_UNIFIED_AIM_CONDUCT_POSTERIOR`,
`PREDICTION_SEAT_REDERIVED_TO_OWN_UPDATED_CONVICTION_SAME_RECEIPT`, and
`NON_PRINT_DEAD_OR_SHALLOW_REST_RESEATED_TO_HIGHEST_POSTABLE_LIVE_LADDER_RUNG`:
each remains raw with `STORE SILENT` gloss. Its `PAL_ATOMIC_...` reasons use the
explicit bed-only prefix gloss above.

### Stored chart fields

| Key | Source / display derivation |
|---|---|
| truth.legs[leg].chart_label | `recorded floor <floor_cents>¢ · <whole minutes>m to bell`; whole minutes truncated toward zero for the compact label only. Full precision remains in `minutes_to_bell` and the two-decimal flag hover. Source remains pinned truth @ c0056976, never tape minima |
| truth.pair.compact_line | `best capturable <sum_cents>¢ · <discount_cents>¢ under par`, or the explicit unavailable reason. Existing full arithmetic `pair.line` retained |
| render.ticks[].hover_lines | Preformatted source-clock label and both as-of tape books/last from that frame; absent values say STORE SILENT. Browser displays the strings without calculating prices/text |
| render.bid_actions[] | Receipt-ordered action display records; ▲ PLACE_REST, ◆ REPRICE_REST or HOLD_REST with changed finite target, ✕ explicit cancel/pull/stand-down or observed uncredited standing target disappearance, ● FILL_EVENT |
| bid_actions[].id / leg / kind / glyph | Stable receipt-id + leg + action ordinal; source leg; display category PLACE/REPRICE/REMOVE/FILL; licensed marker glyph. A HOLD remains raw HOLD_REST even though it uses the diamond |
| receipt / receipt_id / receipt_index / trace_row / detail_url | Original receipt binding and full inspector URL; equal-time receipts are not merged |
| t / timestamp_epoch / minutes_to_bell | Existing face receipt hours, original decision epoch or fill context epoch, and existing trace-bell minutes. No prompt-example timestamps are used |
| old_cents / new_cents / old_known / new_known | Old standing target from `reads.half_pair_state.value.legs[leg].standing_target_cents`, else explicit envelope `active_target_before_cents`, else previously observed rest; new target from action. Explicit null means none; absent state means STORE SILENT, distinguished by known flags |
| marker_cents | New target for PLACE/REPRICE/changed HOLD; former target for removal/fill. No invented target when missing |
| raw.action / reason | Exact derivation `action.action` / `action.reason`. FILL_EVENT is the source row kind, not a fabricated REST action. Fill rows have no action.reason, so it stays null |
| raw.winner_lane | `layered_dual_belief.decision_arbitration.winner.lane`, NOT an envelope writer-lane fallback |
| raw.envelope_mode | `layered_dual_belief.envelope_placement.mode` |
| gloss | Approved table lookup for each raw field; unknown/null => STORE SILENT |
| sentence | Exact `os[receipt_index].legs[leg].sentence` projection. Includes status/P/Q/X/q_author/x_author/plain_sentence. Legacy X is phase-projection cents, not the separately stored deadline |
| book | Exact receipt `reads.books.value[leg]`, including bid_cents, ask_cents, last_trade_cents and source receipt. Never replace an absent last trade with tape, midpoint or running low |
| observation | Null normally. If a previously observed rest disappears from an uncredited half-pair snapshot without a removal action, explicitly states that source transition; raw action/reason stay absent. Credited disappearance is represented once by FILL_EVENT, not a duplicate cancel |
| label / hover_lines | Builder-formatted clock, raw action, old→new, raw winner/mode/reason + separate glosses, exact book, sentence fields and unabridged stored plain_sentence |
| markers.play / inspection | Normalized time progress and downward price coordinate for each axis; `display_progress` clamps only the edge hit target, `boundary` and `label` disclose an out-of-axis receipt. Original source time is unchanged |
| stack_offset_px | Successive coincident leg/time/price receipts offset their hit target by 18 display pixels to remain independently hoverable (e.g. simultaneous GAS PLACE + fill). No time or price changes |

Consecutive HOLD_REST rows with no target change get no marker. Their rest remains
the dashed line. Changed HOLD targets and explicit uncredited disappearance also
feed the builder's existing display rest carry; no new OS action is created.
There is no synthetic cancel at bell: existing miss fading remains separate.
Recorded floor lines are solid, full plot width, at 50% side-color alpha. The ruler
is retrospective and deliberately not clipped by the causal replay playhead.
Bid markers and fill cards are shown only once their receipt ordinal is reached.

### Fill card fields (`render.bid_actions[].fill`)

| Key | Source / derivation |
|---|---|
| context | Original `fill_event_receipt.context`, retained without reinterpreting execution credit |
| cents / triggering_print_cents | Context `entry_cents` / `triggering_print_price_cents`; execution limit and triggering print are distinct |
| place_receipt / place_receipt_id / place_timestamp_epoch | Most recent PLACE_REST for that leg's uninterrupted standing-rest lineage. REPRICE does not reset it; cancel/pull/uncredited disappearance/fill clears it |
| placing_sentence / placing_sentence_lines | Exact sentence and builder-formatted status/P/Q/X/authors/plain_sentence from that PLACE, not the latest reprice or a belief fabricated at the fill. Full text is available in the card's expandable sentence |
| rest_age_minutes | `(fill_timestamp_epoch - original PLACE timestamp_epoch) / 60`; missing PLACE or negative age => null / STORE SILENT. No nearest-row timestamp guess |
| recorded_floor_cents | Only `truth.legs[leg].floor_cents`; absent/unverified ruler => null |
| floor_difference_cents / floor_line | `entry_cents - recorded_floor_cents`; absolute difference labeled above/below the recorded floor. Null inputs => STORE SILENT |
| summary | Stored `<leg> filled <entry>¢ · <minutes>m to bell · print <print>¢ · rest had stood <age>m`. Clock and age display up to two decimals; full values retained |

FILL_EVENT rows themselves have no decision sentence, winner, envelope, reason or
book. These remain STORE SILENT in the fill marker hover; the separate *placing*
sentence is explicitly sourced in its card rather than relabeled as a fill-time belief.
ALT proof: four reprices 55→49→55→49→45; each stored reason is
`BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE`. GAS's card reads
`GAS filled 42¢ · 2880.73m to bell · print 41¢ · rest had stood 0m` and
`4¢ above floor 38¢`. The example 2965m does not match this trace's clock.
URSPAL's PAL fill is 39¢ against the separate recorded ruler of 40¢; the card
truthfully says `1¢ below floor 40¢`, rather than altering either historical source.
