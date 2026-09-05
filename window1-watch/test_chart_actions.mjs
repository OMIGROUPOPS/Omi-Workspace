import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";
import {
  attachChartActions,
  readChartSources,
  tokenGloss,
} from "./chart_actions.mjs";
import { extendFace } from "./face_contract.mjs";
const here = path.dirname(fileURLToPath(import.meta.url));
const read = (id) =>
  unpackFace(
    JSON.parse(fs.readFileSync(path.join(here, "data", `${id}.face.json`))),
  );
const alt = read("KXATPMATCH-26JUL12ALTGAS"),
  urs = read("KXATPCHALLENGERMATCH-26JUL14URSPAL");

test("ALT's four exact reprices preserve raw reasons, winners, books and sentence fields", async () => {
  const reprices = alt.render.bid_actions.filter(
    (a) => a.leg === "ALT" && a.raw.action === "REPRICE_REST",
  );
  assert.deepEqual(
    reprices.map((a) => [a.old_cents, a.new_cents]),
    [
      [55, 49],
      [49, 55],
      [55, 49],
      [49, 45],
    ],
  );
  assert.deepEqual(
    reprices.map((a) => Number(a.t.toFixed(1))),
    [14.9, 23.5, 68.7, 69.2],
  );
  const sources = await readChartSources(alt, here);
  for (const a of reprices) {
    const s = sources.get(a.trace_row),
      d = s.derivations.find((d) => d.leg === a.leg);
    assert.equal(a.raw.reason, d.action.reason);
    assert.equal(a.raw.reason, "BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE");
    assert.equal(a.gloss.reason, "STORE SILENT");
    assert.equal(a.raw.winner_lane, d.winner_lane);
    assert.equal(a.raw.envelope_mode, d.envelope_mode);
    assert.deepEqual(a.book, s.books.ALT);
    assert.deepEqual(a.sentence, alt.os[a.receipt_index].legs.ALT.sentence);
    assert.ok(a.hover_lines.some((l) => l.includes(a.raw.reason)));
  }
  const rebuilt = structuredClone(alt);
  attachChartActions(rebuilt, sources);
  assert.deepEqual(rebuilt, alt);
});
test("GAS fill has recorded execution, triggering print, original PLACE age and truth-only floor delta", () => {
  const a = alt.render.bid_actions.find((a) => a.fill),
    f = a.fill;
  assert.equal(f.cents, 42);
  assert.equal(f.triggering_print_cents, 41);
  assert.equal(f.recorded_floor_cents, 38);
  assert.equal(f.floor_difference_cents, 4);
  assert.equal(f.floor_line, "4¢ above floor 38¢");
  assert.equal(f.rest_age_minutes, 0);
  assert.equal(
    f.summary,
    "GAS filled 42¢ · 2880.73m to bell · print 41¢ · rest had stood 0m",
  );
  const place = alt.render.bid_actions.find(
    (a) => a.receipt_id === f.place_receipt_id && a.leg === "GAS",
  );
  assert.deepEqual(f.placing_sentence, place.sentence);
  assert.equal(a.book, null);
  assert.equal(a.raw.reason, null); // No action.reason on a FILL_EVENT; do not borrow the PLACE reason.
  assert.notEqual(a.stack_offset_px, place.stack_offset_px);
});
test("other-game fills keep the original PLACE across reprices, and can be below a recorded ruler", () => {
  for (const a of urs.render.bid_actions.filter((a) => a.fill)) {
    const p = urs.render.bid_actions.find(
      (p) => p.receipt_id === a.fill.place_receipt_id && p.leg === a.leg,
    );
    assert.equal(
      a.fill.rest_age_minutes,
      (a.timestamp_epoch - p.timestamp_epoch) / 60,
    );
    assert.equal(p.raw.action, "PLACE_REST");
  }
  assert.equal(
    urs.render.bid_actions.find((a) => a.leg === "PAL" && a.fill).fill
      .floor_line,
    "1¢ below floor 40¢",
  );
});
test("approved token map and bed prefixes only; no conjectural gloss", () => {
  assert.equal(
    tokenGloss("INSUFFICIENT_AUTHORITY_NO_WRITER"),
    "no organ wrote this; the library prior was executed",
  );
  assert.equal(
    tokenGloss("LADDER_SHRINK_Q_CLIP_WRITER"),
    "a cheap ending died; bid stepped to the ladder",
  );
  assert.equal(
    tokenGloss("IMMUNITY_HOLD"),
    "frozen by the seat until its deadline",
  );
  for (const token of ["PAL_ATOMIC_Q_TEST", "GIU_TEST", "LAJSVA_TEST"])
    assert.equal(tokenGloss(token), "named hand (bed-only branch)");
  for (const token of [
    null,
    "BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE",
    "NEW_UNMAPPED_REASON",
  ])
    assert.equal(tokenGloss(token), "STORE SILENT");
});
test("HOLD without change is absent, HOLD with change is marked; cancel and uncredited disappearance are marked", () => {
  const f = structuredClone(alt);
  const template = f.os.find((r) => r.kind === "DECISION_STAGE");
  const cases = [
    ["PLACE_REST", null, 55],
    ["HOLD_REST", 55, 55],
    ["HOLD_REST", 55, 54],
    ["CANCEL_REST", 54, null],
    ["HOLD_REST", null, null],
    ["PLACE_REST", null, 53],
    [null, null, null],
  ];
  f.os = cases.map((_, i) => ({
    ...structuredClone(template),
    index: i,
    trace_row: i,
    receipt_id: `fixture-${i}`,
  }));
  const sources = new Map(
    cases.map(([action, old, target], i) => [
      i,
      {
        timestamp_epoch: i,
        standing: { ALT: { credited: false, standing_target_cents: old } },
        derivations: action
          ? [
              {
                leg: "ALT",
                action: {
                  action,
                  target_cents: target,
                  reason: "FIXTURE_UNKNOWN",
                },
              },
            ]
          : [],
      },
    ]),
  );
  const events = attachChartActions(f, sources);
  assert.deepEqual(
    events.map((a) => [a.kind, a.old_cents, a.new_cents]),
    [
      ["PLACE", null, 55],
      ["REPRICE", 55, 54],
      ["REMOVE", 54, null],
      ["PLACE", null, 53],
      ["REMOVE", 53, null],
    ],
  );
  assert.equal(events.at(-1).raw.action, null);
  assert.equal(events.at(-1).gloss.reason, "STORE SILENT");
});
test("full builder rest carry remains identical on both proof games", async () => {
  for (const original of [alt, urs]) {
    const rebuilt = structuredClone(original);
    await extendFace(rebuilt, { here, eventId: rebuilt.provenance.event_id });
    assert.deepEqual(rebuilt.os, original.os);
    const oldRestColumns = ["firstRest", "secondRest"];
    for (const key of oldRestColumns) {
      const before = original.render.columns.indexOf(key),
        after = rebuilt.render.columns.indexOf(key);
      assert.deepEqual(
        rebuilt.render.ticks.map((t) => t[after]),
        original.render.ticks.map((t) => t[before]),
      );
    }
  }
});
