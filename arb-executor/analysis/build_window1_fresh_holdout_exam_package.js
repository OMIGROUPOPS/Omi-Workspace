#!/usr/bin/env node
"use strict";

// Package Stage 1/2 and fail closed before consuming the one-run exam when the
// frozen commits do not expose a population-parametric executable.

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const stage12 = path.resolve(arg("--stage12"));
const compareStage12 = path.resolve(arg("--compare-stage12"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_fresh_holdout_exam_20260806")));
const compare = arg("--compare", null);
const commits = {
  V36: "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
  V35: "0799fba887f1d1e84f9c0ef3e73096fd9d76019e",
  R3: "49f6501561c5d99a7f36c68ec41e0ea7250680e5",
  CLEAN_DEEP: "03bac97b12777d751fbb334fa6ae0f605445498a",
};
const paths = {
  V36: "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
  V35: "arb-executor/analysis/build_window1_v35_living_rest_evidence_gate.js",
  R3: "arb-executor/analysis/build_window1_v29r3_standing_floor_release.js",
  CLEAN_DEEP: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_HYGIENE_CENSUS.json",
};
const requiredStage12 = [
  "PRE_MATCH_BOUNDARY_LEDGER.jsonl",
  "FLOOR_PASS_ADMISSION_LEDGER.jsonl",
  "EXAM_EVENT_LIST.txt",
  "EXAM_POPULATION.json",
  "BOUNDARY_SOURCE_SNAPSHOT.json",
  "STAGE12_FORBIDDEN_ACCESS_RECEIPT.json",
];

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 }); }
function lineMatches(text, pattern) { return text.split(/\r?\n/).map((value, i) => ({ line: i + 1, value })).filter((row) => pattern.test(row.value)); }
function write(name, value) { fs.writeFileSync(path.join(output, name), Buffer.isBuffer(value) ? value : canonical(value)); }
function manifest(root) {
  return Object.fromEntries(fs.readdirSync(root).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => {
    const file = path.join(root, name);
    return [name, { sha256: fileHash(file), bytes: fs.statSync(file).size }];
  }));
}

