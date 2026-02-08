'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal, calculateFairMoneyline } from '@/lib/edge/engine/edgescout';

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

const PERIOD_MAP: Record<string, string> = {
  'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf',
  '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4',
  '1p': 'p1', '2p': 'p2', '3p': 'p3',
};

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
// Utilities
// ============================================================================

const abbrev = (name: string) => {
  const words = name.trim().split(/\s+/);
  return words[words.length - 1].slice(0, 3).toUpperCase();
};

const calcMedian = (arr: number[]): number | undefined => {
  if (arr.length === 0) return undefined;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

const americanToImplied = (odds: number): number => {
  if (odds < 0) return Math.abs(odds) / (Math.abs(odds) + 100);
  return 100 / (odds + 100);
};

// ============================================================================
// LineMovementChart — with OMI fair line overlay
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
  omiFairLine?: number;
}

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam, awayTeam, viewMode, onViewModeChange, commenceTime, sportKey, compact = false, omiFairLine }: LineMovementChartProps) {
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
  // Include OMI fair line in min/max so the Y axis accommodates it
  if (omiFairLine !== undefined) values.push(omiFairLine);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.1;

  const width = 400;
  const height = compact ? 120 : 180;
  const paddingLeft = compact ? 35 : 45;
  const paddingRight = 8;
  const paddingTop = compact ? 6 : 12;
  const paddingBottom = compact ? 14 : 22;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const dataValues = data.map(d => d.value); // original data values (without OMI line)
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
  const chartColor = '#e4e4e7'; // zinc-200 — book line is white/light
  const gradientId = `chart-grad-${gameId}-${effectiveViewMode}`;

  // OMI fair line Y position
  const omiLineY = omiFairLine !== undefined
    ? paddingTop + chartHeight - ((omiFairLine - minVal + padding) / (range + 2 * padding)) * chartHeight
    : null;

  const yLabels = compact ? [
    { value: minVal, y: paddingTop + chartHeight },
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
      {/* Header: tracking side + movement */}
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
          <div className="flex rounded overflow-hidden border border-zinc-700/50">
            {(isGameLive ? ['30M', '1H', '3H', '6H', '24H', 'ALL'] as TimeRange[] : ['1H', '3H', '6H', '24H', 'ALL'] as TimeRange[]).map(r => (
              <button key={r} onClick={() => setTimeRange(r)} className={`px-1 py-0 text-[8px] font-medium ${timeRange === r ? 'bg-zinc-600 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>{r}</button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-1 text-[10px]" style={{ fontVariantNumeric: 'tabular-nums' }}>
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
              <stop offset="0%" stopColor={chartColor} stopOpacity="0.08" />
              <stop offset="100%" stopColor={chartColor} stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* OMI fair line — horizontal dashed cyan */}
          {omiLineY !== null && (
            <>
              <line
                x1={paddingLeft} y1={omiLineY} x2={width - paddingRight} y2={omiLineY}
                stroke="#22d3ee" strokeWidth="1" strokeDasharray="4 3" opacity="0.7"
              />
              <text x={width - paddingRight - 2} y={omiLineY - 4} textAnchor="end" fill="#22d3ee" fontSize="8" fontWeight="bold">OMI</text>
            </>
          )}

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
// TerminalHeader — 36px bar (modified: no edges, shows active market)
// ============================================================================

function TerminalHeader({
  awayTeam, homeTeam, commenceTime, activeMarket, selectedBook, filteredBooks, onSelectBook, isLive,
}: {
  awayTeam: string; homeTeam: string; commenceTime?: string; activeMarket: string;
  selectedBook: string; filteredBooks: string[]; onSelectBook: (book: string) => void; isLive: boolean;
}) {
  const [bookOpen, setBookOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) { if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setBookOpen(false); }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const dateStr = commenceTime
    ? new Date(commenceTime).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) + ' ET'
    : '';

  const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'Moneyline' };

  return (
    <div className="bg-[#0a0a0a] flex items-center justify-between px-3 h-[36px] min-h-[36px]" style={{ gridArea: 'header', borderBottom: '2px solid rgba(6, 78, 59, 0.3)', boxShadow: '0 1px 8px rgba(16, 185, 129, 0.06)' }}>
      <div className="flex items-center gap-3">
        <a href="/edge/portal/sports" className="text-zinc-500 hover:text-zinc-300 transition-colors">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
        </a>
        <span className="text-[13px] font-bold text-zinc-100 tracking-tight font-mono">
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
        <span className="text-[10px] text-zinc-400">Viewing: <span className="text-cyan-400 font-medium">{marketLabels[activeMarket] || activeMarket}</span></span>
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
// OmiFairPricing — the centerpiece
// ============================================================================

type ActiveMarket = 'spread' | 'total' | 'moneyline';

interface BookRow {
  key: string;
  name: string;
  color: string;
  line: string;
  juice: string;
  gap: number;
  signal: 'MISPRICED' | 'VALUE' | 'FAIR' | 'SHARP';
}

function OmiFairPricing({
  pythonPillars, bookmakers, gameData, sportKey, availableTabs,
  activeMarket, activePeriod, onMarketChange, onPeriodChange,
  chartViewMode, onViewModeChange,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  bookmakers: Record<string, any>;
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string };
  sportKey: string;
  availableTabs?: GameDetailClientProps['availableTabs'];
  activeMarket: ActiveMarket;
  activePeriod: string;
  onMarketChange: (m: ActiveMarket) => void;
  onPeriodChange: (p: string) => void;
  chartViewMode: ChartViewMode;
  onViewModeChange: (mode: ChartViewMode) => void;
}) {
  const isSoccer = sportKey?.includes('soccer') ?? false;
  const isNHL = sportKey?.includes('icehockey') ?? false;
  const periodKey = PERIOD_MAP[activePeriod] || 'fullGame';

  // Collect all sportsbook data for this period
  const allBooks = Object.entries(bookmakers)
    .filter(([key]) => {
      const config = BOOK_CONFIG[key];
      return !config || config.type === 'sportsbook'; // include unknown books as sportsbooks
    })
    .map(([key, data]) => ({
      key,
      name: BOOK_CONFIG[key]?.name || key.charAt(0).toUpperCase() + key.slice(1),
      color: BOOK_CONFIG[key]?.color || '#6b7280',
      markets: (data as any).marketGroups?.[periodKey],
    }))
    .filter(b => b.markets);

  // Calculate consensus lines
  const spreadLines = allBooks.map(b => b.markets?.spreads?.home?.line).filter((v): v is number => v !== undefined);
  const totalLines = allBooks.map(b => b.markets?.totals?.line).filter((v): v is number => v !== undefined);
  const consensusSpread = calcMedian(spreadLines);
  const consensusTotal = calcMedian(totalLines);

  // OMI fair lines
  const omiFairSpread = pythonPillars && consensusSpread !== undefined
    ? calculateFairSpread(consensusSpread, pythonPillars.composite) : null;
  const omiFairTotal = pythonPillars && consensusTotal !== undefined
    ? calculateFairTotal(consensusTotal, pythonPillars.gameEnvironment) : null;
  const omiFairML = pythonPillars
    ? calculateFairMoneyline(pythonPillars.composite) : null;

  // Signal determination
  const getSignal = (gap: number, market: ActiveMarket): BookRow['signal'] => {
    const thresholds = market === 'moneyline'
      ? { mispriced: 10, value: 5, sharp: 1 }
      : { mispriced: 1.0, value: 0.5, sharp: 0.25 };
    if (gap <= thresholds.sharp) return 'SHARP';
    if (gap < thresholds.value) return 'FAIR';
    if (gap < thresholds.mispriced) return 'VALUE';
    return 'MISPRICED';
  };

  const signalConfig: Record<BookRow['signal'], { badge: string; border: string; icon: string }> = {
    'MISPRICED': { badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', border: 'border-l-emerald-400', icon: '\u25CF' },
    'VALUE': { badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30', border: 'border-l-amber-400', icon: '\u25CF' },
    'FAIR': { badge: 'bg-zinc-700/50 text-zinc-400 border-zinc-600/30', border: 'border-l-zinc-600', icon: '\u25CB' },
    'SHARP': { badge: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30', border: 'border-l-cyan-400', icon: '\u25C6' },
  };

  // Build book rows for the active market
  const buildBookRows = (): BookRow[] => {
    const rows: BookRow[] = [];
    for (const book of allBooks) {
      if (activeMarket === 'spread') {
        const bookLine = book.markets?.spreads?.home?.line;
        const bookPrice = book.markets?.spreads?.home?.price;
        if (bookLine === undefined || !omiFairSpread) continue;
        const gap = Math.abs(Math.round((bookLine - omiFairSpread.fairLine) * 10) / 10);
        rows.push({
          key: book.key, name: book.name, color: book.color,
          line: formatSpread(bookLine),
          juice: bookPrice !== undefined ? formatOdds(bookPrice) : '--',
          gap,
          signal: getSignal(gap, 'spread'),
        });
      } else if (activeMarket === 'total') {
        const bookLine = book.markets?.totals?.line;
        const bookOverPrice = book.markets?.totals?.over?.price;
        if (bookLine === undefined || !omiFairTotal) continue;
        const gap = Math.abs(Math.round((bookLine - omiFairTotal.fairLine) * 10) / 10);
        rows.push({
          key: book.key, name: book.name, color: book.color,
          line: `${bookLine}`,
          juice: bookOverPrice !== undefined ? formatOdds(bookOverPrice) : '--',
          gap,
          signal: getSignal(gap, 'total'),
        });
      } else {
        // Moneyline — show both sides, gap = implied prob diff, juice = vig%
        const bookHomeOdds = book.markets?.h2h?.home?.price;
        const bookAwayOdds = book.markets?.h2h?.away?.price;
        if (bookHomeOdds === undefined || !omiFairML) continue;
        const bookImplied = americanToImplied(bookHomeOdds) * 100;
        const omiImplied = americanToImplied(omiFairML.homeOdds) * 100;
        const gap = Math.abs(Math.round((bookImplied - omiImplied) * 10) / 10);
        // Vig = sum of implied probabilities - 100%
        const vig = bookAwayOdds !== undefined
          ? Math.round((americanToImplied(bookHomeOdds) + americanToImplied(bookAwayOdds) - 1) * 1000) / 10
          : undefined;
        rows.push({
          key: book.key, name: book.name, color: book.color,
          line: bookAwayOdds !== undefined
            ? `${formatOdds(bookHomeOdds)} / ${formatOdds(bookAwayOdds)}`
            : formatOdds(bookHomeOdds),
          juice: vig !== undefined ? `${vig.toFixed(1)}%` : '--',
          gap,
          signal: getSignal(gap, 'moneyline'),
        });
      }
    }
    return rows.sort((a, b) => b.gap - a.gap);
  };

  const bookRows = buildBookRows();

  // Format OMI fair line display
  const getOmiFairLineDisplay = (): string => {
    if (!pythonPillars) return 'N/A';
    if (activeMarket === 'spread') {
      return omiFairSpread ? formatSpread(omiFairSpread.fairLine) : 'N/A';
    }
    if (activeMarket === 'total') {
      return omiFairTotal ? `${omiFairTotal.fairLine}` : 'N/A';
    }
    if (omiFairML) {
      return `${abbrev(gameData.homeTeam)} ${formatOdds(omiFairML.homeOdds)} / ${abbrev(gameData.awayTeam)} ${formatOdds(omiFairML.awayOdds)}`;
    }
    return 'N/A';
  };

  const gapUnit = activeMarket === 'moneyline' ? '%' : 'pts';

  // Period tabs
  const periodTabs = [
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
  ];

  return (
    <div className="bg-[#0a0a0a] p-3 h-full flex flex-col overflow-auto" style={{ gridArea: 'pricing' }}>
      {/* Market tabs + Period sub-tabs + Line/Price toggle */}
      <div className="flex flex-col gap-1.5 mb-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex gap-0 border-b border-zinc-800">
            {(['spread', 'total', 'moneyline'] as const).filter(m => !isSoccer || m !== 'spread').map(m => (
              <button key={m} onClick={() => onMarketChange(m)}
                className={`px-3 py-1.5 text-[11px] font-medium transition-all relative ${activeMarket === m ? 'text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>
                {m.charAt(0).toUpperCase() + m.slice(1)}
                {activeMarket === m && <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-cyan-400" style={{ boxShadow: '0 1px 4px rgba(34,211,238,0.3)' }} />}
              </button>
            ))}
          </div>
          {/* Line / Price toggle */}
          {activeMarket !== 'moneyline' && (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              <button
                onClick={() => onViewModeChange('line')}
                className={`px-2 py-0.5 text-[9px] font-medium transition-colors ${chartViewMode === 'line' ? 'bg-zinc-700 text-zinc-100' : 'bg-transparent text-zinc-500 hover:text-zinc-300'}`}
              >Line</button>
              <button
                onClick={() => onViewModeChange('price')}
                className={`px-2 py-0.5 text-[9px] font-medium transition-colors ${chartViewMode === 'price' ? 'bg-zinc-700 text-zinc-100' : 'bg-transparent text-zinc-500 hover:text-zinc-300'}`}
              >Price</button>
            </div>
          )}
        </div>
        {/* Period sub-tabs — left-aligned below market tabs */}
        <div className="flex gap-0">
          {periodTabs.map(tab => (
            <button key={tab.key} onClick={() => onPeriodChange(tab.key)}
              className={`px-2 py-1 text-[9px] font-medium transition-all ${activePeriod === tab.key ? 'text-zinc-100 bg-zinc-800/80 rounded' : 'text-zinc-600 hover:text-zinc-400'}`}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* OMI Fair Line — the anchor */}
      <div className="mb-3 flex-shrink-0">
        <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">OMI Fair Line</div>
        <div className="text-[22px] font-bold font-mono text-cyan-400" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {getOmiFairLineDisplay()}
        </div>
        <div className="text-[10px] text-zinc-500 mt-0.5">
          {pythonPillars
            ? `Based on 6-pillar composite (${pythonPillars.composite}) and market analysis`
            : 'Pillar data unavailable — fair line cannot be calculated'}
        </div>
      </div>

      {/* Book comparison table */}
      {bookRows.length > 0 ? (
        <div className="flex-1 min-h-0" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {/* Table header */}
          {(() => {
            const gridCols = activeMarket === 'moneyline'
              ? 'grid-cols-[2px_100px_130px_50px_60px_80px]'
              : 'grid-cols-[2px_120px_80px_60px_60px_90px]';
            return (
              <>
                <div className={`grid ${gridCols} gap-px text-[9px] text-zinc-500 uppercase tracking-widest font-medium mb-px`}>
                  <div />
                  <div className="bg-[#0a0a0a] px-2 py-1">Book</div>
                  <div className="bg-[#0a0a0a] px-1 py-1 text-center">{activeMarket === 'moneyline' ? 'Odds' : 'Their Line'}</div>
                  <div className="bg-[#0a0a0a] px-1 py-1 text-center">{activeMarket === 'moneyline' ? 'Vig' : 'Juice'}</div>
                  <div className="bg-[#0a0a0a] px-1 py-1 text-center">Gap{activeMarket === 'moneyline' ? '%' : ''}</div>
                  <div className="bg-[#0a0a0a] px-1 py-1 text-center">Signal</div>
                </div>
                {/* Book rows */}
                {bookRows.map((row, idx) => {
                  const sc = signalConfig[row.signal];
                  const gapColor = row.signal === 'MISPRICED' ? 'text-emerald-400' :
                    row.signal === 'VALUE' ? 'text-amber-400' :
                    row.signal === 'SHARP' ? 'text-cyan-400' : 'text-zinc-500';
                  return (
                    <div key={row.key} className={`grid ${gridCols} gap-px mb-px group`}>
                      {/* Left accent border */}
                      <div style={{ backgroundColor: row.signal === 'MISPRICED' ? '#34d399' : row.signal === 'VALUE' ? '#fbbf24' : row.signal === 'SHARP' ? '#22d3ee' : '#52525b' }} />
                      {/* Book name */}
                      <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-2 py-1.5 flex items-center gap-1.5 transition-colors">
                        <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: row.color }} />
                        <span className="text-[11px] font-medium text-zinc-200 truncate">{row.name}</span>
                      </div>
                      {/* Their line / Odds */}
                      <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-1.5 text-center transition-colors">
                        <span className="text-[11px] font-mono text-zinc-100">{row.line}</span>
                      </div>
                      {/* Juice / Vig */}
                      <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-1.5 text-center transition-colors">
                        <span className="text-[10px] font-mono text-zinc-400">{row.juice}</span>
                      </div>
                      {/* Gap */}
                      <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-1.5 text-center transition-colors">
                        <span className={`text-[11px] font-mono font-semibold ${gapColor}`}>
                          {row.gap > 0 ? row.gap.toFixed(1) : '0'}{activeMarket === 'moneyline' ? '%' : ''}
                        </span>
                      </div>
                      {/* Signal badge */}
                      <div className="bg-zinc-900/30 group-hover:bg-zinc-900/60 px-1 py-1.5 flex items-center justify-center transition-colors">
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${sc.badge}`}>
                          {row.signal} {sc.icon}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </>
            );
          })()}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-zinc-500 text-[11px]">
          {!pythonPillars ? 'Pillar data needed for fair pricing' : 'No sportsbook data available for this market'}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// PillarBarsCompact — dual-sided bars (center at 50%)
// ============================================================================

function PillarBarsCompact({
  pythonPillars, homeTeam, awayTeam,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  homeTeam: string;
  awayTeam: string;
}) {
  const pillars = [
    { key: 'execution', label: 'EXEC', weight: '20%', fullLabel: 'Execution' },
    { key: 'incentives', label: 'INCV', weight: '10%', fullLabel: 'Incentives' },
    { key: 'shocks', label: 'SHOK', weight: '25%', fullLabel: 'Shocks' },
    { key: 'timeDecay', label: 'TIME', weight: '10%', fullLabel: 'Time Decay' },
    { key: 'flow', label: 'FLOW', weight: '25%', fullLabel: 'Flow' },
    { key: 'gameEnvironment', label: 'ENV', weight: '10%', fullLabel: 'Game Env' },
  ];

  const getBarColor = (score: number) => {
    if (score >= 65) return '#34d399'; // emerald-400
    if (score >= 55) return '#059669'; // emerald-600
    if (score >= 45) return '#71717a'; // zinc-500
    if (score >= 35) return '#f59e0b'; // amber-500
    return '#f87171'; // red-400
  };

  const getTextColor = (score: number) => {
    if (score >= 65) return 'text-emerald-400';
    if (score >= 55) return 'text-emerald-600';
    if (score >= 45) return 'text-zinc-400';
    if (score >= 35) return 'text-amber-400';
    return 'text-red-400';
  };

  const homeAbbrev = abbrev(homeTeam);
  const awayAbbrev = abbrev(awayTeam);

  if (!pythonPillars) {
    return <div className="flex items-center justify-center text-[10px] text-zinc-600 py-2">No pillar data</div>;
  }

  return (
    <div className="flex flex-col gap-1">
      {/* Team labels row */}
      <div className="flex items-center mb-0.5">
        <span className="text-[8px] text-zinc-500 font-mono w-16" />
        <span className="text-[8px] text-zinc-500 font-mono w-6 text-right">{awayAbbrev}</span>
        <div className="flex-1" />
        <span className="text-[8px] text-zinc-500 font-mono w-6">{homeAbbrev}</span>
        <span className="w-6" />
      </div>
      {pillars.map(p => {
        const score = (pythonPillars as any)[p.key] as number;
        const barColor = getBarColor(score);
        // Dual-sided: bar extends from center (50%)
        // score > 50: bar fills right (home-favored)
        // score < 50: bar fills left (away-favored)
        const barWidth = Math.abs(score - 50); // 0-50 range
        const isRight = score >= 50;
        return (
          <div key={p.key} className="flex items-center gap-1">
            <span className="text-[9px] text-zinc-500 w-16 font-mono truncate" title={p.fullLabel}>
              {p.label} <span className="text-zinc-600">({p.weight})</span>
            </span>
            <div className="flex-1 h-[6px] bg-zinc-800 rounded-sm relative overflow-hidden">
              {/* Center line */}
              <div className="absolute left-1/2 top-0 w-px h-full bg-zinc-600 z-10" />
              {isRight ? (
                <div
                  className="absolute top-0 h-full rounded-sm"
                  style={{ left: '50%', width: `${barWidth}%`, backgroundColor: barColor }}
                />
              ) : (
                <div
                  className="absolute top-0 h-full rounded-sm"
                  style={{ left: `${score}%`, width: `${barWidth}%`, backgroundColor: barColor }}
                />
              )}
            </div>
            <span className={`text-[9px] font-mono w-6 text-right font-semibold ${getTextColor(score)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>{score}</span>
          </div>
        );
      })}
      {/* Composite */}
      <div className="flex items-center justify-between mt-1 pt-1 border-t border-zinc-800/50">
        <span className="text-[9px] text-zinc-500 font-mono">COMPOSITE</span>
        <span className={`text-[13px] font-bold font-mono ${getTextColor(pythonPillars.composite)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
          {pythonPillars.composite}
        </span>
      </div>
    </div>
  );
}

// ============================================================================
// WhyThisPrice — analysis panel (pillars + CEQ summary)
// ============================================================================

function WhyThisPrice({
  pythonPillars, ceq, homeTeam, awayTeam,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  ceq: GameCEQ | null | undefined;
  homeTeam: string;
  awayTeam: string;
}) {
  const homeAbbr = abbrev(homeTeam);
  const awayAbbr = abbrev(awayTeam);

  // CEQ summary — show bestEdge if available, otherwise show highest market CEQ
  const getCeqSummary = () => {
    if (ceq?.bestEdge) {
      const { ceq: ceqVal, confidence, market, side } = ceq.bestEdge;
      const marketLabel = market === 'h2h' ? 'Moneyline' : market.charAt(0).toUpperCase() + market.slice(1);
      const sideLabel = side === 'home' ? homeTeam : side === 'away' ? awayTeam : side === 'over' ? 'Over' : side === 'under' ? 'Under' : side;
      const confDesc: Record<string, string> = {
        'STRONG': 'Market strongly validates thesis',
        'EDGE': 'Market validates thesis',
        'WATCH': 'Market partially validates thesis',
        'PASS': 'Market does not validate thesis',
        'RARE': 'Exceptional edge detected',
      };
      return {
        ceq: ceqVal, confidence,
        text: `CEQ: ${ceqVal}% ${confidence} — ${confDesc[confidence] || 'Unknown'}`,
        detail: `${sideLabel} ${marketLabel}`,
      };
    }
    // No bestEdge — find highest CEQ across all markets
    if (!ceq) return null;
    const candidates: { ceq: number; confidence: string; label: string }[] = [];
    if (ceq.spreads?.home) candidates.push({ ceq: ceq.spreads.home.ceq, confidence: ceq.spreads.home.confidence, label: `${homeTeam} Spread` });
    if (ceq.spreads?.away) candidates.push({ ceq: ceq.spreads.away.ceq, confidence: ceq.spreads.away.confidence, label: `${awayTeam} Spread` });
    if (ceq.h2h?.home) candidates.push({ ceq: ceq.h2h.home.ceq, confidence: ceq.h2h.home.confidence, label: `${homeTeam} ML` });
    if (ceq.h2h?.away) candidates.push({ ceq: ceq.h2h.away.ceq, confidence: ceq.h2h.away.confidence, label: `${awayTeam} ML` });
    if (ceq.totals?.over) candidates.push({ ceq: ceq.totals.over.ceq, confidence: ceq.totals.over.confidence, label: 'Over' });
    if (ceq.totals?.under) candidates.push({ ceq: ceq.totals.under.ceq, confidence: ceq.totals.under.confidence, label: 'Under' });
    if (candidates.length === 0) return null;
    const best = candidates.sort((a, b) => b.ceq - a.ceq)[0];
    return {
      ceq: best.ceq, confidence: best.confidence,
      text: `CEQ: ${best.ceq}% ${best.confidence} — No strong edge detected`,
      detail: best.label,
    };
  };

  // Generate plain-English pillar summary
  const generatePillarSummary = (): string[] => {
    if (!pythonPillars) return [];
    const lines: string[] = [];
    const comp = pythonPillars.composite;
    const homeFavored = comp > 52;
    const awayFavored = comp < 48;
    const team = homeFavored ? homeAbbr : awayAbbr;

    // Main thesis line
    if (homeFavored || awayFavored) {
      const strength = Math.abs(comp - 50) > 10 ? 'strongly' : 'slightly';
      lines.push(`Pillars ${strength} favor ${team} (composite ${comp}).`);
    } else {
      lines.push(`No strong lean — composite near neutral (${comp}).`);
    }

    // Top driver(s)
    const pillarData = [
      { key: 'execution', label: 'Execution', score: pythonPillars.execution },
      { key: 'flow', label: 'Sharp flow', score: pythonPillars.flow },
      { key: 'shocks', label: 'Shocks', score: pythonPillars.shocks },
      { key: 'incentives', label: 'Incentives', score: pythonPillars.incentives },
      { key: 'timeDecay', label: 'Time decay', score: pythonPillars.timeDecay },
      { key: 'gameEnvironment', label: 'Game environment', score: pythonPillars.gameEnvironment },
    ];
    const extreme = pillarData
      .map(p => ({ ...p, deviation: Math.abs(p.score - 50) }))
      .sort((a, b) => b.deviation - a.deviation)
      .filter(p => p.deviation > 5);

    if (extreme.length > 0) {
      const top = extreme[0];
      const direction = top.score > 50 ? homeAbbr : awayAbbr;
      lines.push(`${top.label} (${top.score}) is the top driver, leaning ${direction}.`);
    }

    return lines;
  };

  const ceqSummary = getCeqSummary();
  const pillarSummary = generatePillarSummary();

  const confColor = ceqSummary ? (
    ceqSummary.confidence === 'STRONG' || ceqSummary.confidence === 'RARE' ? 'text-emerald-400' :
    ceqSummary.confidence === 'EDGE' ? 'text-blue-400' :
    ceqSummary.confidence === 'WATCH' ? 'text-amber-400' : 'text-zinc-500'
  ) : 'text-zinc-500';

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col" style={{ gridArea: 'analysis' }}>
      <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-2">Why This Price</span>
      <div className="flex-1 min-h-0 overflow-auto">
        <PillarBarsCompact pythonPillars={pythonPillars} homeTeam={homeTeam} awayTeam={awayTeam} />
        {/* Generated pillar summary */}
        {pillarSummary.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {pillarSummary.map((line, i) => (
              <p key={i} className="text-[10px] text-zinc-400 leading-tight">{line}</p>
            ))}
          </div>
        )}
        {/* CEQ summary line */}
        {ceqSummary ? (
          <div className="mt-2 pt-1.5 border-t border-zinc-800/50">
            <div className={`text-[10px] font-mono ${confColor}`}>
              {ceqSummary.text}
            </div>
            <div className="text-[9px] text-zinc-600 mt-0.5">{ceqSummary.detail}</div>
          </div>
        ) : (
          <div className="mt-2 pt-1.5 border-t border-zinc-800/50">
            <div className="text-[10px] text-zinc-600">
              {ceq === undefined ? 'CEQ loading...' : 'No market data for CEQ validation'}
            </div>
          </div>
        )}
      </div>
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
// Main GameDetailClient Component — OMI Fair Pricing Layout
// ============================================================================

export function GameDetailClient({
  gameData, bookmakers, availableBooks, availableTabs,
  userTier = 'tier_2', userEmail, isDemo = false,
  ceq, ceqByPeriod, teamTotalsCeq, edgeCountBreakdown,
  pythonPillarScores, totalEdgeCount = 0,
}: GameDetailClientProps) {
  const isSoccerGame = gameData.sportKey?.includes('soccer') ?? false;
  const [activeMarket, setActiveMarket] = useState<ActiveMarket>(isSoccerGame ? 'moneyline' : 'spread');
  const [activePeriod, setActivePeriod] = useState('full');
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
  const selectedBookMarkets = bookmakers[selectedBook]?.marketGroups || {};

  // CEQ by period
  const tabToPeriodKey: Record<string, keyof CEQByPeriod> = {
    'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf',
    '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4',
    '1p': 'p1', '2p': 'p2', '3p': 'p3',
  };
  const activePeriodKey = tabToPeriodKey[activePeriod] || 'fullGame';
  const activeCeq: GameCEQ | null | undefined = ceqByPeriod?.[activePeriodKey] ?? (activePeriod === 'full' ? ceq : null);

  // Chart selection (synced with activeMarket + activePeriod)
  const generatePriceMovement = (seed: string) => { const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0); const x = Math.sin(hashSeed) * 10000; return (x - Math.floor(x) - 0.5) * 0.15; };

  const getCurrentMarketValues = () => {
    const periodMapped = PERIOD_MAP[activePeriod] || 'fullGame';
    const markets = selectedBookMarkets[periodMapped];
    if (activeMarket === 'spread') {
      return { line: markets?.spreads?.home?.line, homeLine: markets?.spreads?.home?.line, awayLine: markets?.spreads?.away?.line, price: markets?.spreads?.home?.price, homePrice: markets?.spreads?.home?.price, awayPrice: markets?.spreads?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-spread-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-spread-away`) };
    }
    if (activeMarket === 'total') {
      return { line: markets?.totals?.line, price: markets?.totals?.over?.price, overPrice: markets?.totals?.over?.price, underPrice: markets?.totals?.under?.price, overPriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-total-over`), underPriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-total-under`) };
    }
    return { line: undefined, price: markets?.h2h?.home?.price, homePrice: markets?.h2h?.home?.price, awayPrice: markets?.h2h?.away?.price, homePriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-ml-home`), awayPriceMovement: generatePriceMovement(`${gameData.id}-${activePeriod}-ml-away`) };
  };

  const getChartSelection = (): ChartSelection => {
    const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q', '1p': '1P', '2p': '2P', '3p': '3P' };
    const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'ML' };
    const values = getCurrentMarketValues();
    return { type: 'market', market: activeMarket, period: activePeriod, label: `${periodLabels[activePeriod] || 'Full'} ${marketLabels[activeMarket]}`, ...values };
  };

  const chartSelection = getChartSelection();

  const getLineHistory = () => {
    const periodKeyMap: Record<string, string> = { 'full': 'full', '1h': 'h1', '2h': 'h2', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const periodKey = periodKeyMap[activePeriod] || 'full';
    const lazyData = lazyLineHistory[periodKey]?.[activeMarket];
    if (lazyData && lazyData.length > 0) return lazyData;
    return selectedBookMarkets.lineHistory?.[periodKey]?.[activeMarket] || [];
  };

  // Lazy-load line history for non-full-game periods
  const handlePeriodChange = async (period: string) => {
    setActivePeriod(period);
    const tabToPeriod: Record<string, string> = { 'full': 'full', '1h': 'h1', '2h': 'h2', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const periodKey = tabToPeriod[period];
    if (!periodKey || period === 'full') return;
    if (lazyLineHistory[periodKey]) return;
    if (loadingPeriods.has(periodKey)) return;
    const serverData = selectedBookMarkets.lineHistory?.[periodKey];
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

  // Compute OMI fair line for the convergence chart overlay
  const getOmiFairLineForChart = (): number | undefined => {
    if (!pythonPillarScores) return undefined;
    const periodMapped = PERIOD_MAP[activePeriod] || 'fullGame';
    // Get consensus from all sportsbooks for this period
    const allBooksForPeriod = Object.entries(bookmakers)
      .filter(([key]) => { const c = BOOK_CONFIG[key]; return !c || c.type === 'sportsbook'; })
      .map(([, data]) => (data as any).marketGroups?.[periodMapped])
      .filter(Boolean);

    if (activeMarket === 'spread') {
      const lines = allBooksForPeriod.map(m => m?.spreads?.home?.line).filter((v): v is number => v !== undefined);
      const consensus = calcMedian(lines);
      if (consensus === undefined) return undefined;
      return calculateFairSpread(consensus, pythonPillarScores.composite).fairLine;
    }
    if (activeMarket === 'total') {
      const lines = allBooksForPeriod.map(m => m?.totals?.line).filter((v): v is number => v !== undefined);
      const consensus = calcMedian(lines);
      if (consensus === undefined) return undefined;
      return calculateFairTotal(consensus, pythonPillarScores.gameEnvironment).fairLine;
    }
    // Moneyline: return fair home odds
    return calculateFairMoneyline(pythonPillarScores.composite).homeOdds;
  };

  const omiFairLineForChart = getOmiFairLineForChart();

  return (
    <>
      {/* Desktop: OMI Fair Pricing Grid */}
      <div
        className="hidden lg:grid h-full relative"
        style={{
          gridTemplateRows: '36px auto 1fr',
          gridTemplateColumns: '2fr 3fr',
          gridTemplateAreas: `"header header" "pricing pricing" "analysis chart"`,
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
          activeMarket={activeMarket}
          selectedBook={selectedBook}
          filteredBooks={filteredBooks}
          onSelectBook={setSelectedBook}
          isLive={isLive}
        />

        <OmiFairPricing
          pythonPillars={pythonPillarScores}
          bookmakers={bookmakers}
          gameData={gameData}
          sportKey={gameData.sportKey}
          availableTabs={availableTabs}
          activeMarket={activeMarket}
          activePeriod={activePeriod}
          onMarketChange={setActiveMarket}
          onPeriodChange={handlePeriodChange}
          chartViewMode={chartViewMode}
          onViewModeChange={setChartViewMode}
        />

        <WhyThisPrice
          pythonPillars={pythonPillarScores}
          ceq={activeCeq}
          homeTeam={gameData.homeTeam}
          awayTeam={gameData.awayTeam}
        />

        {/* Convergence chart */}
        <div className="bg-[#0a0a0a] p-2 relative" style={{ gridArea: 'chart' }}>
          <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1 block">Line Convergence</span>
          <div className="h-[calc(100%-20px)]">
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
              omiFairLine={omiFairLineForChart}
            />
          </div>
          {showLiveLock && <LiveLockOverlay />}
        </div>
      </div>

      {/* Mobile: Single-column scrollable fallback */}
      <div className="lg:hidden h-auto overflow-y-auto bg-[#0a0a0a]">
        <TerminalHeader
          awayTeam={gameData.awayTeam}
          homeTeam={gameData.homeTeam}
          commenceTime={gameData.commenceTime}
          activeMarket={activeMarket}
          selectedBook={selectedBook}
          filteredBooks={filteredBooks}
          onSelectBook={setSelectedBook}
          isLive={isLive}
        />

        <div className="p-2 space-y-2">
          <OmiFairPricing
            pythonPillars={pythonPillarScores}
            bookmakers={bookmakers}
            gameData={gameData}
            sportKey={gameData.sportKey}
            availableTabs={availableTabs}
            activeMarket={activeMarket}
            activePeriod={activePeriod}
            onMarketChange={setActiveMarket}
            onPeriodChange={handlePeriodChange}
            chartViewMode={chartViewMode}
            onViewModeChange={setChartViewMode}
          />

          <WhyThisPrice
            pythonPillars={pythonPillarScores}
            ceq={activeCeq}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
          />

          <div className="h-[200px] relative bg-zinc-900/50 rounded p-2">
            <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1 block">Line Convergence</span>
            <div className="h-[calc(100%-20px)]">
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
                omiFairLine={omiFairLineForChart}
              />
            </div>
            {showLiveLock && <LiveLockOverlay />}
          </div>
        </div>
      </div>
    </>
  );
}
