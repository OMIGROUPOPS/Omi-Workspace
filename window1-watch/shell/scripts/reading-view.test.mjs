import test from 'node:test';
import assert from 'node:assert/strict';
import { bellTime, cents, plain, readingCard, readingSentence } from '../src/lib/reading-view.ts';
test('sentence is display formatting of the stored call, not a new forecast',()=>{
  assert.equal(readingSentence({status:'RESOLVED',Q:61,X:369.6333333333333}),'Believes 61¢ by 6:10 to the bell.');
  assert.equal(readingSentence({status:'INSUFFICIENT_EVIDENCE',Q:61,X:369}),'Not enough evidence for a new bid.');
  assert.equal(readingSentence(),'No forecast here yet.');
  assert.equal(bellTime(null),'no time recorded');
  assert.equal(cents(null),'no data here');
  assert.equal(plain('STORE SILENT — missing depth'),'no data here — missing depth');
});
test('bid cards retain existing prose; supersessions translate only stored facts',()=>{
  const normal={kind:'REPRICE',card_lines:['ALT · Moved bid 57¢ → 56¢','Why: forecast moved']};
  assert.deepEqual(readingCard(normal),normal.card_lines);
  const a={kind:'SUPERSESSION',card_lines:['GAS · Renewed assumption; bid 41¢','Why: author changed'],minutes_to_bell:480,bid_accountability:{assumption:{Q:41,X_minutes_to_bell:240,member_count:26},renewal:{status:'PENDING'}}};
  assert.deepEqual(readingCard(a),['GAS · Renewed assumption; bid 41¢','Why: author changed','Believed: 41¢ by 4:00 to bell · promise pending','Pool of 26 games · 8:00 to bell']);
});
