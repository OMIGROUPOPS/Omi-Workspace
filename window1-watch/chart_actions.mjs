// Display-only projection of stored receipts. No engine import and no price authoring.
import fs from "node:fs/promises";
import path from "node:path";
import zlib from "node:zlib";
import { plainCard, cardGloss, attachPoolAccuracy } from "./plain_cards.mjs";

const SILENT = "STORE SILENT";
const finite = (v) => typeof v === "number" && Number.isFinite(v);
const value = (v) => (v == null ? SILENT : String(v));
const cents = (v) => (finite(v) ? `${v}¢` : SILENT);
const rest = (v) => (v === null ? "none" : cents(v));
const minutes = (v) => (finite(v) ? `${Number(v.toFixed(2))}m` : SILENT);
export function tokenGloss(token) {
  return cardGloss(token) ?? SILENT;
}
const tokenLine = (label, token) =>
  `${label}: ${value(token)} · ${tokenGloss(token)}`;
export function sentenceLines(sentence) {
  return [
    `status ${value(sentence?.status)} · P ${cents(sentence?.P)} · Q ${cents(sentence?.Q)} · X ${cents(sentence?.X)}`,
    `q_author ${value(sentence?.q_author)} · x_author ${value(sentence?.x_author)}`,
    value(sentence?.plain_sentence),
  ];
}

// Take only the fields needed by the display; an envelope can contain a whole library.
export function chartSource(row) {
  return {
    receipt: row.receipt ?? row.fill_event_receipt?.captured_at_receipt ?? null,
    timestamp_epoch:
      row.timestamp_epoch ??
      row.fill_event_receipt?.context?.fill_timestamp_epoch ??
      null,
    books: row.reads?.books?.value ?? null,
    deadlines: Object.fromEntries(
      Object.entries(row.layers?.micro?.context?.beliefs ?? {}).map(
        ([leg, b]) => [
          leg,
          {
            deadline: b.deadline ?? null,
            predicted_minutes_to_bell: b.predicted_minutes_to_bell ?? null,
          },
        ],
      ),
    ),
    standing: Object.fromEntries(
      Object.entries(row.reads?.half_pair_state?.value?.legs ?? {}).map(
        ([leg, s]) => [
          leg,
          {
            standing_target_cents: s.standing_target_cents,
            credited: s.credited,
          },
        ],
      ),
    ),
    derivations: (row.derivations ?? []).map((d) => ({
      leg: d.leg_id,
      action: d.action ?? null,
      winner_lane:
        d.layered_dual_belief?.decision_arbitration?.winner?.lane ?? null,
      envelope_mode: d.layered_dual_belief?.envelope_placement?.mode ?? null,
      active_target_before_cents:
        d.layered_dual_belief?.envelope_placement?.active_target_before_cents,
    })),
    fill: row.fill_event_receipt?.context ?? null,
  };
}

export async function readChartSources(face, here) {
  const sources = new Map();
  for (const r of face.os) {
    if (!["DECISION_STAGE", "FILL_EVENT"].includes(r.kind)) continue;
    if (!r.detail_url)
      throw new Error(`Missing stored receipt for ${r.receipt}`);
    const file = path.resolve(here, "." + r.detail_url + ".gz");
    if (!file.startsWith(path.resolve(here, "data") + path.sep))
      throw new Error("Receipt outside face data");
    const detail = JSON.parse(zlib.gunzipSync(await fs.readFile(file)));
    if (
      detail.source.event_id !== face.provenance.event_id ||
      detail.source.trace_row !== r.trace_row
    )
      throw new Error(`Receipt source mismatch: ${file}`);
    sources.set(r.trace_row, chartSource(detail.row));
  }
  return sources;
}

function geometry(axis, mtb, level) {
  const progress =
    (axis.start_minutes_to_bell - mtb) /
    (axis.start_minutes_to_bell - axis.end_minutes_to_bell);
  const [low, high] = axis.price_domain ?? [];
  const boundary =
    progress < 0 ? "BEFORE_AXIS" : progress > 1 ? "AFTER_AXIS" : null;
  return {
    progress,
    display_progress: Math.max(0, Math.min(1, progress)),
    boundary,
    price:
      finite(level) && finite(low) && finite(high)
        ? high === low
          ? 0.5
          : (high - level) / (high - low)
        : null,
  };
}

