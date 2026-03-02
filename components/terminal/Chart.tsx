"use client";

// OMNI Terminal — Canvas Chart
// Multi-panel: OHLC Candlesticks + Bollinger Bands + Convergence Time Shading
//              Kyle's Lambda EWMA | VPIN Proxy Bars | Volume Bars

import { useRef, useEffect, useState, useMemo, useCallback } from "react";

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
    const impact = Math.abs(c - o) / Math.max(v, 1) * 80;
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

// ── Component ─────────────────────────────────────────────────

export default function Chart({ ticker }: ChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [showBoll, setShowBoll] = useState(true);
  const [showConv, setShowConv] = useState(true);
  const [dims, setDims] = useState({ w: 0, h: 0 });

  const data = useMemo(
    () => (ticker ? generateOHLCV(ticker) : null),
    [ticker],
  );
  const boll = useMemo(() => (data ? computeBollinger(data) : null), [data]);

  // Track container size
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDims({ w: Math.floor(width), h: Math.floor(height) });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  // ── Canvas draw ─────────────────────────────────────────────
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || !boll) return;

    const dpr = window.devicePixelRatio || 1;
    const W = dims.w;
    const H = dims.h;
    if (W < 80 || H < 80) return;

    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = `${W}px`;
    canvas.style.height = `${H}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // ── Layout constants ──
    const L = 44; // left pad (price axis)
    const R = 6; // right pad
    const T = 2; // top pad
    const B = 18; // bottom pad (time axis)
    const chartW = W - L - R;
    const N = data.length;
    const barW = chartW / N;
    const candleW = Math.max(1, barW * 0.55);

    // Panel heights
    const CANDLE_H = Math.floor(H * 0.55);
    const LAMBDA_H = Math.floor(H * 0.12);
    const VPIN_H = Math.floor(H * 0.12);
    const VOL_H = H - CANDLE_H - LAMBDA_H - VPIN_H;

    const GREEN = "#00FF88";
    const RED = "#FF3366";
    const ORANGE = "#FFA500";

    // Clear
    ctx.fillStyle = "#0A0A0A";
    ctx.fillRect(0, 0, W, H);
    ctx.font = "9px 'Courier New', monospace";

    // Helper: x position for bar index
    const xBar = (i: number) => L + i * barW + barW / 2;

    // ── Price range (candle area) ──
    let pMin = Math.min(...data.map((d) => d.l));
    let pMax = Math.max(...data.map((d) => d.h));
    if (showBoll) {
      pMin = Math.min(pMin, ...boll.map((b) => b.lower));
      pMax = Math.max(pMax, ...boll.map((b) => b.upper));
    }
    const pPad = (pMax - pMin) * 0.06 || 1;
    pMin -= pPad;
    pMax += pPad;
    const pRange = pMax - pMin;

    const yP = (p: number) =>
      T + (1 - (p - pMin) / pRange) * (CANDLE_H - T - 2);

    // ── Convergence time shading ──
    if (showConv) {
      for (let i = 0; i < N; i++) {
        const ct = data[i].convTime;
        ctx.fillStyle =
          ct < 60
            ? "rgba(0,255,136,0.05)"
            : ct < 120
              ? "rgba(255,165,0,0.05)"
              : "rgba(255,51,102,0.04)";
        ctx.fillRect(L + i * barW, T, barW, CANDLE_H - T - 2);
      }
    }

    // ── Horizontal grid lines (candle) ──
    const gridN = 5;
    ctx.strokeStyle = "#1a1a1a";
    ctx.lineWidth = 0.5;
    for (let g = 0; g <= gridN; g++) {
      const y = T + (g / gridN) * (CANDLE_H - T - 2);
      ctx.beginPath();
      ctx.moveTo(L, y);
      ctx.lineTo(W - R, y);
      ctx.stroke();

      const pLabel = pMax - (g / gridN) * pRange;
      ctx.fillStyle = "#555";
      ctx.textAlign = "right";
      ctx.fillText(`${pLabel.toFixed(0)}¢`, L - 4, y + 3);
    }

    // ── Bollinger bands ──
    if (showBoll) {
      // Fill between bands
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const x = xBar(i);
        const y = yP(boll[i].upper);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      for (let i = N - 1; i >= 0; i--) {
        ctx.lineTo(xBar(i), yP(boll[i].lower));
      }
      ctx.closePath();
      ctx.fillStyle = "rgba(255,165,0,0.07)";
      ctx.fill();

      // Upper band
      ctx.strokeStyle = "rgba(255,165,0,0.45)";
      ctx.lineWidth = 1;
      ctx.setLineDash([]);
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const x = xBar(i);
        i === 0
          ? ctx.moveTo(x, yP(boll[i].upper))
          : ctx.lineTo(x, yP(boll[i].upper));
      }
      ctx.stroke();

      // Lower band
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const x = xBar(i);
        i === 0
          ? ctx.moveTo(x, yP(boll[i].lower))
          : ctx.lineTo(x, yP(boll[i].lower));
      }
      ctx.stroke();

      // SMA (middle)
      ctx.strokeStyle = "rgba(255,165,0,0.25)";
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const x = xBar(i);
        i === 0
          ? ctx.moveTo(x, yP(boll[i].mid))
          : ctx.lineTo(x, yP(boll[i].mid));
      }
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // ── Candlesticks ──
    for (let i = 0; i < N; i++) {
      const d = data[i];
      const x = xBar(i);
      const bull = d.c >= d.o;
      const col = bull ? GREEN : RED;

      // Wick
      ctx.strokeStyle = col;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, yP(d.h));
      ctx.lineTo(x, yP(d.l));
      ctx.stroke();

      // Body
      const top = yP(Math.max(d.o, d.c));
      const bot = yP(Math.min(d.o, d.c));
      const bodyH = Math.max(1, bot - top);

      ctx.fillStyle = col;
      ctx.fillRect(x - candleW / 2, top, candleW, bodyH);
    }

    // ── Current price dashed line ──
    const lastC = data[N - 1].c;
    const lastY = yP(lastC);
    ctx.strokeStyle = "#FF6600";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(L, lastY);
    ctx.lineTo(W - R, lastY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Price label box
    ctx.fillStyle = "#FF6600";
    const lblW = L - 2;
    ctx.fillRect(0, lastY - 7, lblW, 14);
    ctx.fillStyle = "#000";
    ctx.textAlign = "center";
    ctx.font = "bold 9px 'Courier New', monospace";
    ctx.fillText(`${lastC.toFixed(0)}¢`, lblW / 2, lastY + 3);
    ctx.font = "9px 'Courier New', monospace";

    // ── Panel separators ──
    const drawSep = (y: number) => {
      ctx.strokeStyle = "#333";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    };
    drawSep(CANDLE_H);
    drawSep(CANDLE_H + LAMBDA_H);
    drawSep(CANDLE_H + LAMBDA_H + VPIN_H);

    // ── KYLE'S LAMBDA PANEL ──
    const lY0 = CANDLE_H;
    const lH = LAMBDA_H;
    const lambdas = data.map((d) => d.lambda);
    const lMax = Math.max(0.02, ...lambdas) * 1.15;
    const yL = (v: number) => lY0 + 1 + (1 - v / lMax) * (lH - 3);

    // Panel label
    ctx.fillStyle = "#555";
    ctx.textAlign = "left";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("KYLE \u03BB", L + 3, lY0 + 10);
    ctx.font = "9px 'Courier New', monospace";

    // Grid line
    ctx.strokeStyle = "#1a1a1a";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(L, lY0 + lH / 2);
    ctx.lineTo(W - R, lY0 + lH / 2);
    ctx.stroke();

    // Threshold 0.012
    const threshY = yL(0.012);
    ctx.strokeStyle = RED;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(L, threshY);
    ctx.lineTo(W - R, threshY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = RED;
    ctx.textAlign = "right";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("0.012", L - 4, threshY + 3);
    ctx.font = "9px 'Courier New', monospace";

    // Lambda line
    ctx.strokeStyle = "#00BFFF";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = xBar(i);
      const y = yL(lambdas[i]);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Y labels
    ctx.fillStyle = "#555";
    ctx.textAlign = "right";
    ctx.fillText(lMax.toFixed(3), L - 4, lY0 + 10);
    ctx.fillText("0", L - 4, lY0 + lH - 3);

    // ── VPIN PROXY PANEL ──
    const vY0 = CANDLE_H + LAMBDA_H;
    const vH = VPIN_H;
    const vpins = data.map((d) => d.vpin);
    const vpMax = Math.max(0.4, ...vpins) * 1.15;

    // Label
    ctx.fillStyle = "#555";
    ctx.textAlign = "left";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("VPIN", L + 3, vY0 + 10);
    ctx.font = "9px 'Courier New', monospace";

    // Threshold lines 0.15 and 0.3
    for (const th of [0.15, 0.3]) {
      const ty = vY0 + vH - 2 - (th / vpMax) * (vH - 5);
      ctx.strokeStyle = "#252525";
      ctx.lineWidth = 0.5;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(L, ty);
      ctx.lineTo(W - R, ty);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // VPIN bars
    for (let i = 0; i < N; i++) {
      const x = xBar(i);
      const v = vpins[i];
      const bH = (v / vpMax) * (vH - 5);
      ctx.fillStyle =
        v < 0.15
          ? "rgba(0,255,136,0.6)"
          : v < 0.3
            ? "rgba(255,165,0,0.6)"
            : "rgba(255,51,102,0.6)";
      ctx.fillRect(x - candleW / 2, vY0 + vH - 2 - bH, candleW, bH);
    }

    // ── VOLUME PANEL ──
    const voY0 = CANDLE_H + LAMBDA_H + VPIN_H;
    const voH = VOL_H;
    const vols = data.map((d) => d.v);
    const volMax = Math.max(...vols) * 1.1;

    // Label
    ctx.fillStyle = "#555";
    ctx.textAlign = "left";
    ctx.font = "bold 8px 'Courier New', monospace";
    ctx.fillText("VOL", L + 3, voY0 + 10);
    ctx.font = "9px 'Courier New', monospace";

    // Volume bars
    for (let i = 0; i < N; i++) {
      const x = xBar(i);
      const d = data[i];
      const bH = (d.v / volMax) * (voH - B - 4);
      ctx.fillStyle =
        d.c >= d.o ? "rgba(0,255,136,0.35)" : "rgba(255,51,102,0.35)";
      ctx.fillRect(x - candleW / 2, voY0 + voH - B - bH, candleW, bH);
    }

    // ── Time axis ──
    ctx.fillStyle = "#555";
    ctx.textAlign = "center";
    const tY = H - 4;
    const step = N >= 60 ? 20 : 10;
    for (let i = 0; i < N; i += step) {
      ctx.fillText(`-${N - i}m`, xBar(i), tY);
    }
    ctx.fillText("now", xBar(N - 1), tY);

    // ── Left axis vertical line ──
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(L, 0);
    ctx.lineTo(L, H);
    ctx.stroke();
  }, [data, boll, dims, showBoll, showConv]);

  useEffect(() => {
    draw();
  }, [draw]);

  // ── Render ──

  if (!ticker) {
    return (
      <div
        className="h-full flex items-center justify-center text-zinc-700 text-xs"
        style={{ fontFamily: "'Courier New', monospace" }}
      >
        Select a ticker from watchlist
      </div>
    );
  }

  const latest = data ? data[data.length - 1] : null;
  const first = data ? data[0] : null;
  const change = latest && first ? latest.c - first.o : 0;
  const changeCol = change >= 0 ? "#00FF88" : "#FF3366";

  return (
    <div
      className="h-full flex flex-col"
      style={{ fontFamily: "'Courier New', monospace" }}
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
          <button
            onClick={() => setShowConv((v) => !v)}
            style={{
              fontSize: "8px",
              padding: "1px 5px",
              borderRadius: "2px",
              border: `1px solid ${showConv ? "#00FF88" : "#333"}`,
              background: showConv ? "rgba(0,255,136,0.12)" : "transparent",
              color: showConv ? "#00FF88" : "#555",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            CONV
          </button>
          <span style={{ width: "1px", height: "12px", background: "#333", margin: "0 2px" }} />
          <button
            style={{
              fontSize: "8px",
              padding: "1px 5px",
              borderRadius: "2px",
              border: "1px solid #FF6600",
              background: "rgba(255,102,0,0.12)",
              color: "#FF6600",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            1m
          </button>
          <button
            style={{
              fontSize: "8px",
              padding: "1px 5px",
              borderRadius: "2px",
              border: "1px solid #333",
              background: "transparent",
              color: "#555",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            5m
          </button>
          <button
            style={{
              fontSize: "8px",
              padding: "1px 5px",
              borderRadius: "2px",
              border: "1px solid #333",
              background: "transparent",
              color: "#555",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            15m
          </button>
        </div>
      </div>

      {/* Canvas container */}
      <div ref={containerRef} className="flex-1 min-h-0">
        <canvas ref={canvasRef} style={{ display: "block" }} />
      </div>
    </div>
  );
}
