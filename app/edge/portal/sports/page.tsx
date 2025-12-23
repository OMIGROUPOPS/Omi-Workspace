import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { createOddsApiClient } from '@/lib/edge/api/odds-api';
import { removeVigFromAmerican } from '@/lib/edge/utils/odds-math';
import Link from 'next/link';
import { SportsHomeGrid } from '@/components/edge/SportsHomeGrid';

const FEATURED_SPORTS = [
  'americanfootball_nfl',
  'americanfootball_ncaaf',
  'basketball_nba', 
  'icehockey_nhl',
  'basketball_ncaab',
];

async function fetchSportGames(client: any, sportKey: string) {
  try {
    const data = await client.fetchOdds(sportKey, {
      regions: 'us',
      markets: 'h2h,spreads,totals',
      oddsFormat: 'american',
    });
    return data.slice(0, 10); // Get first 10 games per sport
  } catch (e) {
    return [];
  }
}

function processGame(game: any, sportKey: string) {
  const bookmaker = game.bookmakers?.[0];
  if (!bookmaker) return null;

  const h2hMarket = bookmaker.markets?.find((m: any) => m.key === 'h2h');
  const spreadsMarket = bookmaker.markets?.find((m: any) => m.key === 'spreads');
  const totalsMarket = bookmaker.markets?.find((m: any) => m.key === 'totals');

  let consensus: any = {};

  if (h2hMarket) {
    const home = h2hMarket.outcomes.find((o: any) => o.name === game.home_team);
    const away = h2hMarket.outcomes.find((o: any) => o.name === game.away_team);
    if (home && away) {
      consensus.h2h = { homePrice: home.price, awayPrice: away.price };
    }
  }

  if (spreadsMarket) {
    const home = spreadsMarket.outcomes.find((o: any) => o.name === game.home_team);
    const away = spreadsMarket.outcomes.find((o: any) => o.name === game.away_team);
    if (home && away) {
      consensus.spreads = { 
        line: home.point, 
        homePrice: home.price, 
        awayPrice: away.price 
      };
    }
  }

  if (totalsMarket) {
    const over = totalsMarket.outcomes.find((o: any) => o.name === 'Over');
    const under = totalsMarket.outcomes.find((o: any) => o.name === 'Under');
    if (over && under) {
      consensus.totals = { 
        line: over.point, 
        overPrice: over.price, 
        underPrice: under.price 
      };
    }
  }

  return {
    id: game.id,
    sportKey: game.sport_key,
    homeTeam: game.home_team,
    awayTeam: game.away_team,
    commenceTime: new Date(game.commence_time),
    consensus,
  };
}

export default async function SportsPage() {
  const client = createOddsApiClient(process.env.ODDS_API_KEY!);

  const allGames: Record<string, any[]> = {};

  for (const sportKey of FEATURED_SPORTS) {
    const games = await fetchSportGames(client, sportKey);
    const processed = games
      .map((g: any) => processGame(g, sportKey))
      .filter(Boolean)
      .sort((a: any, b: any) => a.commenceTime.getTime() - b.commenceTime.getTime());
    
    if (processed.length > 0) {
      allGames[sportKey] = processed;
    }
  }

  return (
    <div className="py-4">
      <SportsHomeGrid games={allGames} />
    </div>
  );
}