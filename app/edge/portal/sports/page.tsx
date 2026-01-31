import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';
import { calculateCEQ, calculateGameCEQ, groupSnapshotsByGame, type ExtendedOddsSnapshot, type GameCEQ, type GameContextData, type TeamStatsData } from '@/lib/edge/engine/edgescout';

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
// Note: outcome_type contains team names (not 'home'/'away'), so we fetch all spreads
// and take the first one per game that has a line value
async function fetchOpeningLines(gameIds: string[]): Promise<Record<string, number>> {
  const openingLines: Record<string, number> = {};

  if (gameIds.length === 0) return openingLines;

  try {
    const supabase = getDirectSupabase();
    // Limit query to improve performance
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('game_id, line, snapshot_time')
      .in('game_id', gameIds)
      .eq('market', 'spreads')
      .not('line', 'is', null)
      .order('snapshot_time', { ascending: true })
      .limit(500); // Only need first snapshot per game

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

// Fetch snapshot history for CEQ calculations
// Only fetches recent snapshots (last 6h) to keep query fast
async function fetchGameSnapshots(gameIds: string[]): Promise<Record<string, ExtendedOddsSnapshot[]>> {
  const snapshotsMap: Record<string, ExtendedOddsSnapshot[]> = {};

  if (gameIds.length === 0) return snapshotsMap;

  try {
    const supabase = getDirectSupabase();
    // Only fetch last 6 hours of snapshots - enough for CEQ calculation, much faster
    const sixHoursAgo = new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString();

    // Create batches of 20 games each
    const batches: string[][] = [];
    for (let i = 0; i < gameIds.length; i += 20) {
      batches.push(gameIds.slice(i, i + 20));
    }

    // Run ALL batches in parallel instead of sequentially
    const results = await Promise.all(
      batches.map(async (batchIds) => {
        const { data, error } = await supabase
          .from('odds_snapshots')
          .select('game_id, market, book_key, outcome_type, line, odds, snapshot_time')
          .in('game_id', batchIds)
          .gte('snapshot_time', sixHoursAgo)
          .order('snapshot_time', { ascending: true })
          .limit(2000); // 2000 per batch, reduced for speed

        if (error) return [];
        return data || [];
      })
    );

    // Merge all results
    for (const data of results) {
      for (const row of data) {
        if (!snapshotsMap[row.game_id]) {
          snapshotsMap[row.game_id] = [];
        }
        snapshotsMap[row.game_id].push({
          game_id: row.game_id,
          market: row.market,
          book_key: row.book_key,
          outcome_type: row.outcome_type,
          line: row.line,
          odds: row.odds,
          snapshot_time: row.snapshot_time,
        });
      }
    }
  } catch (e) {
    console.error('[GameSnapshots] Fetch failed:', e);
  }

  return snapshotsMap;
}

// Fetch all team stats for CEQ Game Environment and Matchup Dynamics pillars
async function fetchAllTeamStats(): Promise<Map<string, TeamStatsData>> {
  const teamStatsMap = new Map<string, TeamStatsData>();
  try {
    const supabase = getDirectSupabase();
    const { data, error } = await supabase
      .from('team_stats')
      .select('*')
      .order('updated_at', { ascending: false })
      .limit(500); // Limit to 500 teams (more than enough for all major sports)

    if (error || !data) return teamStatsMap;

    // Index by team name (lowercase for matching)
    for (const stat of data) {
      const key = stat.team_name?.toLowerCase();
      if (key && !teamStatsMap.has(key)) {
        teamStatsMap.set(key, {
          team_id: stat.team_id,
          team_name: stat.team_name,
          pace: stat.pace,
          offensive_rating: stat.offensive_rating,
          defensive_rating: stat.defensive_rating,
          net_rating: stat.net_rating,
          wins: stat.wins,
          losses: stat.losses,
          win_pct: stat.win_pct,
          home_wins: stat.home_wins,
          home_losses: stat.home_losses,
          away_wins: stat.away_wins,
          away_losses: stat.away_losses,
          streak: stat.streak,
          points_per_game: stat.points_per_game,
          points_allowed_per_game: stat.points_allowed_per_game,
          injuries: stat.injuries || [],
        });
      }
    }
  } catch (e) {
    console.error('[TeamStats] Fetch failed:', e);
  }
  return teamStatsMap;
}

// Build game context from team stats map
function buildGameContext(
  homeTeam: string,
  awayTeam: string,
  sportKey: string,
  teamStatsMap: Map<string, TeamStatsData>
): GameContextData {
  const homeKey = homeTeam?.toLowerCase();
  const awayKey = awayTeam?.toLowerCase();

  // Try exact match first, then partial match
  let homeStats = teamStatsMap.get(homeKey);
  let awayStats = teamStatsMap.get(awayKey);

  // Partial match fallback (e.g., "Los Angeles Lakers" matches "lakers")
  if (!homeStats) {
    for (const [key, stats] of teamStatsMap) {
      if (homeKey?.includes(key) || key.includes(homeKey || '')) {
        homeStats = stats;
        break;
      }
    }
  }
  if (!awayStats) {
    for (const [key, stats] of teamStatsMap) {
      if (awayKey?.includes(key) || key.includes(awayKey || '')) {
        awayStats = stats;
        break;
      }
    }
  }

  return {
    homeTeam: homeStats,
    awayTeam: awayStats,
    league: sportKey?.split('_')[1] || sportKey,
  };
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

function processBackendGame(
  game: any,
  sport: string,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>
) {
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

  // Calculate CEQ using EdgeScout framework
  const gameSnapshots = snapshotsMap[game.game_id] || [];
  let ceqData: GameCEQ | null = null;

  // Build odds data for CEQ calculation
  const gameOdds = {
    spreads: consensus.spreads?.line !== undefined ? {
      home: { line: consensus.spreads.line, odds: consensus.spreads.homePrice || -110 },
      away: { line: -consensus.spreads.line, odds: consensus.spreads.awayPrice || -110 },
    } : undefined,
    h2h: consensus.h2h ? {
      home: consensus.h2h.homePrice,
      away: consensus.h2h.awayPrice,
    } : undefined,
    totals: consensus.totals?.line !== undefined ? {
      line: consensus.totals.line,
      over: consensus.totals.overPrice || -110,
      under: consensus.totals.underPrice || -110,
    } : undefined,
  };

  // Opening lines for CEQ (use spread home line as baseline)
  const openingData = {
    spreads: openingLines[game.game_id] !== undefined ? {
      home: openingLines[game.game_id],
      away: -openingLines[game.game_id],
    } : undefined,
  };

  // Build game context from team stats for CEQ pillars
  const gameContext = buildGameContext(
    game.home_team,
    game.away_team,
    SPORT_MAPPING[sport] || game.sport,
    teamStatsMap
  );

  // Calculate CEQ
  if (gameOdds.spreads || gameOdds.h2h || gameOdds.totals) {
    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      gameSnapshots,
      {}, // allBooksOdds - would need to aggregate from bookmakers
      {
        spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
        h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
        totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
      },
      gameContext
    );
  }

  // Calculate edge if not provided by backend
  let edgeData = null;
  if (ceqData?.bestEdge) {
    edgeData = {
      score: ceqData.bestEdge.ceq,
      confidence: ceqData.bestEdge.confidence,
      side: ceqData.bestEdge.side,
    };
  } else if (game.composite_score && game.overall_confidence) {
    edgeData = {
      score: Math.round(game.composite_score * 100),
      confidence: game.overall_confidence,
      side: game.best_bet?.side || null,
    };
  } else {
    // Fallback to quick edge calculator
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
    ceq: ceqData, // Full CEQ data for UI
    scores: scores[game.game_id] || null,
  };
}

function processOddsApiGame(
  game: any,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>
) {
  const consensus: any = {};
  const allBooksOdds: {
    spreads?: { home: number[]; away: number[] };
    h2h?: { home: number[]; away: number[] };
    totals?: { over: number[]; under: number[] };
  } = {};

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

    // Store all books odds for CEQ calculation
    allBooksOdds.spreads = { home: spreadData.homePrice, away: spreadData.awayPrice };
    allBooksOdds.h2h = { home: h2hPrices.home, away: h2hPrices.away };
    allBooksOdds.totals = { over: totalData.overPrice, under: totalData.underPrice };

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

  // Calculate CEQ using EdgeScout framework
  const gameSnapshots = snapshotsMap[game.id] || [];
  let ceqData: GameCEQ | null = null;

  // Build odds data for CEQ calculation
  const gameOdds = {
    spreads: consensus.spreads?.line !== undefined ? {
      home: { line: consensus.spreads.line, odds: consensus.spreads.homePrice || -110 },
      away: { line: -consensus.spreads.line, odds: consensus.spreads.awayPrice || -110 },
    } : undefined,
    h2h: consensus.h2h ? {
      home: consensus.h2h.homePrice,
      away: consensus.h2h.awayPrice,
    } : undefined,
    totals: consensus.totals?.line !== undefined ? {
      line: consensus.totals.line,
      over: consensus.totals.overPrice || -110,
      under: consensus.totals.underPrice || -110,
    } : undefined,
  };

  // Opening lines for CEQ
  const openingData = {
    spreads: openingLines[game.id] !== undefined ? {
      home: openingLines[game.id],
      away: -openingLines[game.id],
    } : undefined,
  };

  // Build game context from team stats for CEQ pillars
  const gameContext = buildGameContext(
    game.home_team,
    game.away_team,
    game.sport_key,
    teamStatsMap
  );

  // Calculate CEQ
  if (gameOdds.spreads || gameOdds.h2h || gameOdds.totals) {
    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      gameSnapshots,
      allBooksOdds,
      {
        spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
        h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
        totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
      },
      gameContext
    );
  }

  // Determine edge data - prioritize CEQ
  let edgeData;
  if (ceqData?.bestEdge) {
    edgeData = {
      score: ceqData.bestEdge.ceq,
      confidence: ceqData.bestEdge.confidence,
      side: ceqData.bestEdge.side,
    };
  } else {
    // Fallback to quick edge calculator
    edgeData = calculateQuickEdge(
      openingLines[game.id],
      consensus.spreads?.line,
      consensus.spreads?.homePrice,
      consensus.spreads?.awayPrice
    );
  }

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
    bookmakers,
    bookmakerCount: game.bookmakers?.length || 0,
    composite_score: edgeData.score / 100,
    overall_confidence: edgeData.confidence,
    calculatedEdge: edgeData,
    ceq: ceqData, // Full CEQ data for UI
    scores: scores[game.id] || null,
  };
}

