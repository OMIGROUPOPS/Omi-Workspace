#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repo = path.resolve(process.argv[2] || ".");
const implementationCommit = process.argv[3] || execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim();
const out = path.join(repo, ".claude/window1_v53_03_preregistration_20260820/PRE_REGISTRATION.json");
const sha = (value) => crypto.createHash("sha256").update(value).digest("hex");
const show = (commit, file) => execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 });
const parseShow = (commit, file) => JSON.parse(show(commit, file).toString("utf8"));

const truthCommit = "c0056976c446afcb4d9603796a2e06c068ee94d6";
const truthPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const censusCommit = "1d5564b5cdd25de32cfa9244cf21486245ab5b55";
const censusPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/QUEUE_FORMATION_REFLEX_CENSUS.json";
const priorCommit = "e79c1feef76d7dfd7ec2737b3663670ddce0d342";
const priorPath = ".claude/window1_live_v4_replay/v52r_assembled_policy_20260818/COHORT_SELECTION_RECEIPT.json";
const v53Receipts = [
  { iteration: "V53_01", commit: "7ba7c3dd23eb9b87d4584f856d4a247d760a03b4", path: ".claude/window1_v53_preregistration_20260819/PRE_REGISTRATION.json" },
  { iteration: "V53_02", commit: "9dca2006fc9865d9989e03d2633e12f7c0f584af", path: ".claude/window1_v53_02_preregistration_20260820/PRE_REGISTRATION.json" },
];
const truthBytes = show(truthCommit, truthPath);
const censusBytes = show(censusCommit, censusPath);
const priorBytes = show(priorCommit, priorPath);
const truth = JSON.parse(truthBytes), census = JSON.parse(censusBytes), prior = JSON.parse(priorBytes);
if (truth.rows?.length !== 804 || census.rows?.length !== 1143 || prior.fresh_25?.length !== 25) throw new Error("V53-03 pre-registration authority census invalid");

const truthByCode = new Map(truth.rows.map((row) => [row.code, row]));
const excluded = new Set(prior.fresh_25.map((row) => row.code));
for (const receipt of prior.excluded_prior_fresh_cohorts) {
  const parsed = parseShow(receipt.commit, receipt.path);
  for (const row of parsed.fresh_25) excluded.add(row.code);
}
const v53Authorities = [];
for (const receipt of v53Receipts) {
  const bytes = show(receipt.commit, receipt.path);
  const parsed = JSON.parse(bytes);
  if (parsed.population?.fresh_25?.length !== 25) throw new Error(`${receipt.iteration} fresh cohort invalid`);
  for (const row of parsed.population.fresh_25) excluded.add(row.code);
  v53Authorities.push({ ...receipt, sha256: sha(bytes), fresh_events_added_to_exclusion_union: 25 });
}
const pinCodes = ["26JUL16MERDRO", "26JUL12POLKUH", "26JUL19ARSMAR", "26JUL13SANDAN", "26JUL14PUTJEA"].sort();
for (const code of pinCodes) if (!truthByCode.has(code)) throw new Error(`standing pin absent ${code}`);
const pins = pinCodes.map((code) => ({ code, event_id: truthByCode.get(code).event_id, category: truthByCode.get(code).category, role: "STANDING_PIN_FILED_IN_V52L_LINEAGE" }));

const rowsByCode = new Map();
for (const row of census.rows) {
  if (!rowsByCode.has(row.code)) rowsByCode.set(row.code, []);
  rowsByCode.get(row.code).push(row);
}
const seedMaterial = `V53_03_FRESH25|${implementationCommit}`;
const seedSha256 = sha(seedMaterial);
const rank = (value) => sha(`${seedSha256}|${value}`);
const strata = new Map();
for (const [code, rows] of rowsByCode) {
  if (pinCodes.includes(code) || excluded.has(code) || !truthByCode.has(code)) continue;
  const category = truthByCode.get(code).category;
  const stamps = rows.slice().sort((a, b) => a.leg.localeCompare(b.leg)).map((row) => `${row.queue}|${row.formation}|${row.reflex}`);
  const stratum = `${category}|${stamps.join("+")}`;
  if (!strata.has(stratum)) strata.set(stratum, []);
  strata.get(stratum).push({ code, event_id: truthByCode.get(code).event_id, category, census_stamps: stamps, stratum, role: "FRESH_STRATIFIED_COHORT_NOT_IN_V52B_THROUGH_V53_02" });
}
const ordered = [...strata].sort(([a], [b]) => rank(a).localeCompare(rank(b)) || a.localeCompare(b));
for (const [stratum, rows] of ordered) rows.sort((a, b) => rank(`${stratum}|${a.code}`).localeCompare(rank(`${stratum}|${b.code}`)) || a.code.localeCompare(b.code));
const fresh = [];
for (let round = 0; fresh.length < 25; round += 1) {
  let added = 0;
  for (const [, rows] of ordered) if (rows[round] && fresh.length < 25) { fresh.push(rows[round]); added += 1; }
  if (!added) throw new Error(`fresh cohort exhausted at ${fresh.length}`);
}
if (fresh.some((row) => excluded.has(row.code))) throw new Error("prior cohort overlap");
const combined = [...pins, ...fresh];
if (combined.length !== 30 || new Set(combined.map((row) => row.event_id)).size !== 30) throw new Error("5+25 conservation failed");

const receipt = {
  label: "V53_03_STAGE1_PRE_REGISTRATION",
  created_before_grading: true,
  implementation_commit: implementationCommit,
  pins_smoke_pass_required_before_creation: true,
  seed_derivation_law: "SHA256('V53_03_FRESH25|' + V53_03_IMPLEMENTATION_COMMIT)",
  seed_material: seedMaterial,
  seed_sha256: seedSha256,
  authorities: {
    truth_table: { commit: truthCommit, path: truthPath, sha256: sha(truthBytes) },
    reflex_census: { commit: censusCommit, path: censusPath, sha256: sha(censusBytes) },
    prior_cohort_union: { commit: priorCommit, path: priorPath, sha256: sha(priorBytes), iterations: "V52B_THROUGH_V52R" },
    V53_pre_registrations: v53Authorities,
  },
  standing_pins_filed: true,
  zero_overlap_with_prior_iterations: true,
  excluded_prior_fresh_event_count: excluded.size,
  population: { standing_pins: pins, fresh_25: fresh, combined_30: combined },
  event_list_sha256: sha(`${combined.map((row) => row.event_id).sort().join("\n")}\n`),
  stratification: { dimensions: ["category", "paired_queue_formation_reflex_census_stamps"], strata_available: strata.size, method: "HASH_ORDER_STRATA_THEN_ROUND_ROBIN" },
  pre_registered_bar: {
    comparator: "V52L_ON_IDENTICAL_30",
    V53_completes_strictly_more_than_V52l: true,
    every_V52l_complete_held_by_identity: true,
    average_locked_delta_cents_at_least_V52l: true,
    zero_build_assertion_violations: true,
    failure_disposition: "STOP_BANK_CAUSE_NO_FULL_804"
  }
};
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, `${JSON.stringify(receipt, null, 2)}\n`);
process.stdout.write(`${out}\n${receipt.event_list_sha256}\n`);
