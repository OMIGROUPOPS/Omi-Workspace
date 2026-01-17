"use client";

import { useState, useEffect, useRef, useCallback } from "react";

// Types
interface Position {
  ticker: string;
  position: number;
  market_exposure: number;
  resting_orders_count?: number;
  total_cost?: number;
}

interface Trade {
  timestamp: string;
  sport: string;
  game: string;
  team: string;
  direction: string;
  intended_size: number;
  k_fill_count: number;
  k_fill_price?: number;
  k_order_id?: string;
  pm_success: boolean;
  pm_error?: string;
  status: string;
  raw_status?: string;
  execution_mode?: "paper" | "live";
  expected_profit: number;
  roi: number;
}

type TradeFilter = "all" | "live" | "paper";

interface LogEntry {
  time: string;
  message: string;
}

interface ScanInfo {
  scanNumber: number;
  gamesFound: number;
  arbsFound: number;
  isScanning: boolean;
}

interface BotStatus {
  bot_state: "stopped" | "starting" | "running" | "stopping" | "error";
  mode: "paper" | "live";
  balance: number | null;
  positions: Position[];
  trade_count: number;
  timestamp: string;
}

type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

// Configuration
const BOT_SERVER_URL = process.env.NEXT_PUBLIC_BOT_SERVER_URL || "http://localhost:8001";
const WS_URL = BOT_SERVER_URL.replace("http", "ws") + "/ws";

