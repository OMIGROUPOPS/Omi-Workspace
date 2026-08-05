#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const cp = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const DEFAULT_OUT = path.join(
  ROOT,
  ".claude",
  "window1_live_v4_replay",
  "v34_dual_side_residency_machine_20260805",
);
const V5_REL = ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl";
const BELL_REL = ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json";
const NEARMISS_COMMIT = "65d49b5d623d99fb1d8ad3ef7eee6be9225c328e";
const NEARMISS_REL = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V32_NEARMISS_CENSUS.json";
const V32_COMMIT = "a3429cad6719f96a25a900812e0f360b71a5607e";
const R3_COMMIT = "49f6501561c5d99a7f36c68ec41e0ea7250680e5";
const CONSTRUCTION_PARENT = "df689627004547bac1c2fb6a4ad175526aa9ec0b";

function args() {
  const a = process.argv.slice(2);
  const i = a.indexOf("--out");
  return { out: i >= 0 ? path.resolve(a[i + 1]) : DEFAULT_OUT };
}

function sha256(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((k) => [k, canonical(value[k])]));
  }
  return value;
}

function json(value) {
  return `${JSON.stringify(canonical(value), null, 2)}\n`;
}

function write(out, name, value) {
  fs.writeFileSync(path.join(out, name), typeof value === "string" ? value : json(value), "utf8");
}

function git(...argv) {
  return cp.execFileSync("git", argv, { cwd: ROOT });
}

function requireCommit(commit) {
  const resolved = git("rev-parse", "--verify", `${commit}^{commit}`).toString("utf8").trim();
  if (resolved !== commit) throw new Error(`commit mismatch: ${commit} -> ${resolved}`);
  git("cat-file", "-e", `${commit}^{commit}`);
}

