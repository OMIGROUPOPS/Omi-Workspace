import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import Link from 'next/link';
import { SportsGrid } from '@/components/edge/SportsGrid';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const SPORT_MAPPING: Record<string, string> = {
  'americanfootball_nfl': 'NFL',
  'americanfootball_ncaaf': 'NCAAF',
  'basketball_nba': 'NBA',
  'icehockey_nhl': 'NHL',
  'basketball_ncaab': 'NCAAB',
};

async function fetchEdgesFromBackend(sport: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/edges/${sport}`, {
      cache: 'no-store'
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.games || [];
  } catch (e) {
    console.error(`Failed to fetch ${sport}:`, e);
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
  const games = await fetchEdgesFromBackend(backendSport);
  
  let error: string | null = null;
  if (games.length === 0) {
    error = 'No games found. Make sure the backend is running and data has been fetched.';
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