import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { createOddsApiClient } from '@/lib/edge/api/odds-api';
import { GameCard } from '@/components/edge/GameCard';
import { americanToImplied, removeVigFromAmerican } from '@/lib/edge/utils/odds-math';
import Link from 'next/link';

interface PageProps {
  params: Promise<{ sport: string }>;
}

export default async function SportGamesPage({ params }: PageProps) {
  const { sport: sportKey } = await params;
  
  const sportInfo = SUPPORTED_SPORTS.find((s) => s.key === sportKey);
  
  if (!sportInfo) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Sport not found</h1>
          <Link href="/edge/portal/sports" className="text-emerald-400 hover:underline">
            Back to sports
          </Link>
        </div>
      </div>
    );
  }

  // Fetch odds from API
  const client = createOddsApiClient(process.env.ODDS_API_KEY!);
  
  let games: any[] = [];
  let error: string | null = null;

  try {
    const data = await client.fetchOdds(sportKey, {
      regions: 'us',
      markets: 'h2h,spreads,totals',
      oddsFormat: 'american',
    });
    games = data;
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to fetch odds';
  }

  // Transform API data to our format
  const gamesWithOdds = games.map((game) => {
    // Get consensus odds from first bookmaker (we'll improve this later)
    const bookmaker = game.bookmakers?.[0];
    
    let consensus: any = undefined;
    
    if (bookmaker) {
      const h2hMarket = bookmaker.markets.find((m: any) => m.key === 'h2h');
      const spreadsMarket = bookmaker.markets.find((m: any) => m.key === 'spreads');
      const totalsMarket = bookmaker.markets.find((m: any) => m.key === 'totals');

      if (h2hMarket) {
        const home = h2hMarket.outcomes.find((o: any) => o.name === game.home_team);
        const away = h2hMarket.outcomes.find((o: any) => o.name === game.away_team);
        if (home && away) {
          const { true1, true2 } = removeVigFromAmerican(home.price, away.price);
          consensus = {
            ...consensus,
            h2h: {
              homePrice: home.price,
              awayPrice: away.price,
              homeImplied: true1,
              awayImplied: true2,
            },
          };
        }
      }

      if (spreadsMarket) {
        const home = spreadsMarket.outcomes.find((o: any) => o.name === game.home_team);
        const away = spreadsMarket.outcomes.find((o: any) => o.name === game.away_team);
        if (home && away) {
          const { true1, true2 } = removeVigFromAmerican(home.price, away.price);
          consensus = {
            ...consensus,
            spreads: {
              line: home.point,
              homePrice: home.price,
              awayPrice: away.price,
              homeImplied: true1,
              awayImplied: true2,
            },
          };
        }
      }

      if (totalsMarket) {
        const over = totalsMarket.outcomes.find((o: any) => o.name === 'Over');
        const under = totalsMarket.outcomes.find((o: any) => o.name === 'Under');
        if (over && under) {
          const { true1, true2 } = removeVigFromAmerican(over.price, under.price);
          consensus = {
            ...consensus,
            totals: {
              line: over.point,
              overPrice: over.price,
              underPrice: under.price,
              overImplied: true1,
              underImplied: true2,
            },
          };
        }
      }
    }

    return {
      game: {
        id: game.id,
        externalId: game.id,
        sportKey: game.sport_key,
        homeTeam: game.home_team,
        awayTeam: game.away_team,
        commenceTime: new Date(game.commence_time),
        status: 'upcoming' as const,
      },
      consensus,
      edge: undefined, // We'll add edge calculations later
    };
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link 
            href="/edge/portal/sports" 
            className="text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            ← Back
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-3xl">{sportInfo.icon}</span>
            <div>
              <h1 className="text-2xl font-bold">{sportInfo.name}</h1>
              <p className="text-zinc-400 text-sm">{sportInfo.group}</p>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-8">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* No Games */}
        {!error && gamesWithOdds.length === 0 && (
          <div className="text-center py-12">
            <p className="text-zinc-400">No upcoming games found</p>
          </div>
        )}

        {/* Games Grid */}
        {gamesWithOdds.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {gamesWithOdds.map(({ game, consensus, edge }) => (
              <GameCard
                key={game.id}
                game={game}
                consensus={consensus}
                edge={edge}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}