"use strict";

const DWELL_SECONDS = 10;
const QUANTITY = 5;

function integer(name, value) {
  if (!Number.isInteger(value)) throw new Error(`${name} must be an integer`);
  return value;
}

function qualifiedAsk(row) {
  return Boolean(
    row
    && Number.isInteger(row.bid)
    && Number.isInteger(row.ask)
    && row.bid < row.ask
    && Number.isFinite(row.ask_dwell_seconds)
    && row.ask_dwell_seconds >= DWELL_SECONDS
    && Number.isFinite(row.top_ask_size)
    && row.top_ask_size >= QUANTITY
  );
}

function findAnchorRearm(rows, { afterTs, afterReceipt }) {
  if (!Number.isFinite(afterTs)) throw new Error("afterTs must be finite");
  return rows.find((row) => (
    row.ts > afterTs
    && row.receipt !== afterReceipt
    && qualifiedAsk(row)
  )) || null;
}

function findCapRearm(rows, { afterTs, capCents }) {
  if (!Number.isFinite(afterTs)) throw new Error("afterTs must be finite");
  integer("capCents", capCents);
  return rows.find((row) => (
    row.ts > afterTs
    && qualifiedAsk(row)
    && row.spread === 1
    && row.ask <= capCents
    && row.bid <= capCents
  )) || null;
}

function unfalsifiableLowerReceipt(snapshot) {
  if (!snapshot || snapshot.reason !== "ALL_SURVIVING_SHAPES_SAY_LOWER") return { touched: false, placeable: false, reason: "NOT_UNANIMOUS_LOWER" };
  const verdicts = snapshot.shape_verdicts || [];
  const allZero = verdicts.length > 0 && verdicts.every((verdict) => {
    if (verdict.verdict !== "LOWER") return false;
    const distribution = verdict.fitted_descent_distribution;
    const keys = Object.keys(distribution?.counts || {});
    return keys.length > 0 && keys.every((key) => Number(key) === 0);
  });
  if (!allZero) return { touched: false, placeable: false, reason: "DESCENT_SUPPORT_CAN_FALSIFY_LOWER" };
  const p = snapshot.predicates || {};
  const qualified = Boolean(
    p.current_ask_at_observed_low
    && p.ask_dwell_at_least_10_seconds
    && p.top_ask_capacity_at_least_five
    && p.fresh_own_book_receipt
  );
  if (!qualified) return { touched: true, placeable: false, reason: "SUSTAINED_QUALIFIED_DWELL_NOT_ESTABLISHED" };
  if (!p.own_micro_position_observed) return { touched: true, placeable: false, reason: "OWN_MICRO_POSITION_UNRESOLVED" };
  if (!p.inverse_sibling_resolved) return { touched: true, placeable: false, reason: "INVERSE_SIBLING_UNRESOLVED" };
  return {
    touched: true,
    placeable: true,
    reason: "UNFALSIFIABLE_LOWER_SETTLED_BY_SUSTAINED_QUALIFIED_DWELL_AT_OBSERVED_LOW",
  };
}

function findAdmissionReask(rows, { leftTs, rightTs }) {
  if (!Number.isFinite(leftTs) || !Number.isFinite(rightTs) || leftTs >= rightTs) throw new Error("invalid admission window");
  return rows.find((row) => row.ts >= leftTs && row.ts <= rightTs && row.spread === 1) || null;
}

module.exports = {
  DWELL_SECONDS,
  QUANTITY,
  qualifiedAsk,
  findAnchorRearm,
  findCapRearm,
  unfalsifiableLowerReceipt,
  findAdmissionReask,
};
