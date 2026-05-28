#!/usr/bin/env python3
"""
visualize_ground_truth.py — ATP_MAIN exit-atlas-v1 ground-truth visualizer.

Renders the exit atlas as a self-contained, single-file interactive HTML:
two side-by-side heatmaps (EV per N, hit-rate %) over the (anchor cent c, R)
plane, where R = T - c is the cents above entry. No picker, no band logic,
no filters — breakeven floor and ceiling are surfaced only as toggleable
overlays. The operator reads the raw surface.

Inputs (exit_atlas_v1, built by build_exit_atlas_v1.py):
  data/durable/exit_atlas_v1/atp_main_atlas.parquet      (8,550 rows, 90c x 95T)
  data/durable/exit_atlas_v1/atp_main_row_dims.parquet   (90 rows, one per cent)

Output:
  data/durable/exit_atlas_v1/atp_main_ground_truth.html  (self-contained)

EV layer  = ev_full_cell_basis  (canonical cell-basis EV, cents/N, full 4,137-N
            corpus, sigma=1 neighborhood). This IS the user's "ground truth" EV.
Hit layer = raw_reach * 100      (fraction of N's at cent c whose peak >= T).

The HTML embeds the data inline as JSON and draws everything with D3 (CDN).
No server, no network beyond the D3 CDN. Opens directly in a browser.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# Paths — resolve relative to this file so the script runs from anywhere.
# analysis/visualize_ground_truth.py  ->  arb-executor/  ->  data/durable/...
# ----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ARB_ROOT = HERE.parent  # arb-executor/
ATLAS_DIR = ARB_ROOT / "data" / "durable" / "exit_atlas_v1"

ATLAS_PARQUET = ATLAS_DIR / "atp_main_atlas.parquet"
ROW_DIMS_PARQUET = ATLAS_DIR / "atp_main_row_dims.parquet"
OUT_HTML = ATLAS_DIR / "atp_main_ground_truth.html"

# Total N corpus — used for the "$ if deployed on all N at 10ct" projection.
N_TOTAL = 4137
CONTRACTS_AT_10CT = 10  # the operator's reference deployment size


def _clean_num(x):
    """JSON can't carry NaN/inf — coerce to None so JS sees null."""
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def build_payload() -> dict:
    """Load the atlas + row_dims and reduce to the JSON the viz needs."""
    atlas = pd.read_parquet(ATLAS_PARQUET)
    dims = pd.read_parquet(ROW_DIMS_PARQUET)

    # ---- cells: only the valid (T > c) cells with a defined EV -------------
    # We carry the absolute minimum per cell: c, R, hit%, ev. T and $ are
    # derived in JS (T=c+R, $=ev*N_TOTAL/100*10) to keep the file lean.
    valid = atlas[atlas["ev_full_cell_basis"].notna()].copy()
    valid["R"] = valid["T"].astype(int) - valid["c"].astype(int)

    cells = []
    for row in valid.itertuples(index=False):
        cells.append(
            {
                "c": int(row.c),
                "R": int(row.R),
                "hit": _clean_num(row.raw_reach * 100.0),
                "ev": _clean_num(row.ev_full_cell_basis),
            }
        )

    # ---- per-cent row dims -------------------------------------------------
    rows = []
    for d in dims.itertuples(index=False):
        rows.append(
            {
                "c": int(d.c),
                "ownN": int(d.ownN),
                "effN": _clean_num(d.effN),
                "wins": int(d.wins),
                "winRate": _clean_num(d.win_rate_neighborhood),
                "breakevenFloorR": int(d.breakeven_floor_R),
                "ceilingMaxR": int(d.ceiling_max_R),
            }
        )

    ev_vals = [c["ev"] for c in cells if c["ev"] is not None]
    hit_vals = [c["hit"] for c in cells if c["hit"] is not None]

    # Symmetric diverging domain for EV, perceptually centered at 0.
    ev_abs_max = max(abs(min(ev_vals)), abs(max(ev_vals)))

    return {
        "meta": {
            "nTotal": N_TOTAL,
            "contractsAt10ct": CONTRACTS_AT_10CT,
            "cMin": int(atlas["c"].min()),
            "cMax": int(atlas["c"].max()),
            "rMax": int((atlas["T"] - atlas["c"]).max()),
            "evMin": min(ev_vals),
            "evMax": max(ev_vals),
            "evAbsMax": ev_abs_max,
            "hitMin": min(hit_vals),
            "hitMax": max(hit_vals),
            "validCells": len(cells),
        },
        "cells": cells,
        "rows": rows,
    }


