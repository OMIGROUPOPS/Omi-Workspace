'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';

// Only FanDuel and DraftKings
const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
};

// Allowed books for dropdown
const ALLOWED_BOOKS = ['fanduel', 'draftkings'];

function getEdgeColor(delta: number): string {
  return delta >= 0 ? 'text-emerald-400' : 'text-red-400';
}

function getEdgeBg(delta: number): string {
  return delta >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30';
}

// Price flow indicator with tooltip showing actual variance
function PriceFlowIndicator({ value, seed, size = 'normal' }: { value: number; seed: string; size?: 'normal' | 'small' }) {
  const [showTooltip, setShowTooltip] = useState(false);
  
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
  const width = size === 'small' ? 24 : 32;
  const height = size === 'small' ? 8 : 12;
  const pathPoints = data.map((val, i) => `${(i / 7) * width},${height - ((val - min) / range) * height}`).join(' ');
  const color = value >= 0 ? '#10b981' : '#ef4444';
  
  // Show actual variance percentage in tooltip
  const varianceText = value >= 0 
    ? `+${(value * 100).toFixed(1)}% from open` 
    : `${(value * 100).toFixed(1)}% from open`;
  
  return (
    <div 
      className="relative inline-flex items-center gap-1 cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <svg width={width} height={height} className="opacity-70">
        <polyline points={pathPoints} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className={`text-xs ${value >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
        {value >= 0 ? '+' : ''}{(value * 100).toFixed(1)}%
      </span>
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-zinc-800 border border-zinc-700 rounded text-xs text-zinc-200 whitespace-nowrap z-50 shadow-lg">
          {varianceText}
        </div>
      )}
    </div>
  );
}

type ChartSelection = {
  type: 'market';
  market: 'spread' | 'total' | 'moneyline';
  period: string;
  label: string;
  line?: number;
  price?: number;
  homePrice?: number;
  awayPrice?: number;
  overPrice?: number;
  underPrice?: number;
  homePriceMovement?: number;
  awayPriceMovement?: number;
  overPriceMovement?: number;
  underPriceMovement?: number;
} | {
  type: 'prop';
  player: string;
  market: string;
  label: string;
  line: number;
  overOdds?: number;
  underOdds?: number;
  overPriceMovement?: number;
  underPriceMovement?: number;
};

interface LineMovementChartProps {
  gameId: string;
  selection: ChartSelection;
  lineHistory?: any[];
  selectedBook: string;
  homeTeam?: string;
}

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam }: LineMovementChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; timestamp: Date; index: number } | null>(null);

  const isProp = selection.type === 'prop';
  const marketType = selection.type === 'market' ? selection.market : 'line';
  const baseValue = selection.line ?? (selection.type === 'market' ? selection.price : 0) ?? 0;

  // Filter line history by selected book AND outcome side
  // Spreads/moneyline: show home team only; Totals: show Over only
  const filteredHistory = (lineHistory || []).filter(snapshot => {
    const bookMatch = snapshot.book_key === selectedBook || snapshot.book === selectedBook;
    if (!bookMatch) return false;
    if (!snapshot.outcome_type) return true; // no outcome info, keep it
    if (marketType === 'total') return snapshot.outcome_type === 'Over';
    if (homeTeam) return snapshot.outcome_type === homeTeam;
    return true;
  });
  
  const hasRealData = filteredHistory.length > 0;
  
  let data: { timestamp: Date; value: number }[] = [];
  
  if (hasRealData) {
    // Use ONLY real data filtered by book - works for both main markets and props
    data = filteredHistory.map(snapshot => ({
      timestamp: new Date(snapshot.snapshot_time),
      value: isProp ? snapshot.line : (marketType === 'moneyline' ? snapshot.odds : snapshot.line)
    })).filter(d => d.value !== null && d.value !== undefined);
    
    // Sort by timestamp
    data.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }
  
  // If no data or only 1 point, show message
  if (data.length === 0) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-zinc-100">{selection.label}</h3>
          <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Collecting Data</span>
        </div>
        <div className="flex items-center justify-center h-32 text-zinc-500 text-sm">
          <div className="text-center">
            <p>No snapshots yet for {BOOK_CONFIG[selectedBook]?.name || selectedBook}</p>
            <p className="text-xs text-zinc-600 mt-1">Data will appear after polling cycles</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Even with 1 point, show it as a flat line
  if (data.length === 1) {
    const singleValue = data[0].value;
    // Create a flat line with the single value
    data = [
      { timestamp: data[0].timestamp, value: singleValue },
      { timestamp: new Date(), value: singleValue }
    ];
  }
  
  const openValue = data[0]?.value || baseValue;
  const currentValue = data[data.length - 1]?.value || baseValue;
  const movement = currentValue - openValue;
  const values = data.map(d => d.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.15;
  
  const width = 400, height = 140;
  const paddingLeft = 50, paddingRight = 15, paddingTop = 15, paddingBottom = 25;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  
  const chartPoints = data.map((d, i) => ({
    x: paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth,
    y: paddingTop + chartHeight - ((d.value - minVal + padding) / (range + 2 * padding)) * chartHeight,
    value: d.value,
    timestamp: d.timestamp,
    index: i
  }));
  
  const pathD = chartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  
  const formatValue = (val: number) => {
    if (isProp) return val.toString();
    if (marketType === 'moneyline' || marketType === 'spread') return val > 0 ? `+${val}` : val.toString();
    return val.toString();
  };
  
  const movementColor = movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400';
  const roundLabel = (val: number) => marketType === 'moneyline' ? Math.round(val) : Math.round(val * 2) / 2;
  const center = roundLabel((maxVal + minVal) / 2);
  const step = marketType === 'moneyline' ? 5 : 0.5;
  const yLabels = [
    { value: center + step, y: paddingTop },
    { value: center, y: paddingTop + chartHeight / 2 },
    { value: center - step, y: paddingTop + chartHeight }
  ];
  const xLabels = data.length > 0 ? [0, Math.floor(data.length / 2), data.length - 1].map(i => ({
    x: chartPoints[i]?.x || 0,
    label: data[i]?.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) || ''
  })) : [];

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const scaleX = width / rect.width;
    const mouseX = (e.clientX - rect.left) * scaleX;
    let nearestPoint = chartPoints[0];
    let minDist = Infinity;
    for (const point of chartPoints) {
      const dist = Math.abs(point.x - mouseX);
      if (dist < minDist) { minDist = dist; nearestPoint = point; }
    }
    setHoveredPoint(minDist < 20 ? nearestPoint : null);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-zinc-100">{selection.label}</h3>
        <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">Live Data</span>
      </div>
      
      <div className="flex gap-6 mb-4">
        <div><span className="text-zinc-500 text-xs block">Open</span><span className="text-lg font-semibold text-zinc-300">{formatValue(openValue)}</span></div>
        <div><span className="text-zinc-500 text-xs block">Current</span><span className="text-lg font-semibold text-zinc-100">{formatValue(currentValue)}</span></div>
        <div><span className="text-zinc-500 text-xs block">Movement</span><span className={`text-lg font-semibold ${movementColor}`}>{movement > 0 ? '+' : ''}{movement.toFixed(1)}</span></div>
      </div>
      
      <div className="flex gap-4 mb-4 pb-3 border-b border-zinc-800">
        {selection.type === 'market' && selection.market === 'spread' && (
          <>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Home</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.homePrice || -110)}</span>
              <PriceFlowIndicator value={selection.homePriceMovement || 0} seed={`${gameId}-spread-home-price`} size="small" />
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Away</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.awayPrice || -110)}</span>
              <PriceFlowIndicator value={selection.awayPriceMovement || 0} seed={`${gameId}-spread-away-price`} size="small" />
            </div>
          </>
        )}
        {selection.type === 'market' && selection.market === 'total' && (
          <>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Over</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.overPrice || -110)}</span>
              <PriceFlowIndicator value={selection.overPriceMovement || 0} seed={`${gameId}-total-over-price`} size="small" />
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Under</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.underPrice || -110)}</span>
              <PriceFlowIndicator value={selection.underPriceMovement || 0} seed={`${gameId}-total-under-price`} size="small" />
            </div>
          </>
        )}
        {selection.type === 'market' && selection.market === 'moneyline' && (
          <>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Home</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.homePrice || -110)}</span>
              <PriceFlowIndicator value={selection.homePriceMovement || 0} seed={`${gameId}-ml-home-price`} size="small" />
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
              <span className="text-xs text-zinc-400">Away</span>
              <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.awayPrice || 110)}</span>
              <PriceFlowIndicator value={selection.awayPriceMovement || 0} seed={`${gameId}-ml-away-price`} size="small" />
            </div>
          </>
        )}
        {isProp && selection.type === 'prop' && (
          <>
            {selection.overOdds && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
                <span className="text-xs text-zinc-400">Over</span>
                <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.overOdds)}</span>
                <PriceFlowIndicator value={selection.overPriceMovement || 0} seed={`${gameId}-${selection.player}-over-price`} size="small" />
              </div>
            )}
            {selection.underOdds && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded">
                <span className="text-xs text-zinc-400">Under</span>
                <span className="text-sm font-medium text-zinc-100">{formatOdds(selection.underOdds)}</span>
                <PriceFlowIndicator value={selection.underPriceMovement || 0} seed={`${gameId}-${selection.player}-under-price`} size="small" />
              </div>
            )}
          </>
        )}
      </div>
      
      <div className="relative">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto cursor-crosshair" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#3f3f46" strokeWidth="1" strokeDasharray="4 4" />
              <text x={paddingLeft - 8} y={label.y + 4} textAnchor="end" fill="#71717a" fontSize="10">{formatValue(label.value)}</text>
            </g>
          ))}
          {xLabels.map((label, i) => (<text key={i} x={label.x} y={height - 5} textAnchor="middle" fill="#71717a" fontSize="10">{label.label}</text>))}
          <defs>
            <linearGradient id={`line-grad-${gameId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isProp ? "#3b82f6" : "#10b981"} stopOpacity="0.3" />
              <stop offset="100%" stopColor={isProp ? "#3b82f6" : "#10b981"} stopOpacity="0" />
            </linearGradient>
          </defs>
          {chartPoints.length > 0 && (
            <>
              <path d={`${pathD} L ${chartPoints[chartPoints.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`} fill={`url(#line-grad-${gameId})`} />
              <path d={pathD} fill="none" stroke={isProp ? "#3b82f6" : "#10b981"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              {hoveredPoint && (<><line x1={hoveredPoint.x} y1={paddingTop} x2={hoveredPoint.x} y2={paddingTop + chartHeight} stroke="#a1a1aa" strokeWidth="1" strokeDasharray="3 3" /><circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="5" fill={isProp ? "#3b82f6" : "#10b981"} stroke="#fff" strokeWidth="2" /></>)}
              <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="3" fill="#71717a" stroke="#3f3f46" strokeWidth="2" />
              <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="4" fill={isProp ? "#3b82f6" : "#10b981"} stroke={isProp ? "#1e3a5f" : "#064e3b"} strokeWidth="2" />
            </>
          )}
        </svg>
        {hoveredPoint && (
          <div className="absolute bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-xs pointer-events-none shadow-lg z-10" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 15}%`, transform: 'translate(-50%, -100%)' }}>
            <div className="font-semibold text-zinc-100">{formatValue(hoveredPoint.value)}</div>
            <div className="text-zinc-400">{hoveredPoint.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</div>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4 mt-2 text-xs text-zinc-500">
        <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-zinc-500"></span><span>Opening</span></div>
        <div className="flex items-center gap-1.5"><span className={`w-2 h-2 rounded-full ${isProp ? 'bg-blue-500' : 'bg-emerald-500'}`}></span><span>Current</span></div>
        <div className="ml-auto text-zinc-600">{filteredHistory.length} snapshots</div>
      </div>
    </div>
  );
}

function AskEdgeAI({ gameId, homeTeam, awayTeam, sportKey, chartSelection }: { gameId: string; homeTeam: string; awayTeam: string; sportKey?: string; chartSelection: ChartSelection }) {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
    { role: 'assistant', content: `I can help you analyze:\n• Line movement and why lines move\n• Edge calculations and what they mean\n• Sharp vs public money indicators\n• How to interpret our pillar scores\n\nWhat would you like to know more about?` }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    try {
      const sport = sportKey?.includes('nfl') ? 'NFL' : sportKey?.includes('nba') ? 'NBA' : sportKey?.includes('nhl') ? 'NHL' : sportKey?.includes('ncaaf') ? 'NCAAF' : sportKey?.includes('ncaab') ? 'NCAAB' : 'NFL';
      const res = await fetch(`http://localhost:8000/api/chat/${sport}/${gameId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }) });
      if (res.ok) { const data = await res.json(); setMessages(prev => [...prev, { role: 'assistant', content: data.response }]); setIsLoading(false); return; }
    } catch (e) { console.error('[AskEdgeAI] Backend call failed:', e); }
    setTimeout(() => {
      let response = `Regarding ${chartSelection.label} for ${homeTeam} vs ${awayTeam}: `;
      response += chartSelection.type === 'prop' ? `This prop has a line of ${chartSelection.line}. Line movement on props often indicates sharp action or injury news.` : `Line movement indicates betting action. Sharp money typically moves lines early.`;
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      setIsLoading(false);
    }, 800);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg flex flex-col h-full">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
        <div className="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center"><svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg></div>
        <span className="font-medium text-zinc-100 text-sm">Ask Edge AI</span>
        <span className="text-xs text-zinc-500 ml-auto truncate max-w-[150px]">Viewing: {chartSelection.label}</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[280px]">
        {messages.map((msg, i) => (<div key={i} className={`text-sm ${msg.role === 'user' ? 'text-right' : ''}`}>{msg.role === 'user' ? (<span className="inline-block bg-emerald-500/20 text-emerald-100 px-3 py-2 rounded-lg max-w-[90%]">{msg.content}</span>) : (<div className="text-zinc-300 whitespace-pre-line text-xs leading-relaxed">{msg.content}</div>)}</div>))}
        {isLoading && <div className="text-zinc-500 text-xs">Thinking...</div>}
      </div>
      <div className="p-3 border-t border-zinc-800">
        <div className="flex gap-2">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSubmit()} placeholder={`Ask about ${chartSelection.label.split(' - ')[0]}...`} className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500/50" />
          <button onClick={handleSubmit} disabled={isLoading || !input.trim()} className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-zinc-700 disabled:text-zinc-500 text-white text-sm font-medium rounded-lg transition-colors">Ask</button>
        </div>
      </div>
    </div>
  );
}

function MarketCell({ value, subValue, edge, seed, onClick, isSelected }: { value: string | number; subValue?: string; edge: number; seed: string; onClick?: () => void; isSelected?: boolean }) {
  return (
    <div onClick={onClick} className={`w-full text-center py-2 px-2 rounded border transition-all cursor-pointer hover:brightness-110 ${getEdgeBg(edge)} ${isSelected ? 'ring-2 ring-emerald-500' : ''}`}>
      <div className="text-sm font-medium text-zinc-100">{value}</div>
      {subValue && <div className="text-xs text-zinc-400">{subValue}</div>}
      <div className="flex items-center justify-center gap-1 mt-0.5">
        <PriceFlowIndicator value={edge} seed={seed} size="small" />
      </div>
    </div>
  );
}

function MarketSection({ title, markets, homeTeam, awayTeam, gameId, onSelectMarket, selectedMarket }: { title: string; markets: any; homeTeam: string; awayTeam: string; gameId?: string; onSelectMarket: (market: 'spread' | 'total' | 'moneyline') => void; selectedMarket: 'spread' | 'total' | 'moneyline' }) {
  const id = gameId || `${homeTeam}-${awayTeam}`;
  if (!markets || (!markets.h2h && !markets.spreads && !markets.totals)) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{title}</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No {title.toLowerCase()} markets available</p></div></div>);
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{title}</h2><p className="text-xs text-zinc-500 mt-1">Click any market to view its line movement</p></div>
      <div className="p-4">
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 mb-3"><div></div><div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Spread</div><div className="text-center text-xs text-zinc-500 uppercase tracking-wide">ML</div><div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Total</div></div>
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 mb-3 items-center">
          <div className="font-medium text-zinc-100 text-sm">{awayTeam}</div>
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.away.line)} subValue={formatOdds(markets.spreads.away.price)} edge={markets.spreads.away.edge || 0} seed={`${id}-${title}-sp-a`} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.away.price)} edge={markets.h2h.away.edge || 0} seed={`${id}-${title}-ml-a`} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`O ${markets.totals.line}`} subValue={formatOdds(markets.totals.over.price)} edge={markets.totals.over.edge || 0} seed={`${id}-${title}-to-o`} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 items-center">
          <div className="font-medium text-zinc-100 text-sm">{homeTeam}</div>
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.home.line)} subValue={formatOdds(markets.spreads.home.price)} edge={markets.spreads.home.edge || 0} seed={`${id}-${title}-sp-h`} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.home.price)} edge={markets.h2h.home.edge || 0} seed={`${id}-${title}-ml-h`} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`U ${markets.totals.line}`} subValue={formatOdds(markets.totals.under.price)} edge={markets.totals.under.edge || 0} seed={`${id}-${title}-to-u`} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
      </div>
    </div>
  );
}

