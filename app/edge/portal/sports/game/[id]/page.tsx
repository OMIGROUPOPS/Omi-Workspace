import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import { createOddsApiClient } from '@/lib/edge/api/odds-api';
import Link from 'next/link';
import { GameDetailClient } from '@/components/edge/GameDetailClient';

function generateMockEdge(id: string, offset: number = 0): number {
  const seed = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + offset;
  const x = Math.sin(seed) * 10000;
  return (x - Math.floor(x) - 0.5) * 0.08;
}

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ sport?: string }>;
}

// Get sport-specific markets to avoid 422 errors
function getMarketsForSport(sportKey: string): string {
  const baseMarkets = ['h2h', 'spreads', 'totals'];
  const halfMarkets = ['h2h_h1', 'spreads_h1', 'totals_h1', 'h2h_h2', 'spreads_h2', 'totals_h2'];
  const quarterMarkets = ['h2h_q1', 'spreads_q1', 'totals_q1', 'h2h_q2', 'spreads_q2', 'totals_q2', 'h2h_q3', 'spreads_q3', 'totals_q3', 'h2h_q4', 'spreads_q4', 'totals_q4'];
  const periodMarkets = ['h2h_p1', 'spreads_p1', 'totals_p1', 'h2h_p2', 'spreads_p2', 'totals_p2', 'h2h_p3', 'spreads_p3', 'totals_p3'];
  const altMarkets = ['alternate_spreads', 'alternate_totals', 'team_totals'];

  // NFL props
  const nflProps = [
    'player_pass_tds', 'player_pass_yds', 'player_pass_completions', 'player_pass_attempts',
    'player_rush_yds', 'player_rush_attempts', 'player_receptions', 'player_reception_yds',
    'player_anytime_td', 'player_kicking_points', 'player_field_goals'
  ];

  // NBA props
  const nbaProps = [
    'player_points', 'player_rebounds', 'player_assists', 'player_threes',
    'player_blocks', 'player_steals', 'player_turnovers',
    'player_points_rebounds_assists', 'player_points_rebounds',
    'player_points_assists', 'player_rebounds_assists', 'player_double_double'
  ];

  // NHL props
  const nhlProps = [
    'player_goals', 'player_assists', 'player_points', 'player_shots_on_goal',
    'player_power_play_points', 'player_blocked_shots'
  ];

  let markets = [...baseMarkets];

  if (sportKey.includes('nfl') || sportKey.includes('ncaaf')) {
    markets = [...markets, ...halfMarkets, ...quarterMarkets, ...altMarkets, ...nflProps];
  } else if (sportKey.includes('nba') || sportKey.includes('ncaab') || sportKey.includes('wnba') || sportKey.includes('wncaab')) {
    markets = [...markets, ...halfMarkets, ...quarterMarkets, ...altMarkets, ...nbaProps];
  } else if (sportKey.includes('nhl') || sportKey.includes('icehockey')) {
    markets = [...markets, ...periodMarkets, ...altMarkets, ...nhlProps];
  } else if (sportKey.includes('soccer')) {
    markets = [...markets, 'btts', 'draw_no_bet'];
  } else {
    // Default - just base markets
    markets = [...markets, ...altMarkets];
  }

  return markets.join(',');
}

