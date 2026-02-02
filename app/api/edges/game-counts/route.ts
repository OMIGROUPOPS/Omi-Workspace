import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { calculateGameCEQ, fetchGameContext, type ExtendedOddsSnapshot, type GameCEQ } from '@/lib/edge/engine/edgescout';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Count edges from a CEQ result - SAME logic as game detail page
function countPeriodEdges(ceq: GameCEQ | null): number {
  if (!ceq) return 0;
  let count = 0;
  // Spreads: home and away are separate edges
  if (ceq.spreads?.home?.ceq !== undefined && ceq.spreads.home.ceq >= 56) count++;
  if (ceq.spreads?.away?.ceq !== undefined && ceq.spreads.away.ceq >= 56) count++;
  // H2H/Moneyline: home, away, and draw (for soccer) are separate edges
  if (ceq.h2h?.home?.ceq !== undefined && ceq.h2h.home.ceq >= 56) count++;
  if (ceq.h2h?.away?.ceq !== undefined && ceq.h2h.away.ceq >= 56) count++;
  if (ceq.h2h?.draw?.ceq !== undefined && ceq.h2h.draw.ceq >= 56) count++;
  // Totals: over and under are separate edges
  if (ceq.totals?.over?.ceq !== undefined && ceq.totals.over.ceq >= 56) count++;
  if (ceq.totals?.under?.ceq !== undefined && ceq.totals.under.ceq >= 56) count++;
  return count;
}

// Fetch cached game data
async function fetchGameData(gameId: string) {
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from('cached_odds')
    .select('sport_key, game_data')
    .eq('game_id', gameId)
    .single();

  if (error || !data) return null;
  return { sportKey: data.sport_key, gameData: data.game_data };
}

// Fetch opening line
async function fetchOpeningLine(gameId: string): Promise<number | undefined> {
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from('odds_snapshots')
    .select('line')
    .eq('game_id', gameId)
    .eq('market', 'spreads')
    .not('line', 'is', null)
    .order('snapshot_time', { ascending: true })
    .limit(1);

  if (error || !data || data.length === 0) return undefined;
  return data[0].line;
}

// Fetch snapshots for CEQ calculation - limited for performance
async function fetchSnapshots(gameId: string): Promise<ExtendedOddsSnapshot[]> {
  const supabase = getSupabase();
  // PERF: Limit to most recent 500 snapshots - sufficient for edge calculation
  const { data, error } = await supabase
    .from('odds_snapshots')
    .select('game_id, market, book_key, outcome_type, line, odds, snapshot_time')
    .eq('game_id', gameId)
    .order('snapshot_time', { ascending: false })
    .limit(500);

  if (error || !data) return [];
  // Reverse to get chronological order
  return data.reverse().map(row => ({
    game_id: row.game_id,
    market: row.market,
    book_key: row.book_key,
    outcome_type: row.outcome_type,
    line: row.line,
    odds: row.odds,
    snapshot_time: row.snapshot_time,
  }));
}

