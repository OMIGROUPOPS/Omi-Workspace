'use client';

import { useState, useRef, useEffect, createContext, useContext } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';

const ExpandedContext = createContext<{ expandedId: string | null; setExpandedId: (id: string | null) => void }>({ expandedId: null, setExpandedId: () => {} });

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
  'betmgm': { name: 'BetMGM', color: '#c4a44d' },
  'caesars': { name: 'Caesars', color: '#00693e' },
  'pointsbetus': { name: 'PointsBet', color: '#e42222' },
  'bovada': { name: 'Bovada', color: '#cc0000' },
  'betonlineag': { name: 'BetOnline', color: '#ff6600' },
  'lowvig': { name: 'LowVig', color: '#6b7280' },
  'mybookieag': { name: 'MyBookie', color: '#1a1a2e' },
  'williamhill_us': { name: 'Caesars', color: '#00693e' },
  'betus': { name: 'BetUS', color: '#0066cc' },
  'betrivers': { name: 'BetRivers', color: '#1a3c6e' },
  'fanatics': { name: 'Fanatics', color: '#00904a' },
};

// Comprehensive market labels for all sports
const MARKET_LABELS: Record<string, string> = {
  // NFL
  'pass tds': 'Passing TDs',
  'pass yds': 'Passing Yards',
  'pass completions': 'Pass Completions',
  'pass attempts': 'Pass Attempts',
  'pass interceptions': 'Interceptions Thrown',
  'pass longest completion': 'Longest Completion',
  'rush yds': 'Rushing Yards',
  'rush attempts': 'Rush Attempts',
  'rush longest': 'Longest Rush',
  'receptions': 'Receptions',
  'reception yds': 'Receiving Yards',
  'reception longest': 'Longest Reception',
  'anytime td': 'Anytime TD Scorer',
  'first td': 'First TD Scorer',
  'last td': 'Last TD Scorer',
  'kicking points': 'Kicking Points',
  'field goals': 'Field Goals Made',
  'tackles assists': 'Tackles + Assists',
  'sacks': 'Sacks',
  'interceptions': 'Interceptions',
  // NBA
  'points': 'Points',
  'rebounds': 'Rebounds',
  'assists': 'Assists',
  'threes': 'Three Pointers Made',
  'blocks': 'Blocks',
  'steals': 'Steals',
  'turnovers': 'Turnovers',
  'points rebounds assists': 'Pts + Reb + Ast',
  'points rebounds': 'Points + Rebounds',
  'points assists': 'Points + Assists',
  'rebounds assists': 'Rebounds + Assists',
  'double double': 'Double Double',
  'first basket': 'First Basket',
  // NHL
  'goals': 'Goals',
  'shots on goal': 'Shots on Goal',
  'power play points': 'Power Play Points',
  'blocked shots': 'Blocked Shots',
  'anytime goal': 'Anytime Goal Scorer',
  'goal scorer': 'Goal Scorer',
  // Soccer
  'goal scorer anytime': 'Anytime Goal Scorer',
  'shots': 'Shots',
};

function getEdgeColor(delta: number): string {
  if (delta >= 0.03) return 'text-emerald-400';
  if (delta >= 0.01) return 'text-emerald-300/70';
  if (delta <= -0.03) return 'text-red-400';
  if (delta <= -0.01) return 'text-red-300/70';
  return 'text-zinc-500';
}

function getEdgeBg(delta: number): string {
  if (delta >= 0.03) return 'bg-emerald-500/10 border-emerald-500/30';
  if (delta <= -0.03) return 'bg-red-500/10 border-red-500/30';
  return 'bg-zinc-800/50 border-zinc-700/50';
}

const formatEdge = (delta: number) => {
  const pct = (delta * 100).toFixed(1);
  return delta > 0 ? `+${pct}%` : `${pct}%`;
};

function MiniSparkline({ seed, value }: { seed: string; value: number }) {
  const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const data: number[] = [];
  let v = value;
  for (let i = 7; i >= 0; i--) {
    const x = Math.sin(hashSeed * (i + 1)) * 10000;
    const drift = (x - Math.floor(x) - 0.5) * 0.4;
    v = value + drift * ((8 - i) / 8) * 2;
    data.unshift(v);
  }
  data[data.length - 1] = value;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pathPoints = data.map((val, i) => `${(i / 7) * 28},${10 - ((val - min) / range) * 10}`).join(' ');
  const first = data[0];
  const last = data[data.length - 1];
  let color = '#71717a';
  if (last > first + 0.05) color = '#10b981';
  else if (last < first - 0.05) color = '#ef4444';
  return (<svg width="28" height="10" className="inline-block opacity-70"><polyline points={pathPoints} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>);
}

