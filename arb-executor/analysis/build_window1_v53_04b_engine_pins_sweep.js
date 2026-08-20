#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { execFileSync } = require("child_process");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v53_04b_engine_pins_sweep_20260820")));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const runRoot = path.resolve(arg("--run-root", path.join(os.tmpdir(), `v53_04b_engine_pins_sweep_${path.basename(output)}`)));
const runner = path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js");
const policyFile = path.join(repo, "arb-executor/analysis/window1_v53_riser_arming_law.js");
const laws = [
  "A0_CONTROL_PROXY_SECOND_VISIT",
  "A1_PROXY_FIRST_VISIT",
  "A2_FIRST_TRUE_DIVOT_AND_RESUME",
  "A3_FIRST_SELLER_HIT",
  "A4_BID_PERSISTENCE_300S",
  "A5_FIRST_TWO_SIDED_BOOK",
];

const ensure = (value, message) => { if (!value) throw new Error(message); };
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const shaBytes = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileHash = (file) => shaBytes(fs.readFileSync(file));
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const write = (name, value) => fs.writeFileSync(path.join(output, name), typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value));
const manifest = (dir) => {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
};

async function armingLedger(file, lawId) {
  const states = new Map();
  const input = fs.createReadStream(file).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue;
    const row = JSON.parse(line), legId = String(row.leg_identity).split("|").at(-1), view = row.game_view?.legs?.[legId] ?? null;
    const key = `${row.event_id}|${row.leg_identity}`;
    if (!states.has(key)) states.set(key, { event_id: row.event_id, leg_identity: row.leg_identity, arming_law: lawId, armed: false, arm_count: 0, first_arm_timestamp_epoch: null, first_arm_receipt: null, first_arm_reason: null, first_arm_observed_at: null });
    const state = states.get(key), arm = view?.riser_arm;
    if (!arm) continue;
    state.arm_count = Math.max(state.arm_count, Number.isInteger(arm.arm_count) ? arm.arm_count : arm.armed ? 1 : 0);
    if (arm.armed && !state.armed) {
      state.armed = true;
      state.first_arm_timestamp_epoch = arm.armed_timestamp_epoch ?? null;
      state.first_arm_receipt = arm.armed_receipt ?? null;
      state.first_arm_reason = arm.arm_reason ?? null;
      state.first_arm_observed_at = {
        timestamp_epoch: row.timestamp_epoch,
        receipt: row.receipt,
        t_minus_scheduled_seconds: row.t_minus_scheduled_seconds,
        t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds,
      };
    }
  }
  return [...states.values()].sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity));
}

