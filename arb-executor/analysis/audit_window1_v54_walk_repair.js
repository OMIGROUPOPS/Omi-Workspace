"use strict";

const fs = require("fs");
const zlib = require("zlib");
const readline = require("readline");
const crypto = require("crypto");
const path = require("path");

function arg(name) {
  const index = process.argv.indexOf(`--${name}`);
  if (index < 0 || !process.argv[index + 1]) throw new Error(`missing --${name}`);
  return path.resolve(process.argv[index + 1]);
}
function sha256(file) {
  const hash = crypto.createHash("sha256"), fd = fs.openSync(file, "r"), buffer = Buffer.alloc(8 * 1024 * 1024);
  try { for (;;) { const count = fs.readSync(fd, buffer, 0, buffer.length, null); if (!count) break; hash.update(buffer.subarray(0, count)); } }
  finally { fs.closeSync(fd); }
  return hash.digest("hex");
}
function key(row) { return `${row.event_id}|${row.leg_identity}|${row.receipt}`; }
function actionStatement(row) {
  const action = row.joint_license?.action;
  if (!action) return null;
  const target = Number.isInteger(action.target_cents) ? action.target_cents : "NONE";
  const active = Number.isInteger(action.active_target_before_cents) ? action.active_target_before_cents : "NONE";
  return `ACTION=${action.action}; TARGET_CENTS=${target}; ACTIVE_TARGET_BEFORE_CENTS=${active}.`;
}
function preformationLeak(row) {
  const legId = String(row.leg_identity ?? "").split("|").at(-1);
  const end = row.game_view?.legs?.[legId]?.l16_formation_anchor?.formation_end_epoch
    ?? row.birth_license?.game_view?.legs?.[legId]?.l16_formation_anchor?.formation_end_epoch;
  const before = Number.isFinite(end) && Number.isFinite(row.timestamp_epoch) && row.timestamp_epoch < end;
  const posts = ["PLACE_REST", "REPRICE_REST"].includes(row.final_action) || Number.isInteger(row.final_target_cents);
  return before && posts ? { event_id: row.event_id, leg_identity: row.leg_identity, receipt: row.receipt, timestamp_epoch: row.timestamp_epoch, formation_end_epoch: end, seconds_early: end - row.timestamp_epoch, action: row.final_action, target_cents: row.final_target_cents } : null;
}

async function scan(file, selectedKeys = null) {
  const lines = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  const result = { rows: 0, events: new Set(), old_applied: new Map(), selected: new Map(), preformation_leaks: [], formation_gate_rows: 0, missing_hours_from_discovery: 0, min_hours_from_discovery: null, max_hours_from_discovery: null, sentence_action_failures: [] };
  for await (const line of lines) {
    if (!line.trim()) continue;
    const row = JSON.parse(line); result.rows += 1; result.events.add(row.event_id);
    const leak = preformationLeak(row); if (leak) result.preformation_leaks.push(leak);
    if (row.v54_pair_model?.reason === "V54_FORMATION_NOT_SETTLED_NO_POST") result.formation_gate_rows += 1;
    if (!Number.isFinite(row.hours_from_discovery)) result.missing_hours_from_discovery += 1;
    else {
      result.min_hours_from_discovery = result.min_hours_from_discovery === null ? row.hours_from_discovery : Math.min(result.min_hours_from_discovery, row.hours_from_discovery);
      result.max_hours_from_discovery = result.max_hours_from_discovery === null ? row.hours_from_discovery : Math.max(result.max_hours_from_discovery, row.hours_from_discovery);
    }
    const rowKey = key(row);
    if (row.event_id === "KXATPCHALLENGERMATCH-26JUL14URSPAL" && row.v54_pair_model?.applied === true) result.old_applied.set(rowKey, row);
    if (selectedKeys?.has(rowKey)) {
      result.selected.set(rowKey, row);
      const statement = actionStatement(row);
      if (!statement || row.joint_license?.sentence_action_assertion?.equal !== true || !row.joint_license?.sentence?.includes(statement) || row.joint_license?.action?.action !== row.final_action || (row.joint_license?.action?.target_cents ?? null) !== (row.final_target_cents ?? null)) {
        result.sentence_action_failures.push(rowKey);
      }
    }
  }
  return result;
}

async function main() {
  const oldFile = arg("old"), newFile = arg("new"), output = arg("output");
  const oldRun = await scan(oldFile), selectedKeys = new Set(oldRun.old_applied.keys()), newRun = await scan(newFile, selectedKeys);
  const oldContradictions = [...oldRun.old_applied.values()].filter((row) => String(row.joint_license?.sentence ?? "").includes("No pair-model price adjustment was made"));
  const newContradictions = [...newRun.selected.values()].filter((row) => String(row.joint_license?.sentence ?? "").includes("No pair-model price adjustment was made"));
  const oldLeakSummary = Object.values(Object.groupBy(oldRun.preformation_leaks, (row) => row.event_id)).map((rows) => ({
    event_id: rows[0].event_id,
    leaking_receipts: rows.length,
    maximum_seconds_early: Math.max(...rows.map((row) => row.seconds_early)),
    birth_posts: rows.filter((row) => row.action === "PLACE_REST").map((row) => ({ leg_identity: row.leg_identity, receipt: row.receipt, target_cents: row.target_cents, seconds_early: row.seconds_early })),
  }));
  const pass = oldRun.old_applied.size === 110 && oldContradictions.length === 110 && newRun.selected.size === 110 && newContradictions.length === 0 && newRun.sentence_action_failures.length === 0 && newRun.preformation_leaks.length === 0 && newRun.missing_hours_from_discovery === 0;
  const receipt = {
    label: "V54_WALK5_REPAIR_V6",
    pass,
    population: [...newRun.events].sort(),
    scope: { games: 5, full_804_run: false, sealed_read: false, live_mutation: false },
    sentence_action: { old_urspal_applied_receipts: oldRun.old_applied.size, old_contradictory_sentences: oldContradictions.length, reemitted_receipts: newRun.selected.size, remaining_contradictory_sentences: newContradictions.length, hard_assert_failures: newRun.sentence_action_failures },
    preformation: { old_leaks: oldLeakSummary, repaired_leaks: newRun.preformation_leaks, formation_gate_rows: newRun.formation_gate_rows },
    one_clock: { law: "HOURS_FROM_DISCOVERY", rows: newRun.rows, missing: newRun.missing_hours_from_discovery, minimum: newRun.min_hours_from_discovery, maximum: newRun.max_hours_from_discovery },
    external_custody: {
      old_trace: { path: oldFile, sha256: sha256(oldFile), bytes: fs.statSync(oldFile).size, rows: oldRun.rows },
      repaired_trace: { path: newFile, sha256: sha256(newFile), bytes: fs.statSync(newFile).size, rows: newRun.rows, reason_not_committed: "L22 forbids committed files above 50 MB." }
    }
  };
  fs.writeFileSync(output, `${JSON.stringify(receipt, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify({ output, pass, old_urspal_contradictions: oldContradictions.length, reemitted: newRun.selected.size, repaired_preformation_leaks: newRun.preformation_leaks.length, missing_hours: newRun.missing_hours_from_discovery }, null, 2)}\n`);
  if (!pass) process.exitCode = 1;
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
