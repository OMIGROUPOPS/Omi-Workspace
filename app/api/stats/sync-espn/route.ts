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
  { sport: 'basketball', league: 'nba', dbLeague: 'NBA', sportKey: 'basketball_nba', limit: 50, skipDetail: false },
  { sport: 'football', league: 'nfl', dbLeague: 'NFL', sportKey: 'americanfootball_nfl', limit: 50, skipDetail: false },
  { sport: 'baseball', league: 'mlb', dbLeague: 'MLB', sportKey: 'baseball_mlb', limit: 50, skipDetail: false },
  { sport: 'hockey', league: 'nhl', dbLeague: 'NHL', sportKey: 'icehockey_nhl', limit: 50, skipDetail: false },
  { sport: 'basketball', league: 'mens-college-basketball', dbLeague: 'NCAAB', sportKey: 'basketball_ncaab', limit: 200, skipDetail: true },
  { sport: 'football', league: 'college-football', dbLeague: 'NCAAF', sportKey: 'americanfootball_ncaaf', limit: 200, skipDetail: true },
  // EPL synced separately via Football-Data.org (ESPN returns empty stats for soccer)
];

async function fetchESPNTeams(sport: string, league: string, limit: number = 50): Promise<ESPNTeam[]> {
  try {
    const url = `${ESPN_BASE}/${sport}/${league}/teams?limit=${limit}`;
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
// NOTE: The /apis/site/v2/ standings endpoint returns empty data (just fullViewLink).
// The /apis/v2/ endpoint returns actual standings with stats.
const ESPN_STANDINGS_BASE = 'https://site.api.espn.com/apis/v2/sports';

async function fetchStandings(sport: string, league: string): Promise<Map<string, any>> {
  const standingsMap = new Map();
  try {
    const url = `${ESPN_STANDINGS_BASE}/${sport}/${league}/standings`;
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
        // Capture perGameValue (NHL goals/game, shots/game, etc.)
        if (statName && stat.perGameValue !== undefined && stat.perGameValue !== null) {
          const pgVal = parseFloat(String(stat.perGameValue));
          if (!isNaN(pgVal)) {
            stats[statName.toLowerCase() + '_pergame'] = pgVal;
          }
        }
      }
    }

    // Parse opponent stats (NFL/NCAAF: data.results.opponent array)
    const oppCategories = data.results?.opponent || [];
    if (Array.isArray(oppCategories)) {
      for (const category of oppCategories) {
        const catStats = category.stats || category.statistics || [];
        for (const stat of catStats) {
          const statName = stat.name || stat.displayName || stat.abbreviation;
          if (statName && stat.value !== undefined) {
            stats['opp_' + statName.toLowerCase()] = parseFloat(stat.value) || null;
          }
          if (statName && stat.perGameValue !== undefined && stat.perGameValue !== null) {
            const pgVal = parseFloat(String(stat.perGameValue));
            if (!isNaN(pgVal)) {
              stats['opp_' + statName.toLowerCase() + '_pergame'] = pgVal;
            }
          }
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

    const allKeys = Object.keys(stats);
    console.log(`[ESPN SYNC] Stats for team ${teamId}: ${allKeys.length} keys, sample: ${allKeys.slice(0, 15).join(', ')}`);

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
  dbLeague: string,
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

  // If no pace available, estimate from avgpoints (basketball only)
  if (pace === null && sport === 'basketball') {
    const avgPts = advancedStats['avgpoints'] || advancedStats['pointspergame'] || null;
    if (avgPts !== null && typeof avgPts === 'number') {
      // NBA/NCAAB average is ~115/75 PPG, normalize to pace scale (centered at 100)
      const leagueAvgPts = dbLeague === 'NCAAB' ? 75 : 115;
      pace = 100 + ((avgPts - leagueAvgPts) * 0.5);
      pace = Math.round(pace * 10) / 10;
    }
  }

  const offRtg = advancedStats['offensiverating'] || advancedStats['ortg'] || standingsData?.offensiverating || null;
  const defRtg = advancedStats['defensiverating'] || advancedStats['drtg'] || standingsData?.defensiverating || null;

  // Sport-specific PPG and opponent PPG mapping
  const gamesPlayed = wins !== null && losses !== null ? wins + losses : null;
  let calcPpg: number | null = null;
  let calcOppPpg: number | null = null;

  if (sport === 'football') {
    // NFL/NCAAF: ESPN uses "totalPointsPerGame" in scoring category
    calcPpg = advancedStats['totalpointspergame'] ?? null;
    // Opponent PPG from opponent stats section
    calcOppPpg = advancedStats['opp_totalpointspergame'] ?? null;
  } else if (sport === 'hockey') {
    // NHL: goals per game from perGameValue capture
    calcPpg = advancedStats['goals_pergame'] ?? null;
    // Goals against: avgGoalsAgainst is a direct per-game stat, or use perGameValue
    calcOppPpg = advancedStats['avggoalsagainst'] ?? advancedStats['goalsagainst_pergame'] ?? null;
  } else {
    // NBA/NCAAB/default: avgPoints for PPG
    calcPpg = advancedStats['avgpoints'] ?? advancedStats['pointspergame'] ?? null;
    calcOppPpg = advancedStats['opponentpointspergame'] ?? advancedStats['opppts'] ?? null;
    // Standings-based avg (NBA v2 standings provide avgPointsFor/avgPointsAgainst directly)
    if (calcPpg === null && standingsData?.avgpointsfor) {
      calcPpg = parseFloat(standingsData.avgpointsfor);
    }
    if (calcOppPpg === null && standingsData?.avgpointsagainst) {
      calcOppPpg = parseFloat(standingsData.avgpointsagainst);
    }
  }

  // Standings-based fallbacks (all sports)
  if (calcPpg === null) {
    const ptsFor = standingsData?.pointsfor ?? standingsData?.pf ?? null;
    if (ptsFor && gamesPlayed && gamesPlayed > 0) {
      calcPpg = ptsFor / gamesPlayed;
    }
  }
  if (calcOppPpg === null) {
    const ptsAgainst = standingsData?.pointsagainst ?? standingsData?.pa ?? null;
    if (ptsAgainst && gamesPlayed && gamesPlayed > 0) {
      calcOppPpg = ptsAgainst / gamesPlayed;
    }
  }

  console.log(`[ESPN SYNC] ${dbLeague} ${team.displayName}: ppg=${calcPpg?.toFixed(1) ?? 'NULL'}, papg=${calcOppPpg?.toFixed(1) ?? 'NULL'}, pace=${pace ?? 'NULL'}, wins=${wins}, losses=${losses}`);

  return {
    team_id: team.id,
    team_name: team.displayName,
    team_abbrev: team.abbreviation,
    sport: dbLeague,
    league: dbLeague,
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

// === FOOTBALL-DATA.ORG EPL SYNC ===
// ESPN returns empty stats for soccer, so EPL uses Football-Data.org instead
const FOOTBALL_DATA_BASE = 'https://api.football-data.org/v4';

async function syncFootballDataEPL(): Promise<{ synced: number; errors: number; withStats: number }> {
  const apiKey = process.env.FOOTBALL_DATA_API_KEY;

  if (!apiKey) {
    console.log('EPL_SYNC: FOOTBALL_DATA_API_KEY not set, skipping');
    return { synced: 0, errors: 0, withStats: 0 };
  }

  const headers: Record<string, string> = { 'X-Auth-Token': apiKey };
  let synced = 0;
  let errors = 0;
  let withStats = 0;

  try {
    // Single call gets all standings including home/away splits
    const res = await fetch(`${FOOTBALL_DATA_BASE}/competitions/PL/standings`, { headers });
    if (!res.ok) {
      console.error(`EPL_SYNC: Football-Data.org returned ${res.status}`);
      return { synced: 0, errors: 1, withStats: 0 };
    }

    const data = await res.json();
    const totalTable = data.standings?.find((s: any) => s.type === 'TOTAL')?.table;
    const homeTable = data.standings?.find((s: any) => s.type === 'HOME')?.table;
    const awayTable = data.standings?.find((s: any) => s.type === 'AWAY')?.table;

    if (!totalTable || totalTable.length === 0) {
      console.error('EPL_SYNC: No standings table in response');
      return { synced: 0, errors: 1, withStats: 0 };
    }

    const season = new Date().getFullYear().toString();

    for (const entry of totalTable) {
      try {
        const team = entry.team;
        const gp = entry.playedGames || 0;
        const goalsForPG = gp > 0 ? entry.goalsFor / gp : null;
        const goalsAgainstPG = gp > 0 ? entry.goalsAgainst / gp : null;

        // Home/away records
        const homeEntry = homeTable?.find((h: any) => h.team.id === team.id);
        const awayEntry = awayTable?.find((a: any) => a.team.id === team.id);

        // Parse streak from form string (e.g., "W,D,L,W,W")
        let streak: number | null = null;
        if (entry.form) {
          const results = entry.form.split(',');
          let count = 0;
          const last = results[results.length - 1];
          for (let i = results.length - 1; i >= 0; i--) {
            if (results[i] === last) count++;
            else break;
          }
          streak = last === 'W' ? count : last === 'L' ? -count : 0;
        }

        const teamStats: TeamStatsRow = {
          team_id: `fd_${team.id}`,
          team_name: team.name,
          team_abbrev: team.shortName || team.tla || '',
          sport: 'EPL',
          league: 'EPL',
          season,
          pace: null,
          offensive_rating: null,
          defensive_rating: null,
          net_rating: null,
          wins: entry.won,
          losses: entry.lost,
          win_pct: gp > 0 ? entry.won / gp : null,
          home_wins: homeEntry?.won ?? null,
          home_losses: homeEntry?.lost ?? null,
          away_wins: awayEntry?.won ?? null,
          away_losses: awayEntry?.lost ?? null,
          streak,
          points_per_game: goalsForPG,
          points_allowed_per_game: goalsAgainstPG,
          point_differential: goalsForPG !== null && goalsAgainstPG !== null ? goalsForPG - goalsAgainstPG : null,
          true_shooting_pct: null,
          assist_ratio: null,
          rebound_pct: null,
          turnover_ratio: null,
          injuries: [],
          source: 'football-data.org',
          updated_at: new Date().toISOString()
        };

        const { error } = await supabase
          .from('team_stats')
          .upsert(teamStats, { onConflict: 'team_id,sport,season' });

        if (error) {
          console.error(`EPL_SYNC: Error upserting ${team.name}:`, error.message);
          errors++;
        } else {
          synced++;
          if (entry.won !== null || goalsForPG !== null) withStats++;
        }

        console.log(`[EPL SYNC] ${team.name} (${team.tla}): pos=${entry.position}, W${entry.won}-D${entry.draw}-L${entry.lost}, GF/g=${goalsForPG?.toFixed(2)}, GA/g=${goalsAgainstPG?.toFixed(2)}, form=${entry.form}`);
      } catch (err) {
        console.error('EPL_SYNC: Error processing team:', err);
        errors++;
      }
    }

    console.log(`EPL_SYNC: Football-Data.org — synced ${synced} teams (${withStats} with stats), ${errors} errors`);
  } catch (err) {
    console.error('EPL_SYNC: Football-Data.org fetch failed:', err);
    errors++;
  }

  return { synced, errors, withStats };
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sportFilter = searchParams.get('sport');
  const detailed = searchParams.get('detailed') !== 'false'; // Default to true for detailed fetching

  console.log(`Starting ESPN team stats sync... (detailed=${detailed})`);

  const results: { sport: string; league: string; synced: number; errors: number; withStats: number }[] = [];

  for (const config of SPORT_CONFIGS) {
    // Apply sport filter if provided
    if (sportFilter && config.sportKey !== sportFilter && config.league !== sportFilter && config.dbLeague.toLowerCase() !== sportFilter.toLowerCase()) {
      continue;
    }

    // Fetch standings first (contains win/loss records for all teams)
    const standingsMap = await fetchStandings(config.sport, config.league);

    const teams = await fetchESPNTeams(config.sport, config.league, config.limit);
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
          // Fetch team detail (injuries, record) — skip for college to save API calls
          if (!config.skipDetail) {
            teamDetail = await fetchTeamDetail(config.sport, config.league, team.id);
          }

          // Fetch advanced stats
          advancedStats = await fetchTeamStats(config.sport, config.league, team.id);

          // Small delay between API calls
          await new Promise(resolve => setTimeout(resolve, config.skipDetail ? 30 : 50));
        }

        const teamStats = extractTeamStats(
          team,
          config.sport,
          config.league,
          config.dbLeague,
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

    console.log(`ESPN_SYNC: ${config.dbLeague} — synced ${synced} teams (${withStats} with stats), ${errors} errors`);
  }

  // === EPL via Football-Data.org ===
  if (!sportFilter || sportFilter === 'soccer_epl' || sportFilter.toLowerCase() === 'epl') {
    const eplResult = await syncFootballDataEPL();
    results.push({
      sport: 'soccer',
      league: 'EPL',
      synced: eplResult.synced,
      errors: eplResult.errors,
      withStats: eplResult.withStats
    });
  }

  // Clean up legacy rows that used generic sport names (e.g., 'basketball' instead of 'NBA')
  // New rows use dbLeague as sport value to avoid team_id collisions between leagues
  const legacySports = ['basketball', 'football', 'hockey', 'baseball', 'soccer'];
  const { data: deletedLegacy, error: cleanupError } = await supabase
    .from('team_stats')
    .delete()
    .in('sport', legacySports)
    .select('sport');

  if (cleanupError) {
    console.warn('Legacy row cleanup failed:', cleanupError.message);
  } else {
    console.log(`ESPN_SYNC: Deleted ${deletedLegacy?.length || 0} legacy rows with old sport format`);
  }

  // Clean up old ESPN EPL rows (replaced by Football-Data.org)
  const { data: deletedEplEspn, error: eplCleanupError } = await supabase
    .from('team_stats')
    .delete()
    .eq('sport', 'EPL')
    .eq('source', 'espn')
    .select('sport');

  if (eplCleanupError) {
    console.warn('ESPN EPL cleanup failed:', eplCleanupError.message);
  } else if (deletedEplEspn?.length) {
    console.log(`ESPN_SYNC: Deleted ${deletedEplEspn.length} old ESPN EPL rows`);
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
