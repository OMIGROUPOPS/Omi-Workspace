"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import type {
  ActiveTab,
  BotStatus,
  ConnectionStatus,
  LogEntry,
  Position,
  ScanInfo,
  Trade,
} from "@/lib/trading/types";
import { WS_URL } from "@/lib/trading/config";
import {
  fetchStatus,
  fetchTrades,
  startBot,
  stopBot,
  setMode,
  clearData,
  measureLatency,
} from "@/lib/trading/api";
import { computeFullAnalytics } from "@/lib/trading/analytics";

import TradingHeader from "@/components/trading/TradingHeader";
import TradingSidebar from "@/components/trading/TradingSidebar";
import TradingFooter from "@/components/trading/TradingFooter";
import DashboardTab from "@/components/trading/tabs/DashboardTab";
import TradesTab from "@/components/trading/tabs/TradesTab";
import ResearchTab from "@/components/trading/tabs/ResearchTab";
import LogsTab from "@/components/trading/tabs/LogsTab";

export default function TradingDashboard() {
  // ── State ──
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("disconnected");
  const [botState, setBotState] = useState<BotStatus["bot_state"]>("stopped");
  const [mode, setModeState] = useState<"paper" | "live">("paper");
  const [balance, setBalance] = useState<number | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pmBalance] = useState<number>(494.90);
  const [toast, setToast] = useState<string | null>(null);
  const [scanInfo, setScanInfo] = useState<ScanInfo>({
    scanNumber: 0, gamesFound: 0, arbsFound: 0, isScanning: false,
  });
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [uptime, setUptime] = useState("00:00:00");
  const [latency, setLatency] = useState<number | null>(null);
  const [profitHistory, setProfitHistory] = useState<number[]>([0]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeTab, setActiveTab] = useState<ActiveTab>("dashboard");

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ── Derived ──
  const isRunning = botState === "running";
  const combinedBalance = (balance || 0) + pmBalance;

  // ── Analytics ──
  const analytics = useMemo(() => computeFullAnalytics(trades), [trades]);

  useEffect(() => {
    setProfitHistory((prev) => [...prev, analytics.totalPnL].slice(-50));
  }, [analytics.totalPnL]);

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
      setScanInfo((prev) => ({ ...prev, scanNumber: parseInt(scanMatch[1]), isScanning: true, arbsFound: 0 }));
      return;
    }
    const gamesMatch = message.match(/Games:\s*(\d+)|(\d+)\s*games/i);
    if (gamesMatch) {
      setScanInfo((prev) => ({ ...prev, gamesFound: parseInt(gamesMatch[1] || gamesMatch[2]) }));
      return;
    }
    const arbsMatch = message.match(/(\d+)\s*arb|Found\s*(\d+)/i);
    if (arbsMatch) {
      const count = parseInt(arbsMatch[1] || arbsMatch[2]);
      if (count >= 0 && count <= 100) {
        setScanInfo((prev) => ({ ...prev, arbsFound: count }));
      }
      return;
    }
    if (message.includes("Sleeping") || message.includes("sleep")) {
      setScanInfo((prev) => ({ ...prev, isScanning: false }));
    }
  }, []);

  // ── Helpers ──
  const addLog = useCallback((message: string) => {
    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev.slice(-500), { time, message }]);
  }, []);

  const showToast = useCallback((message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
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
      measureLatency().then(setLatency);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        switch (message.type) {
          case "state":
            setBotState(message.data.bot_state);
            setModeState(message.data.mode);
            break;
          case "status":
            setBotState(message.data.bot_state);
            setModeState(message.data.mode);
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
  }, [parseScanInfo]);

  useEffect(() => {
    connectWebSocket();

    const loadData = async () => {
      const [status, tradesData] = await Promise.all([fetchStatus(), fetchTrades()]);
      if (status) {
        setBotState(status.bot_state);
        setModeState(status.mode);
        setBalance(status.balance);
        setPositions(status.positions || []);
      }
      setTrades(tradesData);
    };
    loadData();

    const statusInterval = setInterval(async () => {
      const [status, tradesData, lat] = await Promise.all([
        fetchStatus(),
        fetchTrades(),
        measureLatency(),
      ]);
      if (status) {
        setBotState(status.bot_state);
        setModeState(status.mode);
        setBalance(status.balance);
        setPositions(status.positions || []);
      }
      setTrades(tradesData);
      setLatency(lat);
    }, 5000);

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
  }, [connectWebSocket]);

  // ── Actions ──
  const handleStart = async () => {
    setIsLoading(true);
    setError(null);
    const result = await startBot();
    if (result.ok) addLog("[DASHBOARD] Start command sent");
    else setError(result.error || "Failed to start bot");
    setIsLoading(false);
  };

  const handleStop = async () => {
    setIsLoading(true);
    setError(null);
    const result = await stopBot();
    if (result.ok) addLog("[DASHBOARD] Stop command sent");
    else setError(result.error || "Failed to stop bot");
    setIsLoading(false);
  };

  const handleModeChange = async (newMode: "paper" | "live") => {
    if (botState === "running") { setError("Stop the bot before changing mode"); return; }
    setIsLoading(true);
    setError(null);
    const result = await setMode(newMode);
    if (result.ok) {
      setModeState(newMode);
      addLog(`[DASHBOARD] Mode changed to ${newMode.toUpperCase()}`);
    } else {
      setError(result.error || "Failed to change mode");
    }
    setIsLoading(false);
  };

  const handleClearData = async () => {
    if (!confirm("Clear all trade history and logs? This cannot be undone.")) return;
    const ok = await clearData();
    if (ok) { setTrades([]); setLogs([]); setProfitHistory([0]); showToast("All data cleared"); }
    else showToast("Failed to clear data");
  };

  // ── Render ──
  return (
    <div className="min-h-screen bg-[#07090e] text-slate-200 selection:bg-cyan-500/30 flex flex-col">
      {/* CSS Animations */}
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

      {/* Header */}
      <TradingHeader
        currentTime={currentTime}
        mode={mode}
        botState={botState}
        isRunning={isRunning}
        connectionStatus={connectionStatus}
        scanInfo={scanInfo}
        fillRate={analytics.fillRate}
        uptime={uptime}
        latency={latency}
      />

      {/* Error Banner */}
      {error && (
        <div className="flex-shrink-0 mx-4 mt-2 bg-red-500/8 border border-red-500/20 text-red-400 px-4 py-2 text-xs font-mono flex items-center justify-between rounded">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400/40 hover:text-red-400 ml-4">x</button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex gap-0 p-2 min-h-0 overflow-hidden">
        {/* Sidebar */}
        <TradingSidebar
          mode={mode}
          botState={botState}
          isRunning={isRunning}
          isLoading={isLoading}
          balance={balance}
          pmBalance={pmBalance}
          combinedBalance={combinedBalance}
          stats={{
            liveTrades: analytics.liveTrades,
            paperTrades: analytics.paperTrades,
            failedTrades: analytics.failedTrades,
            fillRate: analytics.fillRate,
            lastSuccessfulTrade: analytics.lastSuccessfulTrade,
          }}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onStart={handleStart}
          onStop={handleStop}
          onModeChange={handleModeChange}
          onClearData={handleClearData}
        />

        {/* Tab Content */}
        <div className="flex-1 min-h-0 pl-2">
          {activeTab === "dashboard" && (
            <DashboardTab
              trades={trades}
              positions={positions}
              profitHistory={profitHistory}
              analytics={analytics}
            />
          )}
          {activeTab === "trades" && (
            <TradesTab trades={trades} analytics={analytics} />
          )}
          {activeTab === "research" && (
            <ResearchTab analytics={analytics} />
          )}
          {activeTab === "logs" && (
            <LogsTab
              logs={logs}
              isRunning={isRunning}
              onClearLogs={() => setLogs([])}
            />
          )}
        </div>
      </div>

      {/* Footer */}
      <TradingFooter mode={mode} tradeCount={trades.length} />

      {/* Toast */}
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
