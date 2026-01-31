'use client';

import { useState, useRef, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { formatOdds, calculateTwoWayEV, formatEV, getEVColor, getEVBgClass } from '@/lib/edge/utils/odds-math';
import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getTimeDisplay, getGameState } from '@/lib/edge/utils/game-state';
import type { CEQResult, GameCEQ, CEQConfidence } from '@/lib/edge/engine/edgescout';
import { LiveEdgeFeed } from './LiveEdgeFeed';

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
};

const GAMES_PER_SPORT_IN_ALL_VIEW = 6;

function getDisplayTeamName(teamName: string, sportKey: string): string {
  if (sportKey.includes('ncaa')) {
    return teamName;
  }
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
  // CEQ thresholds: 50 = neutral, >66 = EDGE, >76 = STRONG, >86 = RARE, <45 = edge other side
  if (ceq >= 76) return { bgTint: 'bg-emerald-500/20', borderTint: 'border-emerald-500/40', textColor: 'text-emerald-400' };
  if (ceq >= 66) return { bgTint: 'bg-emerald-500/15', borderTint: 'border-emerald-500/30', textColor: 'text-emerald-400' };
  if (ceq >= 56) return { bgTint: 'bg-emerald-500/10', borderTint: 'border-emerald-500/20', textColor: 'text-emerald-400' };
  if (ceq <= 35) return { bgTint: 'bg-red-500/15', borderTint: 'border-red-500/30', textColor: 'text-red-400' };
  if (ceq <= 45) return { bgTint: 'bg-red-500/10', borderTint: 'border-red-500/20', textColor: 'text-red-400' };
  return { bgTint: 'bg-zinc-800/80', borderTint: 'border-zinc-700/50', textColor: 'text-zinc-500' };
}

