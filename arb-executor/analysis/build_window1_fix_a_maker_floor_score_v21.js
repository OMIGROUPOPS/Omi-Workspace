#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/fix_a_maker_floor_score_v21_20260804")));
const fixALedger = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/POPULATION_LEG_LEDGER.jsonl.gz");
const referenceCommit = "08fe622badbf92bb43a2f2acbd78b515a1ad5308";
const referencePath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_FLOOR_REGRET_896.csv";
const referenceSummaryPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_FLOOR_CORRECTED_SUMMARY.json";
const artifactRel = ".claude/window1_live_v4_replay/fix_a_maker_floor_score_v21_20260804";
const raw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function ensure(x, message) { if (!x) throw new Error(message); }
function integer(value) { if (value === "" || value === null || value === undefined) return null; const n = Number(value); return Number.isInteger(n) ? n : null; }
function readGzipRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(bytes) { const lines = bytes.toString("utf8").trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((item, i) => [headers[i], item]))); }
function quantile(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function distribution(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, unavailable_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: quantile(xs, .25), median: quantile(xs, .5), p75: quantile(xs, .75), p90: quantile(xs, .9), max: xs.length ? Math.max(...xs) : null, total_numeric_cents: xs.reduce((a, b) => a + b, 0) }; }
function bucket(gap) { if (!Number.isInteger(gap)) return "MAKER_FLOOR_UNAVAILABLE"; if (gap < 0) return "BETTER_THAN_MAKER_FLOOR"; if (gap === 0) return "EXACT_MAKER_FLOOR"; if (gap === 1) return "ONE_CENT_ABOVE_MAKER_FLOOR"; if (gap <= 3) return "TWO_TO_THREE_ABOVE_MAKER_FLOOR"; if (gap <= 9) return "FOUR_TO_NINE_ABOVE_MAKER_FLOOR"; return "TEN_OR_MORE_ABOVE_MAKER_FLOOR"; }
function group(rows, key) { const map = new Map(); for (const row of rows) { const k = key(row); if (!map.has(k)) map.set(k, []); map.get(k).push(row); } return map; }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = key(row); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort()); }
function gitShow(spec) { return childProcess.execFileSync("git", ["show", spec], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }

function summarize(rows) {
  return {
    recovered_legs: rows.length,
    maker_floor_available: rows.filter((row) => Number.isInteger(row.maker_floor_cents)).length,
    seller_aggressed_floor_available: rows.filter((row) => Number.isInteger(row.seller_aggressed_traded_low_cents)).length,
    maker_floor_below_qualifying_ask: rows.filter((row) => Number.isInteger(row.maker_floor_cents) && Number.isInteger(row.qualifying_ask_floor_cents) && row.maker_floor_cents < row.qualifying_ask_floor_cents).length,
    gap_to_maker_floor: distribution(rows.map((row) => row.entry_minus_maker_floor_cents)),
    gap_to_qualifying_ask_floor: distribution(rows.map((row) => row.entry_minus_qualifying_ask_floor_cents)),
    maker_floor_buckets: countBy(rows, (row) => row.maker_floor_bucket),
    maker_floor_source: countBy(rows, (row) => row.maker_floor_source),
  };
}

function main() {
  ensure(fs.existsSync(fixALedger), `missing ${fixALedger}`);
  const verifiedCommit = childProcess.execFileSync("git", ["rev-parse", "--verify", `${referenceCommit}^{commit}`], { cwd: repo, encoding: "utf8" }).trim();
  ensure(verifiedCommit === referenceCommit, "reference commit mismatch");
  childProcess.execFileSync("git", ["cat-file", "-e", `${referenceCommit}^{commit}`], { cwd: repo });
  const csvBytes = gitShow(`${referenceCommit}:${referencePath}`);
  const summaryBytes = gitShow(`${referenceCommit}:${referenceSummaryPath}`);
  const referenceRows = parseCsv(csvBytes), referenceByTicker = new Map(referenceRows.map((row) => [row.ticker, row]));
  ensure(referenceRows.length === 896 && referenceByTicker.size === 896, "reference surface must contain 896 unique legs");
  const referenceSummary = JSON.parse(summaryBytes);
  ensure(referenceSummary.correction.startsWith("maker_floor(leg)=min(qualifying_ask_floor, seller_aggressed_traded_low)"), "maker-floor law mismatch");
  const recovered = readGzipRows(fixALedger).filter((row) => row.isolated_repair_added);
  ensure(recovered.length === 337, `expected 337 Fix A recovered legs, got ${recovered.length}`);
  const rows = recovered.map((leg) => {
    const ref = referenceByTicker.get(leg.ticker);
    ensure(ref, `maker-floor reference missing ${leg.ticker}`);
    const ask = integer(ref.qualifying_ask_floor_cents), seller = integer(ref.seller_aggressed_traded_low_cents), publishedMaker = integer(ref.maker_floor_cents);
    const recomputed = [ask, seller].filter(Number.isInteger).reduce((min, value) => min === null || value < min ? value : min, null);
    ensure(recomputed === publishedMaker, `published maker floor mismatch ${leg.ticker}`);
    ensure(ask === leg.qualifying_ask_floor_cents, `qualifying ask mismatch ${leg.ticker}`);
    const entry = leg.entry_cents;
    ensure(Number.isInteger(entry) && leg.credited, `recovered leg must have credited integer entry ${leg.ticker}`);
    const makerGap = publishedMaker === null ? null : entry - publishedMaker;
    const askGap = ask === null ? null : entry - ask;
    return {
      leg_identity: leg.leg_identity,
      event_id: leg.event_id,
      ticker: leg.ticker,
      category: leg.category,
      price_region: leg.price_region,
      entry_cents: entry,
      qualifying_ask_floor_cents: ask,
      seller_aggressed_traded_low_cents: seller,
      maker_floor_cents: publishedMaker,
      maker_floor_source: publishedMaker === null ? "UNAVAILABLE" : seller !== null && seller < ask ? "SELLER_AGGRESSED_TRADED_LOW" : seller !== null && seller === ask ? "ASK_AND_SELLER_TIE" : "QUALIFYING_ASK_RESIDENCY",
      entry_minus_qualifying_ask_floor_cents: askGap,
      entry_minus_maker_floor_cents: makerGap,
      maker_floor_bucket: bucket(makerGap),
      action_timestamp_epoch: leg.action_timestamp_epoch,
      exact_reference_commit: referenceCommit,
      exact_reference_ticker_row: ref,
    };
  }).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, members]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], ...summarize(members), leg_identities: members.map((row) => row.leg_identity) }));
  const result = {
    schema_version: "WINDOW1_FIX_A_RECOVERED_LEG_MAKER_FLOOR_SCORE_V21",
    law: "MAKER_FLOOR = MIN(QUALIFYING_ASK_FLOOR, SELLER_AGGRESSED_TRADED_LOW)",
    ruling: { commit: referenceCommit, summary_path: referenceSummaryPath, ledger_path: referencePath, summary_sha256: sha256(summaryBytes), ledger_sha256: sha256(csvBytes), reference_rows: referenceRows.length },
    aggregate: summarize(rows),
    category_x_price_region: cells,
    conservation: { recovered_legs: rows.length, partition_rows: cells.reduce((sum, row) => sum + row.recovered_legs, 0), reference_joined: rows.length, missing_reference: 0, maker_floor_recomputation_mismatches: 0, qualifying_ask_mismatches: 0 },
    claim: "DEVELOPMENT_REPLAY_DIAGNOSTIC; FIX_A_RECOVERED_LEGS_ONLY; NOT_HOLDOUT; NOT_MARKET_CEILING",
  };
  ensure(result.conservation.partition_rows === 337, "partition conservation failed");
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "FIX_A_RECOVERED_LEG_MAKER_FLOOR_LEDGER.jsonl.gz"), gzipRows(rows));
  fs.writeFileSync(path.join(out, "FIX_A_MAKER_FLOOR_SCORE.json"), canonical(result));
  fs.writeFileSync(path.join(out, "REFERENCE_BINDING_RECEIPT.json"), canonical(result.ruling));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical({
    schema_version: "WINDOW1_FIX_A_MAKER_FLOOR_SCORE_V21_DETERMINISM",
    clean_builds: 2,
    comparison: "RELATIVE_PATH_SIZE_AND_SHA256",
    regenerable_artifacts_byte_identical: true,
    generated_at_runtime_timestamp: null,
  }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# Fix A recovered legs against corrected maker floors\n\n- Score: ${raw}/${artifactRel}/FIX_A_MAKER_FLOOR_SCORE.json\n- Exact ledger: ${raw}/${artifactRel}/FIX_A_RECOVERED_LEG_MAKER_FLOOR_LEDGER.jsonl.gz\n- Reference binding: ${raw}/${artifactRel}/REFERENCE_BINDING_RECEIPT.json\n`);
  const sourceFiles = [fixALedger, __filename];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sourceFiles.map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), git_object_inputs: { [`${referenceCommit}:${referencePath}`]: { sha256: sha256(csvBytes), bytes: csvBytes.length }, [`${referenceCommit}:${referenceSummaryPath}`]: { sha256: sha256(summaryBytes), bytes: summaryBytes.length } } }));
  const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical(result));
}

main();
