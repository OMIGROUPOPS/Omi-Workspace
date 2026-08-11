#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const REACH_COMMIT = "57daf3c15ad618098a810566d24127df8f17f3f9";
const GAP_COMMIT = "b581cbb58f660939ed9b0c2e88ddc42163dbab9a";
const DIVOT_COMMIT = "d1ac94973252e2f8c28ba32374c29ff7bd605a7e";
const COUNTERFACTUAL_COMMIT = "2b45d14688a0ec05d14ab4975759f1a986398da5";
const FALLER_ANATOMY_COMMIT = "c3961e2c2134aac7ea977d7ab4bb65bf7a263cc4";
const CAUSAL_REACH_COMMIT = "d3db740f143646614bc10778c0b4e27fa519dcd8";
const RISER_FRONTIER_COMMIT = "084df12553928677869bd2857516caa3f0490416";
const LEVEL_POLICY_COMMIT = "cca7c6c1554344711e2ddb32f3d3e2175c44711e";
const V41_COMMIT = "96d33316b0c0020b46b71569fcdbadeaa97a64e3";
const DEEP_GAP_CENSUS_COMMIT = "645e035bce12a4dcaf4cb7f10a3767fa898652a0";
const FULL_BOOK_PNL_COMMIT = "a30f5ccdf0c4233b30bf4017af48707f0db8ff1f";
const ARM_FIRST_EVIDENCE_COMMIT = "9ddfe8c6fec868cf07f92c54c878fe9208253451";
const LOOSEN_ONE_CENT_COMMIT = "52275c9d63be90eb16febd1d2cb10db00bd829c7";
const V43_COMMIT = "01a58334e90acffd4bb0fb17b6ceed17c4f51bbd";
const V45_COMMIT = "3bda0a5476c7fc845891928795f709feff8caabf";
const V43_RECALIBRATION_COMMIT = "b503e4edc2184e8958c97980c2e1769a077bfdd9";
const V43_RESIDUAL_DOCKET_COMMIT = "6934634efcc32cdb26dbe927ce8398a66aa50e92";
const STRICT_ASK_FOOTPRINT_COMMIT = "aa884cc5a1f9465a219d0913dbc237a33bc3a063";
const SURECH_RENDER_COMMIT = "8877c2d519c26b4e54f283ebebcee4933113d100";
const V47_COMMIT = "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34";
const TRADES_TRUTH_RECUT_COMMIT = "e995c81b39174cc67bffcf568390b8d069e5fd8a";
const STANDABILITY_V2_COMMIT = "fe4747cd915830dc16f41c6bbec5e0ca1c14d99c";
const HERKAZ_EXEMPLAR_COMMIT = "b9673399c36fb9e5c14940610e3bf43fd2614c19";
const V36_PACKAGE = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806";
const GAP_PACKAGE = ".claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807";
const OUT_REL = ".claude/window1_live_v4_replay/v38_maker_only_machine_20260807";
const EXPECTED_REACH = { events: 804, legs: 1608, reachable_games: 785, no_reach_games: 19, under_par_games: 637, locked_cents: 5253, union_legs: 1570 };

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const variant = arg("--variant", "v38");
const isV39 = variant === "v39";
const isV40 = variant === "v40";
const isV41 = variant === "v41";
const isV42 = variant === "v42";
const isV43 = variant === "v43";
const isV45 = variant === "v45";
const isV46 = variant === "v46";
const isV47 = variant === "v47";
const isV48 = variant === "v48";
const isV49 = variant === "v49";
const isTradeTruthVariant = isV48 || isV49;
const isV45Family = isV45 || isV46 || isV47 || isTradeTruthVariant;
const isAttribution = isV43 || isV45Family;
const hasDeepGap = isV42 || isAttribution;
const isMaker41 = isV41 || hasDeepGap;
const isPlacementStack = isV39 || isV40 || isMaker41;
if (!["v38", "v39", "v40", "v41", "v42", "v43", "v45", "v46", "v47", "v48", "v49"].includes(variant)) throw new Error(`unknown variant ${variant}`);
const policy = require(isV49 ? "./window1_v49_evidenced_level_standing.js" : isV48 ? "./window1_v48_trades_as_truth.js" : isV47 ? "./window1_v47_same_tick_arm.js" : isV46 ? "./window1_v46_pair_gated_gap_credit.js" : isV45 ? "./window1_v45_guard_release_sibling_credit.js" : isV43 ? "./window1_v43_composed_machine.js" : isV42 ? "./window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "./window1_v41_maker_machine.js" : isV40 ? "./window1_v40_incumbent_direction_placement_stack.js" : isV39 ? "./window1_v39_corrected_placement_stack.js" : "./window1_v38_maker_only_machine.js");
const v43Policy = isV45Family ? require("./window1_v43_composed_machine.js") : null;
const repo = path.resolve(arg("--repo", "."));
const v36Root = path.resolve(arg("--v36-root", "C:/tmp/omi-v36-frozen-bfde"));
const reachRoot = path.resolve(arg("--reach-root", "C:/tmp/omi-reach-57daf3"));
const gapRoot = path.resolve(arg("--gap-root", isPlacementStack ? "C:/tmp/omi-v36-gap-reach-20260807" : repo));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, isV49 ? ".claude/window1_live_v4_replay/v49_evidenced_level_standing_20260810" : isV48 ? ".claude/window1_live_v4_replay/v48_trades_as_truth_20260810" : isV47 ? ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810" : isV46 ? ".claude/window1_live_v4_replay/v46_pair_gated_gap_credit_20260810" : isV45 ? ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809" : isV43 ? ".claude/window1_live_v4_replay/v43_composed_machine_20260809" : isV42 ? ".claude/window1_live_v4_replay/v42_deep_gap_feasibility_guard_20260809" : isV41 ? ".claude/window1_live_v4_replay/v41_maker_machine_20260808" : isV40 ? ".claude/window1_live_v4_replay/v40_incumbent_direction_placement_stack_20260808" : isV39 ? ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807" : OUT_REL)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function writeManifest(dir) {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
}
function gzipRows(rows) {
  const lines = rows.map((row) => JSON.stringify(row)).join("\n");
  return zlib.gzipSync(Buffer.from(`${lines}${lines ? "\n" : ""}`), { level: 9, mtime: 0 });
}
async function writeGzipRowsFile(file, rows) {
  async function* encode() { for await (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
function readRows(file) {
  const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function readRowsBytes(bytes) {
  const text = zlib.gunzipSync(bytes).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function gitHead(root) {
  return require("child_process").execFileSync("git", ["-c", `safe.directory=${path.resolve(root).replaceAll("\\", "/")}`, "rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim();
}
function gitShow(commit, relativePath) {
  return require("child_process").execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 });
}
function safeOutput(dir) {
  const resolved = path.resolve(dir);
  ensure(path.basename(resolved).includes(isV49 ? "v49" : isV48 ? "v48" : isV47 ? "v47" : isV46 ? "v46" : isV45 ? "v45" : isV43 ? "v43" : isV42 ? "v42" : isV41 ? "v41" : isV40 ? "v40" : isV39 ? "v39" : "v38"), `unsafe output ${resolved}`);
  ensure(resolved !== repo && resolved !== path.parse(resolved).root, `unsafe output ${resolved}`);
  fs.rmSync(resolved, { recursive: true, force: true });
  fs.mkdirSync(resolved, { recursive: true });
}
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function percentile(values, q) {
  const x = values.filter(Number.isFinite).sort((a, b) => a - b);
  return x.length ? x[Math.max(0, Math.ceil(q * x.length) - 1)] : null;
}
function distribution(values) {
  const x = values.filter(Number.isFinite);
  return { n: x.length, null_n: values.length - x.length, sum: x.reduce((a, b) => a + b, 0), min: x.length ? Math.min(...x) : null, p25: percentile(x, .25), median: percentile(x, .5), p75: percentile(x, .75), p90: percentile(x, .9), max: x.length ? Math.max(...x) : null };
}
function countBy(rows, fn) {
  const out = {};
  for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; }
  return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}
function clockFields(ts, base) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: Number.isFinite(base.scheduled) ? base.scheduled - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(base.actual_bell) ? base.actual_bell - ts : null,
    t_minus_pre_match_boundary_seconds: base.right - ts,
  };
}
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = +m[4]; if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}

function loadTape(ticker) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing tape ${ticker}`);
  const bytes = fs.readFileSync(file);
  const parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  const ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
  const out = [];
  for (let n = 0; n < parsed.rows.length; n += 1) {
    const values = parsed.rows[n], ts = parseEt(values[ix.ts_et]);
    if (!Number.isFinite(ts)) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(values[ix[`bid_${level}`]]), bs = positive(values[ix[`bid_${level}_sz`]]);
      const ap = integer(values[ix[`ask_${level}`]]), as = positive(values[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const bidDepth = bids.reduce((sum, x) => sum + x[1], 0), askDepth = asks.reduce((sum, x) => sum + x[1], 0);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bidDepth, ask_depth_5: askDepth, depth_ratio: bidDepth / (bidDepth + askDepth), last_trade: integer(values[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, askSince = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; askSince = row.ts; } row.ask_dwell_seconds = row.ts - askSince; }
  return { rows: out, sha256: shaBytes(bytes), bytes: bytes.length };
}

async function loadPrints(tickerBounds) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private prints");
  const hash = crypto.createHash("sha256"), byTicker = new Map([...tickerBounds].map(([ticker]) => [ticker, []]));
  const seen = new Map([...tickerBounds].map(([ticker]) => [ticker, new Set()]));
  let rawRows = 0, admitted = 0, duplicates = 0;
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => hash.update(chunk));
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    rawRows += 1;
    const row = JSON.parse(line), bound = tickerBounds.get(row.ticker);
    if (!bound || !row.true_print) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicates += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    admitted += 1;
    byTicker.get(row.ticker).push({ kind: "PRINT", ticker: row.ticker, ts, ordinal: admitted, receipt: row.receipt_id, price: integer(row.price_cents), size: positive(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side, trade_id: row.trade_id });
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { byTicker, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rawRows, admitted_unique_v36_window_prints: admitted, duplicate_trade_id_rows_rejected: duplicates } };
}

function armSibling(sibling, filled, row, actions, base) {
  sibling.pair_cap_cents = 99 - filled.entry_cents;
  actions.push({ kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, first_fill_cents: filled.entry_cents, pair_cap_cents: sibling.pair_cap_cents });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    const prior = sibling.active_order.target_cents;
    if (policy.lawfulCent(sibling.pair_cap_cents)) {
      sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: "PAIR_CAP" };
      actions.push({ kind: "PAIR_CAP_REPRICE", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior, target_cents: sibling.pair_cap_cents });
    } else {
      sibling.active_order = null;
      actions.push({ kind: "PAIR_CAP_CANCEL", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior });
    }
  }
}

function fillLeg(leg, sibling, row, fillClass, actions, base, normalizedClauses = {}) {
  leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = fillClass; leg.fill_source_state = leg.active_order.source_state; leg.terminal_reason = fillClass;
  if (leg.active_order.gap_credit) {
    leg.gap_credit_fill = { ...leg.active_order.gap_credit, fill_timestamp_epoch: row.ts, fill_receipt: row.receipt, fill_class: fillClass, entry_cents: leg.entry_cents };
  }
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: fillClass, fill_source_state: leg.fill_source_state, evidence: row.kind === "PRINT" ? { kind: "PRINT", trade_id: row.trade_id, price_cents: row.price, size: row.size, taker_side: row.taker_side, taker_book_side: row.taker_book_side } : { kind: "QUOTE_TOUCH", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
  releaseV45GuardAtSiblingCredit(sibling, leg, row, actions, base, normalizedClauses);
}

function takeLeg(leg, sibling, row, actions, base, decision) {
  leg.credited = true; leg.entry_cents = row.ask; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = "PROVEN_TAKER_V36_MATURE_EVIDENCE_FLOOR"; leg.fill_source_state = leg.last_combined_state; leg.terminal_reason = leg.fill_class;
  leg.active_order = null;
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_source_state: leg.fill_source_state, decision_reason: decision.reason, evidence: { kind: "DISPLAYED_ASK_TAKE", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
}

function receiptObservation(row) {
  return { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5 };
}

function noteV42Guard(leg, decision, row, base, actions, triggerLegIdentity) {
  if (!decision.guard) return;
  leg.deep_gap_guard_evaluations += 1;
  const withheld = Boolean(decision.guard.withheld);
  if (withheld) leg.deep_gap_withheld_evaluations += 1;
  if (withheld && !leg.deep_gap_withhold_active) {
    leg.deep_gap_withhold_episodes += 1;
    leg.deep_gap_first_withhold ||= { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
    actions.push({ kind: "DEEP_GAP_WITHHOLD_START", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_action: decision.v41_decision?.action ?? null, v41_target_cents: decision.v41_decision?.target_cents ?? null });
  }
  if (!withheld && leg.deep_gap_withhold_active) {
    leg.deep_gap_lifts += 1;
    leg.deep_gap_last_lift = { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
    actions.push({ kind: "DEEP_GAP_WITHHOLD_LIFT", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_action: decision.v41_decision?.action ?? null, v41_target_cents: decision.v41_decision?.target_cents ?? null });
  }
  leg.deep_gap_withhold_active = withheld;
  if (withheld) leg.deep_gap_last_withhold = { ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, guard: decision.guard, v41_decision: decision.v41_decision };
}

function applyRestDecision(leg, sibling, row, decision, combinedState, detail, actions, base, triggerLegIdentity) {
  if (["PLACE_REST", "REPRICE_REST"].includes(decision.action)) {
    leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: combinedState, ...(decision.gap_credit?.authorized ? { gap_credit: { ...decision.gap_credit, event_id: base.event_id, leg_identity: leg.leg_identity, authorization_timestamp_epoch: row.ts, authorization_receipt: row.receipt } } : {}), ...(decision.evidenced_standing ? { evidenced_standing: decision.evidenced_standing } : {}) };
    leg.first_action ||= detail;
    actions.push({ kind: decision.gap_credit?.authorized ? "GAP_CREDIT_REPRICE_DOWN" : decision.action, event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, target_cents: decision.target_cents, state: combinedState, reason: decision.reason, pulse_floor_cents: detail?.pulse_floor?.floor_cents ?? null, guard: decision.guard ?? null, gap_credit: decision.gap_credit ?? null, evidenced_standing: decision.evidenced_standing ?? null });
  } else if (decision.action === "CANCEL_REST") {
    leg.active_order = null;
    actions.push({ kind: "CANCEL_REST", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, trigger_leg_identity: triggerLegIdentity, reason: decision.reason, guard: decision.guard ?? null });
  } else if (decision.action === "TAKE") {
    leg.first_action ||= detail;
    takeLeg(leg, sibling, row, actions, base, decision);
  }
}

function releaseV45GuardAtSiblingCredit(withheldLeg, creditedLeg, row, actions, base, normalizedClauses) {
  if (!normalizedClauses.release_guard_on_sibling_credit || !withheldLeg.deep_gap_withhold_active || withheldLeg.credited) return;
  const before = withheldLeg.active_order?.target_cents ?? null;
  const ownInputs = withheldLeg.last_placement_inputs;
  withheldLeg.post_credit_guard_release_attempts += 1;
  if (!ownInputs) {
    withheldLeg.post_credit_guard_release_no_book += 1;
    actions.push({ kind: "POST_CREDIT_GUARD_RELEASE_NO_OWN_BOOK", event_id: base.event_id, leg_identity: withheldLeg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: creditedLeg.leg_identity, sibling_entry_cents: creditedLeg.entry_cents, fixed_pair_cap_cents: withheldLeg.pair_cap_cents });
    withheldLeg.deep_gap_withhold_active = false;
    return;
  }
  const inputs = { ...ownInputs, activeTarget: before, pairCap: withheldLeg.pair_cap_cents, siblingBestAsk: creditedLeg.prior_book?.ask ?? ownInputs.siblingBestAsk, siblingCredited: true, clauses: normalizedClauses };
  const decision = policy.decide(inputs);
  ensure(decision.guard_authority_terminated === true && decision.guard === null, `V45 guard authority survived sibling credit ${withheldLeg.leg_identity}`);
  withheldLeg.deep_gap_withhold_active = false;
  withheldLeg.deep_gap_lifts += 1;
  withheldLeg.post_credit_guard_releases += 1;
  const release = { ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: creditedLeg.leg_identity, sibling_entry_cents: creditedLeg.entry_cents, fixed_pair_cap_cents: withheldLeg.pair_cap_cents, prior_withhold: withheldLeg.deep_gap_last_withhold, own_book_receipt: ownInputs.book.receipt, own_book: receiptObservation(ownInputs.book), order_before_cents: before, decision, order_after_cents: null };
  actions.push({ kind: "POST_CREDIT_GUARD_AUTHORITY_TERMINATED", event_id: base.event_id, leg_identity: withheldLeg.leg_identity, ...release });
  const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(ownInputs.book), sibling_observation: creditedLeg.prior_book ? receiptObservation(creditedLeg.prior_book) : null, combined_state: ownInputs.state, pulse_floor: { floor_cents: ownInputs.pulseFloor }, pair_cap_cents: withheldLeg.pair_cap_cents, order_before_cents: before, decision, post_credit_guard_release: true, order_after_cents: null };
  applyRestDecision(withheldLeg, creditedLeg, row, decision, ownInputs.state, detail, actions, base, creditedLeg.leg_identity);
  detail.order_after_cents = withheldLeg.active_order?.target_cents ?? null;
  release.order_after_cents = detail.order_after_cents;
  withheldLeg.post_credit_guard_release = release;
  withheldLeg.last_decision = detail;
}

function reevaluateV42WithSiblingBook(withheldLeg, triggeringLeg, row, actions, base) {
  if (row.kind !== "BOOK" || !withheldLeg.deep_gap_withhold_active || !withheldLeg.last_placement_inputs || withheldLeg.credited) return;
  const before = withheldLeg.active_order?.target_cents ?? null;
  const inputs = { ...withheldLeg.last_placement_inputs, activeTarget: before, pairCap: withheldLeg.pair_cap_cents, siblingBestAsk: row.ask };
  const decision = policy.decide(inputs);
  noteV42Guard(withheldLeg, decision, row, base, actions, triggeringLeg.leg_identity);
  if (decision.guard?.withheld) return;
  const ownBook = withheldLeg.last_placement_inputs.book;
  const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(ownBook), sibling_observation: receiptObservation(row), combined_state: withheldLeg.last_placement_inputs.state, pulse_floor: { floor_cents: withheldLeg.last_placement_inputs.pulseFloor }, pair_cap_cents: withheldLeg.pair_cap_cents, order_before_cents: before, decision, re_evaluated_on_sibling_receipt: true, order_after_cents: null };
  applyRestDecision(withheldLeg, triggeringLeg, row, decision, withheldLeg.last_placement_inputs.state, detail, actions, base, triggeringLeg.leg_identity);
  detail.order_after_cents = withheldLeg.active_order?.target_cents ?? null;
  withheldLeg.last_decision = detail;
}

function simulate(base, tapes, prints, mode, clauses = {}) {
  const ids = Object.keys(base.legs).sort(), actions = [], joinQualifications = [];
  const normalizedClauses = policy.normalizedClauses ? policy.normalizedClauses(clauses) : (isV42 ? { arm_at_first_evidence: false, deep_gap_guard: true, loosen_one_cent: false } : {});
  const event = { event_id: base.event_id, category: base.category, starting_price_split: base.starting_price_split, bell_confidence: base.bell_confidence, edge_source_field: base.edge_source_field, w1_left_epoch: base.left, w1_right_epoch: base.right, mode, clauses: normalizedClauses, legs: {} };
  for (const id of ids) {
    const meta = base.legs[id], reach = meta.reach;
    event.legs[id] = { ...meta, reach: undefined, event_id: base.event_id, credited: false, entry_cents: null, fill_class: null, fill_source_state: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, directional: [], pulse_visits: [], recent_trade_rows: [], prior_true_trade_low_cents: null, prior_true_trade_low_receipt: null, exact_bid_first_receipt: new Map(), evidenced_standing_level_cents: null, evidenced_standing_authority: null, evidenced_standing_decisions: 0, evidenced_standing_first: null, evidenced_standing_last: null, pulse_floor_cents: null, pulse_floor_ever: false, current_bid_level: null, current_bid_since: null, current_bid_last_trade_hit: false, current_bid_last_trade_hit_receipt: null, book_last_trade_hits_by_level: new Map(), seller_hits_by_level: new Map(), persistent_join_level: null, persistent_join_receipt: null, persistent_join_evidence_receipt: null, persistent_join_timestamp_epoch: null, post_join_book_last_trade_receipts: 0, post_join_certified_seller_hits_at_level: 0, running_seller_hit_low: null, running_qualified_ask_low: null, running_qualified_ask_low_unabsorbed: false, running_qualified_ask_low_reformed_nonfalling: false, latest_new_low_evidence_ts: null, downward_evidence_rows: [], last_combined_state: "SETTLED", classifier_rows: 0, classifier_state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, classifier_opposed_rows: 0, classifier_agreement_rows: 0, decision_count: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, last_placement_inputs: null, deep_gap_guard_evaluations: 0, deep_gap_withheld_evaluations: 0, deep_gap_withhold_episodes: 0, deep_gap_lifts: 0, deep_gap_withhold_active: false, deep_gap_first_withhold: null, deep_gap_last_withhold: null, deep_gap_last_lift: null, post_credit_guard_release_attempts: 0, post_credit_guard_releases: 0, post_credit_guard_release_no_book: 0, post_credit_guard_reapplication_prevented_receipts: 0, post_credit_guard_release: null, gap_credit_eligible_receipts: 0, gap_credit_authorized_walks: 0, gap_credit_sibling_uncredited_refusals: 0, gap_credit_no_lawful_reprice: 0, gap_credit_first: null, gap_credit_last: null, gap_credit_fill: null, union_reach_cents: reach.union_reach_cents, union_first_evidence_timestamp_epoch: reach.union_first_evidence_timestamp_epoch, reach_sources: reach.union_sources, reach_inside_v36_edge: reach.union_first_evidence_timestamp_epoch >= base.left && reach.union_first_evidence_timestamp_epoch <= base.right, reach_snapshot: null };
  }
  const timeline = [];
  for (const id of ids) {
    for (const row of tapes.get(id)) timeline.push({ ...row, leg_id: id });
    for (const row of prints.get(id)) timeline.push({ ...row, leg_id: id });
  }
  timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  for (const row of timeline) {
    if (row.ts < base.left || row.ts > base.right) continue;
    const leg = event.legs[row.leg_id], sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if ((isV40 || isMaker41) && Number.isFinite(leg.persistent_join_timestamp_epoch) && row.ts > leg.persistent_join_timestamp_epoch) {
      if (row.kind === "PRINT" && row.taker_side === "no" && row.price === leg.persistent_join_level) leg.post_join_certified_seller_hits_at_level += 1;
      if (row.kind === "BOOK" && row.bid === leg.persistent_join_level && row.last_trade === leg.persistent_join_level) leg.post_join_book_last_trade_receipts += 1;
    }
    if (leg.credited) {
      if (normalizedClauses.deep_gap_guard && row.kind === "BOOK") {
        leg.prior_book = row;
        reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
      }
      continue;
    }
    if (row.kind === "PRINT") {
      leg.recent_trade_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, receipt: row.receipt, trade_id: row.trade_id });
      leg.recent_trade_rows = leg.recent_trade_rows.filter((print) => print.ts <= row.ts && print.ts >= row.ts - policy.LOOKBACK_SECONDS);
      if (mode === "STRICT_PRINT_CROSS" && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "STRICT_PRINT_CROSS_SELLER_AGGRESSED_SIZE_FIVE", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_TRADES_AS_TRUTH" && policy.tradeTruthCredit(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_UNION_REACH" && leg.active_order && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_PRINT_CROSS", actions, base, normalizedClauses); continue;
      }
      if (mode === "MARKET_UNION_REACH" && policy.tradedAtLevel(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_TRADED_AT_LEVEL", actions, base, normalizedClauses); continue;
      }
      if (leg.prior_true_trade_low_cents === null || row.price < leg.prior_true_trade_low_cents) {
        leg.prior_true_trade_low_cents = row.price;
        leg.prior_true_trade_low_receipt = row.receipt;
      }
      if (row.taker_side === "no") {
        const sellerHitMadeNewLow = leg.running_seller_hit_low === null || row.price < leg.running_seller_hit_low;
        leg.seller_hits_by_level.set(row.price, (leg.seller_hits_by_level.get(row.price) || 0) + 1);
        leg.running_seller_hit_low = leg.running_seller_hit_low === null ? row.price : Math.min(leg.running_seller_hit_low, row.price);
        leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, kind: "SELLER_HIT_TRUE_PRINT", receipt: row.receipt });
        if (sellerHitMadeNewLow) leg.latest_new_low_evidence_ts = row.ts;
      }
      if (row.taker_side === "no" || row.taker_side === "yes") leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt }];
      continue;
    }
    if (mode === "MARKET_UNION_REACH" && policy.quoteTouch(leg.active_order, row)) {
      fillLeg(leg, sibling, row, "MARKET_REACH_QUOTE_TOUCH_10S_SIZE_FIVE", actions, base, normalizedClauses);
      if (normalizedClauses.deep_gap_guard) { leg.prior_book = row; reevaluateV42WithSiblingBook(sibling, leg, row, actions, base); }
      continue;
    }
    leg.recent_trade_rows = leg.recent_trade_rows.filter((print) => print.ts <= row.ts && print.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const recentTradeLow = leg.recent_trade_rows.length ? Math.min(...leg.recent_trade_rows.map((print) => print.price)) : null;
    const prior = leg.prior_book, newLowAsk = Boolean(prior && row.ask < prior.ask), newHighBid = Boolean(prior && row.bid > prior.bid);
    const priorExactBidEvidence = leg.exact_bid_first_receipt.get(row.bid) ?? null;
    if (leg.current_bid_level !== row.bid) {
      leg.current_bid_level = row.bid;
      leg.current_bid_since = row.ts;
      leg.current_bid_last_trade_hit = false;
      leg.current_bid_last_trade_hit_receipt = null;
    }
    if (!leg.exact_bid_first_receipt.has(row.bid)) leg.exact_bid_first_receipt.set(row.bid, { level_cents: row.bid, receipt: row.receipt, timestamp_epoch: row.ts });
    if (row.last_trade === row.bid) {
      leg.current_bid_last_trade_hit = true;
      leg.current_bid_last_trade_hit_receipt ||= row.receipt;
      leg.book_last_trade_hits_by_level.set(row.bid, (leg.book_last_trade_hits_by_level.get(row.bid) || 0) + 1);
    }
    if (!prior || row.ask !== prior.ask) leg.pulse_visits.push({ ts: row.ts, ordinal: row.ordinal, ask: row.ask, receipt: row.receipt });
    leg.pulse_visits = policy.trimPulseVisits(leg.pulse_visits, row.ts);
    const pulse = policy.trailingPulseFloor(leg.pulse_visits, row.ts);
    leg.pulse_floor_cents = pulse.floor_cents; if (Number.isInteger(pulse.floor_cents)) leg.pulse_floor_ever = true;
    if (newLowAsk && newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT", receipt: row.receipt }];
    else if (newLowAsk) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt }];
    else if (newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt }];
    const quote = policy.quotePathState(leg.directional, row.ts), pressure = policy.pressureState(row.depth_ratio), combined = policy.combineState(quote, pressure);
    leg.last_combined_state = combined.state;
    leg.classifier_rows += 1;
    leg.classifier_state_counts[combined.state] += 1;
    if (combined.disagreement) leg.classifier_opposed_rows += 1;
    if (combined.authority === "QUOTE_PATH_AND_JUL6_PRESSURE_AGREE") leg.classifier_agreement_rows += 1;
    const joinLevelBeforeReceipt = leg.persistent_join_level;
    const v41Join = isMaker41 ? policy.persistenceJoinUpdate({ state: combined.state, bid: row.bid, residencySeconds: row.ts - leg.current_bid_since, currentJoinLevel: joinLevelBeforeReceipt, clauses: normalizedClauses }) : null;
    const persistentLevelTrigger = isMaker41 ? v41Join.armed : isPlacementStack && row.ts - leg.current_bid_since >= policy.PERSISTENT_LEVEL_SECONDS && leg.current_bid_last_trade_hit;
    if (isPlacementStack && persistentLevelTrigger) {
      if (isMaker41 ? v41Join.changed : leg.persistent_join_level === null || row.bid < leg.persistent_join_level) {
        leg.persistent_join_level = row.bid;
        leg.persistent_join_receipt = row.receipt;
        leg.persistent_join_evidence_receipt = isMaker41 ? row.receipt : leg.current_bid_last_trade_hit_receipt;
        leg.persistent_join_timestamp_epoch = row.ts;
        leg.post_join_book_last_trade_receipts = 0;
        leg.post_join_certified_seller_hits_at_level = 0;
      }
    }
    if (policy.qualifyingAskEvidence && policy.qualifyingAskEvidence(row)) {
      if (leg.running_qualified_ask_low === null || row.ask < leg.running_qualified_ask_low) {
        leg.running_qualified_ask_low = row.ask;
        leg.running_qualified_ask_low_unabsorbed = combined.state === "FALLING";
        leg.running_qualified_ask_low_reformed_nonfalling = combined.state !== "FALLING";
        leg.latest_new_low_evidence_ts = row.ts;
        if (combined.state === "FALLING") leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.ask, kind: "QUALIFYING_ASK_LOW_CREATED_WHILE_FALLING", receipt: row.receipt });
      }
    }
    leg.downward_evidence_rows = leg.downward_evidence_rows.filter((evidence) => evidence.ts <= row.ts && evidence.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const receiptLocalEvidenceFloor = leg.downward_evidence_rows.length ? Math.min(...leg.downward_evidence_rows.map((evidence) => evidence.price)) : null;
    const runningFloors = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const runningEvidenceFloor = runningFloors.length ? Math.min(...runningFloors) : null;
    const floorMature = Number.isFinite(leg.latest_new_low_evidence_ts) && row.ts - leg.latest_new_low_evidence_ts >= policy.LOOKBACK_SECONDS;
    const activeEvidenceFloor = policy.matureDirectionalEvidenceFloor ? policy.matureDirectionalEvidenceFloor({ state: combined.state, runningEvidenceFloor, receiptLocalEvidenceFloor, reformedQualifyingAskFloor: leg.running_qualified_ask_low, reformedQualifyingAskAuthority: leg.running_qualified_ask_low_reformed_nonfalling, floorMature }) : null;
    const causalOwnReachLowCandidates = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const causalOwnReachLow = causalOwnReachLowCandidates.length ? Math.min(...causalOwnReachLowCandidates) : null;
    const wtaInverseFalling = isPlacementStack && combined.state === "RISING" && String(base.category).startsWith("WTA") && sibling.last_combined_state === "FALLING";
    const before = leg.active_order?.target_cents ?? null;
    const askGapCents = prior && Number.isInteger(prior.ask) && Number.isInteger(row.ask) ? prior.ask - row.ask : null;
    const placementInputs = { state: combined.state, book: row, priorAsk: prior?.ask ?? null, askGapCents, activeTarget: before, pairCap: leg.pair_cap_cents, pulseFloor: pulse.floor_cents, persistentJoinLevel: isPlacementStack ? leg.persistent_join_level : null, wtaInverseFalling, causalOwnReachLow, activeEvidenceFloor, floorFirstFlickerLive: activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_unabsorbed, floorMature, recentTradeLow, priorTrueTradeLow: leg.prior_true_trade_low_cents, priorTrueTradeLowReceipt: leg.prior_true_trade_low_receipt, priorExactBidEvidence, evidencedStandingLevel: leg.evidenced_standing_level_cents, evidencedStandingAuthority: leg.evidenced_standing_authority, siblingBestAsk: normalizedClauses.deep_gap_guard ? (sibling.prior_book?.ask ?? null) : undefined, siblingEntryCents: sibling.entry_cents, siblingCredited: sibling.credited, clauses: normalizedClauses };
    leg.last_placement_inputs = placementInputs;
    const atomicReceiptDecision = (isV47 || isTradeTruthVariant) && normalizedClauses.same_tick_arm ? policy.decideReceipt({ ...placementInputs, currentJoinLevel: joinLevelBeforeReceipt, residencySeconds: row.ts - leg.current_bid_since }) : null;
    if (atomicReceiptDecision) ensure(atomicReceiptDecision.effective_join_level_cents === leg.persistent_join_level, `V47 atomic join mismatch ${leg.leg_identity} ${row.receipt}`);
    if (isV49) {
      leg.evidenced_standing_level_cents = atomicReceiptDecision.next_evidenced_standing_level_cents;
      leg.evidenced_standing_authority = atomicReceiptDecision.next_evidenced_standing_authority ?? leg.evidenced_standing_authority;
    }
    const decision = atomicReceiptDecision ? { ...atomicReceiptDecision.decision, ...(isV49 ? { evidenced_standing: { enabled: atomicReceiptDecision.evidenced_level_standing_enabled, raised: atomicReceiptDecision.raised_to_evidenced_level, evidence: atomicReceiptDecision.evidence } } : {}) } : policy.decide(placementInputs);
    if (isV49 && decision.evidenced_standing?.raised) {
      leg.evidenced_standing_decisions += 1;
      const evidenceReceipt = { ...clockFields(row.ts, base), receipt: row.receipt, order_before_cents: before, order_after_cents: decision.target_cents, evidence: decision.evidenced_standing.evidence };
      leg.evidenced_standing_first ||= evidenceReceipt;
      leg.evidenced_standing_last = evidenceReceipt;
    }
    let postCreditGuardBypass = null;
    if (isV45Family && normalizedClauses.release_guard_on_sibling_credit && sibling.credited) {
      const counterfactual = v43Policy.decide({ ...placementInputs, siblingCredited: false, clauses: { ...normalizedClauses, release_guard_on_sibling_credit: false } });
      if (counterfactual.guard?.withheld && !decision.guard?.withheld) {
        leg.post_credit_guard_reapplication_prevented_receipts += 1;
        postCreditGuardBypass = { ...clockFields(row.ts, base), receipt: row.receipt, credited_sibling_leg_identity: sibling.leg_identity, sibling_entry_cents: sibling.entry_cents, fixed_pair_cap_cents: leg.pair_cap_cents, prior_withhold: leg.deep_gap_last_withhold, own_book_receipt: row.receipt, own_book: receiptObservation(row), order_before_cents: before, V43_counterfactual_decision: counterfactual, V45_decision: decision, order_after_cents: null, mechanism: "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED" };
        if (!leg.post_credit_guard_release) {
          leg.post_credit_guard_releases += 1;
          leg.post_credit_guard_release = postCreditGuardBypass;
          actions.push({ kind: "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED", event_id: base.event_id, leg_identity: leg.leg_identity, ...postCreditGuardBypass });
        }
      }
    }
    if (normalizedClauses.deep_gap_guard) noteV42Guard(leg, decision, row, base, actions, leg.leg_identity);
    if (decision.gap_credit?.eligible) {
      leg.gap_credit_eligible_receipts += 1;
      const gapReceipt = { event_id: base.event_id, leg_identity: leg.leg_identity, category: base.category, price_region: leg.price_region, ...clockFields(row.ts, base), receipt: row.receipt, prior_ask_cents: prior?.ask ?? null, current_ask_cents: row.ask, ask_gap_cents: askGapCents, order_before_cents: before, pair_cap_cents: leg.pair_cap_cents, sibling_leg_identity: sibling.leg_identity, sibling_credited: sibling.credited, sibling_entry_cents: sibling.entry_cents, decision: decision.gap_credit, order_after_cents: decision.gap_credit.authorized ? decision.target_cents : before };
      leg.gap_credit_first ||= gapReceipt;
      leg.gap_credit_last = gapReceipt;
      if (decision.gap_credit.authorized) leg.gap_credit_authorized_walks += 1;
      else if (decision.gap_credit.reason === "V46_GAP_CREDIT_REFUSED_SIBLING_NOT_CREDITED") leg.gap_credit_sibling_uncredited_refusals += 1;
      else leg.gap_credit_no_lawful_reprice += 1;
      actions.push({ kind: decision.gap_credit.authorized ? "GAP_CREDIT_AUTHORIZED" : "GAP_CREDIT_REFUSED", ...gapReceipt });
    }
    if (isPlacementStack && decision.placement?.sanity_bound_applied) leg.sanity_bound_rows += 1;
    leg.prior_book = row; leg.decision_count += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1; leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: receiptObservation(row), sibling_observation: sibling.prior_book ? receiptObservation(sibling.prior_book) : null, quote_path_state: quote.state, pressure_state: pressure, combined_state: combined.state, direction_authority: combined.authority, disagreement: combined.disagreement, pulse_floor: pulse, persistent_level_join: { level_cents: leg.persistent_join_level, receipt: leg.persistent_join_receipt, evidence_receipt: leg.persistent_join_evidence_receipt, timestamp_epoch: leg.persistent_join_timestamp_epoch, current_bid_residency_seconds: row.ts - leg.current_bid_since, book_last_trade_equals_bid_receipts: leg.book_last_trade_hits_by_level.get(row.bid) || 0, certified_seller_aggressed_prints_at_current_bid: leg.seller_hits_by_level.get(row.bid) || 0, post_join_book_last_trade_receipts: leg.post_join_book_last_trade_receipts, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level }, wta_other_expression_falling: wtaInverseFalling, causal_own_reach_low_cents: causalOwnReachLow, active_evidence_floor_cents: activeEvidenceFloor, floor_mature: floorMature, pair_cap_cents: leg.pair_cap_cents, order_before_cents: before, decision, order_after_cents: null };
    leg.first_decision ||= detail; leg.last_decision = detail;
    applyRestDecision(leg, sibling, row, decision, combined.state, detail, actions, base, leg.leg_identity);
    detail.order_after_cents = leg.active_order?.target_cents ?? null;
    if (isV47 && v41Join?.changed) {
      const sameReceiptPost = ["PLACE_REST", "REPRICE_REST"].includes(decision.action) && detail.order_after_cents === v41Join.level_cents;
      const alreadyAtLevel = decision.action === "HOLD_REST" && before === v41Join.level_cents && detail.order_after_cents === v41Join.level_cents;
      joinQualifications.push({
        event_id: base.event_id,
        leg_identity: leg.leg_identity,
        category: base.category,
        price_region: leg.price_region,
        bell_confidence: base.bell_confidence,
        mode,
        qualification_timestamp_epoch: row.ts,
        qualification_receipt: row.receipt,
        qualification_level_cents: v41Join.level_cents,
        residency_seconds: row.ts - leg.current_bid_since,
        clause_same_tick_arm: normalizedClauses.same_tick_arm,
        order_before_cents: before,
        decision_action: decision.action,
        decision_reason: decision.reason,
        order_after_cents: detail.order_after_cents,
        guard_withheld: Boolean(decision.guard?.withheld),
        disposition: sameReceiptPost ? "POSTED_ON_QUALIFYING_RECEIPT" : alreadyAtLevel ? "ALREADY_RESTING_AT_QUALIFIED_LEVEL" : decision.guard?.withheld ? "UNCHANGED_GUARD_WITHHELD" : "UNCHANGED_LAW_DID_NOT_POST_QUALIFIED_LEVEL",
        scheduler_latency_seconds: sameReceiptPost || alreadyAtLevel ? 0 : null,
      });
    }
    if (postCreditGuardBypass && leg.post_credit_guard_release === postCreditGuardBypass) postCreditGuardBypass.order_after_cents = detail.order_after_cents;
    if (Number.isInteger(detail.order_after_cents) && detail.order_after_cents >= row.ask) leg.sanity_violation_rows += 1;
    if (row.ts <= leg.union_first_evidence_timestamp_epoch) leg.reach_snapshot = { ...detail };

    // A sibling best-ask change is a new receipt for the V42 clause.  Only a
    // leg actively withheld by V42 is re-evaluated cross-leg; all other V41
    // streams retain their exact incumbent receipt path.
    if (normalizedClauses.deep_gap_guard) reevaluateV42WithSiblingBook(sibling, leg, row, actions, base);
  }
  for (const leg of Object.values(event.legs)) {
    leg.resting_target_at_edge_cents = leg.credited ? null : (leg.active_order?.target_cents ?? null);
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    if (!leg.credited) leg.terminal_reason = leg.decision_count === 0 ? "NO_TWO_SIDED_BOOK_DECISION_INSIDE_V36_EDGE" : leg.active_order ? "REST_UNFILLED_AT_HARD_PREBELL_EDGE" : "NO_LAWFUL_REST_AT_HARD_PREBELL_EDGE";
    leg.final_state = leg.credited ? "CREDITED" : leg.active_order ? "RESTING_UNFILLED" : "NEVER_PLACED_OR_CANCELLED";
    leg.persistent_join_book_last_trade_receipts = leg.persistent_join_level === null ? 0 : (leg.book_last_trade_hits_by_level.get(leg.persistent_join_level) || 0);
    leg.persistent_join_certified_seller_aggressed_prints = leg.persistent_join_level === null ? 0 : (leg.seller_hits_by_level.get(leg.persistent_join_level) || 0);
    delete leg.active_order; delete leg.prior_book; delete leg.directional; delete leg.pulse_visits; delete leg.recent_trade_rows; delete leg.exact_bid_first_receipt; delete leg.first_action; delete leg.seller_hits_by_level; delete leg.book_last_trade_hits_by_level; delete leg.downward_evidence_rows; delete leg.last_placement_inputs; delete leg.deep_gap_withhold_active;
  }
  const legs = Object.values(event.legs);
  event.completed_pair = legs.every((leg) => leg.credited);
  event.combined_entry_cents = event.completed_pair ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
  event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100;
  return { event, actions, joinQualifications };
}

function score(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const completed = events.filter((event) => event.completed_pair), under = completed.filter((event) => event.pair_under_par);
  const frontier = {};
  for (const [name, predicate] of Object.entries({ LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true })) frontier[name] = completed.filter((event) => predicate(event.combined_entry_cents)).length;
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.first_action_timestamp_epoch !== null).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, under_par_pairs: under.length, locked_cents_per_contract: under.reduce((sum, event) => sum + 100 - event.combined_entry_cents, 0), locked_cents_five_lot: under.reduce((sum, event) => sum + (100 - event.combined_entry_cents) * 5, 0), maker_fill_classes: countBy(legs.filter((leg) => leg.credited), (leg) => leg.fill_class), frontier, conservation: { D: events.length, legs: legs.length, pass: events.length === 804 && legs.length === 1608 } };
}

function fullBookPnl(events, closeByTicker) {
  const rows = [], categories = new Map();
  for (const event of events) {
    const legs = Object.values(event.legs), credited = legs.filter((leg) => leg.credited);
    let disposition, pnl = 0, priced = true, nakedLeg = null;
    if (credited.length === 2) {
      disposition = "COMPLETED";
      pnl = 100 - credited.reduce((sum, leg) => sum + leg.entry_cents, 0);
    } else if (credited.length === 1) {
      disposition = "NAKED";
      nakedLeg = credited[0];
      const close = closeByTicker.get(nakedLeg.ticker);
      priced = Number.isInteger(close);
      pnl = priced ? close - nakedLeg.entry_cents : null;
    } else {
      disposition = "SKIP";
      pnl = 0;
    }
    const row = { event_id: event.event_id, category: event.category, disposition, completed: disposition === "COMPLETED", naked: disposition === "NAKED", skip: disposition === "SKIP", pair_entry_cents: disposition === "COMPLETED" ? event.combined_entry_cents : null, completed_locked_cents: disposition === "COMPLETED" ? pnl : 0, naked_leg_identity: nakedLeg?.leg_identity ?? null, naked_entry_cents: nakedLeg?.entry_cents ?? null, naked_close_cents: nakedLeg ? (closeByTicker.get(nakedLeg.ticker) ?? null) : null, naked_priced: disposition === "NAKED" ? priced : null, naked_pnl_cents: disposition === "NAKED" && priced ? pnl : 0, net_cents: disposition === "NAKED" && !priced ? 0 : pnl };
    rows.push(row);
    if (!categories.has(event.category)) categories.set(event.category, []);
    categories.get(event.category).push(row);
  }
  const summarize = (x) => ({ events: x.length, completed_pairs: x.filter((row) => row.completed).length, completed_locked_cents: x.reduce((sum, row) => sum + row.completed_locked_cents, 0), naked_legs: x.filter((row) => row.naked).length, naked_priced: x.filter((row) => row.naked && row.naked_priced).length, naked_open: x.filter((row) => row.naked && !row.naked_priced).length, naked_pnl_cents: x.reduce((sum, row) => sum + row.naked_pnl_cents, 0), skips: x.filter((row) => row.skip).length, true_book_net_cents: x.reduce((sum, row) => sum + row.net_cents, 0) });
  return { aggregate: summarize(rows), by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => [key, summarize(value)])), rows, conservation: { events: rows.length, disposition_sum: rows.filter((row) => row.completed).length + rows.filter((row) => row.naked).length + rows.filter((row) => row.skip).length, pass: rows.length === 804 && rows.every((row) => ["COMPLETED", "NAKED", "SKIP"].includes(row.disposition)) } };
}

function scorePartitions(events) {
  const groups = new Map();
  for (const event of events) {
    const key = `${event.category}|${event.bell_confidence}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(event);
  }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({
    cell,
    category: rows[0].category,
    bell_confidence: rows[0].bell_confidence,
    ...score(rows),
  }));
}

