import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function getDirectSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

async function fetchLineHistory(gameId: string, market: string = 'spread', period: string = 'full', book?: string) {
  const allSnapshots: any[] = [];

  // 1. Query odds_snapshots from Supabase
  try {
    const marketMap: Record<string, string> = {
      'spread': 'spreads',
      'moneyline': 'h2h',
      'total': 'totals',
    };
    const baseMarket = marketMap[market] || market;
    const snapshotMarket = period === 'full' ? baseMarket : `${baseMarket}_${period}`;

    const supabase = getDirectSupabase();
    let query = supabase
      .from('odds_snapshots')
      .select('*')
      .eq('game_id', gameId)
      .eq('market', snapshotMarket)
      .order('snapshot_time', { ascending: true });

    if (book) {
      query = query.eq('book_key', book);
    }

    const { data, error } = await query;
    if (!error && data && data.length > 0) {
      data.forEach((row: any) => {
        allSnapshots.push({
          snapshot_time: row.snapshot_time,
          book_key: row.book_key,
          outcome_type: row.outcome_type,
          line: row.line,
          odds: row.odds,
          source: 'odds_snapshots',
        });
      });
    }
  } catch (e) {
    console.error('[LineHistory API] odds_snapshots query error:', e);
  }

  // 2. Query line_snapshots from backend
  try {
    let url = `${BACKEND_URL}/api/lines/${gameId}?market=${market}&period=${period}`;
    if (book) url += `&book=${book}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.snapshots && data.snapshots.length > 0) {
        data.snapshots.forEach((row: any) => {
          allSnapshots.push({
            snapshot_time: row.snapshot_time,
            book_key: row.book_key,
            outcome_type: row.outcome_type || null,
            line: row.line,
            odds: row.odds,
            source: 'line_snapshots',
          });
        });
      }
    }
  } catch (e) {
    // Backend unavailable
  }

  // 3. Deduplicate
  const seen = new Map<string, any>();
  for (const snap of allSnapshots) {
    const key = `${snap.snapshot_time}-${snap.book_key}-${snap.outcome_type || 'home'}`;
    const existing = seen.get(key);
    if (!existing || (snap.source === 'odds_snapshots' && existing.source === 'line_snapshots')) {
      seen.set(key, snap);
    }
  }

  // 4. Sort and clean
  const merged = Array.from(seen.values())
    .sort((a, b) => new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime())
    .map(({ source, ...rest }) => rest);

  return merged;
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ gameId: string }> }
) {
  const { gameId } = await params;
  const { searchParams } = new URL(request.url);
  const period = searchParams.get('period') || 'full';
  const book = searchParams.get('book') || undefined;

  // Fetch all three markets for this period in parallel
  const [spread, moneyline, total] = await Promise.all([
    fetchLineHistory(gameId, 'spread', period, book),
    fetchLineHistory(gameId, 'moneyline', period, book),
    fetchLineHistory(gameId, 'total', period, book),
  ]);

  return NextResponse.json({
    period,
    spread,
    moneyline,
    total,
  });
}
