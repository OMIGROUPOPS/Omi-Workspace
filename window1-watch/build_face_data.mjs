import crypto from "node:crypto";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import { PassThrough } from "node:stream";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { extendFace, bindCustody, writeGameIndex, inspectorSummary } from "./face_contract.mjs";
import { packFace } from "./face_encoding.mjs";
import { readPinnedTruth, attachRecordedTruth } from "./recorded_truth.mjs";
import { chartSource, attachChartActions } from "./chart_actions.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const dataPath = path.join(here, "data", "altgas.json");
let legs = [];

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[index + 1]]);
  return pairs;
}, []));
const tracePath = typeof args.trace === "string" ? path.resolve(args.trace) : null;
const eventId = typeof args.event === "string" ? args.event : "KXATPMATCH-26JUL12ALTGAS";
const tapeDir = typeof args["tape-dir"] === "string" ? path.resolve(args["tape-dir"]) : null;
if (!/^[A-Za-z0-9_-]+$/.test(eventId)) throw new Error("Unsafe event id");
const outputPath = args.out ? path.resolve(args.out) : path.join(here, "data", tracePath ? `${eventId}.face.json` : "altgas.face.json");
const stagesDir = path.join(path.dirname(outputPath), `${eventId}.stages`);
await fsp.mkdir(stagesDir, { recursive: true });

const raw = tracePath
  ? await loadRawFromTrace(tracePath, eventId, tapeDir)
  : JSON.parse(await fsp.readFile(args.input ?? dataPath, "utf8"));
legs = raw.legs ?? Object.keys(raw?.stages?.[0]?.books ?? {});
if (legs.length !== 2) throw new Error(`Expected two stored legs, got ${JSON.stringify(legs)}`);
const firstStageEpoch = raw?.bell?.first_stage_epoch;
const bellHours = raw?.bell?.hours_to_truth_bell_at_first_stage;
if (!Number.isFinite(firstStageEpoch) || !Number.isFinite(bellHours)) {
  throw new Error("altgas.json has no finite first-stage or bell clock");
}

function hoursFromFirstStage(epoch) {
  return Number.isFinite(epoch) ? (epoch - firstStageEpoch) / 3600 : null;
}

const nyFormatter = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
});

function wallParts(epochMs) {
  const parts = Object.fromEntries(nyFormatter.formatToParts(new Date(epochMs))
    .filter((part) => part.type !== "literal")
    .map((part) => [part.type, Number(part.value)]));
  return Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second);
}

function parseNewYorkEpoch(text) {
  const match = /^(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2}):(\d{2}) (AM|PM)$/.exec(text);
  if (!match) throw new Error(`Unrecognized ts_et: ${text}`);
  let hour = Number(match[4]) % 12;
  if (match[7] === "PM") hour += 12;
  const desiredWall = Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]), hour, Number(match[5]), Number(match[6]));
  let epochMs = desiredWall;
  for (let pass = 0; pass < 2; pass += 1) epochMs += desiredWall - wallParts(epochMs);
  if (wallParts(epochMs) !== desiredWall) throw new Error(`America/New_York conversion failed: ${text}`);
  return epochMs / 1000;
}

function parseCsvLine(line) {
  const fields = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '"') {
      if (quoted && line[index + 1] === '"') {
        value += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === "," && !quoted) {
      fields.push(value);
      value = "";
    } else {
      value += character;
    }
  }
  fields.push(value);
  return fields;
}

function cents(value, zeroIsNull = false) {
  if (value === "" || value == null) return null;
  const number = Number(value);
  if (!Number.isFinite(number) || (zeroIsNull && number === 0)) return null;
  return number;
}

function weightedQuantile(rows, fraction) {
  const ordered = rows
    .filter((row) => Number.isFinite(row.level) && Number.isFinite(row.weight) && row.weight > 0)
    .sort((left, right) => left.level - right.level);
  const total = ordered.reduce((sum, row) => sum + row.weight, 0);
  if (!(total > 0)) return null;
  const target = total * fraction;
  let cumulative = 0;
  for (const row of ordered) {
    cumulative += row.weight;
    if (cumulative >= target) return row.level;
  }
  return ordered.at(-1)?.level ?? null;
}

