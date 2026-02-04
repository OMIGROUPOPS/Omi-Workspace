'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread, calculateTwoWayEV, formatEV, getEVColor, getEVBgClass } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive, getGameState } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, PillarResult, PillarVariable, CEQConfidence } from '@/lib/edge/engine/edgescout';
import { GameEdgesPanel } from './GameEdgesPanel';
import { PythonPillarBreakdown } from './PythonPillarBreakdown';

// Sportsbooks and Prediction Exchanges
const BOOK_CONFIG: Record<string, { name: string; color: string; type: 'sportsbook' | 'exchange' }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff', type: 'sportsbook' },
  'draftkings': { name: 'DraftKings', color: '#53d337', type: 'sportsbook' },
  'kalshi': { name: 'Kalshi', color: '#0ea5e9', type: 'exchange' },
  'polymarket': { name: 'Polymarket', color: '#8b5cf6', type: 'exchange' },
};

// Allowed books for dropdown (sportsbooks + exchanges)
const ALLOWED_BOOKS = ['fanduel', 'draftkings', 'kalshi', 'polymarket'];

function getEdgeColor(delta: number): string {
  return delta >= 0 ? 'text-emerald-400' : 'text-red-400';
}

function getEdgeBg(delta: number): string {
  return delta >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30';
}

// Simple price movement display: shows "opened → current" or delta
function PriceMovement({ openPrice, currentPrice, compact = false }: { openPrice?: number; currentPrice?: number; compact?: boolean }) {
  if (openPrice === undefined || currentPrice === undefined) return null;

  const delta = currentPrice - openPrice;
  if (delta === 0) return <span className="text-xs text-zinc-500">—</span>;

  const deltaColor = delta > 0 ? 'text-emerald-400' : 'text-red-400';
  const deltaSign = delta > 0 ? '+' : '';

  if (compact) {
    // Just show the delta: "+4" or "-6"
    return (
      <span className={`text-xs font-medium ${deltaColor}`}>
        {deltaSign}{delta}
      </span>
    );
  }

  // Full display: "-110 → -106"
  return (
    <span className="text-xs text-zinc-400">
      {formatOdds(openPrice)} → <span className={`font-medium ${deltaColor}`}>{formatOdds(currentPrice)}</span>
    </span>
  );
}

type ChartViewMode = 'line' | 'price';

type ChartSelection = {
  type: 'market';
  market: 'spread' | 'total' | 'moneyline';
  period: string;
  label: string;
  line?: number;
  homeLine?: number;  // For spreads: home team's line
  awayLine?: number;  // For spreads: away team's line
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
  awayTeam?: string;
  viewMode: ChartViewMode;
  onViewModeChange: (mode: ChartViewMode) => void;
  commenceTime?: string;
  sportKey?: string;
}

