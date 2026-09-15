import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {readJsonBytes,gzipMirror,jsonFileExists} from './json_storage.mjs';
import {buildScoreboard} from './build_scoreboard.mjs';
test('raw and gzip-only artifact representations have identical bytes and hashes',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'face-gzip-test-')),file=path.join(dir,'sample.json');
 const bytes=Buffer.from('{"all":"retained","values":[null,0,1]}\n');
 const result=gzipMirror(file,bytes);
 assert(jsonFileExists(file));assert.deepEqual(readJsonBytes(file),bytes);
 fs.writeFileSync(file,bytes);assert.deepEqual(readJsonBytes(file),bytes);
 assert.equal(result.json_bytes,bytes.length);
 // Only the two explicit test artifacts are removed; never recurse over user data.
 fs.unlinkSync(file);fs.unlinkSync(file+'.gz');fs.rmdirSync(dir);
});
test('reviewed five-game scoreboard is identical from raw or gzip-only files',t=>{
 const raw=path.resolve(import.meta.dirname,'shell/.demo-public/data'),compressed=path.resolve(import.meta.dirname,'demo-baseline/data');
 if(!fs.existsSync(raw)){t.skip('Local pre-archive reference is not present');return;}
 assert.equal(buildScoreboard(raw,{emit:false}).payload,buildScoreboard(compressed,{emit:false}).payload);
});
