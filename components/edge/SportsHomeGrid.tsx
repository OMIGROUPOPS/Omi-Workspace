'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getTimeDisplay, getGameState } from '@/lib/edge/utils/game-state';
import { calculateFairSpread, calculateFairTotal, calculateFairMLFromBook, calculateFairMLFromBook3Way } from '@/lib/edge/engine/edgescout';

// --- Light theme palette ---
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

const EDGE_THRESHOLD = 1.5;
const GAMES_PER_SPORT_IN_ALL_VIEW = 6;
const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";

const BOOK_CONFIG: Record<string, { name: string; color: string; type: 'sportsbook' | 'exchange' }> = {
  fanduel:     { name: 'FanDuel',     color: '#1493ff', type: 'sportsbook' },
  draftkings:  { name: 'DraftKings',  color: '#53d337', type: 'sportsbook' },
  kalshi:      { name: 'Kalshi',      color: '#00d395', type: 'exchange' },
  polymarket:  { name: 'Polymarket',  color: '#7C3AED', type: 'exchange' },
};

const AVAILABLE_BOOKS = Object.keys(BOOK_CONFIG);

function isExchange(book: string) {
  return BOOK_CONFIG[book]?.type === 'exchange';
}

function isSoccer(sportKey: string): boolean {
  return sportKey?.includes('soccer') || false;
}

// --- Sport lists ---
const MODELED_SPORTS = [
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'basketball_ncaab', label: 'NCAAB' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF' },
  { key: 'icehockey_nhl', label: 'NHL' },
  { key: 'soccer_epl', label: 'EPL' },
];

const MODELED_SPORT_KEYS = new Set(MODELED_SPORTS.map(s => s.key));

const MORE_SPORTS = [
  { key: 'baseball_mlb', label: 'MLB' },
  { key: 'basketball_wnba', label: 'WNBA' },
  { key: 'basketball_euroleague', label: 'EuroLg' },
  { key: 'icehockey_ahl', label: 'AHL' },
  { key: 'soccer_usa_mls', label: 'MLS' },
  { key: 'soccer_spain_la_liga', label: 'La Liga' },
  { key: 'soccer_germany_bundesliga', label: 'Bundes' },
  { key: 'soccer_italy_serie_a', label: 'Serie A' },
  { key: 'soccer_france_ligue_one', label: 'Ligue 1' },
  { key: 'soccer_uefa_champs_league', label: 'UCL' },
  { key: 'soccer_uefa_europa_league', label: 'Europa' },
  { key: 'soccer_efl_champ', label: 'EFL Ch' },
  { key: 'soccer_netherlands_eredivisie', label: 'Erediv' },
  { key: 'soccer_mexico_ligamx', label: 'Liga MX' },
  { key: 'soccer_fa_cup', label: 'FA Cup' },
  { key: 'mma_mixed_martial_arts', label: 'UFC' },
  { key: 'boxing_boxing', label: 'Boxing' },
  { key: 'tennis_atp_australian_open', label: 'AUS Open' },
  { key: 'tennis_atp_french_open', label: 'FR Open' },
  { key: 'tennis_atp_us_open', label: 'US Open' },
  { key: 'tennis_atp_wimbledon', label: 'Wimbledon' },
  { key: 'golf_masters_tournament_winner', label: 'Masters' },
  { key: 'golf_pga_championship_winner', label: 'PGA' },
  { key: 'golf_us_open_winner', label: 'US Open' },
  { key: 'golf_the_open_championship_winner', label: 'The Open' },
  { key: 'icehockey_sweden_hockey_league', label: 'SHL' },
  { key: 'icehockey_liiga', label: 'Liiga' },
  { key: 'rugbyleague_nrl', label: 'NRL' },
  { key: 'aussierules_afl', label: 'AFL' },
  { key: 'cricket_ipl', label: 'IPL' },
  { key: 'cricket_big_bash', label: 'Big Bash' },
];

const ALL_SPORT_PILLS = [...MODELED_SPORTS, ...MORE_SPORTS];

const SPORT_ORDER = [
  'americanfootball_nfl', 'basketball_nba', 'icehockey_nhl', 'baseball_mlb',
  'americanfootball_ncaaf', 'basketball_ncaab', 'basketball_wnba',
  'soccer_usa_mls', 'soccer_epl', 'soccer_spain_la_liga', 'soccer_germany_bundesliga',
  'soccer_italy_serie_a', 'soccer_france_ligue_one', 'soccer_uefa_champs_league',
  'soccer_uefa_europa_league', 'soccer_efl_champ', 'soccer_netherlands_eredivisie',
  'soccer_mexico_ligamx', 'soccer_fa_cup',
  'mma_mixed_martial_arts', 'boxing_boxing',
  'tennis_atp_australian_open', 'tennis_atp_french_open', 'tennis_atp_us_open', 'tennis_atp_wimbledon',
  'golf_masters_tournament_winner', 'golf_pga_championship_winner', 'golf_us_open_winner', 'golf_the_open_championship_winner',
  'icehockey_ahl', 'icehockey_sweden_hockey_league', 'icehockey_liiga',
  'basketball_euroleague',
  'rugbyleague_nrl', 'aussierules_afl', 'cricket_ipl', 'cricket_big_bash',
];

// --- Helpers ---
function toProb(odds: number): number {
  return odds < 0 ? Math.abs(odds) / (Math.abs(odds) + 100) : 100 / (odds + 100);
}

function oddsToYesCents(odds: number): number {
  return Math.round(toProb(odds) * 100);
}

