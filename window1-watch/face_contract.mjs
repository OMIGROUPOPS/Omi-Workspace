// Display projection only. Never imports or executes the engine. See FIELDS.md.
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

export const GATES = [
  2880, 2160, 1440, 1080, 720, 480, 360, 240, 180, 120, 90, 60, 30, 15, 5,
];
export const SILENT = "STORE SILENT";
const finite = (x) => typeof x === "number" && Number.isFinite(x);
const num = (x) => (finite(x) ? x : null);
const text = (x) => (x == null ? SILENT : String(x));
const cents = (x) => (finite(x) ? `${x}¢` : SILENT);
const sha = (x) => crypto.createHash("sha256").update(x).digest("hex");
const pct = (x) => (finite(x) ? `${(100 * x).toFixed(2)}%` : SILENT);
const withoutSilent = (value) =>
  value?.stamp === SILENT ? null : (value ?? null);

export function inspectorSummary(row) {
  return {
    statuses: Object.fromEntries(
      ["macro", "micro", "micro_micro"].map((k) => [
        k,
        row.layers?.[k]?.context?.status ?? null,
      ]),
    ),
    coherence: row.coherence ?? null,
    seats_before: row.reads?.half_pair_state?.value ?? null,
    legs: (row.derivations ?? []).map((d) => ({
      leg_id: d.leg_id,
      action: d.action ?? null,
      placement: d.layered_dual_belief?.envelope_placement
        ? Object.fromEntries(
            [
              "mode",
              "writer_lane",
              "chosen_target_cents",
              "may_originate_rest",
            ].map((k) => [
              k,
              d.layered_dual_belief.envelope_placement[k] ?? null,
            ]),
          )
        : null,
      lanes_and_winner: d.layered_dual_belief?.decision_arbitration ?? null,
      seat: d.layered_dual_belief?.prediction_seat ?? null,
      authority_target: d.derivation?.pricing_authority?.target_cents ?? null,
      authority_source:
        d.derivation?.pricing_authority?.authority_source ?? null,
      // The unfiltered row below is the authority for every lane, ladder, clip and seat field.
      derivation_keys: Object.keys(d),
    })),
  };
}

