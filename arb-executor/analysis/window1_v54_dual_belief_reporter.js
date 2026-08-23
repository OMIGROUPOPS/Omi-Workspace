"use strict";

const fs = require("fs");
const path = require("path");

function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function writeJson(file, value) { fs.writeFileSync(file, canonical(value), "utf8"); }
function writeText(file, value) { fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }

function compactTimeline(game) {
  const kept = [];
  let priorAction = null, priorCoherence = null, macroSeen = false, microSeen = false, microMicroSeen = false;
  for (const row of game.timeline) {
    const action = row.actions.map((item) => `${item.leg_id}:${item.action.action}:${item.action.target_cents ?? "NONE"}`).join("|");
    const firstResolved = (!macroSeen && row.layer_status.macro === "RESOLVED")
      || (!microSeen && row.layer_status.micro === "RESOLVED")
      || (!microMicroSeen && row.layer_status.micro_micro === "RESOLVED");
    if (!kept.length || firstResolved || row.coherence.status !== priorCoherence || action !== priorAction) kept.push(row);
    macroSeen ||= row.layer_status.macro === "RESOLVED";
    microSeen ||= row.layer_status.micro === "RESOLVED";
    microMicroSeen ||= row.layer_status.micro_micro === "RESOLVED";
    priorAction = action;
    priorCoherence = row.coherence.status;
  }
  const last = game.timeline.at(-1);
  if (last && kept.at(-1)?.receipt !== last.receipt) kept.push(last);
  return kept;
}

