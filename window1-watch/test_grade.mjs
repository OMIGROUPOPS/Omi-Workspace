import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import {
  gradeFace,
  writerClass,
  scanNamed,
  SILENT,
  worstLetter,
} from "./grade_contract.mjs";
import { appendHistory } from "./build_grade.mjs";
const rubric = JSON.parse(
  await fs.readFile(new URL("./grade_rubric.json", import.meta.url)),
);
function fixture() {
  const face = {
    legs: ["ABC", "XYZ"],
    provenance: { event_id: "TEST" },
    formation_end_epoch: 100,
    bell: { timestamp_epoch: 1000 },
    truth: {
      status: "OK",
      span_start_epoch: 100,
      span_end_epoch: 1000,
      legs: {
        ABC: { status: "OK", floor_cents: 58, minutes_to_bell: 8 },
        XYZ: { status: "OK", floor_cents: 38, minutes_to_bell: 2 },
      },
      pair: { sum_cents: 96, discount_cents: 4 },
    },
    bench: { clock_status: "ALIGNED", label: "STALE LIBRARY" },
    render: {
      checkpoints: [{ minutesToBell: 10 }, { minutesToBell: 5 }],
      bid_actions: [],
    },
  };
  const d = (q, mtb) => ({
    has_sentence: true,
    q_present: true,
    x_present: true,
    q_author: "OVERLAP_MEMBERS",
    x_author: "OVERLAP_MEMBER_FLOOR_FRACTIONS",
    tokens: ["OVERLAP_MEMBERS"],
    family: "DRIFT_UP",
    q50: q,
    floor_mtb: mtb,
    formation_end: 100,
    ask: 60,
  });
  const decisions = [
    { epoch: 300, receipt: "a", legs: { ABC: d(58, 8), XYZ: d(38, 2) } },
    { epoch: 600, receipt: "b", legs: { ABC: d(58, 8), XYZ: d(38, 2) } },
  ];
  return { face, decisions };
}
function run(f, named = new Map(), bench = null) {
  return gradeFace(f.face, f.decisions, named, bench, rubric, {});
}
test("authorship uses actual leg decisions, not carried display states", () => {
  const f = fixture();
  delete f.decisions[1].legs.XYZ;
  f.decisions[0].legs.XYZ.q_author = "PRIOR_ONLY";
  const g = run(f);
  assert.equal(g.SENTENCE.leg_receipts_total, 3);
  assert.equal(g.SENTENCE.share_q_authored_by_organ, 2 / 3);
  assert.equal(g.SENTENCE.receipts_with_sentence, 1);
});
test("named symbols disqualify writers; identity metadata and library IDs do not", () => {
  const tokens = [];
  scanNamed(
    {
      event_id: "TEST",
      leg_id: "PAL",
      member: { event_id: "KX-XYZ" },
      winner: { lane: "PAL_ATOMIC_WRITER" },
      reason: "XYZ_EVENT_HAND",
    },
    ["ABC", "XYZ"],
    "TEST",
    (t) => tokens.push(t),
  );
  assert.deepEqual(tokens, ["PAL_ATOMIC_WRITER", "XYZ_EVENT_HAND"]);
  const f = fixture();
  f.decisions[0].legs.ABC.tokens = ["PAL_ATOMIC_WRITER"];
  const g = run(
    f,
    new Map([["PAL_ATOMIC_WRITER", { token: "PAL_ATOMIC_WRITER" }]]),
  );
  assert.equal(g.LETTER.letter, "F");
  assert.ok(g.LETTER.hard_failures.includes("SENTENCE: named tokens"));
});