export async function bindCustody(tracePath, traceSha, suppliedDir) {
  const dirs = [
    suppliedDir,
    tracePath && path.dirname(tracePath),
    tracePath && path.dirname(tracePath).replace(/_custody$/, ""),
    tracePath && path.dirname(path.dirname(tracePath)),
  ].filter(Boolean);
  for (const dir of [...new Set(dirs)]) {
    try {
      const manifestBytes = await fs.readFile(
        path.join(dir, "EXTERNAL_CUSTODY_MANIFEST.json"),
      );
      const manifest = JSON.parse(manifestBytes);
      const bound = (manifest.files ?? []).find(
        (f) =>
          f.logical_path === "REPAIR_FOUR_GAME_TRACE.jsonl.gz" ||
          /REPAIR_FOUR_GAME_TRACE/.test(
            f.logical_path ?? f.custody_location ?? "",
          ),
      );
      // Never stamp today's OS on a historical trace; require that run's trace binding.
      if (bound?.sha256?.toLowerCase() !== traceSha?.toLowerCase()) continue;
      const sourceBytes = await fs.readFile(
        path.join(dir, "PRINT_PRICED_RESIDUE_SWEEP.json"),
      );
      const source = JSON.parse(sourceBytes).source_files?.find(
        (f) => f.path === "arb-executor/analysis/window1_v54_dual_belief_os.js",
      );
      if (source?.sha256)
        return {
          os_sha256: source.sha256,
          os_hash_source: path.join(dir, "PRINT_PRICED_RESIDUE_SWEEP.json"),
          custody_manifest_sha256: sha(manifestBytes),
          os_receipt_sha256: sha(sourceBytes),
        };
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    // New rerun receipts bind the actual before/after OS bytes and this exact trace.
    try {
      const bytes = await fs.readFile(
        path.join(dir, "FACE_RUN_PROVENANCE.json"),
      );
      const run = JSON.parse(bytes);
      if (
        run.trace_sha256 === traceSha &&
        run.os_sha256 === run.os_sha256_after
      )
        return {
          os_sha256: run.os_sha256,
          os_hash_source: path.join(dir, "FACE_RUN_PROVENANCE.json"),
          custody_manifest_sha256: sha(bytes),
        };
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  return {
    os_sha256: null,
    os_hash_source: null,
    custody_manifest_sha256: null,
  };
}

function benchProjection(row, legMap) {
  if (!row) return null;
  const validity = row.validity ?? {};
  const valid = validity.status === "OK" && finite(validity.weighted_share);
  return {
    minutes_to_bell: row.minutes_to_bell,
    status: row.status ?? null,
    validity: {
      status: validity.status ?? null,
      share: num(validity.weighted_share),
      ess: num(validity.ess),
      label: valid
        ? `${pct(validity.weighted_share)}${validity.ess < 10 ? " · LOW ESS telemetry" : ""}`
        : SILENT,
      meter_percent:
        valid && validity.ess >= 10 ? 100 * validity.weighted_share : null,
    },
    roles: Object.fromEntries(
      Object.entries(legMap).map(([leg, side]) => [
        leg,
        row.recognition?.[side]?.current_role ?? null,
      ]),
    ),
    rules: Object.fromEntries(
      Object.entries(row.rules ?? {}).map(([rule, r]) => [
        rule,
        {
          ess: num(r.ess),
          label: finite(r.ess) ? r.ess.toFixed(2) : SILENT,
          status: r.status ?? null,
          sides: Object.fromEntries(
            Object.entries(legMap).map(([leg, side]) => [
              leg,
              {
                status: r.sides?.[side]?.status ?? null,
                ess: num(r.sides?.[side]?.ess),
                family:
                  r.sides?.[side]?.status === "OK"
                    ? (r.sides[side].family?.top ?? null)
                    : null,
              },
            ]),
          ),
        },
      ]),
    ),
  };
}

export async function extendFace(face, { here, eventId, benchPath }) {
  let named = null,
    benchSha = null,
    benchLabel = null;
  const input =
    benchPath === "none"
      ? null
      : (benchPath ??
        path.resolve(
          here,
          "../arb-executor/analysis/tune_bench_v2/TUNE_BENCH_NAMED_CHECKS.json",
        ));
  if (input) {
    try {
      const bytes = await fs.readFile(input),
        bench = JSON.parse(bytes);
      named =
        Object.values(bench.events ?? {}).find((e) => e.event_id === eventId) ??
        null;
      if (named) {
        benchSha = sha(bytes);
        benchLabel = bench.label ?? null;
      }
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  face.version = 2;
  face.provenance.bench_sha256 = benchSha;
  face.provenance.bench_label = benchLabel;
  const benchBell = named?.first_tick
    ? named.first_tick.epoch + named.first_tick.mtb_first * 60
    : null;
  const clockMatch =
    finite(benchBell) &&
    Math.round(benchBell) === Math.round(face.bell.timestamp_epoch);
  face.bench = {
    present: named !== null,
    label: benchLabel,
    source: named ? input : null,
    clock_status: named
      ? clockMatch
        ? "ALIGNED"
        : "CLOCK_MISMATCH_STORE_SILENT"
      : "STORE_SILENT",
    bell_epoch: benchBell,
    clock_delta_seconds: finite(benchBell)
      ? benchBell - face.bell.timestamp_epoch
      : null,
  };
  const firstEpoch = face.bell.timestamp_epoch - face.bell.t * 3600;
  const mtb = (t) => (face.bell.t - t) * 60;
  const ordered = face.os
    .filter((r) => finite(r.t))
    .sort(
      (a, b) =>
        a.t - b.t ||
        (finite(a.trace_row) && finite(b.trace_row)
          ? a.trace_row - b.trace_row
          : 0),
    );
  face.os = ordered;
  const firstStored = ordered.find((r) =>
    face.legs.every((l) => r.legs[l]?.true_trade_count > 0),
  );
  face.first_tick = firstStored
    ? {
        epoch: firstEpoch + firstStored.t * 3600,
        mtb_first: mtb(firstStored.t),
        source: "DECISION_STAGE: both true_trade_count > 0",
        receipt: firstStored.receipt,
      }
    : named?.first_tick
      ? {
          ...named.first_tick,
          mtb_first: (face.bell.timestamp_epoch - named.first_tick.epoch) / 60,
          source: "TUNE_BENCH first true tick epoch mapped to TRACE bell",
        }
      : null;
  if (!finite(face.first_tick?.mtb_first))
    throw new Error(
      "STORE SILENT: no stored first real pair tick; refusing a synthetic level clock",
    );
  face.first_tick.clock_label = `${face.first_tick.mtb_first.toFixed(2)}m to bell`;
  const start = face.first_tick.mtb_first;
  const legMap = named?.first_tick
    ? {
        [named.first_tick.favorite]: "favorite",
        [named.first_tick.underdog]: "underdog",
      }
    : {};
  const inspectionStart = mtb(ordered[0].t);
  const checkpoints = GATES.filter((g) => g <= inspectionStart).map((g) => ({
    minutesToBell: g,
    label: `${g}m`,
    playable: g <= start,
    position_percent: g <= start ? (100 * (start - g)) / start : null,
    bench: benchProjection(
      clockMatch ? named?.gates?.[String(g)] : null,
      legMap,
    ),
  }));
  let rest = Object.fromEntries(face.legs.map((l) => [l, null]));
  let filled = Object.fromEntries(face.legs.map((l) => [l, null]));
  let current = Object.fromEntries(face.legs.map((l) => [l, null]));
  let cumulativeFills = [];
  const memberMax = Object.fromEntries(
    face.legs.map((l) => [
      l,
      Math.max(...ordered.map((r) => num(r.legs[l]?.member_count) ?? 0)),
    ]),
  );
  for (const [index, row] of ordered.entries()) {
    row.index = index;
    row.minutesToBell = mtb(row.t);
    row.clock_label = `${row.minutesToBell.toFixed(2)}m to bell`;
    row.bench_checkpoint = checkpoints.findLastIndex(
      (c) => c.minutesToBell >= row.minutesToBell,
    );
    row.display = {
      legs: {},
      pair_sum: null,
      pair_label: SILENT,
      pair_percent: null,
      above_par: null,
      fills: null,
    };
    const titles = [];
    for (const leg of face.legs) {
      const l = row.legs[leg];
      if (row.kind === "DECISION_STAGE") current[leg] = l;
      const action = l?.action?.name ?? l?.rest?.action;
      // Explicit uncredited standing-state disappearance, not a synthetic bell cancel.
      if (row.standing?.[leg]?.credited === false && row.standing[leg].standing_target_cents === null)
        rest[leg] = null;
      if (["PLACE_REST", "REPRICE_REST"].includes(action)) rest[leg] = l.rest;
      if (action === "HOLD_REST" && finite(l.action?.target_cents) && l.action.target_cents !== rest[leg]?.cents)
        rest[leg] = { cents: l.action.target_cents, lane: l.action.lane ?? null, action };
      if (["PULL_REST", "CANCEL_REST", "STAND_DOWN"].includes(action)) rest[leg] = null;
      if (l?.fill) {
        filled[leg] = l.fill.cents;
        rest[leg] = null;
        cumulativeFills.push(
          `${leg} FILL ${cents(l.fill.cents)} · ${row.clock_label}`,
        );
      }
      const snapshot = current[leg] ?? {};
      const s = snapshot.sentence;
      const noDip = snapshot.member_remaining_dip_zero_weighted_share;
      const restKnown = row.standing?.[leg] != null || current[leg] != null;
      const lane = l?.action?.lane ?? l?.rest?.lane ?? rest[leg]?.lane ?? null;
      row.display.legs[leg] = {
        current_rest: rest[leg]?.cents ?? null,
        rest_known: restKnown,
        rest_label: rest[leg]
          ? cents(rest[leg].cents)
          : restKnown
            ? "none"
            : SILENT,
        last_fill: filled[leg],
        member_count: num(snapshot.member_count),
        member_label: text(snapshot.member_count),
        member_percent:
          finite(snapshot.member_count) && memberMax[leg] > 0
            ? (100 * snapshot.member_count) / memberMax[leg]
            : null,
        sentence: s?.plain_sentence ?? s?.status ?? SILENT,
        belief: `status ${text(s?.status)} · P ${cents(s?.P)} · Q ${cents(s?.Q)} · X ${cents(s?.X)}`,
        authors: `Q ${text(s?.q_author)} · X ${text(s?.x_author)} · source ${text(s?.authority_source)}`,
        family: s?.family ?? null,
        band_line: `no further dip ${pct(noDip)} · q25 level ${cents(snapshot.candidate_level_q25_cents)} · q10 level ${cents(snapshot.candidate_level_q10_cents)}`,
        band:
          finite(snapshot.candidate_level_q25_cents) &&
          finite(snapshot.candidate_level_q75_cents)
            ? [
                snapshot.candidate_level_q25_cents,
                snapshot.candidate_level_q75_cents,
              ]
            : null,
        q10: num(snapshot.candidate_level_q10_cents),
        action: action ?? null,
        lane,
        hand_line: `${text(action)} · ${cents(l?.action?.target_cents)} · lane ${text(lane)}`,
        saw: `bid ${cents(snapshot.bid)} · ask ${cents(snapshot.ask)} · last ${cents(snapshot.last)} · running low ${cents(snapshot.running_low)}`,
      };
      if (l?.fill) titles.push(`${leg} FILL ${cents(l.fill.cents)}`);
      else if (action && action !== "HOLD_REST")
        titles.push(`${leg} ${action} ${cents(l.action?.target_cents)}`);
    }
    // Pair exposure = credited entry, otherwise active rest; never replace absent side with zero.
    const exposure = face.legs.map((l) => filled[l] ?? rest[l]?.cents ?? null);
    if (exposure.every(finite)) {
      row.display.pair_sum = exposure.reduce((a, b) => a + b, 0);
      row.display.pair_label = `${row.display.pair_sum}¢ / 100¢`;
      row.display.pair_percent = Math.min(100, row.display.pair_sum);
      row.display.above_par = row.display.pair_sum > 100;
    }
    row.display.fills = cumulativeFills.join(" · ") || "No recorded fills yet";
    row.title = titles.join(" · ") || row.kind.replaceAll("_", " ");
  }
  const at = (rows, t, field = "t") =>
    rows.findLast((r) => r[field] <= t) ?? null;
  const timeline = new Set([
    face.bell.t,
    (face.first_tick.epoch - firstEpoch) / 3600,
  ]);
  for (const rows of Object.values(face.tape))
    for (const r of rows) timeline.add(r.t);
  for (const r of ordered) timeline.add(r.t);
  for (const c of checkpoints) timeline.add(face.bell.t - c.minutesToBell / 60);
  const columns = [
    "minutesToBell",
    "hours",
    "clock_label",
    "receipt_index",
    "checkpoint_index",
    "firstLast",
    "firstBid",
    "firstAsk",
    "firstRest",
    "secondLast",
    "secondBid",
    "secondAsk",
    "secondRest",
    "firstBand",
    "firstQ10",
    "secondBand",
    "secondQ10",
    "pre_first_tick",
    "plot_remaining",
    "plot_progress",
  ];
  const ticks = [];
  for (const t of [...timeline].sort((a, b) => a - b)) {
    const minutes = mtb(t);
    if (minutes > inspectionStart + 1e-7 || minutes < -1e-7) continue;
    const a = at(face.tape[face.legs[0]], t),
      b = at(face.tape[face.legs[1]], t);
    const exactRows = ordered.filter((r) => r.t === t);
    for (const row of exactRows.length ? exactRows : [at(ordered, t)]) {
      const d = row?.display.legs;
      const one = d?.[face.legs[0]],
        two = d?.[face.legs[1]];
      const preFirst = minutes > start + 1e-7;
      const plotRemaining = Math.max(
        0,
        Math.min(1, minutes / (preFirst ? inspectionStart : start)),
      );
      ticks.push([
        minutes,
        t,
        `${minutes.toFixed(2)}m to bell`,
        row?.index ?? null,
        checkpoints.findLastIndex((c) => c.minutesToBell >= minutes - 1e-7),
        a?.last ?? null,
        a?.bid ?? null,
        a?.ask ?? null,
        one?.current_rest ?? null,
        b?.last ?? null,
        b?.bid ?? null,
        b?.ask ?? null,
        two?.current_rest ?? null,
        one?.band ?? null,
        one?.q10 ?? null,
        two?.band ?? null,
        two?.q10 ?? null,
        preFirst,
        plotRemaining,
        1 - plotRemaining,
      ]);
    }
  }
  for (const c of checkpoints) {
    c.frame = ticks.findLastIndex(
      (t) => Math.abs(t[0] - c.minutesToBell) < 1e-7,
    );
    c.receipt_index = ticks[c.frame]?.[3] ?? null;
  }
  const values = ticks
    .flatMap((t) => [
      ...t.slice(5, 13),
      t[14],
      t[16],
      ...(t[13] ?? []),
      ...(t[15] ?? []),
    ])
    .filter(finite)
    .sort((a, b) => a - b);
  const unique = [...new Set(values)];
  const priceTicks = [
    ...new Set(
      [0, 0.25, 0.5, 0.75, 1].map(
        (q) => unique[Math.floor(q * (unique.length - 1))],
      ),
    ),
  ].filter(finite);
  const playValues = ticks
    .filter((t) => !t[17])
    .flatMap((t) => [
      ...t.slice(5, 13),
      t[14],
      t[16],
      ...(t[13] ?? []),
      ...(t[15] ?? []),
    ])
    .filter(finite)
    .sort((a, b) => a - b);
  const playUnique = [...new Set(playValues)];
  const playPriceTicks = [
    ...new Set(
      [0, 0.25, 0.5, 0.75, 1].map(
        (q) => playUnique[Math.floor(q * (playUnique.length - 1))],
      ),
    ),
  ].filter(finite);
  const pricePosition = (price, pool) =>
    pool.length && pool.at(-1) !== pool[0]
      ? (pool.at(-1) - price) / (pool.at(-1) - pool[0])
      : null;
  const fillEvents = ordered.flatMap((r) =>
    face.legs
      .filter((l) => r.legs[l]?.fill)
      .map((l) => ({
        leg: l,
        minutesToBell: r.minutesToBell,
        cents: r.legs[l].fill.cents,
        label: `${l} fill ${cents(r.legs[l].fill.cents)}`,
        receipt_index: r.index,
        plot_progress: 1 - r.minutesToBell / start,
        inspection_progress: 1 - r.minutesToBell / inspectionStart,
        plot_price: pricePosition(r.legs[l].fill.cents, playValues),
        inspection_price: pricePosition(r.legs[l].fill.cents, values),
      })),
  );
  const misses = face.legs
    .map((l) => {
      if (!rest[l]) return null;
      const placed = ordered.findLast((r) => r.legs[l]?.rest);
      const remaining = face.tape[l].filter(
        (r) => r.t > placed.t && r.t <= face.bell.t && finite(r.last),
      );
      const neverReturned = remaining.length
        ? remaining.every((r) => r.last > rest[l].cents)
        : null;
      return {
        leg: l,
        cents: rest[l].cents,
        never_returned: neverReturned,
        label: neverReturned
          ? `${l} rest ${cents(rest[l].cents)} · tape never returned before bell`
          : `${l} unfilled rest ${cents(rest[l].cents)} · ${neverReturned === null ? SILENT : "tape-return check false"}`,
      };
    })
    .filter(Boolean);
  face.render = {
    columns,
    ticks,
    checkpoints,
    fill_events: fillEvents,
    misses,
    play_start_frame: ticks.findIndex((t) => !t[17]),
    axis: {
      start_minutes_to_bell: start,
      end_minutes_to_bell: 0,
      ticks: [
        start,
        ...checkpoints.filter((c) => c.playable).map((c) => c.minutesToBell),
        0,
      ],
      price_domain: playValues.length
        ? [playValues[0], playValues.at(-1)]
        : null,
      price_ticks: playPriceTicks,
    },
    inspection_axis: {
      start_minutes_to_bell: inspectionStart,
      end_minutes_to_bell: 0,
      ticks: [inspectionStart, ...checkpoints.map((c) => c.minutesToBell), 0],
      price_domain: values.length ? [values[0], values.at(-1)] : null,
      price_ticks: priceTicks,
    },
    total_frames: ticks.length,
    receipt_count: ordered.length,
    verification: Object.fromEntries(
      face.legs
        .map((l) => [
          l,
          {
            first_rest: ordered.find((r) => r.legs[l]?.rest) ?? null,
            first_fill: ordered.find((r) => r.legs[l]?.fill) ?? null,
          },
        ])
        .map(([l, v]) => [
          l,
          Object.fromEntries(
            Object.entries(v).map(([k, r]) => [
              k,
              r
                ? {
                    receipt: r.receipt,
                    receipt_id: r.receipt_id,
                    detail_url: r.detail_url,
                    t: r.t,
                    minutes_to_bell: r.minutesToBell,
                    cents:
                      r.legs[l][k === "first_rest" ? "rest" : "fill"].cents,
                    lane: r.legs[l].rest?.lane ?? null,
                    authority_source:
                      r.legs[l].sentence?.authority_source ?? null,
                  }
                : null,
            ]),
          ),
        ]),
    ),
  };
}

export async function writeGameIndex(directory) {
  const games = new Map();
  for (const name of (await fs.readdir(directory))
    .filter((n) => n.endsWith(".face.json"))
    .sort()) {
    const f = JSON.parse(await fs.readFile(path.join(directory, name), "utf8"));
    if (!f.provenance?.event_id) continue;
    const item = {
      event: f.provenance.event_id,
      category: f.category ?? null,
      os_sha: f.provenance.os_sha256 ?? null,
      trace_sha: f.provenance.trace_sha256 ?? null,
      bench_sha: f.provenance.bench_sha256 ?? null,
      bell: f.bell ?? null,
      first_tick: f.first_tick ?? null,
      url: `/data/${name}`,
      version: f.version ?? 1,
    };
    if (!games.has(item.event) || item.version > games.get(item.event).version)
      games.set(item.event, item);
  }
  await fs.writeFile(
    path.join(directory, "index.json"),
    JSON.stringify({ games: [...games.values()] }),
  );
}
