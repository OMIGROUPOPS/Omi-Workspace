'use client';

import Link from 'next/link';
import { formatOdds, formatSpread } from '@/lib/edge/utils/odds-math';
import type { Game, ConsensusOdds, EdgeCalculation } from '@/types/edge';

const NFL_TEAMS: Record<string, string> = {
  'Arizona Cardinals': 'ari', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'bal', 'Buffalo Bills': 'buf',
  'Carolina Panthers': 'car', 'Chicago Bears': 'chi', 'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle',
  'Dallas Cowboys': 'dal', 'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gb',
  'Houston Texans': 'hou', 'Indianapolis Colts': 'ind', 'Jacksonville Jaguars': 'jax', 'Kansas City Chiefs': 'kc',
  'Las Vegas Raiders': 'lv', 'Los Angeles Chargers': 'lac', 'Los Angeles Rams': 'lar', 'Miami Dolphins': 'mia',
  'Minnesota Vikings': 'min', 'New England Patriots': 'ne', 'New Orleans Saints': 'no', 'New York Giants': 'nyg',
  'New York Jets': 'nyj', 'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit', 'San Francisco 49ers': 'sf',
  'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tb', 'Tennessee Titans': 'ten', 'Washington Commanders': 'wsh',
};

const NBA_TEAMS: Record<string, string> = {
  'Atlanta Hawks': 'atl', 'Boston Celtics': 'bos', 'Brooklyn Nets': 'bkn', 'Charlotte Hornets': 'cha',
  'Chicago Bulls': 'chi', 'Cleveland Cavaliers': 'cle', 'Dallas Mavericks': 'dal', 'Denver Nuggets': 'den',
  'Detroit Pistons': 'det', 'Golden State Warriors': 'gs', 'Houston Rockets': 'hou', 'Indiana Pacers': 'ind',
  'LA Clippers': 'lac', 'Los Angeles Clippers': 'lac', 'Los Angeles Lakers': 'lal', 'LA Lakers': 'lal',
  'Memphis Grizzlies': 'mem', 'Miami Heat': 'mia', 'Milwaukee Bucks': 'mil', 'Minnesota Timberwolves': 'min',
  'New Orleans Pelicans': 'no', 'New York Knicks': 'ny', 'Oklahoma City Thunder': 'okc', 'Orlando Magic': 'orl',
  'Philadelphia 76ers': 'phi', 'Phoenix Suns': 'phx', 'Portland Trail Blazers': 'por', 'Sacramento Kings': 'sac',
  'San Antonio Spurs': 'sa', 'Toronto Raptors': 'tor', 'Utah Jazz': 'utah', 'Washington Wizards': 'wsh',
};

const NHL_TEAMS: Record<string, string> = {
  'Anaheim Ducks': 'ana', 'Arizona Coyotes': 'ari', 'Boston Bruins': 'bos', 'Buffalo Sabres': 'buf',
  'Calgary Flames': 'cgy', 'Carolina Hurricanes': 'car', 'Chicago Blackhawks': 'chi', 'Colorado Avalanche': 'col',
  'Columbus Blue Jackets': 'cbj', 'Dallas Stars': 'dal', 'Detroit Red Wings': 'det', 'Edmonton Oilers': 'edm',
  'Florida Panthers': 'fla', 'Los Angeles Kings': 'la', 'Minnesota Wild': 'min', 'Montreal Canadiens': 'mtl',
  'Nashville Predators': 'nsh', 'New Jersey Devils': 'nj', 'New York Islanders': 'nyi', 'New York Rangers': 'nyr',
  'Ottawa Senators': 'ott', 'Philadelphia Flyers': 'phi', 'Pittsburgh Penguins': 'pit', 'San Jose Sharks': 'sj',
  'Seattle Kraken': 'sea', 'St. Louis Blues': 'stl', 'St Louis Blues': 'stl', 'Tampa Bay Lightning': 'tb',
  'Toronto Maple Leafs': 'tor', 'Utah Hockey Club': 'utah', 'Vancouver Canucks': 'van', 'Vegas Golden Knights': 'vgk',
  'Washington Capitals': 'wsh', 'Winnipeg Jets': 'wpg',
};

const WNBA_TEAMS: Record<string, string> = {
  'Atlanta Dream': 'atl', 'Chicago Sky': 'chi', 'Connecticut Sun': 'conn', 'Dallas Wings': 'dal',
  'Indiana Fever': 'ind', 'Las Vegas Aces': 'lv', 'Los Angeles Sparks': 'la', 'Minnesota Lynx': 'min',
  'New York Liberty': 'ny', 'Phoenix Mercury': 'phx', 'Seattle Storm': 'sea', 'Washington Mystics': 'wsh',
};

// Generate a consistent color from team name for college teams
function getTeamColor(teamName: string): string {
  const colors = [
    '#1d4ed8', '#dc2626', '#059669', '#d97706', '#7c3aed', '#db2777', 
    '#0891b2', '#65a30d', '#ea580c', '#4f46e5', '#be123c', '#0d9488'
  ];
  const hash = teamName.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

function getTeamLogo(teamName: string, sportKey: string): string | null {
  // NFL
  if (sportKey.includes('americanfootball_nfl')) {
    const abbrev = NFL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbrev}.png`;
  }
  // NBA
  if (sportKey === 'basketball_nba') {
    const abbrev = NBA_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nba/500/${abbrev}.png`;
  }
  // NHL
  if (sportKey.includes('icehockey_nhl')) {
    const abbrev = NHL_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/nhl/500/${abbrev}.png`;
  }
  // WNBA
  if (sportKey === 'basketball_wnba') {
    const abbrev = WNBA_TEAMS[teamName];
    if (abbrev) return `https://a.espncdn.com/i/teamlogos/wnba/500/${abbrev}.png`;
  }
  // Return null for college/other sports - will show colored circle instead
  return null;
}

