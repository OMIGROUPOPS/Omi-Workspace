import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { enrichExchangeRows } from '@/lib/edge/utils/exchange-enrichment';

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

// ESPN API endpoints (free, no auth needed)
const ESPN_ENDPOINTS: Record<string, string> = {
  'americanfootball_nfl': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
  'americanfootball_ncaaf': 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
  'basketball_nba': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
  'basketball_ncaab': 'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
  'icehockey_nhl': 'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard',
  'soccer_epl': 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard',
};

// Average game durations by sport (hours) — time-based fallback when ESPN unavailable
const SPORT_DURATIONS: Record<string, number> = {
  americanfootball_nfl: 3.5, americanfootball_ncaaf: 3.5,
  basketball_nba: 2.5, basketball_ncaab: 2.5,
  icehockey_nhl: 3, soccer_epl: 2,
};

interface ESPNGame {
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  status: 'scheduled' | 'in_progress' | 'final';
  statusDetail: string;
  period: number;
  clock: string;
}

function normalizeTeam(name: string): string {
  return name.toLowerCase().replace(/\s+/g, ' ').trim();
}

function teamsMatch(a: string, b: string): boolean {
  const na = normalizeTeam(a);
  const nb = normalizeTeam(b);
  if (na === nb) return true;
  if (na.includes(nb) || nb.includes(na)) return true;
  // Match on last word (mascot) if long enough to avoid false positives
  const la = na.split(' ').pop()!;
  const lb = nb.split(' ').pop()!;
  if (la && lb && la.length > 3 && la === lb) return true;
  return false;
}

function findESPNMatch(homeTeam: string, awayTeam: string, espnGames: ESPNGame[]): ESPNGame | null {
  if (!espnGames) return null;
  for (const eg of espnGames) {
    if (teamsMatch(eg.homeTeam, homeTeam) && teamsMatch(eg.awayTeam, awayTeam)) return eg;
    if (teamsMatch(eg.homeTeam, awayTeam) && teamsMatch(eg.awayTeam, homeTeam)) {
      return { ...eg, homeScore: eg.awayScore, awayScore: eg.homeScore };
    }
  }
  return null;
}

// Fetch live scores from ESPN for sports with active games
async function fetchESPNScores(sportKeys: string[]): Promise<Record<string, ESPNGame[]>> {
  const result: Record<string, ESPNGame[]> = {};
  const uniqueSports = [...new Set(sportKeys.filter(k => ESPN_ENDPOINTS[k]))];
  if (uniqueSports.length === 0) return result;

  await Promise.all(uniqueSports.map(async (sportKey) => {
    try {
      let url = ESPN_ENDPOINTS[sportKey];
      if (sportKey.includes('ncaa')) url += '?groups=50&limit=300';
      const res = await fetch(url, { cache: 'no-store' });
      if (!res.ok) return;
      const data = await res.json();

      const games: ESPNGame[] = [];
      for (const event of data.events || []) {
        const comp = event.competitions?.[0];
        if (!comp?.competitors || comp.competitors.length !== 2) continue;
        const statusType = comp.status?.type?.name || '';
        const statusDetail = comp.status?.type?.shortDetail || '';
        let hTeam = '', aTeam = '', hScore = 0, aScore = 0;
        for (const c of comp.competitors) {
          if (c.homeAway === 'home') {
            hTeam = c.team?.displayName || '';
            hScore = parseInt(c.score || '0') || 0;
          } else {
            aTeam = c.team?.displayName || '';
            aScore = parseInt(c.score || '0') || 0;
          }
        }
        games.push({
          homeTeam: hTeam, awayTeam: aTeam,
          homeScore: hScore, awayScore: aScore,
          status: statusType === 'STATUS_FINAL' ? 'final'
                 : statusType === 'STATUS_IN_PROGRESS' ? 'in_progress'
                 : 'scheduled',
          statusDetail, period: comp.status?.period || 0,
          clock: comp.status?.displayClock || '',
        });
      }
      result[sportKey] = games;
      console.log(`[ESPN] ${sportKey}: ${games.length} games (${games.filter(g => g.status === 'in_progress').length} live, ${games.filter(g => g.status === 'final').length} final)`);
    } catch (e) {
      console.error(`[ESPN] ${sportKey} fetch error:`, e);
    }
  }));

  return result;
}

