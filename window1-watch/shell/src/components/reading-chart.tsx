import { useEffect, useId, useMemo, useRef, useState } from 'react';
import type { Frame, LoadedGame, Receipt } from '@/lib/tune-tape';
import { replayClock, cents, plain, readingCard, sentenceFor, type ReadingAction } from '@/lib/reading-view';
import { FourLineCard } from './four-line-card';

export function ReadingChart({ game, frame, side, receipt, onReceipt }: {
  game: LoadedGame; frame: number; side: string; receipt: Receipt | null; onReceipt: (index: number) => void;
}) {
  const host = useRef<HTMLDivElement>(null), id = useId().replaceAll(':', '');
  const [size, setSize] = useState({ width: 800, height: 320 });
  const [hover, setHover] = useState<{ x: number; row: Frame } | null>(null);
  const [action, setAction] = useState<ReadingAction | null>(null);
  const [floorHover, setFloorHover] = useState(false);
  const now = game.frames[frame], first = side === game.face.legs[0];
  const getLast = (r: Frame) => first ? r.firstLast : r.secondLast;
  const getRest = (r: Frame) => first ? r.firstRest : r.secondRest;
  const floor = game.face.truth?.legs[side];
  const sentence = sentenceFor(receipt, side);
  const cascade = (receipt?.legs[side] as { pool_cascade?: { selected_layer?: string; layers?: Record<string, { member_count?: number }> } } | undefined)?.pool_cascade;
  const memberCount = cascade?.selected_layer ? cascade.layers?.[cascade.selected_layer]?.member_count : undefined;
  const axis = now.pre_first_tick ? game.face.render.inspection_axis : game.face.render.axis;
  const rows = useMemo(() => game.frames.slice(now.pre_first_tick ? 0 : game.face.render.play_start_frame), [game, now.pre_first_tick]);
  const oracle = game.face.oracle?.legs[side]?.path ?? [];
  const actions = useMemo(() => [...game.face.render.bid_actions, ...(game.face.render.supersessions ?? [])].filter(a => a.leg === side) as ReadingAction[], [game, side]);
  // Per-side axis extent is visual geometry, not a forecast or new stored value.
  const domain = useMemo(() => {
    const values = [...rows.flatMap(r => [getLast(r), getRest(r)]), ...oracle.map(r => r.perfect), ...actions.map(a => a.marker_cents), ...game.face.os.map(r=>sentenceFor(r,side)?.Q), floor?.floor_cents].filter((v): v is number => typeof v === 'number' && Number.isFinite(v));
    if (!values.length) return null;
    const low = values.reduce((a,b)=>Math.min(a,b)), high = values.reduce((a,b)=>Math.max(a,b)), padding = Math.max(1, (high - low) * .12);
    return [low - padding, high + padding];
  }, [game, side, now.pre_first_tick]);
  useEffect(() => {
    if (!host.current) return;
    const observer = new ResizeObserver(([entry]) => setSize({ width: entry.contentRect.width, height: entry.contentRect.height }));
    observer.observe(host.current); return () => observer.disconnect();
  }, []);
  useEffect(() => { setAction(null); setHover(null); setFloorHover(false); }, [game, frame]);
  const { width: w, height: h } = size, left = 10, right = w - 34, top = 24, bottom = h - 24;
  const x = (m: number) => left + (axis.start_minutes_to_bell - m) / (axis.start_minutes_to_bell - axis.end_minutes_to_bell) * (right - left);
  const y = (v: number) => domain ? top + (domain[1] - v) / (domain[1] - domain[0]) * (bottom - top) : top;
  function path(data: { m: number; value: number | null }[]) {
    let d = '', previous: number | null = null;
    for (const r of data) {
      if (r.value == null) { previous = null; continue; }
      d += previous == null ? `M${x(r.m)},${y(r.value)}` : `H${x(r.m)}V${y(r.value)}`;
      previous = r.value;
    }
    return d;
  }
  const paths = useMemo(() => ({
    tape: path(rows.map(r => ({m:r.minutesToBell,value:getLast(r)}))),
    rest: path(rows.map(r => ({m:r.minutesToBell,value:getRest(r)}))),
    perfect: path(oracle.map(r => ({m:r.minutesToBell,value:r.perfect}))),
    call: path(game.face.os.map(r=>({m:r.minutesToBell,value:sentenceFor(r,side)?.Q??null}))),
  }), [game, rows, side, size, domain, axis]);
  const tapeSegments=useMemo(()=>{
    const segments:{d:string;tone:string}[]=[];
    for(let i=1;i<rows.length;i++) {
      const a=getLast(rows[i-1]),b=getLast(rows[i]);if(a==null||b==null)continue;
      const tone=b>a?'rise':b<a?'fall':'flat';
      segments.push({d:`M${x(rows[i-1].minutesToBell)},${y(a)}H${x(rows[i].minutesToBell)}V${y(b)}`,tone});
    }return segments;
  },[rows,game,side,size,domain,axis]);
  const pointer = (clientX: number) => {
    if (!host.current) return;
    const px = Math.max(left, Math.min(right, clientX - host.current.getBoundingClientRect().left));
    const mtb = axis.start_minutes_to_bell - (px - left) / (right - left) * (axis.start_minutes_to_bell - axis.end_minutes_to_bell);
    if (mtb < now.minutesToBell) { setHover(null); return; }
    let lo = 0, hi = rows.length;
    while (lo < hi) { const mid = (lo + hi) >>> 1; if (rows[mid].minutesToBell >= mtb) lo = mid + 1; else hi = mid; }
    setHover({ x: px, row: rows[Math.max(0, lo - 1)] }); setAction(null);
  };
  // Filled bids must remain selectable above dense same-price renewal markers.
  const pastActions = actions.filter(a => now.receipt_index != null && a.receipt_index <= now.receipt_index && a.marker_cents != null && a.minutes_to_bell != null).sort((a,b)=>Number(Boolean(a.fill))-Number(Boolean(b.fill)));
  const fill = game.face.render.fill_events.find(f => f.leg === side && f.receipt_index <= (now.receipt_index ?? -1));
  const fillDisplay=action?.fill?game.pressure?.executions?.find(e=>e.action_id===action.id):undefined;
  return <section className="reading-side" aria-label={`${side} chart and sentence`}>
    <header className="reading-sentence" title={`Tape last true trade ${cents(getLast(now))}; receipt's seen price ${cents(sentence?.P)}; forecast ${cents(sentence?.Q)}; expected ${sentence?.X ?? 'no time recorded'} minutes to bell.\n${memberCount == null ? 'No pool count here' : `Pool of ${memberCount} games`}.\nTrace ${game.face.provenance.trace_sha256}\n${receipt?.receipt ?? 'No receipt'}`}>
      <div><strong>{side}</strong><small>{first?'First side':'Second side'}</small></div><div className="engine-last"><b>{cents(getLast(now))}</b><small>last true trade</small></div>
    </header>
    <div className="reading-plot" ref={host} onMouseLeave={() => { setHover(null); setFloorHover(false); }}>
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label={`${side}: recorded tape, our bid, fills, recorded floor and perfect sentence. Hover or tap for exact values.`}>
        <defs><clipPath id={`${id}-past`}><rect x={left} y={0} width={Math.max(0, x(now.minutesToBell) - left)} height={h}/></clipPath></defs>
        {[.25,.5,.75].map(p => <g key={p}><line className="reading-grid" x1={left} x2={right} y1={top+(bottom-top)*p} y2={top+(bottom-top)*p}/>{domain?<text className="reading-axis-label" x={right+5} y={top+(bottom-top)*p+3}>{Math.round(domain[1]-(domain[1]-domain[0])*p)}</text>:null}</g>) }
        {floor?.status === 'OK' && floor.floor_cents != null ? <line data-recorded-floor className="reading-floor" x1={left} x2={right} y1={y(floor.floor_cents)} y2={y(floor.floor_cents)}/> : null}
        <path data-perfect-sentence className="reading-perfect" d={paths.perfect}/>
        <g clipPath={`url(#${id}-past)`}>
          <g data-tape-path>{tapeSegments.map((s,i)=><path key={i} className={`reading-tape tape-${s.tone}`} d={s.d}/>)}</g>
          <path data-call-path className="reading-call" d={paths.call}/>
          <path data-rest-path className="reading-rest" d={paths.rest}/>
        </g>
        <line className="reading-cursor" x1={x(now.minutesToBell)} x2={x(now.minutesToBell)} y1={4} y2={h-4}/>
        <text className="reading-axis-label" x={Math.min(right, x(now.minutesToBell)-6)} y={14} textAnchor="end">now</text>
        <rect fill="transparent" x={left} y={top} width={right-left} height={bottom-top} onMouseMove={e => pointer(e.clientX)} onClick={e => pointer(e.clientX)} />
        {hover && domain ? <><line className="reading-hover-guide" x1={hover.x} x2={hover.x} y1={top} y2={bottom}/>{getLast(hover.row) != null ? <circle cx={hover.x} cy={y(getLast(hover.row)!)} r={3} className="reading-tape-dot"/> : null}</> : null}
        {floor?.status === 'OK' && floor.floor_cents != null && floor.minutes_to_bell != null ? <g className="reading-floor-mark" role="button" tabIndex={0} aria-label={plain(floor.markers.play?.hover_note)} onFocus={() => {setFloorHover(true);setAction(null)}} onBlur={() => setFloorHover(false)} onMouseEnter={() => {setFloorHover(true);setHover(null);setAction(null)}} onMouseLeave={() => setFloorHover(false)} onClick={() => {setFloorHover(v=>!v);setAction(null)}} onKeyDown={e => {if(e.key==='Enter'||e.key===' '){e.preventDefault();setFloorHover(v=>!v)}}}>
          <rect fill="transparent" x={x(floor.minutes_to_bell)-20} y={y(floor.floor_cents)-30} width={40} height={40}/>
          <line x1={x(floor.minutes_to_bell)} x2={x(floor.minutes_to_bell)} y1={y(floor.floor_cents)-17} y2={y(floor.floor_cents)}/>
          <path d={`M${x(floor.minutes_to_bell)},${y(floor.floor_cents)-17}h8v5h-8`}/>
        </g> : null}
        {pastActions.map(a => <g key={a.id} role="button" tabIndex={0} data-action-id={a.id} data-action-kind={a.kind} aria-label={readingCard(a)[0]} className="reading-action" onFocus={() => {setAction(a);setHover(null)}} onMouseEnter={() => {setAction(a);setHover(null);setFloorHover(false)}} onClick={() => {setAction(a);setHover(null)}} onKeyDown={e => {if(e.key==='Enter'||e.key===' '){e.preventDefault();setAction(a)}if(e.key==='Escape')setAction(null)}}>
          <rect fill="transparent" x={x(a.minutes_to_bell!)-10} y={y(a.marker_cents!)-12} width={20} height={24}/>
          {a.fill ? <circle cx={x(a.minutes_to_bell!)} cy={y(a.marker_cents!)} r={5}/> : <rect x={x(a.minutes_to_bell!)-2} y={y(a.marker_cents!)-2} width={4} height={4}/>}
        </g>)}
        <text className="reading-axis-label" x={left} y={h-4}>first tick</text><text className="reading-axis-label" x={right} y={h-4} textAnchor="end">bell</text>
      </svg>
      <div className="reading-line-key"><span>{floor?.status==='OK'?`Recorded floor ${cents(floor.floor_cents)}`:'No verified floor'}</span><span className="reading-bid-key">{fill?'filled':'bid history'}</span></div>
      {!domain ? <p className="reading-no-data">No data here.</p> : null}
      {hover ? <div className="reading-tip" role="tooltip" style={{left:Math.max(8,Math.min(hover.x,w-310))}}>
        <p>{side} · {replayClock(hover.row.minutesToBell)}</p><p>Last trade {cents(getLast(hover.row))} · our bid {getRest(hover.row)==null?'none':cents(getRest(hover.row))}</p>
        <p>Book {cents(first?hover.row.firstBid:hover.row.secondBid)} / {cents(first?hover.row.firstAsk:hover.row.secondAsk)}</p><button onClick={() => {if(hover.row.receipt_index!=null)onReceipt(hover.row.receipt_index)}}>See this moment in Details</button>
      </div> : null}
      {floorHover ? <div className="reading-tip" role="tooltip"><p>{plain(floor?.markers.play?.hover_note)}</p><p>Known afterward, not used by the machine.</p></div> : null}
      {action ? <div className="reading-tip reading-action-tip" role="tooltip" onKeyDown={e=>{if(e.key==='Escape')setAction(null)}}>
        <FourLineCard lines={fillDisplay?.card_lines??readingCard(action)} details={fillDisplay?[fillDisplay.source,...action.details_lines]:action.details_lines} color="var(--color-rest)"/>
        <div className="reading-tip-controls"><button onClick={()=>onReceipt(action.receipt_index)}>Inspect this bid</button><button onClick={()=>setAction(null)}>Close</button></div>
      </div> : null}
    </div>
  </section>;
}