function getTeamInitials(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 2).toUpperCase();
  // For college teams like "Duke Blue Devils" or "Michigan Wolverines"
  // Usually first word is the school name
  if (words.length >= 2) {
    // Check if it's a state name like "Michigan State"
    if (words[1] === 'State' || words[1] === 'Tech') {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return words[0].slice(0, 2).toUpperCase();
  }
  return words[0].slice(0, 2).toUpperCase();
}

function getEdgeColor(delta: number): string {
  if (delta >= 0.03) return 'text-emerald-400';
  if (delta >= 0.01) return 'text-emerald-300/70';
  if (delta <= -0.03) return 'text-red-400';
  if (delta <= -0.01) return 'text-red-300/70';
  return 'text-zinc-500';
}

function getEdgeBg(delta: number): string {
  if (delta >= 0.03) return 'bg-emerald-500/10 border-emerald-500/30';
  if (delta <= -0.03) return 'bg-red-500/10 border-red-500/30';
  return 'bg-zinc-800/50 border-zinc-700/50';
}

function getMockEdge(gameId: string, offset: number): number {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0) + offset;
  const x = Math.sin(seed) * 10000;
  return (x - Math.floor(x) - 0.5) * 0.08;
}

function getTeamAbbrev(teamName: string): string {
  const words = teamName.split(' ');
  if (words.length === 1) return teamName.slice(0, 6);
  // Return last word (usually the mascot) truncated
  return words[words.length - 1].slice(0, 6);
}

function MiniSparkline({ seed, value }: { seed: string; value: number }) {
  const hashSeed = seed.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const data: number[] = [];
  let v = value;
  for (let i = 7; i >= 0; i--) {
    const x = Math.sin(hashSeed * (i + 1)) * 10000;
    const drift = (x - Math.floor(x) - 0.5) * 0.4;
    v = value + drift * ((8 - i) / 8) * 2;
    data.unshift(v);
  }
  data[data.length - 1] = value;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pathPoints = data.map((val, i) => `${(i / 7) * 24},${8 - ((val - min) / range) * 8}`).join(' ');
  const first = data[0];
  const last = data[data.length - 1];
  let color = '#71717a';
  if (last > first + 0.05) color = '#10b981';
  else if (last < first - 0.05) color = '#ef4444';
  return (
    <svg width="24" height="8" className="inline-block opacity-70">
      <polyline points={pathPoints} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Team display component - shows logo or colored circle with initials
function TeamDisplay({ teamName, sportKey }: { teamName: string; sportKey: string }) {
  const logo = getTeamLogo(teamName, sportKey);
  const initials = getTeamInitials(teamName);
  const color = getTeamColor(teamName);
  const abbrev = getTeamAbbrev(teamName);

  return (
    <div className="flex items-center gap-1.5 min-w-0">
      {logo ? (
        <img src={logo} alt={teamName} className="w-5 h-5 object-contain flex-shrink-0" />
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

const formatEdge = (delta: number) => {
  const pct = (delta * 100).toFixed(1);
  return delta > 0 ? `+${pct}%` : `${pct}%`;
};

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
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 1))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(-consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.awayPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-sp-a`} value={getMockEdge(game.id, 1)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 1))}`}>{formatEdge(getMockEdge(game.id, 1))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Away ML */}
        {consensus?.h2h ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 2))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.awayPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-ml-a`} value={getMockEdge(game.id, 2)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 2))}`}>{formatEdge(getMockEdge(game.id, 2))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Over */}
        {consensus?.totals ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 3))}`}>
            <div className="text-[11px] font-medium text-zinc-100">O{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.overPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-to-o`} value={getMockEdge(game.id, 3)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 3))}`}>{formatEdge(getMockEdge(game.id, 3))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>

      {/* Home Team Row */}
      <div className="grid grid-cols-[1fr,1fr,1fr,1fr] px-2 py-1.5 items-center gap-1">
        <TeamDisplay teamName={game.homeTeam} sportKey={game.sportKey} />

        {/* Home Spread */}
        {consensus?.spreads ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 4))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatSpread(consensus.spreads.line)}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.spreads.homePrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-sp-h`} value={getMockEdge(game.id, 4)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 4))}`}>{formatEdge(getMockEdge(game.id, 4))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Home ML */}
        {consensus?.h2h ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 5))}`}>
            <div className="text-[11px] font-medium text-zinc-100">{formatOdds(consensus.h2h.homePrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-ml-h`} value={getMockEdge(game.id, 5)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 5))}`}>{formatEdge(getMockEdge(game.id, 5))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}

        {/* Under */}
        {consensus?.totals ? (
          <div className={`text-center py-1 px-1 rounded border ${getEdgeBg(getMockEdge(game.id, 6))}`}>
            <div className="text-[11px] font-medium text-zinc-100">U{consensus.totals.line}</div>
            <div className="text-[9px] text-zinc-400">{formatOdds(consensus.totals.underPrice)}</div>
            <div className="flex items-center justify-center gap-0.5">
              <MiniSparkline seed={`${game.id}-to-u`} value={getMockEdge(game.id, 6)} />
              <span className={`text-[9px] ${getEdgeColor(getMockEdge(game.id, 6))}`}>{formatEdge(getMockEdge(game.id, 6))}</span>
            </div>
          </div>
        ) : <div className="text-center text-zinc-600 text-[10px]">-</div>}
      </div>
    </Link>
  );
}