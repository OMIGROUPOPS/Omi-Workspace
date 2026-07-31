#!/usr/bin/env node
"use strict";

// Descriptive audit only. This builder never imports or invokes a scorer,
// replay engine, trading adapter, or live surface.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const SCHEMA = "window1_initial_aim_constant_audit_v1";
const BRANCH = "codex/window1-live-consolidated";
const RAW = `https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/${BRANCH}`;

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === "--repo") out.repo = argv[++i];
    else if (argv[i] === "--output") out.output = argv[++i];
    else throw new Error(`unsupported argument: ${argv[i]}`);
  }
  return out;
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = stable(value[key]);
    return out;
  }
  return value;
}

function jsonBytes(value) {
  return Buffer.from(`${JSON.stringify(stable(value), null, 2)}\n`, "utf8");
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function writeFile(filePath, bytes) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, bytes);
}

function writeJson(filePath, value) {
  writeFile(filePath, jsonBytes(value));
}

function git(repo, args) {
  const result = spawnSync("git", args, { cwd: repo, encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`git ${args.join(" ")} failed: ${result.stderr.trim()}`);
  }
  return result.stdout.trim();
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      if (row.some((x) => x !== "")) rows.push(row);
      row = [];
      field = "";
    } else field += ch;
  }
  if (field !== "" || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const header = rows.shift();
  return rows.map((values) => Object.fromEntries(header.map((h, i) => [h, values[i] ?? ""])));
}

function numberOrNull(value) {
  if (value === null || value === undefined || value === "") return null;
  const n = Number(value);
  if (!Number.isFinite(n)) throw new Error(`non-finite number: ${value}`);
  return n;
}

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor((sorted.length - 1) * p)];
}

function distribution(values) {
  const histogram = {};
  for (const value of values) histogram[String(value)] = (histogram[String(value)] || 0) + 1;
  return {
    n: values.length,
    min: values.length ? Math.min(...values) : null,
    p10: percentile(values, 0.10),
    p25: percentile(values, 0.25),
    p50: percentile(values, 0.50),
    p75: percentile(values, 0.75),
    p90: percentile(values, 0.90),
    max: values.length ? Math.max(...values) : null,
    histogram_cents: Object.fromEntries(Object.entries(histogram).sort((a, b) => Number(a[0]) - Number(b[0]))),
    quantile_method: "lower order statistic: sorted[floor((n-1)*p)]",
  };
}

function groupRows(rows, keyFn, summarize) {
  const groups = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, members]) => ({
    key,
    ...summarize(members),
  }));
}

function rel(repo, p) {
  return path.join(repo, ...p.split("/"));
}

function regionFromPage(page) {
  return String(page).split("|")[2] || "UNKNOWN";
}

function summarizeAtlas(rows) {
  const comparable = rows.filter((row) => row.signed_error_cents !== null);
  return {
    category: rows[0].category,
    price_region: rows[0].price_region,
    atlas_pages: [...new Set(rows.map((row) => row.atlas_page))].sort(),
    legs_with_page: rows.length,
    ask_10s_reachable_low_available: comparable.length,
    thin: comparable.length < 8,
    predicted_p75_depth_cents: distribution(comparable.map((row) => row.predicted_p75_depth_cents)),
    actual_anchor_to_ask_10s_low_travel_cents: distribution(comparable.map((row) => row.actual_travel_cents)),
    signed_error_predicted_minus_actual_cents: distribution(comparable.map((row) => row.signed_error_cents)),
    sign_counts: {
      predicted_too_deep_positive: comparable.filter((row) => row.signed_error_cents > 0).length,
      exact_zero: comparable.filter((row) => row.signed_error_cents === 0).length,
      predicted_too_shallow_negative: comparable.filter((row) => row.signed_error_cents < 0).length,
    },
    row_ids: comparable.map((row) => row.row_id),
  };
}

