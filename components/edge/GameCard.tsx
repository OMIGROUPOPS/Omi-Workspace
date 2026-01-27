'use client';

import { useState } from 'react';
import Link from 'next/link';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import type { Game, ConsensusOdds, EdgeCalculation } from '@/types/edge';

function getTeamAbbrev(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 6);
  // Return last word (usually the mascot) truncated
  return words[words.length - 1].slice(0, 6);
}

// Team display component - shows logo or colored circle with initials
function TeamDisplay({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  const initials = getTeamInitials(teamName);
  const color = getTeamColor(teamName);
  const abbrev = getTeamAbbrev(teamName);
  const [imgError, setImgError] = useState(false);

  return (
    <div className="flex items-center gap-1.5 min-w-0">
      {logo && !imgError ? (
        <img src={logo} alt={teamName} className="w-5 h-5 object-contain flex-shrink-0" onError={() => setImgError(true)} />
      ) : (
        <div
          className="w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold text-white flex-shrink-0"
          style={{ backgroundColor: color }}
        >
          {initials}
        </div>
      )}
      <span className="text-[11px] text-zinc-300 truncate">{abbrev}</span>
    </div>
  );
}

interface GameCardProps {
  game: Game;
  consensus?: ConsensusOdds;
  edge?: EdgeCalculation;
}

export function GameCard({ game, consensus, edge }: GameCardProps) {
  const formatGameTime = (date: Date) => {
    return date.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
  };

  return (
    <Link
      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
      className="block bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden hover:border-zinc-700 hover:bg-zinc-900/80 transition-all"
    >
      {/* Header */}
      <div className="px-3 py-2 bg-zinc-800/50 border-b border-zinc-800 flex justify-between items-center">
        <span className="text-xs text-zinc-400">{formatGameTime(game.commenceTime)}</span>
        {edge && edge.status !== 'pass' && (
          <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
            edge.status === 'rare' ? 'bg-purple-500/20 text-purple-400' :
            edge.status === 'strong_edge' ? 'bg-emerald-500/20 text-emerald-400' :
            edge.status === 'edge' ? 'bg-blue-500/20 text-blue-400' :
            'bg-amber-500/20 text-amber-400'
          }`}>
            {edge.status === 'rare' ? '★ RARE' : edge.status === 'strong_edge' ? 'STRONG' : edge.status === 'edge' ? 'EDGE' : 'WATCH'}
          </span>
        )}
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1 border-b border-zinc-800/50">
        <span></span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">Spread</span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">ML</span>
        <span className="text-[9px] text-zinc-500 text-center uppercase">Total</span>
      </div>

      {/* Away Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.awayTeam} sportKey={game.sportKey} />

        {/* Away Spread */}
        {consensus?.spreads ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(-consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.awayPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Away ML */}
        {consensus?.h2h ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.awayPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Over */}
        {consensus?.totals ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">O{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.overPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>

      {/* Home Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.homeTeam} sportKey={game.sportKey} />

        {/* Home Spread */}
        {consensus?.spreads ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.homePrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Home ML */}
        {consensus?.h2h ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.homePrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Under */}
        {consensus?.totals ? (
          <div className="text-center py-1 px-1 rounded border bg-zinc-800/50 border-zinc-700/50">
            <div className="text-[11px] font-medium text-zinc-100">U{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.underPrice)}</div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>
    </Link>
  );
}