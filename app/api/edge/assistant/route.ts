import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// American odds → implied probability
function toProb(odds: number): number {
  return odds < 0 ? Math.abs(odds) / (Math.abs(odds) + 100) : 100 / (odds + 100);
}

// Format American odds with sign
function fmtOdds(odds: number | null | undefined): string {
  if (odds == null) return '--';
  return odds > 0 ? `+${odds}` : `${odds}`;
}

// Format spread with sign
function fmtSpread(line: number | null | undefined): string {
  if (line == null) return '--';
  return line > 0 ? `+${line}` : `${line}`;
}

// Parse game_id from client-sent gameContext string
function parseGameId(gameContext: string): string | null {
  const match = gameContext.match(/Game ID:\s*(\S+)/);
  return match ? match[1] : null;
}

// Parse selected book from client-sent gameContext
function parseSelectedBook(gameContext: string): string {
  const match = gameContext.match(/Selected Book:\s*(\S+)/);
  return match ? match[1] : 'fanduel';
}

// Parse active market/period from client-sent gameContext
function parseViewContext(gameContext: string): { activeMarket: string; activePeriod: string } {
  const marketMatch = gameContext.match(/Active Market:\s*(\S+)/);
  const periodMatch = gameContext.match(/Period:\s*(\S+)/);
  return {
    activeMarket: marketMatch ? marketMatch[1] : 'spread',
    activePeriod: periodMatch ? periodMatch[1] : 'full',
  };
}

// Parse pillar scores from client-sent gameContext (these aren't stored in Supabase)
function parsePillarScores(gameContext: string): {
  composite: number | null;
  execution: number | null;
  incentives: number | null;
  shocks: number | null;
  timeDecay: number | null;
  flow: number | null;
  gameEnvironment: number | null;
} | null {
  const compositeMatch = gameContext.match(/Composite:\s*(\d+)/);
  if (!compositeMatch) return null;

  const execMatch = gameContext.match(/Execution:\s*(\d+)/);
  const incMatch = gameContext.match(/Incentives:\s*(\d+)/);
  const shockMatch = gameContext.match(/Shocks:\s*(\d+)/);
  const tdMatch = gameContext.match(/Time Decay:\s*(\d+)/);
  const flowMatch = gameContext.match(/Flow:\s*(\d+)/);
  const geMatch = gameContext.match(/Game Environment:\s*(\d+)/);

  return {
    composite: parseInt(compositeMatch[1]),
    execution: execMatch ? parseInt(execMatch[1]) : null,
    incentives: incMatch ? parseInt(incMatch[1]) : null,
    shocks: shockMatch ? parseInt(shockMatch[1]) : null,
    timeDecay: tdMatch ? parseInt(tdMatch[1]) : null,
    flow: flowMatch ? parseInt(flowMatch[1]) : null,
    gameEnvironment: geMatch ? parseInt(geMatch[1]) : null,
  };
}

// Edge tier classification
function getEdgeTier(edgePct: number): string {
  const abs = Math.abs(edgePct);
  if (abs < 1) return 'NO EDGE';
  if (abs < 3) return 'LOW';
  if (abs < 5) return 'MID';
  if (abs < 8) return 'HIGH';
  return 'MAX EDGE';
}

// Spread-to-probability rate by sport
const SPREAD_TO_PROB_RATE: Record<string, number> = {
  'americanfootball_nfl': 0.027,
  'americanfootball_ncaaf': 0.027,
  'basketball_nba': 0.033,
  'basketball_ncaab': 0.033,
  'basketball_wnba': 0.033,
  'icehockey_nhl': 0.05,
  'baseball_mlb': 0.04,
  'soccer_epl': 0.04,
  'soccer_usa_mls': 0.04,
};

