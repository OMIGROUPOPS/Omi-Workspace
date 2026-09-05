import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { packFace, unpackFace } from "./face_encoding.mjs";
import { bindCustody, extendFace } from "./face_contract.mjs";
const here = path.dirname(fileURLToPath(import.meta.url));
async function read(event) {
  return unpackFace(
    JSON.parse(
      await fs.readFile(path.join(here, "data", `${event}.face.json`)),
    ),
  );
}
const altId = "KXATPMATCH-26JUL12ALTGAS",
  ursId = "KXATPCHALLENGERMATCH-26JUL14URSPAL";
test("dictionary round trip is exact, including null and repeated nested objects", () => {
  const original = {
    os: [
      {
        value: null,
        text: "stored sentence ".repeat(40),
        details: { n: 0, s: "stored sentence ".repeat(40) },
      },
      {
        value: null,
        text: "stored sentence ".repeat(40),
        details: { n: 0, s: "stored sentence ".repeat(40) },
      },
    ],
  };
  assert.deepEqual(unpackFace(packFace(original)).os, original.os);
});
test("historical custody mismatch is silent, never the current OS hash", async () => {
  const result = await bindCustody(
    "C:/tmp/v54_altgas_extra_2dfb5b0a_20260902_run2_custody/REPAIR_FOUR_GAME_TRACE.jsonl.gz",
    "not-the-bound-trace",
  );
  assert.equal(result.os_sha256, null);
});
test("requested actual rest/fill values and inspector are unchanged", async () => {
  const alt = await read(altId),
    urs = await read(ursId);
  assert.match(alt.provenance.trace_sha256, /^c2fe78f2/);
  assert.match(urs.provenance.trace_sha256, /^ab2345de/);
  assert.equal(alt.render.verification.ALT.first_rest.cents, 55);
  assert.equal(alt.render.verification.GAS.first_fill.cents, 42);
  assert.equal(urs.render.verification.PAL.first_rest.cents, 39);
  assert.equal(urs.render.verification.PAL.first_fill.cents, 39);
  const detail = JSON.parse(
    zlib.gunzipSync(
      await fs.readFile(
        path.join(
          here,
          alt.render.verification.ALT.first_rest.detail_url.slice(1),
        ) + ".gz",
      ),
    ),
  );
  const row = detail.row.derivations.find((d) => d.leg_id === "ALT");
  assert.equal(row.action.action, "PLACE_REST");
  assert.equal(
    row.layered_dual_belief.decision_arbitration.winner.lane,
    "INSUFFICIENT_AUTHORITY_NO_WRITER",
  );
  assert.equal(
    row.derivation.pricing_authority.authority_source,
    "ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET",
  );
  assert.deepEqual(
    detail.inspector.legs.find((d) => d.leg_id === "ALT").lanes_and_winner,
    row.layered_dual_belief.decision_arbitration,
  );
});
test("URSPAL clock mismatch cannot light validity; 480 is not a playable gate", async () => {
  const face = await read(ursId),
    gate = face.render.checkpoints.find((g) => g.minutesToBell === 480);
  assert.equal(face.bench.clock_status, "CLOCK_MISMATCH_STORE_SILENT");
  assert.equal(face.bench.clock_delta_seconds, 2853);
  assert.equal(gate.playable, false);
  assert.equal(gate.bench, null);
  assert.ok(face.first_tick.mtb_first < 480);
  assert.ok(gate.frame < face.render.play_start_frame);
});
test("all frame selections are causal and rests clear on fills; missing members stay null", async () => {
  for (const id of [altId, ursId]) {
    const face = await read(id),
      c = face.render.columns;
    for (const row of face.os)
      assert.ok(
        face.render.ticks.some(
          (t) => t[c.indexOf("receipt_index")] === row.index,
        ),
        "Every receipt has a distinct selectable state",
      );
    for (let i = 1; i < face.os.length; i++) {
      const a = face.os[i - 1],
        b = face.os[i];
      if (a.t === b.t)
        assert.ok(
          a.trace_row < b.trace_row,
          "Equal-time receipts preserve trace order",
        );
    }
    for (const values of face.render.ticks) {
      const f = Object.fromEntries(c.map((k, i) => [k, values[i]]));
      if (f.receipt_index != null)
        assert.ok(face.os[f.receipt_index].t <= f.hours);
    }
    for (const leg of face.legs) {
      const fill = face.os.find((r) => r.legs[leg]?.fill);
      if (fill) assert.equal(fill.display.legs[leg].current_rest, null);
    }
    for (const r of face.os)
      for (const leg of face.legs)
        if (r.legs[leg].member_count == null)
          assert.equal(r.display.legs[leg].member_count, null);
  }
});
test("no bench file means STORE SILENT; no clock synthesis when no true first tick exists", async () => {
  const face = await read(altId);
  await extendFace(face, { here, eventId: altId, benchPath: "none" });
  assert.equal(face.bench.present, false);
  assert.ok(face.render.checkpoints.every((g) => g.bench === null));
  const missing = await read(altId);
  for (const row of missing.os)
    for (const l of Object.values(row.legs)) delete l.true_trade_count;
  await assert.rejects(
    () => extendFace(missing, { here, eventId: altId, benchPath: "none" }),
    /no stored first real pair tick/,
  );
});