function tradedFloorCensus(baseByEvent, printLoad, reachByEvent) {
  const legRows = [], gameRows = [];
  for (const base of [...baseByEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    const reach = reachByEvent.get(base.event_id), legs = [];
    for (const [legId, leg] of Object.entries(base.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const prints = printLoad.byTicker.get(leg.ticker) || [];
      const lawful = prints.filter((row) => row.ts >= base.left && row.ts <= base.right && Number.isInteger(row.price) && typeof row.trade_id === "string" && row.trade_id.length > 0);
      const minimum = lawful.length ? Math.min(...lawful.map((row) => row.price)) : null;
      const floorPrint = Number.isInteger(minimum) ? lawful.find((row) => row.price === minimum) : null;
      const oldUnion = reach?.legs?.[legId]?.union_reach_cents ?? null;
      const row = {
        event_id: base.event_id,
        category: base.category,
        bell_confidence: base.bell_confidence,
        starting_price_split: base.starting_price_split,
        leg_identity: leg.leg_identity,
        ticker: leg.ticker,
        price_region: leg.price_region,
        lawful_span: { left_epoch: base.left, right_epoch: base.right },
        lowest_traded_price_cents: minimum,
        floor_print: floorPrint ? { timestamp_epoch: floorPrint.ts, receipt: floorPrint.receipt, trade_id: floorPrint.trade_id, size: floorPrint.size, taker_side: floorPrint.taker_side, taker_book_side: floorPrint.taker_book_side } : null,
        lawful_true_prints: lawful.length,
        old_union_floor_cents: oldUnion,
        traded_minus_old_union_cents: Number.isInteger(minimum) && Number.isInteger(oldUnion) ? minimum - oldUnion : null,
      };
      legRows.push(row); legs.push(row);
    }
    const traded = legs.map((row) => row.lowest_traded_price_cents), old = legs.map((row) => row.old_union_floor_cents);
    const tradedComplete = traded.every(Number.isInteger), oldComplete = old.every(Number.isInteger);
    const tradedSum = tradedComplete ? traded.reduce((a, b) => a + b, 0) : null;
    const oldSum = oldComplete ? old.reduce((a, b) => a + b, 0) : null;
    const classify = (sum) => !Number.isInteger(sum) ? "UNAVAILABLE" : sum < 100 ? "UNDER_PAR" : "OVER_PAR";
    gameRows.push({
      event_id: base.event_id,
      category: base.category,
      bell_confidence: base.bell_confidence,
      starting_price_split: base.starting_price_split,
      lowest_traded_pair_sum_cents: tradedSum,
      old_union_pair_sum_cents: oldSum,
      traded_floor_class: classify(tradedSum),
      old_union_class: classify(oldSum),
      flip: `${classify(oldSum)}->${classify(tradedSum)}`,
      legs: legs.map((row) => ({ leg_identity: row.leg_identity, lowest_traded_price_cents: row.lowest_traded_price_cents, old_union_floor_cents: row.old_union_floor_cents })),
    });
  }
  const summarize = (rows) => ({ games: rows.length, traded_floor_classes: countBy(rows, (row) => row.traded_floor_class), old_union_classes: countBy(rows, (row) => row.old_union_class), flips: countBy(rows, (row) => row.flip) });
  const categories = new Map();
  for (const row of gameRows) { if (!categories.has(row.category)) categories.set(row.category, []); categories.get(row.category).push(row); }
  return {
    law: "PER_LEG_FLOOR_IS_LOWEST_LAWFUL_TRUE_TRADED_PRICE_IN_HARD_WINDOW1_SPAN; NO_ASK_AGGRESSOR_DWELL_SIZE_OR_ARRIVAL_FILTER",
    aggregate: summarize(gameRows),
    by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => [key, summarize(rows)])),
    leg_rows: legRows,
    game_rows: gameRows,
    conservation: { games: gameRows.length, legs: legRows.length, expected_games: 804, expected_legs: 1608, pass: gameRows.length === 804 && legRows.length === 1608 },
  };
}

function gradeAgainstTradedFloors(events, tradedFloorByLeg) {
  const rows = [], games = [];
  for (const event of events) {
    const legs = Object.values(event.legs).map((leg) => {
      const floor = tradedFloorByLeg.get(leg.leg_identity), value = floor?.lowest_traded_price_cents ?? null;
      const row = { event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, starting_price_split: event.starting_price_split, leg_identity: leg.leg_identity, ticker: leg.ticker, price_region: leg.price_region, credited: leg.credited, entry_cents: leg.entry_cents, lowest_traded_price_cents: value, gap_to_lowest_trade_cents: leg.credited && Number.isInteger(value) ? leg.entry_cents - value : null, fill_class: leg.fill_class };
      rows.push(row); return row;
    });
    games.push({ event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, completed: event.completed_pair, under_par: event.pair_under_par, combined_entry_cents: event.combined_entry_cents, both_traded_floors_available: legs.every((row) => Number.isInteger(row.lowest_traded_price_cents)), pair_traded_floor_cents: legs.every((row) => Number.isInteger(row.lowest_traded_price_cents)) ? legs.reduce((sum, row) => sum + row.lowest_traded_price_cents, 0) : null, gaps_cents: legs.map((row) => row.gap_to_lowest_trade_cents) });
  }
  const summarize = (eventRows, legSubset) => ({ score: score(eventRows), credited_leg_gap_to_lowest_trade_cents: distribution(legSubset.filter((row) => row.credited).map((row) => row.gap_to_lowest_trade_cents)), credited_at_or_better_than_lowest_trade: legSubset.filter((row) => row.credited && Number.isInteger(row.gap_to_lowest_trade_cents) && row.gap_to_lowest_trade_cents <= 0).length, traded_floor_missing_legs: legSubset.filter((row) => !Number.isInteger(row.lowest_traded_price_cents)).length });
  const cells = new Map();
  for (const event of events) { const key = `${event.category}|${event.bell_confidence}`; if (!cells.has(key)) cells.set(key, []); cells.get(key).push(event); }
  return {
    aggregate: summarize(events, rows),
    category_x_bell_confidence: [...cells].sort(([a], [b]) => a.localeCompare(b)).map(([cell, eventRows]) => { const ids = new Set(eventRows.map((row) => row.event_id)); return { cell, category: eventRows[0].category, bell_confidence: eventRows[0].bell_confidence, ...summarize(eventRows, rows.filter((row) => ids.has(row.event_id))) }; }),
    rows,
    games,
    conservation: { games: games.length, legs: rows.length, pass: games.length === 804 && rows.length === 1608 },
  };
}

function ladderDifferential(incumbentEvents, ladderEvents, closeByTicker, ladderName) {
  const prior = new Map(incumbentEvents.map((event) => [event.event_id, event])), rows = [];
  for (const event of ladderEvents) {
    const baseline = prior.get(event.event_id); ensure(baseline, `missing incumbent event ${event.event_id}`);
    for (const [legId, leg] of Object.entries(event.legs)) {
      const old = baseline.legs[legId];
      let disposition = "UNCHANGED";
      if (!old.credited && leg.credited) disposition = "FILL_GAINED";
      else if (old.credited && !leg.credited) disposition = "FILL_LOST";
      else if (old.credited && leg.credited && old.entry_cents !== leg.entry_cents) disposition = leg.entry_cents < old.entry_cents ? "FILL_REPRICED_FAVORABLE" : "FILL_REPRICED_ADVERSE";
      if (disposition === "UNCHANGED") continue;
      rows.push({ event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, leg_identity: leg.leg_identity, ladder: ladderName, disposition, incumbent_credited: old.credited, incumbent_entry_cents: old.entry_cents, ladder_credited: leg.credited, ladder_entry_cents: leg.entry_cents, reprice_delta_cents: old.credited && leg.credited ? leg.entry_cents - old.entry_cents : null, incumbent_pair_completed: baseline.completed_pair, ladder_pair_completed: event.completed_pair, incumbent_combined_entry_cents: baseline.combined_entry_cents, ladder_combined_entry_cents: event.combined_entry_cents });
    }
  }
  const oldBook = fullBookPnl(incumbentEvents, closeByTicker).aggregate, newBook = fullBookPnl(ladderEvents, closeByTicker).aggregate;
  const summarize = (subset) => ({ changed_legs: subset.length, dispositions: countBy(subset, (row) => row.disposition), favorable_reprice_cents: -subset.filter((row) => row.disposition === "FILL_REPRICED_FAVORABLE").reduce((sum, row) => sum + row.reprice_delta_cents, 0), adverse_reprice_cents: subset.filter((row) => row.disposition === "FILL_REPRICED_ADVERSE").reduce((sum, row) => sum + row.reprice_delta_cents, 0) });
  const categories = new Map(); for (const row of rows) { if (!categories.has(row.category)) categories.set(row.category, []); categories.get(row.category).push(row); }
  return { ladder: ladderName, aggregate: summarize(rows), by_category: Object.fromEntries([...categories].sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => [key, summarize(value)])), score_delta: { completed_pairs: score(ladderEvents).completed_pairs - score(incumbentEvents).completed_pairs, under_par_pairs: score(ladderEvents).under_par_pairs - score(incumbentEvents).under_par_pairs, locked_cents: newBook.completed_locked_cents - oldBook.completed_locked_cents, naked_pnl_cents: newBook.naked_pnl_cents - oldBook.naked_pnl_cents, true_book_net_cents: newBook.true_book_net_cents - oldBook.true_book_net_cents }, rows };
}

function deepGapDifferential(v41Events, v42Events, closeByTicker) {
  const current = new Map(v42Events.map((event) => [event.event_id, event])), rows = [];
  for (const prior of v41Events) {
    const next = current.get(prior.event_id); ensure(next, `missing V42 event ${prior.event_id}`);
    const priorLegs = Object.values(prior.legs), nextLegs = Object.values(next.legs);
    const priorCredited = priorLegs.filter((leg) => leg.credited), nextCredited = nextLegs.filter((leg) => leg.credited);
    if (JSON.stringify(priorLegs.map((leg) => [leg.leg_identity, leg.credited, leg.entry_cents, leg.fill_class])) === JSON.stringify(nextLegs.map((leg) => [leg.leg_identity, leg.credited, leg.entry_cents, leg.fill_class]))) continue;
    let classification = "OTHER_CHANGED_STREAM", cents = 0;
    if (priorCredited.length === 1 && nextCredited.length === 0) {
      const leg = priorCredited[0], close = closeByTicker.get(leg.ticker), nakedPnl = Number.isInteger(close) ? close - leg.entry_cents : null;
      if (Number.isInteger(nakedPnl) && nakedPnl < 0) { classification = "LOSS_AVOIDED"; cents = -nakedPnl; }
      else if (Number.isInteger(nakedPnl) && nakedPnl > 0) { classification = "WINNING_NAKED_FORFEITED"; cents = -nakedPnl; }
      else classification = Number.isInteger(nakedPnl) ? "FLAT_NAKED_REMOVED" : "OPEN_NAKED_REMOVED";
    } else if (priorCredited.length === 2 && nextCredited.length < 2) {
      classification = "COMPLETED_PAIR_FORFEITED";
      cents = -(100 - priorCredited.reduce((sum, leg) => sum + leg.entry_cents, 0));
    } else if (nextCredited.length > priorCredited.length) classification = "CREDIT_RECOVERED";
    rows.push({ event_id: prior.event_id, category: prior.category, classification, cents, V41: { credited_legs: priorCredited.length, entries: priorCredited.map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents })) }, V42: { credited_legs: nextCredited.length, entries: nextCredited.map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents })) } });
  }
  return { rows, aggregate: { changed_events: rows.length, losses_avoided: { events: rows.filter((row) => row.classification === "LOSS_AVOIDED").length, cents: rows.filter((row) => row.classification === "LOSS_AVOIDED").reduce((sum, row) => sum + row.cents, 0) }, pairs_forfeited: { events: rows.filter((row) => row.classification === "COMPLETED_PAIR_FORFEITED").length, cents: -rows.filter((row) => row.classification === "COMPLETED_PAIR_FORFEITED").reduce((sum, row) => sum + row.cents, 0) }, winning_naked_forfeited: { events: rows.filter((row) => row.classification === "WINNING_NAKED_FORFEITED").length, cents: -rows.filter((row) => row.classification === "WINNING_NAKED_FORFEITED").reduce((sum, row) => sum + row.cents, 0) }, net_classified_cents: rows.reduce((sum, row) => sum + row.cents, 0), by_class: countBy(rows, (row) => row.classification) } };
}

function kalshiTakerFeePerContractCents(priceCents) {
  ensure(Number.isInteger(priceCents) && priceCents >= 1 && priceCents <= 99, `invalid taker price ${priceCents}`);
  const p = priceCents / 100;
  return Math.ceil(0.07 * p * (1 - p) * 100);
}

function frozenV36NetScore(events) {
  const summarize = (rows) => {
    const legs = rows.flatMap((event) => Object.values(event.legs));
    const takers = legs.filter((leg) => leg.credited && String(leg.fill_class).startsWith("PROVEN_TAKER"));
    const makers = legs.filter((leg) => leg.credited && String(leg.fill_class).startsWith("PROVEN_MAKER"));
    const completed = rows.filter((event) => Object.values(event.legs).every((leg) => leg.credited));
    const grossUnder = completed.filter((event) => Object.values(event.legs).reduce((sum, leg) => sum + leg.entry_cents, 0) < 100);
    const grossLocked = grossUnder.reduce((sum, event) => sum + 100 - Object.values(event.legs).reduce((s, leg) => s + leg.entry_cents, 0), 0);
    const completedNet = completed.map((event) => {
      const eventLegs = Object.values(event.legs), grossCost = eventLegs.reduce((sum, leg) => sum + leg.entry_cents, 0);
      const fees = eventLegs.reduce((sum, leg) => sum + (String(leg.fill_class).startsWith("PROVEN_TAKER") ? kalshiTakerFeePerContractCents(leg.entry_cents) : 0), 0);
      return { gross_cost: grossCost, fee: fees, net_locked: 100 - grossCost - fees };
    });
    const feeAll = takers.reduce((sum, leg) => sum + kalshiTakerFeePerContractCents(leg.entry_cents), 0);
    const feeCompleted = completedNet.reduce((sum, row) => sum + row.fee, 0);
    return {
      events: rows.length,
      credited_legs: takers.length + makers.length,
      maker_legs_fee_exempt: makers.length,
      taker_legs_charged: takers.length,
      completed_pairs: completed.length,
      gross_under_par_pairs: grossUnder.length,
      net_positive_completed_pairs: completedNet.filter((row) => row.net_locked > 0).length,
      games_flipped_negative_by_fees: completedNet.filter((row) => row.gross_cost < 100 && row.net_locked < 0).length,
      games_flipped_to_zero_by_fees: completedNet.filter((row) => row.gross_cost < 100 && row.net_locked === 0).length,
      gross_locked_cents_per_contract: grossLocked,
      gross_locked_cents_five_lot: grossLocked * 5,
      taker_fees_all_credited_legs_cents_per_contract: feeAll,
      taker_fees_all_credited_legs_five_lot: feeAll * 5,
      taker_fees_completed_pairs_cents_per_contract: feeCompleted,
      taker_fees_completed_pairs_five_lot: feeCompleted * 5,
      net_locked_after_all_entry_taker_fees_cents_per_contract: grossLocked - feeAll,
      net_locked_after_all_entry_taker_fees_five_lot: (grossLocked - feeAll) * 5,
      completed_pair_net_locked_cents_per_contract: completedNet.reduce((sum, row) => sum + row.net_locked, 0),
      completed_pair_net_locked_cents_five_lot: completedNet.reduce((sum, row) => sum + row.net_locked, 0) * 5,
    };
  };
  const groups = new Map();
  for (const event of events) { if (!groups.has(event.category)) groups.set(event.category, []); groups.get(event.category).push(event); }
  return { fee_law: "TAKER=CEIL(0.07*P*(1-P)*100)_CENTS_PER_CONTRACT; MAKER=0; FIVE_CONTRACTS_PER_LEG", aggregate: summarize(events), per_category: [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([category, rows]) => ({ category, ...summarize(rows) })) };
}

function frozenV36Score(reachRows) {
  const byEvent = new Map();
  for (const row of reachRows) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  const events = [...byEvent].map(([event_id, legs]) => {
    const completed = legs.length === 2 && legs.every((leg) => leg.v36_credited && Number.isInteger(leg.v36_entry_cents));
    const cost = completed ? legs.reduce((sum, leg) => sum + leg.v36_entry_cents, 0) : null;
    return {
      event_id,
      completed_pair: completed,
      combined_entry_cents: cost,
      pair_under_par: completed && cost < 100,
      legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, {
        first_action_timestamp_epoch: leg.v36_decision_count > 0 ? leg.v36_left_epoch : null,
        credited: Boolean(leg.v36_credited),
        fill_class: leg.v36_fill_class,
      }])),
    };
  });
  return score(events);
}

