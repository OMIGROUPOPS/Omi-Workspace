import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";
import { cardGloss, plainCard } from "./plain_cards.mjs";
import { writerClass } from "./grade_contract.mjs";
import { readGradeRulers } from "./grade_rulers.mjs";

const data = new URL("./data/", import.meta.url);
const files = fs.readdirSync(data).filter((n) => n.startsWith("KX") && n.endsWith(".face.json"));
const json = (name) => JSON.parse(fs.readFileSync(new URL(name, data)));
test("cascade aliases, actual tokens, wildcard sources and veto precedence", () => {
  for (const token of ["POOL_FIRST_TICK", "POOL_FIRST-TICK-ONLY", "POOL_BASE",
    "POOL_CASCADE:FIRST-TICK-ONLY", "POOL_CASCADE:BASE", "POOL_CASCADE_WRITER"]) {
    assert.equal(writerClass([token]), "ORGAN");
    assert.ok(cardGloss(token));
  }
  assert.equal(writerClass(["ACTIVE_REST_HOLD", "POOL_BASE"]), "SEAT");
  assert.equal(writerClass(["PAL_ATOMIC_WRITER", "POOL_BASE"]), "HAND");
  assert.equal(cardGloss("POOL_UNKNOWN"), null);
  assert.equal(cardGloss("POOL_CASCADE:FILED_LAYER"), "the stored cascade layer supplied the forecast");
});

test("all five loaded games have four-line cards, mapped hands and measured MACRO", () => {
  assert.equal(files.length, 5);
  for (const file of files) {
    const face = unpackFace(json(file));
    const grade = json(file.replace(".face.json", ".grade.json"));
    assert.equal(grade.HANDS.writer_class_unmapped, 0, file);
    assert.equal(grade.LETTER.section_grades.HANDS.letter, "A", file);
    assert.notEqual(grade.LETTER.section_grades.MACRO.letter, "STORE SILENT", file);
    assert.equal(grade.MACRO.comparison_clock.bell_epoch, face.bench.bell_epoch);
    for (const leg of Object.values(grade.MACRO.legs)) {
      assert.equal(typeof leg.family_match, "boolean");
      assert.ok(leg.family_call_epoch <= grade.MACRO.comparison_clock.last_gate_epoch);
    }
    for (const a of face.render.bid_actions) {
      assert.equal(a.card_lines.length, 4);
      assert.deepEqual(a.card_lines, plainCard(a));
      assert.ok(!a.card_lines[1].includes("not translated yet"), a.card_lines.join(" / "));
    }
  }
});

test("GIUBAR keeps original, correction and campaign fields without selecting", () => {
  const rulers = readGradeRulers(fileURLToPath(new URL("..", import.meta.url)), "KXATPCHALLENGERMATCH-26JUL12GIUBAR");
  assert.equal(rulers.original_table.legs.BAR.floor_cents, 16);
  assert.equal(rulers.original_table.legs.GIU.floor_cents, 49);
  assert.equal(rulers.original_table.floor_sum_cents, 65);
  assert.deepEqual(rulers.original_table.campaign_ruler_columns, {});
  const correction = rulers.restated_rows[0];
  assert.equal(correction.legs.BAR.floor_cents, 27);
  assert.equal(correction.legs.GIU.floor_cents, 66);
  assert.equal(correction.floor_sum_cents, 93);
  assert.equal(correction.campaign_ruler_fields.game_ruler, "not complete");
  assert.match(correction.campaign_ruler_fields.leg_ruler.GIU, /close 66 - entry 69 = -3/);
  const grade = json("KXATPCHALLENGERMATCH-26JUL12GIUBAR.grade.json");
  assert.deepEqual(grade.RULER_COLUMNS, rulers);
  assert.equal(grade.OUTCOME.best_capturable_cents, 35); // unchanged, explicitly not a selection
});

test("ALT and GAS actual fills and the earlier missed GAS floor are unchanged", () => {
  const face = unpackFace(json("KXATPMATCH-26JUL12ALTGAS.face.json"));
  assert.equal(face.provenance.trace_sha256, "2a6af0af3f3c4602fed97782f7f736a2dff48f2c78eb9496101b25b564885439");
  const fills = face.render.bid_actions.filter((a) => a.kind === "FILL");
  assert.deepEqual(fills.map((a) => [a.leg, a.fill.cents, a.fill.triggering_print_cents]), [["ALT", 60, 60], ["GAS", 38, 38]]);
  // The true-print receipt is subsecond; the pinned truth row has lower precision.
  const atFloor = face.os.find((r) => r.kind === "DECISION_STAGE" && r.receipt === "ccfd87ed-a316-75af-a54c-854f3bd0ea8d");
  assert.equal(atFloor.standing.GAS.standing_target_cents, 37);
  const grade = json("KXATPMATCH-26JUL12ALTGAS.grade.json");
  assert.equal(grade.OUTCOME.captured_cents, 2);
  assert.equal(grade.OUTCOME.capture_ratio, 0.5);
  assert.equal(grade.SENTENCE.q_organ_leg_receipts, 130);
  assert.equal(grade.SENTENCE.leg_receipts_total, 168);
});
