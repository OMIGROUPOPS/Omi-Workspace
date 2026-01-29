'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import { getTeamLogo, getTeamColor, getTeamInitials } from '@/lib/edge/utils/team-logos';
import { getGameState, getTimeDisplay } from '@/lib/edge/utils/game-state';
import { calculateQuickEdge } from '@/lib/edge/engine/edge-calculator';

// Premium color palette
const COLORS = {
  edge: { bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', text: 'text-emerald-400' },
  strong: { bg: 'bg-emerald-500/20', border: 'border-emerald-500/40', text: 'text-emerald-300' },
  rare: { bg: 'bg-purple-500/20', border: 'border-purple-500/40', text: 'text-purple-300' },
  watch: { bg: 'bg-amber-500/15', border: 'border-amber-500/30', text: 'text-amber-400' },
  pass: { bg: 'bg-zinc-800/50', border: 'border-zinc-700/50', text: 'text-zinc-500' },
  live: { bg: 'bg-red-500/10', border: 'border-red-500/40', text: 'text-red-400' },
};

function getTeamAbbrev(teamName: string): string {
  const abbrevMap: Record<string, string> = {
    // NBA
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
    // NFL
    'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
    'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS',
  };
  return abbrevMap[teamName] || teamName.split(' ').pop()?.slice(0, 4).toUpperCase() || 'TBD';
}

interface TeamRowProps {
  teamName: string;
  sportKey: string;
  score?: number | string;
  isHome: boolean;
  spread?: { line: number; odds: number };
  ml?: number;
  total?: { line: number; odds: number; type: 'over' | 'under' };
  hasEdge?: boolean;
  edgeSide?: 'home' | 'away' | null;
}

function TeamRow({ teamName, sportKey, score, isHome, spread, ml, total, hasEdge, edgeSide }: TeamRowProps) {
  const logo = getTeamLogo(teamName, sportKey);
  const initials = getTeamInitials(teamName);
  const color = getTeamColor(teamName);
  const abbrev = getTeamAbbrev(teamName);
  const [imgError, setImgError] = useState(false);

  const isEdgeSide = hasEdge && edgeSide === (isHome ? 'home' : 'away');

  return (
    <div className={`grid grid-cols-[minmax(90px,1fr),48px,60px,60px,60px] items-center gap-1 px-3 py-2 ${
      isEdgeSide ? 'bg-emerald-500/5' : ''
    }`}>
      {/* Team */}
      <div className="flex items-center gap-2 min-w-0">
        {logo && !imgError ? (
          <img src={logo} alt={teamName} className="w-6 h-6 object-contain flex-shrink-0" onError={() => setImgError(true)} />
        ) : (
          <div className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold text-white flex-shrink-0" style={{ backgroundColor: color }}>
            {initials}
          </div>
        )}
        <span className={`text-sm font-medium truncate ${isEdgeSide ? 'text-emerald-300' : 'text-zinc-100'}`}>
          {abbrev}
        </span>
        {isEdgeSide && <span className="text-emerald-400 text-xs">←</span>}
      </div>

      {/* Score */}
      <div className="text-center">
        {score !== undefined ? (
          <span className="text-lg font-bold text-zinc-100 font-mono tabular-nums">{score}</span>
        ) : (
          <span className="text-zinc-600">-</span>
        )}
      </div>

      {/* Spread */}
      <div className={`text-center py-1.5 rounded ${isEdgeSide && spread ? 'bg-emerald-500/20 border border-emerald-500/30' : 'bg-zinc-800/60'}`}>
        {spread ? (
          <>
            <div className="text-xs font-semibold text-zinc-100 font-mono">{formatSpread(spread.line)}</div>
            <div className="text-[10px] text-zinc-400 font-mono">{formatOdds(spread.odds)}</div>
          </>
        ) : <span className="text-zinc-600 text-xs">-</span>}
      </div>

      {/* ML */}
      <div className="text-center py-1.5 rounded bg-zinc-800/60">
        {ml !== undefined ? (
          <div className="text-xs font-semibold text-zinc-100 font-mono">{formatOdds(ml)}</div>
        ) : <span className="text-zinc-600 text-xs">-</span>}
      </div>

      {/* Total */}
      <div className="text-center py-1.5 rounded bg-zinc-800/60">
        {total ? (
          <>
            <div className="text-xs font-semibold text-zinc-100 font-mono">{total.type === 'over' ? 'O' : 'U'}{total.line}</div>
            <div className="text-[10px] text-zinc-400 font-mono">{formatOdds(total.odds)}</div>
          </>
        ) : <span className="text-zinc-600 text-xs">-</span>}
      </div>
    </div>
  );
}

export interface GameCardGame {
  id: string;
  homeTeam: string;
  awayTeam: string;
  sportKey: string;
  commenceTime: string | Date;
}

export interface GameCardConsensus {
  spreads?: { line: number; homePrice: number; awayPrice: number };
  h2h?: { homePrice: number; awayPrice: number };
  totals?: { line: number; overPrice: number; underPrice: number };
}

export interface GameCardScore {
  home: number | string;
  away: number | string;
  period?: string;
  clock?: string;
  completed?: boolean;
}

export interface GameCardEdge {
  score: number;
  confidence: 'PASS' | 'WATCH' | 'EDGE' | 'STRONG' | 'RARE';
  side: 'home' | 'away' | null;
  reason?: string;
}

interface GameCardProps {
  game: GameCardGame;
  consensus?: GameCardConsensus;
  score?: GameCardScore;
  edge?: GameCardEdge;
  openingSpread?: number;
}

export function GameCard({ game, consensus, score, edge, openingSpread }: GameCardProps) {
  const commenceTime = typeof game.commenceTime === 'string' ? new Date(game.commenceTime) : game.commenceTime;
  const gameState = getGameState(commenceTime, game.sportKey);
  const isLive = gameState === 'live';
  const isFinal = gameState === 'final' || score?.completed;

  // Calculate edge if not provided
  const calculatedEdge = edge || calculateQuickEdge(
    openingSpread,
    consensus?.spreads?.line,
    consensus?.spreads?.homePrice,
    consensus?.spreads?.awayPrice
  );

  const edgeColor = calculatedEdge.confidence === 'RARE' ? COLORS.rare :
                    calculatedEdge.confidence === 'STRONG' ? COLORS.strong :
                    calculatedEdge.confidence === 'EDGE' ? COLORS.edge :
                    calculatedEdge.confidence === 'WATCH' ? COLORS.watch : COLORS.pass;

  return (
    <Link
      href={`/edge/portal/sports/game/${game.id}?sport=${game.sportKey}`}
      className={`block rounded-lg overflow-hidden transition-all duration-200 hover:scale-[1.01] hover:shadow-lg ${
        isLive
          ? 'bg-gradient-to-b from-zinc-900 to-zinc-900/95 border border-red-500/40 shadow-red-500/10 shadow-md'
          : 'bg-zinc-900 border border-zinc-800 hover:border-zinc-700'
      }`}
    >
      {/* Header */}
      <div className="px-3 py-2 bg-zinc-800/40 border-b border-zinc-800/80 flex justify-between items-center">
        <div className="flex items-center gap-2">
          {isLive ? (
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 text-xs font-semibold text-red-400 bg-red-500/20 px-2 py-0.5 rounded-full">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                </span>
                LIVE
              </span>
              {score?.period && (
                <span className="text-xs text-zinc-400 font-mono">
                  {score.period} {score.clock && `${score.clock}`}
                </span>
              )}
            </div>
          ) : isFinal ? (
            <span className="text-xs font-semibold text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded-full">FINAL</span>
          ) : (
            <span className="text-xs text-zinc-400 font-medium">{getTimeDisplay(commenceTime, game.sportKey)}</span>
          )}
        </div>

        {/* Edge Badge */}
        {calculatedEdge.confidence !== 'PASS' && (
          <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full ${edgeColor.bg} border ${edgeColor.border}`}>
            <span className={`text-xs font-bold ${edgeColor.text}`}>
              {calculatedEdge.confidence === 'RARE' && '★ '}{calculatedEdge.confidence}
            </span>
            <span className={`text-xs font-mono ${edgeColor.text}`}>{calculatedEdge.score}%</span>
          </div>
        )}
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-[minmax(90px,1fr),48px,60px,60px,60px] items-center gap-1 px-3 py-1 bg-zinc-900/50">
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider">Team</span>
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider text-center">Score</span>
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider text-center">Spread</span>
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider text-center">ML</span>
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider text-center">O/U</span>
      </div>

      {/* Away Team Row */}
      <TeamRow
        teamName={game.awayTeam}
        sportKey={game.sportKey}
        score={(isLive || isFinal) ? score?.away : undefined}
        isHome={false}
        spread={consensus?.spreads ? { line: -consensus.spreads.line, odds: consensus.spreads.awayPrice } : undefined}
        ml={consensus?.h2h?.awayPrice}
        total={consensus?.totals ? { line: consensus.totals.line, odds: consensus.totals.overPrice, type: 'over' } : undefined}
        hasEdge={calculatedEdge.confidence !== 'PASS'}
        edgeSide={calculatedEdge.side}
      />

      {/* Divider */}
      <div className="h-px bg-zinc-800/50 mx-3" />

      {/* Home Team Row */}
      <TeamRow
        teamName={game.homeTeam}
        sportKey={game.sportKey}
        score={(isLive || isFinal) ? score?.home : undefined}
        isHome={true}
        spread={consensus?.spreads ? { line: consensus.spreads.line, odds: consensus.spreads.homePrice } : undefined}
        ml={consensus?.h2h?.homePrice}
        total={consensus?.totals ? { line: consensus.totals.line, odds: consensus.totals.underPrice, type: 'under' } : undefined}
        hasEdge={calculatedEdge.confidence !== 'PASS'}
        edgeSide={calculatedEdge.side}
      />

      {/* Edge Reason Footer (if edge exists) */}
      {calculatedEdge.confidence !== 'PASS' && edge?.reason && (
        <div className="px-3 py-1.5 bg-zinc-800/30 border-t border-zinc-800/50">
          <p className="text-[10px] text-zinc-500 truncate">
            <span className="text-emerald-500">Edge:</span> {edge.reason}
          </p>
        </div>
      )}
    </Link>
  );
}

// Legacy export for compatibility
export default GameCard;
