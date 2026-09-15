import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync,mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {gunzipSync,gzipSync} from 'node:zlib';
import {splitBidDetails,hydrateBidDetails,writeBidDetails,readBidDetails} from './bid_card_details.mjs';
import {packFace,unpackFace} from './face_encoding.mjs';
const fixture={provenance:{event_id:'TEST',os_sha256:'os',trace_sha256:'trace'},os:[],render:{
  bid_actions:[{id:'one',kind:'PLACE',card_lines:['one','two','three','four'],raw:{reason:'stored'},
    bid_accountability:{assumption:{Q:31},renewal:{status:'PENDING'}},details_lines:['Original record'],arbitrary_future_field:[null,{x:1}]}],
  supersessions:[{id:'two',kind:'SUPERSESSION',card_lines:['renewed'],bid_accountability:{supersession:{old_assumption_id:'a',new_assumption_id:'b'}}}]}};
test('all fields and original values survive lazy projection, including unknown future fields',()=>{
  const split=splitBidDetails(fixture);
  assert.equal(split.face.render.bid_actions[0].details_lines,undefined);
  assert.deepEqual(hydrateBidDetails(split.face,split.bytes),fixture);
  assert.deepEqual(hydrateBidDetails(unpackFace(packFace(split.face)),split.bytes),unpackFace(packFace(fixture)));
  assert.equal(split.face.bid_card_details.action_count,2);
});
test('wrong bytes, source provenance and preview mutation fail closed',()=>{
  const split=splitBidDetails(fixture);
  assert.throws(()=>hydrateBidDetails(split.face,Buffer.concat([split.bytes,Buffer.from(' ')])),/hash mismatch/);
  const wrong=structuredClone(split.face);wrong.provenance.trace_sha256='other';
  assert.throws(()=>hydrateBidDetails(wrong,split.bytes));
  const changed=structuredClone(split.face);changed.render.bid_actions[0].card_lines=['invented'];
  assert.throws(()=>hydrateBidDetails(changed,split.bytes));
});
test('old inline faces remain readable without a sidecar',()=>assert.equal(hydrateBidDetails(fixture,null),fixture));
test('large bid histories use bounded chunks and reconstruct every action',()=>{
 const face=structuredClone(fixture);face.render.bid_actions=Array.from({length:520},(_,i)=>({...face.render.bid_actions[0],id:'action-'+i}));
 const root=mkdtempSync(join(tmpdir(),'bid-chunk-test-')),stored=writeBidDetails(face,root);
 assert.equal(stored.bid_card_details.schema,'bid-card-details-v2');
 assert.equal(stored.bid_card_details.chunks.length,4);
 assert.deepEqual(readBidDetails(stored,root),face);
});
const oversized='C:/tmp/unsupported_rests_20260914/runs/KXATPCHALLENGERMATCH-26JUL14GANZIN/FACE_OVERSIZE.json.gz';
test('GANZIN all 7047 action records round-trip; compressed main stays below 2 MiB',{skip:!existsSync(oversized)},()=>{
  const face=unpackFace(JSON.parse(gunzipSync(readFileSync(oversized))));
  const split=splitBidDetails(face);
  assert.deepEqual(hydrateBidDetails(split.face,split.bytes),face);
  assert(gzipSync(JSON.stringify(packFace(split.face))+'\n',{level:9}).length<2*1024*1024);
});
