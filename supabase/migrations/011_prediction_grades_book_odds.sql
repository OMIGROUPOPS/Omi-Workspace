-- Add book_odds column to store actual American odds from book at grading time
-- Enables implied probability edge calculation (not assumed -110)
ALTER TABLE prediction_grades ADD COLUMN IF NOT EXISTS book_odds INTEGER;
