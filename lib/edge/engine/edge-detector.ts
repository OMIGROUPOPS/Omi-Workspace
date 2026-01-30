// Edge Detection Engine
// Identifies betting edges from odds snapshots

import {
  EdgeType,
  MarketType,
  EdgeDetectionResult,
  EDGE_THRESHOLDS,
  EDGE_CONFIDENCE_WEIGHTS,
  SHARP_BOOKS,
  SOFT_BOOKS,
} from '../types/edge';

export interface OddsSnapshot {
  id?: string;
  game_id: string;
  sport_key: string;
  book_key: string;
  market: string;
  outcome_type: string;
  line: number | null;
  odds: number;
  snapshot_time: string;
}

export interface BookOddsData {
  bookKey: string;
  line: number | null;
  odds: number;
  snapshotTime: string;
}

// Group snapshots by book and outcome for analysis
function groupSnapshots(snapshots: OddsSnapshot[]): Map<string, OddsSnapshot[]> {
  const grouped = new Map<string, OddsSnapshot[]>();

  for (const snap of snapshots) {
    const key = `${snap.book_key}|${snap.outcome_type}`;
    const existing = grouped.get(key) || [];
    existing.push(snap);
    grouped.set(key, existing);
  }

  // Sort each group by time
  for (const [key, snaps] of grouped) {
    snaps.sort((a, b) =>
      new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime()
    );
  }

  return grouped;
}

// Get latest snapshot per book for an outcome
function getLatestByBook(snapshots: OddsSnapshot[]): Map<string, OddsSnapshot> {
  const latest = new Map<string, OddsSnapshot>();

  for (const snap of snapshots) {
    const existing = latest.get(snap.book_key);
    if (!existing || new Date(snap.snapshot_time) > new Date(existing.snapshot_time)) {
      latest.set(snap.book_key, snap);
    }
  }

  return latest;
}

// Detect line movement edges
export function detectLineMovement(
  snapshots: OddsSnapshot[],
  marketType: MarketType
): EdgeDetectionResult[] {
  const results: EdgeDetectionResult[] = [];
  const threshold = EDGE_THRESHOLDS.LINE_MOVEMENT[marketType] || 0.5;
  const grouped = groupSnapshots(snapshots);

  // Process each outcome type separately
  const outcomeGroups = new Map<string, OddsSnapshot[]>();
  for (const snap of snapshots) {
    const existing = outcomeGroups.get(snap.outcome_type) || [];
    existing.push(snap);
    outcomeGroups.set(snap.outcome_type, existing);
  }

  for (const [outcomeKey, outcomeSnaps] of outcomeGroups) {
    // Get earliest and latest snapshots across all books
    const sorted = [...outcomeSnaps].sort((a, b) =>
      new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime()
    );

    if (sorted.length < 2) continue;

    // For line-based markets (spreads, totals), compare lines
    if (marketType === 'spreads' || marketType === 'totals' || marketType === 'player_props') {
      const withLines = sorted.filter(s => s.line !== null);
      if (withLines.length < 2) continue;

      const earliest = withLines[0];
      const latestByBook = getLatestByBook(withLines);

      // Find best current book (most favorable line)
      let bestBook: OddsSnapshot | null = null;
      let bestMagnitude = 0;

      for (const [bookKey, latest] of latestByBook) {
        if (earliest.line === null || latest.line === null) continue;

        const movement = Math.abs(latest.line - earliest.line);
        if (movement >= threshold && movement > bestMagnitude) {
          bestMagnitude = movement;
          bestBook = latest;
        }
      }

      if (bestBook && earliest.line !== null && bestBook.line !== null) {
        const movement = bestBook.line - earliest.line;
        const conf = EDGE_CONFIDENCE_WEIGHTS.line_movement;
        const confidence = Math.min(
          conf.base + (Math.abs(movement) / 0.5) * conf.perHalfPoint,
          conf.max
        );

        results.push({
          edgeType: 'line_movement',
          magnitude: Math.abs(movement),
          edgePct: (Math.abs(movement) / Math.abs(earliest.line || 1)) * 100,
          initialValue: earliest.line,
          currentValue: bestBook.line,
          triggeringBook: earliest.book_key,
          bestCurrentBook: bestBook.book_key,
          confidence,
          outcomeKey,
          marketType,
          notes: `Line moved ${movement > 0 ? '+' : ''}${movement.toFixed(1)} from ${earliest.line} to ${bestBook.line}`,
        });
      }
    }

    // For h2h (moneyline), compare odds directly
    if (marketType === 'h2h') {
      const earliest = sorted[0];
      const latestByBook = getLatestByBook(sorted);

      let bestBook: OddsSnapshot | null = null;
      let bestMagnitude = 0;

      for (const [bookKey, latest] of latestByBook) {
        const movement = Math.abs(latest.odds - earliest.odds);
        if (movement >= threshold && movement > bestMagnitude) {
          bestMagnitude = movement;
          bestBook = latest;
        }
      }

      if (bestBook) {
        const movement = bestBook.odds - earliest.odds;
        const conf = EDGE_CONFIDENCE_WEIGHTS.line_movement;
        const confidence = Math.min(
          conf.base + (Math.abs(movement) / 10) * conf.perHalfPoint,
          conf.max
        );

        results.push({
          edgeType: 'line_movement',
          magnitude: Math.abs(movement),
          edgePct: (Math.abs(movement) / Math.abs(earliest.odds || 100)) * 100,
          initialValue: earliest.odds,
          currentValue: bestBook.odds,
          triggeringBook: earliest.book_key,
          bestCurrentBook: bestBook.book_key,
          confidence,
          outcomeKey,
          marketType,
          notes: `Moneyline moved ${movement > 0 ? '+' : ''}${movement} from ${earliest.odds} to ${bestBook.odds}`,
        });
      }
    }
  }

  return results;
}