function classifierTelemetry(events) {
  const legs = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, event_category: event.category, event_bell_confidence: event.bell_confidence })));
  const sealedDirection = (leg) => leg.leg_direction === "CLIMBING" ? "RISING" : leg.leg_direction === "FALLING" ? "FALLING" : leg.leg_direction === "FLAT" ? "SETTLED" : null;
  const summarize = (rows) => {
    const atReach = rows.filter((leg) => sealedDirection(leg) && leg.reach_snapshot?.combined_state);
    const atReachCorrect = atReach.filter((leg) => leg.reach_snapshot.combined_state === sealedDirection(leg));
    return {
      legs: rows.length,
      decision_receipts: rows.reduce((sum, leg) => sum + leg.classifier_rows, 0),
      eligible_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0),
      correct_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0),
      receipt_accuracy: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) ? rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0) / rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) : null,
      reach_moment_eligible_legs: atReach.length,
      reach_moment_correct_legs: atReachCorrect.length,
      reach_moment_accuracy: atReach.length ? atReachCorrect.length / atReach.length : null,
      reach_moment_confusion: countBy(atReach, (leg) => `${sealedDirection(leg)}->${leg.reach_snapshot.combined_state}`),
      agreement_receipts: rows.reduce((sum, leg) => sum + leg.classifier_agreement_rows, 0),
      opposed_receipts_settled: rows.reduce((sum, leg) => sum + leg.classifier_opposed_rows, 0),
    };
  };
  const groups = new Map(); for (const leg of legs) { const key = `${leg.event_category}|${leg.event_bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(leg); }
  return { aggregate: summarize(legs), category_x_bell_confidence: [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, ...summarize(rows) })), telemetry_only_ex_post_direction_not_consumed_by_policy: true };
}

function residualOwner(leg, reach, base) {
  if (leg.credited && leg.entry_cents <= reach) return null;
  if (leg.credited && String(leg.fill_class).includes("TAKER")) return { owner: "TAKE_FIRED_ABOVE_REACH", detail: `take ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (leg.credited) return { owner: `${leg.fill_source_state || "UNKNOWN"}_REST_FILLED_SHALLOW`, detail: `entry ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (!leg.reach_inside_v36_edge) return { owner: "HARD_PREBELL_EDGE_EXCLUDES_REACH_EVIDENCE", detail: `reach evidence ${leg.union_first_evidence_timestamp_epoch} outside ${base.left}..${base.right}`, measurable_cents: null };
  const snapshot = leg.reach_snapshot || leg.last_decision, rest = snapshot?.order_after_cents ?? leg.resting_target_at_edge_cents, cap = snapshot?.pair_cap_cents ?? leg.pair_cap_cents;
  if (Number.isInteger(cap) && reach > cap) return { owner: "PAIR_CAP_ARITHMETIC", detail: `reach ${reach} > cap ${cap}`, measurable_cents: reach - cap };
  if (leg.decision_count === 0) return { owner: "ADMISSION_NO_TWO_SIDED_BOOK", detail: "no decision receipt inside hard edge", measurable_cents: null };
  if (Number.isInteger(rest) && rest >= reach) return { owner: "UNION_REACH_PRECEDED_RESIDENCY_OR_CHANNEL_NOT_REPEATED", detail: `rest ${rest} at/above reach ${reach} but no later union channel`, measurable_cents: 0 };
  const state = snapshot?.combined_state || leg.last_decision?.combined_state || "UNKNOWN";
  const gap = Number.isInteger(rest) ? reach - rest : null;
  if (state === "RISING" && !leg.pulse_floor_ever) return { owner: "RISER_NO_TWO_VISIT_TRAILING_PULSE_FLOOR", detail: `no signable revisited pulse floor; reach ${reach}`, measurable_cents: gap };
  if (state === "RISING") return { owner: "RISER_PULSE_REST_OFF_REACH", detail: `pulse rest ${rest} below reach ${reach}`, measurable_cents: gap };
  if (state === "FALLING") return { owner: "FALLER_V36_NO_CHASE_REST_OFF_REACH", detail: `falling rest ${rest} below reach ${reach}`, measurable_cents: gap };
  return { owner: "SETTLED_BID_MINUS_ONE_REST_OFF_REACH", detail: `settled rest ${rest} below reach ${reach}`, measurable_cents: gap };
}

function gradeAgainstReach(events, reachByEvent, baseByEvent) {
  const rows = [], residuals = [], classRows = [];
  for (const event of events) {
    const reach = reachByEvent.get(event.event_id);
    if (!reach) continue;
    const levels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const reachComplete = levels.every(Number.isInteger), reachCost = reachComplete ? levels.reduce((a, b) => a + b, 0) : null;
    if (!(reachComplete && reachCost < 100)) continue;
    const legRows = [];
    for (const id of Object.keys(event.legs).sort()) {
      const leg = event.legs[id], level = reach.legs[id].union_reach_cents, gap = leg.credited ? leg.entry_cents - level : null;
      const bind = residualOwner(leg, level, baseByEvent.get(event.event_id));
      const row = { event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, starting_price_split: event.starting_price_split, price_region: leg.price_region, bell_confidence: event.bell_confidence, reach_cents: level, reach_sources: reach.legs[id].union_sources, reach_first_evidence_timestamp_epoch: reach.legs[id].union_first_evidence_timestamp_epoch, credited: leg.credited, entry_cents: leg.entry_cents, gap_to_reach_cents: gap, fill_class: leg.fill_class, terminal_state: leg.final_state, terminal_rest_cents: leg.resting_target_at_edge_cents, pair_cap_cents: leg.pair_cap_cents, pulse_floor_ever: leg.pulse_floor_ever, terminal_pulse_floor_cents: leg.pulse_floor_cents, reach_snapshot: leg.reach_snapshot, layer_bind: bind };
      legRows.push(row); rows.push(row); if (bind) residuals.push(row);
    }
    const completed = legRows.every((row) => row.credited), shallowCents = legRows.filter((row) => Number.isInteger(row.gap_to_reach_cents) && row.gap_to_reach_cents > 0).reduce((sum, row) => sum + row.gap_to_reach_cents, 0);
    const grade = completed ? (shallowCents === 0 ? "MATCHED" : "SHALLOW") : "MISSING";
    classRows.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, bell_confidence: event.bell_confidence, reach_cost_cents: reachCost, reach_locked_cents: 100 - reachCost, grade, completed, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, shallow_cents: shallowCents, measurable_residual_cents: legRows.reduce((sum, row) => sum + (row.layer_bind?.measurable_cents || 0), 0), legs: legRows.map((row) => ({ leg_identity: row.leg_identity, reach_cents: row.reach_cents, credited: row.credited, entry_cents: row.entry_cents, gap_to_reach_cents: row.gap_to_reach_cents, owner: row.layer_bind?.owner || null })) });
  }
  const aggregate = { answer_key_games: classRows.length, answer_key_locked_cents: classRows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(classRows, (row) => row.grade), shallow_gap_cents: distribution(rows.map((row) => row.gap_to_reach_cents).filter((gap) => Number.isInteger(gap) && gap > 0)), measurable_residual_cents: distribution(residuals.map((row) => row.layer_bind?.measurable_cents).filter(Number.isFinite)), completed_pairs: classRows.filter((row) => row.completed).length, under_par_pairs: classRows.filter((row) => row.under_par).length };
  ensure(aggregate.answer_key_games === EXPECTED_REACH.under_par_games && aggregate.answer_key_locked_cents === EXPECTED_REACH.locked_cents, "reach answer-key conservation failed");
  return { rows, residuals, classRows, aggregate };
}

function cellSummary(grades) {
  const groups = new Map();
  for (const row of grades.classRows) { const key = `${row.category}|${row.bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, bell_confidence: rows[0].bell_confidence, answer_key_games: rows.length, reach_locked_cents: rows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(rows, (row) => row.grade), completed_pairs: rows.filter((row) => row.completed).length, under_par_pairs: rows.filter((row) => row.under_par).length, shallow_cents: distribution(rows.map((row) => row.shallow_cents).filter((x) => x > 0)), measurable_residual_cents: distribution(rows.map((row) => row.measurable_residual_cents).filter((x) => x > 0)) }));
}

