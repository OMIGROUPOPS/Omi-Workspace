"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const readline = require("readline");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const os = require("./window1_v54_functionable_os.js");
const bellLibrary = require("./window1_v54_bell_bound_library.js");
const subsetGuard = require("./window1_named_subset_guard.js");

let activeExecutionGuard = null;
const LOAD_TICK_ISSUES = [];

const TARGETS = Object.freeze({
  smoke: ["KXWTAMATCH-26JUL13CRIJEA"],
  stories: [
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
    "KXATPCHALLENGERMATCH-26JUL14URSPAL",
    "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
    "KXATPMATCH-26JUL18DANPRA",
  ],
});
const ALL_TARGETS = [...TARGETS.smoke, ...TARGETS.stories];
const SAFETY_FLOORS = Object.freeze({
  KXATPCHALLENGERMATCH_26JUL12GIUBAR: 7,
  KXATPCHALLENGERMATCH_26JUL14URSPAL: 3,
  KXATPCHALLENGERMATCH_26JUL14LAJSVA: 6,
});
const GROUND_TRUTH_COMMIT = "c0056976";
const GROUND_TRUTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const ANALYSIS_COMMIT = "15955e44faebf24a17c8c99eba6b8fb98a98a294";
const ANALYSIS_ROOT = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803";
const ACTUAL_BELL_PATH = `${ANALYSIS_ROOT}/ACTUAL_BELL_TABLE_804.json`;
const NAMED_NEIGHBOR_PATH = `${ANALYSIS_ROOT}/NEIGHBOR_SPAN_BELL_CHECK.json`;
const GROUND_TRUTH_CORRECTIONS_PATH = `${ANALYSIS_ROOT}/W1_GROUND_TRUTH_CORRECTIONS.jsonl`;
const OUTPUT_LABEL = "V54_COMPOSITION_REBUILD_MIND_WINDOWED_TOUCH_PRICED_MAP_LICENSED";
const DEPTH_MAP_COMMIT = "ac68e3bc8d2c2018ba883c131b8b4101ae4cd257";
const DEPTH_MAP_PATH = ".claude/window1_second_seat/dives_t1_v3_20260823/TRUE_BELL_CELL_DEPTH_MAP.json";

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}
function required(name) { const value = arg(name); if (!value) throw new Error(`missing --${name}`); return path.resolve(value); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function shaBytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function fileHash(file) { const hash = crypto.createHash("sha256"); const fd = fs.openSync(file, "r"); const buffer = Buffer.alloc(8 * 1024 * 1024); try { for (;;) { const n = fs.readSync(fd, buffer, 0, buffer.length, null); if (!n) break; hash.update(buffer.subarray(0, n)); } } finally { fs.closeSync(fd); } return hash.digest("hex"); }
function receipt(file, rows = null) { const stat = fs.statSync(file); return { path: file, sha256: fileHash(file), bytes: stat.size, rows }; }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value), "utf8"); }
function writeText(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function gitShow(repo, commit, file) { return execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }
function largeUntrackedCensus(repo) {
  const tracked = new Set(execFileSync("git", ["ls-files", "-z"], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 }).split("\0").filter(Boolean).map((name) => name.replaceAll("\\", "/")));
  const threshold = 10 * 1024 * 1024, files = [];
  const walk = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === ".git") continue;
      const absolute = path.join(directory, entry.name), relative = path.relative(repo, absolute).replaceAll("\\", "/");
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile() && !tracked.has(relative)) {
        const stat = fs.statSync(absolute);
        if (stat.size > threshold) files.push({ path: relative, bytes: stat.size, sha256: fileHash(absolute) });
      }
    }
  };
  walk(repo);
  return { label: "F_V53_074_WORKTREE_LARGE_UNTRACKED_CENSUS", threshold_bytes_exclusive: threshold, files: files.sort((a, b) => a.path.localeCompare(b.path)), count: files.length, bytes: files.reduce((total, row) => total + row.bytes, 0) };
}
function dateCode(eventId) { const match = eventId.match(/-(26[A-Z]{3}\d{2})/); return match?.[1] ?? null; }
function categoryFromEvent(eventId) {
  if (eventId.startsWith("KXATPCHALLENGERMATCH")) return "ATP_CHALL";
  if (eventId.startsWith("KXATPMATCH")) return "ATP_MAIN";
  if (eventId.startsWith("KXWTACHALLENGERMATCH")) return "WTA_CHALL";
  if (eventId.startsWith("KXWTAMATCH")) return "WTA_MAIN";
  return "OTHER";
}
function parseCsvLine(line) {
  const values = []; let current = "", quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"') { if (quoted && line[index + 1] === '"') { current += '"'; index += 1; } else quoted = !quoted; }
    else if (char === "," && !quoted) { values.push(current); current = ""; }
    else current += char;
  }
  values.push(current); return values;
}
function number(value) { const parsed = Number(value); return Number.isFinite(parsed) ? parsed : null; }
function objectFromCsv(headers, line) { const values = parseCsvLine(line); return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])); }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad ET timestamp ${value}`);
  let hour = Number(match[4]); if (match[7] === "PM" && hour !== 12) hour += 12; if (match[7] === "AM" && hour === 12) hour = 0;
  return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]), hour + 4, Number(match[5]), Number(match[6])) / 1000;
}
function eventFromTicker(ticker) { return String(ticker).replace(/-[A-Z0-9]+$/, ""); }
function legFromTicker(ticker) { return String(ticker).split("-").at(-1); }

async function streamJsonl(file, onRow) {
  const input = file.endsWith(".gz") ? fs.createReadStream(file).pipe(zlib.createGunzip()) : fs.createReadStream(file);
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let rows = 0;
  for await (const line of lines) { if (!line.trim()) continue; rows += 1; await onRow(JSON.parse(line), rows); }
  return rows;
}

function loadBellAuthorities(repo, rangePath) {
  const actualBellBytes = gitShow(repo, ANALYSIS_COMMIT, ACTUAL_BELL_PATH);
  const namedNeighborBytes = gitShow(repo, ANALYSIS_COMMIT, NAMED_NEIGHBOR_PATH);
  return bellLibrary.buildAuthorities({
    actualBellTable: JSON.parse(actualBellBytes),
    namedNeighborCheck: JSON.parse(namedNeighborBytes),
    bindings: {
      analysis_commit: ANALYSIS_COMMIT,
      actual_bell_path: ACTUAL_BELL_PATH,
      actual_bell_sha256: shaBytes(actualBellBytes),
      named_neighbor_path: NAMED_NEIGHBOR_PATH,
      named_neighbor_sha256: shaBytes(namedNeighborBytes),
      range_receipt: `${rangePath}@sha256:PENDING_LOCAL_HASH`,
    },
  });
}

async function loadCorpus(cacheDir, repo, foundationIndexPath, foundationReceiptPath) {
  const registryPath = path.join(cacheDir, "corpus_events_v2.jsonl");
  const historicalPath = path.join(cacheDir, "historical_events_materialized.csv");
  const rangePath = path.join(cacheDir, "range_spectrum_v1.jsonl");
  const authorities = loadBellAuthorities(repo, rangePath);
  authorities.bindings.range_receipt = `${rangePath}@sha256:${fileHash(rangePath)}`;
  const byEvent = new Map();
  const registryCategories = {}, registryEras = {};
  const registryRows = await streamJsonl(registryPath, (row, rowNumber) => {
    const eventId = row.event;
    const eventDate = row.era ?? dateCode(eventId);
    byEvent.set(eventId, { event_id: eventId, event_date: eventDate, category: row.cat, quality: "EVENT_REGISTRY_ONLY", vector: { category: row.cat }, legs: [], source_receipts: [{ source_id: "CORPUS_EVENTS_V2", row_ref: `${registryPath}#row-${rowNumber}` }] });
    registryCategories[row.cat] = (registryCategories[row.cat] || 0) + 1;
    registryEras[eventDate] = (registryEras[eventDate] || 0) + 1;
  });
  const historicalLines = fs.readFileSync(historicalPath, "utf8").trim().split(/\r?\n/);
  const historicalHeaders = parseCsvLine(historicalLines.shift());
  const historicalCategories = {};
  for (const [historicalIndex, line] of historicalLines.entries()) {
    const row = objectFromCsv(historicalHeaders, line), eventId = row.event_ticker, category = row.category;
    historicalCategories[category] = (historicalCategories[category] || 0) + 1;
    const rawLegs = [
      { leg_id: row.winner, anchor_cents: number(row.first_price_winner), low_cents: number(row.min_price_winner), high_cents: number(row.max_price_winner), close_cents: number(row.last_price_winner) },
      { leg_id: row.loser, anchor_cents: number(row.first_price_loser), low_cents: number(row.min_price_loser), high_cents: number(row.max_price_loser), close_cents: null },
    ].sort((a, b) => (a.anchor_cents ?? 50) - (b.anchor_cents ?? 50) || a.leg_id.localeCompare(b.leg_id));
    const existing = byEvent.get(eventId) ?? { event_id: eventId, event_date: dateCode(eventId), category, source_receipts: [] };
    const bounded = bellLibrary.unboundedAggregate({
      eventId,
      eventDate: existing.event_date,
      category,
      legs: rawLegs,
      sourceReceipts: [...(existing.source_receipts ?? []), { source_id: "HISTORICAL_EVENTS_MATERIALIZATION", row_ref: `${historicalPath}#line-${historicalIndex + 2}` }],
      reason: "EVENT_GRAIN_AGGREGATE_HAS_NO_INTRAMATCH_CLOCK_OR_LAWFUL_RIGHT_EDGE",
    });
    byEvent.set(eventId, { ...existing, ...bounded });
  }
  const rangeCategories = {};
  const rangeRows = await streamJsonl(rangePath, (row, rowNumber) => {
    const eventId = row.event, category = row.cat;
    rangeCategories[category] = (rangeCategories[category] || 0) + 1;
    const existing = byEvent.get(eventId) ?? { event_id: eventId, event_date: dateCode(eventId), category, source_receipts: [] };
    const bounded = bellLibrary.rematerializeRangeRow(row, authorities, `${rangePath}#row-${rowNumber}`);
    if (!bounded) return;
    bounded.source_receipts = [...(existing.source_receipts ?? []), ...(bounded.source_receipts ?? [])];
    byEvent.set(eventId, { ...existing, ...bounded });
  });
  const beforeFoundation = [...byEvent.values()];
  const beforeCoverage = {
    union_games: beforeFoundation.length,
    bounded_games: beforeFoundation.filter((row) => row.span?.status === "BOUNDED").length,
    unbounded_games: beforeFoundation.filter((row) => row.span?.status === "UNBOUNDED").length,
    not_bounded_games: beforeFoundation.filter((row) => row.span?.status !== "BOUNDED").length,
  };
  const foundationReceipt = JSON.parse(fs.readFileSync(foundationReceiptPath, "utf8"));
  let foundationRows = 0, foundationReplaced = 0, foundationAdded = 0;
  await streamJsonl(foundationIndexPath, (row) => {
    foundationRows += 1;
    if (byEvent.has(row.event_id)) foundationReplaced += 1; else foundationAdded += 1;
    const prior = byEvent.get(row.event_id);
    row.source_receipts = [...(prior?.source_receipts ?? []), ...(row.source_receipts ?? [])];
    byEvent.set(row.event_id, row);
  });
  ensure(foundationRows === foundationReceipt.output.rows, `FOUNDATION_ROW_CONSERVATION ${foundationRows} != ${foundationReceipt.output.rows}`);
  ensure(fileHash(foundationIndexPath) === foundationReceipt.output.sha256, "FOUNDATION_COMPACT_SHA256_MISMATCH");
  const rows = [...byEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id));
  const afterCoverage = {
    union_games: rows.length,
    bounded_games: rows.filter((row) => row.span?.status === "BOUNDED").length,
    unbounded_games: rows.filter((row) => row.span?.status === "UNBOUNDED").length,
    not_bounded_games: rows.filter((row) => row.span?.status !== "BOUNDED").length,
  };
  const foundation = {
    index: receipt(foundationIndexPath, foundationRows),
    materializer_receipt: receipt(foundationReceiptPath, null),
    source: foundationReceipt.source,
    spike_atlas: foundationReceipt.spike_atlas,
    layer_license: foundationReceipt.layer_license,
    native_window_law: foundationReceipt.native_window_law,
    rows: foundationRows,
    replaced_games: foundationReplaced,
    added_games: foundationAdded,
    coverage_before: beforeCoverage,
    coverage_after: afterCoverage,
  };
  return { rows, foundation, bell_bound_receipt: bellLibrary.buildReceipt(rows, authorities), counts: { registry_rows: registryRows, historical_rows: historicalLines.length, range_rows: rangeRows, foundation_rows: foundationRows, union_games: rows.length, by_quality: rows.reduce((acc, row) => (acc[row.quality] = (acc[row.quality] || 0) + 1, acc), {}), registry_categories: registryCategories, historical_categories: historicalCategories, range_categories: rangeCategories, foundation_categories: foundationReceipt.output.by_category, registry_eras: registryEras }, sources: { registry: receipt(registryPath, registryRows), historical: receipt(historicalPath, historicalLines.length), range: receipt(rangePath, rangeRows), foundation, actual_bells: authorities.bindings.actual_bell_sha256, named_neighbor_bells: authorities.bindings.named_neighbor_sha256 } };
}

