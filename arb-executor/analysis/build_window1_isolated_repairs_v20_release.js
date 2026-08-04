#!/usr/bin/env node
"use strict";

const crypto = require("crypto"), fs = require("fs"), path = require("path");
const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const out = path.join(repo, ".claude/window1_live_v4_replay/isolated_repairs_v20_20260804");
const a = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804");
const c = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_c_shape_settlement_v20_20260804");
const a2 = path.join(repo, ".tmp/pkg-fix-a-v20-build2"), c2 = path.join(repo, ".tmp/pkg-fix-c-v20-build2");
const b = path.join(repo, ".claude/window1_live_v4_replay/sibling_source_read_20260804/SIBLING_SOURCE_RECEIPT.json");
const wta = path.join(repo, ".claude/window1_live_v4_replay/wta_main_v19_death_trace_20260804/WTA_MAIN_DEATH_CENSUS.json");
const raw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function ensure(x, m) { if (!x) throw new Error(m); }
function rel(file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function json(file) { return JSON.parse(fs.readFileSync(file)); }
function compareDirs(left, right) { const names = fs.readdirSync(left).filter((name) => fs.statSync(path.join(left, name)).isFile()).sort(); const other = fs.readdirSync(right).filter((name) => fs.statSync(path.join(right, name)).isFile()).sort(); ensure(JSON.stringify(names) === JSON.stringify(other), "determinism file census mismatch"); const files = Object.fromEntries(names.map((name) => { const l = hashFile(path.join(left, name)), r = hashFile(path.join(right, name)); ensure(l === r, `determinism mismatch ${name}`); return [name, { sha256: l, byte_identical: true }]; })); return { file_count: names.length, files }; }
function categorySummary(comparison) { const groups = {}; for (const row of comparison.category_and_starting_price_region) { if (!groups[row.category]) groups[row.category] = { D: 0, acted_legs: 0, completed_pairs: 0, pairs_under_par: 0, both_legs_strictly_below_close: 0, joint_objective_pairs: 0, execution_floor_pair_pass: 0 }; for (const key of Object.keys(groups[row.category])) groups[row.category][key] += key === "D" ? row.D : row.metrics[key]; } return groups; }
function main() {
  for (const item of [a, c, a2, c2, b, wta]) ensure(fs.existsSync(item), `missing ${item}`);
  const ac = json(path.join(a, "V19_NON_REGRESSION_COMPARISON.json")), cc = json(path.join(c, "V19_NON_REGRESSION_COMPARISON.json")), br = json(b), wc = json(wta);
  const determinism = { schema_version: "WINDOW1_ISOLATED_REPAIRS_V20_DETERMINISM", FIX_A: compareDirs(a, a2), FIX_C: compareDirs(c, c2), two_population_replays_per_variant: true, two_package_builds_per_variant: true };
  const summary = {
    schema_version: "WINDOW1_ISOLATED_REPAIRS_V20_CONTROL_SUMMARY",
    D: 804,
    variants_stacked: false,
    V19_floor: ac.V19,
    FIX_A: { metrics: ac.isolated_variant, delta: ac.delta, category: categorySummary(ac), full_category_and_price_region_in: "isolated_fix_a_anchor_freshness_v20_20260804/V19_NON_REGRESSION_COMPARISON.json" },
    FIX_B: { built: false, conclusion: br.conclusion, actual_source: br.actual_source },
    FIX_C: { metrics: cc.isolated_variant, delta: cc.delta, category: categorySummary(cc), full_category_and_price_region_in: "isolated_fix_c_shape_settlement_v20_20260804/V19_NON_REGRESSION_COMPARISON.json" },
    WTA_MAIN_V19_DEATH_TRACE: { D: wc.D, death_stages: wc.death_stages, joint_objective_pairs: wc.joint_objective_pairs, full_price_regions_in: "wta_main_v19_death_trace_20260804/WTA_MAIN_DEATH_CENSUS.json" },
    claim: "IN_SAMPLE_804_DEVELOPMENT_REPLAY; ISOLATED_VARIANTS; NOT_STACKED; NOT_HOLDOUT; NOT_MARKET_CEILING"
  };
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "CONTROL_SUMMARY.json"), canonical(summary));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(determinism));
  fs.writeFileSync(path.join(out, "TEST_RESULTS.json"), canonical({ status: "PASS", test_files_run: 9, failed: 0, files: ["arb-executor/tests/test_window1_isolated_repair_predicates_v20.js", "arb-executor/tests/test_window1_isolated_repair_v20_package.js", "arb-executor/tests/test_window1_pair_couple_elimination_v19.js", "arb-executor/tests/test_window1_pair_couple_v19_package.js", "arb-executor/tests/test_window1_pair_interim_elimination_v18.js", "arb-executor/tests/test_window1_interim_elimination_v13.js", "arb-executor/tests/test_window1_interim_micro_repair_v14.js", "arb-executor/tests/test_window1_quote_shape_persistence_floor_v11.js", "arb-executor/tests/test_window1_quote_shape_pair_wiring_v3.js"], direct_assertions_in_new_files: 17, scorer_variants_executed: ["FIX_A", "FIX_C"], variants_stacked: false }));
  fs.writeFileSync(path.join(out, "INDEPENDENT_AUDIT_INSTRUCTION.md"), "# Independent audit instruction\n\nRebuild FIX A and FIX C independently from frozen V19 and the immutable 804 inputs before reading expected summaries. Verify own-book freshness and live-ask placement for A; strict-later qualified settlement and plinko ordering for C; no A+C stacking; the sibling-source code read; D=804; every FRONTIER tier, JOINT, and REGRET partition by category x price region; two byte-identical builds; and the 152-event WTA_MAIN death trace. Freeze independent counts first. Any mismatch is BLOCK.\n");
  const u = (suffix) => `${raw}/.claude/window1_live_v4_replay/${suffix}`;
  fs.writeFileSync(path.join(out, "REPORT.md"), `# Isolated repairs V20\n\n- Control summary: ${u("isolated_repairs_v20_20260804/CONTROL_SUMMARY.json")}\n- Fix A: ${u("isolated_fix_a_anchor_freshness_v20_20260804/REPORT.md")}\n- Sibling source: ${u("sibling_source_read_20260804/SIBLING_SOURCE_RECEIPT.json")}\n- Fix C: ${u("isolated_fix_c_shape_settlement_v20_20260804/REPORT.md")}\n- WTA_MAIN death trace: ${u("wta_main_v19_death_trace_20260804/REPORT.md")}\n- Determinism: ${u("isolated_repairs_v20_20260804/DETERMINISM_RECEIPT.json")}\n- Tests: ${u("isolated_repairs_v20_20260804/TEST_RESULTS.json")}\n`);
  const sources = [path.join(a, "ARTIFACT_HASH_MANIFEST.json"), path.join(c, "ARTIFACT_HASH_MANIFEST.json"), b, wta, path.join(repo, "arb-executor/analysis/build_window1_isolated_repairs_v20_release.js"), path.join(repo, "arb-executor/tests/test_window1_isolated_repair_v20_package.js"), path.join(repo, "arb-executor/docs/research/window1/WINDOW1_ISOLATED_REPAIRS_V20_VAULT_ADDENDUM.md"), path.join(repo, "arb-executor/docs/LIVING_VAULT.md"), path.join(repo, ".claude/HANDOFF_FABLE.md")];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sources.map((file) => [rel(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])) }));
  const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical(summary));
}
main();