function generateMockLineData(seed: string, currentValue: number, isLine: boolean = false) {
  const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const points = 50;
  const data: { timestamp: Date; value: number }[] = [];
  const now = new Date();
  const startTime = new Date(now);
  startTime.setDate(startTime.getDate() - 7);
  const volatility = isLine ? 0.8 : 8;
  const driftScale = isLine ? 0.5 : 5;
  let value = currentValue;
  for (let i = 0; i < points; i++) {
    const x = Math.sin(hashSeed * (points - i)) * 10000;
    const drift = (x - Math.floor(x) - 0.5) * volatility;
    value = currentValue + drift * ((points - i) / points);
  }
  const openValue = isLine ? Math.round(value * 2) / 2 : Math.round(value);
  value = openValue;
  for (let i = 0; i <= points; i++) {
    const timestamp = new Date(startTime);
    timestamp.setHours(timestamp.getHours() + (i * (24 * 7) / points));
    const x = Math.sin(hashSeed * (i + 1)) * 10000;
    const drift = (x - Math.floor(x) - 0.5) * driftScale;
    const timeWeight = i / points;
    value = openValue + (currentValue - openValue) * timeWeight + drift * (1 - timeWeight * 0.5);
    const finalValue = isLine ? Math.round(value * 2) / 2 : Math.round(value);
    data.push({ timestamp, value: finalValue });
  }
  data[data.length - 1].value = currentValue;
  return { data, openValue };
}