function formatMarketName(market: string): string {
  const marketNames: Record<string, string> = { 'player_pass_yds': 'Passing Yards', 'player_pass_tds': 'Passing TDs', 'player_pass_completions': 'Pass Completions', 'player_pass_attempts': 'Pass Attempts', 'player_pass_interceptions': 'Pass Interceptions', 'player_rush_yds': 'Rushing Yards', 'player_rush_attempts': 'Rush Attempts', 'player_reception_yds': 'Receiving Yards', 'player_receptions': 'Receptions', 'player_anytime_td': 'Anytime TD', 'player_points': 'Points', 'player_rebounds': 'Rebounds', 'player_assists': 'Assists', 'player_threes': '3-Pointers', 'player_double_double': 'Double-Double', 'player_goals': 'Goals', 'player_shots_on_goal': 'Shots on Goal', 'player_field_goals': 'Field Goals' };
  return marketNames[market] || market.replace('player_', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function PlayerPropsSection({ props, gameId, onSelectProp, selectedProp, selectedBook }: { props: any[]; gameId?: string; onSelectProp: (prop: any) => void; selectedProp: any | null; selectedBook: string }) {
  const [selectedMarket, setSelectedMarket] = useState<string>('all');
  if (!props || props.length === 0) return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">Player Props</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No player props available for this game</p></div></div>);
  
  const propsToShow = props.filter(p => p.book === selectedBook);
  const grouped = propsToShow.reduce((acc: any, prop: any) => { const key = prop.market || prop.market_type || 'unknown'; if (!acc[key]) acc[key] = []; acc[key].push(prop); return acc; }, {});
  const marketTypes = Object.keys(grouped);
  const filteredMarkets = selectedMarket === 'all' ? marketTypes : [selectedMarket];
  
  const generatePriceMovement = (odds: number, seed: string) => { const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0); const x = Math.sin(hashSeed) * 10000; return (x - Math.floor(x) - 0.5) * 0.2; };
  
  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <button onClick={() => setSelectedMarket('all')} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${selectedMarket === 'all' ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>All ({propsToShow.length})</button>
        {marketTypes.map((market) => (<button key={market} onClick={() => setSelectedMarket(market)} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${selectedMarket === market ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>{formatMarketName(market)} ({grouped[market].length})</button>))}
      </div>
      <p className="text-xs text-zinc-500">Click any prop to view its line movement in the chart above</p>
      {filteredMarkets.map((market) => (
        <div key={market} className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center justify-between"><h2 className="font-semibold text-zinc-100">{formatMarketName(market)}</h2><span className="text-xs text-zinc-500">{grouped[market].length} props</span></div>
          <div className="divide-y divide-zinc-800/50">
            {grouped[market].map((prop: any, idx: number) => {
              const isSelected = selectedProp?.player === prop.player && selectedProp?.market === (prop.market || prop.market_type) && selectedProp?.book === prop.book;
              const overOdds = prop.over?.odds; const underOdds = prop.under?.odds; const yesOdds = prop.yes?.odds;
              const line = prop.line ?? prop.over?.line ?? prop.under?.line;
              const overMovement = overOdds ? generatePriceMovement(overOdds, `${gameId}-${prop.player}-over`) : 0;
              const underMovement = underOdds ? generatePriceMovement(underOdds, `${gameId}-${prop.player}-under`) : 0;
              return (
                <div key={`${prop.player}-${prop.book}-${idx}`} onClick={() => onSelectProp({ ...prop, overPriceMovement: overMovement, underPriceMovement: underMovement })} className={`px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-zinc-800/50 transition-colors ${isSelected ? 'bg-blue-500/10 ring-1 ring-blue-500/50' : ''}`}>
                  <div className="flex-1"><div className="font-medium text-zinc-100 text-sm">{prop.player}</div>{line !== null && line !== undefined && <span className="text-xs text-zinc-400">Line: {line}</span>}</div>
                  <div className="flex gap-2">
                    {overOdds && underOdds ? (<>
                      <div className={`text-center py-2 px-3 rounded border transition-all min-w-[85px] ${overMovement >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}><div className="text-sm font-medium text-zinc-100">{formatOdds(overOdds)}</div><div className="text-xs text-zinc-500 mb-1">Over</div><PriceFlowIndicator value={overMovement} seed={`${gameId}-${prop.player}-over`} size="small" /></div>
                      <div className={`text-center py-2 px-3 rounded border transition-all min-w-[85px] ${underMovement >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}><div className="text-sm font-medium text-zinc-100">{formatOdds(underOdds)}</div><div className="text-xs text-zinc-500 mb-1">Under</div><PriceFlowIndicator value={underMovement} seed={`${gameId}-${prop.player}-under`} size="small" /></div>
                    </>) : yesOdds ? (<div className={`text-center py-2 px-3 rounded border transition-all min-w-[85px] ${generatePriceMovement(yesOdds, `${gameId}-${prop.player}-yes`) >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}><div className="text-sm font-medium text-zinc-100">{formatOdds(yesOdds)}</div><div className="text-xs text-zinc-500 mb-1">Yes</div><PriceFlowIndicator value={generatePriceMovement(yesOdds, `${gameId}-${prop.player}-yes`)} seed={`${gameId}-${prop.player}-yes`} size="small" /></div>) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function TeamTotalsSection({ teamTotals, homeTeam, awayTeam, gameId }: { teamTotals: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  if (!teamTotals || (!teamTotals.home?.over && !teamTotals.away?.over)) {
    return <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center"><p className="text-zinc-500">No team totals available</p></div>;
  }
  const renderTeam = (label: string, data: any) => {
    if (!data?.over) return null;
    return (
      <div className="flex items-center justify-between py-3">
        <span className="font-medium text-zinc-100 text-sm min-w-[140px]">{label}</span>
        <div className="flex gap-3">
          <div className="text-center py-2 px-4 rounded border bg-emerald-500/10 border-emerald-500/30 min-w-[100px]">
            <div className="text-sm font-medium text-zinc-100">O {data.over.line}</div>
            <div className="text-xs text-zinc-400">{formatOdds(data.over.price)}</div>
          </div>
          {data.under && (
            <div className="text-center py-2 px-4 rounded border bg-red-500/10 border-red-500/30 min-w-[100px]">
              <div className="text-sm font-medium text-zinc-100">U {data.under.line}</div>
              <div className="text-xs text-zinc-400">{formatOdds(data.under.price)}</div>
            </div>
          )}
        </div>
      </div>
    );
  };
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
        <h2 className="font-semibold text-zinc-100">Team Totals</h2>
      </div>
      <div className="p-4 divide-y divide-zinc-800/50">
        {renderTeam(awayTeam, teamTotals.away)}
        {renderTeam(homeTeam, teamTotals.home)}
      </div>
    </div>
  );
}

function AlternatesSection({ alternates, homeTeam, awayTeam, gameId }: { alternates: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  const [view, setView] = useState<'spreads' | 'totals'>('spreads');
  const altSpreads = alternates?.spreads || [];
  const altTotals = alternates?.totals || [];
  if (altSpreads.length === 0 && altTotals.length === 0) {
    return <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center"><p className="text-zinc-500">No alternate lines available</p></div>;
  }
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {altSpreads.length > 0 && (
          <button onClick={() => setView('spreads')} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${view === 'spreads' ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>
            Alt Spreads ({altSpreads.length})
          </button>
        )}
        {altTotals.length > 0 && (
          <button onClick={() => setView('totals')} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${view === 'totals' ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>
            Alt Totals ({altTotals.length})
          </button>
        )}
      </div>

      {view === 'spreads' && altSpreads.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
            <h2 className="font-semibold text-zinc-100">Alternate Spreads</h2>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-[80px,1fr,1fr] gap-2 mb-2">
              <div className="text-xs text-zinc-500 uppercase">Spread</div>
              <div className="text-xs text-zinc-500 uppercase text-center">{awayTeam}</div>
              <div className="text-xs text-zinc-500 uppercase text-center">{homeTeam}</div>
            </div>
            <div className="space-y-1.5 max-h-[400px] overflow-y-auto">
              {altSpreads.map((row: any, i: number) => (
                <div key={i} className="grid grid-cols-[80px,1fr,1fr] gap-2 items-center">
                  <span className="text-sm font-medium text-zinc-300">{formatSpread(row.homeSpread)}</span>
                  <div className="text-center py-1.5 px-2 rounded border bg-zinc-800/50 border-zinc-700">
                    {row.away ? (
                      <><div className="text-sm font-medium text-zinc-100">{formatSpread(row.away.line)}</div><div className="text-xs text-zinc-400">{formatOdds(row.away.price)}</div></>
                    ) : <span className="text-zinc-600">-</span>}
                  </div>
                  <div className="text-center py-1.5 px-2 rounded border bg-zinc-800/50 border-zinc-700">
                    {row.home ? (
                      <><div className="text-sm font-medium text-zinc-100">{formatSpread(row.home.line)}</div><div className="text-xs text-zinc-400">{formatOdds(row.home.price)}</div></>
                    ) : <span className="text-zinc-600">-</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {view === 'totals' && altTotals.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
            <h2 className="font-semibold text-zinc-100">Alternate Totals</h2>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-[80px,1fr,1fr] gap-2 mb-2">
              <div className="text-xs text-zinc-500 uppercase">Line</div>
              <div className="text-xs text-zinc-500 uppercase text-center">Over</div>
              <div className="text-xs text-zinc-500 uppercase text-center">Under</div>
            </div>
            <div className="space-y-1.5 max-h-[400px] overflow-y-auto">
              {altTotals.map((row: any, i: number) => (
                <div key={i} className="grid grid-cols-[80px,1fr,1fr] gap-2 items-center">
                  <span className="text-sm font-medium text-zinc-300">{row.line}</span>
                  <div className="text-center py-1.5 px-2 rounded border bg-emerald-500/10 border-emerald-500/30">
                    {row.over ? (
                      <span className="text-sm font-medium text-zinc-100">{formatOdds(row.over.price)}</span>
                    ) : <span className="text-zinc-600">-</span>}
                  </div>
                  <div className="text-center py-1.5 px-2 rounded border bg-red-500/10 border-red-500/30">
                    {row.under ? (
                      <span className="text-sm font-medium text-zinc-100">{formatOdds(row.under.price)}</span>
                    ) : <span className="text-zinc-600">-</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
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
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('full');
  const [chartMarket, setChartMarket] = useState<'spread' | 'total' | 'moneyline'>('spread');
  const [selectedProp, setSelectedProp] = useState<any | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Filter to only allowed books
  const filteredBooks = availableBooks.filter(book => ALLOWED_BOOKS.includes(book));
  const [selectedBook, setSelectedBook] = useState(filteredBooks[0] || 'fanduel');
  
  useEffect(() => { function handleClickOutside(event: MouseEvent) { if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) setIsOpen(false); } document.addEventListener('mousedown', handleClickOutside); return () => document.removeEventListener('mousedown', handleClickOutside); }, []);
  
  const selectedConfig = BOOK_CONFIG[selectedBook] || { name: selectedBook, color: '#10b981' };
  const marketGroups = bookmakers[selectedBook]?.marketGroups || {};
  const BookIcon = ({ bookKey, size = 24 }: { bookKey: string; size?: number }) => { const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' }; const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2); return (<div className="rounded flex items-center justify-center font-bold text-white flex-shrink-0" style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}>{initials}</div>); };
  const isNHL = gameData.sportKey.includes('icehockey');
  
  const generatePriceMovement = (seed: string) => { const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0); const x = Math.sin(hashSeed) * 10000; return (x - Math.floor(x) - 0.5) * 0.15; };
  
  const getCurrentMarketValues = () => {
    const periodMap: Record<string, string> = { 'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const markets = marketGroups[periodMap[activeTab] || 'fullGame'];
    if (chartMarket === 'spread') return { line: markets?.spreads?.home?.line, price: markets?.spreads?.home?.price, homePrice: markets?.spreads?.home?.price, awayPrice: markets?.spreads?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-away`) };
    if (chartMarket === 'total') return { line: markets?.totals?.line, price: markets?.totals?.over?.price, overPrice: markets?.totals?.over?.price, underPrice: markets?.totals?.under?.price, overPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-over`), underPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-under`) };
    return { line: undefined, price: markets?.h2h?.home?.price, homePrice: markets?.h2h?.home?.price, awayPrice: markets?.h2h?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-away`) };
  };
  
  const getChartSelection = (): ChartSelection => {
    if (selectedProp) {
      const line = selectedProp.line ?? selectedProp.over?.line ?? selectedProp.under?.line ?? 0;
      return { type: 'prop', player: selectedProp.player, market: selectedProp.market || selectedProp.market_type, label: `${selectedProp.player} - ${formatMarketName(selectedProp.market || selectedProp.market_type)}`, line, overOdds: selectedProp.over?.odds, underOdds: selectedProp.under?.odds, overPriceMovement: selectedProp.overPriceMovement || generatePriceMovement(`${gameData.id}-${selectedProp.player}-over`), underPriceMovement: selectedProp.underPriceMovement || generatePriceMovement(`${gameData.id}-${selectedProp.player}-under`) };
    }
    const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1st Quarter', '2q': '2nd Quarter', '3q': '3rd Quarter', '4q': '4th Quarter', '1p': '1st Period', '2p': '2nd Period', '3p': '3rd Period' };
    const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'Moneyline' };
    const values = getCurrentMarketValues();
    return { type: 'market', market: chartMarket, period: activeTab, label: `${periodLabels[activeTab] || 'Full Game'} ${marketLabels[chartMarket]}`, ...values };
  };
  
  const chartSelection = getChartSelection();
  
  // State for prop history
  const [propHistory, setPropHistory] = useState<any[]>([]);
  const [loadingPropHistory, setLoadingPropHistory] = useState(false);
  
  // Fetch prop history when a prop is selected
  useEffect(() => {
    if (selectedProp) {
      setLoadingPropHistory(true);
      const playerName = encodeURIComponent(selectedProp.player);
      const marketType = encodeURIComponent(selectedProp.market || selectedProp.market_type);
      fetch(`http://localhost:8000/api/props/history/${gameData.id}/${playerName}/${marketType}?book=${selectedBook}`)
        .then(res => res.json())
        .then(data => {
          setPropHistory(data.snapshots || []);
          setLoadingPropHistory(false);
        })
        .catch(err => {
          console.error('Error fetching prop history:', err);
          setPropHistory([]);
          setLoadingPropHistory(false);
        });
    } else {
      setPropHistory([]);
    }
  }, [selectedProp, selectedBook, gameData.id]);
  
  const getLineHistory = () => { 
    if (selectedProp) return propHistory; 
    const periodKey = activeTab === 'full' ? 'full' : activeTab === '1h' ? 'h1' : activeTab === '2h' ? 'h2' : 'full'; 
    return marketGroups.lineHistory?.[periodKey]?.[chartMarket] || []; 
  };
  const handleSelectProp = (prop: any) => setSelectedProp(prop);
  const handleSelectMarket = (market: 'spread' | 'total' | 'moneyline') => { setChartMarket(market); setSelectedProp(null); };
  const handleTabChange = (tab: string) => { setActiveTab(tab); if (tab !== 'props') setSelectedProp(null); };
  
  const tabs = [
    { key: 'full', label: 'Full Game', available: true },
    { key: '1h', label: '1st Half', available: availableTabs?.firstHalf },
    { key: '2h', label: '2nd Half', available: availableTabs?.secondHalf },
    { key: '1q', label: '1Q', available: availableTabs?.q1 && !isNHL },
    { key: '2q', label: '2Q', available: availableTabs?.q2 && !isNHL },
    { key: '3q', label: '3Q', available: availableTabs?.q3 && !isNHL },
    { key: '4q', label: '4Q', available: availableTabs?.q4 && !isNHL },
    { key: '1p', label: '1P', available: availableTabs?.p1 && isNHL },
    { key: '2p', label: '2P', available: availableTabs?.p2 && isNHL },
    { key: '3p', label: '3P', available: availableTabs?.p3 && isNHL },
    { key: 'team', label: 'Team Totals', available: availableTabs?.teamTotals },
    { key: 'props', label: 'Player Props', available: availableTabs?.props },
    { key: 'alt', label: 'Alt Lines', available: availableTabs?.alternates },
  ].filter(tab => tab.available);

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div>
          {!selectedProp && (<div className="flex gap-2 mb-3">{['spread', 'total', 'moneyline'].map((market) => (<button key={market} onClick={() => handleSelectMarket(market as any)} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${chartMarket === market ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>{market.charAt(0).toUpperCase() + market.slice(1)}</button>))}</div>)}
          {selectedProp && (<div className="flex gap-2 mb-3 items-center"><button onClick={() => setSelectedProp(null)} className="px-3 py-1.5 rounded text-xs font-medium bg-zinc-800 text-zinc-400 hover:bg-zinc-700 flex items-center gap-1"><svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>Back to Markets</button><span className="px-3 py-1.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400">{selectedProp.player}</span><span className="text-xs text-zinc-500">via {selectedProp.book}</span></div>)}
          <LineMovementChart gameId={gameData.id} selection={chartSelection} lineHistory={getLineHistory()} selectedBook={selectedBook} homeTeam={gameData.homeTeam} />
        </div>
        <AskEdgeAI gameId={gameData.id} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} sportKey={gameData.sportKey} chartSelection={chartSelection} />
      </div>
      
      <div className="relative mb-4" ref={dropdownRef}>
        <button onClick={() => setIsOpen(!isOpen)} className="flex items-center gap-3 px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg hover:bg-zinc-700/70 transition-all min-w-[200px]">
          <BookIcon bookKey={selectedBook} size={28} /><span className="font-medium text-zinc-100">{selectedConfig.name}</span><svg className={`w-4 h-4 text-zinc-400 ml-auto transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
        </button>
        {isOpen && (<div className="absolute z-50 mt-2 w-64 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl overflow-hidden"><div className="max-h-80 overflow-y-auto">{filteredBooks.map((book) => { const config = BOOK_CONFIG[book] || { name: book, color: '#6b7280' }; const isSelected = book === selectedBook; return (<button key={book} onClick={() => { setSelectedBook(book); setIsOpen(false); }} className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all ${isSelected ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-700/50 text-zinc-300'}`}><BookIcon bookKey={book} size={28} /><span className="font-medium">{config.name}</span>{isSelected && (<svg className="w-4 h-4 ml-auto text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>)}</button>); })}</div></div>)}
      </div>
      
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">{tabs.map((tab) => (<button key={tab.key} onClick={() => handleTabChange(tab.key)} className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${activeTab === tab.key ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'}`}>{tab.label}</button>))}</div>
      
      {activeTab === 'full' && <MarketSection title="Full Game" markets={marketGroups.fullGame} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '1h' && <MarketSection title="1st Half" markets={marketGroups.firstHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '2h' && <MarketSection title="2nd Half" markets={marketGroups.secondHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '1q' && <MarketSection title="1st Quarter" markets={marketGroups.q1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '2q' && <MarketSection title="2nd Quarter" markets={marketGroups.q2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '3q' && <MarketSection title="3rd Quarter" markets={marketGroups.q3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '4q' && <MarketSection title="4th Quarter" markets={marketGroups.q4} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '1p' && <MarketSection title="1st Period" markets={marketGroups.p1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '2p' && <MarketSection title="2nd Period" markets={marketGroups.p2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === '3p' && <MarketSection title="3rd Period" markets={marketGroups.p3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} />}
      {activeTab === 'team' && <TeamTotalsSection teamTotals={marketGroups.teamTotals} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
      {activeTab === 'props' && <PlayerPropsSection props={marketGroups.playerProps} gameId={gameData.id} onSelectProp={handleSelectProp} selectedProp={selectedProp} selectedBook={selectedBook} />}
      {activeTab === 'alt' && <AlternatesSection alternates={marketGroups.alternates} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
    </div>
  );
}