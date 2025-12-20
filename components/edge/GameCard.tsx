'use client';

import Link from 'next/link';
import { formatOdds, formatProb, formatSpread } from '@/lib/edge/utils/odds-math';
import { EdgeDelta } from './EdgeDelta';
import { EdgeBadge } from './EdgeBadge';
import type { Game, ConsensusOdds, EdgeCalculation } from '@/types/edge';

interface GameCardProps {
  game: Game;
  consensus?: ConsensusOdds;
  edge?: EdgeCalculation;
}

export function GameCard({ game, consensus, edge }: GameCardProps) {
  const isLive = game.status === 'live';
  const hasEdge = edge && edge.status !== 'pass';

  const formatGameTime = (date: Date) => {
    const d = new Date(date);
    return d.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  return (
    <Link
      href={`/edge/portal/sports/game/${game.id}`}
      className={`
        block bg-zinc-900/50 border border-zinc-800 rounded-lg p-4
        hover:border-zinc-700 hover:bg-zinc-900/80 transition-all duration-200
        ${hasEdge ? 'ring-1 ring-emerald-500/30' : ''}
      `}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {isLive && (
            <span className="flex items-center gap-1 text-xs font-medium text-red-400">
              <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
              LIVE
            </span>
          )}
          <span className="text-xs text-zinc-500">
            {isLive ? `${game.homeScore} - ${game.awayScore}` : formatGameTime(game.commenceTime)}
          </span>
        </div>
        {hasEdge && edge && (
          <EdgeBadge status={edge.status} confidence={edge.adjustedConfidence} />
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-medium text-zinc-100">{game.awayTeam}</span>
          <div className="flex items-center gap-4 text-sm">
            {consensus?.spreads && (
              <span className="text-zinc-300 tabular-nums">
                {formatSpread(-consensus.spreads.line)}{' '}
                <span className="text-zinc-500">{formatOdds(consensus.spreads.awayPrice)}</span>
              </span>
            )}
            {consensus?.h2h && (
              <span className="text-zinc-400 tabular-nums w-16 text-right">
                {formatOdds(consensus.h2h.awayPrice)}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-medium text-zinc-100">{game.homeTeam}</span>
          <div className="flex items-center gap-4 text-sm">
            {consensus?.spreads && (
              <span className="text-zinc-300 tabular-nums">
                {formatSpread(consensus.spreads.line)}{' '}
                <span className="text-zinc-500">{formatOdds(consensus.spreads.homePrice)}</span>
              </span>
            )}
            {consensus?.h2h && (
              <span className="text-zinc-400 tabular-nums w-16 text-right">
                {formatOdds(consensus.h2h.homePrice)}
              </span>
            )}
          </div>
        </div>
      </div>

      {consensus?.totals && (
        <div className="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between text-sm">
          <span className="text-zinc-500">Total</span>
          <div className="flex items-center gap-4">
            <span className="text-zinc-300">
              O {consensus.totals.line}{' '}
              <span className="text-zinc-500">{formatOdds(consensus.totals.overPrice)}</span>
            </span>
            <span className="text-zinc-300">
              U {consensus.totals.line}{' '}
              <span className="text-zinc-500">{formatOdds(consensus.totals.underPrice)}</span>
            </span>
          </div>
        </div>
      )}

      {edge && edge.edgeDelta !== 0 && (
        <div className="mt-3 pt-3 border-t border-zinc-800">
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500">OMI Edge</span>
            <div className="flex items-center gap-3">
              <span className="text-xs text-zinc-400">Book: {formatProb(edge.bookImpliedProb)}</span>
              <span className="text-xs text-zinc-400">OMI: {formatProb(edge.omiTrueProb)}</span>
              <EdgeDelta delta={edge.edgeDelta} size="sm" />
            </div>
          </div>
        </div>
      )}
    </Link>
  );
}