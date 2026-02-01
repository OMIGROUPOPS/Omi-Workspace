import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const ODDS_API_KEY = process.env.ODDS_API_KEY || '';
const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Manual sync for debugging - syncs ONE sport to test
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sport = searchParams.get('sport') || 'basketball_nba';

  if (!ODDS_API_KEY) {
    return NextResponse.json({ error: 'ODDS_API_KEY not configured' }, { status: 500 });
  }

  try {
    // Fetch odds from API
    const url = `${ODDS_API_BASE}/sports/${sport}/odds?apiKey=${ODDS_API_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=american`;
    const res = await fetch(url, { cache: 'no-store' });

    if (!res.ok) {
      return NextResponse.json({ error: `Odds API error: ${res.status}` }, { status: 500 });
    }

    const games = await res.json();

    // Log what we got
    const sampleGame = games[0];
    console.log('[Debug Sync] Sample game:', {
      id: sampleGame?.id,
      homeTeam: sampleGame?.home_team,
      hasBookmakers: !!sampleGame?.bookmakers,
      bookmakerCount: sampleGame?.bookmakers?.length || 0,
      bookmakerKeys: sampleGame?.bookmakers?.map((b: any) => b.key) || [],
    });

    // Upsert to Supabase
    const supabase = getSupabase();
    const rows = games.map((game: any) => ({
      sport_key: sport,
      game_id: game.id,
      game_data: game,
      updated_at: new Date().toISOString(),
    }));

    const { error } = await supabase
      .from('cached_odds')
      .upsert(rows, { onConflict: 'sport_key,game_id' });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      sport,
      gamesSynced: games.length,
      sampleBookmakers: sampleGame?.bookmakers?.map((b: any) => b.key) || [],
      message: 'Refresh the dashboard to see updated data',
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
