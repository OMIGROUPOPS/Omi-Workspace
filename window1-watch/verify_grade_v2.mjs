// Verify a regrade against an explicit before-commit; never rerun the engine.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url)), repo = path.dirname(here);
const before = process.argv[2];
if (!before || !/^[a-f0-9]{8,40}$/i.test(before)) throw new Error("Supply the pre-regrade commit");
const gitBytes = (file) => execFileSync("git", ["show", `${before}:${file}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 });
const old = (file) => JSON.parse(gitBytes(file));
const current = (file) => JSON.parse(fs.readFileSync(path.join(repo, file)));
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const unchanged = (file) => assert.equal(sha(fs.readFileSync(path.join(repo, file))), sha(gitBytes(file)), file);
const indexPath = "window1-watch/data/grades/index.json", history = current(indexPath), priorHistory = old(indexPath);
const games = current("window1-watch/data/index.json").games;
const summarize = (g) => ({
  letter: g.LETTER.letter, governing: g.LETTER.governing_section,
  section_letters: Object.fromEntries(Object.entries(g.LETTER.section_grades).map(([k, v]) => [k, v.letter])),
  card: g.display.sections.map((s) => `${s.name}: ${s.line}`),
  micro: g.MICRO.legs, micro_mode_grades: g.MICRO.mode_grades ?? null,
  fills: g.OUTCOME.legs, captured_cents: g.OUTCOME.captured_cents,
  offered_cents: g.OUTCOME.best_capturable_cents, capture_ratio: g.OUTCOME.capture_ratio,
  ages: g.HANDS.rest_age_at_fill_minutes,
  ruler: g.RULER_COLUMNS?.effective_truth ?? null,
  grade_provenance: g.provenance,
});
const report = { before_commit: before, scope: "Face grading only; existing trace/face/OS/rubric unchanged", games: [] };
unchanged("arb-executor/analysis/window1_v54_dual_belief_os.js");
unchanged("arb-executor/analysis/window1_v54_functionable_os.js");
unchanged("arb-executor/analysis/build_window1_v54_dual_belief.js");
unchanged("window1-watch/grade_rubric.json");
for (const { event } of games) {
  const prefix = `window1-watch/data/${event}`, a = old(prefix + ".grade.json"), b = current(prefix + ".grade.json");
  unchanged(prefix + ".face.json");
  unchanged(prefix + ".face.json.gz");
  for (const key of ["os_sha256", "trace_sha256", "bench_sha256", "stage_inputs_sha256", "stage_files_count", "rubric_sha256", "face_sha256"])
    assert.equal(a.provenance[key], b.provenance[key], `${event}:${key}`);
  assert.deepEqual(a.SENTENCE.author_counts, b.SENTENCE.author_counts);
  assert.equal(b.SENTENCE.gate_1_authorship_certification, "STORE SILENT");
  assert.match(b.display.sections[0].line, /authored \(token metric\)/);
  for (const leg of Object.keys(b.MICRO.legs)) {
    const eligible = b.MICRO.receipt_calls.filter((r) => r.leg === leg && r.eligible);
    assert.equal(b.MICRO.legs[leg].first_eligible_full_span.receipt, eligible[0]?.receipt);
    assert.equal(eligible.length, b.MICRO.legs[leg].remaining_path.receipts_eligible);
    for (const r of eligible) {
      const target = r.targets.executable_future_print;
      if (target.status === "OK") {
        assert.ok(target.floor_epoch > r.epoch);
        assert.ok(target.floor_epoch < Math.min(b.RULER_COLUMNS.effective_truth.span_end_epoch, b.RULER_COLUMNS.effective_truth.bell_epoch));
      }
      if (r.targets.remaining_path.kind === "CARRIED_GATE_STATE_NOT_A_FUTURE_PRINT")
        assert.equal(r.targets.remaining_path.floor_epoch, r.epoch);
    }
  }
  for (const leg of Object.values(b.OUTCOME.legs)) if (leg.filled) {
    const r = leg.revalidation;
    assert.equal(leg.valid_span_fill, r.at_or_after_span_start && r.before_span_end && r.before_bell);
  }
  const entries = history.grades.filter((g) => g.event === event);
  assert.equal(entries.length, priorHistory.grades.filter((g) => g.event === event).length + 1);
  for (const url of new Set(entries.map((g) => g.url))) {
    const file = "window1-watch" + url, bucket = current(file);
    let previous;
    try { previous = old(file); } catch { continue; }
    assert.deepEqual(bucket.grades.slice(0, previous.grades.length), previous.grades);
  }
  report.games.push({ event, before: summarize(a), after: summarize(b),
    preserved_history_snapshots: entries.length - 1,
    checks: "PASS — source bindings, immutable history prefix, first eligible, future target boundaries, all-fill revalidation" });
  console.log(`${event} · ${a.LETTER.letter} -> ${b.LETTER.letter}`);
  console.log("BEFORE\n" + report.games.at(-1).before.card.join("\n"));
  console.log("AFTER\n" + report.games.at(-1).after.card.join("\n"));
  console.log("AGES " + JSON.stringify(b.HANDS.rest_age_at_fill_minutes));
}
assert.equal(history.grades.length, priorHistory.grades.length + games.length);
report.status = "PASS";
const file = path.join(here, "proof", "grade-v2-before-after.json");
fs.writeFileSync(file, JSON.stringify(report, null, 2) + "\n");
console.log(file);
