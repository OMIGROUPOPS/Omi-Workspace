'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
// formatOdds etc. no longer used — fair line rendering is inline
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getTimeDisplay, getGameState } from '@/lib/edge/utils/game-state';

// LiveEdge from live_edges table (returned by dashboard API)
interface LiveEdge {
  id: string;
  game_id: string;
  sport: string;
  market_type: string;       // 'h2h', 'spreads', 'totals'
  outcome_key: string;       // team name, 'Over', 'Under'
  edge_type: string;
  edge_magnitude: number;
  confidence: number | null;
  status: string;
}

// Helper to find live edge confidence for a specific market/outcome
function findLiveEdgeConfidence(
  liveEdges: LiveEdge[] | undefined,
  marketType: 'spreads' | 'h2h' | 'totals',
  outcomeKey: string
): number | undefined {
  if (!liveEdges || liveEdges.length === 0) return undefined;

  // Find matching edge (case-insensitive match for team names)
  const edge = liveEdges.find(e =>
    e.market_type === marketType &&
    (e.outcome_key.toLowerCase() === outcomeKey.toLowerCase() ||
     outcomeKey.toLowerCase().includes(e.outcome_key.toLowerCase()) ||
     e.outcome_key.toLowerCase().includes(outcomeKey.toLowerCase()))
  );

  return edge?.confidence ?? undefined;
}

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
};

const GAMES_PER_SPORT_IN_ALL_VIEW = 6;

function getDisplayTeamName(teamName: string, sportKey: string): string {
  // College sports - show full name
  if (sportKey.includes('ncaa')) {
    return teamName;
  }
  // Soccer - show full name (teams like "Manchester United", "Nottingham Forest" need full names)
  if (sportKey.includes('soccer')) {
    return teamName;
  }
  // Combat sports - show full name (fighter names)
  if (sportKey.includes('mma') || sportKey.includes('boxing')) {
    return teamName;
  }
  // Tennis - show full name
  if (sportKey.includes('tennis')) {
    return teamName;
  }
  // US pro sports - show last word (Lakers, Chiefs, etc.)
  const words = teamName.split(' ');
  return words[words.length - 1];
}

