// Edge Lifecycle Manager
// Handles status transitions for live edges: active → fading → expired

import { createClient } from '@supabase/supabase-js';
import { LiveEdge, EdgeStatus, EDGE_THRESHOLDS } from '../types/edge';
import { EdgeDetector, OddsSnapshot } from './edge-detector';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export class EdgeLifecycleManager {
  private detector: EdgeDetector;

  constructor() {
    this.detector = new EdgeDetector();
  }

  // Get all active edges
  async getActiveEdges(): Promise<LiveEdge[]> {
    const { data, error } = await supabase
      .from('live_edges')
      .select('*')
      .in('status', ['active', 'fading'])
      .order('detected_at', { ascending: false });

    if (error) {
      console.error('[EdgeLifecycle] Error fetching active edges:', error);
      return [];
    }

    return data || [];
  }

  // Get edges for a specific game
  async getGameEdges(gameId: string): Promise<LiveEdge[]> {
    const { data, error } = await supabase
      .from('live_edges')
      .select('*')
      .eq('game_id', gameId)
      .order('detected_at', { ascending: false });

    if (error) {
      console.error('[EdgeLifecycle] Error fetching game edges:', error);
      return [];
    }

    return data || [];
  }

  // Get recent snapshots for a game
  private async getGameSnapshots(gameId: string): Promise<OddsSnapshot[]> {
    const { data, error } = await supabase
      .from('odds_snapshots')
      .select('*')
      .eq('game_id', gameId)
      .order('snapshot_time', { ascending: true });

    if (error) {
      console.error('[EdgeLifecycle] Error fetching snapshots:', error);
      return [];
    }

    return data || [];
  }

  // Evaluate if an edge is still active, fading, or expired
  evaluateEdgeStatus(edge: LiveEdge, currentMagnitude: number | null): EdgeStatus {
    // Check if game has started (expired)
    if (edge.expires_at) {
      const expiresAt = new Date(edge.expires_at);
      if (new Date() >= expiresAt) {
        return 'expired';
      }
    }

    // If we couldn't recalculate the edge, it may have expired
    if (currentMagnitude === null) {
      return 'expired';
    }

    // Check if edge has faded below threshold
    const fadingThreshold = edge.edge_magnitude * EDGE_THRESHOLDS.FADING_THRESHOLD;
    if (currentMagnitude < fadingThreshold) {
      return 'fading';
    }

    // Edge is still active
    return 'active';
  }

  // Recalculate edge magnitude from current snapshots
  async recalculateEdgeMagnitude(edge: LiveEdge): Promise<number | null> {
    const snapshots = await this.getGameSnapshots(edge.game_id);
    if (snapshots.length === 0) return null;

    // Filter to the relevant market and outcome
    const relevantSnaps = snapshots.filter(
      (s) => s.market === edge.market_type || s.market.includes(edge.market_type)
    );

    if (relevantSnaps.length < 2) return null;

    // Get latest values to compare with initial
    const outcomeSnaps = relevantSnaps.filter(
      (s) => s.outcome_type === edge.outcome_key
    );

    if (outcomeSnaps.length === 0) return null;

    // Sort by time and get latest
    const sorted = outcomeSnaps.sort(
      (a, b) => new Date(b.snapshot_time).getTime() - new Date(a.snapshot_time).getTime()
    );
    const latest = sorted[0];

    // Calculate current magnitude based on edge type
    switch (edge.edge_type) {
      case 'line_movement':
      case 'reverse_line': {
        if (edge.initial_value === null || latest.line === null) return null;
        return Math.abs(latest.line - edge.initial_value);
      }
      case 'juice_improvement': {
        if (edge.initial_value === null) return null;
        const initialJuice = Math.abs(edge.initial_value);
        const currentJuice = Math.abs(latest.odds);
        return initialJuice - currentJuice; // Positive means improvement
      }
      case 'exchange_divergence': {
        // Would need to re-fetch sharp book line to compare
        // For now, use current value vs sharp_book_line
        if (edge.sharp_book_line === null) return null;
        const currentValue = edge.market_type === 'h2h' ? latest.odds : latest.line;
        if (currentValue === null) return null;
        return Math.abs(currentValue - edge.sharp_book_line);
      }
      default:
        return null;
    }
  }

  // Handle status transition for an edge
  async transitionEdge(edge: LiveEdge, newStatus: EdgeStatus): Promise<void> {
    const updates: Partial<LiveEdge> & { updated_at: string } = {
      status: newStatus,
      updated_at: new Date().toISOString(),
    };

    if (newStatus === 'fading' && !edge.faded_at) {
      updates.faded_at = new Date().toISOString();
    }
    if (newStatus === 'expired' && !edge.expired_at) {
      updates.expired_at = new Date().toISOString();
    }

    const { error } = await supabase
      .from('live_edges')
      .update(updates)
      .eq('id', edge.id);

    if (error) {
      console.error('[EdgeLifecycle] Error transitioning edge:', error);
    } else {
      console.log(`[EdgeLifecycle] Edge ${edge.id} transitioned: ${edge.status} → ${newStatus}`);
    }
  }

  // Main update loop - check all active edges and update status
  async updateEdgeStatuses(): Promise<{ updated: number; expired: number; fading: number }> {
    const stats = { updated: 0, expired: 0, fading: 0 };
    const activeEdges = await this.getActiveEdges();

    for (const edge of activeEdges) {
      try {
        const currentMagnitude = await this.recalculateEdgeMagnitude(edge);
        const newStatus = this.evaluateEdgeStatus(edge, currentMagnitude);

        if (newStatus !== edge.status) {
          await this.transitionEdge(edge, newStatus);
          stats.updated++;
          if (newStatus === 'expired') stats.expired++;
          if (newStatus === 'fading') stats.fading++;
        }

        // Update current value if it changed
        if (currentMagnitude !== null && edge.edge_magnitude !== currentMagnitude) {
          await supabase
            .from('live_edges')
            .update({
              edge_magnitude: currentMagnitude,
              updated_at: new Date().toISOString(),
            })
            .eq('id', edge.id);
        }
      } catch (e) {
        console.error(`[EdgeLifecycle] Error processing edge ${edge.id}:`, e);
      }
    }

    return stats;
  }

  // Expire edges for games that have started
  async expireStartedGames(): Promise<number> {
    const now = new Date().toISOString();

    const { data, error } = await supabase
      .from('live_edges')
      .update({
        status: 'expired',
        expired_at: now,
        updated_at: now,
      })
      .in('status', ['active', 'fading'])
      .lt('expires_at', now)
      .select('id');

    if (error) {
      console.error('[EdgeLifecycle] Error expiring started games:', error);
      return 0;
    }

    return data?.length || 0;
  }

  // Clean up old expired edges (older than 7 days)
  async cleanupOldEdges(): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 7);

    const { data, error } = await supabase
      .from('live_edges')
      .delete()
      .eq('status', 'expired')
      .lt('expired_at', cutoffDate.toISOString())
      .select('id');

    if (error) {
      console.error('[EdgeLifecycle] Error cleaning up old edges:', error);
      return 0;
    }

    return data?.length || 0;
  }
}

