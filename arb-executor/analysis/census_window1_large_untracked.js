"use strict";

// Worktree Census Law enforcement helper. Read-only except for its JSON receipt.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const args = Object.fromEntries(process.argv.slice(2).reduce((rows, token, index, all) => {
  if (token.startsWith("--")) rows.push([token.slice(2), all[index + 1]]);
  return rows;
}, []));
const repo = path.resolve(args.repo || path.join(__dirname, "..", ".."));
const phase = args.phase || "PRE_DISPOSITION";
const output = path.resolve(args.output || path.join(repo, ".claude", "window1_live_v4_replay", "v54_receipt_repairs_20260821", `WORKTREE_LARGE_UNTRACKED_CENSUS_${phase}.json`));
const threshold = 10 * 1024 * 1024;
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const git = (argv) => execFileSync("git", argv, { cwd: repo, encoding: "buffer", maxBuffer: 64 * 1024 * 1024 }).toString("utf8").split("\0").filter(Boolean);
const walk = (root) => fs.readdirSync(root, { withFileTypes: true }).flatMap((entry) => {
  const target = path.join(root, entry.name);
  return entry.isDirectory() ? walk(target) : entry.isFile() ? [target] : [];
}).sort();
const receipt = (file) => {
  const bytes = fs.readFileSync(file);
  return { path: path.relative(repo, file).replaceAll("\\", "/"), sha256: sha(bytes), bytes: bytes.length };
};
const contentIdentity = (files) => sha(Buffer.from(canonical(files.map(({ path: filePath, sha256, bytes }) => ({ path: filePath, sha256, bytes })))));

const roots = git(["ls-files", "--others", "--exclude-standard", "--directory", "--no-empty-directory", "-z"]);
const artifacts = [];
for (const root of roots) {
  const absolute = path.join(repo, root.replace(/\/$/, ""));
  if (!fs.existsSync(absolute)) continue;
  const files = fs.statSync(absolute).isDirectory() ? walk(absolute).map(receipt) : [receipt(absolute)];
  const bytes = files.reduce((sum, row) => sum + row.bytes, 0);
  if (bytes > threshold) artifacts.push({ path: root.replace(/\/$/, ""), kind: fs.statSync(absolute).isDirectory() ? "DIRECTORY" : "FILE", files: files.length, bytes, content_identity_sha256: contentIdentity(files) });
}
const largeFiles = git(["ls-files", "--others", "--exclude-standard", "-z"]).map((relative) => path.join(repo, relative)).filter((file) => fs.existsSync(file) && fs.statSync(file).isFile() && fs.statSync(file).size > threshold).map(receipt);
const census = {
  label: "WORKTREE_CENSUS_LAW_UNTRACKED_OVER_10_MIB",
  phase,
  threshold: { operator_text: ">10 MB", implemented_bytes_strictly_greater_than: threshold },
  law: "Every close-out enumerates ALL untracked artifacts >10 MB in the worktree; an undisclosed pile discovered later is a violation of the close-out that omitted it.",
  license: { law_index_read_at: "53db48ac", law_index_sha256: "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934", cited_laws: ["L8", "L18", "L20", "L22"], index_gap: ["L20", "L22"] },
  scope: { receipt_only: true, passes: 0, reruns: 0, full_804_runs_started: 0 },
  untracked_artifacts_over_threshold: artifacts.sort((a, b) => a.path.localeCompare(b.path)),
  untracked_regular_files_over_threshold: largeFiles.sort((a, b) => a.path.localeCompare(b.path)),
  counts: { artifacts: artifacts.length, regular_files: largeFiles.length },
};
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, canonical(census), "utf8");
const bytes = fs.readFileSync(output);
process.stdout.write(canonical({ path: output, sha256: sha(bytes), bytes: bytes.length, ...census.counts }));
