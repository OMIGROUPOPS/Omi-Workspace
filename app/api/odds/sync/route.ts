import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { EdgeDetector } from "@/lib/edge/engine/edge-detector";
import { EdgeLifecycleManager, upsertEdge } from "@/lib/edge/engine/edge-lifecycle";
import { calculateGameCEQ, type GameCEQ, type TeamStatsData, type GameContextData } from "@/lib/edge/engine/edgescout";

const CRON_SECRET = process.env.CRON_SECRET || "";
const ODDS_API_KEY = process.env.ODDS_API_KEY || "";
const ODDS_API_BASE = "https://api.the-odds-api.com/v4";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Line movement threshold for triggering pillar recalculation (in points)
const MOVEMENT_THRESHOLD = 0.5;

const SPORT_KEYS: Record<string, string> = {
  // ============================================================================
  // ACTIVE SPORTS (7 total) - Synced on 15-minute cron cycle
  // ============================================================================

  // American Football
  NFL: "americanfootball_nfl",
  NCAAF: "americanfootball_ncaaf",

  // Basketball
  NBA: "basketball_nba",
  NCAAB: "basketball_ncaab",

  // Ice Hockey
  NHL: "icehockey_nhl",

  // Soccer - England
  EPL: "soccer_epl",

  // Tennis - Grand Slams
  TENNIS_AO: "tennis_atp_australian_open",
  TENNIS_FO: "tennis_atp_french_open",
  TENNIS_USO: "tennis_atp_us_open",
  TENNIS_WIM: "tennis_atp_wimbledon",

  // ============================================================================
  // PAUSED SPORTS - Re-enable when in season or budget allows
  // ============================================================================

  // PAUSED: Re-enable when in season or budget allows
  // WNBA: "basketball_wnba",
  // WNCAAB: "basketball_wncaab",
  // EUROLEAGUE: "basketball_euroleague",
  // NBL: "basketball_nbl",

  // PAUSED: Re-enable when in season or budget allows
  // MLB: "baseball_mlb",

  // PAUSED: Re-enable when in season or budget allows
  // AHL: "icehockey_ahl",
  // SHL: "icehockey_sweden_hockey_league",
  // LIIGA: "icehockey_liiga",
  // MESTIS: "icehockey_mestis",

  // PAUSED: Re-enable when in season or budget allows
  // MMA: "mma_mixed_martial_arts",
  // BOXING: "boxing_boxing",

  // PAUSED: Re-enable when in season or budget allows
  // EFL_CHAMP: "soccer_efl_champ",
  // FA_CUP: "soccer_fa_cup",
  // LA_LIGA: "soccer_spain_la_liga",
  // BUNDESLIGA: "soccer_germany_bundesliga",
  // SERIE_A: "soccer_italy_serie_a",
  // LIGUE_1: "soccer_france_ligue_one",
  // EREDIVISIE: "soccer_netherlands_eredivisie",
  // UCL: "soccer_uefa_champs_league",
  // EUROPA: "soccer_uefa_europa_league",
  // MLS: "soccer_usa_mls",
  // LIGA_MX: "soccer_mexico_ligamx",

  // PAUSED: Re-enable when in season or budget allows
  // IPL: "cricket_ipl",
  // BIG_BASH: "cricket_big_bash",
  // CRICKET_TEST: "cricket_test_match",

  // PAUSED: Re-enable when in season or budget allows
  // NRL: "rugbyleague_nrl",

  // PAUSED: Re-enable when in season or budget allows
  // MASTERS: "golf_masters_tournament_winner",
  // PGA_CHAMP: "golf_pga_championship_winner",
  // US_OPEN: "golf_us_open_winner",
  // THE_OPEN: "golf_the_open_championship_winner",

  // PAUSED: Re-enable when in season or budget allows
  // AFL: "aussierules_afl",
};

// Core markets fetched via /sports/{sport}/odds (all sports)
const CORE_MARKETS = "h2h,spreads,totals";