async function main() {
  ensure(path.basename(output).includes("v53"), `unsafe output ${output}`);
  ensure(path.basename(runRoot).includes("v53"), `unsafe run root ${runRoot}`);
  fs.rmSync(output, { recursive: true, force: true }); fs.mkdirSync(output, { recursive: true });
  fs.rmSync(runRoot, { recursive: true, force: true }); fs.mkdirSync(runRoot, { recursive: true });
  const implementationCommit = execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim();
  const rows = [], ledgers = {};
  for (const [ordinal, law] of laws.entries()) {
    const childOutput = path.join(runRoot, `v53_04b_${law}`);
    const args = [runner, "--repo", repo, "--variant", "v53-04", "--stage", "pins5", "--v53-arming-law", law, "--private-root", privateRoot, "--output", childOutput];
    execFileSync(process.execPath, args, { cwd: repo, stdio: ["ignore", "pipe", "inherit"], maxBuffer: 16 * 1024 * 1024 });
    const score = readJson(path.join(childOutput, "PINS_SMOKE_RECEIPT.json"));
    const assertions = readJson(path.join(childOutput, "STAGE1_BUILD_ASSERTIONS.json"));
    const f24 = readJson(path.join(childOutput, "F24_SCOREBOARD.json"));
    const ledger = await armingLedger(path.join(childOutput, "FULL_DECISION_TRACE_5.jsonl.gz"), law);
    const candidate = score.candidate, comparator = score.comparator;
    rows.push({
      selector_order: ordinal,
      law_id: law,
      implementation_commit: implementationCommit,
      completes: candidate.completed_pairs,
      under_par_pairs: candidate.under_par_pairs,
      locked_cents: candidate.locked_cents,
      average_game_delta_cents: candidate.average_locked_delta_cents,
      completed_event_ids: candidate.completed_event_ids,
      champion_event_ids: comparator.completed_event_ids,
      identity_vs_champion: {
        held: comparator.completed_event_ids.filter((id) => candidate.completed_event_ids.includes(id)),
        lost: comparator.completed_event_ids.filter((id) => !candidate.completed_event_ids.includes(id)),
        gained: candidate.completed_event_ids.filter((id) => !comparator.completed_event_ids.includes(id)),
      },
      asserts_clean: assertions.pass === true,
      assertion_receipt_sha256: fileHash(path.join(childOutput, "STAGE1_BUILD_ASSERTIONS.json")),
      arming_events: ledger.reduce((sum, item) => sum + item.arm_count, 0),
      armed_legs: ledger.filter((item) => item.armed).length,
      first_arm_timing_by_leg: ledger,
      source_package_hashes: {
        pins_receipt: fileHash(path.join(childOutput, "PINS_SMOKE_RECEIPT.json")),
        f24_scoreboard: fileHash(path.join(childOutput, "F24_SCOREBOARD.json")),
        market_event_ledger: fileHash(path.join(childOutput, "MARKET_EVENT_LEDGER_5.jsonl.gz")),
      },
    });
    ledgers[law] = ledger;
    write(`${law}_F24_SCOREBOARD.json`, f24);
    write(`${law}_BUILD_ASSERTIONS.json`, assertions);
    write(`${law}_PINS_SCORECARD.json`, score);
    fs.copyFileSync(path.join(childOutput, "MARKET_EVENT_LEDGER_5.jsonl.gz"), path.join(output, `${law}_MARKET_EVENT_LEDGER_5.jsonl.gz`));
    process.stdout.write(`${law}: ${candidate.completed_pairs} completes / ${candidate.locked_cents}c / ${ledger.reduce((sum, item) => sum + item.arm_count, 0)} arms\n`);
  }
  const control = rows[0];
  const controlFence = {
    expected: { completed_pairs: 4, locked_cents: 117 },
    observed: { completed_pairs: control.completes, locked_cents: control.locked_cents },
    identity_exact: control.identity_vs_champion.lost.length === 0 && control.identity_vs_champion.gained.length === 0,
    assertions_clean: control.asserts_clean,
  };
  controlFence.pass = controlFence.observed.completed_pairs === 4 && controlFence.observed.locked_cents === 117 && controlFence.identity_exact && controlFence.assertions_clean;
  ensure(controlFence.pass, `A0 harness defect STOP ${JSON.stringify(controlFence)}`);
  for (const row of rows) {
    row.selector = {
      identity_held: row.identity_vs_champion.lost.length === 0,
      completes_at_least_4: row.completes >= 4,
      asserts_clean: row.asserts_clean,
    };
    row.selector.survivor = Object.values(row.selector).every((value) => value === true);
  }
  const survivors = rows.filter((row) => row.selector.survivor).sort((a, b) => b.locked_cents - a.locked_cents || a.arming_events - b.arming_events || a.selector_order - b.selector_order);
  const winner = survivors[0] ?? null;
  const sweep = {
    label: "V53_04B_ENGINE_PINS_SWEEP",
    object_under_test: "ACTUAL_V53_04_ENGINE_BYTE_EQUAL_OUTSIDE_RISER_ARMING_CLAUSE",
    implementation_commit: implementationCommit,
    control_fence: controlFence,
    selector: { pre_registered: true, survivor_law: "IDENTITY_HELD_AND_COMPLETES_GE_4_AND_ASSERTS_CLEAN", winner_law: "HIGHEST_LOCKED_CENTS_THEN_FEWER_ARMS", stable_final_tie_break: "DECLARED_A0_TO_A5_ORDER", survivors: survivors.map((row) => row.law_id), winner: winner?.law_id ?? null },
    laws: rows,
    disposition: winner ? "SURVIVOR_EXISTS_FRESH25_PREREGISTRATION_PERMITTED" : "STOP_BANK_ARMING_LAW_ENGINE_SPACE_CAUSE_NO_FRESH25",
    full_804_run: false,
  };
  write("ENGINE_PINS_SWEEP.json", sweep);
  write("ENGINE_ARMING_LEDGER.json", { rows: laws.flatMap((law) => ledgers[law]) });
  write("POLICY_BYTE_BINDING.json", {
    implementation_commit: implementationCommit,
    runner: { path: path.relative(repo, runner).replaceAll("\\", "/"), sha256: fileHash(runner) },
    policy: { path: path.relative(repo, policyFile).replaceAll("\\", "/"), sha256: fileHash(policyFile) },
    unchanged_outside_riser_arming_clause: true,
  });
  write("FORBIDDEN_ACCESS_RECEIPT.json", { full_804: false, fresh_25: false, sealed: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false });
  write("REPORT.md", `# V53-04b engine pins sweep\n\nA0 reproduced V52l at ${control.completes} completes / ${control.locked_cents}c: ${controlFence.pass ? "PASS" : "FAIL"}.\n\n${rows.map((row) => `- ${row.law_id}: ${row.completes} completes / ${row.locked_cents}c; arms ${row.arming_events}; identity ${row.selector.identity_held ? "held" : `lost ${row.identity_vs_champion.lost.join(", ")}`}; assertions ${row.asserts_clean ? "clean" : "failed"}; survivor ${row.selector.survivor}.`).join("\n")}\n\nWinner: ${winner?.law_id ?? "NONE"}. ${sweep.disposition}. The fresh 25 and the full 804 were not run in this lane.\n`);

  const baseNames = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const ignored = new Set(["DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"]);
    const names = [...new Set([...baseNames, ...fs.readdirSync(compare)])].filter((name) => !ignored.has(name)).sort();
    const mismatches = names.filter((name) => !fs.existsSync(path.join(output, name)) || !fs.existsSync(path.join(compare, name)) || fileHash(path.join(output, name)) !== fileHash(path.join(compare, name)));
    ensure(!mismatches.length, `V53-04b sweep determinism mismatch ${mismatches.join(",")}`);
    determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); manifest(compare);
  } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  write("DETERMINISM_RECEIPT.json", determinism); manifest(output);
  if (compare) ensure(fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")), "V53-04b final manifests differ");
  process.stdout.write(canonical({ output, winner: winner?.law_id ?? null, control_fence: controlFence, determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error.message}\n`); process.exitCode = 1; });
