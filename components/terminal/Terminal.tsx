"use client";

// OMI Terminal — Main Layout (Redesigned)
// Bloomberg-style dark trading terminal with dynamic data and animation.

import { useState, useEffect, useRef, useCallback } from "react";
import Chart from "./Chart";
import Orderbook from "./Orderbook";
import Scanner from "./Scanner";
import PnL from "./PnL";
import Watchlist from "./Watchlist";
import CountdownBoard from "./CountdownBoard";
import StatusBar from "./StatusBar";
import type {
  OrderbookData,
  ScannerSignal,
  PnLData,
  TerminalStatus,
  CountdownItem,
} from "@/lib/terminal/types";
import { MOCK_MARKETS } from "@/lib/terminal/mock-markets";

// ── Mock data generators ──────────────────────────────────────────────────

function makeMockOrderbook(ticker: string): OrderbookData {
  let seed = 0;
  for (const c of ticker) seed += c.charCodeAt(0);
  const rng = (n: number) => { seed = (seed * 1664525 + 1013904223) & 0xffffffff; return Math.abs(seed % n); };
  const mid = 30 + rng(40);
  const spread = 1 + rng(4);
  const bids: OrderbookData["bids"] = [];
  const asks: OrderbookData["asks"] = [];
  let bprice = mid - Math.floor(spread / 2);
  let aprice = bprice + spread;
  for (let i = 0; i < 8; i++) {
    bids.push({ price: Math.max(1, bprice - i), qty: 50 + rng(200) });
    asks.push({ price: Math.min(99, aprice + i), qty: 50 + rng(200) });
  }
  return { bids, asks };
}

function makeMockSignals(markets: typeof MOCK_MARKETS): ScannerSignal[] {
  return markets.slice(0, 12).map((m, i) => ({
    ticker: m.ticker,
    type: (["SPIKE", "TREND", "SQUEEZE", "HALT", "RESUME", "NEWS"] as const)[i % 6],
    price: m.mid,
    lambda: 0.003 + (i % 5) * 0.004 + Math.random() * 0.005,
    vpin: 0.1 + (i % 4) * 0.08,
    timestamp: Date.now() - i * 45000,
  }));
}

function makeMockPnL(markets: typeof MOCK_MARKETS): PnLData {
  const positions = markets.slice(0, 5).map((m, i) => {
    const avgCost = m.mid + (i % 2 === 0 ? -5 : 7);
    const contracts = (i % 2 === 0 ? 10 : -8) * (i + 1);
    const unrealized_pnl = ((m.mid - avgCost) / 100) * Math.abs(contracts) * 100;
    return {
      ticker: m.ticker,
      contracts,
      avg_cost: avgCost,
      price: m.mid,
      unrealized_pnl: Math.round(unrealized_pnl * 100) / 100,
      secs_to_expiry: 3600 * (i + 1),
    };
  });
  return { positions };
}

function makeMockCountdown(markets: typeof MOCK_MARKETS): CountdownItem[] {
  return markets.slice(0, 3).map((m, i) => ({
    ticker: m.ticker,
    price: m.mid,
    secs_to_close: 120 + i * 180,
    confidence: (["HIGH", "MED", "LOW"] as const)[i],
  }));
}

function makeMockStatus(markets: typeof MOCK_MARKETS, pnlData: PnLData): TerminalStatus {
  const now = new Date();
  return {
    feed_status: "LIVE",
    latency_ms: 12 + Math.floor(Math.random() * 8),
    active_markets: markets.length,
    daily_volume: 2840000 + Math.floor(Math.random() * 50000),
    position_count: pnlData.positions.length,
    total_pnl: pnlData.positions.reduce((s, p) => s + p.unrealized_pnl, 0),
    timestamp: now.toLocaleTimeString("en-US", { hour12: false }),
    market_summary: `${markets.length} ACTIVE MKTS  •  VOL $2.84M  •  TOP: ${markets[0]?.ticker ?? ""}`,
  };
}

// ── Resize handle ─────────────────────────────────────────────────────────

