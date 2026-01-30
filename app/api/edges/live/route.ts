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

// GET /api/edges/live - Returns all active/fading edges
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sport = searchParams.get('sport');
  const status = searchParams.get('status') || 'active,fading';
  const limit = parseInt(searchParams.get('limit') || '50', 10);
  const edgeType = searchParams.get('edge_type');

  const supabase = getSupabase();

  let query = supabase
    .from('live_edges')
    .select('*')
    .in('status', status.split(','))
    .order('detected_at', { ascending: false })
    .limit(limit);

  if (sport) {
    query = query.eq('sport', sport);
  }

  if (edgeType) {
    query = query.eq('edge_type', edgeType);
  }

  const { data, error } = await query;

  if (error) {
    console.error('[Edges API] Error fetching edges:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ edges: data || [] });
}
