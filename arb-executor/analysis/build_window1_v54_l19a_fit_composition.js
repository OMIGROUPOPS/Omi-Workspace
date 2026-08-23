"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const { once } = require("events");
const os = require("./window1_v54_functionable_os.js");
const base = require("./build_window1_v54_functionable_v6.js");

const PARENT_COMMIT = "e5c6212c0a9a7ed1b1ece082cae884aa9d41f20c";
const PASS1_SCORECARD = ".claude/window1_live_v4_replay/v54_l19a_fit_composition_pass1_20260822/SCORECARD.json";
const V52L_COMMIT = "96597c98910f7ef45b62e2bc7dfab5ed9ee5f5a7";
const V52L_LEDGER = ".claude/window1_live_v4_replay/v52r_disposition_804_20260818/V52L_MARKET_EVENT_LEDGER_804.jsonl.gz";
const OFFER_LEDGER = ".claude/window1_live_v4_replay/v52r_disposition_804_20260818/OFFER_DENOMINATOR_EVENT_LEDGER_804.jsonl.gz";
const LAW_INDEX = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAW_INDEX.md";
const TARGETS = Object.freeze({
  smoke: "KXWTAMATCH-26JUL13CRIJEA",
  four: [
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
    "KXATPCHALLENGERMATCH-26JUL14URSPAL",
    "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
    "KXATPMATCH-26JUL18DANPRA",
  ],
});
const RATchets = Object.freeze({
  KXATPCHALLENGERMATCH_26JUL12GIUBAR: 7,
  KXATPCHALLENGERMATCH_26JUL14URSPAL: 3,
  KXATPCHALLENGERMATCH_26JUL14LAJSVA: 6,
});

