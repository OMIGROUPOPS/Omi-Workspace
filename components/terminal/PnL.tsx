"use client";

// OMI Terminal — P&L Panel (Redesigned)
// Shows position P&L with Greeks and animated counters.

import { useRef, useEffect, useState } from "react";
import type { Position, PnLData } from "@/lib/terminal/types";
import { calcGreeks } from "@/lib/terminal/greeks";

interface PnLProps {
  data?: PnLData;
}

// ── Animated counter ──────────────────────────────────────────────────────

function AnimatedValue({
  value,
  formatter,
  color,
  fontSize = "11px",
  glow = false,
}: {
  value: number;
  formatter: (v: number) => string;
  color: string;
  fontSize?: string;
  glow?: boolean;
}) {
  const [display, setDisplay] = useState(value);
  const [ticking, setTicking] = useState(false);
  const prev = useRef(value);

  useEffect(() => {
    if (prev.current !== value) {
      setTicking(true);
      const start = prev.current;
      const end = value;
      const duration = 400;
      const startTime = performance.now();

      const frame = (now: number) => {
        const t = Math.min(1, (now - startTime) / duration);
        const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        setDisplay(start + (end - start) * eased);
        if (t < 1) requestAnimationFrame(frame);
        else {
          setDisplay(end);
          setTicking(false);
          prev.current = end;
        }
      };
      requestAnimationFrame(frame);
    }
  }, [value]);

  return (
    <span
      style={{
        color,
        fontSize,
        fontWeight: 700,
        fontVariantNumeric: "tabular-nums",
        animation: ticking ? "terminal-counter-tick 0.3s ease-out" : undefined,
        textShadow: glow ? `0 0 8px ${color}66` : undefined,
        display: "inline-block",
      }}
    >
      {formatter(display)}
    </span>
  );
}

// ── Position row ──────────────────────────────────────────────────────────

function PositionRow({ pos }: { pos: Position }) {
  const hoursToExpiry = (pos.secs_to_expiry ?? 14400) / 3600;
  const greeks = calcGreeks(pos.price / 100, hoursToExpiry, 0.5);

  const pnlColor = pos.unrealized_pnl >= 0 ? "#00FF88" : "#FF3366";
  const pnlPct = pos.avg_cost > 0 ? ((pos.price - pos.avg_cost) / pos.avg_cost) * 100 : 0;

  // Severity tiers for position sizing
  const posSize = Math.abs(pos.contracts * pos.price);
  const severity =
    posSize > 500 ? "high" :
    posSize > 200 ? "med" : "low";
  const severityColor =
    severity === "high" ? "#FF3366" :
    severity === "med" ? "#FF6600" : "#444";

  return (
    <div
      style={{
        padding: "5px 4px",
        borderBottom: "1px solid #0f0f0f",
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: "4px",
      }}
    >
      {/* Left: ticker + Greeks */}
      <div style={{ minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "5px", marginBottom: "2px" }}>
          <span style={{
            fontSize: "10px",
            fontWeight: 700,
            color: "#ddd",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}>
            {pos.ticker}
          </span>
          <span style={{ fontSize: "7px", color: severityColor, fontWeight: 700, letterSpacing: "0.05em" }}>
            {severity.toUpperCase()}
          </span>
          <span style={{ fontSize: "9px", color: "#444", fontVariantNumeric: "tabular-nums" }}>
            {pos.contracts > 0 ? "+" : ""}{pos.contracts} @ {pos.avg_cost.toFixed(0)}¢
          </span>
        </div>
        {/* Greeks strip */}
        <div style={{ display: "flex", gap: "8px", fontSize: "8px" }}>
          <span style={{ color: "#333" }}>Δ<span style={{ color: "#00BCD4" }}>{greeks.delta.toFixed(2)}</span></span>
          <span style={{ color: "#333" }}>Θ<span style={{ color: "#00BCD4" }}>{greeks.theta.toFixed(1)}</span></span>
          <span style={{ color: "#333" }}>IV<span style={{ color: "#00BCD4" }}>{(greeks.iv * 100).toFixed(0)}%</span></span>
          <span style={{ color: "#333" }}>ν<span style={{ color: "#00BCD4" }}>{greeks.vega.toFixed(2)}</span></span>
        </div>
      </div>

      {/* Right: P&L */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "2px" }}>
        <AnimatedValue
          value={pos.unrealized_pnl}
          formatter={(v) => `${v >= 0 ? "+" : ""}$${Math.abs(v).toFixed(2)}`}
          color={pnlColor}
          fontSize="11px"
          glow
        />
        <span style={{
          fontSize: "8px",
          color: pnlPct >= 0 ? "rgba(0,255,136,0.5)" : "rgba(255,51,102,0.5)",
          fontVariantNumeric: "tabular-nums",
        }}>
          {pnlPct >= 0 ? "+" : ""}{pnlPct.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

// ── Summary bar ───────────────────────────────────────────────────────────

function SummaryBar({ data }: { data: PnLData }) {
  const totalPnl = data.positions.reduce((s, p) => s + p.unrealized_pnl, 0);
  const totalColor = totalPnl >= 0 ? "#00FF88" : "#FF3366";
  const winCount = data.positions.filter((p) => p.unrealized_pnl > 0).length;
  const lossCount = data.positions.filter((p) => p.unrealized_pnl < 0).length;

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "3px 4px",
      borderBottom: "1px solid #1a1a1a",
      background: "#080808",
    }}>
      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
        <span style={{ fontSize: "7px", color: "#444", textTransform: "uppercase", letterSpacing: "0.08em" }}>Total P&L</span>
        <AnimatedValue
          value={totalPnl}
          formatter={(v) => `${v >= 0 ? "+" : ""}$${Math.abs(v).toFixed(2)}`}
          color={totalColor}
          fontSize="12px"
          glow
        />
      </div>
      <div style={{ display: "flex", gap: "6px", fontSize: "8px" }}>
        <span style={{ color: "#00FF88" }}>{winCount}W</span>
        <span style={{ color: "#333" }}>/</span>
        <span style={{ color: "#FF3366" }}>{lossCount}L</span>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────

export default function PnL({ data }: PnLProps) {
  if (!data || data.positions.length === 0) {
    return (
      <div style={{
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#222",
        fontSize: "9px",
      }}>
        No positions
      </div>
    );
  }

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <SummaryBar data={data} />
      <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
        {data.positions.map((pos) => (
          <PositionRow key={pos.ticker} pos={pos} />
        ))}
      </div>
    </div>
  );
}
