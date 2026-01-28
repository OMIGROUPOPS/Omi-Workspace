import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const gameId = searchParams.get("gameId");
  const player = searchParams.get("player");
  const market = searchParams.get("market");
  const book = searchParams.get("book");

  if (!gameId || !player || !market) {
    return NextResponse.json(
      { error: "Missing required parameters: gameId, player, market" },
      { status: 400 }
    );
  }

  try {
    const supabase = getSupabase();

    // Query for both Over and Under outcomes for this player/market
    // outcome_type format is "PlayerName|Over" or "PlayerName|Under"
    const { data, error } = await supabase
      .from("odds_snapshots")
      .select("*")
      .eq("game_id", gameId)
      .eq("market", market)
      .like("outcome_type", `${player}|%`)
      .order("snapshot_time", { ascending: true });

    if (error) {
      console.error("[prop-history] Supabase error:", error);
      return NextResponse.json({ snapshots: [] });
    }

    // Filter by book if specified
    let snapshots = data || [];
    if (book) {
      snapshots = snapshots.filter((s: any) => s.book_key === book);
    }

    // Transform to expected format
    const transformed = snapshots.map((row: any) => {
      // Parse outcome_type to get player and side
      const [playerName, side] = (row.outcome_type || "").split("|");
      return {
        snapshot_time: row.snapshot_time,
        book_key: row.book_key,
        player: playerName,
        side: side || "Over", // "Over" or "Under"
        line: row.line,
        odds: row.odds,
      };
    });

    return NextResponse.json({ snapshots: transformed });
  } catch (e) {
    console.error("[prop-history] Error:", e);
    return NextResponse.json({ snapshots: [] });
  }
}
