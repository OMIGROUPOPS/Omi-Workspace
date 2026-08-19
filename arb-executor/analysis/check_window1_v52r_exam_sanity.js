#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const adapter = require("./window1_v52r_exam_adapter.js");

const args = process.argv.slice(2);
const arg = (name, fallback) => { const index = args.indexOf(name); return index < 0 ? fallback : args[index + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v52r_exam_adapter_sanity_30_20260818")));
const receiptPath = path.resolve(arg("--receipt", path.join(repo, ".claude/window1_live_v4_replay/v52r_exam_adapter_sanity_30_20260818.json")));
const frozen = path.join(repo, adapter.FROZEN_V52R_PACKAGE);
const builder = path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js");
const reuseOutput = arg("--reuse-output", "false") === "true";

if (!fs.existsSync(frozen)) throw new Error(`frozen V52r cohort package absent: ${frozen}`);
if (!reuseOutput) {
  const child = spawnSync(process.execPath, [...process.execArgv, builder, "--variant", "v52r", "--stage", "cohort30", "--repo", repo, "--output", output], { cwd: repo, stdio: "inherit" });
  if (child.error) throw child.error;
  if (child.status !== 0) process.exit(child.status ?? 1);
}
if (!fs.existsSync(output)) throw new Error(`candidate V52r cohort package absent: ${output}`);

const comparison = adapter.compareCohortBuild(frozen, output);
const receipt = {
  ...comparison,
  policy_byte_identity: adapter.attestFrozenPolicy(repo),
  v52e804_lane_non_regression: adapter.attestV52eLaneUnchanged(repo),
  candidate_package_file_count: fs.readdirSync(output).length,
  frozen_package_file_count: fs.readdirSync(frozen).length,
};
fs.mkdirSync(path.dirname(receiptPath), { recursive: true });
fs.writeFileSync(receiptPath, adapter.canonical(receipt));
process.stdout.write(adapter.canonical({ receipt: receiptPath, compared_files: receipt.compared_files, pass: receipt.pass }));
