import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../data");
// The URL remains /data/<event>.stages/<receipt>.json. Only its storage/HTTP representation is gzip.
export function faceDataPlugin() {
  return {
    name: "window1-watch:face-data",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        let pathname;
        try {
          pathname = decodeURIComponent((req.url ?? "").split("?")[0]);
        } catch {
          return next();
        }
        if (!pathname.startsWith("/data/") || !pathname.endsWith(".json")) return next();
        const file = path.resolve(root, pathname.slice("/data/".length));
        if (!file.startsWith(root + path.sep)) {
          res.statusCode = 403;
          res.end();
          return;
        }
        const compressed = file + ".gz",
          chosen = fs.existsSync(compressed) ? compressed : file;
        if (!fs.existsSync(chosen)) return next();
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.setHeader("Cache-Control", "no-cache");
        if (chosen === compressed) res.setHeader("Content-Encoding", "gzip");
        fs.createReadStream(chosen).pipe(res);
      });
    },
  };
}
