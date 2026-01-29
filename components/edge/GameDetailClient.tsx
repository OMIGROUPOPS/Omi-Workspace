'use client';

import { useState, useRef, useEffect } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive, getGameState } from '@/lib/edge/utils/game-state';

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
}

// Time range options for chart (30M only visible when game is live)
type TimeRange = '30M' | '1H' | '3H' | '6H' | '24H' | 'ALL';

function LineMovementChart({ gameId, selection, lineHistory, selectedBook, homeTeam, awayTeam, viewMode, onViewModeChange, commenceTime }: LineMovementChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ x: number; y: number; value: number; timestamp: Date; index: number } | null>(null);
  // Track which side to show: 'home'/'away' for spreads/ML, 'over'/'under' for totals
  const [trackingSide, setTrackingSide] = useState<'home' | 'away' | 'over' | 'under'>('home');
  // Time range for chart - auto-select based on game state
  const [timeRange, setTimeRange] = useState<TimeRange>('ALL');

  const isProp = selection.type === 'prop';
  const marketType = selection.type === 'market' ? selection.market : 'line';
  const baseValue = selection.line ?? (selection.type === 'market' ? selection.price : 0) ?? 0;

  // Parse game start time for live cutoff indicator
  // Using shared game-state utility for consistent state detection across app
  const gameStartTime = commenceTime ? new Date(commenceTime) : null;
  const isGameLive = commenceTime ? checkGameLive(commenceTime) : false;

  // Auto-select time range for live games on mount
  useEffect(() => {
    if (isGameLive && timeRange === 'ALL') {
      setTimeRange('3H'); // Default to 3H for live games to show recent action
    }
  }, [isGameLive]);

  // For price view, determine which side to show
  const isShowingPrice = viewMode === 'price';
  // Moneyline always shows price (it IS the price), so force line mode display
  const effectiveViewMode = marketType === 'moneyline' ? 'line' : viewMode;

  // Determine which outcome to filter by based on trackingSide
  const getOutcomeFilter = () => {
    if (marketType === 'total') {
      return trackingSide === 'under' ? 'Under' : 'Over';
    }
    // For spreads/moneyline, use team names
    if (trackingSide === 'away' && awayTeam) return awayTeam;
    return homeTeam;
  };

  // Filter line history by selected book AND outcome side
  const filteredHistory = (lineHistory || []).filter(snapshot => {
    const bookMatch = snapshot.book_key === selectedBook || snapshot.book === selectedBook;
    if (!bookMatch) return false;
    if (!snapshot.outcome_type) return true; // no outcome info, keep it
    const targetOutcome = getOutcomeFilter();
    if (targetOutcome) return snapshot.outcome_type === targetOutcome;
    return true;
  });

  const hasRealData = filteredHistory.length > 0;

  let data: { timestamp: Date; value: number }[] = [];

  if (hasRealData) {
    // Use ONLY real data filtered by book - works for both main markets and props
    data = filteredHistory.map(snapshot => ({
      timestamp: new Date(snapshot.snapshot_time),
      // For price view, always use odds; for line view, use line (or odds for moneyline)
      value: effectiveViewMode === 'price'
        ? snapshot.odds
        : (isProp ? snapshot.line : (marketType === 'moneyline' ? snapshot.odds : snapshot.line))
    })).filter(d => d.value !== null && d.value !== undefined);

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

    // For price view, show the line value for context
    if (selection.type === 'market' && selection.line !== undefined) {
      if (marketType === 'spread') {
        const lineStr = selection.line > 0 ? `+${selection.line}` : selection.line.toString();
        return `${selection.label} Price @ ${lineStr}`;
      }
      if (marketType === 'total') {
        return `${selection.label} Price @ ${selection.line}`;
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
          {effectiveViewMode === 'price' && selection.type === 'market' && selection.line !== undefined && (marketType === 'spread' || marketType === 'total') && (
            <span className="px-1.5 py-0.5 bg-amber-500/20 border border-amber-500/30 rounded text-[10px] font-medium text-amber-400">
              @ {marketType === 'spread' ? (selection.line > 0 ? `+${selection.line}` : selection.line) : selection.line}
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
      } catch (e) { /* Backend unavailable, use contextual response */ }
    }
    // Contextual response when AI backend is unavailable
    setTimeout(() => {
      const responses = [
        `For ${chartSelection.label}: Line movement typically indicates where sharp money is going. A move toward ${homeTeam} suggests professional action on the home side.`,
        `${awayTeam} @ ${homeTeam}: Watch for reverse line movement where the line moves opposite to public betting percentages - this often signals sharp action.`,
        `Key factors for this ${chartSelection.type === 'prop' ? 'prop' : 'market'}: injury reports, weather (outdoor sports), and late-breaking news can cause significant line movement.`,
      ];
      const response = responses[Math.floor(Math.random() * responses.length)];
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      setIsLoading(false);
    }, 600);
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

function MarketCell({ value, subValue, edge, onClick, isSelected }: { value: string | number; subValue?: string; edge: number; onClick?: () => void; isSelected?: boolean }) {
  // Simplified cell: just show line and price, no confusing percentages
  const edgeColor = edge >= 0 ? 'text-emerald-400' : 'text-red-400';
  const edgeBg = edge >= 0 ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30';

  return (
    <div onClick={onClick} className={`w-full text-center py-2 px-2 rounded border transition-all cursor-pointer hover:brightness-110 ${edgeBg} ${isSelected ? 'ring-2 ring-emerald-500' : ''}`}>
      <div className="text-sm font-medium text-zinc-100">{value}</div>
      {subValue && <div className="text-xs text-zinc-400">{subValue}</div>}
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
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.away.line)} subValue={formatOdds(markets.spreads.away.price)} edge={markets.spreads.away.edge || 0} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.away.price)} edge={markets.h2h.away.edge || 0} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`O ${markets.totals.line}`} subValue={formatOdds(markets.totals.over.price)} edge={markets.totals.over.edge || 0} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
        </div>
        <div className="grid grid-cols-[1fr,100px,100px,100px] gap-3 items-center">
          <div className="font-medium text-zinc-100 text-sm">{homeTeam}</div>
          {markets.spreads ? <MarketCell value={formatSpread(markets.spreads.home.line)} subValue={formatOdds(markets.spreads.home.price)} edge={markets.spreads.home.edge || 0} onClick={() => onSelectMarket('spread')} isSelected={selectedMarket === 'spread'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.h2h ? <MarketCell value={formatOdds(markets.h2h.home.price)} edge={markets.h2h.home.edge || 0} onClick={() => onSelectMarket('moneyline')} isSelected={selectedMarket === 'moneyline'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
          {markets.totals ? <MarketCell value={`U ${markets.totals.line}`} subValue={formatOdds(markets.totals.under.price)} edge={markets.totals.under.edge || 0} onClick={() => onSelectMarket('total')} isSelected={selectedMarket === 'total'} /> : <div className="text-center py-2 text-zinc-600">-</div>}
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
              return (
                <div key={`${prop.player}-${prop.book}-${idx}`} onClick={() => onSelectProp(prop)} className={`px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-zinc-800/50 transition-colors ${isSelected ? 'bg-blue-500/10 ring-1 ring-blue-500/50' : ''}`}>
                  <div className="flex-1"><div className="font-medium text-zinc-100 text-sm">{prop.player}</div>{line !== null && line !== undefined && <span className="text-xs text-zinc-400">Line: {line}</span>}</div>
                  <div className="flex gap-2">
                    {overOdds && underOdds ? (<>
                      <div className="text-center py-2 px-3 rounded border transition-all min-w-[70px] bg-zinc-800/50 border-zinc-700"><div className="text-sm font-medium text-zinc-100">{formatOdds(overOdds)}</div><div className="text-xs text-zinc-500">Over</div></div>
                      <div className="text-center py-2 px-3 rounded border transition-all min-w-[70px] bg-zinc-800/50 border-zinc-700"><div className="text-sm font-medium text-zinc-100">{formatOdds(underOdds)}</div><div className="text-xs text-zinc-500">Under</div></div>
                    </>) : yesOdds ? (<div className="text-center py-2 px-3 rounded border transition-all min-w-[70px] bg-zinc-800/50 border-zinc-700"><div className="text-sm font-medium text-zinc-100">{formatOdds(yesOdds)}</div><div className="text-xs text-zinc-500">Yes</div></div>) : null}
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

// Demo accounts that get full access to live tracking
// Add your email and investor demo emails here
const DEMO_ACCOUNTS: string[] = [
  'omigroup.ops@outlook.com',
  // 'dean@investor.com',
  // 'investor@example.com',
];

interface GameDetailClientProps {
  gameData: { id: string; homeTeam: string; awayTeam: string; sportKey: string; commenceTime?: string };
  bookmakers: Record<string, any>;
  availableBooks: string[];
  availableTabs?: { fullGame?: boolean; firstHalf?: boolean; secondHalf?: boolean; q1?: boolean; q2?: boolean; q3?: boolean; q4?: boolean; p1?: boolean; p2?: boolean; p3?: boolean; props?: boolean; alternates?: boolean; teamTotals?: boolean };
  userTier?: 'tier_1' | 'tier_2';
  userEmail?: string;
  isDemo?: boolean;
}

// Game state detection now uses shared utility from @/lib/edge/utils/game-state

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

export function GameDetailClient({ gameData, bookmakers, availableBooks, availableTabs, userTier = 'tier_2', userEmail, isDemo = false }: GameDetailClientProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('full');
  const [chartMarket, setChartMarket] = useState<'spread' | 'total' | 'moneyline'>('spread');
  const [selectedProp, setSelectedProp] = useState<any | null>(null);
  const [chartViewMode, setChartViewMode] = useState<ChartViewMode>('line');

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
      // Use our API route which queries Supabase odds_snapshots
      fetch(`/api/odds/prop-history?gameId=${gameData.id}&player=${playerName}&market=${marketType}&book=${selectedBook}`)
        .then(res => res.json())
        .then(data => {
          // Transform to format expected by chart (filter to Over side by default)
          // Don't set outcome_type - it would cause filter mismatch since chart expects team names
          const overSnapshots = (data.snapshots || [])
            .filter((s: any) => s.side === 'Over')
            .map((s: any) => ({
              snapshot_time: s.snapshot_time,
              book_key: s.book_key,
              line: s.line,
              odds: s.odds,
            }));
          setPropHistory(overSnapshots);
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
  const handleSelectProp = (prop: any) => { setSelectedProp(prop); setChartViewMode('line'); };
  const handleSelectMarket = (market: 'spread' | 'total' | 'moneyline') => { setChartMarket(market); setSelectedProp(null); setChartViewMode('line'); };
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
          {!selectedProp && (<div className="flex gap-2 mb-3">{['spread', 'total', 'moneyline'].map((market) => (<button key={market} onClick={() => handleSelectMarket(market as any)} className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${chartMarket === market ? 'bg-emerald-500 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'}`}>{market.charAt(0).toUpperCase() + market.slice(1)}</button>))}</div>)}
          {selectedProp && (<div className="flex gap-2 mb-3 items-center"><button onClick={() => setSelectedProp(null)} className="px-3 py-1.5 rounded text-xs font-medium bg-zinc-800 text-zinc-400 hover:bg-zinc-700 flex items-center gap-1"><svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>Back to Markets</button><span className="px-3 py-1.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400">{selectedProp.player}</span><span className="text-xs text-zinc-500">via {selectedProp.book}</span></div>)}
          {/* Demo mode banner ABOVE the chart to avoid overlap */}
          {showDemoBanner && <DemoModeBanner />}
          <LineMovementChart gameId={gameData.id} selection={chartSelection} lineHistory={getLineHistory()} selectedBook={selectedBook} homeTeam={gameData.homeTeam} awayTeam={gameData.awayTeam} viewMode={chartViewMode} onViewModeChange={setChartViewMode} commenceTime={gameData.commenceTime} />
          {/* Lock overlay for tier 1 users viewing live games */}
          {showLiveLock && <LiveLockOverlay />}
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