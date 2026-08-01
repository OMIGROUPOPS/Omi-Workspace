#!/usr/bin/env node
"use strict";

// Cold two-game replay over the frozen quote-shape library. No scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { evaluateMicroPositionEvidence } = require("./window1_quote_shape_micro_position_v2.js");

const args = process.argv.slice(2), value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", args[0] && !args[0].startsWith("--") ? args[0] : "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const outDir = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731")));
const libraryPath = path.resolve(value("--library", path.join(outDir, "QUOTE_SHAPE_LIBRARY.json")));
const stableSamePriceConfirmation = args.includes("--stable-same-price-confirmation");
const receiptName = value("--receipt-name", "TWO_GAME_REPLAY.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const refsPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json");
const frozenFivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const DEFAULT_TARGETS = ["KXATPCHALLENGERMATCH-26JUL19NIKVRB", "KXATPCHALLENGERMATCH-26JUL19HURBIG"];
const TARGETS = new Set(value("--targets", DEFAULT_TARGETS.join(",")).split(",").filter(Boolean));
const PREFIX_KEYS = ["ask_net", "ask_dip", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth"];
const DWELL_SECONDS = 10, QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((v, i) => [headers[i], v])), ordinal: index + 2 })); }
function et(ts) { return new Date((ts - 4 * 3600) * 1000).toISOString().replace("T", " ").replace("Z", " ET"); }
function signed(value) { return Number.isInteger(value) ? `${value >= 0 ? "+" : ""}${value}` : "NULL"; }

