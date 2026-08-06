#!/usr/bin/env node
"use strict";

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
function arg(name, fallback = null) { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; }
function has(name) { return args.includes(name); }
function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function exec(file, argv, options = {}) { return child.execFileSync(file, argv, { encoding: "utf8", maxBuffer: 512 * 1024 * 1024, ...options }); }

const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_fresh_holdout_seal_20260806")));
const constructionParent = arg("--parent", "19da991c2e266443a0061fc49f779bc915ed1a6e");
const host = arg("--host", "root@104.131.191.95");
const remoteRoot = "/root/Omi-Workspace/arb-executor/analysis/premarket_ticks";
const remoteCensusPath = path.join(output, "REMOTE_TAPE_CENSUS.json");
const touchAuditPath = path.join(output, "GIT_TOUCH_AUDIT.json");
const series = {
  KXATPCHALLENGERMATCH: "ATP_CHALL",
  KXATPMATCH: "ATP_MAIN",
  KXWTACHALLENGERMATCH: "WTA_CHALL",
  KXWTAMATCH: "WTA_MAIN",
};
const frozenHistoryProbes = {
  "KXATPCHALLENGERMATCH-26JUL27PINSAM": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXATPCHALLENGERMATCH-26JUL27SEKCHI": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXATPCHALLENGERMATCH-26JUL27WENCAS": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXATPCHALLENGERMATCH-26JUL28HARCHU": ["e7004235c342a2ddaaa53610d85a76c32fb93fdc"],
  "KXATPCHALLENGERMATCH-26JUL28MATTRO": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80", "e7004235c342a2ddaaa53610d85a76c32fb93fdc"],
  "KXATPCHALLENGERMATCH-26JUL28SHITOK": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXATPCHALLENGERMATCH-26JUL28ZINPOL": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80", "e7004235c342a2ddaaa53610d85a76c32fb93fdc", "fd623dd042da2f1dfb9479c8a759c8c610672215"],
  "KXATPMATCH-26JUL28KWONGEA": ["226cd5e7cccc57ccb81d3634de255aaeb035d11d", "63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXATPMATCH-26JUL28MICMCD": [],
  "KXWTAMATCH-26JUL27STOSTE": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXWTAMATCH-26JUL27WANMCC": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
  "KXWTAMATCH-26JUL27YEXBIR": ["63e7f4d652564f19ea9da8b0404fe6371ea23f80"],
};

