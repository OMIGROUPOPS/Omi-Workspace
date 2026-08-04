#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { scoreVariant } = require("./build_window1_pair_cap_v23.js");
const { overlayDecision } = require("./window1_landing_estimator_overlay_v25_policy.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : fallback; };
const repo = path.resolve(arg("--repo", "."));
const out = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804")));
const compare1 = arg("--compare-run1", null), compare2 = arg("--compare-run2", null);
const v23Dir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804");
const v24Dir = path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804");
const accuracyDir = path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804");

function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(v) { return `${JSON.stringify(v, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(p) { return sha256(fs.readFileSync(p)); }
function readRows(p) { const t = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return t ? t.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function countBy(rows, fn) { const out = {}; for (const r of rows) { const k = String(fn(r)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function jsonHash(v) { return sha256(Buffer.from(JSON.stringify(v))); }

function compareBuilds(a, b) {
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const aa = fs.readdirSync(a).filter((n) => !excluded.has(n)).sort(), bb = fs.readdirSync(b).filter((n) => !excluded.has(n)).sort();
  ensure(JSON.stringify(aa) === JSON.stringify(bb), "file census mismatch");
  const mismatches = aa.filter((n) => hashFile(path.join(a, n)) !== hashFile(path.join(b, n)));
  ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`);
  return { clean_builds: 2, compared_files: aa.length, byte_identical: true, mismatches: [] };
}

