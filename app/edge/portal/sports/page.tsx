import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';
import { calculateCEQ, calculateGameCEQ, groupSnapshotsByGame, type ExtendedOddsSnapshot, type GameCEQ, type GameContextData, type TeamStatsData } from '@/lib/edge/engine/edgescout';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const SPORT_MAPPING: Record<string, string> = {
  // American Football
  'NFL': 'americanfootball_nfl',
  'NCAAF': 'americanfootball_ncaaf',
  // Basketball
  'NBA': 'basketball_nba',
  'NCAAB': 'basketball_ncaab',
  'WNBA': 'basketball_wnba',
  'EUROLEAGUE': 'basketball_euroleague',
  // Hockey
  'NHL': 'icehockey_nhl',
  'AHL': 'icehockey_ahl',
  'SHL': 'icehockey_sweden_hockey_league',
  'LIIGA': 'icehockey_liiga',
  // Baseball
  'MLB': 'baseball_mlb',
  // Soccer
  'MLS': 'soccer_usa_mls',
  'EPL': 'soccer_epl',
  'LA_LIGA': 'soccer_spain_la_liga',
  'BUNDESLIGA': 'soccer_germany_bundesliga',
  'SERIE_A': 'soccer_italy_serie_a',
  'LIGUE_1': 'soccer_france_ligue_one',
  'UCL': 'soccer_uefa_champs_league',
  'EUROPA': 'soccer_uefa_europa_league',
  'EFL_CHAMP': 'soccer_efl_champ',
  'EREDIVISIE': 'soccer_netherlands_eredivisie',
  'LIGA_MX': 'soccer_mexico_ligamx',
  'FA_CUP': 'soccer_fa_cup',
  // Tennis
  'TENNIS_AO': 'tennis_atp_australian_open',
  'TENNIS_FO': 'tennis_atp_french_open',
  'TENNIS_USO': 'tennis_atp_us_open',
  'TENNIS_WIM': 'tennis_atp_wimbledon',
  // Golf
  'MASTERS': 'golf_masters_tournament_winner',
  'PGA_CHAMP': 'golf_pga_championship_winner',
  'US_OPEN': 'golf_us_open_winner',
  'THE_OPEN': 'golf_the_open_championship_winner',
  // Combat Sports
  'MMA': 'mma_mixed_martial_arts',
  'BOXING': 'boxing_boxing',
  // Other
  'NRL': 'rugbyleague_nrl',
  'AFL': 'aussierules_afl',
  'IPL': 'cricket_ipl',
  'BIG_BASH': 'cricket_big_bash',
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
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: {
        fetch: (url, options) => fetch(url, { ...options, cache: 'no-store' }),
      },
    }
  );
}

// ESPN scoreboard endpoints (free, no API key)
// Only in-season sports — avoids wasted calls
const ESPN_SCORE_ENDPOINTS: Record<string, string> = {
  NBA: 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
  NHL: 'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard',
  NCAAB: 'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
  EPL: 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard',
};