// Upsert an edge to the database
export async function upsertEdge(
  gameId: string,
  sport: string,
  edge: {
    edgeType: string;
    magnitude: number;
    edgePct: number;
    initialValue: number;
    currentValue: number;
    triggeringBook: string;
    bestCurrentBook: string;
    confidence: number;
    outcomeKey: string;
    marketType: string;
    sharpBookLine?: number;
    notes?: string;
  },
  expiresAt?: string
): Promise<void> {
  const edgeRow = {
    game_id: gameId,
    sport,
    market_type: edge.marketType,
    outcome_key: edge.outcomeKey,
    edge_type: edge.edgeType,
    initial_value: edge.initialValue,
    current_value: edge.currentValue,
    edge_magnitude: edge.magnitude,
    edge_pct: edge.edgePct,
    triggering_book: edge.triggeringBook,
    best_current_book: edge.bestCurrentBook,
    sharp_book_line: edge.sharpBookLine || null,
    status: 'active',
    confidence: edge.confidence,
    notes: edge.notes || null,
    expires_at: expiresAt || null,
    updated_at: new Date().toISOString(),
  };

  const { error } = await supabase
    .from('live_edges')
    .upsert(edgeRow, {
      onConflict: 'game_id,market_type,outcome_key,edge_type',
    });

  if (error) {
    console.error('[EdgeLifecycle] Error upserting edge:', error);
  }
}
