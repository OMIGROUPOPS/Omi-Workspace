// Report-card measurements only. No engine imports, orders or price production.
import fs from "node:fs";
import { microMeasurements, measureRestAges } from "./grade_measurements.mjs";
import { operatorGrade } from "./grade_operator_standard.mjs";
export const SILENT = "STORE SILENT";
const finite = (n) => typeof n === "number" && Number.isFinite(n);
const value = (n) => (finite(n) ? n : SILENT);
const ratio = (n, d) => (d ? n / d : SILENT);
const shown = (n) =>
  finite(n) ? String(Number(n.toFixed(2))) : String(n ?? SILENT);
const unit = (n, suffix) => (finite(n) ? `${shown(n)}${suffix}` : SILENT);
const percent = (n) => (finite(n) ? `${shown(n * 100)}%` : SILENT);
const priorAuthors = new Set([
  "PRIOR_ONLY",
  "LIBRARY_FRACTION_PRIOR",
  "INSUFFICIENT_EVIDENCE",
  SILENT,
]);
// 2dfb5b0a stamps this Q badge from print count/slope; it adds no reweighting.
const nonOrganQAuthors = new Set([
  ...priorAuthors,
  "PRIOR_REWEIGHTED_BY_OWN_WALK",
]);
const fields = fs.readFileSync(new URL("./FIELDS.md", import.meta.url), "utf8");
const writerTable = fields
  .split("<!-- grade-writers:start -->")[1]
  ?.split("<!-- grade-writers:end -->")[0];
if (!writerTable) throw new Error("FIELDS.md: missing grade writer classes");
const writers = writerTable
  .split(/\r?\n/)
  .filter((l) => l.startsWith("| ") && !l.startsWith("| Token"))
  .map((l) =>
    l
      .split("|")
      .map((s) => s.trim())
      .slice(1, 3),
  );
const match = (token, pattern) =>
  pattern.endsWith("*")
    ? token?.startsWith(pattern.slice(0, -1))
    : token === pattern;

