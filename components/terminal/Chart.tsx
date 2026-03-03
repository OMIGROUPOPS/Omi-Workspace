"use client";

// OMI Terminal — Recharts Chart (Redesigned)
// Multi-panel: Candlesticks + Bollinger Bands + Greeks Row
//              Kyle's Lambda | VPIN Bars | Volume

import { useMemo, useState } from "react";
import {
  ComposedChart,
  LineChart,
  BarChart,
  Bar,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import { parseTickerLabel, parseEventName } from "@/lib/terminal/ticker-labels";
import { calcGreeks } from "@/lib/terminal/greeks";

interface ChartProps {
  ticker?: string;
}

interface OHLCV {
  o: number;
  h: number;
  l: number;
  c: number;
  v: number;
  lambda: number;
  vpin: number;
  convTime: number;
}

// ── Deterministic PRNG ────────────────────────────────────────

class Rng {
  private s: number;
  constructor(seed: number) {
    this.s = seed;
  }
  next(): number {
    this.s = (this.s * 1103515245 + 12345) & 0x7fffffff;
    return (this.s >>> 0) / 0x7fffffff;
  }
  normal(): number {
    const u1 = Math.max(1e-10, this.next());
    const u2 = this.next();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }
}

// ── Data generation ───────────────────────────────────────────

function generateOHLCV(ticker: string): OHLCV[] {
  let seed = 0;
  for (let i = 0; i < ticker.length; i++) seed += ticker.charCodeAt(i);
  const rng = new Rng(seed * 31337);

  const bars: OHLCV[] = [];
  let price = (seed % 50) + 25;
  let lambda = 0.007;
  let vpin = 0.12;

  for (let i = 0; i < 120; i++) {
    const o = price;
    const dist50 = price - 50;
    const drift = -dist50 * 0.003;
    const p01 = Math.max(0.02, Math.min(0.98, price / 100));
    const boundaryVol = 1 / (4 * p01 * (1 - p01));
    const vol = (0.3 + rng.next() * 0.8) * Math.sqrt(boundaryVol) * 0.5;
    const change = drift + rng.normal() * vol;
    const c = Math.max(1, Math.min(99, o + change));
    const wickUp = rng.next() * vol * 0.8;
    const wickDn = rng.next() * vol * 0.8;
    const h = Math.min(99, Math.max(o, c) + wickUp);
    const l = Math.max(1, Math.min(o, c) - wickDn);
    const spike = rng.next() < 0.1 ? 3 + rng.next() * 5 : 1;
    const v = Math.floor((40 + rng.next() * 200) * spike);
    const impact = (Math.abs(c - o) / Math.max(v, 1)) * 80;
    lambda = lambda * 0.92 + impact * 0.08;
    const buyPct = 0.3 + rng.next() * 0.4;
    const imbalance = Math.abs(buyPct - (1 - buyPct));
    vpin = vpin * 0.88 + imbalance * 0.12;
    const distBoundary = Math.min(price, 100 - price);
    const convTime = 20 + distBoundary * 2.5 + rng.next() * 40;

    bars.push({
      o: Math.round(o * 100) / 100,
      h: Math.round(h * 100) / 100,
      l: Math.round(l * 100) / 100,
      c: Math.round(c * 100) / 100,
      v,
      lambda: Math.round(lambda * 100000) / 100000,
      vpin: Math.round(vpin * 1000) / 1000,
      convTime: Math.round(convTime),
    });
    price = c;
  }
  return bars;
}

function computeBollinger(bars: OHLCV[], period = 20, k = 2) {
  const result: { mid: number; upper: number; lower: number }[] = [];
  for (let i = 0; i < bars.length; i++) {
    if (i < period - 1) {
      result.push({ mid: bars[i].c, upper: bars[i].c, lower: bars[i].c });
    } else {
      const slice = bars.slice(i - period + 1, i + 1).map((b) => b.c);
      const mean = slice.reduce((a, b) => a + b, 0) / period;
      const std = Math.sqrt(slice.reduce((a, b) => a + (b - mean) ** 2, 0) / period);
      result.push({ mid: mean, upper: mean + std * k, lower: mean - std * k });
    }
  }
  return result;
}

// ── Custom Candlestick Shape ──────────────────────────────────

const CandleShape = (props: any) => {
  const { x, y, width, height, payload } = props;
  if (!payload) return null;
  const { o, h, l, c } = payload;
  const bull = c >= o;
  const color = bull ? "#00FF88" : "#FF3366";
  const candleW = Math.max(1, width * 0.6);
  const wickX = x + width / 2;
  const bodyMax = Math.max(o, c);
  const bodyMin = Math.min(o, c);
  const bodyRange = bodyMax - bodyMin + 0.01;
  const pxPerCent = height / bodyRange;
  const wickHighPx = y - (h - bodyMax) * pxPerCent;
  const wickLowPx = y + height + (bodyMin - l) * pxPerCent;

  return (
    <g>
      <line x1={wickX} y1={wickHighPx} x2={wickX} y2={wickLowPx} stroke={color} strokeWidth={1} />
      <rect x={x + (width - candleW) / 2} y={y} width={candleW} height={Math.max(1, height)} fill={color} />
    </g>
  );
};

// ── Custom Tooltip ────────────────────────────────────────────

const PriceTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div style={{
      background: "#111",
      border: "1px solid #333",
      padding: "6px 10px",
      fontSize: "9px",
      color: "#999",
      borderRadius: "3px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
    }}>
      <div style={{ marginBottom: "2px" }}>
        <span style={{ color: "#888" }}>O:</span><span style={{ color: "#ddd" }}>{d.o.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "4px" }}>H:</span><span style={{ color: "#ddd" }}>{d.h.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "4px" }}>L:</span><span style={{ color: "#ddd" }}>{d.l.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "4px" }}>C:</span><span style={{ color: "#ddd", fontWeight: 600 }}>{d.c.toFixed(1)}</span>
      </div>
      <div style={{ color: "#00BCD4" }}>{"\u03BB"}: {d.lambda.toFixed(5)}</div>
      <div style={{ color: d.vpin < 0.15 ? "#00FF88" : d.vpin < 0.3 ? "#FF6600" : "#FF3366" }}>VPIN: {d.vpin.toFixed(3)}</div>
    </div>
  );
};

