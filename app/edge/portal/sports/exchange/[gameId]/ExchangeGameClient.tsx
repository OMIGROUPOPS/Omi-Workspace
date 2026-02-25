'use client';

import { useState, useMemo, useRef, useEffect } from 'react';

// --- Dark terminal palette ---
const P = {
  pageBg: '#0b0b0b',
  cardBg: '#111111',
  cardBorder: '#1a1a1a',
  headerBar: '#0e0e0e',
  chartBg: '#080808',
  textPrimary: '#dddddd',
  textSecondary: '#888888',
  textMuted: '#555555',
  textFaint: '#333333',
  greenText: '#22c55e',
  greenBg: 'rgba(34,197,94,0.08)',
  greenBorder: 'rgba(34,197,94,0.25)',
  redText: '#ef4444',
  redBg: 'rgba(239,68,68,0.06)',
  redBorder: 'rgba(239,68,68,0.20)',
};

const PLATFORM_CONFIG: Record<string, { name: string; color: string }> = {
  kalshi: { name: 'Kalshi', color: '#00d395' },
  polymarket: { name: 'Polymarket', color: '#7C3AED' },
};

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  fanduel: { name: 'FanDuel', color: '#1493ff' },
  draftkings: { name: 'DraftKings', color: '#53d337' },
};

interface ExchangeGameClientProps {
  gameId: string;
  homeTeam: string;
  awayTeam: string;
  commenceTime?: string;
  sportKey: string;
  platform: string;
  fairLines: {
    fair_spread: number | null;
    fair_total: number | null;
    fair_ml_home: number | null;
    fair_ml_away: number | null;
  } | null;
  history: {
    exchange: string;
    market_type: string;
    yes_price: number | null;
    no_price: number | null;
    subtitle: string | null;
    event_title: string;
    snapshot_time: string;
  }[];
  contracts: {
    exchange: string;
    market_type: string;
    yes_price: number | null;
    no_price: number | null;
    subtitle: string | null;
    event_title: string;
    snapshot_time: string;
  }[];
  sportsbookOdds?: Record<string, {
    h2h?: { homePrice: number; awayPrice: number };
    spreads?: { line: number; homePrice: number; awayPrice: number };
    totals?: { line: number; overPrice: number; underPrice: number };
  }>;
}

// --- Helpers ---

function toProb(americanOdds: number): number {
  return americanOdds < 0
    ? Math.abs(americanOdds) / (Math.abs(americanOdds) + 100)
    : 100 / (americanOdds + 100);
}

