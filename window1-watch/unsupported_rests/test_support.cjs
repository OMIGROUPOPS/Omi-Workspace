// Synthetic boundary tests only; these fixture numbers never enter the OS.
const assert = require('node:assert/strict');
const os = require('../../arb-executor/analysis/window1_v54_dual_belief_os.js');
const builder = require('../../arb-executor/analysis/build_window1_v54_dual_belief.js');
const old = { assumption_id: 'fixture', Q: 40, X_epoch: 100, q_author: 'POOL_BASE', x_author: 'POOL_BASE_FLOOR_MTB', authority_source: 'POOL_CASCADE:BASE' };
function fixture(status = 'PENDING', now = 101) {
  return { leg_ids: ['SIDE'], receipt: 'current', current_epoch: now,
    positions: { SIDE: { standing_target_cents: 40, credited: false } },
    bid_accountability: { active: { SIDE: old }, monitors: new Map([['fixture', { status }]]) } };
}
function sentence(Q = 40, X = 110, status = 'RESOLVED') {
  return { predicted_cents: Q, status, q_author: old.q_author, x_author: old.x_author,
    deadline: { deadline_epoch: X, emitted_at_receipt: 'current', emitted_at_epoch: 101 } };
}
const check = (s,b,t=40,reason='POST_ONLY_BLOCKED',review=false) => os.restSupportDecision(s,'SIDE',b,{authority_source:old.authority_source},t,reason,review);
const tests = [];
function test(name,fn){fn();tests.push(name);}
test('expired exact level with future freshly emitted deadline is renewed',()=>assert.equal(check(fixture(),sentence()).pull,false));
test('new Q blocked by post-only cannot retain the old rest',()=>assert.equal(check(fixture(),sentence(45)).pull,true));
test('new Q blocked by pair cap cannot retain the old rest',()=>assert.equal(check(fixture(),sentence(45),40,'PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE').pull,true));
test('expired Q with no future deadline is pulled',()=>assert.equal(check(fixture(),sentence(40,101)).pull,true));
test('unresolved sentence cannot renew',()=>assert.equal(check(fixture(),sentence(40,110,'INSUFFICIENT_EVIDENCE')).pull,true));
test('stale emission cannot renew',()=>{const b=sentence();b.deadline.emitted_at_receipt='prior';assert.equal(check(fixture(),b).pull,true);});
test('existing veto cancellation is not overturned',()=>assert.equal(check(fixture(),sentence(),null,'VETO').pull,true));
test('postable new target may supersede in a normal decision',()=>assert.equal(check(fixture(),sentence(45),45).replacement_supported,true));
test('pre-print review cannot reprice to the incoming print',()=>assert.equal(check(fixture(),sentence(45),45,'POSTABLE',true).pull,true));
test('unexpired unchanged promise is not subject to a new rule',()=>{const s=fixture('PENDING',99),b=sentence(40,100);assert.equal(check(s,b).required,false);});
test('same deadline instant may still fulfill before review',()=>assert.deepEqual(os.expiredRestLegIds(fixture(),100),[]));
test('later print must first review overdue rest',()=>assert.deepEqual(os.expiredRestLegIds(fixture(),101),['SIDE']));
test('fulfilled promise is not reclassified missed',()=>assert.deepEqual(os.expiredRestLegIds(fixture('FULFILLED'),101),[]));
test('recorded missed promise is reviewed',()=>assert.deepEqual(os.expiredRestLegIds(fixture('MISSED_AT_DEADLINE'),99),['SIDE']));
const row={event_id:'fixture',code:'26JAN01',category:'fixture',legA:'A',legB:'B',verified_span:'OK',bell_epoch:200,span_end_epoch:100};
test('corrected later bell extends replay but not verified span',()=>{const m=builder.targetMeta(row);assert.equal(m.bell_epoch,200);assert.equal(m.span_end_epoch,100);assert.equal(m.bell_alignment.delta_seconds,100);});
test('unknown lawful span remains unknown',()=>assert.equal(builder.targetMeta({...row,verified_span:'UNKNOWN'}).bell_epoch,null));
test('absent ruler bell preserves earlier behavior',()=>assert.equal(builder.targetMeta({...row,bell_epoch:null}).bell_epoch,100));
test('earlier ruler bell remains earlier',()=>assert.equal(builder.targetMeta({...row,bell_epoch:90}).bell_epoch,90));
console.log(JSON.stringify({passed:tests.length,tests},null,2));
