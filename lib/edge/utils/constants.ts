export const CONFIDENCE_THRESHOLDS = {
  PASS: 55,
  WATCH: 59,
  EDGE: 64,
  STRONG_EDGE: 69,
  RARE: 70,
} as const;

export const EDGE_STATUS = {
  PASS: 'pass',
  WATCH: 'watch',
  EDGE: 'edge',
  STRONG_EDGE: 'strong_edge',
  RARE: 'rare',
} as const;

export const EDGE_STATUS_CONFIG = {
  pass: { label: 'Pass', color: 'gray', description: 'No actionable edge' },
  watch: { label: 'Watch', color: 'yellow', description: 'Potential edge forming' },
  edge: { label: 'Edge', color: 'blue', description: 'Actionable edge detected' },
  strong_edge: { label: 'Strong', color: 'green', description: 'High confidence edge' },
  rare: { label: 'Rare', color: 'purple', description: 'Exceptional opportunity' },
} as const;

export const FLOW_CONFIDENCE_BANDS = {
  LOW_THRESHOLD: 0.05,
  MEDIUM_THRESHOLD: 0.20,
  LOW_MULTIPLIER: 0.3,
  MEDIUM_MULTIPLIER: 0.6,
  FULL_MULTIPLIER: 1.0,
} as const;

export const PILLAR_WEIGHTS_DEFAULT = {
  EXECUTION: 0.20,
  INCENTIVES: 0.15,
  SHOCKS: 0.25,
  TIME_DECAY: 0.15,
  FLOW: 0.25,
} as const;

export const MARKET_TYPES = {
  SPREADS: 'spreads',
  H2H: 'h2h',
  TOTALS: 'totals',
} as const;

export const EVENT_CATEGORIES = [
  { key: 'politics', name: 'Politics', icon: '🏛️' },
  { key: 'economics', name: 'Economics', icon: '📈' },
  { key: 'legal', name: 'Legal & Regulatory', icon: '⚖️' },
  { key: 'tech', name: 'Technology', icon: '💻' },
  { key: 'culture', name: 'Culture & Entertainment', icon: '🎬' },
  { key: 'crypto', name: 'Crypto & Web3', icon: '🪙' },
] as const;

export const POLLING_INTERVALS = {
  ODDS_NORMAL_MS: 5 * 60 * 1000,
  ODDS_PREGAME_MS: 1 * 60 * 1000,
  EVENTS_MS: 2 * 60 * 1000,
  PREGAME_WINDOW_MS: 60 * 60 * 1000,
} as const;

