// Hindsight ruler only. Never imported by the engine or used to author an OS field.
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";

export const TRUTH_COMMIT = "c0056976c446afcb4d9603796a2e06c068ee94d6";
export const TRUTH_PATH =
  ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.csv";
const RULER = "RULER — NOT AN OS INPUT";
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const number = (value) =>
  value != null && String(value).trim() !== "" && Number.isFinite(Number(value))
    ? Number(value)
    : null;

// Preserve the exact CSV record (without its record terminator) for its SHA256.
export function parseTruthCsv(text) {
  const records = [];
  let fields = [],
    field = "",
    quoted = false,
    start = 0;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') {
        field += '"';
        i++;
      } else quoted = !quoted;
    } else if (c === "," && !quoted) {
      fields.push(field);
      field = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      fields.push(field);
      if (text.slice(start, i).trim())
        records.push({ fields, raw: text.slice(start, i) });
      if (c === "\r" && text[i + 1] === "\n") i++;
      start = i + 1;
      fields = [];
      field = "";
    } else field += c;
  }
  if (quoted) throw new Error("Unterminated truth-table CSV quote");
  if (start < text.length)
    records.push({ fields: [...fields, field], raw: text.slice(start) });
  const header = records.shift()?.fields;
  if (!header?.includes("verified_span") || !header.includes("legA_floor_c"))
    throw new Error("Unexpected pinned truth-table schema");
  return records.map((r, i) => {
    if (r.fields.length !== header.length)
      throw new Error(`Truth-table record ${i + 2} has the wrong column count`);
    return {
      values: Object.fromEntries(header.map((h, j) => [h, r.fields[j]])),
      raw: r.raw,
      row_number: i + 2,
      row_sha256: hash(Buffer.from(r.raw, "utf8")),
    };
  });
}

export function readPinnedTruth(repoRoot) {
  const bytes = execFileSync("git", ["show", `${TRUTH_COMMIT}:${TRUTH_PATH}`], {
    cwd: repoRoot,
    maxBuffer: 8 * 1024 * 1024,
  });
  return {
    table_commit: TRUTH_COMMIT,
    table_path: TRUTH_PATH,
    table_sha256: hash(bytes),
    rows: parseTruthCsv(bytes.toString("utf8")),
  };
}

