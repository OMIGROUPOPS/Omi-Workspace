// Explicit selected-cohort artifact allowlist. Raw tapes/stages/renewals never enter it.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readJsonBytes,gzipMirror,GZIP_ARCHIVE_BYTES} from '../json_storage.mjs';
const data=path.resolve(import.meta.dirname,'../data'),repo=path.resolve(import.meta.dirname,'../..');
const read=f=>JSON.parse(readJsonBytes(f)),hash=b=>createHash('sha256').update(b).digest('hex');
const selectionFile=path.join(data,'tune-expansion/SELECTION.json'),selection=read(selectionFile);
assert.equal(hash(readJsonBytes(selectionFile)),'c8d0710d1aab2b43e9cb9d9e2813fc9c38f233e8e4941e8647d347aa0a6e4c7b');
const receipt=read(path.join(data,'unsupported-rests/RECEIPT.json'));assert.equal(receipt.verification.status,'PASS');
const events=[...selection.selected.map(r=>r.event_id),'KXATPMATCH-26JUL12ALTGAS'];
const files=new Set(),archives=[];
function add(file){
 if(files.has(file)||files.has(file+'.gz'))return;
 assert(file.startsWith(data+path.sep));assert(!/\.stages[\\/]|renewals|accountability|altgas\.json$/.test(file));
 if(!fs.existsSync(file)&&!fs.existsSync(file+'.gz'))return;
 if(file.endsWith('.json')){
  const bytes=readJsonBytes(file);
  if(bytes.length>=GZIP_ARCHIVE_BYTES){const a=gzipMirror(file,bytes);archives.push({...a,path:path.relative(repo,a.path).replaceAll('\\','/')});files.add(file+'.gz');return;}
 }
 files.add(fs.existsSync(file)?file:file+'.gz');
}
for(const event of events){
 const face=read(path.join(data,event+'.face.json'));
 for(const suffix of ['.face.json','.face.json.gz','.grade.json','.pressure.json','.oracle.json.gz'])add(path.join(data,event+suffix));
 for(const d of face.bid_card_details?.chunks??(face.bid_card_details?[face.bid_card_details]:[]))add(path.join(data,d.detail_url.slice('/data/'.length)+'.gz'));
 for(const d of face.timeline?.chunks??[])add(path.join(data,d.url.slice('/data/'.length)+'.gz'));
 for(const suffix of ['.json','.sentences.json'])add(path.join(data,'tune-expansion/games',event+suffix));
 add(path.join(data,'tune-expansion/faults',event+'.json'));
 const history=path.join(data,'grades',event);
 if(fs.existsSync(history))for(const name of fs.readdirSync(history).filter(n=>n.endsWith('.json')||n.endsWith('.json.gz')))add(path.join(history,name.endsWith('.gz')?name.slice(0,-3):name));
}
for(const name of ['index.json','grades/index.json','scoreboard.json','scoreboard-tune-100.json','GRADE_RECEIPT.json'])add(path.join(data,name));
for(const dir of ['tune-expansion','tune-expansion/faults','unsupported-rests'])for(const entry of fs.readdirSync(path.join(data,dir),{withFileTypes:true}))if(entry.isFile()&&!entry.name.startsWith('ARCHIVE_'))add(path.join(data,dir,entry.name));
const paths=[...files].sort().map(file=>{assert(fs.statSync(file).size<100*1024*1024,'Oversized Git file '+file);return path.relative(repo,file).replaceAll('\\','/')});
const result={scope:'Frozen100 + separate ALT check; exact lossless derived archives; raw local JSON retained',selection_sha256:receipt.selection_sha256,threshold_bytes:GZIP_ARCHIVE_BYTES,archives,files:paths};
fs.writeFileSync(path.join(data,'unsupported-rests/ARCHIVE_RECEIPT.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({files:paths.length,archived:archives.length,archive_bytes:archives.reduce((n,r)=>n+r.gzip_bytes,0)}));
