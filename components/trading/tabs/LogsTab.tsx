"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import type { LogEntry, LogLevel } from "@/lib/trading/types";
import Panel from "../shared/Panel";

interface LogsTabProps {
  logs: LogEntry[];
  isRunning: boolean;
  onClearLogs: () => void;
}

const LOG_LEVELS: LogLevel[] = ["ALL", "SUCCESS", "ERROR", "ORDER", "INFO"];

function getLogLevel(message: string): LogLevel {
  if (message.includes("[OK]") || message.includes("SUCCESS") || message.includes("FILLED"))
    return "SUCCESS";
  if (message.includes("[!]") || message.includes("ERROR") || message.includes("[X]") || message.includes("FAIL") || message.includes("UNHEDGED"))
    return "ERROR";
  if (message.includes("[>>]") || message.includes("SWEEP") || message.includes("[ORDER]"))
    return "ORDER";
  return "INFO";
}

function getLogColor(message: string): string {
  if (message.includes("[OK]") || message.includes("SUCCESS") || message.includes("FILLED"))
    return "text-emerald-400";
  if (message.includes("[!]") || message.includes("ERROR") || message.includes("[X]") || message.includes("FAIL") || message.includes("UNHEDGED"))
    return "text-red-400";
  if (message.includes("[>>]") || message.includes("SWEEP") || message.includes("[ORDER]"))
    return "text-cyan-400";
  if (message.includes("PAPER"))
    return "text-amber-400";
  if (message.includes("[CANCEL]") || message.includes("CLEANUP"))
    return "text-orange-400/80";
  if (message.includes("[SAFETY]") || message.includes("[STOP]"))
    return "text-red-500 font-bold";
  if (message.includes("===") || message.includes("---"))
    return "text-slate-700";
  if (message.includes("[DEBUG]"))
    return "text-slate-600";
  if (message.includes("[i]") || message.includes("Scan"))
    return "text-slate-400";
  return "text-slate-500";
}

export default function LogsTab({ logs, isRunning, onClearLogs }: LogsTabProps) {
  const [levelFilter, setLevelFilter] = useState<LogLevel>("ALL");
  const [searchText, setSearchText] = useState("");
  const logsEndRef = useRef<HTMLDivElement>(null);

  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (levelFilter !== "ALL" && getLogLevel(log.message) !== levelFilter) return false;
      if (searchText && !log.message.toLowerCase().includes(searchText.toLowerCase())) return false;
      return true;
    });
  }, [logs, levelFilter, searchText]);

  const levelCounts = useMemo(() => {
    const counts: Record<LogLevel, number> = { ALL: logs.length, SUCCESS: 0, ERROR: 0, ORDER: 0, INFO: 0 };
    for (const log of logs) {
      const level = getLogLevel(log.message);
      counts[level]++;
    }
    return counts;
  }, [logs]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [filteredLogs]);

  return (
    <div className="flex flex-col h-full min-h-0">
      <Panel
        title="Log"
        className="flex-1 flex flex-col min-h-0"
        headerRight={
          <div className="flex items-center gap-2">
            {isRunning && (
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[9px] text-emerald-500/60 font-mono">LIVE</span>
              </div>
            )}
            <button
              onClick={onClearLogs}
              className="text-[9px] text-slate-600 hover:text-slate-400 font-mono tracking-wider transition-colors"
            >
              CLR
            </button>
          </div>
        }
      >
        {/* Filter bar */}
        <div className="px-3 py-2 flex items-center gap-2 border-b border-slate-800/30">
          <div className="flex gap-0.5 bg-slate-800/40 p-0.5 rounded">
            {LOG_LEVELS.map((level) => {
              const active = levelFilter === level;
              const colorMap: Record<LogLevel, string> = {
                ALL: "bg-slate-700/60 text-slate-200",
                SUCCESS: "bg-emerald-500/15 text-emerald-400",
                ERROR: "bg-red-500/15 text-red-400",
                ORDER: "bg-cyan-500/15 text-cyan-400",
                INFO: "bg-slate-700/60 text-slate-300",
              };
              return (
                <button
                  key={level}
                  onClick={() => setLevelFilter(level)}
                  className={`px-2 py-0.5 text-[9px] font-bold tracking-wider rounded transition-all
                    ${active ? colorMap[level] : "text-slate-600 hover:text-slate-400"}`}
                >
                  {level} <span className="opacity-50">{levelCounts[level]}</span>
                </button>
              );
            })}
          </div>
          <input
            type="text"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="Search logs..."
            className="flex-1 bg-slate-800/30 border border-slate-700/30 rounded px-2 py-1 text-[10px] font-mono
              text-slate-300 placeholder:text-slate-700 outline-none focus:border-slate-600 transition-colors"
          />
        </div>

        {/* Log viewer */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-2 font-mono text-[10px] leading-[18px] bg-[#070a10] min-h-0">
          {filteredLogs.length === 0 ? (
            <div className="text-slate-700 py-8 text-center text-[11px]">
              {logs.length === 0 ? "Waiting for logs..." : "No matching logs"}
            </div>
          ) : (
            <>
              {filteredLogs.map((log, i) => (
                <div key={i} className="flex hover:bg-slate-800/20 rounded px-1 -mx-1">
                  <span className="text-slate-700 select-none mr-2 tabular-nums w-[52px] flex-shrink-0 text-right">
                    {log.time}
                  </span>
                  <span className={getLogColor(log.message)}>{log.message}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </>
          )}
        </div>
      </Panel>
    </div>
  );
}