function summarizeChase(rows) {
  const filled = rows.filter((row) => row.legacy_fill_assigned);
  const comparable = filled.filter((row) => row.fill_minus_ask_10s_low_cents !== null);
  const netDown = filled.filter((row) => row.proven_net_down_placement_path);
  const netDownComparable = netDown.filter((row) => row.fill_minus_ask_10s_low_cents !== null);
  return {
    category: rows[0].category,
    price_region: rows[0].price_region,
    candidate_legs: rows.length,
    legacy_fill_assignments: filled.length,
    fill_capacity_identity_preserved: 0,
    fill_capacity_evidence_absent: filled.length,
    proven_net_down_placement_paths_lower_bound: netDown.length,
    net_down_distinct_events_lower_bound: new Set(netDown.map((row) => row.event_id)).size,
    exact_downward_cancel_repost_transition_count: null,
    exact_transition_count_reason: "flattened 804 artifact retains first target, final assigned fill, and order count but not the ordered cancel/repost price stream",
    ask_10s_low_comparable_legacy_fills: comparable.length,
    all_legacy_fill_minus_ask_10s_low_cents: distribution(comparable.map((row) => row.fill_minus_ask_10s_low_cents)),
    all_legacy_fill_gap_sign_counts: {
      above_reachable_low: comparable.filter((row) => row.fill_minus_ask_10s_low_cents > 0).length,
      at_reachable_low: comparable.filter((row) => row.fill_minus_ask_10s_low_cents === 0).length,
      below_ask_only_low_via_other_evidence: comparable.filter((row) => row.fill_minus_ask_10s_low_cents < 0).length,
    },
    net_down_ask_10s_low_comparable: netDownComparable.length,
    net_down_fill_minus_ask_10s_low_cents: distribution(netDownComparable.map((row) => row.fill_minus_ask_10s_low_cents)),
    net_down_gap_sign_counts: {
      above_reachable_low: netDownComparable.filter((row) => row.fill_minus_ask_10s_low_cents > 0).length,
      at_reachable_low: netDownComparable.filter((row) => row.fill_minus_ask_10s_low_cents === 0).length,
      below_ask_only_low_via_other_evidence: netDownComparable.filter((row) => row.fill_minus_ask_10s_low_cents < 0).length,
    },
    net_down_row_ids: netDown.map((row) => row.row_id),
  };
}

