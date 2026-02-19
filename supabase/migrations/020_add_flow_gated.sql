-- Add flow gate columns to composite_history.
-- flow_gated: true when HIGH/MAX EDGE signal was downgraded because Flow < 0.55
-- pillar_flow: stored so carry-forward & fast-refresh paths can re-evaluate the gate

ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS flow_gated boolean DEFAULT false;
ALTER TABLE composite_history ADD COLUMN IF NOT EXISTS pillar_flow float;
