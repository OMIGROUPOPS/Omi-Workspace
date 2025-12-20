import { CONFIDENCE_THRESHOLDS } from '../utils/constants';
import type { EdgeStatus, PillarScores } from '@/types/edge';

export function getEdgeStatus(confidence: number): EdgeStatus {
  if (confidence >= CONFIDENCE_THRESHOLDS.RARE) return 'rare';
  if (confidence >= CONFIDENCE_THRESHOLDS.STRONG_EDGE) return 'strong_edge';
  if (confidence >= CONFIDENCE_THRESHOLDS.EDGE) return 'edge';
  if (confidence >= CONFIDENCE_THRESHOLDS.WATCH) return 'watch';
  return 'pass';
}

export interface DecisionGateInput {
  pillarScores: PillarScores;
  pillarWeights: PillarScores;
  edgeDelta: number;
  flowConfidenceMultiplier: number;
}

export interface DecisionGateOutput {
  rawConfidence: number;
  adjustedConfidence: number;
  status: EdgeStatus;
  shouldSurface: boolean;
  shouldAlert: boolean;
}

export function runDecisionGate(input: DecisionGateInput): DecisionGateOutput {
  const { pillarScores, pillarWeights, edgeDelta, flowConfidenceMultiplier } = input;

  // Weighted average of pillar scores (0-1 range)
  const weightedScore =
    pillarScores.execution * pillarWeights.execution +
    pillarScores.incentives * pillarWeights.incentives +
    pillarScores.shocks * pillarWeights.shocks +
    pillarScores.timeDecay * pillarWeights.timeDecay +
    pillarScores.flow * pillarWeights.flow;

  // Base confidence from pillar agreement (0-50 range)
  const pillarConfidence = weightedScore * 50;

  // Edge magnitude bonus (0-50 range)
  const edgeMagnitude = Math.abs(edgeDelta);
  const edgeBonus = Math.min(edgeMagnitude * 500, 50);

  // Raw confidence
  const rawConfidence = pillarConfidence + edgeBonus;

  // Apply flow confidence multiplier
  const adjustedConfidence = Math.min(rawConfidence * flowConfidenceMultiplier, 100);

  const status = getEdgeStatus(adjustedConfidence);

  return {
    rawConfidence,
    adjustedConfidence,
    status,
    shouldSurface: status !== 'pass',
    shouldAlert: status === 'strong_edge' || status === 'rare',
  };
}