function ResizeHandle({ onDrag, cursor }: { onDrag: (delta: number, axis: "h" | "v") => void; cursor: string }) {
  const dragging = useRef(false);
  const lastPos = useRef(0);
  const axis = cursor.includes("col") ? "h" : "v";

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    dragging.current = true;
    lastPos.current = axis === "h" ? e.clientX : e.clientY;
    e.preventDefault();
  }, [axis]);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const pos = axis === "h" ? e.clientX : e.clientY;
      onDrag(pos - lastPos.current, axis);
      lastPos.current = pos;
    };
    const onUp = () => { dragging.current = false; };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [onDrag, axis]);

  return (
    <div
      onMouseDown={onMouseDown}
      style={{
        background: "#111",
        cursor,
        flexShrink: 0,
        transition: "background 0.15s",
        ...(axis === "h" ? { width: "3px", height: "100%" } : { height: "3px", width: "100%" }),
      }}
      onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = "#FF6600"; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = "#111"; }}
    />
  );
}

// ── Panel wrapper ─────────────────────────────────────────────────────────

function Panel({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100%",
      minWidth: 0,
      minHeight: 0,
      overflow: "hidden",
      background: "#080808",
    }}>
      <div style={{
        height: "18px",
        display: "flex",
        alignItems: "center",
        padding: "0 6px",
        borderBottom: "1px solid #111",
        background: "#050505",
        flexShrink: 0,
      }}>
        <span style={{
          fontSize: "7px",
          color: "#333",
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          fontWeight: 700,
        }}>
          {label}
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
}

// ── Terminal ──────────────────────────────────────────────────────────────

