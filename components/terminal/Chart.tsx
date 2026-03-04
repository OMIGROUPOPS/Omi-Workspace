"use client";

// OMI Terminal — Recharts Chart (Redesigned v3)
// Full-height chart with prominent Greeks cards panel below header.
// Multi-panel: Candlesticks + Bollinger + Kyle's Lambda + VPIN + Volume
// FIXED: Y-axis domain clamped 0-100, auto-scale with padding,
//        clean cent labels, proper candlestick rendering via Bar shape,
//        subtle Bollinger bands, dominant price line.
//        Y-domain computed from OHLC prices ONLY — Bollinger bands excluded.

import { useMemo, useState } from "react";
import {
  ComposedChart,
  LineChart,
  BarChart,
  Bar,
  Line,
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
  time: number; // epoch ms
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

// ── Timeframe config ──────────────────────────────────────────

const TF_CONFIG: Record<string, { bars: number; intervalMs: number; volScale: number }> = {
  "1m":  { bars: 120, intervalMs: 60_000,      volScale: 0.5 },
  "5m":  { bars: 60,  intervalMs: 300_000,     volScale: 0.9 },
  "15m": { bars: 40,  intervalMs: 900_000,     volScale: 1.4 },
  "1h":  { bars: 24,  intervalMs: 3_600_000,   volScale: 2.2 },
};

// ── Data generation ───────────────────────────────────────────

function generateOHLCV(ticker: string, timeframe: string): OHLCV[] {
  const tf = TF_CONFIG[timeframe] || TF_CONFIG["1m"];
  let seed = 0;
  for (let i = 0; i < ticker.length; i++) seed += ticker.charCodeAt(i);
  const rng = new Rng(seed * 31337);

  const bars: OHLCV[] = [];
  let price = (seed % 50) + 25;
  let lambda = 0.007;
  let vpin = 0.12;

  const now = Date.now();

  for (let i = 0; i < tf.bars; i++) {
    const barTime = now - (tf.bars - 1 - i) * tf.intervalMs;
    const o = price;
    const dist50 = price - 50;
    const drift = -dist50 * 0.003;
    const p01 = Math.max(0.02, Math.min(0.98, price / 100));
    const boundaryVol = 1 / (4 * p01 * (1 - p01));
    const vol = (0.3 + rng.next() * 0.8) * Math.sqrt(boundaryVol) * tf.volScale;
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
      time: barTime,
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
      // Clamp Bollinger bands to valid 0-100 range
      result.push({
        mid: mean,
        upper: Math.min(100, mean + std * k),
        lower: Math.max(0, mean - std * k),
      });
    }
  }
  return result;
}

// ── Candlestick Bar shape ─────────────────────────────────────
// Renders the candle body + wicks using the Bar's `shape` prop.
// The Bar is stacked: invisible base (bodyBase) + visible body (bodyHeight).
// This shape function receives pixel coords from Recharts and draws
// the body rect and wick lines using the payload's OHLCV data.

function CandleShape(props: any) {
  const { x, y, width, height, payload } = props;
  if (!payload || payload.o == null || !width || !height) return null;

  const { o, h, l, c, bodyBase, bodyHeight } = payload;
  const bull = c >= o;
  const color = bull ? "#00FF88" : "#FF3366";

  // The bar is drawn from bodyBase upward by bodyHeight.
  // y = top of the body bar (in pixels), height = body height (pixels)
  // We need pixel Y for high and low wicks.
  // Pixel-per-cent = height / bodyHeight (body range in data units)
  // But bodyHeight can be very small (doji), so we need the full range.

  // For the wick, we compute relative to the body top:
  // bodyTop in data = bodyBase + bodyHeight = max(o,c)
  // bodyBot in data = bodyBase = min(o,c)
  // y (pixel) = top of body bar
  // y + height (pixel) = bottom of body bar

  const bodyTop = bodyBase + bodyHeight; // max(o,c) in data space
  const bodyBot = bodyBase;              // min(o,c) in data space

  // pixel per cent — derived from the bar's pixel height vs data height
  // If bodyHeight is 0 (doji), we can't compute pxPerCent from the body.
  // In that case, we skip wick rendering (they'd be tiny anyway).
  const candleWidth = Math.max(2, width * 0.85);
  const xCenter = x + width / 2;
  const xLeft = xCenter - candleWidth / 2;

  // For wicks: we need to convert data-space distances to pixel-space.
  // Since y-axis is inverted (higher values = lower y), higher price = lower pixel.
  // pxPerCent = height / bodyHeight when bodyHeight > 0
  let wickHighY = y;
  let wickLowY = y + height;

  if (bodyHeight > 0.01) {
    const pxPerCent = height / bodyHeight;
    // High wick extends above body top: h - bodyTop in data units
    const wickUpData = h - bodyTop;
    wickHighY = y - wickUpData * pxPerCent;
    // Low wick extends below body bottom: bodyBot - l in data units
    const wickDownData = bodyBot - l;
    wickLowY = y + height + wickDownData * pxPerCent;
  }

  // Body height: at minimum 1px for doji candles
  const bodyH = Math.max(1, height);

  return (
    <g>
      {/* Wick line */}
      <line
        x1={xCenter}
        y1={wickHighY}
        x2={xCenter}
        y2={wickLowY}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body rectangle */}
      <rect
        x={xLeft}
        y={y}
        width={candleWidth}
        height={bodyH}
        fill={bull ? color : color}
        stroke={color}
        strokeWidth={0.5}
        opacity={bull ? 0.9 : 0.9}
      />
    </g>
  );
}