function loadRows(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`), bytes = fs.readFileSync(file), rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < source.left || ts > source.right) continue; const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, receipt: `${path.basename(file)}#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((s, x) => s + x[1], 0), asks, carried_last: integer(raw.last_trade) });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal); const formedIndex = rows.findIndex((row) => row.spread === 1); const shapeRows = formedIndex >= 0 ? rows.slice(formedIndex) : [];
  return { rows: shapeRows, preformation_rows: formedIndex < 0 ? rows.length : formedIndex, source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}
function prefixRows(rows, left, right) {
  let state = null, firstAsk = null, firstBookTs = null, minAsk = null, spreadMin = null, spreadMax = null, lastAskChange = null, count = 0, changes = 0, askChangeAfterFirstTimestamp = false, spreadIntegral = 0, sizeIntegral = 0, depthIntegral = 0, observedDuration = 0;
  const output = [];
  function integrate(ts) { if (!state) return; const dt = Math.max(0, ts - state.integrated_to); spreadIntegral += state.spread * dt; sizeIntegral += Math.log1p(state.top_ask_size) * dt; depthIntegral += Math.log1p(state.top5_ask_depth) * dt; observedDuration += dt; state.integrated_to = ts; }
  for (const row of rows) {
    integrate(row.ts); if (!state) { firstAsk = row.ask; firstBookTs = row.ts; minAsk = row.ask; lastAskChange = row.ts; spreadMin = row.spread; spreadMax = row.spread; }
    else if (row.ask !== state.ask) { changes += 1; lastAskChange = row.ts; if (row.ts > firstBookTs) askChangeAfterFirstTimestamp = true; }
    minAsk = Math.min(minAsk, row.ask); spreadMin = Math.min(spreadMin, row.spread); spreadMax = Math.max(spreadMax, row.spread); count += 1; state = { ...row, integrated_to: row.ts };
    const elapsed = Math.max(1, row.ts - left), obs = Math.max(1, observedDuration), prefix = { ask_net: row.ask - firstAsk, ask_dip: minAsk - firstAsk, mean_spread: spreadIntegral / obs, spread_range: spreadMax - spreadMin, quote_rate: count * 3600 / elapsed, ask_change_rate: changes * 3600 / elapsed, ask_dwell_fraction: Math.max(0, row.ts - lastAskChange) / elapsed, mean_log_top_ask_size: sizeIntegral / obs, mean_log_top5_ask_depth: depthIntegral / obs };
    output.push({ ...row, prefix, ask_dwell_seconds: row.ts - lastAskChange, ask_change_after_first_timestamp: askChangeAfterFirstTimestamp, strictly_later_same_price_ask_receipt: row.ts > lastAskChange, raw_row_count: count, progress_bin: Math.max(0, Math.min(100, Math.floor((row.ts - left) / (right - left) * 100))) });
  }
  const collapsed = []; for (const row of output) { if (collapsed.length && collapsed[collapsed.length - 1].ts === row.ts) collapsed[collapsed.length - 1] = row; else collapsed.push(row); } return collapsed;
}
function compatibleShapes(group, row, previous) {
  if (row.raw_row_count < 2) return previous;
  const profiles = previous.map((shapeId) => {
    const shape = group.shapes.find((s) => s.shape_id === shapeId), support = shape.envelopes[row.progress_bin]?.empirical_support;
    return { shapeId, distances: support ? PREFIX_KEYS.map((key, d) => Math.abs((row.prefix[key] - support.means[d]) / support.sds[d])) : null };
  });
  // The tree is deliberately ordered. Ask-path position is the micro layer;
  // dwell/spread/cadence/visible size/depth can only resolve ties left by it.
  // Exact empirical minima are a fitted ordering, not a hand-set tolerance.
  const stagedMinimum = (candidates, indexes) => {
    const scored = candidates.map((candidate) => ({ ...candidate, score: candidate.distances ? indexes.reduce((sum, i) => sum + candidate.distances[i] ** 2, 0) : Infinity }));
    const minimum = Math.min(...scored.map((candidate) => candidate.score));
    return scored.filter((candidate) => candidate.score === minimum);
  };
  const micro = stagedMinimum(profiles, [0, 1]);
  return stagedMinimum(micro, [2, 3, 4, 5, 6, 7, 8]).map((x) => x.shapeId);
}
function shapeVerdict(group, shapeId, bin) { const shape = group.shapes.find((s) => s.shape_id === shapeId), delta = shape.medoid_future[bin]; return delta === null ? "UNKNOWN" : delta < 0 ? "LOWER" : "FLOOR"; }
function directionOf(shapeId) { if (shapeId.includes("_UP_")) return "UP"; if (shapeId.includes("_DOWN_")) return "DOWN"; if (shapeId.includes("_FLAT_")) return "FLAT"; return "UNKNOWN"; }
function inverseDirection(direction) { return direction === "UP" ? "DOWN" : direction === "DOWN" ? "UP" : direction; }
function directionObserved(leg, direction) { if (!leg.last || !leg.last.ask_change_after_first_timestamp) return false; const net = leg.last.prefix.ask_net; return direction === "UP" ? net > 0 : direction === "DOWN" ? net < 0 : direction === "FLAT" ? net === 0 : false; }
function capacityAtOrBelow(row, limit) { return row.asks.filter(([price]) => price <= limit).reduce((sum, x) => sum + x[1], 0); }
function downsample(rows, max = 1400) { if (rows.length <= max) return rows; const step = (rows.length - 1) / (max - 1), out = []; for (let i = 0; i < max; i += 1) out.push(rows[Math.round(i * step)]); return out; }

function replayGame(eventId, sources, library, refs) {
  const legs = sources.map((source) => { const loaded = loadRows(source); return { ...source, source_receipt: loaded.source, rows: prefixRows(loaded.rows, source.left, source.right), first_book_ts: loaded.rows[0].ts, first_book_receipt: loaded.rows[0].receipt, first_ask: loaded.rows[0].ask, first_bid: loaded.rows[0].bid, price_region: region(loaded.rows[0].bid), order: null, fill: null, last: null, survivor_shapes: null, decisions: [] }; });
  legs.sort((a, b) => a.leg.localeCompare(b.leg)); const high = [...legs].sort((a, b) => b.first_ask - a.first_ask || a.leg.localeCompare(b.leg))[0], low = legs.find((x) => x !== high), pairKey = `${high.category}|${high.price_region}|${low.price_region}`, tuplesObject = library.pair_shape_tuples[pairKey] || {}, allTuples = Object.keys(tuplesObject).map((key) => { const [highShape, lowShape] = key.split("|"); return { highShape, lowShape, n: tuplesObject[key] }; });
  for (const leg of legs) { const group = library.groups[`${leg.category}|${leg.price_region}`]; if (!group) throw new Error(`missing shape group ${leg.category}|${leg.price_region}`); leg.group = group; leg.survivor_shapes = group.shapes.map((s) => s.shape_id); leg.resolved_direction = null; leg.independent_direction = null; }
  let tuples = allTuples, indices = Object.fromEntries(legs.map((l) => [l.leg, 0])); const clock = [...new Set(legs.flatMap((l) => l.rows.map((r) => r.ts)))].sort((a, b) => a - b);
  for (const ts of clock) {
    const changedThisTick = {};
    for (const leg of legs) {
      let changed = false; while (indices[leg.leg] < leg.rows.length && leg.rows[indices[leg.leg]].ts <= ts) { leg.last = leg.rows[indices[leg.leg]++]; changed = true; }
      changedThisTick[leg.leg] = changed;
      // Do not let a low/sibling leg collapse before the other book exists.
      // The first resolved direction is then an exact inverse constraint on its sibling.
      if (changed && (leg === high || high.last)) {
        leg.survivor_shapes = compatibleShapes(leg.group, leg.last, leg.survivor_shapes);
        const ownDirections = [...new Set(leg.survivor_shapes.map(directionOf))]; if (!leg.independent_direction && ownDirections.length === 1 && ownDirections[0] !== "UNKNOWN") leg.independent_direction = ownDirections[0];
      }
      const directions = [...new Set(leg.survivor_shapes.map(directionOf))]; if (!leg.resolved_direction && directions.length === 1 && directions[0] !== "UNKNOWN") leg.resolved_direction = directions[0];
    }
    for (const sourceLeg of legs) {
      if (!sourceLeg.resolved_direction) continue; const sibling = legs.find((leg) => leg !== sourceLeg); if (sibling.resolved_direction) continue;
      const required = inverseDirection(sourceLeg.resolved_direction), constrained = sibling.survivor_shapes.filter((shapeId) => directionOf(shapeId) === required); if (constrained.length) sibling.survivor_shapes = constrained;
    }
    tuples = tuples.filter((t) => high.survivor_shapes.includes(t.highShape) && low.survivor_shapes.includes(t.lowShape));
    for (const leg of legs) {
      if (!leg.last || leg.fill) continue; const elapsedSinceOwnTick = ts - leg.last.ts, row = { ...leg.last, ts, ask_dwell_seconds: leg.last.ask_dwell_seconds + elapsedSinceOwnTick, progress_bin: Math.max(0, Math.min(100, Math.floor((ts - leg.left) / (leg.right - leg.left) * 100))) };
      const fillRow = stableSamePriceConfirmation ? leg.last : row;
      const distinctStrictlyLaterFillReceipt = stableSamePriceConfirmation ? fillRow.ts > leg.order?.action_ts && fillRow.receipt !== leg.order?.own_book_receipt_at_action : row.ts > leg.order?.action_ts;
      if (leg.order && distinctStrictlyLaterFillReceipt && fillRow.ask <= leg.order.price_cents && fillRow.ask_dwell_seconds >= DWELL_SECONDS && capacityAtOrBelow(fillRow, leg.order.price_cents) >= QUANTITY) { leg.fill = { price_cents: leg.order.price_cents, quantity: QUANTITY, evidence_ts: fillRow.ts, evidence_receipt: fillRow.receipt, evidence_type: "STRICTLY_LATER_ASK_DWELL_AND_DISPLAYED_CAPACITY", ask_cents: fillRow.ask, ask_dwell_seconds: fillRow.ask_dwell_seconds, capacity: capacityAtOrBelow(fillRow, leg.order.price_cents) }; leg.decisions.push({ ts: fillRow.ts, state: "FILLED", receipt: fillRow.receipt, order: leg.order, fill: leg.fill }); continue; }
      if (leg.order) continue;
      const role = leg === high ? "highShape" : "lowShape", shapes = [...new Set(tuples.map((t) => t[role]))], verdicts = shapes.map((id) => ({ shape_id: id, verdict: shapeVerdict(leg.group, id, row.progress_bin) })); let state = "INSUFFICIENT_EVIDENCE", reason = "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP";
      if (row.raw_row_count < 2) reason = "NO_PRIOR_IN_WINDOW_BOOK";
      else if (shapes.length && verdicts.every((x) => x.verdict === "LOWER")) { state = "HOLD"; reason = "ALL_SURVIVING_SHAPES_SAY_LOWER"; }
      else if (shapes.length && verdicts.every((x) => x.verdict === "FLOOR")) {
        const sibling = legs.find((candidate) => candidate !== leg);
        const microEvidence = stableSamePriceConfirmation ? evaluateMicroPositionEvidence({ leg, sibling, dwellSeconds: DWELL_SECONDS }) : { own_micro_position_observed: leg.last.ask_change_after_first_timestamp, evidence_type: leg.last.ask_change_after_first_timestamp ? "ASK_PRICE_TRANSITION" : null, stable_same_price_receipt: false, inverse_sibling_resolved: Boolean(leg.resolved_direction && sibling.independent_direction && inverseDirection(leg.resolved_direction) === sibling.independent_direction && directionObserved(sibling, sibling.independent_direction)) };
        const inverseSiblingResolved = microEvidence.inverse_sibling_resolved, stableSamePriceReceipt = microEvidence.stable_same_price_receipt, ownMicroPositionObserved = microEvidence.own_micro_position_observed, microPositionEvidenceType = microEvidence.evidence_type;
        if (!ownMicroPositionObserved) reason = "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED";
        else if (!inverseSiblingResolved) reason = "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED";
        else if (row.prefix.ask_net !== row.prefix.ask_dip) reason = "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW";
        else if (row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) { state = "PLACE"; reason = stableSamePriceReceipt && !leg.last.ask_change_after_first_timestamp ? "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_STABLE_SAME_PRICE_ASK_IS_EXECUTABLE" : "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_ASK_IS_EXECUTABLE"; }
        else reason = "FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY";
        row.micro_position_evidence_type = microPositionEvidenceType;
        row.stable_same_price_receipt = stableSamePriceReceipt;
        row.inverse_sibling_resolved = inverseSiblingResolved;
      }
      if (state === "PLACE") { const sibling = legs.find((candidate) => candidate !== leg), baseOrder = { price_cents: row.ask, quantity: QUANTITY, action_ts: ts, action_receipt: row.receipt, same_receipt_fill_forbidden: true, surviving_shapes: verdicts, pair_shape_tuples: tuples.map((t) => ({ ...t })) }; leg.order = stableSamePriceConfirmation ? { ...baseOrder, action_receipt: changedThisTick[leg.leg] ? leg.last.receipt : sibling.last?.receipt, own_book_receipt_at_action: leg.last.receipt, own_book_ts_at_action: leg.last.ts, sibling_book_receipt_at_action: sibling.last?.receipt ?? null, sibling_book_ts_at_action: sibling.last?.ts ?? null, micro_position_evidence_type: row.micro_position_evidence_type ?? "ASK_PRICE_TRANSITION" } : baseOrder; }
      const prior = leg.decisions[leg.decisions.length - 1]; if (!prior || prior.state !== state || state === "PLACE") leg.decisions.push({ ts, state, reason, book: { bid: row.bid, ask: row.ask, spread: row.spread, carried_last: row.carried_last, ask_dwell_seconds: row.ask_dwell_seconds, ask_net: row.prefix.ask_net, ask_dip: row.prefix.ask_dip, ask_change_after_first_timestamp: row.ask_change_after_first_timestamp, ...(stableSamePriceConfirmation ? { strictly_later_same_price_ask_receipt: leg.last.strictly_later_same_price_ask_receipt, stable_same_price_receipt: row.stable_same_price_receipt ?? false, micro_position_evidence_type: row.micro_position_evidence_type ?? null, inverse_sibling_resolved: row.inverse_sibling_resolved ?? false } : {}), top_ask_size: row.top_ask_size, top5_ask_depth: row.top5_ask_depth }, surviving_shapes: verdicts, surviving_pair_tuple_count: tuples.length, receipt: row.receipt, order: leg.order });
    }
  }
  const current = refs.current_branch.find((x) => x.event_id === eventId), corrected = refs.corrected_branch.find((x) => x.event_id === eventId);
  return { event_id: eventId, category: legs[0].category, pair_constraint: { identity: "two outcomes sum to 100", training_pair_key: pairKey, initial_pair_shape_tuples: allTuples.length, final_pair_shape_tuples: tuples.length }, legs: Object.fromEntries(legs.map((leg) => { const ref = corrected.legs[leg.leg], entry = leg.fill?.price_cents ?? null; return [leg.leg, { ticker: leg.ticker, price_region: leg.price_region, status: leg.fill ? "CREDITED" : "INSUFFICIENT_EVIDENCE", entry_cents: entry, baseline_entry_cents: current.legs[leg.leg].entry_cents, own_window1_close_cents: ref.own_window1_close_cents, delta_to_own_window1_close_cents: entry === null ? null : entry - ref.own_window1_close_cents, own_bell_price_cents: ref.own_bell_price_cents, delta_to_own_bell_price_cents: entry === null ? null : entry - ref.own_bell_price_cents, own_ask_reachable_low_cents: ref.own_ask_reachable_low_cents, delta_to_own_ask_reachable_low_cents: entry === null ? null : entry - ref.own_ask_reachable_low_cents, pair_reference_cents: "NOT_BOUND", delta_to_pair_reference_cents: "NOT_BOUND", placement: leg.order, fill: leg.fill, surviving_shapes_at_placement: leg.order?.surviving_shapes || [], surviving_shapes_at_terminal: leg.survivor_shapes.map((shape_id) => ({ shape_id, direction: directionOf(shape_id) })), terminal_reason: leg.fill ? "CREDITED_ON_STRICTLY_LATER_EXECUTABLE_ASK" : leg.decisions[leg.decisions.length - 1]?.reason || "NO_LAWFUL_DECISION", decision_changes: leg.decisions, chart_rows: downsample(leg.rows.map((r) => ({ ts: r.ts, bid: r.bid, ask: r.ask, last: r.carried_last }))), source: leg.source_receipt }]; })) };
}

function svgChart(event, sources) {
  const W = 1200, H = 720, left = 64, right = 25, top = 42, panelH = 270, gap = 75, plotW = W - left - right, colors = { bid: "#2563eb", ask: "#f59e0b", last: "#64748b", order: "#dc2626" };
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); let body = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial,sans-serif;fill:#111827}.axis{stroke:#9ca3af;stroke-width:1}.grid{stroke:#e5e7eb;stroke-width:1}.bid{stroke:${colors.bid}}.ask{stroke:${colors.ask}}.last{stroke:${colors.last}}.order{stroke:${colors.order};stroke-width:2}.line{fill:none;stroke-width:1.3}</style><text x="${left}" y="24" font-size="17" font-weight="bold">${esc(event.event_id)} -- quote-shape elimination replay</text>`;
  const legs = Object.entries(event.legs).sort();
  legs.forEach(([legId, leg], index) => { const y0 = top + index * (panelH + gap), rows = leg.chart_rows, source = sources.find((x) => x.leg === legId), minTs = source.left, maxTs = source.right, vals = rows.flatMap((r) => [r.bid, r.ask, r.last]).filter(Number.isFinite), minP = Math.max(0, Math.min(...vals) - 2), maxP = Math.min(100, Math.max(...vals) + 2), x = (ts) => left + (ts - minTs) / (maxTs - minTs) * plotW, y = (p) => y0 + panelH - (p - minP) / Math.max(1, maxP - minP) * panelH;
    for (let p = Math.ceil(minP / 10) * 10; p <= maxP; p += 10) { body += `<line class="grid" x1="${left}" y1="${y(p)}" x2="${W-right}" y2="${y(p)}"/><text x="${left-9}" y="${y(p)+4}" font-size="11" text-anchor="end">${p}</text>`; }
    body += `<line class="axis" x1="${left}" y1="${y0+panelH}" x2="${W-right}" y2="${y0+panelH}"/><text x="${left}" y="${y0-10}" font-size="15" font-weight="bold">${legId}: ${leg.status}; entry ${leg.entry_cents ?? "n/a"}; low ${leg.own_ask_reachable_low_cents}</text>`;
    for (const [key, cls] of [["bid","bid"],["ask","ask"],["last","last"]]) body += `<polyline class="line ${cls}" points="${rows.filter((r) => Number.isFinite(r[key])).map((r) => `${x(r.ts).toFixed(1)},${y(r[key]).toFixed(1)}`).join(" ")}"/>`;
    if (leg.placement) { const end = leg.fill?.evidence_ts || maxTs; body += `<line class="order" x1="${x(leg.placement.action_ts)}" y1="${y(leg.placement.price_cents)}" x2="${x(end)}" y2="${y(leg.placement.price_cents)}"/><circle cx="${x(leg.placement.action_ts)}" cy="${y(leg.placement.price_cents)}" r="4" fill="${colors.order}"/>`; }
    for (let m = 0; m <= 4; m += 1) { const ts = minTs + (maxTs-minTs)*m/4, sched = Math.round((source.scheduled-ts)/60), bell = Math.round((source.bell-ts)/60); body += `<text x="${x(ts)}" y="${y0+panelH+18}" font-size="10" text-anchor="middle">T-${sched}s / T-${bell}b</text>`; }
  });
  body += `<g transform="translate(${left},${H-28})"><line class="bid" x1="0" y1="0" x2="28" y2="0"/><text x="34" y="4" font-size="11">bid</text><line class="ask" x1="80" y1="0" x2="108" y2="0"/><text x="114" y="4" font-size="11">ask</text><line class="last" x1="160" y1="0" x2="188" y2="0"/><text x="194" y="4" font-size="11">carried last</text><line class="order" x1="285" y1="0" x2="313" y2="0"/><text x="319" y="4" font-size="11">our order</text></g></svg>`; return body;
}

