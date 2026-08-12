#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const packageRoot = path.join(repo, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812");
const output = path.resolve(process.argv.includes("--output") ? process.argv[process.argv.indexOf("--output") + 1] : path.join(repo, ".claude/window1_live_v4_replay/v52c_flip_query_20260812"));
const compare = process.argv.includes("--compare") ? path.resolve(process.argv[process.argv.indexOf("--compare") + 1]) : null;
const SOURCE_COMMIT = "08ce27c0a297ed707cfd89aa29e60be223c9df7f";

function ensure(value, message) { if (!value) throw new Error(message); }
function shaFile(file) { const hash = crypto.createHash("sha256"); hash.update(fs.readFileSync(file)); return hash.digest("hex"); }
function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return value;
}
function canonical(value) { return `${JSON.stringify(stable(value), null, 2)}\n`; }
function safeOutput(dir) {
  ensure(dir.startsWith(repo + path.sep) || dir.startsWith(path.resolve("C:/tmp") + path.sep), `unsafe output ${dir}`);
  ensure(!fs.existsSync(dir), `output exists ${dir}`);
  fs.mkdirSync(dir, { recursive: true });
}
async function readGzipRows(file, eventIds) {
  const rows = [];
  const lines = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue;
    const row = JSON.parse(line);
    if (eventIds.has(row.event_id)) rows.push(row);
  }
  return rows;
}
async function writeGzipRows(file, rows) {
  await new Promise((resolve, reject) => {
    const gzip = zlib.createGzip({ level: 9, mtime: 0 });
    const target = fs.createWriteStream(file, { flags: "wx" });
    gzip.on("error", reject); target.on("error", reject); target.on("finish", resolve); gzip.pipe(target);
    for (const row of rows) gzip.write(`${JSON.stringify(stable(row))}\n`);
    gzip.end();
  });
}
function traceKey(row) { return `${row.leg_identity}|${row.timestamp_epoch}|${row.receipt}`; }
function readVerdict(row) {
  return {
    passed: row.read?.passed ?? null,
    state: row.read?.state ?? null,
    quote_path_state: row.read?.quote_path_state ?? null,
    pressure_state: row.read?.pressure_state ?? null,
    receipt: row.read?.receipt ?? null,
  };
}
function decisionState(row) {
  return {
    gate_verdict: row.gate_verdict,
    blocked_clause: row.blocked_clause,
    final_action: row.final_action,
    final_target_cents: row.final_target_cents,
    reason: row.reason,
  };
}
function transitions(rows, machine) {
  const byLeg = new Map();
  for (const row of rows) {
    if (!byLeg.has(row.leg_identity)) byLeg.set(row.leg_identity, []);
    byLeg.get(row.leg_identity).push(row);
  }
  return [...byLeg].sort(([a], [b]) => a.localeCompare(b)).flatMap(([leg, legRows]) => {
    let prior = null;
    return legRows.filter((row) => {
      const now = JSON.stringify(decisionState(row));
      if (now === prior) return false;
      prior = now;
      return true;
    }).map((row) => ({ machine, event_id: row.event_id, leg_identity: leg, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, observation: row.observation, sibling_observation: row.sibling_observation, read: row.read, gate_verdict: row.gate_verdict, blocked_clause: row.blocked_clause, final_action: row.final_action, final_target_cents: row.final_target_cents, reason: row.reason }));
  });
}
function outcomeMap(rows) { return new Map(rows.map((row) => [row.event_id, row])); }
function manifest(dir) {
  return { source_commit: SOURCE_COMMIT, files: Object.fromEntries(fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { sha256: shaFile(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) };
}

async function main() {
  safeOutput(output);
  const baselineOutcomePath = path.join(packageRoot, "V52B_BASELINE_FLOW_OUTCOMES_OBSERVATION_ONLY.json");
  const candidateOutcomePath = path.join(packageRoot, "V52C_FLOW_OUTCOMES_OBSERVATION_ONLY.json");
  const baselineTracePath = path.join(packageRoot, "V52B_BASELINE_FULL_DECISION_TRACE_30_GAMES.jsonl.gz");
  const candidateTracePath = path.join(packageRoot, "V52C_FULL_DECISION_TRACE_30_GAMES.jsonl.gz");
  for (const file of [baselineOutcomePath, candidateOutcomePath, baselineTracePath, candidateTracePath]) ensure(fs.existsSync(file), `missing ${file}`);
  const baselineOutcomes = JSON.parse(fs.readFileSync(baselineOutcomePath, "utf8"));
  const candidateOutcomes = JSON.parse(fs.readFileSync(candidateOutcomePath, "utf8"));
  const candidateByEvent = outcomeMap(candidateOutcomes);
  const flips = baselineOutcomes.filter((row) => row.completed_pair_observation && !candidateByEvent.get(row.event_id)?.completed_pair_observation);
  ensure(flips.length > 0, "no V52b-to-V52c completion flip");
  const flipIds = new Set(flips.map((row) => row.event_id));
  const baselineRows = await readGzipRows(baselineTracePath, flipIds);
  const candidateRows = await readGzipRows(candidateTracePath, flipIds);
  const baselineByKey = new Map(baselineRows.map((row) => [traceKey(row), row]));
  const candidateByKey = new Map(candidateRows.map((row) => [traceKey(row), row]));
  ensure(baselineByKey.size === baselineRows.length && candidateByKey.size === candidateRows.length, "duplicate trace keys");
  const flipReceipts = [];
  const combinedForward = [];
  const forwardTruth = [];
  const consequence = [];
  for (const baselineOutcome of flips.sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    const candidateOutcome = candidateByEvent.get(baselineOutcome.event_id);
    const common = baselineRows.filter((row) => row.event_id === baselineOutcome.event_id && candidateByKey.has(traceKey(row))).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
    const firstSemantic = common.find((row) => JSON.stringify(readVerdict(row)) !== JSON.stringify(readVerdict(candidateByKey.get(traceKey(row))))) ?? null;
    const firstPayload = common.find((row) => JSON.stringify(row.read) !== JSON.stringify(candidateByKey.get(traceKey(row)).read)) ?? null;
    const firstDecision = common.find((row) => JSON.stringify(decisionState(row)) !== JSON.stringify(decisionState(candidateByKey.get(traceKey(row))))) ?? null;
    const divergenceBaseline = firstSemantic ?? firstPayload;
    ensure(divergenceBaseline, `no read divergence ${baselineOutcome.event_id}`);
    const divergenceCandidate = candidateByKey.get(traceKey(divergenceBaseline));
    const start = divergenceBaseline.timestamp_epoch;
    const baselineForward = baselineRows.filter((row) => row.event_id === baselineOutcome.event_id && row.timestamp_epoch >= start).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
    const candidateForward = candidateRows.filter((row) => row.event_id === baselineOutcome.event_id && row.timestamp_epoch >= start).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
    flipReceipts.push({
      event_id: baselineOutcome.event_id,
      divergence_kind: firstSemantic ? "FIRST_SEMANTIC_READ_VERDICT_DIFFERENCE" : "FIRST_READ_EVIDENCE_PAYLOAD_DIFFERENCE",
      common_key: traceKey(divergenceBaseline),
      timestamp_epoch: start,
      t_minus_scheduled_seconds: divergenceBaseline.t_minus_scheduled_seconds,
      t_minus_actual_bell_seconds: divergenceBaseline.t_minus_actual_bell_seconds,
      receipt: divergenceBaseline.receipt,
      leg_identity: divergenceBaseline.leg_identity,
      V52B_BLIND_FIXED_TRAIL: { read_verdict: readVerdict(divergenceBaseline), read_evidence: divergenceBaseline.read, decision: decisionState(divergenceBaseline), observation: divergenceBaseline.observation, sibling_observation: divergenceBaseline.sibling_observation },
      V52C_SIGHTED_FULL_POST_ONSET: { read_verdict: readVerdict(divergenceCandidate), read_evidence: divergenceCandidate.read, decision: decisionState(divergenceCandidate), observation: divergenceCandidate.observation, sibling_observation: divergenceCandidate.sibling_observation },
      first_downstream_decision_difference: firstDecision ? {
        common_key: traceKey(firstDecision),
        timestamp_epoch: firstDecision.timestamp_epoch,
        t_minus_scheduled_seconds: firstDecision.t_minus_scheduled_seconds,
        t_minus_actual_bell_seconds: firstDecision.t_minus_actual_bell_seconds,
        receipt: firstDecision.receipt,
        leg_identity: firstDecision.leg_identity,
        V52B_BLIND_FIXED_TRAIL: { read: firstDecision.read, decision: decisionState(firstDecision), observation: firstDecision.observation, sibling_observation: firstDecision.sibling_observation },
        V52C_SIGHTED_FULL_POST_ONSET: { read: candidateByKey.get(traceKey(firstDecision)).read, decision: decisionState(candidateByKey.get(traceKey(firstDecision))), observation: candidateByKey.get(traceKey(firstDecision)).observation, sibling_observation: candidateByKey.get(traceKey(firstDecision)).sibling_observation },
      } : null,
    });
    combinedForward.push(...baselineForward.map((row) => ({ machine: "V52B_BLIND_FIXED_TRAIL", ...row })), ...candidateForward.map((row) => ({ machine: "V52C_SIGHTED_FULL_POST_ONSET", ...row })));
    const truthIndex = new Map();
    for (const row of [...baselineForward, ...candidateForward]) {
      const key = `${row.timestamp_epoch}|${row.receipt}|${JSON.stringify(row.observation)}`;
      if (!truthIndex.has(key)) truthIndex.set(key, { event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, observation: row.observation, sibling_observation: row.sibling_observation });
    }
    forwardTruth.push(...[...truthIndex.values()]);
    consequence.push({
      event_id: baselineOutcome.event_id,
      divergence_receipt: flipReceipts.at(-1),
      V52B_BLIND_FIXED_TRAIL: { transitions: transitions(baselineForward, "V52B_BLIND_FIXED_TRAIL"), terminal_outcome: baselineOutcome },
      V52C_SIGHTED_FULL_POST_ONSET: { transitions: transitions(candidateForward, "V52C_SIGHTED_FULL_POST_ONSET"), terminal_outcome: candidateOutcome },
    });
  }
  combinedForward.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.machine.localeCompare(b.machine) || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
  forwardTruth.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.receipt.localeCompare(b.receipt));
  const summary = {
    source_commit: SOURCE_COMMIT,
    query: "V52B_COMPLETED_AND_V52C_NOT_COMPLETED_ON_SHARED_30",
    shared_population: 30,
    flip_games: flips.length,
    events: consequence.map((row) => ({ event_id: row.event_id, baseline_completed: row.V52B_BLIND_FIXED_TRAIL.terminal_outcome.completed_pair_observation, baseline_combined_entry_cents: row.V52B_BLIND_FIXED_TRAIL.terminal_outcome.combined_entry_cents_observation, candidate_completed: row.V52C_SIGHTED_FULL_POST_ONSET.terminal_outcome.completed_pair_observation, candidate_combined_entry_cents: row.V52C_SIGHTED_FULL_POST_ONSET.terminal_outcome.combined_entry_cents_observation, divergence_receipt: row.divergence_receipt.receipt, divergence_timestamp_epoch: row.divergence_receipt.timestamp_epoch, first_downstream_decision_difference_receipt: row.divergence_receipt.first_downstream_decision_difference?.receipt ?? null, first_downstream_decision_difference_timestamp_epoch: row.divergence_receipt.first_downstream_decision_difference?.timestamp_epoch ?? null })),
    interpretation: null,
    edits_or_replay: false,
  };
  fs.writeFileSync(path.join(output, "FLIP_QUERY_SUMMARY.json"), canonical(summary), { flag: "wx" });
  fs.writeFileSync(path.join(output, "FIRST_READ_DIVERGENCE.json"), canonical(flipReceipts), { flag: "wx" });
  fs.writeFileSync(path.join(output, "DOWNSTREAM_CONSEQUENCE_CHAIN.json"), canonical(consequence), { flag: "wx" });
  fs.writeFileSync(path.join(output, "INPUT_HASH_BINDING.json"), canonical({ source_commit: SOURCE_COMMIT, inputs: Object.fromEntries([baselineOutcomePath, candidateOutcomePath, baselineTracePath, candidateTracePath].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: shaFile(file), bytes: fs.statSync(file).size }])) }), { flag: "wx" });
  fs.writeFileSync(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ replay_invoked: false, policy_edits: false, behavioral_edits: false, scoring_edits: false, full_804_run: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, interpretation: false }), { flag: "wx" });
  await writeGzipRows(path.join(output, "BOTH_MACHINES_FORWARD_DECISION_TRACE.jsonl.gz"), combinedForward);
  await writeGzipRows(path.join(output, "FORWARD_TRUTH_PATH.jsonl.gz"), forwardTruth);
  const first = flipReceipts[0];
  fs.writeFileSync(path.join(output, "REPORT.md"), `# V52c Iteration 2 flip query - TRACE ONLY\n\nFlip games: ${flips.length}.\n\nFirst flip: \`${first.event_id}\`.\n\nFirst read divergence: \`${first.receipt}\` at epoch \`${first.timestamp_epoch}\`, T-minus scheduled \`${first.t_minus_scheduled_seconds}\`, T-minus actual bell \`${first.t_minus_actual_bell_seconds}\`.\n\nFirst downstream decision difference: \`${first.first_downstream_decision_difference?.receipt ?? "NONE_IN_SHARED_RECEIPTS"}\` at epoch \`${first.first_downstream_decision_difference?.timestamp_epoch ?? "null"}\`.\n\nThe frozen baseline completed at ${flips[0].combined_entry_cents_observation}; V52c did not complete. The attached rows contain both read payloads, the de-duplicated forward observation path, both complete post-divergence decision streams, and terminal outcomes. Interpretation is null. No replay or behavior edit occurred.\n`, { flag: "wx" });
  const namesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  if (compare) {
    const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || shaFile(path.join(compare, name)) !== shaFile(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  }
  fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical(determinism), { flag: "wx" });
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical(manifest(output)), { flag: "wx" });
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    fs.writeFileSync(path.join(compare, "ARTIFACT_HASH_MANIFEST.json"), canonical(manifest(compare)));
    ensure(shaFile(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === shaFile(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ");
  }
  process.stdout.write(canonical({ output, summary, first_divergence: first, rows: { baseline: baselineRows.length, candidate: candidateRows.length, combined_forward: combinedForward.length, forward_truth: forwardTruth.length }, determinism }));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
