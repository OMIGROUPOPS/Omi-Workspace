'use client';

import { useState, useRef, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { formatOdds } from '@/lib/edge/utils/odds-math';
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';

const NFL_TEAMS: Record<string, string> = {
  'Arizona Cardinals': 'ari', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'bal', 'Buffalo Bills': 'buf',
  'Carolina Panthers': 'car', 'Chicago Bears': 'chi', 'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle',
  'Dallas Cowboys': 'dal', 'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gb',
  'Houston Texans': 'hou', 'Indianapolis Colts': 'ind', 'Jacksonville Jaguars': 'jax', 'Kansas City Chiefs': 'kc',
  'Las Vegas Raiders': 'lv', 'Los Angeles Chargers': 'lac', 'Los Angeles Rams': 'lar', 'Miami Dolphins': 'mia',
  'Minnesota Vikings': 'min', 'New England Patriots': 'ne', 'New Orleans Saints': 'no', 'New York Giants': 'nyg',
  'New York Jets': 'nyj', 'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit', 'San Francisco 49ers': 'sf',
  'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tb', 'Tennessee Titans': 'ten', 'Washington Commanders': 'wsh',
};

const NBA_TEAMS: Record<string, string> = {
  'Atlanta Hawks': 'atl', 'Boston Celtics': 'bos', 'Brooklyn Nets': 'bkn', 'Charlotte Hornets': 'cha',
  'Chicago Bulls': 'chi', 'Cleveland Cavaliers': 'cle', 'Dallas Mavericks': 'dal', 'Denver Nuggets': 'den',
  'Detroit Pistons': 'det', 'Golden State Warriors': 'gs', 'Houston Rockets': 'hou', 'Indiana Pacers': 'ind',
  'LA Clippers': 'lac', 'Los Angeles Clippers': 'lac', 'Los Angeles Lakers': 'lal', 'LA Lakers': 'lal',
  'Memphis Grizzlies': 'mem', 'Miami Heat': 'mia', 'Milwaukee Bucks': 'mil', 'Minnesota Timberwolves': 'min',
  'New Orleans Pelicans': 'no', 'New York Knicks': 'ny', 'Oklahoma City Thunder': 'okc', 'Orlando Magic': 'orl',
  'Philadelphia 76ers': 'phi', 'Phoenix Suns': 'phx', 'Portland Trail Blazers': 'por', 'Sacramento Kings': 'sac',
  'San Antonio Spurs': 'sa', 'Toronto Raptors': 'tor', 'Utah Jazz': 'utah', 'Washington Wizards': 'wsh',
};

const NHL_TEAMS: Record<string, string> = {
  'Anaheim Ducks': 'ana', 'Boston Bruins': 'bos', 'Buffalo Sabres': 'buf', 'Calgary Flames': 'cgy',
  'Carolina Hurricanes': 'car', 'Chicago Blackhawks': 'chi', 'Colorado Avalanche': 'col',
  'Columbus Blue Jackets': 'cbj', 'Dallas Stars': 'dal', 'Detroit Red Wings': 'det', 'Edmonton Oilers': 'edm',
  'Florida Panthers': 'fla', 'Los Angeles Kings': 'la', 'Minnesota Wild': 'min', 'Montreal Canadiens': 'mtl',
  'Nashville Predators': 'nsh', 'New Jersey Devils': 'nj', 'New York Islanders': 'nyi', 'New York Rangers': 'nyr',
  'Ottawa Senators': 'ott', 'Philadelphia Flyers': 'phi', 'Pittsburgh Penguins': 'pit', 'San Jose Sharks': 'sj',
  'Seattle Kraken': 'sea', 'St. Louis Blues': 'stl', 'Tampa Bay Lightning': 'tb', 'Toronto Maple Leafs': 'tor',
  'Utah Hockey Club': 'utah', 'Vancouver Canucks': 'van', 'Vegas Golden Knights': 'vgk',
  'Washington Capitals': 'wsh', 'Winnipeg Jets': 'wpg',
};

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
};

const GAMES_PER_SPORT_IN_ALL_VIEW = 6;

