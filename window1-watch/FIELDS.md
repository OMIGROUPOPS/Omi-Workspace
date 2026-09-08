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

## Plain-English cards (current display contract)

This section supersedes the earlier long-hover presentation and unknown-token
gloss rule. Default bid/fill cards contain exactly four builder-written lines in
`render.bid_actions[].card_lines`; the inline `details ▸` toggle is closed on each
new card. `details_lines` retains all original tokens, raw sentence, book and
deadline values. No token is removed from the source. A card line does not wrap;
on a narrow screen its text area scrolls horizontally instead of growing beyond
four lines. Expanding details is the only way to reveal the long raw content.

`plain_cards.mjs` reads the following table as data. These are display translations,
not new laws, prices, orders, or claims that the OS has a new organ. All 64 distinct
action/reason/lane/mode/authority/status tokens observed across GIUBAR, URSPAL,
LAJSVA, DANPRA and ALTGAS in the two custody traces have entries or licensed prefix
matches. The custody SHA256s, event row counts and tokens are in
`proof/card-token-inventory.json`. The actual picker currently has two face files
(ALTGAS and URSPAL); this change audits all five stories without adding games.

<!-- plain-card-gloss:start -->
| Token | Gloss |
|---|---|
| ACTIVE_REST_HOLD | kept the existing bid |
| ASK_ONLY_TICK_VETO_HOLD_STANDING_LAWFUL_REST | only the ask changed; kept the existing bid |
| ASK_ONLY_TICK_VETO_STAND_DOWN | only the ask changed; no new bid |
| AT_FLOOR_IMMUNITY_HOLD_ALL_ROUTINE_MOVERS | frozen by the seat until its deadline |
| BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE | the existing price forecast was used |
| CARRIED_CONVICTION_Q75_BASIS_RESTATED_SURVIVORS_HOLD | kept the bid after updating the remaining outcomes |
| CARRIED_CONVICTION_WRITER | carried the existing price belief forward |
| COHERENT_ENVELOPE_WRITER | the two internal views agreed on a bid |
| COHERENT_LIVE_DEADLINE_PREDICTION_SEATED_AT_UNIFIED_AIM_CONDUCT_POSTERIOR | the agreed forecast became a protected bid with a deadline |
| DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT | views disagree; no bid |
| ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET | the library supplied the forecast; this game's trading had not changed it |
| FLOOR_CAPABLE_WRITER | the two internal views disagreed; posted anyway |
| HOLD_REST | kept the bid |
| IMMUNE_PREDICTION_SEAT_FROM_UNIFIED_CONDITIONED_BELIEF_POSTERIOR | frozen by the seat until its deadline |
| INSUFFICIENT_AUTHORITY_NO_WRITER | no organ wrote this; the library prior was executed |
| INSUFFICIENT_AUTHORITY_STAND_DOWN | no price-writing organ had enough support; no new bid |
| INSUFFICIENT_EVIDENCE | not enough evidence to make this call |
| LADDER_SHRINK_NEXT_LIVE_RUNG_ADMITTED | used the next remaining ladder price |
| LADDER_SHRINK_NEXT_LIVE_RUNG_WRITER | a cheap ending died; used the next remaining ladder price |
| LADDER_SHRINK_Q_CLIP_ADMITTED | a cheap ending died; the ladder allowed a bid change |
| LADDER_SHRINK_Q_CLIP_PAIR_VETO_HOLD | the pair limit blocked the ladder move; kept the bid |
| LADDER_SHRINK_Q_CLIP_WRITER | a cheap ending died; bid stepped to the ladder |
| LAJSVA_* | named hand — a branch that only runs on this game |
| LAYERED_COHERENT_ENVELOPE_Q75_INSIDE_SPREAD_REACH | the agreed forecast supplied a reachable bid inside the spread |
| LIBRARY_FRACTION_PRIOR | the library supplied the forecast deadline |
| LICENSED_FLOOR_TENURE | the observed low had enough support to be used |
| LIVE_LADDER_RESEAT_WRITER | moved to a remaining ladder price that could be posted |
| LOCKED_BOOK_PLACEMENT_ONLY_EXISTING_REST_HELD | the locked book blocked a new bid; kept the existing bid |
| LOCKED_BOOK_PLACEMENT_VETO_EXISTING_REST_HELD | the locked book blocked a new bid; kept the existing bid |
| NON_PRINT_DEAD_OR_SHALLOW_REST_RESEATED_TO_HIGHEST_POSTABLE_LIVE_LADDER_RUNG | moved a dead or shallow bid to the highest postable remaining ladder price |
| NON_PRINT_HIGHEST_POSTABLE_LIVE_LADDER_RUNG_ADMITTED | used the highest remaining ladder price that could be posted |
| NO_ACTION | no bid action was selected |
| OWN_EVIDENCED_LIVE_TOUCH_ENVELOPE_NULL | this game's trading supplied no usable bid |
| PAIR_VETO_SKIPS_LADDER_CLIP_AND_HOLDS_WITHOUT_ABORT | the pair limit blocked the ladder move; kept the bid |
| PAL_ATOMIC_* | named hand — a branch that only runs on this game |
| PAL_LIVE_TOP_LADDER_RUNG_HELD_AFTER_NO_LIVE_PREDICTION_SEAT | named hand — a branch that only runs on this game |
| PAL_LIVE_TOP_LADDER_RUNG_HELD_AFTER_PREDICTION_SEAT_EXIT | named hand — a branch that only runs on this game |
| PANEL_PRIOR_UPDATED_BY_GRADED_CURRENT_GAME_OWN_EVIDENCE | the library forecast was adjusted by this game's own trading |
| PLACE_REST | placed a bid |
| POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST | the new price would take an offer; kept the existing bid |
| POST_ONLY_BLOCKED_NO_EXISTING_POSTABLE_REST | the price would take an offer; no bid was posted |
| PREDICTION_SEATED_REST_AT_UNIFIED_POSTERIOR_FLOOR | posted a protected bid at the combined forecast price |
| PREDICTION_SEAT_IMMUNE_UNTIL_TRACED_SUPPORT_OVERTURN_OR_OWN_DEADLINE_EXPIRY | frozen until its support is overturned or its deadline arrives |
| PREDICTION_SEAT_IMMUNITY | frozen by the seat until its deadline |
| PREDICTION_SEAT_IMMUNITY_HOLD_FROM_SEATING | frozen by the seat until its deadline |
| PREDICTION_SEAT_OWN_CONVICTION_LINEAGE | kept the forecast that originally placed the protected bid |
| PREDICTION_SEAT_OWN_CONVICTION_RESEAT_SAME_RECEIPT | this game's updated belief reset its protected bid |
| PREDICTION_SEAT_REDERIVED_TO_OWN_UPDATED_CONVICTION_SAME_RECEIPT | this game's updated belief reset its protected bid |
| PREDICTION_SEAT_WRITER | the forecast placed a protected bid with a deadline |
| PRICING_AUTHORITY_SILENT_EXISTING_REST_HELD | no new price forecast; kept the existing bid |
| PRICING_AUTHORITY_SILENT_HOLD_EXISTING_REST | no new price forecast; kept the existing bid |
| PRICING_AUTHORITY_TARGET_EXECUTED | posted the price the forecast supplied |
| POOL_CASCADE_WRITER | the selected pool supplied the bid |
| POOL_FIRST_TICK | games matched at the first tick supplied the price forecast |
| POOL_FIRST-TICK-ONLY | games matched at the first tick supplied the price forecast |
| POOL_BASE | the category base pool supplied the price forecast |
| POOL_FIRST_TICK_FLOOR_MTB | the first-tick pool supplied the floor deadline |
| POOL_FIRST-TICK-ONLY_FLOOR_MTB | the first-tick pool supplied the floor deadline |
| POOL_BASE_FLOOR_MTB | the category base pool supplied the floor deadline |
| POOL_CASCADE:FIRST-TICK-ONLY | games matched at the first tick supplied the forecast |
| POOL_CASCADE:BASE | the category base pool supplied the forecast |
| POOL_CASCADE:* | the stored cascade layer supplied the forecast |
| PRIOR_ONLY | the library supplied the price forecast |
| PRIOR_REWEIGHTED_BY_OWN_WALK | the library forecast was adjusted by this game's own trading |
| Q_MOVE_LICENSED_BY_CANDIDATE_FINAL_FLOOR_LADDER_SHRINK | a cheap ending died; bid stepped to the ladder |
| Q_UNPOSTABLE_NEXT_SURVIVING_LADDER_RUNG_BELOW_ASK_ADMITTED | the forecast price could not be posted; used a remaining ladder price below the ask |
| REPRICE_REST | moved the bid |
| RESOLVED | the OS made a price call |
| GIU_* | named hand — a branch that only runs on this game |
| PREDICTION_SEAT_IMMUNE | frozen by the seat until its deadline |
| IMMUNITY_HOLD | frozen by the seat until its deadline |
| OVERLAP_MEMBERS | similar games supplied the price forecast |
| OVERLAP_MEMBERS_FROM_OWN_RANGE_AT_PHASE | games overlapping this game's traded range supplied the forecast |
| OVERLAP_MEMBER_FLOOR_FRACTIONS | similar games supplied the forecast deadline |
| CANCEL_REST | pulled the bid |
| PULL_REST | pulled the bid |
| STAND_DOWN | pulled the bid |
| FILL_EVENT | the standing bid filled |
<!-- plain-card-gloss:end -->

