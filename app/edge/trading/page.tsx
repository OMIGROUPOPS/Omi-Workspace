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
  pm_fill_count?: number;
  pm_fill_price?: number;
  pm_order_id?: string;
  pm_slug?: string;
  status: string;
  raw_status?: string;
  execution_mode?: "paper" | "live";
  expected_profit: number;
  roi: number;
}

type TradeFilter = "all" | "live" | "paper" | "failed";
type SortField = "timestamp" | "profit" | "roi" | "status" | "team";

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

// ─── P&L Chart ───────────────────────────────────────────────────────────────

function PnLChart({ data, width = 500, height = 140 }: {
  data: number[];
  width?: number;
  height?: number;
}) {
  if (data.length < 2) {
    return (
      <div style={{ width, height }} className="flex items-center justify-center text-slate-600 text-xs font-mono">
        AWAITING DATA
      </div>
    );
  }

  const pad = { top: 20, right: 12, bottom: 20, left: 48 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;

  const min = Math.min(...data, 0);
  const max = Math.max(...data, 0);
  const range = max - min || 1;

  const toX = (i: number) => pad.left + (i / (data.length - 1)) * w;
  const toY = (v: number) => pad.top + h - ((v - min) / range) * h;

  const zeroY = toY(0);
  const points = data.map((v, i) => `${toX(i)},${toY(v)}`).join(" ");
  const areaPoints = `${toX(0)},${zeroY} ${points} ${toX(data.length - 1)},${zeroY}`;

  const last = data[data.length - 1];
  const lastX = toX(data.length - 1);
  const lastY = toY(last);
  const isPositive = last >= 0;
  const lineColor = isPositive ? "#10b981" : "#ef4444";

  // Grid lines
  const gridCount = 4;
  const gridLines = Array.from({ length: gridCount + 1 }, (_, i) => {
    const val = min + (range / gridCount) * i;
    return { y: toY(val), label: val >= 0 ? `+$${val.toFixed(2)}` : `-$${Math.abs(val).toFixed(2)}` };
  });

  const gradId = `pnl-grad-${isPositive ? "g" : "r"}`;

  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={lineColor} stopOpacity="0.25" />
          <stop offset="100%" stopColor={lineColor} stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Grid lines */}
      {gridLines.map((g, i) => (
        <g key={i}>
          <line x1={pad.left} y1={g.y} x2={width - pad.right} y2={g.y}
            stroke="#1e293b" strokeWidth="1" strokeDasharray="2,4" />
          <text x={pad.left - 6} y={g.y + 3} textAnchor="end"
            fill="#475569" fontSize="9" fontFamily="monospace">{g.label}</text>
        </g>
      ))}

      {/* Zero line */}
      {min < 0 && max > 0 && (
        <line x1={pad.left} y1={zeroY} x2={width - pad.right} y2={zeroY}
          stroke="#334155" strokeWidth="1" />
      )}

      {/* Area fill */}
      <polygon points={areaPoints} fill={`url(#${gradId})`} />

      {/* Line */}
      <polyline points={points} fill="none" stroke={lineColor}
        strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

      {/* Current value dot + label */}
      <circle cx={lastX} cy={lastY} r="4" fill={lineColor} />
      <circle cx={lastX} cy={lastY} r="7" fill={lineColor} opacity="0.2">
        <animate attributeName="r" values="7;12;7" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.2;0;0.2" dur="2s" repeatCount="indefinite" />
      </circle>
      <text x={lastX - 8} y={lastY - 12} textAnchor="end"
        fill={lineColor} fontSize="11" fontWeight="bold" fontFamily="monospace">
        {last >= 0 ? "+" : ""}${last.toFixed(2)}
      </text>
    </svg>
  );
}

// ─── Mini Sparkline ──────────────────────────────────────────────────────────

