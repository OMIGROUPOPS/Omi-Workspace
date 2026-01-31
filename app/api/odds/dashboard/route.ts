import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { calculateGameCEQ, type ExtendedOddsSnapshot, type GameCEQ, type GameContextData, type TeamStatsData } from '@/lib/edge/engine/edgescout';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';
import { calculateTwoWayEV } from '@/lib/edge/utils/odds-math';

const ODDS_API_KEY = process.env.ODDS_API_KEY || '';
const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

const SPORT_KEYS = [
  'americanfootball_nfl',
  'basketball_nba',
  'icehockey_nhl',
  'americanfootball_ncaaf',
  'basketball_ncaab',
  'baseball_mlb',
  'basketball_wnba',
];

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Fetch live scores
async function fetchLiveScores(): Promise<Record<string, any>> {
  const scores: Record<string, any> = {};
  if (!ODDS_API_KEY) return scores;

  try {
    const results = await Promise.all(
      SPORT_KEYS.map(async (sportKey) => {
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
    console.error('[Dashboard API] Scores fetch failed:', e);
  }

  return scores;
}

// Fetch opening lines
async function fetchOpeningLines(gameIds: string[]): Promise<Record<string, number>> {
  const openingLines: Record<string, number> = {};
  if (gameIds.length === 0) return openingLines;

  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('game_id, line, snapshot_time')
      .in('game_id', gameIds)
      .eq('market', 'spreads')
      .not('line', 'is', null)
      .order('snapshot_time', { ascending: true })
      .limit(500);

    if (!error && data) {
      for (const row of data) {
        if (!openingLines[row.game_id] && row.line !== null) {
          openingLines[row.game_id] = row.line;
        }
      }
    }
  } catch (e) {
    console.error('[Dashboard API] Opening lines fetch failed:', e);
  }

  return openingLines;
}

// Fetch snapshots for CEQ
async function fetchGameSnapshots(gameIds: string[]): Promise<Record<string, ExtendedOddsSnapshot[]>> {
  const snapshotsMap: Record<string, ExtendedOddsSnapshot[]> = {};
  if (gameIds.length === 0) return snapshotsMap;

  try {
    const supabase = getSupabase();
    const sixHoursAgo = new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString();

    const batches: string[][] = [];
    for (let i = 0; i < gameIds.length; i += 20) {
      batches.push(gameIds.slice(i, i + 20));
    }

    const results = await Promise.all(
      batches.map(async (batchIds) => {
        const { data, error } = await supabase
          .from('odds_snapshots')
          .select('game_id, market, book_key, outcome_type, line, odds, snapshot_time')
          .in('game_id', batchIds)
          .gte('snapshot_time', sixHoursAgo)
          .order('snapshot_time', { ascending: true })
          .limit(2000);

        if (error) return [];
        return data || [];
      })
    );

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
    console.error('[Dashboard API] Snapshots fetch failed:', e);
  }

  return snapshotsMap;
}

// Fetch team stats
async function fetchAllTeamStats(): Promise<Map<string, TeamStatsData>> {
  const teamStatsMap = new Map<string, TeamStatsData>();
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('team_stats')
      .select('*')
      .order('updated_at', { ascending: false })
      .limit(500);

    if (error || !data) return teamStatsMap;

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
    console.error('[Dashboard API] Team stats fetch failed:', e);
  }
  return teamStatsMap;
}

function buildGameContext(
  homeTeam: string,
  awayTeam: string,
  sportKey: string,
  teamStatsMap: Map<string, TeamStatsData>
): GameContextData {
  const homeKey = homeTeam?.toLowerCase();
  const awayKey = awayTeam?.toLowerCase();

  let homeStats = teamStatsMap.get(homeKey);
  let awayStats = teamStatsMap.get(awayKey);

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

function processGame(
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

  // Calculate CEQ
  const gameSnapshots = snapshotsMap[game.id] || [];

  const openingData = {
    spreads: openingLines[game.id] !== undefined ? {
      home: openingLines[game.id],
      away: -openingLines[game.id],
    } : undefined,
  };

  const gameContext = buildGameContext(
    game.home_team,
    game.away_team,
    game.sport_key,
    teamStatsMap
  );

  // Calculate CEQ PER BOOK - each book gets its own CEQ based on its prices
  const ceqByBook: Record<string, GameCEQ | null> = {};

  for (const [bookKey, bookOddsData] of Object.entries(bookmakers)) {
    const bookData = bookOddsData as any;

    // Build gameOdds using THIS BOOK's prices (not consensus)
    const bookGameOdds = {
      spreads: bookData.spreads?.line !== undefined ? {
        home: { line: bookData.spreads.line, odds: bookData.spreads.homePrice || -110 },
        away: { line: -bookData.spreads.line, odds: bookData.spreads.awayPrice || -110 },
      } : undefined,
      h2h: bookData.h2h?.homePrice !== undefined ? {
        home: bookData.h2h.homePrice,
        away: bookData.h2h.awayPrice,
      } : undefined,
      totals: bookData.totals?.line !== undefined ? {
        line: bookData.totals.line,
        over: bookData.totals.overPrice || -110,
        under: bookData.totals.underPrice || -110,
      } : undefined,
    };

    if (bookGameOdds.spreads || bookGameOdds.h2h || bookGameOdds.totals) {
      ceqByBook[bookKey] = calculateGameCEQ(
        bookGameOdds,
        openingData,
        gameSnapshots,
        allBooksOdds,  // Pass all books for SBI comparison
        {
          // consensusOdds stays as consensus (for SBI to compare book vs market)
          spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
          h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
          totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
        },
        gameContext
      );
    }
  }

  // Also calculate consensus CEQ for fallback/default view
  let ceqData: GameCEQ | null = null;
  const consensusGameOdds = {
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

  if (consensusGameOdds.spreads || consensusGameOdds.h2h || consensusGameOdds.totals) {
    ceqData = calculateGameCEQ(
      consensusGameOdds,
      openingData,
      gameSnapshots,
      {},  // Empty for consensus (no SBI comparison needed - would compare to itself)
      {
        spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
        h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
        totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
      },
      gameContext
    );
  }

  // Determine edge data
  let edgeData;
  if (ceqData?.bestEdge) {
    edgeData = {
      score: ceqData.bestEdge.ceq,
      confidence: ceqData.bestEdge.confidence,
      side: ceqData.bestEdge.side,
    };
  } else {
    edgeData = calculateQuickEdge(
      openingLines[game.id],
      consensus.spreads?.line,
      consensus.spreads?.homePrice,
      consensus.spreads?.awayPrice
    );
  }

  // Calculate EV for edge validation - edge only valid if EV is not negative
  // Check all markets and see if any have valid edge (CEQ >= 56 AND EV >= 0)
  let hasValidEdge = false;

  if (ceqData) {
    // Check spreads
    if (ceqData.spreads?.home?.ceq !== undefined && ceqData.spreads.home.ceq >= 56) {
      const ev = consensus.spreads?.homePrice && consensus.spreads?.awayPrice
        ? calculateTwoWayEV(consensus.spreads.homePrice, consensus.spreads.awayPrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
    if (!hasValidEdge && ceqData.spreads?.away?.ceq !== undefined && ceqData.spreads.away.ceq >= 56) {
      const ev = consensus.spreads?.awayPrice && consensus.spreads?.homePrice
        ? calculateTwoWayEV(consensus.spreads.awayPrice, consensus.spreads.homePrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
    // Check h2h
    if (!hasValidEdge && ceqData.h2h?.home?.ceq !== undefined && ceqData.h2h.home.ceq >= 56) {
      const ev = consensus.h2h?.homePrice && consensus.h2h?.awayPrice
        ? calculateTwoWayEV(consensus.h2h.homePrice, consensus.h2h.awayPrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
    if (!hasValidEdge && ceqData.h2h?.away?.ceq !== undefined && ceqData.h2h.away.ceq >= 56) {
      const ev = consensus.h2h?.awayPrice && consensus.h2h?.homePrice
        ? calculateTwoWayEV(consensus.h2h.awayPrice, consensus.h2h.homePrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
    // Check totals
    if (!hasValidEdge && ceqData.totals?.over?.ceq !== undefined && ceqData.totals.over.ceq >= 56) {
      const ev = consensus.totals?.overPrice && consensus.totals?.underPrice
        ? calculateTwoWayEV(consensus.totals.overPrice, consensus.totals.underPrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
    if (!hasValidEdge && ceqData.totals?.under?.ceq !== undefined && ceqData.totals.under.ceq >= 56) {
      const ev = consensus.totals?.underPrice && consensus.totals?.overPrice
        ? calculateTwoWayEV(consensus.totals.underPrice, consensus.totals.overPrice)
        : undefined;
      if (ev === undefined || ev >= 0) hasValidEdge = true;
    }
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
    ceq: ceqData,
    ceqByBook,  // Per-book CEQ for selected book display
    scores: scores[game.id] || null,
    hasValidEdge, // True only if CEQ >= 56 AND EV >= 0
  };
}

export async function GET() {
  const startTime = Date.now();

  try {
    const supabase = getSupabase();

    // Fetch all cached odds
    const { data: allCachedData, error } = await supabase
      .from('cached_odds')
      .select('sport_key, game_data, updated_at')
      .in('sport_key', SPORT_KEYS);

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    // Collect all game IDs
    const gameIds: string[] = [];
    if (allCachedData) {
      for (const row of allCachedData) {
        if (row.game_data?.id) gameIds.push(row.game_data.id);
      }
    }

    // Fetch all required data in parallel
    const [scores, openingLines, snapshotsMap, teamStatsMap] = await Promise.all([
      fetchLiveScores(),
      fetchOpeningLines(gameIds),
      fetchGameSnapshots(gameIds),
      fetchAllTeamStats(),
    ]);

    // Process games by sport
    const allGames: Record<string, any[]> = {};
    let totalGames = 0;
    let totalEdges = 0;
    const now = new Date();

    for (const sportKey of SPORT_KEYS) {
      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];

      const games = sportData
        .map((row: any) => processGame(row.game_data, scores, openingLines, snapshotsMap, teamStatsMap))
        .filter(Boolean)
        // Only include games that haven't ended (start time within last 4 hours or future)
        .filter((g: any) => new Date(g.commenceTime).getTime() > now.getTime() - 4 * 60 * 60 * 1000)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      if (games.length > 0) {
        allGames[sportKey] = games;
        totalGames += games.length;
        // Count only valid edges: CEQ >= 56 AND EV >= 0
        totalEdges += games.filter((g: any) => g.hasValidEdge === true).length;
      }
    }

    // Get the most recent update time
    const latestUpdate = allCachedData?.reduce((latest: string | null, row: any) => {
      if (!latest || row.updated_at > latest) return row.updated_at;
      return latest;
    }, null);

    const processingTime = Date.now() - startTime;

    return NextResponse.json({
      games: allGames,
      totalGames,
      totalEdges,
      fetchedAt: new Date().toISOString(),
      dataUpdatedAt: latestUpdate,
      processingTimeMs: processingTime,
    });
  } catch (error) {
    console.error('[Dashboard API] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