// Per-event additional markets fetched via /sports/{sport}/events/{id}/odds
// Only active sports get enrichment to conserve API quota
const EVENT_MARKETS: Record<string, string[]> = {
  // ============================================================================
  // ACTIVE SPORTS - Full enrichment (halves, quarters, alternates, props)
  // ============================================================================

  // American Football - Full Game, 1H, 2H, 1Q, 2Q, 3Q, 4Q
  americanfootball_nfl: [
    // Halves
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    // Quarters
    "h2h_q1", "spreads_q1", "totals_q1",
    "h2h_q2", "spreads_q2", "totals_q2",
    "h2h_q3", "spreads_q3", "totals_q3",
    "h2h_q4", "spreads_q4", "totals_q4",
    // Alt lines and team totals
    "alternate_spreads", "alternate_totals", "team_totals",
    // Player props
    "player_pass_yds", "player_rush_yds", "player_reception_yds",
    "player_receptions", "player_pass_tds", "player_anytime_td",
  ],
  americanfootball_ncaaf: [
    // Halves
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    // Quarters
    "h2h_q1", "spreads_q1", "totals_q1",
    "h2h_q2", "spreads_q2", "totals_q2",
    "h2h_q3", "spreads_q3", "totals_q3",
    "h2h_q4", "spreads_q4", "totals_q4",
    // Alt lines and team totals
    "alternate_spreads", "alternate_totals", "team_totals",
  ],

  // Basketball
  basketball_nba: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "h2h_q1", "spreads_q1", "totals_q1",
    "h2h_q2", "spreads_q2", "totals_q2",
    "h2h_q3", "spreads_q3", "totals_q3",
    "h2h_q4", "spreads_q4", "totals_q4",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_rebounds", "player_assists",
    "player_threes", "player_blocks", "player_steals",
  ],
  basketball_ncaab: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals", "team_totals",
  ],

  // Ice Hockey
  icehockey_nhl: [
    "h2h_p1", "spreads_p1", "totals_p1",
    "h2h_p2", "spreads_p2", "totals_p2",
    "h2h_p3", "spreads_p3", "totals_p3",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_assists", "player_shots_on_goal",
    "player_blocked_shots",
  ],

  // Soccer - EPL only
  soccer_epl: [
    // Halves
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    // Alt lines and special markets
    "alternate_spreads", "alternate_totals", "team_totals",
    "btts", "draw_no_bet",
  ],

  // Tennis - No per-event enrichment (core markets only)

  // ============================================================================
  // PAUSED SPORTS - Re-enable when in season or budget allows
  // ============================================================================

  // PAUSED: basketball_wnba
  // basketball_wnba: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  //   "player_points", "player_rebounds", "player_assists",
  //   "player_threes",
  // ],

  // PAUSED: basketball_euroleague
  // basketball_euroleague: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: icehockey_sweden_hockey_league
  // icehockey_sweden_hockey_league: [
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: icehockey_liiga
  // icehockey_liiga: [
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: baseball_mlb
  // baseball_mlb: [
  //   "alternate_spreads", "alternate_totals", "team_totals",
  //   "pitcher_strikeouts", "batter_total_bases", "batter_hits",
  //   "batter_home_runs", "batter_rbis",
  // ],

  // PAUSED: soccer_uefa_champs_league
  // soccer_uefa_champs_league: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_spain_la_liga
  // soccer_spain_la_liga: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_germany_bundesliga
  // soccer_germany_bundesliga: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_italy_serie_a
  // soccer_italy_serie_a: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_france_ligue_one
  // soccer_france_ligue_one: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_uefa_europa_league
  // soccer_uefa_europa_league: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_usa_mls
  // soccer_usa_mls: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_mexico_ligamx
  // soccer_mexico_ligamx: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals", "team_totals",
  // ],

  // PAUSED: soccer_netherlands_eredivisie
  // soccer_netherlands_eredivisie: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: soccer_efl_champ
  // soccer_efl_champ: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: soccer_fa_cup
  // soccer_fa_cup: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: mma_mixed_martial_arts
  // mma_mixed_martial_arts: [
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: boxing_boxing
  // boxing_boxing: [
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: rugbyleague_nrl
  // rugbyleague_nrl: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],

  // PAUSED: aussierules_afl
  // aussierules_afl: [
  //   "h2h_h1", "spreads_h1", "totals_h1",
  //   "h2h_h2", "spreads_h2", "totals_h2",
  //   "alternate_spreads", "alternate_totals",
  // ],
};

// Market keys to snapshot for line movement charts (includes halves, quarters, periods, and props)
const SNAPSHOT_MARKETS = [
  // Core game markets
  "h2h", "spreads", "totals",
  // Halves
  "h2h_h1", "spreads_h1", "totals_h1",
  "h2h_h2", "spreads_h2", "totals_h2",
  // Quarters (basketball)
  "h2h_q1", "spreads_q1", "totals_q1",
  "h2h_q2", "spreads_q2", "totals_q2",
  "h2h_q3", "spreads_q3", "totals_q3",
  "h2h_q4", "spreads_q4", "totals_q4",
  // Periods (hockey)
  "h2h_p1", "spreads_p1", "totals_p1",
  "h2h_p2", "spreads_p2", "totals_p2",
  "h2h_p3", "spreads_p3", "totals_p3",
  // Alternates
  "alternate_spreads", "alternate_totals", "team_totals",
  // Player props - NBA/WNBA/NCAAB
  "player_points", "player_rebounds", "player_assists", "player_threes",
  "player_blocks", "player_steals", "player_points_rebounds_assists",
  "player_points_rebounds", "player_points_assists", "player_rebounds_assists",
  // Player props - NFL
  "player_pass_yds", "player_pass_tds", "player_pass_completions",
  "player_pass_attempts", "player_pass_interceptions", "player_rush_yds",
  "player_rush_attempts", "player_reception_yds", "player_receptions",
  "player_anytime_td",
  // Player props - NHL
  "player_shots_on_goal", "player_blocked_shots",
  // Player props - MLB
  "pitcher_strikeouts", "batter_total_bases", "batter_hits",
  "batter_home_runs", "batter_rbis",
  // Soccer props
  "btts", "draw_no_bet",
];

// Use direct Supabase client (no cookies needed — cron/API context, not browser)
function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Map Odds API sport_key to ESPN league for filtering
const SPORT_KEY_TO_LEAGUE: Record<string, string> = {
  'basketball_nba': 'NBA',
  'basketball_ncaab': 'NCAAB',
  'basketball_wnba': 'WNBA',
  'americanfootball_nfl': 'NFL',
  'americanfootball_ncaaf': 'NCAAF',
  'icehockey_nhl': 'NHL',
  'baseball_mlb': 'MLB',
  'soccer_epl': 'EPL',
  'soccer_usa_mls': 'MLS',
};

