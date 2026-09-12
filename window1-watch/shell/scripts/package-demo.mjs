import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";

const shell = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(shell, "dist-demo");
const upload = resolve(shell, ".vercel/demo-upload");
const output = resolve(upload, ".vercel/output");
const manifest = JSON.parse(readFileSync(resolve(dist, "demo-assets.json")));
const allowed = new Map(manifest.assets.map(entry => [entry.path, entry.sha256]));
const walk = root => readdirSync(root, { withFileTypes: true }).flatMap(entry => {
  assert.ok(!entry.isSymbolicLink());
  const path = resolve(root, entry.name);
  return entry.isDirectory() ? walk(path) : [path];
});
for (const path of walk(dist)) {
  const name = relative(dist, path).replaceAll("\\", "/");
  assert.ok(allowed.has(name) || name === "index.html" || name === "demo-assets.json" || /^assets\/index-[\w-]+\.(js|css)$/.test(name), `Not allowlisted: ${name}`);
  const bytes = readFileSync(path);
  if (allowed.has(name)) assert.equal(createHash("sha256").update(bytes).digest("hex"), allowed.get(name));
  assert.ok(!/-----BEGIN [\w ]*PRIVATE KEY-----|\b(?:ghp_|github_pat_|AKIA)[A-Za-z0-9_]{16,}|\bvercel_[A-Za-z0-9]{20,}/.test(bytes.toString()), `Possible credential in ${name}`);
  if (name.endsWith(".js")) assert.ok(!/DATABASE_URL|BETTER_AUTH_SECRET|window1_v54_dual_belief_os|arb-executor\/analysis/.test(bytes.toString()), `Server/engine content in ${name}`);
  const destination = resolve(output, "static", name);
  mkdirSync(dirname(destination), { recursive: true });
  copyFileSync(path, destination);
}
const config = {
  version: 3,
  routes: [
    { src: "/data/.*", headers: { "Cache-Control": "public, max-age=0, must-revalidate" }, continue: true },
    { handle: "filesystem" },
    { src: "/.*", status: 404 },
  ],
};
writeFileSync(resolve(output, "config.json"), JSON.stringify(config, null, 2));
copyFileSync(resolve(shell, ".vercel/project.json"), resolve(upload, ".vercel/project.json"));
assert.ok(!existsSync(resolve(output, "functions")), "Static demo must have no server functions");
console.log(`Verified static-only upload: ${walk(resolve(output, "static")).length} files; ${upload}`);
