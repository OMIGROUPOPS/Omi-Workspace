import crypto from "node:crypto";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import { PassThrough } from "node:stream";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const dataPath = path.join(here, "data", "altgas.json");
const outputPath = path.join(here, "data", "altgas.face.json");
const osPath = path.resolve(here, "..", "arb-executor", "analysis", "window1_v54_dual_belief_os.js");
const legs = ["ALT", "GAS"];

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[index + 1]]);
  return pairs;
}, []));
const tracePath = typeof args.trace === "string" ? path.resolve(args.trace) : null;
const eventId = typeof args.event === "string" ? args.event : "KXATPMATCH-26JUL12ALTGAS";
const tapeDir = typeof args["tape-dir"] === "string" ? path.resolve(args["tape-dir"]) : null;

const raw = tracePath
  ? await loadRawFromTrace(tracePath, eventId, tapeDir)
  : JSON.parse(await fsp.readFile(dataPath, "utf8"));
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
    member_count: Number.isFinite(Number(storedMemberCount)) ? Number(storedMemberCount) : null,
    weight_sum: Number.isFinite(Number(storedWeightSum)) ? Number(storedWeightSum) : null,
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
  let firstStage = null;
  let traceLines = 0;
  let matched = 0;
  for await (const line of lines) {
    if (!line) continue;
    traceLines += 1;
    const row = JSON.parse(line);
    if (row?.event_id !== event) continue;
    matched += 1;
    if (row.kind === "DECISION_STAGE") {
      firstStage ??= row;
      stages.push({
        kind: row.kind,
        trigger: row.trigger ?? null,
        receipt: row.receipt ?? null,
        timestamp_epoch: row.timestamp_epoch ?? null,
        books: row?.reads?.books?.value ?? null,
        lows_travel: row?.reads?.lows_travel?.value ?? null,
        macro: { survivor_shapes: row?.layers?.macro?.context?.survivor_shapes ?? null },
        micro: { beliefs: row?.layers?.micro?.context?.beliefs ?? null },
        derivations: Array.isArray(row.derivations) ? row.derivations.map(slimDerivation) : [],
      });
    } else {
      others.push(row);
    }
  }
  if (!firstStage) throw new Error(`No DECISION_STAGE rows for ${event} in ${file}`);
  const traceSha256 = hash.digest("hex");
  return {
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
    running_low: stage?.lows_travel?.[leg]?.observed_traded_low_cents ?? null,
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
    } : null,
    action: derivation?.action ? {
      name: actionName,
      target_cents: derivation.action.target_cents ?? null,
      reason: derivation.action.reason ?? null,
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
    receipt: stage.receipt ?? null,
    kind: stage.kind,
    legs: Object.fromEntries(legs.map((leg) => [leg, stageLeg(stage, leg)])),
  };
}

function otherEntry(row) {
  const result = {
    t: null,
    receipt: null,
    kind: row.kind,
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
const osSha256 = crypto.createHash("sha256").update(await fsp.readFile(osPath)).digest("hex");
const face = {
  provenance: {
    event_id: raw?.provenance?.event_id ?? null,
    trace_sha256: raw?.provenance?.trace_sha256 ?? null,
    os_sha256: osSha256,
  },
  legs,
  bell: {
    t: bellHours,
    timestamp_epoch: firstStageEpoch + bellHours * 3600,
    source: raw?.bell?.bell_source ?? null,
  },
  tape,
  os: osRows,
};

const payload = `${JSON.stringify(face)}\n`;
if (Buffer.byteLength(payload) >= 2 * 1024 * 1024) {
  throw new Error(`altgas.face.json exceeds 2 MiB: ${Buffer.byteLength(payload)} bytes`);
}
const temporaryPath = `${outputPath}.tmp`;
await fsp.writeFile(temporaryPath, payload);
await fsp.rename(temporaryPath, outputPath);
process.stdout.write(`wrote ${outputPath} (${Buffer.byteLength(payload)} bytes)\n`);
process.stdout.write(`tape ALT=${tape.ALT.length} GAS=${tape.GAS.length}; os=${osRows.length}; bell=${bellHours}\n`);
