#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const zlib = require("zlib");
const readline = require("readline");
const { Readable } = require("stream");
const { execFileSync } = require("child_process");

const GAP_COMMIT = "b581cbb58f660939ed9b0c2e88ddc42163dbab9a";
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const GAP_REL = ".claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807/V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz";
const V36_REL = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806";
const FULL_PARTS_REL = `${V36_REL}/FULL_DECISION_TRACE_PARTS.json`;
const STRICT_TRACE_REL = `${V36_REL}/STRICT_DECISION_TRACE_1608.json`;
const OUTPUT_SCHEMA = "v36-faller-side-mirror-anatomy-v1";

function argsOf(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 2) out[argv[i].replace(/^--/, "")] = argv[i + 1];
  for (const key of ["repo", "v36-root", "output"]) if (!out[key]) throw new Error(`missing --${key}`);
  return out;
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = stable(value[key]);
    return out;
  }
  return value;
}

function jsonText(value) {
  return `${JSON.stringify(stable(value), null, 2)}\n`;
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function fileRecord(file, label, displayPath) {
  return { label, path: displayPath, bytes: fs.statSync(file).size, sha256: sha256(file) };
}

function writeJson(file, value) {
  fs.writeFileSync(file, jsonText(value), "utf8");
}

function writeJsonlGz(file, rows) {
  const body = rows.map(row => `${JSON.stringify(stable(row))}\n`).join("");
  fs.writeFileSync(file, zlib.gzipSync(Buffer.from(body), { level: 9, mtime: 0 }));
}

function readJsonlGz(file) {
  return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
}

function gitHead(root) {
  return execFileSync("git", ["-C", root, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
}

function pct(n, d) {
  return d ? Number((100 * n / d).toFixed(3)) : null;
}

function spreadBucket(value) {
  if (!Number.isFinite(value)) return "UNKNOWN";
  if (value <= 0) return "LE_0";
  if (value === 1) return "EQ_1";
  if (value === 2) return "EQ_2";
  return "GE_3";
}

function capRoomBucket(cap, reach) {
  if (!Number.isFinite(cap)) return "UNCAPPED";
  const room = cap - reach;
  if (room < 0) return "BLOCKED_BELOW_REACH";
  if (room === 0) return "AT_REACH";
  if (room <= 3) return "HEADROOM_1_TO_3";
  return "HEADROOM_GE_4";
}

function compactTrace(row) {
  return {
    timestamp_epoch: row.timestamp_epoch,
    t_minus_scheduled_seconds: row.t_minus_scheduled_seconds,
    t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds,
    receipt: row.receipt,
    ordinal: row.ordinal,
    combined_state: row.combined_state,
    quote_path_state: row.quote_path && row.quote_path.state,
    pressure_state: row.pressure_state,
    observation: row.observation,
    pair_cap_cents: row.pair_cap_cents,
    order_before_cents: row.order_before_cents,
    order_after_cents: row.order_after_cents,
    decision_action: row.decision && row.decision.action,
    decision_target_cents: row.decision && row.decision.target_cents,
    decision_reason: row.decision && row.decision.reason,
  };
}

async function* concatenatedPartChunks(parts) {
  for (const file of parts) for await (const chunk of fs.createReadStream(file)) yield chunk;
}

async function readTrace(parts, requests, ownTargets) {
  const input = Readable.from(concatenatedPartChunks(parts));
  const gunzip = input.pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input: gunzip, crlfDelay: Infinity });
  let parsed = 0;
  for await (const line of lines) {
    if (!line) continue;
    parsed += 1;
    const row = JSON.parse(line);
    const reqs = requests.get(row.ticker);
    if (reqs) {
      for (const req of reqs) {
        if (row.timestamp_epoch <= req.target_epoch && (!req.snapshot || row.timestamp_epoch > req.snapshot.timestamp_epoch || (row.timestamp_epoch === req.snapshot.timestamp_epoch && row.ordinal >= req.snapshot.ordinal))) req.snapshot = compactTrace(row);
      }
    }
    const own = ownTargets.get(row.ticker);
    if (own && row.timestamp_epoch <= own.target_epoch) {
      const changed = row.order_before_cents !== row.order_after_cents;
      const first = own.walk_history.length === 0;
      if (first || changed || ["PLACE_REST", "REPRICE_REST", "TAKE"].includes(row.decision && row.decision.action)) own.walk_history.push(compactTrace(row));
    }
  }
  return parsed;
}

function snapshotCore(row) {
  if (!row) return null;
  return {
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    ordinal: row.ordinal,
    combined_state: row.combined_state,
    pressure_state: row.pressure_state,
    pair_cap_cents: row.pair_cap_cents,
    order_after_cents: row.order_after_cents,
    decision_action: row.decision_action,
    decision_reason: row.decision_reason,
  };
}

function taxonomy(row, own, history) {
  const issue = row.layer_bind;
  if (!issue) return { class: "CONTROL_CAPTURED_AT_OR_BETTER_THAN_REACH", reason: "V36 credited at-or-better than union reach" };
  if (issue.owner === "FILL_MODEL_SEAM_NOT_V36_ORGAN") return { class: "STRICT_FILL_SEAM_NOT_POLICY", reason: "rest was resident at-or-above reach but strict print-cross verification did not credit it" };
  if (issue.owner === "PAIR_CAP_ARITHMETIC" || (Number.isFinite(own && own.pair_cap_cents) && own.pair_cap_cents < row.union_reach_cents)) return { class: "CAP_BOUND", reason: `pair cap ${own && own.pair_cap_cents} sat below reach ${row.union_reach_cents}` };
  if (row.leg_direction !== "FALLING") return { class: "STATE_MISLABELED", reason: `V36 read FALLING at reach while the frozen reach-path direction was ${row.leg_direction}` };
  const price = row.v36_credited ? row.v36_entry_cents : own.order_after_cents;
  if (Number.isFinite(price) && price > row.union_reach_cents) return { class: "REST_TOO_SHALLOW", reason: `buy/rest ${price} remained ${price - row.union_reach_cents}c above bottom` };
  const downWalks = history.filter(x => Number.isFinite(x.order_before_cents) && Number.isFinite(x.order_after_cents) && x.order_after_cents < x.order_before_cents).length;
  return { class: "REST_WALKED_TOO_SLOW", reason: `FALLING path ended ${Number.isFinite(price) ? row.union_reach_cents - price : "unknown"}c below the reachable bottom after ${downWalks} downward walks` };
}

function signalValues(row) {
  const own = row.own_at_reach;
  const sibling = row.sibling_at_reach;
  const ownObs = own && own.observation || {};
  const siblingObs = sibling && sibling.observation || {};
  return {
    own_combined_state: own ? own.combined_state : "NO_SNAPSHOT",
    sibling_combined_state: sibling ? sibling.combined_state : "NO_SNAPSHOT",
    own_pressure_state: own ? own.pressure_state : "NO_SNAPSHOT",
    sibling_pressure_state: sibling ? sibling.pressure_state : "NO_SNAPSHOT",
    joint_pressure_read: `${own ? own.pressure_state : "NO_SNAPSHOT"}|${sibling ? sibling.pressure_state : "NO_SNAPSHOT"}`,
    own_spread_dwell: `${spreadBucket(ownObs.spread)}|${Number.isFinite(ownObs.ask_dwell_seconds) && ownObs.ask_dwell_seconds >= 10 ? "DWELL_GE_10" : "DWELL_LT_10_OR_UNKNOWN"}`,
    sibling_spread_dwell: `${spreadBucket(siblingObs.spread)}|${Number.isFinite(siblingObs.ask_dwell_seconds) && siblingObs.ask_dwell_seconds >= 10 ? "DWELL_GE_10" : "DWELL_LT_10_OR_UNKNOWN"}`,
    pair_cap_room: capRoomBucket(own && own.pair_cap_cents, row.reach_bottom_cents),
  };
}

function buildLift(rows, groupKeys) {
  const groupMap = new Map();
  for (const row of rows) {
    const group = groupKeys.map(k => row[k]).join("|");
    if (!groupMap.has(group)) groupMap.set(group, []);
    groupMap.get(group).push(row);
  }
  const out = [];
  for (const [group, members] of [...groupMap].sort((a, b) => a[0].localeCompare(b[0]))) {
    const baseCaptured = members.filter(r => r.captured_control).length;
    const baseRate = pct(baseCaptured, members.length);
    for (const dimension of Object.keys(members[0].signals).sort()) {
      const values = new Map();
      for (const row of members) {
        const value = row.signals[dimension];
        if (!values.has(value)) values.set(value, []);
        values.get(value).push(row);
      }
      for (const [value, subset] of [...values].sort((a, b) => String(a[0]).localeCompare(String(b[0])))) {
        const captured = subset.filter(r => r.captured_control).length;
        const captureRate = pct(captured, subset.length);
        out.push({
          group,
          group_keys: Object.fromEntries(groupKeys.map((k, i) => [k, group.split("|")[i]])),
          signal: dimension,
          value,
          n: subset.length,
          captured_n: captured,
          issue_n: subset.length - captured,
          capture_rate_pct: captureRate,
          same_group_control_n: members.length,
          same_group_control_capture_rate_pct: baseRate,
          lift_capture_percentage_points: Number((captureRate - baseRate).toFixed(3)),
          thin_n_lt_20: subset.length < 20,
        });
      }
    }
  }
  return out;
}

function summarizeTaxonomy(rows) {
  const map = new Map();
  for (const row of rows.filter(r => !r.captured_control)) {
    const key = `${row.category}|${row.price_region}|${row.miss_taxonomy.class}`;
    if (!map.has(key)) map.set(key, { category: row.category, price_region: row.price_region, miss_class: row.miss_taxonomy.class, sides: 0, measured_cents: 0, unpriced_sides: 0 });
    const value = map.get(key);
    value.sides += 1;
    if (Number.isFinite(row.measured_damage_cents)) value.measured_cents += row.measured_damage_cents;
    else value.unpriced_sides += 1;
  }
  return [...map.values()].sort((a, b) => a.category.localeCompare(b.category) || a.price_region.localeCompare(b.price_region) || a.miss_class.localeCompare(b.miss_class));
}

function writeManifest(output) {
  const files = fs.readdirSync(output).filter(x => x !== "ARTIFACT_HASH_MANIFEST.json").sort();
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { files: files.map(name => fileRecord(path.join(output, name), name, name)) });
}