// Build the full game context from Supabase data
async function buildGameContext(gameId: string, clientContext: string): Promise<string> {
  const supabase = getSupabase();
  const selectedBook = parseSelectedBook(clientContext);
  const { activeMarket, activePeriod } = parseViewContext(clientContext);
  const pillarScores = parsePillarScores(clientContext);

  // Query all data in parallel
  const [
    cachedOddsResult,
    compositeResult,
    snapshotsResult,
    exchangeResult,
    gradesResult,
  ] = await Promise.all([
    // 1. cached_odds → game data with teams, bookmakers
    supabase
      .from('cached_odds')
      .select('game_id, sport_key, game_data, updated_at')
      .eq('game_id', gameId)
      .limit(1)
      .single(),

    // 2. composite_history → latest fair lines, per-market composites
    supabase
      .from('composite_history')
      .select('*')
      .eq('game_id', gameId)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single(),

    // 3. odds_snapshots → line movement (last 48h to keep manageable)
    supabase
      .from('odds_snapshots')
      .select('market, book_key, outcome_type, line, odds, snapshot_time')
      .eq('game_id', gameId)
      .gte('snapshot_time', new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString())
      .order('snapshot_time', { ascending: true })
      .limit(500),

    // 4. exchange_data → Kalshi/Polymarket
    supabase
      .from('exchange_data')
      .select('exchange, event_title, contract_ticker, market_type, subtitle, yes_price, no_price, volume, open_interest, snapshot_time')
      .eq('mapped_game_id', gameId)
      .order('snapshot_time', { ascending: false })
      .limit(20),

    // 5. prediction_grades → historical accuracy
    supabase
      .from('prediction_grades')
      .select('market_type, period, omi_fair_line, book_line, gap, signal, prediction_side, actual_result, is_correct, pillar_composite, graded_at')
      .eq('game_id', gameId),
  ]);

  const game = cachedOddsResult.data?.game_data;
  const sportKey = cachedOddsResult.data?.sport_key || '';
  const composite = compositeResult.data;
  const snapshots = snapshotsResult.data || [];
  const exchangeRows = exchangeResult.data || [];
  const grades = gradesResult.data || [];

  if (!game) {
    // Fallback: return client context if no Supabase data found
    return clientContext;
  }

  const homeTeam = game.home_team || 'Home';
  const awayTeam = game.away_team || 'Away';
  const commenceTime = game.commence_time || '';

  // Fetch team_stats for both teams
  const [homeStatsResult, awayStatsResult] = await Promise.all([
    supabase
      .from('team_stats')
      .select('*')
      .ilike('team_name', `%${homeTeam.split(' ').pop()}%`)
      .order('updated_at', { ascending: false })
      .limit(3),
    supabase
      .from('team_stats')
      .select('*')
      .ilike('team_name', `%${awayTeam.split(' ').pop()}%`)
      .order('updated_at', { ascending: false })
      .limit(3),
  ]);

  // Best match: prefer exact name, then partial
  const findBestMatch = (results: any[], teamName: string) => {
    if (!results || results.length === 0) return null;
    const exact = results.find((r: any) => r.team_name?.toLowerCase() === teamName.toLowerCase());
    if (exact) return exact;
    return results[0];
  };

  const homeStats = findBestMatch(homeStatsResult.data || [], homeTeam);
  const awayStats = findBestMatch(awayStatsResult.data || [], awayTeam);

  // Build consensus from bookmakers
  const bookmakers = game.bookmakers || [];
  const median = (arr: number[]) => {
    if (arr.length === 0) return undefined;
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  };

  const h2hHome: number[] = [], h2hAway: number[] = [], h2hDraw: number[] = [];
  const spreadLines: number[] = [], spreadHomeP: number[] = [], spreadAwayP: number[] = [];
  const totalLines: number[] = [], overP: number[] = [], underP: number[] = [];

  // Per-book data for comparison table
  const bookData: Record<string, { spread?: number; spreadHP?: number; spreadAP?: number; mlH?: number; mlA?: number; total?: number; overP?: number; underP?: number }> = {};

  for (const bk of bookmakers) {
    const bd: any = {};
    for (const market of bk.markets || []) {
      if (market.key === 'h2h') {
        const home = market.outcomes?.find((o: any) => o.name === homeTeam);
        const away = market.outcomes?.find((o: any) => o.name === awayTeam);
        const draw = market.outcomes?.find((o: any) => o.name === 'Draw');
        if (home?.price) { h2hHome.push(home.price); bd.mlH = home.price; }
        if (away?.price) { h2hAway.push(away.price); bd.mlA = away.price; }
        if (draw?.price) h2hDraw.push(draw.price);
      }
      if (market.key === 'spreads') {
        const home = market.outcomes?.find((o: any) => o.name === homeTeam);
        const away = market.outcomes?.find((o: any) => o.name === awayTeam);
        if (home?.point !== undefined) {
          spreadLines.push(home.point);
          bd.spread = home.point;
          if (home.price) { spreadHomeP.push(home.price); bd.spreadHP = home.price; }
        }
        if (away?.price) { spreadAwayP.push(away.price); bd.spreadAP = away.price; }
      }
      if (market.key === 'totals') {
        const over = market.outcomes?.find((o: any) => o.name === 'Over');
        const under = market.outcomes?.find((o: any) => o.name === 'Under');
        if (over?.point !== undefined) {
          totalLines.push(over.point);
          bd.total = over.point;
          if (over.price) { overP.push(over.price); bd.overP = over.price; }
        }
        if (under?.price) { underP.push(under.price); bd.underP = under.price; }
      }
    }
    bookData[bk.key] = bd;
  }

  const consSpread = median(spreadLines);
  const consTotal = median(totalLines);
  const consMLHome = median(h2hHome);
  const consMLAway = median(h2hAway);

  // Fair lines from composite_history
  const fairSpread = composite?.fair_spread != null ? Number(composite.fair_spread) : null;
  const fairTotal = composite?.fair_total != null ? Number(composite.fair_total) : null;
  const fairMLHome = composite?.fair_ml_home != null ? Number(composite.fair_ml_home) : null;
  const fairMLAway = composite?.fair_ml_away != null ? Number(composite.fair_ml_away) : null;
  const compSpread = composite?.composite_spread != null ? Number(composite.composite_spread) : null;
  const compTotal = composite?.composite_total != null ? Number(composite.composite_total) : null;
  const compML = composite?.composite_ml != null ? Number(composite.composite_ml) : null;

  // Build the structured context
  const lines: string[] = [];

  // === GAME HEADER ===
  lines.push(`GAME: ${awayTeam} @ ${homeTeam}`);
  lines.push(`Sport: ${sportKey} | Date: ${commenceTime ? new Date(commenceTime).toLocaleString() : 'TBD'}`);
  lines.push(`Game ID: ${gameId}`);
  lines.push(`User is viewing: ${activeMarket} / ${activePeriod} | Selected book: ${selectedBook}`);
  lines.push('');

  // === TEAMS ===
  lines.push('=== TEAMS ===');
  lines.push(`HOME: ${homeTeam}`);
  if (homeStats) {
    const w = homeStats.wins ?? '?', l = homeStats.losses ?? '?';
    const wp = homeStats.win_pct != null ? `${(homeStats.win_pct * 100).toFixed(0)}%` : '?';
    const streak = homeStats.streak != null ? (homeStats.streak > 0 ? `W${homeStats.streak}` : `L${Math.abs(homeStats.streak)}`) : '?';
    lines.push(`  Record: ${w}-${l} (${wp}) | Streak: ${streak}`);
    lines.push(`  PPG: ${homeStats.points_per_game ?? '?'} | PAPG: ${homeStats.points_allowed_per_game ?? '?'} | Pace: ${homeStats.pace ?? '?'}`);
    lines.push(`  Off Rtg: ${homeStats.offensive_rating ?? '?'} | Def Rtg: ${homeStats.defensive_rating ?? '?'} | Net: ${homeStats.net_rating ?? '?'}`);
    if (homeStats.injuries && homeStats.injuries.length > 0) {
      const injList = homeStats.injuries.slice(0, 5).map((inj: any) => typeof inj === 'string' ? inj : `${inj.name} (${inj.status})`).join(', ');
      lines.push(`  Injuries: ${injList}`);
    }
  } else {
    lines.push('  (No stats available)');
  }

  lines.push(`AWAY: ${awayTeam}`);
  if (awayStats) {
    const w = awayStats.wins ?? '?', l = awayStats.losses ?? '?';
    const wp = awayStats.win_pct != null ? `${(awayStats.win_pct * 100).toFixed(0)}%` : '?';
    const streak = awayStats.streak != null ? (awayStats.streak > 0 ? `W${awayStats.streak}` : `L${Math.abs(awayStats.streak)}`) : '?';
    lines.push(`  Record: ${w}-${l} (${wp}) | Streak: ${streak}`);
    lines.push(`  PPG: ${awayStats.points_per_game ?? '?'} | PAPG: ${awayStats.points_allowed_per_game ?? '?'} | Pace: ${awayStats.pace ?? '?'}`);
    lines.push(`  Off Rtg: ${awayStats.offensive_rating ?? '?'} | Def Rtg: ${awayStats.defensive_rating ?? '?'} | Net: ${awayStats.net_rating ?? '?'}`);
    if (awayStats.injuries && awayStats.injuries.length > 0) {
      const injList = awayStats.injuries.slice(0, 5).map((inj: any) => typeof inj === 'string' ? inj : `${inj.name} (${inj.status})`).join(', ');
      lines.push(`  Injuries: ${injList}`);
    }
  } else {
    lines.push('  (No stats available)');
  }
  lines.push('');

  // === BOOK LINES (selected book) ===
  const selBook = bookData[selectedBook];
  lines.push(`=== BOOK LINES (${selectedBook.toUpperCase()}) ===`);
  if (selBook) {
    if (selBook.spread !== undefined) {
      const homeSpread = selBook.spread;
      const awaySpread = -homeSpread;
      const homeFav = homeSpread < 0;
      lines.push(`Spread: ${homeTeam} ${fmtSpread(homeSpread)} (${fmtOdds(selBook.spreadHP)}) ${homeFav ? '[FAVORITE, giving points]' : '[UNDERDOG, getting points]'}`);
      lines.push(`        ${awayTeam} ${fmtSpread(awaySpread)} (${fmtOdds(selBook.spreadAP)}) ${!homeFav ? '[FAVORITE, giving points]' : '[UNDERDOG, getting points]'}`);
    }
    if (selBook.mlH !== undefined) {
      lines.push(`Moneyline: ${homeTeam} ${fmtOdds(selBook.mlH)} / ${awayTeam} ${fmtOdds(selBook.mlA)}`);
    }
    if (selBook.total !== undefined) {
      lines.push(`Total: O${selBook.total} (${fmtOdds(selBook.overP)}) / U${selBook.total} (${fmtOdds(selBook.underP)})`);
    }
  } else {
    lines.push('(No lines available for this book)');
  }
  lines.push('');

  // === ALL BOOKS COMPARISON ===
  const bookNames: Record<string, string> = {
    fanduel: 'FanDuel', draftkings: 'DraftKings', betmgm: 'BetMGM', caesars: 'Caesars',
    pointsbet: 'PointsBet', betrivers: 'BetRivers', unibet: 'Unibet', wynnbet: 'WynnBet',
    bovada: 'Bovada', betonlineag: 'BetOnline', mybookieag: 'MyBookie', lowvig: 'LowVig',
    williamhill_us: 'WilliamHill', superbook: 'SuperBook', twinspires: 'TwinSpires',
    betus: 'BetUS', espnbet: 'ESPN BET', fliff: 'Fliff', hardrockbet: 'HardRock',
    fanatics: 'Fanatics', bet365: 'Bet365',
  };

  if (Object.keys(bookData).length > 1) {
    lines.push('=== ALL BOOKS COMPARISON ===');
    for (const [key, bd] of Object.entries(bookData)) {
      const name = bookNames[key] || key;
      const parts: string[] = [name.padEnd(14)];
      if (bd.spread !== undefined) parts.push(`Sprd: ${fmtSpread(bd.spread)}(${fmtOdds(bd.spreadHP)})`);
      if (bd.mlH !== undefined) parts.push(`ML: ${fmtOdds(bd.mlH)}/${fmtOdds(bd.mlA)}`);
      if (bd.total !== undefined) parts.push(`Tot: ${bd.total}(${fmtOdds(bd.overP)}/${fmtOdds(bd.underP)})`);
      lines.push(`  ${parts.join(' | ')}`);
    }
    lines.push('');
  }

  // === CONSENSUS ===
  lines.push('=== MARKET CONSENSUS (median across all books) ===');
  if (consSpread !== undefined) {
    lines.push(`Spread: ${homeTeam} ${fmtSpread(consSpread)} / ${awayTeam} ${fmtSpread(-consSpread)}`);
  }
  if (consMLHome !== undefined) {
    lines.push(`ML: ${homeTeam} ${fmtOdds(consMLHome)} / ${awayTeam} ${fmtOdds(consMLAway)}`);
  }
  if (consTotal !== undefined) {
    lines.push(`Total: ${consTotal}`);
  }
  lines.push('');

  // === OMI FAIR LINES ===
  lines.push('=== OMI FAIR LINES ===');
  if (fairSpread != null) {
    const homeFav = fairSpread < 0;
    lines.push(`Fair Spread: ${homeTeam} ${fmtSpread(fairSpread)} / ${awayTeam} ${fmtSpread(-fairSpread)}`);
    lines.push(`  → ${homeFav ? homeTeam : awayTeam} is favored by ${Math.abs(fairSpread).toFixed(1)} points according to OMI`);
  }
  if (fairTotal != null) {
    lines.push(`Fair Total: ${fairTotal.toFixed(1)}`);
  }
  if (fairMLHome != null && fairMLAway != null) {
    lines.push(`Fair ML: ${homeTeam} ${fmtOdds(fairMLHome)} / ${awayTeam} ${fmtOdds(fairMLAway)}`);
    const hp = toProb(fairMLHome);
    const ap = toProb(fairMLAway);
    lines.push(`Fair Win Prob: ${homeTeam} ${(hp * 100).toFixed(1)}% / ${awayTeam} ${(ap * 100).toFixed(1)}%`);
  }
  lines.push('');

  // === EDGES ===
  lines.push('=== EDGES ===');
  const rate = SPREAD_TO_PROB_RATE[sportKey] || 0.03;
  let bestEdgePct = 0;
  let bestEdgeMarket = '';

  if (fairSpread != null && consSpread !== undefined) {
    const gap = consSpread - fairSpread;
    const edgePct = Math.abs(gap) * rate * 100;
    const edgeTeam = gap > 0 ? awayTeam : homeTeam;
    const edgeTeamSpread = gap > 0 ? fmtSpread(-consSpread) : fmtSpread(consSpread);
    lines.push(`Spread Edge: ${edgePct.toFixed(1)}% favoring ${edgeTeam} ${edgeTeamSpread}`);
    lines.push(`  → BET: ${edgeTeam} ${edgeTeamSpread} | OMI fair: ${homeTeam} ${fmtSpread(fairSpread)} | Book: ${homeTeam} ${fmtSpread(consSpread)} | Gap: ${Math.abs(gap).toFixed(1)} pts`);
    if (edgePct > bestEdgePct) { bestEdgePct = edgePct; bestEdgeMarket = 'Spread'; }
  }

  if (fairMLHome != null && fairMLAway != null && consMLHome !== undefined && consMLAway !== undefined) {
    const fairHP = toProb(fairMLHome);
    const fairAP = toProb(fairMLAway);
    const bookHP = toProb(consMLHome);
    const bookAP = toProb(consMLAway);
    const normBHP = bookHP / (bookHP + bookAP);
    const normBAP = bookAP / (bookHP + bookAP);
    const homeEdge = (fairHP - normBHP) * 100;
    const awayEdge = (fairAP - normBAP) * 100;
    const biggerEdge = Math.abs(homeEdge) > Math.abs(awayEdge) ? homeEdge : awayEdge;
    const mlEdgeTeam = Math.abs(homeEdge) > Math.abs(awayEdge) ? homeTeam : awayTeam;
    const mlEdgeTeamFairProb = Math.abs(homeEdge) > Math.abs(awayEdge) ? (fairHP * 100).toFixed(1) : (fairAP * 100).toFixed(1);
    const mlEdgeTeamBookProb = Math.abs(homeEdge) > Math.abs(awayEdge) ? (normBHP * 100).toFixed(1) : (normBAP * 100).toFixed(1);
    lines.push(`ML Edge: ${Math.abs(biggerEdge).toFixed(1)}% favoring ${mlEdgeTeam}`);
    lines.push(`  → BET: ${mlEdgeTeam} ML | OMI fair prob: ${mlEdgeTeamFairProb}% | Book implied: ${mlEdgeTeamBookProb}%`);
    if (Math.abs(biggerEdge) > bestEdgePct) { bestEdgePct = Math.abs(biggerEdge); bestEdgeMarket = 'ML'; }
  }

  if (fairTotal != null && consTotal !== undefined) {
    const gap = fairTotal - consTotal;
    const totalRate = rate * 0.5; // Totals are higher-variance
    const edgePct = Math.abs(gap) * totalRate * 100;
    const direction = gap > 0 ? 'Over' : 'Under';
    lines.push(`Total Edge: ${edgePct.toFixed(1)}% favoring ${direction}`);
    lines.push(`  → BET: ${direction} ${consTotal} | OMI fair total: ${fairTotal.toFixed(1)} | Book total: ${consTotal}`);
    if (edgePct > bestEdgePct) { bestEdgePct = edgePct; bestEdgeMarket = 'Total'; }
  }

  lines.push(`Best Edge: ${bestEdgePct.toFixed(1)}% on ${bestEdgeMarket || 'N/A'} → Tier: ${getEdgeTier(bestEdgePct)}`);
  lines.push('');

  // === 6-PILLAR ANALYSIS ===
  if (pillarScores) {
    lines.push(`=== 6-PILLAR ANALYSIS (composite: ${pillarScores.composite}/100) ===`);
    if (pillarScores.execution != null)
      lines.push(`EXEC (20%): ${pillarScores.execution}/100 — Team performance trends, recent form`);
    if (pillarScores.incentives != null)
      lines.push(`INCV (10%): ${pillarScores.incentives}/100 — Motivation, rest, schedule factors`);
    if (pillarScores.shocks != null)
      lines.push(`SHOK (25%): ${pillarScores.shocks}/100 — Injuries, weather, unexpected events`);
    if (pillarScores.timeDecay != null)
      lines.push(`TIME (10%): ${pillarScores.timeDecay}/100 — Line staleness, time since opening`);
    if (pillarScores.flow != null)
      lines.push(`FLOW (25%): ${pillarScores.flow}/100 — Sharp vs public money signals`);
    if (pillarScores.gameEnvironment != null)
      lines.push(`ENV  (10%): ${pillarScores.gameEnvironment}/100 — Pace, venue, matchup dynamics`);
    lines.push('');
  }

  // === PER-MARKET COMPOSITES ===
  if (compSpread != null || compTotal != null || compML != null) {
    lines.push('=== PER-MARKET COMPOSITES ===');
    if (compSpread != null) lines.push(`Spread: ${Number(compSpread).toFixed(0)}/100`);
    if (compTotal != null) lines.push(`Total: ${Number(compTotal).toFixed(0)}/100`);
    if (compML != null) lines.push(`ML: ${Number(compML).toFixed(0)}/100`);
    lines.push('');
  }

  // === LINE MOVEMENT ===
  if (snapshots.length > 0) {
    lines.push('=== LINE MOVEMENT ===');
    // Group by market
    const byMarket: Record<string, typeof snapshots> = {};
    for (const s of snapshots) {
      const key = s.market || 'unknown';
      if (!byMarket[key]) byMarket[key] = [];
      byMarket[key].push(s);
    }

    for (const [market, rows] of Object.entries(byMarket)) {
      if (rows.length === 0) continue;
      const first = rows[0];
      const last = rows[rows.length - 1];
      const openLine = first.line;
      const currentLine = last.line;
      const movement = openLine != null && currentLine != null ? currentLine - openLine : null;

      lines.push(`${market.toUpperCase()}: Open ${openLine ?? '?'} → Current ${currentLine ?? '?'}${movement != null ? ` (moved ${movement > 0 ? '+' : ''}${movement.toFixed(1)})` : ''}`);

      // Show significant moves (line changes > 0.5 pts)
      const moves: string[] = [];
      let prevLine = openLine;
      for (const s of rows) {
        if (prevLine != null && s.line != null && Math.abs(s.line - prevLine) >= 0.5) {
          const ts = new Date(s.snapshot_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
          moves.push(`${ts}: ${prevLine}→${s.line} (${s.book_key || '?'})`);
        }
        prevLine = s.line;
      }
      if (moves.length > 0) {
        lines.push(`  Key moves: ${moves.slice(0, 8).join(', ')}`);
      }
    }
    lines.push('');
  }

  // === EXCHANGE SIGNALS ===
  if (exchangeRows.length > 0) {
    lines.push('=== EXCHANGE SIGNALS ===');
    // Deduplicate by (exchange, contract_ticker) — keep latest
    const seen = new Set<string>();
    for (const row of exchangeRows) {
      const key = `${row.exchange}:${row.contract_ticker || row.subtitle}`;
      if (seen.has(key)) continue;
      seen.add(key);
      const prob = row.yes_price != null ? `${row.yes_price}¢ (${row.yes_price}% implied)` : '?';
      lines.push(`${row.exchange.toUpperCase()}: ${row.subtitle || row.event_title} → ${prob}${row.volume ? ` | Vol: ${row.volume}` : ''}`);
    }
    lines.push('');
  }

  // === PREDICTION GRADES (if game was graded) ===
  if (grades.length > 0) {
    lines.push('=== PREDICTION GRADES (historical accuracy) ===');
    for (const g of grades) {
      const correct = g.is_correct === true ? 'CORRECT' : g.is_correct === false ? 'INCORRECT' : 'PUSH';
      lines.push(`${g.market_type} ${g.period}: ${g.signal} (${g.prediction_side}) → ${g.actual_result} [${correct}] | Gap: ${g.gap?.toFixed(1)} | Composite: ${g.pillar_composite}`);
    }
    lines.push('');
  }

  // === EDGE TIERS REFERENCE ===
  lines.push('=== EDGE TIER SCALE ===');
  lines.push('< 1%: NO EDGE | 1-3%: LOW | 3-5%: MID | 5-8%: HIGH | 8%+: MAX EDGE');
  lines.push(`This game: ${getEdgeTier(bestEdgePct)} on ${bestEdgeMarket || 'N/A'} (${bestEdgePct.toFixed(1)}%)`);

  return lines.join('\n');
}

const BASE_SYSTEM_PROMPT = `You are OMI Edge's AI analyst. You have comprehensive game data provided below. Use ONLY this data to answer questions. Be specific with numbers.

TEAM/SPREAD IDENTIFICATION:
- NEGATIVE spread = FAVORITE (giving points). POSITIVE spread = UNDERDOG (getting points).
- NEVER say a favorite is "getting points" or an underdog is "giving points."
- The EDGES section in the data below already tells you which team/side has the edge and by how much. Trust it.

EDGE EXPLANATION RULES — follow this exact logic:

SPREADS:
- The edge is on the team named in the "favoring [TEAM]" part of the Spread Edge line.
- Use this template: "The edge is on [TEAM] [THEIR SPREAD] because OMI's fair line is [FAIR] but the book offers [BOOK], giving you [GAP] extra points of value."
- Do NOT explain both sides. Just state which team has the edge and why in 2-3 sentences max.

TOTALS:
- Use this template: "The edge is on the [OVER/UNDER] because OMI's fair total is [FAIR] but the book line is [BOOK]."

MONEYLINE:
- Use this template: "The edge is on [TEAM] ML because OMI gives them a [FAIR_PROB]% win probability but the book implies only [BOOK_PROB]%."

GENERAL RESPONSE RULES:
- Lead with the edge. Never start with "there's a discrepancy" or "looking at the data" or "based on the analysis." Be direct.
- State the bet first, then the reason. "The edge is on X because Y."
- Reference specific pillar scores ONLY when the user asks "why" or "which pillar drives this."
- Keep answers under 150 words unless the user explicitly asks for detail.
- If asked about something NOT in the data below, say so honestly rather than guessing.
- Never recommend specific bet amounts — explain what the data shows and let the user decide.
- When the user asks a general "what do you think" or "what's the play" question, lead with the highest-edge market.

CONVERSATIONAL RULES:
- When the user asks "why do you like the spread" or similar casual questions, treat it as "explain the spread edge." If the EDGES section shows an edge, explain it. Don't say "I don't have an edge."
- The EDGE PERCENTAGE is what matters, not the per-market composite score. If edge >= 3%, there IS an edge worth discussing. Say so confidently.
- Match the user's energy. Casual question = casual answer. Don't lecture about confidence scores unless asked.
- If the data shows a +9.0% edge on a team and the user asks about it, EXPLAIN that edge. Never deny it exists.
- You are OMI's analyst. Own the analysis. Say "we like NOR +2.5 because..." not "the data shows a discrepancy..."
- Never contradict what the user sees on screen. If they see a green edge number, acknowledge it and explain it.`;

export async function POST(request: NextRequest) {
  if (!ANTHROPIC_API_KEY) {
    return NextResponse.json(
      { error: 'ANTHROPIC_API_KEY not configured' },
      { status: 500 }
    );
  }

  try {
    const { messages, gameContext } = await request.json();

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json({ error: 'Messages required' }, { status: 400 });
    }

    // Parse game_id from client-sent context
    const gameId = gameContext ? parseGameId(gameContext) : null;

    // Build full context from Supabase (or fall back to client context)
    let fullContext: string;
    if (gameId) {
      try {
        fullContext = await buildGameContext(gameId, gameContext || '');
      } catch (e) {
        console.error('[EdgeAI] Supabase context build failed, using client context:', e);
        fullContext = gameContext || '';
      }
    } else {
      fullContext = gameContext || '';
    }

    const systemPrompt = `${BASE_SYSTEM_PROMPT}\n\n--- GAME DATA ---\n${fullContext}`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: systemPrompt,
        messages: messages.map((msg: { role: string; content: string }) => ({
          role: msg.role,
          content: msg.content,
        })),
        stream: true,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('[EdgeAI] Anthropic API error:', response.status, errText);
      return NextResponse.json(
        { error: `API error: ${response.status}` },
        { status: response.status }
      );
    }

    // Stream the response through
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.type === 'content_block_delta' && parsed.delta?.text) {
                    controller.enqueue(new TextEncoder().encode(parsed.delta.text));
                  }
                } catch {
                  // Skip unparseable chunks
                }
              }
            }
          }
        } catch (e) {
          console.error('[EdgeAI] Stream error:', e);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
      },
    });
  } catch (e) {
    console.error('[EdgeAI] Route error:', e);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}
