import type { TradeEntry } from "./types";

// ── Spread colors ───────────────────────────────────────────────────────────

export function spreadColor(cents: number): string {
  if (cents >= 5) return "text-emerald-400";
  if (cents >= 3) return "text-yellow-400";
  if (cents > 0) return "text-gray-400";
  return "text-red-400";
}

export function spreadBg(cents: number): string {
  if (cents >= 5) return "bg-emerald-500/10";
  if (cents >= 3) return "bg-yellow-500/10";
  return "";
}

export function netColor(cents: number | null | undefined): string {
  if (cents == null) return "text-gray-500";
  if (cents > 0) return "text-emerald-400";
  if (cents < 0) return "text-red-400";
  return "text-gray-400";
}

// ── Status / Sport badges ───────────────────────────────────────────────────

export function statusBadge(status: string, tier?: string): { bg: string; text: string; label: string; tooltip: string } {
  const t = tier || status;
  // Pure arb success
  if (t === "SUCCESS" || status === "SUCCESS")
    return { bg: "bg-emerald-500/20", text: "text-emerald-400", label: "ARB ✓", tooltip: "Both sides filled — guaranteed profit locked" };
  if (t === "TIER1_HEDGE")
    return { bg: "bg-emerald-500/20", text: "text-emerald-300", label: "HEDGE ✓", tooltip: "Delayed hedge filled — position now hedged" };
  // Exits and unwinds
  if (t === "TIER2_EXIT" || status === "EXITED")
    return { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "EXITED", tooltip: "PM filled, K failed — PM position unwound to exit" };
  if (t === "TIER3_UNWIND")
    return { bg: "bg-orange-500/20", text: "text-orange-400", label: "UNWOUND", tooltip: "Unhedged position unwound on PM — realized loss/gain from spread" };
  // Directional risk (Tier 3)
  if (t === "TIER3A" || t === "TIER3A_HOLD")
    return { bg: "bg-purple-500/20", text: "text-purple-400", label: "DIRECTIONAL", tooltip: "OMI signal hold — unhedged directional bet, not risk-free" };
  if (t === "TIER3_OPPOSITE_HEDGE")
    return { bg: "bg-blue-500/20", text: "text-blue-400", label: "OPP HEDGE", tooltip: "Opposite-side hedge — bought both teams across platforms" };
  if (t === "TIER3_OPPOSITE_OVERWEIGHT")
    return { bg: "bg-cyan-500/20", text: "text-cyan-400", label: "OPP OVER", tooltip: "Overweight opposite — extra contracts on opposing team" };
  // No fills
  if (status === "PM_NO_FILL" || status.includes("NO_FILL"))
    return { bg: "bg-gray-500/20", text: "text-gray-400", label: "NO FILL", tooltip: "PM order sent but didn't fill — no position taken" };
  // Unhedged
  if (status === "UNHEDGED")
    return { bg: "bg-red-500/20", text: "text-red-400", label: "UNHEDGED", tooltip: "PM filled but Kalshi didn't — directional risk exposure" };
  // Recovery
  if (status === "RECOVERED")
    return { bg: "bg-emerald-500/20", text: "text-emerald-300", label: "RECOVERED", tooltip: "Previously unhedged position was hedged on retry" };
  // Paper
  if (status === "PAPER" || status === "PAPER_SUCCESS")
    return { bg: "bg-gray-500/20", text: "text-gray-500", label: "PAPER", tooltip: "Simulated trade — no real money" };
  // Skipped
  if (status === "SKIPPED")
    return { bg: "bg-gray-500/20", text: "text-gray-400", label: "SKIPPED", tooltip: "Trade opportunity skipped by executor" };
  // Fallback
  return { bg: "bg-gray-500/20", text: "text-gray-400", label: status, tooltip: status };
}

export function sportBadge(sport: string): string {
  switch (sport) {
    case "NBA":
      return "bg-orange-500/20 text-orange-400";
    case "CBB":
      return "bg-blue-500/20 text-blue-400";
    case "NHL":
      return "bg-cyan-500/20 text-cyan-400";
    case "UFC":
      return "bg-red-500/20 text-red-400";
    default:
      return "bg-gray-500/20 text-gray-400";
  }
}

export function sportChartColor(sport: string): string {
  switch (sport) {
    case "NBA": return "#f97316"; // orange
    case "CBB": return "#3b82f6"; // blue
    case "NHL": return "#06b6d4"; // cyan
    case "UFC": return "#ef4444"; // red
    default:    return "#6b7280"; // gray
  }
}

// ── Time formatting ─────────────────────────────────────────────────────────

