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