export function recordedTruth(face, table) {
  const event = face.provenance.event_id;
  const matches = table.rows.filter((r) => r.values.event_id === event);
  if (matches.length > 1)
    throw new Error(`Duplicate truth-table rows for ${event}`);
  const selected = matches[0],
    row = selected?.values;
  const reason = !row
    ? "NO ROW IN PINNED TABLE"
    : row.verified_span !== "OK"
      ? row.verified_span || "UNKNOWN"
      : null;
  const bell = number(face.bell.timestamp_epoch);
  const tableBell = number(row?.bell_epoch);
  const truth = {
    role: RULER,
    event_id: event,
    table_commit: table.table_commit,
    table_path: table.table_path,
    table_sha256: table.table_sha256,
    row_sha256: selected?.row_sha256 ?? null,
    row_number: selected?.row_number ?? null,
    row_csv: selected?.raw ?? null,
    verified_span: row?.verified_span ?? null,
    status: reason ? "STORE_SILENT" : "OK",
    reason,
    span_start_epoch: number(row?.span_start_epoch),
    span_end_epoch: number(row?.span_end_epoch),
    bell_epoch: bell,
    bell_source: "face.bell.timestamp_epoch",
    table_bell_epoch: tableBell,
    table_bell_source: row?.bell_source ?? null,
    table_bell_delta_seconds:
      bell != null && tableBell != null ? tableBell - bell : null,
    legs: {},
    favorite_leg: null,
    underdog_leg: null,
    pair: null,
  };
  for (const leg of face.legs) {
    const column =
      row?.legA === leg ? "legA" : row?.legB === leg ? "legB" : null;
    let silent = reason ?? (!column ? "LEG NOT IN PINNED ROW" : null);
    const floor = number(row?.[`${column}_floor_c`]),
      epoch = number(row?.[`${column}_floor_epoch`]);
    if (!silent && (floor == null || epoch == null))
      silent = `NO RECORDED FLOOR: ${row?.[`${column}_journey`] || "UNKNOWN"}`;
    if (
      !silent &&
      (truth.span_start_epoch == null || truth.span_end_epoch == null)
    )
      silent = "UNKNOWN VERIFIED SPAN BOUNDS";
    if (
      !silent &&
      (epoch < truth.span_start_epoch || epoch > truth.span_end_epoch)
    )
      silent = "FLOOR OUTSIDE VERIFIED SPAN";
    if (!silent && bell == null) silent = "UNKNOWN GAME BELL";
    const minutes = silent ? null : (bell - epoch) / 60;
    truth.legs[leg] = {
      status: silent ? "STORE_SILENT" : "OK",
      reason: silent,
      source_columns: column
        ? {
            floor_cents: `${column}_floor_c`,
            floor_epoch: `${column}_floor_epoch`,
            anchor_cents: `${column}_open_postformation_c`,
          }
        : null,
      anchor_cents: number(row?.[`${column}_open_postformation_c`]),
      floor_cents: silent ? null : floor,
      floor_epoch: silent ? null : epoch,
      minutes_to_bell: minutes,
      line: silent
        ? `${leg}: STORE SILENT — ${silent}`
        : `${leg} ${floor}¢ @ ${minutes.toFixed(2)}m to bell`,
      marker_label: silent
        ? null
        : `${leg} FLOOR · RECORDED ${floor}¢ @ ${minutes.toFixed(2)}m to bell — ${RULER}`,
      markers: {},
    };
  }
  const anchored = face.legs
    .filter((l) => truth.legs[l].anchor_cents != null)
    .sort((a, b) => truth.legs[b].anchor_cents - truth.legs[a].anchor_cents);
  if (
    anchored.length === 2 &&
    truth.legs[anchored[0]].anchor_cents !==
      truth.legs[anchored[1]].anchor_cents
  )
    [truth.favorite_leg, truth.underdog_leg] = anchored;
  const pairReason =
    reason ??
    (face.legs.find((l) => truth.legs[l].reason)
      ? "MISSING VERIFIED FLOOR ON A SIDE"
      : !truth.favorite_leg
        ? "FAVORITE/UNDERDOG NOT IDENTIFIABLE FROM TABLE OPENS"
        : null);
  if (pairReason)
    truth.pair = {
      sum_cents: null,
      discount_cents: null,
      reason: pairReason,
      line: `best capturable = STORE SILENT — ${pairReason}`,
      discount_line: "STORE SILENT",
    };
  else {
    const fav = truth.legs[truth.favorite_leg].floor_cents,
      dog = truth.legs[truth.underdog_leg].floor_cents,
      sum = fav + dog;
    truth.pair = {
      sum_cents: sum,
      discount_cents: 100 - sum,
      reason: null,
      line: `best capturable = ${fav} + ${dog} = ${sum}¢`,
      discount_line: `${100 - sum}¢ under par`,
    };
  }
  return truth;
}

export function attachRecordedTruth(face, table) {
  face.truth = recordedTruth(face, table);
  if (!face.render) return face.truth;
  for (const [name, axis, priceField] of [
    ["play", face.render.axis, "plot_price"],
    ["inspection", face.render.inspection_axis, "inspection_price"],
  ]) {
    // Display bounds alone may expand to include a ruler; no tape/OS value changes.
    const floors = Object.values(face.truth.legs)
      .filter((l) => l.status === "OK")
      .map((l) => l.floor_cents);
    if (!axis?.price_domain || !floors.length) continue;
    axis.price_domain = [
      Math.min(...axis.price_domain, ...floors),
      Math.max(...axis.price_domain, ...floors),
    ];
    const [low, high] = axis.price_domain;
    for (const leg of Object.values(face.truth.legs)) {
      if (leg.status !== "OK") continue;
      const progress =
        (axis.start_minutes_to_bell - leg.minutes_to_bell) /
        (axis.start_minutes_to_bell - axis.end_minutes_to_bell);
      const boundary =
        progress < 0 ? "BEFORE_AXIS" : progress > 1 ? "AFTER_AXIS" : null;
      leg.markers[name] = {
        progress,
        display_progress: Math.max(0, Math.min(1, progress)),
        boundary,
        glyph:
          boundary === "BEFORE_AXIS"
            ? "◀⚑"
            : boundary === "AFTER_AXIS"
              ? "⚑▶"
              : "⚑",
        label: `${leg.marker_label}${boundary ? ` · ${boundary} (edge flag; original time unchanged)` : ""}`,
        price: high === low ? 0.5 : (high - leg.floor_cents) / (high - low),
      };
    }
    for (const fill of face.render.fill_events)
      fill[priceField] =
        high === low ? 0.5 : (high - fill.cents) / (high - low);
  }
  return face.truth;
}
