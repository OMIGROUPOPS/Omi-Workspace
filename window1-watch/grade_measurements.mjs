// Report-only targets and order-age accounting. No forecast or execution is changed.
const SILENT = "STORE SILENT";
const finite = (n) => typeof n === "number" && Number.isFinite(n);
const mean = (xs) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : SILENT;
const maximum = (xs) => xs.length && xs.every(finite) ? Math.max(...xs) : SILENT;

export function scoreTarget(call, target, bell) {
  if (!target || target.status !== "OK") return {
    floor_error_cents: SILENT, timing_error_minutes: SILENT,
    reason: target?.reason ?? "NO_TARGET",
  };
  return {
    floor_error_cents: finite(call.q50) ? Math.abs(call.q50 - target.floor_cents) : SILENT,
    timing_error_minutes: finite(call.deadline_epoch) && finite(target.floor_epoch)
      ? Math.abs(call.deadline_epoch - target.floor_epoch) / 60 : SILENT,
    target_floor_cents: target.floor_cents,
    target_floor_epoch: target.floor_epoch,
    target_minutes_to_bell: finite(target.floor_epoch) ? (bell - target.floor_epoch) / 60 : SILENT,
  };
}

export function remainingTargets(prints, epoch, truth) {
  const end = Math.min(truth.span_end_epoch, truth.bell_epoch);
  const future = prints.filter((p) => p.epoch > epoch && p.epoch >= truth.span_start_epoch && p.epoch < end);
  const low = future.reduce((best, p) => !best || p.price < best.price ? p : best, null);
  const carried = prints.findLast((p) => p.epoch <= epoch);
  const executable = low ? {
    status: "OK", kind: "EXECUTABLE_FUTURE_PRINT_OBSERVATION", floor_cents: low.price,
    floor_epoch: low.epoch, print_receipt: low.receipt, source_row: low.source_row,
    note: "A later accepted true print, not proof of a hypothetical maker fill",
  } : { status: SILENT, reason: "NO_ACCEPTED_FUTURE_PRINT_IN_CORRECTED_SPAN" };
  const carryWins = carried && (!low || carried.price <= low.price);
  return {
    carried_gate_state: carried ? {
      cents: carried.price, observed_epoch: carried.epoch, print_receipt: carried.receipt,
      source_row: carried.source_row, evaluated_at_epoch: epoch,
      executable_future_print: false,
    } : { status: SILENT, reason: "NO_PRIOR_ACCEPTED_TRUE_PRINT" },
    remaining_path: carryWins ? {
      status: "OK", kind: "CARRIED_GATE_STATE_NOT_A_FUTURE_PRINT",
      floor_cents: carried.price, floor_epoch: epoch,
      carried_print_epoch: carried.epoch, print_receipt: carried.receipt,
    } : executable,
    executable_future_print: executable,
  };
}

