'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getTimeDisplay, getGameState } from '@/lib/edge/utils/game-state';

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

// Spread/total odds → implied probability (handles American odds from any book)
// Fair line edge = diff between fair implied prob and book implied prob
function spreadEdgePct(bookLine: number, bookOdds: number, fairLine: number): number {
  // The book's price already encodes line + juice into one implied probability
  const bookProb = toProb(bookOdds);
  // Fair line at -110 juice (standard) gives baseline; adjust for line diff
  // A 1-point spread diff ≈ 2.5-3% implied probability depending on sport
  // But we directly compare: fair line at standard juice vs book price
  const fairProb = toProb(-110); // fair line assumes -110 standard juice
  // Adjust fair prob for the line gap: each point of spread ≈ 3% probability
  const lineGap = fairLine - bookLine; // positive = fair line is higher (more favorable to home)
  const fairAdjusted = fairProb + lineGap * 0.03;
  return (fairAdjusted - bookProb) * 100;
}

function calcMaxEdge(fair: any, spreads: any, h2h: any, totals: any): number {
  let maxEdge = 0;

  // Spread edge: probability-based using book odds (juice matters)
  if (fair?.fair_spread != null && spreads?.line !== undefined && spreads?.homePrice != null) {
    const homeProb = toProb(spreads.homePrice);
    const awayProb = spreads.awayPrice != null ? toProb(spreads.awayPrice) : 1 - homeProb;
    // Fair spread implies a probability shift: each point ≈ 3%
    const lineGap = spreads.line - fair.fair_spread;
    const fairHomeProb = homeProb + lineGap * 0.03;
    maxEdge = Math.max(maxEdge, Math.abs(fairHomeProb - homeProb) * 100, Math.abs((1 - fairHomeProb) - awayProb) * 100);
  } else if (fair?.fair_spread != null && spreads?.line !== undefined) {
    // Fallback: line-only comparison when no odds available
    maxEdge = Math.max(maxEdge, Math.abs(spreads.line - fair.fair_spread) * 3.0);
  }

  // ML edge: already probability-based
  if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice !== undefined && h2h?.awayPrice !== undefined) {
    const fairHP = toProb(fair.fair_ml_home);
    const fairAP = toProb(fair.fair_ml_away);
    const bookHP = toProb(h2h.homePrice);
    const bookAP = toProb(h2h.awayPrice);
    const normBHP = bookHP / (bookHP + bookAP);
    const normBAP = bookAP / (bookHP + bookAP);
    maxEdge = Math.max(maxEdge, (fairHP - normBHP) * 100, (fairAP - normBAP) * 100);
  }

  // Total edge: probability-based using book odds
  if (fair?.fair_total != null && totals?.line !== undefined && totals?.overPrice != null) {
    const overProb = toProb(totals.overPrice);
    const underProb = totals.underPrice != null ? toProb(totals.underPrice) : 1 - overProb;
    const lineGap = fair.fair_total - totals.line;
    const fairOverProb = overProb + lineGap * 0.02; // totals: ~2% per point
    maxEdge = Math.max(maxEdge, Math.abs(fairOverProb - overProb) * 100, Math.abs((1 - fairOverProb) - underProb) * 100);
  } else if (fair?.fair_total != null && totals?.line !== undefined) {
    maxEdge = Math.max(maxEdge, Math.abs(fair.fair_total - totals.line) * 1.5);
  }

  return maxEdge;
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
}

