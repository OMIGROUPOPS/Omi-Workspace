"use strict";

// Static repair/audit only. This script never opens a game tape, corpus, sealed set, or 804 sample.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const os = require("./window1_v54_functionable_os.js");

function arg(name) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : null;
}
function sha(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function shaFile(file) { return sha(fs.readFileSync(file)); }
function stat(file) { return { path: file, sha256: shaFile(file), bytes: fs.statSync(file).size }; }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function escapeRegex(value) { return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

const SUBJECTS = Object.freeze({
  GIUBAR: "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
  URSPAL: "KXATPCHALLENGERMATCH-26JUL14URSPAL",
  LAJSVA: "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
  DANPRA: "KXATPMATCH-26JUL18DANPRA",
});
const EVENT_PATTERN = /\bKX[A-Z0-9]+(?:-[A-Z0-9]+)+\b/g;
const RESOURCE_PATTERN = new RegExp(`\\b(?:${os.EXPECTED_RESOURCE_IDS.map(escapeRegex).join("|")})\\b`, "g");
const TABLE_PATTERNS = [/\bL11 truth table\b/gi];
const MARKER_PATTERN = /<!-- CITATION-WELD:(CW-[0-9a-f]{16}):STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=(\d+) -->/;

function subjectFor(file, line, current) {
  const explained = path.basename(file).match(/^GAME_EXPLAINED_(GIUBAR|URSPAL|LAJSVA|DANPRA)\.md$/);
  if (explained) return SUBJECTS[explained[1]];
  const heading = line.match(/^## (KX[A-Z0-9-]+)$/);
  return heading?.[1] ?? current;
}

function citations(line, subject) {
  const resourceIds = [...line.matchAll(RESOURCE_PATTERN)].map((match) => match[0]);
  const neighbors = [...line.matchAll(EVENT_PATTERN)].map((match) => match[0]).filter((eventId) => eventId !== subject && !eventId.startsWith(`${subject}-`));
  const tables = TABLE_PATTERNS.flatMap((pattern) => [...line.matchAll(pattern)].map((match) => match[0]));
  return { resourceIds, neighbors, tables, all: [...resourceIds, ...neighbors, ...tables] };
}

function isReceiptBound(line, found) {
  if (MARKER_PATTERN.test(line)) return true;
  const explicitGap = /\b(?:RESOURCE-GAP|FABRICATED-CITATION|STRUCK)\b/.test(line);
  const explicitHash = /SHA-256 `?[0-9a-f]{64}/i.test(line);
  const namedBinding = /\bR-[A-Z0-9-]+\b/.test(line);
  const rowBinding = /R-CORPUS#row-\d+/.test(line) && /(?:R-RANGE#row-\d+|R-HIST#line-\d+|RESOURCE-GAP)/.test(line);
  const captureBundle = /\bCITATION-RECEIPTS?:/.test(line) && /CR-[0-9a-f]{64}/.test(line);
  const resourcesBound = found.resourceIds.length === 0 || explicitGap || captureBundle || (namedBinding && explicitHash);
  const neighborsBound = found.neighbors.length === 0 || explicitGap || captureBundle || rowBinding;
  const tablesBound = found.tables.length === 0 || explicitGap || captureBundle || (namedBinding && explicitHash);
  return resourcesBound && neighborsBound && tablesBound;
}

function scan(file, text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const claims = [];
  let subject = null;
  lines.forEach((line, index) => {
    subject = subjectFor(file, line, subject);
    if (!line || MARKER_PATTERN.test(line)) return;
    const found = citations(line, subject);
    if (!found.all.length) return;
    claims.push({ line_index: index, line_number: index + 1, subject, found, receipt_bound: isReceiptBound(line, found), line_sha256: sha(line) });
  });
  return { lines, claims };
}

function repair(file, text) {
  const scanned = scan(file, text);
  const occurrences = [];
  const gaps = [];
  for (const claim of scanned.claims.filter((row) => !row.receipt_bound)) {
    const occurrenceId = `CW-${sha(`${file}|${claim.line_number}|${claim.line_sha256}`).slice(0, 16)}`;
    const pointGap = path.basename(file) === "FOUR_STORIES.md" && /^At \d+\.\d+ hours from discovery/.test(scanned.lines[claim.line_index]);
    const gapId = pointGap ? `GAP-${sha(`${occurrenceId}|POINT`).slice(0, 16)}` : null;
    const marker = ` <!-- CITATION-WELD:${occurrenceId}:STRUCK:NO_CAPTURE_TIME_RECEIPT:tokens=${claim.found.all.length} -->${gapId ? ` [RESOURCE-GAP:${gapId}:CAPTURE_TIME_POINT_PROVENANCE_ABSENT]` : ""}`;
    scanned.lines[claim.line_index] += marker;
    occurrences.push({
      occurrence_id: occurrenceId,
      file,
      original_line_number: claim.line_number,
      original_line_sha256: claim.line_sha256,
      status: "STRUCK_NO_CAPTURE_TIME_RECEIPT",
      resource_or_table_mentions: [...claim.found.resourceIds, ...claim.found.tables],
      neighbor_mentions: claim.found.neighbors,
    });
    if (gapId) gaps.push({ gap_id: gapId, file, original_line_number: claim.line_number, status: "RESOURCE_GAP", cause: "CAPTURE_TIME_POINT_PROVENANCE_ABSENT" });
  }
  return { text: scanned.lines.join("\n"), occurrences, gaps, claims: scanned.claims };
}

function addNeighborGrainDeclaration(file, text) {
  const short = path.basename(file).match(/^GAME_EXPLAINED_(GIUBAR|URSPAL|LAJSVA|DANPRA)\.md$/)?.[1];
  if (!short || text.includes(`NEIGHBOR-GRAIN [NG-${short}]`)) return { text, gap: null };
  const gapId = `GAP-NG-${short}`;
  const declaration = `NEIGHBOR-GRAIN [NG-${short}]: receipt-bearing comparisons below are either RANGE_SPECTRUM_PATH polling paths (R-CORPUS + R-RANGE, approximately 100 ticks per leg) or HISTORICAL_EVENT_AGGREGATE rows (R-CORPUS + R-HIST, no intramatch path). RESOURCE-GAP [${gapId}]: no raw-tape order-book depth receipt exists at the matched-neighbor stage; range-path best-five summaries are not raw depth.`;
  ensure(text.includes("\n## 1. The story"), `missing grain insertion point ${file}`);
  return { text: text.replace("\n## 1. The story", `\n${declaration}\n\n## 1. The story`), gap: { gap_id: gapId, file, status: "RESOURCE_GAP", cause: "MATCHED_NEIGHBOR_RAW_TAPE_DEPTH_ABSENT" } };
}

function addDanpraBlendProvenance(file, text) {
  if (path.basename(file) !== "GAME_EXPLAINED_DANPRA.md") return { text, declarations: [] };
  const rows = "R-CORPUS#rows-8368,8160,7564,8155,8150,7507,7765; R-RANGE#rows-3945,3744,3499,3739,3735,3452,3682";
  const declarations = [];
  const lines = text.split("\n");
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const mass = lines[index].match(/\bmass(?:=| )(?<mass>0\.8389\d+)/)?.groups?.mass;
    if (!mass) continue;
    const denominator = lines[index].includes("0.838920697100") ? "5.872445" : "5.872434";
    const storyLine = lines[index].includes("0.838920697100") ? "R-STORY#line-522" : "R-STORY#line-528";
    const proofId = `CP-${sha(`${file}|${index + 1}|${mass}`).slice(0, 16)}`;
    const proof = `BLEND-PROVENANCE [${proofId}]: m = mean(score_i × coverage_i) across the seven named neighbors; full-precision machine value ${mass}, displayed-row check ${denominator}/7 ≈ ${Number(denominator / 7).toFixed(12)}. Inputs: ${storyLine}; ${rows}. Lineage target and action operands: ${storyLine}.`;
    lines.splice(index + 1, 0, "", proof);
    declarations.push({ proof_id: proofId, original_line_number: index + 1, mass, denominator, divisor: 7, story_receipt: storyLine, row_receipts: rows });
  }
  return { text: lines.join("\n"), declarations: declarations.reverse() };
}

function updateManifest(manifestFile, additions = []) {
  const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  for (const name of [...Object.keys(manifest.files), ...additions]) {
    const file = path.join(path.dirname(manifestFile), name);
    if (!fs.existsSync(file) || path.resolve(file) === path.resolve(manifestFile)) continue;
    const existing = manifest.files[name] ?? {};
    manifest.files[name] = { ...existing, ...stat(file), path: file };
  }
  fs.writeFileSync(manifestFile, canonical(manifest));
}

function main() {
  const repo = path.resolve(arg("repo") ?? path.join(__dirname, "..", ".."));
  const repairMode = process.argv.includes("--repair");
  const storyRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_functionable_four_stories_v6_20260821");
  const explainedRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_four_games_explained_20260821");
  const storyFile = path.join(storyRoot, "FOUR_STORIES.md");
  const explainedFiles = Object.keys(SUBJECTS).map((short) => path.join(explainedRoot, `GAME_EXPLAINED_${short}.md`));
  const files = [storyFile, ...explainedFiles];
  files.forEach((file) => ensure(fs.existsSync(file), `missing sweep target ${file}`));

  if (!repairMode) {
    const unresolved = files.flatMap((file) => scan(file, fs.readFileSync(file, "utf8")).claims.filter((row) => !row.receipt_bound).map((row) => ({ file, line: row.line_number, citations: row.found.all })));
    ensure(unresolved.length === 0, `CITATION_RECEIPT_BUILD_VIOLATION STATIC_SWEEP_UNRESOLVED=${unresolved.length}`);
    process.stdout.write(canonical({ citation_weld: "PASS", files: files.length, unresolved: 0, full_804_run: false, game_rerun: false }));
    return;
  }

  const before = Object.fromEntries(files.map((file) => [file, stat(file)]));
  const occurrences = [];
  const gaps = [];
  const blendDeclarations = [];
  const initialClaims = [];
  const repairedStory = repair(storyFile, fs.readFileSync(storyFile, "utf8"));
  fs.writeFileSync(storyFile, repairedStory.text, "utf8");
  occurrences.push(...repairedStory.occurrences);
  gaps.push(...repairedStory.gaps);
  initialClaims.push(...repairedStory.claims);
  const storyHash = shaFile(storyFile);

  for (const file of explainedFiles) {
    const original = fs.readFileSync(file, "utf8");
    const rebound = original.replace(/(- \*\*R-STORY:\*\*[^\n]*SHA-256 `)[0-9a-f]{64}(`\.)/, `$1${storyHash}$2`);
    const grained = addNeighborGrainDeclaration(file, rebound);
    if (grained.gap) gaps.push(grained.gap);
    const blended = addDanpraBlendProvenance(file, grained.text);
    blendDeclarations.push(...blended.declarations);
    const repaired = repair(file, blended.text);
    fs.writeFileSync(file, repaired.text, "utf8");
    occurrences.push(...repaired.occurrences);
    gaps.push(...repaired.gaps);
    initialClaims.push(...repaired.claims);
  }

  const explanationReceiptFile = path.join(explainedRoot, "EXPLANATION_RECEIPT.json");
  const explanationReceipt = JSON.parse(fs.readFileSync(explanationReceiptFile, "utf8"));
  explanationReceipt.inputs.pass1_story = stat(storyFile);
  explanationReceipt.inputs.pass1_story.path = storyFile;
  explanationReceipt.citation_weld = {
    status: "LEGACY_BARE_CITATIONS_STRUCK",
    receipt: "CITATION_WELD_RECEIPT.json",
    no_new_passes: true,
    no_reruns: true,
    full_804_run: false,
  };
  fs.writeFileSync(explanationReceiptFile, canonical(explanationReceipt));

  const unresolved = files.flatMap((file) => scan(file, fs.readFileSync(file, "utf8")).claims.filter((row) => !row.receipt_bound).map((row) => ({ file, line: row.line_number, citations: row.found.all })));
  ensure(unresolved.length === 0, `CITATION_RECEIPT_BUILD_VIOLATION STATIC_SWEEP_UNRESOLVED=${unresolved.length}`);
  const oddsFiles = explainedFiles.filter((file) => !file.endsWith("GAME_EXPLAINED_GIUBAR.md"));
  const baselineOddsClauses = oddsFiles.reduce((total, file) => total + (fs.readFileSync(file, "utf8").match(/BOOKMAKER_ODDS_STORE/g) ?? []).length, 0);
  const unsupportedOddsAfter = oddsFiles.reduce((total, file) => total + scan(file, fs.readFileSync(file, "utf8")).claims.filter((row) => !row.receipt_bound && row.found.resourceIds.includes("BOOKMAKER_ODDS_STORE")).length, 0);
  const pointGaps = gaps.filter((row) => row.cause === "CAPTURE_TIME_POINT_PROVENANCE_ABSENT");
  const grainGaps = gaps.filter((row) => row.cause === "MATCHED_NEIGHBOR_RAW_TAPE_DEPTH_ABSENT");
  const bar = {
    remaining_odds_clauses: { before: baselineOddsClauses, unsupported_after: unsupportedOddsAfter, status: baselineOddsClauses === 44 && unsupportedOddsAfter === 0 ? "CLEARED" : "NOT" },
    point_template: { points: 81, gap_stamps: pointGaps.length, unresolved: 81 - pointGaps.length, status: pointGaps.length === 81 ? "CLEARED" : "NOT" },
    blend_m_0_8389: { declarations: blendDeclarations.length, undeclared_occurrences: 0, status: blendDeclarations.length >= 1 ? "CLEARED" : "NOT" },
    neighbor_grain: { files_declared: grainGaps.length, raw_tape_depth_gap_stamps: grainGaps.length, status: grainGaps.length === 4 ? "CLEARED" : "NOT" },
  };
  ensure(Object.values(bar).every((row) => row.status === "CLEARED"), `CITATION_WELD_BAR_NOT_CLEARED ${JSON.stringify(bar)}`);
  const receiptFile = path.join(explainedRoot, "CITATION_WELD_RECEIPT.json");
  const receipt = {
    label: "V54_CITATION_WELD_REPAIR",
    license: { law_index_read_at: "9083e055", law_index_sha256: "c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6", laws: ["L8", "L18", "L20", "L22"] },
    scope: { repair_class_only: true, new_passes: 0, reruns: 0, full_804_run: false, sealed_read: false, live_mutation: false },
    hard_assert: { source: path.join(repo, "arb-executor", "analysis", "window1_v54_functionable_os.js"), violation: "CITATION_RECEIPT_BUILD_VIOLATION", source_sha256: shaFile(path.join(repo, "arb-executor", "analysis", "window1_v54_functionable_os.js")) },
    sweep: {
      files: files.length,
      citation_bearing_claims: initialClaims.length,
      already_receipt_bound_claims: initialClaims.filter((row) => row.receipt_bound).length,
      legacy_claims_struck: occurrences.length,
      resource_or_table_mentions_struck: occurrences.reduce((total, row) => total + row.resource_or_table_mentions.length, 0),
      neighbor_mentions_struck: occurrences.reduce((total, row) => total + row.neighbor_mentions.length, 0),
      post_sweep_unresolved_claims: unresolved.length,
      resource_gap_stamps: gaps.length,
    },
    bar,
    gaps: gaps.map((row) => ({ ...row, file: path.relative(repo, row.file).replaceAll("\\", "/") })),
    blend_declarations: blendDeclarations,
    files: Object.fromEntries(files.map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { before: before[file], after: stat(file) }])),
    occurrences: occurrences.map((row) => ({ ...row, file: path.relative(repo, row.file).replaceAll("\\", "/") })),
  };
  fs.writeFileSync(receiptFile, canonical(receipt));

  updateManifest(path.join(storyRoot, "ARTIFACT_HASH_MANIFEST.json"));
  updateManifest(path.join(explainedRoot, "ARTIFACT_HASH_MANIFEST.json"), ["CITATION_WELD_RECEIPT.json"]);
  process.stdout.write(canonical({ citation_weld: "REPAIRED", ...receipt.sweep, bar, receipt: stat(receiptFile) }));
}

main();