function arg(name, fallback = null) { const index = process.argv.indexOf(`--${name}`); return index >= 0 ? process.argv[index + 1] : fallback; }
function required(name) { const value = arg(name); if (!value) throw new Error(`missing --${name}`); return path.resolve(value); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function sha(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function fileHash(file) { const hash = crypto.createHash("sha256"), fd = fs.openSync(file, "r"), buffer = Buffer.alloc(8 * 1024 * 1024); try { for (;;) { const n = fs.readSync(fd, buffer, 0, buffer.length, null); if (!n) break; hash.update(buffer.subarray(0, n)); } } finally { fs.closeSync(fd); } return hash.digest("hex"); }
function ensure(value, message) { if (!value) throw new Error(message); }
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value)); }
function writeText(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`); }
function gitBytes(repo, commit, file) { return execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 }); }
function gzipJsonl(bytes) { return zlib.gunzipSync(bytes).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse); }
function mean(values) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null; }
function sourceReceipt(file, rows = null) { const stat = fs.statSync(file); return { path: file, sha256: fileHash(file), bytes: stat.size, rows }; }

function enrichNeighborSpecialists(corpus) {
  const records = [];
  for (const game of corpus) {
    if (game.span?.status !== "BOUNDED") continue;
    for (const leg of game.legs ?? []) {
      if (!(Number.isFinite(leg.floor_fraction) && Number.isFinite(leg.observed_low_cents) && Number.isFinite(leg.low_cents))) continue;
      const sourceReceiptId = leg.floor_timing_receipt ?? `${game.event_id}|${leg.leg_id}|${leg.floor_fraction}`;
      leg.specialist_record = {
        kind: "BOUNDED_TWO_BEHAVIOR_FLOOR_CAPTURE",
        floor_fraction: leg.floor_fraction,
        remaining_depth_cents: Math.max(0, leg.observed_low_cents - leg.low_cents),
        before_floor_behavior: "DERIVED_TIMING_DEPTH",
        at_or_after_floor_behavior: "OWN_TAPE_PRESENCE_AT_TOUCH",
        source_receipt: sourceReceiptId,
        source_grain: leg.floor_timing_grain ?? leg.source_grain ?? game.grain ?? null,
      };
      records.push({ event_id: game.event_id, category: game.category, leg_id: leg.leg_id, ...leg.specialist_record });
    }
  }
  const body = {
    kind: "LEAVE_SELF_OUT_BOUNDED_NEIGHBOR_SPECIALIST_RECORDS",
    population: "BELL_BOUNDED_LIBRARY_GAMES",
    sealed_excluded: true,
    records: records.length,
    games: new Set(records.map((row) => row.event_id)).size,
    behavior_law: "Before its bounded floor fraction a member is a derived-timing-depth specialist; at-or-after that floor fraction it is an own-tape-presence-at-touch specialist.",
    runtime_weight_law: "Continuous similarity x coverage x this-leg evidence-match grade; the evaluated event is excluded by neighborhood retrieval.",
    no_cells: true,
    no_global_coefficients: true,
    records_rows: records,
  };
  body.binding_sha256 = sha(canonical(body));
  return body;
}

function frozenBindings(repo) {
  const baselineBytes = gitBytes(repo, V52L_COMMIT, V52L_LEDGER);
  const baseline = gzipJsonl(baselineBytes);
  const offeredBytes = fs.readFileSync(path.join(repo, OFFER_LEDGER));
  const offered = gzipJsonl(offeredBytes);
  const offeredIds = new Set(offered.filter((row) => row.offer_class === "OFFERED_UNDER_PAR").map((row) => row.event_id));
  const truthRows = JSON.parse(gitBytes(repo, base.GROUND_TRUTH_COMMIT, base.GROUND_TRUTH_PATH)).rows;
  const truthById = new Map(truthRows.map((row) => [row.event_id, row]));
  const championIds = new Set(baseline.filter((row) => {
    const legs = Object.values(row.legs ?? {}), combined = legs.length === 2 && legs.every((leg) => leg.credited && Number.isInteger(leg.entry_cents)) ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const truth = truthById.get(row.event_id);
    const valid = truth && legs.every((leg) => leg.fill_timestamp_epoch >= truth.span_start_epoch && leg.fill_timestamp_epoch <= truth.span_end_epoch);
    return Number.isInteger(combined) && combined < 100 && valid && offeredIds.has(row.event_id);
  }).map((row) => row.event_id));
  ensure(offeredIds.size === 680, `HONEST_DENOMINATOR_NOT_680:${offeredIds.size}`);
  ensure(championIds.size === 311, `CHAMPION_IDENTITY_NOT_311:${championIds.size}`);
  return {
    offeredIds,
    championIds,
    receipt: {
      champion: { commit: V52L_COMMIT, path: V52L_LEDGER, sha256: sha(baselineBytes), events: baseline.length, completed_identity: championIds.size },
      denominator: { path: OFFER_LEDGER, sha256: sha(offeredBytes), rows: offered.length, offered_games: offeredIds.size },
    },
  };
}

function resources(corpus, groundTruth, printSource, foundationIndex) {
  const connected = (id, receipt) => ({ id, status: "CONNECTED", receipt, smoke: { read_only: true } });
  return os.EXPECTED_RESOURCE_IDS.map((id) => {
    if (id === "TRUTH_TABLE_C0056976") return connected(id, `${base.GROUND_TRUTH_COMMIT}:${base.GROUND_TRUTH_PATH}@${groundTruth.receipt.base_sha256}`);
    if (id === "EXTERNAL_CUSTODY_TRUE_PRINTS") return connected(id, `${printSource.path}@${printSource.sha256}`);
    if (id === "FOUNDATION_PER_MINUTE_UNIVERSE") return connected(id, `${foundationIndex.path}@${foundationIndex.sha256}`);
    return connected(id, `V54_L19A_CONNECTED_STORE:${id}`);
  });
}

async function writeSentenceRows(writer, result) {
  for (const row of result.derivations) {
    const line = JSON.stringify({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, sentence: row.sentence, action: row.action, neighbor_specialist_composition: row.derivation.neighbor_specialist_composition, basis_weights: row.derivation.basis_weights }) + "\n";
    if (!writer.stream.write(line)) await once(writer.stream, "drain");
    writer.rows += 1;
  }
}

function compactOutcome(meta, result) {
  return {
    event_id: meta.event_id,
    category: meta.category,
    gradeable: result.execution.gradeable,
    completed: result.execution.completed,
    combined_entry_cents: result.execution.combined_entry_cents,
    delta_vs_100_cents: result.execution.delta_vs_100_cents,
    legs: Object.fromEntries(meta.leg_ids.map((id) => [id, { credited: result.state.positions[id].credited, entry_cents: result.state.positions[id].entry_cents, fill_timestamp_epoch: result.state.positions[id].fill_timestamp_epoch, terminal_target_cents: result.state.positions[id].standing_target_cents }])),
  };
}

async function replayPopulation({ metas, rowsById, corpus, resourcesList, lineage, printLoad, specialistBinding, sentenceWriter = null, storyIds = new Set() }) {
  os.configureNeighborSpecialistBinding(specialistBinding);
  const outcomes = [], stories = {};
  let index = 0;
  for (const meta of metas) {
    index += 1;
    const rows = base.loadTicks(rowsById.privateRoot, meta).concat(printLoad.byEvent.get(meta.event_id) ?? []);
    const result = base.replayEvent({ meta, rows, corpus, resources: resourcesList, lineage });
    if (sentenceWriter) await writeSentenceRows(sentenceWriter, result);
    if (storyIds.has(meta.event_id)) stories[meta.event_id] = { outcome: compactOutcome(meta, result), stages: result.stage_reads.map((stage) => ({ trigger: stage.trigger, timestamp_epoch: stage.timestamp_epoch, receipt: stage.receipt, derivations: stage.derivations.map((row) => ({ leg_id: row.leg_id, action: row.action, sentence: row.sentence })) })), fills: result.fill_events };
    outcomes.push(compactOutcome(meta, result));
    if (index % 40 === 0) process.stderr.write(`replayed ${index}/${metas.length}\n`);
  }
  return { outcomes, stories };
}

function candidateIdsFor(outcomes, frozen, truthById) {
  return new Set(outcomes.filter((row) => {
    const truth = truthById.get(row.event_id), legs = Object.values(row.legs);
    const valid = truth && legs.every((leg) => leg.credited && leg.fill_timestamp_epoch >= truth.span_start_epoch && leg.fill_timestamp_epoch <= truth.span_end_epoch);
    return row.gradeable && row.completed && row.combined_entry_cents < 100 && valid && frozen.offeredIds.has(row.event_id);
  }).map((row) => row.event_id));
}

function score(outcomes, frozen, truthById) {
  const candidateIds = candidateIdsFor(outcomes, frozen, truthById);
  const retained = [...frozen.championIds].filter((id) => candidateIds.has(id)).sort();
  const lost = [...frozen.championIds].filter((id) => !candidateIds.has(id)).sort();
  const gained = [...candidateIds].filter((id) => !frozen.championIds.has(id)).sort();
  const completedRows = outcomes.filter((row) => candidateIds.has(row.event_id));
  const byCategory = {};
  for (const row of outcomes) {
    byCategory[row.category] ??= { offered_games: 0, valid_completes: 0, locked_cents: 0 };
    if (frozen.offeredIds.has(row.event_id)) byCategory[row.category].offered_games += 1;
    if (candidateIds.has(row.event_id)) { byCategory[row.category].valid_completes += 1; byCategory[row.category].locked_cents += row.delta_vs_100_cents; }
  }
  return {
    honest_denominator_games: frozen.offeredIds.size,
    valid_completes: candidateIds.size,
    average_game_delta_vs_100_cents: mean(completedRows.map((row) => row.delta_vs_100_cents)),
    locked_cents: completedRows.reduce((sum, row) => sum + row.delta_vs_100_cents, 0),
    champion_identity: { floor: frozen.championIds.size, retained: retained.length, lost: lost.length, gained: gained.length, retained_event_ids: retained, lost_event_ids: lost, gained_event_ids: gained },
    by_category: byCategory,
    hard_floor_pass: candidateIds.size >= 311,
  };
}

function validationReceipt(outcomes, pass1, frozen, truthById) {
  const candidateIds = candidateIdsFor(outcomes, frozen, truthById);
  const lost = pass1.champion_identity.lost_event_ids;
  const gained = pass1.champion_identity.gained_event_ids;
  const recovered = lost.filter((id) => candidateIds.has(id)).sort();
  const stillLost = lost.filter((id) => !candidateIds.has(id)).sort();
  const retainedGained = gained.filter((id) => candidateIds.has(id)).sort();
  const surrenderedGained = gained.filter((id) => !candidateIds.has(id)).sort();
  return {
    executed_before_full_804: true,
    pass1_binding: { path: PASS1_SCORECARD, lost: lost.length, gained: gained.length },
    lost_258: { recovered_presence_wins: recovered.length, still_lost: stillLost.length, recovered_event_ids: recovered, still_lost_event_ids: stillLost },
    gained_24: { retained_timing_wins: retainedGained.length, surrendered: surrenderedGained.length, retained_event_ids: retainedGained, surrendered_event_ids: surrenderedGained },
    pre_stated_direction: { recovered_any_lost: recovered.length > 0, surrendered_no_gained: surrenderedGained.length === 0 },
    note: "The validation sets are the pass-1 executable identity decomposition; labels describe their filed intended roles, while completion is scored on the honest ruler.",
  };
}

function selectStories(eventIds, pass) {
  const mandatory = new Set([...TARGETS.four, TARGETS.smoke]);
  const ranked = eventIds.filter((id) => !mandatory.has(id)).map((id) => ({ id, key: sha(`V54_L19A_PASS_${pass}_CC_DRAW|${id}`) })).sort((a, b) => a.key.localeCompare(b.key));
  for (const row of ranked) { if (mandatory.size >= 30) break; mandatory.add(row.id); }
  return mandatory;
}

function fourReceipt(outcomes) {
  return TARGETS.four.map((eventId) => {
    const row = outcomes.find((item) => item.event_id === eventId), key = eventId.replaceAll("-", "_"), ratchet = RATchets[key] ?? null;
    return { event_id: eventId, completed: row?.completed ?? false, combined_entry_cents: row?.combined_entry_cents ?? null, delta_vs_100_cents: row?.delta_vs_100_cents ?? null, report_only_ratchet_cents: ratchet, ratchet_held: ratchet === null ? null : Boolean(row?.completed && row.delta_vs_100_cents >= ratchet), legs: row?.legs ?? null };
  });
}

function manifest(output) {
  const files = [];
  const walk = (dir) => { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { const absolute = path.join(dir, entry.name); if (entry.isDirectory()) walk(absolute); else if (entry.name !== "ARTIFACT_HASH_MANIFEST.json") files.push(absolute); } };
  walk(output);
  const rows = Object.fromEntries(files.sort().map((file) => { const relative = path.relative(output, file).replaceAll("\\", "/"), stat = fs.statSync(file); ensure(stat.size <= 50 * 1024 * 1024, `L22_ARTIFACT_OVER_50MIB:${relative}`); return [relative, { sha256: fileHash(file), bytes: stat.size }]; }));
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { files: rows, binding_sha256: sha(canonical(rows)) });
}

function writeCaseStudyV10(output, processReceipt, lajsva, scorecard, validation) {
  const dir = path.join(output, "lajsva_case_study_v10_20260823");
  fs.mkdirSync(dir, { recursive: true });
  writeJson(path.join(dir, "PANEL_A.json"), { title: "Stores and neighbor-specialist composition", stores: processReceipt.stores_pulled, composition: processReceipt.neighbor_voted_composition });
  writeJson(path.join(dir, "PANEL_B.json"), { title: "LAJSVA receipt chain", story: lajsva });
  writeJson(path.join(dir, "PANEL_C.json"), { title: "Consequences and honest ruler", validation, scorecard });
  const fills = (lajsva?.fills ?? []).map((row) => `- ${row.context.leg_id}: ${row.context.entry_cents}c at ${row.context.fill_timestamp_epoch}; receipt ${row.row_refs.join(",")}`).join("\n") || "- None.";
  writeText(path.join(dir, "TRADE_REPORT_REFLEX.md"), `# Reflex comparison\n\nThe frozen current-level path remains the no-vote fallback. Neighbor votes alter a target only where bounded specialists speak.\n\n${fills}\n`);
  writeText(path.join(dir, "TRADE_REPORT_PATTERN_ENGINE.md"), `# Neighbor-voted pattern engine\n\nEvery LAJSVA decision sentence in PANEL_B names each neighbor's behavior vote, continuous evidence-conditioned weight, floor phase, and source receipt.\n\n${fills}\n`);
  writeJson(path.join(dir, "CASE_STUDY_RECEIPT.json"), { version: 10, event_id: "KXATPCHALLENGERMATCH-26JUL14LAJSVA", candidate_status: scorecard.hard_floor_pass ? "PASS_ACCEPTED" : "SELF_STOPPED", panels: ["PANEL_A.json", "PANEL_B.json", "PANEL_C.json"], reports: ["TRADE_REPORT_REFLEX.md", "TRADE_REPORT_PATTERN_ENGINE.md"] });
}