### Four-line templates and selection rules

1. `<side> · Placed bid at <new>¢`, `Moved bid <old>¢ → <new>¢`,
   `Pulled bid`, or `Filled at <entry>¢`; values are the existing stored action fields.
2. `Why: <gloss>`. A missing translation in any present reason/lane/mode/author/source/
   status/action is explicit: `Why: not translated yet (<raw token>)`. With all tokens
   known, use the reason's gloss, else the winner-lane gloss. Two contextual cases:
   - `BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE` + `PRIOR_ONLY` +
     `ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET`:
     `the library aimed at <Q>¢; <side>'s own trading didn't change it`.
   - The same reason + `PRIOR_REWEIGHTED_BY_OWN_WALK`:
     `the library aimed at <Q>¢, adjusted by <side>'s own trading`.
     With `OVERLAP_MEMBERS`: `similar games pointed to <Q>¢`.
   - The ladder-shrink reason uses `down` or `up` only if both stored old/new prices
     exist and differ; otherwise `to`. These are words about the recorded move,
     not an inference from the tape slope.
3. `Believed: <side> at <P>¢ now, should reach <Q>¢ by <h:mm> to bell`.
   New `bid_actions[].deadline` stores the original stage belief's `deadline` object
   and `predicted_minutes_to_bell`. Clock source is **deadline.deadline_minutes_to_bell**,
   with explicit stored `predicted_minutes_to_bell` fallback, truncated to a whole
   minute for h:mm formatting. Absent/negative time => STORE SILENT. Legacy `sentence.X`
   remains unchanged in cents and is never used as a clock. Fill cards use the
   original PLACE's `placing_sentence` and new `fill.placing_deadline`.