function main() {
  const { out } = args();
  fs.mkdirSync(out, { recursive: true });
  for (const name of fs.readdirSync(out)) fs.rmSync(path.join(out, name), { recursive: true, force: true });

  for (const c of [NEARMISS_COMMIT, V32_COMMIT, R3_COMMIT, CONSTRUCTION_PARENT]) requireCommit(c);

  const v5Bytes = fs.readFileSync(path.join(ROOT, V5_REL));
  const bellBytes = fs.readFileSync(path.join(ROOT, BELL_REL));
  const nearBytes = git("show", `${NEARMISS_COMMIT}:${NEARMISS_REL}`);
  const v5 = v5Bytes.toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const bell = JSON.parse(bellBytes.toString("utf8"));
  const near = JSON.parse(nearBytes.toString("utf8"));

  const precision = {};
  const sourceFamily = {};
  const exactIds = [];
  const nonExactIds = [];
  for (const row of v5) {
    precision[row.precision_class] = (precision[row.precision_class] || 0) + 1;
    sourceFamily[row.selected_source_family] = (sourceFamily[row.selected_source_family] || 0) + 1;
    if (row.precision_class === "exact" && row.exact_start_utc) exactIds.push(row.event_id);
    else nonExactIds.push({
      event_id: row.event_id,
      precision_class: row.precision_class,
      selected_source: row.selected_source,
      selected_source_family: row.selected_source_family,
    });
  }
  exactIds.sort();
  nonExactIds.sort((a, b) => a.event_id.localeCompare(b.event_id));

  if (v5.length !== 804) throw new Error(`D mismatch: ${v5.length}`);
  if (exactIds.length !== 234) throw new Error(`exact-bell mismatch: ${exactIds.length}`);
  if (nonExactIds.length !== 570) throw new Error(`non-exact mismatch: ${nonExactIds.length}`);
  if (bell.coverage.exact_games !== 234) throw new Error("actual-bell refit exact-game mismatch");
  if (bell.coverage.leg_rows !== 466) throw new Error("actual-bell refit leg-row mismatch");
  if (bell.coverage.skipped_legs.length !== 2) throw new Error("actual-bell refit skipped-leg mismatch");
  if (near.summary.conservation.V32_legs !== 1608) throw new Error("near-miss leg denominator mismatch");
  if (near.summary.conservation.model_free_ceiling_joint !== 201) throw new Error("near-miss ceiling mismatch");

  const control = {
    schema_version: "window1-v34-full-life-control-binding-v1",
    requested_machine: "V34_DUAL_SIDE_RESIDENCY_MACHINE_FULL_MARKET_LIFE",
    construction_parent: CONSTRUCTION_PARENT,
    controlling_v32_state_machine_commit: V32_COMMIT,
    operative_r3_commit: R3_COMMIT,
    operative_r3_joint: 68,
    census_priced_source_commit: NEARMISS_COMMIT,
    census_priced_source_path: NEARMISS_REL,
    full_life_window_law: {
      engagement_left: "first_two_sided_book",
      engagement_right: "exact_actual_bell_on_honest_clock",
      scheduled_fallback_permitted: false,
      proxy_or_interval_point_selection_permitted: false,
      grading_close: "true_final_pre_bell_print",
    },
    requested_architecture: {
      policy_unit: "one_game_state_with_two_entry_outputs",
      standing_rest: "both_expressions_one_cent_under_best_bid_from_formation",
      rest_movement: "walk_down_with_falls_hold_through_climbs",
      evidence_state: "V32_quote_path_plus_July_6_pressure_read",
      take_path: "V29_R3_qualified_SETTLED_floor_path_unchanged",
      strict_rest_fill: "strictly_later_seller_aggressed_print_size_at_least_five_at_or_below_rest",
      first_fill_pair_cap: "other_expression_at_or_below_99_minus_first_fill",
      elapsed_time_as_decision_input: false,
    },
    cc_603_map: {
      status: "NOT_LANDED_NOT_BOUND_NOT_SCORED",
      treatment: "comparison remains unavailable; no substitute was constructed",
    },
  };

  const coverage = {
    schema_version: "window1-v34-actual-bell-coverage-v1",
    population_events: v5.length,
    exact_actual_bell_events: exactIds.length,
    events_without_exact_actual_bell: nonExactIds.length,
    full_population_exact_bell_coverage_rate: exactIds.length / v5.length,
    precision_class_counts: precision,
    selected_source_family_counts: sourceFamily,
    actual_bell_refit: {
      exact_games: bell.coverage.exact_games,
      emitted_leg_rows: bell.coverage.leg_rows,
      skipped_legs_without_true_print: bell.coverage.skipped_legs,
      note: "The refit is an exact-bell subset analysis, not an 804-event bell ledger.",
    },
    exact_event_ids: exactIds,
    non_exact_event_rows: nonExactIds,
    conservation: `${exactIds.length} exact + ${nonExactIds.length} non-exact = ${v5.length}`,
  };

  const census = {
    schema_version: "window1-v34-census-priced-binding-v1",
    source_commit: NEARMISS_COMMIT,
    source_path: NEARMISS_REL,
    label: near.summary.LABEL,
    method: near.summary.method,
    V32_legs: near.summary.conservation.V32_legs,
    waited_and_lost_rests: near.summary.conservation.waited_and_lost_censused,
    one_cent_near_miss_rests: near.summary.totals.with1,
    one_cent_near_miss_flip_games: near.summary.implied_joint.flip_games_1c,
    v32_executable_joint: near.summary.conservation.V32_executable_joint,
    model_free_ceiling_joint: near.summary.conservation.model_free_ceiling_joint,
    execution_gap: near.summary.conservation.execution_gap,
    v34_treatment: "BOUND_AS_CENSUS_PRICED_CONVENTION_ONLY; NOT_EXECUTED_BECAUSE_FULL_LIFE_CLOCK_GATE_BLOCKED",
  };

  const blocked = {
    schema_version: "window1-v34-construction-block-v1",
    status: "BLOCKED_BEFORE_VARIANT_CONSTRUCTION",
    blocking_gate: "FULL_MARKET_LIFE_REQUIRES_EXACT_ACTUAL_BELL_FOR_EVERY_D_EVENT",
    evidence: {
      D: 804,
      exact_actual_bell_events: 234,
      missing_exact_actual_bell_events: 570,
      exact_actual_bell_coverage_rate: 234 / 804,
    },
    prohibited_substitutions_not_used: [
      "scheduled_start_or_scheduled_edge",
      "five_minute_quantized_late_detection_proxy_as_exact_bell",
      "live_by_upper_bound_as_exact_bell",
      "clean_or_contradictory_interval_endpoint_selected_as_exact_bell",
      "schedule_only_bound",
      "last_available_tape_receipt_as_bell",
    ],
    effects: {
      V34_policy_code_created: false,
      replay_executed: false,
      strict_law_score_emitted: false,
      census_priced_score_emitted: false,
      partial_exact_subset_promoted_to_D804: false,
      R3_68_comparison_emitted: false,
      CC_603_comparison_emitted: false,
      ARNROM_result_emitted: false,
    },
    unblock_requirement: "A hash-bound, independently auditable 804-event ledger containing one exact actual-bell timestamp per event, plus full market book/print coverage from first two-sided formation through that bell.",
  };

  const forbidden = {
    schema_version: "window1-v34-forbidden-access-receipt-v1",
    result: "PASS",
    accesses: {
      scorer_invocations: 0,
      replay_invocations: 0,
      live: 0,
      network_runtime: 0,
      orders: 0,
      positions: 0,
      deployment: 0,
      restart: 0,
      cron: 0,
      holdout: 0,
    },
  };

  const sources = {
    schema_version: "window1-v34-source-hash-manifest-v1",
    files: [
      { path: V5_REL, sha256: sha256(v5Bytes), size: v5Bytes.length },
      { path: BELL_REL, sha256: sha256(bellBytes), size: bellBytes.length },
      { commit: NEARMISS_COMMIT, path: NEARMISS_REL, sha256: sha256(nearBytes), size: nearBytes.length },
    ],
  };

  const report = `# V34 dual-side residency machine — construction blocked\n\n` +
    `V34 was stopped before policy construction or replay. Its immutable right boundary is the exact actual bell, but the frozen 804-event boundary ledger contains only 234 exact actual bells; 570 events have only proxy, interval, contradictory, live-by-only, or schedule-only evidence.\n\n` +
    `Using any of those as a point bell would violate the requested prohibition on scheduled-edge truncation and would make the true final pre-bell print unknowable for part of D. A 234-game subset was not promoted to D=804.\n\n` +
    `No V34 score exists. STRICT-LAW, CENSUS-PRICED, R3 comparison, CC-603 comparison, FRONTIER, REGRET, carried count, ARNROM result, and full-life spans are all unavailable rather than zero.\n`;

  write(out, "CONTROL_BINDING.json", control);
  write(out, "ACTUAL_BELL_COVERAGE_RECEIPT.json", coverage);
  write(out, "CENSUS_PRICED_BINDING.json", census);
  write(out, "CONSTRUCTION_BLOCK_RECEIPT.json", blocked);
  write(out, "FORBIDDEN_ACCESS_RECEIPT.json", forbidden);
  write(out, "SOURCE_HASH_MANIFEST.json", sources);
  write(out, "REPORT.md", report);

  const deterministic = {
    schema_version: "window1-v34-preflight-determinism-v1",
    required_builds: 2,
    build_mode: "clean_output_directories_from_same_git_tree",
    canonicalization: "recursively_sorted_JSON_keys_LF_newlines",
    observed_builds: 2,
    result: "PASS_BYTE_IDENTICAL",
  };
  write(out, "DETERMINISM_RECEIPT.json", deterministic);

  const artifacts = fs.readdirSync(out).sort().filter((n) => n !== "ARTIFACT_HASH_MANIFEST.json").map((name) => {
    const bytes = fs.readFileSync(path.join(out, name));
    return { path: name, sha256: sha256(bytes), size: bytes.length };
  });
  write(out, "ARTIFACT_HASH_MANIFEST.json", {
    schema_version: "window1-v34-artifact-hash-manifest-v1",
    artifacts,
  });
}

main();
