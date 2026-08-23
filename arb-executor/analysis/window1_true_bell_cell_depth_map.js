#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith("--") || i + 1 >= argv.length) {
      throw new Error(`expected --key value, got ${key}`);
    }
    out[key.slice(2)] = argv[++i];
  }
  for (const required of ["source", "out-dir", "source-commit"]) {
    if (!out[required]) throw new Error(`missing --${required}`);
  }
  return out;
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function quantile(sorted, p) {
  if (sorted.length === 0) return null;
  if (sorted.length === 1) return sorted[0];
  const h = (sorted.length - 1) * p;
  const lo = Math.floor(h);
  const hi = Math.ceil(h);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (h - lo);
}

function roundHalfUp(value) {
  return Math.floor(value + 0.5);
}

function inc(object, key, amount = 1) {
  object[key] = (object[key] || 0) + amount;
}

function csvCell(value) {
  const text = value === null || value === undefined ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function main() {
  const args = parseArgs(process.argv);
  const sourcePath = path.resolve(args.source);
  const outDir = path.resolve(args["out-dir"]);
  const sourceBytes = fs.readFileSync(sourcePath);
  const lines = zlib.gunzipSync(sourceBytes).toString("utf8").split(/\r?\n/).filter(Boolean);

  const cells = new Map();
  const counts = {
    source_games: lines.length,
    bounded_games: 0,
    unbounded_games_excluded: 0,
    bounded_legs_seen: 0,
    mapped_legs: 0,
    out_of_grid_legs: 0,
    missing_price_legs: 0,
    negative_edge_legs: 0,
  };
  const byCategory = {};
  const byQuality = {};
  const byBellMethod = {};
  const exclusions = [];

  for (let index = 0; index < lines.length; index += 1) {
    const game = JSON.parse(lines[index]);
    const category = game.category || "UNKNOWN";
    const categoryCounts = byCategory[category] ||= {
      source_games: 0,
      bounded_games: 0,
      mapped_legs: 0,
      out_of_grid_legs: 0,
      missing_price_legs: 0,
      negative_edge_legs: 0,
    };
    categoryCounts.source_games += 1;
    inc(byQuality, game.quality || "UNKNOWN");

    const rightEdge = Number(game.span?.end_epoch ?? game.span?.right_edge_epoch);
    if (!game.span || game.span.status !== "BOUNDED" || !Number.isFinite(rightEdge)) {
      counts.unbounded_games_excluded += 1;
      exclusions.push({
        event_id: game.event_id,
        category,
        reason: "UNBOUNDED_OR_NO_LAWFUL_RIGHT_EDGE",
        status: game.span?.status ?? null,
        method: game.span?.method ?? null,
        end_epoch: game.span?.end_epoch ?? null,
        right_edge_epoch: game.span?.right_edge_epoch ?? null,
      });
      continue;
    }

    counts.bounded_games += 1;
    categoryCounts.bounded_games += 1;
    const methods = Array.isArray(game.span.method) ? game.span.method : [game.span.method || "UNKNOWN"];
    for (const method of methods) inc(byBellMethod, method);

    for (const leg of game.legs || []) {
      counts.bounded_legs_seen += 1;
      const close = Number(leg.close_cents);
      const low = Number(leg.low_cents);
      if (!Number.isFinite(close) || !Number.isFinite(low)) {
        counts.missing_price_legs += 1;
        categoryCounts.missing_price_legs += 1;
        exclusions.push({
          event_id: game.event_id,
          leg_id: leg.leg_id,
          category,
          reason: "MISSING_CLOSE_OR_LOW",
          close_cents: leg.close_cents ?? null,
          low_cents: leg.low_cents ?? null,
        });
        continue;
      }
      const cell = Math.trunc(close);
      if (cell < 5 || cell >= 95) {
        counts.out_of_grid_legs += 1;
        categoryCounts.out_of_grid_legs += 1;
        exclusions.push({
          event_id: game.event_id,
          leg_id: leg.leg_id,
          category,
          reason: "OUTSIDE_RATIFIED_5_TO_94_CELL_GRID",
          close_cents: close,
          low_cents: low,
        });
        continue;
      }
      const edge = close - low;
      if (edge < 0) {
        counts.negative_edge_legs += 1;
        categoryCounts.negative_edge_legs += 1;
        exclusions.push({
          event_id: game.event_id,
          leg_id: leg.leg_id,
          category,
          reason: "NEGATIVE_EDGE_DATA_DEFECT",
          close_cents: close,
          low_cents: low,
          edge_cents: edge,
        });
        continue;
      }
      const key = `${category}|${cell}`;
      const bucket = cells.get(key) || {
        category,
        price_cell: cell,
        edges: [],
        event_ids: new Set(),
        grains: {},
        bell_methods: {},
      };
      bucket.edges.push(edge);
      bucket.event_ids.add(game.event_id);
      inc(bucket.grains, game.grain || "UNKNOWN");
      for (const method of methods) inc(bucket.bell_methods, method);
      cells.set(key, bucket);
      counts.mapped_legs += 1;
      categoryCounts.mapped_legs += 1;
    }
  }

  const rows = [...cells.values()]
    .map((bucket) => {
      const sorted = [...bucket.edges].sort((a, b) => a - b);
      const p25 = quantile(sorted, 0.25);
      const p50 = quantile(sorted, 0.50);
      const p75 = quantile(sorted, 0.75);
      return {
        category: bucket.category,
        price_cell: bucket.price_cell,
        n_legs: sorted.length,
        n_games: bucket.event_ids.size,
        edge_p25_raw_cents: p25,
        edge_p50_raw_cents: p50,
        edge_p75_raw_cents: p75,
        edge_p25_cents: roundHalfUp(p25),
        edge_p50_cents: roundHalfUp(p50),
        edge_p75_cents: roundHalfUp(p75),
        edge_min_cents: sorted[0],
        edge_max_cents: sorted.at(-1),
        edge_ge_5_share: sorted.filter((value) => value >= 5).length / sorted.length,
        grains: bucket.grains,
        bell_methods: bucket.bell_methods,
      };
    })
    .sort((a, b) => a.category.localeCompare(b.category) || a.price_cell - b.price_cell);

  const mappedCellsByCategory = {};
  for (const row of rows) inc(mappedCellsByCategory, row.category);
  const table = {
    label: "TRUE_BELL_CELL_CONDITIONAL_DEPTH_MAP_V3",
    status: "RE_DERIVED_UNDER_LAWFUL_BOUNDED_RIGHT_EDGES",
    purpose: "companion measurement for DIVES T1 v3; descriptive adjudication input only",
    law: {
      grid: "ratified 90 one-cent cells per category, close cells [5,95)",
      edge: "bounded-library close_cents minus bounded-library low_cents",
      right_edge: "only CORPUS_INDEX rows with span.status=BOUNDED and finite span.end_epoch",
      unbounded: "excluded, never silently pooled",
      quantile: "type-7 linear interpolation on sorted integer-cent edges; published cent fields round half up and raw values are retained",
    },
    source: {
      path: (args["source-logical-path"] || args.source).replaceAll("\\", "/"),
      commit: args["source-commit"],
      sha256: sha256(sourceBytes),
      bytes: sourceBytes.length,
      rows: lines.length,
    },
    census: {
      ...counts,
      mapped_cells: rows.length,
      mapped_cells_by_category: mappedCellsByCategory,
      by_category: byCategory,
      by_quality: byQuality,
      by_bell_method: byBellMethod,
    },
    cells: rows,
  };

  fs.mkdirSync(outDir, { recursive: true });
  const jsonPath = path.join(outDir, "TRUE_BELL_CELL_DEPTH_MAP.json");
  const csvPath = path.join(outDir, "TRUE_BELL_CELL_DEPTH_MAP.csv");
  const exclusionsPath = path.join(outDir, "TRUE_BELL_CELL_DEPTH_MAP_EXCLUSIONS.json");
  fs.writeFileSync(jsonPath, `${JSON.stringify(table, null, 2)}\n`);

  const headers = [
    "category", "price_cell", "n_legs", "n_games", "edge_p25_raw_cents",
    "edge_p50_raw_cents", "edge_p75_raw_cents", "edge_p25_cents", "edge_p50_cents",
    "edge_p75_cents", "edge_min_cents", "edge_max_cents", "edge_ge_5_share",
    "grains_json", "bell_methods_json",
  ];
  const csvRows = [headers.join(",")];
  for (const row of rows) {
    csvRows.push([
      row.category, row.price_cell, row.n_legs, row.n_games, row.edge_p25_raw_cents,
      row.edge_p50_raw_cents, row.edge_p75_raw_cents, row.edge_p25_cents,
      row.edge_p50_cents, row.edge_p75_cents, row.edge_min_cents, row.edge_max_cents,
      row.edge_ge_5_share, JSON.stringify(row.grains), JSON.stringify(row.bell_methods),
    ].map(csvCell).join(","));
  }
  fs.writeFileSync(csvPath, `${csvRows.join("\n")}\n`);
  fs.writeFileSync(exclusionsPath, `${JSON.stringify({ label: "TRUE_BELL_CELL_DEPTH_MAP_EXCLUSIONS", exclusions }, null, 2)}\n`);

  const artifacts = [jsonPath, csvPath, exclusionsPath].map((artifactPath) => {
    const bytes = fs.readFileSync(artifactPath);
    return {
      path: path.relative(process.cwd(), artifactPath).replaceAll("\\", "/"),
      bytes: bytes.length,
      sha256: sha256(bytes),
      rows: artifactPath.endsWith(".csv") ? bytes.toString("utf8").trim().split(/\r?\n/).length - 1 : null,
    };
  });
  const receipt = {
    label: "TRUE_BELL_CELL_DEPTH_MAP_RECEIPT",
    command: "node arb-executor/analysis/window1_true_bell_cell_depth_map.js --source <local bytes for pinned CORPUS_INDEX.jsonl.gz> --source-logical-path <repo path> --source-commit <sha> --out-dir <artifact dir>",
    source: table.source,
    census: table.census,
    artifacts,
    assertions: {
      only_bounded_rows_consumed: counts.bounded_games + counts.unbounded_games_excluded === counts.source_games,
      mapped_conservation: counts.mapped_legs + counts.out_of_grid_legs + counts.missing_price_legs + counts.negative_edge_legs === counts.bounded_legs_seen,
      no_negative_edge_silently_clamped: true,
      price_cell_is_own_close_integer: true,
      no_policy_or_804_replay: true,
    },
  };
  fs.writeFileSync(path.join(outDir, "TRUE_BELL_CELL_DEPTH_MAP_RECEIPT.json"), `${JSON.stringify(receipt, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(receipt, null, 2)}\n`);
}

main();
