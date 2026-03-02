"use client";

// OMNI Terminal — Recharts Chart
// Multi-panel: OHLC Candlesticks + Bollinger Bands
//              Kyle's Lambda EWMA | VPIN Proxy Bars | Volume Bars

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
  // Normal via Box-Muller
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
  let price = (seed % 50) + 25; // Start 25-75
  let lambda = 0.007;
  let vpin = 0.12;

  for (let i = 0; i < 120; i++) {
    const o = price;

    // Prediction market walk: mean-revert toward 50, bounded 1-99
    const dist50 = price - 50;
    const drift = -dist50 * 0.003;
    // Volatility increases near boundaries (logit effect)
    const p01 = Math.max(0.02, Math.min(0.98, price / 100));
    const boundaryVol = 1 / (4 * p01 * (1 - p01));
    const vol = (0.3 + rng.next() * 0.8) * Math.sqrt(boundaryVol) * 0.5;

    const change = drift + rng.normal() * vol;
    const c = Math.max(1, Math.min(99, o + change));

    // Wicks extend beyond body
    const wickUp = rng.next() * vol * 0.8;
    const wickDn = rng.next() * vol * 0.8;
    const h = Math.min(99, Math.max(o, c) + wickUp);
    const l = Math.max(1, Math.min(o, c) - wickDn);

    // Volume: base + spikes
    const spike = rng.next() < 0.1 ? 3 + rng.next() * 5 : 1;
    const v = Math.floor((40 + rng.next() * 200) * spike);

    // Kyle's lambda EWMA: price impact per unit volume
    const impact = (Math.abs(c - o) / Math.max(v, 1)) * 80;
    lambda = lambda * 0.92 + impact * 0.08;

    // VPIN proxy: order imbalance
    const buyPct = 0.3 + rng.next() * 0.4;
    const imbalance = Math.abs(buyPct - (1 - buyPct));
    vpin = vpin * 0.88 + imbalance * 0.12;

    // Convergence time: faster near boundaries
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

// ── Bollinger Bands (20-period, 2 std dev) ────────────────────

function computeBollinger(bars: OHLCV[], period = 20, k = 2) {
  const result: { mid: number; upper: number; lower: number }[] = [];
  for (let i = 0; i < bars.length; i++) {
    if (i < period - 1) {
      result.push({ mid: bars[i].c, upper: bars[i].c, lower: bars[i].c });
    } else {
      const slice = bars.slice(i - period + 1, i + 1).map((b) => b.c);
      const mean = slice.reduce((a, b) => a + b, 0) / period;
      const std = Math.sqrt(
        slice.reduce((a, b) => a + (b - mean) ** 2, 0) / period,
      );
      result.push({
        mid: mean,
        upper: mean + std * k,
        lower: mean - std * k,
      });
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
  const bodyRange = bodyMax - bodyMin + 0.01; // epsilon to avoid div-by-zero
  const pxPerCent = height / bodyRange;

  // Compute wick pixel positions from body positions
  const wickHighPx = y - (h - bodyMax) * pxPerCent;
  const wickLowPx = y + height + (bodyMin - l) * pxPerCent;

  return (
    <g>
      <line
        x1={wickX}
        y1={wickHighPx}
        x2={wickX}
        y2={wickLowPx}
        stroke={color}
        strokeWidth={1}
      />
      <rect
        x={x + (width - candleW) / 2}
        y={y}
        width={candleW}
        height={Math.max(1, height)}
        fill={color}
      />
    </g>
  );
};

// ── Custom Tooltip ────────────────────────────────────────────

const PriceTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div
      style={{
        background: "#111",
        border: "1px solid #333",
        padding: "6px 10px",
        fontSize: "10px",
        fontFamily: "'Courier New', monospace",
        color: "#ccc",
        borderRadius: "2px",
      }}
    >
      <div>
        O:{d.o.toFixed(1)}¢ H:{d.h.toFixed(1)}¢ L:{d.l.toFixed(1)}¢ C:
        {d.c.toFixed(1)}¢
      </div>
      <div style={{ color: "#00BFFF" }}>λ: {d.lambda.toFixed(5)}</div>
      <div
        style={{
          color:
            d.vpin < 0.15
              ? "#00FF88"
              : d.vpin < 0.3
                ? "#FFA500"
                : "#FF3366",
        }}
      >
        VPIN: {d.vpin.toFixed(3)}
      </div>
    </div>
  );
};

// ── Component ─────────────────────────────────────────────────

export default function Chart({ ticker }: ChartProps) {
  const [showBoll, setShowBoll] = useState(true);

  const data = useMemo(
    () => (ticker ? generateOHLCV(ticker) : null),
    [ticker],
  );
  const boll = useMemo(() => (data ? computeBollinger(data) : null), [data]);

  const { chartData, priceMin, priceMax } = useMemo(() => {
    if (!data || !boll)
      return { chartData: [] as any[], priceMin: 0, priceMax: 100 };

    let pMin = Infinity,
      pMax = -Infinity;
    for (const d of data) {
      pMin = Math.min(pMin, d.l);
      pMax = Math.max(pMax, d.h);
    }
    for (const b of boll) {
      pMin = Math.min(pMin, b.lower);
      pMax = Math.max(pMax, b.upper);
    }
    const pad = (pMax - pMin) * 0.06 || 1;
    pMin -= pad;
    pMax += pad;

    return {
      chartData: data.map((d, i) => ({
        ...d,
        index: i,
        sma: boll[i].mid,
        bollUpper: boll[i].upper,
        bollLower: boll[i].lower,
        bollBase: boll[i].lower,
        bollWidth: boll[i].upper - boll[i].lower,
        candleRange: [
          Math.min(d.o, d.c) - 0.005,
          Math.max(d.o, d.c) + 0.005,
        ] as [number, number],
      })),
      priceMin: pMin,
      priceMax: pMax,
    };
  }, [data, boll]);

  if (!ticker) {
    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#555",
          fontSize: "11px",
          fontFamily: "'Courier New', monospace",
        }}
      >
        Select a ticker from watchlist
      </div>
    );
  }

  const latest = data ? data[data.length - 1] : null;
  const first = data ? data[0] : null;
  const change = latest && first ? latest.c - first.o : 0;
  const changeCol = change >= 0 ? "#00FF88" : "#FF3366";

  // Time axis ticks for volume panel
  const timeTicks: number[] = [];
  for (let i = 0; i < chartData.length; i += 20) timeTicks.push(i);
  if (timeTicks[timeTicks.length - 1] !== chartData.length - 1)
    timeTicks.push(chartData.length - 1);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        minHeight: 0,
        overflow: "hidden",
        fontFamily: "'Courier New', monospace",
      }}
    >
      {/* Header bar */}
      <div
        className="flex items-center justify-between shrink-0"
        style={{ height: "22px", fontSize: "10px" }}
      >
        <div className="flex items-center gap-3">
          <span style={{ color: "#aaa", fontWeight: 600 }}>{ticker}</span>
          {latest && (
            <>
              <span
                style={{ color: changeCol, fontWeight: 700, fontSize: "12px" }}
              >
                {latest.c.toFixed(0)}¢
              </span>
              <span style={{ color: changeCol }}>
                {change >= 0 ? "+" : ""}
                {change.toFixed(1)}
              </span>
              <span style={{ color: "#555", fontSize: "9px" }}>
                H:{latest.h.toFixed(0)} L:{latest.l.toFixed(0)} V:{latest.v}
              </span>
            </>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowBoll((v) => !v)}
            style={{
              fontSize: "8px",
              padding: "1px 5px",
              borderRadius: "2px",
              border: `1px solid ${showBoll ? "#FFA500" : "#333"}`,
              background: showBoll ? "rgba(255,165,0,0.12)" : "transparent",
              color: showBoll ? "#FFA500" : "#555",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            BOLL
          </button>
          <span
            style={{
              width: "1px",
              height: "12px",
              background: "#333",
              margin: "0 2px",
            }}
          />
          {["1m", "5m", "15m"].map((tf, i) => (
            <button
              key={tf}
              style={{
                fontSize: "8px",
                padding: "1px 5px",
                borderRadius: "2px",
                border: `1px solid ${i === 0 ? "#FF6600" : "#333"}`,
                background:
                  i === 0 ? "rgba(255,102,0,0.12)" : "transparent",
                color: i === 0 ? "#FF6600" : "#555",
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* ── Main Price Chart ────────────────────────────────── */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 5, right: 6, left: 0, bottom: 5 }}
          >
            <CartesianGrid stroke="#1a1a1a" />
            <XAxis
              dataKey="index"
              tick={false}
              axisLine={{ stroke: "#333" }}
            />
            <YAxis
              domain={[priceMin, priceMax]}
              tick={{
                fontSize: 9,
                fill: "#888",
                fontFamily: "'Courier New', monospace",
              }}
              tickFormatter={(v: number) => `${v.toFixed(0)}¢`}
              axisLine={{ stroke: "#333" }}
              width={44}
            />
            <Tooltip
              content={<PriceTooltip />}
              cursor={{ stroke: "#444", strokeDasharray: "3 3" }}
            />

            {/* Bollinger band fill (stacked area trick) */}
            {showBoll && (
              <>
                <Area
                  dataKey="bollBase"
                  stackId="boll"
                  fill="transparent"
                  stroke="transparent"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Area
                  dataKey="bollWidth"
                  stackId="boll"
                  fill="rgba(255,165,0,0.15)"
                  stroke="transparent"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  dataKey="bollUpper"
                  stroke="rgba(255,165,0,0.45)"
                  dot={false}
                  strokeWidth={1}
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  dataKey="bollLower"
                  stroke="rgba(255,165,0,0.45)"
                  dot={false}
                  strokeWidth={1}
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  dataKey="sma"
                  stroke="rgba(255,165,0,0.25)"
                  dot={false}
                  strokeDasharray="3 3"
                  strokeWidth={1}
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
              </>
            )}

            {/* Candlesticks */}
            <Bar
              dataKey="candleRange"
              shape={<CandleShape />}
              isAnimationActive={false}
            />

            {/* Current price line */}
            {latest && (
              <ReferenceLine
                y={latest.c}
                stroke="#FF6600"
                strokeDasharray="5 4"
                strokeWidth={1}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* ── Kyle's Lambda Panel ─────────────────────────────── */}
      <div style={{ height: 80, borderTop: "1px solid #333", position: "relative" }}>
        <span
          style={{
            position: "absolute",
            top: 2,
            left: 48,
            fontSize: 8,
            color: "#555",
            fontWeight: 700,
            zIndex: 1,
            fontFamily: "'Courier New', monospace",
          }}
        >
          KYLE &lambda;
        </span>
        <ResponsiveContainer width="100%" height={80}>
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 6, left: 0, bottom: 0 }}
          >
            <CartesianGrid stroke="#1a1a1a" />
            <XAxis
              dataKey="index"
              tick={false}
              axisLine={{ stroke: "#333" }}
            />
            <YAxis
              tick={{ fontSize: 8, fill: "#555" }}
              domain={["auto", "auto"]}
              axisLine={{ stroke: "#333" }}
              width={44}
              tickFormatter={(v: number) => v.toFixed(3)}
            />
            <ReferenceLine
              y={0.012}
              stroke="#FF3366"
              strokeDasharray="4 3"
              label={{
                value: "0.012",
                position: "left",
                fill: "#FF3366",
                fontSize: 8,
                fontWeight: 700,
              }}
            />
            <Line
              dataKey="lambda"
              stroke="#00BFFF"
              dot={false}
              strokeWidth={1.5}
              type="monotone"
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── VPIN Panel ──────────────────────────────────────── */}
      <div style={{ height: 80, borderTop: "1px solid #333", position: "relative" }}>
        <span
          style={{
            position: "absolute",
            top: 2,
            left: 48,
            fontSize: 8,
            color: "#555",
            fontWeight: 700,
            zIndex: 1,
            fontFamily: "'Courier New', monospace",
          }}
        >
          VPIN
        </span>
        <ResponsiveContainer width="100%" height={80}>
          <BarChart
            data={chartData}
            margin={{ top: 8, right: 6, left: 0, bottom: 0 }}
          >
            <CartesianGrid stroke="#1a1a1a" />
            <XAxis
              dataKey="index"
              tick={false}
              axisLine={{ stroke: "#333" }}
            />
            <YAxis
              tick={{ fontSize: 8, fill: "#555" }}
              domain={[0, "auto"]}
              axisLine={{ stroke: "#333" }}
              width={44}
            />
            <ReferenceLine y={0.15} stroke="#333" strokeDasharray="2 2" />
            <ReferenceLine y={0.3} stroke="#333" strokeDasharray="2 2" />
            <Bar dataKey="vpin" isAnimationActive={false}>
              {chartData.map((d, i) => (
                <Cell
                  key={i}
                  fill={
                    d.vpin < 0.15
                      ? "rgba(0,255,136,0.6)"
                      : d.vpin < 0.3
                        ? "rgba(255,165,0,0.6)"
                        : "rgba(255,51,102,0.6)"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Volume Panel ────────────────────────────────────── */}
      <div style={{ height: 80, borderTop: "1px solid #333", position: "relative" }}>
        <span
          style={{
            position: "absolute",
            top: 2,
            left: 48,
            fontSize: 8,
            color: "#555",
            fontWeight: 700,
            zIndex: 1,
            fontFamily: "'Courier New', monospace",
          }}
        >
          VOL
        </span>
        <ResponsiveContainer width="100%" height={80}>
          <BarChart
            data={chartData}
            margin={{ top: 8, right: 6, left: 0, bottom: 5 }}
          >
            <CartesianGrid stroke="#1a1a1a" />
            <XAxis
              dataKey="index"
              ticks={timeTicks}
              tick={{ fontSize: 8, fill: "#555" }}
              tickFormatter={(i: number) =>
                i === chartData.length - 1
                  ? "now"
                  : `-${chartData.length - i}m`
              }
              axisLine={{ stroke: "#333" }}
            />
            <YAxis
              tick={{ fontSize: 8, fill: "#555" }}
              domain={[0, "auto"]}
              axisLine={{ stroke: "#333" }}
              width={44}
            />
            <Bar dataKey="v" isAnimationActive={false}>
              {chartData.map((d, i) => (
                <Cell
                  key={i}
                  fill={
                    d.c >= d.o
                      ? "rgba(0,255,136,0.35)"
                      : "rgba(255,51,102,0.35)"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
