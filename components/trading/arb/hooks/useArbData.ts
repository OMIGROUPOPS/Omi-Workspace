"use client";

import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import type {
  ArbState,
  TradeEntry,
  TradeFilter,
  StatusFilter,
  TimeHorizon,
  TradeSortKey,
} from "../types";
import { toDateStr, todayET, formatDateLabel, formatShortDate, tradePnl, computePnl, isOpenTrade, getKL1Depth } from "../helpers";

export function useArbData() {
  const [state, setState] = useState<ArbState | null>(null);
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const [fetchError, setFetchError] = useState(false);
  const [paused, setPaused] = useState(false);
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [dateOffset, setDateOffset] = useState(0);
  const [dateAll, setDateAll] = useState(false);
  const [showAllSpreads, setShowAllSpreads] = useState(true);
  const [tradeSearch, setTradeSearch] = useState("");
  const [hiddenPositions, setHiddenPositions] = useState<Set<string>>(new Set());
  const [pnlHorizon, setPnlHorizon] = useState<TimeHorizon>("ALL");
  const [pnlSport, setPnlSport] = useState("all");
  const [tradeSortKey, setTradeSortKey] = useState<TradeSortKey>("time");
  const [tradeSortAsc, setTradeSortAsc] = useState(false);
  const [expandedTrade, setExpandedTrade] = useState<number | null>(null);
  const [expandedMonitorTrade, setExpandedMonitorTrade] = useState<number | null>(null);
  const prevPortfolioRef = useRef<{ k: number; pm: number; total: number } | null>(null);
  const [portfolioDelta, setPortfolioDelta] = useState<{ k: number; pm: number; total: number }>({ k: 0, pm: 0, total: 0 });

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("/api/arb", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setState(data);
        setLastFetch(new Date());
        setFetchError(false);
      } else {
        setFetchError(true);
      }
    } catch {
      setFetchError(true);
    }
  }, []);

  useEffect(() => {
    fetchData();
    if (paused) return;
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData, paused]);

  useEffect(() => {
    if (!state?.balances) return;
    const { k_portfolio, pm_portfolio, total_portfolio } = state.balances;
    if (total_portfolio === 0) return;
    const prev = prevPortfolioRef.current;
    if (prev && (prev.k !== k_portfolio || prev.pm !== pm_portfolio)) {
      setPortfolioDelta({
        k: k_portfolio - prev.k,
        pm: pm_portfolio - prev.pm,
        total: total_portfolio - prev.total,
      });
    }
    prevPortfolioRef.current = { k: k_portfolio, pm: pm_portfolio, total: total_portfolio };
  }, [state?.balances?.k_portfolio, state?.balances?.pm_portfolio, state?.balances?.total_portfolio]);

  const hasData = state && state.updated_at;
  const isStale = state?.updated_at && Date.now() - new Date(state.updated_at).getTime() > 60_000;

  // ── Date navigation ──
  const selectedDate = useMemo(() => {
    if (dateAll) return null;
    // Use ET for date navigation
    const d = new Date();
    d.setDate(d.getDate() + dateOffset);
    // Convert to ET date string
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
  }, [dateOffset, dateAll]);

  const dateLabel = useMemo(() => {
    if (dateAll) return "All Time";
    if (dateOffset === 0) return "Today";
    if (dateOffset === -1) return "Yesterday";
    return formatDateLabel(selectedDate || "");
  }, [dateAll, dateOffset, selectedDate]);

  // ── Spreads ──
  const sortedSpreads = useMemo(() => {
    const raw = state?.spreads || [];
    const filtered = showAllSpreads
      ? raw
      : raw.filter((s) => s.spread_buy_pm > 0 || s.spread_buy_k > 0);
    return [...filtered].sort((a, b) => {
      const aMax = Math.max(a.spread_buy_pm, a.spread_buy_k);
      const bMax = Math.max(b.spread_buy_pm, b.spread_buy_k);
      return bMax - aMax;
    });
  }, [state?.spreads, showAllSpreads]);

  // ── Trades ──
  const allTrades = useMemo(() => {
    return [...(state?.trades || [])].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [state?.trades]);

  const filteredTrades = useMemo(() => {
    let trades = allTrades;
    if (selectedDate) {
      trades = trades.filter((t) => toDateStr(t.timestamp) === selectedDate);
    }
    if (tradeFilter === "paper") {
      trades = trades.filter((t) => t.paper_mode);
    } else if (tradeFilter === "live") {
      trades = trades.filter((t) => !t.paper_mode);
    }
    if (statusFilter !== "all") {
      if (statusFilter === "DIRECTIONAL") {
        trades = trades.filter((t) =>
          t.tier === "TIER3A" || t.tier === "TIER3A_HOLD" ||
          t.tier === "TIER3_OPPOSITE_HEDGE" || t.tier === "TIER3_OPPOSITE_OVERWEIGHT"
        );
      } else {
        trades = trades.filter((t) => t.status === statusFilter);
      }
    }
    if (tradeSearch.trim()) {
      const q = tradeSearch.trim().toUpperCase();
      trades = trades.filter(
        (t) => t.team.toUpperCase().includes(q) || t.game_id.toUpperCase().includes(q)
      );
    }
    return trades;
  }, [allTrades, selectedDate, tradeFilter, statusFilter, tradeSearch]);

  const totalPnl = useMemo(() => computePnl(allTrades), [allTrades]);
  const filteredPnl = useMemo(() => computePnl(filteredTrades), [filteredTrades]);

  // ── Positions ──
  const activePositions = useMemo(() => {
    return (state?.positions || []).filter(
      (p) => p.contracts > 0 && !hiddenPositions.has(p.game_id)
    );
  }, [state?.positions, hiddenPositions]);

  const positionValues = useMemo(() => {
    const b = state?.balances;
    if (!b) return { pm: 0, kalshi: 0, total: 0, pmSource: "margin" as string };
    const pm = b.pm_positions ?? ((b.pm_portfolio ?? 0) - (b.pm_cash ?? 0));
    const kalshi = b.k_positions ?? ((b.k_portfolio ?? 0) - (b.k_cash ?? 0));
    const pmSource = b.pm_positions_source ?? "margin";
    return { pm, kalshi, total: pm + kalshi, pmSource };
  }, [state?.balances]);

  const markSettled = (gameId: string) => {
    setHiddenPositions((prev) => new Set(prev).add(gameId));
  };

  // ── P&L History data ──
  const availableSports = useMemo(() => {
    const sports = new Set<string>();
    for (const t of allTrades) {
      if (t.sport) sports.add(t.sport);
    }
    return ["all", ...Array.from(sports).sort()];
  }, [allTrades]);

  const pnlTrades = useMemo(() => {
    let trades = allTrades.filter(
      (t) =>
        !t.paper_mode &&
        (t.contracts_filled > 0 || t.status === "EXITED") &&
        (t.status === "SUCCESS" || t.status === "EXITED" || t.status === "UNHEDGED" ||
         t.tier === "TIER3A_HOLD" || t.tier === "TIER3_OPPOSITE_HEDGE" || t.tier === "TIER3_OPPOSITE_OVERWEIGHT" || t.tier === "TIER1_HEDGE") &&
        tradePnl(t).totalDollars !== null
    );
    if (pnlSport !== "all") trades = trades.filter((t) => t.sport === pnlSport);
    if (pnlHorizon !== "ALL") {
      const now = new Date();
      let cutoff: Date;
      switch (pnlHorizon) {
        case "1D": cutoff = new Date(now.getTime() - 86400000); break;
        case "1W": cutoff = new Date(now.getTime() - 7 * 86400000); break;
        case "1M": cutoff = new Date(now.getTime() - 30 * 86400000); break;
        case "YTD": cutoff = new Date(now.getFullYear(), 0, 1); break;
        default: cutoff = new Date(0);
      }
      trades = trades.filter((t) => new Date(t.timestamp).getTime() >= cutoff.getTime());
    }
    return [...trades].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [allTrades, pnlSport, pnlHorizon]);

  const pnlAllFiltered = useMemo(() => {
    let trades = allTrades.filter((t) => !t.paper_mode);
    if (pnlSport !== "all") trades = trades.filter((t) => t.sport === pnlSport);
    if (pnlHorizon !== "ALL") {
      const now = new Date();
      let cutoff: Date;
      switch (pnlHorizon) {
        case "1D": cutoff = new Date(now.getTime() - 86400000); break;
        case "1W": cutoff = new Date(now.getTime() - 7 * 86400000); break;
        case "1M": cutoff = new Date(now.getTime() - 30 * 86400000); break;
        case "YTD": cutoff = new Date(now.getFullYear(), 0, 1); break;
        default: cutoff = new Date(0);
      }
      trades = trades.filter((t) => new Date(t.timestamp).getTime() >= cutoff.getTime());
    }
    return trades;
  }, [allTrades, pnlSport, pnlHorizon]);

  const pnlSummaryStats = useMemo(() => {
    let tp = 0;
    let wins = 0;
    let losses = 0;
    let best = -Infinity;
    let worst = Infinity;
    let totalContracts = 0;
    let makerFills = 0;

    for (const t of pnlTrades) {
      const pnl = tradePnl(t);
      const net = pnl.totalDollars ?? 0;
      tp += net;
      totalContracts += pnl.qty || 1;
      if (net > 0) wins++;
      else losses++;
      if (net > best) best = net;
      if (net < worst) worst = net;
      if (t.is_maker) makerFills++;
    }

    let gtcAttempts = 0;
    let gtcFills = 0;
    for (const t of pnlAllFiltered) {
      if (t.execution_phase === "gtc") {
        gtcAttempts++;
        if (t.contracts_filled > 0) gtcFills++;
      }
    }

    const noFills = pnlAllFiltered.filter((t) => t.status.includes("NO_FILL")).length;

    return {
      totalTrades: pnlTrades.length,
      totalAttempts: pnlAllFiltered.length,
      wins,
      losses,
      winRate: pnlTrades.length > 0 ? ((wins / pnlTrades.length) * 100).toFixed(1) : "0",
      totalPnl: tp,
      avgProfit: pnlTrades.length > 0 ? tp / pnlTrades.length : 0,
      best: best === -Infinity ? 0 : best,
      worst: worst === Infinity ? 0 : worst,
      noFills,
      totalContracts,
      makerFills,
      gtcAttempts,
      gtcFills,
      gtcFillRate: gtcAttempts > 0 ? ((gtcFills / gtcAttempts) * 100).toFixed(1) : "0",
    };
  }, [pnlTrades, pnlAllFiltered]);

  const cumulativeChartData = useMemo(() => {
    let cumulative = 0;
    return pnlTrades.map((t, i) => {
      const net = tradePnl(t).totalDollars ?? 0;
      cumulative += net;
      return {
        index: i + 1,
        date: toDateStr(t.timestamp),
        time: t.timestamp,
        pnl: Number(cumulative.toFixed(4)),
        tradePnl: Number(net.toFixed(4)),
        team: t.team,
        phase: t.execution_phase || "ioc",
        isMaker: t.is_maker || false,
      };
    });
  }, [pnlTrades]);

  const scatterData = useMemo(() => {
    return pnlTrades.map((t, i) => {
      const pnl = tradePnl(t);
      return {
        index: i + 1,
        net: Number((pnl.totalDollars ?? 0).toFixed(4)),
        spread: t.spread_cents,
        team: t.team,
        contracts: pnl.qty || 1,
        phase: t.execution_phase || "ioc",
        isMaker: t.is_maker || false,
      };
    });
  }, [pnlTrades]);

  const dailyPnlData = useMemo(() => {
    const byDay: Record<string, { pnl: number; trades: number; successes: number; noFills: number; contracts: number; makerFills: number }> = {};
    for (const t of pnlAllFiltered) {
      const day = toDateStr(t.timestamp);
      if (!day) continue;
      if (!byDay[day]) byDay[day] = { pnl: 0, trades: 0, successes: 0, noFills: 0, contracts: 0, makerFills: 0 };
      byDay[day].trades++;
      const pnl = tradePnl(t);
      if (pnl.totalDollars !== null) {
        byDay[day].pnl += pnl.totalDollars;
        byDay[day].successes++;
        byDay[day].contracts += pnl.qty || 1;
        if (t.is_maker) byDay[day].makerFills++;
      }
      if (t.status.includes("NO_FILL")) byDay[day].noFills++;
    }
    return Object.entries(byDay)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, data]) => ({
        date,
        label: formatShortDate(date),
        pnl: Number(data.pnl.toFixed(4)),
        trades: data.trades,
        successes: data.successes,
        noFills: data.noFills,
        contracts: data.contracts,
        makerFills: data.makerFills,
      }));
  }, [pnlAllFiltered]);

  const fillRateStats = useMemo(() => {
    const iocAttempts = pnlAllFiltered.filter((t) => (t.execution_phase || "ioc") === "ioc").length;
    const iocFills = pnlAllFiltered.filter((t) => (t.execution_phase || "ioc") === "ioc" && t.contracts_filled > 0).length;
    const gtcAttempts = pnlAllFiltered.filter((t) => t.execution_phase === "gtc").length;
    const gtcFills = pnlAllFiltered.filter((t) => t.execution_phase === "gtc" && t.contracts_filled > 0).length;

    const spreadBuckets: Record<string, { attempts: number; fills: number }> = {};
    for (const t of pnlAllFiltered) {
      const bucket = t.spread_cents < 3 ? "<3c" : t.spread_cents < 4 ? "3-4c" : t.spread_cents < 5 ? "4-5c" : "5c+";
      if (!spreadBuckets[bucket]) spreadBuckets[bucket] = { attempts: 0, fills: 0 };
      spreadBuckets[bucket].attempts++;
      if (t.contracts_filled > 0) spreadBuckets[bucket].fills++;
    }

    const noFillReasons: Record<string, number> = {};
    for (const t of pnlAllFiltered) {
      if (t.status.includes("NO_FILL")) {
        const reason = t.gtc_cancel_reason || "ioc_expired";
        noFillReasons[reason] = (noFillReasons[reason] || 0) + 1;
      }
    }

    return {
      iocAttempts, iocFills,
      iocRate: iocAttempts > 0 ? ((iocFills / iocAttempts) * 100).toFixed(1) : "0",
      gtcAttempts, gtcFills,
      gtcRate: gtcAttempts > 0 ? ((gtcFills / gtcAttempts) * 100).toFixed(1) : "0",
      spreadBuckets,
      noFillReasons,
    };
  }, [pnlAllFiltered]);

  const sortedPnlTrades = useMemo(() => {
    const trades = [...pnlAllFiltered];
    trades.sort((a, b) => {
      let cmp = 0;
      switch (tradeSortKey) {
        case "time": cmp = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(); break;
        case "spread": cmp = a.spread_cents - b.spread_cents; break;
        case "net": { const aNet = tradePnl(a).totalDollars ?? 0; const bNet = tradePnl(b).totalDollars ?? 0; cmp = aNet - bNet; break; }
        case "qty": cmp = (a.contracts_intended || a.contracts_filled || 0) - (b.contracts_intended || b.contracts_filled || 0); break;
        case "phase": cmp = (a.execution_phase || "ioc").localeCompare(b.execution_phase || "ioc"); break;
      }
      return tradeSortAsc ? cmp : -cmp;
    });
    return trades;
  }, [pnlAllFiltered, tradeSortKey, tradeSortAsc]);

  const handleSort = (key: TradeSortKey) => {
    if (tradeSortKey === key) setTradeSortAsc(!tradeSortAsc);
    else { setTradeSortKey(key); setTradeSortAsc(false); }
  };

  const sortArrow = (key: TradeSortKey) => {
    if (tradeSortKey !== key) return "";
    return tradeSortAsc ? " \u25B2" : " \u25BC";
  };

  // ── Depth gate stats ──
  const depthGateStats = useMemo(() => {
    const etToday = todayET();
    const todaySkipped = allTrades.filter(
      (t) => t.status === "SKIPPED" && toDateStr(t.timestamp) === etToday
    );
    const depthGateSkips = todaySkipped.filter((t) =>
      (t as any).skip_reason?.includes("k_depth_gate") ||
      (t as any).abort_reason?.includes("k_depth_gate")
    ).length;

    // Unwind rates by depth bucket
    const filledTrades = allTrades.filter((t) => !t.paper_mode && t.contracts_filled > 0);
    let belowThreshold = 0, belowUnwinds = 0;
    let aboveThreshold = 0, aboveUnwinds = 0;
    for (const t of filledTrades) {
      const depth = getKL1Depth(t);
      if (depth === null) continue;
      const isUnwind = t.status === "EXITED" || t.status === "UNHEDGED";
      if (depth < 50) {
        belowThreshold++;
        if (isUnwind) belowUnwinds++;
      } else {
        aboveThreshold++;
        if (isUnwind) aboveUnwinds++;
      }
    }

    return {
      skippedToday: depthGateSkips,
      threshold: 50,
      belowThreshold,
      belowUnwindRate: belowThreshold > 0 ? ((belowUnwinds / belowThreshold) * 100).toFixed(0) : "0",
      aboveThreshold,
      aboveUnwindRate: aboveThreshold > 0 ? ((aboveUnwinds / aboveThreshold) * 100).toFixed(0) : "0",
    };
  }, [allTrades]);

  const exportCsv = useCallback(() => {
    const headers = ["Time", "Team", "Sport", "Direction", "Status", "Qty", "Spread", "Net P&L", "Phase", "Maker", "K Price", "PM Price"];
    const rows = sortedPnlTrades.map((t) => [
      t.timestamp, t.team, t.sport, t.direction, t.status,
      t.contracts_filled || 0, t.spread_cents,
      t.actual_pnl?.net_profit_dollars?.toFixed(4) ?? "",
      t.execution_phase || "ioc", t.is_maker ? "Y" : "N",
      t.k_price, t.pm_price,
    ]);
    const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `arb_trades_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [sortedPnlTrades]);

  return {
    state,
    lastFetch,
    fetchError,
    paused,
    setPaused,
    tradeFilter,
    setTradeFilter,
    statusFilter,
    setStatusFilter,
    dateOffset,
    setDateOffset,
    dateAll,
    setDateAll,
    showAllSpreads,
    setShowAllSpreads,
    tradeSearch,
    setTradeSearch,
    pnlHorizon,
    setPnlHorizon,
    pnlSport,
    setPnlSport,
    tradeSortKey,
    tradeSortAsc,
    expandedTrade,
    setExpandedTrade,
    expandedMonitorTrade,
    setExpandedMonitorTrade,
    portfolioDelta,
    hasData,
    isStale,
    selectedDate,
    dateLabel,
    sortedSpreads,
    allTrades,
    filteredTrades,
    totalPnl,
    filteredPnl,
    activePositions,
    positionValues,
    markSettled,
    availableSports,
    pnlTrades,
    pnlAllFiltered,
    pnlSummaryStats,
    cumulativeChartData,
    scatterData,
    dailyPnlData,
    fillRateStats,
    depthGateStats,
    sortedPnlTrades,
    handleSort,
    sortArrow,
    exportCsv,
    fetchData,
    hiddenPositions,
  };
}

export type ArbDataReturn = ReturnType<typeof useArbData>;
