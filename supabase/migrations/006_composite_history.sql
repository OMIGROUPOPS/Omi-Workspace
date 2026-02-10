-- composite_history: Track composite scores and fair lines over time per game
-- Used to monitor how OMI's fair pricing evolves as new data flows in

CREATE TABLE IF NOT EXISTS composite_history (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  game_id text NOT NULL,
  sport_key text NOT NULL,
  timestamp timestamptz DEFAULT now() NOT NULL,
  composite_spread numeric,
  composite_total numeric,
  composite_ml numeric,
  fair_spread numeric,
  fair_total numeric,
  fair_ml_home numeric,
  fair_ml_away numeric,
  book_spread numeric,
  book_total numeric,
  book_ml_home numeric,
  book_ml_away numeric
);

CREATE INDEX IF NOT EXISTS idx_ch_game_time ON composite_history(game_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_ch_sport_time ON composite_history(sport_key, timestamp);

ALTER TABLE composite_history DISABLE ROW LEVEL SECURITY;
