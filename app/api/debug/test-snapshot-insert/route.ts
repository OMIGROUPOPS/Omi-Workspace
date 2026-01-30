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

  // Try to insert a test snapshot row
  const testRow = {
    game_id: "test_" + Date.now(),
    sport_key: "basketball_nba",
    book_key: "fanduel",
    market: "spreads",
    outcome_type: "Test Team",
    line: -5.5,
    odds: -110,
    snapshot_time: new Date().toISOString(),
  };

  const { data, error } = await supabase
    .from("odds_snapshots")
    .insert(testRow)
    .select();

  if (error) {
    return NextResponse.json({
      success: false,
      error: error.message,
      code: error.code,
      details: error.details,
      hint: error.hint,
      test_row: testRow,
      fix: "Run in Supabase SQL: ALTER TABLE odds_snapshots DISABLE ROW LEVEL SECURITY;"
    });
  }

  // Clean up test row
  await supabase
    .from("odds_snapshots")
    .delete()
    .eq("game_id", testRow.game_id);

  return NextResponse.json({
    success: true,
    message: "INSERT works! The sync should be saving snapshots.",
    inserted: data
  });
}
