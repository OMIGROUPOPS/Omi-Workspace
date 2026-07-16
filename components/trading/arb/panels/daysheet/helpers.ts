// ── Day Sheet formatting + derived-value helpers ────────────────────────────

import type {
  DaySheet,
  GamePair,
  NotBidRow,
  OpenRow,
  PairLegSlot,
  SettledRow,
  UnfilledRow,
} from "./types";

export function fmtCents(c: number | null | undefined): string {
  if (c == null || Number.isNaN(c)) return "—";
  return `${c}¢`;
}

export function fmtSignedCents(c: number | null | undefined): string {
  if (c == null || Number.isNaN(c)) return "—";
  return `${c >= 0 ? "+" : ""}${c}¢`;
}

export function fmtDollarsFromCents(c: number): string {
  const dollars = c / 100;
  return `${dollars >= 0 ? "+" : "-"}$${Math.abs(dollars).toFixed(2)}`;
}

export function fmtSignedDollars(d: number): string {
  return `${d >= 0 ? "+" : "-"}$${Math.abs(d).toFixed(2)}`;
}

export function catBadgeColor(cat: string): string {
  // Distinct low-saturation badge colors per category, consistent with the
  // shell's existing sportBadge() convention (bg/10 + text/border same hue).
  const map: Record<string, string> = {
    ATP_MAIN: "bg-[#00bfff]/10 text-[#00bfff] border border-[#00bfff]/30",
    ATP_CHALL: "bg-[#00bfff]/10 text-[#7dd3fc] border border-[#00bfff]/20",
    WTA_MAIN: "bg-[#8b5cf6]/10 text-[#8b5cf6] border border-[#8b5cf6]/30",
    WTA_CHALL: "bg-[#8b5cf6]/10 text-[#c4b5fd] border border-[#8b5cf6]/20",
    ITF_M: "bg-[#ff8c00]/10 text-[#ff8c00] border border-[#ff8c00]/30",
    ITF_W: "bg-[#ff8c00]/10 text-[#ffb454] border border-[#ff8c00]/20",
  };
  return map[cat] ?? "bg-white/10 text-white border border-white/20";
}

/** Parse "HH:MM AM|PM" into minutes since local midnight for a single-day axis. */
export function toMinutes(t: string): number | null {
  const m = t.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
  if (!m) return null;
  let h = parseInt(m[1], 10) % 12;
  const min = parseInt(m[2], 10);
  if (m[3].toUpperCase() === "PM") h += 12;
  return h * 60 + min;
}

export interface GlyphPoint {
  key: "placed" | "filled" | "bell" | "close";
  label: string;
  minutes: number | null;
  color: string;
}

/**
 * Builds the 4-point timeline for a settled row: placed -> filled -> bell -> close.
 * Points are ordered chronologically as given by the source, NOT re-sorted by
 * time-of-day, because the day sheet spans a rolling 24h window (◐carried rows
 * can start "yesterday" and settle "today") where naive minute-of-day sorting
 * would misorder events that cross midnight.
 */
export function buildTimelinePoints(row: {
  placedET: string;
  filledET: string;
  realBell: string;
  closeLabel: string;
}): GlyphPoint[] {
  const closeTimeMatch = row.closeLabel.match(/(\d{1,2}:\d{2} [AP]M)/);
  const closeMinutes = closeTimeMatch ? toMinutes(closeTimeMatch[1]) : null;

  return [
    { key: "placed", label: row.placedET, minutes: toMinutes(row.placedET), color: "#7aa8d6" },
    { key: "filled", label: row.filledET, minutes: toMinutes(row.filledET), color: "#00ff88" },
    { key: "bell", label: row.realBell || "—", minutes: row.realBell ? toMinutes(row.realBell) : null, color: "#ff8c00" },
    { key: "close", label: closeTimeMatch ? closeTimeMatch[1] : "OPEN", minutes: closeMinutes, color: "#ffffff" },
  ];
}

// ── PER-GAME PAIRS grouping (operator's primary lens) ───────────────────────
// Bell-source honesty classification per operator point (3): render as an
// open question, never a violation verdict. C-TAPE-BELL v1 names tape_flow as
// the evidence-grade gun source; percat_fitted/self_fill/price_divergence are
// treated as live-fired-equivalent because each reflects an observed event
// (a fit against the category's own live prints, a self-fill instant, or a
// detected price divergence) rather than a schedule-clock guess. Only
// fallback_bell is the schedule-guess path (LIVING_VAULT line 76: "the tape
// remains the only start-time source" — fallback fires when the tape hasn't
// spoken yet). This mapping is a rendering convenience, not itself doctrine —
// it should be revisited if CC's OS-log wiring defines bell-source classes
// more precisely.
function classifyBellHonesty(source: string | null | undefined): "live" | "estimated" | "unknown" {
  if (!source) return "unknown";
  if (source === "fallback_bell") return "estimated";
  if (source === "no_bell_yet") return "unknown";
  return "live"; // percat_fitted | self_fill | tape_flow | price_divergence
}