4. Bid: `Book then: <bid> / <ask>, last <last> · <minutes-to-bell>m`, exact receipt
   book fields, no midpoint/last/tape substitution. Fill: `<difference>¢ above/below
   the recorded floor (<floor>¢) · rest stood <age>m`. Fill Why is `bid was sitting at
   <entry>¢ when a <triggering_print>¢ trade printed`, both values from fill context.

The dot remains the fill marker; all other bid actions use a small square. Stored
`render.marker_legend` is `▪ bid action · ● fill · ⚑ recorded floor`.
New `truth.legs[leg].hover_note` and `markers.<axis>.hover_note` say:
`Recorded floor <c>¢ printed here · <whole minutes>m to bell · from the truth table
(not an OS input)`. An edge flag adds a plain-English before/after-span disclosure.

### Pool accuracy (not an OS organ)

`render.pool_accuracy.heading` is `POOL ACCURACY · bench only`; `hover_note` is the
operator-specified description of both-side last-hour within-1¢ accuracy; absent
data label is STORE SILENT. Each existing `checkpoints[].bench.pool_accuracy` is a
display-only projection of its unchanged `bench.validity` values:

| Key | Rule |
|---|---|
| label | ESS < 10 => `—`; finite ESS >= 10 and status OK and finite share => percentage with two decimals; otherwise STORE SILENT |
| hover_note | ESS < 10 => `too few games to trust (ESS <n>)`, exact stored n (no rounding up across 10); otherwise the full bench-only description |
| meter_percent | share ×100 only when finite ESS >=10 and status OK; otherwise null |