function memberBand(derivation) {
  const membership = derivation?.overlap_membership ?? {};
  const posteriorRows = derivation?.derivation?.pricing_authority?.true_conditioning?.posterior_rows;
  const weightedRows = Array.isArray(posteriorRows) ? posteriorRows.map((row) => ({
    level: Number.isFinite(row?.candidate_level_cents) ? row.candidate_level_cents : null,
    weight: Number.isFinite(row?.conditioning_weight) ? row.conditioning_weight : null,
    remainingDip: Number.isFinite(row?.member_remaining_dip) ? row.member_remaining_dip : null,
  })).filter((row) => Number.isFinite(row.level) && Number.isFinite(row.weight) && row.weight > 0) : [];
  const posteriorWeight = weightedRows.reduce((sum, row) => sum + row.weight, 0);
  const zeroDipWeight = weightedRows.reduce((sum, row) => sum + (row.remainingDip === 0 ? row.weight : 0), 0);
  const storedMemberCount = membership?.member_count ?? derivation?.membership_count;
  const storedWeightSum = membership?.weight_sum ?? derivation?.membership_weight_sum;
  return {
    member_count: storedMemberCount != null && Number.isFinite(Number(storedMemberCount)) ? Number(storedMemberCount) : null,
    weight_sum: storedWeightSum != null && Number.isFinite(Number(storedWeightSum)) ? Number(storedWeightSum) : null,
    member_remaining_dip_zero_weighted_share: posteriorWeight > 0 ? zeroDipWeight / posteriorWeight : null,
    candidate_level_q10_cents: weightedQuantile(weightedRows, 0.10),
    candidate_level_q25_cents: weightedQuantile(weightedRows, 0.25),
    candidate_level_q50_cents: weightedQuantile(weightedRows, 0.50),
    candidate_level_q75_cents: weightedQuantile(weightedRows, 0.75),
    candidate_level_q90_cents: weightedQuantile(weightedRows, 0.90),
  };
}

function slimDerivation(derivation) {
  return {
    leg_id: derivation?.leg_id ?? null,
    action: derivation?.action ?? null,
    layered_dual_belief: {
      envelope_placement: {
        writer_lane: derivation?.layered_dual_belief?.envelope_placement?.writer_lane ?? null,
        mode: derivation?.layered_dual_belief?.envelope_placement?.mode ?? null,
      },
    },
    face_member_band: memberBand(derivation),
    face_authority_source: derivation?.derivation?.pricing_authority?.authority_source ?? null,
  };
}

async function loadRawFromTrace(file, event, custodyTapeDir) {
  if (!custodyTapeDir) throw new Error("--trace requires --tape-dir");
  const hash = crypto.createHash("sha256");
  const compressed = fs.createReadStream(file);
  compressed.on("data", (chunk) => hash.update(chunk));
  const input = compressed.pipe(file.endsWith(".gz") ? zlib.createGunzip() : new PassThrough());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  const stages = [];
  const others = [];
  const chartSources = new Map();
  let firstStage = null;
  let traceLines = 0;
  let matched = 0;
  for await (const line of lines) {
    if (!line) continue;
    traceLines += 1;
    const row = JSON.parse(line);
    if (row?.event_id !== event) continue;
    matched += 1;
    if (["DECISION_STAGE", "FILL_EVENT"].includes(row.kind)) chartSources.set(traceLines, chartSource(row));
    const receipt = row.receipt ?? row.fill_event_receipt?.captured_at_receipt ?? null;
    const receiptId = crypto.createHash("sha256").update(`${row.kind}\0${receipt}\0${traceLines}`).digest("hex");
    const detail = { source: { event_id: event, trace_row: traceLines, receipt }, inspector: inspectorSummary(row), row };
    await fsp.writeFile(path.join(stagesDir, `${receiptId}.json.gz`), zlib.gzipSync(JSON.stringify(detail)));
    const detailRef = { trace_row: traceLines, receipt_id: receiptId, detail_url: `/data/${event}.stages/${receiptId}.json` };
    if (row.kind === "DECISION_STAGE") {
      firstStage ??= row;
      legs = Object.keys(row?.reads?.books?.value ?? {});
      stages.push({
        ...detailRef,
        kind: row.kind,
        trigger: row.trigger ?? null,
        receipt: row.receipt ?? null,
        timestamp_epoch: row.timestamp_epoch ?? null,
        books: row?.reads?.books?.value ?? null,
        lows_travel: row?.reads?.lows_travel?.value ?? null,
        half_pair_state: row?.reads?.half_pair_state?.value ?? null,
        statuses: Object.fromEntries(Object.entries(row.layers ?? {}).map(([key, value]) => [key, value?.context?.status ?? null])),
        macro: { survivor_shapes: row?.layers?.macro?.context?.survivor_shapes ?? null },
        micro: { beliefs: Object.fromEntries(Object.entries(row?.layers?.micro?.context?.beliefs ?? {}).map(([leg, b]) => [leg, Object.fromEntries(["status", "belief_price_cents", "predicted_cents", "phase_projection_telemetry_cents", "q_author", "x_author", "plain_sentence", "family", "deadline", "predicted_minutes_to_bell"].map(k => [k, b[k] ?? null]))])) },
        derivations: Array.isArray(row.derivations) ? row.derivations.map(slimDerivation) : [],
      });
    } else {
      others.push({ ...row, ...detailRef });
    }
  }
  if (!firstStage) throw new Error(`No DECISION_STAGE rows for ${event} in ${file}`);
  const traceSha256 = hash.digest("hex");
  return {
    legs,
    chartSources,
    category: firstStage?.reads?.category?.value?.category ?? null,
    formation_end_epoch: Object.values(firstStage?.layers?.micro?.context?.beliefs ?? {}).map(b => b.own_evidence?.formation_end_epoch).find(Number.isFinite) ?? null,
    provenance: {
      event_id: event,
      trace_path: file,
      trace_sha256: traceSha256,
      trace_lines: traceLines,
      rows_for_event: matched,
    },
    bell: {
      hours_to_truth_bell_at_first_stage: firstStage?.reads?.time_in_window?.value?.hours_to_truth_bell,
      bell_source: firstStage?.reads?.time_in_window?.value?.bell_source ?? null,
      first_stage_epoch: firstStage.timestamp_epoch,
    },
    stages,
    others,
    tape: Object.fromEntries(legs.map((leg) => [leg, {
      file: path.join(custodyTapeDir, `${event}-${leg}.csv.gz`),
    }])),
  };
}

