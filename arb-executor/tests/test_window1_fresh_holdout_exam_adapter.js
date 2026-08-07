#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const file = path.resolve(__dirname, "../analysis/window1_fresh_holdout_exam_adapter.js");
const source = fs.readFileSync(file, "utf8");

assert(source.includes("const BRAINS ="));
assert(source.includes("R3_excluded_context_only"));
assert(source.includes("strict_trace_byte_identical"));
assert(source.includes("full_scorecard_byte_identical"));
assert(source.includes("authorization single-use guard"));
assert(source.includes("terminalCollapseReceipt"));
assert(source.includes("policy_files_modified: 0"));
assert(source.includes("replay_invocations: 1"));
assert(!source.includes("49f6501561c5d99a7f36c68ec41e0ea7250680e5\",\n+    builder"));
console.log(JSON.stringify({ pass: true, assertions: 9 }));
