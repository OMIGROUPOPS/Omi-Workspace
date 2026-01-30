import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { EdgeDetector } from '@/lib/edge/engine/edge-detector';
import { EdgeLifecycleManager, upsertEdge } from '@/lib/edge/engine/edge-lifecycle';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Get snapshots for a game
async function getGameSnapshots(gameId: string) {
  const { data, error } = await supabase
    .from('odds_snapshots')
    .select('*')
    .eq('game_id', gameId)
    .order('snapshot_time', { ascending: true });

  if (error) {
    console.error('[Edge Detect] Error fetching snapshots:', error);
    return [];
  }

  return data || [];
}

// Get game commence time for expiry
async function getGameCommenceTime(gameId: string): Promise<string | undefined> {
  const { data, error } = await supabase
    .from('cached_odds')
    .select('game_data')
    .eq('game_id', gameId)
    .single();

  if (error || !data) return undefined;

  return data.game_data?.commence_time;
}

// POST /api/edges/detect - Detect edges for a game
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { gameId, sport } = body;

    if (!gameId || !sport) {
      return NextResponse.json(
        { error: 'gameId and sport are required' },
        { status: 400 }
      );
    }

    // Get snapshots for this game
    const snapshots = await getGameSnapshots(gameId);

    if (snapshots.length < 2) {
      return NextResponse.json({
        detected: 0,
        message: 'Insufficient snapshots for edge detection',
      });
    }

    // Get game expire time
    const expiresAt = await getGameCommenceTime(gameId);

    // Run edge detection
    const detector = new EdgeDetector();
    const newEdges = await detector.detectAllEdges(gameId, sport, snapshots);

    // Upsert detected edges to database
    let upsertedCount = 0;
    for (const edge of newEdges) {
      try {
        await upsertEdge(gameId, sport, edge, expiresAt);
        upsertedCount++;
      } catch (e) {
        console.error('[Edge Detect] Error upserting edge:', e);
      }
    }

    // Update lifecycle for existing edges
    const lifecycle = new EdgeLifecycleManager();
    const lifecycleStats = await lifecycle.updateEdgeStatuses();

    return NextResponse.json({
      detected: newEdges.length,
      upserted: upsertedCount,
      lifecycle: lifecycleStats,
      edges: newEdges.map((e) => ({
        type: e.edgeType,
        market: e.marketType,
        outcome: e.outcomeKey,
        magnitude: e.magnitude,
        confidence: e.confidence,
      })),
    });
  } catch (e: any) {
    console.error('[Edge Detect] Error:', e);
    return NextResponse.json(
      { error: e?.message || 'Internal error' },
      { status: 500 }
    );
  }
}

// GET /api/edges/detect - Run edge detection for all active games
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const authHeader = request.headers.get('authorization') || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';
  const cronSecret = process.env.CRON_SECRET || '';

  // Require auth for cron-style detection
  if (!cronSecret || token !== cronSecret) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Get all upcoming games from cached_odds
    const { data: games, error } = await supabase
      .from('cached_odds')
      .select('game_id, sport_key, game_data')
      .gte('game_data->>commence_time', new Date().toISOString());

    if (error) {
      console.error('[Edge Detect] Error fetching games:', error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    let totalDetected = 0;
    const sportSummary: Record<string, number> = {};

    const detector = new EdgeDetector();

    for (const game of games || []) {
      try {
        const snapshots = await getGameSnapshots(game.game_id);
        if (snapshots.length < 2) continue;

        const expiresAt = game.game_data?.commence_time;
        const edges = await detector.detectAllEdges(
          game.game_id,
          game.sport_key,
          snapshots
        );

        for (const edge of edges) {
          await upsertEdge(game.game_id, game.sport_key, edge, expiresAt);
        }

        totalDetected += edges.length;
        sportSummary[game.sport_key] = (sportSummary[game.sport_key] || 0) + edges.length;
      } catch (e) {
        console.error(`[Edge Detect] Error processing game ${game.game_id}:`, e);
      }
    }

    // Update lifecycle for all edges
    const lifecycle = new EdgeLifecycleManager();
    const lifecycleStats = await lifecycle.updateEdgeStatuses();
    await lifecycle.expireStartedGames();

    return NextResponse.json({
      gamesProcessed: games?.length || 0,
      edgesDetected: totalDetected,
      bySport: sportSummary,
      lifecycle: lifecycleStats,
    });
  } catch (e: any) {
    console.error('[Edge Detect] Error:', e);
    return NextResponse.json(
      { error: e?.message || 'Internal error' },
      { status: 500 }
    );
  }
}
