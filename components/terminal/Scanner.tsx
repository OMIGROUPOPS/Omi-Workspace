"use client";

// OMI Terminal — Scanner (Redesigned)
// Signals with severity hierarchy, animated NEW badge, slide-in animation.

import { useState } from "react";
import type { ScannerSignal } from "@/lib/terminal/types";
import { calcGreeks } from "@/lib/terminal/greeks";

interface ScannerProps {
  signals?: ScannerSignal[];
  onSelect?: (ticker: string) => void;
}

// ── Severity tier config ──────────────────────────────────────────────────

const SEVERITY_CONFIG = {
  CRITICAL: { color: "#FF3366", bg: "rgba(255,51,102,0.08)", border: "rgba(255,51,102,0.2)", glow: "rgba(255,51,102,0.3)", rank: 4 },
  HIGH:     { color: "#FF6600", bg: "rgba(255,102,0,0.08)",  border: "rgba(255,102,0,0.2)",  glow: "rgba(255,102,0,0.3)",  rank: 3 },
  MEDIUM:   { color: "#FF6600", bg: "transparent",            border: "transparent",          glow: undefined,             rank: 2 },
  LOW:      { color: "#444",    bg: "transparent",            border: "transparent",          glow: undefined,             rank: 1 },
} as const;

type Severity = keyof typeof SEVERITY_CONFIG;

function getSeverity(signal: ScannerSignal): Severity {
  // Lambda-based classification
  if (signal.lambda !== undefined) {
    if (signal.lambda > 0.02)  return "CRITICAL";
    if (signal.lambda > 0.012) return "HIGH";
    if (signal.lambda > 0.006) return "MEDIUM";
  }
  // Fallback: use signal type
  if (signal.type === "SPIKE" || signal.type === "HALT") return "HIGH";
  if (signal.type === "TREND" || signal.type === "SQUEEZE") return "MEDIUM";
  return "LOW";
}

// ── Signal row ────────────────────────────────────────────────────────────