function fmtOdds(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

const PROB_PER_POINT = 3; // ~3% probability per spread/total point

/** Fair cents for a spread contract.
 *  contractSpread: signed spread from contract (e.g., -8.5)
 *  teamSide: 'home' | 'away' — which team the contract is about
 *  fairSpread: OMI fair spread from home perspective (negative = home favored)
 */
function calcSpreadFairCents(contractSpread: number, teamSide: 'home' | 'away', fairSpread: number): number {
  // Convert OMI fair spread to the contract team's perspective
  const fairForTeam = teamSide === 'home' ? fairSpread : -fairSpread;
  // delta > 0 → contract is easier to cover than OMI expects → higher probability
  const delta = contractSpread - fairForTeam;
  return Math.max(1, Math.min(99, Math.round(50 + delta * PROB_PER_POINT)));
}

/** Fair cents for a total contract (YES = Over).
 *  contractTotal: the total number from the contract (e.g., 147.5)
 *  fairTotal: OMI fair total
 */
function calcTotalFairCents(contractTotal: number, fairTotal: number): number {
  // If fairTotal > contractTotal → Over is more likely → higher fair cents
  return Math.max(1, Math.min(99, Math.round(50 + (fairTotal - contractTotal) * PROB_PER_POINT)));
}

/** Edge as percentage: positive = underpriced (good to buy YES) */
function calcEdgePct(fairCents: number, yesCents: number): number {
  return ((fairCents - yesCents) / yesCents) * 100;
}

// --- Chart types ---
type ChartSeries = { label: string; color: string; data: { time: Date; value: number }[] };
type FairRef = { value: number; label: string };

// --- Generic Price Chart ---
function PriceChart({
  series, fairRefs, platform, yLabel,
}: {
  series: ChartSeries[];
  fairRefs: FairRef[];
  platform: string;
  yLabel?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const allPoints = series.flatMap(s => s.data);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container || allPoints.length === 0) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const pad = { top: 24, right: 80, bottom: 32, left: 50 };
    const cW = W - pad.left - pad.right;
    const cH = H - pad.top - pad.bottom;

    ctx.fillStyle = P.chartBg;
    ctx.fillRect(0, 0, W, H);

    // Auto-scale Y axis
    const allVals = [...allPoints.map(p => p.value), ...fairRefs.map(f => f.value)];
    const dataMin = Math.min(...allVals);
    const dataMax = Math.max(...allVals);
    const yPad = Math.max((dataMax - dataMin) * 0.15, 5);
    const yMin = Math.max(0, Math.floor((dataMin - yPad) / 5) * 5);
    const yMax = Math.min(100, Math.ceil((dataMax + yPad) / 5) * 5);
    const yRange = yMax - yMin || 1;

    const times = allPoints.map(p => p.time.getTime());
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);
    const timeRange = maxTime - minTime || 1;

    const isSparse = allPoints.length <= 2;
    const toX = (t: Date, i?: number) => isSparse
      ? pad.left + (((i ?? 0) + 0.5) / Math.max(allPoints.length, 1)) * cW
      : pad.left + ((t.getTime() - minTime) / timeRange) * cW;
    const toY = (p: number) => pad.top + ((yMax - p) / yRange) * cH;

    // Grid lines
    ctx.strokeStyle = '#e2e4e8';
    ctx.lineWidth = 0.5;
    const gridStep = yRange <= 20 ? 5 : yRange <= 50 ? 10 : 25;
    for (let p = yMin; p <= yMax; p += gridStep) {
      const y = toY(p);
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(W - pad.right, y);
      ctx.stroke();
      ctx.fillStyle = P.textMuted;
      ctx.font = '10px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(`${p}${yLabel || '%'}`, pad.left - 6, y + 3);
    }

    // Time labels
    const sortedTimes = [...new Set(allPoints.map(p => p.time.getTime()))].sort((a, b) => a - b);
    ctx.textAlign = 'center';
    ctx.fillStyle = P.textMuted;
    ctx.font = '10px monospace';
    const labelCount = Math.min(5, sortedTimes.length);
    for (let i = 0; i < labelCount; i++) {
      const idx = Math.floor((i / (labelCount - 1 || 1)) * (sortedTimes.length - 1));
      const t = new Date(sortedTimes[idx]);
      const x = toX(t, idx);
      ctx.fillText(
        t.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }),
        x, H - 8
      );
    }

    // 50% reference line (if visible)
    if (yMin < 50 && yMax > 50) {
      ctx.strokeStyle = '#d1d5db';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(pad.left, toY(50));
      ctx.lineTo(W - pad.right, toY(50));
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Fair reference lines
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 3]);
    for (const fr of fairRefs) {
      if (fr.value >= yMin && fr.value <= yMax) {
        ctx.beginPath();
        ctx.moveTo(pad.left, toY(fr.value));
        ctx.lineTo(W - pad.right, toY(fr.value));
        ctx.stroke();
      }
    }
    ctx.setLineDash([]);
    ctx.font = '9px monospace';
    ctx.fillStyle = '#06b6d4';
    ctx.textAlign = 'left';
    for (const fr of fairRefs) {
      if (fr.value >= yMin && fr.value <= yMax) {
        ctx.fillText(fr.label, W - pad.right + 4, toY(fr.value) + 3);
      }
    }

    // Draw each series
    for (const s of series) {
      const pts = s.data;
      if (pts.length === 0) continue;

      if (pts.length <= 2) {
        // Sparse: dots + labels
        for (let i = 0; i < pts.length; i++) {
          const x = toX(pts[i].time, i);
          const y = toY(pts[i].value);
          ctx.fillStyle = s.color;
          ctx.beginPath(); ctx.arc(x, y, 6, 0, Math.PI * 2); ctx.fill();
          ctx.font = 'bold 11px sans-serif';
          ctx.textAlign = 'left';
          ctx.fillText(`${s.label} ${pts[i].value}%`, x + 10, y + 4);
        }
      } else {
        // Line
        ctx.strokeStyle = s.color;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        for (let i = 0; i < pts.length; i++) {
          const x = toX(pts[i].time, i);
          const y = toY(pts[i].value);
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        // Endpoint dot + label
        const last = pts[pts.length - 1];
        const lx = toX(last.time, pts.length - 1);
        ctx.fillStyle = s.color;
        ctx.beginPath(); ctx.arc(lx, toY(last.value), 4, 0, Math.PI * 2); ctx.fill();
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`${s.label} ${last.value}%`, W - pad.right + 4, toY(last.value) + 4);
      }
    }
  }, [series, fairRefs, platform, allPoints, yLabel]);

  if (allPoints.length === 0) {
    return (
      <div style={{ background: P.chartBg, borderRadius: 8, padding: 40, textAlign: 'center' }}>
        <span style={{ fontSize: 13, color: P.textMuted }}>No price history available for this market</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: 340, borderRadius: 8, overflow: 'hidden' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}

// --- Contract Row ---
function ContractRow({
  label, yesCents, noCents, fairCents, subtitle,
}: {
  label: string;
  yesCents: number | null;
  noCents: number | null;
  fairCents?: number | null;
  subtitle?: string;
}) {
  const edgePct = fairCents != null && yesCents != null && yesCents > 0
    ? calcEdgePct(fairCents, yesCents)
    : null;
  const hasEdge = edgePct != null && Math.abs(edgePct) > 3;
  const isPositive = edgePct != null && edgePct > 3;
  const isNegative = edgePct != null && edgePct < -3;

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
      alignItems: 'center', padding: '10px 12px',
      borderBottom: `1px solid ${P.cardBorder}`,
      background: isPositive ? P.greenBg : isNegative ? P.redBg : 'transparent',
      borderLeft: hasEdge ? `3px solid ${isPositive ? P.greenBorder : P.redBorder}` : '3px solid transparent',
      fontSize: 13,
    }}>
      <div>
        <span style={{ fontWeight: 600, color: P.textPrimary }}>{label}</span>
        {subtitle && <span style={{ fontSize: 10, color: P.textMuted, marginLeft: 6 }}>{subtitle}</span>}
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: P.textPrimary }}>
        {yesCents != null ? `${yesCents}\u00a2` : '--'}
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: P.textSecondary }}>
        {noCents != null ? `${noCents}\u00a2` : '--'}
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: '#06b6d4' }}>
        {fairCents != null ? `${fairCents}\u00a2` : '--'}
      </div>
      <div style={{
        textAlign: 'center', fontFamily: 'monospace', fontWeight: 600,
        color: isPositive ? P.greenText : isNegative ? P.redText : P.textMuted,
      }}>
        {edgePct != null ? `${edgePct > 0 ? '+' : ''}${edgePct.toFixed(1)}%` : '--'}
      </div>
    </div>
  );
}