// Common team name aliases (Odds API name -> ESPN name)
const TEAM_NAME_ALIASES: Record<string, string> = {
  // NBA
  'la clippers': 'los angeles clippers',
  'la lakers': 'los angeles lakers',
  'ny knicks': 'new york knicks',
  // NFL
  'la rams': 'los angeles rams',
  'la chargers': 'los angeles chargers',
  'ny giants': 'new york giants',
  'ny jets': 'new york jets',
  // NHL
  'la kings': 'los angeles kings',
  'ny rangers': 'new york rangers',
  'ny islanders': 'new york islanders',
  // Soccer
  'man united': 'manchester united',
  'man city': 'manchester city',
};

// Fetch all team stats for CEQ calculation, organized by league
async function fetchAllTeamStats(supabase: ReturnType<typeof getSupabase>): Promise<Map<string, Map<string, TeamStatsData>>> {
  // Nested map: league -> teamName -> stats
  const teamStatsByLeague = new Map<string, Map<string, TeamStatsData>>();
  try {
    const { data, error } = await supabase
      .from('team_stats')
      .select('*')
      .order('updated_at', { ascending: false })
      .limit(500);

    if (error) {
      console.error('[Odds Sync] Team stats query error:', error);
      return teamStatsByLeague;
    }

    if (!data || data.length === 0) {
      console.warn('[Odds Sync] Team stats table is empty - GameEnvironment pillar will use defaults');
      return teamStatsByLeague;
    }

    console.log(`[Odds Sync] Loaded ${data.length} team stats from database`);

    for (const stat of data) {
      const league = stat.league?.toUpperCase() || 'UNKNOWN';
      const key = stat.team_name?.toLowerCase();

      if (!key) continue;

      // Get or create league map
      if (!teamStatsByLeague.has(league)) {
        teamStatsByLeague.set(league, new Map<string, TeamStatsData>());
      }
      const leagueMap = teamStatsByLeague.get(league)!;

      if (!leagueMap.has(key)) {
        const teamData: TeamStatsData = {
          team_id: stat.team_id,
          team_name: stat.team_name,
          team_abbrev: stat.team_abbrev,
          pace: stat.pace,
          offensive_rating: stat.offensive_rating,
          defensive_rating: stat.defensive_rating,
          net_rating: stat.net_rating,
          wins: stat.wins,
          losses: stat.losses,
          win_pct: stat.win_pct,
          home_wins: stat.home_wins,
          home_losses: stat.home_losses,
          away_wins: stat.away_wins,
          away_losses: stat.away_losses,
          streak: stat.streak,
          points_per_game: stat.points_per_game,
          points_allowed_per_game: stat.points_allowed_per_game,
          injuries: stat.injuries || [],
        };
        leagueMap.set(key, teamData);

        // Also index by abbreviation
        if (stat.team_abbrev) {
          const abbrevKey = stat.team_abbrev.toLowerCase();
          if (!leagueMap.has(abbrevKey)) {
            leagueMap.set(abbrevKey, teamData);
          }
        }

        // Also index by team nickname (last word of name)
        const words = stat.team_name?.split(' ') || [];
        if (words.length > 1) {
          const nickname = words[words.length - 1].toLowerCase();
          if (!leagueMap.has(nickname) && nickname.length > 3) {
            leagueMap.set(nickname, teamData);
          }
        }
      }
    }

    // Log stats per league
    for (const [league, map] of teamStatsByLeague) {
      console.log(`[Odds Sync] ${league}: ${map.size} team entries`);
    }
  } catch (e) {
    console.error('[Odds Sync] Team stats fetch failed:', e);
  }
  return teamStatsByLeague;
}

// Build game context from team names, filtered by sport
function buildGameContext(
  homeTeam: string,
  awayTeam: string,
  sportKey: string,
  teamStatsByLeague: Map<string, Map<string, TeamStatsData>>
): GameContextData {
  // Map sport_key to ESPN league
  const league = SPORT_KEY_TO_LEAGUE[sportKey] || sportKey.split('_')[1]?.toUpperCase() || 'UNKNOWN';
  const leagueMap = teamStatsByLeague.get(league);

  if (!leagueMap || leagueMap.size === 0) {
    // No stats for this league - skip silently (e.g., tennis, soccer)
    return { homeTeam: undefined, awayTeam: undefined, league };
  }

  // Normalize team names and apply aliases
  let homeKey = homeTeam?.toLowerCase();
  let awayKey = awayTeam?.toLowerCase();

  // Apply aliases if they exist
  if (homeKey && TEAM_NAME_ALIASES[homeKey]) {
    homeKey = TEAM_NAME_ALIASES[homeKey];
  }
  if (awayKey && TEAM_NAME_ALIASES[awayKey]) {
    awayKey = TEAM_NAME_ALIASES[awayKey];
  }

  // Direct lookup
  let homeStats = leagueMap.get(homeKey || '');
  let awayStats = leagueMap.get(awayKey || '');

  // Fallback: partial matching within the same league only
  if (!homeStats && homeKey) {
    for (const [key, stats] of leagueMap) {
      if (homeKey.includes(key) || key.includes(homeKey)) {
        homeStats = stats;
        break;
      }
    }
  }
  if (!awayStats && awayKey) {
    for (const [key, stats] of leagueMap) {
      if (awayKey.includes(key) || key.includes(awayKey)) {
        awayStats = stats;
        break;
      }
    }
  }

  // Log NOT FOUND teams for debugging (only for major sports with stats)
  if (!homeStats && homeKey) {
    console.log(`[Odds Sync] Team NOT FOUND: '${homeTeam}' for sport ${sportKey} (league=${league})`);
  }
  if (!awayStats && awayKey) {
    console.log(`[Odds Sync] Team NOT FOUND: '${awayTeam}' for sport ${sportKey} (league=${league})`);
  }

  return {
    homeTeam: homeStats,
    awayTeam: awayStats,
    league,
  };
}