// Build per-book marketGroups from raw Odds API data - SAME as game detail page
function buildPerBookMarketGroups(gameData: any): Record<string, any> {
  const result: Record<string, any> = {};
  const bookmakers = gameData.bookmakers || [];

  for (const bk of bookmakers) {
    const bookKey = bk.key;
    const marketsByKey: Record<string, any> = {};
    for (const market of (bk.markets || [])) {
      marketsByKey[market.key] = market;
    }

    const isSoccer = (gameData.sport_key || '').includes('soccer');

    const extractMarket = (h2hKey: string, spreadsKey: string, totalsKey: string) => {
      const h2hM = marketsByKey[h2hKey];
      const spreadsM = marketsByKey[spreadsKey];
      const totalsM = marketsByKey[totalsKey];
      const out: any = { h2h: null, spreads: null, totals: null };

      if (h2hM) {
        const home = h2hM.outcomes.find((o: any) => o.name === gameData.home_team);
        const away = h2hM.outcomes.find((o: any) => o.name === gameData.away_team);
        const draw = h2hM.outcomes.find((o: any) => o.name === 'Draw');
        if (home && away) {
          out.h2h = {
            home: { price: home.price },
            away: { price: away.price },
            draw: draw ? { price: draw.price } : undefined,
          };
        }
      }
      if (spreadsM) {
        const home = spreadsM.outcomes.find((o: any) => o.name === gameData.home_team);
        const away = spreadsM.outcomes.find((o: any) => o.name === gameData.away_team);
        if (home && away) {
          out.spreads = {
            home: { line: home.point, price: home.price },
            away: { line: away.point, price: away.price },
          };
        }
      }
      if (totalsM) {
        const over = totalsM.outcomes.find((o: any) => o.name === 'Over');
        const under = totalsM.outcomes.find((o: any) => o.name === 'Under');
        if (over) {
          out.totals = {
            line: over.point,
            over: { price: over.price },
            under: { price: under?.price },
          };
        }
      }
      return out;
    };

    // Team totals
    let teamTotals: any = null;
    if (marketsByKey['team_totals']) {
      teamTotals = { home: { over: null, under: null }, away: { over: null, under: null } };
      for (const o of marketsByKey['team_totals'].outcomes) {
        const isHome = o.description === gameData.home_team;
        const isAway = o.description === gameData.away_team;
        const team = isHome ? 'home' : isAway ? 'away' : null;
        if (team && o.name === 'Over') {
          teamTotals[team].over = { line: o.point, price: o.price };
        } else if (team && o.name === 'Under') {
          teamTotals[team].under = { line: o.point, price: o.price };
        }
      }
    }

    result[bookKey] = {
      marketGroups: {
        fullGame: extractMarket('h2h', 'spreads', 'totals'),
        firstHalf: extractMarket('h2h_h1', 'spreads_h1', 'totals_h1'),
        secondHalf: extractMarket('h2h_h2', 'spreads_h2', 'totals_h2'),
        q1: extractMarket('h2h_q1', 'spreads_q1', 'totals_q1'),
        q2: extractMarket('h2h_q2', 'spreads_q2', 'totals_q2'),
        q3: extractMarket('h2h_q3', 'spreads_q3', 'totals_q3'),
        q4: extractMarket('h2h_q4', 'spreads_q4', 'totals_q4'),
        p1: extractMarket('h2h_p1', 'spreads_p1', 'totals_p1'),
        p2: extractMarket('h2h_p2', 'spreads_p2', 'totals_p2'),
        p3: extractMarket('h2h_p3', 'spreads_p3', 'totals_p3'),
        teamTotals,
      },
    };
  }

  return result;
}

