import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const SPORT_MAPPING: Record<string, string> = {
  'NFL': 'americanfootball_nfl',
  'NCAAF': 'americanfootball_ncaaf',
  'NBA': 'basketball_nba',
  'NHL': 'icehockey_nhl',
  'NCAAB': 'basketball_ncaab',
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

function processBackendGame(game: any) {
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

  return {
    id: game.game_id,
    sportKey: SPORT_MAPPING[game.sport] || game.sport,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: new Date(game.commence_time),
    consensus,
    edges: game.edges,
    pillars: game.pillars,
    composite_score: game.composite_score,
    overall_confidence: game.overall_confidence,
    best_bet: game.best_bet,
    best_edge: game.best_edge,
  };
}

export default async function SportsPage() {
  const sports = ['NFL', 'NCAAF', 'NBA', 'NHL', 'NCAAB'];
  const allGames: Record<string, any[]> = {};

  for (const sport of sports) {
    const games = await fetchEdgesFromBackend(sport);
    const processed = games
      .map(processBackendGame)
      .filter(Boolean)
      .sort((a: any, b: any) => a.commenceTime.getTime() - b.commenceTime.getTime());
    
    const frontendKey = SPORT_MAPPING[sport];
    if (processed.length > 0 && frontendKey) {
      allGames[frontendKey] = processed;
    }
  }

  return (
    <div className="py-4">
      <SportsHomeGrid games={allGames} />
    </div>
  );
}