import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

export async function GET() {
  const supabase = getSupabase();

  // Get cache stats
  const { data, error } = await supabase
    .from('cached_odds')
    .select('sport_key, game_id, updated_at, game_data')
    .limit(5);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  // Analyze bookmaker data
  const analysis = data?.map((row: any) => ({
    sport: row.sport_key,
    gameId: row.game_id,
    updatedAt: row.updated_at,
    homeTeam: row.game_data?.home_team,
    hasBookmakers: !!row.game_data?.bookmakers,
    bookmakerCount: row.game_data?.bookmakers?.length || 0,
    bookmakerKeys: row.game_data?.bookmakers?.map((b: any) => b.key) || [],
  }));

  return NextResponse.json({
    cacheRows: data?.length || 0,
    analysis,
    message: 'Check bookmakerKeys - should contain fanduel, draftkings etc',
  });
}
