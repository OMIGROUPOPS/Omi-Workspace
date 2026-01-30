-- Live Edges Table
-- Tracks real-time betting edges detected from line movements, juice improvements,
-- exchange divergences, and reverse line movements

CREATE TABLE IF NOT EXISTS live_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id TEXT NOT NULL,
  sport TEXT NOT NULL,
  market_type TEXT NOT NULL,           -- 'h2h', 'spreads', 'totals', 'player_props'
  outcome_key TEXT NOT NULL,           -- 'home', 'away', 'over', 'under', 'player_name|stat|over'
  edge_type TEXT NOT NULL,             -- 'line_movement', 'juice_improvement', 'exchange_divergence', 'reverse_line'

  -- Edge details
  initial_value DECIMAL,               -- Original line/price when edge detected
  current_value DECIMAL,               -- Current line/price
  edge_magnitude DECIMAL NOT NULL,     -- Size of edge (0.5 points, 5 cents juice, etc.)
  edge_pct DECIMAL,                    -- Percentage improvement

  -- Books involved
  triggering_book TEXT,                -- Book that triggered the edge
  best_current_book TEXT,              -- Current best book for this edge
  sharp_book_line DECIMAL,             -- Pinnacle/sharp line for comparison

  -- Lifecycle
  status TEXT NOT NULL DEFAULT 'active', -- 'active', 'fading', 'expired'
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  faded_at TIMESTAMPTZ,
  expired_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,              -- Game commence time

  -- Metadata
  confidence DECIMAL,                  -- 0-100 confidence score
  notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(game_id, market_type, outcome_key, edge_type)
);

-- Indexes for real-time queries
CREATE INDEX IF NOT EXISTS idx_live_edges_status ON live_edges(status, sport);
CREATE INDEX IF NOT EXISTS idx_live_edges_game ON live_edges(game_id);
CREATE INDEX IF NOT EXISTS idx_live_edges_detected ON live_edges(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_live_edges_sport ON live_edges(sport);
CREATE INDEX IF NOT EXISTS idx_live_edges_type ON live_edges(edge_type);

-- Enable RLS
ALTER TABLE live_edges ENABLE ROW LEVEL SECURITY;

-- Policies for public read, anon write (for API routes)
CREATE POLICY "Allow public read on live_edges"
  ON live_edges FOR SELECT TO public USING (true);

CREATE POLICY "Allow anon insert on live_edges"
  ON live_edges FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow anon update on live_edges"
  ON live_edges FOR UPDATE TO anon USING (true);

CREATE POLICY "Allow anon delete on live_edges"
  ON live_edges FOR DELETE TO anon USING (true);

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE live_edges;

-- Comments
COMMENT ON TABLE live_edges IS 'Tracks real-time betting edges detected from odds movements';
COMMENT ON COLUMN live_edges.edge_type IS 'Type of edge: line_movement, juice_improvement, exchange_divergence, reverse_line';
COMMENT ON COLUMN live_edges.status IS 'Edge lifecycle status: active, fading, expired';
COMMENT ON COLUMN live_edges.edge_magnitude IS 'Size of the edge (points for spreads/totals, cents for moneyline)';
COMMENT ON COLUMN live_edges.confidence IS 'Confidence score 0-100 based on edge strength and market factors';
