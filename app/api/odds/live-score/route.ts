import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

// ESPN API endpoints (free, no auth)
const ESPN_ENDPOINTS: Record<string, string> = {
  'americanfootball_nfl': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
  'americanfootball_ncaaf': 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
  'basketball_nba': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
  'basketball_ncaab': 'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
  'icehockey_nhl': 'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard',
  'soccer_epl': 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard',
};

function normalizeTeam(name: string): string {
  return name.toLowerCase().replace(/\s+/g, ' ').trim();
}

function teamsMatch(a: string, b: string): boolean {
  const na = normalizeTeam(a);
  const nb = normalizeTeam(b);
  if (na === nb) return true;
  if (na.includes(nb) || nb.includes(na)) return true;
  const la = na.split(' ').pop()!;
  const lb = nb.split(' ').pop()!;
  if (la && lb && la.length > 3 && la === lb) return true;
  return false;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sport = searchParams.get('sport');
  const homeTeam = searchParams.get('home');
  const awayTeam = searchParams.get('away');

  if (!sport || !homeTeam || !awayTeam) {
    return NextResponse.json({ error: 'sport, home, away params required' }, { status: 400 });
  }

  const url = ESPN_ENDPOINTS[sport];
  if (!url) {
    return NextResponse.json({ liveData: null, gameState: 'pregame' });
  }

  try {
    const fetchUrl = sport.includes('ncaa') ? `${url}?groups=50&limit=300` : url;
    const res = await fetch(fetchUrl, { cache: 'no-store' });
    if (!res.ok) {
      return NextResponse.json({ liveData: null, gameState: 'pregame' });
    }

    const data = await res.json();
    for (const event of data.events || []) {
      const comp = event.competitions?.[0];
      if (!comp?.competitors || comp.competitors.length !== 2) continue;

      let hTeam = '', aTeam = '', hScore = 0, aScore = 0;
      let hAbbrev = '', aAbbrev = '', hLogo = '', aLogo = '';
      for (const c of comp.competitors) {
        if (c.homeAway === 'home') {
          hTeam = c.team?.displayName || '';
          hScore = parseInt(c.score || '0') || 0;
          hAbbrev = c.team?.abbreviation || '';
          hLogo = c.team?.logo || '';
        } else {
          aTeam = c.team?.displayName || '';
          aScore = parseInt(c.score || '0') || 0;
          aAbbrev = c.team?.abbreviation || '';
          aLogo = c.team?.logo || '';
        }
      }

      // Match teams (handle flipped home/away)
      const directMatch = teamsMatch(hTeam, homeTeam) && teamsMatch(aTeam, awayTeam);
      const flippedMatch = teamsMatch(hTeam, awayTeam) && teamsMatch(aTeam, homeTeam);
      if (!directMatch && !flippedMatch) continue;

      const status = comp.status || {};
      const statusType = status.type?.name || '';
      const statusDetail = status.type?.shortDetail || status.type?.detail || '';
      const displayClock = status.displayClock || '';
      const period = status.period || 0;

      let gameState: 'pregame' | 'live' | 'final' = 'pregame';
      if (statusType === 'STATUS_FINAL') gameState = 'final';
      else if (statusType === 'STATUS_IN_PROGRESS') gameState = 'live';
      else if (statusType === 'STATUS_HALFTIME') gameState = 'live';

      // If flipped, swap scores
      const finalHomeScore = flippedMatch ? aScore : hScore;
      const finalAwayScore = flippedMatch ? hScore : aScore;
      const finalHomeAbbrev = flippedMatch ? aAbbrev : hAbbrev;
      const finalAwayAbbrev = flippedMatch ? hAbbrev : aAbbrev;
      const finalHomeLogo = flippedMatch ? aLogo : hLogo;
      const finalAwayLogo = flippedMatch ? hLogo : aLogo;

      return NextResponse.json({
        gameState,
        liveData: {
          homeScore: finalHomeScore,
          awayScore: finalAwayScore,
          statusDetail,
          period,
          clock: displayClock,
          homeAbbrev: finalHomeAbbrev,
          awayAbbrev: finalAwayAbbrev,
          homeLogo: finalHomeLogo,
          awayLogo: finalAwayLogo,
        },
      });
    }

    // No match found
    return NextResponse.json({ liveData: null, gameState: 'pregame' });
  } catch (e) {
    console.error('[LiveScore] ESPN fetch error:', e);
    return NextResponse.json({ liveData: null, gameState: 'pregame' });
  }
}
