// Binary Options Greeks Calculator for Prediction Markets
// Contracts settle at 0 or 100. Price p is between 0 and 1.
// T = hours to expiration. sigma = implied volatility estimate.

export interface Greeks {
  delta: number;
  theta: number;
  gamma: number;
  vega: number;
  iv: number;
}

function logit(p: number): number {
  const clamped = Math.max(0.005, Math.min(0.995, p));
  return Math.log(clamped / (1 - clamped));
}

/**
 * Calculate approximate Greeks for a binary option (prediction market contract).
 *
 * @param price - Current price as fraction 0..1 (e.g. 0.64 = 64¢)
 * @param hoursToExpiry - Hours until contract settles
 * @param sigma - Volatility estimate from scanner data (default 0.5)
 */
export function calcGreeks(
  price: number,
  hoursToExpiry: number,
  sigma: number = 0.5,
): Greeks {
  const p = Math.max(0.01, Math.min(0.99, price));
  const T = Math.max(0.01, hoursToExpiry);
  const s = Math.max(0.05, sigma);

  // Delta: sensitivity to probability change
  // For binary: peaks at 50¢, zero at extremes
  // δ ≈ 4 * p * (1-p) — logistic sensitivity
  const delta = 4 * p * (1 - p);

  // Theta: time decay toward boundary per hour
  // Contracts near 100¢ converge toward 100, near 0¢ toward 0
  const boundary = p > 0.5 ? 1 : 0;
  const distance = Math.abs(p - boundary);
  const theta = T > 0 ? -(distance / T) * 100 : 0; // cents per hour

  // Gamma: rate of delta change — spikes near 50¢ at expiry
  const gamma = Math.abs(delta * (1 - 2 * p) * 4);

  // Vega: sensitivity to volatility — highest at 50¢
  const vega = delta * Math.sqrt(T) * 0.5;

  // IV: implied vol backed out from price and time
  const iv = T > 0 ? Math.abs(logit(p)) / Math.sqrt(T) : s;

  return {
    delta: Math.round(delta * 1000) / 1000,
    theta: Math.round(theta * 100) / 100,
    gamma: Math.round(gamma * 1000) / 1000,
    vega: Math.round(vega * 1000) / 1000,
    iv: Math.round(iv * 100) / 100,
  };
}

/**
 * Format Greeks for display.
 */
export function formatGreek(label: string, value: number, suffix = ""): string {
  if (label === "Θ") {
    return `${value >= 0 ? "+" : ""}${value.toFixed(1)}¢/hr`;
  }
  if (label === "IV") {
    return `${(value * 100).toFixed(0)}%`;
  }
  return `${value.toFixed(3)}${suffix}`;
}
