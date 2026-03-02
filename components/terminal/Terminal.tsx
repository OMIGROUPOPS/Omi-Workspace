"use client";

// OMNI Terminal — Main layout
// Flex-based panel layout (no CSS grid overlap issues).

import { useState, useEffect } from "react";
import Watchlist from "./Watchlist";
import Chart from "./Chart";
import Orderbook from "./Orderbook";
import Scanner from "./Scanner";
import CountdownBoard from "./CountdownBoard";
import PnL from "./PnL";
import StatusBar from "./StatusBar";
import type {
  WatchlistItem,
  ScanSignal,
  ScanType,
  CountdownItem,
  PnLBreakdown,
} from "@/lib/terminal/types";

// ── Mock Data ────────────────────────────────────────────────

function mkInfo(
  ticker: string,
  team: string,
  gameId: string,
  type: "moneyline" | "spread" | "total" | "variant",
  category = "Sports",
): import("@/lib/terminal/types").MarketInfo {
  return {
    ticker,
    event_ticker: ticker.replace(/-[YN]$/, ""),
    game_id: gameId,
    market_type: type,
    team,
    floor_strike: null,
    close_time: new Date(Date.now() + 3600_000).toISOString(),
    category,
  };
}

const MOCK_WATCHLIST: WatchlistItem[] = [
  { ticker: "KXMLB-NYY-ML-Y", info: mkInfo("KXMLB-NYY-ML-Y", "NYY Yankees", "mlb-nyy-bos", "moneyline"), best_bid: 61, best_ask: 63, mid: 62, spread: 2, bid_size: 245, ask_size: 180, move_30s: 3, kyle_lambda: 0.0082 },
  { ticker: "KXMLB-BOS-ML-Y", info: mkInfo("KXMLB-BOS-ML-Y", "BOS Red Sox", "mlb-nyy-bos", "moneyline"), best_bid: 36, best_ask: 39, mid: 38, spread: 3, bid_size: 190, ask_size: 210, move_30s: -3, kyle_lambda: 0.0091 },
  { ticker: "KXNBA-LAL-SP-Y", info: mkInfo("KXNBA-LAL-SP-Y", "LAL -3.5", "nba-lal-gsw", "spread"), best_bid: 53, best_ask: 56, mid: 55, spread: 3, bid_size: 120, ask_size: 95, move_30s: 2, kyle_lambda: 0.0065 },
  { ticker: "KXNBA-GSW-SP-Y", info: mkInfo("KXNBA-GSW-SP-Y", "GSW +3.5", "nba-lal-gsw", "spread"), best_bid: 44, best_ask: 47, mid: 45, spread: 3, bid_size: 95, ask_size: 120, move_30s: -2, kyle_lambda: 0.0065 },
  { ticker: "KXCRYPTO-BTC40-Y", info: mkInfo("KXCRYPTO-BTC40-Y", "BTC > $40K", "crypto-btc-40k", "moneyline", "Crypto"), best_bid: 71, best_ask: 73, mid: 72, spread: 2, bid_size: 890, ask_size: 650, move_30s: 1, kyle_lambda: 0.0041 },
  { ticker: "KXCRYPTO-ETH3-N", info: mkInfo("KXCRYPTO-ETH3-N", "ETH < $3K", "crypto-eth-3k", "moneyline", "Crypto"), best_bid: 70, best_ask: 74, mid: 72, spread: 4, bid_size: 310, ask_size: 280, move_30s: -1, kyle_lambda: 0.0055 },
  { ticker: "KXPOL-APPROVE-Y", info: mkInfo("KXPOL-APPROVE-Y", "Approval >45%", "pol-approval", "moneyline", "Politics"), best_bid: 46, best_ask: 50, mid: 48, spread: 4, bid_size: 40, ask_size: 55, move_30s: 0, kyle_lambda: 0.0210 },
  { ticker: "KXECON-FED-CUT-Y", info: mkInfo("KXECON-FED-CUT-Y", "Fed Cut Mar", "econ-fed-mar", "moneyline", "Economics"), best_bid: 33, best_ask: 37, mid: 35, spread: 4, bid_size: 75, ask_size: 90, move_30s: -1, kyle_lambda: 0.0180 },
  { ticker: "KXMLB-NYM-TOT-O", info: mkInfo("KXMLB-NYM-TOT-O", "NYM o8.5", "mlb-nym-phi", "total"), best_bid: 49, best_ask: 53, mid: 51, spread: 4, bid_size: 60, ask_size: 45, move_30s: 1, kyle_lambda: 0.0120 },
  { ticker: "KXNHL-CHI-ML-Y", info: mkInfo("KXNHL-CHI-ML-Y", "CHI Hawks", "nhl-chi-det", "moneyline"), best_bid: 65, best_ask: 69, mid: 67, spread: 4, bid_size: 80, ask_size: 70, move_30s: 2, kyle_lambda: 0.0095 },
];

