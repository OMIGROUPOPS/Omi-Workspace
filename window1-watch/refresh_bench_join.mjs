// Existing faces only. No tape export, OS replay, pricing, or chart transformation.
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { unpackFace, packFace } from "./face_encoding.mjs";
import { CORRECTED_TICK_BENCH_COMMIT, CORRECTED_TICK_BENCH_PATH,
  alignBenchToCorrectedRuler, writeGameIndex } from "./face_contract.mjs";
import { attachPoolAccuracy } from "./plain_cards.mjs";
const here=path.dirname(fileURLToPath(import.meta.url)), repo=path.resolve(here,".."), dataRoot=path.join(here,"data");
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
const source=path.join(repo,CORRECTED_TICK_BENCH_PATH), bytes=await fs.readFile(source);
const pinned=execFileSync("git",["show",`${CORRECTED_TICK_BENCH_COMMIT}:${CORRECTED_TICK_BENCH_PATH}`],{cwd:repo,maxBuffer:32*1024*1024});
assert.equal(sha(bytes),sha(pinned),"Corrected named checks changed: choose an explicit newer baseline, never silently mix runs");
const bench=JSON.parse(bytes), index=JSON.parse(await fs.readFile(path.join(dataRoot,"index.json")));
const report={source,source_commit:CORRECTED_TICK_BENCH_COMMIT,source_sha256:sha(bytes),label:bench.label,
  scope:"Face bench join only; no OS or tape change. Corrected clock uses causal stored-receipt rebasing; no new forecast.",games:[]};
for(const game of index.games) {
  const file=path.join(dataRoot,game.event+".face.json"),face=unpackFace(JSON.parse(await fs.readFile(file)));
  const named=Object.values(bench.events??{}).find(e=>e.event_id===game.event);
  assert.ok(named,`No corrected named check for ${game.event}; do not fall back to the proof run`);
  const protectedKeys=["os","tape","oracle","truth","rulers","bell","first_tick","accountability"];
  const before=Object.fromEntries(protectedKeys.map(k=>[k,JSON.stringify(face[k])]));
  const previousSha=face.provenance.bench_sha256;
  Object.assign(face.provenance,{bench_sha256:sha(bytes),bench_label:bench.label,bench_commit:CORRECTED_TICK_BENCH_COMMIT});
  face.bench={present:true,source,label:bench.label,original_label:bench.label,
    source_commit:CORRECTED_TICK_BENCH_COMMIT};
  await alignBenchToCorrectedRuler(face);
  attachPoolAccuracy(face);
  for(const k of protectedKeys)assert.equal(JSON.stringify(face[k]),before[k],`${game.event}: ${k} changed`);
  const payload=Buffer.from(JSON.stringify(packFace(face))+"\n");
  await fs.writeFile(file,payload);await fs.writeFile(file+".gz",zlib.gzipSync(payload));
  const gradeFile=path.join(dataRoot,game.event+".grade.json"),grade=JSON.parse(await fs.readFile(gradeFile));
  // A grade from a different bench must be rebuilt, never silently relabeled.
  const regrade=grade.provenance.bench_sha256!==sha(bytes);
  if(!regrade){grade.provenance.face_sha256=sha(payload);await fs.writeFile(gradeFile,JSON.stringify(grade,null,2)+"\n");}
  report.games.push({event:game.event,previous_bench_sha256:previousSha,bench_sha256:sha(bytes),
    clock_status:face.bench.clock_status,clock_delta_seconds:face.bench.clock_delta_seconds,
    checkpoints:face.render.checkpoints.map(c=>({gate:c.minutesToBell,source_gate:c.bench?.clock?.source_gate_minutes??null,
      pool_accuracy:c.bench?.pool_accuracy?.label??"STORE SILENT"})),grade_rebuild_required:regrade});
  console.log(`${game.event}: corrected tick bench ${sha(bytes).slice(0,8)} · ${face.bench.clock_status}${regrade?" · REBUILD GRADE":""}`);
}
await writeGameIndex(dataRoot);
await fs.writeFile(path.join(here,"proof/CORRECTED_BENCH_JOIN_RECEIPT.json"),JSON.stringify(report,null,2)+"\n");