// Count edges from a CEQ result (CEQ >= 56 = edge)
function countPeriodEdges(ceq: GameCEQ | null): number {
  if (!ceq) return 0;
  let count = 0;
  if (ceq.spreads?.home?.ceq !== undefined && ceq.spreads.home.ceq >= 56) count++;
  if (ceq.spreads?.away?.ceq !== undefined && ceq.spreads.away.ceq >= 56) count++;
  if (ceq.h2h?.home?.ceq !== undefined && ceq.h2h.home.ceq >= 56) count++;
  if (ceq.h2h?.away?.ceq !== undefined && ceq.h2h.away.ceq >= 56) count++;
  if (ceq.totals?.over?.ceq !== undefined && ceq.totals.over.ceq >= 56) count++;
  if (ceq.totals?.under?.ceq !== undefined && ceq.totals.under.ceq >= 56) count++;
  return count;
}

// Calculate and store edge counts for a game
async function calculateAndStoreEdgeCounts(
  supabase: ReturnType<typeof getSupabase>,
  game: any,
  sportKey: string,
  openingLine: number | undefined,
  snapshots: any[],
  teamStatsByLeague: Map<string, Map<string, TeamStatsData>>
): Promise<{ total: number; breakdown: Record<string, number> }> {
  const breakdown: Record<string, number> = {};
  let total = 0;

  // Build game context for CEQ calculation (filtered by sport/league)
  const gameContext = buildGameContext(game.home_team, game.away_team, sportKey, teamStatsByLeague);

  // Build per-book marketGroups from game data
  const bookmakers = game.bookmakers || [];
  if (bookmakers.length === 0) return { total: 0, breakdown: {} };

  // Helper to extract markets for a period
  const extractPeriodMarkets = (h2hKey: string, spreadsKey: string, totalsKey: string) => {
    const markets: any[] = [];
    for (const bk of bookmakers) {
      const marketsByKey: Record<string, any> = {};
      for (const m of bk.markets || []) marketsByKey[m.key] = m;

      const h2hM = marketsByKey[h2hKey];
      const spreadsM = marketsByKey[spreadsKey];
      const totalsM = marketsByKey[totalsKey];

      const extracted: any = {};
      if (spreadsM) {
        const home = spreadsM.outcomes?.find((o: any) => o.name === game.home_team);
        const away = spreadsM.outcomes?.find((o: any) => o.name === game.away_team);
        if (home && away) {
          extracted.spreads = {
            home: { line: home.point, price: home.price },
            away: { line: away.point, price: away.price },
          };
        }
      }
      if (h2hM) {
        const home = h2hM.outcomes?.find((o: any) => o.name === game.home_team);
        const away = h2hM.outcomes?.find((o: any) => o.name === game.away_team);
        if (home && away) {
          extracted.h2h = { home: { price: home.price }, away: { price: away.price } };
        }
      }
      if (totalsM) {
        const over = totalsM.outcomes?.find((o: any) => o.name === 'Over');
        const under = totalsM.outcomes?.find((o: any) => o.name === 'Under');
        if (over) {
          extracted.totals = { line: over.point, over: { price: over.price }, under: { price: under?.price } };
        }
      }
      if (Object.keys(extracted).length > 0) markets.push(extracted);
    }
    return markets;
  };

  // Calculate CEQ for a period
  const calculatePeriodCEQ = (periodKey: string, h2hKey: string, spreadsKey: string, totalsKey: string): GameCEQ | null => {
    const periodMarkets = extractPeriodMarkets(h2hKey, spreadsKey, totalsKey);
    if (periodMarkets.length === 0) return null;

    const getMedian = (values: number[]) => {
      if (values.length === 0) return undefined;
      const sorted = [...values].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };

    const spreadLines: number[] = [];
    const spreadHomeOdds: number[] = [];
    const spreadAwayOdds: number[] = [];
    const h2hHomeOdds: number[] = [];
    const h2hAwayOdds: number[] = [];
    const totalLines: number[] = [];
    const totalOverOdds: number[] = [];
    const totalUnderOdds: number[] = [];

    for (const m of periodMarkets) {
      if (m.spreads?.home?.line !== undefined) spreadLines.push(m.spreads.home.line);
      if (m.spreads?.home?.price !== undefined) spreadHomeOdds.push(m.spreads.home.price);
      if (m.spreads?.away?.price !== undefined) spreadAwayOdds.push(m.spreads.away.price);
      if (m.h2h?.home?.price !== undefined) h2hHomeOdds.push(m.h2h.home.price);
      if (m.h2h?.away?.price !== undefined) h2hAwayOdds.push(m.h2h.away.price);
      if (m.totals?.line !== undefined) totalLines.push(m.totals.line);
      if (m.totals?.over?.price !== undefined) totalOverOdds.push(m.totals.over.price);
      if (m.totals?.under?.price !== undefined) totalUnderOdds.push(m.totals.under.price);
    }

    const spreadLine = getMedian(spreadLines);
    const h2hHome = getMedian(h2hHomeOdds);
    const h2hAway = getMedian(h2hAwayOdds);
    const totalLine = getMedian(totalLines);

    const hasSpread = spreadLine !== undefined;
    const hasH2h = h2hHome !== undefined && h2hAway !== undefined;
    const hasTotals = totalLine !== undefined;

    if (!hasSpread && !hasH2h && !hasTotals) return null;

    const gameOdds = {
      spreads: hasSpread ? { home: { line: spreadLine!, odds: getMedian(spreadHomeOdds) || -110 }, away: { line: -spreadLine!, odds: getMedian(spreadAwayOdds) || -110 } } : undefined,
      h2h: hasH2h ? { home: h2hHome!, away: h2hAway! } : undefined,
      totals: hasTotals ? { line: totalLine!, over: getMedian(totalOverOdds) || -110, under: getMedian(totalUnderOdds) || -110 } : undefined,
    };

    // Estimate opening for periods
    let periodOpening: any = {};
    if (openingLine !== undefined) {
      const factor = periodKey === 'fullGame' ? 1 : periodKey.includes('Half') ? 0.5 : periodKey.startsWith('q') ? 0.25 : 0.33;
      periodOpening = { spreads: { home: openingLine * factor, away: -openingLine * factor } };
    }

    return calculateGameCEQ(gameOdds, periodOpening, [], {
      spreads: hasSpread ? { home: spreadHomeOdds, away: spreadAwayOdds } : undefined,
      h2h: hasH2h ? { home: h2hHomeOdds, away: h2hAwayOdds } : undefined,
      totals: hasTotals ? { over: totalOverOdds, under: totalUnderOdds } : undefined,
    }, {
      spreads: hasSpread ? { home: getMedian(spreadHomeOdds) || -110, away: getMedian(spreadAwayOdds) || -110 } : undefined,
      h2h: hasH2h ? { home: h2hHome, away: h2hAway } : undefined,
      totals: hasTotals ? { over: getMedian(totalOverOdds) || -110, under: getMedian(totalUnderOdds) || -110 } : undefined,
    }, gameContext);
  };

  // Calculate for all periods
  const periods = [
    { key: 'fullGame', h2h: 'h2h', spreads: 'spreads', totals: 'totals' },
    { key: 'firstHalf', h2h: 'h2h_h1', spreads: 'spreads_h1', totals: 'totals_h1' },
    { key: 'secondHalf', h2h: 'h2h_h2', spreads: 'spreads_h2', totals: 'totals_h2' },
    { key: 'q1', h2h: 'h2h_q1', spreads: 'spreads_q1', totals: 'totals_q1' },
    { key: 'q2', h2h: 'h2h_q2', spreads: 'spreads_q2', totals: 'totals_q2' },
    { key: 'q3', h2h: 'h2h_q3', spreads: 'spreads_q3', totals: 'totals_q3' },
    { key: 'q4', h2h: 'h2h_q4', spreads: 'spreads_q4', totals: 'totals_q4' },
    { key: 'p1', h2h: 'h2h_p1', spreads: 'spreads_p1', totals: 'totals_p1' },
    { key: 'p2', h2h: 'h2h_p2', spreads: 'spreads_p2', totals: 'totals_p2' },
    { key: 'p3', h2h: 'h2h_p3', spreads: 'spreads_p3', totals: 'totals_p3' },
  ];

  for (const p of periods) {
    const ceq = calculatePeriodCEQ(p.key, p.h2h, p.spreads, p.totals);
    const edges = countPeriodEdges(ceq);
    if (edges > 0) {
      breakdown[p.key] = edges;
      total += edges;
    }
  }

  // Upsert to game_edge_counts table
  await supabase.from('game_edge_counts').upsert({
    game_id: game.id,
    sport_key: sportKey,
    total_edges: total,
    breakdown,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'game_id' });

  return { total, breakdown };
}

