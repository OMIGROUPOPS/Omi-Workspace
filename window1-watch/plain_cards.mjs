// Builder-only text: FIELDS.md is the translation table, not executable instructions.
import fs from "node:fs";
const document = fs.readFileSync(
  new URL("./FIELDS.md", import.meta.url),
  "utf8",
);
const section = document
  .split("<!-- plain-card-gloss:start -->")[1]
  ?.split("<!-- plain-card-gloss:end -->")[0];
if (!section) throw new Error("FIELDS.md has no plain-card glossary");
export const CARD_GLOSSES = Object.fromEntries(
  section
    .split(/\r?\n/)
    .filter((l) => l.startsWith("| ") && !l.startsWith("| Token"))
    .map((l) => {
      const cells = l.split("|").map((c) => c.trim());
      return [cells[1], cells[2]];
    }),
);
export const POOL_NOTE =
  "Of the past games the bench pool was using at this gate, the share that called the last hour's move on both sides within 1¢. Bench measurement — the OS doesn't have this organ yet.";
const finite = (n) => typeof n === "number" && Number.isFinite(n);
const number = (n) =>
  finite(n) ? String(Number(n.toFixed(2))) : "STORE SILENT";
const cents = (n) => (finite(n) ? `${n}¢` : "STORE SILENT");
export function cardGloss(token) {
  if (Object.hasOwn(CARD_GLOSSES, token)) return CARD_GLOSSES[token];
  for (const prefix of ["PAL_ATOMIC_", "GIU_", "LAJSVA_"])
    if (token?.startsWith(prefix)) return CARD_GLOSSES[prefix + "*"];
  return null;
}
export function deadlineClock(deadline) {
  const m =
    deadline?.deadline?.deadline_minutes_to_bell ??
    deadline?.predicted_minutes_to_bell;
  if (!finite(m) || m < 0) return "STORE SILENT";
  // Whole-minute display only; never interpret phase-projection cents as time.
  const whole = Math.trunc(m);
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")} to bell`;
}
function beliefLine(leg, sentence, deadline) {
  return `Believed: ${leg} at ${cents(sentence?.P)} now, should reach ${cents(sentence?.Q)} by ${deadlineClock(deadline)}`;
}
function why(a) {
  const s = a.sentence;
  const tokens = [
    a.raw.reason,
    a.raw.winner_lane,
    a.raw.envelope_mode,
    s?.q_author,
    s?.authority_source,
    s?.x_author,
    s?.status,
    a.raw.action,
  ].filter(Boolean);
  const unknown = tokens.find((t) => !cardGloss(t));
  if (unknown) return `not translated yet (${unknown})`;
  if (a.raw.reason === "BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE") {
    if (
      s?.q_author === "PRIOR_ONLY" &&
      s?.authority_source ===
        "ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET"
    )
      return `the library aimed at ${cents(s.Q)}; ${a.leg}'s own trading didn't change it`;
    if (s?.q_author === "PRIOR_REWEIGHTED_BY_OWN_WALK")
      return `the library aimed at ${cents(s.Q)}, adjusted by ${a.leg}'s own trading`;
    if (s?.q_author === "OVERLAP_MEMBERS")
      return `similar games pointed to ${cents(s.Q)}`;
  }
  if (
    a.raw.reason === "Q_MOVE_LICENSED_BY_CANDIDATE_FINAL_FLOOR_LADDER_SHRINK"
  ) {
    const direction =
      finite(a.old_cents) && finite(a.new_cents) && a.old_cents !== a.new_cents
        ? a.new_cents < a.old_cents
          ? "down"
          : "up"
        : "to";
    return `a cheap ending died; bid stepped ${direction} the ladder`;
  }
  return (
    cardGloss(a.raw.reason) ??
    cardGloss(a.raw.winner_lane) ??
    "not translated yet (STORE SILENT)"
  );
}
export function plainCard(a) {
  const action = a.fill
    ? `Filled at ${cents(a.fill.cents)}`
    : a.kind === "PLACE"
      ? `Placed bid at ${cents(a.new_cents)}`
      : a.kind === "REMOVE"
        ? "Pulled bid"
        : `Moved bid ${cents(a.old_cents)} → ${cents(a.new_cents)}`;
  if (a.fill) {
    const f = a.fill,
      delta = f.floor_difference_cents;
    return [
      `${a.leg} · ${action}`,
      `Why: bid was sitting at ${cents(f.cents)} when a ${cents(f.triggering_print_cents)} trade printed`,
      beliefLine(a.leg, f.placing_sentence, f.placing_deadline),
      `${finite(delta) ? `${number(Math.abs(delta))}¢ ${delta < 0 ? "below" : "above"} the recorded floor (${cents(f.recorded_floor_cents)})` : "STORE SILENT — no recorded floor"} · rest stood ${number(f.rest_age_minutes)}m`,
    ];
  }
  return [
    `${a.leg} · ${action}`,
    `Why: ${why(a)}`,
    beliefLine(a.leg, a.sentence, a.deadline),
    `Book then: ${number(a.book?.bid_cents)} / ${number(a.book?.ask_cents)}, last ${number(a.book?.last_trade_cents)} · ${number(a.minutes_to_bell)}m`,
  ];
}
export function poolAccuracy(validity) {
  const ess = validity?.ess,
    share = validity?.share;
  const low = finite(ess) && ess < 10;
  const usable =
    finite(ess) && ess >= 10 && validity?.status === "OK" && finite(share);
  return {
    label: low ? "—" : usable ? `${(share * 100).toFixed(2)}%` : "STORE SILENT",
    hover_note: low ? `too few games to trust (ESS ${ess})` : POOL_NOTE,
    meter_percent: usable ? share * 100 : null,
  };
}
export function attachPoolAccuracy(face) {
  face.render.pool_accuracy = {
    heading: "POOL ACCURACY · bench only",
    hover_note: POOL_NOTE,
    absent_label: "STORE SILENT",
  };
  for (const c of face.render.checkpoints)
    if (c.bench) c.bench.pool_accuracy = poolAccuracy(c.bench.validity);
}
