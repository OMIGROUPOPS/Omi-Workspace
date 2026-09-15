// Resume a failed size-only export from its already hash-bound timeline chunks.
// No replay, tape transformation, receipt removal, or grading change.
import fs from 'node:fs';
import path from 'node:path';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {readTimelineChunks,columnizeTimelinePreview,refreshTimelinePreview} from '../timeline_chunks.mjs';
import {writeGameIndex} from '../face_contract.mjs';
import {buildPressure} from '../build_lab_pressure.mjs';
const event=process.argv[2],dir=process.argv[3],data=path.resolve(import.meta.dirname,'../data');
assert.match(event,/^[A-Z0-9-]+$/);
const replay=JSON.parse(fs.readFileSync(path.join(dir,'REPLAY_RECEIPT.json')));
const stored=JSON.parse(gunzipSync(fs.readFileSync(path.join(dir,'FACE_OVERSIZE.json.gz'))));
assert(stored.timeline,'Only the already completed chunked export may be resumed');
assert.equal(stored.provenance.event_id,event);
assert.equal(stored.provenance.trace_sha256,replay.trace.sha256);
assert.equal(stored.provenance.os_sha256,replay.inputs['window1_v54_dual_belief_os.js']);
const full=readTimelineChunks(stored,data);
const face=columnizeTimelinePreview(refreshTimelinePreview(stored,full));
assert.deepEqual(readTimelineChunks(face,data),full,'Column storage must preserve every receipt/marker');
const bytes=Buffer.from(JSON.stringify(face)+'\n'),encoded=gzipSync(bytes,{level:9});
assert(encoded.length<2*1024*1024,'Main face exceeds 2 MiB');
const file=path.join(data,event+'.face.json');fs.writeFileSync(file+'.tmp',bytes);fs.renameSync(file+'.tmp',file);fs.writeFileSync(file+'.gz',encoded);
console.log(JSON.stringify({event,resumed_from:'FACE_OVERSIZE.json.gz',receipt_count:full.os.length,gzip_bytes:encoded.length,round_trip:'PASS'}));
await writeGameIndex(data);
console.log(JSON.stringify(buildPressure(data,event)));