function fmtSpread(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

function fmtOdds(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

function getDisplayTeamName(teamName: string, sportKey: string): string {
  if (sportKey.includes('ncaa') || sportKey.includes('soccer') ||
      sportKey.includes('mma') || sportKey.includes('boxing') || sportKey.includes('tennis')) {
    return teamName;
  }
  const words = teamName.split(' ');
  return words[words.length - 1];
}

// Sport-specific point-to-probability rates (matches edgescout.ts)
const SPREAD_TO_PROB: Record<string, number> = {
  'basketball_nba': 0.033,
  'basketball_ncaab': 0.030,
  'americanfootball_nfl': 0.027,
  'americanfootball_ncaaf': 0.025,
  'icehockey_nhl': 0.08,
  'baseball_mlb': 0.09,
  'soccer_epl': 0.20,
};

// Total line uses ~60% of spread rate (totals are higher-variance)
const TOTAL_TO_PROB_FACTOR = 0.6;

function getProbRate(sportKey: string): number {
  return SPREAD_TO_PROB[sportKey] || 0.03;
}

// Clean implied probability edge for spread/total:
//   1. Convert OMI fair line difference to fair implied probability
//   2. Compare against book's implied probability (from odds)
//   3. Edge = (fair_prob - book_implied_prob) / book_implied_prob * 100
function spreadEdgeForSide(
  fairSpread: number, bookLine: number, bookOdds: number, sportKey: string, isHome: boolean
): number {
  const rate = getProbRate(sportKey);
  // Line difference from home perspective: negative = book line harder for home to cover
  const lineDiff = bookLine - fairSpread; // e.g. book -17.5, fair -14 → -3.5 (home must cover more)
  // Fair probability of covering this book's line: 50% adjusted by line diff
  const fairCoverProb = 0.5 + lineDiff * rate; // home cover prob at book's line
  const fairProb = isHome ? fairCoverProb : 1 - fairCoverProb;
  // Book's implied probability from odds
  const bookProb = toProb(bookOdds);
  // Edge: how much is fair prob above what book charges
  return (fairProb - bookProb) / bookProb * 100;
}

function totalEdgeForSide(
  fairTotal: number, bookLine: number, bookOdds: number, sportKey: string, isOver: boolean
): number {
  const rate = getProbRate(sportKey) * TOTAL_TO_PROB_FACTOR;
  // Line difference: positive = OMI fair is higher than book → over has edge
  const lineDiff = fairTotal - bookLine;
  const fairOverProb = 0.5 + lineDiff * rate;
  const fairProb = isOver ? fairOverProb : 1 - fairOverProb;
  const bookProb = toProb(bookOdds);
  return (fairProb - bookProb) / bookProb * 100;
}

function calcMaxEdge(fair: any, spreads: any, h2h: any, totals: any, sportKey: string): number {
  let maxEdge = 0;

  // Spread edge: implied probability comparison
  if (fair?.fair_spread != null && spreads?.line !== undefined) {
    if (spreads.homePrice != null) {
      maxEdge = Math.max(maxEdge, spreadEdgeForSide(fair.fair_spread, spreads.line, spreads.homePrice, sportKey, true));
    }
    if (spreads.awayPrice != null) {
      maxEdge = Math.max(maxEdge, spreadEdgeForSide(fair.fair_spread, spreads.line, spreads.awayPrice, sportKey, false));
    }
  }

  // ML edge: pure probability comparison (no line, odds directly convert)
  if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice !== undefined && h2h?.awayPrice !== undefined) {
    const fairHP = toProb(fair.fair_ml_home);
    const fairAP = toProb(fair.fair_ml_away);
    const bookHP = toProb(h2h.homePrice);
    const bookAP = toProb(h2h.awayPrice);
    const normBHP = bookHP / (bookHP + bookAP);
    const normBAP = bookAP / (bookHP + bookAP);
    maxEdge = Math.max(maxEdge, (fairHP - normBHP) * 100, (fairAP - normBAP) * 100);
  }

  // Total edge: implied probability comparison
  if (fair?.fair_total != null && totals?.line !== undefined) {
    if (totals.overPrice != null) {
      maxEdge = Math.max(maxEdge, totalEdgeForSide(fair.fair_total, totals.line, totals.overPrice, sportKey, true));
    }
    if (totals.underPrice != null) {
      maxEdge = Math.max(maxEdge, totalEdgeForSide(fair.fair_total, totals.line, totals.underPrice, sportKey, false));
    }
  }

  return maxEdge;
}

/** Compute fair lines on-the-fly from composite_score when composite_history is missing */
function computeFallbackFair(game: any) {
  const comp = game.composite_score != null ? game.composite_score * 100 : null;
  if (comp == null) return null;
  const spreads = game.consensus?.spreads;
  const totals = game.consensus?.totals;
  const h2h = game.consensus?.h2h;
  const fs = spreads?.line != null ? calculateFairSpread(spreads.line, comp, game.sportKey) : null;
  const ft = totals?.line != null ? calculateFairTotal(totals.line, comp, game.sportKey) : null;
  // 3-way ML for soccer, 2-way for everything else
  const drawPrice = h2h?.drawPrice ?? h2h?.draw;
  let fair_ml_home: number | null = null, fair_ml_away: number | null = null, fair_ml_draw: number | null = null;
  if (drawPrice != null && h2h?.homePrice != null && h2h?.awayPrice != null) {
    const fm3 = calculateFairMLFromBook3Way(h2h.homePrice, drawPrice, h2h.awayPrice, comp);
    fair_ml_home = fm3.homeOdds;
    fair_ml_away = fm3.awayOdds;
    fair_ml_draw = fm3.drawOdds;
  } else if (h2h?.homePrice != null && h2h?.awayPrice != null) {
    const fm = calculateFairMLFromBook(h2h.homePrice, h2h.awayPrice, comp);
    fair_ml_home = fm.homeOdds;
    fair_ml_away = fm.awayOdds;
  }
  return {
    fair_spread: fs?.fairLine ?? null,
    fair_total: ft?.fairLine ?? null,
    fair_ml_home,
    fair_ml_away,
    fair_ml_draw,
  };
}

/** Use composite_history as single source of truth; only fall back to edgescout when no DB entry */
function getEffectiveFair(game: any) {
  return game.fairLines || computeFallbackFair(game);
}

function getCellStyle(edge: number | null): { bg: string; border: string } {
  if (edge == null || Math.abs(edge) < EDGE_THRESHOLD) return { bg: P.neutralBg, border: P.neutralBorder };
  return edge > 0
    ? { bg: P.greenBg, border: P.greenBorder }
    : { bg: P.redBg, border: P.redBorder };
}

// --- Sub-components ---
function TeamLogo({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  const [imgError, setImgError] = useState(false);
  if (logo && !imgError) {
    return <img src={logo} alt={teamName} className="w-5 h-5 object-contain" onError={() => setImgError(true)} />;
  }
  return (
    <div className="w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0"
      style={{ backgroundColor: getTeamColor(teamName) }}
    >
      {getTeamInitials(teamName)}
    </div>
  );
}

function BookIcon({ bookKey, size = 24 }: { bookKey: string; size?: number }) {
  const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' };
  const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2);
  return (
    <div className="rounded flex items-center justify-center font-bold text-white flex-shrink-0"
      style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}
    >
      {initials}
    </div>
  );
}

