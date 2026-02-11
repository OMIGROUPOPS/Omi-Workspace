'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores, PillarResult } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal, calculateFairMoneyline, calculateFairMLFromBook, calculateFairMLFromBook3Way, spreadToMoneyline, removeVig, removeVig3Way, SPORT_KEY_NUMBERS } from '@/lib/edge/engine/edgescout';

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

interface CompositeHistoryPoint {
  timestamp: string;
  fair_spread: number | null;
  fair_total: number | null;
  fair_ml_home: number | null;
  fair_ml_away: number | null;
  fair_ml_draw: number | null;
}

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
  activeMarket?: string;
}

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam, awayTeam, viewMode, onViewModeChange, commenceTime, sportKey, compact = false, omiFairLine, activeMarket: activeMarketProp }: LineMovementChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; timestamp: Date; index: number } | null>(null);
  const [trackingSide, setTrackingSide] = useState<'home' | 'away' | 'over' | 'under' | 'draw'>('home');
  const isSoccer = sportKey?.includes('soccer') ?? false;
  const [timeRange, setTimeRange] = useState<TimeRange>('ALL');
  const [compositeHistory, setCompositeHistory] = useState<CompositeHistoryPoint[]>([]);
  // Soccer 3-way: single-select (one line at a time, toggle switches)

  // Fetch composite history for dynamic OMI fair line
  useEffect(() => {
    if (!gameId) return;
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://omi-workspace-production.up.railway.app';
    fetch(`${BACKEND_URL}/api/composite-history/${gameId}`)
      .then(res => res.ok ? res.json() : [])
      .then((rows: CompositeHistoryPoint[]) => {
        const arr = Array.isArray(rows) ? rows : [];
        if (arr.length > 0) console.log(`[OMI Chart] composite_history: ${arr.length} pts for ${gameId}`, arr[0]);
        setCompositeHistory(arr);
      })
      .catch((err) => { console.warn('[OMI Chart] fetch failed:', err); setCompositeHistory([]); });
  }, [gameId]);

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

  // Helper: filter lineHistory by outcome name
  const filterByOutcome = (target: string) => {
    return (lineHistory || []).filter(snapshot => {
      const bookMatch = snapshot.book_key === selectedBook || snapshot.book === selectedBook;
      if (!bookMatch) return false;
      if (!snapshot.outcome_type) return false;
      const outcomeType = snapshot.outcome_type.toLowerCase();
      const tgt = target.toLowerCase();
      if (outcomeType === tgt) return true;
      // Match generic 'home'/'away' outcome_type (from line_snapshots) to team names
      if (outcomeType === 'home' && homeTeam && tgt === homeTeam.toLowerCase()) return true;
      if (outcomeType === 'away' && awayTeam && tgt === awayTeam.toLowerCase()) return true;
      if (outcomeType.includes(tgt) || tgt.includes(outcomeType)) return true;
      const outcomeLast = outcomeType.split(/\s+/).pop();
      const targetLast = tgt.split(/\s+/).pop();
      return outcomeLast === targetLast;
    });
  };

  // Helper: build data array from snapshots
  const buildDataArray = (snapshots: any[]) => {
    let arr = snapshots.map(s => ({
      timestamp: new Date(s.snapshot_time),
      value: marketType === 'moneyline' ? s.odds : s.line,
    })).filter(d => d.value !== null && d.value !== undefined);
    arr.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    if (timeRange !== 'ALL' && arr.length > 0) {
      const now = new Date();
      const hoursMap: Record<TimeRange, number> = { '30M': 0.5, '1H': 1, '3H': 3, '6H': 6, '24H': 24, 'ALL': 0 };
      const cutoffTime = new Date(now.getTime() - hoursMap[timeRange] * 60 * 60 * 1000);
      arr = arr.filter(d => d.timestamp >= cutoffTime);
    }
    return arr;
  };

  // Soccer 3-way ML: build separate data arrays for home/draw/away
  const isSoccer3Way = isSoccer && marketType === 'moneyline';
  const soccer3WayData = isSoccer3Way ? {
    home: buildDataArray(filterByOutcome(homeTeam || 'home')),
    draw: buildDataArray(filterByOutcome('Draw')),
    away: buildDataArray(filterByOutcome(awayTeam || 'away')),
  } : null;

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

  const hasRealData = filteredHistory.length > 0 || (soccer3WayData && (soccer3WayData.home.length > 0 || soccer3WayData.draw.length > 0 || soccer3WayData.away.length > 0));
  let data: { timestamp: Date; value: number }[] = [];

  if (isSoccer3Way && soccer3WayData) {
    // For soccer 3-way, primary data is the focused (trackingSide) line
    const sideData = trackingSide === 'draw' ? soccer3WayData.draw : trackingSide === 'away' ? soccer3WayData.away : soccer3WayData.home;
    data = sideData.length > 0 ? sideData : soccer3WayData.home;
  } else if (hasRealData) {
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

  const isFilteredEmpty = hasRealData && data.length === 0;

  // Color theming: emerald for line mode, amber for price mode
  const isPrice = effectiveViewMode === 'price';
  const lineColor = isPrice ? '#fbbf24' : '#34d399'; // amber-400 or emerald-400

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
  // Align OMI fair line basis with tracked side: fair line is always HOME spread,
  // so negate when tracking AWAY to match the book data (which also negates for away)
  let chartOmiFairLine = omiFairLine;
  if (marketType === 'spread' && trackingSide === 'away' && chartOmiFairLine !== undefined) {
    chartOmiFairLine = -chartOmiFairLine;
  }

  // Build dynamic OMI fair line data from composite_history
  const resolvedMarket = activeMarketProp || (selection.type === 'market' ? selection.market : 'spread');
  const omiFairLineData: { timestamp: Date; value: number }[] = compositeHistory
    .map(pt => {
      let val: number | null = null;
      if (resolvedMarket === 'spread') val = pt.fair_spread;
      else if (resolvedMarket === 'total') val = pt.fair_total;
      else if (resolvedMarket === 'moneyline') {
        if (trackingSide === 'draw') val = pt.fair_ml_draw;
        else if (trackingSide === 'away') val = pt.fair_ml_away;
        else val = pt.fair_ml_home;
      }
      if (val === null || val === undefined) return null;
      // Negate spread for away side tracking
      if (resolvedMarket === 'spread' && trackingSide === 'away') val = -val;
      return { timestamp: new Date(pt.timestamp), value: val };
    })
    .filter((d): d is { timestamp: Date; value: number } => d !== null);
  const hasOmiTimeSeries = omiFairLineData.length >= 1;

  const openValue = data[0]?.value || baseValue;
  const currentValue = data[data.length - 1]?.value || baseValue;
  const movement = currentValue - openValue;
  const values = data.map(d => d.value);
  if (chartOmiFairLine !== undefined) values.push(chartOmiFairLine);
  // Include all OMI fair line history points in Y-axis scaling
  for (const pt of omiFairLineData) values.push(pt.value);
  // For soccer 3-way single-select, only include tracked side in Y-axis bounds
  if (soccer3WayData) {
    const sideKey = trackingSide === 'draw' ? 'draw' : trackingSide === 'away' ? 'away' : 'home';
    const sideArr = soccer3WayData[sideKey as keyof typeof soccer3WayData];
    for (const pt of sideArr) values.push(pt.value);
  }
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  // Tight Y-axis padding: 5-10% of data range
  let padding: number;
  if (isMLChart) {
    padding = Math.max(range * 0.08, 5);
  } else if (marketType === 'spread' || marketType === 'total') {
    padding = 1.0;
  } else {
    padding = range * 0.1;
  }
  // Minimum visual range (small so chart stays tight to data)
  const minVisualRange = isMLChart ? 15 : 3;
  if (range + 2 * padding < minVisualRange) {
    padding = (minVisualRange - range) / 2;
  }

  const width = 600;
  const height = 300;
  const paddingLeft = 42;
  const paddingRight = 12;
  const paddingTop = 14;
  const paddingBottom = 28;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const chartPoints = data.map((d, i) => {
    const normalizedY = (d.value - minVal + padding) / (range + 2 * padding);
    const y = paddingTop + chartHeight - normalizedY * chartHeight;
    return { x: paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth, y, value: d.value, timestamp: d.timestamp, index: i };
  });

  // Step-line path: horizontal then vertical between each point (how sportsbook lines actually move)
  const pathD = chartPoints.map((p, i) => {
    if (i === 0) return `M ${p.x} ${p.y}`;
    return `H ${p.x} V ${p.y}`;
  }).join(' ');

  // Gradient fill path: step-line path + close to bottom of chart area
  const chartBottom = paddingTop + chartHeight;
  const gradientFillPath = chartPoints.length >= 2
    ? `${pathD} V ${chartBottom} H ${chartPoints[0].x} Z`
    : null;

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

  // Helper: convert a value to SVG Y coordinate
  const valueToY = (val: number) =>
    paddingTop + chartHeight - ((val - minVal + padding) / (range + 2 * padding)) * chartHeight;

  // OMI fair line: build SVG points aligned to the book line X-axis
  // When we have time-series data (>=2 pts), map onto the chart's time span.
  // Clamp X to chart bounds so points before/after book data still render.
  // When only 1 pt or no history, fall back to flat horizontal line.
  const omiChartPoints: { x: number; y: number; value: number }[] = (() => {
    if (hasOmiTimeSeries && omiFairLineData.length >= 2 && data.length >= 2) {
      const bookStartTime = data[0].timestamp.getTime();
      const bookEndTime = data[data.length - 1].timestamp.getTime();
      const bookTimeRange = bookEndTime - bookStartTime || 1;
      const mapped = omiFairLineData.map(pt => {
        const tFrac = (pt.timestamp.getTime() - bookStartTime) / bookTimeRange;
        // Clamp to chart bounds — OMI points outside book time range still plot at edges
        const x = Math.max(paddingLeft, Math.min(paddingLeft + chartWidth, paddingLeft + tFrac * chartWidth));
        return { x, y: valueToY(pt.value), value: pt.value };
      });
      // Extend to chart edges: prepend first value at left edge, append last value at right edge
      if (mapped.length >= 2) {
        const first = mapped[0];
        const last = mapped[mapped.length - 1];
        const extended: typeof mapped = [];
        if (first.x > paddingLeft + 1) {
          extended.push({ x: paddingLeft, y: first.y, value: first.value });
        }
        extended.push(...mapped);
        if (last.x < paddingLeft + chartWidth - 1) {
          extended.push({ x: paddingLeft + chartWidth, y: last.y, value: last.value });
        }
        return extended;
      }
    }
    // Fallback: single composite_history point or static omiFairLine → flat line
    const flatValue = omiFairLineData.length >= 1 ? omiFairLineData[omiFairLineData.length - 1].value : chartOmiFairLine;
    if (flatValue === undefined) return [];
    const y = valueToY(flatValue);
    return [
      { x: paddingLeft, y, value: flatValue },
      { x: paddingLeft + chartWidth, y, value: flatValue },
    ];
  })();

  const hasOmiLine = omiChartPoints.length >= 2;
  const omiPathD = hasOmiLine
    ? omiChartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
    : null;

  // OMI fair line Y position (for flat fallback and convergence label)
  const omiLineY = hasOmiLine ? omiChartPoints[omiChartPoints.length - 1].y : null;
  const currentOmiFairValue = hasOmiLine ? omiChartPoints[omiChartPoints.length - 1].value : chartOmiFairLine;


  // Y-axis labels
  const yLabels = (() => {
    const labels: { value: number; y: number }[] = [];
    const visualMin = minVal - padding;
    const visualMax = maxVal + padding;
    const visualRange = visualMax - visualMin;
    let labelStep: number;
    if (isMLChart) { labelStep = range <= 30 ? 10 : 25; }
    else if (marketType === 'spread' && effectiveViewMode === 'line') { labelStep = range <= 5 ? 0.5 : range <= 15 ? 1.0 : 2.0; }
    else if (marketType === 'total' && effectiveViewMode === 'line') { labelStep = range <= 5 ? 0.5 : range <= 15 ? 1.0 : 2.0; }
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
    <div>
      {/* Row 1: Chart title + time range + Line/Price toggle */}
      <div className="flex items-center justify-between px-2 mb-0.5">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-zinc-300">{chartTitle}</span>
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
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'OVR' : homeAbbr}
              </button>
              {isSoccer && marketType === 'moneyline' && (
                <button
                  onClick={() => setTrackingSide('draw')}
                  className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                    trackingSide === 'draw'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                  }`}
                >DRW</button>
              )}
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('under') : setTrackingSide('away')}
                className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                  (marketType === 'total' ? trackingSide === 'under' : trackingSide === 'away')
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'UND' : awayAbbr}
              </button>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>
          <span className="text-zinc-500">{formatValue(openValue)}</span>
          <span className="text-zinc-600">&rarr;</span>
          <span className="text-zinc-100 font-semibold">{formatValue(currentValue)}</span>
          <span className={`font-semibold ${movementColor}`}>{movement > 0 ? '+' : ''}{isMLChart ? Math.round(movement) : effectiveViewMode === 'price' ? Math.round(movement) : movement.toFixed(1)}</span>
        </div>
      </div>

      {/* Chart SVG — fixed height, step-line rendering */}
      <div className="relative" style={{ height: '200px' }}>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full cursor-crosshair" preserveAspectRatio="xMidYMid meet" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          <defs>
            <linearGradient id={`grad-${gameId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#34d399" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#34d399" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Y-axis gridlines + labels — horizontal dashed only */}
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#333333" strokeWidth="0.5" strokeDasharray="3 3" opacity="0.4" />
              <text x={paddingLeft - 5} y={label.y + 4} textAnchor="end" fill="#a1a1aa" fontSize="12" fontFamily="monospace">{formatValue(label.value)}</text>
            </g>
          ))}

          {/* X-axis date labels */}
          {xLabels.map((label, i) => (
            <text key={i} x={label.x} y={height - 4} textAnchor="middle" fill="#71717a" fontSize="11" fontFamily="monospace">{label.label}</text>
          ))}

          {/* Green gradient fill below step-line */}
          {gradientFillPath && (
            <path d={gradientFillPath} fill={`url(#grad-${gameId})`} />
          )}

          {/* OMI fair line — dashed cyan (dynamic or flat) */}
          {omiPathD && (
            <>
              <path d={omiPathD} fill="none" stroke="#22d3ee" strokeWidth="1" strokeDasharray="4 3" opacity="0.7" />
              {omiChartPoints.length > 0 && (
                <text x={omiChartPoints[omiChartPoints.length - 1].x - 2} y={omiChartPoints[omiChartPoints.length - 1].y - 4} textAnchor="end" fill="#22d3ee" fontSize="8" fontWeight="bold" fontFamily="monospace">OMI</text>
              )}
            </>
          )}

          {/* Book line — single step-line */}
          {chartPoints.length > 0 && (
            <>
              <path d={pathD} fill="none" stroke={lineColor} strokeWidth="2" />
              {/* Open dot — green */}
              <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="3" fill="#34d399" stroke="#18181b" strokeWidth="1" />
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
          <div className="absolute bg-zinc-800/95 border border-zinc-700/50 rounded px-2 py-0.5 text-[9px] pointer-events-none shadow-lg z-10 whitespace-nowrap" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 8}%`, transform: 'translate(-50%, -100%)' }}>
            <span className="font-semibold text-zinc-100 font-mono">{formatValue(hoveredPoint.value)}</span>
            <span className="text-zinc-500 mx-1">/</span>
            <span className="text-zinc-400">{hoveredPoint.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}, {hoveredPoint.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span>
          </div>
        )}
      </div>
      {/* Legend */}
      <div className="flex items-center justify-between px-2 py-0.5 text-[8px] text-zinc-500">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>Open</span>
          <span className="flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full" style={{ backgroundColor: lineColor }}></span>Current</span>
          {hasOmiLine && <span className="flex items-center gap-1"><span className="inline-block w-3 border-t border-dashed border-cyan-400"></span>OMI Fair</span>}
        </div>
        <span className="font-mono">{Math.abs(movement) > 0.05 ? `${Math.abs(isMLChart ? Math.round(movement) : Number(movement.toFixed(1)))} pts` : ''}</span>
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
  activeMarket, activePeriod, selectedBook, commenceTime, renderKey = 0,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  bookmakers: Record<string, any>;
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string };
  sportKey: string;
  activeMarket: ActiveMarket;
  activePeriod: string;
  selectedBook: string;
  commenceTime?: string;
  renderKey?: number;
}) {
  const periodKey = PERIOD_MAP[activePeriod] || 'fullGame';
  const isSoccerGame = sportKey?.includes('soccer') ?? false;

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
  // ML consensus: median of all book odds (needed before fair ML calc)
  const mlHomeOdds = allBooks.map(b => b.markets?.h2h?.home?.price).filter((v): v is number => v !== undefined);
  const mlAwayOdds = allBooks.map(b => b.markets?.h2h?.away?.price).filter((v): v is number => v !== undefined);
  const mlDrawOdds = allBooks.map(b => b.markets?.h2h?.draw?.price).filter((v): v is number => v !== undefined);
  const consensusHomeML = calcMedian(mlHomeOdds);
  const consensusAwayML = calcMedian(mlAwayOdds);
  const consensusDrawML = calcMedian(mlDrawOdds);

  // 3-way fair ML for soccer (home/draw/away)
  const omiFairML3Way = (isSoccerGame && pythonPillars && consensusHomeML !== undefined && consensusDrawML !== undefined && consensusAwayML !== undefined)
    ? calculateFairMLFromBook3Way(consensusHomeML, consensusDrawML, consensusAwayML, pythonPillars.composite)
    : null;

  // ML derived from fair spread for cross-market consistency; fallback to book-anchored adjustment
  const omiFairML = omiFairML3Way
    ? { homeOdds: omiFairML3Way.homeOdds, awayOdds: omiFairML3Way.awayOdds }
    : (omiFairSpread
      ? spreadToMoneyline(omiFairSpread.fairLine, sportKey)
      : (pythonPillars && consensusHomeML !== undefined && consensusAwayML !== undefined
        ? calculateFairMLFromBook(consensusHomeML, consensusAwayML, pythonPillars.composite)
        : (pythonPillars ? calculateFairMoneyline(pythonPillars.composite) : null)));

  // OMI fair ML implied probabilities (no-vig)
  const effectiveHomeML = omiFairML ? omiFairML.homeOdds : (consensusHomeML ?? undefined);
  const effectiveAwayML = omiFairML ? omiFairML.awayOdds : (consensusAwayML ?? undefined);
  const effectiveDrawML = omiFairML3Way ? omiFairML3Way.drawOdds : (consensusDrawML ?? undefined);
  const omiFairHomeProb = effectiveHomeML !== undefined ? americanToImplied(effectiveHomeML) : undefined;
  const omiFairAwayProb = effectiveAwayML !== undefined ? americanToImplied(effectiveAwayML) : undefined;
  const omiFairDrawProb = effectiveDrawML !== undefined ? americanToImplied(effectiveDrawML) : undefined;

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

  // Market-specific confidence: use pillarsByMarket composite when available
  const marketKeyForPillars = activeMarket === 'total' ? 'totals' : activeMarket;
  const pillarPeriodKey = activePeriod === 'full' ? 'full' : (activePeriod === '1h' ? 'h1' : activePeriod === '2h' ? 'h2' : activePeriod?.replace(/(\d)([a-z])/, '$2$1') || 'full');
  const pbm = pythonPillars?.pillarsByMarket;
  const marketPillarData = pbm ? (pbm as any)[marketKeyForPillars]?.[pillarPeriodKey] : undefined;
  const composite = marketPillarData?.composite ?? pythonPillars?.composite ?? 50;

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

  const sideBlocks: SideBlock[] = (() => {
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
        const abs = Math.abs(signedGap);
        if (abs < 0.3) return `${selBookName} is at fair value on ${side}`;
        if (abs < 1.0) return `${selBookName} is close to fair value — only ${abs.toFixed(1)} pts from OMI line`;
        return signedGap > 0
          ? `${selBookName} offers ${abs.toFixed(1)} pts more than fair value on ${side}`
          : `${selBookName} prices ${side} ${abs.toFixed(1)} pts tighter than fair`;
      };

      const mkEvLine = (signedGap: number, cross: number | null) => {
        if (Math.abs(signedGap) < 0.3) return '';
        const sign = signedGap > 0 ? '+' : '\u2212';
        if (signedGap <= 0) return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)} pts`;
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
      // Fallback: if selected book doesn't have totals, use first book that does
      const hasTotals = (b: typeof selBook) => b?.markets?.totals?.line !== undefined && b?.markets?.totals?.line !== null;
      let effBook = selBook;
      let effBookName = selBookName;
      if (!hasTotals(selBook)) {
        const fallback = allBooks.find(b => hasTotals(b));
        if (fallback) { effBook = fallback; effBookName = BOOK_CONFIG[fallback.key]?.name || fallback.key; }
      }

      const bookLine = effBook?.markets?.totals?.line;
      const overPrice = effBook?.markets?.totals?.over?.price;
      const underPrice = effBook?.markets?.totals?.under?.price;
      const fairLine = omiFairTotal?.fairLine;

      // Directional: if fair > book, Over has positive edge, Under has negative
      const overSignedGap = bookLine !== undefined && fairLine !== undefined
        ? Math.round((fairLine - bookLine) * 10) / 10 : 0;
      const underSignedGap = -overSignedGap;

      // Confidence for totals: use market-specific composite (falls back to gameEnvironment)
      const totalsConf = composite; // already resolved via pillarsByMarket for totals
      const overConf = totalsConf;
      const underConf = 100 - totalsConf;

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
        const abs = Math.abs(signedGap);
        if (abs < 0.3) return `${effBookName} is at fair value on ${side}`;
        if (abs < 1.0) return `${effBookName} is close to fair value — only ${abs.toFixed(1)} pts from OMI line`;
        return signedGap > 0
          ? `${effBookName} offers ${abs.toFixed(1)} pts more than fair value on ${side}`
          : `${effBookName} prices ${side} ${abs.toFixed(1)} pts tighter than fair`;
      };

      const mkTotalEv = (signedGap: number, ev: number) => {
        if (Math.abs(signedGap) < 0.3) return '';
        const sign = signedGap > 0 ? '+' : '\u2212';
        if (signedGap <= 0) return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)} pts`;
        return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)} pts${ev > 0 ? ` | EV: +$${ev}/1K` : ''}`;
      };

      return [
        {
          label: 'OVER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: overPrice !== undefined ? formatOdds(overPrice) : '--',
          edgePct: 0, edgePts: overSignedGap, edgeColor: getEdgeColor(overSignedGap, 'total'),
          contextLine: mkTotalContext('Over', overSignedGap),
          evLine: mkTotalEv(overSignedGap, overEv),
          bookName: effBookName, hasData: bookLine !== undefined,
          confidence: overConf, confColor: getConfColor(overConf),
        },
        {
          label: 'UNDER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: underPrice !== undefined ? formatOdds(underPrice) : '--',
          edgePct: 0, edgePts: underSignedGap, edgeColor: getEdgeColor(underSignedGap, 'total'),
          contextLine: mkTotalContext('Under', underSignedGap),
          evLine: mkTotalEv(underSignedGap, underEv),
          bookName: effBookName, hasData: bookLine !== undefined,
          confidence: underConf, confColor: getConfColor(underConf),
        },
      ];
    }
    // Moneyline — fallback: if selected book doesn't have h2h, use first book that does
    const hasH2h = (b: typeof selBook) => b?.markets?.h2h?.home?.price !== undefined && b?.markets?.h2h?.home?.price !== null;
    let mlEffBook = selBook;
    let mlEffBookName = selBookName;
    if (!hasH2h(selBook)) {
      const fallback = allBooks.find(b => hasH2h(b));
      if (fallback) { mlEffBook = fallback; mlEffBookName = BOOK_CONFIG[fallback.key]?.name || fallback.key; }
    }
    const bookHomeOdds = mlEffBook?.markets?.h2h?.home?.price;
    const bookAwayOdds = mlEffBook?.markets?.h2h?.away?.price;
    const bookDrawOdds = mlEffBook?.markets?.h2h?.draw?.price;
    let vigPct = '--';
    let homeSignedGap = 0;
    let awaySignedGap = 0;
    let drawSignedGap = 0;
    let bookHomeProb: number | undefined;
    let bookAwayProb: number | undefined;
    let bookDrawProb: number | undefined;

    // 3-way vig removal for soccer, 2-way for everything else
    if (isSoccerGame && bookHomeOdds !== undefined && bookDrawOdds !== undefined && bookAwayOdds !== undefined) {
      const stripped = removeVig3Way(bookHomeOdds, bookDrawOdds, bookAwayOdds);
      vigPct = `${(stripped.vig * 100).toFixed(1)}%`;
      bookHomeProb = stripped.fairHomeProb;
      bookAwayProb = stripped.fairAwayProb;
      bookDrawProb = stripped.fairDrawProb;
      if (omiFairHomeProb !== undefined) homeSignedGap = Math.round((omiFairHomeProb - stripped.fairHomeProb) * 1000) / 10;
      if (omiFairAwayProb !== undefined) awaySignedGap = Math.round((omiFairAwayProb - stripped.fairAwayProb) * 1000) / 10;
      if (omiFairDrawProb !== undefined) drawSignedGap = Math.round((omiFairDrawProb - stripped.fairDrawProb) * 1000) / 10;
    } else if (bookHomeOdds !== undefined && bookAwayOdds !== undefined) {
      const stripped = removeVig(bookHomeOdds, bookAwayOdds);
      vigPct = `${(stripped.vig * 100).toFixed(1)}%`;
      bookHomeProb = stripped.fairHomeProb;
      bookAwayProb = stripped.fairAwayProb;
      if (omiFairHomeProb !== undefined) homeSignedGap = Math.round((omiFairHomeProb - stripped.fairHomeProb) * 1000) / 10;
      if (omiFairAwayProb !== undefined) awaySignedGap = Math.round((omiFairAwayProb - stripped.fairAwayProb) * 1000) / 10;
    }

    const homeEv = omiFairHomeProb !== undefined && bookHomeOdds !== undefined ? calcEV(omiFairHomeProb, bookHomeOdds) : 0;
    const awayEv = omiFairAwayProb !== undefined && bookAwayOdds !== undefined ? calcEV(omiFairAwayProb, bookAwayOdds) : 0;
    const drawEv = omiFairDrawProb !== undefined && bookDrawOdds !== undefined ? calcEV(omiFairDrawProb, bookDrawOdds) : 0;

    const homeConf = omiFairHomeProb !== undefined ? Math.round(omiFairHomeProb * 100) : composite;
    const awayConf = omiFairAwayProb !== undefined ? Math.round(omiFairAwayProb * 100) : (100 - composite);
    const drawConf = omiFairDrawProb !== undefined ? Math.round(omiFairDrawProb * 100) : 25;
    const homeAbbr = abbrev(gameData.homeTeam);
    const awayAbbr = abbrev(gameData.awayTeam);

    const mkMLContext = (side: string, bookProb: number | undefined, fairProb: number | undefined, signedGap: number) => {
      if (bookProb === undefined || fairProb === undefined) return '';
      const abs = Math.abs(signedGap);
      if (abs < 2) return `${mlEffBookName} is at fair value on ${side} ML`;
      if (abs < 5) return `${mlEffBookName} is close to fair value — only ${abs.toFixed(1)}% from OMI`;
      return signedGap > 0
        ? `${mlEffBookName} offers ${abs.toFixed(1)}% more than fair value on ${side} ML`
        : `${mlEffBookName} prices ${side} ML ${abs.toFixed(1)}% tighter than fair`;
    };

    const mkMLEvLine = (signedGap: number, ev: number) => {
      if (Math.abs(signedGap) < 2) return '';
      const sign = signedGap > 0 ? '+' : '\u2212';
      if (signedGap <= 0) return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)}%`;
      return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)}%${ev > 0 ? ` | EV: +$${ev}/1K` : ''}`;
    };

    const blocks: SideBlock[] = [
      {
        label: awayAbbr, fair: effectiveAwayML !== undefined ? formatOdds(effectiveAwayML) : 'N/A',
        bookLine: bookAwayOdds !== undefined ? formatOdds(bookAwayOdds) : '--', bookOdds: vigPct,
        edgePct: awaySignedGap, edgePts: 0, edgeColor: getEdgeColor(awaySignedGap, 'moneyline'),
        contextLine: mkMLContext(awayAbbr, bookAwayProb, omiFairAwayProb, awaySignedGap),
        evLine: mkMLEvLine(awaySignedGap, awayEv),
        bookName: mlEffBookName, hasData: bookAwayOdds !== undefined, vigPct,
        rawBookOdds: bookAwayOdds, rawFairProb: omiFairAwayProb, rawBookProb: bookAwayProb,
        confidence: awayConf, confColor: getConfColor(awayConf),
      },
    ];

    // Insert draw block for soccer 3-way
    if (isSoccerGame && bookDrawOdds !== undefined) {
      blocks.push({
        label: 'DRW', fair: effectiveDrawML !== undefined ? formatOdds(effectiveDrawML) : 'N/A',
        bookLine: formatOdds(bookDrawOdds), bookOdds: vigPct,
        edgePct: drawSignedGap, edgePts: 0, edgeColor: getEdgeColor(drawSignedGap, 'moneyline'),
        contextLine: mkMLContext('Draw', bookDrawProb, omiFairDrawProb, drawSignedGap),
        evLine: mkMLEvLine(drawSignedGap, drawEv),
        bookName: mlEffBookName, hasData: true, vigPct,
        rawBookOdds: bookDrawOdds, rawFairProb: omiFairDrawProb, rawBookProb: bookDrawProb,
        confidence: drawConf, confColor: getConfColor(drawConf),
      });
    }

    blocks.push({
      label: homeAbbr, fair: effectiveHomeML !== undefined ? formatOdds(effectiveHomeML) : 'N/A',
      bookLine: bookHomeOdds !== undefined ? formatOdds(bookHomeOdds) : '--', bookOdds: vigPct,
      edgePct: homeSignedGap, edgePts: 0, edgeColor: getEdgeColor(homeSignedGap, 'moneyline'),
      contextLine: mkMLContext(homeAbbr, bookHomeProb, omiFairHomeProb, homeSignedGap),
      evLine: mkMLEvLine(homeSignedGap, homeEv),
      bookName: mlEffBookName, hasData: bookHomeOdds !== undefined, vigPct,
      rawBookOdds: bookHomeOdds, rawFairProb: omiFairHomeProb, rawBookProb: bookHomeProb,
      confidence: homeConf, confColor: getConfColor(homeConf),
    });

    return blocks;
  })();

  // All books quick-scan with signed edge (positive = value)
  const allBooksQuickScan = allBooks.filter(b => b.key !== 'pinnacle').map(b => {
    let line = '--';
    let signedEdge = 0;
    let edgeUnit = 'pt';
    if (activeMarket === 'spread') {
      const bookLine = b.markets?.spreads?.home?.line;
      line = bookLine !== undefined ? formatSpread(bookLine) : '--';
      if (bookLine !== undefined && omiFairSpread) {
        // Positive = book gives more than fair (value on home)
        signedEdge = Math.round((bookLine - omiFairSpread.fairLine) * 10) / 10;
      }
    } else if (activeMarket === 'total') {
      const totalLine = b.markets?.totals?.line;
      line = totalLine !== undefined ? `${totalLine}` : '--';
      if (totalLine !== undefined && omiFairTotal) {
        signedEdge = Math.round((omiFairTotal.fairLine - totalLine) * 10) / 10;
      }
    } else {
      const homeOdds = b.markets?.h2h?.home?.price;
      line = homeOdds !== undefined ? formatOdds(homeOdds) : '--';
      edgeUnit = '%';
      if (homeOdds !== undefined && omiFairHomeProb !== undefined) {
        const bookProb = americanToImplied(homeOdds);
        signedEdge = Math.round((omiFairHomeProb - bookProb) * 1000) / 10;
      }
    }
    const absEdge = Math.abs(signedEdge);
    const edgeStr = absEdge > 0.1 ? `(${signedEdge > 0 ? '+' : ''}${signedEdge.toFixed(1)}${edgeUnit})` : '';
    return { key: b.key, name: BOOK_CONFIG[b.key]?.name || b.key, line, edgeStr, signedEdge, absEdge, color: b.color, isSelected: b.key === selectedBook };
  });
  // Find best-value book
  const bestValueBook = allBooksQuickScan.reduce((best, b) => b.signedEdge > best.signedEdge ? b : best, allBooksQuickScan[0]);

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
    <div className="bg-[#0a0a0a] px-3 py-2 flex flex-col" style={{ overflow: 'visible' }}>
      {/* OMI Fair Line — split display for both sides */}
      <div className="mb-1.5 flex-shrink-0">
        <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-0.5">OMI Fair Line</div>
        <div className="flex items-baseline gap-4" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {sideBlocks.map((block, i) => (
            <div key={i} className="flex items-baseline">
              {i > 0 && <span className="text-zinc-600 text-[12px] mr-4">vs</span>}
              <span className="text-[10px] text-zinc-500 mr-1">{block.label}</span>
              <span className="text-[20px] font-bold font-mono text-cyan-400">{block.fair}</span>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-zinc-500 mt-0.5">
          {hasPillars
            ? `Based on 6-pillar composite (${pythonPillars!.composite}) and market analysis`
            : `Based on market consensus (${allBooks.length} books)`}
        </div>
        {pillarsAgoText && <div className="text-[10px] text-zinc-600">{pillarsAgoText}</div>}
        {lineMovementNotice && (
          <div className="text-[10px] text-amber-400 mt-0.5">{lineMovementNotice}</div>
        )}
        {(() => {
          const homeAbbr = abbrev(gameData.homeTeam);
          const awayAbbr = abbrev(gameData.awayTeam);
          let narrative: string;
          if (activeMarket === 'total') {
            if (hasPillars) {
              const totalConf = composite; // market-specific composite (same source as block CONF)
              const lean = totalConf > 52 ? 'Over' : totalConf < 48 ? 'Under' : 'neutral';
              if (lean === 'neutral') {
                narrative = `No strong Over/Under lean (${totalConf}% conf). Fair total at ${omiFairTotal?.fairLine ?? 'N/A'}.`;
              } else {
                const overEdge = sideBlocks[0].edgePts;
                const absOverEdge = Math.abs(overEdge);
                if (absOverEdge < 1.0) {
                  narrative = `Model leans ${lean} (${totalConf}% conf). ${selBookName} total is near fair value (${absOverEdge.toFixed(1)} pts from OMI).`;
                } else {
                  const evStr = sideBlocks[0].evLine.includes('EV') ? sideBlocks[0].evLine.split('|').pop()?.trim() || '' : '';
                  narrative = `Model leans ${lean} (${totalConf}% conf). ${selBookName}: ${overEdge > 0 ? '+' : ''}${overEdge.toFixed(1)} pts edge${evStr ? `, ${evStr}` : ''}.`;
                }
              }
            } else {
              narrative = `Consensus total: ${consensusTotal ?? 'N/A'}. Comparing ${selBookName} against market median.`;
            }
          } else if (activeMarket === 'moneyline' && omiFairHomeProb !== undefined) {
            // ML narrative uses spread-derived implied probability for consistency with fair ML odds
            const homeImplied = Math.round(omiFairHomeProb * 100);
            const awayImplied = 100 - homeImplied;
            const favored = homeImplied >= awayImplied ? homeAbbr : awayAbbr;
            const favoredPct = Math.max(homeImplied, awayImplied);
            const strength = favoredPct >= 70 ? 'strongly ' : favoredPct >= 60 ? '' : 'slightly ';
            const favoredBlock = homeImplied >= awayImplied ? sideBlocks[sideBlocks.length - 1] : sideBlocks[0];
            const edgeVal = favoredBlock.edgePct;
            const absEdge = Math.abs(edgeVal);
            if (absEdge < 5) {
              narrative = `Model ${strength}favors ${favored} (${favoredPct}% implied). ${selBookName} is near fair value.`;
            } else {
              const evStr = favoredBlock.evLine.includes('EV') ? favoredBlock.evLine.split('|').pop()?.trim() || '' : '';
              narrative = `Model ${strength}favors ${favored} (${favoredPct}% implied). ${selBookName}: ${edgeVal > 0 ? '+' : ''}${edgeVal.toFixed(1)}% edge${evStr ? `, ${evStr}` : ''}.`;
            }
          } else if (hasPillars) {
            const comp = pythonPillars!.composite;
            if (comp >= 48 && comp <= 52) {
              narrative = `Near pick'em — ${homeAbbr}/${awayAbbr} (${comp}% conf). Look for line value vs consensus.`;
            } else {
              const favored = comp > 50 ? homeAbbr : awayAbbr;
              const favoredBlock = comp > 50 ? sideBlocks[sideBlocks.length - 1] : sideBlocks[0]; // last=home, first=away
              const edgeVal = favoredBlock.edgePts;
              const absEdge = Math.abs(edgeVal);
              if (absEdge < 1.0) {
                narrative = `Model favors ${favored} (${comp}% conf). ${selBookName} line is near fair value (${absEdge.toFixed(1)} pts from OMI).`;
              } else {
                const evStr = favoredBlock.evLine.includes('EV') ? favoredBlock.evLine.split('|').pop()?.trim() || '' : '';
                narrative = `Model favors ${favored} (${comp}% conf). ${selBookName}: ${edgeVal > 0 ? '+' : ''}${edgeVal.toFixed(1)} pts edge${evStr ? `, ${evStr}` : ''}.`;
              }
            }
          } else {
            narrative = `Comparing ${selBookName} against market consensus of ${allBooks.length} sportsbooks.`;
          }
          return <div className="text-[11px] text-zinc-200 mt-1 leading-snug">{narrative}</div>;
        })()}
      </div>

      {/* Single-book comparison — two side-by-side blocks with edge story */}
      <div key={`blocks-${renderKey}-${activeMarket}-${activePeriod}-${selectedBook}`} className={`grid grid-cols-1 gap-1.5 mb-1 ${sideBlocks.length === 3 ? 'lg:grid-cols-3' : 'lg:grid-cols-2'}`} style={{ fontVariantNumeric: 'tabular-nums', visibility: 'visible' as const, opacity: 1 }}>
        {sideBlocks.map((block, blockIdx) => {
          const edgeVal = activeMarket === 'moneyline' ? block.edgePct : block.edgePts;
          const absEdge = Math.abs(edgeVal);
          const isPositiveEdge = edgeVal > 0;
          const isHighEdge = activeMarket === 'moneyline' ? (isPositiveEdge && absEdge >= 10) : (isPositiveEdge && absEdge >= 1.0);
          const isNearZero = activeMarket === 'moneyline' ? absEdge < 2 : absEdge < 0.3;

          // Format edge display
          const edgeDisplay = (() => {
            if (!block.hasData) return '--';
            if (isNearZero) return 'None';
            const sign = isPositiveEdge ? '+' : '\u2212';
            return `${sign}${absEdge.toFixed(1)}${activeMarket === 'moneyline' ? '%' : ''}`;
          })();

          return (
            <div key={blockIdx} className={`rounded overflow-hidden border border-zinc-800 ${isHighEdge ? 'border-l-2 border-l-emerald-400' : ''}`}>
              {/* Block header — team/side label */}
              <div className="bg-zinc-900 px-2 py-1 border-b border-zinc-800">
                <span className="text-[11px] font-bold text-zinc-100">{block.label}</span>
              </div>
              {/* Comparison: OMI Fair vs Book vs Edge vs Confidence */}
              <div className="px-2 py-1.5">
                <div className="flex items-end justify-between gap-1.5">
                  <div>
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest">{hasPillars ? 'OMI Fair' : 'Consensus'}</div>
                    <div className="text-[18px] font-bold font-mono text-cyan-400">{block.fair}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest">{block.bookName}</div>
                    <div className="text-[18px] font-bold font-mono text-zinc-100">{block.bookLine}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-zinc-500 uppercase tracking-widest">Edge</div>
                    <div className={`text-[18px] font-bold font-mono ${block.edgeColor}`}>
                      {edgeDisplay}
                    </div>
                  </div>
                  {hasPillars && (
                    <div className="text-right">
                      <div className="text-[8px] text-zinc-500 uppercase tracking-widest">Conf</div>
                      <div className={`text-[18px] font-bold font-mono ${block.confColor}`}>
                        {block.confidence}%
                      </div>
                    </div>
                  )}
                </div>
                {block.contextLine && (
                  <div className="mt-1 pt-1 border-t border-zinc-800/50">
                    <div className="text-[10px] text-zinc-400">{block.contextLine}</div>
                    {block.evLine && <div className={`text-[10px] font-medium ${block.edgeColor}`}>{block.evLine}</div>}
                  </div>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[9px] text-zinc-500 font-mono">
                    {activeMarket === 'moneyline' ? `Juice: ${block.bookOdds}` : `Odds: ${block.bookOdds}`}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* All Books quick-scan row — with edge direction and best value */}
      {allBooksQuickScan.length > 1 && (
        <div className="flex-shrink-0 border-t border-zinc-800/50 pt-1 pb-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[8px] text-zinc-600 uppercase tracking-widest">All Books</span>
            {bestValueBook && bestValueBook.signedEdge > (activeMarket === 'moneyline' ? 3 : 0.5) && (
              <span className="text-[10px] font-mono text-emerald-400 font-semibold">
                Best value: {bestValueBook.name} {bestValueBook.line} {bestValueBook.edgeStr}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {allBooksQuickScan.map(b => {
              const isBest = b.key === bestValueBook?.key && b.signedEdge > (activeMarket === 'moneyline' ? 3 : 0.5);
              const edgeColor = isBest ? 'text-emerald-400 font-semibold' : b.absEdge < (activeMarket === 'moneyline' ? 3 : 0.5) ? 'text-zinc-500' : b.signedEdge > 0 ? 'text-emerald-400/70' : 'text-zinc-500';
              return (
                <span key={b.key} className={`text-[10px] font-mono ${b.isSelected ? 'text-cyan-400 font-semibold' : 'text-zinc-400'}`}>
                  <span className="inline-block w-1.5 h-1.5 rounded-sm mr-0.5" style={{ backgroundColor: b.color }} />
                  {b.name}: {b.line} {b.edgeStr && <span className={edgeColor}>{b.edgeStr}</span>}
                </span>
              );
            })}
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
              {/* Center line — dashed for visibility at neutral */}
              <div className="absolute left-1/2 top-0 w-0 h-full z-10" style={{ borderLeft: '1px dashed #71717a' }} />
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
        'PASS': 'Below edge threshold — check book pricing for gaps',
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
    const fallbackDesc = best.ceq >= 50
      ? 'Near neutral — book-specific pricing gaps may offer value'
      : best.ceq >= 40
        ? 'Weak signal — check pricing for book-specific edge'
        : 'No strong edge detected';
    return {
      ceq: best.ceq, confidence: best.confidence,
      text: `CEQ: ${best.ceq}% ${best.confidence} — ${fallbackDesc}`,
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
    <div className="bg-[#0a0a0a] px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1">Why This Price</span>
      <div>
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

function CeqFactors({ ceq, activeMarket, homeTeam, awayTeam }: { ceq: GameCEQ | null | undefined; activeMarket?: ActiveMarket; homeTeam?: string; awayTeam?: string }) {
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
      <div className="bg-[#0a0a0a] px-2 py-1.5 flex items-center justify-center">
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

  const homeAbbr = homeTeam ? abbrev(homeTeam) : 'HOME';
  const awayAbbr = awayTeam ? abbrev(awayTeam) : 'AWAY';
  const favAbbr = (pythonPillars: any) => homeAbbr; // composite >50 = home-favored by convention
  const unfavAbbr = awayAbbr;

  // Detail text generators per factor
  const getDetailText = (key: string, score: number): string => {
    const fav = homeAbbr;
    const unfav = awayAbbr;
    switch (key) {
      case 'marketEfficiency':
        return score > 60 ? 'Market is efficient — books are well-calibrated on this line'
          : score < 40 ? 'Market appears inefficient — significant pricing gaps between books'
          : 'Mixed signals — some market inefficiency detected';
      case 'lineupImpact':
        return score > 60 ? `Lineup advantage confirmed — key player availability favors ${fav}`
          : score < 40 ? `Lineup disadvantage — missing key players weakens ${fav}`
          : 'Lineup impact is neutral — no major availability edge';
      case 'gameEnvironment':
        return score > 60 ? 'Environment favors higher scoring — pace/conditions lean Over'
          : score < 40 ? 'Environment favors lower scoring — pace/conditions lean Under'
          : 'Neutral environment — no strong pace or conditions lean';
      case 'matchupDynamics':
        return score > 60 ? `Matchup favors ${fav} — stylistic advantage`
          : score < 40 ? `Matchup favors ${unfav} — stylistic disadvantage`
          : 'Even matchup — no clear stylistic edge';
      case 'sentiment':
        return score > 60 ? 'Public/sharp sentiment aligns with model — market agrees'
          : score < 40 ? 'Contrarian signal — model disagrees with market sentiment'
          : 'Mixed sentiment — public and sharp money diverge';
      default: return '';
    }
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

  // Compute scores for composite summary
  const scoredFactors = factors.map(f => {
    const rawScore = ceqPillars[f.key].score;
    const score = adjustScore(rawScore, f.key);
    return { ...f, score, rawScore };
  });
  const compositeAvg = Math.round(scoredFactors.reduce((sum, f) => sum + f.score * f.weight, 0) / scoredFactors.reduce((sum, f) => sum + f.weight, 0));
  const strongest = [...scoredFactors].sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50))[0];

  return (
    <div className="bg-[#0a0a0a] px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1">CEQ Factors{activeMarket ? ` — ${activeMarket === 'moneyline' ? 'ML' : activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)}` : ''}</span>
      <div>
        <div className="flex flex-col gap-0.5">
          {scoredFactors.map(f => {
            const wPct = Math.round(f.weight * 100);
            return (
              <div key={f.key}>
                <div className="flex items-center gap-1">
                  <span className="text-[9px] text-zinc-500 font-mono w-16 truncate">{f.label} ({wPct}%)</span>
                  <div className="flex-1 h-[5px] bg-zinc-800 rounded-sm overflow-hidden">
                    <div className="h-full rounded-sm" style={{ width: `${f.score}%`, backgroundColor: getBarColor(f.score) }} />
                  </div>
                  <span className={`text-[9px] font-mono w-5 text-right ${getTextColor(f.score)}`}>{f.score}</span>
                  <span className={`text-[8px] w-12 text-right ${getTextColor(f.score)}`}>{getStrength(f.score)}</span>
                </div>
                <div className="text-[9px] text-zinc-500 ml-[68px] leading-tight">{getDetailText(f.key, f.score)}</div>
              </div>
            );
          })}
        </div>
        {/* Composite summary */}
        <div className="mt-1 pt-1 border-t border-zinc-800/50">
          <div className="text-[9px] text-zinc-400">
            <span className="font-semibold text-zinc-300">CEQ COMPOSITE: {compositeAvg}%</span>
            {' — '}
            {compositeAvg >= 65 ? 'Market strongly validates thesis.'
              : compositeAvg >= 55 ? 'Market partially validates thesis.'
              : compositeAvg >= 45 ? 'Mixed market validation.'
              : 'Market does not validate thesis.'}
            {strongest && ` ${strongest.label} (${strongest.score}) is the ${strongest.score > 50 ? 'strongest validation' : 'weakest'} signal.`}
          </div>
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
// AskEdgeAI — placeholder chatbot panel (right column)
// ============================================================================

function AskEdgeAI({ activeMarket, activePeriod }: { activeMarket: string; activePeriod: string }) {
  const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q' };
  const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'Moneyline' };
  const viewingLabel = `${periodLabels[activePeriod] || 'Full Game'} ${marketLabels[activeMarket] || activeMarket}`;

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a] border-l border-zinc-800">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-800/50">
        <div className="flex items-center gap-1.5">
          <span className="text-[13px]">&#10022;</span>
          <span className="text-[12px] font-semibold text-zinc-200">Ask Edge AI</span>
        </div>
        <span className="text-[9px] text-zinc-500">Viewing: {viewingLabel}</span>
      </div>
      {/* Body */}
      <div className="flex-1 px-3 py-3 overflow-y-auto">
        <p className="text-[11px] text-zinc-400 mb-2">I can help you analyze:</p>
        <ul className="text-[11px] text-zinc-500 space-y-1.5 mb-3">
          <li className="flex items-start gap-1.5"><span className="text-zinc-600 mt-0.5">&#8226;</span>Line movement and why lines move</li>
          <li className="flex items-start gap-1.5"><span className="text-zinc-600 mt-0.5">&#8226;</span>Edge calculations and what they mean</li>
          <li className="flex items-start gap-1.5"><span className="text-zinc-600 mt-0.5">&#8226;</span>Sharp vs public money indicators</li>
          <li className="flex items-start gap-1.5"><span className="text-zinc-600 mt-0.5">&#8226;</span>How to interpret our pillar scores</li>
        </ul>
        <p className="text-[11px] text-zinc-400">What would you like to know more about?</p>
      </div>
      {/* Input */}
      <div className="px-3 pb-3 pt-1">
        <div className="flex gap-1.5">
          <input
            type="text"
            placeholder={`Ask about ${viewingLabel}...`}
            className="flex-1 bg-zinc-900 border border-zinc-700/50 rounded px-2.5 py-1.5 text-[11px] text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
            disabled
          />
          <button className="px-3 py-1.5 bg-zinc-800 border border-zinc-700/50 rounded text-[11px] text-zinc-400 hover:text-zinc-200 transition-colors" disabled>
            Ask
          </button>
        </div>
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


  // Force re-render when market/period changes to fix blank blocks
  const [renderKey, setRenderKey] = useState(0);
  useEffect(() => {
    setRenderKey(prev => prev + 1);
  }, [activeMarket, activePeriod]);

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

  // Append current book odds from cached_odds as the latest chart data point
  // This ensures the chart always ends at the actual current book price, not stale snapshots
  const getLineHistoryWithCurrentOdds = () => {
    const base = getLineHistory();
    const periodMapped = PERIOD_MAP[activePeriod] || 'fullGame';
    const markets = bookmakers[selectedBook]?.marketGroups?.[periodMapped];
    if (!markets) return base;

    const now = new Date().toISOString();
    const syntheticPoints: any[] = [];

    if (activeMarket === 'moneyline' && markets.h2h) {
      if (markets.h2h.home?.price !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: gameData.homeTeam, odds: markets.h2h.home.price, line: 0 });
      }
      if (markets.h2h.away?.price !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: gameData.awayTeam, odds: markets.h2h.away.price, line: 0 });
      }
      if (markets.h2h.draw?.price !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: 'Draw', odds: markets.h2h.draw.price, line: 0 });
      }
    } else if (activeMarket === 'spread' && markets.spreads) {
      if (markets.spreads.home?.line !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: gameData.homeTeam, line: markets.spreads.home.line, odds: markets.spreads.home.price });
      }
      if (markets.spreads.away?.line !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: gameData.awayTeam, line: markets.spreads.away.line, odds: markets.spreads.away.price });
      }
    } else if (activeMarket === 'total' && markets.totals) {
      if (markets.totals.over?.price !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: 'Over', line: markets.totals.line, odds: markets.totals.over.price });
      }
      if (markets.totals.under?.price !== undefined) {
        syntheticPoints.push({ book_key: selectedBook, snapshot_time: now, outcome_type: 'Under', line: markets.totals.line, odds: markets.totals.under.price });
      }
    }

    return [...base, ...syntheticPoints];
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
    // Moneyline: derive from fair spread for consistency; fallback to composite-only
    const spreadLines = allBooksForPeriod.map(m => m?.spreads?.home?.line).filter((v): v is number => v !== undefined);
    const spreadConsensus = calcMedian(spreadLines);
    if (spreadConsensus !== undefined) {
      const fairSpread = calculateFairSpread(spreadConsensus, pythonPillarScores.composite).fairLine;
      return spreadToMoneyline(fairSpread, gameData.sportKey).homeOdds;
    }
    return calculateFairMoneyline(pythonPillarScores.composite).homeOdds;
  };

  const omiFairLineForChart = getOmiFairLineForChart();

  return (
    <>
      {/* Desktop: OMI Fair Pricing Layout */}
      <div
        className="hidden lg:block h-full relative overflow-y-auto"
        style={{ background: '#0a0a0a', fontVariantNumeric: 'tabular-nums' }}
      >
        {/* Subtle scanline overlay */}
        <div className="pointer-events-none absolute inset-0 z-50" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)',
          mixBlendMode: 'multiply',
        }} />

        <div style={{ borderBottom: '1px solid #27272a' }}>
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
        </div>

        {/* Market tabs + period sub-tabs */}
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-zinc-800/50">
          <div className="flex items-center gap-1">
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

        {/* Two-column: Chart (60%) + Ask Edge AI (40%) */}
        <div className="flex border-b border-zinc-800/50" style={{ height: '280px' }}>
          {/* Left: Chart */}
          <div className="relative p-2" style={{ width: '60%' }}>
            <LineMovementChart
              gameId={gameData.id}
              selection={chartSelection}
              lineHistory={getLineHistoryWithCurrentOdds()}
              selectedBook={selectedBook}
              homeTeam={gameData.homeTeam}
              awayTeam={gameData.awayTeam}
              viewMode={chartViewMode}
              onViewModeChange={setChartViewMode}
              commenceTime={gameData.commenceTime}
              sportKey={gameData.sportKey}
              omiFairLine={omiFairLineForChart}
              activeMarket={activeMarket}
            />
            {showLiveLock && <LiveLockOverlay />}
          </div>
          {/* Right: Ask Edge AI */}
          <div style={{ width: '40%' }}>
            <AskEdgeAI activeMarket={activeMarket} activePeriod={activePeriod} />
          </div>
        </div>

        <OmiFairPricing
          key={`desktop-pricing-${renderKey}-${activeMarket}-${activePeriod}-${selectedBook}`}
          pythonPillars={pythonPillarScores}
          bookmakers={bookmakers}
          gameData={gameData}
          sportKey={gameData.sportKey}
          activeMarket={activeMarket}
          activePeriod={activePeriod}
          selectedBook={selectedBook}
          commenceTime={gameData.commenceTime}
          renderKey={renderKey}
        />

        {/* Why This Price + CEQ Factors — side by side */}
        <div className="flex border-t border-zinc-800/50">
          <div className="w-1/2 border-r border-zinc-800/50">
            <WhyThisPrice
              pythonPillars={pythonPillarScores}
              ceq={activeCeq}
              homeTeam={gameData.homeTeam}
              awayTeam={gameData.awayTeam}
              activeMarket={activeMarket}
              activePeriod={activePeriod}
            />
          </div>
          <div className="w-1/2">
            <CeqFactors ceq={activeCeq} activeMarket={activeMarket} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
          </div>
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
                lineHistory={getLineHistoryWithCurrentOdds()}
                selectedBook={selectedBook}
                homeTeam={gameData.homeTeam}
                awayTeam={gameData.awayTeam}
                viewMode={chartViewMode}
                onViewModeChange={setChartViewMode}
                commenceTime={gameData.commenceTime}
                sportKey={gameData.sportKey}
                compact
                omiFairLine={omiFairLineForChart}
                activeMarket={activeMarket}
              />
            </div>
            {showLiveLock && <LiveLockOverlay />}
          </div>

          <OmiFairPricing
            key={`mobile-pricing-${renderKey}-${activeMarket}-${activePeriod}-${selectedBook}`}
            pythonPillars={pythonPillarScores}
            bookmakers={bookmakers}
            gameData={gameData}
            sportKey={gameData.sportKey}
            activeMarket={activeMarket}
            activePeriod={activePeriod}
            selectedBook={selectedBook}
            commenceTime={gameData.commenceTime}
            renderKey={renderKey}
          />

          <WhyThisPrice
            pythonPillars={pythonPillarScores}
            ceq={activeCeq}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
            activeMarket={activeMarket}
            activePeriod={activePeriod}
          />

          <CeqFactors ceq={activeCeq} activeMarket={activeMarket} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} />
        </div>
      </div>
    </>
  );
}
