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
  expected_profit: number;
  roi: number;
}

interface LogEntry {
  time: string;
  message: string;
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

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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
            break;

          case "logs":
            setLogs((prev) => [...prev, ...message.data].slice(-500));
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
  }, []);

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

  // Computed values
  const totalPnL = trades.reduce((sum, t) => {
    if (t.status === "SUCCESS") {
      return sum + t.expected_profit;
    }
    return sum;
  }, 0);

  const successfulTrades = trades.filter((t) => t.status === "SUCCESS").length;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e0e0e0] font-mono p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[#333] pb-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-[#00ff00]">OMI EDGE</h1>
          <span className="text-[#666]">|</span>
          <span className="text-sm text-[#888]">ARB EXECUTOR v6</span>
        </div>

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
            <h2 className="text-sm text-[#888] mb-4 uppercase tracking-wider">Session Stats</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#666]">Total Trades:</span>
                <span>{trades.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#666]">Successful:</span>
                <span className="text-[#00ff00]">{successfulTrades}</span>
              </div>
              <div className="flex justify-between">
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
            <h2 className="text-sm text-[#888] mb-4 uppercase tracking-wider">
              Trade History ({trades.length})
            </h2>
            <div className="max-h-[300px] overflow-y-auto">
              {trades.length === 0 ? (
                <div className="text-[#666] text-sm py-4 text-center">No trades yet</div>
              ) : (
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-[#111]">
                    <tr className="text-[#666] text-left border-b border-[#333]">
                      <th className="pb-2">Time</th>
                      <th className="pb-2">Game</th>
                      <th className="pb-2">Team</th>
                      <th className="pb-2 text-right">Size</th>
                      <th className="pb-2 text-right">P&L</th>
                      <th className="pb-2 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...trades].reverse().map((trade, i) => (
                      <tr key={i} className="border-b border-[#222]">
                        <td className="py-2 text-[#666]">
                          {new Date(trade.timestamp).toLocaleTimeString("en-US", {
                            hour12: false,
                          })}
                        </td>
                        <td className="py-2">{trade.game}</td>
                        <td className="py-2 text-[#00ffff]">{trade.team}</td>
                        <td className="py-2 text-right">{trade.k_fill_count}</td>
                        <td
                          className={`py-2 text-right ${
                            trade.expected_profit >= 0 ? "text-[#00ff00]" : "text-[#ff0000]"
                          }`}
                        >
                          ${trade.expected_profit.toFixed(2)}
                        </td>
                        <td className="py-2 text-right">
                          <span
                            className={`px-1 ${
                              trade.status === "SUCCESS"
                                ? "text-[#00ff00]"
                                : trade.status === "NO_FILL"
                                ? "text-[#888]"
                                : "text-[#ff6600]"
                            }`}
                          >
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