Exact normal hover: "Of the past games the bench pool was using at this gate, the
share that called the last hour's move on both sides within 1¢. Bench measurement
— the OS doesn't have this organ yet."
The original validity share, ESS, status and clock-mismatch policy are untouched.
URSPAL's mismatched bench clock stays STORE SILENT, not a reconstructed percentage.

## Grade card + history — report only, never an OS input

`node window1-watch/build_grade.mjs --event <event>` reads that face and its bound
full receipt files. It writes `<event>.grade.json`, `GRADE_RECEIPT.json`, and appends
history. `rerun_game.ps1` runs it after the face builder, before publishing data.
It never imports the OS, runs a replay, or rewrites a face/stage/tape/truth/bench.

### Writer classes (extension of the plain-English gloss table)

Order is significant: the first matching row across action reason, lane, mode,
and author/source wins. Same-second FILL overrides the table. A fill inherits its
original PLACE's writer tokens. Unknown = STORE SILENT, never assumed ORGAN.
HAND means execution without demonstrated organ authorship, not necessarily a
named hand. RUNG and SEAT are explicitly not new Q/X authors.

<!-- grade-writers:start -->
| Token | Class | Meaning |
| PAL_* | HAND | named game-specific hand |
| GIU_* | HAND | named game-specific hand |
| LAJSVA_* | HAND | named game-specific hand |
| LADDER_* | RUNG | remaining ladder or cheap-ending writer |
| LIVE_LADDER_* | RUNG | remaining ladder writer |
| Q_MOVE_LICENSED_BY_CANDIDATE_FINAL_FLOOR_LADDER_SHRINK | RUNG | cheap ending died |
| NON_PRINT_* | RUNG | ladder reseat |
| Q_UNPOSTABLE_NEXT_SURVIVING_LADDER_RUNG_BELOW_ASK_ADMITTED | RUNG | postable ladder fallback |
| PREDICTION_SEAT* | SEAT | forecast seat or immunity |
| PREDICTION_SEATED_* | SEAT | protected forecast bid |
| IMMUNITY_* | SEAT | frozen by seat |
| ACTIVE_REST_HOLD | SEAT | carried standing bid |
| POOL_FIRST_TICK | ORGAN | first-tick pool price author (alias) |
| POOL_FIRST-TICK-ONLY | ORGAN | first-tick pool price author (stored token) |
| POOL_BASE | ORGAN | category base pool price author |
| POOL_CASCADE:* | ORGAN | stored cascade authority source |
| POOL_CASCADE_WRITER | ORGAN | selected cascade price executed |
| OVERLAP_MEMBERS* | ORGAN | own-range membership forecast |
| COHERENT_ENVELOPE_WRITER | ORGAN | coherent forecast |
| OWN_TOUCH_WRITER | ORGAN | own-evidence writer |
| CARRIED_CONVICTION_WRITER | SEAT | carried forecast |
| FLOOR_CAPABLE_WRITER | HAND | views disagreed; posted anyway |
| INSUFFICIENT_AUTHORITY_NO_WRITER | HAND | library prior executed, no writer |
| BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE | HAND | authority execution, not authorship proof |
| POST_ONLY_* | HAND | execution veto |
| DISAGREES_* | HAND | disagreement veto |
| PRICING_AUTHORITY_SILENT_* | SEAT | existing rest carried |
| LOCKED_BOOK_* | HAND | execution veto |
| NO_ACTION | HAND | no writer selected |
<!-- grade-writers:end -->