function MiniChart({ data, fairValue }: { data?: { t: number; v: number }[]; fairValue?: number | null }) {
  const W = 96, H = 26;
  if (!data || data.length < 2) {
    return <div style={{ width: W, height: H, background: P.chartBg, borderRadius: 4, marginTop: 4 }} />;
  }
  const vals = data.map(d => d.v);
  const allVals = fairValue != null ? [...vals, fairValue] : vals;
  const min = Math.min(...allVals);
  const max = Math.max(...allVals);
  const range = max - min || 1;
  const toY = (v: number) => H - 2 - ((v - min) / range) * (H - 4);
  const points = data.map((d, i) => `${(i / (data.length - 1)) * (W - 4) + 2},${toY(d.v)}`).join(' ');
  const lastY = toY(data[data.length - 1].v);
  const fairY = fairValue != null ? toY(fairValue) : null;
  const lastVal = data[data.length - 1].v;
  const converging = fairValue != null && data.length >= 2
    ? Math.abs(lastVal - fairValue) < Math.abs(data[0].v - fairValue) : null;
  const lineColor = converging === true ? '#22c55e' : converging === false ? '#ef4444' : '#9ca3af';

  return (
    <svg width={W} height={H} style={{ marginTop: 4 }}>
      <rect width={W} height={H} rx={4} fill={P.chartBg} />
      {fairY != null && (
        <line x1={2} y1={fairY} x2={W - 2} y2={fairY} stroke={P.textMuted} strokeWidth={1} strokeDasharray="3,2" opacity={0.4} />
      )}
      <polyline points={points} fill="none" stroke={lineColor} strokeWidth={1.8} />
      <circle cx={W - 2} cy={lastY} r={2.5} fill={lineColor} />
    </svg>
  );
}

