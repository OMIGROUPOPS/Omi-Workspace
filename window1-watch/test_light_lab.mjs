import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {unpackFace} from './face_encoding.mjs';
import {projectExecutions,tMinus,sha} from './build_lab_pressure.mjs';
const data=new URL('./data/',import.meta.url);
const read=file=>JSON.parse(readFileSync(new URL(file,data)));
const games=read('index.json').games;
test('all five sidecars remain bound; executions match stored fills, not later calls',()=>{
  for(const {event} of games) {
    const bytes=readFileSync(new URL(`${event}.face.json`,data)),face=unpackFace(JSON.parse(bytes)),raw=read(`${event}.pressure.json`);
    assert.equal(raw.provenance.face_sha256,sha(bytes));
    assert.equal(raw.provenance.os_sha256,face.provenance.os_sha256);
    assert.equal(raw.provenance.trace_sha256,face.provenance.trace_sha256);
    assert.equal(raw.missing_receipt_indices.length,0);
    assert.deepEqual(projectExecutions(face),raw.executions);
    for(const fill of face.render.bid_actions.filter(a=>a.fill)) {
      const execution=raw.executions.find(e=>e.action_id===fill.id);
      assert.equal(execution.cents,fill.fill.cents);
      assert.ok(execution.origin_receipt_index<=fill.receipt_index);
      const origin=face.render.bid_actions.find(a=>a.leg===fill.leg&&a.receipt_index===execution.origin_receipt_index&&a.new_cents===fill.fill.cents);
      assert.ok(origin);assert.equal(execution.q_cents,origin.sentence.Q);
      assert.equal(execution.card_lines.length,4);
      assert.equal(execution.price_age_minutes,(fill.timestamp_epoch-origin.timestamp_epoch)/60);
    }
    const rows=unpackFace({os:raw.rows,dictionary:raw.dictionary}).os;
    for(const r of rows)for(const side of face.legs) {
      assert.equal(r.minutes_to_bell,face.os[r.receipt_index].minutesToBell);
      for(const v of Object.values(r.legs[side].values))if(v.value!==null)assert.ok(v.source_epoch<=r.timestamp_epoch);
      for(const key of ['taker_flow','maker_residual','refill_ratio','queue','open_interest'])assert.equal(r.legs[side].values[key].value,null);
    }
  }
});
test('call-to-fill lineage survives same-price holds; removes canceled lineage',()=>{
  const action=(i,kind,c,q)=>({id:String(i),leg:'X',receipt_index:i,receipt:String(i),timestamp_epoch:i,kind,new_cents:c,old_cents:i===1?null:50,sentence:{Q:q}});
  const face={bell:{timestamp_epoch:600},render:{bid_actions:[action(1,'PLACE',50,50),action(2,'HOLD',50,51),{...action(3,'FILL',null,null),fill:{cents:50,triggering_print_cents:49,floor_line:'source floor'}},]}};
  const x=projectExecutions(face).at(-1);assert.equal(x.q_cents,50);assert.equal(x.origin_receipt_index,1);
  face.render.bid_actions=[action(1,'PLACE',50,50),action(2,'CANCEL',null,null),action(3,'PLACE',50,52)];
  assert.equal(projectExecutions(face).at(-1).origin_receipt_index,3);
  assert.equal(tMinus(169.28),'T - 2hr 49 min');assert.equal(tMinus(null),'no data here');
});
