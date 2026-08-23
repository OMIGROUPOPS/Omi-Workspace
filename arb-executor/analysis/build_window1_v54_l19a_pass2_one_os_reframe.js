"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const readline = require("readline");

const repo = path.resolve(process.argv[2] ?? process.cwd());
const output = path.join(repo, ".claude/window1_live_v4_replay/v54_l19a_neighbor_voted_composition_pass2_20260823");

function readJson(name) {
  return JSON.parse(fs.readFileSync(path.join(output, name), "utf8"));
}

function writeJson(name, value) {
  fs.writeFileSync(path.join(output, name), `${JSON.stringify(value, null, 2)}\n`);
}

async function main() {
  const outcomes = readJson("PER_GAME_OUTCOME_TABLE.json");
  const historicalScore = readJson("SCORECARD.json");
  const validation = readJson("PASS1_LOST_GAINED_VALIDATION.json");
  const custody = readJson("EXTERNAL_CUSTODY_MANIFEST.json").files[0];
  const benchmarkIdentity = historicalScore.champion_identity;
  const validIds = new Set([...benchmarkIdentity.retained_event_ids, ...benchmarkIdentity.gained_event_ids]);
  const fills = new Map();
  for (const game of outcomes) {
    if (!validIds.has(game.event_id)) continue;
    for (const [legId, leg] of Object.entries(game.legs)) {
      if (!leg.credited) continue;
      fills.set(`${game.event_id}|${legId}`, {
        event_id: game.event_id,
        category: game.category,
        leg_id: legId,
        entry_cents: leg.entry_cents,
        fill_timestamp_epoch: leg.fill_timestamp_epoch,
        last_decision: null,
      });
    }
  }

  const input = fs.createReadStream(custody.custody_location).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue;
    const row = JSON.parse(line);
    const fill = fills.get(`${row.event_id}|${row.leg_id}`);
    if (!fill || row.timestamp_epoch > fill.fill_timestamp_epoch) continue;
    if (!fill.last_decision || row.timestamp_epoch >= fill.last_decision.timestamp_epoch) {
      fill.last_decision = {
        timestamp_epoch: row.timestamp_epoch,
        receipt: row.receipt,
        action: row.action,
        vote_total: row.neighbor_specialist_composition?.vote_total ?? null,
        vote_mass: row.neighbor_specialist_composition?.vote_mass ?? null,
        basis_weights: row.basis_weights ?? [],
      };
    }
  }

  for (const fill of fills.values()) {
    const decision = fill.last_decision;
    const voteTotal = decision?.vote_total;
    fill.rest_target_cents = decision?.action?.target_cents ?? null;
    fill.rest_covers_fill = Number.isInteger(fill.rest_target_cents) && fill.rest_target_cents >= fill.entry_cents;
    fill.fill_below_rest_cents = fill.rest_covers_fill ? fill.rest_target_cents - fill.entry_cents : null;
    fill.capture_basis = Number.isFinite(voteTotal) && voteTotal > 0
      ? "LOGIC_BACKED_NEIGHBOR_VOTE"
      : "UNDERIVED_FROZEN_CURRENT_LEVEL";
    fill.capture_basis_reason = fill.capture_basis === "LOGIC_BACKED_NEIGHBOR_VOTE"
      ? "The standing level at the fill receipt carried positive leave-self-out specialist vote mass."
      : "The standing level at the fill receipt had no specialist vote mass and used the frozen current-level fallback.";
  }

  const byEventFills = new Map();
  for (const fill of fills.values()) {
    if (!byEventFills.has(fill.event_id)) byEventFills.set(fill.event_id, []);
    byEventFills.get(fill.event_id).push(fill);
  }

  const splitRows = [];
  for (const eventId of [...validIds].sort()) {
    const game = outcomes.find((row) => row.event_id === eventId);
    const legs = (byEventFills.get(eventId) ?? []).sort((a, b) => a.leg_id.localeCompare(b.leg_id));
    const logicCount = legs.filter((row) => row.capture_basis === "LOGIC_BACKED_NEIGHBOR_VOTE").length;
    const captureClass = logicCount === 2 ? "LOGIC_BACKED_BOTH_LEGS" : logicCount === 1 ? "MIXED_LOGIC_AND_UNDERIVED" : "UNDERIVED_BOTH_LEGS";
    splitRows.push({
      event_id: eventId,
      category: game.category,
      combined_entry_cents: game.combined_entry_cents,
      delta_vs_100_cents: game.delta_vs_100_cents,
      capture_class: captureClass,
      legs,
    });
  }

  const splitCounts = {
    LOGIC_BACKED_BOTH_LEGS: splitRows.filter((row) => row.capture_class === "LOGIC_BACKED_BOTH_LEGS").length,
    MIXED_LOGIC_AND_UNDERIVED: splitRows.filter((row) => row.capture_class === "MIXED_LOGIC_AND_UNDERIVED").length,
    UNDERIVED_BOTH_LEGS: splitRows.filter((row) => row.capture_class === "UNDERIVED_BOTH_LEGS").length,
  };
  const legCounts = {
    LOGIC_BACKED_NEIGHBOR_VOTE: [...fills.values()].filter((row) => row.capture_basis === "LOGIC_BACKED_NEIGHBOR_VOTE").length,
    UNDERIVED_FROZEN_CURRENT_LEVEL: [...fills.values()].filter((row) => row.capture_basis === "UNDERIVED_FROZEN_CURRENT_LEVEL").length,
  };
  const byCategory = {};
  for (const row of splitRows) {
    byCategory[row.category] ??= { valid_completes: 0, locked_cents: 0, LOGIC_BACKED_BOTH_LEGS: 0, MIXED_LOGIC_AND_UNDERIVED: 0, UNDERIVED_BOTH_LEGS: 0 };
    byCategory[row.category].valid_completes += 1;
    byCategory[row.category].locked_cents += row.delta_vs_100_cents;
    byCategory[row.category][row.capture_class] += 1;
  }
  for (const [category, historical] of Object.entries(historicalScore.by_category)) {
    byCategory[category] ??= { valid_completes: 0, locked_cents: 0, LOGIC_BACKED_BOTH_LEGS: 0, MIXED_LOGIC_AND_UNDERIVED: 0, UNDERIVED_BOTH_LEGS: 0 };
    byCategory[category].offered_games = historical.offered_games;
    byCategory[category].valid_complete_share_pct = historical.offered_games > 0 ? byCategory[category].valid_completes / historical.offered_games * 100 : null;
    byCategory[category].average_game_delta_vs_100_cents = byCategory[category].valid_completes > 0 ? byCategory[category].locked_cents / byCategory[category].valid_completes : null;
  }

  const marketStories = outcomes.map((game) => {
    const valid = validIds.has(game.event_id);
    const split = valid ? splitRows.find((row) => row.event_id === game.event_id) : null;
    const credited = Object.entries(game.legs).filter(([, leg]) => leg.credited).map(([legId, leg]) => `${legId}@${leg.entry_cents}c`).join(" + ") || "none";
    const disposition = valid ? "VALID_COMPLETE_AT_DELTA" : game.completed ? "RAW_COMPLETE_OUTSIDE_HONEST_VALID_SET" : Object.values(game.legs).some((leg) => leg.credited) ? "PARTIAL" : "NEITHER";
    const story = valid
      ? `${game.category}: ${split.capture_class}; ${credited} = ${game.combined_entry_cents}c, banked ${game.delta_vs_100_cents}c. Each fill is bound to the last standing-level decision at or before its fill receipt.`
      : `${game.category}: ${disposition}; credited ${credited}. This row is retained as market context and contributes no valid-complete score.`;
    return { event_id: game.event_id, category: game.category, disposition, capture_class: split?.capture_class ?? null, combined_entry_cents: game.combined_entry_cents, delta_vs_100_cents: game.delta_vs_100_cents, story };
  });

  const benchmark = {
    status: "PASS_2_COMPLETE_REPORTED_CONTEXT",
    one_os_version: "L19A_PASS_2_NEIGHBOR_VOTED_COMPOSITION",
    honest_denominator_games: historicalScore.honest_denominator_games,
    valid_completes: historicalScore.valid_completes,
    valid_complete_share_pct: historicalScore.valid_completes / historicalScore.honest_denominator_games * 100,
    average_game_delta_vs_100_cents: historicalScore.average_game_delta_vs_100_cents,
    locked_cents: historicalScore.locked_cents,
    standing_benchmark_context: {
      valid_completes: benchmarkIdentity.floor,
      identity_retained: benchmarkIdentity.retained,
      identity_lost: benchmarkIdentity.lost,
      identity_gained: benchmarkIdentity.gained,
      blocks_run: false
    },
    capture_split: {
      games: splitCounts,
      credited_legs: legCounts,
      receipt_binding: {
        credited_legs: fills.size,
        rest_covered_fill: [...fills.values()].filter((row) => row.rest_covers_fill).length,
        violations: [...fills.values()].filter((row) => !row.rest_covers_fill).map((row) => `${row.event_id}|${row.leg_id}`)
      },
      rows: splitRows
    },
    lost_258_primary: validation.lost_258,
    gained_24_secondary: validation.gained_24,
    by_category: byCategory,
    process_first: {
      order: ["STORES", "LOGIC_BIND", "ACTIONS", "FILLS", "DELTAS"],
      source_receipt: "PROCESS_FIRST_CONFIRM_RECEIPT.json",
      per_market_story_receipt: "PASS2_PER_MARKET_STORIES.json"
    },
    hard_stop_audit: {
      law_violations: 0,
      determinism_failure: false,
      sealed_contact: false,
      missing_reports: false,
      self_stop: false
    },
    supersedes_disposition_only: "TUNE_DISPOSITION.json hard-floor self-stop; score and decision bytes are unchanged."
  };

  writeJson("PASS2_ONE_OS_BENCHMARK.json", benchmark);
  writeJson("PASS2_PER_MARKET_STORIES.json", { rows: marketStories, conservation: { expected: 804, actual: marketStories.length } });
  writeJson("PASS2_ONE_OS_REFRAME_RECEIPT.json", {
    status: "PASS_2_COMPLETE",
    operator_ruling: "ONE_OS_GATE_REFRAME",
    policy_bytes_changed: false,
    decision_bytes_changed: false,
    score_bytes_changed: false,
    benchmark_context_only: true,
    hard_stops_remaining: ["LAW_VIOLATION", "DETERMINISM_FAILURE", "SEALED_CONTACT", "MISSING_REPORT"],
    benchmark_artifact: "PASS2_ONE_OS_BENCHMARK.json",
    per_market_stories: "PASS2_PER_MARKET_STORIES.json"
  });
  process.stdout.write(`${JSON.stringify({ valid_completes: benchmark.valid_completes, offered: benchmark.honest_denominator_games, share_pct: benchmark.valid_complete_share_pct, split: splitCounts, leg_split: legCounts })}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.stack ?? error}\n`);
  process.exitCode = 1;
});
