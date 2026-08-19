#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const path = require("path");

const args = process.argv.slice(2);
const repoIndex = args.indexOf("--repo");
const repo = path.resolve(repoIndex >= 0 ? args[repoIndex + 1] : ".");
const builder = path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js");
const forwarded = args.filter((value, index) => !(value === "--variant" || (index > 0 && args[index - 1] === "--variant")) && !(value === "--stage" || (index > 0 && args[index - 1] === "--stage")));
const result = childProcess.spawnSync(process.execPath, [builder, "--variant", "v52s804", "--stage", "disposition804", ...forwarded], { cwd: repo, stdio: "inherit" });
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
