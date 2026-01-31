// Live Edge Detection Types
// These types support the real-time edge tracking system

export type EdgeType =
  | 'line_movement'      // Line moved favorably since first snapshot
  | 'juice_improvement'  // Vig reduced on a line
  | 'exchange_divergence' // Sharp book differs from soft books
  | 'reverse_line';      // Public betting one way, line moving opposite

export type EdgeStatus = 'active' | 'fading' | 'expired';

export type MarketType = 'h2h' | 'spreads' | 'totals' | 'player_props';

export interface LiveEdge {
  id: string;
  game_id: string;
  sport: string;
  market_type: MarketType;
  outcome_key: string;            // 'home', 'away', 'over', 'under', 'player_name|stat|over'
  edge_type: EdgeType;

  // Edge details
  initial_value: number | null;   // Original line/price when edge detected
  current_value: number | null;   // Current line/price
  edge_magnitude: number;         // Size of edge (0.5 points, 5 cents juice, etc.)
  edge_pct: number | null;        // Percentage improvement

  // Books involved
  triggering_book: string | null; // Book that triggered the edge
  best_current_book: string | null; // Current best book for this edge
  sharp_book_line: number | null; // Pinnacle/sharp line for comparison

  // Lifecycle
  status: EdgeStatus;
  detected_at: string;
  faded_at: string | null;
  expired_at: string | null;
  expires_at: string | null;      // Game commence time

  // Metadata
  confidence: number | null;      // 0-100 confidence score
  notes: string | null;

  created_at: string;
  updated_at: string;
}

export interface EdgeDetectionResult {
  edgeType: EdgeType;
  magnitude: number;
  edgePct: number;
  initialValue: number;
  currentValue: number;
  triggeringBook: string;
  bestCurrentBook: string;
  confidence: number;
  outcomeKey: string;
  marketType: MarketType;
  sharpBookLine?: number;
  notes?: string;
}

// Detection thresholds
export const EDGE_THRESHOLDS = {
  LINE_MOVEMENT: {
    spreads: 0.5,        // Half point minimum
    totals: 0.5,         // Half point minimum
    h2h: 10,             // 10 cents on moneyline (-150 to -140)
    player_props: 0.5,   // Half point/unit minimum
  },
  JUICE_IMPROVEMENT: 5,  // 5 cents minimum (-110 to -105)
  EXCHANGE_DIVERGENCE: {
    spreads: 1.0,        // 1 point vs sharp
    totals: 1.0,         // 1 point vs sharp
    h2h: 15,             // 15 cents vs sharp
    player_props: 1.0,   // 1 unit vs sharp
  },
  FADING_THRESHOLD: 0.5, // 50% of edge remaining = fading status
} as const;

// Confidence scoring weights - RECALIBRATED for realistic values
// Only sharp divergence and reverse line should hit 70%+
export const EDGE_CONFIDENCE_WEIGHTS = {
  line_movement: {
    base: 35,            // 0.5pt = 43%, 1pt = 51%, 1.5pt = 59%
    perHalfPoint: 8,
    max: 70,             // Cap at 70% - line movement alone isn't definitive
  },
  juice_improvement: {
    base: 20,            // Minor edge, starts low: 5¢ = 35%, 10¢ = 50%
    perCent: 3,
    max: 55,             // Juice alone is small edge, cap at 55%
  },
  exchange_divergence: {
    base: 55,            // Sharp divergence is strong signal
    perPoint: 5,         // 1pt = 60%, 2pt = 65%, 3pt = 70%
    max: 80,             // Can hit 80% with significant divergence
  },
  reverse_line: {
    base: 65,            // Reverse line (sharp action) is strong
    perHalfPoint: 4,
    max: 85,             // Only reverse line can hit 85%
  },
} as const;

// Sharp books for exchange divergence detection
export const SHARP_BOOKS = [
  'pinnacle',
  'betcris',
  'circa',
  'bookmaker',
] as const;

// Soft/retail books for edge opportunities
export const SOFT_BOOKS = [
  'draftkings',
  'fanduel',
  'betmgm',
  'caesars',
  'pointsbet',
  'betrivers',
  'unibet',
] as const;

// Edge type display configuration
export const EDGE_TYPE_CONFIG = {
  line_movement: {
    label: 'Line Movement',
    shortLabel: 'LM',
    description: 'Line moved favorably from opening',
    icon: 'TrendingUp',
    color: 'blue',
  },
  juice_improvement: {
    label: 'Juice Improvement',
    shortLabel: 'JI',
    description: 'Reduced vig on this line',
    icon: 'DollarSign',
    color: 'green',
  },
  exchange_divergence: {
    label: 'Sharp Divergence',
    shortLabel: 'SD',
    description: 'Soft books off from sharp line',
    icon: 'GitBranch',
    color: 'purple',
  },
  reverse_line: {
    label: 'Reverse Line',
    shortLabel: 'RL',
    description: 'Contrarian line movement',
    icon: 'RefreshCw',
    color: 'orange',
  },
} as const;

// Status display configuration
export const EDGE_STATUS_CONFIG = {
  active: {
    label: 'Active',
    color: 'green',
    bgClass: 'bg-green-500/10',
    textClass: 'text-green-500',
    borderClass: 'border-green-500/30',
  },
  fading: {
    label: 'Fading',
    color: 'yellow',
    bgClass: 'bg-yellow-500/10',
    textClass: 'text-yellow-500',
    borderClass: 'border-yellow-500/30',
  },
  expired: {
    label: 'Expired',
    color: 'gray',
    bgClass: 'bg-gray-500/10',
    textClass: 'text-gray-500',
    borderClass: 'border-gray-500/30',
  },
} as const;

// Helper to format edge magnitude for display
export function formatEdgeMagnitude(edge: LiveEdge): string {
  const magnitude = edge.edge_magnitude;

  // Juice improvement is always in cents, not points
  if (edge.edge_type === 'juice_improvement') {
    return `${Math.round(magnitude)}¢ juice`;
  }

  switch (edge.market_type) {
    case 'h2h':
      // Moneyline: show as cents
      return `${magnitude > 0 ? '+' : ''}${Math.round(magnitude)}¢`;
    case 'spreads':
    case 'totals':
    case 'player_props':
      // Points/units
      return `${magnitude > 0 ? '+' : ''}${magnitude.toFixed(1)} pts`;
    default:
      return magnitude.toString();
  }
}

// Helper to format edge for display
export function formatEdgeDescription(edge: LiveEdge): string {
  const config = EDGE_TYPE_CONFIG[edge.edge_type];

  switch (edge.edge_type) {
    case 'line_movement': {
      const pts = edge.edge_magnitude.toFixed(1);
      return `Line moved ${pts} pts (${edge.initial_value} → ${edge.current_value})`;
    }
    case 'juice_improvement': {
      const cents = Math.round(edge.edge_magnitude);
      const from = edge.initial_value;
      const to = edge.current_value;
      return `${cents}¢ savings (${from} → ${to})`;
    }
    case 'exchange_divergence': {
      const pts = edge.edge_magnitude.toFixed(1);
      return `${pts} pts off Pinnacle (sharp: ${edge.sharp_book_line})`;
    }
    case 'reverse_line': {
      const pts = edge.edge_magnitude.toFixed(1);
      return `Sharp money move: ${pts} pts against public`;
    }
    default:
      return config.description;
  }
}