export default async function GameDetailPage({ params, searchParams }: PageProps) {
  const { id: gameId } = await params;
  const { sport: querySport } = await searchParams;

  console.log('[GameDetail] gameId:', gameId);
  console.log('[GameDetail] querySport:', querySport);

  const client = createOddsApiClient(process.env.ODDS_API_KEY!);
  
  let sportKey: string = '';
  let gameInfo: any = null;

  if (querySport) {
    try {
      console.log('[GameDetail] Fetching events for sport:', querySport);
      const events = await client.fetchEvents(querySport);
      console.log('[GameDetail] Found', events.length, 'events');
      const found = events.find((e) => e.id === gameId);
      if (found) {
        console.log('[GameDetail] Found game:', found.home_team, 'vs', found.away_team);
        sportKey = querySport;
        gameInfo = found;
      } else {
        console.log('[GameDetail] Game ID not found in events');
      }
    } catch (e) {
      console.error('[GameDetail] Failed to fetch from query sport:', e);
    }
  }

  if (!sportKey || !gameInfo) {
    const sportsToSearch = [
      'americanfootball_nfl', 'basketball_nba', 'icehockey_nhl',
      'americanfootball_ncaaf', 'basketball_ncaab'
    ];
    
    for (const sport of sportsToSearch) {
      if (sport === querySport) continue;
      try {
        const events = await client.fetchEvents(sport);
        const found = events.find((e) => e.id === gameId);
        if (found) {
          sportKey = sport;
          gameInfo = found;
          break;
        }
      } catch (e) {
        continue;
      }
    }
  }

  if (!sportKey || !gameInfo) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Game not found</h1>
          <p className="text-zinc-500 mb-4 text-sm">ID: {gameId}</p>
          <Link href="/edge/portal/sports" className="text-emerald-400 hover:underline">
            Back to sports
          </Link>
        </div>
      </div>
    );
  }

  // Get sport-specific markets
  const allMarkets = getMarketsForSport(sportKey);
  console.log('[GameDetail] Requesting markets for', sportKey);

  let rawOdds: any = null;
  try {
    rawOdds = await client.fetchEventOdds(sportKey, gameId, { markets: allMarkets });
    console.log('[GameDetail] Got odds, bookmakers:', rawOdds?.bookmakers?.length || 0);
    if (rawOdds?.bookmakers?.[0]?.markets) {
      const marketKeys = rawOdds.bookmakers[0].markets.map((m: any) => m.key);
      console.log('[GameDetail] Markets returned:', marketKeys);
    }
  } catch (e) {
    console.error('[GameDetail] Failed to fetch odds:', e);
  }

  if (!rawOdds?.bookmakers?.length) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">No odds available</h1>
          <p className="text-zinc-500 mb-4">Odds for this game are not yet available</p>
          <Link href={`/edge/portal/sports/${sportKey}`} className="text-emerald-400 hover:underline">
            Back to games
          </Link>
        </div>
      </div>
    );
  }

  const homeTeam = gameInfo.home_team;
  const awayTeam = gameInfo.away_team;

  function processBookmakerOdds(bookmaker: any) {
    const marketGroups: any = {
      fullGame: { h2h: null, spreads: null, totals: null },
      firstHalf: { h2h: null, spreads: null, totals: null },
      secondHalf: { h2h: null, spreads: null, totals: null },
      q1: { h2h: null, spreads: null, totals: null },
      q2: { h2h: null, spreads: null, totals: null },
      q3: { h2h: null, spreads: null, totals: null },
      q4: { h2h: null, spreads: null, totals: null },
      p1: { h2h: null, spreads: null, totals: null },
      p2: { h2h: null, spreads: null, totals: null },
      p3: { h2h: null, spreads: null, totals: null },
      teamTotals: null,
      playerProps: [],
      alternates: { spreads: [], totals: [] },
    };

    for (const market of bookmaker.markets || []) {
      const key = market.key;
      const outcomes = market.outcomes || [];

      if (key === 'h2h') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.fullGame.h2h = {
            home: { price: home.price, edge: generateMockEdge(gameId, 1) },
            away: { price: away.price, edge: generateMockEdge(gameId, 2) },
          };
        }
      } else if (key === 'spreads') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.fullGame.spreads = {
            home: { line: home.point, price: home.price, edge: generateMockEdge(gameId, 3) },
            away: { line: away.point, price: away.price, edge: generateMockEdge(gameId, 4) },
          };
        }
      } else if (key === 'totals') {
        const over = outcomes.find((o: any) => o.name === 'Over');
        const under = outcomes.find((o: any) => o.name === 'Under');
        if (over && under) {
          marketGroups.fullGame.totals = {
            line: over.point,
            over: { price: over.price, edge: generateMockEdge(gameId, 5) },
            under: { price: under.price, edge: generateMockEdge(gameId, 6) },
          };
        }
      }
      else if (key === 'h2h_h1') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.firstHalf.h2h = {
            home: { price: home.price, edge: generateMockEdge(gameId, 11) },
            away: { price: away.price, edge: generateMockEdge(gameId, 12) },
          };
        }
      } else if (key === 'spreads_h1') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.firstHalf.spreads = {
            home: { line: home.point, price: home.price, edge: generateMockEdge(gameId, 13) },
            away: { line: away.point, price: away.price, edge: generateMockEdge(gameId, 14) },
          };
        }
      } else if (key === 'totals_h1') {
        const over = outcomes.find((o: any) => o.name === 'Over');
        const under = outcomes.find((o: any) => o.name === 'Under');
        if (over && under) {
          marketGroups.firstHalf.totals = {
            line: over.point,
            over: { price: over.price, edge: generateMockEdge(gameId, 15) },
            under: { price: under.price, edge: generateMockEdge(gameId, 16) },
          };
        }
      }
      else if (key === 'h2h_h2') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.secondHalf.h2h = {
            home: { price: home.price, edge: generateMockEdge(gameId, 21) },
            away: { price: away.price, edge: generateMockEdge(gameId, 22) },
          };
        }
      } else if (key === 'spreads_h2') {
        const home = outcomes.find((o: any) => o.name === homeTeam);
        const away = outcomes.find((o: any) => o.name === awayTeam);
        if (home && away) {
          marketGroups.secondHalf.spreads = {
            home: { line: home.point, price: home.price, edge: generateMockEdge(gameId, 23) },
            away: { line: away.point, price: away.price, edge: generateMockEdge(gameId, 24) },
          };
        }
      } else if (key === 'totals_h2') {
        const over = outcomes.find((o: any) => o.name === 'Over');
        const under = outcomes.find((o: any) => o.name === 'Under');
        if (over && under) {
          marketGroups.secondHalf.totals = {
            line: over.point,
            over: { price: over.price, edge: generateMockEdge(gameId, 25) },
            under: { price: under.price, edge: generateMockEdge(gameId, 26) },
          };
        }
      }
      else if (key.match(/_(q[1-4]|p[1-3])$/)) {
        const suffix = key.slice(-2);
        const type = key.replace(`_${suffix}`, '');
        const periodKey = suffix as 'q1' | 'q2' | 'q3' | 'q4' | 'p1' | 'p2' | 'p3';
        const offset = { q1: 30, q2: 40, q3: 50, q4: 60, p1: 70, p2: 80, p3: 90 }[periodKey] || 30;

        if (type === 'h2h') {
          const home = outcomes.find((o: any) => o.name === homeTeam);
          const away = outcomes.find((o: any) => o.name === awayTeam);
          if (home && away) {
            marketGroups[periodKey].h2h = {
              home: { price: home.price, edge: generateMockEdge(gameId, offset + 1) },
              away: { price: away.price, edge: generateMockEdge(gameId, offset + 2) },
            };
          }
        } else if (type === 'spreads') {
          const home = outcomes.find((o: any) => o.name === homeTeam);
          const away = outcomes.find((o: any) => o.name === awayTeam);
          if (home && away) {
            marketGroups[periodKey].spreads = {
              home: { line: home.point, price: home.price, edge: generateMockEdge(gameId, offset + 3) },
              away: { line: away.point, price: away.price, edge: generateMockEdge(gameId, offset + 4) },
            };
          }
        } else if (type === 'totals') {
          const over = outcomes.find((o: any) => o.name === 'Over');
          const under = outcomes.find((o: any) => o.name === 'Under');
          if (over && under) {
            marketGroups[periodKey].totals = {
              line: over.point,
              over: { price: over.price, edge: generateMockEdge(gameId, offset + 5) },
              under: { price: under.price, edge: generateMockEdge(gameId, offset + 6) },
            };
          }
        }
      }
      else if (key === 'team_totals') {
        const homeOver = outcomes.find((o: any) => o.name === homeTeam && o.description === 'Over');
        const homeUnder = outcomes.find((o: any) => o.name === homeTeam && o.description === 'Under');
        const awayOver = outcomes.find((o: any) => o.name === awayTeam && o.description === 'Over');
        const awayUnder = outcomes.find((o: any) => o.name === awayTeam && o.description === 'Under');
        
        marketGroups.teamTotals = {
          home: homeOver && homeUnder ? {
            line: homeOver.point,
            over: { price: homeOver.price, edge: generateMockEdge(gameId, 100) },
            under: { price: homeUnder.price, edge: generateMockEdge(gameId, 101) },
          } : null,
          away: awayOver && awayUnder ? {
            line: awayOver.point,
            over: { price: awayOver.price, edge: generateMockEdge(gameId, 102) },
            under: { price: awayUnder.price, edge: generateMockEdge(gameId, 103) },
          } : null,
        };
      }
      else if (key === 'alternate_spreads') {
        for (const o of outcomes) {
          marketGroups.alternates.spreads.push({
            team: o.name,
            line: o.point,
            price: o.price,
            edge: generateMockEdge(gameId + o.point, 110),
          });
        }
      }
      else if (key === 'alternate_totals') {
        for (const o of outcomes) {
          marketGroups.alternates.totals.push({
            type: o.name,
            line: o.point,
            price: o.price,
            edge: generateMockEdge(gameId + o.point, 120),
          });
        }
      }
      else if (key.startsWith('player_')) {
        const propType = key.replace('player_', '').replace(/_/g, ' ');
        for (const o of outcomes) {
          const playerName = o.description || o.name;
          const existing = marketGroups.playerProps.find(
            (p: any) => p.player === playerName && p.market === propType
          );
          if (existing) {
            if (o.name === 'Over') {
              existing.over = { price: o.price, edge: generateMockEdge(gameId + playerName, 130) };
            } else if (o.name === 'Under') {
              existing.under = { price: o.price, edge: generateMockEdge(gameId + playerName, 131) };
            } else {
              existing.yes = { price: o.price, edge: generateMockEdge(gameId + playerName, 132) };
            }
          } else {
            const prop: any = { player: playerName, market: propType, line: o.point };
            if (o.name === 'Over') {
              prop.over = { price: o.price, edge: generateMockEdge(gameId + playerName, 130) };
            } else if (o.name === 'Under') {
              prop.under = { price: o.price, edge: generateMockEdge(gameId + playerName, 131) };
            } else {
              prop.yes = { price: o.price, edge: generateMockEdge(gameId + playerName, 132) };
            }
            marketGroups.playerProps.push(prop);
          }
        }
      }
    }

    return { marketGroups };
  }

  const bookmakers: Record<string, any> = {};
  const availableBooks: string[] = [];

  for (const bm of rawOdds.bookmakers) {
    bookmakers[bm.key] = processBookmakerOdds(bm);
    availableBooks.push(bm.key);
  }

  const hasFirstHalf = availableBooks.some(b => bookmakers[b]?.marketGroups?.firstHalf?.h2h || bookmakers[b]?.marketGroups?.firstHalf?.spreads);
  const hasSecondHalf = availableBooks.some(b => bookmakers[b]?.marketGroups?.secondHalf?.h2h || bookmakers[b]?.marketGroups?.secondHalf?.spreads);
  const hasQ1 = availableBooks.some(b => bookmakers[b]?.marketGroups?.q1?.h2h || bookmakers[b]?.marketGroups?.q1?.spreads);
  const hasQ2 = availableBooks.some(b => bookmakers[b]?.marketGroups?.q2?.h2h || bookmakers[b]?.marketGroups?.q2?.spreads);
  const hasQ3 = availableBooks.some(b => bookmakers[b]?.marketGroups?.q3?.h2h || bookmakers[b]?.marketGroups?.q3?.spreads);
  const hasQ4 = availableBooks.some(b => bookmakers[b]?.marketGroups?.q4?.h2h || bookmakers[b]?.marketGroups?.q4?.spreads);
  const hasP1 = availableBooks.some(b => bookmakers[b]?.marketGroups?.p1?.h2h || bookmakers[b]?.marketGroups?.p1?.spreads);
  const hasP2 = availableBooks.some(b => bookmakers[b]?.marketGroups?.p2?.h2h || bookmakers[b]?.marketGroups?.p2?.spreads);
  const hasP3 = availableBooks.some(b => bookmakers[b]?.marketGroups?.p3?.h2h || bookmakers[b]?.marketGroups?.p3?.spreads);
  const hasProps = availableBooks.some(b => bookmakers[b]?.marketGroups?.playerProps?.length > 0);
  const hasAlts = availableBooks.some(b => bookmakers[b]?.marketGroups?.alternates?.spreads?.length > 0 || bookmakers[b]?.marketGroups?.alternates?.totals?.length > 0);
  const hasTeamTotals = availableBooks.some(b => bookmakers[b]?.marketGroups?.teamTotals?.home || bookmakers[b]?.marketGroups?.teamTotals?.away);

  const sportConfig = SUPPORTED_SPORTS.find(s => s.key === sportKey);
  const isNHL = sportKey.includes('icehockey');

  return (
    <div className="py-6">
      <div className="mb-6">
        <Link 
          href={`/edge/portal/sports/${sportKey}`}
          className="inline-flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to {sportConfig?.name || 'games'}
        </Link>
        
        <div className="flex items-center gap-4">
          <div className="text-3xl">{sportConfig?.icon || '🏆'}</div>
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">{awayTeam} @ {homeTeam}</h1>
            <p className="text-zinc-400">
              {new Date(gameInfo.commence_time).toLocaleString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>
      </div>

      <GameDetailClient
        gameData={{ id: gameId, homeTeam, awayTeam, sportKey }}
        bookmakers={bookmakers}
        availableBooks={availableBooks}
        availableTabs={{
          fullGame: true,
          firstHalf: hasFirstHalf,
          secondHalf: hasSecondHalf,
          q1: hasQ1,
          q2: hasQ2,
          q3: hasQ3,
          q4: hasQ4,
          p1: hasP1,
          p2: hasP2,
          p3: hasP3,
          props: hasProps,
          alternates: hasAlts,
          teamTotals: hasTeamTotals,
        }}
      />
    </div>
  );
}