function getTeamLogo(teamName: string, sportKey: string): string | null {
  if (sportKey.includes('nfl')) {
    const abbrev = NFL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbrev}.png`;
  }
  if (sportKey.includes('nba')) {
    const abbrev = NBA_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nba/500/${abbrev}.png`;
  }
  if (sportKey.includes('nhl') || sportKey.includes('icehockey')) {
    const abbrev = NHL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nhl/500/${abbrev}.png`;
  }
  return null;
}

function getTeamColor(teamName: string): string {
  const colors = ['#1d4ed8', '#dc2626', '#059669', '#d97706', '#7c3aed', '#db2777', '#0891b2', '#65a30d'];
  const hash = teamName.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

function getTeamInitials(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 2).toUpperCase();
  return words[0].slice(0, 2).toUpperCase();
}

function getDisplayTeamName(teamName: string, sportKey: string): string {
  if (sportKey.includes('ncaa')) {
    return teamName;
  }
  const words = teamName.split(' ');
  return words[words.length - 1];
}

function TeamLogo({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  if (logo) return <img src={logo} alt={teamName} className="w-5 h-5 object-contain" />;

  return (
    <div
      className="w-5 h-5 rounded-full flex items-center justify-center text-[7px] font-bold text-white flex-shrink-0"
      style={{ backgroundColor: getTeamColor(teamName) }}
    >
      {getTeamInitials(teamName)}
    </div>
  );
}

function getMockEdge(gameId: string, marketIndex: number, bookSeed: number = 0): number {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + bookSeed;
  const x = Math.sin(seed + marketIndex) * 10000;
  return ((x - Math.floor(x)) - 0.5) * 10;
}

function MiniSparkline({ gameId, marketIndex, bookSeed = 0 }: { gameId: string; marketIndex: number; bookSeed?: number }) {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + marketIndex + bookSeed;
  const points: number[] = [];
  for (let i = 0; i < 8; i++) {
    const x = Math.sin(seed + i * 0.7) * 10000;
    points.push((x - Math.floor(x)) * 10);
  }

  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const height = 12;
  const width = 24;

  const pathData = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * width;
      const y = height - ((p - min) / range) * height;
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');

  const trend = points[points.length - 1] - points[0];
  const color = trend >= 0 ? '#10b981' : '#ef4444';

  return (
    <svg width={width} height={height} className="opacity-60">
      <path d={pathData} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
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

function OddsCell({ line, price, gameId, marketIndex, bookSeed = 0 }: { line?: number | string; price: number; gameId: string; marketIndex: number; bookSeed?: number }) {
  const edge = getMockEdge(gameId, marketIndex, bookSeed);
  const edgeColor = edge >= 0 ? 'text-emerald-400' : 'text-red-400';
  const bgTint = edge >= 2 ? 'bg-emerald-500/10' : edge <= -2 ? 'bg-red-500/5' : 'bg-zinc-800/80';
  const borderTint = edge >= 3 ? 'border-emerald-500/30' : edge <= -3 ? 'border-red-500/20' : 'border-zinc-700/50';

  return (
    <div className={`flex flex-col items-center justify-center p-1.5 ${bgTint} border ${borderTint} rounded hover:border-zinc-600 transition-all cursor-pointer group`}>
      <div className="flex items-center gap-0.5">
        <span className="text-xs font-semibold text-zinc-100 font-mono">
          {line !== undefined && (typeof line === 'number' ? (line > 0 ? `+${line}` : line) : line)}
        </span>
      </div>
      <span className={`text-[11px] font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-300'}`}>
        {formatOdds(price)}
      </span>
      <div className="flex items-center gap-0.5 mt-0.5">
        <MiniSparkline gameId={gameId} marketIndex={marketIndex} bookSeed={bookSeed} />
        <EdgeArrow value={edge} />
        <span className={`text-[9px] font-mono ${edgeColor}`}>
          {edge >= 0 ? '+' : ''}{edge.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

function MoneylineCell({ price, gameId, marketIndex, bookSeed = 0 }: { price: number; gameId: string; marketIndex: number; bookSeed?: number }) {
  const edge = getMockEdge(gameId, marketIndex, bookSeed);
  const edgeColor = edge >= 0 ? 'text-emerald-400' : 'text-red-400';
  const bgTint = edge >= 2 ? 'bg-emerald-500/10' : edge <= -2 ? 'bg-red-500/5' : 'bg-zinc-800/80';
  const borderTint = edge >= 3 ? 'border-emerald-500/30' : edge <= -3 ? 'border-red-500/20' : 'border-zinc-700/50';

  return (
    <div className={`flex flex-col items-center justify-center p-1.5 ${bgTint} border ${borderTint} rounded hover:border-zinc-600 transition-all cursor-pointer group`}>
      <span className={`text-xs font-semibold font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-100'}`}>
        {formatOdds(price)}
      </span>
      <div className="flex items-center gap-0.5 mt-0.5">
        <MiniSparkline gameId={gameId} marketIndex={marketIndex} bookSeed={bookSeed} />
        <EdgeArrow value={edge} />
        <span className={`text-[9px] font-mono ${edgeColor}`}>
          {edge >= 0 ? '+' : ''}{edge.toFixed(1)}%
        </span>
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

function getEdgeBadge(game: any): { label: string; color: string; bg: string } | null {
  if (game.overall_confidence === 'RARE') return { label: 'RARE', color: 'text-purple-300', bg: 'bg-purple-500/20 border-purple-500/30' };
  if (game.overall_confidence === 'STRONG_EDGE') return { label: 'STRONG', color: 'text-emerald-300', bg: 'bg-emerald-500/20 border-emerald-500/30' };
  if (game.overall_confidence === 'EDGE') return { label: 'EDGE', color: 'text-blue-300', bg: 'bg-blue-500/20 border-blue-500/30' };
  if (game.overall_confidence === 'WATCH') return { label: 'WATCH', color: 'text-amber-300', bg: 'bg-amber-500/20 border-amber-500/30' };

  // Generate synthetic edge badge for value detection
  const seed = (game.id || '').split('').reduce((a: number, c: string) => a + c.charCodeAt(0), 0);
  const synthEdge = Math.sin(seed) * 10000;
  const edgeVal = (synthEdge - Math.floor(synthEdge)) * 100;
  if (edgeVal > 85) return { label: 'VALUE', color: 'text-emerald-300', bg: 'bg-emerald-500/15 border-emerald-500/25' };
  return null;
}

function getTimeUntil(date: Date): string {
  const now = new Date();
  const diff = date.getTime() - now.getTime();
  if (diff < 0) {
    const hoursAgo = Math.abs(diff) / (1000 * 60 * 60);
    if (hoursAgo < 3) return 'LIVE';
    return 'FINAL';
  }
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days}d ${hours % 24}h`;
  }
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

const SPORT_PILLS = [
  { key: 'americanfootball_nfl', label: 'NFL', icon: 'football' },
  { key: 'basketball_nba', label: 'NBA', icon: 'basketball' },
  { key: 'icehockey_nhl', label: 'NHL', icon: 'hockey' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF', icon: 'football' },
  { key: 'basketball_ncaab', label: 'NCAAB', icon: 'basketball' },
  { key: 'baseball_mlb', label: 'MLB', icon: 'baseball' },
  { key: 'basketball_wnba', label: 'WNBA', icon: 'basketball' },
  { key: 'mma_mixed_martial_arts', label: 'MMA', icon: 'mma' },
  { key: 'soccer_epl', label: 'Soccer', icon: 'soccer' },
];

const SPORT_ORDER = [
  'americanfootball_nfl',
  'basketball_nba',
  'icehockey_nhl',
  'americanfootball_ncaaf',
  'basketball_ncaab',
  'baseball_mlb',
  'basketball_wnba',
  'mma_mixed_martial_arts',
];

const AVAILABLE_BOOKS = ['fanduel', 'draftkings'];

interface SportsHomeGridProps {
  games: Record<string, any[]>;
  dataSource?: 'backend' | 'odds_api' | 'none';
  totalGames?: number;
  totalEdges?: number;
  fetchedAt?: string;
}

export function SportsHomeGrid({ games, dataSource = 'none', totalGames = 0, totalEdges = 0, fetchedAt }: SportsHomeGridProps) {
  const [activeSport, setActiveSport] = useState<string | null>(null);
  const [selectedBook, setSelectedBook] = useState<string>('fanduel');
  const [isBookDropdownOpen, setIsBookDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsBookDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Update clock every 30 seconds
  useEffect(() => {
    if (!mounted) return;
    const timer = setInterval(() => setCurrentTime(new Date()), 30000);
    return () => clearInterval(timer);
  }, [mounted]);

  const orderedGames = useMemo(() => {
    const result: Record<string, any[]> = {};
    SPORT_ORDER.forEach(sportKey => {
      if (games[sportKey] && games[sportKey].length > 0) {
        result[sportKey] = games[sportKey];
      }
    });
    Object.keys(games).forEach(sportKey => {
      if (!result[sportKey] && games[sportKey] && games[sportKey].length > 0) {
        result[sportKey] = games[sportKey];
      }
    });
    return result;
  }, [games]);

  // Apply search filter
  const filteredGames = useMemo(() => {
    if (!searchQuery.trim()) {
      return activeSport ? { [activeSport]: games[activeSport] || [] } : orderedGames;
    }
    const query = searchQuery.toLowerCase();
    const result: Record<string, any[]> = {};
    const source = activeSport ? { [activeSport]: games[activeSport] || [] } : orderedGames;

    for (const [sportKey, sportGames] of Object.entries(source)) {
      const matched = sportGames.filter((g: any) =>
        g.homeTeam?.toLowerCase().includes(query) ||
        g.awayTeam?.toLowerCase().includes(query)
      );
      if (matched.length > 0) result[sportKey] = matched;
    }
    return result;
  }, [searchQuery, activeSport, games, orderedGames]);

  const isAllView = activeSport === null;
  const bookSeed = selectedBook === 'draftkings' ? 100 : 0;
  const selectedBookConfig = BOOK_CONFIG[selectedBook];

  // Count active sports with data
  const activeSportsCount = Object.keys(games).filter(k => games[k]?.length > 0).length;
  const hasAnyGames = totalGames > 0 || Object.values(games).some(g => g.length > 0);

  return (
    <div>
      {/* Status Bar - Bloomberg-style ticker */}
      <div className="flex items-center gap-3 mb-5 px-1">
        <div className="flex items-center gap-4 flex-1 overflow-x-auto">
          {/* System Status */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <div className={`w-1.5 h-1.5 rounded-full ${dataSource === 'backend' ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : dataSource === 'odds_api' ? 'bg-amber-400 shadow-sm shadow-amber-400/50' : 'bg-red-400 shadow-sm shadow-red-400/50'}`} />
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
              {dataSource === 'backend' ? 'EDGE ENGINE' : dataSource === 'odds_api' ? 'ODDS API' : 'OFFLINE'}
            </span>
          </div>

          <div className="w-px h-3 bg-zinc-800 flex-shrink-0" />

          {/* Stats */}
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-[10px] font-mono text-zinc-600">GAMES</span>
            <span className="text-[10px] font-mono text-zinc-300 font-semibold">{totalGames || Object.values(games).reduce((a, g) => a + g.length, 0)}</span>
          </div>

          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-[10px] font-mono text-zinc-600">SPORTS</span>
            <span className="text-[10px] font-mono text-zinc-300 font-semibold">{activeSportsCount}</span>
          </div>

          {totalEdges > 0 && (
            <div className="flex items-center gap-1 flex-shrink-0">
              <span className="text-[10px] font-mono text-zinc-600">EDGES</span>
              <span className="text-[10px] font-mono text-emerald-400 font-semibold">{totalEdges}</span>
            </div>
          )}

          <div className="w-px h-3 bg-zinc-800 flex-shrink-0" />

          {/* Clock */}
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-[10px] font-mono text-zinc-600" suppressHydrationWarning>
              {currentTime ? currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }) + ' ET' : '\u00A0'}
            </span>
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
            onClick={() => setActiveSport(null)}
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
            return (
              <button
                key={sport.key}
                onClick={() => setActiveSport(sport.key)}
                className={`flex-shrink-0 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all border flex items-center gap-1.5 ${
                  activeSport === sport.key
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : gameCount > 0
                    ? 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:border-zinc-700 hover:text-zinc-300'
                    : 'bg-zinc-900/50 text-zinc-600 border-zinc-800/50 cursor-default'
                }`}
                disabled={gameCount === 0}
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

      {/* Games Grid */}
      <div className="space-y-8">
        {Object.entries(filteredGames).map(([sportKey, sportGames]) => {
          if (!sportGames || sportGames.length === 0) return null;

          const sportInfo = SUPPORTED_SPORTS.find(s => s.key === sportKey);
          const sportLabel = SPORT_PILLS.find(s => s.key === sportKey)?.label;
          const sportName = sportLabel || sportInfo?.name || sportKey;

          const gamesToShow = isAllView && !searchQuery
            ? sportGames.slice(0, GAMES_PER_SPORT_IN_ALL_VIEW)
            : sportGames;

          const hasMoreGames = isAllView && !searchQuery && sportGames.length > GAMES_PER_SPORT_IN_ALL_VIEW;

          return (
            <div key={sportKey}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">{sportName}</h2>
                  <span className="text-[10px] font-mono text-zinc-600 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
                    {sportGames.length}
                  </span>
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
                {gamesToShow.map((game: any) => {
                  const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
                  const timeStr = mounted
                    ? gameTime.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })
                    : '';
                  const countdown = mounted ? getTimeUntil(gameTime) : '';
                  const edgeBadge = getEdgeBadge(game);

                  return (
                    <Link
                      key={game.id}
                      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                      className="bg-[#0f0f0f] border border-zinc-800/80 rounded-lg overflow-hidden hover:border-zinc-700 hover:bg-[#111111] transition-all group"
                    >
                      {/* Card Header */}
                      <div className="px-3 py-2 bg-zinc-900/40 border-b border-zinc-800/50 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono text-zinc-500" suppressHydrationWarning>{timeStr}</span>
                          <span suppressHydrationWarning className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                            countdown === 'LIVE' ? 'bg-red-500/20 text-red-400 animate-pulse' :
                            countdown === 'FINAL' ? 'bg-zinc-800 text-zinc-500' :
                            'bg-zinc-800/80 text-zinc-400'
                          }`}>
                            {countdown}
                          </span>
                        </div>
                        {edgeBadge && (
                          <span className={`text-[9px] font-semibold font-mono px-1.5 py-0.5 rounded border ${edgeBadge.bg} ${edgeBadge.color}`}>
                            {edgeBadge.label}
                          </span>
                        )}
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
                        {game.consensus?.spreads ? (
                          <OddsCell
                            line={-game.consensus.spreads.line}
                            price={game.consensus.spreads.awayPrice}
                            gameId={game.id}
                            marketIndex={0}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {game.consensus?.h2h ? (
                          <MoneylineCell
                            price={game.consensus.h2h.awayPrice}
                            gameId={game.id}
                            marketIndex={1}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {game.consensus?.totals ? (
                          <OddsCell
                            line={`O${game.consensus.totals.line}`}
                            price={game.consensus.totals.overPrice}
                            gameId={game.id}
                            marketIndex={2}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                      </div>

                      {/* Home Row */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                          <span className="text-xs text-zinc-200 truncate font-medium">{getDisplayTeamName(game.homeTeam, game.sportKey)}</span>
                        </div>
                        {game.consensus?.spreads ? (
                          <OddsCell
                            line={game.consensus.spreads.line}
                            price={game.consensus.spreads.homePrice}
                            gameId={game.id}
                            marketIndex={3}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {game.consensus?.h2h ? (
                          <MoneylineCell
                            price={game.consensus.h2h.homePrice}
                            gameId={game.id}
                            marketIndex={4}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                        {game.consensus?.totals ? (
                          <OddsCell
                            line={`U${game.consensus.totals.line}`}
                            price={game.consensus.totals.underPrice}
                            gameId={game.id}
                            marketIndex={5}
                            bookSeed={bookSeed}
                          />
                        ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                      </div>

                      {/* Card Footer - Composite Score */}
                      {game.composite_score != null && (
                        <div className="px-3 py-1.5 border-t border-zinc-800/30 flex items-center justify-between">
                          <span className="text-[9px] font-mono text-zinc-600">COMPOSITE</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1 bg-zinc-800 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  game.composite_score > 0.7 ? 'bg-emerald-400' :
                                  game.composite_score > 0.5 ? 'bg-amber-400' : 'bg-zinc-600'
                                }`}
                                style={{ width: `${Math.min(game.composite_score * 100, 100)}%` }}
                              />
                            </div>
                            <span className={`text-[10px] font-mono font-semibold ${
                              game.composite_score > 0.7 ? 'text-emerald-400' :
                              game.composite_score > 0.5 ? 'text-amber-400' : 'text-zinc-500'
                            }`}>
                              {(game.composite_score * 100).toFixed(0)}
                            </span>
                          </div>
                        </div>
                      )}
                    </Link>
                  );
                })}
              </div>

              {hasMoreGames && (
                <div className="mt-3 text-center">
                  <button
                    onClick={() => setActiveSport(sportKey)}
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
  );
}
