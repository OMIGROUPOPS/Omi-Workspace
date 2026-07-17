"""HTML/CSS/JS for the live /daysheet page.

Digit-grammar rewrite (Plex, 07-17). Replaces the mock-ported render
with the operator's locked digit-only column contract across all three
tabs: POSITIONS, ORDERS, CLOSED. No sentences, no italic hint prose,
no "join pending" placeholders, no "no bell yet" strings. Every unshipped
value is a muted `—` with a native title-attribute tooltip whose text
matches the wire-status map filed in the PR description. Icons only:
⏱ (held to sweep), ✕ (pulled), Σ (combined), ⚑ (walk-flagged), red
PAIR ✕ (empty player slot), muted — (unshipped/unsourced).

This is still a single self-contained stdlib page — no build step, no
external JS/CSS. It is embedded as a triple-quoted string in
fund_tracker.py and served byte for byte through the same token gate as
the rest of that server's HTML.
"""

PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>DAY SHEET — LIVE</title>
<style>
  :root{
    --bg:#000; --panel:#0a0a0a; --border:#1a1a2e;
    --orange:#ff8c00; --green:#00ff88; --red:#ff3333;
    --blue:#00bfff; --purple:#8b5cf6; --grey:#7a7a85; --dimgrey:#4a4a54;
    --white:#ffffff;
  }
  *{box-sizing:border-box;}
  html,body{
    margin:0; padding:0; background:var(--bg); color:var(--white);
    font-family:'SF Mono','Consolas','Menlo',monospace;
    max-width:100vw; overflow-x:hidden;
  }
  .app{ padding:14px 16px 40px; max-width:1400px; margin:0 auto; }

  .topbar{
    display:flex; align-items:center; gap:14px; padding:6px 4px 12px;
    font-size:10px; color:var(--grey);
  }
  .topbar .clock{
    color:var(--white); font-weight:700; font-size:12px; letter-spacing:0.03em;
  }
  .topbar .clock .tz{ color:var(--grey); font-weight:400; font-size:9px; margin-left:3px; }
  .topbar .age{ color:var(--grey); }
  .topbar .age b{ color:var(--orange); font-weight:700; }
  .topbar .sep{ color:var(--dimgrey); }
  .live-dot{
    display:inline-block; width:6px; height:6px; border-radius:50%;
    background:var(--red); margin-right:4px; box-shadow:0 0 4px var(--red);
    animation:pulse 1.4s infinite;
  }
  @keyframes pulse{ 0%,100%{opacity:1;} 50%{opacity:0.35;} }

  .tabs{ display:flex; gap:6px; margin-bottom:8px; border-bottom:1px solid var(--border); padding-bottom:10px; }
  .tab{
    font-size:10px; letter-spacing:0.12em; text-transform:uppercase;
    padding:6px 12px; border:1px solid var(--border); background:transparent;
    color:var(--grey); cursor:pointer; font-family:inherit; font-weight:700;
  }
  .tab.active{ color:var(--orange); border-color:rgba(255,140,0,0.5); background:rgba(255,140,0,0.1); }
  .tab .count{ color:inherit; opacity:0.7; margin-left:4px; }

  /* Slate dead-space strip: digit-only aggregate row per tab.
     "7 games · 2Σ · 3 (red) · 2 resting" — icons + digits, no words
     beyond the four unavoidable nouns. */
  .slate{
    display:flex; gap:14px; padding:6px 12px; margin-bottom:6px;
    font-size:9.5px; color:var(--grey); border:1px solid var(--border);
    background:#050505; letter-spacing:0.04em;
  }
  .slate b{ color:var(--white); font-weight:700; }
  .slate .sigma{ color:var(--green); font-weight:700; }
  .slate .red{ color:var(--red); font-weight:700; }
  .slate .sep{ color:var(--dimgrey); }

  /* Digit-only column contracts. One shared grid pattern per tab,
     used identically by the colhead and every legrow so cells line
     up character-for-character down the sheet. */
  .colhead{
    display:grid; font-size:8px; letter-spacing:0.1em; text-transform:uppercase;
    color:var(--grey); padding:6px 12px; font-weight:600;
    border:1px solid var(--border); background:#040404;
  }
  /* POSITIONS (filled): PLAYER · CT · FILLED · T−X · Δ VS W1 · MARK · UNRLZD · $COST */
  .colhead.positions-filled,
  .legrow.positions-filled{
    grid-template-columns: 130px 40px 60px 56px 62px 52px 66px 66px;
    column-gap:12px;
  }
  /* POSITIONS (resting) / ORDERS (both use the same shape):
     PLAYER · CT · BID · POSTED · T−X · BEST · GAP */
  .colhead.orders-shape,
  .legrow.orders-shape{
    grid-template-columns: 130px 40px 60px 82px 56px 60px 60px;
    column-gap:12px;
  }
  /* CLOSED (filled): PLAYER · CT · FILLED · T−X · Δ VS W1 · W1 CLOSE · CORRIDOR · EXIT · YIELD ($) · ROI */
  .colhead.closed-filled,
  .legrow.closed-filled{
    grid-template-columns: 130px 40px 60px 56px 62px 62px 66px 60px 72px 56px;
    column-gap:10px;
  }
  /* CLOSED (un-filled sibling row inside a graded box):
     — · CT · ⏱/✕ · T−X (BID) · W1 LOW · W1 CLOSE · BOUNCE · W2 HIGH */
  .colhead.closed-unfilled,
  .legrow.closed-unfilled{
    grid-template-columns: 130px 40px 68px 72px 60px 66px 60px 60px;
    column-gap:10px;
  }
  .colhead span, .legrow span{
    text-align:right; white-space:nowrap; overflow:hidden;
    text-overflow:ellipsis;
  }
  .colhead span.lbl-last, .legrow span.player{
    text-align:left;
  }

  .gamebox{
    border:1px solid var(--border); background:var(--panel);
    margin-bottom:8px; overflow:hidden;
  }
  .gamehead{
    display:flex; align-items:center; gap:8px; padding:6px 12px;
    font-size:10px; border-bottom:1px solid var(--border); background:#050505;
  }
  .gamehead .names{ color:var(--white); font-weight:700; }
  .gamehead .meta{ color:var(--grey); font-size:9px; }
  .gamehead .walkflag{ color:var(--orange); font-size:11px; cursor:help; }
  .gamehead .deeplink{ margin-left:0; }

  .headright{ margin-left:auto; display:flex; align-items:center; gap:8px; }
  .schedbell{ color:var(--grey); font-size:9px; display:flex; align-items:center; gap:5px; }
  .schedbell .official{ color:var(--blue); font-weight:700; }
  .schedbell .srcbadge{
    font-size:7.5px; border:1px solid var(--border); padding:0 3px;
    color:var(--grey); text-transform:uppercase;
  }
  .schedbell .srcbadge.live{ color:var(--blue); border-color:rgba(0,191,255,0.4); }

  .legrow{
    display:grid; align-items:center; padding:5px 12px; font-size:10.5px;
    border-top:1px solid rgba(26,26,46,0.5);
  }
  .legrow span.player{
    color:var(--orange); font-weight:700; font-size:11px;
  }
  .legrow .num{ color:var(--white); font-weight:600; }
  .legrow .green{ color:var(--green); font-weight:700; }
  .legrow .red{ color:var(--red); font-weight:700; }
  .legrow .blue{ color:var(--blue); font-weight:700; }
  .legrow .grey{ color:var(--grey); }

  /* Muted em-dash: the operator's single "not shipped / not sourced"
     glyph. Any tooltip lands on the em-dash itself via the native
     title attribute — no popover, no inline prose, no color noise. */
  .mdash{
    color:var(--dimgrey); cursor:help; text-decoration:none;
    border-bottom:1px dotted var(--dimgrey);
  }

  /* Red PAIR ✕ chip: renders in an OWN legrow that has only a single
     grid column, so it spans the row cleanly. */
  .pair-x-row{
    padding:8px 12px; border-top:1px solid rgba(26,26,46,0.5);
    text-align:left;
  }
  .pair-x-chip{
    display:inline-block; color:var(--red); font-weight:800;
    font-size:10.5px; letter-spacing:0.05em;
    border:1px solid rgba(255,51,51,0.5); padding:1px 6px;
    background:rgba(255,51,51,0.08); cursor:help;
  }

  /* Foot Σ bar: only rendered on both-filled cards. Rendered as a
     grid row so Σ cost / Σ payout / Σ yield / ROI line up under
     $COST / EXIT / YIELD / ROI. */
  .foot-sigma{
    display:grid; padding:6px 12px;
    border-top:1px solid rgba(255,140,0,0.35);
    background:#050505; font-size:10.5px;
    align-items:center;
  }
  .foot-sigma span{ text-align:right; white-space:nowrap; }
  .foot-sigma .lbl-sigma{
    text-align:left; color:var(--orange); font-weight:800;
    letter-spacing:0.06em;
  }
  .foot-sigma.positions{
    grid-template-columns: 130px 40px 60px 56px 62px 52px 66px 66px;
    column-gap:12px;
  }
  .foot-sigma.closed{
    grid-template-columns: 130px 40px 60px 56px 62px 62px 66px 60px 72px 56px;
    column-gap:10px;
  }

  .gradechip{
    font-size:10.5px; font-weight:800; padding:1px 6px; letter-spacing:0.05em;
    border:1px solid currentColor; white-space:nowrap; flex-shrink:0;
  }
  .grade-A{ color:var(--green); } .grade-B{ color:var(--blue); }
  .grade-C{ color:var(--orange); } .grade-D,.grade-F{ color:var(--red); }
  .grade-UNGRADED{ color:var(--dimgrey); }

  .deeplink{
    color:var(--orange); text-decoration:none; font-size:9px;
    border:1px solid rgba(255,140,0,0.35); padding:1px 6px;
  }
  .deeplink:hover{ background:rgba(255,140,0,0.1); }

  .empty{ font-size:10px; color:var(--dimgrey); text-align:center; padding:24px 0; }
  .tapeage-stale{ color:var(--red) !important; font-weight:700; animation:pulse 1s infinite; }

  /* Icon glyph normalisation — kept size-consistent across tabs so the
     ⏱ ✕ Σ ⚑ set never wobbles between rows. */
  .icon{ font-size:11px; display:inline-block; }
  .icon.grey{ color:var(--grey); }
