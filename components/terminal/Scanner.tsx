"use client";

// OMI Terminal — Scanner / Signal feed (Modular Box v4)
// Inner content of parent TermBox — no outer border/header.
// Severity pills, strategy tags, two-line signal rows, fade-in, filter bar.

import { useState, useEffect, useMemo, useRef } from "react";
import type { ReactNode } from "react";
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
  HIGH:   { color: "#FF3366", bg: "rgba(255,51,102,0.04)",  border: "#FF3366", pill: "#FF3366",              pillText: "#fff" },
  MEDIUM: { color: "#FF6600", bg: "rgba(255,102,0,0.03)",   border: "#FF6600", pill: "#FF6600",              pillText: "#000" },
  LOW:    { color: "#00BCD4", bg: "transparent",            border: "#1a1a1a", pill: "rgba(0,188,212,0.15)", pillText: "#00BCD4" },
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

function formatDescription(desc: string): ReactNode[] {
  const segments = desc.split(/\s{2,}/);
  const result: ReactNode[] = [];
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
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "transparent",
      }}
    >
      {/* Filter buttons bar */}
      <div
        style={{
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          gap: "3px",
          paddingBottom: "6px",
          borderBottom: "1px solid #141414",
          marginBottom: "4px",
        }}
      >
        {filterButtons.map(({ type, label }) => {
          const active = filter === type;
          const strat = type ? STRAT_TAG[type] : null;
          const activeColor = type === null ? "#FF6600" : (strat?.color || "#888");
          const activeBg = type === null ? "rgba(255,102,0,0.1)" : (strat?.bg || "rgba(136,136,136,0.1)");

          return (
            <button
              key={label}
              onClick={() => onFilterChange?.(type)}
              style={{
                fontSize: "8px",
                padding: "2px 7px",
                borderRadius: "3px",
                border: active
                  ? `1px solid ${activeColor}40`
                  : "1px solid #1a1a1a",
                cursor: "pointer",
                fontWeight: 700,
                letterSpacing: "0.05em",
                background: active ? activeBg : "transparent",
                color: active ? activeColor : "#3a3a3a",
                transition: "all 0.12s",
                fontFamily: "inherit",
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  e.currentTarget.style.color = "#666";
                  e.currentTarget.style.borderColor = "#2a2a2a";
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  e.currentTarget.style.color = "#3a3a3a";
                  e.currentTarget.style.borderColor = "#1a1a1a";
                }
              }}
            >
              {label}
            </button>
          );
        })}

        {/* Signal count badge */}
        <span
          style={{
            marginLeft: "auto",
            fontSize: "8px",
            color: "#333",
            fontVariantNumeric: "tabular-nums",
            fontWeight: 600,
          }}
        >
          {filtered.length}
        </span>
      </div>

      {/* Signal list */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          scrollbarWidth: "none",
        }}
      >
        {filtered.length === 0 ? (
          // Empty state: centered pulsing icon
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#2a2a2a",
              fontSize: "9px",
              gap: "10px",
            }}
          >
            <div
              style={{
                width: "30px",
                height: "30px",
                borderRadius: "50%",
                border: "1px solid #181818",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                animation: "terminal-pulse 2s ease-in-out infinite",
              }}
            >
              <span style={{ fontSize: "13px", color: "#1e1e1e" }}>◈</span>
            </div>
            <span style={{ letterSpacing: "0.06em", textTransform: "uppercase", fontSize: "8px" }}>
              Scanning for signals...
            </span>
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
                  padding: "5px 6px 5px 0",
                  borderLeft: `2px solid ${sev.border}`,
                  borderBottom: "1px solid #0f0f0f",
                  background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.008)",
                  cursor: "pointer",
                  transition: "background 0.08s",
                  animation: isNew ? "terminal-signal-in 0.6s ease-out" : "none",
                  borderRadius: "0 2px 2px 0",
                  marginBottom: "1px",
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = "#121212"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.008)"; }}
              >
                {/* Line 1: Severity pill · Strategy tag · Ticker · Relative time */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    paddingLeft: "5px",
                    marginBottom: "3px",
                  }}
                >
                  {/* Severity pill — single char H/M/L */}
                  <span
                    style={{
                      fontSize: "7px",
                      fontWeight: 800,
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
                      fontWeight: 700,
                      padding: "1px 5px",
                      borderRadius: "2px",
                      background: strat.bg,
                      color: strat.color,
                      lineHeight: "11px",
                      letterSpacing: "0.05em",
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
                        background: "rgba(0,255,136,0.13)",
                        color: "#00FF88",
                        lineHeight: "10px",
                        letterSpacing: "0.05em",
                        flexShrink: 0,
                        animation: "terminal-new-badge 10s forwards",
                      }}
                    >
                      NEW
                    </span>
                  )}

                  {/* Ticker label — bright white, bold */}
                  <span
                    style={{
                      fontSize: "9px",
                      fontWeight: 700,
                      color: "#e8e8e8",
                      flex: 1,
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                      minWidth: 0,
                    }}
                  >
                    {tickerLabel}
                  </span>

                  {/* Relative time */}
                  {sig.timestamp && (
                    <span
                      style={{
                        fontSize: "8px",
                        color: "#2e2e2e",
                        fontVariantNumeric: "tabular-nums",
                        flexShrink: 0,
                        minWidth: "18px",
                        textAlign: "right",
                      }}
                      suppressHydrationWarning
                    >
                      {relativeTime(sig.timestamp)}
                    </span>
                  )}
                </div>

                {/* Line 2 (indented): Description + depth badge */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    paddingLeft: "14px",
                  }}
                >
                  {/* Timestamp (subtle) */}
                  {sig.timestamp && (
                    <span
                      style={{
                        fontSize: "7px",
                        color: "#252525",
                        fontVariantNumeric: "tabular-nums",
                        flexShrink: 0,
                      }}
                      suppressHydrationWarning
                    >
                      {formatTimestamp(sig.timestamp)}
                    </span>
                  )}

                  {/* Description text with highlighted numbers */}
                  <span
                    style={{
                      fontSize: "8px",
                      color: "#444",
                      flex: 1,
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                      textOverflow: "ellipsis",
                      minWidth: 0,
                    }}
                  >
                    {formatDescription(sig.description)}
                  </span>

                  {/* Depth badge */}
                  {sig.depth > 0 && (
                    <span
                      style={{
                        fontSize: "7px",
                        color: "#3a3a3a",
                        fontVariantNumeric: "tabular-nums",
                        flexShrink: 0,
                        background: "rgba(255,255,255,0.025)",
                        padding: "1px 4px",
                        borderRadius: "2px",
                        border: "1px solid #1a1a1a",
                      }}
                    >
                      {sig.depth}
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