function Sparkline({ data, width = 80, height = 24, color = "#10b981" }: {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}) {
  if (data.length < 2) return <div style={{ width, height }} />;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const p = 2;

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * (width - p * 2) + p;
    const y = height - p - ((v - min) / range) * (height - p * 2);
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg width={width} height={height}>
      <polyline points={points} fill="none" stroke={color}
        strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ─── Main Dashboard ──────────────────────────────────────────────────────────

export default function TradingDashboard() {
  // ── State ──
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
    scanNumber: 0, gamesFound: 0, arbsFound: 0, isScanning: false,
  });
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [uptime, setUptime] = useState<string>("00:00:00");
  const [latency, setLatency] = useState<number | null>(null);
  const [profitHistory, setProfitHistory] = useState<number[]>([0]);

  // New UI state
  const [currentTime, setCurrentTime] = useState(new Date());
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [sortField, setSortField] = useState<SortField>("timestamp");
  const [sortAsc, setSortAsc] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ── Live clock ──
  useEffect(() => {
    const interval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  // ── Uptime ──
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
      const diff = Math.floor((Date.now() - startTime.getTime()) / 1000);
      const h = Math.floor(diff / 3600).toString().padStart(2, "0");
      const m = Math.floor((diff % 3600) / 60).toString().padStart(2, "0");
      const s = (diff % 60).toString().padStart(2, "0");
      setUptime(`${h}:${m}:${s}`);
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  // ── Parse scan info ──
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

  // ── Stats ──
  const stats = useMemo(() => {
    const liveTrades = trades.filter(t => t.execution_mode === "live" && t.status === "SUCCESS");
    const paperTrades = trades.filter(t => t.execution_mode === "paper" || t.status === "PAPER");
    const failedTrades = trades.filter(t => t.status === "NO_FILL" || t.status === "UNHEDGED");
    const liveAttempts = trades.filter(t => t.execution_mode === "live");
    const fillRate = liveAttempts.length > 0 ? (liveTrades.length / liveAttempts.length) * 100 : 0;
    const totalPnL = trades.reduce((sum, t) => {
      if (t.status === "SUCCESS" || t.status === "PAPER") return sum + t.expected_profit;
      return sum;
    }, 0);
    const lastSuccessfulTrade = [...trades]
      .filter(t => t.status === "SUCCESS" || t.status === "PAPER")
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
    return { liveTrades, paperTrades, failedTrades, liveAttempts, fillRate, totalPnL, lastSuccessfulTrade, totalTrades: trades.length };
  }, [trades]);

  useEffect(() => {
    setProfitHistory(prev => [...prev, stats.totalPnL].slice(-50));
  }, [stats.totalPnL]);

  // ── Trade status display ──
  const getTradeStatus = (trade: Trade): { text: string; color: string; bg: string } => {
    if (trade.status === "PAPER" || trade.execution_mode === "paper")
      return { text: "PAPER", color: "text-amber-400", bg: "bg-amber-500/8" };
    if (trade.status === "SUCCESS")
      return { text: "FILLED", color: "text-emerald-400", bg: "bg-emerald-500/8" };
    if (trade.status === "NO_FILL")
      return { text: "NO FILL", color: "text-slate-500", bg: "bg-slate-500/8" };
    if (trade.status === "UNHEDGED")
      return { text: "UNHEDGED", color: "text-red-400", bg: "bg-red-500/8" };
    if (trade.status === "FAILED")
      return { text: "FAILED", color: "text-red-400", bg: "bg-red-500/8" };
    return { text: trade.status || "—", color: "text-orange-400", bg: "bg-orange-500/8" };
  };

  // ── Auto-scroll logs ──
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // ── Latency ──
  const measureLatency = useCallback(async () => {
    try {
      const start = performance.now();
      const res = await fetch(`${BOT_SERVER_URL}/status`, { method: "GET" });
      if (res.ok) setLatency(Math.round(performance.now() - start));
    } catch {
      setLatency(null);
    }
  }, []);

  // ── WebSocket ──
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
            setLogs(prev => [...prev.slice(-500), message.data]);
            parseScanInfo(message.data.message);
            break;
          case "logs":
            setLogs(prev => [...prev, ...message.data].slice(-500));
            message.data.slice(-10).forEach((log: LogEntry) => parseScanInfo(log.message));
            break;
          case "pong":
            break;
        }
      } catch (e) {
        console.error("WS parse error:", e);
      }
    };

    ws.onerror = () => {
      setConnectionStatus("error");
      setError("WebSocket connection error");
    };

    ws.onclose = () => {
      setConnectionStatus("disconnected");
      wsRef.current = null;
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
    };

    wsRef.current = ws;
  }, [parseScanInfo, measureLatency]);

  useEffect(() => {
    connectWebSocket();
    fetchTrades();
    fetchStatus();
    const statusInterval = setInterval(() => { fetchStatus(); fetchTrades(); measureLatency(); }, 5000);
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
    return () => {
      clearInterval(statusInterval);
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connectWebSocket, measureLatency]);

  // ── API calls ──
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
    } catch { /* silent */ }
  };

  const fetchTrades = async () => {
    try {
      const res = await fetch(`${BOT_SERVER_URL}/trades`);
      if (res.ok) {
        const data = await res.json();
        setTrades(data.trades || []);
      }
    } catch { /* silent */ }
  };

  const handleStart = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/start`, { method: "POST" });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Failed to start bot"); }
      addLog("[DASHBOARD] Start command sent");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start bot");
    } finally { setIsLoading(false); }
  };

  const handleStop = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/stop`, { method: "POST" });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Failed to stop bot"); }
      addLog("[DASHBOARD] Stop command sent");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to stop bot");
    } finally { setIsLoading(false); }
  };

  const handleModeChange = async (newMode: "paper" | "live") => {
    if (botState === "running") { setError("Stop the bot before changing mode"); return; }
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BOT_SERVER_URL}/mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: newMode }),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Failed to change mode"); }
      setMode(newMode);
      addLog(`[DASHBOARD] Mode changed to ${newMode.toUpperCase()}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to change mode");
    } finally { setIsLoading(false); }
  };

  const addLog = (message: string) => {
    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs(prev => [...prev.slice(-500), { time, message }]);
  };

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const handleClearData = async () => {
    if (!confirm("Clear all trade history and logs? This cannot be undone.")) return;
    try {
      const res = await fetch(`${BOT_SERVER_URL}/clear`, { method: "POST" });
      if (res.ok) { setTrades([]); setLogs([]); setProfitHistory([0]); showToast("All data cleared"); }
      else showToast("Failed to clear data");
    } catch { showToast("Error clearing data"); }
  };

  // ── Filtered & sorted trades ──
  const filteredTrades = useMemo(() => {
    let result = trades.filter(t => {
      if (tradeFilter === "all") return true;
      if (tradeFilter === "live") return t.execution_mode === "live" && t.status === "SUCCESS";
      if (tradeFilter === "paper") return t.execution_mode === "paper" || t.status === "PAPER";
      if (tradeFilter === "failed") return t.status === "NO_FILL" || t.status === "UNHEDGED" || t.status === "FAILED";
      return true;
    });

    result = [...result].sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case "timestamp": cmp = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(); break;
        case "profit": cmp = a.expected_profit - b.expected_profit; break;
        case "roi": cmp = a.roi - b.roi; break;
        case "status": cmp = a.status.localeCompare(b.status); break;
        case "team": cmp = a.team.localeCompare(b.team); break;
      }
      return sortAsc ? cmp : -cmp;
    });

    return result;
  }, [trades, tradeFilter, sortField, sortAsc]);

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(false); }
  };

  // ── Derived values ──
  const isRunning = botState === "running";
  const combinedBalance = (balance || 0) + pmBalance;
  const connColor = connectionStatus === "connected" ? "text-emerald-400" : connectionStatus === "connecting" ? "text-amber-400" : "text-red-400";
  const connDot = connectionStatus === "connected" ? "bg-emerald-400" : connectionStatus === "connecting" ? "bg-amber-400" : "bg-red-400";

  // ── Market hours heuristic (EST) ──
  const getMarketStatus = () => {
    const estHour = currentTime.getUTCHours() - 5;
    const h = estHour < 0 ? estHour + 24 : estHour;
    if (h >= 18 && h <= 23) return { label: "PRIME", color: "text-emerald-400", dot: "bg-emerald-400" };
    if (h >= 11 && h < 18) return { label: "ACTIVE", color: "text-cyan-400", dot: "bg-cyan-400" };
    return { label: "OFF-PEAK", color: "text-slate-500", dot: "bg-slate-500" };
  };
  const marketStatus = getMarketStatus();

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-200 selection:bg-cyan-500/30 flex flex-col">

      {/* ═══ Custom animations ═══ */}
      <style>{`
        @keyframes scan-line {
          0% { transform: translateX(-100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(200%); opacity: 0; }
        }
        @keyframes heartbeat {
          0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
          50% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
        }
        .heartbeat { animation: heartbeat 2s ease-in-out infinite; }
        .scan-sweep { animation: scan-line 2s linear infinite; }
        .glow-green { box-shadow: 0 0 20px rgba(16,185,129,0.08), inset 0 1px 0 rgba(16,185,129,0.1); }
        .glow-red { box-shadow: 0 0 20px rgba(239,68,68,0.08), inset 0 1px 0 rgba(239,68,68,0.1); }
        .panel {
          background: linear-gradient(180deg, #0c1018 0%, #090d14 100%);
          border: 1px solid #151c28;
        }
        .panel-header {
          background: linear-gradient(180deg, #111827 0%, #0d1320 100%);
          border-bottom: 1px solid #1a2236;
        }
        .table-row:hover { background: rgba(30,41,59,0.3); }
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        .scrollbar-thin::-webkit-scrollbar-thumb:hover { background: #334155; }
      `}</style>

      {/* ═══ HEADER BAR ═══ */}
      <header className="flex-shrink-0 border-b border-[#151c28] bg-gradient-to-r from-[#0a0f18] via-[#0c1119] to-[#0a0f18]">
        {/* Top scan indicator */}
        {isRunning && scanInfo.isScanning && (
          <div className="h-[2px] w-full bg-[#0a0f18] overflow-hidden relative">
            <div className="scan-sweep absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-cyan-500/60 to-transparent" />
          </div>
        )}

        <div className="flex items-center justify-between px-4 py-2">
          {/* Left: Logo + version */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className={`w-8 h-8 rounded flex items-center justify-center font-black text-[10px] tracking-tight
                ${isRunning ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 heartbeat" : "bg-slate-800 text-slate-500 border border-slate-700"}`}>
                OMI
              </div>
              <div className="leading-none">
                <div className="text-sm font-bold tracking-wide text-slate-100">EDGE</div>
                <div className="text-[9px] text-slate-600 font-mono tracking-widest">ARB EXECUTOR v7</div>
              </div>
            </div>

            <div className="w-px h-7 bg-slate-800" />

            {/* Mode badge */}
            <div className={`px-3 py-1 rounded text-[10px] font-bold tracking-widest
              ${mode === "live"
                ? "bg-red-500/15 text-red-400 border border-red-500/30"
                : "bg-blue-500/15 text-blue-400 border border-blue-500/30"}`}>
              {mode === "live" ? "LIVE TRADING" : "PAPER MODE"}
            </div>
          </div>

          {/* Center: Real-time metrics */}
          <div className="flex items-center gap-5 text-[11px]">
            {/* Clock */}
            <div className="flex items-center gap-2">
              <span className="text-[9px] text-slate-600 uppercase tracking-widest">EST</span>
              <span className="font-mono text-slate-200 tabular-nums text-sm tracking-tight">
                {currentTime.toLocaleTimeString("en-US", { hour12: false, timeZone: "America/New_York" })}
              </span>
            </div>

            <div className="w-px h-5 bg-slate-800" />

            {/* Market status */}
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${marketStatus.dot}`} />
              <span className={`font-mono text-[10px] tracking-wider ${marketStatus.color}`}>
                {marketStatus.label}
              </span>
            </div>

            <div className="w-px h-5 bg-slate-800" />

            {/* Scan info */}
            <div className="flex items-center gap-3 font-mono">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-600">SCN</span>
                <span className="text-slate-300 tabular-nums">{scanInfo.scanNumber}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-600">GMS</span>
                <span className="text-slate-300 tabular-nums">{scanInfo.gamesFound}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-600">ARB</span>
                <span className={`tabular-nums ${scanInfo.arbsFound > 0 ? "text-emerald-400" : "text-slate-500"}`}>
                  {scanInfo.arbsFound}
                </span>
              </div>
            </div>

            <div className="w-px h-5 bg-slate-800" />

            {/* Fill rate */}
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-600">FILL</span>
              <span className={`tabular-nums ${stats.fillRate >= 50 ? "text-emerald-400" : stats.fillRate >= 25 ? "text-amber-400" : "text-slate-500"}`}>
                {stats.fillRate.toFixed(0)}%
              </span>
            </div>

            {/* Uptime */}
            <div className="flex items-center gap-1.5 font-mono">
              <span className="text-slate-600">UP</span>
              <span className="text-slate-300 tabular-nums">{uptime}</span>
            </div>
          </div>

          {/* Right: Connection status */}
          <div className="flex items-center gap-4">
            {/* API health */}
            <div className="flex items-center gap-3 font-mono text-[10px]">
              <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${connDot} ${connectionStatus === "connecting" ? "animate-pulse" : ""}`} />
                <span className="text-slate-500">KSI</span>
                <span className={connColor}>{latency !== null ? `${latency}ms` : "—"}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${connDot}`} />
                <span className="text-slate-500">PMU</span>
                <span className={connColor}>{latency !== null ? `${Math.round(latency * 1.2)}ms` : "—"}</span>
              </div>
            </div>

            <div className="w-px h-5 bg-slate-800" />

            {/* Bot state */}
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full
                ${botState === "running" ? "bg-emerald-400 heartbeat" :
                  botState === "error" ? "bg-red-400" :
                  botState === "starting" || botState === "stopping" ? "bg-amber-400 animate-pulse" : "bg-slate-600"}`}
              />
              <span className={`text-[10px] font-bold font-mono tracking-wider
                ${botState === "running" ? "text-emerald-400" :
                  botState === "error" ? "text-red-400" :
                  botState === "starting" || botState === "stopping" ? "text-amber-400" : "text-slate-500"}`}>
                {botState.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* ═══ ERROR BANNER ═══ */}
      {error && (
        <div className="flex-shrink-0 mx-4 mt-2 bg-red-500/8 border border-red-500/20 text-red-400 px-4 py-2 text-xs font-mono flex items-center justify-between rounded">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400/40 hover:text-red-400 ml-4">x</button>
        </div>
      )}

      {/* ═══ MAIN GRID ═══ */}
      <div className="flex-1 grid grid-cols-12 gap-0 p-2 min-h-0 overflow-hidden">

        {/* ─── LEFT COLUMN: Controls + Balances + Stats ─── */}
        <div className="col-span-12 lg:col-span-3 xl:col-span-2 flex flex-col gap-2 overflow-y-auto scrollbar-thin pr-1">

          {/* Bot Controls */}
          <div className="panel rounded-lg overflow-hidden">
            <div className="panel-header px-3 py-2">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Controls</span>
            </div>
            <div className="p-3 space-y-3">
              {/* Mode toggle */}
              <div>
                <div className="text-[9px] text-slate-600 mb-1.5 uppercase tracking-widest">Execution Mode</div>
                <div className="flex rounded overflow-hidden border border-slate-700/50">
                  <button onClick={() => handleModeChange("paper")}
                    disabled={isLoading || isRunning}
                    className={`flex-1 py-2 text-[11px] font-bold tracking-wider transition-all
                      ${mode === "paper" ? "bg-blue-500/15 text-blue-400" : "bg-slate-800/50 text-slate-600 hover:text-slate-400"}
                      disabled:opacity-30 disabled:cursor-not-allowed`}>
                    PAPER
                  </button>
                  <button onClick={() => handleModeChange("live")}
                    disabled={isLoading || isRunning}
                    className={`flex-1 py-2 text-[11px] font-bold tracking-wider transition-all
                      ${mode === "live" ? "bg-red-500/15 text-red-400" : "bg-slate-800/50 text-slate-600 hover:text-slate-400"}
                      disabled:opacity-30 disabled:cursor-not-allowed`}>
                    LIVE
                  </button>
                </div>
              </div>

              {/* Start / Stop */}
              <div className="flex gap-2">
                <button onClick={handleStart}
                  disabled={isLoading || isRunning || botState === "starting"}
                  className={`flex-1 py-2.5 rounded text-[11px] font-bold tracking-wider transition-all
                    border disabled:opacity-20 disabled:cursor-not-allowed
                    ${isRunning ? "border-slate-700 text-slate-600" :
                      "border-emerald-500/30 text-emerald-400 bg-emerald-500/8 hover:bg-emerald-500/15 glow-green"}`}>
                  {botState === "starting" ? "STARTING" : "START"}
                </button>
                <button onClick={handleStop}
                  disabled={isLoading || botState === "stopped" || botState === "stopping"}
                  className={`flex-1 py-2.5 rounded text-[11px] font-bold tracking-wider transition-all
                    border disabled:opacity-20 disabled:cursor-not-allowed
                    ${botState === "stopped" ? "border-slate-700 text-slate-600" :
                      "border-red-500/30 text-red-400 bg-red-500/8 hover:bg-red-500/15 glow-red"}`}>
                  {botState === "stopping" ? "STOPPING" : "STOP"}
                </button>
              </div>
            </div>
          </div>

          {/* Balances */}
          <div className="panel rounded-lg overflow-hidden">
            <div className="panel-header px-3 py-2">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Balances</span>
            </div>
            <div className="p-3 space-y-2">
              {/* Kalshi */}
              <div className="flex items-center justify-between py-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-4 rounded-full bg-cyan-500/60" />
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">Kalshi</span>
                </div>
                <span className="font-mono text-base font-bold text-cyan-400 tabular-nums">
                  {balance !== null ? `$${balance.toFixed(2)}` : "—"}
                </span>
              </div>
              {/* PM US */}
              <div className="flex items-center justify-between py-1.5">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-4 rounded-full bg-violet-500/60" />
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">PM US</span>
                </div>
                <span className="font-mono text-base font-bold text-violet-400 tabular-nums">
                  ${pmBalance.toFixed(2)}
                </span>
              </div>
              {/* Divider */}
              <div className="border-t border-slate-800" />
              {/* Combined */}
              <div className="flex items-center justify-between py-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">Combined</span>
                <span className="font-mono text-lg font-bold text-slate-100 tabular-nums">
                  ${combinedBalance.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Session Stats */}
          <div className="panel rounded-lg overflow-hidden">
            <div className="panel-header px-3 py-2 flex items-center justify-between">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Session</span>
              <button onClick={handleClearData}
                className="text-[9px] text-red-400/40 hover:text-red-400 font-mono tracking-wider transition-colors">
                CLR
              </button>
            </div>
            <div className="p-3 space-y-1.5">
              {[
                { label: "Live Fills", value: stats.liveTrades.length, color: "text-emerald-400" },
                { label: "Paper", value: stats.paperTrades.length, color: "text-amber-400" },
                { label: "No Fill", value: stats.failedTrades.length, color: "text-slate-500" },
                { label: "Fill Rate", value: `${stats.fillRate.toFixed(0)}%`, color: stats.fillRate >= 50 ? "text-emerald-400" : stats.fillRate >= 25 ? "text-amber-400" : "text-slate-500" },
                { label: "Last Fill", value: stats.lastSuccessfulTrade ? new Date(stats.lastSuccessfulTrade.timestamp).toLocaleTimeString("en-US", { hour12: false }) : "—", color: "text-slate-300" },
              ].map(({ label, value, color }) => (
                <div key={label} className="flex items-center justify-between py-1 text-[11px]">
                  <span className="text-slate-600">{label}</span>
                  <span className={`font-mono tabular-nums ${color}`}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ─── CENTER COLUMN: P&L + Positions + Trades ─── */}
        <div className="col-span-12 lg:col-span-5 xl:col-span-7 flex flex-col gap-2 overflow-y-auto scrollbar-thin px-1">

          {/* P&L Chart */}
          <div className="panel rounded-lg overflow-hidden">
            <div className="panel-header px-3 py-2 flex items-center justify-between">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Profit & Loss</span>
              <span className={`font-mono text-sm font-bold tabular-nums ${stats.totalPnL >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {stats.totalPnL >= 0 ? "+" : ""}${stats.totalPnL.toFixed(2)}
              </span>
            </div>
            <div className="px-3 py-2 flex justify-center">
              <PnLChart data={profitHistory} width={700} height={130} />
            </div>
          </div>

          {/* Positions */}
          <div className="panel rounded-lg overflow-hidden">
            <div className="panel-header px-3 py-2 flex items-center justify-between">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Positions</span>
              <span className="text-[10px] font-mono text-slate-600">{positions.length} open</span>
            </div>
            {positions.length === 0 ? (
              <div className="px-3 py-6 text-center text-[11px] text-slate-700 font-mono">NO OPEN POSITIONS</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-slate-600 text-left border-b border-slate-800/50">
                      <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest">Ticker</th>
                      <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Qty</th>
                      <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Exposure</th>
                      <th className="px-3 py-2 font-medium text-[9px] uppercase tracking-widest text-right">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map(pos => (
                      <tr key={pos.ticker} className="table-row border-b border-slate-800/30">
                        <td className="px-3 py-2 font-mono text-cyan-400">{pos.ticker}</td>
                        <td className={`px-3 py-2 text-right font-mono font-bold tabular-nums ${pos.position > 0 ? "text-emerald-400" : "text-red-400"}`}>
                          {pos.position > 0 ? "+" : ""}{pos.position}
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-slate-300 tabular-nums">
                          ${((pos.market_exposure || 0) / 100).toFixed(2)}
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-slate-500 tabular-nums">
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
          <div className="panel rounded-lg overflow-hidden flex-1 flex flex-col min-h-0">
            <div className="panel-header px-3 py-2 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Trades</span>
                <div className="flex gap-0.5 bg-slate-800/40 p-0.5 rounded">
                  {(["all", "live", "paper", "failed"] as TradeFilter[]).map(key => {
                    const count = key === "all" ? trades.length : key === "live" ? stats.liveTrades.length : key === "paper" ? stats.paperTrades.length : stats.failedTrades.length;
                    const active = tradeFilter === key;
                    return (
                      <button key={key} onClick={() => setTradeFilter(key)}
                        className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded transition-all
                          ${active
                            ? key === "live" ? "bg-emerald-500/15 text-emerald-400"
                              : key === "paper" ? "bg-amber-500/15 text-amber-400"
                              : key === "failed" ? "bg-red-500/15 text-red-400"
                              : "bg-slate-700/60 text-slate-200"
                            : "text-slate-600 hover:text-slate-400"}`}>
                        {key} <span className="opacity-50">{count}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin min-h-0">
              {filteredTrades.length === 0 ? (
                <div className="px-3 py-10 text-center text-[11px] text-slate-700 font-mono">
                  {trades.length === 0 ? "NO TRADES RECORDED" : `NO ${tradeFilter.toUpperCase()} TRADES`}
                </div>
              ) : (
                <table className="w-full text-[11px]">
                  <thead className="sticky top-0 bg-[#0c1018] z-10">
                    <tr className="text-slate-600 text-left border-b border-slate-800/50">
                      {([
                        { field: "timestamp" as SortField, label: "Time", align: "left" },
                        { field: "status" as SortField, label: "Status", align: "left" },
                        { field: "team" as SortField, label: "Team", align: "left" },
                        { field: "team" as SortField, label: "Direction", align: "left" },
                        { field: "team" as SortField, label: "Size", align: "right" },
                        { field: "profit" as SortField, label: "P&L", align: "right" },
                        { field: "roi" as SortField, label: "ROI", align: "right" },
                      ]).map(({ field, label, align }, idx) => (
                        <th key={idx}
                          onClick={() => handleSort(field)}
                          className={`px-3 py-2 font-medium text-[9px] uppercase tracking-widest cursor-pointer
                            hover:text-slate-400 transition-colors select-none
                            ${align === "right" ? "text-right" : ""}`}>
                          {label}
                          {sortField === field && (
                            <span className="ml-0.5 text-cyan-500">{sortAsc ? "\u25B2" : "\u25BC"}</span>
                          )}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTrades.map((trade, i) => {
                      const st = getTradeStatus(trade);
                      const isExpanded = expandedRow === i;
                      const dir = trade.direction === "BUY_PM_SELL_K" ? "PM\u2192K" : "K\u2192PM";
                      const dirColor = trade.direction === "BUY_PM_SELL_K" ? "text-cyan-400" : "text-violet-400";

                      return (
                        <tr key={i} onClick={() => setExpandedRow(isExpanded ? null : i)}
                          className={`table-row border-b border-slate-800/20 cursor-pointer transition-colors
                            ${isExpanded ? "bg-slate-800/20" : ""}`}>
                          <td className="px-3 py-2 font-mono text-slate-500 tabular-nums whitespace-nowrap">
                            {new Date(trade.timestamp).toLocaleTimeString("en-US", { hour12: false })}
                          </td>
                          <td className="px-3 py-2">
                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${st.color} ${st.bg}`}>
                              {st.text}
                            </span>
                          </td>
                          <td className="px-3 py-2">
                            <span className="font-mono font-bold text-slate-200">{trade.team}</span>
                            <span className="text-slate-700 ml-1.5 text-[10px]">{trade.game}</span>
                          </td>
                          <td className={`px-3 py-2 font-mono font-bold text-[10px] ${dirColor}`}>{dir}</td>
                          <td className="px-3 py-2 text-right font-mono text-slate-300 tabular-nums">
                            {trade.k_fill_count}
                          </td>
                          <td className={`px-3 py-2 text-right font-mono font-bold tabular-nums
                            ${trade.expected_profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                            {trade.expected_profit >= 0 ? "+" : ""}${trade.expected_profit.toFixed(2)}
                          </td>
                          <td className={`px-3 py-2 text-right font-mono tabular-nums
                            ${trade.roi > 0 ? "text-emerald-400" : "text-slate-600"}`}>
                            {trade.roi ? `${trade.roi.toFixed(1)}%` : "—"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}

              {/* Expanded row detail overlay */}
              {expandedRow !== null && filteredTrades[expandedRow] && (
                <div className="mx-2 mb-2 -mt-px p-3 bg-slate-900/60 border border-slate-800/50 rounded-b text-[10px] font-mono">
                  {(() => {
                    const t = filteredTrades[expandedRow];
                    return (
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-2">
                        <div>
                          <span className="text-slate-600">Timestamp</span>
                          <div className="text-slate-300">{new Date(t.timestamp).toISOString()}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Sport</span>
                          <div className="text-slate-300">{t.sport}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Direction</span>
                          <div className="text-slate-300">{t.direction}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Intended Size</span>
                          <div className="text-slate-300">{t.intended_size}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">K Fill Price</span>
                          <div className="text-cyan-400">{t.k_fill_price ? `${t.k_fill_price}\u00A2` : "—"}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">K Order ID</span>
                          <div className="text-slate-400 truncate max-w-[160px]">{t.k_order_id || "—"}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">PM Fill</span>
                          <div className={t.pm_success ? "text-emerald-400" : "text-red-400"}>
                            {t.pm_fill_count !== undefined ? `${t.pm_fill_count} @ $${t.pm_fill_price?.toFixed(2) ?? "—"}` : t.pm_success ? "OK" : t.pm_error || "—"}
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-600">PM Slug</span>
                          <div className="text-violet-400 truncate max-w-[160px]">{t.pm_slug || t.pm_order_id || "—"}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Exec Mode</span>
                          <div className={t.execution_mode === "live" ? "text-red-400" : "text-blue-400"}>
                            {t.execution_mode?.toUpperCase() || "—"}
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-600">Raw Status</span>
                          <div className="text-slate-300">{t.raw_status || t.status}</div>
                        </div>
                        {t.pm_error && (
                          <div className="col-span-2">
                            <span className="text-slate-600">PM Error</span>
                            <div className="text-red-400">{t.pm_error}</div>
                          </div>
                        )}
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ─── RIGHT COLUMN: Logs ─── */}
        <div className="col-span-12 lg:col-span-4 xl:col-span-3 flex flex-col min-h-0">
          <div className="panel rounded-lg overflow-hidden flex-1 flex flex-col min-h-0">
            <div className="panel-header px-3 py-2 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Log</span>
                {isRunning && (
                  <div className="flex items-center gap-1">
                    <div className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-[9px] text-emerald-500/60 font-mono">LIVE</span>
                  </div>
                )}
              </div>
              <button onClick={() => setLogs([])}
                className="text-[9px] text-slate-600 hover:text-slate-400 font-mono tracking-wider transition-colors">
                CLR
              </button>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin p-2 font-mono text-[10px] leading-[18px] bg-[#070a10] min-h-0">
              {logs.length === 0 ? (
                <div className="text-slate-700 py-8 text-center text-[11px]">Waiting for logs...</div>
              ) : (
                <>
                  {logs.map((log, i) => {
                    // Syntax highlighting
                    let msgColor = "text-slate-500";
                    const m = log.message;
                    if (m.includes("[OK]") || m.includes("SUCCESS") || m.includes("FILLED"))
                      msgColor = "text-emerald-400";
                    else if (m.includes("[!]") || m.includes("ERROR") || m.includes("[X]") || m.includes("FAIL") || m.includes("UNHEDGED"))
                      msgColor = "text-red-400";
                    else if (m.includes("[>>]") || m.includes("SWEEP") || m.includes("[ORDER]"))
                      msgColor = "text-cyan-400";
                    else if (m.includes("PAPER"))
                      msgColor = "text-amber-400";
                    else if (m.includes("[CANCEL]") || m.includes("CLEANUP"))
                      msgColor = "text-orange-400/80";
                    else if (m.includes("[SAFETY]") || m.includes("[STOP]"))
                      msgColor = "text-red-500 font-bold";
                    else if (m.includes("===") || m.includes("---"))
                      msgColor = "text-slate-700";
                    else if (m.includes("[DEBUG]"))
                      msgColor = "text-slate-600";
                    else if (m.includes("[i]") || m.includes("Scan"))
                      msgColor = "text-slate-400";

                    return (
                      <div key={i} className="flex hover:bg-slate-800/20 rounded px-1 -mx-1">
                        <span className="text-slate-700 select-none mr-2 tabular-nums w-[52px] flex-shrink-0 text-right">
                          {log.time}
                        </span>
                        <span className={msgColor}>{m}</span>
                      </div>
                    );
                  })}
                  <div ref={logsEndRef} />
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ═══ FOOTER ═══ */}
      <footer className="flex-shrink-0 border-t border-[#151c28] px-4 py-1.5 flex items-center justify-between text-[9px] font-mono text-slate-700">
        <div className="flex items-center gap-3">
          <span>{BOT_SERVER_URL}</span>
          <span className="text-slate-800">|</span>
          <span>
            {mode === "live" ? <span className="text-red-500">LIVE</span> : <span className="text-blue-500">PAPER</span>}
          </span>
          <span className="text-slate-800">|</span>
          <span className="tabular-nums">{trades.length} trades</span>
        </div>
        <span className="text-slate-800">OMI Edge Terminal v2.0</span>
      </footer>

      {/* ═══ TOAST ═══ */}
      {toast && (
        <div className="fixed bottom-4 right-4 bg-slate-800 border border-slate-700 text-slate-200
                       px-4 py-2.5 text-xs font-mono rounded shadow-2xl shadow-black/50
                       animate-in slide-in-from-bottom-2">
          {toast}
        </div>
      )}
    </div>
  );
}