function SignalRow({
  signal,
  onSelect,
  isNew,
}: {
  signal: ScannerSignal;
  onSelect?: (ticker: string) => void;
  isNew: boolean;
}) {
  const severity = getSeverity(signal);
  const cfg = SEVERITY_CONFIG[severity];
  const greeks = calcGreeks(signal.price / 100, 4, signal.lambda ?? 0.5);

  const typeColors: Record<string, string> = {
    SPIKE: "#FF6600", TREND: "#00BCD4", SQUEEZE: "#FF3366",
    HALT: "#FF3366", RESUME: "#00FF88", NEWS: "#FFD700",
  };
  const typeColor = typeColors[signal.type] ?? "#555";

  return (
    <div
      onClick={() => onSelect?.(signal.ticker)}
      style={{
        padding: "5px 4px",
        borderBottom: "1px solid #0f0f0f",
        background: cfg.bg,
        border: cfg.border !== "transparent" ? `1px solid ${cfg.border}` : undefined,
        borderRadius: cfg.border !== "transparent" ? "2px" : undefined,
        marginBottom: cfg.border !== "transparent" ? "1px" : undefined,
        cursor: "pointer",
        animation: isNew ? "terminal-signal-in 0.6s ease-out" : undefined,
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: "4px",
      }}
    >
      {/* Left */}
      <div style={{ minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "5px", marginBottom: "2px" }}>
          {/* Severity dot */}
          <div style={{
            width: "5px", height: "5px",
            borderRadius: "50%",
            background: cfg.color,
            flexShrink: 0,
            boxShadow: cfg.glow ? `0 0 4px ${cfg.glow}` : undefined,
          }} />
          <span style={{
            color: "#ccc",
            fontSize: "10px",
            fontWeight: 700,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            textShadow: cfg.glow ? `0 0 8px ${cfg.glow}` : undefined,
          }}>
            {signal.ticker}
          </span>
          {/* Type badge */}
          <span style={{
            fontSize: "7px",
            padding: "1px 4px",
            borderRadius: "2px",
            background: `${typeColor}18`,
            color: typeColor,
            fontWeight: 700,
            letterSpacing: "0.06em",
            flexShrink: 0,
          }}>
            {signal.type}
          </span>
          {/* NEW badge */}
          {isNew && (
            <span style={{
              fontSize: "6px",
              padding: "1px 3px",
              borderRadius: "2px",
              background: "rgba(0,255,136,0.15)",
              color: "#00FF88",
              fontWeight: 700,
              letterSpacing: "0.08em",
              animation: "terminal-new-badge 3s ease-out forwards",
            }}>
              NEW
            </span>
          )}
        </div>
        {/* Greeks strip */}
        <div style={{ display: "flex", gap: "8px", fontSize: "8px" }}>
          <span style={{ color: "#333" }}>Δ<span style={{ color: "#555" }}>{greeks.delta.toFixed(2)}</span></span>
          <span style={{ color: "#333" }}>Θ<span style={{ color: "#555" }}>{greeks.theta.toFixed(1)}</span></span>
          <span style={{ color: "#333" }}>λ<span style={{
            color: signal.lambda !== undefined
              ? (signal.lambda > 0.012 ? cfg.color : "#555")
              : "#555"
          }}>{signal.lambda !== undefined ? signal.lambda.toFixed(4) : "—"}</span></span>
        </div>
      </div>

      {/* Right */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "3px" }}>
        <span style={{
          fontSize: "11px",
          fontWeight: 700,
          color: signal.price >= 50 ? "#00FF88" : "#FF3366",
          fontVariantNumeric: "tabular-nums",
          textShadow: signal.price >= 50 ? "0 0 6px rgba(0,255,136,0.25)" : "0 0 6px rgba(255,51,102,0.25)",
        }}>
          {signal.price.toFixed(0)}¢
        </span>
        <span style={{ fontSize: "8px", color: cfg.color, fontWeight: 700, letterSpacing: "0.04em" }}>
          {severity}
        </span>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────

export default function Scanner({ signals = [], onSelect }: ScannerProps) {
  const [filter, setFilter] = useState<Severity | "ALL">("ALL");

  // Sort by severity rank desc, then by price distance from 50
  const sorted = [...signals]
    .map((s) => ({ ...s, _sev: getSeverity(s) }))
    .sort((a, b) => {
      const rankDiff = SEVERITY_CONFIG[b._sev].rank - SEVERITY_CONFIG[a._sev].rank;
      if (rankDiff !== 0) return rankDiff;
      return Math.abs(b.price - 50) - Math.abs(a.price - 50);
    });

  const filtered = filter === "ALL" ? sorted : sorted.filter((s) => s._sev === filter);

  // Track "new" signals (first 2 of each severity)
  const newSet = new Set(sorted.slice(0, 3).map((s) => s.ticker));

  const counts = {
    CRITICAL: sorted.filter((s) => s._sev === "CRITICAL").length,
    HIGH:     sorted.filter((s) => s._sev === "HIGH").length,
    MEDIUM:   sorted.filter((s) => s._sev === "MEDIUM").length,
    LOW:      sorted.filter((s) => s._sev === "LOW").length,
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Filter bar */}
      <div style={{
        display: "flex",
        gap: "2px",
        padding: "3px 2px",
        borderBottom: "1px solid #1a1a1a",
        flexShrink: 0,
      }}>
        {(["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((tier) => {
          const isActive = filter === tier;
          const cfg = tier !== "ALL" ? SEVERITY_CONFIG[tier] : null;
          const count = tier === "ALL" ? sorted.length : counts[tier];
          return (
            <button
              key={tier}
              onClick={() => setFilter(tier)}
              style={{
                fontSize: "7px",
                padding: "2px 5px",
                borderRadius: "2px",
                border: `1px solid ${isActive ? (cfg?.color ?? "#FF6600") : "#1a1a1a"}`,
                background: isActive ? `${cfg?.color ?? "#FF6600"}18` : "transparent",
                color: isActive ? (cfg?.color ?? "#FF6600") : "#333",
                cursor: "pointer",
                fontWeight: 700,
                letterSpacing: "0.05em",
              }}
            >
              {tier} {count > 0 && <span style={{ opacity: 0.7 }}>{count}</span>}
            </button>
          );
        })}
      </div>

      {/* Signal list */}
      <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
        {filtered.length === 0 ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#222", fontSize: "9px" }}>
            No signals
          </div>
        ) : (
          filtered.map((signal) => (
            <SignalRow
              key={signal.ticker}
              signal={signal}
              onSelect={onSelect}
              isNew={newSet.has(signal.ticker)}
            />
          ))
        )}
      </div>
    </div>
  );
}