// --- Sportsbook Comparison Row ---
function CompRow({ color, label, col1, col2, col3, col4, highlight }: {
  color: string;
  label: string;
  col1: string;
  col2: string;
  col3: string;
  col4: string;
  highlight?: boolean;
}) {
  const textColor = highlight ? '#06b6d4' : P.textPrimary;
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr 1fr',
      alignItems: 'center', padding: '8px 12px',
      borderBottom: `1px solid ${P.cardBorder}`, fontSize: 12,
      background: highlight ? P.chartBg : 'transparent',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 6, height: 6, borderRadius: '50%', background: color, flexShrink: 0 }} />
        <span style={{ fontWeight: 600, color: textColor }}>{label}</span>
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: textColor }}>{col1}</div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: textColor }}>{col2}</div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: textColor }}>{col3}</div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: textColor }}>{col4}</div>
    </div>
  );
}

// --- Main Component ---
export function ExchangeGameClient({
  gameId, homeTeam, awayTeam, commenceTime, sportKey, platform,
  fairLines, history, contracts, sportsbookOdds,
}: ExchangeGameClientProps) {
  const [activeMarket, setActiveMarket] = useState<'moneyline' | 'spread' | 'total'>('moneyline');

  const platformConfig = PLATFORM_CONFIG[platform] || PLATFORM_CONFIG.kalshi;
  const gameTime = commenceTime ? new Date(commenceTime) : null;
  const timeStr = gameTime
    ? gameTime.toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
    : '';

  // Team matching
  const homeLast = homeTeam.toLowerCase().split(' ').pop()!;
  const awayLast = awayTeam.toLowerCase().split(' ').pop()!;

  const matchTeam = (sub: string): 'home' | 'away' | null => {
    const s = sub.toLowerCase();
    const homeLower = homeTeam.toLowerCase();
    const awayLower = awayTeam.toLowerCase();
    if (s.includes(homeLast) || s.includes(homeLower) || homeLower.includes(s)) return 'home';
    if (s.includes(awayLast) || s.includes(awayLower) || awayLower.includes(s)) return 'away';
    return null;
  };

  // Separate contracts by market type and platform
  const platformContracts = contracts.filter(c => c.exchange === platform);
  const mlContracts = platformContracts.filter(c => c.market_type === 'moneyline' && c.subtitle && c.subtitle !== 'Draw');
  const drawContracts = platformContracts.filter(c => c.market_type === 'moneyline' && c.subtitle === 'Draw');
  const spreadContracts = platformContracts.filter(c => c.market_type === 'spread' && c.subtitle);
  const totalContracts = platformContracts.filter(c => c.market_type === 'total' && c.subtitle);

  // Fair values as cents for ML
  const fairHomeCents = fairLines?.fair_ml_home != null ? Math.round(toProb(fairLines.fair_ml_home) * 100) : null;
  const fairAwayCents = fairLines?.fair_ml_away != null ? Math.round(toProb(fairLines.fair_ml_away) * 100) : null;

  const homeMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'home');
  const awayMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'away');

  // --- Parse spread contract info ---
  const parseSpreadContract = (c: typeof contracts[0]) => {
    const sub = c.subtitle || '';
    const lineMatch = sub.match(/\(([+-]?\d+\.?\d*)\)/);
    const spreadNum = lineMatch ? parseFloat(lineMatch[1]) : null;
    const teamName = sub.replace(/\s*\([^)]*\)\s*$/, '').trim();
    const teamSide = matchTeam(teamName);
    const fairCents = spreadNum != null && teamSide && fairLines?.fair_spread != null
      ? calcSpreadFairCents(spreadNum, teamSide, fairLines.fair_spread)
      : null;
    return { teamName, spreadNum, teamSide, fairCents };
  };

  // --- Parse total contract info ---
  const parseTotalContract = (c: typeof contracts[0]) => {
    const lineMatch = (c.subtitle || '').match(/([\d.]+)/);
    const totalNum = lineMatch ? parseFloat(lineMatch[1]) : null;
    const fairCents = totalNum != null && fairLines?.fair_total != null
      ? calcTotalFairCents(totalNum, fairLines.fair_total)
      : null;
    return { totalNum, fairCents };
  };

  // --- Sorted spread contracts by edge (highest positive first) ---
  const sortedSpreadContracts = useMemo(() => {
    return [...spreadContracts].sort((a, b) => {
      const aInfo = parseSpreadContract(a);
      const bInfo = parseSpreadContract(b);
      const aEdge = aInfo.fairCents != null && a.yes_price != null && a.yes_price > 0
        ? calcEdgePct(aInfo.fairCents, a.yes_price) : -Infinity;
      const bEdge = bInfo.fairCents != null && b.yes_price != null && b.yes_price > 0
        ? calcEdgePct(bInfo.fairCents, b.yes_price) : -Infinity;
      return bEdge - aEdge;
    });
  }, [spreadContracts, fairLines]);

  // --- Sorted total contracts by edge (highest positive first) ---
  const sortedTotalContracts = useMemo(() => {
    return [...totalContracts].sort((a, b) => {
      const aInfo = parseTotalContract(a);
      const bInfo = parseTotalContract(b);
      const aEdge = aInfo.fairCents != null && a.yes_price != null && a.yes_price > 0
        ? calcEdgePct(aInfo.fairCents, a.yes_price) : -Infinity;
      const bEdge = bInfo.fairCents != null && b.yes_price != null && b.yes_price > 0
        ? calcEdgePct(bInfo.fairCents, b.yes_price) : -Infinity;
      return bEdge - aEdge;
    });
  }, [totalContracts, fairLines]);

  // --- Primary contracts for chart ---
  const primarySpread = useMemo(() => {
    if (spreadContracts.length === 0) return null;
    // Closest to 50¢
    return [...spreadContracts].sort((a, b) =>
      Math.abs((a.yes_price ?? 50) - 50) - Math.abs((b.yes_price ?? 50) - 50)
    )[0];
  }, [spreadContracts]);

  const primaryTotal = useMemo(() => {
    if (totalContracts.length === 0) return null;
    return [...totalContracts].sort((a, b) =>
      Math.abs((a.yes_price ?? 50) - 50) - Math.abs((b.yes_price ?? 50) - 50)
    )[0];
  }, [totalContracts]);

  // --- Chart data based on active market ---
  const { chartSeries, chartFairRefs, chartTitle, chartLegend } = useMemo(() => {
    const platformColor = platformConfig.color;
    const awayColor = '#ef4444';

    if (activeMarket === 'moneyline') {
      // ML: two lines (home/away)
      const mlHistory = history.filter(h => h.market_type === 'moneyline' && h.subtitle);
      const byTime = new Map<string, typeof mlHistory>();
      for (const h of mlHistory) {
        const arr = byTime.get(h.snapshot_time) || [];
        arr.push(h);
        byTime.set(h.snapshot_time, arr);
      }
      const homeData: { time: Date; value: number }[] = [];
      const awayData: { time: Date; value: number }[] = [];
      for (const [time, rows] of byTime) {
        let hp: number | null = null;
        let ap: number | null = null;
        for (const r of rows) {
          const side = matchTeam(r.subtitle || '');
          if (side === 'home') hp = r.yes_price;
          else if (side === 'away') ap = r.yes_price;
        }
        if (hp != null && ap != null) {
          const t = new Date(time);
          homeData.push({ time: t, value: hp });
          awayData.push({ time: t, value: ap });
        }
      }
      homeData.sort((a, b) => a.time.getTime() - b.time.getTime());
      awayData.sort((a, b) => a.time.getTime() - b.time.getTime());

      const refs: FairRef[] = [];
      if (fairHomeCents != null) refs.push({ value: fairHomeCents, label: `OMI ${fairHomeCents}%` });
      if (fairAwayCents != null) refs.push({ value: fairAwayCents, label: `OMI ${fairAwayCents}%` });

      const homeLabel = homeTeam.split(' ').pop() || 'Home';
      const awayLabel = awayTeam.split(' ').pop() || 'Away';

      return {
        chartSeries: [
          { label: homeLabel, color: platformColor, data: homeData },
          { label: awayLabel, color: awayColor, data: awayData },
        ],
        chartFairRefs: refs,
        chartTitle: 'Win Probability',
        chartLegend: [
          { label: homeTeam, color: platformColor },
          { label: awayTeam, color: awayColor },
          ...(refs.length > 0 ? [{ label: 'OMI Fair', color: '#06b6d4', dashed: true }] : []),
        ],
      };
    }

    if (activeMarket === 'spread' && primarySpread) {
      const sub = primarySpread.subtitle || '';
      const matchedHistory = history.filter(h =>
        h.market_type === 'spread' && h.subtitle === sub && h.yes_price != null
      );
      const data = matchedHistory
        .map(h => ({ time: new Date(h.snapshot_time), value: h.yes_price! }))
        .sort((a, b) => a.time.getTime() - b.time.getTime());

      const info = parseSpreadContract(primarySpread);
      const refs: FairRef[] = [];
      if (info.fairCents != null) refs.push({ value: info.fairCents, label: `OMI ${info.fairCents}¢` });

      return {
        chartSeries: [{ label: sub, color: platformColor, data }],
        chartFairRefs: refs,
        chartTitle: `Spread: ${sub}`,
        chartLegend: [
          { label: sub, color: platformColor },
          ...(refs.length > 0 ? [{ label: 'OMI Fair', color: '#06b6d4', dashed: true }] : []),
        ],
      };
    }

    if (activeMarket === 'total' && primaryTotal) {
      const sub = primaryTotal.subtitle || '';
      const matchedHistory = history.filter(h =>
        h.market_type === 'total' && h.subtitle === sub && h.yes_price != null
      );
      const data = matchedHistory
        .map(h => ({ time: new Date(h.snapshot_time), value: h.yes_price! }))
        .sort((a, b) => a.time.getTime() - b.time.getTime());

      const info = parseTotalContract(primaryTotal);
      const refs: FairRef[] = [];
      if (info.fairCents != null) refs.push({ value: info.fairCents, label: `OMI ${info.fairCents}¢` });

      const lineMatch = sub.match(/([\d.]+)/);
      const line = lineMatch ? lineMatch[1] : '';

      return {
        chartSeries: [{ label: `Over ${line}`, color: platformColor, data }],
        chartFairRefs: refs,
        chartTitle: `Total: ${sub}`,
        chartLegend: [
          { label: `Over ${line}`, color: platformColor },
          ...(refs.length > 0 ? [{ label: 'OMI Fair', color: '#06b6d4', dashed: true }] : []),
        ],
      };
    }

    // Fallback: empty
    return { chartSeries: [], chartFairRefs: [], chartTitle: 'Price History', chartLegend: [] };
  }, [activeMarket, history, homeTeam, awayTeam, fairHomeCents, fairAwayCents, primarySpread, primaryTotal, fairLines, platformConfig.color]);

  const markets = [
    { key: 'moneyline' as const, label: 'Moneyline', count: mlContracts.length + drawContracts.length },
    { key: 'spread' as const, label: 'Spread', count: spreadContracts.length },
    { key: 'total' as const, label: 'Total', count: totalContracts.length },
  ];

  const hasBooks = sportsbookOdds && Object.keys(sportsbookOdds).length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Game Header */}
      <div style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: P.textPrimary }}>
              {awayTeam} <span style={{ color: P.textMuted, fontWeight: 400 }}>at</span> {homeTeam}
            </div>
            <div style={{ fontSize: 12, color: P.textSecondary, marginTop: 2 }} suppressHydrationWarning>{timeStr}</div>
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 10px', borderRadius: 6,
            background: P.headerBar, border: `1px solid ${P.cardBorder}`,
          }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: platformConfig.color }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: P.textPrimary }}>{platformConfig.name}</span>
          </div>
        </div>
      </div>

      {/* Market Tabs — ABOVE chart so they control it */}
      <div style={{ display: 'flex', gap: 4 }}>
        {markets.map(m => (
          <button key={m.key} onClick={() => setActiveMarket(m.key)}
            style={{
              padding: '6px 14px', borderRadius: 6, border: `1px solid ${P.cardBorder}`,
              background: activeMarket === m.key ? P.textPrimary : P.cardBg,
              color: activeMarket === m.key ? '#ffffff' : P.textSecondary,
              fontSize: 12, fontWeight: 600, cursor: 'pointer',
            }}
          >
            {m.label} {m.count > 0 && <span style={{ opacity: 0.6 }}>({m.count})</span>}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: `1px solid ${P.cardBorder}` }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: P.textPrimary, letterSpacing: 1, textTransform: 'uppercase' }}>
            {chartTitle}
          </span>
        </div>
        <div style={{ padding: 12 }}>
          <PriceChart series={chartSeries} fairRefs={chartFairRefs} platform={platform} />
        </div>
        <div style={{ padding: '8px 16px', borderTop: `1px solid ${P.cardBorder}`, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {chartLegend.map((item, i) => (
            <div key={i} className="flex items-center gap-1.5">
              <div style={{
                width: 16, height: 'dashed' in item ? 2 : 3,
                background: item.color, borderRadius: 1,
                ...('dashed' in item ? { borderTop: `1px dashed ${item.color}` } : {}),
              }} />
              <span style={{ fontSize: 10, color: P.textSecondary }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Contracts Grid */}
      <div style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 12, overflow: 'hidden' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
          padding: '8px 12px', background: P.headerBar,
          borderBottom: `1px solid ${P.cardBorder}`,
          fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <div>Contract</div>
          <div style={{ textAlign: 'center' }}>YES</div>
          <div style={{ textAlign: 'center' }}>NO</div>
          <div style={{ textAlign: 'center' }}>OMI Fair</div>
          <div style={{ textAlign: 'center' }}>Edge %</div>
        </div>

        {activeMarket === 'moneyline' && (
          <>
            {homeMl && (
              <ContractRow label={homeTeam} yesCents={homeMl.yes_price} noCents={homeMl.no_price} fairCents={fairHomeCents} subtitle="Win" />
            )}
            {awayMl && (
              <ContractRow label={awayTeam} yesCents={awayMl.yes_price} noCents={awayMl.no_price} fairCents={fairAwayCents} subtitle="Win" />
            )}
            {drawContracts.length > 0 && drawContracts.map((c, i) => (
              <ContractRow key={`draw-${i}`} label="Draw" yesCents={c.yes_price} noCents={c.no_price} />
            ))}
            {!homeMl && !awayMl && drawContracts.length === 0 && (
              <div style={{ padding: 24, textAlign: 'center', color: P.textMuted, fontSize: 13 }}>
                No moneyline contracts available
              </div>
            )}
          </>
        )}

        {activeMarket === 'spread' && (
          <>
            {sortedSpreadContracts.length > 0 ? (
              sortedSpreadContracts.map((c, i) => {
                const info = parseSpreadContract(c);
                return (
                  <ContractRow
                    key={i}
                    label={info.teamName}
                    subtitle={info.spreadNum != null ? `(${info.spreadNum > 0 ? '+' : ''}${info.spreadNum})` : undefined}
                    yesCents={c.yes_price}
                    noCents={c.no_price}
                    fairCents={info.fairCents}
                  />
                );
              })
            ) : (
              <div style={{ padding: 24, textAlign: 'center', color: P.textMuted, fontSize: 13 }}>
                No spread contracts available
              </div>
            )}
          </>
        )}

        {activeMarket === 'total' && (
          <>
            {sortedTotalContracts.length > 0 ? (
              sortedTotalContracts.map((c, i) => {
                const info = parseTotalContract(c);
                const lineMatch = (c.subtitle || '').match(/([\d.]+)/);
                const line = lineMatch ? lineMatch[1] : '';
                return (
                  <ContractRow
                    key={i}
                    label={`O/U ${line}`}
                    subtitle={`YES = Over ${line}`}
                    yesCents={c.yes_price}
                    noCents={c.no_price}
                    fairCents={info.fairCents}
                  />
                );
              })
            ) : (
              <div style={{ padding: 24, textAlign: 'center', color: P.textMuted, fontSize: 13 }}>
                No total contracts available
              </div>
            )}
          </>
        )}
      </div>

      {/* Sportsbook Comparison */}
      {hasBooks && (
        <div style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ padding: '10px 16px', borderBottom: `1px solid ${P.cardBorder}` }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: P.textPrimary, letterSpacing: 1, textTransform: 'uppercase' }}>
              Sportsbook Comparison
            </span>
          </div>

          {activeMarket === 'moneyline' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Home</div>
                <div style={{ textAlign: 'center' }}>Away</div>
                <div style={{ textAlign: 'center' }}>Home Impl %</div>
                <div style={{ textAlign: 'center' }}>Away Impl %</div>
              </div>
              {/* Exchange row */}
              <CompRow
                color={platformConfig.color}
                label={platformConfig.name}
                col1={homeMl?.yes_price != null ? `${homeMl.yes_price}\u00a2` : '--'}
                col2={awayMl?.yes_price != null ? `${awayMl.yes_price}\u00a2` : '--'}
                col3={homeMl?.yes_price != null ? `${homeMl.yes_price}%` : '--'}
                col4={awayMl?.yes_price != null ? `${awayMl.yes_price}%` : '--'}
                highlight
              />
              {/* Sportsbook rows */}
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => {
                const homeImpl = odds.h2h?.homePrice != null ? (toProb(odds.h2h.homePrice) * 100).toFixed(1) : null;
                const awayImpl = odds.h2h?.awayPrice != null ? (toProb(odds.h2h.awayPrice) * 100).toFixed(1) : null;
                return (
                  <CompRow
                    key={key}
                    color={BOOK_CONFIG[key]?.color || '#888888'}
                    label={BOOK_CONFIG[key]?.name || key}
                    col1={odds.h2h?.homePrice != null ? fmtOdds(odds.h2h.homePrice) : '--'}
                    col2={odds.h2h?.awayPrice != null ? fmtOdds(odds.h2h.awayPrice) : '--'}
                    col3={homeImpl ? `${homeImpl}%` : '--'}
                    col4={awayImpl ? `${awayImpl}%` : '--'}
                  />
                );
              })}
              {/* OMI Fair row */}
              {fairLines?.fair_ml_home != null && fairLines?.fair_ml_away != null && (
                <CompRow
                  color="#06b6d4"
                  label="OMI Fair"
                  col1={fmtOdds(fairLines.fair_ml_home)}
                  col2={fmtOdds(fairLines.fair_ml_away)}
                  col3={fairHomeCents != null ? `${fairHomeCents}%` : '--'}
                  col4={fairAwayCents != null ? `${fairAwayCents}%` : '--'}
                  highlight
                />
              )}
            </>
          )}

          {activeMarket === 'spread' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Line</div>
                <div style={{ textAlign: 'center' }}>Home</div>
                <div style={{ textAlign: 'center' }}>Home Impl %</div>
                <div style={{ textAlign: 'center' }}>Away Impl %</div>
              </div>
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => {
                if (!odds.spreads) return null;
                const homeImpl = (toProb(odds.spreads.homePrice) * 100).toFixed(1);
                const awayImpl = (toProb(odds.spreads.awayPrice) * 100).toFixed(1);
                const line = odds.spreads.line;
                return (
                  <CompRow
                    key={key}
                    color={BOOK_CONFIG[key]?.color || '#888888'}
                    label={BOOK_CONFIG[key]?.name || key}
                    col1={line > 0 ? `+${line}` : `${line}`}
                    col2={fmtOdds(odds.spreads.homePrice)}
                    col3={`${homeImpl}%`}
                    col4={`${awayImpl}%`}
                  />
                );
              })}
              {fairLines?.fair_spread != null && (
                <CompRow
                  color="#06b6d4"
                  label="OMI Fair"
                  col1={fairLines.fair_spread > 0 ? `+${fairLines.fair_spread}` : `${fairLines.fair_spread}`}
                  col2="--"
                  col3="--"
                  col4="--"
                  highlight
                />
              )}
            </>
          )}

          {activeMarket === 'total' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Line</div>
                <div style={{ textAlign: 'center' }}>Over</div>
                <div style={{ textAlign: 'center' }}>Over Impl %</div>
                <div style={{ textAlign: 'center' }}>Under Impl %</div>
              </div>
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => {
                if (!odds.totals) return null;
                const overImpl = (toProb(odds.totals.overPrice) * 100).toFixed(1);
                const underImpl = (toProb(odds.totals.underPrice) * 100).toFixed(1);
                return (
                  <CompRow
                    key={key}
                    color={BOOK_CONFIG[key]?.color || '#888888'}
                    label={BOOK_CONFIG[key]?.name || key}
                    col1={`${odds.totals.line}`}
                    col2={fmtOdds(odds.totals.overPrice)}
                    col3={`${overImpl}%`}
                    col4={`${underImpl}%`}
                  />
                );
              })}
              {fairLines?.fair_total != null && (
                <CompRow
                  color="#06b6d4"
                  label="OMI Fair"
                  col1={fairLines.fair_total.toFixed(1)}
                  col2="--"
                  col3="--"
                  col4="--"
                  highlight
                />
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
