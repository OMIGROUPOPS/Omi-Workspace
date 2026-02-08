'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread, calculateTwoWayEV, formatEV, getEVColor, getEVBgClass } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal } from '@/lib/edge/engine/edgescout';

// ============================================================================
// Constants
// ============================================================================

const BOOK_CONFIG: Record<string, { name: string; color: string; type: 'sportsbook' | 'exchange' }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff', type: 'sportsbook' },
  'draftkings': { name: 'DraftKings', color: '#53d337', type: 'sportsbook' },
  'kalshi': { name: 'Kalshi', color: '#0ea5e9', type: 'exchange' },
  'polymarket': { name: 'Polymarket', color: '#8b5cf6', type: 'exchange' },
};

const ALLOWED_BOOKS = ['fanduel', 'draftkings', 'kalshi', 'polymarket'];

// ============================================================================
// Types
// ============================================================================

type ChartViewMode = 'line' | 'price';
type TimeRange = '30M' | '1H' | '3H' | '6H' | '24H' | 'ALL';

type ChartSelection = {
  type: 'market';
  market: 'spread' | 'total' | 'moneyline';
  period: string;
  label: string;
  line?: number;
  homeLine?: number;
  awayLine?: number;
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

type CEQByPeriod = {
  fullGame?: GameCEQ | null;
  firstHalf?: GameCEQ | null;
  secondHalf?: GameCEQ | null;
  q1?: GameCEQ | null;
  q2?: GameCEQ | null;
  q3?: GameCEQ | null;
  q4?: GameCEQ | null;
  p1?: GameCEQ | null;
  p2?: GameCEQ | null;
  p3?: GameCEQ | null;
};

interface EdgeCountBreakdown {
  total: number;
  fullGame: number;
  firstHalf: number;
  secondHalf: number;
  quarters: number;
  periods: number;
  teamTotals: number;
}

interface GameDetailClientProps {
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string; commenceTime?: string };
  bookmakers: Record<string, any>;
  availableBooks: string[];
  availableTabs?: { fullGame?: boolean; firstHalf?: boolean; secondHalf?: boolean; q1?: boolean; q2?: boolean; q3?: boolean; q4?: boolean; p1?: boolean; p2?: boolean; p3?: boolean; alternates?: boolean; teamTotals?: boolean };
  userTier?: 'tier_1' | 'tier_2';
  userEmail?: string;
  isDemo?: boolean;
  ceq?: GameCEQ | null;
  ceqByPeriod?: CEQByPeriod;
  teamTotalsCeq?: { home: GameCEQ | null; away: GameCEQ | null } | null;
  edgeCountBreakdown?: EdgeCountBreakdown;
  pythonPillarScores?: PythonPillarScores | null;
  totalEdgeCount?: number;
}

// ============================================================================
// LineMovementChart (kept, modified with compact prop)
// ============================================================================

