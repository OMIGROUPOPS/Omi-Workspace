import type { PillarScores } from '@/types/edge';
import { PILLAR_WEIGHTS_DEFAULT } from '../utils/constants';

export function calculatePillarAdjustment(
  scores: PillarScores,
  weights: PillarScores = {
    execution: PILLAR_WEIGHTS_DEFAULT.EXECUTION,
    incentives: PILLAR_WEIGHTS_DEFAULT.INCENTIVES,
    shocks: PILLAR_WEIGHTS_DEFAULT.SHOCKS,
    timeDecay: PILLAR_WEIGHTS_DEFAULT.TIME_DECAY,
    flow: PILLAR_WEIGHTS_DEFAULT.FLOW,
  }
): number {
  const weightedSum =
    (scores.execution - 0.5) * weights.execution +
    (scores.incentives - 0.5) * weights.incentives +
    (scores.shocks - 0.5) * weights.shocks +
    (scores.timeDecay - 0.5) * weights.timeDecay +
    (scores.flow - 0.5) * weights.flow;

  return weightedSum * 0.3;
}

export function calculateOmiProbability(
  bookImpliedProb: number,
  pillarAdjustment: number
): number {
  const adjusted = bookImpliedProb + pillarAdjustment;
  return Math.max(0.01, Math.min(0.99, adjusted));
}

export function generateMockPillarScores(gameId: string): PillarScores {
  const seed = gameId.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const seededRandom = (offset: number) => {
    const x = Math.sin(seed + offset) * 10000;
    return 0.5 + (x - Math.floor(x) - 0.5) * 0.4;
  };

  return {
    execution: seededRandom(1),
    incentives: seededRandom(2),
    shocks: seededRandom(3),
    timeDecay: seededRandom(4),
    flow: seededRandom(5),
  };
}

export function calculateEdge(
  bookImpliedProb: number,
  pillarScores: PillarScores
): {
  omiTrueProb: number;
  edgeDelta: number;
  pillarAdjustment: number;
} {
  const pillarAdjustment = calculatePillarAdjustment(pillarScores);
  const omiTrueProb = calculateOmiProbability(bookImpliedProb, pillarAdjustment);
  const edgeDelta = omiTrueProb - bookImpliedProb;

  return {
    omiTrueProb,
    edgeDelta,
    pillarAdjustment,
  };
}