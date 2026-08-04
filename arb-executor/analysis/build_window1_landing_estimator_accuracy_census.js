#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : fallback; };
const repo = path.resolve(arg("--repo", "."));
const out = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804")));
const compare1 = arg("--compare-run1", null), compare2 = arg("--compare-run2", null);
const v24Dir = path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804");
const v23Dir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804");

function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(v) { return `${JSON.stringify(v, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(p) { return sha256(fs.readFileSync(p)); }
function readRows(p) { const t = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return t ? t.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function group(rows, fn) { const m = new Map(); for (const r of rows) { const k = fn(r); if (!m.has(k)) m.set(k, []); m.get(k).push(r); } return m; }
function quantile(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function distribution(values) { const xs = values.filter(Number.isFinite); return { n: xs.length, min: xs.length ? Math.min(...xs) : null, p25: quantile(xs, .25), median: quantile(xs, .5), p75: quantile(xs, .75), p90: quantile(xs, .9), max: xs.length ? Math.max(...xs) : null }; }
function mean(values) { const xs = values.filter(Number.isFinite); return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null; }

function summary(rows) {
  const errors = rows.map((r) => r.signed_error_cents), abs = errors.map(Math.abs), baseAbs = rows.map((r) => Math.abs(r.live_ask_minus_audited_close_cents));
  return {
    n: rows.length,
    q50_signed_error_cents: distribution(errors),
    MAE_cents: mean(abs),
    bias_cents: mean(errors),
    current_live_ask_baseline_MAE_cents: mean(baseAbs),
    q25_q75_interval_inside_n: rows.filter((r) => r.audited_close_inside_q25_q75).length,
    q25_q75_interval_calibration: rows.length ? rows.filter((r) => r.audited_close_inside_q25_q75).length / rows.length : null,
  };
}

function authority(cell) {
  const s = summary(cell);
  const checks = {
    validation_n_at_least_30: s.n >= 30,
    q50_MAE_strictly_beats_live_ask_baseline: s.MAE_cents < s.current_live_ask_baseline_MAE_cents,
    central_50pct_interval_calibration_at_least_50pct: s.q25_q75_interval_calibration >= .5,
  };
  return { authorized: Object.values(checks).every(Boolean), checks, stated_error_bar: "CELL q50 MAE MUST BE STRICTLY LOWER THAN DECISION-TIME LIVE-ASK-AS-CLOSE MAE; n>=30; q25-q75 empirical coverage>=0.50", metrics: s };
}

function compareBuilds(a, b) {
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const aa = fs.readdirSync(a).filter((n) => !excluded.has(n)).sort(), bb = fs.readdirSync(b).filter((n) => !excluded.has(n)).sort();
  ensure(JSON.stringify(aa) === JSON.stringify(bb), "file census mismatch");
  const mismatches = aa.filter((n) => hashFile(path.join(a, n)) !== hashFile(path.join(b, n)));
  ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`);
  return { clean_builds: 2, compared_files: aa.length, byte_identical: true, mismatches: [] };
}

