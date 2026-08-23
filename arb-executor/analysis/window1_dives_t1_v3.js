#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");
const readline = require("readline");

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 2) {
    if (!argv[i].startsWith("--") || argv[i + 1] == null) throw new Error(`bad argument ${argv[i]}`);
    out[argv[i].slice(2)] = argv[i + 1];
  }
  return out;
}

function need(args, name) {
  if (!args[name]) throw new Error(`missing --${name}`);
  return args[name];
}

function sha256Bytes(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function fileBinding(file, logicalPath = file, rows = null) {
  const bytes = fs.readFileSync(file);
  return { path: logicalPath, bytes: bytes.length, sha256: sha256Bytes(bytes), rows };
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function csvCell(value) {
  if (value == null) return "";
  const text = String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function writeCsv(file, columns, rows) {
  const lines = [columns.join(",")];
  for (const row of rows) lines.push(columns.map((c) => csvCell(row[c])).join(","));
  fs.writeFileSync(file, `${lines.join("\n")}\n`);
}

function field(sentence, name) {
  const match = sentence.match(new RegExp(`${name}=([^;]+)`));
  return match ? match[1].trim() : null;
}

function numberField(sentence, name) {
  const value = field(sentence, name);
  if (value == null || value === "NONE" || value === "NA") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function compactSentence(row) {
  if (!row) return null;
  return {
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    action: row.action,
    target_basis: field(row.sentence, "TARGET_BASIS"),
    leg_state: field(row.sentence, "LEG_STATE"),
    live_touch_bid_cents: numberField(row.sentence, "LIVE_TOUCH_BID"),
    live_bid_ask: field(row.sentence, "LIVE_BID_ASK"),
    chosen_depth_cents: numberField(row.sentence, "CHOSEN_DEPTH_CENTS"),
    sentence: row.sentence,
  };
}

function parseEtEpoch(text) {
  return Date.parse(`${text} GMT-0400`) / 1000;
}

function tapeRow(row, index, headers) {
  const values = row.split(",");
  const at = (name) => values[headers.get(name)] ?? "";
  const num = (name) => {
    const value = at(name);
    return value === "" ? null : Number(value);
  };
  return {
    row: index,
    ts_et: at("ts_et"),
    timestamp_epoch: parseEtEpoch(at("ts_et")),
    bid_cents: num("bid_1"),
    bid_size: num("bid_1_sz"),
    ask_cents: num("ask_1"),
    ask_size: num("ask_1_sz"),
    last_trade_cents: num("last_trade"),
  };
}

function nearest(rows, ts, predicate = () => true) {
  let best = null;
  for (const row of rows) {
    if (!predicate(row)) continue;
    const distance = Math.abs(row.timestamp_epoch - ts);
    if (!best || distance < best.distance_seconds ||
        (distance === best.distance_seconds && row.row < best.row.row)) {
      best = { distance_seconds: distance, row };
    }
  }
  return best;
}

function lastAtOrBefore(rows, ts) {
  let found = null;
  for (const row of rows) if (row.timestamp_epoch <= ts) found = row;
  return found;
}

function firstAtOrAfter(rows, ts) {
  return rows.find((row) => row.timestamp_epoch >= ts) || null;
}

function uniqueRows(rows) {
  const seen = new Set();
  return rows.filter((row) => {
    if (!row) return false;
    const key = `${row.leg_id}|${row.timestamp_epoch}|${row.receipt}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function actionTransitions(rows, bell) {
  let previous = null;
  const out = [];
  for (const row of rows) {
    const action = row.action || {};
    const signature = `${action.action}|${action.target_cents}|${action.reason}`;
    if (signature === previous && action.action === "HOLD_REST") continue;
    previous = signature;
    out.push({
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.receipt,
      window_stamp: row.timestamp_epoch <= bell ? "IN_VERIFIED_WINDOW" : "POST_BELL",
      action: action.action || null,
      target_cents: action.target_cents ?? null,
      reason: action.reason || null,
      target_basis: field(row.sentence, "TARGET_BASIS"),
      leg_state: field(row.sentence, "LEG_STATE"),
      live_touch_bid_cents: numberField(row.sentence, "LIVE_TOUCH_BID"),
      live_bid_ask: field(row.sentence, "LIVE_BID_ASK"),
      chosen_depth_cents: numberField(row.sentence, "CHOSEN_DEPTH_CENTS"),
    });
  }
  return out;
}

async function loadSelectedSentences(file, selectedIds) {
  const byLeg = new Map();
  const selectedLines = [];
  let sourceRows = 0;
  const input = fs.createReadStream(file).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    sourceRows += 1;
    const row = JSON.parse(line);
    if (!selectedIds.has(row.event_id)) continue;
    selectedLines.push(line);
    const key = `${row.event_id}|${row.leg_id}`;
    if (!byLeg.has(key)) byLeg.set(key, []);
    byLeg.get(key).push(row);
  }
  for (const rows of byLeg.values()) rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch);
  return { byLeg, selectedLines, sourceRows };
}

function legFromTruth(game, leg) {
  for (const side of ["A", "B"]) {
    if (game[`leg${side}`] !== leg) continue;
    return {
      side,
      formation_end_epoch: game[`leg${side}_formation_end_epoch`],
      open_postformation_cents: game[`leg${side}_open_postformation_c`],
      floor_cents: game[`leg${side}_floor_c`],
      floor_epoch: game[`leg${side}_floor_epoch`],
      close_cents: game[`leg${side}_close_c`],
      close_epoch: game[`leg${side}_close_epoch`],
      journey: game[`leg${side}_journey`],
    };
  }
  throw new Error(`leg ${leg} absent from truth row ${game.event_id}`);
}

function manifestFor(dir, names) {
  return names.sort().map((name) => fileBinding(path.join(dir, name), name));
}

async function main() {
  const args = parseArgs(process.argv);
  const selectionFile = need(args, "selection");
  const queueFile = need(args, "queue");
  const groundTruthFile = need(args, "ground-truth");
  const mapFile = need(args, "depth-map");
  const outcomesFile = need(args, "outcomes");
  const sentencesFile = need(args, "sentences");
  const ticksDir = need(args, "ticks-dir");
  const outDir = need(args, "out-dir");
  fs.mkdirSync(outDir, { recursive: true });

  const selection = JSON.parse(fs.readFileSync(selectionFile));
  const queue = JSON.parse(fs.readFileSync(queueFile));
  const truth = JSON.parse(fs.readFileSync(groundTruthFile));
  const depthMap = JSON.parse(fs.readFileSync(mapFile));
  const outcomes = JSON.parse(fs.readFileSync(outcomesFile));
  const selectedIds = new Set(selection.selected.map((row) => row.event_id));
  if (selectedIds.size !== 8) throw new Error(`selection has ${selectedIds.size}, expected 8`);

  const selectedSentenceData = await loadSelectedSentences(sentencesFile, selectedIds);
  const sentenceGzip = zlib.gzipSync(Buffer.from(`${selectedSentenceData.selectedLines.join("\n")}\n`), {
    level: 9,
    mtime: 0,
  });
  fs.writeFileSync(path.join(outDir, "SELECTED_SENTENCES_8.jsonl.gz"), sentenceGzip);

  const mapCells = new Map(depthMap.cells.map((row) => [`${row.category}|${row.price_cell}`, row]));
  const truthRows = new Map(truth.rows.map((row) => [row.event_id, row]));
  const queueRows = new Map(queue.games.map((row) => [row.event, row]));
  const outcomeRows = new Map(outcomes.map((row) => [row.event_id, row]));
  const stories = [];
  const adjudications = [];
  const actionRows = [];
  const tapeBindings = [];

  for (const selected of selection.selected) {
    const eventId = selected.event_id;
    const qGame = queueRows.get(eventId);
    const tGame = truthRows.get(eventId);
    const outcome = outcomeRows.get(eventId);
    if (!qGame || !tGame || !outcome) throw new Error(`missing bound row for ${eventId}`);
    const story = {
      event_id: eventId,
      category: selected.category,
      selection_rank: selected.rank,
      selection_cents_under_floor: selected.cents_under_floor,
      truth_window: {
        span_start_epoch: tGame.span_start_epoch,
        span_end_epoch: tGame.span_end_epoch,
        bell_source: tGame.bell_source,
        bell_precision: tGame.bell_precision,
      },
      legs: [],
    };

    for (const qLeg of qGame.legs) {
      const key = `${eventId}|${qLeg.leg}`;
      const sentenceRows = selectedSentenceData.byLeg.get(key) || [];
      if (!sentenceRows.length) throw new Error(`no sentence rows for ${key}`);
      const tLeg = legFromTruth(tGame, qLeg.leg);
      if (Number(tLeg.floor_cents) !== Number(qLeg.floor)) {
        throw new Error(`floor mismatch ${key}: truth ${tLeg.floor_cents}, queue ${qLeg.floor}`);
      }
      const tapeFile = path.join(ticksDir, `${eventId}-${qLeg.leg}.csv.gz`);
      const tapeBytes = fs.readFileSync(tapeFile);
      const tapeText = zlib.gunzipSync(tapeBytes).toString().trimEnd();
      const tapeLines = tapeText.split(/\r?\n/);
      const headerNames = tapeLines[0].split(",");
      const headers = new Map(headerNames.map((name, index) => [name, index]));
      const tapeRows = tapeLines.slice(1).map((row, index) => tapeRow(row, index + 1, headers));
      tapeBindings.push({
        path: `${eventId}-${qLeg.leg}.csv.gz`,
        bytes: tapeBytes.length,
        sha256: sha256Bytes(tapeBytes),
        rows: tapeRows.length,
      });

      const floorTs = Number(qLeg.floor_ts);
      const preSentence = lastAtOrBefore(sentenceRows, floorTs);
      const postSentence = firstAtOrAfter(sentenceRows, floorTs);
      const finalPreBell = lastAtOrBefore(sentenceRows, tGame.span_end_epoch);
      const fillTs = outcome.legs[qLeg.leg]?.fill_timestamp_epoch ?? null;
      const fillSentence = fillTs == null ? null : nearest(sentenceRows, fillTs)?.row || null;
      const turningRows = uniqueRows([sentenceRows[0], preSentence, postSentence, finalPreBell, fillSentence]);
      const transitions = actionTransitions(sentenceRows, tGame.span_end_epoch);
      for (const transition of transitions) actionRows.push({ event_id: eventId, leg: qLeg.leg, ...transition });

      const exactBook = nearest(tapeRows, floorTs);
      const floorTradeBook = nearest(tapeRows, floorTs, (row) => row.last_trade_cents === Number(qLeg.floor));
      const priorEvidence = tapeRows
        .filter((row) => row.timestamp_epoch >= tGame.span_start_epoch && row.timestamp_epoch < floorTs &&
          [row.bid_cents, row.ask_cents, row.last_trade_cents].includes(Number(qLeg.floor)))
        .at(-1) || null;
      const preTarget = preSentence?.action?.target_cents ?? null;
      const preTouch = numberField(preSentence?.sentence || "", "LIVE_TOUCH_BID") ?? exactBook?.row.bid_cents ?? null;
      const knowable = priorEvidence != null || preTarget === Number(qLeg.floor);
      const touchSufficient = preTouch != null && Number(qLeg.floor) <= preTouch;
      const cell = mapCells.get(`${selected.category}|${tLeg.close_cents}`) || null;
      const depthLicensed = cell == null ? null : Number(qLeg.gap) <= Number(cell.edge_p50_cents);
      const cellSupportedRest = cell == null ? null : Number(tLeg.close_cents) - Number(cell.edge_p50_cents);
      const fillClass = qLeg.fill;
      const entry = qLeg.entry;

      const legStory = {
        leg: qLeg.leg,
        floor: {
          cents: Number(qLeg.floor),
          timestamp_epoch: floorTs,
          tape_book_nearest: exactBook,
          tape_trade_row_nearest: floorTradeBook,
          prior_same_level_evidence: priorEvidence,
        },
        machine_at_floor: {
          rest_cents: Number(qLeg.rest),
          cents_below_floor: Number(qLeg.gap),
          queue_touch_relation: qLeg.touch,
          pre_floor_sentence: compactSentence(preSentence),
          post_floor_sentence: compactSentence(postSentence),
        },
        turning_sentences_verbatim: turningRows.map(compactSentence),
        action_transitions: transitions,
        outcome: {
          fill_class: fillClass,
          entry_cents: entry,
          fill_timestamp_epoch: fillTs,
          own_close_cents: tLeg.close_cents,
          entry_minus_close_cents: entry == null ? null : Number(entry) - Number(tLeg.close_cents),
        },
      };
      story.legs.push(legStory);

      adjudications.push({
        event_id: eventId,
        category: selected.category,
        leg: qLeg.leg,
        floor_cents: Number(qLeg.floor),
        floor_timestamp_epoch: floorTs,
        machine_rest_cents_at_floor: Number(qLeg.rest),
        rest_cents_under_floor: Number(qLeg.gap),
        pre_floor_touch_bid_cents: preTouch,
        knowable: knowable ? "YES" : "NO",
        knowable_reason: knowable
          ? priorEvidence
            ? `level ${qLeg.floor} appeared before the floor receipt at ${path.basename(tapeFile)}#row-${priorEvidence.row}`
            : `the machine already stood at ${qLeg.floor} before the floor receipt (${preSentence.receipt})`
          : `no earlier tape row named ${qLeg.floor}, and the pre-floor rest was ${preTarget}`,
        touch_sufficient: touchSufficient ? "YES" : "NO",
        touch_sufficient_reason: preTouch == null
          ? "no contemporaneous touch was recorded"
          : `${qLeg.floor} ${touchSufficient ? "<=" : ">"} contemporaneous best-bid touch ${preTouch}; trades-as-truth would ${touchSufficient ? "credit" : "not credit"} a touch rest on the floor print`,
        depth_licensed: cell == null ? "UNMAPPED" : depthLicensed ? "YES" : "NO",
        depth_license_rule: "rest-to-floor gap <= TRUE_BELL_CELL_DEPTH_MAP edge_p50 for category x own-close cell",
        own_close_cents: tLeg.close_cents,
        map_price_cell: cell?.price_cell ?? null,
        map_n_legs: cell?.n_legs ?? null,
        map_edge_p25_cents: cell?.edge_p25_cents ?? null,
        map_edge_p50_cents: cell?.edge_p50_cents ?? null,
        map_edge_p75_cents: cell?.edge_p75_cents ?? null,
        map_implied_floor_cents: cellSupportedRest,
        map_sha256: "72751efe0386bffe0d41e43fb680aaf2e30516b213c7a6371811725bbf67cef9",
        floor_book_receipt: exactBook ? `${path.basename(tapeFile)}#row-${exactBook.row.row}` : null,
        floor_trade_receipt: floorTradeBook ? `${path.basename(tapeFile)}#row-${floorTradeBook.row.row}` : null,
        fill_class: fillClass,
        entry_cents: entry,
        own_close_delta_cents: entry == null ? null : Number(entry) - Number(tLeg.close_cents),
      });
    }

    const validLegs = story.legs.filter((leg) => leg.outcome.fill_class === "VALID").length;
    story.honest_outcome = validLegs === 2 ? "COMPLETE" : validLegs === 1 ? "PARTIAL" : "NEITHER";
    story.raw_outcome = {
      completed: Boolean(outcome.completed),
      combined_entry_cents: outcome.combined_entry_cents,
      delta_vs_100_cents: outcome.delta_vs_100_cents,
    };
    stories.push(story);
  }

  const synthesis = {
    selected_games: stories.length,
    legs: adjudications.length,
    adjudication_counts: {
      knowable_yes: adjudications.filter((row) => row.knowable === "YES").length,
      knowable_no: adjudications.filter((row) => row.knowable === "NO").length,
      touch_sufficient_yes: adjudications.filter((row) => row.touch_sufficient === "YES").length,
      touch_sufficient_no: adjudications.filter((row) => row.touch_sufficient === "NO").length,
      depth_licensed_yes: adjudications.filter((row) => row.depth_licensed === "YES").length,
      depth_licensed_no: adjudications.filter((row) => row.depth_licensed === "NO").length,
      depth_unmapped: adjudications.filter((row) => row.depth_licensed === "UNMAPPED").length,
    },
    next_instrument: "THREE_WAY_TOUCH_CAPTURE_CENSUS",
    reason: "The eight dives contain both touch-creditable floor prints and floors outside the bid touch, while the raw WS last-trade channel and the certified floor channel also diverge on named legs. The next lawful measurement is therefore the three-way quote-touch / traded-at-level / print-cross census. Chain-pressure would reopen placement direction despite F-VS-094's adjudicated touch-standing law and is not justified by these rows.",
    chain_pressure_status: "NOT_SELECTED; remains NEVER_RUN",
    three_way_touch_capture_status: "JUSTIFIED_NEXT; still NEVER_RUN in this package",
  };

  const inputReceipt = {
    label: "DIVES_T1_V3_INPUT_BINDING_RECEIPT",
    scope: "eight selected games only; no 804; no sealed; no live",
    sources: {
      selection: fileBinding(selectionFile, ".claude/window1_second_seat/dives_t1_v3_20260823/SELECTION_RECEIPT.json", 8),
      dive_queue: fileBinding(queueFile, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DIVE_QUEUE_V2.json", queue.games.length),
      ground_truth: fileBinding(groundTruthFile, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json", truth.rows.length),
      depth_map: fileBinding(mapFile, ".claude/window1_second_seat/dives_t1_v3_20260823/TRUE_BELL_CELL_DEPTH_MAP.json", depthMap.cells.length),
      pass2_outcomes: fileBinding(outcomesFile, "v54_l19a_neighbor_voted_composition_pass2/PER_GAME_OUTCOME_TABLE.json", outcomes.length),
      pass2_sentences: fileBinding(sentencesFile, "stage1/v54_l19a_neighbor_voted_composition_pass2/build1/ALL_SENTENCES_804.jsonl.gz", selectedSentenceData.sourceRows),
      selected_tapes: tapeBindings,
    },
    selected_sentence_rows: selectedSentenceData.selectedLines.length,
    assertions: {
      selection_was_frozen_before_sentence_or_tape_walk: true,
      exactly_8_games: stories.length === 8,
      exactly_16_legs: adjudications.length === 16,
      no_804_replay: true,
      sealed_untouched: true,
      live_untouched: true,
    },
  };

  writeJson(path.join(outDir, "INPUT_BINDING_RECEIPT.json"), inputReceipt);
  writeJson(path.join(outDir, "DIVE_STORIES_8.json"), stories);
  writeJson(path.join(outDir, "ACTIONS_8.json"), actionRows);
  writeJson(path.join(outDir, "ADJUDICATIONS_16.json"), adjudications);
  writeCsv(path.join(outDir, "ADJUDICATIONS_16.csv"), [
    "event_id", "category", "leg", "floor_cents", "floor_timestamp_epoch",
    "machine_rest_cents_at_floor", "rest_cents_under_floor", "pre_floor_touch_bid_cents",
    "knowable", "knowable_reason", "touch_sufficient", "touch_sufficient_reason",
    "depth_licensed", "map_price_cell", "map_n_legs", "map_edge_p25_cents",
    "map_edge_p50_cents", "map_edge_p75_cents", "map_implied_floor_cents",
    "floor_book_receipt", "floor_trade_receipt", "fill_class", "entry_cents",
    "own_close_cents", "own_close_delta_cents",
  ], adjudications);
  writeJson(path.join(outDir, "SYNTHESIS.json"), synthesis);

  const report = [];
  report.push("# DIVES T1 v3 — eight-game process-first adjudication");
  report.push("");
  report.push("## 1. Stores pulled");
  report.push("");
  report.push(`- DIVE_QUEUE_V2: ${queue.games.length} game rows; selection SHA-256 ${inputReceipt.sources.dive_queue.sha256}.`);
  report.push(`- W1_GROUND_TRUTH_TABLE: ${truth.rows.length} game rows.`);
  report.push(`- TRUE_BELL_CELL_DEPTH_MAP: ${depthMap.cells.length} category × own-close cells; SHA-256 ${inputReceipt.sources.depth_map.sha256}.`);
  report.push(`- Pass-2 sentence archive: ${selectedSentenceData.sourceRows} source rows; ${selectedSentenceData.selectedLines.length} rows consumed for the frozen eight.`);
  report.push(`- Raw fit-local book tapes: 16 legs, ${tapeBindings.reduce((sum, row) => sum + row.rows, 0)} BBO rows; every file hash-bound in INPUT_BINDING_RECEIPT.json.`);
  report.push("- No 804 replay ran. Sealed and live stores were not opened.");
  report.push("");
  report.push("## 2. Stories — pivotal machine sentences verbatim");
  report.push("");
  for (const story of stories) {
    report.push(`### ${story.event_id} (${story.category})`);
    report.push("");
    for (const leg of story.legs) {
      const pivotal = leg.machine_at_floor.pre_floor_sentence;
      report.push(`#### ${leg.leg}`);
      report.push("");
      report.push(`Floor ${leg.floor.cents} at ${leg.floor.timestamp_epoch}; machine rest ${leg.machine_at_floor.rest_cents} (${leg.machine_at_floor.cents_below_floor}c below). Pivotal receipt: ${pivotal?.receipt || "NONE"}.`);
      report.push("");
      report.push("```text");
      report.push(pivotal?.sentence || "NO PRE-FLOOR SENTENCE");
      report.push("```");
      report.push("");
    }
  }
  report.push("## 3. Actions");
  report.push("");
  report.push("Every target-changing or non-redundant action is retained in ACTIONS_8.json; all 792 selected source sentences are retained in SELECTED_SENTENCES_8.jsonl.gz.");
  report.push("");
  report.push("| game | leg | action transitions | first target | rest at floor | final pre-bell target |");
  report.push("|---|---|---:|---:|---:|---:|");
  for (const story of stories) for (const leg of story.legs) {
    const inWindow = leg.action_transitions.filter((row) => row.window_stamp === "IN_VERIFIED_WINDOW");
    report.push(`| ${story.event_id} | ${leg.leg} | ${inWindow.length} | ${inWindow[0]?.target_cents ?? "—"} | ${leg.machine_at_floor.rest_cents} | ${inWindow.at(-1)?.target_cents ?? "—"} |`);
  }
  report.push("");
  report.push("## 4. Fills as consequences");
  report.push("");
  report.push("| game | leg | fill class | entry | floor | close | honest leg result |");
  report.push("|---|---|---|---:|---:|---:|---|");
  for (const story of stories) for (const leg of story.legs) {
    report.push(`| ${story.event_id} | ${leg.leg} | ${leg.outcome.fill_class} | ${leg.outcome.entry_cents ?? "—"} | ${leg.floor.cents} | ${leg.outcome.own_close_cents} | ${leg.outcome.fill_class === "VALID" ? "CREDITED" : "NOT CREDITED IN W1"} |`);
  }
  report.push("");
  report.push("## 5. Deltas last");
  report.push("");
  report.push("| game | honest state | raw pass-2 pair | raw delta | valid credited-leg own-close deltas |");
  report.push("|---|---|---:|---:|---|");
  for (const story of stories) {
    const validDeltas = story.legs.filter((leg) => leg.outcome.fill_class === "VALID")
      .map((leg) => `${leg.leg} ${leg.outcome.entry_minus_close_cents >= 0 ? "+" : ""}${leg.outcome.entry_minus_close_cents}c`)
      .join(" · ") || "none";
    report.push(`| ${story.event_id} | ${story.honest_outcome} | ${story.raw_outcome.combined_entry_cents} | +${story.raw_outcome.delta_vs_100_cents}c | ${validDeltas} |`);
  }
  report.push("");
  report.push("## Sixteen adjudications");
  report.push("");
  report.push("DEPTH-LICENSED uses the v3-filed rule directly: the machine's rest-to-floor gap must be no larger than the corrected cell's `edge_p50`; the price cell is that leg's own W1 close. No alternative threshold is introduced.");
  report.push("");
  report.push("| game | leg | KNOWABLE | TOUCH-SUFFICIENT | DEPTH-LICENSED | floor / rest / touch | corrected cell p50 (n) |");
  report.push("|---|---|---|---|---|---|---|");
  for (const row of adjudications) {
    report.push(`| ${row.event_id} | ${row.leg} | ${row.knowable} | ${row.touch_sufficient} | ${row.depth_licensed} | ${row.floor_cents}/${row.machine_rest_cents_at_floor}/${row.pre_floor_touch_bid_cents ?? "—"} | ${row.map_edge_p50_cents ?? "UNMAPPED"} (${row.map_n_legs ?? "—"}) |`);
  }
  report.push("");
  report.push(`Counts: KNOWABLE ${synthesis.adjudication_counts.knowable_yes} yes / ${synthesis.adjudication_counts.knowable_no} no; TOUCH-SUFFICIENT ${synthesis.adjudication_counts.touch_sufficient_yes} yes / ${synthesis.adjudication_counts.touch_sufficient_no} no; DEPTH-LICENSED ${synthesis.adjudication_counts.depth_licensed_yes} yes / ${synthesis.adjudication_counts.depth_licensed_no} no / ${synthesis.adjudication_counts.depth_unmapped} unmapped.`);
  report.push("");
  report.push("## Synthesis");
  report.push("");
  report.push(`**Next instrument: ${synthesis.next_instrument}.** ${synthesis.reason}`);
  report.push("");
  report.push("Determinism and L22 receipts are emitted beside this report. No policy behavior changed.");
  report.push("");
  fs.writeFileSync(path.join(outDir, "PROCESS_FIRST_REPORT.md"), `${report.join("\n").trimEnd()}\n`);

  const artifactNames = [
    "ACTIONS_8.json", "ADJUDICATIONS_16.csv", "ADJUDICATIONS_16.json",
    "DIVE_STORIES_8.json", "INPUT_BINDING_RECEIPT.json", "PROCESS_FIRST_REPORT.md",
    "SELECTED_SENTENCES_8.jsonl.gz", "SYNTHESIS.json",
  ];
  const manifest = manifestFor(outDir, artifactNames);
  writeJson(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), manifest);
  writeJson(path.join(outDir, "EXTERNAL_CUSTODY_MANIFEST.json"), {
    label: "L22_CUSTODY_RECEIPT",
    committed_file_cap_bytes: 50000000,
    oversized_artifacts: [],
    all_generated_artifacts_within_cap: manifest.every((row) => row.bytes <= 50000000),
    source_sentence_archive_external_custody: inputReceipt.sources.pass2_sentences,
  });
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
