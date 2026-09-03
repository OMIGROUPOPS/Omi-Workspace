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
provenance.os_sha256 <- SHA256 of arb-executor/analysis/window1_v54_dual_belief_os.js
stand-down/pull action series <- STORE SILENT; exported action names are HOLD_REST, PLACE_REST, and REPRICE_REST