function TeamLogo({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  const [imgError, setImgError] = useState(false);

  if (logo && !imgError) {
    return <img src={logo} alt={teamName} className="w-5 h-5 object-contain" onError={() => setImgError(true)} />;
  }

  return (
    <div
      className="w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0"
      style={{ backgroundColor: getTeamColor(teamName) }}
    >
      {getTeamInitials(teamName)}
    </div>
  );
}

// Signal tier system
type SignalTier = 'MAX_EDGE' | 'HIGH_EDGE' | 'MID_EDGE' | 'LOW_EDGE' | 'NO_EDGE';

function getSignalTier(maxEdgePct: number): SignalTier {
  if (maxEdgePct >= 8) return 'MAX_EDGE';
  if (maxEdgePct >= 5) return 'HIGH_EDGE';
  if (maxEdgePct >= 3) return 'MID_EDGE';
  if (maxEdgePct >= 1) return 'LOW_EDGE';
  return 'NO_EDGE';
}

const SIGNAL_TIER_STYLE: Record<SignalTier, { label: string; text: string; bg: string; border: string; glow: string }> = {
  MAX_EDGE:  { label: 'MAX EDGE',  text: 'text-cyan-400',    bg: 'bg-cyan-500/15',    border: 'border-cyan-500/40',    glow: 'shadow-cyan-500/20' },
  HIGH_EDGE: { label: 'HIGH EDGE', text: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', glow: 'shadow-emerald-500/15' },
  MID_EDGE:  { label: 'MID EDGE',  text: 'text-amber-400',   bg: 'bg-amber-500/15',   border: 'border-amber-500/30',   glow: '' },
  LOW_EDGE:  { label: 'LOW EDGE',  text: 'text-zinc-400',    bg: 'bg-zinc-700/40',    border: 'border-zinc-600/30',    glow: '' },
  NO_EDGE:   { label: 'NO EDGE',   text: 'text-zinc-600',    bg: 'bg-zinc-800/40',    border: 'border-zinc-700/30',    glow: '' },
};

// Calculate max edge % for a game (across all markets)
function calcMaxEdge(
  fair: any,
  spreads: any,
  h2h: any,
  totals: any
): { maxEdge: number; bestMarket: string; bestSide: string } {
  let maxEdge = 0;
  let bestMarket = '';
  let bestSide = '';

  // Spread edge
  if (fair?.fair_spread != null && spreads?.line !== undefined) {
    const homeE = (spreads.line - fair.fair_spread) * 3.0;
    const awayE = -homeE;
    if (Math.abs(homeE) > maxEdge) { maxEdge = Math.abs(homeE); bestMarket = 'spread'; bestSide = homeE > 0 ? 'home' : 'away'; }
    if (Math.abs(awayE) > maxEdge) { maxEdge = Math.abs(awayE); bestMarket = 'spread'; bestSide = awayE > 0 ? 'home' : 'away'; }
  }

  // ML edge
  if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice !== undefined && h2h?.awayPrice !== undefined) {
    const toProb = (o: number) => o < 0 ? Math.abs(o) / (Math.abs(o) + 100) : 100 / (o + 100);
    const fairHP = toProb(fair.fair_ml_home);
    const fairAP = toProb(fair.fair_ml_away);
    const bookHP = toProb(h2h.homePrice);
    const bookAP = toProb(h2h.awayPrice);
    const normBHP = bookHP / (bookHP + bookAP);
    const normBAP = bookAP / (bookHP + bookAP);
    const homeMLEdge = (fairHP - normBHP) * 100;
    const awayMLEdge = (fairAP - normBAP) * 100;
    if (Math.abs(homeMLEdge) > maxEdge) { maxEdge = Math.abs(homeMLEdge); bestMarket = 'ml'; bestSide = homeMLEdge > 0 ? 'home' : 'away'; }
    if (Math.abs(awayMLEdge) > maxEdge) { maxEdge = Math.abs(awayMLEdge); bestMarket = 'ml'; bestSide = awayMLEdge > 0 ? 'home' : 'away'; }
  }

  // Total edge
  if (fair?.fair_total != null && totals?.line !== undefined) {
    const overE = (fair.fair_total - totals.line) * 1.5;
    if (Math.abs(overE) > maxEdge) { maxEdge = Math.abs(overE); bestMarket = 'total'; bestSide = overE > 0 ? 'over' : 'under'; }
  }

  return { maxEdge, bestMarket, bestSide };
}

// Format spread line with sign
function fmtSpread(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

// Format American odds
function fmtOdds(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

// Conviction bar from composite scores (0-100, 50 is neutral)
function ConvictionBar({ score }: { score: number | null }) {
  if (score == null) return null;
  const deviation = Math.abs(score - 50);
  const widthPct = Math.min(deviation * 2, 100); // 0-50 deviation → 0-100% width
  const color = score >= 55 ? '#10b981' : score <= 45 ? '#ef4444' : '#71717a';
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${widthPct}%`, backgroundColor: color }} />
      </div>
      <span className="text-[9px] font-mono text-zinc-500">{Math.round(score)}</span>
    </div>
  );
}

function BookIcon({ bookKey, size = 24 }: { bookKey: string; size?: number }) {
  const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' };
  const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2);
  return (
    <div
      className="rounded flex items-center justify-center font-bold text-white flex-shrink-0"
      style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}
    >
      {initials}
    </div>
  );
}

// Modeled sports — these get primary tabs
const MODELED_SPORTS = [
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'basketball_ncaab', label: 'NCAAB' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF' },
  { key: 'icehockey_nhl', label: 'NHL' },
  { key: 'soccer_epl', label: 'EPL' },
];

const MODELED_SPORT_KEYS = new Set(MODELED_SPORTS.map(s => s.key));

// All other sports for the "More" overflow
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

// Combined for lookups
const ALL_SPORT_PILLS = [...MODELED_SPORTS, ...MORE_SPORTS];

const SPORT_ORDER = [
  // US Major Sports first
  'americanfootball_nfl',
  'basketball_nba',
  'icehockey_nhl',
  'baseball_mlb',
  'americanfootball_ncaaf',
  'basketball_ncaab',
  'basketball_wnba',
  // Soccer
  'soccer_usa_mls',
  'soccer_epl',
  'soccer_spain_la_liga',
  'soccer_germany_bundesliga',
  'soccer_italy_serie_a',
  'soccer_france_ligue_one',
  'soccer_uefa_champs_league',
  'soccer_uefa_europa_league',
  'soccer_efl_champ',
  'soccer_netherlands_eredivisie',
  'soccer_mexico_ligamx',
  'soccer_fa_cup',
  // Combat Sports
  'mma_mixed_martial_arts',
  'boxing_boxing',
  // Tennis
  'tennis_atp_australian_open',
  'tennis_atp_french_open',
  'tennis_atp_us_open',
  'tennis_atp_wimbledon',
  // Golf
  'golf_masters_tournament_winner',
  'golf_pga_championship_winner',
  'golf_us_open_winner',
  'golf_the_open_championship_winner',
  // Hockey - Other
  'icehockey_ahl',
  'icehockey_sweden_hockey_league',
  'icehockey_liiga',
  // Basketball - Other
  'basketball_euroleague',
  // Other Sports
  'rugbyleague_nrl',
  'aussierules_afl',
  'cricket_ipl',
  'cricket_big_bash',
];

const AVAILABLE_BOOKS = ['fanduel', 'draftkings'];

// Core sports that should ALWAYS be visible and enabled (even with 0 games)
const CORE_SPORTS = MODELED_SPORTS.map(s => s.key);

interface SportsHomeGridProps {
  games: Record<string, any[]>;
  dataSource?: 'backend' | 'odds_api' | 'none';
  totalGames?: number;
  totalEdges?: number;
  fetchedAt?: string;
}

export function SportsHomeGrid({ games: initialGames, dataSource: initialDataSource = 'none', totalGames: initialTotalGames = 0, totalEdges: initialTotalEdges = 0, fetchedAt: initialFetchedAt }: SportsHomeGridProps) {
  const [activeSport, setActiveSportRaw] = useState<string | null>(null);

  // Wrapper to log ALL activeSport changes
  const setActiveSport = (newValue: string | null, source: string = 'unknown') => {
    console.log(`[SPORT CHANGE] ${source}: activeSport changing from "${activeSport}" to "${newValue}"`);
    console.trace('[SPORT CHANGE] Stack trace:');
    setActiveSportRaw(newValue);
  };
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

  const refreshData = useCallback(async (showSpinner = true) => {
    console.log('[REFRESH] Starting refresh, activeSport before:', activeSport);
    if (showSpinner) setIsRefreshing(true);
    try {
      const res = await fetch('/api/odds/dashboard');
      if (!res.ok) throw new Error('Refresh failed');
      const data = await res.json();

      console.log('[REFRESH] Got data:', {
        sports: Object.keys(data.games || {}),
        gameCounts: Object.fromEntries(
          Object.entries(data.games || {}).map(([k, v]: [string, any]) => [k, v?.length || 0])
        ),
        totalGames: data.totalGames,
      });

      setGames(data.games || {});
      setTotalGames(data.totalGames || 0);
      setTotalEdges(data.totalEdges || 0);
      setLastUpdated(new Date());
      setSecondsSinceUpdate(0);
      if (data.games && Object.keys(data.games).length > 0) {
        setDataSource('odds_api');
      }
      console.log('[REFRESH] Completed, activeSport after:', activeSport);
    } catch (e) {
      console.error('[SportsHomeGrid] Refresh error:', e);
    } finally {
      if (showSpinner) setIsRefreshing(false);
    }
  }, [activeSport]);

  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());
    setLastUpdated(initialFetchedAt ? new Date(initialFetchedAt) : new Date());
    // Reset to "All Sports" view on mount/navigation to ensure "+ more games" buttons are visible
    setActiveSport(null, 'mount-effect');
  }, [initialFetchedAt]);


  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsBookDropdownOpen(false);
      }
      if (moreSportsRef.current && !moreSportsRef.current.contains(event.target as Node)) {
        setShowMoreSports(false);
      }
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

  // Smart sport ordering: games today first, then this week, then rest
  const orderedGames = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const todayEnd = new Date(todayStart.getTime() + 24 * 60 * 60 * 1000);
    const weekEnd = new Date(todayStart.getTime() + 7 * 24 * 60 * 60 * 1000);

    // Collect all sport keys (SPORT_ORDER first, then any extras)
    const allSportKeys = [...SPORT_ORDER];
    Object.keys(games).forEach(key => {
      if (!allSportKeys.includes(key)) allSportKeys.push(key);
    });

    // Build metadata per sport
    const sportMeta: { key: string; games: any[]; gamesToday: number; gamesWithOdds: number }[] = [];

    for (const sportKey of allSportKeys) {
      const sportGames = games[sportKey];
      if (!sportGames || sportGames.length === 0) continue;

      let gamesToday = 0;
      let gamesWithOdds = 0;

      for (const g of sportGames) {
        const t = new Date(g.commenceTime);
        if (t >= todayStart && t < todayEnd) gamesToday++;
        const hasOdds = g.consensus?.spreads?.line !== undefined ||
                       g.consensus?.h2h?.homePrice !== undefined ||
                       g.consensus?.totals?.line !== undefined;
        if (hasOdds) gamesWithOdds++;
      }

      sportMeta.push({ key: sportKey, games: sportGames, gamesToday, gamesWithOdds });
    }

    // Sort: (1) has games today with odds, (2) has games today no odds, (3) future games with odds, (4) rest
    sportMeta.sort((a, b) => {
      const aTier = a.gamesToday > 0 && a.gamesWithOdds > 0 ? 0
                  : a.gamesToday > 0 ? 1
                  : a.gamesWithOdds > 0 ? 2 : 3;
      const bTier = b.gamesToday > 0 && b.gamesWithOdds > 0 ? 0
                  : b.gamesToday > 0 ? 1
                  : b.gamesWithOdds > 0 ? 2 : 3;
      if (aTier !== bTier) return aTier - bTier;
      // Within same tier, keep SPORT_ORDER priority
      const aOrder = SPORT_ORDER.indexOf(a.key);
      const bOrder = SPORT_ORDER.indexOf(b.key);
      if (aOrder !== -1 && bOrder !== -1) return aOrder - bOrder;
      if (aOrder !== -1) return -1;
      if (bOrder !== -1) return 1;
      return b.gamesWithOdds - a.gamesWithOdds;
    });

    const result: Record<string, any[]> = {};
    for (const entry of sportMeta) {
      result[entry.key] = entry.games;
    }
    return result;
  }, [games]);

  // Separate live games from pregame games
  const { liveGames: allLiveGames, pregameGames } = useMemo(() => {
    const live: any[] = [];
    const pregame: Record<string, any[]> = {};

    for (const [sportKey, sportGames] of Object.entries(orderedGames)) {
      const pregameForSport: any[] = [];
      for (const game of sportGames) {
        const state = getGameState(game.commenceTime, game.sportKey);
        if (state === 'live') {
          live.push({ ...game, sportKey });
        } else if (state === 'upcoming') {
          pregameForSport.push(game);
        }
        // Skip 'final' games from dashboard
      }
      if (pregameForSport.length > 0) {
        pregame[sportKey] = pregameForSport;
      }
    }

    return { liveGames: live, pregameGames: pregame };
  }, [orderedGames]);

  const hasLiveGames = allLiveGames.length > 0;

  // Faster refresh when live games are present
  useEffect(() => {
    if (!mounted) return;
    const interval = hasLiveGames ? 20000 : 45000; // 20s for live, 45s otherwise
    console.log('[INTERVAL] Setting up live-aware refresh every', interval/1000, 'seconds, hasLiveGames:', hasLiveGames);
    const refreshTimer = setInterval(() => {
      console.log('[INTERVAL] Auto-refresh triggered (live-aware), activeSport:', activeSport);
      refreshData(false);
    }, interval);
    return () => {
      console.log('[INTERVAL] Clearing live-aware refresh timer');
      clearInterval(refreshTimer);
    };
  }, [mounted, refreshData, hasLiveGames, activeSport]);

  const filteredGames = useMemo(() => {
    // Use pregameGames instead of orderedGames to exclude live games
    const source = activeSport
      ? { [activeSport]: pregameGames[activeSport] || [] }
      : pregameGames;

    if (!searchQuery.trim()) {
      return source;
    }

    const query = searchQuery.toLowerCase();
    const result: Record<string, any[]> = {};

    for (const [sportKey, sportGames] of Object.entries(source)) {
      const matched = sportGames.filter((g: any) =>
        g.homeTeam?.toLowerCase().includes(query) ||
        g.awayTeam?.toLowerCase().includes(query)
      );
      if (matched.length > 0) result[sportKey] = matched;
    }
    return result;
  }, [searchQuery, activeSport, pregameGames]);

  const isAllView = activeSport === null;
  const selectedBookConfig = BOOK_CONFIG[selectedBook];
  const activeSportsCount = Object.keys(games).filter(k => games[k]?.length > 0).length;
  const hasAnyGames = totalGames > 0 || Object.values(games).some(g => g.length > 0);

  // Debug: Log render state
  console.log('[RENDER]', {
    activeSport,
    isAllView,
    gameCounts: Object.fromEntries(
      Object.entries(games).map(([k, v]) => [k, v?.length || 0])
    ),
    filteredGamesSports: Object.keys(filteredGames),
  });

  return (
    <div>
      {/* Premium Status Bar */}
      <div className="mb-6 p-4 bg-gradient-to-r from-zinc-900/80 to-zinc-900/40 rounded-xl border border-zinc-800/60">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${dataSource !== 'none' ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50 animate-pulse' : 'bg-red-400 shadow-lg shadow-red-400/50'}`} />
              <span className={`text-xs font-semibold ${dataSource !== 'none' ? 'text-emerald-400' : 'text-red-400'}`}>
                {dataSource !== 'none' ? 'LIVE FEED' : 'OFFLINE'}
              </span>
            </div>

            <div className="h-4 w-px bg-zinc-800" />

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-800/60 rounded-lg">
                <span className="text-[10px] font-mono text-zinc-500">GAMES</span>
                <span className="text-xs font-mono font-bold text-zinc-200">{totalGames || Object.values(games).reduce((a, g) => a + g.length, 0)}</span>
              </div>

              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-800/60 rounded-lg">
                <span className="text-[10px] font-mono text-zinc-500">MARKETS</span>
                <span className="text-xs font-mono font-bold text-zinc-200">{activeSportsCount}</span>
              </div>

              {totalEdges > 0 && (
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                  <span className="text-[10px] font-mono text-emerald-500">EDGES</span>
                  <span className="text-xs font-mono font-bold text-emerald-400">{totalEdges}</span>
                </div>
              )}

            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 bg-zinc-800/40 rounded-lg" suppressHydrationWarning>
              {hasLiveGames && (
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-amber-500"></span>
                </span>
              )}
              <span className={`text-[10px] font-mono ${secondsSinceUpdate > 60 ? 'text-amber-500' : 'text-zinc-500'}`}>
                {hasLiveGames && <span className="text-amber-400 mr-1">LIVE</span>}
                Updated {secondsSinceUpdate < 60 ? `${secondsSinceUpdate}s` : `${Math.floor(secondsSinceUpdate / 60)}m`} ago
              </span>
            </div>

            <button
              onClick={() => refreshData(true)}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-2.5 py-1.5 bg-zinc-800/60 hover:bg-zinc-700/60 border border-zinc-700/50 rounded-lg transition-colors disabled:opacity-50"
              title="Refresh odds and recalculate edges"
            >
              <svg
                className={`w-3.5 h-3.5 text-zinc-400 ${isRefreshing ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span className="text-[10px] font-medium text-zinc-400">
                {isRefreshing ? 'Updating...' : 'Refresh'}
              </span>
            </button>

            <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/40 rounded-lg" suppressHydrationWarning>
              <svg className="w-3.5 h-3.5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs font-mono text-zinc-400">
                {currentTime ? currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : '--:--:--'}
              </span>
              <span className="text-[10px] font-mono text-zinc-600">ET</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-5">
        <div className="relative max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search teams..."
            className="w-full bg-zinc-900/80 border border-zinc-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-emerald-500/40 focus:bg-zinc-900 transition-all font-mono"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Sport pills + Book dropdown */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex gap-1.5 overflow-x-auto pb-2 flex-1 items-center">
          <button
            onClick={() => setActiveSport(null, 'all-button-click')}
            className={`flex-shrink-0 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all border ${
              activeSport === null
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:border-zinc-700 hover:text-zinc-300'
            }`}
          >
            ALL
          </button>
          {MODELED_SPORTS.map((sport) => {
            const gameCount = games[sport.key]?.length || 0;
            return (
              <button
                key={sport.key}
                onClick={() => setActiveSport(sport.key, 'sport-pill-click')}
                className={`flex-shrink-0 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all border flex items-center gap-1.5 ${
                  activeSport === sport.key
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:border-zinc-700 hover:text-zinc-300'
                }`}
              >
                {sport.label}
                {gameCount > 0 && (
                  <span className={`text-[9px] font-mono ${activeSport === sport.key ? 'text-emerald-500' : 'text-zinc-600'}`}>
                    {gameCount}
                  </span>
                )}
              </button>
            );
          })}

          {/* More sports dropdown */}
          <div className="relative flex-shrink-0" ref={moreSportsRef}>
            <button
              onClick={() => setShowMoreSports(!showMoreSports)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all border flex items-center gap-1 ${
                !MODELED_SPORT_KEYS.has(activeSport || '') && activeSport !== null
                  ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                  : 'bg-zinc-900 text-zinc-500 border-zinc-800 hover:border-zinc-700 hover:text-zinc-300'
              }`}
            >
              More
              <svg className={`w-3 h-3 transition-transform ${showMoreSports ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {showMoreSports && (
              <div className="absolute left-0 z-50 mt-1.5 w-48 max-h-64 overflow-y-auto bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl">
                {MORE_SPORTS.map((sport) => {
                  const gameCount = games[sport.key]?.length || 0;
                  if (gameCount === 0) return null;
                  return (
                    <button
                      key={sport.key}
                      onClick={() => { setActiveSport(sport.key, 'more-sport-click'); setShowMoreSports(false); }}
                      className={`w-full flex items-center justify-between px-3 py-2 text-left transition-all text-xs ${
                        activeSport === sport.key ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-800 text-zinc-300'
                      }`}
                    >
                      <span>{sport.label}</span>
                      <span className="text-[9px] font-mono text-zinc-600">{gameCount}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Book Dropdown */}
        <div className="relative flex-shrink-0" ref={dropdownRef}>
          <button
            onClick={() => setIsBookDropdownOpen(!isBookDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-md hover:border-zinc-700 transition-all"
          >
            <BookIcon bookKey={selectedBook} size={20} />
            <span className="font-medium text-zinc-200 text-xs">{selectedBookConfig?.name}</span>
            <svg
              className={`w-3.5 h-3.5 text-zinc-500 transition-transform ${isBookDropdownOpen ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {isBookDropdownOpen && (
            <div className="absolute right-0 z-50 mt-1.5 w-44 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl overflow-hidden">
              {AVAILABLE_BOOKS.map((book) => {
                const config = BOOK_CONFIG[book];
                const isSelected = book === selectedBook;
                return (
                  <button
                    key={book}
                    onClick={() => {
                      setSelectedBook(book);
                      setIsBookDropdownOpen(false);
                    }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2.5 text-left transition-all ${
                      isSelected ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-zinc-800 text-zinc-300'
                    }`}
                  >
                    <BookIcon bookKey={book} size={22} />
                    <span className="font-medium text-sm">{config?.name}</span>
                    {isSelected && (
                      <svg className="w-3.5 h-3.5 ml-auto text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
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
          <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-zinc-300 mb-2">No Active Markets</h3>
          <p className="text-sm text-zinc-500 text-center max-w-md mb-1">
            {dataSource === 'none'
              ? 'Unable to connect to data sources. The Edge Engine backend and Odds API are both unreachable.'
              : 'No upcoming games found across monitored sports. Markets will populate when games are scheduled.'}
          </p>
          <div className="flex items-center gap-3 mt-4">
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-md">
              <div className={`w-1.5 h-1.5 rounded-full ${dataSource !== 'none' ? 'bg-emerald-400' : 'bg-red-400'}`} />
              <span className="text-[10px] font-mono text-zinc-500">
                {dataSource === 'backend' ? 'BACKEND OK' : dataSource === 'odds_api' ? 'API OK' : 'NO CONNECTION'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Search empty state */}
      {hasAnyGames && searchQuery && Object.keys(filteredGames).length === 0 && (
        <div className="flex flex-col items-center justify-center py-16">
          <p className="text-sm text-zinc-500">No games matching &ldquo;{searchQuery}&rdquo;</p>
          <button onClick={() => setSearchQuery('')} className="mt-2 text-xs text-emerald-400 hover:text-emerald-300">
            Clear search
          </button>
        </div>
      )}

      {/* Main Content with Sidebar */}
      <div className="flex gap-6">
        {/* Games Grid - Pregame Only */}
        <div className="flex-1 space-y-8">
        {Object.entries(filteredGames).map(([sportKey, sportGames]) => {
          if (!sportGames || sportGames.length === 0) return null;

          const sportInfo = SUPPORTED_SPORTS.find(s => s.key === sportKey);
          const sportLabel = ALL_SPORT_PILLS.find(s => s.key === sportKey)?.label;
          const sportName = sportLabel || sportInfo?.name || sportKey;

          // Check if ANY game in this sport has odds
          const gamesWithOdds = sportGames.filter((g: any) =>
            g.consensus?.spreads?.line !== undefined ||
            g.consensus?.h2h?.homePrice !== undefined ||
            g.consensus?.totals?.line !== undefined
          ).length;

          // Collapsed single-line for sports with 0 odds-loaded games
          if (gamesWithOdds === 0) {
            return (
              <div key={sportKey} className="flex items-center justify-between py-2.5 px-3 bg-zinc-900/40 border border-zinc-800/40 rounded-lg opacity-50">
                <div className="flex items-center gap-2">
                  <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">{sportName}</h2>
                  <span className="text-[10px] font-mono text-zinc-600">&middot;</span>
                  <span className="text-[10px] font-mono text-zinc-600">{sportGames.length} game{sportGames.length !== 1 ? 's' : ''}</span>
                  <span className="text-[10px] font-mono text-zinc-600">&middot;</span>
                  <span className="text-[10px] font-mono text-zinc-600">No odds available</span>
                </div>
                <Link
                  href={`/edge/portal/sports/${sportKey}`}
                  className="text-[10px] text-zinc-600 hover:text-zinc-400 font-mono transition-colors"
                >
                  View
                </Link>
              </div>
            );
          }

          const gamesToShow = isAllView && !searchQuery
            ? sportGames.slice(0, GAMES_PER_SPORT_IN_ALL_VIEW)
            : sportGames;

          const hasMoreGames = isAllView && !searchQuery && sportGames.length > GAMES_PER_SPORT_IN_ALL_VIEW;

          return (
            <div key={sportKey}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <h2 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">{sportName}</h2>
                  <span className="text-[10px] font-mono text-zinc-600">&middot;</span>
                  <span className="text-[10px] font-mono text-zinc-500">{sportGames.length}</span>
                </div>
                <Link
                  href={`/edge/portal/sports/${sportKey}`}
                  className="text-xs text-zinc-500 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                >
                  View all
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {(() => {
                  // Pre-compute edges for sorting
                  const gamesWithEdge = gamesToShow.map((game: any) => {
                    const fair = game.fairLines;
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;
                    const { maxEdge } = calcMaxEdge(fair, spreads, h2h, totals);
                    return { game, maxEdge };
                  });

                  // Sort: highest edge first, NO EDGE (<1%) last
                  gamesWithEdge.sort((a, b) => b.maxEdge - a.maxEdge);

                  // Split into edge / no-edge groups
                  const withEdge = gamesWithEdge.filter(g => g.maxEdge >= 1);
                  const noEdge = gamesWithEdge.filter(g => g.maxEdge < 1);

                  const renderCard = ({ game, maxEdge }: { game: any; maxEdge: number }, isNoEdge = false) => {
                    const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
                    const timeStr = mounted
                      ? gameTime.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })
                      : '';
                    const countdown = mounted ? getTimeDisplay(gameTime, game.sportKey) : '';
                    const isLive = countdown === 'LIVE';

                    const fair = game.fairLines;
                    const bookOdds = game.bookmakers?.[selectedBook];
                    const spreads = bookOdds?.spreads || game.consensus?.spreads;
                    const h2h = bookOdds?.h2h || game.consensus?.h2h;
                    const totals = bookOdds?.totals || game.consensus?.totals;
                    const bookLabel = selectedBook === 'fanduel' ? 'FD' : 'DK';

                    // Edge calculations
                    let homeSpreadEdge: number | undefined, awaySpreadEdge: number | undefined;
                    if (fair?.fair_spread != null && spreads?.line !== undefined) {
                      homeSpreadEdge = (spreads.line - fair.fair_spread) * 3.0;
                      awaySpreadEdge = -homeSpreadEdge;
                    }

                    let homeMLEdge: number | undefined, awayMLEdge: number | undefined;
                    if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice !== undefined && h2h?.awayPrice !== undefined) {
                      const toProb = (o: number) => o < 0 ? Math.abs(o) / (Math.abs(o) + 100) : 100 / (o + 100);
                      const fairHP = toProb(fair.fair_ml_home);
                      const fairAP = toProb(fair.fair_ml_away);
                      const bookHP = toProb(h2h.homePrice);
                      const bookAP = toProb(h2h.awayPrice);
                      const normBHP = bookHP / (bookHP + bookAP);
                      const normBAP = bookAP / (bookHP + bookAP);
                      homeMLEdge = (fairHP - normBHP) * 100;
                      awayMLEdge = (fairAP - normBAP) * 100;
                    }

                    let overEdge: number | undefined, underEdge: number | undefined;
                    if (fair?.fair_total != null && totals?.line !== undefined) {
                      overEdge = (fair.fair_total - totals.line) * 1.5;
                      underEdge = -overEdge;
                    }

                    const tier = getSignalTier(maxEdge);
                    const tierStyle = SIGNAL_TIER_STYLE[tier];
                    const hasOdds = spreads?.line !== undefined || h2h?.homePrice !== undefined || totals?.line !== undefined;

                    // Composite score for conviction bar (average of available composites)
                    const composites = [fair?.composite_spread, fair?.composite_total, fair?.composite_ml].filter((v: any) => v != null) as number[];
                    const avgComposite = composites.length > 0 ? composites.reduce((a: number, b: number) => a + b, 0) / composites.length : null;

                    // Best edge side highlight (which team row to emphasize)
                    const homeEdgeMax = Math.max(homeSpreadEdge ?? 0, homeMLEdge ?? 0);
                    const awayEdgeMax = Math.max(awaySpreadEdge ?? 0, awayMLEdge ?? 0);
                    const edgeSide: 'home' | 'away' | null = homeEdgeMax > 1 || awayEdgeMax > 1
                      ? (homeEdgeMax >= awayEdgeMax ? 'home' : 'away')
                      : null;

                    return (
                      <Link
                        key={game.id}
                        href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                        className={`bg-[#0f0f0f] rounded-lg overflow-hidden hover:bg-[#111111] transition-all group ${
                          isLive
                            ? 'border-2 border-red-500/50 shadow-lg shadow-red-500/10'
                            : isNoEdge
                            ? 'border border-zinc-800/50 opacity-60'
                            : !hasOdds
                            ? 'border border-zinc-800/50 opacity-30'
                            : 'border border-zinc-800/80 hover:border-zinc-700'
                        } ${tierStyle.glow ? `shadow-md ${tierStyle.glow}` : ''}`}
                      >
                        {/* Card Header: time + signal badge + CEQ bar */}
                        <div className="px-3 py-2 border-b border-zinc-800/50 flex items-center justify-between bg-zinc-900/40">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono text-zinc-500" suppressHydrationWarning>{timeStr}</span>
                            {isLive ? (
                              <span className="flex items-center gap-1.5 text-[10px] font-semibold text-red-400 bg-red-500/20 px-2 py-0.5 rounded-full">
                                <span className="relative flex h-1.5 w-1.5">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"></span>
                                </span>
                                LIVE
                              </span>
                            ) : countdown === 'FINAL' ? (
                              <span className="text-[10px] font-semibold text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-full">FINAL</span>
                            ) : (
                              <span className="text-[10px] font-mono text-zinc-600 bg-zinc-800/50 px-1.5 py-0.5 rounded">{countdown}</span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {hasOdds && fair && (
                              <span className={`text-[9px] font-bold font-mono px-2 py-0.5 rounded-full border ${tierStyle.text} ${tierStyle.bg} ${tierStyle.border}`}>
                                {tierStyle.label}
                              </span>
                            )}
                            {avgComposite != null && <ConvictionBar score={avgComposite} />}
                          </div>
                        </div>

                        {/* Live Score */}
                        {isLive && game.scores && (
                          <div className="px-3 py-1.5 border-b border-zinc-800/30 bg-zinc-900/60 flex items-center justify-center">
                            <span className="text-lg font-bold font-mono text-zinc-100">
                              {game.scores.away} - {game.scores.home}
                            </span>
                          </div>
                        )}

                        {/* Away Team Block */}
                        <div className={`px-3 py-2 ${edgeSide === 'away' ? 'border-l-2 border-l-cyan-500/50 bg-cyan-500/[0.03]' : ''}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                            <span className="text-xs text-zinc-200 truncate font-medium flex-1">{getDisplayTeamName(game.awayTeam, game.sportKey)}</span>
                          </div>
                          <div className="flex items-center gap-3 ml-7">
                            {/* OMI Fair Spread — hero */}
                            {fair?.fair_spread != null ? (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">OMI</span>
                                <span className="text-sm font-bold font-mono text-cyan-400">{fmtSpread(-fair.fair_spread)}</span>
                              </div>
                            ) : spreads?.line !== undefined ? (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">SPRD</span>
                                <span className="text-sm font-mono text-zinc-300">{fmtSpread(-spreads.line)}</span>
                              </div>
                            ) : null}
                            {/* Book spread + edge */}
                            {fair?.fair_spread != null && spreads?.line !== undefined && (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">{bookLabel}</span>
                                <span className="text-[11px] font-mono text-zinc-400">{fmtSpread(-spreads.line)}</span>
                                {awaySpreadEdge !== undefined && Math.abs(awaySpreadEdge) >= 1 && (
                                  <span className={`text-[9px] font-mono font-semibold ${awaySpreadEdge > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {awaySpreadEdge > 0 ? '+' : ''}{awaySpreadEdge.toFixed(1)}%
                                  </span>
                                )}
                              </div>
                            )}
                            {/* ML */}
                            {h2h?.awayPrice !== undefined && (
                              <div className="flex items-center gap-1 ml-auto">
                                <span className="text-[9px] font-mono text-zinc-600">ML</span>
                                <span className="text-[11px] font-mono text-zinc-400">{fmtOdds(h2h.awayPrice)}</span>
                                {awayMLEdge !== undefined && Math.abs(awayMLEdge) >= 1 && (
                                  <span className={`text-[9px] font-mono ${awayMLEdge > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {awayMLEdge > 0 ? '+' : ''}{awayMLEdge.toFixed(1)}%
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Divider */}
                        <div className="border-b border-zinc-800/30 mx-3" />

                        {/* Home Team Block */}
                        <div className={`px-3 py-2 ${edgeSide === 'home' ? 'border-l-2 border-l-cyan-500/50 bg-cyan-500/[0.03]' : ''}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                            <span className="text-xs text-zinc-200 truncate font-medium flex-1">{getDisplayTeamName(game.homeTeam, game.sportKey)}</span>
                          </div>
                          <div className="flex items-center gap-3 ml-7">
                            {/* OMI Fair Spread — hero */}
                            {fair?.fair_spread != null ? (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">OMI</span>
                                <span className="text-sm font-bold font-mono text-cyan-400">{fmtSpread(fair.fair_spread)}</span>
                              </div>
                            ) : spreads?.line !== undefined ? (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">SPRD</span>
                                <span className="text-sm font-mono text-zinc-300">{fmtSpread(spreads.line)}</span>
                              </div>
                            ) : null}
                            {/* Book spread + edge */}
                            {fair?.fair_spread != null && spreads?.line !== undefined && (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] font-mono text-zinc-600">{bookLabel}</span>
                                <span className="text-[11px] font-mono text-zinc-400">{fmtSpread(spreads.line)}</span>
                                {homeSpreadEdge !== undefined && Math.abs(homeSpreadEdge) >= 1 && (
                                  <span className={`text-[9px] font-mono font-semibold ${homeSpreadEdge > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {homeSpreadEdge > 0 ? '+' : ''}{homeSpreadEdge.toFixed(1)}%
                                  </span>
                                )}
                              </div>
                            )}
                            {/* ML */}
                            {h2h?.homePrice !== undefined && (
                              <div className="flex items-center gap-1 ml-auto">
                                <span className="text-[9px] font-mono text-zinc-600">ML</span>
                                <span className="text-[11px] font-mono text-zinc-400">{fmtOdds(h2h.homePrice)}</span>
                                {homeMLEdge !== undefined && Math.abs(homeMLEdge) >= 1 && (
                                  <span className={`text-[9px] font-mono ${homeMLEdge > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {homeMLEdge > 0 ? '+' : ''}{homeMLEdge.toFixed(1)}%
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Draw Row - Soccer only */}
                        {game.sportKey?.includes('soccer') && (() => {
                          const drawPrice = h2h?.drawPrice ?? h2h?.draw;
                          if (!drawPrice) return null;
                          return (
                            <>
                              <div className="border-b border-zinc-800/30 mx-3" />
                              <div className="px-3 py-1.5 flex items-center gap-3">
                                <div className="w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold text-zinc-500 bg-zinc-800 flex-shrink-0">X</div>
                                <span className="text-[11px] text-zinc-500 font-medium">Draw</span>
                                <span className="text-[11px] font-mono text-zinc-400 ml-auto">{fmtOdds(drawPrice)}</span>
                              </div>
                            </>
                          );
                        })()}

                        {/* Total Line Row */}
                        {(fair?.fair_total != null || totals?.line !== undefined) && (
                          <div className="px-3 py-1.5 border-t border-zinc-800/30 bg-zinc-900/30 flex items-center gap-3">
                            <span className="text-[9px] font-mono text-zinc-600 font-semibold">O/U</span>
                            {fair?.fair_total != null ? (
                              <>
                                <div className="flex items-center gap-1">
                                  <span className="text-[9px] font-mono text-zinc-600">OMI</span>
                                  <span className="text-xs font-bold font-mono text-cyan-400">{fair.fair_total.toFixed(1)}</span>
                                </div>
                                {totals?.line !== undefined && (
                                  <div className="flex items-center gap-1">
                                    <span className="text-[9px] font-mono text-zinc-600">{bookLabel}</span>
                                    <span className="text-[11px] font-mono text-zinc-400">{totals.line}</span>
                                    {overEdge !== undefined && Math.abs(overEdge) >= 0.5 && (
                                      <span className={`text-[9px] font-mono ${overEdge > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {overEdge > 0 ? 'O' : 'U'}{Math.abs(overEdge).toFixed(1)}%
                                      </span>
                                    )}
                                  </div>
                                )}
                              </>
                            ) : totals?.line !== undefined ? (
                              <span className="text-[11px] font-mono text-zinc-400">{totals.line}</span>
                            ) : null}
                          </div>
                        )}
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
                                className="flex items-center gap-2 text-[10px] font-mono text-zinc-600 hover:text-zinc-400 transition-colors py-1"
                              >
                                <svg className={`w-3 h-3 transition-transform ${noEdgeCollapsed ? '' : 'rotate-90'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                                {noEdge.length} NO EDGE game{noEdge.length !== 1 ? 's' : ''}
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
                <div className="mt-3 text-center">
                  <button
                    onClick={() => setActiveSport(sportKey, 'more-games-click')}
                    className="text-xs text-zinc-500 hover:text-emerald-400 font-mono transition-colors"
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
    </div>
  );
}