export default function TradingDashboard() {
  // State
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("disconnected");
  const [botState, setBotState] = useState<BotStatus["bot_state"]>("stopped");
  const [mode, setMode] = useState<"paper" | "live">("paper");
  const [balance, setBalance] = useState<number | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pmBalance] = useState<number>(494.90); // Tony's PM balance - hardcoded for now
  const [toast, setToast] = useState<string | null>(null);
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [scanInfo, setScanInfo] = useState<ScanInfo>({
    scanNumber: 0,
    gamesFound: 0,
    arbsFound: 0,
    isScanning: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Parse scan info from log message
  const parseScanInfo = useCallback((message: string) => {
    // Match: "=== Scan 123 ==="
    const scanMatch = message.match(/=== Scan (\d+) ===/);
    if (scanMatch) {
      setScanInfo(prev => ({ ...prev, scanNumber: parseInt(scanMatch[1]), isScanning: true, arbsFound: 0 }));
      return;
    }
    // Match: "Found 5 games to scan"
    const gamesMatch = message.match(/Found (\d+) games? to scan/);
    if (gamesMatch) {
      setScanInfo(prev => ({ ...prev, gamesFound: parseInt(gamesMatch[1]) }));
      return;
    }
    // Match: "[*] Found 3 arbs"
    const arbsMatch = message.match(/\[\*\] Found (\d+) arb/);
    if (arbsMatch) {
      setScanInfo(prev => ({ ...prev, arbsFound: parseInt(arbsMatch[1]) }));
      return;
    }
    // Match: "Sleeping" indicates scan complete
    if (message.includes("Sleeping")) {
      setScanInfo(prev => ({ ...prev, isScanning: false }));
    }
  }, []);

  // Helper to get trade status display - uses trade's stored status/mode, not current dashboard mode
  const getTradeStatus = (trade: Trade): { text: string; color: string } => {
    // If status is already PAPER, show as paper trade
    if (trade.status === "PAPER") {
      return { text: "PAPER", color: "text-[#ffff00]" };
    }
    // If execution_mode is paper but status isn't PAPER (legacy trades), show PAPER
    if (trade.execution_mode === "paper") {
      return { text: "PAPER", color: "text-[#ffff00]" };
    }
    // Live trade statuses
    if (trade.status === "SUCCESS") {
      return { text: "SUCCESS", color: "text-[#00ff00]" };
    }
    if (trade.status === "NO_FILL") {
      return { text: "NO_FILL", color: "text-[#888]" };
    }
    if (trade.status === "UNHEDGED") {
      return { text: "UNHEDGED", color: "text-[#ff0000]" };
    }
    if (trade.status === "FAILED") {
      return { text: "FAILED", color: "text-[#ff0000]" };
    }
    // Unknown status
    return { text: trade.status || "UNKNOWN", color: "text-[#ff6600]" };
  };

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionStatus("connecting");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnectionStatus("connected");
      setError(null);
      // Request initial status
      ws.send(JSON.stringify({ type: "get_status" }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        switch (message.type) {
          case "state":
            setBotState(message.data.bot_state);
            setMode(message.data.mode);
            break;

          case "status":
            setBotState(message.data.bot_state);
            setMode(message.data.mode);
            setBalance(message.data.balance);
            setPositions(message.data.positions || []);
            break;

          case "log":
            setLogs((prev) => [...prev.slice(-500), message.data]);
            parseScanInfo(message.data.message);
            break;

          case "logs":
            setLogs((prev) => [...prev, ...message.data].slice(-500));
            // Parse last few logs for scan info
            message.data.slice(-10).forEach((log: LogEntry) => parseScanInfo(log.message));
            break;

          case "pong":
            // Keep-alive response
            break;
        }
      } catch (e) {
        console.error("WS message parse error:", e);
      }
    };

    ws.onerror = () => {
      setConnectionStatus("error");
      setError("WebSocket connection error");
    };

    ws.onclose = () => {
      setConnectionStatus("disconnected");
      wsRef.current = null;

      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };

    wsRef.current = ws;
  }, [parseScanInfo]);

  // Initial connection
  useEffect(() => {
    connectWebSocket();
    fetchTrades();
    fetchStatus();

    // Periodic status refresh
    const statusInterval = setInterval(() => {
      fetchStatus();
      fetchTrades();
    }, 5000);

    // Keep-alive ping
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);

    return () => {
      clearInterval(statusInterval);
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [connectWebSocket]);

  // API calls
  const fetchStatus = async () => {
    try {
      const res = await fetch(`${BOT_SERVER_URL}/status`);
      if (res.ok) {
        const data: BotStatus = await res.json();
        setBotState(data.bot_state);
        setMode(data.mode);
        setBalance(data.balance);
        setPositions(data.positions || []);
      }
    } catch (e) {
      // Silent fail - WebSocket will keep us updated
    }
  };

  const fetchTrades = async () => {
    try {
      const res = await fetch(`${BOT_SERVER_URL}/trades`);
      if (res.ok) {
        const data = await res.json();
        setTrades(data.trades || []);
      }
    } catch (e) {
      // Silent fail
    }
  };

  const handleStart = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/start`, { method: "POST" });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to start bot");
      }
      addLog("[DASHBOARD] Start command sent");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start bot");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/stop`, { method: "POST" });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to stop bot");
      }
      addLog("[DASHBOARD] Stop command sent");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to stop bot");
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = async (newMode: "paper" | "live") => {
    if (botState === "running") {
      setError("Stop the bot before changing mode");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: newMode }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to change mode");
      }
      setMode(newMode);
      addLog(`[DASHBOARD] Mode changed to ${newMode.toUpperCase()}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to change mode");
    } finally {
      setIsLoading(false);
    }
  };

  const addLog = (message: string) => {
    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev.slice(-500), { time, message }]);
  };

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const handlePmRefresh = () => {
    showToast("PM balance refresh not yet implemented");
  };

  const handleClearData = async () => {
    if (!confirm("Clear all trade history and logs? This cannot be undone.")) return;
    try {
      const res = await fetch(`${BOT_SERVER_URL}/clear`, { method: "POST" });
      if (res.ok) {
        setTrades([]);
        setLogs([]);
        showToast("All data cleared");
      } else {
        showToast("Failed to clear data");
      }
    } catch (e) {
      showToast("Error clearing data");
    }
  };

  // Computed values - STRICT filtering:
  // Live = execution_mode is "live" AND status is "SUCCESS" (actually filled & hedged)
  // Paper = execution_mode is "paper" OR status is "PAPER"
  const filteredTrades = trades.filter((t) => {
    if (tradeFilter === "all") return true;
    if (tradeFilter === "live") return t.execution_mode === "live" && t.status === "SUCCESS";
    if (tradeFilter === "paper") return t.execution_mode === "paper" || t.status === "PAPER";
    return true;
  });

  // Only count SUCCESSFUL live trades (filled AND hedged)
  const liveTrades = trades.filter((t) => t.execution_mode === "live" && t.status === "SUCCESS");
  // Paper trades include PAPER status or paper execution mode
  const paperTrades = trades.filter((t) => t.execution_mode === "paper" || t.status === "PAPER");
  // Failed/NO_FILL trades
  const failedTrades = trades.filter((t) => t.status === "NO_FILL" || t.status === "UNHEDGED");

  const totalPnL = trades.reduce((sum, t) => {
    if (t.status === "SUCCESS" || t.status === "PAPER") {
      return sum + t.expected_profit;
    }
    return sum;
  }, 0);

  const successfulTrades = trades.filter((t) => t.status === "SUCCESS" || t.status === "PAPER").length;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e0e0e0] font-mono p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[#333] pb-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-[#00ff00]">OMI EDGE</h1>
          <span className="text-[#666]">|</span>
          <span className="text-sm text-[#888]">ARB EXECUTOR v6</span>
        </div>

        {/* Scanning Indicator */}
        {botState === "running" && (
          <div className="flex items-center gap-4 bg-[#111] border border-[#333] px-4 py-2">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${scanInfo.isScanning ? "bg-[#00ffff] animate-pulse" : "bg-[#333]"}`} />
              <span className={`text-sm font-bold ${scanInfo.isScanning ? "text-[#00ffff]" : "text-[#666]"}`}>
                {scanInfo.isScanning ? "SCANNING" : "IDLE"}
              </span>
            </div>
            <span className="text-[#666]">|</span>
            <span className="text-xs text-[#888]">Scan #{scanInfo.scanNumber}</span>
            <span className="text-xs text-[#888]">{scanInfo.gamesFound} games</span>
            <span className={`text-xs ${scanInfo.arbsFound > 0 ? "text-[#00ff00]" : "text-[#888]"}`}>
              {scanInfo.arbsFound} arbs
            </span>
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connectionStatus === "connected"
                ? "bg-[#00ff00]"
                : connectionStatus === "connecting"
                ? "bg-[#ffff00] animate-pulse"
                : "bg-[#ff0000]"
            }`}
          />
          <span className="text-xs text-[#888] uppercase">{connectionStatus}</span>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-[#ff0000]/20 border border-[#ff0000] text-[#ff6666] px-4 py-2 mb-4 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-[#888] hover:text-white">
            [dismiss]
          </button>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left Column - Controls & Status */}
        <div className="col-span-12 lg:col-span-3 space-y-4">
          {/* Bot Controls */}
          <div className="bg-[#111] border border-[#333] p-4">
            <h2 className="text-sm text-[#888] mb-4 uppercase tracking-wider">Bot Control</h2>

            {/* Mode Toggle */}
            <div className="mb-4">
              <label className="text-xs text-[#666] mb-2 block">EXECUTION MODE</label>
              <div className="flex">
                <button
                  onClick={() => handleModeChange("paper")}
                  disabled={isLoading || botState === "running"}
                  className={`flex-1 py-2 text-sm border ${
                    mode === "paper"
                      ? "bg-[#1a1a2e] border-[#4444ff] text-[#6666ff]"
                      : "bg-[#111] border-[#333] text-[#666] hover:border-[#444]"
                  } disabled:opacity-50`}
                >
                  PAPER
                </button>
                <button
                  onClick={() => handleModeChange("live")}
                  disabled={isLoading || botState === "running"}
                  className={`flex-1 py-2 text-sm border border-l-0 ${
                    mode === "live"
                      ? "bg-[#2e1a1a] border-[#ff4444] text-[#ff6666]"
                      : "bg-[#111] border-[#333] text-[#666] hover:border-[#444]"
                  } disabled:opacity-50`}
                >
                  LIVE
                </button>
              </div>
            </div>

            {/* Start/Stop Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleStart}
                disabled={isLoading || botState === "running" || botState === "starting"}
                className="flex-1 py-3 bg-[#003300] hover:bg-[#004400] border border-[#00ff00] text-[#00ff00]
                         disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-sm font-bold"
              >
                {botState === "starting" ? "STARTING..." : "START"}
              </button>
              <button
                onClick={handleStop}
                disabled={isLoading || botState === "stopped" || botState === "stopping"}
                className="flex-1 py-3 bg-[#330000] hover:bg-[#440000] border border-[#ff0000] text-[#ff0000]
                         disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-sm font-bold"
              >
                {botState === "stopping" ? "STOPPING..." : "STOP"}
              </button>
            </div>

            {/* Bot State */}
            <div className="mt-4 pt-4 border-t border-[#333]">
              <div className="flex justify-between text-sm">
                <span className="text-[#666]">State:</span>
                <span
                  className={`uppercase font-bold ${
                    botState === "running"
                      ? "text-[#00ff00]"
                      : botState === "error"
                      ? "text-[#ff0000]"
                      : botState === "starting" || botState === "stopping"
                      ? "text-[#ffff00]"
                      : "text-[#888]"
                  }`}
                >
                  {botState}
                </span>
              </div>
            </div>
          </div>

          {/* Balances */}
          <div className="bg-[#111] border border-[#333] p-4">
            <h2 className="text-sm text-[#888] mb-3 uppercase tracking-wider">Account Balances</h2>
            <div className="space-y-3">
              {/* Kalshi */}
              <div>
                <div className="text-xs text-[#666] mb-1">KALSHI</div>
                <div className="text-2xl font-bold text-[#00ff00]">
                  {balance !== null ? `$${balance.toFixed(2)}` : "---"}
                </div>
              </div>
              {/* Polymarket */}
              <div className="pt-2 border-t border-[#333]">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-[#666]">POLYMARKET</span>
                  <button
                    onClick={handlePmRefresh}
                    className="text-xs text-[#666] hover:text-[#888] px-1.5 py-0.5 border border-[#333] hover:border-[#444]"
                  >
                    refresh
                  </button>
                </div>
                <div className="text-2xl font-bold text-[#a855f7]">
                  ${pmBalance.toFixed(2)}
                </div>
              </div>
              {/* Combined */}
              <div className="pt-2 border-t border-[#333]">
                <div className="text-xs text-[#666] mb-1">COMBINED</div>
                <div className="text-xl font-bold text-[#e0e0e0]">
                  ${((balance || 0) + pmBalance).toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="bg-[#111] border border-[#333] p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm text-[#888] uppercase tracking-wider">Session Stats</h2>
              <button
                onClick={handleClearData}
                className="text-xs text-[#ff6666] hover:text-[#ff8888] px-2 py-1 border border-[#ff4444] hover:border-[#ff6666]"
              >
                Clear All
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#666]">Live Fills:</span>
                <span className="text-[#00ff00]">{liveTrades.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#666]">Paper Trades:</span>
                <span className="text-[#ffff00]">{paperTrades.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#666]">No Fill:</span>
                <span className="text-[#888]">{failedTrades.length}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-[#333]">
                <span className="text-[#666]">Est. P&L:</span>
                <span className={totalPnL >= 0 ? "text-[#00ff00]" : "text-[#ff0000]"}>
                  ${totalPnL.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column - Positions & Trades */}
        <div className="col-span-12 lg:col-span-5 space-y-4">
          {/* Positions */}
          <div className="bg-[#111] border border-[#333] p-4">
            <h2 className="text-sm text-[#888] mb-4 uppercase tracking-wider">Open Positions</h2>
            {positions.length === 0 ? (
              <div className="text-[#666] text-sm py-4 text-center">No open positions</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-[#666] text-left border-b border-[#333]">
                      <th className="pb-2">Ticker</th>
                      <th className="pb-2 text-right">Position</th>
                      <th className="pb-2 text-right">Exposure</th>
                      <th className="pb-2 text-right">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((pos) => (
                      <tr key={pos.ticker} className="border-b border-[#222]">
                        <td className="py-2 text-[#00ffff]">{pos.ticker}</td>
                        <td
                          className={`py-2 text-right ${
                            pos.position > 0 ? "text-[#00ff00]" : "text-[#ff0000]"
                          }`}
                        >
                          {pos.position > 0 ? "+" : ""}
                          {pos.position}
                        </td>
                        <td className="py-2 text-right">
                          ${((pos.market_exposure || 0) / 100).toFixed(2)}
                        </td>
                        <td className="py-2 text-right text-[#888]">
                          ${((pos.total_cost || 0) / 100).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Trade History */}
          <div className="bg-[#111] border border-[#333] p-4">
            {/* Header with tabs */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm text-[#888] uppercase tracking-wider">Trade History</h2>
              <div className="flex gap-1">
                <button
                  onClick={() => setTradeFilter("all")}
                  className={`px-2 py-1 text-xs border ${
                    tradeFilter === "all"
                      ? "bg-[#333] border-[#555] text-white"
                      : "border-[#333] text-[#666] hover:border-[#444]"
                  }`}
                >
                  All ({trades.length})
                </button>
                <button
                  onClick={() => setTradeFilter("live")}
                  className={`px-2 py-1 text-xs border ${
                    tradeFilter === "live"
                      ? "bg-[#2e1a1a] border-[#ff4444] text-[#ff6666]"
                      : "border-[#333] text-[#666] hover:border-[#444]"
                  }`}
                >
                  Live ({liveTrades.length})
                </button>
                <button
                  onClick={() => setTradeFilter("paper")}
                  className={`px-2 py-1 text-xs border ${
                    tradeFilter === "paper"
                      ? "bg-[#2e2e1a] border-[#ffff44] text-[#ffff66]"
                      : "border-[#333] text-[#666] hover:border-[#444]"
                  }`}
                >
                  Paper ({paperTrades.length})
                </button>
              </div>
            </div>
            <div className="max-h-[400px] overflow-y-auto">
              {filteredTrades.length === 0 ? (
                <div className="text-[#666] text-sm py-4 text-center">
                  {trades.length === 0 ? "No trades yet" : `No ${tradeFilter} trades`}
                </div>
              ) : (
                <div className="space-y-2">
                  {[...filteredTrades].reverse().map((trade, i) => {
                    const status = getTradeStatus(trade);
                    return (
                      <div key={i} className="bg-[#0a0a0a] border border-[#222] p-3">
                        {/* Header row */}
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-[#666] text-xs">
                              {new Date(trade.timestamp).toLocaleTimeString("en-US", { hour12: false })}
                            </span>
                            <span className={`text-xs px-1.5 py-0.5 ${status.color} border border-current`}>
                              {status.text}
                            </span>
                          </div>
                          <span className={`text-sm font-bold ${trade.expected_profit >= 0 ? "text-[#00ff00]" : "text-[#ff0000]"}`}>
                            {trade.expected_profit >= 0 ? "+" : ""}${trade.expected_profit.toFixed(2)}
                          </span>
                        </div>
                        {/* Details */}
                        <div className="text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-[#00ffff] font-bold">{trade.team}</span>
                            <span className="text-[#666]">|</span>
                            <span className="text-[#888]">{trade.game}</span>
                          </div>
                          <div className="flex items-center gap-4 text-[#888]">
                            <span>
                              Dir: <span className={trade.direction === "YES" ? "text-[#00ff00]" : "text-[#ff6666]"}>{trade.direction || "YES"}</span>
                            </span>
                            <span>
                              Size: <span className="text-white">{trade.k_fill_count}</span>
                            </span>
                            <span>
                              K: <span className="text-[#00ffff]">{trade.k_fill_price ? `${trade.k_fill_price}¢` : "--"}</span>
                            </span>
                            <span>
                              ROI: <span className={trade.roi > 0 ? "text-[#00ff00]" : "text-[#888]"}>{trade.roi ? `${trade.roi.toFixed(1)}%` : "--"}</span>
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Logs */}
        <div className="col-span-12 lg:col-span-4">
          <div className="bg-[#111] border border-[#333] p-4 h-full">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm text-[#888] uppercase tracking-wider">Bot Logs</h2>
              <button
                onClick={() => setLogs([])}
                className="text-xs text-[#666] hover:text-[#888] px-2 py-1 border border-[#333] hover:border-[#444]"
              >
                Clear
              </button>
            </div>
            <div className="bg-[#0a0a0a] border border-[#222] h-[500px] overflow-y-auto p-2 text-xs">
              {logs.length === 0 ? (
                <div className="text-[#666] py-4 text-center">Waiting for logs...</div>
              ) : (
                <>
                  {logs.map((log, i) => (
                    <div key={i} className="py-0.5 hover:bg-[#1a1a1a]">
                      <span className="text-[#666]">[{log.time}]</span>{" "}
                      <span
                        className={
                          log.message.includes("[OK]") || log.message.includes("SUCCESS")
                            ? "text-[#00ff00]"
                            : log.message.includes("[!]") ||
                              log.message.includes("ERROR") ||
                              log.message.includes("[X]")
                            ? "text-[#ff6666]"
                            : log.message.includes("[>>]")
                            ? "text-[#00ffff]"
                            : log.message.includes("PAPER")
                            ? "text-[#ffff00]"
                            : "text-[#aaa]"
                        }
                      >
                        {log.message}
                      </span>
                    </div>
                  ))}
                  <div ref={logsEndRef} />
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-[#333] text-xs text-[#666] flex justify-between">
        <span>
          Server: {BOT_SERVER_URL} | Mode:{" "}
          <span className={mode === "live" ? "text-[#ff6666]" : "text-[#6666ff]"}>
            {mode.toUpperCase()}
          </span>
        </span>
        <span>OMI Edge Arb Executor Dashboard</span>
      </div>

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 right-4 bg-[#222] border border-[#444] text-[#e0e0e0] px-4 py-3 text-sm shadow-lg">
          {toast}
        </div>
      )}
    </div>
  );
}
