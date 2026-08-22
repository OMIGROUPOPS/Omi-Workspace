"use strict";

// V54 clean-diet library materialization. A path-derived price is only exposed
// when the path has a filed, lawful right edge. UNBOUNDED is retained as data,
// but its path lows/highs/closes are deliberately unavailable to derivation.

function number(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function cent(value) {
  const parsed = number(value);
  return Number.isInteger(parsed) && parsed >= 1 && parsed <= 99 ? parsed : null;
}

function eventCode(eventId) {
  return String(eventId).match(/-(26[A-Z]{3}\d{2}[A-Z0-9]+)$/)?.[1] ?? null;
}

function median(values) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!rows.length) return null;
  const middle = Math.floor(rows.length / 2);
  return rows.length % 2 ? rows[middle] : (rows[middle - 1] + rows[middle]) / 2;
}

function buildAuthorities({ actualBellTable, namedNeighborCheck, bindings }) {
  const named = new Map();
  for (const [index, row] of (namedNeighborCheck?.neighbors ?? []).entries()) {
    named.set(row.neighbor, {
      ...row,
      receipt: `${bindings.analysis_commit}:${bindings.named_neighbor_path}#neighbors-${index + 1}`,
    });
  }
  return {
    actual_bells: actualBellTable ?? {},
    named,
    bindings,
  };
}

function resolveSpan(row, authorities) {
  if (row.edge_src === "official_actual" && Number.isFinite(number(row.right_edge))) {
    return {
      status: "BOUNDED",
      method: "OFFICIAL_ACTUAL_RANGE_SPECTRUM",
      right_edge_epoch: number(row.right_edge),
      inclusive: true,
      receipt: authorities.bindings.range_receipt,
    };
  }

  const code = eventCode(row.event);
  const filed = code ? authorities.actual_bells[code] : null;
  if (filed && Number.isFinite(number(filed.bell_epoch))) {
    const signature = filed.source === "TAPE_SIGNATURE";
    return {
      status: "BOUNDED",
      method: signature ? "IN_PLAY_SIGNATURE_ROW_RATE_MIRRORED_REPRICING" : "OFFICIAL_ACTUAL_MACHINE_RECEIPT",
      right_edge_epoch: number(filed.bell_epoch),
      inclusive: !signature,
      receipt: `${authorities.bindings.analysis_commit}:${authorities.bindings.actual_bell_path}#${code}`,
      filed_source: filed.source,
    };
  }

  const named = authorities.named.get(row.event);
  if (named && Number.isFinite(number(named.inplay_signature_epoch))) {
    return {
      status: "BOUNDED",
      method: "IN_PLAY_SIGNATURE_NAMED_NEIGHBOR_FVS050",
      right_edge_epoch: number(named.inplay_signature_epoch),
      inclusive: false,
      receipt: named.receipt,
    };
  }

  return {
    status: "UNBOUNDED",
    method: "UNBOUNDED",
    right_edge_epoch: null,
    inclusive: false,
    receipt: filed
      ? `${authorities.bindings.analysis_commit}:${authorities.bindings.actual_bell_path}#${code}`
      : authorities.bindings.range_receipt,
    reason: filed?.source === "BELL_UNRESOLVED"
      ? "FILED_BELL_UNRESOLVED"
      : "NO_OFFICIAL_ACTUAL_OR_FILED_IN_PLAY_SIGNATURE",
  };
}

function referencesInside(leg, span) {
  if (span.status !== "BOUNDED" || !Array.isArray(leg?.ticks)) return [];
  return leg.ticks
    .map((tick) => ({
      timestamp_epoch: number(tick?.[0]),
      bid_cents: cent(tick?.[1]),
      ask_cents: cent(tick?.[2]),
      reference_cents: cent(tick?.[3]),
    }))
    .filter((tick) => Number.isFinite(tick.timestamp_epoch)
      && Number.isInteger(tick.reference_cents)
      && (span.inclusive ? tick.timestamp_epoch <= span.right_edge_epoch : tick.timestamp_epoch < span.right_edge_epoch));
}

