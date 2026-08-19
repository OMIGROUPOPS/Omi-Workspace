"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");
const baseAdapter = require("./window1_v52r_exam_adapter.js");

const PARENT_COMMIT = "96597c98910f7ef45b62e2bc7dfab5ed9ee5f5a7";
const LAW_INDEX_COMMIT = "ae731326";
const LAW_INDEX_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md";
const SIM_COMMIT = "f30ea3ebeca4eec15790bb013a9c8e9f5a4fb852";
const SIM_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SLACK_CONDITIONAL_SHIFT.json";
const POLICY_ROOTS = [
  "arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js",
  "arb-executor/analysis/window1_v52l_causal_stability_onset.js",
  "arb-executor/analysis/window1_n9_clean_store.js",
];

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function gitBytes(repo, commit, relativePath) { return childProcess.execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, encoding: null, maxBuffer: 512 * 1024 * 1024 }); }
function localRequireClosure(repo, roots) {
  const pending = [...roots], seen = new Set();
  while (pending.length) {
    const relativePath = pending.pop().replaceAll("\\", "/");
    if (seen.has(relativePath)) continue;
    seen.add(relativePath);
    const source = fs.readFileSync(path.join(repo, relativePath), "utf8"), dir = path.posix.dirname(relativePath);
    for (const match of source.matchAll(/require\(["'](\.\/.+?\.js)["']\)/g)) pending.push(path.posix.normalize(path.posix.join(dir, match[1])));
  }
  return [...seen].sort();
}

function attestFrozenV52lPolicy(repo) {
  const files = {};
  for (const relativePath of localRequireClosure(repo, POLICY_ROOTS)) {
    const current = fs.readFileSync(path.join(repo, relativePath)), frozen = gitBytes(repo, PARENT_COMMIT, relativePath);
    files[relativePath] = { frozen_sha256: sha256(frozen), current_sha256: sha256(current), frozen_bytes: frozen.length, current_bytes: current.length, byte_identical: Buffer.compare(frozen, current) === 0 };
  }
  const pass = Object.values(files).every((row) => row.byte_identical);
  ensure(pass, "V52l incumbent policy byte identity failed");
  return { frozen_parent_commit: PARENT_COMMIT, roots: POLICY_ROOTS, transitive_files: files, file_count: Object.keys(files).length, all_byte_identical: true };
}

function loadBindings(repo) {
  const law = gitBytes(repo, LAW_INDEX_COMMIT, LAW_INDEX_PATH), simBytes = gitBytes(repo, SIM_COMMIT, SIM_PATH), sim = JSON.parse(simBytes);
  ensure(sha256(law) === "e2e42c72a619d8ad02542d8a655e83203cae1d8c30500684c14ce191d74e4afb", "LAW_INDEX binding changed");
  const incumbent = new Set(sim.grid["DEF+0|verified"].completes), openLoop = new Set(sim.grid["DEF+SLACK1|verified"].completes);
  const knifeEdges = [...incumbent].filter((eventId) => !openLoop.has(eventId)).sort();
  ensure(knifeEdges.length === 68, `sim knife-edge conservation changed ${knifeEdges.length}`);
  return {
    law_index: { commit: LAW_INDEX_COMMIT, path: LAW_INDEX_PATH, sha256: sha256(law), bytes: law.length, consulted_laws: ["L14", "L17", "L18"] },
    simulation: { commit: SIM_COMMIT, path: SIM_PATH, sha256: sha256(simBytes), bytes: simBytes.length, stamp: sim.stamp, verdict: "OPEN_LOOP_SLACK_REJECTED; CLOSED_LOOP_FORM_AUTHORIZED_FOR_EXECUTABLE_TEST", incumbent_verified_completes: incumbent.size, open_loop_slack1_verified_completes: openLoop.size },
    knife_edges: knifeEdges,
  };
}

function exposures(events) {
  const rows = events.map((event) => {
    const credited = Object.values(event.legs).filter((leg) => leg.credited).sort((a, b) => (a.fill_timestamp_epoch ?? Infinity) - (b.fill_timestamp_epoch ?? Infinity));
    if (credited.length === 2) return { event_id: event.event_id, disposition: "CREATED_RESOLVED", duration_seconds: Math.abs(credited[0].fill_timestamp_epoch - credited[1].fill_timestamp_epoch) };
    if (credited.length === 1) return { event_id: event.event_id, disposition: "CREATED_UNRESOLVED", duration_seconds: event.w1_right_epoch && credited[0].fill_timestamp_epoch ? event.w1_right_epoch - credited[0].fill_timestamp_epoch : null };
    return { event_id: event.event_id, disposition: "NOT_CREATED", duration_seconds: null };
  });
  const count = (name) => rows.filter((row) => row.disposition === name).length;
  return { created_resolved: count("CREATED_RESOLVED"), created_unresolved: count("CREATED_UNRESOLVED"), not_created: count("NOT_CREATED"), rows };
}

function buildArtifacts(args) {
  // V52s has no role classifier.  Receipt conservation uses the same compact
  // trace serializer, so the base artifact builder receives a mechanical
  // receipt counter and an intentionally empty terminal-role map.
  args.roleStats.role_receipt_rows = args.traceStats.rows;
  const built = baseAdapter.buildExamArtifacts(args);
  const score = built.artifacts["TWO_RULER_SCORECARD.json"].CANON_MARKET_GRADE;
  const strict = built.artifacts["TWO_RULER_SCORECARD.json"].STRICT_PRINT_CROSS;
  const baseline = built.artifacts["LINEAGE_V52L_V52R.json"].V52L;
  ensure(baseline.completed_pairs === 311 && baseline.locked_cents === 714, `L17 V52l baseline changed ${baseline.completed_pairs}/${baseline.locked_cents}`);
  const bindings = loadBindings(args.repo);
  const marketById = new Map(built.rows.marketRows.map((row) => [row.event_id, row]));
  const knifeRows = bindings.knife_edges.map((simulationEventId) => {
    // The analysis-seat simulation serializes the short exchange code
    // (26JUL...), while the replay ledger retains the canonical Kalshi event
    // identity (KX...-26JUL...).  Resolve that frozen representation mismatch
    // by a unique suffix join; never rewrite either source identity.
    const matches = [...marketById.keys()].filter((eventId) => eventId.endsWith(simulationEventId));
    ensure(matches.length === 1, `knife-edge identity join ${simulationEventId} matched ${matches.length}`);
    const eventId = matches[0], row = marketById.get(eventId);
    return { simulation_event_id: simulationEventId, event_id: eventId, V52s_state: row.state, combined_entry_cents: row.combined_entry_cents, preserved: row.state === "COMPLETE_AT_DELTA" };
  });
  const lostKnifeEdges = knifeRows.filter((row) => !row.preserved);
  const budgetSummaries = args.candidateRun.marketEvents.map((event) => ({ event_id: event.event_id, ...event.v52s_joint_budget_receipt_summary }));
  const depthActions = args.candidateRun.actions.filter((row) => row.kind.startsWith("V52S_"));
  const invariant = {
    events: budgetSummaries.length,
    phase_evaluations: budgetSummaries.reduce((sum, row) => sum + row.phase_evaluations, 0),
    unique_receipts_event_sum: budgetSummaries.reduce((sum, row) => sum + row.unique_receipts, 0),
    lift_events: budgetSummaries.reduce((sum, row) => sum + row.lift_events, 0),
    yield_events: budgetSummaries.reduce((sum, row) => sum + row.yield_events, 0),
    invariant_violations: budgetSummaries.reduce((sum, row) => sum + row.invariant_violations, 0),
    maximum_joint_target_sum_cents: Math.max(...budgetSummaries.map((row) => row.max_joint_target_sum_cents ?? 0)),
    completed_at_loss: score.completed_at_loss,
    every_depth_action_has_both_clocks: depthActions.every((row) => Object.hasOwn(row, "t_minus_scheduled_seconds") && Object.hasOwn(row, "t_minus_actual_bell_seconds")),
  };
  ensure(invariant.invariant_violations === 0 && invariant.maximum_joint_target_sum_cents <= 99 && invariant.completed_at_loss === 0, "V52s invariant proof failed");
  const candidateExposure = exposures(args.candidateRun.marketEvents), baselineExposure = exposures(args.baselineRun.marketEvents);
  const bar = {
    completed_pairs_at_least_305: { value: score.completed_pairs, threshold: 305, pass: score.completed_pairs >= 305 },
    net_banked_cents_above_714: { value: score.locked_cents, threshold_exclusive: 714, pass: score.locked_cents > 714 },
    all_68_open_loop_knife_edges_preserved: { preserved: knifeRows.length - lostKnifeEdges.length, expected: 68, lost: lostKnifeEdges.map((row) => row.event_id), pass: lostKnifeEdges.length === 0 },
    zero_par_crossing_completions: { value: score.completed_at_loss, pass: score.completed_at_loss === 0 },
    REFLEX_POST_zero: { value: built.artifacts["POSTING_TIME_AND_READ_AT_POST.json"].REFLEX_POST, pass: built.artifacts["POSTING_TIME_AND_READ_AT_POST.json"].REFLEX_POST === 0 },
  };
  bar.overall_pass = Object.values(bar).filter((row) => typeof row === "object" && Object.hasOwn(row, "pass")).every((row) => row.pass);

  delete built.artifacts["LINEAGE_V52L_V52R.json"];
  built.artifacts["LINEAGE_V52L_V52S.json"] = { grading_binding: args.groundTruth.binding, V52L: baseline, V52S: score, delta: { completed_pairs: score.completed_pairs - baseline.completed_pairs, under_par_pairs: score.under_par_pairs - baseline.under_par_pairs, locked_cents: score.locked_cents - baseline.locked_cents } };
  built.artifacts["V52S_LAW_AND_SIM_BINDING.json"] = bindings;
  built.artifacts["V52S_KNIFE_EDGE_68_PRESERVATION.json"] = { source: bindings.simulation, expected: 68, rows: knifeRows, preserved: knifeRows.length - lostKnifeEdges.length, lost: lostKnifeEdges.length, pass: lostKnifeEdges.length === 0 };
  built.artifacts["V52S_JOINT_BUDGET_INVARIANT_RECEIPT.json"] = { mechanism: "CLOSED_LOOP_JOINT_BUDGET_INVARIANT_WITH_YIELD_PRIORITY_DEPTH", pair_budget_cents: 99, tape_tick_cents: 1, tape_tick_is_market_unit_not_fitted_constant: true, incumbent_defaults_senior: true, depth_lifts_junior: true, re_evaluated_before_market_interaction_on_every_receipt_phase: true, ...invariant, event_summaries: budgetSummaries };
  built.artifacts["V52S_DEPTH_LIFT_AND_YIELD_LEDGER.json"] = { rows_externalized_to: "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.jsonl.gz", count: depthActions.length, by_kind: Object.fromEntries([...new Set(depthActions.map((row) => row.kind))].sort().map((kind) => [kind, depthActions.filter((row) => row.kind === kind).length])), both_clocks_pass: invariant.every_depth_action_has_both_clocks };
  built.artifacts["V52S_SERIALIZATION_RECEIPT.json"] = { role: "MECHANICAL_STREAMING_GZIP_ONLY", row_ledger: "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.jsonl.gz", summary: "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.json", rows: depthActions.length, policy_bytes_changed: false, decisions_changed: false, scores_changed: false };
  built.artifacts["V52S_EXPOSURE_DELTA.json"] = { V52L: { created_resolved: baselineExposure.created_resolved, created_unresolved: baselineExposure.created_unresolved, not_created: baselineExposure.not_created }, V52S: { created_resolved: candidateExposure.created_resolved, created_unresolved: candidateExposure.created_unresolved, not_created: candidateExposure.not_created }, delta: { created_resolved: candidateExposure.created_resolved - baselineExposure.created_resolved, created_unresolved: candidateExposure.created_unresolved - baselineExposure.created_unresolved, not_created: candidateExposure.not_created - baselineExposure.not_created }, rows: candidateExposure.rows };
  built.artifacts["V52S_MECHANISM_BAR.json"] = bar;
  built.artifacts["CONTROL_BINDING.json"] = { variant: "V52S_JOINT_BUDGET_YIELD_PRIORITY_DEPTH_804", exact_parent: PARENT_COMMIT, lineage: "V52L", scope: "DEV_804_DIRECT", grading_source: args.groundTruth.binding, policy_edits: false, one_mechanism: true, sealed: false, deployment: false, live: false };
  built.artifacts["FORBIDDEN_ACCESS_RECEIPT.json"] = { sealed: false, holdout: false, deployment: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, scavenger: false };
  built.artifacts["BOTH_CLOCKS_ROLE_RECEIPT.json"] = { role: "V52S_DEPTH_LIFT_AND_YIELD_RECEIPTS", rows: depthActions.length, fields: ["t_minus_scheduled_seconds", "t_minus_actual_bell_seconds"], missing_field_rows: depthActions.filter((row) => !Object.hasOwn(row, "t_minus_scheduled_seconds") || !Object.hasOwn(row, "t_minus_actual_bell_seconds")).map((row) => `${row.event_id}|${row.leg_identity}|${row.receipt}`), pass: invariant.every_depth_action_has_both_clocks };
  built.report = `# V52s joint-budget invariant with yield-priority depth — full dev-804\n\nLAW_INDEX ${bindings.law_index.sha256}; laws L14, L17, L18. V52l incumbent policy bytes are frozen at parent ${PARENT_COMMIT}.\n\n- Market valid-fill completed/under-par ${score.completed_pairs}/${score.under_par_pairs}; banked ${score.locked_cents}c; frontier <=93/<=95/<=97/<100/any ${score.frontier.LE_93}/${score.frontier.LE_95}/${score.frontier.LE_97}/${score.frontier.LT_100}/${score.frontier.ANY_PRICE}.\n- Strict build-verification completed/under-par ${strict.completed_pairs}/${strict.under_par_pairs}; banked ${strict.locked_cents}c.\n- L17 V52l baseline ${baseline.completed_pairs} completes / ${baseline.locked_cents}c; deltas ${score.completed_pairs - baseline.completed_pairs} / ${score.locked_cents - baseline.locked_cents}c.\n- Closed-loop invariant: ${invariant.phase_evaluations} receipt-phase evaluations, ${invariant.lift_events} lifts, ${invariant.yield_events} yields, maximum joint target ${invariant.maximum_joint_target_sum_cents}c, violations ${invariant.invariant_violations}, AT_LOSS ${score.completed_at_loss}.\n- Open-loop simulation knife edges preserved ${knifeRows.length - lostKnifeEdges.length}/68.\n- Exposure unresolved ${baselineExposure.created_unresolved} -> ${candidateExposure.created_unresolved}. REFLEX_POST ${built.artifacts["POSTING_TIME_AND_READ_AT_POST.json"].REFLEX_POST}.\n- Mechanism bar: ${bar.overall_pass ? "PASS" : "FAIL"}. No sealed, live, network, order, position, exit, settlement, DCA, or deployment access.\n`;
  return { ...built, bindings, knifeRows, depthActions, bar };
}

module.exports = { PARENT_COMMIT, LAW_INDEX_COMMIT, LAW_INDEX_PATH, SIM_COMMIT, SIM_PATH, attestFrozenV52lPolicy, loadBindings, buildArtifacts, canonical, sha256 };
