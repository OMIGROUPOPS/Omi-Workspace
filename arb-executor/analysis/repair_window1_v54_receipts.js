"use strict";

// Receipt-only repair. Never executes a policy, opens a game tape, or mutates the
// untracked V54 trace. It binds existing committed prose and existing trace bytes.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { execFileSync } = require("child_process");

const repo = path.resolve(process.argv[2] || path.join(__dirname, "..", ".."));
const rel = (file) => path.relative(repo, file).replaceAll("\\", "/");
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const ensure = (condition, message) => { if (!condition) throw new Error(message); };
const git = (args, options = {}) => execFileSync("git", args, { cwd: repo, encoding: options.encoding ?? "utf8", maxBuffer: options.maxBuffer ?? 64 * 1024 * 1024 });
const gitBytes = (commit, file) => git(["show", `${commit}:${file}`], { encoding: "buffer", maxBuffer: 64 * 1024 * 1024 });
const stat = (file) => ({ path: rel(file), sha256: sha(fs.readFileSync(file)), bytes: fs.statSync(file).size });
const lines = (bytes) => bytes.toString("utf8").replace(/\r\n/g, "\n").split("\n");
const writeJson = (file, value) => fs.writeFileSync(file, canonical(value), "utf8");

const law = {
  read_at: "a2c8d842",
  path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md",
  sha256: "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934",
  laws: ["L8", "L18", "L20", "L22"],
};

const storyRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_functionable_four_stories_v6_20260821");
const explainedRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_four_games_explained_20260821");
const repairRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_receipt_repairs_20260821");
const traceRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_pair_model_iteration_01_804_authoritative_build1_20260821");
const findingsFile = path.join(repo, "arb-executor", "docs", "research", "window1", "FINDINGS_V53.md");
fs.mkdirSync(repairRoot, { recursive: true });

function updateManifest(file, additions = []) {
  const manifest = JSON.parse(fs.readFileSync(file, "utf8"));
  for (const name of [...Object.keys(manifest.files), ...additions]) {
    const artifact = path.join(path.dirname(file), name);
    if (!fs.existsSync(artifact) || path.resolve(artifact) === path.resolve(file)) continue;
    manifest.files[name] = { ...(manifest.files[name] || {}), path: artifact, sha256: sha(fs.readFileSync(artifact)), bytes: fs.statSync(artifact).size };
  }
  writeJson(file, manifest);
}

