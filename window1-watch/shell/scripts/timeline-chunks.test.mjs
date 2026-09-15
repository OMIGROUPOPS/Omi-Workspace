import test from 'node:test';
import assert from 'node:assert/strict';
import {splitTimeline} from '../../timeline_chunks.mjs';
import {decodeTimelinePreview,loadTimelineReceipt} from '../src/lib/timeline-chunks.ts';
test('scrubbing fetches only needed receipt chunks, validates hashes, preserves all markers',async()=>{
 const original=globalThis.fetch;let calls=0;
 const face={provenance:{event_id:'TEST',os_sha256:'os',trace_sha256:'trace'},os:Array.from({length:8},(_,index)=>({index,t:index,minutesToBell:8-index,kind:'DECISION_STAGE',clock_label:'recorded',title:'receipt',legs:{SIDE:{Q:index}}})),render:{columns:['minutesToBell','receipt_index'],ticks:[[8,0],[6,2],[1,7]],bid_actions:[{id:'original',leg:'SIDE',kind:'PLACE',receipt_index:2,card_lines:['stored']}],supersessions:[]}};
 face.legs=['SIDE'];for(const row of face.os)row.legs.SIDE.sentence={Q:row.index};
 const split=splitTimeline(face,3),chunks=new Map(split.chunks.map(c=>[c.descriptor.url,c.bytes]));
 globalThis.fetch=async url=>{calls++;return new Response(chunks.get(url))};
 try{
  const preview=structuredClone(split.face);decodeTimelinePreview(preview);
  assert.equal(calls,0);assert.equal(preview.render.bid_actions.length,1);assert.deepEqual(preview.render.ticks,face.render.ticks);
  assert(preview.os.every(r=>r.timeline_pending));
  assert.deepEqual(preview.os.map(r=>r.legs.SIDE.sentence.Q),face.os.map(r=>r.legs.SIDE.sentence.Q));
  await loadTimelineReceipt(preview,2);assert.equal(calls,1);assert.equal(preview.os[2].legs.SIDE.Q,2);assert(preview.os[7].timeline_pending);
  assert.equal(preview.render.bid_actions[0].id,'original');
  await loadTimelineReceipt(preview,1);assert.equal(calls,1);
  await loadTimelineReceipt(preview,7);assert.equal(calls,2);assert.equal(preview.os[7].legs.SIDE.Q,7);assert(preview.os[4].timeline_pending);
  globalThis.fetch=async()=>new Response('bad');
  await assert.rejects(loadTimelineReceipt(preview,4),/hash mismatch/);
 }finally{globalThis.fetch=original;}
});
