import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import Link from 'next/link';
import { GameDetailClient } from '@/components/edge/GameDetailClient';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function getSupabase() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
      },
    }
  );
}

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ sport?: string }>;
}

async function fetchLineHistory(gameId: string, market: string = 'spread', period: string = 'full', book?: string) {
  try {
    let url = `${BACKEND_URL}/api/lines/${gameId}?market=${market}&period=${period}`;
    if (book) url += `&book=${book}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.snapshots || [];
  } catch (e) {
    console.error('[GameDetail] Line history fetch error:', e);
    return [];
  }
}

async function fetchAllGamesForSport(sport: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/edges/${sport}`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.games || [];
  } catch (e) {
    console.error('[GameDetail] Sport games fetch error:', e);
    return [];
  }
}

async function fetchProps(sport: string, gameId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/props/${sport}/${gameId}`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.props || [];
  } catch (e) {
    console.error('[GameDetail] Props fetch error:', e);
    return [];
  }
}

async function fetchConsensus(sport: string, gameId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/consensus/${sport}/${gameId}`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('[GameDetail] Consensus fetch error:', e);
    return null;
  }
}

async function fetchPerBookOdds(sport: string, gameId: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/odds/${sport}/${gameId}`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('[GameDetail] Per-book odds fetch error:', e);
    return null;
  }
}

async function fetchGameFromCache(gameId: string) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('sport_key, game_data')
      .eq('game_id', gameId)
      .single();

    if (error || !data) return null;
    return data;
  } catch (e) {
    console.error('[GameDetail] Cache fetch error:', e);
    return null;
  }
}

function buildConsensusFromBookmakers(game: any) {
  const bookmakers = game.bookmakers;
  if (!bookmakers || bookmakers.length === 0) return {};

  const h2h: { home: number[]; away: number[] } = { home: [], away: [] };
  const spreads: { homeLine: number[]; homeOdds: number[]; awayLine: number[]; awayOdds: number[] } = { homeLine: [], homeOdds: [], awayLine: [], awayOdds: [] };
  const totals: { line: number[]; overOdds: number[]; underOdds: number[] } = { line: [], overOdds: [], underOdds: [] };

  for (const bk of bookmakers) {
    for (const market of bk.markets) {
      if (market.key === 'h2h') {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        if (home) h2h.home.push(home.price);
        if (away) h2h.away.push(away.price);
      }
      if (market.key === 'spreads') {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        if (home?.point !== undefined) {
          spreads.homeLine.push(home.point);
          spreads.homeOdds.push(home.price);
        }
        if (away?.point !== undefined) {
          spreads.awayLine.push(away.point);
          spreads.awayOdds.push(away.price);
        }
      }
      if (market.key === 'totals') {
        const over = market.outcomes.find((o: any) => o.name === 'Over');
        const under = market.outcomes.find((o: any) => o.name === 'Under');
        if (over?.point !== undefined) {
          totals.line.push(over.point);
          totals.overOdds.push(over.price);
        }
        if (under) totals.underOdds.push(under.price);
      }
    }
  }

  const median = (arr: number[]) => {
    if (arr.length === 0) return undefined;
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
  };

  const consensus: any = {};

  if (h2h.home.length > 0) {
    consensus.h2h = { home: median(h2h.home), away: median(h2h.away) };
  }
  if (spreads.homeLine.length > 0) {
    consensus.spreads = {
      home: { line: median(spreads.homeLine), odds: median(spreads.homeOdds) },
      away: { line: median(spreads.awayLine), odds: median(spreads.awayOdds) },
    };
  }
  if (totals.line.length > 0) {
    consensus.totals = {
      over: { line: median(totals.line), odds: median(totals.overOdds) },
      under: { odds: median(totals.underOdds) },
    };
  }

  return consensus;
}

// Generate deterministic mock edge based on game ID
function generateMockEdge(id: string, offset: number = 0): number {
  const seed = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + offset;
  const x = Math.sin(seed) * 10000;
  return (x - Math.floor(x) - 0.5) * 0.08;
}

export default async function GameDetailPage({ params, searchParams }: PageProps) {
  const { id: gameId } = await params;
  const { sport: querySport } = await searchParams;

  let gameData: any = null;
  let sportKey: string = querySport || '';
  let backendSportKey: string = '';

  const sportMap: Record<string, string> = {
    'americanfootball_nfl': 'NFL',
    'basketball_nba': 'NBA',
    'icehockey_nhl': 'NHL',
    'americanfootball_ncaaf': 'NCAAF',
    'basketball_ncaab': 'NCAAB',
  };

  if (querySport) {
    backendSportKey = sportMap[querySport] || querySport.toUpperCase();
    const allGames = await fetchAllGamesForSport(backendSportKey);
    gameData = allGames.find((g: any) => g.game_id === gameId);
    if (gameData) {
      sportKey = querySport;
    }
  }

  if (!gameData) {
    const sportsToSearch = ['NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB'];
    const reverseMap: Record<string, string> = {
      'NFL': 'americanfootball_nfl',
      'NBA': 'basketball_nba',
      'NHL': 'icehockey_nhl',
      'NCAAF': 'americanfootball_ncaaf',
      'NCAAB': 'basketball_ncaab',
    };
    
    for (const sport of sportsToSearch) {
      const allGames = await fetchAllGamesForSport(sport);
      const found = allGames.find((g: any) => g.game_id === gameId);
      if (found) {
        gameData = found;
        sportKey = reverseMap[sport] || sport.toLowerCase();
        backendSportKey = sport;
        break;
      }
    }
  }

  // Fallback: read from cached_odds table
  if (!gameData) {
    const cached = await fetchGameFromCache(gameId);
    if (cached) {
      const raw = cached.game_data;
      gameData = {
        game_id: raw.id,
        home_team: raw.home_team,
        away_team: raw.away_team,
        commence_time: raw.commence_time,
        consensus_odds: buildConsensusFromBookmakers(raw),
      };
      sportKey = cached.sport_key;
      backendSportKey = sportMap[cached.sport_key] || cached.sport_key.toUpperCase();
    }
  }

  if (!gameData) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Game not found</h1>
          <p className="text-zinc-500 mb-4 text-sm">ID: {gameId}</p>
          <p className="text-zinc-600 text-xs mb-4">Make sure the backend is running and data has been fetched.</p>
          <Link href="/edge/portal/sports" className="text-emerald-400 hover:underline">
            Back to sports
          </Link>
        </div>
      </div>
    );
  }

  // Fetch per-book odds data
  const perBookOdds = await fetchPerBookOdds(backendSportKey, gameId);
  
  // Fetch props
  const propsData = await fetchProps(backendSportKey, gameId);
  
  // Fetch consensus data as fallback
  const consensusData = await fetchConsensus(backendSportKey, gameId);

  // Fetch line history for all periods
  const [
    spreadHistory, mlHistory, totalHistory,
    spreadH1History, totalH1History,
    spreadH2History, totalH2History
  ] = await Promise.all([
    fetchLineHistory(gameId, 'spread', 'full'),
    fetchLineHistory(gameId, 'moneyline', 'full'),
    fetchLineHistory(gameId, 'total', 'full'),
    fetchLineHistory(gameId, 'spread', 'h1'),
    fetchLineHistory(gameId, 'total', 'h1'),
    fetchLineHistory(gameId, 'spread', 'h2'),
    fetchLineHistory(gameId, 'total', 'h2'),
  ]);

  const homeTeam = gameData.home_team;
  const awayTeam = gameData.away_team;
  const commenceTime = gameData.commence_time;
  const compositeScore = gameData.composite_score || 0.5;
  const confidence = gameData.overall_confidence || 'PASS';

  // Build line history object
  const lineHistory = {
    full: { spread: spreadHistory, moneyline: mlHistory, total: totalHistory },
    h1: { spread: spreadH1History, total: totalH1History },
    h2: { spread: spreadH2History, total: totalH2History },
  };

  // Use per-book odds if available, otherwise fall back to consensus
  let bookmakers: Record<string, any> = {};
  let availableBooks: string[] = [];

  if (perBookOdds && perBookOdds.bookmakers) {
    // Use real per-book data
    bookmakers = perBookOdds.bookmakers;
    availableBooks = perBookOdds.books || Object.keys(bookmakers);
    
    // Add line history and props to each book's marketGroups
    Object.keys(bookmakers).forEach(book => {
      if (bookmakers[book].marketGroups) {
        bookmakers[book].marketGroups.lineHistory = lineHistory;
        // Props are already filtered by book in the backend
        if (!bookmakers[book].marketGroups.playerProps || bookmakers[book].marketGroups.playerProps.length === 0) {
          bookmakers[book].marketGroups.playerProps = propsData.filter((p: any) => p.book === book);
        }
      }
    });
  } else {
    // Fallback to consensus data
    const consensus = gameData.consensus_odds || consensusData?.consensus || {};
    const edges = gameData.edges || {};
    
    const buildMarket = (marketData: any, prefix: string) => {
      if (!marketData) return { h2h: null, spreads: null, totals: null };
      
      const result: any = { h2h: null, spreads: null, totals: null };
      
      if (marketData.spreads?.home) {
        result.spreads = {
          home: { 
            line: marketData.spreads.home.line, 
            price: marketData.spreads.home.odds,
            edge: edges[`${prefix}spread_home`]?.edge_pct || generateMockEdge(gameId, prefix.length + 3)
          },
          away: { 
            line: marketData.spreads.away?.line, 
            price: marketData.spreads.away?.odds,
            edge: edges[`${prefix}spread_away`]?.edge_pct || generateMockEdge(gameId, prefix.length + 4)
          },
        };
      }

      if (marketData.h2h?.home !== undefined) {
        result.h2h = {
          home: { 
            price: marketData.h2h.home,
            edge: edges[`${prefix}ml_home`]?.edge_pct || generateMockEdge(gameId, prefix.length + 1)
          },
          away: { 
            price: marketData.h2h.away,
            edge: edges[`${prefix}ml_away`]?.edge_pct || generateMockEdge(gameId, prefix.length + 2)
          },
        };
      }

      if (marketData.totals?.over) {
        result.totals = {
          line: marketData.totals.over.line,
          over: { 
            price: marketData.totals.over.odds,
            edge: edges[`${prefix}total_over`]?.edge_pct || generateMockEdge(gameId, prefix.length + 5)
          },
          under: { 
            price: marketData.totals.under?.odds,
            edge: edges[`${prefix}total_under`]?.edge_pct || generateMockEdge(gameId, prefix.length + 6)
          },
        };
      }
      
      return result;
    };
    
    const marketGroups: any = {
      fullGame: buildMarket(consensus, ''),
      firstHalf: buildMarket(consensus.first_half, 'h1_'),
      secondHalf: buildMarket(consensus.second_half, 'h2_'),
      q1: buildMarket(consensus.quarters?.q1, 'q1_'),
      q2: buildMarket(consensus.quarters?.q2, 'q2_'),
      q3: buildMarket(consensus.quarters?.q3, 'q3_'),
      q4: buildMarket(consensus.quarters?.q4, 'q4_'),
      p1: buildMarket(consensus.periods?.p1, 'p1_'),
      p2: buildMarket(consensus.periods?.p2, 'p2_'),
      p3: buildMarket(consensus.periods?.p3, 'p3_'),
      teamTotals: null,
      playerProps: propsData,
      alternates: { spreads: [], totals: [] },
      lineHistory: lineHistory,
    };

    // Get unique books from props
    const booksFromProps: string[] = Array.from(
      new Set(propsData.map((p: any) => String(p.book || '')).filter((b: string) => b && b !== ''))
    );
    const defaultBooks = ['fanduel', 'draftkings'];
    availableBooks = booksFromProps.length > 0 ? booksFromProps : defaultBooks;
    
    // For consensus fallback, all books show the same data
    availableBooks.forEach(book => {
      bookmakers[book] = { marketGroups };
    });
  }

  const fullSportKey = sportKey;
  const sportConfig = SUPPORTED_SPORTS.find(s => s.key === fullSportKey);

  const scoreColor = compositeScore >= 0.5 ? 'text-emerald-400' : 'text-red-400';
  const scoreBg = compositeScore >= 0.5 ? 'bg-emerald-500/10' : 'bg-red-500/10';

  const hasProps = propsData && propsData.length > 0;
  const isNHL = fullSportKey.includes('icehockey');
  const isFootball = fullSportKey.includes('football');
  const isBasketball = fullSportKey.includes('basketball');

  // Check if we have any half/quarter data
  const hasFirstHalf = Object.values(bookmakers).some((b: any) => 
    b.marketGroups?.firstHalf?.spreads || b.marketGroups?.firstHalf?.h2h || b.marketGroups?.firstHalf?.totals
  );
  const hasSecondHalf = Object.values(bookmakers).some((b: any) => 
    b.marketGroups?.secondHalf?.spreads || b.marketGroups?.secondHalf?.h2h || b.marketGroups?.secondHalf?.totals
  );

  return (
    <div className="py-6">
      <div className="mb-6">
        <Link 
          href={`/edge/portal/sports/${fullSportKey}`}
          className="inline-flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to {sportConfig?.name || 'games'}
        </Link>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-3xl">{sportConfig?.icon || '🏆'}</div>
            <div>
              <h1 className="text-2xl font-bold text-zinc-100">{awayTeam} @ {homeTeam}</h1>
              <p className="text-zinc-400">
                {new Date(commenceTime).toLocaleString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1.5 rounded-lg ${scoreBg} flex items-center gap-2`}>
              <span className="text-xs text-zinc-400">Edge Score</span>
              <span className={`text-lg font-bold ${scoreColor}`}>
                {(compositeScore * 100).toFixed(0)}%
              </span>
            </div>
            <span className={`text-xs font-medium px-2 py-1 rounded ${
              confidence === 'STRONG_EDGE' ? 'bg-emerald-500/20 text-emerald-400' :
              confidence === 'EDGE' ? 'bg-emerald-500/10 text-emerald-300' :
              confidence === 'WATCH' ? 'bg-yellow-500/10 text-yellow-400' :
              'bg-zinc-800 text-zinc-500'
            }`}>
              {confidence}
            </span>
          </div>
        </div>
      </div>

      <GameDetailClient
        gameData={{ id: gameId, homeTeam, awayTeam, sportKey: fullSportKey }}
        bookmakers={bookmakers}
        availableBooks={availableBooks}
        availableTabs={{
          fullGame: true,
          firstHalf: true,
          secondHalf: true,
          q1: isFootball || isBasketball,
          q2: isFootball || isBasketball,
          q3: isFootball || isBasketball,
          q4: isFootball || isBasketball,
          p1: isNHL,
          p2: isNHL,
          p3: isNHL,
          props: hasProps,
          alternates: true,
          teamTotals: true,
        }}
      />
    </div>
  );
}