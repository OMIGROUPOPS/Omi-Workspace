// Named-check extract only; original lines remain local, never static assets.
import fs from 'node:fs';
import readline from 'node:readline';
import crypto from 'node:crypto';
import {once} from 'node:events';
import {finished} from 'node:stream/promises';
import assert from 'node:assert/strict';
const root='C:/tmp/unsupported_rests_20260914',event='KXATPMATCH-26JUL12ALTGAS';
const source='C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl',path=root+'/'+event+'.prints.jsonl';
const expected=JSON.parse(fs.readFileSync('C:/tmp/tune_expansion_20260914/SELECTED_PRINTS_RECEIPT.json')).source.sha256;
const input=fs.createReadStream(source),hash=crypto.createHash('sha256'),out=fs.createWriteStream(path+'.tmp'),outHash=crypto.createHash('sha256');
input.on('data',b=>hash.update(b));let rows=0;
for await(const line of readline.createInterface({input,crlfDelay:Infinity})){
 if(!line)continue;const r=JSON.parse(line);if(![event+'-ALT',event+'-GAS'].includes(r.ticker))continue;
 const bytes=line+'\n';outHash.update(bytes);rows++;if(!out.write(bytes))await once(out,'drain');
}
const done=finished(out);out.end();await done;assert.equal(hash.digest('hex'),expected);
fs.renameSync(path+'.tmp',path);const receipt={event,path,rows,bytes:fs.statSync(path).size,sha256:outHash.digest('hex'),source_sha256:expected};
fs.writeFileSync(root+'/ALT_PRINTS_RECEIPT.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
