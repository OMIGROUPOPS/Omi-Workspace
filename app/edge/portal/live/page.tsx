'use client';

import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Link from 'next/link';
import { formatOdds } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getGameState, getEstimatedPeriod } from '@/lib/edge/utils/game-state';

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
};

const AVAILABLE_BOOKS = ['fanduel', 'draftkings'];

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
    return <img src={logo} alt={teamName} className="w-6 h-6 object-contain" onError={() => setImgError(true)} />;
  }

  return (
    <div
      className="w-6 h-6 rounded-full flex items-center justify-center text-[8px] font-bold text-white flex-shrink-0"
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
    <div
      className="rounded flex items-center justify-center font-bold text-white flex-shrink-0"
      style={{ backgroundColor: config.color, width: size, height: size, fontSize: size * 0.4 }}
    >
      {initials}
    </div>
  );
}

function OddsCell({ line, price }: { line?: number | string; price: number }) {
  return (
    <div className="flex flex-col items-center justify-center p-2 bg-[#1a1f2b] border border-zinc-700/50 rounded hover:brightness-110 transition-all cursor-pointer">
      <div className="flex items-center gap-0.5">
        <span className="text-sm font-semibold text-zinc-100 font-mono">
          {line !== undefined && (typeof line === 'number' ? (line > 0 ? `+${line}` : line) : line)}
        </span>
      </div>
      <div className="flex items-center gap-1">
        <span className={`text-xs font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-300'}`}>
          {formatOdds(price)}
        </span>
      </div>
    </div>
  );
}

function MoneylineCell({ price }: { price: number }) {
  return (
    <div className="flex flex-col items-center justify-center p-2 bg-[#1a1f2b] border border-zinc-700/50 rounded hover:brightness-110 transition-all cursor-pointer">
      <span className={`text-sm font-semibold font-mono ${price > 0 ? 'text-emerald-400' : 'text-zinc-100'}`}>
        {formatOdds(price)}
      </span>
    </div>
  );
}