Cascade glosses include the actual hyphenated `POOL_FIRST-TICK-ONLY` token and
the requested `POOL_FIRST_TICK` alias; neither changes the OS token. Exact gloss
matches precede declared trailing-`*` prefix matches. A cascade execution card's
Why line names its stored authority source; raw fields remain in details.
HOLD/veto/named-hand precedence stays unchanged. STEP telemetry is not promoted
to a writer by this change.

### Grade fields and denominators

The family comparison is now independently clocked by the bound bench, not by
the chart's trace clock. `MACRO.comparison_clock` stores `source`, `bell_epoch`
(bench `first_tick.epoch + mtb_first*60`), `trace_bell_epoch`, `delta_seconds`,
`last_gate_epoch` (bench bell minus last gate times 60), and the exact `rule`.
Only filed bench gates at/after its first tick are used. `pool_accuracy_by_gate`
adds that bench-clock `epoch`. Neither this lookup nor a clock disagreement
changes MICRO, the chart, an OS timestamp, Q/X, or execution.

Each `MACRO.legs[leg]` adds `family_call_receipt`, `family_call_epoch`,
`family_call_minutes_to_bench_bell`, `family_call_age_at_gate_minutes`, and
`gate_after_trace_bell`. Called family is the latest stored belief-family at or
before the bench gate, including read-only beliefs for already-credited sides.
A later receipt missing that side does not erase its previous call. If the
bench gate is after replay ends, retain the last recorded call and expose its
age and the after-trace-bell flag; do not invent a new receipt or family.
Realized family remains the bench's filed label at the same gate. Missing bell,
label or call remains STORE SILENT; exact-token family mismatches remain failures.

`RULER_COLUMNS` in each grade is **RULER — NOT AN OS INPUT**.
`grade_rulers.mjs` reads the table @ `c0056976` and the correction ledger @
`15955e44`, applying EVERY matching correction in ledger order to the grading
ruler, not to OS inputs. `original_table` contains the complete original
`row_csv` and parsed `values`, commit/path/file SHA, exact CSV-row SHA
and row number, verified-span status/bounds/bell/source, per-leg floor/epoch/
close values and `source_columns`. `restated_rows[]` contains correction ID,
exact JSONL-row SHA, authority/evidence, restated span/bell/source and per-leg
floor/epoch/close columns. Each set's `floor_sum_cents` is its two filed floors
summed and `under_par_cents` is 100 minus that sum; absent inputs stay null.
`correction_source` records the correction file commit/path/SHA.

