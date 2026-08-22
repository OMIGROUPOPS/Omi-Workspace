#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const EVENT_ID = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
const DISCOVERY = 1784007323;
const FORMATION_END = 1784007603;
const TRUE_BELL = 1784078400;
const FABLE_COMMIT = "afe38772";
const RAW_COMMIT = "ef6f3975";
const LAW_INDEX_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md";
const RAW_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAJSVA_RAW_TAPE.md";
const RAW_RECON_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAJSVA_RAW_TAPE_RECONCILIATION.json";
const FINDINGS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/FINDINGS_VERIFICATION_SEAT.md";
const CORRECTIONS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_CORRECTIONS.jsonl";
const STORY_PATH = ".claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES.md";
const STORY_RECEIPT_PATH = ".claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FOUR_STORIES_RECEIPT.json";
const FUNCTIONALITY_PATH = ".claude/window1_live_v4_replay/v54_functionable_four_stories_v6_20260821/FUNCTIONALITY_RECEIPT.json";
const EXPLAINED_PATH = ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/GAME_EXPLAINED_LAJSVA.md";
const EXPLANATION_RECEIPT_PATH = ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/EXPLANATION_RECEIPT.json";
const CITATION_WELD_PATH = ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/CITATION_WELD_RECEIPT.json";
const OUT_REL = ".claude/window1_live_v4_replay/lajsva_case_study_v1_20260822";
const READER_NAMES = [
  "anchor_settle", "opening_split", "drift", "steps_stillness",
  "shape_survival", "ripeness", "lows_travel", "joint_state_spread_dwell",
  "divots", "depth_size", "volume", "sibling_state", "category",
  "time_in_window", "books", "half_pair_state",
];

function fail(message) { throw new Error(message); }
function ensure(condition, message) { if (!condition) fail(message); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function iso(epoch) { return new Date(epoch * 1000).toISOString(); }
function fmt(value, digits = 3) { return Number.isFinite(value) ? Number(value).toFixed(digits) : "GAP"; }
function h(value) {
  return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}
function md(value) { return String(value ?? "").replaceAll("|", "\\|").replaceAll("\n", " "); }
function git(repo, args, encoding = null) {
  return execFileSync("git", args, { cwd: repo, encoding, maxBuffer: 256 * 1024 * 1024 });
}
function gitShow(repo, commit, file) { return git(repo, ["show", `${commit}:${file}`]); }
function currentBlob(repo, file) { return gitShow(repo, "HEAD", file); }
function writeText(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8");
}
function writeJson(file, value) { writeText(file, canonical(value)); }
function fileReceipt(file, root) {
  const bytes = fs.readFileSync(file);
  return { path: path.relative(root, file).replaceAll("\\", "/"), bytes: bytes.length, sha256: sha256(bytes) };
}
function dataForScript(value) { return JSON.stringify(value).replaceAll("<", "\\u003c"); }
function lineReceipt(commit, file, line, label = null) {
  return { commit, path: file, line, label, id: `${commit}:${file}#L${line}` };
}

function parseRawTape(rawBuffer) {
  const lines = rawBuffer.toString("utf8").split(/\r?\n/);
  const rows = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!/^\d+\.\d{3} \|/.test(line)) continue;
    const parts = line.split(" | ");
    ensure(parts.length === 9, `raw tape column count line ${i + 1}: ${parts.length}`);
    const [epochRaw, deltaRaw, leg, bidRaw, askRaw, lastRaw, trade, marker, source] = parts;
    const row = {
      line: i + 1,
      epoch: Number(epochRaw),
      delta: Number(deltaRaw),
      leg,
      bid: bidRaw === "" ? null : Number(bidRaw),
      ask: askRaw === "" ? null : Number(askRaw),
      last: lastRaw === "" || lastRaw === "0" ? null : Number(lastRaw),
      trade,
      marker,
      source,
      receipt: `${RAW_COMMIT}:${RAW_PATH}#L${i + 1}`,
    };
    if (source.startsWith("ticks#row-")) row.kind = "book";
    else if (trade.includes("trade_id=")) row.kind = "trade";
    else if (marker.startsWith("REFLEX ")) row.kind = "reflex";
    else if (marker.startsWith("V6-PASS1")) row.kind = "v6";
    else if (marker.startsWith("FILL ")) row.kind = "fill";
    else if (marker.startsWith("FLOOR PRINT")) row.kind = "floor";
    else if (marker.startsWith("DISCOVERY")) row.kind = "discovery";
    else if (marker.startsWith("FORMATION END")) row.kind = "formation";
    else if (marker.startsWith("TRUE BELL")) row.kind = "bell";
    else row.kind = "other";

    if (row.kind === "trade") {
      const match = trade.match(/^(\d+)c x ([0-9.]+) taker=(yes|no) trade_id=([a-f0-9-]+)$/);
      ensure(match, `trade parse line ${i + 1}`);
      row.price = Number(match[1]);
      row.quantity = Number(match[2]);
      row.taker = match[3];
      row.trade_id = match[4];
    }
    if (row.kind === "reflex") {
      const match = marker.match(/^REFLEX (PLACE_REST|REPRICE_REST)@(\d+) receipt=(\S+) reason=(\S+)$/);
      ensure(match, `reflex parse line ${i + 1}`);
      row.action = match[1];
      row.price = Number(match[2]);
      row.action_receipt = match[3];
      row.reason = match[4];
    }
    if (row.kind === "v6") {
      const match = marker.match(/(PLACE_REST|REPRICE_REST|HOLD_REST)@(\d+) \(before (NONE|\d+)\)$/);
      ensure(match, `v6 parse line ${i + 1}`);
      row.action = match[1];
      row.price = Number(match[2]);
      row.before = match[3] === "NONE" ? null : Number(match[3]);
    }
    if (row.kind === "fill" || row.kind === "floor") {
      const priceMatch = marker.match(/ (\d+)c/);
      ensure(priceMatch, `${row.kind} price parse line ${i + 1}`);
      row.price = Number(priceMatch[1]);
    }
    rows.push(row);
  }
  ensure(rows.length === 1876, `raw tape rows ${rows.length} != 1876`);

  const state = { LAJ: { bid: null, ask: null }, SVA: { bid: null, ask: null } };
  for (const row of rows) {
    if (row.kind === "book" && state[row.leg]) {
      state[row.leg] = { bid: row.bid, ask: row.ask };
      continue;
    }
    if (row.kind !== "trade") continue;
    const book = state[row.leg];
    row.book_at_print = { ...book };
    ensure(Number.isFinite(book.bid) && Number.isFinite(book.ask), `missing BBO at trade ${row.line}`);
    const bidDistance = Math.abs(row.price - book.bid);
    const askDistance = Math.abs(row.price - book.ask);
    row.flow = bidDistance <= askDistance ? "HIT" : "LIFT";
    row.flow_basis = row.price === book.bid ? "AT_BID" : row.price === book.ask ? "AT_ASK" : `NEAREST_${row.flow === "HIT" ? "BID" : "ASK"}`;
  }

  const counts = {};
  for (const kind of ["book", "trade", "reflex", "v6", "fill", "floor", "discovery", "formation", "bell", "other"])
    counts[kind] = rows.filter((row) => row.kind === kind).length;
  counts.hit = rows.filter((row) => row.kind === "trade" && row.flow === "HIT").length;
  counts.lift = rows.filter((row) => row.kind === "trade" && row.flow === "LIFT").length;
  counts.by_leg = Object.fromEntries(["LAJ", "SVA"].map((leg) => [leg, {
    book: rows.filter((row) => row.kind === "book" && row.leg === leg).length,
    trade: rows.filter((row) => row.kind === "trade" && row.leg === leg).length,
    reflex: rows.filter((row) => row.kind === "reflex" && row.leg === leg).length,
    v6: rows.filter((row) => row.kind === "v6" && row.leg === leg).length,
  }]));
  ensure(counts.book === 1250 && counts.trade === 543 && counts.reflex === 54 && counts.v6 === 21, `ARSMAR counts ${JSON.stringify(counts)}`);
  ensure(counts.hit + counts.lift === counts.trade, "every trade must be lift/hit classified");
  return { lines, rows, counts };
}

function parseReaders(line) {
  const reads = {};
  for (let index = 0; index < READER_NAMES.length; index += 1) {
    const name = READER_NAMES[index];
    const marker = `${name}=`;
    const start = line.indexOf(marker);
    ensure(start >= 0, `story reader missing ${name}`);
    const valueStart = start + marker.length;
    const end = index + 1 < READER_NAMES.length
      ? line.indexOf(` · ${READER_NAMES[index + 1]}=`, valueStart)
      : line.indexOf(". The named neighborhood was", valueStart);
    ensure(end > valueStart, `story reader boundary ${name}`);
    reads[name] = JSON.parse(line.slice(valueStart, end));
  }
  return reads;
}

function mean(values) {
  const valid = values.filter(Number.isFinite);
  return valid.length ? valid.reduce((sum, value) => sum + value, 0) / valid.length : null;
}