</style>
</head>
<body>
<div class="app">

  <div class="topbar">
    <span class="clock" id="etclock">--:--:-- PM<span class="tz">ET</span></span>
    <span class="sep">|</span>
    <span class="age">last fill <b id="tapeage">—</b> ago</span>
    <span class="sep">|</span>
    <span class="age">recorder <b id="recage">—</b> <span id="recstate"></span></span>
  </div>

  <div class="tabs">
    <button class="tab active" data-tab="positions" onclick="switchTab('positions')">POSITIONS <span class="count" id="cnt-positions">(0)</span></button>
    <button class="tab" data-tab="orders" onclick="switchTab('orders')">ORDERS <span class="count" id="cnt-orders">(0)</span></button>
    <button class="tab" data-tab="closed" onclick="switchTab('closed')">CLOSED <span class="count" id="cnt-closed">(0)</span></button>
  </div>

  <div id="positions" class="tabpanel">
    <div class="slate" id="slate-positions"></div>
    <div id="positions-body"></div>
  </div>

  <div id="orders" class="tabpanel" style="display:none;">
    <div class="slate" id="slate-orders"></div>
    <div id="orders-body"></div>
  </div>

  <div id="closed" class="tabpanel" style="display:none;">
    <div class="slate" id="slate-closed"></div>
    <div id="closed-body"></div>
  </div>

