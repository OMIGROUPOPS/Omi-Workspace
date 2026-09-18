import test from 'node:test';
import assert from 'node:assert/strict';
import { riserBidChoices } from './bid_choices.mjs';
const license = extra => ({role:'CLIMBER', allowed:true, entry_cents:55, destination_cents:66,
  price_increment:{increment_cents:1}, waiting_reason:null, written_reason:'stored reason', ...extra});
const choice = (table, name) => table.rows.find(r => r.cells[0].includes(name))?.cells[3];
test('only a riser gets near-market candidates', () => {
  assert.equal(riserBidChoices({role:'FALLER'}, 53, 56), null);
  assert.equal(riserBidChoices(undefined, 53, 56), null);
});
test('the stored licensed entry marks the chosen candidate; nothing is re-licensed', () => {
  const t = riserBidChoices(license(), 53, 56);
  assert.deepEqual(t.rows.map(r => r.cells[0]), ['55¢ · ask−1', '53¢ · join best bid', 'wait']);
  assert.deepEqual(t.rows.map(r => r.cells[2]), ['11¢', '13¢', '—']);
  assert.deepEqual(t.rows.map(r => r.licensed), [true, false, false]);
  assert.equal(choice(t, 'join best bid'), 'not chosen');
  assert.equal(t.raw_reason, 'stored reason');
  const joined = riserBidChoices(license({entry_cents:53}), 53, 56);
  assert.equal(choice(joined, 'join best bid'), 'chosen');
  assert.equal(choice(joined, 'ask−1'), 'not chosen');
});
test('waiting is the chosen row and keeps the OS reason verbatim', () => {
  const t = riserBidChoices(license({allowed:false, entry_cents:null, waiting_reason:'counterpart has no eligible purchase plan'}), 58, 59);
  assert.deepEqual(t.rows.map(r => r.cells[3]), ['not licensed', 'chosen · counterpart has no eligible purchase plan']);
  assert(t.rows.every(r => !r.licensed));
});
test('a withheld entry is best but waiting, never licensed', () => {
  const t = riserBidChoices(license({allowed:false, entry_cents:53, waiting_reason:'entry withheld by VETO'}), 53, 54);
  assert.equal(t.rows[0].cells[0], '53¢ · join best bid (= ask−1)');
  assert.equal(t.rows[0].cells[3], 'best · waiting');
  assert.equal(t.rows[0].licensed, false);
  assert.equal(t.rows.at(-1).cells[3], 'chosen · entry withheld by VETO');
});
test('a stored entry off both candidates is shown as stored; a missing book invents no level', () => {
  const kept = riserBidChoices(license({entry_cents:50}), 53, 56);
  assert.equal(choice(kept, 'stored licensed entry'), 'chosen');
  const blind = riserBidChoices(license({allowed:false, entry_cents:null, waiting_reason:'missing or locked book'}), null, null);
  assert.deepEqual(blind.rows.map(r => r.cells[0]), ['wait']);
});
test('an unresolved destination is absent, not a labelled close', () => {
  const t = riserBidChoices(license({allowed:false, entry_cents:null, destination_cents:null, waiting_reason:'too few direction-matched past games'}), 56, 59);
  assert.deepEqual(t.rows[0].cells.slice(1, 3), ['no data here', 'no data here']);
});
