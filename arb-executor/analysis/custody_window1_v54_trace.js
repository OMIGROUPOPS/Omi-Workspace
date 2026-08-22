"use strict";

// Receipt-only custody finalizer. It never executes a game or policy. It verifies
// the operator-moved V54 trace against its pre-move provenance and writes the two
// private L22 manifests.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, token, index, all) => {
  if (!token.startsWith("--")) return pairs;
  pairs.push([token.slice(2), all[index + 1]]);
  return pairs;
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

const traceRoot = required("trace-root");
const sourceRoot = required("source-root");
const provenancePath = required("provenance");
const traceManifestPath = path.join(traceRoot, "TRACE_FILE_MANIFEST.json");
const custodyManifestPath = path.join(traceRoot, "CUSTODY_MANIFEST.json");

ensure(fs.existsSync(traceRoot) && fs.statSync(traceRoot).isDirectory(), `custody trace absent: ${traceRoot}`);
ensure(!fs.existsSync(sourceRoot), `source still exists after custody move: ${sourceRoot}`);
ensure(traceRoot.toLowerCase().includes(`${path.sep}omi-window1-private${path.sep}`), `destination is not under OMI-Window1-private: ${traceRoot}`);

const provenanceBytes = fs.readFileSync(provenancePath);
const provenance = JSON.parse(provenanceBytes.toString("utf8"));
const names = fs.readdirSync(traceRoot)
  .filter((name) => !["TRACE_FILE_MANIFEST.json", "CUSTODY_MANIFEST.json"].includes(name))
  .filter((name) => fs.statSync(path.join(traceRoot, name)).isFile())
  .sort();
ensure(names.length === 802, `trace entry count changed: ${names.length}`);

const priorManifestSha = sha(Buffer.from(canonical(provenance.files)));
ensure(priorManifestSha === provenance.trace.file_manifest_sha256, "pre-move provenance file manifest hash does not re-derive");
const priorByName = new Map(provenance.files.map((row) => [path.basename(row.path), row]));
const files = names.map((name) => {
  const receipt = fileReceipt(path.join(traceRoot, name));
  const prior = priorByName.get(name);
  ensure(prior, `file absent from pre-move provenance: ${name}`);
  ensure(receipt.sha256 === prior.sha256 && receipt.bytes === prior.bytes, `post-move byte mismatch: ${name}`);
  return { name, sha256: receipt.sha256, bytes: receipt.bytes };
});
ensure(priorByName.size === files.length, "pre-move provenance contains unmatched files");

const totalBytes = files.reduce((sum, row) => sum + row.bytes, 0);
ensure(totalBytes === 164665281, `trace byte count changed: ${totalBytes}`);
const contentIdentitySha = sha(Buffer.from(canonical(files)));
const traceManifest = {
  label: "V54_802_FILE_TRACE_PRIVATE_CUSTODY_FILE_MANIFEST",
  license: {
    law_index_read_at: "686e8c8d",
    law_index_sha256: "c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6",
    laws: ["L8", "L18", "L20", "L22"],
  },
  operator_word: "CUSTODY",
  trace_root: traceRoot,
  entries: files.length,
  bytes: totalBytes,
  content_identity_sha256: contentIdentitySha,
  pre_move_file_manifest_sha256: priorManifestSha,
  files,
};
fs.writeFileSync(traceManifestPath, canonical(traceManifest), "utf8");
const traceManifestReceipt = fileReceipt(traceManifestPath);

const custodyManifest = {
  label: "V54_802_FILE_TRACE_L22_EXTERNAL_CUSTODY",
  operator_word: "CUSTODY",
  disposition: "MOVED_TO_PRIVATE_CUSTODY",
  source_path: sourceRoot,
  source_absent_verified: !fs.existsSync(sourceRoot),
  private_path: traceRoot,
  trace: {
    entries: files.length,
    bytes: totalBytes,
    content_identity_sha256: contentIdentitySha,
    pre_move_file_manifest_sha256: priorManifestSha,
  },
  trace_file_manifest: {
    path: traceManifestPath,
    sha256: traceManifestReceipt.sha256,
    bytes: traceManifestReceipt.bytes,
  },
  provenance_receipt: {
    path: provenancePath,
    sha256: sha(provenanceBytes),
    bytes: provenanceBytes.length,
  },
  reason_not_committed: "L22 forbids committing the 164,665,281-byte trace and its private custody manifests remain beside it.",
  execution: {
    game_passes: 0,
    reruns: 0,
    full_804_run: false,
    sealed_read: false,
    live_mutation: false,
  },
};
fs.writeFileSync(custodyManifestPath, canonical(custodyManifest), "utf8");
const custodyManifestReceipt = fileReceipt(custodyManifestPath);

process.stdout.write(canonical({
  disposition: custodyManifest.disposition,
  source_absent_verified: custodyManifest.source_absent_verified,
  private_path: traceRoot,
  entries: files.length,
  bytes: totalBytes,
  trace_content_identity_sha256: contentIdentitySha,
  pre_move_file_manifest_sha256: priorManifestSha,
  trace_file_manifest: { path: traceManifestPath, ...traceManifestReceipt },
  custody_manifest: { path: custodyManifestPath, ...custodyManifestReceipt },
}));