export function timeAgo(iso: string): string {
  if (!iso) return "never";
  const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
  const diff = Date.now() - new Date(s).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 0) return "just now";
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export function formatUptime(seconds: number): string {
  if (!seconds) return "0s";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export function formatDateTime(iso: string): string {
  if (!iso) return "-";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    const d = new Date(s);
    const mon = d.toLocaleString("en-US", { month: "short", timeZone: "America/New_York" });
    const day = Number(new Intl.DateTimeFormat("en-US", { day: "numeric", timeZone: "America/New_York" }).format(d));
    const time = d.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
      timeZone: "America/New_York",
    });
    return `${mon} ${day} ${time} EST`;
  } catch {
    return iso;
  }
}

export function formatTimeOnly(iso: string): string {
  if (!iso) return "";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    const d = new Date(s);
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    return "";
  }
}

export function formatTimeHM(iso: string): string {
  if (!iso) return "";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    const d = new Date(s);
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return "";
  }
}

/** Convert a UTC timestamp to YYYY-MM-DD in US Eastern Time. */
export function toETDate(utcTimestamp: string): string {
  if (!utcTimestamp) return "";
  try {
    const s = utcTimestamp.endsWith("Z") || utcTimestamp.includes("+") ? utcTimestamp : utcTimestamp + "Z";
    const d = new Date(s);
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/New_York",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(d);
    const y = parts.find((p) => p.type === "year")?.value ?? "";
    const m = parts.find((p) => p.type === "month")?.value ?? "";
    const day = parts.find((p) => p.type === "day")?.value ?? "";
    return `${y}-${m}-${day}`;
  } catch {
    return "";
  }
}

/** Get today's date as YYYY-MM-DD in US Eastern Time. */
export function todayET(): string {
  return toETDate(new Date().toISOString());
}

export function isToday(dateStr: string | undefined): boolean {
  if (!dateStr) return false;
  return dateStr === todayET();
}

/** Convert ISO timestamp to YYYY-MM-DD (ET). All date grouping uses Eastern Time. */
export function toDateStr(iso: string): string {
  return toETDate(iso);
}

/** Extract L1 depth at arb price from depth_walk_log[0]. */
export function getL1Depth(t: TradeEntry): { k: number | null; pm: number | null } {
  const log = t.sizing_details?.depth_walk_log;
  if (log && log.length > 0) {
    return { k: log[0].k_remaining ?? null, pm: log[0].pm_remaining ?? null };
  }
  return { k: null, pm: null };
}

/** Backward-compat: returns just K L1 depth. */
export function getKL1Depth(t: TradeEntry): number | null {
  return getL1Depth(t).k;
}

/** Color class for depth value (red < 50, yellow 50-199, green >= 200). */
export function depthColor(depth: number | null): string {
  if (depth === null) return "text-gray-600";
  if (depth < 50) return "text-red-400";
  if (depth < 200) return "text-yellow-400";
  return "text-emerald-400";
}

/** @deprecated Use depthColor */
export const kDepthColor = depthColor;

/** Format number with commas. */
export function fmtNum(n: number): string {
  return n.toLocaleString("en-US");
}

export function formatDateLabel(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr + "T12:00:00Z");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
}

export function formatShortDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr + "T12:00:00Z");
    return d.toLocaleDateString("en-US", { month: "numeric", day: "numeric" });
  } catch {
    return dateStr;
  }
}

export function mappingsHealthColor(iso: string): string {
  if (!iso) return "bg-gray-500";
  const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
  const hours = (Date.now() - new Date(s).getTime()) / 3600000;
  if (hours < 3) return "bg-emerald-500";
  if (hours < 6) return "bg-yellow-500";
  return "bg-red-500";
}

// ── Trade P&L ───────────────────────────────────────────────────────────────

export function isOpenTrade(t: TradeEntry): boolean {
  const tier = t.tier || "";
  if (tier === "TIER3A_HOLD" || tier === "TIER3_OPPOSITE_HEDGE" || tier === "TIER3_OPPOSITE_OVERWEIGHT") return true;
  if (t.status === "UNHEDGED" && tier !== "TIER3_UNWIND") return true;
  return false;
}

/** Compute signed unwind P&L in dollars. Returns null if insufficient data. */
function _computeUnwindPnl(t: TradeEntry, qty: number): number | null {
  // Priority 1: New signed field (total cents, positive=profit)
  if (t.unwind_pnl_cents != null) {
    return t.unwind_pnl_cents / 100;
  }
  // Priority 2: Recompute from direction + pm_price + unwind_fill_price
  if (t.unwind_fill_price != null && t.pm_price > 0 && qty > 0) {
    if (t.direction === "BUY_PM_SELL_K") {
      return ((t.unwind_fill_price * 100) - t.pm_price) * qty / 100;
    } else {
      return (t.pm_price - (t.unwind_fill_price * 100)) * qty / 100;
    }
  }
  // Priority 3: Old unsigned field (always treated as loss)
  if (t.unwind_loss_cents != null && t.unwind_loss_cents !== 0) {
    return -(Math.abs(t.unwind_loss_cents) / 100);
  }
  return null;
}