function ChartModal({ seed, priceValue, label, lineValue, onClose }: { seed: string; priceValue: number; label: string; lineValue?: number; onClose: () => void }) {
  const hasLine = typeof lineValue === 'number' && !isNaN(lineValue);
  const chartValue = hasLine ? lineValue : priceValue;
  const isLineChart = hasLine;
  const { data, openValue } = generateMockLineData(seed, chartValue, isLineChart);
  const movement = chartValue - openValue;
  const values = data.map(d => d.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.1;
  const width = 500, height = 200, paddingLeft = 55, paddingRight = 20, paddingTop = 20, paddingBottom = 35;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  const points = values.map((val, i) => ({
    x: paddingLeft + (i / (values.length - 1)) * chartWidth,
    y: paddingTop + chartHeight - ((val - minVal + padding) / (range + 2 * padding)) * chartHeight,
    value: val
  }));
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const formatChartValue = (val: number) => isLineChart ? (val > 0 ? `+${val}` : val.toString()) : (val > 0 ? `+${val}` : val.toString());
  const yLabels = [{ value: maxVal, y: paddingTop }, { value: (maxVal + minVal) / 2, y: paddingTop + chartHeight / 2 }, { value: minVal, y: paddingTop + chartHeight }];
  const xLabels = [0, Math.floor(data.length / 2), data.length - 1].map(i => ({ x: points[i].x, label: data[i].timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }));
  const chartTitle = isLineChart ? `${label} - Line Movement` : `${label} - Price Movement`;
  const legendText = isLineChart ? 'line' : 'price';

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60" />
      <div className="relative bg-zinc-900 border border-zinc-700 rounded-xl p-5 w-full max-w-lg shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white rounded-lg transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
        <h3 className="text-lg font-semibold text-zinc-100 mb-1 pr-10">{chartTitle}</h3>
        {isLineChart && <p className="text-xs text-zinc-500 mb-3">Current price: {formatOdds(priceValue)}</p>}
        <div className="flex gap-8 mb-4">
          <div><span className="text-zinc-500 text-xs block mb-1">Open</span><span className="text-xl font-semibold text-zinc-300">{formatChartValue(openValue)}</span></div>
          <div><span className="text-zinc-500 text-xs block mb-1">Current</span><span className="text-xl font-semibold text-zinc-100">{formatChartValue(chartValue)}</span></div>
          <div><span className="text-zinc-500 text-xs block mb-1">Movement</span><span className={`text-xl font-semibold ${movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400'}`}>{movement > 0 ? '+' : ''}{isLineChart ? movement.toFixed(1) : movement.toFixed(0)}</span></div>
        </div>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          {yLabels.map((label, i) => (<g key={i}><line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#3f3f46" strokeWidth="1" strokeDasharray="4 4" /><text x={paddingLeft - 8} y={label.y + 4} textAnchor="end" fill="#71717a" fontSize="11">{formatChartValue(label.value)}</text></g>))}
          {xLabels.map((label, i) => (<text key={i} x={label.x} y={height - 10} textAnchor="middle" fill="#71717a" fontSize="11">{label.label}</text>))}
          <defs><linearGradient id={`modal-grad-${seed}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#10b981" stopOpacity="0.3" /><stop offset="100%" stopColor="#10b981" stopOpacity="0" /></linearGradient></defs>
          <path d={`${pathD} L ${points[points.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`} fill={`url(#modal-grad-${seed})`} />
          <path d={pathD} fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx={points[points.length - 1].x} cy={points[points.length - 1].y} r="5" fill="#10b981" stroke="#064e3b" strokeWidth="2" />
          <circle cx={points[0].x} cy={points[0].y} r="4" fill="#71717a" stroke="#3f3f46" strokeWidth="2" />
        </svg>
        <div className="flex items-center gap-4 mt-3 text-xs text-zinc-500">
          <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-zinc-500"></span><span>Opening {legendText}</span></div>
          <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-500"></span><span>Current {legendText}</span></div>
        </div>
      </div>
    </div>
  );
}

function MarketCell({ value, subValue, edge, seed, label, lineValue }: { value: string | number; subValue?: string; edge: number; seed: string; label: string; lineValue?: number }) {
  const { expandedId, setExpandedId } = useContext(ExpandedContext);
  const isExpanded = expandedId === seed;
  const priceValue = typeof value === 'string' ? parseFloat(value.replace(/[^-\d.]/g, '')) : value;
  return (
    <>
      <button onClick={() => setExpandedId(isExpanded ? null : seed)} className={`w-full text-center py-2 px-2 rounded border transition-all hover:brightness-110 cursor-pointer ${getEdgeBg(edge)} ${isExpanded ? 'ring-2 ring-emerald-500/50' : ''}`}>
        <div className="text-sm font-medium text-zinc-100">{value}</div>
        {subValue && <div className="text-xs text-zinc-400">{subValue}</div>}
        <div className="flex items-center justify-center gap-1 mt-0.5">
          <MiniSparkline seed={seed} value={edge} />
          <span className={`text-xs ${getEdgeColor(edge)}`}>{formatEdge(edge)}</span>
        </div>
      </button>
      {isExpanded && <ChartModal seed={seed} priceValue={priceValue} label={label} lineValue={lineValue} onClose={() => setExpandedId(null)} />}
    </>
  );
}

function MarketSection({ title, markets, homeTeam, awayTeam, gameId }: { title: string; markets: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  const id = gameId || `${homeTeam}-${awayTeam}`;
  if (!markets || (!markets.h2h && !markets.spreads && !markets.totals)) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{title}</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No {title.toLowerCase()} markets available</p></div></div>);
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{title}</h2></div>
      <div className="p-4">
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 mb-3">
          <div></div>
          <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Spread</div>
          <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">ML</div>
          <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Total</div>
        </div>
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 mb-3 items-center">
          <div className="font-medium text-zinc-100 text-sm">{awayTeam}</div>
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.away.line)} subValue={formatOdds(markets.spreads.away.price)} edge={markets.spreads.away.edge} seed={`${id}-${title}-sp-a`} label={`${awayTeam} Spread`} lineValue={markets.spreads.away.line} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.away.price)} edge={markets.h2h.away.edge} seed={`${id}-${title}-ml-a`} label={`${awayTeam} ML`} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`O ${markets.totals.line}`} subValue={formatOdds(markets.totals.over.price)} edge={markets.totals.over.edge} seed={`${id}-${title}-to-o`} label="Over" lineValue={markets.totals.line} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 items-center">
          <div className="font-medium text-zinc-100 text-sm">{homeTeam}</div>
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.home.line)} subValue={formatOdds(markets.spreads.home.price)} edge={markets.spreads.home.edge} seed={`${id}-${title}-sp-h`} label={`${homeTeam} Spread`} lineValue={markets.spreads.home.line} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.home.price)} edge={markets.h2h.home.edge} seed={`${id}-${title}-ml-h`} label={`${homeTeam} ML`} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`U ${markets.totals.line}`} subValue={formatOdds(markets.totals.under.price)} edge={markets.totals.under.edge} seed={`${id}-${title}-to-u`} label="Under" lineValue={markets.totals.line} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
      </div>
    </div>
  );
}