// Pass 1: Fetch all games for a sport with core markets (h2h, spreads, totals)
async function fetchCoreOdds(
  sportKey: string
): Promise<{ games: any[]; cost: number; remaining: string | null }> {
  // The Odds API /odds endpoint returns all upcoming games by default
  // No date filtering parameters are supported on this endpoint
  const params = new URLSearchParams({
    apiKey: ODDS_API_KEY,
    regions: "us",
    markets: CORE_MARKETS,
    oddsFormat: "american",
    bookmakers: "fanduel,draftkings,pinnacle",
  });

  const url = `${ODDS_API_BASE}/sports/${sportKey}/odds?${params}`;
  const res = await fetch(url);

  if (!res.ok) {
    if (res.status === 422) {
      // Sport not in season or no events — not an error
      return { games: [], cost: 0, remaining: null };
    }
    throw new Error(`API ${res.status}`);
  }

  const remaining = res.headers.get("x-requests-remaining");
  const cost = parseInt(res.headers.get("x-requests-last") || "3", 10);
  const games: any[] = await res.json();

  return { games, cost, remaining };
}

// Pass 2: Enrich a single event with additional markets (props, alts, halves)
async function fetchEventMarkets(
  sportKey: string,
  eventId: string,
  markets: string[]
): Promise<{ bookmakers: any[]; cost: number; remaining: string | null }> {
  const params = new URLSearchParams({
    apiKey: ODDS_API_KEY,
    regions: "us",
    markets: markets.join(","),
    oddsFormat: "american",
    bookmakers: "fanduel,draftkings,pinnacle",
  });

  const url = `${ODDS_API_BASE}/sports/${sportKey}/events/${eventId}/odds?${params}`;
  const res = await fetch(url);

  if (!res.ok) {
    return { bookmakers: [], cost: 0, remaining: null };
  }

  const remaining = res.headers.get("x-requests-remaining");
  const cost = parseInt(res.headers.get("x-requests-last") || "0", 10);
  const data = await res.json();

  return { bookmakers: data.bookmakers || [], cost, remaining };
}

