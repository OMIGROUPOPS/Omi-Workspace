#!/usr/bin/env node
"use strict";

const { evaluateMicroPositionEvidence } = require("./window1_quote_shape_micro_position_v2.js");

function direction(shapeId) {
  if (String(shapeId).includes("_UP_")) return "UP";
  if (String(shapeId).includes("_DOWN_")) return "DOWN";
  if (String(shapeId).includes("_FLAT_")) return "FLAT";
  return "UNKNOWN";
}

function inverse(value) { return value === "UP" ? "DOWN" : value === "DOWN" ? "UP" : value; }

function structurallyCompatible(highShape, lowShape) {
  const high = direction(highShape), low = direction(lowShape);
  return high !== "UNKNOWN" && low !== "UNKNOWN" && inverse(high) === low;
}

// The empirical tuple table is sparse at pair grain. Keep every observed tuple,
// then add only inverse-compatible direction tuples from the two already-fitted
// marginal libraries. Generated rows carry n=0 and never masquerade as observed
// support. This repairs denominator coverage; it does not add a new shape.
function completePairTupleSupport({ observedTupleObject, highShapes, lowShapes }) {
  const map = new Map();
  for (const [key, count] of Object.entries(observedTupleObject || {})) {
    const [highShape, lowShape] = key.split("|");
    map.set(key, { highShape, lowShape, n: count, support_class: "EMPIRICALLY_OBSERVED_PAIR_TUPLE" });
  }
  for (const highShape of highShapes) for (const lowShape of lowShapes) {
    if (!structurallyCompatible(highShape, lowShape)) continue;
    const key = `${highShape}|${lowShape}`;
    if (!map.has(key)) map.set(key, { highShape, lowShape, n: 0, support_class: "STRUCTURAL_INVERSE_CLOSURE" });
  }
  return [...map.values()].sort((a, b) => `${a.highShape}|${a.lowShape}`.localeCompare(`${b.highShape}|${b.lowShape}`));
}

function ownMicroObserved(leg, dwellSeconds) {
  return evaluateMicroPositionEvidence({ leg, sibling: null, dwellSeconds }).own_micro_position_observed;
}

function evaluatePairWiringEvidence({ leg, sibling, dwellSeconds, survivingTuples, legRole }) {
  const base = evaluateMicroPositionEvidence({ leg, sibling, dwellSeconds });
  if (base.inverse_sibling_resolved) return { ...base, inverse_sibling_proof_type: "INDEPENDENT_SIBLING_DIRECTION" };
  if (!Array.isArray(survivingTuples) || survivingTuples.length !== 1) return { ...base, inverse_sibling_proof_type: null };
  const tuple = survivingTuples[0];
  const siblingRole = legRole === "highShape" ? "lowShape" : "highShape";
  const ownShape = tuple[legRole], siblingShape = tuple[siblingRole];
  const tupleIsInverse = structurallyCompatible(legRole === "highShape" ? ownShape : siblingShape, legRole === "highShape" ? siblingShape : ownShape);
  const ownDirectionMatches = leg?.resolved_direction && direction(ownShape) === leg.resolved_direction;
  const siblingShapeStillAlive = Array.isArray(sibling?.survivor_shapes) && sibling.survivor_shapes.includes(siblingShape);
  const siblingHasOwnMicroReceipt = ownMicroObserved(sibling, dwellSeconds);
  const tupleProof = Boolean(tupleIsInverse && ownDirectionMatches && siblingShapeStillAlive && siblingHasOwnMicroReceipt);
  return {
    ...base,
    inverse_sibling_resolved: tupleProof,
    inverse_sibling_proof_type: tupleProof ? "SINGLE_SURVIVING_INVERSE_PAIR_TUPLE_WITH_SIBLING_OWN_MICRO_RECEIPT" : null,
  };
}

module.exports = { completePairTupleSupport, evaluatePairWiringEvidence, direction, structurallyCompatible };