// ── Greeks Display Row ────────────────────────────────────────

function GreeksRow({ price, sigma }: { price: number; sigma: number }) {
  // Assume ~4 hours to expiry for display purposes (typical prediction market)
  const greeks = calcGreeks(price / 100, 4, sigma || 0.5);

  const items = [
    { label: "\u0394", value: greeks.delta.toFixed(2), color: "#00BCD4" },
    { label: "\u0398", value: `${greeks.theta >= 0 ? "+" : ""}${greeks.theta.toFixed(1)}\u00A2/hr`, color: "#00BCD4" },
    { label: "\u0393", value: greeks.gamma.toFixed(3), color: "#00BCD4" },
    { label: "\u03BD", value: greeks.vega.toFixed(2), color: "#00BCD4" },
    { label: "IV", value: `${(greeks.iv * 100).toFixed(0)}%`, color: "#00BCD4" },
  ];

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "12px",
      height: "22px",
      padding: "0 4px",
      borderBottom: "1px solid #1a1a1a",
      background: "rgba(0,188,212,0.02)",
    }}>
      {items.map((item, i) => (
        <span key={i} style={{ display: "flex", alignItems: "center", gap: "3px", fontSize: "9px" }}>
          <span style={{ color: item.color, fontWeight: 700, fontSize: "10px" }}>{item.label}</span>
          <span style={{ color: "#ccc", fontVariantNumeric: "tabular-nums" }}>{item.value}</span>
          {i < items.length - 1 && (
            <span style={{ color: "#222", marginLeft: "6px" }}>|</span>
          )}
        </span>
      ))}
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────

