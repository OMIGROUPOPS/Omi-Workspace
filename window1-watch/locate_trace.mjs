import fs from 'node:fs';
import zlib from 'node:zlib';
import readline from 'node:readline';
// Discovery only. The subsequent builder reads to EOF and verifies the whole gzip.
const [event,...files] = process.argv.slice(2);
for (const file of files) {
  const raw=fs.createReadStream(file), unzip=zlib.createGunzip();
  try {
    for await (const line of readline.createInterface({input:raw.pipe(unzip),crlfDelay:Infinity})) {
      const row=JSON.parse(line);
      if (row.event_id===event && row.kind==='DECISION_STAGE') { console.log(file); process.exitCode=0; raw.destroy();unzip.destroy();process.exit(0); }
    }
  } catch { /* An incomplete candidate is not a custody source. */ }
  finally { raw.destroy();unzip.destroy(); }
}
process.exitCode=3;
