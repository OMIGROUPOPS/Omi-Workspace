-- calibration_config: DB-backed pillar weights and scale factors per sport
-- Allows reflection engine to push updated weights without code changes
-- weight_calculator.py reads from this table (with 5-min cache, hardcoded fallback)

CREATE TABLE IF NOT EXISTS calibration_config (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  sport_key text NOT NULL,
  config_type text NOT NULL,  -- 'pillar_weights' or 'scale_factors'
  config_data jsonb NOT NULL,
  created_at timestamptz DEFAULT now(),
  active boolean DEFAULT true
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cc_active_unique
  ON calibration_config(sport_key, config_type)
  WHERE active = true;

CREATE INDEX IF NOT EXISTS idx_cc_lookup
  ON calibration_config(sport_key, config_type, active);

ALTER TABLE calibration_config DISABLE ROW LEVEL SECURITY;

-- Seed: pillar_weights per sport (from config.py SPORT_WEIGHTS)
INSERT INTO calibration_config (sport_key, config_type, config_data) VALUES
('NBA', 'pillar_weights', '{"execution": 0.20, "incentives": 0.10, "shocks": 0.20, "time_decay": 0.20, "flow": 0.20, "game_environment": 0.10}'),
('NCAAB', 'pillar_weights', '{"execution": 0.15, "incentives": 0.15, "shocks": 0.25, "time_decay": 0.10, "flow": 0.25, "game_environment": 0.10}'),
('NFL', 'pillar_weights', '{"execution": 0.15, "incentives": 0.15, "shocks": 0.25, "time_decay": 0.05, "flow": 0.25, "game_environment": 0.15}'),
('NCAAF', 'pillar_weights', '{"execution": 0.15, "incentives": 0.15, "shocks": 0.25, "time_decay": 0.10, "flow": 0.25, "game_environment": 0.10}'),
('NHL', 'pillar_weights', '{"execution": 0.15, "incentives": 0.10, "shocks": 0.25, "time_decay": 0.15, "flow": 0.25, "game_environment": 0.10}'),
('EPL', 'pillar_weights', '{"execution": 0.20, "incentives": 0.25, "shocks": 0.20, "time_decay": 0.15, "flow": 0.15, "game_environment": 0.05}');

-- Seed: scale_factors (global, from internal_grader.py constants)
INSERT INTO calibration_config (sport_key, config_type, config_data) VALUES
('GLOBAL', 'scale_factors', '{"spread_factor": 0.15, "total_factor": 0.20, "ml_factor": 0.01}');