// Map ESPN team names to Odds API game IDs via cached_odds
// Returns scores keyed by Odds API game_id for compatibility
async function fetchLiveScores(): Promise<Record<string, any>> {
  const scores: Record<string, any> = {};

  try {
    // Fetch ESPN scoreboards in parallel (free, cached 5 min)
    const entries = Object.entries(ESPN_SCORE_ENDPOINTS);
    const results = await Promise.all(
      entries.map(async ([, url]) => {
        try {
          const res = await fetch(url, { next: { revalidate: 300 } });
          if (!res.ok) return [];
          const data = await res.json();
          return data.events || [];
        } catch {
          return [];
        }
      })
    );

    // Build team-name-to-score lookup from ESPN data
    // Key: "hometeam_normalized|awayteam_normalized" -> score data
    const teamScores = new Map<string, { home: number; away: number; completed: boolean }>();

    for (const events of results) {
      for (const event of events) {
        try {
          const comp = event.competitions?.[0];
          if (!comp) continue;
          const statusName = comp.status?.type?.name || '';
          const isFinal = statusName === 'STATUS_FINAL';
          const isLive = statusName === 'STATUS_IN_PROGRESS';
          if (!isFinal && !isLive) continue;

          const competitors = comp.competitors || [];
          if (competitors.length !== 2) continue;

          let homeTeam = '', awayTeam = '';
          let homeScore = 0, awayScore = 0;

          for (const c of competitors) {
            const name = (c.team?.displayName || '').toLowerCase().trim();
            const score = parseInt(c.score || '0') || 0;
            if (c.homeAway === 'home') { homeTeam = name; homeScore = score; }
            else { awayTeam = name; awayScore = score; }
          }

          if (homeTeam && awayTeam) {
            teamScores.set(`${homeTeam}|${awayTeam}`, { home: homeScore, away: awayScore, completed: isFinal });
          }
        } catch { /* skip malformed event */ }
      }
    }

    // Match against cached_odds by team names
    const supabase = getDirectSupabase();
    const { data: cachedGames } = await supabase
      .from('cached_odds')
      .select('game_id, game_data')
      .limit(500);

    for (const row of cachedGames || []) {
      const gd = row.game_data;
      if (!gd?.home_team || !gd?.away_team) continue;
      const home = gd.home_team.toLowerCase().trim();
      const away = gd.away_team.toLowerCase().trim();

      // Direct match
      let match = teamScores.get(`${home}|${away}`);
      // Try partial: ESPN "Indiana Pacers" vs Odds API "Indiana Pacers" should direct-match,
      // but for "Wolverhampton Wanderers" vs "Wolves" we need fuzzy
      if (!match) {
        for (const [key, val] of teamScores) {
          const [espnHome, espnAway] = key.split('|');
          if ((espnHome.includes(home) || home.includes(espnHome)) &&
              (espnAway.includes(away) || away.includes(espnAway))) {
            match = val;
            break;
          }
        }
      }

      if (match) {
        scores[row.game_id] = {
          home: match.home,
          away: match.away,
          completed: match.completed,
          lastUpdate: null,
        };
      }
    }
  } catch (e) {
    console.error('[Scores] ESPN fetch failed:', e);
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

// Fetch live edges for all games
async function fetchLiveEdges(gameIds: string[]): Promise<Record<string, any[]>> {
  const edgesMap: Record<string, any[]> = {};
  if (gameIds.length === 0) return edgesMap;

  try {
    const supabase = getDirectSupabase();
    const { data, error } = await supabase
      .from('live_edges')
      .select('*')
      .in('game_id', gameIds)
      .in('status', ['active', 'fading'])
      .order('detected_at', { ascending: false });

    if (error || !data) return edgesMap;

    for (const edge of data) {
      if (!edgesMap[edge.game_id]) {
        edgesMap[edge.game_id] = [];
      }
      edgesMap[edge.game_id].push(edge);
    }
  } catch (e) {
    console.error('[LiveEdges] Fetch failed:', e);
  }

  return edgesMap;
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

// Edge threshold: game counts as "edge" if max edge >= 3%
const EDGE_THRESHOLD = 3.0;

// American odds → implied probability
function toProb(odds: number): number {
  return odds < 0 ? Math.abs(odds) / (Math.abs(odds) + 100) : 100 / (odds + 100);
}

// Calculate max edge % for a game using composite fair lines vs book consensus
// Same formulas as edgescout.ts / GameDetailClient / dashboard API
function calculateMaxEdge(
  fairLines: { fair_spread: number | null; fair_total: number | null; fair_ml_home: number | null; fair_ml_away: number | null },
  consensus: any
): number {
  let maxEdge = 0;

  if (fairLines.fair_spread != null && consensus.spreads?.line !== undefined) {
    maxEdge = Math.max(maxEdge, Math.abs(fairLines.fair_spread - consensus.spreads.line) * 3.0);
  }

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

  if (fairLines.fair_total != null && consensus.totals?.line !== undefined) {
    maxEdge = Math.max(maxEdge, Math.abs(fairLines.fair_total - consensus.totals.line) * 3.0);
  }

  return maxEdge;
}

function processBackendGame(
  game: any,
  sport: string,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>,
  edgesMap: Record<string, any[]>,
  fairLinesMap: Record<string, any>
) {
  const liveEdges = edgesMap[game.game_id] || [];
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

  // Build per-book odds data if bookmakers available
  const bookmakers: Record<string, any> = {};
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
      const bookOdds: any = {};
      for (const market of bookmaker.markets || []) {
        if (market.key === 'h2h') {
          const home = market.outcomes?.find((o: any) => o.name === game.home_team);
          const away = market.outcomes?.find((o: any) => o.name === game.away_team);
          if (home) h2hPrices.home.push(home.price);
          if (away) h2hPrices.away.push(away.price);
          bookOdds.h2h = { homePrice: home?.price, awayPrice: away?.price };
        }
        if (market.key === 'spreads') {
          const home = market.outcomes?.find((o: any) => o.name === game.home_team);
          const away = market.outcomes?.find((o: any) => o.name === game.away_team);
          if (home?.point !== undefined) {
            spreadData.line.push(home.point);
            spreadData.homePrice.push(home.price);
          }
          if (away) spreadData.awayPrice.push(away.price);
          bookOdds.spreads = { line: home?.point, homePrice: home?.price, awayPrice: away?.price };
        }
        if (market.key === 'totals') {
          const over = market.outcomes?.find((o: any) => o.name === 'Over');
          const under = market.outcomes?.find((o: any) => o.name === 'Under');
          if (over?.point !== undefined) {
            totalData.line.push(over.point);
            totalData.overPrice.push(over.price);
          }
          if (under) totalData.underPrice.push(under.price);
          bookOdds.totals = { line: over?.point, overPrice: over?.price, underPrice: under?.price };
        }
      }
      bookmakers[bookmaker.key] = bookOdds;
    }

    if (spreadData.homePrice.length > 0) allBooksOdds.spreads = { home: spreadData.homePrice, away: spreadData.awayPrice };
    if (h2hPrices.home.length > 0) allBooksOdds.h2h = h2hPrices;
    if (totalData.overPrice.length > 0) allBooksOdds.totals = { over: totalData.overPrice, under: totalData.underPrice };
  }

  // Calculate CEQ PER BOOK - each book gets its own CEQ based on its prices
  const ceqByBook: Record<string, GameCEQ | null> = {};

  for (const [bookKey, bookOddsData] of Object.entries(bookmakers)) {
    const bookData = bookOddsData as any;

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
        allBooksOdds,
        {
          spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
          h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
          totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
        },
        gameContext
      );
    }
  }

  // Calculate consensus CEQ (fallback)
  if (gameOdds.spreads || gameOdds.h2h || gameOdds.totals) {
    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      gameSnapshots,
      {},  // Empty for consensus (no SBI comparison needed)
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
    bookmakers,
    bookmakerCount: game.bookmakers?.length || 0,
    edges: game.edges,
    pillars: game.pillars,
    composite_score: game.composite_score || (edgeData.score / 100),
    overall_confidence: game.overall_confidence || edgeData.confidence,
    best_bet: game.best_bet,
    best_edge: game.best_edge,
    calculatedEdge: edgeData,
    ceq: ceqData,
    ceqByBook,  // Per-book CEQ for selected book display
    scores: scores[game.game_id] || null,
    liveEdges,  // Pre-detected edges from live_edges table
    fairLines: fairLinesMap[game.game_id] || null,
  };
}

