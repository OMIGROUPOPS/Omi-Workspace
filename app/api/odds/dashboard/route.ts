import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// ACTIVE SPORTS - Must match app/api/odds/sync/route.ts SPORT_KEYS
const SPORT_KEYS = [
  'americanfootball_nfl',
  'americanfootball_ncaaf',
  'basketball_nba',
  'basketball_ncaab',
  'icehockey_nhl',
  'soccer_epl',
  'tennis_atp_australian_open',
  'tennis_atp_french_open',
  'tennis_atp_us_open',
  'tennis_atp_wimbledon',
];

// Edge threshold: game counts as "edge" if max edge >= 3%
const EDGE_THRESHOLD = 3.0;

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: {
        fetch: (url, options) => fetch(url, { ...options, cache: 'no-store' }),
      },
    }
  );
}

// Stub — live scores disabled to save API budget
async function fetchLiveScores(): Promise<Record<string, any>> {
  return {};
}

// Fetch latest composite_history entry per game (single source of truth for fair lines)
async function fetchLatestFairLines(gameIds: string[]): Promise<Record<string, {
  fair_spread: number | null;
  fair_total: number | null;
  fair_ml_home: number | null;
  fair_ml_away: number | null;
}>> {
  const fairLines: Record<string, any> = {};
  if (gameIds.length === 0) return fairLines;

  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('composite_history')
      .select('game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away')
      .in('game_id', gameIds)
      .order('timestamp', { ascending: false });

    if (error || !data) return fairLines;

    // Keep only the latest row per game_id (results ordered DESC)
    for (const row of data) {
      if (!fairLines[row.game_id]) {
        fairLines[row.game_id] = {
          fair_spread: row.fair_spread != null ? Number(row.fair_spread) : null,
          fair_total: row.fair_total != null ? Number(row.fair_total) : null,
          fair_ml_home: row.fair_ml_home != null ? Number(row.fair_ml_home) : null,
          fair_ml_away: row.fair_ml_away != null ? Number(row.fair_ml_away) : null,
        };
      }
    }
  } catch (e) {
    console.error('[Dashboard API] Fair lines fetch failed:', e);
  }

  return fairLines;
}

// American odds → implied probability
function toProb(odds: number): number {
  return odds < 0 ? Math.abs(odds) / (Math.abs(odds) + 100) : 100 / (odds + 100);
}

// Calculate max edge % for a game using composite fair lines vs book consensus
// Same formulas as edgescout.ts / GameDetailClient
function calculateMaxEdge(
  fairLines: { fair_spread: number | null; fair_total: number | null; fair_ml_home: number | null; fair_ml_away: number | null },
  consensus: any
): number {
  let maxEdge = 0;

  // Spread edge: abs(fair_spread - book_spread) * 3.0
  if (fairLines.fair_spread != null && consensus.spreads?.line !== undefined) {
    maxEdge = Math.max(maxEdge, Math.abs(fairLines.fair_spread - consensus.spreads.line) * 3.0);
  }

  // ML edge: compare vig-free implied probabilities
  if (fairLines.fair_ml_home != null && fairLines.fair_ml_away != null &&
      consensus.h2h?.homePrice !== undefined && consensus.h2h?.awayPrice !== undefined) {
    const fairHP = toProb(fairLines.fair_ml_home);
    const fairAP = toProb(fairLines.fair_ml_away);
    const bookHP = toProb(consensus.h2h.homePrice);
    const bookAP = toProb(consensus.h2h.awayPrice);
    const normBHP = bookHP / (bookHP + bookAP);
    const normBAP = bookAP / (bookHP + bookAP);
    maxEdge = Math.max(maxEdge, (fairHP - normBHP) * 100, (fairAP - normBAP) * 100);
  }

  // Total edge: abs(fair_total - book_total) * 1.5 (totals are higher-variance)
  if (fairLines.fair_total != null && consensus.totals?.line !== undefined) {
    maxEdge = Math.max(maxEdge, Math.abs(fairLines.fair_total - consensus.totals.line) * 1.5);
  }

  return maxEdge;
}

