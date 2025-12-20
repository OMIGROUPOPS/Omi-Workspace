export type EdgeStatus = 'pass' | 'watch' | 'edge' | 'strong_edge' | 'rare';
export type MarketType = 'spreads' | 'h2h' | 'totals';
export type FlowType = 'informed' | 'reflexive' | 'noise';
export type Tier = 'tier_1' | 'tier_2';
export type GameStatus = 'upcoming' | 'live' | 'completed' | 'cancelled';

export interface PillarScores {
  execution: number;
  incentives: number;
  shocks: number;
  timeDecay: number;
  flow: number;
}

export interface PillarNotes {
  execution?: string;
  incentives?: string;
  shocks?: string;
  timeDecay?: string;
  flow?: string;
}

export interface EdgeCalculation {
  bookImpliedProb: number;
  omiTrueProb: number;
  edgeDelta: number;
  rawConfidence: number;
  adjustedConfidence: number;
  status: EdgeStatus;
  recommendedSide?: string;
  sideLabel?: string;
}

export interface Game {
  id: string;
  externalId: string;
  sportKey: string;
  homeTeam: string;
  awayTeam: string;
  commenceTime: Date;
  status: GameStatus;
  homeScore?: number;
  awayScore?: number;
}

export interface ConsensusOdds {
  spreads?: {
    line: number;
    homePrice: number;
    awayPrice: number;
    homeImplied: number;
    awayImplied: number;
  };
  h2h?: {
    homePrice: number;
    awayPrice: number;
    homeImplied: number;
    awayImplied: number;
  };
  totals?: {
    line: number;
    overPrice: number;
    underPrice: number;
    overImplied: number;
    underImplied: number;
  };
}

export interface LineSnapshot {
  id: string;
  gameId: string;
  marketType: MarketType;
  timestamp: Date;
  lineValue: number;
  price: number;
  impliedProb: number;
  omiTrueProb?: number;
  edgeDelta?: number;
  eventFlag?: 'injury' | 'steam' | 'sharp_move' | 'news' | 'weather' | 'lineup';
  eventNote?: string;
}

export interface EdgeUser {
  id: string;
  email: string;
  fullName?: string;
  tier: Tier;
  subscriptionStatus: 'active' | 'cancelled' | 'past_due' | 'trialing';
  createdAt: Date;
}