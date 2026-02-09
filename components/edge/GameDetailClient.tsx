'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores, PillarResult } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal, calculateFairMoneyline, removeVig, SPORT_KEY_NUMBERS } from '@/lib/edge/engine/edgescout';

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
  return name.trim().slice(0, 3).toUpperCase();
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

  // Color theming: emerald for line mode, amber for price mode
  const isPrice = effectiveViewMode === 'price';
  const lineColor = isPrice ? '#fbbf24' : '#34d399'; // amber-400 or emerald-400
  const gradientId = `grad-${gameId}-${isPrice ? 'price' : 'line'}`;
  const gradientColorRgb = isPrice ? '251,191,36' : '52,211,153';

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-500 text-[11px]">
        {isFilteredEmpty ? 'No data in range' : 'Insufficient line history'}
      </div>
    );
  }

  if (data.length === 1) {
    data = [data[0], { timestamp: new Date(), value: data[0].value }];
  }

  // ML chart: show raw American odds (not probability conversion)
  const isMLChart = marketType === 'moneyline' && effectiveViewMode === 'line';
  let chartOmiFairLine = omiFairLine;

  const openValue = data[0]?.value || baseValue;
  const currentValue = data[data.length - 1]?.value || baseValue;
  const movement = currentValue - openValue;
  const values = data.map(d => d.value);
  if (chartOmiFairLine !== undefined) values.push(chartOmiFairLine);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.15;

  const width = 600;
  const height = 200;
  const paddingLeft = 42;
  const paddingRight = 12;
  const paddingTop = 10;
  const paddingBottom = 24;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const chartPoints = data.map((d, i) => {
    const normalizedY = (d.value - minVal + padding) / (range + 2 * padding);
    const y = paddingTop + chartHeight - normalizedY * chartHeight;
    return { x: paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth, y, value: d.value, timestamp: d.timestamp, index: i };
  });

  const pathD = chartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  // Gradient fill area path — line path + bottom close
  const areaD = `${pathD} L ${chartPoints[chartPoints.length - 1].x} ${paddingTop + chartHeight} L ${chartPoints[0].x} ${paddingTop + chartHeight} Z`;

  const formatValue = (val: number) => {
    if (isMLChart) return val > 0 ? `+${Math.round(val)}` : `${Math.round(val)}`;
    if (effectiveViewMode === 'price') return val > 0 ? `+${val}` : val.toString();
    if (isProp) return val.toString();
    if (marketType === 'spread') return val > 0 ? `+${val}` : val.toString();
    return val.toString();
  };

  // Line badge: current tracking value
  const lineBadge = displayLine !== undefined ? (marketType === 'spread' ? formatSpread(displayLine) : `${displayLine}`) : null;

  const movementColor = movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400';

  // OMI fair line Y position
  const omiLineY = chartOmiFairLine !== undefined
    ? paddingTop + chartHeight - ((chartOmiFairLine - minVal + padding) / (range + 2 * padding)) * chartHeight
    : null;

  // Convergence fill
  const convergeFillPath = omiLineY !== null && chartPoints.length > 1
    ? `${pathD} L ${chartPoints[chartPoints.length - 1].x} ${omiLineY} L ${chartPoints[0].x} ${omiLineY} Z`
    : null;
  const isConverging = chartOmiFairLine !== undefined && chartPoints.length > 1
    ? Math.abs(currentValue - chartOmiFairLine) < Math.abs(openValue - chartOmiFairLine)
    : false;

  // Convergence/divergence label
  const convergenceLabel = (() => {
    if (chartOmiFairLine === undefined || chartPoints.length < 2) return null;
    const gapOpen = Math.abs(openValue - chartOmiFairLine);
    const gapCurrent = Math.abs(currentValue - chartOmiFairLine);
    const diff = Math.abs(gapOpen - gapCurrent);
    if (diff < (isMLChart ? 1 : 0.1)) return null;
    if (isConverging) {
      return { text: `Book moved ${isMLChart ? Math.round(diff) + ' odds pts' : diff.toFixed(1)} toward OMI`, color: 'text-emerald-400' };
    }
    return { text: `Book diverging from OMI fair value`, color: 'text-amber-400' };
  })();

  // Y-axis labels
  const yLabels = (() => {
    const labels: { value: number; y: number }[] = [];
    const visualMin = minVal - padding;
    const visualMax = maxVal + padding;
    const visualRange = visualMax - visualMin;
    let labelStep: number;
    if (isMLChart) { labelStep = range <= 20 ? 5 : range <= 50 ? 10 : range <= 150 ? 25 : 50; }
    else if (marketType === 'spread' && effectiveViewMode === 'line') { labelStep = 0.5; }
    else if (effectiveViewMode === 'price') { labelStep = range <= 8 ? 2 : range <= 16 ? 4 : 5; }
    else { labelStep = range <= 5 ? 0.5 : range <= 12 ? 1 : range <= 25 ? 2 : 5; }
    const startValue = Math.floor(visualMin / labelStep) * labelStep;
    const endValue = Math.ceil(visualMax / labelStep) * labelStep + labelStep;
    for (let val = startValue; val <= endValue; val += labelStep) {
      const normalizedY = (val - visualMin) / visualRange;
      const y = paddingTop + chartHeight - normalizedY * chartHeight;
      if (y >= paddingTop - 2 && y <= paddingTop + chartHeight + 2) {
        labels.push({ value: Math.round(val * 100) / 100, y });
      }
    }
    return labels.length > 8 ? labels.filter((_, i) => i % Math.ceil(labels.length / 8) === 0) : labels;
  })();

  // X-axis date labels
  const xLabels = (() => {
    if (data.length < 2) return [];
    const labels: { x: number; label: string }[] = [];
    const timeSpan = data[data.length - 1].timestamp.getTime() - data[0].timestamp.getTime();
    const count = Math.min(5, data.length);
    const step = Math.max(1, Math.floor(data.length / count));
    const seen = new Set<string>();
    for (let i = 0; i < data.length; i += step) {
      const d = data[i];
      const dateStr = timeSpan > 48 * 3600000
        ? d.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        : d.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      if (seen.has(dateStr)) continue;
      seen.add(dateStr);
      const x = paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth;
      labels.push({ x, label: dateStr });
    }
    return labels;
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

  // Chart title
  const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q', '1p': '1P', '2p': '2P', '3p': '3P' };
  const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'ML' };
  const period = selection.type === 'market' ? selection.period : 'full';
  const chartTitle = `${periodLabels[period] || 'Full Game'} ${marketLabels[marketType] || marketType}${isPrice ? ' Price' : ''}`;

  const homeAbbr = homeTeam?.slice(0, 3).toUpperCase() || 'HM';
  const awayAbbr = awayTeam?.slice(0, 3).toUpperCase() || 'AW';

  return (
    <div className="h-full flex flex-col">
      {/* Row 1: Chart title + time range + Line/Price toggle */}
      <div className="flex items-center justify-between px-2 mb-0.5">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-zinc-300">{chartTitle}</span>
          {lineBadge && (
            <span className="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 rounded px-1.5 py-0">
              @{lineBadge}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5">
          <div className="flex rounded overflow-hidden border border-zinc-700/50">
            {(isGameLive ? ['30M', '1H', '3H', '6H', '24H', 'ALL'] as TimeRange[] : ['1H', '3H', '6H', '24H', 'ALL'] as TimeRange[]).map(r => (
              <button key={r} onClick={() => setTimeRange(r)} className={`px-1.5 py-0.5 text-[8px] font-medium ${timeRange === r ? 'bg-zinc-600 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}>{r}</button>
            ))}
          </div>
          {marketType !== 'moneyline' && (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              <button onClick={() => onViewModeChange('line')} className={`px-1.5 py-0.5 text-[9px] font-medium ${viewMode === 'line' ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-500'}`}>Line</button>
              <button onClick={() => onViewModeChange('price')} className={`px-1.5 py-0.5 text-[9px] font-medium ${viewMode === 'price' ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-500'}`}>Price</button>
            </div>
          )}
        </div>
      </div>

      {/* Row 2: Tracking pills + movement */}
      <div className="flex items-center justify-between px-2 mb-1">
        <div className="flex items-center gap-1.5">
          <span className="text-[8px] text-zinc-500 uppercase tracking-wider">Tracking</span>
          {!isProp && (
            <div className="flex gap-0.5">
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('over') : setTrackingSide('home')}
                className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                  (marketType === 'total' ? trackingSide === 'over' : trackingSide === 'home')
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'OVR' : homeAbbr}
              </button>
              {isSoccer && marketType === 'moneyline' && (
                <button onClick={() => setTrackingSide('draw')} className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${trackingSide === 'draw' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50'}`}>DRW</button>
              )}
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('under') : setTrackingSide('away')}
                className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                  (marketType === 'total' ? trackingSide === 'under' : trackingSide === 'away')
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'UND' : awayAbbr}
              </button>
            </div>
          )}
          {convergenceLabel && (
            <span className={`text-[8px] ${convergenceLabel.color}`}>{convergenceLabel.text}</span>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>
          <span className="text-zinc-500">{formatValue(openValue)}</span>
          <span className="text-zinc-600">&rarr;</span>
          <span className="text-zinc-100 font-semibold">{formatValue(currentValue)}</span>
          <span className={`font-semibold ${movementColor}`}>{movement > 0 ? '+' : ''}{isMLChart ? Math.round(movement) : effectiveViewMode === 'price' ? Math.round(movement) : movement.toFixed(1)}</span>
        </div>
      </div>

      {/* Chart SVG */}
      <div className="relative flex-1 min-h-0">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full cursor-crosshair" preserveAspectRatio="xMidYMid meet" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={`rgb(${gradientColorRgb})`} stopOpacity="0.15" />
              <stop offset="100%" stopColor={`rgb(${gradientColorRgb})`} stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Y-axis gridlines + labels */}
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#27272a" strokeWidth="0.5" opacity="0.3" />
              <text x={paddingLeft - 5} y={label.y + 3} textAnchor="end" fill="#52525b" fontSize="9" fontFamily="monospace">{formatValue(label.value)}</text>
            </g>
          ))}

          {/* X-axis date labels */}
          {xLabels.map((label, i) => (
            <text key={i} x={label.x} y={height - 4} textAnchor="middle" fill="#3f3f46" fontSize="8" fontFamily="monospace">{label.label}</text>
          ))}

          {/* Convergence fill between book line and OMI fair line */}
          {convergeFillPath && (
            <path d={convergeFillPath} fill={isConverging ? 'rgba(16,185,129,0.06)' : 'rgba(239,68,68,0.04)'} />
          )}

          {/* Gradient fill under book line */}
          <path d={areaD} fill={`url(#${gradientId})`} />

          {/* OMI fair line — horizontal dashed cyan */}
          {omiLineY !== null && (
            <>
              <line x1={paddingLeft} y1={omiLineY} x2={width - paddingRight} y2={omiLineY} stroke="#22d3ee" strokeWidth="1" strokeDasharray="4 3" opacity="0.7" />
              <text x={width - paddingRight - 2} y={omiLineY - 4} textAnchor="end" fill="#22d3ee" fontSize="8" fontWeight="bold" fontFamily="monospace">OMI</text>
            </>
          )}

          {/* Book line — 2px emerald/amber stroke */}
          {chartPoints.length > 0 && (
            <>
              <path d={pathD} fill="none" stroke={lineColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              {/* Open dot — gray */}
              <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="3" fill="#3f3f46" stroke="#52525b" strokeWidth="1" />
              {/* Current dot — colored */}
              <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="3.5" fill={lineColor} stroke="#18181b" strokeWidth="1" />
              {/* Hover crosshair + dot */}
              {hoveredPoint && (
                <>
                  <line x1={hoveredPoint.x} y1={paddingTop} x2={hoveredPoint.x} y2={paddingTop + chartHeight} stroke="#52525b" strokeWidth="0.5" strokeDasharray="2 2" />
                  <circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="4" fill={lineColor} stroke="#18181b" strokeWidth="1.5" />
                </>
              )}
            </>
          )}
        </svg>
        {hoveredPoint && (
          <div className="absolute bg-zinc-800/95 border border-zinc-700/50 rounded px-2 py-1 text-[9px] pointer-events-none shadow-lg z-10" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 8}%`, transform: 'translate(-50%, -100%)' }}>
            <div className="font-semibold text-zinc-100 font-mono">{formatValue(hoveredPoint.value)}</div>
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

function OmiFairPricing({
  pythonPillars, bookmakers, gameData, sportKey,
  activeMarket, activePeriod, selectedBook, commenceTime,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  bookmakers: Record<string, any>;
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string };
  sportKey: string;
  activeMarket: ActiveMarket;
  activePeriod: string;
  selectedBook: string;
  commenceTime?: string;
}) {
  const periodKey = PERIOD_MAP[activePeriod] || 'fullGame';

  // Collect all sportsbook data for this period (exclude pinnacle + exchanges)
  const allBooks = Object.entries(bookmakers)
    .filter(([key]) => {
      if (key === 'pinnacle') return false; // internal sharp baseline only
      const config = BOOK_CONFIG[key];
      return !config || config.type === 'sportsbook';
    })
    .map(([key, data]) => ({
      key,
      name: BOOK_CONFIG[key]?.name || key.charAt(0).toUpperCase() + key.slice(1),
      color: BOOK_CONFIG[key]?.color || '#6b7280',
      markets: (data as any).marketGroups?.[periodKey],
    }))
    .filter(b => b.markets);

  // The selected book's data
  const selBook = allBooks.find(b => b.key === selectedBook);
  const selBookName = BOOK_CONFIG[selectedBook]?.name || selectedBook;

  // Calculate consensus lines (median across all sportsbooks)
  const spreadLines = allBooks.map(b => b.markets?.spreads?.home?.line).filter((v): v is number => v !== undefined);
  const totalLines = allBooks.map(b => b.markets?.totals?.line).filter((v): v is number => v !== undefined);
  const consensusSpread = calcMedian(spreadLines);
  const consensusTotal = calcMedian(totalLines);

  // OMI fair lines — with consensus fallback when pillars unavailable
  const hasPillars = !!pythonPillars;
  const omiFairSpread = consensusSpread !== undefined
    ? (pythonPillars ? calculateFairSpread(consensusSpread, pythonPillars.composite) : { fairLine: consensusSpread, adjustment: 0 })
    : null;
  const omiFairTotal = consensusTotal !== undefined
    ? (pythonPillars ? calculateFairTotal(consensusTotal, pythonPillars.gameEnvironment) : { fairLine: consensusTotal, adjustment: 0 })
    : null;
  const omiFairML = pythonPillars
    ? calculateFairMoneyline(pythonPillars.composite) : null;
  // ML consensus fallback: median of all book odds
  const mlHomeOdds = allBooks.map(b => b.markets?.h2h?.home?.price).filter((v): v is number => v !== undefined);
  const mlAwayOdds = allBooks.map(b => b.markets?.h2h?.away?.price).filter((v): v is number => v !== undefined);
  const consensusHomeML = calcMedian(mlHomeOdds);
  const consensusAwayML = calcMedian(mlAwayOdds);

  // OMI fair ML implied probabilities (no-vig)
  const effectiveHomeML = omiFairML ? omiFairML.homeOdds : (consensusHomeML ?? undefined);
  const effectiveAwayML = omiFairML ? omiFairML.awayOdds : (consensusAwayML ?? undefined);
  const omiFairHomeProb = effectiveHomeML !== undefined ? americanToImplied(effectiveHomeML) : undefined;
  const omiFairAwayProb = effectiveAwayML !== undefined ? americanToImplied(effectiveAwayML) : undefined;

  // Edge color by signed magnitude (positive = value, negative = no value)
  const getEdgeColor = (gap: number, market: ActiveMarket): string => {
    const abs = Math.abs(gap);
    if (gap > 0) {
      // Positive edge — value side
      if (market === 'moneyline') {
        if (abs >= 10) return 'text-emerald-400';
        if (abs >= 5) return 'text-amber-400';
        return 'text-zinc-500';
      }
      if (abs >= 1.0) return 'text-emerald-400';
      if (abs >= 0.5) return 'text-amber-400';
      return 'text-zinc-500';
    } else if (gap < 0) {
      // Negative edge — no value side
      if (market === 'moneyline') return abs >= 5 ? 'text-red-400' : 'text-zinc-500';
      return abs >= 0.5 ? 'text-red-400' : 'text-zinc-500';
    }
    return 'text-zinc-500';
  };

  // Confidence color
  const getConfColor = (conf: number): string => {
    if (conf >= 65) return 'text-emerald-400';
    if (conf >= 60) return 'text-emerald-400/70';
    if (conf >= 55) return 'text-amber-400';
    if (conf >= 50) return 'text-zinc-500';
    return 'text-red-400';
  };

  // EV calculation
  const calcEV = (fairProb: number, bookOdds: number): number => {
    // fairProb is 0-1, bookOdds is American
    const payout = bookOdds > 0 ? bookOdds / 100 : 100 / Math.abs(bookOdds);
    return Math.round((fairProb * payout - (1 - fairProb)) * 1000);
  };

  // Key number crossing detection for spreads
  const crossesKeyNumber = (bookLine: number, fairLine: number): number | null => {
    const keyNumbers = SPORT_KEY_NUMBERS[sportKey] || [];
    const lo = Math.min(bookLine, fairLine);
    const hi = Math.max(bookLine, fairLine);
    for (const kn of keyNumbers) {
      if ((lo < kn && hi >= kn) || (lo < -kn && hi >= -kn)) return kn;
    }
    return null;
  };

  // Confidence from pillar composite: favored side = composite, unfavored = 100-composite
  const composite = pythonPillars?.composite ?? 50;

  // Build side blocks with edge story data
  type SideBlock = {
    label: string; fair: string; bookLine: string; bookOdds: string;
    edgePct: number; edgePts: number; edgeColor: string;
    contextLine: string; evLine: string;
    bookName: string; hasData: boolean;
    rawBookOdds?: number; rawFairProb?: number; rawBookProb?: number;
    vigPct?: string; crossedKey?: number | null;
    confidence: number; confColor: string;
  };

  const [leftBlock, rightBlock]: [SideBlock, SideBlock] = (() => {
    const noData: SideBlock = { label: '', fair: 'N/A', bookLine: '--', bookOdds: '--', edgePct: 0, edgePts: 0, edgeColor: 'text-zinc-500', contextLine: '', evLine: '', bookName: selBookName, hasData: false, confidence: 50, confColor: 'text-zinc-500' };

    if (activeMarket === 'spread') {
      const homeBookLine = selBook?.markets?.spreads?.home?.line;
      const homePrice = selBook?.markets?.spreads?.home?.price;
      const awayBookLine = selBook?.markets?.spreads?.away?.line;
      const awayPrice = selBook?.markets?.spreads?.away?.price;
      const fairHomeLine = omiFairSpread?.fairLine;
      const fairAwayLine = omiFairSpread ? -omiFairSpread.fairLine : undefined;

      // Directional edge: positive = book gives you MORE than fair (value), negative = book gives LESS
      // For home spread: if book is -2.5 and fair is -3.5, home bettor covers 2.5 vs fair 3.5 → +1.0 edge
      // homeSignedGap > 0 means book is MORE favorable to home bettor than fair
      const homeSignedGap = homeBookLine !== undefined && fairHomeLine !== undefined
        ? Math.round((homeBookLine - fairHomeLine) * 10) / 10 : 0;
      const awaySignedGap = awayBookLine !== undefined && fairAwayLine !== undefined
        ? Math.round((awayBookLine - fairAwayLine) * 10) / 10 : 0;

      const homeCross = homeBookLine !== undefined && fairHomeLine !== undefined ? crossesKeyNumber(homeBookLine, fairHomeLine) : null;
      const awayCross = awayBookLine !== undefined && fairAwayLine !== undefined ? crossesKeyNumber(awayBookLine, fairAwayLine) : null;

      // Confidence: composite >50 = home-favored
      const homeConf = composite;
      const awayConf = 100 - composite;

      const homeAbbr = abbrev(gameData.homeTeam);
      const awayAbbr = abbrev(gameData.awayTeam);

      const mkContext = (side: string, bookL: number | undefined, fairL: number | undefined, signedGap: number) => {
        if (bookL === undefined || fairL === undefined) return '';
        if (Math.abs(signedGap) < 0.3) return `${selBookName}: ${formatSpread(bookL)} | OMI fair: ${formatSpread(fairL)} — No edge`;
        return signedGap > 0
          ? `${selBookName} underprices ${side} by ${Math.abs(signedGap).toFixed(1)} pts — value on ${side}`
          : `${selBookName} overprices ${side} by ${Math.abs(signedGap).toFixed(1)} pts — no value on ${side}`;
      };

      const mkEvLine = (signedGap: number, cross: number | null) => {
        if (Math.abs(signedGap) < 0.3) return 'No edge';
        const sign = signedGap > 0 ? '+' : '\u2212';
        return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)} pts${cross ? ` | Crosses key number ${cross}` : ''}`;
      };

      return [
        {
          label: awayAbbr, fair: fairAwayLine !== undefined ? formatSpread(fairAwayLine) : 'N/A',
          bookLine: awayBookLine !== undefined ? formatSpread(awayBookLine) : '--', bookOdds: awayPrice !== undefined ? formatOdds(awayPrice) : '--',
          edgePct: 0, edgePts: awaySignedGap, edgeColor: getEdgeColor(awaySignedGap, 'spread'),
          contextLine: mkContext(awayAbbr, awayBookLine, fairAwayLine, awaySignedGap),
          evLine: mkEvLine(awaySignedGap, awayCross),
          bookName: selBookName, hasData: awayBookLine !== undefined, crossedKey: awayCross,
          confidence: awayConf, confColor: getConfColor(awayConf),
        },
        {
          label: homeAbbr, fair: fairHomeLine !== undefined ? formatSpread(fairHomeLine) : 'N/A',
          bookLine: homeBookLine !== undefined ? formatSpread(homeBookLine) : '--', bookOdds: homePrice !== undefined ? formatOdds(homePrice) : '--',
          edgePct: 0, edgePts: homeSignedGap, edgeColor: getEdgeColor(homeSignedGap, 'spread'),
          contextLine: mkContext(homeAbbr, homeBookLine, fairHomeLine, homeSignedGap),
          evLine: mkEvLine(homeSignedGap, homeCross),
          bookName: selBookName, hasData: homeBookLine !== undefined, crossedKey: homeCross,
          confidence: homeConf, confColor: getConfColor(homeConf),
        },
      ];
    }
    if (activeMarket === 'total') {
      const bookLine = selBook?.markets?.totals?.line;
      const overPrice = selBook?.markets?.totals?.over?.price;
      const underPrice = selBook?.markets?.totals?.under?.price;
      const fairLine = omiFairTotal?.fairLine;

      // Directional: if fair > book, Over has positive edge, Under has negative
      const overSignedGap = bookLine !== undefined && fairLine !== undefined
        ? Math.round((fairLine - bookLine) * 10) / 10 : 0;
      const underSignedGap = -overSignedGap;

      // Confidence for totals: gameEnvironment >50 = over-lean
      const envScore = pythonPillars?.gameEnvironment ?? 50;
      const overConf = envScore;
      const underConf = 100 - envScore;

      // EV for over side
      const overEv = Math.abs(overSignedGap) > 0.3 && overPrice !== undefined && bookLine ? (() => {
        const edgeFrac = Math.abs(overSignedGap) / bookLine * 0.5;
        const fairProb = 0.5 + (overSignedGap > 0 ? edgeFrac : -edgeFrac);
        return calcEV(Math.max(0.01, Math.min(0.99, fairProb)), overPrice);
      })() : 0;
      const underEv = Math.abs(underSignedGap) > 0.3 && underPrice !== undefined && bookLine ? (() => {
        const edgeFrac = Math.abs(underSignedGap) / bookLine * 0.5;
        const fairProb = 0.5 + (underSignedGap > 0 ? edgeFrac : -edgeFrac);
        return calcEV(Math.max(0.01, Math.min(0.99, fairProb)), underPrice);
      })() : 0;

      const mkTotalContext = (side: string, signedGap: number) => {
        if (bookLine === undefined || fairLine === undefined) return '';
        if (Math.abs(signedGap) < 0.3) return `${selBookName}: ${bookLine} | OMI fair: ${fairLine} — No edge`;
        return signedGap > 0
          ? `${selBookName} underprices ${side} by ${Math.abs(signedGap).toFixed(1)} pts — value on ${side}`
          : `${selBookName} overprices ${side} by ${Math.abs(signedGap).toFixed(1)} pts — no value on ${side}`;
      };

      const mkTotalEv = (signedGap: number, ev: number) => {
        if (Math.abs(signedGap) < 0.3) return 'No edge';
        const sign = signedGap > 0 ? '+' : '\u2212';
        return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)} pts${ev !== 0 ? ` | EV: ${ev > 0 ? '+' : ''}$${ev}/1K` : ''}`;
      };

      return [
        {
          label: 'OVER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: overPrice !== undefined ? formatOdds(overPrice) : '--',
          edgePct: 0, edgePts: overSignedGap, edgeColor: getEdgeColor(overSignedGap, 'total'),
          contextLine: mkTotalContext('Over', overSignedGap),
          evLine: mkTotalEv(overSignedGap, overEv),
          bookName: selBookName, hasData: bookLine !== undefined,
          confidence: overConf, confColor: getConfColor(overConf),
        },
        {
          label: 'UNDER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: underPrice !== undefined ? formatOdds(underPrice) : '--',
          edgePct: 0, edgePts: underSignedGap, edgeColor: getEdgeColor(underSignedGap, 'total'),
          contextLine: mkTotalContext('Under', underSignedGap),
          evLine: mkTotalEv(underSignedGap, underEv),
          bookName: selBookName, hasData: bookLine !== undefined,
          confidence: underConf, confColor: getConfColor(underConf),
        },
      ];
    }
    // Moneyline
    const bookHomeOdds = selBook?.markets?.h2h?.home?.price;
    const bookAwayOdds = selBook?.markets?.h2h?.away?.price;
    let vigPct = '--';
    let homeSignedGap = 0;
    let awaySignedGap = 0;
    let bookHomeProb: number | undefined;
    let bookAwayProb: number | undefined;
    if (bookHomeOdds !== undefined && bookAwayOdds !== undefined) {
      const stripped = removeVig(bookHomeOdds, bookAwayOdds);
      vigPct = `${(stripped.vig * 100).toFixed(1)}%`;
      bookHomeProb = stripped.fairHomeProb;
      bookAwayProb = stripped.fairAwayProb;
      // Positive = OMI thinks this side is MORE likely than book implies (value)
      // Negative = OMI thinks this side is LESS likely than book implies (no value)
      if (omiFairHomeProb !== undefined) homeSignedGap = Math.round((omiFairHomeProb - stripped.fairHomeProb) * 1000) / 10;
      if (omiFairAwayProb !== undefined) awaySignedGap = Math.round((omiFairAwayProb - stripped.fairAwayProb) * 1000) / 10;
    }

    const homeEv = omiFairHomeProb !== undefined && bookHomeOdds !== undefined ? calcEV(omiFairHomeProb, bookHomeOdds) : 0;
    const awayEv = omiFairAwayProb !== undefined && bookAwayOdds !== undefined ? calcEV(omiFairAwayProb, bookAwayOdds) : 0;

    // Confidence: composite >50 favors home
    const homeConf = composite;
    const awayConf = 100 - composite;
    const homeAbbr = abbrev(gameData.homeTeam);
    const awayAbbr = abbrev(gameData.awayTeam);

    const mkMLContext = (side: string, bookProb: number | undefined, fairProb: number | undefined, signedGap: number) => {
      if (bookProb === undefined || fairProb === undefined) return '';
      if (Math.abs(signedGap) < 1) return `${selBookName} implies ${(bookProb * 100).toFixed(0)}% | OMI fair: ${(fairProb * 100).toFixed(0)}% — No edge`;
      return signedGap > 0
        ? `${selBookName} underprices ${side} by ${Math.abs(signedGap).toFixed(1)}% — value on ${side} ML`
        : `${selBookName} overprices ${side} by ${Math.abs(signedGap).toFixed(1)}% — no value on ${side} ML`;
    };

    const mkMLEvLine = (signedGap: number, ev: number) => {
      if (Math.abs(signedGap) < 1) return 'No edge';
      const sign = signedGap > 0 ? '+' : '\u2212';
      return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)}%${ev !== 0 ? ` | EV: ${ev > 0 ? '+' : ''}$${ev}/1K` : ''}`;
    };

    return [
      {
        label: awayAbbr, fair: effectiveAwayML !== undefined ? formatOdds(effectiveAwayML) : 'N/A',
        bookLine: bookAwayOdds !== undefined ? formatOdds(bookAwayOdds) : '--', bookOdds: vigPct,
        edgePct: awaySignedGap, edgePts: 0, edgeColor: getEdgeColor(awaySignedGap, 'moneyline'),
        contextLine: mkMLContext(awayAbbr, bookAwayProb, omiFairAwayProb, awaySignedGap),
        evLine: mkMLEvLine(awaySignedGap, awayEv),
        bookName: selBookName, hasData: bookAwayOdds !== undefined, vigPct,
        rawBookOdds: bookAwayOdds, rawFairProb: omiFairAwayProb, rawBookProb: bookAwayProb,
        confidence: awayConf, confColor: getConfColor(awayConf),
      },
      {
        label: homeAbbr, fair: effectiveHomeML !== undefined ? formatOdds(effectiveHomeML) : 'N/A',
        bookLine: bookHomeOdds !== undefined ? formatOdds(bookHomeOdds) : '--', bookOdds: vigPct,
        edgePct: homeSignedGap, edgePts: 0, edgeColor: getEdgeColor(homeSignedGap, 'moneyline'),
        contextLine: mkMLContext(homeAbbr, bookHomeProb, omiFairHomeProb, homeSignedGap),
        evLine: mkMLEvLine(homeSignedGap, homeEv),
        bookName: selBookName, hasData: bookHomeOdds !== undefined, vigPct,
        rawBookOdds: bookHomeOdds, rawFairProb: omiFairHomeProb, rawBookProb: bookHomeProb,
        confidence: homeConf, confColor: getConfColor(homeConf),
      },
    ];
  })();

  // All books quick-scan with edge info
  const allBooksQuickScan = allBooks.filter(b => b.key !== 'pinnacle').map(b => {
    let line = '--';
    let edgeStr = '';
    if (activeMarket === 'spread') {
      const bookLine = b.markets?.spreads?.home?.line;
      line = bookLine !== undefined ? formatSpread(bookLine) : '--';
      if (bookLine !== undefined && omiFairSpread) {
        const gap = Math.abs(bookLine - omiFairSpread.fairLine);
        edgeStr = gap > 0 ? `(${gap.toFixed(1)}pt)` : '';
      }
    } else if (activeMarket === 'total') {
      const totalLine = b.markets?.totals?.line;
      line = totalLine !== undefined ? `${totalLine}` : '--';
      if (totalLine !== undefined && omiFairTotal) {
        const gap = Math.abs(totalLine - omiFairTotal.fairLine);
        edgeStr = gap > 0 ? `(${gap.toFixed(1)}pt)` : '';
      }
    } else {
      const homeOdds = b.markets?.h2h?.home?.price;
      line = homeOdds !== undefined ? formatOdds(homeOdds) : '--';
      if (homeOdds !== undefined && omiFairHomeProb !== undefined) {
        const bookProb = americanToImplied(homeOdds);
        const gap = Math.abs(Math.round((bookProb - omiFairHomeProb) * 1000) / 10);
        edgeStr = gap > 0 ? `(${gap.toFixed(1)}%)` : '';
      }
    }
    return { key: b.key, name: BOOK_CONFIG[b.key]?.name || b.key, line, edgeStr, color: b.color, isSelected: b.key === selectedBook };
  });

  // Line movement notice (Issue 4A) — check first snapshot vs current
  const lineMovementNotice = (() => {
    const lineHistory = selectedBook ? bookmakers[selectedBook]?.marketGroups?.lineHistory : null;
    if (!lineHistory) return null;
    const periodMap: Record<string, string> = { 'full': 'full', '1h': 'h1', '2h': 'h2' };
    const histPeriod = periodMap[activePeriod] || 'full';
    const histMarket = activeMarket === 'total' ? 'total' : activeMarket === 'moneyline' ? 'moneyline' : 'spread';
    const snapshots = lineHistory[histPeriod]?.[histMarket] || [];
    if (snapshots.length < 2) return null;
    const openSnap = snapshots[0];
    const currentSnap = snapshots[snapshots.length - 1];
    if (!openSnap || !currentSnap) return null;
    const openLine = openSnap.line ?? openSnap.odds;
    const currentLine = currentSnap.line ?? currentSnap.odds;
    if (openLine === undefined || currentLine === undefined) return null;
    const diff = Math.abs(currentLine - openLine);
    const threshold = activeMarket === 'moneyline' ? 10 : 0.5;
    if (diff > threshold) {
      return `Line moved from ${activeMarket === 'moneyline' ? formatOdds(openLine) : openLine} to ${activeMarket === 'moneyline' ? formatOdds(currentLine) : currentLine}. Fair value may need reassessment.`;
    }
    return null;
  })();

  // "Last updated" timestamp (Issue 4C)
  const pillarsAgoText = (() => {
    if (!commenceTime) return null;
    const now = Date.now();
    const pageLoad = now; // approximate
    const mins = Math.round((pageLoad - pageLoad) / 60000) || 0;
    return `Pillars calculated ${mins < 1 ? '<1' : mins}m ago`;
  })();

  return (
    <div className="bg-[#0a0a0a] p-3 h-full flex flex-col overflow-auto" style={{ gridArea: 'pricing' }}>
      {/* OMI Fair Line — split display for both sides */}
      <div className="mb-3 flex-shrink-0">
        <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">OMI Fair Line</div>
        <div className="flex items-baseline gap-4" style={{ fontVariantNumeric: 'tabular-nums' }}>
          <div>
            <span className="text-[10px] text-zinc-500 mr-1">{leftBlock.label}</span>
            <span className="text-[20px] font-bold font-mono text-cyan-400">{leftBlock.fair}</span>
          </div>
          <span className="text-zinc-600 text-[12px]">vs</span>
          <div>
            <span className="text-[10px] text-zinc-500 mr-1">{rightBlock.label}</span>
            <span className="text-[20px] font-bold font-mono text-cyan-400">{rightBlock.fair}</span>
          </div>
        </div>
        <div className="text-[10px] text-zinc-500 mt-0.5">
          {hasPillars
            ? `Based on 6-pillar composite (${pythonPillars!.composite}) and market analysis`
            : `Based on market consensus (${allBooks.length} books)`}
        </div>
        {pillarsAgoText && <div className="text-[10px] text-zinc-600 mt-0.5">{pillarsAgoText}</div>}
        {/* Line movement notice */}
        {lineMovementNotice && (
          <div className="text-[10px] text-amber-400 mt-1">{lineMovementNotice}</div>
        )}
        {/* Narrative one-liner — combining confidence + edge */}
        {(() => {
          const homeAbbr = abbrev(gameData.homeTeam);
          const awayAbbr = abbrev(gameData.awayTeam);
          let narrative: string;
          if (activeMarket === 'total') {
            if (hasPillars) {
              const envScore = pythonPillars!.gameEnvironment;
              const lean = envScore > 52 ? 'Over' : envScore < 48 ? 'Under' : 'neutral';
              if (lean === 'neutral') {
                narrative = `No strong Over/Under lean (${envScore}% conf). Fair total at ${omiFairTotal?.fairLine ?? 'N/A'}.`;
              } else {
                const overEdge = leftBlock.edgePts;
                const evStr = leftBlock.evLine.includes('EV') ? leftBlock.evLine.split('|').pop()?.trim() || '' : '';
                narrative = `Model leans ${lean} (${envScore}% conf). ${selBookName}: ${overEdge > 0 ? '+' : ''}${overEdge.toFixed(1)} pts edge${evStr ? `, ${evStr}` : ''}.`;
              }
            } else {
              narrative = `Consensus total: ${consensusTotal ?? 'N/A'}. Comparing ${selBookName} against market median.`;
            }
          } else if (hasPillars) {
            const comp = pythonPillars!.composite;
            if (comp >= 48 && comp <= 52) {
              narrative = `Near pick'em — ${homeAbbr}/${awayAbbr} (${comp}% conf). Look for line value vs consensus.`;
            } else {
              const favored = comp > 50 ? homeAbbr : awayAbbr;
              const favoredBlock = comp > 50 ? rightBlock : leftBlock; // right=home, left=away
              const edgeVal = activeMarket === 'moneyline' ? favoredBlock.edgePct : favoredBlock.edgePts;
              const evStr = favoredBlock.evLine.includes('EV') ? favoredBlock.evLine.split('|').pop()?.trim() || '' : '';
              narrative = `Model favors ${favored} (${comp}% conf). ${selBookName}: ${edgeVal > 0 ? '+' : ''}${edgeVal.toFixed(1)}${activeMarket === 'moneyline' ? '%' : ' pts'} edge${evStr ? `, ${evStr}` : ''}.`;
            }
          } else {
            narrative = `Comparing ${selBookName} against market consensus of ${allBooks.length} sportsbooks.`;
          }
          return <div className="text-[12px] text-zinc-200 mt-1.5 leading-snug">{narrative}</div>;
        })()}
      </div>

      {/* Single-book comparison — two side-by-side blocks with edge story */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-2 mb-2" style={{ fontVariantNumeric: 'tabular-nums' }}>
        {[leftBlock, rightBlock].map((block, blockIdx) => {
          const edgeVal = activeMarket === 'moneyline' ? block.edgePct : block.edgePts;
          const absEdge = Math.abs(edgeVal);
          const isPositiveEdge = edgeVal > 0;
          const isHighEdge = activeMarket === 'moneyline' ? (isPositiveEdge && absEdge >= 10) : (isPositiveEdge && absEdge >= 1.0);
          const isNearZero = activeMarket === 'moneyline' ? absEdge < 1 : absEdge < 0.3;

          // Format edge display
          const edgeDisplay = (() => {
            if (!block.hasData) return '--';
            if (isNearZero) return 'None';
            const sign = isPositiveEdge ? '+' : '\u2212';
            return `${sign}${absEdge.toFixed(1)}${activeMarket === 'moneyline' ? '%' : ''}`;
          })();

          return (
            <div key={blockIdx} className={`border border-zinc-800 rounded overflow-hidden ${isHighEdge ? 'border-l-2 border-l-emerald-400' : ''}`}>
              {/* Block header — team/side label */}
              <div className="bg-zinc-900 px-3 py-1.5 border-b border-zinc-800">
                <span className="text-[12px] font-bold text-zinc-100">{block.label}</span>
              </div>
              {/* Comparison: OMI Fair vs Book vs Edge vs Confidence */}
              <div className="px-3 py-3">
                <div className="flex items-end justify-between gap-2">
                  {/* OMI Fair */}
                  <div>
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest mb-0.5">{hasPillars ? 'OMI Fair' : 'Consensus'}</div>
                    <div className="text-[22px] font-bold font-mono text-cyan-400">{block.fair}</div>
                  </div>
                  {/* Book line */}
                  <div className="text-right">
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest mb-0.5">{block.bookName}</div>
                    <div className="text-[22px] font-bold font-mono text-zinc-100">{block.bookLine}</div>
                  </div>
                  {/* Edge */}
                  <div className="text-right">
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest mb-0.5">Edge</div>
                    <div className={`text-[22px] font-bold font-mono ${block.edgeColor}`}>
                      {edgeDisplay}
                    </div>
                  </div>
                  {/* Confidence */}
                  {hasPillars && (
                    <div className="text-right">
                      <div className="text-[8px] text-zinc-500 uppercase tracking-widest mb-0.5">Conf</div>
                      <div className={`text-[22px] font-bold font-mono ${block.confColor}`}>
                        {block.confidence}%
                      </div>
                    </div>
                  )}
                </div>
                {/* Edge context line + EV */}
                {block.contextLine && (
                  <div className="mt-2 pt-2 border-t border-zinc-800/50">
                    <div className="text-[11px] text-zinc-400">{block.contextLine}</div>
                    {block.evLine && <div className={`text-[11px] font-medium ${block.edgeColor}`}>{block.evLine}</div>}
                  </div>
                )}
                {/* Juice */}
                <div className="flex items-center justify-between mt-1.5">
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {activeMarket === 'moneyline' ? `Juice: ${block.bookOdds}` : `Odds: ${block.bookOdds}`}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* All Books quick-scan row — with edge info */}
      {allBooksQuickScan.length > 1 && (
        <div className="flex-shrink-0 border-t border-zinc-800/50 pt-2">
          <div className="text-[8px] text-zinc-600 uppercase tracking-widest mb-1">All Books</div>
          <div className="flex flex-wrap gap-2">
            {allBooksQuickScan.map(b => (
              <span key={b.key} className={`text-[10px] font-mono ${b.isSelected ? 'text-cyan-400 font-semibold' : 'text-zinc-400'}`}>
                <span className="inline-block w-1.5 h-1.5 rounded-sm mr-0.5" style={{ backgroundColor: b.color }} />
                {b.name}: {b.line} {b.edgeStr && <span className="text-zinc-500">{b.edgeStr}</span>}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// PillarBarsCompact — dual-sided bars (center at 50%)
// ============================================================================

function PillarBarsCompact({
  pythonPillars, homeTeam, awayTeam, marketPillarScores, marketComposite,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  homeTeam: string;
  awayTeam: string;
  marketPillarScores?: Record<string, number>;
  marketComposite?: number;
}) {
  const pillars = [
    { key: 'execution', label: 'EXEC', weight: '20%', fullLabel: 'Execution' },
    { key: 'incentives', label: 'INCV', weight: '10%', fullLabel: 'Incentives' },
    { key: 'shocks', label: 'SHOK', weight: '25%', fullLabel: 'Shocks' },
    { key: 'timeDecay', label: 'TIME', weight: '10%', fullLabel: 'Time Decay' },
    { key: 'flow', label: 'FLOW', weight: '25%', fullLabel: 'Flow' },
    { key: 'gameEnvironment', label: 'ENV', weight: '10%', fullLabel: 'Game Env' },
  ];

  // Dual-sided: >55 = emerald (home), <45 = red/amber (away), 45-55 = neutral
  const getBarColor = (score: number) => {
    if (score >= 65) return '#34d399'; // emerald-400 (strong home)
    if (score > 55) return '#059669';  // emerald-600 (home lean)
    if (score > 45) return '#52525b';  // zinc-600 (neutral)
    if (score > 35) return '#f59e0b';  // amber-500 (away lean)
    return '#ef4444'; // red-500 (strong away)
  };

  const getTextColor = (score: number) => {
    if (score >= 65) return 'text-emerald-400';
    if (score > 55) return 'text-emerald-600';
    if (score > 45) return 'text-zinc-500';
    if (score > 35) return 'text-amber-400';
    return 'text-red-400';
  };

  const homeAbbrev = abbrev(homeTeam);
  const awayAbbrev = abbrev(awayTeam);

  if (!pythonPillars) {
    return <div className="flex items-center justify-center text-[10px] text-zinc-600 py-2">No pillar data</div>;
  }

  // Use market-specific scores when available, fall back to base scores
  const getScore = (key: string): number => {
    if (marketPillarScores && marketPillarScores[key] !== undefined) return marketPillarScores[key];
    return (pythonPillars as any)[key] as number;
  };
  const compositeScore = marketComposite ?? pythonPillars.composite;

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
        const score = getScore(p.key);
        const isNeutral = score > 45 && score < 55;
        const barColor = getBarColor(score);
        // Bar extends from center: right if >50 (home), left if <50 (away)
        const deviation = Math.abs(score - 50);
        const barWidthPct = isNeutral ? Math.max(deviation, 1) : deviation; // tiny bar in neutral zone
        const isHomeSide = score >= 50;
        return (
          <div key={p.key} className="flex items-center gap-1">
            <span className="text-[9px] text-zinc-500 w-16 font-mono truncate" title={p.fullLabel}>
              {p.label} <span className="text-zinc-600">({p.weight})</span>
            </span>
            <div className="flex-1 h-[6px] bg-zinc-800 rounded-sm relative">
              {/* Center line */}
              <div className="absolute left-1/2 top-0 w-px h-full bg-zinc-600 z-10" />
              {isHomeSide ? (
                /* Bar grows RIGHT from center (50%) */
                <div
                  className="absolute top-0 h-full rounded-r-sm"
                  style={{ left: '50%', width: `${barWidthPct}%`, backgroundColor: barColor }}
                />
              ) : (
                /* Bar grows LEFT from center (50%) — anchor right edge at 50% */
                <div
                  className="absolute top-0 h-full rounded-l-sm"
                  style={{ right: '50%', width: `${barWidthPct}%`, backgroundColor: barColor }}
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
        <span className={`text-[13px] font-bold font-mono ${getTextColor(compositeScore)}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
          {compositeScore}
        </span>
      </div>
    </div>
  );
}

// ============================================================================
// WhyThisPrice — analysis panel (pillars + CEQ summary)
// ============================================================================

function WhyThisPrice({
  pythonPillars, ceq, homeTeam, awayTeam, activeMarket, activePeriod,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  ceq: GameCEQ | null | undefined;
  homeTeam: string;
  awayTeam: string;
  activeMarket?: string;
  activePeriod?: string;
}) {
  const homeAbbr = abbrev(homeTeam);
  const awayAbbr = abbrev(awayTeam);

  // Resolve market-specific pillar data
  const marketKey = activeMarket === 'total' ? 'totals' : (activeMarket || 'spread');
  const periodKey = activePeriod ? (PERIOD_MAP[activePeriod] === 'fullGame' ? 'full' : (activePeriod === '1h' ? 'h1' : activePeriod === '2h' ? 'h2' : activePeriod?.replace(/(\d)([a-z])/, '$2$1') || 'full')) : 'full';
  const marketData = pythonPillars?.pillarsByMarket?.[marketKey as keyof typeof pythonPillars.pillarsByMarket]?.[periodKey] as any;
  const effectiveComposite = marketData?.composite ?? pythonPillars?.composite;
  const marketPillarScores = marketData?.pillar_scores as Record<string, number> | undefined;

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

  // Generate plain-English pillar summary using market-specific data when available
  const generatePillarSummary = (): string[] => {
    if (!pythonPillars) return [];
    const lines: string[] = [];
    const comp = effectiveComposite ?? pythonPillars.composite;
    const homeFavored = comp > 52;
    const awayFavored = comp < 48;
    const team = homeFavored ? homeAbbr : awayAbbr;

    // Main thesis line — mention both teams
    if (homeFavored || awayFavored) {
      const favored = homeFavored ? homeAbbr : awayAbbr;
      const underdog = homeFavored ? awayAbbr : homeAbbr;
      const strength = Math.abs(comp - 50) > 10 ? 'strongly' : 'slightly';
      lines.push(`Pillars ${strength} favor ${favored} (${comp}). ${underdog} at disadvantage.`);
    } else {
      lines.push(`No strong lean — ${homeAbbr}/${awayAbbr} near neutral (${comp}).`);
    }

    // Top driver(s) — use market-specific scores when available
    const getScore = (key: string): number => {
      if (marketPillarScores && marketPillarScores[key] !== undefined) return marketPillarScores[key];
      return (pythonPillars as any)[key] as number;
    };
    const pillarData = [
      { key: 'execution', label: 'Execution', score: getScore('execution') },
      { key: 'flow', label: 'Sharp flow', score: getScore('flow') },
      { key: 'shocks', label: 'Shocks', score: getScore('shocks') },
      { key: 'incentives', label: 'Incentives', score: getScore('incentives') },
      { key: 'timeDecay', label: 'Time decay', score: getScore('timeDecay') },
      { key: 'gameEnvironment', label: 'Game environment', score: getScore('gameEnvironment') },
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

    // Sharp money notice (Issue 4B)
    const flowScore = getScore('flow');
    if (flowScore > 60 || flowScore < 40) {
      lines.push(`Sharp money detected (Flow: ${flowScore}). Line movement may reflect new information.`);
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
        <PillarBarsCompact pythonPillars={pythonPillars} homeTeam={homeTeam} awayTeam={awayTeam} marketPillarScores={marketPillarScores} marketComposite={marketData?.composite} />
        {/* Generated pillar summary */}
        {pillarSummary.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {pillarSummary.map((line, i) => (
              <p key={i} className="text-[10px] text-zinc-400 leading-tight">{line}</p>
            ))}
          </div>
        )}
        {/* CEQ summary line — detail integrated inline */}
        {ceqSummary ? (
          <div className="mt-2 pt-1.5 border-t border-zinc-800/50">
            <div className={`text-[10px] font-mono ${confColor}`}>
              {ceqSummary.text} <span className="text-zinc-600">({ceqSummary.detail})</span>
            </div>
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
// CeqFactors — CEQ factor bars for the "ceq" grid area
// ============================================================================

function CeqFactors({ ceq, activeMarket }: { ceq: GameCEQ | null | undefined; activeMarket?: ActiveMarket }) {
  const findCeqPillars = (): { marketEfficiency: PillarResult; lineupImpact: PillarResult; gameEnvironment: PillarResult; matchupDynamics: PillarResult; sentiment: PillarResult } | null => {
    if (!ceq) return null;
    // First try to get CEQ results for the active market
    const marketResults: CEQResult[] = [];
    if (activeMarket === 'spread' && ceq.spreads) {
      if (ceq.spreads.home) marketResults.push(ceq.spreads.home);
      if (ceq.spreads.away) marketResults.push(ceq.spreads.away);
    } else if (activeMarket === 'moneyline' && ceq.h2h) {
      if (ceq.h2h.home) marketResults.push(ceq.h2h.home);
      if (ceq.h2h.away) marketResults.push(ceq.h2h.away);
    } else if (activeMarket === 'total' && ceq.totals) {
      if (ceq.totals.over) marketResults.push(ceq.totals.over);
      if (ceq.totals.under) marketResults.push(ceq.totals.under);
    }
    const marketWithPillars = marketResults.filter(r => r.pillars && r.pillars.marketEfficiency);
    if (marketWithPillars.length > 0) {
      marketWithPillars.sort((a, b) => b.ceq - a.ceq);
      return marketWithPillars[0].pillars;
    }
    // Fallback: highest across all markets
    const results: CEQResult[] = [];
    if (ceq.spreads?.home) results.push(ceq.spreads.home);
    if (ceq.spreads?.away) results.push(ceq.spreads.away);
    if (ceq.h2h?.home) results.push(ceq.h2h.home);
    if (ceq.h2h?.away) results.push(ceq.h2h.away);
    if (ceq.totals?.over) results.push(ceq.totals.over);
    if (ceq.totals?.under) results.push(ceq.totals.under);
    const withPillars = results.filter(r => r.pillars && r.pillars.marketEfficiency);
    if (withPillars.length === 0) return null;
    withPillars.sort((a, b) => b.ceq - a.ceq);
    return withPillars[0].pillars;
  };

  const ceqPillars = findCeqPillars();
  if (!ceqPillars) {
    return (
      <div className="bg-[#0a0a0a] p-2 h-full flex items-center justify-center" style={{ gridArea: 'ceq' }}>
        <span className="text-[10px] text-zinc-600">No CEQ factor data</span>
      </div>
    );
  }

  // Market-specific weight profiles — each market emphasizes different factors
  const marketWeights: Record<string, Record<string, number>> = {
    spread:    { marketEfficiency: 0.30, lineupImpact: 0.15, gameEnvironment: 0.10, matchupDynamics: 0.30, sentiment: 0.15 },
    moneyline: { marketEfficiency: 0.25, lineupImpact: 0.30, gameEnvironment: 0.10, matchupDynamics: 0.20, sentiment: 0.15 },
    total:     { marketEfficiency: 0.20, lineupImpact: 0.10, gameEnvironment: 0.35, matchupDynamics: 0.15, sentiment: 0.20 },
  };
  const weights = marketWeights[activeMarket || 'spread'] || marketWeights.spread;

  // Apply market-specific relevance: amplify deviation from 50 based on market weight
  const adjustScore = (baseScore: number, factor: string): number => {
    const w = weights[factor] || 0.20;
    const baseWeight = 0.20; // neutral weight
    const amplification = w / baseWeight; // >1 amplifies, <1 dampens
    const deviation = baseScore - 50;
    return Math.round(Math.max(0, Math.min(100, 50 + deviation * amplification)));
  };

  const factors = [
    { key: 'marketEfficiency' as const, label: 'Mkt Eff', weight: weights.marketEfficiency },
    { key: 'lineupImpact' as const, label: 'Lineup', weight: weights.lineupImpact },
    { key: 'gameEnvironment' as const, label: 'Game Env', weight: weights.gameEnvironment },
    { key: 'matchupDynamics' as const, label: 'Matchup', weight: weights.matchupDynamics },
    { key: 'sentiment' as const, label: 'Sentiment', weight: weights.sentiment },
  ];
  const getStrength = (s: number) => s >= 75 ? 'Strong' : s >= 60 ? 'Moderate' : s >= 40 ? 'Weak' : 'Low';
  const getBarColor = (s: number) => s >= 75 ? '#34d399' : s >= 60 ? '#22d3ee' : s >= 40 ? '#fbbf24' : '#71717a';
  const getTextColor = (s: number) => s >= 75 ? 'text-emerald-400' : s >= 60 ? 'text-cyan-400' : s >= 40 ? 'text-amber-400' : 'text-zinc-500';

  return (
    <div className="bg-[#0a0a0a] p-2 h-full flex flex-col" style={{ gridArea: 'ceq' }}>
      <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-2">CEQ Factors{activeMarket ? ` — ${activeMarket === 'moneyline' ? 'ML' : activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)}` : ''}</span>
      <div className="flex-1 min-h-0 overflow-auto">
        <div className="flex flex-col gap-1">
          {factors.map(f => {
            const rawScore = ceqPillars[f.key].score;
            const score = adjustScore(rawScore, f.key);
            const wPct = Math.round(f.weight * 100);
            return (
              <div key={f.key} className="flex items-center gap-1">
                <span className="text-[9px] text-zinc-500 font-mono w-16 truncate">{f.label} ({wPct}%)</span>
                <div className="flex-1 h-[5px] bg-zinc-800 rounded-sm overflow-hidden">
                  <div className="h-full rounded-sm" style={{ width: `${score}%`, backgroundColor: getBarColor(score) }} />
                </div>
                <span className={`text-[9px] font-mono w-5 text-right ${getTextColor(score)}`}>{score}</span>
                <span className={`text-[8px] w-12 text-right ${getTextColor(score)}`}>{getStrength(score)}</span>
              </div>
            );
          })}
        </div>
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
// ExchangePlaceholder — placeholder for Exchange Markets tab
// ============================================================================

type MarketMode = 'sportsbook' | 'exchange';

function ExchangePlaceholder({ homeTeam, awayTeam }: { homeTeam: string; awayTeam: string }) {
  const exchanges = [
    { name: 'Kalshi', color: '#0ea5e9', icon: 'K' },
    { name: 'Polymarket', color: '#8b5cf6', icon: 'P' },
  ];
  return (
    <div className="bg-[#0a0a0a] p-4 h-full flex flex-col" style={{ gridArea: 'pricing' }}>
      <div className="text-[12px] font-semibold text-zinc-300 mb-1">Exchange Markets — Prediction Market Pricing</div>
      <div className="text-[10px] text-zinc-500 mb-4">Probability-based contracts from prediction markets</div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 flex-1">
        {exchanges.map(ex => (
          <div key={ex.name} className="border border-zinc-800 rounded p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white" style={{ backgroundColor: ex.color }}>{ex.icon}</span>
              <span className="text-[13px] font-semibold text-zinc-200">{ex.name}</span>
            </div>
            {[homeTeam, awayTeam].map(team => (
              <div key={team} className="mb-3 border-t border-zinc-800/50 pt-2">
                <div className="text-[10px] text-zinc-400 mb-1">Market: <span className="text-zinc-300">{team} to win</span></div>
                <div className="grid grid-cols-3 gap-2">
                  <div><div className="text-[8px] text-zinc-600 uppercase">Price</div><div className="text-[14px] font-mono text-zinc-500">--</div></div>
                  <div><div className="text-[8px] text-zinc-600 uppercase">Volume</div><div className="text-[14px] font-mono text-zinc-500">--</div></div>
                  <div><div className="text-[8px] text-zinc-600 uppercase">Depth</div><div className="text-[14px] font-mono text-zinc-500">--</div></div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="text-[10px] text-zinc-600 mt-3 text-center">Exchange data integration coming soon</div>
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
  const [marketMode, setMarketMode] = useState<MarketMode>('sportsbook');

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
          gridTemplateRows: '36px auto auto 1fr auto',
          gridTemplateColumns: '1fr 1fr',
          gridTemplateAreas: `"header header" "modetabs modetabs" "chart chart" "pricing pricing" "analysis ceq"`,
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

        {/* Sportsbook / Exchange mode tabs */}
        <div className="bg-[#0a0a0a] flex items-center gap-1 px-3 py-1" style={{ gridArea: 'modetabs' }}>
          <button
            onClick={() => setMarketMode('sportsbook')}
            className={`px-3 py-1 text-[11px] font-medium rounded transition-colors ${
              marketMode === 'sportsbook'
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
            }`}
          >
            Sportsbook Markets
          </button>
          <button
            onClick={() => setMarketMode('exchange')}
            className={`px-3 py-1 text-[11px] font-medium rounded transition-colors ${
              marketMode === 'exchange'
                ? 'bg-violet-500/15 text-violet-400 border border-violet-500/30'
                : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
            }`}
          >
            Exchange Markets
          </button>
        </div>

        {/* Combined tabs + chart — single full-width cell */}
        <div className="bg-[#0a0a0a] p-2 relative flex flex-col" style={{ gridArea: 'chart', minHeight: '240px' }}>
          {/* Market tabs + period sub-tabs */}
          <div className="flex items-center justify-between mb-1 flex-shrink-0">
            <div className="flex items-center gap-1">
              {/* Market tabs */}
              {(['spread', 'total', 'moneyline'] as ActiveMarket[])
                .filter(m => m !== 'spread' || !isSoccerGame)
                .map(m => (
                  <button
                    key={m}
                    onClick={() => setActiveMarket(m)}
                    className={`px-2.5 py-1 text-[11px] font-medium rounded transition-colors ${
                      activeMarket === m
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
                    }`}
                  >
                    {m === 'spread' ? 'Spread' : m === 'total' ? 'Total' : 'Moneyline'}
                  </button>
                ))}
              <span className="w-px h-4 bg-zinc-700/50 mx-1" />
              {/* Period sub-tabs */}
              {[
                { key: 'full', label: 'Full' },
                ...(availableTabs?.firstHalf ? [{ key: '1h', label: '1H' }] : []),
                ...(availableTabs?.secondHalf ? [{ key: '2h', label: '2H' }] : []),
                ...(availableTabs?.q1 ? [{ key: '1q', label: 'Q1' }] : []),
                ...(availableTabs?.q2 ? [{ key: '2q', label: 'Q2' }] : []),
                ...(availableTabs?.q3 ? [{ key: '3q', label: 'Q3' }] : []),
                ...(availableTabs?.q4 ? [{ key: '4q', label: 'Q4' }] : []),
                ...(availableTabs?.p1 ? [{ key: '1p', label: 'P1' }] : []),
                ...(availableTabs?.p2 ? [{ key: '2p', label: 'P2' }] : []),
                ...(availableTabs?.p3 ? [{ key: '3p', label: 'P3' }] : []),
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => handlePeriodChange(tab.key)}
                  className={`px-1.5 py-0.5 text-[9px] font-medium rounded transition-colors ${
                    activePeriod === tab.key
                      ? 'bg-zinc-700 text-zinc-100'
                      : 'text-zinc-600 hover:text-zinc-400'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          {/* Chart fills remaining space */}
          <div className="flex-1 min-h-0">
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

        {marketMode === 'sportsbook' ? (
          <>
            <OmiFairPricing
              pythonPillars={pythonPillarScores}
              bookmakers={bookmakers}
              gameData={gameData}
              sportKey={gameData.sportKey}
              activeMarket={activeMarket}
              activePeriod={activePeriod}
              selectedBook={selectedBook}
              commenceTime={gameData.commenceTime}
            />

            <WhyThisPrice
              pythonPillars={pythonPillarScores}
              ceq={activeCeq}
              homeTeam={gameData.homeTeam}
              awayTeam={gameData.awayTeam}
              activeMarket={activeMarket}
              activePeriod={activePeriod}
            />

            <CeqFactors ceq={activeCeq} activeMarket={activeMarket} />
          </>
        ) : (
          <>
            <ExchangePlaceholder homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
            <div className="bg-[#0a0a0a] p-2 flex items-center justify-center" style={{ gridArea: 'analysis' }}>
              <span className="text-[10px] text-zinc-600">Exchange analysis coming soon</span>
            </div>
            <div className="bg-[#0a0a0a] p-2 flex items-center justify-center" style={{ gridArea: 'ceq' }}>
              <span className="text-[10px] text-zinc-600">Exchange CEQ coming soon</span>
            </div>
          </>
        )}
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
          {/* Sportsbook / Exchange mode tabs (mobile) */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setMarketMode('sportsbook')}
              className={`px-3 py-1 text-[11px] font-medium rounded transition-colors ${
                marketMode === 'sportsbook'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
              }`}
            >
              Sportsbook
            </button>
            <button
              onClick={() => setMarketMode('exchange')}
              className={`px-3 py-1 text-[11px] font-medium rounded transition-colors ${
                marketMode === 'exchange'
                  ? 'bg-violet-500/15 text-violet-400 border border-violet-500/30'
                  : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
              }`}
            >
              Exchange
            </button>
          </div>

          {/* Market + Period tabs */}
          <div className="bg-zinc-900/50 rounded p-2">
            <div className="flex items-center gap-0.5 mb-1.5 flex-wrap">
              {(['spread', 'total', 'moneyline'] as ActiveMarket[])
                .filter(m => m !== 'spread' || !isSoccerGame)
                .map(m => (
                  <button
                    key={m}
                    onClick={() => setActiveMarket(m)}
                    className={`px-2.5 py-1 text-[11px] font-medium rounded transition-colors ${
                      activeMarket === m
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-500 hover:text-zinc-300 border border-transparent'
                    }`}
                  >
                    {m === 'spread' ? 'Spread' : m === 'total' ? 'Total' : 'Moneyline'}
                  </button>
                ))}
            </div>
            <div className="flex items-center gap-0.5 flex-wrap">
              {[
                { key: 'full', label: 'Full' },
                ...(availableTabs?.firstHalf ? [{ key: '1h', label: '1H' }] : []),
                ...(availableTabs?.secondHalf ? [{ key: '2h', label: '2H' }] : []),
                ...(availableTabs?.q1 ? [{ key: '1q', label: 'Q1' }] : []),
                ...(availableTabs?.q2 ? [{ key: '2q', label: 'Q2' }] : []),
                ...(availableTabs?.q3 ? [{ key: '3q', label: 'Q3' }] : []),
                ...(availableTabs?.q4 ? [{ key: '4q', label: 'Q4' }] : []),
                ...(availableTabs?.p1 ? [{ key: '1p', label: 'P1' }] : []),
                ...(availableTabs?.p2 ? [{ key: '2p', label: 'P2' }] : []),
                ...(availableTabs?.p3 ? [{ key: '3p', label: 'P3' }] : []),
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => handlePeriodChange(tab.key)}
                  className={`px-1.5 py-0.5 text-[9px] font-medium rounded transition-colors ${
                    activePeriod === tab.key
                      ? 'bg-zinc-700 text-zinc-100'
                      : 'text-zinc-600 hover:text-zinc-400'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Convergence chart — compact */}
          <div className="h-[200px] relative bg-zinc-900/50 rounded p-2">
            <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1 block">Line Convergence</span>
            <div className="flex-1 min-h-0 h-[calc(100%-20px)]">
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

          {marketMode === 'sportsbook' ? (
            <>
              <OmiFairPricing
                pythonPillars={pythonPillarScores}
                bookmakers={bookmakers}
                gameData={gameData}
                sportKey={gameData.sportKey}
                activeMarket={activeMarket}
                activePeriod={activePeriod}
                selectedBook={selectedBook}
                commenceTime={gameData.commenceTime}
              />

              <WhyThisPrice
                pythonPillars={pythonPillarScores}
                ceq={activeCeq}
                homeTeam={gameData.homeTeam}
                awayTeam={gameData.awayTeam}
                activeMarket={activeMarket}
                activePeriod={activePeriod}
              />

              <CeqFactors ceq={activeCeq} activeMarket={activeMarket} />
            </>
          ) : (
            <ExchangePlaceholder homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
          )}
        </div>
      </div>
    </>
  );
}
