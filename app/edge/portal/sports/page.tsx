import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const ODDS_API_KEY = process.env.ODDS_API_KEY || '';
const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

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

// Direct Supabase client for non-cookie operations
function getDirectSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Fetch live scores from The Odds API
async function fetchLiveScores(): Promise<Record<string, any>> {
  const scores: Record<string, any> = {};

  if (!ODDS_API_KEY) return scores;

  const sportKeys = [
    'americanfootball_nfl', 'basketball_nba', 'icehockey_nhl',
    'americanfootball_ncaaf', 'basketball_ncaab', 'baseball_mlb', 'basketball_wnba'
  ];

  try {
    // Fetch scores for each sport in parallel
    const results = await Promise.all(
      sportKeys.map(async (sportKey) => {
        try {
          const url = `${ODDS_API_BASE}/sports/${sportKey}/scores?apiKey=${ODDS_API_KEY}&daysFrom=1`;
          const res = await fetch(url, { cache: 'no-store' });
          if (!res.ok) return [];
          return res.json();
        } catch {
          return [];
        }
      })
    );

    // Process all scores into a map by game ID
    for (const sportScores of results) {
      for (const game of sportScores) {
        if (game.scores && game.scores.length >= 2) {
          const homeScore = game.scores.find((s: any) => s.name === game.home_team);
          const awayScore = game.scores.find((s: any) => s.name === game.away_team);
          scores[game.id] = {
            home: parseInt(homeScore?.score || '0'),
            away: parseInt(awayScore?.score || '0'),
            completed: game.completed,
            lastUpdate: game.last_update,
          };
        }
      }
    }
  } catch (e) {
    console.error('[Scores] Fetch failed:', e);
  }

  return scores;
}

// Fetch opening lines from odds_snapshots for edge calculation
async function fetchOpeningLines(gameIds: string[]): Promise<Record<string, number>> {
  const openingLines: Record<string, number> = {};

  if (gameIds.length === 0) return openingLines;

  try {
    const supabase = getDirectSupabase();
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('game_id, line, snapshot_time')
      .in('game_id', gameIds)
      .eq('market', 'spreads')
      .eq('outcome_type', 'home')
      .order('snapshot_time', { ascending: true });

    if (!error && data) {
      // Get first snapshot (opening line) for each game
      for (const row of data) {
        if (!openingLines[row.game_id] && row.line !== null) {
          openingLines[row.game_id] = row.line;
        }
      }
    }
  } catch (e) {
    console.error('[OpeningLines] Fetch failed:', e);
  }

  return openingLines;
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

function processBackendGame(game: any, sport: string, scores: Record<string, any>, openingLines: Record<string, number>) {
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

  // Calculate edge if not provided by backend
  let edgeData = null;
  if (game.composite_score && game.overall_confidence) {
    edgeData = {
      score: Math.round(game.composite_score * 100),
      confidence: game.overall_confidence,
      side: game.best_bet?.side || null,
    };
  } else {
    // Calculate using our edge calculator
    const calculated = calculateQuickEdge(
      openingLines[game.game_id],
      consensus.spreads?.line,
      consensus.spreads?.homePrice,
      consensus.spreads?.awayPrice
    );
    edgeData = calculated;
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
    composite_score: game.composite_score || (edgeData.score / 100),
    overall_confidence: game.overall_confidence || edgeData.confidence,
    best_bet: game.best_bet,
    best_edge: game.best_edge,
    calculatedEdge: edgeData,
    scores: scores[game.game_id] || null,
  };
}

function processOddsApiGame(game: any, scores: Record<string, any>, openingLines: Record<string, number>) {
  const consensus: any = {};

  if (game.bookmakers && game.bookmakers.length > 0) {
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

  // Extract per-bookmaker odds
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

  // Calculate edge
  const calculated = calculateQuickEdge(
    openingLines[game.id],
    consensus.spreads?.line,
    consensus.spreads?.homePrice,
    consensus.spreads?.awayPrice
  );

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
    bookmakers,
    bookmakerCount: game.bookmakers?.length || 0,
    composite_score: calculated.score / 100,
    overall_confidence: calculated.confidence,
    calculatedEdge: calculated,
    scores: scores[game.id] || null,
  };
}

async function fetchFromCache(sportKey: string, scores: Record<string, any>, openingLines: Record<string, number>) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .eq('sport_key', sportKey);

    if (error || !data) return [];

    return data
      .map((row: any) => processOddsApiGame(row.game_data, scores, openingLines))
      .filter(Boolean);
  } catch (e) {
    console.error(`[Cache] Failed to fetch ${sportKey}:`, e);
    return [];
  }
}

export default async function SportsPage() {
  const sports = ['NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB', 'MLB', 'WNBA', 'MMA', 'TENNIS_AO', 'TENNIS_FO', 'TENNIS_USO', 'TENNIS_WIM'];
  const allGames: Record<string, any[]> = {};
  let dataSource: 'backend' | 'odds_api' | 'none' = 'none';
  let totalGames = 0;
  let totalEdges = 0;
  const fetchedAt = new Date().toISOString();

  // Fetch live scores in parallel with game data
  const [scoresData, backendResults] = await Promise.all([
    fetchLiveScores(),
    Promise.all(sports.map(async (sport) => {
      const games = await fetchEdgesFromBackend(sport);
      return { sport, games };
    }))
  ]);

  const hasBackendData = backendResults.some(r => r.games.length > 0);

  // Collect all game IDs for opening line lookup
  const allGameIds: string[] = [];
  for (const { games } of backendResults) {
    for (const game of games) {
      if (game.game_id) allGameIds.push(game.game_id);
    }
  }

  // Fetch opening lines for edge calculation
  const openingLines = await fetchOpeningLines(allGameIds);

  if (hasBackendData) {
    dataSource = 'backend';
    for (const { sport, games } of backendResults) {
      const processed = games
        .map((g: any) => processBackendGame(g, sport, scoresData, openingLines))
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
        const games = await fetchFromCache(sportKey, scoresData, openingLines);
        return { sport, games };
      })
    );

    const hasCachedData = cacheResults.some(r => r.games.length > 0);
    if (hasCachedData) dataSource = 'odds_api';

    for (const { sport, games } of cacheResults) {
      const frontendKey = SPORT_MAPPING[sport];
      if (games.length > 0 && frontendKey) {
        const now = new Date();
        const upcoming = games
          .filter((g: any) => new Date(g.commenceTime).getTime() > now.getTime() - 4 * 60 * 60 * 1000)
          .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());
        if (upcoming.length > 0) {
          allGames[frontendKey] = upcoming;
          totalGames += upcoming.length;
          totalEdges += upcoming.filter((g: any) =>
            g.overall_confidence && g.overall_confidence !== 'PASS'
          ).length;
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
