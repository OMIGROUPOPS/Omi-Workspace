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
  // Contrarian: edge opposes significant line movement direction
  isContrarian: boolean;
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

// Inline SVG step-line chart with interactive hover, conditional fair line, and source attribution
function PropLineChart({ data, fairLine, fairSource }: { data: any[]; fairLine: number; fairSource: 'pinnacle' | 'consensus' }) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const W = 680, H = 140, PAD_X = 40, PAD_R = 120, PAD_Y = 20;
  const lines = data.map(d => Number(d.line)).filter(n => !isNaN(n));
  if (lines.length < 2) return null;

  // Show fair line only when it differs from at least one book line (not stagnant)
  const showFairLine = lines.some(l => Math.abs(l - fairLine) >= 0.25);

  // Include fair line in range only when shown
  const allValues = showFairLine ? [...lines, fairLine] : lines;
  const minLine = Math.min(...allValues);
  const maxLine = Math.max(...allValues);
  const range = maxLine - minLine || 1;

  const chartW = W - PAD_X - PAD_R;
  const xStep = chartW / (lines.length - 1);
  const valToY = (val: number) => PAD_Y + (1 - (val - minLine) / range) * (H - PAD_Y * 2);

  // Build step-line path
  const points: string[] = [];
  lines.forEach((val, i) => {
    const x = PAD_X + i * xStep;
    const y = valToY(val);
    if (i === 0) {
      points.push(`M ${x} ${y}`);
    } else {
      points.push(`H ${x}`);
      points.push(`V ${y}`);
    }
  });
  const pathD = points.join(' ');
  const fairY = valToY(fairLine);

  // Y-axis labels
  const yLabels = [minLine, (minLine + maxLine) / 2, maxLine];

  // X-axis timestamps
  const firstTime = data[0]?.snapshot_time ? new Date(data[0].snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '';
  const lastTime = data[data.length - 1]?.snapshot_time ? new Date(data[data.length - 1].snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';

  // Fair line label with source attribution
  const fairValStr = Number.isInteger(fairLine) ? String(fairLine) : fairLine.toFixed(1);
  const srcTag = fairSource === 'pinnacle' ? 'PIN' : 'consensus';
  const fairLabel = `Fair: ${fairValStr} (${srcTag})`;
  const labelX = W - PAD_R + 8;

  // --- Hover logic ---
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * W;
    const idx = Math.round((mouseX - PAD_X) / xStep);
    setHoverIdx(Math.max(0, Math.min(lines.length - 1, idx)));
  };
  const handleMouseLeave = () => setHoverIdx(null);

  // Hover data
  const hd = hoverIdx !== null ? data[hoverIdx] : null;
  const hx = hoverIdx !== null ? PAD_X + hoverIdx * xStep : 0;
  const hy = hoverIdx !== null ? valToY(lines[hoverIdx]) : 0;
  const hTime = hd?.snapshot_time
    ? new Date(hd.snapshot_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true })
    : '';
  const hLine = hoverIdx !== null ? lines[hoverIdx] : 0;
  const hBook = hd?.book_key || '';
  const fmtBk = (b: string) => b.toLowerCase() === 'fanduel' ? 'FD' : b.toLowerCase() === 'draftkings' ? 'DK' : b.slice(0, 3).toUpperCase();
  const fmtO = (o: number) => o > 0 ? `+${o}` : `${o}`;
  const tipL1 = hTime;
  const tipL2 = `Line: ${Number.isInteger(hLine) ? hLine : hLine.toFixed(1)} (${fmtBk(hBook)})`;
  const tipL3 = hd?.over_odds != null && hd?.under_odds != null
    ? `O ${fmtO(hd.over_odds)} / U ${fmtO(hd.under_odds)}`
    : hd?.over_odds != null ? `O ${fmtO(hd.over_odds)}` : '';
  const tipW = 180;
  const tipX = hoverIdx !== null && hx + tipW + 10 > W - PAD_R ? hx - tipW - 10 : hx + 10;

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${W} ${H}`}
      className="w-full max-w-[680px] cursor-crosshair select-none"
      style={{ height: '140px' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Grid lines */}
      {yLabels.map((val, i) => {
        const y = valToY(val);
        return (
          <g key={i}>
            <line x1={PAD_X} y1={y} x2={W - PAD_R} y2={y} stroke={P.cardBorder} strokeWidth="1" />
            <text x={PAD_X - 4} y={y + 3} textAnchor="end" fill={P.textMuted} fontSize="9" fontFamily="monospace">
              {Number.isInteger(val) ? val : val.toFixed(1)}
            </text>
          </g>
        );
      })}
      {/* Fair line (only when non-stagnant) */}
      {showFairLine && (
        <>
          <line x1={PAD_X} y1={fairY} x2={W - PAD_R} y2={fairY} stroke="#ea580c" strokeWidth="1.5" strokeDasharray="6 4" opacity="0.85" />
          <rect x={labelX - 4} y={fairY - 9} width={tipW - 60} height={18} rx="4" fill="#fff7ed" stroke="#fed7aa" strokeWidth="0.5" />
          <text x={labelX} y={fairY + 4} fill="#ea580c" fontSize="11" fontFamily="monospace" fontWeight="bold">
            {fairLabel}
          </text>
          {/* Convergence fill */}
          {lines.map((val, i) => {
            if (i === lines.length - 1) return null;
            const x1 = PAD_X + i * xStep;
            const x2 = PAD_X + (i + 1) * xStep;
            const bookY = valToY(val);
            return (
              <rect
                key={i}
                x={x1}
                y={Math.min(bookY, fairY)}
                width={x2 - x1}
                height={Math.abs(bookY - fairY)}
                fill={bookY < fairY ? 'rgba(234,88,12,0.08)' : 'rgba(234,88,12,0.05)'}
              />
            );
          })}
        </>
      )}
      {/* Step-line path (book line) */}
      <path d={pathD} fill="none" stroke={P.textSecondary} strokeWidth="2" />
      {/* Dot on last point */}
      <circle cx={PAD_X + (lines.length - 1) * xStep} cy={valToY(lines[lines.length - 1])} r="3" fill={P.textSecondary} />
      {/* X-axis labels */}
      <text x={PAD_X} y={H - 2} fill={P.textMuted} fontSize="8" fontFamily="monospace">{firstTime}</text>
      <text x={W - PAD_R} y={H - 2} textAnchor="end" fill={P.textMuted} fontSize="8" fontFamily="monospace">{lastTime}</text>
      {/* Hover crosshair + tooltip */}
      {hoverIdx !== null && (
        <g>
          <line x1={hx} y1={PAD_Y} x2={hx} y2={H - PAD_Y} stroke={P.textMuted} strokeWidth="1" strokeDasharray="2 2" />
          <circle cx={hx} cy={hy} r="4" fill={P.cardBg} stroke={P.textPrimary} strokeWidth="1.5" />
          <rect x={tipX} y={8} width={tipW} height={50} rx="4" fill={P.cardBg} stroke={P.cardBorder} strokeWidth="1" />
          <text x={tipX + 6} y={22} fill={P.textMuted} fontSize="9" fontFamily="monospace">{tipL1}</text>
          <text x={tipX + 6} y={35} fill={P.textPrimary} fontSize="10" fontFamily="monospace" fontWeight="bold">{tipL2}</text>
          <text x={tipX + 6} y={48} fill={P.textSecondary} fontSize="9" fontFamily="monospace">{tipL3}</text>
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
            compositeMap.set(row.game_id, Number(row.composite_total));
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
            composite: Math.round((row.composite_score ?? 50)),
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

          // Find best edge across all retail entries and sides
          let bestEdgePct = 0;
          let bestEdgeSide: 'Over' | 'Under' | null = null;
          let bestEdgeBook = '';
          let bestEdgeOdds = 0;
          let bestEdgeLine = 0;

          for (const entry of retailEntries) {
            const lineDiff = entry.line - fairLine;

            if (Math.abs(lineDiff) >= 0.5) {
              // Line differs from fair value: edge = |diff| × 3% per point
              const edgePct = Math.abs(lineDiff) * 3;
              // book_line < fair → Over is easier to hit → Over edge
              // book_line > fair → Under is easier to hit → Under edge
              const side: 'Over' | 'Under' = lineDiff < 0 ? 'Over' : 'Under';
              const odds = side === 'Over' ? entry.overOdds : entry.underOdds;

              if (odds && edgePct > bestEdgePct) {
                bestEdgePct = edgePct;
                bestEdgeSide = side;
                bestEdgeBook = entry.book;
                bestEdgeOdds = odds;
                bestEdgeLine = entry.line;
              }
            } else {
              // Same line — compare implied probabilities
              if (pinnacleEntry) {
                // Compare retail odds vs Pinnacle (sharp reference)
                if (entry.overOdds && pinnacleEntry.overOdds) {
                  const retailProb = oddsToProb(entry.overOdds);
                  const sharpProb = oddsToProb(pinnacleEntry.overOdds);
                  // Positive edge = retail offers better odds than sharp
                  const edge = (sharpProb - retailProb) * 100;
                  if (edge > bestEdgePct) {
                    bestEdgePct = edge;
                    bestEdgeSide = 'Over';
                    bestEdgeBook = entry.book;
                    bestEdgeOdds = entry.overOdds;
                    bestEdgeLine = entry.line;
                  }
                }
                if (entry.underOdds && pinnacleEntry.underOdds) {
                  const retailProb = oddsToProb(entry.underOdds);
                  const sharpProb = oddsToProb(pinnacleEntry.underOdds);
                  const edge = (sharpProb - retailProb) * 100;
                  if (edge > bestEdgePct) {
                    bestEdgePct = edge;
                    bestEdgeSide = 'Under';
                    bestEdgeBook = entry.book;
                    bestEdgeOdds = entry.underOdds;
                    bestEdgeLine = entry.line;
                  }
                }
              } else if (retailEntries.length > 1) {
                // No Pinnacle — cross-book comparison on same line
                for (const side of ['Over', 'Under'] as const) {
                  const oddsKey = side === 'Over' ? 'overOdds' : 'underOdds';
                  const sameLineOdds = retailEntries
                    .filter(e => Math.abs(e.line - entry.line) < 0.25 && e[oddsKey] !== null)
                    .map(e => ({ book: e.book, odds: e[oddsKey]!, line: e.line }));

                  if (sameLineOdds.length >= 2) {
                    const best = sameLineOdds.reduce((a, b) => a.odds > b.odds ? a : b);
                    const worst = sameLineOdds.reduce((a, b) => a.odds < b.odds ? a : b);
                    const edge = (oddsToProb(worst.odds) - oddsToProb(best.odds)) * 100;
                    if (edge > bestEdgePct) {
                      bestEdgePct = edge;
                      bestEdgeSide = side;
                      bestEdgeBook = best.book;
                      bestEdgeOdds = best.odds;
                      bestEdgeLine = best.line;
                    }
                  }
                }
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

          // Apply min confidence filter
          if (confidence < minCEQ) continue;

          // Build retail odds arrays for display
          const retailOverOdds = retailEntries
            .filter(e => e.overOdds !== null)
            .map(e => ({ book: e.book, odds: e.overOdds!, line: e.line }));
          const retailUnderOdds = retailEntries
            .filter(e => e.underOdds !== null)
            .map(e => ({ book: e.book, odds: e.underOdds!, line: e.line }));

          // Contrarian: edge direction opposes significant line movement
          // If book line moved >=2pts from fair value AND edge opposes that movement
          const lineDelta = bestEdgeLine - fairLine;
          const isContrarian = Math.abs(lineDelta) >= 2 && (
            (lineDelta > 0 && bestEdgeSide === 'Under') || // line moved UP, model says Under
            (lineDelta < 0 && bestEdgeSide === 'Over')     // line moved DOWN, model says Over
          );

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
            edgeBook: bestEdgeBook,
            edgeLine: bestEdgeLine,
            gameComposite,
            compositeModifier: modifier,
            fairSource: hasPinnacle ? 'pinnacle' : 'consensus',
            isContrarian,
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
  }, [selectedSport, minCEQ]);

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
            Edges on player prop markets (FanDuel & DraftKings)
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

      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
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
          <span className="text-xs" style={{ color: P.textMuted }}>Min Conf:</span>
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
            const bestCEQ = Math.max(
              ...Array.from(game.propsByType.values()).flat().map(p => p.edgeCEQ)
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
                      <span className={`text-xs px-2 py-0.5 rounded border ${getCEQBadgeColor(bestCEQ)}`}>
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
                          <div className="hidden lg:grid gap-0 px-3 py-1.5 text-[10px] font-medium uppercase tracking-wide" style={{ gridTemplateColumns: '3fr 1fr 2.5fr 2.5fr 2fr 1fr', color: P.textMuted }}>
                            <div>Player</div>
                            <div className="text-center">Line</div>
                            <div className="text-center">Over (FD / DK)</div>
                            <div className="text-center">Under (FD / DK)</div>
                            <div className="text-center">Best Edge</div>
                            <div className="text-center">Conf</div>
                          </div>

                          {/* Props Rows */}
                          <div>
                            {props.map((prop, idx) => {
                              const propKey = `${game.gameId}|${prop.player}|${prop.propType}|${prop.fairLine}`;
                              const isPropExpanded = expandedProps.has(propKey);
                              const history = propHistory[propKey];
                              const isLoadingHist = loadingHistory.has(propKey);

                              // Find FD and DK odds for over and under
                              const fdOver = prop.retailOverOdds.find(o => o.book.toLowerCase() === 'fanduel');
                              const dkOver = prop.retailOverOdds.find(o => o.book.toLowerCase() === 'draftkings');
                              const fdUnder = prop.retailUnderOdds.find(o => o.book.toLowerCase() === 'fanduel');
                              const dkUnder = prop.retailUnderOdds.find(o => o.book.toLowerCase() === 'draftkings');

                              // Determine best over/under odds for highlighting
                              const bestOverOdds = fdOver && dkOver ? (fdOver.odds >= dkOver.odds ? 'fd' : 'dk') : fdOver ? 'fd' : dkOver ? 'dk' : null;
                              const bestUnderOdds = fdUnder && dkUnder ? (fdUnder.odds >= dkUnder.odds ? 'fd' : 'dk') : fdUnder ? 'fd' : dkUnder ? 'dk' : null;

                              return (
                                <div key={`${prop.player}-${prop.fairLine}-${idx}`}>
                                  {/* Main row */}
                                  <div
                                    onClick={() => toggleProp(propKey, game.gameId, prop.player, prop.propType)}
                                    className="cursor-pointer transition-colors"
                                    style={{ background: isPropExpanded ? P.neutralBg : idx % 2 === 0 ? P.neutralBg : P.cardBg }}
                                  >
                                    {/* Desktop layout */}
                                    <div className="hidden lg:grid gap-0 px-3 py-2 items-center" style={{ gridTemplateColumns: '3fr 1fr 2.5fr 2.5fr 2fr 1fr' }}>
                                      {/* Player */}
                                      <div className="flex items-center gap-2">
                                        <ChevronRight className={`w-3 h-3 transition-transform flex-shrink-0 ${isPropExpanded ? 'rotate-90' : ''}`} style={{ color: P.textMuted }} />
                                        <span className="text-sm font-semibold truncate" style={{ color: P.textPrimary }}>
                                          {prop.player}
                                        </span>
                                      </div>

                                      {/* Fair Line */}
                                      <div className="text-center">
                                        <span className="text-sm font-mono" style={{ color: P.textPrimary }}>{prop.fairLine}</span>
                                      </div>

                                      {/* Over (FD / DK) */}
                                      <div className="text-center flex items-center justify-center gap-2">
                                        <span className="text-xs font-mono" style={{ color: bestOverOdds === 'fd' ? P.greenText : P.textSecondary }}>
                                          {fdOver ? `FD ${formatOdds(fdOver.odds)}` : <span style={{ color: P.textFaint }}>FD —</span>}
                                        </span>
                                        <span className="text-[10px]" style={{ color: P.textFaint }}>/</span>
                                        <span className="text-xs font-mono" style={{ color: bestOverOdds === 'dk' ? P.greenText : P.textSecondary }}>
                                          {dkOver ? `DK ${formatOdds(dkOver.odds)}` : <span style={{ color: P.textFaint }}>DK —</span>}
                                        </span>
                                      </div>

                                      {/* Under (FD / DK) */}
                                      <div className="text-center flex items-center justify-center gap-2">
                                        <span className="text-xs font-mono" style={{ color: bestUnderOdds === 'fd' ? P.greenText : P.textSecondary }}>
                                          {fdUnder ? `FD ${formatOdds(fdUnder.odds)}` : <span style={{ color: P.textFaint }}>FD —</span>}
                                        </span>
                                        <span className="text-[10px]" style={{ color: P.textFaint }}>/</span>
                                        <span className="text-xs font-mono" style={{ color: bestUnderOdds === 'dk' ? P.greenText : P.textSecondary }}>
                                          {dkUnder ? `DK ${formatOdds(dkUnder.odds)}` : <span style={{ color: P.textFaint }}>DK —</span>}
                                        </span>
                                      </div>

                                      {/* Best Edge */}
                                      <div className="text-center">
                                        <div className="flex items-center justify-center gap-1">
                                          <span className="text-xs font-semibold" style={{ color: P.textPrimary }}>
                                            {prop.edgeSide} {prop.edgeLine}
                                          </span>
                                          <span className="text-[10px]" style={{ color: P.textMuted }}>@{formatBook(prop.edgeBook)}</span>
                                          {prop.isContrarian && (
                                            <span className="text-[9px] font-bold px-1 py-px rounded" style={{ color: '#b45309', background: '#fef3c7', border: '1px solid #fcd34d' }}>
                                              CTR
                                            </span>
                                          )}
                                        </div>
                                        <div className={`text-[10px] ${EDGE_TIER_COLORS[prop.edgeTier]}`}>
                                          {prop.edgePct.toFixed(1)}% {EDGE_TIER_LABELS[prop.edgeTier]}
                                        </div>
                                      </div>

                                      {/* CEQ */}
                                      <div className="text-center">
                                        <div className={`text-sm font-bold ${getCEQColor(prop.edgeCEQ)}`}>
                                          {prop.edgeCEQ}%
                                        </div>
                                        {prop.compositeModifier > 1.0 && (
                                          <div className="text-[10px]" style={{ color: P.textMuted }}>
                                            +{Math.round((prop.compositeModifier - 1) * 100)}% boost
                                          </div>
                                        )}
                                      </div>
                                    </div>

                                    {/* Mobile layout */}
                                    <div className="lg:hidden px-3 py-2">
                                      <div className="flex items-center justify-between mb-1">
                                        <div className="flex items-center gap-2">
                                          <ChevronRight className={`w-3 h-3 transition-transform flex-shrink-0 ${isPropExpanded ? 'rotate-90' : ''}`} style={{ color: P.textMuted }} />
                                          <span className="text-sm font-semibold" style={{ color: P.textPrimary }}>{prop.player}</span>
                                        </div>
                                        <div className={`text-sm font-bold ${getCEQColor(prop.edgeCEQ)}`}>
                                          {prop.edgeCEQ}%
                                        </div>
                                      </div>
                                      <div className="flex items-center gap-3 text-xs pl-5">
                                        <span className="font-mono" style={{ color: P.textPrimary }}>{prop.fairLine}</span>
                                        <span className="font-semibold" style={{ color: P.textPrimary }}>
                                          {prop.edgeSide} {prop.edgeLine} @{formatBook(prop.edgeBook)}
                                        </span>
                                        <span className={EDGE_TIER_COLORS[prop.edgeTier]}>
                                          {prop.edgePct.toFixed(1)}% {EDGE_TIER_LABELS[prop.edgeTier]}
                                        </span>
                                        {prop.isContrarian && (
                                          <span className="text-[9px] font-bold px-1 py-px rounded" style={{ color: '#b45309', background: '#fef3c7', border: '1px solid #fcd34d' }}>
                                            CTR
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {/* Expandable Detail Panel */}
                                  {isPropExpanded && (
                                    <div className="px-4 py-3" style={{ background: P.chartBg, borderTop: `1px solid ${P.cardBorder}` }}>
                                      {/* Line History Chart or Comparison Bar */}
                                      <div className="mb-3">
                                        {isLoadingHist ? (
                                          <div className="flex items-center justify-center py-6">
                                            <RefreshCw className="w-4 h-4 animate-spin" style={{ color: P.textMuted }} />
                                          </div>
                                        ) : history && history.length > 1 ? (
                                          <PropLineChart data={history} fairLine={prop.fairLine} fairSource={prop.fairSource} />
                                        ) : (
                                          <PropComparisonBar prop={prop} />
                                        )}
                                      </div>

                                      {/* Detail Row */}
                                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                                        {/* Line movement */}
                                        {history && history.length > 1 && (
                                          <div style={{ color: P.textSecondary }}>
                                            <span style={{ color: P.textMuted }}>Opened:</span>{' '}
                                            <span className="font-mono" style={{ color: P.textPrimary }}>{history[0].line}</span>
                                            <span style={{ color: P.textFaint }} className="mx-1">&rarr;</span>
                                            <span style={{ color: P.textMuted }}>Current:</span>{' '}
                                            <span className="font-mono" style={{ color: P.textPrimary }}>{history[history.length - 1].line}</span>
                                            <span className="ml-1 font-mono" style={{ color: history[history.length - 1].line - history[0].line > 0 ? P.greenText : history[history.length - 1].line - history[0].line < 0 ? P.redText : P.textMuted }}>
                                              ({history[history.length - 1].line - history[0].line > 0 ? '+' : ''}{(history[history.length - 1].line - history[0].line).toFixed(1)})
                                            </span>
                                          </div>
                                        )}

                                        {/* Book odds summary */}
                                        <div style={{ color: P.textSecondary }}>
                                          <span style={{ color: P.textMuted }}>FD:</span>{' '}
                                          <span className="font-mono" style={{ color: P.greenText }}>O {fdOver ? formatOdds(fdOver.odds) : '—'}</span>
                                          <span style={{ color: P.textFaint }} className="mx-1">/</span>
                                          <span className="font-mono" style={{ color: P.redText }}>U {fdUnder ? formatOdds(fdUnder.odds) : '—'}</span>
                                          <span style={{ color: P.neutralBorder }} className="mx-2">|</span>
                                          <span style={{ color: P.textMuted }}>DK:</span>{' '}
                                          <span className="font-mono" style={{ color: P.greenText }}>O {dkOver ? formatOdds(dkOver.odds) : '—'}</span>
                                          <span style={{ color: P.textFaint }} className="mx-1">/</span>
                                          <span className="font-mono" style={{ color: P.redText }}>U {dkUnder ? formatOdds(dkUnder.odds) : '—'}</span>
                                        </div>

                                        {/* Best edge + fair source + contrarian */}
                                        <div style={{ color: P.textSecondary }}>
                                          <span style={{ color: P.textMuted }}>Best:</span>{' '}
                                          <span className="font-semibold" style={{ color: P.textPrimary }}>
                                            {formatBook(prop.edgeBook)} {prop.edgeSide} {prop.edgeLine} {formatOdds(prop.edgeOdds)}
                                          </span>
                                          <span className={`ml-1 ${EDGE_TIER_COLORS[prop.edgeTier]}`}>
                                            {prop.edgePct.toFixed(1)}% {EDGE_TIER_LABELS[prop.edgeTier]}
                                          </span>
                                          {prop.isContrarian && (
                                            <span className="ml-1.5 text-[10px] font-bold px-1 py-px rounded" style={{ color: '#b45309', background: '#fef3c7', border: '1px solid #fcd34d' }}>
                                              CONTRARIAN
                                            </span>
                                          )}
                                          {prop.compositeModifier > 1.0 && (
                                            <span className="ml-1" style={{ color: P.textMuted }}>
                                              (game composite boost)
                                            </span>
                                          )}
                                        </div>
                                      </div>

                                      {/* Fair source + contrarian context */}
                                      <div className="flex items-center gap-3 mt-2 text-[10px]">
                                        <span style={{ color: P.textMuted }}>
                                          Fair: <span className="font-mono" style={{ color: P.textSecondary }}>{Number.isInteger(prop.fairLine) ? prop.fairLine : prop.fairLine.toFixed(1)}</span>
                                          <span className="ml-1" style={{ color: P.textMuted }}>({prop.fairSource === 'pinnacle' ? 'PIN current' : 'consensus'})</span>
                                        </span>
                                        {prop.isContrarian && history && history.length > 1 && (
                                          <span style={{ color: '#b45309' }}>
                                            Line moved {history[history.length - 1].line - history[0].line > 0 ? '+' : ''}{(history[history.length - 1].line - history[0].line).toFixed(1)} but model says {prop.edgeSide}
                                          </span>
                                        )}
                                        {prop.isContrarian && !(history && history.length > 1) && (
                                          <span style={{ color: '#b45309' }}>
                                            Book line {prop.edgeLine} vs fair {prop.fairLine} ({prop.edgeLine > prop.fairLine ? '+' : ''}{(prop.edgeLine - prop.fairLine).toFixed(1)}), model says {prop.edgeSide}
                                          </span>
                                        )}
                                      </div>

                                      {/* Compressed Pillar Bar */}
                                      {gamePillars[game.gameId] ? (() => {
                                        const gp = gamePillars[game.gameId];
                                        const pillars = [
                                          { key: 'EXEC', val: gp.execution },
                                          { key: 'INCV', val: gp.incentives },
                                          { key: 'SHCK', val: gp.shocks },
                                          { key: 'TIME', val: gp.timeDecay },
                                          { key: 'FLOW', val: gp.flow },
                                          { key: 'ENV', val: gp.gameEnvironment },
                                        ];
                                        const pillarColor = (v: number) =>
                                          v >= 60 ? P.greenText : v <= 40 ? P.redText : P.textSecondary;
                                        return (
                                          <div className="mt-3 pt-2" style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                                            <div className="flex items-center gap-1 text-[10px] font-mono flex-wrap">
                                              <span style={{ color: P.textMuted }} className="mr-1">Game Context:</span>
                                              {pillars.map((pl, i) => (
                                                <span key={pl.key}>
                                                  <span style={{ color: P.textMuted }}>{pl.key}</span>{' '}
                                                  <span style={{ color: pillarColor(pl.val) }}>{pl.val}</span>
                                                  {i < pillars.length - 1 && <span style={{ color: P.textFaint }} className="mx-0.5">&middot;</span>}
                                                </span>
                                              ))}
                                              <span style={{ color: P.textFaint }} className="mx-1">&rarr;</span>
                                              <span style={{ color: P.textMuted }}>Composite</span>{' '}
                                              <span style={{ color: pillarColor(gp.composite) }}>{gp.composite}</span>
                                            </div>
                                          </div>
                                        );
                                      })() : (
                                        <div className="mt-3 pt-2" style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                                          <span className="text-[10px] font-mono" style={{ color: P.textFaint }}>Game context unavailable</span>
                                        </div>
                                      )}
                                    </div>
                                  )}
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
