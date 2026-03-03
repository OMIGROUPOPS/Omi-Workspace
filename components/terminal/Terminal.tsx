"use client";

// OMI Terminal — Main layout (Redesigned)
// Flex-based panel layout with live scanner data polling.
// Bloomberg-style dark terminal aesthetic.

import { useState, useEffect, useCallback, useMemo } from "react";
import Watchlist from "./Watchlist";
import Chart from "./Chart";
import Orderbook from "./Orderbook";
import Scanner from "./Scanner";
import CountdownBoard from "./CountdownBoard";
import PnL from "./PnL";
import StatusBar from "./StatusBar";
import type {
  ScanSignal,
  ScanType,
  CountdownItem,
  PnLBreakdown,
  CategoryData,
  ScannerStatusData,
  TradesResponse,
  ConnectionStatus,
  MarketInfo,
} from "@/lib/terminal/types";

// ── Polling helper ──────────────────────────────────────────

function usePolling<T>(url: string, intervalMs: number) {
  const [data, setData] = useState<T | null>(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const res = await fetch(url, { cache: "no-store" });
        if (res.ok && active) {
          setData(await res.json());
        }
      } catch {
        // Scanner offline — leave stale data
      }
    };
    poll();
    const id = setInterval(poll, intervalMs);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [url, intervalMs]);

  return data;
}

// ── Component ────────────────────────────────────────────────