async function main() {
  ensure(gitHead(v36Root) === V36_COMMIT, "V36 frozen worktree mismatch");
  ensure(gitHead(reachRoot) === REACH_COMMIT, "reach frozen worktree mismatch");
  ensure(gitHead(gapRoot) === GAP_COMMIT, "gap-grade frozen worktree mismatch");
  ensure(isPlacementStack || gitHead(repo) === GAP_COMMIT || compare, "V38 must build from b581cbb parent before commit");
  safeOutput(output);
  const v36Package = path.join(v36Root, V36_PACKAGE), gapPackage = path.join(gapRoot, GAP_PACKAGE);
  const v36StrictFrozenEvents = readRows(path.join(v36Package, "STRICT_EVENT_LEDGER.jsonl.gz"));
  ensure(v36StrictFrozenEvents.length === 804, "frozen V36 strict ledger must contain 804 events");
  const spans = JSON.parse(fs.readFileSync(path.join(v36Package, "WINDOW1_SPAN_804.json"), "utf8")).rows;
  const v36Trace = JSON.parse(fs.readFileSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json"), "utf8")).rows;
  const reachRows = readRows(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz"));
  ensure(spans.length === 804 && v36Trace.length === 1608 && reachRows.length === 1608, "frozen population mismatch");
  const traceByLeg = new Map(v36Trace.map((row) => [row.leg_identity, row])), reachByLeg = new Map(reachRows.map((row) => [row.leg_identity, row]));
  const reachByEvent = new Map(), baseByEvent = new Map(), tickerBounds = new Map();
  for (const row of reachRows) {
    if (!reachByEvent.has(row.event_id)) reachByEvent.set(row.event_id, { event_id: row.event_id, legs: {} });
    reachByEvent.get(row.event_id).legs[row.leg_id] = row;
  }
  for (const span of spans) {
    const scheduled = Number.isFinite(span.formation_clock?.t_minus_scheduled_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_scheduled_seconds : null;
    const actualBell = Number.isFinite(span.formation_clock?.t_minus_actual_bell_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_actual_bell_seconds : null;
    const base = { event_id: span.event_id, category: span.category, starting_price_split: span.starting_price_split, bell_confidence: span.precision_class, edge_source_field: span.edge_source_field, left: span.w1_left_epoch, right: span.w1_right_epoch, scheduled, actual_bell: actualBell, legs: {} };
    for (const leg of span.per_leg) {
      const prior = traceByLeg.get(leg.leg_identity), reach = reachByLeg.get(leg.leg_identity);
      ensure(prior && reach, `missing leg binding ${leg.leg_identity}`);
      const legId = leg.leg_identity.split("|").at(-1);
      base.legs[legId] = { leg_id: legId, leg_identity: leg.leg_identity, ticker: leg.ticker, category: span.category, price_region: prior.price_region, leg_direction: reach.leg_direction, reach };
      tickerBounds.set(leg.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
    }
    ensure(Object.keys(base.legs).length === 2, `event not paired ${span.event_id}`);
    baseByEvent.set(span.event_id, base);
  }
  ensure(baseByEvent.size === 804 && tickerBounds.size === 1608, "base conservation failed");
  const machineSpecs = isV49 ? [
    { name: "TRADE_TRUTH_V47_BASELINE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, evidenced_level_standing: false } },
    { name: "V49_EVIDENCED_LEVEL_STANDING", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: false, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, evidenced_level_standing: true } },
  ] : isV48 ? [
    { name: "V47_BASELINE", market_mode: "MARKET_UNION_REACH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: false, placement_ladder: "V47_INCUMBENT" } },
    { name: "TRADE_TRUTH_V47_INCUMBENT", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "V47_INCUMBENT" } },
    { name: "TRADE_TRUTH_BID_MINUS_ONE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "BID_MINUS_ONE" } },
    { name: "TRADE_TRUTH_BID", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "BID" } },
    { name: "TRADE_TRUTH_RECENT_TRADE", market_mode: "MARKET_TRADES_AS_TRUTH", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, placement_ladder: "LOWEST_RECENT_TRADED_LEVEL" } },
  ] : isV47 ? [
    { name: "V45_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: false } },
    { name: "V47_SAME_TICK_ARM", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true } },
  ] : isV46 ? [
    { name: "V45_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true } },
    { name: "V46_PAIR_GATED_GAP_CREDIT", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, pair_gated_gap_credit: true } },
  ] : isV45 ? [
    { name: "V43_BASELINE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true } },
    { name: "V45_GUARD_RELEASE_AT_SIBLING_CREDIT", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true } },
  ] : isV43 ? [
    { name: "V41_BASELINE", clauses: {} },
    { name: "C1_ARM_ONLY", clauses: { arm_at_first_evidence: true } },
    { name: "C2_GUARD_ONLY", clauses: { deep_gap_guard: true } },
    { name: "C3_LOOSEN_ONLY", clauses: { loosen_one_cent: true } },
    { name: "C1_C2_ARM_GUARD", clauses: { arm_at_first_evidence: true, deep_gap_guard: true } },
    { name: "C1_C3_ARM_LOOSEN", clauses: { arm_at_first_evidence: true, loosen_one_cent: true } },
    { name: "C2_C3_GUARD_LOOSEN", clauses: { deep_gap_guard: true, loosen_one_cent: true } },
    { name: "V43_ALL_THREE", clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true } },
  ] : [{ name: "PRIMARY", clauses: isV42 ? { deep_gap_guard: true } : {} }];
  const machineRuns = new Map(machineSpecs.map((spec) => [spec.name, { spec, marketEvents: [], strictEvents: [], actions: [], joinQualifications: [] }]));
  const printLoad = await loadPrints(tickerBounds), tapeHashes = {};
  let index = 0;
  for (const base of [...baseByEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    index += 1; if (index % 50 === 0) process.stderr.write(`${isV49 ? "V49x2" : isV48 ? "V48x5" : isV47 ? "V47x2" : isV46 ? "V46x2" : isV45 ? "V45x2" : isV43 ? "V43x8" : isV42 ? "V42" : isV41 ? "V41" : isV40 ? "V40" : isV39 ? "V39" : "V38"} replay ${index}/804\n`);
    const tapes = new Map(), prints = new Map();
    for (const [id, leg] of Object.entries(base.legs)) {
      const loaded = loadTape(leg.ticker); tapeHashes[leg.ticker] = { sha256: loaded.sha256, bytes: loaded.bytes };
      tapes.set(id, loaded.rows); prints.set(id, printLoad.byTicker.get(leg.ticker));
    }
    for (const spec of machineSpecs) {
      const marketMode = spec.market_mode || "MARKET_UNION_REACH";
      const run = machineRuns.get(spec.name), market = simulate(base, tapes, prints, marketMode, spec.clauses), strict = simulate(base, tapes, prints, "STRICT_PRINT_CROSS", spec.clauses);
      run.marketEvents.push(market.event); run.strictEvents.push(strict.event);
      for (const row of market.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
      for (const row of strict.joinQualifications) run.joinQualifications.push({ machine: spec.name, ...row });
      for (const row of market.actions) run.actions.push({ machine: spec.name, mode: marketMode, ...row });
      for (const row of strict.actions) run.actions.push({ machine: spec.name, mode: "STRICT_PRINT_CROSS", ...row });
    }
  }
  const primaryRun = machineRuns.get(isV49 ? "V49_EVIDENCED_LEVEL_STANDING" : isV48 ? "TRADE_TRUTH_V47_INCUMBENT" : isV47 ? "V47_SAME_TICK_ARM" : isV46 ? "V46_PAIR_GATED_GAP_CREDIT" : isV45 ? "V45_GUARD_RELEASE_AT_SIBLING_CREDIT" : isV43 ? "V43_ALL_THREE" : "PRIMARY"), marketEvents = primaryRun.marketEvents, strictEvents = primaryRun.strictEvents, allActions = primaryRun.actions;
  const marketScore = score(marketEvents), strictScore = score(strictEvents), marketGrades = gradeAgainstReach(marketEvents, reachByEvent, baseByEvent), strictGrades = gradeAgainstReach(strictEvents, reachByEvent, baseByEvent), v36Score = frozenV36Score(reachRows), v36NetScore = frozenV36NetScore(v36StrictFrozenEvents);
  ensure(v36NetScore.aggregate.taker_legs_charged === 882, "V36 taker-leg fee population changed");
  const v41LedgerPath = ".claude/window1_live_v4_replay/v41_maker_machine_20260808/MARKET_EVENT_LEDGER.jsonl.gz";
  const closeAuditPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
  const fullBookReceiptPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V41_FULL_BOOK_PNL.json";
  const deepGapCensusPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAP_UNFEASIBLE_CENSUS.json";
  const v41FrozenEvents = hasDeepGap ? readRows(path.join(repo, v41LedgerPath)) : null;
  const closeAuditBytes = hasDeepGap ? gitShow(FULL_BOOK_PNL_COMMIT, closeAuditPath) : null;
  const fullBookReceiptBytes = hasDeepGap ? gitShow(FULL_BOOK_PNL_COMMIT, fullBookReceiptPath) : null;
  const deepGapCensusBytes = hasDeepGap ? gitShow(DEEP_GAP_CENSUS_COMMIT, deepGapCensusPath) : null;
  const closeByTicker = new Map();
  if (hasDeepGap) {
    const parsed = parseCsv(closeAuditBytes.toString("utf8")), ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
    // a30f5ccd's full-book method intentionally prices only the frozen replay
    // close column.  The independently audited close column repairs 250
    // gradeability holes but is not the ruler used by the +782c receipt.
    for (const values of parsed.rows) {
      const raw = values[ix.replay_close_cents];
      closeByTicker.set(values[ix.ticker], /^\d+$/.test(raw) ? Number(raw) : null);
    }
    ensure(closeByTicker.size === 1608, `close audit count ${closeByTicker.size}`);
    ensure(v41FrozenEvents.length === 804, "frozen V41 event count changed");
  }
  const v41FullBook = hasDeepGap ? fullBookPnl(v41FrozenEvents, closeByTicker) : null;
  const v42FullBook = hasDeepGap ? fullBookPnl(marketEvents, closeByTicker) : null;
  const deepGapDiff = hasDeepGap ? deepGapDifferential(v41FrozenEvents, marketEvents, closeByTicker) : null;
  const fullBookFrozenReceipt = hasDeepGap ? JSON.parse(fullBookReceiptBytes) : null;
  const deepGapFrozenReceipt = hasDeepGap ? JSON.parse(deepGapCensusBytes) : null;
  const deepGapT10 = hasDeepGap ? deepGapFrozenReceipt.GUARD.sweep["T=10"] : null;
  if (hasDeepGap) {
    ensure(v41FullBook.aggregate.completed_pairs === 243 && v41FullBook.aggregate.completed_locked_cents === 732, "V41 completed-book reconstruction changed");
    ensure(v41FullBook.aggregate.naked_pnl_cents === 50 && v41FullBook.aggregate.naked_open === 63 && v41FullBook.aggregate.true_book_net_cents === 782, `V41 true-book reconstruction changed: ${JSON.stringify(v41FullBook.aggregate)}`);
    ensure(fullBookFrozenReceipt.TRUE_BOOK.NET_CENTS === 782 && fullBookFrozenReceipt.COMPLETED.pairs === 243, "a30f5ccd binding changed");
    ensure((-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents === 73, "645e035b T=10 binding changed");
  }
  const v42Acceptance = isV42 ? { completed_pairs: { value: marketScore.completed_pairs, minimum: 240, pass: marketScore.completed_pairs >= 240 }, true_book_net_cents: { value: v42FullBook.aggregate.true_book_net_cents, strict_minimum: 782, pass: v42FullBook.aggregate.true_book_net_cents > 782 } } : null;
  if (v42Acceptance) v42Acceptance.pass = v42Acceptance.completed_pairs.pass && v42Acceptance.true_book_net_cents.pass;
  const summarizeCategoryScores = (events) => Object.fromEntries([...new Set(events.map((event) => event.category))].sort().map((category) => {
    const cell = score(events.filter((event) => event.category === category));
    return [category, { D: cell.D, completed_pairs: cell.completed_pairs, under_par_pairs: cell.under_par_pairs, locked_cents_per_contract: cell.locked_cents_per_contract, frontier: cell.frontier }];
  }));
  const v48TradedFloors = isTradeTruthVariant ? tradedFloorCensus(baseByEvent, printLoad, reachByEvent) : null;
  const v48TradedFloorByLeg = isTradeTruthVariant ? new Map(v48TradedFloors.leg_rows.map((row) => [row.leg_identity, row])) : null;
  const attributionRows = isAttribution ? machineSpecs.map((spec) => {
    const run = machineRuns.get(spec.name), market = score(run.marketEvents), strict = score(run.strictEvents), fullBook = fullBookPnl(run.marketEvents, closeByTicker), tradeFloorGrade = isTradeTruthVariant ? gradeAgainstTradedFloors(run.marketEvents, v48TradedFloorByLeg) : null;
    return { machine: spec.name, market_mode: spec.market_mode || "MARKET_UNION_REACH", clauses: policy.normalizedClauses(spec.clauses), MARKET: market, MARKET_UNION_REACH: market, STRICT_PRINT_CROSS: strict, FULL_BOOK: fullBook.aggregate, TRADED_FLOOR_GRADE: tradeFloorGrade?.aggregate ?? null, category_x_bell_confidence: isTradeTruthVariant ? { MARKET: scorePartitions(run.marketEvents), STRICT_PRINT_CROSS: scorePartitions(run.strictEvents), TRADED_FLOOR_GRADE: tradeFloorGrade.category_x_bell_confidence } : null, by_category: { MARKET: summarizeCategoryScores(run.marketEvents), MARKET_UNION_REACH: summarizeCategoryScores(run.marketEvents), STRICT_PRINT_CROSS: summarizeCategoryScores(run.strictEvents), FULL_BOOK: fullBook.by_category }, full_book_rows: fullBook.rows, traded_floor_rows: tradeFloorGrade?.rows ?? null, traded_floor_games: tradeFloorGrade?.games ?? null };
  }) : null;
  const attributionByName = isAttribution ? new Map(attributionRows.map((row) => [row.machine, row])) : null;
  const v48BaselineReproduction = isV48 ? (() => {
    const row = attributionByName.get("V47_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET.completed_pairs, under_par_pairs: row.MARKET.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V47_commit: V47_COMMIT, expected, observed, pass };
  })() : null;
  const v49BaselineReproduction = isV49 ? (() => {
    const row = attributionByName.get("TRADE_TRUTH_V47_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET.completed_pairs, under_par_pairs: row.MARKET.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V47_commit: V47_COMMIT, scoring_ruler: "TRADES_AS_TRUTH", expected, observed, pass };
  })() : null;
  const v49Differential = isV49 ? ladderDifferential(machineRuns.get("TRADE_TRUTH_V47_BASELINE").marketEvents, machineRuns.get("V49_EVIDENCED_LEVEL_STANDING").marketEvents, closeByTicker, "V49_EVIDENCED_LEVEL_STANDING") : null;
  const v48LadderNames = isV48 ? ["TRADE_TRUTH_BID_MINUS_ONE", "TRADE_TRUTH_BID", "TRADE_TRUTH_RECENT_TRADE"] : [];
  const v48SelectedRung = isV48 ? [...v48LadderNames].sort((a, b) => {
    const x = attributionByName.get(a), y = attributionByName.get(b);
    return y.FULL_BOOK.true_book_net_cents - x.FULL_BOOK.true_book_net_cents || y.MARKET.completed_pairs - x.MARKET.completed_pairs || y.FULL_BOOK.completed_locked_cents - x.FULL_BOOK.completed_locked_cents || a.localeCompare(b);
  })[0] : null;
  const v48LadderDiffs = isV48 ? Object.fromEntries(v48LadderNames.map((name) => [name, ladderDifferential(machineRuns.get("TRADE_TRUTH_V47_INCUMBENT").marketEvents, machineRuns.get(name).marketEvents, closeByTicker, name)])) : null;
  const receiptReproduction = isV43 ? {
    V41_BASELINE: { expected: { completed_pairs: 243, locked_cents: 732, naked_pnl_cents: 50, true_book_net_cents: 782 }, observed: attributionByName.get("V41_BASELINE").FULL_BOOK },
    C1_ARM_ONLY: { expected: { completed_pairs: 313, locked_cents: 925, naked_pnl_cents: 76, true_book_net_cents: 1001, frontier: { LE_93: 17, LE_95: 39, LE_97: 95, LT_100: 313 } }, observed: { ...attributionByName.get("C1_ARM_ONLY").FULL_BOOK, frontier: attributionByName.get("C1_ARM_ONLY").MARKET_UNION_REACH.frontier } },
    C3_LOOSEN_ONLY: { expected: { completed_pairs: 281, locked_cents: 799, naked_pnl_cents: 34, true_book_net_cents: 833 }, observed: attributionByName.get("C3_LOOSEN_ONLY").FULL_BOOK },
    C2_GUARD_ONLY: { controlling_receipt_expected_net_improvement_cents: 73, observed: attributionByName.get("C2_GUARD_ONLY").FULL_BOOK, observed_net_improvement_cents: attributionByName.get("C2_GUARD_ONLY").FULL_BOOK.true_book_net_cents - 782 },
  } : null;
  if (receiptReproduction) {
    for (const row of Object.values(receiptReproduction)) {
      if (!row.expected) continue;
      row.pass = Object.entries(row.expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, expected]) => row.observed.frontier[tier] === expected) : row.observed[key === "locked_cents" ? "completed_locked_cents" : key] === value);
    }
    receiptReproduction.C2_GUARD_ONLY.pass = receiptReproduction.C2_GUARD_ONLY.observed_net_improvement_cents === 73;
  }
  const v43Acceptance = isV43 ? {
    completed_pairs: { value: attributionByName.get("V43_ALL_THREE").MARKET_UNION_REACH.completed_pairs, minimum: 313, pass: attributionByName.get("V43_ALL_THREE").MARKET_UNION_REACH.completed_pairs >= 313 },
    true_book_net_cents: { value: attributionByName.get("V43_ALL_THREE").FULL_BOOK.true_book_net_cents, strict_minimum: 1001, pass: attributionByName.get("V43_ALL_THREE").FULL_BOOK.true_book_net_cents > 1001 },
  } : null;
  const v45BaselineReproduction = isV45 ? (() => {
    const row = attributionByName.get("V43_BASELINE");
    const expected = { completed_pairs: 395, completed_locked_cents: 1910, naked_pnl_cents: -162, true_book_net_cents: 1748, strict_completed_pairs: 331, frontier: { LE_93: 51, LE_95: 70, LE_97: 141, LT_100: 395 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V43_commit: V43_COMMIT, expected, observed, pass };
  })() : null;
  const v45Acceptance = isV45 ? (() => {
    const row = attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT");
    return {
      baseline_reproduction: v45BaselineReproduction,
      completed_pairs: { value: row.MARKET_UNION_REACH.completed_pairs, minimum: 395, pass: row.MARKET_UNION_REACH.completed_pairs >= 395 },
      true_book_net_cents: { value: row.FULL_BOOK.true_book_net_cents, strict_minimum: 1748, pass: row.FULL_BOOK.true_book_net_cents > 1748 },
      naked_pnl_cents: { value: row.FULL_BOOK.naked_pnl_cents, strict_minimum: -162, pass: row.FULL_BOOK.naked_pnl_cents > -162 },
    };
  })() : null;
  const v46BaselineReproduction = isV46 ? (() => {
    const row = attributionByName.get("V45_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, under_par_pairs: row.MARKET_UNION_REACH.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V45_commit: V45_COMMIT, expected, observed, pass };
  })() : null;
  const v47BaselineReproduction = isV47 ? (() => {
    const row = attributionByName.get("V45_BASELINE");
    const expected = { completed_pairs: 396, under_par_pairs: 396, completed_locked_cents: 1936, naked_pnl_cents: -162, true_book_net_cents: 1774, strict_completed_pairs: 331, frontier: { LE_93: 52, LE_95: 71, LE_97: 142, LT_100: 396 } };
    const observed = { completed_pairs: row.MARKET_UNION_REACH.completed_pairs, under_par_pairs: row.MARKET_UNION_REACH.under_par_pairs, completed_locked_cents: row.FULL_BOOK.completed_locked_cents, naked_pnl_cents: row.FULL_BOOK.naked_pnl_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents, strict_completed_pairs: row.STRICT_PRINT_CROSS.completed_pairs, frontier: row.MARKET_UNION_REACH.frontier };
    const pass = Object.entries(expected).every(([key, value]) => key === "frontier" ? Object.entries(value).every(([tier, n]) => observed.frontier[tier] === n) : observed[key] === value);
    return { frozen_V45_commit: V45_COMMIT, expected, observed, pass };
  })() : null;
  const layerGroups = new Map();
  for (const row of marketGrades.residuals) { const key = row.layer_bind.owner; if (!layerGroups.has(key)) layerGroups.set(key, []); layerGroups.get(key).push(row); }
  const layerRanking = [...layerGroups].map(([owner, rows]) => ({ owner, games: new Set(rows.map((row) => row.event_id)).size, sides: rows.length, measurable_cents: rows.reduce((sum, row) => sum + (row.layer_bind.measurable_cents || 0), 0), category_x_bell_confidence: countBy(rows, (row) => `${row.category}|${row.bell_confidence}`) })).sort((a, b) => b.measurable_cents - a.measurable_cents || b.games - a.games || a.owner.localeCompare(b.owner));
  const namedLabels = isV49 ? ["HERKAZ", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV48 ? ["LUZTSE", "SALIBR", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV47 ? ["SURECH", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"] : isV46 ? ["PANFAL", "ARNROM", "KIRSEK", "KRUFER", "BOSCOP"] : isV45 ? ["LUZTSE", "COLCER", "SMIYUN", "VANLEE", "SAINUG", "PENTHA", "SHEOLI", "ARNROM", "KRUFER", "KIRSEK"] : isV43 ? ["KIRSEK", "ARNROM", "KRUFER", "BOSCOP", "PUTJEA", "BORDIM", "ROCBUE", "KREZHE"] : isV42 ? ["PUTJEA", "ROCBUE", "KREZHE", "BORDIM", "ARNROM"] : isV41 ? ["ARNROM", "BOSCOP", "NIKVRB", "WESPAA", "KRUFER"] : ["ARNROM", "BOSCOP", "WESPAA", "NIKVRB", "GANJAN"];
  const named = {};
  for (const label of namedLabels) {
    const market = marketEvents.find((event) => event.event_id.includes(label)), strict = strictEvents.find((event) => event.event_id.includes(label));
    ensure(market && strict, `named game absent ${label}`);
    const reach = reachByEvent.get(market.event_id), reachLevels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const legView = (event) => Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_rest_cents: leg.resting_target_at_edge_cents, final_causal_state: leg.last_combined_state, persistent_join_level_cents: leg.persistent_join_level, persistent_join_timestamp_epoch: leg.persistent_join_timestamp_epoch, persistent_join_book_last_trade_receipts: leg.persistent_join_book_last_trade_receipts, persistent_join_certified_seller_aggressed_prints: leg.persistent_join_certified_seller_aggressed_prints, persistent_join_evidence_receipt: leg.persistent_join_evidence_receipt, post_join_book_last_trade_receipts: leg.post_join_book_last_trade_receipts, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level, sanity_bound_receipts: leg.sanity_bound_rows, sanity_violations: leg.sanity_violation_rows }]));
    named[label] = { event_id: market.event_id, reach_levels: Object.fromEntries(Object.entries(reach.legs).map(([id, leg]) => [id, leg.union_reach_cents])), reach_combined_cents: reachLevels.every(Number.isInteger) ? reachLevels.reduce((a, b) => a + b, 0) : null, MARKET_UNION_REACH: { completed: market.completed_pair, combined_entry_cents: market.combined_entry_cents, under_par: market.pair_under_par, legs: legView(market) }, STRICT_PRINT_CROSS: { completed: strict.completed_pair, combined_entry_cents: strict.combined_entry_cents, under_par: strict.pair_under_par, legs: legView(strict) } };
  }
  if (!isV42 && !isAttribution) ensure(named.ARNROM.reach_combined_cents === 88 && named.BOSCOP.reach_combined_cents === 75 && named.NIKVRB.reach_combined_cents === 86, "named reach identities changed");
  const namedAttribution = isAttribution ? Object.fromEntries(machineSpecs.map((spec) => {
    const run = machineRuns.get(spec.name), gameRows = {};
    for (const label of namedLabels) {
      const market = run.marketEvents.find((event) => event.event_id.includes(label)), strict = run.strictEvents.find((event) => event.event_id.includes(label));
      gameRows[label] = { event_id: market.event_id, MARKET_UNION_REACH: { completed: market.completed_pair, combined_entry_cents: market.combined_entry_cents, under_par: market.pair_under_par, legs: Object.fromEntries(Object.entries(market.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason }])) }, STRICT_PRINT_CROSS: { completed: strict.completed_pair, combined_entry_cents: strict.combined_entry_cents, under_par: strict.pair_under_par } };
    }
    return [spec.name, gameRows];
  })) : null;
  const policyFile = path.join(repo, isV49 ? "arb-executor/analysis/window1_v49_evidenced_level_standing.js" : isV48 ? "arb-executor/analysis/window1_v48_trades_as_truth.js" : isV47 ? "arb-executor/analysis/window1_v47_same_tick_arm.js" : isV46 ? "arb-executor/analysis/window1_v46_pair_gated_gap_credit.js" : isV45 ? "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js" : isV43 ? "arb-executor/analysis/window1_v43_composed_machine.js" : isV42 ? "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "arb-executor/analysis/window1_v41_maker_machine.js" : isV40 ? "arb-executor/analysis/window1_v40_incumbent_direction_placement_stack.js" : isV39 ? "arb-executor/analysis/window1_v39_corrected_placement_stack.js" : "arb-executor/analysis/window1_v38_maker_only_machine.js"), builderFile = __filename;
  const wrapperFile = path.join(repo, isV49 ? "arb-executor/analysis/build_window1_v49_evidenced_level_standing.js" : isV48 ? "arb-executor/analysis/build_window1_v48_trades_as_truth.js" : isV47 ? "arb-executor/analysis/build_window1_v47_same_tick_arm.js" : isV46 ? "arb-executor/analysis/build_window1_v46_pair_gated_gap_credit.js" : isV45 ? "arb-executor/analysis/build_window1_v45_guard_release_sibling_credit.js" : isV43 ? "arb-executor/analysis/build_window1_v43_composed_machine.js" : isV42 ? "arb-executor/analysis/build_window1_v42_deep_gap_feasibility_guard.js" : isV41 ? "arb-executor/analysis/build_window1_v41_maker_machine.js" : isV40 ? "arb-executor/analysis/build_window1_v40_incumbent_direction_placement_stack.js" : "arb-executor/analysis/build_window1_v39_corrected_placement_stack.js");
  const policyText = fs.readFileSync(policyFile, "utf8");
  const makerPolicyLineageText = hasDeepGap ? `${fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js"), "utf8")}\n${isAttribution ? fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js"), "utf8") : ""}\n${policyText}` : policyText;
  if (!isPlacementStack || isMaker41) ensure(!/action:\s*["']TAKE["']/.test(policyText) && !/function\s+.*take/i.test(policyText) && !/matureFloorTakePermission/.test(policyText), `take path survived in ${variant.toUpperCase()} policy`);
  if (isV39) ensure(/V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED/.test(policyText), "V36 take path missing from V39");
  if (isV40) {
    ensure(!/window1_v39|agreementWeightedDirection/.test(policyText), "V39 classifier survived in V40 policy");
    ensure(/MATURE_EVIDENCE_FLOOR_TAKE/.test(policyText), "V36 take path missing from V40");
  }
  if (isMaker41) {
    ensure(!/window1_v39|window1_v40|action:\s*["']TAKE["']|matureFloorTakePermission/.test(makerPolicyLineageText), "V41/V42 imported a forbidden classifier or take path");
    ensure(/PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1/.test(makerPolicyLineageText), "V41 persistence-only join authority absent");
    ensure(policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState, "V41 state machine is not V36 incumbent");
  }
  if (hasDeepGap) {
    ensure(policy.DEEP_GAP_TOLERANCE_CENTS === 10, "V42 tolerance changed");
    if (isV42) ensure(policy.placementTarget === require("./window1_v41_maker_machine.js").placementTarget, "V42 changed V41 placement target law");
  }
  if (isAttribution) {
    ensure(!/walk[_ -]?lag/i.test(policyText), "V43 imported excluded walk-lag removal");
    ensure(policy.normalizedClauses({}).arm_at_first_evidence === false, "V43 clause defaults are not all off");
    ensure(policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState, "V43 changed V41/V36 state machine");
  }
  const causalReachPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAUSAL_REACH.json";
  const riserFrontierPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_TRIGGER_FRONTIER.json";
  const levelPolicyPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LEVEL_POLICY_REALIZATION.json";
  const armFirstEvidencePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CONVICTION_LAG_REMOVAL.json";
  const loosenOneCentPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/FLOW_ABOVE_REST_LOOSENING_SWEEP.json";
  const causalReachBytes = isMaker41 ? gitShow(CAUSAL_REACH_COMMIT, causalReachPath) : null;
  const riserFrontierBytes = isMaker41 ? gitShow(RISER_FRONTIER_COMMIT, riserFrontierPath) : null;
  const levelPolicyBytes = isMaker41 ? gitShow(LEVEL_POLICY_COMMIT, levelPolicyPath) : null;
  const causalReachReceipt = isMaker41 ? JSON.parse(causalReachBytes) : null;
  const riserFrontierReceipt = isMaker41 ? JSON.parse(riserFrontierBytes) : null;
  const levelPolicyReceipt = isMaker41 ? JSON.parse(levelPolicyBytes) : null;
  const armFirstEvidenceBytes = isAttribution ? gitShow(ARM_FIRST_EVIDENCE_COMMIT, armFirstEvidencePath) : null;
  const loosenOneCentBytes = isAttribution ? gitShow(LOOSEN_ONE_CENT_COMMIT, loosenOneCentPath) : null;
  const armFirstEvidenceReceipt = isAttribution ? JSON.parse(armFirstEvidenceBytes) : null;
  const loosenOneCentReceipt = isAttribution ? JSON.parse(loosenOneCentBytes) : null;
  const v43RecalibrationPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_COMPOSITION_RECALIBRATION.json";
  const v43DocketPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_RESIDUAL_DOCKET.json";
  const luztseMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v43_docket/26JUL18LUZTSE_DECISION_MARKS.json";
  const luztseTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v43_docket/26JUL18LUZTSE_DUAL_TIMELINE_V2.csv";
  const v43RecalibrationBytes = isV45 ? gitShow(V43_RECALIBRATION_COMMIT, v43RecalibrationPath) : null;
  const v43DocketBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, v43DocketPath) : null;
  const luztseMarksBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, luztseMarksPath) : null;
  const luztseTimelineBytes = isV45 ? gitShow(V43_RESIDUAL_DOCKET_COMMIT, luztseTimelinePath) : null;
  const strictAskFootprintPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STRICT_ASK_CREDIT_FOOTPRINT.json";
  const strictAskFootprintMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STRICT_ASK_CREDIT_FOOTPRINT.md";
  const panfalMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v45_docket/26JUL13PANFAL_DECISION_MARKS.json";
  const panfalTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/v45_docket/26JUL13PANFAL_DUAL_TIMELINE_V2.csv";
  const strictAskFootprintBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, strictAskFootprintPath) : null;
  const strictAskFootprintMdBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, strictAskFootprintMdPath) : null;
  const panfalMarksBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, panfalMarksPath) : null;
  const panfalTimelineBytes = isV46 ? gitShow(STRICT_ASK_FOOTPRINT_COMMIT, panfalTimelinePath) : null;
  const strictAskFootprint = isV46 ? JSON.parse(strictAskFootprintBytes) : null;
  const frozenV45ControlPath = ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809/CONTROL_BINDING.json";
  const frozenV45ScorePath = ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809/ATTRIBUTION_SCORECARD.json";
  const frozenV45PolicyPath = "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js";
  const frozenV45ControlBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45ControlPath) : null;
  const frozenV45ScoreBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45ScorePath) : null;
  const frozenV45PolicyBytes = (isV46 || isV47) ? gitShow(V45_COMMIT, frozenV45PolicyPath) : null;
  const surechMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/l4_archetype/SURECH_DECISION_MARKS.json";
  const surechTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/l4_archetype/SURECH_DUAL_TIMELINE_V2.csv";
  const surechMarksBytes = isV47 ? gitShow(SURECH_RENDER_COMMIT, surechMarksPath) : null;
  const surechTimelineBytes = isV47 ? gitShow(SURECH_RENDER_COMMIT, surechTimelinePath) : null;
  const tradesTruthRecutPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_316_RECUT.json";
  const tradesTruthRecutMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_316_RECUT.md";
  const tradesTruthRecutBytes = isV48 ? gitShow(TRADES_TRUTH_RECUT_COMMIT, tradesTruthRecutPath) : null;
  const tradesTruthRecutMdBytes = isV48 ? gitShow(TRADES_TRUTH_RECUT_COMMIT, tradesTruthRecutMdPath) : null;
  const tradesTruthRecut = isV48 ? JSON.parse(tradesTruthRecutBytes) : null;
  const standabilityPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STANDABILITY_V2_PLACEMENT_WINDOW.json";
  const standabilityMdPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/STANDABILITY_V2_PLACEMENT_WINDOW.md";
  const herkazPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/WLE_TOP_EXEMPLAR.json";
  const herkazMarksPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/wle_top/26JUL12HERKAZ_DECISION_MARKS.json";
  const herkazTimelinePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/wle_top/26JUL12HERKAZ_DUAL_TIMELINE_V2.csv";
  const standabilityBytes = isV49 ? gitShow(STANDABILITY_V2_COMMIT, standabilityPath) : null;
  const standabilityMdBytes = isV49 ? gitShow(STANDABILITY_V2_COMMIT, standabilityMdPath) : null;
  const herkazBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazPath) : null;
  const herkazMarksBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazMarksPath) : null;
  const herkazTimelineBytes = isV49 ? gitShow(HERKAZ_EXEMPLAR_COMMIT, herkazTimelinePath) : null;
  const standabilityReceipt = isV49 ? JSON.parse(standabilityBytes) : null;
  const herkazReceipt = isV49 ? JSON.parse(herkazBytes) : null;
  if (isMaker41) {
    ensure(causalReachReceipt.CAUSAL_REACH.under_par === 504 && causalReachReceipt.CAUSAL_REACH.locked === 3319, "causal reach binding changed");
    ensure(riserFrontierReceipt.per_trigger.T4_persist300.under_par === 631, "persistence-only trigger frontier changed");
    ensure(levelPolicyReceipt.per_policy.P2_join.under_par === 480, "P2 realization binding changed");
  }
  if (isAttribution) {
    ensure(armFirstEvidenceReceipt.rows.ARM.completed === 313 && armFirstEvidenceReceipt.rows.ARM.true_book === 1001, "9ddfe8c6 ARM binding changed");
    ensure(loosenOneCentReceipt.per_k["k=1"].completed === 281 && loosenOneCentReceipt.per_k["k=1"].true_book === 833, "52275c9d +1c binding changed");
  }
  if (isV46) {
    ensure(strictAskFootprint.FOOTPRINT?.total === 50, "aa884cc5 footprint leg count changed");
    ensure(strictAskFootprint.FOOTPRINT?.by_chain_link?.CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY === 42, "aa884cc5 L6 footprint changed");
    ensure(strictAskFootprint.THE_FIX?.ADVERSE?.naked_unfrozen_legs === 11 && strictAskFootprint.THE_FIX?.ADVERSE?.naked_only_distribution?.median === 44, "aa884cc5 naked-knife binding changed");
    ensure(shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), "V45 inherited Git-normalized policy bytes differ from 3bda0a54");
    ensure(JSON.parse(frozenV45ControlBytes).schema_version === "window1-v45-guard-release-sibling-credit-control-v1", "V45 frozen control binding changed");
  }
  if (isV47) {
    ensure(shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), "V45 inherited Git-normalized policy bytes differ from 3bda0a54");
    ensure(JSON.parse(frozenV45ControlBytes).schema_version === "window1-v45-guard-release-sibling-credit-control-v1", "V45 frozen control binding changed");
    ensure(JSON.parse(surechMarksBytes).event === "KXATPCHALLENGERMATCH-26JUL14SURECH", "SURECH render identity changed");
  }
  if (isV48) {
    ensure(tradesTruthRecut.population?.L6_legs_recut === 342, "e995c81b re-cut leg population changed");
    ensure(tradesTruthRecut.verdicts?.REST_AT_AVAILABLE + tradesTruthRecut.verdicts?.REST_BELOW_AVAILABLE === 330, "e995c81b real-offer population changed");
    ensure(!Object.hasOwn(tradesTruthRecut.channel_that_set_lowest || {}, "SELLER_CROSS"), "e995c81b unexpectedly contains seller-cross as a lowest channel");
  }
  if (isV49) {
    ensure(standabilityReceipt.recoverable_under_window_law.games === 81 && standabilityReceipt.recoverable_under_window_law.locked_cents === 1162, "fe4747cd window-law target changed");
    ensure(standabilityReceipt.conservation.the_46_analyzed === 46 && standabilityReceipt.conservation.WINDOW_LAWFUL_EVIDENCE === 20, "fe4747cd placement-window recut changed");
    ensure(herkazReceipt.game === "26JUL12HERKAZ" && herkazReceipt.P_evidenced_level === 46 && herkazReceipt.completing_print.price === 46, "b9673399 HERKAZ fingerprint changed");
  }
  const control = isV49
    ? { schema_version: "window1-v49-evidenced-level-standing-control-v1", base: V47_COMMIT, frozen_V47: V47_COMMIT, controlling_receipts: [STANDABILITY_V2_COMMIT, HERKAZ_EXEMPLAR_COMMIT, LOOSEN_ONE_CENT_COMMIT], architecture: { change: "UNIVERSAL_PLUS_ONE_REPLACED_BY_CAUSAL_EVIDENCE_CONDITIONAL_STAND_AT_P", lawful_level_evidence: ["STRICTLY_EARLIER_TRUE_TRADE_AT_OR_BELOW_P", `OWN_BEST_BID_CONTINUOUSLY_STANDING_AT_P_FOR_INHERITED_${policy.PERSISTENT_LEVEL_SECONDS}_SECONDS`], inherited_standing_constant: { seconds: policy.PERSISTENT_LEVEL_SECONDS, provenance: "V47_PERSISTENCE_ONLY_JOIN_LAW" }, historical_bid_sighting_alone: "NO_AUTHORITY", effect: "TRACKING_REST_STANDS_AT_P_INSTEAD_OF_P_MINUS_ONE", no_evidence: "V41_BID_MINUS_ONE_OR_JOIN_INCUMBENT_PATH", untouched: ["PERSISTENT_JOIN", "WTA_OTHER_EXPRESSION_HOLD", "PAIR_CAP", "POST_ONLY_SANITY", "DEEP_GAP_GUARD", "SIBLING_CREDIT_RELEASE", "SAME_TICK_ARM", "HARD_PREBELL_EDGE"], clocks_as_decision_inputs: [] }, acceptance_bar: { zero_bound_named_regressions: true, HERKAZ_completes_HER_at_or_better_46: true, aggregate_target: null }, fill_rulers: { market_scoring: "ANY_TRUE_TRADE_AT_OR_BELOW_PRIOR_LAWFUL_REST", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } }
    : isV48
    ? { schema_version: "window1-v48-trades-as-truth-control-v1", base: V47_COMMIT, frozen_V47: V47_COMMIT, controlling_receipts: [TRADES_TRUTH_RECUT_COMMIT], architecture: { law_change: "A_STANDING_REST_CREDITS_ON_ANY_TRUE_TRADE_PRINT_AT_OR_BELOW_ITS_LEVEL_AFTER_THE_REST_STOOD", excluded_credit_filters: ["ASK", "QUOTE_TOUCH", "AGGRESSOR_SIDE", "DWELL", "SIZE", "ARRIVAL_DIRECTION", "CHANNEL_TAXONOMY"], asks_role: "PLACEMENT_ONLY_NEVER_CREDIT_OR_FLOOR", lawful_span: "V47_HARD_PREBELL_EDGE_UNCHANGED", strict_ruler: "V47_STRICT_PRINT_CROSS_BUILD_VERIFICATION_ONLY", placement_attribution: ["V47_INCUMBENT", "BID_MINUS_ONE", "BID", "LOWEST_TRUE_TRADE_TRAILING_300S"], placement_honesty: "V47_INCUMBENT_IS_A_MIXED_OPERATIVE_STACK_AND_IS_NOT_RELABELLED_BID_MINUS_ONE", clocks_as_decision_inputs: [] }, acceptance_bar: { zero_bound_named_regressions: true, aggregate_target: null, gains_reported_as_observed: true }, fill_rulers: { market_scoring: "ANY_TRUE_TRADE_AT_OR_BELOW_PRIOR_LAWFUL_REST", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } }
    : isV46
    ? { schema_version: "window1-v46-pair-gated-gap-credit-control-v1", base: V45_COMMIT, frozen_V45: V45_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [STRICT_ASK_FOOTPRINT_COMMIT], architecture: { incumbent: "V45_BYTE_IDENTICAL_EXCEPT_ONE_PAIR_GATED_GAP_CREDIT_CLAUSE", incumbent_clause: "FALLING_NO_CHASE_STRICT_ASK_CREDIT", additional_credit_event: "SINGLE_RECEIPT_ASK_GAP_GE_3_CENTS", authorization: "OTHER_EXPRESSION_ALREADY_CREDITED", authorized_effect: "REPRICE_EXISTING_FALLING_REST_DOWN_TO_MIN_CURRENT_ASK_MINUS_1_PAIR_CAP", sibling_not_credited: "V45_ACTION_STREAM_UNCHANGED", fill_credit: "INHERITED_MARKET_UNION_OR_STRICT_LATER_RECEIPT_ONLY_NO_SAME_RECEIPT_FABRICATION", pair_cap: "V45_UNCHANGED", sanity_bound: "REST_STRICTLY_BELOW_CURRENT_BEST_ASK", clocks_as_decision_inputs: [], hard_prebell_edge: "V45_UNCHANGED", take_path: "DELETED_IN_V41" }, acceptance_bar: { completed_pairs_min: 396, true_book_net_cents_strictly_greater_than: 1774, zero_bound_regressions: true, PANFAL_at_or_better_92_and_locked_min_8: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV47
    ? { schema_version: "window1-v47-same-tick-arm-control-v1", base: V45_COMMIT, frozen_V45: V45_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [SURECH_RENDER_COMMIT], architecture: { incumbent: "V45_BYTE_IDENTICAL_EXCEPT_EXPLICIT_ATOMIC_RECEIPT_PIPELINE", fix: "JOIN_QUALIFICATION_AND_PLACEMENT_DECISION_EXECUTE_IN_ONE_RECEIPT_LOCAL_CALL", qualification_law: "V45_UNCHANGED", persistence_level_definition: "V45_UNCHANGED", target_guard_cap_sanity_fill_and_edge_laws: "V45_UNCHANGED", scheduler_latency_after_qualification: 0, clocks_as_decision_inputs: [], hard_prebell_edge: "V45_UNCHANGED", take_path: "DELETED_IN_V41" }, evidence_scope: { SURECH_render_role: "OLDER_L4_ARCHETYPE_EVIDENCE_NOT_A_FROZEN_V45_DECISION_TRACE", executable_SEG_C_footprint: "V45_VS_V47_WHOLE_804" }, acceptance_bar: { V45_reproduced: true, zero_named_regressions: true, aggregate_gain_required: false }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV45
    ? { schema_version: "window1-v45-guard-release-sibling-credit-control-v1", base: V43_COMMIT, frozen_V43: V43_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [V43_RESIDUAL_DOCKET_COMMIT, V43_RECALIBRATION_COMMIT, DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT], architecture: { incumbent: "V43_BYTE_IDENTICAL_EXCEPT_ONE_POST_CREDIT_GUARD_AUTHORITY_TERMINATION", pre_fill_deep_gap_guard: "V43_T10_REMAINS_ACTIVE_UNCHANGED", release_trigger: "OTHER_EXPRESSION_CREDITED", release_effect: "ACTIVE_DEEP_GAP_WITHHOLD_TERMINATES_AND_REST_POSTS_IMMEDIATELY_AT_V43_LAWFUL_LEVEL", fixed_pair_cap: "99_MINUS_CREDITED_SIBLING_ENTRY", sanity_bound: "V43_REST_STRICTLY_BELOW_CURRENT_BEST_ASK_UNCHANGED", clocks_as_decision_inputs: [], hard_prebell_edge: "V43_UNCHANGED", take_path: "DELETED_IN_V41" }, acceptance_bar: { completed_pairs_min: 395, true_book_net_cents_strictly_greater_than: 1748, naked_pnl_cents_strictly_greater_than: -162, named_at_or_better_and_scope_checks: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV43
    ? { schema_version: "window1-v43-composed-machine-control-v1", parent: V41_COMMIT, frozen_V41: V41_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [ARM_FIRST_EVIDENCE_COMMIT, DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT, LOOSEN_ONE_CENT_COMMIT], architecture: { incumbent: "V41_BYTE_IDENTICAL_EXCEPT_EXPLICIT_RECEIPT_PRICED_CLAUSE_COMBINATIONS", clause_1: "RISING_PERSISTED_LEVEL_JOINABLE_FROM_FIRST_OBSERVATION_NO_300S_NO_SELLER_HIT_NO_SECOND_VISIT", excluded_from_clause_1: "WALK_LAG_REMOVAL_HELD_NOT_INCLUDED", clause_2: "REST_AT_L_UNLAWFUL_IFF_99_MINUS_L_IS_STRICTLY_LESS_THAN_SIBLING_CONTEMPORANEOUS_BEST_ASK_MINUS_10", clause_3: "TRACKING_REST_MIN_BEST_BID_PAIR_CAP_BEST_ASK_MINUS_1", pairwise_and_combined_attribution: true, take_path: "DELETED_IN_V41", pair_cap: "V41_UNCHANGED", clocks_as_decision_inputs: [], hard_prebell_edge: "V41_UNCHANGED" }, acceptance_bar: { true_book_net_cents_strictly_greater_than: 1001, completed_pairs_min: 313, zero_named_regressions: true }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV42
    ? { schema_version: "window1-v42-deep-gap-feasibility-guard-control-v1", parent: V41_COMMIT, frozen_V41: V41_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_COMMIT, CAUSAL_REACH_COMMIT, RISER_FRONTIER_COMMIT, LEVEL_POLICY_COMMIT], architecture: { incumbent: "V41_BYTE_IDENTICAL_EXCEPT_ONE_RECEIPT_CAUSAL_FEASIBILITY_CLAUSE", clause: "REST_AT_L_UNLAWFUL_IFF_99_MINUS_L_IS_STRICTLY_LESS_THAN_SIBLING_CONTEMPORANEOUS_BEST_ASK_MINUS_10", tolerance_cents: policy.DEEP_GAP_TOLERANCE_CENTS, reevaluation: "EVERY_OWN_BOOK_RECEIPT_AND_EVERY_SIBLING_BOOK_RECEIPT_WHILE_WITHHELD", lift: "THE_MOMENT_SIBLING_ASK_MINUS_IMPLIED_CAP_IS_LE_10", missing_sibling_book: "NO_GUARD_AUTHORITY_V41_UNCHANGED", clocks_as_decision_inputs: [], take_path: "DELETED_IN_V41", hard_prebell_edge: "V41_UNCHANGED" }, acceptance_bar: { true_book_net_cents_strictly_greater_than: 782, completed_pairs_min: 240 }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS", build_verification: "STRICT_PRINT_CROSS", never_swapped: true } }
    : isV41
    ? { schema_version: "window1-v41-maker-machine-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [CAUSAL_REACH_COMMIT, RISER_FRONTIER_COMMIT, LEVEL_POLICY_COMMIT, COUNTERFACTUAL_COMMIT], architecture: { entry_unit: "ONE_GAME_STATE_TWO_SINGLE_REST_OUTPUTS", T5_arming: "EVERY_LEG_PLACES_FROM_FIRST_TWO_SIDED_BOOK_WITH_NO_PRE_PLACEMENT_EVIDENCE_GATE", direction: "V36_INCUMBENT_QUOTE_PATH_PLUS_JUL6_PRESSURE_STATE_MACHINE", FALLING: "V36_CAUSAL_NO_CHASE_WALKING_REST", SETTLED: "V36_BID_MINUS_ONE_TRACKING", RISING: `BID_MINUS_ONE_TRACKER_UNTIL_CURRENT_BID_LEVEL_PERSISTS_${policy.PERSISTENT_LEVEL_SECONDS}S_THEN_SINGLE_REST_JOINS_DEEPEST_PERSISTENT_LEVEL; SELLER_HIT_NOT_REQUIRED; P2_OVERRIDES_P1`, WTA_inverse_falling_hold: "WTA_RISING_SIDE_WITH_OTHER_EXPRESSION_FALLING_HOLDS_DEEPER_CAUSAL_OWN_LEVEL", sanity_bound: "REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "DELETED_NOT_GATED", pair_cap: "99_MINUS_FIRST_FILL_LAZY_LEG_1", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "CANON_UNION_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true }, comparison: { V36_gross: "FROZEN_STRICT_EVENT_LEDGER", V36_net: "TAKER_PER_CONTRACT_CEIL_0_07_P_1_MINUS_P; MAKER_ZERO", causal_reach: { under_par: 504, locked_cents: 3319 } } }
    : isV40
    ? { schema_version: "window1-v40-incumbent-direction-placement-stack-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [COUNTERFACTUAL_COMMIT, "2c54d724186d2f8b152205379aef88499c457a7a", FALLER_ANATOMY_COMMIT, "ff5880d11a88b0d12415f5371d7cbb61331957e4"], architecture: { direction: "V36_INCUMBENT_QUOTE_PATH_PLUS_JUL6_PRESSURE_STATE_MACHINE_BYTE_FOR_FUNCTION_INHERITED", classifier_research_status: "V39_CAUSAL_CLASSIFIER_SEVERED_CLASSIFIER_RESEARCH_OPEN", persistent_level_join: `V36_INCUMBENT_RISING_CURRENT_BID_RESIDENCY_GE_${policy.PERSISTENT_LEVEL_SECONDS}S_AND_LAST_TRADED_AT_LEVEL_THEN_REST_AT_LEVEL`, WTA_inverse_falling_hold: "WTA_V36_INCUMBENT_RISING_SIDE_ONLY_DEEPER_OF_TRAILING_PULSE_FLOOR_AND_CAUSAL_RUNNING_OWN_REACH_LOW", sanity_bound: "EVERY_REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "V36_MATURE_FLOOR_TAKE_INTACT", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, acceptance_bar: { completed_pairs_min: 270, LE_93_min: 12, LE_95_min: 24 }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST_PLUS_PROVEN_TAKER", never_swapped: true } }
    : isV39
    ? { schema_version: "window1-v39-corrected-placement-stack-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [COUNTERFACTUAL_COMMIT, "2c54d724186d2f8b152205379aef88499c457a7a", FALLER_ANATOMY_COMMIT], architecture: { causal_direction: "DECISION_TIME_QUOTE_PATH_PLUS_JUL6_PRESSURE_AGREEMENT_WEIGHTED; OPPOSED_DIRECTIONAL_VOTES_SETTLE; NO_EX_POST_LABEL_INPUT", persistent_level_join: `RISING_CURRENT_BID_RESIDENCY_GE_${policy.PERSISTENT_LEVEL_SECONDS}S_AND_SELLER_HIT_AT_LEVEL_THEN_REST_AT_LEVEL`, WTA_inverse_falling_hold: "WTA_RISING_SIDE_ONLY_DEEPER_OF_TRAILING_PULSE_FLOOR_AND_CAUSAL_RUNNING_OWN_REACH_LOW", sanity_bound: "EVERY_REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "V36_MATURE_FLOOR_TAKE_INTACT", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST_PLUS_PROVEN_TAKER", never_swapped: true } }
    : { schema_version: "window1-v38-maker-only-control-v1", parent: GAP_COMMIT, frozen_V36: V36_COMMIT, frozen_union_reach: REACH_COMMIT, sealed_divot_census: DIVOT_COMMIT, architecture: { entry_actions: ["PLACE_REST", "REPRICE_REST"], take_path: "REMOVED_FROM_POLICY_SOURCE_NOT_GATED", FALLING: "V36_NO_CHASE_WALKING_REST_UNCHANGED", RISING: `REST_AT_LOWEST_ASK_LEVEL_WITH_AT_LEAST_${policy.PULSE_REVISIT_MIN}_DISTINCT_VISITS_INSIDE_EXISTING_${policy.LOOKBACK_SECONDS}S_RECEIPT_HORIZON; POST_ONLY_REQUIRES_STANDING_ASK_ABOVE_NEW_REST`, SETTLED: "BID_MINUS_ONE_TRACKING", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } };
  const pulseBinding = { commit: DIVOT_COMMIT, path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json", source_sha256: fileHash(path.join(reachRoot, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json")), adopted: { ask_side_dwell_10s_depth_median_cents: 1, ask_side_dwell_10s_depth_p90_cents: 2, trailing_horizon_seconds: policy.LOOKBACK_SECONDS, minimum_distinct_level_visits: policy.PULSE_REVISIT_MIN }, causal_revisit_definition: "ASK_LEVEL_ENTRY_AFTER_A_DIFFERENT_PRIOR_ASK; UNCHANGED RECORDER SNAPSHOTS DO_NOT INCREMENT VISITS" };
  const directionTelemetry = isV39 ? classifierTelemetry(marketEvents) : null;
  const counterPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PLACEMENT_LAW_COUNTERFACTUAL_V2.json";
  const counterBytes = isPlacementStack ? gitShow(COUNTERFACTUAL_COMMIT, counterPath) : null;
  const counterReceipt = isPlacementStack ? JSON.parse(counterBytes) : null;
  const anatomyPath = ".claude/window1_live_v4_replay/v36_faller_side_mirror_anatomy_20260807/FALLER_ISSUE_ANATOMY_399.jsonl.gz";
  const anatomyBytes = isV39 ? gitShow(FALLER_ANATOMY_COMMIT, anatomyPath) : null;
  const anatomyMislabels = isV39 ? readRowsBytes(anatomyBytes).filter((row) => row.miss_taxonomy?.class === "STATE_MISLABELED") : [];
  const marketLegByIdentity = new Map(marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
  const reconstructedRecovery = anatomyMislabels.map((row) => {
    const identity = `${row.event_id}|${row.leg_id}`, leg = marketLegByIdentity.get(identity);
    return { event_id: row.event_id, leg_identity: identity, frozen_ex_post_direction: String(row.miss_taxonomy.reason).split(" was ").at(-1), v36_credited: row.v36_credited, v36_entry_cents: row.v36_entry_cents, union_reach_cents: row.reach_bottom_cents, v39_credited: Boolean(leg?.credited), v39_entry_cents: leg?.entry_cents ?? null, recovered_at_or_better_than_reach: Boolean(leg?.credited && Number.isInteger(row.reach_bottom_cents) && leg.entry_cents <= row.reach_bottom_cents) };
  });
  const mislabelRecovery = isV39 ? { controlling_counterfactual_denominator: counterReceipt.faller_mislabel.measured_ran_faller_on_nonfaller, controlling_counterfactual_forfeited: counterReceipt.faller_mislabel.forfeited, controlling_counterfactual_credited: counterReceipt.faller_mislabel.credited, identity_binding_status: "NOT_BOUND_IN_2B45D146_AGGREGATE_RECEIPT_SO_NO_FALSE_115_SIDE_NUMERATOR_IS_EMITTED", independently_reconstructable_c396_cohort: { sides: reconstructedRecovery.length, recovered_credited: reconstructedRecovery.filter((row) => row.v39_credited && !row.v36_credited).length, recovered_at_or_better_than_reach: reconstructedRecovery.filter((row) => row.recovered_at_or_better_than_reach && !row.v36_credited).length }, telemetry_law: "FROZEN_EX_POST_DIRECTION_USED_ONLY_AFTER_REPLAY; NEVER_PASSED_TO_POLICY" } : null;
  const marketLegs = marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, category: event.category, bell_confidence: event.bell_confidence })));
  const sanity = isPlacementStack ? { legs: marketLegs.length, bound_application_receipts: marketLegs.reduce((sum, leg) => sum + leg.sanity_bound_rows, 0), post_decision_rest_at_or_above_ask_violations: marketLegs.reduce((sum, leg) => sum + leg.sanity_violation_rows, 0), legs_with_violation: marketLegs.filter((leg) => leg.sanity_violation_rows > 0).length, violations_by_category_x_bell_confidence: countBy(marketLegs.filter((leg) => leg.sanity_violation_rows > 0), (leg) => `${leg.category}|${leg.bell_confidence}`) } : null;
  const v36Comparison = isPlacementStack ? { frozen_commit: V36_COMMIT, frozen_gross_score: v36Score, frozen_net_of_taker_fee_score: v36NetScore, V41_maker_fee: isMaker41 ? { maker_fills_fee_exempt: true, taker_fills: 0, total_entry_fees_cents: 0, net_equals_gross: true } : null, causal_reach_reference: isMaker41 ? { commit: CAUSAL_REACH_COMMIT, under_par: causalReachReceipt.CAUSAL_REACH.under_par, locked_cents: causalReachReceipt.CAUSAL_REACH.locked } : null, reach_answer_key_grade_from_b581cbb: { matched: 52, shallow: 212, one_missing: 486, both_missing: 35, no_reach: 19, completed_on_637_answer_key: 264 }, [`${variant.toUpperCase()}_market_union_reach`]: marketScore, [`${variant.toUpperCase()}_strict_build_verification`]: strictScore } : null;
  const strictLegByIdentity = new Map(strictEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
  const joinRows = (isV40 || isMaker41) ? marketLegs.filter((leg) => Number.isInteger(leg.persistent_join_level)).map((leg) => {
    const strictLeg = strictLegByIdentity.get(leg.leg_identity);
    return {
      event_id: leg.event_id,
      leg_identity: leg.leg_identity,
      category: leg.category,
      bell_confidence: leg.bell_confidence,
      incumbent_state_at_terminal_decision: leg.last_combined_state,
      join_level_cents: leg.persistent_join_level,
      join_timestamp_epoch: leg.persistent_join_timestamp_epoch,
      join_receipt: leg.persistent_join_receipt,
      trigger_evidence_receipt: leg.persistent_join_evidence_receipt,
      all_book_last_trade_at_level_receipts: leg.persistent_join_book_last_trade_receipts,
      all_certified_seller_aggressed_prints_at_level: leg.persistent_join_certified_seller_aggressed_prints,
      post_join_book_last_trade_at_level_receipts: leg.post_join_book_last_trade_receipts,
      post_join_certified_seller_aggressed_prints_at_level: leg.post_join_certified_seller_hits_at_level,
      market_credited: leg.credited,
      market_entry_cents: leg.entry_cents,
      market_fill_timestamp_epoch: leg.fill_timestamp_epoch,
      market_fill_class: leg.fill_class,
      strict_credited: Boolean(strictLeg?.credited),
      strict_entry_cents: strictLeg?.entry_cents ?? null,
      strict_fill_timestamp_epoch: strictLeg?.fill_timestamp_epoch ?? null,
      strict_fill_class: strictLeg?.fill_class ?? null,
    };
  }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity)) : [];
  const joinReceipt = (isV40 || isMaker41) ? {
    join_legs: joinRows.length,
    market_credited_after_join: joinRows.filter((row) => row.market_credited && row.market_fill_timestamp_epoch > row.join_timestamp_epoch).length,
    strict_credited_after_join: joinRows.filter((row) => row.strict_credited && row.strict_fill_timestamp_epoch > row.join_timestamp_epoch).length,
    post_join_certified_seller_hit_distribution: distribution(joinRows.map((row) => row.post_join_certified_seller_aggressed_prints_at_level)),
    post_join_book_last_trade_receipt_distribution: distribution(joinRows.map((row) => row.post_join_book_last_trade_at_level_receipts)),
    zero_post_join_certified_seller_hits: joinRows.filter((row) => row.post_join_certified_seller_aggressed_prints_at_level === 0).length,
    by_category_x_bell_confidence: countBy(joinRows, (row) => `${row.category}|${row.bell_confidence}`),
    BOSCOP_COP: joinRows.find((row) => row.leg_identity.endsWith("BOSCOP|COP")) || null,
  } : null;
  const acceptance = isV40 ? { completed_pairs: { value: marketScore.completed_pairs, minimum: 270, pass: marketScore.completed_pairs >= 270 }, LE_93: { value: marketScore.frontier.LE_93, minimum: 12, pass: marketScore.frontier.LE_93 >= 12 }, LE_95: { value: marketScore.frontier.LE_95, minimum: 24, pass: marketScore.frontier.LE_95 >= 24 } } : null;
  if (acceptance) acceptance.pass = Object.values(acceptance).filter((row) => row && typeof row === "object" && "pass" in row).every((row) => row.pass);
  const v39TelemetryPath = ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807/CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json";
  const classifierResearchOpen = isV40 ? {
    status: "CLASSIFIER_RESEARCH_OPEN",
    V39_package_commit: "ff5880d11a88b0d12415f5371d7cbb61331957e4",
    V39_telemetry_path: v39TelemetryPath,
    V39_telemetry_sha256: fileHash(path.join(repo, v39TelemetryPath)),
    V39_reach_moment_accuracy: JSON.parse(fs.readFileSync(path.join(repo, v39TelemetryPath), "utf8")).aggregate.reach_moment_accuracy,
    ruling: "NO_BUILD_MAY_GATE_ON_A_NEW_DIRECTION_READ_UNTIL_IT_VALIDATES_ABOVE_THE_INCUMBENT_ON_HELD_OUT_LEGS",
    V40_policy_imports_V39: false,
    V40_state_combiner_identity: policy.combineState === require("./window1_v36_state_directional_rest_mature_floor.js").combineState,
  } : null;
  if (classifierResearchOpen) ensure(classifierResearchOpen.V40_state_combiner_identity, "V40 does not inherit V36 state combiner");
  const namedCausality = isV39 ? {
    controlling_counterfactual: {
      commit: COUNTERFACTUAL_COMMIT,
      ruler: counterReceipt.ruler,
      warning: "THE COUNTERFACTUAL CREDITS UNION REACH AT THE REST LEVEL WITHOUT REQUIRING A STRICTLY LATER CAUSAL RECEIPT; V39 DOES NOT RETRO-CREDIT THAT HINDSIGHT CONVENTION",
    },
    ARNROM: {
      ordered_target: "ARN joins 50; pair 89",
      result: named.ARNROM.MARKET_UNION_REACH,
      adjudication: named.ARNROM.MARKET_UNION_REACH.completed && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents === 89 ? "PASS" : "FAIL",
    },
    BOSCOP: {
      ordered_target: "COP joins 47; pair 77",
      result: named.BOSCOP.MARKET_UNION_REACH,
      adjudication: named.BOSCOP.MARKET_UNION_REACH.completed && named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents === 77 ? "PASS" : "FAIL_CLOSED_NO_STRICTLY_LATER_UNION_REACH_AFTER_CAUSAL_JOIN",
      explanation: "COP causally joined 47 only after the persistent-level seller-hit receipt. No later quote-touch, traded-at-level, or print-cross receipt reached that resting order before the hard edge, so pair 77 is not credited.",
    },
    WESPAA: { role: "CAUSAL_CLASSIFIER_TEST_CASE", result: named.WESPAA.MARKET_UNION_REACH },
    NIKVRB: { role: "NEGATIVE_CONTROL_PERSISTENT_JOIN_DOES_NOT_OVERRIDE_PULSE_OR_INCUMBENT_PATH", result: named.NIKVRB.MARKET_UNION_REACH },
    GANJAN: { role: "NAMED_DAMAGE_REGRESSION", result: named.GANJAN.MARKET_UNION_REACH },
  } : null;
  const namedV40 = isV40 ? {
    ARNROM: { ordered: "ARN joins 50; pair 89", result: named.ARNROM.MARKET_UNION_REACH, pass: named.ARNROM.MARKET_UNION_REACH.completed && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents === 89 },
    BOSCOP: { ordered: "REPORT_TRIGGER_LATENESS_BOUNDARY", result: named.BOSCOP.MARKET_UNION_REACH, COP_join_evidence: joinReceipt.BOSCOP_COP, boundary: joinReceipt.BOSCOP_COP?.post_join_certified_seller_aggressed_prints_at_level > 0 ? "LATER_CERTIFIED_HIT_EXISTS" : "NO_LATER_CERTIFIED_SELLER_HIT_AFTER_JOIN" },
    WESPAA: { ordered: "EXPECT_V36_BEHAVIOR_CLASSIFIER_SEVERED", result: named.WESPAA.MARKET_UNION_REACH },
    NIKVRB: { ordered: "NEGATIVE_CONTROL", result: named.NIKVRB.MARKET_UNION_REACH },
  } : null;
  const namedV41 = isV41 ? {
    ordered: { ARNROM: "maker rests should approach ARN~50 plus ROM38=88; report causal truth without retro-credit", BOSCOP: "named maker machine regression", NIKVRB: "named pulse/tracker regression", WESPAA: "named empty/forfeit regression", KRUFER: "named placement-stack regression" },
    ARNROM: {
      result: named.ARNROM.MARKET_UNION_REACH,
      exact_rest_and_fill_sequence: allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && row.event_id.includes("ARNROM") && ["PLACE_REST", "REPRICE_REST", "PAIR_ARM", "PAIR_CAP_REPRICE", "FILL"].includes(row.kind)),
      observed_combined_entry_cents: named.ARNROM.MARKET_UNION_REACH.combined_entry_cents,
      near_88: Number.isInteger(named.ARNROM.MARKET_UNION_REACH.combined_entry_cents) && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents <= 90,
      no_fabricated_target_credit: true,
    },
    BOSCOP: named.BOSCOP,
    NIKVRB: named.NIKVRB,
    WESPAA: named.WESPAA,
    KRUFER: named.KRUFER,
  } : null;
  const v42GuardLegs = hasDeepGap ? marketLegs.filter((leg) => leg.deep_gap_withhold_episodes > 0).map((leg) => ({ event_id: leg.event_id, leg_identity: leg.leg_identity, category: leg.category, bell_confidence: leg.bell_confidence, guard_evaluations: leg.deep_gap_guard_evaluations, withheld_evaluations: leg.deep_gap_withheld_evaluations, withhold_episodes: leg.deep_gap_withhold_episodes, lifts: leg.deep_gap_lifts, first_withhold: leg.deep_gap_first_withhold, last_withhold: leg.deep_gap_last_withhold, last_lift: leg.deep_gap_last_lift, credited: leg.credited, entry_cents: leg.entry_cents, terminal_reason: leg.terminal_reason })).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity)) : [];
  const v42GuardActions = hasDeepGap ? allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && String(row.kind).startsWith("DEEP_GAP_")) : [];
  const v45ReleasedRestLedger = isV45 ? (() => {
    const baselineByEvent = new Map(machineRuns.get("V43_BASELINE").marketEvents.map((event) => [event.event_id, event]));
    const rows = marketEvents.flatMap((event) => Object.values(event.legs).filter((leg) => leg.post_credit_guard_releases > 0).map((leg) => {
      const release = leg.post_credit_guard_release, baselineEvent = baselineByEvent.get(event.event_id), baselineLeg = baselineEvent.legs[leg.leg_id];
      const sibling = Object.values(event.legs).find((candidate) => candidate.leg_identity === release.credited_sibling_leg_identity);
      return { event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, released_leg_identity: leg.leg_identity, credited_sibling_leg_identity: release.credited_sibling_leg_identity, sibling_entry_cents: release.sibling_entry_cents, fixed_pair_cap_cents: release.fixed_pair_cap_cents, release_timestamp_epoch: release.timestamp_epoch, t_minus_scheduled_seconds: release.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: release.t_minus_actual_bell_seconds, release_receipt: release.receipt, mechanism: release.mechanism || "ACTIVE_WITHHOLD_TERMINATED_AT_SIBLING_CREDIT", own_book_receipt: release.own_book_receipt, own_book: release.own_book, released_rest_cents: release.order_after_cents, reapplication_prevented_receipts: leg.post_credit_guard_reapplication_prevented_receipts, filled_after_release: leg.credited && leg.fill_timestamp_epoch >= release.timestamp_epoch, fill_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class, pair_completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, sibling_stayed_credited: Boolean(sibling?.credited), V43_baseline: { released_leg_credited: baselineLeg.credited, released_leg_entry_cents: baselineLeg.entry_cents, pair_completed: baselineEvent.completed_pair, combined_entry_cents: baselineEvent.combined_entry_cents }, completion_gained_vs_V43: event.completed_pair && !baselineEvent.completed_pair, new_exposure_vs_V43: !event.completed_pair && Object.values(event.legs).filter((candidate) => candidate.credited).length > Object.values(baselineEvent.legs).filter((candidate) => candidate.credited).length, terminal_reason: leg.terminal_reason };
    })).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.released_leg_identity.localeCompare(b.released_leg_identity));
    return { rows, summary: { released_rests: rows.length, active_withholds_terminated_at_credit: rows.filter((row) => row.mechanism === "ACTIVE_WITHHOLD_TERMINATED_AT_SIBLING_CREDIT").length, future_reapplications_prevented: rows.filter((row) => row.mechanism === "POST_CREDIT_GUARD_REAPPLICATION_PREVENTED").length, released_and_filled: rows.filter((row) => row.filled_after_release).length, released_unfilled: rows.filter((row) => !row.filled_after_release).length, two_columns: { pairs_completed: { events: rows.filter((row) => row.completion_gained_vs_V43).length, identities: rows.filter((row) => row.completion_gained_vs_V43).map((row) => row.event_id) }, new_exposure: { events: rows.filter((row) => row.new_exposure_vs_V43).length, identities: rows.filter((row) => row.new_exposure_vs_V43).map((row) => row.event_id) } }, by_category: countBy(rows, (row) => row.category), conservation: { rows: rows.length, filled_plus_unfilled: rows.filter((row) => row.filled_after_release).length + rows.filter((row) => !row.filled_after_release).length, pass: rows.length === rows.filter((row) => row.filled_after_release).length + rows.filter((row) => !row.filled_after_release).length } } };
  })() : null;
  const v41ActionRows = hasDeepGap ? readRows(path.join(repo, ".claude/window1_live_v4_replay/v41_maker_machine_20260808/ACTION_TRACE.jsonl.gz")).filter((row) => row.mode === "MARKET_UNION_REACH") : [];
  const normalizedAction = (row) => ({ kind: row.kind, event_id: row.event_id, leg_identity: row.leg_identity, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, target_cents: row.target_cents ?? null, entry_cents: row.entry_cents ?? null, pair_cap_cents: row.pair_cap_cents ?? null, reason: row.reason ?? null, fill_class: row.fill_class ?? null });
  const actionStreams = (rows) => {
    const map = new Map();
    for (const row of rows.filter((item) => !String(item.kind).startsWith("DEEP_GAP_") && !["GAP_CREDIT_AUTHORIZED", "GAP_CREDIT_REFUSED"].includes(item.kind))) { if (!map.has(row.leg_identity)) map.set(row.leg_identity, []); map.get(row.leg_identity).push(normalizedAction(row)); }
    return map;
  };
  const v42Differential = hasDeepGap ? (() => {
    const prior = actionStreams(v41ActionRows), next = actionStreams(allActions.filter((row) => row.mode === "MARKET_UNION_REACH")), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V41_action_stream_sha256: shaBytes(priorBytes), V42_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V41_commit: V41_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v45Differential = isV45 ? (() => {
    const priorRows = machineRuns.get("V43_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V43_action_stream_sha256: shaBytes(priorBytes), V45_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V43_commit: V43_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v46Differential = isV46 ? (() => {
    const priorRows = machineRuns.get("V45_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V46_PAIR_GATED_GAP_CREDIT").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V45_action_stream_sha256: shaBytes(priorBytes), V46_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V45_commit: V45_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v47Differential = isV47 ? (() => {
    const priorRows = machineRuns.get("V45_BASELINE").actions.filter((row) => row.mode === "MARKET_UNION_REACH"), nextRows = machineRuns.get("V47_SAME_TICK_ARM").actions.filter((row) => row.mode === "MARKET_UNION_REACH");
    const prior = actionStreams(priorRows), next = actionStreams(nextRows), changed = [], unchanged = [];
    for (const identity of marketLegs.map((leg) => leg.leg_identity).sort()) {
      const priorBytes = canonical(prior.get(identity) || []), nextBytes = canonical(next.get(identity) || []);
      const row = { leg_identity: identity, V45_action_stream_sha256: shaBytes(priorBytes), V47_action_stream_sha256: shaBytes(nextBytes), byte_identical: priorBytes === nextBytes };
      (row.byte_identical ? unchanged : changed).push(row);
    }
    return { frozen_V45_commit: V45_COMMIT, compared_leg_streams: 1608, changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed, unchanged_aggregate_sha256: shaBytes(canonical(unchanged)), conservation: { sum: changed.length + unchanged.length, expected: 1608, pass: changed.length + unchanged.length === 1608 } };
  })() : null;
  const v47SegCFootprint = isV47 ? (() => {
    const priorRun = machineRuns.get("V45_BASELINE"), nextRun = machineRuns.get("V47_SAME_TICK_ARM");
    const keyOf = (row) => `${row.mode}|${row.event_id}|${row.leg_identity}|${row.qualification_receipt}|${row.qualification_level_cents}`;
    const actionIndex = (actions) => {
      const index = new Map();
      for (const row of actions) {
        if (!["PLACE_REST", "REPRICE_REST"].includes(row.kind)) continue;
        const key = `${row.mode}|${row.leg_identity}|${row.target_cents}`;
        if (!index.has(key)) index.set(key, []);
        index.get(key).push(row);
      }
      for (const values of index.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
      return index;
    };
    const priorActions = actionIndex(priorRun.actions), nextActions = actionIndex(nextRun.actions);
    const postFor = (qualification, index) => {
      if (qualification.disposition === "ALREADY_RESTING_AT_QUALIFIED_LEVEL") return { timestamp_epoch: qualification.qualification_timestamp_epoch, receipt: qualification.qualification_receipt, latency_seconds: 0, disposition: qualification.disposition };
      const candidates = index.get(`${qualification.mode}|${qualification.leg_identity}|${qualification.qualification_level_cents}`) || [];
      let low = 0, high = candidates.length;
      while (low < high) {
        const middle = (low + high) >>> 1;
        if (candidates[middle].timestamp_epoch < qualification.qualification_timestamp_epoch) low = middle + 1;
        else high = middle;
      }
      const hit = candidates[low];
      return hit ? { timestamp_epoch: hit.timestamp_epoch, receipt: hit.receipt, latency_seconds: hit.timestamp_epoch - qualification.qualification_timestamp_epoch, disposition: hit.timestamp_epoch === qualification.qualification_timestamp_epoch && hit.receipt === qualification.qualification_receipt ? "POSTED_ON_QUALIFYING_RECEIPT" : "POSTED_LATER_AFTER_UNCHANGED_LAW" } : { timestamp_epoch: null, receipt: null, latency_seconds: null, disposition: qualification.disposition };
    };
    const priorByKey = new Map(priorRun.joinQualifications.map((row) => [keyOf(row), row]));
    const nextByKey = new Map(nextRun.joinQualifications.map((row) => [keyOf(row), row]));
    ensure(priorByKey.size === priorRun.joinQualifications.length && nextByKey.size === nextRun.joinQualifications.length, "duplicate SEG_C qualification key");
    ensure(priorByKey.size === nextByKey.size && [...priorByKey.keys()].every((key) => nextByKey.has(key)), "V45/V47 deep-join qualification set changed");
    const priorMarket = new Map(priorRun.marketEvents.map((event) => [event.event_id, event])), nextMarket = new Map(nextRun.marketEvents.map((event) => [event.event_id, event]));
    const aggregates = new Map();
    const totals = { V45_zero_qualification_to_post_rows: 0, V47_zero_qualification_to_post_rows: 0, V45_positive_qualification_to_post_rows: 0, V47_positive_qualification_to_post_rows: 0, V45_positive_scheduler_latency_rows: 0, V47_positive_scheduler_latency_rows: 0, unchanged_law_no_post_rows: 0 };
    for (const [key, prior] of priorByKey) {
      const next = nextByKey.get(key), V45 = postFor(prior, priorActions), V47 = postFor(next, nextActions), groupKey = `${prior.mode}|${prior.leg_identity}`;
      if (!aggregates.has(groupKey)) {
        const priorEvent = priorMarket.get(prior.event_id), nextEvent = nextMarket.get(prior.event_id), legId = prior.leg_identity.split("|").at(-1), priorLeg = priorEvent.legs[legId], nextLeg = nextEvent.legs[legId];
        aggregates.set(groupKey, { key: groupKey, event_id: prior.event_id, leg_identity: prior.leg_identity, category: prior.category, price_region: prior.price_region, bell_confidence: prior.bell_confidence, mode: prior.mode, qualification_rows: 0, first_qualification: null, last_qualification: null, levels_cents: new Set(), V45_latencies: [], V47_latencies: [], V45_dispositions: {}, V47_dispositions: {}, V45_positive_scheduler_latency_rows: 0, V47_positive_scheduler_latency_rows: 0, V45_outcome: prior.mode === "MARKET_UNION_REACH" ? { leg_credited: priorLeg.credited, leg_entry_cents: priorLeg.entry_cents, pair_completed: priorEvent.completed_pair, combined_entry_cents: priorEvent.combined_entry_cents } : null, V47_outcome: prior.mode === "MARKET_UNION_REACH" ? { leg_credited: nextLeg.credited, leg_entry_cents: nextLeg.entry_cents, pair_completed: nextEvent.completed_pair, combined_entry_cents: nextEvent.combined_entry_cents } : null, outcome_changed: prior.mode === "MARKET_UNION_REACH" && (priorLeg.credited !== nextLeg.credited || priorLeg.entry_cents !== nextLeg.entry_cents || priorEvent.completed_pair !== nextEvent.completed_pair || priorEvent.combined_entry_cents !== nextEvent.combined_entry_cents) });
      }
      const aggregate = aggregates.get(groupKey), qualification = { timestamp_epoch: prior.qualification_timestamp_epoch, receipt: prior.qualification_receipt, level_cents: prior.qualification_level_cents, residency_seconds: prior.residency_seconds };
      aggregate.qualification_rows += 1;
      aggregate.first_qualification ||= qualification;
      aggregate.last_qualification = qualification;
      aggregate.levels_cents.add(prior.qualification_level_cents);
      if (Number.isFinite(V45.latency_seconds)) aggregate.V45_latencies.push(V45.latency_seconds);
      if (Number.isFinite(V47.latency_seconds)) aggregate.V47_latencies.push(V47.latency_seconds);
      aggregate.V45_dispositions[V45.disposition] = (aggregate.V45_dispositions[V45.disposition] || 0) + 1;
      aggregate.V47_dispositions[V47.disposition] = (aggregate.V47_dispositions[V47.disposition] || 0) + 1;
      if (V45.latency_seconds === 0) totals.V45_zero_qualification_to_post_rows += 1;
      if (V47.latency_seconds === 0) totals.V47_zero_qualification_to_post_rows += 1;
      if (Number.isFinite(V45.latency_seconds) && V45.latency_seconds > 0) totals.V45_positive_qualification_to_post_rows += 1;
      if (Number.isFinite(V47.latency_seconds) && V47.latency_seconds > 0) totals.V47_positive_qualification_to_post_rows += 1;
      if (Number.isFinite(prior.scheduler_latency_seconds) && prior.scheduler_latency_seconds > 0) { totals.V45_positive_scheduler_latency_rows += 1; aggregate.V45_positive_scheduler_latency_rows += 1; }
      if (Number.isFinite(next.scheduler_latency_seconds) && next.scheduler_latency_seconds > 0) { totals.V47_positive_scheduler_latency_rows += 1; aggregate.V47_positive_scheduler_latency_rows += 1; }
      if (V47.timestamp_epoch === null) totals.unchanged_law_no_post_rows += 1;
    }
    const rows = [...aggregates.values()].map((row) => ({ ...row, levels_cents: [...row.levels_cents].sort((a, b) => a - b), V45: { qualification_to_post_latency_seconds: distribution(row.V45_latencies), disposition_counts: row.V45_dispositions, positive_scheduler_latency_rows: row.V45_positive_scheduler_latency_rows }, V47: { qualification_to_post_latency_seconds: distribution(row.V47_latencies), disposition_counts: row.V47_dispositions, positive_scheduler_latency_rows: row.V47_positive_scheduler_latency_rows }, V45_latencies: undefined, V47_latencies: undefined, V45_dispositions: undefined, V47_dispositions: undefined, V45_positive_scheduler_latency_rows: undefined, V47_positive_scheduler_latency_rows: undefined })).sort((a, b) => a.mode.localeCompare(b.mode) || a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity));
    const outcomeChanged = rows.filter((row) => row.outcome_changed);
    const summary = { qualification_rows: priorRun.joinQualifications.length, deep_join_legs: rows.length, by_mode: countBy(priorRun.joinQualifications, (row) => row.mode), ...totals, outcome_changed_rows: outcomeChanged.length, outcome_changed_events: [...new Set(outcomeChanged.map((row) => row.event_id))].sort(), SURECH: rows.filter((row) => row.event_id.includes("SURECH")), evidence_ruling: "8877c2d5_IS_AN_OLDER_L4_ARCHETYPE_RENDER_NOT_A_V45_TRACE; EXECUTABLE_V45_ALREADY_POSTS_JOIN_CHANGES_ON_THE_QUALIFYING_RECEIPT", latency_ruling: "QUALIFICATION_TO_POST_DELAY_FROM_UNCHANGED_GUARDS_IS_NOT_SCHEDULER_LATENCY", footprint_grain: "ONE_ROW_PER_MODE_AND_DEEP_JOIN_LEG", conservation: { V45_qualifications: priorRun.joinQualifications.length, V47_qualifications: nextRun.joinQualifications.length, qualification_assignment_sum: rows.reduce((sum, row) => sum + row.qualification_rows, 0), ledger_rows: rows.length, expected_ledger_rows: aggregates.size, pass: priorRun.joinQualifications.length === nextRun.joinQualifications.length && rows.reduce((sum, row) => sum + row.qualification_rows, 0) === priorRun.joinQualifications.length && rows.length === aggregates.size } };
    return { rows, summary };
  })() : null;
  const v46GapLedger = isV46 ? (() => {
    const baselineByEvent = new Map(machineRuns.get("V45_BASELINE").marketEvents.map((event) => [event.event_id, event]));
    const gapActions = allActions.filter((row) => row.mode === "MARKET_UNION_REACH" && row.kind === "GAP_CREDIT_REPRICE_DOWN");
    const rows = gapActions.map((action) => {
      const event = marketEvents.find((candidate) => candidate.event_id === action.event_id), baselineEvent = baselineByEvent.get(action.event_id), leg = Object.values(event.legs).find((candidate) => candidate.leg_identity === action.leg_identity), baselineLeg = Object.values(baselineEvent.legs).find((candidate) => candidate.leg_identity === action.leg_identity);
      const sibling = Object.values(event.legs).find((candidate) => candidate.leg_identity !== action.leg_identity);
      return { event_id: action.event_id, category: event.category, price_region: leg.price_region, leg_identity: action.leg_identity, timestamp_epoch: action.timestamp_epoch, t_minus_scheduled_seconds: action.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: action.t_minus_actual_bell_seconds, receipt: action.receipt, prior_ask_cents: action.gap_credit?.prior_ask_cents ?? null, current_ask_cents: action.gap_credit?.current_ask_cents ?? null, ask_gap_cents: action.gap_credit?.ask_gap_cents ?? null, order_after_cents: action.target_cents, sibling_credited_at_walk: true, sibling_entry_cents: action.gap_credit?.sibling_entry_cents ?? null, pair_cap_cents: action.gap_credit?.pair_cap_cents ?? null, leg_filled: leg.credited, leg_entry_cents: leg.entry_cents, fill_class: leg.fill_class, gap_credit_fill: leg.gap_credit_fill, pair_completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, falling_tail_depth_cents: leg.credited && Number.isInteger(leg.union_reach_cents) ? leg.entry_cents - leg.union_reach_cents : null, V45: { leg_credited: baselineLeg.credited, leg_entry_cents: baselineLeg.entry_cents, pair_completed: baselineEvent.completed_pair, combined_entry_cents: baselineEvent.combined_entry_cents }, completion_gained_vs_V45: event.completed_pair && !baselineEvent.completed_pair, new_exposure_vs_V45: !event.completed_pair && Object.values(event.legs).filter((candidate) => candidate.credited).length > Object.values(baselineEvent.legs).filter((candidate) => candidate.credited).length, sibling_stayed_credited: sibling.credited };
    }).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity));
    const changedEvents = new Set(rows.filter((row) => row.completion_gained_vs_V45).map((row) => row.event_id));
    const exposureEvents = new Set(rows.filter((row) => row.new_exposure_vs_V45).map((row) => row.event_id));
    const legRows = marketLegs.filter((leg) => leg.gap_credit_eligible_receipts > 0);
    return { rows, summary: { authorized_walks: rows.length, authorized_legs: new Set(rows.map((row) => row.leg_identity)).size, authorized_events: new Set(rows.map((row) => row.event_id)).size, authorized_walks_that_filled: rows.filter((row) => row.gap_credit_fill).length, eligible_legs: legRows.length, sibling_uncredited_refusal_receipts: legRows.reduce((sum, leg) => sum + leg.gap_credit_sibling_uncredited_refusals, 0), sibling_uncredited_refusal_legs: legRows.filter((leg) => leg.gap_credit_sibling_uncredited_refusals > 0).length, no_lawful_reprice_receipts: legRows.reduce((sum, leg) => sum + leg.gap_credit_no_lawful_reprice, 0), two_columns: { pairs_completed: { events: changedEvents.size, identities: [...changedEvents].sort() }, new_exposure: { events: exposureEvents.size, identities: [...exposureEvents].sort() } }, falling_tail_depth_cents: distribution(rows.filter((row) => row.gap_credit_fill).map((row) => row.falling_tail_depth_cents)), by_category: countBy(rows, (row) => row.category), conservation: { authorized_walk_rows: rows.length, leg_authorized_walk_sum: legRows.reduce((sum, leg) => sum + leg.gap_credit_authorized_walks, 0), pass: rows.length === legRows.reduce((sum, leg) => sum + leg.gap_credit_authorized_walks, 0) } } };
  })() : null;
  const namedV42 = isV42 ? (() => {
    const rowsFor = (label) => v42GuardActions.filter((row) => row.event_id.includes(label));
    const put = rowsFor("PUTJEA"), roc = rowsFor("ROCBUE"), kre = rowsFor("KREZHE"), bor = rowsFor("BORDIM");
    const putFingerprint = put.find((row) => row.leg_identity.endsWith("|JEA") && row.kind === "DEEP_GAP_WITHHOLD_START" && row.v41_target_cents === 64 && row.guard?.sibling_best_ask_cents === 93 && row.guard?.implied_sibling_cap_cents === 35) || null;
    const bordimDimWithholds = bor.filter((row) => row.leg_identity.endsWith("|DIM") && row.kind === "DEEP_GAP_WITHHOLD_START");
    return {
      PUTJEA: { ordered: "JEA_REST_64_WITHHELD_WHILE_PUT_ASK_93_AND_IMPLIED_CAP_35", fingerprint: putFingerprint, actions: put, result: named.PUTJEA },
      ROCBUE: { ordered: "DEEP_TAIL_LOSS_CASE", actions: roc, result: named.ROCBUE },
      KREZHE: { ordered: "DEEP_TAIL_LOSS_CASE", actions: kre, result: named.KREZHE },
      BORDIM: { ordered: "MARGINAL_GAP_ONE_CENT_MUST_NOT_BE_WITHHELD", DIM_withhold_starts: bordimDimWithholds.length, actions: bor, result: named.BORDIM },
      ARNROM: { role: "V41_REGRESSION", result: named.ARNROM },
      assertions: { PUTJEA_fingerprint_pass: Boolean(putFingerprint), ROCBUE_touched: roc.some((row) => row.kind === "DEEP_GAP_WITHHOLD_START"), KREZHE_touched: kre.some((row) => row.kind === "DEEP_GAP_WITHHOLD_START"), BORDIM_DIM_not_withheld: bordimDimWithholds.length === 0 },
    };
  })() : null;
  if (namedV42) {
    ensure(namedV42.assertions.PUTJEA_fingerprint_pass, "PUTJEA JEA 64/93/cap35 fingerprint did not fire");
    ensure(namedV42.assertions.ROCBUE_touched && namedV42.assertions.KREZHE_touched, "named deep-tail cases did not fire");
    ensure(namedV42.assertions.BORDIM_DIM_not_withheld, "BORDIM marginal DIM leg was withheld");
  }
  const namedV43 = isV43 ? (() => {
    const rowsFor = (label) => v42GuardActions.filter((row) => row.event_id.includes(label));
    const put = rowsFor("PUTJEA"), bor = rowsFor("BORDIM");
    const putFingerprint = put.find((row) => row.leg_identity.endsWith("|JEA") && row.kind === "DEEP_GAP_WITHHOLD_START" && row.v41_target_cents === 64 && row.guard?.sibling_best_ask_cents === 93 && row.guard?.implied_sibling_cap_cents === 35) || null;
    const bordimWithholds = bor.filter((row) => row.leg_identity.endsWith("|DIM") && row.kind === "DEEP_GAP_WITHHOLD_START");
    const observed = { KIRSEK: named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents, ARNROM: named.ARNROM.MARKET_UNION_REACH.combined_entry_cents, KRUFER: named.KRUFER.MARKET_UNION_REACH.combined_entry_cents, BOSCOP: named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents };
    const assertions = { KIRSEK_47: observed.KIRSEK === 47, ARNROM_90: observed.ARNROM === 90, KRUFER_96: observed.KRUFER === 96, BOSCOP_94: observed.BOSCOP === 94, PUTJEA_fingerprint_pass: Boolean(putFingerprint), BORDIM_DIM_not_withheld: bordimWithholds.length === 0 };
    return { ordered: { KIRSEK: "COMPLETES_AT_47_KIR_APPROX_30_VIA_FIRST_EVIDENCE_PLUS_SEK_17", ARNROM: "ZERO_REGRESSION_90", KRUFER: "ZERO_REGRESSION_96", BOSCOP: "ZERO_REGRESSION_94", PUTJEA: "JEA_REST_64_WITHHELD_AT_SIBLING_ASK_93_IMPLIED_CAP_35", BORDIM: "MARGINAL_ONE_CENT_GAP_MUST_NOT_BE_WITHHELD" }, observed, assertions, PUTJEA: { fingerprint: putFingerprint, actions: put }, BORDIM: { DIM_withhold_starts: bordimWithholds.length, actions: bor }, by_machine: namedAttribution };
  })() : null;
  if (v43Acceptance) {
    v43Acceptance.named_regressions = { pass: Object.values(namedV43.assertions).every(Boolean), assertions: namedV43.assertions };
    v43Acceptance.receipt_single_clause_reproduction = { pass: Object.values(receiptReproduction).every((row) => row.pass), rows: Object.fromEntries(Object.entries(receiptReproduction).map(([name, row]) => [name, row.pass])) };
    v43Acceptance.pass = v43Acceptance.completed_pairs.pass && v43Acceptance.true_book_net_cents.pass && v43Acceptance.named_regressions.pass && v43Acceptance.receipt_single_clause_reproduction.pass;
  }
  const namedV45 = isV45 ? (() => {
    const baseline = namedAttribution.V43_BASELINE, releaseRows = v45ReleasedRestLedger.rows;
    const view = (label) => {
      const current = named[label].MARKET_UNION_REACH, prior = baseline[label].MARKET_UNION_REACH;
      const fullEvent = marketEvents.find((event) => event.event_id.includes(label));
      const rows = releaseRows.filter((row) => row.event_id.includes(label));
      let disposition = "NO_POST_CREDIT_RELEASE";
      if (rows.some((row) => row.completion_gained_vs_V43)) disposition = "RELEASED_AND_COMPLETED_PAIR";
      else if (rows.some((row) => row.filled_after_release)) disposition = "RELEASED_AND_FILLED_NO_NEW_COMPLETION";
      else if (rows.length) disposition = "RELEASED_UNFILLED";
      else if (!Object.values(current.legs).some((leg) => leg.credited)) disposition = "NO_SIBLING_CREDIT_PRE_FILL_GUARD_UNCHANGED";
      else disposition = "SIBLING_CREDIT_BUT_NO_ACTIVE_GUARD_WITHHOLD";
      return { event_id: named[label].event_id, V43: prior, V45: current, released_rest_rows: rows, disposition, causal_forensics: Object.fromEntries(Object.entries(fullEvent.legs).map(([id, leg]) => [id, { pair_cap_cents: leg.pair_cap_cents, terminal_rest_cents: leg.resting_target_at_edge_cents, union_reach_cents: leg.union_reach_cents, union_first_evidence_timestamp_epoch: leg.union_first_evidence_timestamp_epoch, reach_inside_hard_edge: leg.reach_inside_v36_edge, persistent_join_level_cents: leg.persistent_join_level, persistent_join_timestamp_epoch: leg.persistent_join_timestamp_epoch, post_join_certified_seller_hits_at_level: leg.post_join_certified_seller_hits_at_level, post_credit_guard_releases: leg.post_credit_guard_releases, post_credit_guard_reapplication_prevented_receipts: leg.post_credit_guard_reapplication_prevented_receipts, terminal_reason: leg.terminal_reason }])) };
    };
    const rows = Object.fromEntries(namedLabels.map((label) => [label, view(label)]));
    const exactOutcome = (label, ceiling) => rows[label].V45.completed && rows[label].V45.combined_entry_cents <= ceiling;
    const normalizedOutcome = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: Object.fromEntries(Object.entries(value.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class }])) });
    const unchanged = (label) => canonical(normalizedOutcome(rows[label].V45)) === canonical(normalizedOutcome(rows[label].V43));
    const assertions = { LUZTSE_completes_at_or_better_90: exactOutcome("LUZTSE", 90), PENTHA_unchanged_without_sibling_credit: unchanged("PENTHA"), SHEOLI_unchanged_without_sibling_credit: unchanged("SHEOLI"), ARNROM_at_or_better_89: exactOutcome("ARNROM", 89), KRUFER_at_or_better_96: exactOutcome("KRUFER", 96), KIRSEK_at_or_better_24: exactOutcome("KIRSEK", 24), no_new_exposure_from_post_credit_release: v45ReleasedRestLedger.summary.two_columns.new_exposure.events === 0 };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; MECHANISM_FINGERPRINTS_BIND_TO_MECHANISM_NOT_TICK_VALUES", rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  if (v45Acceptance) {
    v45Acceptance.named_checks = { pass: namedV45.pass, assertions: namedV45.assertions };
    v45Acceptance.pass = v45Acceptance.baseline_reproduction.pass && v45Acceptance.completed_pairs.pass && v45Acceptance.true_book_net_cents.pass && v45Acceptance.naked_pnl_cents.pass && v45Acceptance.named_checks.pass;
  }
  const namedV46 = isV46 ? (() => {
    const baseline = namedAttribution.V45_BASELINE, rows = {};
    for (const label of namedLabels) {
      const current = named[label].MARKET_UNION_REACH, prior = baseline[label].MARKET_UNION_REACH;
      const event = marketEvents.find((candidate) => candidate.event_id.includes(label));
      rows[label] = { event_id: event.event_id, V45: prior, V46: current, gap_credit_legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { eligible_receipts: leg.gap_credit_eligible_receipts, authorized_walks: leg.gap_credit_authorized_walks, sibling_uncredited_refusals: leg.gap_credit_sibling_uncredited_refusals, first: leg.gap_credit_first, last: leg.gap_credit_last, fill: leg.gap_credit_fill, terminal_rest_cents: leg.resting_target_at_edge_cents, terminal_reason: leg.terminal_reason }])) };
    }
    const atOrBetter = (label, ceiling) => rows[label].V46.completed && rows[label].V46.combined_entry_cents <= ceiling;
    const lockedAtLeast = (label, minimum) => rows[label].V46.completed && 100 - rows[label].V46.combined_entry_cents >= minimum;
    const assertions = { PANFAL_completes_at_or_better_92: atOrBetter("PANFAL", 92), PANFAL_locked_at_least_8: lockedAtLeast("PANFAL", 8), ARNROM_at_or_better_89: atOrBetter("ARNROM", 89), KIRSEK_at_or_better_24: atOrBetter("KIRSEK", 24), KRUFER_at_or_better_96: atOrBetter("KRUFER", 96), BOSCOP_at_or_better_80: atOrBetter("BOSCOP", 80), no_new_exposure_from_pair_gated_gap_credit: v46GapLedger.summary.two_columns.new_exposure.events === 0 };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; GAP_CREDIT_REPRICE_REQUIRES_SIBLING_ALREADY_CREDITED", rows, assertions, pass: Object.values(assertions).every(Boolean), PANFAL_mechanism_diagnosis: { both_V45_legs_uncredited: Object.values(rows.PANFAL.V45.legs).every((leg) => !leg.credited), sibling_credit_authority_ever_available: Object.values(rows.PANFAL.gap_credit_legs).some((leg) => leg.authorized_walks > 0), conclusion: Object.values(rows.PANFAL.V45.legs).every((leg) => !leg.credited) ? "ORDERED_NAMED_OUTCOME_IS_UNREACHABLE_UNDER_THE_ORDERED_PAIR_GATE_BECAUSE_NEITHER_EXPRESSION_IS_CREDITED_BEFORE_THE_PAN_GAP" : "PAIR_GATE_AUTHORITY_EXISTED" } };
  })() : null;
  const v46Acceptance = isV46 ? (() => {
    const row = attributionByName.get("V46_PAIR_GATED_GAP_CREDIT"), baseline = attributionByName.get("V45_BASELINE");
    const frontierPass = ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => row.MARKET_UNION_REACH.frontier[tier] >= baseline.MARKET_UNION_REACH.frontier[tier]);
    const boundRegressions = { under_par_non_regression: row.MARKET_UNION_REACH.under_par_pairs >= baseline.MARKET_UNION_REACH.under_par_pairs, locked_cents_non_regression: row.FULL_BOOK.completed_locked_cents >= baseline.FULL_BOOK.completed_locked_cents, frontier_non_regression: frontierPass, strict_build_verification_non_regression: row.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs, no_new_exposure: v46GapLedger.summary.two_columns.new_exposure.events === 0, named: namedV46.assertions };
    const out = { baseline_reproduction: v46BaselineReproduction, completed_pairs: { value: row.MARKET_UNION_REACH.completed_pairs, minimum: 396, pass: row.MARKET_UNION_REACH.completed_pairs >= 396 }, true_book_net_cents: { value: row.FULL_BOOK.true_book_net_cents, strict_minimum: 1774, pass: row.FULL_BOOK.true_book_net_cents > 1774 }, zero_bound_regressions: { checks: boundRegressions, pass: Object.values(boundRegressions).every((value) => typeof value === "boolean" ? value : Object.values(value).every(Boolean)) }, named_checks: { pass: namedV46.pass, assertions: namedV46.assertions } };
    out.pass = out.baseline_reproduction.pass && out.completed_pairs.pass && out.true_book_net_cents.pass && out.zero_bound_regressions.pass && out.named_checks.pass;
    return out;
  })() : null;
  const namedV47 = isV47 ? (() => {
    const baseline = namedAttribution.V45_BASELINE, rows = {};
    const view = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: Object.fromEntries(Object.entries(value.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class }])) });
    for (const label of namedLabels) rows[label] = { event_id: named[label].event_id, V45: view(baseline[label].MARKET_UNION_REACH), V47: view(named[label].MARKET_UNION_REACH), byte_identical_outcome: canonical(view(baseline[label].MARKET_UNION_REACH)) === canonical(view(named[label].MARKET_UNION_REACH)) };
    const assertions = { SURECH_causal_reach_null_remains_unfilled: !rows.SURECH.V45.completed && !rows.SURECH.V47.completed && Object.values(rows.SURECH.V47.legs).every((leg) => !leg.credited), ARNROM_no_regression: rows.ARNROM.byte_identical_outcome, KIRSEK_no_regression: rows.KIRSEK.byte_identical_outcome, KRUFER_no_regression: rows.KRUFER.byte_identical_outcome, BOSCOP_no_regression: rows.BOSCOP.byte_identical_outcome, PANFAL_no_regression: rows.PANFAL.byte_identical_outcome };
    return { rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  const v47Acceptance = isV47 ? (() => {
    const row = attributionByName.get("V47_SAME_TICK_ARM"), baseline = attributionByName.get("V45_BASELINE");
    const regressionChecks = { market_completed: row.MARKET_UNION_REACH.completed_pairs >= baseline.MARKET_UNION_REACH.completed_pairs, market_under_par: row.MARKET_UNION_REACH.under_par_pairs >= baseline.MARKET_UNION_REACH.under_par_pairs, locked_cents: row.FULL_BOOK.completed_locked_cents >= baseline.FULL_BOOK.completed_locked_cents, true_book: row.FULL_BOOK.true_book_net_cents >= baseline.FULL_BOOK.true_book_net_cents, strict_completed: row.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs, frontier: ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => row.MARKET_UNION_REACH.frontier[tier] >= baseline.MARKET_UNION_REACH.frontier[tier]), named: namedV47.pass };
    const out = { baseline_reproduction: v47BaselineReproduction, correctness: { V47_qualification_rows: v47SegCFootprint.summary.qualification_rows, V47_zero_qualification_to_post_rows: v47SegCFootprint.summary.V47_zero_qualification_to_post_rows, V47_positive_qualification_to_post_rows: v47SegCFootprint.summary.V47_positive_qualification_to_post_rows, V47_positive_scheduler_latency_rows: v47SegCFootprint.summary.V47_positive_scheduler_latency_rows, pass: v47SegCFootprint.summary.V47_positive_scheduler_latency_rows === 0 }, zero_regressions: { checks: regressionChecks, pass: Object.values(regressionChecks).every(Boolean) }, gain_required: false, observed_gain: { completed_pairs: row.MARKET_UNION_REACH.completed_pairs - baseline.MARKET_UNION_REACH.completed_pairs, locked_cents: row.FULL_BOOK.completed_locked_cents - baseline.FULL_BOOK.completed_locked_cents, true_book_net_cents: row.FULL_BOOK.true_book_net_cents - baseline.FULL_BOOK.true_book_net_cents } };
    out.pass = out.baseline_reproduction.pass && out.correctness.pass && out.zero_regressions.pass;
    return out;
  })() : null;
  const namedV48 = isV48 ? (() => {
    const selected = namedAttribution[v48SelectedRung], baseline = namedAttribution.V47_BASELINE, lawOnly = namedAttribution.TRADE_TRUTH_V47_INCUMBENT;
    const view = (row) => ({ completed: row.completed, combined_entry_cents: row.combined_entry_cents, under_par: row.under_par, legs: Object.fromEntries(Object.entries(row.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_reason: leg.terminal_reason }])) });
    const machineRows = {};
    for (const machine of machineSpecs.map((spec) => spec.name)) {
      machineRows[machine] = {};
      for (const label of namedLabels) machineRows[machine][label] = view(namedAttribution[machine][label].MARKET_UNION_REACH);
    }
    const selectedRun = machineRuns.get(v48SelectedRung), truthRun = machineRuns.get("TRADE_TRUTH_V47_INCUMBENT");
    const luzEvent = truthRun.marketEvents.find((event) => event.event_id.includes("LUZTSE"));
    const tseIdentity = Object.values(luzEvent.legs).find((leg) => leg.leg_identity.endsWith("|TSE")).leg_identity;
    const tseActions = truthRun.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.leg_identity === tseIdentity).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
    const tseFills = tseActions.filter((row) => row.kind === "FILL");
    const tseFill = tseFills[0] || null;
    const restPeriods = [];
    for (let i = 0; i < tseActions.length; i += 1) {
      const row = tseActions[i];
      if (!["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(row.kind) || row.target_cents !== 79) continue;
      const next = tseActions.slice(i + 1).find((candidate) => ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE", "PAIR_CAP_CANCEL", "CANCEL_REST", "FILL"].includes(candidate.kind));
      restPeriods.push({ start_epoch: row.timestamp_epoch, start_receipt: row.receipt, end_epoch: next?.timestamp_epoch ?? luzEvent.w1_right_epoch, end_receipt: next?.receipt ?? null });
    }
    const tseMeta = Object.values(baseByEvent.get(luzEvent.event_id).legs).find((leg) => leg.leg_identity === tseIdentity);
    const tsePrints = printLoad.byTicker.get(tseMeta.ticker) || [];
    const qualifyingPrints = restPeriods.flatMap((period) => tsePrints.filter((print) => print.ts > period.start_epoch && print.ts <= period.end_epoch && print.price <= 79).map((print) => ({ period, timestamp_epoch: print.ts, receipt: print.receipt, trade_id: print.trade_id, price_cents: print.price, size: print.size, taker_side: print.taker_side, taker_book_side: print.taker_book_side })));
    const floorRow = v48TradedFloorByLeg.get(tseIdentity);
    const creditedAt79 = Boolean(luzEvent.legs.TSE.credited && luzEvent.legs.TSE.entry_cents === 79);
    const selectedRows = machineRows[v48SelectedRung];
    const atOrBetter = (label, ceiling) => selectedRows[label].completed && selectedRows[label].combined_entry_cents <= ceiling;
    const normalized = (value) => canonical({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: value.legs });
    const noWorse = (label) => {
      const before = machineRows.V47_BASELINE[label], after = selectedRows[label];
      if (!before.completed) return !after.completed || after.under_par;
      return after.completed && after.combined_entry_cents <= before.combined_entry_cents;
    };
    const assertions = {
      LUZTSE_TSE_trade_truth_iff: creditedAt79 === (qualifyingPrints.length > 0),
      ARNROM_at_or_better_89: atOrBetter("ARNROM", 89),
      KIRSEK_at_or_better_24: atOrBetter("KIRSEK", 24),
      KRUFER_at_or_better_96: atOrBetter("KRUFER", 96),
      BOSCOP_at_or_better_80: atOrBetter("BOSCOP", 80),
      PANFAL_no_regression: noWorse("PANFAL"),
    };
    return {
      selected_ladder: v48SelectedRung,
      selection_law: "MAX_TRUE_BOOK_NET_CENTS_THEN_COMPLETED_PAIRS_THEN_COMPLETED_LOCKED_CENTS_THEN_MACHINE_NAME; NO_NAMED_RESULT_USED_FOR_SELECTION",
      by_machine: machineRows,
      LUZTSE_TSE: { leg_identity: tseIdentity, rest_periods_at_79: restPeriods, qualifying_post_stand_prints_at_or_below_79: qualifyingPrints, credited_at_79: creditedAt79, fills: tseFills, absolute_window_floor_print: floorRow.floor_print, absolute_floor_precedes_first_79_rest_by_seconds: restPeriods.length && floorRow.floor_print ? restPeriods[0].start_epoch - floorRow.floor_print.timestamp_epoch : null, condition: "CREDIT_IFF_TRUE_TRADE_PRINT_AT_OR_BELOW_79_WHILE_THE_79_REST_STOOD", pass: assertions.LUZTSE_TSE_trade_truth_iff },
      SALIBR_IBR_by_rung: Object.fromEntries(machineSpecs.map((spec) => [spec.name, machineRows[spec.name].SALIBR])),
      V47_baseline_vs_law_only_byte_equal_placements_not_claimed: normalized(machineRows.V47_BASELINE.ARNROM) === normalized(machineRows.TRADE_TRUTH_V47_INCUMBENT.ARNROM),
      assertions,
      pass: Object.values(assertions).every(Boolean),
    };
  })() : null;
  const v48Acceptance = isV48 ? (() => {
    const selected = attributionByName.get(v48SelectedRung), lawOnly = attributionByName.get("TRADE_TRUTH_V47_INCUMBENT");
    const out = {
      baseline_reproduction: v48BaselineReproduction,
      selected_ladder: v48SelectedRung,
      aggregate_targets: null,
      law_only_observed: { completed_pairs: lawOnly.MARKET.completed_pairs, true_book_net_cents: lawOnly.FULL_BOOK.true_book_net_cents },
      selected_observed: { completed_pairs: selected.MARKET.completed_pairs, true_book_net_cents: selected.FULL_BOOK.true_book_net_cents },
      zero_bound_named_regressions: { pass: namedV48.pass, assertions: namedV48.assertions },
    };
    out.pass = out.baseline_reproduction.pass && out.zero_bound_named_regressions.pass;
    return out;
  })() : null;
  const v49EvidenceLedger = isV49 ? (() => {
    const run = machineRuns.get("V49_EVIDENCED_LEVEL_STANDING");
    const actionRows = run.actions.filter((row) => row.mode === "MARKET_TRADES_AS_TRUTH" && row.evidenced_standing?.raised).map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, category: baseByEvent.get(row.event_id).category, price_region: baseByEvent.get(row.event_id).legs[row.leg_identity.split("|").at(-1)].price_region, timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, receipt: row.receipt, action: row.kind, target_cents: row.target_cents, state: row.state, evidence: row.evidenced_standing.evidence }));
    const eventById = new Map(run.marketEvents.map((event) => [event.event_id, event]));
    const legIds = [...new Set(actionRows.map((row) => row.leg_identity))].sort();
    const legs = legIds.map((identity) => {
      const eventId = identity.split("|").slice(0, -1).join("|"), event = eventById.get(eventId), leg = Object.values(event.legs).find((value) => value.leg_identity === identity);
      return { event_id: eventId, leg_identity: identity, category: event.category, price_region: leg.price_region, evidenced_action_count: actionRows.filter((row) => row.leg_identity === identity).length, credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, first: actionRows.find((row) => row.leg_identity === identity), last: actionRows.filter((row) => row.leg_identity === identity).at(-1) };
    });
    return { rows: actionRows, legs, summary: { evidenced_actions: actionRows.length, evidenced_legs: legs.length, evidenced_games: new Set(legs.map((row) => row.event_id)).size, credited_legs: legs.filter((row) => row.credited).length, evidence_sources: countBy(actionRows.flatMap((row) => row.evidence.sources), (row) => row.source), fills_gained: v49Differential.rows.filter((row) => row.disposition === "FILL_GAINED").length, fills_repriced_favorable: v49Differential.rows.filter((row) => row.disposition === "FILL_REPRICED_FAVORABLE").length, fills_repriced_adverse: v49Differential.rows.filter((row) => row.disposition === "FILL_REPRICED_ADVERSE").length, fills_lost: v49Differential.rows.filter((row) => row.disposition === "FILL_LOST").length } };
  })() : null;
  const v49WindowTarget = isV49 ? (() => {
    const baseline = machineRuns.get("TRADE_TRUTH_V47_BASELINE").marketEvents, current = machineRuns.get("V49_EVIDENCED_LEVEL_STANDING").marketEvents;
    const baselineById = new Map(baseline.map((event) => [event.event_id, event]));
    const detailed = standabilityReceipt.detail.filter((row) => row.verdict === "WINDOW_LAWFUL_EVIDENCE").map((row) => {
      const event = current.find((candidate) => candidate.event_id.includes(row.code)), prior = baselineById.get(event.event_id), leg = Object.values(event.legs).find((value) => value.leg_id === row.leg), priorLeg = Object.values(prior.legs).find((value) => value.leg_id === row.leg);
      return { receipt_code: row.code, event_id: event.event_id, leg_id: row.leg, target_print_price_cents: row.print_price, V47_credited: priorLeg.credited, V47_entry_cents: priorLeg.entry_cents, V49_credited: leg.credited, V49_entry_cents: leg.entry_cents, V49_at_or_better_target: leg.credited && leg.entry_cents <= row.print_price, V47_pair_completed: prior.completed_pair, V49_pair_completed: event.completed_pair, pair_conversion: !prior.completed_pair && event.completed_pair };
    });
    const overallConversions = current.filter((event) => !baselineById.get(event.event_id).completed_pair && event.completed_pair);
    return { frozen_receipt_target: { games: standabilityReceipt.recoverable_under_window_law.games, locked_cents: standabilityReceipt.recoverable_under_window_law.locked_cents, by_category: standabilityReceipt.recoverable_under_window_law.by_category }, identity_binding: "THE_FE4747CD_RECEIPT_FREEZES_THE_81_GAME_TARGET_AS_AGGREGATES_BUT_DOES_NOT_EMIT_ALL_81_IDENTITIES; V49_DOES_NOT_FABRICATE_AN_INTERSECTION", frozen_detailed_lawful_evidence_rows: detailed, detailed_rows: detailed.length, detailed_at_or_better: detailed.filter((row) => row.V49_at_or_better_target).length, detailed_pair_conversions: detailed.filter((row) => row.pair_conversion).length, executable_all_population_pair_conversions_vs_V47: overallConversions.length, executable_conversion_event_ids: overallConversions.map((event) => event.event_id).sort() };
  })() : null;
  const namedV49 = isV49 ? (() => {
    const baseline = namedAttribution.TRADE_TRUTH_V47_BASELINE, current = namedAttribution.V49_EVIDENCED_LEVEL_STANDING, rows = {};
    const view = (value) => ({ completed: value.completed, combined_entry_cents: value.combined_entry_cents, under_par: value.under_par, legs: value.legs });
    for (const label of namedLabels) rows[label] = { event_id: named[label].event_id, V47: view(baseline[label].MARKET_UNION_REACH), V49: view(current[label].MARKET_UNION_REACH), evidenced_actions: v49EvidenceLedger.rows.filter((row) => row.event_id.includes(label)) };
    const noWorse = (label) => !rows[label].V47.completed ? true : rows[label].V49.completed && rows[label].V49.combined_entry_cents <= rows[label].V47.combined_entry_cents;
    const herLeg = rows.HERKAZ.V49.legs.HER;
    const assertions = { HERKAZ_completes: rows.HERKAZ.V49.completed, HERKAZ_HER_at_or_better_46: herLeg.credited && herLeg.entry_cents <= 46, HERKAZ_HER_trade_truth_fill: herLeg.fill_class === "MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST", ARNROM_no_regression: noWorse("ARNROM"), KIRSEK_no_regression: noWorse("KIRSEK"), KRUFER_no_regression: noWorse("KRUFER"), BOSCOP_no_regression: noWorse("BOSCOP"), PANFAL_no_regression: noWorse("PANFAL") };
    return { ordered_law: "NAMED_COMPLETION_PASSES_AT_REQUIRED_COMBINED_PRICE_OR_BETTER; HERKAZ_MECHANISM_BINDS_HER_AT_EVIDENCED_46_AND_LATER_TRUE_TRADE_CREDIT", rows, assertions, pass: Object.values(assertions).every(Boolean) };
  })() : null;
  const v49Acceptance = isV49 ? (() => {
    const current = attributionByName.get("V49_EVIDENCED_LEVEL_STANDING"), baseline = attributionByName.get("TRADE_TRUTH_V47_BASELINE");
    const checks = { named: namedV49.pass, completed_non_regression: current.MARKET.completed_pairs >= baseline.MARKET.completed_pairs, frontier_non_regression: ["LE_93", "LE_95", "LE_97", "LT_100"].every((tier) => current.MARKET.frontier[tier] >= baseline.MARKET.frontier[tier]), strict_completed_non_regression: current.STRICT_PRINT_CROSS.completed_pairs >= baseline.STRICT_PRINT_CROSS.completed_pairs };
    return { baseline_reproduction: v49BaselineReproduction, zero_bound_regressions: { checks, pass: Object.values(checks).every(Boolean) }, aggregate_target: null, observed: { completed_pairs: current.MARKET.completed_pairs, under_par_pairs: current.MARKET.under_par_pairs, full_book: current.FULL_BOOK, frontier: current.MARKET.frontier, strict_completed_pairs: current.STRICT_PRINT_CROSS.completed_pairs }, pass: v49BaselineReproduction.pass && Object.values(checks).every(Boolean) };
  })() : null;
  const v43GuardOnlyDiff = isV43 ? deepGapDifferential(machineRuns.get("V41_BASELINE").marketEvents, machineRuns.get("C2_GUARD_ONLY").marketEvents, closeByTicker) : null;
  const v43AttributionScorecard = isV43 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    receipt_reproduction: receiptReproduction,
    composition_bar: v43Acceptance,
    interaction_deltas_vs_V41: attributionRows.map((row) => ({ machine: row.machine, completed_pairs_delta: row.MARKET_UNION_REACH.completed_pairs - 243, locked_cents_delta: row.FULL_BOOK.completed_locked_cents - 732, naked_pnl_cents_delta: row.FULL_BOOK.naked_pnl_cents - 50, true_book_net_cents_delta: row.FULL_BOOK.true_book_net_cents - 782 })),
  } : null;
  const v45AttributionScorecard = isV45 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V43_reproduction: v45BaselineReproduction,
    acceptance: v45Acceptance,
    delta_V45_minus_V43: { completed_pairs: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").MARKET_UNION_REACH.completed_pairs - attributionByName.get("V43_BASELINE").MARKET_UNION_REACH.completed_pairs, under_par_pairs: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").MARKET_UNION_REACH.under_par_pairs - attributionByName.get("V43_BASELINE").MARKET_UNION_REACH.under_par_pairs, locked_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.completed_locked_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.completed_locked_cents, naked_pnl_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.naked_pnl_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.naked_pnl_cents, true_book_net_cents: attributionByName.get("V45_GUARD_RELEASE_AT_SIBLING_CREDIT").FULL_BOOK.true_book_net_cents - attributionByName.get("V43_BASELINE").FULL_BOOK.true_book_net_cents },
  } : null;
  const v46AttributionScorecard = isV46 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V45_reproduction: v46BaselineReproduction,
    acceptance: v46Acceptance,
    delta_V46_minus_V45: { completed_pairs: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").MARKET_UNION_REACH.completed_pairs - attributionByName.get("V45_BASELINE").MARKET_UNION_REACH.completed_pairs, under_par_pairs: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").MARKET_UNION_REACH.under_par_pairs - attributionByName.get("V45_BASELINE").MARKET_UNION_REACH.under_par_pairs, locked_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.completed_locked_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.completed_locked_cents, naked_pnl_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.naked_pnl_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.naked_pnl_cents, true_book_net_cents: attributionByName.get("V46_PAIR_GATED_GAP_CREDIT").FULL_BOOK.true_book_net_cents - attributionByName.get("V45_BASELINE").FULL_BOOK.true_book_net_cents },
  } : null;
  const v47AttributionScorecard = isV47 ? {
    order: machineSpecs.map((spec) => spec.name),
    rows: attributionRows.map(({ full_book_rows, ...row }) => row),
    frozen_V45_reproduction: v47BaselineReproduction,
    acceptance: v47Acceptance,
    delta_V47_minus_V45: v47Acceptance.observed_gain,
  } : null;
  const v48AttributionScorecard = isV48 ? {
    order: machineSpecs.map((spec) => spec.name),
    market_law: "ANY_TRUE_TRADE_AT_OR_BELOW_A_PRIOR_LAWFUL_STANDING_REST; ASKS_NEVER_CREDIT_AND_NEVER_DEFINE_THE_FLOOR",
    rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row),
    frozen_V47_reproduction: v48BaselineReproduction,
    selected_ladder: v48SelectedRung,
    selection_law: namedV48.selection_law,
    acceptance: v48Acceptance,
  } : null;
  const v49AttributionScorecard = isV49 ? {
    order: machineSpecs.map((spec) => spec.name),
    market_law: "ANY_TRUE_TRADE_AT_OR_BELOW_A_PRIOR_LAWFUL_STANDING_REST; ASKS_INFORM_PLACEMENT_ONLY",
    rows: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row),
    frozen_V47_reproduction: v49BaselineReproduction,
    differential: { aggregate: v49Differential.aggregate, by_category: v49Differential.by_category, score_delta: v49Differential.score_delta },
    acceptance: v49Acceptance,
  } : null;
  const core = {
    "CONTROL_BINDING.json": canonical(control),
    ...((isPlacementStack && !isMaker41) ? { "TAKE_PATH_INTACT_RECEIPT.json": canonical({ frozen_V36_commit: V36_COMMIT, V36_policy_path: "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js", V36_policy_sha256: fileHash(path.join(v36Root, "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js")), variant_policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), variant_policy_sha256: fileHash(policyFile), decision_reason: isV40 ? "MATURE_EVIDENCE_FLOOR_TAKE" : "V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED", market_taker_fills: marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length, strict_taker_fills: strictEvents.flatMap((event) => Object.values(event.legs)).filter((leg) => String(leg.fill_class).includes("TAKER")).length, V38_tombstone_role: "REJECTED_MAKER_ONLY_NEGATIVE_CONTROL_NOT_INHERITED" }) } : { "TAKE_PATH_DELETION_RECEIPT.json": canonical({ policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), policy_sha256: fileHash(policyFile), forbidden_action_literal_TAKE_count: (policyText.match(/action:\s*["']TAKE["']/g) || []).length, take_named_function_count: (policyText.match(/function\s+\w*take\w*/gi) || []).length, market_taker_fills: marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length, strict_taker_fills: strictEvents.flatMap((event) => Object.values(event.legs)).filter((leg) => String(leg.fill_class).includes("TAKER")).length, entry_actions_exported: ["PLACE_REST", "REPRICE_REST"], maker_fees_cents: 0, pass: true }) }),
    "PULSE_FLOOR_BINDING.json": canonical(pulseBinding),
    "MARKET_GRADE_SCORECARD.json": canonical(isV49 ? { score: marketScore, traded_floor_grade: attributionByName.get("V49_EVIDENCED_LEVEL_STANDING").TRADED_FLOOR_GRADE, ruler: "TRADES_AS_TRUTH" } : isV48 ? { score: marketScore, traded_floor_grade: attributionByName.get("TRADE_TRUTH_V47_INCUMBENT").TRADED_FLOOR_GRADE, ruler: "TRADES_AS_TRUTH" } : { score: marketScore, reach_grade: marketGrades.aggregate, comparison_answer_key: EXPECTED_REACH }),
    "STRICT_BUILD_VERIFICATION_SCORECARD.json": canonical(isTradeTruthVariant ? { score: strictScore, traded_floor_grade: gradeAgainstTradedFloors(strictEvents, v48TradedFloorByLeg).aggregate, role: "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE" } : { score: strictScore, reach_grade: strictGrades.aggregate, role: "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE" }),
    "CATEGORY_X_BELL_CONFIDENCE.json": canonical(isV49 ? { BASELINE: attributionByName.get("TRADE_TRUTH_V47_BASELINE").category_x_bell_confidence, V49: attributionByName.get("V49_EVIDENCED_LEVEL_STANDING").category_x_bell_confidence } : isV48 ? { MARKET_TRADES_AS_TRUTH: attributionByName.get("TRADE_TRUTH_V47_INCUMBENT").category_x_bell_confidence, selected_ladder: v48SelectedRung, SELECTED: attributionByName.get(v48SelectedRung).category_x_bell_confidence } : { MARKET_UNION_REACH: cellSummary(marketGrades), STRICT_PRINT_CROSS: cellSummary(strictGrades), conservation: { market_answer_key_D: marketGrades.classRows.length, strict_answer_key_D: strictGrades.classRows.length, expected: 637, pass: marketGrades.classRows.length === 637 && strictGrades.classRows.length === 637 } }),
    ...(!isTradeTruthVariant ? {
      "REACH_GRADE_EVENT_LEDGER.jsonl.gz": gzipRows(marketGrades.classRows),
      "REACH_GRADE_LEG_LEDGER.jsonl.gz": gzipRows(marketGrades.rows),
      "RESIDUAL_LAYER_BIND_LEDGER.jsonl.gz": gzipRows(marketGrades.residuals),
      "LAYER_BIND_RANKING.json": canonical({ rows: layerRanking, conservation: { residual_sides: marketGrades.residuals.length, ranked_sides: layerRanking.reduce((sum, row) => sum + row.sides, 0), pass: marketGrades.residuals.length === layerRanking.reduce((sum, row) => sum + row.sides, 0) } }),
    } : {}),
    ...(isV39 ? { "CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json": canonical(directionTelemetry), "MISLABEL_RECOVERY_RECEIPT.json": canonical(mislabelRecovery), "MISLABEL_RECOVERY_LEDGER.jsonl.gz": gzipRows(reconstructedRecovery) } : {}),
    ...(isPlacementStack ? { "REST_SANITY.json": canonical(sanity), "V36_COMPARISON.json": canonical(v36Comparison) } : {}),
    ...(isV40 ? { "CLASSIFIER_RESEARCH_OPEN_RECEIPT.json": canonical(classifierResearchOpen), "ACCEPTANCE_BAR.json": canonical(acceptance), "PERSISTENT_JOIN_POST_EVIDENCE_RECEIPT.json": canonical(joinReceipt), "PERSISTENT_JOIN_POST_EVIDENCE_LEDGER.jsonl.gz": gzipRows(joinRows) } : {}),
    ...(isMaker41 ? { "PERSISTENCE_ONLY_JOIN_RECEIPT.json": canonical({ controlling_frontier: { commit: RISER_FRONTIER_COMMIT, sha256: shaBytes(riserFrontierBytes), T4_persist300: riserFrontierReceipt.per_trigger.T4_persist300 }, controlling_level_policy: { commit: LEVEL_POLICY_COMMIT, sha256: shaBytes(levelPolicyBytes), P2_join: levelPolicyReceipt.per_policy.P2_join, P3_join_track: levelPolicyReceipt.per_policy.P3_join_track }, seller_hit_gate_removed: true, first_two_sided_tracker_until_join: true, join_overrides_tracker: true, join_census: joinReceipt }), "PERSISTENT_JOIN_LEDGER.jsonl.gz": gzipRows(joinRows), "CAUSAL_REACH_BINDING.json": canonical({ commit: CAUSAL_REACH_COMMIT, path: causalReachPath, sha256: shaBytes(causalReachBytes), CAUSAL_REACH: causalReachReceipt.CAUSAL_REACH, conservation: causalReachReceipt.conservation }), ...(isV41 ? { "NAMED_V41_RECEIPT.json": canonical(namedV41) } : {}) } : {}),
    ...(isV49 ? {
      "V49_RECEIPT_BINDINGS.json": canonical({
        frozen_V47: { commit: V47_COMMIT, baseline_reproduction: v49BaselineReproduction },
        standability_v2: { commit: STANDABILITY_V2_COMMIT, json_path: standabilityPath, json_sha256: shaBytes(standabilityBytes), markdown_path: standabilityMdPath, markdown_sha256: shaBytes(standabilityMdBytes), target_games: standabilityReceipt.recoverable_under_window_law.games, target_locked_cents: standabilityReceipt.recoverable_under_window_law.locked_cents },
        HERKAZ: { commit: HERKAZ_EXEMPLAR_COMMIT, receipt_path: herkazPath, receipt_sha256: shaBytes(herkazBytes), marks_path: herkazMarksPath, marks_sha256: shaBytes(herkazMarksBytes), timeline_path: herkazTimelinePath, timeline_sha256: shaBytes(herkazTimelineBytes), evidenced_level_cents: herkazReceipt.P_evidenced_level },
        universal_plus_one_receipt: { commit: LOOSEN_ONE_CENT_COMMIT, path: loosenOneCentPath, sha256: shaBytes(loosenOneCentBytes), controlling_row: loosenOneCentReceipt.per_k["k=1"] },
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v49AttributionScorecard),
      "EVIDENCED_STANDING_RECEIPT.json": canonical(v49EvidenceLedger.summary),
      "EVIDENCED_STANDING_ACTION_LEDGER.jsonl.gz": gzipRows(v49EvidenceLedger.rows),
      "EVIDENCED_STANDING_LEG_LEDGER.jsonl.gz": gzipRows(v49EvidenceLedger.legs),
      "V47_V49_DIFFERENTIAL_RECEIPT.json": canonical({ aggregate: v49Differential.aggregate, by_category: v49Differential.by_category, score_delta: v49Differential.score_delta }),
      "V47_V49_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v49Differential.rows),
      "STANDABILITY_V2_EXECUTABLE_CONVERSION.json": canonical(v49WindowTarget),
      "NAMED_V49_RECEIPT.json": canonical(namedV49),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v49Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v49Acceptance.pass ? "PASS" : "BLOCKED_V47_REMAINS_OPERATIVE", operative_candidate: v49Acceptance.pass ? "V49_EVIDENCED_LEVEL_STANDING" : "V47_FB74C8B8", aggregate_targets: null, reasons: [...(!v49Acceptance.baseline_reproduction.pass ? ["V47_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v49Acceptance.zero_bound_regressions.pass ? ["BOUND_REGRESSION"] : [])], no_forced_values: true }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })) }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", required_fields: ["trade_id", "exchange_timestamp", "price"], asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true }),
    } : {}),
    ...(isV48 ? {
      "V48_RECEIPT_BINDINGS.json": canonical({
        frozen_V47: { commit: V47_COMMIT, baseline_reproduction: v48BaselineReproduction },
        controlling_recut: { commit: TRADES_TRUTH_RECUT_COMMIT, json_path: tradesTruthRecutPath, json_sha256: shaBytes(tradesTruthRecutBytes), markdown_path: tradesTruthRecutMdPath, markdown_sha256: shaBytes(tradesTruthRecutMdBytes), re_cut_legs: tradesTruthRecut.population.L6_legs_recut, true_offer_existed: tradesTruthRecut.corrected_totals.true_offer_existed, seller_cross_set_lowest_legs: 0 },
        scoped_law: "ANY_TRUE_TRADE_PRINT_AT_OR_BELOW_A_LAWFUL_REST_AFTER_THE_REST_STOOD_CREDITS; NO_CHANNEL_AGGRESSOR_DWELL_SIZE_OR_ARRIVAL_FILTER",
        placement_honesty: "V47_INCUMBENT_IS_MIXED; BID_MINUS_ONE_BID_AND_RECENT_TRADE_ARE_EXPLICIT_EXECUTABLE_RUNGS",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v48AttributionScorecard),
      "TRADED_FLOOR_RE_SUM.json": canonical({ law: v48TradedFloors.law, aggregate: v48TradedFloors.aggregate, by_category: v48TradedFloors.by_category, conservation: v48TradedFloors.conservation }),
      "TRADED_FLOOR_GAME_LEDGER.jsonl.gz": gzipRows(v48TradedFloors.game_rows),
      "TRADED_FLOOR_LEG_LEDGER.jsonl.gz": gzipRows(v48TradedFloors.leg_rows),
      "PLACEMENT_LADDER_ATTRIBUTION.json": canonical({ baseline: "TRADE_TRUTH_V47_INCUMBENT", rungs: Object.fromEntries(Object.entries(v48LadderDiffs).map(([name, value]) => [name, { aggregate: value.aggregate, by_category: value.by_category, score_delta: value.score_delta }])), selected: v48SelectedRung, selection_law: namedV48.selection_law }),
      "PLACEMENT_LADDER_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(Object.values(v48LadderDiffs).flatMap((value) => value.rows)),
      "NAMED_V48_RECEIPT.json": canonical(namedV48),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v48Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v48Acceptance.pass ? "PASS" : "BLOCKED", operative_candidate: v48Acceptance.pass ? v48SelectedRung : "V47_FB74C8B8_REMAINS_OPERATIVE", aggregate_targets: null, reasons: [ ...(!v48Acceptance.baseline_reproduction.pass ? ["V47_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v48Acceptance.zero_bound_named_regressions.pass ? ["BOUND_NAMED_REGRESSION"] : []) ], no_forced_values: true }),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, market_mode: row.market_mode, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v48Acceptance }),
      "TRADES_AS_TRUTH_CREDIT_LAW.json": canonical({ order_must_preexist_print: true, timestamp_relation: "PRINT_TIMESTAMP_STRICTLY_GREATER_THAN_REST_ACTION_TIMESTAMP", price_relation: "TRUE_TRADE_PRICE_LE_REST_LEVEL", required_fields: ["trade_id", "exchange_timestamp", "price"], forbidden_filters: ["ask", "aggressor", "dwell", "displayed_size", "arrival_direction", "channel"], asks_role: "PLACEMENT_ONLY", strict_build_verification_separate: true }),
    } : {}),
    ...(isV47 ? {
      "V47_RECEIPT_BINDINGS.json": canonical({
        frozen_V45: { commit: V45_COMMIT, baseline_reproduction: v47BaselineReproduction, control_path: frozenV45ControlPath, control_sha256: shaBytes(frozenV45ControlBytes), attribution_path: frozenV45ScorePath, attribution_sha256: shaBytes(frozenV45ScoreBytes), inherited_policy_path: frozenV45PolicyPath, inherited_policy_git_sha256: shaBytes(frozenV45PolicyBytes), working_git_normalized_sha256: shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), git_normalized_policy_byte_identical: shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))) },
        SURECH_forensic: { commit: SURECH_RENDER_COMMIT, marks_path: surechMarksPath, marks_sha256: shaBytes(surechMarksBytes), timeline_path: surechTimelinePath, timeline_sha256: shaBytes(surechTimelineBytes), role: "OLDER_L4_ARCHETYPE_EVIDENCE_NOT_A_FROZEN_V45_DECISION_TRACE" },
        scoped_law: "JOIN_QUALIFICATION_AND_PLACEMENT_DECISION_ARE_ONE_ATOMIC_RECEIPT_LOCAL_OPERATION; ALL_DECISION_LAWS_UNCHANGED",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v47AttributionScorecard),
      "SEG_C_SAME_TICK_RECEIPT.json": canonical(v47SegCFootprint.summary),
      "SEG_C_SAME_TICK_FOOTPRINT.jsonl.gz": gzipRows(v47SegCFootprint.rows),
      "V45_V47_DIFFERENTIAL_RECEIPT.json": canonical(v47Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v47Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v47Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V45_REMAINS_OPERATIVE", operative_baseline: v47Acceptance.pass ? "V47_SAME_TICK_ARM" : "V45_3bda0a54", gains_required: false, reasons: [ ...(!v47Acceptance.baseline_reproduction.pass ? ["V45_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v47Acceptance.correctness.pass ? ["POSITIVE_SCHEDULER_LATENCY_SURVIVED"] : []), ...(!v47Acceptance.zero_regressions.pass ? ["BOUND_REGRESSION"] : []) ], no_forced_values: true }),
      "NAMED_V47_RECEIPT.json": canonical(namedV47),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v47Acceptance }),
    } : {}),
    ...(isV46 ? {
      "V46_RECEIPT_BINDINGS.json": canonical({
        frozen_V45: { commit: V45_COMMIT, baseline_reproduction: v46BaselineReproduction, control_path: frozenV45ControlPath, control_sha256: shaBytes(frozenV45ControlBytes), attribution_path: frozenV45ScorePath, attribution_sha256: shaBytes(frozenV45ScoreBytes), inherited_policy_path: frozenV45PolicyPath, inherited_policy_git_sha256: shaBytes(frozenV45PolicyBytes), working_filesystem_sha256: fileHash(path.join(repo, frozenV45PolicyPath)), working_git_normalized_sha256: shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n"))), git_normalized_policy_byte_identical: shaBytes(frozenV45PolicyBytes) === shaBytes(Buffer.from(fs.readFileSync(path.join(repo, frozenV45PolicyPath), "utf8").replace(/\r\n/g, "\n")))} ,
        footprint: { commit: STRICT_ASK_FOOTPRINT_COMMIT, path: strictAskFootprintPath, sha256: shaBytes(strictAskFootprintBytes), markdown_path: strictAskFootprintMdPath, markdown_sha256: shaBytes(strictAskFootprintMdBytes), frozen_legs: strictAskFootprint.FOOTPRINT.total, L6_misstamped_legs: strictAskFootprint.FOOTPRINT.by_chain_link.CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY, naked_knife_legs: strictAskFootprint.THE_FIX.ADVERSE.naked_unfrozen_legs, naked_knife_median_adverse_cents: strictAskFootprint.THE_FIX.ADVERSE.naked_only_distribution.median, role: "ANALYTICAL_FOOTPRINT_BINDING_NOT_EXECUTABLE_AGGREGATE" },
        PANFAL_forensic: { marks_path: panfalMarksPath, marks_sha256: shaBytes(panfalMarksBytes), timeline_path: panfalTimelinePath, timeline_sha256: shaBytes(panfalTimelineBytes), role: "ORDERED_NAMED_EXEMPLAR" },
        scoped_law: "ASK_GAP_GE_3_CREDITS_A_FALLING_REPRICE_DOWN_ONLY_WHEN_OTHER_EXPRESSION_ALREADY_CREDITED; OTHERWISE_V45_ACTION_UNCHANGED",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v46AttributionScorecard),
      "GAP_CREDIT_RECEIPT.json": canonical(v46GapLedger.summary),
      "GAP_CREDIT_LEDGER.jsonl.gz": gzipRows(v46GapLedger.rows),
      "V45_V46_DIFFERENTIAL_RECEIPT.json": canonical(v46Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v46Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v46Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V45_REMAINS_OPERATIVE", operative_baseline: v46Acceptance.pass ? "V46_PAIR_GATED_GAP_CREDIT" : "V45_3bda0a54", reasons: [ ...(!v46Acceptance.baseline_reproduction.pass ? ["V45_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v46Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []), ...(!v46Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []), ...(!v46Acceptance.zero_bound_regressions.pass ? ["BOUND_REGRESSION"] : []), ...(!v46Acceptance.named_checks.pass ? ["NAMED_CHECK_FAILED"] : []) ], no_forced_values: true }),
      "NAMED_V46_RECEIPT.json": canonical(namedV46),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v46Acceptance }),
    } : {}),
    ...(isV45 ? {
      "V45_RECEIPT_BINDINGS.json": canonical({
        frozen_V43: { commit: V43_COMMIT, baseline_reproduction: v45BaselineReproduction },
        recalibration: { commit: V43_RECALIBRATION_COMMIT, path: v43RecalibrationPath, sha256: shaBytes(v43RecalibrationBytes), role: "WHOLE_GUARD_REMOVAL_COMPARISON_ONLY_NOT_IMPORTED" },
        residual_docket: { commit: V43_RESIDUAL_DOCKET_COMMIT, path: v43DocketPath, sha256: shaBytes(v43DocketBytes) },
        LUZTSE_forensic: { marks_path: luztseMarksPath, marks_sha256: shaBytes(luztseMarksBytes), timeline_path: luztseTimelinePath, timeline_sha256: shaBytes(luztseTimelineBytes), role: "POST_CREDIT_GUARD_WITHHOLD_EXEMPLAR" },
        scoped_law: "PRE_FILL_DEEP_GAP_GUARD_STAYS; ONLY_ACTIVE_WITHHOLD_ON_OTHER_LEG_TERMINATES_AT_SIBLING_CREDIT",
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v45AttributionScorecard),
      "RELEASED_REST_RECEIPT.json": canonical(v45ReleasedRestLedger.summary),
      "RELEASED_REST_LEDGER.jsonl.gz": gzipRows(v45ReleasedRestLedger.rows),
      "V43_V45_DIFFERENTIAL_RECEIPT.json": canonical(v45Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v45Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v45Acceptance.pass ? "PASS_OPERATIVE" : "BLOCKED_V43_REMAINS_OPERATIVE", operative_baseline: v45Acceptance.pass ? "V45_GUARD_RELEASE_AT_SIBLING_CREDIT" : "V43_01a58334", reasons: [ ...(!v45Acceptance.baseline_reproduction.pass ? ["V43_BASELINE_REPRODUCTION_FAILED"] : []), ...(!v45Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []), ...(!v45Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []), ...(!v45Acceptance.naked_pnl_cents.pass ? ["NAKED_BOOK_DID_NOT_IMPROVE"] : []), ...(!v45Acceptance.named_checks.pass ? ["NAMED_CHECK_FAILED"] : []) ], no_forced_values: true }),
      "NAMED_V45_RECEIPT.json": canonical(namedV45),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), acceptance: v45Acceptance }),
    } : {}),
    ...(isV43 ? {
      "CLAUSE_BINDINGS.json": canonical({
        clause_1: { commit: ARM_FIRST_EVIDENCE_COMMIT, path: armFirstEvidencePath, sha256: shaBytes(armFirstEvidenceBytes), controlling_row: armFirstEvidenceReceipt.rows.ARM, included: "ARM_AT_FIRST_EVIDENCE_ONLY", explicitly_excluded: "WALK_LAG_REMOVAL" },
        clause_2: { commit: DEEP_GAP_CENSUS_COMMIT, path: deepGapCensusPath, sha256: shaBytes(deepGapCensusBytes), T10: { ...deepGapT10, derived_net_cents: (-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents }, full_book_method_commit: FULL_BOOK_PNL_COMMIT, full_book_method_path: fullBookReceiptPath, full_book_method_sha256: shaBytes(fullBookReceiptBytes) },
        clause_3: { commit: LOOSEN_ONE_CENT_COMMIT, path: loosenOneCentPath, sha256: shaBytes(loosenOneCentBytes), controlling_row: loosenOneCentReceipt.per_k["k=1"], law: loosenOneCentReceipt.law },
      }),
      "ATTRIBUTION_SCORECARD.json": canonical(v43AttributionScorecard),
      "DEEP_GAP_GUARD_ALONE_RECEIPT.json": canonical({ controlling_census: { commit: DEEP_GAP_CENSUS_COMMIT, T10: deepGapT10 }, score: attributionByName.get("C2_GUARD_ONLY"), differential_vs_V41: v43GuardOnlyDiff.aggregate }),
      "DEEP_GAP_GUARD_ALONE_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(v43GuardOnlyDiff.rows),
      "COMBINED_DIFFERENTIAL_RECEIPT.json": canonical(v42Differential),
      "COMPOSITION_ACCEPTANCE_BAR.json": canonical(v43Acceptance),
      "CONSTRUCTION_STATUS.json": canonical({ status: v43Acceptance.pass ? "PASS" : "BLOCKED_NOT_OPERATIVE", operative_baseline: v43Acceptance.pass ? "V43_ALL_THREE" : "V41_96d33316", reasons: [
        ...(!v43Acceptance.receipt_single_clause_reproduction.pass ? ["ANALYSIS_ONLY_RECEIPT_PRICING_DOES_NOT_REPRODUCE_AS_EXECUTABLE_RECEIPT_CAUSAL_POLICY"] : []),
        ...(!v43Acceptance.named_regressions.pass ? ["MANDATORY_NAMED_IDENTITIES_CHANGED"] : []),
        ...(!v43Acceptance.completed_pairs.pass ? ["COMPLETION_BAR_FAILED"] : []),
        ...(!v43Acceptance.true_book_net_cents.pass ? ["TRUE_BOOK_BAR_FAILED"] : []),
      ], no_forced_values: true, no_operative_supersession_on_block: true }),
      "NAMED_V43_RECEIPT.json": canonical(namedV43),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", audited_close_column_role: "NOT_CONSUMED_BY_A30F5CCD_FULL_BOOK_METHOD", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, rows: attributionRows.map((row) => ({ machine: row.machine, aggregate: row.FULL_BOOK, by_category: row.by_category.FULL_BOOK })), composition_bar: v43Acceptance }),
    } : {}),
    ...(isV42 ? {
      "DEEP_GAP_GUARD_RECEIPT.json": canonical({ law: control.architecture.clause, tolerance_cents: policy.DEEP_GAP_TOLERANCE_CENTS, controlling_census: { commit: DEEP_GAP_CENSUS_COMMIT, path: deepGapCensusPath, sha256: shaBytes(deepGapCensusBytes), T10: { ...deepGapT10, derived_net_cents: (-deepGapT10.withheld_naked_loss_cents) - deepGapT10.completed_locked_forfeited_cents - deepGapT10.winning_naked_forfeited_cents } }, market: { affected_legs: v42GuardLegs.length, withhold_episodes: v42GuardLegs.reduce((sum, row) => sum + row.withhold_episodes, 0), withheld_evaluations: v42GuardLegs.reduce((sum, row) => sum + row.withheld_evaluations, 0), lifts: v42GuardLegs.reduce((sum, row) => sum + row.lifts, 0), by_category_x_bell_confidence: countBy(v42GuardLegs, (row) => `${row.category}|${row.bell_confidence}`) }, two_columns: { losses_avoided: deepGapDiff.aggregate.losses_avoided, pairs_and_winners_forfeited: { completed_pairs: deepGapDiff.aggregate.pairs_forfeited, winning_naked: deepGapDiff.aggregate.winning_naked_forfeited } }, actual_full_book_delta_cents: v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents }),
      "DEEP_GAP_GUARD_LEG_LEDGER.jsonl.gz": gzipRows(v42GuardLegs),
      "DEEP_GAP_DIFFERENTIAL_RECEIPT.json": canonical(v42Differential),
      "DEEP_GAP_OUTCOME_DIFFERENTIAL.json": canonical(deepGapDiff.aggregate),
      "DEEP_GAP_OUTCOME_DIFFERENTIAL_LEDGER.jsonl.gz": gzipRows(deepGapDiff.rows),
      "FULL_BOOK_PNL.json": canonical({ method: { commit: FULL_BOOK_PNL_COMMIT, receipt_path: fullBookReceiptPath, receipt_sha256: shaBytes(fullBookReceiptBytes), close_audit_path: closeAuditPath, close_audit_sha256: shaBytes(closeAuditBytes), close_column: "replay_close_cents", audited_close_column_role: "NOT_CONSUMED_BY_A30F5CCD_FULL_BOOK_METHOD", completed: "100_MINUS_PAIR_ENTRY", naked: "FROZEN_REPLAY_WINDOW1_CLOSE_MINUS_ENTRY_WHERE_AVAILABLE", skip: 0 }, V41_reconstructed: v41FullBook.aggregate, V42: v42FullBook.aggregate, by_category: v42FullBook.by_category, delta_cents: v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents, acceptance: v42Acceptance }),
      "FULL_BOOK_EVENT_LEDGER.jsonl.gz": gzipRows(v42FullBook.rows),
      "ACCEPTANCE_BAR.json": canonical(v42Acceptance),
      "NAMED_V42_RECEIPT.json": canonical(namedV42),
    } : {}),
    "MARKET_EVENT_LEDGER.jsonl.gz": gzipRows(marketEvents),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(strictEvents),
    "DECISION_TRACE_1608.jsonl.gz": gzipRows((isTradeTruthVariant ? attributionByName.get(isV49 ? "V49_EVIDENCED_LEVEL_STANDING" : "TRADE_TRUTH_V47_INCUMBENT").traded_floor_rows : marketGrades.rows).map((row) => ({ ...row, ...(isTradeTruthVariant ? {} : { reach_snapshot: row.reach_snapshot }), first_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].first_decision, last_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].last_decision }))),
    "NAMED_GAMES.json": canonical({ games: named, action_rows: allActions.filter((row) => namedLabels.some((name) => row.event_id.includes(name)) && (row.kind === "FILL" || String(row.kind).includes("DEEP_GAP") || String(row.kind).includes("POST_CREDIT") || String(row.kind).includes("GAP_CREDIT") || String(row.reason).includes("PERSISTENT") || String(row.reason).includes("FIRST_OBSERVATION") || String(row.reason).includes("ONE_CENT_LESS_GREEDY") || String(row.reason).includes("WTA_OTHER_EXPRESSION_FALLING"))) }),
    ...(isV39 ? { "NAMED_CAUSALITY_RECEIPT.json": canonical(namedCausality) } : {}),
    ...(isV40 ? { "NAMED_V40_RECEIPT.json": canonical(namedV40) } : {}),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, exit_accesses: 0, settlement_accesses: 0, DCA_accesses: 0, deployment_accesses: 0, private_scope: "FIT_DEVELOPMENT_804_TAPE_AND_CERTIFIED_PRINT_CACHE_ONLY", mutations: 0 }),
    "SOURCE_HASH_MANIFEST.json": canonical({
      commits: { V36: V36_COMMIT, UNION_REACH: REACH_COMMIT, GAP_GRADE_PARENT: GAP_COMMIT, DIVOT_CENSUS: DIVOT_COMMIT, ...(isPlacementStack ? { COUNTERFACTUAL: COUNTERFACTUAL_COMMIT } : {}), ...(isV39 ? { FALLER_ANATOMY: FALLER_ANATOMY_COMMIT } : {}), ...(isV40 ? { V39_EVIDENCE_PACKAGE: "ff5880d11a88b0d12415f5371d7cbb61331957e4" } : {}), ...(isMaker41 ? { CAUSAL_REACH: CAUSAL_REACH_COMMIT, RISER_TRIGGER_FRONTIER: RISER_FRONTIER_COMMIT, LEVEL_POLICY_REALIZATION: LEVEL_POLICY_COMMIT } : {}), ...(hasDeepGap ? { V41_PACKAGE: V41_COMMIT, DEEP_GAP_CENSUS: DEEP_GAP_CENSUS_COMMIT, FULL_BOOK_PNL_METHOD: FULL_BOOK_PNL_COMMIT } : {}), ...(isAttribution ? { ARM_FIRST_EVIDENCE: ARM_FIRST_EVIDENCE_COMMIT, LOOSEN_ONE_CENT: LOOSEN_ONE_CENT_COMMIT } : {}), ...(isV45 ? { V43_OPERATIVE: V43_COMMIT, V43_RECALIBRATION: V43_RECALIBRATION_COMMIT, V43_RESIDUAL_DOCKET: V43_RESIDUAL_DOCKET_COMMIT } : {}), ...(isV46 ? { V45_OPERATIVE: V45_COMMIT, STRICT_ASK_CREDIT_FOOTPRINT: STRICT_ASK_FOOTPRINT_COMMIT } : {}), ...(isV47 ? { V45_OPERATIVE: V45_COMMIT, SURECH_RENDER: SURECH_RENDER_COMMIT } : {}), ...(isV48 ? { V47_OPERATIVE: V47_COMMIT, TRADES_TRUTH_RECUT: TRADES_TRUTH_RECUT_COMMIT } : {}), ...(isV49 ? { V47_OPERATIVE: V47_COMMIT, STANDABILITY_V2: STANDABILITY_V2_COMMIT, HERKAZ_EXEMPLAR: HERKAZ_EXEMPLAR_COMMIT } : {}) },
      public: {
        [path.relative(repo, policyFile).replaceAll("\\", "/")]: { sha256: fileHash(policyFile), bytes: fs.statSync(policyFile).size },
        [path.relative(repo, builderFile).replaceAll("\\", "/")]: { sha256: fileHash(builderFile), bytes: fs.statSync(builderFile).size },
        ...(isPlacementStack ? { [path.relative(repo, wrapperFile).replaceAll("\\", "/")]: { sha256: fileHash(wrapperFile), bytes: fs.statSync(wrapperFile).size } } : {}),
        ...(isV41 ? {
          "arb-executor/tests/test_window1_v41_maker_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine.js")).size },
          "arb-executor/tests/test_window1_v41_maker_machine_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v41_maker_machine_package.js")).size },
        } : {}),
        ...(hasDeepGap ? {
          "arb-executor/analysis/window1_v41_maker_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v41_maker_machine.js")).size },
          "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js")).size },
          "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard.js")).size },
          "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v42_deep_gap_feasibility_guard_package.js")).size },
          [v41LedgerPath]: { sha256: fileHash(path.join(repo, v41LedgerPath)), bytes: fs.statSync(path.join(repo, v41LedgerPath)).size },
        } : {}),
        ...(isV43 ? {
          "arb-executor/tests/test_window1_v43_composed_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine.js")).size },
          "arb-executor/tests/test_window1_v43_composed_machine_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v43_composed_machine_package.js")).size },
        } : {}),
        ...(isV45 ? {
          "arb-executor/analysis/window1_v43_composed_machine.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v43_composed_machine.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v43_composed_machine.js")).size },
          "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v45_guard_release_sibling_credit_package.js")).size },
        } : {}),
        ...(isV46 ? {
          "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit.js")).size },
          "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v46_pair_gated_gap_credit_package.js")).size },
        } : {}),
        ...(isV47 ? {
          "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js")).size },
          "arb-executor/tests/test_window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v47_same_tick_arm_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v47_same_tick_arm_package.js")).size },
        } : {}),
        ...(isV48 ? {
          "arb-executor/analysis/window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v48_trades_as_truth.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth.js")).size },
          "arb-executor/tests/test_window1_v48_trades_as_truth_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v48_trades_as_truth_package.js")).size },
        } : {}),
        ...(isV49 ? {
          "arb-executor/analysis/window1_v47_same_tick_arm.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")), bytes: fs.statSync(path.join(repo, "arb-executor/analysis/window1_v47_same_tick_arm.js")).size },
          "arb-executor/tests/test_window1_v49_evidenced_level_standing.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing.js")).size },
          "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v49_evidenced_level_standing_package.js")).size },
        } : {}),
        ...(isV40 ? { [v39TelemetryPath]: { sha256: fileHash(path.join(repo, v39TelemetryPath)), bytes: fs.statSync(path.join(repo, v39TelemetryPath)).size } } : {}),
        [`${GAP_PACKAGE}/UNION_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")).size },
        [`${GAP_PACKAGE}/V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")).size },
      },
      frozen_V36: { WINDOW1_SPAN_804: { sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")), bytes: fs.statSync(path.join(v36Package, "WINDOW1_SPAN_804.json")).size }, STRICT_DECISION_TRACE_1608: { sha256: fileHash(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")), bytes: fs.statSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")).size } },
      git_bound_receipts: isPlacementStack ? { [counterPath]: { commit: COUNTERFACTUAL_COMMIT, sha256: shaBytes(counterBytes), bytes: counterBytes.length }, ...(isV39 ? { [anatomyPath]: { commit: FALLER_ANATOMY_COMMIT, sha256: shaBytes(anatomyBytes), bytes: anatomyBytes.length } } : {}), ...(isMaker41 ? { [causalReachPath]: { commit: CAUSAL_REACH_COMMIT, sha256: shaBytes(causalReachBytes), bytes: causalReachBytes.length }, [riserFrontierPath]: { commit: RISER_FRONTIER_COMMIT, sha256: shaBytes(riserFrontierBytes), bytes: riserFrontierBytes.length }, [levelPolicyPath]: { commit: LEVEL_POLICY_COMMIT, sha256: shaBytes(levelPolicyBytes), bytes: levelPolicyBytes.length } } : {}), ...(hasDeepGap ? { [deepGapCensusPath]: { commit: DEEP_GAP_CENSUS_COMMIT, sha256: shaBytes(deepGapCensusBytes), bytes: deepGapCensusBytes.length }, [fullBookReceiptPath]: { commit: FULL_BOOK_PNL_COMMIT, sha256: shaBytes(fullBookReceiptBytes), bytes: fullBookReceiptBytes.length }, [closeAuditPath]: { commit: FULL_BOOK_PNL_COMMIT, sha256: shaBytes(closeAuditBytes), bytes: closeAuditBytes.length } } : {}), ...(isAttribution ? { [armFirstEvidencePath]: { commit: ARM_FIRST_EVIDENCE_COMMIT, sha256: shaBytes(armFirstEvidenceBytes), bytes: armFirstEvidenceBytes.length }, [loosenOneCentPath]: { commit: LOOSEN_ONE_CENT_COMMIT, sha256: shaBytes(loosenOneCentBytes), bytes: loosenOneCentBytes.length } } : {}), ...(isV45 ? { [v43RecalibrationPath]: { commit: V43_RECALIBRATION_COMMIT, sha256: shaBytes(v43RecalibrationBytes), bytes: v43RecalibrationBytes.length }, [v43DocketPath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(v43DocketBytes), bytes: v43DocketBytes.length }, [luztseMarksPath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(luztseMarksBytes), bytes: luztseMarksBytes.length }, [luztseTimelinePath]: { commit: V43_RESIDUAL_DOCKET_COMMIT, sha256: shaBytes(luztseTimelineBytes), bytes: luztseTimelineBytes.length } } : {}), ...(isV46 ? { [frozenV45ControlPath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45ControlBytes), bytes: frozenV45ControlBytes.length }, [frozenV45ScorePath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45ScoreBytes), bytes: frozenV45ScoreBytes.length }, [frozenV45PolicyPath]: { commit: V45_COMMIT, sha256: shaBytes(frozenV45PolicyBytes), bytes: frozenV45PolicyBytes.length }, [strictAskFootprintPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(strictAskFootprintBytes), bytes: strictAskFootprintBytes.length }, [strictAskFootprintMdPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(strictAskFootprintMdBytes), bytes: strictAskFootprintMdBytes.length }, [panfalMarksPath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(panfalMarksBytes), bytes: panfalMarksBytes.length }, [panfalTimelinePath]: { commit: STRICT_ASK_FOOTPRINT_COMMIT, sha256: shaBytes(panfalTimelineBytes), bytes: panfalTimelineBytes.length } } : {}), ...(isV48 ? { [tradesTruthRecutPath]: { commit: TRADES_TRUTH_RECUT_COMMIT, sha256: shaBytes(tradesTruthRecutBytes), bytes: tradesTruthRecutBytes.length }, [tradesTruthRecutMdPath]: { commit: TRADES_TRUTH_RECUT_COMMIT, sha256: shaBytes(tradesTruthRecutMdBytes), bytes: tradesTruthRecutMdBytes.length } } : {}), ...(isV49 ? { [standabilityPath]: { commit: STANDABILITY_V2_COMMIT, sha256: shaBytes(standabilityBytes), bytes: standabilityBytes.length }, [standabilityMdPath]: { commit: STANDABILITY_V2_COMMIT, sha256: shaBytes(standabilityMdBytes), bytes: standabilityMdBytes.length }, [herkazPath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazBytes), bytes: herkazBytes.length }, [herkazMarksPath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazMarksBytes), bytes: herkazMarksBytes.length }, [herkazTimelinePath]: { commit: HERKAZ_EXEMPLAR_COMMIT, sha256: shaBytes(herkazTimelineBytes), bytes: herkazTimelineBytes.length } } : {}) } : {},
      private_prints: printLoad.receipt,
      private_tapes: tapeHashes,
    }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  if (isAttribution) {
    async function* attributionEvents(kind) {
      for (const spec of machineSpecs) for (const event of machineRuns.get(spec.name)[kind]) yield { machine: spec.name, clauses: policy.normalizedClauses(spec.clauses), ...event };
    }
    async function* attributionFullBookRows() {
      for (const row of attributionRows) for (const event of row.full_book_rows) yield { machine: row.machine, clauses: row.clauses, ...event };
    }
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_MARKET_EVENT_LEDGER.jsonl.gz"), attributionEvents("marketEvents"));
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_STRICT_EVENT_LEDGER.jsonl.gz"), attributionEvents("strictEvents"));
    await writeGzipRowsFile(path.join(output, "ATTRIBUTION_FULL_BOOK_LEDGER.jsonl.gz"), attributionFullBookRows());
  }
  await writeGzipRowsFile(path.join(output, "ACTION_TRACE.jsonl.gz"), allActions);
  write("REPORT.md", isV49
    ? `# V49 evidenced-level standing - ${v49Acceptance.pass ? "PASS" : "BLOCKED / V47 REMAINS OPERATIVE"}\n\nV49 replaces V47's universal tracking-rest +1-cent loosen with one causal rule: stand at current best bid P only after an earlier true trade printed at-or-below P or the own best bid continuously stood at P for V47's inherited ${policy.PERSISTENT_LEVEL_SECONDS}-second persistence interval. A historical bid sighting alone has no authority. Without either receipt the bid-minus-one tracker runs; persistent joins and WTA holds are never overwritten. Pair cap, post-only sanity, deep-gap guard, sibling-credit release, same-tick arming, and the hard edge remain unchanged.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET.completed_pairs}, under par ${row.MARKET.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET.frontier.LE_93}/${row.MARKET.frontier.LE_95}/${row.MARKET.frontier.LE_97}/${row.MARKET.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V47 trades-as-truth baseline reproduction: ${v49BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Evidenced-standing actions / legs / games: ${v49EvidenceLedger.summary.evidenced_actions}/${v49EvidenceLedger.summary.evidenced_legs}/${v49EvidenceLedger.summary.evidenced_games}.\n- Outcome columns: gained ${v49EvidenceLedger.summary.fills_gained}; favorable reprices ${v49EvidenceLedger.summary.fills_repriced_favorable}; adverse reprices ${v49EvidenceLedger.summary.fills_repriced_adverse}; lost ${v49EvidenceLedger.summary.fills_lost}.\n- HERKAZ: ${namedV49.rows.HERKAZ.V49.combined_entry_cents ?? "INCOMPLETE"}; HER ${namedV49.rows.HERKAZ.V49.legs.HER.entry_cents ?? "UNFILLED"}; named mechanism ${namedV49.assertions.HERKAZ_HER_trade_truth_fill ? "PASS" : "FAIL"}.\n- fe4747cd freezes 81 games / 1,162c only as aggregate. It exposes 20 detailed WINDOW_LAWFUL_EVIDENCE identities; ${v49WindowTarget.detailed_at_or_better}/${v49WindowTarget.detailed_rows} are credited at-or-better and ${v49WindowTarget.detailed_pair_conversions} convert. Whole-population executable pair conversions versus V47: ${v49WindowTarget.executable_all_population_pair_conversions_vs_V47}. No unstated 81-row intersection was fabricated.\n- Bound named regressions: ${namedV49.pass ? "ZERO" : "PRESENT"}. Aggregate targets are null; observed values were not forced.\n- Overall: ${v49Acceptance.pass ? "PASS" : "BLOCKED"}.\n`
    : isV48
    ? `# V48 trades-as-truth crediting - ${v48Acceptance.pass ? "PASS" : "BLOCKED / V47 REMAINS OPERATIVE"}\n\nV48 changes one credit law on frozen V47: a lawful standing rest credits when any identified true trade prints at-or-below its level strictly after the rest stood. Ask observations remain placement inputs only. Aggressor side, dwell, displayed size, arrival direction, and the prior channel taxonomy are not credit filters or floor inputs. Strict seller-aggressed print crossing remains a separate build-verification ruler.\n\n${attributionRows.map((row) => `- ${row.machine} [${row.market_mode}]: completed ${row.MARKET.completed_pairs}, under par ${row.MARKET.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET.frontier.LE_93}/${row.MARKET.frontier.LE_95}/${row.MARKET.frontier.LE_97}/${row.MARKET.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V47 reproduction: ${v48BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- The operative V47 placement stack is mixed; it is not mislabeled bid-1. The three requested executable rungs are scored independently.\n- Selected ladder by frozen full-book-first rule: ${v48SelectedRung}.\n- Traded-floor re-sum: ${JSON.stringify(v48TradedFloors.aggregate.traded_floor_classes)}; flips ${JSON.stringify(v48TradedFloors.aggregate.flips)}.\n- LUZTSE|TSE credit receipt: ${namedV48.LUZTSE_TSE.pass ? "PASS" : "FAIL"}; ${namedV48.LUZTSE_TSE.fills.length ? JSON.stringify(namedV48.LUZTSE_TSE.fills[0].evidence) : "NO QUALIFYING PRINT"}.\n- SALIBR|IBR outcomes are frozen rung-by-rung in NAMED_V48_RECEIPT.json.\n- Bound named regressions: ${namedV48.pass ? "ZERO" : "PRESENT"}. Aggregate targets were intentionally null; observed numbers were not forced.\n- Overall: ${v48Acceptance.pass ? "PASS" : "BLOCKED"}.\n`
    : isV47
    ? `# V47 same-tick arm - ${v47Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V45 REMAINS OPERATIVE"}\n\nV47 freezes one pipeline-correctness invariant on operative V45: a changed deep-join qualification and the placement decision are one receipt-local operation. Persistence, first-evidence arming, targets, guards, caps, sanity, fill rulers, and the hard edge are unchanged.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V45 reproduction: ${v47BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- SEG_C qualification rows: ${v47SegCFootprint.summary.qualification_rows}; V45/V47 positive qualification-to-post rows ${v47SegCFootprint.summary.V45_positive_qualification_to_post_rows}/${v47SegCFootprint.summary.V47_positive_qualification_to_post_rows}; V47 positive scheduler-latency rows ${v47SegCFootprint.summary.V47_positive_scheduler_latency_rows}. Qualification-to-post delay caused by an unchanged guard is reported separately and is not scheduler latency.\n- Changed outcomes: ${v47SegCFootprint.summary.outcome_changed_rows}; changed action streams: ${v47Differential.changed_leg_streams}.\n- SURECH remains unfilled as ordered; the 8877c2d5 render is older L4 archetype evidence, not a frozen V45 trace. The executable V45 baseline already posted each unguarded changed join on its qualifying receipt, so V47's correctness invariant yields zero score delta rather than a manufactured gain.\n- Named zero-regression checks: ${namedV47.pass ? "PASS" : "FAIL"}.\n- Acceptance: zero scheduler latency ${v47Acceptance.correctness.pass ? "PASS" : "FAIL"}; zero regressions ${v47Acceptance.zero_regressions.pass ? "PASS" : "FAIL"}; gain required NO; overall ${v47Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV46
    ? `# V46 pair-gated gap credit - ${v46Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V45 REMAINS OPERATIVE"}\n\nV46 adds one clause to frozen operative V45: on a FALLING leg with an existing rest, a single-receipt ask gap of at least ${policy.ASK_GAP_CREDIT_MIN_CENTS} cents licenses a reprice down only after the game's other expression is already credited. Without sibling credit the V45 action stream is unchanged. The reprice posts at min(current ask minus one, pair cap); fills still require an inherited later market-union or strict-print receipt.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V45 reproduction: ${v46BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Gap-credit walks: ${v46GapLedger.summary.authorized_walks} across ${v46GapLedger.summary.authorized_legs} legs; filled ${v46GapLedger.summary.authorized_walks_that_filled}.\n- Two columns: completion gains ${v46GapLedger.summary.two_columns.pairs_completed.events}; new exposure ${v46GapLedger.summary.two_columns.new_exposure.events}.\n- Sibling-uncredited refusal receipts: ${v46GapLedger.summary.sibling_uncredited_refusal_receipts} across ${v46GapLedger.summary.sibling_uncredited_refusal_legs} legs. The frozen aa884cc5 footprint's 11 naked-knife legs / median +44c remain an analytical binding, not a coerced replay count.\n- PANFAL ${named.PANFAL.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}: ${namedV46.PANFAL_mechanism_diagnosis.conclusion}.\n- ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n- Bar: completed >=396 ${v46Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1774c ${v46Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; zero bound regressions ${v46Acceptance.zero_bound_regressions.pass ? "PASS" : "FAIL"}; named ${v46Acceptance.named_checks.pass ? "PASS" : "FAIL"}; overall ${v46Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV45
    ? `# V45 guard release at sibling credit — ${v45Acceptance.pass ? "PASS / OPERATIVE" : "BLOCKED / V43 REMAINS OPERATIVE"}\n\nV45 adds exactly one clause to operative V43: the pre-fill T=10 deep-gap guard remains unchanged, but its authority over the other leg terminates immediately when the sibling is credited. The released rest is posted from the last lawful own-book state, bounded by the fixed 99-minus-sibling-entry pair cap and the inherited sanity bound.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Frozen V43 reproduction: ${v45BaselineReproduction.pass ? "PASS" : "FAIL"}.\n- Post-credit releases: ${v45ReleasedRestLedger.summary.released_rests}; filled ${v45ReleasedRestLedger.summary.released_and_filled}; unfilled ${v45ReleasedRestLedger.summary.released_unfilled}.\n- Two columns: completion gains ${v45ReleasedRestLedger.summary.two_columns.pairs_completed.events}; new exposure ${v45ReleasedRestLedger.summary.two_columns.new_exposure.events}.\n- Named LUZTSE ${named.LUZTSE.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; COLCER ${named.COLCER.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.COLCER.disposition}; SMIYUN ${named.SMIYUN.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.SMIYUN.disposition}; VANLEE ${named.VANLEE.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.VANLEE.disposition}; SAINUG ${named.SAINUG.MARKET_UNION_REACH.combined_entry_cents ?? namedV45.rows.SAINUG.disposition}.\n- PENTHA and SHEOLI remain unchanged because neither receives a sibling credit. ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n- Bar: completed >=395 ${v45Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1748c ${v45Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; naked book >-162c ${v45Acceptance.naked_pnl_cents.pass ? "PASS" : "FAIL"}; named ${v45Acceptance.named_checks.pass ? "PASS" : "FAIL"}; overall ${v45Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV43
    ? `# V43 composed machine — ${v43Acceptance.pass ? "PASS" : "BLOCKED / NOT OPERATIVE"}\n\nV43 evaluates all eight combinations of exactly three receipt-priced clauses on frozen V41 from one shared 804-event input load: first-evidence arming only (the adverse walk-lag removal is excluded), the T=10 deep-gap feasibility guard, and the +1c tracking-rest loosening. V41's maker-only, no-clock, pair-cap, sanity-bound, and hard pre-bell laws remain in force.\n\n${attributionRows.map((row) => `- ${row.machine}: completed ${row.MARKET_UNION_REACH.completed_pairs}, under par ${row.MARKET_UNION_REACH.under_par_pairs}, locked ${row.FULL_BOOK.completed_locked_cents}c, naked ${row.FULL_BOOK.naked_pnl_cents}c, true book ${row.FULL_BOOK.true_book_net_cents}c, frontier ${row.MARKET_UNION_REACH.frontier.LE_93}/${row.MARKET_UNION_REACH.frontier.LE_95}/${row.MARKET_UNION_REACH.frontier.LE_97}/${row.MARKET_UNION_REACH.frontier.LT_100}; strict ${row.STRICT_PRINT_CROSS.completed_pairs}.`).join("\n")}\n\n- Receipt single-clause reproduction: ${v43Acceptance.receipt_single_clause_reproduction.pass ? "PASS" : "FAIL"}. The controlling ARM and +1 receipts are static analysis-seat re-scores, not executable decision traces; V43 does not coerce their aggregate values into replay output.\n- Composition bar: completed >=313 ${v43Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >1001c ${v43Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; named regressions ${v43Acceptance.named_regressions.pass ? "ZERO" : "PRESENT"}; overall ${v43Acceptance.pass ? "PASS" : "BLOCKED"}.\n- Named V43: KIRSEK ${named.KIRSEK.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; PUTJEA exact 64/93/cap35 fingerprint ${namedV43.assertions.PUTJEA_fingerprint_pass ? "PASS" : "FAIL"}; BORDIM DIM not withheld ${namedV43.assertions.BORDIM_DIM_not_withheld ? "PASS" : "FAIL"}.\n- Because the receipt and named laws do not reproduce, V43 does not supersede V41 even though its observed aggregate numeric bars clear. No forced or post-hoc aggregate is emitted as an executable score.\n- Market value uses CANON union channels; strict print crossing remains build verification only.\n`
    : isV42
    ? `# V42 deep-gap feasibility guard\n\nV42 changes one V41 clause: a V41 rest target L is temporarily unlawful only while (99-L) is strictly more than 10 cents below the sibling's contemporaneous best ask. The clause is re-evaluated on every own-book receipt and every sibling-book receipt while withheld. It lifts without a clock the moment the live gap is at most 10 cents. Missing sibling-book evidence never gates V41. All placement, state, persistence-join, pair-cap, fill, and edge laws remain V41.\n\n- Market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; locked ${marketScore.locked_cents_per_contract}c. Strict build verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- V41 full book reconstructed: completed ${v41FullBook.aggregate.completed_pairs}, locked ${v41FullBook.aggregate.completed_locked_cents}c, naked ${v41FullBook.aggregate.naked_pnl_cents}c, true book ${v41FullBook.aggregate.true_book_net_cents}c.\n- V42 full book: completed ${v42FullBook.aggregate.completed_pairs}, locked ${v42FullBook.aggregate.completed_locked_cents}c, naked ${v42FullBook.aggregate.naked_pnl_cents}c, true book ${v42FullBook.aggregate.true_book_net_cents}c; delta ${v42FullBook.aggregate.true_book_net_cents - v41FullBook.aggregate.true_book_net_cents}c.\n- Acceptance: completed >=240 ${v42Acceptance.completed_pairs.pass ? "PASS" : "FAIL"}; true book >+782c ${v42Acceptance.true_book_net_cents.pass ? "PASS" : "FAIL"}; overall ${v42Acceptance.pass ? "PASS" : "FAIL"}.\n- Guard affected ${v42GuardLegs.length} legs across ${v42GuardLegs.reduce((sum, row) => sum + row.withhold_episodes, 0)} withholding episodes; ${v42GuardLegs.reduce((sum, row) => sum + row.lifts, 0)} receipt-causal lifts.\n- Guard columns: losses avoided ${deepGapDiff.aggregate.losses_avoided.events}/${deepGapDiff.aggregate.losses_avoided.cents}c; completed pairs forfeited ${deepGapDiff.aggregate.pairs_forfeited.events}/${deepGapDiff.aggregate.pairs_forfeited.cents}c; winning naked legs forfeited ${deepGapDiff.aggregate.winning_naked_forfeited.events}/${deepGapDiff.aggregate.winning_naked_forfeited.cents}c.\n- PUTJEA fingerprint ${namedV42.assertions.PUTJEA_fingerprint_pass ? "PASS" : "FAIL"}; ROCBUE ${namedV42.assertions.ROCBUE_touched ? "WITHHELD" : "NOT_WITHHELD"}; KREZHE ${namedV42.assertions.KREZHE_touched ? "WITHHELD" : "NOT_WITHHELD"}; BORDIM DIM not withheld ${namedV42.assertions.BORDIM_DIM_not_withheld ? "PASS" : "FAIL"}.\n`
    : isV41
    ? `# V41 maker machine\n\nV41 deletes the take path. Every leg carries one post-only rest from its first two-sided book. FALLING and SETTLED use the V36 incumbent walking laws. RISING tracks bid minus one until a bid level has persisted for ${policy.PERSISTENT_LEVEL_SECONDS} seconds, then the same single rest joins the deepest armed persistent level; the seller-hit trigger is absent. The WTA other-expression-FALLING hold, rest-below-ask sanity bound, lazy first-fill pair cap, no-clock law, and hard pre-bell edge remain in force.\n\nMarket scoring uses CANON union channels; strict seller-aggressed print crossing is build verification only. Maker fees are zero.\n\n- V41 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; locked ${marketScore.locked_cents_per_contract}c per-contract aggregate (${marketScore.locked_cents_five_lot}c at five lots); frontier ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}/${marketScore.frontier.LT_100}.\n- V41 strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- V36 gross completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}. V36 taker legs charged: ${v36NetScore.aggregate.taker_legs_charged}; gross locked ${v36NetScore.aggregate.gross_locked_cents_five_lot}c; fees on all credited taker legs ${v36NetScore.aggregate.taker_fees_all_credited_legs_five_lot}c; portfolio net ${v36NetScore.aggregate.net_locked_after_all_entry_taker_fees_five_lot}c.\n- Causal-reach reference: ${causalReachReceipt.CAUSAL_REACH.under_par} under-par / ${causalReachReceipt.CAUSAL_REACH.locked}c locked.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}.\n- Persistent JOIN legs: ${joinReceipt.join_legs}; market fills after join: ${joinReceipt.market_credited_after_join}; strict fills after join: ${joinReceipt.strict_credited_after_join}.\n- Rest sanity violations: ${sanity.post_decision_rest_at_or_above_ask_violations}. Market taker fills: ${marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length}.\n- ARNROM observed: ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; exact rest/fill sequence is frozen in NAMED_V41_RECEIPT.json. BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; KRUFER ${named.KRUFER.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}.\n`
    : isV40
    ? `# V40 placement stack on incumbent direction\n\nV40 inherits V36's state machine and mature-floor take path. The V39 causal classifier is severed and vaulted CLASSIFIER_RESEARCH_OPEN after 437/1,279 reach-moment calls (34.17%). V40 adds only the persistent-level join gated by V36's own RISING state, the WTA other-expression-FALLING deeper hold, and the universal rest-below-ask sanity bound.\n\nMarket grade uses the CANON union-reach channels; strict seller-print crossing plus proven takes is build verification.\n\n- V36 frozen completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}; frontier ${v36Score.frontier.LE_93}/${v36Score.frontier.LE_95}/${v36Score.frontier.LE_97}.\n- V40 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}; frontier ${marketScore.frontier.LE_93}/${marketScore.frontier.LE_95}/${marketScore.frontier.LE_97}.\n- Acceptance bar completed>=270 and <=93/<=95>=12/24: ${acceptance.pass ? "PASS" : "FAIL"}.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}; shallow ${marketGrades.aggregate.shallow_gap_cents.sum}c; measurable residual ${marketGrades.aggregate.measurable_residual_cents.sum}c.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Persistent JOIN legs: ${joinReceipt.join_legs}; zero later certified seller hits at the joined level: ${joinReceipt.zero_post_join_certified_seller_hits}.\n- Rest sanity: ${sanity.post_decision_rest_at_or_above_ask_violations} violations after ${sanity.bound_application_receipts} bound applications.\n- Named market outcomes: ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}. BOSCOP post-join certified seller hits at COP 47: ${joinReceipt.BOSCOP_COP?.post_join_certified_seller_aggressed_prints_at_level ?? "NOT_JOINED"}.\n`
    : isV39
    ? `# V39 corrected placement stack\n\nV39 runs on frozen V36 with its mature-floor take path intact. The receipt-causal direction classifier combines trailing quote-path and July-6 pressure without reading an ex-post path label; opposing directional votes settle. RISING sides may join a bid only after 300 seconds of continuous residency and a last-traded-at-level book receipt. WTA RISING sides whose other expression reads FALLING hold to the deeper causal pulse/reach level. Every rest is strictly below the current ask.\n\nMarket grade uses the CANON union-reach channels; strict seller-print crossing plus proven takes is build verification.\n\n- V36 frozen completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}.\n- V39 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}. This regresses the frozen V36 count and therefore does not supersede V36.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}; shallow ${marketGrades.aggregate.shallow_gap_cents.sum}c; measurable residual ${marketGrades.aggregate.measurable_residual_cents.sum}c.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Direction telemetry: ${directionTelemetry.aggregate.correct_receipts}/${directionTelemetry.aggregate.eligible_receipts} eligible receipt calls correct and ${directionTelemetry.aggregate.reach_moment_correct_legs}/${directionTelemetry.aggregate.reach_moment_eligible_legs} reach-moment legs correct; ex-post labels consumed by policy: 0.\n- The 2b45d146 115-side cohort has no frozen identity list, so recovery is not fabricated; the independently reproducible c3961e2c cohort has ${mislabelRecovery.independently_reconstructable_c396_cohort.sides} sides and ${mislabelRecovery.independently_reconstructable_c396_cohort.recovered_at_or_better_than_reach} previously uncredited sides recovered at/better than reach.\n- Rest sanity: ${sanity.post_decision_rest_at_or_above_ask_violations} violations after ${sanity.bound_application_receipts} bound applications.\n- Named market outcomes: ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}. BOSCOP causally joined COP at 47 but had no strictly later union-reach receipt; the 2b45d146 counterfactual's pair-77 credit is not replay-causal and is not imported.\n`
    : `# V38 maker-only machine\n\nV38 removes the take path from the executable policy source. FALLING preserves V36 no-chase rest behavior; SETTLED tracks bid minus one; RISING rests at the lowest ask level revisited at least twice inside the inherited 300-second receipt horizon, only after the standing ask has moved above that floor so the new order remains post-only. Pair cap, lazy first-fill coupling, no-clock law, and the V36 hard pre-bell edge remain intact.\n\nMarket grade uses the CANON union reach ruler; strict seller-print crossing is printed only as build verification.\n\n- Market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}.\n- Market reach grades across the 637-game answer key: ${JSON.stringify(marketGrades.aggregate.grades)}.\n- Market shallow gap cents: ${marketGrades.aggregate.shallow_gap_cents.sum}; measurable residual cents: ${marketGrades.aggregate.measurable_residual_cents.sum}.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Named reach: ARNROM ${named.ARNROM.reach_combined_cents}; BOSCOP ${named.BOSCOP.reach_combined_cents}; NIKVRB ${named.NIKVRB.reach_combined_cents}; GANJAN ${named.GANJAN.reach_combined_cents}.\n`);
  const namesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  write("DETERMINISM_RECEIPT.json", canonical(determinism));
  writeManifest(output);
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    writeManifest(compare);
    ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "finalized artifact manifests differ");
  }
  process.stdout.write(canonical({ output, MARKET: marketScore, STRICT_PRINT_CROSS: strictScore, ...(isV49 ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v49Acceptance, EVIDENCED_STANDING: v49EvidenceLedger.summary, WINDOW_TARGET: v49WindowTarget, named: namedV49 } : isV48 ? { ATTRIBUTION: attributionRows.map(({ full_book_rows, traded_floor_rows, traded_floor_games, ...row }) => row), ACCEPTANCE: v48Acceptance, TRADED_FLOOR_RE_SUM: v48TradedFloors.aggregate, SELECTED_LADDER: v48SelectedRung, named: namedV48 } : isV47 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v47Acceptance, SEG_C: v47SegCFootprint.summary, named } : isV46 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v46Acceptance, GAP_CREDIT: v46GapLedger.summary, named } : isV45 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v45Acceptance, RELEASES: v45ReleasedRestLedger.summary, named } : isV43 ? { reach_grade: marketGrades.aggregate, ATTRIBUTION: attributionRows.map(({ full_book_rows, ...row }) => row), ACCEPTANCE: v43Acceptance, named } : isV42 ? { reach_grade: marketGrades.aggregate, FULL_BOOK: v42FullBook.aggregate, ACCEPTANCE: v42Acceptance, GUARD: { affected_legs: v42GuardLegs.length, differential: deepGapDiff.aggregate }, named } : { reach_grade: marketGrades.aggregate, named }) }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
