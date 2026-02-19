-- Migration 021: Add is_correct + market_type to prediction_accuracy_log
-- Unifies Performance + Accuracy tabs on a single table.

-- 1. Add columns
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS is_correct boolean;
ALTER TABLE prediction_accuracy_log ADD COLUMN IF NOT EXISTS market_type text DEFAULT 'spread';

-- 2. Backfill market_type for all existing rows (they are all spread-based)
UPDATE prediction_accuracy_log
SET market_type = 'spread'
WHERE market_type IS NULL;

-- 3. Backfill is_correct from omi_vs_book_spread_edge
--    positive edge = OMI was closer to actual than book = correct
--    negative edge = book was closer = incorrect
--    zero or NULL = push / unknown
UPDATE prediction_accuracy_log
SET is_correct = TRUE
WHERE omi_vs_book_spread_edge > 0
  AND is_correct IS NULL;

UPDATE prediction_accuracy_log
SET is_correct = FALSE
WHERE omi_vs_book_spread_edge < 0
  AND is_correct IS NULL;

-- Edge exactly 0 or NULL stays is_correct = NULL (push / indeterminate)
