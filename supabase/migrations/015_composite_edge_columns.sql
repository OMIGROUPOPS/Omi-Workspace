-- Add edge tracking columns to composite_history
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS raw_edge_pct numeric;
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS capped_edge_pct numeric;

-- Add draw ML columns to composite_history (soccer 3-way moneylines)
-- Migration 008 was never applied — adding here
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS fair_ml_draw numeric;
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS book_ml_draw numeric;

-- Add edge tracking columns to prediction_accuracy_log
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS raw_edge_pct numeric;
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS capped_edge_pct numeric;