function main() {
  const library = JSON.parse(fs.readFileSync(libraryPath)), refs = JSON.parse(fs.readFileSync(refsPath)), frozenFive = JSON.parse(fs.readFileSync(frozenFivePath)), windows = Object.fromEntries(frozenFive.events.map((e) => [e.event_id, e.window])), raw = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = raw.shift().split(","), quoteRows = raw.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))), sourcesByEvent = {};
  for (const q of quoteRows) if (TARGETS.has(q.event_id)) { if (!sourcesByEvent[q.event_id]) sourcesByEvent[q.event_id] = []; sourcesByEvent[q.event_id].push({ event_id: q.event_id, category: q.category, leg: q.leg, ticker: q.ticker, left: Number(q.left_ts), right: Number(q.right_ts), scheduled: Number(q.scheduled_start_ts), bell: Number(windows[q.event_id].actual_bell_ts) }); }
  const events = [...TARGETS].sort().map((id) => replayGame(id, sourcesByEvent[id], library, refs)), receipt = { schema_version: stableSamePriceConfirmation ? "WINDOW1_QUOTE_SHAPE_STABLE_SAME_PRICE_REPLAY_V2" : "WINDOW1_QUOTE_SHAPE_ELIMINATION_TWO_GAME_REPLAY_V1", cold: true, outcome_knowledge_consumed: false, score_free: true, library_sha256: sha256(fs.readFileSync(libraryPath)), decision_law: { macro: "category + first one-tick-spread lawful-book price band initializes every empirical quote topology", pair: "the first independently resolved ask-path direction removes non-inverse sibling directions; historically observed pair tuples remain the provenance set", micro: "at each own-book tick, exact fitted distance minima first retain the closest ask-net/dip shapes, then dwell/spread/cadence/displayed-size/top-five-depth resolves only the remaining tie; eliminated shapes never return", micro_micro: stableSamePriceConfirmation ? "the joint clock re-evaluates carried lawful BBO state on either leg's tick; own micro-position evidence is either an ask-price transition or a strictly later same-price own ask receipt carrying at least 10 seconds dwell and positive displayed size; PLACE also requires an independently observed inverse sibling direction, current ask equal to observed ask low, inherited 10-second dwell, and displayed ask quantity >=5" : "the joint clock re-evaluates carried lawful BBO state on either leg's tick; PLACE additionally requires an own ask transition after the first timestamp, an independently observed inverse sibling direction, current ask equal to observed ask low, inherited 10-second dwell, and displayed ask quantity >=5", states: ["PLACE", "HOLD", "INSUFFICIENT_EVIDENCE"], place: "all surviving pair-constrained shape medoids say FLOOR and micro-micro evidence is executable", hold: "all surviving shape medoids say LOWER", insufficient: "no prior in-window book, disagreement, no own micro position, unresolved sibling direction, missing library evidence, or execution evidence unavailable", fill: stableSamePriceConfirmation ? "a distinct own ask receipt with source timestamp strictly later than action; ask<=X; ask dwell>=10 seconds; displayed capacity>=5" : "strictly later ask receipt, ask<=X, ask dwell>=10 seconds, displayed capacity>=5" }, events };
  fs.mkdirSync(outDir, { recursive: true }); fs.writeFileSync(path.join(outDir, receiptName), canonical(receipt)); for (const event of events) { const shortName = stableSamePriceConfirmation ? event.event_id.replace(/^KX(?:ATP|WTA)(?:CHALLENGER)?MATCH-26JUL\d+/, "") : event.event_id.includes("NIKVRB") ? "NIKVRB" : "HURBIG"; fs.writeFileSync(path.join(outDir, `${shortName}_QUOTE_SHAPE_REPLAY.svg`), svgChart(event, sourcesByEvent[event.event_id])); }
  process.stdout.write(canonical({ status: "BUILT", events: events.map((e) => ({ event_id: e.event_id, legs: Object.fromEntries(Object.entries(e.legs).map(([k,v]) => [k,{ status:v.status, entry:v.entry_cents, low:v.own_ask_reachable_low_cents, shapes:v.surviving_shapes_at_placement.map((s)=>s.shape_id) }])) })) }));
}

main();
