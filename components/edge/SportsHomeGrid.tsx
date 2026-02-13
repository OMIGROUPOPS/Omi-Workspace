'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { formatOdds, calculateTwoWayEV, formatEV, getEVColor, getEVBgClass } from '@/lib/edge/utils/odds-math';
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

function EdgeArrow({ value }: { value: number }) {
  if (Math.abs(value) < 0.5) return null;
  const isUp = value > 0;
  return (
    <svg width="8" height="8" viewBox="0 0 8 8" className="flex-shrink-0">
      <path
        d={isUp ? 'M4 1 L7 5 L5 5 L5 7 L3 7 L3 5 L1 5 Z' : 'M4 7 L7 3 L5 3 L5 1 L3 1 L3 3 L1 3 Z'}
        fill={isUp ? '#10b981' : '#ef4444'}
      />
    </svg>
  );
}

// CEQ-based styling helper
function getCEQStyles(ceq: number | undefined): { bgTint: string; borderTint: string; textColor: string } {
  if (ceq === undefined) {
    return { bgTint: 'bg-zinc-800/80', borderTint: 'border-zinc-700/50', textColor: 'text-zinc-500' };
  }
  if (ceq >= 76) return { bgTint: 'bg-emerald-500/20', borderTint: 'border-emerald-500/40', textColor: 'text-emerald-400' };
  if (ceq >= 66) return { bgTint: 'bg-emerald-500/15', borderTint: 'border-emerald-500/30', textColor: 'text-emerald-400' };
  if (ceq >= 56) return { bgTint: 'bg-emerald-500/10', borderTint: 'border-emerald-500/20', textColor: 'text-emerald-400' };
  if (ceq <= 35) return { bgTint: 'bg-red-500/15', borderTint: 'border-red-500/30', textColor: 'text-red-400' };
  if (ceq <= 45) return { bgTint: 'bg-red-500/10', borderTint: 'border-red-500/20', textColor: 'text-red-400' };
  return { bgTint: 'bg-zinc-800/80', borderTint: 'border-zinc-700/50', textColor: 'text-zinc-500' };
}

function OddsCell({ line, price, edgePct }: { line?: number | string; price: number; ev?: number; ceq?: number; topDrivers?: string[]; edgePct?: number }) {
  return (
    <div className="flex flex-col items-center justify-center p-1.5 bg-[#1a1f2b] border border-zinc-700/50 rounded hover:brightness-110 transition-all cursor-pointer">
      <div className="flex items-center gap-0.5">
        <span className="text-xs font-semibold text-zinc-100 font-mono">
          {line !== undefined && (typeof line === 'number' ? (line > 0 ? `+${line}` : line) : line)}
        </span>
      </div>
      <div className="flex items-center gap-1">
        <span className={`text-[11px] font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-300'}`}>
          {formatOdds(price)}
        </span>
        {edgePct !== undefined && Math.abs(edgePct) >= 1.0 && (
          <span className={`text-[9px] font-mono ${edgePct > 0 ? 'text-emerald-400' : 'text-red-400'}`}>{edgePct > 0 ? '+' : ''}{edgePct.toFixed(1)}%</span>
        )}
      </div>
    </div>
  );
}

