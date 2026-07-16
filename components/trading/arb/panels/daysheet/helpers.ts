// ── Day Sheet formatting + derived-value helpers ────────────────────────────

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
