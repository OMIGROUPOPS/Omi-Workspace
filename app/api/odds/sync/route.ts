import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { EdgeDetector } from "@/lib/edge/engine/edge-detector";
import { EdgeLifecycleManager, upsertEdge } from "@/lib/edge/engine/edge-lifecycle";

const CRON_SECRET = process.env.CRON_SECRET || "";
const ODDS_API_KEY = process.env.ODDS_API_KEY || "";
const ODDS_API_BASE = "https://api.the-odds-api.com/v4";

const SPORT_KEYS: Record<string, string> = {
  // American Football
  NFL: "americanfootball_nfl",
  NCAAF: "americanfootball_ncaaf",

  // Basketball
  NBA: "basketball_nba",
  NCAAB: "basketball_ncaab",
  WNBA: "basketball_wnba",
  WNCAAB: "basketball_wncaab",
  EUROLEAGUE: "basketball_euroleague",
  NBL: "basketball_nbl",

  // Baseball
  MLB: "baseball_mlb",

  // Ice Hockey
  NHL: "icehockey_nhl",
  AHL: "icehockey_ahl",
  SHL: "icehockey_sweden_hockey_league",
  LIIGA: "icehockey_liiga",
  MESTIS: "icehockey_mestis",

  // Tennis - Grand Slams
  TENNIS_AO: "tennis_atp_australian_open",
  TENNIS_FO: "tennis_atp_french_open",
  TENNIS_USO: "tennis_atp_us_open",
  TENNIS_WIM: "tennis_atp_wimbledon",

  // Combat Sports
  MMA: "mma_mixed_martial_arts",
  BOXING: "boxing_boxing",

  // Soccer - England
  EPL: "soccer_epl",
  EFL_CHAMP: "soccer_efl_champ",
  FA_CUP: "soccer_fa_cup",

  // Soccer - Europe Top Leagues
  LA_LIGA: "soccer_spain_la_liga",
  BUNDESLIGA: "soccer_germany_bundesliga",
  SERIE_A: "soccer_italy_serie_a",
  LIGUE_1: "soccer_france_ligue_one",
  EREDIVISIE: "soccer_netherlands_eredivisie",

  // Soccer - International
  UCL: "soccer_uefa_champs_league",
  EUROPA: "soccer_uefa_europa_league",

  // Soccer - Americas
  MLS: "soccer_usa_mls",
  LIGA_MX: "soccer_mexico_ligamx",

  // Cricket
  IPL: "cricket_ipl",
  BIG_BASH: "cricket_big_bash",
  CRICKET_TEST: "cricket_test_match",

  // Rugby
  NRL: "rugbyleague_nrl",

  // Golf (outrights only)
  MASTERS: "golf_masters_tournament_winner",
  PGA_CHAMP: "golf_pga_championship_winner",
  US_OPEN: "golf_us_open_winner",
  THE_OPEN: "golf_the_open_championship_winner",

  // Aussie Rules
  AFL: "aussierules_afl",
};

// Core markets fetched via /sports/{sport}/odds (all sports)
const CORE_MARKETS = "h2h,spreads,totals";

// Per-event additional markets fetched via /sports/{sport}/events/{id}/odds
// Pro sports get full enrichment; others get basic enrichment to conserve quota
const EVENT_MARKETS: Record<string, string[]> = {
  // American Football
  americanfootball_nfl: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_pass_yds", "player_rush_yds", "player_reception_yds",
    "player_receptions", "player_pass_tds", "player_anytime_td",
  ],
  americanfootball_ncaaf: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
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
  basketball_wnba: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_rebounds", "player_assists",
    "player_threes",
  ],
  basketball_euroleague: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals",
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
  icehockey_sweden_hockey_league: [
    "alternate_spreads", "alternate_totals",
  ],
  icehockey_liiga: [
    "alternate_spreads", "alternate_totals",
  ],

  // Baseball
  baseball_mlb: [
    "alternate_spreads", "alternate_totals", "team_totals",
    "pitcher_strikeouts", "batter_total_bases", "batter_hits",
    "batter_home_runs", "batter_rbis",
  ],

  // Soccer (top leagues get more markets)
  soccer_epl: [
    "alternate_spreads", "alternate_totals",
    "btts", "draw_no_bet",
  ],
  soccer_uefa_champs_league: [
    "alternate_spreads", "alternate_totals",
  ],
  soccer_spain_la_liga: [
    "alternate_spreads", "alternate_totals",
  ],
  soccer_germany_bundesliga: [
    "alternate_spreads", "alternate_totals",
  ],
  soccer_italy_serie_a: [
    "alternate_spreads", "alternate_totals",
  ],
  soccer_france_ligue_one: [
    "alternate_spreads", "alternate_totals",
  ],
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

// Pass 1: Fetch all games for a sport with core markets (h2h, spreads, totals)
async function fetchCoreOdds(
  sportKey: string
): Promise<{ games: any[]; cost: number; remaining: string | null }> {
  const params = new URLSearchParams({
    apiKey: ODDS_API_KEY,
    regions: "us",
    markets: CORE_MARKETS,
    oddsFormat: "american",
    bookmakers: "fanduel,draftkings",
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
    bookmakers: "fanduel,draftkings",
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
        for (const outcome of market.outcomes || []) {
          // For props: outcome.description is player name, outcome.name is "Over"/"Under"
          // For game markets: outcome.name is team name or "Over"/"Under"
          const outcomeType = isProp && outcome.description
            ? `${outcome.description}|${outcome.name}` // e.g., "DeMar DeRozan|Over"
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

// Shared sync logic used by both GET (cron) and POST (manual)
async function runSync() {
  if (!ODDS_API_KEY) {
    return NextResponse.json(
      { error: "ODDS_API_KEY not configured" },
      { status: 500 }
    );
  }

  const supabase = getSupabase();
  let totalSynced = 0;
  let totalCost = 0;
  let lastRemaining: string | null = null;
  const errors: string[] = [];
  const sportSummary: Record<
    string,
    { games: number; enriched: number; cost: number; edges?: number }
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
      };

      console.log(
        `[Odds Sync] ${sport}: ${games.length} games, ${enrichedCount} enriched, ${edgesDetected} edges (${sportCost} reqs)`
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
