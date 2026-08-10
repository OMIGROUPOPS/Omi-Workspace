#!/usr/bin/env node
"use strict";

const path = require("path");
const { spawnSync } = require("child_process");

const builder = path.join(__dirname, "build_window1_v38_maker_only.js");
const result = spawnSync(process.execPath, [...process.execArgv, builder, "--variant", "v47", ...process.argv.slice(2)], {
  stdio: "inherit",
});
process.exit(result.status ?? 1);
