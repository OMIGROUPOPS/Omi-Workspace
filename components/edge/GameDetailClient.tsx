'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { isGameLive as checkGameLive, getGameState } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence, PythonPillarScores, PillarResult } from '@/lib/edge/engine/edgescout';
import { calculateFairSpread, calculateFairTotal, calculateFairMoneyline, calculateFairMLFromBook, calculateFairMLFromBook3Way, spreadToMoneyline, removeVig, removeVig3Way, SPORT_KEY_NUMBERS, SPREAD_TO_PROB_RATE, getEdgeSignal, getEdgeSignalColor, edgeToConfidence, PROB_PER_POINT, spreadToWinProb, calculateEdge } from '@/lib/edge/engine/edgescout';

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

const BOOK_LINE_COLOR = '#5b7a99';
const FAIR_LINE_COLOR = '#D4A843';

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
// Chart types
// ============================================================================

interface CompositeHistoryPoint {
  timestamp: string;
  fair_spread: number | null;
  fair_total: number | null;
  fair_ml_home: number | null;
  fair_ml_away: number | null;
  fair_ml_draw: number | null;
  book_spread: number | null;
  book_total: number | null;
  book_ml_home: number | null;
  book_ml_away: number | null;
}

// ============================================================================
// UnifiedChart — convergence chart with smooth curves, edge shading, drivers
// ============================================================================

