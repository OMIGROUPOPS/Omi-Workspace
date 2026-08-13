#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/v52e_disposition_804_blocked_20260813");
const json = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
let tests = 0;
const check = (value, message) => { tests += 1; assert.ok(value, message); };

const block = json("EXAM_BLOCK_RECEIPT.json"), trace = json("TRACE_CHUNK_MANIFEST.json"), policy = json("POLICY_BYTE_IDENTITY.json"), offer = json("OFFER_DENOMINATOR_BINDING.json"), determinism = json("DETERMINISM_RECEIPT.json"), forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json"), artifacts = json("ARTIFACT_HASH_MANIFEST.json");
check(block.status === "BLOCKED_PRE_SCORE_SPECIFICATION_AMBIGUITY", "block status");
check(block.replay_events_processed === 804, "804 replay events");
check(block.observed_unrepresentable_games === 4, "four unrepresentable games");
check(block.score_rows_emitted === 0, "zero score rows");
check(block.rerun_after_specification_block === false, "no post-block rerun");
check(trace.chunk_count === 101 && trace.chunks.length === 101, "trace chunk conservation");
check(trace.chunks.every((row) => row.bytes > 0 && row.bytes < 100_000_000), "Git-safe nonempty chunks");
check(trace.chunks.every((row) => hash(path.join(out, row.name)) === row.sha256), "trace hashes");
check(policy.all_byte_identical, "policy identity");
check(Object.values(policy.files).every((row) => row.byte_identical), "all policy files identical");
check(offer.requested.OFFERED_POST_ONSET === 612 && offer.requested.GE_10 === 90 && offer.requested.GE_5 === 236 && offer.requested.GE_3 === 384 && offer.requested.THIN_1_TO_2 === 228, "offer denominator binding");
check(offer.scored_capture === null, "offer capture remains null");
check(determinism.byte_identical_score_builds === null, "no false determinism claim");
check(Object.values(forbidden).every((value) => value === false), "forbidden access all false");
check(["TWO_RULER_SCORECARD.json", "FRONTIER.json", "REGRET_GAUGE.json"].every((name) => !fs.existsSync(path.join(out, name))), "score artifacts absent");
check(Object.entries(artifacts.files).every(([name, row]) => hash(path.join(out, name)) === row.sha256), "artifact hashes");

console.log(JSON.stringify({ tests, pass: true, status: block.status, trace_chunks: trace.chunk_count, trace_bytes: trace.total_bytes }));
