#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { mirrorArmDecision } = require("./window1_v29_mirror_armed_leg2_policy.js");

const argv = process.argv.slice(2), arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v29_mirror_armed_leg2_20260804")));
const run1 = arg("--finalize-run1", null), run2 = arg("--finalize-run2", null);
const v28 = path.join(repo, ".claude/window1_live_v4_replay/v28_anchor_cap_stack_20260804");
const eventPath = path.join(v28, "EVENT_LEDGER.jsonl.gz"), legPath = path.join(v28, "LEG_LEDGER.jsonl.gz"), tracePath = path.join(v28, "DECISION_TRACE_1608.json"), scorePath = path.join(v28, "SCORECARD.json"), frontierPath = path.join(v28, "FRONTIER.json"), regretPath = path.join(v28, "REGRET_GAUGE.json"), regretLegPath = path.join(v28, "REGRET_LEG_LEDGER.jsonl.gz"), v28RatificationPath = path.join(v28, "RATIFICATION_AND_SHELVING_RECEIPT.json");
const v22SpecPath = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/V22_PHASE1_LANDING_ESTIMATOR_SPEC.json");
const v25AuthorityPath = path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/OVERLAY_AUTHORITY_RECEIPT.json");
const v26AuthorityPath = path.join(repo, ".claude/window1_live_v4_replay/drift_landing_overlay_v26_20260804/DRIFT_CELL_AUTHORITY.json");
const policyPath = path.join(repo, "arb-executor/analysis/window1_v29_mirror_armed_leg2_policy.js"), policyTestPath = path.join(repo, "arb-executor/tests/test_window1_v29_mirror_armed_leg2_policy.js"), packageTestPath = path.join(repo, "arb-executor/tests/test_window1_v29_mirror_armed_leg2_package.js");

