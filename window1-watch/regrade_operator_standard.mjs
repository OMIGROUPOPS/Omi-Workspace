// Regrade existing saved traces only; snapshot old cards, preserve history, verify sources.
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { build, appendHistory } from "./build_grade.mjs";
import { readGradePrints } from "./grade_prints.mjs";
const here=path.dirname(fileURLToPath(import.meta.url)), repo=path.dirname(here);
const read=async(p)=>JSON.parse(await fs.readFile(p));
const sha=(b)=>crypto.createHash("sha256").update(b).digest("hex");
const data=path.join(here,"data"), index=await read(path.join(data,"index.json"));
const games=await Promise.all(index.games.map(async({event})=>({event,
  legs:(await read(path.join(data,event+".face.json"))).legs})));
const protectedPaths=["arb-executor/analysis/window1_v54_dual_belief_os.js",
  "arb-executor/analysis/window1_v54_functionable_os.js","arb-executor/analysis/build_window1_v54_dual_belief.js",
  "window1-watch/face_contract.mjs","window1-watch/data/index.json",
  ...games.flatMap(({event})=>["window1-watch/data/"+event+".face.json","window1-watch/data/"+event+".face.json.gz"])];
const hashes=async()=>Object.fromEntries(await Promise.all(protectedPaths.map(async(p)=>[p,sha(await fs.readFile(path.join(repo,p)))])));
const beforeHashes=await hashes(), oldHistory=await read(path.join(data,"grades/index.json"));
const before={}, buckets={};
const card=(g)=>({ letter:g.LETTER.letter, governing:g.LETTER.governing_section,
  sections:Object.fromEntries(Object.entries(g.LETTER.section_grades).map(([k,v])=>[k,v.letter])),
  lines:g.display.sections.map((s)=>`${s.name}: ${s.line}`),
  first_calls:Object.fromEntries(Object.entries(g.MICRO.legs).map(([k,v])=>[k,v.first_eligible_full_span])),
  roles:g.MACRO.operator_roles??null, fills:g.OUTCOME.legs, pair_sum:g.OUTCOME.pair_sum,
  captured_cents:g.OUTCOME.captured_cents, offered_cents:g.OUTCOME.best_capturable_cents,
  oracle:g.MICRO.oracle_diagnostic?.legs??null, provenance:g.provenance });
for(const {event} of games){
  before[event]=await read(path.join(data,event+".grade.json"));
  const g=before[event], p=g.provenance;
  const file=path.join(data,"grades",event,`${p.os_sha256.slice(0,8)}_${p.trace_sha256.slice(0,8)}.json`);
  const bucket=await read(file);buckets[event]={file,grades:bucket.grades};
  // A previously refreshed local card can differ from its older history snapshot.
  // Preserve that exact pre-change card too, rather than silently discarding it.
  if(!bucket.grades.some((x)=>JSON.stringify(x)===JSON.stringify(g))) await appendHistory(data,g,g.timestamp);
}
const report={scope:"Face-only rubric; no replay, no engine edit; before = actual working cards, not assumed HEAD",
  before_commit:execFileSync("git",["rev-parse","HEAD"],{cwd:repo}).toString().trim(),
  protected_sha256_before:beforeHashes,games:[]};
const prints=await readGradePrints("C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl",games);
for(const {event} of games){
  const after=await build(event,prints[event]), prior=before[event];
  for(const key of ["os_sha256","trace_sha256","bench_sha256","stage_inputs_sha256","stage_files_count"])
    assert.equal(after.provenance[key],prior.provenance[key],`${event}:${key}`);
  assert.deepEqual(after.OUTCOME,prior.OUTCOME,`${event}: outcome changed`);
  assert.deepEqual(after.SENTENCE.author_counts,prior.SENTENCE.author_counts);
  assert.equal(after.SENTENCE.gate_1_authorship_certification,"STORE SILENT");
  const bucket=await read(buckets[event].file);
  assert.deepEqual(bucket.grades.slice(0,buckets[event].grades.length),buckets[event].grades);
  assert.ok(bucket.grades.some((g)=>JSON.stringify(g)===JSON.stringify(prior)),"before card missing from history");
  report.games.push({event,before:card(prior),after:card(after),
    previous_history_snapshots_preserved:buckets[event].grades.length,
    snapshots_appended:bucket.grades.length-buckets[event].grades.length});
}
report.protected_sha256_after=await hashes();
assert.deepEqual(report.protected_sha256_after,beforeHashes);
const history=await read(path.join(data,"grades/index.json"));
for(let i=0;i<oldHistory.grades.length;i++){
  for(const key of ["grade_sha256","letter","url","revision","timestamp"])
    assert.equal(history.grades[i][key],oldHistory.grades[i][key],`History ${i}:${key}`);
}
report.status="PASS — existing outcomes, stage bindings, OS/face hashes and full history prefixes preserved";
report.old_history_entries=oldHistory.grades.length;report.new_history_entries=history.grades.length;
const file=path.join(here,"proof","GRADE_RUBRIC_V1_BEFORE_AFTER.json");
await fs.writeFile(file,JSON.stringify(report,null,2)+"\n");
console.log(report.status);
for(const row of report.games)console.log(JSON.stringify({event:row.event,before:row.before.letter,
  after:row.after.letter,sections:row.after.sections,captured:row.after.captured_cents,offered:row.after.offered_cents}));
console.log(file);
