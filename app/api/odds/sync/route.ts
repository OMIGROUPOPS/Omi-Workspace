import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

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

function getSupabase() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
      },
    }
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

export async function POST(request: Request) {
  try {
    const authHeader = request.headers.get("x-cron-secret");
    if (!CRON_SECRET || authHeader !== CRON_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

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

        // Upsert to Supabase
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
  } catch (error) {
    console.error("[Odds Sync] Fatal error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