// Detect juice improvement edges
export function detectJuiceImprovement(
  snapshots: OddsSnapshot[],
  marketType: MarketType
): EdgeDetectionResult[] {
  const results: EdgeDetectionResult[] = [];
  const threshold = EDGE_THRESHOLDS.JUICE_IMPROVEMENT;

  // Group by outcome
  const outcomeGroups = new Map<string, OddsSnapshot[]>();
  for (const snap of snapshots) {
    const existing = outcomeGroups.get(snap.outcome_type) || [];
    existing.push(snap);
    outcomeGroups.set(snap.outcome_type, existing);
  }

  for (const [outcomeKey, outcomeSnaps] of outcomeGroups) {
    // Sort by time
    const sorted = [...outcomeSnaps].sort((a, b) =>
      new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime()
    );

    if (sorted.length < 2) continue;

    const earliest = sorted[0];
    const latestByBook = getLatestByBook(sorted);

    // Find best juice improvement
    let bestBook: OddsSnapshot | null = null;
    let bestImprovement = 0;

    for (const [bookKey, latest] of latestByBook) {
      // For negative odds, a smaller absolute value is better (less juice)
      // -110 is standard, -105 is better (5 cents improvement)
      const earliestJuice = Math.abs(earliest.odds);
      const latestJuice = Math.abs(latest.odds);

      // Only consider improvements (juice went down)
      if (latestJuice < earliestJuice) {
        const improvement = earliestJuice - latestJuice;
        if (improvement >= threshold && improvement > bestImprovement) {
          bestImprovement = improvement;
          bestBook = latest;
        }
      }
    }

    if (bestBook) {
      const earliestJuice = Math.abs(earliest.odds);
      const improvement = earliestJuice - Math.abs(bestBook.odds);
      const conf = EDGE_CONFIDENCE_WEIGHTS.juice_improvement;
      const confidence = Math.min(
        conf.base + improvement * conf.perCent,
        conf.max
      );

      results.push({
        edgeType: 'juice_improvement',
        magnitude: improvement,
        edgePct: (improvement / earliestJuice) * 100,
        initialValue: earliest.odds,
        currentValue: bestBook.odds,
        triggeringBook: earliest.book_key,
        bestCurrentBook: bestBook.book_key,
        confidence,
        outcomeKey,
        marketType,
        notes: `Juice improved by ${improvement} cents (${earliest.odds} to ${bestBook.odds})`,
      });
    }
  }

  return results;
}

// Detect exchange/sharp book divergence
export function detectExchangeDivergence(
  snapshots: OddsSnapshot[],
  marketType: MarketType
): EdgeDetectionResult[] {
  const results: EdgeDetectionResult[] = [];
  const threshold = EDGE_THRESHOLDS.EXCHANGE_DIVERGENCE[marketType] || 1.0;

  // Get latest snapshot per book per outcome
  const outcomeGroups = new Map<string, OddsSnapshot[]>();
  for (const snap of snapshots) {
    const existing = outcomeGroups.get(snap.outcome_type) || [];
    existing.push(snap);
    outcomeGroups.set(snap.outcome_type, existing);
  }

  for (const [outcomeKey, outcomeSnaps] of outcomeGroups) {
    const latestByBook = getLatestByBook(outcomeSnaps);

    // Find sharp book line
    let sharpSnap: OddsSnapshot | null = null;
    for (const sharpBook of SHARP_BOOKS) {
      if (latestByBook.has(sharpBook)) {
        sharpSnap = latestByBook.get(sharpBook)!;
        break;
      }
    }

    if (!sharpSnap) continue;

    const sharpLine = marketType === 'h2h' ? sharpSnap.odds : sharpSnap.line;
    if (sharpLine === null) continue;

    // Compare soft books to sharp line
    for (const softBook of SOFT_BOOKS) {
      const softSnap = latestByBook.get(softBook);
      if (!softSnap) continue;

      const softLine = marketType === 'h2h' ? softSnap.odds : softSnap.line;
      if (softLine === null) continue;

      const divergence = Math.abs(softLine - sharpLine);
      if (divergence >= threshold) {
        const conf = EDGE_CONFIDENCE_WEIGHTS.exchange_divergence;
        const confidence = Math.min(
          conf.base + divergence * conf.perPoint,
          conf.max
        );

        results.push({
          edgeType: 'exchange_divergence',
          magnitude: divergence,
          edgePct: (divergence / Math.abs(sharpLine || 1)) * 100,
          initialValue: softLine,
          currentValue: softLine,
          triggeringBook: softBook,
          bestCurrentBook: softBook,
          sharpBookLine: sharpLine,
          confidence,
          outcomeKey,
          marketType,
          notes: `${softBook} at ${softLine} vs sharp (${sharpSnap.book_key}) at ${sharpLine}`,
        });
      }
    }
  }

  return results;
}

