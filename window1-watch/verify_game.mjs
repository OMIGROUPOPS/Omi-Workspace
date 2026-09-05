import fs from 'node:fs';
import { unpackFace } from './face_encoding.mjs';
const file=process.argv[2], face=unpackFace(JSON.parse(fs.readFileSync(file,'utf8')));
for(const key of ['event_id','os_sha256','trace_sha256','bench_sha256']) console.log(`${key.toUpperCase()} ${face.provenance[key]??'STORE SILENT'}`);
for(const leg of face.legs) for(const key of ['first_rest','first_fill']) console.log(`${leg}_${key.toUpperCase()} ${JSON.stringify(face.render.verification[leg][key])}`);
console.log(`FACE_BYTES ${fs.statSync(file).size} FRAMES ${face.render.total_frames} RECEIPTS ${face.render.receipt_count}`);
console.log(`FIRST_TICK ${JSON.stringify(face.first_tick)}`);