test("PRIOR_REWEIGHTED_BY_OWN_WALK is a non-organ Q badge, without changing X", () => {
  const f = fixture();
  for (const row of f.decisions)
    for (const leg of Object.values(row.legs))
      leg.q_author = "PRIOR_REWEIGHTED_BY_OWN_WALK";
  const g = run(f);
  assert.equal(g.SENTENCE.q_organ_leg_receipts, 0);
  assert.equal(g.SENTENCE.leg_receipts_total, 4);
  assert.equal(g.SENTENCE.share_q_authored_by_organ, 0);
  assert.equal(g.SENTENCE.share_x_authored_by_organ, 1);
  assert.equal(g.SENTENCE.author_counts.q.PRIOR_REWEIGHTED_BY_OWN_WALK, 4);
  assert.ok(
    g.SENTENCE.non_organ_q_authors.includes("PRIOR_REWEIGHTED_BY_OWN_WALK"),
  );
});
test("writer table precedence and unknowns", () => {
  assert.equal(
    writerClass(["LADDER_SHRINK_Q_CLIP_WRITER", "PAL_ATOMIC_WRITER"]),
    "HAND",
  );
  assert.equal(writerClass(["PREDICTION_SEAT_WRITER"]), "SEAT");
  assert.equal(writerClass(["OVERLAP_MEMBERS"]), "ORGAN");
  assert.equal(writerClass(["UNMAPPED"]), SILENT);
  assert.equal(writerClass([], true), "SAME_SECOND");
});
test("held gate requires every remaining call and cannot use future decisions", () => {
  const f = fixture();
  let g = run(f);
  assert.equal(g.MICRO.legs.ABC.first_gate_within_2c_and_held, 10);
  f.decisions[1].legs.ABC.q50 = 50;
  g = run(f);
  assert.equal(g.MICRO.legs.ABC.first_gate_within_2c_and_held, null);
  f.decisions[1].legs.ABC.q50 = null;
  g = run(f);
  assert.equal(g.MICRO.legs.ABC.floor_error_cents, SILENT);
  f.decisions.push({
    epoch: 950,
    receipt: "future",
    legs: { ABC: { q50: 58 } },
  });
  assert.equal(run(f).MICRO.legs.ABC.floor_error_cents, SILENT);
});
test("only bound aligned bench labels and pool data are used", () => {
  const f = fixture();
  const gate = {
    validity: { ess: 9, weighted_share: 0.5, status: "OK" },
    rules: {
      BASE: {
        sides: {
          favorite: {
            realized_family: "DRIFT_UP",
            family: { top: "SLEEPER" },
            status: "OK",
            ess: 20,
          },
        },
      },
    },
  };
  const bench = {
    events: {
      TEST: {
        event_id: "TEST",
        first_tick: { favorite: "ABC", underdog: "XYZ" },
        gates: { 5: gate },
      },
    },
  };
  let g = run(f, new Map(), bench);
  assert.equal(g.MACRO.legs.ABC.realized_family, "DRIFT_UP");
  assert.equal(g.MACRO.pile_ess_at_last_gate, 9);
  f.face.bench.clock_status = "MISMATCH";
  g = run(f, new Map(), bench);
  assert.equal(g.MACRO.legs.ABC.realized_family, SILENT);
  assert.equal(g.MACRO.pile_ess_at_last_gate, SILENT);
});
test("post-only and preformation audit actual placement rows, not holds", () => {
  const f = fixture();
  f.decisions[0].legs.ABC.action = { action: "PLACE_REST", target_cents: 60 };
  f.decisions[0].epoch = 99;
  const g = run(f);
  assert.equal(g.HANDS.post_only_violations, 1);
  assert.equal(g.HANDS.pre_formation_placements, 1);
  assert.equal(g.LETTER.letter, "F");
  f.decisions[0].legs.ABC.ask = null;
  assert.equal(run(f).HANDS.post_only_violations, SILENT);
});
test("span-bound capture excludes bell and partials; same timestamp forces F", () => {
  const f = fixture();
  const fill = (leg, cents, time, age) => ({
    kind: "FILL",
    leg,
    receipt: leg,
    timestamp_epoch: time,
    raw: { action: "FILL_EVENT" },
    fill: {
      cents,
      rest_age_minutes: age,
      place_receipt: "a",
      floor_difference_cents: 0,
    },
  });
  f.face.render.bid_actions = [fill("ABC", 58, 500, 0)];
  let g = run(f);
  assert.equal(g.OUTCOME.captured_cents, 0);
  assert.equal(g.LETTER.letter, "F");
  f.face.render.bid_actions.push(fill("XYZ", 38, 1000, 10));
  g = run(f);
  assert.equal(g.OUTCOME.pair_sum, 96);
  assert.equal(g.OUTCOME.captured_cents, 0);
  f.face.render.bid_actions[1].timestamp_epoch = 999;
  g = run(f);
  assert.equal(g.OUTCOME.captured_cents, 4);
  assert.equal(g.OUTCOME.capture_ratio, 1);
  f.face.truth.status = "UNKNOWN";
  assert.equal(run(f).OUTCOME.captured_cents, SILENT);
});
test("missing rubric section is not an A; demonstrated F still dominates", () => {
  assert.equal(worstLetter(["A", SILENT], rubric), SILENT);
  assert.equal(worstLetter(["F", SILENT], rubric), "F");
  assert.match(rubric.status, /PLACEHOLDER/);
});
test("history retains repeated hashes and earlier snapshots", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "face-grade-test-"));
  const g = run(fixture());
  g.provenance = {
    os_sha256: "a".repeat(64),
    trace_sha256: "b".repeat(64),
    os_commit: "commit",
    os_commit_order: 20,
  };
  await appendHistory(root, g, "2026-09-06T00:00:00Z");
  await appendHistory(
    root,
    { ...g, LETTER: { ...g.LETTER, letter: "B" } },
    "2026-09-06T00:01:00Z",
  );
  const history = JSON.parse(
    await fs.readFile(path.join(root, "grades/TEST/aaaaaaaa_bbbbbbbb.json")),
  );
  const index = JSON.parse(
    await fs.readFile(path.join(root, "grades/index.json")),
  );
  assert.equal(history.grades.length, 2);
  assert.equal(history.grades[0].LETTER.letter, g.LETTER.letter);
  assert.equal(history.grades[1].LETTER.letter, "B");
  assert.equal(index.grades.length, 2);
  assert.ok(index.grades[0].x < index.grades[1].x);
});
test("real proofs preserve facts, source citations and missing fields", async () => {
  const read = async (e) =>
    JSON.parse(
      await fs.readFile(new URL(`./data/${e}.grade.json`, import.meta.url)),
    );
  const alt = await read("KXATPMATCH-26JUL12ALTGAS"),
    ur = await read("KXATPCHALLENGERMATCH-26JUL14URSPAL");
  assert.equal(alt.SENTENCE.share_q_authored_by_organ, 0);
  assert.equal(alt.SENTENCE.q_organ_leg_receipts, 0);
  assert.equal(alt.SENTENCE.leg_receipts_total, 155);
  assert.equal(alt.SENTENCE.author_counts.q.PRIOR_REWEIGHTED_BY_OWN_WALK, 18);
  assert.equal(alt.SENTENCE.share_x_authored_by_organ, 0);
  assert.equal(alt.OUTCOME.captured_cents, 0);
  assert.equal(alt.OUTCOME.best_capturable_cents, 4);
  assert.equal(alt.HANDS.same_second_fills, 1);
  assert.equal(alt.LETTER.letter, "F");
  assert.ok(
    ur.SENTENCE.named_tokens_found.some((t) => t.startsWith("PAL_ATOMIC")),
  );
  assert.equal(ur.LETTER.letter, "F");
  assert.equal(ur.OUTCOME.legs.PAL.valid_span_fill, false);
  assert.equal(ur.OUTCOME.pair_sum, 97);
  assert.equal(ur.OUTCOME.captured_cents, 0);
  assert.equal(ur.MACRO.pile_ess_at_last_gate, SILENT);
  for (const g of [alt, ur]) {
    assert.equal(Object.keys(g.receipt.citations).length, 4);
    assert.equal(g.HANDS.writer_class_unmapped, 0);
  }
});