function emit(context) {
  const { output, storesPulled, corpus, storyResults, fillEvents, floorBreaks, lawViolations, allDerivations, targets } = context;
  const coherence = JSON.parse(fs.readFileSync(path.join(output, "COHERENCE_TIMELINES.json"), "utf8"));
  const deadlineScores = JSON.parse(fs.readFileSync(path.join(output, "BELIEF_DEADLINE_SCORING_TABLE.json"), "utf8"));
  const compact = Object.fromEntries(Object.entries(coherence.games).map(([eventId, game]) => [eventId, { first_coherence: game.first_coherence, ever_coherent: game.ever_coherent, timeline: compactTimeline(game) }]));
  const actions = Object.entries(compact).flatMap(([eventId, game]) => game.timeline.flatMap((row) => row.actions.map((item) => ({ event_id: eventId, leg_id: item.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, action: item.action, coherence: row.coherence, envelope: item.envelope, sentence_verbatim: item.sentence_verbatim }))));
  const receipt = {
    label: "V54_PHASE_CONDITIONED_LIVE_DEADLINE_PROCESS_FIRST",
    order: ["STORES_PULLED_WITH_LAYERS", "URSPAL_LAJSVA_LAYER_WALKS", "OWN_DEADLINE_SCORING", "GIUBAR_DANPRA_COHERENT_BASELINES", "ACTIONS_WITH_REASONS", "FILLS_AS_CONSEQUENCES", "DELTAS_AND_GATE_LAST"],
    stores_pulled_with_layers: {
      target_tape_rows: storesPulled.tick_rows_by_game,
      foundation: { games_served: corpus.foundation.rows, source_rows: corpus.foundation.index.rows, grain: "MINUTE", layers: ["MACRO", "MICRO"], micro_micro: false },
      range: { rows: corpus.counts.range_rows, grain: "RANGE_POLL", layers: ["MACRO", "MICRO"], micro_micro: false },
      historical: { rows: corpus.counts.historical_rows, grain: "EVENT/RANGE_POLL", layers: ["MACRO"], micro_micro: false },
      event_registry: { rows: corpus.counts.registry_rows, grain: "EVENT", layers: ["MACRO"], micro_micro: false },
      subsecond: { book_source: "EXTERNAL_CUSTODY_DUAL_BOOK", print_source: "EXTERNAL_CUSTODY_TRUE_PRINTS", grain: "SUBSECOND_RECEIPT", layers: ["MICRO_MICRO"] },
      odds: storesPulled.odds,
    },
    urspal_lajsva_layer_walks: Object.fromEntries(["KXATPCHALLENGERMATCH-26JUL14URSPAL", "KXATPCHALLENGERMATCH-26JUL14LAJSVA"].map((eventId) => [eventId, compact[eventId]])),
    own_deadline_scoring: { rows: deadlineScores.row_count, graded_rows: deadlineScores.graded_rows, hit_rows: deadlineScores.hit_rows, stale_deadline_emissions: deadlineScores.stale_deadline_emissions, all_fresh: deadlineScores.all_deadlines_fresh_and_not_before_emission },
    giubar_danpra_coherent_baselines: Object.fromEntries(["KXATPCHALLENGERMATCH-26JUL12GIUBAR", "KXATPMATCH-26JUL18DANPRA"].map((eventId) => [eventId, compact[eventId]])),
    actions_with_reasons: actions,
    fills_as_consequences: fillEvents,
    deltas_and_gate_last: { results: storyResults, floor_breaks: floorBreaks, law_violations: lawViolations, gate_pass: floorBreaks.length === 0 && lawViolations.length === 0 },
  };
  writeJson(path.join(output, "PROCESS_FIRST_CONFIRM_RECEIPT.json"), receipt);
  const walk = (eventId) => {
    const game = compact[eventId];
    return `### ${eventId}\n\nEver coherent: ${game.ever_coherent}. First coherence: ${JSON.stringify(game.first_coherence)}.\n\n${game.timeline.map((row) => `- ${row.timestamp_epoch} [${row.receipt}]: layers=${JSON.stringify(row.layer_status)}; coherence=${row.coherence.status}; predicted sum=${row.coherence.predicted_sum_cents ?? "UNKNOWN"}; spread=${row.coherence.spread_settle_bound_cents ?? "UNKNOWN"}. ${row.actions.map((item) => `${item.leg_id} ${item.action.action} ${item.action.target_cents ?? "NONE"}; sentence VERBATIM: ${item.sentence_verbatim}`).join(" || ")}`.trimEnd()).join("\n")}`;
  };
  const markdown = `# Conditioned-belief, live-deadline build — process-first confirmation

## 1. Stores pulled, with grain and layer

${Object.entries(storesPulled.tick_rows_by_game).map(([eventId, counts]) => `- ${eventId}: ${counts.total} tape rows (${counts.books} book, ${counts.prints} true-print); SUBSECOND/TICK receipts are the only MICRO-MICRO action source.`).join("\n")}
- Foundation: ${corpus.foundation.rows} games / ${corpus.foundation.index.rows} compact rows, MINUTE, MACRO/MICRO only.
- Range: ${corpus.counts.range_rows} rows, RANGE_POLL, MACRO/MICRO only.
- Historical: ${corpus.counts.historical_rows} rows, EVENT/RANGE_POLL, MACRO only.
- Registry: ${corpus.counts.registry_rows} rows, EVENT, MACRO only.
- Odds: ${targets.stories.map((eventId) => `${eventId}=RESOURCE-GAP`).join("; ")}.

## 2. URSPAL and LAJSVA, layer by layer

${walk("KXATPCHALLENGERMATCH-26JUL14URSPAL")}

${walk("KXATPCHALLENGERMATCH-26JUL14LAJSVA")}

## 3. Each prediction graded at its own live deadline

- ${deadlineScores.row_count} emitted predictions; ${deadlineScores.graded_rows} had a true print through their own deadline; ${deadlineScores.hit_rows} hit at-or-below the prediction; stale deadlines before emission=${deadlineScores.stale_deadline_emissions}; all deadline stamps fresh=${deadlineScores.all_deadlines_fresh_and_not_before_emission}.
- Full scoring rows: BELIEF_DEADLINE_SCORING_TABLE.json.

## 4. GIUBAR and DANPRA against their coherent baselines

- GIUBAR: ever coherent=${compact["KXATPCHALLENGERMATCH-26JUL12GIUBAR"].ever_coherent}; first coherence=${JSON.stringify(compact["KXATPCHALLENGERMATCH-26JUL12GIUBAR"].first_coherence)}.
- DANPRA: ever coherent=${compact["KXATPMATCH-26JUL18DANPRA"].ever_coherent}; first coherence=${JSON.stringify(compact["KXATPMATCH-26JUL18DANPRA"].first_coherence)}.

## 5. Actions with reasons

${actions.map((row) => `- ${row.event_id}|${row.leg_id} @ ${row.timestamp_epoch} [${row.receipt}]: ${row.action.action} ${row.action.target_cents ?? "NONE"}; ${row.action.reason}; coherence=${row.coherence.status}; envelope=${JSON.stringify(row.envelope)}.`).join("\n")}

## 6. Fills as consequences

${fillEvents.length ? fillEvents.map((row) => `- ${row.context.event_id}|${row.context.leg_id}: credited ${row.context.entry_cents}¢ at ${row.context.fill_timestamp_epoch} on standing rest ${row.context.prior_standing_target_cents}¢; triggering print ${row.context.triggering_print_price_cents}¢ [${row.context.execution_price_basis}]; trade receipt ${row.row_refs.join(",")}.`).join("\n") : "- None."}

## 7. Deltas and gate verdict — last

${storyResults.map((row) => `- ${row.event_id}: ${row.layered_dual_belief.completed ? `${row.layered_dual_belief.combined_entry_cents}¢, Δ${row.layered_dual_belief.delta_vs_100_cents}` : "PARTIAL"}.`).join("\n")}

Gate: ${floorBreaks.length === 0 && lawViolations.length === 0 ? "PASS" : `SELF-STOP (${floorBreaks.length ? "ratchet break" : "law violation"})`}.
`;
  writeText(path.join(output, "PROCESS_FIRST_CONFIRM.md"), markdown);
  return receipt;
}

module.exports = { emit };
