-- game_results: Snapshot of prediction + final scores for grading
-- Created by ResultsTracker.snapshot_prediction_at_close()
-- Graded by AutoGrader.grade_completed_games()

CREATE TABLE IF NOT EXISTS game_results (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  game_id text NOT NULL UNIQUE,
  sport_key text NOT NULL,
  home_team text,
  away_team text,
  commence_time timestamptz,

  -- Closing lines (captured at prediction snapshot)
  closing_spread_home numeric,
  closing_spread_odds numeric,
  closing_ml_home integer,
  closing_ml_away integer,
  closing_total_line numeric,
  closing_total_over_odds numeric,

  -- Our edges at time of prediction
  our_edge_spread_home numeric DEFAULT 0,
  our_edge_spread_away numeric DEFAULT 0,
  our_edge_ml_home numeric DEFAULT 0,
  our_edge_ml_away numeric DEFAULT 0,
  our_edge_total_over numeric DEFAULT 0,
  our_edge_total_under numeric DEFAULT 0,

  -- Composite + confidence
  composite_score numeric,
  confidence_level text,

  -- Pillar scores
  pillar_execution numeric,
  pillar_incentives numeric,
  pillar_shocks numeric,
  pillar_time_decay numeric,
  pillar_flow numeric,
  pillar_game_environment numeric,

  -- Best bet
  best_bet_market text,
  best_bet_edge numeric,

  -- Actual results (filled by grading)
  home_score integer,
  away_score integer,
  final_spread numeric,
  final_total numeric,
  winner text,
  spread_result text,
  ml_result text,
  total_result text,
  best_bet_result text,
  graded_at timestamptz,

  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gr_game ON game_results(game_id);
CREATE INDEX IF NOT EXISTS idx_gr_sport ON game_results(sport_key);
CREATE INDEX IF NOT EXISTS idx_gr_graded ON game_results(graded_at);
CREATE INDEX IF NOT EXISTS idx_gr_commence ON game_results(commence_time);