function rematerializeLeg(legId, leg, span) {
  const anchor = cent(leg?.anchor);
  const refs = referencesInside(leg, span);
  const prices = refs.map((row) => row.reference_cents);
  const low = prices.length ? prices.reduce((value, price) => Math.min(value, price), Infinity) : null;
  const floorEpoch = Number.isInteger(low)
    ? refs.find((row) => row.reference_cents === low)?.timestamp_epoch ?? null
    : null;
  const firstEpoch = refs[0]?.timestamp_epoch ?? null;
  const floorDuration = Number.isFinite(firstEpoch) && Number.isFinite(span.right_edge_epoch)
    ? span.right_edge_epoch - firstEpoch
    : null;
  const floorFraction = Number.isFinite(floorEpoch) && Number.isFinite(floorDuration) && floorDuration > 0
    ? Math.max(0, Math.min(1, (floorEpoch - firstEpoch) / floorDuration))
    : null;
  const spreads = refs
    .filter((row) => Number.isInteger(row.bid_cents) && Number.isInteger(row.ask_cents))
    .map((row) => row.ask_cents - row.bid_cents);
  return {
    leg_id: legId,
    anchor_cents: anchor,
    low_cents: low,
    floor_epoch: floorEpoch,
    floor_fraction: floorFraction,
    floor_timing_grain: "RANGE_POLL",
    floor_timing_basis: "FIRST_LAWFUL_REFERENCE_POLL_AT_REMATERIALIZED_LOW",
    floor_timing_receipt: Number.isFinite(floorEpoch) ? `${span.receipt}|${legId}@${floorEpoch}` : null,
    high_cents: prices.length ? prices.reduce((value, price) => Math.max(value, price), -Infinity) : null,
    close_cents: prices.length ? prices.at(-1) : null,
    net_cents: prices.length && Number.isInteger(anchor) ? prices.at(-1) - anchor : null,
    shape: leg?.shape ?? null,
    spread_median_cents: median(spreads),
    n_traded_polls: refs.length,
    source: leg?.source ?? null,
    span_status: span.status,
    span_method: span.method,
    span_right_edge_epoch: span.right_edge_epoch,
    span_receipt: span.receipt,
    original_low_cents: cent(leg?.low),
    original_close_cents: cent(leg?.close),
  };
}

function vectorFromLegs(category, legs, firstTick, span) {
  const travels = legs.map((leg) => Number.isFinite(leg.high_cents) && Number.isFinite(leg.low_cents) ? leg.high_cents - leg.low_cents : null);
  const inverse = Number.isFinite(legs[0]?.net_cents) && Number.isFinite(legs[1]?.net_cents)
    ? 1 - Math.abs(legs[0].net_cents + legs[1].net_cents) / (Math.abs(legs[0].net_cents) + Math.abs(legs[1].net_cents) + 1)
    : null;
  return {
    category,
    anchor_split_cents: Number.isFinite(legs[0]?.anchor_cents) && Number.isFinite(legs[1]?.anchor_cents) ? Math.abs(legs[0].anchor_cents - legs[1].anchor_cents) : null,
    leg0_anchor_cents: legs[0]?.anchor_cents ?? null,
    leg1_anchor_cents: legs[1]?.anchor_cents ?? null,
    leg0_drift_cents: legs[0]?.net_cents ?? null,
    leg1_drift_cents: legs[1]?.net_cents ?? null,
    leg0_travel_cents: travels[0],
    leg1_travel_cents: travels[1],
    joint_mid_sum_cents: Number.isFinite(legs[0]?.anchor_cents) && Number.isFinite(legs[1]?.anchor_cents) ? legs[0].anchor_cents + legs[1].anchor_cents : null,
    joint_spread_cents: Number.isFinite(legs[0]?.spread_median_cents) && Number.isFinite(legs[1]?.spread_median_cents) ? legs[0].spread_median_cents + legs[1].spread_median_cents : null,
    inverse_coherence: inverse,
    volume_log1p: Math.log1p((legs[0]?.n_traded_polls ?? 0) + (legs[1]?.n_traded_polls ?? 0)),
    hours_from_discovery: Number.isFinite(firstTick) && Number.isFinite(span.right_edge_epoch) ? (span.right_edge_epoch - firstTick) / 3600 : null,
    divot_depth_cents: Number.isFinite(legs[0]?.anchor_cents) && Number.isFinite(legs[0]?.low_cents) && Number.isFinite(legs[1]?.anchor_cents) && Number.isFinite(legs[1]?.low_cents)
      ? (Math.max(0, legs[0].anchor_cents - legs[0].low_cents) + Math.max(0, legs[1].anchor_cents - legs[1].low_cents)) / 2
      : null,
  };
}

function rematerializeRangeRow(row, authorities, rowRef) {
  const span = resolveSpan(row, authorities);
  const legs = Object.entries(row.legs ?? {})
    .map(([legId, leg]) => rematerializeLeg(legId, leg, span))
    .sort((a, b) => (a.anchor_cents ?? 50) - (b.anchor_cents ?? 50) || a.leg_id.localeCompare(b.leg_id));
  if (legs.length !== 2) return null;
  const firstTick = Object.values(row.legs ?? {}).reduce((minimum, leg) => Array.isArray(leg.ticks)
    ? leg.ticks.reduce((inner, tick) => Number.isFinite(number(tick?.[0])) ? Math.min(inner, number(tick[0])) : inner, minimum)
    : minimum, Infinity);
  const sourceReceipts = [rowRef, span.receipt].filter(Boolean);
  return {
    event_id: row.event,
    event_date: eventCode(row.event)?.slice(0, 5) ?? null,
    category: row.cat,
    quality: span.status === "BOUNDED" ? "RANGE_SPECTRUM_PATH_BELL_BOUNDED" : "RANGE_SPECTRUM_PATH_UNBOUNDED",
    span,
    legs,
    vector: vectorFromLegs(row.cat, legs, firstTick, span),
    source_receipts: [...new Set(sourceReceipts)].map((value) => typeof value === "string" ? { source_id: "BELL_BOUND_LIBRARY", row_ref: value } : value),
  };
}

