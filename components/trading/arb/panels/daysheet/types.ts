// ── Day Sheet types ─────────────────────────────────────────────────────────
// Source: .claude/today_sheet/LATEST.md (regenerates 5:55a / 11a / 4p ET)

export interface DaySheetHeader {
  dateLabel: string; // "July 16, 2026"
  generatedAt: string; // "11:56 AM ET"
  nav: number; // dollars
  tailCents: number; // session realized TAIL, in cents (signed)
  pathCents: number; // session realized PATH, in cents (signed)
  wageredToday: number; // dollars
  pOfferedPct: number; // executor participation %
  pOfferedFilled: number;
  pOfferedPosted: number;
  pMarketPct: number; // funnel participation %
  pMarketFilledLegs: number;
  pMarketListedLegs: number; // approx (~1476) — may carry a "~" prefix in source
  pMarketListedLegsApprox: boolean;
}

export type SettledOutcome = "win" | "loss";

export interface SettledRow {
  match: string;
  carried: boolean;
  cat: string;
  leg: string;
  bandCents: number;
  placedET: string;
  filledET: string;
  fillCents: number;
  w1BestCents: number | null; // null when source prints "no pre-bell tape"
  w1BestAt: string;
  w1BestNote: string | null; // verbatim note when no numeric value, e.g. "no pre-bell tape"
  realBell: string; // e.g. "07:00 AM"
  realBellSource: string; // e.g. "percat_fitted" | "fallback_bell" | "self_fill" | "tape_flow" | "price_divergence"
  schedET: string;
  schedDeltaMin: number; // signed, minutes vs Kalshi schedule
  exitRequiredCents: number;
  exitRequiredDeltaCents: number; // the "(+8)" part
  bestTickAfterFillCents: number | null; // null when source prints "—"
  bestTickAfterFillAt: string;
  bestTickAfterFillNote: string | null; // e.g. "—"
  closeLabel: string; // "EXIT 46¢ 08:19 AM" | "SETTLED LOSS 0¢"
  pnlCents: number; // signed, dollars-equivalent in cents ("+40¢" / "-270¢")
  pnlPctOfBasis: number; // signed, e.g. 105 or -500
  outcome: SettledOutcome;
  postBellFill: boolean; // filled timestamp occurred after the real bell timestamp
}

export interface OpenRow {
  match: string;
  carried: boolean;
  cat: string;
  leg: string;
  bandCents: number;
  placedET: string;
  filledET: string;
  fillCents: number;
  w1BestCents: number | null;
  w1BestAt: string;
  w1BestNote: string | null;
  realBell: string;
  realBellSource: string;
  schedET: string;
  schedDeltaMin: number;
  exitRequiredCents: number;
  exitRequiredDeltaCents: number;
  bestTickAfterFillCents: number | null;
  bestTickAfterFillAt: string;
  bestTickAfterFillNote: string | null;
  markCents: number;
  markVsBasisCents: number; // signed
  exitRestingCents: number;
  exitRestingQty: number;
  exitOrderId: string;
}

export type UnfilledReason = "never_traded_that_low" | "we_pulled_it" | "traded_but_late";

export interface UnfilledRow {
  match: string;
  cat: string;
  leg: string;
  aimCents: number;
  tapeLowCents: number | null;
  tapeLowAt: string | null;
  reason: UnfilledReason;
  reasonRaw: string; // verbatim source text — bucket ③ language must stay verbatim per spec
  pulledAtET: string | null; // parsed out of "we pulled it (match went live, HH:MM AM/PM ET)"
  tradedButLateCents: number | null; // parsed out of "traded X¢ at — but our bid arrived later"
}

export type NotBidIntent = "never_reached_decision" | "intentional";

export interface NotBidRow {
  match: string;
  cat: string;
  band: string | null; // "—" in source when absent
  intent: NotBidIntent;
  plainReason: string; // "never conceived" | "aim under the lawful floor — never conceived" | "outside window" | "below volume floor"
  tapeNote: string; // always "tape: see game report" observed
}

export interface NotBidGroup {
  plainReason: string;
  count: number;
  byCategory: Record<string, number>;
  rows: NotBidRow[];
}

export interface DaySheet {
  header: DaySheetHeader;
  settled: SettledRow[];
  open: OpenRow[];
  unfilled: UnfilledRow[];
  notBid: NotBidRow[];
  notBidGrouped: NotBidGroup[];
  meta: {
    settledCountLabel: number; // "(76)" as printed in source heading
    settledRowsActual: number; // rows actually parsed (may differ — dual-leg matches)
    unfilledCountLabel: number;
    unfilledRowsActual: number;
    notBidCountLabel: number;
    notBidRowsActual: number;
    generatedAt: string;
    sourceMtimeIso: string | null;
  };
}

// ── PER-GAME PAIRS (operator's primary lens, 2026-07-16) ────────────────────
// §0A THE OPERATOR'S FRAME: "the whole game is filling BOTH sides of each
// match in Window 1 at a fair price." This groups settled/open/unfilled rows
// by `match` so every leg's fill (or aim, if unfilled) can sit beside its
// sibling leg and beside that leg's own W1-lowest-traded price. "One-sided"
// is the LIVING_VAULT's own term (§ C-SHIMIC-TRACE / pair_law_violation
// commentary: "the pair went one-sided BY CANCEL") — reused here as-is,
// never invented fresh vocabulary for something doctrine already names.

export type LegBucket = "settled" | "open" | "unfilled" | "not_bid";

export interface PairLegSlot {
  bucket: LegBucket;
  leg: string; // e.g. "Tor", "Dal"
  cat: string;
  // Our side of the trade: what we actually paid (settled/open) or would
  // have paid (unfilled aim). Null only for not_bid legs (never conceived).
  ourCents: number | null;
  ourIsAim: boolean; // true when ourCents is an aim/target, not an actual fill
  // That leg's own lowest traded price in Window 1, per THE LEG COLUMNS LAW.
  w1LowCents: number | null;
  w1LowAt: string | null;
  w1LowNote: string | null; // e.g. "no pre-bell tape" — never coerced to a number
  // Delta = ourCents - w1LowCents, in cents. Positive = we paid/aimed above
  // the leg's own best W1 print (worse); negative = at-or-below it (better).
  // Null whenever either side of the subtraction is missing.
  deltaCents: number | null;
  // Bell-source honesty, per operator point (3): render as an OPEN QUESTION,
  // never a violation verdict. "live" = tape_flow/percat_fitted/self_fill/
  // price_divergence sources; "estimated" = fallback_bell. Unknown when no
  // bell data exists at all (e.g. unfilled/not_bid legs carry none).
  bellHonesty: "live" | "estimated" | "unknown";
  realBellSource: string | null;
  outcome: SettledOutcome | null; // settled rows only
  pnlCents: number | null; // settled rows only
  reasonRaw: string | null; // unfilled/not_bid verbatim reason, kept exact
  plainReason: string | null; // not_bid plain reason, kept exact
}

export interface GamePair {
  match: string;
  carried: boolean;
  cat: string;
  legs: PairLegSlot[]; // 1 or 2 — some games print only one leg across all buckets
  // "One-sided" per doctrine's own term: only one leg has an actual fill
  // (settled or open) while the sibling is unfilled/not_bid/missing. A game
  // that never bid either leg is NOT flagged one-sided — it simply has no
  // filled legs at all and is a separate, quieter case.
  filledLegCount: number;
  isOneSided: boolean;
  isBothFilled: boolean;
}