export function namedToken(token, legs = [], event = "") {
  if (typeof token !== "string") return false;
  return (
    /^(PAL_|GIU_|LAJSVA_)/.test(token) ||
    legs.some((l) => token.startsWith(l + "_")) ||
    (event && token.includes(event) && /WRITER|GATED|HAND/.test(token))
  );
}
export function writerClass(tokens, sameSecond = false) {
  if (sameSecond) return "SAME_SECOND";
  // Table order establishes precedence (named hand before ladder/seat).
  for (const [pattern, cls] of writers)
    if (tokens.some((t) => match(t, pattern))) return cls;
  return SILENT;
}
export function scanNamed(root, legs, event, visit, field = "") {
  if (typeof root === "string") {
    // Exact symbolic values, not prose, library event identities, or receipt paths.
    if (/^[A-Z0-9_-]+$/.test(root) && namedToken(root, legs, event))
      visit(root, field);
  } else if (root && typeof root === "object") {
    for (const [key, v] of Object.entries(root)) {
      if (
        [
          "event_id",
          "leg_id",
          "receipt",
          "source_receipt",
          "receipt_id",
        ].includes(key)
      )
        continue;
      scanNamed(v, legs, event, visit, field ? `${field}.${key}` : key);
    }
  }
}
export function projectDecision(row, face) {
  const legs = {};
  for (const d of row.derivations ?? []) {
    const l = d.leg_id,
      a = d.derivation?.pricing_authority,
      b = row.layers?.micro?.context?.beliefs?.[l];
    const deadline = b?.deadline;
    const tokens = [
      d.action?.reason,
      d.layered_dual_belief?.decision_arbitration?.winner?.lane,
      d.layered_dual_belief?.envelope_placement?.writer_lane,
      d.layered_dual_belief?.envelope_placement?.mode,
      a?.authority_source,
      b?.q_author,
      b?.x_author,
    ].filter(Boolean);
    legs[l] = {
      has_sentence:
        !!b?.plain_sentence &&
        finite(b?.current_cents) &&
        finite(b?.predicted_cents) &&
        finite(
          deadline?.deadline_minutes_to_bell ?? b?.predicted_minutes_to_bell,
        ),
      q_author: b?.q_author ?? null,
      x_author: b?.x_author ?? null,
      q_present: finite(b?.predicted_cents),
      x_present: finite(
        deadline?.deadline_minutes_to_bell ?? b?.predicted_minutes_to_bell,
      ),
      tokens,
      family: b?.family ?? row.layers?.macro?.context?.families?.[l] ?? null,
      q50: a?.true_conditioning?.posterior_q50_cents ?? null,
      q25: a?.true_conditioning?.quantiles?.q25?.level_cents ?? null,
      q75: a?.true_conditioning?.quantiles?.q75?.level_cents ?? null,
      band_source: "pricing_authority.true_conditioning.quantiles.q25/q75.level_cents",
      floor_mtb:
        deadline?.deadline_minutes_to_bell ??
        b?.predicted_minutes_to_bell ??
        null,
      action: d.action ?? null,
      ask: row.reads?.books?.value?.[l]?.ask_cents ?? null,
      formation_end:
        d.derivation?.formation_end_epoch ?? b?.own_evidence?.formation_end_epoch ?? face.formation_end_epoch ?? null,
      // Explicit weights and unique own prints; an author token alone is not Gate-1 proof.
      own_print_receipts: b?.own_print_receipts ?? [],
      evidence_rows: a?.own_evidence_rows ?? [],
    };
  }
  const forecasts = Object.fromEntries(Object.entries(row.layers?.micro?.context?.beliefs ?? {}).map(([leg, b]) => {
    const d = legs[leg];
    const q50 = d?.q50 ?? b.predicted_cents ?? null;
    return [leg, {
      ...d, status: b.status ?? null, q50,
      q_source: finite(d?.q50) ? "pricing_authority.true_conditioning.posterior_q50_cents" : "belief.predicted_cents",
      has_sentence: !!b.plain_sentence && finite(b.current_cents) && finite(q50) &&
        finite(b.deadline?.deadline_epoch ?? b.predicted_minutes_to_bell),
      q_author: b.q_author ?? null, x_author: b.x_author ?? null,
      q25: d?.q25 ?? b.pool_cascade?.quantiles?.q25?.level_cents ?? null,
      q75: d?.q75 ?? b.pool_cascade?.quantiles?.q75?.level_cents ?? null,
      band_source: finite(d?.q25) && finite(d?.q75) ? d.band_source : "belief.pool_cascade.quantiles.q25/q75.level_cents",
      floor_mtb: b.deadline?.deadline_minutes_to_bell ?? b.predicted_minutes_to_bell ?? null,
      deadline_epoch: b.deadline?.deadline_epoch ?? null,
      formation_end: d?.formation_end ?? b.own_evidence?.formation_end_epoch ?? face.formation_end_epoch ?? null,
    }];
  }));
  return {
    epoch: row.timestamp_epoch, receipt: row.receipt, legs, forecasts,
    roles: Object.fromEntries(face.legs.map((leg) => [leg,
      row.layers?.macro?.context?.pool_cascade?.sides?.[leg]?.roles ??
      row.layers?.micro?.context?.beliefs?.[leg]?.pool_cascade?.roles ?? null,
    ])),
    // Credited sides can still have a telemetry belief, without an order derivation.
    families: Object.fromEntries(face.legs.map((leg) => [leg,
      row.layers?.micro?.context?.beliefs?.[leg]?.family ??
      row.layers?.macro?.context?.families?.[leg] ?? legs[leg]?.family ?? null,
    ])),
  };
}
function metricGrade(v, rule, rubric) {
  if (!finite(v)) return SILENT;
  for (const letter of rubric.letters.filter((l) => l !== "F")) {
    const c = rule.cutoffs[letter];
    if (!finite(c)) throw new Error(`Invalid PLACEHOLDER cutoff ${letter}`);
    if (rule.direction === "min" ? v >= c : v <= c) return letter;
  }
  return "F";
}
export function worstLetter(letters, rubric) {
  if (letters.includes("F")) return "F";
  if (!letters.length || letters.includes(SILENT)) return SILENT;
  return letters.reduce((a, b) =>
    rubric.letters.indexOf(a) > rubric.letters.indexOf(b) ? a : b,
  );
}
function maxComplete(values) {
  return values.length && values.every(finite) ? Math.max(...values) : SILENT;
}

