-- Add draw columns to composite_history for soccer 3-way ML
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS fair_ml_draw integer;
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS book_ml_draw integer;