export default function Terminal() {
  const [selectedTicker, setSelectedTicker] = useState<string | undefined>(undefined);
  const [orderbookData, setOrderbookData] = useState<OrderbookData | undefined>(undefined);
  const [signals, setSignals] = useState<ScannerSignal[]>([]);
  const [pnlData, setPnlData] = useState<PnLData | undefined>(undefined);
  const [countdownItems, setCountdownItems] = useState<CountdownItem[]>([]);
  const [status, setStatus] = useState<TerminalStatus>({
    feed_status: "LIVE",
    latency_ms: 12,
    active_markets: 0,
    daily_volume: 0,
    position_count: 0,
    total_pnl: 0,
    timestamp: "",
    market_summary: "",
  });

  // Panel sizing state (px)
  const [leftW, setLeftW] = useState(170);
  const [rightW, setRightW] = useState(160);
  const [topH, setTopH] = useState(240);

  const handleResize = useCallback((delta: number, axis: "h" | "v", panel: string) => {
    if (axis === "h") {
      if (panel === "left") setLeftW((w) => Math.max(120, Math.min(300, w + delta)));
      if (panel === "right") setRightW((w) => Math.max(120, Math.min(300, w - delta)));
    } else {
      if (panel === "top") setTopH((h) => Math.max(120, Math.min(500, h + delta)));
    }
  }, []);

  // Initialize mock data
  useEffect(() => {
    const pnl = makeMockPnL(MOCK_MARKETS);
    setSignals(makeMockSignals(MOCK_MARKETS));
    setPnlData(pnl);
    setCountdownItems(makeMockCountdown(MOCK_MARKETS));
    setStatus(makeMockStatus(MOCK_MARKETS, pnl));
  }, []);

  // Tick every 2s
  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedTicker) setOrderbookData(makeMockOrderbook(selectedTicker));
      const pnl = makeMockPnL(MOCK_MARKETS);
      setPnlData(pnl);
      setStatus(makeMockStatus(MOCK_MARKETS, pnl));
    }, 2000);
    return () => clearInterval(interval);
  }, [selectedTicker]);

  const handleSelect = (ticker: string) => {
    setSelectedTicker(ticker);
    setOrderbookData(makeMockOrderbook(ticker));
  };

  return (
    <div style={{
      width: "100%",
      height: "100vh",
      background: "#080808",
      display: "flex",
      flexDirection: "column",
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      color: "#eee",
      overflow: "hidden",
    }}>
      {/* ── Header ── */}
      <div style={{
        height: "28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 12px",
        borderBottom: "1px solid #111",
        background: "#050505",
        flexShrink: 0,
        position: "relative",
        overflow: "hidden",
      }}>
        {/* Scanline sweep */}
        <div style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "1px",
          background: "linear-gradient(90deg, transparent, rgba(255,102,0,0.3), transparent)",
          animation: "terminal-scanline 4s linear infinite",
          pointerEvents: "none",
        }} />

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{
            color: "#FF6600",
            fontWeight: 700,
            fontSize: "11px",
            letterSpacing: "0.15em",
            textShadow: "0 0 12px rgba(255,102,0,0.4)",
          }}>
            OMI TERMINAL
          </span>
          <span style={{ color: "#1a1a1a", fontSize: "8px" }}>|</span>
          <span style={{ color: "#222", fontSize: "8px", letterSpacing: "0.08em" }}>PREDICTION MARKETS</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {["EQUITY", "CRYPTO", "POLITICS", "SPORTS"].map((cat) => (
            <span
              key={cat}
              style={{
                fontSize: "7px",
                color: "#222",
                letterSpacing: "0.1em",
                cursor: "pointer",
                padding: "2px 6px",
                borderRadius: "2px",
                border: "1px solid transparent",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLSpanElement).style.color = "#FF6600";
                (e.currentTarget as HTMLSpanElement).style.borderColor = "rgba(255,102,0,0.2)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLSpanElement).style.color = "#222";
                (e.currentTarget as HTMLSpanElement).style.borderColor = "transparent";
              }}
            >
              {cat}
            </span>
          ))}
        </div>
      </div>

      {/* ── Main grid ── */}
      <div style={{ flex: 1, display: "flex", minHeight: 0, overflow: "hidden" }}>
        {/* Left column */}
        <div style={{ width: leftW, display: "flex", flexDirection: "column", flexShrink: 0, minHeight: 0 }}>
          {/* Watchlist top */}
          <div style={{ height: topH, flexShrink: 0, borderBottom: "1px solid #111" }}>
            <Panel label="Watchlist">
              <Watchlist
                markets={MOCK_MARKETS}
                selectedTicker={selectedTicker}
                onSelect={handleSelect}
              />
            </Panel>
          </div>
          <ResizeHandle onDrag={(d) => handleResize(d, "v", "top")} cursor="row-resize" />
          {/* Countdown bottom */}
          <div style={{ flex: 1, minHeight: 0, borderTop: "1px solid #111" }}>
            <Panel label="Settlement">
              <CountdownBoard
                items={countdownItems}
                onSelect={handleSelect}
                upcomingMarkets={MOCK_MARKETS.slice(0, 6).map((m) => ({
                  ticker: m.ticker,
                  team: m.team,
                  mid: m.mid,
                  spread: m.spread,
                  category: m.category,
                }))}
              />
            </Panel>
          </div>
        </div>

        <ResizeHandle onDrag={(d) => handleResize(d, "h", "left")} cursor="col-resize" />

        {/* Center column */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, minHeight: 0 }}>
          {/* Chart top */}
          <div style={{ height: topH, flexShrink: 0, borderBottom: "1px solid #111" }}>
            <Panel label={selectedTicker ?? "Chart"}>
              <Chart ticker={selectedTicker} />
            </Panel>
          </div>
          <ResizeHandle onDrag={(d) => handleResize(d, "v", "top")} cursor="row-resize" />
          {/* Scanner + P&L bottom */}
          <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Panel label="Scanner">
                <Scanner signals={signals} onSelect={handleSelect} />
              </Panel>
            </div>
            <div style={{ width: "1px", background: "#111" }} />
            <div style={{ width: rightW, flexShrink: 0 }}>
              <Panel label="P&L">
                <PnL data={pnlData} />
              </Panel>
            </div>
          </div>
        </div>

        <ResizeHandle onDrag={(d) => handleResize(d, "h", "right")} cursor="col-resize" />

        {/* Right column */}
        <div style={{ width: rightW, flexShrink: 0, minHeight: 0 }}>
          <Panel label="Order Book">
            <Orderbook data={orderbookData} />
          </Panel>
        </div>
      </div>

      {/* ── Status bar ── */}
      <div style={{ height: "20px", flexShrink: 0 }}>
        <StatusBar status={status} />
      </div>
    </div>
  );
}
