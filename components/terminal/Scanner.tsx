"use client";

// OMI Terminal — Scanner / Signal feed (Visual Overhaul v3)
// Severity pills, strategy tags, full market names, cleaner rows.
// Props interface preserved: { signals, filter, onFilterChange }

import { useState, useEffect, useMemo, useRef } from "react";
import type { ScanSignal, ScanType } from "@/lib/terminal/types";
import { parseTickerLabel } from "@/lib/terminal/ticker-labels";

interface ScannerProps {
  signals?: ScanSignal[];
  filter?: ScanType | null;
  onFilterChange?: (f: ScanType | null) => void;
}

// Strategy tags with colors
const STRAT_TAG: Record<string, { label: string; color: string; bg: string }> = {
  resolution:          { label: "RES",  color: "#00FF88", bg: "rgba(0,255,136,0.12)" },
  momentum_lag:        { label: "MTM",  color: "#FFD600", bg: "rgba(255,214,0,0.12)" },
  contradiction_mono:  { label: "MONO", color: "#c084fc", bg: "rgba(192,132,252,0.12)" },
  contradiction_cross: { label: "XCON", color: "#c084fc", bg: "rgba(192,132,252,0.12)" },
  whale_momentum:      { label: "WHL",  color: "#00BCD4", bg: "rgba(0,188,212,0.12)" },
};

// Severity styles
const SEV_STYLE: Record<string, { color: string; bg: string; border: string; pill: string; pillText: string }> = {
  HIGH:   { color: "#FF3366", bg: "rgba(255,51,102,0.04)", border: "#FF3366", pill: "#FF3366", pillText: "#fff" },
  MEDIUM: { color: "#FF6600", bg: "rgba(255,102,0,0.03)", border: "#FF6600", pill: "#FF6600", pillText: "#000" },
  LOW:    { color: "#00BCD4", bg: "transparent",           border: "#1a1a1a", pill: "rgba(0,188,212,0.15)", pillText: "#00BCD4" },
};

function formatTimestamp(ts: number): string {
  const d = new Date(ts);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
}

