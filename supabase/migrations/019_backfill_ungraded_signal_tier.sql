-- Backfill: reclassify prediction_accuracy_log rows that were tagged "NO EDGE"
-- but have NULL omi_fair_spread — these games were never properly analyzed and
-- their garbage/stale fair lines inflate the NO EDGE tier's error metrics.

UPDATE prediction_accuracy_log
SET signal_tier = 'UNGRADED'
WHERE signal_tier = 'NO EDGE'
  AND omi_fair_spread IS NULL;