const MOCK_SIGNALS: ScanSignal[] = [
  { scan_type: "momentum_lag", severity: "HIGH", ticker: "KXMLB-NYY-ML-Y", game_id: "mlb-nyy-bos", entry_side: "buy_yes", entry_price: 63, target: 68, stop: 58, description: "ML +5c (\u0394logit=+0.21) spread only +2c (\u0394logit=+0.08)", depth: 180, timestamp: Date.now() - 12000 },
  { scan_type: "resolution", severity: "HIGH", ticker: "KXMLB-BOS-ML-Y", game_id: "mlb-nyy-bos", entry_side: "buy_no", entry_price: 3, target: 100, stop: 0, description: "BOS 97\u00a2 bridge=0.98 \u03c3=0.15 T=45s kelly=12ct", depth: 240, bridge_confidence: 0.98, sigma_estimate: 0.15, time_remaining: 45, optimal_size: 12, timestamp: Date.now() - 8000 },
  { scan_type: "whale_momentum", severity: "MEDIUM", ticker: "KXCRYPTO-BTC40-Y", game_id: "crypto-btc-40k", entry_side: "buy_yes", entry_price: 73, target: 78, stop: 68, description: "Whale 500ct BTC>40K YES@72 taker=yes", depth: 650, timestamp: Date.now() - 25000 },
  { scan_type: "contradiction_mono", severity: "LOW", ticker: "KXNBA-LAL-SP-Y", game_id: "nba-lal-gsw", entry_side: "buy_yes", entry_price: 56, target: 62, stop: 50, description: "LAL spread vs ML contradiction 3c gap", depth: 95, timestamp: Date.now() - 45000 },
  { scan_type: "momentum_lag", severity: "MEDIUM", ticker: "KXNHL-CHI-ML-Y", game_id: "nhl-chi-det", entry_side: "buy_yes", entry_price: 69, target: 74, stop: 64, description: "Spread +3c (\u0394logit=+0.12) ML lagging +1c (\u0394logit=+0.04)", depth: 70, timestamp: Date.now() - 60000 },
  { scan_type: "resolution", severity: "HIGH", ticker: "KXCRYPTO-ETH3-N", game_id: "crypto-eth-3k", entry_side: "buy_no", entry_price: 4, target: 100, stop: 0, description: "ETH 3\u00a2 bridge=0.97 \u03c3=0.22 T=120s kelly=8ct", depth: 280, bridge_confidence: 0.97, sigma_estimate: 0.22, time_remaining: 120, optimal_size: 8, timestamp: Date.now() - 5000 },
];

const INITIAL_COUNTDOWN: CountdownItem[] = [
  { ticker: "KXMLB-BOS-ML-Y", info: mkInfo("KXMLB-BOS-ML-Y", "BOS Red Sox", "mlb-nyy-bos", "moneyline"), price: 97, side: "near_100", secs_to_close: 45, bridge_confidence: 0.98, sigma: 0.15, depth: 240, kelly_size: 12 },
  { ticker: "KXMLB-NYM-TOT-O", info: mkInfo("KXMLB-NYM-TOT-O", "NYM o8.5", "mlb-nym-phi", "total"), price: 4, side: "near_0", secs_to_close: 60, bridge_confidence: 0.97, sigma: 0.18, depth: 45, kelly_size: 3 },
  { ticker: "KXCRYPTO-ETH3-N", info: mkInfo("KXCRYPTO-ETH3-N", "ETH < $3K", "crypto-eth-3k", "moneyline", "Crypto"), price: 3, side: "near_0", secs_to_close: 120, bridge_confidence: 0.97, sigma: 0.22, depth: 280, kelly_size: 8 },
  { ticker: "KXCRYPTO-BTC40-Y", info: mkInfo("KXCRYPTO-BTC40-Y", "BTC > $40K", "crypto-btc-40k", "moneyline", "Crypto"), price: 96, side: "near_100", secs_to_close: 180, bridge_confidence: 0.95, sigma: 0.30, depth: 650, kelly_size: 5 },
];

