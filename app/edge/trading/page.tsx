"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";

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

type TradeFilter = "all" | "live" | "paper" | "failed";

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

// Mini Sparkline component
function Sparkline({ data, width = 120, height = 32, color = "#00ff00" }: {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}) {
  if (data.length < 2) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-[#444] text-xs">
        No data
      </div>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const padding = 2;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * (width - padding * 2) + padding;
    const y = height - padding - ((value - min) / range) * (height - padding * 2);
    return `${x},${y}`;
  }).join(' ');

  const lastPoint = data[data.length - 1];
  const lastX = width - padding;
  const lastY = height - padding - ((lastPoint - min) / range) * (height - padding * 2);

  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id="sparklineGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* Area fill */}
      <polygon
        points={`${padding},${height - padding} ${points} ${lastX},${height - padding}`}
        fill="url(#sparklineGradient)"
      />
      {/* Line */}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Current value dot */}
      <circle cx={lastX} cy={lastY} r="3" fill={color} />
    </svg>
  );
}

// Status indicator component
function StatusDot({ status, size = "sm", pulse = false }: {
  status: "success" | "warning" | "error" | "neutral" | "info";
  size?: "sm" | "md";
  pulse?: boolean;
}) {
  const colors = {
    success: "bg-emerald-500 shadow-emerald-500/50",
    warning: "bg-amber-500 shadow-amber-500/50",
    error: "bg-red-500 shadow-red-500/50",
    neutral: "bg-zinc-500 shadow-zinc-500/50",
    info: "bg-cyan-500 shadow-cyan-500/50",
  };

  const sizes = {
    sm: "w-2 h-2",
    md: "w-3 h-3",
  };

  return (
    <div
      className={`rounded-full shadow-lg ${colors[status]} ${sizes[size]} ${pulse ? "animate-pulse" : ""}`}
    />
  );
}

// Card component for consistent styling
function Card({ children, className = "", glow = false }: {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}) {
  return (
    <div className={`
      bg-zinc-900/80 backdrop-blur-sm border border-zinc-800
      rounded-lg shadow-xl
      ${glow ? "shadow-emerald-500/10 border-emerald-500/30" : ""}
      ${className}
    `}>
      {children}
    </div>
  );
}