// Build flat consensus from bookmakers (median across all books)
// Returns flat format: spreads.line, h2h.homePrice, totals.line
function buildConsensus(game: any) {
  const bookmakers = game.bookmakers;
  if (!bookmakers || bookmakers.length === 0) return {};

  const h2hPrices: { home: number[]; away: number[]; draw: number[] } = { home: [], away: [], draw: [] };
  const spreadData: { line: number[]; homePrice: number[]; awayPrice: number[] } = { line: [], homePrice: [], awayPrice: [] };
  const totalData: { line: number[]; overPrice: number[]; underPrice: number[] } = { line: [], overPrice: [], underPrice: [] };

  for (const bk of bookmakers) {
    for (const market of bk.markets) {
      if (market.key === 'h2h') {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        const draw = market.outcomes.find((o: any) => o.name === 'Draw');
        if (home) h2hPrices.home.push(home.price);
        if (away) h2hPrices.away.push(away.price);
        if (draw) h2hPrices.draw.push(draw.price);
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

  const consensus: any = {};

  if (h2hPrices.home.length > 0) {
    consensus.h2h = {
      homePrice: median(h2hPrices.home),
      awayPrice: median(h2hPrices.away),
      drawPrice: h2hPrices.draw.length > 0 ? median(h2hPrices.draw) : undefined,
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

  return consensus;
}

// Process a single game from cached_odds into dashboard format
function processGame(
  game: any,
  scores: Record<string, any>,
  fairLinesMap: Record<string, any>
) {
  const consensus = buildConsensus(game);

  // Extract per-bookmaker odds (flat format matching server page)
  const bookmakers: Record<string, any> = {};
  if (game.bookmakers) {
    for (const bookmaker of game.bookmakers) {
      const bookOdds: any = {};
      for (const market of bookmaker.markets) {
        if (market.key === 'h2h') {
          const home = market.outcomes.find((o: any) => o.name === game.home_team);
          const away = market.outcomes.find((o: any) => o.name === game.away_team);
          const draw = market.outcomes.find((o: any) => o.name === 'Draw');
          bookOdds.h2h = { homePrice: home?.price, awayPrice: away?.price, drawPrice: draw?.price };
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

  // Attach fair lines from composite_history (single source of truth)
  const fairLines = fairLinesMap[game.id] || null;

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
    bookmakers,
    fairLines,
    scores: scores[game.id] || null,
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

    // Fetch fair lines and scores in parallel
    const [scores, fairLinesMap] = await Promise.all([
      fetchLiveScores(),
      fetchLatestFairLines(gameIds),
    ]);

    // Process games by sport
    const allGames: Record<string, any[]> = {};
    let totalGames = 0;
    let totalEdges = 0;
    const now = new Date();
    const sevenDaysFromNow = now.getTime() + 7 * 24 * 60 * 60 * 1000;
    const fourHoursAgo = now.getTime() - 4 * 60 * 60 * 1000;

    for (const sportKey of SPORT_KEYS) {
      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];

      const games = sportData
        .map((row: any) => processGame(row.game_data, scores, fairLinesMap))
        .filter(Boolean)
        // Keep future games AND games that started within last 4 hours (live/recently finished)
        .filter((g: any) => new Date(g.commenceTime).getTime() > fourHoursAgo)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      if (games.length > 0) {
        allGames[sportKey] = games;
        totalGames += games.length;

        // Count edges: games with composite_history fair lines AND max edge >= 3% AND within 7 days
        totalEdges += games.filter((g: any) => {
          if (!g.fairLines) return false;
          const gameTime = new Date(g.commenceTime).getTime();
          if (gameTime > sevenDaysFromNow) return false;
          return calculateMaxEdge(g.fairLines, g.consensus) >= EDGE_THRESHOLD;
        }).length;
      }
    }

    // Get the most recent update time
    const latestUpdate = allCachedData?.reduce((latest: string | null, row: any) => {
      if (!latest || row.updated_at > latest) return row.updated_at;
      return latest;
    }, null);

    const processingTime = Date.now() - startTime;
    console.log(`[Dashboard API] ${totalGames} games, ${totalEdges} edges (>=${EDGE_THRESHOLD}%), ${Object.keys(fairLinesMap).length} fair lines, ${processingTime}ms`);

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