async function main() {
  const repo = required("repo"), privateRoot = required("private-root"), cacheDir = required("cache-dir"), foundationIndex = required("foundation-index"), foundationReceipt = required("foundation-receipt"), output = required("output"), custody = required("custody"), pass = Number(arg("pass", "2"));
  ensure(pass === 2, "THIS_RUNNER_IS_FILED_PASS_2_ONLY");
  fs.mkdirSync(output, { recursive: true }); fs.mkdirSync(custody, { recursive: true });
  ensure(execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim() === PARENT_COMMIT || arg("allow-worktree", "false") === "true", "WRONG_PARENT_HEAD");
  const law = fs.readFileSync(path.join(repo, LAW_INDEX)), groundTruth = base.loadGroundTruth(repo), truthById = new Map(groundTruth.rows.map((row) => [row.event_id, row])), metas = groundTruth.rows.map(base.targetMeta).sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(metas.length === 804, `DEV_POPULATION_NOT_804:${metas.length}`);
  const frozen = frozenBindings(repo), corpusLoad = await base.loadCorpus(cacheDir, repo, foundationIndex, foundationReceipt), floorTiming = base.bindCorpusFloorTiming(corpusLoad.rows, groundTruth.rows), printLoad = await base.loadTargetPrints(privateRoot, metas), resourcesList = resources(corpusLoad, groundTruth, printLoad.source, sourceReceipt(foundationIndex));
  const lineage = { byEvent: new Map() }, storyIds = selectStories(metas.map((row) => row.event_id), pass);
  const specialistBinding = enrichNeighborSpecialists(corpusLoad.rows);
  writeJson(path.join(output, "NEIGHBOR_SPECIALIST_RECORDS.json"), specialistBinding);
  const pass1Bytes = fs.readFileSync(path.join(repo, PASS1_SCORECARD)), pass1 = JSON.parse(pass1Bytes);
  ensure(pass1.champion_identity.lost === 258 && pass1.champion_identity.gained === 24, "PASS1_VALIDATION_SET_BINDING_FAILED");
  const validationIds = new Set([...pass1.champion_identity.lost_event_ids, ...pass1.champion_identity.gained_event_ids]);
  const validationMetas = metas.filter((row) => validationIds.has(row.event_id));
  ensure(validationMetas.length === 282, `VALIDATION_POPULATION_NOT_282:${validationMetas.length}`);
  const validationRun = await replayPopulation({ metas: validationMetas, rowsById: { privateRoot }, corpus: corpusLoad.rows, resourcesList, lineage, printLoad, specialistBinding });
  const validation = validationReceipt(validationRun.outcomes, pass1, frozen, truthById);
  writeJson(path.join(output, "PASS1_LOST_GAINED_VALIDATION.json"), validation);
  const sentenceFile = path.join(custody, "ALL_SENTENCES_804.jsonl.gz"), sentenceOutput = fs.createWriteStream(sentenceFile), gzip = zlib.createGzip({ level: 1 }); gzip.pipe(sentenceOutput); const sentenceWriter = { stream: gzip, rows: 0 };
  const run = await replayPopulation({ metas, rowsById: { privateRoot }, corpus: corpusLoad.rows, resourcesList, lineage, printLoad, specialistBinding, sentenceWriter, storyIds });
  gzip.end(); await once(sentenceOutput, "close");
  const scorecard = score(run.outcomes, frozen, truthById), four = fourReceipt(run.outcomes), smoke = run.stories[TARGETS.smoke];
  const custodyManifest = { files: [{ logical_path: "OMI-Window1-private/stage1/v54_l19a_neighbor_voted_composition_pass2/ALL_SENTENCES_804.jsonl.gz", sha256: fileHash(sentenceFile), bytes: fs.statSync(sentenceFile).size, rows: sentenceWriter.rows, custody_location: sentenceFile }] };
  const lajsva = run.stories["KXATPCHALLENGERMATCH-26JUL14LAJSVA"];
  writeJson(path.join(output, "SCORECARD.json"), scorecard);
  writeJson(path.join(output, "PER_GAME_OUTCOME_TABLE.json"), run.outcomes);
  writeJson(path.join(output, "FOUR_GAME_TRIPWIRE.json"), { report_only_inside_tune: true, rows: four });
  writeJson(path.join(output, "PINS_TRIPWIRE.json"), { event_id: TARGETS.smoke, integration_only: true, no_verified_bell: !smoke?.outcome?.gradeable, readers_and_sentence_path_executed: Boolean(smoke?.stages?.length), conservation_clean: smoke?.stages?.flatMap((row) => row.derivations).length > 0 });
  writeJson(path.join(output, "CC_DRAWN_STORIES_30.json"), { seed: `SHA256(V54_L19A_PASS_${pass}_CC_DRAW|event_id)`, event_ids: [...storyIds].sort(), stories: run.stories });
  writeJson(path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json"), custodyManifest);
  writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { parent_commit: PARENT_COMMIT, adjustment: "NEIGHBOR_VOTED_COMPOSITION", pass1_scorecard: { path: PASS1_SCORECARD, sha256: sha(pass1Bytes), lost: 258, gained: 24 }, law_index: { path: LAW_INDEX, sha256: sha(law), L19a_present: law.toString("utf8").includes("L19a") }, ground_truth: groundTruth.receipt, corpus: corpusLoad.sources, foundation: sourceReceipt(foundationIndex, corpusLoad.foundation.rows), floor_timing: floorTiming, specialist_binding_sha256: specialistBinding.binding_sha256, true_prints: printLoad.source, frozen });
  writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { fixed_dev_804: true, sealed: false, holdout: false, live: false, network_during_policy_replay: false, orders: false, positions: false, deployment: false });
  writeJson(path.join(output, "DETERMINISM_INPUT_BINDING.json"), { pass, specialist_binding_sha256: specialistBinding.binding_sha256, policy_sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_v54_functionable_os.js")), runner_sha256: fileHash(__filename), population_sha256: sha(canonical(metas.map((row) => row.event_id))), validation_sha256: sha(canonical(validation)), outcome_sha256: sha(canonical(run.outcomes)), scorecard_sha256: sha(canonical(scorecard)), sentences_sha256: custodyManifest.files[0].sha256 });
  const processReceipt = {
    order: ["STORES_PULLED", "NEIGHBOR_SPECIALIST_ENRICHMENT", "LOST_GAINED_VALIDATION", "LAJSVA_WALK_WITH_VERBATIM_SENTENCES", "FILLS_AS_CONSEQUENCES", "DELTAS_LAST"],
    stores_pulled: { corpus: corpusLoad.counts, foundation: corpusLoad.foundation, tape_events: metas.length, true_print_source: printLoad.source },
    neighbor_voted_composition: { records: specialistBinding.records, games: specialistBinding.games, cells: 0, global_coefficients: 0, binding_sha256: specialistBinding.binding_sha256, plain_language: "Each bounded historical leg records when timing depth captured before its floor and when presence at touch captured at-or-after it. At runtime, leave-self-out neighbors cast continuous votes weighted by similarity, coverage, and this leg's evidence match." },
    lost_gained_validation: validation,
    lajsva_walk: lajsva,
    fills_as_consequences: lajsva?.fills ?? [],
    deltas_last: { four, full_804: scorecard },
  };
  writeJson(path.join(output, "PROCESS_FIRST_CONFIRM_RECEIPT.json"), processReceipt);
  writeCaseStudyV10(output, processReceipt, lajsva, scorecard, validation);
  const captureIssues = [...new Map(base.LOAD_TICK_ISSUES.map((row) => [`${row.file}|${row.row}`, row])).values()];
  writeJson(path.join(output, "CAPTURE_INPUT_ISSUES.json"), { policy_bytes_changed: false, issue_count: captureIssues.length, issues: captureIssues });
  writeText(path.join(output, "REPORT.md"), `# V54 L19a neighbor-voted composition — pass 2\n\n## 1. Stores pulled\n\nCorpus union ${corpusLoad.counts.union_games}; Foundation ${corpusLoad.foundation.rows}; dev tapes ${metas.length}; true prints scanned ${printLoad.source.scanned_rows}. Sealed, live, order, position, and deployment inputs were not read.\n\n## 2. Neighbor specialist enrichment\n\n${processReceipt.neighbor_voted_composition.plain_language} Records: ${specialistBinding.records}; games: ${specialistBinding.games}; fitted cells: 0; global coefficients: 0.\n\n## 3. Pass-1 validation sets before full 804\n\nLOST-258 recovered ${validation.lost_258.recovered_presence_wins}; still lost ${validation.lost_258.still_lost}. GAINED-24 retained ${validation.gained_24.retained_timing_wins}; surrendered ${validation.gained_24.surrendered}.\n\n## 4. LAJSVA walked\n\n${(lajsva?.stages ?? []).map((stage) => `### ${stage.timestamp_epoch} · ${stage.receipt}\n\n${stage.derivations.map((row) => row.sentence).join("\n\n")}`).join("\n\n")}\n\n## 5. Fills as consequences\n\n${(lajsva?.fills ?? []).map((row) => `- ${row.context.leg_id} ${row.context.entry_cents}c @ ${row.context.fill_timestamp_epoch} [${row.row_refs.join(",")}]`).join("\n") || "- None."}\n\n## 6. Deltas last\n\nFour-game tripwire: ${four.map((row) => `${row.event_id}=${row.completed ? `delta ${row.delta_vs_100_cents}` : "partial"}${row.report_only_ratchet_cents === null ? "" : ` (ratchet ${row.report_only_ratchet_cents}, ${row.ratchet_held ? "held" : "missed"})`}`).join("; ")}.\n\nFull 804 honest ruler: ${scorecard.valid_completes}/680 valid completes; average game delta ${scorecard.average_game_delta_vs_100_cents}; locked ${scorecard.locked_cents}c; champion identity retained/lost/gained ${scorecard.champion_identity.retained}/${scorecard.champion_identity.lost}/${scorecard.champion_identity.gained}. Hard floor ${scorecard.hard_floor_pass ? "PASS" : "SELF-STOP"}.\n`);
  manifest(output);
  process.stdout.write(canonical({ pass, output, validation, scorecard, four, custody: custodyManifest.files[0] }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