// Merge additional bookmaker markets into existing game object
function mergeBookmakers(game: any, additionalBookmakers: any[]) {
  for (const newBk of additionalBookmakers) {
    const existingBk = game.bookmakers.find(
      (b: any) => b.key === newBk.key
    );
    if (existingBk) {
      existingBk.markets.push(...newBk.markets);
    } else {
      game.bookmakers.push(newBk);
    }
  }
}

// Build snapshot rows from games for odds_snapshots table
function buildSnapshotRows(games: any[], sportKey: string, snapshotTime: string) {
  const rows: any[] = [];
  for (const game of games) {
    if (!game.bookmakers) continue;
    for (const bk of game.bookmakers) {
      for (const market of bk.markets || []) {
        if (!SNAPSHOT_MARKETS.includes(market.key)) continue;
        const isProp = market.key.startsWith("player_") ||
                       market.key.startsWith("pitcher_") ||
                       market.key.startsWith("batter_");
        const isTeamTotal = market.key === "team_totals";
        for (const outcome of market.outcomes || []) {
          // For props: outcome.description is player name, outcome.name is "Over"/"Under"
          // For team_totals: outcome.description is team name, outcome.name is "Over"/"Under"
          // For game markets: outcome.name is team name or "Over"/"Under"
          const outcomeType = (isProp || isTeamTotal) && outcome.description
            ? `${outcome.description}|${outcome.name}` // e.g., "DeMar DeRozan|Over" or "Chicago Bulls|Over"
            : outcome.name;

          rows.push({
            game_id: game.id,
            sport_key: sportKey,
            book_key: bk.key,
            market: market.key,
            outcome_type: outcomeType,
            line: outcome.point ?? null,
            odds: outcome.price,
            snapshot_time: snapshotTime,
          });
        }
      }
    }
  }
  return rows;
}

// Cleanup finished games from cached_odds (games that ended 5+ hours ago)
// We keep live/in-progress games so they continue to be polled
async function cleanupStaleGames(supabase: ReturnType<typeof getSupabase>): Promise<number> {
  // Only delete games that started more than 5 hours ago (definitely finished)
  const fiveHoursAgo = new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString();
  const { data, error } = await supabase
    .from("cached_odds")
    .delete()
    .lt("game_data->>commence_time", fiveHoursAgo)
    .select("game_id");

  if (error) {
    console.error("[Odds Sync] Cleanup failed:", error.message);
    return 0;
  }

  const count = data?.length || 0;
  if (count > 0) {
    console.log(`[Odds Sync] Cleaned up ${count} finished games from cached_odds`);
  }
  return count;
}

// Get the most recent spread line for a game from line_snapshots
async function getPreviousSpreadLine(
  supabase: ReturnType<typeof getSupabase>,
  gameId: string
): Promise<number | null> {
  const { data, error } = await supabase
    .from('line_snapshots')
    .select('line')
    .eq('game_id', gameId)
    .eq('market_type', 'spread')
    .eq('market_period', 'full')
    .order('snapshot_time', { ascending: false })
    .limit(1)
    .single();

  if (error || !data) return null;
  return data.line;
}

// Trigger pillar recalculation via Python backend
async function triggerPillarRecalculation(
  gameId: string,
  sport: string
): Promise<{ composite: number | null; error?: string }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/pillars/${sport}/${gameId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(10000), // 10s timeout
    });

    if (!res.ok) {
      return { composite: null, error: `HTTP ${res.status}` };
    }

    const data = await res.json();
    return { composite: data.composite_score ?? null };
  } catch (e: any) {
    return { composite: null, error: e?.message || 'Unknown error' };
  }
}