function unboundedAggregate({ eventId, eventDate, category, legs, sourceReceipts, reason }) {
  const cleaned = legs.map((leg) => ({
    ...leg,
    low_cents: null,
    high_cents: null,
    close_cents: null,
    net_cents: null,
    span_status: "UNBOUNDED",
    span_method: "UNBOUNDED",
  }));
  return {
    event_id: eventId,
    event_date: eventDate,
    category,
    quality: "HISTORICAL_EVENT_AGGREGATE_UNBOUNDED",
    span: { status: "UNBOUNDED", method: "UNBOUNDED", right_edge_epoch: null, reason },
    legs: cleaned,
    vector: {
      category,
      anchor_split_cents: Number.isFinite(cleaned[0]?.anchor_cents) && Number.isFinite(cleaned[1]?.anchor_cents) ? Math.abs(cleaned[0].anchor_cents - cleaned[1].anchor_cents) : null,
      leg0_anchor_cents: cleaned[0]?.anchor_cents ?? null,
      leg1_anchor_cents: cleaned[1]?.anchor_cents ?? null,
      leg0_drift_cents: null,
      leg1_drift_cents: null,
      leg0_travel_cents: null,
      leg1_travel_cents: null,
      joint_mid_sum_cents: Number.isFinite(cleaned[0]?.anchor_cents) && Number.isFinite(cleaned[1]?.anchor_cents) ? cleaned[0].anchor_cents + cleaned[1].anchor_cents : null,
      joint_spread_cents: null,
      inverse_coherence: null,
      volume_log1p: null,
      hours_from_discovery: null,
      divot_depth_cents: null,
    },
    source_receipts: sourceReceipts,
  };
}

function buildReceipt(rows, authorities) {
  const byMethod = {}, byCategory = {};
  for (const row of rows) {
    const method = row.span?.method ?? "UNBOUNDED";
    byMethod[method] = (byMethod[method] ?? 0) + 1;
    byCategory[row.category] ??= {};
    byCategory[row.category][method] = (byCategory[row.category][method] ?? 0) + 1;
  }
  const namedCorrections = [];
  for (const named of authorities.named.values()) {
    const row = rows.find((candidate) => candidate.event_id === named.neighbor);
    if (!row) continue;
    const legs = {};
    for (const leg of row.legs) {
      const expected = named.legs?.[leg.leg_id]?.prebell_low_by_signature ?? null;
      if (row.span?.method === "IN_PLAY_SIGNATURE_NAMED_NEIGHBOR_FVS050" && Number.isFinite(expected) && leg.low_cents !== expected) throw new Error(`BELL_BOUND_NAMED_CORRECTION_MISMATCH ${row.event_id}|${leg.leg_id}|${leg.low_cents}|${expected}`);
      legs[leg.leg_id] = {
        before_low_cents: leg.original_low_cents,
        after_low_cents: leg.low_cents,
        correction_cents: Number.isInteger(leg.original_low_cents) && Number.isInteger(leg.low_cents) ? leg.low_cents - leg.original_low_cents : null,
        expected_after_cents: expected,
        verification: row.span?.method === "IN_PLAY_SIGNATURE_NAMED_NEIGHBOR_FVS050"
          ? "MATCHED_FILED_SIGNATURE_LOW"
          : row.span?.status === "BOUNDED" ? "BOUND_BY_STRONGER_NON_NAMED_METHOD" : "UNBOUNDED_NOT_SERVED",
      };
    }
    namedCorrections.push({ event_id: row.event_id, category: row.category, span: row.span, legs });
  }
  return {
    label: "LIBRARY_BELL_BOUND_RECEIPT",
    law: "F-VS-050_REPAIR",
    analysis_commit: authorities.bindings.analysis_commit,
    source_bindings: authorities.bindings,
    corpus_rows: rows.length,
    spans_by_method: byMethod,
    spans_by_method_category: byCategory,
    named_lajsva_danpra_neighbors_before_after: namedCorrections,
    unbounded_policy: "STAMP_RETAINED; PATH LOW/REACH/FLOOR FIELDS NULL; NEVER SILENTLY SERVED",
  };
}

module.exports = {
  eventCode,
  buildAuthorities,
  resolveSpan,
  rematerializeRangeRow,
  unboundedAggregate,
  buildReceipt,
};
