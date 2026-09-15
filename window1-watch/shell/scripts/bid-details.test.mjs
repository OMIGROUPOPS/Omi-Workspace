import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {loadBidDetail} from '../src/lib/bid-details.ts';
test('detail fetch is explicit, cached by game/hash, and rejects corrupt data',async()=>{
 const original=globalThis.fetch;let requests=0;
 const record={schema:'bid-card-details-v1',event:'TEST',os_sha256:'os',trace_sha256:'trace',actions:{bid_actions:[{id:'a',details_lines:['stored renewal']}],supersessions:[{id:'b',details_lines:['stored supersession']}]}};
 const bytes=JSON.stringify(record),source={...record,actions:undefined,detail_url:'/data/TEST.bid-details.json',sha256_uncompressed:createHash('sha256').update(bytes).digest('hex'),action_count:2};
 globalThis.fetch=async()=>{requests++;return new Response(bytes,{headers:{'content-type':'application/json'}})};
 try {
  assert.equal(requests,0);
  assert.deepEqual((await loadBidDetail(source,'a')).details_lines,['stored renewal']);
  assert.deepEqual((await loadBidDetail(source,'b')).details_lines,['stored supersession']);
  assert.equal(requests,1);
  await assert.rejects(loadBidDetail({...source,sha256_uncompressed:'wrong'},'a'),/hash mismatch/);
  await assert.rejects(loadBidDetail({...source,detail_url:'/other'},'a'),/Invalid/);
 }finally{globalThis.fetch=original;}
});
test('a pending timeline marker resolves its exact bounded bid-detail chunk',async()=>{
 const original=globalThis.fetch;const requests=[];
 const record={schema:'bid-card-details-v2',event:'CHUNK',os_sha256:'os',trace_sha256:'trace',group:'bid_actions',first:256,actions:[{id:'original-hash',details_lines:['stored original assumption']}]};
 const bytes=JSON.stringify(record),chunk={group:record.group,first:256,last:256,detail_url:'/data/CHUNK.bid-details/bid_actions-256.json',sha256_uncompressed:createHash('sha256').update(bytes).digest('hex'),bytes_uncompressed:Buffer.byteLength(bytes)};
 const source={schema:record.schema,event:record.event,os_sha256:record.os_sha256,trace_sha256:record.trace_sha256,action_count:257,chunks:[chunk]};
 globalThis.fetch=async url=>{requests.push(url);return new Response(bytes)};
 try{
  const result=await loadBidDetail(source,'timeline:bid_actions:256');
  assert.equal(result.id,'original-hash');
  assert.deepEqual(result.details_lines,record.actions[0].details_lines);
  assert.equal((await loadBidDetail(source,'original-hash','bid_actions:256')).id,result.id);
  assert.deepEqual(requests,[chunk.detail_url]);
  await assert.rejects(loadBidDetail(source,'timeline:bid_actions:255'),/Invalid/);
 }finally{globalThis.fetch=original}
});