// Check line movement and trigger recalculation if needed
async function checkLineMovementAndRecalculate(
  supabase: ReturnType<typeof getSupabase>,
  game: any,
  sport: string,
  sportKey: string
): Promise<{ triggered: boolean; delta?: number; oldComposite?: number; newComposite?: number }> {
  // Extract current spread line from game data
  const bookmakers = game.bookmakers || [];
  let currentLine: number | null = null;

  for (const bk of bookmakers) {
    const spreadsMarket = bk.markets?.find((m: any) => m.key === 'spreads');
    if (spreadsMarket?.outcomes) {
      const homeOutcome = spreadsMarket.outcomes.find((o: any) => o.name === game.home_team);
      if (homeOutcome?.point !== undefined) {
        currentLine = homeOutcome.point;
        break;
      }
    }
  }

  if (currentLine === null) {
    return { triggered: false };
  }

  // Get previous line
  const previousLine = await getPreviousSpreadLine(supabase, game.id);
  if (previousLine === null) {
    return { triggered: false };
  }

  // Check if movement exceeds threshold
  const delta = Math.abs(currentLine - previousLine);
  if (delta < MOVEMENT_THRESHOLD) {
    return { triggered: false };
  }

  console.log(`[ODDS_SYNC] Game ${game.id} line moved ${delta.toFixed(1)} pts (${previousLine} -> ${currentLine}) - recalculating pillars`);

  // Get current composite from cached_odds or game_edge_counts
  const { data: edgeData } = await supabase
    .from('game_edge_counts')
    .select('composite_score')
    .eq('game_id', game.id)
    .single();
  const oldComposite = edgeData?.composite_score ?? null;

  // Trigger recalculation
  const result = await triggerPillarRecalculation(game.id, sport);

  if (result.error) {
    console.error(`[ODDS_SYNC] Game ${game.id} pillar recalculation failed: ${result.error}`);
    return { triggered: true, delta };
  }

  if (result.composite !== null) {
    // Store updated composite in game_edge_counts
    await supabase
      .from('game_edge_counts')
      .upsert({
        game_id: game.id,
        sport_key: sportKey,
        composite_score: result.composite,
        updated_at: new Date().toISOString(),
      }, { onConflict: 'game_id' });

    console.log(`[ODDS_SYNC] Game ${game.id} composite updated: ${oldComposite?.toFixed(3) ?? 'null'} -> ${result.composite.toFixed(3)}`);
    return { triggered: true, delta, oldComposite: oldComposite ?? undefined, newComposite: result.composite };
  }

  return { triggered: true, delta };
}

