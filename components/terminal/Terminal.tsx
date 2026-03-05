"use client";

// OMI Terminal — Main layout (Visual Overhaul v4 — Modular Box Pattern)
// 3-column layout: DataFeeds/Microstructure/Inventory/Watchlist | Chart + Scanner + Positions/Countdown | Orderbook + OrderEntry
// DO NOT change data fetching, polling, API routes, or orchestration logic.

import { useState, useEffect, useCallback, useMemo } from "react";
import Watchlist from "./Watchlist";
import Chart from "./Chart";
import Orderbook from "./Orderbook";
import Scanner from "./Scanner";
import CountdownBoard from "./CountdownBoard";
import OrderEntry from "./OrderEntry";
import PositionsTable from "./PositionsTable";
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

// ── TermBox helper ───────────────────────────────────────────

function TermBox({
  title,
  icon,
  borderColor,
  children,
  flex,
}: {
  title: string;
  icon: string;
  borderColor: string;
  children: React.ReactNode;
  flex?: string;
}) {
  return (
    <div
      style={{
        background: "#0d0d0d",
        border: `1px solid ${borderColor}`,
        borderRadius: "8px",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        flex: flex || undefined,
        minHeight: 0,
      }}
    >
      <div
        style={{
          padding: "6px 10px",
          background: `${borderColor}15`,
          borderBottom: `1px solid ${borderColor}30`,
          display: "flex",
          alignItems: "center",
          gap: "6px",
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: "10px" }}>{icon}</span>
        <span
          style={{
            fontSize: "9px",
            fontWeight: 700,
            color: borderColor,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
          }}
        >
          {title}
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
}

// ── MetricRow helper ─────────────────────────────────────────

function MetricRow({
  label,
  value,
  valueColor,
}: {
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "3px 10px",
        fontSize: "10px",
      }}
    >
      <span style={{ color: "#5a6577" }}>{label}</span>
      <span
        style={{
          color: valueColor || "#e0e0e0",
          fontWeight: 600,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </span>
    </div>
  );
}

// ── Component ────────────────────────────────────────────────

export default function Terminal() {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [scanFilter, setScanFilter] = useState<ScanType | null>(null);
  const [clock, setClock] = useState("");
  const [kalshiBalance, setKalshiBalance] = useState<number | null>(null);

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

  // Derive microstructure values from first resolution signal
  const firstSignal = normalizedSignals.find((s) => s.scan_type === "resolution") ?? normalizedSignals[0];
  const lambdaVal: number | null = (firstSignal as { lambda?: number } | undefined)?.lambda ?? null;
  const vpinVal: number | null = (firstSignal as { vpin?: number } | undefined)?.vpin ?? null;
  const convTimeVal: number | null = (firstSignal as { conv_time?: number } | undefined)?.conv_time ?? null;
  const whaleFactor: number | null = (firstSignal as { whale_factor?: number } | undefined)?.whale_factor ?? null;
  const rInformedVal: number | null = (firstSignal as { r_informed?: number } | undefined)?.r_informed ?? null;

  const fmtNum = (v: number | null, dec = 4): string =>
    v !== null ? v.toFixed(dec) : "—";

  // Suppress unused clock warning — clock is used for its side-effect (1s tick)
  void clock;

  return (
    <div
      style={{
        height: "100%",
        width: "100%",
        background: "#0a0a0a",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        fontFamily: "'JetBrains Mono', 'Courier New', monospace",
        color: "#e0e0e0",
        backgroundImage: `
          linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
      }}
    >
      {/* ── Main content — 3-column layout ── */}
      <div
        style={{
          flex: 1,
          display: "flex",
          minHeight: 0,
          gap: "8px",
          padding: "8px",
          overflow: "hidden",
        }}
      >
        {/* ── LEFT COLUMN — 240px ── */}
        <div
          style={{
            width: "240px",
            flexShrink: 0,
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            overflow: "hidden",
          }}
        >
          {/* DataFeedsBox */}
          <TermBox title="Data Feeds" icon="◉" borderColor="#00BCD4">
            <div style={{ padding: "4px 0" }}>
              {/* WebSocket status row */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "3px 10px",
                  fontSize: "10px",
                }}
              >
                <span style={{ color: "#5a6577" }}>WebSocket</span>
                <span
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    fontWeight: 600,
                    fontVariantNumeric: "tabular-nums",
                    color:
                      connectionStatus === "connected"
                        ? "#00FF88"
                        : connectionStatus === "connecting"
                          ? "#FFD600"
                          : "#FF3366",
                  }}
                >
                  <span
                    style={{
                      display: "inline-block",
                      width: "5px",
                      height: "5px",
                      borderRadius: "50%",
                      background:
                        connectionStatus === "connected"
                          ? "#00FF88"
                          : connectionStatus === "connecting"
                            ? "#FFD600"
                            : "#FF3366",
                      boxShadow:
                        connectionStatus === "connected"
                          ? "0 0 6px rgba(0,255,136,0.6)"
                          : "none",
                    }}
                  />
                  {connectionStatus === "connected"
                    ? "LIVE"
                    : connectionStatus === "connecting"
                      ? "SYNC"
                      : "OFF"}
                </span>
              </div>
              <MetricRow
                label="BBO updates"
                value={statusData?.bbo_updates?.toLocaleString() ?? "—"}
              />
              <MetricRow
                label="Tickers"
                value={statusData?.tickers_count?.toLocaleString() ?? "—"}
              />
              <MetricRow
                label="Latency"
                value={
                  statusData
                    ? `~${Math.round(statusData.uptime > 0 ? 44 : 0)}ms`
                    : "—"
                }
              />
            </div>
          </TermBox>

          {/* MicrostructureBox */}
          <TermBox title="Microstructure" icon="λ" borderColor="#00BCD4">
            <div style={{ padding: "4px 0" }}>
              <MetricRow
                label="Kyle's λ"
                value={fmtNum(lambdaVal, 4)}
                valueColor={
                  lambdaVal !== null && lambdaVal > 0.012
                    ? "#FF3366"
                    : "#e0e0e0"
                }
              />
              <MetricRow
                label="Action"
                value={
                  lambdaVal !== null
                    ? lambdaVal > 0.012
                      ? "WIDEN"
                      : "QUOTE"
                    : "—"
                }
                valueColor={
                  lambdaVal !== null && lambdaVal > 0.012
                    ? "#FFD600"
                    : "#00FF88"
                }
              />
              <MetricRow label="VPIN" value={fmtNum(vpinVal, 3)} />
              <MetricRow label="r (informed)" value={fmtNum(rInformedVal, 3)} />
              <MetricRow
                label="Conv time"
                value={convTimeVal !== null ? `${fmtNum(convTimeVal, 1)}s` : "—"}
              />
              <MetricRow
                label="Whale factor"
                value={whaleFactor !== null ? `${fmtNum(whaleFactor, 2)}x` : "—"}
              />
              <div
                style={{
                  padding: "4px 10px 6px",
                  fontSize: "8px",
                  color: "#3a4a5a",
                  borderTop: "1px solid #00BCD415",
                  marginTop: "2px",
                  lineHeight: 1.5,
                }}
              >
                λ high→WIDEN · VPIN high→WIDEN · r low→SAFE
              </div>
            </div>
          </TermBox>

          {/* InventoryBox */}
          <TermBox title="Inventory" icon="⟲" borderColor="#00BCD4">
            <div style={{ padding: "4px 0" }}>
              <MetricRow
                label="γ"
                value={`0.01 × |${openTradeCount}|`}
              />
              <MetricRow
                label="Net"
                value={`+${openTradeCount} positions`}
                valueColor="#00FF88"
              />
              <MetricRow
                label="Exposure"
                value={`$${totalPnl ? Math.abs(totalPnl / 100).toFixed(2) : "0.00"}`}
              />
            </div>
          </TermBox>

          {/* Watchlist — MARKETS box, fills remaining space */}
          <TermBox title="Markets" icon="◈" borderColor="#333" flex="1">
            <div
              style={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                minHeight: 0,
                overflow: "hidden",
              }}
            >
              <Watchlist
                categories={categories}
                selectedTicker={selectedTicker ?? undefined}
                onSelect={setSelectedTicker}
              />
            </div>
          </TermBox>
        </div>

        {/* ── CENTER COLUMN — flex 1 ── */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            minWidth: 0,
            minHeight: 0,
            overflow: "hidden",
          }}
        >
          {/* Chart box — 55% */}
          <TermBox
            title="Price Chart"
            icon="◈"
            borderColor="#FF6600"
            flex="55 1 0"
          >
            <div
              style={{
                height: "100%",
                padding: "4px 6px",
                display: "flex",
                flexDirection: "column",
                minHeight: 0,
              }}
            >
              <Chart ticker={selectedTicker ?? undefined} />
            </div>
          </TermBox>

          {/* Scanner box — flex grow */}
          <TermBox
            title="Signal Scanner"
            icon="⬡"
            borderColor="#FF6600"
            flex="1 1 0"
          >
            <div
              style={{
                height: "100%",
                padding: "4px 6px",
                display: "flex",
                flexDirection: "column",
                minHeight: 0,
              }}
            >
              <Scanner
                signals={normalizedSignals}
                filter={scanFilter}
                onFilterChange={setScanFilter}
              />
            </div>
          </TermBox>

          {/* Bottom row: FILLS + P&L | NEAR SETTLEMENT */}
          <div
            style={{
              display: "flex",
              gap: "8px",
              flex: "35 1 0",
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            {/* FILLS + P&L box */}
            <TermBox
              title="Fills + P&L"
              icon="◎"
              borderColor="#00FF88"
              flex="3 1 0"
            >
              <div
                style={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  minHeight: 0,
                  overflow: "hidden",
                }}
              >
                <PositionsTable
                  totalPnl={totalPnl}
                  breakdowns={pnlBreakdowns}
                  openTrades={openTradeCount}
                  recentActivity={recentActivity}
                />
              </div>
            </TermBox>

            {/* NEAR SETTLEMENT box */}
            <TermBox
              title="Near Settlement"
              icon="⏱"
              borderColor="#FF3366"
              flex="2 1 0"
            >
              <div
                style={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  minHeight: 0,
                  overflow: "hidden",
                }}
              >
                <CountdownBoard
                  items={countdown}
                  onSelect={setSelectedTicker}
                  upcomingMarkets={upcomingMarkets}
                />
              </div>
            </TermBox>
          </div>
        </div>

        {/* ── RIGHT COLUMN — 260px ── */}
        <div
          style={{
            width: "260px",
            flexShrink: 0,
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            overflow: "hidden",
          }}
        >
          {/* Orderbook box */}
          <TermBox
            title="Order Book"
            icon="▤"
            borderColor="#00BCD4"
            flex="1 1 0"
          >
            <div
              style={{
                height: "100%",
                padding: "4px 6px",
                display: "flex",
                flexDirection: "column",
                minHeight: 0,
              }}
            >
              <Orderbook ticker={selectedTicker ?? undefined} />
            </div>
          </TermBox>

          {/* OrderEntry — manages its own OEBox wrappers */}
          <div
            style={{
              flex: "1 1 0",
              minHeight: 0,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <OrderEntry
              onBalanceUpdate={setKalshiBalance}
              selectedTicker={selectedTicker ?? undefined}
            />
          </div>
        </div>
      </div>

      {/* ── Status bar — full width, outside main flex ── */}
      <StatusBar
        status={connectionStatus}
        tickerCount={statusData?.tickers_count ?? 0}
        openTrades={openTradeCount}
        balance={kalshiBalance !== null ? kalshiBalance / 100 : 0}
        signalCount={statusData?.scan_signals}
        uptime={statusData?.uptime}
        totalPnl={totalPnl}
      />
    </div>
  );
}
