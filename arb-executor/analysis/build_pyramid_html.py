#!/usr/bin/env python3
"""
Interactive PYRAMID visualizer (HTML/D3) fed by the CORRECTED ground-truth
surface ({cat}_corrected_surface_v3.json). Layout:

  - X axis: each cent is its own vertical column (underdogs 5-49, favorites 50-94),
    laid out left->right across the full price range.
  - Y axis: EVERY individual exit offset gets its own labeled cell row, +1 at the
    bottom climbing to that cent's 99c ceiling at the top. Big, scrollable.
  - Cell color: lens (ROI% default / EV / hit%), RdYlGn @ 0.
  - White ring: the chosen achievable best-X for that cent.
  - Hover: full per-cell readout + achievable rule + neighbor borrows (same
    provenance as the ground-truth heatmap).

Self-contained single file: {cat}_pyramid_v3.html
"""
import json, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent / "data" / "durable" / "exit_atlas_v1"
CAT = os.environ.get("CATEGORY", "atp_main").lower()
SURF = ATLAS / f"{CAT}_corrected_surface_v3.json"
OUT = ATLAS / f"{CAT}_pyramid_v3.html"

HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{CAT_LABEL} - Pyramid v3</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  :root{ --bg:#0e1116; --panel:#151a21; --border:#252c36; --ink:#e6edf3;
    --ink-soft:#8b98a5; --ink-faint:#5a6675; --ring:#ffffff;
    --pos:#46d17a; --neg:#e5484d; --mid:#caa83a;
    --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans)}
  header{position:sticky;top:0;z-index:30;background:linear-gradient(180deg,#0e1116 70%,rgba(14,17,22,0));
    padding:14px 18px 10px;border-bottom:1px solid var(--border)}
  h1{margin:0;font-size:18px;font-weight:800;letter-spacing:.2px}
  .sub{color:var(--ink-soft);font-size:12px;margin-top:3px;line-height:1.5}
  .controls{display:flex;gap:18px;align-items:center;margin-top:9px;flex-wrap:wrap}
  .controls label{font-size:12px;color:var(--ink-soft);cursor:pointer}
  .controls input{vertical-align:middle;margin-right:4px}
  .glabel{color:var(--ink);font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.6px;margin-right:4px}
  .legend{display:inline-flex;align-items:center;gap:7px;font-size:11px;color:var(--ink-soft)}
  .legbar{width:150px;height:11px;border-radius:3px;border:1px solid var(--border)}
  #scroll{overflow:auto;height:calc(100vh - 118px)}
  svg{display:block;font-family:var(--mono)}
  .cell{stroke:#0e1116;stroke-width:.4px}
  .cell:hover{stroke:#fff;stroke-width:1px}
  .yt{fill:var(--ink-faint);font-size:9px}
  .ytmaj{fill:var(--ink-soft);font-size:9.5px;font-weight:700}
  .clab{fill:var(--ink);font-size:11px;font-weight:800}
  .chit{font-size:10px;font-weight:800}
  .cev{fill:var(--ink-soft);font-size:9px}
  .bestlab{fill:#fff;font-size:9px;font-weight:800;pointer-events:none}
  .seclab{fill:#cfe6ff;font-size:9px;font-weight:700;pointer-events:none}
  .band{fill:var(--ink);font-size:13px;font-weight:800}
  .bandsub{fill:var(--ink-soft);font-size:11px;font-weight:500}
  #tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .08s;z-index:50;
    background:#0b0e13;border:1px solid #2b333d;border-radius:9px;padding:10px 12px;
    font-family:var(--mono);font-size:11.5px;line-height:1.55;max-width:330px;
    box-shadow:0 8px 30px rgba(0,0,0,.5)}
  .tdim{color:var(--ink-faint)} .tpos{color:var(--pos)} .tneg{color:var(--neg)}
  .trule{height:1px;background:#222a33;margin:6px 0}
  .tnbr{display:inline-block;color:#9fb3c8;background:#161c24;border-radius:4px;padding:1px 5px;margin:1px 2px;font-size:10.5px}
</style></head>
<body>
<header>
  <h1>{CAT_LABEL} &middot; PYRAMID &middot; every exit offset to the 99c ceiling</h1>
  <div class="sub">Ground truth = corpus-reconstructed own-cost-basis surface (matches the locked achievable best-X). Each cent is a column; each row is one exit offset +X. <b style="color:#fff">White ring</b> = EV-max achievable exit &nbsp;&middot;&nbsp; <b style="color:#ff9de8">magenta dash</b> = harmony exit (EV&times;reliability) &mdash; shown only where it disagrees with the ring (the lottery cells). Hover any cell for the full readout + neighbor borrows.</div>
  <div class="controls">
    <span class="glabel">Lens</span>
    <label><input type="radio" name="lens" value="best" checked> Best (EV &amp; hit harmonized)</label>
    <label><input type="radio" name="lens" value="roi"> ROI %</label>
    <label><input type="radio" name="lens" value="ev"> EV (cents)</label>
    <label><input type="radio" name="lens" value="hit"> Hit %</label>
    <span style="width:18px"></span>
    <span class="glabel">Shoulder</span>
    <label><input type="checkbox" id="shoulderTog"> show &ge;70%-of-peak shoulder tick</label>
    <span style="width:18px"></span>
    <span class="legend"><span id="legL">-60%</span><span class="legbar" id="legbar"></span><span id="legR">+60%</span></span>
  </div>
</header>
<div id="scroll"><svg id="svg"></svg></div>
<div id="tip"></div>
<script>
const DATA = {DATA_JSON};
const cells = DATA.cells;
const rows = DATA.rows;
const rowByC = new Map(rows.map(r=>[r.c,r]));
const achByC = c => { const r=rowByC.get(c); return r? r.achievable : null; };
const achLByC = c => { const r=rowByC.get(c); return r? r.achievableLocked : null; };
const effNByC = c => { const r=rowByC.get(c); return r&&r.effN!=null? r.effN : null; };

// group cells by cent
const byC = d3.group(cells, d=>d.c);
const allC = Array.from(byC.keys()).sort((a,b)=>a-b);
const MAXR = 94;                     // tallest possible offset (5c -> +94)

// ---- geometry: big cells, scrollable ----
const CW = 26;                       // column width per cent
const CH = 15;                       // height per offset cell (each row labeled)
const GUT_L = 56;                    // left gutter (y labels)
const TOP = 18;                      // top pad inside a band
const LAB_H = 64;                    // space under each pyramid for cent labels
const BAND_GAP = 46;                 // gap/title between underdog & favorite bands

const UNDER = allC.filter(c=>c<50);
const FAV   = allC.filter(c=>c>=50);

const plotH = TOP + MAXR*CH;         // full height of one band's grid
const bandW = GUT_L + Math.max(UNDER.length, FAV.length)*CW + 30;

const totalW = bandW + 20;
const totalH = 16 + (plotH+LAB_H) + BAND_GAP + 24 + (plotH+LAB_H) + 40;

const svg = d3.select("#svg").attr("width", totalW).attr("height", totalH);

// ---- color scales ----
const roiColor = d3.scaleLinear().domain([-60,-20,0,30,80])
  .range(["#a01722","#e5484d","#1a1f26","#2a6e3f","#46d17a"]).clamp(true);
const evColor = d3.scaleLinear().domain([-12,-4,0,5,14])
  .range(["#a01722","#e5484d","#1a1f26","#2a6e3f","#46d17a"]).clamp(true);
const hitColor = d3.scaleSequential(d3.interpolateViridis).domain([0,100]);
// HARMONY score: reward EV but penalize unreliability. A profitable AND likely
// exit scores highest; a high-EV lottery (low hit) is dimmed; a negative-EV
// exit goes red regardless of hit. score = ev * hit_weight, hit_weight in
// [0.35..1] so a 100% exit keeps full EV and a 20% lottery keeps ~half.
function harmonyScore(d){ const w=0.35+0.65*(d.hit/100); return d.ev*w; }
const bestColor = d3.scaleLinear().domain([-10,-3,0,4,11])
  .range(["#a01722","#e5484d","#1a1f26","#2a6e3f","#46d17a"]).clamp(true);
let lens="best";
function valOf(d){ return lens==="roi"? d.roi : lens==="ev"? d.ev : lens==="hit"? d.hit : harmonyScore(d); }
function colOf(d){ return lens==="roi"? roiColor(d.roi) : lens==="ev"? evColor(d.ev) : lens==="hit"? hitColor(d.hit) : bestColor(harmonyScore(d)); }

// the harmonized 'best' exit per cent: the offset maximizing harmonyScore
function harmonyR(c){ const arr=byC.get(c); if(!arr) return null;
  let best=null,bv=-1e9; arr.forEach(d=>{ const s=harmonyScore(d); if(s>bv){bv=s;best=d.R;} }); return best; }

function hitTier(h){ return h>=70?"#46d17a":h>=45?"#e3c04a":"#e5484d"; }

// shoulder: lowest R keeping >=70% of peak (positive) lens-peak EV
function shoulderR(c){
  const arr=byC.get(c); if(!arr) return null;
  let peak=-1e9; arr.forEach(d=>{ if(d.ev>peak) peak=d.ev; });
  if(peak<=0) return null;
  let best=null; arr.forEach(d=>{ if(d.ev>=0.7*peak){ if(best===null||d.R<best) best=d.R; } });
  return best;
}

let showShoulder=false;

function drawBand(g, cents, originY){
  const xOf = i => GUT_L + i*CW;
  // y labels: EVERY offset gets a tick; bold every 5th
  const yTopOf = R => originY + TOP + (MAXR - R)*CH;   // R=MAXR at top, R=1 at bottom
  for(let R=1; R<=MAXR; R++){
    const major = (R%5===0)||R===1;
    g.append("text").attr("class", major?"ytmaj":"yt")
      .attr("x", GUT_L-6).attr("y", yTopOf(R)+CH-3).attr("text-anchor","end")
      .text("+"+R);
  }
  // cells
  cents.forEach((c,i)=>{
    const arr=byC.get(c)||[];
    const a=achByC(c);
    const sh=showShoulder?shoulderR(c):null;
    arr.forEach(d=>{
      g.append("rect").datum(d).attr("class","cell")
        .attr("x", xOf(i)).attr("y", yTopOf(d.R))
        .attr("width", CW-1).attr("height", CH-1)
        .attr("fill", colOf(d))
        .on("mousemove", (ev,dd)=>showTip(ev,dd))
        .on("mouseleave", hideTip);
    });
    // best-X ring
    if(a && a.bestX!=null){
      g.append("rect").attr("x", xOf(i)-1).attr("y", yTopOf(a.bestX)-1)
        .attr("width", CW+1).attr("height", CH+1).attr("fill","none")
        .attr("stroke","#fff").attr("stroke-width",2).attr("pointer-events","none");
      g.append("text").attr("class","bestlab").attr("x", xOf(i)+CW/2)
        .attr("y", yTopOf(a.bestX)+CH-4).attr("text-anchor","middle").text("+"+a.bestX);
    }
    // shoulder tick (dashed cyan) — optional
    if(sh!=null && (!a||sh!==a.bestX)){
      g.append("rect").attr("x", xOf(i)-1).attr("y", yTopOf(sh)-1)
        .attr("width", CW+1).attr("height", CH+1).attr("fill","none")
        .attr("stroke","#39c2ff").attr("stroke-width",1.4)
        .attr("stroke-dasharray","3,2").attr("pointer-events","none");
    }
    // HARMONY exit (magenta dashed) — only shown when it disagrees with the
    // EV-max ring, i.e. the lottery cells where 'best' is ambiguous.
    const hR=harmonyR(c);
    if(lens==="best" && hR!=null && a && hR!==a.bestX){
      g.append("rect").attr("x", xOf(i)-1).attr("y", yTopOf(hR)-1)
        .attr("width", CW+1).attr("height", CH+1).attr("fill","none")
        .attr("stroke","#ff5dd2").attr("stroke-width",1.8)
        .attr("stroke-dasharray","4,2").attr("pointer-events","none");
      g.append("text").attr("class","seclab").attr("fill","#ffb3ec")
        .attr("x", xOf(i)+CW/2).attr("y", yTopOf(hR)+CH-4)
        .attr("text-anchor","middle").text("+"+hR);
    }
    // cent label block under the pyramid
    const ah=a&&a.hit!=null?a.hit:0;
    const ly=originY+TOP+MAXR*CH+14;
    g.append("text").attr("class","clab").attr("x",xOf(i)+CW/2).attr("y",ly)
      .attr("text-anchor","middle").text(c+"c");
    g.append("text").attr("class","chit").attr("x",xOf(i)+CW/2).attr("y",ly+15)
      .attr("text-anchor","middle").attr("fill",hitTier(ah)).text(Math.round(ah)+"%");
    g.append("text").attr("class","cev").attr("x",xOf(i)+CW/2).attr("y",ly+29)
      .attr("text-anchor","middle").text(a?(a.ev>=0?"+":"")+a.ev.toFixed(1)+"c":"-");
  });
}

const gU = svg.append("g");
const gF = svg.append("g");
let yU = 36, yF;

svg.append("text").attr("class","band").attr("x",18).attr("y",yU-6)
  .text("UNDERDOGS  5-49c");
svg.append("text").attr("class","bandsub").attr("x",178).attr("y",yU-6)
  .text("-  the engine: deep bounces, low hit");

function layout(){
  yF = yU + plotH + LAB_H + BAND_GAP;
}
layout();
svg.append("text").attr("class","band").attr("x",18).attr("y",yF-6)
  .text("FAVORITES  50-94c");
svg.append("text").attr("class","bandsub").attr("x",168).attr("y",yF-6)
  .text("-  the ballast: shallow exits, high hit");

function redraw(){
  gU.selectAll("*").remove(); gF.selectAll("*").remove();
  drawBand(gU, UNDER, yU);
  drawBand(gF, FAV, yF);
}
redraw();

// ---- lens & legend ----
function setLegend(){
  let stops, l, r;
  if(lens==="best"){ stops=[[0,"#a01722"],[.3,"#e5484d"],[.48,"#1a1f26"],[.66,"#2a6e3f"],[1,"#46d17a"]]; l="weak"; r="strong"; }
  else if(lens==="roi"){ stops=[[0,"#a01722"],[.33,"#e5484d"],[.5,"#1a1f26"],[.7,"#2a6e3f"],[1,"#46d17a"]]; l="-60%"; r="+80%"; }
  else if(lens==="ev"){ stops=[[0,"#a01722"],[.3,"#e5484d"],[.46,"#1a1f26"],[.66,"#2a6e3f"],[1,"#46d17a"]]; l="-12c"; r="+14c"; }
  else { stops=[[0,d3.interpolateViridis(0)],[.5,d3.interpolateViridis(.5)],[1,d3.interpolateViridis(1)]]; l="0%"; r="100%"; }
  const grad="linear-gradient(90deg,"+stops.map(s=>s[1]+" "+(s[0]*100)+"%").join(",")+")";
  document.getElementById("legbar").style.background=grad;
  document.getElementById("legL").textContent=l;
  document.getElementById("legR").textContent=r;
}
setLegend();
document.querySelectorAll('input[name=lens]').forEach(rb=>{
  rb.addEventListener("change",e=>{ lens=e.target.value; setLegend(); redraw(); });
});
document.getElementById("shoulderTog").addEventListener("change",e=>{
  showShoulder=e.target.checked; redraw();
});

// ---- tooltip ----
const tip=document.getElementById("tip");
const fmtEv=v=>v==null?"-":(v>=0?"+":"")+v.toFixed(2);
const fmtRoi=v=>v==null?"-":(v>=0?"+":"")+v.toFixed(0)+"%";
const fmtHit=v=>v==null?"-":v.toFixed(0);
const dollarsOf=(ev,c)=> ev==null?null: ev*10/100*10; // 10 contracts, ev in cents
function showTip(event,d){
  const r=rowByC.get(d.c), a=achByC(d.c), aL=achLByC(d.c);
  const T=d.c+d.R;
  const evCls=d.ev>=0?"tpos":"tneg", roiCls=d.roi>=0?"tpos":"tneg";
  let nbr="";
  if(r&&r.neighbors&&r.neighbors.length){
    nbr=r.neighbors.slice().sort((x,y)=>y.pct-x.pct).slice(0,6)
      .map(n=>`<span class="tnbr">${n.c}c: ${n.pct.toFixed(0)}% (N=${n.ownN})</span>`).join(" ");
  }
  let aH="";
  if(a){
    const aCls=a.roi>=0?"tpos":"tneg";
    const isBest=(d.R===a.bestX);
    const basis=a.basis==="own-N"?"own-N (credible own tape)":"pooled (leaned on neighbor cluster)";
    aH=`<div class="trule"></div><span class="tdim">achievable best-X (${basis}):</span><br>`+
       `exit +${a.bestX}c (T=${a.bestT}c) &nbsp; ROI <span class="${aCls}">${fmtRoi(a.roi*100<=200?a.roi*100<=2?a.roi*100:a.roi:a.roi)}</span> &nbsp;`+
       (a.hit!=null?`hit ${fmtHit(a.hit*100<=100?a.hit*100<=1?a.hit*100:a.hit:a.hit)}%`:"hold")+
       (isBest?` &nbsp;<b style="color:#39c2ff">&#9664; this row</b>`:"")+`<br>`+
       `<span class="tdim">rule:</span> ${a.rule||("exit at +"+a.bestX+"c")}`;
    if(aL){ const lc=aL.roi>=0?"tpos":"tneg";
      aH+=`<br><span class="tdim">locked own-N ref (N=${aL.N}):</span> +${aL.bestX}c &#8594; <span class="${lc}">${fmtRoi(aL.roi)}</span>`; }
  }
  const dol=dollarsOf(d.ev,d.c);
  tip.innerHTML=
    `<b>c=${d.c}c</b> &middot; exit +${d.R} &#8594; T=${T}c<br>`+
    `<span class="tdim">at this exit:</span> EV <span class="${evCls}">${fmtEv(d.ev)}c</span> &nbsp; `+
    `ROI <span class="${roiCls}">${fmtRoi(d.roi)}</span> &nbsp; hit ${fmtHit(d.hit)}%<br>`+
    `<span class="tdim">@10 contracts:</span> <span class="${evCls}">${dol>=0?"+":""}$${dol.toFixed(2)}</span> &nbsp; `+
    `<span class="tdim">N=${d.n!=null?d.n:(r?r.ownN:"-")}</span>`+
    aH+
    `<div class="trule"></div><span class="tdim">borrows from (own N=${r?r.ownN:"-"}, eff N=${r&&r.effN!=null?r.effN.toFixed(0):"-"}):</span><br>${nbr}`;
  tip.style.opacity=1;
  const pad=14; let x=event.clientX+pad,y=event.clientY+pad;
  const bb=tip.getBoundingClientRect();
  if(x+bb.width>window.innerWidth) x=event.clientX-bb.width-pad;
  if(y+bb.height>window.innerHeight) y=event.clientY-bb.height-pad;
  tip.style.left=x+"px"; tip.style.top=y+"px";
}
function hideTip(){ tip.style.opacity=0; }
</script></body></html>
"""

payload = json.loads(SURF.read_text())
cat_label = payload.get("meta", {}).get("category", CAT.upper())
out = (HTML
       .replace("{CAT_LABEL}", cat_label)
       .replace("{DATA_JSON}", json.dumps(payload, separators=(",", ":"))))
OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