// ── Custom Tooltip ────────────────────────────────────────────

const PriceTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div style={{
      background: "#111",
      border: "1px solid #333",
      padding: "8px 12px",
      fontSize: "10px",
      color: "#999",
      borderRadius: "4px",
      boxShadow: "0 4px 16px rgba(0,0,0,0.6)",
    }}>
      <div style={{ marginBottom: "3px" }}>
        <span style={{ color: "#888" }}>O:</span><span style={{ color: "#ddd", fontWeight: 600 }}>{d.o.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "6px" }}>H:</span><span style={{ color: "#ddd", fontWeight: 600 }}>{d.h.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "6px" }}>L:</span><span style={{ color: "#ddd", fontWeight: 600 }}>{d.l.toFixed(1)}</span>
        <span style={{ color: "#888", marginLeft: "6px" }}>C:</span><span style={{ color: "#ddd", fontWeight: 700 }}>{d.c.toFixed(1)}</span>
      </div>
      <div style={{ color: "#00BCD4" }}>{"\u03BB"}: {d.lambda.toFixed(5)}</div>
      <div style={{ color: d.vpin < 0.15 ? "#00FF88" : d.vpin < 0.3 ? "#FF6600" : "#FF3366" }}>VPIN: {d.vpin.toFixed(3)}</div>
    </div>
  );
};

// ── Greeks Card Panel ─────────────────────────────────────────

