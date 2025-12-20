// American odds to implied probability
export function americanToImplied(odds: number): number {
    if (odds > 0) {
      return 100 / (odds + 100);
    }
    return Math.abs(odds) / (Math.abs(odds) + 100);
  }
  
  // Implied probability to American odds
  export function impliedToAmerican(prob: number): number {
    if (prob >= 0.5) {
      return Math.round(-100 * prob / (1 - prob));
    }
    return Math.round(100 * (1 - prob) / prob);
  }
  
  // Remove vig and get true probabilities
  export function removeVig(prob1: number, prob2: number): { 
    true1: number; 
    true2: number; 
    vig: number 
  } {
    const total = prob1 + prob2;
    const vig = total - 1;
    return {
      true1: prob1 / total,
      true2: prob2 / total,
      vig: vig * 100,
    };
  }
  
  // Remove vig from American odds directly
  export function removeVigFromAmerican(odds1: number, odds2: number) {
    const implied1 = americanToImplied(odds1);
    const implied2 = americanToImplied(odds2);
    return removeVig(implied1, implied2);
  }
  
  // Format American odds for display
  export function formatOdds(odds: number): string {
    if (odds > 0) return `+${odds}`;
    return odds.toString();
  }
  
  // Format probability as percentage
  export function formatProb(prob: number, decimals: number = 1): string {
    return `${(prob * 100).toFixed(decimals)}%`;
  }
  
  // Calculate edge delta
  export function calculateEdgeDelta(omiProb: number, bookImpliedProb: number): number {
    return omiProb - bookImpliedProb;
  }
  
  // Format edge delta for display
  export function formatEdgeDelta(delta: number): string {
    const pct = (delta * 100).toFixed(1);
    if (delta > 0) return `+${pct}%`;
    return `${pct}%`;
  }
  
  // Format spread for display
  export function formatSpread(point: number): string {
    if (point > 0) return `+${point}`;
    return point.toString();
  }