async function fetchFromCache(
  sportKey: string,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>
) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .eq('sport_key', sportKey);

    if (error || !data) return [];

    return data
      .map((row: any) => processOddsApiGame(row.game_data, scores, openingLines, snapshotsMap, teamStatsMap))
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

  // Collect all game IDs for opening line and snapshot lookup
  const allGameIds: string[] = [];
  for (const { games } of backendResults) {
    for (const game of games) {
      if (game.game_id) allGameIds.push(game.game_id);
    }
  }

  // Fetch opening lines, snapshots, and team stats for CEQ calculation
  const [openingLines, snapshotsMap, teamStatsMap] = await Promise.all([
    fetchOpeningLines(allGameIds),
    fetchGameSnapshots(allGameIds),
    fetchAllTeamStats(),
  ]);

  if (hasBackendData) {
    dataSource = 'backend';
    for (const { sport, games } of backendResults) {
      const processed = games
        .map((g: any) => processBackendGame(g, sport, scoresData, openingLines, snapshotsMap, teamStatsMap))
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
    // Fetch all cached odds in a single query (no sport filter, do filtering after)
    const supabase = getSupabase();
    const sportKeys = sports.map(s => SPORT_MAPPING[s]).filter(Boolean);

    // Single query for all sports
    const { data: allCachedData } = await supabase
      .from('cached_odds')
      .select('sport_key, game_data')
      .in('sport_key', sportKeys);

    // Collect all game IDs
    const cachedGameIds: string[] = [];
    if (allCachedData) {
      for (const row of allCachedData) {
        if (row.game_data?.id) cachedGameIds.push(row.game_data.id);
      }
    }

    // Fetch snapshots for cached games (already parallelized)
    const cachedSnapshotsMap = cachedGameIds.length > 0
      ? await fetchGameSnapshots(cachedGameIds)
      : {};

    // Process all games directly from the single query result
    const cacheResults: { sport: string; games: any[] }[] = sports.map(sport => {
      const sportKey = SPORT_MAPPING[sport];
      if (!sportKey) return { sport, games: [] };

      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];
      const games = sportData
        .map((row: any) => processOddsApiGame(row.game_data, scoresData, openingLines, cachedSnapshotsMap, teamStatsMap))
        .filter(Boolean);
      return { sport, games };
    });

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
