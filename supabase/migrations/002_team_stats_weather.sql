-- Team Stats Table (populated from ESPN/NBA.com APIs)
-- Feeds: Game Environment pillar, Matchup Dynamics pillar

CREATE TABLE IF NOT EXISTS team_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id TEXT NOT NULL,
  team_name TEXT NOT NULL,
  team_abbrev TEXT,
  sport TEXT NOT NULL,
  league TEXT,
  season TEXT,

  -- Pace & efficiency (Game Environment pillar)
  pace DECIMAL,
  offensive_rating DECIMAL,
  defensive_rating DECIMAL,
  net_rating DECIMAL,

  -- Record
  wins INT,
  losses INT,
  win_pct DECIMAL,
  home_wins INT,
  home_losses INT,
  away_wins INT,
  away_losses INT,
  streak INT, -- positive = win streak, negative = loss streak

  -- Scoring stats
  points_per_game DECIMAL,
  points_allowed_per_game DECIMAL,
  point_differential DECIMAL,

  -- Additional advanced stats
  true_shooting_pct DECIMAL,
  assist_ratio DECIMAL,
  rebound_pct DECIMAL,
  turnover_ratio DECIMAL,

  -- Injuries (JSON array of injured players)
  injuries JSONB DEFAULT '[]'::jsonb,

  -- Metadata
  source TEXT DEFAULT 'espn',
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(team_id, sport, season)
);

-- Game Weather Table (for outdoor sports: NFL, MLB, Soccer, Golf)
-- Feeds: Game Environment pillar

CREATE TABLE IF NOT EXISTS game_weather (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id TEXT NOT NULL,
  sport TEXT,
  venue_name TEXT,
  venue_city TEXT,
  venue_state TEXT,
  venue_lat DECIMAL,
  venue_lon DECIMAL,

  -- Weather data
  temperature_f DECIMAL,
  feels_like_f DECIMAL,
  wind_speed_mph DECIMAL,
  wind_gust_mph DECIMAL,
  wind_direction TEXT,
  wind_degrees INT,
  humidity_pct DECIMAL,
  precipitation_pct DECIMAL,
  conditions TEXT,
  weather_icon TEXT,

  -- Game impact assessment
  is_dome BOOLEAN DEFAULT FALSE,
  weather_impact_score INT, -- 0-100, higher = more impact on game

  fetched_at TIMESTAMPTZ DEFAULT NOW(),
  game_time TIMESTAMPTZ,

  UNIQUE(game_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_team_stats_sport ON team_stats(sport);
CREATE INDEX IF NOT EXISTS idx_team_stats_team ON team_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_league ON team_stats(league);
CREATE INDEX IF NOT EXISTS idx_team_stats_updated ON team_stats(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_game_weather_game ON game_weather(game_id);
CREATE INDEX IF NOT EXISTS idx_game_weather_sport ON game_weather(sport);
CREATE INDEX IF NOT EXISTS idx_game_weather_time ON game_weather(game_time);

-- Enable RLS
ALTER TABLE team_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_weather ENABLE ROW LEVEL SECURITY;

-- Policies for public read, service role write
CREATE POLICY "Allow public read on team_stats"
  ON team_stats FOR SELECT TO public USING (true);

CREATE POLICY "Allow anon insert on team_stats"
  ON team_stats FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anon update on team_stats"
  ON team_stats FOR UPDATE TO anon USING (true);

CREATE POLICY "Allow public read on game_weather"
  ON game_weather FOR SELECT TO public USING (true);

CREATE POLICY "Allow anon insert on game_weather"
  ON game_weather FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anon update on game_weather"
  ON game_weather FOR UPDATE TO anon USING (true);

-- Comments
COMMENT ON TABLE team_stats IS 'Team statistics from ESPN/NBA.com for EdgeScout pillars';
COMMENT ON TABLE game_weather IS 'Weather data for outdoor sports games';
COMMENT ON COLUMN team_stats.pace IS 'Possessions per 48 minutes (NBA) or plays per game';
COMMENT ON COLUMN team_stats.offensive_rating IS 'Points scored per 100 possessions';
COMMENT ON COLUMN team_stats.defensive_rating IS 'Points allowed per 100 possessions';
COMMENT ON COLUMN game_weather.weather_impact_score IS '0-100 score indicating how much weather affects gameplay';
