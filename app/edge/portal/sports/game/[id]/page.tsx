import Link from 'next/link';
import { GameDetailClient } from '@/components/edge/GameDetailClient';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { calculateGameCEQ, fetchGameContext, type ExtendedOddsSnapshot, type GameCEQ, type PythonPillarScores } from '@/lib/edge/engine/edgescout';
import { calculateTwoWayEV } from '@/lib/edge/utils/odds-math';
import { isTier2Account } from '@/lib/edge/auth-tier';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Fetch Python pillar scores from backend
async function fetchPythonPillars(gameId: string, sport: string): Promise<PythonPillarScores | null> {
  try {
    // Map sport key to backend format
    const sportMap: Record<string, string> = {
      'americanfootball_nfl': 'NFL',
      'basketball_nba': 'NBA',
      'icehockey_nhl': 'NHL',
      'americanfootball_ncaaf': 'NCAAF',
      'basketball_ncaab': 'NCAAB',
    };
    const backendSport = sportMap[sport] || sport.toUpperCase();

    const response = await fetch(
      `${BACKEND_URL}/api/pillars/${backendSport}/${gameId}`,
      { cache: 'no-store' }
    );

    if (!response.ok) {
      console.log(`[PythonPillars] Backend returned ${response.status} for ${gameId}`);
      return null;
    }

    const data = await response.json();

    // Transform from 0-1 scale to 0-100
    // Note: Python uses snake_case (time_decay, game_environment)
    // Use ?? (nullish coalescing) not || to preserve valid 0 scores
    const ps = data.pillar_scores ?? {};

    // Transform per-market/period pillar data (also 0-1 → 0-100)
    const transformMarketPeriods = (marketData: Record<string, any> | undefined) => {
      if (!marketData) return {};
      const result: Record<string, any> = {};
      for (const [periodKey, periodData] of Object.entries(marketData)) {
        const pd = periodData as any;
        const pillarScores: Record<string, number> = {};
        if (pd.pillar_scores) {
          pillarScores.execution = Math.round((pd.pillar_scores.execution ?? 0.5) * 100);
          pillarScores.incentives = Math.round((pd.pillar_scores.incentives ?? 0.5) * 100);
          pillarScores.shocks = Math.round((pd.pillar_scores.shocks ?? 0.5) * 100);
          pillarScores.timeDecay = Math.round((pd.pillar_scores.time_decay ?? 0.5) * 100);
          pillarScores.flow = Math.round((pd.pillar_scores.flow ?? 0.5) * 100);
          pillarScores.gameEnvironment = Math.round((pd.pillar_scores.game_environment ?? 0.5) * 100);
        }
        result[periodKey] = {
          composite: Math.round((pd.composite ?? 0.5) * 100),
          confidence: pd.confidence || 'PASS',
          weights: pd.weights || {},
          pillar_scores: Object.keys(pillarScores).length > 0 ? pillarScores : undefined,
        };
      }
      return result;
    };

    return {
      execution: Math.round((ps.execution ?? 0.5) * 100),
      incentives: Math.round((ps.incentives ?? 0.5) * 100),
      shocks: Math.round((ps.shocks ?? 0.5) * 100),
      timeDecay: Math.round((ps.time_decay ?? 0.5) * 100),
      flow: Math.round((ps.flow ?? 0.5) * 100),
      gameEnvironment: Math.round((ps.game_environment ?? 0.5) * 100),
      composite: Math.round((data.composite_score ?? 0.5) * 100),
      pillarsByMarket: data.pillars_by_market ? {
        spread: transformMarketPeriods(data.pillars_by_market.spread),
        totals: transformMarketPeriods(data.pillars_by_market.totals),
        moneyline: transformMarketPeriods(data.pillars_by_market.moneyline),
      } : undefined,
    };
  } catch (error) {
    console.log(`[PythonPillars] Failed to fetch: ${error instanceof Error ? error.message : 'unknown'}`);
    return null;
  }
}

interface ExchangeMarket {
  exchange: 'kalshi' | 'polymarket';
  market_id: string;
  market_title: string;
  yes_price: number | null;
  no_price: number | null;
  yes_bid: number | null;
  yes_ask: number | null;
  no_bid: number | null;
  no_ask: number | null;
  spread: number | null;
  volume_24h: number | null;
  liquidity_depth: any;
}

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

// Fetch all snapshots for CEQ calculation
async function fetchSnapshotsForCEQ(gameId: string): Promise<ExtendedOddsSnapshot[]> {
  try {
    const supabase = getDirectSupabase();
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('game_id, market, book_key, outcome_type, line, odds, snapshot_time')
      .eq('game_id', gameId)
      .order('snapshot_time', { ascending: true });

    if (error || !data) return [];

    return data.map(row => ({
      game_id: row.game_id,
      market: row.market,
      book_key: row.book_key,
      outcome_type: row.outcome_type,
      line: row.line,
      odds: row.odds,
      snapshot_time: row.snapshot_time,
    }));
  } catch (e) {
    console.error('[GameDetail] Snapshots for CEQ fetch error:', e);
    return [];
  }
}