// Shared sync logic used by both GET (cron) and POST (manual)
async function runSync() {
  if (!ODDS_API_KEY) {
    return NextResponse.json(
      { error: "ODDS_API_KEY not configured" },
      { status: 500 }
    );
  }

  const supabase = getSupabase();

  // Fetch team stats once for all games (used by GameEnvironment pillar)
  const teamStatsByLeague = await fetchAllTeamStats(supabase);

  // Cleanup stale games before syncing new ones
  const gamesDeleted = await cleanupStaleGames(supabase);

  let totalSynced = 0;
  let totalCost = 0;
  let lastRemaining: string | null = null;
  const errors: string[] = [];
  const sportSummary: Record<
    string,
    { games: number; enriched: number; cost: number; edges?: number; recalcs?: number }
  > = {};
  const snapshotTime = new Date().toISOString();

  for (const [sport, sportKey] of Object.entries(SPORT_KEYS)) {
    try {
      // Pass 1: Core markets for all games
      const { games, cost: coreCost, remaining } =
        await fetchCoreOdds(sportKey);
      if (remaining) lastRemaining = remaining;
      let sportCost = coreCost;
      let enrichedCount = 0;

      if (games.length === 0) {
        sportSummary[sport] = { games: 0, enriched: 0, cost: sportCost };
        continue;
      }

      // Pass 2: Per-event enrichment (pro sports only)
      const additionalMarkets = EVENT_MARKETS[sportKey];
      if (additionalMarkets && additionalMarkets.length > 0) {
        for (const game of games) {
          try {
            const { bookmakers, cost, remaining: evtRemaining } =
              await fetchEventMarkets(
                sportKey,
                game.id,
                additionalMarkets
              );
            sportCost += cost;
            if (evtRemaining) lastRemaining = evtRemaining;

            if (bookmakers.length > 0) {
              mergeBookmakers(game, bookmakers);
              enrichedCount++;
            }
          } catch (e: any) {
            // Log but continue — don't fail the whole sport on one event
            console.error(
              `[Odds Sync] ${sport} event ${game.id} enrich failed:`,
              e?.message
            );
          }
        }
      }

      totalCost += sportCost;

      // Upsert to Supabase cached_odds
      const rows = games.map((game: any) => ({
        sport_key: sportKey,
        game_id: game.id,
        game_data: game,
        updated_at: new Date().toISOString(),
      }));

      const { error } = await supabase
        .from("cached_odds")
        .upsert(rows, { onConflict: "sport_key,game_id" });

      if (error) {
        errors.push(`${sport}: ${error.message}`);
      } else {
        totalSynced += games.length;
      }

      // Check for significant line movements and trigger pillar recalculation
      // Use Promise.allSettled so slow/failed calls don't block the sync
      let recalcTriggered = 0;
      const recalcPromises = games.map((game: any) =>
        checkLineMovementAndRecalculate(supabase, game, sport, sportKey)
      );
      const recalcResults = await Promise.allSettled(recalcPromises);
      for (const result of recalcResults) {
        if (result.status === 'fulfilled' && result.value.triggered) {
          recalcTriggered++;
        }
      }
      if (recalcTriggered > 0) {
        console.log(`[ODDS_SYNC] ${sport}: Triggered ${recalcTriggered} pillar recalculations due to line movement`);
      }

      // Calculate and store edge counts for each game
      // Get opening lines for this sport's games
      const gameIds = games.map((g: any) => g.id);
      const { data: openingData } = await supabase
        .from('odds_snapshots')
        .select('game_id, line')
        .in('game_id', gameIds)
        .eq('market', 'spreads')
        .not('line', 'is', null)
        .order('snapshot_time', { ascending: true })
        .limit(gameIds.length * 2);

      const openingLines: Record<string, number> = {};
      if (openingData) {
        for (const row of openingData) {
          if (!openingLines[row.game_id] && row.line !== null) {
            openingLines[row.game_id] = row.line;
          }
        }
      }

      // Calculate edge counts in parallel (batched)
      let totalEdgeCounts = 0;
      const EDGE_BATCH = 10;
      for (let i = 0; i < games.length; i += EDGE_BATCH) {
        const batch = games.slice(i, i + EDGE_BATCH);
        await Promise.all(batch.map(async (game: any) => {
          try {
            const { total } = await calculateAndStoreEdgeCounts(
              supabase,
              game,
              sportKey,
              openingLines[game.id],
              [], // snapshots not needed for basic edge counting
              teamStatsByLeague
            );
            totalEdgeCounts += total;
          } catch (e) {
            // Silent fail for edge counts - not critical
          }
        }));
      }
      console.log(`[Odds Sync] ${sport}: Calculated ${totalEdgeCounts} total edges across ${games.length} games`);

      // Save snapshots to odds_snapshots
      const snapshotRows = buildSnapshotRows(games, sportKey, snapshotTime);
      let snapshotsSaved = 0;
      let snapshotErrors: string[] = [];

      if (snapshotRows.length > 0) {
        // Batch insert in chunks of 500 to avoid payload limits
        for (let i = 0; i < snapshotRows.length; i += 500) {
          const chunk = snapshotRows.slice(i, i + 500);
          const { error: snapError } = await supabase
            .from("odds_snapshots")
            .insert(chunk);
          if (snapError) {
            const errMsg = `${sport} snapshot chunk ${i}-${i + chunk.length} failed: ${snapError.message}`;
            console.error(`[Odds Sync] ${errMsg}`);
            snapshotErrors.push(errMsg);
            errors.push(errMsg);  // ADD TO ERRORS ARRAY!
          } else {
            snapshotsSaved += chunk.length;
          }
        }
      }

      console.log(`[Odds Sync] ${sport}: ${games.length} games, ${snapshotRows.length} snapshot rows built, ${snapshotsSaved} saved`);

      // Trigger edge detection for each game
      let edgesDetected = 0;
      const detector = new EdgeDetector();
      for (const game of games) {
        try {
          const gameSnapshots = snapshotRows.filter(r => r.game_id === game.id);
          if (gameSnapshots.length >= 2) {
            const edges = await detector.detectAllEdges(game.id, sportKey, gameSnapshots);
            for (const edge of edges) {
              await upsertEdge(game.id, sportKey, edge, game.commence_time);
              edgesDetected++;
            }
          }
        } catch (e) {
          console.error(`[Odds Sync] Edge detection failed for ${game.id}:`, e);
        }
      }

      sportSummary[sport] = {
        games: games.length,
        enriched: enrichedCount,
        cost: sportCost,
        edges: edgesDetected,
        recalcs: recalcTriggered,
      };

      console.log(
        `[Odds Sync] ${sport}: ${games.length} games, ${enrichedCount} enriched, ${edgesDetected} edges, ${recalcTriggered} recalcs (${sportCost} reqs)`
      );
    } catch (e: any) {
      const msg = e?.message || String(e);
      console.error(`[Odds Sync] ${sport} failed:`, msg);
      errors.push(`${sport}: ${msg}`);
    }
  }

  // Update edge lifecycle (expire started games, update fading edges)
  let lifecycleStats = { updated: 0, expired: 0, fading: 0 };
  try {
    const lifecycle = new EdgeLifecycleManager();
    lifecycleStats = await lifecycle.updateEdgeStatuses();
    const expiredGames = await lifecycle.expireStartedGames();
    lifecycleStats.expired += expiredGames;
    console.log(`[Odds Sync] Edge lifecycle: ${lifecycleStats.updated} updated, ${lifecycleStats.expired} expired, ${lifecycleStats.fading} fading`);
  } catch (e) {
    console.error('[Odds Sync] Edge lifecycle update failed:', e);
  }

  console.log(
    `[Odds Sync] Done: ${totalSynced} games, ${totalCost} reqs used, ${lastRemaining} remaining`
  );

  return NextResponse.json({
    synced: totalSynced,
    staleGamesDeleted: gamesDeleted,
    requestsUsed: totalCost,
    remaining: lastRemaining,
    sports: sportSummary,
    edgeLifecycle: lifecycleStats,
    errors: errors.length > 0 ? errors : undefined,
  });
}

// Vercel cron max duration (seconds) — prevent premature timeout
export const maxDuration = 300;

// GET handler for Vercel cron (sends Authorization: Bearer <CRON_SECRET>)
export async function GET(request: Request) {
  try {
    const authHeader = request.headers.get("authorization") || "";
    const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
    if (!CRON_SECRET || token !== CRON_SECRET) {
      console.error("[Odds Sync] Auth failed. CRON_SECRET set:", !!CRON_SECRET, "Token received:", !!token);
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    return await runSync();
  } catch (error: any) {
    console.error("[Odds Sync] Fatal error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error", message: error?.message },
      { status: 500 }
    );
  }
}

// POST handler for manual sync (uses x-cron-secret header)
export async function POST(request: Request) {
  try {
    const authHeader = request.headers.get("x-cron-secret");
    if (!CRON_SECRET || authHeader !== CRON_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    return await runSync();
  } catch (error) {
    console.error("[Odds Sync] Fatal error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