function OddsCell({ line, price, ev, ceq, topDrivers }: { line?: number | string; price: number; ev?: number; ceq?: number; topDrivers?: string[] }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const hasEV = ev !== undefined && Math.abs(ev) >= 0.5;
  const hasCEQ = ceq !== undefined && ceq !== null;

  // Use EV for styling (primary), fall back to CEQ
  const evBg = hasEV ? getEVBgClass(ev) : 'bg-zinc-800/80 border-zinc-700/50';
  const evColor = hasEV ? getEVColor(ev) : 'text-zinc-500';

  const confidence = hasCEQ
    ? ceq >= 86 ? 'RARE' : ceq >= 76 ? 'STRONG' : ceq >= 66 ? 'EDGE' : ceq >= 56 ? 'WATCH' : 'PASS'
    : null;

  return (
    <div
      className={`relative flex flex-col items-center justify-center p-1.5 ${evBg} rounded hover:border-zinc-600 transition-all cursor-pointer group`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="flex items-center gap-0.5">
        <span className="text-xs font-semibold text-zinc-100 font-mono">
          {line !== undefined && (typeof line === 'number' ? (line > 0 ? `+${line}` : line) : line)}
        </span>
      </div>
      <div className="flex items-center gap-1">
        <span className={`text-[11px] font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-300'}`}>
          {formatOdds(price)}
        </span>
        {hasEV && (
          <span className={`text-[9px] font-mono font-medium ${evColor}`}>
            {formatEV(ev)}
          </span>
        )}
      </div>
      {/* Tooltip with CEQ details */}
      {showTooltip && (hasEV || hasCEQ) && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl p-2 text-left">
          {hasEV && (
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-zinc-500 uppercase">EV</span>
              <span className={`text-xs font-bold ${evColor}`}>{formatEV(ev)}</span>
            </div>
          )}
          {hasCEQ && (
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-zinc-500 uppercase">CEQ Score</span>
              <span className={`text-xs font-bold ${getCEQStyles(ceq).textColor}`}>{ceq}%</span>
            </div>
          )}
          {confidence && confidence !== 'PASS' && (
            <div className={`text-[10px] font-medium ${getCEQStyles(ceq).textColor} mb-1`}>{confidence}</div>
          )}
          {topDrivers && topDrivers.length > 0 && (
            <div className="border-t border-zinc-800 pt-1 mt-1">
              <div className="text-[9px] text-zinc-500 mb-0.5">Top Drivers:</div>
              {topDrivers.slice(0, 3).map((driver, i) => (
                <div key={i} className="text-[9px] text-zinc-400 truncate">{driver}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MoneylineCell({ price, ev, ceq, topDrivers }: { price: number; ev?: number; ceq?: number; topDrivers?: string[] }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const hasEV = ev !== undefined && Math.abs(ev) >= 0.5;
  const hasCEQ = ceq !== undefined && ceq !== null;

  // Use EV for styling (primary), fall back to CEQ
  const evBg = hasEV ? getEVBgClass(ev) : 'bg-zinc-800/80 border-zinc-700/50';
  const evColor = hasEV ? getEVColor(ev) : 'text-zinc-500';

  const confidence = hasCEQ
    ? ceq >= 86 ? 'RARE' : ceq >= 76 ? 'STRONG' : ceq >= 66 ? 'EDGE' : ceq >= 56 ? 'WATCH' : 'PASS'
    : null;

  return (
    <div
      className={`relative flex flex-col items-center justify-center p-1.5 ${evBg} rounded hover:border-zinc-600 transition-all cursor-pointer group`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="flex items-center gap-1">
        <span className={`text-xs font-semibold font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-100'}`}>
          {formatOdds(price)}
        </span>
        {hasEV && (
          <span className={`text-[9px] font-mono font-medium ${evColor}`}>
            {formatEV(ev)}
          </span>
        )}
      </div>
      {/* Tooltip with EV and CEQ details */}
      {showTooltip && (hasEV || hasCEQ) && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl p-2 text-left">
          {hasEV && (
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-zinc-500 uppercase">EV</span>
              <span className={`text-xs font-bold ${evColor}`}>{formatEV(ev)}</span>
            </div>
          )}
          {hasCEQ && (
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-zinc-500 uppercase">CEQ Score</span>
              <span className={`text-xs font-bold ${getCEQStyles(ceq).textColor}`}>{ceq}%</span>
            </div>
          )}
          {confidence && confidence !== 'PASS' && (
            <div className={`text-[10px] font-medium ${getCEQStyles(ceq).textColor} mb-1`}>{confidence}</div>
          )}
          {topDrivers && topDrivers.length > 0 && (
            <div className="border-t border-zinc-800 pt-1 mt-1">
              <div className="text-[9px] text-zinc-500 mb-0.5">Top Drivers:</div>
              {topDrivers.slice(0, 3).map((driver, i) => (
                <div key={i} className="text-[9px] text-zinc-400 truncate">{driver}</div>
              ))}
            </div>
          )}
        </div>
      )}
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

function getEdgeBadge(game: any): { label: string; color: string; bg: string; score?: number; context?: string } | null {
  // Dashboard cards should be clean - no edge badges
  // Users click through to game detail page to see CEQ analysis
  return null;
}

// Using shared getTimeDisplay from game-state.ts for consistent game state detection

const SPORT_PILLS = [
  { key: 'americanfootball_nfl', label: 'NFL', icon: 'football' },
  { key: 'basketball_nba', label: 'NBA', icon: 'basketball' },
  { key: 'icehockey_nhl', label: 'NHL', icon: 'hockey' },
  { key: 'americanfootball_ncaaf', label: 'NCAAF', icon: 'football' },
  { key: 'basketball_ncaab', label: 'NCAAB', icon: 'basketball' },
  { key: 'baseball_mlb', label: 'MLB', icon: 'baseball' },
  { key: 'basketball_wnba', label: 'WNBA', icon: 'basketball' },
  { key: 'mma_mixed_martial_arts', label: 'MMA', icon: 'mma' },
  { key: 'tennis_atp_australian_open', label: 'AUS Open', icon: 'tennis' },
  { key: 'tennis_atp_french_open', label: 'FR Open', icon: 'tennis' },
  { key: 'tennis_atp_us_open', label: 'US Open', icon: 'tennis' },
  { key: 'tennis_atp_wimbledon', label: 'Wimbledon', icon: 'tennis' },
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
  'tennis_atp_australian_open',
  'tennis_atp_french_open',
  'tennis_atp_us_open',
  'tennis_atp_wimbledon',
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
  const [liveEdgeCount, setLiveEdgeCount] = useState(0);
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
  const selectedBookConfig = BOOK_CONFIG[selectedBook];

  // Count active sports with data
  const activeSportsCount = Object.keys(games).filter(k => games[k]?.length > 0).length;
  const hasAnyGames = totalGames > 0 || Object.values(games).some(g => g.length > 0);

  return (
    <div>
      {/* Premium Status Bar */}
      <div className="mb-6 p-4 bg-gradient-to-r from-zinc-900/80 to-zinc-900/40 rounded-xl border border-zinc-800/60">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Left: System Status */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${dataSource !== 'none' ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50 animate-pulse' : 'bg-red-400 shadow-lg shadow-red-400/50'}`} />
              <span className={`text-xs font-semibold ${dataSource !== 'none' ? 'text-emerald-400' : 'text-red-400'}`}>
                {dataSource !== 'none' ? 'LIVE FEED' : 'OFFLINE'}
              </span>
            </div>

            <div className="h-4 w-px bg-zinc-800" />

            {/* Stats Badges */}
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

              {liveEdgeCount > 0 && (
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                  </span>
                  <span className="text-[10px] font-mono text-blue-500">LIVE</span>
                  <span className="text-xs font-mono font-bold text-blue-400">{liveEdgeCount}</span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Clock */}
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

      {/* Main Content with Sidebar */}
      <div className="flex gap-6">
        {/* Games Grid */}
        <div className="flex-1 space-y-8">
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
                  const countdown = mounted ? getTimeDisplay(gameTime, game.sportKey) : '';
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
                          {/* Live Score Display - Show prominently */}
                          {(countdown === 'LIVE' || countdown === 'FINAL') && game.scores && (
                            <span className="text-sm font-bold font-mono text-zinc-100 bg-zinc-800/80 px-2 py-0.5 rounded border border-zinc-700/50">
                              {game.scores.away} - {game.scores.home}
                            </span>
                          )}
                        </div>
                        {edgeBadge && (
                          <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border ${edgeBadge.bg} ${edgeBadge.color}`}>
                            <span className="text-[9px] font-bold">
                              {edgeBadge.label === 'RARE' && '★ '}{edgeBadge.label}:
                            </span>
                            {edgeBadge.context && (
                              <span className="text-[9px] font-medium">{edgeBadge.context}</span>
                            )}
                            {edgeBadge.score && (
                              <span className="text-[9px] font-mono opacity-80">({edgeBadge.score}%)</span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Column Headers */}
                      <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1 border-b border-zinc-800/30">
                        <span className="text-[9px] text-zinc-600 uppercase font-mono tracking-wider"></span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">SPRD</span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">ML</span>
                        <span className="text-[9px] text-zinc-600 uppercase text-center font-mono tracking-wider">O/U</span>
                      </div>

                      {/* Away Row - Use selected book's odds or fall back to consensus */}
                      {(() => {
                        const bookOdds = game.bookmakers?.[selectedBook];
                        const spreads = bookOdds?.spreads || game.consensus?.spreads;
                        const h2h = bookOdds?.h2h || game.consensus?.h2h;
                        const totals = bookOdds?.totals || game.consensus?.totals;
                        // Extract CEQ data for away side
                        const ceq = game.ceq as GameCEQ | undefined;
                        const awaySpreadsData = ceq?.spreads?.away;
                        const awayH2hData = ceq?.h2h?.away;
                        const overTotalsData = ceq?.totals?.over;

                        // Calculate EV for each market using consensus as fair value
                        const consensus = game.consensus;
                        const spreadEV = spreads?.awayPrice && spreads?.homePrice
                          ? calculateTwoWayEV(
                              spreads.awayPrice,
                              spreads.homePrice,
                              consensus?.spreads?.awayPrice,
                              consensus?.spreads?.homePrice
                            )
                          : undefined;
                        const mlEV = h2h?.awayPrice && h2h?.homePrice
                          ? calculateTwoWayEV(
                              h2h.awayPrice,
                              h2h.homePrice,
                              consensus?.h2h?.awayPrice,
                              consensus?.h2h?.homePrice
                            )
                          : undefined;
                        const overEV = totals?.overPrice && totals?.underPrice
                          ? calculateTwoWayEV(
                              totals.overPrice,
                              totals.underPrice,
                              consensus?.totals?.overPrice,
                              consensus?.totals?.underPrice
                            )
                          : undefined;

                        return (
                          <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 items-center">
                            <div className="flex items-center gap-2 min-w-0">
                              <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                              <span className="text-xs text-zinc-200 truncate font-medium">{getDisplayTeamName(game.awayTeam, game.sportKey)}</span>
                            </div>
                            {spreads?.line !== undefined ? (
                              <OddsCell
                                line={-spreads.line}
                                price={spreads.awayPrice}
                                ev={spreadEV}
                                ceq={awaySpreadsData?.ceq}
                                topDrivers={awaySpreadsData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                            {h2h?.awayPrice !== undefined ? (
                              <MoneylineCell
                                price={h2h.awayPrice}
                                ev={mlEV}
                                ceq={awayH2hData?.ceq}
                                topDrivers={awayH2hData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                            {totals?.line !== undefined ? (
                              <OddsCell
                                line={`O${totals.line}`}
                                price={totals.overPrice}
                                ev={overEV}
                                ceq={overTotalsData?.ceq}
                                topDrivers={overTotalsData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                          </div>
                        );
                      })()}

                      {/* Home Row - Use selected book's odds or fall back to consensus */}
                      {(() => {
                        const bookOdds = game.bookmakers?.[selectedBook];
                        const spreads = bookOdds?.spreads || game.consensus?.spreads;
                        const h2h = bookOdds?.h2h || game.consensus?.h2h;
                        const totals = bookOdds?.totals || game.consensus?.totals;
                        // Extract CEQ data for home side
                        const ceq = game.ceq as GameCEQ | undefined;
                        const homeSpreadsData = ceq?.spreads?.home;
                        const homeH2hData = ceq?.h2h?.home;
                        const underTotalsData = ceq?.totals?.under;

                        // Calculate EV for each market using consensus as fair value
                        const consensus = game.consensus;
                        const spreadEV = spreads?.homePrice && spreads?.awayPrice
                          ? calculateTwoWayEV(
                              spreads.homePrice,
                              spreads.awayPrice,
                              consensus?.spreads?.homePrice,
                              consensus?.spreads?.awayPrice
                            )
                          : undefined;
                        const mlEV = h2h?.homePrice && h2h?.awayPrice
                          ? calculateTwoWayEV(
                              h2h.homePrice,
                              h2h.awayPrice,
                              consensus?.h2h?.homePrice,
                              consensus?.h2h?.awayPrice
                            )
                          : undefined;
                        const underEV = totals?.underPrice && totals?.overPrice
                          ? calculateTwoWayEV(
                              totals.underPrice,
                              totals.overPrice,
                              consensus?.totals?.underPrice,
                              consensus?.totals?.overPrice
                            )
                          : undefined;

                        return (
                          <div className="grid grid-cols-[1fr,65px,65px,65px] gap-1.5 px-3 py-1.5 items-center">
                            <div className="flex items-center gap-2 min-w-0">
                              <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                              <span className="text-xs text-zinc-200 truncate font-medium">{getDisplayTeamName(game.homeTeam, game.sportKey)}</span>
                            </div>
                            {spreads?.line !== undefined ? (
                              <OddsCell
                                line={spreads.line}
                                price={spreads.homePrice}
                                ev={spreadEV}
                                ceq={homeSpreadsData?.ceq}
                                topDrivers={homeSpreadsData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                            {h2h?.homePrice !== undefined ? (
                              <MoneylineCell
                                price={h2h.homePrice}
                                ev={mlEV}
                                ceq={homeH2hData?.ceq}
                                topDrivers={homeH2hData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                            {totals?.line !== undefined ? (
                              <OddsCell
                                line={`U${totals.line}`}
                                price={totals.underPrice}
                                ev={underEV}
                                ceq={underTotalsData?.ceq}
                                topDrivers={underTotalsData?.topDrivers}
                              />
                            ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                          </div>
                        );
                      })()}

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

        {/* Live Edge Feed Sidebar - Hidden on mobile, shown on lg+ screens */}
        <div className="hidden lg:block w-80 flex-shrink-0">
          <div className="sticky top-4 h-[calc(100vh-8rem)] bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
            <LiveEdgeFeed
              sport={activeSport || undefined}
              maxEdges={15}
              showFilters={true}
              autoRefresh={true}
              onEdgeCount={setLiveEdgeCount}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