interface LineMovementChartProps {
  gameId: string;
  selection: ChartSelection;
  lineHistory?: any[];
  selectedBook: string;
  homeTeam?: string;
  awayTeam?: string;
  viewMode: ChartViewMode;
  onViewModeChange: (mode: ChartViewMode) => void;
  commenceTime?: string;
  sportKey?: string;
  compact?: boolean;
}

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam, awayTeam, viewMode, onViewModeChange, commenceTime, sportKey, compact = false }: LineMovementChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; timestamp: Date; index: number } | null>(null);
  const [trackingSide, setTrackingSide] = useState<'home' | 'away' | 'over' | 'under' | 'draw'>('home');
  const isSoccer = sportKey?.includes('soccer') ?? false;
  const [timeRange, setTimeRange] = useState<TimeRange>('ALL');

  const isProp = selection.type === 'prop';
  const marketType = selection.type === 'market' ? selection.market : 'line';

  const getDisplayLine = () => {
    if (selection.type === 'prop') return selection.line;
    if (marketType === 'spread') {
      return trackingSide === 'away' ? selection.awayLine : selection.homeLine;
    }
    return selection.line;
  };
  const displayLine = getDisplayLine();
  const baseValue = displayLine ?? (selection.type === 'market' ? selection.price : 0) ?? 0;
  const isGameLive = commenceTime ? checkGameLive(commenceTime) : false;
  const effectiveViewMode = marketType === 'moneyline' ? 'line' : viewMode;

  const getOutcomeFilter = () => {
    if (marketType === 'total') return trackingSide === 'under' ? 'Under' : 'Over';
    if (trackingSide === 'draw') return 'Draw';
    if (trackingSide === 'away' && awayTeam) return awayTeam;
    return homeTeam;
  };

  const filteredHistory = (lineHistory || []).filter(snapshot => {
    const bookMatch = snapshot.book_key === selectedBook || snapshot.book === selectedBook;
    if (!bookMatch) return false;
    const targetOutcome = getOutcomeFilter();
    if (!snapshot.outcome_type) {
      if (marketType === 'spread' || marketType === 'total') return true;
      if (marketType === 'moneyline') return trackingSide === 'home';
      return true;
    }
    if (!targetOutcome) return true;
    const outcomeType = snapshot.outcome_type.toLowerCase();
    const target = targetOutcome.toLowerCase();
    if (target === 'over' || target === 'under') return outcomeType === target;
    if (outcomeType === 'home' || outcomeType === 'away') return outcomeType === trackingSide;
    if (outcomeType === target) return true;
    if (outcomeType.includes(target) || target.includes(outcomeType)) return true;
    const outcomeLast = outcomeType.split(/\s+/).pop();
    const targetLast = target.split(/\s+/).pop();
    if (outcomeLast === targetLast) return true;
    return false;
  });

  const hasRealData = filteredHistory.length > 0;
  let data: { timestamp: Date; value: number }[] = [];

  if (hasRealData) {
    data = filteredHistory.map(snapshot => {
      let value: number;
      if (effectiveViewMode === 'price') { value = snapshot.odds; }
      else if (isProp) { value = snapshot.line; }
      else if (marketType === 'moneyline') { value = snapshot.odds; }
      else if (marketType === 'spread') {
        if (snapshot.outcome_type) { value = snapshot.line; }
        else { value = trackingSide === 'away' ? (snapshot.line * -1) : snapshot.line; }
      } else { value = snapshot.line; }
      return { timestamp: new Date(snapshot.snapshot_time), value };
    }).filter(d => d.value !== null && d.value !== undefined);
    data.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    if (timeRange !== 'ALL' && data.length > 0) {
      const now = new Date();
      const hoursMap: Record<TimeRange, number> = { '30M': 0.5, '1H': 1, '3H': 3, '6H': 6, '24H': 24, 'ALL': 0 };
      const cutoffTime = new Date(now.getTime() - hoursMap[timeRange] * 60 * 60 * 1000);
      data = data.filter(d => d.timestamp >= cutoffTime);
    }
  }

  const isFilteredEmpty = hasRealData && filteredHistory.length > 0 && data.length === 0;

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-500 text-[11px]">
        {isFilteredEmpty ? 'No data in range' : `No snapshots for ${BOOK_CONFIG[selectedBook]?.name || selectedBook}`}
      </div>
    );
  }

  if (data.length === 1) {
    data = [data[0], { timestamp: new Date(), value: data[0].value }];
  }

  const openValue = data[0]?.value || baseValue;
  const currentValue = data[data.length - 1]?.value || baseValue;
  const movement = currentValue - openValue;
  const values = data.map(d => d.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.1;

  // Compact chart dimensions
  const width = 400;
  const height = compact ? 100 : 180;
  const paddingLeft = compact ? 35 : 45;
  const paddingRight = 8;
  const paddingTop = compact ? 6 : 12;
  const paddingBottom = compact ? 14 : 22;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const chartPoints = data.map((d, i) => {
    const normalizedY = (d.value - minVal + padding) / (range + 2 * padding);
    const y = paddingTop + chartHeight - normalizedY * chartHeight;
    return { x: paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth, y, value: d.value, timestamp: d.timestamp, index: i };
  });

  const pathD = chartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  const formatValue = (val: number) => {
    if (effectiveViewMode === 'price') return val > 0 ? `+${val}` : val.toString();
    if (isProp) return val.toString();
    if (marketType === 'moneyline' || marketType === 'spread') return val > 0 ? `+${val}` : val.toString();
    return val.toString();
  };

  const movementColor = movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400';
  const chartColor = effectiveViewMode === 'price' ? '#f59e0b' : (isProp ? '#3b82f6' : '#10b981');
  const gradientId = `chart-grad-${gameId}-${effectiveViewMode}`;

  // Minimal Y labels for compact mode
  const yLabels = compact ? [
    { value: minVal, y: paddingTop + chartHeight - (0) },
    { value: maxVal, y: paddingTop },
  ] : (() => {
    const labels: { value: number; y: number }[] = [];
    const visualMin = minVal - padding;
    const visualMax = maxVal + padding;
    const visualRange = visualMax - visualMin;
    let labelStep = range <= 5 ? 0.5 : range <= 12 ? 1 : range <= 25 ? 2 : 5;
    if (effectiveViewMode === 'price' || marketType === 'moneyline') {
      labelStep = range <= 8 ? 2 : range <= 16 ? 4 : 5;
    }
    const startValue = Math.floor(visualMin / labelStep) * labelStep;
    const endValue = Math.ceil(visualMax / labelStep) * labelStep + labelStep;
    for (let val = startValue; val <= endValue; val += labelStep) {
      const normalizedY = (val - visualMin) / visualRange;
      const y = paddingTop + chartHeight - normalizedY * chartHeight;
      if (y >= paddingTop - 2 && y <= paddingTop + chartHeight + 2) {
        labels.push({ value: val, y });
      }
    }
    return labels.length > 8 ? labels.filter((_, i) => i % Math.ceil(labels.length / 8) === 0) : labels;
  })();

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
    <div className="h-full flex flex-col">
      {/* Compact header: tracking + movement in one line */}
      <div className="flex items-center justify-between px-1 mb-1">
        <div className="flex items-center gap-1.5">
          {!isProp && (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('over') : setTrackingSide('home')}
                className={`px-1 py-0 text-[9px] font-medium transition-colors ${
                  (marketType === 'total' ? trackingSide === 'over' : trackingSide === 'home')
                    ? 'bg-zinc-700 text-zinc-100' : 'bg-transparent text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'O' : (homeTeam?.slice(0, 3).toUpperCase() || 'HM')}
              </button>
              {isSoccer && marketType === 'moneyline' && (
                <button onClick={() => setTrackingSide('draw')} className={`px-1 py-0 text-[9px] font-medium transition-colors ${trackingSide === 'draw' ? 'bg-zinc-700 text-zinc-100' : 'bg-transparent text-zinc-500'}`}>DRW</button>
              )}
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('under') : setTrackingSide('away')}
                className={`px-1 py-0 text-[9px] font-medium transition-colors ${
                  (marketType === 'total' ? trackingSide === 'under' : trackingSide === 'away')
                    ? 'bg-zinc-700 text-zinc-100' : 'bg-transparent text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'U' : (awayTeam?.slice(0, 3).toUpperCase() || 'AW')}
              </button>
            </div>
          )}
          {!compact && (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              {(isGameLive ? ['30M', '1H', '3H', '6H', '24H', 'ALL'] as TimeRange[] : ['1H', '3H', '6H', '24H', 'ALL'] as TimeRange[]).map(r => (
                <button key={r} onClick={() => setTimeRange(r)} className={`px-1 py-0 text-[8px] font-medium ${timeRange === r ? 'bg-zinc-600 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>{r}</button>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-1 text-[10px]">
          <span className="text-zinc-500">{formatValue(openValue)}</span>
          <span className="text-zinc-600">&rarr;</span>
          <span className="text-zinc-100 font-semibold">{formatValue(currentValue)}</span>
          <span className={`font-medium ${movementColor}`}>{movement > 0 ? '+' : ''}{effectiveViewMode === 'price' ? Math.round(movement) : movement.toFixed(1)}</span>
        </div>
      </div>

      {/* Chart SVG */}
      <div className="relative flex-1 min-h-0">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full cursor-crosshair" preserveAspectRatio="none" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#27272a" strokeWidth="0.5" />
              <text x={paddingLeft - 4} y={label.y + 3} textAnchor="end" fill="#52525b" fontSize={compact ? "8" : "9"}>{formatValue(label.value)}</text>
            </g>
          ))}
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={chartColor} stopOpacity="0.15" />
              <stop offset="100%" stopColor={chartColor} stopOpacity="0" />
            </linearGradient>
          </defs>
          {chartPoints.length > 0 && (
            <>
              <path d={`${pathD} L ${chartPoints[chartPoints.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`} fill={`url(#${gradientId})`} />
              <path d={pathD} fill="none" stroke={chartColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="2" fill="#52525b" stroke="#3f3f46" strokeWidth="0.5" />
              <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="2" fill={chartColor} stroke="#18181b" strokeWidth="0.5" />
              {hoveredPoint && (
                <>
                  <line x1={hoveredPoint.x} y1={paddingTop} x2={hoveredPoint.x} y2={paddingTop + chartHeight} stroke="#3f3f46" strokeWidth="1" />
                  <circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="3" fill={chartColor} stroke="#18181b" strokeWidth="1" />
                </>
              )}
            </>
          )}
        </svg>
        {hoveredPoint && (
          <div className="absolute bg-zinc-800/95 border border-zinc-700/50 rounded px-1.5 py-1 text-[9px] pointer-events-none shadow-lg z-10" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 8}%`, transform: 'translate(-50%, -100%)' }}>
            <div className="font-semibold text-zinc-100">{formatValue(hoveredPoint.value)}</div>
            <div className="text-zinc-500">{hoveredPoint.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// TerminalHeader - 36px bar
// ============================================================================

function TerminalHeader({
  awayTeam, homeTeam, commenceTime, totalEdgeCount, bestEdge, selectedBook, filteredBooks, onSelectBook, isLive,
}: {
  awayTeam: string; homeTeam: string; commenceTime?: string; totalEdgeCount: number;
  bestEdge: { ceq: number; side: string; market: string } | null;
  selectedBook: string; filteredBooks: string[]; onSelectBook: (book: string) => void; isLive: boolean;
}) {
  const [bookOpen, setBookOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) { if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setBookOpen(false); }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const abbrev = (name: string) => {
    const words = name.trim().split(/\s+/);
    return words[words.length - 1].slice(0, 3).toUpperCase();
  };

  const dateStr = commenceTime
    ? new Date(commenceTime).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) + ' ET'
    : '';

  return (
    <div className="bg-[#0a0a0a] flex items-center justify-between px-3 h-[36px] min-h-[36px]" style={{ gridArea: 'header', borderBottom: '2px solid rgba(6, 78, 59, 0.3)', boxShadow: '0 1px 8px rgba(16, 185, 129, 0.06)' }}>
      <div className="flex items-center gap-3">
        <a href="/edge/portal/sports" className="text-zinc-500 hover:text-zinc-300 transition-colors">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
        </a>
        <span className="text-[13px] font-bold text-zinc-100 tracking-tight font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {abbrev(awayTeam)} @ {abbrev(homeTeam)}
        </span>
        <span className="text-[10px] text-zinc-500 hidden sm:inline" title={`${awayTeam} @ ${homeTeam}`}>
          {awayTeam} vs {homeTeam}
        </span>
        {isLive && (
          <span className="flex items-center gap-1">
            <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span></span>
            <span className="text-[10px] font-medium text-red-400">LIVE</span>
          </span>
        )}
        <span className="text-[10px] text-zinc-500">{dateStr}</span>
      </div>
      <div className="flex items-center gap-3">
        {totalEdgeCount > 0 && (
          <span className="text-[10px] font-bold text-emerald-400">{totalEdgeCount} Edge{totalEdgeCount !== 1 ? 's' : ''}</span>
        )}
        {bestEdge && bestEdge.ceq >= 60 && (
          <span className="text-[10px] text-cyan-400 font-mono">Best: {bestEdge.ceq}% {bestEdge.side} {bestEdge.market}</span>
        )}
        {/* Book selector */}
        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setBookOpen(!bookOpen)} className="flex items-center gap-1.5 px-2 py-0.5 bg-zinc-800/80 border border-zinc-700/50 rounded text-[11px] text-zinc-300 hover:bg-zinc-700/80">
            <span className="w-3 h-3 rounded flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0" style={{ backgroundColor: BOOK_CONFIG[selectedBook]?.color || '#6b7280' }}>
              {(BOOK_CONFIG[selectedBook]?.name || selectedBook).charAt(0)}
            </span>
            {BOOK_CONFIG[selectedBook]?.name || selectedBook}
            <svg className={`w-3 h-3 text-zinc-500 transition-transform ${bookOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
          {bookOpen && (
            <div className="absolute right-0 z-50 mt-1 w-44 bg-zinc-800 border border-zinc-700 rounded shadow-xl overflow-hidden">
              {filteredBooks.map(book => (
                <button key={book} onClick={() => { onSelectBook(book); setBookOpen(false); }}
                  className={`w-full flex items-center gap-2 px-3 py-1.5 text-left text-[11px] transition-colors ${book === selectedBook ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-700/50 text-zinc-300'}`}>
                  <span className="w-3 h-3 rounded flex items-center justify-center text-[7px] font-bold text-white" style={{ backgroundColor: BOOK_CONFIG[book]?.color || '#6b7280' }}>{(BOOK_CONFIG[book]?.name || book).charAt(0)}</span>
                  {BOOK_CONFIG[book]?.name || book}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// FairLinePanel - YOUR LINE vs BOOK LINE
// ============================================================================

function FairLinePanel({
  pythonPillars, marketGroups, homeTeam, awayTeam, sportKey,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  marketGroups: any; homeTeam: string; awayTeam: string; sportKey: string;
}) {
  const isSoccer = sportKey?.includes('soccer') ?? false;
  const spreadLine = marketGroups?.fullGame?.spreads?.home?.line;
  const totalLine = marketGroups?.fullGame?.totals?.line;
  const mlHome = marketGroups?.fullGame?.h2h?.home?.price;
  const mlAway = marketGroups?.fullGame?.h2h?.away?.price;

  const fairSpread = pythonPillars && spreadLine !== undefined
    ? calculateFairSpread(spreadLine, pythonPillars.composite)
    : null;
  const fairTotal = pythonPillars && totalLine !== undefined
    ? calculateFairTotal(totalLine, pythonPillars.gameEnvironment)
    : null;

  const fmtSpread = (v: number) => v > 0 ? `+${v}` : `${v}`;

  const renderCard = (label: string, bookVal: string, fairVal: string | null, gap: number | null, edgeSide: string | null) => {
    const hasEdge = gap !== null && Math.abs(gap) >= 0.5 && edgeSide;
    const gapColor = hasEdge ? 'text-emerald-400' : (gap !== null ? 'text-zinc-500' : 'text-zinc-600');
    return (
      <div className={`rounded px-2 py-1.5 ${hasEdge ? 'bg-emerald-500/5 border border-emerald-500/15' : 'bg-zinc-800/40 border border-zinc-800/60'}`}>
        <div className="text-[9px] text-zinc-500 uppercase tracking-wider mb-0.5">{label}</div>
        <div className="flex items-baseline justify-between gap-2">
          <div className="flex items-baseline gap-2">
            <span className="text-[11px] text-zinc-300 font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>{bookVal}</span>
            {fairVal ? (
              <span className="text-[11px] text-cyan-400 font-mono font-semibold" style={{ fontVariantNumeric: 'tabular-nums' }}>{fairVal}</span>
            ) : (
              <span className="text-[10px] text-zinc-600 font-mono italic">N/A</span>
            )}
          </div>
          <span className={`text-[10px] font-mono font-semibold ${gapColor}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
            {gap !== null ? (gap > 0 ? `+${gap}` : `${gap}`) : '--'}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col" style={{ gridArea: 'fairline' }}>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest">Fair Line vs Book</span>
        <div className="flex items-center gap-2">
          <span className="text-[9px] text-zinc-600">{pythonPillars ? 'Pillar-derived' : 'No pillar data'}</span>
          <div className="flex items-center gap-1 text-[8px]">
            <span className="text-zinc-500">BOOK</span>
            <span className="text-cyan-500">FAIR</span>
            <span className="text-zinc-500">GAP</span>
          </div>
        </div>
      </div>
      <div className="flex-1 min-h-0 flex flex-col gap-1">
        {!isSoccer && renderCard(
          'Spread',
          spreadLine !== undefined ? fmtSpread(spreadLine) : '--',
          fairSpread ? fmtSpread(fairSpread.fairLine) : null,
          fairSpread?.gap ?? null,
          fairSpread?.edgeSide ?? null
        )}
        {renderCard(
          'Total',
          totalLine !== undefined ? `${totalLine}` : '--',
          fairTotal ? `${fairTotal.fairLine}` : null,
          fairTotal?.gap ?? null,
          fairTotal?.edgeSide ?? null
        )}
        {renderCard(
          `${awayTeam.split(/\s+/).pop()?.slice(0, 3).toUpperCase() || 'AWY'} ML`,
          mlAway !== undefined ? formatOdds(mlAway) : '--',
          null, null, null
        )}
        {renderCard(
          `${homeTeam.split(/\s+/).pop()?.slice(0, 3).toUpperCase() || 'HME'} ML`,
          mlHome !== undefined ? formatOdds(mlHome) : '--',
          null, null, null
        )}

        {/* Edge summary */}
        {(fairSpread?.edgeSide || fairTotal?.edgeSide) && (
          <div className="mt-auto pt-1 border-t border-zinc-800/50">
            {fairSpread?.edgeSide && (
              <div className="text-[10px] text-emerald-400">
                Spread edge: <span className="font-semibold">{fairSpread.edgeSide === 'home' ? homeTeam : awayTeam}</span> ({fairSpread.gap > 0 ? '+' : ''}{fairSpread.gap} pts)
              </div>
            )}
            {fairTotal?.edgeSide && (
              <div className="text-[10px] text-emerald-400">
                Total edge: <span className="font-semibold">{fairTotal.edgeSide === 'over' ? 'Over' : 'Under'}</span> ({fairTotal.gap > 0 ? '+' : ''}{fairTotal.gap} pts)
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// PillarBarsCompact - 6 inline horizontal bars
// ============================================================================

function PillarBarsCompact({ pythonPillars }: { pythonPillars: PythonPillarScores | null | undefined }) {
  const pillars = [
    { key: 'execution', label: 'EXEC', weight: '20%', fullLabel: 'Execution' },
    { key: 'incentives', label: 'INCV', weight: '10%', fullLabel: 'Incentives' },
    { key: 'shocks', label: 'SHOK', weight: '25%', fullLabel: 'Shocks' },
    { key: 'timeDecay', label: 'TIME', weight: '10%', fullLabel: 'Time Decay' },
    { key: 'flow', label: 'FLOW', weight: '25%', fullLabel: 'Flow' },
    { key: 'gameEnvironment', label: 'ENV', weight: '10%', fullLabel: 'Game Env' },
  ];

  const getBarColor = (score: number) => {
    if (score >= 65) return 'bg-emerald-400';
    if (score >= 55) return 'bg-emerald-600';
    if (score >= 45) return 'bg-zinc-500';
    if (score >= 35) return 'bg-amber-500';
    return 'bg-red-400';
  };

  const getBarGlow = (score: number) => {
    if (score >= 65) return '0 0 6px rgba(52, 211, 153, 0.3)';
    if (score >= 55) return '0 0 4px rgba(5, 150, 105, 0.2)';
    if (score <= 35) return '0 0 6px rgba(239, 68, 68, 0.25)';
    return 'none';
  };

  const getTextColor = (score: number) => {
    if (score >= 65) return 'text-emerald-400';
    if (score >= 55) return 'text-emerald-600';
    if (score >= 45) return 'text-zinc-400';
    if (score >= 35) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col" style={{ gridArea: 'pillars' }}>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest">6-Pillar Analysis</span>
        {pythonPillars && (
          <span className={`text-[14px] font-bold font-mono ${getTextColor(pythonPillars.composite)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
            {pythonPillars.composite}
            <span className="text-[9px] text-zinc-600 ml-0.5">composite</span>
          </span>
        )}
      </div>
      {!pythonPillars ? (
        <div className="flex-1 flex items-center justify-center text-[10px] text-zinc-600">No pillar data available</div>
      ) : (
        <div className="flex-1 min-h-0 flex flex-col justify-between">
          {pillars.map(p => {
            const score = (pythonPillars as any)[p.key] as number;
            return (
              <div key={p.key} className="flex items-center gap-1.5">
                <span className="text-[9px] text-zinc-500 w-16 font-mono truncate" title={p.fullLabel}>
                  {p.label} <span className="text-zinc-600">({p.weight})</span>
                </span>
                <div className="flex-1 h-[6px] bg-zinc-800 rounded-sm overflow-hidden relative">
                  {/* Center line at 50% */}
                  <div className="absolute left-1/2 top-0 w-px h-full bg-zinc-600/50 z-10" />
                  <div
                    className={`h-full rounded-sm transition-all ${getBarColor(score)}`}
                    style={{ width: `${score}%`, boxShadow: getBarGlow(score) }}
                  />
                </div>
                <span className={`text-[9px] font-mono w-6 text-right font-semibold ${getTextColor(score)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>{score}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// CEQBarsCompact - 5 inline CEQ factor bars
// ============================================================================

function CEQBarsCompact({ ceq }: { ceq: GameCEQ | null | undefined }) {
  // Extract active CEQ result for best market
  const getCeqResult = (): CEQResult | null => {
    if (!ceq) return null;
    if (ceq.bestEdge) {
      const { market, side } = ceq.bestEdge;
      if (market === 'spread') return side === 'home' ? ceq.spreads?.home ?? null : ceq.spreads?.away ?? null;
      if (market === 'h2h') return side === 'home' ? ceq.h2h?.home ?? null : ceq.h2h?.away ?? null;
      if (market === 'total') return side === 'over' ? ceq.totals?.over ?? null : ceq.totals?.under ?? null;
    }
    // Fallback: pick first available
    return ceq.spreads?.home ?? ceq.h2h?.home ?? ceq.totals?.over ?? null;
  };

  const ceqResult = getCeqResult();

  const factors = ceqResult ? [
    { label: 'Mkt Eff', score: ceqResult.pillars.marketEfficiency.score, weight: ceqResult.pillars.marketEfficiency.weight },
    { label: 'Lineup', score: ceqResult.pillars.lineupImpact.score, weight: ceqResult.pillars.lineupImpact.weight },
    { label: 'GameEnv', score: ceqResult.pillars.gameEnvironment.score, weight: ceqResult.pillars.gameEnvironment.weight },
    { label: 'Matchup', score: ceqResult.pillars.matchupDynamics.score, weight: ceqResult.pillars.matchupDynamics.weight },
    { label: 'Sentmnt', score: ceqResult.pillars.sentiment.score, weight: ceqResult.pillars.sentiment.weight },
  ] : [];

  const getBarColor = (score: number, weight: number) => {
    if (weight === 0) return 'bg-zinc-700';
    if (score >= 70) return 'bg-emerald-400';
    if (score >= 60) return 'bg-blue-400';
    if (score >= 40) return 'bg-zinc-500';
    if (score >= 30) return 'bg-amber-400';
    return 'bg-red-400';
  };

  const getBarGlow = (score: number, weight: number) => {
    if (weight === 0) return 'none';
    if (score >= 70) return '0 0 6px rgba(52, 211, 153, 0.3)';
    if (score >= 60) return '0 0 4px rgba(96, 165, 250, 0.25)';
    if (score <= 30) return '0 0 6px rgba(239, 68, 68, 0.25)';
    return 'none';
  };

  const getTextColor = (score: number, weight: number) => {
    if (weight === 0) return 'text-zinc-600';
    if (score >= 70) return 'text-emerald-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-zinc-400';
    if (score >= 30) return 'text-amber-400';
    return 'text-red-400';
  };

  const confBadgeStyle = ceqResult ? (() => {
    switch (ceqResult.confidence) {
      case 'STRONG': return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      case 'EDGE': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'WATCH': return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
      default: return 'bg-zinc-800 text-zinc-500 border border-zinc-700';
    }
  })() : '';

  const confTextColor = ceqResult ? (
    ceqResult.confidence === 'STRONG' ? 'text-emerald-400' :
    ceqResult.confidence === 'EDGE' ? 'text-blue-400' :
    ceqResult.confidence === 'WATCH' ? 'text-amber-400' : 'text-zinc-500'
  ) : 'text-zinc-500';

  // Build thesis line
  const getThesis = () => {
    if (!ceqResult || !ceq?.bestEdge) return null;
    const { market, side, ceq: ceqVal } = ceq.bestEdge;
    const marketLabel = market === 'h2h' ? 'Moneyline' : market === 'spread' ? 'Spread' : 'Total';
    const sideLabel = side.charAt(0).toUpperCase() + side.slice(1);
    if (ceqVal < 60) return null;
    return `${sideLabel} ${marketLabel} validated at ${ceqVal}%`;
  };
  const thesis = getThesis();

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col" style={{ gridArea: 'ceqfactors' }}>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest">CEQ Validation</span>
        {ceqResult && (
          <div className="flex items-center gap-1.5">
            <span className={`text-[14px] font-bold font-mono ${confTextColor}`} style={{ fontVariantNumeric: 'tabular-nums' }}>{Math.round(ceqResult.ceq)}%</span>
            <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${confBadgeStyle}`}>{ceqResult.confidence}</span>
          </div>
        )}
      </div>
      {!ceqResult ? (
        <div className="flex-1 flex items-center justify-center text-[10px] text-zinc-600">No CEQ data available</div>
      ) : (
        <div className="flex-1 min-h-0 flex flex-col justify-between">
          {factors.map(f => (
            <div key={f.label} className="flex items-center gap-1.5">
              <span className="text-[9px] text-zinc-500 w-16 font-mono truncate">
                {f.label} <span className="text-zinc-600">({Math.round(f.weight * 100)}%)</span>
              </span>
              <div className="flex-1 h-[6px] bg-zinc-800 rounded-sm overflow-hidden relative">
                {/* Center line at 50% */}
                <div className="absolute left-1/2 top-0 w-px h-full bg-zinc-600/50 z-10" />
                <div
                  className={`h-full rounded-sm transition-all ${getBarColor(f.score, f.weight)}`}
                  style={{ width: `${f.weight > 0 ? Math.max(5, f.score) : 0}%`, boxShadow: getBarGlow(f.score, f.weight) }}
                />
              </div>
              <span className={`text-[9px] font-mono w-6 text-right font-semibold ${getTextColor(f.score, f.weight)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>{f.weight > 0 ? Math.round(f.score) : '--'}</span>
            </div>
          ))}
          {/* Thesis line */}
          {thesis && (
            <div className="mt-1 pt-1 border-t border-zinc-800/50">
              <span className={`text-[9px] ${confTextColor}`}>{thesis}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MarketsTable - Period tabs + dense table + EDGE column
// ============================================================================

function MarketsTable({
  gameData, marketGroups, bookmakers, activeTab, onTabChange, tabs,
  chartMarket, onSelectMarket, ceq, teamTotalsCeq, sportKey, selectedBook,
}: {
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string };
  marketGroups: any; bookmakers: Record<string, any>;
  activeTab: string; onTabChange: (tab: string) => void;
  tabs: { key: string; label: string }[];
  chartMarket: 'spread' | 'total' | 'moneyline';
  onSelectMarket: (m: 'spread' | 'total' | 'moneyline') => void;
  ceq: GameCEQ | null | undefined;
  teamTotalsCeq?: { home: GameCEQ | null; away: GameCEQ | null } | null;
  sportKey: string; selectedBook: string;
}) {
  const isSoccer = sportKey?.includes('soccer') ?? false;
  const periodMap: Record<string, string> = { 'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
  const periodKey = periodMap[activeTab] || 'fullGame';
  const markets = marketGroups[periodKey];

  // Calculate consensus for EV
  const getConsensus = () => {
    const books = Object.values(bookmakers);
    const spreadHomePrices: number[] = [], spreadAwayPrices: number[] = [];
    const mlHomePrices: number[] = [], mlAwayPrices: number[] = [];
    const overPrices: number[] = [], underPrices: number[] = [];
    for (const book of books) {
      const mg = (book as any).marketGroups?.[periodKey];
      if (mg?.spreads?.home?.price) spreadHomePrices.push(mg.spreads.home.price);
      if (mg?.spreads?.away?.price) spreadAwayPrices.push(mg.spreads.away.price);
      if (mg?.h2h?.home?.price) mlHomePrices.push(mg.h2h.home.price);
      if (mg?.h2h?.away?.price) mlAwayPrices.push(mg.h2h.away.price);
      if (mg?.totals?.over?.price) overPrices.push(mg.totals.over.price);
      if (mg?.totals?.under?.price) underPrices.push(mg.totals.under.price);
    }
    const median = (arr: number[]) => {
      if (arr.length === 0) return undefined;
      const sorted = [...arr].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };
    return {
      spreads: { home: median(spreadHomePrices), away: median(spreadAwayPrices) },
      h2h: { home: median(mlHomePrices), away: median(mlAwayPrices) },
      totals: { over: median(overPrices), under: median(underPrices) },
    };
  };

  const consensus = getConsensus();

  // Adjusted EV (same logic as old MarketSection)
  const getAdjustedEV = (rawEV: number | undefined, ceqVal: number | undefined): number | undefined => {
    if (ceqVal === undefined) return rawEV;
    if (ceqVal >= 76) return Math.max(rawEV ?? 0, 5 + (ceqVal - 76) * 0.3);
    if (ceqVal >= 66) return Math.max(rawEV ?? 0, 3 + (ceqVal - 66) * 0.2);
    if (ceqVal >= 56) return Math.max(rawEV ?? 0, 1 + (ceqVal - 56) * 0.2);
    if (ceqVal >= 45) { const nev = (ceqVal - 50) * 0.1; return Math.max(rawEV ?? nev, nev); }
    const negEV = -0.5 - (45 - ceqVal) * 0.125;
    return Math.min(rawEV ?? negEV, negEV);
  };

  // Calculate EVs
  const rawSpreadHomeEV = markets?.spreads?.home?.price && markets?.spreads?.away?.price
    ? calculateTwoWayEV(markets.spreads.home.price, markets.spreads.away.price, consensus?.spreads?.home, consensus?.spreads?.away) : undefined;
  const rawSpreadAwayEV = markets?.spreads?.home?.price && markets?.spreads?.away?.price
    ? calculateTwoWayEV(markets.spreads.away.price, markets.spreads.home.price, consensus?.spreads?.away, consensus?.spreads?.home) : undefined;
  const rawMlHomeEV = markets?.h2h?.home?.price && markets?.h2h?.away?.price
    ? calculateTwoWayEV(markets.h2h.home.price, markets.h2h.away.price, consensus?.h2h?.home, consensus?.h2h?.away) : undefined;
  const rawMlAwayEV = markets?.h2h?.home?.price && markets?.h2h?.away?.price
    ? calculateTwoWayEV(markets.h2h.away.price, markets.h2h.home.price, consensus?.h2h?.away, consensus?.h2h?.home) : undefined;
  const rawOverEV = markets?.totals?.over?.price && markets?.totals?.under?.price
    ? calculateTwoWayEV(markets.totals.over.price, markets.totals.under.price, consensus?.totals?.over, consensus?.totals?.under) : undefined;
  const rawUnderEV = markets?.totals?.over?.price && markets?.totals?.under?.price
    ? calculateTwoWayEV(markets.totals.under.price, markets.totals.over.price, consensus?.totals?.under, consensus?.totals?.over) : undefined;

  const spreadHomeEV = getAdjustedEV(rawSpreadHomeEV, ceq?.spreads?.home?.ceq);
  const spreadAwayEV = getAdjustedEV(rawSpreadAwayEV, ceq?.spreads?.away?.ceq);
  const mlHomeEV = getAdjustedEV(rawMlHomeEV, ceq?.h2h?.home?.ceq);
  const mlAwayEV = getAdjustedEV(rawMlAwayEV, ceq?.h2h?.away?.ceq);
  const overEV = getAdjustedEV(rawOverEV, ceq?.totals?.over?.ceq);
  const underEV = getAdjustedEV(rawUnderEV, ceq?.totals?.under?.ceq);

  // Find best edge for each team row
  const findBestEdge = (side: 'away' | 'home'): { ceq: number; label: string; confidence: string } | null => {
    const candidates: { ceq: number; label: string; confidence: string }[] = [];
    if (side === 'away') {
      if (ceq?.spreads?.away?.ceq && ceq.spreads.away.ceq >= 60) candidates.push({ ceq: ceq.spreads.away.ceq, label: 'Spread', confidence: ceq.spreads.away.confidence });
      if (ceq?.h2h?.away?.ceq && ceq.h2h.away.ceq >= 60) candidates.push({ ceq: ceq.h2h.away.ceq, label: 'ML', confidence: ceq.h2h.away.confidence });
      if (ceq?.totals?.over?.ceq && ceq.totals.over.ceq >= 60) candidates.push({ ceq: ceq.totals.over.ceq, label: 'Over', confidence: ceq.totals.over.confidence });
    } else {
      if (ceq?.spreads?.home?.ceq && ceq.spreads.home.ceq >= 60) candidates.push({ ceq: ceq.spreads.home.ceq, label: 'Spread', confidence: ceq.spreads.home.confidence });
      if (ceq?.h2h?.home?.ceq && ceq.h2h.home.ceq >= 60) candidates.push({ ceq: ceq.h2h.home.ceq, label: 'ML', confidence: ceq.h2h.home.confidence });
      if (ceq?.totals?.under?.ceq && ceq.totals.under.ceq >= 60) candidates.push({ ceq: ceq.totals.under.ceq, label: 'Under', confidence: ceq.totals.under.confidence });
    }
    if (candidates.length === 0) return null;
    return candidates.sort((a, b) => b.ceq - a.ceq)[0];
  };

  const awayEdge = findBestEdge('away');
  const homeEdge = findBestEdge('home');

  const getEdgeBadgeColor = (ceqVal: number) => {
    if (ceqVal >= 75) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (ceqVal >= 65) return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
  };

  const getCellBg = (ev: number | undefined, ceqVal: number | undefined) => {
    if (ceqVal && ceqVal >= 60) {
      if (ceqVal >= 75) return 'bg-emerald-500/10';
      if (ceqVal >= 65) return 'bg-blue-500/10';
      return 'bg-amber-500/5';
    }
    return '';
  };

  // Is this an exchange view?
  const isExchange = selectedBook === 'kalshi' || selectedBook === 'polymarket';

  // For team totals and alternates, render special content
  if (activeTab === 'team') {
    return (
      <div className="bg-[#0a0a0a] p-2 h-full flex flex-col overflow-auto" style={{ gridArea: 'markets' }}>
        <div className="flex gap-0 mb-2 overflow-x-auto flex-shrink-0 border-b border-zinc-800">
          {tabs.map(tab => (
            <button key={tab.key} onClick={() => onTabChange(tab.key)}
              className={`px-2.5 py-1 text-[10px] font-medium whitespace-nowrap transition-all relative ${activeTab === tab.key ? 'text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>
              {tab.label}
              {activeTab === tab.key && <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-emerald-400" style={{ boxShadow: '0 1px 4px rgba(16,185,129,0.3)' }} />}
            </button>
          ))}
        </div>
        <TeamTotalsSection teamTotals={marketGroups.teamTotals} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
      </div>
    );
  }

  if (activeTab === 'alt') {
    return (
      <div className="bg-[#0a0a0a] p-2 h-full flex flex-col overflow-auto" style={{ gridArea: 'markets' }}>
        <div className="flex gap-0 mb-2 overflow-x-auto flex-shrink-0 border-b border-zinc-800">
          {tabs.map(tab => (
            <button key={tab.key} onClick={() => onTabChange(tab.key)}
              className={`px-2.5 py-1 text-[10px] font-medium whitespace-nowrap transition-all relative ${activeTab === tab.key ? 'text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>
              {tab.label}
              {activeTab === tab.key && <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-emerald-400" style={{ boxShadow: '0 1px 4px rgba(16,185,129,0.3)' }} />}
            </button>
          ))}
        </div>
        <AlternatesSection alternates={marketGroups.alternates} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
      </div>
    );
  }

  if (isExchange) {
    return (
      <div className="bg-[#0a0a0a] p-2 h-full flex flex-col overflow-auto" style={{ gridArea: 'markets' }}>
        <div className="flex gap-0 mb-2 overflow-x-auto flex-shrink-0 border-b border-zinc-800">
          {tabs.map(tab => (
            <button key={tab.key} onClick={() => onTabChange(tab.key)}
              className={`px-2.5 py-1 text-[10px] font-medium whitespace-nowrap transition-all relative ${activeTab === tab.key ? 'text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>
              {tab.label}
              {activeTab === tab.key && <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-emerald-400" style={{ boxShadow: '0 1px 4px rgba(16,185,129,0.3)' }} />}
            </button>
          ))}
        </div>
        <ExchangeMarketsSection
          exchangeMarkets={marketGroups.exchangeMarkets || []}
          exchange={selectedBook as 'kalshi' | 'polymarket'}
          homeTeam={gameData.homeTeam}
          awayTeam={gameData.awayTeam}
        />
      </div>
    );
  }

  // Edge progress bar renderer
  const renderEdgeCell = (edge: { ceq: number; label: string; confidence: string } | null) => {
    if (!edge) return null;
    const pct = Math.min(100, Math.max(0, ((edge.ceq - 50) / 50) * 100));
    const barColor = edge.ceq >= 75 ? 'bg-emerald-400' : edge.ceq >= 65 ? 'bg-blue-400' : 'bg-amber-400';
    const barGlow = edge.ceq >= 75 ? '0 0 6px rgba(52,211,153,0.3)' : edge.ceq >= 65 ? '0 0 4px rgba(96,165,250,0.25)' : 'none';
    return (
      <div className="flex items-center gap-1 w-full">
        <div className="flex-1 h-[5px] bg-zinc-800 rounded-sm overflow-hidden">
          <div className={`h-full rounded-sm ${barColor}`} style={{ width: `${pct}%`, boxShadow: barGlow }} />
        </div>
        <span className={`text-[9px] font-bold font-mono whitespace-nowrap ${getEdgeBadgeColor(edge.ceq).split(' ').find(c => c.startsWith('text-'))}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
          {edge.ceq}%
        </span>
      </div>
    );
  };

  // Grid col template
  const gridCols = isSoccer
    ? 'grid-cols-[1fr_80px_80px_minmax(80px,auto)]'
    : 'grid-cols-[1fr_80px_80px_80px_minmax(80px,auto)]';

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col overflow-auto" style={{ gridArea: 'markets' }}>
      {/* Period tabs - terminal style with emerald underline */}
      <div className="flex gap-0 mb-2 overflow-x-auto flex-shrink-0 border-b border-zinc-800">
        {tabs.map(tab => (
          <button key={tab.key} onClick={() => onTabChange(tab.key)}
            className={`px-2.5 py-1 text-[10px] font-medium whitespace-nowrap transition-all relative ${activeTab === tab.key ? 'text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>
            {tab.label}
            {activeTab === tab.key && (
              <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-emerald-400" style={{ boxShadow: '0 1px 4px rgba(16,185,129,0.3)' }} />
            )}
          </button>
        ))}
      </div>

      {/* Market type pills */}
      <div className="flex gap-1 mb-2 flex-shrink-0">
        {(['spread', 'total', 'moneyline'] as const).filter(m => !isSoccer || m !== 'spread').map(m => (
          <button key={m} onClick={() => onSelectMarket(m)}
            className={`px-2 py-0.5 rounded-full text-[9px] font-medium transition-all border ${
              chartMarket === m
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                : 'bg-zinc-800/50 text-zinc-500 border-zinc-700/30 hover:text-zinc-300 hover:border-zinc-600/50'
            }`}>
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      {/* Dense table */}
      {markets ? (
        <div className="flex-1 min-h-0" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {/* Header row */}
          <div className={`grid ${gridCols} gap-px text-[9px] text-zinc-500 uppercase tracking-widest font-medium mb-px`} style={{ background: '#27272a' }}>
            <div className="bg-[#0a0a0a] px-2 py-1">Team</div>
            {!isSoccer && <div className="bg-[#0a0a0a] px-1 py-1 text-center">Spread</div>}
            <div className="bg-[#0a0a0a] px-1 py-1 text-center">ML</div>
            <div className="bg-[#0a0a0a] px-1 py-1 text-center">Total</div>
            <div className="bg-[#0a0a0a] px-1 py-1 text-center">Edge</div>
          </div>

          {/* Away row */}
          <div className={`grid ${gridCols} gap-px mb-px group`} style={{ background: '#27272a' }}>
            <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-2 py-1.5 flex items-center transition-colors">
              <span className="text-[11px] font-medium text-zinc-200 truncate">{gameData.awayTeam}</span>
            </div>
            {!isSoccer && (
              <div className={`bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(spreadAwayEV, ceq?.spreads?.away?.ceq)}`} onClick={() => onSelectMarket('spread')}>
                {markets.spreads ? (
                  <>
                    <div className="text-[11px] font-medium text-zinc-100 font-mono">{formatSpread(markets.spreads.away.line)}</div>
                    <div className="flex items-center justify-center gap-0.5">
                      <span className="text-[10px] text-zinc-400 font-mono">{formatOdds(markets.spreads.away.price)}</span>
                      {spreadAwayEV !== undefined && <span className={`text-[9px] font-mono ${getEVColor(spreadAwayEV)}`}>{formatEV(spreadAwayEV)}</span>}
                    </div>
                  </>
                ) : <span className="text-zinc-600 text-[10px]">-</span>}
              </div>
            )}
            <div className={`bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(mlAwayEV, ceq?.h2h?.away?.ceq)}`} onClick={() => onSelectMarket('moneyline')}>
              {markets.h2h ? (
                <>
                  <div className="text-[11px] font-medium text-zinc-100 font-mono">{formatOdds(markets.h2h.away.price)}</div>
                  {mlAwayEV !== undefined && <div className={`text-[9px] font-mono ${getEVColor(mlAwayEV)}`}>{formatEV(mlAwayEV)}</div>}
                </>
              ) : <span className="text-zinc-600 text-[10px]">-</span>}
            </div>
            <div className={`bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(overEV, ceq?.totals?.over?.ceq)}`} onClick={() => onSelectMarket('total')}>
              {markets.totals ? (
                <>
                  <div className="text-[11px] font-medium text-zinc-100 font-mono">O {markets.totals.line}</div>
                  <div className="flex items-center justify-center gap-0.5">
                    <span className="text-[10px] text-zinc-400 font-mono">{formatOdds(markets.totals.over.price)}</span>
                    {overEV !== undefined && <span className={`text-[9px] font-mono ${getEVColor(overEV)}`}>{formatEV(overEV)}</span>}
                  </div>
                </>
              ) : <span className="text-zinc-600 text-[10px]">-</span>}
            </div>
            {/* Edge column with progress bar */}
            <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1.5 py-0.5 flex items-center transition-colors">
              {renderEdgeCell(awayEdge)}
            </div>
          </div>

          {/* Home row - alternating slightly lighter bg */}
          <div className={`grid ${gridCols} gap-px group`} style={{ background: '#27272a' }}>
            <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-2 py-1.5 flex items-center transition-colors">
              <span className="text-[11px] font-medium text-zinc-200 truncate">{gameData.homeTeam}</span>
            </div>
            {!isSoccer && (
              <div className={`bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(spreadHomeEV, ceq?.spreads?.home?.ceq)}`} onClick={() => onSelectMarket('spread')}>
                {markets.spreads ? (
                  <>
                    <div className="text-[11px] font-medium text-zinc-100 font-mono">{formatSpread(markets.spreads.home.line)}</div>
                    <div className="flex items-center justify-center gap-0.5">
                      <span className="text-[10px] text-zinc-400 font-mono">{formatOdds(markets.spreads.home.price)}</span>
                      {spreadHomeEV !== undefined && <span className={`text-[9px] font-mono ${getEVColor(spreadHomeEV)}`}>{formatEV(spreadHomeEV)}</span>}
                    </div>
                  </>
                ) : <span className="text-zinc-600 text-[10px]">-</span>}
              </div>
            )}
            <div className={`bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(mlHomeEV, ceq?.h2h?.home?.ceq)}`} onClick={() => onSelectMarket('moneyline')}>
              {markets.h2h ? (
                <>
                  <div className="text-[11px] font-medium text-zinc-100 font-mono">{formatOdds(markets.h2h.home.price)}</div>
                  {mlHomeEV !== undefined && <div className={`text-[9px] font-mono ${getEVColor(mlHomeEV)}`}>{formatEV(mlHomeEV)}</div>}
                </>
              ) : <span className="text-zinc-600 text-[10px]">-</span>}
            </div>
            <div className={`bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-0.5 text-center cursor-pointer transition-colors ${getCellBg(underEV, ceq?.totals?.under?.ceq)}`} onClick={() => onSelectMarket('total')}>
              {markets.totals ? (
                <>
                  <div className="text-[11px] font-medium text-zinc-100 font-mono">U {markets.totals.line}</div>
                  <div className="flex items-center justify-center gap-0.5">
                    <span className="text-[10px] text-zinc-400 font-mono">{formatOdds(markets.totals.under.price)}</span>
                    {underEV !== undefined && <span className={`text-[9px] font-mono ${getEVColor(underEV)}`}>{formatEV(underEV)}</span>}
                  </div>
                </>
              ) : <span className="text-zinc-600 text-[10px]">-</span>}
            </div>
            {/* Edge column with progress bar */}
            <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1.5 py-0.5 flex items-center transition-colors">
              {renderEdgeCell(homeEdge)}
            </div>
          </div>

          {/* Soccer draw row */}
          {isSoccer && markets?.h2h?.draw && (
            <div className={`grid grid-cols-[1fr_80px_80px_minmax(80px,auto)] gap-px mt-px group`} style={{ background: '#27272a' }}>
              <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-2 py-1 transition-colors"><span className="text-[11px] font-medium text-zinc-400">Draw</span></div>
              <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1 py-0.5 text-center cursor-pointer transition-colors" onClick={() => onSelectMarket('moneyline')}>
                <div className="text-[11px] font-medium text-zinc-100 font-mono">{formatOdds(markets.h2h.draw.price)}</div>
              </div>
              <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1 py-0.5 transition-colors"></div>
              <div className="bg-[#0a0a0a] group-hover:bg-zinc-900/80 px-1.5 py-0.5 flex items-center transition-colors">
                {ceq?.h2h?.draw?.ceq && ceq.h2h.draw.ceq >= 60 ? renderEdgeCell({ ceq: ceq.h2h.draw.ceq, label: 'Draw', confidence: ceq.h2h.draw.confidence }) : null}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-zinc-500 text-[11px]">
          No market data available
        </div>
      )}
    </div>
  );
}

// ============================================================================
// TeamTotalsSection (kept, slightly simplified)
// ============================================================================

function TeamTotalsSection({ teamTotals, homeTeam, awayTeam }: { teamTotals: any; homeTeam: string; awayTeam: string }) {
  if (!teamTotals || (!teamTotals.home?.over && !teamTotals.away?.over)) {
    return <div className="flex-1 flex items-center justify-center text-zinc-500 text-[11px]">No team totals available</div>;
  }
  const renderTeam = (label: string, data: any) => {
    if (!data?.over) return null;
    const overEV = data.over?.price && data.under?.price ? calculateTwoWayEV(data.over.price, data.under.price) : undefined;
    const underEV = data.over?.price && data.under?.price ? calculateTwoWayEV(data.under.price, data.over.price) : undefined;
    return (
      <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/50 last:border-0">
        <span className="text-[11px] font-medium text-zinc-200 min-w-[100px]">{label}</span>
        <div className="flex gap-2">
          <div className={`text-center py-1 px-2 rounded border ${getEVBgClass(overEV ?? 0)}`}>
            <div className="text-[11px] font-medium text-zinc-100">O {data.over.line}</div>
            <div className="flex items-center justify-center gap-0.5">
              <span className="text-[10px] text-zinc-400">{formatOdds(data.over.price)}</span>
              {overEV !== undefined && Math.abs(overEV) >= 0.5 && <span className={`text-[9px] font-mono ${getEVColor(overEV)}`}>{formatEV(overEV)}</span>}
            </div>
          </div>
          {data.under && (
            <div className={`text-center py-1 px-2 rounded border ${getEVBgClass(underEV ?? 0)}`}>
              <div className="text-[11px] font-medium text-zinc-100">U {data.under.line}</div>
              <div className="flex items-center justify-center gap-0.5">
                <span className="text-[10px] text-zinc-400">{formatOdds(data.under.price)}</span>
                {underEV !== undefined && Math.abs(underEV) >= 0.5 && <span className={`text-[9px] font-mono ${getEVColor(underEV)}`}>{formatEV(underEV)}</span>}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };
  return (
    <div className="flex-1 min-h-0">
      {renderTeam(awayTeam, teamTotals.away)}
      {renderTeam(homeTeam, teamTotals.home)}
    </div>
  );
}

// ============================================================================
// AlternatesSection (kept)
// ============================================================================

function AlternatesSection({ alternates, homeTeam, awayTeam }: { alternates: any; homeTeam: string; awayTeam: string }) {
  const [view, setView] = useState<'spreads' | 'totals'>('spreads');
  const altSpreads = alternates?.spreads || [];
  const altTotals = alternates?.totals || [];
  if (altSpreads.length === 0 && altTotals.length === 0) {
    return <div className="flex-1 flex items-center justify-center text-zinc-500 text-[11px]">No alternate lines available</div>;
  }

  return (
    <div className="flex-1 min-h-0 overflow-auto">
      <div className="flex gap-1 mb-2">
        {altSpreads.length > 0 && <button onClick={() => setView('spreads')} className={`px-2 py-0.5 rounded text-[10px] font-medium ${view === 'spreads' ? 'bg-emerald-500/80 text-white' : 'bg-zinc-800 text-zinc-400'}`}>Alt Spreads</button>}
        {altTotals.length > 0 && <button onClick={() => setView('totals')} className={`px-2 py-0.5 rounded text-[10px] font-medium ${view === 'totals' ? 'bg-emerald-500/80 text-white' : 'bg-zinc-800 text-zinc-400'}`}>Alt Totals</button>}
      </div>
      {view === 'spreads' && altSpreads.length > 0 && (
        <div className="space-y-0.5">
          <div className="grid grid-cols-[60px,1fr,1fr] gap-1 text-[9px] text-zinc-500 uppercase">
            <div>Spread</div><div className="text-center">{awayTeam}</div><div className="text-center">{homeTeam}</div>
          </div>
          {altSpreads.map((row: any, i: number) => (
            <div key={i} className="grid grid-cols-[60px,1fr,1fr] gap-1 items-center">
              <span className="text-[10px] font-medium text-zinc-300">{formatSpread(row.homeSpread)}</span>
              <div className="text-center text-[10px]">
                {row.away ? <><span className="text-zinc-100">{formatSpread(row.away.line)}</span> <span className="text-zinc-500">{formatOdds(row.away.price)}</span></> : '-'}
              </div>
              <div className="text-center text-[10px]">
                {row.home ? <><span className="text-zinc-100">{formatSpread(row.home.line)}</span> <span className="text-zinc-500">{formatOdds(row.home.price)}</span></> : '-'}
              </div>
            </div>
          ))}
        </div>
      )}
      {view === 'totals' && altTotals.length > 0 && (
        <div className="space-y-0.5">
          <div className="grid grid-cols-[60px,1fr,1fr] gap-1 text-[9px] text-zinc-500 uppercase">
            <div>Line</div><div className="text-center">Over</div><div className="text-center">Under</div>
          </div>
          {altTotals.map((row: any, i: number) => (
            <div key={i} className="grid grid-cols-[60px,1fr,1fr] gap-1 items-center">
              <span className="text-[10px] font-medium text-zinc-300">{row.line}</span>
              <div className="text-center text-[10px]">{row.over ? <span className="text-zinc-100">{formatOdds(row.over.price)}</span> : '-'}</div>
              <div className="text-center text-[10px]">{row.under ? <span className="text-zinc-100">{formatOdds(row.under.price)}</span> : '-'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// ExchangeMarketsSection (kept, simplified for terminal)
// ============================================================================

function ExchangeMarketsSection({ exchangeMarkets, exchange, homeTeam, awayTeam }: { exchangeMarkets: any[]; exchange: 'kalshi' | 'polymarket'; homeTeam: string; awayTeam: string }) {
  if (!exchangeMarkets || exchangeMarkets.length === 0) {
    return <div className="flex-1 flex items-center justify-center text-zinc-500 text-[11px]">No matching prediction markets</div>;
  }
  const formatPrice = (price: number | null) => price !== null ? `${price}c` : '-';
  return (
    <div className="flex-1 min-h-0 overflow-auto space-y-1">
      {exchangeMarkets.map((market, idx) => (
        <div key={market.market_id || idx} className="border border-zinc-800/50 rounded p-2">
          <div className="text-[10px] font-medium text-zinc-200 mb-1 truncate">{market.market_title}</div>
          <div className="flex gap-3 text-[10px]">
            <span className="text-emerald-400 font-mono">YES {formatPrice(market.yes_price)}</span>
            <span className="text-red-400 font-mono">NO {formatPrice(market.no_price)}</span>
            {market.spread !== null && <span className="text-zinc-500">Spread: {market.spread}c</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Demo/Lock components
// ============================================================================

const DEMO_ACCOUNTS: string[] = ['omigroup.ops@outlook.com'];

function LiveLockOverlay() {
  return (
    <div className="absolute inset-0 bg-zinc-900/80 backdrop-blur-sm flex flex-col items-center justify-center z-20 rounded">
      <div className="text-center p-4">
        <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-amber-500/20 flex items-center justify-center">
          <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
        </div>
        <h3 className="text-sm font-semibold text-zinc-100 mb-1">Live Tracking</h3>
        <p className="text-[10px] text-zinc-400 mb-2">Upgrade to Tier 2</p>
        <button className="px-3 py-1 bg-amber-500 hover:bg-amber-600 text-black font-medium rounded text-[11px]">Upgrade</button>
      </div>
    </div>
  );
}

// ============================================================================
// Main GameDetailClient Component - Bloomberg Terminal Layout
// ============================================================================

export function GameDetailClient({
  gameData, bookmakers, availableBooks, availableTabs,
  userTier = 'tier_2', userEmail, isDemo = false,
  ceq, ceqByPeriod, teamTotalsCeq, edgeCountBreakdown,
  pythonPillarScores, totalEdgeCount = 0,
}: GameDetailClientProps) {
  const [activeTab, setActiveTab] = useState('full');
  const isSoccerGame = gameData.sportKey?.includes('soccer') ?? false;
  const [chartMarket, setChartMarket] = useState<'spread' | 'total' | 'moneyline'>(isSoccerGame ? 'moneyline' : 'spread');
  const [chartViewMode, setChartViewMode] = useState<ChartViewMode>('line');
  const [lazyLineHistory, setLazyLineHistory] = useState<Record<string, Record<string, any[]>>>({});
  const [loadingPeriods, setLoadingPeriods] = useState<Set<string>>(new Set());

  // User/demo state
  const [localEmail, setLocalEmail] = useState<string | null>(null);
  useEffect(() => {
    const storedEmail = localStorage.getItem('omi_edge_email');
    if (storedEmail) setLocalEmail(storedEmail);
  }, []);
  const effectiveEmail = userEmail || localEmail;
  const isDemoUser = isDemo || (effectiveEmail && DEMO_ACCOUNTS.includes(effectiveEmail.toLowerCase()));
  const isLive = gameData.commenceTime ? checkGameLive(gameData.commenceTime) : false;
  const showLiveLock = isLive && userTier === 'tier_1' && !isDemoUser;

  const filteredBooks = availableBooks.filter(book => ALLOWED_BOOKS.includes(book));
  const [selectedBook, setSelectedBook] = useState(filteredBooks[0] || 'fanduel');
  const marketGroups = bookmakers[selectedBook]?.marketGroups || {};
  const isNHL = gameData.sportKey.includes('icehockey');

  // CEQ by period
  const tabToPeriodKey: Record<string, keyof CEQByPeriod> = {
    'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf',
    '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4',
    '1p': 'p1', '2p': 'p2', '3p': 'p3',
  };
  const isSpecialTab = activeTab === 'team' || activeTab === 'alt';
  const activePeriodKey = tabToPeriodKey[activeTab] || 'fullGame';
  const activeCeq: GameCEQ | null | undefined = isSpecialTab ? null : (ceqByPeriod?.[activePeriodKey] ?? (activeTab === 'full' ? ceq : null));

  // Chart selection
  const generatePriceMovement = (seed: string) => { const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0); const x = Math.sin(hashSeed) * 10000; return (x - Math.floor(x) - 0.5) * 0.15; };

  const getCurrentMarketValues = () => {
    const periodMap: Record<string, string> = { 'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const markets = marketGroups[periodMap[activeTab] || 'fullGame'];
    if (chartMarket === 'spread') {
      return { line: markets?.spreads?.home?.line, homeLine: markets?.spreads?.home?.line, awayLine: markets?.spreads?.away?.line, price: markets?.spreads?.home?.price, homePrice: markets?.spreads?.home?.price, awayPrice: markets?.spreads?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-away`) };
    }
    if (chartMarket === 'total') {
      return { line: markets?.totals?.line, price: markets?.totals?.over?.price, overPrice: markets?.totals?.over?.price, underPrice: markets?.totals?.under?.price, overPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-over`), underPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-under`) };
    }
    return { line: undefined, price: markets?.h2h?.home?.price, homePrice: markets?.h2h?.home?.price, awayPrice: markets?.h2h?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-away`) };
  };

  const getChartSelection = (): ChartSelection => {
    const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q', '1p': '1P', '2p': '2P', '3p': '3P' };
    const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'ML' };
    const values = getCurrentMarketValues();
    return { type: 'market', market: chartMarket, period: activeTab, label: `${periodLabels[activeTab] || 'Full'} ${marketLabels[chartMarket]}`, ...values };
  };

  const chartSelection = getChartSelection();

  const getLineHistory = () => {
    const periodKeyMap: Record<string, string> = { 'full': 'full', '1h': 'h1', '2h': 'h2', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const periodKey = periodKeyMap[activeTab] || 'full';
    const lazyData = lazyLineHistory[periodKey]?.[chartMarket];
    if (lazyData && lazyData.length > 0) return lazyData;
    return marketGroups.lineHistory?.[periodKey]?.[chartMarket] || [];
  };

  const handleSelectMarket = (market: 'spread' | 'total' | 'moneyline') => { setChartMarket(market); setChartViewMode('line'); };

  // Lazy-load line history
  const handleTabChange = async (tab: string) => {
    setActiveTab(tab);
    const tabToPeriod: Record<string, string> = { 'full': 'full', '1h': 'h1', '2h': 'h2', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const periodKey = tabToPeriod[tab];
    if (!periodKey || tab === 'full' || tab === 'team' || tab === 'alt') return;
    if (lazyLineHistory[periodKey]) return;
    if (loadingPeriods.has(periodKey)) return;
    const serverData = marketGroups.lineHistory?.[periodKey];
    if (serverData?.spread?.length > 0 || serverData?.moneyline?.length > 0 || serverData?.total?.length > 0) return;
    setLoadingPeriods(prev => new Set(prev).add(periodKey));
    try {
      const res = await fetch(`/api/lines/${gameData.id}?period=${periodKey}`);
      if (res.ok) {
        const data = await res.json();
        setLazyLineHistory(prev => ({ ...prev, [periodKey]: { spread: data.spread || [], moneyline: data.moneyline || [], total: data.total || [] } }));
      }
    } catch (e) {
      console.error(`[CLIENT] Failed to lazy-load line history for ${periodKey}:`, e);
    } finally {
      setLoadingPeriods(prev => { const next = new Set(prev); next.delete(periodKey); return next; });
    }
  };

  const tabs = [
    { key: 'full', label: 'Full' },
    ...(availableTabs?.firstHalf ? [{ key: '1h', label: '1H' }] : []),
    ...(availableTabs?.secondHalf ? [{ key: '2h', label: '2H' }] : []),
    ...(availableTabs?.q1 && !isNHL ? [{ key: '1q', label: '1Q' }] : []),
    ...(availableTabs?.q2 && !isNHL ? [{ key: '2q', label: '2Q' }] : []),
    ...(availableTabs?.q3 && !isNHL ? [{ key: '3q', label: '3Q' }] : []),
    ...(availableTabs?.q4 && !isNHL ? [{ key: '4q', label: '4Q' }] : []),
    ...(availableTabs?.p1 && isNHL ? [{ key: '1p', label: '1P' }] : []),
    ...(availableTabs?.p2 && isNHL ? [{ key: '2p', label: '2P' }] : []),
    ...(availableTabs?.p3 && isNHL ? [{ key: '3p', label: '3P' }] : []),
    ...(availableTabs?.teamTotals ? [{ key: 'team', label: 'Team Tot' }] : []),
    ...(availableTabs?.alternates ? [{ key: 'alt', label: 'Alt Lines' }] : []),
  ];

  // Best edge for header
  const getBestEdge = () => {
    if (!activeCeq?.bestEdge || activeCeq.bestEdge.ceq < 60) return null;
    const be = activeCeq.bestEdge;
    const sideLabel = be.side === 'home' ? gameData.homeTeam : be.side === 'away' ? gameData.awayTeam : be.side === 'over' ? 'Over' : be.side === 'under' ? 'Under' : be.side;
    return { ceq: be.ceq, side: sideLabel, market: be.market === 'h2h' ? 'ML' : be.market };
  };

  return (
    <>
      {/* Desktop: Bloomberg Terminal Grid */}
      <div
        className="hidden lg:grid h-full relative"
        style={{
          gridTemplateRows: '36px minmax(140px, 1fr) minmax(120px, 1fr) minmax(180px, 2fr)',
          gridTemplateColumns: '2fr 3fr',
          gridTemplateAreas: `"header header" "chart fairline" "pillars ceqfactors" "markets markets"`,
          gap: '1px',
          background: '#27272a',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {/* Subtle scanline overlay */}
        <div className="pointer-events-none absolute inset-0 z-50" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)',
          mixBlendMode: 'multiply',
        }} />
        <TerminalHeader
          awayTeam={gameData.awayTeam}
          homeTeam={gameData.homeTeam}
          commenceTime={gameData.commenceTime}
          totalEdgeCount={totalEdgeCount}
          bestEdge={getBestEdge()}
          selectedBook={selectedBook}
          filteredBooks={filteredBooks}
          onSelectBook={setSelectedBook}
          isLive={isLive}
        />

        {/* Chart cell */}
        <div className="bg-[#0a0a0a] p-2 relative" style={{ gridArea: 'chart' }}>
          {isSpecialTab ? (
            <div className="h-full flex items-center justify-center text-zinc-500 text-[11px]">
              {activeTab === 'team' ? 'Team totals' : 'Alt lines'}
            </div>
          ) : (
            <>
              <LineMovementChart
                gameId={gameData.id}
                selection={chartSelection}
                lineHistory={getLineHistory()}
                selectedBook={selectedBook}
                homeTeam={gameData.homeTeam}
                awayTeam={gameData.awayTeam}
                viewMode={chartViewMode}
                onViewModeChange={setChartViewMode}
                commenceTime={gameData.commenceTime}
                sportKey={gameData.sportKey}
                compact
              />
              {showLiveLock && <LiveLockOverlay />}
            </>
          )}
        </div>

        <FairLinePanel
          pythonPillars={pythonPillarScores}
          marketGroups={marketGroups}
          homeTeam={gameData.homeTeam}
          awayTeam={gameData.awayTeam}
          sportKey={gameData.sportKey}
        />

        <PillarBarsCompact pythonPillars={pythonPillarScores} />

        <CEQBarsCompact ceq={activeCeq} />

        <MarketsTable
          gameData={gameData}
          marketGroups={marketGroups}
          bookmakers={bookmakers}
          activeTab={activeTab}
          onTabChange={handleTabChange}
          tabs={tabs}
          chartMarket={chartMarket}
          onSelectMarket={handleSelectMarket}
          ceq={activeCeq}
          teamTotalsCeq={teamTotalsCeq}
          sportKey={gameData.sportKey}
          selectedBook={selectedBook}
        />
      </div>

      {/* Mobile: Single-column scrollable fallback */}
      <div className="lg:hidden h-auto overflow-y-auto">
        <TerminalHeader
          awayTeam={gameData.awayTeam}
          homeTeam={gameData.homeTeam}
          commenceTime={gameData.commenceTime}
          totalEdgeCount={totalEdgeCount}
          bestEdge={getBestEdge()}
          selectedBook={selectedBook}
          filteredBooks={filteredBooks}
          onSelectBook={setSelectedBook}
          isLive={isLive}
        />

        <div className="p-2 space-y-2 bg-[#0a0a0a]">
          {/* Chart */}
          <div className="h-[200px] relative bg-zinc-900/50 rounded p-2">
            {!isSpecialTab ? (
              <>
                <LineMovementChart
                  gameId={gameData.id}
                  selection={chartSelection}
                  lineHistory={getLineHistory()}
                  selectedBook={selectedBook}
                  homeTeam={gameData.homeTeam}
                  awayTeam={gameData.awayTeam}
                  viewMode={chartViewMode}
                  onViewModeChange={setChartViewMode}
                  commenceTime={gameData.commenceTime}
                  sportKey={gameData.sportKey}
                />
                {showLiveLock && <LiveLockOverlay />}
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 text-[11px]">No chart for this tab</div>
            )}
          </div>

          {/* Fair Line */}
          <FairLinePanel
            pythonPillars={pythonPillarScores}
            marketGroups={marketGroups}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
            sportKey={gameData.sportKey}
          />

          {/* Pillars */}
          <PillarBarsCompact pythonPillars={pythonPillarScores} />

          {/* CEQ */}
          <CEQBarsCompact ceq={activeCeq} />

          {/* Markets */}
          <div className="min-h-[300px]">
            <MarketsTable
              gameData={gameData}
              marketGroups={marketGroups}
              bookmakers={bookmakers}
              activeTab={activeTab}
              onTabChange={handleTabChange}
              tabs={tabs}
              chartMarket={chartMarket}
              onSelectMarket={handleSelectMarket}
              ceq={activeCeq}
              teamTotalsCeq={teamTotalsCeq}
              sportKey={gameData.sportKey}
              selectedBook={selectedBook}
            />
          </div>
        </div>
      </div>
    </>
  );
}