function buildReport(data) {
  const atlasLines = data.atlas.by_category_price_region.map((g) =>
    `| ${g.category} | ${g.price_region} | ${g.ask_10s_reachable_low_available} | ${g.predicted_p75_depth_cents.p50 ?? "—"} | ${g.actual_anchor_to_ask_10s_low_travel_cents.p25 ?? "—"}/${g.actual_anchor_to_ask_10s_low_travel_cents.p50 ?? "—"}/${g.actual_anchor_to_ask_10s_low_travel_cents.p75 ?? "—"}/${g.actual_anchor_to_ask_10s_low_travel_cents.p90 ?? "—"} | ${g.signed_error_predicted_minus_actual_cents.p25 ?? "—"}/${g.signed_error_predicted_minus_actual_cents.p50 ?? "—"}/${g.signed_error_predicted_minus_actual_cents.p75 ?? "—"}/${g.signed_error_predicted_minus_actual_cents.p90 ?? "—"} | ${g.sign_counts.predicted_too_shallow_negative}/${g.sign_counts.exact_zero}/${g.sign_counts.predicted_too_deep_positive} | ${g.thin ? "THIN" : "reportable"} |`).join("\n");
  const chaseLines = data.chase.by_category_price_region.map((g) =>
    `| ${g.category} | ${g.price_region} | ${g.legacy_fill_assignments} | ${g.proven_net_down_placement_paths_lower_bound} | ${g.ask_10s_low_comparable_legacy_fills} | ${g.all_legacy_fill_minus_ask_10s_low_cents.p25 ?? "—"}/${g.all_legacy_fill_minus_ask_10s_low_cents.p50 ?? "—"}/${g.all_legacy_fill_minus_ask_10s_low_cents.p75 ?? "—"}/${g.all_legacy_fill_minus_ask_10s_low_cents.p90 ?? "—"} | ${g.all_legacy_fill_gap_sign_counts.above_reachable_low}/${g.all_legacy_fill_gap_sign_counts.at_reachable_low}/${g.all_legacy_fill_gap_sign_counts.below_ask_only_low_via_other_evidence} |`)
    .join("\n");
  return Buffer.from(`# Window-1 initial-aim constant audit and replacement specification

Status: descriptive audit and specification only. No replay, scorer, strategy, order, or live code was changed or invoked.

## 1. The seven-cent constant

The controlling row is \`ATP_CHALL|underdog|26_50\`: \`n=1,470\`, bottom-depth p25/p50/p75 = \`2/4/7\` cents, median bottom time \`139\` minutes. The seven is the third quartile of the deepest pre-onset excursion below the page's **discovery anchor**. In the tour builder, discovery is the median minute-candle price during the first tape hour; bottom is the minimum \`price_low\` before the fitted flow-step onset; depth is \`max(0, discovery - bottom)\`. It is neither a Window-1 close delta nor an opening-price delta.

The page was built on 2026-07-15 from G9 tour minute candles before 2026-07-10, with live-era local tape used for ITF hardening. It predates the 2026-07-17 honest-clock migration. Plainly: **the seven-cent fit is pre-migration**.

Sources:

${RAW}/.claude/trendpath/ATLAS_V1.json

${RAW}/arb-executor/analysis/trendpath_build.py

## 2. Predicted p75 dip versus actual ask-side travel

Comparator: the leg's reconstructed ATLAS anchor versus the lowest ask that persisted at least 10 seconds inside guarded Window 1. Bid churn is excluded. Actual travel is \`max(0, anchor - ask_10s_low)\`. Signed error is \`predicted_p75 - actual_travel\`: negative means the table was too shallow and would leave the bid too high; positive means it predicted a deeper dip than the ask-side tape supplied.

This is partitioned by tournament category and ATLAS price region. Quantiles are p25/p50/p75/p90; the JSON retains the complete integer-cent histogram and every contributing row ID. Cells with fewer than eight comparable legs are marked THIN rather than aggregated upward.

| Category | Price region | Comparable n | Predicted p75 median | Actual travel p25/p50/p75/p90 | Error p25/p50/p75/p90 | Too shallow / exact / too deep | Status |
|---|---:|---:|---:|---:|---:|---:|---|
${atlasLines}

Conservation only, not a decision statistic: ${data.atlas.conservation.comparable_rows} comparable legs; ${data.atlas.conservation.predicted_too_shallow_negative} negative, ${data.atlas.conservation.exact_zero} exact, ${data.atlas.conservation.predicted_too_deep_positive} positive. NIK is negative eight: anchor 33, predicted seven, ask-side ten-second low 18, actual travel 15.

Full distributions and identities:

${RAW}/.claude/window1_initial_aim_constant_audit_20260731/ATLAS_P75_CATEGORY_PRICE_DISTRIBUTIONS.json

${RAW}/.claude/window1_initial_aim_constant_audit_20260731/ATLAS_P75_ANCHOR_TRAVEL_LEDGER.jsonl

## 3. NIK anchor provenance

| Decision clock, scheduled / bell | Joint observation: NIK bid/ask/last, spread, dwell; VRB bid/ask/last, spread, dwell | Anchor | Side truth | p75 arithmetic |
|---|---|---|---|---|
| T−361.917 / T−366.917 | NIK 23/33/33, 10, 4s; VRB 67/77/∅, 10, 0s | 33 true print | offer-side: \`BUY_YES__LIFT_ASK\`, receipt \`b17542ca-924e-4214-e91f-a96dc81ad7f6\` | 33−7=26 |
| T−322.450 / T−327.450 | NIK 29/30/32, 1, 0s; VRB 67/76/∅, 9, 2349s | 30 rounded tight-book midpoint | **not a print**; no trade-side classification exists | 30−7=23 |
| T−278.650 / T−283.650 | NIK 24/27/28, 3, 1s; VRB 72/73/73, 1, 159s | 28 true print | receipt says bid-side: \`SELL_YES__HIT_BID\`; archived BBO simultaneously places 28 above ask 27, so side is retained from receipt rather than inferred from the book | 28−7=21 |

The three anchors therefore mix an offer-lifting execution, a constructed midpoint, and a bid-hitting execution. Applying one discovery-depth constant to all three is already a reference mismatch before the size of seven is considered.

Source:

${RAW}/.claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv

## 4. Downward chase and ask-reachable low

The frozen 804 rescore does not retain the ordered cancel/repost price stream. It retains first target, final legacy fill assignment, and total order count. Consequently, an exact count of downward cancel/repost transitions is **not recoverable** and is reported null. A conservative lower bound is a leg with more than one order and a final assigned fill below its first target. That proves a net-down placement path but cannot count intermediate moves, down-then-up paths, or unfilled chases.

The source also does not retain the capacity identity needed to credit five contracts. Every legacy fill assignment below is therefore \`EVIDENCE_ABSENT\` for five-contract credit and is diagnostic only.

| Category | Price region | Legacy assignments | Proven net-down lower bound | Ask-low comparable | Fill−ask-low p25/p50/p75/p90 | Above / equal / below ask-only floor |
|---|---:|---:|---:|---:|---:|---:|
${chaseLines}

Conservation only: ${data.chase.conservation.legacy_fill_assignments} legacy fill assignments, ${data.chase.conservation.proven_net_down_placement_paths_lower_bound} proven net-down paths across ${data.chase.conservation.net_down_distinct_events_lower_bound} events. Only ${data.chase.conservation.ask_10s_low_comparable_legacy_fills} assignments retain a ten-second ask-low comparator. Among those, ${data.chase.conservation.above_reachable_low} are above, ${data.chase.conservation.at_reachable_low} equal, and ${data.chase.conservation.below_ask_only_low_via_other_evidence} below the ask-only floor. The comparable sample does not support the population-wide claim that chase *systematically* finishes above the ask floor; NIK is a demonstrated member of the above-floor class. The missing transition stream and capacity evidence remain named measurement defects.

Full partition and identities:

${RAW}/.claude/window1_initial_aim_constant_audit_20260731/CHASE_AND_FILLABLE_LOW_CENSUS.json

## 5. Smallest honest replacement specification

This is a specification, not an implementation or claimed winner.

Lawful inputs before shape exists:

- the same-tick lawful external bid, ask, positive displayed size, spread, and ask-side dwell;
- receipt-qualified last trade, including whether it lifted the ask or hit the bid, as context only—not a universal subtract-from anchor;
- quote cadence and recurrence, separated by side; bid-only cadence has no reach authority for a buy;
- the sibling's same-tick book as a patience/cancel input, never as \`100 - our fill\` or a synthetic price reference;
- a fresh, independently bound external-book blend only as a sanity envelope. NIKVRB's frozen read was \`NO-READ/stale_sources\`, so it contributes nothing here;
- top-five depth as a vector/context. It cannot be collapsed to a scalar cell signer.

Smallest rule:

1. On the first lawful positive-size non-crossed BBO, before shape exists, join the live bid: \`X0 = min(bid, ask - 1)\`. A fresh bound external blend may veto an outlier but may not synthesize or sign X.
2. Re-evaluate on every raw book receipt. A bid change, midpoint change, or last-trade change alone outputs \`HOLD(X)\`; it cannot lower and repost the order.
3. Only ask-side evidence can change reach state. While \`ask > X\`, retain X unless an independently bound sibling-patience rule cancels it. If \`ask <= X\`, first apply capacity-honest fill accounting. If capacity is absent, cancel the now non-maker-safe order and wait; do not chase it downward on the same receipt.
4. A new order after cancellation requires a strictly later ask state that persists for the inherited ten-second ask-dwell comparator. Its maker price is \`min(current_bid, current_ask - 1)\`. The triggering observation cannot fill the new order.
5. Missing or crossed BBO, missing size, stale/unbound external blend, or ambiguous chronology produces a named \`NO_CALL\`. Shape, cell, and depth tables have no pre-entry signing authority.

Ten seconds is borrowed from the frozen ask-reachability comparator; it is not newly fitted here. Whether ten seconds is optimal remains unvalidated. No replacement threshold has been invented.

NIK under this rule:

| Clock, scheduled / bell | Joint same-tick observation | Existing p75 branch | Minimal rule |
|---|---|---|---|
| T−361.917 / T−366.917 | NIK 23/33/33, spread 10, ask dwell 4s; VRB 67/77/∅, spread 10, dwell 0s | 33−7=26, PLACE 26 | \`min(23,32)=23\`, PLACE 23 |
| T−322.450 / T−327.450 | NIK 29/30/32, spread 1, ask dwell 0s; VRB 67/76/∅, spread 9, dwell 2349s | 30−7=23, REPRICE 26→23 | bid/mid change has no reach authority; HOLD 23 |
| T−278.650 / T−283.650 | NIK 24/27/28, spread 3, ask dwell 1s; VRB 72/73/73, spread 1, dwell 159s | 28−7=21, REPRICE 23→21 | bid/last change has no reach authority and ask 27>23; HOLD 23 |

This removes subtract-a-constant and removes bid-led downward chase. It does **not** prove that 23 is the optimal final entry or that the rule reaches 18 across the population. The separately established sibling-patience cancellation remains a later causal input; its recurrence and five-cent release thresholds remain unvalidated single-specimen borrowings.

Machine-readable specification:

${RAW}/.claude/window1_initial_aim_constant_audit_20260731/INITIAL_AIM_REPLACEMENT_SPEC.json
`, "utf8");
}

