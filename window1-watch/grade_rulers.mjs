// Grading ruler only: apply every filed correction; never author an OS input.
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import { readPinnedTruth, recordedTruth } from "./recorded_truth.mjs";

export const CORRECTIONS_COMMIT = "15955e44faebf24a17c8c99eba6b8fb98a98a294";
export const CORRECTIONS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_CORRECTIONS.jsonl";
const hash = (b) => crypto.createHash("sha256").update(b).digest("hex");
const numeric = (v) => v != null && String(v).trim() !== "" && Number.isFinite(Number(v))
  ? Number(v) : null;

export function applyRulerDisplayClock(face, truth) {
  if (!Number.isFinite(truth?.bell_epoch)) return false;
  const delta = truth.bell_epoch - face.bell.timestamp_epoch;
  if (!delta) return false;
  face.trace_bell ??= { ...face.bell };
  face.bell = { ...face.bell, timestamp_epoch: truth.bell_epoch,
    t: face.bell.t + delta / 3600, source: truth.bell_source,
    role: "Corrected ruler display clock — trace_bell preserves the OS clock",
    corrections_commit: truth.corrections_commit };
  return true;
}

export function applyFiledCorrections(face, table, corrections) {
  const original = table.rows.find((r) => r.values.event_id === face.provenance.event_id);
  if (!original) return recordedTruth(face, table);
  const values = { ...original.values };
  for (const { value: c } of corrections) {
    for (const [key, v] of Object.entries(c.after ?? {})) {
      const side = ["legA", "legB"].find((s) => key === `${s}_${values[s]}`);
      if (side) {
        for (const [column, n] of Object.entries(v)) values[`${side}_${column}`] = n;
      } else if (v === null || typeof v !== "object") values[key] = v;
    }
  }
  const effectiveTable = { ...table, rows: [{ ...original, values }] };
  const truth = recordedTruth({ ...face, bell: { timestamp_epoch: numeric(values.bell_epoch) } }, effectiveTable);
  truth.bell_source = values.bell_source ?? null;
  truth.corrections_commit = CORRECTIONS_COMMIT;
  truth.applied_corrections = corrections.map(({ raw, value: c }) => ({
    correction_id: c.correction_id, row_sha256: hash(Buffer.from(raw)),
  }));
  truth.effective_row = values;
  truth.row_csv_role = "Original pinned row, before correction overlays";
  for (const { value: c } of corrections) {
    const offered = c.after?.offered_under_par;
    if (offered && (offered.floor_sum_c !== truth.pair.sum_cents || offered.margin_c !== truth.pair.discount_cents))
      throw new Error(`Filed denominator disagrees with corrected floors: ${c.correction_id}`);
  }
  return truth;
}

export function readGradeRulers(repo, event, face) {
  const table = readPinnedTruth(repo);
  const record = table.rows.find((r) => r.values.event_id === event);
  const row = record?.values;
  const bytes = execFileSync("git", ["show", `${CORRECTIONS_COMMIT}:${CORRECTIONS_PATH}`],
    { cwd: repo, maxBuffer: 8 * 1024 * 1024 });
  const corrections = bytes.toString("utf8").split(/\r?\n/).filter(Boolean)
    .map((raw) => ({ raw, value: JSON.parse(raw) }))
    .filter((r) => r.value.event_id === event);
  const legColumns = (source, corrected = false) => Object.fromEntries(
    ["legA", "legB"].filter((side) => row?.[side]).map((side) => {
      const leg = row[side], prefix = corrected ? `${side}_${leg}` : side;
      const data = corrected ? source[prefix] : source;
      const key = (name) => corrected ? name : `${side}_${name}`;
      const column = (name) => corrected ? `after.${prefix}.${name}` : key(name);
      return [leg, {
        floor_cents: numeric(data?.[key("floor_c")]),
        floor_epoch: numeric(data?.[key("floor_epoch")]),
        close_cents: numeric(data?.[key("close_c")]),
        source_columns: { floor_cents: column("floor_c"), floor_epoch: column("floor_epoch"), close_cents: column("close_c") },
      }];
    }),
  );
  const pair = (legs) => {
    const floors = Object.values(legs).map((l) => l.floor_cents);
    const sum = floors.length === 2 && floors.every((n) => n !== null)
      ? floors.reduce((a, b) => a + b, 0) : null;
    return { floor_sum_cents: sum, under_par_cents: sum === null ? null : 100 - sum };
  };
  const originalLegs = legColumns(row);
  return {
    role: "RULER COMPARISON ONLY — NOT AN OS INPUT",
    event_id: event,
    selection: "ALL FILED CORRECTIONS IN LEDGER ORDER — effective grading ruler; original rows retained",
    original_table: {
      commit: table.table_commit, path: table.table_path, sha256: table.table_sha256,
      row_sha256: record?.row_sha256 ?? null, row_number: record?.row_number ?? null,
      row_csv: record?.raw ?? null, values: row ?? null,
      status: row?.verified_span ?? "STORE SILENT",
      bell_epoch: numeric(row?.bell_epoch), bell_source: row?.bell_source ?? null,
      span_start_epoch: numeric(row?.span_start_epoch), span_end_epoch: numeric(row?.span_end_epoch),
      legs: originalLegs, ...pair(originalLegs),
      campaign_ruler_columns: Object.fromEntries(Object.entries(row ?? {}).filter(([k]) => /campaign|ruler/i.test(k))),
      column_note: "Pinned CSV uses legA_floor_c / legB_floor_c, not a literal floor_cents column; absent campaign/ruler columns are not invented.",
    },
    correction_source: { commit: CORRECTIONS_COMMIT, path: CORRECTIONS_PATH, sha256: hash(bytes) },
    restated_rows: corrections.map(({ raw, value: c }) => {
      const after = c.after ?? {}, legs = legColumns(after, true);
      return {
        correction_id: c.correction_id, row_sha256: hash(Buffer.from(raw)),
        row_jsonl: raw, original_correction: c,
        authority: c.authority, evidence: c.evidence,
        bell_epoch: after.bell_epoch ?? null, bell_source: after.bell_source ?? null,
        span_start_epoch: after.span_start_epoch ?? null, span_end_epoch: after.span_end_epoch ?? null,
        legs, ...pair(legs),
        offered_under_par: after.offered_under_par ?? null,
        campaign_ruler_fields: { game_ruler: after.game_ruler ?? null, leg_ruler: after.leg_ruler ?? null },
        campaign_source_columns: ["after.game_ruler", "after.leg_ruler"],
      };
    }),
    ...(face ? { effective_truth: applyFiledCorrections(face, table, corrections) } : {}),
  };
}