// Fetch opening line for a specific game
// Note: outcome_type contains team names (not 'home'/'away'), so we fetch all spreads
// and take the first one with a negative line (home team typically has negative spread in favorites)
async function fetchOpeningLine(gameId: string): Promise<number | undefined> {
  try {
    const supabase = getDirectSupabase();
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('line, outcome_type')
      .eq('game_id', gameId)
      .eq('market', 'spreads')
      .not('line', 'is', null)
      .order('snapshot_time', { ascending: true })
      .limit(2);

    if (error || !data || data.length === 0) return undefined;
    // Return the first spread line (either side works for opening line reference)
    return data[0].line;
  } catch (e) {
    console.error('[GameDetail] Opening line fetch error:', e);
    return undefined;
  }
}

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ sport?: string; demo?: string }>;
}

async function fetchLineHistory(gameId: string, market: string = 'spread', period: string = 'full', book?: string) {
  // MERGE BOTH DATA SOURCES for complete history:
  // - odds_snapshots (Supabase): older historical data (Jan 28 → Jan 31)
  // - line_snapshots (backend): newer data (Jan 31 → present)

  const allSnapshots: any[] = [];

  // 1. Query odds_snapshots from Supabase (older historical data)
  try {
    const marketMap: Record<string, string> = {
      'spread': 'spreads',
      'moneyline': 'h2h',
      'total': 'totals',
    };
    const baseMarket = marketMap[market] || market;
    const snapshotMarket = period === 'full' ? baseMarket : `${baseMarket}_${period}`;

    const supabase = getSupabase();
    let query = supabase
      .from('odds_snapshots')
      .select('*')
      .eq('game_id', gameId)
      .eq('market', snapshotMarket)
      .order('snapshot_time', { ascending: true });

    if (book) {
      query = query.eq('book_key', book);
    }

    const { data, error } = await query;
    if (!error && data && data.length > 0) {
      // Convert to normalized format
      data.forEach((row: any) => {
        allSnapshots.push({
          snapshot_time: row.snapshot_time,
          book_key: row.book_key,
          outcome_type: row.outcome_type, // odds_snapshots has this field
          line: row.line,
          odds: row.odds,
          source: 'odds_snapshots',
        });
      });
    }
  } catch (e) {
    console.error('[GameDetail] odds_snapshots query error:', e);
  }

  // 2. Query line_snapshots from backend (newer data)
  // Note: line_snapshots doesn't have outcome_type, only stores home side
  try {
    let url = `${BACKEND_URL}/api/lines/${gameId}?market=${market}&period=${period}`;
    if (book) url += `&book=${book}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.snapshots && data.snapshots.length > 0) {
        data.snapshots.forEach((row: any) => {
          allSnapshots.push({
            snapshot_time: row.snapshot_time,
            book_key: row.book_key,
            outcome_type: row.outcome_type || null, // line_snapshots may not have this
            line: row.line,
            odds: row.odds,
            source: 'line_snapshots',
          });
        });
      }
    }
  } catch (e) {
    // Backend unavailable, continue with what we have
  }

  // 3. Deduplicate by timestamp + book_key + outcome_type
  // Prefer odds_snapshots data when there's a conflict (has outcome_type)
  const seen = new Map<string, any>();
  for (const snap of allSnapshots) {
    // Create unique key: timestamp + book + outcome (for deduplication)
    const key = `${snap.snapshot_time}-${snap.book_key}-${snap.outcome_type || 'home'}`;
    const existing = seen.get(key);

    // Keep odds_snapshots version if it exists (has outcome_type)
    if (!existing || (snap.source === 'odds_snapshots' && existing.source === 'line_snapshots')) {
      seen.set(key, snap);
    }
  }

  // 4. Convert to array, sort chronologically, remove source field
  const merged = Array.from(seen.values())
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime())
    .map(({ source, ...rest }) => rest); // Remove internal source field

  return merged;
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

// Fetch exchange markets (Kalshi/Polymarket) that match this game
async function fetchExchangeMarkets(homeTeam: string, awayTeam: string, sportKey: string): Promise<ExchangeMarket[]> {
  try {
    const supabase = getDirectSupabase();

    // Get latest snapshot time
    const { data: latestSnapshot } = await supabase
      .from('exchange_snapshots')
      .select('snapshot_time')
      .order('snapshot_time', { ascending: false })
      .limit(1)
      .single();

    if (!latestSnapshot) return [];

    // Map sport key to exchange sport format
    const sportMap: Record<string, string> = {
      'americanfootball_nfl': 'americanfootball_nfl',
      'basketball_nba': 'basketball_nba',
      'icehockey_nhl': 'icehockey_nhl',
      'baseball_mlb': 'baseball_mlb',
    };
    const exchangeSport = sportMap[sportKey];

    // Query exchange markets for this sport
    let query = supabase
      .from('exchange_snapshots')
      .select('*')
      .eq('snapshot_time', latestSnapshot.snapshot_time)
      .eq('category', 'sports');

    if (exchangeSport) {
      query = query.eq('sport', exchangeSport);
    }

    const { data, error } = await query;
    if (error || !data) return [];

    // Filter to markets that mention either team
    const homeKeywords = homeTeam.toLowerCase().split(' ');
    const awayKeywords = awayTeam.toLowerCase().split(' ');

    return data.filter((market: any) => {
      const title = market.market_title.toLowerCase();
      const homeMatch = homeKeywords.some(kw => kw.length > 3 && title.includes(kw));
      const awayMatch = awayKeywords.some(kw => kw.length > 3 && title.includes(kw));
      return homeMatch || awayMatch;
    });
  } catch (e) {
    console.error('[GameDetail] Exchange markets fetch error:', e);
    return [];
  }
}

// Transform exchange market to bookmaker-compatible format
function buildExchangeMarketGroups(markets: ExchangeMarket[], homeTeam: string, awayTeam: string) {
  // Group markets by exchange
  const kalshiMarkets = markets.filter(m => m.exchange === 'kalshi');
  const polymarketMarkets = markets.filter(m => m.exchange === 'polymarket');

  const buildMarketGroup = (exchangeMarkets: ExchangeMarket[]) => {
    if (exchangeMarkets.length === 0) return null;

    // Find moneyline-style markets (who will win)
    const winMarket = exchangeMarkets.find(m =>
      m.market_title.toLowerCase().includes('win') ||
      m.market_title.toLowerCase().includes('winner')
    );

    // Build h2h from YES price (YES = team wins)
    let h2h: any = null;
    if (winMarket && winMarket.yes_price !== null) {
      // YES price represents probability, convert to American odds
      const yesProb = winMarket.yes_price / 100;
      const noProb = (winMarket.no_price || (100 - winMarket.yes_price)) / 100;

      const probToAmerican = (prob: number) => {
        if (prob >= 0.5) return Math.round(-100 * prob / (1 - prob));
        return Math.round(100 * (1 - prob) / prob);
      };

      h2h = {
        home: { price: probToAmerican(yesProb), edge: 0, exchangePrice: winMarket.yes_price },
        away: { price: probToAmerican(noProb), edge: 0, exchangePrice: winMarket.no_price },
      };
    }

    return {
      fullGame: { h2h, spreads: null, totals: null },
      firstHalf: { h2h: null, spreads: null, totals: null },
      secondHalf: { h2h: null, spreads: null, totals: null },
      teamTotals: null,
      playerProps: [],
      alternates: { spreads: [], totals: [] },
      lineHistory: {},
      exchangeMarkets: exchangeMarkets, // Include raw exchange data
    };
  };

  return {
    kalshi: kalshiMarkets.length > 0 ? { marketGroups: buildMarketGroup(kalshiMarkets) } : null,
    polymarket: polymarketMarkets.length > 0 ? { marketGroups: buildMarketGroup(polymarketMarkets) } : null,
  };
}

function buildConsensusFromBookmakers(game: any) {
  const bookmakers = game.bookmakers;
  if (!bookmakers || bookmakers.length === 0) return {};

  const h2h: { home: number[]; away: number[]; draw: number[] } = { home: [], away: [], draw: [] };
  const spreads: { homeLine: number[]; homeOdds: number[]; awayLine: number[]; awayOdds: number[] } = { homeLine: [], homeOdds: [], awayLine: [], awayOdds: [] };
  const totals: { line: number[]; overOdds: number[]; underOdds: number[] } = { line: [], overOdds: [], underOdds: [] };

  for (const bk of bookmakers) {
    for (const market of bk.markets) {
      if (market.key === 'h2h') {
        const home = market.outcomes.find((o: any) => o.name === game.home_team);
        const away = market.outcomes.find((o: any) => o.name === game.away_team);
        const draw = market.outcomes.find((o: any) => o.name === 'Draw');
        if (home) h2h.home.push(home.price);
        if (away) h2h.away.push(away.price);
        if (draw) h2h.draw.push(draw.price);
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
    consensus.h2h = {
      home: median(h2h.home),
      away: median(h2h.away),
      draw: h2h.draw.length > 0 ? median(h2h.draw) : undefined,
    };
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

// Build per-book marketGroups from raw cached Odds API data
// Extracts ALL markets: core (h2h, spreads, totals), halves, alternates, team totals, player props
function buildPerBookFromCache(game: any): Record<string, { marketGroups: any }> {
  const result: Record<string, { marketGroups: any }> = {};
  const bookmakers = game.bookmakers || [];

  for (const bk of bookmakers) {
    const bookKey = bk.key;
    const marketsByKey: Record<string, any> = {};
    for (const market of (bk.markets || [])) {
      marketsByKey[market.key] = market;
    }

    const extractMarket = (h2hKey: string, spreadsKey: string, totalsKey: string) => {
      const h2hM = marketsByKey[h2hKey];
      const spreadsM = marketsByKey[spreadsKey];
      const totalsM = marketsByKey[totalsKey];
      const out: any = { h2h: null, spreads: null, totals: null };

      if (h2hM) {
        const home = h2hM.outcomes.find((o: any) => o.name === game.home_team);
        const away = h2hM.outcomes.find((o: any) => o.name === game.away_team);
        const draw = h2hM.outcomes.find((o: any) => o.name === 'Draw');
        if (home && away) {
          out.h2h = {
            home: { price: home.price, edge: 0 },
            away: { price: away.price, edge: 0 },
            draw: draw ? { price: draw.price, edge: 0 } : undefined,
          };
        }
      }
      if (spreadsM) {
        const home = spreadsM.outcomes.find((o: any) => o.name === game.home_team);
        const away = spreadsM.outcomes.find((o: any) => o.name === game.away_team);
        if (home && away) {
          out.spreads = {
            home: { line: home.point, price: home.price, edge: 0 },
            away: { line: away.point, price: away.price, edge: 0 },
          };
        }
      }
      if (totalsM) {
        const over = totalsM.outcomes.find((o: any) => o.name === 'Over');
        const under = totalsM.outcomes.find((o: any) => o.name === 'Under');
        if (over) {
          out.totals = {
            line: over.point,
            over: { price: over.price, edge: 0 },
            under: { price: under?.price, edge: 0 },
          };
        }
      }
      return out;
    };

    // Alternate spreads - grouped by home spread line
    const altSpreadsByLine: Map<number, any> = new Map();
    if (marketsByKey['alternate_spreads']) {
      for (const o of marketsByKey['alternate_spreads'].outcomes) {
        const isHome = o.name === game.home_team;
        const homeSpread = isHome ? o.point : -o.point;
        if (!altSpreadsByLine.has(homeSpread)) {
          altSpreadsByLine.set(homeSpread, { homeSpread, home: null, away: null });
        }
        const entry = altSpreadsByLine.get(homeSpread)!;
        if (isHome) {
          entry.home = { line: o.point, price: o.price };
        } else {
          entry.away = { line: o.point, price: o.price };
        }
      }
    }
    const altSpreads = Array.from(altSpreadsByLine.values()).sort((a, b) => a.homeSpread - b.homeSpread);

    // Alternate totals - grouped by line
    const altTotalsByLine: Map<number, any> = new Map();
    if (marketsByKey['alternate_totals']) {
      for (const o of marketsByKey['alternate_totals'].outcomes) {
        const line = o.point;
        if (!altTotalsByLine.has(line)) {
          altTotalsByLine.set(line, { line, over: null, under: null });
        }
        const entry = altTotalsByLine.get(line)!;
        if (o.name === 'Over') {
          entry.over = { price: o.price };
        } else if (o.name === 'Under') {
          entry.under = { price: o.price };
        }
      }
    }
    const altTotals = Array.from(altTotalsByLine.values()).sort((a, b) => a.line - b.line);

    // Team totals
    let teamTotals: any = null;
    if (marketsByKey['team_totals']) {
      teamTotals = { home: { over: null, under: null }, away: { over: null, under: null } };
      for (const o of marketsByKey['team_totals'].outcomes) {
        const isHome = o.description === game.home_team;
        const isAway = o.description === game.away_team;
        const team = isHome ? 'home' : isAway ? 'away' : null;
        if (team && o.name === 'Over') {
          teamTotals[team].over = { line: o.point, price: o.price };
        } else if (team && o.name === 'Under') {
          teamTotals[team].under = { line: o.point, price: o.price };
        }
      }
    }

    // Player props
    const playerProps: any[] = [];
    for (const [key, market] of Object.entries(marketsByKey)) {
      if (!key.startsWith('player_') && !key.startsWith('pitcher_') && !key.startsWith('batter_')) continue;
      const outcomes = (market as any).outcomes || [];
      const hasOverUnder = outcomes.some((o: any) => o.name === 'Over' || o.name === 'Under');

      if (hasOverUnder) {
        // Over/Under props - description is player name
        const byPlayer: Record<string, any> = {};
        for (const o of outcomes) {
          const pName = o.description;
          if (!pName) continue;
          if (!byPlayer[pName]) {
            byPlayer[pName] = { player: pName, market: key, market_type: key, book: bookKey, line: null, over: null, under: null };
          }
          if (o.name === 'Over') {
            byPlayer[pName].over = { odds: o.price, line: o.point };
            byPlayer[pName].line = o.point;
          } else if (o.name === 'Under') {
            byPlayer[pName].under = { odds: o.price, line: o.point };
            if (byPlayer[pName].line === null) byPlayer[pName].line = o.point;
          }
        }
        playerProps.push(...Object.values(byPlayer));
      } else {
        // Yes/no props (e.g., anytime TD) - name is player name
        for (const o of outcomes) {
          playerProps.push({
            player: o.description || o.name, market: key, market_type: key, book: bookKey,
            line: o.point ?? null, over: null, under: null,
            yes: { odds: o.price },
          });
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
        playerProps,
        alternates: { spreads: altSpreads, totals: altTotals },
        lineHistory: {},
      },
    };
  }

  return result;
}

// Edge values are only shown when real data is available from the backend
// No mock/fake edges - this is an enterprise product where data integrity matters

export default async function GameDetailPage({ params, searchParams }: PageProps) {
  const { id: gameId } = await params;
  const { sport: querySport, demo } = await searchParams;

  // Check for demo mode via URL param
  const isDemo = demo === 'true';

  // Get user email from session (for demo account check)
  let userEmail: string | undefined;
  try {
    const supabase = getSupabase();
    const { data: { user } } = await supabase.auth.getUser();
    userEmail = user?.email;
  } catch (e) {
    // No session or error - that's fine
  }

  let gameData: any = null;
  let cachedRaw: any = null; // Raw cached game data with all enriched markets
  let sportKey: string = querySport || '';
  let backendSportKey: string = '';

  const sportMap: Record<string, string> = {
    'americanfootball_nfl': 'NFL',
    'basketball_nba': 'NBA',
    'icehockey_nhl': 'NHL',
    'americanfootball_ncaaf': 'NCAAF',
    'basketball_ncaab': 'NCAAB',
    'baseball_mlb': 'MLB',
    'basketball_wnba': 'WNBA',
    'mma_mixed_martial_arts': 'MMA',
    'tennis_atp_australian_open': 'TENNIS_AO',
    'tennis_atp_french_open': 'TENNIS_FO',
    'tennis_atp_us_open': 'TENNIS_USO',
    'tennis_atp_wimbledon': 'TENNIS_WIM',
    'soccer_epl': 'EPL',
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
    const sportsToSearch = ['NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB', 'MLB', 'EPL', 'WNBA', 'MMA', 'TENNIS_AO', 'TENNIS_FO', 'TENNIS_USO', 'TENNIS_WIM'];
    const reverseMap: Record<string, string> = {
      'NFL': 'americanfootball_nfl',
      'NBA': 'basketball_nba',
      'NHL': 'icehockey_nhl',
      'NCAAF': 'americanfootball_ncaaf',
      'NCAAB': 'basketball_ncaab',
      'MLB': 'baseball_mlb',
      'WNBA': 'basketball_wnba',
      'MMA': 'mma_mixed_martial_arts',
      'TENNIS_AO': 'tennis_atp_australian_open',
      'TENNIS_FO': 'tennis_atp_french_open',
      'TENNIS_USO': 'tennis_atp_us_open',
      'TENNIS_WIM': 'tennis_atp_wimbledon',
      'EPL': 'soccer_epl',
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
      cachedRaw = raw; // Store for enriched market extraction
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

  // Fetch per-book odds data and consensus (critical for initial render)
  const [perBookOdds, consensusData] = await Promise.all([
    fetchPerBookOdds(backendSportKey, gameId),
    fetchConsensus(backendSportKey, gameId),
  ]);

  // PERFORMANCE: Only fetch Full Game line history on initial load (3 calls instead of 30)
  // Other periods (1H, 2H, Q1-Q4, P1-P3) are lazy-loaded when user clicks tab
  const [spreadHistory, mlHistory, totalHistory] = await Promise.all([
    fetchLineHistory(gameId, 'spread', 'full'),
    fetchLineHistory(gameId, 'moneyline', 'full'),
    fetchLineHistory(gameId, 'total', 'full'),
  ]);

  // PERFORMANCE: These are loaded async after page renders (non-blocking)
  // Props, pillars, and exchange markets don't block initial render
  const propsData: any[] = []; // Loaded client-side

  const homeTeam = gameData.home_team;
  const awayTeam = gameData.away_team;
  const commenceTime = gameData.commence_time;
  const compositeScore = gameData.composite_score || 0.5;
  const confidence = gameData.overall_confidence || 'PASS';

  // Build line history object - only Full Game on initial load
  // Other periods are lazy-loaded client-side when user clicks tab
  const lineHistory: Record<string, Record<string, any[]>> = {
    full: { spread: spreadHistory, moneyline: mlHistory, total: totalHistory },
    // Empty arrays for other periods - will be populated client-side on demand
    h1: { spread: [], moneyline: [], total: [] },
    h2: { spread: [], moneyline: [], total: [] },
    q1: { spread: [], moneyline: [], total: [] },
    q2: { spread: [], moneyline: [], total: [] },
    q3: { spread: [], moneyline: [], total: [] },
    q4: { spread: [], moneyline: [], total: [] },
    p1: { spread: [], moneyline: [], total: [] },
    p2: { spread: [], moneyline: [], total: [] },
    p3: { spread: [], moneyline: [], total: [] },
  };

  // Fetch data for CEQ calculation (including team stats, weather, and Python pillars)
  const [ceqSnapshots, openingLine, gameContext, pythonPillars] = await Promise.all([
    fetchSnapshotsForCEQ(gameId),
    fetchOpeningLine(gameId),
    fetchGameContext(gameId, homeTeam, awayTeam, sportKey),
    fetchPythonPillars(gameId, sportKey),
  ]);

  // ALWAYS use cached_odds from Supabase for odds data (same source as populate-counts)
  // This ensures dashboard and game detail page show identical edge counts
  let bookmakers: Record<string, any> = {};
  let availableBooks: string[] = [];

  // Get cached odds data from Supabase
  let rawData = cachedRaw;
  if (!rawData) {
    const cached = await fetchGameFromCache(gameId);
    if (cached) rawData = cached.game_data;
  }

  if (rawData && rawData.bookmakers && rawData.bookmakers.length > 0) {
    // Build per-book marketGroups from cached Odds API data
    const perBook = buildPerBookFromCache(rawData);
    bookmakers = perBook;
    availableBooks = Object.keys(perBook);

    // Inject line history and props into each book
    Object.keys(bookmakers).forEach(book => {
      if (bookmakers[book].marketGroups) {
        bookmakers[book].marketGroups.lineHistory = lineHistory;
        // Add props data
        if (!bookmakers[book].marketGroups.playerProps || bookmakers[book].marketGroups.playerProps.length === 0) {
          bookmakers[book].marketGroups.playerProps = propsData.filter((p: any) => p.book === book);
        }
      }
    });
  }

  // Fetch and merge exchange markets (Kalshi/Polymarket)
  const exchangeMarkets = await fetchExchangeMarkets(homeTeam, awayTeam, sportKey);
  if (exchangeMarkets.length > 0) {
    const exchangeData = buildExchangeMarketGroups(exchangeMarkets, homeTeam, awayTeam);
    if (exchangeData.kalshi) {
      bookmakers['kalshi'] = exchangeData.kalshi;
      if (!availableBooks.includes('kalshi')) availableBooks.push('kalshi');
    }
    if (exchangeData.polymarket) {
      bookmakers['polymarket'] = exchangeData.polymarket;
      if (!availableBooks.includes('polymarket')) availableBooks.push('polymarket');
    }
  }

  const fullSportKey = sportKey;

  // Extract Pinnacle lines (sharp baseline for FDV calculation)
  const pinnacleBook = bookmakers['pinnacle'] as any;
  const pinnacleFullGame = pinnacleBook?.marketGroups?.fullGame;
  const pinnacleSpreadLine = pinnacleFullGame?.spreads?.home?.line;
  const pinnacleTotalLine = pinnacleFullGame?.totals?.line;

  // Helper to calculate CEQ for any period using bookmaker data
  function calculatePeriodCEQ(periodKey: string, selectedBookKey: string = 'fanduel'): GameCEQ | null {
    // Aggregate odds from all bookmakers for this period
    const periodMarkets = Object.values(bookmakers)
      .map((b: any) => b.marketGroups?.[periodKey])
      .filter(Boolean);

    // Get selected book's lines for FDV comparison against Pinnacle
    const selectedBook = bookmakers[selectedBookKey] as any;
    const selectedBookMarkets = selectedBook?.marketGroups?.[periodKey];
    const bookSpreadLine = selectedBookMarkets?.spreads?.home?.line;
    const bookTotalLine = selectedBookMarkets?.totals?.line;

    if (periodMarkets.length === 0) return null;

    // Get median values from all bookmakers
    const getMedian = (values: number[]) => {
      if (values.length === 0) return undefined;
      const sorted = [...values].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };

    // Collect spread data
    const spreadLines: number[] = [];
    const spreadHomeOdds: number[] = [];
    const spreadAwayOdds: number[] = [];
    // Collect h2h data
    const h2hHomeOdds: number[] = [];
    const h2hAwayOdds: number[] = [];
    const h2hDrawOdds: number[] = [];
    // Collect totals data
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

    // For non-fullGame periods, estimate opening line from full game opening line
    // This allows CEQ to detect line movement even for period markets
    let periodOpeningData: any = {};
    if (openingLine !== undefined) {
      if (periodKey === 'fullGame') {
        periodOpeningData = { spreads: { home: openingLine, away: -openingLine } };
      } else if (periodKey === 'firstHalf' || periodKey === 'secondHalf') {
        // Half spreads are typically ~50% of full game spread
        const halfOpeningLine = openingLine * 0.5;
        periodOpeningData = { spreads: { home: halfOpeningLine, away: -halfOpeningLine } };
      } else if (periodKey.startsWith('q')) {
        // Quarter spreads are typically ~25% of full game spread
        const quarterOpeningLine = openingLine * 0.25;
        periodOpeningData = { spreads: { home: quarterOpeningLine, away: -quarterOpeningLine } };
      } else if (periodKey.startsWith('p')) {
        // NHL period spreads are typically ~33% of full game (3 periods)
        const periodOpeningLineValue = openingLine * 0.33;
        periodOpeningData = { spreads: { home: periodOpeningLineValue, away: -periodOpeningLineValue } };
      }
    }

    // Filter snapshots for this period's market types
    const marketSuffix = periodKey === 'fullGame' ? '' :
                        periodKey === 'firstHalf' ? '_h1' :
                        periodKey === 'secondHalf' ? '_h2' :
                        periodKey.startsWith('q') ? `_${periodKey}` :
                        periodKey.startsWith('p') ? `_${periodKey}` : '';
    const periodSnapshots = marketSuffix
      ? ceqSnapshots.filter(s => s.market?.endsWith(marketSuffix))
      : ceqSnapshots.filter(s => !s.market?.includes('_'));

    // If no period-specific snapshots, use full game snapshots scaled by time factor
    // This provides some momentum signal even for periods without historical data
    const effectiveSnapshots = periodSnapshots.length > 0 ? periodSnapshots : [];

    // Calculate EV for each market using selected book odds vs consensus
    // EV = (fair prob - implied prob) * 100
    // Fair prob from consensus, implied prob from selected book
    const selectedSpreadHome = selectedBookMarkets?.spreads?.home?.price;
    const selectedSpreadAway = selectedBookMarkets?.spreads?.away?.price;
    const selectedH2hHome = selectedBookMarkets?.h2h?.home?.price;
    const selectedH2hAway = selectedBookMarkets?.h2h?.away?.price;
    const selectedTotalOver = selectedBookMarkets?.totals?.over?.price;
    const selectedTotalUnder = selectedBookMarkets?.totals?.under?.price;

    const evData = {
      spreads: hasSpread && selectedSpreadHome && selectedSpreadAway ? {
        home: calculateTwoWayEV(selectedSpreadHome, selectedSpreadAway, periodSpreadHomeOdds, periodSpreadAwayOdds),
        away: calculateTwoWayEV(selectedSpreadAway, selectedSpreadHome, periodSpreadAwayOdds, periodSpreadHomeOdds),
      } : undefined,
      h2h: hasH2h && selectedH2hHome && selectedH2hAway ? {
        home: calculateTwoWayEV(selectedH2hHome, selectedH2hAway, periodH2hHome, periodH2hAway),
        away: calculateTwoWayEV(selectedH2hAway, selectedH2hHome, periodH2hAway, periodH2hHome),
      } : undefined,
      totals: hasTotals && selectedTotalOver && selectedTotalUnder ? {
        over: calculateTwoWayEV(selectedTotalOver, selectedTotalUnder, periodTotalOverOdds, periodTotalUnderOdds),
        under: calculateTwoWayEV(selectedTotalUnder, selectedTotalOver, periodTotalUnderOdds, periodTotalOverOdds),
      } : undefined,
    };

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
      gameContext,
      pythonPillars || undefined,  // Pass Python pillars if available
      // Pinnacle sharp lines (for FDV baseline) - only for full game
      periodKey === 'fullGame' && pinnacleSpreadLine !== undefined ? {
        spreads: { home: pinnacleSpreadLine, away: -pinnacleSpreadLine },
        totals: pinnacleTotalLine
      } : undefined,
      // Selected book's lines (for FDV comparison)
      bookSpreadLine !== undefined ? {
        spreads: { home: bookSpreadLine, away: -bookSpreadLine },
        totals: bookTotalLine
      } : undefined,
      // EV data for CEQ integration
      evData,
      // sportKey - to skip spreads for soccer
      sportKey
    );
  }

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

  // Calculate CEQ for team totals (home and away teams separately)
  function calculateTeamTotalsCEQ(): { home: GameCEQ | null; away: GameCEQ | null } | null {
    const getMedian = (values: number[]) => {
      if (values.length === 0) return undefined;
      const sorted = [...values].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };

    // Collect team totals from all bookmakers
    const homeLines: number[] = [];
    const homeOverOdds: number[] = [];
    const homeUnderOdds: number[] = [];
    const awayLines: number[] = [];
    const awayOverOdds: number[] = [];
    const awayUnderOdds: number[] = [];

    for (const book of Object.values(bookmakers)) {
      const teamTotals = (book as any).marketGroups?.teamTotals;
      if (!teamTotals) continue;

      if (teamTotals.home?.over?.line !== undefined) {
        homeLines.push(teamTotals.home.over.line);
        if (teamTotals.home.over.price !== undefined) homeOverOdds.push(teamTotals.home.over.price);
        if (teamTotals.home.under?.price !== undefined) homeUnderOdds.push(teamTotals.home.under.price);
      }
      if (teamTotals.away?.over?.line !== undefined) {
        awayLines.push(teamTotals.away.over.line);
        if (teamTotals.away.over.price !== undefined) awayOverOdds.push(teamTotals.away.over.price);
        if (teamTotals.away.under?.price !== undefined) awayUnderOdds.push(teamTotals.away.under.price);
      }
    }

    if (homeLines.length === 0 && awayLines.length === 0) return null;

    const calculateTeamCEQ = (
      lines: number[],
      overOdds: number[],
      underOdds: number[]
    ): GameCEQ | null => {
      const line = getMedian(lines);
      const overPrice = getMedian(overOdds) || -110;
      const underPrice = getMedian(underOdds) || -110;

      if (line === undefined) return null;

      const gameOdds = {
        totals: { line, over: overPrice, under: underPrice },
      };

      return calculateGameCEQ(
        gameOdds,
        {}, // No opening line for team totals
        [], // No snapshots for team totals
        { totals: { over: overOdds, under: underOdds } },
        { totals: { over: overPrice, under: underPrice } },
        gameContext,
        pythonPillars || undefined,  // Pass Python pillars if available
        undefined,  // No Pinnacle lines for team totals
        undefined,  // No book lines for team totals
        undefined   // No EV data for team totals
      );
    };

    return {
      home: calculateTeamCEQ(homeLines, homeOverOdds, homeUnderOdds),
      away: calculateTeamCEQ(awayLines, awayOverOdds, awayUnderOdds),
    };
  }

  const teamTotalsCeq = calculateTeamTotalsCEQ();

  // Legacy ceqData for backwards compatibility
  const ceqData = ceqByPeriod.fullGame;

  // Count COMPREHENSIVE edges across ALL periods and ALL markets/sides
  // Each side is counted separately: spread home, spread away, h2h home, h2h away, total over, total under
  // This gives up to 6 potential edges per period
  function countPeriodEdges(ceq: typeof ceqData): number {
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

  // Build comprehensive edge count breakdown
  const edgeCountBreakdown = {
    total: 0,
    fullGame: countPeriodEdges(ceqByPeriod.fullGame),
    firstHalf: countPeriodEdges(ceqByPeriod.firstHalf),
    secondHalf: countPeriodEdges(ceqByPeriod.secondHalf),
    quarters: countPeriodEdges(ceqByPeriod.q1) + countPeriodEdges(ceqByPeriod.q2) +
              countPeriodEdges(ceqByPeriod.q3) + countPeriodEdges(ceqByPeriod.q4),
    periods: countPeriodEdges(ceqByPeriod.p1) + countPeriodEdges(ceqByPeriod.p2) +
             countPeriodEdges(ceqByPeriod.p3),
    teamTotals: 0,
  };

  // Count team total edges (4 possible: home over, home under, away over, away under)
  if (teamTotalsCeq?.home?.totals?.over?.ceq !== undefined && teamTotalsCeq.home.totals.over.ceq >= 56) edgeCountBreakdown.teamTotals++;
  if (teamTotalsCeq?.home?.totals?.under?.ceq !== undefined && teamTotalsCeq.home.totals.under.ceq >= 56) edgeCountBreakdown.teamTotals++;
  if (teamTotalsCeq?.away?.totals?.over?.ceq !== undefined && teamTotalsCeq.away.totals.over.ceq >= 56) edgeCountBreakdown.teamTotals++;
  if (teamTotalsCeq?.away?.totals?.under?.ceq !== undefined && teamTotalsCeq.away.totals.under.ceq >= 56) edgeCountBreakdown.teamTotals++;

  // Calculate total
  edgeCountBreakdown.total = edgeCountBreakdown.fullGame + edgeCountBreakdown.firstHalf +
    edgeCountBreakdown.secondHalf + edgeCountBreakdown.quarters + edgeCountBreakdown.periods +
    edgeCountBreakdown.teamTotals;

  const totalEdgeCount = edgeCountBreakdown.total;

  // Only check books that users can actually select (fanduel, draftkings, kalshi, polymarket)
  const SELECTABLE_BOOKS = ['fanduel', 'draftkings', 'kalshi', 'polymarket'];
  const selectableBookmakers = Object.entries(bookmakers)
    .filter(([key]) => SELECTABLE_BOOKS.includes(key))
    .map(([, value]) => value);

  const hasProps = (propsData && propsData.length > 0) ||
    selectableBookmakers.some((b: any) => b.marketGroups?.playerProps?.length > 0);
  const hasAlternates = selectableBookmakers.some((b: any) =>
    (b.marketGroups?.alternates?.spreads?.length > 0) || (b.marketGroups?.alternates?.totals?.length > 0));
  const hasTeamTotals = selectableBookmakers.some((b: any) =>
    b.marketGroups?.teamTotals?.home?.over || b.marketGroups?.teamTotals?.away?.over);
  const isNHL = fullSportKey.includes('icehockey');
  const isFootball = fullSportKey.includes('football');
  const isBasketball = fullSportKey.includes('basketball');

  // Check if we have any half/quarter data from selectable books
  const hasFirstHalf = selectableBookmakers.some((b: any) =>
    b.marketGroups?.firstHalf?.spreads || b.marketGroups?.firstHalf?.h2h || b.marketGroups?.firstHalf?.totals
  );
  const hasSecondHalf = selectableBookmakers.some((b: any) =>
    b.marketGroups?.secondHalf?.spreads || b.marketGroups?.secondHalf?.h2h || b.marketGroups?.secondHalf?.totals
  );
  const hasQuarters = selectableBookmakers.some((b: any) =>
    b.marketGroups?.q1?.spreads || b.marketGroups?.q1?.h2h || b.marketGroups?.q1?.totals
  );
  const hasHockeyPeriods = selectableBookmakers.some((b: any) =>
    b.marketGroups?.p1?.spreads || b.marketGroups?.p1?.h2h || b.marketGroups?.p1?.totals
  );

  return (
    <div className="min-h-[calc(100vh-56px)] lg:h-[calc(100vh-56px)] overflow-y-auto lg:overflow-hidden">
      <GameDetailClient
        gameData={{ id: gameId, homeTeam, awayTeam, sportKey: fullSportKey, commenceTime }}
        bookmakers={bookmakers}
        availableBooks={availableBooks}
        userTier={isTier2Account(userEmail) ? "tier_2" : "tier_1"}
        userEmail={userEmail}
        isDemo={isDemo}
        ceq={ceqData}
        ceqByPeriod={ceqByPeriod}
        teamTotalsCeq={teamTotalsCeq}
        edgeCountBreakdown={edgeCountBreakdown}
        pythonPillarScores={pythonPillars}
        totalEdgeCount={totalEdgeCount}
        availableTabs={{
          fullGame: true,
          firstHalf: hasFirstHalf || isFootball || isBasketball || isNHL,
          secondHalf: hasSecondHalf || isFootball || isBasketball,
          q1: hasQuarters || ((isFootball || isBasketball) && !isNHL),
          q2: hasQuarters || ((isFootball || isBasketball) && !isNHL),
          q3: hasQuarters || ((isFootball || isBasketball) && !isNHL),
          q4: hasQuarters || ((isFootball || isBasketball) && !isNHL),
          p1: hasHockeyPeriods || isNHL,
          p2: hasHockeyPeriods || isNHL,
          p3: hasHockeyPeriods || isNHL,
          alternates: hasAlternates,
          teamTotals: hasTeamTotals,
        }}
      />
    </div>
  );
}