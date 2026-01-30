import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const BACKEND_URL = process.env.BACKEND_URL || "https://api.omigroup.io";

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export async function GET() {
  const supabase = getSupabase();

  // Get game IDs from cached_odds (these are CURRENT games)
  const { data: cachedGames } = await supabase
    .from("cached_odds")
    .select("game_id, game_data, updated_at")
    .limit(10);

  const cachedIds = (cachedGames || []).map(r => r.game_id);

  // For each cached game, check if it has snapshots
  const gamesWithSnapshots: any[] = [];
  for (const game of cachedGames || []) {
    const { count } = await supabase
      .from("odds_snapshots")
      .select("*", { count: "exact", head: true })
      .eq("game_id", game.game_id);

    gamesWithSnapshots.push({
      game_id: game.game_id,
      teams: `${game.game_data?.away_team} @ ${game.game_data?.home_team}`,
      updated_at: game.updated_at,
      snapshot_count: count || 0
    });
  }

  // Get all unique game IDs from snapshots
  const { data: snapshotIds } = await supabase
    .from("odds_snapshots")
    .select("game_id")
    .limit(1000);

  const uniqueSnapshotIds = [...new Set((snapshotIds || []).map(r => r.game_id))];

  // Check how many snapshot game_ids match cached_odds game_ids
  const matchingIds = uniqueSnapshotIds.filter(id => cachedIds.includes(id));
  const orphanedSnapshotIds = uniqueSnapshotIds.filter(id => !cachedIds.includes(id));

  return NextResponse.json({
    current_games: gamesWithSnapshots,
    snapshot_stats: {
      total_unique_game_ids: uniqueSnapshotIds.length,
      matching_current_games: matchingIds.length,
      orphaned_old_games: orphanedSnapshotIds.length,
      orphaned_ids_sample: orphanedSnapshotIds.slice(0, 3)
    },
    diagnosis: matchingIds.length === 0
      ? "CRITICAL: No snapshots exist for current games! Sync may be failing to save snapshots."
      : `OK: ${matchingIds.length} current games have snapshots.`
  });
}
