'use client';

import { useState, useMemo, useRef, useEffect } from 'react';

const P = {
  pageBg: '#ebedf0',
  cardBg: '#ffffff',
  cardBorder: '#e2e4e8',
  headerBar: '#f4f5f7',
  chartBg: '#f7f8f9',
  textPrimary: '#1f2937',
  textSecondary: '#6b7280',
  textMuted: '#9ca3af',
  textFaint: '#b0b5bd',
  greenText: '#16a34a',
  greenBg: 'rgba(34,197,94,0.06)',
  greenBorder: 'rgba(34,197,94,0.3)',
  redText: '#dc2626',
  redBg: 'rgba(239,68,68,0.06)',
  redBorder: 'rgba(239,68,68,0.25)',
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

function toProb(americanOdds: number): number {
  return americanOdds < 0
    ? Math.abs(americanOdds) / (Math.abs(americanOdds) + 100)
    : 100 / (americanOdds + 100);
}

function fmtOdds(v: number | null | undefined): string {
  if (v == null) return '--';
  return v > 0 ? `+${v}` : `${v}`;
}

// --- Probability Chart ---
function ProbabilityChart({
  history, homeTeam, awayTeam, fairLines, platform,
}: {
  history: ExchangeGameClientProps['history'];
  homeTeam: string;
  awayTeam: string;
  fairLines: ExchangeGameClientProps['fairLines'];
  platform: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const chartData = useMemo(() => {
    const homeLower = homeTeam.toLowerCase();
    const awayLower = awayTeam.toLowerCase();
    const homeLast = homeLower.split(' ').pop()!;
    const awayLast = awayLower.split(' ').pop()!;

    const matchSub = (sub: string): 'home' | 'away' | null => {
      const s = sub.toLowerCase();
      if (s.includes(homeLast) || s.includes(homeLower) || homeLower.includes(s)) return 'home';
      if (s.includes(awayLast) || s.includes(awayLower) || awayLower.includes(s)) return 'away';
      return null;
    };

    const mlHistory = history.filter(h => h.market_type === 'moneyline' && h.subtitle);
    const byTime = new Map<string, typeof mlHistory>();
    for (const h of mlHistory) {
      const arr = byTime.get(h.snapshot_time) || [];
      arr.push(h);
      byTime.set(h.snapshot_time, arr);
    }

    const points: { time: Date; homeProb: number; awayProb: number }[] = [];
    for (const [time, rows] of byTime) {
      let homeProb: number | null = null;
      let awayProb: number | null = null;
      for (const r of rows) {
        const side = matchSub(r.subtitle || '');
        if (side === 'home') homeProb = r.yes_price;
        else if (side === 'away') awayProb = r.yes_price;
      }
      if (homeProb != null && awayProb != null) {
        points.push({ time: new Date(time), homeProb, awayProb });
      }
    }
    return points.sort((a, b) => a.time.getTime() - b.time.getTime());
  }, [history, homeTeam, awayTeam]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container || chartData.length === 0) return;

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

    // Auto-scale Y axis to data range with padding
    const allProbs = chartData.flatMap(d => [d.homeProb, d.awayProb]);
    const fairProbs: number[] = [];
    if (fairLines?.fair_ml_home != null) fairProbs.push(Math.round(toProb(fairLines.fair_ml_home) * 100));
    if (fairLines?.fair_ml_away != null) fairProbs.push(Math.round(toProb(fairLines.fair_ml_away) * 100));
    const allVals = [...allProbs, ...fairProbs];
    const dataMin = Math.min(...allVals);
    const dataMax = Math.max(...allVals);
    const yPad = Math.max((dataMax - dataMin) * 0.15, 5);
    const yMin = Math.max(0, Math.floor((dataMin - yPad) / 5) * 5);
    const yMax = Math.min(100, Math.ceil((dataMax + yPad) / 5) * 5);
    const yRange = yMax - yMin || 1;

    const minTime = chartData[0].time.getTime();
    const maxTime = chartData[chartData.length - 1].time.getTime();
    const timeRange = maxTime - minTime || 1;

    const isSparse = chartData.length <= 2;
    const toX = isSparse
      ? (_t: Date, i: number) => pad.left + ((i + 0.5) / Math.max(chartData.length, 1)) * cW
      : (t: Date) => pad.left + ((t.getTime() - minTime) / timeRange) * cW;
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
      ctx.fillText(`${p}%`, pad.left - 6, y + 3);
    }

    // Time labels
    ctx.textAlign = 'center';
    ctx.fillStyle = P.textMuted;
    ctx.font = '10px monospace';
    const labelCount = Math.min(5, chartData.length);
    for (let i = 0; i < labelCount; i++) {
      const idx = Math.floor((i / (labelCount - 1 || 1)) * (chartData.length - 1));
      const pt = chartData[idx];
      const x = toX(pt.time, idx);
      ctx.fillText(
        pt.time.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }),
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

    // Fair line references
    if (fairLines?.fair_ml_home != null && fairLines?.fair_ml_away != null) {
      const fairHome = Math.round(toProb(fairLines.fair_ml_home) * 100);
      const fairAway = Math.round(toProb(fairLines.fair_ml_away) * 100);
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 1;
      ctx.setLineDash([6, 3]);
      for (const fv of [fairHome, fairAway]) {
        ctx.beginPath();
        ctx.moveTo(pad.left, toY(fv));
        ctx.lineTo(W - pad.right, toY(fv));
        ctx.stroke();
      }
      ctx.setLineDash([]);
      ctx.font = '9px monospace';
      ctx.fillStyle = '#06b6d4';
      ctx.textAlign = 'left';
      ctx.fillText(`OMI ${fairHome}%`, W - pad.right + 4, toY(fairHome) + 3);
      ctx.fillText(`OMI ${fairAway}%`, W - pad.right + 4, toY(fairAway) + 3);
    }

    const platformColor = PLATFORM_CONFIG[platform]?.color || '#00d395';
    const awayColor = '#ef4444';
    const homeLabel = homeTeam.split(' ').pop();
    const awayLabel = awayTeam.split(' ').pop();

    if (isSparse) {
      for (let i = 0; i < chartData.length; i++) {
        const x = toX(chartData[i].time, i);
        const yHome = toY(chartData[i].homeProb);
        const yAway = toY(chartData[i].awayProb);
        // Dots
        ctx.fillStyle = platformColor;
        ctx.beginPath(); ctx.arc(x, yHome, 6, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = awayColor;
        ctx.beginPath(); ctx.arc(x, yAway, 6, 0, Math.PI * 2); ctx.fill();
        // Labels
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillStyle = platformColor;
        ctx.fillText(`${homeLabel} ${chartData[i].homeProb}%`, x + 10, yHome + 4);
        ctx.fillStyle = awayColor;
        ctx.fillText(`${awayLabel} ${chartData[i].awayProb}%`, x + 10, yAway + 4);
      }
    } else {
      // Home line
      ctx.strokeStyle = platformColor;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      for (let i = 0; i < chartData.length; i++) {
        const x = toX(chartData[i].time, i);
        const y = toY(chartData[i].homeProb);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      // Away line
      ctx.strokeStyle = awayColor;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      for (let i = 0; i < chartData.length; i++) {
        const x = toX(chartData[i].time, i);
        const y = toY(chartData[i].awayProb);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      // Endpoint dots + labels
      const last = chartData[chartData.length - 1];
      const lx = toX(last.time, chartData.length - 1);
      ctx.fillStyle = platformColor;
      ctx.beginPath(); ctx.arc(lx, toY(last.homeProb), 4, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = awayColor;
      ctx.beginPath(); ctx.arc(lx, toY(last.awayProb), 4, 0, Math.PI * 2); ctx.fill();
      ctx.font = 'bold 10px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillStyle = platformColor;
      ctx.fillText(`${homeLabel} ${last.homeProb}%`, W - pad.right + 4, toY(last.homeProb) + 4);
      ctx.fillStyle = awayColor;
      ctx.fillText(`${awayLabel} ${last.awayProb}%`, W - pad.right + 4, toY(last.awayProb) + 4);
    }
  }, [chartData, fairLines, homeTeam, awayTeam, platform]);

  if (chartData.length === 0) {
    return (
      <div style={{ background: P.chartBg, borderRadius: 8, padding: 40, textAlign: 'center' }}>
        <span style={{ fontSize: 13, color: P.textMuted }}>No probability history available</span>
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
  label, yesCents, noCents, fairCents, subtitle, edgeHighlight,
}: {
  label: string;
  yesCents: number | null;
  noCents: number | null;
  fairCents?: number | null;
  subtitle?: string;
  edgeHighlight?: boolean;
}) {
  const edge = fairCents != null && yesCents != null ? yesCents - fairCents : null;
  const hasEdge = edge != null && Math.abs(edge) > 2;
  const isPositive = edge != null && edge > 2;
  const isNegative = edge != null && edge < -2;

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
        {edge != null ? `${edge > 0 ? '+' : ''}${edge.toFixed(1)}` : '--'}
      </div>
    </div>
  );
}

// --- Sportsbook Comparison Row ---
function BookRow({ bookKey, label, homeOdds, awayOdds, line }: {
  bookKey: string;
  label: string;
  homeOdds?: number;
  awayOdds?: number;
  line?: number;
}) {
  const color = BOOK_CONFIG[bookKey]?.color || '#6b7280';
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
      alignItems: 'center', padding: '8px 12px',
      borderBottom: `1px solid ${P.cardBorder}`, fontSize: 12,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 6, height: 6, borderRadius: '50%', background: color, flexShrink: 0 }} />
        <span style={{ fontWeight: 600, color: P.textPrimary }}>{label}</span>
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: P.textPrimary }}>
        {homeOdds != null ? fmtOdds(homeOdds) : '--'}
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: P.textPrimary }}>
        {awayOdds != null ? fmtOdds(awayOdds) : '--'}
      </div>
      <div style={{ textAlign: 'center', fontFamily: 'monospace', color: P.textSecondary }}>
        {line != null ? (line > 0 ? `+${line}` : `${line}`) : '--'}
      </div>
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

  // Separate contracts by market type and platform
  const platformContracts = contracts.filter(c => c.exchange === platform);
  const mlContracts = platformContracts.filter(c => c.market_type === 'moneyline' && c.subtitle && c.subtitle !== 'Draw');
  const drawContracts = platformContracts.filter(c => c.market_type === 'moneyline' && c.subtitle === 'Draw');
  const spreadContracts = platformContracts.filter(c => c.market_type === 'spread' && c.subtitle);
  const totalContracts = platformContracts.filter(c => c.market_type === 'total' && c.subtitle);

  // Fair values as cents
  const fairHomeCents = fairLines?.fair_ml_home != null ? Math.round(toProb(fairLines.fair_ml_home) * 100) : null;
  const fairAwayCents = fairLines?.fair_ml_away != null ? Math.round(toProb(fairLines.fair_ml_away) * 100) : null;

  const homeLast = homeTeam.toLowerCase().split(' ').pop()!;
  const awayLast = awayTeam.toLowerCase().split(' ').pop()!;

  const matchTeam = (sub: string) => {
    const s = sub.toLowerCase();
    const homeLower = homeTeam.toLowerCase();
    const awayLower = awayTeam.toLowerCase();
    if (s.includes(homeLast) || s.includes(homeLower) || homeLower.includes(s)) return 'home';
    if (s.includes(awayLast) || s.includes(awayLower) || awayLower.includes(s)) return 'away';
    return null;
  };

  const homeMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'home');
  const awayMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'away');

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

      {/* Probability Chart */}
      <div style={{ background: P.cardBg, border: `1px solid ${P.cardBorder}`, borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: `1px solid ${P.cardBorder}` }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: P.textPrimary, letterSpacing: 1, textTransform: 'uppercase' }}>
            Win Probability
          </span>
        </div>
        <div style={{ padding: 12 }}>
          <ProbabilityChart history={history} homeTeam={homeTeam} awayTeam={awayTeam} fairLines={fairLines} platform={platform} />
        </div>
        <div style={{ padding: '8px 16px', borderTop: `1px solid ${P.cardBorder}`, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 16, height: 3, background: platformConfig.color, borderRadius: 1 }} />
            <span style={{ fontSize: 10, color: P.textSecondary }}>{homeTeam}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 16, height: 3, background: '#ef4444', borderRadius: 1 }} />
            <span style={{ fontSize: 10, color: P.textSecondary }}>{awayTeam}</span>
          </div>
          {fairLines?.fair_ml_home != null && (
            <div className="flex items-center gap-1.5">
              <div style={{ width: 16, height: 2, background: '#06b6d4', borderRadius: 1, borderTop: '1px dashed #06b6d4' }} />
              <span style={{ fontSize: 10, color: P.textSecondary }}>OMI Fair</span>
            </div>
          )}
        </div>
      </div>

      {/* Market Tabs */}
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
          <div style={{ textAlign: 'center' }}>Edge</div>
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
            {spreadContracts.length > 0 ? (
              spreadContracts
                .sort((a, b) => Math.abs((a.yes_price ?? 50) - 50) - Math.abs((b.yes_price ?? 50) - 50))
                .map((c, i) => {
                  const sub = c.subtitle || c.event_title || '';
                  const lineMatch = sub.match(/\(([+-]?\d+\.?\d*)\)/);
                  const lineStr = lineMatch ? lineMatch[1] : '';
                  const teamName = sub.replace(/\s*\([^)]*\)\s*$/, '');
                  return (
                    <ContractRow
                      key={i}
                      label={teamName}
                      subtitle={lineStr ? `(${lineStr})` : undefined}
                      yesCents={c.yes_price}
                      noCents={c.no_price}
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
            {totalContracts.length > 0 ? (
              totalContracts
                .sort((a, b) => {
                  const aLine = parseFloat((a.subtitle || '').match(/[\d.]+/)?.[0] || '0');
                  const bLine = parseFloat((b.subtitle || '').match(/[\d.]+/)?.[0] || '0');
                  return aLine - bLine;
                })
                .map((c, i) => {
                  const lineMatch = (c.subtitle || '').match(/([\d.]+)/);
                  const line = lineMatch ? lineMatch[1] : '';
                  return (
                    <ContractRow
                      key={i}
                      label={`O/U ${line}`}
                      subtitle={`YES = Over ${line}`}
                      yesCents={c.yes_price}
                      noCents={c.no_price}
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
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Home</div>
                <div style={{ textAlign: 'center' }}>Away</div>
                <div style={{ textAlign: 'center' }}>Implied %</div>
              </div>
              {/* Exchange row */}
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                alignItems: 'center', padding: '8px 12px',
                borderBottom: `1px solid ${P.cardBorder}`, fontSize: 12,
                background: P.chartBg,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: platformConfig.color, flexShrink: 0 }} />
                  <span style={{ fontWeight: 600, color: P.textPrimary }}>{platformConfig.name}</span>
                </div>
                <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: P.textPrimary }}>
                  {homeMl?.yes_price != null ? `${homeMl.yes_price}\u00a2` : '--'}
                </div>
                <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: P.textPrimary }}>
                  {awayMl?.yes_price != null ? `${awayMl.yes_price}\u00a2` : '--'}
                </div>
                <div style={{ textAlign: 'center', fontFamily: 'monospace', color: P.textSecondary }}>--</div>
              </div>
              {/* Sportsbook rows */}
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => (
                <BookRow
                  key={key}
                  bookKey={key}
                  label={BOOK_CONFIG[key]?.name || key}
                  homeOdds={odds.h2h?.homePrice}
                  awayOdds={odds.h2h?.awayPrice}
                />
              ))}
              {/* OMI Fair row */}
              {fairLines?.fair_ml_home != null && (
                <div style={{
                  display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                  alignItems: 'center', padding: '8px 12px',
                  borderBottom: `1px solid ${P.cardBorder}`, fontSize: 12,
                  background: P.chartBg,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#06b6d4', flexShrink: 0 }} />
                    <span style={{ fontWeight: 600, color: '#06b6d4' }}>OMI Fair</span>
                  </div>
                  <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: '#06b6d4' }}>
                    {fmtOdds(fairLines.fair_ml_home)}
                  </div>
                  <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: '#06b6d4' }}>
                    {fmtOdds(fairLines.fair_ml_away)}
                  </div>
                  <div style={{ textAlign: 'center', fontFamily: 'monospace', color: '#06b6d4' }}>
                    {fairHomeCents != null ? `${fairHomeCents}%` : '--'}
                  </div>
                </div>
              )}
            </>
          )}

          {activeMarket === 'spread' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Line</div>
                <div style={{ textAlign: 'center' }}>Home</div>
                <div style={{ textAlign: 'center' }}>Away</div>
              </div>
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => (
                odds.spreads ? (
                  <BookRow
                    key={key}
                    bookKey={key}
                    label={BOOK_CONFIG[key]?.name || key}
                    homeOdds={odds.spreads.homePrice}
                    awayOdds={odds.spreads.awayPrice}
                    line={odds.spreads.line}
                  />
                ) : null
              ))}
              {fairLines?.fair_spread != null && (
                <div style={{
                  display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                  alignItems: 'center', padding: '8px 12px', fontSize: 12, background: P.chartBg,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#06b6d4', flexShrink: 0 }} />
                    <span style={{ fontWeight: 600, color: '#06b6d4' }}>OMI Fair</span>
                  </div>
                  <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: '#06b6d4' }}>
                    {fairLines.fair_spread > 0 ? `+${fairLines.fair_spread}` : fairLines.fair_spread}
                  </div>
                  <div style={{ textAlign: 'center' }}>--</div>
                  <div style={{ textAlign: 'center' }}>--</div>
                </div>
              )}
            </>
          )}

          {activeMarket === 'total' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                padding: '6px 12px', background: P.headerBar,
                borderBottom: `1px solid ${P.cardBorder}`,
                fontSize: 9, fontWeight: 700, color: P.textMuted, letterSpacing: 1, textTransform: 'uppercase',
              }}>
                <div>Book</div>
                <div style={{ textAlign: 'center' }}>Line</div>
                <div style={{ textAlign: 'center' }}>Over</div>
                <div style={{ textAlign: 'center' }}>Under</div>
              </div>
              {Object.entries(sportsbookOdds || {}).map(([key, odds]) => (
                odds.totals ? (
                  <BookRow
                    key={key}
                    bookKey={key}
                    label={BOOK_CONFIG[key]?.name || key}
                    homeOdds={odds.totals.overPrice}
                    awayOdds={odds.totals.underPrice}
                    line={odds.totals.line}
                  />
                ) : null
              ))}
              {fairLines?.fair_total != null && (
                <div style={{
                  display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
                  alignItems: 'center', padding: '8px 12px', fontSize: 12, background: P.chartBg,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#06b6d4', flexShrink: 0 }} />
                    <span style={{ fontWeight: 600, color: '#06b6d4' }}>OMI Fair</span>
                  </div>
                  <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: '#06b6d4' }}>
                    {fairLines.fair_total.toFixed(1)}
                  </div>
                  <div style={{ textAlign: 'center' }}>--</div>
                  <div style={{ textAlign: 'center' }}>--</div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