export const SUPPORTED_SPORTS = [
  // American Football
  { key: 'americanfootball_nfl', name: 'NFL', group: 'American Football', icon: '🏈', active: true, hasOutrights: false },
  { key: 'americanfootball_nfl_super_bowl_winner', name: 'Super Bowl Winner', group: 'American Football', icon: '🏆', active: true, hasOutrights: true },
  { key: 'americanfootball_ncaaf', name: 'NCAAF', group: 'American Football', icon: '🏈', active: true, hasOutrights: false },
  { key: 'americanfootball_ncaaf_championship_winner', name: 'NCAAF Championship', group: 'American Football', icon: '🏆', active: true, hasOutrights: true },

  // Basketball
  { key: 'basketball_nba', name: 'NBA', group: 'Basketball', icon: '🏀', active: true, hasOutrights: false },
  { key: 'basketball_nba_championship_winner', name: 'NBA Championship', group: 'Basketball', icon: '🏆', active: true, hasOutrights: true },
  { key: 'basketball_ncaab', name: 'NCAAB', group: 'Basketball', icon: '🏀', active: true, hasOutrights: false },
  { key: 'basketball_ncaab_championship_winner', name: 'NCAAB Championship', group: 'Basketball', icon: '🏆', active: true, hasOutrights: true },
  { key: 'basketball_wncaab', name: 'WNCAAB', group: 'Basketball', icon: '🏀', active: true, hasOutrights: false },
  { key: 'basketball_nbl', name: 'NBL Australia', group: 'Basketball', icon: '🏀', active: true, hasOutrights: false },

  // Baseball
  { key: 'baseball_mlb_world_series_winner', name: 'MLB World Series', group: 'Baseball', icon: '🏆', active: true, hasOutrights: true },

  // Ice Hockey
  { key: 'icehockey_nhl', name: 'NHL', group: 'Ice Hockey', icon: '🏒', active: true, hasOutrights: false },
  { key: 'icehockey_nhl_championship_winner', name: 'Stanley Cup Winner', group: 'Ice Hockey', icon: '🏆', active: true, hasOutrights: true },
  { key: 'icehockey_ahl', name: 'AHL', group: 'Ice Hockey', icon: '🏒', active: true, hasOutrights: false },
  { key: 'icehockey_sweden_hockey_league', name: 'SHL Sweden', group: 'Ice Hockey', icon: '🏒', active: true, hasOutrights: false },
  { key: 'icehockey_liiga', name: 'Liiga Finland', group: 'Ice Hockey', icon: '🏒', active: true, hasOutrights: false },
  { key: 'icehockey_mestis', name: 'Mestis Finland', group: 'Ice Hockey', icon: '🏒', active: true, hasOutrights: false },

  // Combat Sports
  { key: 'mma_mixed_martial_arts', name: 'MMA', group: 'Combat Sports', icon: '🥊', active: true, hasOutrights: false },
  { key: 'boxing_boxing', name: 'Boxing', group: 'Combat Sports', icon: '🥊', active: true, hasOutrights: false },

  // Soccer - England
  { key: 'soccer_epl', name: 'EPL', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_efl_champ', name: 'Championship', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_england_league1', name: 'League 1', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_england_league2', name: 'League 2', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_fa_cup', name: 'FA Cup', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_england_efl_cup', name: 'EFL Cup', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },

  // Soccer - Europe Top Leagues
  { key: 'soccer_spain_la_liga', name: 'La Liga', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_spain_segunda_division', name: 'La Liga 2', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_germany_bundesliga', name: 'Bundesliga', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_germany_bundesliga2', name: 'Bundesliga 2', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_germany_liga3', name: '3. Liga Germany', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_italy_serie_a', name: 'Serie A', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_italy_serie_b', name: 'Serie B', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_france_ligue_one', name: 'Ligue 1', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_france_ligue_two', name: 'Ligue 2', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_netherlands_eredivisie', name: 'Eredivisie', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_portugal_primeira_liga', name: 'Primeira Liga', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_belgium_first_div', name: 'Belgium First Div', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_austria_bundesliga', name: 'Austrian Bundesliga', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_switzerland_superleague', name: 'Swiss Superleague', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_denmark_superliga', name: 'Denmark Superliga', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_greece_super_league', name: 'Greece Super League', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_turkey_super_league', name: 'Turkey Super League', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_spl', name: 'Scottish Premiership', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },

  // Soccer - Americas
  { key: 'soccer_brazil_campeonato', name: 'Brasileirão', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_mexico_ligamx', name: 'Liga MX', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_conmebol_copa_libertadores', name: 'Copa Libertadores', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_conmebol_copa_sudamericana', name: 'Copa Sudamericana', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },

  // Soccer - International
  { key: 'soccer_uefa_champs_league', name: 'Champions League', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_fifa_world_cup', name: 'FIFA World Cup', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_fifa_world_cup_winner', name: 'World Cup Winner', group: 'Soccer', icon: '🏆', active: true, hasOutrights: true },
  { key: 'soccer_fifa_world_cup_qualifiers_europe', name: 'WC Qualifiers Europe', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },
  { key: 'soccer_africa_cup_of_nations', name: 'Africa Cup of Nations', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },

  // Soccer - Oceania
  { key: 'soccer_australia_aleague', name: 'A-League', group: 'Soccer', icon: '⚽', active: true, hasOutrights: false },

  // Golf
  { key: 'golf_masters_tournament_winner', name: 'Masters', group: 'Golf', icon: '⛳', active: true, hasOutrights: true },
  { key: 'golf_pga_championship_winner', name: 'PGA Championship', group: 'Golf', icon: '⛳', active: true, hasOutrights: true },
  { key: 'golf_us_open_winner', name: 'US Open', group: 'Golf', icon: '⛳', active: true, hasOutrights: true },
  { key: 'golf_the_open_championship_winner', name: 'The Open', group: 'Golf', icon: '⛳', active: true, hasOutrights: true },

  // Cricket
  { key: 'cricket_big_bash', name: 'Big Bash', group: 'Cricket', icon: '🏏', active: true, hasOutrights: false },
  { key: 'cricket_test_match', name: 'Test Matches', group: 'Cricket', icon: '🏏', active: true, hasOutrights: false },

  // Rugby
  { key: 'rugbyleague_nrl', name: 'NRL', group: 'Rugby', icon: '🏉', active: true, hasOutrights: false },
  { key: 'rugbyleague_nrl_state_of_origin', name: 'State of Origin', group: 'Rugby', icon: '🏉', active: true, hasOutrights: false },
  { key: 'rugbyunion_six_nations', name: 'Six Nations', group: 'Rugby', icon: '🏉', active: true, hasOutrights: false },

  // Aussie Rules
  { key: 'aussierules_afl', name: 'AFL', group: 'Aussie Rules', icon: '🏉', active: true, hasOutrights: false },

  // Handball
  { key: 'handball_germany_bundesliga', name: 'Handball Bundesliga', group: 'Handball', icon: '🤾', active: true, hasOutrights: false },

  // Politics
  { key: 'politics_us_presidential_election_winner', name: 'US Presidential Election', group: 'Politics', icon: '🗳️', active: true, hasOutrights: true },
] as const;