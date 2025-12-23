import { SUPPORTED_SPORTS, PILLAR_WEIGHTS_DEFAULT } from '@/lib/edge/utils/constants';
import { createOddsApiClient } from '@/lib/edge/api/odds-api';
import { removeVigFromAmerican } from '@/lib/edge/utils/odds-math';
import Link from 'next/link';
import { SportsGrid } from '@/components/edge/SportsGrid';

function generateMockPillarScores(gameId: string) {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const seededRandom = (offset: number) => {
    const x = Math.sin(seed + offset) * 10000;
    return 0.5 + (x - Math.floor(x) - 0.5) * 0.4;
  };
  return {
    execution: seededRandom(1),
    incentives: seededRandom(2),
    shocks: seededRandom(3),
    timeDecay: seededRandom(4),
    flow: seededRandom(5),
  };
}

function calculateEdge(bookImpliedProb: number, pillarScores: any) {
  const weights = PILLAR_WEIGHTS_DEFAULT;
  const weightedSum =
    (pillarScores.execution - 0.5) * weights.EXECUTION +
    (pillarScores.incentives - 0.5) * weights.INCENTIVES +
    (pillarScores.shocks - 0.5) * weights.SHOCKS +
    (pillarScores.timeDecay - 0.5) * weights.TIME_DECAY +
    (pillarScores.flow - 0.5) * weights.FLOW;
  const pillarAdjustment = weightedSum * 0.3;
  const omiTrueProb = Math.max(0.01, Math.min(0.99, bookImpliedProb + pillarAdjustment));
  return { omiTrueProb, edgeDelta: omiTrueProb - bookImpliedProb, pillarAdjustment };
}

function getEdgeStatus(confidence: number) {
  if (confidence >= 45) return 'rare';
  if (confidence >= 38) return 'strong_edge';
  if (confidence >= 32) return 'edge';
  if (confidence >= 25) return 'watch';
  return 'pass';
}

function runDecisionGate(pillarScores: any, edgeDelta: number) {
  const weights = PILLAR_WEIGHTS_DEFAULT;
  const weightedScore =
    pillarScores.execution * weights.EXECUTION +
    pillarScores.incentives * weights.INCENTIVES +
    pillarScores.shocks * weights.SHOCKS +
    pillarScores.timeDecay * weights.TIME_DECAY +
    pillarScores.flow * weights.FLOW;
  const pillarConfidence = weightedScore * 50;
  const edgeBonus = Math.min(Math.abs(edgeDelta) * 500, 50);
  const rawConfidence = pillarConfidence + edgeBonus;
  const adjustedConfidence = Math.min(rawConfidence * 0.8, 100);
  return { rawConfidence, adjustedConfidence, status: getEdgeStatus(adjustedConfidence) };
}

function processBookmaker(bookmaker: any, game: any) {
  const h2hMarket = bookmaker.markets.find((m: any) => m.key === 'h2h');
  const spreadsMarket = bookmaker.markets.find((m: any) => m.key === 'spreads');
  const totalsMarket = bookmaker.markets.find((m: any) => m.key === 'totals');
  let consensus: any = undefined;
  let edge: any = undefined;

  if (h2hMarket) {
    const home = h2hMarket.outcomes.find((o: any) => o.name === game.home_team);
    const away = h2hMarket.outcomes.find((o: any) => o.name === game.away_team);
    if (home && away) {
      const { true1, true2 } = removeVigFromAmerican(home.price, away.price);
      consensus = { ...consensus, h2h: { homePrice: home.price, awayPrice: away.price, homeImplied: true1, awayImplied: true2 } };
      const pillarScores = generateMockPillarScores(game.id);
      const edgeCalc = calculateEdge(true1, pillarScores);
      const decision = runDecisionGate(pillarScores, edgeCalc.edgeDelta);
      edge = { bookImpliedProb: true1, omiTrueProb: edgeCalc.omiTrueProb, edgeDelta: edgeCalc.edgeDelta, rawConfidence: decision.rawConfidence, adjustedConfidence: decision.adjustedConfidence, status: decision.status };
    }
  }

  if (spreadsMarket) {
    const home = spreadsMarket.outcomes.find((o: any) => o.name === game.home_team);
    const away = spreadsMarket.outcomes.find((o: any) => o.name === game.away_team);
    if (home && away) {
      const { true1, true2 } = removeVigFromAmerican(home.price, away.price);
      consensus = { ...consensus, spreads: { line: home.point, homePrice: home.price, awayPrice: away.price, homeImplied: true1, awayImplied: true2 } };
    }
  }

  if (totalsMarket) {
    const over = totalsMarket.outcomes.find((o: any) => o.name === 'Over');
    const under = totalsMarket.outcomes.find((o: any) => o.name === 'Under');
    if (over && under) {
      const { true1, true2 } = removeVigFromAmerican(over.price, under.price);
      consensus = { ...consensus, totals: { line: over.point, overPrice: over.price, underPrice: under.price, overImplied: true1, underImplied: true2 } };
    }
  }

  return { consensus, edge };
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

  const client = createOddsApiClient(process.env.ODDS_API_KEY!);
  let games: any[] = [];
  let error: string | null = null;
  let availableBooks: string[] = [];

  try {
    const data = await client.fetchOdds(sportKey, { regions: 'us', markets: 'h2h,spreads,totals', oddsFormat: 'american' });
    games = data;
    const bookSet = new Set<string>();
    games.forEach((game: any) => game.bookmakers?.forEach((b: any) => bookSet.add(b.key)));
    availableBooks = Array.from(bookSet);
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to fetch odds';
  }

  const gamesWithAllBooks = games.map((game) => {
    const bookmakerOdds: Record<string, { consensus: any; edge: any }> = {};
    game.bookmakers?.forEach((bookmaker: any) => { bookmakerOdds[bookmaker.key] = processBookmaker(bookmaker, game); });
    return {
      game: { id: game.id, externalId: game.id, sportKey: game.sport_key, homeTeam: game.home_team, awayTeam: game.away_team, commenceTime: new Date(game.commence_time), status: 'upcoming' as const },
      bookmakerOdds,
    };
  });

  const sorted = [...gamesWithAllBooks].sort((a, b) => new Date(a.game.commenceTime).getTime() - new Date(b.game.commenceTime).getTime());

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

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6"><p className="text-red-400">{error}</p></div>}
      {!error && sorted.length === 0 && <div className="text-center py-12"><p className="text-zinc-400">No upcoming games found</p></div>}
      {sorted.length > 0 && <SportsGrid games={sorted} availableBooks={availableBooks} />}
    </div>
  );
}