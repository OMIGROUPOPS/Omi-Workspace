-- Add edge tracking columns to composite_history
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS raw_edge_pct numeric;
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS capped_edge_pct numeric;

-- Add edge tracking columns to prediction_accuracy_log
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS raw_edge_pct numeric;
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS capped_edge_pct numeric;
