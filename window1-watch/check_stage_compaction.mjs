// Read-only audit of temporary uncompressed projections against final recoverable gzip rows.
import fs from 'node:fs/promises';import path from 'node:path';import zlib from 'node:zlib';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),data=path.join(here,'data'),verified=[];
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
for(const event of process.argv.slice(2)){
  if(!/^[A-Za-z0-9_-]+$/.test(event))throw new Error('Unsafe event');
  const directory=path.join(data,`${event}.stages`);
  for(const name of (await fs.readdir(directory)).filter(n=>n.endsWith('.json'))){
    const file=path.join(directory,name),raw=JSON.parse(await fs.readFile(file)),packed=JSON.parse(zlib.gunzipSync(await fs.readFile(file+'.gz')));
    if(hash(raw.row)!==hash(packed.row))throw new Error(`Original row differs: ${file}`);
    verified.push({file,bytes:(await fs.stat(file)).size});
  }
}
await fs.writeFile(path.join(here,'.runtime','verified-uncompressed-copies.json'),JSON.stringify(verified));
console.log(`VERIFIED ${verified.length} full original rows; ${verified.reduce((s,r)=>s+r.bytes,0)} redundant uncompressed bytes. No files deleted.`);
