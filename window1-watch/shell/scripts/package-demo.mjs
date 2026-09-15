import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {gzipSync,gunzipSync} from 'node:zlib';

const shell = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(shell, "dist-demo");
// Content-addressed upload roots cannot retain an obsolete bundle from a prior build.
const buildId = createHash("sha256").update(readFileSync(resolve(dist, "index.html"))).update(readFileSync(resolve(dist, "demo-assets.json"))).digest("hex").slice(0, 16);
const upload = resolve(shell, `.vercel/demo-upload-${buildId}`);
const output = resolve(upload, ".vercel/output");
const manifest = JSON.parse(readFileSync(resolve(dist, "demo-assets.json")));
const allowed = new Map(manifest.assets.map(entry => [entry.path, entry]));
const walk = root => readdirSync(root, { withFileTypes: true }).flatMap(entry => {
  assert.ok(!entry.isSymbolicLink());
  const path = resolve(root, entry.name);
  return entry.isDirectory() ? walk(path) : [path];
});
const gzipRoutes=[];let uploadedBytes=0;
for (const path of walk(dist)) {
  const name = relative(dist, path).replaceAll("\\", "/");
  assert.ok(allowed.has(name) || name === "index.html" || name === "demo-assets.json" || /^assets\/index-[\w-]+\.(js|css)$/.test(name), `Not allowlisted: ${name}`);
  const storedBytes = readFileSync(path), precompressed=name.endsWith('.json.gz');
  const bytes=precompressed?gunzipSync(storedBytes):storedBytes, logicalName=precompressed?name.slice(0,-3):name;
  if (allowed.has(name)) {
    const entry=allowed.get(name);assert.equal(createHash("sha256").update(storedBytes).digest("hex"), entry.sha256);
    if(precompressed){assert.equal(entry.json_path,logicalName);assert.equal(createHash('sha256').update(bytes).digest('hex'),entry.sha256_uncompressed);assert.equal(bytes.length,entry.json_bytes);}
  }
  assert.ok(!/-----BEGIN [\w ]*PRIVATE KEY-----|\b(?:ghp_|github_pat_|AKIA)[A-Za-z0-9_]{16,}|\bvercel_[A-Za-z0-9]{20,}/.test(bytes.toString()), `Possible credential in ${name}`);
  if (name.endsWith(".js")) assert.ok(!/DATABASE_URL|BETTER_AUTH_SECRET|window1_v54_dual_belief_os|arb-executor\/analysis/.test(bytes.toString()), `Server/engine content in ${name}`);
  const encoded=precompressed?storedBytes:name.endsWith('.json')?gzipSync(bytes,{level:9}):bytes;
  if(logicalName.endsWith('.face.json'))assert(encoded.length<2*1024*1024,`Face transfer exceeds 2 MiB: ${name}`);
  const storedName=name.endsWith('.json')?name+'.gz':name;
  if(logicalName.endsWith('.json')){assert.deepEqual(gunzipSync(encoded),bytes);gzipRoutes.push({src:'/'+logicalName.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),dest:'/'+storedName,headers:{'Content-Type':'application/json; charset=utf-8','Content-Encoding':'gzip','Cache-Control':'public, max-age=0, must-revalidate'}});}
  uploadedBytes+=encoded.length;
  const destination = resolve(output, "static", storedName);
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, encoded);
}
const config = {
  version: 3,
  routes: [
    ...gzipRoutes,
    { src: "/data/.*", headers: { "Cache-Control": "public, max-age=0, must-revalidate" }, continue: true },
    { handle: "filesystem" },
    { src: "/.*", status: 404 },
  ],
};
writeFileSync(resolve(output, "config.json"), JSON.stringify(config, null, 2));
copyFileSync(resolve(shell, ".vercel/project.json"), resolve(upload, ".vercel/project.json"));
assert.ok(!existsSync(resolve(output, "functions")), "Static demo must have no server functions");
writeFileSync(resolve(upload,'UPLOAD_RECEIPT.json'),JSON.stringify({uploaded_bytes:uploadedBytes,uncompressed_asset_bytes:manifest.uncompressed_asset_bytes??manifest.total_bytes,files:walk(resolve(output,'static')).length,route_count:gzipRoutes.length,policy:'Lossless gzip HTTP representation; original JSON bytes/hash preserved; static only.'},null,2));
console.log(`Verified static-only upload: ${walk(resolve(output, "static")).length} files; ${uploadedBytes} bytes; ${upload}`);
