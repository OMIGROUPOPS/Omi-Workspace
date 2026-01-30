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
  const errors: string[] = [];

  // Count total snapshots
  const { count: snapshotCount, error: countError } = await supabase
    .from("odds_snapshots")
    .select("*", { count: "exact", head: true });

  if (countError) errors.push(`count: ${countError.message}`);

  // Get recent snapshots - try without ordering first
  const { data: sample, error: sampleError } = await supabase
    .from("odds_snapshots")
    .select("*")
    .limit(5);

  if (sampleError) errors.push(`sample: ${sampleError.message}`);

  // Try ordered query
  const { data: recent, error: recentError } = await supabase
    .from("odds_snapshots")
    .select("game_id, sport_key, market, book_key, snapshot_time, odds, line")
    .order("snapshot_time", { ascending: false })
    .limit(10);

  if (recentError) errors.push(`recent: ${recentError.message}`);

  // Count cached odds
  const { count: cachedCount, error: cachedError } = await supabase
    .from("cached_odds")
    .select("*", { count: "exact", head: true });

  if (cachedError) errors.push(`cached: ${cachedError.message}`);

  // Count distinct games in snapshots
  const { data: distinctGames, error: distinctError } = await supabase
    .from("odds_snapshots")
    .select("game_id")
    .limit(1000);

  if (distinctError) errors.push(`distinct: ${distinctError.message}`);

  const uniqueGameCount = distinctGames ? new Set(distinctGames.map(g => g.game_id)).size : 0;

  // Check table structure by getting one row
  const { data: oneRow, error: oneRowError } = await supabase
    .from("odds_snapshots")
    .select("*")
    .limit(1)
    .single();

  const columns = oneRow ? Object.keys(oneRow) : [];

  return NextResponse.json({
    odds_snapshots: {
      total_rows: snapshotCount ?? null,
      distinct_games: uniqueGameCount,
      columns: columns,
      sample_row: oneRow || null,
      recent: recent || [],
      sample_unordered: sample || [],
    },
    cached_odds: {
      total_rows: cachedCount ?? null,
    },
    errors: errors.length > 0 ? errors : null,
    diagnosis: snapshotCount === 0 || snapshotCount === null
      ? "PROBLEM: odds_snapshots is empty or unreadable. Check RLS policies."
      : snapshotCount && snapshotCount < 100
        ? "WARNING: Very few snapshots. Cron may have just started."
        : "OK: Snapshots are being collected.",
    rls_hint: errors.length > 0
      ? "RLS may be blocking. Run in Supabase SQL: ALTER TABLE odds_snapshots ENABLE ROW LEVEL SECURITY; CREATE POLICY 'Allow all' ON odds_snapshots FOR ALL USING (true);"
      : null,
  });
}
