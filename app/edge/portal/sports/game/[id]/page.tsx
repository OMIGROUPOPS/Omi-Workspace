import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import Link from 'next/link';
import { GameDetailClient } from '@/components/edge/GameDetailClient';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { calculateGameCEQ, type ExtendedOddsSnapshot, type GameCEQ } from '@/lib/edge/engine/edgescout';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

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
  // Try backend first
  try {
    let url = `${BACKEND_URL}/api/lines/${gameId}?market=${market}&period=${period}`;
    if (book) url += `&book=${book}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.snapshots && data.snapshots.length > 0) return data.snapshots;
    }
  } catch (e) {
    // Backend unavailable, fall through to Supabase
  }

  // Fallback: query odds_snapshots from Supabase
  try {
    const marketMap: Record<string, string> = {
      'spread': 'spreads',
      'moneyline': 'h2h',
      'total': 'totals',
    };
    // Build market key with period suffix (e.g., spreads_h1 for 1st half spread)
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
    if (error || !data || data.length === 0) return [];

    // Convert to the format expected by the line chart
    return data.map((row: any) => ({
      snapshot_time: row.snapshot_time,
      book_key: row.book_key,
      outcome_type: row.outcome_type,
      line: row.line,
      odds: row.odds,
    }));
  } catch (e) {
    console.error('[GameDetail] Snapshot fallback error:', e);
    return [];
  }
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
        if (home && away) {
          out.h2h = {
            home: { price: home.price, edge: 0 },
            away: { price: away.price, edge: 0 },
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
    const sportsToSearch = ['NFL', 'NBA', 'NHL', 'NCAAF', 'NCAAB', 'MLB', 'WNBA', 'MMA', 'TENNIS_AO', 'TENNIS_FO', 'TENNIS_USO', 'TENNIS_WIM'];
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

  // Fetch per-book odds data
  const perBookOdds = await fetchPerBookOdds(backendSportKey, gameId);
  
  // Fetch props
  const propsData = await fetchProps(backendSportKey, gameId);
  
  // Fetch consensus data as fallback
  const consensusData = await fetchConsensus(backendSportKey, gameId);

  // Fetch line history for all periods
  const [
    spreadHistory, mlHistory, totalHistory,
    spreadH1History, totalH1History,
    spreadH2History, totalH2History
  ] = await Promise.all([
    fetchLineHistory(gameId, 'spread', 'full'),
    fetchLineHistory(gameId, 'moneyline', 'full'),
    fetchLineHistory(gameId, 'total', 'full'),
    fetchLineHistory(gameId, 'spread', 'h1'),
    fetchLineHistory(gameId, 'total', 'h1'),
    fetchLineHistory(gameId, 'spread', 'h2'),
    fetchLineHistory(gameId, 'total', 'h2'),
  ]);

  const homeTeam = gameData.home_team;
  const awayTeam = gameData.away_team;
  const commenceTime = gameData.commence_time;
  const compositeScore = gameData.composite_score || 0.5;
  const confidence = gameData.overall_confidence || 'PASS';

  // Build line history object
  const lineHistory = {
    full: { spread: spreadHistory, moneyline: mlHistory, total: totalHistory },
    h1: { spread: spreadH1History, total: totalH1History },
    h2: { spread: spreadH2History, total: totalH2History },
  };

  // Fetch data for CEQ calculation
  const [ceqSnapshots, openingLine] = await Promise.all([
    fetchSnapshotsForCEQ(gameId),
    fetchOpeningLine(gameId),
  ]);

  // Use per-book odds if available, otherwise fall back to consensus
  let bookmakers: Record<string, any> = {};
  let availableBooks: string[] = [];

  if (perBookOdds && perBookOdds.bookmakers) {
    // Use real per-book data
    bookmakers = perBookOdds.bookmakers;
    availableBooks = perBookOdds.books || Object.keys(bookmakers);
    
    // Add line history and props to each book's marketGroups
    Object.keys(bookmakers).forEach(book => {
      if (bookmakers[book].marketGroups) {
        bookmakers[book].marketGroups.lineHistory = lineHistory;
        // Props are already filtered by book in the backend
        if (!bookmakers[book].marketGroups.playerProps || bookmakers[book].marketGroups.playerProps.length === 0) {
          bookmakers[book].marketGroups.playerProps = propsData.filter((p: any) => p.book === book);
        }
      }
    });
  } else {
    // Try cached raw data for per-book enriched markets (props, alts, halves, team totals)
    let rawData = cachedRaw;
    if (!rawData) {
      // Game came from backend but perBookOdds failed — try cache
      const cached = await fetchGameFromCache(gameId);
      if (cached) rawData = cached.game_data;
    }

    if (rawData && rawData.bookmakers && rawData.bookmakers.length > 0) {
      // Build per-book marketGroups from cached Odds API data
      const perBook = buildPerBookFromCache(rawData);
      bookmakers = perBook;
      availableBooks = Object.keys(perBook);

      // Inject line history into each book
      Object.keys(bookmakers).forEach(book => {
        if (bookmakers[book].marketGroups) {
          bookmakers[book].marketGroups.lineHistory = lineHistory;
        }
      });
    } else {
      // Last resort: consensus fallback (only core markets)
      const consensus = gameData.consensus_odds || consensusData?.consensus || {};
      const edges = gameData.edges || {};

      const buildMarket = (marketData: any, prefix: string) => {
        if (!marketData) return { h2h: null, spreads: null, totals: null };
        const result: any = { h2h: null, spreads: null, totals: null };
        if (marketData.spreads?.home) {
          result.spreads = {
            home: { line: marketData.spreads.home.line, price: marketData.spreads.home.odds, edge: edges[`${prefix}spread_home`]?.edge_pct || null },
            away: { line: marketData.spreads.away?.line, price: marketData.spreads.away?.odds, edge: edges[`${prefix}spread_away`]?.edge_pct || null },
          };
        }
        if (marketData.h2h?.home !== undefined) {
          result.h2h = {
            home: { price: marketData.h2h.home, edge: edges[`${prefix}ml_home`]?.edge_pct || null },
            away: { price: marketData.h2h.away, edge: edges[`${prefix}ml_away`]?.edge_pct || null },
          };
        }
        if (marketData.totals?.over) {
          result.totals = {
            line: marketData.totals.over.line,
            over: { price: marketData.totals.over.odds, edge: edges[`${prefix}total_over`]?.edge_pct || null },
            under: { price: marketData.totals.under?.odds, edge: edges[`${prefix}total_under`]?.edge_pct || null },
          };
        }
        return result;
      };

      const marketGroups: any = {
        fullGame: buildMarket(consensus, ''),
        firstHalf: buildMarket(consensus.first_half, 'h1_'),
        secondHalf: buildMarket(consensus.second_half, 'h2_'),
        q1: buildMarket(consensus.quarters?.q1, 'q1_'),
        q2: buildMarket(consensus.quarters?.q2, 'q2_'),
        q3: buildMarket(consensus.quarters?.q3, 'q3_'),
        q4: buildMarket(consensus.quarters?.q4, 'q4_'),
        p1: buildMarket(consensus.periods?.p1, 'p1_'),
        p2: buildMarket(consensus.periods?.p2, 'p2_'),
        p3: buildMarket(consensus.periods?.p3, 'p3_'),
        teamTotals: null,
        playerProps: propsData,
        alternates: { spreads: [], totals: [] },
        lineHistory: lineHistory,
      };

      const defaultBooks = ['fanduel', 'draftkings'];
      availableBooks = defaultBooks;
      availableBooks.forEach(book => {
        bookmakers[book] = { marketGroups };
      });
    }
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
  const sportConfig = SUPPORTED_SPORTS.find(s => s.key === fullSportKey);

  // Calculate CEQ (Composite Edge Quotient) using EdgeScout framework
  let ceqData: GameCEQ | null = null;
  const consensus = gameData.consensus_odds || {};

  if (consensus.spreads || consensus.h2h || consensus.totals) {
    const gameOdds = {
      spreads: consensus.spreads?.home ? {
        home: { line: consensus.spreads.home.line || consensus.spreads.home, odds: consensus.spreads.home.odds || -110 },
        away: { line: consensus.spreads.away?.line || -(consensus.spreads.home.line || 0), odds: consensus.spreads.away?.odds || -110 },
      } : undefined,
      h2h: consensus.h2h ? {
        home: consensus.h2h.home,
        away: consensus.h2h.away,
      } : undefined,
      totals: consensus.totals?.over ? {
        line: consensus.totals.over.line,
        over: consensus.totals.over.odds || -110,
        under: consensus.totals.under?.odds || -110,
      } : undefined,
    };

    const openingData = {
      spreads: openingLine !== undefined ? {
        home: openingLine,
        away: -openingLine,
      } : undefined,
    };

    ceqData = calculateGameCEQ(
      gameOdds,
      openingData,
      ceqSnapshots,
      {}, // allBooksOdds - would need to aggregate
      {
        spreads: consensus.spreads?.home ? { home: consensus.spreads.home.odds || -110, away: consensus.spreads.away?.odds || -110 } : undefined,
        h2h: consensus.h2h ? { home: consensus.h2h.home, away: consensus.h2h.away } : undefined,
        totals: consensus.totals?.over ? { over: consensus.totals.over.odds || -110, under: consensus.totals.under?.odds || -110 } : undefined,
      }
    );
  }

  // Use CEQ for display if available
  const ceqBestScore = ceqData?.bestEdge?.ceq;
  const displayScore = ceqBestScore !== undefined ? ceqBestScore / 100 : compositeScore;
  const displayConfidence = ceqData?.bestEdge?.confidence || confidence;

  const scoreColor = displayScore >= 0.5 ? 'text-emerald-400' : 'text-red-400';
  const scoreBg = displayScore >= 0.5 ? 'bg-emerald-500/10' : 'bg-red-500/10';

  const hasProps = (propsData && propsData.length > 0) ||
    Object.values(bookmakers).some((b: any) => b.marketGroups?.playerProps?.length > 0);
  const hasAlternates = Object.values(bookmakers).some((b: any) =>
    (b.marketGroups?.alternates?.spreads?.length > 0) || (b.marketGroups?.alternates?.totals?.length > 0));
  const hasTeamTotals = Object.values(bookmakers).some((b: any) =>
    b.marketGroups?.teamTotals?.home?.over || b.marketGroups?.teamTotals?.away?.over);
  const isNHL = fullSportKey.includes('icehockey');
  const isFootball = fullSportKey.includes('football');
  const isBasketball = fullSportKey.includes('basketball');

  // Check if we have any half/quarter data
  const hasFirstHalf = Object.values(bookmakers).some((b: any) =>
    b.marketGroups?.firstHalf?.spreads || b.marketGroups?.firstHalf?.h2h || b.marketGroups?.firstHalf?.totals
  );
  const hasSecondHalf = Object.values(bookmakers).some((b: any) =>
    b.marketGroups?.secondHalf?.spreads || b.marketGroups?.secondHalf?.h2h || b.marketGroups?.secondHalf?.totals
  );

  return (
    <div className="py-6">
      <div className="mb-6">
        <Link
          href="/edge/portal/sports"
          className="inline-flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </Link>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-3xl">{sportConfig?.icon || '🏆'}</div>
            <div>
              <h1 className="text-2xl font-bold text-zinc-100">{awayTeam} @ {homeTeam}</h1>
              <p className="text-zinc-400">
                {new Date(commenceTime).toLocaleString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1.5 rounded-lg ${scoreBg} flex items-center gap-2`}>
              <span className="text-xs text-zinc-400">CEQ Score</span>
              <span className={`text-lg font-bold ${scoreColor}`}>
                {(displayScore * 100).toFixed(0)}%
              </span>
            </div>
            <span className={`text-xs font-medium px-2 py-1 rounded ${
              displayConfidence === 'RARE' ? 'bg-purple-500/20 text-purple-400' :
              displayConfidence === 'STRONG' || displayConfidence === 'STRONG_EDGE' ? 'bg-emerald-500/20 text-emerald-400' :
              displayConfidence === 'EDGE' ? 'bg-blue-500/20 text-blue-300' :
              displayConfidence === 'WATCH' ? 'bg-amber-500/10 text-amber-400' :
              'bg-zinc-800 text-zinc-500'
            }`}>
              {displayConfidence}
            </span>
            {ceqData?.bestEdge && (
              <span className="text-[10px] text-zinc-500">
                {ceqData.bestEdge.side} {ceqData.bestEdge.market}
              </span>
            )}
          </div>
        </div>
      </div>

      <GameDetailClient
        gameData={{ id: gameId, homeTeam, awayTeam, sportKey: fullSportKey, commenceTime }}
        bookmakers={bookmakers}
        availableBooks={availableBooks}
        userTier="tier_1"
        userEmail={userEmail}
        isDemo={isDemo}
        ceq={ceqData}
        availableTabs={{
          fullGame: true,
          firstHalf: hasFirstHalf || isFootball || isBasketball || isNHL,
          secondHalf: hasSecondHalf || isFootball || isBasketball,
          q1: isFootball || isBasketball,
          q2: isFootball || isBasketball,
          q3: isFootball || isBasketball,
          q4: isFootball || isBasketball,
          p1: isNHL,
          p2: isNHL,
          p3: isNHL,
          props: hasProps,
          alternates: hasAlternates,
          teamTotals: hasTeamTotals,
        }}
      />
    </div>
  );
}