import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { gunzipSync } from "node:zlib";
import { buildScoreboard } from "../../build_scoreboard.mjs";

const shell = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(shell, "../data");
buildScoreboard(source);
const target = resolve(shell, ".demo-public");
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const entries = [];
const allowed = new Set();
const within = (root, name) => {
  const path = resolve(root, name);
  if (!path.startsWith(root + sep)) throw new Error(`Unsafe asset path: ${name}`);
  return path;
};
function put(name, bytes) {
  const path = within(target, name);
  allowed.add(name.replaceAll("\\", "/"));
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, bytes);
  entries.push({ path: name, bytes: bytes.length, sha256: sha(bytes) });
}
const indexBytes = readFileSync(resolve(source, "index.json"));
const index = JSON.parse(indexBytes);
if (index.games.length !== 5) throw new Error("Demo requires the five reviewed games; review the allowlist before extending it");
put("data/index.json", indexBytes);
put("data/desk-status.json", readFileSync(resolve(source, "desk-status.json")));
put("data/scoreboard.json", readFileSync(resolve(source, "scoreboard.json")));
for (const game of index.games) {
  if (!/^[A-Z0-9-]+$/.test(game.event) || game.url !== `/data/${game.event}.face.json`) throw new Error("Unexpected game URL");
  const faceBytes = readFileSync(within(source, `${game.event}.face.json`));
  const face = JSON.parse(faceBytes);
  const gradeBytes = readFileSync(within(source, `${game.event}.grade.json`));
  const grade = JSON.parse(gradeBytes);
  if (grade.event !== game.event || grade.provenance.face_sha256 !== sha(faceBytes) ||
      grade.provenance.os_sha256 !== face.provenance.os_sha256 ||
      grade.provenance.trace_sha256 !== face.provenance.trace_sha256) throw new Error(`Unbound grade: ${game.event}`);
  put(`data/${game.event}.face.json`, faceBytes);
  put(`data/${game.event}.grade.json`, gradeBytes);
  const pressureFile = within(source, `${game.event}.pressure.json`);
  // On the desktop a deliberate pressure rebuild joins local stages. Hosted
  // builds only consume the reviewed compact asset; they have no stage files.
  if (existsSync(pressureFile)) {
    const pressureBytes = readFileSync(pressureFile);
    const pressure = JSON.parse(pressureBytes);
    if (pressure.event !== game.event || pressure.provenance.face_sha256 !== sha(faceBytes) ||
        pressure.provenance.trace_sha256 !== face.provenance.trace_sha256 ||
        pressure.provenance.os_sha256 !== face.provenance.os_sha256) throw new Error(`Unbound pressure: ${game.event}`);
    put(`data/${game.event}.pressure.json`, pressureBytes);
  }
  if (face.oracle?.detail_url) {
    if (face.oracle.detail_url !== `/data/${game.event}.oracle.json`) throw new Error("Unexpected oracle URL");
    const oracleBytes = gunzipSync(readFileSync(within(source, `${game.event}.oracle.json.gz`)));
    if (sha(oracleBytes) !== face.oracle.sha256_uncompressed) throw new Error(`Unbound oracle: ${game.event}`);
    put(`data/${game.event}.oracle.json`, oracleBytes);
  }
}
// The strip uses only this compact index, not individual historical stage files.
put("data/grades/index.json", readFileSync(resolve(source, "grades/index.json")));
put("favicon.svg", readFileSync(resolve(shell, "public/favicon.svg")));
function files(root) {
  if (!existsSync(root)) return [];
  return readdirSync(root, { withFileTypes: true }).flatMap(entry => {
    const path = resolve(root, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symlink not allowed in demo: ${path}`);
    return entry.isDirectory() ? files(path) : [path];
  });
}
// Fail closed on stale assets; do not delete or copy broad data directories.
for (const path of files(target)) {
  const name = relative(target, path).replaceAll("\\", "/");
  if (name !== "demo-assets.json" && !allowed.has(name)) throw new Error(`Non-allowlisted demo asset: ${name}`);
}
const detailFiles = files(source).filter(path => /\.stages[\\/]|[\\/]renewals[^\\/]*|\.accountability\.json/.test(path));
const omittedBytes = detailFiles.reduce((sum, path) => sum + statSync(path).size, 0);
const manifest = {
  games: index.games.map(game => game.event),
  policy: "Static face/grade/oracle/pressure plus picker/history only. Pressure is compact hash-bound receipt readings, not raw depth or trades. No raw exports, engine, credentials, stages or renewal streams.",
  omitted_detail_files: detailFiles.length,
  omitted_detail_bytes: omittedBytes,
  assets: entries,
  total_bytes: entries.reduce((sum, entry) => sum + entry.bytes, 0),
};
writeFileSync(resolve(target, "demo-assets.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(JSON.stringify(manifest, null, 2));