function MarketCell({
  bookValue, bookPrice, fairValue, edge, exchangeMode, label,
  chartData, fairChartValue,
}: {
  bookValue: string;
  bookPrice?: string;
  fairValue: string | null;
  edge: number | null;
  exchangeMode?: boolean;
  label?: string;
  chartData?: { t: number; v: number }[];
  fairChartValue?: number | null;
}) {
  const { bg, border } = getCellStyle(edge);
  const hasEdge = edge != null && Math.abs(edge) >= EDGE_THRESHOLD;
  const edgeColor = hasEdge ? (edge! > 0 ? P.greenText : P.redText) : P.textMuted;

  return (
    <div style={{
      background: bg, borderRight: `1px solid ${border}`,
      borderLeft: hasEdge ? `3px solid ${border}` : undefined,
      padding: '6px 8px', minHeight: 70, display: 'flex', flexDirection: 'column',
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
          {bookValue}
        </span>
        {bookPrice && (
          <span style={{ fontSize: 10, color: P.textSecondary, fontFamily: 'monospace' }}>
            {bookPrice}
          </span>
        )}
      </div>
      {fairValue && (
        <div style={{ fontSize: 10, color: P.textMuted, marginTop: 1, fontFamily: 'monospace' }}>
          Fair {fairValue}
        </div>
      )}
      {hasEdge && (
        <div style={{ fontSize: 10, fontWeight: 600, color: edgeColor, marginTop: 1 }}>
          {edge! > 0 ? '+' : ''}{edge!.toFixed(1)}%
        </div>
      )}
      {chartData && chartData.length >= 2 && (
        <MiniChart data={chartData} fairValue={fairChartValue} />
      )}
    </div>
  );
}

// --- Main Component ---
interface SportsHomeGridProps {
  games: Record<string, any[]>;
  dataSource?: 'backend' | 'odds_api' | 'none';
  totalGames?: number;
  totalEdges?: number;
  fetchedAt?: string;
  view?: 'tier1' | 'tier2';
}

export function SportsHomeGrid({
  games: initialGames, dataSource: initialDataSource = 'none',
  totalGames: initialTotalGames = 0, totalEdges: initialTotalEdges = 0,
  fetchedAt: initialFetchedAt,
  view = 'tier1',
}: SportsHomeGridProps) {
  const [activeSport, setActiveSport] = useState<string | null>(null);
  const [selectedBook, setSelectedBook] = useState<string>('fanduel');
  const [isBookDropdownOpen, setIsBookDropdownOpen] = useState(false);
  const [showMoreSports, setShowMoreSports] = useState(false);
  const [noEdgeCollapsed, setNoEdgeCollapsed] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const moreSportsRef = useRef<HTMLDivElement>(null);

  const [games, setGames] = useState(initialGames);
  const [dataSource, setDataSource] = useState(initialDataSource);
  const [totalGames, setTotalGames] = useState(initialTotalGames);
  const [totalEdges, setTotalEdges] = useState(initialTotalEdges);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(initialFetchedAt ? new Date(initialFetchedAt) : null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [secondsSinceUpdate, setSecondsSinceUpdate] = useState(0);

  const exchangeMode = isExchange(selectedBook);
  const selectedBookConfig = BOOK_CONFIG[selectedBook];

  const refreshData = useCallback(async (showSpinner = true) => {
    if (showSpinner) setIsRefreshing(true);
    try {
      const res = await fetch('/api/odds/dashboard');
      if (!res.ok) throw new Error('Refresh failed');
      const data = await res.json();
      setGames(data.games || {});
      setTotalGames(data.totalGames || 0);
      setTotalEdges(data.totalEdges || 0);
      setLastUpdated(new Date());
      setSecondsSinceUpdate(0);
      if (data.games && Object.keys(data.games).length > 0) setDataSource('odds_api');
    } catch (e) {
      console.error('[SportsHomeGrid] Refresh error:', e);
    } finally {
      if (showSpinner) setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());
    setLastUpdated(initialFetchedAt ? new Date(initialFetchedAt) : new Date());
    setActiveSport(null);
  }, [initialFetchedAt]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) setIsBookDropdownOpen(false);
      if (moreSportsRef.current && !moreSportsRef.current.contains(event.target as Node)) setShowMoreSports(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      setSecondsSinceUpdate(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [mounted]);

  // Smart sport ordering
  const orderedGames = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const todayEnd = new Date(todayStart.getTime() + 86400000);
    const allSportKeys = [...SPORT_ORDER];
    Object.keys(games).forEach(key => { if (!allSportKeys.includes(key)) allSportKeys.push(key); });

    const sportMeta: { key: string; games: any[]; gamesToday: number; gamesWithOdds: number }[] = [];
    for (const sportKey of allSportKeys) {
      const sg = games[sportKey];
      if (!sg || sg.length === 0) continue;
      let gamesToday = 0, gamesWithOdds = 0;
      for (const g of sg) {
        const t = new Date(g.commenceTime);
        if (t >= todayStart && t < todayEnd) gamesToday++;
        if (g.consensus?.spreads?.line !== undefined || g.consensus?.h2h?.homePrice !== undefined || g.consensus?.totals?.line !== undefined) gamesWithOdds++;
      }
      sportMeta.push({ key: sportKey, games: sg, gamesToday, gamesWithOdds });
    }

    sportMeta.sort((a, b) => {
      const tier = (x: typeof a) => x.gamesToday > 0 && x.gamesWithOdds > 0 ? 0 : x.gamesToday > 0 ? 1 : x.gamesWithOdds > 0 ? 2 : 3;
      const diff = tier(a) - tier(b);
      if (diff !== 0) return diff;
      const aO = SPORT_ORDER.indexOf(a.key), bO = SPORT_ORDER.indexOf(b.key);
      if (aO !== -1 && bO !== -1) return aO - bO;
      if (aO !== -1) return -1;
      if (bO !== -1) return 1;
      return b.gamesWithOdds - a.gamesWithOdds;
    });

    const result: Record<string, any[]> = {};
    for (const e of sportMeta) result[e.key] = e.games;
    return result;
  }, [games]);

  // Filter + sort games by view: tier1 = pregame only, tier2 = all states
  const { hasLiveGames, sortedGamesBySport } = useMemo(() => {
    let hasLive = false;
    const sorted: Record<string, any[]> = {};
    const stateOrder: Record<string, number> = { live: 0, pregame: 1, final: 2 };

    for (const [sportKey, sportGames] of Object.entries(orderedGames)) {
      // Tier 1 dashboard: only pregame games (live/final belong to Tier 2 Live Markets)
      const filtered = view === 'tier1'
        ? sportGames.filter((g: any) => (g.gameState || 'pregame') === 'pregame')
        : sportGames;

      const games = [...filtered].sort((a, b) => {
        const sa = stateOrder[a.gameState || 'pregame'] ?? 1;
        const sb = stateOrder[b.gameState || 'pregame'] ?? 1;
        if (sa !== sb) return sa - sb;
        const ta = new Date(a.commenceTime).getTime();
        const tb = new Date(b.commenceTime).getTime();
        if ((a.gameState || 'pregame') === 'final') return tb - ta;
        return ta - tb;
      });
      if (games.length > 0) {
        sorted[sportKey] = games;
        if (games.some(g => g.gameState === 'live')) hasLive = true;
      }
    }

    return { hasLiveGames: hasLive, sortedGamesBySport: sorted };
  }, [orderedGames, view]);

  // Auto-refresh: 10s when live games, 45s otherwise
  useEffect(() => {
    if (!mounted) return;
    const interval = hasLiveGames ? 10000 : 45000;
    console.log(`[SportsHomeGrid] Auto-refresh set to ${interval / 1000}s (hasLiveGames=${hasLiveGames})`);
    const timer = setInterval(() => {
      console.log(`[SportsHomeGrid] Polling live scores... (${new Date().toLocaleTimeString()})`);
      refreshData(false);
    }, interval);
    return () => clearInterval(timer);
  }, [mounted, refreshData, hasLiveGames]);

  // Filter by sport + search
  const filteredGames = useMemo(() => {
    const source = activeSport ? { [activeSport]: sortedGamesBySport[activeSport] || [] } : sortedGamesBySport;
    if (!searchQuery.trim()) return source;
    const q = searchQuery.toLowerCase();
    const result: Record<string, any[]> = {};
    for (const [sportKey, sg] of Object.entries(source)) {
      const matched = sg.filter((g: any) => g.homeTeam?.toLowerCase().includes(q) || g.awayTeam?.toLowerCase().includes(q));
      if (matched.length > 0) result[sportKey] = matched;
    }
    return result;
  }, [searchQuery, activeSport, sortedGamesBySport]);

  // Debug: log first live game's liveData on each data update
  useEffect(() => {
    for (const sportGames of Object.values(sortedGamesBySport)) {
      const liveGame = sportGames.find((g: any) => g.gameState === 'live');
      if (liveGame) {
        console.log(`[LiveData DEBUG] ${liveGame.awayTeam} @ ${liveGame.homeTeam}: gameState=${liveGame.gameState}, liveData=`, liveGame.liveData);
        break;
      }
    }
  }, [sortedGamesBySport]);

  const isAllView = activeSport === null;
  const activeSportsCount = Object.keys(games).filter(k => games[k]?.length > 0).length;
  const hasAnyGames = totalGames > 0 || Object.values(games).some(g => g.length > 0);

  // --- RENDER ---
  return (
    <div style={{ background: P.pageBg, minHeight: '100vh', fontFamily: FONT, padding: '16px 16px 32px' }}>

      {/* Status Bar */}
      <div style={{
        marginBottom: 20, padding: '12px 16px', background: P.cardBg,
        borderRadius: 12, border: `1px solid ${P.cardBorder}`,
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${dataSource !== 'none' ? 'bg-emerald-500 animate-pulse' : 'bg-red-400'}`} />
              <span style={{ fontSize: 11, fontWeight: 600, color: dataSource !== 'none' ? P.greenText : P.redText }}>
                {dataSource !== 'none' ? 'LIVE FEED' : 'OFFLINE'}
              </span>
            </div>
            <div style={{ width: 1, height: 16, background: P.cardBorder }} />
            <div className="flex items-center gap-3">
              <div style={{ background: P.neutralBg, borderRadius: 6, padding: '3px 8px', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontSize: 9, fontWeight: 600, color: P.textFaint, letterSpacing: 1 }}>GAMES</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                  {totalGames || Object.values(games).reduce((a, g) => a + g.length, 0)}
                </span>
              </div>
              <div style={{ background: P.neutralBg, borderRadius: 6, padding: '3px 8px', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontSize: 9, fontWeight: 600, color: P.textFaint, letterSpacing: 1 }}>SPORTS</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>{activeSportsCount}</span>
              </div>
              {totalEdges > 0 && (
                <div style={{
                  background: P.greenBg, border: `1px solid ${P.greenBorder}`,
                  borderRadius: 6, padding: '3px 8px', display: 'flex', alignItems: 'center', gap: 4,
                }}>
                  <span style={{ fontSize: 9, fontWeight: 600, color: P.greenText, letterSpacing: 1 }}>EDGES</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: P.greenText, fontFamily: 'monospace' }}>{totalEdges}</span>
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2" style={{ padding: '3px 8px', background: P.neutralBg, borderRadius: 6 }} suppressHydrationWarning>
              {hasLiveGames && (
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                </span>
              )}
              <span style={{ fontSize: 10, color: secondsSinceUpdate > 60 ? '#d97706' : P.textMuted, fontFamily: 'monospace' }}>
                {hasLiveGames && <span style={{ color: '#16a34a', marginRight: 4 }}>LIVE {hasLiveGames ? '10s' : '45s'}</span>}
                Updated {secondsSinceUpdate < 60 ? `${secondsSinceUpdate}s` : `${Math.floor(secondsSinceUpdate / 60)}m`} ago
                {lastUpdated && <span style={{ color: P.textFaint, marginLeft: 4 }}>({lastUpdated.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })})</span>}
              </span>
            </div>
            <button onClick={() => refreshData(true)} disabled={isRefreshing}
              style={{
                display: 'flex', alignItems: 'center', gap: 4, padding: '4px 10px',
                background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 6,
                cursor: 'pointer', fontSize: 10, fontWeight: 500, color: P.textSecondary,
              }}
            >
              <svg className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} style={{ color: P.textMuted }}
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {isRefreshing ? 'Updating...' : 'Refresh'}
            </button>
            <div className="flex items-center gap-2" style={{ padding: '3px 8px', background: P.neutralBg, borderRadius: 6 }} suppressHydrationWarning>
              <span style={{ fontSize: 11, color: P.textSecondary, fontFamily: 'monospace' }}>
                {currentTime ? currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : '--:--:--'}
              </span>
              <span style={{ fontSize: 9, color: P.textFaint }}>ET</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: 16 }}>
        <div className="relative max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: P.textMuted }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search teams..."
            style={{
              width: '100%', background: P.headerBar, border: `1px solid ${P.cardBorder}`,
              borderRadius: 8, paddingLeft: 36, paddingRight: 16, paddingTop: 8, paddingBottom: 8,
              fontSize: 13, color: P.textPrimary, fontFamily: FONT, outline: 'none',
            }}
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: P.textMuted, background: 'none', border: 'none', cursor: 'pointer' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Sport pills + Book selector */}
      <div className="flex items-center justify-between gap-4" style={{ marginBottom: 20 }}>
        <div className="flex gap-1.5 overflow-x-auto pb-1 flex-1 items-center">
          <button onClick={() => setActiveSport(null)}
            style={{
              flexShrink: 0, padding: '5px 12px', borderRadius: 6, fontSize: 12, fontWeight: 600,
              border: `1px solid ${activeSport === null ? P.cardBorder : 'transparent'}`,
              background: activeSport === null ? P.cardBg : 'transparent',
              color: activeSport === null ? P.textPrimary : P.textMuted,
              cursor: 'pointer',
              boxShadow: activeSport === null ? '0 1px 2px rgba(0,0,0,0.04)' : 'none',
            }}
          >
            ALL
          </button>
          {MODELED_SPORTS.map(sport => {
            const gc = games[sport.key]?.length || 0;
            const active = activeSport === sport.key;
            return (
              <button key={sport.key} onClick={() => setActiveSport(sport.key)}
                style={{
                  flexShrink: 0, padding: '5px 12px', borderRadius: 6, fontSize: 12, fontWeight: 500,
                  border: `1px solid ${active ? P.cardBorder : 'transparent'}`,
                  background: active ? P.cardBg : 'transparent',
                  color: active ? P.textPrimary : P.textMuted,
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
                  boxShadow: active ? '0 1px 2px rgba(0,0,0,0.04)' : 'none',
                }}
              >
                {sport.label}
                {gc > 0 && <span style={{ fontSize: 9, fontFamily: 'monospace', color: active ? P.textSecondary : P.textFaint }}>{gc}</span>}
              </button>
            );
          })}
          {/* More sports dropdown */}
          <div className="relative flex-shrink-0" ref={moreSportsRef}>
            <button onClick={() => setShowMoreSports(!showMoreSports)}
              style={{
                padding: '5px 10px', borderRadius: 6, fontSize: 12, fontWeight: 500,
                border: `1px solid ${!MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? P.cardBorder : 'transparent'}`,
                background: !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? P.cardBg : 'transparent',
                color: !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? P.textPrimary : P.textMuted,
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 3,
                boxShadow: !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? '0 1px 2px rgba(0,0,0,0.04)' : 'none',
              }}
            >
              More
              <svg className={`w-3 h-3 transition-transform ${showMoreSports ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {showMoreSports && (
              <div className="absolute left-0 z-50 mt-1.5 w-48 max-h-64 overflow-y-auto" style={{
                background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 8,
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              }}>
                {MORE_SPORTS.map(sport => {
                  const gc = games[sport.key]?.length || 0;
                  if (gc === 0) return null;
                  return (
                    <button key={sport.key}
                      onClick={() => { setActiveSport(sport.key); setShowMoreSports(false); }}
                      className="w-full flex items-center justify-between"
                      style={{
                        padding: '6px 12px', textAlign: 'left', fontSize: 12, cursor: 'pointer',
                        background: activeSport === sport.key ? P.neutralBg : 'transparent',
                        color: activeSport === sport.key ? P.greenText : P.textPrimary,
                        border: 'none',
                      }}
                    >
                      <span>{sport.label}</span>
                      <span style={{ fontSize: 9, fontFamily: 'monospace', color: P.textFaint }}>{gc}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Book Selector */}
        <div className="relative flex-shrink-0" ref={dropdownRef}>
          <button onClick={() => setIsBookDropdownOpen(!isBookDropdownOpen)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px',
              background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 6, cursor: 'pointer',
            }}
          >
            <BookIcon bookKey={selectedBook} size={20} />
            <span style={{ fontSize: 12, fontWeight: 600, color: P.textPrimary }}>{selectedBookConfig?.name}</span>
            <svg className={`w-3.5 h-3.5 transition-transform ${isBookDropdownOpen ? 'rotate-180' : ''}`}
              style={{ color: P.textMuted }} fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {isBookDropdownOpen && (
            <div className="absolute right-0 z-50 mt-1.5 w-48 overflow-hidden" style={{
              background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 8,
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            }}>
              {AVAILABLE_BOOKS.map(book => {
                const config = BOOK_CONFIG[book];
                const isSel = book === selectedBook;
                return (
                  <button key={book}
                    onClick={() => { setSelectedBook(book); setIsBookDropdownOpen(false); }}
                    className="w-full flex items-center gap-2.5"
                    style={{
                      padding: '8px 12px', textAlign: 'left', cursor: 'pointer', border: 'none',
                      background: isSel ? P.neutralBg : 'transparent', color: P.textPrimary,
                    }}
                  >
                    <BookIcon bookKey={book} size={22} />
                    <span style={{ fontSize: 13, fontWeight: 500, flex: 1 }}>{config?.name}</span>
                    {config.type === 'exchange' && (
                      <span style={{ fontSize: 9, color: P.textFaint, background: P.neutralBg, padding: '1px 4px', borderRadius: 3 }}>
                        Exchange
                      </span>
                    )}
                    {isSel && (
                      <svg className="w-3.5 h-3.5" style={{ color: P.greenText }} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Empty State */}
      {!hasAnyGames && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4" style={{ background: P.neutralBg, border: `1px solid ${P.cardBorder}` }}>
            <svg className="w-8 h-8" style={{ color: P.textFaint }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: P.textPrimary, marginBottom: 8 }}>No Active Markets</h3>
          <p style={{ fontSize: 13, color: P.textSecondary, textAlign: 'center', maxWidth: 360 }}>
            {dataSource === 'none' ? 'Unable to connect to data sources.' : 'No upcoming games found.'}
          </p>
        </div>
      )}

      {/* Search empty state */}
      {hasAnyGames && searchQuery && Object.keys(filteredGames).length === 0 && (
        <div className="flex flex-col items-center justify-center py-16">
          <p style={{ fontSize: 13, color: P.textMuted }}>No games matching &ldquo;{searchQuery}&rdquo;</p>
          <button onClick={() => setSearchQuery('')} style={{ marginTop: 8, fontSize: 12, color: P.greenText, background: 'none', border: 'none', cursor: 'pointer' }}>
            Clear search
          </button>
        </div>
      )}

      {/* Game Cards */}
      <div className="space-y-8">
        {Object.entries(filteredGames).map(([sportKey, sportGames]) => {
          if (!sportGames || sportGames.length === 0) return null;
          const sportLabel = ALL_SPORT_PILLS.find(s => s.key === sportKey)?.label ||
            SUPPORTED_SPORTS.find(s => s.key === sportKey)?.name || sportKey;

          const gamesWithOdds = sportGames.filter((g: any) =>
            g.consensus?.spreads?.line !== undefined || g.consensus?.h2h?.homePrice !== undefined || g.consensus?.totals?.line !== undefined
          ).length;

          // Collapsed row for sports with no odds
          if (gamesWithOdds === 0) {
            return (
              <div key={sportKey} className="flex items-center justify-between"
                style={{ padding: '8px 12px', background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 8, opacity: 0.5 }}
              >
                <div className="flex items-center gap-2">
                  <span style={{ fontSize: 12, fontWeight: 600, color: P.textSecondary, textTransform: 'uppercase', letterSpacing: 1 }}>{sportLabel}</span>
                  <span style={{ fontSize: 10, color: P.textFaint }}>{sportGames.length} game{sportGames.length !== 1 ? 's' : ''} &middot; No odds</span>
                </div>
              </div>
            );
          }

          const gamesToShow = isAllView && !searchQuery ? sportGames.slice(0, GAMES_PER_SPORT_IN_ALL_VIEW) : sportGames;
          const hasMoreGames = isAllView && !searchQuery && sportGames.length > GAMES_PER_SPORT_IN_ALL_VIEW;

          return (
            <div key={sportKey}>
              <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
                <div className="flex items-center gap-2">
                  <span style={{ fontSize: 13, fontWeight: 700, color: P.textPrimary, textTransform: 'uppercase', letterSpacing: 1 }}>{sportLabel}</span>
                  <span style={{ fontSize: 10, color: P.textFaint, fontFamily: 'monospace' }}>{sportGames.length}</span>
                </div>
                <Link href={`/edge/portal/sports/${sportKey}`}
                  className="flex items-center gap-1" style={{ fontSize: 11, color: P.textMuted, textDecoration: 'none' }}
                >
                  View all
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {(() => {
                  // Pre-compute edges for sorting
                  const gamesWithEdge = gamesToShow.map((game: any) => {
                    const fair = getEffectiveFair(game);
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;
                    const maxEdge = calcMaxEdge(fair, spreads, h2h, totals, game.sportKey);
                    return { game, maxEdge };
                  });

                  // Sort: LIVE first, then pregame by edge, then FINAL last
                  gamesWithEdge.sort((a, b) => {
                    const stateOrder = (g: any) => g.game.gameState === 'live' ? 0 : g.game.gameState === 'final' ? 2 : 1;
                    const stateDiff = stateOrder(a) - stateOrder(b);
                    if (stateDiff !== 0) return stateDiff;
                    return b.maxEdge - a.maxEdge;
                  });
                  const withEdge = gamesWithEdge.filter(g => g.maxEdge >= EDGE_THRESHOLD);
                  const noEdge = gamesWithEdge.filter(g => g.maxEdge < EDGE_THRESHOLD);

                  const renderCard = ({ game, maxEdge }: { game: any; maxEdge: number }, isNoEdge = false) => {
                    const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
                    const timeStr = mounted ? gameTime.toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';
                    const isLive = game.gameState === 'live';
                    const isFinal = game.gameState === 'final';
                    const countdown = mounted ? (isLive ? 'LIVE' : isFinal ? 'FINAL' : getTimeDisplay(gameTime, game.sportKey)) : '';

                    const fair = getEffectiveFair(game);
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;

                    // Per-cell edges — clean implied probability comparison
                    let homeSpreadEdge: number | null = null, awaySpreadEdge: number | null = null;
                    if (fair?.fair_spread != null && spreads?.line !== undefined) {
                      if (spreads.homePrice != null) homeSpreadEdge = spreadEdgeForSide(fair.fair_spread, spreads.line, spreads.homePrice, game.sportKey, true);
                      if (spreads.awayPrice != null) awaySpreadEdge = spreadEdgeForSide(fair.fair_spread, spreads.line, spreads.awayPrice, game.sportKey, false);
                    }

                    let homeMLEdge: number | null = null, awayMLEdge: number | null = null;
                    let drawEdge: number | null = null;
                    const gameSoccer = isSoccer(game.sportKey);
                    if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice != null && h2h?.awayPrice != null) {
                      const fairHP = toProb(fair.fair_ml_home);
                      const fairAP = toProb(fair.fair_ml_away);
                      const bookHP = toProb(h2h.homePrice);
                      const bookAP = toProb(h2h.awayPrice);
                      const drawPrice = h2h?.drawPrice ?? h2h?.draw;
                      if (gameSoccer && drawPrice != null) {
                        // 3-way: normalize across all 3 outcomes
                        const bookDP = toProb(drawPrice);
                        const totalBook = bookHP + bookAP + bookDP;
                        const normBHP = bookHP / totalBook;
                        const normBAP = bookAP / totalBook;
                        const normBDP = bookDP / totalBook;
                        // Use proper 3-way fair draw if available, else residual
                        const fairDP = fair?.fair_ml_draw != null
                          ? toProb(fair.fair_ml_draw)
                          : Math.max(0, 1 - fairHP - fairAP);
                        homeMLEdge = (fairHP - normBHP) * 100;
                        awayMLEdge = (fairAP - normBAP) * 100;
                        drawEdge = (fairDP - normBDP) * 100;
                      } else {
                        // 2-way: normalize home + away only
                        const normBHP = bookHP / (bookHP + bookAP);
                        const normBAP = bookAP / (bookHP + bookAP);
                        homeMLEdge = (fairHP - normBHP) * 100;
                        awayMLEdge = (fairAP - normBAP) * 100;
                      }
                    }

                    let overEdge: number | null = null, underEdge: number | null = null;
                    if (fair?.fair_total != null && totals?.line !== undefined) {
                      if (totals.overPrice != null) overEdge = totalEdgeForSide(fair.fair_total, totals.line, totals.overPrice, game.sportKey, true);
                      if (totals.underPrice != null) underEdge = totalEdgeForSide(fair.fair_total, totals.line, totals.underPrice, game.sportKey, false);
                    }

                    const displayAway = getDisplayTeamName(game.awayTeam, game.sportKey);
                    const displayHome = getDisplayTeamName(game.homeTeam, game.sportKey);

                    // Exchange mode formatting
                    const fmtML = (odds: number | undefined) => {
                      if (odds == null) return '--';
                      if (exchangeMode) return `${oddsToYesCents(odds)}\u00a2`;
                      return fmtOdds(odds);
                    };

                    return (
                      <Link key={game.id} href={exchangeMode
                            ? `/edge/portal/sports/exchange/${game.id}?sport=${game.sportKey}&platform=${selectedBook}`
                            : `/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                        className="block group"
                        style={{
                          background: P.cardBg,
                          border: isLive ? '2px solid #16a34a' : isFinal ? `1px solid ${P.textMuted}` : `1px solid ${P.cardBorder}`,
                          borderRadius: 12,
                          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                          opacity: isNoEdge ? 0.45 : isFinal ? 0.75 : 1,
                          transition: 'all 0.15s',
                          overflow: 'hidden',
                          textDecoration: 'none',
                        }}
                      >
                        {/* Header */}
                        <div style={{
                          background: P.headerBar, padding: '6px 12px',
                          borderBottom: `1px solid ${P.cardBorder}`,
                          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        }}>
                          <span style={{ fontSize: 11, color: P.textSecondary }} suppressHydrationWarning>{timeStr}</span>
                          <div className="flex items-center gap-2">
                            {isLive ? (
                              <span className="flex items-center gap-1" style={{ fontSize: 10, fontWeight: 700, color: '#16a34a' }}>
                                <span className="relative flex h-1.5 w-1.5">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                                </span>
                                LIVE
                                {game.liveData?.statusDetail && game.liveData.statusDetail !== 'Score unavailable' && (
                                  <span style={{ fontWeight: 500, color: P.textSecondary, marginLeft: 2, fontSize: 9 }}>
                                    {game.liveData.statusDetail}
                                  </span>
                                )}
                              </span>
                            ) : isFinal ? (
                              <span style={{ fontSize: 10, fontWeight: 600, color: P.textMuted }}>FINAL</span>
                            ) : (
                              <span style={{ fontSize: 10, color: P.textFaint, fontFamily: 'monospace' }}>{countdown}</span>
                            )}
                            {maxEdge >= 8 && (
                              <span style={{ fontSize: 9, fontWeight: 700, color: '#d97706', background: '#fef3c7',
                                borderRadius: 4, padding: '1px 5px', marginLeft: 4 }}>
                                HIGH VARIANCE
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Team Rows */}
                        <div style={{ padding: '8px 12px' }}>
                          {/* Away */}
                          <div className="flex items-center gap-2" style={{ marginBottom: 4 }}>
                            <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                            <span style={{ fontSize: 13, fontWeight: 600, color: P.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {displayAway}
                            </span>
                            {(isLive || isFinal) && game.liveData?.awayScore != null && (
                              <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace', }}>{game.liveData.awayScore}</span>
                            )}
                          </div>
                          {/* Home */}
                          <div className="flex items-center gap-2">
                            <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                            <span style={{ fontSize: 13, fontWeight: 600, color: P.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {displayHome}
                            </span>
                            {(isLive || isFinal) && game.liveData?.homeScore != null && (
                              <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace', }}>{game.liveData.homeScore}</span>
                            )}
                          </div>
                        </div>

                        {/* Live/Final covering indicator: SPREAD: Fair NEB -0.5 | 45-45 | ✗ Not Covering */}
                        {(isLive || isFinal) && game.liveData && game.liveData.homeScore != null && fair?.fair_spread != null && (
                          <div style={{
                            padding: '5px 12px', borderTop: `1px solid ${P.cardBorder}`,
                            display: 'flex', alignItems: 'center', gap: 6,
                            background: P.neutralBg, fontFamily: 'monospace', fontSize: 10,
                          }}>
                            {(() => {
                              const margin = game.liveData.homeScore - game.liveData.awayScore;
                              const atsMargin = margin + fair.fair_spread;
                              const scoreStr = `${game.liveData.awayScore}-${game.liveData.homeScore}`;
                              // Determine covering status
                              let statusLabel: string;
                              let statusColor: string;
                              if (isFinal && game.liveData.spreadResult) {
                                const result = game.liveData.spreadResult.toUpperCase();
                                statusLabel = result === 'WIN' ? '✓ Covered' : result === 'LOSS' ? '✗ Missed' : '— Push';
                                statusColor = result === 'WIN' ? P.greenText : result === 'LOSS' ? P.redText : P.textMuted;
                              } else {
                                const isPush = atsMargin === 0;
                                const isCovering = atsMargin > 0;
                                if (isPush) {
                                  statusLabel = '— Push';
                                  statusColor = P.textMuted;
                                } else if (isLive) {
                                  statusLabel = isCovering ? '✓ Covering' : '✗ Not Covering';
                                  statusColor = isCovering ? P.greenText : P.redText;
                                } else {
                                  statusLabel = isCovering ? '✓ Covered' : '✗ Missed';
                                  statusColor = isCovering ? P.greenText : P.redText;
                                }
                              }
                              return (
                                <>
                                  <span style={{ color: P.textMuted, fontWeight: 600, letterSpacing: 0.5 }}>SPREAD:</span>
                                  <span style={{ color: P.textSecondary }}>Fair {displayHome} {fmtSpread(fair.fair_spread)}</span>
                                  <span style={{ color: P.textFaint }}>|</span>
                                  <span style={{ color: P.textSecondary, fontWeight: 600 }}>{scoreStr}</span>
                                  <span style={{ color: P.textFaint }}>|</span>
                                  <span style={{ fontWeight: 700, color: statusColor }}>{statusLabel}</span>
                                </>
                              );
                            })()}
                          </div>
                        )}

                        {/* Market Grid — soccer vs non-soccer layout */}
                        <div style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                          {gameSoccer ? (
                            /* ===== SOCCER: 4-col 1-row (Home ML | Draw | Away ML | Total) ===== */
                            <>
                              <div className="grid grid-cols-4" style={{ borderBottom: `1px solid ${P.cardBorder}` }}>
                                {['HOME', 'DRAW', 'AWAY', 'TOTAL'].map((h, i) => (
                                  <div key={i} style={{
                                    padding: '3px 8px', fontSize: 9, fontWeight: 700, color: P.textFaint,
                                    textAlign: 'center', letterSpacing: 1,
                                    borderRight: i < 3 ? `1px solid ${P.cardBorder}` : undefined,
                                  }}>
                                    {h}
                                  </div>
                                ))}
                              </div>
                              <div className="grid grid-cols-4">
                                {/* Home ML */}
                                <MarketCell
                                  bookValue={fmtML(h2h?.homePrice)}
                                  fairValue={fair?.fair_ml_home != null ? fmtOdds(fair.fair_ml_home) : null}
                                  edge={homeMLEdge}
                                />
                                {/* Draw */}
                                <MarketCell
                                  bookValue={fmtOdds(h2h?.drawPrice ?? h2h?.draw)}
                                  fairValue={null}
                                  edge={drawEdge}
                                />
                                {/* Away ML */}
                                <MarketCell
                                  bookValue={fmtML(h2h?.awayPrice)}
                                  fairValue={fair?.fair_ml_away != null ? fmtOdds(fair.fair_ml_away) : null}
                                  edge={awayMLEdge}
                                />
                                {/* Total (O/U stacked) */}
                                <MarketCell
                                  bookValue={totals?.line !== undefined ? `O/U ${totals.line}` : '--'}
                                  bookPrice={totals?.overPrice != null ? `(${fmtOdds(totals.overPrice)})` : undefined}
                                  fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                  edge={overEdge}
                                />
                              </div>
                            </>
                          ) : (
                            /* ===== US SPORTS: 3-col 2-row (Spread | Total | ML) ===== */
                            <>
                              {/* Market Headers */}
                              <div className="grid grid-cols-3" style={{ borderBottom: `1px solid ${P.cardBorder}` }}>
                                {[
                                  'SPREAD',
                                  'TOTAL',
                                  'ML',
                                ].map((h, i) => (
                                  <div key={i} style={{
                                    padding: '3px 8px', fontSize: 9, fontWeight: 700, color: P.textFaint,
                                    textAlign: 'center', letterSpacing: 1,
                                    borderRight: i < 2 ? `1px solid ${P.cardBorder}` : undefined,
                                  }}>
                                    {h}
                                  </div>
                                ))}
                              </div>

                              {/* Away market row */}
                              <div className="grid grid-cols-3" style={{ borderBottom: `1px solid ${P.cardBorder}` }}>
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.spreads?.line !== undefined ? fmtSpread(-bookOdds.spreads.line) : '--'}
                                    bookPrice={bookOdds?.spreads?.exchangeNo != null ? `${bookOdds.spreads.exchangeNo}\u00a2` : undefined}
                                    fairValue={fair?.fair_spread != null ? fmtSpread(-fair.fair_spread) : null}
                                    edge={bookOdds?.spreads ? awaySpreadEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={spreads?.line !== undefined ? fmtSpread(-spreads.line) : '--'}
                                    bookPrice={spreads?.awayPrice != null ? `(${fmtOdds(spreads.awayPrice)})` : undefined}
                                    fairValue={fair?.fair_spread != null ? fmtSpread(-fair.fair_spread) : null}
                                    edge={awaySpreadEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.totals?.line !== undefined ? `O ${bookOdds.totals.line}` : '--'}
                                    bookPrice={bookOdds?.totals?.exchangeOverYes != null ? `${bookOdds.totals.exchangeOverYes}\u00a2` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={bookOdds?.totals ? overEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={totals?.line !== undefined ? `O ${totals.line}` : '--'}
                                    bookPrice={totals?.overPrice != null ? `(${fmtOdds(totals.overPrice)})` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={overEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.h2h?.exchangeAwayYes != null ? `${bookOdds.h2h.exchangeAwayYes}\u00a2` : '--'}
                                    fairValue={fair?.fair_ml_away != null ? `${oddsToYesCents(fair.fair_ml_away)}\u00a2` : null}
                                    edge={bookOdds?.h2h ? awayMLEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={fmtML(h2h?.awayPrice)}
                                    fairValue={fair?.fair_ml_away != null ? fmtOdds(fair.fair_ml_away) : null}
                                    edge={awayMLEdge}
                                  />
                                )}
                              </div>

                              {/* Home market row */}
                              <div className="grid grid-cols-3">
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.spreads?.line !== undefined ? fmtSpread(bookOdds.spreads.line) : '--'}
                                    bookPrice={bookOdds?.spreads?.exchangeYes != null ? `${bookOdds.spreads.exchangeYes}\u00a2` : undefined}
                                    fairValue={fair?.fair_spread != null ? fmtSpread(fair.fair_spread) : null}
                                    edge={bookOdds?.spreads ? homeSpreadEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={spreads?.line !== undefined ? fmtSpread(spreads.line) : '--'}
                                    bookPrice={spreads?.homePrice != null ? `(${fmtOdds(spreads.homePrice)})` : undefined}
                                    fairValue={fair?.fair_spread != null ? fmtSpread(fair.fair_spread) : null}
                                    edge={homeSpreadEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.totals?.line !== undefined ? `U ${bookOdds.totals.line}` : '--'}
                                    bookPrice={bookOdds?.totals?.exchangeUnderYes != null ? `${bookOdds.totals.exchangeUnderYes}\u00a2` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={bookOdds?.totals ? underEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={totals?.line !== undefined ? `U ${totals.line}` : '--'}
                                    bookPrice={totals?.underPrice != null ? `(${fmtOdds(totals.underPrice)})` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={underEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <MarketCell
                                    bookValue={bookOdds?.h2h?.exchangeHomeYes != null ? `${bookOdds.h2h.exchangeHomeYes}\u00a2` : '--'}
                                    fairValue={fair?.fair_ml_home != null ? `${oddsToYesCents(fair.fair_ml_home)}\u00a2` : null}
                                    edge={bookOdds?.h2h ? homeMLEdge : null}
                                  />
                                ) : (
                                  <MarketCell
                                    bookValue={fmtML(h2h?.homePrice)}
                                    fairValue={fair?.fair_ml_home != null ? fmtOdds(fair.fair_ml_home) : null}
                                    edge={homeMLEdge}
                                  />
                                )}
                              </div>
                            </>
                          )}
                        </div>
                      </Link>
                    );
                  };

                  return (
                    <>
                      {withEdge.map(g => renderCard(g))}
                      {noEdge.length > 0 && (
                        <>
                          {withEdge.length > 0 && (
                            <div className="col-span-full">
                              <button
                                onClick={(e) => { e.preventDefault(); setNoEdgeCollapsed(!noEdgeCollapsed); }}
                                className="flex items-center gap-2"
                                style={{ fontSize: 10, color: P.textMuted, background: 'none', border: 'none', cursor: 'pointer', padding: '4px 0' }}
                              >
                                <svg className={`w-3 h-3 transition-transform ${noEdgeCollapsed ? '' : 'rotate-90'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                                {noEdge.length} no-edge game{noEdge.length !== 1 ? 's' : ''}
                              </button>
                            </div>
                          )}
                          {(!noEdgeCollapsed || withEdge.length === 0) && noEdge.map(g => renderCard(g, true))}
                        </>
                      )}
                    </>
                  );
                })()}
              </div>

              {hasMoreGames && (
                <div style={{ marginTop: 12, textAlign: 'center' }}>
                  <button onClick={() => setActiveSport(sportKey)}
                    style={{ fontSize: 12, color: P.textMuted, background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    + {sportGames.length - GAMES_PER_SPORT_IN_ALL_VIEW} more games
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
