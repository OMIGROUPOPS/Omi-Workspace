import test from 'node:test';
import assert from 'node:assert/strict';
import {splitTimeline,hydrateTimeline} from './timeline_chunks.mjs';
const face={provenance:{event_id:'TEST',os_sha256:'os',trace_sha256:'trace'},os:Array.from({length:8},(_,i)=>({index:i,t:i,minutesToBell:8-i,kind:'DECISION_STAGE',clock_label:'recorded',title:'receipt',legs:{SIDE:{Q:i}}})),render:{columns:['minutesToBell','receipt_index'],ticks:[[8,0],[6,2],[1,7]],bid_actions:[{id:'real-hash:SIDE',leg:'SIDE',kind:'PLACE',receipt_index:2,marker_cents:17,minutes_to_bell:6,card_lines:['stored']}],supersessions:[]}};
test('timeline chunking retains every receipt, marker, original ID and tick exactly',()=>{
 const split=splitTimeline(face,3),map=new Map(split.chunks.map(c=>[c.descriptor.url,c.bytes]));
 assert.equal(split.chunks.length,3);
 assert.deepEqual(hydrateTimeline(split.face,d=>map.get(d.url)),face);
 assert.throws(()=>hydrateTimeline(split.face,()=>Buffer.from('broken')),/hash mismatch/);
});