function main() {
  const decisionsPath = path.join(v24Dir, "LANDING_ESTIMATE_RECEIPTS.jsonl.gz"), legsPath = path.join(v23Dir, "V23_LEG_LEDGER.jsonl.gz");
  ensure(fs.existsSync(decisionsPath) && fs.existsSync(legsPath), "frozen inputs absent");
  const decisions = readRows(decisionsPath), legs = readRows(legsPath), byLeg = new Map(legs.map((r) => [r.leg_identity, r]));
  ensure(legs.length === 1608, "leg denominator");
  const rows = [];
  for (const receipt of decisions) {
    if (receipt.landing_estimate?.state !== "BOUND") continue;
    const leg = byLeg.get(receipt.leg_identity); ensure(leg, `unknown leg ${receipt.leg_identity}`);
    const liveAsk = receipt.live_book?.ask ?? receipt.live_book_at_resolution?.ask;
    const close = leg.audited_close_cents;
    if (!Number.isInteger(liveAsk) || !Number.isInteger(close)) continue;
    const directName = `${leg.category}|${receipt.path_family}`;
    rows.push({
      leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, role: receipt.role,
      decision_timestamp_epoch: receipt.pair_resolution?.timestamp_epoch ?? null,
      t_minus_scheduled_seconds: receipt.pair_resolution?.t_minus_scheduled_seconds ?? null,
      t_minus_actual_bell_seconds: receipt.pair_resolution?.t_minus_actual_bell_seconds ?? null,
      path_family: receipt.path_family, source_tier: receipt.landing_estimate.borrowed_from === directName ? "DIRECT_CATEGORY_X_PATH_FAMILY" : "PARENT_POOL",
      borrowed_from: receipt.landing_estimate.borrowed_from, training_n: receipt.landing_estimate.n,
      live_ask_cents: liveAsk, q25_cents: receipt.landing_estimate.q25, q50_cents: receipt.landing_estimate.q50, q75_cents: receipt.landing_estimate.q75,
      audited_close_cents: close, signed_error_cents: receipt.landing_estimate.q50 - close, absolute_error_cents: Math.abs(receipt.landing_estimate.q50 - close),
      live_ask_minus_audited_close_cents: liveAsk - close,
      audited_close_inside_q25_q75: close >= receipt.landing_estimate.q25 && close <= receipt.landing_estimate.q75,
      walk_forward_proof: receipt.landing_estimate.walk_forward_proof,
    });
  }
  ensure(rows.every((r) => r.walk_forward_proof), "non-walk-forward row");
  const cells = [...group(rows, (r) => `${r.category}|${r.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rs]) => {
    const [category, price_region] = key.split("|");
    return { category, price_region, all: summary(rs), direct: summary(rs.filter((r) => r.source_tier.startsWith("DIRECT"))), parent_pool: summary(rs.filter((r) => r.source_tier === "PARENT_POOL")), overlay_authority: authority(rs) };
  });
  const authorityCells = cells.filter((c) => c.overlay_authority.authorized).map((c) => `${c.category}|${c.price_region}`);
  const result = {
    population_legs: 1608,
    estimator_covered_and_audited_close_available: rows.length,
    coverage_rate: rows.length / 1608,
    uncovered_or_close_unavailable: 1608 - rows.length,
    aggregate: summary(rows),
    direct: summary(rows.filter((r) => r.source_tier.startsWith("DIRECT"))),
    parent_pool: summary(rows.filter((r) => r.source_tier === "PARENT_POOL")),
    category_x_price_region: cells,
    overlay_authority_law: authority([]).stated_error_bar,
    authorized_cells: authorityCells,
    authorized_cell_count: authorityCells.length,
  };
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "ESTIMATOR_ACCURACY_CENSUS.json"), canonical(result));
  fs.writeFileSync(path.join(out, "ESTIMATOR_ACCURACY_LEDGER.jsonl.gz"), gzipRows(rows));
  fs.writeFileSync(path.join(out, "OVERLAY_CELL_AUTHORITY.json"), canonical({ law: result.overlay_authority_law, cells: cells.map((c) => ({ category: c.category, price_region: c.price_region, ...c.overlay_authority })), authorized_cells: authorityCells }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ placement_logic_executed: false, scorer_executed: false, development_only: true, holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false }));
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ inputs: { [path.relative(repo, decisionsPath).replaceAll("\\", "/")]: { sha256: hashFile(decisionsPath), bytes: fs.statSync(decisionsPath).size }, [path.relative(repo, legsPath).replaceAll("\\", "/")]: { sha256: hashFile(legsPath), bytes: fs.statSync(legsPath).size } }, code: { "arb-executor/analysis/build_window1_landing_estimator_accuracy_census.js": { sha256: hashFile(__filename), bytes: fs.statSync(__filename).size }, "arb-executor/tests/test_window1_landing_estimator_accuracy_census.js": { sha256: hashFile(path.join(repo, "arb-executor/tests/test_window1_landing_estimator_accuracy_census.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_landing_estimator_accuracy_census.js")).size } } }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# Landing estimator standalone accuracy census\n\nThis census executes no placement logic. It measures every causally walk-forward q25/q50/q75 estimate with an audited close. Cell authority requires n>=30, q50 MAE strictly below the decision-time live-ask baseline MAE, and q25-q75 coverage >=0.50.\n`);
  if (compare1 && compare2) fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(compareBuilds(path.resolve(compare1), path.resolve(compare2))));
  const names = fs.readdirSync(out).filter((n) => n !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((n) => [n, { sha256: hashFile(path.join(out, n)), bytes: fs.statSync(path.join(out, n)).size }])) }));
  process.stdout.write(canonical(result));
}

if (require.main === module) main();
module.exports = { authority, summary };
