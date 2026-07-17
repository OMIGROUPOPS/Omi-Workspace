"""HTML/CSS/JS for the live /daysheet page.

Ported from the approved mock (mock/daysheet_mock_v4.html, "the spec,
verbatim") almost 1:1 for CSS and structure. What changed for the live
build:

  - All three tabs are now populated by fetch() against the four JSON
    routes this same file's sibling module (daysheet_panel.py) serves,
    instead of hardcoded DETAILS/PROOF objects.
  - Proof-popover unit label corrected from "lots" to "ct" (contracts) —
    per the standing Time Sourcing Law amendment note; "lots" was a mock
    placeholder word, this market trades contracts, not lots.
  - Every place the mock had a hardcoded exhibit now renders from real
    game data, with an honest empty/placeholder state matching the mock's
    own "no-bell yet" / "not bid — never conceived" / "GAP-named" style
    whenever the underlying live field isn't available. Never a fabricated
    number.
  - "ungraded" chip style added for the CLOSED tab (grey, not a color used
    for A-F) for the case where DAYSHEET.json doesn't exist yet for a day.

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
  .live-tag{
    color:var(--red); font-weight:700; font-size:8px; letter-spacing:0.06em;
    margin-left:5px;
  }

  .tabs{ display:flex; gap:6px; margin-bottom:14px; border-bottom:1px solid var(--border); padding-bottom:10px; }
  .tab{
    font-size:10px; letter-spacing:0.12em; text-transform:uppercase;
    padding:6px 12px; border:1px solid var(--border); background:transparent;
    color:var(--grey); cursor:pointer; font-family:inherit; font-weight:700;
  }
  .tab.active{ color:var(--orange); border-color:rgba(255,140,0,0.5); background:rgba(255,140,0,0.1); }
  .tab .count{ color:inherit; opacity:0.7; margin-left:4px; }

  .colhead{
    display:grid; font-size:8px; letter-spacing:0.1em; text-transform:uppercase;
    color:var(--grey); padding:0 12px 6px; font-weight:600;
  }
  .colhead.positions{ grid-template-columns: 112px 46px 46px 150px 150px 30px 60px 80px; }
  .colhead.orders{ grid-template-columns: 96px 46px 90px 90px 30px 70px; }
  .colhead.closed{ grid-template-columns: 100px 90px 34px 90px 56px 80px; column-gap:10px; }
  .colhead span{ text-align:right; white-space:nowrap; }
  .colhead span.lbl-last{ text-align:left; }

  .gamebox{
    border:1px solid var(--border); background:var(--panel);
    margin-bottom:8px; overflow:hidden; cursor:pointer;
  }
  .gamebox:hover{ border-color:rgba(255,140,0,0.35); }
  .gamehead{
    display:flex; align-items:center; gap:8px; padding:6px 12px;
    font-size:10px; border-bottom:1px solid var(--border); background:#050505;
  }
  .gamehead .names{ color:var(--white); font-weight:700; }
  .gamehead .meta{ color:var(--grey); font-size:9px; }
  .badge-both{
    font-size:7px; letter-spacing:0.08em; text-transform:uppercase; font-weight:700;
    color:var(--green); border:1px solid rgba(0,255,136,0.4); background:rgba(0,255,136,0.08);
    padding:1px 5px; margin-left:auto;
  }

  .legrow{
    display:grid; align-items:center; padding:5px 12px; font-size:10px;
    border-top:1px solid rgba(26,26,46,0.5);
  }
  .legrow.positions{ grid-template-columns: 112px 46px 46px 150px 150px 30px 60px 80px; }
  .legrow.orders{ grid-template-columns: 96px 46px 90px 90px 30px 70px; }
  .legrow.closed{ grid-template-columns: 100px 90px 34px 90px 56px 80px; column-gap:10px; }
  .legrow span{ text-align:right; white-space:nowrap; }
  .legrow span.last{ text-align:left; color:var(--orange); font-weight:700; }

  .lo{ color:var(--blue); } .hi{ color:var(--purple); }
  .rangepair .lo{ color:var(--blue); } .rangepair .sep{ color:var(--dimgrey); margin:0 2px; }
  .win{ color:var(--green); font-weight:700; } .loss{ color:var(--red); font-weight:700; }
  .delta-neg{ color:var(--green); font-weight:700; } .delta-pos{ color:var(--red); font-weight:700; }
  .result-99{ color:var(--green); font-weight:700; } .result-1{ color:var(--red); font-weight:700; }
  .gray-line{
    grid-column:1 / -1; padding:4px 12px 6px; font-size:9px; color:var(--grey);
    font-style:italic; border-top:1px solid rgba(26,26,46,0.5);
  }
  .no-bell{ color:var(--dimgrey); font-style:italic; }
  .bellchip{ color:var(--grey); font-size:9px; }
  .bellchip .est{ color:var(--grey); font-size:8px; border:1px solid var(--border); padding:0 3px; margin-left:2px; }
  .bellchip .live{ color:var(--blue); font-size:8px; border:1px solid rgba(0,191,255,0.4); padding:0 3px; margin-left:2px; }
  .bellchip .official{ color:var(--green); font-size:8px; border:1px solid rgba(0,255,136,0.4); padding:0 3px; margin-left:2px; font-weight:700; }
  .gamehead .deeplink{ margin-left:auto; }
  .footnote .walkpart{ color:var(--grey); }
  .footnote .walkverdict{ color:var(--green); font-weight:700; }

  .overlay{
    position:fixed; inset:0; background:rgba(0,0,0,0.85); display:none;
    align-items:center; justify-content:center; z-index:50; padding:20px;
  }
  .overlay.open{ display:flex; }
  .detailbox{
    background:var(--panel); border:1px solid rgba(255,140,0,0.4);
    max-width:760px; width:100%; max-height:88vh; overflow-y:auto;
    padding:0; position:relative;
  }
  .detailhead{
    display:flex; align-items:center; gap:10px; padding:12px 16px;
    border-bottom:1px solid var(--border); background:#050505;
  }
  .detailhead .names{ font-size:13px; font-weight:700; color:var(--white); }
  .detailhead .meta{ font-size:9px; color:var(--grey); }
  .closebtn{
    margin-left:auto; background:none; border:1px solid var(--border); color:var(--grey);
    font-family:inherit; font-size:10px; padding:3px 8px; cursor:pointer;
  }
  .closebtn:hover{ color:var(--orange); border-color:rgba(255,140,0,0.4); }

  .gradebar{
    display:flex; align-items:baseline; gap:8px; padding:8px 16px;
    border-bottom:1px solid var(--border); font-size:10px;
  }
  .gradechip{
    font-size:12px; font-weight:800; padding:2px 8px; letter-spacing:0.05em;
    border:1px solid currentColor; white-space:nowrap; flex-shrink:0;
  }
  .grade-A{ color:var(--green); } .grade-B{ color:var(--blue); }
  .grade-C{ color:var(--orange); } .grade-D,.grade-F{ color:var(--red); }
  .grade-UNGRADED{ color:var(--dimgrey); }
  .footnote{ color:var(--grey); font-size:9.5px; }
  .footnote b{ color:var(--white); font-weight:700; }
  .footnote .cls{ color:var(--orange); }
  .footnote .fix{ color:var(--blue); }

  .gradebar-inline{
    display:flex; align-items:baseline; gap:8px; padding:6px 12px;
    border-top:1px solid rgba(26,26,46,0.5); font-size:9.5px; background:#060606;
  }
  .gradebar-inline .gradechip{ font-size:10px; padding:1px 6px; }
  .gradebar-inline .footnote{ font-size:9px; min-width:0; }

  .detailbody{ display:flex; padding:14px 16px; gap:16px; }
  .detailleg{ flex:1; min-width:0; }
  .detailleg .lastname{ color:var(--orange); font-weight:700; font-size:12px; margin-bottom:6px; }
  .statline{
    display:grid; grid-template-columns: 70px 1fr; gap:6px; font-size:9.5px;
    padding:2px 0; color:var(--grey);
  }
  .statline b{ color:var(--white); }
  .statusline{
    margin-top:8px; padding-top:8px; border-top:1px solid rgba(26,26,46,0.5);
    font-size:10px; color:var(--white); line-height:1.5;
  }
  .statusline .warn{ color:var(--red); font-weight:700; }
  .statusline .est{ color:var(--grey); font-size:8.5px; border:1px solid var(--border); padding:0 3px; margin-left:2px; }
  .statusline .live{ color:var(--blue); font-size:8.5px; border:1px solid rgba(0,191,255,0.4); padding:0 3px; margin-left:2px; }
  .divider{ width:1px; background:var(--border); }

  .hint{ font-size:8.5px; color:var(--dimgrey); text-align:center; padding-top:2px; }
  .empty{ font-size:10px; color:var(--dimgrey); text-align:center; padding:24px 0; font-style:italic; }

  .join-pending{ color:var(--dimgrey); font-style:italic; }

  .exitline{
    grid-column:1 / -1; padding:4px 12px 6px; font-size:9px; color:var(--blue);
    border-top:1px solid rgba(26,26,46,0.5); display:flex; align-items:center; gap:8px;
  }
  .exitline .lbl{ color:var(--grey); }
  .deeplink{
    color:var(--orange); text-decoration:none; font-size:9px; margin-left:auto;
    border:1px solid rgba(255,140,0,0.35); padding:1px 6px;
  }
  .deeplink:hover{ background:rgba(255,140,0,0.1); }

  .proofable{ cursor:pointer; border-bottom:1px dotted currentColor; display:inline-block; width:fit-content; margin-left:auto; }
  .proofable:hover{ opacity:0.75; }
  .popover{
    position:fixed; z-index:100; background:#0d0d10; border:1px solid rgba(0,191,255,0.4);
    padding:8px 10px; font-size:9px; min-width:220px; max-width:340px; display:none;
    box-shadow:0 4px 16px rgba(0,0,0,0.6);
  }
  .popover.open{ display:block; }
  .popover .ptitle{ color:var(--blue); font-weight:700; margin-bottom:5px; font-size:9px; }
  .popover .print{
    display:flex; justify-content:space-between; gap:8px; padding:2px 0; color:var(--grey);
    border-top:1px solid rgba(26,26,46,0.6);
  }
  .popover .print:first-of-type{ border-top:none; }
  .popover .print b{ color:var(--white); }
  .popover .print .ct{ color:var(--purple); }
  .popover .receipt{
    font-size:8px; color:var(--dimgrey); margin-top:6px; padding-top:5px;
    border-top:1px solid var(--border);
  }
</style>
</head>
<body>
<div class="app">

  <div class="topbar">
    <span class="clock" id="etclock">--:--:-- PM<span class="tz">ET</span></span>
    <span class="sep">|</span>
    <span class="age">last fill <b id="tapeage">--</b> ago</span>
    <span class="sep">|</span>
    <span class="age">recorder <b id="recage">--</b> <span id="recstate"></span></span>
  </div>

  <div class="tabs">
    <button class="tab active" data-tab="positions" onclick="switchTab('positions')">POSITIONS <span class="count" id="cnt-positions">(0)</span></button>
    <button class="tab" data-tab="orders" onclick="switchTab('orders')">ORDERS <span class="count" id="cnt-orders">(0)</span></button>
    <button class="tab" data-tab="closed" onclick="switchTab('closed')">CLOSED <span class="count" id="cnt-closed">(0)</span></button>
  </div>

  <div id="positions" class="tabpanel">
    <div class="colhead positions">
      <span class="lbl-last">LAST (KALSHI)</span><span>OURS (FILL)</span><span></span><span>W1 LOW·HIGH (TRADED)</span><span>CORR LOW·HIGH (TRADED)</span><span>CT</span><span>COST</span><span>PAYOUT@EXIT</span>
    </div>
    <div id="positions-body"></div>
    <div class="hint">click a game to open its detail · click any low·high value for its tape proof</div>
  </div>

  <div id="orders" class="tabpanel" style="display:none;">
    <div class="colhead orders">
      <span class="lbl-last">LAST</span><span>AIM</span><span>W1 LO/HI</span><span>CORR LO/HI</span><span>CT</span><span>AGE</span>
    </div>
    <div id="orders-body"></div>
  </div>

  <div id="closed" class="tabpanel" style="display:none;">
    <div class="colhead closed">
      <span class="lbl-last">OURS (FILL)</span><span>W1 CLOSE (TRADED)</span><span>Δ</span><span>CORR CLOSE (TRADED)</span><span>RESULT</span><span>REALIZED</span>
    </div>
    <div id="closed-body"></div>
  </div>

</div>

<div class="overlay" id="overlay" onclick="if(event.target===this)closeDetail()">
  <div class="detailbox" id="detailbox"></div>
</div>

<div class="popover" id="popover"></div>

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

  function esc(s){ return (s===null||s===undefined) ? '' : String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

  function fmtCents(v){ return (v===null||v===undefined) ? '—' : v + '¢'; }
  function fmtDollars(v_c){ return (v_c===null||v_c===undefined) ? '—' : '$' + (v_c/100).toFixed(2); }

  // NAME LAW: a null last_name = failed join — never a ticker fragment
  function legName(l){
    return l.last_name ? '<span class="last">' + esc(l.last_name) + '</span>'
                       : '<span class="last join-pending">join pending</span>';
  }
  // CORRIDOR LAW: both anchors always — sched + first point. The bell
  // MEANS first-point evidence; estimates clamp to >= sched; where no
  // source observed anything, "first pt not observed (>= sched)" —
  // never a fabricated time.
  // C-OFFICIAL-BELL: THE bell = the official milestone start (KALSHI)
  // when it exists, else our own LIVE first-point evidence, else
  // "not observed (≥ sched)". Estimates live only in the hover note.
  function anchorsChip(a){
    if(!a) return '<span class="no-bell">no anchors</span>';
    const sched = a.sched ? 'sched ' + esc(a.sched) : 'sched unknown';
    let fpPart;
    const fp = a.fp;
    if(fp && fp.badge === 'OFFICIAL'){
      fpPart = 'bell ' + esc(fp.label) + ' · official <span class="official">KALSHI</span>';
    } else if(fp){
      fpPart = 'bell ' + esc(fp.label) + ' (' + esc(fp.src) + ') <span class="live">LIVE</span>';
    } else {
      fpPart = 'bell not observed' + (a.sched ? ' (≥ ' + esc(a.sched) + ')' : '');
    }
    const defect = (fp && fp.defect)
      ? ' <span class="loss" title="' + esc(fp.defect) + '">⚠ BELL&lt;SCHED filed</span>' : '';
    const hover = a.est_note ? ' title="' + esc(a.est_note) + '"' : '';
    return '<span class="bellchip"' + hover + '>' + sched + ' · ' + fpPart + defect + '</span>';
  }
  // W1/CORR lo·hi cell from the real tape; "no tape" is a named state
  // empty-state text per the SILENT-EMPTY TAPE LOOKUP law: a fact
  // ("no W1 prints") renders ONLY when coverage proves it; lookup
  // failures render as the named gap, filed server-side.
  function winEmpty(win, which){
    const st = win[which + '_state'];
    if(st === 'tape_gap') return '<span class="no-bell">tape gap — filed</span>';
    if(st === 'no_anchor') return '<span class="no-bell">no sched anchor — filed</span>';
    if(which === 'corr') return '<span class="no-bell">no corridor prints</span>';
    return '<span class="no-bell">no W1 prints</span>';
  }
  function winCell(win, which, ticker, name){
    if(!win || win.state === 'no_tape') return '<span class="no-bell">no tape</span>';
    if(win.state === 'tape_error') return '<span class="no-bell">tape fetch error</span>';
    const w = win[which];
    if(!w) return winEmpty(win, which);
    return '<span class="rangepair proofable" onclick="event.stopPropagation(); openProof(event,\'' + esc(ticker) + '\',\'' + esc(name||ticker) + '\')">' +
      '<span class="lo">' + w.lo + '</span><span class="sep">·</span><span class="hi">' + w.hi + '¢</span></span>';
  }
  function winClose(win, which, ticker, name){
    if(!win || win.state === 'no_tape') return '<span class="no-bell">no tape</span>';
    if(win.state === 'tape_error') return '<span class="no-bell">tape fetch error</span>';
    const w = win[which];
    if(!w) return winEmpty(win, which);
    return '<span class="proofable" onclick="event.stopPropagation(); openProof(event,\'' + esc(ticker) + '\',\'' + esc(name||ticker) + '\')">' + w.close + '¢</span>';
  }
  function gameHead(g){
    const link = '<a class="deeplink" href="' + esc(g.deeplink) + '" target="_blank" onclick="event.stopPropagation()">↗ KALSHI</a>';
    return '<div class="gamehead"><span class="names' + (g.joined ? '' : ' join-pending') + '">' + esc(g.names) + '</span>' +
      '<span class="meta">' + esc(g.tournament || '') + '</span>' +
      '<span class="meta">' + anchorsChip(g.anchors) + '</span>' + link + '</div>';
  }

  // ── proof-on-click: real tape prints fetched per ticker ──
  const tapeCache = {};
  async function openProof(evt, ticker, title){
    const pop = document.getElementById('popover');
    let data = tapeCache[ticker];
    if(!data){
      try{
        const r = await fetch(withTok('/api/tape/' + encodeURIComponent(ticker) + '.json'));
        data = await r.json();
        tapeCache[ticker] = data;
      }catch(e){
        data = { prints: [], has_receipt: false };
      }
    }
    if(!data.has_receipt || !data.prints.length){
      pop.innerHTML = '<div class="ptitle">no tape</div><div class="receipt">the public trades tape has no prints for this ticker — the miss is filed server-side, never styled over</div>';
    } else {
      let winRows = '';
      if(data.windows){
        const w = data.windows;
        if(w.w1) winRows += '<div class="print"><span>W1 lo·hi·close</span><b><span class="lo">' + w.w1.lo + '</span>·<span class="hi">' + w.w1.hi + '</span>·' + w.w1.close + '¢</b><span class="ct">' + w.w1.n + ' prints</span></div>';
        if(w.corr) winRows += '<div class="print"><span>CORR lo·hi·close</span><b><span class="lo">' + w.corr.lo + '</span>·<span class="hi">' + w.corr.hi + '</span>·' + w.corr.close + '¢</b><span class="ct">' + w.corr.n + ' prints</span></div>';
      }
      const rows = data.prints.map(p =>
        '<div class="print"><span>' + esc(p.t) + '</span><b>' + esc(p.price_c) + '¢</b><span class="ct">' + esc(p.ct) + ' ct</span></div>'
      ).join('');
      pop.innerHTML =
        '<div class="ptitle">' + esc(title || ticker) + ' · tape' + (data.n_total ? ' (' + data.n_total + ' prints, last ' + data.prints.length + ' shown)' : '') + '</div>' +
        winRows + rows +
        '<div class="receipt">source: ' + esc(data.source || 'kalshi public trades') + ' · every number here has a receipt</div>';
    }
    const rect = evt.target.getBoundingClientRect();
    pop.style.left = Math.min(rect.left, window.innerWidth - 350) + 'px';
    pop.style.top = (rect.bottom + 6) + 'px';
    pop.classList.add('open');
  }
  document.addEventListener('click', (e) => {
    const pop = document.getElementById('popover');
    if(pop.classList.contains('open') && !pop.contains(e.target) && !e.target.classList.contains('proofable')){
      pop.classList.remove('open');
    }
  });

  function closeDetail(){ document.getElementById('overlay').classList.remove('open'); }

  function openDetailGeneric(title, meta, gradeHtml, legsHtml){
    document.getElementById('detailbox').innerHTML =
      '<div class="detailhead"><span class="names">' + esc(title) + '</span><span class="meta">' + esc(meta) + '</span>' +
      '<button class="closebtn" onclick="closeDetail()">CLOSE ✕</button></div>' +
      gradeHtml +
      '<div class="detailbody">' + legsHtml + '</div>';
    document.getElementById('overlay').classList.add('open');
  }

  // ── POSITIONS ──
  async function loadPositions(){
    const body = document.getElementById('positions-body');
    let games = [];
    try{
      const r = await fetch(withTok('/api/positions.json'));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-positions').textContent = '(' + games.length + ')';
    if(!games.length){
      body.innerHTML = '<div class="empty">no open positions right now</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const legs = g.legs.map(l => (
        '<div class="legrow positions">' +
        legName(l) +
        '<span>' + fmtCents(l.mark_c) + '</span>' +
        '<span>' + fmtCents(l.fill_price_c ?? l.basis_c) + '</span>' +
        '<span>' + winCell(l.win, 'w1', l.ticker, l.last_name) + '</span>' +
        '<span>' + winCell(l.win, 'corr', l.ticker, l.last_name) + '</span>' +
        '<span>' + esc(l.qty) + '</span>' +
        '<span>' + fmtDollars(l.basis_c * l.qty) + '</span>' +
        '<span>' + (l.exit_resting ? fmtDollars(l.exit_resting.price_c * l.exit_resting.qty) : '—') + '</span>' +
        '</div>' +
        (l.exit_resting ?
          '<div class="exitline"><span class="lbl">exit</span> <b>@' + l.exit_resting.price_c + '¢ ×' + l.exit_resting.qty + ' resting</b></div>'
          : '<div class="exitline"><span class="lbl">exit</span> <span class="no-bell">no exit resting yet</span></div>')
      )).join('');
      const grayLine = g.gray_line ? '<div class="gray-line">' + esc(g.gray_line) + '</div>' : '';
      const walkBar = g.walk
        ? '<div class="gradebar-inline"><span class="footnote"><b>WALK (provisional — game open)</b> <span class="cls">' + esc(g.walk.charge || '') + '</span>' +
          (g.walk.verdict ? ' <span class="walkverdict">→ ' + esc(g.walk.verdict) + '</span>' : '') + '</span></div>'
        : '';
      return '<div class="gamebox">' + gameHead(g) + legs + grayLine + walkBar + '</div>';
    }).join('');
  }

  // ── ORDERS ──
  async function loadOrders(){
    const body = document.getElementById('orders-body');
    let games = [];
    try{
      const r = await fetch(withTok('/api/orders.json'));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-orders').textContent = '(' + games.reduce((a,g)=>a+g.legs.length,0) + ')';
    if(!games.length){
      body.innerHTML = '<div class="empty">no resting unfilled orders right now</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const legs = g.legs.map(l => (
        '<div class="legrow orders">' +
        legName(l) +
        '<span>' + fmtCents(l.aim_c) + '</span>' +
        '<span>' + winCell(l.win, 'w1', l.ticker, l.last_name) + '</span>' +
        '<span>' + winCell(l.win, 'corr', l.ticker, l.last_name) + '</span>' +
        '<span>' + esc(l.qty) + '</span>' +
        '<span>' + esc(l.age_label) + '</span>' +
        '</div>'
      )).join('');
      return '<div class="gamebox">' + gameHead(g) + legs + '</div>';
    }).join('');
  }

  // ── CLOSED ──
  function gradeChip(status, grade){
    if(status !== 'graded' || !grade){
      return '<span class="gradechip grade-UNGRADED">UNGRADED</span>';
    }
    return '<span class="gradechip grade-' + esc(grade) + '">GRADE ' + esc(grade) + '</span>';
  }

  async function loadClosed(){
    const body = document.getElementById('closed-body');
    let games = [];
    try{
      // ?day=YYYYMMDD deep-links a prior day's CLOSED sheet
      const dayParam = new URLSearchParams(window.location.search).get('day');
      const r = await fetch(withTok('/api/closed.json' + (dayParam ? '?day=' + encodeURIComponent(dayParam) : '')));
      games = await r.json();
    }catch(e){ games = []; }
    document.getElementById('cnt-closed').textContent = '(' + games.length + ')';
    if(!games.length){
      body.innerHTML = '<div class="empty">no closed games for today yet</div>';
      return;
    }
    body.innerHTML = games.map(g => {
      const legs = g.legs.map(l => {
        // ONE ROW PER LEG: OURS = avg entry fill; exit in its own line
        const oursLbl = (l.ours_c === null || l.ours_c === undefined) ? '—'
          : l.ours_c + '¢' + (l.n_entry_fills > 1 ? ' <span class="no-bell">(' + l.n_entry_fills + ' fills avg)</span>' : '');
        // time law: Δ has meaning only on W1 fills
        const delta = (l.delta_c === null || l.delta_c === undefined)
          ? '<span class="no-bell">' + (l.fill_window && l.fill_window !== 'W1' ? esc(l.fill_window) + ' — Δ n/a' : '—') + '</span>'
          : '<span class="' + (l.delta_c <= 0 ? 'delta-neg' : 'delta-pos') + '">' + (l.delta_c > 0 ? '+' : '') + l.delta_c + '</span>';
        const result = l.result === '99' ? '<span class="result-99">99¢</span>'
          : l.result === '1' ? '<span class="result-1">1¢</span>'
          : l.result === 'cashed' ? '<span class="win">cashed</span>'
          : '<span class="no-bell">open</span>';
        const realized = (l.realized_c === null || l.realized_c === undefined)
          ? '<span class="no-bell">open</span>'
          : '<span class="' + (l.realized_c >= 0 ? 'win' : 'loss') + '">' + (l.realized_c >= 0 ? '+' : '') + l.realized_c + '¢</span>';
        // time law: entry line carries placed ET -> filled ET (placed
        // has no honest source yet — the schema gap stays named)
        const entryLine = l.filled_et
          ? '<div class="exitline"><span class="lbl">entry</span> placed <span class="no-bell">— (no source: schema gap)</span> → filled <b>' + esc(l.filled_et) + '</b>' +
            (l.fill_window ? ' <span class="lbl">[' + esc(l.fill_window) + ']</span>' : ' <span class="no-bell">[window unclassifiable]</span>') +
            (l.grade_was ? (l.grade_was.indexOf('F') === 0
              ? ' <span class="win">exonerated: fill pre-' + ((l.win && l.win.fp && l.win.fp.badge === 'OFFICIAL') ? 'official-start' : 'first-point') + ' (was ' + esc(l.grade_was) + ')</span>'
              : ' <span class="loss">convicted vs ' + ((l.win && l.win.fp && l.win.fp.badge === 'OFFICIAL') ? 'official bell' : 'observed first point') + ' (was ' + esc(l.grade_was) + ')</span>') : '') +
            ((!l.grade_was && (l.grade || '').indexOf('F') === 0 && l.fill_window === 'W2' && l.win && l.win.fp && l.win.fp.badge === 'OFFICIAL') ? ' <span class="loss">convicted vs official bell</span>' : '') +
            (l.grade_note ? ' <span class="loss">' + esc(l.grade_note) + '</span>' : '') +
            '</div>'
          : '';
        const exitLine = l.exit
          ? '<div class="exitline"><span class="lbl">exit</span> <b>@' + l.exit.price_c + '¢ ×' + l.exit.qty + '</b> <span class="lbl">filled ' + esc(l.exit.at) + '</span></div>'
          : (l.result === '99' || l.result === '1'
              ? '<div class="exitline"><span class="lbl">exit</span> <span class="no-bell">settled, no sell fill</span></div>'
              : '');
        return '<div class="legrow closed">' +
          '<span class="last" style="text-align:right;">' + (l.last_name ? esc(l.last_name) : '<span class="join-pending">join pending</span>') + ' ' + oursLbl + '</span>' +
          '<span>' + winClose(l.win, 'w1', l.ticker, l.last_name) + '</span>' +
          '<span>' + delta + '</span>' +
          '<span>' + winClose(l.win, 'corr', l.ticker, l.last_name) + '</span>' +
          '<span>' + result + '</span>' +
          '<span>' + realized + '</span>' +
          '</div>' + entryLine + exitLine;
      }).join('');
      const chip = gradeChip(g.grade_status, g.grade);
      let footnote = '';
      if(g.walk){
        // THE WALK footnote, standing format: charge -> amendment -> verdict
        footnote = '<b>WALK</b> <span class="cls">' + esc(g.walk.charge || '') + '</span>' +
          (g.walk.amendment ? ' <span class="walkpart">→ ' + esc(g.walk.amendment) + '</span>' : '') +
          (g.walk.verdict ? ' <span class="walkverdict">→ ' + esc(g.walk.verdict) + '</span>' : '');
      } else if(g.footnote){
        footnote = esc(g.footnote);
      } else if(g.grade_status === 'ungraded'){
        footnote = 'DAYSHEET.json not yet generated for this day — no grade rendered';
      }
      return '<div class="gamebox">' + gameHead(g) +
        legs +
        '<div class="gradebar-inline">' + chip + '<span class="footnote">' + footnote + '</span></div>' +
        '</div>';
    }).join('');
  }

  function fmtAge(s){
    s = Math.round(s);
    if(s < 120) return s + 's';
    if(s < 7200) return Math.round(s/60) + 'm';
    return (s/3600).toFixed(1) + 'h';
  }
  async function loadTapeAge(){
    try{
      const r = await fetch(withTok('/api/positions.json'));
      // last-fill age grows lawfully on a quiet book; RECORDER age is
      // the feed-liveness alarm (>300s = STALE, loud, never silent)
      const age = r.headers.get('X-Tape-Age-Seconds');
      const rec = r.headers.get('X-Recorder-Age-Seconds');
      document.getElementById('tapeage').textContent = age ? fmtAge(age) : '—';
      const recEl = document.getElementById('recage');
      const st = document.getElementById('recstate');
      if(rec){
        recEl.textContent = fmtAge(rec);
        const stale = Number(rec) > 300;
        st.innerHTML = stale ? '<span class="loss">FEED STALE — not serving fresh truth</span>'
                             : '<span class="win">OK</span>';
      } else {
        recEl.textContent = '—';
        st.innerHTML = '<span class="loss">NO HEARTBEAT</span>';
      }
    }catch(e){}
  }

  loadPositions();
  loadOrders();
  loadClosed();
  loadTapeAge();
  // deep-linkable tabs: /daysheet?token=...#closed opens on CLOSED
  const hashTab = (window.location.hash || '').replace('#','');
  if(['positions','orders','closed'].includes(hashTab)) switchTab(hashTab);
  setInterval(() => { loadPositions(); loadOrders(); loadClosed(); loadTapeAge(); }, 30000);
</script>
</body>
</html>
"""
