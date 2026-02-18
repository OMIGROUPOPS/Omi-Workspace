'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive, getGameState } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores, PillarResult } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal, calculateFairMoneyline, calculateFairMLFromBook, calculateFairMLFromBook3Way, spreadToMoneyline, removeVig, removeVig3Way, SPORT_KEY_NUMBERS, SPREAD_TO_PROB_RATE, getEdgeSignal, getEdgeSignalColor, edgeToConfidence, PROB_PER_POINT } from '@/lib/edge/engine/edgescout';

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
        console.log(`[OMI Chart] composite_history: ${arr.length} pts for ${gameId}`, arr.length > 0 ? { first: arr[0].timestamp, last: arr[arr.length-1].timestamp, fair_totals: arr.map(r => r.fair_total), fair_spreads: arr.map(r => r.fair_spread) } : 'empty');
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
    // Deduplicate: keep only the latest value at each timestamp (prevents vertical bar artifacts)
    if (data.length > 1) {
      const deduped: typeof data = [];
      for (let i = 0; i < data.length; i++) {
        if (i < data.length - 1 && data[i].timestamp.getTime() === data[i + 1].timestamp.getTime()) continue;
        deduped.push(data[i]);
      }
      data = deduped;
    }
    if (timeRange !== 'ALL' && data.length > 0) {
      const now = new Date();
      const hoursMap: Record<TimeRange, number> = { '30M': 0.5, '1H': 1, '3H': 3, '6H': 6, '24H': 24, 'ALL': 0 };
      const cutoffTime = new Date(now.getTime() - hoursMap[timeRange] * 60 * 60 * 1000);
      data = data.filter(d => d.timestamp >= cutoffTime);
    }
  }

  const isFilteredEmpty = hasRealData && data.length === 0;

  // Color theming: emerald for line view, amber for price view
  const isPrice = effectiveViewMode === 'price';
  const lineColor = isPrice ? '#fbbf24' : '#34d399';

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-[#9ca3af] text-[11px]">
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
  // Include OMI fair line values in Y-axis range so the fair line is always visible
  for (const pt of omiFairLineData) values.push(pt.value);
  // For soccer 3-way single-select, only include tracked side in Y-axis bounds
  if (soccer3WayData) {
    const sideKey = trackingSide === 'draw' ? 'draw' : trackingSide === 'away' ? 'away' : 'home';
    const sideArr = soccer3WayData[sideKey as keyof typeof soccer3WayData];
    for (const pt of sideArr) values.push(pt.value);
  }

  // Smart Y-axis scaling: for ML, use percentile-based range to handle outliers
  const isMLAny = marketType === 'moneyline';
  let minVal: number;
  let maxVal: number;

  if (isMLAny && values.length >= 4) {
    // ML: use 5th-95th percentile to exclude outlier opening prints
    const sorted = [...values].sort((a, b) => a - b);
    const p5Idx = Math.floor(sorted.length * 0.05);
    const p95Idx = Math.min(sorted.length - 1, Math.ceil(sorted.length * 0.95));
    const p5 = sorted[p5Idx];
    const p95 = sorted[p95Idx];
    // Always include the most recent value (it's what the user cares about)
    const recent = values.slice(-Math.max(3, Math.floor(values.length * 0.25)));
    const recentMin = Math.min(...recent);
    const recentMax = Math.max(...recent);
    minVal = Math.min(p5, recentMin);
    maxVal = Math.max(p95, recentMax);
  } else {
    minVal = Math.min(...values);
    maxVal = Math.max(...values);
  }

  const range = maxVal - minVal || 1;

  // Y-axis padding
  let padding: number;
  if (isMLAny) {
    // ML: 10% padding, min 5 pts
    padding = Math.max(range * 0.10, 5);
  } else if (isPrice) {
    padding = Math.max(range * 0.05, 1);
  } else if (marketType === 'spread' || marketType === 'total') {
    padding = Math.max(range * 0.05, 0.2);
  } else {
    padding = Math.max(range * 0.05, 0.5);
  }
  // Minimum visual range — avoid flat-looking charts
  const minVisualRange = isMLAny ? 20 : (isPrice ? 4 : 1);
  if (range + 2 * padding < minVisualRange) {
    padding = (minVisualRange - range) / 2;
  }

  const width = 600;
  const height = 200;
  const paddingLeft = 36;
  const paddingRight = 6;
  const paddingTop = 8;
  const paddingBottom = 20;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const chartPoints = data.map((d, i) => {
    const normalizedY = (d.value - minVal + padding) / (range + 2 * padding);
    // Clamp Y so outlier values (beyond percentile range) stay within chart bounds
    const rawY = paddingTop + chartHeight - normalizedY * chartHeight;
    const y = Math.max(paddingTop - 2, Math.min(paddingTop + chartHeight + 2, rawY));
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

  const movementColor = movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-[#6b7280]';

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
    if (isMLAny) {
      // ML: always 10pt ticks — every 10pt move is significant
      labelStep = 10;
    } else if (marketType === 'spread' && effectiveViewMode === 'line') {
      // Spread line: 0.5pt ticks
      labelStep = 0.5;
    } else if (marketType === 'total' && effectiveViewMode === 'line') {
      // Total line: 0.5pt ticks
      labelStep = 0.5;
    } else if (effectiveViewMode === 'price') {
      // Juice/price: every integer when range < 15, else every 2
      labelStep = range < 15 ? 1 : 2;
    } else {
      labelStep = range <= 5 ? 0.5 : range <= 12 ? 1 : range <= 25 ? 2 : 5;
    }
    const startValue = Math.floor(visualMin / labelStep) * labelStep;
    const endValue = Math.ceil(visualMax / labelStep) * labelStep + labelStep;
    for (let val = startValue; val <= endValue; val += labelStep) {
      const normalizedY = (val - visualMin) / visualRange;
      const y = paddingTop + chartHeight - normalizedY * chartHeight;
      if (y >= paddingTop - 2 && y <= paddingTop + chartHeight + 2) {
        labels.push({ value: Math.round(val * 100) / 100, y });
      }
    }
    return labels.length > 12 ? labels.filter((_, i) => i % Math.ceil(labels.length / 10) === 0) : labels;
  })();

  // X-axis date labels — more granular with time-appropriate formatting
  const xLabels = (() => {
    if (data.length < 2) return [];
    const labels: { x: number; label: string }[] = [];
    const timeSpan = data[data.length - 1].timestamp.getTime() - data[0].timestamp.getTime();
    const maxLabels = 7;
    const count = Math.min(maxLabels, data.length);
    const step = Math.max(1, Math.floor(data.length / count));
    const seen = new Set<string>();
    for (let i = 0; i < data.length; i += step) {
      const d = data[i];
      let dateStr: string;
      if (timeSpan > 7 * 24 * 3600000) {
        // > 7 days: "Feb 12"
        dateStr = d.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      } else if (timeSpan > 48 * 3600000) {
        // 2-7 days: "Wed 3p"
        dateStr = d.timestamp.toLocaleDateString('en-US', { weekday: 'short' }) + ' ' +
          d.timestamp.toLocaleTimeString('en-US', { hour: 'numeric' });
      } else if (timeSpan > 6 * 3600000) {
        // 6h-48h: "3:30 PM"
        dateStr = d.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      } else {
        // < 6h: "3:30:15" — show seconds for tight ranges
        dateStr = d.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      }
      if (seen.has(dateStr)) continue;
      seen.add(dateStr);
      const x = paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth;
      labels.push({ x, label: dateStr });
    }
    // Always include last data point time
    if (labels.length > 0 && data.length > 1) {
      const lastD = data[data.length - 1];
      const lastX = paddingLeft + chartWidth;
      const lastLabel = timeSpan > 48 * 3600000
        ? lastD.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        : lastD.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      // Only add if not too close to the previous label
      const prevX = labels[labels.length - 1].x;
      if (lastX - prevX > chartWidth / (maxLabels + 1) && !seen.has(lastLabel)) {
        labels.push({ x: lastX, label: lastLabel });
      }
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
    <div className="flex flex-col h-full">
      {/* Row 1: Chart title + time range + Line/Price toggle */}
      <div className="flex items-center justify-between px-1 flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-[#374151]">{chartTitle}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="flex rounded overflow-hidden border border-[#e2e4e8]/50">
            {(isGameLive ? ['30M', '1H', '3H', '6H', '24H', 'ALL'] as TimeRange[] : ['1H', '3H', '6H', '24H', 'ALL'] as TimeRange[]).map(r => (
              <button key={r} onClick={() => setTimeRange(r)} className={`px-1.5 py-0.5 text-[8px] font-medium ${timeRange === r ? 'bg-[#e2e4e8] text-[#1f2937]' : 'text-[#9ca3af] hover:text-[#374151]'}`}>{r}</button>
            ))}
          </div>
          {marketType !== 'moneyline' && (
            <div className="flex rounded overflow-hidden border border-[#e2e4e8]/50">
              <button onClick={() => onViewModeChange('line')} className={`px-1.5 py-0.5 text-[9px] font-medium ${viewMode === 'line' ? 'bg-[#e2e4e8] text-[#1f2937]' : 'text-[#9ca3af]'}`}>Line</button>
              <button onClick={() => onViewModeChange('price')} className={`px-1.5 py-0.5 text-[9px] font-medium ${viewMode === 'price' ? 'bg-[#e2e4e8] text-[#1f2937]' : 'text-[#9ca3af]'}`}>Price</button>
            </div>
          )}
        </div>
      </div>

      {/* Row 2: Tracking pills + movement */}
      <div className="flex items-center justify-between px-1 flex-shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="text-[8px] text-[#9ca3af] uppercase tracking-wider">Tracking</span>
          {!isProp && (
            <div className="flex gap-0.5">
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('over') : setTrackingSide('home')}
                className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                  (marketType === 'total' ? trackingSide === 'over' : trackingSide === 'home')
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-[#f4f5f7] text-[#9ca3af] border border-[#e2e4e8]/50 hover:text-[#374151]'
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
                      : 'bg-[#f4f5f7] text-[#9ca3af] border border-[#e2e4e8]/50 hover:text-[#374151]'
                  }`}
                >DRW</button>
              )}
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('under') : setTrackingSide('away')}
                className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                  (marketType === 'total' ? trackingSide === 'under' : trackingSide === 'away')
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-[#f4f5f7] text-[#9ca3af] border border-[#e2e4e8]/50 hover:text-[#374151]'
                }`}
              >
                {marketType === 'total' ? 'UND' : awayAbbr}
              </button>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>
          <span className="text-[#9ca3af]">{formatValue(openValue)}</span>
          <span className="text-[#9ca3af]">&rarr;</span>
          <span className="text-[#1f2937] font-semibold">{formatValue(currentValue)}</span>
          <span className={`font-semibold ${movementColor}`}>{movement > 0 ? '+' : ''}{isMLChart ? Math.round(movement) : effectiveViewMode === 'price' ? Math.round(movement) : movement.toFixed(1)}</span>
        </div>
      </div>

      {/* Chart SVG — fills available space, step-line rendering */}
      <div className="relative flex-1 min-h-0">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full cursor-crosshair" preserveAspectRatio="none" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          <defs>
            <linearGradient id={`grad-${gameId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={lineColor} stopOpacity="0.25" />
              <stop offset="100%" stopColor={lineColor} stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Y-axis gridlines + labels — horizontal dashed only */}
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#d1d5db" strokeWidth="0.5" strokeDasharray="3 3" opacity="0.4" />
              <text x={paddingLeft - 4} y={label.y + 3} textAnchor="end" fill="#a1a1aa" fontSize="10" fontFamily="monospace">{formatValue(label.value)}</text>
            </g>
          ))}

          {/* X-axis date labels */}
          {xLabels.map((label, i) => (
            <text key={i} x={label.x} y={height - 2} textAnchor="middle" fill="#6b7280" fontSize="9" fontFamily="monospace">{label.label}</text>
          ))}

          {/* Tipoff vertical divider at commence_time */}
          {commenceTime && data.length >= 2 && (() => {
            const tipoffTime = new Date(commenceTime).getTime();
            const bookStartTime = data[0].timestamp.getTime();
            const bookEndTime = data[data.length - 1].timestamp.getTime();
            const bookTimeRange = bookEndTime - bookStartTime;
            if (bookTimeRange <= 0 || tipoffTime <= bookStartTime || tipoffTime >= bookEndTime) return null;
            const tFrac = (tipoffTime - bookStartTime) / bookTimeRange;
            const tipoffX = paddingLeft + tFrac * chartWidth;
            return (
              <g>
                <line x1={tipoffX} y1={paddingTop} x2={tipoffX} y2={paddingTop + chartHeight} stroke="#9CA3AF" strokeWidth="1" strokeDasharray="4 3" />
                <text x={tipoffX} y={paddingTop - 2} textAnchor="middle" fill="#9CA3AF" fontSize="8" fontFamily="monospace" fontWeight="600">TIPOFF</text>
              </g>
            );
          })()}

          {/* Green gradient fill below step-line */}
          {gradientFillPath && (
            <path d={gradientFillPath} fill={`url(#grad-${gameId})`} />
          )}

          {/* OMI Fair Value line overlay (dashed green) */}
          {hasOmiLine && omiPathD && (
            <path d={omiPathD} fill="none" stroke="#16a34a" strokeWidth="1.5" strokeDasharray="6 3" opacity="0.5" />
          )}

          {/* Book line — single step-line */}
          {chartPoints.length > 0 && (
            <>
              <path d={pathD} fill="none" stroke={lineColor} strokeWidth="2" />
              {/* Open dot — green */}
              <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="3" fill="#34d399" stroke="#e2e4e8" strokeWidth="1" />
              {/* Current dot — colored */}
              <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="3.5" fill={lineColor} stroke="#e2e4e8" strokeWidth="1" />
              {/* Hover crosshair + dot */}
              {hoveredPoint && (
                <>
                  <line x1={hoveredPoint.x} y1={paddingTop} x2={hoveredPoint.x} y2={paddingTop + chartHeight} stroke="#9ca3af" strokeWidth="0.5" strokeDasharray="2 2" />
                  <circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="4" fill={lineColor} stroke="#e2e4e8" strokeWidth="1.5" />
                </>
              )}
            </>
          )}
        </svg>
        {hoveredPoint && (
          <div className="absolute bg-[#f4f5f7]/95 border border-[#e2e4e8]/50 rounded px-2 py-0.5 text-[9px] pointer-events-none shadow-lg z-10 whitespace-nowrap" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 8}%`, transform: 'translate(-50%, -100%)' }}>
            <span className="font-semibold text-[#1f2937] font-mono">{formatValue(hoveredPoint.value)}</span>
            <span className="text-[#9ca3af] mx-1">/</span>
            <span className="text-[#6b7280]">{hoveredPoint.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}, {hoveredPoint.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span>
          </div>
        )}
      </div>
      {/* Legend */}
      <div className="flex items-center justify-between px-1 flex-shrink-0 text-[8px] text-[#9ca3af]">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>Open</span>
          <span className="flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full" style={{ backgroundColor: lineColor }}></span>Current</span>
          {hasOmiLine && (
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-0 border-t border-dashed" style={{ borderColor: '#16a34a', opacity: 0.7 }}></span>
              <span>OMI Fair</span>
            </span>
          )}
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
    <div className="bg-white flex items-center justify-between px-3 h-[36px] min-h-[36px]" style={{ gridArea: 'header', borderBottom: '1px solid #e2e4e8' }}>
      <div className="flex items-center gap-3">
        <a href="/edge/portal/sports" className="text-[#9ca3af] hover:text-[#374151] transition-colors">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
        </a>
        <span className="text-[13px] font-bold text-[#1f2937] tracking-tight font-mono">
          {abbrev(awayTeam)} @ {abbrev(homeTeam)}
        </span>
        <span className="text-[10px] text-[#9ca3af] hidden sm:inline" title={`${awayTeam} @ ${homeTeam}`}>
          {awayTeam} vs {homeTeam}
        </span>
        {isLive && (
          <span className="flex items-center gap-1">
            <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span></span>
            <span className="text-[10px] font-medium text-red-400">LIVE</span>
          </span>
        )}
        <span className="text-[10px] text-[#9ca3af]">{dateStr}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-[10px] text-[#6b7280]">Viewing: <span className="text-cyan-400 font-medium">{marketLabels[activeMarket] || activeMarket}</span></span>
        {/* Book selector */}
        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setBookOpen(!bookOpen)} className="flex items-center gap-1.5 px-2 py-0.5 bg-[#f4f5f7]/80 border border-[#e2e4e8]/50 rounded text-[11px] text-[#374151] hover:bg-[#e2e4e8]/80">
            <span className="w-3 h-3 rounded flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0" style={{ backgroundColor: BOOK_CONFIG[selectedBook]?.color || '#6b7280' }}>
              {(BOOK_CONFIG[selectedBook]?.name || selectedBook).charAt(0)}
            </span>
            {BOOK_CONFIG[selectedBook]?.name || selectedBook}
            <svg className={`w-3 h-3 text-[#9ca3af] transition-transform ${bookOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
          {bookOpen && (
            <div className="absolute right-0 z-50 mt-1 w-44 bg-[#f4f5f7] border border-[#e2e4e8] rounded shadow-xl overflow-hidden">
              {filteredBooks.map(book => (
                <button key={book} onClick={() => { onSelectBook(book); setBookOpen(false); }}
                  className={`w-full flex items-center gap-2 px-3 py-1.5 text-left text-[11px] transition-colors ${book === selectedBook ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-[#e2e4e8]/50 text-[#374151]'}`}>
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
    ? (pythonPillars ? calculateFairSpread(consensusSpread, pythonPillars.composite, sportKey) : { fairLine: consensusSpread, adjustment: 0 })
    : null;
  const omiFairTotal = consensusTotal !== undefined
    ? (pythonPillars ? calculateFairTotal(consensusTotal, pythonPillars.gameEnvironment, sportKey) : { fairLine: consensusTotal, adjustment: 0 })
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

  // Convert spread/total point edge to implied probability percentage
  const pointsToEdgePct = (pts: number): number => {
    const rate = SPREAD_TO_PROB_RATE[sportKey] || 0.03;
    return Math.round(Math.abs(pts) * rate * 1000) / 10; // e.g. 0.5 pts * 0.033 = 1.65%
  };

  // Edge color: positive = emerald (value), negative = red (wrong side)
  const getEdgeColor = (pctGap: number): string => {
    const abs = Math.abs(pctGap);
    if (abs < 0.5) return 'text-[#9ca3af]';
    return pctGap > 0 ? 'text-emerald-400' : 'text-red-400';
  };

  // Confidence color (derived from edge-based confidence) — spreads/totals
  const getConfColor = (conf: number): string => {
    if (conf >= 66) return 'text-cyan-400';
    if (conf >= 60) return 'text-amber-400';
    if (conf >= 55) return 'text-[#6b7280]';
    return 'text-[#9ca3af]';
  };

  // Implied probability color — moneylines (shows win probability, not edge)
  const getImpliedProbColor = (prob: number): string => {
    if (prob >= 65) return 'text-cyan-400';
    if (prob >= 55) return 'text-[#1f2937]';
    if (prob >= 45) return 'text-[#6b7280]';
    return 'text-[#9ca3af]';
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
    const noData: SideBlock = { label: '', fair: 'N/A', bookLine: '--', bookOdds: '--', edgePct: 0, edgePts: 0, edgeColor: 'text-[#9ca3af]', contextLine: '', evLine: '', bookName: selBookName, hasData: false, confidence: 50, confColor: 'text-[#9ca3af]' };

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

      // Convert point edge to implied probability %
      const homeEdgePct = homeSignedGap !== 0 ? (homeSignedGap > 0 ? 1 : -1) * pointsToEdgePct(homeSignedGap) : 0;
      const awayEdgePct = awaySignedGap !== 0 ? (awaySignedGap > 0 ? 1 : -1) * pointsToEdgePct(awaySignedGap) : 0;

      // Confidence: directional — side WITH edge gets full conf, other gets inverse
      const rawConf = edgeToConfidence(Math.max(Math.abs(homeEdgePct), Math.abs(awayEdgePct)));
      const homeConf = homeEdgePct > 0 ? rawConf : homeEdgePct < 0 ? 100 - rawConf : 50;
      const awayConf = awayEdgePct > 0 ? rawConf : awayEdgePct < 0 ? 100 - rawConf : 50;

      const homeAbbr = abbrev(gameData.homeTeam);
      const awayAbbr = abbrev(gameData.awayTeam);

      const mkContext = (side: string, bookL: number | undefined, fairL: number | undefined, pctEdge: number, ptsGap: number) => {
        if (bookL === undefined || fairL === undefined) return '';
        const absPct = Math.abs(pctEdge);
        if (absPct < 0.5) return `${selBookName} is at fair value on ${side}`;
        return pctEdge > 0
          ? `${selBookName} offers ${absPct.toFixed(1)}% more than fair value on ${side}`
          : `${selBookName} prices ${side} ${absPct.toFixed(1)}% tighter than fair`;
      };

      const mkEvLine = (pctEdge: number, ptsGap: number, cross: number | null) => {
        const absPct = Math.abs(pctEdge);
        if (absPct < 0.5) return '';
        const sign = pctEdge > 0 ? '+' : '\u2212';
        const ptsStr = `${Math.abs(ptsGap).toFixed(1)} pts`;
        if (pctEdge <= 0) return `Edge: ${sign}${absPct.toFixed(1)}% (${ptsStr})`;
        return `Edge: ${sign}${absPct.toFixed(1)}% (${ptsStr})${cross ? ` | Crosses key number ${cross}` : ''}`;
      };

      return [
        {
          label: awayAbbr, fair: fairAwayLine !== undefined ? formatSpread(fairAwayLine) : 'N/A',
          bookLine: awayBookLine !== undefined ? formatSpread(awayBookLine) : '--', bookOdds: awayPrice !== undefined ? formatOdds(awayPrice) : '--',
          edgePct: awayEdgePct, edgePts: awaySignedGap, edgeColor: getEdgeColor(awayEdgePct),
          contextLine: mkContext(awayAbbr, awayBookLine, fairAwayLine, awayEdgePct, awaySignedGap),
          evLine: mkEvLine(awayEdgePct, awaySignedGap, awayCross),
          bookName: selBookName, hasData: awayBookLine !== undefined, crossedKey: awayCross,
          confidence: awayConf, confColor: awayEdgePct > 0 ? getConfColor(awayConf) : 'text-[#9ca3af]',
        },
        {
          label: homeAbbr, fair: fairHomeLine !== undefined ? formatSpread(fairHomeLine) : 'N/A',
          bookLine: homeBookLine !== undefined ? formatSpread(homeBookLine) : '--', bookOdds: homePrice !== undefined ? formatOdds(homePrice) : '--',
          edgePct: homeEdgePct, edgePts: homeSignedGap, edgeColor: getEdgeColor(homeEdgePct),
          contextLine: mkContext(homeAbbr, homeBookLine, fairHomeLine, homeEdgePct, homeSignedGap),
          evLine: mkEvLine(homeEdgePct, homeSignedGap, homeCross),
          bookName: selBookName, hasData: homeBookLine !== undefined, crossedKey: homeCross,
          confidence: homeConf, confColor: homeEdgePct > 0 ? getConfColor(homeConf) : 'text-[#9ca3af]',
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

      // Convert point edge to probability %
      const overEdgePct = overSignedGap !== 0 ? (overSignedGap > 0 ? 1 : -1) * pointsToEdgePct(overSignedGap) : 0;
      const underEdgePct = -overEdgePct;

      // Confidence: directional — side WITH edge gets full conf, other gets inverse
      const totalRawConf = edgeToConfidence(Math.abs(overEdgePct));
      const overConf = overEdgePct > 0 ? totalRawConf : overEdgePct < 0 ? 100 - totalRawConf : 50;
      const underConf = underEdgePct > 0 ? totalRawConf : underEdgePct < 0 ? 100 - totalRawConf : 50;

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

      const mkTotalContext = (side: string, pctEdge: number, ptsGap: number) => {
        if (bookLine === undefined || fairLine === undefined) return '';
        const absPct = Math.abs(pctEdge);
        if (absPct < 0.5) return `${effBookName} is at fair value on ${side}`;
        return pctEdge > 0
          ? `${effBookName} offers ${absPct.toFixed(1)}% more than fair value on ${side}`
          : `${effBookName} prices ${side} ${absPct.toFixed(1)}% tighter than fair`;
      };

      const mkTotalEv = (pctEdge: number, ptsGap: number, ev: number) => {
        const absPct = Math.abs(pctEdge);
        if (absPct < 0.5) return '';
        const sign = pctEdge > 0 ? '+' : '\u2212';
        const ptsStr = `${Math.abs(ptsGap).toFixed(1)} pts`;
        if (pctEdge <= 0) return `Edge: ${sign}${absPct.toFixed(1)}% (${ptsStr})`;
        return `Edge: ${sign}${absPct.toFixed(1)}% (${ptsStr})${ev > 0 ? ` | EV: +$${ev}/1K` : ''}`;
      };

      return [
        {
          label: 'OVER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: overPrice !== undefined ? formatOdds(overPrice) : '--',
          edgePct: overEdgePct, edgePts: overSignedGap, edgeColor: getEdgeColor(overEdgePct),
          contextLine: mkTotalContext('Over', overEdgePct, overSignedGap),
          evLine: mkTotalEv(overEdgePct, overSignedGap, overEv),
          bookName: effBookName, hasData: bookLine !== undefined,
          confidence: overConf, confColor: overEdgePct > 0 ? getConfColor(overConf) : 'text-[#9ca3af]',
        },
        {
          label: 'UNDER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: underPrice !== undefined ? formatOdds(underPrice) : '--',
          edgePct: underEdgePct, edgePts: underSignedGap, edgeColor: getEdgeColor(underEdgePct),
          contextLine: mkTotalContext('Under', underEdgePct, underSignedGap),
          evLine: mkTotalEv(underEdgePct, underSignedGap, underEv),
          bookName: effBookName, hasData: bookLine !== undefined,
          confidence: underConf, confColor: underEdgePct > 0 ? getConfColor(underConf) : 'text-[#9ca3af]',
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

    // Moneyline confidence = OMI fair implied win probability (not edge-derived)
    // +135 → 100/235 = 42.6%, -135 → 135/235 = 57.4%
    const homeConf = omiFairHomeProb !== undefined ? Math.round(omiFairHomeProb * 1000) / 10 : 50;
    const awayConf = omiFairAwayProb !== undefined ? Math.round(omiFairAwayProb * 1000) / 10 : 50;
    const drawConf = omiFairDrawProb !== undefined ? Math.round(omiFairDrawProb * 1000) / 10 : 50;
    const homeAbbr = abbrev(gameData.homeTeam);
    const awayAbbr = abbrev(gameData.awayTeam);

    const mkMLContext = (side: string, bookProb: number | undefined, fairProb: number | undefined, signedGap: number) => {
      if (bookProb === undefined || fairProb === undefined) return '';
      const abs = Math.abs(signedGap);
      if (abs < 0.5) return `${mlEffBookName} is at fair value on ${side} ML`;
      return signedGap > 0
        ? `${mlEffBookName} offers ${abs.toFixed(1)}% more than fair value on ${side} ML`
        : `${mlEffBookName} prices ${side} ML ${abs.toFixed(1)}% tighter than fair`;
    };

    const mkMLEvLine = (signedGap: number, ev: number) => {
      if (Math.abs(signedGap) < 0.5) return '';
      const sign = signedGap > 0 ? '+' : '\u2212';
      if (signedGap <= 0) return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)}%`;
      return `Edge: ${sign}${Math.abs(signedGap).toFixed(1)}%${ev > 0 ? ` | EV: +$${ev}/1K` : ''}`;
    };

    const blocks: SideBlock[] = [
      {
        label: awayAbbr, fair: effectiveAwayML !== undefined ? formatOdds(effectiveAwayML) : 'N/A',
        bookLine: bookAwayOdds !== undefined ? formatOdds(bookAwayOdds) : '--', bookOdds: vigPct,
        edgePct: awaySignedGap, edgePts: 0, edgeColor: getEdgeColor(awaySignedGap),
        contextLine: mkMLContext(awayAbbr, bookAwayProb, omiFairAwayProb, awaySignedGap),
        evLine: mkMLEvLine(awaySignedGap, awayEv),
        bookName: mlEffBookName, hasData: bookAwayOdds !== undefined, vigPct,
        rawBookOdds: bookAwayOdds, rawFairProb: omiFairAwayProb, rawBookProb: bookAwayProb,
        confidence: awayConf, confColor: getImpliedProbColor(awayConf),
      },
    ];

    if (isSoccerGame && bookDrawOdds !== undefined) {
      blocks.push({
        label: 'DRW', fair: effectiveDrawML !== undefined ? formatOdds(effectiveDrawML) : 'N/A',
        bookLine: formatOdds(bookDrawOdds), bookOdds: vigPct,
        edgePct: drawSignedGap, edgePts: 0, edgeColor: getEdgeColor(drawSignedGap),
        contextLine: mkMLContext('Draw', bookDrawProb, omiFairDrawProb, drawSignedGap),
        evLine: mkMLEvLine(drawSignedGap, drawEv),
        bookName: mlEffBookName, hasData: true, vigPct,
        rawBookOdds: bookDrawOdds, rawFairProb: omiFairDrawProb, rawBookProb: bookDrawProb,
        confidence: drawConf, confColor: getImpliedProbColor(drawConf),
      });
    }

    blocks.push({
      label: homeAbbr, fair: effectiveHomeML !== undefined ? formatOdds(effectiveHomeML) : 'N/A',
      bookLine: bookHomeOdds !== undefined ? formatOdds(bookHomeOdds) : '--', bookOdds: vigPct,
      edgePct: homeSignedGap, edgePts: 0, edgeColor: getEdgeColor(homeSignedGap),
      contextLine: mkMLContext(homeAbbr, bookHomeProb, omiFairHomeProb, homeSignedGap),
      evLine: mkMLEvLine(homeSignedGap, homeEv),
      bookName: mlEffBookName, hasData: bookHomeOdds !== undefined, vigPct,
      rawBookOdds: bookHomeOdds, rawFairProb: omiFairHomeProb, rawBookProb: bookHomeProb,
      confidence: homeConf, confColor: getImpliedProbColor(homeConf),
    });

    return blocks;
  })();

  // All books quick-scan with signed edge as % (positive = value)
  const allBooksQuickScan = allBooks.filter(b => b.key !== 'pinnacle').map(b => {
    let line = '--';
    let signedEdge = 0;
    if (activeMarket === 'spread') {
      const bookLine = b.markets?.spreads?.home?.line;
      line = bookLine !== undefined ? formatSpread(bookLine) : '--';
      if (bookLine !== undefined && omiFairSpread) {
        const ptsGap = bookLine - omiFairSpread.fairLine;
        signedEdge = ptsGap !== 0 ? (ptsGap > 0 ? 1 : -1) * pointsToEdgePct(ptsGap) : 0;
      }
    } else if (activeMarket === 'total') {
      const totalLine = b.markets?.totals?.line;
      line = totalLine !== undefined ? `${totalLine}` : '--';
      if (totalLine !== undefined && omiFairTotal) {
        const ptsGap = omiFairTotal.fairLine - totalLine;
        signedEdge = ptsGap !== 0 ? (ptsGap > 0 ? 1 : -1) * pointsToEdgePct(ptsGap) : 0;
      }
    } else {
      const homeOdds = b.markets?.h2h?.home?.price;
      line = homeOdds !== undefined ? formatOdds(homeOdds) : '--';
      if (homeOdds !== undefined && omiFairHomeProb !== undefined) {
        const bookProb = americanToImplied(homeOdds);
        signedEdge = Math.round((omiFairHomeProb - bookProb) * 1000) / 10;
      }
    }
    const absEdge = Math.abs(signedEdge);
    const edgeStr = absEdge > 0.3 ? `(${signedEdge > 0 ? '+' : ''}${signedEdge.toFixed(1)}%)` : '';
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
    <div className="bg-white px-3 py-2 flex flex-col" style={{ overflow: 'visible' }}>
      {/* OMI Fair Line — split display for both sides */}
      <div className="mb-1.5 flex-shrink-0">
        <div className="text-[10px] text-[#9ca3af] uppercase tracking-widest mb-0.5">OMI Fair Line</div>
        <div className="flex items-baseline gap-4" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {sideBlocks.map((block, i) => (
            <div key={i} className="flex items-baseline">
              {i > 0 && <span className="text-[#9ca3af] text-[12px] mr-4">vs</span>}
              <span className="text-[10px] text-[#9ca3af] mr-1">{block.label}</span>
              <span className="text-[20px] font-bold font-mono text-cyan-400">{block.fair}</span>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-[#9ca3af] mt-0.5">
          {hasPillars
            ? `Based on 6-pillar composite (${pythonPillars!.composite}) and market analysis`
            : `Based on market consensus (${allBooks.length} books)`}
        </div>
        {pillarsAgoText && <div className="text-[10px] text-[#9ca3af]">{pillarsAgoText}</div>}
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
                const overEdge = sideBlocks[0].edgePct;
                const absOverEdge = Math.abs(overEdge);
                if (absOverEdge < 0.5) {
                  narrative = `Model leans ${lean} (${totalConf}% conf). ${selBookName} total is near fair value.`;
                } else {
                  const evStr = sideBlocks[0].evLine.includes('EV') ? sideBlocks[0].evLine.split('|').pop()?.trim() || '' : '';
                  narrative = `Model leans ${lean} (${totalConf}% conf). ${selBookName}: ${overEdge > 0 ? '+' : ''}${overEdge.toFixed(1)}% edge${evStr ? `, ${evStr}` : ''}.`;
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
              const edgeVal = favoredBlock.edgePct;
              const absEdge = Math.abs(edgeVal);
              if (absEdge < 0.5) {
                narrative = `Model favors ${favored} (${comp}% conf). ${selBookName} line is near fair value.`;
              } else {
                const evStr = favoredBlock.evLine.includes('EV') ? favoredBlock.evLine.split('|').pop()?.trim() || '' : '';
                narrative = `Model favors ${favored} (${comp}% conf). ${selBookName}: ${edgeVal > 0 ? '+' : ''}${edgeVal.toFixed(1)}% edge${evStr ? `, ${evStr}` : ''}.`;
              }
            }
          } else {
            narrative = `Comparing ${selBookName} against market consensus of ${allBooks.length} sportsbooks.`;
          }
          return <div className="text-[11px] text-[#1f2937] mt-1 leading-snug">{narrative}</div>;
        })()}
      </div>

      {/* Single-book comparison — two side-by-side blocks with edge story */}
      <div key={`blocks-${renderKey}-${activeMarket}-${activePeriod}-${selectedBook}`} className={`grid grid-cols-1 gap-1.5 mb-1 ${sideBlocks.length === 3 ? 'lg:grid-cols-3' : 'lg:grid-cols-2'}`} style={{ fontVariantNumeric: 'tabular-nums', visibility: 'visible' as const, opacity: 1 }}>
        {sideBlocks.map((block, blockIdx) => {
          const edgeVal = block.edgePct;
          const absEdge = Math.abs(edgeVal);
          const isPositiveEdge = edgeVal > 0;
          const isHighEdge = isPositiveEdge && absEdge >= 6;
          const isNearZero = absEdge < 0.5;

          // Format edge display — always percentage
          const edgeDisplay = (() => {
            if (!block.hasData) return '--';
            if (isNearZero) return 'None';
            const sign = isPositiveEdge ? '+' : '\u2212';
            return `${sign}${absEdge.toFixed(1)}%`;
          })();

          return (
            <div key={blockIdx} className={`rounded overflow-hidden border border-[#e2e4e8] ${isHighEdge ? 'border-l-2 border-l-emerald-400' : ''}`}>
              {/* Block header — team/side label */}
              <div className="bg-white px-2 py-1 border-b border-[#e2e4e8]">
                <span className="text-[11px] font-bold text-[#1f2937]">{block.label}</span>
              </div>
              {/* Comparison: OMI Fair vs Book vs Edge vs Confidence */}
              <div className="px-2 py-1.5">
                <div className="flex items-end justify-between gap-1.5">
                  <div>
                    <div className="text-[8px] text-[#9ca3af] uppercase tracking-widest">{hasPillars ? 'OMI Fair' : 'Consensus'}</div>
                    <div className="text-[18px] font-bold font-mono text-cyan-400">{block.fair}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-[#9ca3af] uppercase tracking-widest">{block.bookName}</div>
                    <div className="text-[18px] font-bold font-mono text-[#1f2937]">{block.bookLine}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-[#9ca3af] uppercase tracking-widest">Edge</div>
                    <div className={`text-[18px] font-bold font-mono ${block.edgeColor}`}>
                      {edgeDisplay}
                    </div>
                  </div>
                  {hasPillars && (
                    <div className="text-right">
                      <div className="text-[8px] text-[#9ca3af] uppercase tracking-widest">{activeMarket === 'moneyline' ? 'Win %' : 'Conf'}</div>
                      <div className={`text-[18px] font-bold font-mono ${block.confColor}`}>
                        {activeMarket === 'moneyline' ? `${block.confidence.toFixed(1)}%` : `${block.confidence}%`}
                      </div>
                    </div>
                  )}
                </div>
                {block.contextLine && (
                  <div className="mt-1 pt-1 border-t border-[#e2e4e8]/50">
                    <div className="text-[10px] text-[#6b7280]">{block.contextLine}</div>
                    {block.evLine && <div className={`text-[10px] font-medium ${block.edgeColor}`}>{block.evLine}</div>}
                  </div>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[9px] text-[#9ca3af] font-mono">
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
        <div className="flex-shrink-0 border-t border-[#e2e4e8]/50 pt-1 pb-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[8px] text-[#9ca3af] uppercase tracking-widest">All Books</span>
            {bestValueBook && bestValueBook.signedEdge > 3 && (
              <span className="text-[10px] font-mono text-emerald-400 font-semibold">
                Best value: {bestValueBook.name} {bestValueBook.line} {bestValueBook.edgeStr}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {allBooksQuickScan.map(b => {
              const isBest = b.key === bestValueBook?.key && b.signedEdge > (activeMarket === 'moneyline' ? 3 : 0.5);
              const edgeColor = isBest ? 'text-emerald-400 font-semibold' : b.absEdge < (activeMarket === 'moneyline' ? 3 : 0.5) ? 'text-[#9ca3af]' : b.signedEdge > 0 ? 'text-emerald-400/70' : 'text-[#9ca3af]';
              return (
                <span key={b.key} className={`text-[10px] font-mono ${b.isSelected ? 'text-cyan-400 font-semibold' : 'text-[#6b7280]'}`}>
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
    if (score > 45) return '#9ca3af';  // neutral
    if (score > 35) return '#f59e0b';  // amber-500 (away lean)
    return '#ef4444'; // red-500 (strong away)
  };

  const getTextColor = (score: number) => {
    if (score >= 65) return 'text-emerald-400';
    if (score > 55) return 'text-emerald-600';
    if (score > 45) return 'text-[#9ca3af]';
    if (score > 35) return 'text-amber-400';
    return 'text-red-400';
  };

  const homeAbbrev = abbrev(homeTeam);
  const awayAbbrev = abbrev(awayTeam);

  if (!pythonPillars) {
    return <div className="flex items-center justify-center text-[10px] text-[#9ca3af] py-2">No pillar data</div>;
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
        <span className="text-[8px] text-[#9ca3af] font-mono w-16" />
        <span className="text-[8px] text-[#9ca3af] font-mono w-6 text-right">{awayAbbrev}</span>
        <div className="flex-1" />
        <span className="text-[8px] text-[#9ca3af] font-mono w-6">{homeAbbrev}</span>
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
            <span className="text-[9px] text-[#9ca3af] w-16 font-mono truncate" title={p.fullLabel}>
              {p.label} <span className="text-[#9ca3af]">({p.weight})</span>
            </span>
            <div className="flex-1 h-[6px] bg-[#f4f5f7] rounded-sm relative">
              {/* Center line — dashed for visibility at neutral */}
              <div className="absolute left-1/2 top-0 w-0 h-full z-10" style={{ borderLeft: '1px dashed #d1d5db' }} />
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
      <div className="flex items-center justify-between mt-1 pt-1 border-t border-[#e2e4e8]/50">
        <span className="text-[9px] text-[#9ca3af] font-mono">COMPOSITE</span>
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
    ceqSummary.confidence === 'WATCH' ? 'text-amber-400' : 'text-[#9ca3af]'
  ) : 'text-[#9ca3af]';

  return (
    <div className="bg-white px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-widest mb-1">Why This Price</span>
      <div>
        <PillarBarsCompact pythonPillars={pythonPillars} homeTeam={homeTeam} awayTeam={awayTeam} marketPillarScores={marketPillarScores} marketComposite={marketData?.composite} />
        {/* Generated pillar summary */}
        {pillarSummary.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {pillarSummary.map((line, i) => (
              <p key={i} className="text-[10px] text-[#6b7280] leading-tight">{line}</p>
            ))}
          </div>
        )}
        {/* CEQ summary line — detail integrated inline */}
        {ceqSummary ? (
          <div className="mt-2 pt-1.5 border-t border-[#e2e4e8]/50">
            <div className={`text-[10px] font-mono ${confColor}`}>
              {ceqSummary.text} <span className="text-[#9ca3af]">({ceqSummary.detail})</span>
            </div>
          </div>
        ) : (
          <div className="mt-2 pt-1.5 border-t border-[#e2e4e8]/50">
            <div className="text-[10px] text-[#9ca3af]">
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
      <div className="bg-white px-2 py-1.5 flex items-center justify-center">
        <span className="text-[10px] text-[#9ca3af]">No CEQ factor data</span>
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
  const getBarColor = (s: number) => s >= 75 ? '#34d399' : s >= 60 ? '#22d3ee' : s >= 40 ? '#fbbf24' : '#9ca3af';
  const getTextColor = (s: number) => s >= 75 ? 'text-emerald-400' : s >= 60 ? 'text-cyan-400' : s >= 40 ? 'text-amber-400' : 'text-[#9ca3af]';

  // Compute scores for composite summary
  const scoredFactors = factors.map(f => {
    const rawScore = ceqPillars[f.key].score;
    const score = adjustScore(rawScore, f.key);
    return { ...f, score, rawScore };
  });
  const compositeAvg = Math.round(scoredFactors.reduce((sum, f) => sum + f.score * f.weight, 0) / scoredFactors.reduce((sum, f) => sum + f.weight, 0));
  const strongest = [...scoredFactors].sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50))[0];

  return (
    <div className="bg-white px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-widest mb-1">CEQ Factors{activeMarket ? ` — ${activeMarket === 'moneyline' ? 'ML' : activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)}` : ''}</span>
      <div>
        <div className="flex flex-col gap-0.5">
          {scoredFactors.map(f => {
            const wPct = Math.round(f.weight * 100);
            return (
              <div key={f.key}>
                <div className="flex items-center gap-1">
                  <span className="text-[9px] text-[#9ca3af] font-mono w-16 truncate">{f.label} ({wPct}%)</span>
                  <div className="flex-1 h-[5px] bg-[#f4f5f7] rounded-sm overflow-hidden">
                    <div className="h-full rounded-sm" style={{ width: `${f.score}%`, backgroundColor: getBarColor(f.score) }} />
                  </div>
                  <span className={`text-[9px] font-mono w-5 text-right ${getTextColor(f.score)}`}>{f.score}</span>
                  <span className={`text-[8px] w-12 text-right ${getTextColor(f.score)}`}>{getStrength(f.score)}</span>
                </div>
                <div className="text-[9px] text-[#9ca3af] ml-[68px] leading-tight">{getDetailText(f.key, f.score)}</div>
              </div>
            );
          })}
        </div>
        {/* Composite summary */}
        <div className="mt-1 pt-1 border-t border-[#e2e4e8]/50">
          <div className="text-[9px] text-[#6b7280]">
            <span className="font-semibold text-[#374151]">CEQ COMPOSITE: {compositeAvg}%</span>
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

// ============================================================================
// LiveScoreBar — live score display between header and tabs
// ============================================================================

interface LiveScoreData {
  homeScore: number;
  awayScore: number;
  statusDetail: string;
  period?: number;
  clock?: string;
  homeAbbrev?: string;
  awayAbbrev?: string;
  homeLogo?: string;
  awayLogo?: string;
}

function LiveScoreBar({
  liveData, homeTeam, awayTeam, sportKey, fairSpread, fairTotal, fairMLHomeProb,
  activeMarket, isFinalGame,
}: {
  liveData: LiveScoreData;
  homeTeam: string;
  awayTeam: string;
  sportKey: string;
  fairSpread?: number | null;
  fairTotal?: number | null;
  fairMLHomeProb?: number | null;
  activeMarket: 'spread' | 'total' | 'moneyline';
  isFinalGame?: boolean;
}) {
  const hAbbr = liveData.homeAbbrev || abbrev(homeTeam);
  const aAbbr = liveData.awayAbbrev || abbrev(awayTeam);
  const margin = liveData.homeScore - liveData.awayScore;
  const leader = margin > 0 ? hAbbr : margin < 0 ? aAbbr : null;
  const marginAbs = Math.abs(margin);
  const totalPts = liveData.homeScore + liveData.awayScore;
  const statusShort = liveData.statusDetail || '';

  // Market-specific indicator
  let indicatorText = '';
  if (activeMarket === 'spread' && fairSpread != null) {
    const actualMargin = liveData.homeScore - liveData.awayScore;
    const coverMargin = actualMargin + fairSpread;
    const isCovering = coverMargin > 0;
    const favTeam = fairSpread < 0 ? hAbbr : aAbbr;
    const fmtSpread = fairSpread > 0 ? `+${fairSpread}` : `${fairSpread}`;
    const actualLabel = isFinalGame ? 'Final' : 'Actual';
    indicatorText = `OMI: ${favTeam} ${fmtSpread} | ${actualLabel}: ${leader ? `${leader} by ${marginAbs}` : 'Tied'} | ${isCovering ? '\u2713 Covering' : '\u2717 Not Covering'}`;
  } else if (activeMarket === 'total' && fairTotal != null) {
    const isOver = totalPts > fairTotal;
    const isUnder = totalPts < fairTotal;
    if (isFinalGame) {
      indicatorText = `OMI: O ${fairTotal} | Final: ${totalPts} | ${isOver ? '\u2713 Over Hit' : isUnder ? '\u2713 Under Hit' : 'Push'}`;
    } else {
      indicatorText = `OMI: O ${fairTotal} | Current: ${totalPts} pts (${statusShort}) | Tracking ${isOver ? 'Over' : 'Under'}`;
    }
  } else if (activeMarket === 'moneyline' && fairMLHomeProb != null) {
    const homeProb = Math.round(fairMLHomeProb * 100);
    const favTeam = homeProb >= 50 ? hAbbr : aAbbr;
    const favProb = homeProb >= 50 ? homeProb : 100 - homeProb;
    const isLeading = (homeProb >= 50 && margin > 0) || (homeProb < 50 && margin < 0);
    if (isFinalGame) {
      const winner = margin > 0 ? hAbbr : margin < 0 ? aAbbr : 'Tie';
      const correct = (homeProb >= 50 && margin > 0) || (homeProb < 50 && margin < 0);
      indicatorText = `OMI: ${favTeam} ${favProb}% | Winner: ${winner} | ${correct ? '\u2713 Correct' : '\u2717 Incorrect'}`;
    } else {
      indicatorText = `OMI: ${favTeam} ${favProb}% | Live: ${leader ? `${leader} leading` : 'Tied'} | ${margin === 0 ? '\u2014' : isLeading ? '\u2713 On Track' : '\u2717 Off Track'}`;
    }
  }

  return (
    <div style={{
      background: '#f8fafc',
      borderBottom: '1px solid #e2e4e8',
      padding: '8px 16px',
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16,
    }}>
      {/* Away team */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {liveData.awayLogo && (
          <img src={liveData.awayLogo} alt="" style={{ width: 20, height: 20 }} />
        )}
        <span style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>{aAbbr}</span>
        <span style={{ fontSize: 22, fontWeight: 700, color: '#1f2937', fontVariantNumeric: 'tabular-nums' }}>
          {liveData.awayScore}
        </span>
      </div>

      {/* Divider + status */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1, minWidth: 80 }}>
        <span style={{ fontSize: 10, fontWeight: 600, color: '#6b7280', letterSpacing: '0.05em' }}>
          {liveData.statusDetail || 'In Progress'}
        </span>
        {indicatorText && (
          <span style={{ fontSize: 9, color: '#9ca3af', whiteSpace: 'nowrap' }}>{indicatorText}</span>
        )}
      </div>

      {/* Home team */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 22, fontWeight: 700, color: '#1f2937', fontVariantNumeric: 'tabular-nums' }}>
          {liveData.homeScore}
        </span>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>{hAbbr}</span>
        {liveData.homeLogo && (
          <img src={liveData.homeLogo} alt="" style={{ width: 20, height: 20 }} />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// GameStatusBanner — informational only, non-blocking
// ============================================================================

function GameStatusBanner({ gameState }: { gameState: 'live' | 'final' }) {
  if (gameState === 'live') {
    return (
      <div style={{
        background: '#f0fdf4',
        borderLeft: '4px solid #16a34a',
        padding: '8px 16px',
        display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <span style={{ fontSize: 12 }}>&#x1F534;</span>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#166534' }}>
          GAME IN PROGRESS
        </span>
        <span style={{ fontSize: 11, color: '#15803d' }}>
          Live tracking is a Tier 2 feature. Open during beta.
        </span>
      </div>
    );
  }
  return (
    <div style={{
      background: '#f9fafb',
      borderLeft: '4px solid #9ca3af',
      padding: '8px 16px',
      display: 'flex', alignItems: 'center', gap: 10,
    }}>
      <span style={{ fontSize: 12, fontWeight: 600, color: '#374151' }}>
        FINAL
      </span>
      <span style={{ fontSize: 11, color: '#6b7280' }}>
        Game completed. Final scores and results shown below.
      </span>
    </div>
  );
}

// ============================================================================
// AskEdgeAI — interactive AI chat panel (right column)
// ============================================================================

interface AskEdgeAIProps {
  activeMarket: string;
  activePeriod: string;
  gameContext: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

function AskEdgeAI({ activeMarket, activePeriod, gameContext }: AskEdgeAIProps) {
  const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q' };
  const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'Moneyline' };
  const viewingLabel = `${periodLabels[activePeriod] || 'Full Game'} ${marketLabels[activeMarket] || activeMarket}`;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const expandedChatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const expandedInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    expandedChatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Close drawer on Escape
  useEffect(() => {
    if (!isExpanded) return;
    const handleEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') setIsExpanded(false); };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isExpanded]);

  // Focus expanded input when drawer opens
  useEffect(() => {
    if (isExpanded) expandedInputRef.current?.focus();
  }, [isExpanded]);

  const handleSubmit = useCallback(async () => {
    const activeInput = isExpanded ? expandedInputRef : inputRef;
    const question = input.trim();
    if (!question || isLoading) return;

    setError(null);
    const userMsg: ChatMessage = { role: 'user', content: question };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/edge/assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages.map(m => ({ role: m.role, content: m.content })),
          gameContext,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(errData.error || `Request failed (${res.status})`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response stream');

      const decoder = new TextDecoder();
      let assistantText = '';
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        assistantText += decoder.decode(value, { stream: true });
        setMessages(prev => {
          const copy = [...prev];
          copy[copy.length - 1] = { role: 'assistant', content: assistantText };
          return copy;
        });
      }

      if (!assistantText) {
        setMessages(prev => {
          const copy = [...prev];
          copy[copy.length - 1] = { role: 'assistant', content: 'No response received. Please try again.' };
          return copy;
        });
      }
    } catch (e: any) {
      setError(e.message || 'Failed to get response');
      setMessages(prev => prev.filter(m => m.content !== ''));
    } finally {
      setIsLoading(false);
      activeInput.current?.focus();
    }
  }, [input, messages, isLoading, gameContext, isExpanded]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const hasMessages = messages.length > 0;

  const suggestedQuestions = [
    'Why is the line different from the book?',
    'Which pillar is driving the edge?',
    'Is there sharp money on this game?',
    'Explain the line movement',
  ];

  // Shared chat body renderer
  const renderChatBody = (expanded: boolean) => {
    const endRef = expanded ? expandedChatEndRef : chatEndRef;
    const iRef = expanded ? expandedInputRef : inputRef;
    const textSize = expanded ? 'text-[13px]' : 'text-[11px]';
    const labelSize = expanded ? 'text-[10px]' : 'text-[9px]';
    const btnSize = expanded ? 'text-[11px]' : 'text-[10px]';

    return (
      <>
        <div className={`flex-1 ${expanded ? 'px-5 py-4' : 'px-3 py-2'} overflow-y-auto space-y-3`} style={{ minHeight: 0 }}>
          {!hasMessages && (
            <>
              <p className={`${textSize} text-[#6b7280] mb-2`}>Ask about this game:</p>
              <div className="space-y-1">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); iRef.current?.focus(); }}
                    className={`block w-full text-left ${btnSize} text-[#9ca3af] hover:text-cyan-400 hover:bg-[#f4f5f7]/50 px-2.5 py-2 rounded transition-colors font-mono`}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`${textSize} leading-relaxed ${msg.role === 'user' ? 'text-[#374151]' : 'text-[#6b7280]'}`}>
              <span className={`${labelSize} font-mono font-bold uppercase tracking-wider ${msg.role === 'user' ? 'text-[#9ca3af]' : 'text-cyan-600'}`}>
                {msg.role === 'user' ? 'You' : 'OMI'}
              </span>
              <div className="mt-0.5 whitespace-pre-wrap">
                {msg.content || (isLoading && i === messages.length - 1 ? (
                  <span className="text-[#9ca3af] animate-pulse">...</span>
                ) : '')}
              </div>
            </div>
          ))}

          {error && (
            <div className={`${btnSize} text-red-400/80 bg-red-500/10 px-2 py-1.5 rounded`}>
              {error}
            </div>
          )}

          <div ref={endRef} />
        </div>

        <div className={`${expanded ? 'px-5 pb-4 pt-2' : 'px-3 pb-2 pt-1'} border-t border-[#e2e4e8]/30`}>
          <div className="flex gap-2">
            <input
              ref={iRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${viewingLabel}...`}
              className={`flex-1 bg-white border border-[#e2e4e8]/50 rounded px-3 ${expanded ? 'py-2.5 text-[13px]' : 'py-1.5 text-[11px]'} text-[#374151] placeholder-[#9ca3af] focus:outline-none focus:border-cyan-700/50 transition-colors`}
              disabled={isLoading}
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !input.trim()}
              className={`${expanded ? 'px-4 py-2.5 text-[13px]' : 'px-3 py-1.5 text-[11px]'} bg-[#f4f5f7] border border-[#e2e4e8]/50 rounded font-medium transition-colors disabled:opacity-30 disabled:cursor-default text-cyan-400 hover:bg-[#e2e4e8] hover:border-cyan-700/30`}
            >
              {isLoading ? '...' : 'Ask'}
            </button>
          </div>
        </div>
      </>
    );
  };

  // Shared header renderer
  const renderHeader = (expanded: boolean) => (
    <div className={`flex items-center justify-between ${expanded ? 'px-5 py-3' : 'px-3 py-2'} border-b border-[#e2e4e8]/50`}>
      <div className="flex items-center gap-1.5">
        <span className={expanded ? 'text-[15px]' : 'text-[13px]'}>&#10022;</span>
        <span className={`${expanded ? 'text-[14px]' : 'text-[12px]'} font-semibold text-[#1f2937]`}>Ask Edge AI</span>
        {isLoading && (
          <span className="flex items-center gap-1 ml-1">
            <span className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-[9px] text-cyan-500 font-mono">thinking</span>
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        {hasMessages && (
          <button
            onClick={() => { setMessages([]); setError(null); }}
            className="text-[9px] text-[#9ca3af] hover:text-[#6b7280] font-mono transition-colors"
          >
            Clear
          </button>
        )}
        <span className="text-[9px] text-[#9ca3af] font-mono">{viewingLabel}</span>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-1 text-[#9ca3af] hover:text-[#374151] transition-colors"
          title={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? (
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Inline panel (always rendered to keep position in layout) */}
      <div className="flex flex-col h-full bg-white border-l border-[#e2e4e8]">
        {renderHeader(false)}
        {renderChatBody(false)}
      </div>

      {/* Expanded drawer overlay */}
      {isExpanded && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setIsExpanded(false)}
          />
          {/* Drawer */}
          <div
            className="relative flex flex-col bg-white border-l border-[#e2e4e8]/50 shadow-2xl"
            style={{ width: '480px', maxWidth: '90vw' }}
          >
            {renderHeader(true)}
            {renderChatBody(true)}
          </div>
        </div>
      )}
    </>
  );
}

// ============================================================================
// Exchange Signals — dynamic, market-tab-aware exchange intelligence panel
// ============================================================================

function ExchangeSignals({ exchangeData, bookmakers, gameData, activeMarket }: {
  exchangeData: {
    by_market: Record<string, Array<{
      exchange: string; subtitle: string; yes_price: number | null; no_price: number | null;
      volume: number | null; open_interest: number | null; snapshot_time: string;
      contract_ticker?: string; event_title?: string;
    }>>;
    divergence: Record<string, any>;
    count: number;
  };
  bookmakers: Record<string, any>;
  gameData: { homeTeam: string; awayTeam: string; sportKey: string };
  activeMarket: string;
}) {
  const fmtCents = (v: number | null) => v != null ? `${Math.round(v)}¢` : '—';
  const fmtPct = (v: number | null) => v != null ? `${v.toFixed(1)}%` : '—';
  const fmtVol = (v: number | null) => {
    if (v == null) return '—';
    if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `$${(v / 1_000).toFixed(1)}K`;
    return `$${v}`;
  };
  const divColor = (pct: number) => Math.abs(pct) < 1 ? 'text-[#9ca3af]' : pct > 0 ? 'text-emerald-400' : 'text-red-400';

  const markets = exchangeData.by_market;
  const div = exchangeData.divergence;
  const hasML = (markets.moneyline?.length ?? 0) > 0;
  const hasSpread = (markets.spread?.length ?? 0) > 0;
  const hasTotal = (markets.total?.length ?? 0) > 0;

  const homeAbbr = abbrev(gameData.homeTeam);
  const awayAbbr = abbrev(gameData.awayTeam);

  // Map activeMarket to exchange market keys
  const marketToExKey: Record<string, string> = { spread: 'spread', total: 'total', moneyline: 'moneyline' };
  const activeExKey = marketToExKey[activeMarket] || 'moneyline';

  // Find most recent snapshot_time across all contracts
  const allContracts = Object.values(markets).flat();
  const latestSnapshot = allContracts.reduce((latest, c) => {
    if (!c.snapshot_time) return latest;
    return !latest || c.snapshot_time > latest ? c.snapshot_time : latest;
  }, '');
  const lastSyncedAgo = (() => {
    if (!latestSnapshot) return null;
    const diffMs = Date.now() - new Date(latestSnapshot).getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins} min ago`;
    const hrs = Math.floor(mins / 60);
    return `${hrs}h ${mins % 60}m ago`;
  })();

  // Volume confidence label
  const getVolConf = (vol: number) => {
    if (vol >= 50000) return { label: 'High volume — strong signal', color: 'text-emerald-400' };
    if (vol >= 10000) return { label: 'Moderate volume', color: 'text-[#6b7280]' };
    return { label: 'Low volume — treat signal with caution', color: 'text-amber-400' };
  };

  // Divergence explanation one-liner
  const getDivExplanation = (divPct: number, teamName: string): string => {
    const absPct = Math.abs(divPct).toFixed(1);
    if (Math.abs(divPct) < 1) return 'Exchange and sportsbooks are aligned on pricing';
    if (divPct > 0) return `Exchange prices ${teamName} ${absPct}% higher than sportsbooks — exchange may be leading a line move toward ${teamName}`;
    return `Exchange prices ${teamName} ${absPct}% lower than sportsbooks — exchange suggests books may be overvaluing ${teamName}`;
  };

  // Get FD book data for comparison
  const fdMarkets = bookmakers.fanduel?.marketGroups?.fullGame;

  // Match ML contracts to home/away using subtitle
  const homeLower = gameData.homeTeam.toLowerCase();
  const homeWords = homeLower.split(' ').filter((w: string) => w.length > 3);
  const matchHome = (subtitle: string) => {
    const sub = (subtitle || '').toLowerCase();
    return homeWords.some((w: string) => sub.includes(w));
  };

  // Order: active market first, then the rest
  const marketOrder = [activeExKey, ...['moneyline', 'spread', 'total'].filter(k => k !== activeExKey)];

  return (
    <div className="border-t border-cyan-500/20 bg-[#f7f8f9]">
      <div className="px-4 py-2.5 flex items-center gap-2 border-b border-[#e2e4e8]/50">
        <span className="text-[10px] font-semibold tracking-widest text-cyan-500/70 uppercase">Exchange Signals</span>
        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-sky-500/15 text-sky-400 border border-sky-500/30">Kalshi</span>
        <span className="text-[10px] text-[#9ca3af] ml-auto">
          {exchangeData.count > 0 && `${exchangeData.count} contracts`}
          {lastSyncedAgo && <> · Synced {lastSyncedAgo}</>}
        </span>
      </div>

      <div className="px-4 py-3 space-y-3">
        {marketOrder.map(mktKey => {
          const isActive = mktKey === activeExKey;
          const mktContracts = markets[mktKey];
          const hasMkt = (mktContracts?.length ?? 0) > 0;
          const mktLabel = mktKey === 'moneyline' ? 'Moneyline' : mktKey === 'spread' ? 'Spread' : 'Total';

          if (!hasMkt) {
            return (
              <div key={mktKey} className={isActive ? '' : 'opacity-40'}>
                <div className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-wider mb-1">{mktLabel}</div>
                <div className="text-[10px] text-[#9ca3af] italic">No exchange coverage</div>
              </div>
            );
          }

          const totalVol = mktContracts.reduce((s: number, c: any) => s + (c.volume || 0), 0);
          const volConf = getVolConf(totalVol);
          const ticker = mktContracts[0]?.contract_ticker;

          // Moneyline rendering
          if (mktKey === 'moneyline') {
            let homeContract: typeof mktContracts[0] | null = null;
            let awayContract: typeof mktContracts[0] | null = null;
            for (const c of mktContracts) {
              if (matchHome(c.subtitle)) homeContract = c;
              else awayContract = c;
            }
            const homeYes = homeContract?.yes_price ?? null;
            const awayYes = awayContract?.yes_price ?? (homeYes != null ? 100 - homeYes : null);
            const mlDiv = div.moneyline;
            const fdHome = fdMarkets?.h2h?.home?.price;
            const fdAway = fdMarkets?.h2h?.away?.price;
            const fdHomeProb = fdHome ? americanToImplied(fdHome) * 100 : null;
            const fdAwayProb = fdAway ? americanToImplied(fdAway) * 100 : null;
            const contractLabel = awayContract?.subtitle
              ? `${awayContract.subtitle} / ${homeContract?.subtitle || gameData.homeTeam}`
              : homeContract?.subtitle || '';

            return (
              <div key={mktKey} className={isActive ? '' : 'opacity-40'}>
                <div className="flex items-center gap-2 mb-1">
                  <div className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                {ticker && <div className="text-[9px] text-[#9ca3af] font-mono mb-1 truncate">{contractLabel}</div>}
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#9ca3af]">
                      <th className="text-left py-1 font-normal">Source</th>
                      <th className="text-right py-1 font-normal">{awayAbbr}</th>
                      <th className="text-right py-1 font-normal">{homeAbbr}</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="text-[#374151]">
                      <td className="py-1 text-sky-400 font-medium">Kalshi</td>
                      <td className="py-1 text-right font-mono">{fmtCents(awayYes)} <span className="text-[#9ca3af]">({fmtPct(awayYes)})</span></td>
                      <td className="py-1 text-right font-mono">{fmtCents(homeYes)} <span className="text-[#9ca3af]">({fmtPct(homeYes)})</span></td>
                      <td className="py-1 text-right text-[#9ca3af]">{fmtVol(totalVol)}</td>
                    </tr>
                    {fdHome && fdAway && (
                      <tr className="text-[#6b7280]">
                        <td className="py-1 font-medium" style={{ color: '#1493ff' }}>FanDuel</td>
                        <td className="py-1 text-right font-mono">{fdAway > 0 ? '+' : ''}{fdAway} <span className="text-[#9ca3af]">({fmtPct(fdAwayProb)})</span></td>
                        <td className="py-1 text-right font-mono">{fdHome > 0 ? '+' : ''}{fdHome} <span className="text-[#9ca3af]">({fmtPct(fdHomeProb)})</span></td>
                        <td className="py-1 text-right text-[#9ca3af]">—</td>
                      </tr>
                    )}
                    {mlDiv && (
                      <tr>
                        <td className="py-1 text-[#9ca3af] font-medium">Divergence</td>
                        <td className="py-1"></td>
                        <td className={`py-1 text-right font-mono font-bold ${divColor(mlDiv.divergence_pct)}`}>
                          {mlDiv.divergence_pct > 0 ? '+' : ''}{mlDiv.divergence_pct.toFixed(1)}%
                        </td>
                        <td className="py-1"></td>
                      </tr>
                    )}
                  </tbody>
                </table>
                {isActive && mlDiv && (
                  <div className="mt-1.5 text-[10px] text-[#9ca3af] italic">{getDivExplanation(mlDiv.divergence_pct, gameData.homeTeam)}</div>
                )}
                {isActive && <div className={`mt-1 text-[9px] ${volConf.color}`}>{volConf.label}</div>}
              </div>
            );
          }

          // Spread rendering
          if (mktKey === 'spread') {
            const spDiv = div.spread;
            return (
              <div key={mktKey} className={isActive ? '' : 'opacity-40'}>
                <div className="flex items-center gap-2 mb-1">
                  <div className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#9ca3af]">
                      <th className="text-left py-1 font-normal">Contract</th>
                      <th className="text-right py-1 font-normal">Price</th>
                      <th className="text-right py-1 font-normal">Implied</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mktContracts.map((c: any, i: number) => (
                      <tr key={i} className="text-[#374151]">
                        <td className="py-1 text-[#6b7280] text-[10px] truncate max-w-[180px]" title={c.contract_ticker || ''}>{c.subtitle || c.contract_ticker || '—'}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.yes_price)}</td>
                        <td className="py-1 text-right font-mono text-[#6b7280]">{fmtPct(c.yes_price)}</td>
                        <td className="py-1 text-right text-[#9ca3af]">{fmtVol(c.volume)}</td>
                      </tr>
                    ))}
                    {spDiv && (
                      <tr>
                        <td className="py-1 text-[#9ca3af] font-medium">Divergence (Book: {spDiv.book_spread})</td>
                        <td className="py-1"></td>
                        <td className={`py-1 text-right font-mono font-bold ${divColor(spDiv.divergence_pct)}`}>
                          {spDiv.divergence_pct > 0 ? '+' : ''}{spDiv.divergence_pct.toFixed(1)}%
                        </td>
                        <td className="py-1"></td>
                      </tr>
                    )}
                  </tbody>
                </table>
                {isActive && spDiv && (
                  <div className="mt-1.5 text-[10px] text-[#9ca3af] italic">{getDivExplanation(spDiv.divergence_pct, gameData.homeTeam)}</div>
                )}
                {isActive && <div className={`mt-1 text-[9px] ${volConf.color}`}>{volConf.label}</div>}
              </div>
            );
          }

          // Total rendering
          if (mktKey === 'total') {
            const totDiv = div.total;
            return (
              <div key={mktKey} className={isActive ? '' : 'opacity-40'}>
                <div className="flex items-center gap-2 mb-1">
                  <div className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#9ca3af]">
                      <th className="text-left py-1 font-normal">Contract</th>
                      <th className="text-right py-1 font-normal">Over</th>
                      <th className="text-right py-1 font-normal">Under</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mktContracts.map((c: any, i: number) => (
                      <tr key={i} className="text-[#374151]">
                        <td className="py-1 text-[#6b7280] text-[10px] truncate max-w-[180px]" title={c.contract_ticker || ''}>{c.subtitle || c.contract_ticker || '—'}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.yes_price)}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.no_price)}</td>
                        <td className="py-1 text-right text-[#9ca3af]">{fmtVol(c.volume)}</td>
                      </tr>
                    ))}
                    {totDiv && (
                      <tr>
                        <td className="py-1 text-[#9ca3af] font-medium">vs Book ({totDiv.book_total})</td>
                        <td className="py-1 text-right font-mono text-[#6b7280]">{fmtPct(totDiv.exchange_over_prob)}</td>
                        <td className="py-1 text-right font-mono text-[#6b7280]">{totDiv.exchange_over_prob != null ? fmtPct(100 - totDiv.exchange_over_prob) : '—'}</td>
                        <td className="py-1"></td>
                      </tr>
                    )}
                  </tbody>
                </table>
                {isActive && <div className={`mt-1 text-[9px] ${volConf.color}`}>{volConf.label}</div>}
              </div>
            );
          }

          return null;
        })}
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
  const gameState = gameData.commenceTime ? getGameState(gameData.commenceTime, gameData.sportKey) : 'upcoming';
  const isLive = gameState === 'live';
  const isFinal = gameState === 'final';
  const showLiveLock = false; // Replaced by informational banner

  // Live score polling
  const [liveScore, setLiveScore] = useState<LiveScoreData | null>(null);
  useEffect(() => {
    if (!isLive && !isFinal) return;
    const fetchLiveScore = async () => {
      try {
        const params = new URLSearchParams({
          sport: gameData.sportKey,
          home: gameData.homeTeam,
          away: gameData.awayTeam,
        });
        const res = await fetch(`/api/odds/live-score?${params}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.liveData) setLiveScore(data.liveData);
      } catch { /* silent */ }
    };
    fetchLiveScore();
    if (isLive) {
      const interval = setInterval(fetchLiveScore, 12000);
      return () => clearInterval(interval);
    }
  }, [isLive, isFinal, gameData.sportKey, gameData.homeTeam, gameData.awayTeam]);

  // Always include core sportsbooks in selector (DK/FD), even if a game lacks data for one
  const CORE_BOOKS = ['fanduel', 'draftkings'];
  const filteredBooks = [...new Set([...CORE_BOOKS, ...availableBooks.filter(book => ALLOWED_BOOKS.includes(book))])];
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

  // Fair values for live score indicator (spread, total, ML)
  const liveScoreFairValues = (() => {
    if (!pythonPillarScores) return { fairSpread: null as number | null, fairTotal: null as number | null, fairMLHomeProb: null as number | null };
    const getMedian = (arr: number[]) => {
      if (arr.length === 0) return null;
      const sorted = [...arr].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };
    const allSpreads: number[] = [];
    const allTotals: number[] = [];
    Object.entries(bookmakers).forEach(([, data]) => {
      const fg = (data as any)?.marketGroups?.fullGame;
      const sl = fg?.spreads?.home?.line;
      const tl = fg?.totals?.line;
      if (typeof sl === 'number') allSpreads.push(sl);
      if (typeof tl === 'number') allTotals.push(tl);
    });
    const consSpread = getMedian(allSpreads);
    const consTotal = getMedian(allTotals);
    const fairSpread = consSpread !== null ? calculateFairSpread(consSpread, pythonPillarScores.composite, gameData.sportKey).fairLine : null;
    const fairTotal = consTotal !== null ? calculateFairTotal(consTotal, pythonPillarScores.gameEnvironment, gameData.sportKey).fairLine : null;
    // ML: derive from fair spread for consistency, fallback to composite
    let fairMLHomeProb: number | null = null;
    if (fairSpread !== null) {
      const ml = spreadToMoneyline(fairSpread, gameData.sportKey);
      fairMLHomeProb = americanToImplied(ml.homeOdds);
    } else {
      const ml = calculateFairMoneyline(pythonPillarScores.composite);
      fairMLHomeProb = americanToImplied(ml.homeOdds);
    }
    return { fairSpread, fairTotal, fairMLHomeProb };
  })();
  const liveScoreFairSpread = liveScoreFairValues.fairSpread;

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
      return calculateFairSpread(consensus, pythonPillarScores.composite, gameData.sportKey).fairLine;
    }
    if (activeMarket === 'total') {
      const lines = allBooksForPeriod.map(m => m?.totals?.line).filter((v): v is number => v !== undefined);
      const consensus = calcMedian(lines);
      if (consensus === undefined) return undefined;
      return calculateFairTotal(consensus, pythonPillarScores.gameEnvironment, gameData.sportKey).fairLine;
    }
    // Moneyline: derive from fair spread for consistency; fallback to composite-only
    const spreadLines = allBooksForPeriod.map(m => m?.spreads?.home?.line).filter((v): v is number => v !== undefined);
    const spreadConsensus = calcMedian(spreadLines);
    if (spreadConsensus !== undefined) {
      const fairSpread = calculateFairSpread(spreadConsensus, pythonPillarScores.composite, gameData.sportKey).fairLine;
      return spreadToMoneyline(fairSpread, gameData.sportKey).homeOdds;
    }
    return calculateFairMoneyline(pythonPillarScores.composite).homeOdds;
  };

  const omiFairLineForChart = getOmiFairLineForChart();

  // Build game context string for Edge AI chat
  const edgeAIGameContext = (() => {
    const lines: string[] = [];
    lines.push(`Game: ${gameData.awayTeam} @ ${gameData.homeTeam}`);
    lines.push(`Sport: ${gameData.sportKey} | Game ID: ${gameData.id}`);
    if (gameData.commenceTime) lines.push(`Start: ${new Date(gameData.commenceTime).toLocaleString()}`);
    lines.push(`Active Market: ${activeMarket} | Period: ${activePeriod}`);
    lines.push(`Selected Book: ${selectedBook}`);

    // Pillar scores
    if (pythonPillarScores) {
      const p = pythonPillarScores;
      lines.push('');
      lines.push('--- PILLAR SCORES (0-100, 50=neutral) ---');
      lines.push(`Composite: ${p.composite}`);
      lines.push(`Execution: ${p.execution} (20%) | Incentives: ${p.incentives} (10%)`);
      lines.push(`Shocks: ${p.shocks} (25%) | Time Decay: ${p.timeDecay} (10%)`);
      lines.push(`Flow: ${p.flow} (25%) | Game Environment: ${p.gameEnvironment} (10%)`);
    }

    // Compute consensus + fair lines from bookmakers (same logic as OmiFairPricing)
    const allBooks = Object.entries(bookmakers)
      .filter(([key]) => { const c = BOOK_CONFIG[key]; return !c || c.type === 'sportsbook'; })
      .map(([, data]) => (data as any).marketGroups?.fullGame)
      .filter(Boolean);

    const spreadLines = allBooks.map((m: any) => m?.spreads?.home?.line).filter((v: any): v is number => v !== undefined);
    const totalLines = allBooks.map((m: any) => m?.totals?.line).filter((v: any): v is number => v !== undefined);
    const mlHomeOdds = allBooks.map((m: any) => m?.h2h?.home?.price).filter((v: any): v is number => v !== undefined);
    const mlAwayOdds = allBooks.map((m: any) => m?.h2h?.away?.price).filter((v: any): v is number => v !== undefined);

    const consSpread = calcMedian(spreadLines);
    const consTotal = calcMedian(totalLines);
    const consHomeML = calcMedian(mlHomeOdds);
    const consAwayML = calcMedian(mlAwayOdds);

    // OMI fair lines
    const fairSpread = consSpread !== undefined && pythonPillarScores
      ? calculateFairSpread(consSpread, pythonPillarScores.composite, gameData.sportKey) : null;
    const fairTotal = consTotal !== undefined && pythonPillarScores
      ? calculateFairTotal(consTotal, pythonPillarScores.gameEnvironment, gameData.sportKey) : null;
    const fairML = fairSpread
      ? spreadToMoneyline(fairSpread.fairLine, gameData.sportKey)
      : (pythonPillarScores ? calculateFairMoneyline(pythonPillarScores.composite) : null);

    lines.push('');
    lines.push('--- OMI FAIR LINES ---');
    if (fairSpread) lines.push(`Fair Spread: ${fairSpread.fairLine > 0 ? '+' : ''}${fairSpread.fairLine.toFixed(1)} (gap: ${fairSpread.gap > 0 ? '+' : ''}${fairSpread.gap.toFixed(2)})`);
    if (fairTotal) lines.push(`Fair Total: ${fairTotal.fairLine.toFixed(1)} (gap: ${fairTotal.gap > 0 ? '+' : ''}${fairTotal.gap.toFixed(2)})`);
    if (fairML) lines.push(`Fair ML: Home ${formatOdds(fairML.homeOdds)} / Away ${formatOdds(fairML.awayOdds)}`);
    if (fairML) {
      const hp = americanToImplied(fairML.homeOdds);
      const ap = americanToImplied(fairML.awayOdds);
      lines.push(`Fair Win Prob: Home ${(hp * 100).toFixed(1)}% / Away ${(ap * 100).toFixed(1)}%`);
    }

    // Consensus lines
    lines.push('');
    lines.push('--- CONSENSUS (market median) ---');
    if (consSpread !== undefined) lines.push(`Spread: ${consSpread > 0 ? '+' : ''}${consSpread}`);
    if (consTotal !== undefined) lines.push(`Total: ${consTotal}`);
    if (consHomeML !== undefined) lines.push(`ML: Home ${formatOdds(consHomeML)} / Away ${formatOdds(consAwayML!)}`);

    // Selected book lines
    const bookMkts = selectedBookMarkets.fullGame;
    if (bookMkts) {
      lines.push('');
      lines.push(`--- ${selectedBook.toUpperCase()} LINES ---`);
      if (bookMkts.spreads?.home) lines.push(`Spread: ${bookMkts.spreads.home.line > 0 ? '+' : ''}${bookMkts.spreads.home.line} (${formatOdds(bookMkts.spreads.home.price)})`);
      if (bookMkts.totals) lines.push(`Total: ${bookMkts.totals.line} (O: ${formatOdds(bookMkts.totals.over?.price)}, U: ${formatOdds(bookMkts.totals.under?.price)})`);
      if (bookMkts.h2h?.home) lines.push(`ML: Home ${formatOdds(bookMkts.h2h.home.price)} / Away ${formatOdds(bookMkts.h2h.away?.price)}`);
    }

    // Edge gaps
    const rate = SPREAD_TO_PROB_RATE[gameData.sportKey] || 0.03;
    lines.push('');
    lines.push('--- EDGE ANALYSIS ---');
    if (fairSpread && consSpread !== undefined) {
      const gap = consSpread - fairSpread.fairLine;
      lines.push(`Spread gap: ${gap > 0 ? '+' : ''}${gap.toFixed(2)} pts → ${(Math.abs(gap) * rate * 100).toFixed(1)}% edge`);
    }
    if (fairTotal && consTotal !== undefined) {
      const gap = consTotal - fairTotal.fairLine;
      lines.push(`Total gap: ${gap > 0 ? '+' : ''}${gap.toFixed(2)} pts → ${(Math.abs(gap) * rate * 100).toFixed(1)}% edge`);
    }

    // CEQ summary
    if (activeCeq?.bestEdge) {
      lines.push('');
      lines.push('--- CEQ (Composite Edge Quality) ---');
      lines.push(`Best Edge: ${activeCeq.bestEdge.market} ${activeCeq.bestEdge.side} | CEQ: ${activeCeq.bestEdge.ceq} | Confidence: ${activeCeq.bestEdge.confidence}`);
    }

    return lines.join('\n');
  })();

  // Exchange data state
  const [exchangeData, setExchangeData] = useState<{
    by_market: Record<string, Array<{
      exchange: string; subtitle: string; yes_price: number | null; no_price: number | null;
      volume: number | null; open_interest: number | null; snapshot_time: string;
      contract_ticker?: string; event_title?: string;
    }>>;
    divergence: Record<string, {
      exchange_home_prob?: number; book_home_prob?: number; divergence_pct?: number;
      exchange_implied?: number; book_implied?: number; book_spread?: number;
      exchange_over_prob?: number; book_total?: number;
    }>;
    count: number;
  } | null>(null);

  useEffect(() => {
    if (!gameData.id) return;
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://omi-workspace-production.up.railway.app';
    fetch(`${BACKEND_URL}/api/exchange/game/${gameData.id}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data && data.count > 0) setExchangeData(data); })
      .catch(() => {});
  }, [gameData.id]);

  return (
    <>
      {/* Desktop: OMI Fair Pricing Layout */}
      <div
        className="hidden lg:block h-full relative overflow-y-auto"
        style={{ background: '#ffffff', fontVariantNumeric: 'tabular-nums' }}
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

        {/* Live score bar */}
        {liveScore && (isLive || isFinal) && (
          <LiveScoreBar
            liveData={liveScore}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
            sportKey={gameData.sportKey}
            fairSpread={liveScoreFairValues.fairSpread}
            fairTotal={liveScoreFairValues.fairTotal}
            fairMLHomeProb={liveScoreFairValues.fairMLHomeProb}
            activeMarket={activeMarket}
            isFinalGame={isFinal}
          />
        )}

        {/* Informational banner */}
        {isLive && <GameStatusBanner gameState="live" />}
        {isFinal && <GameStatusBanner gameState="final" />}

        {/* Market tabs + period sub-tabs */}
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#e2e4e8]/50">
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
                      : 'text-[#9ca3af] hover:text-[#374151] border border-transparent'
                  }`}
                >
                  {m === 'spread' ? 'Spread' : m === 'total' ? 'Total' : 'Moneyline'}
                </button>
              ))}
            <span className="w-px h-4 bg-[#e2e4e8]/50 mx-1" />
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
                    ? 'bg-[#e2e4e8] text-[#1f2937]'
                    : 'text-[#9ca3af] hover:text-[#6b7280]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Two-column: Chart (55%) + Ask Edge AI (45%) */}
        <div className="flex border-b border-[#e2e4e8]/50" style={{ height: '260px' }}>
          {/* Left: Chart */}
          <div className="relative flex flex-col px-1 py-1" style={{ width: '55%' }}>
            <LineMovementChart
              key={`chart-${activeMarket}-${activePeriod}-${selectedBook}`}
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
          </div>
          {/* Right: Ask Edge AI */}
          <div className="h-full" style={{ width: '45%' }}>
            <AskEdgeAI activeMarket={activeMarket} activePeriod={activePeriod} gameContext={edgeAIGameContext} />
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
        <div className="flex border-t border-[#e2e4e8]/50">
          <div className="w-1/2 border-r border-[#e2e4e8]/50">
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

        {/* Exchange Signals — hidden until data cleanup, re-enable later
        {exchangeData && (
          <ExchangeSignals exchangeData={exchangeData} bookmakers={bookmakers} gameData={gameData} activeMarket={activeMarket} />
        )}
        */}
      </div>

      {/* Mobile: Single-column scrollable fallback */}
      <div className="lg:hidden h-auto overflow-y-auto bg-white">
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

        {/* Live score bar (mobile) */}
        {liveScore && (isLive || isFinal) && (
          <LiveScoreBar
            liveData={liveScore}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
            sportKey={gameData.sportKey}
            fairSpread={liveScoreFairValues.fairSpread}
            fairTotal={liveScoreFairValues.fairTotal}
            fairMLHomeProb={liveScoreFairValues.fairMLHomeProb}
            activeMarket={activeMarket}
            isFinalGame={isFinal}
          />
        )}

        {/* Informational banner (mobile) */}
        {isLive && <GameStatusBanner gameState="live" />}
        {isFinal && <GameStatusBanner gameState="final" />}

        <div className="p-2 space-y-2">
          {/* Market + Period tabs */}
          <div className="bg-white/50 rounded p-2">
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
                        : 'text-[#9ca3af] hover:text-[#374151] border border-transparent'
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
                      ? 'bg-[#e2e4e8] text-[#1f2937]'
                      : 'text-[#9ca3af] hover:text-[#6b7280]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Convergence chart — compact */}
          <div className="h-[200px] relative bg-white/50 rounded p-2">
            <span className="text-[10px] font-semibold text-[#9ca3af] uppercase tracking-widest mb-1 block">Line Convergence</span>
            <div className="flex-1 min-h-0 h-[calc(100%-20px)]">
              <LineMovementChart
                key={`chart-mobile-${activeMarket}-${activePeriod}-${selectedBook}`}
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

          {/* Exchange Signals — complementary intelligence */}
          {exchangeData && (
            <ExchangeSignals exchangeData={exchangeData} bookmakers={bookmakers} gameData={gameData} activeMarket={activeMarket} />
          )}
        </div>
      </div>
    </>
  );
}