function relativeTime(ts: number): string {
  const secs = Math.max(0, Math.floor((Date.now() - ts) / 1000));
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m`;
  const hrs = Math.floor(mins / 60);
  return `${hrs}h`;
}

function formatDescription(desc: string): React.ReactNode[] {
  const segments = desc.split(/\s{2,}/);
  const result: React.ReactNode[] = [];
  segments.forEach((seg, si) => {
    if (si > 0) {
      result.push(
        <span key={`sep-${si}`} style={{ color: "#2a2a2a", margin: "0 3px" }}>·</span>
      );
    }
    const parts = seg.split(/(\d+\.?\d*(?:c|¢|ct|s|%|L)?|@\d+\.?\d*s?)/g);
    parts.forEach((part, pi) => {
      if (/^\d+\.?\d*(?:c|¢|ct|s|%|L)?$/.test(part) || /^@\d+/.test(part)) {
        result.push(<span key={`${si}-${pi}`} style={{ color: "#eee", fontWeight: 600 }}>{part}</span>);
      } else {
        result.push(<span key={`${si}-${pi}`}>{part}</span>);
      }
    });
  });
  return result;
}

export default function Scanner({ signals = [], filter, onFilterChange }: ScannerProps) {
  // Re-render every 5s to update relative times
  const [, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 5000);
    return () => clearInterval(id);
  }, []);

  const seenKeysRef = useRef<Set<string>>(new Set());

  // Deduplicate: same ticker + same strategy within 30s
  const deduped = useMemo(() => {
    const seen = new Map<string, ScanSignal>();
    for (const sig of signals) {
      const key = `${sig.ticker}:${sig.scan_type}`;
      const existing = seen.get(key);
      if (!existing) {
        seen.set(key, sig);
      } else {
        const gap = Math.abs((sig.timestamp || 0) - (existing.timestamp || 0));
        if (gap < 30000) {
          if ((sig.timestamp || 0) > (existing.timestamp || 0)) {
            seen.set(key, sig);
          }
        }
      }
    }
    return Array.from(seen.values());
  }, [signals]);

  const filtered = filter ? deduped.filter((s) => s.scan_type === filter) : deduped;

  // Track new signals for fade-in
  const newSignalKeys = useMemo(() => {
    const newKeys = new Set<string>();
    for (const sig of filtered) {
      const key = `${sig.ticker}:${sig.timestamp}`;
      if (!seenKeysRef.current.has(key)) {
        newKeys.add(key);
      }
    }
    for (const sig of filtered) {
      seenKeysRef.current.add(`${sig.ticker}:${sig.timestamp}`);
    }
    if (seenKeysRef.current.size > 500) {
      const arr = Array.from(seenKeysRef.current);
      seenKeysRef.current = new Set(arr.slice(-300));
    }
    return newKeys;
  }, [filtered]);

  const filterButtons: { type: ScanType | null; label: string }[] = [
    { type: null, label: "ALL" },
    { type: "resolution", label: "RES" },
    { type: "momentum_lag", label: "MTM" },
    { type: "contradiction_mono", label: "MONO" },
    { type: "whale_momentum", label: "WHL" },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header + filter bar */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "4px",
        paddingBottom: "4px",
        borderBottom: "1px solid #1a1a1a",
      }}>
        <div style={{ display: "flex", gap: "3px", alignItems: "center" }}>
          {filterButtons.map(({ type, label }) => {
            const active = filter === type;
            const strat = type ? STRAT_TAG[type] : null;
            return (
              <button
                key={label}
                onClick={() => onFilterChange?.(type)}
                style={{
                  fontSize: "8px",
                  padding: "2px 6px",
                  borderRadius: "3px",
                  border: active
                    ? `1px solid ${type === null ? "#FF6600" : (strat?.color || "#555")}40`
                    : "1px solid #1a1a1a",
                  cursor: "pointer",
                  fontWeight: 600,
                  letterSpacing: "0.04em",
                  background: active
                    ? type === null ? "rgba(255,102,0,0.1)" : strat?.bg || "#333"
                    : "transparent",
                  color: active
                    ? type === null ? "#FF6600" : strat?.color || "#fff"
                    : "#444",
                  transition: "all 0.12s",
                  fontFamily: "inherit",
                }}
              >
                {label}
              </button>
            );
          })}
        </div>
        <span style={{ fontSize: "9px", color: "#444", fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>
          {filtered.length}
        </span>
      </div>

      {/* Signal list */}
      <div
        className="flex-1 overflow-y-auto"
        style={{ scrollbarWidth: "none" }}
      >
        {filtered.length === 0 ? (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            color: "#333",
            fontSize: "9px",
            gap: "8px",
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              border: "1px solid #1a1a1a",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              animation: "terminal-pulse 2s ease-in-out infinite",
            }}>
              <span style={{ fontSize: "14px", color: "#222" }}>◈</span>
            </div>
            <span>Scanning for signals...</span>
          </div>
        ) : (
          filtered.map((sig, i) => {
            const sev = SEV_STYLE[sig.severity] || SEV_STYLE.LOW;
            const strat = STRAT_TAG[sig.scan_type] || { label: "SIG", color: "#888", bg: "rgba(136,136,136,0.1)" };
            const sigKey = `${sig.ticker}:${sig.timestamp}`;
            const isNew = newSignalKeys.has(sigKey);
            const isFirst = i === 0;
            const isRecentFirst = isFirst && sig.timestamp && (Date.now() - sig.timestamp) < 10000;

            // Parse ticker label
            const eventTicker = sig.ticker.replace(/-[YN]$/, "");
            const sigParts = sig.ticker.split("-");
            let rawTeam = sigParts.length >= 3 ? sigParts[sigParts.length - 2] : sigParts[sigParts.length - 1] || sig.ticker.slice(-8);
            if (/^\d+[A-Z]+\d+/.test(rawTeam) && sigParts.length >= 4) {
              rawTeam = sigParts[sigParts.length - 3] || rawTeam;
            }
            const tickerLabel = parseTickerLabel(sig.ticker, rawTeam, eventTicker);

            return (
              <div
                key={`${sig.ticker}-${sig.timestamp}-${i}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                  padding: "4px 5px",
                  background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)",
                  cursor: "pointer",
                  borderLeft: `2px solid ${sev.border}`,
                  transition: "background 0.08s",
                  animation: isNew ? "terminal-signal-in 0.6s ease-out" : "none",
                  borderRadius: "0 2px 2px 0",
                  marginBottom: "1px",
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "#131313"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"; }}
              >
                {/* Timestamp */}
                {sig.timestamp && (
                  <span style={{
                    fontSize: "7px",
                    color: "#3a3a3a",
                    fontVariantNumeric: "tabular-nums",
                    flexShrink: 0,
                    minWidth: "38px",
                  }} suppressHydrationWarning>
                    {formatTimestamp(sig.timestamp)}
                  </span>
                )}

                {/* Severity pill */}
                <span
                  style={{
                    fontSize: "7px",
                    fontWeight: 700,
                    padding: "1px 4px",
                    borderRadius: "2px",
                    background: sev.pill,
                    color: sev.pillText,
                    lineHeight: "11px",
                    letterSpacing: "0.02em",
                    flexShrink: 0,
                    minWidth: "12px",
                    textAlign: "center",
                  }}
                >
                  {sig.severity.charAt(0)}
                </span>

                {/* Strategy tag */}
                <span
                  style={{
                    fontSize: "7px",
                    fontWeight: 600,
                    padding: "1px 5px",
                    borderRadius: "2px",
                    background: strat.bg,
                    color: strat.color,
                    lineHeight: "11px",
                    letterSpacing: "0.04em",
                    flexShrink: 0,
                  }}
                >
                  {strat.label}
                </span>

                {/* NEW badge */}
                {isRecentFirst && (
                  <span
                    style={{
                      fontSize: "6px",
                      fontWeight: 700,
                      padding: "1px 4px",
                      borderRadius: "2px",
                      background: "rgba(0,255,136,0.15)",
                      color: "#00FF88",
                      lineHeight: "10px",
                      letterSpacing: "0.04em",
                      flexShrink: 0,
                      animation: "terminal-new-badge 10s forwards",
                    }}
                  >
                    NEW
                  </span>
                )}

                {/* Ticker label + Description */}
                <span
                  style={{
                    fontSize: "8px",
                    color: "#666",
                    flex: 1,
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                    minWidth: 0,
                  }}
                >
                  <span style={{ color: "#bbb", fontWeight: 600 }}>{tickerLabel}</span>
                  <span style={{ color: "#1e1e1e", margin: "0 4px" }}>·</span>
                  <span style={{ color: "#666" }}>{formatDescription(sig.description)}</span>
                </span>

                {/* Depth */}
                {sig.depth > 0 && (
                  <span style={{
                    fontSize: "8px",
                    color: "#555",
                    fontVariantNumeric: "tabular-nums",
                    flexShrink: 0,
                    background: "rgba(255,255,255,0.03)",
                    padding: "1px 3px",
                    borderRadius: "2px",
                  }}>
                    {sig.depth}
                  </span>
                )}

                {/* Relative time */}
                {sig.timestamp && (
                  <span style={{
                    fontSize: "8px",
                    color: "#444",
                    fontVariantNumeric: "tabular-nums",
                    flexShrink: 0,
                    minWidth: "18px",
                    textAlign: "right",
                  }}>
                    {relativeTime(sig.timestamp)}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
