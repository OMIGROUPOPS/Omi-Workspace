import {createHash} from 'node:crypto';
import {existsSync,mkdirSync,readFileSync,readdirSync,statSync,writeFileSync} from 'node:fs';
import {dirname,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {buildScoreboard} from '../../build_scoreboard.mjs';
import {readJsonBytes,jsonFileExists} from '../../json_storage.mjs';
const shell=resolve(dirname(fileURLToPath(import.meta.url)),'..'),source=resolve(shell,'../data');
// Preserve the previously published five-game bundle for games outside the draw.
// Do not ship unrelated dirty worktree replays.
const baseline=resolve(shell,'../demo-baseline'),target=resolve(shell,'.vercel/tune100-public-gzip');
const sha=b=>createHash('sha256').update(b).digest('hex'),json=p=>JSON.parse(readJsonBytes(p));
const selectionBytes=readFileSync(resolve(source,'tune-expansion/SELECTION.json')),selection=JSON.parse(selectionBytes);
assert.equal(sha(selectionBytes),'c8d0710d1aab2b43e9cb9d9e2813fc9c38f233e8e4941e8647d347aa0a6e4c7b');
assert.equal(selection.selected.length,100);
const selected=new Set(selection.selected.map(r=>r.event_id)),oldIndex=json(resolve(baseline,'data/index.json')),localIndex=json(resolve(source,'index.json'));
const rerunReceipt=resolve(source,'unsupported-rests/RECEIPT.json');
const rerun=existsSync(rerunReceipt)?json(rerunReceipt):null;
const current=new Set([...selected,...(rerun?['KXATPMATCH-26JUL12ALTGAS']:[])]);
if(rerun){assert.equal(rerun.selection_sha256,sha(selectionBytes));assert.equal(rerun.verification.status,'PASS');}
assert.equal(oldIndex.games.length,5,'Previously published baseline must remain the reviewed five');
const baselineManifest=json(resolve(baseline,'demo-assets.json'));
for(const entry of baselineManifest.assets)assert.equal(sha(readJsonBytes(resolve(baseline,entry.path))),entry.sha256,'Baseline changed: '+entry.path);
const games=[...oldIndex.games.filter(g=>!current.has(g.event)),...localIndex.games.filter(g=>current.has(g.event))].sort((a,b)=>a.event.localeCompare(b.event));
assert.equal(games.length,104);assert.equal(new Set(games.map(g=>g.event)).size,104);
const entries=[],allowed=new Set();
function within(root,name){const p=resolve(root,name);assert(p.startsWith(root+sep),'Unsafe asset path');return p;}
function put(name,bytes){
 const zipped=name.endsWith('.json'),storedName=name+(zipped?'.gz':''),encoded=zipped?gzipSync(bytes,{level:9}):bytes;
 if(zipped)assert.equal(sha(gunzipSync(encoded)),sha(bytes));
 const p=within(target,storedName);mkdirSync(dirname(p),{recursive:true});writeFileSync(p,encoded);
 allowed.add(storedName.replaceAll('\\','/'));
 entries.push({path:storedName,bytes:encoded.length,sha256:sha(encoded),...(zipped?{json_path:name,json_bytes:bytes.length,sha256_uncompressed:sha(bytes)}:{})});
}
const encode=v=>Buffer.from(JSON.stringify(v)+'\n');
put('data/index.json',encode({...localIndex,games}));
put('data/desk-status.json',readJsonBytes(resolve(baseline,'data/desk-status.json')));
put('data/tune-expansion/SELECTION.json',encode({schema:selection.schema,seed:selection.seed,selection_sha256:sha(selectionBytes),quotas:selection.quotas,selected:selection.selected}));
for(const game of games){
 assert(/^[A-Z0-9-]+$/.test(game.event)&&game.url===`/data/${game.event}.face.json`);
 const root=current.has(game.event)?source:resolve(baseline,'data');
 const faceBytes=readJsonBytes(within(root,game.event+'.face.json')),face=JSON.parse(faceBytes),gradeBytes=readJsonBytes(within(root,game.event+'.grade.json')),grade=JSON.parse(gradeBytes);
 assert.equal(grade.event,game.event);assert.equal(grade.provenance.face_sha256,sha(faceBytes));assert.equal(grade.provenance.os_sha256,face.provenance.os_sha256);assert.equal(grade.provenance.trace_sha256,face.provenance.trace_sha256);
 if(current.has(game.event))assert.equal(face.provenance.os_sha256,(rerun?.inputs??selection.inputs)['window1_v54_dual_belief_os.js']);
 put(`data/${game.event}.face.json`,faceBytes);put(`data/${game.event}.grade.json`,gradeBytes);
 const pressurePath=within(root,game.event+'.pressure.json');
 if(jsonFileExists(pressurePath)){const bytes=readJsonBytes(pressurePath),p=JSON.parse(bytes);assert.equal(p.provenance.face_sha256,sha(faceBytes));assert.equal(p.provenance.trace_sha256,face.provenance.trace_sha256);put(`data/${game.event}.pressure.json`,bytes);}
 if(face.oracle?.detail_url){assert.equal(face.oracle.detail_url,`/data/${game.event}.oracle.json`);const p=within(root,game.event+'.oracle.json'),bytes=existsSync(p+'.gz')?gunzipSync(readFileSync(p+'.gz')):readFileSync(p);assert.equal(sha(bytes),face.oracle.sha256_uncompressed);put(`data/${game.event}.oracle.json`,bytes);}
 if(face.bid_card_details)for(const d of face.bid_card_details.chunks??[face.bid_card_details]){const name=face.bid_card_details.chunks?`${game.event}.bid-details/${d.group}-${d.first}.json`:game.event+'.bid-details.json';assert.equal(d.detail_url,`/data/${name}`);const bytes=gunzipSync(readFileSync(within(root,name+'.gz')));assert.equal(sha(bytes),d.sha256_uncompressed);const detail=JSON.parse(bytes);assert.equal(detail.event,game.event);assert.equal(detail.os_sha256,face.provenance.os_sha256);assert.equal(detail.trace_sha256,face.provenance.trace_sha256);put('data/'+name,bytes);}
 if(face.timeline)for(const d of face.timeline.chunks){const name=`${game.event}.timeline/${d.first}.json`;assert.equal(d.url,`/data/${name}`);const bytes=gunzipSync(readFileSync(within(root,name+'.gz')));assert.equal(sha(bytes),d.sha256_uncompressed);const c=JSON.parse(bytes);assert.equal(c.event,game.event);assert.equal(c.os_sha256,face.provenance.os_sha256);assert.equal(c.trace_sha256,face.provenance.trace_sha256);put('data/'+name,bytes);}
 if(selected.has(game.event)){const p=within(source,`tune-expansion/faults/${game.event}.json`),bytes=readFileSync(p),fault=JSON.parse(bytes);assert.equal(fault.provenance.face_sha256,sha(faceBytes));assert.equal(fault.provenance.grade_sha256,sha(gradeBytes));put(`data/tune-expansion/faults/${game.event}.json`,bytes);}
}
put('data/tune-expansion/faults/index.json',readFileSync(resolve(source,'tune-expansion/faults/index.json')));
const localHistory=json(resolve(source,'grades/index.json')),oldHistory=json(resolve(baseline,'data/grades/index.json'));
const history={...localHistory,grades:[...oldHistory.grades.filter(g=>!current.has(g.event)),...localHistory.grades.filter(g=>current.has(g.event))],views:Object.fromEntries(games.map(g=>[g.event,(current.has(g.event)?localHistory:oldHistory).views?.[g.event]]))};
put('data/grades/index.json',encode(history));
put('data/scoreboard.json',Buffer.from(buildScoreboard(resolve(target,'data'),{emit:false}).payload));
put('data/scoreboard-tune-100.json',Buffer.from(buildScoreboard(resolve(target,'data'),{emit:false,events:[...selected],scope:`${rerun?.verification.label?rerun.verification.label+'; ':''}Frozen 100-game draw; safety-flagged fills excluded from credit; overlapping fault labels`,determinism:rerun?.verification.determinism_sample}).payload));
put('favicon.svg',readFileSync(resolve(shell,'public/favicon.svg')));
function files(root){if(!existsSync(root))return [];return readdirSync(root,{withFileTypes:true}).flatMap(e=>{assert(!e.isSymbolicLink());const p=resolve(root,e.name);return e.isDirectory()?files(p):[p];});}
for(const p of files(target)){const name=relative(target,p).replaceAll('\\','/');assert(name==='demo-assets.json'||allowed.has(name),'Non-allowlisted stale asset: '+name);}
const details=files(source).filter(p=>/\.stages[\\/]|[\\/]renewals[^\\/]*|\.accountability\.json/.test(p));
const manifest={games:games.map(g=>g.event),selection_sha256:sha(selectionBytes),preserved_baseline_asset_manifest_sha256:sha(readFileSync(resolve(baseline,'demo-assets.json'))),policy:'Frozen100 plus ALT check and three other previously published games. Compact face/grade/oracle/pressure/faults, picker/history/scoreboard, approved hash-bound bid and timeline chunks. Lossless gzip storage with original JSON URLs. No raw prints, remaining704, engine, credentials, full stages or renewal streams.',omitted_detail_files:details.length,omitted_detail_bytes:details.reduce((s,p)=>s+statSync(p).size,0),assets:entries,total_bytes:entries.reduce((s,e)=>s+e.bytes,0),uncompressed_asset_bytes:entries.reduce((s,e)=>s+(e.json_bytes??e.bytes),0)};
writeFileSync(resolve(target,'demo-assets.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({games:games.length,selected:selected.size,total_bytes:manifest.total_bytes,omitted_detail_bytes:manifest.omitted_detail_bytes,assets:entries.length}));
