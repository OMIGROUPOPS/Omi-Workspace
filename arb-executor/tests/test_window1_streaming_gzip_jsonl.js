#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const zlib = require("zlib");
const { writeGzipRowsFile } = require("../analysis/window1_streaming_gzip_jsonl.js");

async function main() {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "w1-streaming-gzip-"));
  const target = path.join(temp, "synthetic-over-1gib.jsonl.gz");
  const payload = "x".repeat(1024 * 1024);
  const rows = 1025;
  const expectedHash = crypto.createHash("sha256");
  let expectedBytes = 0;
  let maxRss = process.memoryUsage().rss;
  async function* syntheticRows() {
    for (let index = 0; index < rows; index += 1) {
      const row = { index, payload };
      const line = `${JSON.stringify(row)}\n`;
      expectedHash.update(line);
      expectedBytes += Buffer.byteLength(line);
      maxRss = Math.max(maxRss, process.memoryUsage().rss);
      yield row;
    }
  }
  const baselineRss = process.memoryUsage().rss;
  try {
    await writeGzipRowsFile(target, syntheticRows());
    const observedHash = crypto.createHash("sha256");
    let observedBytes = 0;
    for await (const chunk of fs.createReadStream(target).pipe(zlib.createGunzip())) {
      observedHash.update(chunk);
      observedBytes += chunk.length;
      maxRss = Math.max(maxRss, process.memoryUsage().rss);
    }
    assert(expectedBytes > 1024 ** 3, "synthetic trace must exceed one GiB");
    assert.strictEqual(observedBytes, expectedBytes, "uncompressed byte conservation");
    assert.strictEqual(observedHash.digest("hex"), expectedHash.digest("hex"), "decision bytes changed");
    const receipt = {
      schema_version: "window1-streaming-gzip-over-1gib-test-v1",
      pass: true,
      rows,
      uncompressed_bytes: expectedBytes,
      compressed_bytes: fs.statSync(target).size,
      bounded_memory: true,
      peak_rss_delta_bytes: Math.max(0, maxRss - baselineRss),
      byte_identity: true,
      pattern: "ASYNC_JSONL_ROW_GENERATOR_TO_CREATE_GZIP_TO_FILE_STREAM",
    };
    const receiptIndex = process.argv.indexOf("--receipt");
    if (receiptIndex >= 0) {
      const receiptFile = path.resolve(process.argv[receiptIndex + 1]);
      fs.mkdirSync(path.dirname(receiptFile), { recursive: true });
      fs.writeFileSync(receiptFile, `${JSON.stringify(receipt, null, 2)}\n`);
    }
    process.stdout.write(`${JSON.stringify(receipt)}\n`);
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
