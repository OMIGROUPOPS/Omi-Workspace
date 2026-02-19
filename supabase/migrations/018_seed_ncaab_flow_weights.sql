-- Seed NCAAB weights based on accuracy data showing Flow is the only pillar
-- with positive accuracy lift (+8.59) while all others are negative (-3 to -6).
-- This gives the feedback loop a correct starting point instead of requiring
-- dozens of EMA cycles to converge from fundamentally wrong initial weights.
--
-- Old NCAAB weights: execution=0.15, incentives=0.15, shocks=0.25,
--                    time_decay=0.10, flow=0.25, game_environment=0.10
-- New NCAAB weights: execution=0.10, incentives=0.08, shocks=0.10,
--                    time_decay=0.08, flow=0.50, game_environment=0.14

UPDATE calibration_config
SET config_data = '{"execution": 0.10, "incentives": 0.08, "shocks": 0.10, "time_decay": 0.08, "flow": 0.50, "game_environment": 0.14}'::jsonb
WHERE sport_key = 'NCAAB'
  AND config_type = 'pillar_weights'
  AND active = true;

-- If no row exists (edge case), insert it
INSERT INTO calibration_config (sport_key, config_type, config_data, active)
SELECT 'NCAAB', 'pillar_weights',
       '{"execution": 0.10, "incentives": 0.08, "shocks": 0.10, "time_decay": 0.08, "flow": 0.50, "game_environment": 0.14}'::jsonb,
       true
WHERE NOT EXISTS (
    SELECT 1 FROM calibration_config
    WHERE sport_key = 'NCAAB' AND config_type = 'pillar_weights' AND active = true
);
