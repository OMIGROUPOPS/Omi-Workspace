#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const readline = require("readline");
const crypto = require("crypto");

const V41_COMMIT = "96d33316b0c0020b46b71569fcdbadeaa97a64e3";
const TEMPLATE_COMMIT = "bd9e2afdcc5a8c4414438771d33c8229fb2bf1cd";
const PACKAGE_REL = ".claude/window1_live_v4_replay/v41_maker_machine_20260808";
const TARGETS = [
  { code: "ROUJAK", eventId: "KXWTACHALLENGERMATCH-26JUL12ROUJAK" },
  { code: "PUTJEA", eventId: "KXWTAMATCH-26JUL14PUTJEA" },
];

function parseArgs(argv) {
  const out = { repo: ".", out: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === "--repo") out.repo = argv[++i];
    else if (argv[i] === "--out") out.out = argv[++i];
    else throw new Error(`unknown argument: ${argv[i]}`);
  }
  out.repo = path.resolve(out.repo);
  out.out = path.resolve(out.out || path.join(out.repo, PACKAGE_REL, "exemplar_packs"));
  return out;
}

async function readGzipJsonl(file) {
  const rows = [];
  const input = fs.createReadStream(file).pipe(zlib.createGunzip());
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) if (line) rows.push(JSON.parse(line));
  return rows;
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function et(epoch) {
  if (epoch === null || epoch === undefined) return null;
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(epoch * 1000));
  const p = Object.fromEntries(parts.map((x) => [x.type, x.value]));
  return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}:${p.second}`;
}

function clock(row) {
  return {
    timestamp_epoch: row.timestamp_epoch,
    timestamp_et: et(row.timestamp_epoch),
    t_minus_scheduled_seconds: row.t_minus_scheduled_seconds,
    t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds,
    t_minus_pre_match_boundary_seconds: row.t_minus_pre_match_boundary_seconds,
  };
}

function restMark(row) {
  return {
    ...clock(row),
    kind: row.kind,
    target_cents: row.target_cents,
    state: row.state,
    reason: row.reason,
    pulse_floor_cents: row.pulse_floor_cents,
    receipt: row.receipt,
  };
}

function fillMark(row) {
  return {
    ...clock(row),
    kind: row.kind,
    entry_cents: row.entry_cents,
    fill_class: row.fill_class,
    fill_source_state: row.fill_source_state,
    evidence: row.evidence,
    receipt: row.receipt,
  };
}

function capMark(row) {
  return {
    ...clock(row),
    kind: row.kind,
    first_fill_cents: row.first_fill_cents,
    pair_cap_cents: row.pair_cap_cents,
    receipt: row.receipt,
  };
}

function legCode(identity) {
  return identity.split("|").at(-1);
}

async function main() {
  const args = parseArgs(process.argv);
  const pkg = path.join(args.repo, PACKAGE_REL);
  const actionFile = path.join(pkg, "ACTION_TRACE.jsonl.gz");
  const decisionFile = path.join(pkg, "DECISION_TRACE_1608.jsonl.gz");
  const eventFile = path.join(pkg, "MARKET_EVENT_LEDGER.jsonl.gz");
  const manifestFile = path.join(pkg, "ARTIFACT_HASH_MANIFEST.json");
  const [actions, decisions, events] = await Promise.all([
    readGzipJsonl(actionFile),
    readGzipJsonl(decisionFile),
    readGzipJsonl(eventFile),
  ]);
  const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  fs.mkdirSync(args.out, { recursive: true });

  for (const target of TARGETS) {
    const event = events.find((x) => x.event_id === target.eventId && x.mode === "MARKET_UNION_REACH");
    if (!event) throw new Error(`missing market event row: ${target.eventId}`);
    const eventActions = actions.filter((x) => x.event_id === target.eventId && x.mode === "MARKET_UNION_REACH");
    const eventDecisions = decisions.filter((x) => x.event_id === target.eventId);
    if (eventDecisions.length > 2) throw new Error(`unexpected duplicate decision rows: ${target.eventId}`);
    const legs = {};
    for (const [code, ledgerLeg] of Object.entries(event.legs)) {
      const identity = ledgerLeg.leg_identity;
      const legActions = eventActions.filter((x) => x.leg_identity === identity);
      const restRows = legActions.filter((x) => x.kind === "PLACE_REST" || x.kind === "REPRICE_REST");
      const joinRows = restRows.filter((x) => String(x.reason).includes("PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1"));
      const fills = legActions.filter((x) => x.kind === "FILL");
      const caps = legActions.filter((x) => x.kind === "PAIR_ARM");
      const decision = eventDecisions.find((x) => x.leg_identity === identity) || null;
      legs[code] = {
        ticker: ledgerLeg.ticker,
        leg_identity: identity,
        global_direction: ledgerLeg.leg_direction,
        price_region: ledgerLeg.price_region,
        credited: ledgerLeg.credited,
        entry_cents: ledgerLeg.entry_cents,
        fill_class: ledgerLeg.fill_class,
        fill_timestamp_epoch: ledgerLeg.fill_timestamp_epoch,
        fill_timestamp_et: et(ledgerLeg.fill_timestamp_epoch),
        terminal_state: decision ? decision.terminal_state : ledgerLeg.final_state,
        terminal_reason: ledgerLeg.terminal_reason,
        terminal_rest_cents: decision ? decision.terminal_rest_cents : ledgerLeg.resting_target_at_edge_cents,
        pair_cap_cents: decision ? decision.pair_cap_cents : ledgerLeg.pair_cap_cents,
        rest_trajectory: {
          transition_count: restRows.length,
          rows: restRows.map(restMark),
        },
        join_commit_events: joinRows.map(restMark),
        fills: fills.map(fillMark),
        cap_events: caps.map(capMark),
        conservation: {
          places: restRows.filter((x) => x.kind === "PLACE_REST").length,
          reprices: restRows.filter((x) => x.kind === "REPRICE_REST").length,
          joins: joinRows.length,
          fills: fills.length,
          caps: caps.length,
        },
      };
    }

    const output = {
      schema_version: "V41_DECISION_MARKS_STANDING_V1",
      source_binding: {
        v41_commit: V41_COMMIT,
        standing_template_commit: TEMPLATE_COMMIT,
        standing_template_path: `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/${target.code}_DECISION_MARKS.json`,
        source_files: {
          ACTION_TRACE: { sha256: manifest.files["ACTION_TRACE.jsonl.gz"].sha256 },
          DECISION_TRACE_1608: { sha256: manifest.files["DECISION_TRACE_1608.jsonl.gz"].sha256 },
          MARKET_EVENT_LEDGER: { sha256: manifest.files["MARKET_EVENT_LEDGER.jsonl.gz"].sha256 },
        },
        replay_invocations: 0,
        extraction_scope: "READ_ONLY_MARKET_UNION_REACH_ROWS_FROM_FROZEN_V41_PACKAGE",
      },
      event: event.event_id,
      code: target.code,
      category: event.category,
      bell_confidence: event.bell_confidence,
      walkthrough_class: event.completed_pair ? "completed" : Object.values(event.legs).some((x) => x.credited) ? "carried" : "skipped",
      combined_entry_cents: event.combined_entry_cents,
      pair_under_par: event.pair_under_par,
      completed_pair: event.completed_pair,
      w1_span: {
        left: event.w1_left_epoch,
        left_et: et(event.w1_left_epoch),
        right: event.w1_right_epoch,
        right_et: et(event.w1_right_epoch),
      },
      template: "DUAL_TIMELINE_V2 + DECISION_MARKS (standing exemplar template)",
      legs,
      event_conservation: {
        market_action_rows: eventActions.length,
        rest_transition_rows: Object.values(legs).reduce((n, x) => n + x.rest_trajectory.transition_count, 0),
        fill_rows: Object.values(legs).reduce((n, x) => n + x.fills.length, 0),
        cap_rows: Object.values(legs).reduce((n, x) => n + x.cap_events.length, 0),
        leg_rows: Object.keys(legs).length,
        leg_codes_match_identity: Object.entries(legs).every(([code, x]) => legCode(x.leg_identity) === code),
      },
    };
    const outFile = path.join(args.out, `${target.code}_V41_DECISION_MARKS.json`);
    fs.writeFileSync(outFile, `${JSON.stringify(output, null, 1)}\n`);
  }

  const receipt = {
    schema_version: "V41_DECISION_MARKS_EXTRACTION_RECEIPT_V1",
    source_v41_commit: V41_COMMIT,
    standing_template_commit: TEMPLATE_COMMIT,
    replay_invocations: 0,
    files: Object.fromEntries(TARGETS.map((x) => {
      const file = path.join(args.out, `${x.code}_V41_DECISION_MARKS.json`);
      return [path.basename(file), { sha256: sha256(file), bytes: fs.statSync(file).size }];
    })),
  };
  fs.writeFileSync(path.join(args.out, "EXTRACTION_RECEIPT.json"), `${JSON.stringify(receipt, null, 1)}\n`);
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
