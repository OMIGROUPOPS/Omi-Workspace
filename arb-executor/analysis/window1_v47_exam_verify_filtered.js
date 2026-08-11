#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { Writable } = require("stream");
const { pipeline } = require("stream/promises");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

async function main() {
  const [root, memberList] = process.argv.slice(2);
  if (!root || !memberList) {
    throw new Error("usage: window1_v47_exam_verify_filtered.js RAW_DIR MEMBER_LIST");
  }
  const names = fs.readFileSync(memberList, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((value) => path.basename(value));
  const found = fs.readdirSync(root).filter((value) => value.endsWith(".jsonl.gz")).sort();
  if (JSON.stringify(found) !== JSON.stringify(names)) {
    throw new Error(`member mismatch found=${found.length} expected=${names.length}`);
  }
  let compressedBytes = 0;
  let uncompressedBytes = 0;
  for (const name of found) {
    const source = path.join(root, name);
    compressedBytes += fs.statSync(source).size;
    await pipeline(
      fs.createReadStream(source),
      zlib.createGunzip(),
      new Writable({
        write(chunk, _encoding, done) {
          uncompressedBytes += chunk.length;
          done();
        },
      }),
    );
  }
  process.stdout.write(`${JSON.stringify({
    members: found.length,
    compressed_bytes: compressedBytes,
    uncompressed_bytes: uncompressedBytes,
    member_list_sha256: sha256(memberList),
    gzip_integrity: "PASS",
  })}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
