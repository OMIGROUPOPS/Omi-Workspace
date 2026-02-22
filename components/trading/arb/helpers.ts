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

export function statusBadge(status: string): { bg: string; text: string } {
  if (status === "HEDGED" || status === "FILLED" || status === "SUCCESS")
    return { bg: "bg-emerald-500/20", text: "text-emerald-400" };
  if (status.includes("NO_FILL") || status === "EXITED")
    return { bg: "bg-yellow-500/20", text: "text-yellow-400" };
  if (status === "FAILED" || status === "ERROR" || status === "UNHEDGED")
    return { bg: "bg-red-500/20", text: "text-red-400" };
  if (status === "SKIPPED")
    return { bg: "bg-gray-500/20", text: "text-gray-400" };
  return { bg: "bg-gray-500/20", text: "text-gray-400" };
}

export function sportBadge(sport: string): string {
  switch (sport) {
    case "NBA":
      return "bg-orange-500/20 text-orange-400";
    case "CBB":
      return "bg-blue-500/20 text-blue-400";
    case "NHL":
      return "bg-cyan-500/20 text-cyan-400";
    default:
      return "bg-gray-500/20 text-gray-400";
  }
}

export function sportChartColor(sport: string): string {
  switch (sport) {
    case "NBA": return "#f97316"; // orange
    case "CBB": return "#3b82f6"; // blue
    case "NHL": return "#06b6d4"; // cyan
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
    const mon = d.toLocaleString("en-US", { month: "short" });
    const day = d.getDate();
    const time = d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    return `${mon} ${day} ${time}`;
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

export function isToday(dateStr: string | undefined): boolean {
  if (!dateStr) return false;
  const today = new Date().toISOString().slice(0, 10);
  return dateStr === today;
}

export function toDateStr(iso: string): string {
  if (!iso) return "";
  try {
    const s = iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z";
    return new Date(s).toISOString().slice(0, 10);
  } catch {
    return "";
  }
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

export function tradePnl(t: TradeEntry): {
  perContract: number | null;
  totalDollars: number | null;
  qty: number;
  isOpen: boolean;
  spreadCents: number | null;
} {
  const qty = t.contracts_filled > 0 ? t.contracts_filled : (t.contracts_intended || 0);
  const spreadCents = t.spread_cents ?? null;

  if (t.settlement_pnl != null) {
    const pc = qty > 0 ? (t.settlement_pnl * 100) / qty : t.settlement_pnl * 100;
    return { perContract: pc, totalDollars: t.settlement_pnl, qty, isOpen: false, spreadCents };
  }

  if (isOpenTrade(t)) {
    return { perContract: null, totalDollars: null, qty, isOpen: true, spreadCents };
  }

  if (t.status === "EXITED" || t.tier === "TIER3_UNWIND") {
    if (t.unwind_loss_cents != null && t.unwind_loss_cents !== 0) {
      const totalLoss = Math.abs(t.unwind_loss_cents);
      const perContract = qty > 0 ? -(totalLoss / qty) : -totalLoss;
      return { perContract, totalDollars: -(totalLoss / 100), qty, isOpen: false, spreadCents };
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
    if (t.unwind_loss_cents != null) {
      const totalLoss = Math.abs(t.unwind_loss_cents);
      const perContract = qty > 0 ? -(totalLoss / qty) : -totalLoss;
      return { perContract, totalDollars: -(totalLoss / 100), qty, isOpen: false, spreadCents };
    }
  }

  return { perContract: null, totalDollars: null, qty, isOpen: false, spreadCents };
}

export function computePnl(trades: TradeEntry[]) {
  let arbPnl = 0;
  let exitedLoss = 0;
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
    const qty = t.contracts_filled > 0 ? t.contracts_filled : (t.contracts_intended || 0);

    // Track fees
    totalFees += (t.pm_fee || 0) + (t.k_fee || 0);

    if (isOpenTrade(t)) {
      const sp = t.settlement_pnl != null ? parseFloat(String(t.settlement_pnl)) : NaN;
      if (!isNaN(sp)) {
        directionalPnl += sp;
        dirCount++;
        if (sp >= 0) realizedWins++;
        else realizedLosses++;
      } else {
        openCount++;
      }
      continue;
    }

    if (t.status === "SUCCESS") {
      const sp = t.settlement_pnl != null ? parseFloat(String(t.settlement_pnl)) : NaN;
      if (!isNaN(sp)) {
        arbPnl += sp;
        if (sp >= 0) realizedWins++;
        else realizedLosses++;
      } else if (t.spread_cents != null && qty > 0) {
        const pnlDollars = (t.spread_cents * qty) / 100;
        arbPnl += pnlDollars;
        if (pnlDollars >= 0) realizedWins++;
        else realizedLosses++;
      }
      continue;
    }

    if (t.status === "EXITED") {
      const sp = t.settlement_pnl != null ? parseFloat(String(t.settlement_pnl)) : NaN;
      if (!isNaN(sp)) {
        exitedLoss += sp;
        if (sp < 0) realizedLosses++;
        else realizedWins++;
      } else if (t.unwind_loss_cents != null && t.unwind_loss_cents !== 0) {
        const lossDollars = -(Math.abs(t.unwind_loss_cents) / 100);
        exitedLoss += lossDollars;
        realizedLosses++;
      }
      continue;
    }
  }

  const netTotal = arbPnl + exitedLoss + directionalPnl;
  return {
    arbPnl,
    exitedLoss,
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
