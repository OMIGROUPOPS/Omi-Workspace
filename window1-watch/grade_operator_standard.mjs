// Hindsight performance grading only. No engine imports or price production.
const SILENT = "STORE SILENT";
const finite = (x) => typeof x === "number" && Number.isFinite(x);
const numeric = (x) => x !== null && x !== undefined && String(x).trim() !== "" && Number.isFinite(Number(x)) ? Number(x) : null;
const show = (x) => finite(x) ? String(Number(x.toFixed(2))) : SILENT;
export function worst(letters, rubric) {
  if (letters.includes("F")) return "F";
  if (!letters.length || letters.includes(SILENT)) return SILENT;
  return letters.reduce((a, b) => rubric.letters.indexOf(a) >= rubric.letters.indexOf(b) ? a : b);
}
function thresholdGrade(value, cutoffs, direction, rubric) {
  if (!finite(value)) return SILENT;
  return rubric.letters.find((letter) => finite(cutoffs[letter]) &&
    (direction === "max" ? value <= cutoffs[letter] : value >= cutoffs[letter])) ?? "F";
}
export function floorCallGrade(call, rule, rubric) {
  if (call?.reason === "NO_ELIGIBLE_FORECAST") return { letter: "F", reason: call.reason };
  if (!finite(call?.floor_error_cents)) return { letter: SILENT, reason: "NO_VERIFIED_FLOOR_OR_CALL" };
  const point = thresholdGrade(call.floor_error_cents, rule.maximum_point_error_cents, "max", rubric);
  const { q25, q75, q50, target_floor_cents: floor } = call;
  const valid = [q25, q50, q75, floor].every(finite) && q25 <= q50 && q50 <= q75;
  const contains = valid ? q25 <= floor && floor <= q75 : null;
  const width = valid ? q75 - q25 : null;
  const range = contains ? rubric.letters.find((l) => finite(rule.range_credit[l]?.maximum_width_cents) &&
    width <= rule.range_credit[l].maximum_width_cents) ?? "F" : valid ? "F" : SILENT;
  const letter = range !== SILENT && rubric.letters.indexOf(range) < rubric.letters.indexOf(point) ? range : point;
  return { letter, point_letter: point, range_letter: range, q50, q25, q75,
    floor_error_cents: call.floor_error_cents, band_width_cents: width, band_contains_floor: contains,
    receipt: call.receipt, source: call.band_source ?? null, target_floor_cents: floor,
    floor_already_observed_at_call: call.floor_already_observed_at_call,
    reason: letter !== point ? "FIRST_CALL_RANGE_CREDIT" : "FIRST_CALL_POINT_ERROR" };
}
export function operatorGrade(face, decisions, sections, rubric) {
  if (rubric.rubric_id !== "OPERATOR_STANDARD_V1") throw new Error("Unsupported operator rubric");
  const { sentence, macro, micro, hands, outcome } = sections, sides = face.legs;
  const rules = rubric.sections, truth = face.truth;
  const end = Math.min(truth?.span_end_epoch, truth?.bell_epoch);
  const macroLegs = {};
  for (const leg of sides) {
    const records = decisions.filter((r) => r.epoch >= truth?.span_start_epoch && r.epoch < end && r.roles?.[leg]);
    const fill = outcome.legs[leg];
    const beforeFill = records.filter((r) => !finite(fill?.fill_epoch) || r.epoch <= fill.fill_epoch);
    const first = beforeFill.find((r) => ["CLIMBER", "FALLER"].includes(r.roles[leg].first_bind));
    const called = first?.roles[leg].first_bind ?? (beforeFill.length ? "NOT_CALLABLE" : SILENT);
    const row = truth?.effective_row;
    const side = ["legA", "legB"].find((s) => row?.[s] === leg);
    const open = side ? numeric(row[`${side}_open_postformation_c`]) : null;
    const close = side ? numeric(row[`${side}_close_c`]) : null;
    const drift = finite(open) && finite(close) ? close - open : null;
    const realized = drift === null ? SILENT : drift >= rules.MACRO.role_drift_cents ? "CLIMBER"
      : drift <= -rules.MACRO.role_drift_cents ? "FALLER" : "NOT_CALLABLE";
    macroLegs[leg] = { called_role: called, realized_role: realized,
      correct: called === SILENT || realized === SILENT ? SILENT : called === realized,
      first_recorded_receipt: first?.receipt ?? null, first_recorded_epoch: first?.epoch ?? null,
      first_bind_epoch: first?.roles[leg].first_bind_epoch ?? null,
      final_stored_role: records.at(-1)?.roles[leg].current_role ?? SILENT,
      flip_count: records.length && records.every((r) => finite(r.roles[leg].flip_count))
        ? Math.max(...records.map((r) => r.roles[leg].flip_count)) : SILENT,
      open_cents: open, close_cents: close, realized_drift_cents: drift,
      role_source: "layers.macro.context.pool_cascade.sides[leg].roles (or belief.pool_cascade.roles)",
      realized_source: side ? `corrected effective_row.${side}_close_c - ${side}_open_postformation_c` : SILENT };
  }
  macro.operator_roles = macroLegs;
  macro.operator_rule = rules.MACRO;
  const correct = Object.values(macroLegs).every((l) => typeof l.correct === "boolean")
    ? Object.values(macroLegs).filter((l) => l.correct).length / sides.length : null;
  const microLegs = Object.fromEntries(sides.map((leg) => [leg, floorCallGrade(micro.legs[leg].first_eligible_full_span, rules.MICRO, rubric)]));
  micro.operator_first_call = microLegs;
  micro.aggregation = rules.MICRO.aggregation;
  micro.mode_grades = { first_eligible_full_span: worst(Object.values(microLegs).map((l) => l.letter), rubric),
    remaining_path: "DIAGNOSTIC — does not govern", executable_future_print: "DIAGNOSTIC — does not govern" };
  micro.oracle_diagnostic = {
    scope: "Existing face oracle; receipt-weighted, includes post-fill forecasts; not a letter cutoff",
    provenance: face.oracle?.provenance ?? SILENT,
    legs: Object.fromEntries(sides.map((leg) => {
      const o = face.oracle?.legs?.[leg];
      return [leg, { mean_absolute_gap_cents: o?.mean_absolute_gap_cents ?? SILENT,
        comparable_receipts: o?.comparable_receipts ?? SILENT, receipt_count: o?.receipt_count ?? SILENT,
        missing_q_receipts: o?.missing_q_receipts ?? SILENT, no_future_print_receipts: o?.no_future_print_receipts ?? SILENT }];
    })) };
  const trade = { legs: {}, rule: rules.TRADE, same_second_fills: hands.same_second_fills };
  for (const leg of sides) {
    const fill = outcome.legs[leg], ruler = truth?.legs?.[leg];
    const age = hands.rest_age_at_fill_minutes.find((a) => a.leg === leg);
    const action = hands.actions.find((a) => a.leg === leg && a.kind === "FILL");
    trade.legs[leg] = { ...fill, floor_cents: ruler?.floor_cents ?? SILENT,
      floor_epoch: ruler?.floor_epoch ?? null,
      floor_printed_before_fill: fill.filled && finite(ruler?.floor_epoch) ? ruler.floor_epoch < fill.fill_epoch : null,
      floor_printed_before_order: finite(ruler?.floor_epoch) && finite(action?.order_lineage_start_epoch)
        ? ruler.floor_epoch < action.order_lineage_start_epoch : SILENT,
      order_lineage_age_minutes: age?.order_lineage_age_minutes ?? null,
      current_price_age_minutes: age?.current_price_age_minutes ?? null,
      note: "Full-span floor premium retained even if floor already printed; queue/earlier maker fill is not assumed" };
  }
  const validFills = Object.values(trade.legs).filter((l) => l.valid_span_fill === true);
  const errorsKnown = validFills.every((l) => finite(l.vs_floor_cents));
  const noOffer = truth?.status === "OK" && finite(outcome.best_capturable_cents) && outcome.best_capturable_cents <= 0;
  const invalidFill = Object.values(trade.legs).some((l) => l.filled && l.valid_span_fill === false);
  const unknownFill = Object.values(trade.legs).some((l) => l.filled && (l.valid_span_fill === SILENT || !finite(l.vs_floor_cents)));
  let tradeLetter = unknownFill ? SILENT : validFills.length === sides.length
    ? thresholdGrade(Math.max(...validFills.map((l) => Math.abs(l.vs_floor_cents))), rules.TRADE.maximum_both_fill_error_cents, "max", rubric)
    : validFills.length ? rules.TRADE.one_valid_fill : rules.TRADE.no_valid_fills;
  if (validFills.length === sides.length && errorsKnown && tradeLetter === "F") tradeLetter = rules.TRADE.both_filled_but_further;
  const pair = { ...outcome, rule: rules.PAIR, offered: noOffer ? false : finite(outcome.best_capturable_cents) ? true : SILENT };
  let pairLetter = outcome.valid_pair_completed === SILENT ? SILENT : !outcome.valid_pair_completed ? "F"
    : !finite(outcome.pair_sum) ? SILENT : outcome.pair_sum > rules.PAIR.par_cents ? "F"
    : outcome.pair_sum === rules.PAIR.par_cents ? rules.PAIR.complete_at_par
    : !finite(outcome.capture_ratio) ? SILENT
    : thresholdGrade(outcome.capture_ratio, rules.PAIR.minimum_capture_ratio, "min", rubric);
  if (pairLetter === "F" && outcome.valid_pair_completed && outcome.captured_cents > 0) pairLetter = rules.PAIR.positive_capture_below_B;
  if (noOffer) { pairLetter = "NOT OFFERED"; if (!validFills.length) tradeLetter = "NOT OFFERED"; }
  const hard = [sentence.named_tokens_found.length ? "SENTENCE: named tokens" : null,
    hands.observed_pre_formation_placements > 0 ? "HANDS: pre-formation placements" : null,
    hands.same_second_fills > 0 ? "HANDS: same-second fill" : null,
    hands.observed_post_only_violations > 0 ? "HANDS: post-only violation" : null,
    invalidFill ? "TRADE: fill outside corrected span/bell" : null,
    finite(outcome.pair_sum) && outcome.pair_sum > rules.PAIR.par_cents ? "PAIR: over par" : null].filter(Boolean);
  const safetyUnknown = hands.fill_age_uncheckable > 0 || hands.post_only_uncheckable > 0 || hands.formation_uncheckable > 0;
  const grades = {
    MACRO: { letter: thresholdGrade(correct, rules.MACRO.minimum_correct_side_share, "min", rubric), metrics: { correct_side_share: correct }, legs: macroLegs },
    MICRO: { letter: worst(Object.values(microLegs).map((l) => l.letter), rubric), legs: microLegs },
    TRADE: { letter: tradeLetter, metrics: { valid_fills: validFills.length, side_count: sides.length }, legs: trade.legs },
    PAIR: { letter: pairLetter, metrics: { pair_sum: outcome.pair_sum, capture_ratio: outcome.capture_ratio, offered_cents: outcome.best_capturable_cents } },
  };
  const letter = hard.length ? "F" : noOffer ? "NOT OFFERED" : worst([...Object.values(grades).map((s) => s.letter), ...(safetyUnknown ? [SILENT] : [])], rubric);
  const governing = hard.length ? hard.join(" · ") : noOffer ? "NOT OFFERED — corrected floor pair offers no discount"
    : safetyUnknown && letter === SILENT ? "UNVERIFIED SAFETY EVIDENCE"
    : Object.entries(grades).filter(([, g]) => g.letter === letter).map(([name]) => name).join(" · ");
  const lines = {
    MACRO: sides.map((l) => `${l} ${macroLegs[l].called_role} → ${macroLegs[l].realized_role}`).join(" · "),
    MICRO: sides.map((l) => `${l} Q ${show(microLegs[l].q50)} vs floor ${show(microLegs[l].target_floor_cents)}¢; range ${show(microLegs[l].q25)}–${show(microLegs[l].q75)}`).join(" · "),
    TRADE: sides.map((l) => trade.legs[l].filled ? `${l} ${show(trade.legs[l].cents)}¢ (+${show(trade.legs[l].vs_floor_cents)}¢${trade.legs[l].floor_printed_before_fill ? "; floor printed earlier" : ""})` : `${l} unfilled`).join(" · "),
    PAIR: noOffer ? "Not offered — recorded floors sum to par or above" : `${show(outcome.pair_sum)}¢ pair · ${show(outcome.captured_cents)} of ${show(outcome.best_capturable_cents)}¢ captured`,
  };
  return { grades, trade, pair, hard, letter, governing, lines, safetyUnknown };
}
