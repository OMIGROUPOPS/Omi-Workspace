// Hindsight face ruler. This module is never imported by the OS or replay builder.
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";

const SILENT = "STORE SILENT";
const finite = Number.isFinite;
const fmt = n => finite(n) ? Number(n.toFixed(2)).toString() : SILENT;
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");

// Strictly later means timestamp > receipt, not carried last and not the triggering print.
export function remainingFloors(prints, epochs, start, end, bell) {
  const accepted = prints.filter(p => p.epoch >= start && p.epoch <= end && p.epoch < bell)
    .sort((a, b) => a.epoch - b.epoch);
  const suffix = new Array(accepted.length);
  let minimum = null;
  for (let i = accepted.length - 1; i >= 0; i--) {
    if (minimum == null || accepted[i].price < minimum) minimum = accepted[i].price;
    suffix[i] = minimum;
  }
  let cursor = 0;
  return epochs.map(t => {
    while (cursor < accepted.length && accepted[cursor].epoch <= t) cursor++;
    return t < start || t > end || t >= bell ? null : suffix[cursor] ?? null;
  });
}

export function buildOraclePath(face, { prints, bookReceipts, bookSources = [], accountability = [] }) {
  const truth = face.rulers?.effective_truth ?? face.truth;
  const bell = truth?.bell_epoch, start = truth?.span_start_epoch, end = truth?.span_end_epoch;
  const first = face.first_tick?.epoch;
  const reason = truth?.status !== "OK" ? truth?.reason ?? "NO VERIFIED SPAN"
    : ![first, bell, start, end].every(finite) ? "UNKNOWN SPAN OR FIRST TICK" : null;
  const base = { role: "RULER — NOT AN OS INPUT", label: "perfect sentence", reason,
    status: reason ? "STORE_SILENT" : "OK", provenance: {
      prints: prints.provenance, books: bookSources, os_sha256: face.provenance.os_sha256,
      trace_sha256: face.provenance.trace_sha256, truth_commit: truth?.table_commit,
      truth_row_sha256: truth?.row_sha256, corrections_commit: truth?.corrections_commit,
      span_start_epoch: start, span_end_epoch: end, bell_epoch: bell, first_tick_epoch: first,
    }, rules: {
      floor: "Minimum strictly later accepted positive-size true prints; corrected span inclusive, bell exclusive. Equal-time/triggering prints are excluded. No book-last, carried floor, interpolation or table floor substitutes. No future print => STORE SILENT.",
      receipts: "Every custody book row (including unchanged prices), every print receipt (including non-witness zero-size rows), plus trace receipts. Identity deduplicated; recorded trace/renewal timestamp takes priority over book second. Synthetic first-tick/bell endpoints are drawing only, never mean denominators.",
      sentence: "Most recent stored decision at or before each receipt; null Q stays null. No post-fill new sentence is invented. Layer and ESS are the author, not STEP telemetry. Renewal is exact-tick only; absent is STORE SILENT.",
      summary: "Receipt-weighted mean absolute gap from first tick through corrected bell, only finite Q and future floor; not time-weighted. At fill is the signed gap at that fill receipt with strictly later prints (not the filling print). Widest is maximum absolute gap, earliest receipt breaks ties. Full-run hindsight, not a live score.",
    }, legs: {} };
  if (reason) {
    for (const leg of face.legs) base.legs[leg] = { hud_line: `${leg} GAP: ${SILENT} — ${reason}` };
    return { summary: base, detail: null };
  }
  const firstEpoch = face.bell.timestamp_epoch - face.bell.t * 3600;
  const rows = face.os.map(r => ({ ...r, epoch: firstEpoch + r.t * 3600 }));
  const decisions = rows.filter(r => r.kind === "DECISION_STAGE").sort((a, b) => a.epoch - b.epoch || a.index - b.index);
  const identities = new Map();
  for (const r of [...bookReceipts, ...(prints.receipts ?? [])]) identities.set(r.receipt, { ...r });
  for (const r of accountability.filter(r => r.kind === "BID_RENEWAL" && r.phase === "TICK"))
    identities.set(r.tick_receipt, { epoch: r.timestamp_epoch, receipt: r.tick_receipt, kind: r.tick_kind });
  for (const r of rows) if (r.receipt) identities.set(r.receipt, { epoch: r.epoch, receipt: r.receipt, kind: r.kind });
  const timeline = [...identities.values()].filter(r => r.epoch >= first && r.epoch <= bell)
    .sort((a, b) => a.epoch - b.epoch || a.receipt.localeCompare(b.receipt));
  const epochs = timeline.map(r => r.epoch);
  const inspectionStart = face.render.inspection_axis.start_minutes_to_bell;
  const renewals = new Map(accountability.filter(r => r.kind === "BID_RENEWAL" && r.phase === "TICK")
    .map(r => [`${r.tick_receipt}|${r.leg_id}`, r.status]));
  const selected = [];
  let decisionCursor = -1;
  for (const t of epochs) {
    while (decisionCursor + 1 < decisions.length && decisions[decisionCursor + 1].epoch <= t) decisionCursor++;
    selected.push(decisions[decisionCursor] ?? null);
  }
  const detail = { role: base.role, provenance: base.provenance,
    columns: ["epoch", "minutesToBell", "progress", "inspection_progress", "receipt", "clock_label", "receipt_index"],
    ticks: timeline.map((r, i) => { const mtb = (bell - r.epoch) / 60; return [r.epoch, mtb,
      (r.epoch - first) / (bell - first), 1 - mtb / inspectionStart, r.receipt,
      `${fmt(mtb)}m to bell`, selected[i]?.index ?? null]; }),
    value_columns: ["profile", "gap", "bar_y", "bar_height"], legs: {} };
  for (const leg of face.legs) {
    const floors = remainingFloors(prints.legs[leg] ?? [], epochs, start, end, bell);
    const values = [], profiles = [], profileMap = new Map();
    const gaps = [];
    const fills = rows.filter(r => finite(r.legs?.[leg]?.fill?.cents) && r.epoch >= start && r.epoch <= end && r.epoch < bell);
    for (let i = 0; i < timeline.length; i++) {
      const state = selected[i]?.legs?.[leg], sentence = state?.sentence;
      const q = finite(sentence?.Q) ? sentence.Q : null, floor = floors[i];
      const gap = q != null && floor != null ? q - floor : null;
      const layer = state?.pool_cascade?.selected_layer ?? sentence?.authority_source ?? sentence?.q_author ?? null;
      const ess = state?.pool_cascade?.layers?.[layer]?.ess ?? null;
      const renewal = renewals.get(`${timeline[i].receipt}|${leg}`) ?? null;
      const profile = { Q: q, perfect: floor, gap, layer, ess, renewal_status: renewal,
        lines: [`Q ${fmt(q)}¢ · perfect ${fmt(floor)}¢ · gap ${gap > 0 ? "+" : ""}${fmt(gap)}¢`,
          `layer ${layer ?? SILENT} · ESS ${fmt(ess)}`, `renewal ${renewal ?? SILENT}`] };
      const key = JSON.stringify(profile);
      if (!profileMap.has(key)) { profileMap.set(key, profiles.length); profiles.push(profile); }
      values.push([profileMap.get(key), gap]);
      if (gap != null) gaps.push({ gap, index: i });
    }
    const widest = gaps.reduce((best, r) => !best || Math.abs(r.gap) > Math.abs(best.gap) ? r : best, null);
    const extent = widest ? Math.abs(widest.gap) : 0;
    for (const v of values) v.push(v[1] == null || !extent ? null : (extent - Math.max(0, v[1])) / (extent * 2),
      v[1] == null || !extent ? null : Math.abs(v[1]) / (extent * 2));
    const mean = gaps.length ? gaps.reduce((n, r) => n + Math.abs(r.gap), 0) / gaps.length : null;
    const fillPoints = fills.map(fill => {
      const index = timeline.findIndex(t => t.receipt === fill.receipt);
      const v = values[index], p = profiles[v?.[0]];
      return { receipt: fill.receipt, index, cents: fill.legs[leg].fill.cents,
        gap: p?.gap ?? null, progress: detail.ticks[index]?.[2], inspection_progress: detail.ticks[index]?.[3],
        y: p?.gap != null ? extent ? (extent - p.gap) / (extent * 2) : 0.5 : null,
        label: `${leg} fill ${fill.legs[leg].fill.cents}¢ · gap ${fmt(p?.gap)}¢ · ${detail.ticks[index]?.[5] ?? SILENT}` };
    });
    const path = [];
    // Lossless changes only for drawing; the receipt table above is never downsampled.
    for (let i = 0; i < timeline.length; i++) {
      if (i > 0 && floors[i] == null && floors[i - 1] != null)
        path.push({ minutesToBell: detail.ticks[i][1], perfect: floors[i - 1] });
      if (i === 0 || floors[i] !== floors[i - 1]) path.push({ minutesToBell: detail.ticks[i][1], perfect: floors[i] });
    }
    path.push({ minutesToBell: 0, perfect: null });
    const widestMtb = widest ? detail.ticks[widest.index][1] : null;
    base.legs[leg] = { mean_absolute_gap_cents: mean, at_fill_gap_cents: fillPoints[0]?.gap ?? null,
      widest_absolute_gap_cents: widest ? extent : null, widest_signed_gap_cents: widest?.gap ?? null,
      widest_minutes_to_bell: widestMtb, receipt_count: timeline.length, comparable_receipts: gaps.length,
      missing_q_receipts: values.filter(v => profiles[v[0]].Q == null).length,
      no_future_print_receipts: floors.filter(f => f == null).length,
      hud_line: `${leg} GAP: mean |Q − floor| from first tick ${fmt(mean)}¢ · at fill ${fmt(fillPoints[0]?.gap)}¢ · widest ${fmt(widest ? extent : null)}¢ at ${fmt(widestMtb)}m`,
      path, fill_points: fillPoints, extent };
    detail.legs[leg] = { profiles, values };
  }
  return { summary: base, detail };
}

export async function attachOraclePath(face, input) {
  const { summary, detail } = buildOraclePath(face, input);
  if (detail) {
    const name = `${face.provenance.event_id}.oracle.json`;
    const payload = Buffer.from(JSON.stringify(detail));
    await fs.writeFile(path.join(input.dataRoot, name + ".gz"), zlib.gzipSync(payload));
    Object.assign(summary, { detail_url: `/data/${name}`, sha256_uncompressed: sha(payload) });
  }
  face.oracle = summary;
}
