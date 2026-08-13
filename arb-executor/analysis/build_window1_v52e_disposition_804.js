#!/usr/bin/env node
"use strict";

const path = require("path");
const { spawnSync } = require("child_process");

const args = process.argv.slice(2);
const repoIndex = args.indexOf("--repo");
const repo = path.resolve(repoIndex >= 0 ? args[repoIndex + 1] : ".");
const builder = path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js");
const child = spawnSync(process.execPath, [...process.execArgv, builder, "--variant", "v52e804", "--stage", "disposition804", ...args], { cwd: repo, stdio: "inherit" });
if (child.error) throw child.error;
process.exit(child.status ?? 1);
