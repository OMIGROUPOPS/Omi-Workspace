import {createHash} from 'node:crypto';
import {mkdirSync,readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {gzipSync, gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {readTimelineChunks} from './timeline_chunks.mjs';

const groups = ['bid_actions', 'supersessions'];
const previewKeys = ['id', 'leg', 'kind', 'glyph', 'stack_offset_px', 'card_lines', 'label',
  'receipt_index', 'markers', 'marker_cents', 'minutes_to_bell', 'fill'];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');

// Storage projection only: the full original action objects remain byte-value exact.
export function splitBidDetails(face) {
  const event = face.provenance.event_id;
  assert.match(event, /^[A-Z0-9-]+$/);
  const detail = {schema: 'bid-card-details-v1', event,
    os_sha256: face.provenance.os_sha256, trace_sha256: face.provenance.trace_sha256,
    actions: Object.fromEntries(groups.map(key => [key, face.render[key] ?? []]))};
  const bytes = Buffer.from(JSON.stringify(detail) + '\n');
  const descriptor = {schema: detail.schema, event, os_sha256: detail.os_sha256,
    trace_sha256: detail.trace_sha256, detail_url: `/data/${event}.bid-details.json`,
    sha256_uncompressed: sha(bytes), bytes_uncompressed: bytes.length,
    action_count: groups.reduce((n, key) => n + detail.actions[key].length, 0)};
  const render = {...face.render};
  for (const key of groups) render[key] = detail.actions[key].map(action => {
    const preview = Object.fromEntries(previewKeys.filter(k => k in action).map(k => [k, action[k]]));
    // Preserve the existing supersession front without loading its verbose audit.
    if (key === 'supersessions') preview.bid_accountability = action.bid_accountability;
    return preview;
  });
  return {face: {...face, render, bid_card_details: descriptor}, bytes};
}

export function hydrateBidDetails(face, bytes) {
  if (!face.bid_card_details) return face;
  const d = face.bid_card_details;
  assert.equal(sha(bytes), d.sha256_uncompressed, 'Bid-card detail hash mismatch');
  const detail = JSON.parse(bytes);
  assert.equal(detail.schema, 'bid-card-details-v1');
  assert.equal(bytes.length, d.bytes_uncompressed);
  assert.equal(groups.reduce((n, key) => n + detail.actions[key].length, 0), d.action_count);
  for (const key of ['event', 'os_sha256', 'trace_sha256']) assert.equal(detail[key], d[key]);
  assert.equal(detail.event, face.provenance.event_id);
  assert.equal(detail.os_sha256, face.provenance.os_sha256);
  assert.equal(detail.trace_sha256, face.provenance.trace_sha256);
  const render = {...face.render};
  for (const key of groups) {
    assert.equal(detail.actions[key].length, face.render[key].length);
    face.render[key].forEach((preview, i) => {
      for (const [field, value] of Object.entries(preview)) assert.deepEqual(detail.actions[key][i][field], value);
    });
    render[key] = detail.actions[key];
  }
  const result = {...face, render};
  delete result.bid_card_details;
  return result;
}

export function readBidDetails(face, dataRoot) {
  face=readTimelineChunks(face,dataRoot);
  if (!face.bid_card_details) return face;
  assert.match(face.provenance.event_id, /^[A-Z0-9-]+$/);
  if(face.bid_card_details.schema==='bid-card-details-v2'){
    const d=face.bid_card_details,render={...face.render};
    for(const group of groups)render[group]=[];
    for(const c of d.chunks){
      assert.equal(c.detail_url,`/data/${d.event}.bid-details/${c.group}-${c.first}.json`);
      const bytes=gunzipSync(readFileSync(join(dataRoot,`${d.event}.bid-details`,`${c.group}-${c.first}.json.gz`)));
      assert.equal(sha(bytes),c.sha256_uncompressed);assert.equal(bytes.length,c.bytes_uncompressed);
      const part=JSON.parse(bytes);for(const k of ['schema','event','os_sha256','trace_sha256'])assert.equal(part[k],d[k]);
      assert.equal(part.group,c.group);assert.equal(part.first,c.first);assert.equal(render[c.group].length,c.first);
      assert.equal(part.actions.length,c.last-c.first+1);render[c.group].push(...part.actions);
    }
    for(const group of groups){
      assert.equal(render[group].length,face.render[group].length);
      face.render[group].forEach((preview,i)=>{for(const [k,v]of Object.entries(preview))if(k!=='bid_detail_key')assert.deepEqual(render[group][i][k],v)});
    }
    assert.equal(groups.reduce((n,g)=>n+render[g].length,0),d.action_count);
    assert.equal(d.event,face.provenance.event_id);assert.equal(d.os_sha256,face.provenance.os_sha256);assert.equal(d.trace_sha256,face.provenance.trace_sha256);
    const result={...face,render};delete result.bid_card_details;return result;
  }
  const name = `${face.provenance.event_id}.bid-details.json`;
  assert.equal(face.bid_card_details.detail_url, `/data/${name}`);
  return hydrateBidDetails(face, gunzipSync(readFileSync(join(dataRoot, name + '.gz'))));
}

export function writeBidDetails(face, dataRoot) {
  if(groups.reduce((n,g)=>n+(face.render[g]?.length??0),0)>512){
    const event=face.provenance.event_id;assert.match(event,/^[A-Z0-9-]+$/);
    const descriptor={schema:'bid-card-details-v2',event,os_sha256:face.provenance.os_sha256,trace_sha256:face.provenance.trace_sha256,
      action_count:groups.reduce((n,g)=>n+(face.render[g]?.length??0),0),chunks:[]};
    const dir=join(dataRoot,`${event}.bid-details`);mkdirSync(dir,{recursive:true});const render={...face.render};
    for(const group of groups){
      const rows=face.render[group]??[];
      for(let first=0;first<rows.length;first+=256){
        const actions=rows.slice(first,first+256),part={schema:descriptor.schema,event,os_sha256:descriptor.os_sha256,trace_sha256:descriptor.trace_sha256,group,first,actions};
        const bytes=Buffer.from(JSON.stringify(part)+'\n');
        assert.deepEqual(JSON.parse(bytes).actions,actions,'Lossless bid-detail chunk');
        writeFileSync(join(dir,`${group}-${first}.json.gz`),gzipSync(bytes,{level:9}));
        descriptor.chunks.push({group,first,last:first+actions.length-1,detail_url:`/data/${event}.bid-details/${group}-${first}.json`,sha256_uncompressed:sha(bytes),bytes_uncompressed:bytes.length});
      }
      render[group]=rows.map((action,i)=>{
        const preview=Object.fromEntries(previewKeys.filter(k=>k in action).map(k=>[k,action[k]]));
        preview.bid_detail_key=`${group}:${i}`;
        if(group==='supersessions')preview.bid_accountability=action.bid_accountability;
        return preview;
      });
    }
    return {...face,render,bid_card_details:descriptor};
  }
  const split = splitBidDetails(face);
  assert.deepEqual(hydrateBidDetails(split.face, split.bytes), face, 'Lossless bid-card round trip');
  writeFileSync(join(dataRoot, `${face.provenance.event_id}.bid-details.json.gz`), gzipSync(split.bytes, {level: 9}));
  return split.face;
}