export default function Terminal() {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [scanFilter, setScanFilter] = useState<ScanType | null>(null);
  const [clock, setClock] = useState("");

  // Live data polling
  const rawSignals = usePolling<ScanSignal[]>("/api/scanner/signals", 3000);
  const statusData = usePolling<ScannerStatusData>("/api/scanner/status", 5000);
  const categoriesResp = usePolling<{ categories: CategoryData[]; total_tickers: number; total_events: number }>("/api/scanner/categories", 10000);
  const tradesData = usePolling<TradesResponse>("/api/scanner/trades", 5000);

  const signals: ScanSignal[] = rawSignals ?? [];
  const categories: CategoryData[] = categoriesResp?.categories ?? [];

  // Connection status
  const connectionStatus: ConnectionStatus = statusData
    ? statusData.ws_connected
      ? "connected"
      : "disconnected"
    : "connecting";

  // 1s clock + countdown timer
  const [countdown, setCountdown] = useState<CountdownItem[]>([]);

  // Build countdown from resolution signals
  const buildCountdown = useCallback((): CountdownItem[] => {
    const now = Date.now();
    const fiveMinAgo = now - 5 * 60 * 1000;
    return signals
      .filter(
        (s) =>
          s.scan_type === "resolution" &&
          s.time_remaining &&
          (s.timestamp ?? 0) * 1000 > fiveMinAgo,
      )
      .map((s) => {
        const elapsed = (now - (s.timestamp ?? 0) * 1000) / 1000;
        const secsLeft = Math.max(0, (s.time_remaining || 0) - elapsed);
        const info: MarketInfo = {
          ticker: s.ticker,
          event_ticker: s.ticker.replace(/-[YN]$/, ""),
          game_id: s.game_id,
          market_type: "variant",
          team: s.ticker.split("-").slice(-2, -1)[0] || s.ticker.slice(-8),
          floor_strike: null,
          close_time: null,
          category: "",
        };
        return {
          ticker: s.ticker,
          info,
          price: s.entry_price,
          side: (s.entry_price >= 50 ? "near_100" : "near_0") as
            | "near_100"
            | "near_0",
          secs_to_close: Math.round(secsLeft),
          bridge_confidence: s.bridge_confidence || 0,
          sigma: s.sigma_estimate || 0,
          depth: s.depth,
          kelly_size: s.optimal_size || 0,
        };
      })
      .filter((c) => c.secs_to_close > 0)
      .slice(0, 10);
  }, [signals]);

  useEffect(() => {
    setCountdown(buildCountdown());
  }, [buildCountdown]);

  useEffect(() => {
    const tick = () => {
      setClock(
        new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        }),
      );
      setCountdown((prev) =>
        prev.map((item) => ({
          ...item,
          secs_to_close: Math.max(0, item.secs_to_close - 1),
        })),
      );
    };
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, []);

  // Build PnL breakdowns from trades data
  const pnlBreakdowns: PnLBreakdown[] = tradesData
    ? Object.values(tradesData.summary.by_strategy).map((bs) => ({
        scan_type: bs.scan_type as ScanType,
        total_pnl: bs.total_pnl,
        trade_count: bs.trade_count,
        winners: bs.winners,
        losers: bs.losers,
        avg_hold_time: bs.avg_hold_time,
        avg_edge: bs.avg_edge,
      }))
    : [];

  const totalPnl = tradesData?.summary.total_pnl ?? 0;
  const openTradeCount = tradesData?.summary.open_count ?? 0;

  // Normalize signal timestamps (API sends epoch seconds, frontend expects ms)
  const normalizedSignals: ScanSignal[] = signals.map((s) => ({
    ...s,
    timestamp:
      s.timestamp && s.timestamp < 1e12
        ? s.timestamp * 1000
        : s.timestamp ?? Date.now(),
  }));

  // Derive upcomingMarkets: tickers nearest to 0 or 100 (for CountdownBoard empty state)
  const upcomingMarkets = useMemo(() => {
    const allTickers: { ticker: string; team: string; mid: number; spread: number; category: string }[] = [];
    for (const cat of categories) {
      for (const t of cat.top_tickers) {
        if (t.mid !== null && t.mid !== undefined) {
          allTickers.push({ ticker: t.ticker, team: t.team, mid: t.mid, spread: t.spread, category: cat.category });
        }
      }
    }
    return allTickers
      .sort((a, b) => Math.min(a.mid, 100 - a.mid) - Math.min(b.mid, 100 - b.mid))
      .slice(0, 10);
  }, [categories]);

  // Derive recentActivity: latest 8 signals for PnL activity feed
  const recentActivity = useMemo(() => {
    return normalizedSignals.slice(0, 8).map((s) => ({
      scan_type: s.scan_type,
      ticker: s.ticker,
      severity: s.severity,
      description: s.description,
      timestamp: s.timestamp,
    }));
  }, [normalizedSignals]);

  return (
    <div
      className="h-full w-full bg-[#0a0a0a] text-slate-200 flex flex-col overflow-hidden"
      style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}
    >
      {/* ── Top bar — Bloomberg-style header ── */}
      <div
        className="flex items-center justify-between px-4 shrink-0"
        style={{
          height: "30px",
          background: "linear-gradient(180deg, #111 0%, #0d0d0d 100%)",
          borderBottom: "1px solid #1a1a1a",
        }}
      >
        <div className="flex items-center gap-3">
          <span
            style={{
              color: "#FF6600",
              fontWeight: 800,
              fontSize: "14px",
              letterSpacing: "0.12em",
              textShadow: "0 0 12px rgba(255,102,0,0.3)",
            }}
          >
            OMI
          </span>
          <span
            style={{
              color: "#666",
              fontSize: "11px",
              letterSpacing: "0.15em",
              fontWeight: 500,
            }}
          >
            TERMINAL
          </span>
          <span style={{ color: "#333", fontSize: "9px" }}>v0.3</span>
        </div>
        <div className="flex items-center gap-4" style={{ fontSize: "10px" }}>
          <span style={{ color: "#555", fontVariantNumeric: "tabular-nums" }}>
            {new Date().toISOString().slice(0, 10)}
          </span>
          <span style={{ color: "#666", fontVariantNumeric: "tabular-nums", fontWeight: 600 }} suppressHydrationWarning>
            {clock}
          </span>
          <span
            style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              color:
                connectionStatus === "connected" ? "#00FF88" : connectionStatus === "connecting" ? "#FFD600" : "#FF3366",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background:
                  connectionStatus === "connected"
                    ? "#00FF88"
                    : connectionStatus === "connecting"
                      ? "#FFD600"
                      : "#FF3366",
                boxShadow:
                  connectionStatus === "connected"
                    ? "0 0 8px rgba(0,255,136,0.5)"
                    : "none",
                animation:
                  connectionStatus === "connected"
                    ? "terminal-pulse 2s ease-in-out infinite"
                    : connectionStatus === "connecting"
                      ? "terminal-pulse 0.8s ease-in-out infinite"
                      : "none",
              }}
            />
            <span style={{ fontWeight: 600, letterSpacing: "0.05em", fontSize: "9px" }}>
              {connectionStatus === "connected"
                ? "LIVE"
                : connectionStatus === "connecting"
                  ? "CONNECTING"
                  : "OFFLINE"}
            </span>
          </span>
        </div>
      </div>

      {/* ── Main content area ── */}
      <div
        style={{ flex: 1, display: "flex", minHeight: 0, overflow: "hidden" }}
      >
        {/* ── Watchlist sidebar ── */}
        <div
          style={{
            width: "175px",
            flexShrink: 0,
            background: "#0d0d0d",
            borderRight: "1px solid #1a1a1a",
            padding: "6px",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Watchlist
            categories={categories}
            selectedTicker={selectedTicker ?? undefined}
            onSelect={setSelectedTicker}
          />
        </div>

        {/* ── Center + Right panels ── */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            minWidth: 0,
            minHeight: 0,
          }}
        >
          {/* ── Top row: Chart + Orderbook — capped at 350px ── */}
          <div
            style={{
              flex: "0 1 350px",
              maxHeight: "350px",
              display: "flex",
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            {/* Chart */}
            <div
              style={{
                flex: 1,
                background: "#0d0d0d",
                borderBottom: "1px solid #1a1a1a",
                borderRight: "1px solid #1a1a1a",
                padding: "6px",
                overflow: "hidden",
                minWidth: 0,
                minHeight: 0,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <Chart ticker={selectedTicker ?? undefined} />
            </div>

            {/* Orderbook */}
            <div
              style={{
                width: "210px",
                flexShrink: 0,
                background: "#0d0d0d",
                borderBottom: "1px solid #1a1a1a",
                padding: "6px",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <Orderbook ticker={selectedTicker ?? undefined} />
            </div>
          </div>

          {/* ── Bottom row: Scanner + Countdown + P&L — takes remaining space ── */}
          <div
            style={{
              flex: 1,
              display: "flex",
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            {/* Scanner */}
            <div
              style={{
                flex: 5,
                background: "#0d0d0d",
                borderRight: "1px solid #1a1a1a",
                padding: "6px",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                minWidth: 0,
              }}
            >
              <Scanner
                signals={normalizedSignals}
                filter={scanFilter}
                onFilterChange={setScanFilter}
              />
            </div>

            {/* Countdown */}
            <div
              style={{
                flex: 3,
                background: "#0d0d0d",
                borderRight: "1px solid #1a1a1a",
                padding: "6px",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                minWidth: 0,
              }}
            >
              <CountdownBoard items={countdown} onSelect={setSelectedTicker} upcomingMarkets={upcomingMarkets} />
            </div>

            {/* P&L */}
            <div
              style={{
                flex: 3,
                background: "#0d0d0d",
                padding: "6px",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                minWidth: 0,
              }}
            >
              <PnL
                totalPnl={totalPnl}
                breakdowns={pnlBreakdowns}
                openTrades={openTradeCount}
                signalCount={statusData?.scan_signals}
                categoryCount={categories.length}
                recentActivity={recentActivity}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ── Status bar ── */}
      <StatusBar
        status={connectionStatus}
        tickerCount={statusData?.tickers_count ?? 0}
        openTrades={openTradeCount}
        balance={460}
        signalCount={statusData?.scan_signals}
        uptime={statusData?.uptime}
      />
    </div>
  );
}