export default function LiveMarketsPage() {
  const [games, setGames] = useState<Record<string, any[]>>({});
  const [selectedBook, setSelectedBook] = useState<string>('fanduel');
  const [isBookDropdownOpen, setIsBookDropdownOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [secondsSinceUpdate, setSecondsSinceUpdate] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/odds/dashboard');
      if (!res.ok) throw new Error('Fetch failed');
      const data = await res.json();
      setGames(data.games || {});
      setLastUpdated(new Date());
      setSecondsSinceUpdate(0);
    } catch (e) {
      console.error('[LiveMarkets] Fetch error:', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    setMounted(true);
    fetchData();
  }, [fetchData]);

  // Auto-refresh every 15 seconds for live games
  useEffect(() => {
    if (!mounted) return;
    const timer = setInterval(fetchData, 15000);
    return () => clearInterval(timer);
  }, [mounted, fetchData]);

  // Update seconds counter
  useEffect(() => {
    if (!mounted) return;
    const timer = setInterval(() => {
      setSecondsSinceUpdate(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [mounted]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsBookDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter for live games only
  const liveGames = useMemo(() => {
    const live: any[] = [];
    for (const [sportKey, sportGames] of Object.entries(games)) {
      for (const game of sportGames) {
        const state = getGameState(game.commenceTime, game.sportKey || sportKey);
        if (state === 'live') {
          live.push({ ...game, sportKey: game.sportKey || sportKey });
        }
      }
    }
    // Sort by commence time (most recent first)
    return live.sort((a, b) => new Date(b.commenceTime).getTime() - new Date(a.commenceTime).getTime());
  }, [games]);

  const selectedBookConfig = BOOK_CONFIG[selectedBook];

  if (isLoading) {
    return (
      <div className="py-4 px-4 max-w-[1600px] mx-auto">
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="mb-6 p-4 bg-gradient-to-r from-red-900/20 to-zinc-900/40 rounded-xl border border-red-800/40">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              <h1 className="text-lg font-semibold text-zinc-100">Live Markets</h1>
              <span className="text-[10px] font-mono text-amber-500 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">TIER 2</span>
            </div>
            <div className="h-4 w-px bg-zinc-800" />
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-800/60 rounded-lg">
              <span className="text-[10px] font-mono text-zinc-500">LIVE</span>
              <span className="text-sm font-mono font-bold text-red-400">{liveGames.length}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 bg-zinc-800/40 rounded-lg" suppressHydrationWarning>
              <span className="text-[10px] font-mono text-zinc-500">
                Updated {secondsSinceUpdate < 60 ? `${secondsSinceUpdate}s` : `${Math.floor(secondsSinceUpdate / 60)}m`} ago
              </span>
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
        </div>
      </div>

      {/* Empty State */}
      {liveGames.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 bg-zinc-900/30 rounded-xl border border-zinc-800/50">
          <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-zinc-300 mb-2">No Live Games</h3>
          <p className="text-sm text-zinc-500 text-center max-w-md">
            No games are currently in progress. Check back when games are live for real-time odds and period tracking.
          </p>
          <Link
            href="/edge/portal/sports"
            className="mt-4 text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            View upcoming games
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      )}

      {/* Live Games Grid */}
      {liveGames.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {liveGames.map((game: any) => {
            const gameTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
            const periodInfo = mounted ? getEstimatedPeriod(gameTime, game.sportKey) : null;
            const bookOdds = game.bookmakers?.[selectedBook];
            const spreads = bookOdds?.spreads || game.consensus?.spreads;
            const h2h = bookOdds?.h2h || game.consensus?.h2h;
            const totals = bookOdds?.totals || game.consensus?.totals;

            return (
              <Link
                key={game.id}
                href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                className="bg-[#0f0f0f] border border-red-500/30 hover:border-red-500/50 rounded-xl overflow-hidden hover:bg-[#111111] transition-all group"
              >
                {/* Card Header */}
                <div className="px-4 py-3 border-b flex items-center justify-between bg-red-500/5 border-red-500/20">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-2 text-sm font-semibold text-red-400 bg-red-500/20 px-3 py-1 rounded-full">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                      </span>
                      {periodInfo || 'LIVE'}
                    </span>
                    {game.scores && (
                      <span className="text-lg font-bold font-mono text-zinc-100 bg-zinc-800/80 px-3 py-1 rounded-lg border border-zinc-700/50">
                        {game.scores.away} - {game.scores.home}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] font-mono text-zinc-600 uppercase">
                    {game.sportKey?.split('_').pop()}
                  </span>
                </div>

                {/* Column Headers */}
                <div className="grid grid-cols-[1fr,70px,70px,70px] gap-2 px-4 py-2 border-b border-zinc-800/30">
                  <span className="text-[10px] text-zinc-600 uppercase font-mono tracking-wider"></span>
                  <span className="text-[10px] text-zinc-600 uppercase text-center font-mono tracking-wider">SPRD</span>
                  <span className="text-[10px] text-zinc-600 uppercase text-center font-mono tracking-wider">ML</span>
                  <span className="text-[10px] text-zinc-600 uppercase text-center font-mono tracking-wider">O/U</span>
                </div>

                {/* Away Row */}
                <div className="grid grid-cols-[1fr,70px,70px,70px] gap-2 px-4 py-2 items-center">
                  <div className="flex items-center gap-3 min-w-0">
                    <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                    <span className="text-sm text-zinc-200 truncate font-medium">{getDisplayTeamName(game.awayTeam, game.sportKey)}</span>
                    {game.scores && (
                      <span className="text-lg font-bold font-mono text-zinc-300 ml-auto">{game.scores.away}</span>
                    )}
                  </div>
                  {spreads?.line !== undefined ? (
                    <OddsCell line={-spreads.line} price={spreads.awayPrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                  {h2h?.awayPrice !== undefined ? (
                    <MoneylineCell price={h2h.awayPrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                  {totals?.line !== undefined ? (
                    <OddsCell line={`O${totals.line}`} price={totals.overPrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                </div>

                {/* Home Row */}
                <div className="grid grid-cols-[1fr,70px,70px,70px] gap-2 px-4 py-2 items-center">
                  <div className="flex items-center gap-3 min-w-0">
                    <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                    <span className="text-sm text-zinc-200 truncate font-medium">{getDisplayTeamName(game.homeTeam, game.sportKey)}</span>
                    {game.scores && (
                      <span className="text-lg font-bold font-mono text-zinc-300 ml-auto">{game.scores.home}</span>
                    )}
                  </div>
                  {spreads?.line !== undefined ? (
                    <OddsCell line={spreads.line} price={spreads.homePrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                  {h2h?.homePrice !== undefined ? (
                    <MoneylineCell price={h2h.homePrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                  {totals?.line !== undefined ? (
                    <OddsCell line={`U${totals.line}`} price={totals.underPrice} />
                  ) : <div className="text-center text-zinc-700 text-[10px] font-mono">--</div>}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
