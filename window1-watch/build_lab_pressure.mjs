// Display-only projection of stored reads. Never runs the OS or infers flow.
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync } from 'node:zlib';
import { packFace, unpackFace } from './face_encoding.mjs';

const here = dirname(fileURLToPath(import.meta.url));
export const sha = value => createHash('sha256').update(value).digest('hex');
const finite = value => typeof value === 'number' && Number.isFinite(value);
const number = value => new Intl.NumberFormat('en-US', {maximumFractionDigits: 2}).format(value);
const absent = 'no data here';
const fields = [
  ['contracts', 'Contracts traded', 'volume', 'contracts', 'contracts'],
  ['prints', 'True prints', 'volume', 'print_count', 'prints'],
  ['bid_depth', 'Bid size · five levels', 'depth_size', 'bid_depth_5', 'contracts'],
  ['ask_depth', 'Ask size · five levels', 'depth_size', 'ask_depth_5', 'contracts'],
  ['top_bid', 'Best bid size', 'depth_size', 'top_bid_size', 'contracts'],
  ['top_ask', 'Best ask size', 'depth_size', 'top_ask_size', 'contracts'],
];
export function projectStage(face, receipt, detail, sourceSha) {
  const row = detail.row, event = face.provenance.event_id;
  if (detail.source?.event_id !== event || row.event_id !== event ||
      detail.source?.trace_row !== receipt.trace_row || row.receipt !== receipt.receipt ||
      row.kind !== receipt.kind) throw new Error('PRESSURE_STAGE_IDENTITY_MISMATCH');
  const id = sha(`${row.kind}\0${row.receipt}\0${receipt.trace_row}`);
  if (id !== receipt.receipt_id) throw new Error('PRESSURE_RECEIPT_ID_MISMATCH');
  if (!finite(row.timestamp_epoch)) throw new Error('PRESSURE_STAGE_CLOCK_MISSING');
  const pool = row.layers?.macro?.context?.pool_cascade ??
    row.derivations?.find(x => x.derivation?.pool_cascade)?.derivation?.pool_cascade;
  const read = (reader, key, side) => {
    const value = row.reads?.[reader];
    const result = value?.value?.[side]?.[key];
    const valid = value?.status === 'CONNECTED' && finite(value.timestamp_epoch) &&
      value.timestamp_epoch <= row.timestamp_epoch && finite(result);
    return {value: valid ? result : null, source: `row.reads.${reader}.value.${side}.${key}`,
      source_epoch: value?.timestamp_epoch ?? null,
      reason: valid ? null : 'This receipt has no connected, causal numeric reading.'};
  };
  const legs = Object.fromEntries(face.legs.map(side => {
    const values = Object.fromEntries(fields.map(([key, label, reader, field, unit]) => {
      const result = read(reader, field, side);
      return [key, {...result, label, unit, text: result.value === null ? absent : `${number(result.value)} ${unit}`}];
    }));
    // A quote-size snapshot does not identify selling, consumption or maker pull.
    // The verified recovery is library-only. Do not join a library member to a
    // loaded named check, substitute arithmetic for API direction, or emit zero.
    for (const [key, label] of [['taker_flow','Buying / selling'],['maker_residual','Maker add / pull'],
      ['refill_ratio','Refill'],['queue','Size at our bid'],['open_interest','Open interest']]) {
      values[key] = {label, value:null, text:absent, unit:null, source:null, source_epoch:null,
        reason:'No exact game / receipt / span-bound feature is present in this replay. Library recovery is not a named-game measurement.'};
    }
    const sidePool = pool?.sides?.[side], selected = sidePool?.layers?.[sidePool.selected_layer];
    const q = selected?.floors?.q50?.level_cents, count = selected?.member_count;
    const author = finite(q) && finite(count) ? `${number(q)}¢ · pool of ${number(count)} games` : absent;
    return [side, {values, cards:[
      {label:'Trading', text:`${values.contracts.text} · ${values.prints.text}`, keys:['contracts','prints']},
      {label:'Book · bid / ask size', text:values.bid_depth.value !== null && values.ask_depth.value !== null ?
        `${number(values.bid_depth.value)} / ${number(values.ask_depth.value)}` : absent,
        keys:['bid_depth','ask_depth','top_bid','top_ask']},
      {label:'Flow / maker pressure', text:absent, keys:['taker_flow','maker_residual','refill_ratio','queue','open_interest']},
      {label:'Current call', text:author, keys:[], source:'row.layers.macro.context.pool_cascade.sides (or stored derivation)',
        raw_layer:sidePool?.selected_layer ?? null, q_cents:finite(q)?q:null, member_count:finite(count)?count:null,
        note:'The recorded pool authored this call. The displayed volume and depth are not proof that these readings authored it.'},
    ]}];
  }));
  const joint = row.reads?.joint_state_spread_dwell;
  const sum = joint?.status === 'CONNECTED' && finite(joint.timestamp_epoch) && joint.timestamp_epoch <= row.timestamp_epoch
    ? joint.value?.mid_sum_cents : null;
  const minutes = (face.bell.timestamp_epoch - row.timestamp_epoch) / 60;
  const rounded = Math.round(Math.abs(minutes));
  return {receipt_index:receipt.index, receipt_id:receipt.receipt_id, receipt:receipt.receipt,
    trace_row:receipt.trace_row, timestamp_epoch:row.timestamp_epoch, minutes_to_bell:minutes,
    clock_label:`T ${minutes < 0 ? '+' : '-'} ${Math.floor(rounded/60)}hr ${rounded%60} min`,
    stage_sha256:sourceSha, legs,
    pair:{mid_sum_cents:finite(sum)?sum:null, text:finite(sum)?`Pair book midpoints ${number(sum)}¢`:absent,
      source:'row.reads.joint_state_spread_dwell.value.mid_sum_cents'},
  };
}