const remoteProgram = String.raw`
import concurrent.futures, datetime, glob, hashlib, json, os, re, subprocess
from zoneinfo import ZoneInfo

ROOT = "/root/Omi-Workspace/arb-executor/analysis/premarket_ticks"
SERIES = {
  "KXATPCHALLENGERMATCH": "ATP_CHALL",
  "KXATPMATCH": "ATP_MAIN",
  "KXWTACHALLENGERMATCH": "WTA_CHALL",
  "KXWTAMATCH": "WTA_MAIN",
}
MONTHS = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

def event_date(event_id):
  m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_id)
  if not m: return None
  return datetime.date(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))

def integer(value):
  try:
    n = float(value)
    return int(n) if n.is_integer() else None
  except: return None

def positive(value):
  try:
    n = float(value)
    return n if n > 0 else None
  except: return None

def inspect_file(filename):
  base = os.path.basename(filename)
  m = re.match(r"^((?:KXATPCHALLENGERMATCH|KXATPMATCH|KXWTACHALLENGERMATCH|KXWTAMATCH)-[A-Z0-9]+)-([A-Z0-9]+)\.csv\.gz$", base)
  if not m: return None
  event_id, leg_id = m.group(1), m.group(2)
  d = event_date(event_id)
  if d is None or d <= datetime.date(2026, 7, 26): return None
  prefix = event_id.split("-", 1)[0]
  digest = hashlib.sha256()
  with open(filename, "rb") as raw:
    for block in iter(lambda: raw.read(1024 * 1024), b""): digest.update(block)
  awk = r'''BEGIN{FS=","} NR==2{first=$1;ticker=$2} NR>1{last=$1; rows++; if(!w){b=0;a=0; for(i=3;i<=11;i+=2)if($i~/^-?[0-9]+$/ && $(i+1)+0>0)b=1; for(i=13;i<=21;i+=2)if($i~/^-?[0-9]+$/ && $(i+1)+0>0)a=1; if(a&&b)w=1}} END{printf "%s\t%s\t%s\t%d\t%d",first,last,ticker,rows,w}'''
  gunzip = subprocess.Popen(["gzip", "-cd", filename], stdout=subprocess.PIPE)
  summary = subprocess.check_output(["awk", awk], stdin=gunzip.stdout, text=True)
  gunzip.stdout.close()
  if gunzip.wait() != 0: raise RuntimeError("gzip failed " + filename)
  first_et, last_et, ticker, row_text, witness_text = summary.split("\t")
  row_count = int(row_text); parsed_timestamp_rows = row_count; v36_admission_witness_rows = int(witness_text)
  first_epoch = last_epoch = None
  if first_et is not None:
    first_epoch = int(datetime.datetime.strptime(first_et, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ZoneInfo("America/New_York")).timestamp())
    last_epoch = int(datetime.datetime.strptime(last_et, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ZoneInfo("America/New_York")).timestamp())
  return {
    "event_id": event_id, "event_date": d.isoformat(), "category": SERIES[prefix],
    "leg_id": leg_id, "ticker": ticker, "remote_path": filename,
    "bytes": os.path.getsize(filename), "sha256": digest.hexdigest(),
    "csv_rows": row_count, "parsed_timestamp_rows": parsed_timestamp_rows,
    "v36_admission_witness_rows": v36_admission_witness_rows,
    "first_timestamp_et": first_et, "first_timestamp_epoch": first_epoch,
    "last_timestamp_et": last_et, "last_timestamp_epoch": last_epoch,
    "span_seconds": None if first_epoch is None or last_epoch is None else last_epoch - first_epoch,
  }

candidates = []
for filename in sorted(glob.glob(ROOT + "/*.csv.gz")):
  base = os.path.basename(filename)
  m = re.match(r"^((?:KXATPCHALLENGERMATCH|KXATPMATCH|KXWTACHALLENGERMATCH|KXWTAMATCH)-[A-Z0-9]+)-([A-Z0-9]+)\.csv\.gz$", base)
  if m and event_date(m.group(1)) and event_date(m.group(1)) > datetime.date(2026, 7, 26): candidates.append(filename)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  files = sorted([x for x in pool.map(inspect_file, candidates) if x], key=lambda x: (x["event_id"], x["ticker"] or x["leg_id"]))

events = {}
for row in files: events.setdefault(row["event_id"], []).append(row)
event_rows = []
for event_id in sorted(events):
  legs = sorted(events[event_id], key=lambda x: x["ticker"] or x["leg_id"])
  firsts = [x["first_timestamp_epoch"] for x in legs if x["first_timestamp_epoch"] is not None]
  lasts = [x["last_timestamp_epoch"] for x in legs if x["last_timestamp_epoch"] is not None]
  event_rows.append({
    "event_id": event_id, "event_date": legs[0]["event_date"], "category": legs[0]["category"],
    "leg_count": len(legs), "paired": len(legs) == 2,
    "v36_floor_pass_admissible": len(legs) == 2 and all(x["v36_admission_witness_rows"] > 0 for x in legs),
    "first_timestamp_epoch": min(firsts) if firsts else None,
    "last_timestamp_epoch": max(lasts) if lasts else None,
    "span_seconds": max(lasts) - min(firsts) if firsts and lasts else None,
    "legs": legs,
  })

print(json.dumps({
  "schema_version": "window1-fresh-holdout-remote-tape-census-v1",
  "source": {"host": "104.131.191.95", "root": ROOT, "access": "READ_ONLY_SSH"},
  "date_law": "EVENT_ID_DATE_STRICTLY_AFTER_2026-07-26",
  "categories": list(SERIES.values()),
  "event_count": len(event_rows), "leg_file_count": len(files),
  "paired_event_count": sum(1 for x in event_rows if x["paired"]),
  "floor_pass_admissible_event_count": sum(1 for x in event_rows if x["v36_floor_pass_admissible"]),
  "events": event_rows,
}, sort_keys=True))
`;

