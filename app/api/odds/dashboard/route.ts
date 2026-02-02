import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { calculateGameCEQ, type ExtendedOddsSnapshot, type GameCEQ, type GameContextData, type TeamStatsData } from '@/lib/edge/engine/edgescout';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';
import { calculateTwoWayEV } from '@/lib/edge/utils/odds-math';

const ODDS_API_KEY = process.env.ODDS_API_KEY || '';
const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

const SPORT_KEYS = [
  // American Football
  'americanfootball_nfl',
  'americanfootball_ncaaf',
  // Basketball
  'basketball_nba',
  'basketball_ncaab',
  'basketball_wnba',
  'basketball_euroleague',
  // Hockey
  'icehockey_nhl',
  'icehockey_ahl',
  'icehockey_sweden_hockey_league',
  'icehockey_liiga',
  // Baseball
  'baseball_mlb',
  // Soccer
  'soccer_usa_mls',
  'soccer_epl',
  'soccer_spain_la_liga',
  'soccer_germany_bundesliga',
  'soccer_italy_serie_a',
  'soccer_france_ligue_one',
  'soccer_uefa_champs_league',
  'soccer_uefa_europa_league',
  'soccer_efl_champ',
  'soccer_netherlands_eredivisie',
  'soccer_mexico_ligamx',
  'soccer_fa_cup',
  // Tennis
  'tennis_atp_australian_open',
  'tennis_atp_french_open',
  'tennis_atp_us_open',
  'tennis_atp_wimbledon',
  // Golf
  'golf_masters_tournament_winner',
  'golf_pga_championship_winner',
  'golf_us_open_winner',
  'golf_the_open_championship_winner',
  // Combat Sports
  'mma_mixed_martial_arts',
  'boxing_boxing',
  // Other
  'rugbyleague_nrl',
  'aussierules_afl',
  'cricket_ipl',
  'cricket_big_bash',
];

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