`original_table.campaign_ruler_columns` copies actual CSV columns matching
campaign/ruler (empty if absent). `restated_rows[].campaign_ruler_fields` copies
`after.game_ruler` / `after.leg_ruler` verbatim, named by
`campaign_source_columns`; `offered_under_par` copies the filed object, if any.
`selection` says all filed corrections; no floor is selected by performance.
Each `restated_rows[]` additionally preserves the exact `row_jsonl` and complete
`original_correction`, including before/after, authority, evidence and downstream notes.
`effective_truth` is the overlaid grading ruler: effective row, floor/epoch,
bell/source, spans, pair sum/discount, and applied correction IDs/row SHAs.
All scalar after-fields and every leg field are overlaid generically; nested
campaign/offered fields remain verbatim in `original_correction`. Filed offered
sum/discount must agree with the corrected floors or grading fails loudly.
The pinned CSV calls its columns `legA_floor_c` / `legB_floor_c`, not literally
`floor_cents`; GIUBAR's campaign ruler is in the correction ledger, not the CSV.
Existing trace/face inputs and chart floor markers are unchanged. The grade's
OUTCOME and MICRO use `effective_truth`; its own ruler line is explicit on the
GRADE panel so its corrected values cannot be mistaken for the old chart ruler. Grade
provenance includes `grade_rulers_sha256`; its taxonomy receipt is adjacent to
the actually bound named-check file, not the obsolete minute-bench receipt.

- `version`, `event`, `provenance`: schema, exact face event, historical OS/trace/
  bench hashes, truth commit/row hash, face hash, rubric hash, receipt hash,
  source OS commit/topological commit count (STORE SILENT if not locatable), and
  face-worktree HEAD at grading. Today's OS never replaces the face's OS hash.
  Builder, grade-contract and FIELDS byte hashes identify the exact grading code
  and writer mapping, including before the resulting artifact is committed.
  `stage_inputs_sha256` hashes ordered `relative URL + NUL + gzip file SHA + LF`
  records for all inspected DECISION_STAGE files; `stage_files_count` is their count.
- `SENTENCE.receipts_total`: DECISION_STAGE count, not FLOOR_PRINT/FILL_EVENT.
  `receipts_with_sentence`: both legs have a stored plain sentence, finite P, Q,
  and deadline. `leg_receipts_total/with_sentence` expose the side denominator.
  Q/X organ shares divide qualifying leg decisions by **all** leg decisions;
  missing or INSUFFICIENT authors/targets never qualify. Author must not be
  PRIOR_ONLY/LIBRARY_FRACTION_PRIOR and the action/authority must carry no named
  token. Q additionally excludes PRIOR_REWEIGHTED_BY_OWN_WALK: the
  `2dfb5b0abf3fdf8669b8750d2780effd44a7319c` diff stamps that badge from own-print
  count/slope without changing `ownEvidenceChannelGrades` or
  `conditionPriorDistribution`. A badge is not reweighting or authorship.
  `non_organ_q_authors` records the full Q exclusion list on the grade.
  `q_organ_leg_receipts`, `x_organ_leg_receipts`, `author_counts` expose exact
  counts; raw labels are preserved, not relabelled. X classification is unchanged.
  Remaining token shares are NOT Gate-1 certification:
  `gate_1_authorship_certification` stays STORE SILENT, reason supplied.
  Old history snapshots keep their original grading rule; each new run appends
  the corrected grade and receipt rather than rewriting history.
- `named_tokens_found/evidence`: distinct symbolic PAL_*/GIU_*/LAJSVA_* values,
  current leg-prefixed tokens, or event-containing WRITER/GATED/HAND tokens in
  full decision rows, with occurrence count and first field/receipt. Event IDs,
  leg IDs, receipt metadata and library identities are not writer tokens.
  This is an on-row audit; unrecorded code branches cannot be certified absent.
- `MACRO.last_gate/receipt/legs`: final stored atlas checkpoint (smallest
  minutes-to-bell), last causal decision at that gate. Raw OS `belief.family`
  versus bound bench `realized_family`; different vocabularies are not silently
  translated. `bench_families_by_rule` preserves all six comparators; no best
  rule is selected retrospectively. `family_match` is exact-token equality.
  `pile_ess_at_last_gate` is explicitly the bench validity pool ESS, NOT OS
  membership ESS. `pool_accuracy_by_gate` stores share, ESS, status and reason.
  No bound bench or missing bench bell => STORE SILENT. Family grading uses the
  bench bell for both the called-family as-of lookup and realized-family gate.
  The trace clock and chart checkpoint joins remain unchanged. Bench label retained.