function TeamTotalsSection({ teamTotals, homeTeam, awayTeam, gameId }: { teamTotals: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  const id = gameId || `${homeTeam}-${awayTeam}`;
  if (!teamTotals) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Team Totals</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No team totals available</p></div></div>);
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Team Totals</h2></div>
      <div className="p-4 space-y-3">
        {teamTotals.away && (<div className="grid grid-cols-[1fr,100px,100px] gap-3 items-center"><div className="font-medium text-zinc-100 text-sm">{awayTeam} <span className="text-zinc-500">({teamTotals.away.line})</span></div><MarketCell value={formatOdds(teamTotals.away.over.price)} subValue="Over" edge={teamTotals.away.over.edge} seed={`${id}-tt-a-o`} label={`${awayTeam} Team Total`} lineValue={teamTotals.away.line} /><MarketCell value={formatOdds(teamTotals.away.under.price)} subValue="Under" edge={teamTotals.away.under.edge} seed={`${id}-tt-a-u`} label={`${awayTeam} Team Total`} lineValue={teamTotals.away.line} /></div>)}
        {teamTotals.home && (<div className="grid grid-cols-[1fr,100px,100px] gap-3 items-center"><div className="font-medium text-zinc-100 text-sm">{homeTeam} <span className="text-zinc-500">({teamTotals.home.line})</span></div><MarketCell value={formatOdds(teamTotals.home.over.price)} subValue="Over" edge={teamTotals.home.over.edge} seed={`${id}-tt-h-o`} label={`${homeTeam} Team Total`} lineValue={teamTotals.home.line} /><MarketCell value={formatOdds(teamTotals.home.under.price)} subValue="Under" edge={teamTotals.home.under.edge} seed={`${id}-tt-h-u`} label={`${homeTeam} Team Total`} lineValue={teamTotals.home.line} /></div>)}
      </div>
    </div>
  );
}

