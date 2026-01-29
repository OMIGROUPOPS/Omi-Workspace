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
