-- prediction_grades: Per-market/period/book grading rows
-- Used by the internal Edge performance dashboard to track prediction accuracy

CREATE TABLE IF NOT EXISTS prediction_grades (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  game_id text NOT NULL,
  sport_key text NOT NULL,
  market_type text NOT NULL,       -- spread, total, moneyline
  period text DEFAULT 'full',      -- full, h1, h2, q1-q4, p1-p3
  omi_fair_line numeric,           -- OMI's fair line value
  book_line numeric,               -- Book's line value
  book_name text,                  -- fanduel, draftkings, etc.
  gap numeric,                     -- omi_fair_line - book_line
  signal text,                     -- MISPRICED, VALUE, FAIR, SHARP
  confidence_tier integer,         -- 55, 60, 65, 70
  prediction_side text,            -- home, away, over, under
  actual_result text,              -- home_covered, away_covered, over, under, push
  is_correct boolean,              -- true, false, null (push)
  pillar_composite numeric,        -- composite score at time of prediction
  ceq_score numeric,               -- CEQ score at time of prediction
  graded_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pg_game ON prediction_grades(game_id);
CREATE INDEX IF NOT EXISTS idx_pg_sport ON prediction_grades(sport_key);
CREATE INDEX IF NOT EXISTS idx_pg_graded ON prediction_grades(graded_at);
CREATE INDEX IF NOT EXISTS idx_pg_tier ON prediction_grades(confidence_tier);
CREATE INDEX IF NOT EXISTS idx_pg_market ON prediction_grades(market_type);