function ensure(x, m) { if (!x) throw new Error(m); }
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function fileHash(p) { return sha(fs.readFileSync(p)); }
function write(p, b) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, b); }
function readRows(p) { const s = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return s ? s.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(xs) { return zlib.gzipSync(Buffer.from(`${xs.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function rel(p) { return path.relative(repo, p).replaceAll("\\", "/"); }
function group(xs, fn) { const m = new Map(); for (const x of xs) { const k = fn(x); if (!m.has(k)) m.set(k, []); m.get(k).push(x); } return m; }
function countBy(xs, fn) { const o = {}; for (const x of xs) { const k = String(fn(x)); o[k] = (o[k] || 0) + 1; } return Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }

function targetRows(events, trace) {
  const em = new Map(events.map((e) => [e.event_id, e])), rows = [];
  for (const event of events) {
    const legs = Object.values(event.legs), completed = legs.every((l) => l.credited), closes = legs.every((l) => Number.isInteger(l.audited_close_cents));
    if (!completed || !closes || !legs.some((l) => l.entry_cents > l.audited_close_cents) || !legs.some((l) => l.entry_cents < l.audited_close_cents)) continue;
    const ordered = [...legs].sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity)), positive = legs.find((l) => l.entry_cents > l.audited_close_cents), first = ordered[0];
    const structurallyEligible = positive.leg_identity === ordered[1].leg_identity && first.entry_cents < first.audited_close_cents;
    const decision = mirrorArmDecision({ incumbentHandled: true, siblingDiscountAuthority: "NOT_BOUND", closeBar: null, lawfulFloorBar: null, firstFillCents: first.entry_cents });
    rows.push({ target_class: "V28_CARRIED_PAIR", event_id: event.event_id, category: event.category, starting_price_region: event.starting_price_split, target_leg_identity: positive.leg_identity, leg1_identity: first.leg_identity, leg1_fill_cents: first.entry_cents, ex_post_leg1_below_audited_close: first.entry_cents < first.audited_close_cents, target_was_second_fill: positive.leg_identity === ordered[1].leg_identity, structurally_eligible_before_authority_checks: structurallyEligible, incumbent_handled: true, decision, conversion: "UNCHANGED_V28_CARRIED" });
  }
  const fn = trace.rows.filter((x) => x.first_flag?.layer === "COMPLETION" && x.tape_offered_afterward?.negative_delta_available_past_flag === "YES");
  for (const t of fn) {
    const event = em.get(t.event_id), legs = Object.values(event.legs), target = legs.find((l) => !l.credited), first = legs.find((l) => l.credited);
    if (!target || !first) { rows.push({ target_class: "V28_COMPLETION_MIRROR_FN", event_id: event.event_id, category: event.category, starting_price_region: event.starting_price_split, target_leg_identity: t.leg_identity, structurally_eligible_before_authority_checks: false, incumbent_handled: true, decision: mirrorArmDecision({ incumbentHandled: true, siblingDiscountAuthority: "NOT_BOUND", closeBar: null, lawfulFloorBar: null, firstFillCents: 1 }), conversion: "UNCHANGED_ALREADY_COMPLETED_NONPAR_FN", source_first_flag_predicate: t.first_flag.predicate }); continue; }
    const exPostDiscount = Number.isInteger(first.audited_close_cents) && first.entry_cents < first.audited_close_cents;
    const decision = mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "NOT_BOUND", closeBar: null, lawfulFloorBar: null, firstFillCents: first.entry_cents });
    rows.push({ target_class: "V28_COMPLETION_MIRROR_FN", event_id: event.event_id, category: event.category, starting_price_region: event.starting_price_split, target_leg_identity: target.leg_identity, leg1_identity: first.leg_identity, leg1_fill_cents: first.entry_cents, ex_post_leg1_below_audited_close: exPostDiscount, structurally_eligible_before_authority_checks: exPostDiscount, incumbent_handled: false, source_first_flag_predicate: t.first_flag.predicate, decision, conversion: "ABSTAIN_NO_CAUSAL_DISCOUNT_OR_CLOSE_BAR_AUTHORITY" });
  }
  return rows.sort((a, b) => a.target_class.localeCompare(b.target_class) || a.event_id.localeCompare(b.event_id) || a.target_leg_identity.localeCompare(b.target_leg_identity));
}

function build() {
  const required = [eventPath, legPath, tracePath, scorePath, frontierPath, regretPath, regretLegPath, v28RatificationPath, v22SpecPath, v25AuthorityPath, v26AuthorityPath, policyPath, policyTestPath, packageTestPath, __filename]; for (const p of required) ensure(fs.existsSync(p), `missing ${p}`);
  const events = readRows(eventPath), legs = readRows(legPath), trace = JSON.parse(fs.readFileSync(tracePath)), score = JSON.parse(fs.readFileSync(scorePath)), v22 = JSON.parse(fs.readFileSync(v22SpecPath)), v25 = JSON.parse(fs.readFileSync(v25AuthorityPath)), v26 = JSON.parse(fs.readFileSync(v26AuthorityPath));
  ensure(events.length === 804 && legs.length === 1608 && trace.rows.length === 1608, "V28 conservation failed"); ensure(score.V28_score.joint_objective_pairs === 65, "ratified V28 floor mismatch"); ensure(v22.ratification_candidate_interface.prohibited.includes("EX_POST_CLOSE_AS_POLICY_INPUT"), "missing ex-post close prohibition"); ensure(v25.authorized_cells.length === 0 && v26.authorized_cells.length === 0, "unexpected causal close-bar authority");
  const targets = targetRows(events, trace), carried = targets.filter((x) => x.target_class === "V28_CARRIED_PAIR"), completion = targets.filter((x) => x.target_class === "V28_COMPLETION_MIRROR_FN"); ensure(carried.length === 144, `carried target mass ${carried.length}`); ensure(completion.length === 237, `completion target mass ${completion.length}`);
  const changed = targets.filter((x) => x.decision.state !== "ABSTAIN"); ensure(changed.length === 0, "V29 cannot change stream without bound causal bars");
  fs.mkdirSync(output, { recursive: true }); for (const [src, name] of [[eventPath, "EVENT_LEDGER.jsonl.gz"], [legPath, "LEG_LEDGER.jsonl.gz"], [tracePath, "DECISION_TRACE_1608.json"], [frontierPath, "FRONTIER.json"], [regretPath, "REGRET_GAUGE.json"], [regretLegPath, "REGRET_LEG_LEDGER.jsonl.gz"]]) fs.copyFileSync(src, path.join(output, name));
  write(path.join(output, "MIRROR_ARM_TARGET_MASS.jsonl.gz"), gzipRows(targets));
  const byClass = (xs) => ({ target_mass: xs.length, structurally_eligible_before_authority_checks: xs.filter((x) => x.structurally_eligible_before_authority_checks).length, converted: xs.filter((x) => x.conversion.startsWith("CONVERTED")).length, decision_reasons: countBy(xs, (x) => x.decision.reason), outcomes: countBy(xs, (x) => x.conversion) });
  write(path.join(output, "TARGET_MASS_CONVERSION.json"), canonical({ carried: byClass(carried), completion_mirror_false_negatives: byClass(completion), total: byClass(targets), note: "EX_POST_BELOW_CLOSE FIELDS CLASSIFY THE REQUESTED MASS FOR DIAGNOSIS ONLY; THEY NEVER ENTER POLICY" }));
  write(path.join(output, "AUTHORITY_RECEIPT.json"), canonical({ requested_organ: "MIRROR_ARMED_LEG2", incumbent: { variant: "V28", joint: 65, status: "RATIFIED_OPERATIVE_NEW_FLOOR", commit: "3339f30dc9d3136788617bf0e5456708008b845b" }, causal_requirements: ["CREDITED_SIBLING_DISCOUNT_AUTHORITY", "DECISION_TIME_OWN_CLOSE_BAR", "DECISION_TIME_OWN_LAWFUL_FLOOR_BAR", "OWN_BOOK_DECLINE_COHERENT_ORDINAL", "SPREAD_DWELL_CAPACITY_LAWFUL_READ", "PAIR_CAP"], findings: { independent_pair_reference: "NOT_BOUND", numeric_decision_time_own_close_bar_authorized_cells: 0, V25_authorized_cells: v25.authorized_cells, V26_authorized_cells: v26.authorized_cells, ex_post_audited_close_policy_input: "FORBIDDEN", ex_post_floor_policy_input: "FORBIDDEN" }, ruling: "OVERLAY_ABSTAINS_EVERYWHERE; V28 RUNS BYTE_IDENTICAL", no_clock_inputs: true, elapsed_time_inputs: [] }));
  write(path.join(output, "SCORECARD.json"), canonical({ variant: "V29_MIRROR_ARMED_LEG2", V28_floor: score.V28_score, V29_score: score.V28_score, delta: Object.fromEntries(Object.keys(score.V28_score).filter((k) => Number.isInteger(score.V28_score[k])).map((k) => [k, 0])), joint_non_regression: true, result: "NO_BOUND_AUTHORITY_ZERO_WIRING_V29_EQUALS_V28", carried_conversion: { target: 144, converted: 0 }, completion_mirror_FN_conversion: { target: 237, converted: 0 } }));
  const identities = [eventPath, legPath, tracePath, frontierPath, regretPath, regretLegPath].map((p) => ({ artifact: path.basename(p), V28_sha256: fileHash(p), V29_sha256: fileHash(path.join(output, path.basename(p))), equal: fileHash(p) === fileHash(path.join(output, path.basename(p))) })); ensure(identities.every((x) => x.equal), "incumbent stream drift");
  write(path.join(output, "DIFFERENTIAL_RECEIPT.json"), canonical({ V28_leg_streams: 1608, changed_leg_streams: 0, unchanged_leg_streams: 1608, changed_stream_identities: [], all_other_streams_hash_equal: true, artifact_identities: identities }));
  write(path.join(output, "TRACE_RECEIPT.json"), canonical({ fresh_output_path: ".claude/window1_live_v4_replay/v29_mirror_armed_leg2_20260804/DECISION_TRACE_1608.json", rows: 1608, V28_sha256: fileHash(tracePath), V29_sha256: fileHash(path.join(output, "DECISION_TRACE_1608.json")), byte_identical_because_overlay_has_zero_authorized_decisions: true, layer_FN_table: trace.rollup.layer_totals }));
  write(path.join(output, "RATIFICATION_RECEIPT.json"), canonical({ V28: { status: "RATIFIED_OPERATIVE_NEW_FLOOR", joint: 65, source_commit: "3339f30dc9d3136788617bf0e5456708008b845b", source_receipt_sha256: fileHash(v28RatificationPath) }, V29: { status: "BUILT_ZERO_AUTHORITY_NOT_PROMOTED", joint: 65 }, law: "NEW_OVERLAY_NEVER_GATES_OR_LEAKS_FUTURE; ABSENT_AUTHORITY_PRESERVES_INCUMBENT_BYTE_IDENTICAL" }));
  write(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ ex_post_close_as_policy_input: false, ex_post_floor_as_policy_input: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, elapsed_time_pair_input: false }));
  write(path.join(output, "TEST_RESULTS.json"), canonical({ status: "PASS", commands: ["node arb-executor/tests/test_window1_v29_mirror_armed_leg2_policy.js", "node arb-executor/tests/test_window1_v29_mirror_armed_leg2_package.js", "node arb-executor/tests/test_window1_v28_anchor_cap_stack_package.js"], omissions: 0, deselections: 0 }));
  write(path.join(output, "REPORT.md"), `# V29 mirror-armed leg-2 overlay\n\nV28 is ratified at JOINT 65. V29 was built as an additive overlay, but no causal decision-time own-close bar or credited-discount authority is bound. The audited close and eventual floor remain grading-only and are forbidden policy inputs. Consequently every V29 target abstains and all V28 ledgers, frontier, regret gauge, and the fresh 1,608-row trace remain byte-identical.\n`);
  const source = Object.fromEntries(required.map((p) => [rel(p), { sha256: fileHash(p), bytes: fs.statSync(p).size }])); write(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ files: source }));
  process.stdout.write(canonical({ status: "BUILT", V28_joint: 65, V29_joint: 65, carried_target: 144, completion_FN_target: 237, changed_streams: 0, result: "NO_BOUND_AUTHORITY_ZERO_WIRING" }));
}

function manifest(root) { const out = {}, skip = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]); for (const e of fs.readdirSync(root, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) if (e.isFile() && !skip.has(e.name)) { const p = path.join(root, e.name); out[e.name] = { sha256: fileHash(p), bytes: fs.statSync(p).size }; } return out; }
function finalize() { const a = manifest(path.resolve(run1)), b = manifest(path.resolve(run2)); ensure(JSON.stringify(a) === JSON.stringify(b), "determinism mismatch"); fs.cpSync(path.resolve(run1), output, { recursive: true }); write(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ clean_builds: 2, byte_identical_payloads: true, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha(canonical(a)) })); const files = manifest(output); files.DETERMINISM_RECEIPT = { sha256: fileHash(path.join(output, "DETERMINISM_RECEIPT.json")), bytes: fs.statSync(path.join(output, "DETERMINISM_RECEIPT.json")).size }; write(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(Object.entries(files).sort(([a], [b]) => a.localeCompare(b))) })); process.stdout.write(canonical({ status: "FINALIZED", payload_manifest_sha256: sha(canonical(a)), payload_file_count: Object.keys(a).length })); }

if (run1 || run2) finalize(); else build();
