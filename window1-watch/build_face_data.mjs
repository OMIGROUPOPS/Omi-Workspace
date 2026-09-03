import crypto from "node:crypto";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const dataPath = path.join(here, "data", "altgas.json");
const outputPath = path.join(here, "data", "altgas.face.json");
const osPath = path.resolve(here, "..", "arb-executor", "analysis", "window1_v54_dual_belief_os.js");
const legs = ["ALT", "GAS"];

const raw = JSON.parse(await fsp.readFile(dataPath, "utf8"));
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
  const actionName = derivation?.action?.action ?? null;
  const isRest = actionName === "PLACE_REST" || actionName === "REPRICE_REST";
  return {
    bid: stage?.books?.[leg]?.bid_cents ?? null,
    ask: stage?.books?.[leg]?.ask_cents ?? null,
    running_low: stage?.lows_travel?.[leg]?.observed_traded_low_cents ?? null,
    survivors: Array.isArray(survivorList) ? survivorList.length : null,
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