function repairStrikeLedger() {
  const receiptFile = path.join(explainedRoot, "CITATION_WELD_RECEIPT.json");
  const receipt = JSON.parse(fs.readFileSync(receiptFile, "utf8"));
  const baseCommit = "9083e055";
  const weldedCommit = "4c7a4b5a29adcaa18cd139c6172e39111c2dc73e";
  const byFile = Object.groupBy(receipt.occurrences, (row) => row.file);
  let beforeMatches = 0;
  let afterMatches = 0;
  let explainedBeforeMatches = 0;
  let explainedAfterMatches = 0;
  const fileChecks = [];

  for (const [file, occurrences] of Object.entries(byFile)) {
    const originalLines = lines(gitBytes(baseCommit, file));
    const weldedLines = lines(gitBytes("HEAD", file));
    const used = new Set();
    let fileBefore = 0;
    let fileAfter = 0;
    for (const occurrence of occurrences) {
      const oldLineNumber = occurrence.welded_line_number ?? occurrence.original_line_number;
      if (!receipt.line_hash_repair && sha(Buffer.from(originalLines[oldLineNumber - 1] ?? "", "utf8")) === occurrence.original_line_sha256) {
        beforeMatches += 1;
        fileBefore += 1;
        if (file.includes("GAME_EXPLAINED_")) explainedBeforeMatches += 1;
      }
      const weldedLine = weldedLines[oldLineNumber - 1] || "";
      ensure(weldedLine.includes(occurrence.occurrence_id), `weld marker moved: ${occurrence.occurrence_id}`);
      const legacy = weldedLine.split(" <!-- CITATION-WELD:")[0];
      const candidates = [];
      originalLines.forEach((line, index) => { if (line === legacy && !used.has(index)) candidates.push(index); });
      ensure(candidates.length > 0, `committed original line absent: ${occurrence.occurrence_id}`);
      const originalIndex = candidates.sort((a, b) => Math.abs((a + 1) - oldLineNumber) - Math.abs((b + 1) - oldLineNumber))[0];
      used.add(originalIndex);
      occurrence.original_commit = baseCommit;
      occurrence.original_line_number = originalIndex + 1;
      occurrence.original_line_sha256 = sha(Buffer.from(originalLines[originalIndex], "utf8"));
      occurrence.welded_commit = weldedCommit;
      occurrence.welded_line_number = oldLineNumber;
      occurrence.welded_legacy_sha256 = sha(Buffer.from(legacy, "utf8"));
      occurrence.welded_committed_line_sha256 = sha(Buffer.from(weldedLine, "utf8"));
      if (sha(Buffer.from(originalLines[occurrence.original_line_number - 1], "utf8")) === occurrence.original_line_sha256) {
        afterMatches += 1;
        fileAfter += 1;
        if (file.includes("GAME_EXPLAINED_")) explainedAfterMatches += 1;
      }
    }
    const priorFileCheck = receipt.line_hash_repair?.files?.find((row) => row.file === file);
    fileChecks.push({ file, occurrences: occurrences.length, committed_coordinate_matches_before: priorFileCheck?.committed_coordinate_matches_before ?? fileBefore, committed_coordinate_matches_after: fileAfter });
  }

  if (receipt.line_hash_repair) {
    beforeMatches = receipt.line_hash_repair.before.all_matches;
    explainedBeforeMatches = receipt.line_hash_repair.before.explained_matches;
  }

  const explainedFiles = ["GIUBAR", "URSPAL", "LAJSVA", "DANPRA"].map((id) => `.claude/window1_live_v4_replay/v54_four_games_explained_20260821/GAME_EXPLAINED_${id}.md`);
  const bindingRewrites = [];
  let visibleUnchangedLines = 0;
  let preNonemptyLines = 0;
  let absentPreLines = 0;
  for (const file of explainedFiles) {
    const before = lines(gitBytes(baseCommit, file));
    const after = lines(gitBytes("HEAD", file));
    const beforeBinding = before.find((line) => line.startsWith("- **R-STORY:**"));
    const afterBinding = after.find((line) => line.startsWith("- **R-STORY:**"));
    ensure(beforeBinding && afterBinding, `R-STORY binding absent: ${file}`);
    const normalizedBefore = beforeBinding.replace(/[0-9a-f]{64}/, "<STORY_SHA>");
    const normalizedAfter = afterBinding.replace(/[0-9a-f]{64}/, "<STORY_SHA>");
    ensure(normalizedBefore === normalizedAfter, `R-STORY binding changed beyond sha: ${file}`);
    bindingRewrites.push({ file, kind: "R_STORY_MARKDOWN_BINDING", before_line_sha256: sha(Buffer.from(beforeBinding)), after_line_sha256: sha(Buffer.from(afterBinding)), only_story_sha_changed: true });
    const afterSet = new Set(after.flatMap((line) => [line, line.split(" <!-- CITATION-WELD:")[0]]));
    for (const line of before.filter(Boolean)) {
      preNonemptyLines += 1;
      if (afterSet.has(line)) visibleUnchangedLines += 1;
      else absentPreLines += 1;
    }
  }
  ensure(absentPreLines === 4, `unexpected prose lines not byte-visible: ${absentPreLines}`);
  const beforeExplanation = JSON.parse(gitBytes(baseCommit, ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/EXPLANATION_RECEIPT.json").toString("utf8"));
  const afterExplanation = JSON.parse(gitBytes("HEAD", ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/EXPLANATION_RECEIPT.json").toString("utf8"));
  bindingRewrites.push({
    file: ".claude/window1_live_v4_replay/v54_four_games_explained_20260821/EXPLANATION_RECEIPT.json",
    kind: "R_STORY_RECEIPT_BINDING",
    before: beforeExplanation.inputs.pass1_story,
    after: afterExplanation.inputs.pass1_story,
    only_story_binding_changed: beforeExplanation.inputs.pass1_story.path === afterExplanation.inputs.pass1_story.path,
  });
  ensure(bindingRewrites.length === 5 && bindingRewrites.every((row) => row.only_story_sha_changed === true || row.only_story_binding_changed === true), "five R-STORY bindings not conserved");

  receipt.line_hash_repair = {
    status: "REPAIRED_AGAINST_COMMITTED_BYTES",
    original_commit: baseCommit,
    welded_commit: weldedCommit,
    cause: "The repair classified lines after inserting neighbor-grain and blend-provenance rows, then stored those expanded-buffer line coordinates as original_line_number. The digests named the legacy text, but the coordinates did not address the pre-weld committed bytes; every explained-file lookup therefore drifted.",
    before: { all_matches: beforeMatches, all_occurrences: receipt.occurrences.length, explained_matches: explainedBeforeMatches, explained_occurrences: 105 },
    after: { all_matches: afterMatches, all_occurrences: receipt.occurrences.length, explained_matches: explainedAfterMatches, explained_occurrences: 105 },
    files: fileChecks,
    byte_visibility: {
      prose_files: explainedFiles,
      pre_nonempty_lines: preNonemptyLines,
      unchanged_lines_still_byte_visible: visibleUnchangedLines,
      non_byte_visible_markdown_lines: absentPreLines,
      five_binding_records_only: true,
      binding_rewrites: bindingRewrites,
    },
  };
  ensure(afterMatches === receipt.occurrences.length && explainedAfterMatches === 105, "committed-byte line repair incomplete");
  writeJson(receiptFile, receipt);
  return { receipt: stat(receiptFile), ...receipt.line_hash_repair };
}

function auditTrace() {
  ensure(fs.existsSync(traceRoot), `trace absent: ${traceRoot}`);
  const names = fs.readdirSync(traceRoot).filter((name) => fs.statSync(path.join(traceRoot, name)).isFile()).sort();
  ensure(names.length === 802, `trace file count changed: ${names.length}`);
  const files = names.map((name) => {
    const file = path.join(traceRoot, name);
    const bytes = fs.readFileSync(file);
    const info = fs.statSync(file);
    return { path: rel(file), sha256: sha(bytes), bytes: info.size, birthtime_utc: info.birthtime.toISOString(), last_write_utc: info.mtime.toISOString() };
  });
  const totalBytes = files.reduce((sum, row) => sum + row.bytes, 0);
  const localTime = (value) => new Date(value).toLocaleString("en-CA", { timeZone: "America/New_York", hour12: false, timeZoneName: "shortOffset" });
  const samples = [713, 451, 592].map((chunk) => {
    const name = `V54_FULL_PAIR_LICENSE_TRACE_804_CHUNK_${String(chunk).padStart(3, "0")}.jsonl.gz`;
    const compressed = fs.readFileSync(path.join(traceRoot, name));
    const uncompressed = zlib.gunzipSync(compressed);
    const text = uncompressed.toString("utf8");
    return {
      path: rel(path.join(traceRoot, name)),
      compressed_sha256: sha(compressed),
      compressed_bytes: compressed.length,
      uncompressed_sha256: sha(uncompressed),
      uncompressed_bytes: uncompressed.length,
      rows: text.split(/\r?\n/).filter(Boolean).length,
      verbatim_utf8: text,
    };
  });
  const builderPath = "arb-executor/analysis/build_window1_v38_maker_only.js";
  const builderBytes = gitBytes("2e1c8b41", builderPath);
  const findingsText = fs.readFileSync(findingsFile, "utf8");
  const orderReceipt = findingsText.split(/\r?\n/).find((line) => line.startsWith("F-V53-040 |"));
  ensure(orderReceipt, "F-V53-040 order receipt absent");
  const reflog = git(["reflog", "--date=iso-strict", "--format=%h %gd %gs", "--since=2026-08-21T11:35:00-04:00", "--until=2026-08-21T12:30:00-04:00"]).trim().split(/\r?\n/).filter(Boolean);
  const receipt = {
    label: "V54_UNTRACKED_804_TRACE_PROVENANCE_AND_CUSTODY_LIST",
    license: law,
    trace: {
      path: rel(traceRoot),
      regular_files: names.length,
      filesystem_entries_including_root_directory: names.length + 1,
      compressed_bytes: totalBytes,
      first_file_birthtime_utc: files.map((row) => row.birthtime_utc).sort()[0],
      last_file_write_utc: files.map((row) => row.last_write_utc).sort().at(-1),
      first_file_birthtime_local: localTime(files.map((row) => row.birthtime_utc).sort()[0]),
      last_file_write_local: localTime(files.map((row) => row.last_write_utc).sort().at(-1)),
      file_manifest_sha256: sha(Buffer.from(canonical(files))),
      committed: false,
      deleted: false,
      mutated_by_this_audit: false,
      custody_status: "LISTED_FOR_OPERATOR_DISPOSITION_NOT_TRANSFERRED",
      disposition_authority: "OPERATOR",
    },
    creator: {
      script: builderPath,
      head_at_trace_start: "2e1c8b41",
      script_sha256_at_head: sha(builderBytes),
      head_binding_method: "git reflog brackets the 11:39:19-04:00 local write start between the 11:38:32-04:00 2e1c8b41 commit and the 12:23:41-04:00 0a2affce commit",
      reflog_receipts: reflog,
      selected_route: { variant: "v54", stage: "tune804", output_override: rel(traceRoot) },
      exact_shell_command_receipt: "ABSENT",
      minimum_reconstructed_invocation: `node ${builderPath} --variant v54 --stage tune804 --output ${rel(traceRoot)}`,
      source_receipts: [
        `${builderPath}:199 isV54Tune804`,
        `${builderPath}:3392-3393 V54_PAIR_MODEL tune804 machine spec`,
        `${builderPath}:3506 trace writer prefix`,
        `${builderPath}:3546 simulate(...)`,
        `${builderPath}:3551-3574 license-span collection`,
        `${builderPath}:3583-3585 action extraction`,
        `${builderPath}:3736-3740 fixed-804 grading path`,
      ],
    },
    order: {
      produced_under: "V54 CHECK-SET order 2026-08-21",
      receipt: orderReceipt,
      scope_lock_disposition: "VIOLATION_FILED_AS_F_V53_069_BY_CURRENT_ORDER",
    },
    contents: {
      classification: "DECISION_LICENSE_SPANS_WITH_ACTION_VERDICTS_NOT_RETRIEVAL_ARTIFACTS",
      decision_pass_executed: true,
      fixed_population_path_selected: true,
      retrieval_artifacts_present: false,
      explanation: "Each JSONL row is a compressed span of V54 semantic decision licenses and includes lineage_decision, gate_verdict, final_action, final_target_cents, and the machine sentence. The builder calls simulate over replayBases before appending these spans and later enters fixed-804 grading.",
      three_files_verbatim_below: true,
    },
    sample_files: samples,
    files,
  };
  const receiptFile = path.join(repairRoot, "V54_TRACE_PROVENANCE_RECEIPT.json");
  writeJson(receiptFile, receipt);
  return stat(receiptFile);
}

function complianceCensus() {
  const siblingKeys = new Set(["construction_assertions_passed", "frozen_reference_row_verified", "commit_object_verified", "all_readers_fired"]);
  const tracked = git(["ls-files", "*.js"]).trim().split(/\r?\n/).filter(Boolean);
  const locations = [];
  for (const file of tracked) {
    const source = fs.readFileSync(path.join(repo, file), "utf8").split(/\r?\n/);
    source.forEach((line, index) => {
      for (const key of siblingKeys) if (new RegExp(`\\b${key}\\s*:\\s*(?:true|false)\\b`).test(line)) locations.push({ path: file, line: index + 1, key, literal: line.match(new RegExp(`\\b${key}\\s*:\\s*(true|false)\\b`))[1] });
    });
  }
  ensure(locations.length === 3, `graveyard hardcoded verdict census changed: ${locations.length}`);
  return {
    definition: "Tracked production JavaScript output keys whose names assert construction/reader verification or compliance and whose value is a boolean literal; preregistered acceptance criteria, tests, and domain-state passed flags are excluded.",
    target_literals_removed: [
      { path: "arb-executor/analysis/build_window1_v54_functionable_v6.js", former_line: 469, key: "zero_law_violations", path_kind: "finalize_existing" },
      { path: "arb-executor/analysis/build_window1_v54_functionable_v6.js", former_line: 506, key: "zero_law_violations", path_kind: "fresh_receipt" },
      { path: "arb-executor/analysis/build_window1_v54_functionable_v6.js", former_line: 497, key: "all_readers_fired", path_kind: "integration_smoke" },
    ],
    graveyard_hardcoded_compliance_or_verdict_literals: { count: locations.length, locations, disposition: "CATALOGED_UNTOUCHED" },
    total_sites_swept: locations.length + 3,
  };
}

const lineRepair = repairStrikeLedger();
const traceReceipt = auditTrace();

const storyReceipt = path.join(storyRoot, "FOUR_STORIES_RECEIPT.json");
const explanationReceiptFile = path.join(explainedRoot, "EXPLANATION_RECEIPT.json");
const explanationReceipt = JSON.parse(fs.readFileSync(explanationReceiptFile, "utf8"));
const committedExplanationReceipt = JSON.parse(gitBytes("HEAD", rel(explanationReceiptFile)).toString("utf8"));
const storyReceiptStat = stat(storyReceipt);
explanationReceipt.inputs.pass1_result = { ...explanationReceipt.inputs.pass1_result, path: committedExplanationReceipt.inputs.pass1_result.path, sha256: storyReceiptStat.sha256, bytes: storyReceiptStat.bytes };
writeJson(explanationReceiptFile, explanationReceipt);

updateManifest(path.join(storyRoot, "ARTIFACT_HASH_MANIFEST.json"));
updateManifest(path.join(explainedRoot, "ARTIFACT_HASH_MANIFEST.json"));

const repairReceipt = {
  label: "V54_TWO_COSTUMES_AND_RECEIPT_REPAIR",
  license: law,
  scope: { repair_class_only: true, passes: 0, reruns: 0, full_804_run: false, trace_read_only: true },
  f_vs_040: {
    result: "HARDCODED_LAW_VERDICT_REMOVED_NOT_REPLACED",
    source: stat(path.join(repo, "arb-executor", "analysis", "build_window1_v54_functionable_v6.js")),
    artifact: stat(storyReceipt),
    census: complianceCensus(),
  },
  f_vs_041: { result: "DECISION_PASS_SCOPE_LOCK_VIOLATION_FILED_TRACE_LEFT_UNTRACKED", receipt: traceReceipt },
  f_vs_038: { result: "STRIKE_LEDGER_REBOUND_TO_COMMITTED_BYTES", repair: lineRepair },
};
const repairReceiptFile = path.join(repairRoot, "TWO_COSTUMES_RECEIPT.json");
writeJson(repairReceiptFile, repairReceipt);
writeJson(path.join(repairRoot, "ARTIFACT_HASH_MANIFEST.json"), {
  label: repairReceipt.label,
  files: {
    "TWO_COSTUMES_RECEIPT.json": stat(repairReceiptFile),
    "V54_TRACE_PROVENANCE_RECEIPT.json": traceReceipt,
  },
});

process.stdout.write(canonical({
  receipt_repair: "COMPLETE",
  graveyard_literal_count: repairReceipt.f_vs_040.census.graveyard_hardcoded_compliance_or_verdict_literals.count,
  trace_regular_files: 802,
  trace_committed: false,
  decision_pass_executed: true,
  strike_hashes: lineRepair.after,
  r_story_binding_records: lineRepair.byte_visibility.binding_rewrites.length,
  receipts: [stat(repairReceiptFile), traceReceipt],
}));
