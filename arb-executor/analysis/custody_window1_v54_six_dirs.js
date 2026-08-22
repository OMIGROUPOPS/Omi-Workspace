"use strict";

// Receipt-only CUSTODY-ALL finalizer. The directories must already have been
// moved with native filesystem tooling. This script verifies every byte against
// the committed pre-disposition manifest and writes one private manifest set.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const args = Object.fromEntries(process.argv.slice(2).reduce((rows, token, index, all) => {
  if (token.startsWith("--")) rows.push([token.slice(2), all[index + 1]]);
  return rows;
}, []));
const required = (name) => {
  if (!args[name]) throw new Error(`missing --${name}`);
  return path.resolve(args[name]);
};
const ensure = (condition, message) => { if (!condition) throw new Error(message); };
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileReceipt = (file) => {
  const bytes = fs.readFileSync(file);
  return { sha256: sha(bytes), bytes: bytes.length };
};

const repo = required("repo");
const custodyRoot = required("custody-root");
const preManifestPath = required("pre-manifest");
const sourceRoot = path.join(repo, ".claude", "window1_live_v4_replay");
const fileManifestPath = path.join(custodyRoot, "SIX_DIR_FILE_MANIFEST.json");
const custodyManifestPath = path.join(custodyRoot, "CUSTODY_MANIFEST.json");
ensure(custodyRoot.toLowerCase().includes(`${path.sep}omi-window1-private${path.sep}`), `custody root is outside OMI-Window1-private: ${custodyRoot}`);
ensure(fs.existsSync(custodyRoot) && fs.statSync(custodyRoot).isDirectory(), `custody root absent: ${custodyRoot}`);

const preBytes = fs.readFileSync(preManifestPath);
const pre = JSON.parse(preBytes.toString("utf8"));
ensure(pre.directories.length === 6, `pre-manifest directory count changed: ${pre.directories.length}`);
let verifiedFiles = 0;
let verifiedBytes = 0;
const directories = pre.directories.map((row) => {
  const name = path.basename(row.path);
  const source = path.join(sourceRoot, name);
  const destination = path.join(custodyRoot, name);
  ensure(!fs.existsSync(source), `workspace source remains after CUSTODY-ALL: ${source}`);
  ensure(fs.existsSync(destination) && fs.statSync(destination).isDirectory(), `private destination absent: ${destination}`);
  const actualNames = fs.readdirSync(destination).filter((file) => fs.statSync(path.join(destination, file)).isFile()).sort();
  ensure(actualNames.length === row.files, `file count mismatch ${name}: ${actualNames.length}/${row.files}`);
  const expectedByName = new Map(row.file_receipts.map((file) => [file.name, file]));
  const receipts = actualNames.map((file) => {
    const expected = expectedByName.get(file);
    ensure(expected, `unexpected custody file: ${name}/${file}`);
    const actual = fileReceipt(path.join(destination, file));
    ensure(actual.sha256 === expected.sha256 && actual.bytes === expected.bytes, `custody byte mismatch: ${name}/${file}`);
    verifiedFiles += 1;
    verifiedBytes += actual.bytes;
    return { name: file, sha256: actual.sha256, bytes: actual.bytes };
  });
  const identity = sha(Buffer.from(canonical(receipts)));
  ensure(identity === row.content_identity_sha256, `directory identity mismatch: ${name}`);
  return { name, private_path: destination, files: receipts.length, bytes: receipts.reduce((sum, file) => sum + file.bytes, 0), content_identity_sha256: identity, file_receipts: receipts };
});
ensure(verifiedFiles === 2027 && verifiedBytes === 686293157, `aggregate custody mismatch: ${verifiedFiles}/${verifiedBytes}`);
const combinedIdentity = sha(Buffer.from(canonical(directories.map(({ name, files, bytes, content_identity_sha256 }) => ({ path: `.claude/window1_live_v4_replay/${name}`, files, bytes, content_identity_sha256 })))));
ensure(combinedIdentity === pre.combined_content_identity_sha256, "combined content identity changed during custody");

const fileManifest = {
  label: "V54_SIX_DIR_PRIVATE_CUSTODY_SHA256_BYTES_ENTRIES_MANIFEST",
  operator_word: "CUSTODY-ALL",
  private_root: custodyRoot,
  directory_entries: directories.length,
  file_entries: verifiedFiles,
  bytes: verifiedBytes,
  combined_content_identity_sha256: combinedIdentity,
  directories,
};
fs.writeFileSync(fileManifestPath, canonical(fileManifest), "utf8");
const fileManifestReceipt = fileReceipt(fileManifestPath);

const custodyManifest = {
  label: "V54_SIX_DIR_L22_EXTERNAL_CUSTODY",
  operator_word: "CUSTODY-ALL",
  disposition: "ALL_SIX_MOVED_TO_PRIVATE_CUSTODY",
  workspace_source_root: sourceRoot,
  all_six_sources_absent_verified: pre.directories.every((row) => !fs.existsSync(path.join(sourceRoot, path.basename(row.path)))),
  private_root: custodyRoot,
  directory_entries: directories.length,
  file_entries: verifiedFiles,
  bytes: verifiedBytes,
  combined_content_identity_sha256: combinedIdentity,
  pre_disposition_manifest: { path: preManifestPath, sha256: sha(preBytes), bytes: preBytes.length },
  private_file_manifest: { path: fileManifestPath, sha256: fileManifestReceipt.sha256, bytes: fileManifestReceipt.bytes },
  reason_not_committed: "L22 external custody: the six payload directories total 686,293,157 bytes.",
  execution: { game_passes: 0, reruns: 0, full_804_runs_started: 0, sealed_read: false, live_mutation: false },
};
fs.writeFileSync(custodyManifestPath, canonical(custodyManifest), "utf8");
const custodyManifestReceipt = fileReceipt(custodyManifestPath);
process.stdout.write(canonical({
  disposition: custodyManifest.disposition,
  private_root: custodyRoot,
  directories: directories.length,
  files: verifiedFiles,
  bytes: verifiedBytes,
  combined_content_identity_sha256: combinedIdentity,
  file_manifest: { path: fileManifestPath, ...fileManifestReceipt },
  custody_manifest: { path: custodyManifestPath, ...custodyManifestReceipt },
}));
