import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export async function GET() {
  const supabase = getSupabase();

  // Count total snapshots
  const { count: snapshotCount, error: countError } = await supabase
    .from("odds_snapshots")
    .select("*", { count: "exact", head: true });

  // Get recent snapshots
  const { data: recent, error: recentError } = await supabase
    .from("odds_snapshots")
    .select("game_id, sport_key, market, book_key, snapshot_time")
    .order("snapshot_time", { ascending: false })
    .limit(10);

  // Count cached odds
  const { count: cachedCount } = await supabase
    .from("cached_odds")
    .select("*", { count: "exact", head: true });

  // Count distinct games in snapshots
  const { data: distinctGames } = await supabase
    .from("odds_snapshots")
    .select("game_id")
    .limit(1000);

  const uniqueGameCount = distinctGames ? new Set(distinctGames.map(g => g.game_id)).size : 0;

  return NextResponse.json({
    odds_snapshots: {
      total_rows: snapshotCount ?? `Error: ${countError?.message}`,
      distinct_games: uniqueGameCount,
      recent: recent || [],
    },
    cached_odds: {
      total_rows: cachedCount,
    },
    diagnosis: snapshotCount === 0
      ? "PROBLEM: odds_snapshots is empty. Cron job may not be running or may be failing."
      : snapshotCount && snapshotCount < 100
        ? "WARNING: Very few snapshots. Cron may have just started or is failing."
        : "OK: Snapshots are being collected.",
  });
}
