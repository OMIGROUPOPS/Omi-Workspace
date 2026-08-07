#!/usr/bin/env node
"use strict";

const child = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "window1-exam-adapter-gate-"));
const output = path.join(repo, ".claude", "_tmp_window1_fresh_holdout_exam_adapter_gate_compare");

try {
  child.execFileSync("node", [
    "arb-executor/analysis/build_window1_fresh_holdout_exam_adapter_gate.js",
    "--repo", ".",
    "--output", output,
  ], { cwd: repo, stdio: "pipe" });
  const readiness = JSON.parse(fs.readFileSync(path.join(output, "ADAPTER_READINESS_RECEIPT.json"), "utf8"));
  if (readiness.status !== "BLOCKED_BEFORE_DEV_INERTNESS_AND_STAGE3") throw new Error("gate did not block");
  if (!readiness.blockers.includes("R3_REQUIRES_FROZEN_V29R2_DECISION_STATE_NOT_RAW_TAPES")) throw new Error("R3 blocker absent");
  if (!readiness.blockers.includes("STRICT_FILL_LAW_CANNOT_BE_EVALUATED_FROM_SEALED_BOOK_SNAPSHOTS")) throw new Error("strict-fill blocker absent");
  if (readiness.stage3.authorization_consumed !== false || readiness.stage3.brain_invocations.total !== 0) throw new Error("authorization accounting changed");
  const identity = JSON.parse(fs.readFileSync(path.join(output, "POLICY_BYTE_IDENTITY_RECEIPT.json"), "utf8"));
  for (const brain of Object.values(identity.brains)) {
    if (!brain.builder.byte_identical || brain.policies.some((row) => !row.byte_identical)) throw new Error("policy identity failed");
  }
  const seal = JSON.parse(fs.readFileSync(path.join(output, "SEAL_REWRITE_RECONCILIATION.json"), "utf8"));
  if (!seal.controlling_corrected_declaration.verifies || seal.changed_paths.length !== 8) throw new Error("seal reconciliation failed");
  process.stdout.write("adapter_gate_tests_passed\n");
} finally {
  if (fs.existsSync(output)) fs.rmSync(output, { recursive: true, force: true });
  fs.rmSync(temp, { recursive: true, force: true });
}