// Stat display component
function StatValue({ value, unit = "", color = "text-zinc-100", mono = true }: {
  value: string | number;
  unit?: string;
  color?: string;
  mono?: boolean;
}) {
  return (
    <span className={`${color} ${mono ? "font-mono" : ""}`}>
      {value}{unit && <span className="text-zinc-500 text-xs ml-0.5">{unit}</span>}
    </span>
  );
}

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
  const [pmBalance] = useState<number>(494.90);
  const [toast, setToast] = useState<string | null>(null);
  const [tradeFilter, setTradeFilter] = useState<TradeFilter>("all");
  const [scanInfo, setScanInfo] = useState<ScanInfo>({
    scanNumber: 0,
    gamesFound: 0,
    arbsFound: 0,
    isScanning: false,
  });
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [uptime, setUptime] = useState<string>("00:00:00");
  const [latency, setLatency] = useState<number | null>(null);
  const [profitHistory, setProfitHistory] = useState<number[]>([0]);

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Calculate uptime
  useEffect(() => {
    if (botState === "running" && !startTime) {
      setStartTime(new Date());
    } else if (botState === "stopped") {
      setStartTime(null);
      setUptime("00:00:00");
    }
  }, [botState, startTime]);

  useEffect(() => {
    if (!startTime) return;

    const interval = setInterval(() => {
      const now = new Date();
      const diff = Math.floor((now.getTime() - startTime.getTime()) / 1000);
      const hours = Math.floor(diff / 3600).toString().padStart(2, '0');
      const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
      const seconds = (diff % 60).toString().padStart(2, '0');
      setUptime(`${hours}:${minutes}:${seconds}`);
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  // Parse scan info from log message
  const parseScanInfo = useCallback((message: string) => {
    const scanMatch = message.match(/Scan #?(\d+)/i);
    if (scanMatch) {
      setScanInfo(prev => ({ ...prev, scanNumber: parseInt(scanMatch[1]), isScanning: true, arbsFound: 0 }));
      return;
    }
    const gamesMatch = message.match(/Games:\s*(\d+)|(\d+)\s*games/i);
    if (gamesMatch) {
      setScanInfo(prev => ({ ...prev, gamesFound: parseInt(gamesMatch[1] || gamesMatch[2]) }));
      return;
    }
    const arbsMatch = message.match(/(\d+)\s*arb|Found\s*(\d+)/i);
    if (arbsMatch) {
      const count = parseInt(arbsMatch[1] || arbsMatch[2]);
      if (count >= 0 && count <= 100) {
        setScanInfo(prev => ({ ...prev, arbsFound: count }));
      }
      return;
    }
    if (message.includes("Sleeping") || message.includes("sleep")) {
      setScanInfo(prev => ({ ...prev, isScanning: false }));
    }
  }, []);

  // Calculate fill rate and stats
  const stats = useMemo(() => {
    const liveTrades = trades.filter(t => t.execution_mode === "live" && t.status === "SUCCESS");
    const paperTrades = trades.filter(t => t.execution_mode === "paper" || t.status === "PAPER");
    const failedTrades = trades.filter(t => t.status === "NO_FILL" || t.status === "UNHEDGED");
    const liveAttempts = trades.filter(t => t.execution_mode === "live");

    const fillRate = liveAttempts.length > 0
      ? (liveTrades.length / liveAttempts.length) * 100
      : 0;

    const totalPnL = trades.reduce((sum, t) => {
      if (t.status === "SUCCESS" || t.status === "PAPER") {
        return sum + t.expected_profit;
      }
      return sum;
    }, 0);

    const lastSuccessfulTrade = [...trades]
      .filter(t => t.status === "SUCCESS" || t.status === "PAPER")
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];

    return {
      liveTrades,
      paperTrades,
      failedTrades,
      liveAttempts,
      fillRate,
      totalPnL,
      lastSuccessfulTrade,
      totalTrades: trades.length,
    };
  }, [trades]);

  // Update profit history
  useEffect(() => {
    setProfitHistory(prev => {
      const newHistory = [...prev, stats.totalPnL];
      return newHistory.slice(-30); // Keep last 30 data points
    });
  }, [stats.totalPnL]);

  // Get trade status display
  const getTradeStatus = (trade: Trade): { text: string; color: string; bgColor: string } => {
    if (trade.status === "PAPER" || trade.execution_mode === "paper") {
      return { text: "PAPER", color: "text-amber-400", bgColor: "bg-amber-500/10 border-amber-500/30" };
    }
    if (trade.status === "SUCCESS") {
      return { text: "SUCCESS", color: "text-emerald-400", bgColor: "bg-emerald-500/10 border-emerald-500/30" };
    }
    if (trade.status === "NO_FILL") {
      return { text: "NO_FILL", color: "text-zinc-400", bgColor: "bg-zinc-500/10 border-zinc-500/30" };
    }
    if (trade.status === "UNHEDGED") {
      return { text: "UNHEDGED", color: "text-red-400", bgColor: "bg-red-500/10 border-red-500/30" };
    }
    if (trade.status === "FAILED") {
      return { text: "FAILED", color: "text-red-400", bgColor: "bg-red-500/10 border-red-500/30" };
    }
    return { text: trade.status || "UNKNOWN", color: "text-orange-400", bgColor: "bg-orange-500/10 border-orange-500/30" };
  };

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Ping for latency
  const measureLatency = useCallback(async () => {
    try {
      const start = performance.now();
      const res = await fetch(`${BOT_SERVER_URL}/status`, { method: "GET" });
      if (res.ok) {
        const end = performance.now();
        setLatency(Math.round(end - start));
      }
    } catch {
      setLatency(null);
    }
  }, []);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionStatus("connecting");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnectionStatus("connected");
      setError(null);
      ws.send(JSON.stringify({ type: "get_status" }));
      measureLatency();
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
            message.data.slice(-10).forEach((log: LogEntry) => parseScanInfo(log.message));
            break;

          case "pong":
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
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };

    wsRef.current = ws;
  }, [parseScanInfo, measureLatency]);

  // Initial connection
  useEffect(() => {
    connectWebSocket();
    fetchTrades();
    fetchStatus();

    const statusInterval = setInterval(() => {
      fetchStatus();
      fetchTrades();
      measureLatency();
    }, 5000);

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
  }, [connectWebSocket, measureLatency]);

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
    } catch {
      // Silent fail
    }
  };

  const fetchTrades = async () => {
    try {
      const res = await fetch(`${BOT_SERVER_URL}/trades`);
      if (res.ok) {
        const data = await res.json();
        setTrades(data.trades || []);
      }
    } catch {
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

  const handleClearData = async () => {
    if (!confirm("Clear all trade history and logs? This cannot be undone.")) return;
    try {
      const res = await fetch(`${BOT_SERVER_URL}/clear`, { method: "POST" });
      if (res.ok) {
        setTrades([]);
        setLogs([]);
        setProfitHistory([0]);
        showToast("All data cleared");
      } else {
        showToast("Failed to clear data");
      }
    } catch {
      showToast("Error clearing data");
    }
  };

  // Filtered trades
  const filteredTrades = trades.filter((t) => {
    if (tradeFilter === "all") return true;
    if (tradeFilter === "live") return t.execution_mode === "live" && t.status === "SUCCESS";
    if (tradeFilter === "paper") return t.execution_mode === "paper" || t.status === "PAPER";
    if (tradeFilter === "failed") return t.status === "NO_FILL" || t.status === "UNHEDGED" || t.status === "FAILED";
    return true;
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-4 selection:bg-emerald-500/30">
      {/* Top Stats Bar */}
      <div className="mb-4">
        <Card className="p-3">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Logo & Title */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center font-bold text-sm">
                  OMI
                </div>
                <div>
                  <h1 className="text-lg font-bold text-zinc-100">OMI EDGE</h1>
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider">ARB EXECUTOR v6</p>
                </div>
              </div>
            </div>

            {/* Real-time Stats */}
            <div className="flex items-center gap-6 text-sm">
              {/* Scan Status */}
              <div className="flex items-center gap-2">
                <StatusDot
                  status={scanInfo.isScanning ? "info" : "neutral"}
                  pulse={scanInfo.isScanning}
                />
                <div className="flex flex-col">
                  <span className="text-[10px] text-zinc-500 uppercase">Scan</span>
                  <span className="font-mono text-zinc-100">#{scanInfo.scanNumber}</span>
                </div>
              </div>

              <div className="w-px h-8 bg-zinc-800" />

              {/* Games */}
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-500 uppercase">Games</span>
                <span className="font-mono text-zinc-100">{scanInfo.gamesFound}</span>
              </div>

              {/* Arbs */}
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-500 uppercase">Arbs</span>
                <span className={`font-mono ${scanInfo.arbsFound > 0 ? "text-emerald-400" : "text-zinc-400"}`}>
                  {scanInfo.arbsFound}
                </span>
              </div>

              <div className="w-px h-8 bg-zinc-800" />

              {/* Fill Rate */}
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-500 uppercase">Fill Rate</span>
                <span className={`font-mono ${
                  stats.fillRate >= 50 ? "text-emerald-400" :
                  stats.fillRate >= 25 ? "text-amber-400" : "text-red-400"
                }`}>
                  {stats.fillRate.toFixed(1)}%
                </span>
              </div>

              {/* Uptime */}
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-500 uppercase">Uptime</span>
                <span className="font-mono text-zinc-100">{uptime}</span>
              </div>

              <div className="w-px h-8 bg-zinc-800" />

              {/* Connection & Latency */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <StatusDot
                    status={connectionStatus === "connected" ? "success" : connectionStatus === "connecting" ? "warning" : "error"}
                    pulse={connectionStatus === "connecting"}
                  />
                  <div className="flex flex-col">
                    <span className="text-[10px] text-zinc-500 uppercase">API</span>
                    <span className={`text-xs font-mono ${
                      connectionStatus === "connected" ? "text-emerald-400" :
                      connectionStatus === "connecting" ? "text-amber-400" : "text-red-400"
                    }`}>
                      {latency !== null ? `${latency}ms` : "---"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Mode Badge */}
              <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                mode === "live"
                  ? "bg-red-500/20 text-red-400 border border-red-500/50"
                  : "bg-blue-500/20 text-blue-400 border border-blue-500/50"
              }`}>
                {mode}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 px-4 py-3 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400/60 hover:text-red-400 transition-colors">
            ✕
          </button>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left Column - Controls & Status */}
        <div className="col-span-12 lg:col-span-3 space-y-4">
          {/* Bot Controls */}
          <Card className="p-4">
            <h2 className="text-xs text-zinc-500 mb-4 uppercase tracking-wider font-medium">Bot Control</h2>

            {/* Mode Toggle */}
            <div className="mb-4">
              <label className="text-[10px] text-zinc-600 mb-2 block uppercase tracking-wider">Execution Mode</label>
              <div className="flex rounded-lg overflow-hidden border border-zinc-700">
                <button
                  onClick={() => handleModeChange("paper")}
                  disabled={isLoading || botState === "running"}
                  className={`flex-1 py-2.5 text-sm font-medium transition-all ${
                    mode === "paper"
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-400"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  PAPER
                </button>
                <button
                  onClick={() => handleModeChange("live")}
                  disabled={isLoading || botState === "running"}
                  className={`flex-1 py-2.5 text-sm font-medium transition-all ${
                    mode === "live"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-400"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
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
                className="flex-1 py-3 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/50
                         text-emerald-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all
                         text-sm font-bold rounded-lg hover:shadow-lg hover:shadow-emerald-500/10"
              >
                {botState === "starting" ? "STARTING..." : "START"}
              </button>
              <button
                onClick={handleStop}
                disabled={isLoading || botState === "stopped" || botState === "stopping"}
                className="flex-1 py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/50
                         text-red-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all
                         text-sm font-bold rounded-lg hover:shadow-lg hover:shadow-red-500/10"
              >
                {botState === "stopping" ? "STOPPING..." : "STOP"}
              </button>
            </div>

            {/* Bot State */}
            <div className="mt-4 pt-4 border-t border-zinc-800">
              <div className="flex justify-between items-center text-sm">
                <span className="text-zinc-500">State</span>
                <div className="flex items-center gap-2">
                  <StatusDot
                    status={
                      botState === "running" ? "success" :
                      botState === "error" ? "error" :
                      (botState === "starting" || botState === "stopping") ? "warning" : "neutral"
                    }
                    pulse={botState === "starting" || botState === "stopping"}
                  />
                  <span className={`uppercase font-bold font-mono ${
                    botState === "running" ? "text-emerald-400" :
                    botState === "error" ? "text-red-400" :
                    (botState === "starting" || botState === "stopping") ? "text-amber-400" : "text-zinc-400"
                  }`}>
                    {botState}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Balances */}
          <Card className="p-4">
            <h2 className="text-xs text-zinc-500 mb-4 uppercase tracking-wider font-medium">Account Balances</h2>
            <div className="space-y-4">
              {/* Kalshi */}
              <div className="p-3 bg-zinc-800/50 rounded-lg border border-zinc-700/50">
                <div className="text-[10px] text-zinc-500 mb-1 uppercase tracking-wider">Kalshi</div>
                <div className="text-2xl font-bold font-mono text-emerald-400">
                  {balance !== null ? `$${balance.toFixed(2)}` : "---"}
                </div>
              </div>
              {/* Polymarket */}
              <div className="p-3 bg-zinc-800/50 rounded-lg border border-zinc-700/50">
                <div className="text-[10px] text-zinc-500 mb-1 uppercase tracking-wider">Polymarket</div>
                <div className="text-2xl font-bold font-mono text-purple-400">
                  ${pmBalance.toFixed(2)}
                </div>
              </div>
              {/* Combined */}
              <div className="p-3 bg-gradient-to-br from-emerald-500/10 to-purple-500/10 rounded-lg border border-zinc-700/50">
                <div className="text-[10px] text-zinc-500 mb-1 uppercase tracking-wider">Combined</div>
                <div className="text-2xl font-bold font-mono text-zinc-100">
                  ${((balance || 0) + pmBalance).toFixed(2)}
                </div>
              </div>
            </div>
          </Card>

          {/* Session Stats */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Session Stats</h2>
              <button
                onClick={handleClearData}
                className="text-[10px] text-red-400/60 hover:text-red-400 px-2 py-1 border border-red-500/30
                         hover:border-red-500/50 rounded transition-all hover:bg-red-500/10"
              >
                Clear All
              </button>
            </div>

            {/* P&L with Sparkline */}
            <div className="mb-4 p-3 bg-zinc-800/50 rounded-lg border border-zinc-700/50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Estimated P&L</span>
                <span className={`text-xl font-bold font-mono ${
                  stats.totalPnL >= 0 ? "text-emerald-400" : "text-red-400"
                }`}>
                  {stats.totalPnL >= 0 ? "+" : ""}${stats.totalPnL.toFixed(2)}
                </span>
              </div>
              <Sparkline
                data={profitHistory}
                color={stats.totalPnL >= 0 ? "#10b981" : "#ef4444"}
                width={200}
                height={40}
              />
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center py-1.5 border-b border-zinc-800/50">
                <span className="text-zinc-500">Live Fills</span>
                <span className="font-mono text-emerald-400">{stats.liveTrades.length}</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-zinc-800/50">
                <span className="text-zinc-500">Paper Trades</span>
                <span className="font-mono text-amber-400">{stats.paperTrades.length}</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-zinc-800/50">
                <span className="text-zinc-500">No Fill</span>
                <span className="font-mono text-zinc-400">{stats.failedTrades.length}</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-zinc-800/50">
                <span className="text-zinc-500">Fill Rate</span>
                <span className={`font-mono ${
                  stats.fillRate >= 50 ? "text-emerald-400" :
                  stats.fillRate >= 25 ? "text-amber-400" : "text-red-400"
                }`}>
                  {stats.fillRate.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-zinc-500">Last Success</span>
                <span className="font-mono text-zinc-300 text-xs">
                  {stats.lastSuccessfulTrade
                    ? new Date(stats.lastSuccessfulTrade.timestamp).toLocaleTimeString("en-US", { hour12: false })
                    : "---"
                  }
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Middle Column - Positions & Trades */}
        <div className="col-span-12 lg:col-span-5 space-y-4">
          {/* Positions */}
          <Card className="p-4">
            <h2 className="text-xs text-zinc-500 mb-4 uppercase tracking-wider font-medium">Open Positions</h2>
            {positions.length === 0 ? (
              <div className="text-zinc-500 text-sm py-8 text-center bg-zinc-800/30 rounded-lg border border-zinc-800">
                No open positions
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-zinc-500 text-left">
                      <th className="pb-3 font-medium text-[10px] uppercase tracking-wider">Ticker</th>
                      <th className="pb-3 font-medium text-[10px] uppercase tracking-wider text-right">Position</th>
                      <th className="pb-3 font-medium text-[10px] uppercase tracking-wider text-right">Exposure</th>
                      <th className="pb-3 font-medium text-[10px] uppercase tracking-wider text-right">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((pos) => (
                      <tr key={pos.ticker} className="border-t border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                        <td className="py-3 font-mono text-cyan-400">{pos.ticker}</td>
                        <td className={`py-3 text-right font-mono ${pos.position > 0 ? "text-emerald-400" : "text-red-400"}`}>
                          {pos.position > 0 ? "+" : ""}{pos.position}
                        </td>
                        <td className="py-3 text-right font-mono text-zinc-300">
                          ${((pos.market_exposure || 0) / 100).toFixed(2)}
                        </td>
                        <td className="py-3 text-right font-mono text-zinc-500">
                          ${((pos.total_cost || 0) / 100).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Trade History */}
          <Card className="p-4">
            {/* Header with tabs */}
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <h2 className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Trade History</h2>
              <div className="flex gap-1 bg-zinc-800/50 p-1 rounded-lg">
                {[
                  { key: "all", label: "All", count: trades.length },
                  { key: "live", label: "Live", count: stats.liveTrades.length, color: "emerald" },
                  { key: "paper", label: "Paper", count: stats.paperTrades.length, color: "amber" },
                  { key: "failed", label: "Failed", count: stats.failedTrades.length, color: "zinc" },
                ].map(({ key, label, count, color }) => (
                  <button
                    key={key}
                    onClick={() => setTradeFilter(key as TradeFilter)}
                    className={`px-3 py-1.5 text-xs rounded-md transition-all font-medium ${
                      tradeFilter === key
                        ? color === "emerald"
                          ? "bg-emerald-500/20 text-emerald-400"
                          : color === "amber"
                          ? "bg-amber-500/20 text-amber-400"
                          : color === "zinc"
                          ? "bg-zinc-600/50 text-zinc-300"
                          : "bg-zinc-700 text-zinc-100"
                        : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-700/50"
                    }`}
                  >
                    {label} <span className="opacity-60">({count})</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="max-h-[400px] overflow-y-auto space-y-2 pr-1">
              {filteredTrades.length === 0 ? (
                <div className="text-zinc-500 text-sm py-8 text-center bg-zinc-800/30 rounded-lg border border-zinc-800">
                  {trades.length === 0 ? "No trades yet" : `No ${tradeFilter} trades`}
                </div>
              ) : (
                [...filteredTrades].reverse().map((trade, i) => {
                  const status = getTradeStatus(trade);
                  return (
                    <div
                      key={i}
                      className={`p-3 rounded-lg border transition-all hover:border-zinc-600 ${status.bgColor}`}
                    >
                      {/* Header row */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-zinc-500 text-xs font-mono">
                            {new Date(trade.timestamp).toLocaleTimeString("en-US", { hour12: false })}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium uppercase ${status.color} border border-current/30`}>
                            {status.text}
                          </span>
                        </div>
                        <span className={`text-sm font-bold font-mono ${trade.expected_profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                          {trade.expected_profit >= 0 ? "+" : ""}${trade.expected_profit.toFixed(2)}
                        </span>
                      </div>
                      {/* Details */}
                      <div className="text-xs">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className="text-cyan-400 font-bold">{trade.team}</span>
                          <span className="text-zinc-600">|</span>
                          <span className="text-zinc-400">{trade.game}</span>
                        </div>
                        <div className="flex items-center gap-4 text-zinc-500">
                          <span>
                            Size: <span className="text-zinc-200 font-mono">{trade.k_fill_count}</span>
                          </span>
                          <span>
                            Price: <span className="text-cyan-400 font-mono">{trade.k_fill_price ? `${trade.k_fill_price}¢` : "--"}</span>
                          </span>
                          <span>
                            ROI: <span className={`font-mono ${trade.roi > 0 ? "text-emerald-400" : "text-zinc-400"}`}>
                              {trade.roi ? `${trade.roi.toFixed(1)}%` : "--"}
                            </span>
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </div>

        {/* Right Column - Logs */}
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-4 h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Bot Logs</h2>
              <button
                onClick={() => setLogs([])}
                className="text-[10px] text-zinc-500 hover:text-zinc-300 px-2 py-1 border border-zinc-700
                         hover:border-zinc-600 rounded transition-all hover:bg-zinc-800"
              >
                Clear
              </button>
            </div>
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg flex-1 overflow-hidden">
              <div className="h-[550px] overflow-y-auto p-3 text-xs font-mono">
                {logs.length === 0 ? (
                  <div className="text-zinc-600 py-4 text-center">Waiting for logs...</div>
                ) : (
                  <>
                    {logs.map((log, i) => (
                      <div key={i} className="py-0.5 hover:bg-zinc-900/50 rounded px-1 -mx-1">
                        <span className="text-zinc-600">[{log.time}]</span>{" "}
                        <span
                          className={
                            log.message.includes("[OK]") || log.message.includes("SUCCESS")
                              ? "text-emerald-400"
                              : log.message.includes("[!]") || log.message.includes("ERROR") || log.message.includes("[X]")
                              ? "text-red-400"
                              : log.message.includes("[>>]") || log.message.includes("SWEEP")
                              ? "text-cyan-400"
                              : log.message.includes("PAPER")
                              ? "text-amber-400"
                              : log.message.includes("[CANCEL]") || log.message.includes("CLEANUP")
                              ? "text-orange-400"
                              : "text-zinc-400"
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
          </Card>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-zinc-800 text-xs text-zinc-600 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <span className="font-mono">{BOT_SERVER_URL}</span>
          <span className="text-zinc-800">|</span>
          <span>
            Mode: <span className={mode === "live" ? "text-red-400 font-medium" : "text-blue-400 font-medium"}>
              {mode.toUpperCase()}
            </span>
          </span>
        </div>
        <span className="text-zinc-700">OMI Edge Trading Terminal v1.0</span>
      </div>

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 right-4 bg-zinc-800 border border-zinc-700 text-zinc-100
                       px-4 py-3 text-sm rounded-lg shadow-2xl animate-in slide-in-from-bottom-2">
          {toast}
        </div>
      )}
    </div>
  );
}