async function loadTape(file) {
  const input = fs.createReadStream(file).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let header = null;
  let indexes = null;
  let previous = null;
  const rows = [];
  for await (const line of lines) {
    if (!header) {
      header = parseCsvLine(line);
      indexes = Object.fromEntries(header.map((name, index) => [name, index]));
      for (const required of ["ts_et", "bid_1", "ask_1", "last_trade"]) {
        if (!Number.isInteger(indexes[required])) throw new Error(`${path.basename(file)} lacks ${required}`);
      }
      continue;
    }
    if (!line) continue;
    const fields = parseCsvLine(line);
    const row = {
      t: hoursFromFirstStage(parseNewYorkEpoch(fields[indexes.ts_et])),
      bid: cents(fields[indexes.bid_1]),
      ask: cents(fields[indexes.ask_1]),
      last: cents(fields[indexes.last_trade], true),
    };
    const signature = `${row.bid ?? "null"}|${row.ask ?? "null"}|${row.last ?? "null"}`;
    if (signature !== previous) {
      rows.push(row);
      previous = signature;
    }
  }
  return rows;
}

function emptyLeg() {
  return {
    bid: null,
    ask: null,
    running_low: null,
    survivors: null,
    sentence: null,
    action: null,
    rest: null,
    print: null,
    fill: null,
  };
}

function stageLeg(stage, leg) {
  const belief = stage?.micro?.beliefs?.[leg] ?? null;
  const survivorList = stage?.macro?.survivor_shapes?.legs?.[leg]?.survivor_shapes;
  const derivation = (stage?.derivations ?? []).find((row) => row?.leg_id === leg) ?? null;
  const band = derivation?.face_member_band ?? memberBand(derivation);
  const actionName = derivation?.action?.action ?? null;
  const isRest = actionName === "PLACE_REST" || actionName === "REPRICE_REST";
  return {
    bid: stage?.books?.[leg]?.bid_cents ?? null,
    ask: stage?.books?.[leg]?.ask_cents ?? null,
    last: stage?.books?.[leg]?.last_trade_cents ?? null,
    running_low: stage?.lows_travel?.[leg]?.observed_traded_low_cents ?? null,
    true_trade_count: stage?.lows_travel?.[leg]?.true_trade_count ?? null,
    survivors: Array.isArray(survivorList) ? survivorList.length : null,
    member_count: band.member_count,
    weight_sum: band.weight_sum,
    member_remaining_dip_zero_weighted_share: band.member_remaining_dip_zero_weighted_share,
    candidate_level_q10_cents: band.candidate_level_q10_cents,
    candidate_level_q25_cents: band.candidate_level_q25_cents,
    candidate_level_q50_cents: band.candidate_level_q50_cents,
    candidate_level_q75_cents: band.candidate_level_q75_cents,
    candidate_level_q90_cents: band.candidate_level_q90_cents,
    sentence: belief ? {
      status: belief.status ?? null,
      P: belief.belief_price_cents ?? null,
      Q: belief.predicted_cents ?? null,
      X: belief.phase_projection_telemetry_cents ?? null,
      q_author: belief.q_author ?? null,
      x_author: belief.x_author ?? null,
      plain_sentence: belief.plain_sentence ?? null,
      family: belief.family ?? null,
      predicted_minutes_to_bell: belief.predicted_minutes_to_bell ?? null,
      authority_source: derivation?.face_authority_source ?? derivation?.derivation?.pricing_authority?.authority_source ?? null,
    } : null,
    action: derivation?.action ? {
      name: actionName,
      target_cents: derivation.action.target_cents ?? null,
      reason: derivation.action.reason ?? null,
      lane: derivation?.layered_dual_belief?.envelope_placement?.writer_lane ?? null,
    } : null,
    rest: isRest ? {
      action: actionName,
      cents: derivation.action.target_cents ?? null,
      lane: derivation?.layered_dual_belief?.envelope_placement?.writer_lane ?? null,
      mode: derivation?.layered_dual_belief?.envelope_placement?.mode ?? null,
    } : null,
    print: null,
    fill: null,
  };
}