export function gradeFace(
  face,
  decisions,
  namedEvidence,
  bench,
  rubric,
  provenance,
  printInput = null,
) {
  const event = face.provenance.event_id,
    sides = face.legs;
  const entries = decisions.flatMap((r) =>
    Object.entries(r.legs).map(([leg, d]) => ({
      ...d,
      leg,
      receipt: r.receipt,
    })),
  );
  const organ = (d, axis) =>
    d[`${axis}_present`] &&
    typeof d[`${axis}_author`] === "string" &&
    !(axis === "q" ? nonOrganQAuthors : priorAuthors).has(
      d[`${axis}_author`],
    ) &&
    !d.tokens.some((t) => namedToken(t, sides, event));
  const q = entries.filter((d) => organ(d, "q")).length,
    x = entries.filter((d) => organ(d, "x")).length;
  const sentence = {
    receipts_total: decisions.length,
    receipts_with_sentence: decisions.filter((r) =>
      sides.every((l) => r.legs[l]?.has_sentence),
    ).length,
    leg_receipts_total: entries.length,
    leg_receipts_with_sentence: entries.filter((d) => d.has_sentence).length,
    q_organ_leg_receipts: q,
    x_organ_leg_receipts: x,
    share_q_authored_by_organ: ratio(q, entries.length),
    share_x_authored_by_organ: ratio(x, entries.length),
    non_organ_q_authors: [...nonOrganQAuthors],
    named_tokens_found: [...namedEvidence.keys()].sort(),
    named_token_evidence: [...namedEvidence.values()].sort((a, b) =>
      a.token.localeCompare(b.token),
    ),
    author_counts: Object.fromEntries(
      ["q", "x"].map((axis) => [
        axis,
        entries.reduce((out, d) => {
          const token = d[`${axis}_author`] ?? SILENT;
          out[token] = (out[token] ?? 0) + 1;
          return out;
        }, {}),
      ]),
    ),
    authorship_scope:
      "Author-token metric excluding prior-only badges, including PRIOR_REWEIGHTED_BY_OWN_WALK; not certification of the Gate-1 own-receipt/weight chain.",
    gate_1_authorship_certification: SILENT,
    gate_1_reason:
      "Author labels do not independently prove causal own-print weights and own-clock authorship; do not equate the token share with passing Gate 1.",
  };
  const benchEvent =
    bench &&
    Object.values(bench.events ?? {}).find((e) => e.event_id === event);
  const first = benchEvent?.first_tick;
  const familyAt = (r, leg) => r?.families?.[leg] ?? r?.legs?.[leg]?.family;
  const benchBell = finite(first?.epoch) && finite(first?.mtb_first)
    ? first.epoch + first.mtb_first * 60 : null;
  // Compare on the bench clock without shifting an OS decision or recomputing a family.
  // A later receipt lacking a side does not erase that side's last recorded call.
  const macroGates = finite(benchBell) ? Object.keys(benchEvent.gates ?? {})
    .map(Number).filter((g) => finite(g) && g <= first.mtb_first)
    .sort((a, b) => b - a).map((gate) => {
      const epoch = benchBell - gate * 60;
      const available = decisions.filter((r) => r.epoch <= epoch);
      return { gate, epoch, stage: available.at(-1), legs: Object.fromEntries(
        sides.map((leg) => [leg, available.findLast((r) => familyAt(r, leg))])
      ) };
    }) : [];
  const macroLast = macroGates.at(-1);
  const benchLast = benchEvent?.gates?.[String(macroLast?.gate)];
  const benchReason = !benchEvent
    ? "NO_BOUND_BENCH_EVENT"
    : !finite(benchBell)
      ? "NO_BENCH_BELL"
      : !macroLast
        ? "NO_BENCH_GATE_AFTER_FIRST_TICK"
      : null;
  const macro = {
    last_gate: macroLast?.gate ?? SILENT,
    receipt: macroLast?.stage?.receipt ?? null,
    comparison_clock: {
      source: "BENCH_FIRST_TICK_EPOCH_PLUS_MTB",
      bell_epoch: benchBell,
      trace_bell_epoch: (face.trace_bell ?? face.bell).timestamp_epoch,
      delta_seconds: finite(benchBell) ? benchBell - (face.trace_bell ?? face.bell).timestamp_epoch : null,
      last_gate_epoch: macroLast?.epoch ?? null,
      rule: "At bench bell minus gate*60, use each leg's latest stored OS family at or before that epoch; realized family and pool accuracy use the same bench gate. No OS call is recomputed.",
    },
    legs: {},
    pile_ess_at_last_gate: value(benchLast?.validity?.ess),
    pool_accuracy_by_gate: macroGates.map((g) => {
      const v = benchEvent?.gates?.[String(g.gate)]?.validity;
      return {
        gate: g.gate,
        epoch: g.epoch,
        share: value(v?.weighted_share),
        ess: value(v?.ess),
        status: v?.status ?? SILENT,
        reason: benchReason ?? (!v ? "NO_STORED_VALIDITY" : null),
      };
    }),
    bench_label: face.bench?.label ?? SILENT,
    bench_reason: benchReason,
    ess_source: "Bench validity pool, not OS membership ESS",
  };
  const micro = microMeasurements(face, decisions, printInput);
  for (const leg of sides) {
    const bside =
      benchEvent?.first_tick?.favorite === leg
        ? "favorite"
        : benchEvent?.first_tick?.underdog === leg
          ? "underdog"
          : null;
    const rules = Object.fromEntries(
      Object.entries(benchLast?.rules ?? {}).map(([key, r]) => [
        key,
        {
          called_family:
            r.sides?.[bside]?.status === "OK"
              ? (r.sides[bside].family?.top ?? SILENT)
              : SILENT,
          realized_family: r.sides?.[bside]?.realized_family ?? SILENT,
          ess: value(r.sides?.[bside]?.ess),
          status: r.sides?.[bside]?.status ?? SILENT,
        },
      ]),
    );
    // Realized label already computed by the bound bench taxonomy. Never substitute an OS family.
    const realized = [
      ...new Set(
        Object.values(rules)
          .map((r) => r.realized_family)
          .filter((r) => r !== SILENT),
      ),
    ];
    if (realized.length > 1)
      throw new Error(`Contradictory realized bench families: ${leg}`);
    const call = macroLast?.legs?.[leg];
    const actual = realized[0] ?? SILENT,
      called = familyAt(call, leg) ?? SILENT;
    macro.legs[leg] = {
      realized_family: actual,
      family_called_at_last_gate: called,
      family_call_receipt: call?.receipt ?? null,
      family_call_epoch: call?.epoch ?? null,
      family_call_minutes_to_bench_bell: call && finite(benchBell)
        ? (benchBell - call.epoch) / 60 : null,
      family_call_age_at_gate_minutes: call && macroLast
        ? (macroLast.epoch - call.epoch) / 60 : null,
      gate_after_trace_bell: macroLast
        ? macroLast.epoch > (face.trace_bell ?? face.bell).timestamp_epoch : null,
      family_match:
        actual === SILENT || called === SILENT ? SILENT : called === actual,
      family_call_source:
        "Stored OS belief.family; cascade beliefs carry the selected pool's modal family",
      bench_families_by_rule: rules,
      reason:
        benchReason ??
        (actual === SILENT
          ? "NO_REALIZED_TAXONOMY_LABEL"
          : called === SILENT
            ? "NO_OS_FAMILY_AT_LAST_GATE"
            : null),
    };
  }
  const byReceipt = new Map(decisions.map((d) => [d.receipt, d]));
  const ages = measureRestAges(face.render.bid_actions);
  const actions = face.render.bid_actions.map((a) => {
    const raw = Object.values(a.raw ?? {}).filter((v) => typeof v === "string");
    const age = ages.get(a.id ?? a);
    const sameSecond = age.same_second_fill;
    let tokens = raw;
    if (a.kind === "FILL")
      tokens = [
        ...raw,
        ...(byReceipt.get(age.current_price_receipt ?? a.fill?.place_receipt)?.legs?.[a.leg]?.tokens ?? []),
      ];
    return {
      receipt: a.receipt,
      leg: a.leg,
      action: a.raw?.action ?? a.kind,
      kind: a.kind,
      minutes_to_bell: value(a.minutes_to_bell),
      old_cents: a.old_cents,
      new_cents: a.new_cents,
      writer_class: writerClass(tokens, sameSecond === true),
      tokens,
      ...age,
      timestamp_epoch: a.timestamp_epoch,
      rest_age_at_fill_minutes:
        a.kind === "FILL" ? age.current_price_age_minutes : null,
      legacy_display_rest_age_minutes: a.kind === "FILL" ? value(a.fill?.rest_age_minutes) : null,
      same_second_fill: sameSecond,
      source_url: a.detail_url,
    };
  });
  const placed = decisions.flatMap((r) =>
    Object.entries(r.legs)
      .filter(([, d]) =>
        ["PLACE_REST", "REPRICE_REST"].includes(
          d.action?.type ?? d.action?.name ?? d.action?.action,
        ),
      )
      .map(([leg, d]) => ({ r, d, leg })),
  );
  const postOnlyUnknown = placed.filter(
    ({ d }) => !finite(d.action?.target_cents) || !finite(d.ask),
  );
  const badPost = placed.filter(
    ({ d }) =>
      finite(d.action?.target_cents) &&
      finite(d.ask) &&
      d.action.target_cents >= d.ask,
  );
  const formationUnknown = placed.filter(
    ({ d, r }) => !finite(d.formation_end) || !finite(r.epoch),
  );
  const pre = placed.filter(
    ({ d, r }) => finite(d.formation_end) && r.epoch < d.formation_end,
  );
  const hands = {
    actions,
    age_rule: "Lineage begins at PLACE, survives reprices, ends on remove/fill. Current-price age resets only on a level change. Same-second tests current-price start and fill timestamps, not rounded minute ages. Missing starts remain STORE SILENT.",
    placement_rows: placed.length,
    rest_age_at_fill_minutes: actions
      .filter((a) => a.kind === "FILL")
      .map((a) => ({
        leg: a.leg,
        receipt: a.receipt,
        minutes: a.rest_age_at_fill_minutes,
        order_lineage_age_minutes: a.order_lineage_age_minutes,
        current_price_age_minutes: a.current_price_age_minutes,
        order_lineage_receipt: a.order_lineage_receipt,
        current_price_receipt: a.current_price_receipt,
      })),
    post_only_violations: postOnlyUnknown.length ? SILENT : badPost.length,
    observed_post_only_violations: badPost.length,
    post_only_uncheckable: postOnlyUnknown.length,
    pre_formation_placements: formationUnknown.length ? SILENT : pre.length,
    observed_pre_formation_placements: pre.length,
    formation_uncheckable: formationUnknown.length,
    same_second_fills: actions.filter((a) => a.same_second_fill === true).length,
    fill_age_uncheckable: actions.filter(
      (a) => a.kind === "FILL" && (!finite(a.rest_age_at_fill_minutes) || !finite(a.order_lineage_age_minutes)),
    ).length,
    writer_class_unmapped: actions.filter((a) => a.writer_class === SILENT)
      .length,
    violation_receipts: [
      ...new Set([...badPost, ...pre].map((p) => p.r.receipt)),
    ],
  };
  const outcome = {
    legs: {},
    pair_completed: false,
    pair_sum: SILENT,
    captured_cents: SILENT,
    best_capturable_cents: value(face.truth?.pair?.discount_cents),
    best_capturable_pair_sum_cents: value(face.truth?.pair?.sum_cents),
    capture_ratio: SILENT,
    definition:
      "Verified-span under-par completed-pair discount only; partial pair captures zero cents. Same-second conduct is graded separately.",
  };
  for (const leg of sides) {
    const fills = face.render.bid_actions.filter(
      (a) => a.leg === leg && a.kind === "FILL",
    );
    if (fills.length > 1)
      throw new Error(
        `Multiple credited fills for ${leg}; no aggregation rule supplied`,
      );
    const f = fills[0],
      ruler = face.truth?.legs?.[leg];
    const spanKnown =
      face.truth?.status === "OK" &&
      finite(face.truth.span_start_epoch) &&
      finite(face.truth.span_end_epoch) && finite(face.truth.bell_epoch);
    const valid = f
      ? spanKnown && finite(f.timestamp_epoch)
        ? f.timestamp_epoch >= face.truth.span_start_epoch &&
          f.timestamp_epoch < face.truth.span_end_epoch && f.timestamp_epoch < face.truth.bell_epoch
        : SILENT
      : false;
    outcome.legs[leg] = {
      filled: !!f,
      cents: f ? value(f.fill?.cents) : null,
      vs_floor_cents:
        f && ruler?.status === "OK"
          ? value(f.fill?.cents - ruler.floor_cents)
          : f
            ? SILENT
            : null,
      fill_epoch: f?.timestamp_epoch ?? null,
      valid_span_fill: valid,
      revalidation: f ? {
        ruler_bell_epoch: face.truth?.bell_epoch ?? null,
        span_start_epoch: face.truth?.span_start_epoch ?? null,
        span_end_epoch: face.truth?.span_end_epoch ?? null,
        at_or_after_span_start: spanKnown ? f.timestamp_epoch >= face.truth.span_start_epoch : SILENT,
        before_span_end: spanKnown ? f.timestamp_epoch < face.truth.span_end_epoch : SILENT,
        before_bell: spanKnown ? f.timestamp_epoch < face.truth.bell_epoch : SILENT,
        correction_ids: (face.truth?.applied_corrections ?? []).map((c) => c.correction_id),
      } : null,
      reason:
        f && valid === SILENT
          ? "NO_VERIFIED_FILL_SPAN"
          : f && !valid
            ? "FILL_OUTSIDE_VERIFIED_SPAN"
            : null,
    };
  }
  const olegs = Object.values(outcome.legs);
  outcome.pair_completed = olegs.every((l) => l.filled);
  outcome.pair_sum =
    outcome.pair_completed && olegs.every((l) => finite(l.cents))
      ? olegs.reduce((a, l) => a + l.cents, 0)
      : null;
  outcome.valid_pair_completed = olegs.some((l) => l.valid_span_fill === SILENT)
    ? SILENT
    : olegs.every((l) => l.valid_span_fill === true);
  if (outcome.valid_pair_completed !== SILENT)
    outcome.captured_cents =
      outcome.valid_pair_completed && finite(outcome.pair_sum)
        ? Math.max(0, 100 - outcome.pair_sum)
        : 0;
  if (
    finite(outcome.captured_cents) &&
    finite(outcome.best_capturable_cents) &&
    outcome.best_capturable_cents > 0
  )
    outcome.capture_ratio =
      outcome.captured_cents / outcome.best_capturable_cents;
  const result = operatorGrade(face, decisions, { sentence, macro, micro, hands, outcome }, rubric);
  const { grades, trade, pair, hard, letter, governing, lines } = result;
  const diagnostics = {
    sentence: `Q ${percent(sentence.share_q_authored_by_organ)} · X ${percent(sentence.share_x_authored_by_organ)} authored (token metric); Gate-1 certification ${sentence.gate_1_authorship_certification}`,
    oracle: sides.map((l) => `${l}: ${unit(micro.oracle_diagnostic.legs[l].mean_absolute_gap_cents, "¢")}`).join(" · "),
    timing: sides.map((l) => `${l}: first ${unit(micro.legs[l].first_eligible_full_span.timing_error_minutes, "m")}; remaining MAE ${unit(micro.legs[l].executable_future_print.mean_timing_error_minutes, "m")}`).join(" · "),
  };
  return {
    version: 3, event, provenance,
    SENTENCE: sentence, MACRO: macro, MICRO: micro, HANDS: hands, OUTCOME: outcome,
    TRADE: trade, PAIR: pair,
    LETTER: { letter, governing_section: governing, hard_failures: hard,
      section_grades: grades, rubric_status: rubric.status, rubric_id: rubric.rubric_id,
      capture_bonus_applied: false, safety_evidence_missing: result.safetyUnknown,
      performance_not_certification: true },
    display: {
      letter: letter === rubric.letter.no_offer_label ? rubric.letter.no_offer_display : letter,
      label: hard.length ? "Safety/named failure · cutoff-independent F" : rubric.status,
      governing,
      ruler_line: `Grading ruler: ${sides.map((l) => `${l} ${unit(face.truth?.legs?.[l]?.floor_cents, "¢")}`).join(" + ")} · ${unit(outcome.best_capturable_cents, "¢")} offered · ${(face.truth?.applied_corrections ?? []).length} filed corrections`,
      ruler_hover_lines: [
        `RULER — NOT AN OS INPUT · table ${face.truth?.table_commit ?? SILENT} · corrections ${face.truth?.corrections_commit ?? SILENT}`,
        `Bell ${face.truth?.bell_epoch ?? SILENT} · span [${face.truth?.span_start_epoch ?? SILENT}, ${face.truth?.span_end_epoch ?? SILENT})`,
        "Original rows, all corrections and per-fill eligibility remain in the grade JSON. No OS or trace changed.",
      ],
      diagnostic_line: diagnostics.sentence,
      diagnostic_hover_lines: [diagnostics.sentence, `Oracle mean gap (diagnostic): ${diagnostics.oracle}`,
        `Timing (diagnostic): ${diagnostics.timing}`,
        "Exact family, flips, authorship and full receipt error series remain in the JSON; none is silently certified."],
      sections: Object.entries(grades).map(([name, grade]) => ({
        name, mark: rubric.letter.pass_marks.includes(grade.letter) && !hard.length ? "✓" : "!",
        line: `${grade.letter} · ${lines[name]}`,
        hover_lines: [
          `${name}: ${grade.letter} · ${rubric.status}`,
          JSON.stringify(grade),
          name === "MICRO" ? `Oracle mean gap (diagnostic): ${diagnostics.oracle} · ${diagnostics.timing}`
            : name === "MACRO" ? `Flips (diagnostic): ${sides.map((l) => `${l} ${macro.operator_roles[l].flip_count}`).join(" · ")}`
              : name === "TRADE" ? `Ages: ${hands.rest_age_at_fill_minutes.map((a) => `${a.leg} lineage ${unit(a.order_lineage_age_minutes, "m")}, current price ${unit(a.current_price_age_minutes, "m")}`).join(" · ")}`
                : rubric.letter.aggregation,
        ],
      })),
    },
  };
}
