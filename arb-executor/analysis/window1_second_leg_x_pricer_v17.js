"use strict";

// Causal second-leg shape eliminator.  The only policy-time input added by
// this module is the already-credited first-leg price X.  Eventual sibling
// floors are fit facts; the target event is removed before every fit.

const MIN_CELL_N = 20;

function finite(value) { const n = Number(value); return Number.isFinite(n) ? n : null; }
function quantile(values, p) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  return rows.length ? rows[Math.floor((rows.length - 1) * p)] : null;
}
function distribution(values) {
  const rows = values.filter(Number.isFinite);
  const p10 = quantile(rows, 0.10), p25 = quantile(rows, 0.25), p75 = quantile(rows, 0.75), p90 = quantile(rows, 0.90);
  return {
    n: rows.length,
    min: rows.length ? Math.min(...rows) : null,
    p10,
    p25,
    median: quantile(rows, 0.50),
    p75,
    p90,
    max: rows.length ? Math.max(...rows) : null,
    iqr: p25 === null ? null : p75 - p25,
    p90_p10_width: p10 === null ? null : p90 - p10,
  };
}
function linearFit(rows) {
  if (rows.length < 3) return null;
  const xs = rows.map((row) => finite(row.first_fill_x_cents));
  const ys = rows.map((row) => finite(row.sibling_eventual_ask_floor_cents));
  if (xs.some((x) => x === null) || ys.some((y) => y === null)) return null;
  const mx = xs.reduce((a, b) => a + b, 0) / xs.length;
  const my = ys.reduce((a, b) => a + b, 0) / ys.length;
  const denominator = xs.reduce((sum, x) => sum + (x - mx) ** 2, 0);
  const slope = denominator === 0 ? 0 : xs.reduce((sum, x, i) => sum + (x - mx) * (ys[i] - my), 0) / denominator;
  return { intercept: my - slope * mx, slope, predict: (x) => my + slope * (x - mx) };
}
function leaveOneOutResiduals(rows) {
  const residuals = [];
  for (let i = 0; i < rows.length; i += 1) {
    const fit = linearFit(rows.filter((_, index) => index !== i));
    if (fit) residuals.push(rows[i].sibling_eventual_ask_floor_cents - fit.predict(rows[i].first_fill_x_cents));
  }
  return residuals;
}

function conditionalFloorDistribution(library, { eventId, category, startingPriceSplit, firstFillX }) {
  const cellKey = `${category}|${startingPriceSplit}`;
  const sourceCell = library.cells?.[cellKey];
  if (!sourceCell) return { usable: false, reason: "NO_X_CONDITIONAL_CELL", cell_key: cellKey, leave_one_event_out_n: 0 };
  const rows = sourceCell.training_rows.filter((row) => row.event_id !== eventId);
  if (rows.length < MIN_CELL_N) return { usable: false, reason: "X_CONDITIONAL_CELL_THIN_AFTER_LEAVE_ONE_EVENT_OUT", cell_key: cellKey, leave_one_event_out_n: rows.length };
  const fit = linearFit(rows);
  const residuals = leaveOneOutResiduals(rows);
  if (!fit || residuals.length < MIN_CELL_N) return { usable: false, reason: "X_CONDITIONAL_FIT_UNAVAILABLE", cell_key: cellKey, leave_one_event_out_n: rows.length };
  const residual = distribution(residuals), center = fit.predict(firstFillX);
  if (![center, residual.p10, residual.p90].every(Number.isFinite)) return { usable: false, reason: "X_CONDITIONAL_DISTRIBUTION_NONFINITE", cell_key: cellKey, leave_one_event_out_n: rows.length };
  return {
    usable: true,
    reason: "LEAVE_ONE_EVENT_OUT_X_CONDITIONAL_DISTRIBUTION_BOUND",
    cell_key: cellKey,
    leave_one_event_out_n: rows.length,
    first_fill_x_cents: firstFillX,
    fitted_center_cents: center,
    empirical_support_floor_low_cents: center + residual.min,
    empirical_support_floor_high_cents: center + residual.max,
    central_distribution_floor_low_cents: center + residual.p10,
    central_distribution_floor_high_cents: center + residual.p90,
    residual_distribution: residual,
    model: { intercept: fit.intercept, slope: fit.slope },
    uncertainty_statistic_provenance: "V16_LEAVE_ONE_EVENT_OUT_P10_P90_WIDTH",
    elimination_support_law: "EMPIRICAL_LEAVE_ONE_EVENT_OUT_P10_P90_DISTRIBUTION_OVERLAP; NO_POINT_TARGET",
  };
}

function narrowSiblingShapes(library, input) {
  const conditional = conditionalFloorDistribution(library, input);
  if (!conditional.usable) return { ...conditional, applied: false, prior_shape_ids: [...input.shapeIds], retained_shape_ids: [...input.shapeIds], eliminated_shapes: [], abstaining_shapes: [] };
  const retained = [], eliminated = [], abstaining = [];
  for (const shapeId of input.shapeIds) {
    const memberRows = (library.shape_floor_support?.[shapeId]?.rows || []).filter((row) => row.event_id !== input.eventId);
    const shapeFloorDistribution = distribution(memberRows.map((row) => row.qualifying_ask_floor_cents));
    if (memberRows.length < MIN_CELL_N || shapeFloorDistribution.p10 === null || shapeFloorDistribution.p90 === null) {
      retained.push(shapeId);
      abstaining.push({ shape_id: shapeId, shape_leave_one_event_out_support_n: memberRows.length, reason: "SHAPE_MEMBER_FLOOR_DISTRIBUTION_THIN_OR_UNAVAILABLE_LEAVE_ONE_EVENT_OUT" });
      continue;
    }
    const overlaps = shapeFloorDistribution.p90 >= conditional.central_distribution_floor_low_cents && shapeFloorDistribution.p10 <= conditional.central_distribution_floor_high_cents;
    if (overlaps) retained.push(shapeId);
    else eliminated.push({ shape_id: shapeId, shape_leave_one_event_out_support_n: memberRows.length, shape_member_floor_distribution: shapeFloorDistribution, reason: "SHAPE_MEMBER_FLOOR_DISTRIBUTION_DISJOINT_FROM_X_CONDITIONAL_DISTRIBUTION" });
  }
  return {
    ...conditional,
    applied: true,
    prior_shape_ids: [...input.shapeIds],
    retained_shape_ids: retained,
    eliminated_shapes: eliminated,
    abstaining_shapes: abstaining,
    all_shapes_eliminated: retained.length === 0,
    comparison_law: "LEAVE_ONE_EVENT_OUT_SHAPE_MEMBER_P10_P90_DISTRIBUTION_OVERLAPS_LEAVE_ONE_EVENT_OUT_X_CONDITIONAL_P10_P90_DISTRIBUTION; NO_POINT_TARGET",
  };
}

module.exports = { MIN_CELL_N, distribution, linearFit, leaveOneOutResiduals, conditionalFloorDistribution, narrowSiblingShapes };