// Fetch snapshots for CEQ - no time limit to match game detail
async function fetchGameSnapshots(gameIds: string[]): Promise<Record<string, ExtendedOddsSnapshot[]>> {
  const snapshotsMap: Record<string, ExtendedOddsSnapshot[]> = {};
  if (gameIds.length === 0) return snapshotsMap;

  try {
    const supabase = getSupabase();

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

// Live edge type from live_edges table
interface LiveEdge {
  id: string;
  game_id: string;
  sport: string;
  market_type: string;       // 'h2h', 'spreads', 'totals'
  outcome_key: string;       // team name, 'Over', 'Under'
  edge_type: string;
  edge_magnitude: number;
  confidence: number | null;
  status: string;            // 'active', 'fading', 'expired'
  detected_at: string;
  triggering_book?: string;
  best_current_book?: string;
}

// Fetch live edges for all games
async function fetchLiveEdges(gameIds: string[]): Promise<Record<string, LiveEdge[]>> {
  const edgesMap: Record<string, LiveEdge[]> = {};
  if (gameIds.length === 0) return edgesMap;

  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('live_edges')
      .select('*')
      .in('game_id', gameIds)
      .in('status', ['active', 'fading'])
      .order('detected_at', { ascending: false });

    if (error || !data) return edgesMap;

    // Group edges by game_id
    for (const edge of data) {
      if (!edgesMap[edge.game_id]) {
        edgesMap[edge.game_id] = [];
      }
      edgesMap[edge.game_id].push(edge);
    }
  } catch (e) {
    console.error('[Dashboard API] Live edges fetch failed:', e);
  }

  return edgesMap;
}

// Build consensus from bookmakers - EXACT same function as game detail page
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

// Helper to count edges from a CEQ result (same logic as game detail page)
function countCEQEdges(ceq: GameCEQ | null): number {
  if (!ceq) return 0;
  let count = 0;
  // Spreads: home and away are separate edges
  if (ceq.spreads?.home?.ceq !== undefined && ceq.spreads.home.ceq >= 56) count++;
  if (ceq.spreads?.away?.ceq !== undefined && ceq.spreads.away.ceq >= 56) count++;
  // H2H/Moneyline: home and away are separate edges
  if (ceq.h2h?.home?.ceq !== undefined && ceq.h2h.home.ceq >= 56) count++;
  if (ceq.h2h?.away?.ceq !== undefined && ceq.h2h.away.ceq >= 56) count++;
  // Totals: over and under are separate edges
  if (ceq.totals?.over?.ceq !== undefined && ceq.totals.over.ceq >= 56) count++;
  if (ceq.totals?.under?.ceq !== undefined && ceq.totals.under.ceq >= 56) count++;
  return count;
}

// Helper to build consensus for a specific period from bookmakers
function buildPeriodConsensus(game: any, h2hKey: string, spreadsKey: string, totalsKey: string) {
  const bookmakers = game.bookmakers;
  if (!bookmakers || bookmakers.length === 0) return null;

  const h2h: { home: number[]; away: number[] } = { home: [], away: [] };
  const spreads: { homeLine: number[]; homeOdds: number[]; awayOdds: number[] } = { homeLine: [], homeOdds: [], awayOdds: [] };
  const totals: { line: number[]; overOdds: number[]; underOdds: number[] } = { line: [], overOdds: [], underOdds: [] };

  for (const bk of bookmakers) {
    for (const market of bk.markets) {
      if (market.key === h2hKey) {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        if (home) h2h.home.push(home.price);
        if (away) h2h.away.push(away.price);
      }
      if (market.key === spreadsKey) {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        if (home?.point !== undefined) {
          spreads.homeLine.push(home.point);
          spreads.homeOdds.push(home.price);
        }
        if (away) spreads.awayOdds.push(away.price);
      }
      if (market.key === totalsKey) {
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

  const hasData = h2h.home.length > 0 || spreads.homeLine.length > 0 || totals.line.length > 0;
  if (!hasData) return null;

  return {
    h2h: h2h.home.length > 0 ? { homePrice: median(h2h.home), awayPrice: median(h2h.away) } : undefined,
    spreads: spreads.homeLine.length > 0 ? {
      line: median(spreads.homeLine),
      homePrice: median(spreads.homeOdds),
      awayPrice: median(spreads.awayOdds)
    } : undefined,
    totals: totals.line.length > 0 ? {
      line: median(totals.line),
      overPrice: median(totals.overOdds),
      underPrice: median(totals.underOdds)
    } : undefined,
  };
}

// Helper to build team totals consensus
function buildTeamTotalsConsensus(game: any) {
  const bookmakers = game.bookmakers;
  if (!bookmakers || bookmakers.length === 0) return null;

  const homeOver: { line: number[]; odds: number[] } = { line: [], odds: [] };
  const homeUnder: { odds: number[] } = { odds: [] };
  const awayOver: { line: number[]; odds: number[] } = { line: [], odds: [] };
  const awayUnder: { odds: number[] } = { odds: [] };

  for (const bk of bookmakers) {
    for (const market of bk.markets) {
      if (market.key === 'team_totals') {
        for (const o of market.outcomes) {
          const isHome = o.description === game.home_team;
          const isAway = o.description === game.away_team;
          if (isHome && o.name === 'Over' && o.point !== undefined) {
            homeOver.line.push(o.point);
            homeOver.odds.push(o.price);
          } else if (isHome && o.name === 'Under') {
            homeUnder.odds.push(o.price);
          } else if (isAway && o.name === 'Over' && o.point !== undefined) {
            awayOver.line.push(o.point);
            awayOver.odds.push(o.price);
          } else if (isAway && o.name === 'Under') {
            awayUnder.odds.push(o.price);
          }
        }
      }
    }
  }

  const median = (arr: number[]) => {
    if (arr.length === 0) return undefined;
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  };

  const hasData = homeOver.line.length > 0 || awayOver.line.length > 0;
  if (!hasData) return null;

  return {
    home: homeOver.line.length > 0 ? {
      line: median(homeOver.line),
      overPrice: median(homeOver.odds),
      underPrice: median(homeUnder.odds),
    } : undefined,
    away: awayOver.line.length > 0 ? {
      line: median(awayOver.line),
      overPrice: median(awayOver.odds),
      underPrice: median(awayUnder.odds),
    } : undefined,
  };
}

function processGame(
  game: any,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>,
  edgesMap: Record<string, LiveEdge[]>
) {
  // Use EXACT same consensus building as game detail page
  const consensus = buildConsensusFromBookmakers(game);

  // Get live edges for this game
  const liveEdges = edgesMap[game.id] || [];

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
  const openingLine = openingLines[game.id];

  const gameContext = buildGameContext(
    game.home_team,
    game.away_team,
    game.sport_key,
    teamStatsMap
  );

  // EXACT SAME normalizer functions as game detail page
  // Handle both backend format and cached format
  const getSpreadLine = () => {
    if (consensus.spreads?.home?.line !== undefined) return consensus.spreads.home.line;
    if (consensus.spreads?.line !== undefined) return consensus.spreads.line;
    return undefined;
  };
  const getSpreadHomeOdds = () => consensus.spreads?.home?.odds || consensus.spreads?.homePrice || -110;
  const getSpreadAwayOdds = () => consensus.spreads?.away?.odds || consensus.spreads?.awayPrice || -110;
  const getH2hHome = () => consensus.h2h?.home?.price || consensus.h2h?.home || consensus.h2h?.homePrice;
  const getH2hAway = () => consensus.h2h?.away?.price || consensus.h2h?.away || consensus.h2h?.awayPrice;
  const getTotalLine = () => consensus.totals?.over?.line || consensus.totals?.line;
  const getTotalOverOdds = () => consensus.totals?.over?.odds || consensus.totals?.overPrice || -110;
  const getTotalUnderOdds = () => consensus.totals?.under?.odds || consensus.totals?.underPrice || -110;

  const spreadLine = getSpreadLine();
  const hasSpread = spreadLine !== undefined;
  const hasH2h = getH2hHome() !== undefined;
  const hasTotals = getTotalLine() !== undefined;

  // EXACT SAME gameOdds structure as game detail page
  let ceqData: GameCEQ | null = null;
  if (hasSpread || hasH2h || hasTotals) {
    const gameOdds = {
      spreads: hasSpread ? {
        home: { line: spreadLine, odds: getSpreadHomeOdds() },
        away: { line: -spreadLine, odds: getSpreadAwayOdds() },
      } : undefined,
      h2h: hasH2h ? {
        home: getH2hHome(),
        away: getH2hAway(),
      } : undefined,
      totals: hasTotals ? {
        line: getTotalLine(),
        over: getTotalOverOdds(),
        under: getTotalUnderOdds(),
      } : undefined,
    };

    // EXACT SAME openingData structure as game detail page
    const openingData = {
      spreads: openingLine !== undefined ? {
        home: openingLine,
        away: -openingLine,
      } : undefined,
    };

    // EXACT SAME calculateGameCEQ call as game detail page
    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      gameSnapshots,
      {}, // Empty allBooksOdds - matches game detail
      {
        spreads: hasSpread ? { home: getSpreadHomeOdds(), away: getSpreadAwayOdds() } : undefined,
        h2h: hasH2h ? { home: getH2hHome(), away: getH2hAway() } : undefined,
        totals: hasTotals ? { over: getTotalOverOdds(), under: getTotalUnderOdds() } : undefined,
      },
      gameContext
    );
  }

  // Use same CEQ for all books (consensus-based)
  const ceqByBook: Record<string, GameCEQ | null> = {};
  for (const bookKey of Object.keys(bookmakers)) {
    ceqByBook[bookKey] = ceqData;
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

  // Calculate CEQ for ALL periods (same as game detail page)
  // This gives us comprehensive edge count across Full Game, 1H, 2H, Q1-Q4, Team Totals
  const calculatePeriodCEQ = (periodConsensus: any, periodOpeningLine?: number): GameCEQ | null => {
    if (!periodConsensus) return null;

    const spreadLine = periodConsensus.spreads?.line;
    const hasSpread = spreadLine !== undefined;
    const hasH2h = periodConsensus.h2h?.homePrice !== undefined;
    const hasTotals = periodConsensus.totals?.line !== undefined;

    if (!hasSpread && !hasH2h && !hasTotals) return null;

    const periodGameOdds = {
      spreads: hasSpread ? {
        home: { line: spreadLine, odds: periodConsensus.spreads?.homePrice || -110 },
        away: { line: -spreadLine, odds: periodConsensus.spreads?.awayPrice || -110 },
      } : undefined,
      h2h: hasH2h ? {
        home: periodConsensus.h2h.homePrice,
        away: periodConsensus.h2h.awayPrice,
      } : undefined,
      totals: hasTotals ? {
        line: periodConsensus.totals.line,
        over: periodConsensus.totals.overPrice || -110,
        under: periodConsensus.totals.underPrice || -110,
      } : undefined,
    };

    const periodOpeningData = periodOpeningLine !== undefined ? {
      spreads: { home: periodOpeningLine, away: -periodOpeningLine },
    } : {};

    return calculateGameCEQ(
      periodGameOdds,
      periodOpeningData,
      [], // No snapshots for periods on dashboard (performance)
      {},
      {
        spreads: hasSpread ? { home: periodConsensus.spreads?.homePrice || -110, away: periodConsensus.spreads?.awayPrice || -110 } : undefined,
        h2h: hasH2h ? { home: periodConsensus.h2h.homePrice, away: periodConsensus.h2h.awayPrice } : undefined,
        totals: hasTotals ? { over: periodConsensus.totals.overPrice || -110, under: periodConsensus.totals.underPrice || -110 } : undefined,
      },
      gameContext
    );
  };

  // Build period consensus and calculate CEQ for each period
  const periodConsensusData: Record<string, any> = {
    fullGame: consensus,
    firstHalf: buildPeriodConsensus(game, 'h2h_h1', 'spreads_h1', 'totals_h1'),
    secondHalf: buildPeriodConsensus(game, 'h2h_h2', 'spreads_h2', 'totals_h2'),
    q1: buildPeriodConsensus(game, 'h2h_q1', 'spreads_q1', 'totals_q1'),
    q2: buildPeriodConsensus(game, 'h2h_q2', 'spreads_q2', 'totals_q2'),
    q3: buildPeriodConsensus(game, 'h2h_q3', 'spreads_q3', 'totals_q3'),
    q4: buildPeriodConsensus(game, 'h2h_q4', 'spreads_q4', 'totals_q4'),
    p1: buildPeriodConsensus(game, 'h2h_p1', 'spreads_p1', 'totals_p1'),
    p2: buildPeriodConsensus(game, 'h2h_p2', 'spreads_p2', 'totals_p2'),
    p3: buildPeriodConsensus(game, 'h2h_p3', 'spreads_p3', 'totals_p3'),
  };

  // Calculate opening lines for periods (estimate from full game)
  const periodOpeningLines: Record<string, number | undefined> = {
    fullGame: openingLine,
    firstHalf: openingLine !== undefined ? openingLine * 0.5 : undefined,
    secondHalf: openingLine !== undefined ? openingLine * 0.5 : undefined,
    q1: openingLine !== undefined ? openingLine * 0.25 : undefined,
    q2: openingLine !== undefined ? openingLine * 0.25 : undefined,
    q3: openingLine !== undefined ? openingLine * 0.25 : undefined,
    q4: openingLine !== undefined ? openingLine * 0.25 : undefined,
    p1: openingLine !== undefined ? openingLine * 0.33 : undefined,
    p2: openingLine !== undefined ? openingLine * 0.33 : undefined,
    p3: openingLine !== undefined ? openingLine * 0.33 : undefined,
  };

  // Calculate CEQ for each period
  const ceqByPeriod: Record<string, GameCEQ | null> = {
    fullGame: ceqData, // Already calculated above
    firstHalf: calculatePeriodCEQ(periodConsensusData.firstHalf, periodOpeningLines.firstHalf),
    secondHalf: calculatePeriodCEQ(periodConsensusData.secondHalf, periodOpeningLines.secondHalf),
    q1: calculatePeriodCEQ(periodConsensusData.q1, periodOpeningLines.q1),
    q2: calculatePeriodCEQ(periodConsensusData.q2, periodOpeningLines.q2),
    q3: calculatePeriodCEQ(periodConsensusData.q3, periodOpeningLines.q3),
    q4: calculatePeriodCEQ(periodConsensusData.q4, periodOpeningLines.q4),
    p1: calculatePeriodCEQ(periodConsensusData.p1, periodOpeningLines.p1),
    p2: calculatePeriodCEQ(periodConsensusData.p2, periodOpeningLines.p2),
    p3: calculatePeriodCEQ(periodConsensusData.p3, periodOpeningLines.p3),
  };

  // Calculate team totals CEQ
  const teamTotalsConsensus = buildTeamTotalsConsensus(game);
  let teamTotalsCeq: { home: GameCEQ | null; away: GameCEQ | null } | null = null;
  if (teamTotalsConsensus) {
    const calcTeamTotalCEQ = (teamData: any): GameCEQ | null => {
      if (!teamData?.line) return null;
      const teamGameOdds = {
        totals: {
          line: teamData.line,
          over: teamData.overPrice || -110,
          under: teamData.underPrice || -110,
        },
      };
      return calculateGameCEQ(teamGameOdds, {}, [], {}, {
        totals: { over: teamData.overPrice || -110, under: teamData.underPrice || -110 },
      }, gameContext);
    };
    teamTotalsCeq = {
      home: calcTeamTotalCEQ(teamTotalsConsensus.home),
      away: calcTeamTotalCEQ(teamTotalsConsensus.away),
    };
  }

  // Count TOTAL edges across ALL periods (same logic as game detail page)
  let totalEdgeCount = 0;
  totalEdgeCount += countCEQEdges(ceqByPeriod.fullGame);
  totalEdgeCount += countCEQEdges(ceqByPeriod.firstHalf);
  totalEdgeCount += countCEQEdges(ceqByPeriod.secondHalf);
  totalEdgeCount += countCEQEdges(ceqByPeriod.q1);
  totalEdgeCount += countCEQEdges(ceqByPeriod.q2);
  totalEdgeCount += countCEQEdges(ceqByPeriod.q3);
  totalEdgeCount += countCEQEdges(ceqByPeriod.q4);
  totalEdgeCount += countCEQEdges(ceqByPeriod.p1);
  totalEdgeCount += countCEQEdges(ceqByPeriod.p2);
  totalEdgeCount += countCEQEdges(ceqByPeriod.p3);

  // Count team totals edges (4 possible: home over, home under, away over, away under)
  if (teamTotalsCeq?.home?.totals?.over?.ceq !== undefined && teamTotalsCeq.home.totals.over.ceq >= 56) totalEdgeCount++;
  if (teamTotalsCeq?.home?.totals?.under?.ceq !== undefined && teamTotalsCeq.home.totals.under.ceq >= 56) totalEdgeCount++;
  if (teamTotalsCeq?.away?.totals?.over?.ceq !== undefined && teamTotalsCeq.away.totals.over.ceq >= 56) totalEdgeCount++;
  if (teamTotalsCeq?.away?.totals?.under?.ceq !== undefined && teamTotalsCeq.away.totals.under.ceq >= 56) totalEdgeCount++;

  // Check for valid edge - PRIMARY: check live_edges, FALLBACK: CEQ >= 56
  const hasValidEdge = totalEdgeCount > 0;

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
    ceqByBook,
    ceqByPeriod,  // Include period CEQ for frontend
    teamTotalsCeq, // Include team totals CEQ
    totalEdgeCount, // Total edges across all periods
    scores: scores[game.id] || null,
    hasValidEdge,
    liveEdges,  // Include pre-detected edges for frontend to use directly
  };
}

export async function GET() {
  const startTime = Date.now();

  try {
    const supabase = getSupabase();

    // Fetch all cached odds - use explicit limit to ensure we get all rows
    const { data: allCachedData, error, count } = await supabase
      .from('cached_odds')
      .select('sport_key, game_data, updated_at', { count: 'exact' })
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
    const [scores, openingLines, snapshotsMap, teamStatsMap, edgesMap] = await Promise.all([
      fetchLiveScores(),
      fetchOpeningLines(gameIds),
      fetchGameSnapshots(gameIds),
      fetchAllTeamStats(),
      fetchLiveEdges(gameIds),
    ]);

    // Process games by sport
    const allGames: Record<string, any[]> = {};
    let totalGames = 0;
    let totalEdges = 0;
    const now = new Date();

    for (const sportKey of SPORT_KEYS) {
      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];

      const processedGames = sportData
        .map((row: any) => processGame(row.game_data, scores, openingLines, snapshotsMap, teamStatsMap, edgesMap))
        .filter(Boolean);

      const fourHoursAgo = now.getTime() - 4 * 60 * 60 * 1000;

      const games = processedGames
        // Keep future games AND games that started within last 4 hours (live/recently finished)
        .filter((g: any) => new Date(g.commenceTime).getTime() > fourHoursAgo)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      // Debug logging for NBA (minimal)
      if (sportKey === 'basketball_nba') {
        console.log(`[Dashboard API] NBA: ${sportData.length} cached -> ${processedGames.length} processed -> ${games.length} after filter`);
      }

      if (games.length > 0) {
        allGames[sportKey] = games;
        totalGames += games.length;
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
