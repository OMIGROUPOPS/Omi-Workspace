// Read-only custody scan; writes only the face glossary coverage receipt.
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const traces = process.argv.slice(2);
if (!traces.length) throw new Error("Supply custody traces");
const report = { files: [], games: {}, tokens: {} };
for (const trace of traces) {
  const hash = crypto.createHash("sha256"),
    input = fs.createReadStream(trace);
  input.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({
    input: input.pipe(zlib.createGunzip()),
    crlfDelay: Infinity,
  });
  let rows = 0;
  for await (const line of lines) {
    if (!line) continue;
    const r = JSON.parse(line);
    rows++;
    if (r.kind !== "DECISION_STAGE") continue;
    report.games[r.event_id] = (report.games[r.event_id] ?? 0) + 1;
    const emit = (field, token) => {
      if (typeof token !== "string") return;
      const entry = (report.tokens[token] ??= {
        fields: [],
        games: [],
        count: 0,
      });
      if (!entry.fields.includes(field)) entry.fields.push(field);
      if (!entry.games.includes(r.event_id)) entry.games.push(r.event_id);
      entry.count++;
    };
    for (const d of r.derivations ?? []) {
      emit("action", d.action?.action);
      emit("reason", d.action?.reason);
      emit(
        "winner.lane",
        d.layered_dual_belief?.decision_arbitration?.winner?.lane,
      );
      emit("envelope.mode", d.layered_dual_belief?.envelope_placement?.mode);
      emit(
        "authority_source",
        d.derivation?.pricing_authority?.authority_source,
      );
    }
    for (const b of Object.values(r.layers?.micro?.context?.beliefs ?? {}))
      for (const key of ["status", "q_author", "x_author"]) emit(key, b[key]);
  }
  report.files.push({ path: trace, sha256: hash.digest("hex"), rows });
}
await fsp.writeFile(
  path.join(here, "proof", "card-token-inventory.json"),
  JSON.stringify(report, null, 2) + "\n",
);
console.log(
  JSON.stringify(
    {
      files: report.files,
      games: report.games,
      tokens: Object.keys(report.tokens).sort(),
    },
    null,
    2,
  ),
);