function PlayerPropsSection({ props, gameId }: { props: any[]; gameId?: string }) {
  if (!props || props.length === 0) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Player Props</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No player props available</p></div></div>);
  }
  const grouped = props.reduce((acc: any, prop: any) => { const key = prop.market; if (!acc[key]) acc[key] = []; acc[key].push(prop); return acc; }, {});
  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([market, marketProps]: [string, any]) => (
        <div key={market} className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{MARKET_LABELS[market] || market.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h2></div>
          <div className="p-4 space-y-2">
            {marketProps.map((prop: any, idx: number) => (
              <div key={idx} className="grid grid-cols-[1fr,100px,100px] gap-3 items-center py-2 border-b border-zinc-800/50 last:border-0">
                <div><div className="font-medium text-zinc-100 text-sm">{prop.player}</div>{prop.line !== null && prop.line !== undefined && <div className="text-xs text-zinc-500">Line: {prop.line}</div>}</div>
                {prop.over && prop.under ? (<><MarketCell value={formatOdds(prop.over.price)} subValue="Over" edge={prop.over.edge} seed={`${gameId}-${prop.player}-${market}-o`} label={`${prop.player} ${MARKET_LABELS[market] || market}`} lineValue={prop.line} /><MarketCell value={formatOdds(prop.under.price)} subValue="Under" edge={prop.under.edge} seed={`${gameId}-${prop.player}-${market}-u`} label={`${prop.player} ${MARKET_LABELS[market] || market}`} lineValue={prop.line} /></>) : prop.yes ? (<><MarketCell value={formatOdds(prop.yes.price)} edge={prop.yes.edge} seed={`${gameId}-${prop.player}-${market}-y`} label={prop.player} /><div></div></>) : null}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AlternatesSection({ alternates, homeTeam, awayTeam, gameId }: { alternates: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  if (!alternates || (alternates.spreads?.length === 0 && alternates.totals?.length === 0)) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Alternate Lines</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No alternate lines available</p></div></div>);
  }
  const homeSpreads = alternates.spreads?.filter((s: any) => s.team === homeTeam) || [];
  const awaySpreads = alternates.spreads?.filter((s: any) => s.team === awayTeam) || [];
  const overs = alternates.totals?.filter((t: any) => t.type === 'Over') || [];
  const unders = alternates.totals?.filter((t: any) => t.type === 'Under') || [];
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Alternate Lines</h2></div>
      <div className="p-4 space-y-6">
        {(homeSpreads.length > 0 || awaySpreads.length > 0) && (<div><h3 className="text-sm font-medium text-zinc-300 mb-3">Alternate Spreads</h3><div className="grid grid-cols-2 gap-4"><div><h4 className="text-xs text-zinc-500 mb-2">{homeTeam}</h4><div className="grid grid-cols-3 gap-2">{homeSpreads.slice(0, 12).map((s: any, idx: number) => (<MarketCell key={idx} value={formatSpread(s.line)} subValue={formatOdds(s.price)} edge={s.edge} seed={`${gameId}-alt-sp-h-${idx}`} label={`${homeTeam} Alt Spread`} lineValue={s.line} />))}</div></div><div><h4 className="text-xs text-zinc-500 mb-2">{awayTeam}</h4><div className="grid grid-cols-3 gap-2">{awaySpreads.slice(0, 12).map((s: any, idx: number) => (<MarketCell key={idx} value={formatSpread(s.line)} subValue={formatOdds(s.price)} edge={s.edge} seed={`${gameId}-alt-sp-a-${idx}`} label={`${awayTeam} Alt Spread`} lineValue={s.line} />))}</div></div></div></div>)}
        {(overs.length > 0 || unders.length > 0) && (<div><h3 className="text-sm font-medium text-zinc-300 mb-3">Alternate Totals</h3><div className="grid grid-cols-2 gap-4"><div><h4 className="text-xs text-zinc-500 mb-2">Over</h4><div className="grid grid-cols-3 gap-2">{overs.slice(0, 12).map((t: any, idx: number) => (<MarketCell key={idx} value={`O ${t.line}`} subValue={formatOdds(t.price)} edge={t.edge} seed={`${gameId}-alt-to-o-${idx}`} label={`Alt Total Over`} lineValue={t.line} />))}</div></div><div><h4 className="text-xs text-zinc-500 mb-2">Under</h4><div className="grid grid-cols-3 gap-2">{unders.slice(0, 12).map((t: any, idx: number) => (<MarketCell key={idx} value={`U ${t.line}`} subValue={formatOdds(t.price)} edge={t.edge} seed={`${gameId}-alt-to-u-${idx}`} label={`Alt Total Under`} lineValue={t.line} />))}</div></div></div></div>)}
      </div>
    </div>
  );
}

interface GameDetailClientProps {
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string };
  bookmakers: Record<string, any>;
  availableBooks: string[];
  availableTabs?: { fullGame?: boolean; firstHalf?: boolean; secondHalf?: boolean; q1?: boolean; q2?: boolean; q3?: boolean; q4?: boolean; p1?: boolean; p2?: boolean; p3?: boolean; props?: boolean; alternates?: boolean; teamTotals?: boolean };
}

export function GameDetailClient({ gameData, bookmakers, availableBooks, availableTabs }: GameDetailClientProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('full');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const priorityOrder = ['fanduel', 'draftkings', 'betmgm', 'williamhill_us', 'betrivers'];
  const sortedBooks = [...availableBooks].sort((a, b) => { const aIndex = priorityOrder.indexOf(a); const bIndex = priorityOrder.indexOf(b); if (aIndex === -1 && bIndex === -1) return 0; if (aIndex === -1) return 1; if (bIndex === -1) return -1; return aIndex - bIndex; });
  const [selectedBook, setSelectedBook] = useState(sortedBooks[0] || '');
  useEffect(() => { function handleClickOutside(event: MouseEvent) { if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) setIsOpen(false); } document.addEventListener('mousedown', handleClickOutside); return () => document.removeEventListener('mousedown', handleClickOutside); }, []);
  const selectedConfig = BOOK_CONFIG[selectedBook] || { name: selectedBook, color: '#6b7280' };
  const marketGroups = bookmakers[selectedBook]?.marketGroups || {};
  const BookIcon = ({ bookKey, size = 24 }: { bookKey: string; size?: number }) => { const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' }; const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2); return (<div className="rounded flex items-center justify-center font-bold text-white flex-shrink-0" style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}>{initials}</div>); };
  
  // Determine if NHL (use periods) or other sports (use quarters)
  const isNHL = gameData.sportKey.includes('icehockey');
  
  const tabs = [
    { key: 'full', label: 'Full Game', available: true },
    { key: '1h', label: '1st Half', available: availableTabs?.firstHalf },
    { key: '2h', label: '2nd Half', available: availableTabs?.secondHalf },
    // Quarters for NBA/NFL
    { key: '1q', label: '1Q', available: availableTabs?.q1 && !isNHL },
    { key: '2q', label: '2Q', available: availableTabs?.q2 && !isNHL },
    { key: '3q', label: '3Q', available: availableTabs?.q3 && !isNHL },
    { key: '4q', label: '4Q', available: availableTabs?.q4 && !isNHL },
    // Periods for NHL
    { key: '1p', label: '1P', available: availableTabs?.p1 && isNHL },
    { key: '2p', label: '2P', available: availableTabs?.p2 && isNHL },
    { key: '3p', label: '3P', available: availableTabs?.p3 && isNHL },
    { key: 'team', label: 'Team Totals', available: availableTabs?.teamTotals },
    { key: 'props', label: 'Player Props', available: availableTabs?.props },
    { key: 'alt', label: 'Alt Lines', available: availableTabs?.alternates },
  ].filter(tab => tab.available);

  return (
    <ExpandedContext.Provider value={{ expandedId, setExpandedId }}>
      <div>
        <div className="relative mb-6" ref={dropdownRef}>
          <button onClick={() => setIsOpen(!isOpen)} className="flex items-center gap-3 px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg hover:bg-zinc-700/70 transition-all min-w-[200px]">
            <BookIcon bookKey={selectedBook} size={28} />
            <span className="font-medium text-zinc-100">{selectedConfig.name}</span>
            <svg className={`w-4 h-4 text-zinc-400 ml-auto transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
          {isOpen && (<div className="absolute z-50 mt-2 w-64 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl overflow-hidden"><div className="max-h-80 overflow-y-auto">{sortedBooks.map((book) => { const config = BOOK_CONFIG[book] || { name: book, color: '#6b7280' }; const isSelected = book === selectedBook; return (<button key={book} onClick={() => { setSelectedBook(book); setIsOpen(false); }} className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all ${isSelected ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-700/50 text-zinc-300'}`}><BookIcon bookKey={book} size={28} /><span className="font-medium">{config.name}</span>{isSelected && (<svg className="w-4 h-4 ml-auto text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>)}</button>); })}</div></div>)}
        </div>
        {tabs.length > 1 && (<div className="flex gap-2 mb-6 overflow-x-auto pb-2">{tabs.map((tab) => (<button key={tab.key} onClick={() => setActiveTab(tab.key)} className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${activeTab === tab.key ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'}`}>{tab.label}</button>))}</div>)}
        {activeTab === 'full' && <MarketSection title="Full Game" markets={marketGroups.fullGame} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '1h' && <MarketSection title="1st Half" markets={marketGroups.firstHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '2h' && <MarketSection title="2nd Half" markets={marketGroups.secondHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '1q' && <MarketSection title="1st Quarter" markets={marketGroups.q1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '2q' && <MarketSection title="2nd Quarter" markets={marketGroups.q2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '3q' && <MarketSection title="3rd Quarter" markets={marketGroups.q3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '4q' && <MarketSection title="4th Quarter" markets={marketGroups.q4} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '1p' && <MarketSection title="1st Period" markets={marketGroups.p1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '2p' && <MarketSection title="2nd Period" markets={marketGroups.p2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === '3p' && <MarketSection title="3rd Period" markets={marketGroups.p3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === 'team' && <TeamTotalsSection teamTotals={marketGroups.teamTotals} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        {activeTab === 'props' && <PlayerPropsSection props={marketGroups.playerProps} gameId={gameData.id} />}
        {activeTab === 'alt' && <AlternatesSection alternates={marketGroups.alternates} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
      </div>
    </ExpandedContext.Provider>
  );
}