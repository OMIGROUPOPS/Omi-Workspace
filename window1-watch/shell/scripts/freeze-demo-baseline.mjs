// Preserve the already reviewed five-game static bundle, never dirty local replays.
import fs from 'node:fs';
import path from 'node:path';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const source=path.resolve(import.meta.dirname,'../.demo-public'),target=path.resolve(import.meta.dirname,'../../demo-baseline');
const sha=b=>createHash('sha256').update(b).digest('hex');
const manifestBytes=fs.readFileSync(path.join(source,'demo-assets.json')),manifest=JSON.parse(manifestBytes);
assert.equal(manifest.games.length,5);
for(const entry of manifest.assets){
 assert(!/stages\/|renewals|accountability|\.env|\.pem/.test(entry.path));
 const file=path.resolve(source,entry.path);assert(file.startsWith(source+path.sep));
 const bytes=fs.readFileSync(file);assert.equal(sha(bytes),entry.sha256);
 const encoded=entry.path.endsWith('.json')?gzipSync(bytes,{level:9}):bytes;
 if(entry.path.endsWith('.json'))assert.equal(sha(gunzipSync(encoded)),entry.sha256);
 const dest=path.resolve(target,entry.path+(entry.path.endsWith('.json')?'.gz':''));assert(dest.startsWith(target+path.sep));
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,encoded);
}
fs.writeFileSync(path.join(target,'demo-assets.json'),manifestBytes);
console.log(JSON.stringify({files:manifest.assets.length,original_manifest_sha256:sha(manifestBytes),target}));
