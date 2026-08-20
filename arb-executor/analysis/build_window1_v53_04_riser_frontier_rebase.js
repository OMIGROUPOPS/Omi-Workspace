"use strict";

// V53-04 T1 is a measurement lane, not a mechanism exam.  It re-runs the
// retained riser-trigger frontier on the verified W1 spans and deliberately
// keeps the operator's joint-state, trade-backed DIVOT separate from the old
// ask-descent/dwell/return proxy.

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");
const readline = require("readline");
const child = require("child_process");

const repo = path.resolve(__dirname, "../..");
const privateRoot = process.env.OMI_WINDOW1_PRIVATE || path.join(process.env.USERPROFILE || path.resolve(repo, ".."), "OMI-Window1-private");
const output = path.resolve(process.argv[2] || path.join(repo, ".claude/window1_v53_04_riser_frontier_rebase_20260820"));
const TRUTH_COMMIT = "c0056976c446afcb4d9603796a2e06c068ee94d6";
const CAUSAL_COMMIT = "d3db740f143646614bc10778c0b4e27fa519dcd8";
const PRIOR_COMMIT = "084df12553928677869bd2857516caa3f0490416";
const TRUTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const CAUSAL_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAUSAL_LEG_TABLE.json";
const PRIOR_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_TRIGGER_FRONTIER.json";
const TRIGGERS = ["T1_SECOND_TRUE_DIVOT_VISIT", "T2_FIRST_TRUE_DIVOT_AND_RESUME", "T3_FIRST_SELLER_HIT", "T4_BID_PERSISTENCE_300S", "T5_FIRST_TWO_SIDED_BOOK"];
const PERSIST_SECONDS = 300;

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function gitShow(commit, file) { return child.execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 512 * 1024 * 1024 }); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let h = +m[4]; if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/), header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}
function loadBooks(ticker, left, right, hashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing book ${ticker}`);
  const bytes = fs.readFileSync(file), parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  hashes[ticker] = { sha256: sha(bytes), bytes: bytes.length };
  const ix = Object.fromEntries(parsed.header.map((name, index) => [name, index])), rows = [];
  for (let i = 0; i < parsed.rows.length; i += 1) {
    const r = parsed.rows[i], ts = parseEt(r[ix.ts_et]);
    if (!Number.isFinite(ts) || ts < left || ts > right) continue;
    const bid = integer(r[ix.bid_1]), ask = integer(r[ix.ask_1]);
    if (!Number.isInteger(bid) || !Number.isInteger(ask)) continue;
    rows.push({ ts, receipt: `${ticker}.csv.gz#row-${i + 2}`, bid, ask, bid_size: positive(r[ix.bid_1_sz]), ask_size: positive(r[ix.ask_1_sz]), last_trade: integer(r[ix.last_trade]) });
  }
  return rows;
}
function latestAt(rows, ts) {
  let lo = 0, hi = rows.length - 1, hit = -1;
  while (lo <= hi) { const mid = (lo + hi) >> 1; if (rows[mid].ts <= ts) { hit = mid; lo = mid + 1; } else hi = mid - 1; }
  return hit >= 0 ? rows[hit] : null;
}
async function loadPrints(bounds) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private prints");
  const byTicker = new Map([...bounds].map(([ticker]) => [ticker, []])), seen = new Map([...bounds].map(([ticker]) => [ticker, new Set()]));
  const digest = crypto.createHash("sha256"), input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => digest.update(chunk));
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  let raw = 0, admitted = 0, duplicates = 0;
  for await (const line of rl) {
    if (!line) continue; raw += 1;
    const row = JSON.parse(line), bound = bounds.get(row.ticker);
    if (!bound || row.true_print !== true) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicates += 1; continue; }
    seen.get(row.ticker).add(row.trade_id); admitted += 1;
    byTicker.get(row.ticker).push({ ts, receipt: row.receipt_id || `prints.jsonl#${raw}`, trade_id: row.trade_id, price: integer(row.price_cents), size: positive(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side });
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.ts - b.ts || a.trade_id.localeCompare(b.trade_id));
  return { byTicker, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: digest.digest("hex"), bytes: fs.statSync(file).size, raw_rows: raw, admitted_unique_rows: admitted, duplicate_trade_ids_rejected: duplicates } };
}
function trueDivots(prints, ownBooks, siblingBooks) {
  const candidates = [];
  let runningHigh = null;
  for (let i = 0; i < prints.length; i += 1) {
    const p = prints[i], own = latestAt(ownBooks, p.ts), sibling = latestAt(siblingBooks, p.ts);
    const joint = own && sibling ? { own: { bid: own.bid, ask: own.ask, receipt: own.receipt }, sibling: { bid: sibling.bid, ask: sibling.ask, receipt: sibling.receipt } } : null;
    const nextHigher = prints.slice(i + 1).find((q) => q.price > p.price);
    const strengthening = Number.isInteger(runningHigh) && p.price < runningHigh;
    const tradeBackedAtTrough = own && p.price <= own.bid;
    if (joint && strengthening && tradeBackedAtTrough && nextHigher) {
      candidates.push({ trough_ts: p.ts, trough_receipt: p.receipt, trough_price_cents: p.price, trough_size: p.size, joint_state: joint, resume_ts: nextHigher.ts, resume_receipt: nextHigher.receipt, resume_price_cents: nextHigher.price });
    }
    runningHigh = runningHigh === null ? p.price : Math.max(runningHigh, p.price);
  }
  return candidates;
}
function proxyTroughs(books) {
  const visits = [];
  let prior = null, runningLow = null;
  for (const row of books) {
    if (prior && row.ask < prior.ask) {
      const resume = books.find((q) => q.ts > row.ts && q.ask > row.ask);
      if (resume) visits.push({ trough_ts: row.ts, trough_receipt: row.receipt, trough_price_cents: row.ask, resume_ts: resume.ts, resume_receipt: resume.receipt, resume_price_cents: resume.ask, proxy: "ASK_DESCENT_AND_RETURN_NO_TRADE_OR_JOINT_STATE_REQUIREMENT" });
    }
    runningLow = runningLow === null ? row.ask : Math.min(runningLow, row.ask);
    prior = row;
  }
  return visits;
}
function triggerRows(prints, ownBooks, siblingBooks, divotMode) {
  const divots = divotMode === "TRUE_DIVOT" ? trueDivots(prints, ownBooks, siblingBooks) : proxyTroughs(ownBooks);
  const firstSeller = prints.find((p) => p.taker_book_side === "bid" || p.taker_side === "no") || null;
  let persist = null, level = null, since = null;
  for (const row of ownBooks) {
    if (row.bid !== level) { level = row.bid; since = row.ts; }
    if (row.ts - since >= PERSIST_SECONDS) { persist = { ...row, qualification_started_ts: since }; break; }
  }
  const t1 = divots.length >= 2 ? divots[1] : null, t2 = divots[0] || null;
  return {
    T1_SECOND_TRUE_DIVOT_VISIT: t1 ? { ts: t1.trough_ts, receipt: t1.trough_receipt, level: t1.trough_price_cents, evidence: t1 } : null,
    T2_FIRST_TRUE_DIVOT_AND_RESUME: t2 ? { ts: t2.resume_ts, receipt: t2.resume_receipt, level: latestAt(ownBooks, t2.resume_ts)?.bid ?? t2.trough_price_cents, evidence: t2 } : null,
    T3_FIRST_SELLER_HIT: firstSeller ? { ts: firstSeller.ts, receipt: firstSeller.receipt, level: latestAt(ownBooks, firstSeller.ts)?.bid ?? firstSeller.price, evidence: firstSeller } : null,
    T4_BID_PERSISTENCE_300S: persist ? { ts: persist.ts, receipt: persist.receipt, level: persist.bid, evidence: { qualification_started_ts: persist.qualification_started_ts, qualification_seconds: persist.ts - persist.qualification_started_ts, provenance: `${PRIOR_COMMIT}:${PRIOR_PATH}` } } : null,
    T5_FIRST_TWO_SIDED_BOOK: ownBooks[0] ? { ts: ownBooks[0].ts, receipt: ownBooks[0].receipt, level: ownBooks[0].bid, evidence: { bid: ownBooks[0].bid, ask: ownBooks[0].ask } } : null,
  };
}
function summarize(events) {
  const completed = events.filter((row) => Number.isInteger(row.sum_cents)), under = completed.filter((row) => row.sum_cents < 100);
  const frontier = { LE_93: under.filter((r) => r.sum_cents <= 93).length, LE_95: under.filter((r) => r.sum_cents <= 95).length, LE_97: under.filter((r) => r.sum_cents <= 97).length, LT_100: under.length };
  const byCategory = {};
  for (const category of [...new Set(events.map((r) => r.category))].sort()) {
    const rows = events.filter((r) => r.category === category), c = rows.filter((r) => Number.isInteger(r.sum_cents)), u = c.filter((r) => r.sum_cents < 100);
    byCategory[category] = { population: rows.length, completed: c.length, under_par: u.length, locked_cents: u.reduce((s, r) => s + 100 - r.sum_cents, 0), frontier: { LE_93: u.filter((r) => r.sum_cents <= 93).length, LE_95: u.filter((r) => r.sum_cents <= 95).length, LE_97: u.filter((r) => r.sum_cents <= 97).length, LT_100: u.length } };
  }
  return { completed: completed.length, under_par: under.length, locked_cents: under.reduce((s, r) => s + 100 - r.sum_cents, 0), frontier, by_category: byCategory };
}
function deriveAnchor(row, legId) {
  const index = row.legA === legId ? "A" : row.legB === legId ? "B" : null;
  const names = index === "A" ? ["legA_open_postformation_c"] : index === "B" ? ["legB_open_postformation_c"] : [];
  for (const name of names) if (Number.isInteger(row[name])) return row[name];
  return null;
}
function pickLegIds(row) {
  const ids = [row.leg_a, row.leg_b, row.leg_A, row.leg_B, row.leg_1, row.leg_2].filter((x) => typeof x === "string");
  return [...new Set(ids)].slice(0, 2);
}
function percentile(values, q) { if (!values.length) return null; const s = [...values].sort((a, b) => a - b), i = (s.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return lo === hi ? s[lo] : s[lo] + (s[hi] - s[lo]) * (i - lo); }

async function main() {
  const truthBytes = gitShow(TRUTH_COMMIT, TRUTH_PATH), causalBytes = gitShow(CAUSAL_COMMIT, CAUSAL_PATH), priorBytes = gitShow(PRIOR_COMMIT, PRIOR_PATH);
  const truth = JSON.parse(truthBytes), causal = JSON.parse(causalBytes), prior = JSON.parse(priorBytes);
  ensure(truth.rows.length === 804, "truth table is not 804 rows");
  const truthByEvent = new Map(truth.rows.map((row) => [row.event_id, row]));
  const causalRows = Object.entries(causal).map(([ticker, row]) => ({ ticker, ...row }));
  const byEvent = new Map();
  for (const row of causalRows) { if (!byEvent.has(row.event)) byEvent.set(row.event, []); byEvent.get(row.event).push(row); }
  const scoredEvents = [...byEvent].filter(([, rows]) => rows.length === 2 && rows.every((r) => Number.isInteger(r.anytime_reach)));
  const risers = causalRows.filter((row) => row.branch === "RISING" && truthByEvent.get(row.event)?.verified_span === "OK");
  const bounds = new Map();
  for (const row of risers) { const t = truthByEvent.get(row.event); bounds.set(row.ticker, { left: t.span_start_epoch, right: t.span_end_epoch }); }
  const detailCache = path.join(output, "RISER_TRIGGER_DETAIL.jsonl.gz"), priorResultPath = path.join(output, "RISER_TRIGGER_FRONTIER_REBASED.json"), bookCache = path.join(output, "PRIVATE_BOOK_INPUT_MANIFEST.json");
  let printLoad, bookHashes = {}, perRiser = [];
  if (fs.existsSync(detailCache) && fs.existsSync(priorResultPath) && fs.existsSync(bookCache)) {
    perRiser = zlib.gunzipSync(fs.readFileSync(detailCache)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
    printLoad = { receipt: JSON.parse(fs.readFileSync(priorResultPath, "utf8")).private_inputs.prints };
    bookHashes = JSON.parse(fs.readFileSync(bookCache, "utf8"));
    ensure(perRiser.length === risers.length, `cached riser detail count ${perRiser.length} != ${risers.length}`);
  } else {
    printLoad = await loadPrints(bounds);
  for (let n = 0; n < risers.length; n += 1) {
    const riser = risers[n], truthRow = truthByEvent.get(riser.event), siblings = byEvent.get(riser.event), sibling = siblings.find((r) => r.ticker !== riser.ticker);
    const ownBooks = loadBooks(riser.ticker, truthRow.span_start_epoch, truthRow.span_end_epoch, bookHashes);
    const siblingBooks = loadBooks(sibling.ticker, truthRow.span_start_epoch, truthRow.span_end_epoch, bookHashes);
    const prints = printLoad.byTicker.get(riser.ticker) || [];
    const columns = {};
    for (const divotMode of ["TRUE_DIVOT", "PROXY_ONLY_TROUGH"]) {
      const triggers = triggerRows(prints, ownBooks, siblingBooks, divotMode), outcomes = {};
      for (const name of TRIGGERS) {
        const trigger = triggers[name], later = trigger ? prints.filter((p) => p.ts >= trigger.ts) : [];
        const reach = later.length ? Math.min(...later.map((p) => p.price)) : null;
        outcomes[name] = { trigger, causal_trade_reach_cents: reach, false_arm: Boolean(trigger && Number.isInteger(trigger.level) && (!Number.isInteger(reach) || reach > trigger.level)), false_arm_cents: trigger && Number.isInteger(trigger.level) && Number.isInteger(reach) ? Math.max(0, reach - trigger.level) : null, hard_arm: Boolean(trigger && !Number.isInteger(reach)) };
      }
      columns[divotMode] = outcomes;
    }
    perRiser.push({ event_id: riser.event, ticker: riser.ticker, leg_id: riser.leg, category: riser.cat, family: riser.family, anytime_reach_cents: riser.anytime_reach, print_rows: prints.length, columns });
    if ((n + 1) % 50 === 0) process.stderr.write(`rebased ${n + 1}/${risers.length} risers\n`);
  }
  }
  const riserByTicker = new Map(perRiser.map((r) => [r.ticker, r]));
  const scoreColumns = {};
  for (const divotMode of ["TRUE_DIVOT", "PROXY_ONLY_TROUGH"]) {
    scoreColumns[divotMode] = {};
    for (const triggerName of TRIGGERS) {
      const eventRows = scoredEvents.map(([eventId, legs]) => {
        const values = legs.map((leg) => leg.branch === "RISING" ? riserByTicker.get(leg.ticker)?.columns[divotMode][triggerName].causal_trade_reach_cents ?? null : leg.anytime_reach);
        return { event_id: eventId, category: legs[0].cat, values_cents: values, sum_cents: values.every(Number.isInteger) ? values[0] + values[1] : null };
      });
      const triggerOutcomes = perRiser.map((r) => r.columns[divotMode][triggerName]);
      scoreColumns[divotMode][triggerName] = { ...summarize(eventRows), riser_legs: perRiser.length, riser_legs_without_trigger_or_post_trigger_trade: triggerOutcomes.filter((o) => !Number.isInteger(o.causal_trade_reach_cents)).length, false_arms: triggerOutcomes.filter((o) => o.false_arm).length, false_arm_cents: triggerOutcomes.reduce((s, o) => s + (o.false_arm_cents || 0), 0), hard_arms: triggerOutcomes.filter((o) => o.hard_arm).length };
    }
  }
  const incumbent = scoreColumns.TRUE_DIVOT.T1_SECOND_TRUE_DIVOT_VISIT;
  const eligible = TRIGGERS.filter((name) => scoreColumns.TRUE_DIVOT[name].false_arm_cents <= 1.5 * incumbent.false_arm_cents);
  const picked = eligible.sort((a, b) => scoreColumns.TRUE_DIVOT[b].under_par - scoreColumns.TRUE_DIVOT[a].under_par || scoreColumns.TRUE_DIVOT[a].hard_arms - scoreColumns.TRUE_DIVOT[b].hard_arms || a.localeCompare(b))[0];

  // Secondary anchor-k measurement on the two prior 30-game cohorts.  Pins
  // are intentionally repeated because the dispatch names sixty pairs, not
  // fifty-five unique identities.
  const cohortPaths = [
    ".claude/window1_v53_02_preregistration_20260820/PRE_REGISTRATION.json",
    ".claude/window1_v53_03_preregistration_20260820/PRE_REGISTRATION.json",
  ];
  const cohortRows = cohortPaths.flatMap((file) => JSON.parse(fs.readFileSync(path.join(repo, file), "utf8")).population.combined_30);
  const anchorRows = [];
  for (let occurrence = 0; occurrence < cohortRows.length; occurrence += 1) {
    const member = cohortRows[occurrence], row = truthByEvent.get(member.event_id), legs = byEvent.get(member.event_id) || [];
    for (const k of [1, 2, 3]) {
      const values = legs.map((leg) => { const anchor = deriveAnchor(row, leg.leg); return Number.isInteger(anchor) ? anchor - k : null; });
      const floors = legs.map((leg) => leg.anytime_reach);
      const credited = values.map((target, i) => Number.isInteger(target) && Number.isInteger(floors[i]) && floors[i] <= target);
      anchorRows.push({ occurrence, event_id: member.event_id, category: member.category, k_cents: k, targets_cents: values, floors_cents: floors, credited, completed: credited.length === 2 && credited.every(Boolean), combined_target_cents: values.every(Number.isInteger) ? values[0] + values[1] : null, under_par: credited.length === 2 && credited.every(Boolean) && values[0] + values[1] < 100, locked_cents: credited.length === 2 && credited.every(Boolean) && values[0] + values[1] < 100 ? 100 - values[0] - values[1] : 0, too_deep_legs: credited.filter((x) => !x).length });
    }
  }
  const anchorSummary = Object.fromEntries([1, 2, 3].map((k) => { const rows = anchorRows.filter((r) => r.k_cents === k); return [`ANCHOR_MINUS_${k}`, { observations: rows.length, unique_events: new Set(rows.map((r) => r.event_id)).size, completed: rows.filter((r) => r.completed).length, under_par: rows.filter((r) => r.under_par).length, locked_cents: rows.reduce((s, r) => s + r.locked_cents, 0), too_deep_legs: rows.reduce((s, r) => s + r.too_deep_legs, 0) }]; }));

  const v5302L1L8Path = ".claude/window1_live_v4_replay/v53_02_understanding_bounds_stage1_20260820/PER_GAME_L1_L8.json";
  const v5302Rows = JSON.parse(fs.readFileSync(path.join(repo, v5302L1L8Path), "utf8")).rows;
  const backfillRows = [];
  for (const event of v5302Rows) {
    if (event.L8_OUTCOME.candidate.completed) continue;
    const truthRow = truthByEvent.get(event.event_id);
    for (const [identity, leg] of Object.entries(event.L7_CREDIT.why).filter(([, value]) => value.credited)) {
      const legId = identity.split("|").at(-1), side = truthRow?.legA === legId ? "A" : truthRow?.legB === legId ? "B" : null;
      const close = side ? truthRow[`leg${side}_close_c`] : null;
      backfillRows.push({ event_id: event.event_id, leg_identity: identity, category: truthRow?.category ?? null, entry_cents: leg.entry_cents, own_W1_close_cents: Number.isInteger(close) ? close : null, signed_entry_minus_own_close_cents: Number.isInteger(close) ? leg.entry_cents - close : null, gradeable: Number.isInteger(close), source: { entry: `${v5302L1L8Path}:L7_CREDIT`, close: `${TRUTH_COMMIT}:${TRUTH_PATH}` } });
    }
  }

  fs.mkdirSync(output, { recursive: true });
  const result = {
    label: "RISER_TRIGGER_FRONTIER_REBASED",
    stamp: "DESCRIPTIVE_MEASUREMENT_NOT_MECHANISM_EXAM",
    authorities: { truth_table: { commit: TRUTH_COMMIT, path: TRUTH_PATH, sha256: sha(truthBytes) }, causal_leg_table: { commit: CAUSAL_COMMIT, path: CAUSAL_PATH, sha256: sha(causalBytes), role: "RISING_IDENTITY_AND_FIXED_NON_RISER_MACHINERY" }, retained_method: { commit: PRIOR_COMMIT, path: PRIOR_PATH, sha256: sha(priorBytes) } },
    definitions: { DIVOT: "STRENGTHENING_SIDE_ONLY; BOTH_BOOKS_FORMED_AT_TROUGH; TRUE_PRINT_AT_OR_BELOW_DISPLAYED_BID; PRIOR_HIGH_EXISTS; STRICTLY_LATER_HIGHER_PRINT RESUMES", PROXY_ONLY_TROUGH: "ASK_DESCENT_AND_LATER_RETURN_WITHOUT_TRADE_OR_JOINT_STATE_REQUIREMENT; NEVER CALLED A DIVOT", CANON_CREDIT: "ANY TRUE TRADE AT_OR_BELOW A PRIOR STANDING LEVEL; FRONTIER REACH IS LOWEST TRUE TRADE AT_OR_AFTER CAUSAL ARM", T4_constant: { seconds: PERSIST_SECONDS, provenance: `${PRIOR_COMMIT}:${PRIOR_PATH}` } },
    conservation: { full_population: truth.rows.length, verified_span_OK: truth.rows.filter((r) => r.verified_span === "OK").length, scored_fixed_reach_events: scoredEvents.length, causal_leg_rows: causalRows.length, riser_legs_rebased: perRiser.length, old_frontier_games: prior.conservation.games, old_frontier_risers: prior.conservation.risers },
    score_columns: scoreColumns,
    pick_rule: { expression: "MAX_TRUE_DIVOT_COLUMN_UNDER_PAR_WITH_FALSE_ARM_CENTS_LE_1_5X_INCUMBENT; TIE_FEWER_HARD_ARMS", incumbent_false_arm_cents: incumbent.false_arm_cents, maximum_allowed_false_arm_cents: 1.5 * incumbent.false_arm_cents, eligible, picked },
    secondary_anchor_minus_k: anchorSummary,
    private_inputs: { prints: printLoad.receipt, book_files: Object.keys(bookHashes).length, book_manifest_sha256: sha(Buffer.from(canonical(bookHashes))) },
  };
  fs.writeFileSync(path.join(output, "RISER_TRIGGER_FRONTIER_REBASED.json"), canonical(result));
  fs.writeFileSync(path.join(output, "RISER_TRIGGER_DETAIL.jsonl.gz"), zlib.gzipSync(perRiser.map((r) => JSON.stringify(r)).join("\n") + "\n", { level: 9, mtime: 0 }));
  fs.writeFileSync(path.join(output, "ANCHOR_MINUS_K_DETAIL.jsonl.gz"), zlib.gzipSync(anchorRows.map((r) => JSON.stringify(r)).join("\n") + "\n", { level: 9, mtime: 0 }));
  fs.writeFileSync(path.join(output, "BACKFILL_LEG_DELTAS.json"), canonical({ label: "V53_02_INCOMPLETE_PAIR_CREDITED_LEG_DELTAS", credited_legs: backfillRows.length, gradeable_legs: backfillRows.filter((r) => r.gradeable).length, unavailable_close_legs: backfillRows.filter((r) => !r.gradeable).length, rows: backfillRows }));
  fs.writeFileSync(path.join(output, "PRIVATE_BOOK_INPUT_MANIFEST.json"), canonical(bookHashes));
  fs.writeFileSync(path.join(output, "REPORT.md"), `# V53-04 riser-trigger frontier rebase\n\nThis is a measurement lane, not a mechanism exam. The full population conserves to 804; ${scoredEvents.length} fixed-reach events and ${perRiser.length} riser legs are comparable to the retained frontier.\n\nThe operator-defined DIVOT and the ask-trough proxy are separate columns. The pick is **${picked}** under the registered rule.\n\n${TRIGGERS.map((name) => `- ${name}: true-divot column ${scoreColumns.TRUE_DIVOT[name].under_par} under-par / ${scoreColumns.TRUE_DIVOT[name].locked_cents}c; proxy column ${scoreColumns.PROXY_ONLY_TROUGH[name].under_par} / ${scoreColumns.PROXY_ONLY_TROUGH[name].locked_cents}c; false-arm ${scoreColumns.TRUE_DIVOT[name].false_arm_cents}c, hard ${scoreColumns.TRUE_DIVOT[name].hard_arms}.`).join("\n")}\n`);
  const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(), manifest = Object.fromEntries(files.map((name) => { const bytes = fs.readFileSync(path.join(output, name)); return [name, { sha256: sha(bytes), bytes: bytes.length }]; }));
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical(manifest));
  process.stdout.write(canonical({ output, picked, true: scoreColumns.TRUE_DIVOT, proxy: scoreColumns.PROXY_ONLY_TROUGH, anchorSummary }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