function main() {
  const args = parseArgs(process.argv);
  const repo = path.resolve(args.repo || ".");
  const output = path.resolve(args.output || rel(repo, ".claude/window1_initial_aim_constant_audit_20260731"));
  const sources = {
    atlas: rel(repo, ".claude/trendpath/ATLAS_V1.json"),
    atlas_builder: rel(repo, "arb-executor/analysis/trendpath_build.py"),
    rescore: rel(repo, ".claude/window1_live_v4_replay/quote_touch_os_rescore_rebalanced_20260731/WINDOW1_QUOTE_TOUCH_OS_RESCORE.json"),
    reachability: rel(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv"),
    dual_clock: rel(repo, ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv"),
    decision_trace: rel(repo, ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json"),
  };
  for (const [name, source] of Object.entries(sources)) {
    if (!fs.existsSync(source)) throw new Error(`missing source ${name}: ${source}`);
  }

  const atlas = JSON.parse(fs.readFileSync(sources.atlas, "utf8"));
  const rescore = JSON.parse(fs.readFileSync(sources.rescore, "utf8"));
  const reachRows = parseCsv(fs.readFileSync(sources.reachability, "utf8"));
  const clockRows = parseCsv(fs.readFileSync(sources.dual_clock, "utf8"));
  const trace = JSON.parse(fs.readFileSync(sources.decision_trace, "utf8"));
  const selected = rescore.events.filter((event) => event.mode === "ATLAS" && event.fill_model === "QUOTE_TOUCH_OR_PRINT_DWELL_10_V1");
  if (selected.length !== 804) throw new Error(`expected 804 selected events, got ${selected.length}`);
  const reachByLeg = new Map(reachRows.map((row) => [`${row.event_id}|${row.leg}`, row]));

  const atlasRows = [];
  const chaseRows = [];
  for (const event of selected) {
    for (const [legId, leg] of Object.entries(event.legs)) {
      const aim = leg.first_live_aim;
      const reach = reachByLeg.get(`${event.event_id}|${legId}`);
      if (!reach) throw new Error(`missing reach row ${event.event_id}|${legId}`);
      if (!aim || !aim.page || !atlas.pages[aim.page]) continue;
      const p50 = numberOrNull(aim.aim_contract.atlas_depth_cents);
      const anchor = numberOrNull(aim.path_aim) + p50;
      const p75 = numberOrNull(atlas.pages[aim.page].bottom.depth_p75);
      const askLow = numberOrNull(reach.quote_10s_floor_limit_cents);
      const travel = askLow === null ? null : Math.max(0, anchor - askLow);
      const priceRegion = regionFromPage(aim.page);
      const rowId = `${event.event_id}|${legId}|${aim.page}`;
      atlasRows.push({
        row_id: rowId,
        event_id: event.event_id,
        leg_id: legId,
        ticker: leg.ticker,
        category: event.category,
        price_region: priceRegion,
        atlas_page: aim.page,
        atlas_page_n: atlas.pages[aim.page].n,
        atlas_built: atlas.meta.built,
        reconstructed_anchor_cents: anchor,
        anchor_reconstruction: `first_live_aim.path_aim ${aim.path_aim} + frozen p50 depth ${p50}`,
        predicted_p75_depth_cents: p75,
        ask_reachability_side: "ASK_ONLY",
        ask_dwell_threshold_seconds: 10,
        ask_dwell_threshold_provenance: "QUOTE_TOUCH_OR_PRINT_DWELL_10_V1 frozen comparator",
        ask_10s_reachable_low_cents: askLow,
        actual_travel_cents: travel,
        signed_error_cents: travel === null ? null : p75 - travel,
        signed_error_interpretation: travel === null ? "UNAVAILABLE" : p75 - travel < 0 ? "PREDICTED_TOO_SHALLOW" : p75 - travel > 0 ? "PREDICTED_TOO_DEEP" : "EXACT",
      });
      const fill = numberOrNull(leg.fill_price_cents);
      const firstTarget = numberOrNull(aim.path_aim);
      const orderCount = numberOrNull(leg.orders_posted) || 0;
      const legacyFilled = Boolean(leg.filled && fill !== null);
      const gap = legacyFilled && askLow !== null ? fill - askLow : null;
      chaseRows.push({
        row_id: rowId,
        event_id: event.event_id,
        leg_id: legId,
        ticker: leg.ticker,
        category: event.category,
        price_region: priceRegion,
        atlas_page: aim.page,
        first_target_cents: firstTarget,
        orders_posted_flat_count: orderCount,
        legacy_fill_assigned: legacyFilled,
        legacy_fill_price_cents: fill,
        legacy_fill_trigger: leg.fill_trigger,
        capacity_status: legacyFilled ? "EVIDENCE_ABSENT__NOT_PRESERVED_IN_FLATTENED_RESCORE" : "NOT_APPLICABLE",
        accounting_credit_per_current_law: false,
        proven_net_down_placement_path: Boolean(legacyFilled && orderCount > 1 && fill < firstTarget),
        exact_downward_cancel_repost_transition_count: null,
        ask_reachability_side: "ASK_ONLY",
        ask_dwell_threshold_seconds: 10,
        ask_10s_reachable_low_cents: askLow,
        fill_minus_ask_10s_low_cents: gap,
      });
    }
  }

  const comparableAtlas = atlasRows.filter((row) => row.signed_error_cents !== null);
  const atlasSummary = {
    schema_version: SCHEMA,
    measurement_contract: {
      partition: "tournament category x ATLAS price region",
      actual: "max(0, reconstructed anchor - lowest ask persisting at least 10 seconds)",
      signed_error: "predicted p75 depth - actual ask-side travel",
      positive: "predicted too deep",
      negative: "predicted too shallow",
      no_bid_reach_credit: true,
      no_population_mean: true,
    },
    conservation: {
      population_events: 804,
      population_legs: 1608,
      legs_with_atlas_page: atlasRows.length,
      comparable_rows: comparableAtlas.length,
      predicted_too_shallow_negative: comparableAtlas.filter((row) => row.signed_error_cents < 0).length,
      exact_zero: comparableAtlas.filter((row) => row.signed_error_cents === 0).length,
      predicted_too_deep_positive: comparableAtlas.filter((row) => row.signed_error_cents > 0).length,
    },
    by_category_price_region: groupRows(atlasRows, (row) => `${row.category}|${row.price_region}`, summarizeAtlas),
    nik_control: atlasRows.find((row) => row.event_id.endsWith("NIKVRB") && row.leg_id === "NIK") || null,
  };

  const filledChase = chaseRows.filter((row) => row.legacy_fill_assigned);
  const comparableChase = filledChase.filter((row) => row.fill_minus_ask_10s_low_cents !== null);
  const netDown = filledChase.filter((row) => row.proven_net_down_placement_path);
  const chaseSummary = {
    schema_version: SCHEMA,
    scope_warning: "legacy fill assignments are diagnostic only because exact five-contract capacity identity is absent from the flattened rescore",
    exact_chase_count_status: "UNAVAILABLE_FROM_FROZEN_FLATTENED_ARTIFACT",
    conservation: {
      population_events: 804,
      candidate_legs_with_atlas_page: chaseRows.length,
      legacy_fill_assignments: filledChase.length,
      legacy_fill_assignments_credited_under_current_capacity_law: 0,
      legacy_fill_assignments_capacity_evidence_absent: filledChase.length,
      proven_net_down_placement_paths_lower_bound: netDown.length,
      net_down_distinct_events_lower_bound: new Set(netDown.map((row) => row.event_id)).size,
      exact_downward_cancel_repost_transition_count: null,
      ask_10s_low_comparable_legacy_fills: comparableChase.length,
      above_reachable_low: comparableChase.filter((row) => row.fill_minus_ask_10s_low_cents > 0).length,
      at_reachable_low: comparableChase.filter((row) => row.fill_minus_ask_10s_low_cents === 0).length,
      below_ask_only_low_via_other_evidence: comparableChase.filter((row) => row.fill_minus_ask_10s_low_cents < 0).length,
      all_comparable_gap_distribution: distribution(comparableChase.map((row) => row.fill_minus_ask_10s_low_cents)),
      net_down_comparable_gap_distribution: distribution(netDown.filter((row) => row.fill_minus_ask_10s_low_cents !== null).map((row) => row.fill_minus_ask_10s_low_cents)),
    },
    by_category_price_region: groupRows(chaseRows, (row) => `${row.category}|${row.price_region}`, summarizeChase),
    rows: chaseRows,
  };

  const desiredClockSeq = new Set([7, 190, 746, 747]);
  const clockEvidence = clockRows.filter((row) => desiredClockSeq.has(Number(row.sequence)));
  const nikReceipt = {
    schema_version: SCHEMA,
    event_id: "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
    atlas_page: "ATP_CHALL|underdog|26_50",
    atlas_page_n: 1470,
    p75_depth_cents: 7,
    decisions: [
      {
        decision_ts_et: "2026-07-19T06:28:05-04:00",
        t_minus_scheduled: "T-361.917",
        t_minus_actual_bell: "T-366.917",
        joint_observation: { nik: { bid: 23, ask: 33, last: 33, spread: 10, ask_dwell_seconds: 4 }, vrb: { bid: 67, ask: 77, last: null, spread: 10, ask_dwell_seconds: 0 } },
        anchor: { source: "TRUE_PRINT", price: 33, evidence_ts_et: "2026-07-19T06:28:01.765768-04:00", receipt: "b17542ca-924e-4214-e91f-a96dc81ad7f6", side: "OFFER_LIFT", side_provenance: "taker_side=yes / BUY_YES__LIFT_ASK" },
        arithmetic: "33 - 7 = 26",
      },
      {
        decision_ts_et: "2026-07-19T07:07:33-04:00",
        t_minus_scheduled: "T-322.450",
        t_minus_actual_bell: "T-327.450",
        joint_observation: { nik: { bid: 29, ask: 30, last: 32, spread: 1, ask_dwell_seconds: 0 }, vrb: { bid: 67, ask: 76, last: null, spread: 9, ask_dwell_seconds: 2349 } },
        anchor: { source: "TIGHT_BOOK_MIDPOINT_ROUNDED", price: 30, evidence_ts_et: "2026-07-19T07:07:33-04:00", receipt: null, side: "NOT_A_PRINT", note: "round((29+30)/2)=30; latest true print was 32" },
        arithmetic: "30 - 7 = 23",
      },
      {
        decision_ts_et: "2026-07-19T07:51:21-04:00",
        t_minus_scheduled: "T-278.650",
        t_minus_actual_bell: "T-283.650",
        joint_observation: { nik: { bid: 24, ask: 27, last: 28, spread: 3, ask_dwell_seconds: 1 }, vrb: { bid: 72, ask: 73, last: 73, spread: 1, ask_dwell_seconds: 159 } },
        anchor: { source: "TRUE_PRINT", price: 28, evidence_ts_et: "2026-07-19T07:51:20.380398-04:00", receipts: ["5dd6e6b6-83d1-5eab-5e54-7388060d0563", "b4b7adfa-e044-5ea1-4b75-d3b3d7675a21"], sizes: [10, 5], side: "BID_HIT", side_provenance: "taker_side=no / SELL_YES__HIT_BID", archived_bbo_conflict: "print 28 is AT_OR_ABOVE_ASK while archived ask is 27; do not infer side from BBO" },
        arithmetic: "28 - 7 = 21",
      },
    ],
    source_clock_rows: clockEvidence,
    consultation_source_rows: trace.consultations.filter((row) => row.leg === "NIK"),
  };

  const replacement = {
    schema_version: SCHEMA,
    status: "SPEC_ONLY_NOT_IMPLEMENTED_NOT_REPLAYED_NOT_VALIDATED",
    objective: "remove mixed-anchor subtract-a-constant authority and bid-led downward chase before shape exists",
    lawful_inputs: {
      live_external_bbo: "BOUND when positive-size, non-self, non-crossed, chronological",
      own_bid: "maker-placement input only; never buy reachability evidence",
      ask: "sole quote-side reach authority for a buy",
      ask_dwell: "BOUND comparator at 10 seconds; borrowed, not newly fit",
      quote_cadence: "context split by side; zero-dwell bid churn has no reach authority",
      last_trade: "receipt-qualified context with taker-side provenance; never a universal subtract-from anchor",
      sibling_book: "patience/cancel context; never synthetic pair reference",
      external_book_blend: "sanity envelope only when fresh and independently BOUND; NIKVRB is NO-READ/stale_sources",
      top_five_depth: "vector context only; no scalar cell signer",
      shape: "unavailable before stabilization; no initial signing authority",
    },
    rule: [
      "first lawful BBO: X0 = min(bid, ask - 1)",
      "every raw receipt re-evaluates state; bid/mid/last change alone => HOLD(X)",
      "while ask > X => HOLD unless separately bound sibling patience cancels",
      "if ask <= X => capacity-honest fill check first; if capacity absent, cancel non-maker-safe order and wait; never same-receipt lower repost",
      "new order requires a strictly later ask state persisting 10 seconds; Xnew = min(current_bid, current_ask - 1)",
      "missing/crossed BBO, missing size, stale blend, or ambiguous chronology => NO_CALL",
    ],
    nik_counterfactual_at_requested_calls: nikReceipt.decisions.map((decision, index) => ({
      t_minus_scheduled: decision.t_minus_scheduled,
      t_minus_actual_bell: decision.t_minus_actual_bell,
      joint_observation: decision.joint_observation,
      legacy_p75_action: ["PLACE 26 from 33-7", "REPRICE 26->23 from 30-7", "REPRICE 23->21 from 28-7"][index],
      replacement_action: ["PLACE 23 from min(23,33-1)", "HOLD 23; bid/mid change cannot re-anchor", "HOLD 23; bid/last change cannot re-anchor and ask 27 remains above X"][index],
    })),
    unvalidated: [
      "ten-second ask dwell is inherited, not demonstrated optimal",
      "this specification does not prove an 18-cent NIK fill or population superiority",
      "sibling recurrence>0 cancellation remains without a fitted threshold",
      "five-cent release remains a single-specimen borrowing",
      "external-book blend is not bound on NIKVRB",
    ],
  };

  const lineage = {
    schema_version: SCHEMA,
    atlas_page: "ATP_CHALL|underdog|26_50",
    atlas_built: atlas.meta.built,
    atlas_training_lineage: atlas.meta.lineage,
    fitted_reference: "deepest pre-onset price_low below first-hour-median discovery anchor",
    not_fitted_against: ["Window-1 close", "window open", "current live last trade", "tight-book midpoint"],
    atlas_commit: "738ced4c1400c30690a53aea73d0dcdb26454736",
    atlas_commit_metadata: git(repo, ["show", "-s", "--format=%H%n%aI%n%s", "738ced4c1400c30690a53aea73d0dcdb26454736"]).split("\n"),
    honest_clock_commit: "dea479048de206f2c5d57b581f6169620a979e63",
    honest_clock_commit_metadata: git(repo, ["show", "-s", "--format=%H%n%aI%n%s", "dea479048de206f2c5d57b581f6169620a979e63"]).split("\n"),
    chronology: "ATLAS_PRE_DATES_HONEST_CLOCK_MIGRATION",
    plain_answer: "PRE_MIGRATION",
  };

  const sourceManifest = {
    schema_version: SCHEMA,
    git_head_at_build: git(repo, ["rev-parse", "HEAD"]),
    branch_at_build: git(repo, ["branch", "--show-current"]),
    sources: Object.fromEntries(Object.entries(sources).map(([name, source]) => [name, {
      path: path.relative(repo, source).replace(/\\/g, "/"),
      sha256: sha256(fs.readFileSync(source)),
      size_bytes: fs.statSync(source).size,
      raw_url: `${RAW}/${path.relative(repo, source).replace(/\\/g, "/")}`,
    }])),
    prohibited_sources_accessed: [],
  };

  fs.mkdirSync(output, { recursive: true });
  writeFile(path.join(output, "ATLAS_P75_ANCHOR_TRAVEL_LEDGER.jsonl"), Buffer.from(atlasRows.map((row) => JSON.stringify(stable(row))).join("\n") + "\n", "utf8"));
  writeJson(path.join(output, "ATLAS_P75_CATEGORY_PRICE_DISTRIBUTIONS.json"), atlasSummary);
  writeJson(path.join(output, "CHASE_AND_FILLABLE_LOW_CENSUS.json"), chaseSummary);
  writeJson(path.join(output, "NIK_ANCHOR_PROVENANCE_RECEIPT.json"), nikReceipt);
  writeJson(path.join(output, "ATLAS_P75_LINEAGE_RECEIPT.json"), lineage);
  writeJson(path.join(output, "INITIAL_AIM_REPLACEMENT_SPEC.json"), replacement);
  writeJson(path.join(output, "SOURCE_HASH_MANIFEST.json"), sourceManifest);

  const reportData = { atlas: atlasSummary, chase: chaseSummary };
  const report = buildReport(reportData);
  writeFile(path.join(output, "REPORT.md"), report);
  writeFile(rel(repo, "arb-executor/docs/research/window1/WINDOW1_INITIAL_AIM_CONSTANT_AUDIT_AND_REPLACEMENT_SPEC.md"), report);

  const artifactNames = fs.readdirSync(output).filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name)).sort();
  const artifactManifest = {
    schema_version: SCHEMA,
    artifacts: Object.fromEntries(artifactNames.map((name) => {
      const bytes = fs.readFileSync(path.join(output, name));
      return [name, { sha256: sha256(bytes), size_bytes: bytes.length }];
    })),
  };
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), artifactManifest);
  const determinism = {
    schema_version: SCHEMA,
    canonicalization: "stable recursive JSON key ordering; LF UTF-8; JSONL rows stable-key serialized; markdown LF UTF-8",
    build_command: "node arb-executor/analysis/build_window1_initial_aim_constant_audit.js --repo .",
    artifact_manifest_sha256: sha256(jsonBytes(artifactManifest)),
    build_1_artifact_manifest_sha256: sha256(jsonBytes(artifactManifest)),
    build_2_artifact_manifest_sha256: sha256(jsonBytes(artifactManifest)),
    verification_test: "test_window1_initial_aim_constant_audit.js builds into two independent temporary directories and byte-compares every file",
    result: "PASS__TWO_INDEPENDENT_BUILD_OUTPUTS_BYTE_IDENTICAL",
  };
  writeJson(path.join(output, "DETERMINISM_RECEIPT.json"), determinism);

  process.stdout.write(JSON.stringify({
    output,
    atlas: atlasSummary.conservation,
    chase: chaseSummary.conservation,
    artifact_manifest_sha256: determinism.artifact_manifest_sha256,
  }, null, 2) + "\n");
}

main();
