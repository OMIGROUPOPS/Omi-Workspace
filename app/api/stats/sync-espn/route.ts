import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const ESPN_BASE = 'https://site.api.espn.com/apis/site/v2/sports';

interface ESPNTeam {
  id: string;
  displayName: string;
  abbreviation: string;
  record?: {
    items?: Array<{
      type: string;
      summary: string;
      stats?: Array<{ name: string; value: number }>;
    }>;
  };
  injuries?: Array<{
    athlete: { displayName: string };
    type: { description: string };
    status: string;
  }>;
}

interface ESPNTeamsResponse {
  sports?: Array<{
    leagues?: Array<{
      teams?: Array<{ team: ESPNTeam }>;
    }>;
  }>;
}

interface TeamStatsRow {
  team_id: string;
  team_name: string;
  team_abbrev: string;
  sport: string;
  league: string;
  season: string;
  pace: number | null;
  offensive_rating: number | null;
  defensive_rating: number | null;
  net_rating: number | null;
  wins: number | null;
  losses: number | null;
  win_pct: number | null;
  home_wins: number | null;
  home_losses: number | null;
  away_wins: number | null;
  away_losses: number | null;
  streak: number | null;
  points_per_game: number | null;
  points_allowed_per_game: number | null;
  point_differential: number | null;
  true_shooting_pct: number | null;
  assist_ratio: number | null;
  rebound_pct: number | null;
  turnover_ratio: number | null;
  injuries: unknown[];
  source: string;
  updated_at: string;
}

const SPORT_CONFIGS = [
  { sport: 'basketball', league: 'nba', sportKey: 'basketball_nba' },
  { sport: 'football', league: 'nfl', sportKey: 'americanfootball_nfl' },
  { sport: 'baseball', league: 'mlb', sportKey: 'baseball_mlb' },
  { sport: 'hockey', league: 'nhl', sportKey: 'icehockey_nhl' },
];

async function fetchESPNTeams(sport: string, league: string): Promise<ESPNTeam[]> {
  try {
    const url = `${ESPN_BASE}/${sport}/${league}/teams?limit=50`;
    console.log(`Fetching: ${url}`);

    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) {
      console.error(`ESPN API error for ${sport}/${league}: ${response.status}`);
      return [];
    }

    const data: ESPNTeamsResponse = await response.json();
    const teams = data.sports?.[0]?.leagues?.[0]?.teams?.map(t => t.team) || [];
    console.log(`Found ${teams.length} teams for ${sport}/${league}`);
    return teams;
  } catch (error) {
    console.error(`Error fetching ${sport}/${league}:`, error);
    return [];
  }
}