export function buildPressure(dataRoot, event) {
  if (!/^[A-Z0-9-]+$/.test(event)) throw new Error('Invalid pressure event');
  const bytes = readFileSync(resolve(dataRoot, `${event}.face.json`));
  const face = unpackFace(JSON.parse(bytes)), rows = [], missing = [];
  for (const receipt of face.os) {
    if (receipt.kind !== 'DECISION_STAGE') continue;
    const relative = `${event}.stages/${receipt.receipt_id}.json.gz`;
    if (receipt.detail_url !== `/data/${relative.slice(0,-3)}`) throw new Error('PRESSURE_STAGE_PATH_MISMATCH');
    const file = resolve(dataRoot, relative);
    if (!file.startsWith(resolve(dataRoot)+sep)) throw new Error('Unsafe stage path');
    if (!existsSync(file)) { missing.push(receipt.index); continue; }
    const content = gunzipSync(readFileSync(file));
    rows.push(projectStage(face, receipt, JSON.parse(content), sha(content)));
  }
  rows.sort((a,b) => a.timestamp_epoch-b.timestamp_epoch || a.receipt_index-b.receipt_index);
  const encoded = packFace({os:rows});
  const result = {schema:'LAB_PRESSURE_READS_V1', event,
    provenance:{face_sha256:sha(bytes), os_sha256:face.provenance.os_sha256,
      trace_sha256:face.provenance.trace_sha256, builder_sha256:sha(readFileSync(fileURLToPath(import.meta.url)))},
    policy:'Stored receipt reads only. Last recorded receipt is explicitly carried between receipts; never a current-tick estimate. No engine, pricing or grade changes.',
    missing_receipt_indices:missing, rows:encoded.os, dictionary:encoded.dictionary};
  const payload = JSON.stringify(result)+'\n';
  writeFileSync(resolve(dataRoot, `${event}.pressure.json`), payload);
  return {event, rows:rows.length, missing:missing.length, bytes:Buffer.byteLength(payload), sha256:sha(payload)};
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const data = resolve(here,'data');
  const games = process.argv[2] ? [process.argv[2]] : JSON.parse(readFileSync(resolve(data,'index.json'))).games.map(g=>g.event);
  for (const event of games) console.log(JSON.stringify(buildPressure(data,event)));
}
