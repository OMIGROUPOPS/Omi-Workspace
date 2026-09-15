import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";
import { extendFace, CORRECTED_TICK_BENCH_PATH, CORRECTED_TICK_BENCH_COMMIT } from "./face_contract.mjs";
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,"..");
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
test("all loaded faces and current grades bind the corrected named suite; ruler-clock joins are causal", async()=>{
  const index=JSON.parse(await fs.readFile(path.join(here,"data/index.json")));
  const source=path.join(root,CORRECTED_TICK_BENCH_PATH),expected=sha(await fs.readFile(source));
  for(const game of index.games){
    const bytes=await fs.readFile(path.join(here,"data",game.event+".face.json"));
    const f=unpackFace(JSON.parse(bytes));
    assert.equal(path.resolve(f.bench.source),source);
    assert.equal(f.provenance.bench_sha256,expected);
    assert.equal(f.provenance.bench_commit,CORRECTED_TICK_BENCH_COMMIT);
    assert.doesNotMatch(f.bench.label,/STALE|PROOF RUN/);
    for(const c of f.render.checkpoints)if(c.bench?.clock){
      assert.ok(c.bench.clock.source_receipt_epoch<=f.bell.timestamp_epoch-c.minutesToBell*60);
      assert.ok(c.bench.clock.carried_age_minutes>=0);
    }
    const grade=JSON.parse(await fs.readFile(path.join(here,"data",game.event+".grade.json")));
    assert.equal(grade.provenance.bench_sha256,expected);
    assert.equal(grade.provenance.face_sha256,sha(bytes));
  }
});
test("future ordinary face builds default to corrected ticks, not minute proof",async()=>{
  const index=JSON.parse(await fs.readFile(path.join(here,"data/index.json")));
  const game=index.games[0], f=unpackFace(JSON.parse(await fs.readFile(path.join(here,"data",game.event+".face.json"))));
  await extendFace(f,{here,eventId:game.event});
  assert.equal(path.resolve(f.bench.source),path.join(root,CORRECTED_TICK_BENCH_PATH));
  assert.equal(f.provenance.bench_commit,CORRECTED_TICK_BENCH_COMMIT);
});
