import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const repo=path.resolve(import.meta.dirname,'../..'), root='C:/tmp/unsupported_rests_20260914';
const data=path.join(repo,'window1-watch/data');
const selection=JSON.parse(fs.readFileSync(path.join(root,'SELECTION.json')));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.equal(hash(path.join(root,'SELECTION.json')),'c8d0710d1aab2b43e9cb9d9e2813fc9c38f233e8e4941e8647d347aa0a6e4c7b');
const inputs=Object.fromEntries(Object.keys(selection.inputs).map(name=>[name,hash(path.join(repo,'arb-executor/analysis',name))]));
assert.equal(inputs['window1_v54_functionable_os.js'],selection.inputs['window1_v54_functionable_os.js']);
const pin={schema:'UNSUPPORTED_RESTS_RUN_INPUTS_V1',inputs,selection_sha256:hash(path.join(root,'SELECTION.json')),scope:'Same frozen 100 plus ALTGAS named check; conduct exact-level renewal/pull and corrected replay bell only; no pool, price, grade-rubric, source-tape or selection changes.',prepared_at:new Date().toISOString()};
const pinPath=path.join(root,'RUN_INPUTS.json');
if(fs.existsSync(pinPath))assert.deepEqual(JSON.parse(fs.readFileSync(pinPath)).inputs,inputs);else fs.writeFileSync(pinPath,JSON.stringify(pin,null,2)+'\n',{flag:'wx'});
const backup=path.join(root,'before_compact');fs.mkdirSync(backup,{recursive:true});
const events=new Set([...selection.selected.map(r=>r.event_id),'KXATPMATCH-26JUL12ALTGAS']);
const saved=[];
for(const name of fs.readdirSync(data)){
 if(!fs.statSync(path.join(data,name)).isFile())continue;
 if(![...events].some(e=>name.startsWith(e+'.'))&&!['index.json','GRADE_RECEIPT.json','SCOREBOARD.json'].includes(name))continue;
 const dst=path.join(backup,name);if(!fs.existsSync(dst))fs.copyFileSync(path.join(data,name),dst,fs.constants.COPYFILE_EXCL);
 saved.push({name,sha256:hash(dst),bytes:fs.statSync(dst).size});
}
for(const name of ['grades','tune-expansion']){const dst=path.join(backup,name);if(!fs.existsSync(dst))fs.cpSync(path.join(data,name),dst,{recursive:true,errorOnExist:true,force:false});}
const manifest=path.join(backup,'MANIFEST.json');if(!fs.existsSync(manifest))fs.writeFileSync(manifest,JSON.stringify({saved,at:new Date().toISOString()},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({inputs,saved_compact_files:saved.length,backup},null,2));