- `MICRO` version 2 replaces the old last-gate/full-span and retrospective
  held-gate selector. `legs[leg].first_eligible_full_span` is selected in stored
  receipt order BEFORE inspecting future targets: resolved P/Q/X sentence,
  finite Q/deadline, own formation complete, inside corrected span and bell.
  Includes receipt/order/epoch, Q/authors/deadline, full recorded floor target,
  absolute floor/timing errors and `floor_already_observed_at_call` (a past floor
  remains a retrospective comparison, never a claimed prediction).
  `receipt_calls[]` records both sides at every decision, including unavailable
  forecasts with explicit eligibility reasons. Stored belief forecasts after a
  side fills are included; they are not new actions or extra authorship votes.
  Q is posterior_q50_cents when present, else the stored belief.predicted_cents;
  `q_source` records which. Never substitute a rest, bench forecast or new price.
  `deadline_epoch` uses stored absolute deadline, else ORIGINAL trace bell minus
  stored X. `stored_x_minutes_to_trace_bell` and
  `x_minutes_to_corrected_bell` label the two clocks for the SAME instant.
  Every eligible call has `targets.carried_gate_state` (last accepted print at
  or before receipt, with original observation time/receipt), `remaining_path`
  (minimum of carry and strictly later in-span prints), and
  `executable_future_print` (strictly later accepted print minimum only).
  Carried minima use the receipt epoch and kind
  CARRIED_GATE_STATE_NOT_A_FUTURE_PRINT. A future-print target is an observed
  trade, NOT proof a hypothetical maker rest could fill. First equal future
  minimum wins; a carry tied with a future minimum remains timed at receipt.
  No future prints => future-print target STORE SILENT, not zero error.
  `remaining_path_score` and `executable_future_print_score` each match Q/X to
  that target's floor and epoch. `legs.*.remaining_path` and
  `legs.*.executable_future_print` report eligible/scored/unscored counts, mean
  and maximum floor/timing errors. `mode_metrics` and `mode_grades` separately
  apply the unchanged MICRO rubric to first/full and all-receipt/remaining
  maximum errors; MICRO is their worst grade. Descriptive means are not cutoffs.
  `grade_prints.mjs` streams existing custody prints once for `--all`, filters
  true_print=true/positive size/finite price-time/identity, dedupes exact receipt
  identity per ticker (conflicts fail), and preserves equal-time source order.
  `print_source` binds path/SHA/bytes/source and selected row counts, invalid and
  duplicate counts and per-leg totals. Date.parse uses the replay millisecond
  clock. No book last or chart interpolation becomes a print; raw private tape
  is not copied into public data. Per-target receipt/source row remains auditable.
- `HANDS.actions`: all chart bid actions (including changed HOLD/disappearance),
  raw tokens, writer class, receipt/source URL, old/new cents, minute-to-bell.
  `order_lineage_*` starts at PLACE, survives reprice and ends on removal/fill.
  `current_price_*` starts at PLACE and resets on an actual price change; a
  same-price reprice/unchanged HOLD does not reset it. Both have start epoch,
  source receipt and age minutes at each action. `rest_age_at_fill_minutes` now
  explicitly aliases current-price age; `legacy_display_rest_age_minutes`
  preserves the former chart lineage number. Same-second fill compares the
  integer seconds of current-price start and fill, not rounded minute ages.
  Missing starts stay STORE SILENT. Placement checks include PLACE_REST and REPRICE_REST:
  target >= contemporaneous ask violates post-only; epoch < stored formation end
  is pre-formation. Unknown inputs make total STORE SILENT; observed violations
  and uncheckable counts remain separate. No unchanged HOLD is a new placement.
  `fill_age_uncheckable` and `writer_class_unmapped` expose gaps; any such gap or
  missing formation prevents a passing HANDS section instead of inventing safety.