export function SportsHomeGrid({
  games: initialGames, dataSource: initialDataSource = 'none',
  totalGames: initialTotalGames = 0, totalEdges: initialTotalEdges = 0,
  fetchedAt: initialFetchedAt,
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

  // Separate live/pregame
  const { liveGames: allLiveGames, pregameGames } = useMemo(() => {
    const live: any[] = [];
    const pregame: Record<string, any[]> = {};
    for (const [sportKey, sportGames] of Object.entries(orderedGames)) {
      const pg: any[] = [];
      for (const game of sportGames) {
        const state = getGameState(game.commenceTime, game.sportKey);
        if (state === 'live') live.push({ ...game, sportKey });
        else if (state === 'upcoming') pg.push(game);
      }
      if (pg.length > 0) pregame[sportKey] = pg;
    }
    return { liveGames: live, pregameGames: pregame };
  }, [orderedGames]);

  const hasLiveGames = allLiveGames.length > 0;

  // Auto-refresh
  useEffect(() => {
    if (!mounted) return;
    const interval = hasLiveGames ? 20000 : 45000;
    const timer = setInterval(() => refreshData(false), interval);
    return () => clearInterval(timer);
  }, [mounted, refreshData, hasLiveGames]);

  // Filter by sport + search
  const filteredGames = useMemo(() => {
    const source = activeSport ? { [activeSport]: pregameGames[activeSport] || [] } : pregameGames;
    if (!searchQuery.trim()) return source;
    const q = searchQuery.toLowerCase();
    const result: Record<string, any[]> = {};
    for (const [sportKey, sg] of Object.entries(source)) {
      const matched = sg.filter((g: any) => g.homeTeam?.toLowerCase().includes(q) || g.awayTeam?.toLowerCase().includes(q));
      if (matched.length > 0) result[sportKey] = matched;
    }
    return result;
  }, [searchQuery, activeSport, pregameGames]);

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
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"></span>
                </span>
              )}
              <span style={{ fontSize: 10, color: secondsSinceUpdate > 60 ? '#d97706' : P.textMuted, fontFamily: 'monospace' }}>
                {hasLiveGames && <span style={{ color: '#ef4444', marginRight: 4 }}>LIVE</span>}
                Updated {secondsSinceUpdate < 60 ? `${secondsSinceUpdate}s` : `${Math.floor(secondsSinceUpdate / 60)}m`} ago
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
              width: '100%', background: P.cardBg, border: `1px solid ${P.cardBorder}`,
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
              border: `1px solid ${activeSport === null ? P.textPrimary : P.cardBorder}`,
              background: activeSport === null ? P.textPrimary : P.cardBg,
              color: activeSport === null ? '#ffffff' : P.textSecondary,
              cursor: 'pointer',
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
                  border: `1px solid ${active ? P.textPrimary : P.cardBorder}`,
                  background: active ? P.textPrimary : P.cardBg,
                  color: active ? '#ffffff' : P.textSecondary,
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
                }}
              >
                {sport.label}
                {gc > 0 && <span style={{ fontSize: 9, fontFamily: 'monospace', color: active ? 'rgba(255,255,255,0.6)' : P.textFaint }}>{gc}</span>}
              </button>
            );
          })}
          {/* More sports dropdown */}
          <div className="relative flex-shrink-0" ref={moreSportsRef}>
            <button onClick={() => setShowMoreSports(!showMoreSports)}
              style={{
                padding: '5px 10px', borderRadius: 6, fontSize: 12, fontWeight: 500,
                border: `1px solid ${!MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? P.textPrimary : P.cardBorder}`,
                background: !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? P.textPrimary : P.cardBg,
                color: !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null ? '#ffffff' : P.textMuted,
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 3,
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
                    const fair = game.fairLines;
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;
                    const maxEdge = calcMaxEdge(fair, spreads, h2h, totals);
                    return { game, maxEdge };
                  });

                  gamesWithEdge.sort((a, b) => b.maxEdge - a.maxEdge);
                  const withEdge = gamesWithEdge.filter(g => g.maxEdge >= EDGE_THRESHOLD);
                  const noEdge = gamesWithEdge.filter(g => g.maxEdge < EDGE_THRESHOLD);

                  const renderCard = ({ game, maxEdge }: { game: any; maxEdge: number }, isNoEdge = false) => {
                    const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
                    const timeStr = mounted ? gameTime.toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';
                    const countdown = mounted ? getTimeDisplay(gameTime, game.sportKey) : '';
                    const isLive = countdown === 'LIVE';

                    const fair = game.fairLines;
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;

                    // Per-cell edges — probability-based, incorporates book juice
                    let homeSpreadEdge: number | null = null, awaySpreadEdge: number | null = null;
                    if (fair?.fair_spread != null && spreads?.line !== undefined) {
                      if (spreads.homePrice != null) {
                        // Probability-based: book odds encode line + juice together
                        const bookHomeProb = toProb(spreads.homePrice);
                        const bookAwayProb = spreads.awayPrice != null ? toProb(spreads.awayPrice) : 1 - bookHomeProb;
                        // Fair spread shift: each point of spread gap ≈ 3% probability
                        const lineGap = spreads.line - fair.fair_spread;
                        homeSpreadEdge = (bookHomeProb + lineGap * 0.03 - bookHomeProb) * 100; // = lineGap * 3
                        // But now factor in the actual juice difference vs standard -110
                        const stdProb = toProb(-110); // 0.5238
                        const homeJuiceEdge = (stdProb - bookHomeProb) * 100; // positive = book is overcharging
                        homeSpreadEdge = lineGap * 3.0 + homeJuiceEdge;
                        awaySpreadEdge = -lineGap * 3.0 + (spreads.awayPrice != null ? (stdProb - bookAwayProb) * 100 : -homeJuiceEdge);
                      } else {
                        // Fallback: line-only
                        homeSpreadEdge = (spreads.line - fair.fair_spread) * 3.0;
                        awaySpreadEdge = -homeSpreadEdge;
                      }
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
                        // Fair draw = 1 - fairHome - fairAway (residual)
                        const fairDP = Math.max(0, 1 - fairHP - fairAP);
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
                      if (totals.overPrice != null) {
                        const bookOverProb = toProb(totals.overPrice);
                        const bookUnderProb = totals.underPrice != null ? toProb(totals.underPrice) : 1 - bookOverProb;
                        const stdProb = toProb(-110);
                        const lineGap = fair.fair_total - totals.line;
                        overEdge = lineGap * 2.0 + (stdProb - bookOverProb) * 100;
                        underEdge = -lineGap * 2.0 + (totals.underPrice != null ? (stdProb - bookUnderProb) * 100 : -(stdProb - bookOverProb) * 100);
                      } else {
                        overEdge = (fair.fair_total - totals.line) * 1.5;
                        underEdge = -overEdge;
                      }
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
                      <Link key={game.id} href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                        className="block group"
                        style={{
                          background: P.cardBg,
                          border: isLive ? '2px solid #ef4444' : `1px solid ${P.cardBorder}`,
                          borderRadius: 12,
                          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                          opacity: isNoEdge ? 0.45 : 1,
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
                              <span className="flex items-center gap-1" style={{ fontSize: 10, fontWeight: 700, color: '#ef4444' }}>
                                <span className="relative flex h-1.5 w-1.5">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"></span>
                                </span>
                                LIVE
                              </span>
                            ) : countdown !== 'FINAL' ? (
                              <span style={{ fontSize: 10, color: P.textFaint, fontFamily: 'monospace' }}>{countdown}</span>
                            ) : (
                              <span style={{ fontSize: 10, fontWeight: 600, color: P.textMuted }}>FINAL</span>
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
                            {isLive && game.scores && (
                              <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>{game.scores.away}</span>
                            )}
                          </div>
                          {/* Home */}
                          <div className="flex items-center gap-2">
                            <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                            <span style={{ fontSize: 13, fontWeight: 600, color: P.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {displayHome}
                            </span>
                            {isLive && game.scores && (
                              <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>{game.scores.home}</span>
                            )}
                          </div>
                        </div>

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
                                  exchangeMode ? 'YES/NO' : 'SPREAD',
                                  exchangeMode ? '' : 'TOTAL',
                                  exchangeMode ? '' : 'ML',
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
                                    bookValue={h2h?.awayPrice != null ? `${oddsToYesCents(h2h.awayPrice)}\u00a2 YES` : '--'}
                                    fairValue={fair?.fair_ml_away != null ? `${oddsToYesCents(fair.fair_ml_away)}\u00a2` : null}
                                    edge={awayMLEdge}
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
                                  <div style={{ background: P.neutralBg, borderRight: `1px solid ${P.neutralBorder}`, minHeight: 70, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: 10, color: P.textFaint }}>--</span>
                                  </div>
                                ) : (
                                  <MarketCell
                                    bookValue={totals?.line !== undefined ? `O ${totals.line}` : '--'}
                                    bookPrice={totals?.overPrice != null ? `(${fmtOdds(totals.overPrice)})` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={overEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <div style={{ background: P.neutralBg, minHeight: 70, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: 10, color: P.textFaint }}>--</span>
                                  </div>
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
                                    bookValue={h2h?.homePrice != null ? `${oddsToYesCents(h2h.homePrice)}\u00a2 YES` : '--'}
                                    fairValue={fair?.fair_ml_home != null ? `${oddsToYesCents(fair.fair_ml_home)}\u00a2` : null}
                                    edge={homeMLEdge}
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
                                  <div style={{ background: P.neutralBg, borderRight: `1px solid ${P.neutralBorder}`, minHeight: 70, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: 10, color: P.textFaint }}>--</span>
                                  </div>
                                ) : (
                                  <MarketCell
                                    bookValue={totals?.line !== undefined ? `U ${totals.line}` : '--'}
                                    bookPrice={totals?.underPrice != null ? `(${fmtOdds(totals.underPrice)})` : undefined}
                                    fairValue={fair?.fair_total != null ? fair.fair_total.toFixed(1) : null}
                                    edge={underEdge}
                                  />
                                )}
                                {exchangeMode ? (
                                  <div style={{ background: P.neutralBg, minHeight: 70, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: 10, color: P.textFaint }}>--</span>
                                  </div>
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