function main() {
  const eventPath = path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz"), legPath = path.join(v23Dir, "V23_LEG_LEDGER.jsonl.gz");
  const authorityPath = path.join(accuracyDir, "OVERLAY_CELL_AUTHORITY.json"), accuracyLedgerPath = path.join(accuracyDir, "ESTIMATOR_ACCURACY_LEDGER.jsonl.gz");
  const v24LegPath = path.join(v24Dir, "V24_LEG_LEDGER.jsonl.gz"), v23FrontierPath = path.join(v23Dir, "FRONTIER.json"), v23RegretPath = path.join(v23Dir, "REGRET_GAUGE.json");
  for (const p of [eventPath, legPath, authorityPath, accuracyLedgerPath, v24LegPath, v23FrontierPath, v23RegretPath]) ensure(fs.existsSync(p), `missing ${p}`);
  const eventBytes = fs.readFileSync(eventPath), legBytes = fs.readFileSync(legPath), events = readRows(eventPath), legs = readRows(legPath);
  ensure(events.length === 804 && legs.length === 1608, "V23 conservation");
  const authority = JSON.parse(fs.readFileSync(authorityPath, "utf8")), authorized = new Set(authority.authorized_cells);
  const accuracyRows = readRows(accuracyLedgerPath), estimateByLeg = new Map(accuracyRows.map((r) => [r.leg_identity, r]));
  const v24Legs = readRows(v24LegPath), v24ByLeg = new Map(v24Legs.map((r) => [r.leg_identity, r]));
  const overlay = legs.map((leg) => {
    const cellAuthorized = authorized.has(`${leg.category}|${leg.price_region}`), estimate = estimateByLeg.get(leg.leg_identity);
    const v24 = v24ByLeg.get(leg.leg_identity), phased = v24?.v24_role === "MIRROR_PHASED" && v24.acted ? { state: "PLACE", price_cents: v24.entry_cents ?? v24.placement?.price_cents } : null;
    const incumbentAction = leg.acted ? { price_cents: leg.entry_cents ?? leg.placement?.price_cents } : null;
    const decision = overlayDecision({ cellAuthorized, incumbentAction, estimate: estimate ? { state: "BOUND", q50: estimate.q50_cents } : null, phasedMirrorCandidate: phased });
    return { leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, cell_authorized: cellAuthorized, estimate_covered: Boolean(estimate), decision };
  });
  const changesAuthorized = overlay.filter((r) => r.decision.state !== "FALLBACK");
  ensure(authorized.size === 0, `accuracy census unexpectedly authorized cells: ${[...authorized].join(",")}`);
  ensure(changesAuthorized.length === 0, "overlay changed legs without authority");
  // Canonical V19-style abstention fallback: copy the incumbent streams byte-for-byte.
  const v25EventBytes = eventBytes, v25LegBytes = legBytes;
  const v25Events = events, v25Legs = legs;
  const diffs = v25Legs.map((leg, i) => ({ leg_identity: leg.leg_identity, v23_sha256: jsonHash(legs[i]), v25_sha256: jsonHash(leg), equal: jsonHash(legs[i]) === jsonHash(leg), overlay_state: overlay[i].decision.state, overlay_reason: overlay[i].decision.reason }));
  ensure(diffs.every((r) => r.equal), "non-authoritative leg changed");
  const closes = new Map(legs.map((l) => [l.ticker, { audited_close_cents: l.audited_close_cents }]));
  const score = scoreVariant("V25_ESTIMATOR_OVERLAY", v25Events, closes), baseline = scoreVariant("V23_OPERATIVE_BASELINE", events, closes);
  ensure(JSON.stringify(score.aggregate) === JSON.stringify(baseline.aggregate), "zero-authority score differs");
  ensure(score.aggregate.joint_objective_pairs === 45 && score.aggregate.strict_carried_pairs === 88, "V23 floor not conserved");
  const v23Frontier = JSON.parse(fs.readFileSync(v23FrontierPath, "utf8")), v23Regret = JSON.parse(fs.readFileSync(v23RegretPath, "utf8"));
  const miss = v25Legs.map((leg) => ({ leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, address: leg.credited ? "CAPTURED_INCUMBENT_V23" : leg.acted ? "DIED_INCUMBENT_ACTED_NOT_CREDITED" : "DIED_INCUMBENT_NO_ACTION", overlay_disposition: "ABSTAIN_NO_AUTHORIZED_CELL_V23_BYTE_IDENTICAL", incumbent_terminal_reason: leg.terminal_reason }));
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "V25_EVENT_LEDGER.jsonl.gz"), v25EventBytes);
  fs.writeFileSync(path.join(out, "V25_LEG_LEDGER.jsonl.gz"), v25LegBytes);
  fs.writeFileSync(path.join(out, "OVERLAY_EVALUATION_LEDGER.jsonl.gz"), gzipRows(overlay));
  fs.writeFileSync(path.join(out, "V23_TO_V25_LEG_DIFFERENTIAL.jsonl.gz"), gzipRows(diffs));
  fs.writeFileSync(path.join(out, "DIFFERENTIAL_RECEIPT.json"), canonical({ V23_event_ledger_sha256: sha256(eventBytes), V25_event_ledger_sha256: sha256(v25EventBytes), event_ledgers_byte_identical: Buffer.compare(eventBytes, v25EventBytes) === 0, V23_leg_ledger_sha256: sha256(legBytes), V25_leg_ledger_sha256: sha256(v25LegBytes), leg_ledgers_byte_identical: Buffer.compare(legBytes, v25LegBytes) === 0, differing_leg_streams: diffs.filter((r) => !r.equal).length, identical_leg_streams: diffs.filter((r) => r.equal).length, authorized_cells: [...authorized], overlay_actions: changesAuthorized.length }));
  fs.writeFileSync(path.join(out, "FRONTIER.json"), canonical({ fixed_denominator: 804, V23: baseline, V25: score, V23_source_frontier_sha256: hashFile(v23FrontierPath), exact_score_identity: true }));
  fs.writeFileSync(path.join(out, "REGRET_GAUGE.json"), canonical({ V23_source_sha256: hashFile(v23RegretPath), V23: v23Regret.V23_PAIR_CAP_IMMEDIATE, V25: v23Regret.V23_PAIR_CAP_IMMEDIATE, exact_regret_identity: true }));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_1608.jsonl.gz"), gzipRows(miss));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_CONSERVATION.json"), canonical({ denominator: 1608, unique_leg_identities: new Set(miss.map((r) => r.leg_identity)).size, addresses: countBy(miss, (r) => r.address), sum: miss.length, conserved: true }));
  fs.writeFileSync(path.join(out, "OVERLAY_AUTHORITY_RECEIPT.json"), canonical({ overlay_law: "NEW_LAYER_IS_OVERLAY_NEVER_GATE; ABSENT_AUTHORITY_RUNS_INCUMBENT_BYTE_IDENTICAL", canonical_template: "V19_ABSTENTION_FALLBACK", accuracy_authority_sha256: hashFile(authorityPath), stated_error_bar: authority.law, authorized_cells: [...authorized], result: "NO_CELL_EARNED_AUTHORITY; V25_EQUALS_V23" }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_only: true, holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, elapsed_time_pair_input: false }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V25 estimator overlay\n\nThe standalone census authorized zero category-by-region cells. Under the overlay law, V25 therefore executes the canonical V19 fallback and is byte-identical to V23 on all 1,608 leg streams. V25 scores exactly 45 JOINT and 88 carried. No placement was blocked, replaced, or released by the estimator.\n`);
  const sources = [eventPath, legPath, authorityPath, accuracyLedgerPath, v24LegPath, v23FrontierPath, v23RegretPath, __filename, path.join(repo, "arb-executor/analysis/window1_landing_estimator_overlay_v25_policy.js"), path.join(repo, "arb-executor/tests/test_window1_landing_estimator_overlay_v25.js")];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sources.map((p) => [path.relative(repo, p).replaceAll("\\", "/"), { sha256: hashFile(p), bytes: fs.statSync(p).size }])) }));
  if (compare1 && compare2) fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(compareBuilds(path.resolve(compare1), path.resolve(compare2))));
  const names = fs.readdirSync(out).filter((n) => n !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((n) => [n, { sha256: hashFile(path.join(out, n)), bytes: fs.statSync(path.join(out, n)).size }])) }));
  process.stdout.write(canonical({ V23: baseline.aggregate, V25: score.aggregate, differential: JSON.parse(fs.readFileSync(path.join(out, "DIFFERENTIAL_RECEIPT.json"), "utf8")), miss: countBy(miss, (r) => r.address) }));
}

if (require.main === module) main();