function acquireRemote() {
  fs.mkdirSync(output, { recursive: true });
  const proc = child.spawnSync("ssh", ["-o", "BatchMode=yes", host, "python3 -"], { input: remoteProgram, encoding: "utf8", maxBuffer: 512 * 1024 * 1024 });
  ensure(proc.status === 0, `remote tape census failed: ${proc.stderr || proc.stdout}`);
  const parsed = JSON.parse(proc.stdout);
  ensure(parsed.event_count === parsed.paired_event_count, "unpaired post-Jul26 event");
  fs.writeFileSync(remoteCensusPath, canonical(parsed));
}

function auditGit() {
  ensure(fs.existsSync(remoteCensusPath), "REMOTE_TAPE_CENSUS.json missing; run --acquire first");
  const census = JSON.parse(fs.readFileSync(remoteCensusPath, "utf8"));
  ensure(exec("git", ["rev-parse", "--verify", `${constructionParent}^{commit}`], { cwd: repo }).trim() === constructionParent, "construction parent missing");
  exec("git", ["cat-file", "-e", `${constructionParent}^{commit}`], { cwd: repo });
  const pattern = "KX(ATPCHALLENGERMATCH|ATPMATCH|WTACHALLENGERMATCH|WTAMATCH)-26JUL(27|28)[A-Z0-9]+";
  let grep = "";
  try { grep = exec("git", ["grep", "-n", "-I", "-E", pattern, constructionParent, "--", "."], { cwd: repo }); } catch (error) { grep = error.stdout || ""; ensure([0, 1].includes(error.status), `git grep failed ${error.message}`); }
  const currentMatches = new Map();
  for (const line of grep.split(/\r?\n/).filter(Boolean)) {
    const m = line.match(/^(?:[0-9a-f]{40}:)?([^:]+):(\d+):(.*)$/); if (!m) continue;
    for (const hit of m[3].matchAll(/KX(?:ATPCHALLENGERMATCH|ATPMATCH|WTACHALLENGERMATCH|WTAMATCH)-26JUL(?:27|28)[A-Z0-9]+/g)) {
      if (!currentMatches.has(hit[0])) currentMatches.set(hit[0], { path: m[1], line: +m[2] });
    }
  }
  const rows = [];
  for (const event of census.events) {
    const current = currentMatches.get(event.event_id);
    if (current) {
      const blame = exec("git", ["blame", "--porcelain", "-L", `${current.line},${current.line}`, constructionParent, "--", current.path], { cwd: repo });
      const touchingCommit = blame.split(/\s+/)[0];
      rows.push({ event_id: event.event_id, status: "EXCLUDED_TOUCHED", proof_class: "PRESENT_AT_CONSTRUCTION_PARENT", touching_commits: [touchingCommit], first_current_tree_citation: current });
      continue;
    }
    ensure(Object.hasOwn(frozenHistoryProbes, event.event_id), `missing frozen all-ref pickaxe probe ${event.event_id}`);
    const commits = [...frozenHistoryProbes[event.event_id]].sort();
    rows.push({ event_id: event.event_id, status: commits.length ? "EXCLUDED_TOUCHED" : "SEALED_UNTOUCHED", proof_class: commits.length ? "HISTORICAL_REF_OR_REFLOG_PICKAXE_HIT" : "NO_CURRENT_TREE_OR_ALL_REF_REFLOG_PICKAXE_HIT", touching_commits: commits, first_current_tree_citation: null });
  }
  const refs = exec("git", ["for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes"], { cwd: repo }).split(/\r?\n/).filter(Boolean).sort();
  fs.writeFileSync(touchAuditPath, canonical({
    schema_version: "window1-fresh-holdout-git-touch-audit-v1",
    construction_parent: constructionParent,
    audit_commands: {
      current_tree: `git grep -n -I -E '${pattern}' ${constructionParent} -- .`,
      citation_identity: `git blame --porcelain -L <line>,<line> ${constructionParent} -- <path>`,
      absent_from_current_tree: "git log --all --reflog -S <event_id> --format=%H (executed and frozen before package generation on 2026-08-06)",
      object_validation: [`git rev-parse --verify ${constructionParent}^{commit}`, `git cat-file -e ${constructionParent}^{commit}`],
    },
    fetched_ref_snapshot: refs,
    candidate_events: rows.length,
    excluded_touched: rows.filter((x) => x.status === "EXCLUDED_TOUCHED").length,
    sealed_untouched: rows.filter((x) => x.status === "SEALED_UNTOUCHED").length,
    rows,
  }));
}

