#!/usr/bin/env node
"use strict";

// Fail-closed construction gate for the sealed-171 three-brain exam adapter.
// It proves source identity and input compatibility without invoking a brain.

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => {
  const index = argv.indexOf(name);
  return index < 0 ? fallback : argv[index + 1];
};
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg(
  "--output",
  path.join(repo, ".claude/window1_fresh_holdout_exam_adapter_gate_20260806"),
));
const compare = arg("--compare", null);

const stage12 = path.join(repo, ".claude/window1_fresh_holdout_exam_20260806");
const correctedSeal = path.join(repo, ".claude/boot_gate_stage_b_recorder_seal_20260806");
const rewrittenSeal = path.join(repo, ".claude/window1_fresh_holdout_seal_20260806");
const controllingListSha = "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313";
const boundarySha = "70f8b28749d8e1fd60e64af6e3ced41e556b2a20e5898ec692f0e4f7081b7c0a";

const brains = {
  V36: {
    commit: "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
    builder: "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
    policies: ["arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js"],
  },
  V35: {
    commit: "0799fba887f1d1e84f9c0ef3e73096fd9d76019e",
    builder: "arb-executor/analysis/build_window1_v35_living_rest_evidence_gate.js",
    policies: ["arb-executor/analysis/window1_v35_living_rest_evidence_gate.js"],
  },
  R3: {
    commit: "49f6501561c5d99a7f36c68ec41e0ea7250680e5",
    builder: "arb-executor/analysis/build_window1_v29r3_standing_floor_release.js",
    policies: [
      "arb-executor/analysis/window1_v29r3_standing_floor_release_policy.js",
      "arb-executor/analysis/window1_interim_elimination_v13.js",
    ],
  },
};

const changedSealPaths = [
  "ARTIFACT_HASH_MANIFEST.json",
  "FORBIDDEN_ACCESS_RECEIPT.json",
  "GIT_TOUCH_AUDIT.json",
  "ONE_RUN_GATE_RECEIPT.json",
  "REPORT.md",
  "SEALED_DECLARATION.json",
  "SEALED_EVENT_LIST.txt",
  "SOURCE_HASH_MANIFEST.json",
];

function ensure(value, message) {
  if (!value) throw new Error(message);
}
function canonical(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}
function sha(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}
function fileHash(file) {
  return sha(fs.readFileSync(file));
}
function gitShow(commit, relative) {
  return child.execFileSync("git", ["show", `${commit}:${relative}`], {
    cwd: repo,
    maxBuffer: 256 * 1024 * 1024,
  });
}
function requireCommit(commit) {
  const resolved = child.execFileSync(
    "git", ["rev-parse", "--verify", `${commit}^{commit}`],
    { cwd: repo, encoding: "utf8" },
  ).trim();
  ensure(resolved === commit, `commit identity mismatch ${commit}`);
  child.execFileSync("git", ["cat-file", "-e", `${commit}^{commit}`], { cwd: repo });
}
function lines(text, pattern) {
  return text.split(/\r?\n/)
    .map((value, index) => ({ line: index + 1, value }))
    .filter((row) => pattern.test(row.value));
}
function json(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}
function write(name, value) {
  const bytes = Buffer.isBuffer(value) ? value : Buffer.from(canonical(value));
  fs.writeFileSync(path.join(output, name), bytes);
}
function safeClean(target) {
  const resolved = path.resolve(target);
  ensure(path.basename(resolved) === "window1_fresh_holdout_exam_adapter_gate_20260806" ||
    path.basename(resolved) === "_tmp_window1_fresh_holdout_exam_adapter_gate_compare",
  `unsafe output ${resolved}`);
  ensure(resolved.startsWith(path.join(repo, ".claude") + path.sep), `output outside package root ${resolved}`);
  fs.rmSync(resolved, { recursive: true, force: true });
  fs.mkdirSync(resolved, { recursive: true });
}
function manifest(root) {
  return Object.fromEntries(fs.readdirSync(root)
    .filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name))
    .sort()
    .map((name) => {
      const file = path.join(root, name);
      return [name, { sha256: fileHash(file), bytes: fs.statSync(file).size }];
    }));
}
function verifyManifest(root) {
  const values = json(path.join(root, "ARTIFACT_HASH_MANIFEST.json")).files;
  const mismatches = [];
  for (const [name, expected] of Object.entries(values)) {
    const file = path.join(root, name);
    if (!fs.existsSync(file) || fileHash(file) !== expected.sha256 || fs.statSync(file).size !== expected.bytes) {
      mismatches.push(name);
    }
  }
  return { entries: Object.keys(values).length, mismatches, pass: mismatches.length === 0 };
}