function legFromSettled(r: SettledRow): PairLegSlot {
  const bellHonesty = classifyBellHonesty(r.realBellSource);
  const deltaCents = r.w1BestCents != null ? r.fillCents - r.w1BestCents : null;
  return {
    bucket: "settled",
    leg: r.leg,
    cat: r.cat,
    ourCents: r.fillCents,
    ourIsAim: false,
    w1LowCents: r.w1BestCents,
    w1LowAt: r.w1BestCents != null ? r.w1BestAt : null,
    w1LowNote: r.w1BestNote,
    deltaCents,
    bellHonesty,
    realBellSource: r.realBellSource || null,
    outcome: r.outcome,
    pnlCents: r.pnlCents,
    reasonRaw: null,
    plainReason: null,
  };
}

function legFromOpen(r: OpenRow): PairLegSlot {
  const bellHonesty = classifyBellHonesty(r.realBellSource);
  const deltaCents = r.w1BestCents != null ? r.fillCents - r.w1BestCents : null;
  return {
    bucket: "open",
    leg: r.leg,
    cat: r.cat,
    ourCents: r.fillCents,
    ourIsAim: false,
    w1LowCents: r.w1BestCents,
    w1LowAt: r.w1BestCents != null ? r.w1BestAt : null,
    w1LowNote: r.w1BestNote,
    deltaCents,
    bellHonesty,
    realBellSource: r.realBellSource || null,
    outcome: null,
    pnlCents: null,
    reasonRaw: null,
    plainReason: null,
  };
}

function legFromUnfilled(r: UnfilledRow): PairLegSlot {
  const deltaCents = r.tapeLowCents != null ? r.aimCents - r.tapeLowCents : null;
  return {
    bucket: "unfilled",
    leg: r.leg,
    cat: r.cat,
    ourCents: r.aimCents,
    ourIsAim: true,
    w1LowCents: r.tapeLowCents,
    w1LowAt: r.tapeLowAt,
    w1LowNote: r.tapeLowCents == null ? "never traded" : null,
    deltaCents,
    bellHonesty: "unknown", // unfilled rows carry no bell field in the source
    realBellSource: null,
    outcome: null,
    pnlCents: null,
    reasonRaw: r.reasonRaw,
    plainReason: null,
  };
}

function legFromNotBid(r: NotBidRow): PairLegSlot {
  return {
    bucket: "not_bid",
    leg: r.band ?? "—", // NotBidRow has no dedicated leg field; band/plainReason carry context
    cat: r.cat,
    ourCents: null,
    ourIsAim: false,
    w1LowCents: null,
    w1LowAt: null,
    w1LowNote: null,
    deltaCents: null,
    bellHonesty: "unknown",
    realBellSource: null,
    outcome: null,
    pnlCents: null,
    reasonRaw: null,
    plainReason: r.plainReason,
  };
}

/**
 * Groups all four buckets by `match` into PER-GAME PAIRS — the operator's
 * primary lens (§0A: "the whole game is filling BOTH sides of each match in
 * Window 1 at a fair price"). NotBid rows carry no per-leg identity in the
 * source (no `leg` column — see types.ts NotBidRow), so a not_bid row can
 * only contribute a game-level placeholder slot, never a named leg; it is
 * included so a game that never bid either side still appears in the pairs
 * view rather than silently vanishing.
 */
export function buildGamePairs(sheet: Pick<DaySheet, "settled" | "open" | "unfilled" | "notBid">): GamePair[] {
  const byMatch = new Map<string, GamePair>();

  const ensure = (match: string, carried: boolean, cat: string): GamePair => {
    let g = byMatch.get(match);
    if (!g) {
      g = { match, carried, cat, legs: [], filledLegCount: 0, isOneSided: false, isBothFilled: false };
      byMatch.set(match, g);
    }
    return g;
  };

  for (const r of sheet.settled) ensure(r.match, r.carried, r.cat).legs.push(legFromSettled(r));
  for (const r of sheet.open) ensure(r.match, r.carried, r.cat).legs.push(legFromOpen(r));
  for (const r of sheet.unfilled) ensure(r.match, false, r.cat).legs.push(legFromUnfilled(r));
  for (const r of sheet.notBid) {
    const g = ensure(r.match, false, r.cat);
    // Only attach a not_bid placeholder if this game has no legs yet at all —
    // if a sibling leg already filled/opened/went unfilled, the not_bid row
    // for the OTHER leg still deserves its own slot (true one-sidedness).
    g.legs.push(legFromNotBid(r));
  }

  for (const g of byMatch.values()) {
    const filled = g.legs.filter((l) => l.bucket === "settled" || l.bucket === "open");
    g.filledLegCount = filled.length;
    // One-sided per doctrine's own term: exactly one leg has an actual fill
    // while at least one other leg slot exists (unfilled/not_bid/missing) and
    // is NOT itself filled. A single-leg game with nothing else recorded is
    // still one-sided if that leg filled — the sibling simply never appears
    // in ANY bucket, which is itself the one-sidedness (cancel-stranded class
    // named at LIVING_VAULT §C-SHIMIC-TRACE: "cancel-made one-sidedness is
    // invisible to the fill-instant stamp" — this view surfaces it instead).
    g.isBothFilled = filled.length >= 2;
    g.isOneSided = filled.length === 1;
  }

  return Array.from(byMatch.values()).sort((a, b) => a.match.localeCompare(b.match));
}