// Fetch detailed team info including record from team detail endpoint
async function fetchTeamDetail(sport: string, league: string, teamId: string): Promise<any> {
  try {
    const url = `${ESPN_BASE}/${sport}/${league}/teams/${teamId}`;
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error fetching team detail ${teamId}:`, error);
    return null;
  }
}

// Fetch standings for a league to get win/loss records
async function fetchStandings(sport: string, league: string): Promise<Map<string, any>> {
  const standingsMap = new Map();
  try {
    const url = `${ESPN_BASE}/${sport}/${league}/standings`;
    console.log(`Fetching standings: ${url}`);

    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) return standingsMap;

    const data = await response.json();

    // Parse standings - structure varies by sport
    const children = data.children || [];
    for (const group of children) {
      const standings = group.standings?.entries || [];
      for (const entry of standings) {
        const teamId = entry.team?.id;
        if (teamId) {
          // Extract stats from the entry
          const stats: Record<string, any> = {};
          for (const stat of entry.stats || []) {
            stats[stat.name?.toLowerCase() || stat.type?.toLowerCase()] = stat.value;
          }
          standingsMap.set(teamId, {
            ...stats,
            streak: entry.streak?.value || null,
          });
        }
      }
    }

    console.log(`Found standings for ${standingsMap.size} teams in ${league}`);
  } catch (error) {
    console.error(`Error fetching standings for ${league}:`, error);
  }
  return standingsMap;
}

async function fetchTeamStats(sport: string, league: string, teamId: string): Promise<Record<string, number | null>> {
  try {
    const url = `${ESPN_BASE}/${sport}/${league}/teams/${teamId}/statistics`;
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) return {};

    const data = await response.json();
    const stats: Record<string, number | null> = {};

    // Parse statistics from ESPN response
    const categories = data.results?.stats?.categories || data.stats?.categories || [];
    for (const category of categories) {
      for (const stat of category.stats || []) {
        if (stat.name && stat.value !== undefined) {
          stats[stat.name.toLowerCase()] = parseFloat(stat.value) || null;
        }
      }
    }

    return stats;
  } catch (error) {
    console.error(`Error fetching stats for team ${teamId}:`, error);
    return {};
  }
}

function parseRecord(summary: string): { wins: number; losses: number } | null {
  // Parse "10-5" or "10-5-2" format
  const match = summary.match(/(\d+)-(\d+)/);
  if (match) {
    return { wins: parseInt(match[1]), losses: parseInt(match[2]) };
  }
  return null;
}

function extractTeamStats(
  team: ESPNTeam,
  sport: string,
  league: string,
  advancedStats: Record<string, number | null>,
  standingsData?: Record<string, any>,
  teamDetail?: any
): TeamStatsRow {
  const season = new Date().getFullYear().toString();

  // Parse record from ESPN data - try multiple sources
  let wins: number | null = null;
  let losses: number | null = null;
  let homeWins: number | null = null;
  let homeLosses: number | null = null;
  let awayWins: number | null = null;
  let awayLosses: number | null = null;
  let streak: number | null = null;

  // Source 1: Standings data (most reliable for records)
  if (standingsData) {
    wins = standingsData.wins ?? standingsData.w ?? null;
    losses = standingsData.losses ?? standingsData.l ?? null;

    // Parse streak (e.g., "W3" -> 3, "L2" -> -2)
    const streakStr = standingsData.streak;
    if (typeof streakStr === 'string') {
      const match = streakStr.match(/([WL])(\d+)/i);
      if (match) {
        streak = parseInt(match[2]) * (match[1].toUpperCase() === 'W' ? 1 : -1);
      }
    } else if (typeof streakStr === 'number') {
      streak = streakStr;
    }

    // Home/away from standings
    if (standingsData.home) {
      const homeParsed = parseRecord(standingsData.home);
      if (homeParsed) {
        homeWins = homeParsed.wins;
        homeLosses = homeParsed.losses;
      }
    }
    if (standingsData.road || standingsData.away) {
      const awayParsed = parseRecord(standingsData.road || standingsData.away);
      if (awayParsed) {
        awayWins = awayParsed.wins;
        awayLosses = awayParsed.losses;
      }
    }
  }

  // Source 2: Team record items (fallback)
  if (wins === null) {
    const records = team.record?.items || teamDetail?.team?.record?.items || [];
    for (const record of records) {
      const parsed = parseRecord(record.summary);
      if (!parsed) continue;

      if (record.type === 'total') {
        wins = parsed.wins;
        losses = parsed.losses;
      } else if (record.type === 'home') {
        homeWins = parsed.wins;
        homeLosses = parsed.losses;
      } else if (record.type === 'road' || record.type === 'away') {
        awayWins = parsed.wins;
        awayLosses = parsed.losses;
      }
    }
  }

  // Source 3: Team detail record string
  if (wins === null && teamDetail?.team?.record) {
    const recordStr = teamDetail.team.record;
    if (typeof recordStr === 'string') {
      const parsed = parseRecord(recordStr);
      if (parsed) {
        wins = parsed.wins;
        losses = parsed.losses;
      }
    }
  }

  // Calculate win percentage
  const winPct = wins !== null && losses !== null && (wins + losses) > 0
    ? wins / (wins + losses)
    : null;

  // Parse injuries from team detail
  const injuries = (teamDetail?.team?.injuries || team.injuries || []).map((inj: any) => ({
    player: inj.athlete?.displayName || inj.displayName || 'Unknown',
    type: inj.type?.description || inj.description || 'Unknown',
    status: inj.status || 'Unknown'
  }));

  // Map ESPN stats to our schema - try multiple field names
  const pace = advancedStats['pace'] || advancedStats['possessions'] || standingsData?.pace || null;
  const offRtg = advancedStats['offensiverating'] || advancedStats['ortg'] || standingsData?.offensiverating || null;
  const defRtg = advancedStats['defensiverating'] || advancedStats['drtg'] || standingsData?.defensiverating || null;
  const ppg = advancedStats['pointspergame'] || advancedStats['avgpoints'] || advancedStats['pts'] ||
              standingsData?.pointsfor || standingsData?.avgpointsfor || null;
  const oppPpg = advancedStats['opponentpointspergame'] || advancedStats['opppts'] ||
                 standingsData?.pointsagainst || standingsData?.avgpointsagainst || null;

  // Calculate PPG from standings total points if needed
  let calcPpg = ppg;
  let calcOppPpg = oppPpg;
  const gamesPlayed = wins !== null && losses !== null ? wins + losses : null;

  if (calcPpg === null && standingsData?.pointsfor && gamesPlayed && gamesPlayed > 0) {
    calcPpg = standingsData.pointsfor / gamesPlayed;
  }
  if (calcOppPpg === null && standingsData?.pointsagainst && gamesPlayed && gamesPlayed > 0) {
    calcOppPpg = standingsData.pointsagainst / gamesPlayed;
  }

  return {
    team_id: team.id,
    team_name: team.displayName,
    team_abbrev: team.abbreviation,
    sport: sport,
    league: league.toUpperCase(),
    season: season,
    pace: pace,
    offensive_rating: offRtg,
    defensive_rating: defRtg,
    net_rating: offRtg !== null && defRtg !== null ? offRtg - defRtg : null,
    wins,
    losses,
    win_pct: winPct,
    home_wins: homeWins,
    home_losses: homeLosses,
    away_wins: awayWins,
    away_losses: awayLosses,
    streak,
    points_per_game: calcPpg,
    points_allowed_per_game: calcOppPpg,
    point_differential: calcPpg !== null && calcOppPpg !== null ? calcPpg - calcOppPpg : null,
    true_shooting_pct: advancedStats['trueshootingpercentage'] || advancedStats['ts%'] || null,
    assist_ratio: advancedStats['assistratio'] || advancedStats['astratio'] || null,
    rebound_pct: advancedStats['reboundpercentage'] || advancedStats['reb%'] || null,
    turnover_ratio: advancedStats['turnoverratio'] || advancedStats['toratio'] || null,
    injuries: injuries,
    source: 'espn',
    updated_at: new Date().toISOString()
  };
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sportFilter = searchParams.get('sport');
  const detailed = searchParams.get('detailed') !== 'false'; // Default to true for detailed fetching

  console.log(`Starting ESPN team stats sync... (detailed=${detailed})`);

  const results: { sport: string; league: string; synced: number; errors: number; withStats: number }[] = [];

  for (const config of SPORT_CONFIGS) {
    // Apply sport filter if provided
    if (sportFilter && config.sportKey !== sportFilter && config.league !== sportFilter) {
      continue;
    }

    // Fetch standings first (contains win/loss records for all teams)
    const standingsMap = await fetchStandings(config.sport, config.league);

    const teams = await fetchESPNTeams(config.sport, config.league);
    let synced = 0;
    let errors = 0;
    let withStats = 0;

    for (const team of teams) {
      try {
        // Get standings data for this team
        const standingsData = standingsMap.get(team.id);

        // Fetch detailed team info and advanced stats if detailed mode
        let advancedStats: Record<string, number | null> = {};
        let teamDetail: any = null;

        if (detailed) {
          // Fetch team detail (includes injuries, record)
          teamDetail = await fetchTeamDetail(config.sport, config.league, team.id);

          // Fetch advanced stats
          advancedStats = await fetchTeamStats(config.sport, config.league, team.id);

          // Small delay between API calls
          await new Promise(resolve => setTimeout(resolve, 50));
        }

        const teamStats = extractTeamStats(
          team,
          config.sport,
          config.league,
          advancedStats,
          standingsData,
          teamDetail
        );

        // Track if we got actual stats
        if (teamStats.wins !== null || teamStats.points_per_game !== null) {
          withStats++;
        }

        // Upsert to Supabase
        const { error } = await supabase
          .from('team_stats')
          .upsert(teamStats, {
            onConflict: 'team_id,sport,season'
          });

        if (error) {
          console.error(`Error upserting ${team.displayName}:`, error.message);
          errors++;
        } else {
          synced++;
        }

        // Small delay to be nice to ESPN API
        await new Promise(resolve => setTimeout(resolve, 50));
      } catch (error) {
        console.error(`Error processing ${team.displayName}:`, error);
        errors++;
      }
    }

    results.push({
      sport: config.sport,
      league: config.league,
      synced,
      errors,
      withStats
    });

    console.log(`${config.league}: Synced ${synced} teams (${withStats} with stats), ${errors} errors`);
  }

  return NextResponse.json({
    success: true,
    timestamp: new Date().toISOString(),
    detailed,
    results
  });
}

export const dynamic = 'force-dynamic';
export const maxDuration = 300; // 5 minutes for detailed sync
