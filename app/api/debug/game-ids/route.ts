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

  // Get game IDs from odds_snapshots
  const { data: snapshotIds } = await supabase
    .from("odds_snapshots")
    .select("game_id")
    .limit(10);

  const uniqueSnapshotIds = [...new Set((snapshotIds || []).map(r => r.game_id))];

  // Get game IDs from cached_odds (Odds API format)
  const { data: cachedGames } = await supabase
    .from("cached_odds")
    .select("game_id, game_data")
    .limit(5);

  const cachedIds = (cachedGames || []).map(r => ({
    game_id: r.game_id,
    game_data_id: r.game_data?.id,
    teams: `${r.game_data?.away_team} @ ${r.game_data?.home_team}`
  }));

  // Try to fetch from backend to see their ID format
  let backendIds: any[] = [];
  try {
    const res = await fetch(`${BACKEND_URL}/api/edges/NBA`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(3000)
    });
    if (res.ok) {
      const data = await res.json();
      backendIds = (data.games || []).slice(0, 5).map((g: any) => ({
        game_id: g.game_id,
        teams: `${g.away_team} @ ${g.home_team}`
      }));
    }
  } catch (e) {
    backendIds = [{ error: "Backend unreachable" }];
  }

  return NextResponse.json({
    snapshot_game_ids: uniqueSnapshotIds.slice(0, 5),
    cached_odds_ids: cachedIds,
    backend_ids: backendIds,
    diagnosis: {
      snapshot_format: uniqueSnapshotIds[0]?.length === 32 ? "hash (Odds API)" : "other",
      match_check: "Compare backend_ids.game_id with snapshot_game_ids - they must match!"
    }
  });
}