</div>

<script>
  const TOK = new URLSearchParams(window.location.search).get('token') || '';
  function withTok(path){ return path + (path.includes('?') ? '&' : '?') + 'token=' + encodeURIComponent(TOK); }

  function tickClock(){
    const el = document.getElementById('etclock');
    if(!el) return;
    const now = new Date();
    const opts = { hour:'numeric', minute:'2-digit', second:'2-digit', hour12:true, timeZone:'America/New_York' };
    el.innerHTML = now.toLocaleTimeString('en-US', opts) + '<span class="tz">ET</span>';
  }
  tickClock();
  setInterval(tickClock, 1000);

  function switchTab(name){
    document.querySelectorAll('.tabpanel').forEach(p => p.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  }

  function esc(s){ return (s===null||s===undefined) ? '' : String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  // TOOLTIP MAP (single source of truth, wire-status column 3):
  //   POSTED_UNSHIPPED  — snap_orders does not persist order-creation time (schema gap, filed)
  //   TX_UNSHIPPED      — T−X requires PLACED-ET; unshipped (schema gap, filed)
  //   BEST_UNSHIPPED    — live best/gap for resting side not yet piped from CC
  //   GAP_UNSHIPPED     — live gap depends on BEST; unshipped
  //   W1_LOW_UNSHIPPED  — sibling tape quadruplet unshipped (CC-side)
  //   W1_CLOSE_UNSHIPPED
  //   BOUNCE_UNSHIPPED
  //   W2_HIGH_UNSHIPPED
  // Every unshipped cell renders as <span class="mdash" title="{tip}">—</span>.
  const TIP = {
    POSTED:  'PLACED-ET not shipped — snap_orders does not persist order-creation time (schema gap, filed)',
    TX:      'T−X not shipped — needs PLACED-ET (schema gap, filed)',
    BEST:    'live best not shipped from CC for resting side',
    GAP:     'live gap not shipped — depends on BEST',
    W1_LOW:  'W1 low not shipped — sibling tape quadruplet (CC-side)',
    W1_CLOSE:'W1 close not shipped — sibling tape quadruplet (CC-side)',
    BOUNCE:  'bounce not shipped — sibling tape quadruplet (CC-side)',
    W2_HIGH: 'W2 high not shipped — sibling tape quadruplet (CC-side)',
    HELD:    'held to the bell sweep — sibling bid, never traded',
    PULLED:  'pulled before sweep — sibling bid, cancelled',
    NEVER:   'never conceived — sibling was never bid'
  };
  function mdash(key){
    return '<span class="mdash" title="' + esc(TIP[key] || 'unshipped') + '">—</span>';
  }

  // Money formatting — every digit-cell prints through one of these so
  // punctuation (¢ vs $ vs %) is fully deterministic and never inline-prose.
  function cents(v){ return (v===null||v===undefined) ? mdash('NEVER') : v + '¢'; }
  function dollars(cents_v){
    return (cents_v===null||cents_v===undefined) ? '—' : '$' + (cents_v/100).toFixed(2);
  }
  function pct(x){ return (x===null||x===undefined) ? '—' : (x>=0?'+':'') + x.toFixed(1) + '%'; }
  function signedCents(v){
    if(v===null||v===undefined) return '—';
    return (v>0?'+':'') + v + '¢';
  }
  function txMin(sched_ep, ref_ep){
    if(!sched_ep || !ref_ep) return null;
    return Math.round((ref_ep - sched_ep) / 60);
  }
  function fmtTx(min){
    if(min===null||min===undefined) return null;
    return (min<0?'T−':'T+') + Math.abs(min) + 'm';
  }
  function fmtEtShort(label){
    // "9:01:12 AM ET" -> "9:01 AM" (digit-only compression for narrow cells)
    if(!label) return '—';
    const m = String(label).match(/^(\d{1,2}:\d{2})(?::\d{2})?\s*(AM|PM)/i);
    return m ? (m[1] + ' ' + m[2].toUpperCase()) : label;
  }

  // Anchors chip: sched · bell(source badge). Digit-only, kept identical
  // across tabs. Never proxies from snapshot ts.
  function anchorsChip(a){
    if(!a) return '';
    const sched = a.sched ? esc(a.sched) : '—';
    const fp = a.fp;
    let bell;
    if(fp && fp.observed){
      bell = '<b class="official">' + esc(fp.label) + '</b>' +
             '<span class="srcbadge live">LIVE</span>';
    } else if(fp){
      bell = '<span title="estimate ' + esc(fp.label) + '">est ' + esc(fp.label) + '</span>' +
             '<span class="srcbadge">EST</span>';
    } else {
      bell = '<span class="mdash" title="no bell source has fired for this event yet">—</span>';
    }
    return '<span class="schedbell"><span>SCHED ' + sched + '</span>' + bell + '</span>';
  }

  function gameHead(g, gradeHtml){
    const link = '<a class="deeplink" href="' + esc(g.deeplink) + '" target="_blank" onclick="event.stopPropagation()">↗ KALSHI</a>';
    const walk = g.walk
      ? '<span class="walkflag" title="' + esc((g.walk.charge || '') + ((g.walk.verdict) ? ' — ' + g.walk.verdict : '')) + '">⚑</span>'
      : '';
    return '<div class="gamehead">' +
      '<span class="names">' + esc(g.names) + '</span>' +
      '<span class="meta">' + esc(g.tournament || '') + '</span>' +
      anchorsChip(g.anchors) +
      walk +
      '<span class="headright">' + (gradeHtml || '') + link + '</span>' +
      '</div>';
  }

  // ── SLATE dead-space strip ───────────────────────────────────
  function renderSlate(slate){
    const p = slate.positions || {}; const o = slate.orders || {}; const c = slate.closed || {};
    document.getElementById('slate-positions').innerHTML =
      '<span><b>' + (p.games||0) + '</b> games</span>' +
      '<span class="sep">·</span>' +
      '<span class="sigma">' + (p.both_filled||0) + 'Σ</span>' +
      '<span class="sep">·</span>' +
      '<span class="red">' + (p.red_slot||0) + ' red</span>';
    document.getElementById('slate-orders').innerHTML =
      '<span><b>' + (o.games||0) + '</b> games</span>' +
      '<span class="sep">·</span>' +
      '<span class="red">' + (o.red_slot||0) + ' red</span>';
    document.getElementById('slate-closed').innerHTML =
      '<span><b>' + (c.games||0) + '</b> games</span>' +
      '<span class="sep">·</span>' +
      '<span class="sigma">' + (c.both_filled||0) + 'Σ</span>' +
      '<span class="sep">·</span>' +
      '<span class="red">' + (c.red_slot||0) + ' red</span>' +
      '<span class="sep">·</span>' +
      '<span class="grey">' + (c.resting||0) + ' resting</span>';
  }
  async function loadSlate(){
    try{
      const r = await fetch(withTok('/api/slate.json'));
      renderSlate(await r.json());
    }catch(e){
      renderSlate({positions:{},orders:{},closed:{}});
    }
  }

  // ── POSITIONS ─────────────────────────────────────────────────
  const POS_HEAD_FILLED =
    '<div class="colhead positions-filled">' +
    '<span class="lbl-last">PLAYER</span>' +
    '<span>CT</span><span>FILLED</span><span>T−X</span>' +
    '<span>Δ VS W1</span><span>MARK</span><span>UNRLZD</span><span>$COST</span>' +
    '</div>';
  const POS_HEAD_RESTING =
    '<div class="colhead orders-shape">' +
    '<span class="lbl-last">PLAYER</span>' +
    '<span>CT</span><span>BID</span><span>POSTED</span>' +
    '<span>T−X</span><span>BEST</span><span>GAP</span>' +
    '</div>';

  function posFilledRow(l, sched_ep){
    const tx = fmtTx(txMin(sched_ep, l.fill_ep));
    const dW1 = (l.win && l.win.w1) ? (l.fill_price_c - l.win.w1.close) : null;
    const cost = (l.fill_price_c || l.basis_c) * l.qty;
    const unrlzd = (l.mark_c !== undefined && l.fill_price_c !== undefined)
      ? (l.mark_c - l.fill_price_c) * l.qty : null;
    const deltaCls = dW1 === null ? '' : (dW1 <= 0 ? 'green' : 'red');
    const unrlCls = unrlzd === null ? '' : (unrlzd >= 0 ? 'green' : 'red');
    return '<div class="legrow positions-filled">' +
      '<span class="player">' + esc(l.last_name) + '</span>' +
      '<span class="num">' + esc(l.qty) + '</span>' +
      '<span class="num">' + cents(l.fill_price_c) + '</span>' +
      '<span class="grey">' + (tx || mdash('TX')) + '</span>' +
      '<span class="' + deltaCls + '">' + (dW1===null ? mdash('W1_CLOSE') : signedCents(dW1)) + '</span>' +
      '<span class="num">' + cents(l.mark_c) + '</span>' +
      '<span class="' + unrlCls + '">' + (unrlzd===null ? '—' : (unrlzd>=0?'+':'') + '$' + (Math.abs(unrlzd)/100).toFixed(2)) + '</span>' +
      '<span class="num">' + dollars(cost) + '</span>' +
      '</div>';
  }
  function posRestingRow(l){
    // Resting-only leg: BID present, everything schema-gapped is muted.
    const bid = l.exit_resting ? l.exit_resting.price_c : (l.aim_c || null);
    return '<div class="legrow orders-shape">' +
      '<span class="player">' + esc(l.last_name) + '</span>' +
      '<span class="num">' + esc(l.qty) + '</span>' +
      '<span class="num">' + cents(bid) + '</span>' +
      '<span>' + mdash('POSTED') + '</span>' +
      '<span>' + mdash('TX') + '</span>' +
      '<span>' + mdash('BEST') + '</span>' +
      '<span>' + mdash('GAP') + '</span>' +
      '</div>';
  }
  function pairXRow(kind){
    // kind is a TIP key: NEVER / HELD / PULLED
    return '<div class="pair-x-row">' +
      '<span class="pair-x-chip" title="' + esc(TIP[kind]) + '">PAIR ✕</span>' +
      '</div>';
  }

  async function loadPositions(){
    const body = document.getElementById('positions-body');
    let games = [];
    try{
      const r = await fetch(withTok('/api/positions.json'));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-positions').textContent = '(' + games.length + ')';
    if(!games.length){
      body.innerHTML = POS_HEAD_FILLED + '<div class="empty">no open positions right now</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const sched_ep = (g.anchors && g.anchors.sched_ep) || null;
      const filledLegs = (g.legs || []).filter(l => (l.qty || 0) > 0 && l.fill_price_c !== undefined && l.fill_price_c !== null);
      const bothFilled = filledLegs.length >= 2;
      const hasMissing = !!g.gray_line || filledLegs.length < 2;

      let head = '';
      let rows = '';
      if(bothFilled){
        head = POS_HEAD_FILLED;
        rows = filledLegs.map(l => posFilledRow(l, sched_ep)).join('');
      } else if(filledLegs.length === 1){
        // one filled + one missing sibling -> red PAIR ✕ chip below
        head = POS_HEAD_FILLED;
        rows = posFilledRow(filledLegs[0], sched_ep) + pairXRow('NEVER');
      } else {
        head = POS_HEAD_RESTING;
        rows = (g.legs || []).map(posRestingRow).join('');
      }

      let foot = '';
      if(bothFilled){
        const cost = filledLegs.reduce((s,l)=>s + (l.fill_price_c || l.basis_c) * l.qty, 0);
        const unrlzd = filledLegs.reduce((s,l)=>s + ((l.mark_c||0) - (l.fill_price_c||0)) * l.qty, 0);
        const mark = filledLegs.reduce((s,l)=>s + (l.mark_c||0) * l.qty, 0);
        const unrlCls = unrlzd >= 0 ? 'green' : 'red';
        foot = '<div class="foot-sigma positions">' +
          '<span class="lbl-sigma">Σ</span>' +
          '<span></span><span></span><span></span><span></span>' +
          '<span></span>' +
          '<span class="' + unrlCls + '">' + (unrlzd>=0?'+':'') + '$' + (Math.abs(unrlzd)/100).toFixed(2) + '</span>' +
          '<span class="num">' + dollars(cost) + '</span>' +
          '</div>';
      }
      return '<div class="gamebox">' + gameHead(g) + head + rows + foot + '</div>';
    }).join('');
  }

  // ── ORDERS ────────────────────────────────────────────────────
  const ORD_HEAD =
    '<div class="colhead orders-shape">' +
    '<span class="lbl-last">PLAYER</span>' +
    '<span>CT</span><span>BID</span><span>POSTED</span>' +
    '<span>T−X</span><span>BEST</span><span>GAP</span>' +
    '</div>';

  function ordRow(l){
    return '<div class="legrow orders-shape">' +
      '<span class="player">' + esc(l.last_name) + '</span>' +
      '<span class="num">' + esc(l.qty) + '</span>' +
      '<span class="num">' + cents(l.aim_c) + '</span>' +
      '<span>' + mdash('POSTED') + '</span>' +
      '<span>' + mdash('TX') + '</span>' +
      '<span>' + mdash('BEST') + '</span>' +
      '<span>' + mdash('GAP') + '</span>' +
      '</div>';
  }
  async function loadOrders(){
    const body = document.getElementById('orders-body');
    let games = [];
    try{
      const r = await fetch(withTok('/api/orders.json'));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-orders').textContent = '(' + games.reduce((a,g)=>a+(g.legs||[]).length,0) + ')';
    if(!games.length){
      body.innerHTML = ORD_HEAD + '<div class="empty">no resting orders</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const legs = (g.legs || []).map(ordRow).join('');
      const half = ((g.legs || []).length < 2) ? pairXRow('NEVER') : '';
      return '<div class="gamebox">' + gameHead(g) + ORD_HEAD + legs + half + '</div>';
    }).join('');
  }

  // ── CLOSED ────────────────────────────────────────────────────
  const CLS_HEAD_FILLED =
    '<div class="colhead closed-filled">' +
    '<span class="lbl-last">PLAYER</span>' +
    '<span>CT</span><span>FILLED</span><span>T−X</span>' +
    '<span>Δ VS W1</span><span>W1 CLOSE</span><span>CORRIDOR</span>' +
    '<span>EXIT</span><span>YIELD ($)</span><span>ROI</span>' +
    '</div>';
  const CLS_HEAD_UNFILLED =
    '<div class="colhead closed-unfilled">' +
    '<span class="lbl-last">SIBLING</span>' +
    '<span>CT</span><span>ICON</span><span>T−X (BID)</span>' +
    '<span>W1 LOW</span><span>W1 CLOSE</span>' +
    '<span>BOUNCE</span><span>W2 HIGH</span>' +
    '</div>';

  function gradeChip(status, grade){
    if(status !== 'graded' || !grade){
      return '<span class="gradechip grade-UNGRADED" title="DAYSHEET.json not yet generated for this day">UNGRADED</span>';
    }
    return '<span class="gradechip grade-' + esc(grade) + '">GRADE ' + esc(grade) + '</span>';
  }

  function closedFilledRow(l, sched_ep){
    const tx = fmtTx(txMin(sched_ep, l.fill_ep));
    const dW1 = (l.win && l.win.w1) ? (l.ours_c - l.win.w1.close) : null;
    const cost_c = l.ours_c * l.qty;
    const yield_c = (l.realized_c === null || l.realized_c === undefined) ? null : l.realized_c;
    const roi = (yield_c === null || cost_c === 0) ? null : (yield_c / cost_c * 100);
    const deltaCls = dW1 === null ? '' : (dW1 <= 0 ? 'green' : 'red');
    const yieldCls = yield_c === null ? '' : (yield_c >= 0 ? 'green' : 'red');
    const roiCls = roi === null ? '' : (roi >= 0 ? 'green' : 'red');
    const exitCell = l.exit
      ? '<span class="num">' + l.exit.price_c + '¢</span>'
      : (l.result === '99' ? '<span class="green">99¢</span>'
         : l.result === '1' ? '<span class="red">1¢</span>' : mdash('BEST'));
    const yieldStr = yield_c === null ? '—'
      : (yield_c>=0?'+':'') + '$' + (Math.abs(yield_c)/100).toFixed(2);
    const roiStr = roi === null ? '—' : (roi>=0?'+':'') + roi.toFixed(1) + '%';
    return '<div class="legrow closed-filled">' +
      '<span class="player">' + esc(l.last_name) + '</span>' +
      '<span class="num">' + esc(l.qty) + '</span>' +
      '<span class="num">' + cents(l.ours_c) + '</span>' +
      '<span class="grey">' + (tx || mdash('TX')) + '</span>' +
      '<span class="' + deltaCls + '">' + (dW1===null ? mdash('W1_CLOSE') : signedCents(dW1)) + '</span>' +
      '<span class="num">' + ((l.win && l.win.w1) ? l.win.w1.close + '¢' : mdash('W1_CLOSE')) + '</span>' +
      '<span class="num">' + ((l.win && l.win.corr) ? l.win.corr.close + '¢' : mdash('W1_CLOSE')) + '</span>' +
      '<span>' + exitCell + '</span>' +
      '<span class="' + yieldCls + '">' + yieldStr + '</span>' +
      '<span class="' + roiCls + '">' + roiStr + '</span>' +
      '</div>';
  }

  function closedUnfilledRow(s, sched_ep){
    // sibling record — kind: held / pulled / never_bid
    let iconCell;
    let txCell;
    if(s.kind === 'held'){
      const heldMin = (s.ep && s.pulled_ep) ? Math.round((s.pulled_ep - s.ep) / 60) : null;
      iconCell = '<span class="icon" title="' + esc(TIP.HELD) + '">⏱ ' + (heldMin===null?'—':heldMin+'m') + '</span>';
      const tx = fmtTx(txMin(sched_ep, s.ep));
      txCell = (tx || '—') + (s.px!==null ? ' ('+s.px+'¢)' : '');
    } else if(s.kind === 'pulled'){
      const iconMin = (s.ep && s.pulled_ep) ? Math.round((s.pulled_ep - s.ep) / 60) : null;
      iconCell = '<span class="icon red" title="' + esc(TIP.PULLED) + '">✕ ' + (iconMin===null?'—':iconMin+'m') + '</span>';
      const tx = fmtTx(txMin(sched_ep, s.ep));
      txCell = (tx || '—') + (s.px!==null ? ' ('+s.px+'¢)' : '');
    } else {
      // never_bid
      iconCell = '<span class="pair-x-chip" title="' + esc(TIP.NEVER) + '">PAIR ✕</span>';
      txCell = mdash('NEVER');
    }
    return '<div class="legrow closed-unfilled">' +
      '<span class="player">' + esc(s.last_name || '—') + '</span>' +
      '<span class="num">' + (s.qty === null || s.qty === undefined ? '—' : esc(s.qty)) + '</span>' +
      '<span>' + iconCell + '</span>' +
      '<span class="grey">' + txCell + '</span>' +
      '<span>' + mdash('W1_LOW') + '</span>' +
      '<span>' + mdash('W1_CLOSE') + '</span>' +
      '<span>' + mdash('BOUNCE') + '</span>' +
      '<span>' + mdash('W2_HIGH') + '</span>' +
      '</div>';
  }

  async function loadClosed(){
    const body = document.getElementById('closed-body');
    let games = [];
    try{
      const dayParam = new URLSearchParams(window.location.search).get('day');
      const r = await fetch(withTok('/api/closed.json' + (dayParam ? '?day=' + encodeURIComponent(dayParam) : '')));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-closed').textContent = '(' + games.length + ')';
    if(!games.length){
      body.innerHTML = CLS_HEAD_FILLED + '<div class="empty">no closed games for today yet</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const sched_ep = (g.anchors && g.anchors.sched_ep) || null;
      const chip = gradeChip(g.grade_status, g.grade);
      const filledLegs = (g.legs || []);
      const filledRows = filledLegs.map(l => closedFilledRow(l, sched_ep)).join('');
      const sibs = (g.siblings || []);
      const sibRows = sibs.length
        ? CLS_HEAD_UNFILLED + sibs.map(s => closedUnfilledRow(s, sched_ep)).join('')
        : '';

      let foot = '';
      if(g.pair_complete && filledLegs.length >= 2){
        const cost = filledLegs.reduce((s,l)=> s + l.ours_c * l.qty, 0);
        const payout = filledLegs.reduce((s,l)=> {
          if(l.exit) return s + l.exit.price_c * l.exit.qty;
          if(l.result === '99') return s + 99 * l.qty;
          if(l.result === '1') return s + 1 * l.qty;
          return s;
        }, 0);
        const yield_c = filledLegs.reduce((s,l)=> s + ((l.realized_c===null||l.realized_c===undefined) ? 0 : l.realized_c), 0);
        const roi = cost > 0 ? (yield_c / cost * 100) : null;
        const yCls = yield_c >= 0 ? 'green' : 'red';
        const rCls = roi === null ? '' : (roi >= 0 ? 'green' : 'red');
        foot = '<div class="foot-sigma closed">' +
          '<span class="lbl-sigma">Σ</span>' +
          '<span></span><span></span><span></span><span></span>' +
          '<span></span><span></span>' +
          '<span class="num">' + dollars(payout) + '</span>' +
          '<span class="' + yCls + '">' + (yield_c>=0?'+':'') + '$' + (Math.abs(yield_c)/100).toFixed(2) + '</span>' +
          '<span class="' + rCls + '">' + (roi===null?'—':((roi>=0?'+':'') + roi.toFixed(1) + '%')) + '</span>' +
          '</div>';
      }

      return '<div class="gamebox">' + gameHead(g, chip) +
        CLS_HEAD_FILLED + filledRows + sibRows + foot +
        '</div>';
    }).join('');
  }

  // ── header age tickers (unchanged wire) ──
  function fmtAge(s){
    s = Math.round(s);
    if(s < 120) return s + 's';
    if(s < 7200) return Math.round(s/60) + 'm';
    return (s/3600).toFixed(1) + 'h';
  }
  async function loadTapeAge(){
    try{
      const r = await fetch(withTok('/api/positions.json'));
      const age = r.headers.get('X-Tape-Age-Seconds');
      const rec = r.headers.get('X-Recorder-Age-Seconds');
      document.getElementById('tapeage').textContent = age ? fmtAge(age) : '—';
      const recEl = document.getElementById('recage');
      const st = document.getElementById('recstate');
      if(rec){
        recEl.textContent = fmtAge(rec);
        const stale = Number(rec) > 300;
        recEl.classList.toggle('tapeage-stale', stale);
        st.innerHTML = stale ? '<span class="tapeage-stale">FEED STALE</span>' : '';
      } else {
        recEl.textContent = '—';
        st.innerHTML = '<span class="red">NO HEARTBEAT</span>';
      }
    }catch(e){}
  }

  loadSlate();
  loadPositions();
  loadOrders();
  loadClosed();
  loadTapeAge();
  const hashTab = (window.location.hash || '').replace('#','');
  if(['positions','orders','closed'].includes(hashTab)) switchTab(hashTab);
  setInterval(() => { loadSlate(); loadPositions(); loadOrders(); loadClosed(); loadTapeAge(); }, 30000);
</script>
</body>
</html>
"""