function stageEntry(stage) {
  return {
    t: hoursFromFirstStage(stage.timestamp_epoch),
    trace_row: stage.trace_row ?? null,
    receipt: stage.receipt ?? null,
    kind: stage.kind,
    receipt_id: stage.receipt_id ?? null,
    detail_url: stage.detail_url ?? null,
    statuses: stage.statuses ?? null,
    standing: stage?.half_pair_state?.legs ? Object.fromEntries(Object.entries(stage.half_pair_state.legs).map(([l,s])=>[l,{credited:s.credited??null,entry_cents:s.entry_cents??null,standing_target_cents:s.standing_target_cents??null}])) : null,
    legs: Object.fromEntries(legs.map((leg) => [leg, stageLeg(stage, leg)])),
  };
}

function otherEntry(row) {
  const result = {
    t: null,
    trace_row: row.trace_row ?? null,
    receipt: null,
    kind: row.kind,
    receipt_id: row.receipt_id ?? null,
    detail_url: row.detail_url ?? null,
    legs: Object.fromEntries(legs.map((leg) => [leg, emptyLeg()])),
  };
  if (row.kind === "FLOOR_PRINT_DECISION_INSTANT") {
    result.t = hoursFromFirstStage(row.timestamp_epoch);
    result.receipt = row.receipt ?? null;
    if (legs.includes(row.leg_id)) result.legs[row.leg_id].print = { cents: row.print_price_cents ?? null };
  } else if (row.kind === "FILL_EVENT") {
    const fill = row.fill_event_receipt;
    result.t = hoursFromFirstStage(fill?.context?.fill_timestamp_epoch);
    result.receipt = fill?.captured_at_receipt ?? null;
    const leg = fill?.context?.leg_id;
    if (legs.includes(leg)) result.legs[leg].fill = { cents: fill.context.entry_cents ?? null };
  }
  return result;
}

const tape = Object.fromEntries(await Promise.all(legs.map(async (leg) => {
  const file = raw?.tape?.[leg]?.file;
  if (!file) throw new Error(`altgas.json has no tape file for ${leg}`);
  return [leg, await loadTape(file)];
})));

const osRows = [
  ...(raw.stages ?? []).map(stageEntry),
  ...(raw.others ?? []).map(otherEntry),
];
const custody = await bindCustody(tracePath ?? raw.provenance?.trace_path, raw.provenance?.trace_sha256, args["receipt-dir"]);
const face = {
  provenance: {
    event_id: raw?.provenance?.event_id ?? null,
    trace_sha256: raw?.provenance?.trace_sha256 ?? null,
    trace_path: raw?.provenance?.trace_path ?? null,
    ...custody,
  },
  legs,
  category: raw.category ?? null,
  formation_end_epoch: raw.formation_end_epoch ?? null,
  bell: {
    t: bellHours,
    timestamp_epoch: firstStageEpoch + bellHours * 3600,
    source: raw?.bell?.bell_source ?? null,
  },
  tape,
  os: osRows,
};
// Keep the original no-argument exporter contract for rerun_altgas.ps1 and its
// legacy page. Tune-test is the explicit trace-backed path, with full inspectors.
if (tracePath) await extendFace(face, { here, eventId, benchPath: args.bench });
attachRecordedTruth(face, readPinnedTruth(path.resolve(here, "..")));
if (tracePath) attachChartActions(face, raw.chartSources);

const payload = `${JSON.stringify(tracePath ? packFace(face) : face)}\n`;
const compressedPayload = zlib.gzipSync(payload);
if (compressedPayload.length >= 2 * 1024 * 1024) {
  throw new Error(`Face transfer payload exceeds 2 MiB: ${compressedPayload.length} bytes`);
}
const temporaryPath = `${outputPath}.tmp`;
await fsp.writeFile(temporaryPath, payload);
await fsp.rename(temporaryPath, outputPath);
await fsp.writeFile(`${outputPath}.gz`,compressedPayload);
process.stdout.write(`wrote ${outputPath} (${Buffer.byteLength(payload)} bytes; gzip transfer ${compressedPayload.length} bytes)\n`);
await writeGameIndex(path.dirname(outputPath));
process.stdout.write(`tape ${legs.map(l => `${l}=${tape[l].length}`).join(" ")}; os=${osRows.length}; bell=${bellHours}\n`);