# ----------------------------------------------------------------------------
# The HTML template. {DATA_JSON} is replaced with the embedded payload.
# All CSS/JS inline; D3 v7 from CDN.
# ----------------------------------------------------------------------------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ATP_MAIN — Exit Atlas v1 Ground Truth</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  :root {
    --bg: #ffffff;
    --panel: #f7f7f8;
    --panel-border: #e2e2e6;
    --ink: #14151a;
    --ink-soft: #5c6068;
    --ink-faint: #9aa0a8;
    --grid-empty: transparent;
    --accent: #2563eb;
    --row-hl: rgba(37, 99, 235, 0.16);
    --overlay-floor: #b026ff;
    --overlay-ceil: #ff1493;
    --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0e0f13;
      --panel: #16181d;
      --panel-border: #2a2d35;
      --ink: #e8eaed;
      --ink-soft: #a7adb6;
      --ink-faint: #6b7079;
      --accent: #5b8dff;
      --row-hl: rgba(91, 141, 255, 0.20);
    }
  }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: var(--sans);
    -webkit-font-smoothing: antialiased;
  }
  body { padding: 14px 18px 24px; }
  h1 { font-size: 17px; font-weight: 650; margin: 0 0 2px; letter-spacing: -0.01em; }
  .sub { font-size: 12px; color: var(--ink-soft); margin: 0 0 12px; }
  .sub code { font-family: var(--mono); font-size: 11px; }

  .controls {
    display: flex; flex-wrap: wrap; gap: 14px 22px; align-items: center;
    padding: 9px 12px; margin-bottom: 12px;
    background: var(--panel); border: 1px solid var(--panel-border); border-radius: 8px;
    font-size: 12.5px;
  }
  .controls label { display: inline-flex; gap: 6px; align-items: center; cursor: pointer; user-select: none; }
  .controls input[type=checkbox] { accent-color: var(--accent); width: 14px; height: 14px; }
  .ctl-group { display: inline-flex; gap: 16px; align-items: center; }
  .ctl-sep { width: 1px; height: 18px; background: var(--panel-border); }
  .swatch { display: inline-block; width: 18px; height: 3px; border-radius: 2px; vertical-align: middle; margin-right: 2px; }

  .stage { display: flex; gap: 16px; align-items: flex-start; }
  .plots { display: flex; gap: 18px; flex: 1 1 auto; min-width: 0; }
  .plot-wrap { flex: 1 1 0; min-width: 0; }
  .plot-title { font-size: 12.5px; font-weight: 600; margin: 0 0 1px; }
  .plot-sub { font-size: 11px; color: var(--ink-soft); margin: 0 0 6px; min-height: 14px; }
  svg { display: block; width: 100%; height: auto; }
  .cell { shape-rendering: crispEdges; }
  .gutter-label { font-family: var(--mono); font-size: 8px; }
  .axis-label { font-size: 11px; fill: var(--ink-soft); font-family: var(--sans); }
  .tick-label { font-size: 9px; fill: var(--ink-faint); font-family: var(--mono); }
  .hl-rect { fill: var(--row-hl); pointer-events: none; }
  .overlay-floor { stroke: var(--overlay-floor); stroke-width: 1.4; fill: none; pointer-events: none; }
  .overlay-ceil  { stroke: var(--overlay-ceil);  stroke-width: 1.2; fill: none; stroke-dasharray: 3 2; pointer-events: none; }
  .density-bar { fill: var(--ink-faint); }
  .density-bar.thin { fill: #e0a000; }

  /* legend */
  .legend { margin-top: 4px; }
  .legend text { font-family: var(--mono); font-size: 9px; fill: var(--ink-soft); }

  /* side panel */
  .side {
    flex: 0 0 360px; max-width: 360px;
    background: var(--panel); border: 1px solid var(--panel-border); border-radius: 8px;
    padding: 10px 12px; max-height: calc(100vh - 40px); overflow: auto;
  }
  .side h2 { font-size: 13px; margin: 0 0 2px; font-weight: 650; }
  .side .hint { font-size: 11px; color: var(--ink-soft); margin: 0 0 8px; }
  table.detail { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 11px; }
  table.detail th, table.detail td { padding: 2px 6px; text-align: right; white-space: nowrap; }
  table.detail th {
    position: sticky; top: 0; background: var(--panel);
    color: var(--ink-soft); font-weight: 600; cursor: pointer; user-select: none;
    border-bottom: 1px solid var(--panel-border);
  }
  table.detail th:hover { color: var(--ink); }
  table.detail th.sorted::after { content: " \25BC"; font-size: 8px; }
  table.detail th.sorted.asc::after { content: " \25B2"; }
  table.detail td:first-child, table.detail th:first-child { text-align: left; }
  table.detail tbody tr:nth-child(even) { background: rgba(127,127,127,0.06); }
  td.pos { color: #138a36; } td.neg { color: #c0392b; }
  @media (prefers-color-scheme: dark) {
    td.pos { color: #5cd17f; } td.neg { color: #ff7a6b; }
  }

  /* tooltip */
  #tip {
    position: fixed; pointer-events: none; z-index: 50;
    background: rgba(20,21,26,0.96); color: #f2f3f5;
    border: 1px solid rgba(255,255,255,0.12); border-radius: 6px;
    padding: 7px 9px; font-family: var(--mono); font-size: 11px; line-height: 1.5;
    box-shadow: 0 6px 20px rgba(0,0,0,0.35); opacity: 0; transition: opacity 0.08s;
    white-space: nowrap;
  }
  #tip b { color: #fff; }
  #tip .tip-ev-pos { color: #5cd17f; } #tip .tip-ev-neg { color: #ff7a6b; }
  .foot { margin-top: 12px; font-size: 10.5px; color: var(--ink-faint); }
  .foot code { font-family: var(--mono); }
</style>
</head>
<body>
  <h1>ATP_MAIN — Exit Atlas v1 · Ground Truth</h1>
  <p class="sub">
    Every cell &times; every conceivable R, EV computed across the full
    <code>4,137-N</code> corpus (sigma=1 neighborhood, cell basis). No picker, no
    bands, no filters — overlays only. <span id="cellcount"></span>
  </p>

  <div class="controls">
    <div class="ctl-group">
      <label><input type="checkbox" id="tg-floor"><span class="swatch" style="background:var(--overlay-floor)"></span>Breakeven floor</label>
      <label><input type="checkbox" id="tg-ceil"><span class="swatch" style="background:var(--overlay-ceil)"></span>Ceiling (R=99&minus;c)</label>
      <label><input type="checkbox" id="tg-density">Density overlay (ownN)</label>
    </div>
    <div class="ctl-sep"></div>
    <div class="ctl-group" style="font-size:11.5px;color:var(--ink-soft)">
      <span>Click a <b>row</b> for R-by-R · click a <b>column header (R)</b> for cross-cent spectrum</span>
    </div>
  </div>

  <div class="stage">
    <div class="plots">
      <div class="plot-wrap">
        <p class="plot-title">Ground-truth EV — avg cents earned per N</p>
        <p class="plot-sub">at every (cell, R), full 4,137-N database · diverging RdYlGn @ 0</p>
        <div id="plot-ev"></div>
      </div>
      <div class="plot-wrap">
        <p class="plot-title">Ground-truth hit rate — % of all N reaching T</p>
        <p class="plot-sub">the bare bounce surface · sequential viridis</p>
        <div id="plot-hit"></div>
      </div>
    </div>
    <div class="side" id="side">
      <h2>Inspector</h2>
      <p class="hint">Hover for a cell readout. Click a row or an R column header to load the full curve here.</p>
    </div>
  </div>

  <div class="foot">
    Source: <code>exit_atlas_v1/atp_main_atlas.parquet</code> (EV =
    <code>ev_full_cell_basis</code>, hit = <code>raw_reach&times;100</code>) +
    <code>atp_main_row_dims.parquet</code>. R = T &minus; c.
    $ figures project EV over all <span id="ntot"></span> N at 10&cent;.
  </div>

  <div id="tip"></div>

<script>
const DATA = {DATA_JSON};
</script>
<script>
(function () {
  "use strict";
  const M = DATA.meta;
  const cells = DATA.cells;
  const rows = DATA.rows;
  const rowByC = new Map(rows.map(r => [r.c, r]));

  document.getElementById("cellcount").textContent =
    M.validCells.toLocaleString() + " valid cells.";
  document.getElementById("ntot").textContent = M.nTotal.toLocaleString();

  // ---- geometry -----------------------------------------------------------
  const cMin = M.cMin, cMax = M.cMax;          // 5..94
  const rMin = 1, rMax = M.rMax;               // 1..94
  const nC = cMax - cMin + 1;                  // 90 rows
  const nR = rMax - rMin + 1;                  // 94 cols

  // index lookups for fast cell access
  const cellMap = new Map();                   // key "c|R" -> cell
  cells.forEach(d => cellMap.set(d.c + "|" + d.R, d));

  // layout constants (data-space px; SVG scales responsively via viewBox)
  const GUT = 34;     // left gutter for "N=" labels + density bars
  const TOP = 8, BOT = 26, RIGHT = 6;
  const CW = 6.4, CH = 6.4;                     // cell size
  const plotW = nR * CW;
  const plotH = nC * CH;
  const W = GUT + plotW + RIGHT;
  const H = TOP + plotH + BOT;

  // y: c=cMax at top, c=cMin at bottom
  const yOf = c => TOP + (cMax - c) * CH;
  const xOf = R => GUT + (R - rMin) * CW;

  // ---- color scales -------------------------------------------------------
  // EV diverging RdYlGn, symmetric about 0 (green = positive).
  const evColor = d3.scaleDiverging(
    t => d3.interpolateRdYlGn(t)
  ).domain([-M.evAbsMax, 0, M.evAbsMax]);
  // Hit rate sequential viridis 0..100.
  const hitColor = d3.scaleSequential(d3.interpolateViridis).domain([0, 100]);

  const fmtEv = v => (v == null ? "—" : (v >= 0 ? "+" : "") + v.toFixed(2));
  const fmtHit = v => (v == null ? "—" : v.toFixed(1));
  const fmtDol = v => (v == null ? "—" : "$" + v.toFixed(2));
  const dollarsOf = ev => ev == null ? null : ev * M.nTotal / 100 * M.contractsAt10ct;

  // ---- build one heatmap SVG ---------------------------------------------
  // kind: "ev" | "hit"
  function buildPlot(containerId, kind) {
    const svg = d3.select("#" + containerId).append("svg")
      .attr("viewBox", `0 0 ${W} ${H + 22}`)   // +22 for legend strip
      .attr("preserveAspectRatio", "xMidYMid meet");

    // highlight rects (under cells) — row + column
    const hlRow = svg.append("rect").attr("class", "hl-rect").style("display", "none");
    const hlCol = svg.append("rect").attr("class", "hl-rect").style("display", "none");

    // cells layer
    const g = svg.append("g");
    const sel = g.selectAll("rect.cell")
      .data(cells, d => d.c + "|" + d.R)
      .enter().append("rect")
      .attr("class", "cell")
      .attr("x", d => xOf(d.R))
      .attr("y", d => yOf(d.c))
      .attr("width", CW)
      .attr("height", CH)
      .attr("fill", d => {
        const v = kind === "ev" ? d.ev : d.hit;
        if (v == null) return "transparent";
        return kind === "ev" ? evColor(v) : hitColor(v);
      })
      .on("mousemove", (ev, d) => showTip(ev, d))
      .on("mouseleave", hideTip)
      .on("click", (ev, d) => selectRow(d.c));

    // overlays layer (floor + ceiling), drawn per row
    const ovFloor = svg.append("g").style("display", "none");
    const ovCeil = svg.append("g").style("display", "none");
    rows.forEach(r => {
      // breakeven floor: vertical tick at R = breakevenFloorR on this row
      const Rf = r.breakevenFloorR;
      if (Rf >= rMin && Rf <= r.ceilingMaxR) {
        ovFloor.append("line")
          .attr("class", "overlay-floor")
          .attr("x1", xOf(Rf)).attr("x2", xOf(Rf))
          .attr("y1", yOf(r.c)).attr("y2", yOf(r.c) + CH);
      }
      // ceiling: the last valid cell on this row (R = ceilingMaxR)
      const Rc = r.ceilingMaxR;
      if (Rc >= rMin) {
        ovCeil.append("line")
          .attr("class", "overlay-ceil")
          .attr("x1", xOf(Rc) + CW).attr("x2", xOf(Rc) + CW)
          .attr("y1", yOf(r.c)).attr("y2", yOf(r.c) + CH);
      }
    });

    // density layer (ownN bars in the gutter) — hidden by default
    const dens = svg.append("g").style("display", "none");
    const maxOwn = d3.max(rows, r => r.ownN);
    const densScale = d3.scaleLinear().domain([0, maxOwn]).range([0, GUT - 4]);
    rows.forEach(r => {
      dens.append("rect")
        .attr("class", "density-bar" + (r.ownN < 30 ? " thin" : ""))
        .attr("x", GUT - 2 - densScale(r.ownN))
        .attr("y", yOf(r.c) + 1)
        .attr("width", densScale(r.ownN))
        .attr("height", CH - 1);
    });

    // gutter "N=" labels
    const gut = svg.append("g");
    rows.forEach(r => {
      gut.append("text")
        .attr("class", "gutter-label")
        .attr("x", GUT - 3)
        .attr("y", yOf(r.c) + CH - 1)
        .attr("text-anchor", "end")
        .attr("fill", r.ownN < 30 ? "var(--ink-faint)" : "var(--ink)")
        .text("N=" + r.ownN)
        .style("cursor", "pointer")
        .on("click", () => selectRow(r.c));
    });

    // y axis ticks (every 5 cents)
    for (let c = cMin; c <= cMax; c++) {
      if (c % 5 === 0) {
        svg.append("text").attr("class", "tick-label")
          .attr("x", 2).attr("y", yOf(c) + CH).attr("text-anchor", "start")
          .style("display", "none"); // gutter already crowded; keep clean
      }
    }
    // x axis ticks (every 5 R) + axis label, clickable column headers
    const xaxis = svg.append("g");
    for (let R = rMin; R <= rMax; R++) {
      if (R === 1 || R % 5 === 0) {
        xaxis.append("text").attr("class", "tick-label")
          .attr("x", xOf(R) + CW / 2).attr("y", H - 14)
          .attr("text-anchor", "middle").text(R)
          .style("cursor", "pointer")
          .on("click", () => selectCol(R));
      }
    }
    // invisible wide click strips per column for easy column selection
    const colHit = svg.append("g");
    for (let R = rMin; R <= rMax; R++) {
      colHit.append("rect")
        .attr("x", xOf(R)).attr("y", H - 12).attr("width", CW).attr("height", 12)
        .attr("fill", "transparent").style("cursor", "pointer")
        .on("click", () => selectCol(R));
    }
    svg.append("text").attr("class", "axis-label")
      .attr("x", GUT + plotW / 2).attr("y", H)
      .attr("text-anchor", "middle").text("R  (cents above entry, T = c + R)");

    // ---- legend strip ----
    const legY = H + 8;
    const legW = 150, legH = 8, legX = GUT;
    const lg = svg.append("g").attr("class", "legend");
    const gradId = containerId + "-grad";
    const defs = svg.append("defs");
    const grad = defs.append("linearGradient").attr("id", gradId)
      .attr("x1", "0%").attr("x2", "100%");
    const stops = 12;
    for (let i = 0; i <= stops; i++) {
      const t = i / stops;
      let col;
      if (kind === "ev") col = evColor(-M.evAbsMax + t * 2 * M.evAbsMax);
      else col = hitColor(t * 100);
      grad.append("stop").attr("offset", (t * 100) + "%").attr("stop-color", col);
    }
    lg.append("rect").attr("x", legX).attr("y", legY)
      .attr("width", legW).attr("height", legH).attr("fill", `url(#${gradId})`)
      .attr("stroke", "var(--panel-border)");
    if (kind === "ev") {
      lg.append("text").attr("x", legX).attr("y", legY + legH + 9).attr("text-anchor", "start")
        .text((-M.evAbsMax).toFixed(1) + "c");
      lg.append("text").attr("x", legX + legW / 2).attr("y", legY + legH + 9).attr("text-anchor", "middle").text("0");
      lg.append("text").attr("x", legX + legW).attr("y", legY + legH + 9).attr("text-anchor", "end")
        .text("+" + M.evAbsMax.toFixed(1) + "c");
    } else {
      lg.append("text").attr("x", legX).attr("y", legY + legH + 9).attr("text-anchor", "start").text("0%");
      lg.append("text").attr("x", legX + legW).attr("y", legY + legH + 9).attr("text-anchor", "end").text("100%");
    }

    return { svg, sel, hlRow, hlCol, ovFloor, ovCeil, dens };
  }

  const P_EV = buildPlot("plot-ev", "ev");
  const P_HIT = buildPlot("plot-hit", "hit");
  const plots = [P_EV, P_HIT];

  // ---- tooltip ------------------------------------------------------------
  const tip = document.getElementById("tip");
  function showTip(event, d) {
    const r = rowByC.get(d.c);
    const T = d.c + d.R;
    const dol = dollarsOf(d.ev);
    const evCls = d.ev == null ? "" : (d.ev >= 0 ? "tip-ev-pos" : "tip-ev-neg");
    tip.innerHTML =
      `<b>c=${d.c}c</b>, R=+${d.R}, T=${T}c<br>` +
      `EV: <span class="${evCls}">${fmtEv(d.ev)}c</span> per N<br>` +
      `Hit rate: ${fmtHit(d.hit)}%<br>` +
      `ownN at this cent: ${r ? r.ownN : "—"}<br>` +
      `if deployed on all ${M.nTotal} N at 10ct: <b>${fmtDol(dol)}</b>`;
    tip.style.opacity = 1;
    const pad = 14;
    let x = event.clientX + pad, y = event.clientY + pad;
    const bb = tip.getBoundingClientRect();
    if (x + bb.width > window.innerWidth) x = event.clientX - bb.width - pad;
    if (y + bb.height > window.innerHeight) y = event.clientY - bb.height - pad;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  function hideTip() { tip.style.opacity = 0; }

  // ---- highlight helpers --------------------------------------------------
  function clearHL() {
    plots.forEach(p => {
      p.hlRow.style("display", "none");
      p.hlCol.style("display", "none");
    });
  }
  function highlightRow(c) {
    clearHL();
    plots.forEach(p => {
      p.hlRow
        .attr("x", GUT).attr("y", yOf(c) - 0.5)
        .attr("width", plotW).attr("height", CH + 1)
        .style("display", null);
    });
  }
  function highlightCol(R) {
    clearHL();
    plots.forEach(p => {
      p.hlCol
        .attr("x", xOf(R) - 0.5).attr("y", TOP)
        .attr("width", CW + 1).attr("height", plotH)
        .style("display", null);
    });
  }

  // ---- side panel: sortable table -----------------------------------------
  let sortState = { key: "R", asc: true };
  function renderTable(title, hint, columns, data) {
    const side = d3.select("#side");
    side.html("");
    side.append("h2").text(title);
    side.append("p").attr("class", "hint").text(hint);

    const sortKey = sortState.key;
    const cmp = (a, b) => {
      let va = a[sortKey], vb = b[sortKey];
      if (va == null) va = -Infinity; if (vb == null) vb = -Infinity;
      return sortState.asc ? va - vb : vb - va;
    };
    const sorted = data.slice().sort(cmp);

    const table = side.append("table").attr("class", "detail");
    const thead = table.append("thead").append("tr");
    columns.forEach(col => {
      const th = thead.append("th").text(col.label).attr("data-key", col.key);
      if (col.key === sortState.key) th.classed("sorted", true).classed("asc", sortState.asc);
      th.on("click", () => {
        if (sortState.key === col.key) sortState.asc = !sortState.asc;
        else { sortState.key = col.key; sortState.asc = true; }
        renderTable(title, hint, columns, data);
      });
    });
    const tbody = table.append("tbody");
    sorted.forEach(d => {
      const tr = tbody.append("tr");
      columns.forEach(col => {
        const td = tr.append("td").html(col.fmt(d[col.key], d));
        if (col.key === "ev") td.attr("class", d.ev == null ? "" : (d.ev >= 0 ? "pos" : "neg"));
        if (col.key === "dollars") td.attr("class", d.dollars == null ? "" : (d.dollars >= 0 ? "pos" : "neg"));
      });
    });
  }

  const COL_R   = { key: "R", label: "R", fmt: v => "+" + v };
  const COL_T   = { key: "T", label: "T", fmt: v => v + "c" };
  const COL_C   = { key: "c", label: "c", fmt: v => v + "c" };
  const COL_HIT = { key: "hit", label: "hit%", fmt: v => fmtHit(v) };
  const COL_EV  = { key: "ev", label: "EV/N", fmt: v => fmtEv(v) };
  const COL_DOL = { key: "dollars", label: "$@10ct", fmt: v => fmtDol(v) };

  function selectRow(c) {
    highlightRow(c);
    const r = rowByC.get(c);
    const data = cells.filter(d => d.c === c).map(d => ({
      R: d.R, T: d.c + d.R, hit: d.hit, ev: d.ev, dollars: dollarsOf(d.ev),
    }));
    sortState = { key: "R", asc: true };
    renderTable(
      `Cell c=${c}c  ·  ownN=${r ? r.ownN : "—"}`,
      `Every conceivable R for this entry cent. Breakeven floor R≥${r ? r.breakevenFloorR : "—"}, ceiling R≤${r ? r.ceilingMaxR : "—"}. $ = EV over all ${M.nTotal} N @10ct.`,
      [COL_R, COL_T, COL_HIT, COL_EV, COL_DOL], data
    );
  }

  function selectCol(R) {
    highlightCol(R);
    const data = cells.filter(d => d.R === R).map(d => ({
      c: d.c, T: d.c + d.R, hit: d.hit, ev: d.ev, dollars: dollarsOf(d.ev),
    }));
    sortState = { key: "c", asc: true };
    renderTable(
      `Fixed R = +${R}  ·  cross-cent spectrum`,
      `How the same +${R}c offset performs across every entry cent. $ = EV over all ${M.nTotal} N @10ct.`,
      [COL_C, COL_T, COL_HIT, COL_EV, COL_DOL], data
    );
  }

  // expose for keyboard/external (and the gutter handlers already call them)
  window.__selectRow = selectRow;
  window.__selectCol = selectCol;

  // ---- toggles ------------------------------------------------------------
  document.getElementById("tg-floor").addEventListener("change", e => {
    const on = e.target.checked;
    plots.forEach(p => p.ovFloor.style("display", on ? null : "none"));
  });
  document.getElementById("tg-ceil").addEventListener("change", e => {
    const on = e.target.checked;
    plots.forEach(p => p.ovCeil.style("display", on ? null : "none"));
  });
  document.getElementById("tg-density").addEventListener("change", e => {
    const on = e.target.checked;
    plots.forEach(p => p.dens.style("display", on ? null : "none"));
  });

  // default selection so the inspector isn't empty: a known problematic cell
  selectRow(38);
})();
</script>
</body>
</html>
"""


def main() -> None:
    payload = build_payload()
    data_json = json.dumps(payload, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("{DATA_JSON}", data_json)
    OUT_HTML.write_text(html, encoding="utf-8")
    m = payload["meta"]
    print(f"wrote {OUT_HTML}")
    print(f"  valid cells : {m['validCells']}")
    print(f"  c range     : {m['cMin']}..{m['cMax']}  R max: {m['rMax']}")
    print(f"  EV range    : {m['evMin']:.3f}..{m['evMax']:.3f}  (|max|={m['evAbsMax']:.3f})")
    print(f"  hit range   : {m['hitMin']:.2f}..{m['hitMax']:.2f}")
    print(f"  size        : {OUT_HTML.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
