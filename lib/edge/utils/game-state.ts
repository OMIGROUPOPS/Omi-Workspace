// Centralized game state detection
// Use this everywhere to ensure consistent game state across the app

export type GameState = 'upcoming' | 'live' | 'final';

// Average game durations by sport (in hours)
const GAME_DURATIONS: Record<string, number> = {
  basketball_nba: 2.5,
  basketball_ncaab: 2.5,
  basketball_wnba: 2,
  americanfootball_nfl: 3.5,
  americanfootball_ncaaf: 3.5,
  icehockey_nhl: 3,
  baseball_mlb: 3.5,
  mma_mixed_martial_arts: 4,
  // Tennis can vary widely
  tennis: 3,
};

const DEFAULT_DURATION = 3; // hours

/**
 * Determine the current state of a game
 * @param commenceTime - Game start time (string or Date)
 * @param sportKey - Sport identifier for duration lookup
 * @returns GameState - 'upcoming', 'live', or 'final'
 */
export function getGameState(commenceTime: string | Date, sportKey?: string): GameState {
  const gameStart = typeof commenceTime === 'string' ? new Date(commenceTime) : commenceTime;
  const now = new Date();

  // Game hasn't started yet
  if (now < gameStart) {
    return 'upcoming';
  }

  // Calculate expected end time based on sport
  const duration = sportKey
    ? GAME_DURATIONS[sportKey] || DEFAULT_DURATION
    : DEFAULT_DURATION;

  const expectedEnd = new Date(gameStart.getTime() + duration * 60 * 60 * 1000);

  // Game is in progress
  if (now < expectedEnd) {
    return 'live';
  }

  // Game has ended
  return 'final';
}

/**
 * Check if a game is currently live
 */
export function isGameLive(commenceTime: string | Date, sportKey?: string): boolean {
  return getGameState(commenceTime, sportKey) === 'live';
}

/**
 * Check if a game has finished
 */
export function isGameFinal(commenceTime: string | Date, sportKey?: string): boolean {
  return getGameState(commenceTime, sportKey) === 'final';
}

/**
 * Check if a game is upcoming
 */
export function isGameUpcoming(commenceTime: string | Date, sportKey?: string): boolean {
  return getGameState(commenceTime, sportKey) === 'upcoming';
}

/**
 * Get a human-readable time string
 * @returns "LIVE", "FINAL", or countdown like "2h 30m"
 */
export function getTimeDisplay(commenceTime: string | Date, sportKey?: string): string {
  const state = getGameState(commenceTime, sportKey);

  if (state === 'live') return 'LIVE';
  if (state === 'final') return 'FINAL';

  // Calculate countdown
  const gameStart = typeof commenceTime === 'string' ? new Date(commenceTime) : commenceTime;
  const now = new Date();
  const diff = gameStart.getTime() - now.getTime();

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days}d ${hours % 24}h`;
  }
  if (hours > 0) return `${hours}h ${mins}m`;
  if (mins > 0) return `${mins}m`;
  return 'Soon';
}

/**
 * Get hours since game started (useful for live game tracking)
 */
export function getHoursSinceStart(commenceTime: string | Date): number {
  const gameStart = typeof commenceTime === 'string' ? new Date(commenceTime) : commenceTime;
  const now = new Date();
  return (now.getTime() - gameStart.getTime()) / (1000 * 60 * 60);
}

/**
 * Estimate current period/quarter for a live game
 * Returns format like "Q2 8:30" or "2nd 12:45" or "P2 10:00"
 */
export function getEstimatedPeriod(commenceTime: string | Date, sportKey?: string): string | null {
  const state = getGameState(commenceTime, sportKey);
  if (state !== 'live') return null;

  const gameStart = typeof commenceTime === 'string' ? new Date(commenceTime) : commenceTime;
  const now = new Date();
  const elapsedMinutes = (now.getTime() - gameStart.getTime()) / (1000 * 60);

  // Sport-specific period calculation
  if (sportKey?.includes('basketball_nba') || sportKey?.includes('basketball_wnba')) {
    // NBA: 4 quarters of 12 minutes each (48 min game time, ~2.5 hours real time)
    // Account for breaks, timeouts, halftime (~20 min halftime)
    const periodMinutes = 35; // ~35 real minutes per quarter including stoppages
    const quarter = Math.min(4, Math.floor(elapsedMinutes / periodMinutes) + 1);
    const inPeriodMinutes = elapsedMinutes % periodMinutes;
    const timeRemaining = Math.max(0, 12 - Math.floor(inPeriodMinutes * 12 / periodMinutes));
    return `Q${quarter} ${timeRemaining}:00`;
  }

  if (sportKey?.includes('basketball_ncaab')) {
    // NCAAB: 2 halves of 20 minutes each
    const halfMinutes = 60; // ~60 real minutes per half including stoppages
    const half = elapsedMinutes < halfMinutes ? 1 : 2;
    const inHalfMinutes = elapsedMinutes % halfMinutes;
    const timeRemaining = Math.max(0, 20 - Math.floor(inHalfMinutes * 20 / halfMinutes));
    return `${half}H ${timeRemaining}:00`;
  }

  if (sportKey?.includes('americanfootball')) {
    // NFL/NCAAF: 4 quarters of 15 minutes each
    const periodMinutes = 45; // ~45 real minutes per quarter including stoppages
    const quarter = Math.min(4, Math.floor(elapsedMinutes / periodMinutes) + 1);
    const inPeriodMinutes = elapsedMinutes % periodMinutes;
    const timeRemaining = Math.max(0, 15 - Math.floor(inPeriodMinutes * 15 / periodMinutes));
    return `Q${quarter} ${timeRemaining}:00`;
  }

  if (sportKey?.includes('icehockey')) {
    // NHL: 3 periods of 20 minutes each
    const periodMinutes = 50; // ~50 real minutes per period including intermissions
    const period = Math.min(3, Math.floor(elapsedMinutes / periodMinutes) + 1);
    const inPeriodMinutes = elapsedMinutes % periodMinutes;
    const timeRemaining = Math.max(0, 20 - Math.floor(inPeriodMinutes * 20 / periodMinutes));
    return `P${period} ${timeRemaining}:00`;
  }

  if (sportKey?.includes('soccer')) {
    // Soccer: 2 halves of 45 minutes each
    const halfMinutes = 55; // ~55 real minutes per half including stoppage time
    const half = elapsedMinutes < halfMinutes ? 1 : 2;
    const inHalfMinutes = elapsedMinutes % halfMinutes;
    const matchMinute = Math.floor(inHalfMinutes * 45 / halfMinutes) + (half === 2 ? 45 : 0);
    return `${matchMinute}'`;
  }

  // Default: just show elapsed time
  const hours = Math.floor(elapsedMinutes / 60);
  const mins = Math.floor(elapsedMinutes % 60);
  return `${hours}:${mins.toString().padStart(2, '0')}`;
}