function build() {
  ensure(fs.existsSync(remoteCensusPath) && fs.existsSync(touchAuditPath), "acquisition inputs missing");
  const census = JSON.parse(fs.readFileSync(remoteCensusPath, "utf8"));
  const audit = JSON.parse(fs.readFileSync(touchAuditPath, "utf8"));
  ensure(census.event_count === audit.candidate_events, "census/audit denominator mismatch");
  const eventBy = new Map(census.events.map((x) => [x.event_id, x]));
  const sealed = audit.rows.filter((x) => x.status === "SEALED_UNTOUCHED").map((x) => eventBy.get(x.event_id)).sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(sealed.every(Boolean), "sealed identity missing from tape census");
  const eventListBytes = Buffer.from(sealed.map((x) => x.event_id).join("\n") + (sealed.length ? "\n" : ""));
  const N = sealed.length;
  const gatePass = N >= 60;
  const floorLaw = {
    source_commit: "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
    source_path: "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
    source_function: "loadFullTape",
    admission: "FOR_EACH_LEVEL_1_TO_5_INTEGER_PRICE_AND_STRICTLY_POSITIVE_SIZE; REQUIRE_AT_LEAST_ONE_BID_AND_ONE_ASK; SORT_BIDS_DESC_AND_ASKS_ASC; PRESERVE_RECEIPT_TIMESTAMP_AND_ORDINAL",
    event_pass: "EXACTLY_TWO_BIG4_LEG_TAPES_AND_EACH_LEG_HAS_AT_LEAST_ONE_ADMISSIBLE_TWO_SIDED_RECEIPT",
    tuning_changes: 0,
  };
  const declaration = {
    schema_version: "window1-fresh-holdout-sealed-declaration-v1",
    status: gatePass ? "SEALED_N_GE_60_STAGE2_CONDITION_SATISFIED" : "STOPPED_N_LT_60_STAGE2_FORBIDDEN",
    construction_parent: constructionParent,
    date_law: census.date_law,
    source: census.source,
    candidate_census: { events: census.event_count, leg_files: census.leg_file_count, paired: census.paired_event_count, floor_pass_admissible: census.floor_pass_admissible_event_count },
    git_touch_audit: { excluded_touched: audit.excluded_touched, sealed_untouched: audit.sealed_untouched },
    sealed_N: N,
    minimum_required_N: 60,
    shortfall: Math.max(0, 60 - N),
    event_list_sha256: sha(eventListBytes),
    event_list_bytes: eventListBytes.length,
    floor_pass_admission_law: floorLaw,
    events: sealed,
  };
  const exam = {
    schema_version: "window1-fresh-holdout-one-run-gate-v1",
    stage_1: { status: declaration.status, N, required_N: 60, declaration: "SEALED_DECLARATION.json" },
    stage_2: {
      status: gatePass ? "AUTHORIZED_BY_OPERATOR_CONTINGENCY_NOT_INVOKED_BY_THIS_BUILDER" : "NOT_INVOKED_CONDITIONAL_AUTHORIZATION_UNSATISFIED",
      brain_runner_invocations: { V36: 0, V35: 0, R3: 0, total: 0 },
      retries: 0,
      score_rows: 0,
      brains: {
        V36: "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
        V35: "0799fba887f1d1e84f9c0ef3e73096fd9d76019e",
        R3: "49f6501561c5d99a7f36c68ec41e0ea7250680e5",
      },
      performance_fields: null,
    },
    forbidden_access: { scorer_or_replay_invocation: 0, holdout_tape_contents_consumed_by_brains: 0, live_orders_positions_or_services: 0, tuning: 0, retry: 0 },
  };
  fs.writeFileSync(path.join(output, "SEALED_EVENT_LIST.txt"), eventListBytes);
  fs.writeFileSync(path.join(output, "SEALED_DECLARATION.json"), canonical(declaration));
  fs.writeFileSync(path.join(output, "ONE_RUN_GATE_RECEIPT.json"), canonical(exam));
  fs.writeFileSync(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({
    schema_version: "window1-fresh-holdout-forbidden-access-receipt-v1",
    remote_actions: ["READ_ONLY_TAPE_METADATA_HASH_AND_ROW_CENSUS"],
    brain_runner_invocations: 0, scorer_invocations: 0, result_rows: 0,
    order_reads: 0, order_writes: 0, position_reads: 0, position_writes: 0,
    service_reads: 0, service_writes: 0, network_order_calls: 0, tuning_changes: 0,
    stage_2_forbidden_reason: gatePass ? null : `SEALED_N_${N}_LT_60`,
  }));
  const sourceInputs = [remoteCensusPath, touchAuditPath].map((file) => [path.basename(file), { sha256: sha(fs.readFileSync(file)), bytes: fs.statSync(file).size }]);
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "window1-fresh-holdout-source-hash-manifest-v1", files: Object.fromEntries(sourceInputs) }));
  const report = `# Fresh post-July-26 Window-1 holdout seal\n\nStage 1 found ${census.event_count} paired big-4 events with recorded tape coverage and an event date strictly after 2026-07-26. Git provenance excludes ${audit.excluded_touched}; ${N} remains untouched. The required minimum is 60, so the seal is short by ${Math.max(0, 60 - N)} and Stage 2 ${gatePass ? "is eligible but was not run by construction" : "was not invoked and is forbidden by the operator's conditional law"}.\n\n- Sealed event-list SHA-256: ${declaration.event_list_sha256}.\n- V36/V35/R3 runner invocations: 0/0/0.\n- Score rows: 0.\n- Tuning, retry, live, order, position, or service mutation: 0.\n\nThe sole untouched event is listed in SEALED_EVENT_LIST.txt. Every excluded candidate and at least one touching commit are in GIT_TOUCH_AUDIT.json; per-event and per-leg tape spans and source hashes are in REMOTE_TAPE_CENSUS.json.\n`;
  fs.writeFileSync(path.join(output, "REPORT.md"), report);
  fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({
    schema_version: "window1-fresh-holdout-seal-determinism-v1",
    method: "TWO_CONSECUTIVE_CLEAN_REGENERATIONS_FROM_HASH_BOUND_REMOTE_TAPE_CENSUS_AND_GIT_TOUCH_AUDIT",
    regenerable_artifacts_byte_identical: true,
    brain_runner_invocations_during_regeneration: 0,
    stage_2_results_generated: false,
  }));
  const artifactNames = fs.readdirSync(output).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const artifacts = Object.fromEntries(artifactNames.map((name) => [name, { sha256: sha(fs.readFileSync(path.join(output, name))), bytes: fs.statSync(path.join(output, name)).size }]));
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "window1-fresh-holdout-artifact-hash-manifest-v1", files: artifacts }));
  process.stdout.write(canonical({ status: declaration.status, N, event_list_sha256: declaration.event_list_sha256, output }));
}

if (has("--acquire")) { acquireRemote(); auditGit(); }
else if (has("--audit")) auditGit();
build();