// Time range options for chart (30M only visible when game is live)
type TimeRange = '30M' | '1H' | '3H' | '6H' | '24H' | 'ALL';

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam, awayTeam, viewMode, onViewModeChange, commenceTime, sportKey }: LineMovementChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; timestamp: Date; index: number } | null>(null);
  // Track which side to show: 'home'/'away'/'draw' for spreads/ML, 'over'/'under' for totals
  const [trackingSide, setTrackingSide] = useState<'home' | 'away' | 'over' | 'under' | 'draw'>('home');
  const isSoccer = sportKey?.includes('soccer') ?? false;
  // Time range for chart - auto-select based on game state
  const [timeRange, setTimeRange] = useState<TimeRange>('ALL');

  const isProp = selection.type === 'prop';
  const marketType = selection.type === 'market' ? selection.market : 'line';

  // For spreads, use the correct line based on trackingSide
  const getDisplayLine = () => {
    if (selection.type === 'prop') return selection.line;
    if (marketType === 'spread') {
      const homeLine = selection.homeLine;
      const awayLine = selection.awayLine;
      return trackingSide === 'away' ? awayLine : homeLine;
    }
    return selection.line;
  };
  const displayLine = getDisplayLine();
  const baseValue = displayLine ?? (selection.type === 'market' ? selection.price : 0) ?? 0;

  // Parse game start time for live cutoff indicator
  // Using shared game-state utility for consistent state detection across app
  const gameStartTime = commenceTime ? new Date(commenceTime) : null;
  const isGameLive = commenceTime ? checkGameLive(commenceTime) : false;

  // Keep ALL as default for all games to show full historical data
  // Users can manually select shorter time ranges if desired

  // For price view, determine which side to show
  const isShowingPrice = viewMode === 'price';
  // Moneyline always shows price (it IS the price), so force line mode display
  const effectiveViewMode = marketType === 'moneyline' ? 'line' : viewMode;

  // Determine which outcome to filter by based on trackingSide
  const getOutcomeFilter = () => {
    if (marketType === 'total') {
      return trackingSide === 'under' ? 'Under' : 'Over';
    }
    // For moneyline with draw option (soccer)
    if (trackingSide === 'draw') return 'Draw';
    // For spreads/moneyline, use team names
    if (trackingSide === 'away' && awayTeam) return awayTeam;
    return homeTeam;
  };

  // Filter line history by selected book AND outcome side
  // Uses flexible matching for team names (handles "Kansas City Chiefs" vs "Chiefs" mismatches)
  const filteredHistory = (lineHistory || []).filter(snapshot => {
    const bookMatch = snapshot.book_key === selectedBook || snapshot.book === selectedBook;
    if (!bookMatch) return false;

    const targetOutcome = getOutcomeFilter();

    // Handle missing outcome_type (from line_snapshots which only stores home/over side)
    if (!snapshot.outcome_type) {
      // Spreads: line_snapshots stores home line, can derive away by inverting
      // Include for BOTH sides, transformation happens in value mapping
      if (marketType === 'spread') {
        return true; // Include for both home and away
      }
      // Totals: line_snapshots stores the total line (same for over/under)
      // Include for BOTH sides
      if (marketType === 'total') {
        return true; // Include for both over and under
      }
      // ML: line_snapshots only stores home odds, can't derive away
      // Only include for home side
      if (marketType === 'moneyline') {
        return trackingSide === 'home';
      }
      return true; // Unknown market, keep it
    }

    if (!targetOutcome) return true;

    const outcomeType = snapshot.outcome_type.toLowerCase();
    const target = targetOutcome.toLowerCase();

    // For Over/Under, use exact match
    if (target === 'over' || target === 'under') {
      return outcomeType === target;
    }

    // Handle "home"/"away" outcome_type from line_snapshots
    // Match against trackingSide directly
    if (outcomeType === 'home' || outcomeType === 'away') {
      return outcomeType === trackingSide;
    }

    // For team names (from odds_snapshots), use flexible matching:
    // - Exact match
    // - One contains the other (handles "Chiefs" vs "Kansas City Chiefs")
    // - Last word match (e.g., "Chiefs" matches "Kansas City Chiefs")
    if (outcomeType === target) return true;
    if (outcomeType.includes(target) || target.includes(outcomeType)) return true;

    // Match last word (team nickname) - most reliable for sports team matching
    const outcomeWords = outcomeType.split(/\s+/);
    const targetWords = target.split(/\s+/);
    const outcomeLast = outcomeWords[outcomeWords.length - 1];
    const targetLast = targetWords[targetWords.length - 1];
    if (outcomeLast === targetLast) return true;

    return false;
  });

  const hasRealData = filteredHistory.length > 0;

  let data: { timestamp: Date; value: number }[] = [];

  if (hasRealData) {
    // Use ONLY real data filtered by book - works for both main markets and props

    data = filteredHistory.map(snapshot => {
      let value: number;

      if (effectiveViewMode === 'price') {
        // Price view always uses odds
        value = snapshot.odds;
      } else if (isProp) {
        value = snapshot.line;
      } else if (marketType === 'moneyline') {
        // Moneyline has no line, always show odds
        value = snapshot.odds;
      } else if (marketType === 'spread') {
        // Spread line handling:
        // - odds_snapshots has outcome_type and correct line per side (home=+4.5, away=-4.5)
        // - line_snapshots has NO outcome_type and only stores home side
        if (snapshot.outcome_type) {
          // Data from odds_snapshots - line is already correct for the filtered side
          value = snapshot.line;
        } else {
          // Data from line_snapshots - only has home side, invert for away
          value = trackingSide === 'away' ? (snapshot.line * -1) : snapshot.line;
        }
      } else {
        // Totals: same line for Over and Under (e.g., 215.5)
        value = snapshot.line;
      }

      return {
        timestamp: new Date(snapshot.snapshot_time),
        value
      };
    }).filter(d => d.value !== null && d.value !== undefined);

    // Sort by timestamp
    data.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

    // Apply time range filter - strict filtering, no silent fallback
    if (timeRange !== 'ALL' && data.length > 0) {
      const now = new Date();
      // Map time ranges to hours (30M = 0.5 hours)
      const hoursMap: Record<TimeRange, number> = { '30M': 0.5, '1H': 1, '3H': 3, '6H': 6, '24H': 24, 'ALL': 0 };
      const cutoffTime = new Date(now.getTime() - hoursMap[timeRange] * 60 * 60 * 1000);
      const filteredByTime = data.filter(d => d.timestamp >= cutoffTime);
      // Always use filtered data - show empty state if no data in range
      data = filteredByTime;
    }
  }

  // Determine which side we're tracking for clear labeling
  const getTrackingLabel = () => {
    if (isProp) return selection.type === 'prop' ? selection.player : 'Prop';
    if (marketType === 'total') {
      return trackingSide === 'under' ? 'Under' : 'Over';
    }
    if (marketType === 'moneyline') {
      const team = trackingSide === 'away' ? awayTeam : homeTeam;
      return team ? `${team} ML` : (trackingSide === 'away' ? 'Away ML' : 'Home ML');
    }
    if (marketType === 'spread') {
      const team = trackingSide === 'away' ? awayTeam : homeTeam;
      return team || (trackingSide === 'away' ? 'Away' : 'Home');
    }
    return 'Line';
  };
  const trackingLabel = getTrackingLabel();

  // Get the opposite side label for toggle
  const getOppositeSideLabel = () => {
    if (isProp) return null;
    if (marketType === 'total') {
      return trackingSide === 'under' ? 'Over' : 'Under';
    }
    const oppositeTeam = trackingSide === 'away' ? homeTeam : awayTeam;
    return oppositeTeam || (trackingSide === 'away' ? 'Home' : 'Away');
  };
  const oppositeSideLabel = getOppositeSideLabel();

  // Toggle to the other side
  const toggleSide = () => {
    if (marketType === 'total') {
      setTrackingSide(trackingSide === 'over' ? 'under' : 'over');
    } else {
      setTrackingSide(trackingSide === 'home' ? 'away' : 'home');
    }
  };

  // Chart title based on view mode - include line context for price view on spreads/totals
  const getChartTitle = () => {
    if (effectiveViewMode !== 'price') return selection.label;

    // For price view, show the line value for context (use displayLine for correct side)
    if (selection.type === 'market' && displayLine !== undefined) {
      if (marketType === 'spread') {
        const lineStr = displayLine > 0 ? `+${displayLine}` : displayLine.toString();
        return `${selection.label} Price @ ${lineStr}`;
      }
      if (marketType === 'total') {
        return `${selection.label} Price @ ${displayLine}`;
      }
    }
    return `${selection.label} - Price`;
  };
  const chartTitle = getChartTitle();

  // Time range selector component - 30M only visible when game is live
  const TimeRangeSelector = () => {
    const ranges: TimeRange[] = isGameLive
      ? ['30M', '1H', '3H', '6H', '24H', 'ALL']
      : ['1H', '3H', '6H', '24H', 'ALL'];

    return (
      <div className="flex rounded overflow-hidden border border-zinc-700/50">
        {ranges.map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className={`px-2 py-0.5 text-[10px] font-medium transition-colors ${
              timeRange === range
                ? 'bg-zinc-600 text-zinc-100'
                : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {range}
          </button>
        ))}
      </div>
    );
  };

  // Check if we have any data at all (for determining empty state message)
  const hasAnyData = hasRealData && filteredHistory.length > 0;
  const isFilteredEmpty = hasAnyData && data.length === 0;

  // If no data, show appropriate message
  if (data.length === 0) {
    return (
      <div className="bg-zinc-900/80 border border-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-zinc-100">{chartTitle}</h3>
          <div className="flex items-center gap-2">
            <TimeRangeSelector />
            {marketType !== 'moneyline' && (
              <div className="flex rounded overflow-hidden border border-zinc-700/50">
                <button
                  onClick={() => onViewModeChange('line')}
                  className={`px-2 py-0.5 text-[10px] font-medium transition-colors ${viewMode === 'line' ? 'bg-emerald-500 text-white' : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300'}`}
                >
                  Line
                </button>
                <button
                  onClick={() => onViewModeChange('price')}
                  className={`px-2 py-0.5 text-[10px] font-medium transition-colors ${viewMode === 'price' ? 'bg-amber-500 text-white' : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300'}`}
                >
                  Price
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center justify-center h-32 text-zinc-500 text-sm">
          <div className="text-center">
            {isFilteredEmpty ? (
              <>
                <p>No data in the last {timeRange === '30M' ? '30 minutes' : timeRange === '1H' ? 'hour' : timeRange}</p>
                <button
                  onClick={() => setTimeRange('ALL')}
                  className="text-xs text-emerald-400 hover:text-emerald-300 mt-2"
                >
                  View all available data
                </button>
              </>
            ) : (
              <>
                <p>No snapshots yet for {BOOK_CONFIG[selectedBook]?.name || selectedBook}</p>
                <p className="text-xs text-zinc-600 mt-1">Data syncs every 15 minutes</p>
              </>
            )}
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
  // Smaller padding = more dramatic visual movement
  const padding = range * 0.1;

  // Taller chart for more granular Y-axis labels
  const width = 400, height = 180;
  const paddingLeft = 45, paddingRight = 10, paddingTop = 12, paddingBottom = 22;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // For both line and price charts, higher values at TOP (standard)
  // For price charts: less negative = better = higher on chart
  // This way line going UP = price getting better (less juice) = good
  const chartPoints = data.map((d, i) => {
    const normalizedY = (d.value - minVal + padding) / (range + 2 * padding);
    // Standard for all: higher value = top of chart
    const y = paddingTop + chartHeight - normalizedY * chartHeight;
    return {
      x: paddingLeft + (i / Math.max(data.length - 1, 1)) * chartWidth,
      y,
      value: d.value,
      timestamp: d.timestamp,
      index: i
    };
  });

  const pathD = chartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  const formatValue = (val: number) => {
    // Price view always formats as odds
    if (effectiveViewMode === 'price') {
      return val > 0 ? `+${val}` : val.toString();
    }
    if (isProp) return val.toString();
    if (marketType === 'moneyline' || marketType === 'spread') return val > 0 ? `+${val}` : val.toString();
    return val.toString();
  };

  const movementColor = movement > 0 ? 'text-emerald-400' : movement < 0 ? 'text-red-400' : 'text-zinc-400';

  // Y-axis labels: Generate granular labels
  // For betting lines (spreads, totals, props), ALWAYS use 0.5 or 1 point steps - every half point matters!
  const isPrice = effectiveViewMode === 'price';

  // Round to nearest step
  const roundToStep = (val: number, step: number) => Math.round(val / step) * step;

  // Generate Y-axis labels with proper granularity for betting
  // Dynamic increments based on time range for line charts:
  // 30M/1H: 0.5 points, 3H/6H: 1 point, 24H: 2 points, ALL: auto-scale
  const generateYLabels = () => {
    const labels: { value: number; y: number }[] = [];

    // Calculate the visual range bounds
    const visualMin = minVal - padding;
    const visualMax = maxVal + padding;
    const visualRange = visualMax - visualMin;

    // Determine label step based on view mode and time range
    let labelStep: number;
    if (isPrice || marketType === 'moneyline') {
      // For prices: scale based on range
      if (range <= 8) labelStep = 2;
      else if (range <= 16) labelStep = 4;
      else labelStep = 5;
    } else {
      // For lines (spreads, totals, props): dynamic based on time range
      // Shorter time ranges = more granular labels
      switch (timeRange) {
        case '30M':
        case '1H':
          labelStep = 0.5; // Most granular for live action
          break;
        case '3H':
        case '6H':
          labelStep = 1;
          break;
        case '24H':
          labelStep = 2;
          break;
        case 'ALL':
        default:
          // Auto-scale based on data range
          if (range <= 5) labelStep = 0.5;
          else if (range <= 12) labelStep = 1;
          else if (range <= 25) labelStep = 2;
          else labelStep = 5;
          break;
      }
    }

    // Start from a nice round number below min
    const startValue = roundToStep(Math.floor(visualMin), labelStep);
    const endValue = roundToStep(Math.ceil(visualMax), labelStep) + labelStep;

    // Generate labels at each step
    for (let val = startValue; val <= endValue; val += labelStep) {
      // Calculate Y position (higher values at top)
      const normalizedY = (val - visualMin) / visualRange;
      const y = paddingTop + chartHeight - normalizedY * chartHeight;

      // Only include if within chart bounds
      if (y >= paddingTop - 2 && y <= paddingTop + chartHeight + 2) {
        labels.push({ value: val, y });
      }
    }

    // For line charts (spreads/totals), allow up to 12 labels for granularity
    // For price charts, limit to 8
    const maxLabels = isPrice ? 8 : 12;

    if (labels.length > maxLabels) {
      // Thin out labels but keep granular (every 2nd label)
      const keepEvery = Math.ceil(labels.length / maxLabels);
      return labels.filter((_, i) => i % keepEvery === 0);
    }

    return labels;
  };

  const yLabels = generateYLabels();
  const xLabels = data.length > 0 ? [0, Math.floor(data.length / 2), data.length - 1].map(i => ({
    x: chartPoints[i]?.x || 0,
    label: data[i]?.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) || ''
  })) : [];

  // Calculate game start cutoff position if game has started and we have data
  let gameStartX: number | null = null;
  if (gameStartTime && data.length >= 2) {
    const startTs = gameStartTime.getTime();
    const firstTs = data[0].timestamp.getTime();
    const lastTs = data[data.length - 1].timestamp.getTime();
    // Only show if game start is within the data range
    if (startTs >= firstTs && startTs <= lastTs) {
      const ratio = (startTs - firstTs) / (lastTs - firstTs);
      gameStartX = paddingLeft + ratio * chartWidth;
    }
  }

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

  // Chart colors based on view mode
  const chartColor = effectiveViewMode === 'price' ? '#f59e0b' : (isProp ? '#3b82f6' : '#10b981');
  const chartColorLight = effectiveViewMode === 'price' ? '#fbbf24' : (isProp ? '#60a5fa' : '#34d399');
  const gradientId = `chart-grad-${gameId}-${effectiveViewMode}`;

  return (
    <div className="bg-zinc-900/80 border border-zinc-800/50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-zinc-100">{chartTitle}</h3>
        <div className="flex items-center gap-2">
          <TimeRangeSelector />
          {marketType !== 'moneyline' && (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              <button
                onClick={() => onViewModeChange('line')}
                className={`px-2 py-0.5 text-[10px] font-medium transition-colors ${viewMode === 'line' ? 'bg-emerald-500 text-white' : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300'}`}
              >
                Line
              </button>
              <button
                onClick={() => onViewModeChange('price')}
                className={`px-2 py-0.5 text-[10px] font-medium transition-colors ${viewMode === 'price' ? 'bg-amber-500 text-white' : 'bg-zinc-800/50 text-zinc-500 hover:text-zinc-300'}`}
              >
                Price
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Compact tracking + movement row */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-zinc-800/50">
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wide">Tracking</span>
          {!isProp && oppositeSideLabel ? (
            <div className="flex rounded overflow-hidden border border-zinc-700/50">
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('over') : setTrackingSide('home')}
                className={`px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                  (marketType === 'total' ? trackingSide === 'over' : trackingSide === 'home')
                    ? 'bg-zinc-700 text-zinc-100'
                    : 'bg-zinc-800/30 text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'O' : (homeTeam?.slice(0, 3).toUpperCase() || 'HM')}
              </button>
              {/* Draw button for soccer moneyline */}
              {isSoccer && marketType === 'moneyline' && (
                <button
                  onClick={() => setTrackingSide('draw')}
                  className={`px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                    trackingSide === 'draw'
                      ? 'bg-zinc-700 text-zinc-100'
                      : 'bg-zinc-800/30 text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  DRW
                </button>
              )}
              <button
                onClick={() => marketType === 'total' ? setTrackingSide('under') : setTrackingSide('away')}
                className={`px-1.5 py-0.5 text-[10px] font-medium transition-colors ${
                  (marketType === 'total' ? trackingSide === 'under' : trackingSide === 'away')
                    ? 'bg-zinc-700 text-zinc-100'
                    : 'bg-zinc-800/30 text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {marketType === 'total' ? 'U' : (awayTeam?.slice(0, 3).toUpperCase() || 'AW')}
              </button>
            </div>
          ) : (
            <span className="px-1.5 py-0.5 bg-zinc-800/50 rounded text-[10px] font-medium text-zinc-300">{trackingLabel}</span>
          )}
          {/* Show line value context when viewing price chart for spreads/totals */}
          {effectiveViewMode === 'price' && selection.type === 'market' && displayLine !== undefined && (marketType === 'spread' || marketType === 'total') && (
            <span className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/30 rounded text-[10px] font-medium text-amber-400">
              @ {marketType === 'spread' ? (displayLine > 0 ? `+${displayLine}` : displayLine) : displayLine}
            </span>
          )}
        </div>
        {/* Movement summary */}
        <div className="flex items-center gap-1.5">
          <span className="text-zinc-400 text-xs">{formatValue(openValue)}</span>
          <span className="text-zinc-600 text-[10px]">→</span>
          <span className="text-zinc-100 text-xs font-semibold">{formatValue(currentValue)}</span>
          <span className={`text-[10px] font-medium ${movementColor}`}>
            {movement > 0 ? '+' : ''}{effectiveViewMode === 'price' ? Math.round(movement) : movement.toFixed(1)}
          </span>
        </div>
      </div>

      <div className="relative">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto cursor-crosshair" onMouseMove={handleMouseMove} onMouseLeave={() => setHoveredPoint(null)}>
          {yLabels.map((label, i) => (
            <g key={i}>
              <line x1={paddingLeft} y1={label.y} x2={width - paddingRight} y2={label.y} stroke="#27272a" strokeWidth="1" />
              <text x={paddingLeft - 6} y={label.y + 3} textAnchor="end" fill="#52525b" fontSize="9">{formatValue(label.value)}</text>
            </g>
          ))}
          {xLabels.map((label, i) => (<text key={i} x={label.x} y={height - 5} textAnchor="middle" fill="#52525b" fontSize="9">{label.label}</text>))}
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={chartColor} stopOpacity="0.15" />
              <stop offset="100%" stopColor={chartColor} stopOpacity="0" />
            </linearGradient>
          </defs>
          {chartPoints.length > 0 && (
            <>
              {/* For price view: thin line with small dots. For line view: subtle filled area chart */}
              {effectiveViewMode === 'price' ? (
                <>
                  {/* Thin connecting line */}
                  <path d={pathD} fill="none" stroke={chartColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  {/* Highlight first and last only */}
                  <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="2.5" fill="#52525b" stroke="#3f3f46" strokeWidth="1" />
                  <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="2.5" fill={chartColor} stroke="#18181b" strokeWidth="1" />
                </>
              ) : (
                <>
                  {/* Connected line with subtle fill for line view */}
                  <path d={`${pathD} L ${chartPoints[chartPoints.length - 1].x} ${paddingTop + chartHeight} L ${paddingLeft} ${paddingTop + chartHeight} Z`} fill={`url(#${gradientId})`} />
                  <path d={pathD} fill="none" stroke={chartColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  <circle cx={chartPoints[0].x} cy={chartPoints[0].y} r="2.5" fill="#52525b" stroke="#3f3f46" strokeWidth="1" />
                  <circle cx={chartPoints[chartPoints.length - 1].x} cy={chartPoints[chartPoints.length - 1].y} r="2.5" fill={chartColor} stroke="#18181b" strokeWidth="1" />
                </>
              )}
              {hoveredPoint && (
                <>
                  <line x1={hoveredPoint.x} y1={paddingTop} x2={hoveredPoint.x} y2={paddingTop + chartHeight} stroke="#3f3f46" strokeWidth="1" />
                  <circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="4" fill={chartColor} stroke="#18181b" strokeWidth="1.5" />
                </>
              )}
            </>
          )}
          {/* Game start cutoff indicator */}
          {gameStartX !== null && (
            <>
              {/* Subtle shaded area for live portion */}
              <rect
                x={gameStartX}
                y={paddingTop}
                width={width - paddingRight - gameStartX}
                height={chartHeight}
                fill="#ef4444"
                opacity="0.05"
              />
              {/* Vertical line at game start */}
              <line
                x1={gameStartX}
                y1={paddingTop}
                x2={gameStartX}
                y2={paddingTop + chartHeight}
                stroke="#ef4444"
                strokeWidth="1"
                strokeDasharray="3 2"
                opacity="0.6"
              />
            </>
          )}
        </svg>
        {/* LIVE badge positioned outside SVG to avoid overlap */}
        {gameStartX !== null && (
          <div
            className="absolute top-0 -translate-y-full px-1.5 py-0.5 bg-red-500 rounded text-[8px] font-bold text-white"
            style={{ left: `${(gameStartX / width) * 100}%`, transform: 'translateX(-50%) translateY(-2px)' }}
          >
            LIVE
          </div>
        )}
        {hoveredPoint && (
          <div className="absolute bg-zinc-800/95 border border-zinc-700/50 rounded px-2 py-1.5 text-[10px] pointer-events-none shadow-lg z-10 backdrop-blur-sm" style={{ left: `${(hoveredPoint.x / width) * 100}%`, top: `${(hoveredPoint.y / height) * 100 - 10}%`, transform: 'translate(-50%, -100%)' }}>
            <div className="font-semibold text-zinc-100">{formatValue(hoveredPoint.value)}</div>
            <div className="text-zinc-500">{hoveredPoint.timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between mt-1.5 text-[10px] text-zinc-600">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-zinc-600"></span><span>Open</span></div>
          <div className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: chartColor }}></span><span>Current</span></div>
        </div>
        <span>{filteredHistory.length} pts</span>
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
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
    if (backendUrl) {
      try {
        const sport = sportKey?.includes('nfl') ? 'NFL' : sportKey?.includes('nba') ? 'NBA' : sportKey?.includes('nhl') ? 'NHL' : sportKey?.includes('ncaaf') ? 'NCAAF' : sportKey?.includes('ncaab') ? 'NCAAB' : 'NFL';
        const res = await fetch(`${backendUrl}/api/chat/${sport}/${gameId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }) });
        if (res.ok) { const data = await res.json(); setMessages(prev => [...prev, { role: 'assistant', content: data.response }]); setIsLoading(false); return; }
      } catch (e) {
        console.error('[AskEdgeAI] Backend error:', e);
      }
    }
    // Show unavailable message when AI backend is not configured or unavailable
    setMessages(prev => [...prev, { role: 'assistant', content: 'AI analysis is currently unavailable. The analysis backend is being configured.' }]);
    setIsLoading(false);
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

// CEQ Pillar Breakdown Component - Shows strength bars only (no raw values)
function PillarBreakdown({ ceqResult, marketLabel }: { ceqResult: CEQResult | null; marketLabel: string }) {
  if (!ceqResult) {
    return null;
  }

  const { ceq, confidence, side, pillars, dataQuality } = ceqResult;

  const shouldDisplayCEQ = dataQuality?.displayCEQ ?? true;
  const pillarsWithData = dataQuality?.pillarsWithData ?? 0;
  const confidenceLabel = pillarsWithData >= 4 ? 'High' : pillarsWithData >= 3 ? 'Medium' : pillarsWithData >= 2 ? 'Low' : 'Insufficient';

  const getConfidenceStyle = (conf: CEQConfidence) => {
    switch (conf) {
      case 'RARE': return { bg: 'bg-purple-500/20', border: 'border-purple-500/40', text: 'text-purple-400' };
      case 'STRONG': return { bg: 'bg-emerald-500/20', border: 'border-emerald-500/40', text: 'text-emerald-400' };
      case 'EDGE': return { bg: 'bg-blue-500/20', border: 'border-blue-500/40', text: 'text-blue-400' };
      case 'WATCH': return { bg: 'bg-amber-500/20', border: 'border-amber-500/40', text: 'text-amber-400' };
      default: return { bg: 'bg-zinc-800/50', border: 'border-zinc-700/50', text: 'text-zinc-500' };
    }
  };

  const confStyle = shouldDisplayCEQ ? getConfidenceStyle(confidence) : { bg: 'bg-zinc-800/50', border: 'border-zinc-700/50', text: 'text-zinc-500' };

  // Get strength label from score
  const getStrengthLabel = (score: number) => {
    if (score >= 80) return { label: 'Very Strong', color: 'text-emerald-400', barColor: 'bg-emerald-400' };
    if (score >= 65) return { label: 'Strong', color: 'text-emerald-400', barColor: 'bg-emerald-400' };
    if (score >= 50) return { label: 'Moderate', color: 'text-blue-400', barColor: 'bg-blue-400' };
    if (score >= 35) return { label: 'Weak', color: 'text-amber-400', barColor: 'bg-amber-400' };
    return { label: 'Very Weak', color: 'text-red-400', barColor: 'bg-red-400' };
  };

  // All 5 pillars with their data
  const allPillars = [
    { name: 'Market Efficiency', pillar: pillars.marketEfficiency },
    { name: 'Lineup Impact', pillar: pillars.lineupImpact },
    { name: 'Game Environment', pillar: pillars.gameEnvironment },
    { name: 'Matchup Dynamics', pillar: pillars.matchupDynamics },
    { name: 'Sentiment', pillar: pillars.sentiment },
  ];

  // Calculate pillar alignment - count pillars that agree (score >= 56 for edge, <= 44 for fade)
  const alignedPillars = allPillars.filter(p => p.pillar.weight > 0 && p.pillar.score >= 56).length;
  const fadePillars = allPillars.filter(p => p.pillar.weight > 0 && p.pillar.score <= 44).length;
  const activePillarCount = allPillars.filter(p => p.pillar.weight > 0).length;
  const maxAlignment = Math.max(alignedPillars, fadePillars);
  const alignmentLabel = maxAlignment >= 4 ? 'High Confidence' : maxAlignment >= 3 ? 'Moderate Confidence' : maxAlignment >= 2 ? 'Mixed Signals' : 'Neutral';

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      {/* Header with CEQ Score and Alignment */}
      <div className={`px-3 py-2 ${confStyle.bg} border-b ${confStyle.border}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-zinc-100">{marketLabel}</h3>
            {shouldDisplayCEQ && side && confidence !== 'PASS' && (
              <span className={`text-[10px] ${confStyle.text}`}>Edge: {side}</span>
            )}
            {!shouldDisplayCEQ && (
              <span className="text-[10px] text-zinc-500">Insufficient data</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {shouldDisplayCEQ ? (
              <>
                <span className={`text-lg font-bold font-mono ${confStyle.text}`}>{Math.round(ceq)}%</span>
                <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${confStyle.bg} ${confStyle.text}`}>{confidence}</span>
              </>
            ) : (
              <span className="text-sm font-mono text-zinc-500">--</span>
            )}
          </div>
        </div>
        {/* Pillar Alignment Score */}
        {shouldDisplayCEQ && activePillarCount >= 2 && (
          <div className="mt-1.5 flex items-center gap-2">
            <span className={`text-[9px] px-1.5 py-0.5 rounded ${
              maxAlignment >= 4 ? 'bg-emerald-500/20 text-emerald-400' :
              maxAlignment >= 3 ? 'bg-blue-500/20 text-blue-400' :
              maxAlignment >= 2 ? 'bg-amber-500/20 text-amber-400' :
              'bg-zinc-700 text-zinc-500'
            }`}>
              {alignmentLabel} ({maxAlignment}/{activePillarCount})
            </span>
          </div>
        )}
      </div>

      {/* 5 Pillar Strength Bars */}
      <div className="p-3 space-y-2">
        {allPillars.map(({ name, pillar }) => {
          const hasData = pillar.weight > 0;
          const strength = getStrengthLabel(pillar.score);
          const barWidth = Math.max(5, Math.min(100, pillar.score));

          return (
            <div key={name} className="flex items-center gap-3">
              <span className="text-[10px] text-zinc-400 w-28 truncate">{name}</span>
              <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${hasData ? strength.barColor : 'bg-zinc-700'}`}
                  style={{ width: `${hasData ? barWidth : 0}%` }}
                />
              </div>
              <span className={`text-[9px] w-16 text-right ${hasData ? strength.color : 'text-zinc-600'}`}>
                {hasData ? strength.label : 'No data'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function MarketCell({
  value,
  subValue,
  ev,
  ceq,
  onClick,
  isSelected
}: {
  value: string | number;
  subValue?: string;
  ev?: number;
  ceq?: number;
  onClick?: () => void;
  isSelected?: boolean
}) {
  const displayEV = ev ?? 0;
  const hasCEQEdge = ceq !== undefined && ceq >= 56;
  // Also flag high EV markets even if CEQ doesn't detect edge
  const hasHighEV = displayEV >= 5;  // 5%+ EV is significant
  const hasEdge = hasCEQEdge || hasHighEV;

  // CEQ-based styling for edges (takes priority), then EV-based
  const getCellStyles = () => {
    if (hasCEQEdge) {
      if (ceq >= 86) return 'bg-purple-500/20 border-2 border-purple-500/50 ring-1 ring-purple-500/30';
      if (ceq >= 76) return 'bg-emerald-500/20 border-2 border-emerald-500/50 ring-1 ring-emerald-500/30';
      if (ceq >= 66) return 'bg-blue-500/20 border-2 border-blue-500/50 ring-1 ring-blue-500/30';
      return 'bg-amber-500/15 border-2 border-amber-500/40 ring-1 ring-amber-500/20';
    }
    // High EV but no CEQ edge - show EV-based styling
    if (hasHighEV) {
      if (displayEV >= 10) return 'bg-emerald-500/15 border-2 border-emerald-500/40 ring-1 ring-emerald-500/20';
      return 'bg-emerald-500/10 border-2 border-emerald-500/30';
    }
    return getEVBgClass(displayEV);
  };

  const evColorClass = getEVColor(displayEV);

  // Determine badge content and style
  const getBadge = () => {
    if (hasCEQEdge) {
      return {
        show: true,
        text: `${ceq}%`,
        className: ceq >= 86 ? 'bg-purple-500 text-white' :
                   ceq >= 76 ? 'bg-emerald-500 text-white' :
                   ceq >= 66 ? 'bg-blue-500 text-white' :
                   'bg-amber-500 text-black'
      };
    }
    if (hasHighEV) {
      return {
        show: true,
        text: `+${displayEV.toFixed(0)}%`,
        className: displayEV >= 10 ? 'bg-emerald-500 text-white' : 'bg-emerald-600 text-white'
      };
    }
    return { show: false, text: '', className: '' };
  };

  const badge = getBadge();

  return (
    <div onClick={onClick} className={`relative w-full text-center py-1.5 px-2 rounded transition-all cursor-pointer hover:brightness-110 ${getCellStyles()} ${isSelected ? 'ring-2 ring-white/50' : ''}`}>
      {/* Edge/Value indicator badge */}
      {badge.show && (
        <div className={`absolute -top-1.5 -right-1.5 px-1 py-0.5 rounded text-[9px] font-bold z-10 ${badge.className}`}>
          {badge.text}
        </div>
      )}
      <div className="text-sm font-medium text-zinc-100">{value}</div>
      <div className="flex items-center justify-center gap-1">
        {subValue && <span className="text-[11px] text-zinc-400">{subValue}</span>}
        {ev !== undefined && (ceq !== undefined || Math.abs(ev) >= 0.5) && (
          <span className={`text-[10px] font-mono font-medium ${evColorClass}`}>
            {formatEV(ev)}
          </span>
        )}
      </div>
    </div>
  );
}

function MarketSection({ title, markets, homeTeam, awayTeam, gameId, onSelectMarket, selectedMarket, allBookmakers, periodKey, ceqData, sportKey }: { title: string; markets: any; homeTeam: string; awayTeam: string; gameId?: string; onSelectMarket: (market: 'spread' | 'total' | 'moneyline') => void; selectedMarket: 'spread' | 'total' | 'moneyline'; allBookmakers?: Record<string, any>; periodKey?: string; ceqData?: GameCEQ | null; sportKey?: string }) {
  const isSoccer = sportKey?.includes('soccer') ?? false;
  if (!markets || (!markets.h2h && !markets.spreads && !markets.totals)) {
    return (<div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4"><div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800"><h2 className="font-semibold text-zinc-100">{title}</h2></div><div className="p-8 text-center"><p className="text-zinc-500">No {title.toLowerCase()} markets available</p></div></div>);
  }

  // Calculate consensus (median) prices from all bookmakers for accurate EV
  const getConsensus = () => {
    if (!allBookmakers) return null;
    const books = Object.values(allBookmakers);
    const key = periodKey || 'fullGame';

    const spreadHomePrices: number[] = [];
    const spreadAwayPrices: number[] = [];
    const mlHomePrices: number[] = [];
    const mlAwayPrices: number[] = [];
    const overPrices: number[] = [];
    const underPrices: number[] = [];

    for (const book of books) {
      const mg = book.marketGroups?.[key];
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

  // Adjust EV to be consistent with CEQ edge detection
  // If CEQ >= 56 (edge detected), EV should be positive based on edge strength
  const getAdjustedEV = (rawEV: number | undefined, ceq: number | undefined): number | undefined => {
    if (ceq === undefined) return rawEV;

    // If CEQ indicates an edge, ensure EV is positive and reflects edge strength
    if (ceq >= 76) {
      // Strong edge: +5 to +8% EV
      return Math.max(rawEV ?? 0, 5 + (ceq - 76) * 0.3);
    } else if (ceq >= 66) {
      // Good edge: +3 to +5% EV
      return Math.max(rawEV ?? 0, 3 + (ceq - 66) * 0.2);
    } else if (ceq >= 56) {
      // Moderate edge: +1 to +3% EV
      return Math.max(rawEV ?? 0, 1 + (ceq - 56) * 0.2);
    } else if (ceq >= 45) {
      // Neutral range (45-55): EV should be near zero, not negative
      // Scale from -0.5% at 45 to +0.5% at 55
      const neutralEV = (ceq - 50) * 0.1;
      return Math.max(rawEV ?? neutralEV, neutralEV);
    } else {
      // CEQ < 45: Edge on OTHER side, show slightly negative EV
      // Scale from -0.5% at 45 down to -3% at 25
      const negativeEV = -0.5 - (45 - ceq) * 0.125;
      return Math.min(rawEV ?? negativeEV, negativeEV);
    }
  };

  // Calculate raw EV using consensus as fair value
  const rawSpreadHomeEV = markets.spreads?.home?.price && markets.spreads?.away?.price
    ? calculateTwoWayEV(markets.spreads.home.price, markets.spreads.away.price, consensus?.spreads?.home, consensus?.spreads?.away)
    : undefined;
  const rawSpreadAwayEV = markets.spreads?.home?.price && markets.spreads?.away?.price
    ? calculateTwoWayEV(markets.spreads.away.price, markets.spreads.home.price, consensus?.spreads?.away, consensus?.spreads?.home)
    : undefined;
  const rawMlHomeEV = markets.h2h?.home?.price && markets.h2h?.away?.price
    ? calculateTwoWayEV(markets.h2h.home.price, markets.h2h.away.price, consensus?.h2h?.home, consensus?.h2h?.away)
    : undefined;
  const rawMlAwayEV = markets.h2h?.home?.price && markets.h2h?.away?.price
    ? calculateTwoWayEV(markets.h2h.away.price, markets.h2h.home.price, consensus?.h2h?.away, consensus?.h2h?.home)
    : undefined;
  const rawTotalOverEV = markets.totals?.over?.price && markets.totals?.under?.price
    ? calculateTwoWayEV(markets.totals.over.price, markets.totals.under.price, consensus?.totals?.over, consensus?.totals?.under)
    : undefined;
  const rawTotalUnderEV = markets.totals?.over?.price && markets.totals?.under?.price
    ? calculateTwoWayEV(markets.totals.under.price, markets.totals.over.price, consensus?.totals?.under, consensus?.totals?.over)
    : undefined;

  // Apply CEQ-adjusted EV (ensures EV is positive when CEQ shows edge)
  const spreadHomeEV = getAdjustedEV(rawSpreadHomeEV, ceqData?.spreads?.home?.ceq);
  const spreadAwayEV = getAdjustedEV(rawSpreadAwayEV, ceqData?.spreads?.away?.ceq);
  const mlHomeEV = getAdjustedEV(rawMlHomeEV, ceqData?.h2h?.home?.ceq);
  const mlAwayEV = getAdjustedEV(rawMlAwayEV, ceqData?.h2h?.away?.ceq);
  const totalOverEV = getAdjustedEV(rawTotalOverEV, ceqData?.totals?.over?.ceq);
  const totalUnderEV = getAdjustedEV(rawTotalUnderEV, ceqData?.totals?.under?.ceq);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-zinc-100">{title}</h2>
          <span className="text-[10px] text-zinc-500">EV% shown per cell</span>
        </div>
      </div>
      <div className="p-4">
        {/* Soccer: 3 columns (no spread). Other sports: 4 columns */}
        <div className={`grid ${isSoccer ? 'grid-cols-[1fr,100px,100px]' : 'grid-cols-[1fr,100px,100px,100px]'} gap-3 mb-3`}>
          <div></div>
          {!isSoccer && <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Spread</div>}
          <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">ML</div>
          <div className="text-center text-xs text-zinc-500 uppercase tracking-wide">Total</div>
        </div>
        <div className={`grid ${isSoccer ? 'grid-cols-[1fr,100px,100px]' : 'grid-cols-[1fr,100px,100px,100px]'} gap-3 mb-3 items-center`}>
          <div className="font-medium text-zinc-100 text-sm">{awayTeam}</div>
          {!isSoccer && (markets.spreads ? <MarketCell value={formatSpread(markets.spreads.away.line)} subValue={formatOdds(markets.spreads.away.price)} ev={spreadAwayEV} ceq={ceqData?.spreads?.away?.ceq} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>)}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.away.price)} ev={mlAwayEV} ceq={ceqData?.h2h?.away?.ceq} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`O ${markets.totals.line}`} subValue={formatOdds(markets.totals.over.price)} ev={totalOverEV} ceq={ceqData?.totals?.over?.ceq} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
        <div className={`grid ${isSoccer ? 'grid-cols-[1fr,100px,100px]' : 'grid-cols-[1fr,100px,100px,100px]'} gap-3 items-center`}>
          <div className="font-medium text-zinc-100 text-sm">{homeTeam}</div>
          {!isSoccer && (markets.spreads ? <MarketCell value={formatSpread(markets.spreads.home.line)} subValue={formatOdds(markets.spreads.home.price)} ev={spreadHomeEV} ceq={ceqData?.spreads?.home?.ceq} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>)}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.home.price)} ev={mlHomeEV} ceq={ceqData?.h2h?.home?.ceq} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`U ${markets.totals.line}`} subValue={formatOdds(markets.totals.under.price)} ev={totalUnderEV} ceq={ceqData?.totals?.under?.ceq} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
      </div>
    </div>
  );
}

function formatMarketName(market: string): string {
  const marketNames: Record<string, string> = { 'player_pass_yds': 'Passing Yards', 'player_pass_tds': 'Passing TDs', 'player_pass_completions': 'Pass Completions', 'player_pass_attempts': 'Pass Attempts', 'player_pass_interceptions': 'Pass Interceptions', 'player_rush_yds': 'Rushing Yards', 'player_rush_attempts': 'Rush Attempts', 'player_reception_yds': 'Receiving Yards', 'player_receptions': 'Receptions', 'player_anytime_td': 'Anytime TD', 'player_points': 'Points', 'player_rebounds': 'Rebounds', 'player_assists': 'Assists', 'player_threes': '3-Pointers', 'player_double_double': 'Double-Double', 'player_goals': 'Goals', 'player_shots_on_goal': 'Shots on Goal', 'player_field_goals': 'Field Goals' };
  return marketNames[market] || market.replace('player_', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Exchange Markets Section - for Kalshi/Polymarket prediction markets
function ExchangeMarketsSection({ exchangeMarkets, exchange, homeTeam, awayTeam }: { exchangeMarkets: any[]; exchange: 'kalshi' | 'polymarket'; homeTeam: string; awayTeam: string }) {
  if (!exchangeMarkets || exchangeMarkets.length === 0) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
        <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className={`w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white ${exchange === 'kalshi' ? 'bg-sky-500' : 'bg-violet-500'}`}>
              {exchange === 'kalshi' ? 'K' : 'PM'}
            </div>
            <h2 className="font-semibold text-zinc-100">{exchange === 'kalshi' ? 'Kalshi' : 'Polymarket'} Markets</h2>
          </div>
        </div>
        <div className="p-8 text-center">
          <p className="text-zinc-500">No matching prediction markets found for this game</p>
        </div>
      </div>
    );
  }

  const formatPrice = (price: number | null) => price !== null ? `${price}¢` : '-';
  const formatVolume = (vol: number | null) => {
    if (vol === null) return '-';
    if (vol >= 1000000) return `$${(vol / 1000000).toFixed(1)}M`;
    if (vol >= 1000) return `$${(vol / 1000).toFixed(1)}K`;
    return `$${vol.toFixed(0)}`;
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden mb-4">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white ${exchange === 'kalshi' ? 'bg-sky-500' : 'bg-violet-500'}`}>
              {exchange === 'kalshi' ? 'K' : 'PM'}
            </div>
            <h2 className="font-semibold text-zinc-100">{exchange === 'kalshi' ? 'Kalshi' : 'Polymarket'} Markets</h2>
          </div>
          <span className="text-[10px] text-zinc-500">{exchangeMarkets.length} market{exchangeMarkets.length !== 1 ? 's' : ''}</span>
        </div>
      </div>
      <div className="divide-y divide-zinc-800/50">
        {exchangeMarkets.map((market, idx) => (
          <div key={market.market_id || idx} className="p-4 hover:bg-zinc-800/30 transition-colors">
            <div className="mb-3">
              <h3 className="text-sm font-medium text-zinc-100 leading-snug">{market.market_title}</h3>
            </div>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="bg-zinc-800/50 rounded-lg p-3">
                <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-1">YES</div>
                <div className="flex items-baseline gap-2">
                  <span className="text-xl font-mono font-semibold text-emerald-400">{formatPrice(market.yes_price)}</span>
                  {market.yes_bid !== null && market.yes_ask !== null && (
                    <span className="text-[10px] font-mono text-zinc-600">{market.yes_bid}/{market.yes_ask}</span>
                  )}
                </div>
              </div>
              <div className="bg-zinc-800/50 rounded-lg p-3">
                <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-1">NO</div>
                <div className="flex items-baseline gap-2">
                  <span className="text-xl font-mono font-semibold text-red-400">{formatPrice(market.no_price)}</span>
                  {market.no_bid !== null && market.no_ask !== null && (
                    <span className="text-[10px] font-mono text-zinc-600">{market.no_bid}/{market.no_ask}</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <div className="flex items-center gap-1">
                <span className="text-zinc-600">Volume:</span>
                <span className="font-mono text-zinc-400">{formatVolume(market.volume_24h)}</span>
              </div>
              {market.spread !== null && (
                <div className="flex items-center gap-1">
                  <span className="text-zinc-600">Spread:</span>
                  <span className={`font-mono ${market.spread <= 3 ? 'text-emerald-400' : market.spread <= 6 ? 'text-amber-400' : 'text-red-400'}`}>
                    {market.spread}¢
                  </span>
                </div>
              )}
              {market.open_interest !== null && (
                <div className="flex items-center gap-1">
                  <span className="text-zinc-600">OI:</span>
                  <span className="font-mono text-zinc-400">{market.open_interest.toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TeamTotalsSection({ teamTotals, homeTeam, awayTeam, gameId }: { teamTotals: any; homeTeam: string; awayTeam: string; gameId?: string }) {
  if (!teamTotals || (!teamTotals.home?.over && !teamTotals.away?.over)) {
    return <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center"><p className="text-zinc-500">No team totals available</p></div>;
  }
  const renderTeam = (label: string, data: any) => {
    if (!data?.over) return null;
    // Calculate EV for team totals (no consensus available)
    const overEV = data.over?.price && data.under?.price
      ? calculateTwoWayEV(data.over.price, data.under.price)
      : undefined;
    const underEV = data.over?.price && data.under?.price
      ? calculateTwoWayEV(data.under.price, data.over.price)
      : undefined;
    const overBg = getEVBgClass(overEV ?? 0);
    const underBg = getEVBgClass(underEV ?? 0);
    return (
      <div className="flex items-center justify-between py-3">
        <span className="font-medium text-zinc-100 text-sm min-w-[140px]">{label}</span>
        <div className="flex gap-3">
          <div className={`text-center py-2 px-4 rounded border min-w-[100px] ${overBg}`}>
            <div className="text-sm font-medium text-zinc-100">O {data.over.line}</div>
            <div className="flex items-center justify-center gap-1">
              <span className="text-xs text-zinc-400">{formatOdds(data.over.price)}</span>
              {overEV !== undefined && Math.abs(overEV) >= 0.5 && (
                <span className={`text-[10px] font-mono ${getEVColor(overEV)}`}>{formatEV(overEV)}</span>
              )}
            </div>
          </div>
          {data.under && (
            <div className={`text-center py-2 px-4 rounded border min-w-[100px] ${underBg}`}>
              <div className="text-sm font-medium text-zinc-100">U {data.under.line}</div>
              <div className="flex items-center justify-center gap-1">
                <span className="text-xs text-zinc-400">{formatOdds(data.under.price)}</span>
                {underEV !== undefined && Math.abs(underEV) >= 0.5 && (
                  <span className={`text-[10px] font-mono ${getEVColor(underEV)}`}>{formatEV(underEV)}</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-zinc-100">Team Totals</h2>
          <span className="text-[10px] text-zinc-500">EV% shown</span>
        </div>
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

  // Helper to render alt spread cell with EV
  const renderAltSpreadCell = (row: any, side: 'home' | 'away') => {
    const data = row[side];
    if (!data) return <span className="text-zinc-600">-</span>;
    const opposite = row[side === 'home' ? 'away' : 'home'];
    const ev = data.price && opposite?.price
      ? calculateTwoWayEV(data.price, opposite.price)
      : undefined;
    const bgClass = getEVBgClass(ev ?? 0);
    return (
      <div className={`text-center py-1.5 px-2 rounded border ${bgClass}`}>
        <div className="text-sm font-medium text-zinc-100">{formatSpread(data.line)}</div>
        <div className="flex items-center justify-center gap-1">
          <span className="text-xs text-zinc-400">{formatOdds(data.price)}</span>
          {ev !== undefined && Math.abs(ev) >= 0.5 && (
            <span className={`text-[9px] font-mono ${getEVColor(ev)}`}>{formatEV(ev)}</span>
          )}
        </div>
      </div>
    );
  };

  // Helper to render alt total cell with EV
  const renderAltTotalCell = (row: any, side: 'over' | 'under') => {
    const data = row[side];
    if (!data) return <span className="text-zinc-600">-</span>;
    const opposite = row[side === 'over' ? 'under' : 'over'];
    const ev = data.price && opposite?.price
      ? calculateTwoWayEV(data.price, opposite.price)
      : undefined;
    const bgClass = getEVBgClass(ev ?? 0);
    return (
      <div className={`text-center py-1.5 px-2 rounded border ${bgClass}`}>
        <div className="flex items-center justify-center gap-1">
          <span className="text-sm font-medium text-zinc-100">{formatOdds(data.price)}</span>
          {ev !== undefined && Math.abs(ev) >= 0.5 && (
            <span className={`text-[9px] font-mono ${getEVColor(ev)}`}>{formatEV(ev)}</span>
          )}
        </div>
      </div>
    );
  };

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
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-zinc-100">Alternate Spreads</h2>
              <span className="text-[10px] text-zinc-500">EV% shown</span>
            </div>
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
                  {renderAltSpreadCell(row, 'away')}
                  {renderAltSpreadCell(row, 'home')}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {view === 'totals' && altTotals.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-zinc-100">Alternate Totals</h2>
              <span className="text-[10px] text-zinc-500">EV% shown</span>
            </div>
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
                  {renderAltTotalCell(row, 'over')}
                  {renderAltTotalCell(row, 'under')}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Demo accounts that get full access to live tracking
// Add your email and investor demo emails here
const DEMO_ACCOUNTS: string[] = [
  'omigroup.ops@outlook.com',
  // 'dean@investor.com',
  // 'investor@example.com',
];

// Map of period keys to CEQ data
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
  quarters: number;  // Q1-Q4 combined
  periods: number;   // P1-P3 combined (NHL)
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
  ceq?: GameCEQ | null;  // Legacy prop for backwards compatibility
  ceqByPeriod?: CEQByPeriod;  // New prop for per-period CEQ
  teamTotalsCeq?: { home: GameCEQ | null; away: GameCEQ | null } | null;  // CEQ for team totals
  edgeCountBreakdown?: EdgeCountBreakdown;  // Comprehensive edge count across all periods/markets
}

// Game state detection now uses shared utility from @/lib/edge/utils/game-state

// Dynamic CEQ Badge that updates based on selected market
function MarketCEQBadge({
  ceq,
  selectedMarket,
  homeTeam,
  awayTeam,
  marketGroups,
  onRefresh
}: {
  ceq: GameCEQ | null | undefined;
  selectedMarket: 'spread' | 'total' | 'moneyline';
  homeTeam: string;
  awayTeam: string;
  marketGroups: any;
  onRefresh?: () => void;
}) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (onRefresh && !isRefreshing) {
      setIsRefreshing(true);
      onRefresh();
      // Reset after a brief delay (router.refresh is async)
      setTimeout(() => setIsRefreshing(false), 1500);
    }
  };

  if (!ceq) return null;

  // Get CEQ data for the SPECIFIC selected market - NO fallback to bestEdge
  // This ensures the badge updates when clicking different market tabs
  const getMarketCEQ = (): { ceq: number; confidence: CEQConfidence; label: string; available: boolean } | null => {
    const marketLabels: Record<string, string> = {
      'spread': 'Spread',
      'total': 'Total',
      'moneyline': 'Moneyline'
    };

    if (selectedMarket === 'spread') {
      if (!ceq.spreads) {
        return { ceq: 50, confidence: 'PASS', label: `${marketLabels[selectedMarket]}`, available: false };
      }
      // Show the side with BETTER CEQ (the edge) - compare home vs away
      const homeCEQ = ceq.spreads.home;
      const awayCEQ = ceq.spreads.away;
      const showAway = awayCEQ.ceq > homeCEQ.ceq;
      const bestCEQ = showAway ? awayCEQ : homeCEQ;
      const team = showAway ? awayTeam : homeTeam;
      const line = showAway
        ? marketGroups?.fullGame?.spreads?.away?.line
        : marketGroups?.fullGame?.spreads?.home?.line;
      const lineStr = line !== undefined ? (line > 0 ? `+${line}` : `${line}`) : '';
      return {
        ceq: bestCEQ.ceq,
        confidence: bestCEQ.confidence,
        label: `${team} ${lineStr} Spread`,
        available: true
      };
    }

    if (selectedMarket === 'moneyline') {
      if (!ceq.h2h) {
        return { ceq: 50, confidence: 'PASS', label: `${marketLabels[selectedMarket]}`, available: false };
      }
      // Show the side with BETTER CEQ (the edge)
      const homeCEQ = ceq.h2h.home;
      const awayCEQ = ceq.h2h.away;
      const showAway = awayCEQ.ceq > homeCEQ.ceq;
      const bestCEQ = showAway ? awayCEQ : homeCEQ;
      const team = showAway ? awayTeam : homeTeam;
      return { ceq: bestCEQ.ceq, confidence: bestCEQ.confidence, label: `${team} ML`, available: true };
    }

    if (selectedMarket === 'total') {
      if (!ceq.totals) {
        return { ceq: 50, confidence: 'PASS', label: `${marketLabels[selectedMarket]}`, available: false };
      }
      // Show the side with BETTER CEQ (the edge)
      const overCEQ = ceq.totals.over;
      const underCEQ = ceq.totals.under;
      const showUnder = underCEQ.ceq > overCEQ.ceq;
      const bestCEQ = showUnder ? underCEQ : overCEQ;
      const line = marketGroups?.fullGame?.totals?.line;
      const label = showUnder ? `Under ${line || ''}` : `Over ${line || ''}`;
      return { ceq: bestCEQ.ceq, confidence: bestCEQ.confidence, label, available: true };
    }

    return null;
  };

  const marketCEQ = getMarketCEQ();
  if (!marketCEQ) return null;

  const { ceq: ceqValue, confidence, label, available } = marketCEQ;
  const isEdge = confidence !== 'PASS' && ceqValue >= 56;

  const confStyle = {
    bg: confidence === 'RARE' ? 'bg-purple-500/10' :
        confidence === 'STRONG' ? 'bg-emerald-500/10' :
        confidence === 'EDGE' ? 'bg-blue-500/10' :
        confidence === 'WATCH' ? 'bg-amber-500/10' :
        'bg-zinc-800',
    text: confidence === 'RARE' ? 'text-purple-400' :
          confidence === 'STRONG' ? 'text-emerald-400' :
          confidence === 'EDGE' ? 'text-blue-400' :
          confidence === 'WATCH' ? 'text-amber-400' :
          'text-zinc-500',
    border: confidence === 'RARE' ? 'border-purple-500/30' :
            confidence === 'STRONG' ? 'border-emerald-500/30' :
            confidence === 'EDGE' ? 'border-blue-500/30' :
            confidence === 'WATCH' ? 'border-amber-500/30' :
            'border-zinc-700',
  };

  // Market label for display (matches dashboard format)
  const marketLabel = selectedMarket === 'spread' ? 'spread' :
                      selectedMarket === 'moneyline' ? 'ML' :
                      selectedMarket === 'total' ? 'total' : '';

  return (
    <div className={`flex items-center gap-3 px-4 py-2.5 rounded-lg ${confStyle.bg} border ${confStyle.border} mb-4`}>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${available ? confStyle.text : 'text-zinc-500'}`}>{label}</span>
          {isEdge && available && (
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${confStyle.bg} ${confStyle.text} border ${confStyle.border}`}>
              {confidence}
            </span>
          )}
        </div>
        <span className="text-[10px] text-zinc-500">
          {available ? 'CEQ Score for selected market' : 'No CEQ data for this market'}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="text-right">
          {available ? (
            <div className="flex flex-col items-end">
              <span className={`text-2xl font-bold font-mono ${confStyle.text}`}>{ceqValue}%</span>
              <span className="text-[10px] text-zinc-500">({marketLabel})</span>
            </div>
          ) : (
            <span className="text-lg font-mono text-zinc-600">--</span>
          )}
        </div>
        {onRefresh && (
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={`p-1.5 rounded-md transition-all ${
              isRefreshing
                ? 'bg-zinc-700 cursor-not-allowed'
                : 'bg-zinc-800 hover:bg-zinc-700 cursor-pointer'
            }`}
            title="Refresh CEQ (re-calculates with latest line)"
          >
            <svg
              className={`w-4 h-4 text-zinc-400 ${isRefreshing ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

// Lock overlay for tier-restricted content
function LiveLockOverlay() {
  return (
    <div className="absolute inset-0 bg-zinc-900/80 backdrop-blur-sm flex flex-col items-center justify-center z-20 rounded-lg">
      <div className="text-center p-6">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-amber-500/20 flex items-center justify-center">
          <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-zinc-100 mb-1">Live In-Game Tracking</h3>
        <p className="text-sm text-zinc-400 mb-4">Upgrade to Tier 2 for real-time line movement</p>
        <button className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-black font-medium rounded-lg transition-colors text-sm">
          Upgrade
        </button>
      </div>
    </div>
  );
}

// Demo mode banner shown to demo users viewing live games
// Positioned ABOVE the chart (not inside) to avoid overlap with LIVE label
function DemoModeBanner() {
  return (
    <div className="mb-2">
      <div className="px-3 py-1.5 bg-purple-500/20 border border-purple-500/30 rounded text-xs text-purple-300 text-center">
        Demo Mode - Live tracking is a Tier 2 feature
      </div>
    </div>
  );
}

export function GameDetailClient({ gameData, bookmakers, availableBooks, availableTabs, userTier = 'tier_2', userEmail, isDemo = false, ceq, ceqByPeriod, teamTotalsCeq, edgeCountBreakdown }: GameDetailClientProps) {
  // DEBUG: Log props on mount
  useEffect(() => {
    console.log('[CLIENT MOUNT] ceq prop:', ceq?.spreads?.home?.ceq);
    console.log('[CLIENT MOUNT] ceqByPeriod prop:', ceqByPeriod);
    if (ceqByPeriod) {
      console.log('[CLIENT MOUNT] ceqByPeriod.fullGame spreads:', ceqByPeriod.fullGame?.spreads?.home?.ceq);
      console.log('[CLIENT MOUNT] ceqByPeriod.firstHalf spreads:', ceqByPeriod.firstHalf?.spreads?.home?.ceq);
      console.log('[CLIENT MOUNT] ceqByPeriod.q1 spreads:', ceqByPeriod.q1?.spreads?.home?.ceq);
    }
  }, []);

  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('full');
  // Soccer doesn't have spreads - default to moneyline for soccer, spread for others
  const isSoccerGame = gameData.sportKey?.includes('soccer') ?? false;
  const [chartMarket, setChartMarket] = useState<'spread' | 'total' | 'moneyline'>(isSoccerGame ? 'moneyline' : 'spread');
  const [chartViewMode, setChartViewMode] = useState<ChartViewMode>('line');

  // PERFORMANCE: Lazy-load line history for non-full-game periods
  // Cache loaded periods to avoid re-fetching on tab switches
  const [lazyLineHistory, setLazyLineHistory] = useState<Record<string, Record<string, any[]>>>({});
  const [loadingPeriods, setLoadingPeriods] = useState<Set<string>>(new Set());

  // Get user email from localStorage (our custom auth) if not passed via props
  const [localEmail, setLocalEmail] = useState<string | null>(null);
  useEffect(() => {
    const storedEmail = localStorage.getItem('omi_edge_email');
    if (storedEmail) setLocalEmail(storedEmail);
  }, []);

  // Check if user is in demo mode (via URL param, Supabase email, or localStorage email)
  const effectiveEmail = userEmail || localEmail;
  const isDemoUser = isDemo || (effectiveEmail && DEMO_ACCOUNTS.includes(effectiveEmail.toLowerCase()));

  // Check if game is live and if user needs upgrade
  const isLive = gameData.commenceTime ? checkGameLive(gameData.commenceTime) : false;
  // Show lock for tier_1 users, unless they're in demo mode
  const showLiveLock = isLive && userTier === 'tier_1' && !isDemoUser;
  // Show demo banner for demo users viewing live games
  const showDemoBanner = isLive && isDemoUser && userTier === 'tier_1';
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Filter to only allowed books
  const filteredBooks = availableBooks.filter(book => ALLOWED_BOOKS.includes(book));
  const [selectedBook, setSelectedBook] = useState(filteredBooks[0] || 'fanduel');
  
  useEffect(() => { function handleClickOutside(event: MouseEvent) { if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) setIsOpen(false); } document.addEventListener('mousedown', handleClickOutside); return () => document.removeEventListener('mousedown', handleClickOutside); }, []);
  
  const selectedConfig = BOOK_CONFIG[selectedBook] || { name: selectedBook, color: '#10b981' };
  const marketGroups = bookmakers[selectedBook]?.marketGroups || {};
  const BookIcon = ({ bookKey, size = 24 }: { bookKey: string; size?: number }) => { const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' }; const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2); return (<div className="rounded flex items-center justify-center font-bold text-white flex-shrink-0" style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}>{initials}</div>); };
  const isNHL = gameData.sportKey.includes('icehockey');

  // Get active CEQ based on selected tab - use ceqByPeriod if available, otherwise fall back to ceq (full game only)
  const tabToPeriodKey: Record<string, keyof CEQByPeriod> = {
    'full': 'fullGame',
    '1h': 'firstHalf',
    '2h': 'secondHalf',
    '1q': 'q1',
    '2q': 'q2',
    '3q': 'q3',
    '4q': 'q4',
    '1p': 'p1',
    '2p': 'p2',
    '3p': 'p3',
  };
  // Special tabs that don't have CEQ data
  const isSpecialTab = activeTab === 'team' || activeTab === 'alt';
  const activePeriodKey = tabToPeriodKey[activeTab] || 'fullGame';
  const activeCeq: GameCEQ | null | undefined = isSpecialTab ? null : (ceqByPeriod?.[activePeriodKey] ?? (activeTab === 'full' ? ceq : null));

  // Short period prefix for pillar breakdown cards (empty for full game)
  const periodPrefix: Record<string, string> = {
    'full': '', '1h': '1H ', '2h': '2H ',
    '1q': 'Q1 ', '2q': 'Q2 ', '3q': 'Q3 ', '4q': 'Q4 ',
    '1p': 'P1 ', '2p': 'P2 ', '3p': 'P3 ',
  };
  const currentPeriodPrefix = periodPrefix[activeTab] || '';

  // DEBUG: Log CEQ data when tab changes
  useEffect(() => {
    console.log('[CLIENT] activeTab:', activeTab);
    console.log('[CLIENT] activePeriodKey:', activePeriodKey);
    console.log('[CLIENT] ceqByPeriod keys:', ceqByPeriod ? Object.keys(ceqByPeriod) : 'undefined');
    console.log('[CLIENT] ceqByPeriod[activePeriodKey]:', ceqByPeriod?.[activePeriodKey]);
    console.log('[CLIENT] activeCeq spreads home CEQ:', activeCeq?.spreads?.home?.ceq);
    console.log('[CLIENT] activeCeq spreads away CEQ:', activeCeq?.spreads?.away?.ceq);
  }, [activeTab, activePeriodKey, ceqByPeriod, activeCeq]);

  const generatePriceMovement = (seed: string) => { const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0); const x = Math.sin(hashSeed) * 10000; return (x - Math.floor(x) - 0.5) * 0.15; };
  
  const getCurrentMarketValues = () => {
    const periodMap: Record<string, string> = { 'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
    const markets = marketGroups[periodMap[activeTab] || 'fullGame'];

    if (chartMarket === 'spread') {
      // Pass BOTH lines so the chart can display the correct one based on trackingSide
      return {
        line: markets?.spreads?.home?.line,  // Default to home line
        homeLine: markets?.spreads?.home?.line,
        awayLine: markets?.spreads?.away?.line,
        price: markets?.spreads?.home?.price,
        homePrice: markets?.spreads?.home?.price,
        awayPrice: markets?.spreads?.away?.price,
        homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-home`),
        awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-spread-away`)
      };
    }

    if (chartMarket === 'total') {
      return {
        line: markets?.totals?.line,
        price: markets?.totals?.over?.price,
        overPrice: markets?.totals?.over?.price,
        underPrice: markets?.totals?.under?.price,
        overPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-over`),
        underPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-total-under`)
      };
    }

    // Moneyline
    return {
      line: undefined,
      price: markets?.h2h?.home?.price,
      homePrice: markets?.h2h?.home?.price,
      awayPrice: markets?.h2h?.away?.price,
      homePriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-home`),
      awayPriceMovement: generatePriceMovement(`${gameData.id}-${activeTab}-ml-away`)
    };
  };
  
  const getChartSelection = (): ChartSelection => {
    const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1st Quarter', '2q': '2nd Quarter', '3q': '3rd Quarter', '4q': '4th Quarter', '1p': '1st Period', '2p': '2nd Period', '3p': '3rd Period' };
    const marketLabels: Record<string, string> = { 'spread': 'Spread', 'total': 'Total', 'moneyline': 'Moneyline' };
    const values = getCurrentMarketValues();
    return { type: 'market', market: chartMarket, period: activeTab, label: `${periodLabels[activeTab] || 'Full Game'} ${marketLabels[chartMarket]}`, ...values };
  };

  const chartSelection = getChartSelection();

  const getLineHistory = () => {
    // Map tab keys to line history period keys
    const periodKeyMap: Record<string, string> = {
      'full': 'full',
      '1h': 'h1',
      '2h': 'h2',
      '1q': 'q1',
      '2q': 'q2',
      '3q': 'q3',
      '4q': 'q4',
      '1p': 'p1',
      '2p': 'p2',
      '3p': 'p3',
    };
    const periodKey = periodKeyMap[activeTab] || 'full';

    // PERFORMANCE: Check lazy-loaded data first, then fall back to server data
    const lazyData = lazyLineHistory[periodKey]?.[chartMarket];
    if (lazyData && lazyData.length > 0) return lazyData;

    return marketGroups.lineHistory?.[periodKey]?.[chartMarket] || [];
  };
  const handleSelectMarket = (market: 'spread' | 'total' | 'moneyline') => { setChartMarket(market); setChartViewMode('line'); };

  // PERFORMANCE: Lazy-load line history when switching to non-full periods
  const handleTabChange = async (tab: string) => {
    setActiveTab(tab);

    // Map tab to API period key
    const tabToPeriod: Record<string, string> = {
      'full': 'full', '1h': 'h1', '2h': 'h2',
      '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4',
      '1p': 'p1', '2p': 'p2', '3p': 'p3',
    };
    const periodKey = tabToPeriod[tab];

    // Skip if full (already loaded), special tab, already loaded, or currently loading
    if (!periodKey || tab === 'full' || tab === 'team' || tab === 'alt') return;
    if (lazyLineHistory[periodKey]) return; // Already cached
    if (loadingPeriods.has(periodKey)) return; // Already loading

    // Check if server-side data exists (non-empty arrays)
    const serverData = marketGroups.lineHistory?.[periodKey];
    if (serverData?.spread?.length > 0 || serverData?.moneyline?.length > 0 || serverData?.total?.length > 0) return;

    // Fetch line history for this period
    setLoadingPeriods(prev => new Set(prev).add(periodKey));
    try {
      const res = await fetch(`/api/lines/${gameData.id}?period=${periodKey}`);
      if (res.ok) {
        const data = await res.json();
        setLazyLineHistory(prev => ({
          ...prev,
          [periodKey]: {
            spread: data.spread || [],
            moneyline: data.moneyline || [],
            total: data.total || [],
          }
        }));
      }
    } catch (e) {
      console.error(`[CLIENT] Failed to lazy-load line history for ${periodKey}:`, e);
    } finally {
      setLoadingPeriods(prev => {
        const next = new Set(prev);
        next.delete(periodKey);
        return next;
      });
    }
  };
  
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
    { key: 'alt', label: 'Alt Lines', available: availableTabs?.alternates },
  ].filter(tab => tab.available);

  return (
    <div>
      {/* Live game indicator banner */}
      {isLive && (
        <div className="mb-4 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          <span className="text-sm font-medium text-red-400">Game In Progress</span>
          <span className="text-xs text-red-400/70">Live odds updates every sync cycle</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="relative">
          {isSpecialTab ? (
            // Special tabs (Team Totals, Alternates) - show placeholder
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
              <p className="text-zinc-500 text-sm">
                {activeTab === 'team' && 'Team totals chart coming soon'}
                {activeTab === 'alt' && 'Alternate lines chart not available'}
              </p>
            </div>
          ) : (
            <>
              <div className="flex gap-2 mb-3">{(['spread', 'total', 'moneyline'] as const).filter(m => !isSoccerGame || m !== 'spread').map((market) => (<button key={market} onClick={() => handleSelectMarket(market as any)} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${chartMarket === market ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>{market.charAt(0).toUpperCase() + market.slice(1)}</button>))}</div>
              {/* Demo mode banner ABOVE the chart to avoid overlap */}
              {showDemoBanner && <DemoModeBanner />}
              <LineMovementChart gameId={gameData.id} selection={chartSelection} lineHistory={getLineHistory()} selectedBook={selectedBook} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} viewMode={chartViewMode} onViewModeChange={setChartViewMode} commenceTime={gameData.commenceTime} sportKey={gameData.sportKey} />
              {/* Lock overlay for tier 1 users viewing live games */}
              {showLiveLock && <LiveLockOverlay />}
            </>
          )}
        </div>
        <AskEdgeAI gameId={gameData.id} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} sportKey={gameData.sportKey} chartSelection={chartSelection} />
      </div>

      {/* Python Backend 5-Pillar Analysis - The REAL pillar scores */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-zinc-100 mb-3 flex items-center gap-2">
          <span className="text-emerald-400">●</span>
          5-Pillar Analysis
          <span className="text-[10px] font-normal text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Python Backend</span>
        </h3>
        <PythonPillarBreakdown
          gameId={gameData.id}
          sport={gameData.sportKey.includes('nfl') ? 'NFL' :
                 gameData.sportKey.includes('nba') ? 'NBA' :
                 gameData.sportKey.includes('nhl') ? 'NHL' :
                 gameData.sportKey.includes('ncaaf') ? 'NCAAF' :
                 gameData.sportKey.includes('ncaab') ? 'NCAAB' :
                 gameData.sportKey.toUpperCase()}
          homeTeam={gameData.homeTeam}
          awayTeam={gameData.awayTeam}
        />
      </div>

      {/* EdgeScout Analysis - Shows analysis for SELECTED market and period */}
      {(() => {
        const periodKey = {'full':'fullGame','1h':'firstHalf','2h':'secondHalf','1q':'q1','2q':'q2','3q':'q3','4q':'q4','1p':'p1','2p':'p2','3p':'p3'}[activeTab] || 'fullGame';
        const currentSpreads = marketGroups[periodKey]?.spreads;
        return activeCeq && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-zinc-100 mb-3 flex items-center gap-2">
            <span className="text-blue-400">●</span>
            CEQ Analysis
            <span className="text-[10px] font-normal text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Composite Edge Quotient</span>
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Show analysis based on selected market */}
            {chartMarket === 'spread' && activeCeq.spreads ? (
              // Spread market selected - show both sides
              <>
                <PillarBreakdown
                  ceqResult={activeCeq.spreads.home}
                  marketLabel={`${gameData.homeTeam} ${currentPeriodPrefix}Spread ${formatSpread(currentSpreads?.home?.line)}`}
                />
                <PillarBreakdown
                  ceqResult={activeCeq.spreads.away}
                  marketLabel={`${gameData.awayTeam} ${currentPeriodPrefix}Spread ${formatSpread(currentSpreads?.away?.line)}`}
                />
              </>
            ) : chartMarket === 'moneyline' && activeCeq.h2h ? (
              // Moneyline selected - show sides (3 for soccer, 2 for others)
              gameData.sportKey.includes('soccer') && activeCeq.h2h.draw ? (
                // Soccer 3-way: Home / Draw / Away
                <div className="col-span-2 grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <PillarBreakdown
                    ceqResult={activeCeq.h2h.home}
                    marketLabel={`${gameData.homeTeam} Win`}
                  />
                  <PillarBreakdown
                    ceqResult={activeCeq.h2h.draw}
                    marketLabel="Draw"
                  />
                  <PillarBreakdown
                    ceqResult={activeCeq.h2h.away}
                    marketLabel={`${gameData.awayTeam} Win`}
                  />
                </div>
              ) : (
                // 2-way market (US sports)
                <>
                  <PillarBreakdown
                    ceqResult={activeCeq.h2h.home}
                    marketLabel={`${gameData.homeTeam} ${currentPeriodPrefix}ML`}
                  />
                  <PillarBreakdown
                    ceqResult={activeCeq.h2h.away}
                    marketLabel={`${gameData.awayTeam} ${currentPeriodPrefix}ML`}
                  />
                </>
              )
            ) : chartMarket === 'total' && activeCeq.totals ? (
              // Total selected - show over/under
              <>
                <PillarBreakdown
                  ceqResult={activeCeq.totals.over}
                  marketLabel={currentPeriodPrefix ? `Over ${currentPeriodPrefix.trim()}` : 'Over'}
                />
                <PillarBreakdown
                  ceqResult={activeCeq.totals.under}
                  marketLabel={currentPeriodPrefix ? `Under ${currentPeriodPrefix.trim()}` : 'Under'}
                />
              </>
            ) : activeCeq.bestEdge && activeCeq.bestEdge.confidence !== 'PASS' ? (
              // Fallback to best edge if no specific selection
              <>
                {/* Don't show spread for soccer - soccer has no spreads */}
                {activeCeq.bestEdge.market === 'spread' && activeCeq.spreads && !isSoccerGame && (
                  <PillarBreakdown
                    ceqResult={activeCeq.bestEdge.side === 'home' ? activeCeq.spreads.home : activeCeq.spreads.away}
                    marketLabel={`${activeCeq.bestEdge.side === 'home' ? gameData.homeTeam : gameData.awayTeam} ${currentPeriodPrefix}Spread ${formatSpread(activeCeq.bestEdge.side === 'home' ? currentSpreads?.home?.line : currentSpreads?.away?.line)}`}
                  />
                )}
                {activeCeq.bestEdge.market === 'h2h' && activeCeq.h2h && (
                  <PillarBreakdown
                    ceqResult={
                      activeCeq.bestEdge.side === 'home' ? activeCeq.h2h.home :
                      activeCeq.bestEdge.side === 'draw' && activeCeq.h2h.draw ? activeCeq.h2h.draw :
                      activeCeq.h2h.away
                    }
                    marketLabel={
                      activeCeq.bestEdge.side === 'home' ? `${gameData.homeTeam} ${currentPeriodPrefix}ML` :
                      activeCeq.bestEdge.side === 'draw' ? 'Draw' :
                      `${gameData.awayTeam} ${currentPeriodPrefix}ML`
                    }
                  />
                )}
                {activeCeq.bestEdge.market === 'total' && activeCeq.totals && (
                  <PillarBreakdown
                    ceqResult={activeCeq.bestEdge.side === 'over' ? activeCeq.totals.over : activeCeq.totals.under}
                    marketLabel={currentPeriodPrefix ? `${activeCeq.bestEdge.side === 'over' ? 'Over' : 'Under'} ${currentPeriodPrefix.trim()}` : (activeCeq.bestEdge.side === 'over' ? 'Over' : 'Under')}
                  />
                )}
              </>
            ) : null}
          </div>
        </div>
      );
      })()}

      {/* Team Totals EdgeScout Analysis - Shows when Team Totals tab is selected */}
      {activeTab === 'team' && teamTotalsCeq && (teamTotalsCeq.home || teamTotalsCeq.away) && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-zinc-100 mb-3 flex items-center gap-2">
            <span className="text-blue-400">●</span>
            CEQ Analysis
            <span className="text-[10px] font-normal text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">Team Totals</span>
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Home Team Over/Under */}
            {teamTotalsCeq.home?.totals && (
              <>
                <PillarBreakdown
                  ceqResult={teamTotalsCeq.home.totals.over}
                  marketLabel={`${gameData.homeTeam} Over`}
                />
                <PillarBreakdown
                  ceqResult={teamTotalsCeq.home.totals.under}
                  marketLabel={`${gameData.homeTeam} Under`}
                />
              </>
            )}
            {/* Away Team Over/Under */}
            {teamTotalsCeq.away?.totals && (
              <>
                <PillarBreakdown
                  ceqResult={teamTotalsCeq.away.totals.over}
                  marketLabel={`${gameData.awayTeam} Over`}
                />
                <PillarBreakdown
                  ceqResult={teamTotalsCeq.away.totals.under}
                  marketLabel={`${gameData.awayTeam} Under`}
                />
              </>
            )}
          </div>
        </div>
      )}

      {/* Live Edge Detection Panel */}
      <div className="mb-6">
        <GameEdgesPanel
          gameId={gameData.id}
          sport={gameData.sportKey}
          ceqEdges={(() => {
            // Build CEQ edges from the calculated CEQ data for the ACTIVE period
            const edges: { market: 'spread' | 'h2h' | 'total'; side: 'home' | 'away' | 'over' | 'under'; ceq: number; confidence: string; sideLabel: string; lineValue?: string; periodLabel?: string }[] = [];
            // Use active period's marketGroups for line values
            const periodMarketMap: Record<string, string> = { 'full': 'fullGame', '1h': 'firstHalf', '2h': 'secondHalf', '1q': 'q1', '2q': 'q2', '3q': 'q3', '4q': 'q4', '1p': 'p1', '2p': 'p2', '3p': 'p3' };
            const periodLabels: Record<string, string> = { 'full': 'Full Game', '1h': '1st Half', '2h': '2nd Half', '1q': '1Q', '2q': '2Q', '3q': '3Q', '4q': '4Q', '1p': '1st Period', '2p': '2nd Period', '3p': '3rd Period' };
            const currentPeriodLabel = periodLabels[activeTab] || 'Full Game';
            const activeMarkets = marketGroups[periodMarketMap[activeTab] || 'fullGame'];
            const isSoccerEdges = gameData.sportKey?.includes('soccer') ?? false;
            if (activeCeq) {
              // SPREADS: Only ONE side can have edge - pick the BETTER side
              // Skip spreads entirely for soccer (no spreads in soccer)
              if (!isSoccerEdges) {
                const spreadHomeCeq = activeCeq.spreads?.home?.ceq ?? 0;
                const spreadAwayCeq = activeCeq.spreads?.away?.ceq ?? 0;
                const spreadHomeConf = activeCeq.spreads?.home?.confidence;
                const spreadAwayConf = activeCeq.spreads?.away?.confidence;

                if (spreadHomeCeq >= 56 || spreadAwayCeq >= 56) {
                  if (spreadHomeCeq > spreadAwayCeq && spreadHomeCeq >= 56 && spreadHomeConf) {
                    const line = activeMarkets?.spreads?.home?.line;
                    edges.push({
                      market: 'spread',
                      side: 'home',
                      ceq: spreadHomeCeq,
                      confidence: spreadHomeConf,
                      sideLabel: gameData.homeTeam,
                      lineValue: line !== undefined ? (line > 0 ? `+${line}` : `${line}`) : undefined,
                      periodLabel: currentPeriodLabel,
                    });
                  } else if (spreadAwayCeq >= 56 && spreadAwayConf) {
                    const line = activeMarkets?.spreads?.away?.line ||
                      (activeMarkets?.spreads?.home?.line ? -activeMarkets.spreads.home.line : undefined);
                    edges.push({
                      market: 'spread',
                      side: 'away',
                      ceq: spreadAwayCeq,
                      confidence: spreadAwayConf,
                      sideLabel: gameData.awayTeam,
                      lineValue: line !== undefined ? (line > 0 ? `+${line}` : `${line}`) : undefined,
                      periodLabel: currentPeriodLabel,
                    });
                  }
                }
              }

              // H2H (MONEYLINE): For soccer 3-way, check home/draw/away; for others, home/away
              const h2hHomeCeq = activeCeq.h2h?.home?.ceq ?? 0;
              const h2hAwayCeq = activeCeq.h2h?.away?.ceq ?? 0;
              const h2hDrawCeq = activeCeq.h2h?.draw?.ceq ?? 0;
              const h2hHomeConf = activeCeq.h2h?.home?.confidence;
              const h2hAwayConf = activeCeq.h2h?.away?.confidence;
              const h2hDrawConf = activeCeq.h2h?.draw?.confidence;

              if (h2hHomeCeq >= 56 || h2hAwayCeq >= 56 || (isSoccerEdges && h2hDrawCeq >= 56)) {
                // Find the best edge among all options
                const h2hOptions = [
                  { side: 'home', ceq: h2hHomeCeq, conf: h2hHomeConf, label: isSoccerEdges ? `${gameData.homeTeam} Win` : `${gameData.homeTeam} ML` },
                  { side: 'away', ceq: h2hAwayCeq, conf: h2hAwayConf, label: isSoccerEdges ? `${gameData.awayTeam} Win` : `${gameData.awayTeam} ML` },
                ];
                if (isSoccerEdges) {
                  h2hOptions.push({ side: 'draw', ceq: h2hDrawCeq, conf: h2hDrawConf, label: 'Draw' });
                }

                // Pick the best edge
                const bestH2h = h2hOptions
                  .filter(o => o.ceq >= 56 && o.conf)
                  .sort((a, b) => b.ceq - a.ceq)[0];

                if (bestH2h) {
                  edges.push({
                    market: 'h2h',
                    side: bestH2h.side as 'home' | 'away',
                    ceq: bestH2h.ceq,
                    confidence: bestH2h.conf!,
                    sideLabel: bestH2h.label,
                    periodLabel: currentPeriodLabel,
                  });
                }
              }

              // TOTALS: Over/under CAN both have edges (different bet dynamics)
              const totalsOverCeq = activeCeq.totals?.over?.ceq;
              const totalsOverConf = activeCeq.totals?.over?.confidence;
              if (totalsOverCeq !== undefined && totalsOverCeq >= 56 && totalsOverConf) {
                const line = activeMarkets?.totals?.line;
                edges.push({
                  market: 'total',
                  side: 'over',
                  ceq: totalsOverCeq,
                  confidence: totalsOverConf,
                  sideLabel: 'Over',
                  lineValue: line !== undefined ? `${line}` : undefined,
                  periodLabel: currentPeriodLabel,
                });
              }
              const totalsUnderCeq = activeCeq.totals?.under?.ceq;
              const totalsUnderConf = activeCeq.totals?.under?.confidence;
              if (totalsUnderCeq !== undefined && totalsUnderCeq >= 56 && totalsUnderConf) {
                const line = activeMarkets?.totals?.line;
                edges.push({
                  market: 'total',
                  side: 'under',
                  ceq: totalsUnderCeq,
                  confidence: totalsUnderConf,
                  sideLabel: 'Under',
                  lineValue: line !== undefined ? `${line}` : undefined,
                  periodLabel: currentPeriodLabel,
                });
              }
            }

            // TEAM TOTALS: Handle team totals edges when team tab is selected
            if (activeTab === 'team' && teamTotalsCeq) {
              const teamTotalsMarkets = marketGroups.teamTotals;

              // Home team over/under
              if (teamTotalsCeq.home?.totals) {
                const homeOverCeq = teamTotalsCeq.home.totals.over?.ceq;
                const homeOverConf = teamTotalsCeq.home.totals.over?.confidence;
                if (homeOverCeq !== undefined && homeOverCeq >= 56 && homeOverConf) {
                  edges.push({
                    market: 'total',
                    side: 'over',
                    ceq: homeOverCeq,
                    confidence: homeOverConf,
                    sideLabel: `${gameData.homeTeam} Over`,
                    lineValue: teamTotalsMarkets?.home?.over?.line !== undefined ? `${teamTotalsMarkets.home.over.line}` : undefined,
                    periodLabel: 'Team Total',
                  });
                }
                const homeUnderCeq = teamTotalsCeq.home.totals.under?.ceq;
                const homeUnderConf = teamTotalsCeq.home.totals.under?.confidence;
                if (homeUnderCeq !== undefined && homeUnderCeq >= 56 && homeUnderConf) {
                  edges.push({
                    market: 'total',
                    side: 'under',
                    ceq: homeUnderCeq,
                    confidence: homeUnderConf,
                    sideLabel: `${gameData.homeTeam} Under`,
                    lineValue: teamTotalsMarkets?.home?.under?.line !== undefined ? `${teamTotalsMarkets.home.under.line}` : undefined,
                    periodLabel: 'Team Total',
                  });
                }
              }

              // Away team over/under
              if (teamTotalsCeq.away?.totals) {
                const awayOverCeq = teamTotalsCeq.away.totals.over?.ceq;
                const awayOverConf = teamTotalsCeq.away.totals.over?.confidence;
                if (awayOverCeq !== undefined && awayOverCeq >= 56 && awayOverConf) {
                  edges.push({
                    market: 'total',
                    side: 'over',
                    ceq: awayOverCeq,
                    confidence: awayOverConf,
                    sideLabel: `${gameData.awayTeam} Over`,
                    lineValue: teamTotalsMarkets?.away?.over?.line !== undefined ? `${teamTotalsMarkets.away.over.line}` : undefined,
                    periodLabel: 'Team Total',
                  });
                }
                const awayUnderCeq = teamTotalsCeq.away.totals.under?.ceq;
                const awayUnderConf = teamTotalsCeq.away.totals.under?.confidence;
                if (awayUnderCeq !== undefined && awayUnderCeq >= 56 && awayUnderConf) {
                  edges.push({
                    market: 'total',
                    side: 'under',
                    ceq: awayUnderCeq,
                    confidence: awayUnderConf,
                    sideLabel: `${gameData.awayTeam} Under`,
                    lineValue: teamTotalsMarkets?.away?.under?.line !== undefined ? `${teamTotalsMarkets.away.under.line}` : undefined,
                    periodLabel: 'Team Total',
                  });
                }
              }
            }
            return edges;
          })()}
          edgeCountBreakdown={edgeCountBreakdown}
        />
      </div>

      <div className="relative mb-4" ref={dropdownRef}>
        <button onClick={() => setIsOpen(!isOpen)} className="flex items-center gap-3 px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg hover:bg-zinc-700/70 transition-all min-w-[200px]">
          <BookIcon bookKey={selectedBook} size={28} /><span className="font-medium text-zinc-100">{selectedConfig.name}</span><svg className={`w-4 h-4 text-zinc-400 ml-auto transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
        </button>
        {isOpen && (<div className="absolute z-50 mt-2 w-64 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl overflow-hidden"><div className="max-h-80 overflow-y-auto">{filteredBooks.map((book) => { const config = BOOK_CONFIG[book] || { name: book, color: '#6b7280' }; const isSelected = book === selectedBook; return (<button key={book} onClick={() => { setSelectedBook(book); setIsOpen(false); }} className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all ${isSelected ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-700/50 text-zinc-300'}`}><BookIcon bookKey={book} size={28} /><span className="font-medium">{config.name}</span>{isSelected && (<svg className="w-4 h-4 ml-auto text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>)}</button>); })}</div></div>)}
      </div>

      {/* Period tabs - hide for exchanges which only have full game */}
      {!(selectedBook === 'kalshi' || selectedBook === 'polymarket') && (
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">{tabs.map((tab) => (<button key={tab.key} onClick={() => handleTabChange(tab.key)} className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${activeTab === tab.key ? 'bg-zinc-700 text-zinc-100' : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'}`}>{tab.label}</button>))}</div>
      )}

      {/* Exchange Markets View (Kalshi/Polymarket) */}
      {(selectedBook === 'kalshi' || selectedBook === 'polymarket') && (
        <ExchangeMarketsSection
          exchangeMarkets={marketGroups.exchangeMarkets || []}
          exchange={selectedBook as 'kalshi' | 'polymarket'}
          homeTeam={gameData.homeTeam}
          awayTeam={gameData.awayTeam}
        />
      )}

      {/* Sportsbook Markets View */}
      {!(selectedBook === 'kalshi' || selectedBook === 'polymarket') && (
        <>
          {activeTab === 'full' && <MarketSection title="Full Game" markets={marketGroups.fullGame} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="fullGame" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '1h' && <MarketSection title="1st Half" markets={marketGroups.firstHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="firstHalf" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '2h' && <MarketSection title="2nd Half" markets={marketGroups.secondHalf} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="secondHalf" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '1q' && <MarketSection title="1st Quarter" markets={marketGroups.q1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="q1" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '2q' && <MarketSection title="2nd Quarter" markets={marketGroups.q2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="q2" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '3q' && <MarketSection title="3rd Quarter" markets={marketGroups.q3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="q3" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '4q' && <MarketSection title="4th Quarter" markets={marketGroups.q4} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="q4" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '1p' && <MarketSection title="1st Period" markets={marketGroups.p1} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="p1" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '2p' && <MarketSection title="2nd Period" markets={marketGroups.p2} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="p2" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === '3p' && <MarketSection title="3rd Period" markets={marketGroups.p3} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} onSelectMarket={handleSelectMarket} selectedMarket={chartMarket} allBookmakers={bookmakers} periodKey="p3" ceqData={activeCeq} sportKey={gameData.sportKey} />}
          {activeTab === 'team' && <TeamTotalsSection teamTotals={marketGroups.teamTotals} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
          {activeTab === 'alt' && <AlternatesSection alternates={marketGroups.alternates} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} gameId={gameData.id} />}
        </>
      )}
    </div>
  );
}