function vectorFromReads(reads) {
  const oriented = Object.keys(reads.anchor_settle.anchors_cents).map((id) => ({
    id,
    anchor: reads.anchor_settle.anchors_cents[id],
    drift: reads.drift[id].drift_cents,
    travel: reads.lows_travel[id].travel_cents,
  })).sort((a, b) => (a.anchor ?? 50) - (b.anchor ?? 50) || a.id.localeCompare(b.id));
  const contracts = Object.values(reads.volume).reduce((sum, row) => sum + (Number(row.contracts) || 0), 0);
  return {
    category: reads.category.category,
    anchor_split_cents: reads.opening_split.absolute_split_cents,
    leg0_anchor_cents: oriented[0].anchor,
    leg1_anchor_cents: oriented[1].anchor,
    leg0_drift_cents: oriented[0].drift,
    leg1_drift_cents: oriented[1].drift,
    leg0_travel_cents: oriented[0].travel,
    leg1_travel_cents: oriented[1].travel,
    joint_mid_sum_cents: reads.joint_state_spread_dwell.mid_sum_cents,
    joint_spread_cents: reads.joint_state_spread_dwell.spread_sum_cents,
    inverse_coherence: reads.sibling_state.inverse_coherence,
    volume_log1p: Math.log1p(contracts),
    hours_from_discovery: reads.time_in_window.hours_from_discovery,
    divot_depth_cents: mean(Object.values(reads.divots).map((row) => Number(row.mean_depth_cents))),
    oriented_leg_ids: oriented.map((row) => row.id),
  };
}

function parseStory(storyBuffer, sourceCommit) {
  const lines = storyBuffer.toString("utf8").split(/\r?\n/);
  let inEvent = false;
  const stages = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (line.startsWith("## ")) { inEvent = line === `## ${EVENT_ID}`; continue; }
    if (!inEvent || !line.startsWith("At ")) continue;
    const hoursMatch = line.match(/^At ([0-9.]+) hours from discovery/);
    if (!hoursMatch) continue;
    const hours = Number(hoursMatch[1]);
    const reads = parseReaders(line);
    const afterSummary = line.slice(line.indexOf(". ", line.indexOf("The derivation produced")) + 2);
    const pattern = /At ([0-9.]+) hours from discovery, all sixteen readers fired for ([^.]+)\. The named neighborhood is (.*?)\. ([A-Z0-9]+) has anchor ([^,]+), neighborhood low ratio ([^,]+), lineage target ([^,]+), pair cap ([^,]+), and post-only cap ([^.]+)\. Resources consulted: (.*?)\. ACTION=([^;]+); TARGET_CENTS=([^;]+); ACTIVE_TARGET_BEFORE_CENTS=([^.]+)\./g;
    const matches = [...afterSummary.matchAll(pattern)];
    ensure(matches.length === 2, `story derivation sentences line ${i + 1}: ${matches.length}`);
    const neighbors = matches[0][3].split(", ").map((entry) => {
      const match = entry.match(/^(.*)@([0-9.]+)$/);
      ensure(match, `neighbor parse ${entry}`);
      return { event_id: match[1], score: Number(match[2]) };
    });
    const actions = Object.fromEntries(matches.map((match) => [match[4], {
      leg: match[4],
      anchor: Number(match[5]),
      ratio: Number(match[6]),
      lineage: match[7] === "NONE" ? null : Number(match[7]),
      pair_cap: Number(match[8]),
      post_only_cap: Number(match[9]),
      claimed_resources: match[10].split(", "),
      action: match[11],
      target: match[12] === "NONE" ? null : Number(match[12]),
      before: match[13] === "NONE" ? null : Number(match[13]),
      sentence: match[0],
    }]));
    const gapMatches = [...line.matchAll(/\[RESOURCE-GAP:([^:\]]+):([^\]]+)\]/g)];
    const gaps = gapMatches.map((match) => ({ id: match[1], cause: match[2] }));
    ensure(gaps.length === 1, `stage gap count line ${i + 1}: ${gaps.length}`);
    const scores = neighbors.map((row) => row.score);
    stages.push({
      stage: stages.length + 1,
      line: i + 1,
      hours,
      epoch: DISCOVERY + hours * 3600,
      iso: iso(DISCOVERY + hours * 3600),
      reads,
      fingerprint: vectorFromReads(reads),
      neighbors,
      neighborhood_min: Math.min(...scores),
      neighborhood_max: Math.max(...scores),
      neighborhood_width: Math.max(...scores) - Math.min(...scores),
      actions,
      gaps,
      receipt: `${sourceCommit}:${STORY_PATH}#L${i + 1}`,
    });
  }
  ensure(stages.length === 20, `LAJSVA stages ${stages.length} != 20`);
  return { lines, stages };
}

function findingsReceipts(buffer) {
  const lines = buffer.toString("utf8").split(/\r?\n/);
  const result = {};
  for (const id of ["F-VS-050", "F-VS-052", "F-VS-053", "F-VS-054", "F-VS-055"]) {
    const index = lines.findIndex((line) => line.startsWith(`${id} |`));
    ensure(index >= 0, `finding missing ${id}`);
    result[id] = lineReceipt(FABLE_COMMIT, FINDINGS_PATH, index + 1, id);
  }
  return result;
}

function compactStage(stage) {
  return {
    stage: stage.stage, line: stage.line, hours: stage.hours, epoch: stage.epoch, iso: stage.iso,
    reads: stage.reads, fingerprint: stage.fingerprint, neighbors: stage.neighbors,
    neighborhood_min: stage.neighborhood_min, neighborhood_max: stage.neighborhood_max,
    neighborhood_width: stage.neighborhood_width, actions: stage.actions, gaps: stage.gaps,
    receipt: stage.receipt,
  };
}

function rawCompact(rows) {
  return rows.map((row) => ({
    line: row.line, epoch: row.epoch, delta: row.delta, leg: row.leg, bid: row.bid, ask: row.ask,
    last: row.last, kind: row.kind, price: row.price, quantity: row.quantity, taker: row.taker,
    trade_id: row.trade_id, flow: row.flow, flow_basis: row.flow_basis, book_at_print: row.book_at_print,
    action: row.action, before: row.before, reason: row.reason, action_receipt: row.action_receipt,
    marker: row.marker, source: row.source, receipt: row.receipt,
  }));
}

function notablePrints(rows) {
  const specs = [
    { key: "SVA_FLOOR", leg: "SVA", epoch: 1784020201.830, label: "SVA lawful floor 41¢" },
    { key: "SVA_KISS_6", leg: "SVA", epoch: 1784020209.484, quantity: 6, label: "SVA kiss print 41¢ ×6" },
    { key: "SVA_KISS_10", leg: "SVA", epoch: 1784020209.484, quantity: 10, label: "SVA kiss print 41¢ ×10" },
    { key: "LAJ_FILL", leg: "LAJ", epoch: 1784052830.356, label: "LAJ credited fill print 53¢" },
    { key: "LAJ_FLOOR", leg: "LAJ", epoch: 1784060123.219, label: "LAJ lawful floor 51¢" },
  ];
  return specs.map((spec) => {
    const row = rows.find((candidate) => candidate.kind === "trade" && candidate.leg === spec.leg
      && Math.abs(candidate.epoch - spec.epoch) < 0.002 && (spec.quantity === undefined || candidate.quantity === spec.quantity));
    ensure(row, `notable print ${spec.key}`);
    return { ...spec, price: row.price, trade_id: row.trade_id, flow: row.flow, receipt: row.receipt, line: row.line };
  });
}

function receiptTag(value) { return `[receipt: ${value}]`; }
function gapTag(id, cause = "CAPTURE_TIME_POINT_PROVENANCE_ABSENT") { return `[RESOURCE-GAP: ${id} — ${cause}]`; }

function reportPreamble(title, findings, sourceHead) {
  return `# ${title}\n\n` +
    `CASE STUDY v1 · AS-OCCURRED · ${EVENT_ID}. ${receiptTag(findings["F-VS-052"].id)}\n\n` +
    `This report has the six sections required by F-VS-055. A factual line ends in a receipt; unsupported consultation provenance is printed as GAP. ${receiptTag(findings["F-VS-055"].id)}\n\n` +
    `Source binding: raw tape ${RAW_COMMIT}:${RAW_PATH}; pass-1 story ${sourceHead}:${STORY_PATH}. ${receiptTag(`${RAW_COMMIT}:${RAW_PATH}#L1-L8`)}\n\n`;
}