export function microMeasurements(face, decisions, printInput) {
  const truth = face.truth, bell = truth?.bell_epoch;
  const traceBell = (face.trace_bell ?? face.bell).timestamp_epoch;
  const micro = {
    version: 2,
    eligibility_rule: "First in trace receipt order with a stored resolved P/Q/X sentence, finite Q and deadline, after own formation and inside the corrected span and bell. No future target participates in selection.",
    deadline_rule: "Stored absolute deadline_epoch, else original trace bell minus stored X; express that same instant on the corrected ruler clock. Never move a prediction when the ruler bell changes.",
    remaining_rule: "At every eligible receipt: minimum of carried accepted true print and strictly later accepted prints before corrected span end/bell. A carried minimum is timed at the receipt, not credited as a new print. Also score the future-print-only target separately.",
    aggregation: "First-call/full-span and all-receipt/remaining-path metrics are scored separately with unchanged MICRO rubric cutoffs. MICRO takes the worst mode; each mode uses the maximum error across its scored receipts/sides. Mean errors and denominators are reported, not alternative cutoffs.",
    clock: { ruler_bell_epoch: bell, trace_bell_epoch: traceBell },
    print_source: printInput?.provenance ?? SILENT,
    legs: {}, receipt_calls: [],
  };
  for (const leg of face.legs) {
    const ruler = truth?.legs?.[leg];
    const rows = [];
    for (const [order, row] of decisions.entries()) {
      const d = (row.forecasts ?? row.legs)?.[leg];
      const deadline = d?.deadline_epoch ?? (finite(d?.floor_mtb) ? traceBell - d.floor_mtb * 60 : null);
      const reason = !d ? "NO_STORED_FORECAST_ON_RECEIPT"
        : !d.has_sentence || d.status !== "RESOLVED" || !finite(d.q50) || !finite(deadline) ? "NO_RESOLVED_P_Q_X_FORECAST"
        : !finite(d.formation_end) ? "UNKNOWN_OWN_FORMATION"
        : !finite(row.epoch) || row.epoch < d.formation_end ? "BEFORE_OWN_FORMATION"
        : truth?.status !== "OK" || ![truth.span_start_epoch, truth.span_end_epoch, bell].every(finite) ? "NO_VERIFIED_RULER_SPAN"
        : row.epoch < truth.span_start_epoch || row.epoch >= Math.min(truth.span_end_epoch, bell) ? "OUTSIDE_CORRECTED_SPAN_OR_BELL" : null;
      const call = {
        leg, receipt_order: order, trace_row: row.trace_row ?? null, receipt: row.receipt,
        epoch: row.epoch, eligible: reason === null, eligibility_reason: reason,
        minutes_to_bell: finite(bell) ? (bell - row.epoch) / 60 : SILENT,
        q50: d?.q50 ?? null, q_source: d?.q_source ?? null,
        q25: d?.q25 ?? null, q75: d?.q75 ?? null, band_source: d?.band_source ?? null,
        q_author: d?.q_author ?? null, x_author: d?.x_author ?? null,
        deadline_epoch: deadline, stored_deadline_epoch: d?.deadline_epoch ?? null,
        stored_x_minutes_to_trace_bell: d?.floor_mtb ?? null,
        x_minutes_to_corrected_bell: finite(deadline) && finite(bell) ? (bell - deadline) / 60 : SILENT,
      };
      if (call.eligible) {
        call.targets = printInput?.legs?.[leg] ? remainingTargets(printInput.legs[leg], row.epoch, truth) : {
          remaining_path: { status: SILENT, reason: "NO_ACCEPTED_TRUE_PRINT_SOURCE" },
          executable_future_print: { status: SILENT, reason: "NO_ACCEPTED_TRUE_PRINT_SOURCE" },
          carried_gate_state: { status: SILENT, reason: "NO_ACCEPTED_TRUE_PRINT_SOURCE" },
        };
        call.remaining_path_score = scoreTarget(call, call.targets.remaining_path, bell);
        call.executable_future_print_score = scoreTarget(call, call.targets.executable_future_print, bell);
      }
      rows.push(call);
    }
    const eligible = rows.filter((r) => r.eligible), first = eligible[0];
    const full = ruler?.status === "OK" ? {
      status: "OK", kind: "FULL_SPAN_RECORDED_FLOOR", floor_cents: ruler.floor_cents,
      floor_epoch: ruler.floor_epoch,
    } : { status: SILENT, reason: ruler?.reason ?? "NO_VERIFIED_FLOOR" };
    const summarize = (key) => {
      const scores = eligible.map((c) => c[key]);
      const good = scores.filter((s) => finite(s?.floor_error_cents) && finite(s?.timing_error_minutes));
      return {
        receipts_eligible: eligible.length, receipts_scored: good.length,
        receipts_unscored: eligible.length - good.length,
        mean_floor_error_cents: mean(good.map((s) => s.floor_error_cents)),
        mean_timing_error_minutes: mean(good.map((s) => s.timing_error_minutes)),
        max_floor_error_cents: maximum(scores.map((s) => s?.floor_error_cents)),
        max_timing_error_minutes: maximum(scores.map((s) => s?.timing_error_minutes)),
      };
    };
    micro.legs[leg] = {
      first_eligible_full_span: first ? {
        receipt: first.receipt, receipt_order: first.receipt_order, epoch: first.epoch,
        minutes_to_bell: first.minutes_to_bell, q50: first.q50,
        q25: first.q25, q75: first.q75, band_source: first.band_source,
        q_author: first.q_author, x_author: first.x_author, deadline_epoch: first.deadline_epoch,
        target: full, floor_already_observed_at_call: finite(full.floor_epoch) ? full.floor_epoch <= first.epoch : SILENT,
        ...scoreTarget(first, full, bell),
      } : { status: SILENT, reason: "NO_ELIGIBLE_FORECAST", floor_error_cents: SILENT, timing_error_minutes: SILENT },
      remaining_path: summarize("remaining_path_score"),
      executable_future_print: summarize("executable_future_print_score"),
    };
    micro.receipt_calls.push(...rows);
  }
  micro.receipt_calls.sort((a, b) => a.receipt_order - b.receipt_order || a.leg.localeCompare(b.leg));
  micro.mode_metrics = Object.fromEntries(["first_eligible_full_span", "remaining_path"].map((mode) => [mode, {
    max_floor_error_cents: maximum(Object.values(micro.legs).map((l) => l[mode][mode === "remaining_path" ? "max_floor_error_cents" : "floor_error_cents"])),
    max_timing_error_minutes: maximum(Object.values(micro.legs).map((l) => l[mode][mode === "remaining_path" ? "max_timing_error_minutes" : "timing_error_minutes"])),
  }]));
  return micro;
}

export function measureRestAges(actions) {
  const active = new Map(), out = new Map();
  for (const a of actions) {
    let state = active.get(a.leg);
    const point = { epoch: a.timestamp_epoch, receipt: a.receipt };
    if (a.kind === "PLACE") state = { lineage: point, price: point, cents: a.new_cents };
    else if (["REPRICE", "HOLD_CHANGE"].includes(a.kind) || a.raw?.action === "REPRICE_REST") {
      state = { lineage: state?.lineage ?? null,
        price: a.new_cents !== state?.cents ? point : state?.price ?? null, cents: a.new_cents };
    }
    const age = (p) => finite(p?.epoch) && finite(a.timestamp_epoch) && a.timestamp_epoch >= p.epoch
      ? (a.timestamp_epoch - p.epoch) / 60 : SILENT;
    out.set(a.id ?? a, {
      order_lineage_receipt: state?.lineage?.receipt ?? null,
      order_lineage_start_epoch: state?.lineage?.epoch ?? null,
      current_price_receipt: state?.price?.receipt ?? null,
      current_price_start_epoch: state?.price?.epoch ?? null,
      order_lineage_age_minutes: age(state?.lineage),
      current_price_age_minutes: age(state?.price),
      same_second_fill: a.kind === "FILL" && finite(state?.price?.epoch) && finite(a.timestamp_epoch)
        ? Math.floor(a.timestamp_epoch) === Math.floor(state.price.epoch) : a.kind === "FILL" ? SILENT : false,
    });
    if (["FILL", "REMOVE"].includes(a.kind)) active.delete(a.leg);
    else if (state) active.set(a.leg, state);
  }
  return out;
}