export default function Chart({ ticker }: ChartProps) {
  const [showBoll, setShowBoll] = useState(true);

  const data = useMemo(() => (ticker ? generateOHLCV(ticker) : null), [ticker]);
  const boll = useMemo(() => (data ? computeBollinger(data) : null), [data]);

  const { chartData, priceMin, priceMax } = useMemo(() => {
    if (!data || !boll) return { chartData: [] as any[], priceMin: 0, priceMax: 100 };
    let pMin = Infinity, pMax = -Infinity;
    for (const d of data) { pMin = Math.min(pMin, d.l); pMax = Math.max(pMax, d.h); }
    for (const b of boll) { pMin = Math.min(pMin, b.lower); pMax = Math.max(pMax, b.upper); }
    const pad = (pMax - pMin) * 0.06 || 1;
    pMin -= pad;
    pMax += pad;
    return {
      chartData: data.map((d, i) => ({
        ...d, index: i, sma: boll[i].mid, bollUpper: boll[i].upper, bollLower: boll[i].lower,
        bollBase: boll[i].lower, bollWidth: boll[i].upper - boll[i].lower,
        candleRange: [Math.min(d.o, d.c) - 0.005, Math.max(d.o, d.c) + 0.005] as [number, number],
      })),
      priceMin: pMin,
      priceMax: pMax,
    };
  }, [data, boll]);

  if (!ticker) {
    return (
      <div style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "#333",
        fontSize: "10px",
        gap: "8px",
      }}>
        <div style={{ fontSize: "18px", color: "#222" }}>{"\u25C8"}</div>
        <div>Select a ticker from watchlist</div>
      </div>
    );
  }

  const latest = data ? data[data.length - 1] : null;
  const first = data ? data[0] : null;
  const change = latest && first ? latest.c - first.o : 0;
  const changeCol = change >= 0 ? "#00FF88" : "#FF3366";
  const changeArrow = change >= 0 ? "\u25B2" : "\u25BC";

  // Parse ticker into human-readable labels
  const eventTicker = ticker.replace(/-[YN]$/, "");
  const rawTeam = ticker.split("-").slice(-2, -1)[0] || ticker.slice(-8);
  const tickerLabel = parseTickerLabel(ticker, rawTeam, eventTicker);
  const eventName = parseEventName(eventTicker);

  const timeTicks: number[] = [];
  for (let i = 0; i < chartData.length; i += 30) timeTicks.push(i);
  if (timeTicks[timeTicks.length - 1] !== chartData.length - 1) timeTicks.push(chartData.length - 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", minHeight: 0, overflow: "hidden" }}>
      {/* ── Ticker header — Bloomberg-style prominent ── */}
      <div className="flex items-center justify-between shrink-0" style={{
        height: "32px",
        padding: "0 4px",
        borderBottom: "1px solid #1a1a1a",
      }}>
        <div className="flex items-center gap-3">
          <span style={{ color: "#eee", fontWeight: 700, fontSize: "13px", letterSpacing: "0.02em" }}>
            {tickerLabel}
          </span>
          <span style={{ color: "#444", fontSize: "9px" }}>{eventName}</span>
          {latest && (
            <span style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              padding: "2px 8px",
              borderRadius: "3px",
              border: `1px solid ${change >= 0 ? "rgba(0,255,136,0.25)" : "rgba(255,51,102,0.25)"}`,
              background: change >= 0 ? "rgba(0,255,136,0.08)" : "rgba(255,51,102,0.08)",
            }}>
              <span style={{
                color: changeCol,
                fontWeight: 700,
                fontSize: "18px",
                fontVariantNumeric: "tabular-nums",
                textShadow: `0 0 12px ${change >= 0 ? "rgba(0,255,136,0.3)" : "rgba(255,51,102,0.3)"}`,
              }}>
                {latest.c.toFixed(0)}&cent;
              </span>
              <span style={{ color: changeCol, fontSize: "10px", fontWeight: 600 }}>
                {changeArrow}{change >= 0 ? "+" : ""}{change.toFixed(1)}
              </span>
            </span>
          )}
          {latest && (
            <span style={{ color: "#444", fontSize: "8px", fontVariantNumeric: "tabular-nums" }}>
              H:{latest.h.toFixed(0)} L:{latest.l.toFixed(0)} V:{latest.v}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowBoll((v) => !v)}
            style={{
              fontSize: "7px", padding: "2px 6px", borderRadius: "2px",
              border: `1px solid ${showBoll ? "#FF6600" : "#222"}`,
              background: showBoll ? "rgba(255,102,0,0.12)" : "transparent",
              color: showBoll ? "#FF6600" : "#444", cursor: "pointer",
              fontWeight: 600, letterSpacing: "0.05em",
            }}
          >
            BOLL
          </button>
          {["1m", "5m", "15m"].map((tf, i) => (
            <button
              key={tf}
              style={{
                fontSize: "7px", padding: "2px 6px", borderRadius: "2px",
                border: `1px solid ${i === 0 ? "#FF6600" : "#222"}`,
                background: i === 0 ? "rgba(255,102,0,0.12)" : "transparent",
                color: i === 0 ? "#FF6600" : "#444", cursor: "pointer",
                fontWeight: 600, letterSpacing: "0.05em",
              }}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* ── Greeks Row ── */}
      {latest && (
        <GreeksRow price={latest.c} sigma={latest.vpin} />
      )}

      {/* ── Main Price Chart ── */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 6, left: 0, bottom: 4 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis dataKey="index" tick={false} axisLine={{ stroke: "#1a1a1a" }} />
            <YAxis
              domain={[priceMin, priceMax]}
              tick={{ fontSize: 8, fill: "#444" }}
              tickFormatter={(v: number) => `${v.toFixed(0)}`}
              axisLine={{ stroke: "#1a1a1a" }}
              width={32}
            />
            <Tooltip content={<PriceTooltip />} cursor={{ stroke: "#333", strokeDasharray: "3 3" }} />

            {showBoll && (
              <>
                <Area dataKey="bollBase" stackId="boll" fill="transparent" stroke="transparent" type="monotone" isAnimationActive={false} tooltipType="none" />
                <Area dataKey="bollWidth" stackId="boll" fill="rgba(255,102,0,0.06)" stroke="transparent" type="monotone" isAnimationActive={false} tooltipType="none" />
                <Line dataKey="bollUpper" stroke="rgba(255,102,0,0.35)" dot={false} strokeWidth={1} type="monotone" isAnimationActive={false} tooltipType="none" />
                <Line dataKey="bollLower" stroke="rgba(255,102,0,0.35)" dot={false} strokeWidth={1} type="monotone" isAnimationActive={false} tooltipType="none" />
                <Line dataKey="sma" stroke="rgba(255,102,0,0.18)" dot={false} strokeDasharray="3 3" strokeWidth={1} type="monotone" isAnimationActive={false} tooltipType="none" />
              </>
            )}

            <Bar dataKey="candleRange" shape={<CandleShape />} isAnimationActive={false} />
            {latest && <ReferenceLine y={latest.c} stroke="#FF6600" strokeDasharray="5 4" strokeWidth={1} />}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* ── Kyle's Lambda Panel ── */}
      <div style={{ height: 52, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{
          position: "absolute", top: 3, left: 36, fontSize: 7, color: "#555", fontWeight: 700, zIndex: 1,
          letterSpacing: "0.08em", textTransform: "uppercase",
        }}>
          KYLE {"\u03BB"}
        </div>
        {latest && (
          <div style={{
            position: "absolute", top: 2, right: 8, fontSize: 13, color: "#00BCD4", fontWeight: 700, zIndex: 1,
            fontVariantNumeric: "tabular-nums",
            textShadow: "0 0 8px rgba(0,188,212,0.3)",
          }}>
            {latest.lambda.toFixed(4)}
          </div>
        )}
        <ResponsiveContainer width="100%" height={52}>
          <LineChart data={chartData} margin={{ top: 8, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis dataKey="index" tick={false} axisLine={{ stroke: "#1a1a1a" }} />
            <YAxis tick={{ fontSize: 7, fill: "#333" }} domain={["auto", "auto"]} axisLine={{ stroke: "#1a1a1a" }} width={32} tickFormatter={(v: number) => v.toFixed(3)} />
            <ReferenceLine y={0.012} stroke="#FF3366" strokeDasharray="4 3" strokeWidth={1.5} label={{ value: "0.012", position: "right", fill: "#FF3366", fontSize: 7 }} />
            <Line dataKey="lambda" stroke="#00BCD4" dot={false} strokeWidth={1.5} type="monotone" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── VPIN Panel ── */}
      <div style={{ height: 52, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{
          position: "absolute", top: 3, left: 36, fontSize: 7, color: "#555", fontWeight: 700, zIndex: 1,
          letterSpacing: "0.08em", textTransform: "uppercase",
        }}>
          VPIN
        </div>
        {latest && (
          <div style={{
            position: "absolute", top: 2, right: 8, fontSize: 13, fontWeight: 700, zIndex: 1,
            fontVariantNumeric: "tabular-nums",
            color: latest.vpin < 0.15 ? "#00FF88" : latest.vpin < 0.3 ? "#FF6600" : "#FF3366",
            textShadow: `0 0 8px ${latest.vpin < 0.15 ? "rgba(0,255,136,0.3)" : latest.vpin < 0.3 ? "rgba(255,102,0,0.3)" : "rgba(255,51,102,0.3)"}`,
          }}>
            {latest.vpin.toFixed(3)}
          </div>
        )}
        <ResponsiveContainer width="100%" height={52}>
          <BarChart data={chartData} margin={{ top: 8, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis dataKey="index" tick={false} axisLine={{ stroke: "#1a1a1a" }} />
            <YAxis tick={{ fontSize: 7, fill: "#333" }} domain={[0, "auto"]} axisLine={{ stroke: "#1a1a1a" }} width={32} />
            <ReferenceLine y={0.15} stroke="#333" strokeDasharray="2 2" />
            <ReferenceLine y={0.3} stroke="#333" strokeDasharray="2 2" />
            <Bar dataKey="vpin" isAnimationActive={false}>
              {chartData.map((d, i) => (
                <Cell key={i} fill={d.vpin < 0.15 ? "rgba(0,255,136,0.5)" : d.vpin < 0.3 ? "rgba(255,102,0,0.5)" : "rgba(255,51,102,0.5)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Volume Panel — compact ── */}
      <div style={{ height: 36, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{ position: "absolute", top: 2, left: 36, fontSize: 7, color: "#444", fontWeight: 700, zIndex: 1, letterSpacing: "0.05em" }}>
          VOL
        </div>
        <ResponsiveContainer width="100%" height={36}>
          <BarChart data={chartData} margin={{ top: 6, right: 6, left: 0, bottom: 2 }}>
            <XAxis
              dataKey="index" ticks={timeTicks}
              tick={{ fontSize: 7, fill: "#333" }}
              tickFormatter={(i: number) => i === chartData.length - 1 ? "now" : `-${chartData.length - i}m`}
              axisLine={{ stroke: "#1a1a1a" }}
            />
            <YAxis tick={false} axisLine={false} width={32} />
            <Bar dataKey="v" isAnimationActive={false}>
              {chartData.map((d, i) => (
                <Cell key={i} fill={d.c >= d.o ? "rgba(0,255,136,0.3)" : "rgba(255,51,102,0.3)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