// Fetch graded game results from game_results table
async function fetchGameResults(gameIds: string[]): Promise<Record<string, {
  homeScore: number;
  awayScore: number;
  spreadResult: string | null;
  mlResult: string | null;
  totalResult: string | null;
  finalSpread: number | null;
  finalTotal: number | null;
}>> {
  if (gameIds.length === 0) return {};
  try {
    const supabase = getSupabase();
    const { data } = await supabase
      .from('game_results')
      .select('game_id, home_score, away_score, spread_result, ml_result, total_result, final_spread, final_total')
      .in('game_id', gameIds)
      .not('home_score', 'is', null);

    const results: Record<string, any> = {};
    for (const row of data || []) {
      results[row.game_id] = {
        homeScore: row.home_score,
        awayScore: row.away_score,
        spreadResult: row.spread_result,
        mlResult: row.ml_result,
        totalResult: row.total_result,
        finalSpread: row.final_spread != null ? Number(row.final_spread) : null,
        finalTotal: row.final_total != null ? Number(row.final_total) : null,
      };
    }
    return results;
  } catch (e) {
    console.error('[Dashboard API] Game results fetch failed:', e);
    return {};
  }
}

// Fetch latest composite_history entry per game (single source of truth for fair lines)
async function fetchLatestFairLines(gameIds: string[]): Promise<Record<string, {
  fair_spread: number | null;
  fair_total: number | null;
  fair_ml_home: number | null;
  fair_ml_away: number | null;
  composite_spread: number | null;
  composite_total: number | null;
  composite_ml: number | null;
}>> {
  const fairLines: Record<string, any> = {};
  if (gameIds.length === 0) return fairLines;

  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('composite_history')
      .select('game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away, composite_spread, composite_total, composite_ml')
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
          composite_spread: row.composite_spread != null ? Number(row.composite_spread) : null,
          composite_total: row.composite_total != null ? Number(row.composite_total) : null,
          composite_ml: row.composite_ml != null ? Number(row.composite_ml) : null,
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
  espnData: Record<string, ESPNGame[]>,
  gameResults: Record<string, any>,
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

  // Determine game state and live data
  const commenceTime = new Date(game.commence_time);
  const now = new Date();
  let gameState: 'pregame' | 'live' | 'final' = 'pregame';
  let liveData: any = null;

  // Check graded game_results first (most authoritative)
  const graded = gameResults[game.id];
  if (graded) {
    gameState = 'final';
    liveData = {
      homeScore: graded.homeScore,
      awayScore: graded.awayScore,
      statusDetail: 'Final',
      spreadResult: graded.spreadResult,
      mlResult: graded.mlResult,
      totalResult: graded.totalResult,
      finalSpread: graded.finalSpread,
      finalTotal: graded.finalTotal,
    };
  } else if (now > commenceTime) {
    // Game has started — check ESPN for live/final status
    const espnGames = espnData[game.sport_key] || [];
    const espnMatch = findESPNMatch(game.home_team, game.away_team, espnGames);

    if (espnMatch) {
      if (espnMatch.status === 'final') {
        gameState = 'final';
        liveData = {
          homeScore: espnMatch.homeScore,
          awayScore: espnMatch.awayScore,
          statusDetail: espnMatch.statusDetail || 'Final',
          period: espnMatch.period,
          clock: espnMatch.clock,
        };
      } else if (espnMatch.status === 'in_progress') {
        gameState = 'live';
        liveData = {
          homeScore: espnMatch.homeScore,
          awayScore: espnMatch.awayScore,
          statusDetail: espnMatch.statusDetail,
          period: espnMatch.period,
          clock: espnMatch.clock,
        };
      } else {
        // ESPN says scheduled but commence_time passed — treat as live (pre-tip)
        gameState = 'live';
        liveData = { statusDetail: 'Starting soon' };
      }
    } else {
      // No ESPN match — use time-based fallback
      const duration = SPORT_DURATIONS[game.sport_key] || 3;
      const expectedEnd = new Date(commenceTime.getTime() + duration * 60 * 60 * 1000);
      if (now < expectedEnd) {
        gameState = 'live';
        liveData = { statusDetail: 'Score unavailable' };
      } else {
        gameState = 'final';
        liveData = { statusDetail: 'Final (score pending)' };
      }
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
    fairLines,
    gameState,
    liveData,
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

    // Build game team lookup for exchange ML matching
    const gameTeamsMap: Record<string, { home: string; away: string }> = {};
    if (allCachedData) {
      for (const row of allCachedData) {
        if (row.game_data?.home_team && row.game_data?.away_team) {
          gameTeamsMap[row.game_data.id] = {
            home: row.game_data.home_team,
            away: row.game_data.away_team,
          };
        }
      }
    }

    // Determine which sports have started games (need ESPN live scores)
    const now = new Date();
    const sportsNeedingScores: string[] = [];
    if (allCachedData) {
      const seen = new Set<string>();
      for (const row of allCachedData) {
        const ct = row.game_data?.commence_time;
        if (ct && new Date(ct) <= now && !seen.has(row.sport_key)) {
          seen.add(row.sport_key);
          sportsNeedingScores.push(row.sport_key);
        }
      }
    }

    // Fetch exchange data, fair lines, ESPN scores, and game results in parallel
    const fetchExchange = async (marketType: string) => {
      const { data } = await supabase
        .from('exchange_data')
        .select('exchange, market_type, yes_price, no_price, subtitle, event_title, mapped_game_id')
        .not('mapped_game_id', 'is', null)
        .eq('market_type', marketType)
        .order('snapshot_time', { ascending: false })
        .limit(1000);
      return data || [];
    };

    const [espnData, gameResults, fairLinesMap, mlRows, spreadRows, totalRows] = await Promise.all([
      fetchESPNScores(sportsNeedingScores),
      fetchGameResults(gameIds),
      fetchLatestFairLines(gameIds),
      fetchExchange('moneyline'),
      fetchExchange('spread'),
      fetchExchange('total'),
    ]);

    // Build exchange bookmakers by game ID
    const exchangeBookmakersByGameId: Record<string, Record<string, any>> = {};
    {
      const rawRows = [...mlRows, ...spreadRows, ...totalRows];
      // Enrich Polymarket rows (null subtitle) by parsing event_title
      const exchangeRows = enrichExchangeRows(rawRows, gameTeamsMap);

      if (exchangeRows.length > 0) {
        // De-dup: keep only latest snapshot per (game, exchange, market_type, subtitle)
        const seen = new Set<string>();
        const deduped: typeof exchangeRows = [];
        for (const row of exchangeRows) {
          const key = `${row.mapped_game_id}|${row.exchange}|${row.market_type}|${row.subtitle ?? ''}`;
          if (seen.has(key)) continue;
          seen.add(key);
          deduped.push(row);
        }

        // Group by game_id -> exchange
        const grouped: Record<string, Record<string, typeof deduped>> = {};
        for (const row of deduped) {
          const gid = row.mapped_game_id;
          if (!gid) continue;
          if (!grouped[gid]) grouped[gid] = {};
          if (!grouped[gid][row.exchange]) grouped[gid][row.exchange] = [];
          grouped[gid][row.exchange].push(row);
        }

        const centToAmerican = (cents: number) => {
          const prob = cents / 100;
          if (prob <= 0 || prob >= 1) return 0;
          return prob >= 0.5
            ? Math.round(-100 * prob / (1 - prob))
            : Math.round(100 * (1 - prob) / prob);
        };

        for (const [gameId, exchanges] of Object.entries(grouped)) {
          exchangeBookmakersByGameId[gameId] = {};
          const teams = gameTeamsMap[gameId];

          for (const [exchange, contracts] of Object.entries(exchanges)) {
            const bookOdds: any = {};

            // --- Moneyline ---
            const mlContracts = contracts.filter(c => c.market_type === 'moneyline' && c.subtitle);
            if (mlContracts.length >= 2 && teams) {
              let homeMl: (typeof mlContracts)[0] | null = null;
              let awayMl: (typeof mlContracts)[0] | null = null;
              const homeLower = teams.home.toLowerCase();
              const awayLower = teams.away.toLowerCase();
              for (const c of mlContracts) {
                const sub = (c.subtitle || '').toLowerCase();
                if (!homeMl && (sub.includes(homeLower) || homeLower.includes(sub))) homeMl = c;
                if (!awayMl && (sub.includes(awayLower) || awayLower.includes(sub))) awayMl = c;
              }
              if (!homeMl || !awayMl) {
                const homeLast = homeLower.split(' ').pop()!;
                const awayLast = awayLower.split(' ').pop()!;
                for (const c of mlContracts) {
                  const sub = (c.subtitle || '').toLowerCase();
                  if (!homeMl && sub.includes(homeLast)) homeMl = c;
                  if (!awayMl && sub.includes(awayLast)) awayMl = c;
                }
              }
              if (homeMl && awayMl) {
                bookOdds.h2h = {
                  homePrice: centToAmerican(homeMl.yes_price ?? 50),
                  awayPrice: centToAmerican(awayMl.yes_price ?? 50),
                  exchangeHomeYes: homeMl.yes_price,
                  exchangeAwayYes: awayMl.yes_price,
                };
              }
            } else if (mlContracts.length === 1) {
              const ml = mlContracts[0];
              if (ml.yes_price != null) {
                bookOdds.h2h = {
                  homePrice: centToAmerican(ml.yes_price),
                  awayPrice: centToAmerican(ml.no_price ?? (100 - ml.yes_price)),
                  exchangeHomeYes: ml.yes_price,
                  exchangeAwayYes: ml.no_price ?? (100 - ml.yes_price),
                };
              }
            }

            // --- Spread ---
            const spreadContracts = contracts.filter(c => c.market_type === 'spread' && c.subtitle);
            if (spreadContracts.length > 0) {
              const primary = spreadContracts.reduce((best, c) =>
                Math.abs((c.yes_price ?? 50) - 50) < Math.abs((best.yes_price ?? 50) - 50) ? c : best
              );
              const sub = primary.subtitle || primary.event_title || '';
              const lineMatch = sub.match(/(\d+\.?\d*)/);
              const rawLine = lineMatch ? parseFloat(lineMatch[1]) : undefined;
              let signedLine = rawLine;
              const isHomeTeamContract = teams && sub.toLowerCase().includes(
                teams.home.toLowerCase().split(' ').pop()!
              );
              if (rawLine !== undefined && teams) {
                signedLine = isHomeTeamContract ? -rawLine : rawLine;
              }
              bookOdds.spreads = {
                line: signedLine,
                homePrice: isHomeTeamContract
                  ? centToAmerican(primary.yes_price ?? 50)
                  : centToAmerican(primary.no_price ?? 50),
                awayPrice: isHomeTeamContract
                  ? centToAmerican(primary.no_price ?? 50)
                  : centToAmerican(primary.yes_price ?? 50),
                exchangeYes: primary.yes_price,
                exchangeNo: primary.no_price,
              };
            }

            // --- Total ---
            const totalContracts = contracts.filter(c => c.market_type === 'total' && c.subtitle);
            if (totalContracts.length > 0) {
              const primary = totalContracts.reduce((best, c) =>
                Math.abs((c.yes_price ?? 50) - 50) < Math.abs((best.yes_price ?? 50) - 50) ? c : best
              );
              const sub = primary.subtitle || primary.event_title || '';
              const lineMatch = sub.match(/(\d+\.?\d*)/);
              const totalLine = lineMatch ? parseFloat(lineMatch[1]) : undefined;
              bookOdds.totals = {
                line: totalLine,
                overPrice: centToAmerican(primary.yes_price ?? 50),
                underPrice: centToAmerican(primary.no_price ?? 50),
                exchangeOverYes: primary.yes_price,
                exchangeUnderYes: primary.no_price,
              };
            }

            exchangeBookmakersByGameId[gameId][exchange] = bookOdds;
          }
        }
      }
    }

    // Process games by sport
    const allGames: Record<string, any[]> = {};
    let totalGames = 0;
    let totalEdges = 0;
    const sevenDaysFromNow = now.getTime() + 7 * 24 * 60 * 60 * 1000;
    const twentyFourHoursAgo = now.getTime() - 24 * 60 * 60 * 1000;

    for (const sportKey of SPORT_KEYS) {
      const sportData = allCachedData?.filter((row: any) => row.sport_key === sportKey) || [];

      const games = sportData
        .map((row: any) => {
          const result = processGame(row.game_data, espnData, gameResults, fairLinesMap);
          // Merge exchange bookmakers (Kalshi, Polymarket)
          const exchangeBooks = exchangeBookmakersByGameId[row.game_data?.id];
          if (exchangeBooks && result) {
            result.bookmakers = { ...result.bookmakers, ...exchangeBooks };
          }
          return result;
        })
        .filter(Boolean)
        // Keep future games AND games from the last 24 hours
        .filter((g: any) => new Date(g.commenceTime).getTime() > twentyFourHoursAgo)
        // Sort: live first, then pregame (soonest), then final (most recent)
        .sort((a: any, b: any) => {
          const stateOrder: Record<string, number> = { live: 0, pregame: 1, final: 2 };
          const sa = stateOrder[a.gameState] ?? 1;
          const sb = stateOrder[b.gameState] ?? 1;
          if (sa !== sb) return sa - sb;
          const ta = new Date(a.commenceTime).getTime();
          const tb = new Date(b.commenceTime).getTime();
          if (a.gameState === 'final') return tb - ta;
          return ta - tb;
        });

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

    // Debug: game state counts and exchange coverage
    let gamesWithExchange = 0, liveCount = 0, finalCount = 0;
    for (const sportGames of Object.values(allGames)) {
      for (const g of sportGames as any[]) {
        if (g.bookmakers?.kalshi || g.bookmakers?.polymarket) gamesWithExchange++;
        if (g.gameState === 'live') liveCount++;
        if (g.gameState === 'final') finalCount++;
      }
    }
    console.log(`[Dashboard API] ${totalGames} games, ${totalEdges} edges (>=${EDGE_THRESHOLD}%), ${Object.keys(fairLinesMap).length} fair lines, ${processingTime}ms`);
    console.log(`[Dashboard API] States: ${liveCount} live, ${totalGames - liveCount - finalCount} pregame, ${finalCount} final | ESPN fetched: ${sportsNeedingScores.join(', ') || 'none'}`);
    console.log(`[Dashboard API] Exchange merge: ${gamesWithExchange} of ${totalGames} games have exchange data, ${Object.keys(exchangeBookmakersByGameId).length} mapped game IDs`);

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