// Detect reverse line movement (contrarian signal)
// This is a simplified version - full implementation would need public betting data
export function detectReverseLine(
  snapshots: OddsSnapshot[],
  marketType: MarketType,
  publicBettingPct?: { home: number; away: number }
): EdgeDetectionResult[] {
  const results: EdgeDetectionResult[] = [];

  // Without public betting data, we can detect rapid line movements
  // that suggest sharp money against public perception
  const threshold = EDGE_THRESHOLDS.LINE_MOVEMENT[marketType] || 0.5;

  // Group by outcome
  const outcomeGroups = new Map<string, OddsSnapshot[]>();
  for (const snap of snapshots) {
    const existing = outcomeGroups.get(snap.outcome_type) || [];
    existing.push(snap);
    outcomeGroups.set(snap.outcome_type, existing);
  }

  for (const [outcomeKey, outcomeSnaps] of outcomeGroups) {
    const sorted = [...outcomeSnaps].sort((a, b) =>
      new Date(a.snapshot_time).getTime() - new Date(b.snapshot_time).getTime()
    );

    if (sorted.length < 3) continue;

    // Look for rapid movements in last few snapshots
    const recentSnaps = sorted.slice(-5);
    if (recentSnaps.length < 2) continue;

    const recentStart = recentSnaps[0];
    const recentEnd = recentSnaps[recentSnaps.length - 1];

    if (marketType === 'spreads' || marketType === 'totals') {
      if (recentStart.line === null || recentEnd.line === null) continue;

      const movement = Math.abs(recentEnd.line - recentStart.line);
      const timeSpanHours =
        (new Date(recentEnd.snapshot_time).getTime() -
          new Date(recentStart.snapshot_time).getTime()) /
        (1000 * 60 * 60);

      // Rapid movement: significant move in short time
      if (movement >= threshold * 2 && timeSpanHours <= 2) {
        const conf = EDGE_CONFIDENCE_WEIGHTS.reverse_line;
        const confidence = Math.min(
          conf.base + (movement / 0.5) * conf.perHalfPoint,
          conf.max
        );

        results.push({
          edgeType: 'reverse_line',
          magnitude: movement,
          edgePct: (movement / Math.abs(recentStart.line || 1)) * 100,
          initialValue: recentStart.line,
          currentValue: recentEnd.line,
          triggeringBook: recentEnd.book_key,
          bestCurrentBook: recentEnd.book_key,
          confidence,
          outcomeKey,
          marketType,
          notes: `Rapid move: ${movement.toFixed(1)} pts in ${timeSpanHours.toFixed(1)}h - likely sharp action`,
        });
      }
    }
  }

  return results;
}

// Main edge detection function - runs all detection algorithms
export class EdgeDetector {
  async detectAllEdges(
    gameId: string,
    sport: string,
    snapshots: OddsSnapshot[]
  ): Promise<EdgeDetectionResult[]> {
    const allEdges: EdgeDetectionResult[] = [];

    // Group snapshots by market type
    const marketGroups = new Map<string, OddsSnapshot[]>();
    for (const snap of snapshots) {
      const existing = marketGroups.get(snap.market) || [];
      existing.push(snap);
      marketGroups.set(snap.market, existing);
    }

    for (const [market, marketSnaps] of marketGroups) {
      // Determine market type
      let marketType: MarketType = 'h2h';
      if (market.includes('spread')) marketType = 'spreads';
      else if (market.includes('total')) marketType = 'totals';
      else if (market.startsWith('player_') || market.startsWith('pitcher_') || market.startsWith('batter_')) {
        marketType = 'player_props';
      }

      // Run all detection algorithms
      const lineMovementEdges = detectLineMovement(marketSnaps, marketType);
      const juiceEdges = detectJuiceImprovement(marketSnaps, marketType);
      const divergenceEdges = detectExchangeDivergence(marketSnaps, marketType);
      const reverseEdges = detectReverseLine(marketSnaps, marketType);

      allEdges.push(
        ...lineMovementEdges,
        ...juiceEdges,
        ...divergenceEdges,
        ...reverseEdges
      );
    }

    // Deduplicate edges by outcome and type (keep highest confidence)
    const uniqueEdges = new Map<string, EdgeDetectionResult>();
    for (const edge of allEdges) {
      const key = `${edge.marketType}|${edge.outcomeKey}|${edge.edgeType}`;
      const existing = uniqueEdges.get(key);
      if (!existing || edge.confidence > existing.confidence) {
        uniqueEdges.set(key, edge);
      }
    }

    return Array.from(uniqueEdges.values());
  }
}