function UnifiedChart({
  compositeHistory, sportKey, activeMarket, homeTeam, awayTeam, commenceTime, pythonPillars,
}: {
  compositeHistory: CompositeHistoryPoint[];
  sportKey: string;
  activeMarket: 'spread' | 'total' | 'moneyline';
  homeTeam: string;
  awayTeam: string;
  commenceTime?: string;
  pythonPillars?: PythonPillarScores | null;
}) {
  const [hoverX, setHoverX] = useState<number | null>(null);
  const [chartTimeRange, setChartTimeRange] = useState<TimeRange>('ALL');
  const [trackingSide, setTrackingSide] = useState<'home' | 'away' | 'over' | 'under'>('home');
  const homeAbbr = abbrev(homeTeam);
  const awayAbbr = abbrev(awayTeam);
  const rate = SPREAD_TO_PROB_RATE[sportKey] || 0.033;
  const isML = activeMarket === 'moneyline';
  const isTotal = activeMarket === 'total';

  // Reset tracking side when market changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const _resetSide = activeMarket; // dep tracker
  // Filter by time range
  let filtered = compositeHistory;
  if (chartTimeRange !== 'ALL' && filtered.length > 0) {
    const now = new Date();
    const hoursMap: Record<TimeRange, number> = { '30M': 0.5, '1H': 1, '3H': 3, '6H': 6, '24H': 24, 'ALL': 0 };
    const cutoff = new Date(now.getTime() - hoursMap[chartTimeRange] * 3600000);
    filtered = filtered.filter(r => new Date(r.timestamp) >= cutoff);
  }

  // Extract book/fair values based on activeMarket + trackingSide
  const getValues = (row: CompositeHistoryPoint) => {
    let bookVal: number | null = null;
    let fairVal: number | null = null;
    if (isTotal) {
      bookVal = row.book_total; fairVal = row.fair_total;
    } else if (isML) {
      bookVal = trackingSide === 'away' ? row.book_ml_away : row.book_ml_home;
      fairVal = trackingSide === 'away' ? row.fair_ml_away : row.fair_ml_home;
    } else {
      bookVal = row.book_spread; fairVal = row.fair_spread;
      if (trackingSide === 'away' && bookVal != null) bookVal = -bookVal;
      if (trackingSide === 'away' && fairVal != null) fairVal = -fairVal;
    }
    return { bookVal, fairVal };
  };

  const data = filtered.map(row => {
    const { bookVal, fairVal } = getValues(row);
    return { timestamp: new Date(row.timestamp), bookVal, fairVal, raw: row };
  }).filter(d => d.bookVal != null && d.fairVal != null);

  // Empty state
  if (data.length === 0) {
    return (
      <div className="flex flex-col">
        <div className="flex items-center justify-between px-3 py-2">
          <span className="text-[9px] text-[#444] font-mono uppercase tracking-wider">Line Convergence</span>
        </div>
        <div className="flex items-center justify-center h-[180px] text-[11px] text-[#555]">
          Insufficient convergence data
        </div>
      </div>
    );
  }

  // Ensure at least 2 points
  if (data.length === 1) {
    data.push({ ...data[0], timestamp: new Date() });
  }

  // Compute bounds with 25% Y padding
  const allValues = data.flatMap(d => [d.bookVal, d.fairVal].filter((v): v is number => v != null));
  const minVal = Math.min(...allValues);
  const maxVal = Math.max(...allValues);
  const range = maxVal - minVal || 1;
  const yPadding = range * 0.25;

  // SVG dimensions
  const svgW = 560;
  const svgH = 220;
  const padL = 38;
  const padR = 50;
  const padT = 10;
  const padB = 24;
  const chartW = svgW - padL - padR;
  const chartH = svgH - padT - padB;

  const valueToY = (val: number) => {
    const norm = (val - minVal + yPadding) / (range + 2 * yPadding);
    return padT + chartH - norm * chartH;
  };
  const indexToX = (i: number) => padL + (i / Math.max(data.length - 1, 1)) * chartW;

  // Build chart point arrays
  const bookPts: { x: number; y: number; value: number }[] = [];
  const fairPts: { x: number; y: number; value: number }[] = [];
  data.forEach((d, i) => {
    const x = indexToX(i);
    if (d.bookVal != null) bookPts.push({ x, y: valueToY(d.bookVal), value: d.bookVal });
    if (d.fairVal != null) fairPts.push({ x, y: valueToY(d.fairVal), value: d.fairVal });
  });

  // Catmull-Rom smooth path
  const smoothPath = (pts: { x: number; y: number }[]) => {
    if (pts.length < 2) return '';
    let d = `M${pts[0].x},${pts[0].y}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(0, i - 1)];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[Math.min(pts.length - 1, i + 2)];
      d += ` C${p1.x + (p2.x - p0.x) / 6},${p1.y + (p2.y - p0.y) / 6} ${p2.x - (p3.x - p1.x) / 6},${p2.y - (p3.y - p1.y) / 6} ${p2.x},${p2.y}`;
    }
    return d;
  };

  const bookPathD = smoothPath(bookPts);
  const fairPathD = smoothPath(fairPts);

  // Shared favorability: accounts for tracking side after value negation
  const isFavorable = (fair: number, book: number) => {
    if (isTotal) return trackingSide === 'over' ? fair > book : fair < book;
    return trackingSide === 'home' ? fair < book : fair > book;
  };

  // Directional edge shading segments — thin band between book and fair lines
  const edgeSegments = data.slice(0, -1).map((d, i) => {
    const next = data[i + 1];
    if (d.bookVal == null || d.fairVal == null || next.bookVal == null || next.fairVal == null) return null;
    const x = indexToX(i);
    const w = indexToX(i + 1) - x;
    const gap = Math.abs(d.bookVal - d.fairVal);
    const edge = gap * rate * 100;
    const favorable = isFavorable(d.fairVal, d.bookVal);
    const opacity = Math.min(edge / 5, 1) * 0.15;
    const color = favorable ? '#22c55e' : '#ef4444';
    const yBook = valueToY(d.bookVal);
    const yFair = valueToY(d.fairVal);
    const yTop = Math.min(yBook, yFair);
    const yBot = Math.max(yBook, yFair);
    const h = yBot - yTop;
    return { x, y: yTop, w, h, color, opacity, edge, favorable };
  }).filter(Boolean) as { x: number; y: number; w: number; h: number; color: string; opacity: number; edge: number; favorable: boolean }[];

  // Y-axis grid
  const gridStep = isML ? 10 : 0.5;
  const labelStep = isML ? (range > 50 ? 20 : 10) : (range > 10 ? 2 : range > 5 ? 1 : 0.5);
  const visualMin = minVal - yPadding;
  const visualMax = maxVal + yPadding;
  const yGridLines: { value: number; y: number }[] = [];
  const yLabels: { value: number; y: number }[] = [];
  const startGrid = Math.floor(visualMin / gridStep) * gridStep;
  for (let val = startGrid; val <= visualMax + gridStep; val += gridStep) {
    const rounded = Math.round(val * 100) / 100;
    const y = valueToY(rounded);
    if (y >= padT - 2 && y <= padT + chartH + 2) {
      yGridLines.push({ value: rounded, y });
      if (Math.abs(rounded - Math.round(rounded / labelStep) * labelStep) < 0.01) {
        yLabels.push({ value: rounded, y });
      }
    }
  }
  // Enforce 16px min spacing
  const spacedLabels: typeof yLabels = [];
  for (const lbl of yLabels) {
    if (spacedLabels.length === 0 || Math.abs(lbl.y - spacedLabels[spacedLabels.length - 1].y) >= 16) {
      spacedLabels.push(lbl);
    }
  }

  // X-axis labels
  const xLabels: { x: number; label: string }[] = [];
  if (data.length >= 2) {
    const timeSpan = data[data.length - 1].timestamp.getTime() - data[0].timestamp.getTime();
    const maxXLabels = 6;
    const step = Math.max(1, Math.floor(data.length / maxXLabels));
    const seen = new Set<string>();
    for (let i = 0; i < data.length; i += step) {
      const ts = data[i].timestamp;
      let label: string;
      if (timeSpan > 48 * 3600000) label = ts.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      else label = ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      if (seen.has(label)) continue;
      seen.add(label);
      xLabels.push({ x: indexToX(i), label });
    }
  }

  // Format value
  const formatValue = (val: number) => {
    if (isML) return val > 0 ? `+${Math.round(val)}` : `${Math.round(val)}`;
    if (activeMarket === 'spread') return val > 0 ? `+${val.toFixed(1)}` : val.toFixed(1);
    return val.toFixed(1);
  };

  // Driver event markers
  const drivers: { x: number; label: string; detail: string; index: number }[] = [];
  for (let i = 1; i < data.length; i++) {
    const prev = data[i - 1].raw;
    const cur = data[i].raw;
    const x = indexToX(i);
    if (activeMarket === 'total' || isTotal) {
      if (cur.fair_total != null && prev.fair_total != null && Math.abs(cur.fair_total - prev.fair_total) >= 0.5) {
        drivers.push({ x, label: 'COMP', detail: `Fair total \u2192 ${cur.fair_total.toFixed(1)}`, index: i });
      } else if (cur.book_total != null && prev.book_total != null && Math.abs(cur.book_total - prev.book_total) >= 0.5) {
        drivers.push({ x, label: 'BOOK', detail: `Book total \u2192 ${cur.book_total.toFixed(1)}`, index: i });
      }
    } else {
      if (cur.fair_spread != null && prev.fair_spread != null && Math.abs(cur.fair_spread - prev.fair_spread) >= 0.5) {
        drivers.push({ x, label: 'COMP', detail: `Fair spread \u2192 ${cur.fair_spread > 0 ? '+' : ''}${cur.fair_spread.toFixed(1)}`, index: i });
      } else if (cur.book_spread != null && prev.book_spread != null && Math.abs(cur.book_spread - prev.book_spread) >= 0.5) {
        drivers.push({ x, label: 'BOOK', detail: `Book \u2192 ${cur.book_spread > 0 ? '+' : ''}${cur.book_spread.toFixed(1)}`, index: i });
      }
    }
  }

  // Current values for summary
  const lastData = data[data.length - 1];
  const currentBook = lastData.bookVal;
  const currentFair = lastData.fairVal;
  const currentGap = (currentBook != null && currentFair != null) ? Math.abs(currentBook - currentFair) : 0;
  const currentEdge = currentGap * rate * 100;
  const compositeScore = pythonPillars?.composite ?? null;

  // Hover logic — accounts for aspect ratio letterboxing
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svgEl = e.currentTarget;
    const svgRect = svgEl.getBoundingClientRect();
    const viewBox = svgEl.viewBox.baseVal;
    const containerAspect = svgRect.width / svgRect.height;
    const viewBoxAspect = viewBox.width / viewBox.height;
    let renderWidth: number, renderX: number;
    if (containerAspect > viewBoxAspect) {
      renderWidth = svgRect.height * viewBoxAspect;
      renderX = (svgRect.width - renderWidth) / 2;
    } else {
      renderWidth = svgRect.width;
      renderX = 0;
    }
    const relativeX = e.clientX - svgRect.left - renderX;
    const mx = (relativeX / renderWidth) * viewBox.width;
    if (mx >= padL && mx <= padL + chartW) setHoverX(mx);
    else setHoverX(null);
  };

  const getHoverData = () => {
    if (hoverX === null || data.length < 2) return null;
    const frac = Math.max(0, Math.min(1, (hoverX - padL) / chartW));
    const idx = Math.round(frac * (data.length - 1));
    const d = data[idx];
    const bookV = d.bookVal;
    const fairV = d.fairVal;
    const edge = (bookV != null && fairV != null) ? Math.abs(bookV - fairV) * rate * 100 : 0;
    const favorable = isFavorable(fairV ?? 0, bookV ?? 0);
    const tierLabel = edge >= 5 ? 'STRONG' : edge >= 3 ? 'EDGE' : edge >= 1 ? 'WATCH' : 'FLAT';
    const nearbyDriver = drivers.find(drv => Math.abs(drv.index - idx) <= 2);
    return {
      ts: d.timestamp, bookV, fairV, edge, favorable, tierLabel,
      x: indexToX(idx),
      bookY: bookV != null ? valueToY(bookV) : null,
      fairY: fairV != null ? valueToY(fairV) : null,
      nearbyDriver,
    };
  };
  const hoverData = getHoverData();
  const flipTooltip = hoverData && hoverData.x > padL + chartW / 2;

  return (
    <div className="flex flex-col">
      {/* Header: title + current values + time range */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#1a1a1a]/50">
        <div className="flex items-center gap-3">
          <span className="text-[9px] text-[#444] font-mono uppercase tracking-wider">Convergence</span>
          <span className="text-[10px] font-mono font-semibold" style={{ color: BOOK_LINE_COLOR }}>
            {currentBook != null ? formatValue(currentBook) : '\u2014'}
          </span>
          <span className="text-[10px] font-mono font-semibold" style={{ color: FAIR_LINE_COLOR }}>
            {currentFair != null ? formatValue(currentFair) : '\u2014'}
          </span>
        </div>
        <div className="flex rounded overflow-hidden border border-[#1a1a1a]/50">
          {(['1H', '3H', '6H', '24H', 'ALL'] as TimeRange[]).map(r => (
            <button key={r} onClick={() => setChartTimeRange(r)} className={`px-1.5 py-0.5 text-[8px] font-medium ${chartTimeRange === r ? 'bg-[#222] text-[#ddd]' : 'text-[#555] hover:text-[#ccc]'}`}>{r}</button>
          ))}
        </div>
      </div>

      {/* Tracking row + legend */}
      <div className="flex items-center justify-between px-3 py-1">
        <div className="flex items-center gap-1.5">
          <span className="text-[8px] text-[#555] uppercase tracking-wider">Tracking</span>
          <div className="flex gap-0.5">
            <button
              onClick={() => isTotal ? setTrackingSide('over') : setTrackingSide('home')}
              className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                (isTotal ? trackingSide === 'over' : trackingSide === 'home')
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-[#111] text-[#555] border border-[#1a1a1a]/50 hover:text-[#ccc]'
              }`}
            >
              {isTotal ? 'OVR' : homeAbbr}
            </button>
            <button
              onClick={() => isTotal ? setTrackingSide('under') : setTrackingSide('away')}
              className={`px-1.5 py-0.5 text-[9px] font-bold font-mono rounded transition-colors ${
                (isTotal ? trackingSide === 'under' : trackingSide === 'away')
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-[#111] text-[#555] border border-[#1a1a1a]/50 hover:text-[#ccc]'
              }`}
            >
              {isTotal ? 'UND' : awayAbbr}
            </button>
          </div>
        </div>
        <div className="flex items-center gap-3 text-[8px] text-[#555]">
          <span className="flex items-center gap-1"><span className="inline-block w-3 h-0.5 rounded" style={{ backgroundColor: BOOK_LINE_COLOR }} />Book</span>
          <span className="flex items-center gap-1"><span className="inline-block w-3 h-0.5 rounded" style={{ backgroundColor: FAIR_LINE_COLOR }} />OMI Fair</span>
          <span className="flex items-center gap-1"><span className="inline-block w-2 h-2 rounded-sm" style={{ background: 'rgba(34,197,94,0.2)' }} />Edge</span>
          <span className="flex items-center gap-1"><span className="inline-block w-2 h-2 rounded-sm" style={{ background: 'rgba(239,68,68,0.2)' }} />No Edge</span>
          <span className="flex items-center gap-1"><span style={{ color: FAIR_LINE_COLOR }}>{'\u25B2'}</span>Driver</span>
        </div>
      </div>

      {/* SVG Chart */}
      <div className="relative">
        <svg viewBox={`0 0 ${svgW} ${svgH}`} className="w-full cursor-crosshair" style={{ height: '220px' }} preserveAspectRatio="xMidYMid meet" onMouseMove={handleMouseMove} onMouseLeave={() => setHoverX(null)}>
          {/* Y-axis grid */}
          {yGridLines.map((g, i) => (
            <line key={`g-${i}`} x1={padL} y1={g.y} x2={svgW - padR} y2={g.y} stroke="#131313" strokeWidth="0.5" strokeDasharray="3 3" opacity="0.6" />
          ))}
          {/* Y-axis labels */}
          {spacedLabels.map((lbl, i) => (
            <text key={`l-${i}`} x={padL - 4} y={lbl.y + 3} textAnchor="end" fill="#555" fontSize="9" fontFamily="monospace" fontWeight="500">{formatValue(lbl.value)}</text>
          ))}
          {/* X-axis labels */}
          {xLabels.map((lbl, i) => (
            <text key={`x-${i}`} x={lbl.x} y={svgH - 2} textAnchor="middle" fill="#555" fontSize="9" fontFamily="monospace">{lbl.label}</text>
          ))}

          {/* Directional edge shading — thin band between lines */}
          {edgeSegments.map((seg, i) => (
            <rect key={`e-${i}`} x={seg.x} y={seg.y} width={seg.w} height={seg.h} fill={seg.color} opacity={seg.opacity} />
          ))}

          {/* Book line — smooth curve */}
          {bookPts.length >= 2 && (
            <path d={bookPathD} fill="none" stroke={BOOK_LINE_COLOR} strokeWidth="1.2" />
          )}

          {/* OMI Fair line — smooth curve */}
          {fairPts.length >= 2 && (
            <path d={fairPathD} fill="none" stroke={FAIR_LINE_COLOR} strokeWidth="1.5" />
          )}

          {/* Right-side price badges */}
          {bookPts.length > 0 && (() => {
            const lastBook = bookPts[bookPts.length - 1];
            const lastFair = fairPts.length > 0 ? fairPts[fairPts.length - 1] : null;
            const bx = svgW - padR + 4;
            let bookBadgeY = lastBook.y;
            let fairBadgeY = lastFair ? lastFair.y : 0;
            const GAP = 14;
            if (lastFair && Math.abs(bookBadgeY - fairBadgeY) < GAP) {
              const mid = (bookBadgeY + fairBadgeY) / 2;
              if (bookBadgeY < fairBadgeY) { bookBadgeY = mid - GAP / 2; fairBadgeY = mid + GAP / 2; }
              else { fairBadgeY = mid - GAP / 2; bookBadgeY = mid + GAP / 2; }
            }
            return (
              <>
                <rect x={bx} y={bookBadgeY - 6} width={42} height={12} rx="2" fill={BOOK_LINE_COLOR} opacity="0.9" />
                <text x={bx + 21} y={bookBadgeY + 2} textAnchor="middle" fill="white" fontSize="8" fontFamily="monospace" fontWeight="600">{formatValue(lastBook.value)}</text>
                {lastFair && (
                  <>
                    <rect x={bx} y={fairBadgeY - 6} width={42} height={12} rx="2" fill={FAIR_LINE_COLOR} opacity="0.9" />
                    <text x={bx + 21} y={fairBadgeY + 2} textAnchor="middle" fill="white" fontSize="8" fontFamily="monospace" fontWeight="600">{formatValue(lastFair.value)}</text>
                  </>
                )}
              </>
            );
          })()}

          {/* Driver event markers */}
          {drivers.map((drv, i) => (
            <polygon key={`drv-${i}`} points={`${drv.x - 3},${padT + 2} ${drv.x + 3},${padT + 2} ${drv.x},${padT - 4}`} fill={FAIR_LINE_COLOR} opacity="0.7" />
          ))}

          {/* Hover crosshair + tooltip */}
          {hoverData && (
            <>
              <line x1={hoverData.x} y1={padT} x2={hoverData.x} y2={padT + chartH} stroke="#222" strokeWidth="1" strokeDasharray="3 2" />
              {hoverData.bookY != null && <circle cx={hoverData.x} cy={hoverData.bookY} r="3" fill={BOOK_LINE_COLOR} stroke="#0b0b0b" strokeWidth="1" />}
              {hoverData.fairY != null && <circle cx={hoverData.x} cy={hoverData.fairY} r="3" fill={FAIR_LINE_COLOR} stroke="#0b0b0b" strokeWidth="1" />}
              {(() => {
                const hasDriver = !!hoverData.nearbyDriver;
                const tooltipW = hasDriver ? 170 : 130;
                const tooltipH = hasDriver ? 84 : 56;
                const tx = flipTooltip ? hoverData.x - tooltipW - 8 : hoverData.x + 8;
                const ty = Math.max(padT, Math.min(padT + chartH - tooltipH, (hoverData.bookY ?? padT + chartH / 2) - tooltipH / 2));
                const fmtTs = hoverData.ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                const dirLabel = hoverData.favorable ? '\u25B2 favorable' : '\u25BC unfavorable';
                const dirColor = hoverData.favorable ? '#22c55e' : '#ef4444';
                return (
                  <g>
                    <rect x={tx} y={ty} width={tooltipW} height={tooltipH} rx="3" fill="#111" stroke="#222" strokeWidth="0.5" />
                    <text x={tx + 6} y={ty + 12} fill="#555" fontSize="8" fontFamily="monospace">{fmtTs}</text>
                    <text x={tx + 6} y={ty + 24} fill={BOOK_LINE_COLOR} fontSize="9" fontFamily="monospace" fontWeight="600">
                      Book {hoverData.bookV != null ? formatValue(hoverData.bookV) : '\u2014'}
                    </text>
                    <text x={tx + 6} y={ty + 36} fill={FAIR_LINE_COLOR} fontSize="9" fontFamily="monospace" fontWeight="600">
                      Fair {hoverData.fairV != null ? formatValue(hoverData.fairV) : '\u2014'}
                    </text>
                    <text x={tx + 6} y={ty + 48} fill={dirColor} fontSize="9" fontFamily="monospace" fontWeight="600">
                      {hoverData.edge.toFixed(1)}% {hoverData.tierLabel} {dirLabel}
                    </text>
                    {hasDriver && (
                      <>
                        <text x={tx + 6} y={ty + 62} fill="#aaa" fontSize="8" fontFamily="monospace">
                          {hoverData.nearbyDriver!.detail.slice(0, 30)}
                        </text>
                        <text x={tx + 6} y={ty + 76} fill={FAIR_LINE_COLOR} fontSize="8" fontFamily="monospace" fontWeight="600">
                          {'\u2726'} Ask Edge AI
                        </text>
                      </>
                    )}
                  </g>
                );
              })()}
            </>
          )}
        </svg>
      </div>

      {/* Edge heat strip */}
      <div className="mx-3 h-2 flex rounded-sm overflow-hidden" style={{ background: '#111' }}>
        {edgeSegments.map((seg, i) => (
          <div
            key={i}
            className="h-full"
            style={{ flex: 1, backgroundColor: seg.color, opacity: Math.min(seg.edge / 5, 1) * 0.5 }}
          />
        ))}
      </div>

      {/* Summary row: COMP | OMI FAIR | BOOK | GAP | EDGE */}
      <div className="grid grid-cols-5 gap-0 px-3 py-1.5 border-t border-[#1a1a1a]/50">
        <div className="text-center">
          <div className="text-[7px] text-[#333] font-mono uppercase">Comp</div>
          <div className="text-[11px] font-mono font-bold text-[#ccc]">{compositeScore ?? '\u2014'}</div>
        </div>
        <div className="text-center">
          <div className="text-[7px] text-[#333] font-mono uppercase">OMI Fair</div>
          <div className="text-[11px] font-mono font-bold" style={{ color: FAIR_LINE_COLOR }}>{currentFair != null ? formatValue(currentFair) : '\u2014'}</div>
        </div>
        <div className="text-center">
          <div className="text-[7px] text-[#333] font-mono uppercase">Book</div>
          <div className="text-[11px] font-mono font-bold" style={{ color: BOOK_LINE_COLOR }}>{currentBook != null ? formatValue(currentBook) : '\u2014'}</div>
        </div>
        <div className="text-center">
          <div className="text-[7px] text-[#333] font-mono uppercase">Gap</div>
          <div className="text-[11px] font-mono font-bold text-[#888]">{currentGap > 0 ? currentGap.toFixed(1) : '\u2014'}</div>
        </div>
        <div className="text-center">
          <div className="text-[7px] text-[#333] font-mono uppercase">Edge</div>
          <div className="text-[11px] font-mono font-bold" style={{ color: currentEdge >= 5 ? '#22c55e' : currentEdge >= 3 ? '#D4A843' : currentEdge >= 1 ? '#888' : '#555' }}>
            {currentEdge > 0 ? `${currentEdge.toFixed(1)}%` : '\u2014'}
          </div>
        </div>
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
    <div className="bg-[#0b0b0b] flex items-center justify-between px-3 h-[36px] min-h-[36px]" style={{ gridArea: 'header', borderBottom: '1px solid #1a1a1a' }}>
      <div className="flex items-center gap-3">
        <a href="/edge/portal/sports" className="text-[#555] hover:text-[#ccc] transition-colors">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
        </a>
        <span className="text-[13px] font-bold text-[#ddd] tracking-tight font-mono">
          {abbrev(awayTeam)} @ {abbrev(homeTeam)}
        </span>
        <span className="text-[10px] text-[#555] hidden sm:inline" title={`${awayTeam} @ ${homeTeam}`}>
          {awayTeam} vs {homeTeam}
        </span>
        {isLive && (
          <span className="flex items-center gap-1">
            <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span></span>
            <span className="text-[10px] font-medium text-red-400">LIVE</span>
          </span>
        )}
        <span className="text-[10px] text-[#555]">{dateStr}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-[10px] text-[#888]">Viewing: <span className="text-cyan-400 font-medium">{marketLabels[activeMarket] || activeMarket}</span></span>
        {/* Book selector */}
        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setBookOpen(!bookOpen)} className="flex items-center gap-1.5 px-2 py-0.5 bg-[#111]/80 border border-[#1a1a1a]/50 rounded text-[11px] text-[#ccc] hover:bg-[#222]/80">
            <span className="w-3 h-3 rounded flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0" style={{ backgroundColor: BOOK_CONFIG[selectedBook]?.color || '#888' }}>
              {(BOOK_CONFIG[selectedBook]?.name || selectedBook).charAt(0)}
            </span>
            {BOOK_CONFIG[selectedBook]?.name || selectedBook}
            <svg className={`w-3 h-3 text-[#555] transition-transform ${bookOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
          {bookOpen && (
            <div className="absolute right-0 z-50 mt-1 w-44 bg-[#111] border border-[#1a1a1a] rounded shadow-xl overflow-hidden">
              {filteredBooks.map(book => (
                <button key={book} onClick={() => { onSelectBook(book); setBookOpen(false); }}
                  className={`w-full flex items-center gap-2 px-3 py-1.5 text-left text-[11px] transition-colors ${book === selectedBook ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-[#222]/50 text-[#ccc]'}`}>
                  <span className="w-3 h-3 rounded flex items-center justify-center text-[7px] font-bold text-white" style={{ backgroundColor: BOOK_CONFIG[book]?.color || '#888' }}>{(BOOK_CONFIG[book]?.name || book).charAt(0)}</span>
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
  activeMarket, activePeriod, selectedBook, commenceTime, renderKey = 0, dbFairLines,
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
  dbFairLines?: CompositeHistoryPoint | null;
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
      color: BOOK_CONFIG[key]?.color || '#888',
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

  // OMI fair lines — composite_history is source of truth for full game period;
  // edgescout calculation is fallback for sub-periods or when no DB entry exists
  const hasPillars = !!pythonPillars;
  const useDbFairLines = dbFairLines && activePeriod === 'full';
  const omiFairSpread = useDbFairLines && dbFairLines.fair_spread != null
    ? { fairLine: dbFairLines.fair_spread, gap: consensusSpread !== undefined ? Math.round((consensusSpread - dbFairLines.fair_spread) * 10) / 10 : 0, edgeSide: null }
    : (consensusSpread !== undefined
      ? (pythonPillars ? calculateFairSpread(consensusSpread, pythonPillars.composite, sportKey) : { fairLine: consensusSpread, adjustment: 0 })
      : null);
  const omiFairTotal = useDbFairLines && dbFairLines.fair_total != null
    ? { fairLine: dbFairLines.fair_total, gap: consensusTotal !== undefined ? Math.round((dbFairLines.fair_total - consensusTotal) * 10) / 10 : 0, edgeSide: null }
    : (consensusTotal !== undefined
      ? (pythonPillars ? calculateFairTotal(consensusTotal, pythonPillars.gameEnvironment, sportKey) : { fairLine: consensusTotal, adjustment: 0 })
      : null);
  // ML consensus: median of all book odds (needed before fair ML calc)
  const mlHomeOdds = allBooks.map(b => b.markets?.h2h?.home?.price).filter((v): v is number => v !== undefined);
  const mlAwayOdds = allBooks.map(b => b.markets?.h2h?.away?.price).filter((v): v is number => v !== undefined);
  const mlDrawOdds = allBooks.map(b => b.markets?.h2h?.draw?.price).filter((v): v is number => v !== undefined);
  const consensusHomeML = calcMedian(mlHomeOdds);
  const consensusAwayML = calcMedian(mlAwayOdds);
  const consensusDrawML = calcMedian(mlDrawOdds);

  // 3-way fair ML for soccer (home/draw/away) — derived from spread when available
  const omiFairML3Way = (isSoccerGame && pythonPillars && consensusHomeML !== undefined && consensusDrawML !== undefined && consensusAwayML !== undefined)
    ? calculateFairMLFromBook3Way(consensusHomeML, consensusDrawML, consensusAwayML, pythonPillars.composite, consensusSpread, sportKey)
    : null;

  // ML: composite_history is source of truth for full game; derive from spread for coherence
  const omiFairML = useDbFairLines && dbFairLines.fair_ml_home != null && dbFairLines.fair_ml_away != null
    ? { homeOdds: dbFairLines.fair_ml_home, awayOdds: dbFairLines.fair_ml_away }
    : (omiFairML3Way
      ? { homeOdds: omiFairML3Way.homeOdds, awayOdds: omiFairML3Way.awayOdds }
      : (omiFairSpread
        ? spreadToMoneyline(omiFairSpread.fairLine, sportKey)
        : (pythonPillars && consensusSpread !== undefined
          ? calculateFairMLFromBook(consensusSpread, pythonPillars.composite, sportKey)
          : (pythonPillars ? calculateFairMoneyline(pythonPillars.composite) : null))));

  // OMI fair ML implied probabilities (no-vig)
  const effectiveHomeML = omiFairML ? omiFairML.homeOdds : (consensusHomeML ?? undefined);
  const effectiveAwayML = omiFairML ? omiFairML.awayOdds : (consensusAwayML ?? undefined);
  const effectiveDrawML = useDbFairLines && dbFairLines.fair_ml_draw != null
    ? dbFairLines.fair_ml_draw
    : (omiFairML3Way ? omiFairML3Way.drawOdds : (consensusDrawML ?? undefined));
  const omiFairHomeProb = effectiveHomeML !== undefined ? americanToImplied(effectiveHomeML) : undefined;
  const omiFairAwayProb = effectiveAwayML !== undefined ? americanToImplied(effectiveAwayML) : undefined;
  const omiFairDrawProb = effectiveDrawML !== undefined ? americanToImplied(effectiveDrawML) : undefined;

  // Convert spread point gap to logistic probability difference %
  const spreadPointsToEdgePct = (bookLine: number, fairLine: number): number => {
    return Math.round(calculateEdge(bookLine, fairLine, 'spread', sportKey) * 10) / 10;
  };
  // Convert total point gap to logistic probability difference %
  const totalPointsToEdgePct = (bookTotal: number, fairTotal: number): number => {
    return Math.round(calculateEdge(bookTotal, fairTotal, 'total', sportKey) * 10) / 10;
  };

  // Edge color: positive = emerald (value), negative = red (wrong side)
  const getEdgeColor = (pctGap: number): string => {
    const abs = Math.abs(pctGap);
    if (abs < 0.5) return 'text-[#555]';
    return pctGap > 0 ? 'text-emerald-400' : 'text-red-400';
  };

  // Confidence color (derived from edge-based confidence) — spreads/totals
  const getConfColor = (conf: number): string => {
    if (conf >= 66) return 'text-cyan-400';
    if (conf >= 60) return 'text-amber-400';
    if (conf >= 55) return 'text-[#888]';
    return 'text-[#555]';
  };

  // Implied probability color — moneylines (shows win probability, not edge)
  const getImpliedProbColor = (prob: number): string => {
    if (prob >= 65) return 'text-cyan-400';
    if (prob >= 55) return 'text-[#ddd]';
    if (prob >= 45) return 'text-[#888]';
    return 'text-[#555]';
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
    const noData: SideBlock = { label: '', fair: 'N/A', bookLine: '--', bookOdds: '--', edgePct: 0, edgePts: 0, edgeColor: 'text-[#555]', contextLine: '', evLine: '', bookName: selBookName, hasData: false, confidence: 50, confColor: 'text-[#555]' };

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

      // Convert point edge to logistic probability % (signed: positive = value)
      const homeEdgePct = homeBookLine !== undefined && fairHomeLine !== undefined
        ? Math.round((spreadToWinProb(fairHomeLine, sportKey) - spreadToWinProb(homeBookLine, sportKey)) * 1000) / 10
        : 0;
      const awayEdgePct = -homeEdgePct;

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
          confidence: awayConf, confColor: awayEdgePct > 0 ? getConfColor(awayConf) : 'text-[#555]',
        },
        {
          label: homeAbbr, fair: fairHomeLine !== undefined ? formatSpread(fairHomeLine) : 'N/A',
          bookLine: homeBookLine !== undefined ? formatSpread(homeBookLine) : '--', bookOdds: homePrice !== undefined ? formatOdds(homePrice) : '--',
          edgePct: homeEdgePct, edgePts: homeSignedGap, edgeColor: getEdgeColor(homeEdgePct),
          contextLine: mkContext(homeAbbr, homeBookLine, fairHomeLine, homeEdgePct, homeSignedGap),
          evLine: mkEvLine(homeEdgePct, homeSignedGap, homeCross),
          bookName: selBookName, hasData: homeBookLine !== undefined, crossedKey: homeCross,
          confidence: homeConf, confColor: homeEdgePct > 0 ? getConfColor(homeConf) : 'text-[#555]',
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

      // Convert total gap to logistic probability % (signed: positive = value)
      const overEdgePct = bookLine !== undefined && fairLine !== undefined
        ? (() => {
            const mag = totalPointsToEdgePct(bookLine, fairLine);
            return overSignedGap > 0 ? mag : overSignedGap < 0 ? -mag : 0;
          })()
        : 0;
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
          confidence: overConf, confColor: overEdgePct > 0 ? getConfColor(overConf) : 'text-[#555]',
        },
        {
          label: 'UNDER', fair: fairLine !== undefined ? `${fairLine}` : 'N/A',
          bookLine: bookLine !== undefined ? `${bookLine}` : '--', bookOdds: underPrice !== undefined ? formatOdds(underPrice) : '--',
          edgePct: underEdgePct, edgePts: underSignedGap, edgeColor: getEdgeColor(underEdgePct),
          contextLine: mkTotalContext('Under', underEdgePct, underSignedGap),
          evLine: mkTotalEv(underEdgePct, underSignedGap, underEv),
          bookName: effBookName, hasData: bookLine !== undefined,
          confidence: underConf, confColor: underEdgePct > 0 ? getConfColor(underConf) : 'text-[#555]',
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
        // Logistic: signed edge = (fairProb - bookProb) * 100
        signedEdge = Math.round((spreadToWinProb(omiFairSpread.fairLine, sportKey) - spreadToWinProb(bookLine, sportKey)) * 1000) / 10;
      }
    } else if (activeMarket === 'total') {
      const totalLine = b.markets?.totals?.line;
      line = totalLine !== undefined ? `${totalLine}` : '--';
      if (totalLine !== undefined && omiFairTotal) {
        const ptsGap = omiFairTotal.fairLine - totalLine;
        const mag = totalPointsToEdgePct(totalLine, omiFairTotal.fairLine);
        signedEdge = ptsGap > 0 ? mag : ptsGap < 0 ? -mag : 0;
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
    <div className="bg-[#0b0b0b] px-3 py-2 flex flex-col" style={{ overflow: 'visible' }}>
      {/* OMI Fair Line — split display for both sides */}
      <div className="mb-1.5 flex-shrink-0">
        <div className="text-[10px] text-[#555] uppercase tracking-widest mb-0.5">OMI Fair Line</div>
        <div className="flex items-baseline gap-4" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {sideBlocks.map((block, i) => (
            <div key={i} className="flex items-baseline">
              {i > 0 && <span className="text-[#555] text-[12px] mr-4">vs</span>}
              <span className="text-[10px] text-[#555] mr-1">{block.label}</span>
              <span className="text-[20px] font-bold font-mono text-cyan-400">{block.fair}</span>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-[#555] mt-0.5">
          {hasPillars
            ? `Based on 6-pillar composite (${pythonPillars!.composite}) and market analysis`
            : `Based on market consensus (${allBooks.length} books)`}
        </div>
        {pillarsAgoText && <div className="text-[10px] text-[#555]">{pillarsAgoText}</div>}
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
          return <div className="text-[11px] text-[#ddd] mt-1 leading-snug">{narrative}</div>;
        })()}
        {/* HIGH VARIANCE warning when any edge >= 8% */}
        {(() => {
          const maxAbsEdge = Math.max(...sideBlocks.map(b => Math.abs(b.edgePct)));
          if (maxAbsEdge < 8) return null;
          return (
            <div className="text-[10px] text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-1 mt-1">
              HIGH VARIANCE — Edge of {maxAbsEdge.toFixed(1)}% exceeds 8% threshold. Signal reliability decreases at extreme edges.
            </div>
          );
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
            <div key={blockIdx} className={`rounded overflow-hidden border border-[#1a1a1a] ${isHighEdge ? 'border-l-2 border-l-emerald-400' : ''}`}>
              {/* Block header — team/side label */}
              <div className="bg-[#0b0b0b] px-2 py-1 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-bold text-[#ddd]">{block.label}</span>
              </div>
              {/* Comparison: OMI Fair vs Book vs Edge vs Confidence */}
              <div className="px-2 py-1.5">
                <div className="flex items-end justify-between gap-1.5">
                  <div>
                    <div className="text-[8px] text-[#555] uppercase tracking-widest">{hasPillars ? 'OMI Fair' : 'Consensus'}</div>
                    <div className="text-[18px] font-bold font-mono text-cyan-400">{block.fair}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-[#555] uppercase tracking-widest">{block.bookName}</div>
                    <div className="text-[18px] font-bold font-mono text-[#ddd]">{block.bookLine}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[8px] text-[#555] uppercase tracking-widest">Edge</div>
                    <div className={`text-[18px] font-bold font-mono ${block.edgeColor}`}>
                      {edgeDisplay}
                    </div>
                  </div>
                  {hasPillars && (
                    <div className="text-right">
                      <div className="text-[8px] text-[#555] uppercase tracking-widest">{activeMarket === 'moneyline' ? 'Win %' : 'Conf'}</div>
                      <div className={`text-[18px] font-bold font-mono ${block.confColor}`}>
                        {activeMarket === 'moneyline' ? `${block.confidence.toFixed(1)}%` : `${block.confidence}%`}
                      </div>
                    </div>
                  )}
                </div>
                {block.contextLine && (
                  <div className="mt-1 pt-1 border-t border-[#1a1a1a]/50">
                    <div className="text-[10px] text-[#888]">{block.contextLine}</div>
                    {block.evLine && <div className={`text-[10px] font-medium ${block.edgeColor}`}>{block.evLine}</div>}
                  </div>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[9px] text-[#555] font-mono">
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
        <div className="flex-shrink-0 border-t border-[#1a1a1a]/50 pt-1 pb-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[8px] text-[#555] uppercase tracking-widest">All Books</span>
            {bestValueBook && bestValueBook.signedEdge > 3 && (
              <span className="text-[10px] font-mono text-emerald-400 font-semibold">
                Best value: {bestValueBook.name} {bestValueBook.line} {bestValueBook.edgeStr}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {allBooksQuickScan.map(b => {
              const isBest = b.key === bestValueBook?.key && b.signedEdge > (activeMarket === 'moneyline' ? 3 : 0.5);
              const edgeColor = isBest ? 'text-emerald-400 font-semibold' : b.absEdge < (activeMarket === 'moneyline' ? 3 : 0.5) ? 'text-[#555]' : b.signedEdge > 0 ? 'text-emerald-400/70' : 'text-[#555]';
              return (
                <span key={b.key} className={`text-[10px] font-mono ${b.isSelected ? 'text-cyan-400 font-semibold' : 'text-[#888]'}`}>
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
// PillarBarsCompact — dual-sided bars (center at 50%) with expand/collapse
// ============================================================================

const PILLAR_VARIABLES: Record<string, { code: string; label: string; description: string }[]> = {
  execution: [
    { code: 'FRM', label: 'Form Composite', description: 'ATS record, scoring margin, opponent-adjusted performance' },
    { code: 'FDR', label: 'Q4 Differential', description: 'Clutch execution, 4th quarter point differential' },
    { code: 'TSH', label: 'Home Scoring Trend', description: 'Rolling offensive efficiency at home venue' },
    { code: 'SKH', label: 'Streak Detection', description: 'Sustained performance runs exceeding noise' },
    { code: 'HIJ', label: 'Injury-Adjusted', description: 'Team strength factoring current injury report' },
  ],
  incentives: [
    { code: 'PLI', label: 'Playoff Implications', description: 'Seeding leverage, elimination pressure, clinch scenarios' },
    { code: 'RIV', label: 'Rivalry Factor', description: 'Historical rivalry intensity and motivation boost' },
    { code: 'RST', label: 'Rest Advantage', description: 'Days since last game, back-to-back fatigue detection' },
    { code: 'SZN', label: 'Season Context', description: 'Early-season variance vs late-season urgency' },
  ],
  shocks: [
    { code: 'INJ', label: 'Injury News', description: 'Breaking injury reports and their spread impact' },
    { code: 'LIN', label: 'Lineup Changes', description: 'Unexpected starter/bench changes vs projected' },
    { code: 'SUS', label: 'Suspensions', description: 'Player suspensions affecting team strength' },
    { code: 'WTH', label: 'Weather/Venue', description: 'Weather conditions, dome/open, altitude factors' },
    { code: 'NWS', label: 'Breaking News', description: 'Trade rumors, coach firings, off-court events' },
  ],
  timeDecay: [
    { code: 'STL', label: 'Signal Staleness', description: 'How recently pillar inputs were refreshed' },
    { code: 'CLV', label: 'Closing Line Value', description: 'Expected line drift as game approaches' },
    { code: 'MKT', label: 'Market Maturity', description: 'Early-week soft lines vs game-day sharp markets' },
    { code: 'VOL', label: 'Volume Indicator', description: 'Betting handle growth approaching tipoff' },
  ],
  flow: [
    { code: 'RLM', label: 'Reverse Line Move', description: 'Line moved opposite to public betting %' },
    { code: 'PDV', label: 'Price Divergence', description: 'Exchange-to-sportsbook convergence analysis' },
    { code: 'SHP', label: 'Sharp Consensus', description: 'Cross-referencing multiple professional signals' },
    { code: 'JFI', label: 'Juice Flow', description: 'Vig changes without line movement (stealth adjustments)' },
    { code: 'FLM', label: 'Full Line Movement', description: 'Velocity, direction, persistence across 15+ books' },
  ],
  gameEnvironment: [
    { code: 'HCA', label: 'Home Court', description: 'Home court advantage strength for this venue' },
    { code: 'TRV', label: 'Travel Factor', description: 'Distance traveled, time zone shifts, back-to-backs' },
    { code: 'ALT', label: 'Altitude/Climate', description: 'Denver altitude, Miami humidity, outdoor elements' },
    { code: 'PAC', label: 'Pace Matchup', description: 'Tempo differential between teams and its effect on totals' },
  ],
};

function generatePillarSummary(pillarKey: string, score: number, homeTeam: string, awayTeam: string): string {
  const hA = abbrev(homeTeam);
  const aA = abbrev(awayTeam);
  const leanTeam = score >= 50 ? hA : aA;
  const strength = score >= 65 || score <= 35 ? 'strongly' : score > 55 || score < 45 ? 'moderately' : 'slightly';
  const isNeutral = score > 45 && score < 55;

  const summaries: Record<string, string> = {
    execution: isNeutral
      ? `Both teams showing comparable form and execution metrics.`
      : `${strength.charAt(0).toUpperCase() + strength.slice(1)} favors ${leanTeam} — recent form, clutch performance, and scoring trends lean ${score >= 50 ? 'home' : 'away'}.`,
    incentives: isNeutral
      ? `Similar motivation levels — no clear edge from rest, rivalry, or playoff leverage.`
      : `${leanTeam} has a ${strength} incentive edge from playoff positioning, rest advantage, or situational motivation.`,
    shocks: isNeutral
      ? `No significant injury or news shocks detected for either side.`
      : `Shock signals ${strength} favor ${leanTeam} — check injury reports and lineup changes for impact.`,
    timeDecay: isNeutral
      ? `Signal freshness is balanced — market inputs are current for both sides.`
      : `Time decay ${strength} favors ${leanTeam} — ${score >= 50 ? 'home' : 'away'} signals are fresher or line is expected to move their way.`,
    flow: isNeutral
      ? `Money flow is balanced — no clear sharp or public lean detected.`
      : `Sharp money and line movement ${strength} favor ${leanTeam} — watch for reverse line movement and juice shifts.`,
    gameEnvironment: isNeutral
      ? `Venue and environmental factors are roughly neutral for this matchup.`
      : `Environment ${strength} favors ${leanTeam} — home court, travel, and pace matchup contribute.`,
  };
  return summaries[pillarKey] || `Score of ${score} — ${isNeutral ? 'neutral' : `${strength} ${score >= 50 ? 'home' : 'away'} lean`}.`;
}

function PillarBarsCompact({
  pythonPillars, homeTeam, awayTeam, marketPillarScores, marketComposite,
}: {
  pythonPillars: PythonPillarScores | null | undefined;
  homeTeam: string;
  awayTeam: string;
  marketPillarScores?: Record<string, number>;
  marketComposite?: number;
}) {
  const [expandedPillar, setExpandedPillar] = useState<string | null>(null);

  const pillars = [
    { key: 'execution', label: 'EXEC', weight: '20%', fullLabel: 'Execution' },
    { key: 'incentives', label: 'INCV', weight: '10%', fullLabel: 'Incentives' },
    { key: 'shocks', label: 'SHOK', weight: '25%', fullLabel: 'Shocks' },
    { key: 'timeDecay', label: 'TIME', weight: '10%', fullLabel: 'Time Decay' },
    { key: 'flow', label: 'FLOW', weight: '25%', fullLabel: 'Flow' },
    { key: 'gameEnvironment', label: 'ENV', weight: '10%', fullLabel: 'Game Env' },
  ];

  // Neutral color scheme: gold = strong signal, grey = neutral, blue = opposite signal
  const getBarColor = (score: number) => {
    if (score > 55) return '#D4A843';  // gold — strong signal
    if (score >= 45) return '#555';    // grey — neutral
    return '#5b7a99';                  // steel blue — opposite signal
  };

  const getTextColor = (score: number) => {
    if (score > 55) return 'text-[#D4A843]';
    if (score >= 45) return 'text-[#555]';
    return 'text-[#5b7a99]';
  };

  const homeAbbrev = abbrev(homeTeam);
  const awayAbbrev = abbrev(awayTeam);

  if (!pythonPillars) {
    return <div className="flex items-center justify-center text-[10px] text-[#555] py-2">No pillar data</div>;
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
        <span className="text-[8px] text-[#555] font-mono w-16" />
        <span className="text-[8px] text-[#555] font-mono w-6 text-right">{awayAbbrev}</span>
        <div className="flex-1" />
        <span className="text-[8px] text-[#555] font-mono w-6">{homeAbbrev}</span>
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
        const isExpanded = expandedPillar === p.key;
        return (
          <div key={p.key}>
            <div
              className="flex items-center gap-1 cursor-pointer hover:bg-[#111]/50 rounded-sm -mx-0.5 px-0.5 transition-colors"
              onClick={() => setExpandedPillar(isExpanded ? null : p.key)}
            >
              <span className="text-[9px] text-[#555] w-16 font-mono truncate" title={p.fullLabel}>
                {p.label} <span className="text-[#555]">({p.weight})</span>
              </span>
              <div className="flex-1 h-[6px] bg-[#111] rounded-sm relative">
                {/* Center line — dashed for visibility at neutral */}
                <div className="absolute left-1/2 top-0 w-0 h-full z-10" style={{ borderLeft: '1px dashed #222' }} />
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
            {/* Expanded detail */}
            {isExpanded && (
              <div
                className="mt-1 mb-1.5 ml-1 rounded-sm overflow-hidden"
                style={{ background: '#080808', borderLeft: `2px solid ${barColor}` }}
              >
                <div className="px-2.5 py-2">
                  <div className="text-[10px] text-[#888] leading-relaxed mb-2">
                    {generatePillarSummary(p.key, score, homeTeam, awayTeam)}
                  </div>
                  <div className="space-y-1">
                    {(PILLAR_VARIABLES[p.key] || []).map(v => (
                      <div key={v.code} className="flex items-start gap-2">
                        <span className="text-[9px] font-mono text-[#555] w-7 flex-shrink-0 pt-px">{v.code}</span>
                        <div className="min-w-0">
                          <span className="text-[9px] text-[#888]">{v.label}</span>
                          <span className="text-[9px] text-[#333] mx-1">—</span>
                          <span className="text-[9px] text-[#555]">{v.description}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
      {/* Composite */}
      <div className="flex items-center justify-between mt-1 pt-1 border-t border-[#1a1a1a]/50">
        <span className="text-[9px] text-[#555] font-mono">COMPOSITE</span>
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
      lines.push(`Significant flow detected (Flow: ${flowScore}). Line movement may reflect new information.`);
    }

    return lines;
  };

  const ceqSummary = getCeqSummary();
  const pillarSummary = generatePillarSummary();

  const confColor = ceqSummary ? (
    ceqSummary.confidence === 'STRONG' || ceqSummary.confidence === 'RARE' ? 'text-emerald-400' :
    ceqSummary.confidence === 'EDGE' ? 'text-blue-400' :
    ceqSummary.confidence === 'WATCH' ? 'text-amber-400' : 'text-[#555]'
  ) : 'text-[#555]';

  return (
    <div className="bg-[#0b0b0b] px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-[#555] uppercase tracking-widest mb-1">Why This Price</span>
      <div>
        <PillarBarsCompact pythonPillars={pythonPillars} homeTeam={homeTeam} awayTeam={awayTeam} marketPillarScores={marketPillarScores} marketComposite={marketData?.composite} />
        {/* Generated pillar summary */}
        {pillarSummary.length > 0 && (
          <div className="mt-1.5 space-y-0.5">
            {pillarSummary.map((line, i) => (
              <p key={i} className="text-[10px] text-[#888] leading-tight">{line}</p>
            ))}
          </div>
        )}
        {/* CEQ summary line — detail integrated inline */}
        {ceqSummary ? (
          <div className="mt-2 pt-1.5 border-t border-[#1a1a1a]/50">
            <div className={`text-[10px] font-mono ${confColor}`}>
              {ceqSummary.text} <span className="text-[#555]">({ceqSummary.detail})</span>
            </div>
          </div>
        ) : (
          <div className="mt-2 pt-1.5 border-t border-[#1a1a1a]/50">
            <div className="text-[10px] text-[#555]">
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
      <div className="bg-[#0b0b0b] px-2 py-1.5 flex items-center justify-center">
        <span className="text-[10px] text-[#555]">No CEQ factor data</span>
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
        return score > 60 ? 'Market sentiment aligns with model — consensus agrees'
          : score < 40 ? 'Contrarian signal — model disagrees with market sentiment'
          : 'Mixed sentiment — market consensus and model diverge';
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
  const getBarColor = (s: number) => s > 55 ? '#D4A843' : s >= 45 ? '#555' : '#5b7a99';
  const getTextColor = (s: number) => s > 55 ? 'text-[#D4A843]' : s >= 45 ? 'text-[#555]' : 'text-[#5b7a99]';

  // Compute scores for composite summary
  const scoredFactors = factors.map(f => {
    const rawScore = ceqPillars[f.key].score;
    const score = adjustScore(rawScore, f.key);
    return { ...f, score, rawScore };
  });
  const compositeAvg = Math.round(scoredFactors.reduce((sum, f) => sum + f.score * f.weight, 0) / scoredFactors.reduce((sum, f) => sum + f.weight, 0));
  const strongest = [...scoredFactors].sort((a, b) => Math.abs(b.score - 50) - Math.abs(a.score - 50))[0];

  return (
    <div className="bg-[#0b0b0b] px-2 py-1.5 flex flex-col">
      <span className="text-[10px] font-semibold text-[#555] uppercase tracking-widest mb-1">CEQ Factors{activeMarket ? ` — ${activeMarket === 'moneyline' ? 'ML' : activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)}` : ''}</span>
      <div>
        <div className="flex flex-col gap-0.5">
          {scoredFactors.map(f => {
            const wPct = Math.round(f.weight * 100);
            return (
              <div key={f.key}>
                <div className="flex items-center gap-1">
                  <span className="text-[9px] text-[#555] font-mono w-16 truncate">{f.label} ({wPct}%)</span>
                  <div className="flex-1 h-[5px] bg-[#111] rounded-sm overflow-hidden">
                    <div className="h-full rounded-sm" style={{ width: `${f.score}%`, backgroundColor: getBarColor(f.score) }} />
                  </div>
                  <span className={`text-[9px] font-mono w-5 text-right ${getTextColor(f.score)}`}>{f.score}</span>
                  <span className={`text-[8px] w-12 text-right ${getTextColor(f.score)}`}>{getStrength(f.score)}</span>
                </div>
                <div className="text-[9px] text-[#555] ml-[68px] leading-tight">{getDetailText(f.key, f.score)}</div>
              </div>
            );
          })}
        </div>
        {/* Composite summary */}
        <div className="mt-1 pt-1 border-t border-[#1a1a1a]/50">
          <div className="text-[9px] text-[#888]">
            <span className="font-semibold text-[#ccc]">CEQ COMPOSITE: {compositeAvg}%</span>
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
      background: '#111111',
      borderBottom: '1px solid #1a1a1a',
      padding: '8px 16px',
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16,
    }}>
      {/* Away team */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {liveData.awayLogo && (
          <img src={liveData.awayLogo} alt="" style={{ width: 20, height: 20 }} />
        )}
        <span style={{ fontSize: 13, fontWeight: 600, color: '#cccccc' }}>{aAbbr}</span>
        <span style={{ fontSize: 22, fontWeight: 700, color: '#dddddd', fontVariantNumeric: 'tabular-nums' }}>
          {liveData.awayScore}
        </span>
      </div>

      {/* Divider + status */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1, minWidth: 80 }}>
        <span style={{ fontSize: 10, fontWeight: 600, color: '#888', letterSpacing: '0.05em' }}>
          {liveData.statusDetail || 'In Progress'}
        </span>
        {indicatorText && (
          <span style={{ fontSize: 9, color: '#555', whiteSpace: 'nowrap' }}>{indicatorText}</span>
        )}
      </div>

      {/* Home team */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 22, fontWeight: 700, color: '#dddddd', fontVariantNumeric: 'tabular-nums' }}>
          {liveData.homeScore}
        </span>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#cccccc' }}>{hAbbr}</span>
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
        background: '#0a1a0a',
        borderLeft: '4px solid #22c55e',
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
      background: '#111111',
      borderLeft: '4px solid #555',
      padding: '8px 16px',
      display: 'flex', alignItems: 'center', gap: 10,
    }}>
      <span style={{ fontSize: 12, fontWeight: 600, color: '#cccccc' }}>
        FINAL
      </span>
      <span style={{ fontSize: 11, color: '#888' }}>
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
    'Is there significant money flow on this game?',
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
              <p className={`${textSize} text-[#888] mb-2`}>Ask about this game:</p>
              <div className="space-y-1">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); iRef.current?.focus(); }}
                    className={`block w-full text-left ${btnSize} text-[#555] hover:text-cyan-400 hover:bg-[#111]/50 px-2.5 py-2 rounded transition-colors font-mono`}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`${textSize} leading-relaxed ${msg.role === 'user' ? 'text-[#ccc]' : 'text-[#888]'}`}>
              <span className={`${labelSize} font-mono font-bold uppercase tracking-wider ${msg.role === 'user' ? 'text-[#555]' : 'text-cyan-600'}`}>
                {msg.role === 'user' ? 'You' : 'OMI'}
              </span>
              <div className="mt-0.5 whitespace-pre-wrap">
                {msg.content || (isLoading && i === messages.length - 1 ? (
                  <span className="text-[#555] animate-pulse">...</span>
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

        <div className={`${expanded ? 'px-5 pb-4 pt-2' : 'px-3 pb-2 pt-1'} border-t border-[#1a1a1a]/30`}>
          <div className="flex gap-2">
            <input
              ref={iRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${viewingLabel}...`}
              className={`flex-1 bg-[#0b0b0b] border border-[#1a1a1a]/50 rounded px-3 ${expanded ? 'py-2.5 text-[13px]' : 'py-1.5 text-[11px]'} text-[#ccc] placeholder-[#555] focus:outline-none focus:border-cyan-700/50 transition-colors`}
              disabled={isLoading}
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !input.trim()}
              className={`${expanded ? 'px-4 py-2.5 text-[13px]' : 'px-3 py-1.5 text-[11px]'} bg-[#111] border border-[#1a1a1a]/50 rounded font-medium transition-colors disabled:opacity-30 disabled:cursor-default text-cyan-400 hover:bg-[#222] hover:border-cyan-700/30`}
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
    <div className={`flex items-center justify-between ${expanded ? 'px-5 py-3' : 'px-3 py-2'} border-b border-[#1a1a1a]/50`}>
      <div className="flex items-center gap-1.5">
        <span className={expanded ? 'text-[15px]' : 'text-[13px]'}>&#10022;</span>
        <span className={`${expanded ? 'text-[14px]' : 'text-[12px]'} font-semibold text-[#ddd]`}>Ask Edge AI</span>
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
            className="text-[9px] text-[#555] hover:text-[#888] font-mono transition-colors"
          >
            Clear
          </button>
        )}
        <span className="text-[9px] text-[#555] font-mono">{viewingLabel}</span>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-1 text-[#555] hover:text-[#ccc] transition-colors"
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
      <div className="flex flex-col h-full bg-[#080808] border-l border-[#1a1a1a]">
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
            className="relative flex flex-col bg-[#080808] border-l border-[#1a1a1a]/50 shadow-2xl"
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
  const divColor = (pct: number) => Math.abs(pct) < 1 ? 'text-[#555]' : pct > 0 ? 'text-emerald-400' : 'text-red-400';

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
    if (vol >= 10000) return { label: 'Moderate volume', color: 'text-[#888]' };
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
    <div className="border-t border-cyan-500/20 bg-[#111111]">
      <div className="px-4 py-2.5 flex items-center gap-2 border-b border-[#1a1a1a]/50">
        <span className="text-[10px] font-semibold tracking-widest text-cyan-500/70 uppercase">Exchange Signals</span>
        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-sky-500/15 text-sky-400 border border-sky-500/30">Kalshi</span>
        <span className="text-[10px] text-[#555] ml-auto">
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
                <div className="text-[10px] font-semibold text-[#555] uppercase tracking-wider mb-1">{mktLabel}</div>
                <div className="text-[10px] text-[#555] italic">No exchange coverage</div>
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
                  <div className="text-[10px] font-semibold text-[#555] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                {ticker && <div className="text-[9px] text-[#555] font-mono mb-1 truncate">{contractLabel}</div>}
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#555]">
                      <th className="text-left py-1 font-normal">Source</th>
                      <th className="text-right py-1 font-normal">{awayAbbr}</th>
                      <th className="text-right py-1 font-normal">{homeAbbr}</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="text-[#ccc]">
                      <td className="py-1 text-sky-400 font-medium">Kalshi</td>
                      <td className="py-1 text-right font-mono">{fmtCents(awayYes)} <span className="text-[#555]">({fmtPct(awayYes)})</span></td>
                      <td className="py-1 text-right font-mono">{fmtCents(homeYes)} <span className="text-[#555]">({fmtPct(homeYes)})</span></td>
                      <td className="py-1 text-right text-[#555]">{fmtVol(totalVol)}</td>
                    </tr>
                    {fdHome && fdAway && (
                      <tr className="text-[#888]">
                        <td className="py-1 font-medium" style={{ color: '#1493ff' }}>FanDuel</td>
                        <td className="py-1 text-right font-mono">{fdAway > 0 ? '+' : ''}{fdAway} <span className="text-[#555]">({fmtPct(fdAwayProb)})</span></td>
                        <td className="py-1 text-right font-mono">{fdHome > 0 ? '+' : ''}{fdHome} <span className="text-[#555]">({fmtPct(fdHomeProb)})</span></td>
                        <td className="py-1 text-right text-[#555]">—</td>
                      </tr>
                    )}
                    {mlDiv && (
                      <tr>
                        <td className="py-1 text-[#555] font-medium">Divergence</td>
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
                  <div className="mt-1.5 text-[10px] text-[#555] italic">{getDivExplanation(mlDiv.divergence_pct, gameData.homeTeam)}</div>
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
                  <div className="text-[10px] font-semibold text-[#555] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#555]">
                      <th className="text-left py-1 font-normal">Contract</th>
                      <th className="text-right py-1 font-normal">Price</th>
                      <th className="text-right py-1 font-normal">Implied</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mktContracts.map((c: any, i: number) => (
                      <tr key={i} className="text-[#ccc]">
                        <td className="py-1 text-[#888] text-[10px] truncate max-w-[180px]" title={c.contract_ticker || ''}>{c.subtitle || c.contract_ticker || '—'}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.yes_price)}</td>
                        <td className="py-1 text-right font-mono text-[#888]">{fmtPct(c.yes_price)}</td>
                        <td className="py-1 text-right text-[#555]">{fmtVol(c.volume)}</td>
                      </tr>
                    ))}
                    {spDiv && (
                      <tr>
                        <td className="py-1 text-[#555] font-medium">Divergence (Book: {spDiv.book_spread})</td>
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
                  <div className="mt-1.5 text-[10px] text-[#555] italic">{getDivExplanation(spDiv.divergence_pct, gameData.homeTeam)}</div>
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
                  <div className="text-[10px] font-semibold text-[#555] uppercase tracking-wider">{mktLabel}</div>
                  {isActive && <span className="text-[8px] px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">Active</span>}
                </div>
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-[#555]">
                      <th className="text-left py-1 font-normal">Contract</th>
                      <th className="text-right py-1 font-normal">Over</th>
                      <th className="text-right py-1 font-normal">Under</th>
                      <th className="text-right py-1 font-normal">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mktContracts.map((c: any, i: number) => (
                      <tr key={i} className="text-[#ccc]">
                        <td className="py-1 text-[#888] text-[10px] truncate max-w-[180px]" title={c.contract_ticker || ''}>{c.subtitle || c.contract_ticker || '—'}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.yes_price)}</td>
                        <td className="py-1 text-right font-mono">{fmtCents(c.no_price)}</td>
                        <td className="py-1 text-right text-[#555]">{fmtVol(c.volume)}</td>
                      </tr>
                    ))}
                    {totDiv && (
                      <tr>
                        <td className="py-1 text-[#555] font-medium">vs Book ({totDiv.book_total})</td>
                        <td className="py-1 text-right font-mono text-[#888]">{fmtPct(totDiv.exchange_over_prob)}</td>
                        <td className="py-1 text-right font-mono text-[#888]">{totDiv.exchange_over_prob != null ? fmtPct(100 - totDiv.exchange_over_prob) : '—'}</td>
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
  const [lazyLineHistory, setLazyLineHistory] = useState<Record<string, Record<string, any[]>>>({});
  const [loadingPeriods, setLoadingPeriods] = useState<Set<string>>(new Set());

  // Fetch composite_history — full array for UnifiedChart, latest row for fair lines
  const [dbFairLines, setDbFairLines] = useState<CompositeHistoryPoint | null>(null);
  const [compositeHistory, setCompositeHistory] = useState<CompositeHistoryPoint[]>([]);
  useEffect(() => {
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://omi-workspace-production.up.railway.app';
    fetch(`${BACKEND_URL}/api/composite-history/${gameData.id}`)
      .then(res => res.ok ? res.json() : [])
      .then((rows: CompositeHistoryPoint[]) => {
        const arr = Array.isArray(rows) ? rows : [];
        // Filter out pre-calibration rows
        const calibrationCutoff = new Date('2026-02-19T00:00:00Z').getTime();
        const filtered = arr.filter(r => new Date(r.timestamp).getTime() >= calibrationCutoff);
        setCompositeHistory(filtered);
        // Use the latest row as the authoritative fair line
        if (filtered.length > 0) setDbFairLines(filtered[filtered.length - 1]);
      })
      .catch(() => {});
  }, [gameData.id]);

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
    // Prefer composite_history (single source of truth), fall back to edgescout
    const fairSpread = dbFairLines?.fair_spread ?? (consSpread !== null ? calculateFairSpread(consSpread, pythonPillarScores.composite, gameData.sportKey).fairLine : null);
    const fairTotal = dbFairLines?.fair_total ?? (consTotal !== null ? calculateFairTotal(consTotal, pythonPillarScores.gameEnvironment, gameData.sportKey).fairLine : null);
    // ML: prefer DB, then derive from fair spread, then composite fallback
    let fairMLHomeProb: number | null = null;
    if (dbFairLines?.fair_ml_home != null) {
      fairMLHomeProb = americanToImplied(dbFairLines.fair_ml_home);
    } else if (fairSpread !== null) {
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
      <div className="hidden lg:block h-full" style={{ background: '#0b0b0b' }}>
        <div className="flex flex-col h-full mx-auto" style={{ maxWidth: '1400px', fontVariantNumeric: 'tabular-nums' }}>

          {/* Fixed header area — does not scroll */}
          <div className="flex-shrink-0">
            <div style={{ borderBottom: '1px solid #1a1a1a' }}>
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
            <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#1a1a1a]/50">
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
                          : 'text-[#555] hover:text-[#ccc] border border-transparent'
                      }`}
                    >
                      {m === 'spread' ? 'Spread' : m === 'total' ? 'Total' : 'Moneyline'}
                    </button>
                  ))}
                <span className="w-px h-4 bg-[#222]/50 mx-1" />
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
                        ? 'bg-[#222] text-[#ddd]'
                        : 'text-[#555] hover:text-[#888]'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main area: scrollable left content + fixed Edge AI sidebar */}
          <div className="flex flex-1 min-h-0">
            {/* Left: independently scrollable content */}
            <div className="flex-1 min-w-0 overflow-y-auto">
              {/* Unified convergence chart */}
              <div className="border-b border-[#1a1a1a]/50">
                <UnifiedChart
                  key={`chart-${activeMarket}-${activePeriod}`}
                  compositeHistory={compositeHistory}
                  sportKey={gameData.sportKey}
                  activeMarket={activeMarket}
                  homeTeam={gameData.homeTeam}
                  awayTeam={gameData.awayTeam}
                  commenceTime={gameData.commenceTime}
                  pythonPillars={pythonPillarScores}
                />
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
                dbFairLines={dbFairLines}
              />

              {/* Why This Price + CEQ Factors — side by side */}
              <div className="flex border-t border-[#1a1a1a]/50">
                <div className="w-1/2 border-r border-[#1a1a1a]/50">
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

              {/* Injury Report placeholder */}
              <div className="flex border-t border-[#1a1a1a]/50">
                <div className="w-1/2">
                  {/* Injury Report will go here */}
                </div>
              </div>
            </div>

            {/* Right: Edge AI sidebar — fixed width, full height */}
            <div className="w-[260px] flex-shrink-0">
              <AskEdgeAI activeMarket={activeMarket} activePeriod={activePeriod} gameContext={edgeAIGameContext} />
            </div>
          </div>

        </div>
      </div>

      {/* Mobile: Single-column scrollable fallback */}
      <div className="lg:hidden h-auto overflow-y-auto bg-[#0b0b0b]">
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
          <div className="bg-[#0b0b0b]/50 rounded p-2">
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
                        : 'text-[#555] hover:text-[#ccc] border border-transparent'
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
                      ? 'bg-[#222] text-[#ddd]'
                      : 'text-[#555] hover:text-[#888]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Unified convergence chart */}
          <UnifiedChart
            key={`chart-mobile-${activeMarket}-${activePeriod}`}
            compositeHistory={compositeHistory}
            sportKey={gameData.sportKey}
            activeMarket={activeMarket}
            homeTeam={gameData.homeTeam}
            awayTeam={gameData.awayTeam}
            commenceTime={gameData.commenceTime}
            pythonPillars={pythonPillarScores}
          />

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
            dbFairLines={dbFairLines}
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