const MOCK_PNL: PnLBreakdown[] = [
  { scan_type: "resolution", total_pnl: 4200, trade_count: 6, winners: 5, losers: 1, avg_hold_time: 95, avg_edge: 0.12 },
  { scan_type: "momentum_lag", total_pnl: 1500, trade_count: 4, winners: 3, losers: 1, avg_hold_time: 180, avg_edge: 0.08 },
  { scan_type: "whale_momentum", total_pnl: -800, trade_count: 2, winners: 0, losers: 2, avg_hold_time: 240, avg_edge: 0.05 },
  { scan_type: "contradiction_mono", total_pnl: 500, trade_count: 1, winners: 1, losers: 0, avg_hold_time: 300, avg_edge: 0.06 },
];

// ── Component ────────────────────────────────────────────────

export default function Terminal() {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [scanFilter, setScanFilter] = useState<ScanType | null>(null);
  const [countdown, setCountdown] = useState(INITIAL_COUNTDOWN);
  const [clock, setClock] = useState("");

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

  const totalPnl = MOCK_PNL.reduce((sum, b) => sum + b.total_pnl, 0);

  return (
    <div
      className="h-full w-full bg-[#0a0a0a] text-slate-200 flex flex-col overflow-hidden"
      style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}
    >
      {/* ── Top bar ── */}
      <div
        className="flex items-center justify-between px-4 shrink-0"
        style={{ height: "28px", background: "#111", borderBottom: "1px solid #222" }}
      >
        <div className="flex items-center gap-3">
          <span style={{ color: "#FF6600", fontWeight: 700, fontSize: "13px", letterSpacing: "0.1em" }}>
            OMNI
          </span>
          <span style={{ color: "#555", fontSize: "10px", letterSpacing: "0.15em" }}>
            EXCHANGE TERMINAL
          </span>
          <span style={{ color: "#333", fontSize: "9px" }}>v0.1.0</span>
        </div>
        <div className="flex items-center gap-4" style={{ fontSize: "10px" }}>
          <span style={{ color: "#555" }}>{new Date().toISOString().slice(0, 10)}</span>
          <span style={{ color: "#555" }} suppressHydrationWarning>{clock}</span>
          <span style={{ color: "#22c55e" }}>
            <span
              style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: "#22c55e",
                marginRight: "4px",
                boxShadow: "0 0 6px rgba(34,197,94,0.5)",
              }}
            />
            LIVE
          </span>
        </div>
      </div>

      {/* ── Main content area ── */}
      <div style={{ flex: 1, display: "flex", minHeight: 0, overflow: "hidden" }}>

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
            items={MOCK_WATCHLIST}
            selectedTicker={selectedTicker ?? undefined}
            onSelect={setSelectedTicker}
          />
        </div>

        {/* ── Center + Right panels ── */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, minHeight: 0 }}>

          {/* ── Top row: Chart + Orderbook (60%) ── */}
          <div style={{ height: "60%", display: "flex", minHeight: 0 }}>
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

          {/* ── Bottom row: Scanner + Countdown + P&L (40%) ── */}
          <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
            {/* Scanner */}
            <div
              style={{
                flex: 4,
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
                signals={MOCK_SIGNALS}
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
              <CountdownBoard items={countdown} onSelect={setSelectedTicker} />
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
              <PnL totalPnl={totalPnl} breakdowns={MOCK_PNL} openTrades={3} />
            </div>
          </div>
        </div>
      </div>

      {/* ── Status bar ── */}
      <StatusBar
        status="connected"
        tickerCount={MOCK_WATCHLIST.length}
        openTrades={3}
        balance={460}
      />
    </div>
  );
}
