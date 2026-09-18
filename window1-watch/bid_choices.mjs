// Display labels only. The riser's near-market candidates are read from one
// stored licensing receipt: its causal book (row.reads.books) and the OS-written
// entry_license. The OS alone decides which level is licensed; nothing here
// re-tests eligibility, the pair cap or the destination. "Discount left" is
// display arithmetic on two stored numbers, like the builder-written spread.
const finite = value => typeof value === 'number' && Number.isFinite(value);
const number = value => new Intl.NumberFormat('en-US', {maximumFractionDigits: 2}).format(value);
const cents = value => finite(value) ? `${number(value)}¢` : 'no data here';
export const RISER_CHOICE_COLUMNS = ['Level', 'Destination', 'Discount left', 'Choice'];
export function riserBidChoices(license, bid, ask) {
  if (license?.role !== 'CLIMBER') return null;
  const step = license.price_increment?.increment_cents, entry = license.entry_cents;
  const destination = license.destination_cents, waiting = license.waiting_reason ?? null;
  const destinationCell = finite(destination) ? `${cents(destination)} close` : 'no data here';
  const improved = finite(ask) && finite(step) ? ask - step : null;
  const candidates = [];
  if (finite(improved) && improved !== bid) candidates.push({name: `ask−${number(step)}`, level: improved,
    source: `row.reads.books ask ${ask} − stored price_increment ${step}`});
  if (finite(bid)) candidates.push({name: improved === bid ? `join best bid (= ask−${number(step)})` : 'join best bid', level: bid,
    source: `row.reads.books bid ${bid}`});
  // A renewed or held entry that is neither near-market candidate is shown as stored, never rounded onto one.
  if (finite(entry) && !candidates.some(c => c.level === entry)) candidates.push({name: 'stored licensed entry', level: entry,
    source: 'entry_license.entry_cents; not one of this receipt\'s two near-market candidates'});
  const held = finite(entry) && license.allowed !== true;
  const rows = candidates.map(c => {
    const chosen = c.level === entry;
    return {cells: [`${cents(c.level)} · ${c.name}`, destinationCell,
      finite(destination) ? cents(destination - c.level) : 'no data here',
      chosen ? license.allowed === true ? 'chosen' : 'best · waiting' : finite(entry) ? 'not chosen' : 'not licensed'],
      licensed: chosen && license.allowed === true,
      source: `${c.source}; destination ${destination}; licensed entry ${entry ?? 'none'}; allowed ${license.allowed}`};
  });
  rows.push({cells: ['wait', destinationCell, '—',
    license.allowed === true ? 'not chosen' : `chosen · ${waiting ?? 'no data here'}`], licensed: false,
    source: `entry_license.allowed ${license.allowed}; waiting_reason ${waiting ?? 'none'}${held ? '; entry retained but withheld' : ''}`});
  return {header: 'BID CHOICES · NEAR-MARKET ENTRY', columns: RISER_CHOICE_COLUMNS, rows,
    note: `Riser order of preference: ask−${finite(step) ? number(step) : '?'}, then join best bid, else wait. Discount left is destination minus level — a forecast close, not a realized one.`,
    raw_reason: license.written_reason ?? null,
    source: 'row.layers.micro.context.beliefs.entry_license + row.reads.books of the same receipt; the OS wrote the choice'};
}
