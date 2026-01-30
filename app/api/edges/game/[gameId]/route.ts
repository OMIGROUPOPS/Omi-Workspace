import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

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

// GET /api/edges/game/[gameId] - Returns edges for a specific game
export async function GET(
  request: Request,
  { params }: { params: { gameId: string } }
) {
  const { gameId } = params;
  const { searchParams } = new URL(request.url);
  const includeExpired = searchParams.get('include_expired') === 'true';

  if (!gameId) {
    return NextResponse.json({ error: 'gameId is required' }, { status: 400 });
  }

  const supabase = getSupabase();

  let query = supabase
    .from('live_edges')
    .select('*')
    .eq('game_id', gameId)
    .order('detected_at', { ascending: false });

  if (!includeExpired) {
    query = query.in('status', ['active', 'fading']);
  }

  const { data, error } = await query;

  if (error) {
    console.error('[Edges API] Error fetching game edges:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  // Deduplicate edges by game_id + market_type + outcome_key + edge_type
  // Keep the most recent edge (first since ordered by detected_at desc)
  const seenKeys = new Set<string>();
  const dedupedEdges = (data || []).filter((edge) => {
    const key = `${edge.game_id}|${edge.market_type}|${edge.outcome_key}|${edge.edge_type}`;
    if (seenKeys.has(key)) {
      return false; // Skip duplicate
    }
    seenKeys.add(key);
    return true;
  });

  // Group edges by status for easier consumption
  const active = dedupedEdges.filter((e) => e.status === 'active');
  const fading = dedupedEdges.filter((e) => e.status === 'fading');
  const expired = dedupedEdges.filter((e) => e.status === 'expired');

  return NextResponse.json({
    gameId,
    edges: dedupedEdges,
    summary: {
      active: active.length,
      fading: fading.length,
      expired: expired.length,
      total: dedupedEdges.length,
    },
    grouped: {
      active,
      fading,
      expired: includeExpired ? expired : [],
    },
  });
}
