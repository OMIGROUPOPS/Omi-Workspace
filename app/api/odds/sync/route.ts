import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const CRON_SECRET = process.env.CRON_SECRET || "";
const ODDS_API_KEY = process.env.ODDS_API_KEY || "";
const ODDS_API_BASE = "https://api.the-odds-api.com/v4";

const SPORT_KEYS: Record<string, string> = {
  NFL: "americanfootball_nfl",
  NCAAF: "americanfootball_ncaaf",
  NBA: "basketball_nba",
  NHL: "icehockey_nhl",
  NCAAB: "basketball_ncaab",
  MLB: "baseball_mlb",
  WNBA: "basketball_wnba",
  MMA: "mma_mixed_martial_arts",
  TENNIS_AO: "tennis_atp_australian_open",
  TENNIS_FO: "tennis_atp_french_open",
  TENNIS_USO: "tennis_atp_us_open",
  TENNIS_WIM: "tennis_atp_wimbledon",
};

// Core markets fetched via /sports/{sport}/odds (all sports)
const CORE_MARKETS = "h2h,spreads,totals";

// Per-event additional markets fetched via /sports/{sport}/events/{id}/odds
// Only for pro sports — college/MMA use core only to conserve quota
const EVENT_MARKETS: Record<string, string[]> = {
  americanfootball_nfl: [
    // Halves
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    // Alternates & team totals
    "alternate_spreads", "alternate_totals", "team_totals",
    // Player props
    "player_pass_yds", "player_rush_yds", "player_reception_yds",
    "player_receptions", "player_pass_tds", "player_anytime_td",
  ], // 15 markets
  basketball_nba: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_rebounds", "player_assists",
    "player_threes", "player_blocks", "player_steals",
  ], // 15 markets
  icehockey_nhl: [
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_assists", "player_shots_on_goal",
    "player_blocked_shots",
  ], // 7 markets
  baseball_mlb: [
    "alternate_spreads", "alternate_totals", "team_totals",
    "pitcher_strikeouts", "batter_total_bases", "batter_hits",
    "batter_home_runs", "batter_rbis",
  ], // 8 markets
  basketball_wnba: [
    "h2h_h1", "spreads_h1", "totals_h1",
    "h2h_h2", "spreads_h2", "totals_h2",
    "alternate_spreads", "alternate_totals", "team_totals",
    "player_points", "player_rebounds", "player_assists",
    "player_threes",
  ], // 13 markets
};

// Market keys to snapshot for line movement charts (includes halves)
const SNAPSHOT_MARKETS = [
  "h2h", "spreads", "totals",
  "h2h_h1", "spreads_h1", "totals_h1",
  "h2h_h2", "spreads_h2", "totals_h2",
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
        for (const outcome of market.outcomes || []) {
          rows.push({
            game_id: game.id,
            sport_key: sportKey,
            book_key: bk.key,
            market: market.key,
            outcome_type: outcome.name,
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
    { games: number; enriched: number; cost: number }
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
      if (snapshotRows.length > 0) {
        // Batch insert in chunks of 500 to avoid payload limits
        for (let i = 0; i < snapshotRows.length; i += 500) {
          const chunk = snapshotRows.slice(i, i + 500);
          const { error: snapError } = await supabase
            .from("odds_snapshots")
            .insert(chunk);
          if (snapError) {
            console.error(`[Odds Sync] ${sport} snapshot save failed:`, snapError.message);
          }
        }
      }

      sportSummary[sport] = {
        games: games.length,
        enriched: enrichedCount,
        cost: sportCost,
      };

      console.log(
        `[Odds Sync] ${sport}: ${games.length} games, ${enrichedCount} enriched (${sportCost} reqs)`
      );
    } catch (e: any) {
      const msg = e?.message || String(e);
      console.error(`[Odds Sync] ${sport} failed:`, msg);
      errors.push(`${sport}: ${msg}`);
    }
  }

  console.log(
    `[Odds Sync] Done: ${totalSynced} games, ${totalCost} reqs used, ${lastRemaining} remaining`
  );

  return NextResponse.json({
    synced: totalSynced,
    requestsUsed: totalCost,
    remaining: lastRemaining,
    sports: sportSummary,
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