function GreeksPanel({ price, sigma }: { price: number; sigma: number }) {
  const greeks = calcGreeks(price / 100, 4, sigma || 0.5);

  const cards = [
    {
      label: "\u0394 Delta",
      value: greeks.delta.toFixed(3),
      color: "#00BCD4",
      bar: greeks.delta,
      barColor: "#00BCD4",
    },
    {
      label: "\u0398 Theta",
      value: `${greeks.theta >= 0 ? "+" : ""}${greeks.theta.toFixed(1)}\u00A2/hr`,
      color: greeks.theta < 0 ? "#FF3366" : "#00FF88",
      bar: Math.min(1, Math.abs(greeks.theta) / 10),
      barColor: greeks.theta < 0 ? "#FF3366" : "#00FF88",
    },
    {
      label: "\u0393 Gamma",
      value: greeks.gamma.toFixed(3),
      color: "#c084fc",
      bar: Math.min(1, greeks.gamma),
      barColor: "#c084fc",
    },
    {
      label: "\u03BD Vega",
      value: greeks.vega.toFixed(3),
      color: "#FFD600",
      bar: Math.min(1, greeks.vega),
      barColor: "#FFD600",
    },
    {
      label: "IV",
      value: `${(greeks.iv * 100).toFixed(0)}%`,
      color: "#FF6600",
      bar: Math.min(1, greeks.iv / 3),
      barColor: "#FF6600",
    },
  ];

  return (
    <div style={{
      display: "flex",
      gap: "4px",
      padding: "4px 2px",
      borderBottom: "1px solid #1a1a1a",
      background: "rgba(0,188,212,0.02)",
      flexShrink: 0,
    }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            flex: 1,
            background: "rgba(255,255,255,0.02)",
            borderRadius: "4px",
            padding: "4px 6px",
            border: "1px solid #1a1a1a",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            width: "100%",
            height: `${Math.max(2, card.bar * 100)}%`,
            background: `${card.barColor}08`,
            transition: "height 0.5s ease-out",
          }} />
          <div style={{ position: "relative", zIndex: 1 }}>
            <div style={{ fontSize: "7px", color: "#555", letterSpacing: "0.05em", fontWeight: 600, marginBottom: "2px" }}>
              {card.label}
            </div>
            <div style={{
              fontSize: "12px",
              fontWeight: 700,
              color: card.color,
              fontVariantNumeric: "tabular-nums",
              textShadow: `0 0 8px ${card.color}30`,
            }}>
              {card.value}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Y-Axis domain and tick helpers ────────────────────────────

function computeYDomain(
  dataMin: number,
  dataMax: number,
): { domain: [number, number]; ticks: number[] } {
  const rawMin = Math.max(0, dataMin);
  const rawMax = Math.min(100, dataMax);
  const range = rawMax - rawMin || 1;

  const pad = range * 0.1;
  let lo = Math.floor((rawMin - pad) / 5) * 5;
  let hi = Math.ceil((rawMax + pad) / 5) * 5;

  lo = Math.max(0, lo);
  hi = Math.min(100, hi);

  if (hi - lo < 10) {
    const mid = (lo + hi) / 2;
    lo = Math.max(0, Math.round(mid - 5));
    hi = Math.min(100, Math.round(mid + 5));
  }

  const span = hi - lo;
  let step: number;
  if (span <= 15) step = 2;
  else if (span <= 30) step = 5;
  else if (span <= 60) step = 10;
  else step = 20;

  const ticks: number[] = [];
  const firstTick = Math.ceil(lo / step) * step;
  for (let v = firstTick; v <= hi; v += step) {
    ticks.push(v);
  }

  return { domain: [lo, hi], ticks };
}

// ── Component ─────────────────────────────────────────────────

export default function Chart({ ticker }: ChartProps) {
  const [showLine, setShowLine] = useState(true);
  const [activeTimeframe, setActiveTimeframe] = useState("1m");

  const data = useMemo(() => (ticker ? generateOHLCV(ticker, activeTimeframe) : null), [ticker, activeTimeframe]);
  const boll = useMemo(() => (data ? computeBollinger(data) : null), [data]);

  const { chartData, yDomain, yTicks } = useMemo(() => {
    if (!data || !boll) return { chartData: [] as any[], yDomain: [0, 100] as [number, number], yTicks: [0, 25, 50, 75, 100] };

    // Y-axis domain from OHLC price data ONLY — exclude Bollinger bands
    // so bands don't inflate the visible range beyond actual price action.
    let dataMin = Infinity;
    let dataMax = -Infinity;
    for (const d of data) {
      dataMin = Math.min(dataMin, d.l);
      dataMax = Math.max(dataMax, d.h);
    }

    const { domain, ticks } = computeYDomain(dataMin, dataMax);

    return {
      chartData: data.map((d, i) => ({
        ...d,
        index: i,
        sma: boll[i].mid,
        bollUpper: boll[i].upper,
        bollLower: boll[i].lower,
        // Candlestick stacked bar data:
        // bodyBase = min(open, close) — invisible base bar
        // bodyHeight = |close - open| — visible body bar
        bodyBase: Math.min(d.o, d.c),
        bodyHeight: Math.max(0.01, Math.abs(d.c - d.o)), // min 0.01 for doji
      })),
      yDomain: domain,
      yTicks: ticks,
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
        fontSize: "11px",
        gap: "12px",
      }}>
        <div style={{
          width: "48px",
          height: "48px",
          borderRadius: "50%",
          border: "2px solid #1a1a1a",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "20px",
          color: "#222",
        }}>
          {"\u25C8"}
        </div>
        <div style={{ color: "#444" }}>Select a market from the watchlist</div>
        <div style={{ fontSize: "9px", color: "#333" }}>Click any ticker on the left to load chart data</div>
      </div>
    );
  }

  const latest = data ? data[data.length - 1] : null;
  const first = data ? data[0] : null;
  const change = latest && first ? latest.c - first.o : 0;
  const changeCol = change >= 0 ? "#00FF88" : "#FF3366";
  const changeArrow = change >= 0 ? "\u25B2" : "\u25BC";

  const eventTicker = ticker.replace(/-[YN]$/, "");
  const parts = ticker.split("-");
  let rawTeam = parts.length >= 3 ? parts[parts.length - 2] : parts[parts.length - 1] || ticker.slice(-8);
  if (/^\d+[A-Z]+\d+/.test(rawTeam) && parts.length >= 4) {
    rawTeam = parts[parts.length - 3] || rawTeam;
  }
  const tickerLabel = parseTickerLabel(ticker, rawTeam, eventTicker);
  const eventName = parseEventName(eventTicker);

  const tickStep = Math.max(1, Math.floor(chartData.length / 5));
  const timeTicks: number[] = [];
  for (let i = 0; i < chartData.length; i += tickStep) timeTicks.push(i);
  if (timeTicks[timeTicks.length - 1] !== chartData.length - 1) timeTicks.push(chartData.length - 1);

  const formatTime = (idx: number) => {
    const bar = chartData[idx];
    if (!bar || !bar.time) return "";
    const d = new Date(bar.time);
    const hh = d.getHours().toString().padStart(2, "0");
    const mm = d.getMinutes().toString().padStart(2, "0");
    if (activeTimeframe === "1h") {
      const mon = (d.getMonth() + 1).toString().padStart(2, "0");
      const day = d.getDate().toString().padStart(2, "0");
      return `${mon}/${day} ${hh}:${mm}`;
    }
    return `${hh}:${mm}`;
  };

  const timeframes = ["1m", "5m", "15m", "1h"];

  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", minHeight: 0, overflow: "hidden" }}>
      {/* ── Ticker header — Bloomberg-style ── */}
      <div className="flex items-center justify-between shrink-0" style={{
        height: "38px",
        padding: "0 6px",
        borderBottom: "1px solid #1a1a1a",
        background: "rgba(255,255,255,0.01)",
      }}>
        <div className="flex items-center gap-3">
          <span style={{ color: "#eee", fontWeight: 700, fontSize: "14px", letterSpacing: "0.02em" }}>
            {tickerLabel}
          </span>
          <span style={{ color: "#555", fontSize: "10px" }}>{eventName}</span>
          {latest && (
            <span style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "3px 10px",
              borderRadius: "4px",
              border: `1px solid ${change >= 0 ? "rgba(0,255,136,0.3)" : "rgba(255,51,102,0.3)"}`,
              background: change >= 0 ? "rgba(0,255,136,0.08)" : "rgba(255,51,102,0.08)",
            }}>
              <span style={{
                color: changeCol,
                fontWeight: 700,
                fontSize: "20px",
                fontVariantNumeric: "tabular-nums",
                textShadow: `0 0 16px ${change >= 0 ? "rgba(0,255,136,0.3)" : "rgba(255,51,102,0.3)"}`,
              }}>
                {latest.c.toFixed(0)}&cent;
              </span>
              <span style={{ color: changeCol, fontSize: "11px", fontWeight: 600 }}>
                {changeArrow}{change >= 0 ? "+" : ""}{change.toFixed(1)}
              </span>
            </span>
          )}
          {latest && (
            <span style={{ color: "#555", fontSize: "9px", fontVariantNumeric: "tabular-nums" }}>
              H:{latest.h.toFixed(0)} L:{latest.l.toFixed(0)} V:{latest.v}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowLine((v) => !v)}
            style={{
              fontSize: "9px", padding: "3px 8px", borderRadius: "3px",
              border: `1px solid ${showLine ? "#00BCD4" : "#2a2a2a"}`,
              background: showLine ? "rgba(0,188,212,0.15)" : "transparent",
              color: showLine ? "#00BCD4" : "#555", cursor: "pointer",
              fontWeight: 600, letterSpacing: "0.05em",
              transition: "all 0.15s",
              minWidth: "42px",
              textAlign: "center" as const,
            }}
          >
            {showLine ? "LINE" : "OHLC"}
          </button>
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setActiveTimeframe(tf)}
              style={{
                fontSize: "9px", padding: "3px 8px", borderRadius: "3px",
                border: `1px solid ${activeTimeframe === tf ? "#FF6600" : "#2a2a2a"}`,
                background: activeTimeframe === tf ? "rgba(255,102,0,0.15)" : "transparent",
                color: activeTimeframe === tf ? "#FF6600" : "#555", cursor: "pointer",
                fontWeight: 600, letterSpacing: "0.05em",
                transition: "all 0.15s",
              }}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* ── Greeks Card Panel ── */}
      {latest && (
        <GreeksPanel price={latest.c} sigma={latest.vpin} />
      )}

      {/* ── Main Price Chart ── */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 6, left: 0, bottom: 4 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis
              dataKey="index"
              ticks={timeTicks}
              tick={{ fontSize: 8, fill: "#666" }}
              tickFormatter={formatTime}
              axisLine={{ stroke: "#1a1a1a" }}
              tickLine={{ stroke: "#333" }}
              interval={0}
              height={20}
            />
            <YAxis
              yAxisId="price"
              domain={yDomain}
              ticks={yTicks}
              tick={{ fontSize: 9, fill: "#555" }}
              tickFormatter={(v: number) => `${v}\u00A2`}
              axisLine={{ stroke: "#1a1a1a" }}
              width={40}
              allowDataOverflow={true}
            />
            <Tooltip content={<PriceTooltip />} cursor={{ stroke: "#333", strokeDasharray: "3 3" }} />

            {showLine ? (
              <>
                {/* ── LINE mode ── */}
                {/* Bollinger upper & lower — thin dashed, subtle */}
                <Line
                  yAxisId="price"
                  dataKey="bollUpper"
                  stroke="rgba(255,102,0,0.25)"
                  dot={false}
                  strokeWidth={0.8}
                  strokeDasharray="4 3"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  yAxisId="price"
                  dataKey="bollLower"
                  stroke="rgba(255,102,0,0.25)"
                  dot={false}
                  strokeWidth={0.8}
                  strokeDasharray="4 3"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                {/* SMA midline — thin dashed yellow */}
                <Line
                  yAxisId="price"
                  dataKey="sma"
                  stroke="#FFD600"
                  dot={false}
                  strokeWidth={1}
                  strokeDasharray="6 4"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                {/* Close price — dominant white line */}
                <Line
                  yAxisId="price"
                  dataKey="c"
                  stroke="#FFFFFF"
                  dot={false}
                  strokeWidth={2.5}
                  type="monotone"
                  isAnimationActive={false}
                />
              </>
            ) : (
              <>
                {/* ── OHLC Candlestick mode ── */}
                {/* Bollinger bands — very subtle in OHLC mode */}
                <Line
                  yAxisId="price"
                  dataKey="bollUpper"
                  stroke="rgba(255,102,0,0.15)"
                  dot={false}
                  strokeWidth={0.6}
                  strokeDasharray="3 3"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  yAxisId="price"
                  dataKey="bollLower"
                  stroke="rgba(255,102,0,0.15)"
                  dot={false}
                  strokeWidth={0.6}
                  strokeDasharray="3 3"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                <Line
                  yAxisId="price"
                  dataKey="sma"
                  stroke="rgba(255,214,0,0.4)"
                  dot={false}
                  strokeWidth={0.8}
                  strokeDasharray="6 4"
                  type="monotone"
                  isAnimationActive={false}
                  tooltipType="none"
                />
                {/* Stacked Bar candlesticks:
                    Base bar (bodyBase) is invisible — positions the visible bar correctly.
                    Body bar (bodyHeight) uses custom shape to draw candle + wicks. */}
                <Bar
                  yAxisId="price"
                  dataKey="bodyBase"
                  stackId="candle"
                  fill="transparent"
                  stroke="none"
                  isAnimationActive={false}
                />
                <Bar
                  yAxisId="price"
                  dataKey="bodyHeight"
                  stackId="candle"
                  shape={<CandleShape />}
                  isAnimationActive={false}
                />
              </>
            )}

            {/* Current price reference line */}
            {latest && (
              <ReferenceLine
                yAxisId="price"
                y={latest.c}
                stroke="#FF6600"
                strokeDasharray="5 4"
                strokeWidth={1}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* ── Kyle's Lambda Panel ── */}
      <div style={{ height: 48, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{
          position: "absolute", top: 3, left: 36, fontSize: 8, color: "#555", fontWeight: 700, zIndex: 1,
          letterSpacing: "0.08em", textTransform: "uppercase",
        }}>
          KYLE {"\u03BB"}
        </div>
        {latest && (
          <div style={{
            position: "absolute", top: 2, right: 8, fontSize: 14, color: "#00BCD4", fontWeight: 700, zIndex: 1,
            fontVariantNumeric: "tabular-nums",
            textShadow: "0 0 10px rgba(0,188,212,0.3)",
          }}>
            {latest.lambda.toFixed(4)}
          </div>
        )}
        <ResponsiveContainer width="100%" height={48}>
          <LineChart data={chartData} margin={{ top: 8, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis dataKey="index" tick={false} axisLine={{ stroke: "#1a1a1a" }} />
            <YAxis tick={{ fontSize: 7, fill: "#333" }} domain={["auto", "auto"]} axisLine={{ stroke: "#1a1a1a" }} width={40} tickFormatter={(v: number) => v.toFixed(3)} />
            <ReferenceLine y={0.012} stroke="#FF3366" strokeDasharray="4 3" strokeWidth={1.5} label={{ value: "0.012", position: "right", fill: "#FF3366", fontSize: 7 }} />
            <Line dataKey="lambda" stroke="#00BCD4" dot={false} strokeWidth={1.5} type="monotone" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── VPIN Panel ── */}
      <div style={{ height: 48, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{
          position: "absolute", top: 3, left: 36, fontSize: 8, color: "#555", fontWeight: 700, zIndex: 1,
          letterSpacing: "0.08em", textTransform: "uppercase",
        }}>
          VPIN
        </div>
        {latest && (
          <div style={{
            position: "absolute", top: 2, right: 8, fontSize: 14, fontWeight: 700, zIndex: 1,
            fontVariantNumeric: "tabular-nums",
            color: latest.vpin < 0.15 ? "#00FF88" : latest.vpin < 0.3 ? "#FF6600" : "#FF3366",
            textShadow: `0 0 10px ${latest.vpin < 0.15 ? "rgba(0,255,136,0.3)" : latest.vpin < 0.3 ? "rgba(255,102,0,0.3)" : "rgba(255,51,102,0.3)"}`,
          }}>
            {latest.vpin.toFixed(3)}
          </div>
        )}
        <ResponsiveContainer width="100%" height={48}>
          <BarChart data={chartData} margin={{ top: 8, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#141414" />
            <XAxis dataKey="index" tick={false} axisLine={{ stroke: "#1a1a1a" }} />
            <YAxis tick={{ fontSize: 7, fill: "#333" }} domain={[0, "auto"]} axisLine={{ stroke: "#1a1a1a" }} width={40} />
            <ReferenceLine y={0.15} stroke="#333" strokeDasharray="2 2" />
            <ReferenceLine y={0.3} stroke="#333" strokeDasharray="2 2" />
            <Bar dataKey="vpin" isAnimationActive={false}>
              {chartData.map((d: any, i: number) => (
                <Cell key={i} fill={d.vpin < 0.15 ? "rgba(0,255,136,0.5)" : d.vpin < 0.3 ? "rgba(255,102,0,0.5)" : "rgba(255,51,102,0.5)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Volume Panel — compact ── */}
      <div style={{ height: 32, borderTop: "1px solid #1a1a1a", position: "relative" }}>
        <div style={{ position: "absolute", top: 2, left: 36, fontSize: 8, color: "#444", fontWeight: 700, zIndex: 1, letterSpacing: "0.05em" }}>
          VOL
        </div>
        <ResponsiveContainer width="100%" height={32}>
          <BarChart data={chartData} margin={{ top: 6, right: 6, left: 0, bottom: 2 }}>
            <XAxis
              dataKey="index" ticks={timeTicks}
              tick={{ fontSize: 7, fill: "#555" }}
              tickFormatter={formatTime}
              axisLine={{ stroke: "#1a1a1a" }}
              tickLine={{ stroke: "#333" }}
            />
            <YAxis tick={false} axisLine={false} width={40} />
            <Bar dataKey="v" isAnimationActive={false}>
              {chartData.map((d: any, i: number) => (
                <Cell key={i} fill={d.c >= d.o ? "rgba(0,255,136,0.3)" : "rgba(255,51,102,0.3)"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
