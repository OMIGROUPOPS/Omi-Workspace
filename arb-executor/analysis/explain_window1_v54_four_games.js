"use strict";

// Receipt-only explainer. This file never imports or executes the OS, never
// retrieves a new neighborhood, and never reads the fixed-804 source set.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { execFileSync } = require("child_process");

const TARGETS = Object.freeze([
  "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
  "KXATPCHALLENGERMATCH-26JUL14URSPAL",
  "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
  "KXATPMATCH-26JUL18DANPRA",
]);
const SHORT = Object.freeze({
  KXATPCHALLENGERMATCH_26JUL12GIUBAR: "GIUBAR",
  KXATPCHALLENGERMATCH_26JUL14URSPAL: "URSPAL",
  KXATPCHALLENGERMATCH_26JUL14LAJSVA: "LAJSVA",
  KXATPMATCH_26JUL18DANPRA: "DANPRA",
});
const PICKS = Object.freeze({
  KXATPCHALLENGERMATCH_26JUL12GIUBAR: [1, 3, 6, 10, 11, 14, 19],
  KXATPCHALLENGERMATCH_26JUL14URSPAL: [1, 2, 6, 9, 10, 12, 23],
  KXATPCHALLENGERMATCH_26JUL14LAJSVA: [1, 3, 5, 9, 16, 18, 20],
  KXATPMATCH_26JUL18DANPRA: [1, 4, 6, 11, 12, 15, 18, 19],
});
const STORY_TEXT = Object.freeze({
  GIUBAR: [
    "Hour 0 opened as an unformed 31/67 anchor pair behind 5/95 and 4/95 books. The references briefly crossed toward 50/49 and then 44/76, but formation law correctly kept both sides silent. At 0.143889 hours both formations completed; the seven named comparisons had narrowed enough for 24 BAR / 65 GIU, with a 98-cent pair ceiling and neither post-only cap binding.",
    "For most of the next twelve hours the machine followed the market downward in small revisions rather than predicting the late finesse: BAR cycled 22–25 and GIU 61–65. At 12.192778 hours BAR's book broke to a 19 bid while the rest was 20. The true print at 19 credited BAR. The sibling arithmetic then moved GIU from 61 to 59 as BAR's 19-cent entry became the pair commitment.",
    "GIU credited at 59 at hour 12.479156, completing the pair at 78 and a 22-cent discount. That is a good capture, but not the ceiling. Before the provisional L11 bell, BAR later printed 16 and GIU 49; the tape's deepest lawful per-side pair was therefore 65, a 35-cent discount. We captured 19/59 and left 3 cents on BAR plus 10 on GIU.",
    "What the OS missed was the size and timing of the last-hour two-sided collapse. The neighborhood did eventually reorient, but only after BAR had already fallen and the pair commitment forced the sibling response. After both credits, the derivation layer also kept writing PLACE_REST sentences even though the executor's credited-position guard suppressed those actions. The receipts prove a strong result and a semantic humility defect at the same time.",
  ].join("\n\n"),
  URSPAL: [
    "Hour 0 began unformed at 38/62 anchors behind symmetric 4/95 books. Formation took 0.704444 hours. The first lawful posture was 20 PAL / 59 URS; as the books settled, the joint picture moved that pair through 28/49 and then 31/51. Nothing in those early points foresaw the full late inversion.",
    "At hour 12.024469 the pair stood 31 PAL / 49 URS. PAL printed 31 at 12.039239 and credited. With 31 committed, the sibling cap widened and URS was re-derived at 53, then 50. URS printed 46 at 12.669913 and completed the pair at 77, a 23-cent discount.",
    "The realized tape kept moving after capture: PAL reached 30, while URS reached 28 immediately before the L11 bell. The provisional ceiling was therefore 58, or a 42-cent discount. The capture gave up 1 cent on PAL and 18 on URS. The large URS gap is the clearest case here of a machine following a collapse rather than anticipating its finesse.",
    "The bell itself is not settled socially: the committed CC note says the recorded bell appears at least 48 minutes late relative to the external move. L11 still makes the truth-table epoch the only grading source, so this document does not move it; capture-versus-ceiling remains PROVISIONAL. As in GIUBAR, post-credit PLACE_REST sentences continued even though the credited guard prevented new rests.",
  ].join("\n\n"),
  LAJSVA: [
    "Hour 0 opened around 59/41 and formed quickly, at 0.077778 hours. The first lawful pair was 47 LAJ / 35 SVA. At 2.432880 hours the OS briefly came up to 52/33, then spent the rest of the game oscillating mostly between 47–49 on LAJ and 32–37 on SVA as the named neighborhood changed.",
    "The market was more stable than those eventual-low comparisons. LAJ's deepest lawful pre-bell print was 51 and SVA's was 41, so the tape did offer 92 in separate formation-lawful moments: an 8-cent provisional ceiling that would have preserved the +6 floor. The OS captured neither because its late rests were 47/36, nine cents deeper in total than the two realized lows.",
    "At the bell the final seven neighbors produced weighted low ratios 0.775197 and 0.861969. With anchors 59/41, those ratios, the 53/41 lineage, and the declared neighborhood mass rounded to 47/36; neither pair cap nor post-only cap caused the miss. The miss was therefore in the neighborhood's eventual-low expectation, not in a placement constant.",
    "No reweighting of those same seven neighbors can simultaneously lift the low-side ratio enough for 41 and the high-side ratio enough for 51; the convex receipt proof is below. A new same-stage survival corpus table might change that answer, but pass 1 contains no such table and this lane is forbidden to build or test one. The truthful answer is: the existing declared neighborhood cannot preserve +6, and a corpus adjustment is plausible but unproved.",
  ].join("\n\n"),
  DANPRA: [
    "Hour 0 looked like a noisy 58/41 anchor pair, but formation lasted 4.321944 hours. The pre-formation tape wandered through 52/34, 52/60, and 71/60; formation law correctly kept every target absent. At formation completion, the first rests were 49 DAN / 36 PRA.",
    "By hour 5.546949 the books had settled near 58/43 and the OS wanted 51/38. DAN then stayed near 59–62 while PRA stayed near 40–43. PRA's rest moved down to 31 and finally back to 33; DAN stayed 51. The displayed market thus held the operator's roughly 59/40 shape while the machine waited for the deeper dips its named May/June neighborhood had historically shown.",
    "Those dips never arrived. The deepest lawful prints were 59 DAN and 41 PRA, summing to par. The provisional ceiling was therefore zero discount. Neither 51 nor 33 could fill; their final shortfalls were 8 cents per side. Hindsight could have completed at 59/41, but that would have bought no pair discount, so completion alone would not have improved the economic story.",
    "The final arithmetic was coherent but overconfident about travel: 58×0.863019 blended with lineage 59 became 51; 41×0.788299 blended with lineage 40 became 33. The exact May/June terminal tape rows are below. What remains unexplained is why DANPRA survived without the neighborhood's typical dip; the receipts contain prices and books, not injury, scheduling, or participant-state causes.",
  ].join("\n\n"),
});
const UNEXPLAINED = Object.freeze({
  GIUBAR: [
    "No receipt names the exogenous cause of the late BAR/GIU collapse; the stores contain market data, not player-status news.",
    "The bell is TAPE_INFERENCE, not a CC-ratified official time, so the ceiling remains provisional.",
    "The derivation receipt does not explain why a credited leg still receives a PLACE_REST sentence while the executor silently suppresses it.",
  ],
  URSPAL: [
    "The cause of URS falling from the sixties to 28 is absent from every connected market store.",
    "CC identified a likely late bell but did not replace L11's truth-table epoch; the lawful analysis window remains disputed but unchanged.",
    "Post-credit action sentences describe rests that the credited guard does not execute.",
  ],
  LAJSVA: [
    "The receipts do not explain why both legs remained shallower than the neighborhood's weighted eventual lows.",
    "Pass 1 has no same-elapsed-stage survival table, so a corpus remedy cannot be claimed without a forbidden new analysis pass.",
    "The two per-side minima occurred at different times; the 92-cent ceiling is a standing-rest opportunity, not a simultaneous displayed pair.",
  ],
  DANPRA: [
    "No connected resource explains why the 59/40 shape survived while the named May/June games dipped.",
    "The neighborhood uses full historical path summaries; it has no participant-state or match-context causal variable.",
    "The bell is TAPE_INFERENCE and awaits CC ratification.",
  ],
});

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}
function required(name) {
  const value = arg(name);
  if (!value) throw new Error(`missing --${name}`);
  return path.resolve(value);
}
function key(eventId) { return eventId.replaceAll("-", "_"); }
function shaBytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function shaFile(file) { return shaBytes(fs.readFileSync(file)); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function writeText(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function writeJson(file, value) { writeText(file, canonical(value)); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function finite(value) { if (value === null || value === undefined || value === "") return null; const n = Number(value); return Number.isFinite(n) ? n : null; }
function cent(value) { const n = finite(value); return Number.isInteger(n) && n >= 1 && n <= 99 ? n : null; }
function mean(values) { const xs = values.filter(Number.isFinite); return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null; }
function wordCount(value) { return value.trim().split(/\s+/).filter(Boolean).length; }
function fmt(value, digits = 6) { return Number.isFinite(value) ? Number(value).toFixed(digits) : "UNKNOWN"; }
function iso(epoch) { return Number.isFinite(epoch) ? new Date(epoch * 1000).toISOString() : "UNKNOWN"; }
function parseValue(value) { if (value === "NONE" || value === "UNKNOWN") return null; return finite(value); }
function physicalReceipt(file) { const stat = fs.statSync(file); return { path: file, sha256: shaFile(file), bytes: stat.size }; }
function gitShow(repo, spec) { return execFileSync("git", ["show", spec], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }

function parseReaders(line) {
  const names = ["anchor_settle", "opening_split", "drift", "steps_stillness", "shape_survival", "ripeness", "lows_travel", "joint_state_spread_dwell", "divots", "depth_size", "volume", "sibling_state", "category", "time_in_window", "books", "half_pair_state"];
  const reads = {};
  names.forEach((name, index) => {
    const marker = `${name}=`;
    const start = line.indexOf(marker);
    ensure(start >= 0, `missing reader ${name}`);
    const valueStart = start + marker.length;
    const end = index + 1 < names.length
      ? line.indexOf(` · ${names[index + 1]}=`, valueStart)
      : line.indexOf(". The named neighborhood was", valueStart);
    ensure(end > valueStart, `reader boundary ${name}`);
    reads[name] = JSON.parse(line.slice(valueStart, end));
  });
  return reads;
}

function parseStory(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  const byEvent = new Map();
  let current = null;
  lines.forEach((line, lineIndex) => {
    const heading = line.match(/^## (KX[A-Z0-9-]+)$/);
    if (heading) { current = TARGETS.includes(heading[1]) ? heading[1] : null; return; }
    if (!current || !line.startsWith("At ")) return;
    const hoursMatch = line.match(/^At ([0-9.]+) hours from discovery/);
    if (!hoursMatch) return;
    const reads = parseReaders(line);
    const afterSummary = line.slice(line.indexOf(". ", line.indexOf("The derivation produced")) + 2);
    const sentencePattern = /At ([0-9.]+) hours from discovery, all sixteen readers fired for ([^.]+)\. The named neighborhood is (.*?)\. ([A-Z0-9]+) has anchor ([^,]+), neighborhood low ratio ([^,]+), lineage target ([^,]+), pair cap ([^,]+), and post-only cap ([^.]+)\. Resources consulted: (.*?)\. ACTION=([^;]+); TARGET_CENTS=([^;]+); ACTIVE_TARGET_BEFORE_CENTS=([^.]+)\./g;
    const matches = [...afterSummary.matchAll(sentencePattern)];
    ensure(matches.length === 2, `sentence count ${current} line ${lineIndex + 1}: ${matches.length}`);
    const neighborhood = matches[0][3].split(", ").map((entry) => {
      const match = entry.match(/^(.*)@([0-9.]+)$/);
      ensure(match, `bad neighbor ${entry}`);
      return { event_id: match[1], printed_score: Number(match[2]) };
    });
    const derivations = matches.map((match) => ({
      sentence: match[0],
      leg_id: match[4],
      anchor_cents: parseValue(match[5]),
      weighted_low_ratio: parseValue(match[6]),
      lineage_target_cents: parseValue(match[7]),
      pair_cap_cents: parseValue(match[8]),
      post_only_cap_cents: parseValue(match[9]),
      resources: match[10].split(", "),
      action: match[11],
      target_cents: parseValue(match[12]),
      active_before_cents: parseValue(match[13]),
    }));
    if (!byEvent.has(current)) byEvent.set(current, []);
    const values = byEvent.get(current);
    values.push({ event_id: current, stage: values.length + 1, line: lineIndex + 1, hours: Number(hoursMatch[1]), reads, neighborhood, derivations });
  });
  TARGETS.forEach((id) => ensure(byEvent.has(id), `story event missing ${id}`));
  return byEvent;
}

function vectorFromReads(stage) {
  const ids = Object.keys(stage.reads.anchor_settle.anchors_cents);
  const oriented = ids.map((id) => ({
    id,
    anchor: stage.reads.anchor_settle.anchors_cents[id],
    drift: stage.reads.drift[id].drift_cents,
    travel: stage.reads.lows_travel[id].travel_cents,
  })).sort((a, b) => (a.anchor ?? 50) - (b.anchor ?? 50) || a.id.localeCompare(b.id));
  const contracts = Object.values(stage.reads.volume).reduce((sum, row) => sum + (finite(row.contracts) ?? 0), 0);
  return {
    category: stage.reads.category.category,
    anchor_split_cents: stage.reads.opening_split.absolute_split_cents,
    leg0_anchor_cents: oriented[0].anchor,
    leg1_anchor_cents: oriented[1].anchor,
    leg0_drift_cents: oriented[0].drift,
    leg1_drift_cents: oriented[1].drift,
    leg0_travel_cents: oriented[0].travel,
    leg1_travel_cents: oriented[1].travel,
    joint_mid_sum_cents: stage.reads.joint_state_spread_dwell.mid_sum_cents,
    joint_spread_cents: stage.reads.joint_state_spread_dwell.spread_sum_cents,
    inverse_coherence: stage.reads.sibling_state.inverse_coherence,
    volume_log1p: Math.log1p(contracts),
    hours_from_discovery: stage.reads.time_in_window.hours_from_discovery,
    divot_depth_cents: mean(Object.values(stage.reads.divots).map((row) => finite(row.mean_depth_cents))),
    oriented_leg_ids: oriented.map((row) => row.id),
  };
}

function similarity(query, candidate, declaration) {
  let total = 0, covered = 0, distance = 0;
  for (const [field, weight] of Object.entries(declaration.weights)) {
    total += weight;
    if (field === "category") {
      if (query.category && candidate.category) { covered += weight; distance += weight * (query.category === candidate.category ? 0 : 1); }
      continue;
    }
    const q = finite(query[field]), c = finite(candidate[field]), scale = finite(declaration.scales[field]);
    if (q === null || c === null || scale === null || scale <= 0) continue;
    covered += weight;
    distance += weight * Math.abs(q - c) / scale;
  }
  const coverage = total ? covered / total : 0;
  const normalized = covered ? distance / covered : null;
  return { coverage, normalized_distance: normalized, score: normalized === null ? 0 : coverage * Math.exp(-normalized) };
}

function enrichStage(stage, corpus, declaration) {
  const vector = vectorFromReads(stage);
  const neighbors = stage.neighborhood.map((printed, index) => {
    const corpusRow = corpus.get(printed.event_id);
    ensure(corpusRow, `corpus row missing ${printed.event_id}`);
    const match = similarity(vector, corpusRow.vector, declaration);
    ensure(Math.abs(match.score - printed.printed_score) < 0.00001, `score re-derivation ${printed.event_id}: ${match.score} vs ${printed.printed_score}`);
    return { ...printed, ...match, grade: `N${index + 1}`, corpus: corpusRow };
  });
  const mass = mean(neighbors.map((row) => row.score * row.coverage));
  const derivations = stage.derivations.map((derivation) => {
    const orientedIndex = vector.oriented_leg_ids.indexOf(derivation.leg_id);
    const rows = neighbors.map((neighbor) => {
      const leg = neighbor.corpus.legs[orientedIndex];
      if (!leg || !finite(leg.anchor_cents) || !finite(leg.low_cents) || leg.anchor_cents <= 0) return null;
      return { event_id: neighbor.event_id, leg_id: leg.leg_id, score: neighbor.score, coverage: neighbor.coverage, weight: neighbor.score * neighbor.coverage, anchor: leg.anchor_cents, low: leg.low_cents, ratio: leg.low_cents / leg.anchor_cents };
    }).filter(Boolean);
    const denominator = rows.reduce((sum, row) => sum + row.weight, 0);
    const numerator = rows.reduce((sum, row) => sum + row.weight * row.ratio, 0);
    const ratio = denominator ? numerator / denominator : null;
    ensure(ratio === null || Math.abs(ratio - derivation.weighted_low_ratio) < 1e-10, `ratio re-derivation ${stage.event_id}|${stage.stage}|${derivation.leg_id}`);
    const raw = ratio === null ? null : Math.round(derivation.anchor_cents * ratio);
    const blended = raw !== null && derivation.lineage_target_cents !== null ? Math.round(mass * raw + (1 - mass) * derivation.lineage_target_cents) : (raw ?? derivation.lineage_target_cents);
    const capped = blended === null ? null : Math.max(1, Math.min(blended, derivation.pair_cap_cents, derivation.post_only_cap_cents));
    return { ...derivation, oriented_index: orientedIndex, neighbor_rows: rows, denominator, numerator, ratio, neighborhood_mass: mass, raw_target: raw, blended_target: blended, capped_target: capped };
  });
  return { ...stage, vector, neighbors, derivations };
}

function loadGzipJsonl(file) {
  const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8");
  return text.split(/\r?\n/).filter(Boolean).map((line, index) => ({ ...JSON.parse(line), _row: index + 1 }));
}
function loadJsonl(file) {
  return fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map((line, index) => ({ ...JSON.parse(line), _row: index + 1 }));
}
function parseCsvLine(line) {
  const out = []; let value = "", quote = false;
  for (let i = 0; i < line.length; i += 1) {
    const c = line[i];
    if (c === '"') { if (quote && line[i + 1] === '"') { value += '"'; i += 1; } else quote = !quote; }
    else if (c === "," && !quote) { out.push(value); value = ""; }
    else value += c;
  }
  out.push(value); return out;
}
function historicalRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean);
  const headers = parseCsvLine(lines[0]);
  const map = new Map();
  lines.slice(1).forEach((line, index) => {
    const values = parseCsvLine(line);
    const row = Object.fromEntries(headers.map((header, i) => [header, values[i] ?? ""]));
    row._line = index + 2;
    map.set(row.event_ticker, row);
  });
  return map;
}

function rangeEvidence(record, corpusRow) {
  if (!record) return "RESOURCE-GAP — RANGE ROW MISSING";
  const legs = corpusRow.legs.map((summary) => {
    const leg = record.legs?.[summary.leg_id];
    if (!leg || !Array.isArray(leg.ticks)) return `${summary.leg_id}: RESOURCE-GAP — no tick array`;
    const findTick = (value) => {
      const index = leg.ticks.findIndex((tick) => [tick[1], tick[2], tick[3]].some((cell) => finite(cell) === finite(value)));
      return index >= 0 ? `tick#${index + 1}[${leg.ticks[index].join(",")}]` : "aggregate-field-only";
    };
    const last = leg.ticks.at(-1);
    return `${summary.leg_id} anchor ${summary.anchor_cents} (${findTick(summary.anchor_cents)}), low ${summary.low_cents} (${findTick(summary.low_cents)}), close ${summary.close_cents ?? "?"} (terminal tick#${leg.ticks.length}[${last.join(",")}])`;
  });
  return `R-RANGE#row-${record._row}; ${legs.join("; ")}`;
}

function sourceEvidence(neighbor, rangeByEvent, historicalByEvent) {
  const row = neighbor.corpus;
  if (row.quality === "RANGE_SPECTRUM_PATH") return rangeEvidence(rangeByEvent.get(row.event_id), row);
  if (row.quality === "HISTORICAL_EVENT_AGGREGATE") {
    const historical = historicalByEvent.get(row.event_id);
    return historical ? `R-HIST#line-${historical._line}; RESOURCE-GAP — AGGREGATE ONLY, no intramatch tape survives this receipt` : "RESOURCE-GAP — R-HIST row missing";
  }
  return `${row.quality}; RESOURCE-GAP — REGISTRY ONLY, no tape row available`;
}

function eventResult(receipt, eventId) { return receipt.results.find((row) => row.event_id === eventId); }
function formationEpoch(meta, legId) { return legId === meta.legA ? Number(meta.legA_formation_end_epoch) : Number(meta.legB_formation_end_epoch); }
function stageEpoch(meta, stage) { return Number(meta.recorder_open_epoch) + stage.hours * 3600; }
function eligiblePrints(prints, meta, legId, afterEpoch = -Infinity) {
  return prints.filter((row) => row.event_id === meta.event_id && row.leg_id === legId && row.timestamp_epoch >= formationEpoch(meta, legId) && row.timestamp_epoch > afterEpoch + 0.005 && row.timestamp_epoch <= Number(meta.bell_epoch));
}
function minimumPrint(rows) { return rows.length ? [...rows].sort((a, b) => a.price_cents - b.price_cents || a.timestamp_epoch - b.timestamp_epoch)[0] : null; }

function expectedBand(stage, legId) {
  const derivation = stage.derivations.find((row) => row.leg_id === legId);
  const prices = derivation.neighbor_rows.map((row) => derivation.anchor_cents * row.ratio);
  return prices.length ? { low: Math.min(...prices), high: Math.max(...prices) } : null;
}
function surprises(stages, prints, meta) {
  const out = [];
  for (const stage of stages) for (const derivation of stage.derivations) {
    const band = expectedBand(stage, derivation.leg_id);
    const realized = minimumPrint(eligiblePrints(prints, meta, derivation.leg_id, stageEpoch(meta, stage)));
    if (!band || !realized) continue;
    if (realized.price_cents < band.low) out.push({ stage: stage.stage, hours: stage.hours, leg_id: derivation.leg_id, prediction: [band.low, band.high], realized: realized.price_cents, direction: "DEEPER_THAN_ALL_NEIGHBORS", magnitude: band.low - realized.price_cents, moment_epoch: realized.timestamp_epoch, print_row: realized._row, receipt: realized.receipt });
    else if (realized.price_cents > band.high) out.push({ stage: stage.stage, hours: stage.hours, leg_id: derivation.leg_id, prediction: [band.low, band.high], realized: realized.price_cents, direction: "SHALLOWER_THAN_ALL_NEIGHBORS_AT_BELL", magnitude: realized.price_cents - band.high, moment_epoch: Number(meta.bell_epoch), print_row: realized._row, receipt: realized.receipt });
  }
  return out;
}

function hindsight(stages, prints, meta) {
  const out = [];
  for (const stage of stages) for (const derivation of stage.derivations) {
    const progress = stage.reads.anchor_settle.formation_progress[derivation.leg_id];
    if (!Number.isFinite(progress) || progress < 1) continue;
    const position = stage.reads.half_pair_state.legs[derivation.leg_id];
    if (position.credited) {
      out.push({ stage: stage.stage, hours: stage.hours, leg_id: derivation.leg_id, decision: `${derivation.action}@${derivation.target_cents ?? "NONE"}`, better_action: "NO_ACTION_CREDITED", realized: position.entry_cents, reading: "half_pair_state.credited=true", defect: "sentence emitted; executor credited guard suppressed mutation" });
      continue;
    }
    const future = minimumPrint(eligiblePrints(prints, meta, derivation.leg_id, stageEpoch(meta, stage)));
    if (!future || derivation.target_cents === future.price_cents) continue;
    const band = expectedBand(stage, derivation.leg_id);
    let reading = "NONE IN THE SIXTEEN — HINDSIGHT ONLY";
    if (band && future.price_cents >= band.low && future.price_cents <= band.high) reading = `neighborhood low envelope ${fmt(band.low, 2)}..${fmt(band.high, 2)}`;
    else if (finite(stage.reads.lows_travel[derivation.leg_id].low_cents) <= future.price_cents) reading = `lows_travel running low ${stage.reads.lows_travel[derivation.leg_id].low_cents}`;
    out.push({ stage: stage.stage, hours: stage.hours, leg_id: derivation.leg_id, decision: `${derivation.action}@${derivation.target_cents ?? "NONE"}`, better_action: `REST@${future.price_cents}`, realized: future.price_cents, print_row: future._row, receipt: future.receipt, moment_epoch: future.timestamp_epoch, reading, defect: null });
  }
  return out;
}

function ceiling(prints, meta, result) {
  const legs = [meta.legA, meta.legB].map((legId) => {
    const low = minimumPrint(eligiblePrints(prints, meta, legId));
    const position = result.functionable_v6.legs[legId];
    const captured = position.entry_cents;
    return {
      leg_id: legId,
      formation_epoch: formationEpoch(meta, legId),
      minimum_cents: low?.price_cents ?? null,
      minimum_epoch: low?.timestamp_epoch ?? null,
      minimum_iso: iso(low?.timestamp_epoch),
      filtered_print_row: low?._row ?? null,
      print_receipt: low?.receipt ?? null,
      captured_cents: captured,
      capture_gap_cents: Number.isInteger(captured) && low ? captured - low.price_cents : null,
      final_rest_cents: position.standing_target_cents,
      final_rest_shortfall_cents: !Number.isInteger(captured) && low && Number.isInteger(position.standing_target_cents) ? low.price_cents - position.standing_target_cents : null,
    };
  });
  const sum = legs.every((row) => Number.isInteger(row.minimum_cents)) ? legs.reduce((total, row) => total + row.minimum_cents, 0) : null;
  return { status: "PROVISIONAL_UNTIL_CC_RULES_BELL", bell_epoch: Number(meta.bell_epoch), bell_source: meta.bell_source, legs, pair_ceiling_sum_cents: sum, pair_ceiling_discount_cents: Number.isInteger(sum) ? 100 - sum : null, captured_sum_cents: result.functionable_v6.combined_entry_cents, captured_discount_cents: result.functionable_v6.delta_vs_100_cents };
}

function rawPrefix(stage, bindings, prints, meta) {
  return Object.entries(stage.reads.books).map(([legId, book]) => {
    const match = String(book.receipt).match(/#row-(\d+)$/);
    const row = match ? Number(match[1]) : null;
    const seen = prints.filter((item) => item.event_id === stage.event_id && item.leg_id === legId && item.timestamp_epoch <= stageEpoch(meta, stage) + 0.005);
    const lastPrint = seen.at(-1);
    return `${legId}: R-BOOK-${legId}#rows-1..${row ?? "?"}, terminal ${book.receipt} = ${book.bid_cents}/${book.ask_cents} last ${book.last_trade_cents ?? "NONE"}; R-PRINTS predicate event=${stage.event_id},leg=${legId},ts<=${fmt(stageEpoch(meta, stage), 3)} (${seen.length} rows${lastPrint ? `; last #row-${lastPrint._row} ${lastPrint.receipt}@${lastPrint.price_cents}` : ""})`;
  }).join("\n\n");
}

function receiptBindings(meta, pass1, files, tickReceipts, truthReceipt, sourceReceipts) {
  const lines = [
    `- **R-LAW:** \`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md\` @ commit \`dcac4032\`, SHA-256 \`c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6\`.`,
    `- **R-STORY:** \`${path.relative(files.repo, files.story).replaceAll("\\", "/")}\`, SHA-256 \`${shaFile(files.story)}\`.`,
    `- **R-RESULT:** \`${path.relative(files.repo, files.storyReceipt).replaceAll("\\", "/")}\`, SHA-256 \`${shaFile(files.storyReceipt)}\`.`,
    `- **R-CORPUS:** \`${path.relative(files.repo, files.corpusIndex).replaceAll("\\", "/")}\`, SHA-256 \`${shaFile(files.corpusIndex)}\`; row numbers are decompressed JSONL rows.`,
    `- **R-RANGE:** external custody \`${files.range}\`, SHA-256 \`${pass1.census.stores.find((row) => row.id === "range_spectrum_v1").sha256}\`, ${fs.statSync(files.range).size} bytes; row/tick refs below.`,
    `- **R-HIST:** external custody \`${files.historical}\`, SHA-256 \`${pass1.census.stores.find((row) => row.id === "historical_events").sha256}\`, ${fs.statSync(files.historical).size} bytes; physical CSV line refs below.`,
    `- **R-PRINTS:** \`${path.relative(files.repo, files.targetPrints).replaceAll("\\", "/")}\`, SHA-256 \`${shaFile(files.targetPrints)}\`; rows are decompressed JSONL rows. Upstream full tape: \`${sourceReceipts.target_prints.path}\`, SHA-256 \`${sourceReceipts.target_prints.sha256}\`.`,
    `- **R-TRUTH:** \`c0056976:${truthReceipt.path}\`, SHA-256 \`${truthReceipt.sha256}\`; event row \`${meta.event_id}\`, bell ${meta.bell_epoch} (${meta.bell_source}).`,
    `- **R-LINEAGE:** external custody \`${sourceReceipts.lineage.path}\`, SHA-256 \`${sourceReceipts.lineage.sha256}\`, ${sourceReceipts.lineage.bytes} bytes, ${sourceReceipts.lineage.rows} rows; only lineage values already printed in R-STORY are used here.`,
  ];
  tickReceipts.forEach((row) => lines.push(`- **R-BOOK-${row.leg_id}:** external custody \`${row.path}\`, SHA-256 \`${row.sha256}\`, ${row.bytes} bytes, ${row.rows} data rows.`));
  return lines.join("\n");
}

function neighborhoodTable(stage, rangeByEvent, historicalByEvent) {
  const lines = ["| Grade | Named neighbor | Score / coverage | Corpus row | Specific source-tape rows leaned on |", "|---|---|---:|---|---|"];
  stage.neighbors.forEach((neighbor) => {
    lines.push(`| ${neighbor.grade} | ${neighbor.event_id} (${neighbor.corpus.event_date}) | ${fmt(neighbor.score)} / ${fmt(neighbor.coverage)} | R-CORPUS#row-${neighbor.corpus._row}; ${neighbor.corpus.quality} | ${sourceEvidence(neighbor, rangeByEvent, historicalByEvent)} |`);
  });
  return lines.join("\n");
}

function arithmeticBlock(stage) {
  return stage.derivations.map((row) => {
    const terms = row.neighbor_rows.map((item) => `${item.event_id}:(${fmt(item.score)}×${fmt(item.coverage)})×(${item.low}/${item.anchor})`).join(" + ");
    const massTerms = row.neighbor_rows.map((item) => `${fmt(item.score)}×${fmt(item.coverage)}`).join(" + ");
    const formation = stage.reads.anchor_settle.formation_progress[row.leg_id];
    const calculation = formation < 1
      ? `Formation progress ${fmt(formation)} < 1 overrides the computed candidate; lawful action is ${row.action}@NONE.`
      : `Σweighted-ratio / Σweight = (${terms}) / ${fmt(row.denominator)} = ${fmt(row.ratio, 12)}. Raw round(${row.anchor_cents}×${fmt(row.ratio, 12)})=${row.raw_target}; m=mean(score×coverage)=(${massTerms})/${row.neighbor_rows.length}=${fmt(row.neighborhood_mass, 12)} using the named-neighbor R-CORPUS/R-RANGE/R-HIST rows immediately above; blend with lineage ${row.lineage_target_cents ?? "NONE"} from the quoted R-STORY sentence gives ${row.blended_target}; min(pair cap ${row.pair_cap_cents}, post-only cap ${row.post_only_cap_cents}) gives ${row.capped_target}. Printed action ${row.action}@${row.target_cents ?? "NONE"}, active-before ${row.active_before_cents ?? "NONE"}.`;
    return `**${row.leg_id}.** ${calculation}\n\n> ${row.sentence}`;
  }).join("\n\n");
}

function turningPointBlock(stage, files, meta, prints, rangeByEvent, historicalByEvent) {
  const readerLines = Object.entries(stage.reads).map(([name, value]) => `| ${name} | \`${JSON.stringify(value)}\` | R-STORY#line-${stage.line}; raw cumulative prefixes above |`);
  return `### TP${stage.stage} — ${fmt(stage.hours)} hours from discovery (${iso(stageEpoch(meta, stage))})

**Raw tape rows → readers.** The sixteen readers consume the cumulative prefixes, not only the terminal rows:

${rawPrefix(stage, files, prints, meta)}

| Reader | Receipt value | Re-derivation pointer |
|---|---|---|
${readerLines.join("\n")}

**Fingerprint.** \`${JSON.stringify(stage.vector)}\` [R-STORY#line-${stage.line}; similarity declaration R-RESULT].

**Named neighborhood and the exact historical rows used.**

${neighborhoodTable(stage, rangeByEvent, historicalByEvent)}

**Derivation arithmetic → action → verbatim sentence.**

${arithmeticBlock(stage)}
`;
}

function captureBlock(value) {
  const rows = value.legs.map((row) => `| ${row.leg_id} | ${row.minimum_cents} | ${fmt((row.minimum_epoch - row.formation_epoch) / 3600)} h after formation; ${row.minimum_iso} | R-PRINTS#row-${row.filtered_print_row}; ${row.print_receipt} | ${row.captured_cents ?? "NONE"} | ${row.capture_gap_cents ?? `NONE; final rest ${row.final_rest_cents}, shortfall ${row.final_rest_shortfall_cents}`} |`);
  return `Status: **${value.status}**. L11 bell ${value.bell_epoch} from ${value.bell_source}; this explanation does not alter it.

| Side | Deepest lawful print | Moment | Receipt | Captured | Gap to ceiling |
|---|---:|---|---|---:|---:|
${rows.join("\n")}

Pair ceiling: ${value.pair_ceiling_sum_cents}¢, discount ${value.pair_ceiling_discount_cents}¢. Captured pair: ${value.captured_sum_cents ?? "NONE"}, discount ${value.captured_discount_cents ?? "NONE"}. Per-side minima need not be simultaneous; this is the deepest standing-rest opportunity each side's tape actually offered.`;
}

function surpriseBlock(rows) {
  if (!rows.length) return "No pass-1 stage forecast missed the receipt-defined neighbor-low envelope.";
  return [
    "Audit convention: because pass 1 emitted no prediction interval, the expected range is the minimum-to-maximum normalized low of its seven named neighbors, mapped onto the target anchor. Every pass-1 stage whose later lawful true-print minimum left that envelope is listed; this is an explanation metric, not a model change.",
    "",
    "| Stage | Side | Neighbor-low prediction | Realized | Departure | Realization receipt |",
    "|---:|---|---:|---:|---:|---|",
    ...rows.map((row) => `| ${row.stage} @ ${fmt(row.hours)}h | ${row.leg_id} | ${fmt(row.prediction[0], 2)}..${fmt(row.prediction[1], 2)} | ${row.realized} | ${row.direction} by ${fmt(row.magnitude, 2)}¢ | ${iso(row.moment_epoch)}; R-PRINTS#row-${row.print_row}; ${row.receipt} |`),
  ].join("\n");
}

function hindsightBlock(rows) {
  if (!rows.length) return "No decision in the pass-1 receipt is beaten under the stated true-print hindsight convention.";
  return [
    "A decision is listed when a later formation-lawful true print proves a different rest would have captured closer to the per-side ceiling, or when a credited leg still receives a new action sentence. This is hindsight, never a claim that the future row was knowable.",
    "",
    "| Stage | Side | Printed decision | Hindsight-better action | Reading that could have licensed it | Realized receipt / defect |",
    "|---:|---|---|---|---|---|",
    ...rows.map((row) => `| ${row.stage} @ ${fmt(row.hours)}h | ${row.leg_id} | ${row.decision} | ${row.better_action} | ${row.reading} | ${row.defect ?? `${iso(row.moment_epoch)}; R-PRINTS#row-${row.print_row}; ${row.receipt}`} |`),
  ].join("\n");
}

function maxHighRatioAtLowThreshold(points, threshold) {
  let best = -Infinity, witness = null;
  points.forEach((point) => { if (point.low >= threshold && point.high > best) { best = point.high; witness = [point.id, 1, point.id, 0]; } });
  for (const a of points) for (const b of points) {
    if (a.id === b.id || a.low === b.low) continue;
    const weightA = (threshold - b.low) / (a.low - b.low);
    if (weightA < 0 || weightA > 1) continue;
    const high = weightA * a.high + (1 - weightA) * b.high;
    if (high > best) { best = high; witness = [a.id, weightA, b.id, 1 - weightA]; }
  }
  return { best, witness };
}

function lajsvaAdjustment(stages, ceilingValue) {
  const finalStage = stages.at(-1);
  const lowId = finalStage.vector.oriented_leg_ids[0], highId = finalStage.vector.oriented_leg_ids[1];
  const lowDerivation = finalStage.derivations.find((row) => row.leg_id === lowId);
  const highDerivation = finalStage.derivations.find((row) => row.leg_id === highId);
  const points = finalStage.neighbors.map((neighbor) => ({
    id: neighbor.event_id,
    low: neighbor.corpus.legs[0].low_cents / neighbor.corpus.legs[0].anchor_cents,
    high: neighbor.corpus.legs[1].low_cents / neighbor.corpus.legs[1].anchor_cents,
  }));
  const lowRequired = 40.5 / lowDerivation.anchor_cents;
  const highRequired = 50.5 / highDerivation.anchor_cents;
  const convex = maxHighRatioAtLowThreshold(points, lowRequired);
  const witness = convex.witness ? `${convex.witness[0]}@${fmt(convex.witness[1])} + ${convex.witness[2]}@${fmt(convex.witness[3])}` : "NONE";
  return `## 5. LAJSVA 47/36 causal chain and adjustment answer

The last turning point above is the full receipt chain. In short: ${highId} used ratio ${fmt(highDerivation.ratio, 12)}, so round(${highDerivation.anchor_cents}×ratio)=${highDerivation.raw_target}; mass ${fmt(highDerivation.neighborhood_mass, 12)} blended lineage ${highDerivation.lineage_target_cents} to ${highDerivation.blended_target}, and caps ${highDerivation.pair_cap_cents}/${highDerivation.post_only_cap_cents} left ${highDerivation.target_cents}. ${lowId} used ratio ${fmt(lowDerivation.ratio, 12)}, so round(${lowDerivation.anchor_cents}×ratio)=${lowDerivation.raw_target}; the same declared mass blended lineage ${lowDerivation.lineage_target_cents} to ${lowDerivation.target_cents}. That is exactly 47/36.

To preserve +6, both sides had to capture at a sum no greater than 94. R-PRINTS proves the tape offered ${ceilingValue.legs.map((row) => `${row.leg_id} ${row.minimum_cents}`).join(" + ")} = ${ceilingValue.pair_ceiling_sum_cents}, so 51/41 would have completed at +${ceilingValue.pair_ceiling_discount_cents}. For the final seven alone, the ${lowId} raw target needs normalized low at least ${fmt(lowRequired, 6)} to round to 41, while ${highId} needs at least ${fmt(highRequired, 6)} to round to 51. Under every nonnegative reweighting of those same seven that meets the low-side requirement, the maximum attainable high-side ratio is ${fmt(convex.best, 6)} (best convex witness ${witness}), below ${fmt(highRequired, 6)}. **Therefore no declared-similarity reweighting of the final seven preserves +6.**

A corpus adjustment could only be claimed after adding and testing a same-elapsed-stage survival table. Pass 1 contains no such table. This no-rerun lane therefore stamps the corpus answer **UNPROVED**, not yes.`;
}

function danpraLookalikes(stages, rangeByEvent) {
  const finalStage = stages.at(-1);
  const lines = finalStage.neighbors.map((neighbor) => {
    const range = rangeByEvent.get(neighbor.event_id);
    const legs = neighbor.corpus.legs.map((summary) => {
      const tape = range?.legs?.[summary.leg_id];
      const last = tape?.ticks?.at(-1);
      return `${summary.leg_id}: anchor ${summary.anchor_cents}, low ${summary.low_cents}, close ${summary.close_cents}; same-stage terminal tick#${tape?.ticks?.length ?? "?"} [${last?.join(",") ?? "missing"}]`;
    }).join("; ");
    return `| ${neighbor.event_id} | ${fmt(neighbor.score)} | R-CORPUS#row-${neighbor.corpus._row}; R-RANGE#row-${range?._row ?? "?"} | ${legs} |`;
  });
  const dan = finalStage.derivations.find((row) => row.leg_id === "DAN"), pra = finalStage.derivations.find((row) => row.leg_id === "PRA");
  return `## 5. DANPRA 51/33 and the May/June tapes at the same stage

DAN: round(58×${fmt(dan.ratio, 12)})=${dan.raw_target}; mass ${fmt(dan.neighborhood_mass, 12)} blends lineage ${dan.lineage_target_cents} to ${dan.blended_target}; caps ${dan.pair_cap_cents}/${dan.post_only_cap_cents} leave 51. PRA: round(41×${fmt(pra.ratio, 12)})=${pra.raw_target}; the same mass blends lineage ${pra.lineage_target_cents} to ${pra.blended_target}; caps ${pra.pair_cap_cents}/${pra.post_only_cap_cents} leave 33.

"Same stage" here means each neighbor's terminal/right-edge row because the query point is DANPRA's provisional bell. These are the exact May/June source rows, not paraphrased outcomes:

| Neighbor | Score | Receipts | Terminal tape facts |
|---|---:|---|---|
${lines.join("\n")}

The neighborhood's lows licensed 51/33; its terminal rows show that those games generally recovered toward their anchors. DANPRA never supplied the antecedent dip, so recovery behavior was not enough to make the rests reachable.`;
}

function explainedMarkdown({ eventId, stages, selected, bindings, rangeByEvent, historicalByEvent, files, prints, meta, ceilingValue, surpriseRows, hindsightRows }) {
  const short = SHORT[key(eventId)];
  const story = STORY_TEXT[short];
  ensure(wordCount(story) <= 900, `${short} story exceeds two-page guard`);
  const extra = short === "LAJSVA" ? lajsvaAdjustment(stages, ceilingValue) : short === "DANPRA" ? danpraLookalikes(stages, rangeByEvent) : "";
  return (`# Game explained — ${short}

License: LAW_INDEX read at \`dcac4032\`, SHA-256 \`c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6\`; laws L0 L8 L11 L18 L20 L22. Explanation lane only: pass-1 receipts and named custody rows; zero runs, zero passes, zero tuning, zero 804 reads.

Steps-Behind Law: assume the OS is always a few steps behind the market's finesse. This explanation states what was missed, what surprised, and what remains unexplained.

## Receipt bindings

${bindings}

NEIGHBOR-GRAIN: receipt-bearing comparisons below are either RANGE_SPECTRUM_PATH polling paths (R-CORPUS + R-RANGE, approximately 100 ticks per leg) or HISTORICAL_EVENT_AGGREGATE rows (R-CORPUS + R-HIST, no intramatch path). RESOURCE-GAP: no raw-tape order-book depth receipt exists at the matched-neighbor stage; range-path best-five summaries are not raw depth.

## 1. The story — hour 0 to bell (${wordCount(story)} words; two-page guard passed)

${story}

## 2. Turning points — ${selected.length} complete causal chains

${selected.map((stage) => turningPointBlock(stage, files, meta, prints, rangeByEvent, historicalByEvent)).join("\n")}

## 3. Capture vs ceiling

${captureBlock(ceilingValue)}

## 4. The surprise and humility ledger

### Every receipt-defined neighborhood-range departure

${surpriseBlock(surpriseRows)}

### Every decision hindsight beats

${hindsightBlock(hindsightRows)}

### What remains unexplained

${UNEXPLAINED[short].map((row) => `- ${row}`).join("\n")}
${extra ? `\n\n${extra}` : ""}
`).trimEnd();
}

async function main() {
  const repo = required("repo"), pass1Root = required("pass1"), privateRoot = required("private"), cache = required("cache"), output = required("output");
  const story = path.join(pass1Root, "FOUR_STORIES.md"), storyReceipt = path.join(pass1Root, "FOUR_STORIES_RECEIPT.json"), corpusIndex = path.join(pass1Root, "CORPUS_INDEX.jsonl.gz"), targetPrints = path.join(pass1Root, "TARGET_PRINTS_5.jsonl.gz"), sourceFile = path.join(pass1Root, "SOURCE_RECEIPTS.json"), censusFile = path.join(pass1Root, "CORPUS_CENSUS.json"), pass1ManifestFile = path.join(pass1Root, "ARTIFACT_HASH_MANIFEST.json");
  const range = path.join(cache, "range_spectrum_v1.jsonl"), historical = path.join(cache, "historical_events_materialized.csv");
  const requiredFiles = [story, storyReceipt, corpusIndex, targetPrints, sourceFile, censusFile, pass1ManifestFile, range, historical];
  requiredFiles.forEach((file) => ensure(fs.existsSync(file), `missing receipt ${file}`));
  const pass1Manifest = JSON.parse(fs.readFileSync(pass1ManifestFile, "utf8"));
  for (const name of ["FOUR_STORIES.md", "FOUR_STORIES_RECEIPT.json", "CORPUS_INDEX.jsonl.gz", "TARGET_PRINTS_5.jsonl.gz"]) ensure(pass1Manifest.files[name].sha256 === shaFile(path.join(pass1Root, name)), `pass1 hash mismatch ${name}`);

  const receipt = JSON.parse(fs.readFileSync(storyReceipt, "utf8"));
  ensure(receipt.pass === 1 && receipt.passes_executed === 1 && receipt.self_stop_triggered, "not the frozen pass-1 receipt");
  const sourceReceipts = JSON.parse(fs.readFileSync(sourceFile, "utf8")), census = JSON.parse(fs.readFileSync(censusFile, "utf8"));
  const parsed = parseStory(story);
  const corpusRows = loadGzipJsonl(corpusIndex), corpus = new Map(corpusRows.map((row) => [row.event_id, row]));
  const allStages = new Map(TARGETS.map((eventId) => [eventId, parsed.get(eventId).map((stage) => enrichStage(stage, corpus, receipt.similarity_declaration))]));
  const named = new Set([...allStages.values()].flatMap((stages) => stages.flatMap((stage) => stage.neighbors.map((row) => row.event_id))));
  const rangeByEvent = new Map(loadJsonl(range).filter((row) => named.has(row.event)).map((row) => [row.event, row]));
  const historicalByEvent = historicalRows(historical);
  const prints = loadGzipJsonl(targetPrints).filter((row) => TARGETS.includes(row.event_id));
  ensure(new Set(prints.map((row) => row.event_id)).size === 4, "filtered prints scope mismatch");

  const truthPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
  const truthBytes = gitShow(repo, `c0056976:${truthPath}`), truth = JSON.parse(truthBytes.toString("utf8"));
  const truthByEvent = new Map(truth.rows.filter((row) => TARGETS.includes(row.event_id)).map((row) => [row.event_id, row]));
  ensure(truthByEvent.size === 4, "truth target count");
  const truthReceipt = { path: truthPath, sha256: shaBytes(truthBytes) };
  const files = { repo, story, storyReceipt, corpusIndex, targetPrints, range, historical };
  fs.mkdirSync(output, { recursive: true });

  const gameReceipts = [];
  for (const eventId of TARGETS) {
    const short = SHORT[key(eventId)], stages = allStages.get(eventId), picks = PICKS[key(eventId)], selected = picks.map((number) => stages[number - 1]);
    ensure(selected.every(Boolean) && selected.length >= 5 && selected.length <= 8, `turning-point selection ${eventId}`);
    const meta = truthByEvent.get(eventId), result = eventResult(receipt, eventId);
    const tickReceipts = [meta.legA, meta.legB].map((legId) => {
      const file = path.join(privateRoot, "fit-local", "ticks", `${eventId}-${legId}.csv.gz`), raw = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8");
      return { leg_id: legId, ...physicalReceipt(file), rows: raw.split(/\r?\n/).filter(Boolean).length - 1 };
    });
    const bindings = receiptBindings(meta, { census }, files, tickReceipts, truthReceipt, sourceReceipts);
    const ceilingValue = ceiling(prints, meta, result), surpriseRows = surprises(stages, prints, meta), hindsightRows = hindsight(stages, prints, meta);
    const markdown = explainedMarkdown({ eventId, stages, selected, bindings, rangeByEvent, historicalByEvent, files, prints, meta, ceilingValue, surpriseRows, hindsightRows });
    const outFile = path.join(output, `GAME_EXPLAINED_${short}.md`);
    writeText(outFile, markdown);
    gameReceipts.push({ event_id: eventId, short_id: short, pass1_turning_points: stages.length, explained_turning_points: selected.map((row) => row.stage), story_words: wordCount(STORY_TEXT[short]), capture_vs_ceiling: ceilingValue, surprises: surpriseRows.length, hindsight_beaten_decisions: hindsightRows.length, post_credit_sentence_actions: hindsightRows.filter((row) => row.defect).length, unexplained: UNEXPLAINED[short], file: path.basename(outFile) });
  }

  const humility = [
    "# Humility ledger — four games, pass-1 receipts only",
    "",
    "License: LAW_INDEX @ `dcac4032`, SHA-256 `c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6`; L0 L8 L11 L18 L20 L22. Zero new passes, reruns, tuning, or 804 engagement.",
    "",
    "| Game | Captured | Provisional lawful ceiling | Capture gap | Surprise rows | Hindsight-beaten decisions | Post-credit sentence actions |",
    "|---|---:|---:|---:|---:|---:|---:|",
    ...gameReceipts.map((row) => {
      const c = row.capture_vs_ceiling;
      const gap = c.legs.map((leg) => `${leg.leg_id}:${leg.capture_gap_cents ?? `uncaptured/rest-short-${leg.final_rest_shortfall_cents}`}`).join(", ");
      return `| ${row.short_id} | ${c.captured_sum_cents ?? "NONE"} | ${c.pair_ceiling_sum_cents} (Δ${c.pair_ceiling_discount_cents}) | ${gap} | ${row.surprises} | ${row.hindsight_beaten_decisions} | ${row.post_credit_sentence_actions} |`;
    }),
    "",
    "## Plain admissions",
    "",
    ...gameReceipts.flatMap((row) => [`### ${row.short_id}`, "", ...row.unexplained.map((item) => `- ${item}`), ""]),
    "## System-level miss",
    "",
    "SENTENCE==ACTION is internally true, but it is not sufficient: after a leg is credited, pass 1 can still derive and print PLACE_REST while the replay executor separately suppresses the mutation with its credited-position guard. That is a semantic action/execution gap, not a sentence-string mismatch.",
  ].join("\n");
  writeText(path.join(output, "HUMILITY_LEDGER.md"), humility);

  const explanationReceipt = {
    label: "V54_FOUR_GAMES_EXPLAINED_HUMILITY_LEDGER",
    license: { law_index_commit: "dcac4032", law_index_sha256: "c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6", laws: ["L0", "L8", "L11", "L18", "L20", "L22"] },
    scope: { explanation_only: true, source_pass: 1, new_passes: 0, reruns: 0, tuning: false, full_804_run: false, fixed_804_read: false, sealed_read: false, live_mutation: false, targets: TARGETS },
    inputs: { pass1_story: physicalReceipt(story), pass1_result: physicalReceipt(storyReceipt), corpus_index: physicalReceipt(corpusIndex), filtered_prints: physicalReceipt(targetPrints), range_custody: { path: range, sha256: census.stores.find((row) => row.id === "range_spectrum_v1").sha256, bytes: fs.statSync(range).size }, historical_custody: { path: historical, sha256: census.stores.find((row) => row.id === "historical_events").sha256, bytes: fs.statSync(historical).size }, truth_table: truthReceipt },
    games: gameReceipts,
  };
  writeJson(path.join(output, "EXPLANATION_RECEIPT.json"), explanationReceipt);

  const manifestFiles = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const manifest = { label: "V54_FOUR_GAMES_EXPLAINED_HUMILITY_LEDGER", files: Object.fromEntries(manifestFiles.map((name) => [name, physicalReceipt(path.join(output, name))])), scope: explanationReceipt.scope };
  ensure(Object.values(manifest.files).every((row) => row.bytes <= 50 * 1024 * 1024), "L22 file cap exceeded");
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), manifest);
  process.stdout.write(canonical({ output, files: manifestFiles.length + 1, games: gameReceipts.map((row) => ({ game: row.short_id, turning_points: row.explained_turning_points, surprises: row.surprises, hindsight: row.hindsight_beaten_decisions, post_credit: row.post_credit_sentence_actions, ceiling: row.capture_vs_ceiling.pair_ceiling_sum_cents })), scope: explanationReceipt.scope }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error.message}\n`); process.exitCode = 1; });