function MoneylineCell({ price, edgePct }: { price: number; ev?: number; ceq?: number; topDrivers?: string[]; edgePct?: number }) {
  return (
    <div className="flex flex-col items-center justify-center p-1.5 bg-[#1a1f2b] border border-zinc-700/50 rounded hover:brightness-110 transition-all cursor-pointer">
      <div className="flex items-center gap-1">
        <span className={`text-xs font-semibold font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-100'}`}>
          {formatOdds(price)}
        </span>
        {edgePct !== undefined && Math.abs(edgePct) >= 1.0 && (
          <span className={`text-[9px] font-mono ${edgePct > 0 ? 'text-emerald-400' : 'text-red-400'}`}>{edgePct > 0 ? '+' : ''}{edgePct.toFixed(1)}%</span>
        )}
      </div>
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

// Sport pills grouped by category
const SPORT_PILLS = [
  // American Football
  { key: 'americanfootball_nfl', label: 'NFL', icon: 'football', group: 'Football' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF', icon: 'football', group: 'Football' },

  // Basketball
  { key: 'basketball_nba', label: 'NBA', icon: 'basketball', group: 'Basketball' },
  { key: 'basketball_ncaab', label: 'NCAAB', icon: 'basketball', group: 'Basketball' },
  { key: 'basketball_wnba', label: 'WNBA', icon: 'basketball', group: 'Basketball' },
  { key: 'basketball_euroleague', label: 'EuroLg', icon: 'basketball', group: 'Basketball' },

  // Hockey
  { key: 'icehockey_nhl', label: 'NHL', icon: 'hockey', group: 'Hockey' },
  { key: 'icehockey_ahl', label: 'AHL', icon: 'hockey', group: 'Hockey' },
  { key: 'icehockey_sweden_hockey_league', label: 'SHL', icon: 'hockey', group: 'Hockey' },
  { key: 'icehockey_liiga', label: 'Liiga', icon: 'hockey', group: 'Hockey' },

  // Baseball
  { key: 'baseball_mlb', label: 'MLB', icon: 'baseball', group: 'Baseball' },

  // Soccer - Major
  { key: 'soccer_usa_mls', label: 'MLS', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_epl', label: 'EPL', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_spain_la_liga', label: 'La Liga', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_germany_bundesliga', label: 'Bundes', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_italy_serie_a', label: 'Serie A', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_france_ligue_one', label: 'Ligue 1', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_uefa_champs_league', label: 'UCL', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_uefa_europa_league', label: 'Europa', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_efl_champ', label: 'EFL Ch', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_netherlands_eredivisie', label: 'Erediv', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_mexico_ligamx', label: 'Liga MX', icon: 'soccer', group: 'Soccer' },
  { key: 'soccer_fa_cup', label: 'FA Cup', icon: 'soccer', group: 'Soccer' },

  // Tennis
  { key: 'tennis_atp_australian_open', label: 'AUS Open', icon: 'tennis', group: 'Tennis' },
  { key: 'tennis_atp_french_open', label: 'FR Open', icon: 'tennis', group: 'Tennis' },
  { key: 'tennis_atp_us_open', label: 'US Open', icon: 'tennis', group: 'Tennis' },
  { key: 'tennis_atp_wimbledon', label: 'Wimbledon', icon: 'tennis', group: 'Tennis' },

  // Golf
  { key: 'golf_masters_tournament_winner', label: 'Masters', icon: 'golf', group: 'Golf' },
  { key: 'golf_pga_championship_winner', label: 'PGA', icon: 'golf', group: 'Golf' },
  { key: 'golf_us_open_winner', label: 'US Open', icon: 'golf', group: 'Golf' },
  { key: 'golf_the_open_championship_winner', label: 'The Open', icon: 'golf', group: 'Golf' },

  // Combat Sports
  { key: 'mma_mixed_martial_arts', label: 'UFC', icon: 'mma', group: 'Combat' },
  { key: 'boxing_boxing', label: 'Boxing', icon: 'boxing', group: 'Combat' },

  // Other
  { key: 'rugbyleague_nrl', label: 'NRL', icon: 'rugby', group: 'Other' },
  { key: 'aussierules_afl', label: 'AFL', icon: 'afl', group: 'Other' },
  { key: 'cricket_ipl', label: 'IPL', icon: 'cricket', group: 'Other' },
  { key: 'cricket_big_bash', label: 'Big Bash', icon: 'cricket', group: 'Other' },
];

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
const CORE_SPORTS = [
  'americanfootball_nfl',
  'basketball_nba',
  'icehockey_nhl',
  'baseball_mlb',
  'americanfootball_ncaaf',
  'basketball_ncaab',
  'basketball_wnba',
  'soccer_epl',
  'soccer_usa_mls',
  'mma_mixed_martial_arts',
];

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
  const [searchQuery, setSearchQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

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
        <div className="flex gap-1.5 overflow-x-auto pb-2 flex-1">
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
          {SPORT_PILLS.map((sport) => {
            const gameCount = games[sport.key]?.length || 0;
            const isCoreSport = CORE_SPORTS.includes(sport.key);
            // Core sports are always enabled, others only if they have games
            const isEnabled = isCoreSport || gameCount > 0;
            return (
              <button
                key={sport.key}
                onClick={() => isEnabled && setActiveSport(sport.key, 'sport-pill-click')}
                className={`flex-shrink-0 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all border flex items-center gap-1.5 ${
                  activeSport === sport.key
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : isEnabled
                    ? 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:border-zinc-700 hover:text-zinc-300'
                    : 'bg-zinc-900/50 text-zinc-600 border-zinc-800/50 cursor-default'
                }`}
                disabled={!isEnabled}
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
          const sportLabel = SPORT_PILLS.find(s => s.key === sportKey)?.label;
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

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
                {gamesToShow.map((game: any) => {
                  const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
                  const timeStr = mounted
                    ? gameTime.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })
                    : '';
                  const countdown = mounted ? getTimeDisplay(gameTime, game.sportKey) : '';

                  // Calculate edge percentages from fair lines
                  const fair = game.fairLines;
                  const bookOdds = game.bookmakers?.[selectedBook];
                  const spreads = bookOdds?.spreads || game.consensus?.spreads;
                  const h2h = bookOdds?.h2h || game.consensus?.h2h;
                  const totals = bookOdds?.totals || game.consensus?.totals;

                  // Spread edge: signed, both sides (positive = value on that side)
                  let homeSpreadEdge: number | undefined, awaySpreadEdge: number | undefined;
                  if (fair?.fair_spread != null && spreads?.line !== undefined) {
                    homeSpreadEdge = (spreads.line - fair.fair_spread) * 3.0;
                    awaySpreadEdge = -homeSpreadEdge;
                  }

                  // ML edge: signed implied probability gap
                  let homeMLEdge: number | undefined, awayMLEdge: number | undefined;
                  if (fair?.fair_ml_home != null && fair?.fair_ml_away != null && h2h?.homePrice !== undefined && h2h?.awayPrice !== undefined) {
                    const toProb = (o: number) => o < 0 ? Math.abs(o) / (Math.abs(o) + 100) : 100 / (o + 100);
                    const fairHomeProb = toProb(fair.fair_ml_home);
                    const fairAwayProb = toProb(fair.fair_ml_away);
                    const bookHomeProb = toProb(h2h.homePrice);
                    const bookAwayProb = toProb(h2h.awayPrice);
                    const normBHP = bookHomeProb / (bookHomeProb + bookAwayProb);
                    const normBAP = bookAwayProb / (bookHomeProb + bookAwayProb);
                    homeMLEdge = (fairHomeProb - normBHP) * 100;
                    awayMLEdge = (fairAwayProb - normBAP) * 100;
                  }

                  // Total edge: signed, both sides (positive over = fair higher than book)
                  let overEdge: number | undefined, underEdge: number | undefined;
                  if (fair?.fair_total != null && totals?.line !== undefined) {
                    overEdge = (fair.fair_total - totals.line) * 3.0;
                    underEdge = -overEdge;
                  }

                  // Check if card has any odds data
                  const hasOdds = spreads?.line !== undefined || h2h?.homePrice !== undefined || totals?.line !== undefined;

                  return (
                    <Link
                      key={game.id}
                      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                      className={`bg-[#0f0f0f] border border-zinc-800/80 hover:border-zinc-700 rounded-lg overflow-hidden hover:bg-[#111111] transition-all group ${!hasOdds ? 'opacity-30' : ''}`}
                    >
                      {/* Card Header */}
                      <div className="px-3 py-2 border-b flex items-center justify-between bg-zinc-900/40 border-zinc-800/50">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono text-zinc-500" suppressHydrationWarning>{timeStr}</span>
                          {countdown === 'LIVE' ? (
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
                            <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800/50 px-2 py-0.5 rounded">{countdown}</span>
                          )}
                          {(countdown === 'LIVE' || countdown === 'FINAL') && game.scores && (
                            <span className="text-sm font-bold font-mono text-zinc-100 bg-zinc-800/80 px-2 py-0.5 rounded border border-zinc-700/50">
                              {game.scores.away} - {game.scores.home}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Column Headers */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1 border-b border-zinc-800/30">
                        <span className="text-[9px] text-zinc-600 uppercase font-mono tracking-wider"></span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">SPRD</span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">ML</span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">O/U</span>
                      </div>

                      {/* Away Row */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                          <span className="text-xs text-zinc-200 truncate font-medium">{getDisplayTeamName(game.awayTeam, game.sportKey)}</span>
                        </div>
                        {spreads?.line !== undefined ? (
                          <OddsCell line={-spreads.line} price={spreads.awayPrice} edgePct={awaySpreadEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {h2h?.awayPrice !== undefined ? (
                          <MoneylineCell price={h2h.awayPrice} edgePct={awayMLEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {totals?.line !== undefined ? (
                          <OddsCell line={`O${totals.line}`} price={totals.overPrice} edgePct={overEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                      </div>

                      {/* Draw Row - Soccer only */}
                      {game.sportKey?.includes('soccer') && (() => {
                        const drawPrice = h2h?.drawPrice ?? h2h?.draw;
                        if (!drawPrice) return null;
                        return (
                          <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1 items-center bg-zinc-900/30">
                            <div className="flex items-center gap-2 min-w-0">
                              <div className="w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold text-zinc-400 bg-zinc-800 flex-shrink-0">
                                X
                              </div>
                              <span className="text-xs text-zinc-400 font-medium">Draw</span>
                            </div>
                            <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>
                            <MoneylineCell price={drawPrice} />
                            <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>
                          </div>
                        );
                      })()}

                      {/* Home Row */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                          <span className="text-xs text-zinc-200 truncate font-medium">{getDisplayTeamName(game.homeTeam, game.sportKey)}</span>
                        </div>
                        {spreads?.line !== undefined ? (
                          <OddsCell line={spreads.line} price={spreads.homePrice} edgePct={homeSpreadEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {h2h?.homePrice !== undefined ? (
                          <MoneylineCell price={h2h.homePrice} edgePct={homeMLEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {totals?.line !== undefined ? (
                          <OddsCell line={`U${totals.line}`} price={totals.underPrice} edgePct={underEdge} />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                      </div>
                    </Link>
                  );
                })}
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