function processOddsApiGame(
  game: any,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>,
  edgesMap: Record<string, any[]>,
  fairLinesMap: Record<string, any>
) {
  const liveEdges = edgesMap[game.id] || [];
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

  // Calculate CEQ PER BOOK - each book gets its own CEQ based on its prices
  const ceqByBook: Record<string, GameCEQ | null> = {};

  for (const [bookKey, bookOddsData] of Object.entries(bookmakers)) {
    const bookData = bookOddsData as any;

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
        allBooksOdds,
        {
          spreads: consensus.spreads ? { home: consensus.spreads.homePrice, away: consensus.spreads.awayPrice } : undefined,
          h2h: consensus.h2h ? { home: consensus.h2h.homePrice, away: consensus.h2h.awayPrice } : undefined,
          totals: consensus.totals ? { over: consensus.totals.overPrice, under: consensus.totals.underPrice } : undefined,
        },
        gameContext
      );
    }
  }

  // Calculate consensus CEQ (fallback)
  if (gameOdds.spreads || gameOdds.h2h || gameOdds.totals) {
    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      gameSnapshots,
      {},  // Empty for consensus (no SBI comparison needed)
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
    ceq: ceqData,
    ceqByBook,  // Per-book CEQ for selected book display
    scores: scores[game.id] || null,
    liveEdges,  // Pre-detected edges from live_edges table
    fairLines: fairLinesMap[game.id] || null,
  };
}

