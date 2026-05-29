#!/usr/bin/env python3
"""
visualize_ground_truth_v2.py — ATP_MAIN neighbor-pooled ground-truth visualizer.

Same spirit as v1: two side-by-side triangular heatmaps over the (anchor cent c,
R) plane, R = T - c. Every cell, every conceivable R out to that cent's ceiling
(T <= 99). No picker, no chains, no filters — breakeven/ceiling/density are
toggleable overlays only. The operator reads the raw surface.

The ONE change from v1: the surface is NEIGHBOR-POOLED. Each cell borrows N from
its neighboring cents (Gaussian, sigma=5 from leave-one-cent-out CV), so a cent
is no longer judged off its thin own-N count. The gradient is smooth and flows
across price — the data is one spectrum.

Reads the pre-computed surface from build_pooled_surface.py:
  data/durable/exit_atlas_v1/atp_main_pooled_surface.json

Emits a self-contained single-file HTML (D3 v7 from CDN):
  data/durable/exit_atlas_v1/atp_main_ground_truth_v2.html

Lenses (radio switch, NOT a filter — just which surface colors the left plot):
  EV   — avg cents earned per N (diverging RdYlGn @ 0)
  ROI  — EV / cost, % (cheap & expensive cents compete on the same scale)
The right plot is always the hit-rate surface (viridis).

Rich hover exposes what each cell "takes from and assumes":
  EV / hit / ROI for that exit, the neighbor contribution breakdown (which cents
  feed the cell and at what weight / effective-N), and the two-sided-G complement.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARB_ROOT = HERE.parent
ATLAS_DIR = ARB_ROOT / "data" / "durable" / "exit_atlas_v1"
SURFACE_JSON = ATLAS_DIR / "atp_main_pooled_surface_v3.json"
OUT_HTML = ATLAS_DIR / "atp_main_ground_truth_v3.html"


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ATP_MAIN — Ground Truth v3 · Pooled Best-X</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  :root {
    --bg: #ffffff; --panel: #f7f7f8; --panel-border: #e2e2e6;
    --ink: #14151a; --ink-soft: #5c6068; --ink-faint: #9aa0a8;
    --accent: #2563eb; --row-hl: rgba(37, 99, 235, 0.16);
    --overlay-floor: #b026ff; --overlay-ceil: #ff1493; --overlay-comp: #00b3a4;
    --overlay-bestx: #00c2ff;
    --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0e0f13; --panel: #16181d; --panel-border: #2a2d35;
      --ink: #e8eaed; --ink-soft: #a7adb6; --ink-faint: #6b7079;
      --accent: #5b8dff; --row-hl: rgba(91, 141, 255, 0.20);
    }
  }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: var(--sans); -webkit-font-smoothing: antialiased; }
  body { padding: 14px 18px 24px; }
  h1 { font-size: 17px; font-weight: 650; margin: 0 0 2px; letter-spacing: -0.01em; }
  .sub { font-size: 12px; color: var(--ink-soft); margin: 0 0 12px; }
  .sub code { font-family: var(--mono); font-size: 11px; }

  .controls { display: flex; flex-wrap: wrap; gap: 14px 22px; align-items: center;
    padding: 9px 12px; margin-bottom: 12px; background: var(--panel);
    border: 1px solid var(--panel-border); border-radius: 8px; font-size: 12.5px; }
  .controls label { display: inline-flex; gap: 6px; align-items: center; cursor: pointer; user-select: none; }
  .controls input { accent-color: var(--accent); }
  .ctl-group { display: inline-flex; gap: 16px; align-items: center; }
  .ctl-sep { width: 1px; height: 18px; background: var(--panel-border); }
  .ctl-group b.glabel { font-weight: 600; color: var(--ink-soft); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
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
  .overlay-bestx { stroke: var(--overlay-bestx); stroke-width: 1.6; fill: none; pointer-events: none; }
  .bestx-dot { fill: var(--overlay-bestx); pointer-events: none; }
  .density-bar { fill: var(--ink-faint); }
  .density-bar.thin { fill: #e0a000; }

  .legend { margin-top: 4px; }
  .legend text { font-family: var(--mono); font-size: 9px; fill: var(--ink-soft); }

  .side { flex: 0 0 380px; max-width: 380px; background: var(--panel);
    border: 1px solid var(--panel-border); border-radius: 8px;
    padding: 10px 12px; max-height: calc(100vh - 40px); overflow: auto; }
  .side h2 { font-size: 13px; margin: 0 0 2px; font-weight: 650; }
  .side .hint { font-size: 11px; color: var(--ink-soft); margin: 0 0 8px; }
  table.detail { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 11px; }
  table.detail th, table.detail td { padding: 2px 6px; text-align: right; white-space: nowrap; }
  table.detail th { position: sticky; top: 0; background: var(--panel);
    color: var(--ink-soft); font-weight: 600; cursor: pointer; user-select: none;
    border-bottom: 1px solid var(--panel-border); }
  table.detail th:hover { color: var(--ink); }
  table.detail th.sorted::after { content: " \25BC"; font-size: 8px; }
  table.detail th.sorted.asc::after { content: " \25B2"; }
  table.detail td:first-child, table.detail th:first-child { text-align: left; }
  table.detail tbody tr:nth-child(even) { background: rgba(127,127,127,0.06); }
  td.pos { color: #138a36; } td.neg { color: #c0392b; }
  @media (prefers-color-scheme: dark) { td.pos { color: #5cd17f; } td.neg { color: #ff7a6b; } }

  #tip { position: fixed; pointer-events: none; z-index: 50;
    background: rgba(20,21,26,0.97); color: #f2f3f5;
    border: 1px solid rgba(255,255,255,0.12); border-radius: 6px;
    padding: 8px 10px; font-family: var(--mono); font-size: 11px; line-height: 1.55;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4); opacity: 0; transition: opacity 0.08s;
    white-space: nowrap; max-width: 320px; }
  #tip b { color: #fff; }
  #tip .tip-ev-pos { color: #5cd17f; } #tip .tip-ev-neg { color: #ff7a6b; }
  #tip .tip-rule { border-top: 1px solid rgba(255,255,255,0.14); margin: 5px 0; }
  #tip .tip-dim { color: #aab0ba; }
  #tip .tip-nbr { color: #d8dde4; font-size: 10px; }
  .foot { margin-top: 12px; font-size: 10.5px; color: var(--ink-faint); }
  .foot code { font-family: var(--mono); }
</style>
</head>
<body>
  <h1>ATP_MAIN — Ground Truth v3 · Pooled Best-X</h1>
  <p class="sub">
    <b>Default lens = Achievable:</b> every row is colored by its best exit, taken as the
    BETTER of its own raw T-20 Foundation tape and the neighbor-pooled read &mdash; pooling
    only enriches thin cells upward, never drags a Foundation-positive cell negative. So every
    cent &mdash; favorites included &mdash; reads its true achievable edge (green = positive); only
    67/68/82 stay soft because they are negative on the raw tapes themselves.
    Switch to <b>EV</b> to see every individual exit (most are bad, so the top looks red there &mdash;
    that is the average of all exits, not the best one). EV/hit/ROI
    pooled across the full <code>4,137-N</code> corpus with each cent borrowing N
    from its neighbors (Gaussian, <code id="sigtxt">&sigma;</code>, CV-chosen). No
    picker, no chains, no filters — overlays only. <span id="cellcount"></span>
  </p>

  <div class="controls">
    <div class="ctl-group">
      <b class="glabel">Left lens</b>
      <label><input type="radio" name="lens" value="ev"> EV (cents/N)</label>
      <label><input type="radio" name="lens" value="roi"> ROI (EV/cost %)</label>
      <label><input type="radio" name="lens" value="ach" checked> Achievable (pooled best-X ROI)</label>
      <label><input type="radio" name="lens" value="fin"> Finest config (dual-layer)</label>
    </div>
    <div class="ctl-sep"></div>
    <div class="ctl-group">
      <b class="glabel">Overlays</b>
      <label><input type="checkbox" id="tg-floor"><span class="swatch" style="background:var(--overlay-floor)"></span>Breakeven floor</label>
      <label><input type="checkbox" id="tg-ceil"><span class="swatch" style="background:var(--overlay-ceil)"></span>Ceiling (R=99&minus;c)</label>
      <label><input type="checkbox" id="tg-bestx" checked><span class="swatch" style="background:var(--overlay-bestx)"></span>Best-X (pooled)</label>
      <label><input type="checkbox" id="tg-density">Density (ownN)</label>
    </div>
    <div class="ctl-sep"></div>
    <div class="ctl-group" style="font-size:11.5px;color:var(--ink-soft)">
      <span>Click a <b>row</b> for R-by-R · click an <b>R</b> for cross-cent spectrum</span>
    </div>
  </div>

  <div class="stage">
    <div class="plots">
      <div class="plot-wrap">
        <p class="plot-title" id="left-title">Pooled EV — avg cents earned per N</p>
        <p class="plot-sub" id="left-sub">at every (cell, R), neighbor-pooled · diverging RdYlGn @ 0</p>
        <div id="plot-left"></div>
      </div>
      <div class="plot-wrap">
        <p class="plot-title">Pooled hit rate — % of pooled N reaching T</p>
        <p class="plot-sub">the bounce surface · sequential viridis</p>
        <div id="plot-hit"></div>
      </div>
    </div>
    <div class="side" id="side">
      <h2>Inspector</h2>
      <p class="hint">Hover any cell for its full readout + what it borrows from. Click a row or an R column header to load the curve here.</p>
    </div>
  </div>

  <div class="foot">
    Source: <code>atp_main_pooled_surface_v3.json</code> (built by
    <code>build_pooled_surface_v3.py</code> from <code>atp_main_spike_perN.parquet</code>).
    Cell basis: enter at c; reach T &rarr; +(T&minus;c); else settle 99&minus;c (win) or &minus;c (loss).
    R = T &minus; c. Neighbor pooling &sigma; from leave-one-cent-out CV.
    <br><b>Best-X</b> / <b>Achievable</b> are the <b>POOLED</b> hindsight-optimal exit-or-hold per cent:
    each cent sweeps every reachable X over its <b>neighbor-weighted N</b> (effN, often hundreds) and picks
    the X maximizing pooled PnL. Pool width &sigma; is chosen per-cent by leave-one-cent-out CV (wide where
    cheap, tight in the favorite zone), with an <b>own-N fallback</b> when neighbors only contaminate the cell.
    The LOCKED own-N map (<code>descriptive_1c</code>) is shown alongside for reference. <b>Descriptive / hindsight</b>, NOT predictive.
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
  const ach = DATA.achievable || {};
  const achLocked = DATA.achievableLocked || {};
  const finest = DATA.finest || {};
  const achByC = c => ach[c] || (rowByC.get(c) && rowByC.get(c).achievable) || null;
  const finByC = c => finest[c] || null;
  const achLockedByC = c => achLocked[c] || (rowByC.get(c) && rowByC.get(c).achievableLocked) || null;
  // achievable ROI range (locked best-X per cent) for the achievable lens scale
  const achRois = Object.values(ach).map(a => a.roi).filter(v => v != null);
  const achAbsMax = achRois.length ? Math.max(Math.abs(d3.min(achRois)), Math.abs(d3.max(achRois))) : 1;

  document.getElementById("cellcount").textContent = M.validCells.toLocaleString() + " valid cells.";
  document.getElementById("sigtxt").textContent = "\u03c3=" + M.sigmaBase;

  const cMin = M.cMin, cMax = M.cMax;
  const rMin = 1, rMax = M.rMax;
  const nC = cMax - cMin + 1, nR = rMax - rMin + 1;

  const cellMap = new Map();
  cells.forEach(d => cellMap.set(d.c + "|" + d.R, d));

  const GUT = 34, TOP = 8, BOT = 26, RIGHT = 6;
  const CW = 6.4, CH = 6.4;
  const plotW = nR * CW, plotH = nC * CH;
  const W = GUT + plotW + RIGHT, H = TOP + plotH + BOT;
  const yOf = c => TOP + (cMax - c) * CH;
  const xOf = R => GUT + (R - rMin) * CW;

  // color scales: EV & ROI diverging @0; hit sequential viridis
  const evColor = d3.scaleDiverging(t => d3.interpolateRdYlGn(t)).domain([-M.evAbsMax, 0, M.evAbsMax]);
  const roiColor = d3.scaleDiverging(t => d3.interpolateRdYlGn(t)).domain([-M.roiAbsMax, 0, M.roiAbsMax]);
  // achievable lens: log-ish diverging on the locked best-X ROI (cheap cents huge,
  // so use a soft sqrt compression to keep the favorite zone readable)
  const achScaleMax = Math.min(achAbsMax, 25);  // clamp; cheap cents run to +200%, compress
  function achColor(roi) {
    if (roi == null) return "transparent";
    const v = Math.max(-achScaleMax, Math.min(achScaleMax, roi));
    return d3.interpolateRdYlGn(0.5 + 0.5 * v / achScaleMax);
  }
  const hitColor = d3.scaleSequential(d3.interpolateViridis).domain([0, 100]);

  const fmtEv = v => (v == null ? "—" : (v >= 0 ? "+" : "") + v.toFixed(2));
  const fmtRoi = v => (v == null ? "—" : (v >= 0 ? "+" : "") + v.toFixed(0) + "%");
  const fmtHit = v => (v == null ? "—" : v.toFixed(1));
  const fmtDol = v => (v == null ? "—" : (v < 0 ? "-$" + Math.abs(v).toFixed(2) : "$" + v.toFixed(2)));
  // $ if this exit were deployed at 10 contracts/N. CRITICAL: scale by THIS
  // cell's effective neighbor N (the contracts actually in its price range),
  // NOT the whole 4,137 corpus. The full corpus is dominated by cheap/mid
  // anchors that never traded near a favorite cent -- pricing them all at an
  // 88c entry booked nonsense -88c losses and made every favorite look
  // "deployed-negative." Each cell feeds only from its own neighborhood.
  const CONTRACTS = 10;
  const effNofC = c => { const r = rowByC.get(c); return (r && r.effN != null) ? r.effN : M.nTotal; };
  const dollarsOf = (ev, c) => ev == null ? null : ev * effNofC(c) / 100 * CONTRACTS;

  let lens = "ach";  // "ev" | "roi" | "ach" — default to the achievable best-X surface
  // For the achievable lens every cell in a cent's row shares that cent's locked
  // best-X ROI (it is a per-cent achievable read, not per-(c,R)). The best-X
  // marker shows WHICH R that is.
  const leftVal = d => {
    if (lens === "ev") return d.ev;
    if (lens === "roi") return d.roi;
    if (lens === "fin") { const f = finByC(d.c); return f ? f.effRoi : null; }
    const a = achByC(d.c);
    return a ? a.roi : null;
  };
  // Finest lens renders the DUAL layer: hue = eff-N ROI (pooled depth), and
  // CONFIDENCE modulates it -- 'confident' (own-N and eff-N agree) renders at
  // full opacity; 'thin'/'own-only' (layers diverge) renders dimmed so a
  // borrowed positive can't masquerade as a proven one. A cell with NO positive
  // config is absent from finest -> transparent (honestly blank, not least-bad).
  // EFF-N LEADS: a positive eff-N pool is the verdict. 'confident' = own-N also
  // agrees (full). 'tape-watch' = eff-N positive but the thin/drift-biased own
  // tape lags -- a mild dim (watch-note), NOT the old heavy downgrade, because
  // own-N can no longer veto the deep pool. Blank only if no positive config.
  const finOpacity = c => {
    const f = finByC(c);
    if (!f) return 0.0;
    if (f.confidence === "confident") return 1.0;
    return 0.78; // tape-watch: eff-N positive, own tape lags (likely T-20 drift bias)
  };
  const leftColor = v => {
    if (v == null) return "transparent";
    if (lens === "ev") return evColor(v);
    if (lens === "roi") return roiColor(v);
    return achColor(v);  // "ach" and "fin" both use the RdYlGn ROI scale
  };

  function buildPlot(containerId, kind) {
    // kind: "left" (lens-driven) | "hit"
    const svg = d3.select("#" + containerId).append("svg")
      .attr("viewBox", `0 0 ${W} ${H + 22}`).attr("preserveAspectRatio", "xMidYMid meet");
    const hlRow = svg.append("rect").attr("class", "hl-rect").style("display", "none");
    const hlCol = svg.append("rect").attr("class", "hl-rect").style("display", "none");

    const g = svg.append("g");
    const sel = g.selectAll("rect.cell")
      .data(cells, d => d.c + "|" + d.R)
      .enter().append("rect")
      .attr("class", "cell")
      .attr("x", d => xOf(d.R)).attr("y", d => yOf(d.c))
      .attr("width", CW).attr("height", CH)
      .attr("fill", d => kind === "hit"
        ? (d.hit == null ? "transparent" : hitColor(d.hit))
        : leftColor(leftVal(d)))
      .on("mousemove", (ev, d) => showTip(ev, d))
      .on("mouseleave", hideTip)
      .on("click", (ev, d) => selectRow(d.c));

    const ovFloor = svg.append("g").style("display", "none");
    const ovCeil = svg.append("g").style("display", "none");
    rows.forEach(r => {
      const Rf = r.breakevenFloorR;
      if (Rf >= rMin && Rf <= r.ceilingMaxR) {
        ovFloor.append("line").attr("class", "overlay-floor")
          .attr("x1", xOf(Rf)).attr("x2", xOf(Rf))
          .attr("y1", yOf(r.c)).attr("y2", yOf(r.c) + CH);
      }
      const Rc = r.ceilingMaxR;
      if (Rc >= rMin) {
        ovCeil.append("line").attr("class", "overlay-ceil")
          .attr("x1", xOf(Rc) + CW).attr("x2", xOf(Rc) + CW)
          .attr("y1", yOf(r.c)).attr("y2", yOf(r.c) + CH);
      }
    });

    // best-X marker: the locked hindsight-optimal exit R per cent (a vertical
    // tick in that cent's row at R = bestX), drawn on BOTH heatmaps. ON by default.
    const ovBestX = svg.append("g");
    rows.forEach(r => {
      const a = r.achievable || achByC(r.c);
      if (!a || a.bestX == null) return;
      // No profitable exit => no "best" tick. Drawing a cyan best-X on a cell
      // whose achievable EV is <=0 (the honest no-config cells, e.g. 68/82)
      // falsely reads as a profitable best and lands under the floor.
      if ((a.ev || 0) <= 0) return;
      const Rb = a.bestX;
      if (Rb < rMin || Rb > r.ceilingMaxR) return;
      ovBestX.append("line").attr("class", "overlay-bestx")
        .attr("x1", xOf(Rb) + CW / 2).attr("x2", xOf(Rb) + CW / 2)
        .attr("y1", yOf(r.c)).attr("y2", yOf(r.c) + CH);
      ovBestX.append("circle").attr("class", "bestx-dot")
        .attr("cx", xOf(Rb) + CW / 2).attr("cy", yOf(r.c) + CH / 2).attr("r", 1.1);
    });

    const dens = svg.append("g").style("display", "none");
    const maxOwn = d3.max(rows, r => r.ownN);
    const densScale = d3.scaleLinear().domain([0, maxOwn]).range([0, GUT - 4]);
    rows.forEach(r => {
      dens.append("rect").attr("class", "density-bar" + (r.ownN < 30 ? " thin" : ""))
        .attr("x", GUT - 2 - densScale(r.ownN)).attr("y", yOf(r.c) + 1)
        .attr("width", densScale(r.ownN)).attr("height", CH - 1);
    });

    const gut = svg.append("g");
    rows.forEach(r => {
      // Thin the gutter to every 5th cent so the 8px "N=" labels never crowd.
      // Non-labeled rows still get a clickable tick to preserve row selection.
      const labeled = (r.c % 5 === 0);
      if (labeled) {
        gut.append("text").attr("class", "gutter-label")
          .attr("x", GUT - 3).attr("y", yOf(r.c) + CH - 1).attr("text-anchor", "end")
          .attr("fill", r.ownN < 30 ? "var(--ink-faint)" : "var(--ink)")
          .text(r.c + "\u00A2 \u00B7 N=" + r.ownN).style("cursor", "pointer")
          .on("click", () => selectRow(r.c));
      } else {
        gut.append("line").attr("class", "gutter-tick")
          .attr("x1", GUT - 6).attr("x2", GUT - 3)
          .attr("y1", yOf(r.c) + CH / 2).attr("y2", yOf(r.c) + CH / 2)
          .attr("stroke", "var(--ink-faint)").attr("stroke-width", 0.5)
          .style("cursor", "pointer").on("click", () => selectRow(r.c));
      }
    });

    const xaxis = svg.append("g");
    for (let R = rMin; R <= rMax; R++) {
      if (R === 1 || R % 5 === 0) {
        xaxis.append("text").attr("class", "tick-label")
          .attr("x", xOf(R) + CW / 2).attr("y", H - 14).attr("text-anchor", "middle")
          .text(R).style("cursor", "pointer").on("click", () => selectCol(R));
      }
    }
    const colHit = svg.append("g");
    for (let R = rMin; R <= rMax; R++) {
      colHit.append("rect").attr("x", xOf(R)).attr("y", H - 12)
        .attr("width", CW).attr("height", 12).attr("fill", "transparent")
        .style("cursor", "pointer").on("click", () => selectCol(R));
    }
    svg.append("text").attr("class", "axis-label")
      .attr("x", GUT + plotW / 2).attr("y", H).attr("text-anchor", "middle")
      .text("R  (cents above entry, T = c + R)");

    // legend
    const legY = H + 8, legW = 150, legH = 8, legX = GUT;
    const lg = svg.append("g").attr("class", "legend");
    const gradId = containerId + "-grad";
    const defs = svg.append("defs");
    const grad = defs.append("linearGradient").attr("id", gradId).attr("x1", "0%").attr("x2", "100%");
    const stops = 12;
    function legColAt(t) {
      if (kind === "hit") return hitColor(t * 100);
      if (lens === "ev") return evColor(-M.evAbsMax + t * 2 * M.evAbsMax);
      if (lens === "roi") return roiColor(-M.roiAbsMax + t * 2 * M.roiAbsMax);
      return achColor(-achScaleMax + t * 2 * achScaleMax);
    }
    for (let i = 0; i <= stops; i++) {
      grad.append("stop").attr("offset", (i / stops * 100) + "%").attr("stop-color", legColAt(i / stops));
    }
    const legRect = lg.append("rect").attr("x", legX).attr("y", legY)
      .attr("width", legW).attr("height", legH).attr("fill", `url(#${gradId})`)
      .attr("stroke", "var(--panel-border)");
    const legL = lg.append("text").attr("x", legX).attr("y", legY + legH + 9).attr("text-anchor", "start");
    const legM = lg.append("text").attr("x", legX + legW / 2).attr("y", legY + legH + 9).attr("text-anchor", "middle");
    const legR = lg.append("text").attr("x", legX + legW).attr("y", legY + legH + 9).attr("text-anchor", "end");
    function refreshLegend() {
      // rebuild gradient stops for current lens
      grad.selectAll("stop").remove();
      for (let i = 0; i <= stops; i++) grad.append("stop").attr("offset", (i / stops * 100) + "%").attr("stop-color", legColAt(i / stops));
      if (kind === "hit") { legL.text("0%"); legM.text(""); legR.text("100%"); }
      else if (lens === "ev") { legL.text((-M.evAbsMax).toFixed(1) + "c"); legM.text("0"); legR.text("+" + M.evAbsMax.toFixed(1) + "c"); }
      else if (lens === "roi") { legL.text((-M.roiAbsMax).toFixed(0) + "%"); legM.text("0"); legR.text("+" + M.roiAbsMax.toFixed(0) + "%"); }
      else { legL.text((-achScaleMax).toFixed(0) + "%"); legM.text("0"); legR.text("\u2265+" + achScaleMax.toFixed(0) + "%"); }
    }
    refreshLegend();

    return { svg, sel, hlRow, hlCol, ovFloor, ovCeil, ovBestX, dens, kind, refreshLegend };
  }

  const P_LEFT = buildPlot("plot-left", "left");
  const P_HIT = buildPlot("plot-hit", "hit");
  const plots = [P_LEFT, P_HIT];

  // ---- lens switch --------------------------------------------------------
  function applyLens() {
    P_LEFT.sel.attr("fill", d => leftColor(leftVal(d)));
    // Finest lens dims cells whose two layers disagree (thin/own-only) so a
    // borrowed positive never reads as a proven one; full opacity = confident
    // (own-N actual value AND eff-N pooled depth both positive at the same X).
    P_LEFT.sel.attr("fill-opacity", d => (lens === "fin" ? finOpacity(d.c) : 1));
    P_LEFT.refreshLegend();
    if (lens === "ev") {
      document.getElementById("left-title").textContent = "Pooled EV — avg cents earned per N";
      document.getElementById("left-sub").textContent = "at every (cell, R), neighbor-pooled · diverging RdYlGn @ 0";
    } else if (lens === "roi") {
      document.getElementById("left-title").textContent = "Pooled ROI — EV ÷ entry cost";
      document.getElementById("left-sub").textContent = "cheap & expensive cents on one scale · diverging RdYlGn @ 0";
    } else if (lens === "fin") {
      document.getElementById("left-title").textContent = "Finest config — dual-layer (own-N value × eff-N depth)";
      document.getElementById("left-sub").textContent = "hue = stability-scored eff-N ROI (the deep, drift-unbiased estimator leads) · FULL = own-N tape also agrees · slight DIM = tape-watch (thin own tape lags, likely T-20 drift bias) · blank = no positive config";
    } else {
      document.getElementById("left-title").textContent = "Achievable ROI — pooled best-X exit-or-hold (per cent)";
      document.getElementById("left-sub").textContent = "each row colored by its neighbor-pooled best-X ROI · best-X tick marks the R · CV-selected σ, own-N fallback · descriptive";
    }
  }
  document.querySelectorAll('input[name=lens]').forEach(r => {
    r.addEventListener("change", e => { lens = e.target.value; applyLens(); });
  });

  // ---- tooltip ------------------------------------------------------------
  const tip = document.getElementById("tip");
  function showTip(event, d) {
    const r = rowByC.get(d.c);
    const T = d.c + d.R;
    const evCls = d.ev == null ? "" : (d.ev >= 0 ? "tip-ev-pos" : "tip-ev-neg");
    const roiCls = d.roi == null ? "" : (d.roi >= 0 ? "tip-ev-pos" : "tip-ev-neg");
    let nbrHtml = "";
    if (r && r.neighbors && r.neighbors.length) {
      const top = r.neighbors.slice().sort((a,b)=>b.pct-a.pct).slice(0, 6);
      nbrHtml = top.map(n =>
        `<span class="tip-nbr">${n.c}c: ${n.pct.toFixed(0)}% (N=${n.ownN})</span>`
      ).join("&nbsp; ");
    }
    const comp = (r && r.complementC != null) ? (r.complementC + "c") : "—";
    const dol = dollarsOf(d.ev, d.c);
    const dolCls = d.ev == null ? "" : (d.ev >= 0 ? "tip-ev-pos" : "tip-ev-neg");
    const a = achByC(d.c);
    const aL = achLockedByC(d.c);
    let achHtml = "";
    if (a) {
      const aCls = a.roi == null ? "" : (a.roi >= 0 ? "tip-ev-pos" : "tip-ev-neg");
      const isBest = (d.R === a.bestX);
      const basisTxt = a.basis === "own-N"
        ? `own-N only (neighbors contaminated; \u03c3=0)`
        : `pooled \u03c3=${a.sigma!=null?a.sigma:"?"} (neighbor-weighted)`;
      achHtml =
        `<div class="tip-rule"></div>` +
        `<span class="tip-dim">POOLED best-X (${basisTxt}):</span><br>` +
        `exit +${a.bestX}c (T=${a.bestT}c) &nbsp; ROI <span class="${aCls}">${fmtRoi(a.roi)}</span> &nbsp; ` +
        (a.hit!=null ? `hit ${fmtHit(a.hit)}%` : `hold-to-settle`) +
        (isBest ? ` &nbsp;<b style="color:#00c2ff">\u25c0 this R</b>` : "") + `<br>` +
        `<span class="tip-dim">rule:</span> ${a.rule}`;
      if (aL) {
        const lCls = aL.roi == null ? "" : (aL.roi >= 0 ? "tip-ev-pos" : "tip-ev-neg");
        achHtml +=
          `<br><span class="tip-dim">locked own-N ref (N=${aL.N}):</span> ` +
          `+${aL.bestX}c \u2192 <span class="${lCls}">${fmtRoi(aL.roi)}</span>`;
      }
    }
    tip.innerHTML =
      `<b>c=${d.c}c</b> &middot; R=+${d.R} &rarr; T=${T}c<br>` +
      `<span class="tip-dim">pooled @ this R:</span> EV <span class="${evCls}">${fmtEv(d.ev)}c</span> &nbsp; ` +
      `ROI <span class="${roiCls}">${fmtRoi(d.roi)}</span> &nbsp; ` +
      `hit ${fmtHit(d.hit)}%<br>` +
      `<span class="tip-dim">if deployed on this cent's ${effNofC(d.c).toFixed(0)} eff-N (its price range) @10ct:</span> <span class="${dolCls}">${fmtDol(dol)}</span>` +
      achHtml +
      `<div class="tip-rule"></div>` +
      `<span class="tip-dim">borrows from (own N=${r ? r.ownN : "—"}, eff N=${r && r.effN!=null ? r.effN.toFixed(0) : "—"}):</span><br>` +
      `${nbrHtml}` +
      `<div class="tip-rule"></div>` +
      `<span class="tip-dim">two-sided-G complement:</span> ${comp}`;
    tip.style.opacity = 1;
    const pad = 14;
    let x = event.clientX + pad, y = event.clientY + pad;
    const bb = tip.getBoundingClientRect();
    if (x + bb.width > window.innerWidth) x = event.clientX - bb.width - pad;
    if (y + bb.height > window.innerHeight) y = event.clientY - bb.height - pad;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  function hideTip() { tip.style.opacity = 0; }

  // ---- highlight ----------------------------------------------------------
  function clearHL() { plots.forEach(p => { p.hlRow.style("display", "none"); p.hlCol.style("display", "none"); }); }
  function highlightRow(c) {
    clearHL();
    plots.forEach(p => p.hlRow.attr("x", GUT).attr("y", yOf(c) - 0.5)
      .attr("width", plotW).attr("height", CH + 1).style("display", null));
  }
  function highlightCol(R) {
    clearHL();
    plots.forEach(p => p.hlCol.attr("x", xOf(R) - 0.5).attr("y", TOP)
      .attr("width", CW + 1).attr("height", plotH).style("display", null));
  }

  // ---- side panel ---------------------------------------------------------
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
        if (col.key === "roi") td.attr("class", d.roi == null ? "" : (d.roi >= 0 ? "pos" : "neg"));
        if (col.key === "dollars") td.attr("class", d.dollars == null ? "" : (d.dollars >= 0 ? "pos" : "neg"));
      });
    });
  }

  const COL_R   = { key: "R", label: "R", fmt: v => "+" + v };
  const COL_T   = { key: "T", label: "T", fmt: v => v + "c" };
  const COL_C   = { key: "c", label: "c", fmt: v => v + "c" };
  const COL_HIT = { key: "hit", label: "hit%", fmt: v => fmtHit(v) };
  const COL_EV  = { key: "ev", label: "EV/N", fmt: v => fmtEv(v) };
  const COL_ROI = { key: "roi", label: "ROI", fmt: v => fmtRoi(v) };
  const COL_DOL = { key: "dollars", label: "$@10ct", fmt: v => fmtDol(v) };

  function selectRow(c) {
    highlightRow(c);
    const r = rowByC.get(c);
    const data = cells.filter(d => d.c === c).map(d => ({ R: d.R, T: d.c + d.R, hit: d.hit, ev: d.ev, roi: d.roi, dollars: dollarsOf(d.ev, d.c) }));
    sortState = { key: "R", asc: true };
    const effTxt = r && r.effN != null ? r.effN.toFixed(0) : "—";
    const a = achByC(c);
    const aL = achLockedByC(c);
    const basisTxt = a ? (a.basis === "own-N" ? "own-N only (σ=0, neighbors contaminated)" : `pooled σ=${a.sigma}`) : "";
    const achLine = a
      ? ` POOLED best-X (${basisTxt}): exit +${a.bestX}c (T=${a.bestT}c) → ROI ${fmtRoi(a.roi)}${a.hit!=null?", hit "+fmtHit(a.hit)+"%":" (hold-to-settle)"}. Rule: ${a.rule}.` +
        (aL ? ` Locked own-N ref: +${aL.bestX}c → ${fmtRoi(aL.roi)} [N=${aL.N}].` : "") +
        ` Hindsight-optimal / descriptive — not predictive.`
      : "";
    // dual-layer finest config: own-N actual value AND eff-N pooled depth
    const f = finByC(c);
    const finLine = f
      ? ` ★ FINEST CONFIG: exit +${f.bestX}c (T=${f.bestT}c) — ${f.confidence.toUpperCase()}.` +
        ` Layer A own-N (actual value, N=${f.ownN}): ROI ${fmtRoi(f.ownRoi)}, hit ${fmtHit(f.ownHit)}%.` +
        ` Layer B eff-N (pooled depth, σ=${f.sigma.toFixed(1)}): ROI ${fmtRoi(f.effRoi)}, hit ${fmtHit(f.effHit)}%, Sharpe ${f.effSharpe.toFixed(2)}.` +
        ` ${f.confidence === "confident" ? "Eff-N (deep, drift-unbiased) leads positive AND the own tape agrees — proven & deep." : "Eff-N (deep, drift-unbiased) leads positive; the thin own tape lags — likely T-20 snapshot drift bias (the cells that read this cent late skew toward just-weakened). Eff-N is the truer estimator, so this is a watch-note, not a downgrade."}`
      : ` ★ FINEST CONFIG: none — no exit clears positive EV on the converted basis (honestly blank, not least-bad).`;
    renderTable(
      `Cell c=${c}c  ·  ownN=${r ? r.ownN : "—"}  effN=${effTxt}`,
      `Every conceivable R for this entry cent (pooled). Breakeven R≥${r ? r.breakevenFloorR : "—"}, ceiling R≤${r ? r.ceilingMaxR : "—"}. Complement ${r && r.complementC!=null ? r.complementC+"c" : "—"}. $ = EV × this cent's ${effTxt} eff-N @10ct (its own price range, NOT the full corpus).` + finLine + achLine,
      [COL_R, COL_T, COL_HIT, COL_EV, COL_ROI, COL_DOL], data
    );
  }
  function selectCol(R) {
    highlightCol(R);
    const data = cells.filter(d => d.R === R).map(d => ({ c: d.c, T: d.c + d.R, hit: d.hit, ev: d.ev, roi: d.roi, dollars: dollarsOf(d.ev, d.c) }));
    sortState = { key: "c", asc: true };
    renderTable(
      `Fixed R = +${R}  ·  cross-cent spectrum`,
      `How the same +${R}c offset performs across every entry cent (pooled). $ = EV × each cent's own eff-N @10ct (its price range, NOT the full corpus).`,
      [COL_C, COL_T, COL_HIT, COL_EV, COL_ROI, COL_DOL], data
    );
  }
  window.__selectRow = selectRow; window.__selectCol = selectCol;

  // ---- toggles ------------------------------------------------------------
  document.getElementById("tg-floor").addEventListener("change", e => {
    plots.forEach(p => p.ovFloor.style("display", e.target.checked ? null : "none"));
  });
  document.getElementById("tg-ceil").addEventListener("change", e => {
    plots.forEach(p => p.ovCeil.style("display", e.target.checked ? null : "none"));
  });
  document.getElementById("tg-bestx").addEventListener("change", e => {
    plots.forEach(p => p.ovBestX.style("display", e.target.checked ? null : "none"));
  });
  document.getElementById("tg-density").addEventListener("change", e => {
    plots.forEach(p => p.dens.style("display", e.target.checked ? null : "none"));
  });

  applyLens();
  selectRow(38);
})();
</script>
</body>
</html>
"""


def main() -> None:
    payload = json.loads(SURFACE_JSON.read_text(encoding="utf-8"))
    data_json = json.dumps(payload, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("{DATA_JSON}", data_json)
    OUT_HTML.write_text(html, encoding="utf-8")
    m = payload["meta"]
    print(f"wrote {OUT_HTML}")
    print(f"  valid cells : {m['validCells']}")
    print(f"  c range     : {m['cMin']}..{m['cMax']}  R max: {m['rMax']}")
    print(f"  EV range    : {m['evMin']:.3f}..{m['evMax']:.3f}")
    print(f"  ROI range   : {m['roiMin']:.1f}..{m['roiMax']:.1f}%")
    print(f"  size        : {OUT_HTML.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
