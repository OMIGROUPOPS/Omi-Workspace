import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import Link from 'next/link';
import { SportsGrid } from '@/components/edge/SportsGrid';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const SPORT_MAPPING: Record<string, string> = {
  'americanfootball_nfl': 'NFL',
  'americanfootball_ncaaf': 'NCAAF',
  'basketball_nba': 'NBA',
  'icehockey_nhl': 'NHL',
  'basketball_ncaab': 'NCAAB',
  'baseball_mlb': 'MLB',
  'basketball_wnba': 'WNBA',
  'mma_mixed_martial_arts': 'MMA',
  'tennis_atp_australian_open': 'TENNIS_AO',
  'tennis_atp_french_open': 'TENNIS_FO',
  'tennis_atp_us_open': 'TENNIS_USO',
  'tennis_atp_wimbledon': 'TENNIS_WIM',
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

function processOddsApiGame(game: any) {
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
      consensus.h2h = { homePrice: median(h2hPrices.home), awayPrice: median(h2hPrices.away) };
    }
    if (spreadData.line.length > 0) {
      consensus.spreads = { line: median(spreadData.line), homePrice: median(spreadData.homePrice), awayPrice: median(spreadData.awayPrice) };
    }
    if (totalData.line.length > 0) {
      consensus.totals = { line: median(totalData.line), overPrice: median(totalData.overPrice), underPrice: median(totalData.underPrice) };
    }
  }

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: game.commence_time,
    consensus,
  };
}

async function fetchFromCache(sportKey: string) {
  try {
    const supabase = getSupabase();
    const { data, error } = await supabase
      .from('cached_odds')
      .select('game_data')
      .eq('sport_key', sportKey);

    if (error || !data) return [];

    return data
      .map((row: any) => processOddsApiGame(row.game_data))
      .filter(Boolean);
  } catch (e) {
    return [];
  }
}

interface PageProps {
  params: Promise<{ sport: string }>;
}

