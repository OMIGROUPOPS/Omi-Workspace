-- Migration 022: Player stats cache for BallDontLie API data
-- Stores player season averages, recent game logs, and advanced stats
-- Used by player_analytics.py to compute projections, form scores, and consistency signals

CREATE TABLE IF NOT EXISTS player_stats_cache (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    player_name text NOT NULL,
    bdl_player_id integer,
    sport_key text NOT NULL DEFAULT 'basketball_nba',
    season_averages jsonb DEFAULT '{}'::jsonb,
    recent_games jsonb DEFAULT '[]'::jsonb,
    advanced_stats jsonb DEFAULT '{}'::jsonb,
    injury_status text,
    fetched_at timestamptz DEFAULT now(),
    expires_at timestamptz DEFAULT now() + interval '2 hours',
    UNIQUE (player_name, sport_key)
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_player_stats_cache_name ON player_stats_cache (player_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_cache_bdl_id ON player_stats_cache (bdl_player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_cache_expires ON player_stats_cache (expires_at);