function build() {
  safeClean(output);
  for (const brain of Object.values(brains)) requireCommit(brain.commit);

  const population = json(path.join(stage12, "EXAM_POPULATION.json"));
  const boundaryFile = path.join(stage12, "PRE_MATCH_BOUNDARY_LEDGER.jsonl");
  const eventList = fs.readFileSync(path.join(stage12, "EXAM_EVENT_LIST.txt"));
  const correctedList = fs.readFileSync(path.join(correctedSeal, "SEALED_EVENT_LIST.txt"));
  const correctedDeclaration = json(path.join(correctedSeal, "CORRECTED_SEALED_DECLARATION.json"));
  ensure(population.admitted_N === 171, "exam N changed");
  ensure(fileHash(boundaryFile) === boundarySha, "boundary hash changed");
  ensure(sha(eventList) === controllingListSha && eventList.equals(correctedList), "seal list mismatch");
  ensure(correctedDeclaration.event_list_sha256 === controllingListSha, "corrected declaration mismatch");

  const identity = {};
  const interfaceAudit = {};
  for (const [name, brain] of Object.entries(brains)) {
    const builderGit = gitShow(brain.commit, brain.builder);
    const builderWorking = fs.readFileSync(path.join(repo, brain.builder));
    ensure(builderGit.equals(builderWorking), `${name} builder working bytes differ from frozen commit`);
    const text = builderGit.toString("utf8");
    identity[name] = {
      commit: brain.commit,
      builder: {
        path: brain.builder,
        sha256_before: sha(builderGit),
        sha256_after: sha(builderWorking),
        bytes_before: builderGit.length,
        bytes_after: builderWorking.length,
        byte_identical: builderGit.equals(builderWorking),
      },
      policies: brain.policies.map((relative) => {
        const before = gitShow(brain.commit, relative);
        const after = fs.readFileSync(path.join(repo, relative));
        ensure(before.equals(after), `${name} policy working bytes differ ${relative}`);
        return {
          path: relative,
          sha256_before: sha(before),
          sha256_after: sha(after),
          bytes_before: before.length,
          bytes_after: after.length,
          byte_identical: before.equals(after),
        };
      }),
    };
    interfaceAudit[name] = {
      fixed_development_denominator: lines(text, /(?:baseEvents|events)\.length === 804/),
      fixed_development_leg_denominator: lines(text, /(?:inputLegs|v28Legs|baseTrace\.rows|tickers\.size)\.length?\s*===?\s*1608|tickers\.size === 1608/),
      fixed_input_bindings: lines(text, /const (?:base|eventPath|legPath|tracePath|scorePath|receiptPath|dispositionPath|START_LEDGER_PATH|R3_EVENT_PATH)\s*=/),
      external_population_argument: lines(text, /--(?:event-list|population|boundary|print-ledger|tape-root)/),
    };
  }

  const r3Text = gitShow(brains.R3.commit, brains.R3.builder).toString("utf8");
  const r3Blocker = {
    code: "R3_REQUIRES_FROZEN_V29R2_DECISION_STATE_NOT_RAW_TAPES",
    evidence: {
      input_bindings: lines(r3Text, /const (?:eventPath|legPath|tracePath|scorePath|receiptPath|dispositionPath)\s*=/),
      consumption: lines(r3Text, /const events = readRows\(eventPath\).*baseReceipts = readRows\(receiptPath\)/),
      denominator: lines(r3Text, /events\.length === 804.*baseReceipts\.length === 371/),
      raw_tape_boundary_entry_point: lines(r3Text, /--(?:event-list|boundary|print-ledger|tape-root)/),
    },
    missing_sealed_inputs: [
      "V29R2 EVENT_LEDGER for the sealed population",
      "V29R2 LEG_LEDGER for the sealed population",
      "V29R2 DECISION_TRACE for the sealed population",
      "V29R2 MIRROR_ARM_RECEIPTS for the sealed population",
      "V28 predecessor state for the sealed population",
    ],
    ruling: "Generating these upstream decisions is policy reconstruction, not path/population/ledger rebinding.",
  };

  const tapeSchema = {
    census_location: "VPS_READ_ONLY_FROM_STAGE12_ADMISSION_LEDGER",
    tapes: 342,
    unique_headers: 1,
    header: "ts_et,ticker,bid_1,bid_1_sz,bid_2,bid_2_sz,bid_3,bid_3_sz,bid_4,bid_4_sz,bid_5,bid_5_sz,ask_1,ask_1_sz,ask_2,ask_2_sz,ask_3,ask_3_sz,ask_4,ask_4_sz,ask_5,ask_5_sz,mid,bid_depth_5,ask_depth_5,depth_ratio,last_trade",
    required_strict_fill_fields: ["trade_id", "taker_side", "trade_size", "exchange_trade_timestamp"],
    headers_with_all_required_fields: 0,
    carried_last_trade_is_not_true_print_identity: true,
    blocker: "STRICT_FILL_LAW_CANNOT_BE_EVALUATED_FROM_SEALED_BOOK_SNAPSHOTS",
  };

  const rewrittenManifest = verifyManifest(rewrittenSeal);
  const rewriteRows = changedSealPaths.map((name) => {
    const relative = `.claude/window1_fresh_holdout_seal_20260806/${name}`;
    const working = fs.readFileSync(path.join(repo, relative));
    const committed = gitShow("HEAD", relative);
    return {
      path: relative,
      committed_sha256: sha(committed),
      working_sha256: sha(working),
      committed_bytes: committed.length,
      working_bytes: working.length,
      changed: !committed.equals(working),
    };
  });
  ensure(rewriteRows.every((row) => row.changed), "expected eight rewritten seal paths");
  const obsoleteWorkingDeclaration = json(path.join(rewrittenSeal, "SEALED_DECLARATION.json"));
  const obsoleteWorkingList = fs.readFileSync(path.join(rewrittenSeal, "SEALED_EVENT_LIST.txt"));
  const sealRewrite = {
    changed_paths: rewriteRows,
    common_write_timestamp_utc_observed: "2026-08-07T00:28:50Z",
    process_observation: {
      process_name: "node",
      pid: 10140,
      observed_before_exit: true,
      exact_command_line_captured: false,
    },
    writer_attribution: {
      path: "arb-executor/analysis/build_window1_fresh_holdout_seal_exam.js",
      confidence: "HIGH_SCHEMA_AND_DEFAULT_OUTPUT_PATH_MATCH; EXACT_EXITED_PROCESS_COMMAND_LINE_NOT_RECOVERABLE",
      reason: "The builder's default output, schema names, current-ref touch audit, N=0 rewrite and all-eight common write time match the observed files.",
    },
    rewritten_obsolete_package_self_verifies: rewrittenManifest,
    rewritten_obsolete_declaration: {
      N: obsoleteWorkingDeclaration.sealed_N,
      list_sha256: sha(obsoleteWorkingList),
      controlling: false,
      reason: "Superseded by the corrected decision-relevant TOUCH law package.",
    },
    controlling_corrected_declaration: {
      N: correctedDeclaration.sealed_N,
      declared_list_sha256: correctedDeclaration.event_list_sha256,
      actual_list_sha256: sha(correctedList),
      exam_list_sha256: sha(eventList),
      byte_identical_to_exam_list: correctedList.equals(eventList),
      verifies: correctedDeclaration.sealed_N === 171 &&
        correctedDeclaration.event_list_sha256 === sha(correctedList) &&
        correctedList.equals(eventList),
    },
    disposition: "PRESERVED_UNSTAGED_NOT_COMMITTED_NOT_USED_BY_EXAM",
  };

  const readiness = {
    status: "BLOCKED_BEFORE_DEV_INERTNESS_AND_STAGE3",
    input_binding_only_adapter_constructible: false,
    blockers: [r3Blocker.code, tapeSchema.blocker],
    dev_inertness: {
      V36: "NOT_STARTED_COMPLETE_THREE_BRAIN_ADAPTER_ABSENT",
      V35: "NOT_STARTED_COMPLETE_THREE_BRAIN_ADAPTER_ABSENT",
      R3: "NOT_STARTABLE_WITH_SEALED_RAW_INPUT_CONTRACT",
      decision_trace_comparisons: 0,
      scorecard_comparisons: 0,
    },
    stage3: {
      exam_process_invocations: 0,
      brain_invocations: { V36: 0, V35: 0, R3: 0, total: 0 },
      retries: 0,
      score_rows: 0,
      authorization_consumed: false,
    },
    required_operator_resolution: [
      "Authorize and freeze an exchange true-print ledger for all 342 sealed legs, or provide an already sealed hash-bound one.",
      "Provide or independently audit the complete V28->V29R2->R3 raw-tape replay lineage; an R3-only path adapter cannot synthesize predecessor decisions.",
    ],
  };

  write("POLICY_BYTE_IDENTITY_RECEIPT.json", { schema_version: "window1-exam-policy-byte-identity-v1", brains: identity });
  write("INPUT_INTERFACE_AUDIT.json", { schema_version: "window1-exam-input-interface-audit-v1", brains: interfaceAudit });
  write("R3_TRANSITIVE_INPUT_BLOCKER.json", r3Blocker);
  write("SEALED_STRICT_FILL_INPUT_AUDIT.json", tapeSchema);
  write("SEAL_REWRITE_RECONCILIATION.json", sealRewrite);
  write("ADAPTER_READINESS_RECEIPT.json", readiness);
  write("DEV_INERTNESS_GATE_RECEIPT.json", readiness.dev_inertness);
  write("EXAM_EXECUTION_RECEIPT.json", readiness.stage3);
  write("FORBIDDEN_ACCESS_RECEIPT.json", {
    live_engine_accesses: 0,
    order_accesses: 0,
    position_accesses: 0,
    service_mutations: 0,
    policy_mutations: 0,
    brain_invocations: 0,
    scorer_invocations: 0,
    public_trade_backfill_requests: 0,
    sealed_tape_access: "READ_ONLY_HEADER_CENSUS_ONLY",
  });
  write("CONTROL_BINDING.json", {
    construction_parent: child.execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim(),
    population_N: population.admitted_N,
    population_sha256: controllingListSha,
    boundary_sha256: boundarySha,
    brains: Object.fromEntries(Object.entries(brains).map(([name, brain]) => [name, brain.commit])),
    standing_authorization: "OPERATOR_PROMPT_THIS_TASK",
    authorization_consumed: false,
  });
  write("REPORT.md", Buffer.from(`# Sealed-171 exam adapter - fail-closed before DEV inertness\n\nThe binding-only adapter cannot be constructed from the supplied sealed inputs. All 342 sealed tape files carry BBO/depth and a carried last_trade field but no exchange trade identity, aggressor side, trade size or exchange timestamp, so the strict fill law cannot be evaluated. R3 is not a raw-tape brain: its frozen entry point consumes V29-R2 event, leg, trace, disposition and arm-receipt outputs. Synthesizing those decisions would be policy reconstruction.\n\nAll frozen builders and policy modules are byte-identical to their pinned Git objects. No DEV adapted harness or sealed exam brain ran. Decision-trace comparisons, scorecard comparisons, brain invocations, retries and score rows are zero. The standing one-run authorization remains unconsumed.\n\nThe eight externally rewritten old-seal files are self-consistent as an obsolete N=0 package but are not controlling. Their schema/default-output fingerprint matches build_window1_fresh_holdout_seal_exam.js; the exact command line of the exited Node process was not captured. The corrected 171-event declaration and the exam list remain byte-identical at SHA-256 ${controllingListSha}.\n`, "utf8"));
  write("INDEPENDENT_REVIEW_INSTRUCTION.md", Buffer.from("Independently validate every pinned Git object and policy byte hash; inspect the exact R3 builder input bindings and confirm it requires V29-R2 decision artifacts rather than raw tapes; recompute the 342-header sealed-tape schema census and confirm strict seller-aggressor evidence is absent; verify the corrected 171-event seal/list hash; confirm no DEV adapted harness, brain, scorer or Stage-3 exam process ran and authorization remains unconsumed.\n", "utf8"));
  write("SOURCE_HASH_MANIFEST.json", {
    files: {
      "arb-executor/analysis/build_window1_fresh_holdout_exam_adapter_gate.js": {
        sha256: fileHash(__filename),
        bytes: fs.statSync(__filename).size,
      },
    },
    frozen_policy_files: identity,
  });
  const firstManifest = manifest(output);
  if (compare) {
    const other = manifest(path.resolve(compare));
    ensure(JSON.stringify(firstManifest) === JSON.stringify(other), "adapter-gate package determinism mismatch");
    write("DETERMINISM_RECEIPT.json", {
      builds: 2,
      byte_identical: true,
      compared_files: Object.keys(firstManifest).length,
      mismatches: [],
    });
  } else {
    write("DETERMINISM_RECEIPT.json", { builds: 1, byte_identical: null, role: "FIRST_BUILD" });
  }
  const artifactFiles = manifest(output);
  artifactFiles["DETERMINISM_RECEIPT.json"] = {
    sha256: fileHash(path.join(output, "DETERMINISM_RECEIPT.json")),
    bytes: fs.statSync(path.join(output, "DETERMINISM_RECEIPT.json")).size,
  };
  write("ARTIFACT_HASH_MANIFEST.json", {
    files: Object.fromEntries(Object.entries(artifactFiles).sort(([a], [b]) => a.localeCompare(b))),
  });
  process.stdout.write(canonical(readiness));
}

build();