export default async function SportGamesPage({ params }: PageProps) {
  const { sport: sportKey } = await params;
  const sportInfo = SUPPORTED_SPORTS.find((s) => s.key === sportKey);

  if (!sportInfo) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Sport not found</h1>
          <Link href="/edge/portal/sports" className="text-emerald-400 hover:underline">Back to sports</Link>
        </div>
      </div>
    );
  }

  const backendSport = SPORT_MAPPING[sportKey] || sportKey.toUpperCase();
  let games = await fetchEdgesFromBackend(backendSport);
  let fromCache = false;

  // Fallback: if backend returns nothing, try Supabase cached_odds
  if (games.length === 0) {
    const cachedGames = await fetchFromCache(sportKey);
    if (cachedGames.length > 0) {
      fromCache = true;
      // Filter to upcoming games only
      const now = new Date();
      const upcoming = cachedGames
        .filter((g: any) => new Date(g.commenceTime).getTime() > now.getTime() - 3 * 60 * 60 * 1000)
        .sort((a: any, b: any) => new Date(a.commenceTime).getTime() - new Date(b.commenceTime).getTime());

      // Convert cached games to the format expected by SportsGrid
      const cachedWithBooks = upcoming.map((g: any) => ({
        game: {
          id: g.id,
          externalId: g.id,
          sportKey: g.sportKey,
          homeTeam: g.homeTeam,
          awayTeam: g.awayTeam,
          commenceTime: new Date(g.commenceTime),
          status: 'upcoming' as const,
        },
        bookmakerOdds: {
          consensus: { consensus: g.consensus, edge: { status: 'pass', adjustedConfidence: 0, edgeDelta: 0 } }
        },
        edgeCount: 0,  // Cached games don't have edge calculation yet
      }));

      const sorted = cachedWithBooks.sort((a: any, b: any) =>
        new Date(a.game.commenceTime).getTime() - new Date(b.game.commenceTime).getTime()
      );

      return (
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-6">
            <Link href="/edge/portal/sports" className="text-zinc-400 hover:text-zinc-200 transition-colors flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </Link>
            <div className="flex items-center gap-3">
              <span className="text-3xl">{sportInfo.icon}</span>
              <div>
                <h1 className="text-2xl font-bold">{sportInfo.name}</h1>
                <p className="text-zinc-400 text-sm">{sportInfo.group}</p>
              </div>
            </div>
          </div>
          {sorted.length === 0 && <div className="text-center py-12"><p className="text-zinc-400">No upcoming games found</p></div>}
          {sorted.length > 0 && <SportsGrid games={sorted} availableBooks={['consensus']} />}
        </div>
      );
    }
  }

  let error: string | null = null;
  if (games.length === 0) {
    error = 'No games found. The backend is unreachable and no cached data is available.';
  }

  // Transform backend data to match SportsGrid expected format
  const gamesWithAllBooks = games.map((game: any) => {
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

    // Build edge info
    const edge = {
      status: game.overall_confidence?.toLowerCase() || 'pass',
      adjustedConfidence: (game.composite_score || 0.5) * 100,
      edgeDelta: game.best_edge || 0,
    };

    // Calculate edge count - estimate based on backend data
    // Full detailed edge count is calculated on the game detail page
    // Here we estimate based on composite_score and pillar_scores
    let edgeCount = 0;
    const conf = (game.overall_confidence || '').toLowerCase();
    const score = game.composite_score || 0;

    if (conf === 'edge' || conf === 'strong' || conf === 'rare' || score >= 0.56) {
      // Base estimate: each strong pillar contributes potential edges
      const pillars = game.pillar_scores || {};
      let strongPillars = 0;
      for (const [, pillarScore] of Object.entries(pillars)) {
        if (typeof pillarScore === 'number' && pillarScore >= 0.6) strongPillars++;
      }

      // Estimate edges based on composite score and pillar strength
      // Score 0.86+ (RARE): likely 8-12 edges across markets/periods
      // Score 0.76+ (STRONG): likely 4-8 edges
      // Score 0.66+ (EDGE): likely 2-4 edges
      // Score 0.56+ (WATCH): likely 1-2 edges
      if (score >= 0.86) edgeCount = Math.max(8, strongPillars * 2);
      else if (score >= 0.76) edgeCount = Math.max(4, strongPillars + 2);
      else if (score >= 0.66) edgeCount = Math.max(2, strongPillars + 1);
      else if (score >= 0.56) edgeCount = Math.max(1, strongPillars);
    }

    return {
      game: {
        id: game.game_id,
        externalId: game.game_id,
        sportKey: sportKey,
        homeTeam: game.home_team,
        awayTeam: game.away_team,
        commenceTime: new Date(game.commence_time),
        status: 'upcoming' as const,
      },
      bookmakerOdds: {
        consensus: { consensus, edge }
      },
      pillars: game.pillar_scores,
      composite_score: game.composite_score,
      overall_confidence: game.overall_confidence,
      edgeCount,
    };
  });

  const sorted = [...gamesWithAllBooks].sort((a, b) => 
    new Date(a.game.commenceTime).getTime() - new Date(b.game.commenceTime).getTime()
  );

  // Filter out games that have already started (commenced more than 3 hours ago)
  const now = new Date();
  const filtered = sorted.filter(g => {
    const gameTime = new Date(g.game.commenceTime);
    const hoursAgo = (now.getTime() - gameTime.getTime()) / (1000 * 60 * 60);
    return hoursAgo < 3; // Show games that started less than 3 hours ago
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/edge/portal/sports" className="text-zinc-400 hover:text-zinc-200 transition-colors flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </Link>
        <div className="flex items-center gap-3">
          <span className="text-3xl">{sportInfo.icon}</span>
          <div>
            <h1 className="text-2xl font-bold">{sportInfo.name}</h1>
            <p className="text-zinc-400 text-sm">{sportInfo.group}</p>
          </div>
        </div>
      </div>

      {error && filtered.length === 0 && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6"><p className="text-red-400">{error}</p></div>}
      {!error && filtered.length === 0 && <div className="text-center py-12"><p className="text-zinc-400">No upcoming games found</p></div>}
      {filtered.length > 0 && <SportsGrid games={filtered} availableBooks={['consensus']} />}
    </div>
  );
}