function build() {
  ensure(fs.existsSync(stage12) && fs.existsSync(compareStage12), "both Stage-1/2 builds required");
  for (const name of requiredStage12) {
    ensure(fs.existsSync(path.join(stage12, name)), `missing Stage-1/2 artifact ${name}`);
    ensure(fs.existsSync(path.join(compareStage12, name)), `missing comparison Stage-1/2 artifact ${name}`);
    ensure(fileHash(path.join(stage12, name)) === fileHash(path.join(compareStage12, name)), `Stage-1/2 determinism mismatch ${name}`);
  }
  const population = JSON.parse(fs.readFileSync(path.join(stage12, "EXAM_POPULATION.json"), "utf8"));
  ensure(population.gate_pass === true && population.admitted_N >= 60, "N<60 stop law");
  ensure(population.sealed_input_list_sha256 === "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313", "seal hash changed");
  fs.rmSync(output, { recursive: true, force: true });
  fs.mkdirSync(output, { recursive: true });
  for (const name of requiredStage12) fs.copyFileSync(path.join(stage12, name), path.join(output, name));

  const audit = {};
  for (const name of ["V36", "V35", "R3"]) {
    const source = gitShow(commits[name], paths[name]);
    const text = source.toString("utf8");
    audit[name] = {
      commit: commits[name],
      source_path: paths[name],
      source_sha256: sha(source),
      source_bytes: source.length,
      fixed_development_denominator_assertions: lineMatches(text, /(?:baseEvents|events)\.length === 804/),
      frozen_input_bindings: lineMatches(text, /(?:const base =|const eventPath =|const floorFile =|const baseTraceFile =)/),
      accepts_external_event_list: false,
      accepts_external_boundary_ledger: false,
      accepts_external_population_tape_root: false,
    };
  }
  audit.R3.posthoc_transformer_proof = {
    input_event_path: lineMatches(gitShow(commits.R3, paths.R3).toString("utf8"), /const eventPath = path\.join\(r2/),
    input_v28_conservation: lineMatches(gitShow(commits.R3, paths.R3).toString("utf8"), /V28 conservation failed|R2 conservation failed/),
    finding: "R3 consumes frozen V28/R2 development result ledgers; it does not reconstruct its incumbent path from arbitrary raw tapes.",
  };
  const cleanDeepBytes = gitShow(commits.CLEAN_DEEP, paths.CLEAN_DEEP);
  const cleanDeep = JSON.parse(cleanDeepBytes);
  const readiness = {
    schema_version: "window1-fresh-holdout-exam-execution-readiness-v1",
    stage_1_boundary: "PASS_FROZEN",
    stage_2_admission: "PASS_FROZEN_N_GE_60",
    stage_3: "NOT_STARTED_FAIL_CLOSED",
    authorization_consumed: false,
    exam_process_invocations: 0,
    brain_invocations: { V36: 0, V35: 0, R3: 0, total: 0 },
    retries: 0,
    score_rows: 0,
    performance_fields: null,
    blocker: {
      code: "NO_FROZEN_THREE_BRAIN_POPULATION_PARAMETRIC_EXECUTABLE",
      detail: "V35 and V36 hard-assert the 804 development base; R3 is a posthoc transform of frozen V28/R2 development ledgers. Calling a newly reimplemented adapter on the sealed population would not be the three frozen brains unchanged and would irreversibly spend the one run without parity proof.",
      required_resolution: "Freeze and independently verify a reusable tape-input adapter for each exact commit, with byte/semantic parity on the development corpus, before issuing a fresh one-run command.",
    },
  };
  write("FROZEN_BRAIN_EXECUTABILITY_AUDIT.json", { schema_version: "window1-fresh-holdout-exam-brain-audit-v1", brains: audit });
  write("CONTROL_BINDING.json", {
    schema_version: "window1-fresh-holdout-exam-control-binding-v1",
    construction_parent: "db77cd443c6801f30789a672607399fed5fdd0f9",
    corrected_seal_commit: "db77cd443c6801f30789a672607399fed5fdd0f9",
    corrected_seal_event_list_sha256: "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313",
    frozen_brains: commits,
    one_run_authority: "OPERATOR_PROMPT_THIS_TASK",
    one_run_consumed: false,
    stage3_command: null,
  });
  write("EXECUTION_READINESS_BLOCKER.json", readiness);
  write("CLEAN_DEEP_METHOD_BINDING.json", {
    commit: commits.CLEAN_DEEP,
    path: paths.CLEAN_DEEP,
    sha256: sha(cleanDeepBytes),
    method: cleanDeep.note,
    exact_clean_dev_reference: {
      V36: cleanDeep.per_model.V36.exact_and_clean,
      V35: cleanDeep.per_model.V35.exact_and_clean,
      R3: null,
    },
    holdout_rows: null,
  });
  write("DETERMINISM_RECEIPT.json", {
    schema_version: "window1-fresh-holdout-exam-determinism-v1",
    stage12_clean_builds: 2,
    stage12_byte_identical_files: requiredStage12.length,
    exam_brain_runs: 0,
    score_render_builds: 0,
    reason_score_determinism_not_applicable: readiness.blocker.code,
  });
  write("PREPARATION_PROCESS_RECEIPT.json", {
    schema_version: "window1-fresh-holdout-exam-preparation-process-v1",
    policy_blind_stage12_processes_started: 7,
    authoritative_clean_builds: ["stage12_e", "stage12_f"],
    authoritative_clean_builds_byte_identical: true,
    discarded_preparation_builds: {
      slow_full_rescan: "terminated before admission output after boundary generation; zero brain calls and zero scores",
      stage12_a_b: "discarded because request-attempt counters in the metadata source snapshot were refreshed between builds; boundary, admission, population and forbidden-access artifacts were already byte-identical",
    },
    exam_process_invocations: 0,
    brain_invocations: 0,
    retries_after_exam_start: 0,
    authorization_consumed: false,
  });
  write("FORBIDDEN_ACCESS_RECEIPT.json", {
    schema_version: "window1-fresh-holdout-exam-forbidden-access-v1",
    holdout_brain_consumption: 0,
    live_engine_access: 0,
    order_access: 0,
    position_access: 0,
    service_mutation: 0,
    tuning: 0,
    retry: 0,
    boundary_network_access: "PUBLIC_EXCHANGE_MARKET_METADATA_FOR_MISSING_SCHEDULE_BOUNDS_ONLY",
    tape_access: "READ_ONLY_FROZEN_SEALED_TAPE_ADMISSION_CENSUS",
  });
  write("REPORT.md", Buffer.from(`# Fresh Window-1 holdout exam - fail-closed before one run\n\nStage 1 froze ${population.admitted_N} boundary rows and Stage 2 admitted ${population.admitted_N} events under the unchanged V36 floor-pass law. The boundary ledger SHA-256 is \`${population.boundary_ledger_sha256}\`; the exam event-list SHA-256 is \`${population.exam_event_list_sha256}\`. Precision classes are ${JSON.stringify(population.precision_classes)}.\n\nStage 3 was not started. V35 and V36 are development builders with hard D=804 input bindings, while R3 is a posthoc transform of frozen V28/R2 development ledgers. No frozen executable accepts the sealed event list, new boundary ledger and raw tapes for all three commits. Reimplementing that missing interface inside the authorized exam would violate "three frozen brains unchanged" and make the one run irreproducible.\n\nAuthorization remains unconsumed: exam process invocations 0; brain invocations 0; retries 0; score rows 0.\n`, "utf8"));
  write("INDEPENDENT_REVIEW_INSTRUCTION.md", Buffer.from("Verify the sealed-list hash, recompute all 171 boundary selections from BOUNDARY_SOURCE_SNAPSHOT.json, recheck every tape hash and the unchanged floor-pass admission ledger, then independently inspect the exact V36/V35/R3 Git objects. Confirm V35/V36 hard-bind D=804 and R3 consumes frozen V28/R2 result ledgers; confirm no exam process or brain was invoked and the standing one-run authorization was not consumed.\n", "utf8"));
  const sources = [
    "arb-executor/analysis/build_window1_fresh_holdout_exam_stage12.py",
    "arb-executor/analysis/build_window1_fresh_holdout_exam_package.js",
  ];
  write("SOURCE_HASH_MANIFEST.json", {
    files: Object.fromEntries(sources.map((rel) => [rel, { sha256: fileHash(path.join(repo, rel)), bytes: fs.statSync(path.join(repo, rel)).size }])),
    git_objects: Object.fromEntries(Object.entries(audit).map(([name, row]) => [name, { commit: row.commit, path: row.source_path, sha256: row.source_sha256, bytes: row.source_bytes }])),
  });
  const beforeManifest = manifest(output);
  if (compare) {
    const compareManifest = manifest(path.resolve(compare));
    ensure(JSON.stringify(beforeManifest) === JSON.stringify(compareManifest), "package determinism mismatch");
  }
  write("ARTIFACT_HASH_MANIFEST.json", { files: manifest(output) });
  process.stdout.write(canonical({ status: readiness.stage_3, N: population.admitted_N, authorization_consumed: false, output }));
}

build();