function buildReflexReport(tape, notable, findings, sourceHead) {
  const actions = tape.rows.filter((row) => row.kind === "reflex");
  const svaFill = tape.rows.find((row) => row.kind === "fill" && row.leg === "SVA");
  const lajFill = tape.rows.find((row) => row.kind === "fill" && row.leg === "LAJ");
  const floorSva = notable.find((row) => row.key === "SVA_FLOOR");
  const floorLaj = notable.find((row) => row.key === "LAJ_FLOOR");
  const rows = actions.map((row, index) => `| ${index + 1} | ${fmt(row.delta / 3600, 6)} | ${row.leg} | ${row.action} | ${row.price}¢ | ${md(row.reason)} | ${md(row.action_receipt)} | ${md(row.receipt)} |`).join("\n");
  return reportPreamble("THE REFLEX'S TRADE REPORT — LAJSVA", findings, sourceHead) +
`## 1 — WHAT I BELIEVED AT OPEN

I held no market belief. My action reason was \`V54_UNDECIDED_CHAMPION_BYTE_EQUAL\`; that is a tracking state, not a story about either player or the pair. ${receiptTag(actions[0].receipt)}

I therefore had no named neighborhood, no causal picture, and no pair-coherent conviction to hand to the sibling after a fill. ${receiptTag(findings["F-VS-053"].id)}

## 2 — WHAT I DECIDED PER SIDE AND WHY (resources named)

On SVA I followed the current champion rest until a 41¢ rest was present. On LAJ I did the same until a 53¢ rest was present. The only machine-written reason on all 54 actions was \`V54_UNDECIDED_CHAMPION_BYTE_EQUAL\`. ${receiptTag(`${actions[0].receipt}; ${actions.at(-1).receipt}`)}

The resources evidenced by the action rows are \`FULL_DECISION_TRACE_5\` and the cited dual-book row on each action. There is no receipt showing that the reflex consulted a corpus, odds store, macro table, or neighbor. ${receiptTag(`${RAW_COMMIT}:${RAW_PATH}#L3`)}

## 3 — EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME

All 54 action rows are reproduced below; hours use the one discovery clock. ${receiptTag(`${RAW_COMMIT}:${RAW_PATH}`)}

| # | Hours | Leg | Action | Rest | Reason at the time | Machine row receipt | Tape receipt |
|---:|---:|---|---|---:|---|---|---|
${rows}

## 4 — WHAT HAPPENED

SVA was credited at 41¢ at ${fmt(svaFill.epoch, 3)} and LAJ was credited at 53¢ at ${fmt(lajFill.epoch, 3)}; the completed pair cost 94¢, or 6¢ under par. ${receiptTag(`${svaFill.receipt}; ${lajFill.receipt}; ${findings["F-VS-052"].id}`)}

The lawful pre-bell floors were SVA 41¢ at ${fmt(floorSva.epoch, 3)} and LAJ 51¢ at ${fmt(floorLaj.epoch, 3)}. Their standing-rest ceiling was 92¢, so the reflex left 2¢ of pair discount uncaptured. ${receiptTag(`${floorSva.receipt}; ${floorLaj.receipt}; ${findings["F-VS-052"].id}`)}

The SVA fill is only a second-grain pass: the rest flapped 41→40→41 inside one recorder second, 16 contracts stood ahead, and the two 41¢ prints totaled exactly 16. Strictly-after subsecond causality is unprovable; credit was fill-model optimism. ${receiptTag(findings["F-VS-054"].id)}

## 5 — MY GRADE OF MY OWN TRADE, GOOD/BAD/MIXED, WITH REASONING

Decision grade: **BAD**. I cannot call a tracking rest a good decision when I held no belief, consulted no evidenced pattern, and did not turn first credit into a sibling plan. ${receiptTag(`${actions[0].receipt}; ${findings["F-VS-053"].id}`)}

Outcome grade: **GOOD, separately**. The recorded outcome completed at 94¢ for Δ6; that favorable result does not retroactively supply the missing decision-time belief. ${receiptTag(findings["F-VS-052"].id)}

## 6 — WHAT I'D FLAG FOR THE LIBRARY

Flag the SVA kiss as a fill-model calibration case: preserve the 1-second ordering, the 41→40→41 flap, the 16-lot ahead, and the 6+10 prints; do not label subsecond ownership proved. ${receiptTag(findings["F-VS-054"].id)}

Flag the missing belief handoff: when first credit is a conviction, the sibling plan must derive from the same pair belief; the reflex did not have such a belief to hand off. ${receiptTag(findings["F-VS-053"].id)}
`;
}

function buildPatternReport(tape, stages, notable, findings, sourceHead) {
  const v6 = tape.rows.filter((row) => row.kind === "v6");
  const floorSva = notable.find((row) => row.key === "SVA_FLOOR");
  const floorLaj = notable.find((row) => row.key === "LAJ_FLOOR");
  const beliefs = stages.map((stage) => `| ${stage.stage} | ${fmt(stage.hours, 6)} | ${stage.neighbors.map((row) => `${row.event_id}@${row.score.toFixed(6)}`).join(", ")} | ${stage.actions.LAJ.target ?? "NONE"}/${stage.actions.SVA.target ?? "NONE"} | ${md(stage.receipt)} · ${gapTag(stage.gaps[0].id)} |`).join("\n");
  const actionRows = v6.map((row, index) => {
    const stage = stages.reduce((best, candidate) => Math.abs(candidate.epoch - row.epoch) < Math.abs(best.epoch - row.epoch) ? candidate : best, stages[0]);
    return `| ${index + 1} | ${fmt(row.delta / 3600, 6)} | ${row.leg} | ${row.action} | ${row.before ?? "NONE"}→${row.price}¢ | target change recorded; capture-time causal consultation provenance GAP | ${md(row.receipt)} · ${md(stage.receipt)} · ${gapTag(stage.gaps[0].id)} |`;
  }).join("\n");
  const final = stages.at(-1);
  const finalNeighbors = final.neighbors.map((row) => `${row.event_id}@${row.score.toFixed(6)}`).join(", ");
  const resources = final.actions.LAJ.claimed_resources.join(", ");
  return reportPreamble("THE PATTERN ENGINE'S TRADE REPORT — LAJSVA", findings, sourceHead) +
`## 1 — WHAT I BELIEVED AT OPEN

At open I oriented the pair SVA(41) / LAJ(59), emitted a graded seven-neighbor neighborhood, and held both sides while formation progress was zero. The emitter's point claim is retained, but its consultation-time row provenance was later gap-stamped. ${receiptTag(stages[0].receipt)} ${gapTag(stages[0].gaps[0].id)}

These are the 20 reported belief stages. The names and scores are the machine's written outputs; “trusted” does not erase the provenance GAP printed beside every stage. ${receiptTag(`${sourceHead}:${STORY_PATH}`)}

| Stage | Hours | Reported named neighborhood | LAJ/SVA derivation | Receipt / gap |
|---:|---:|---|---:|---|
${beliefs}

## 2 — WHAT I DECIDED PER SIDE AND WHY (resources named)

My final reported neighborhood was ${finalNeighbors}. The score band was ${final.neighborhood_min.toFixed(6)}–${final.neighborhood_max.toFixed(6)} (width ${final.neighborhood_width.toFixed(6)}). ${receiptTag(final.receipt)} ${gapTag(final.gaps[0].id)}

For LAJ I reported weighted low ratio ${final.actions.LAJ.ratio.toFixed(12)}: round(59×ratio)=46, then lineage 53 blended to 47; caps 63/52 did not bind below 47. For SVA I reported ${final.actions.SVA.ratio.toFixed(12)}: round(41×ratio)=35, then lineage 41 blended to 36; caps 52/48 left 36. That is the 47/36 rest. ${receiptTag(`${sourceHead}:${EXPLAINED_PATH}#L384; ${sourceHead}:${EXPLAINED_PATH}#L388`)} ${gapTag(final.gaps[0].id)}

The legacy story named these resources: ${resources}. The citation weld found no capture-time point provenance for the consultation sentence, so this report does **not** relabel connectivity as consultation. ${receiptTag(`${sourceHead}:${CITATION_WELD_PATH}`)} ${gapTag(final.gaps[0].id)}

## 3 — EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME

The accepted raw tape contains 21 v6 pass-1 action markers. Each marker is reproduced; the price change is evidenced, while the claimed causal consultation is GAP. ${receiptTag(`${RAW_COMMIT}:${RAW_PATH}`)}

| # | Hours | Leg | Action | Change | Reason status | Receipt / gap |
|---:|---:|---|---|---:|---|---|
${actionRows}

## 4 — WHAT HAPPENED

Nothing reached the rests. LAJ's lawful floor was 51¢, 4¢ above 47; SVA's lawful floor was 41¢, 5¢ above 36. The pair target 83¢ therefore did not complete and neither leg filled. ${receiptTag(`${floorLaj.receipt}; ${floorSva.receipt}; ${findings["F-VS-052"].id}`)}

The first reflex SVA credit at 41¢ did not enter pass-1's half-pair state: the next recorded stage still said \`credited_count=0\`. A fill→sibling→fingerprint→neighborhood→LAJ causal cascade is therefore not proved in the as-occurred pass. ${receiptTag(`${tape.rows.find((row) => row.kind === "fill" && row.leg === "SVA").receipt}; ${stages.find((stage) => stage.epoch > 1784020209.484).receipt}`)} ${gapTag("GAP-LAJSVA-FILL-HANDOFF", "CROSS_PASS_FILL_CREDIT_NOT_PRESENT")}

## 5 — MY GRADE OF MY OWN TRADE, GOOD/BAD/MIXED, WITH REASONING

Decision grade: **BAD**. My two rests missed the lawful floors by 4¢ and 5¢, and the diet I used was contaminated by in-play lows: 12 of the 14 named DANPRA/LAJSVA neighbors had \`low_frac ≥ 0.94\`. ${receiptTag(findings["F-VS-050"].id)}

Outcome grade: **BAD**. No side filled and no pair completed. That outcome is graded separately from the decision-time diagnosis above. ${receiptTag(findings["F-VS-052"].id)}

## 6 — WHAT I'D FLAG FOR THE LIBRARY

Bell-bound every historical span before serving a low. For the LAJSVA neighbors, the accepted measurement raises served lows by 3–19¢ in eleven named legs, directly attacking the diet that pulled 47/36 too deep. ${receiptTag(findings["F-VS-050"].id)}

Preserve range-path grain honestly: roughly 100 polling ticks per leg are not raw order-book depth. The matched-neighbor raw-depth comparison remains a resource gap. ${receiptTag(`${sourceHead}:${EXPLAINED_PATH}#L396`)} ${gapTag("GAP-NG-LAJSVA", "NO_RAW_TAPE_ORDER_BOOK_DEPTH_AT_MATCHED_NEIGHBOR_STAGE")}

Make first-credit handoff receipt-bearing. F-VS-053 requires pair coherence, but this as-occurred pass preserved no receipt showing the reflex fill entering the pattern engine. ${receiptTag(findings["F-VS-053"].id)} ${gapTag("GAP-LAJSVA-FILL-HANDOFF", "CROSS_PASS_FILL_CREDIT_NOT_PRESENT")}
`;
}

const BASE_CSS = `
:root{color-scheme:light dark;--bg:light-dark(#f6f3ed,#111418);--surface:light-dark(#fffdf8,#181d23);--text:light-dark(#17202a,#ecf1f6);--muted:light-dark(#63707c,#9aa7b5);--grid:light-dark(#d8d4ca,#303842);--bid:light-dark(#086f57,#61d0ad);--ask:light-dark(#9a3e31,#ff8e7d);--trade:light-dark(#245ca6,#73a7ff);--hit:light-dark(#7a3e00,#f4a259);--lift:light-dark(#145b75,#62c2e8);--reflex:light-dark(#7149a8,#c49aff);--v6:light-dark(#006a78,#50d5e3);--good:light-dark(#176b3a,#68d391);--bad:light-dark(#a02d2d,#ff7b7b);--warn:light-dark(#8a5a00,#ffc857);--gap:light-dark(#a02d2d,#ff7b7b);--focus:light-dark(#315a91,#8bb7ff)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}main{max-width:1680px;margin:0 auto;padding:24px}p,li,code{overflow-wrap:anywhere}h1,h2,h3{font-family:ui-sans-serif,system-ui,sans-serif;font-weight:650;letter-spacing:-.02em}h1{font-size:28px;margin:0 0 6px}h2{font-size:19px;margin:28px 0 10px}h3{font-size:15px;margin:18px 0 8px}.sub{color:var(--muted);margin-bottom:16px}.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0}.chip,button{border:1px solid var(--grid);background:var(--surface);color:var(--text);padding:6px 9px;border-radius:5px;font:inherit}.chip{display:inline-flex;gap:6px}button{cursor:pointer}button:hover,button:focus{border-color:var(--focus)}.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);margin:8px 0 14px}.sw{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:5px}.panel{background:var(--surface);border:1px solid var(--grid);padding:14px;margin:12px 0}.chart{width:100%;height:auto;display:block}.axis{fill:var(--muted);font-size:11px}.grid{stroke:var(--grid);stroke-width:1}.frame{fill:none;stroke:var(--grid)}.bid{fill:none;stroke:var(--bid);stroke-width:1.5}.ask{fill:none;stroke:var(--ask);stroke-width:1.5}.pair{fill:none;stroke:var(--trade);stroke-width:1.5}.target{fill:none;stroke:var(--v6);stroke-width:2}.coherence{fill:none;stroke:var(--reflex);stroke-width:1.5}.band{fill:color-mix(in srgb,var(--trade) 18%,transparent);stroke:none}.gapband{fill:url(#hatch)}.note{fill:var(--text);font-size:11px}.receipt{color:var(--muted);overflow-wrap:anywhere}.gap{color:var(--gap);font-weight:650}.ok{color:var(--good)}.bad{color:var(--bad)}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;vertical-align:top;padding:6px 7px;border-bottom:1px solid var(--grid)}th{color:var(--muted);font-weight:650;position:sticky;top:0;background:var(--surface)}.tablewrap{overflow:auto;max-height:620px}.detailgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}.nodeflow{display:grid;grid-template-columns:repeat(5,minmax(130px,1fr));gap:10px;align-items:stretch}.node{border-top:3px solid var(--grid);padding:9px;background:color-mix(in srgb,var(--surface) 90%,var(--grid))}.node.break{border-color:var(--gap)}.node.pass{border-color:var(--good)}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:color-mix(in srgb,var(--surface) 85%,var(--grid));padding:10px;border:1px solid var(--grid)}a{color:var(--focus)}details{margin:8px 0}summary{cursor:pointer}.counts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:14px}.count{border-top:2px solid var(--grid);padding-top:7px}.count b{display:block;font-size:18px}@media(max-width:800px){main{padding:12px}.detailgrid{grid-template-columns:1fr}.nodeflow{grid-template-columns:1fr}.panel{padding:8px}}
`;

function htmlShell(title, body, script = "") {
  return `<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${h(title)}</title><style>${BASE_CSS}</style></head><body><main>${body}</main>${script ? `<script>${script}</script>` : ""}</body></html>`;
}

function panelAHtml(data) {
  const notableRows = data.notable.map((row) => `<tr><td>${h(row.label)}</td><td>${fmt((row.epoch - DISCOVERY) / 3600, 6)}h</td><td>${row.price}¢</td><td>${h(row.flow)}</td><td><code>${h(row.trade_id)}</code></td><td class="receipt">${h(row.receipt)}</td></tr>`).join("");
  const countCards = [
    ["raw rows", data.counts.total], ["book steps", data.counts.book], ["true prints", data.counts.trade],
    ["HIT / LIFT", `${data.counts.hit} / ${data.counts.lift}`], ["reflex actions", data.counts.reflex],
    ["v6 actions", data.counts.v6], ["fills / floors", `${data.counts.fill} / ${data.counts.floor}`],
    ["boundary markers", data.counts.boundaries],
  ].map(([label, value]) => `<div class="count"><b>${h(value)}</b>${h(label)}</div>`).join("");
  const body = `
<h1>Panel A — LAJSVA pair render</h1><div class="sub">CASE STUDY v1 · AS-OCCURRED · one discovery clock · T-minus secondary · source-bound at ${h(RAW_COMMIT)}</div>
<div class="bar"><button data-focus="full">Full span</button><button data-focus="formation">Formation</button><button data-focus="sva">SVA floor + kiss</button><button data-focus="lajfill">LAJ fill</button><button data-focus="lajfloor">LAJ floor</button><button data-focus="bell">Bell</button><span id="window-label" class="chip"></span></div>
<div class="legend"><span><i class="sw" style="background:var(--bid)"></i>best bid</span><span><i class="sw" style="background:var(--ask)"></i>best ask</span><span>▼ HIT bid</span><span>▲ LIFT ask</span><span style="color:var(--reflex)">◆ reflex</span><span style="color:var(--v6)">■ v6 pass-1</span><span style="color:var(--good)">◎ credited fill</span><span class="gap">//// recorder-resolution gap</span></div>
<section class="panel"><h2>LAJ — best book, every print, both action systems</h2><svg id="price-LAJ" class="chart" viewBox="0 0 1500 310" role="img" aria-label="LAJ best bid ask, all prints, reflex and v6 actions"></svg></section>
<section class="panel"><h2>SVA — best book, every print, both action systems</h2><svg id="price-SVA" class="chart" viewBox="0 0 1500 310" role="img" aria-label="SVA best bid ask, all prints, reflex and v6 actions"></svg></section>
<section class="panel"><h2>Pair standing — bid sum against the 92¢ lawful ceiling</h2><svg id="pair-sum" class="chart" viewBox="0 0 1500 190" role="img" aria-label="Pair best bid sum with 92 cent lawful ceiling"></svg><p class="receipt">The 92¢ line is the standing-rest sum of separate lawful minima 51/41, not a simultaneous displayed pair. Receipt: ${h(data.receipts.fvs052)}</p></section>
<section class="panel"><h2>LAJ PICTURE strip — as occurred</h2><svg id="picture-LAJ" class="chart" viewBox="0 0 1500 230" role="img" aria-label="LAJ polarity, neighborhood score band, derivation and pair coherence"></svg></section>
<section class="panel"><h2>SVA PICTURE strip — as occurred</h2><svg id="picture-SVA" class="chart" viewBox="0 0 1500 230" role="img" aria-label="SVA polarity, neighborhood score band, derivation and pair coherence"></svg></section>
<section class="panel"><h2>Notable prints — trade IDs and receipts</h2><div class="tablewrap"><table><thead><tr><th>Print</th><th>Hours</th><th>Price</th><th>Flow</th><th>trade_id</th><th>Tape receipt</th></tr></thead><tbody>${notableRows}</tbody></table></div></section>
<section class="panel"><h2>ARSMAR counts block</h2><div class="counts">${countCards}</div><p class="receipt">Partition check: 1,250 book + 543 prints + 54 reflex + 21 v6 + 2 fills + 2 floors + discovery + two formation ends + bell = 1,876 rows. The reconciliation JSON's summary fields <code>rows=1862</code> and <code>v6_actions=7</code> conflict with the accepted tape's own exact row partition and are retained in CASE_STUDY_RECEIPT.json. Receipt: ${h(data.receipts.raw_recon)}</p><p class="gap">Recorder gaps: no outage ledger is present. Only the proved 1-second timestamp-resolution gap around the SVA kiss is shaded; the drawn band has a minimum visible width but the receipt interval is exactly [1784020209,1784020210). Receipt: ${h(data.receipts.fvs054)}</p></section>`;
  const script = `
const D=${dataForScript(data)};
const NS="http://www.w3.org/2000/svg";let domain=[D.discovery,D.bell];
const focus={full:[D.discovery,D.bell],formation:[D.discovery,D.formation+900],sva:[1784020000,1784020500],lajfill:[1784052400,1784053300],lajfloor:[1784059500,1784060800],bell:[1784077600,D.bell]};
function x(t){return 82+(t-domain[0])/(domain[1]-domain[0])*1388}function y(v,top,bottom,min=0,max=100){return bottom-(v-min)/(max-min)*(bottom-top)}
function esc(s){return String(s==null?"":s).replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function defs(){return '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="var(--gap)" stroke-width="2"/></pattern></defs>'}
function stepPath(rows,key,top,bottom,min=0,max=100){let d="",last=null;for(const r of rows){if(r.epoch<domain[0]||r.epoch>domain[1]||r[key]==null)continue;const xx=x(r.epoch),yy=y(r[key],top,bottom,min,max);if(last)d+=" H"+xx.toFixed(2)+" V"+yy.toFixed(2);else d+="M"+xx.toFixed(2)+" "+yy.toFixed(2);last=[xx,yy]}return d}
function linePath(rows,key,top,bottom,min=0,max=100){return rows.filter(r=>r.epoch>=domain[0]&&r.epoch<=domain[1]&&r[key]!=null).map((r,i)=>(i?"L":"M")+x(r.epoch).toFixed(2)+" "+y(r[key],top,bottom,min,max).toFixed(2)).join(" ")}
function axes(top,bottom,min=0,max=100){let s='<rect class="frame" x="82" y="'+top+'" width="1388" height="'+(bottom-top)+'"/>';for(let v=min;v<=max;v+=(max-min)/4){const yy=y(v,top,bottom,min,max);s+='<line class="grid" x1="82" x2="1470" y1="'+yy+'" y2="'+yy+'"/><text class="axis" x="74" y="'+(yy+4)+'" text-anchor="end">'+Math.round(v)+'¢</text>'}for(let i=0;i<=6;i++){const t=domain[0]+(domain[1]-domain[0])*i/6,xx=x(t),hr=(t-D.discovery)/3600,tm=(D.bell-t)/3600;s+='<line class="grid" x1="'+xx+'" x2="'+xx+'" y1="'+top+'" y2="'+bottom+'"/><text class="axis" x="'+xx+'" y="'+(bottom+17)+'" text-anchor="middle">H+'+hr.toFixed(2)+'</text><text class="axis" x="'+xx+'" y="'+(bottom+31)+'" text-anchor="middle">T−'+tm.toFixed(2)+'h</text>'}return s}
function gapBand(top,bottom){const exact=x(1784020210)-x(1784020209),w=Math.max(4,exact),xx=x(1784020209)-w/2;return '<rect class="gapband" x="'+xx+'" y="'+top+'" width="'+w+'" height="'+(bottom-top)+'"><title>Recorder resolution gap [1784020209,1784020210) · '+esc(D.receipts.fvs054)+'</title></rect>'}
function symbol(row,top,bottom){const xx=x(row.epoch),yy=y(row.price,top,bottom),title=esc(row.flow+' '+row.leg+' '+row.price+'¢ x'+row.quantity+' trade_id='+row.trade_id+' · '+row.flow_basis+' · '+row.receipt);if(row.flow==="HIT")return '<path d="M'+(xx-3)+' '+(yy-4)+'L'+(xx+3)+' '+(yy-4)+'L'+xx+' '+(yy+4)+'Z" fill="var(--hit)"><title>'+title+'</title></path>';return '<path d="M'+(xx-3)+' '+(yy+4)+'L'+(xx+3)+' '+(yy+4)+'L'+xx+' '+(yy-4)+'Z" fill="var(--lift)"><title>'+title+'</title></path>'}
function actionMark(row,top,bottom){const xx=x(row.epoch),yy=y(row.price,top,bottom),c=row.kind==="reflex"?"var(--reflex)":"var(--v6)",title=esc(row.kind.toUpperCase()+' '+row.action+'@'+row.price+' · '+row.receipt);return row.kind==="reflex"?'<path d="M'+xx+' '+(yy-5)+'l5 5-5 5-5-5Z" fill="'+c+'"><title>'+title+'</title></path>':'<rect x="'+(xx-4)+'" y="'+(yy-4)+'" width="8" height="8" fill="'+c+'"><title>'+title+'</title></rect>'}
function fillMark(row,top,bottom){const xx=x(row.epoch),yy=y(row.price,top,bottom);return '<circle cx="'+xx+'" cy="'+yy+'" r="8" fill="none" stroke="var(--good)" stroke-width="3"><title>CREDITED FILL '+row.leg+' '+row.price+'¢ · '+esc(row.receipt)+'</title></circle>'}
function boundaryMarks(leg,top,bottom){let s='';for(const row of D.rows.filter(r=>(r.kind==='discovery'||r.kind==='bell'||(r.kind==='formation'&&r.leg===leg))&&r.epoch>=domain[0]&&r.epoch<=domain[1])){const xx=x(row.epoch),label=row.kind==='formation'?'FORMATION END':row.kind.toUpperCase();s+='<line x1="'+xx+'" x2="'+xx+'" y1="'+top+'" y2="'+bottom+'" stroke="var(--muted)" stroke-dasharray="2 3"><title>'+label+' · '+esc(row.receipt)+'</title></line>'}return s}
function renderPrice(leg){const svg=document.getElementById('price-'+leg),rows=D.rows.filter(r=>r.leg===leg),books=rows.filter(r=>r.kind==='book'),trades=rows.filter(r=>r.kind==='trade'&&r.epoch>=domain[0]&&r.epoch<=domain[1]),actions=rows.filter(r=>(r.kind==='reflex'||r.kind==='v6')&&r.epoch>=domain[0]&&r.epoch<=domain[1]),fills=rows.filter(r=>r.kind==='fill'&&r.epoch>=domain[0]&&r.epoch<=domain[1]),notes=D.notable.filter(n=>n.leg===leg&&n.epoch>=domain[0]&&n.epoch<=domain[1]);let s=defs()+axes(20,260)+gapBand(20,260)+boundaryMarks(leg,20,260);s+='<path class="bid" d="'+stepPath(books,'bid',20,260)+'"/><path class="ask" d="'+stepPath(books,'ask',20,260)+'"/>';s+=trades.map(r=>symbol(r,20,260)).join('')+actions.map(r=>actionMark(r,20,260)).join('')+fills.map(r=>fillMark(r,20,260)).join('');for(const [ni,n] of notes.entries()){const xx=x(n.epoch),labelY=34+ni*15;s+='<line x1="'+xx+'" x2="'+xx+'" y1="20" y2="260" stroke="var(--warn)" stroke-dasharray="3 3"><title>'+esc(n.receipt)+'</title></line><text class="note" x="'+Math.min(1250,Math.max(88,xx+6))+'" y="'+labelY+'">'+esc(n.label)+' · '+esc(n.trade_id.slice(0,8))+'…</text>'}svg.innerHTML=s}
function renderPair(){const svg=document.getElementById('pair-sum');let s=defs()+axes(20,135,70,115)+gapBand(20,135);s+='<line x1="82" x2="1470" y1="'+y(92,20,135,70,115)+'" y2="'+y(92,20,135,70,115)+'" stroke="var(--warn)" stroke-dasharray="6 4"/><text class="note" x="86" y="'+(y(92,20,135,70,115)-6)+'">92¢ lawful standing-rest ceiling</text><path class="pair" d="'+stepPath(D.pairSum,'sum',20,135,70,115)+'"/>';svg.innerHTML=s}
function renderPicture(leg){const svg=document.getElementById('picture-'+leg),st=D.stages.filter(r=>r.epoch>=domain[0]&&r.epoch<=domain[1]);let s=defs();s+='<rect x="82" y="18" width="1388" height="30" fill="color-mix(in srgb,var(--muted) 20%,transparent)"/><text class="note" x="88" y="38">POLARITY: V54_UNDECIDED (reflex reason; no belief)</text>';s+='<text class="axis" x="74" y="82" text-anchor="end">score</text><rect class="frame" x="82" y="58" width="1388" height="55"/>';if(st.length){const upper=st.map(r=>({epoch:r.epoch,v:r.neighborhood_max})),lower=[...st].reverse().map(r=>({epoch:r.epoch,v:r.neighborhood_min}));const p=upper.concat(lower).map((r,i)=>(i?'L':'M')+x(r.epoch).toFixed(2)+' '+y(r.v,58,113,0,1).toFixed(2)).join(' ')+'Z';s+='<path class="band" d="'+p+'"/><path class="pair" d="'+linePath(st.map(r=>({epoch:r.epoch,v:(r.neighborhood_min+r.neighborhood_max)/2})),'v',58,113,0,1)+'"/>'}s+='<text class="axis" x="74" y="152" text-anchor="end">target</text><rect class="frame" x="82" y="123" width="1388" height="55"/><path class="target" d="'+linePath(st.map(r=>({epoch:r.epoch,v:r.actions[leg].target})),'v',123,178,0,100)+'"/>';s+='<text class="axis" x="74" y="208" text-anchor="end">cohere</text><path class="coherence" d="'+linePath(st.map(r=>({epoch:r.epoch,v:r.reads.sibling_state.inverse_coherence})),'v',187,220,0,1)+'"/>';for(const r of st){const xx=x(r.epoch),target=r.actions[leg].target;if(target!=null)s+='<circle cx="'+xx+'" cy="'+y(target,123,178)+'" r="3" fill="var(--v6)"><title>Stage '+r.stage+' '+leg+' '+r.actions[leg].action+'@'+target+' · '+esc(r.receipt)+' · RESOURCE-GAP '+esc(r.gaps[0].id)+'</title></circle>'}const last=st.at(-1);if(last&&last.actions[leg].target!=null)s+='<text class="note" x="'+Math.min(1400,x(last.epoch)+7)+'" y="'+(y(last.actions[leg].target,123,178)-6)+'">'+leg+' '+last.actions[leg].target+'¢</text>';svg.innerHTML=s}
function draw(){renderPrice('LAJ');renderPrice('SVA');renderPair();renderPicture('LAJ');renderPicture('SVA');document.getElementById('window-label').textContent='H+'+((domain[0]-D.discovery)/3600).toFixed(3)+' → H+'+((domain[1]-D.discovery)/3600).toFixed(3)+' · T−'+((D.bell-domain[1])/3600).toFixed(3)+'h'}
document.querySelectorAll('[data-focus]').forEach(b=>b.addEventListener('click',()=>{domain=focus[b.dataset.focus];draw()}));draw();
`;
  return htmlShell("LAJSVA Case Study v1 — Panel A Pair Render", body, script);
}

function panelBHtml(data) {
  const laneRows = [...READER_NAMES, "NEIGHBORHOOD_RETRIEVAL", "DERIVATION", "CONSERVATION_CHECK", "SENTENCE_EMITTER"];
  const body = `
<h1>Panel B — LAJSVA component engagement</h1><div class="sub">CASE STUDY v1 · AS-OCCURRED · 20 receipt-bearing stages · one clock · click a stage</div>
<div class="legend"><span class="ok">● captured reader value</span><span style="color:var(--trade)">◆ retrieval</span><span style="color:var(--v6)">■ derivation</span><span class="gap">G capture-time provenance gap</span></div>
<section class="panel"><svg id="lanes" class="chart" viewBox="0 0 1600 820" role="img" aria-label="Twenty time-aligned engagement stages across sixteen readers, retrieval, derivation, conservation and sentence emitter"></svg></section>
<section class="panel"><h2 id="detail-title">Stage detail</h2><div id="stage-detail" aria-live="polite"></div></section>
<section class="panel"><h2>SVA-fill cascade — worked as occurred</h2><div class="nodeflow"><div class="node pass"><b>1 · FILL</b><br>SVA 41¢ credit marker<br><span class="receipt">${h(data.cascade.fill_receipt)}</span></div><div class="node break"><b>2 · SIBLING READER</b><br>Next pass stage still <code>credited_count=0</code><br><span class="gap">GAP: cross-pass credit absent</span></div><div class="node break"><b>3 · FINGERPRINT</b><br>Fingerprint exists, but no fill-induced change is receipt-welded<br><span class="gap">GAP</span></div><div class="node break"><b>4 · NEIGHBORHOOD</b><br>Named neighbors returned, but causation from fill is not proved<br><span class="gap">GAP</span></div><div class="node break"><b>5 · LAJ RE-DERIVATION</b><br>${h(data.cascade.next_laj_action)} exists; it is not a proved fill cascade<br><span class="receipt">${h(data.cascade.next_stage_receipt)}</span></div></div><p class="receipt">F-VS-053 states the required pair-coherent behavior; it is not evidence that pass-1 performed the missing handoff. Required-law receipt: ${h(data.receipts.fvs053)}.</p></section>
<section class="panel"><h2>Visible resource gaps</h2><ul><li>20/20 emitted point claims carry <code>CAPTURE_TIME_POINT_PROVENANCE_ABSENT</code>; every retrieval column is ringed G. Receipt: ${h(data.receipts.citation_weld)}</li><li>Matched-neighbor grain is range-path polling (about 100 ticks/leg); raw order-book depth is GAP. Receipt: ${h(data.receipts.neighbor_grain)}</li><li>Per-stage conservation was enforced by build code but no capture-time per-stage conservation receipt survives; lane is stamped GAP, not silently painted PASS. Receipt: ${h(data.receipts.functionality)}</li><li>Recorder subsecond ordering at the SVA kiss is unresolved inside one second. Receipt: ${h(data.receipts.fvs054)}</li></ul></section>`;
  const script = `
const D=${dataForScript(data)},LANES=${JSON.stringify(laneRows)};const svg=document.getElementById('lanes'),W=1600,left=285,right=32,chartTop=62,rowH=34;const x=t=>left+(t-D.discovery)/(D.bell-D.discovery)*(W-left-right),y=i=>chartTop+i*rowH;
function esc(s){return String(s==null?"":s).replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function draw(){let s='<rect class="frame" x="'+left+'" y="'+(chartTop-18)+'" width="'+(W-left-right)+'" height="'+(LANES.length*rowH)+'"/>';for(let i=0;i<LANES.length;i++){const yy=y(i);s+='<line class="grid" x1="'+left+'" x2="'+(W-right)+'" y1="'+yy+'" y2="'+yy+'"/><text class="axis" x="'+(left-10)+'" y="'+(yy+4)+'" text-anchor="end">'+esc(LANES[i])+'</text>'}for(let k=0;k<=6;k++){const t=D.discovery+(D.bell-D.discovery)*k/6,xx=x(t);s+='<line class="grid" x1="'+xx+'" x2="'+xx+'" y1="'+(chartTop-18)+'" y2="'+(y(LANES.length-1)+18)+'"/><text class="axis" x="'+xx+'" y="34" text-anchor="middle">H+'+((t-D.discovery)/3600).toFixed(2)+'</text><text class="axis" x="'+xx+'" y="49" text-anchor="middle">T−'+((D.bell-t)/3600).toFixed(2)+'h</text>'}const seen={};for(const st of D.stages){const raw=x(st.epoch),key=st.epoch.toFixed(3),offset=(seen[key]||0)*4;seen[key]=(seen[key]||0)+1;const xx=raw+offset;s+='<line x1="'+xx+'" x2="'+xx+'" y1="'+y(0)+'" y2="'+y(LANES.length-1)+'" stroke="color-mix(in srgb,var(--trade) 28%,transparent)" stroke-width="1"><title>engagement edge '+esc(st.receipt)+'</title></line>';for(let i=0;i<16;i++)s+='<circle class="stage-hit" data-stage="'+st.stage+'" cx="'+xx+'" cy="'+y(i)+'" r="4" fill="var(--good)"><title>Stage '+st.stage+' '+esc(LANES[i])+' · '+esc(st.receipt)+'</title></circle>';s+='<path class="stage-hit" data-stage="'+st.stage+'" d="M'+xx+' '+(y(16)-6)+'l6 6-6 6-6-6Z" fill="var(--trade)"><title>'+esc(st.neighbors.map(n=>n.event_id+'@'+n.score.toFixed(6)).join(', '))+'</title></path><text class="gap stage-hit" data-stage="'+st.stage+'" x="'+(xx+7)+'" y="'+(y(16)+4)+'">G</text>';s+='<rect class="stage-hit" data-stage="'+st.stage+'" x="'+(xx-5)+'" y="'+(y(17)-5)+'" width="10" height="10" fill="var(--v6)"><title>LAJ '+esc(st.actions.LAJ.action)+'@'+esc(st.actions.LAJ.target)+'; SVA '+esc(st.actions.SVA.action)+'@'+esc(st.actions.SVA.target)+'</title></rect>';s+='<text class="gap stage-hit" data-stage="'+st.stage+'" x="'+(xx-4)+'" y="'+(y(18)+4)+'">G</text><path class="stage-hit" data-stage="'+st.stage+'" d="M'+xx+' '+(y(19)-6)+'l6 12h-12Z" fill="var(--warn)"/><text class="gap" x="'+(xx+7)+'" y="'+(y(19)+4)+'">G</text>'}svg.innerHTML=s;document.querySelectorAll('.stage-hit').forEach(el=>{el.style.cursor='pointer';el.addEventListener('click',()=>show(Number(el.dataset.stage)))})}
function show(n){const st=D.stages[n-1],fp=Object.entries(st.fingerprint).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td><code>'+esc(JSON.stringify(v))+'</code></td></tr>').join(''),ng=st.neighbors.map((r,i)=>'<tr><td>N'+(i+1)+'</td><td>'+esc(r.event_id)+'</td><td>'+r.score.toFixed(6)+'</td></tr>').join(''),reads=Object.entries(st.reads).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td><code>'+esc(JSON.stringify(v))+'</code></td></tr>').join('');document.getElementById('detail-title').textContent='Stage '+st.stage+' · H+'+st.hours.toFixed(6)+' · '+st.iso;document.getElementById('stage-detail').innerHTML='<div class="detailgrid"><div><h3>Query fingerprint</h3><table><tbody>'+fp+'</tbody></table><h3>Derivation</h3><p>LAJ '+esc(st.actions.LAJ.action)+' @ '+esc(st.actions.LAJ.target)+'¢ · ratio '+st.actions.LAJ.ratio.toFixed(12)+'</p><p>SVA '+esc(st.actions.SVA.action)+' @ '+esc(st.actions.SVA.target)+'¢ · ratio '+st.actions.SVA.ratio.toFixed(12)+'</p></div><div><h3>Named neighborhood · width '+st.neighborhood_width.toFixed(6)+'</h3><table><thead><tr><th>Grade</th><th>ID</th><th>Score</th></tr></thead><tbody>'+ng+'</tbody></table><p class="gap">RESOURCE-GAP '+esc(st.gaps[0].id)+' · '+esc(st.gaps[0].cause)+'</p><p class="receipt">'+esc(st.receipt)+'</p></div></div><details><summary>All sixteen computed readings</summary><div class="tablewrap"><table><tbody>'+reads+'</tbody></table></div></details>'}
draw();show(20);
`;
  return htmlShell("LAJSVA Case Study v1 — Panel B Engagement", body, script);
}

function panelCHtml(data) {
  const reflexRows = data.reflex_actions.map((row, i) => `<tr><td>${i + 1}</td><td>${fmt(row.delta / 3600, 6)}</td><td>${h(row.leg)}</td><td>${h(row.action)}@${row.price}¢</td><td>${h(row.reason)}</td><td class="receipt">${h(row.receipt)}</td></tr>`).join("");
  const v6Rows = data.v6_actions.map((row, i) => `<tr><td>${i + 1}</td><td>${fmt(row.delta / 3600, 6)}</td><td>${h(row.leg)}</td><td>${row.before ?? "NONE"}→${row.price}¢</td><td class="gap">GAP causal provenance</td><td class="receipt">${h(row.receipt)}</td></tr>`).join("");
  const body = `
<h1>Panel C — LAJSVA trade reports</h1><div class="sub">CASE STUDY v1 · AS-OCCURRED · six F-VS-055 sections · welded receipt status preserved</div>
<section class="panel"><h2>The reflex's report</h2><h3>1 · WHAT I BELIEVED AT OPEN</h3><p><b>No belief.</b> The machine wrote <code>V54_UNDECIDED_CHAMPION_BYTE_EQUAL</code>, a tracking state without a market story. <span class="receipt">${h(data.receipts.first_reflex)}</span></p><h3>2 · WHAT I DECIDED PER SIDE AND WHY (resources named)</h3><p>SVA tracked to 41¢; LAJ tracked to 53¢. The only evidenced resource class is the walk decision trace plus each cited dual-book row. <span class="receipt">${h(data.reflex_actions[0].receipt)} · ${h(data.reflex_actions.at(-1).receipt)}</span></p><h3>3 · EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME</h3><details><summary>54 reflex actions</summary><div class="tablewrap"><table><thead><tr><th>#</th><th>Hours</th><th>Leg</th><th>Action</th><th>Reason</th><th>Receipt</th></tr></thead><tbody>${reflexRows}</tbody></table></div></details><h3>4 · WHAT HAPPENED</h3><p>41 + 53 = 94¢, Δ6. The lawful standing-rest ceiling was 41 + 51 = 92¢, Δ8. The SVA kiss was only second-grain and had 16 ahead. <span class="receipt">${h(data.receipts.fvs052)} · ${h(data.receipts.fvs054)}</span></p><h3>5 · MY GRADE OF MY OWN TRADE, GOOD/BAD/MIXED, WITH REASONING</h3><p><b class="bad">Decision BAD</b> · <b class="ok">Outcome GOOD, separately</b>. No-belief tracking cannot borrow quality from a favorable result. <span class="receipt">${h(data.receipts.fvs055)} · ${h(data.receipts.fvs052)}</span></p><h3>6 · WHAT I'D FLAG FOR THE LIBRARY</h3><p>Fill-model optimism and the absent pair-belief handoff. <span class="receipt">${h(data.receipts.fvs054)} · ${h(data.receipts.fvs053)}</span> <a href="TRADE_REPORT_REFLEX.md">Open the complete receipt-welded report.</a></p></section>
<section class="panel"><h2>The pattern engine's report</h2><h3>1 · WHAT I BELIEVED AT OPEN</h3><p>I emitted graded named neighborhoods and a 20-stage narrowing picture; every consultation sentence carries a capture-time provenance GAP. <span class="receipt">${h(data.receipts.story)} · ${h(data.receipts.citation_weld)}</span></p><h3>2 · WHAT I DECIDED PER SIDE AND WHY (resources named)</h3><p>The final reported ratios were LAJ ${data.final.actions.LAJ.ratio.toFixed(12)} and SVA ${data.final.actions.SVA.ratio.toFixed(12)}, producing 47/36 after lineage blend and caps. <span class="receipt">${h(data.final.receipt)}</span> <span class="gap">GAP ${h(data.final.gaps[0].id)}</span></p><h3>3 · EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME</h3><details><summary>21 pass-1 action markers</summary><div class="tablewrap"><table><thead><tr><th>#</th><th>Hours</th><th>Leg</th><th>Change</th><th>Status</th><th>Receipt</th></tr></thead><tbody>${v6Rows}</tbody></table></div></details><h3>4 · WHAT HAPPENED</h3><p>LAJ stopped 4¢ above 47; SVA stopped 5¢ above 36. Neither filled. <span class="receipt">${h(data.receipts.fvs052)}</span></p><h3>5 · MY GRADE OF MY OWN TRADE, GOOD/BAD/MIXED, WITH REASONING</h3><p><b class="bad">Decision BAD · Outcome BAD</b>. The accepted contamination check found 12/14 named neighbors' lows in the last 6% of their unbounded spans. <span class="receipt">${h(data.receipts.fvs050)} · ${h(data.receipts.fvs052)}</span></p><h3>6 · WHAT I'D FLAG FOR THE LIBRARY</h3><p>Bell-bound the library and preserve raw-depth/resource gaps. <span class="receipt">${h(data.receipts.fvs050)} · ${h(data.receipts.neighbor_grain)}</span> <a href="TRADE_REPORT_PATTERN_ENGINE.md">Open the complete receipt-welded report.</a></p></section>
<section class="panel"><h2>Decision and outcome stay separate</h2><table><thead><tr><th>System</th><th>Decision grade</th><th>Outcome grade</th><th>Why / receipt</th></tr></thead><tbody><tr><td>Reflex</td><td class="bad">BAD</td><td class="ok">GOOD · Δ6</td><td>No belief; favorable completion · <span class="receipt">${h(data.receipts.fvs052)}</span></td></tr><tr><td>Pattern engine</td><td class="bad">BAD</td><td class="bad">BAD · no fills</td><td>Contaminated low diet drove 47/36 too deep · <span class="receipt">${h(data.receipts.fvs050)}</span></td></tr></tbody></table><p class="receipt">Law: ${h(data.receipts.fvs055)} · outcome: ${h(data.receipts.fvs052)} · contamination: ${h(data.receipts.fvs050)}</p></section>`;
  return htmlShell("LAJSVA Case Study v1 — Panel C Trade Reports", body);
}

function main() {
  const repo = path.resolve(process.argv[2] || process.cwd());
  const sourceHead = git(repo, ["rev-parse", "HEAD"], "utf8").trim();
  const out = path.join(repo, OUT_REL);
  const rawBuffer = gitShow(repo, RAW_COMMIT, RAW_PATH);
  const rawReconBuffer = gitShow(repo, RAW_COMMIT, RAW_RECON_PATH);
  const lawIndexBuffer = gitShow(repo, FABLE_COMMIT, LAW_INDEX_PATH);
  const findingsBuffer = gitShow(repo, FABLE_COMMIT, FINDINGS_PATH);
  const correctionsBuffer = gitShow(repo, FABLE_COMMIT, CORRECTIONS_PATH);
  const storyBuffer = currentBlob(repo, STORY_PATH);
  const storyReceiptBuffer = currentBlob(repo, STORY_RECEIPT_PATH);
  const functionalityBuffer = currentBlob(repo, FUNCTIONALITY_PATH);
  const explainedBuffer = currentBlob(repo, EXPLAINED_PATH);
  const explanationReceiptBuffer = currentBlob(repo, EXPLANATION_RECEIPT_PATH);
  const citationWeldBuffer = currentBlob(repo, CITATION_WELD_PATH);
  ensure(sha256(rawBuffer) === "802c590b8b748b9620d4e42362394e6a9976fc2f161275286bda192c18faa869", "LAJSVA_RAW_TAPE sha mismatch");
  ensure(sha256(rawReconBuffer) === "d9dfad4835abdbd5c06b3665e16fe02c1e4bfa82139c93d898ac83620273d413", "LAJSVA reconciliation sha mismatch");
  const tape = parseRawTape(rawBuffer);
  const story = parseStory(storyBuffer, sourceHead);
  const findings = findingsReceipts(findingsBuffer);
  const recon = JSON.parse(rawReconBuffer.toString("utf8"));
  ensure(sha256(lawIndexBuffer) === "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934", "LAW_INDEX sha mismatch");
  const corrections = correctionsBuffer.toString("utf8").trim().split(/\r?\n/).map((line) => JSON.parse(line));
  ensure(corrections.some((row) => row.correction_id === "W1TT-C-001") && corrections.some((row) => row.correction_id === "W1TT-C-002"), "bound corrections missing");
  ensure(corrections.every((row) => row.event_id !== EVENT_ID), "LAJSVA unexpectedly touched by W1TT correction");
  const notable = notablePrints(tape.rows);
  const firstAfterFill = story.stages.find((stage) => stage.epoch > 1784020209.484);
  ensure(firstAfterFill && firstAfterFill.reads.half_pair_state.credited_count === 0, "as-occurred fill handoff expectation changed");

  const pairSum = [];
  const pairState = { LAJ: null, SVA: null };
  for (const row of tape.rows.filter((candidate) => candidate.kind === "book")) {
    pairState[row.leg] = row.bid;
    if (Number.isFinite(pairState.LAJ) && Number.isFinite(pairState.SVA))
      pairSum.push({ epoch: row.epoch, sum: pairState.LAJ + pairState.SVA, receipt: row.receipt });
  }
  const compactRows = rawCompact(tape.rows);
  const stages = story.stages.map(compactStage);
  const receipts = {
    raw: `${RAW_COMMIT}:${RAW_PATH}@sha256:${sha256(rawBuffer)}`,
    raw_recon: `${RAW_COMMIT}:${RAW_RECON_PATH}@sha256:${sha256(rawReconBuffer)}`,
    story: `${sourceHead}:${STORY_PATH}@sha256:${sha256(storyBuffer)}`,
    functionality: `${sourceHead}:${FUNCTIONALITY_PATH}@sha256:${sha256(functionalityBuffer)}`,
    citation_weld: `${sourceHead}:${CITATION_WELD_PATH}@sha256:${sha256(citationWeldBuffer)}`,
    neighbor_grain: `${sourceHead}:${EXPLAINED_PATH}#L396`,
    fvs050: findings["F-VS-050"].id,
    fvs052: findings["F-VS-052"].id,
    fvs053: findings["F-VS-053"].id,
    fvs054: findings["F-VS-054"].id,
    fvs055: findings["F-VS-055"].id,
  };
  const panelAData = {
    event_id: EVENT_ID, discovery: DISCOVERY, formation: FORMATION_END, bell: TRUE_BELL,
    rows: compactRows, pairSum, stages, notable, receipts,
    counts: {
      total: tape.rows.length, ...tape.counts,
      boundaries: tape.counts.discovery + tape.counts.formation + tape.counts.bell,
    },
  };
  const panelBData = {
    event_id: EVENT_ID, discovery: DISCOVERY, bell: TRUE_BELL, stages, receipts,
    cascade: {
      fill_receipt: tape.rows.find((row) => row.kind === "fill" && row.leg === "SVA").receipt,
      next_stage_receipt: firstAfterFill.receipt,
      next_laj_action: `${firstAfterFill.actions.LAJ.action}@${firstAfterFill.actions.LAJ.target}¢`,
      gap_id: "GAP-LAJSVA-FILL-HANDOFF",
    },
  };
  const reflexActions = compactRows.filter((row) => row.kind === "reflex");
  const v6Actions = compactRows.filter((row) => row.kind === "v6");
  const panelCData = {
    reflex_actions: reflexActions, v6_actions: v6Actions, final: stages.at(-1), receipts: {
      ...receipts, first_reflex: reflexActions[0].receipt,
    },
  };

  const files = {
    panel_a: path.join(out, "PANEL_A_PAIR_RENDER.html"),
    panel_b: path.join(out, "PANEL_B_ENGAGEMENT.html"),
    panel_c: path.join(out, "PANEL_C_TRADE_REPORTS.html"),
    reflex_report: path.join(out, "TRADE_REPORT_REFLEX.md"),
    pattern_report: path.join(out, "TRADE_REPORT_PATTERN_ENGINE.md"),
    receipt: path.join(out, "CASE_STUDY_RECEIPT.json"),
    manifest: path.join(out, "ARTIFACT_HASH_MANIFEST.json"),
  };
  writeText(files.panel_a, panelAHtml(panelAData));
  writeText(files.panel_b, panelBHtml(panelBData));
  writeText(files.panel_c, panelCHtml(panelCData));
  writeText(files.reflex_report, buildReflexReport(tape, notable, findings, sourceHead));
  writeText(files.pattern_report, buildPatternReport(tape, story.stages, notable, findings, sourceHead));

  const firstOutputs = [files.panel_a, files.panel_b, files.panel_c, files.reflex_report, files.pattern_report].map((file) => fileReceipt(file, repo));
  const receipt = {
    label: "LAJSVA_CASE_STUDY_V1_AS_OCCURRED",
    event_id: EVENT_ID,
    generated_at_utc: new Date().toISOString(),
    source_head: sourceHead,
    scope: { render_report_lane_only: true, passes: 0, reruns: 0, full_804_run: false, sealed_read: false, live_mutation: false },
    license: {
      law_index_read_at: FABLE_COMMIT,
      law_index_sha256: "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934",
      requested_laws: ["L6", "L8", "L11", "L18", "L20", "L22"],
      index_gap: ["L20", "L22"],
    },
    input_bindings: [
      { id: "LAW_INDEX", commit: FABLE_COMMIT, path: LAW_INDEX_PATH, bytes: lawIndexBuffer.length, sha256: sha256(lawIndexBuffer) },
      { id: "LAJSVA_RAW_TAPE", commit: RAW_COMMIT, path: RAW_PATH, bytes: rawBuffer.length, sha256: sha256(rawBuffer) },
      { id: "LAJSVA_RAW_TAPE_RECONCILIATION", commit: RAW_COMMIT, path: RAW_RECON_PATH, bytes: rawReconBuffer.length, sha256: sha256(rawReconBuffer) },
      { id: "W1_GROUND_TRUTH_CORRECTIONS", commit: FABLE_COMMIT, path: CORRECTIONS_PATH, bytes: correctionsBuffer.length, sha256: sha256(correctionsBuffer) },
      { id: "FOUR_STORIES", commit: sourceHead, path: STORY_PATH, bytes: storyBuffer.length, sha256: sha256(storyBuffer) },
      { id: "FOUR_STORIES_RECEIPT", commit: sourceHead, path: STORY_RECEIPT_PATH, bytes: storyReceiptBuffer.length, sha256: sha256(storyReceiptBuffer) },
      { id: "FUNCTIONALITY_RECEIPT", commit: sourceHead, path: FUNCTIONALITY_PATH, bytes: functionalityBuffer.length, sha256: sha256(functionalityBuffer) },
      { id: "GAME_EXPLAINED_LAJSVA", commit: sourceHead, path: EXPLAINED_PATH, bytes: explainedBuffer.length, sha256: sha256(explainedBuffer) },
      { id: "EXPLANATION_RECEIPT", commit: sourceHead, path: EXPLANATION_RECEIPT_PATH, bytes: explanationReceiptBuffer.length, sha256: sha256(explanationReceiptBuffer) },
      { id: "CITATION_WELD_RECEIPT", commit: sourceHead, path: CITATION_WELD_PATH, bytes: citationWeldBuffer.length, sha256: sha256(citationWeldBuffer) },
    ],
    findings,
    corrections: { bound_ids: corrections.map((row) => row.correction_id), lajsva_rows: 0, disposition: "W1TT-C-001/002 BOUND; NEITHER TOUCHES LAJSVA" },
    clock: { discovery_epoch: DISCOVERY, formation_end_epoch: FORMATION_END, true_bell_epoch: TRUE_BELL, hours: (TRUE_BELL - DISCOVERY) / 3600 },
    arsmar_counts: {
      accepted_tape_rows: tape.rows.length,
      book_step_rows: tape.counts.book,
      true_print_rows: tape.counts.trade,
      print_flow_classification: { HIT: tape.counts.hit, LIFT: tape.counts.lift, unclassified: 0, method: "nearest contemporaneous BBO; equality at bid/ask controls" },
      reflex_actions: tape.counts.reflex,
      v6_pass1_action_markers: tape.counts.v6,
      fills: tape.counts.fill,
      floor_markers: tape.counts.floor,
      discovery_markers: tape.counts.discovery,
      formation_end_markers: tape.counts.formation,
      bell_markers: tape.counts.bell,
      partition_sum: Object.values({ book: tape.counts.book, trade: tape.counts.trade, reflex: tape.counts.reflex, v6: tape.counts.v6, fill: tape.counts.fill, floor: tape.counts.floor, discovery: tape.counts.discovery, formation: tape.counts.formation, bell: tape.counts.bell }).reduce((a, b) => a + b, 0),
      reconciliation_summary_conflict_preserved: { reconciliation_rows: recon.rows, reconciliation_v6_actions: recon.v6_actions, tape_rows: tape.rows.length, tape_v6_marker_rows: tape.counts.v6, disposition: "TAPE_PARTITION_CONTROLS_RENDER; CONFLICT_NOT_SILENTLY_REWRITTEN" },
    },
    panel_a: {
      both_legs: true, every_book_step: true, every_trade: true, every_trade_lift_hit_marked: true,
      reflex_actions: tape.counts.reflex, v6_actions: tape.counts.v6, fills: tape.counts.fill,
      floor_prints: notable.filter((row) => row.key.endsWith("FLOOR")), pair_ceiling_cents: 92,
      recorder_gap_render: { status: "RESOURCE_GAP_EXCEPT_PROVED_RESOLUTION_INTERVAL", exact_interval: [1784020209, 1784020210], receipt: receipts.fvs054 },
      picture: { polarity: "V54_UNDECIDED", neighborhood_band: "continuous min/max reported similarity score", derivation_levels: true, final_levels: { LAJ: 47, SVA: 36 }, pair_coherence: "sibling_state.inverse_coherence" },
    },
    panel_b: {
      stages: stages.length, reader_lanes: READER_NAMES, reader_engagement_marks: stages.length * READER_NAMES.length,
      retrieval_queries: stages.length, derivation_stages: stages.length, sentence_stages: stages.length,
      stage_point_provenance_gaps: stages.map((stage) => ({ stage: stage.stage, line: stage.line, ...stage.gaps[0] })),
      conservation: { rendered_lane: true, capture_time_per_stage_receipt: "RESOURCE_GAP", build_assert_source: `${sourceHead}:arb-executor/analysis/build_window1_v54_functionable_v6.js#L405` },
      sva_fill_cascade: {
        status: "BROKEN_AFTER_FILL_IN_AS_OCCURRED_RECEIPTS",
        fill_receipt: panelBData.cascade.fill_receipt,
        next_stage: { receipt: firstAfterFill.receipt, credited_count: firstAfterFill.reads.half_pair_state.credited_count, laj_action: panelBData.cascade.next_laj_action },
        gap_id: panelBData.cascade.gap_id,
        required_behavior_receipt: receipts.fvs053,
      },
    },
    panel_c: {
      reports: ["REFLEX", "PATTERN_ENGINE"], sections_per_report: 6,
      reflex_grade: { decision: "BAD", outcome: "GOOD_DELTA_6_SEPARATE" },
      pattern_grade: { decision: "BAD", outcome: "BAD_NO_FILLS" },
      contaminated_diet_receipt: receipts.fvs050,
    },
    regeneration_contract: {
      builder: "arb-executor/analysis/build_lajsva_case_study_v1.mjs",
      command: "node arb-executor/analysis/build_lajsva_case_study_v1.mjs",
      behavior: "deterministically regenerates the AS-OCCURRED package from committed inputs; after an accepted LAJSVA repair, run the same builder from the repair commit and file as the next case-study version so v1 remains the before spine",
    },
    outputs: firstOutputs,
  };
  writeJson(files.receipt, receipt);
  const manifestRows = [...firstOutputs, fileReceipt(files.receipt, repo)];
  writeJson(files.manifest, {
    label: "LAJSVA_CASE_STUDY_V1_ARTIFACT_HASH_MANIFEST",
    root: OUT_REL,
    file_count: manifestRows.length,
    all_under_50_mb: manifestRows.every((row) => row.bytes <= 50 * 1024 * 1024),
    files: manifestRows,
    note: "The manifest does not self-hash. No file is oversize; external custody is not required.",
  });
  const finalRows = [...manifestRows, fileReceipt(files.manifest, repo)];
  for (const row of finalRows) ensure(row.bytes <= 50 * 1024 * 1024, `oversize ${row.path}`);
  console.log(canonical({ output_root: OUT_REL, source_head: sourceHead, files: finalRows, counts: receipt.arsmar_counts, cascade: receipt.panel_b.sva_fill_cascade }));
}

main();
