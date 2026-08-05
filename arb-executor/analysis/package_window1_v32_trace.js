#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const output = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805");
const source = path.join(output, "FULL_DECISION_TRACE.jsonl.gz");
const partBytes = 80 * 1024 * 1024;
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileHash = (file) => sha(fs.readFileSync(file));
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;

function split(prefix) {
  const descriptor = fs.openSync(source, "r"); const size = fs.statSync(source).size; const parts = [];
  try {
    for (let offset = 0, index = 1; offset < size; offset += partBytes, index += 1) {
      const length = Math.min(partBytes, size - offset), buffer = Buffer.allocUnsafe(length); const read = fs.readSync(descriptor, buffer, 0, length, offset); if (read !== length) throw new Error("short trace read"); const file = path.join(output, `${prefix}.part${String(index).padStart(3, "0")}`); fs.writeFileSync(file, buffer); parts.push(file);
    }
  } finally { fs.closeSync(descriptor); }
  return parts;
}

function remove(files) { for (const file of files) fs.rmSync(file); }

const sourceHash = fileHash(source), sourceBytes = fs.statSync(source).size;
const first = split(".trace-package-run1"), second = split(".trace-package-run2");
if (first.length !== second.length) throw new Error("trace split count mismatch");
for (let index = 0; index < first.length; index += 1) if (fileHash(first[index]) !== fileHash(second[index])) throw new Error(`trace split mismatch part ${index + 1}`);
const finalParts = [];
for (let index = 0; index < first.length; index += 1) { const target = path.join(output, `FULL_DECISION_TRACE.jsonl.gz.part${String(index + 1).padStart(3, "0")}`); fs.renameSync(first[index], target); finalParts.push(target); }
remove(second);
const reassembled = crypto.createHash("sha256"); let reassembledBytes = 0; for (const file of finalParts) { const bytes = fs.readFileSync(file); reassembled.update(bytes); reassembledBytes += bytes.length; }
if (reassembled.digest("hex") !== sourceHash || reassembledBytes !== sourceBytes) throw new Error("trace reassembly mismatch");
fs.rmSync(source);
const script = path.resolve(__filename);
const receipt = {
  law: "FIXED_80_MIB_BYTE_SLICING_OF_ALREADY_TWO_BUILD_IDENTICAL_GZIP_STREAM",
  semantic_change: false,
  source_trace: { logical_path: "FULL_DECISION_TRACE.jsonl.gz", sha256: sourceHash, bytes: sourceBytes },
  packaging_runs: 2,
  byte_identical_parts_across_packaging_runs: true,
  part_size_bytes: partBytes,
  parts: Object.fromEntries(finalParts.map((file) => [path.basename(file), { sha256: fileHash(file), bytes: fs.statSync(file).size }])),
  reassembly: { sha256: sourceHash, bytes: reassembledBytes, exact: true },
  packaging_source: { path: path.relative(path.resolve(output, "../../.."), script).replaceAll("\\", "/"), sha256: fileHash(script), bytes: fs.statSync(script).size },
};
fs.writeFileSync(path.join(output, "TRACE_PACKAGING_RECEIPT.json"), canonical(receipt));
const detPath = path.join(output, "DETERMINISM_RECEIPT.json"), det = JSON.parse(fs.readFileSync(detPath)); det.postbuild_trace_packaging = { packaging_runs: 2, byte_identical: true, exact_reassembly: true, source_trace_sha256: sourceHash, part_count: finalParts.length }; fs.writeFileSync(detPath, canonical(det));
const manifestPath = path.join(output, "ARTIFACT_HASH_MANIFEST.json"); const names = fs.readdirSync(output).filter((name) => name !== path.basename(manifestPath)).sort(); fs.writeFileSync(manifestPath, canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
process.stdout.write(canonical(receipt));
