// Replay-independent face regression receipt. Reads the committed stage files only.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";

const here = path.dirname(fileURLToPath(import.meta.url)), repo = path.dirname(here);
const baseline = "87049680809b07f878a2a1c454ccc309f8f2f24c";
const hash = (b) => crypto.createHash("sha256").update(b).digest("hex");
const json = (file) => JSON.parse(fs.readFileSync(path.join(here, "data", file)));
const previous = (file) => JSON.parse(execFileSync("git", ["show", `${baseline}:window1-watch/data/${file}`],
  { cwd: repo, maxBuffer: 32 * 1024 * 1024 }));
const cleanDisplay = (face) => {
  const copy = structuredClone(face);
  for (const a of copy.render.bid_actions)
    for (const key of ["card_lines", "details_lines", "hover_lines", "gloss"])
      delete a[key];
  return copy;
};
const output = { baseline_commit: baseline, scope: "FACE ONLY", games: [] };
for (const file of fs.readdirSync(path.join(here, "data")).filter((f) => f.startsWith("KX") && f.endsWith(".face.json"))) {
  const face = unpackFace(json(file)), before = unpackFace(previous(file));
  assert.deepEqual(cleanDisplay(face), cleanDisplay(before));
  const gradeFile = file.replace(".face.json", ".grade.json"), grade = json(gradeFile), oldGrade = previous(gradeFile);
  for (const key of ["SENTENCE", "MICRO", "OUTCOME"])
    assert.deepEqual(grade[key], oldGrade[key]);
  assert.equal(grade.provenance.stage_inputs_sha256, oldGrade.provenance.stage_inputs_sha256);
  assert.equal(grade.HANDS.writer_class_unmapped, 0);
  const historyPath = `grades/${grade.event}/${grade.provenance.os_sha256.slice(0, 8)}_${grade.provenance.trace_sha256.slice(0, 8)}.json`;
  const oldHistory = previous(historyPath), history = json(historyPath);
  assert.deepEqual(history.grades.slice(0, oldHistory.grades.length), oldHistory.grades);
  output.games.push({ event: grade.event, grade_sha256: hash(fs.readFileSync(path.join(here, "data", gradeFile))),
    letter: grade.LETTER.letter, sections: grade.LETTER.section_grades,
    macro: grade.MACRO, unmapped_writers: grade.HANDS.writer_class_unmapped,
    invariants: "OS, tape, truth, bench joins, marker geometry, fills/rests, SENTENCE/MICRO/OUTCOME and prior history snapshots unchanged" });
  if (grade.RULER_COLUMNS.restated_rows.length)
    output.games.at(-1).ruler_columns = grade.RULER_COLUMNS;
  if (!grade.event.endsWith("ALTGAS")) continue;
  const actions = face.render.bid_actions;
  const readStage = (r) => JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(here, "." + r.detail_url + ".gz")))).row;
  const actionByReceipt = new Map(actions.map((a) => [`${a.receipt}:${a.leg}`, a]));
  output.altgas = {
    event: grade.event, os_sha256: grade.provenance.os_sha256, trace_sha256: grade.provenance.trace_sha256,
    grade_card: { letter: grade.LETTER, lines: grade.display.sections },
    per_gate: face.os.filter((r) => r.receipt.includes("|ATLAS_GATE|")).map((r) => {
      const raw = readStage(r);
      return { minutes_to_bell: r.minutesToBell, receipt: r.receipt, legs: Object.fromEntries(face.legs.map((leg) => {
        const state = raw.reads.half_pair_state.value.legs[leg];
        const action = raw.derivations?.find((d) => d.leg_id === leg)?.action;
        const emitted = ["PLACE_REST", "REPRICE_REST"].includes(action?.action);
        const license = emitted ? r.receipt : state.standing_license_receipt;
        const author = actionByReceipt.get(`${license}:${leg}`);
        return [leg, { rest_cents: state.credited ? null : emitted ? action.target_cents : state.standing_target_cents,
          credited: state.credited, entry_cents: state.entry_cents,
          rest_writer: author?.sentence?.q_author ?? null,
          rest_license_receipt: license ?? null,
          receipt_q_author: r.legs[leg]?.sentence?.q_author ?? null,
          action: action?.action ?? "CREDITED_LEG_READ_NO_ORDER_EMISSION" }];
      })) };
    }),
    actions: actions.map((a) => ({ leg: a.leg, minutes_to_bell: a.minutes_to_bell, kind: a.kind,
      old_cents: a.old_cents, new_cents: a.new_cents, receipt: a.receipt,
      writer: a.sentence?.q_author ?? null, raw: a.raw,
      fill: a.fill ? { cents: a.fill.cents, print_cents: a.fill.triggering_print_cents,
        rest_age_from_place_minutes: a.fill.rest_age_minutes } : null })),
    missed_first_gas_floor: face.os.filter((r) => r.kind === "FLOOR_PRINT_DECISION_INSTANT")
      .map(readStage).filter((r) => r.leg_id === "GAS" && r.print_price_cents === face.truth.legs.GAS.floor_cents
        && r.floor_relation === "NEW_TRUE_TRADE_LOW").map((r) => {
          const stage = face.os.find((s) => s.kind === "DECISION_STAGE" && s.receipt === r.stage_receipt);
          const decision = readStage(stage);
          const d = decision.derivations.find((v) => v.leg_id === "GAS");
          return { print: r, minutes_to_bell: stage.minutesToBell,
            standing_cents: decision.reads.half_pair_state.value.legs.GAS.standing_target_cents,
            action: d.action, target_cents: d.derivation.pricing_authority.target_cents,
            writer: decision.layers.micro.context.beliefs.GAS.q_author };
        }),
  };
}
const file = path.join(here, "proof", "cascade-face-fix-receipt.json");
fs.writeFileSync(file, JSON.stringify(output, null, 2) + "\n");
for (const game of output.games)
  console.log(`${game.event} · HANDS ${game.sections.HANDS.letter} · MACRO ${game.sections.MACRO.letter} · immutable run fields PASS`);
console.log(JSON.stringify(output.altgas.per_gate.map((r) => ({ gate: Math.round(r.minutes_to_bell), legs: r.legs })), null, 2));
console.log(file);