async function fetchFromCache(
  sportKey: string,
  scores: Record<string, any>,
  openingLines: Record<string, number>,
  snapshotsMap: Record<string, ExtendedOddsSnapshot[]>,
  teamStatsMap: Map<string, TeamStatsData>,
  edgesMap: Record<string, any[]>,
  fairLinesMap: Record<string, any>
) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .eq('sport_key', sportKey);

    if (error || !data) return [];

    return data
      .map((row: any) => processOddsApiGame(row.game_data, scores, openingLines, snapshotsMap, teamStatsMap, edgesMap, fairLinesMap))
      .filter(Boolean);
  } catch (e) {
    console.error(`[Cache] Failed to fetch ${sportKey}:`, e);
    return [];
  }
}

export default async function SportsPage() {
  // All sports that have mappings in SPORT_MAPPING
  const sports = Object.keys(SPORT_MAPPING);
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

  // Also collect cached game IDs for composite_history fetch
  const supabaseForFairLines = getDirectSupabase();
  const allSportKeys = sports.map(s => SPORT_MAPPING[s]).filter(Boolean);
  const { data: cachedForIds } = await supabaseForFairLines
    .from('cached_odds')
    .select('game_data')
    .in('sport_key', allSportKeys);
  const cachedIds = (cachedForIds || []).map((r: any) => r.game_data?.id).filter(Boolean);
  const allKnownGameIds = [...new Set([...allGameIds, ...cachedIds])];

  // Fetch opening lines, snapshots, team stats, live edges, AND composite_history fair lines
  const [openingLines, snapshotsMap, teamStatsMap, edgesMap, fairLinesMap] = await Promise.all([
    fetchOpeningLines(allGameIds),
    fetchGameSnapshots(allGameIds),
    fetchAllTeamStats(),
    fetchLiveEdges(allGameIds),
    (async () => {
      const map: Record<string, any> = {};
      if (allKnownGameIds.length === 0) return map;
      const { data, error } = await supabaseForFairLines
        .from('composite_history')
        .select('game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away')
        .in('game_id', allKnownGameIds)
        .order('timestamp', { ascending: false });
      if (error || !data) return map;
      for (const row of data) {
        if (!map[row.game_id]) {
          map[row.game_id] = {
            fair_spread: row.fair_spread != null ? Number(row.fair_spread) : null,
            fair_total: row.fair_total != null ? Number(row.fair_total) : null,
            fair_ml_home: row.fair_ml_home != null ? Number(row.fair_ml_home) : null,
            fair_ml_away: row.fair_ml_away != null ? Number(row.fair_ml_away) : null,
          };
        }
      }
      return map;
    })(),
  ]);

  // ALWAYS fetch cached_odds for bookmaker data (backend doesn't include it)
  const supabase = getSupabase();
  const sportKeys = sports.map(s => SPORT_MAPPING[s]).filter(Boolean);
  const { data: cachedOddsData } = await supabase
    .from('cached_odds')
    .select('game_id, game_data')
    .in('sport_key', sportKeys);

  // Build map of game_id -> bookmakers from cached_odds
  const bookmakersByGameId: Record<string, any[]> = {};
  if (cachedOddsData) {
    for (const row of cachedOddsData) {
      if (row.game_data?.bookmakers && row.game_id) {
        bookmakersByGameId[row.game_id] = row.game_data.bookmakers;
      }
    }
  }

  // Process backend data for sports that have it
  if (hasBackendData) {
    dataSource = 'backend';
    for (const { sport, games } of backendResults) {
      if (games.length === 0) continue; // Skip sports with no backend data - will get from cache below

      const processed = games
        .map((g: any) => {
          // Inject bookmakers from cached_odds into backend game
          const cachedBookmakers = bookmakersByGameId[g.game_id];
          if (cachedBookmakers) {
            g.bookmakers = cachedBookmakers;
          }
          return processBackendGame(g, sport, scoresData, openingLines, snapshotsMap, teamStatsMap, edgesMap, fairLinesMap);
        })
        .filter(Boolean)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      const frontendKey = SPORT_MAPPING[sport];
      if (processed.length > 0 && frontendKey) {
        allGames[frontendKey] = processed;
        totalGames += processed.length;
        const now7d = Date.now() + 7 * 24 * 60 * 60 * 1000;
        totalEdges += processed.filter((g: any) => {
          if (!g.fairLines) return false;
          if (new Date(g.commenceTime).getTime() > now7d) return false;
          return calculateMaxEdge(g.fairLines, g.consensus) >= EDGE_THRESHOLD;
        }).length;
      }
    }
  }

  // ALWAYS fetch cached_odds for sports not covered by backend (soccer, golf, cricket, etc.)
  {
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

    // Fetch snapshots, live edges, AND opening lines for cached games
    const [cachedSnapshotsMap, cachedEdgesMap, cachedOpeningLines] = cachedGameIds.length > 0
      ? await Promise.all([
          fetchGameSnapshots(cachedGameIds),
          fetchLiveEdges(cachedGameIds),
          fetchOpeningLines(cachedGameIds),
        ])
      : [{}, {}, {}];

    // Process all games directly from the single query result
    const cacheResults: { sport: string; games: any[] }[] = sports.map(sport => {
      const sportKey = SPORT_MAPPING[sport];
      if (!sportKey) return { sport, games: [] };

      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];
      const games = sportData
        .map((row: any) => processOddsApiGame(row.game_data, scoresData, cachedOpeningLines, cachedSnapshotsMap, teamStatsMap, cachedEdgesMap, fairLinesMap))
        .filter(Boolean);
      return { sport, games };
    });

    const hasCachedData = cacheResults.some(r => r.games.length > 0);
    if (hasCachedData && dataSource === 'none') dataSource = 'odds_api';

    for (const { sport, games } of cacheResults) {
      const frontendKey = SPORT_MAPPING[sport];
      // Only add if not already populated from backend
      if (games.length > 0 && frontendKey && !allGames[frontendKey]) {
        const now = new Date();
        const upcoming = games
          .filter((g: any) => new Date(g.commenceTime).getTime() > now.getTime() - 4 * 60 * 60 * 1000)
          .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());
        if (upcoming.length > 0) {
          allGames[frontendKey] = upcoming;
          totalGames += upcoming.length;
          const now7d = Date.now() + 7 * 24 * 60 * 60 * 1000;
          totalEdges += upcoming.filter((g: any) => {
            if (!g.fairLines) return false;
            if (new Date(g.commenceTime).getTime() > now7d) return false;
            return calculateMaxEdge(g.fairLines, g.consensus) >= EDGE_THRESHOLD;
          }).length;
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
