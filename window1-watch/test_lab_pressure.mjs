import test from 'node:test';
import assert from 'node:assert/strict';
import { projectStage, sha } from './build_lab_pressure.mjs';
const face={provenance:{event_id:'TEST'},legs:['LEFT','RIGHT'],bell:{timestamp_epoch:2000}};
const receipt={index:0,trace_row:2,receipt:'r',kind:'DECISION_STAGE',receipt_id:sha('DECISION_STAGE\0r\0'+2)};
const detail=()=>({source:{event_id:'TEST',trace_row:2},row:{event_id:'TEST',kind:'DECISION_STAGE',receipt:'r',timestamp_epoch:1000,
  reads:{volume:{status:'CONNECTED',timestamp_epoch:1000,value:{LEFT:{contracts:0,print_count:2}}}},layers:{}}});
test('zero is a real reading; missing pressure is not zero',()=>{
  const row=projectStage(face,receipt,detail(),'hash');
  assert.equal(row.legs.LEFT.values.contracts.value,0);
  assert.equal(row.legs.RIGHT.values.contracts.text,'no data here');
  assert.equal(row.legs.LEFT.values.maker_residual.value,null);
  assert.equal(row.legs.LEFT.values.maker_residual.text,'no data here');
});
test('future or disconnected reader cannot leak',()=>{
  const d=detail();d.row.reads.volume.timestamp_epoch=1001;
  assert.equal(projectStage(face,receipt,d,'hash').legs.LEFT.values.contracts.value,null);
  d.row.reads.volume.timestamp_epoch=1000;d.row.reads.volume.status='MISSING';
  assert.equal(projectStage(face,receipt,d,'hash').legs.LEFT.values.contracts.value,null);
});
test('event, receipt and stage line joins are exact',()=>{
  for(const mutate of [d=>d.source.event_id='OTHER',d=>d.row.receipt='other',d=>d.source.trace_row=3]){
    const d=detail();mutate(d);assert.throws(()=>projectStage(face,receipt,d,'hash'),/IDENTITY/);
  }
});
