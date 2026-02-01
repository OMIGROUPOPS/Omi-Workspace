-- Add outcome_type column to line_snapshots for home/away distinction
-- This enables tracking both sides of ML markets

ALTER TABLE line_snapshots
ADD COLUMN IF NOT EXISTS outcome_type TEXT;

-- Create index for efficient filtering
CREATE INDEX IF NOT EXISTS idx_line_snapshots_outcome
ON line_snapshots(game_id, market_type, market_period, outcome_type);
