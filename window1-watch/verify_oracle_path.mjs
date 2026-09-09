import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { packFace, unpackFace } from "./face_encoding.mjs";
import { readGradePrints } from "./grade_prints.mjs";
const here = path.dirname(fileURLToPath(import.meta.url)), repo = path.resolve(here, "..");
const baseline = process.argv[2];
if (!baseline) throw new Error("Usage: node window1-watch/verify_oracle_path.mjs <baseline commit> [--preserve-face]");
const sha = b => crypto.createHash("sha256").update(b).digest("hex");
const games = JSON.parse(fs.readFileSync(path.join(here,"data/index.json"))).games;
const faces = games.map(g => unpackFace(JSON.parse(fs.readFileSync(path.join(here,"data",g.event+".face.json")))));
const prints = await readGradePrints("C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl",faces.map(f=>({event:f.provenance.event_id,legs:f.legs})));
const report = { baseline, role:"RULER — NOT AN OS INPUT", tests:[], games:[] };
for (const f of faces) {
  const event=f.provenance.event_id, file=path.join(here,"data",event+".face.json");
  const original=unpackFace(JSON.parse(execFileSync("git",["show",`${baseline}:window1-watch/data/${event}.face.json`],{cwd:repo,maxBuffer:50e6})));
  for(const key of ["os","bell","first_tick","legs"]) assert.deepEqual(f[key],original[key]);
  for(const key of ["span_start_epoch","span_end_epoch","bell_epoch"])
    assert.equal(f.truth[key],original.truth[key]);
  const oracle=f.oracle, bytes=zlib.gunzipSync(fs.readFileSync(path.join(here,"."+oracle.detail_url+".gz")));
  assert.equal(sha(bytes),oracle.sha256_uncompressed);
  assert.equal(prints[event].provenance.sha256,oracle.provenance.prints.sha256);
  const data=JSON.parse(bytes);
  const game={event,os_sha256:f.provenance.os_sha256,trace_sha256:f.provenance.trace_sha256,
    oracle_sha256:sha(bytes),oracle_gzip_bytes:fs.statSync(path.join(here,"."+oracle.detail_url+".gz")).size,legs:{}};
  for(const leg of f.legs) {
    const tape=prints[event].legs[leg].filter(p=>p.epoch>=f.truth.span_start_epoch&&p.epoch<=f.truth.span_end_epoch&&p.epoch<f.truth.bell_epoch);
    const series=data.legs[leg];
    // Independent multiset deletion sweep, not the builder's reverse suffix algorithm.
    const counts=new Map();for(const p of tape)counts.set(p.price,(counts.get(p.price)??0)+1);
    let cursor=0,sum=0,count=0;
    for(let i=0;i<data.ticks.length;i++) {
      const epoch=data.ticks[i][0],profile=series.profiles[series.values[i][0]];
      while(cursor<tape.length&&tape[cursor].epoch<=epoch){const p=tape[cursor++];counts.set(p.price,counts.get(p.price)-1);if(!counts.get(p.price))counts.delete(p.price);}
      const expected=epoch>=f.truth.span_start_epoch&&epoch<=f.truth.span_end_epoch&&epoch<f.truth.bell_epoch&&counts.size?Math.min(...counts.keys()):null;
      assert.equal(profile.perfect,expected,`${event}/${leg}/${i}`);
      const gap=profile.Q!=null&&expected!=null?profile.Q-expected:null;
      assert.equal(profile.gap,gap);assert.equal(series.values[i][1],gap);
      if(gap!=null){sum+=Math.abs(gap);count++;}
    }
    assert.equal(oracle.legs[leg].mean_absolute_gap_cents,count?sum/count:null);
    assert.equal(oracle.legs[leg].comparable_receipts,count);
    game.legs[leg]={...oracle.legs[leg],path:undefined,fill_points:oracle.legs[leg].fill_points};
    console.log(oracle.legs[leg].hud_line);
  }
  // Oracle-only publication: do not accidentally reselect an older bench when
  // replay-independent face generation discovers its default bench path.
  if(process.argv.includes("--preserve-face")) {
    const out=Buffer.from(JSON.stringify(packFace({...original,oracle}))+"\n");
    fs.writeFileSync(file,out);fs.writeFileSync(file+".gz",zlib.gzipSync(out));
  }
  const published=unpackFace(JSON.parse(fs.readFileSync(file)));delete published.oracle;
  delete published.dictionary;delete original.dictionary;delete original.oracle;
  assert.deepEqual(published,original,"Only oracle may change in an existing face");
  if(process.argv.includes("--preserve-grade-history")) {
    const gradePath=`window1-watch/data/${event}.grade.json`;
    const previousGrade=JSON.parse(execFileSync("git",["show",`${baseline}:${gradePath}`],{cwd:repo,maxBuffer:50e6}));
    previousGrade.provenance.face_sha256=sha(fs.readFileSync(file));
    fs.writeFileSync(path.join(repo,gradePath),JSON.stringify(previousGrade,null,2)+"\n");
  }
  report.games.push(game);
}
report.tests=["All receipt floors match independent forward multiset sweep", "Signed gaps and receipt-weighted means verified", "Every existing face field except oracle is unchanged", "No engine replay; source OS and trace hashes unchanged", "Positive-size source accepted by filed grade_prints rule", "All five saved games checked"];
const osFile="arb-executor/analysis/window1_v54_dual_belief_os.js";
assert.equal(sha(fs.readFileSync(path.join(repo,osFile))),sha(execFileSync("git",["show",`${baseline}:${osFile}`],{cwd:repo,maxBuffer:5e6})));
report.os_sha256=sha(fs.readFileSync(path.join(repo,osFile)));
fs.writeFileSync(path.join(here,"proof/ORACLE_PATH_RECEIPT.json"),JSON.stringify(report,null,2)+"\n");
if(process.argv.includes("--preserve-face")) {
  const { writeGameIndex } = await import("./face_contract.mjs");await writeGameIndex(path.join(here,"data"));
}
if(process.argv.includes("--preserve-grade-history")) {
  // A new hindsight overlay is not a new OS run or grade. Keep the strip exact.
  const changed=execFileSync("git",["diff","--name-only",baseline,"--","window1-watch/data/grades"],{cwd:repo}).toString().trim().split(/\r?\n/).filter(Boolean);
  for(const relative of [...changed,"window1-watch/data/GRADE_RECEIPT.json"])
    fs.writeFileSync(path.join(repo,relative),execFileSync("git",["show",`${baseline}:${relative}`],{cwd:repo,maxBuffer:80e6}));
}