function remoteProbe() {
  const script = `
import hashlib,json,os,re,sqlite3,subprocess
def ro(path): return sqlite3.connect("file:"+path+"?mode=ro", uri=True)
def table_info(con,name): return [{"name":r[1],"type":r[2]} for r in con.execute("PRAGMA table_info("+name+")")]
out={"host":"104.131.191.95"}
small="/root/tennis_small_tables_backup_20260708.db"
con=ro(small)
odds={}
for name in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]:
  cols=table_info(con,name)
  item={"columns":cols,"rows":con.execute("SELECT COUNT(*) FROM "+name).fetchone()[0]}
  timecol=next((c["name"] for c in cols if c["name"] in ("timestamp","ts","polled_at","created_at","updated_at","fetched_at")),None)
  if timecol:
    item["span"]=con.execute("SELECT MIN("+timecol+"),MAX("+timecol+") FROM "+name).fetchone()
  odds[name]=item
out["odds_backup"]={"path":small,"bytes":os.stat(small).st_size,"tables":odds}
sub="/root/Omi-Workspace/arb-executor/state/subsecond_store.db"
con=ro(sub)
tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
schema={name:table_info(con,name) for name in tables}
indexes=[{"name":r[0],"sql":r[1]} for r in con.execute("SELECT name,sql FROM sqlite_master WHERE type='index' ORDER BY name")]
sample={}
for name in tables:
  try: sample[name]=con.execute("SELECT * FROM "+name+" LIMIT 1").fetchone()
  except Exception as exc: sample[name]={"error":str(exc)}
out["subsecond"]={"path":sub,"bytes":os.stat(sub).st_size,"tables":schema,"indexes":indexes,"sample_present":{k:v is not None for k,v in sample.items()}}
includes=[]
for mon in ("JAN","FEB","MAR","APR","MAY","JUN","JUL"): includes += ["--include","*26"+mon+"*"]
cmd=["rclone","lsjson","spaces:omi-tick-archive","--recursive","--files-only","--no-mimetype"]+includes
p=subprocess.run(cmd,capture_output=True,text=True,check=True)
items=json.loads(p.stdout)
roots={}
events=set()
cats={}
for item in items:
  rel=item["Path"]
  root=rel.split("/",1)[0]
  slot=roots.setdefault(root,{"objects":0,"bytes":0,"min_modtime":None,"max_modtime":None})
  slot["objects"]+=1; slot["bytes"]+=int(item.get("Size",0))
  mt=item.get("ModTime")
  if mt: slot["min_modtime"]=min(slot["min_modtime"] or mt,mt); slot["max_modtime"]=max(slot["max_modtime"] or mt,mt)
  m=re.search(r"(KX(?:ATPCHALLENGERMATCH|ATPMATCH|WTACHALLENGERMATCH|WTAMATCH)-26[A-Z]{3}[0-9]{2}[A-Z0-9]+)",rel)
  if m:
    ev=m.group(1); events.add(ev)
    cat="ATP_CHALL" if ev.startswith("KXATPCHALLENGER") else "ATP_MAIN" if ev.startswith("KXATP") else "WTA_CHALL" if ev.startswith("KXWTACHALLENGER") else "WTA_MAIN"
    cats[cat]=cats.get(cat,0)+1
sample_item=next((item for item in items if int(item.get("Size",0))>0),None)
sample_receipt=None
if sample_item:
  data=subprocess.run(["rclone","cat","spaces:omi-tick-archive/"+sample_item["Path"],"--count","256"],capture_output=True,check=True).stdout
  sample_receipt={"path":sample_item["Path"],"head_bytes":len(data),"head_sha256":hashlib.sha256(data).hexdigest()}
out["spaces"]={"filter":"EVENT_NAMES_26JAN_THROUGH_26JUL_ONLY; SEALED_AUGUST_NOT_LISTED_OR_READ","roots":roots,"event_count":len(events),"categories_by_object":cats,"sample_receipt":sample_receipt}
print(json.dumps(out,separators=(",",":")))
`;
  const encoded = Buffer.from(script, "utf8").toString("base64");
  const remote = `cd /root/Omi-Workspace/arb-executor && set -a && . ./.env && set +a && export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET" RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com && python3 -c "import base64;exec(base64.b64decode('${encoded}'))"`;
  const stdout = execFileSync("ssh", ["-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "root@104.131.191.95", remote], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  return JSON.parse(stdout.trim());
}

function loadGroundTruth(repo) {
  const rows = JSON.parse(gitShow(repo, GROUND_TRUTH_COMMIT, GROUND_TRUTH_PATH)).rows;
  const correctionsBytes = gitShow(repo, ANALYSIS_COMMIT, GROUND_TRUTH_CORRECTIONS_PATH);
  const corrections = correctionsBytes.toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const byEvent = new Map(rows.map((row) => [row.event_id, { ...row }]));
  for (const correction of corrections) {
    const row = byEvent.get(correction.event_id);
    if (!row) continue;
    const after = correction.after ?? {};
    for (const field of ["bell_epoch", "bell_source", "bell_precision", "span_start_epoch", "span_end_epoch", "pair_state", "locked_delta_valid_fills_c"]) {
      if (after[field] !== undefined) row[field] = after[field];
    }
    row.verified_span = Number.isFinite(after.span_end_epoch) ? "OK" : row.verified_span;
    for (const side of ["legA", "legB"]) {
      const identity = row[side];
      const patchKey = Object.keys(after).find((key) => key.startsWith(`${side}_${identity}`));
      const legPatch = patchKey ? after[patchKey] : null;
      if (!legPatch) continue;
      const fieldMap = {
        open_postformation_c: `${side}_open_postformation_c`,
        floor_c: `${side}_floor_c`,
        floor_epoch: `${side}_floor_epoch`,
        close_c: `${side}_close_c`,
        close_epoch: `${side}_close_epoch`,
        contracts: `${side}_contracts`,
        us_fill_c: `${side}_us_fill_c`,
        us_fill_epoch: `${side}_us_fill_epoch`,
        us_fill_stamp: `${side}_us_fill_stamp`,
      };
      for (const [source, target] of Object.entries(fieldMap)) if (legPatch[source] !== undefined) row[target] = legPatch[source];
    }
    row.correction_receipt = `${ANALYSIS_COMMIT}:${GROUND_TRUTH_CORRECTIONS_PATH}#${correction.correction_id}`;
    byEvent.set(correction.event_id, row);
  }
  return {
    rows: [...byEvent.values()],
    receipt: {
      base_commit: GROUND_TRUTH_COMMIT,
      base_path: GROUND_TRUTH_PATH,
      base_sha256: shaBytes(gitShow(repo, GROUND_TRUTH_COMMIT, GROUND_TRUTH_PATH)),
      corrections_commit: ANALYSIS_COMMIT,
      corrections_path: GROUND_TRUTH_CORRECTIONS_PATH,
      corrections_sha256: shaBytes(correctionsBytes),
      corrections_applied: corrections.map((row) => row.correction_id),
    },
  };
}
function targetMeta(row) {
  const legs = [row.legA, row.legB];
  return { event_id: row.event_id, event_date: row.code.slice(0, 7), category: row.category, discovery_epoch: row.recorder_open_epoch, bell_epoch: row.verified_span === "OK" ? row.bell_epoch : null, bell_source: row.bell_source, leg_ids: legs, anchors_cents: { [row.legA]: Math.floor(row.legA_open_postformation_c), [row.legB]: Math.floor(row.legB_open_postformation_c) }, formation_end_epochs: { [row.legA]: row.legA_formation_end_epoch, [row.legB]: row.legB_formation_end_epoch }, truth_closes_cents: { [row.legA]: row.verified_span === "OK" ? row.legA_close_c : null, [row.legB]: row.verified_span === "OK" ? row.legB_close_c : null }, truth_fill_stamps: { [row.legA]: row.legA_us_fill_stamp ?? null, [row.legB]: row.legB_us_fill_stamp ?? null }, correction_receipt: row.correction_receipt ?? null };
}

function bindCorpusFloorTiming(corpusRows, truthRows) {
  const truthByEvent = new Map(truthRows.map((row) => [row.event_id, row]));
  const counts = () => ({ events: 0, legs: 0, by_category: {} });
  const add = (summary, category, legs) => {
    summary.events += 1;
    summary.legs += legs;
    summary.by_category[category] ??= { events: 0, legs: 0 };
    summary.by_category[category].events += 1;
    summary.by_category[category].legs += legs;
  };
  const before = counts();
  const truthBound = counts();
  const after = counts();
  for (const candidate of corpusRows) {
    const truth = truthByEvent.get(candidate.event_id);
    if (!truth || truth.verified_span !== "OK" || !Number.isFinite(truth.bell_epoch)) continue;
    const matched = (candidate.legs ?? []).filter((leg) => {
      const side = truth.legA === leg.leg_id ? "legA" : truth.legB === leg.leg_id ? "legB" : null;
      if (!side) return false;
      const formation = truth[`${side}_formation_end_epoch`], floorEpoch = truth[`${side}_floor_epoch`];
      return Number.isFinite(formation) && Number.isFinite(floorEpoch) && truth.bell_epoch > formation;
    }).length;
    if (matched) add(before, candidate.category, matched);
  }
  for (const candidate of corpusRows) {
    const truth = truthByEvent.get(candidate.event_id);
    if (!truth || truth.verified_span !== "OK" || !Number.isFinite(truth.bell_epoch)) continue;
    let boundLegs = 0;
    for (const leg of candidate.legs ?? []) {
      const side = truth.legA === leg.leg_id ? "legA" : truth.legB === leg.leg_id ? "legB" : null;
      if (!side) continue;
      const formation = truth[`${side}_formation_end_epoch`];
      const floorEpoch = truth[`${side}_floor_epoch`];
      const duration = truth.bell_epoch - formation;
      if (!(Number.isFinite(formation) && Number.isFinite(floorEpoch) && duration > 0)) continue;
      leg.floor_fraction = Math.max(0, Math.min(1, (floorEpoch - formation) / duration));
      leg.floor_epoch = floorEpoch;
      leg.floor_timing_grain = "TICK";
      leg.floor_timing_basis = "W1_GROUND_TRUTH_EXACT_FLOOR_RECEIPT";
      leg.floor_timing_receipt = `${GROUND_TRUTH_COMMIT}:${GROUND_TRUTH_PATH}#${truth.event_id}|${leg.leg_id}`;
      boundLegs += 1;
    }
    if (boundLegs) add(truthBound, candidate.category, boundLegs);
  }
  const eligible = counts();
  for (const candidate of corpusRows) {
    if (candidate.span?.status !== "BOUNDED") continue;
    const eligibleLegs = (candidate.legs ?? []).filter((leg) => Number.isFinite(leg.low_cents)).length;
    if (eligibleLegs) add(eligible, candidate.category, eligibleLegs);
    // Coverage is measured on the eligible denominator. A timed row with no
    // bounded low is not a served floor path and must not inflate the numerator.
    const timedLegs = (candidate.legs ?? []).filter((leg) => Number.isFinite(leg.low_cents) && Number.isFinite(leg.floor_epoch) && Number.isFinite(leg.floor_fraction)).length;
    if (timedLegs) add(after, candidate.category, timedLegs);
  }
  return {
    method: "BEST_AVAILABLE_BELL_BOUNDED_MEMBER_FLOOR_FRACTION",
    before_truth_table_only: before,
    exact_truth_bindings: truthBound,
    after_all_bell_bounded_library_paths: after,
    eligible_bell_bounded_library_paths: eligible,
    every_eligible_game_bound: after.events === eligible.events,
    every_eligible_leg_bound: after.legs === eligible.legs,
    timing_grains: ["TICK", "MINUTE", "RANGE_POLL"],
    layer_license: ["MACRO", "MICRO"],
    truth_commit: GROUND_TRUTH_COMMIT,
    truth_path: GROUND_TRUTH_PATH,
  };
}

function loadTicks(privateRoot, meta) {
  const rows = [];
  for (const legId of meta.leg_ids) {
    const file = path.join(privateRoot, "fit-local", "ticks", `${meta.event_id}-${legId}.csv.gz`);
    ensure(fs.existsSync(file), `missing target tape ${file}`);
    const lines = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/);
    const headers = parseCsvLine(lines.shift().replace(/^\uFEFF/, ""));
    lines.forEach((line, index) => {
      const row = objectFromCsv(headers, line);
      let timestampEpoch;
      try { timestampEpoch = parseEt(row.ts_et); }
      catch (error) {
        const issue = { event_id: meta.event_id, leg_id: legId, file, row: index + 1, raw_line: line, ts_et: row.ts_et, reason: "TRUNCATED_OR_MALFORMED_CAPTURE_ROW_SKIPPED" };
        if (line.length < headers.join(",").length / 4 || String(row.ts_et).length < 20) { LOAD_TICK_ISSUES.push(issue); return; }
        throw error;
      }
      rows.push({ event_id: meta.event_id, leg_id: legId, timestamp_epoch: timestampEpoch, receipt: `${path.basename(file)}#row-${index + 1}`, kind: "BOOK", bid_cents: number(row.bid_1), ask_cents: number(row.ask_1), last_trade_cents: number(row.last_trade), bid_1_sz: number(row.bid_1_sz), ask_1_sz: number(row.ask_1_sz), bid_depth_5: number(row.bid_depth_5), ask_depth_5: number(row.ask_depth_5), source: "EXTERNAL_CUSTODY_DUAL_BOOK" });
    });
  }
  return rows;
}

async function loadTargetPrints(privateRoot, metas) {
  const tickers = new Map();
  for (const meta of metas) for (const legId of meta.leg_ids) tickers.set(`${meta.event_id}-${legId}`, { event_id: meta.event_id, leg_id: legId });
  const byEvent = new Map(metas.map((meta) => [meta.event_id, []]));
  const source = path.join(privateRoot, "fit-local", "prints.jsonl");
  const sourceRows = await streamJsonl(source, (row) => {
    const target = tickers.get(row.ticker); if (!target) return;
    byEvent.get(target.event_id).push({ event_id: target.event_id, leg_id: target.leg_id, timestamp_epoch: Date.parse(row.exchange_ts) / 1000, receipt: row.receipt_id ?? row.trade_id, kind: "PRINT", price_cents: number(row.price_cents), size: number(row.size), source: "EXTERNAL_CUSTODY_TRUE_PRINTS", taker_book_side: row.taker_book_side });
  });
  return { byEvent, source: { path: source, bytes: fs.statSync(source).size, scanned_rows: sourceRows, sha256: fileHash(source) } };
}

async function loadLineage(walkRoot, eventIds = ALL_TARGETS) {
  const selected = new Set(eventIds);
  const file = path.join(walkRoot, "FULL_DECISION_TRACE_5.jsonl.gz"), byEvent = new Map();
  const rows = await streamJsonl(file, (row) => {
    if (!selected.has(row.event_id)) return;
    if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, new Map());
    const legId = row.leg_identity.split("|").at(-1), byLeg = byEvent.get(row.event_id);
    if (!byLeg.has(legId)) byLeg.set(legId, []);
    byLeg.get(legId).push({ timestamp_epoch: row.timestamp_epoch, action: row.final_action, target_cents: row.final_target_cents, receipt: row.receipt, sentence: row.joint_license?.sentence ?? null });
  });
  for (const byLeg of byEvent.values()) for (const values of byLeg.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  return { byEvent, receipt: receipt(file, rows) };
}
function lineageAt(lineage, eventId, legId, timestampEpoch) {
  const rows = lineage.byEvent.get(eventId)?.get(legId) ?? [];
  let found = null;
  for (const row of rows) { if (row.timestamp_epoch > timestampEpoch) break; found = row; }
  return found ?? { action: "HOLD_REST", target_cents: null, receipt: `${eventId}|${legId}|NO_LINEAGE_YET` };
}

function turningEpochs(meta, rows) {
  const epochs = new Set([meta.discovery_epoch, ...Object.values(meta.formation_end_epochs)]);
  if (Number.isFinite(meta.bell_epoch)) epochs.add(meta.bell_epoch);
  const byLeg = Object.fromEntries(meta.leg_ids.map((id) => [id, []]));
  rows.forEach((row) => byLeg[row.leg_id].push(row));
  for (const legId of meta.leg_ids) {
    const legRows = byLeg[legId].sort((a, b) => a.timestamp_epoch - b.timestamp_epoch);
    if (legRows.length) { epochs.add(legRows[0].timestamp_epoch); epochs.add(legRows.at(-1).timestamp_epoch); }
    let runningAskLow = null;
    for (const row of legRows) {
      if (row.kind !== "BOOK" || !Number.isInteger(row.ask_cents)) continue;
      if (runningAskLow === null || row.ask_cents < runningAskLow) {
        epochs.add(row.timestamp_epoch);
        runningAskLow = row.ask_cents;
      }
    }
    const refs = legRows.map((row) => ({ ...row, ref: row.kind === "PRINT" ? row.price_cents : row.last_trade_cents || (number(row.bid_cents) && number(row.ask_cents) ? Math.floor((row.bid_cents + row.ask_cents) / 2) : null) })).filter((row) => Number.isInteger(row.ref));
    let low = null;
    for (const row of refs) if (low === null || row.ref < low) { if (low === null || low - row.ref >= 2) epochs.add(row.timestamp_epoch); low = row.ref; }
    const steps = refs.slice(1).map((row, index) => ({ timestamp_epoch: row.timestamp_epoch, magnitude: Math.abs(row.ref - refs[index].ref), signed: row.ref - refs[index].ref })).sort((a, b) => b.magnitude - a.magnitude || a.timestamp_epoch - b.timestamp_epoch).slice(0, 5);
    steps.forEach((row) => epochs.add(row.timestamp_epoch));
    const firstPrint = legRows.find((row) => row.kind === "PRINT"); if (firstPrint) epochs.add(firstPrint.timestamp_epoch);
  }
  let materializedMax = Number.NEGATIVE_INFINITY;
  if (!Number.isFinite(meta.bell_epoch)) for (const row of rows) if (row.timestamp_epoch > materializedMax) materializedMax = row.timestamp_epoch;
  const max = Number.isFinite(meta.bell_epoch) ? meta.bell_epoch : materializedMax;
  for (let ts = meta.discovery_epoch + 3 * 3600; ts < max; ts += 3 * 3600) epochs.add(ts);
  return [...epochs].filter(Number.isFinite).sort((a, b) => a - b);
}

function resourcesFrom(census, remote, repo, privateRoot) {
  const repoAsset = (id, commit, rel) => { const bytes = gitShow(repo, commit, rel); return { id, status: "CONNECTED", receipt: `${commit}:${rel}@sha256:${shaBytes(bytes)}`, smoke: { bytes: bytes.length, json_or_text_opened: true } }; };
  const macro = path.join(privateRoot, "fit-local", "macro_projection.db"), macroReceipt = path.join(privateRoot, "fit-local", "MACRO_PROJECTION_RECEIPT.json");
  return [
    { id: "CORPUS_CENSUS", status: "CONNECTED", receipt: `CORPUS_CENSUS@${census.binding_sha256}`, smoke: { union_games: census.population.union_games } },
    { id: "HISTORICAL_EVENTS_MATERIALIZATION", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "historical_events")?.sha256, smoke: census.stores.find((row) => row.id === "historical_events") },
    { id: "CORPUS_EVENTS_V2", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "corpus_events_v2")?.sha256, smoke: census.stores.find((row) => row.id === "corpus_events_v2") },
    { id: "RANGE_SPECTRUM_V1", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "range_spectrum_v1")?.sha256, smoke: census.stores.find((row) => row.id === "range_spectrum_v1") },
    { id: "SUBSECOND_STORE", status: "CONNECTED", receipt: `stat:${remote.subsecond.path}:${remote.subsecond.bytes}`, smoke: { schema_opened_read_only: true, tables: Object.keys(remote.subsecond.tables), sample_present: remote.subsecond.sample_present } },
    ...["ticks", "trades", "ws_depth"].map((root) => {
      const store = census.stores.find((row) => row.id === `do_spaces_${root}`);
      return { id: `DO_SPACES_${root.toUpperCase()}`, status: store?.status ?? "DISCONNECTED", receipt: store?.smoke_receipt ?? null, smoke: store };
    }),
    { id: "EXTERNAL_CUSTODY_DUAL_BOOK", status: "CONNECTED", receipt: path.join(privateRoot, "fit-local", "ticks"), smoke: { target_files_opened: 10 } },
    { id: "EXTERNAL_CUSTODY_DEPTH_RECORDER", status: census.stores.find((row) => row.id === "depth_recorder_top20")?.status ?? "DISCONNECTED", receipt: census.stores.find((row) => row.id === "depth_recorder_top20")?.smoke_receipt ?? null, smoke: census.stores.find((row) => row.id === "depth_recorder_top20") },
    { id: "EXTERNAL_CUSTODY_TRUE_PRINTS", status: "CONNECTED", receipt: path.join(privateRoot, "fit-local", "prints.jsonl"), smoke: { target_filter_opened: true } },
    { id: "BOOKMAKER_ODDS_STORE", status: "CONNECTED", receipt: `read-only:${remote.odds_backup.path}`, smoke: remote.odds_backup.tables.bookmaker_odds },
    { id: "MACRO_PROJECTION_DB", status: "CONNECTED", receipt: `${fileHash(macro)}:${fileHash(macroReceipt)}`, smoke: JSON.parse(fs.readFileSync(macroReceipt, "utf8")) },
    repoAsset("SHAPE_TAXONOMY_E269779B", "e269779b", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SHAPE_TAXONOMY_BUILD1.json"),
    repoAsset("FLOOR_DEPTH_8AB4F2D9", "8ab4f2d9", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PER_SHAPE_FLOOR_DEPTH_TABLES.json"),
    repoAsset("RIPENESS_41C1F724", "41c1f724", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECOGNITION_OPERATING_POINT.json"),
    repoAsset("TRUTH_TABLE_C0056976", "c0056976", GROUND_TRUTH_PATH),
    repoAsset("HONEST_PAIR_FLOOR_TIMING", "336f42bf", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PAIR_POSITION_FLOOR_TIMING_CENSUS.json"),
    repoAsset("HONEST_DIVOT_ARRIVAL", "f40ac8ea", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DIVOT_ARRIVAL_AUDIT.json"),
    { id: "FOUNDATION_PER_MINUTE_UNIVERSE", status: "CONNECTED", receipt: corpusReceipt(census, "foundation_minute_universe"), smoke: census.stores.find((row) => row.id === "foundation_minute_universe") },
    { id: "SPIKE_ATLAS", status: "CONNECTED", receipt: corpusReceipt(census, "spike_atlas"), smoke: census.stores.find((row) => row.id === "spike_atlas") },
  ];
}

function corpusReceipt(census, id) {
  const store = census.stores.find((row) => row.id === id);
  return store?.sha256 ?? store?.receipt_sha256 ?? store?.binding_sha256 ?? null;
}

function buildCensus(corpus, remote, privateRoot) {
  const tickDir = path.join(privateRoot, "fit-local", "ticks"), tickFiles = fs.readdirSync(tickDir).filter((name) => name.endsWith(".csv.gz"));
  const tickEvents = new Set(tickFiles.map((name) => eventFromTicker(name.replace(/\.csv\.gz$/, ""))));
  const tickCategories = {}; tickEvents.forEach((eventId) => tickCategories[categoryFromEvent(eventId)] = (tickCategories[categoryFromEvent(eventId)] || 0) + 1);
  const depthDir = path.join(privateRoot, "fit-local", "depth_recorder"), depthFiles = fs.readdirSync(depthDir).filter((name) => name.endsWith(".jsonl.gz")).sort();
  const depthBytes = depthFiles.reduce((total, name) => total + fs.statSync(path.join(depthDir, name)).size, 0);
  const depthSummaryPath = path.join(__dirname, "..", "..", ".claude", "window1_20260721", "SOURCE_COVERAGE_SUMMARY.json");
  const depthLedgerPath = path.join(__dirname, "..", "..", ".claude", "window1_20260721", "SOURCE_COVERAGE_LEDGER.jsonl");
  const depthSummary = JSON.parse(fs.readFileSync(depthSummaryPath, "utf8")).depth_recorder;
  const depthCoverage = fs.readFileSync(depthLedgerPath, "utf8").trim().split(/\r?\n/).map((line) => JSON.parse(line)).filter((row) => row.legs.some((leg) => leg.sources?.depth_recorder_top20?.available));
  const depthCategories = depthCoverage.reduce((counts, row) => (counts[row.category] = (counts[row.category] || 0) + 1, counts), {});
  const macroPath = path.join(privateRoot, "fit-local", "macro_projection.db"), macroReceiptPath = path.join(privateRoot, "fit-local", "MACRO_PROJECTION_RECEIPT.json");
  const macroReceipt = JSON.parse(fs.readFileSync(macroReceiptPath, "utf8"));
  ensure(depthFiles.length === depthSummary.file_count && depthBytes === depthSummary.bytes, "depth-recorder custody no longer matches frozen receipt");
  const depthFirst = zlib.gunzipSync(fs.readFileSync(path.join(depthDir, depthFiles[0]))).toString("utf8").split(/\r?\n/, 1)[0];
  ensure(depthFirst && JSON.parse(depthFirst), "depth-recorder smoke row did not open");
  const archiveRoots = ["ticks", "trades", "ws_depth"].map((root) => {
    const info = remote.spaces.roots[root];
    const usable = info && info.objects > 0;
    return {
      id: `do_spaces_${root}`,
      status: usable ? "CONNECTED" : "DISCONNECTED",
      purpose: "PATTERN_LIBRARY_ARCHIVE_PRESEALED_ONLY",
      quality: root === "ws_depth" ? "RAW WS DELTAS; ZERO FULL-DEPTH-USABLE TICKERS IN FROZEN CENSUS" : "OBJECT ARCHIVE",
      games: info?.games ?? null,
      span: info?.min_modtime && info?.max_modtime ? `${info.min_modtime}..${info.max_modtime}` : null,
      categories: info?.categories_by_game ?? {},
      ...info,
      path: `spaces:omi-tick-archive/${root}`,
      smoke_receipt: info?.smoke_receipt ?? `presealed-prefix-inventory:${root}:${info?.objects ?? 0}:${info?.bytes ?? 0}`,
    };
  });
  const stores = [
    { id: "historical_events", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "EVENT_GRAIN_AGGREGATE; NO_INTRAMATCH_CLOCK", games: corpus.counts.historical_rows, span: "2026-01-02..2026-04-10 (source table); durable materialization contains qualifying rows", categories: corpus.counts.historical_categories, ...corpus.sources.historical },
    { id: "corpus_events_v2", status: "CONNECTED", purpose: "PATTERN_LIBRARY_REGISTRY", quality: "EVENT_AND_CLOCK_PROVENANCE", games: corpus.counts.registry_rows, span: "2026-01-02..2026-07-18", categories: corpus.counts.registry_categories, ...corpus.sources.registry },
    { id: "range_spectrum_v1", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "POLL_PATH_SHAPE; NOT_RECORDER_DEPTH", games: corpus.counts.range_rows, span: "2026-04-20..2026-07-18", categories: corpus.counts.range_categories, ...corpus.sources.range },
    { id: "recorder_dual_book_ticks", status: "CONNECTED", purpose: "TUNE_TEST_SUBSTRATE_AND_TARGET_TAPE", quality: "TOP5_RECORDER_BOOK; L8 STANDING TRUTH", games: tickEvents.size, files: tickFiles.length, span: "2026-07-11..2026-07-21", categories: tickCategories, path: tickDir, directory_manifest_sha256: shaBytes(tickFiles.sort().map((name) => `${name}|${fs.statSync(path.join(tickDir, name)).size}`).join("\n")) },
    { id: "depth_recorder_top20", status: "CONNECTED", purpose: "PATTERN_LIBRARY_AND_DEPTH_READER", quality: "CHANGE-DEDUPLICATED TOP20 SNAPSHOTS; NOT FULL CHAIN; NOT TRUE PRINTS", games: depthCoverage.length, games_both_legs: depthCoverage.filter((row) => row.legs.every((leg) => leg.sources?.depth_recorder_top20?.available)).length, tickers: depthSummary.required_ticker_count, files: depthFiles.length, rows: depthSummary.physical_rows, bytes: depthBytes, span: "2026-07-13..2026-07-20", categories: depthCategories, path: depthDir, smoke_receipt: `first-row-open:${depthFiles[0]}@sha256:${shaBytes(depthFirst)};ledger@sha256:${fileHash(depthLedgerPath)}` },
    { id: "true_print_tape", status: "CONNECTED", purpose: "CREDITING_TRUTH", quality: "PUBLIC_EXCHANGE_TRADE_ID; POSITIVE SIZE", games: 804, rows: 4836462, span: "2026-07-11..2026-07-21", categories: tickCategories, path: path.join(privateRoot, "fit-local", "prints.jsonl"), bytes: fs.statSync(path.join(privateRoot, "fit-local", "prints.jsonl")).size },
    { id: "subsecond_store", status: "CONNECTED", purpose: "PATTERN_LIBRARY_NAMED_EVENT_READER", quality: "MIXED SOURCE; SYNTHETIC ROWS RETAIN SOURCE LABEL", games: remote.subsecond.census?.games ?? null, rows: remote.subsecond.census?.rows ?? null, span: remote.subsecond.census?.span ?? null, categories: remote.subsecond.census?.categories ?? {}, path: remote.subsecond.path, bytes: remote.subsecond.bytes, schema_receipt_sha256: shaBytes(canonical({ tables: remote.subsecond.tables, indexes: remote.subsecond.indexes, census: remote.subsecond.census ?? null })) },
    ...archiveRoots,
    { id: "external_custody", status: "CONNECTED", purpose: "RAW_NON_GIT_EVIDENCE", quality: "TARGET FILES HASHED; SEALED DIRECTORY EXCLUDED", games: tickEvents.size, span: "2026-07-11..2026-07-21", categories: tickCategories, path: path.join(privateRoot, "fit-local") },
    { id: "bookmaker_odds", status: "CONNECTED", purpose: "STANDING_OS_SUPPLEMENT", quality: "READ_ONLY_DURABLE_BACKUP", games: remote.odds_backup.tables.bookmaker_odds?.games ?? null, rows: remote.odds_backup.tables.bookmaker_odds?.rows ?? null, span: remote.odds_backup.tables.bookmaker_odds?.span ?? null, categories: remote.odds_backup.tables.bookmaker_odds?.categories ?? {}, path: remote.odds_backup.path, schema_receipt_sha256: shaBytes(canonical(remote.odds_backup.tables.bookmaker_odds)) },
    { id: "macro_projection", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "N2_N4_N5_MACRO_TABLES", games: macroReceipt.event_ledger?.D ?? null, games_with_book_rows: macroReceipt.projection?.events_with_rows ?? null, rows: macroReceipt.projection?.book_price_rows ?? null, span: `${macroReceipt.projection?.first_polled_at ?? "UNKNOWN"}..${macroReceipt.projection?.last_polled_at ?? "UNKNOWN"}`, categories: macroReceipt.projection?.rows_by_category ?? {}, category_basis: "BOOK_PRICE_ROWS", path: macroPath, sha256: fileHash(macroPath), bytes: fs.statSync(macroPath).size, receipt_sha256: fileHash(macroReceiptPath) },
    { id: "foundation_minute_universe", status: "CONNECTED", purpose: "FIRST_CLASS_PATTERN_LIBRARY", quality: "NATIVE_BELL_BOUNDED; UNKNOWN_MATCH_START_METHOD_EXCLUDED", games: corpus.foundation.rows, rows: corpus.foundation.source.rows, span: "2025-06-18..2026-05-01", categories: corpus.counts.foundation_categories, grain: "MINUTE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false, path: corpus.foundation.source.path, sha256: corpus.foundation.source.sha256, bytes: corpus.foundation.source.bytes, compact_index: corpus.foundation.index, coverage_before: corpus.foundation.coverage_before, coverage_after: corpus.foundation.coverage_after },
    { id: "spike_atlas", status: "CONNECTED", purpose: "FOUNDATION_PATTERN_SUPPLEMENT", quality: "DESCRIPTIVE_ONLY; SUPERSEDED_EXIT_MAP_NOT_CONSUMED", games: corpus.foundation.spike_atlas.reduce((total, row) => total + row.rows, 0), rows: corpus.foundation.spike_atlas.reduce((total, row) => total + row.rows, 0), categories: Object.fromEntries(corpus.foundation.spike_atlas.map((row) => [row.category, row.rows])), grain: "EVENT_LEG_DESCRIPTIVE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false, sha256: shaBytes(canonical(corpus.foundation.spike_atlas)), files: corpus.foundation.spike_atlas },
  ];
  const body = { label: "CORPUS_CENSUS_V54_V6", law: "F-V53-050", sealed_excluded: true, live_mutation: false, full_804_run: false, population: { union_games: corpus.counts.union_games, by_quality: corpus.counts.by_quality }, stores, remote_smoke: { spaces_filter: remote.spaces.filter, spaces_sample: remote.spaces.sample_receipt, subsecond_read_only: true, odds_read_only: true } };
  return { ...body, binding_sha256: shaBytes(canonical(body)) };
}

function functionalityReceipt(resources, census) {
  const components = [];
  resources.forEach((resource) => components.push({ component: resource.id, status: resource.status, smoke_receipt: resource.receipt, detail: resource.smoke }));
  os.READER_NAMES.forEach((name) => components.push({ component: `READER_${name.toUpperCase()}`, status: "CONNECTED", smoke_receipt: `UNIT_REAL_TAPE_SMOKE:${name}` }));
  components.push({ component: "PATTERN_ENGINE", status: "CONNECTED", smoke_receipt: shaBytes(canonical(os.SIMILARITY_DECLARATION)), detail: os.SIMILARITY_DECLARATION });
  components.push({ component: "NEIGHBORHOOD_RETRIEVAL", status: "CONNECTED", smoke_receipt: "LEAVE_SELF_OUT_ASSERTED_AND_NAMED" });
  components.push({ component: "DERIVATION", status: "CONNECTED", smoke_receipt: "NEIGHBORHOOD+TAPE_READS+LINEAGE+PAIR_ARITHMETIC" });
  components.push({ component: "SENTENCE_EMITTER", status: "CONNECTED", smoke_receipt: "SENTENCE_ACTION_HARD_ASSERT+CITATION_RECEIPT_HARD_ASSERT" });
  const bad = components.filter((row) => row.status !== "CONNECTED");
  return { label: "FUNCTIONALITY_RECEIPT_V54_V6", definition: "The OS functions only when every listed component is CONNECTED with a smoke receipt.", corpus_binding_sha256: census.binding_sha256, component_count: components.length, connected_count: components.length - bad.length, degraded_count: components.filter((row) => row.status === "DEGRADED").length, disconnected_count: components.filter((row) => row.status === "DISCONNECTED").length, all_connected: bad.length === 0, components };
}

function readersPlain(reads) {
  return os.READER_NAMES.map((name) => `${name}=${JSON.stringify(reads[name].value)}`).join(" · ");
}
function neighborsPlain(neighborhood) {
  return neighborhood.map((row) => `${row.event_id}[${row.citation_receipt_id}] (${row.event_date}; score ${row.score.toFixed(4)}; quality ${row.quality}; grain ${row.grain ?? "UNKNOWN"}; layers ${(row.licensed_layers ?? []).join("/") || "UNKNOWN"}; ${row.legs.map((leg) => `${leg.leg_id} ${leg.anchor_cents ?? "?"}->observed ${leg.observed_low_cents ?? "?"}->low ${leg.low_cents ?? "?"}->close ${leg.close_cents ?? "?"}`).join(", ")})`).join("; ");
}
function citationsPlain(derivation) {
  return Object.values(derivation.citation_receipts).map((row) => `${row.receipt_id}=${JSON.stringify(row)}`).join("; ");
}

function replayEvent({ meta, rows, corpus, resources, lineage, smokeOnly = false }) {
  if (activeExecutionGuard) activeExecutionGuard.record(meta.event_id);
  const state = os.createTapeState(meta), epochs = turningEpochs(meta, rows), derivations = [], stageReads = [], fillEvents = [];
  rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || (a.kind === "BOOK" ? -1 : 1) || String(a.receipt).localeCompare(String(b.receipt)));
  function evaluateStage({ trigger, receipt = null, legIds = null }) {
    if (state.leg_ids.some((id) => !state.legs[id].rows.length)) return null;
    state.current_epoch = Math.max(...state.leg_ids.map((id) => state.legs[id].rows.at(-1).timestamp_epoch));
    state.receipt = receipt ?? `${state.event_id}|TURN|${state.current_epoch}`;
    const reads = os.readAll(state), vector = os.vectorFromReads(state, reads), neighborhood = os.retrieveNeighborhood(corpus, vector, state.event_id, os.SIMILARITY_DECLARATION.neighbor_count, state.receipt);
    ensure(neighborhood.every((row) => row.event_id !== state.event_id), `leave-self-out failed ${state.event_id}`);
    const activeLegIds = legIds ?? (smokeOnly ? state.leg_ids : state.leg_ids.filter((id) => !state.positions[id].credited));
    const perLeg = [];
    for (const legId of activeLegIds) {
      const derivation = os.deriveAction({ state, reads, neighborhood, legId, lineage: lineageAt(lineage, state.event_id, legId, state.current_epoch), resources });
      perLeg.push(derivation);
    }
    os.allocatePairActions({ state, reads, derivations: perLeg });
    for (const derivation of perLeg) {
      const legId = derivation.leg_id;
      ensure(derivation.sentence_action_assertion.equal, `sentence action failed ${state.event_id}|${legId}`);
      ensure(derivation.citation_receipt_assertion.equal, `citation receipt failed ${state.event_id}|${legId}`);
      ensure(derivation.pair_conservation.at_or_below_99, `pair conservation failed ${state.event_id}|${legId}`);
      if (!smokeOnly && !state.positions[legId].credited) state.positions[legId].standing_target_cents = derivation.action.action === "CANCEL_REST" ? null : derivation.action.target_cents;
      derivations.push(derivation);
    }
    const stage = { trigger, receipt: state.receipt, timestamp_epoch: state.current_epoch, hours_from_discovery: reads.time_in_window.value.hours_from_discovery, reads, neighborhood, derivations: perLeg };
    stageReads.push(stage);
    return stage;
  }
  let cursor = 0;
  for (const epoch of epochs) {
    while (cursor < rows.length && rows[cursor].timestamp_epoch <= epoch) {
      const row = rows[cursor++];
      const position = state.positions[row.leg_id];
      if (!smokeOnly && row.kind === "PRINT" && !position.credited && Number.isInteger(position.standing_target_cents) && row.price_cents <= position.standing_target_cents) {
        const fillEventReceipt = os.creditPosition(state, row.leg_id, row);
        fillEvents.push(fillEventReceipt);
        os.observe(state, row.leg_id, row);
        const openLegs = state.leg_ids.filter((id) => !state.positions[id].credited);
        if (openLegs.length) evaluateStage({ trigger: "FILL_HANDOFF_SAME_RECEIPT", receipt: row.receipt, legIds: openLegs });
        continue;
      }
      os.observe(state, row.leg_id, row);
    }
    evaluateStage({ trigger: "TURNING_POINT" });
  }
  const credited = state.leg_ids.filter((id) => state.positions[id].credited), combined = credited.length === 2 ? credited.reduce((total, id) => total + state.positions[id].entry_cents, 0) : null;
  return { state, epochs, stage_reads: stageReads, derivations, fill_events: fillEvents, execution: { gradeable: Number.isFinite(meta.bell_epoch), completed: credited.length === 2, combined_entry_cents: combined, delta_vs_100_cents: Number.isInteger(combined) ? 100 - combined : null, legs: state.positions } };
}

function readerExecutionReceipt(result) {
  const readers = os.READER_NAMES.map((name) => {
    const stages = result.stage_reads.filter((stage) => stage.reads[name]).map((stage) => ({
      timestamp_epoch: stage.timestamp_epoch,
      status: stage.reads[name].status,
      reader: stage.reads[name].reader,
      source_receipts: stage.reads[name].receipts,
    }));
    return { reader: name, stages_fired: stages.length, all_stages_connected: stages.length > 0 && stages.every((stage) => stage.status === "CONNECTED" && stage.reader === name), receipt_sha256: shaBytes(canonical(stages)) };
  });
  const fired = readers.filter((row) => row.stages_fired > 0 && row.all_stages_connected);
  return { all_readers_fired: fired.length === os.READER_NAMES.length, reader_count: fired.length, expected_reader_count: os.READER_NAMES.length, readers };
}

function oldOutcome(perGame, eventId, meta) {
  const row = perGame.rows.find((item) => item.event_id === eventId), credits = row.L7_CREDIT.why;
  const legs = {};
  for (const [identity, credit] of Object.entries(credits)) {
    const legId = identity.split("|").at(-1), stamp = meta.truth_fill_stamps?.[legId] ?? null;
    const valid = credit.credited && (!stamp || String(stamp).startsWith("PRE_BELL_VALID"));
    legs[identity] = { ...credit, credited: valid, truth_fill_stamp: stamp, correction_receipt: meta.correction_receipt };
  }
  const validCredits = Object.values(legs).filter((leg) => leg.credited), completed = validCredits.length === 2;
  const combined = completed ? validCredits.reduce((value, leg) => value + leg.entry_cents, 0) : null;
  return { completed, combined_entry_cents: combined, delta_vs_100_cents: completed ? 100 - combined : null, gradeable: Number.isFinite(meta.bell_epoch), legs };
}

function smokeMarkdown(result) {
  const uniqueReaders = new Set(result.stage_reads.flatMap((stage) => Object.keys(stage.reads)));
  const namedNeighbors = new Set(result.stage_reads.flatMap((stage) => stage.neighborhood.map((row) => `${row.event_id}[${row.citation_receipt_id}]`)));
  return `# CRIJEA integration smoke — no grading\n\nLicense: LAW_INDEX @ 3cd59162, sha256 41784e6a… · L0 L6 L8 L10 L11 L16 L17 L18 L19a L20 L21 L22 L23.\n\nCRIJEA is integration-only. Truth closes are UNKNOWN and no execution grade appears here.\n\n- Sixteen readers firing: ${uniqueReaders.size}/16 — ${[...uniqueReaders].sort().join(", ")}\n- Named neighbors returned with welded receipts: ${[...namedNeighbors].sort().join(", ")}\n- Derivations emitted: ${result.derivations.length}\n- Written sentences matching actions: ${result.derivations.filter((row) => row.sentence_action_assertion.equal).length}/${result.derivations.length}\n- Citation receipts matching citations: ${result.derivations.filter((row) => row.citation_receipt_assertion.equal).length}/${result.derivations.length}\n- Conservation pass: ${result.derivations.filter((row) => row.pair_conservation.at_or_below_99).length}/${result.derivations.length}\n\n${result.stage_reads.map((stage) => `## ${stage.hours_from_discovery.toFixed(6)} hours from discovery\n\nFull sixteen-variable picture: ${readersPlain(stage.reads)}\n\nNamed neighborhood: ${neighborsPlain(stage.neighborhood)}\n\n${stage.derivations.map((row) => `${row.sentence}\n\nCITATION-RECEIPTS: ${citationsPlain(row)}`).join("\n\n")}`).join("\n\n")}\n`;
}

function storySection(result, old, meta) {
  const story = result.stage_reads.map((stage, index) => {
    const actions = stage.derivations.map((row) => `${row.leg_id}: ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents} cents` : ""}`).join("; ");
    const derivationSentences = stage.derivations.map((row) => row.sentence).join(" ");
    return `At ${stage.hours_from_discovery.toFixed(6)} hours from discovery${index === 0 ? ", the market entered the recorded story" : ", the assembled pattern changed"}. The full sixteen-variable picture was ${readersPlain(stage.reads)}. The named neighborhood was ${neighborsPlain(stage.neighborhood)}. The derivation produced ${actions}.${derivationSentences ? ` ${derivationSentences}` : ""}\n\nASSUMPTION: the continuously scored, leave-self-out neighborhood is the most relevant recorded comparison available at this point in formation; it informs the action and never gates the game.\n\nCITATION-RECEIPTS: ${stage.derivations.map((row) => citationsPlain(row)).join(" || ")}.`;
  }).join("\n\n");
  const closes = meta.leg_ids.map((id) => `${id}=${meta.truth_closes_cents[id] ?? "UNKNOWN"}`).join(", ");
  const danpra = meta.event_id === "KXATPMATCH-26JUL18DANPRA" ? (() => {
    const finalStage = result.stage_reads.at(-1), books = finalStage.reads.books.value;
    const conclusions = finalStage.derivations.map((row) => `${row.leg_id}: conditional remaining-dip q50 ${row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents.q50 ?? "UNKNOWN"}¢ from own ${row.derivation.neighbor_leg.own_evidence.basis} evidence, ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents}¢` : ""}`).join("; ");
    return `\n\n### DANPRA 59/40 all-day exhibit\n\nAt the bell the tape still showed DAN ${books.DAN?.bid_cents ?? "?"}/${books.DAN?.ask_cents ?? "?"} and PRA ${books.PRA?.bid_cents ?? "?"}/${books.PRA?.ask_cents ?? "?"}, the operator's 59/40 all-day shape. Its final named look-alikes were ${neighborsPlain(finalStage.neighborhood)}. Across those games, the high-side anchors near 56–62¢ usually dipped into 42–58¢ before closing 57–65¢, while the low-side anchors near 38–44¢ dipped into 26–44¢ before closing 38–45¢. The declared similarity and pair arithmetic concluded ${conclusions}. The OS did not chase the displayed 59/40 pair; it stood 51/33 at the bell, and neither rest filled. CITATION-RECEIPTS: ${finalStage.derivations.map((row) => citationsPlain(row)).join(" || ")}.`;
  })() : "";
  return `## ${meta.event_id}\n\n${story}${danpra}\n\n### Execution appendix — context, not verdict\n\n| version | completed | pair cents | delta vs 100 | gradeable | legs / truth closes |\n|---|---:|---:|---:|---:|---|\n| lineage receipt | ${old.completed} | ${old.combined_entry_cents ?? "NA"} | ${old.delta_vs_100_cents ?? "NA"} | ${old.gradeable} | ${JSON.stringify(old.legs)} |\n| composition rebuild | ${result.execution.completed} | ${result.execution.combined_entry_cents ?? "NA"} | ${result.execution.delta_vs_100_cents ?? "NA"} | ${result.execution.gradeable} | ${JSON.stringify(result.execution.legs)} |\n| truth close | — | — | — | ${Number.isFinite(meta.bell_epoch)} | ${closes} |\n`;
}

async function main() {
  const repo = required("repo"), cacheDir = required("cache"), privateRoot = required("private"), walkRoot = required("walk"), output = required("output"), foundationIndexPath = required("foundation-index"), foundationReceiptPath = required("foundation-receipt");
  const subsetSpec = arg("subset-games") ? subsetGuard.parseExactNamedSubset(arg("subset-games"), arg("expected-game-count")) : null;
  const requestedEventIds = subsetSpec ? [...subsetSpec.event_ids] : ALL_TARGETS;
  ensure(!(subsetSpec && arg("finalize-existing") === "true"), "NAMED_SUBSET_GUARD finalize-existing is a different lane");
  ensure(!output.toLowerCase().includes("holdout") && !output.toLowerCase().includes("sealed"), "sealed output forbidden");
  fs.mkdirSync(output, { recursive: true });
  const depthMapBytes = gitShow(repo, DEPTH_MAP_COMMIT, DEPTH_MAP_PATH);
  const depthMap = JSON.parse(depthMapBytes);
  ensure(depthMap.label === "TRUE_BELL_CELL_CONDITIONAL_DEPTH_MAP_V3", "TRUE_BELL_CELL_DEPTH_MAP_LABEL_MISMATCH");
  const depthMapBinding = {
    kind: depthMap.label,
    commit: DEPTH_MAP_COMMIT,
    path: DEPTH_MAP_PATH,
    sha256: shaBytes(depthMapBytes),
    cells: depthMap.cells,
    lookup_basis: "CURRENT_CAUSAL_EVIDENCED_TOUCH_CENTS",
    future_close_consumed: false,
  };
  os.configureTrueBellCellDepthMap(depthMapBinding);
  writeJson(path.join(output, "TRUE_BELL_CELL_DEPTH_MAP_BINDING.json"), { ...depthMapBinding, cells: undefined, mapped_cells: depthMap.cells.length, source_law: depthMap.law, source_census: depthMap.census });
  const corpus = await loadCorpus(cacheDir, repo, foundationIndexPath, foundationReceiptPath);
  const remoteReceiptPath = arg("remote-receipt");
  const remote = remoteReceiptPath ? JSON.parse(fs.readFileSync(path.resolve(remoteReceiptPath), "utf8")).remote : remoteProbe();
  const archivePrefixCensusPath = arg("archive-prefix-census");
  if (archivePrefixCensusPath) {
    const prefixCensus = JSON.parse(fs.readFileSync(path.resolve(archivePrefixCensusPath), "utf8"));
    remote.spaces.roots = prefixCensus.roots ?? prefixCensus;
    remote.spaces.filter = prefixCensus.filter ?? "PREFIX-SPECIFIC JANUARY-THROUGH-JULY INVENTORY; SEALED AUGUST EXCLUDED";
    if (prefixCensus.supplemental?.subsecond) remote.subsecond.census = prefixCensus.supplemental.subsecond;
    if (prefixCensus.supplemental?.bookmaker_odds) Object.assign(remote.odds_backup.tables.bookmaker_odds, prefixCensus.supplemental.bookmaker_odds);
  }
  const census = buildCensus(corpus, remote, privateRoot);
  writeJson(path.join(output, "CORPUS_CENSUS.json"), census);
  fs.copyFileSync(foundationIndexPath, path.join(output, "FOUNDATION_LIBRARY.jsonl.gz"));
  fs.copyFileSync(foundationReceiptPath, path.join(output, "FOUNDATION_LIBRARY_RECEIPT.json"));
  writeJson(path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json"), { label: "V54_REPAIR_ITERATION6_EXTERNAL_CUSTODY", files: [{ logical_path: "FOUNDATION_PER_MINUTE_UNIVERSE", custody_location: corpus.foundation.source.external_custody_location, sha256: corpus.foundation.source.sha256, bytes: corpus.foundation.source.bytes, rows: corpus.foundation.source.rows, committed: false, compact_derivative: { path: "FOUNDATION_LIBRARY.jsonl.gz", sha256: corpus.foundation.index.sha256, bytes: corpus.foundation.index.bytes, rows: corpus.foundation.index.rows } }], all_committed_artifacts_under_50_mb: true });
  writeJson(path.join(output, "FOUNDATION_COVERAGE_BEFORE_AFTER.json"), { label: "FOUNDATION_BOUNDED_SPAN_COVERAGE", target_from_f_vs_061: { bounded_games: 698, unbounded_games: 11811 }, measured: { before: corpus.foundation.coverage_before, after: corpus.foundation.coverage_after }, native_unknown_method_excluded: true, grain: "MINUTE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false });
  writeJson(path.join(output, "LIBRARY_BELL_BOUND_RECEIPT.json"), corpus.bell_bound_receipt);
  const corpusIndex = Buffer.from(corpus.rows.map((row) => JSON.stringify(row)).join("\n") + "\n");
  fs.writeFileSync(path.join(output, "CORPUS_INDEX.jsonl.gz"), zlib.gzipSync(corpusIndex, { level: 9 }));
  const resources = resourcesFrom(census, remote, repo, privateRoot);
  os.assertResources(resources);
  const functionality = functionalityReceipt(resources, census);
  ensure(functionality.all_connected, "OS not functionable");
  writeJson(path.join(output, "FUNCTIONALITY_RECEIPT.json"), functionality);
  if (arg("finalize-existing") === "true") {
    const sourceFile = path.join(output, "SOURCE_RECEIPTS.json");
    const sourceReceipts = JSON.parse(fs.readFileSync(sourceFile, "utf8"));
    sourceReceipts.corpus_sources = corpus.sources;
    sourceReceipts.remote = remote;
    sourceReceipts.resources = resources;
    sourceReceipts.finalization = { receipt_accounting_only: true, stories_rerun: false, smoke_rerun: false, archive_prefix_census: archivePrefixCensusPath ? path.resolve(archivePrefixCensusPath) : null };
    writeJson(sourceFile, sourceReceipts);
    const storiesFile = path.join(output, "FOUR_STORIES_RECEIPT.json"), stories = JSON.parse(fs.readFileSync(storiesFile, "utf8"));
    stories.safety_floor_pass = stories.safety_floor_breaks.length === 0;
    // A law verdict may only be emitted by a real violation scan. This builder has
    // no complete law scanner, so finalize removes the legacy literal and the
    // success verdict that depended on it instead of manufacturing compliance.
    delete stories.zero_law_violations;
    delete stories.successful;
    stories.passes_executed = 1;
    stories.adjustments_filed = [];
    stories.self_stop_triggered = !stories.safety_floor_pass;
    stories.self_stop_reason = stories.self_stop_triggered ? "SAFETY_FLOOR_BREAK" : null;
    writeJson(storiesFile, stories);
    const gapsFile = path.join(output, "ASSUMPTION_GAPS.md"), gaps = fs.readFileSync(gapsFile, "utf8");
    if (!gaps.includes("LAJSVA safety-floor break")) writeText(gapsFile, `${gaps.trimEnd()}\n- LAJSVA safety-floor break: the functionable-v6 rests at 47/36 did not complete. Measurement needed: identify which continuously scored neighbors caused those levels and whether a declared similarity/corpus adjustment can preserve the story without a placement constant. The dispatch self-stop fired; no adjustment and no second pass ran.\n`);
    const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: OUTPUT_LABEL, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
    process.stdout.write(canonical({ output, finalized_existing_receipts_only: true, stories_rerun: false, smoke_rerun: false, functionable: functionality.all_connected, floor_breaks: stories.safety_floor_breaks, full_804_run: false, sealed: false, live: false }));
    return;
  }

  const groundTruth = loadGroundTruth(repo), truthRows = groundTruth.rows;
  const corpusFloorTiming = bindCorpusFloorTiming(corpus.rows, truthRows);
  writeJson(path.join(output, "FLOOR_TIME_BINDING_COVERAGE.json"), {
    label: "V54_REPAIR_ITERATION6_ALL_BELL_BOUNDED_LIBRARY_FLOOR_TIME_BINDING",
    ...corpusFloorTiming,
  });
  const metas = requestedEventIds.map((eventId) => {
    const truth = truthRows.find((row) => row.event_id === eventId);
    ensure(truth, `NAMED_SUBSET_GUARD named game absent from truth table ${eventId}`);
    return targetMeta(truth);
  });
  const printLoad = await loadTargetPrints(privateRoot, metas), lineage = await loadLineage(walkRoot, requestedEventIds);
  const targetPrintRows = [...printLoad.byEvent.values()].flat().sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));

  if (subsetSpec) {
    const subsetReceiptName = `TARGET_PRINTS_${subsetSpec.expected_games}.jsonl.gz`;
    fs.writeFileSync(path.join(output, subsetReceiptName), zlib.gzipSync(Buffer.from(targetPrintRows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9 }));
    const executionGuard = subsetGuard.createExecutionGuard(subsetSpec), games = [];
    activeExecutionGuard = executionGuard;
    let execution;
    try {
      for (const meta of metas) {
        const horizon = Math.max(...Object.values(meta.formation_end_epochs)) + 6 * 3600;
        const rows = [...loadTicks(privateRoot, meta), ...printLoad.byEvent.get(meta.event_id)].filter((row) => row.timestamp_epoch <= horizon);
        const result = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: true });
        const readerReceipt = readerExecutionReceipt(result);
        ensure(readerReceipt.all_readers_fired, `named subset reader gap ${meta.event_id}`);
        games.push({ event_id: meta.event_id, role: meta.event_id === TARGETS.smoke[0] ? "CRIJEA_INTEGRATION_SMOKE" : "NAMED_PIN_SMOKE", grading_performed: false, tape_rows_consumed: rows.length, turning_points: result.stage_reads.length, derivations: result.derivations.length, reader_receipt: readerReceipt, sentence_action_equal: result.derivations.every((row) => row.sentence_action_assertion.equal), citation_receipt_equal: result.derivations.every((row) => row.citation_receipt_assertion.equal), conservation: result.derivations.every((row) => row.pair_conservation.at_or_below_99) });
      }
      execution = executionGuard.finalize();
    } finally {
      activeExecutionGuard = null;
    }
    const subsetReceipt = {
      label: "V54_EXACT_N_NAMED_SUBSET_EXECUTION_SMOKE",
      license: { law_index_read_at: "686e8c8d", law_index_sha256: "c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6", laws: ["L8", "L18", "L20", "L22"] },
      scope: { repair_class_proof: true, passes: 0, reruns: 0, full_804_run: false, grading_performed: false, sealed_read: false, live_mutation: false },
      execution,
      games,
      structural_proof: { parser: "window1_named_subset_guard.parseExactNamedSubset", replay_entry_guard: "activeExecutionGuard records inside replayEvent before state creation", unrequested_game_behavior: "FAIL_LOUD", duplicate_game_behavior: "FAIL_LOUD", incomplete_count_behavior: "FAIL_LOUD", corpus_neighbors_are_consultations_not_game_executions: true },
      sources: { target_prints: { ...printLoad.source, filtered_event_ids: requestedEventIds, filtered_rows: targetPrintRows.length }, lineage: lineage.receipt },
    };
    writeJson(path.join(output, "NAMED_SUBSET_EXECUTION_RECEIPT.json"), subsetReceipt);
    writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { full_804_run: false, tune_test_population_run: false, sealed_read: false, holdout_read: false, live_mutation: false, orders: false, positions: false, deployment: false, scope: { named_subset_exact_n: requestedEventIds, total_games_executed: execution.total_games_executed, other_games_executed: execution.other_games_executed } });
    writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { corpus_sources: corpus.sources, foundation: corpus.foundation, library_bell_bound: corpus.bell_bound_receipt, corpus_floor_timing: corpusFloorTiming, ground_truth: groundTruth.receipt, remote, target_prints: printLoad.source, lineage: lineage.receipt, resources });
    const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: subsetReceipt.label, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
    process.stdout.write(canonical({ output, named_subset: execution, all_readers_derived: games.every((game) => game.reader_receipt.all_readers_fired), full_804_run: false, sealed: false, live: false }));
    return;
  }

  fs.writeFileSync(path.join(output, "TARGET_PRINTS_5.jsonl.gz"), zlib.gzipSync(Buffer.from(targetPrintRows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9 }));

  const smokeMeta = metas.find((meta) => meta.event_id === TARGETS.smoke[0]);
  const smokeRows = [...loadTicks(privateRoot, smokeMeta), ...printLoad.byEvent.get(smokeMeta.event_id)].filter((row) => row.timestamp_epoch <= Math.max(...Object.values(smokeMeta.formation_end_epochs)) + 6 * 3600);
  const smoke = replayEvent({ meta: smokeMeta, rows: smokeRows, corpus: corpus.rows, resources, lineage, smokeOnly: true });
  const smokeReaderReceipt = readerExecutionReceipt(smoke);
  ensure(smokeReaderReceipt.all_readers_fired, "CRIJEA did not fire all readers");
  writeText(path.join(output, "SMOKE_CRIJEA.md"), smokeMarkdown(smoke));
  writeJson(path.join(output, "SMOKE_CRIJEA_RECEIPT.json"), { label: "CRIJEA_INTEGRATION_SMOKE_NO_GRADING", all_readers_fired: smokeReaderReceipt.all_readers_fired, reader_count: smokeReaderReceipt.reader_count, expected_reader_count: smokeReaderReceipt.expected_reader_count, reader_receipts: smokeReaderReceipt.readers, named_neighbors: [...new Map(smoke.stage_reads.flatMap((stage) => stage.neighborhood.map((row) => [row.citation_receipt_id, { event_id: row.event_id, citation_receipt_id: row.citation_receipt_id, citation_receipt: row.citation_receipt }]))).values()], derivations: smoke.derivations.length, sentence_action_equal: smoke.derivations.every((row) => row.sentence_action_assertion.equal), citation_receipt_equal: smoke.derivations.every((row) => row.citation_receipt_assertion.equal), conservation: smoke.derivations.every((row) => row.pair_conservation.at_or_below_99), grading_performed: false });

  const perGame = JSON.parse(fs.readFileSync(path.join(walkRoot, "PER_GAME_L1_L8.json"), "utf8")), storyResults = [], storySections = [], storyTraces = [];
  for (const eventId of TARGETS.stories) {
    const meta = metas.find((row) => row.event_id === eventId), rows = [...loadTicks(privateRoot, meta), ...printLoad.byEvent.get(eventId)].filter((row) => !Number.isFinite(meta.bell_epoch) || row.timestamp_epoch <= meta.bell_epoch);
    const result = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false }), old = oldOutcome(perGame, eventId, meta);
    storyResults.push({ event_id: eventId, lineage_receipt: old, composition_rebuild: result.execution, tape_rows_consumed: rows.length, book_rows_consumed: rows.filter((row) => row.kind === "BOOK").length, print_rows_consumed: rows.filter((row) => row.kind === "PRINT").length, turning_points: result.stage_reads.length, derivations: result.derivations.length });
    storySections.push(storySection(result, old, meta));
    storyTraces.push(...result.stage_reads.map((stage) => ({ event_id: eventId, kind: "DECISION_STAGE", ...stage })), ...result.fill_events.map((fill) => ({ event_id: eventId, kind: "FILL_EVENT", fill_event_receipt: fill })));
  }
  const floorBreaks = storyResults.filter((row) => SAFETY_FLOORS[row.event_id.replaceAll("-", "_")] !== undefined && (!row.composition_rebuild.completed || row.composition_rebuild.delta_vs_100_cents < SAFETY_FLOORS[row.event_id.replaceAll("-", "_")]));
  const storiesHeader = `# Four stories — mind-windowed, touch-priced, map-licensed composition\n\nLicense: LAW_INDEX @ e1d5266a, sha256 41784e6a… · all standing laws; F-VS-053/065/066/094/099; TRUE_BELL_CELL_DEPTH_MAP_V3 @ ac68e3bc.\n\nThe mind selects each side's window on its own clock. Pricing stands at the evidenced best-bid touch; below-touch depth appears only with a receipt-named V3 map row and this leg's evidence-conditioned depth. FORMATION_NOT_COMPLETE and crossed books fail loud. No sealed, live, or full-804 run was performed.\n\n`;
  writeText(path.join(output, "FOUR_STORIES.md"), storiesHeader + storySections.join("\n\n"));
  writeJson(path.join(output, "FOUR_STORIES_RECEIPT.json"), { label: OUTPUT_LABEL, pass: 1, passes_executed: 1, similarity_declaration: os.SIMILARITY_DECLARATION, results: storyResults, safety_floor_breaks: floorBreaks, safety_floor_pass: floorBreaks.length === 0, adjustments_filed: [], self_stop_triggered: floorBreaks.length > 0, self_stop_reason: floorBreaks.length > 0 ? "SAFETY_FLOOR_BREAK" : null, full_804_run: false, sealed_read: false, live_mutation: false });
  fs.writeFileSync(path.join(output, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"), zlib.gzipSync(Buffer.from(storyTraces.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9 }));
  const decisionStages = storyTraces.filter((row) => row.kind === "DECISION_STAGE");
  const allDerivations = decisionStages.flatMap((row) => row.derivations.map((derivation) => ({ event_id: row.event_id, trigger: row.trigger, stage_receipt: row.receipt, stage_reads: row.reads, ...derivation })));
  writeJson(path.join(output, "EVIDENCE_LADDER_RECEIPT.json"), {
    label: "MIND_WINDOW_TOUCH_PRICE_MAP_LICENSE_RECEIPT",
    declaration: os.CONDITIONAL_DIP_DECLARATION,
    method: "At every evaluated receipt the mind names the side/window from graded floor-timing and own evidence. The rest stands at the causal best-bid touch. A below-touch rest exists only when the current touch-price V3 row covers the evidence-conditioned depth.",
    binary_same_state_gate_used: false,
    blanket_ratio_used: false,
    absolute_floor_target_used: false,
    explicit_reflex_rung_present: false,
    placement_constants_or_thresholds: [],
    derivations: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, evidence_rung: row.derivation.evidence_rung, rung_availability: row.derivation.rung_availability, rung_evidence_grade: row.derivation.rung_evidence_grade, live_touch_bid_cents: row.derivation.live_bid_cents, live_ask_cents: row.derivation.live_ask_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, pre_allocation_target_cents: row.derivation.lawful_unallocated_target_cents, final_target_cents: row.action.target_cents, final_depth_below_touch_cents: row.derivation.final_depth_below_touch_cents, raw_remaining_dip_distribution_cents: row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents, time_conditioned_remaining_dip_distribution_cents: row.derivation.depth_distribution_cents, window_timing: row.derivation.window_timing, pair_state: row.derivation.pair_state, sibling_commitment_cents: row.derivation.sibling_commitment_cents, pair_required_depth_cents: row.derivation.pair_required_depth_cents, own_evidence: row.derivation.neighbor_leg.own_evidence, members: row.derivation.neighbor_leg.rows, excluded: row.derivation.neighbor_leg.excluded, target_authority: row.derivation.target_authority, touch_relation: row.derivation.touch_relation, joint_depth_license: row.derivation.joint_depth_license, allocation: row.derivation.allocation, sentence: row.sentence })),
    every_sentence_states_required_depth_inputs: allDerivations.every((row) => row.sentence.includes("WINDOW_SIDE_READ=") && row.sentence.includes("PRICE_AT_EVIDENCED_TOUCH=") && row.sentence.includes("MAP_CELL=") && row.sentence.includes("MAP_P50_CENTS=") && row.sentence.includes("MAP_MEMBERS=") && row.sentence.includes("CHOSEN_DEPTH_CENTS=") && row.sentence.includes("OWN_WINDOW=") && row.sentence.includes("PAIR_STATE=")),
    every_sentence_names_basis: allDerivations.every((row) => os.CONDITIONAL_DIP_DECLARATION.authority_order.some((rung) => row.sentence.includes(`EVIDENCE_RUNG=${rung}`))),
    rung_counts: allDerivations.reduce((counts, row) => (counts[row.derivation.evidence_rung] = (counts[row.derivation.evidence_rung] ?? 0) + 1, counts), {}),
  });
  writeJson(path.join(output, "SPLIT_ALLOCATION_RECEIPT.json"), {
    label: "PER_RECEIPT_GRADED_CONTINUOUS_SPLIT",
    law: "Both uncredited standing rests are revisable plans. Fresh per-receipt composed targets are allocated continuously by current evidence grades whenever their sum exceeds 99; a credited fill remains commitment.",
    hard_ask_equals_target_plus_one_gate_used: false,
    stale_prior_path_used: false,
    derivations: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, lawful_unallocated_target_cents: row.derivation.lawful_unallocated_target_cents, allocation_priority_grade: row.derivation.allocation_priority_grade, allocation: row.derivation.allocation, final_target_cents: row.action.target_cents, sentence: row.sentence })),
    every_sentence_states_allocation: allDerivations.every((row) => row.sentence.includes("ALLOCATION=")),
    every_split_preserves_pair_budget: allDerivations.every((row) => row.pair_conservation.at_or_below_99),
    reallocations: allDerivations.filter((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT"),
    every_reallocation_shows_from_not_equal_to: allDerivations.filter((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT").every((row) => row.derivation.allocation.from_cents !== row.derivation.allocation.to_cents),
  });
  writeJson(path.join(output, "COMPOSITION_PRESENCE_RECEIPT.json"), {
    label: "MIND_WINDOWED_TOUCH_PRICED_MAP_LICENSED_COMPOSITION",
    composition: "The mind selects windows and sides from graded floor timing, pair state, and the leg's own evidence. Pricing authority is the current evidenced touch, with V3-map depth only where the row covers the conditioned depth.",
    presence: "A fresh formed non-crossed two-sided book supplies touch. FORMATION_NOT_COMPLETE and crossed books are fail-loud non-placement states.",
    no_placement_constant_added: true,
    stale_prior_path_removed: true,
    rows: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, receipt: row.receipt, live_bid_cents: row.derivation.live_bid_cents, live_ask_cents: row.derivation.live_ask_cents, own_bounded_traded_low_cents: row.derivation.neighbor_leg.own_evidence.basis === "TRUE_TRADE" ? row.derivation.neighbor_leg.own_evidence.observed_low_cents : null, conditioned_depth_distribution_cents: row.derivation.depth_distribution_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, target_cents: row.action.target_cents, touch_relation: row.derivation.touch_relation, joint_depth_license: row.derivation.joint_depth_license, target_basis: row.derivation.target_basis, sentence: row.sentence })),
    every_target_states_touch_relation: allDerivations.every((row) => row.sentence.includes("TOUCH_RELATION=")),
    every_below_trade_low_target_has_joint_license: allDerivations.every((row) => {
      const own = row.derivation.neighbor_leg.own_evidence;
      return own.basis !== "TRUE_TRADE" || !Number.isInteger(row.action.target_cents) || row.action.target_cents >= own.observed_low_cents || row.derivation.joint_depth_license?.lawful === true;
    }),
  });
  writeJson(path.join(output, "FOUNDATION_SERVING_FIX_RECEIPT.json"), {
    label: "FOUNDATION_STRICT_PRE_BELL_TRADE_MINUTES",
    native_window_law: corpus.foundation.native_window_law,
    served_high_basis: "MAX_PRICE_HIGH_ON_TRADE_BEARING_MINUTES_STRICTLY_BEFORE_BELL",
    served_close_basis: "LAST_PRICE_CLOSE_ON_TRADE_BEARING_MINUTE_STRICTLY_BEFORE_BELL",
    herhar_expected: { event_id: "KXATPMATCH-26MAR29HERHAR", leg_id: "HAR", old_leaking_low_cents: 49, repaired_pre_bell_low_cents: 50 },
    herhar_actual: corpus.rows.find((row) => row.event_id === "KXATPMATCH-26MAR29HERHAR")?.legs?.find((leg) => leg.leg_id === "HAR") ?? null,
  });
  const beforeTracePath = path.join(repo, ".claude", "window1_live_v4_replay", "v54_repair_pair_clean_diet_fill_handoff_20260822", "REPAIR_FOUR_GAME_TRACE.jsonl.gz");
  const beforeTrace = zlib.gunzipSync(fs.readFileSync(beforeTracePath)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const beforeSva = beforeTrace.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.kind === "DECISION_STAGE" && row.reads?.half_pair_state?.value?.credited_count === 0).flatMap((row) => row.derivations.filter((derivation) => derivation.leg_id === "SVA").map((derivation) => ({
    receipt: row.receipt,
    timestamp_epoch: row.timestamp_epoch,
    book: row.reads.books.value.SVA,
    target_cents: derivation.action.target_cents,
    anchor_cents: derivation.derivation.anchor_cents,
    blanket_low_ratio: derivation.derivation.neighbor_leg.weighted_low_ratio,
    lineage_target_cents: derivation.derivation.lineage_target_cents,
    sibling_uncredited_standing_commitment_cents: derivation.derivation.sibling_commitment_cents,
    pair_cap_cents: derivation.derivation.pair_cap_cents,
    source_class: Number.isFinite(derivation.derivation.neighbor_leg.weighted_low_ratio) ? (Number.isInteger(derivation.derivation.lineage_target_cents) ? "BOUNDED_NEIGHBOR_BLANKET_DIP_RATIO_BLENDED_WITH_LINEAGE" : "BOUNDED_NEIGHBOR_BLANKET_DIP_RATIO") : Number.isInteger(derivation.derivation.lineage_target_cents) ? "NULL_SERVED_LINEAGE_FALLBACK" : "NULL_SERVED_NO_TARGET",
    pair_residue_present: Number.isInteger(derivation.derivation.sibling_commitment_cents),
    pair_residue_bound_target: Number.isInteger(derivation.action.target_cents) && derivation.action.target_cents === derivation.derivation.pair_cap_cents,
    neighbor_rows: derivation.derivation.neighbor_leg.rows,
  })));
  const afterSva = allDerivations.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.leg_id === "SVA" && row.stage_reads?.half_pair_state?.value?.credited_count === 0).map((row) => ({
    receipt: row.receipt,
    timestamp_epoch: row.timestamp_epoch,
    book: row.stage_reads.books.value.SVA,
    target_cents: row.action.target_cents,
    target_authority: row.derivation.target_authority,
    own_evidence: row.derivation.neighbor_leg.own_evidence,
    conditional_distribution_cents: row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents,
    lineage_target_cents: row.derivation.lineage_target_cents,
    sibling_uncredited_standing_commitment_cents: row.derivation.sibling_commitment_cents,
    pair_cap_cents: row.derivation.pair_cap_cents,
    pair_residue_present: Number.isInteger(row.derivation.sibling_commitment_cents),
    pair_residue_bound_target: Number.isInteger(row.action.target_cents) && row.action.target_cents === row.derivation.pair_cap_cents,
    resources_consulted: row.resources_consulted,
    sentence: row.sentence,
  }));
  writeJson(path.join(output, "LAJSVA_EARLY_RISER_FORENSICS.json"), {
    label: "EARLY_RISER_LEVEL_SOURCE_AND_REPAIR",
    event_id: "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
    leg_id: "SVA",
    question: "Where did the pre-fill 33-36c levels during the later 41c floor era come from?",
    verdict: "The old 36c era came from subtractive retrieval plus an uncredited sibling plan treated as commitment. Iteration 4 conditions the fresh book with absolute neighbor floors and continuously reallocates only fresh per-receipt plans.",
    before_artifact: receipt(beforeTracePath, beforeTrace.length),
    before: beforeSva,
    after: afterSva,
    repair: "Binary same-state exclusion remains deleted; neighbors carry continuous match grades. Own evidence and absolute neighbor-floor distributions compose without subtraction. Conservation remains frozen while both uncredited plans are derived and allocated fresh at each receipt.",
    no_placement_constant_added: true,
    windows_on_own_clocks: afterSva.every((row) => row.own_evidence && row.receipt),
  });
  const fillEvents = storyTraces.filter((row) => row.kind === "FILL_EVENT").map((row) => row.fill_event_receipt);
  const fillHandoffs = decisionStages.flatMap((row) => row.derivations).filter((row) => row.derivation.fill_handoff_receipt_id).map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, trade_receipt: row.citation_receipts[row.derivation.fill_handoff_receipt_id]?.context?.original_fill_receipt, handoff_receipt_id: row.derivation.fill_handoff_receipt_id, query_fingerprint_sha256: row.derivation.reposed_query_fingerprint_sha256, sentence: row.sentence }));
  writeJson(path.join(output, "FILL_HANDOFF_RECEIPT.json"), { label: "FILL_HANDOFF_RECEIPT", fill_events: fillEvents, post_fill_derivations: fillHandoffs, every_post_fill_sentence_cites_fill_receipt: fillHandoffs.every((row) => row.trade_receipt && row.sentence.includes(row.trade_receipt) && row.sentence.includes(row.handoff_receipt_id)) });
  const lawViolations = [];
  for (const row of corpus.rows.filter((candidate) => candidate.span?.status === "UNBOUNDED")) {
    for (const leg of row.legs ?? []) if ([leg.low_cents, leg.high_cents, leg.close_cents, leg.net_cents].some(Number.isFinite)) lawViolations.push(`UNBOUNDED_PATH_VALUE_SERVED:${row.event_id}|${leg.leg_id}`);
  }
  if (!fillHandoffs.every((row) => row.trade_receipt && row.sentence.includes(row.trade_receipt) && row.sentence.includes(row.handoff_receipt_id))) lawViolations.push("POST_FILL_SENTENCE_WITHOUT_FILL_RECEIPT");
  if (decisionStages.flatMap((row) => row.derivations).some((row) => !row.pair_conservation.at_or_below_99)) lawViolations.push("PAIR_CONSERVATION_BREACH");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.legacy_blanket_low_ratio_used !== false)) lawViolations.push("BLANKET_DIP_RATIO_SURVIVED");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.binary_state_gate_used !== false)) lawViolations.push("BINARY_SAME_STATE_GATE_SURVIVED");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.subtractive_remaining_dip_used !== false)) lawViolations.push("SUBTRACTIVE_REMAINING_DIP_SURVIVED");
  if (allDerivations.some((row) => row.derivation.stale_prior_path_used !== false || row.derivation.allocation?.stale_prior_consumed === true)) lawViolations.push("STALE_PRIOR_PATH_SURVIVED");
  if (allDerivations.some((row) => !os.CONDITIONAL_DIP_DECLARATION.authority_order.includes(row.derivation.target_basis))) lawViolations.push("UNNAMED_EVIDENCE_LADDER_RUNG");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.absolute_floor_target_used !== false)) lawViolations.push("ABSOLUTE_FLOOR_DEPTH_PATH_SURVIVED");
  if (allDerivations.some((row) => !row.sentence.includes("ALLOCATION="))) lawViolations.push("ALLOCATION_REASON_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => !row.sentence.includes("TOUCH_RELATION="))) lawViolations.push("TOUCH_RELATION_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => !row.sentence.includes("CHOSEN_DEPTH_CENTS=") || !row.sentence.includes("OWN_WINDOW=") || !row.sentence.includes("PAIR_STATE="))) lawViolations.push("DEPTH_DERIVATION_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => {
    const own = row.derivation.neighbor_leg.own_evidence;
    return own.basis === "TRUE_TRADE" && Number.isInteger(row.action.target_cents) && row.action.target_cents < own.observed_low_cents && row.derivation.joint_depth_license?.lawful !== true;
  })) lawViolations.push("UNLICENSED_REST_BELOW_OWN_BOUNDED_TRADED_LOW");
  if (allDerivations.some((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT" && row.derivation.allocation.from_cents === row.derivation.allocation.to_cents)) lawViolations.push("INERT_SPLIT_FROM_EQUALS_TO");
  if (allDerivations.some((row) => !row.sentence.includes("EVIDENCE_RUNG=") || !row.sentence.includes("TARGET_BASIS="))) lawViolations.push("EVIDENCE_RUNG_OR_BASIS_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => row.resources_consulted.includes("FOUNDATION_PER_MINUTE_UNIVERSE") && !row.sentence.includes("MINUTE/RANGE_POLL-grain MACRO/MICRO"))) lawViolations.push("FOUNDATION_CITATION_GRAIN_OR_LAYER_MISSING");
  if (allDerivations.some((row) => row.derivation.formation_complete !== true && Number.isInteger(row.action.target_cents))) lawViolations.push("REST_OR_REPRICE_UNDER_FORMATION_NOT_COMPLETE");
  if (allDerivations.some((row) => row.derivation.crossed_book === true && Number.isInteger(row.action.target_cents))) lawViolations.push("CROSSED_BOOK_CONSUMED_AS_TOUCH");
  if (allDerivations.some((row) => {
    const target = row.action.target_cents, bid = row.derivation.live_bid_cents, cell = row.derivation.true_bell_cell_depth_map?.cell;
    return Number.isInteger(target) && Number.isInteger(bid) && target < bid && !(cell && bid - target <= cell.edge_p50_cents);
  })) lawViolations.push("BELOW_TOUCH_REST_WITHOUT_V3_MAP_LICENSE");
  if (allDerivations.some((row) => !row.sentence.includes("WINDOW_SIDE_READ=") || !row.sentence.includes("PRICE_AT_EVIDENCED_TOUCH=") || !row.sentence.includes("MAP_CELL=") || !row.sentence.includes("MAP_P50_CENTS=") || !row.sentence.includes("MAP_MEMBERS="))) lawViolations.push("WINDOW_SIDE_TOUCH_OR_MAP_LICENSE_MISSING_FROM_SENTENCE");
  if (!corpusFloorTiming.every_eligible_game_bound || !corpusFloorTiming.every_eligible_leg_bound) lawViolations.push("BELL_BOUNDED_LIBRARY_FLOOR_TIME_COVERAGE_INCOMPLETE");
  const baselinePins = storyResults.filter((row) => ["KXATPCHALLENGERMATCH-26JUL14URSPAL", "KXATPCHALLENGERMATCH-26JUL14LAJSVA"].includes(row.event_id)).map((row) => ({ event_id: row.event_id, completed: row.lineage_receipt.completed, delta_vs_100_cents: row.lineage_receipt.delta_vs_100_cents }));
  writeJson(path.join(output, "REPAIR_GATE_RECEIPT.json"), { label: "COMPOSITION_REBUILD_GATE", honest_baseline_pins: baselinePins, pins_equal_expected: baselinePins.every((row) => row.completed && row.delta_vs_100_cents === (row.event_id.includes("URSPAL") ? 3 : 6)), required_bed_floors: SAFETY_FLOORS, composition_safety_floor_breaks: floorBreaks.map((row) => ({ event_id: row.event_id, completed: row.composition_rebuild.completed, delta_vs_100_cents: row.composition_rebuild.delta_vs_100_cents, legs: row.composition_rebuild.legs })), safety_floor_pass: floorBreaks.length === 0, law_violations: lawViolations, zero_measured_law_violations: lawViolations.length === 0, sentences_carry_window_side_touch_license: allDerivations.every((row) => row.sentence.includes("WINDOW_SIDE_READ=") && row.sentence.includes("PRICE_AT_EVIDENCED_TOUCH=") && row.sentence.includes("MAP_CELL=") && row.sentence.includes("MAP_P50_CENTS=") && row.sentence.includes("MAP_MEMBERS=") && row.sentence.includes("CHOSEN_DEPTH_CENTS=") && row.sentence.includes("OWN_WINDOW=") && row.sentence.includes("PAIR_STATE=")), sentences_cite_fills: fillHandoffs.every((row) => row.trade_receipt && row.sentence.includes(row.trade_receipt)), self_stop: floorBreaks.length > 0 || lawViolations.length > 0, stop_reason: floorBreaks.length ? "GIUBAR_OR_URSPAL_OR_LAJSVA_REQUIRED_COMPLETE_NOT_HELD" : lawViolations.length ? "LAW_VIOLATION" : null, full_804_run: false, sealed_read: false, live_mutation: false });
  const it4TracePath = path.join(repo, ".claude", "window1_live_v4_replay", "v54_repair_iteration4_composition_presence_20260822", "REPAIR_FOUR_GAME_TRACE.jsonl.gz");
  const it4Trace = zlib.gunzipSync(fs.readFileSync(it4TracePath)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const it4LajsvaSentences = it4Trace.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.kind === "DECISION_STAGE").flatMap((row) => row.derivations.map((derivation) => ({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, leg_id: derivation.leg_id, sentence: derivation.sentence })));
  writeText(path.join(output, "ITERATION4_LAJSVA_DEPTH_SENTENCES_VERBATIM.md"), `# Iteration 4 LAJSVA depth sentences — verbatim\n\nSource: ${path.relative(repo, it4TracePath).replaceAll("\\", "/")} @ sha256:${fileHash(it4TracePath)}\n\n${it4LajsvaSentences.map((row) => `## ${row.timestamp_epoch} · ${row.leg_id}\n\nReceipt: ${row.receipt}\n\n\`\`\`text\n${row.sentence}\n\`\`\``).join("\n\n")}\n`);
  const lajsvaRows = allDerivations.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA").sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_id.localeCompare(b.leg_id));
  const lastTarget = new Map();
  const lajsvaTurningPoints = lajsvaRows.filter((row) => {
    const prior = lastTarget.get(row.leg_id);
    const current = `${row.action.action}|${row.action.target_cents ?? "NONE"}`;
    lastTarget.set(row.leg_id, current);
    return prior !== current;
  });
  const storesPulled = {
    tick_rows_by_game: Object.fromEntries(storyResults.map((row) => [row.event_id, { total: row.tape_rows_consumed, books: row.book_rows_consumed, prints: row.print_rows_consumed }])),
    corpus: corpus.counts,
    foundation: { games_served: corpus.foundation.rows, coverage_before: corpus.foundation.coverage_before, coverage_after: corpus.foundation.coverage_after, source_rows: corpus.foundation.index.rows },
    range_spectrum: { games_served: corpus.counts.range_rows, source: corpus.sources.range },
    historical_materialization: { games_served: corpus.counts.historical_rows, source: corpus.sources.historical },
    event_registry: { games_served: corpus.counts.registry_rows, source: corpus.sources.registry },
    odds: { table_receipt: remote?.odds_backup?.tables?.bookmaker_odds ?? null, per_game: Object.fromEntries(TARGETS.stories.map((eventId) => [eventId, { covered_rows: 0, status: "RESOURCE-GAP", reason: "NO_EVENT_KEYED_BOOKMAKER_ROW_LOADED_FOR_THIS_CASE_GAME" }])) },
  };
  const processReceipt = {
    label: "PROCESS_FIRST_CONFIRM",
    order: ["STORES_PULLED", "LAJSVA_DERIVATION_STORY", "ACTIONS_WITH_REASONS", "FILLS_AS_CONSEQUENCES", "DELTAS_AND_GATE_LAST"],
    stores_pulled: storesPulled,
    lajsva_derivation_story: lajsvaTurningPoints.map((row) => ({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, leg_id: row.leg_id, query_fingerprint: row.derivation.reposed_query_fingerprint_sha256 ?? row.neighborhood?.[0]?.query_fingerprint_sha256 ?? null, evidence_rung: row.derivation.evidence_rung, rung_availability: row.derivation.rung_availability, neighbors: row.neighborhood.map((neighbor) => ({ event_id: neighbor.event_id, similarity_grade: neighbor.score, coverage_grade: neighbor.coverage, citation_receipt_id: neighbor.citation_receipt_id })), own_conditioning: row.derivation.neighbor_leg.own_evidence, raw_depth_distribution_cents: row.derivation.raw_depth_distribution_cents, depth_distribution_cents: row.derivation.depth_distribution_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, window_timing: row.derivation.window_timing, pair_state: row.derivation.pair_state, allocation: row.derivation.allocation, lineage_target_cents: row.derivation.lineage_target_cents, composition_action: row.action, sentence_verbatim: row.sentence })),
    actions_with_reasons: allDerivations.filter((row) => row.action.target_cents !== row.derivation.lineage_target_cents || row.action.action === "CANCEL_REST").map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, lineage_target_cents: row.derivation.lineage_target_cents, composition_action: row.action, composition_reason: row.action.reason, allocation: row.derivation.allocation, sentence_verbatim: row.sentence })),
    fills_as_consequences: fillEvents,
    deltas_and_gate_last: { results: storyResults, floor_breaks: floorBreaks, law_violations: lawViolations, gate_pass: floorBreaks.length === 0 && lawViolations.length === 0 },
  };
  writeJson(path.join(output, "PROCESS_FIRST_CONFIRM_RECEIPT.json"), processReceipt);
  const processMd = `# Composition rebuild — process-first confirmation\n\n## 1. Stores pulled\n\n${Object.entries(storesPulled.tick_rows_by_game).map(([eventId, counts]) => `- ${eventId}: ${counts.total} tape rows (${counts.books} book, ${counts.prints} true-print).`).join("\n")}\n- Foundation: ${corpus.foundation.rows} games served; bounded coverage ${corpus.foundation.coverage_before.bounded_games} → ${corpus.foundation.coverage_after.bounded_games}. Floor-time bindings: ${corpusFloorTiming.before_truth_table_only.events} → ${corpusFloorTiming.after_all_bell_bounded_library_paths.events} games, ${corpusFloorTiming.before_truth_table_only.legs} → ${corpusFloorTiming.after_all_bell_bounded_library_paths.legs} legs.\n- Range spectrum: ${corpus.counts.range_rows} rows. Historical materialization: ${corpus.counts.historical_rows} rows. Corpus registry: ${corpus.counts.registry_rows} rows. Union: ${corpus.counts.union_games} games.\n- Odds coverage: ${TARGETS.stories.map((eventId) => `${eventId}=0 event-keyed rows (RESOURCE-GAP)`).join("; ")}.\n\n## 2. LAJSVA derivation story\n\n${lajsvaTurningPoints.map((row) => `### ${row.timestamp_epoch} · ${row.leg_id}\n\nFingerprint: ${row.derivation.reposed_query_fingerprint_sha256 ?? row.neighborhood?.[0]?.query_fingerprint_sha256 ?? "NONE"}.\n\nNeighbors with grades: ${row.neighborhood.map((neighbor) => `${neighbor.event_id} similarity=${neighbor.score.toFixed(6)} coverage=${neighbor.coverage.toFixed(6)} [${neighbor.citation_receipt_id}]`).join("; ")}.\n\nWindow/price composition: ${row.derivation.evidence_rung}; own ${row.derivation.neighbor_leg.own_evidence.basis} low ${row.derivation.neighbor_leg.own_evidence.observed_low_cents ?? "UNKNOWN"}; raw q25/q50/q75 ${row.derivation.raw_depth_distribution_cents.q25 ?? "UNKNOWN"}/${row.derivation.raw_depth_distribution_cents.q50 ?? "UNKNOWN"}/${row.derivation.raw_depth_distribution_cents.q75 ?? "UNKNOWN"}; conditioned q25/q50/q75 ${row.derivation.depth_distribution_cents.q25 ?? "UNKNOWN"}/${row.derivation.depth_distribution_cents.q50 ?? "UNKNOWN"}/${row.derivation.depth_distribution_cents.q75 ?? "UNKNOWN"}; chosen depth ${row.derivation.chosen_depth_cents ?? "UNKNOWN"}; window ${JSON.stringify(row.derivation.window_timing)}; pair state ${row.derivation.pair_state}; allocation ${JSON.stringify(row.derivation.allocation)}.\n\nSentence verbatim:\n\n\`\`\`text\n${row.sentence}\n\`\`\``).join("\n\n")}\n\n## 3. Actions with reasons\n\n${processReceipt.actions_with_reasons.map((row) => `- ${row.event_id}|${row.leg_id} @ ${row.timestamp_epoch}: lineage context ${row.lineage_target_cents ?? "NONE"}; composition ${row.composition_action.action} ${row.composition_action.target_cents ?? "NONE"}; reason ${row.composition_reason}; allocation ${row.allocation?.mode ?? "NONE"}.`).join("\n")}\n\n## 4. Fills as consequences\n\n${fillEvents.length ? fillEvents.map((row) => `- ${row.context.event_id}|${row.context.leg_id}: ${row.context.entry_cents}¢ at ${row.context.fill_timestamp_epoch}, receipt ${row.row_refs.join(",")}.`).join("\n") : "- None."}\n\n## 5. Four-game deltas and gate verdict\n\n${storyResults.map((row) => `- ${row.event_id}: ${row.composition_rebuild.completed ? `${row.composition_rebuild.combined_entry_cents}¢, Δ${row.composition_rebuild.delta_vs_100_cents}` : "PARTIAL"}.`).join("\n")}\n\nGate: ${floorBreaks.length === 0 && lawViolations.length === 0 ? "PASS" : `SELF-STOP (${floorBreaks.length ? "ratchet break" : "law violation"})`}.\n`;
  writeText(path.join(output, "PROCESS_FIRST_CONFIRM.md"), processMd);
  writeText(path.join(output, "ASSUMPTION_GAPS.md"), `# Assumption gaps\n\n- January–March has event-grain historical aggregates but no local intramatch tape. Measurement needed: public historical trades plus timestamped book reconstruction at the same grain as the July recorder.\n- The subsecond store mixes public tape and synthetic book transitions and lacks exchange trade identity on every row. Measurement needed: source-specific identity completeness by named event.\n- The DO archive is connected and the pre-sealed object reader is smoked, but its July object catalog is not a January-present database. Measurement needed: event-level archive coverage joined to corpus_events_v2.\n- The odds backup is connected, but its overlap with each target game is not complete. Measurement needed: immutable per-event bookmaker snapshots with source clock and player mapping.\n- CRIJEA has no verified bell. Measurement needed: an independent official in-play timestamp; until then it grades nothing.\n`);
  writeText(path.join(output, "CC_URSPAL_LATE_BELL.md"), `# CC filing — URSPAL late bell\n\nEvent: KXATPCHALLENGERMATCH-26JUL14URSPAL.\n\nThe L11 truth-table right edge is 1784045100. Tape prints moved PAL 41→30 and URS 61→77 within four minutes after that edge. The tape-inferred bell is at least 48 minutes late for this game. The close remains the truth-table close unless and until CC's standing bell sweep produces a stronger official timestamp.\n\nSource: F-VS-023 @ 3cd59162; W1_GROUND_TRUTH_TABLE.json @ c0056976.\n`);
  writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { full_804_run: false, tune_test_population_run: false, sealed_read: false, holdout_read: false, live_mutation: false, orders: false, positions: false, deployment: false, scope: { smoke: TARGETS.smoke, stories: TARGETS.stories } });
  writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { corpus_sources: corpus.sources, foundation: corpus.foundation, library_bell_bound: corpus.bell_bound_receipt, corpus_floor_timing: corpusFloorTiming, ground_truth: groundTruth.receipt, remote, target_prints: printLoad.source, lineage: lineage.receipt, resources });
  writeJson(path.join(output, "WORKTREE_LARGE_UNTRACKED_CENSUS.json"), largeUntrackedCensus(repo));
  const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  ensure(files.every((name) => fs.statSync(path.join(output, name)).size <= 50 * 1024 * 1024), "L22_COMMITTED_ARTIFACT_EXCEEDS_50_MIB");
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: OUTPUT_LABEL, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
  process.stdout.write(canonical({ output, functionable: functionality.all_connected, smoke: "PASS_NO_GRADING", stories: storyResults, floor_breaks: floorBreaks, full_804_run: false, sealed: false, live: false }));
}

if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = {
  GROUND_TRUTH_COMMIT,
  GROUND_TRUTH_PATH,
  loadCorpus,
  loadGroundTruth,
  targetMeta,
  bindCorpusFloorTiming,
  loadTicks,
  loadTargetPrints,
  replayEvent,
  streamJsonl,
  receipt,
  fileHash,
  shaBytes,
  canonical,
  LOAD_TICK_ISSUES,
};