export function tradePnl(t: TradeEntry): {
  perContract: number | null;
  totalDollars: number | null;
  qty: number;
  isOpen: boolean;
  spreadCents: number | null;
} {
  const qty = t.contracts_filled > 0 ? t.contracts_filled : (t.contracts_intended || 0);
  const spreadCents = t.spread_cents ?? null;

  // Priority 1: reconciled_pnl (cash_ledger.py ground truth)
  if (t.reconciled_pnl != null) {
    const rp = t.reconciled_pnl;
    const pc = qty > 0 ? (rp * 100) / qty : rp * 100;
    return { perContract: pc, totalDollars: rp, qty, isOpen: false, spreadCents };
  }

  // Priority 2: settlement_pnl (kalshi_reconciler)
  if (t.settlement_pnl != null) {
    const pc = qty > 0 ? (t.settlement_pnl * 100) / qty : t.settlement_pnl * 100;
    return { perContract: pc, totalDollars: t.settlement_pnl, qty, isOpen: false, spreadCents };
  }

  // Priority 3: arb_net_total_cents (post-unwind locked P&L)
  const arbNet = (t as any).arb_net_total_cents;
  if (arbNet != null) {
    const totalDollars = arbNet / 100;
    const pc = qty > 0 ? arbNet / qty : arbNet;
    return { perContract: pc, totalDollars, qty, isOpen: false, spreadCents };
  }

  if (isOpenTrade(t)) {
    return { perContract: null, totalDollars: null, qty, isOpen: true, spreadCents };
  }

  if (t.status === "EXITED" || t.tier === "TIER3_UNWIND") {
    const pnl = _computeUnwindPnl(t, qty);
    if (pnl !== null) {
      const pc = qty > 0 ? (pnl * 100) / qty : pnl * 100;
      return { perContract: pc, totalDollars: pnl, qty, isOpen: false, spreadCents };
    }
    return { perContract: null, totalDollars: null, qty, isOpen: false, spreadCents };
  }

  if (t.status === "SUCCESS" || t.tier === "TIER1_HEDGE") {
    if (t.actual_pnl) {
      return {
        perContract: t.actual_pnl.per_contract.net,
        totalDollars: t.actual_pnl.net_profit_dollars,
        qty,
        isOpen: false,
        spreadCents,
      };
    }
    if (t.estimated_net_profit_cents != null) {
      const pc = t.estimated_net_profit_cents;
      return { perContract: pc, totalDollars: (pc * qty) / 100, qty, isOpen: false, spreadCents };
    }
  }

  if (t.tier === "TIER2_EXIT") {
    if (t.actual_pnl) {
      return {
        perContract: t.actual_pnl.per_contract.net,
        totalDollars: t.actual_pnl.net_profit_dollars,
        qty,
        isOpen: false,
        spreadCents,
      };
    }
    const pnl = _computeUnwindPnl(t, qty);
    if (pnl !== null) {
      const pc = qty > 0 ? (pnl * 100) / qty : pnl * 100;
      return { perContract: pc, totalDollars: pnl, qty, isOpen: false, spreadCents };
    }
  }

  return { perContract: null, totalDollars: null, qty, isOpen: false, spreadCents };
}

export function computePnl(trades: TradeEntry[]) {
  let arbPnl = 0;
  let exitedPnl = 0;
  let directionalPnl = 0;
  let successes = 0;
  let fills = 0;
  let openCount = 0;
  let realizedWins = 0;
  let realizedLosses = 0;
  let dirCount = 0;
  let totalFees = 0;

  for (const t of trades) {
    if (t.status === "SUCCESS") successes++;
    if (t.contracts_filled > 0) fills++;

    // Track fees
    totalFees += (t.pm_fee || 0) + (t.k_fee || 0);

    // Use tradePnl() for ALL trades — single priority chain:
    // reconciled_pnl > settlement_pnl > actual_pnl > estimated
    const pnl = tradePnl(t);

    if (pnl.isOpen) {
      openCount++;
      continue;
    }

    if (pnl.totalDollars == null) continue;

    // Categorize by status for breakdown
    if (t.status === "EXITED") {
      exitedPnl += pnl.totalDollars;
    } else if (isOpenTrade(t)) {
      // "Open" trade that has settlement/reconciled P&L (settled directional)
      directionalPnl += pnl.totalDollars;
      dirCount++;
    } else {
      arbPnl += pnl.totalDollars;
    }

    if (pnl.totalDollars >= 0) realizedWins++;
    else realizedLosses++;
  }

  const netTotal = arbPnl + exitedPnl + directionalPnl;
  return {
    arbPnl,
    exitedPnl,
    directionalPnl,
    netTotal,
    successes,
    fills,
    count: trades.length,
    openCount,
    realizedWins,
    realizedLosses,
    dirCount,
    totalFees,
  };
}
