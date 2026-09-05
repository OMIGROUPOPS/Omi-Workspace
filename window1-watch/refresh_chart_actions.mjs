// Rebuild display fields from the committed full receipt files, not a new OS replay.
import fs from "node:fs/promises";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";
import { readChartSources, attachChartActions } from "./chart_actions.mjs";
import { readPinnedTruth, attachRecordedTruth } from "./recorded_truth.mjs";
const here = path.dirname(fileURLToPath(import.meta.url));
const table = readPinnedTruth(path.resolve(here, ".."));
if (!process.argv.slice(2).length) throw new Error("Supply event ids");
for (const event of process.argv.slice(2)) {
  if (!/^[A-Za-z0-9_-]+$/.test(event)) throw new Error("Unsafe event id");
  const file = path.join(here, "data", `${event}.face.json`);
  const packed = JSON.parse(await fs.readFile(file, "utf8"));
  const face = unpackFace(structuredClone(packed));
  if (face.provenance.event_id !== event) throw new Error("Event mismatch");
  attachRecordedTruth(face, table);
  attachChartActions(face, await readChartSources(face, here));
  // Preserve the existing OS dictionary and every stored OS/tape field byte-for-byte.
  packed.render = face.render;
  packed.truth = face.truth;
  const bytes = JSON.stringify(packed) + "\n";
  const zipped = zlib.gzipSync(bytes);
  if (zipped.length >= 2 * 1024 * 1024)
    throw new Error("Face exceeds 2 MiB transfer budget");
  await fs.writeFile(file + ".tmp", bytes);
  await fs.rename(file + ".tmp", file);
  await fs.writeFile(file + ".gz", zipped);
  console.log(
    `${event}: ${face.render.bid_actions.length} markers; ${zipped.length} gzip bytes`,
  );
  for (const a of face.render.bid_actions.filter(
    (a) => a.fill || face.render.bid_actions.length < 20,
  ))
    console.log(
      JSON.stringify({
        label: a.label,
        reason: a.raw.reason,
        fill: a.fill?.summary,
        floor: a.fill?.floor_line,
      }),
    );
}
