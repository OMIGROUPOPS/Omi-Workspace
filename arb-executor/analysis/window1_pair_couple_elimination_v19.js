"use strict";

// A V19 pair hypothesis is an observed combination of two V13 interim
// single-leg hypotheses.  It may remove inconsistent leg hypotheses only when
// its exact couple, or its explicitly named structural parent, passed the
// July-6 hard-n/coherence law.  No signable couple means ABSTAIN, never veto.

function familyOf(shapeId) {
  const match = String(shapeId).match(/^(.+?)_(?:le25|26_50|51_75|ge76)_INTERIM_PATH_(\d+)(?:_ORD_.+)?$/);
  return match ? `${match[1]}|INTERIM_PATH_${match[2]}` : null;
}

function exactKey(highShape, lowShape) { return `${highShape}|${lowShape}`; }

function narrowBySignableCouples({ group, highShapes, lowShapes }) {
  if (!group) return { status: "PAIR_COUPLE_SOURCE_UNAVAILABLE_ABSTAIN", high_shapes: highShapes, low_shapes: lowShapes, couples: [], removed_high_shapes: [], removed_low_shapes: [] };
  const high = new Set(highShapes), low = new Set(lowShapes);
  const couples = (group.couples || []).filter((row) => row.usable_for_signing && high.has(row.high_shape_id) && low.has(row.low_shape_id));
  if (!couples.length) return { status: "NO_SIGNABLE_PAIR_COUPLE_ABSTAIN_TO_V11", high_shapes: highShapes, low_shapes: lowShapes, couples: [], removed_high_shapes: [], removed_low_shapes: [] };
  const allowedHigh = new Set(couples.map((row) => row.high_shape_id));
  const allowedLow = new Set(couples.map((row) => row.low_shape_id));
  const narrowedHigh = highShapes.filter((id) => allowedHigh.has(id));
  const narrowedLow = lowShapes.filter((id) => allowedLow.has(id));
  if (!narrowedHigh.length || !narrowedLow.length) return { status: "PAIR_COUPLE_CONTRADICTION_ABSTAIN_TO_V11", high_shapes: highShapes, low_shapes: lowShapes, couples: [], removed_high_shapes: [], removed_low_shapes: [] };
  return {
    status: "SIGNABLE_PAIR_COUPLES_NARROWED_BOTH_LEG_SETS",
    high_shapes: narrowedHigh,
    low_shapes: narrowedLow,
    couples,
    removed_high_shapes: highShapes.filter((id) => !allowedHigh.has(id)),
    removed_low_shapes: lowShapes.filter((id) => !allowedLow.has(id)),
  };
}

module.exports = { familyOf, exactKey, narrowBySignableCouples };