- `OUTCOME.legs`: recorded filled/cents/epoch and signed entry minus ruler floor.
  `valid_span_fill` requires corrected truth OK, span_start <= fill < span_end
  AND fill < corrected bell. `revalidation` records all bounds, each predicate
  and correction IDs for EVERY observed fill. `vs_floor_cents` is recomputed
  against the corrected floor, never copied from an old chart annotation.
  `pair_completed/pair_sum` are recorded fills; `valid_pair_completed` adds span
  checks. Captured = max(0,100-sum) for a valid complete, otherwise zero; unknown
  fill span remains STORE SILENT. Partial pairs capture zero, never unrealized
  profit. `best_capturable_cents` = truth discount (4 for ALTGAS), distinct from
  `best_capturable_pair_sum_cents` = truth floors' sum (96). Ratio = captured /
  positive offered discount, otherwise STORE SILENT. Do not clamp ratios to 1.
  Conduct F does not erase the separately reported mechanical span-valid outcome.
- `LETTER`: hard F for any named token, observed pre-formation placement, or
  same-second fill. Else worst section letter; missing section means STORE SILENT
  unless another section already proves F. `governing_section`, hard failures,
  section metrics and rubric status are explicit. `display` stores all HUD lines,
  hover numbers and marks: only an A section without a hard failure gets ✓;
  other sections get attention (!). All cutoff letters remain PLACEHOLDER.

### PLACEHOLDER cutoffs — edit grade_rubric.json, not the OS

| Section metric | A | B | C | D | F |
|---|---:|---:|---:|---:|---|
| min(Q share, X share), minimum | .95 | .80 | .60 | .40 | below D |
| raw OS/realized family match share, minimum | 1 | .75 | .50 | .25 | below D |
| worst-side floor error cents, maximum | 2 | 4 | 6 | 10 | above D |
| worst-side timing error minutes, maximum | 30 | 60 | 120 | 240 | above D |
| post-only violations, maximum | 0 | 1 | 2 | 3 | above D |
| capture ratio, minimum | .90 | .75 | .50 | .25 | below D |

MICRO uses the worse of floor and timing in each of its two modes, then their
worst grade; missing evidence never passes. These are **PLACEHOLDER bench choices**,
not inherited law or calibrated performance thresholds. The hard F conditions
come directly from the operator and do not depend on these cutoffs.

### Append-only grading history

`data/grades/<event>/<os_sha8>_<trace_sha8>.json` contains `grades[]`: a new full
snapshot is appended on every invocation, preserving earlier snapshots even if
rubric/code changes while OS+trace stay identical. `data/grades/index.json`
lists every snapshot's timestamp, provenance, letter, ratio, source file/revision,
grade hash, governing section and builder-written plot coordinates/hover lines.
Exact-hash collisions are rejected. Index order is OS commit ancestry count,
then recorded append order; absent commit is disclosed, ordered last. Within a
game, x is commit order with reruns tied by append order; y follows rubric letter
order, with an explicit STORE SILENT row. Loading shows current `<event>.grade.json`
only when its OS/trace/face hashes agree with the loaded face. History is separate
and never replaces the current game's data or receipts. Missing grade shows STORE
SILENT; stale binding shows a mismatch notice, never a different OS's letter.

`GRADE_RECEIPT.json` binds all four prior-art files by SHA and location/commit,
plus the bench taxonomy receipt. Each grade retains that complete receipt and its
hash, so later source changes cannot rewrite historical citations.

Grade provenance additionally binds the corrections commit/file SHA, effective
truth SHA, custody true-print SHA, and `grade_measurements.mjs`/`grade_prints.mjs`
SHAs. SENTENCE card wording is `authored (token metric)`; its Gate-1 certification
remains independently STORE SILENT. `display.ruler_line/ruler_hover_lines` are
builder-written corrected grading facts, separate from the unchanged trace/chart
clock. HANDS hover lists lineage and current-price durations separately.
