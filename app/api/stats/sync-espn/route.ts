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
    const data = await response.json();

    // Debug: Log team detail structure including record.items
    const team = data.team;
    if (team) {
      const recordItems = team.record?.items || [];
      console.log(`[ESPN DEBUG] Team detail for ${team.displayName}:`, {
        hasRecord: !!team.record,
        recordItems: recordItems.map((item: any) => ({
          type: item.type,
          summary: item.summary,
          stats: item.stats?.slice(0, 5).map((s: any) => ({ name: s.name, value: s.value }))
        })),
        standingSummary: team.standingSummary,
      });
    }

    return data;
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

    // Debug: Log standings structure
    console.log(`[ESPN DEBUG] Standings response keys:`, Object.keys(data));

    // Parse standings - structure varies by sport
    const children = data.children || [];
    console.log(`[ESPN DEBUG] Found ${children.length} groups in standings`);

    for (const group of children) {
      const standings = group.standings?.entries || [];
      for (const entry of standings) {
        const teamId = entry.team?.id;
        const teamName = entry.team?.displayName;
        if (teamId) {
          // Extract stats from the entry
          const stats: Record<string, any> = {};
          for (const stat of entry.stats || []) {
            const statName = stat.name?.toLowerCase() || stat.type?.toLowerCase() || stat.abbreviation?.toLowerCase();
            if (statName) {
              stats[statName] = stat.value ?? stat.displayValue;
            }
          }

          // Get streak from multiple possible locations
          let streakValue = entry.streak?.value ||
                           entry.streak?.displayValue ||
                           stats.streak ||
                           stats.strk ||
                           null;

          // Also check for streak in the stats array with different key names
          for (const stat of entry.stats || []) {
            const statName = (stat.name || stat.type || stat.abbreviation || '').toLowerCase();
            if (statName === 'streak' || statName === 'strk' || statName === 'l10') {
              if (streakValue === null) {
                streakValue = stat.displayValue || stat.value || null;
              }
            }
          }

          // Debug first team
          if (standingsMap.size === 0) {
            console.log(`[ESPN DEBUG] First standings entry for ${teamName}:`, {
              entryKeys: Object.keys(entry),
              streakObj: entry.streak,
              allStats: (entry.stats || []).map((s: any) => ({ name: s.name, type: s.type, abbr: s.abbreviation, value: s.displayValue || s.value })),
              streakValue
            });
          }

          standingsMap.set(teamId, {
            ...stats,
            streak: streakValue,
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
    console.log(`[ESPN DEBUG] Fetching stats: ${url}`);
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      next: { revalidate: 0 }
    });

    if (!response.ok) {
      console.log(`[ESPN DEBUG] Stats endpoint returned ${response.status}`);
      return {};
    }

    const data = await response.json();
    const stats: Record<string, number | null> = {};

    // Debug: Log the structure
    console.log(`[ESPN DEBUG] Stats response keys:`, Object.keys(data));

    // Try multiple paths to find stats
    const categories = data.results?.stats?.categories ||
                       data.stats?.categories ||
                       data.splitCategories?.[0]?.stats ||
                       data.statistics?.splits?.categories ||
                       [];

    console.log(`[ESPN DEBUG] Found ${categories.length} categories`);

    for (const category of categories) {
      const catStats = category.stats || category.statistics || [];
      for (const stat of catStats) {
        const statName = stat.name || stat.displayName || stat.abbreviation;
        if (statName && stat.value !== undefined) {
          stats[statName.toLowerCase()] = parseFloat(stat.value) || null;
        }
      }
    }

    // Also try flat stats array
    const flatStats = data.stats || data.statistics || [];
    if (Array.isArray(flatStats)) {
      for (const stat of flatStats) {
        const statName = stat.name || stat.displayName || stat.abbreviation;
        if (statName && stat.value !== undefined) {
          stats[statName.toLowerCase()] = parseFloat(stat.value) || null;
        }
      }
    }

    console.log(`[ESPN DEBUG] Extracted stats keys:`, Object.keys(stats).slice(0, 20));
    if (stats['pace']) console.log(`[ESPN DEBUG] Found pace: ${stats['pace']}`);

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

  // Helper to parse streak string (e.g., "W3" -> 3, "L2" -> -2)
  const parseStreak = (streakStr: any): number | null => {
    if (typeof streakStr === 'number') return streakStr;
    if (typeof streakStr === 'string') {
      const match = streakStr.match(/([WL])(\d+)/i);
      if (match) {
        return parseInt(match[2]) * (match[1].toUpperCase() === 'W' ? 1 : -1);
      }
    }
    return null;
  };

  // Source 1: Standings data (most reliable for records)
  if (standingsData) {
    wins = standingsData.wins ?? standingsData.w ?? null;
    losses = standingsData.losses ?? standingsData.l ?? null;

    // Parse streak from standings
    streak = parseStreak(standingsData.streak) ?? parseStreak(standingsData.strk) ?? null;

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

  // Source 4: Streak from team detail record.items (fallback if standings didn't have it)
  if (streak === null && teamDetail?.team?.record?.items) {
    const recordItems = teamDetail.team.record.items;
    for (const item of recordItems) {
      // Look for streak in stats array within each record item
      if (item.stats) {
        for (const stat of item.stats) {
          const statName = (stat.name || stat.type || '').toLowerCase();
          if (statName === 'streak' || statName === 'strk') {
            streak = parseStreak(stat.value) ?? parseStreak(stat.displayValue) ?? null;
            if (streak !== null) break;
          }
        }
      }
      if (streak !== null) break;
    }
  }

  // Source 5: Try team.streak directly
  if (streak === null && teamDetail?.team?.streak) {
    streak = parseStreak(teamDetail.team.streak);
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

  // Map ESPN stats to our schema - try multiple field names for pace
  // NBA pace is typically ~100 possessions per game
  // Since ESPN doesn't provide pace directly, we estimate from scoring
  // Higher scoring teams typically play at faster pace
  let pace = advancedStats['pace'] ||
             advancedStats['poss'] ||
             advancedStats['possessions'] ||
             advancedStats['possessionspergame'] ||
             standingsData?.pace ||
             null;

  // If no pace available, estimate from avgpoints
  // NBA average is ~115 PPG, normalize to pace scale (centered at 100)
  if (pace === null) {
    const avgPts = advancedStats['avgpoints'] || advancedStats['pointspergame'] || advancedStats['pts'] || null;
    if (avgPts !== null && typeof avgPts === 'number') {
      // Convert points to estimated pace: ~115 PPG = 100 pace
      // Every 5 points above/below average = ~2-3 pace difference
      const leagueAvgPts = league === 'NBA' ? 115 : league === 'NFL' ? 23 : 100;
      pace = 100 + ((avgPts - leagueAvgPts) * 0.5);
      pace = Math.round(pace * 10) / 10; // Round to 1 decimal
    }
  }
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

  // Debug log for first few teams
  console.log(`[ESPN DEBUG] Extracted for ${team.displayName}: pace=${pace}, streak=${streak}, wins=${wins}, losses=${losses}`);

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