export function attachChartActions(face, sources) {
  const events = [],
    active = {},
    places = {};
  const add = (r, leg, src, d, old, next, kind, observation = null) => {
    const sentence = r.legs[leg]?.sentence ?? null;
    const book = src.books?.[leg] ?? null;
    const marker = kind === "FILL" ? "●" : "▪";
    const level = kind === "REMOVE" || kind === "FILL" ? old : next;
    const raw = {
      action: kind === "FILL" ? r.kind : (d?.action?.action ?? null),
      reason: d?.action?.reason ?? null,
      winner_lane: d?.winner_lane ?? null,
      envelope_mode: d?.envelope_mode ?? null,
    };
    const item = {
      id: `${r.receipt_id}:${leg}:${events.length}`,
      leg,
      kind,
      glyph: marker,
      receipt: r.receipt,
      receipt_id: r.receipt_id,
      receipt_index: r.index,
      trace_row: r.trace_row,
      detail_url: r.detail_url,
      t: r.t,
      timestamp_epoch: src.timestamp_epoch,
      minutes_to_bell: r.minutesToBell,
      old_cents: old ?? null,
      new_cents: next ?? null,
      marker_cents: level ?? null,
      old_known: old !== undefined,
      new_known: next !== undefined,
      raw,
      observation,
      sentence,
      deadline: src.deadlines?.[leg] ?? null,
      book,
      gloss: Object.fromEntries(
        Object.entries(raw).map(([k, v]) => [k, tokenGloss(v)]),
      ),
      label: `${leg} ${value(raw.action)} · ${rest(old)} → ${rest(next)} · ${minutes(r.minutesToBell)} to bell`,
      hover_lines: [
        `${leg} · ${minutes(r.minutesToBell)} to bell · ${value(raw.action)} · ${rest(old)} → ${rest(next)}`,
        tokenLine("winner.lane", raw.winner_lane),
        tokenLine("envelope mode", raw.envelope_mode),
        tokenLine("action.reason", raw.reason),
        `book bid ${cents(book?.bid_cents)} / ask ${cents(book?.ask_cents)} / last ${cents(book?.last_trade_cents)}`,
        ...sentenceLines(sentence),
        ...(observation ? [observation] : []),
      ],
      markers: {
        play: geometry(face.render.axis, r.minutesToBell, level),
        inspection: geometry(
          face.render.inspection_axis,
          r.minutesToBell,
          level,
        ),
      },
    };
    for (const g of Object.values(item.markers))
      g.label = `${item.label}${g.boundary ? ` · ${g.boundary} (edge marker; original time unchanged)` : ""}`;
    events.push(item);
    return item;
  };
  for (const r of face.os) {
    const src = sources.get(r.trace_row);
    if (!src) continue;
    if (r.kind === "FILL_EVENT") {
      const fill = src.fill,
        leg = fill?.leg_id;
      if (!face.legs.includes(leg)) continue;
      const old = fill.prior_standing_target_cents ?? active[leg];
      const item = add(r, leg, src, null, old, null, "FILL");
      // A fill row has no decision or book: don't relabel the placing decision as its own.
      const place = places[leg] ?? null;
      const age =
        place &&
        finite(fill.fill_timestamp_epoch) &&
        finite(place.timestamp_epoch)
          ? (fill.fill_timestamp_epoch - place.timestamp_epoch) / 60
          : null;
      const floor = face.truth?.legs[leg]?.floor_cents ?? null;
      const delta =
        finite(fill.entry_cents) && finite(floor)
          ? fill.entry_cents - floor
          : null;
      item.fill = {
        cents: fill.entry_cents ?? null,
        triggering_print_cents: fill.triggering_print_price_cents ?? null,
        context: fill,
        place_receipt: place?.receipt ?? null,
        place_receipt_id: place?.receipt_id ?? null,
        place_timestamp_epoch: place?.timestamp_epoch ?? null,
        placing_sentence: place?.sentence ?? null,
        placing_deadline: place?.deadline ?? null,
        placing_sentence_lines: sentenceLines(place?.sentence),
        rest_age_minutes: age != null && age >= 0 ? age : null,
        recorded_floor_cents: floor,
        floor_difference_cents: delta,
        floor_line:
          delta == null
            ? SILENT
            : `${Math.abs(delta)}¢ ${delta < 0 ? "below" : "above"} floor ${floor}¢`,
        summary: `${leg} filled ${cents(fill.entry_cents)} · ${minutes(r.minutesToBell)} to bell · print ${cents(fill.triggering_print_price_cents)} · rest had stood ${minutes(age != null && age >= 0 ? age : null)}`,
      };
      item.hover_lines.push(item.fill.summary, item.fill.floor_line);
      active[leg] = null;
      places[leg] = null;
      continue;
    }
    for (const leg of face.legs) {
      const d = src.derivations.find((d) => d.leg === leg);
      const state = src.standing[leg];
      // A credited disappearance is represented by its separate FILL_EVENT, not a second cancel.
      if (state?.credited) continue;
      const hasState = state && Object.hasOwn(state, "standing_target_cents");
      const old = hasState
        ? state.standing_target_cents
        : d &&
            Object.hasOwn(d, "active_target_before_cents") &&
            d.active_target_before_cents !== undefined
          ? d.active_target_before_cents
          : active[leg];
      if (hasState && old === null && finite(active[leg])) {
        add(
          r,
          leg,
          src,
          null,
          active[leg],
          null,
          "REMOVE",
          "reads.half_pair_state.value.legs: standing target became null; action.reason STORE SILENT",
        );
        places[leg] = null;
      }
      active[leg] = old;
      if (!d?.action) continue;
      const action = d.action.action,
        target = d.action.target_cents;
      if (
        ["PLACE_REST", "REPRICE_REST"].includes(action) ||
        (action === "HOLD_REST" && finite(target) && target !== old)
      ) {
        const item = add(
          r,
          leg,
          src,
          d,
          old,
          target,
          action === "PLACE_REST" ? "PLACE" : "REPRICE",
        );
        if (action === "PLACE_REST") places[leg] = item;
        active[leg] = target;
      } else if (/CANCEL|STAND_DOWN|PULL_REST/.test(action) && finite(old)) {
        add(r, leg, src, d, old, null, "REMOVE");
        active[leg] = null;
        places[leg] = null;
      }
    }
  }
  // Identical-time/price receipts retain individual hit targets around the exact anchor.
  const stacks = new Map();
  for (const event of events) {
    event.card_lines = plainCard(event);
    event.details_lines = [
      ...event.hover_lines,
      `deadline: ${JSON.stringify(event.deadline)}`,
      ...(event.fill
        ? [
            ...event.fill.placing_sentence_lines,
            `placing deadline: ${JSON.stringify(event.fill.placing_deadline)}`,
          ]
        : []),
      ...Object.entries(event.raw).map(
        ([field, token]) =>
          `${field}: ${token ?? "STORE SILENT"} · ${cardGloss(token) ?? "not translated yet"}`,
      ),
    ];
    const key = JSON.stringify([
      event.leg,
      event.minutes_to_bell,
      event.marker_cents,
    ]);
    const ordinal = stacks.get(key) ?? 0;
    event.stack_offset_px = ordinal * 18;
    stacks.set(key, ordinal + 1);
  }
  face.render.bid_actions = events;
  face.render.marker_legend = "▪ bid action · ● fill · ⚑ recorded floor";
  attachPoolAccuracy(face);
  // All chart hover strings are written here, never composed from prices in React.
  let hoverIndex = face.render.columns.indexOf("hover_lines");
  if (hoverIndex < 0) hoverIndex = face.render.columns.push("hover_lines") - 1;
  for (const tick of face.render.ticks) {
    const f = Object.fromEntries(
      face.render.columns.map((key, i) => [key, tick[i]]),
    );
    tick[hoverIndex] = [
      f.clock_label,
      ...face.legs.map((leg, i) => {
        const prefix = i ? "second" : "first";
        return `${leg} book bid ${cents(f[prefix + "Bid"])} / ask ${cents(f[prefix + "Ask"])} · last ${cents(f[prefix + "Last"])}`;
      }),
    ];
  }
  return events;
}
