import {createHash} from 'node:crypto';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {gzipSync,gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {packFace,unpackFace} from './face_encoding.mjs';
const groups=['bid_actions','supersessions'];
const receiptColumns=['index','t','minutesToBell','kind','clock_label','title'];
const markerColumns=['leg','kind','glyph','stack_offset_px','card_lines','label','receipt_index','marker_cents','minutes_to_bell','fill','bid_accountability','bid_detail_key',
 'markers.play.display_progress','markers.play.boundary','markers.play.price','markers.inspection.display_progress','markers.inspection.boundary','markers.inspection.price'];
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const at=(row,key)=>key.split('.').reduce((v,k)=>v?.[k],row)??null;
const transpose=rows=>rows[0]?.map((_,i)=>rows.map(row=>row[i]))??[];
export function refreshTimelinePreview(main, full) {
 const columns=[...receiptColumns,...(full.legs??[]).map(leg=>`legs.${leg}.sentence.Q`)];
 const rows=full.os.map(row=>columns.map(key=>at(row,key)));
 return {...main,os:main.timeline?.receipt_storage==='columns'?transpose(rows):rows,
  timeline:{...main.timeline,receipt_columns:columns}};
}
export function columnizeTimelinePreview(main){
 if(!main.timeline)return main;
 const t=main.timeline,render={...main.render};
 if(t.marker_storage!=='columns')for(const key of groups)render[key]=transpose(render[key]);
 return {...main,render,os:t.receipt_storage==='columns'?main.os:transpose(main.os),
  timeline:{...t,receipt_storage:'columns',marker_storage:'columns'}};
}

export function splitTimeline(face,chunkSize=512){
 const event=face.provenance.event_id;assert.match(event,/^[A-Z0-9-]+$/);
 assert(face.os.every((r,i)=>r.index===i),'Timeline receipt positions must remain exact');
 const binding={schema:'face-timeline-v1',event,os_sha256:face.provenance.os_sha256,trace_sha256:face.provenance.trace_sha256};
 const chunks=[];
 for(let first=0;first<face.os.length;first+=chunkSize){
  const last=Math.min(first+chunkSize,face.os.length)-1;
  const actions=Object.fromEntries(groups.map(key=>[key,(face.render[key]??[]).flatMap((value,index)=>value.receipt_index>=first&&value.receipt_index<=last?[{index,value}]:[])]));
  const payload={...binding,first,last,os:face.os.slice(first,last+1),actions,
   ...(first===0&&face.dictionary?{original_dictionary:face.dictionary}:{})};
  const bytes=Buffer.from(JSON.stringify(packFace(payload))+'\n');
  chunks.push({descriptor:{first,last,url:`/data/${event}.timeline/${first}.json`,sha256_uncompressed:sha(bytes),bytes_uncompressed:bytes.length},bytes});
 }
 assert.equal(chunks.reduce((n,c)=>n+Object.values(JSON.parse(c.bytes).actions).reduce((m,a)=>m+a.length,0),0),groups.reduce((n,key)=>n+(face.render[key]?.length??0),0),'Every marker must belong to a receipt chunk');
 const render={...face.render,ticks:transpose(face.render.ticks)};
 for(const key of groups)render[key]=(face.render[key]??[]).map(row=>markerColumns.map(field=>at(row,field)));
 const main={...face,os:face.os.map(row=>receiptColumns.map(key=>at(row,key))),render,
  timeline:{...binding,receipt_columns:receiptColumns,marker_columns:markerColumns,tick_storage:'columns',chunks:chunks.map(c=>c.descriptor)}};
 delete main.dictionary;
 return {face:columnizeTimelinePreview(refreshTimelinePreview(main,face)),chunks};
}

export function hydrateTimeline(face,readBytes){
 if(!face.timeline)return face;
 const t=face.timeline,os=[],actions=Object.fromEntries(groups.map(key=>[key,new Array(t.marker_storage==='columns'?(face.render[key][0]?.length??0):face.render[key].length)]));
 assert.equal(t.schema,'face-timeline-v1');
 let dictionary;
 for(const d of t.chunks){
  const bytes=readBytes(d);assert.equal(sha(bytes),d.sha256_uncompressed,'Timeline hash mismatch');assert.equal(bytes.length,d.bytes_uncompressed);
  const chunk=unpackFace(JSON.parse(bytes));
  for(const key of ['schema','event','os_sha256','trace_sha256'])assert.equal(chunk[key],t[key]);
  assert.equal(chunk.first,d.first);assert.equal(chunk.last,d.last);assert.equal(os.length,d.first);
  os.push(...chunk.os);
  for(const key of groups)for(const item of chunk.actions[key]){assert.equal(actions[key][item.index],undefined);actions[key][item.index]=item.value;}
  if(chunk.original_dictionary)dictionary=chunk.original_dictionary;
 }
 assert.equal(os.length,t.receipt_storage==='columns'?face.os[0]?.length:face.os.length);
 for(const key of groups)assert.equal(actions[key].filter(Boolean).length,actions[key].length);
 const result={...face,os,render:{...face.render,...actions,ticks:transpose(face.render.ticks)}};
 delete result.timeline;
 if(dictionary)result.dictionary=dictionary;
 assert.equal(t.event,result.provenance.event_id);assert.equal(t.os_sha256,result.provenance.os_sha256);assert.equal(t.trace_sha256,result.provenance.trace_sha256);
 return result;
}

export function readTimelineChunks(face,dataRoot){
 return hydrateTimeline(face,d=>{
  assert.equal(d.url,`/data/${face.provenance.event_id}.timeline/${d.first}.json`);
  return gunzipSync(readFileSync(join(dataRoot,`${face.provenance.event_id}.timeline`,`${d.first}.json.gz`)));
 });
}

export function writeTimelineChunks(face,dataRoot){
 // Do not stringify an entire large OS timeline merely to decide to chunk it:
 // V8 has a per-string limit even when there is ample heap. Large timelines
 // enter the same bounded, lossless path directly.
 if(face.os.length<=512&&gzipSync(JSON.stringify(packFace(face))+'\n',{level:9}).length<2*1024*1024)return face;
 const split=splitTimeline(face);
 const byUrl=new Map(split.chunks.map(c=>[c.descriptor.url,c.bytes]));
 assert.deepEqual(hydrateTimeline(split.face,d=>byUrl.get(d.url)),face,'Lossless timeline round trip');
 const dir=join(dataRoot,`${face.provenance.event_id}.timeline`);mkdirSync(dir,{recursive:true});
 for(const c of split.chunks)writeFileSync(join(dir,`${c.descriptor.first}.json.gz`),gzipSync(c.bytes,{level:9}));
 return split.face;
}
