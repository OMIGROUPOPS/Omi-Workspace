import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import zlib from "node:zlib";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { unpackFace } from "./face_encoding.mjs";
import { readGradeRulers } from "./grade_rulers.mjs";
import { readGradePrints } from "./grade_prints.mjs";
import {
  gradeFace,
  projectDecision,
  scanNamed,
  SILENT,
} from "./grade_contract.mjs";

const here = path.dirname(fileURLToPath(import.meta.url)),
  repo = path.dirname(here);
const sha = (b) => crypto.createHash("sha256").update(b).digest("hex");
const args = process.argv.slice(2);
const arg = (key) => args[args.indexOf("--" + key) + 1];
const option = (key) => (args.includes("--" + key) ? arg(key) : undefined);
const git = (...argv) =>
  execFileSync("git", argv, { cwd: repo, maxBuffer: 20 * 1024 * 1024 });
const json = (b) => JSON.parse(b);
const encode = (o) => JSON.stringify(o, null, 2) + "\n";
async function readJson(file, fallback) {
  try {
    return json(await fs.readFile(file));
  } catch (e) {
    if (e.code === "ENOENT" && fallback !== undefined) return fallback;
    throw e;
  }
}
async function writeJson(file, data) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file + ".tmp", encode(data));
  await fs.rename(file + ".tmp", file);
}
async function citation(file, role, external = false) {
  const bytes = await fs.readFile(file);
  const rel = path.relative(repo, file).replaceAll("\\", "/");
  let commit = null;
  if (!external)
    commit =
      git("log", "-1", "--format=%H", "--", rel).toString().trim() || null;
  return {
    path: external ? file : rel,
    sha256: sha(bytes),
    bytes: bytes.length,
    commit: commit ?? SILENT,
    role,
  };
}
async function sourceReceipt(benchSource) {
  const audit =
    ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803";
  const prior =
    option("prior-report") ??
    "C:/tmp/omi-v53-understanding-organ-20260819/.claude/window1_live_v4_replay/v54_walk5_repair_v6_20260821/PER_GAME_L1_L8.json";
  const citations = {};
  citations.PER_GAME_L1_L8 = await citation(
    prior,
    "Replaced per-game L1–L8 report. Builder baseline reads rows[].L7_CREDIT.why.",
    true,
  );
  const legacy = await readJson(prior);
  citations.PER_GAME_L1_L8.rows = legacy.rows.length;
  if (!legacy.rows.every((r) => r.L7_CREDIT && r.L8_OUTCOME))
    throw new Error("Unrecognized PER_GAME_L1_L8");
  citations.HONEST_SCOREBOARD = await citation(
    path.join(repo, audit, "HONEST_SCOREBOARD.md"),
    "Truth-table offered cents and span-valid captured cents; complete under par, not apparent fills.",
  );
  citations.OFFER_DENOMINATOR = await citation(
    path.join(repo, audit, "OFFER_DENOMINATOR.md"),
    "Definition B: verified-span floors under par; both credited fills inside the span for capture.",
  );
  citations.GATE_1_OBJECT = await citation(
    path.join(repo, "artifacts/review_mirror/GATE_1_OBJECT.md"),
    "P/Q/X require an author reading this leg; test 1 own receipt weights, test 2 own clock, test 3 no named pricing rule.",
  );
  const benchPath = benchSource
    ? path.resolve(repo, path.dirname(benchSource), "TUNE_BENCH_RECEIPT.json")
    : null;
  const receipt = benchPath ? await readJson(benchPath, null) : null;
  return {
    version: 2,
    role: "REPORT ONLY — no OS inputs changed",
    citations,
    bench_taxonomy_receipt: receipt
      ? {
          ...(await citation(
            benchPath,
            "Realized family rule, inherited 17-point taxonomy plus declared bench choices.",
          )),
          signature_method:
            receipt.prior_art?.SHAPE_TAXONOMY_BUILD1?.signature_method_verbatim,
          bench_choices: receipt.prior_art?.taxonomy_bench_choices,
          label: receipt.label,
        }
      : SILENT,
    rules: {
      authorship:
        "Q excludes PRIOR_REWEIGHTED_BY_OWN_WALK as a non-organ badge: 2dfb5b0abf3fdf8669b8750d2780effd44a7319c stamps the label from print count/slope without changing ownEvidenceChannelGrades or conditionPriorDistribution. Raw author counts are retained; X classification is unchanged. Remaining token shares are not Gate-1 evidence-chain certification.",
      missing: "STORE SILENT; no number or author is invented.",
      outcomes:
        "Offered = positive truth discount; captured = positive discount of span-valid complete, otherwise zero; partial is zero.",
      history:
        "Fixed OS8_trace8 file appends a full snapshot to grades[]; earlier rubric results are retained.",
      taxonomy:
        "Read realized labels from the hash-bound bench. Compare each side's latest stored family as of bench bell minus gate*60 against that same bench gate; no OS timestamp or family is recomputed. MICRO and chart clocks stay unchanged.",
      cascade_writers:
        "FIELDS.md maps POOL_FIRST_TICK (alias), POOL_FIRST-TICK-ONLY, POOL_BASE, POOL_CASCADE:* and POOL_CASCADE_WRITER to ORGAN. Hold/veto precedence and raw tokens remain unchanged.",
      ruler_comparison:
        "Apply every event-matching correction from W1_GROUND_TRUTH_CORRECTIONS.jsonl @15955e44 in ledger order to the original pinned row. Effective floors, bell, span and denominator grade this run; original CSV and full correction JSONL rows remain alongside. Every observed fill is revalidated against both corrected span and bell. No trace, face input, or OS call is changed.",
      micro: "First eligible stored resolved P/Q/X forecast in receipt order versus full recorded span; every eligible receipt versus its remaining path, with separate carried state and strictly future-print targets. Match timing to each target using the original absolute deadline. Existing rubric cutoffs unchanged; worst of the two grading modes. Receipt-level errors, means and denominators retained.",
      hands_ages: "Separate original PLACE lineage age from current-price age, resetting only the latter on price change; remove/fill ends the lineage. Fill same-second check uses the current-price start timestamp. The legacy chart age is preserved, not used as current-price duration.",
      named_scope:
        "Exact symbolic named tokens on rows; no inference that unrecorded code branches are absent.",
    },
  };
}
function osCommit(osSha) {
  if (!/^[a-f0-9]{64}$/i.test(osSha ?? ""))
    return { commit: SILENT, order: null };
  const file = "arb-executor/analysis/window1_v54_dual_belief_os.js";
  const commits = git("rev-list", "HEAD", "--", file)
    .toString()
    .trim()
    .split(/\r?\n/);
  for (const commit of commits) {
    try {
      if (sha(git("show", `${commit}:${file}`)) === osSha.toLowerCase())
        return {
          commit,
          order: Number(git("rev-list", "--count", commit).toString().trim()),
        };
    } catch {
      /* File might not exist in a deletion commit. */
    }
  }
  return { commit: SILENT, order: null };
}
export async function appendHistory(
  dataRoot,
  grade,
  timestamp = new Date().toISOString(),
) {
  const p = grade.provenance,
    event = grade.event;
  for (const k of ["os_sha256", "trace_sha256"])
    if (!/^[a-f0-9]{64}$/i.test(p[k] ?? ""))
      throw new Error(`Cannot key grade history without ${k}`);
  const basename = `${p.os_sha256.slice(0, 8)}_${p.trace_sha256.slice(0, 8)}.json`;
  const url = `/data/grades/${event}/${basename}`,
    file = path.join(dataRoot, "grades", event, basename);
  const bucket = await readJson(file, {
    version: 1,
    event,
    os_sha256: p.os_sha256,
    trace_sha256: p.trace_sha256,
    grades: [],
  });
  if (
    bucket.os_sha256 !== p.os_sha256 ||
    bucket.trace_sha256 !== p.trace_sha256 ||
    bucket.event !== event
  )
    throw new Error("Grade history hash-prefix collision");
  const indexFile = path.join(dataRoot, "grades/index.json");
  const index = await readJson(indexFile, {
    version: 1,
    grades: [],
    axis: { letters: ["A", "B", "C", "D", "F", SILENT] },
  });
  const snapshot = { ...grade, timestamp };
  bucket.grades.push(snapshot);
  const entry = {
    event,
    timestamp,
    os_sha: p.os_sha256,
    trace_sha: p.trace_sha256,
    os_commit: p.os_commit,
    commit_order: p.os_commit_order,
    grading_commit: p.grading_commit,
    letter: grade.LETTER.letter,
    capture_ratio: grade.OUTCOME.capture_ratio,
    governing_section: grade.LETTER.governing_section,
    url,
    revision: bucket.grades.length - 1,
    grade_sha256: sha(encode(snapshot)),
    append_order: index.grades.length,
  };
  index.grades.push(entry);
  for (const id of new Set(index.grades.map((g) => g.event))) {
    const rows = index.grades
      .filter((g) => g.event === id)
      .sort(
        (a, b) =>
          (a.commit_order ?? Infinity) - (b.commit_order ?? Infinity) ||
          a.append_order - b.append_order,
      );
    rows.forEach((r, i) => {
      r.x = 30 + i * 34;
      r.y = 16 + index.axis.letters.indexOf(r.letter) * 18;
      r.hover_lines = [
        `${r.os_sha} · ${r.letter}`,
        r.governing_section,
        `${r.timestamp} · run ${r.append_order + 1}`,
        r.commit_order == null
          ? "OS commit order STORE SILENT"
          : `OS commit ${r.os_commit}`,
      ];
    });
  }
  index.views = Object.fromEntries(
    [...new Set(index.grades.map((g) => g.event))].map((id) => [
      id,
      {
        width: Math.max(
          180,
          60 + index.grades.filter((g) => g.event === id).length * 34,
        ),
        height: 126,
        labels: index.axis.letters.map((letter, i) => ({
          letter: letter === SILENT ? "—" : letter,
          y: 16 + i * 18,
        })),
      },
    ]),
  );
  await writeJson(file, bucket);
  await writeJson(indexFile, index);
  await writeJson(path.join(dataRoot, event + ".grade.json"), snapshot);
  return { snapshot, entry };
}
export async function build(event, printInput) {
  if (!/^[A-Z0-9-]+$/.test(event ?? ""))
    throw new Error(
      "Usage: node window1-watch/build_grade.mjs --event <event_id>",
    );
  const dataRoot = path.join(here, "data"),
    faceFile = path.join(dataRoot, event + ".face.json");
  const faceBytes = await fs.readFile(faceFile),
    face = unpackFace(json(faceBytes));
  if (face.provenance?.event_id !== event)
    throw new Error("Face event mismatch");
  if (!printInput) {
    const all = await readGradePrints(option("prints") ?? "C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl", [{ event, legs: face.legs }]);
    printInput = all[event];
  }
  const rubricBytes = await fs.readFile(path.join(here, "grade_rubric.json")),
    rubric = json(rubricBytes);
  const decisions = [],
    named = new Map(),
    stageDigest = crypto.createHash("sha256");
  for (const stage of face.os) {
    if (stage.kind !== "DECISION_STAGE") continue;
    const relative = stage.detail_url?.replace(/^\/data\//, "");
    if (!relative) throw new Error("Missing inspector binding");
    const file = path.resolve(dataRoot, relative + ".gz");
    if (!file.startsWith(path.resolve(dataRoot) + path.sep))
      throw new Error("Unsafe stage path");
    const stageBytes = await fs.readFile(file);
    stageDigest.update(`${relative}\0${sha(stageBytes)}\n`);
    const stored = json(zlib.gunzipSync(stageBytes)),
      row = stored.row;
    if (
      row.event_id !== event ||
      row.receipt !== stage.receipt ||
      stored.source.trace_row !== stage.trace_row
    )
      throw new Error("Stage binding mismatch");
    decisions.push({ ...projectDecision(row, face), trace_row: stored.source.trace_row });
    scanNamed(row, face.legs, event, (token, field) => {
      if (!named.has(token))
        named.set(token, {
          token,
          count: 0,
          first_receipt: row.receipt,
          first_field: field,
        });
      named.get(token).count++;
    });
  }
  let bench = null;
  if (face.bench?.present && face.bench.source) {
    const bytes = await fs.readFile(face.bench.source);
    if (sha(bytes) !== face.provenance.bench_sha256)
      throw new Error(
        "Bench SHA mismatch; rebuild the face explicitly, never join a changed file",
      );
    bench = json(bytes);
  }
  const receipt = await sourceReceipt(face.bench?.source),
    receiptSha = sha(encode(receipt));
  const os = osCommit(face.provenance.os_sha256);
  const rulers = readGradeRulers(repo, event, face);
  const effectiveFace = { ...face, truth: rulers.effective_truth };
  const provenance = {
    os_sha256: face.provenance.os_sha256,
    trace_sha256: face.provenance.trace_sha256,
    bench_sha256: face.provenance.bench_sha256 ?? null,
    truth_commit: face.truth?.table_commit ?? null,
    truth_row_sha256: face.truth?.row_sha256 ?? null,
    truth_corrections_commit: rulers.correction_source.commit,
    truth_corrections_sha256: rulers.correction_source.sha256,
    effective_truth_sha256: sha(encode(rulers.effective_truth)),
    true_print_source_sha256: printInput.provenance.sha256,
    face_sha256: sha(faceBytes),
    stage_inputs_sha256: stageDigest.digest("hex"),
    stage_files_count: decisions.length,
    rubric_sha256: sha(rubricBytes),
    receipt_sha256: receiptSha,
    grade_builder_sha256: sha(
      await fs.readFile(fileURLToPath(import.meta.url)),
    ),
    grade_contract_sha256: sha(
      await fs.readFile(path.join(here, "grade_contract.mjs")),
    ),
    grade_rulers_sha256: sha(await fs.readFile(path.join(here, "grade_rulers.mjs"))),
    grade_measurements_sha256: sha(await fs.readFile(path.join(here, "grade_measurements.mjs"))),
    grade_prints_sha256: sha(await fs.readFile(path.join(here, "grade_prints.mjs"))),
    fields_sha256: sha(await fs.readFile(path.join(here, "FIELDS.md"))),
    os_commit: os.commit,
    os_commit_order: os.order,
    grading_commit: git("rev-parse", "HEAD").toString().trim(),
  };
  const grade = gradeFace(effectiveFace, decisions, named, bench, rubric, provenance, printInput);
  grade.RULER_COLUMNS = rulers;
  grade.receipt = receipt;
  await writeJson(path.join(dataRoot, "GRADE_RECEIPT.json"), receipt);
  const { snapshot } = await appendHistory(dataRoot, grade);
  console.log(
    `${event} · ${snapshot.LETTER.letter} · ${snapshot.LETTER.governing_section}`,
  );
  for (const section of snapshot.display.sections)
    console.log(`${section.name}: ${section.line}`);
  console.log(`grade: ${path.join(dataRoot, event + ".grade.json")}`);
  return snapshot;
}
if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  try {
    if (args.includes("--all")) {
      const index = await readJson(path.join(here, "data/index.json"));
      const games = await Promise.all(index.games.map(async (g) => ({ event: g.event,
        legs: json(await fs.readFile(path.join(here, "data", g.event + ".face.json"))).legs })));
      const prints = await readGradePrints(option("prints") ?? "C:/Users/omigr/OMI-Window1-private/fit-local/prints.jsonl", games);
      for (const g of games) await build(g.event, prints[g.event]);
    } else await build(option("event"));
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  }
}
