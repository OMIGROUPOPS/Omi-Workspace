-- Add stale flag to game_results
-- Pre-Feb-10 data had broken Shocks/Flow pillars — not worth grading
ALTER TABLE game_results ADD COLUMN IF NOT EXISTS stale boolean DEFAULT false;

-- Mark all pre-Feb-10 game_results as stale
UPDATE game_results SET stale = true WHERE commence_time < '2026-02-10T00:00:00+00:00';
