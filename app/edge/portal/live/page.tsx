'use client';

import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Link from 'next/link';
import { formatOdds } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getGameState, getEstimatedPeriod } from '@/lib/edge/utils/game-state';

// Light theme palette (matches SportsHomeGrid)
const P = {
  pageBg: '#ebedf0',
  cardBg: '#ffffff',
  cardBorder: '#e2e4e8',
  headerBar: '#f4f5f7',
  textPrimary: '#1f2937',
  textSecondary: '#6b7280',
  textMuted: '#9ca3af',
  textFaint: '#b0b5bd',
  greenText: '#16a34a',
  greenBg: 'rgba(34,197,94,0.06)',
  greenBorder: 'rgba(34,197,94,0.35)',
  neutralBg: '#f7f8f9',
  neutralBorder: '#ecedef',
};

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

function fmtSpread(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

function fmtOdds(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
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

  // Auto-refresh every 10 seconds for live games
  useEffect(() => {
    if (!mounted) return;
    const timer = setInterval(fetchData, 10000);
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

  // Filter for live games only — use gameState from dashboard API
  const liveGames = useMemo(() => {
    const live: any[] = [];
    for (const [sportKey, sportGames] of Object.entries(games)) {
      for (const game of sportGames) {
        if (game.gameState === 'live') {
          live.push({ ...game, sportKey: game.sportKey || sportKey });
        }
      }
    }
    return live.sort((a, b) => new Date(b.commenceTime).getTime() - new Date(a.commenceTime).getTime());
  }, [games]);

  const selectedBookConfig = BOOK_CONFIG[selectedBook];
  const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";

  if (isLoading) {
    return (
      <div style={{ padding: '16px 16px 32px', fontFamily: FONT }}>
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
            <span style={{ fontSize: 11, color: P.textMuted, fontFamily: 'monospace', textTransform: 'uppercase', letterSpacing: 1 }}>Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: P.pageBg, minHeight: '100vh', fontFamily: FONT, padding: '16px 16px 32px' }}>

      {/* Status Bar */}
      <div style={{
        marginBottom: 20, padding: '12px 16px', background: P.cardBg,
        borderRadius: 12, border: `1px solid ${P.cardBorder}`,
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span style={{ fontSize: 13, fontWeight: 700, color: P.textPrimary }}>Live Markets</span>
              <span style={{
                fontSize: 9, fontFamily: 'monospace', fontWeight: 600,
                color: '#16a34a', background: P.greenBg, border: `1px solid ${P.greenBorder}`,
                padding: '2px 6px', borderRadius: 4, letterSpacing: 1,
              }}>TIER 2</span>
            </div>
            <div style={{ width: 1, height: 16, background: P.cardBorder }} />
            <div style={{ background: P.neutralBg, borderRadius: 6, padding: '3px 8px', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ fontSize: 9, fontWeight: 600, color: P.textFaint, letterSpacing: 1 }}>LIVE</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: P.greenText, fontFamily: 'monospace' }}>{liveGames.length}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2" style={{ padding: '3px 8px', background: P.neutralBg, borderRadius: 6 }} suppressHydrationWarning>
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
              </span>
              <span style={{ fontSize: 10, color: P.textMuted, fontFamily: 'monospace' }}>
                <span style={{ color: '#16a34a', marginRight: 4 }}>LIVE 10s</span>
                Updated {secondsSinceUpdate < 60 ? `${secondsSinceUpdate}s` : `${Math.floor(secondsSinceUpdate / 60)}m`} ago
                {lastUpdated && <span style={{ color: P.textFaint, marginLeft: 4 }}>({lastUpdated.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })})</span>}
              </span>
            </div>

            {/* Book Dropdown */}
            <div className="relative flex-shrink-0" ref={dropdownRef}>
              <button
                onClick={() => setIsBookDropdownOpen(!isBookDropdownOpen)}
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
                        className="w-full flex items-center gap-2.5"
                        style={{
                          padding: '8px 12px', textAlign: 'left', cursor: 'pointer', border: 'none',
                          background: isSelected ? P.neutralBg : 'transparent', color: P.textPrimary,
                        }}
                      >
                        <BookIcon bookKey={book} size={22} />
                        <span style={{ fontSize: 13, fontWeight: 500, flex: 1 }}>{config?.name}</span>
                        {isSelected && (
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
        </div>
      </div>

      {/* Empty State */}
      {liveGames.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20" style={{
          background: P.cardBg, borderRadius: 12, border: `1px solid ${P.cardBorder}`,
        }}>
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4" style={{
            background: P.neutralBg, border: `1px solid ${P.cardBorder}`,
          }}>
            <svg className="w-8 h-8" style={{ color: P.textFaint }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: P.textPrimary, marginBottom: 8 }}>No Live Games</h3>
          <p style={{ fontSize: 13, color: P.textSecondary, textAlign: 'center', maxWidth: 400 }}>
            No games are currently in progress. Check back when games are live for real-time odds and period tracking.
          </p>
          <Link
            href="/edge/portal/sports"
            className="flex items-center gap-1"
            style={{ marginTop: 16, fontSize: 12, color: P.greenText, textDecoration: 'none' }}
          >
            View upcoming games
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            const bookOdds = game.bookmakers?.[selectedBook];
            const spreads = bookOdds?.spreads || game.consensus?.spreads;
            const h2h = bookOdds?.h2h || game.consensus?.h2h;
            const totals = bookOdds?.totals || game.consensus?.totals;
            const displayAway = getDisplayTeamName(game.awayTeam, game.sportKey);
            const displayHome = getDisplayTeamName(game.homeTeam, game.sportKey);
            const liveData = game.liveData;
            const fair = game.fairLines;

            return (
              <Link
                key={game.id}
                href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
                className="block group"
                style={{
                  background: P.cardBg,
                  border: `2px solid ${P.greenText}`,
                  borderRadius: 12,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                  overflow: 'hidden',
                  textDecoration: 'none',
                  transition: 'all 0.15s',
                }}
              >
                {/* Card Header */}
                <div style={{
                  background: P.headerBar, padding: '6px 12px',
                  borderBottom: `1px solid ${P.cardBorder}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}>
                  <span className="flex items-center gap-1.5" style={{ fontSize: 10, fontWeight: 700, color: P.greenText }}>
                    <span className="relative flex h-1.5 w-1.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                    </span>
                    LIVE
                    {liveData?.statusDetail && liveData.statusDetail !== 'Score unavailable' && (
                      <span style={{ fontWeight: 500, color: P.textSecondary, marginLeft: 2, fontSize: 9 }}>
                        {liveData.statusDetail}
                      </span>
                    )}
                  </span>
                  <span style={{ fontSize: 10, color: P.textFaint, fontFamily: 'monospace', textTransform: 'uppercase' }}>
                    {game.sportKey?.split('_').pop()}
                  </span>
                </div>

                {/* Team Rows */}
                <div style={{ padding: '8px 12px' }}>
                  {/* Away */}
                  <div className="flex items-center gap-2" style={{ marginBottom: 4 }}>
                    <TeamLogo teamName={game.awayTeam} sportKey={game.sportKey} />
                    <span style={{ fontSize: 13, fontWeight: 600, color: P.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {displayAway}
                    </span>
                    {liveData?.awayScore != null && (
                      <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>{liveData.awayScore}</span>
                    )}
                  </div>
                  {/* Home */}
                  <div className="flex items-center gap-2">
                    <TeamLogo teamName={game.homeTeam} sportKey={game.sportKey} />
                    <span style={{ fontSize: 13, fontWeight: 600, color: P.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {displayHome}
                    </span>
                    {liveData?.homeScore != null && (
                      <span style={{ fontSize: 16, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>{liveData.homeScore}</span>
                    )}
                  </div>
                </div>

                {/* Covering indicator */}
                {liveData && liveData.homeScore != null && fair?.fair_spread != null && (
                  <div style={{
                    padding: '5px 12px', borderTop: `1px solid ${P.cardBorder}`,
                    display: 'flex', alignItems: 'center', gap: 6,
                    background: P.neutralBg, fontFamily: 'monospace', fontSize: 10,
                  }}>
                    {(() => {
                      const margin = liveData.homeScore - liveData.awayScore;
                      const atsMargin = margin + fair.fair_spread;
                      const scoreStr = `${liveData.awayScore}-${liveData.homeScore}`;
                      const isPush = atsMargin === 0;
                      const isCovering = atsMargin > 0;
                      let statusLabel: string;
                      let statusColor: string;
                      if (isPush) {
                        statusLabel = '— Push';
                        statusColor = P.textMuted;
                      } else {
                        statusLabel = isCovering ? '✓ Covering' : '✗ Not Covering';
                        statusColor = isCovering ? P.greenText : '#b91c1c';
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

                {/* Market Grid — 3-col: Spread | Total | ML */}
                <div style={{ borderTop: `1px solid ${P.cardBorder}` }}>
                  {/* Headers */}
                  <div className="grid grid-cols-3" style={{ borderBottom: `1px solid ${P.cardBorder}` }}>
                    {['SPREAD', 'TOTAL', 'ML'].map((h, i) => (
                      <div key={i} style={{
                        padding: '3px 8px', fontSize: 9, fontWeight: 700, color: P.textFaint,
                        textAlign: 'center', letterSpacing: 1,
                        borderRight: i < 2 ? `1px solid ${P.cardBorder}` : undefined,
                      }}>
                        {h}
                      </div>
                    ))}
                  </div>

                  {/* Away Row */}
                  <div className="grid grid-cols-3" style={{ borderBottom: `1px solid ${P.cardBorder}` }}>
                    <div style={{ padding: '6px 8px', borderRight: `1px solid ${P.neutralBorder}`, background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {spreads?.line !== undefined ? fmtSpread(-spreads.line) : '--'}
                      </span>
                      {spreads?.awayPrice != null && (
                        <span style={{ fontSize: 10, color: P.textSecondary, fontFamily: 'monospace', marginLeft: 4 }}>
                          ({fmtOdds(spreads.awayPrice)})
                        </span>
                      )}
                    </div>
                    <div style={{ padding: '6px 8px', borderRight: `1px solid ${P.neutralBorder}`, background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {totals?.line !== undefined ? `O ${totals.line}` : '--'}
                      </span>
                      {totals?.overPrice != null && (
                        <span style={{ fontSize: 10, color: P.textSecondary, fontFamily: 'monospace', marginLeft: 4 }}>
                          ({fmtOdds(totals.overPrice)})
                        </span>
                      )}
                    </div>
                    <div style={{ padding: '6px 8px', background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {h2h?.awayPrice != null ? fmtOdds(h2h.awayPrice) : '--'}
                      </span>
                    </div>
                  </div>

                  {/* Home Row */}
                  <div className="grid grid-cols-3">
                    <div style={{ padding: '6px 8px', borderRight: `1px solid ${P.neutralBorder}`, background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {spreads?.line !== undefined ? fmtSpread(spreads.line) : '--'}
                      </span>
                      {spreads?.homePrice != null && (
                        <span style={{ fontSize: 10, color: P.textSecondary, fontFamily: 'monospace', marginLeft: 4 }}>
                          ({fmtOdds(spreads.homePrice)})
                        </span>
                      )}
                    </div>
                    <div style={{ padding: '6px 8px', borderRight: `1px solid ${P.neutralBorder}`, background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {totals?.line !== undefined ? `U ${totals.line}` : '--'}
                      </span>
                      {totals?.underPrice != null && (
                        <span style={{ fontSize: 10, color: P.textSecondary, fontFamily: 'monospace', marginLeft: 4 }}>
                          ({fmtOdds(totals.underPrice)})
                        </span>
                      )}
                    </div>
                    <div style={{ padding: '6px 8px', background: P.neutralBg }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: P.textPrimary, fontFamily: 'monospace' }}>
                        {h2h?.homePrice != null ? fmtOdds(h2h.homePrice) : '--'}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