// Calculate edge count for a single game - SAME logic as game detail page
async function calculateGameEdgeCount(gameId: string): Promise<number> {
  // Fetch game data
  const cached = await fetchGameData(gameId);
  if (!cached) return 0;

  const { sportKey, gameData } = cached;
  const homeTeam = gameData.home_team;
  const awayTeam = gameData.away_team;

  // Fetch required data in parallel
  // PERF: Skip fetchGameContext for edge counting - it's expensive and not essential for counts
  const [openingLine, snapshots] = await Promise.all([
    fetchOpeningLine(gameId),
    fetchSnapshots(gameId),
  ]);
  const gameContext = {}; // Empty context is fine for edge counting

  // Build bookmakers with marketGroups
  const bookmakers = buildPerBookMarketGroups(gameData);
  if (Object.keys(bookmakers).length === 0) return 0;

  // Helper to calculate CEQ for a period - SAME as game detail page
  const calculatePeriodCEQ = (periodKey: string): GameCEQ | null => {
    const periodMarkets = Object.values(bookmakers)
      .map((b: any) => b.marketGroups?.[periodKey])
      .filter(Boolean);

    if (periodMarkets.length === 0) return null;

    const getMedian = (values: number[]) => {
      if (values.length === 0) return undefined;
      const sorted = [...values].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };

    // Collect data from all bookmakers
    const spreadLines: number[] = [];
    const spreadHomeOdds: number[] = [];
    const spreadAwayOdds: number[] = [];
    const h2hHomeOdds: number[] = [];
    const h2hAwayOdds: number[] = [];
    const h2hDrawOdds: number[] = [];
    const totalLines: number[] = [];
    const totalOverOdds: number[] = [];
    const totalUnderOdds: number[] = [];

    for (const markets of periodMarkets) {
      if (markets.spreads?.home?.line !== undefined) spreadLines.push(markets.spreads.home.line);
      if (markets.spreads?.home?.price !== undefined) spreadHomeOdds.push(markets.spreads.home.price);
      if (markets.spreads?.away?.price !== undefined) spreadAwayOdds.push(markets.spreads.away.price);
      if (markets.h2h?.home?.price !== undefined) h2hHomeOdds.push(markets.h2h.home.price);
      if (markets.h2h?.away?.price !== undefined) h2hAwayOdds.push(markets.h2h.away.price);
      if (markets.h2h?.draw?.price !== undefined) h2hDrawOdds.push(markets.h2h.draw.price);
      if (markets.totals?.line !== undefined) totalLines.push(markets.totals.line);
      if (markets.totals?.over?.price !== undefined) totalOverOdds.push(markets.totals.over.price);
      if (markets.totals?.under?.price !== undefined) totalUnderOdds.push(markets.totals.under.price);
    }

    const periodSpreadLine = getMedian(spreadLines);
    const periodSpreadHomeOdds = getMedian(spreadHomeOdds) || -110;
    const periodSpreadAwayOdds = getMedian(spreadAwayOdds) || -110;
    const periodH2hHome = getMedian(h2hHomeOdds);
    const periodH2hAway = getMedian(h2hAwayOdds);
    const periodH2hDraw = getMedian(h2hDrawOdds);
    const periodTotalLine = getMedian(totalLines);
    const periodTotalOverOdds = getMedian(totalOverOdds) || -110;
    const periodTotalUnderOdds = getMedian(totalUnderOdds) || -110;

    const hasSpread = periodSpreadLine !== undefined;
    const hasH2h = periodH2hHome !== undefined && periodH2hAway !== undefined;
    const hasTotals = periodTotalLine !== undefined;

    if (!hasSpread && !hasH2h && !hasTotals) return null;

    const gameOdds = {
      spreads: hasSpread ? {
        home: { line: periodSpreadLine!, odds: periodSpreadHomeOdds },
        away: { line: -periodSpreadLine!, odds: periodSpreadAwayOdds },
      } : undefined,
      h2h: hasH2h ? {
        home: periodH2hHome!,
        away: periodH2hAway!,
        draw: periodH2hDraw,  // Include draw for soccer 3-way markets
      } : undefined,
      totals: hasTotals ? {
        line: periodTotalLine!,
        over: periodTotalOverOdds,
        under: periodTotalUnderOdds,
      } : undefined,
    };

    // Estimate opening line for periods
    let periodOpeningData: any = {};
    if (openingLine !== undefined) {
      if (periodKey === 'fullGame') {
        periodOpeningData = { spreads: { home: openingLine, away: -openingLine } };
      } else if (periodKey === 'firstHalf' || periodKey === 'secondHalf') {
        const halfOpeningLine = openingLine * 0.5;
        periodOpeningData = { spreads: { home: halfOpeningLine, away: -halfOpeningLine } };
      } else if (periodKey.startsWith('q')) {
        const quarterOpeningLine = openingLine * 0.25;
        periodOpeningData = { spreads: { home: quarterOpeningLine, away: -quarterOpeningLine } };
      } else if (periodKey.startsWith('p')) {
        const periodOpeningLineValue = openingLine * 0.33;
        periodOpeningData = { spreads: { home: periodOpeningLineValue, away: -periodOpeningLineValue } };
      }
    }

    // Filter snapshots for this period
    const marketSuffix = periodKey === 'fullGame' ? '' :
                        periodKey === 'firstHalf' ? '_h1' :
                        periodKey === 'secondHalf' ? '_h2' :
                        periodKey.startsWith('q') ? `_${periodKey}` :
                        periodKey.startsWith('p') ? `_${periodKey}` : '';
    const periodSnapshots = marketSuffix
      ? snapshots.filter(s => s.market?.endsWith(marketSuffix))
      : snapshots.filter(s => !s.market?.includes('_'));

    return calculateGameCEQ(
      gameOdds,
      periodOpeningData,
      periodSnapshots,
      {
        spreads: hasSpread ? { home: spreadHomeOdds, away: spreadAwayOdds } : undefined,
        h2h: hasH2h ? { home: h2hHomeOdds, away: h2hAwayOdds } : undefined,
        totals: hasTotals ? { over: totalOverOdds, under: totalUnderOdds } : undefined,
      },
      {
        spreads: hasSpread ? { home: periodSpreadHomeOdds, away: periodSpreadAwayOdds } : undefined,
        h2h: hasH2h ? { home: periodH2hHome, away: periodH2hAway } : undefined,
        totals: hasTotals ? { over: periodTotalOverOdds, under: periodTotalUnderOdds } : undefined,
      },
      gameContext
    );
  };

  // Calculate CEQ for all periods
  const ceqByPeriod: Record<string, GameCEQ | null> = {
    fullGame: calculatePeriodCEQ('fullGame'),
    firstHalf: calculatePeriodCEQ('firstHalf'),
    secondHalf: calculatePeriodCEQ('secondHalf'),
    q1: calculatePeriodCEQ('q1'),
    q2: calculatePeriodCEQ('q2'),
    q3: calculatePeriodCEQ('q3'),
    q4: calculatePeriodCEQ('q4'),
    p1: calculatePeriodCEQ('p1'),
    p2: calculatePeriodCEQ('p2'),
    p3: calculatePeriodCEQ('p3'),
  };


  // Calculate team totals CEQ
  let teamTotalsEdges = 0;
  const firstBook = Object.values(bookmakers)[0] as any;
  const teamTotals = firstBook?.marketGroups?.teamTotals;
  if (teamTotals) {
    const calcTeamTotalCEQ = (teamData: any): GameCEQ | null => {
      if (!teamData?.over?.line) return null;
      const teamGameOdds = {
        totals: {
          line: teamData.over.line,
          over: teamData.over.price || -110,
          under: teamData.under?.price || -110,
        },
      };
      return calculateGameCEQ(teamGameOdds, {}, [], {}, {
        totals: { over: teamData.over.price || -110, under: teamData.under?.price || -110 },
      }, gameContext);
    };

    const homeCeq = calcTeamTotalCEQ(teamTotals.home);
    const awayCeq = calcTeamTotalCEQ(teamTotals.away);

    if (homeCeq?.totals?.over?.ceq !== undefined && homeCeq.totals.over.ceq >= 56) teamTotalsEdges++;
    if (homeCeq?.totals?.under?.ceq !== undefined && homeCeq.totals.under.ceq >= 56) teamTotalsEdges++;
    if (awayCeq?.totals?.over?.ceq !== undefined && awayCeq.totals.over.ceq >= 56) teamTotalsEdges++;
    if (awayCeq?.totals?.under?.ceq !== undefined && awayCeq.totals.under.ceq >= 56) teamTotalsEdges++;
  }

  // Count total edges - SAME as game detail page
  let totalEdgeCount = 0;
  totalEdgeCount += countPeriodEdges(ceqByPeriod.fullGame);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.firstHalf);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.secondHalf);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.q1);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.q2);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.q3);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.q4);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.p1);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.p2);
  totalEdgeCount += countPeriodEdges(ceqByPeriod.p3);
  totalEdgeCount += teamTotalsEdges;

  return totalEdgeCount;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const gameIds: string[] = body.gameIds || [];

    if (gameIds.length === 0) {
      return NextResponse.json({ counts: {} });
    }

    // Limit to 50 games per request for performance
    const limitedGameIds = gameIds.slice(0, 50);

    // Calculate edge counts in parallel (with concurrency limit)
    const BATCH_SIZE = 10;
    const counts: Record<string, number> = {};

    for (let i = 0; i < limitedGameIds.length; i += BATCH_SIZE) {
      const batch = limitedGameIds.slice(i, i + BATCH_SIZE);
      const results = await Promise.all(
        batch.map(async (gameId) => {
          try {
            const count = await calculateGameEdgeCount(gameId);
            return { gameId, count };
          } catch (err) {
            console.error(`[game-counts API] Error calculating ${gameId}:`, err);
            return { gameId, count: 0 };
          }
        })
      );

      for (const { gameId, count } of results) {
        counts[gameId] = count;
      }
    }

    return NextResponse.json({ counts });
  } catch (error) {
    console.error('[game-counts API] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Also support GET with query param for single game
export async function GET(request: NextRequest) {
  const gameId = request.nextUrl.searchParams.get('gameId');

  if (!gameId) {
    return NextResponse.json({ error: 'gameId required' }, { status: 400 });
  }

  try {
    const count = await calculateGameEdgeCount(gameId);
    return NextResponse.json({ gameId, count });
  } catch (error) {
    console.error('[game-counts API] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
