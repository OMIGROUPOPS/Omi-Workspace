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
assert(source.includes('require("./window1_streaming_gzip_jsonl.js")'));
assert(source.includes("async function materializeBrainArtifacts"));
assert(source.includes("async function runAndMaterializeBrain"));
assert(source.includes('"FULL_DECISION_TRACE.jsonl.gz": result.decisions'));
assert(source.includes("for (const [artifact, rows] of Object.entries(brainRowArtifacts(result))) await writeGzipRowsFile"));
assert(source.includes("all_jsonl_ledgers_streamed: true"));
assert(source.includes("full_decision_trace_jsonl_byte_identical"));
assert(source.includes("frozenFullTraceDigest"));
assert(!source.includes('"FULL_DECISION_TRACE.jsonl.gz": gzipRows(result.decisions)'));
assert(!source.includes("function gzipRows"));
assert(!source.includes("rows.map(JSON.stringify).join"));
assert(!source.includes("const results = {}, artifactBuilds = {}"));
assert(source.includes('policySha256: "5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73"'));
assert(source.includes('policySha256: "14d237ccfcda4c716a43c6c455ad0f4a8c8994835f770bd3ff18ce4d7d79a54f"'));
assert(!source.includes("49f6501561c5d99a7f36c68ec41e0ea7250680e5\",\n+    builder"));
console.log(JSON.stringify({ pass: true, assertions: 22 }));
