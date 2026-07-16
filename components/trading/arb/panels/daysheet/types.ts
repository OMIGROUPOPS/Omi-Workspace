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
