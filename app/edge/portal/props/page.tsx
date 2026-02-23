'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';
import { RefreshCw, User, TrendingUp, Filter, ExternalLink, Clock, ChevronDown, ChevronRight } from 'lucide-react';
import Link from 'next/link';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const SPORTS = [
  { key: 'all', label: 'All Sports', emoji: '' },
  // US Major Sports
  { key: 'americanfootball_nfl', label: 'NFL', emoji: '\u{1F3C8}' },
  { key: 'basketball_nba', label: 'NBA', emoji: '\u{1F3C0}' },
  { key: 'icehockey_nhl', label: 'NHL', emoji: '\u{1F3D2}' },
  { key: 'baseball_mlb', label: 'MLB', emoji: '\u{26BE}' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF', emoji: '\u{1F3C8}' },
  { key: 'basketball_ncaab', label: 'NCAAB', emoji: '\u{1F3C0}' },
  { key: 'basketball_wnba', label: 'WNBA', emoji: '\u{1F3C0}' },
  // Soccer
  { key: 'soccer_epl', label: 'EPL', emoji: '\u{26BD}' },
  { key: 'soccer_usa_mls', label: 'MLS', emoji: '\u{26BD}' },
  { key: 'soccer_spain_la_liga', label: 'La Liga', emoji: '\u{26BD}' },
  // Combat
  { key: 'mma_mixed_martial_arts', label: 'UFC', emoji: '\u{1F94A}' },
  { key: 'boxing_boxing', label: 'Boxing', emoji: '\u{1F94A}' },
];

// Prop type labels and display order
const PROP_TYPE_ORDER = [
  'player_points',
  'player_rebounds',
  'player_assists',
  'player_threes',
  'player_steals',
  'player_blocks',
  'player_points_rebounds_assists',
  'player_points_rebounds',
  'player_points_assists',
  'player_rebounds_assists',
  'player_double_double',
  'player_triple_double',
  'player_pass_yds',
  'player_pass_tds',
  'player_rush_yds',
  'player_reception_yds',
  'player_receptions',
  'player_anytime_td',
  'player_goals',
  'player_shots_on_goal',
  'player_blocked_shots',
  'player_power_play_points',
  // MLB
  'pitcher_strikeouts',
  'batter_hits',
  'batter_home_runs',
  'batter_total_bases',
  'batter_rbis',
  // Soccer
  'player_goal_scorer_anytime',
  'player_shots',
  'player_tackles',
];

const PROP_TYPE_LABELS: Record<string, string> = {
  player_points: 'Points',
  player_assists: 'Assists',
  player_rebounds: 'Rebounds',
  player_steals: 'Steals',
  player_blocks: 'Blocks',
  player_threes: '3-Pointers',
  player_points_rebounds_assists: 'Pts+Rebs+Asts',
  player_points_rebounds: 'Pts+Rebs',
  player_points_assists: 'Pts+Asts',
  player_rebounds_assists: 'Rebs+Asts',
  player_double_double: 'Double-Double',
  player_triple_double: 'Triple-Double',
  player_pass_yds: 'Pass Yards',
  player_pass_tds: 'Pass TDs',
  player_pass_completions: 'Completions',
  player_pass_attempts: 'Pass Attempts',
  player_pass_interceptions: 'INTs',
  player_rush_yds: 'Rush Yards',
  player_rush_attempts: 'Rush Attempts',
  player_reception_yds: 'Rec Yards',
  player_receptions: 'Receptions',
  player_anytime_td: 'Anytime TD',
  player_goals: 'Goals',
  player_shots_on_goal: 'Shots on Goal',
  player_blocked_shots: 'Blocked Shots',
  player_power_play_points: 'PP Points',
  batter_hits: 'Hits',
  batter_home_runs: 'Home Runs',
  batter_total_bases: 'Total Bases',
  batter_rbis: 'RBIs',
  batter_runs_scored: 'Runs',
  batter_strikeouts: 'Strikeouts',
  pitcher_strikeouts: 'Strikeouts',
  pitcher_hits_allowed: 'Hits Allowed',
  pitcher_outs: 'Outs',
  // Soccer
  player_goal_scorer_anytime: 'Anytime Scorer',
  player_shots: 'Shots',
  player_tackles: 'Tackles',
  player_fouls: 'Fouls',
  player_cards: 'Cards',
};

// Light theme palette (matches SportsHomeGrid + Live Markets)
const P = {
  pageBg: '#ebedf0',
  cardBg: '#ffffff',
  cardBorder: '#e2e4e8',
  headerBar: '#f4f5f7',
  chartBg: '#f0f1f3',
  textPrimary: '#1f2937',
  textSecondary: '#6b7280',
  textMuted: '#9ca3af',
  textFaint: '#b0b5bd',
  greenText: '#16a34a',
  greenBg: 'rgba(34,197,94,0.06)',
  greenBorder: 'rgba(34,197,94,0.35)',
  redText: '#b91c1c',
  redBg: 'rgba(239,68,68,0.04)',
  redBorder: 'rgba(239,68,68,0.25)',
  neutralBg: '#f7f8f9',
  neutralBorder: '#ecedef',
};

// Sharp book for benchmark (used internally, NOT displayed)
const SHARP_BOOK = 'pinnacle';

// Retail books to display and compare
const RETAIL_BOOKS = ['fanduel', 'draftkings'];

// ============================================================================
// Edge Tier System (matching game markets from edgescout.ts)
// ============================================================================
type EdgeTier = 'NO_EDGE' | 'LOW' | 'MID' | 'HIGH' | 'REVIEW';

const EDGE_TIER_LABELS: Record<EdgeTier, string> = {
  NO_EDGE: 'NO EDGE',
  LOW: 'LOW EDGE',
  MID: 'MID EDGE',
  HIGH: 'HIGH EDGE',
  REVIEW: 'REVIEW',
};

const EDGE_TIER_COLORS: Record<EdgeTier, string> = {
  NO_EDGE: 'text-gray-400',
  LOW: 'text-gray-500',
  MID: 'text-gray-600',
  HIGH: 'text-green-600',
  REVIEW: 'text-red-600',
};

interface PropOutcome {
  player: string;
  propType: string;
  line: number;
  side: 'Over' | 'Under';
  odds: number;
  book: string;
}

interface ParsedProp {
  player: string;
  propType: string;
  propTypeLabel: string;
  fairLine: number;
  // Pinnacle reference
  pinnacleOverOdds: number | null;
  pinnacleUnderOdds: number | null;
  // Retail odds per book (may have different lines)
  retailOverOdds: { book: string; odds: number; line: number }[];
  retailUnderOdds: { book: string; odds: number; line: number }[];
  // Edge result
  edgeSide: 'Over' | 'Under' | null;
  edgePct: number;
  edgeCEQ: number;
  edgeTier: EdgeTier;
  edgeOdds: number;
  edgeBook: string;
  edgeLine: number;
  // Game composite
  gameComposite: number | null;
  compositeModifier: number;
  // Fair value source
  fairSource: 'pinnacle' | 'consensus';
  // Alt book hint: other book has better price on the same side
  altBookHint: string | null;
  // Edge type: 'line' = fair line differs, 'price' = same line, different odds
  edgeType: 'line' | 'price';
  // Conviction score: 0-100 weighted signal composite
  conviction: number;
}

interface GameWithProps {
  gameId: string;
  homeTeam: string;
  awayTeam: string;
  sport: string;
  commenceTime: string;
  propsByType: Map<string, ParsedProp[]>;
}

// Convert American odds to implied probability
function oddsToProb(americanOdds: number): number {
  if (americanOdds > 0) {
    return 100 / (americanOdds + 100);
  } else {
    return Math.abs(americanOdds) / (Math.abs(americanOdds) + 100);
  }
}

function median(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

// Edge % → Confidence % (same mapping as game markets in edgescout.ts)
function edgeToConfidence(edgePct: number): number {
  const ae = Math.abs(edgePct);
  if (ae < 1)  return Math.round(50 + ae * 4);           // 0→50, 1→54
  if (ae < 3)  return Math.round(55 + (ae - 1) * 2);     // 1→55, 3→59
  if (ae < 6)  return Math.round(60 + (ae - 3) * 5 / 3); // 3→60, 6→65
  if (ae < 10) return Math.round(66 + (ae - 6));          // 6→66, 10→70
  return Math.min(75, Math.round(71 + (ae - 10) * 0.5));  // 10→71, capped at 75
}

function getEdgeTier(edgePct: number): EdgeTier {
  const ae = Math.abs(edgePct);
  if (ae >= 10) return 'REVIEW';
  if (ae >= 6) return 'HIGH';
  if (ae >= 3) return 'MID';
  if (ae >= 1) return 'LOW';
  return 'NO_EDGE';
}

// ============================================================================
// Logistic edge calculation — prop-type-specific k-values
// k = how much probability shifts per 1 point of line difference
// Higher k = smaller typical lines (rebounds, TDs) where 1 pt matters more
// Lower k = larger typical lines (pass yards, combo props) where 1 pt matters less
// These are starting estimates — calibrate from graded prop data over time.
// ============================================================================
const PROP_K_VALUES: Record<string, number> = {
  // Basketball
  player_points: 0.15,
  player_rebounds: 0.25,
  player_assists: 0.25,
  player_threes: 0.35,
  player_steals: 0.35,
  player_blocks: 0.35,
  player_points_rebounds_assists: 0.08,
  player_points_rebounds: 0.10,
  player_points_assists: 0.10,
  player_rebounds_assists: 0.15,
  player_double_double: 0.50,
  player_triple_double: 0.50,
  // Football
  player_pass_yds: 0.02,
  player_pass_tds: 0.50,
  player_pass_completions: 0.06,
  player_pass_attempts: 0.06,
  player_pass_interceptions: 0.50,
  player_rush_yds: 0.04,
  player_rush_attempts: 0.08,
  player_reception_yds: 0.04,
  player_receptions: 0.20,
  player_anytime_td: 0.50,
  // Hockey
  player_goals: 0.50,
  player_shots_on_goal: 0.25,
  player_blocked_shots: 0.35,
  player_power_play_points: 0.40,
  // Baseball
  pitcher_strikeouts: 0.15,
  batter_hits: 0.30,
  batter_home_runs: 0.50,
  batter_total_bases: 0.15,
  batter_rbis: 0.30,
  // Soccer
  player_goal_scorer_anytime: 0.50,
  player_shots: 0.25,
  player_tackles: 0.25,
};

/**
 * Logistic prop edge: converts line difference to probability edge.
 * Uses the same logistic approach as game-level spread→ML conversion.
 * Returns edge% (0-50 range) and side (Over/Under).
 */
function propEdgeLogistic(bookLine: number, fairLine: number, propType: string): { edgePct: number; side: 'Over' | 'Under' } {
  const k = PROP_K_VALUES[propType] ?? 0.15;
  const diff = fairLine - bookLine; // positive = fair higher = Over easier on the book line
  const fairProb = 1 / (1 + Math.exp(-diff * k));
  const edgePct = Math.abs(fairProb - 0.50) * 100;
  const side: 'Over' | 'Under' = diff > 0 ? 'Over' : 'Under';
  return { edgePct, side };
}

// Game composite modifier: boosts edge when pillar analysis agrees with direction
// composite_total > 55 → game leans toward more scoring → boost Over props
// composite_total < 45 → game leans toward less scoring → boost Under props
function getGameCompositeModifier(composite: number | null, edgeSide: 'Over' | 'Under'): number {
  if (composite === null) return 1.0;
  if (composite > 60 && edgeSide === 'Over') return 1.2;
  if (composite > 55 && edgeSide === 'Over') return 1.1;
  if (composite < 40 && edgeSide === 'Under') return 1.2;
  if (composite < 45 && edgeSide === 'Under') return 1.1;
  return 1.0;
}

// ============================================================================
// Signal bars, Conviction score, Narrative generation
// ============================================================================

interface PropSignals {
  sharpLine: number;      // 0-100: Does Pinnacle confirm the edge?
  lineMovement: number;   // 0-100: Has the line moved toward the edge?
  gameContext: number;     // 0-100: Does game composite support the direction?
  priceValue: number;     // 0-100: How large is the edge?
  bookConsensus: number;  // 0-100: Do other books agree?
}

const SIGNAL_LABELS: { key: keyof PropSignals; label: string }[] = [
  { key: 'sharpLine', label: 'Sharp Line' },
  { key: 'lineMovement', label: 'Line Movement' },
  { key: 'gameContext', label: 'Game Context' },
  { key: 'priceValue', label: 'Price Value' },
  { key: 'bookConsensus', label: 'Book Consensus' },
];

const SIGNAL_WEIGHTS: Record<keyof PropSignals, number> = {
  sharpLine: 0.30,
  lineMovement: 0.20,
  gameContext: 0.15,
  priceValue: 0.25,
  bookConsensus: 0.10,
};

function computePropSignals(opts: {
  fairSource: 'pinnacle' | 'consensus';
  edgeSide: 'Over' | 'Under';
  edgePct: number;
  fairLine: number;
  edgeLine: number;
  gameComposite: number | null; // 0-100 scale
  altBookHint: string | null;
  edgeOdds: number;
}, history: any[] | null): PropSignals {
  // 1. Sharp Line (0-100): Pinnacle-backed = higher base, line gap boosts
  let sharpLine = opts.fairSource === 'pinnacle' ? 70 : 45;
  const lineDiff = Math.abs(opts.fairLine - opts.edgeLine);
  if (lineDiff >= 2) sharpLine = Math.min(100, sharpLine + 20);
  else if (lineDiff >= 1) sharpLine = Math.min(100, sharpLine + 10);
  else if (lineDiff >= 0.5) sharpLine = Math.min(100, sharpLine + 5);

  // 2. Line Movement (0-100): movement confirming edge = higher
  let lineMovement = 50;
  if (history && history.length >= 2) {
    const openLine = history[0].line;
    const currentLine = history[history.length - 1].line;
    const movement = currentLine - openLine;
    const confirmsEdge = (opts.edgeSide === 'Over' && movement > 0) ||
                         (opts.edgeSide === 'Under' && movement < 0);
    const absMove = Math.abs(movement);
    if (confirmsEdge) {
      lineMovement = Math.min(95, 55 + Math.round(absMove * 10));
    } else if (absMove > 0.25) {
      lineMovement = Math.max(10, 45 - Math.round(absMove * 10));
    }
  }

  // 3. Game Context (0-100): composite alignment with edge direction
  let gameContext = 50;
  if (opts.gameComposite !== null) {
    if (opts.edgeSide === 'Over') {
      gameContext = Math.min(95, Math.max(10, opts.gameComposite));
    } else {
      gameContext = Math.min(95, Math.max(10, 100 - opts.gameComposite));
    }
  }

  // 4. Price Value (0-100): edge size mapped to signal
  const priceValue = Math.min(95, Math.round(50 + opts.edgePct * 5));

  // 5. Book Consensus (0-100): alt book agrees = confirmation
  let bookConsensus = 50;
  if (opts.altBookHint) bookConsensus = 72;
  if (opts.edgeOdds > 0) bookConsensus = Math.min(95, bookConsensus + 8);

  return { sharpLine, lineMovement, gameContext, priceValue, bookConsensus };
}

function computeConviction(signals: PropSignals): number {
  return Math.round(
    signals.sharpLine * SIGNAL_WEIGHTS.sharpLine +
    signals.lineMovement * SIGNAL_WEIGHTS.lineMovement +
    signals.gameContext * SIGNAL_WEIGHTS.gameContext +
    signals.priceValue * SIGNAL_WEIGHTS.priceValue +
    signals.bookConsensus * SIGNAL_WEIGHTS.bookConsensus
  );
}

function generatePropNarrative(
  opts: { edgeSide: 'Over' | 'Under'; edgePct: number; fairLine: number; edgeLine: number; propTypeLabel: string; edgeType: 'line' | 'price'; fairSource: 'pinnacle' | 'consensus' },
  signals: PropSignals,
  history: any[] | null,
): string {
  const parts: string[] = [];

  // Sharp line confirmation
  if (signals.sharpLine >= 70) {
    parts.push(`Sharp line confirms ${opts.edgeSide}`);
  } else if (signals.sharpLine >= 55) {
    parts.push(`Sharp line leans ${opts.edgeSide}`);
  }

  // Line movement
  if (history && history.length >= 2) {
    const movement = history[history.length - 1].line - history[0].line;
    if (signals.lineMovement >= 60 && Math.abs(movement) >= 0.5) {
      parts.push(`line moved ${movement > 0 ? 'up' : 'down'} ${Math.abs(movement).toFixed(1)}pt`);
    }
  }

  // Game context
  if (signals.gameContext >= 65) parts.push('game context supports');
  else if (signals.gameContext <= 35) parts.push('game context opposes');

  // Edge specifics
  const lineDiff = Math.abs(opts.fairLine - opts.edgeLine);
  if (opts.edgeType === 'line' && lineDiff >= 0.5) {
    parts.push(`book ${lineDiff.toFixed(1)}pt ${opts.edgeSide === 'Over' ? 'below' : 'above'} fair`);
  } else if (opts.edgeType === 'price') {
    parts.push(`${opts.edgePct.toFixed(1)}% price edge at same line`);
  }

  if (parts.length === 0) {
    return `${opts.edgePct.toFixed(1)}% ${opts.edgeSide} edge on ${opts.propTypeLabel}.`;
  }
  // Capitalize first part
  parts[0] = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
  return parts.join(', ') + '.';
}

function getSignalBarColor(value: number): string {
  if (value >= 70) return P.greenText;
  if (value >= 55) return '#ca8a04'; // amber
  if (value >= 40) return P.textSecondary;
  return P.redText;
}

function getConvictionColor(conv: number): string {
  if (conv >= 70) return P.greenText;
  if (conv >= 60) return '#ca8a04';
  if (conv >= 50) return P.textSecondary;
  return P.textMuted;
}

// Format a line value consistently (shared between chart and description)
function fmtLine(v: number): string {
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

// TradingView-style step chart: continuous crosshair, edge fill, both lines interactive
function PropLineChart({ data, fairLine, fairSource }: { data: any[]; fairLine: number; fairSource: 'pinnacle' | 'consensus' }) {
  const [hoverX, setHoverX] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Debug: log fair value sources so chart vs description can be audited in console
  useEffect(() => {
    const last = data[data.length - 1];
    console.log('[PropLineChart] fairLine:', fairLine, '| source:', fairSource,
      '| lastSnapshot:', last?.line, '| book:', last?.book_key, '| time:', last?.snapshot_time);
  }, [fairLine, fairSource, data]);

  const W = 700, H = 195, PAD_X = 40, PAD_R = 78, PAD_Y = 14, CHART_B = 142;

  // Filter to single book (prefer FanDuel) to avoid mixed-book step chart
  const bookCounts = new Map<string, number>();
  data.forEach(d => {
    const bk = (d.book_key || '').toLowerCase();
    bookCounts.set(bk, (bookCounts.get(bk) || 0) + 1);
  });
  let primaryBook = 'fanduel';
  if ((bookCounts.get('fanduel') || 0) < 2) {
    let maxN = 0;
    bookCounts.forEach((n, bk) => { if (n > maxN) { maxN = n; primaryBook = bk; } });
  }
  const bookData = data.filter(d => (d.book_key || '').toLowerCase() === primaryBook);
  const bookFullName = primaryBook === 'fanduel' ? 'FanDuel' : primaryBook === 'draftkings' ? 'DraftKings' : primaryBook;
  const bookShort = primaryBook === 'fanduel' ? 'FD' : primaryBook === 'draftkings' ? 'DK' : primaryBook.slice(0, 3).toUpperCase();

  const vals = bookData.map(d => Number(d.line)).filter(n => !isNaN(n));
  if (vals.length < 2) return null;

  // Y scale includes both lines
  const allY = [...vals, fairLine];
  const yMin = Math.min(...allY);
  const yMax = Math.max(...allY);
  const yRange = yMax - yMin || 1;
  const chartW = W - PAD_X - PAD_R;
  const xStep = chartW / (vals.length - 1);
  const toY = (v: number) => PAD_Y + (1 - (v - yMin) / yRange) * (CHART_B - PAD_Y);
  const fairY = toY(fairLine);

  // Book step-line path
  const pathParts: string[] = [];
  vals.forEach((v, i) => {
    const x = PAD_X + i * xStep;
    const y = toY(v);
    if (i === 0) pathParts.push(`M ${x} ${y}`);
    else { pathParts.push(`H ${x}`); pathParts.push(`V ${y}`); }
  });
  const bookPath = pathParts.join(' ');

  // Y-axis ticks
  const yTicks = [yMin, (yMin + yMax) / 2, yMax];

  // X-axis timestamps
  const t0 = bookData[0]?.snapshot_time
    ? new Date(bookData[0].snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '';
  const tN = bookData[bookData.length - 1]?.snapshot_time
    ? new Date(bookData[bookData.length - 1].snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';

  // Endpoint positions + collision avoidance
  const lastX = PAD_X + (vals.length - 1) * xStep;
  const lastBookY = toY(vals[vals.length - 1]);
  const GAP = 14;
  let eLblBookY = lastBookY, eLblFairY = fairY;
  if (Math.abs(eLblBookY - eLblFairY) < GAP) {
    const mid = (eLblBookY + eLblFairY) / 2;
    if (lastBookY <= fairY) { eLblBookY = mid - GAP / 2; eLblFairY = mid + GAP / 2; }
    else { eLblFairY = mid - GAP / 2; eLblBookY = mid + GAP / 2; }
  }

  // --- Continuous crosshair hover ---
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const mx = ((e.clientX - rect.left) / rect.width) * W;
    if (mx < PAD_X || mx > PAD_X + chartW) { setHoverX(null); return; }
    setHoverX(mx);
  };
  const handleMouseLeave = () => setHoverX(null);

  // Step-chart interpolation: last known value before cursor X
  const stepIdx = hoverX !== null
    ? Math.min(vals.length - 1, Math.max(0, Math.floor((hoverX - PAD_X) / xStep)))
    : null;
  const hBookVal = stepIdx !== null ? vals[stepIdx] : null;
  const hBookY = hBookVal !== null ? toY(hBookVal) : 0;
  const hd = stepIdx !== null ? bookData[stepIdx] : null;
  const hTime = hd?.snapshot_time
    ? new Date(hd.snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true })
    : '';

  // Crosshair label collision avoidance
  const CH_GAP = 13;
  let chBookY = hBookY, chFairY = fairY;
  if (hoverX !== null && Math.abs(chBookY - chFairY) < CH_GAP) {
    const mid = (chBookY + chFairY) / 2;
    if (hBookY <= fairY) { chBookY = mid - CH_GAP / 2; chFairY = mid + CH_GAP / 2; }
    else { chFairY = mid - CH_GAP / 2; chBookY = mid + CH_GAP / 2; }
  }
  // Flip labels left if near right edge
  const lblW = 64;
  const lblDx = hoverX !== null && hoverX > W - PAD_R - lblW - 14 ? -(lblW + 6) : 8;

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[700px] cursor-crosshair select-none"
      style={{ height: '195px' }} onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>

      {/* Grid lines */}
      {yTicks.map((val, i) => {
        const y = toY(val);
        return (
          <g key={i}>
            <line x1={PAD_X} y1={y} x2={W - PAD_R} y2={y} stroke={P.cardBorder} strokeWidth="1" />
            <text x={PAD_X - 4} y={y + 3} textAnchor="end" fill={P.textMuted} fontSize="9" fontFamily="monospace">{fmtLine(val)}</text>
          </g>
        );
      })}

      {/* Edge fill: green when OMI > book (positive edge), red when OMI < book */}
      {vals.map((v, i) => {
        if (i === vals.length - 1) return null;
        const x1 = PAD_X + i * xStep;
        const x2 = PAD_X + (i + 1) * xStep;
        const bY = toY(v);
        const gap = Math.abs(bY - fairY);
        if (gap < 1) return null;
        const positive = fairLine > v; // OMI fair above book = positive edge
        return (
          <rect key={i} x={x1} y={Math.min(bY, fairY)} width={x2 - x1} height={gap}
            fill={positive ? 'rgba(220,252,231,0.3)' : 'rgba(252,231,231,0.3)'} />
        );
      })}

      {/* OMI Fair line — solid orange, 2px */}
      <line x1={PAD_X} y1={fairY} x2={lastX} y2={fairY} stroke="#ea580c" strokeWidth="2" />
      {/* Orange dots at each data point X */}
      {vals.map((_, i) => (
        <circle key={`f${i}`} cx={PAD_X + i * xStep} cy={fairY} r="3" fill="#ea580c" stroke={P.cardBg} strokeWidth="1" />
      ))}

      {/* Book step-line — solid green, 2px */}
      <path d={bookPath} fill="none" stroke="#16a34a" strokeWidth="2" />
      {/* Green dots at each data point */}
      {vals.map((v, i) => (
        <circle key={`b${i}`} cx={PAD_X + i * xStep} cy={toY(v)} r="3" fill="#16a34a" stroke={P.cardBg} strokeWidth="1" />
      ))}

      {/* Endpoint labels (always visible) */}
      <text x={lastX + 10} y={eLblBookY + 4} fill="#16a34a" fontSize="10" fontFamily="monospace" fontWeight="bold">
        {bookShort} {fmtLine(vals[vals.length - 1])}
      </text>
      <text x={lastX + 10} y={eLblFairY + 4} fill="#ea580c" fontSize="10" fontFamily="monospace" fontWeight="bold">
        OMI {fmtLine(fairLine)}
      </text>

      {/* X-axis */}
      <text x={PAD_X} y={CHART_B + 18} fill={P.textMuted} fontSize="8" fontFamily="monospace">{t0}</text>
      <text x={lastX} y={CHART_B + 18} textAnchor="end" fill={P.textMuted} fontSize="8" fontFamily="monospace">{tN}</text>

      {/* Legend */}
      <g transform={`translate(${PAD_X}, ${H - 10})`}>
        <line x1="0" y1="0" x2="12" y2="0" stroke="#16a34a" strokeWidth="2" />
        <circle cx="6" cy="0" r="1.5" fill="#16a34a" />
        <text x="16" y="3" fill={P.textSecondary} fontSize="9" fontFamily="monospace">{bookFullName}</text>
        <text x="72" y="3" fill={P.textFaint} fontSize="9">|</text>
        <line x1="82" y1="0" x2="94" y2="0" stroke="#ea580c" strokeWidth="2" />
        <circle cx="88" cy="0" r="1.5" fill="#ea580c" />
        <text x="98" y="3" fill={P.textSecondary} fontSize="9" fontFamily="monospace">OMI Fair</text>
        <text x="156" y="3" fill={P.textFaint} fontSize="9">|</text>
        <rect x="166" y="-5" width="12" height="10" rx="1" fill="rgba(220,252,231,0.5)" stroke="#bbf7d0" strokeWidth="0.5" />
        <text x="182" y="3" fill={P.textSecondary} fontSize="9" fontFamily="monospace">Edge Zone</text>
      </g>

      {/* Continuous crosshair */}
      {hoverX !== null && stepIdx !== null && hBookVal !== null && (
        <g>
          {/* Vertical crosshair line */}
          <line x1={hoverX} y1={PAD_Y} x2={hoverX} y2={CHART_B} stroke="#d1d5db" strokeWidth="1" strokeDasharray="3 2" />

          {/* Circle + label on book line */}
          <circle cx={hoverX} cy={hBookY} r="4" fill="#16a34a" stroke={P.cardBg} strokeWidth="1.5" />
          <rect x={hoverX + lblDx - 2} y={chBookY - 8} width={lblW} height={15} rx="3" fill="rgba(255,255,255,0.92)" />
          <text x={hoverX + lblDx} y={chBookY + 4} fill="#16a34a" fontSize="9" fontFamily="monospace" fontWeight="bold">
            {bookShort}: {fmtLine(hBookVal)}
          </text>

          {/* Circle + label on OMI fair line */}
          <circle cx={hoverX} cy={fairY} r="4" fill="#ea580c" stroke={P.cardBg} strokeWidth="1.5" />
          <rect x={hoverX + lblDx - 2} y={chFairY - 8} width={lblW} height={15} rx="3" fill="rgba(255,255,255,0.92)" />
          <text x={hoverX + lblDx} y={chFairY + 4} fill="#ea580c" fontSize="9" fontFamily="monospace" fontWeight="bold">
            OMI: {fmtLine(fairLine)}
          </text>

          {/* Time label at bottom of crosshair */}
          <text x={hoverX} y={CHART_B + 12} textAnchor="middle" fill={P.textSecondary} fontSize="8" fontFamily="monospace">
            {hTime}
          </text>
        </g>
      )}
    </svg>
  );
}

// Number-line comparison bar: shows FD, DK, and OMI Fair markers on a horizontal scale
function PropComparisonBar({ prop }: { prop: ParsedProp }) {
  const fdOver = prop.retailOverOdds.find(o => o.book.toLowerCase() === 'fanduel');
  const dkOver = prop.retailOverOdds.find(o => o.book.toLowerCase() === 'draftkings');
  const fdLine = fdOver?.line;
  const dkLine = dkOver?.line;
  const fairLine = prop.fairLine;

  const values = [fdLine, dkLine, fairLine].filter((v): v is number => v != null);
  if (values.length < 2) return null;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const pad = range * 0.2;
  const scaleMin = min - pad;
  const scaleMax = max + pad;
  const scaleRange = scaleMax - scaleMin;
  const toX = (v: number) => ((v - scaleMin) / scaleRange) * 100;

  const fmtVal = (v: number) => Number.isInteger(v) ? String(v) : v.toFixed(1);

  const markers: { label: string; value: number; color: string; bg: string; border: string }[] = [];
  if (fdLine != null) markers.push({ label: 'FD', value: fdLine, color: '#1493ff', bg: '#eff6ff', border: '#bfdbfe' });
  if (dkLine != null) markers.push({ label: 'DK', value: dkLine, color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' });
  markers.push({ label: 'OMI', value: fairLine, color: '#ea580c', bg: '#fff7ed', border: '#fed7aa' });

  return (
    <div style={{ padding: '12px 0' }}>
      <div style={{ position: 'relative', height: 40, margin: '0 16px' }}>
        {/* Track */}
        <div style={{ position: 'absolute', top: 18, left: 0, right: 0, height: 4, background: P.cardBorder, borderRadius: 2 }} />
        {/* Markers */}
        {markers.map((m) => (
          <div key={m.label} style={{ position: 'absolute', left: `${toX(m.value)}%`, transform: 'translateX(-50%)', textAlign: 'center', zIndex: m.label === 'OMI' ? 2 : 1 }}>
            <div style={{
              fontSize: 10, fontWeight: 700, fontFamily: 'monospace', color: m.color,
              background: m.bg, border: `1px solid ${m.border}`,
              borderRadius: 4, padding: '1px 5px', marginBottom: 2, whiteSpace: 'nowrap',
            }}>
              {m.label} {fmtVal(m.value)}
            </div>
            <div style={{ width: m.label === 'OMI' ? 10 : 8, height: m.label === 'OMI' ? 10 : 8, borderRadius: '50%', background: m.color, margin: '0 auto', border: `2px solid ${P.cardBg}`, boxShadow: '0 0 0 1px ' + m.border }} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function PlayerPropsPage() {
  const [gamesWithProps, setGamesWithProps] = useState<GameWithProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSport, setSelectedSport] = useState('all');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [expandedGames, setExpandedGames] = useState<Set<string>>(new Set());
  const [expandedProps, setExpandedProps] = useState<Set<string>>(new Set());
  const [propHistory, setPropHistory] = useState<Record<string, any[]>>({});
  const [loadingHistory, setLoadingHistory] = useState<Set<string>>(new Set());
  const [gamePillars, setGamePillars] = useState<Record<string, {
    execution: number; incentives: number; shocks: number;
    timeDecay: number; flow: number; gameEnvironment: number;
    composite: number;
  }>>({});
  const [minCEQ, setMinCEQ] = useState(55);
  const [selectedBook, setSelectedBook] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('omi_prop_book') || 'fanduel';
    }
    return 'fanduel';
  });

  // Persist book selection
  useEffect(() => {
    localStorage.setItem('omi_prop_book', selectedBook);
  }, [selectedBook]);

  const fetchPropsFromCachedOdds = useCallback(async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('cached_odds')
        .select('game_data');

      if (selectedSport !== 'all') {
        query = query.eq('game_data->>sport_key', selectedSport);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      // Fetch game composites for all games in one batch
      const gameIds = (data || []).map((r: any) => r.game_data?.id).filter(Boolean);
      const compositeMap = new Map<string, number>();
      if (gameIds.length > 0) {
        const { data: compData } = await supabase
          .from('composite_history')
          .select('game_id, composite_total')
          .in('game_id', gameIds)
          .order('timestamp', { ascending: false });
        for (const row of compData || []) {
          if (!compositeMap.has(row.game_id) && row.composite_total != null) {
            compositeMap.set(row.game_id, Math.round(Number(row.composite_total) * 100));
          }
        }
      }

      // Fetch pillar scores from predictions table (active games)
      const pillarMap: typeof gamePillars = {};
      if (gameIds.length > 0) {
        const { data: pillarData } = await supabase
          .from('predictions')
          .select('game_id, pillar_execution, pillar_incentives, pillar_shocks, pillar_time_decay, pillar_flow, composite_score, pillars_json')
          .in('game_id', gameIds);
        for (const row of pillarData || []) {
          // game_environment is only in pillars_json, not a dedicated column
          let gameEnv = 0.5;
          try {
            const pillarsObj = typeof row.pillars_json === 'string'
              ? JSON.parse(row.pillars_json)
              : row.pillars_json;
            if (pillarsObj?.game_environment?.score != null) {
              gameEnv = pillarsObj.game_environment.score;
            }
          } catch { /* use default */ }

          pillarMap[row.game_id] = {
            execution: Math.round((row.pillar_execution ?? 0.5) * 100),
            incentives: Math.round((row.pillar_incentives ?? 0.5) * 100),
            shocks: Math.round((row.pillar_shocks ?? 0.5) * 100),
            timeDecay: Math.round((row.pillar_time_decay ?? 0.5) * 100),
            flow: Math.round((row.pillar_flow ?? 0.5) * 100),
            gameEnvironment: Math.round(gameEnv * 100),
            composite: Math.round((row.composite_score ?? 0.5) * 100),
          };
        }
      }
      setGamePillars(pillarMap);

      const gamesData: GameWithProps[] = [];

      for (const row of data || []) {
        const game = row.game_data;
        if (!game?.bookmakers) continue;

        // Parse all prop outcomes from all bookmakers
        const propOutcomes: PropOutcome[] = [];

        for (const bookmaker of game.bookmakers) {
          for (const market of bookmaker.markets || []) {
            const isProp = market.key.startsWith('player_') ||
                          market.key.startsWith('pitcher_') ||
                          market.key.startsWith('batter_');

            if (!isProp) continue;

            for (const outcome of market.outcomes || []) {
              if (!outcome.description || !outcome.name || outcome.point === undefined) continue;

              propOutcomes.push({
                player: outcome.description,
                propType: market.key,
                line: outcome.point,
                side: outcome.name as 'Over' | 'Under',
                odds: outcome.price,
                book: bookmaker.key,
              });
            }
          }
        }

        if (propOutcomes.length === 0) continue;

        // Group by player|propType (NOT including line) for cross-line edge detection
        const propGroups = new Map<string, {
          player: string;
          propType: string;
          entries: Map<string, {
            book: string;
            line: number;
            overOdds: number | null;
            underOdds: number | null;
          }>;
        }>();

        for (const outcome of propOutcomes) {
          const groupKey = `${outcome.player}|${outcome.propType}`;
          if (!propGroups.has(groupKey)) {
            propGroups.set(groupKey, {
              player: outcome.player,
              propType: outcome.propType,
              entries: new Map(),
            });
          }
          const group = propGroups.get(groupKey)!;
          const entryKey = `${outcome.book}|${outcome.line}`;
          if (!group.entries.has(entryKey)) {
            group.entries.set(entryKey, {
              book: outcome.book,
              line: outcome.line,
              overOdds: null,
              underOdds: null,
            });
          }
          const entry = group.entries.get(entryKey)!;
          if (outcome.side === 'Over') {
            entry.overOdds = outcome.odds;
          } else {
            entry.underOdds = outcome.odds;
          }
        }

        // Calculate edge for each prop group using fair-value methodology
        const gameComposite = compositeMap.get(game.id) ?? null;
        const propsByType = new Map<string, ParsedProp[]>();

        for (const [, group] of propGroups) {
          const entries = Array.from(group.entries.values());

          // Separate Pinnacle (sharp reference) and retail
          const pinnacleEntry = entries.find(e => e.book.toLowerCase() === SHARP_BOOK);
          const retailEntries = entries.filter(e => RETAIL_BOOKS.includes(e.book.toLowerCase()));

          if (retailEntries.length === 0) continue;

          // Fair line = Pinnacle CURRENT line (sharp fair value), or median of retail CURRENT lines
          const hasPinnacle = !!pinnacleEntry;
          const fairLine = hasPinnacle
            ? pinnacleEntry.line
            : median(retailEntries.map(e => e.line));

          // ── Edge calculation: selected book only ──
          // Find entry for the user's selected book
          const myEntry = retailEntries.find(e => e.book.toLowerCase() === selectedBook);
          if (!myEntry) continue; // selected book doesn't offer this prop

          let bestEdgePct = 0;
          let bestEdgeSide: 'Over' | 'Under' | null = null;
          let bestEdgeOdds = 0;
          let edgeType: 'line' | 'price' = 'line';

          const lineDiff = myEntry.line - fairLine;

          if (Math.abs(lineDiff) >= 0.25) {
            // Line differs from fair: use logistic probability edge
            const { edgePct, side } = propEdgeLogistic(myEntry.line, fairLine, group.propType);
            const odds = side === 'Over' ? myEntry.overOdds : myEntry.underOdds;
            if (odds && edgePct > 0.5) {
              bestEdgePct = edgePct;
              bestEdgeSide = side;
              bestEdgeOdds = odds;
            }
          } else if (pinnacleEntry) {
            // Same line — compare implied probabilities vs Pinnacle
            edgeType = 'price';
            if (myEntry.overOdds && pinnacleEntry.overOdds) {
              const retailProb = oddsToProb(myEntry.overOdds);
              const sharpProb = oddsToProb(pinnacleEntry.overOdds);
              const edge = (sharpProb - retailProb) * 100;
              if (edge > bestEdgePct) {
                bestEdgePct = edge;
                bestEdgeSide = 'Over';
                bestEdgeOdds = myEntry.overOdds;
              }
            }
            if (myEntry.underOdds && pinnacleEntry.underOdds) {
              const retailProb = oddsToProb(myEntry.underOdds);
              const sharpProb = oddsToProb(pinnacleEntry.underOdds);
              const edge = (sharpProb - retailProb) * 100;
              if (edge > bestEdgePct) {
                bestEdgePct = edge;
                bestEdgeSide = 'Under';
                bestEdgeOdds = myEntry.underOdds;
              }
            }
          }

          // Skip if no meaningful edge found
          if (bestEdgeSide === null || bestEdgePct < 0.5) continue;

          // Apply game composite modifier
          const modifier = getGameCompositeModifier(gameComposite, bestEdgeSide);
          const adjustedEdgePct = bestEdgePct * modifier;

          // Map to confidence and tier (same as game markets)
          const confidence = edgeToConfidence(adjustedEdgePct);
          const tier = getEdgeTier(adjustedEdgePct);

          // Build retail odds arrays for display (all books for reference)
          const retailOverOdds = retailEntries
            .filter(e => e.overOdds !== null)
            .map(e => ({ book: e.book, odds: e.overOdds!, line: e.line }));
          const retailUnderOdds = retailEntries
            .filter(e => e.underOdds !== null)
            .map(e => ({ book: e.book, odds: e.underOdds!, line: e.line }));

          // Check if the OTHER book has a better price on the same side
          let altBookHint: string | null = null;
          const otherBook = selectedBook === 'fanduel' ? 'draftkings' : 'fanduel';
          const otherEntry = retailEntries.find(e => e.book.toLowerCase() === otherBook);
          if (otherEntry && bestEdgeSide) {
            const myOdds = bestEdgeSide === 'Over' ? myEntry.overOdds : myEntry.underOdds;
            const otherOdds = bestEdgeSide === 'Over' ? otherEntry.overOdds : otherEntry.underOdds;
            if (myOdds && otherOdds && otherOdds > myOdds) {
              const otherLabel = otherBook === 'fanduel' ? 'FD' : 'DK';
              altBookHint = `Better price on ${otherLabel}: ${otherOdds > 0 ? '+' : ''}${otherOdds}`;
            }
          }

          // Compute conviction score (base: without history, lineMovement=50)
          const baseSignals = computePropSignals({
            fairSource: hasPinnacle ? 'pinnacle' : 'consensus',
            edgeSide: bestEdgeSide,
            edgePct: Math.round(adjustedEdgePct * 10) / 10,
            fairLine,
            edgeLine: myEntry.line,
            gameComposite,
            altBookHint,
            edgeOdds: bestEdgeOdds,
          }, null);
          const conviction = computeConviction(baseSignals);

          // Apply min score filter
          if (conviction < minCEQ) continue;

          const parsedProp: ParsedProp = {
            player: group.player,
            propType: group.propType,
            propTypeLabel: PROP_TYPE_LABELS[group.propType] || group.propType.replace('player_', '').replace(/_/g, ' '),
            fairLine,
            pinnacleOverOdds: pinnacleEntry?.overOdds ?? null,
            pinnacleUnderOdds: pinnacleEntry?.underOdds ?? null,
            retailOverOdds,
            retailUnderOdds,
            edgeSide: bestEdgeSide,
            edgePct: Math.round(adjustedEdgePct * 10) / 10,
            edgeCEQ: confidence,
            edgeTier: tier,
            edgeOdds: bestEdgeOdds,
            edgeBook: myEntry.book,
            edgeLine: myEntry.line,
            gameComposite,
            compositeModifier: modifier,
            fairSource: hasPinnacle ? 'pinnacle' : 'consensus',
            altBookHint,
            edgeType,
            conviction,
          };

          // Group by prop type
          if (!propsByType.has(group.propType)) {
            propsByType.set(group.propType, []);
          }
          propsByType.get(group.propType)!.push(parsedProp);
        }

        // Sort by edge descending within each prop type
        for (const [, props] of propsByType) {
          props.sort((a, b) => b.edgePct - a.edgePct);
        }

        if (propsByType.size === 0) continue;

        gamesData.push({
          gameId: game.id,
          homeTeam: game.home_team,
          awayTeam: game.away_team,
          sport: game.sport_key,
          commenceTime: game.commence_time,
          propsByType,
        });
      }

      // Sort games by total number of edges
      gamesData.sort((a, b) => {
        const aEdges = Array.from(a.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
        const bEdges = Array.from(b.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
        return bEdges - aEdges;
      });

      setGamesWithProps(gamesData);
      setLastUpdated(new Date());
      setError(null);

      // Auto-expand first 3 games with edges
      const gamesWithEdges = new Set(gamesData.slice(0, 3).map(g => g.gameId));
      setExpandedGames(gamesWithEdges);

    } catch (e: any) {
      setError(e?.message || 'Failed to load player props');
    } finally {
      setLoading(false);
    }
  }, [selectedSport, minCEQ, selectedBook]);

  useEffect(() => {
    fetchPropsFromCachedOdds();
  }, [fetchPropsFromCachedOdds]);

  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    if (date < now) {
      return 'LIVE';
    }
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatOdds = (odds: number): string => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const formatBook = (book: string): string => {
    if (book.toLowerCase() === 'fanduel') return 'FD';
    if (book.toLowerCase() === 'draftkings') return 'DK';
    return book.slice(0, 2).toUpperCase();
  };

  const getSportEmoji = (sport: string): string => {
    return SPORTS.find((s) => s.key === sport)?.emoji || '\u{1F3C6}';
  };

  const toggleGame = (gameId: string) => {
    const newExpanded = new Set(expandedGames);
    if (newExpanded.has(gameId)) {
      newExpanded.delete(gameId);
    } else {
      newExpanded.add(gameId);
    }
    setExpandedGames(newExpanded);
  };

  const getCEQColor = (ceq: number): string => {
    if (ceq >= 66) return 'text-green-600';    // HIGH/MAX
    if (ceq >= 60) return 'text-gray-700';     // MID
    if (ceq >= 55) return 'text-gray-500';     // LOW
    return 'text-gray-400';                    // NO EDGE
  };

  const getCEQBadgeColor = (ceq: number): string => {
    if (ceq >= 66) return 'bg-green-50 text-green-700 border-green-200';
    if (ceq >= 60) return 'bg-gray-100 text-gray-600 border-gray-200';
    if (ceq >= 55) return 'bg-gray-50 text-gray-500 border-gray-200';
    return 'bg-gray-50 text-gray-400 border-gray-200';
  };

  const getSportBorderColor = (sport: string): string => {
    if (sport.includes('nba') || sport.includes('ncaab') || sport.includes('wnba')) return '#f97316';
    if (sport.includes('nfl') || sport.includes('ncaaf')) return '#ef4444';
    if (sport.includes('nhl')) return '#3b82f6';
    if (sport.includes('mlb')) return '#22c55e';
    if (sport.includes('soccer')) return '#a855f7';
    if (sport.includes('mma') || sport.includes('boxing')) return '#ef4444';
    return '#71717a';
  };

  const toggleProp = async (propKey: string, gameId: string, player: string, marketType: string) => {
    const newExpanded = new Set(expandedProps);
    if (newExpanded.has(propKey)) {
      newExpanded.delete(propKey);
      setExpandedProps(newExpanded);
      return;
    }
    newExpanded.add(propKey);
    setExpandedProps(newExpanded);

    // Lazy fetch history on first expand
    if (!propHistory[propKey] && !loadingHistory.has(propKey)) {
      setLoadingHistory(prev => new Set(prev).add(propKey));
      try {
        const { data } = await supabase
          .from('prop_snapshots')
          .select('*')
          .eq('game_id', gameId)
          .eq('player_name', player)
          .eq('market_type', marketType)
          .order('snapshot_time', { ascending: true });

        setPropHistory(prev => ({ ...prev, [propKey]: data || [] }));
      } catch {
        setPropHistory(prev => ({ ...prev, [propKey]: [] }));
      } finally {
        setLoadingHistory(prev => {
          const next = new Set(prev);
          next.delete(propKey);
          return next;
        });
      }
    }
  };

  // Get sorted prop types for a game
  const getSortedPropTypes = (propsByType: Map<string, ParsedProp[]>): string[] => {
    const types = Array.from(propsByType.keys());
    return types.sort((a, b) => {
      const aIndex = PROP_TYPE_ORDER.indexOf(a);
      const bIndex = PROP_TYPE_ORDER.indexOf(b);
      if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
      if (aIndex === -1) return 1;
      if (bIndex === -1) return -1;
      return aIndex - bIndex;
    });
  };

  const totalPropsWithEdges = gamesWithProps.reduce(
    (acc, game) => acc + Array.from(game.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0),
    0
  );

  const totalPlayers = new Set(
    gamesWithProps.flatMap(g =>
      Array.from(g.propsByType.values()).flat().map(p => p.player)
    )
  ).size;

  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto" style={{ background: P.pageBg, minHeight: '100vh' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: P.textPrimary }}>
            <User className="w-6 h-6" style={{ color: '#7c3aed' }} />
            Player Props
          </h1>
          <p className="text-sm mt-1" style={{ color: P.textSecondary }}>
            Fair lines vs your book — ranked by edge size
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-xs flex items-center gap-1" style={{ color: P.textMuted }}>
              <Clock className="w-3 h-3" />
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchPropsFromCachedOdds}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors disabled:opacity-50"
            style={{ background: P.cardBg, color: P.textSecondary, border: `1px solid ${P.cardBorder}` }}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Book Toggle + Filters Row */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        {/* Book Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium" style={{ color: P.textMuted }}>My Book:</span>
          <div className="flex gap-0 rounded-lg overflow-hidden" style={{ border: `1px solid ${P.cardBorder}` }}>
            {[{ key: 'fanduel', label: 'FanDuel' }, { key: 'draftkings', label: 'DraftKings' }].map((book) => (
              <button
                key={book.key}
                onClick={() => setSelectedBook(book.key)}
                className="px-3 py-1.5 text-xs font-semibold transition-colors"
                style={selectedBook === book.key
                  ? { background: '#7c3aed', color: '#ffffff' }
                  : { background: P.cardBg, color: P.textSecondary }
                }
              >
                {book.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4" style={{ color: P.textMuted }} />
          <div className="flex gap-1 flex-wrap">
            {SPORTS.map((sport) => (
              <button
                key={sport.key}
                onClick={() => setSelectedSport(sport.key)}
                className="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
                style={selectedSport === sport.key
                  ? { background: '#f3e8ff', color: '#7c3aed', border: '1px solid #c4b5fd' }
                  : { background: P.cardBg, color: P.textSecondary, border: `1px solid ${P.cardBorder}` }
                }
              >
                {sport.emoji} {sport.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs" style={{ color: P.textMuted }}>Min Score:</span>
          <div className="flex gap-1">
            {[50, 55, 60, 66].map((val) => (
              <button
                key={val}
                onClick={() => setMinCEQ(val)}
                className="px-2 py-1 rounded text-xs transition-colors"
                style={minCEQ === val
                  ? { background: P.textPrimary, color: P.cardBg }
                  : { background: P.cardBg, color: P.textSecondary, border: `1px solid ${P.cardBorder}` }
                }
              >
                {val}%
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Edge Tier Legend */}
      <div className="flex items-center gap-4 mb-4 text-xs" style={{ color: P.textMuted }}>
        <span style={{ color: P.textSecondary }}>LOW</span>
        <span style={{ color: P.textPrimary }}>MID</span>
        <span style={{ color: P.greenText }}>HIGH</span>
        <span style={{ color: '#15803d' }}>MAX</span>
        <span style={{ color: P.textFaint }} className="ml-1">= fair value vs book line</span>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-lg p-4" style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderTopColor: '#a855f7', borderTopWidth: '2px' }}>
          <div className="text-2xl font-bold" style={{ color: P.textPrimary }}>{totalPropsWithEdges}</div>
          <div className="text-xs" style={{ color: P.textMuted }}>Props with Edges</div>
        </div>
        <div className="rounded-lg p-4" style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderTopColor: '#8b5cf6', borderTopWidth: '2px' }}>
          <div className="text-2xl font-bold" style={{ color: '#7c3aed' }}>{totalPlayers}</div>
          <div className="text-xs" style={{ color: P.textMuted }}>Players</div>
        </div>
        <div className="rounded-lg p-4" style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderTopColor: '#10b981', borderTopWidth: '2px' }}>
          <div className="text-2xl font-bold" style={{ color: P.greenText }}>{gamesWithProps.length}</div>
          <div className="text-xs" style={{ color: P.textMuted }}>Games with Edges</div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg p-4 mb-6" style={{ background: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="text-sm" style={{ color: P.redText }}>{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && gamesWithProps.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 animate-spin" style={{ color: P.textMuted }} />
        </div>
      )}

      {/* Empty State */}
      {!loading && totalPropsWithEdges === 0 && !error && (
        <div className="text-center py-12">
          <TrendingUp className="w-12 h-12 mx-auto mb-4" style={{ color: P.textFaint }} />
          <h3 className="text-lg font-medium mb-2" style={{ color: P.textSecondary }}>No Player Props Edges</h3>
          <p className="text-sm" style={{ color: P.textMuted }}>
            No player prop edges detected above {minCEQ}% confidence. Try lowering the threshold or check back later.
          </p>
        </div>
      )}

      {/* Games List */}
      {!loading && gamesWithProps.length > 0 && (
        <div className="space-y-4">
          {gamesWithProps.map((game) => {
            const isExpanded = expandedGames.has(game.gameId);
            const totalEdges = Array.from(game.propsByType.values()).reduce((sum, arr) => sum + arr.length, 0);
            const bestConviction = Math.max(
              ...Array.from(game.propsByType.values()).flat().map(p => p.conviction)
            );

            return (
              <div
                key={game.gameId}
                className="rounded-lg overflow-hidden"
                style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderLeftColor: getSportBorderColor(game.sport), borderLeftWidth: '3px' }}
              >
                {/* Game Header */}
                <button
                  onClick={() => toggleGame(game.gameId)}
                  className="w-full px-4 py-3 transition-colors"
                  style={{ background: P.headerBar, borderBottom: `1px solid ${P.cardBorder}` }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4" style={{ color: P.textMuted }} />
                      ) : (
                        <ChevronRight className="w-4 h-4" style={{ color: P.textMuted }} />
                      )}
                      <span className="text-lg">{getSportEmoji(game.sport)}</span>
                      <span className="font-semibold" style={{ color: P.textPrimary }}>
                        {game.awayTeam} @ {game.homeTeam}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded border ${getCEQBadgeColor(bestConviction)}`}>
                        {totalEdges} edge{totalEdges !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium" style={{ color: formatTime(game.commenceTime) === 'LIVE' ? '#dc2626' : P.textMuted }}>
                        {formatTime(game.commenceTime)}
                      </span>
                      <Link
                        href={`/edge/portal/sports/game/${game.gameId}?sport=${game.sport}`}
                        onClick={(e) => e.stopPropagation()}
                        className="transition-colors hover:opacity-70"
                        style={{ color: P.textMuted }}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                </button>

                {/* Props by Type */}
                {isExpanded && (
                  <div className="p-3 space-y-4">
                    {getSortedPropTypes(game.propsByType).map((propType) => {
                      const props = game.propsByType.get(propType)!;
                      const propLabel = PROP_TYPE_LABELS[propType] || propType;

                      return (
                        <div key={propType}>
                          {/* Prop Type Header */}
                          <div className="flex items-center gap-2 mb-2 px-2">
                            <TrendingUp className="w-3.5 h-3.5" style={{ color: '#7c3aed' }} />
                            <span className="text-sm font-semibold" style={{ color: P.textPrimary }}>{propLabel}</span>
                            <span className="text-xs" style={{ color: P.textMuted }}>({props.length})</span>
                          </div>

                          {/* Table Header */}
                          <div className="hidden lg:grid gap-0 px-3 py-1.5 text-[10px] font-medium uppercase tracking-wide" style={{ gridTemplateColumns: '3fr 1fr 1.5fr 1.5fr 2.5fr 1fr', color: P.textMuted }}>
                            <div>Player</div>
                            <div className="text-center">Fair</div>
                            <div className="text-center">Over</div>
                            <div className="text-center">Under</div>
                            <div className="text-center">Edge</div>
                            <div className="text-center">Score</div>
                          </div>

                          {/* Props Rows */}
                          <div>
                            {props.map((prop, idx) => {
                              const propKey = `${game.gameId}|${prop.player}|${prop.propType}|${prop.fairLine}`;
                              const isPropExpanded = expandedProps.has(propKey);
                              const history = propHistory[propKey];
                              const isLoadingHist = loadingHistory.has(propKey);

                              // Selected book odds
                              const myOver = prop.retailOverOdds.find(o => o.book.toLowerCase() === selectedBook);
                              const myUnder = prop.retailUnderOdds.find(o => o.book.toLowerCase() === selectedBook);

                              return (
                                <div key={`${prop.player}-${prop.fairLine}-${idx}`}>
                                  {/* Main row */}
                                  <div
                                    onClick={() => toggleProp(propKey, game.gameId, prop.player, prop.propType)}
                                    className="cursor-pointer transition-colors"
                                    style={{ background: isPropExpanded ? P.neutralBg : idx % 2 === 0 ? P.neutralBg : P.cardBg }}
                                  >
                                    {/* Desktop layout */}
                                    <div className="hidden lg:grid gap-0 px-3 py-2 items-center" style={{ gridTemplateColumns: '3fr 1fr 1.5fr 1.5fr 2.5fr 1fr' }}>
                                      {/* Player */}
                                      <div className="flex items-center gap-2">
                                        <ChevronRight className={`w-3 h-3 transition-transform flex-shrink-0 ${isPropExpanded ? 'rotate-90' : ''}`} style={{ color: P.textMuted }} />
                                        <span className="text-sm font-semibold truncate" style={{ color: P.textPrimary }}>
                                          {prop.player}
                                        </span>
                                      </div>

                                      {/* Fair Line */}
                                      <div className="text-center">
                                        <span className="text-sm font-mono" style={{ color: '#ea580c' }}>{prop.fairLine}</span>
                                      </div>

                                      {/* Over odds (selected book) */}
                                      <div className="text-center">
                                        <span className="text-xs font-mono" style={{ color: prop.edgeSide === 'Over' ? P.greenText : P.textSecondary }}>
                                          {myOver ? `O ${formatOdds(myOver.odds)}` : '—'}
                                        </span>
                                      </div>

                                      {/* Under odds (selected book) */}
                                      <div className="text-center">
                                        <span className="text-xs font-mono" style={{ color: prop.edgeSide === 'Under' ? P.greenText : P.textSecondary }}>
                                          {myUnder ? `U ${formatOdds(myUnder.odds)}` : '—'}
                                        </span>
                                      </div>

                                      {/* Edge */}
                                      <div className="text-center">
                                        <div className="flex items-center justify-center gap-1">
                                          <span className="text-xs font-semibold" style={{ color: P.textPrimary }}>
                                            {prop.edgeSide} {prop.edgeLine}
                                          </span>
                                        </div>
                                        <div className="flex items-center justify-center gap-1">
                                          <span className={`text-[10px] ${EDGE_TIER_COLORS[prop.edgeTier]}`}>
                                            {prop.edgePct.toFixed(1)}% {EDGE_TIER_LABELS[prop.edgeTier]}
                                          </span>
                                          {prop.altBookHint && (
                                            <span className="text-[9px] px-1 py-px rounded" style={{ color: '#7c3aed', background: '#f3e8ff', border: '1px solid #c4b5fd' }}>
                                              ALT
                                            </span>
                                          )}
                                        </div>
                                      </div>

                                      {/* Conviction Score */}
                                      <div className="text-center">
                                        <div className="text-sm font-bold font-mono" style={{ color: getConvictionColor(prop.conviction) }}>
                                          {prop.conviction}
                                        </div>
                                        <div className="text-[9px]" style={{ color: P.textMuted }}>
                                          {prop.edgeType === 'line' ? 'LINE' : 'PRICE'}
                                        </div>
                                      </div>
                                    </div>

                                    {/* Mobile layout */}
                                    <div className="lg:hidden px-3 py-2">
                                      <div className="flex items-center justify-between mb-1">
                                        <div className="flex items-center gap-2">
                                          <ChevronRight className={`w-3 h-3 transition-transform flex-shrink-0 ${isPropExpanded ? 'rotate-90' : ''}`} style={{ color: P.textMuted }} />
                                          <span className="text-sm font-semibold" style={{ color: P.textPrimary }}>{prop.player}</span>
                                        </div>
                                        <div className="text-sm font-bold font-mono" style={{ color: getConvictionColor(prop.conviction) }}>
                                          {prop.conviction}
                                        </div>
                                      </div>
                                      <div className="flex items-center gap-3 text-xs pl-5">
                                        <span className="font-mono" style={{ color: '#ea580c' }}>{prop.fairLine}</span>
                                        <span className="font-semibold" style={{ color: P.textPrimary }}>
                                          {prop.edgeSide} {prop.edgeLine}
                                        </span>
                                        <span className={EDGE_TIER_COLORS[prop.edgeTier]}>
                                          {prop.edgePct.toFixed(1)}% {EDGE_TIER_LABELS[prop.edgeTier]}
                                        </span>
                                      </div>
                                    </div>
                                  </div>

                                  {/* Expandable Detail Panel */}
                                  {isPropExpanded && (() => {
                                    // Compute full signals with history for expanded view
                                    const fullSignals = computePropSignals({
                                      fairSource: prop.fairSource,
                                      edgeSide: prop.edgeSide!,
                                      edgePct: prop.edgePct,
                                      fairLine: prop.fairLine,
                                      edgeLine: prop.edgeLine,
                                      gameComposite: prop.gameComposite,
                                      altBookHint: prop.altBookHint,
                                      edgeOdds: prop.edgeOdds,
                                    }, history || null);
                                    const fullConviction = computeConviction(fullSignals);
                                    const narrative = generatePropNarrative({
                                      edgeSide: prop.edgeSide!,
                                      edgePct: prop.edgePct,
                                      fairLine: prop.fairLine,
                                      edgeLine: prop.edgeLine,
                                      propTypeLabel: prop.propTypeLabel,
                                      edgeType: prop.edgeType,
                                      fairSource: prop.fairSource,
                                    }, fullSignals, history || null);

                                    return (
                                      <div className="px-4 py-3" style={{ background: P.chartBg, borderTop: `1px solid ${P.cardBorder}` }}>
                                        {/* Section 1: Mini Chart */}
                                        {isLoadingHist ? (
                                          <div className="flex items-center justify-center py-4 mb-3">
                                            <RefreshCw className="w-4 h-4 animate-spin" style={{ color: P.textMuted }} />
                                          </div>
                                        ) : history && history.length >= 3 ? (
                                          <div className="mb-3">
                                            <PropLineChart data={history} fairLine={prop.fairLine} fairSource={prop.fairSource} />
                                          </div>
                                        ) : null}

                                        {/* Section 2: Over / Under Comparison Boxes */}
                                        <div className="grid grid-cols-2 gap-2 mb-3">
                                          {/* Over box */}
                                          <div className="rounded-lg p-2.5" style={{ background: P.cardBg, border: `1px solid ${prop.edgeSide === 'Over' ? P.greenBorder : P.cardBorder}` }}>
                                            <div className="text-[10px] font-semibold uppercase tracking-wide mb-1.5" style={{ color: prop.edgeSide === 'Over' ? P.greenText : P.textMuted }}>
                                              Over
                                            </div>
                                            <div className="flex justify-between items-baseline mb-0.5">
                                              <span className="text-[10px]" style={{ color: P.textMuted }}>Book</span>
                                              <span className="text-sm font-mono font-bold" style={{ color: P.textPrimary }}>
                                                {myOver ? `${myOver.line} (${formatOdds(myOver.odds)})` : '\u2014'}
                                              </span>
                                            </div>
                                            <div className="flex justify-between items-baseline">
                                              <span className="text-[10px]" style={{ color: P.textMuted }}>Fair</span>
                                              <span className="text-sm font-mono font-bold" style={{ color: '#ea580c' }}>{fmtLine(prop.fairLine)}</span>
                                            </div>
                                            {prop.edgeSide === 'Over' && (
                                              <div className="mt-1.5 pt-1.5" style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                                                <span className="text-xs font-semibold" style={{ color: P.greenText }}>
                                                  +{prop.edgePct.toFixed(1)}% {prop.edgeType === 'line' ? 'Line Edge' : 'Price Edge'}
                                                </span>
                                              </div>
                                            )}
                                          </div>
                                          {/* Under box */}
                                          <div className="rounded-lg p-2.5" style={{ background: P.cardBg, border: `1px solid ${prop.edgeSide === 'Under' ? P.greenBorder : P.cardBorder}` }}>
                                            <div className="text-[10px] font-semibold uppercase tracking-wide mb-1.5" style={{ color: prop.edgeSide === 'Under' ? P.greenText : P.textMuted }}>
                                              Under
                                            </div>
                                            <div className="flex justify-between items-baseline mb-0.5">
                                              <span className="text-[10px]" style={{ color: P.textMuted }}>Book</span>
                                              <span className="text-sm font-mono font-bold" style={{ color: P.textPrimary }}>
                                                {myUnder ? `${myUnder.line} (${formatOdds(myUnder.odds)})` : '\u2014'}
                                              </span>
                                            </div>
                                            <div className="flex justify-between items-baseline">
                                              <span className="text-[10px]" style={{ color: P.textMuted }}>Fair</span>
                                              <span className="text-sm font-mono font-bold" style={{ color: '#ea580c' }}>{fmtLine(prop.fairLine)}</span>
                                            </div>
                                            {prop.edgeSide === 'Under' && (
                                              <div className="mt-1.5 pt-1.5" style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                                                <span className="text-xs font-semibold" style={{ color: P.greenText }}>
                                                  +{prop.edgePct.toFixed(1)}% {prop.edgeType === 'line' ? 'Line Edge' : 'Price Edge'}
                                                </span>
                                              </div>
                                            )}
                                          </div>
                                        </div>

                                        {/* Section 3: WHY THIS PRICE Signal Bars */}
                                        <div className="mb-3 rounded-lg p-2.5" style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}` }}>
                                          <div className="text-[10px] font-semibold uppercase tracking-widest mb-2" style={{ color: P.textMuted }}>Why This Price</div>
                                          {SIGNAL_LABELS.map(({ key, label }) => {
                                            const value = fullSignals[key];
                                            return (
                                              <div key={key} className="flex items-center gap-2 mb-1">
                                                <span className="text-[10px] w-[88px] text-right shrink-0" style={{ color: P.textSecondary }}>{label}</span>
                                                <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: P.neutralBg }}>
                                                  <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, background: getSignalBarColor(value) }} />
                                                </div>
                                                <span className="text-[10px] font-mono w-5 text-right shrink-0" style={{ color: getSignalBarColor(value) }}>{value}</span>
                                              </div>
                                            );
                                          })}
                                        </div>

                                        {/* Section 4: Conviction Score + Fair Source */}
                                        <div className="flex items-center justify-between mb-2">
                                          <div className="flex items-center gap-3">
                                            <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: P.textMuted }}>Conviction</span>
                                            <span className="text-xl font-bold font-mono" style={{ color: getConvictionColor(fullConviction) }}>{fullConviction}</span>
                                          </div>
                                          <div className="text-[10px]" style={{ color: P.textMuted }}>
                                            Fair: <span className="font-mono" style={{ color: '#ea580c' }}>{fmtLine(prop.fairLine)}</span>
                                            <span className="ml-1">({prop.fairSource === 'pinnacle' ? 'Pinnacle' : 'consensus'})</span>
                                            {prop.altBookHint && (
                                              <span className="ml-2" style={{ color: '#7c3aed' }}>{prop.altBookHint}</span>
                                            )}
                                          </div>
                                        </div>

                                        {/* Section 5: One-Line Narrative */}
                                        <p className="text-xs leading-relaxed" style={{ color: P.textSecondary }}>
                                          {narrative}
                                        </p>
                                      </div>
                                    );
                                  })()}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
