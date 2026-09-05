import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  readPinnedTruth,
  recordedTruth,
  attachRecordedTruth,
  parseTruthCsv,
  TRUTH_COMMIT,
} from "./recorded_truth.mjs";
const here = path.dirname(fileURLToPath(import.meta.url)),
  root = path.resolve(here, "..");
const table = readPinnedTruth(root),
  base = "42be2fdf141febbaae7b1f9f8e8a8b7f9c3d9a69";
const ALT = "KXATPMATCH-26JUL12ALTGAS",
  URS = "KXATPCHALLENGERMATCH-26JUL14URSPAL";
const face = (id) =>
  JSON.parse(fs.readFileSync(path.join(here, "data", `${id}.face.json`)));
function withoutActionDisplay(face) {
  const copy = structuredClone(face);
  delete copy.render.bid_actions;
  delete copy.render.pool_accuracy;
  delete copy.render.marker_legend;
  for (const c of copy.render.checkpoints) if (c.bench) delete c.bench.pool_accuracy;
  const hover = copy.render.columns.indexOf("hover_lines");
  if (hover >= 0) {
    copy.render.columns.splice(hover, 1);
    for (const tick of copy.render.ticks) tick.splice(hover, 1);
  }
  return copy;
}

test("exact pinned records, SHA256 and original CSV columns", () => {
  for (const id of [ALT, URS]) {
    const f = face(id),
      row = table.rows.find((r) => r.values.event_id === id);
    assert.equal(f.truth.table_commit, TRUTH_COMMIT);
    assert.equal(
      f.truth.row_sha256,
      crypto.createHash("sha256").update(row.raw, "utf8").digest("hex"),
    );
    for (const [leg, l] of Object.entries(f.truth.legs)) {
      const prefix = row.values.legA === leg ? "legA" : "legB";
      assert.equal(l.source_columns.floor_cents, prefix + "_floor_c");
      assert.equal(l.floor_cents, Number(row.values[prefix + "_floor_c"]));
      assert.equal(l.floor_epoch, Number(row.values[prefix + "_floor_epoch"]));
      assert.equal(
        l.minutes_to_bell,
        (f.bell.timestamp_epoch - l.floor_epoch) / 60,
      );
    }
  }
});
test("ALT 58 + 38 = 96; URS 57 + PAL 40 = 97; use game bell without silently shifting it", () => {
  const a = face(ALT).truth,
    u = face(URS).truth;
  assert.equal(a.pair.line, "best capturable = 58 + 38 = 96¢");
  assert.equal(a.pair.discount_line, "4¢ under par");
  assert.equal(a.legs.ALT.minutes_to_bell.toFixed(2), "3362.56");
  assert.equal(a.legs.GAS.minutes_to_bell.toFixed(2), "425.54");
  assert.equal(u.pair.line, "best capturable = 57 + 40 = 97¢");
  assert.equal(u.pair.discount_line, "3¢ under par");
  assert.equal(u.table_bell_delta_seconds, 2853);
  assert.equal(u.legs.URS.minutes_to_bell.toFixed(2), "159.16");
  assert.equal(u.legs.PAL.minutes_to_bell.toFixed(2), "351.42");
  assert.equal(u.legs.PAL.markers.play.boundary, "BEFORE_AXIS");
  assert.equal(u.legs.PAL.markers.inspection.boundary, null);
});
test("ruler refresh leaves every existing OS, tape, benchmark and receipt field unchanged", () => {
  for (const id of [ALT, URS]) {
    const original = JSON.parse(
      execFileSync(
        "git",
        ["show", `${base}:window1-watch/data/${id}.face.json`],
        { cwd: root, maxBuffer: 32 * 1024 * 1024 },
      ),
    );
    const current = withoutActionDisplay(face(id));
    delete current.truth;
    assert.deepEqual(current, original);
    const rebuilt = structuredClone(original);
    attachRecordedTruth(rebuilt, table);
    assert.deepEqual(rebuilt, withoutActionDisplay(face(id)));
  }
});
test("UNKNOWN, NO_FORMATION and EMPTY cannot turn finite fixture floors into a ruler", () => {
  for (const status of [
    "UNKNOWN",
    "NO_FORMATION",
    "EMPTY (bell before formation end)",
  ]) {
    const fixture = structuredClone(table);
    fixture.rows.find((r) => r.values.event_id === ALT).values.verified_span =
      status;
    const t = recordedTruth(face(ALT), fixture);
    assert.equal(t.reason, status);
    assert.equal(t.pair.sum_cents, null);
    for (const l of Object.values(t.legs)) {
      assert.equal(l.floor_cents, null);
      assert.equal(l.floor_epoch, null);
      assert.equal(l.minutes_to_bell, null);
      assert.match(l.line, /STORE SILENT/);
      assert.ok(l.line.includes(status));
    }
  }
});
test("absent records, blank floor epochs and floors outside the verified span stay silent", () => {
  assert.equal(
    recordedTruth(face(ALT), { ...table, rows: [] }).reason,
    "NO ROW IN PINNED TABLE",
  );
  for (const epoch of ["", "UNKNOWN", "0"]) {
    const fixture = structuredClone(table);
    fixture.rows.find(
      (r) => r.values.event_id === ALT,
    ).values.legA_floor_epoch = epoch;
    const t = recordedTruth(face(ALT), fixture);
    assert.equal(t.legs.ALT.floor_cents, null);
    assert.equal(t.pair.sum_cents, null);
  }
});
test("CSV receipt hashing preserves quotes and embedded newlines, excluding only the record terminator", () => {
  const raw = 'E,OK,58,"two, lines\nand ""quotes"""';
  const rows = parseTruthCsv(
    "event_id,verified_span,legA_floor_c,note\r\n" + raw + "\r\n",
  );
  assert.equal(rows[0].raw, raw);
  assert.equal(rows[0].values.note, 'two, lines\nand "quotes"');
  assert.equal(
    rows[0].row_sha256,
    crypto.createHash("sha256").update(raw).digest("hex"),
  );
});
