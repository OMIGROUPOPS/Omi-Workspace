import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { unpackFace } from "./face_encoding.mjs";
import {
  cardGloss,
  plainCard,
  deadlineClock,
  poolAccuracy,
  POOL_NOTE,
} from "./plain_cards.mjs";
const read = (name) =>
  JSON.parse(fs.readFileSync(new URL(name, import.meta.url)));
const alt = unpackFace(read("./data/KXATPMATCH-26JUL12ALTGAS.face.json"));
const ur = unpackFace(
  read("./data/KXATPCHALLENGERMATCH-26JUL14URSPAL.face.json"),
);
test("all 64 observed card tokens across five custody games have translations", () => {
  const inventory = read("./proof/card-token-inventory.json");
  assert.equal(Object.keys(inventory.games).length, 5);
  assert.equal(Object.keys(inventory.tokens).length, 64);
  assert.deepEqual(
    Object.keys(inventory.tokens).filter((t) => !cardGloss(t)),
    [],
  );
});
test("all loaded action cards have four stored English lines and square bid markers", () => {
  for (const face of [alt, ur])
    for (const a of face.render.bid_actions) {
      assert.equal(a.card_lines.length, 4);
      assert.ok(
        a.card_lines.every((l) => typeof l === "string" && !l.includes("\n")),
      );
      assert.equal(a.glyph, a.fill ? "●" : "▪");
      assert.ok(!a.card_lines[1].includes("not translated yet"));
      assert.ok(a.details_lines.some((l) => l.includes(a.raw.action)));
      assert.deepEqual(a.card_lines, plainCard(a));
    }
});
test("the four ALT reprices use actual forecast deadlines, never the legacy X cents", () => {
  const actions = alt.render.bid_actions.filter(
    (a) => a.leg === "ALT" && a.raw.action === "REPRICE_REST",
  );
  assert.deepEqual(
    actions.map((a) => a.card_lines[0]),
    [
      "ALT · Moved bid 55¢ → 49¢",
      "ALT · Moved bid 49¢ → 55¢",
      "ALT · Moved bid 55¢ → 49¢",
      "ALT · Moved bid 49¢ → 45¢",
    ],
  );
  assert.deepEqual(
    actions.map((a) => a.card_lines[2]),
    [
      "Believed: ALT at 59¢ now, should reach 49¢ by 49:34 to bell",
      "Believed: ALT at 58¢ now, should reach 55¢ by 4:16 to bell",
      "Believed: ALT at 58¢ now, should reach 49¢ by 1:18 to bell",
      "Believed: ALT at 58¢ now, should reach 45¢ by 0:04 to bell",
    ],
  );
  assert.equal(
    actions[0].card_lines[1],
    "Why: the library aimed at 49¢; ALT's own trading didn't change it",
  );
  assert.equal(
    actions[1].card_lines[1],
    "Why: the library aimed at 55¢, adjusted by ALT's own trading",
  );
  assert.equal(
    actions[0].card_lines[3],
    "Book then: 57 / 58, last 59 · 3395.68m",
  );
});
test("GAS fill uses its PLACE sentence and actual print, floor difference and age", () => {
  const a = alt.render.bid_actions.find((a) => a.fill);
  assert.deepEqual(a.card_lines, [
    "GAS · Filled at 42¢",
    "Why: bid was sitting at 42¢ when a 41¢ trade printed",
    "Believed: GAS at 42¢ now, should reach 42¢ by 1:52 to bell",
    "4¢ above the recorded floor (38¢) · rest stood 0m",
  ]);
});
test("untranslated future token is explicit; missing clock is not filled with phase cents", () => {
  const a = structuredClone(alt.render.bid_actions[0]);
  a.raw.reason = "FUTURE_TOKEN";
  a.deadline = null;
  assert.equal(plainCard(a)[1], "Why: not translated yet (FUTURE_TOKEN)");
  assert.ok(plainCard(a)[2].endsWith("by STORE SILENT"));
  assert.equal(
    deadlineClock({ predicted_minutes_to_bell: 60 }),
    "1:00 to bell",
  );
  assert.equal(
    deadlineClock({ deadline: { deadline_minutes_to_bell: -1 } }),
    "STORE SILENT",
  );
});
test("pool accuracy suppresses low ESS, preserves the boundary and raw numbers", () => {
  const sample = { status: "OK", ess: 9.999, share: 0.5 };
  assert.deepEqual(poolAccuracy(sample), {
    label: "—",
    hover_note: "too few games to trust (ESS 9.999)",
    meter_percent: null,
  });
  assert.deepEqual(sample, { status: "OK", ess: 9.999, share: 0.5 });
  assert.deepEqual(poolAccuracy({ ...sample, ess: 10 }), {
    label: "50.00%",
    hover_note: POOL_NOTE,
    meter_percent: 50,
  });
  assert.equal(poolAccuracy({ ...sample, ess: null }).label, "STORE SILENT");
  for (const f of [alt, ur])
    for (const c of f.render.checkpoints)
      if (c.bench)
        assert.deepEqual(c.bench.pool_accuracy, poolAccuracy(c.bench.validity));
});
