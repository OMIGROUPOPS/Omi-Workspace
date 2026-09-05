// Reproject only the ruler onto existing faces; no replay, tape edit or OS re-encoding.
import fs from "node:fs/promises";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { readPinnedTruth, attachRecordedTruth } from "./recorded_truth.mjs";
const here = path.dirname(fileURLToPath(import.meta.url));
const events = process.argv.slice(2);
if (!events.length) throw new Error("Supply the event ids to refresh");
const table = readPinnedTruth(path.resolve(here, ".."));
for (const event of events) {
  if (!/^[A-Za-z0-9_-]+$/.test(event)) throw new Error("Unsafe event id");
  const file = path.join(here, "data", `${event}.face.json`);
  const face = JSON.parse(await fs.readFile(file, "utf8"));
  if (face.provenance.event_id !== event)
    throw new Error("Face event mismatch");
  const truth = attachRecordedTruth(face, table);
  const bytes = `${JSON.stringify(face)}\n`;
  await fs.writeFile(file + ".tmp", bytes);
  await fs.rename(file + ".tmp", file);
  await fs.writeFile(file + ".gz", zlib.gzipSync(bytes));
  console.log(
    `${event}\n${Object.values(truth.legs)
      .map((l) => l.line)
      .join(
        "\n",
      )}\n${truth.pair.line} · ${truth.pair.discount_line}\nTABLE_COMMIT ${truth.table_commit}\nROW_SHA256 ${truth.row_sha256}`,
  );
}
