import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const SPORT_MAPPING: Record<string, string> = {
  'NFL': 'americanfootball_nfl',
  'NCAAF': 'americanfootball_ncaaf',
  'NBA': 'basketball_nba',
  'NHL': 'icehockey_nhl',
  'NCAAB': 'basketball_ncaab',
  'MLB': 'baseball_mlb',
  'WNBA': 'basketball_wnba',
  'MMA': 'mma_mixed_martial_arts',
  'TENNIS_AO': 'tennis_atp_australian_open',
  'TENNIS_FO': 'tennis_atp_french_open',
  'TENNIS_USO': 'tennis_atp_us_open',
  'TENNIS_WIM': 'tennis_atp_wimbledon',
};

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

async function fetchEdgesFromBackend(sport: string) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${BACKEND_URL}/api/edges/${sport}`, {
      cache: 'no-store',
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!res.ok) return [];
    const data = await res.json();
    return data.games || [];
  } catch (e) {
    return [];
  }
}

function processBackendGame(game: any, sport: string) {
  const consensus: any = {};

  if (game.consensus_odds?.h2h) {
    consensus.h2h = {
      homePrice: game.consensus_odds.h2h.home,
      awayPrice: game.consensus_odds.h2h.away,
    };
  }

  if (game.consensus_odds?.spreads) {
    consensus.spreads = {
      line: game.consensus_odds.spreads.home?.line,
      homePrice: game.consensus_odds.spreads.home?.odds,
      awayPrice: game.consensus_odds.spreads.away?.odds,
    };
  }

  if (game.consensus_odds?.totals) {
    consensus.totals = {
      line: game.consensus_odds.totals.over?.line,
      overPrice: game.consensus_odds.totals.over?.odds,
      underPrice: game.consensus_odds.totals.under?.odds,
    };
  }

  return {
    id: game.game_id,
    sportKey: SPORT_MAPPING[sport] || game.sport,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
    edges: game.edges,
    pillars: game.pillars,
    composite_score: game.composite_score,
    overall_confidence: game.overall_confidence,
    best_bet: game.best_bet,
    best_edge: game.best_edge,
  };
}

function processOddsApiGame(game: any) {
  const consensus: any = {};

  if (game.bookmakers && game.bookmakers.length > 0) {
    // Aggregate consensus from all bookmakers
    const h2hPrices: { home: number[]; away: number[] } = { home: [], away: [] };
    const spreadData: { line: number[]; homePrice: number[]; awayPrice: number[] } = { line: [], homePrice: [], awayPrice: [] };
    const totalData: { line: number[]; overPrice: number[]; underPrice: number[] } = { line: [], overPrice: [], underPrice: [] };

    for (const bookmaker of game.bookmakers) {
      for (const market of bookmaker.markets) {
        if (market.key === 'h2h') {
          const home = market.outcomes.find((o: any) => o.name === game.home_team);
          const away = market.outcomes.find((o: any) => o.name === game.away_team);
          if (home) h2hPrices.home.push(home.price);
          if (away) h2hPrices.away.push(away.price);
        }
        if (market.key === 'spreads') {
          const home = market.outcomes.find((o: any) => o.name === game.home_team);
          const away = market.outcomes.find((o: any) => o.name === game.away_team);
          if (home?.point !== undefined) {
            spreadData.line.push(home.point);
            spreadData.homePrice.push(home.price);
          }
          if (away) spreadData.awayPrice.push(away.price);
        }
        if (market.key === 'totals') {
          const over = market.outcomes.find((o: any) => o.name === 'Over');
          const under = market.outcomes.find((o: any) => o.name === 'Under');
          if (over?.point !== undefined) {
            totalData.line.push(over.point);
            totalData.overPrice.push(over.price);
          }
          if (under) totalData.underPrice.push(under.price);
        }
      }
    }

    const median = (arr: number[]) => {
      if (arr.length === 0) return undefined;
      const sorted = [...arr].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
    };

    if (h2hPrices.home.length > 0) {
      consensus.h2h = {
        homePrice: median(h2hPrices.home),
        awayPrice: median(h2hPrices.away),
      };
    }
    if (spreadData.line.length > 0) {
      consensus.spreads = {
        line: median(spreadData.line),
        homePrice: median(spreadData.homePrice),
        awayPrice: median(spreadData.awayPrice),
      };
    }
    if (totalData.line.length > 0) {
      consensus.totals = {
        line: median(totalData.line),
        overPrice: median(totalData.overPrice),
        underPrice: median(totalData.underPrice),
      };
    }
  }

  // Extract per-bookmaker odds for sportsbook filtering
  const bookmakers: Record<string, any> = {};
  if (game.bookmakers) {
    for (const bookmaker of game.bookmakers) {
      const bookOdds: any = {};
      for (const market of bookmaker.markets) {
        if (market.key === 'h2h') {
          const home = market.outcomes.find((o: any) => o.name === game.home_team);
          const away = market.outcomes.find((o: any) => o.name === game.away_team);
          bookOdds.h2h = { homePrice: home?.price, awayPrice: away?.price };
        }
        if (market.key === 'spreads') {
          const home = market.outcomes.find((o: any) => o.name === game.home_team);
          const away = market.outcomes.find((o: any) => o.name === game.away_team);
          bookOdds.spreads = { line: home?.point, homePrice: home?.price, awayPrice: away?.price };
        }
        if (market.key === 'totals') {
          const over = market.outcomes.find((o: any) => o.name === 'Over');
          const under = market.outcomes.find((o: any) => o.name === 'Under');
          bookOdds.totals = { line: over?.point, overPrice: over?.price, underPrice: under?.price };
        }
      }
      bookmakers[bookmaker.key] = bookOdds;
    }
  }

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
    bookmakers, // Per-book odds for sportsbook filtering
    bookmakerCount: game.bookmakers?.length || 0,
  };
}

async function fetchFromCache(sportKey: string) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .eq('sport_key', sportKey);

    if (error || !data) return [];

    return data
      .map((row: any) => processOddsApiGame(row.game_data))
      .filter(Boolean);
  } catch (e) {
    console.error(`[Cache] Failed to fetch ${sportKey}:`, e);
    return [];
  }
}

export default async function SportsPage() {
  const sports = ['NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB', 'MLB', 'MMA', 'TENNIS_AO', 'TENNIS_FO', 'TENNIS_USO', 'TENNIS_WIM'];
  const allGames: Record<string, any[]> = {};
  let dataSource: 'backend' | 'odds_api' | 'none' = 'none';
  let totalGames = 0;
  let totalEdges = 0;
  const fetchedAt = new Date().toISOString();

  // Try backend first (parallel fetch)
  const backendResults = await Promise.all(
    sports.map(async (sport) => {
      const games = await fetchEdgesFromBackend(sport);
      return { sport, games };
    })
  );

  const hasBackendData = backendResults.some(r => r.games.length > 0);

  if (hasBackendData) {
    dataSource = 'backend';
    for (const { sport, games } of backendResults) {
      const processed = games
        .map((g: any) => processBackendGame(g, sport))
        .filter(Boolean)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      const frontendKey = SPORT_MAPPING[sport];
      if (processed.length > 0 && frontendKey) {
        allGames[frontendKey] = processed;
        totalGames += processed.length;
        totalEdges += processed.filter((g: any) =>
          g.overall_confidence && g.overall_confidence !== 'PASS'
        ).length;
      }
    }
  } else {
    // Fallback: read from cached_odds table
    const cacheResults = await Promise.all(
      sports.map(async (sport) => {
        const sportKey = SPORT_MAPPING[sport];
        if (!sportKey) return { sport, games: [] };
        const games = await fetchFromCache(sportKey);
        return { sport, games };
      })
    );

    const hasCachedData = cacheResults.some(r => r.games.length > 0);
    if (hasCachedData) dataSource = 'odds_api';

    for (const { sport, games } of cacheResults) {
      const frontendKey = SPORT_MAPPING[sport];
      if (games.length > 0 && frontendKey) {
        // Filter to upcoming games only
        const now = new Date();
        const upcoming = games
          .filter((g: any) => new Date(g.commenceTime).getTime() > now.getTime() - 3 * 60 * 60 * 1000)
          .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());
        if (upcoming.length > 0) {
          allGames[frontendKey] = upcoming;
          totalGames += upcoming.length;
        }
      }
    }
  }

  return (
    <div className="py-4 px-4 max-w-[1600px] mx-auto">
      <SportsHomeGrid
        games={allGames}
        dataSource={dataSource}
        totalGames={totalGames}
        totalEdges={totalEdges}
        fetchedAt={fetchedAt}
      />
    </div>
  );
}
