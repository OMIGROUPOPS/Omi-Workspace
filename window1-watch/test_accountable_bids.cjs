"use strict";
const test = require('node:test'), assert = require('node:assert/strict');
const os = require('../arb-executor/analysis/window1_v54_dual_belief_os.js');
function fixture() {
  const state = os.createTapeState({ event_id:'TEST', leg_ids:['A','B'], discovery_epoch:0,
    bell_epoch:100, formation_end_epochs:{A:0,B:0}, anchors_cents:{A:57,B:43} });
  state.current_epoch=10; state.receipt='place';
  state.legs.A.current_book={receipt:'book',bid_cents:57,ask_cents:60,last_trade_cents:59};
  state.legs.A.prints.push({receipt:'first',price_cents:59});
  state.positions.A.standing_target_cents=57;
  const d={leg_id:'A',receipt:'place',sentence:'full stored sentence',action:{action:'PLACE_REST',target_cents:57,reason:'RAW_HOLD'},
    derivation:{pricing_authority:{authority_source:'POOL_CASCADE:BASE'}},
    layered_dual_belief:{micro:{beliefs:{A:{plain_sentence:'Q 57 by 50',predicted_cents:57,belief_price_cents:59,
      deadline:{deadline_epoch:50},predicted_minutes_to_bell:1,q_author:'POOL_BASE',x_author:'POOL_BASE_FLOOR_MTB',
      pool_cascade:{selected_layer:'BASE',roles:{current_role:'CLIMBER'},layers:{BASE:{ess:10,member_count:10,weight_sum:10}}}}}}}};
  const first=os.accountableDecision(state,d); return {state,d,first};
}
function tick(f,epoch,extra={}) { const row={kind:'BOOK',leg_id:'A',receipt:`tick-${epoch}`,timestamp_epoch:epoch,...extra};
  os.observe(f.state,'A',row); return os.accountableRenewals(f.state,row).find(r=>r.leg_id==='A'); }
test('book-only renewal is unresolved and preserves frozen promise/position',()=>{
 const f=fixture(), saved=JSON.stringify(f.first.assumption), positions=JSON.stringify(f.state.positions);
 const r=tick(f,11,{bid_cents:57,ask_cents:58,last_trade_cents:59});
 assert.equal(r.status,'PENDING'); assert.equal(r.effect,'unresolved');assert.equal(r.hold_reason,'RAW_HOLD');
 assert.equal(r.remains_postable,true);assert.equal(r.reason_scope,'CARRIED_EXECUTED_REASON_NO_NEW_PRICING_DECISION');
 assert.equal(JSON.stringify(f.first.assumption),saved);assert.equal(JSON.stringify(f.state.positions),positions);
 assert.ok(Object.isFrozen(f.first.assumption));
});
test('support is not fulfilment; later on-time positive print fulfils',()=>{
 const f=fixture(); let r=tick(f,12,{kind:'PRINT',price_cents:58,size:3});
 assert.equal(r.effect,'supports'); assert.equal(r.status,'PENDING');
 r=tick(f,13,{kind:'PRINT',price_cents:57,size:3});assert.equal(r.status,'FULFILLED');
 assert.equal(tick(f,60).status,'FULFILLED');
});
test('zero-size, opposite-side and same-placement-time prints do not fulfil',()=>{
 const f=fixture();assert.equal(tick(f,10,{kind:'PRINT',price_cents:57,size:3}).status,'PENDING');
 assert.equal(tick(f,11,{kind:'PRINT',price_cents:57,size:0}).status,'PENDING');
 const row={kind:'PRINT',leg_id:'B',receipt:'sibling',timestamp_epoch:12,price_cents:40,size:3};
 os.observe(f.state,'B',row);assert.equal(os.accountableRenewals(f.state,row)[0].status,'PENDING');
});
test('deadline fails only once; late witness cannot erase the miss',()=>{
 const f=fixture();let r=tick(f,50);assert.equal(r.status,'MISSED_AT_DEADLINE');assert.equal(r.effect,'contradicts');
 r=tick(f,51,{kind:'PRINT',price_cents:57,size:3});assert.equal(r.status,'MISSED_AT_DEADLINE');
 assert.equal(f.state.bid_accountability.lines.filter(r=>r.kind==='ASSUMPTION_OUTCOME').length,1);
});
test('same-price changed-X HOLD explicitly supersedes and original outcome is retained',()=>{
 const f=fixture();f.state.current_epoch=20;f.state.receipt=f.d.receipt='renew';f.d.action.action='HOLD_REST';
 f.d.layered_dual_belief.micro.beliefs.A.deadline.deadline_epoch=70;
 const next=os.accountableDecision(f.state,f.d);assert.equal(next.supersession.old_assumption_id,f.first.assumption.assumption_id);
 assert.ok(next.supersession.reasons.includes('AUTHORITY_FORECAST_DEADLINE_CHANGED'));
 assert.equal(f.first.assumption.X_epoch,50);assert.equal(next.assumption.X_epoch,70);
 tick(f,55);const outcome=f.state.bid_accountability.lines.find(r=>r.kind==='ASSUMPTION_OUTCOME');
 assert.equal(outcome.assumption_id,f.first.assumption.assumption_id);assert.equal(outcome.superseded,true);
});
test('author change and reprice have explicit links; unchanged HOLD does not supersede',()=>{
 const f=fixture();f.d.action.action='HOLD_REST';f.d.receipt=f.state.receipt='same';
 assert.equal(os.accountableDecision(f.state,f.d).supersession,null);
 f.d.layered_dual_belief.micro.beliefs.A.q_author='POOL_FIRST';
 assert.ok(os.accountableDecision(f.state,f.d).supersession.reasons.includes('AUTHORITY_CHANGE'));
 f.state.current_epoch=22;f.d.receipt=f.state.receipt='move';f.d.action={action:'REPRICE_REST',target_cents:56,reason:'RAW_REPRICE'};
 f.state.positions.A.standing_target_cents=56;
 assert.ok(os.accountableDecision(f.state,f.d).supersession.reason);
});
test('fill tick renews the old bid before closing; later ticks do not renew a filled bid',()=>{
 const f=fixture(), row={kind:'PRINT',leg_id:'A',receipt:'fill',timestamp_epoch:20,price_cents:57,size:2};
 os.creditPosition(f.state,'A',row);os.observe(f.state,'A',row);
 const r=os.accountableRenewals(f.state,row)[0];assert.equal(r.disposition,'FILLED');assert.equal(r.status,'FULFILLED');
 assert.equal(tick(f,21),undefined);
});
test('unknown book/deadline stay unknown, not evidence or permission',()=>{
 const f=fixture();f.d.layered_dual_belief.micro.beliefs.A.deadline.deadline_epoch=null;
 f.d.receipt=f.state.receipt='unknown';os.accountableDecision(f.state,f.d);
 f.state.legs.A.current_book=null;const r=tick(f,60,{kind:'PRINT',price_cents:56,size:2});
 assert.equal(r.remains_postable,null);assert.equal(r.status,'PENDING');
});
