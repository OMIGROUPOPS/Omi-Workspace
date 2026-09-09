import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import {unpackFace} from './face_encoding.mjs';
const face=unpackFace(JSON.parse(fs.readFileSync(new URL('./data/KXATPMATCH-26JUL12ALTGAS.face.json',import.meta.url))));
test('every bid marker has immutable assumption and as-of renewal; four lines remain',()=>{
 for(const a of face.render.bid_actions){
  assert.ok(a.bid_accountability?.assumption,`${a.kind} ${a.receipt}`);
  assert.ok(a.bid_accountability?.renewal,`${a.kind} ${a.receipt}`);
  assert.equal(a.card_lines.length,4);
  assert.ok(a.details_lines.some(l=>l.startsWith('Immutable assumption:')));
 }
});
test('supersessions are linked, small, and not duplicated in grade order inputs',()=>{
 assert.ok(face.render.supersessions.length);
 for(const a of face.render.supersessions){
  assert.equal(a.glyph,'◦');assert.equal(a.card_lines.length,4);
  const s=a.bid_accountability.supersession;assert.ok(s.old_assumption_id&&s.new_assumption_id&&s.reason);
  assert.ok(!face.render.bid_actions.some(b=>b.id===a.id));
 }
});
test('baseline fills and ALT first reprice preserved; row 272 has a carried hold reason',()=>{
 assert.deepEqual(face.render.bid_actions.filter(a=>a.kind==='FILL').map(a=>[a.leg,a.fill.cents]).sort(),[['ALT',60],['GAS',38]]);
 const a=face.render.bid_actions.find(a=>a.leg==='ALT'&&a.kind==='REPRICE');
 assert.deepEqual([a.old_cents,a.new_cents],[57,56]);assert.ok(a.bid_accountability.supersession);
 const audit=JSON.parse(zlib.gunzipSync(fs.readFileSync(new URL('.'+face.accountability.detail_url+'.gz',import.meta.url))));
 const r=audit.rows.find(r=>r.kind==='BID_RENEWAL'&&r.leg_id==='ALT'&&r.tick_receipt==='KXATPMATCH-26JUL12ALTGAS-ALT.csv.gz#row-272');
 assert.equal(r.status,'PENDING');assert.equal(r.effect,'unresolved');assert.equal(r.hold_reason,'PRICING_AUTHORITY_TARGET_EXECUTED');
 assert.equal(r.reason_scope,'CARRIED_EXECUTED_REASON_NO_NEW_PRICING_DECISION');
});