function compareAndFinalize(primary, secondary) {
  const namesA = fs.readdirSync(primary).filter(x => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(x)).sort();
  const namesB = fs.readdirSync(secondary).filter(x => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(x)).sort();
  if (JSON.stringify(namesA) !== JSON.stringify(namesB)) throw new Error("determinism file census mismatch");
  const mismatches = namesA.filter(name => sha256(path.join(primary, name)) !== sha256(path.join(secondary, name)));
  if (mismatches.length) throw new Error(`determinism mismatch: ${mismatches.join(",")}`);
  const receipt = { clean_builds: 2, compared_files: namesA.length, byte_identical: true, mismatches: [] };
  for (const root of [primary, secondary]) {
    writeJson(path.join(root, "DETERMINISM_RECEIPT.json"), receipt);
    writeManifest(root);
  }
}

async function main() {
  const args = argsOf(process.argv);
  const repo = path.resolve(args.repo);
  const v36Root = path.resolve(args["v36-root"]);
  const output = path.resolve(args.output);
  if (fs.existsSync(output)) throw new Error(`output exists: ${output}`);
  if (gitHead(repo) !== GAP_COMMIT) throw new Error("gap parent HEAD mismatch");
  if (gitHead(v36Root) !== V36_COMMIT) throw new Error("V36 worktree HEAD mismatch");
  fs.mkdirSync(output, { recursive: true });

  const gapFile = path.join(repo, GAP_REL);
  const partsManifestFile = path.join(v36Root, FULL_PARTS_REL);
  const strictTraceFile = path.join(v36Root, STRICT_TRACE_REL);
  const partsManifest = JSON.parse(fs.readFileSync(partsManifestFile, "utf8"));
  const partFiles = partsManifest.parts.map(p => path.join(v36Root, V36_REL, p.name));
  for (let i = 0; i < partFiles.length; i++) {
    if (fs.statSync(partFiles[i]).size !== partsManifest.parts[i].bytes || sha256(partFiles[i]) !== partsManifest.parts[i].sha256) throw new Error(`V36 trace part mismatch: ${partFiles[i]}`);
  }

  const allLegs = readJsonlGz(gapFile);
  if (allLegs.length !== 1608) throw new Error(`gap leg conservation failed: ${allLegs.length}`);
  const byEvent = new Map();
  for (const row of allLegs) {
    if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []);
    byEvent.get(row.event_id).push(row);
  }
  const fallers = allLegs.filter(r => r.reach_moment_snapshot && r.reach_moment_snapshot.combined_state === "FALLING" && Number.isFinite(r.union_reach_cents));
  const issues = fallers.filter(r => r.layer_bind);
  if (fallers.length !== 511 || issues.length !== 399) throw new Error(`faller population changed: ${fallers.length}/${issues.length}`);

  const requests = new Map();
  const ownTargets = new Map();
  const addRequest = (ticker, req) => {
    if (!requests.has(ticker)) requests.set(ticker, []);
    requests.get(ticker).push(req);
  };
  for (const row of fallers) {
    const targetEpoch = row.union_first_evidence_timestamp_epoch;
    const ownReq = { key: `${row.ticker}|own`, target_epoch: targetEpoch, snapshot: null };
    const sibling = byEvent.get(row.event_id).find(x => x.ticker !== row.ticker);
    const siblingReq = { key: `${row.ticker}|sibling`, target_epoch: targetEpoch, snapshot: null };
    row._ownReq = ownReq;
    row._siblingReq = siblingReq;
    row._siblingTicker = sibling.ticker;
    addRequest(row.ticker, ownReq);
    addRequest(sibling.ticker, siblingReq);
    ownTargets.set(row.ticker, { target_epoch: targetEpoch, walk_history: [] });
  }
  const parsedRows = await readTrace(partFiles, requests, ownTargets);
  if (parsedRows !== 3631920) throw new Error(`full trace row conservation changed: ${parsedRows}`);

  const snapshotMismatches = [];
  const anatomy = fallers.map(row => {
    const own = row._ownReq.snapshot;
    const sibling = row._siblingReq.snapshot;
    const history = ownTargets.get(row.ticker).walk_history;
    const prior = row.reach_moment_snapshot;
    if (JSON.stringify(snapshotCore(own)) !== JSON.stringify(snapshotCore(prior))) snapshotMismatches.push(row.ticker);
    const tax = taxonomy(row, own, history);
    const reach = row.union_reach_cents;
    const rest = own && own.order_after_cents;
    const lastWalk = [...history].reverse().find(x => x.order_before_cents !== x.order_after_cents) || null;
    const result = {
      schema_version: OUTPUT_SCHEMA,
      event_id: row.event_id,
      ticker: row.ticker,
      leg_id: row.leg_id,
      category: row.category,
      price_region: row.price_region,
      bell_confidence: row.bell_confidence,
      reach_bottom_cents: reach,
      reach_sources: row.union_sources,
      reach_evidence_timestamp_epoch: row.union_first_evidence_timestamp_epoch,
      reach_trade_evidence: row.traded_at_level_evidence,
      reach_quote_evidence: row.quote_touch_evidence,
      own_at_reach: own,
      sibling_ticker: row._siblingTicker,
      sibling_at_reach: sibling,
      snapshot_age_seconds: own ? Number((row.union_first_evidence_timestamp_epoch - own.timestamp_epoch).toFixed(6)) : null,
      v36_entry_cents: row.v36_entry_cents,
      v36_fill_class: row.v36_fill_class,
      v36_credited: row.v36_credited,
      v36_rest_at_reach_cents: rest,
      rest_minus_reach_cents: Number.isFinite(rest) ? rest - reach : null,
      entry_minus_reach_cents: Number.isFinite(row.v36_entry_cents) ? row.v36_entry_cents - reach : null,
      measured_damage_cents: row.layer_bind && row.layer_bind.measured_damage_cents,
      original_gap_owner: row.layer_bind && row.layer_bind.owner,
      original_issue_kind: row.layer_bind && row.layer_bind.issue_kind,
      captured_control: !row.layer_bind,
      miss_taxonomy: tax,
      walk_summary: {
        recorded_order_transitions: history.length,
        downward_walks: history.filter(x => Number.isFinite(x.order_before_cents) && Number.isFinite(x.order_after_cents) && x.order_after_cents < x.order_before_cents).length,
        upward_walks: history.filter(x => Number.isFinite(x.order_before_cents) && Number.isFinite(x.order_after_cents) && x.order_after_cents > x.order_before_cents).length,
        first_rest_cents: history.length ? history[0].order_after_cents : null,
        last_walk_before_reach: lastWalk,
      },
    };
    result.signals = signalValues(result);
    return result;
  }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  if (snapshotMismatches.length) throw new Error(`reach snapshot reconstruction mismatch: ${snapshotMismatches.slice(0, 5).join(",")}`);

  const issueRows = anatomy.filter(r => !r.captured_control);
  const walkRows = issueRows.map(row => ({ event_id: row.event_id, ticker: row.ticker, leg_id: row.leg_id, reach_bottom_cents: row.reach_bottom_cents, reach_evidence_timestamp_epoch: row.reach_evidence_timestamp_epoch, walk_history: ownTargets.get(row.ticker).walk_history }));
  const named = {};
  for (const token of ["GANJAN", "KRALOR", "WESPAA"]) {
    const rows = anatomy.filter(r => r.event_id.includes(token));
    named[token] = { rows, finding: rows.length ? "FALLER_SIDE_FOUND" : "NO_FALLER_SIDE_WITH_UNION_REACH" };
  }
  const ownerMap = {};
  for (const row of issueRows) {
    const key = `${row.original_gap_owner}|${row.original_issue_kind}`;
    if (!ownerMap[key]) ownerMap[key] = { sides: 0, measured_cents: 0 };
    ownerMap[key].sides += 1;
    ownerMap[key].measured_cents += row.measured_damage_cents || 0;
  }
  const taxonomyRows = summarizeTaxonomy(anatomy);
  const summary = {
    schema_version: OUTPUT_SCHEMA,
    population: {
      all_legs: 1608,
      faller_sides_with_union_reach: anatomy.length,
      issue_sides: issueRows.length,
      captured_controls: anatomy.filter(r => r.captured_control).length,
      issue_owner_x_kind: ownerMap,
      measured_issue_cents: issueRows.reduce((s, r) => s + (r.measured_damage_cents || 0), 0),
    },
    taxonomy_rows: taxonomyRows,
    taxonomy_conservation: { issue_sides: issueRows.length, classified_sides: taxonomyRows.reduce((s, r) => s + r.sides, 0), pass: issueRows.length === taxonomyRows.reduce((s, r) => s + r.sides, 0) },
  };
  const lift = {
    definition: "capture lift percentage points = P(V36 credited at-or-better than union reach | signal) minus the same category or category x price-region faller control rate; descriptive only, no fit and no policy authority",
    category_rows: buildLift(anatomy, ["category"]),
    category_x_price_region_rows: buildLift(anatomy, ["category", "price_region"]),
  };
  const slateBinding = {
    status: "EXPLICITLY_BOUND_FROM_OPERATOR_FIELDS",
    note: "No separately committed riser-exam schema was found on the fetched analysis ref. The candidate slate is therefore frozen exactly to the named fields rather than inferred.",
    fields: ["own combined state", "other expression combined state", "own pressure state", "other pressure state", "joint pressure read", "own spread+dwell", "other spread+dwell", "pair-cap room"],
    control: "all 511 sides V36 read as FALLING at the union-reach moment; captured control means V36 credited at-or-better than reach",
  };
  const traceReceipt = { full_trace_rows_parsed: parsedRows, reach_snapshot_targets: fallers.length, sibling_snapshot_targets: fallers.length, snapshot_reconstruction_mismatches: [], full_trace_parts: partFiles.length };
  const forbidden = { policy_invocations: 0, replay_invocations: 0, scoring_changes: 0, holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, exit_accesses: 0, deployment_accesses: 0, mutations: 0, scope: "READ_ONLY_FROZEN_DEV_804_GAP_AND_V36_TRACE_ARTIFACTS" };

  writeJsonlGz(path.join(output, "FALLER_SIDE_ANATOMY_511.jsonl.gz"), anatomy);
  writeJsonlGz(path.join(output, "FALLER_ISSUE_ANATOMY_399.jsonl.gz"), issueRows);
  writeJsonlGz(path.join(output, "FALLER_REST_WALK_HISTORY_399.jsonl.gz"), walkRows);
  writeJson(path.join(output, "FALLER_POPULATION_AND_TAXONOMY.json"), summary);
  writeJson(path.join(output, "CANDIDATE_SIGNAL_LIFT.json"), lift);
  writeJson(path.join(output, "CANDIDATE_SLATE_BINDING.json"), slateBinding);
  writeJson(path.join(output, "NAMED_GAMES.json"), named);
  writeJson(path.join(output, "TRACE_RECONSTRUCTION_RECEIPT.json"), traceReceipt);
  writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), forbidden);
  writeJson(path.join(output, "CONTROL_BINDING.json"), { gap_commit: GAP_COMMIT, v36_commit: V36_COMMIT, gap_ledger: GAP_REL, v36_full_trace_manifest: FULL_PARTS_REL, schema_version: OUTPUT_SCHEMA });
  writeJson(path.join(output, "SOURCE_HASH_MANIFEST.json"), {
    commits: { gap: GAP_COMMIT, v36: V36_COMMIT },
    files: [
      fileRecord(gapFile, "V36_GAP_TO_REACH_LEG_LEDGER", `${GAP_COMMIT}:${GAP_REL}`),
      fileRecord(partsManifestFile, "V36_FULL_TRACE_PARTS_MANIFEST", `${V36_COMMIT}:${FULL_PARTS_REL}`),
      fileRecord(strictTraceFile, "V36_STRICT_DECISION_TRACE_1608", `${V36_COMMIT}:${STRICT_TRACE_REL}`),
      ...partFiles.map((file, i) => fileRecord(file, `V36_FULL_TRACE_PART_${i}`, `${V36_COMMIT}:${V36_REL}/${path.basename(file)}`)),
      fileRecord(path.join(repo, "arb-executor/analysis/build_v36_faller_side_mirror_anatomy.js"), "BUILDER", "arb-executor/analysis/build_v36_faller_side_mirror_anatomy.js"),
    ],
  });

  const taxTotals = {};
  for (const row of issueRows) {
    const key = row.miss_taxonomy.class;
    if (!taxTotals[key]) taxTotals[key] = { sides: 0, measured_cents: 0 };
    taxTotals[key].sides += 1;
    taxTotals[key].measured_cents += row.measured_damage_cents || 0;
  }
  const report = [
    "# V36 faller-side mirror anatomy",
    "",
    `Read-only anatomy of frozen V36 at ${V36_COMMIT} against the b581cbb union-reach gap ledger. No policy or replay was invoked.`,
    "",
    `Population: ${anatomy.length} faller sides with reach = ${issueRows.length} issue sides + ${anatomy.length - issueRows.length} captured controls. Measured issue cents: ${summary.population.measured_issue_cents}.`,
    "",
    "## Miss taxonomy",
    "",
    "| class | sides | measured cents |",
    "|---|---:|---:|",
    ...Object.entries(taxTotals).sort((a, b) => b[1].measured_cents - a[1].measured_cents).map(([key, value]) => `| ${key} | ${value.sides} | ${value.measured_cents} |`),
    "",
    "Signal lift is descriptive capture-rate lift against the complete faller control within category and category x price-region. Thin n<20 cells remain marked thin and are never pooled.",
    "",
    "Named rows for GANJAN, KRALOR, and WESPAA are frozen in NAMED_GAMES.json. Every issue side has its exact reach evidence, own and sibling snapshot, both clocks, pressure reads, spread/dwell, cap room, action receipt, and full rest-walk history.",
  ].join("\n") + "\n";
  fs.writeFileSync(path.join(output, "REPORT.md"), report, "utf8");
  writeJson(path.join(output, "DETERMINISM_RECEIPT.json"), { clean_builds: 2, status: "PENDING_SECOND_CLEAN_BUILD" });
  writeManifest(output);

  if (args["compare-to"]) compareAndFinalize(path.resolve(args["compare-to"]), output);
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
