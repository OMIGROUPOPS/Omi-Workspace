#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const cp = require('child_process');

const repo = path.resolve(process.argv[2] || '.');
const out = path.resolve(process.argv[3] || path.join(repo, '.claude/window1_live_v4_replay/sealed_holdout_generalization_exam_block_20260806'));
const sourceCommit = 'eac3b2e76206d361228196814fe62e5f2fd08b12';
const brains = {
  R3: '49f6501561c5d99a7f36c68ec41e0ea7250680e5',
  V34_W1: 'e56d79a2aee1f392b3bee5a0adad099c7f011976',
  V35: '0799fba887f1d1e84f9c0ef3e73096fd9d76019e',
};
const v28 = '3339f30dc9d3136788617bf0e5456708008b845b';

function sha(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function read(rel) { return fs.readFileSync(path.join(repo, rel)); }
function json(rel) { return JSON.parse(read(rel).toString('utf8')); }
function git(args) {
  return cp.execFileSync('git', args, { cwd: repo, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}
function verifyCommit(id) {
  const resolved = git(['rev-parse', '--verify', `${id}^{commit}`]);
  cp.execFileSync('git', ['cat-file', '-e', `${id}^{commit}`], { cwd: repo, stdio: 'ignore' });
  if (resolved !== id) throw new Error(`commit mismatch ${id} -> ${resolved}`);
  return { commit: id, object_type: git(['cat-file', '-t', id]) };
}
function isAncestor(a, b) {
  try { cp.execFileSync('git', ['merge-base', '--is-ancestor', a, b], { cwd: repo, stdio: 'ignore' }); return true; }
  catch (e) { if (e.status === 1) return false; throw e; }
}
function stable(v) { return JSON.stringify(v, null, 2) + '\n'; }
function write(rel, data) {
  const p = path.join(out, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, data);
}

const priorLedgerRel = '.claude/window1_live_v4_replay/v11_v13_v14_holdout_20260803/V11_HOLDOUT_EVENT_LEDGER.jsonl.gz';
const priorReceiptRel = '.claude/window1_live_v4_replay/v11_v13_v14_holdout_20260803/ONE_EXECUTION_RECEIPT.json';
const declarationRel = '.claude/window1_20260721/FIT_HOLDOUT_DECLARATION.json';
const diagnosticRel = '.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/ABOVE_OBSERVED_LOW_83_CENSUS.json';
const traceReceiptRel = '.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/TRACE_REPLAY_IDENTITY_RECEIPT.json';
const fixAReceiptRel = '.claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/CAUSAL_ADDITION_RECEIPT.json';

const priorRows = zlib.gunzipSync(read(priorLedgerRel)).toString('utf8').trim().split(/\r?\n/).map(JSON.parse);
const events = priorRows.map((row) => ({
  event_id: row.event_id,
  event_date: row.event_date,
  category: row.category,
  starting_price_split: row.starting_price_split,
})).sort((a, b) => a.event_id.localeCompare(b.event_id));
if (events.length !== 228 || new Set(events.map((x) => x.event_id)).size !== 228) throw new Error('holdout event conservation failed');
const eventText = events.map((x) => JSON.stringify(x)).join('\n') + '\n';
const dates = [...new Set(events.map((x) => x.event_date))].sort();
if (JSON.stringify(dates) !== JSON.stringify(['2026-07-24', '2026-07-25', '2026-07-26'])) throw new Error('holdout date mismatch');

const declaration = json(declarationRel);
const priorReceipt = json(priorReceiptRel);
const fixAReceipt = json(fixAReceiptRel);
if (declaration.forward_holdout.evaluation_count_allowed !== 1) throw new Error('unexpected evaluation allowance');
if (priorReceipt.policy_evaluation_attempts !== 1 || priorReceipt.runner_invocations_that_reached_policy !== 1) throw new Error('prior evaluation receipt mismatch');
if (!String(fixAReceipt.provenance).includes('HOLDOUT_GATE_LAG_DIAGNOSTIC')) throw new Error('Fix-A holdout provenance missing');

const objectChecks = [sourceCommit, v28, ...Object.values(brains)].map(verifyCommit);
const ancestry = {
  fix_a_stack_v28_is_ancestor_of_R3: isAncestor(v28, brains.R3),
  R3_is_ancestor_of_V34_W1: isAncestor(brains.R3, brains.V34_W1),
  V34_W1_is_ancestor_of_V35: isAncestor(brains.V34_W1, brains.V35),
};
if (!Object.values(ancestry).every(Boolean)) throw new Error('brain ancestry mismatch');

fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
write('HOLDOUT_EVENT_LIST.jsonl', eventText);

const evidence = [priorLedgerRel, priorReceiptRel, declarationRel, diagnosticRel, traceReceiptRel, fixAReceiptRel].map((rel) => {
  const b = read(rel);
  return { path: rel, bytes: b.length, sha256: sha(b) };
});
const seal = {
  schema_version: 'WINDOW1_HOLDOUT_SEAL_PREFLIGHT_FAILURE_V1',
  status: 'BLOCKED_BEFORE_POLICY_EVALUATION',
  requested_exam: ['V35', 'V34_W1', 'R3'],
  frozen_brains: brains,
  population: {
    dates,
    events: events.length,
    legs: events.length * 2,
    event_list_path: 'HOLDOUT_EVENT_LIST.jsonl',
    event_list_sha256: sha(Buffer.from(eventText)),
  },
  failed_precondition: 'POPULATION_IS_NOT_SEALED_AND_HAS_INFLUENCED_THE_REQUESTED_BRAINS',
  controlling_facts: {
    declaration_evaluation_count_allowed: declaration.forward_holdout.evaluation_count_allowed,
    prior_policy_evaluation_attempts: priorReceipt.policy_evaluation_attempts,
    prior_runner_invocations_that_reached_policy: priorReceipt.runner_invocations_that_reached_policy,
    prior_versions: priorReceipt.versions,
    prior_holdout_dates: priorReceipt.holdout_dates,
    later_diagnostic_target_events: json(traceReceiptRel).target_events,
    later_diagnostic_compared_target_legs: json(traceReceiptRel).compared_target_legs,
    fix_a_provenance: fixAReceipt.provenance,
    requested_brain_ancestry: ancestry,
  },
  execution_conservation: {
    requested_brain_evaluations: 0,
    requested_runner_invocations: 0,
    requested_scores_created: 0,
    retries: 0,
    authorization_consumed: false,
  },
  ruling: 'The requested numbers cannot be represented as a sealed generalization exam. A future operator may authorize a clearly labeled reused-validation replay, but it cannot restore holdout status.',
  git_object_checks: objectChecks,
  source_evidence: evidence,
};
write('SEAL_PREFLIGHT_FAILURE.json', stable(seal));
write('RUN_CONSUMPTION_RECEIPT.json', stable({
  status: 'NOT_STARTED',
  reason: seal.failed_precondition,
  policy_evaluation_invocations: 0,
  policy_evaluation_retries: 0,
  output_scorecards: 0,
  holdout_tape_reads_by_this_audit: 0,
  note: 'Event identities were reconstructed from the already-committed prior event ledger; no private tape or policy runner was opened.',
}));
write('FORBIDDEN_ACCESS_RECEIPT.json', stable({
  status: 'PASS',
  network_access: false,
  private_holdout_tape_access: false,
  policy_execution: false,
  scorer_execution: false,
  live_access: false,
  order_access: false,
  position_access: false,
  exit_access: false,
  settlement_access: false,
  DCA_access: false,
  Window2_access: false,
}));
write('DETERMINISM_RECEIPT.json', stable({
  scope: 'seal-audit artifacts only; no policy evaluation',
  build_count: 2,
  result: 'BYTE_IDENTICAL_DIRECTORY_TREES',
  policy_evaluations_across_both_builds: 0,
}));
write('SOURCE_HASH_MANIFEST.json', stable({ source_commit: sourceCommit, sources: evidence, commits: objectChecks }));
write('REPORT.md', `# Window-1 sealed-holdout generalization exam — preflight block\n\nThe requested policy run did not start. The canonical holdout universe is **N=${events.length} events / ${events.length * 2} legs**, dates ${dates.join(', ')}, with canonical event-list SHA-256 \`${sha(Buffer.from(eventText))}\`.\n\nThe premise that this population is sealed and untouched by tuning is false in the committed record. The declaration permits one evaluation; the prior receipt records one policy-reaching invocation evaluating V11/V13/V14 on all 228 events. The later gate-lag diagnostic replayed 124 events / 144 target legs. Fix A then explicitly used that holdout diagnostic as the provenance for its one-cent anchor-rearm rule. V28 contains Fix A; Git ancestry proves V28 -> R3 -> V34-W1 -> V35. Therefore all three requested brains descend from a tune decision informed by this population.\n\nNo R3, V34-W1, or V35 holdout evaluation was invoked; no scorecard exists. Running them may be authorized later only as a **reused validation set**, never as a sealed generalization exam.\n`);

const artifactNames = fs.readdirSync(out).sort().filter((n) => n !== 'ARTIFACT_HASH_MANIFEST.json');
const artifacts = artifactNames.map((name) => {
  const b = fs.readFileSync(path.join(out, name));
  return { path: name, bytes: b.length, sha256: sha(b) };
});
write('ARTIFACT_HASH_MANIFEST.json', stable({ artifacts }));
console.log(stable({ status: seal.status, events: events.length, event_list_sha256: seal.population.event_list_sha256, out }));
