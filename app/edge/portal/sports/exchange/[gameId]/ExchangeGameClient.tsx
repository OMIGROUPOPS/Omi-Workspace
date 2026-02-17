'use client';

import { useState, useMemo, useRef, useEffect } from 'react';

// Light theme palette
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
  greenBg: 'rgba(34,197,94,0.08)',
  greenBorder: 'rgba(34,197,94,0.3)',
  redText: '#dc2626',
  redBg: 'rgba(239,68,68,0.06)',
  redBorder: 'rgba(239,68,68,0.25)',
};

const PLATFORM_CONFIG: Record<string, { name: string; color: string }> = {
  kalshi: { name: 'Kalshi', color: '#00d395' },
  polymarket: { name: 'Polymarket', color: '#7C3AED' },
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
}

function toProb(americanOdds: number): number {
  return americanOdds < 0
    ? Math.abs(americanOdds) / (Math.abs(americanOdds) + 100)
    : 100 / (americanOdds + 100);
}

// Probability chart using canvas
function ProbabilityChart({
  history,
  homeTeam,
  awayTeam,
  fairLines,
  platform,
}: {
  history: ExchangeGameClientProps['history'];
  homeTeam: string;
  awayTeam: string;
  fairLines: ExchangeGameClientProps['fairLines'];
  platform: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Extract ML history: group by snapshot_time, find home/away contracts
  const chartData = useMemo(() => {
    const mlHistory = history.filter(h => h.market_type === 'moneyline' && h.subtitle);
    if (mlHistory.length === 0) return [];

    // Group by snapshot_time
    const byTime = new Map<string, typeof mlHistory>();
    for (const h of mlHistory) {
      const arr = byTime.get(h.snapshot_time) || [];
      arr.push(h);
      byTime.set(h.snapshot_time, arr);
    }

    const homeLower = homeTeam.toLowerCase();
    const awayLower = awayTeam.toLowerCase();
    const homeLast = homeLower.split(' ').pop()!;
    const awayLast = awayLower.split(' ').pop()!;

    const points: { time: Date; homeProb: number; awayProb: number }[] = [];
    for (const [time, rows] of byTime) {
      let homeProb: number | null = null;
      let awayProb: number | null = null;
      for (const r of rows) {
        const sub = (r.subtitle || '').toLowerCase();
        if (sub.includes(homeLast) || sub.includes(homeLower)) {
          homeProb = r.yes_price;
        } else if (sub.includes(awayLast) || sub.includes(awayLower)) {
          awayProb = r.yes_price;
        }
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
    const pad = { top: 20, right: 20, bottom: 30, left: 45 };
    const cW = W - pad.left - pad.right;
    const cH = H - pad.top - pad.bottom;

    // Clear
    ctx.fillStyle = P.chartBg;
    ctx.fillRect(0, 0, W, H);

    const minTime = chartData[0].time.getTime();
    const maxTime = chartData[chartData.length - 1].time.getTime();
    const timeRange = maxTime - minTime || 1;

    const toX = (t: Date) => pad.left + ((t.getTime() - minTime) / timeRange) * cW;
    const toY = (p: number) => pad.top + ((100 - p) / 100) * cH;

    // Grid lines
    ctx.strokeStyle = '#e2e4e8';
    ctx.lineWidth = 0.5;
    for (const p of [0, 25, 50, 75, 100]) {
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
    const labelCount = Math.min(5, chartData.length);
    for (let i = 0; i < labelCount; i++) {
      const idx = Math.floor((i / (labelCount - 1 || 1)) * (chartData.length - 1));
      const pt = chartData[idx];
      const x = toX(pt.time);
      ctx.fillText(
        pt.time.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }),
        x,
        H - 6
      );
    }

    // 50% reference line
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, toY(50));
    ctx.lineTo(W - pad.right, toY(50));
    ctx.stroke();
    ctx.setLineDash([]);

    // Fair line references
    if (fairLines?.fair_ml_home != null && fairLines?.fair_ml_away != null) {
      const fairHome = Math.round(toProb(fairLines.fair_ml_home) * 100);
      const fairAway = Math.round(toProb(fairLines.fair_ml_away) * 100);
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 1;
      ctx.setLineDash([6, 3]);
      ctx.beginPath();
      ctx.moveTo(pad.left, toY(fairHome));
      ctx.lineTo(W - pad.right, toY(fairHome));
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(pad.left, toY(fairAway));
      ctx.lineTo(W - pad.right, toY(fairAway));
      ctx.stroke();
      ctx.setLineDash([]);

      // Labels
      ctx.font = '9px monospace';
      ctx.fillStyle = '#06b6d4';
      ctx.textAlign = 'left';
      ctx.fillText(`OMI ${fairHome}%`, W - pad.right + 3, toY(fairHome) + 3);
      ctx.fillText(`OMI ${fairAway}%`, W - pad.right + 3, toY(fairAway) + 3);
    }

    // Home probability line
    const platformColor = PLATFORM_CONFIG[platform]?.color || '#00d395';
    ctx.strokeStyle = platformColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < chartData.length; i++) {
      const x = toX(chartData[i].time);
      const y = toY(chartData[i].homeProb);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Away probability line
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < chartData.length; i++) {
      const x = toX(chartData[i].time);
      const y = toY(chartData[i].awayProb);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Legend
    const lastPt = chartData[chartData.length - 1];
    ctx.font = 'bold 10px sans-serif';
    ctx.fillStyle = platformColor;
    ctx.textAlign = 'right';
    ctx.fillText(`${homeTeam.split(' ').pop()} ${lastPt.homeProb}%`, W - pad.right - 4, toY(lastPt.homeProb) - 6);
    ctx.fillStyle = '#ef4444';
    ctx.fillText(`${awayTeam.split(' ').pop()} ${lastPt.awayProb}%`, W - pad.right - 4, toY(lastPt.awayProb) - 6);
  }, [chartData, fairLines, homeTeam, awayTeam, platform]);

  if (chartData.length === 0) {
    return (
      <div style={{ background: P.chartBg, borderRadius: 8, padding: 40, textAlign: 'center' }}>
        <span style={{ fontSize: 13, color: P.textMuted }}>No probability history available</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: 300, borderRadius: 8, overflow: 'hidden' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}

// Contract row component
function ContractRow({
  label,
  yesCents,
  noCents,
  fairCents,
  subtitle,
}: {
  label: string;
  yesCents: number | null;
  noCents: number | null;
  fairCents?: number | null;
  subtitle?: string;
}) {
  const edge = fairCents != null && yesCents != null ? yesCents - fairCents : null;
  const edgeColor = edge != null ? (edge > 2 ? P.greenText : edge < -2 ? P.redText : P.textMuted) : P.textMuted;

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
        alignItems: 'center',
        padding: '8px 12px',
        borderBottom: `1px solid ${P.cardBorder}`,
        fontSize: 13,
      }}
    >
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
      <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 600, color: edgeColor }}>
        {edge != null ? `${edge > 0 ? '+' : ''}${edge.toFixed(1)}%` : '--'}
      </div>
    </div>
  );
}

export function ExchangeGameClient({
  gameId,
  homeTeam,
  awayTeam,
  commenceTime,
  sportKey,
  platform,
  fairLines,
  history,
  contracts,
}: ExchangeGameClientProps) {
  const [activeMarket, setActiveMarket] = useState<'moneyline' | 'spread' | 'total'>('moneyline');

  const platformConfig = PLATFORM_CONFIG[platform] || PLATFORM_CONFIG.kalshi;

  const gameTime = commenceTime ? new Date(commenceTime) : null;
  const timeStr = gameTime
    ? gameTime.toLocaleString('en-US', {
        weekday: 'short', month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit',
      })
    : '';

  // Separate contracts by market type and exchange
  const platformContracts = contracts.filter(c => c.exchange === platform);
  const mlContracts = platformContracts.filter(c => c.market_type === 'moneyline');
  const spreadContracts = platformContracts.filter(c => c.market_type === 'spread');
  const totalContracts = platformContracts.filter(c => c.market_type === 'total');

  // Fair ML as cents
  const fairHomeCents = fairLines?.fair_ml_home != null
    ? Math.round(toProb(fairLines.fair_ml_home) * 100) : null;
  const fairAwayCents = fairLines?.fair_ml_away != null
    ? Math.round(toProb(fairLines.fair_ml_away) * 100) : null;

  const homeLast = homeTeam.toLowerCase().split(' ').pop()!;
  const awayLast = awayTeam.toLowerCase().split(' ').pop()!;

  // Match ML contracts to home/away
  const matchTeam = (sub: string) => {
    const s = sub.toLowerCase();
    if (s.includes(homeLast) || s.includes(homeTeam.toLowerCase())) return 'home';
    if (s.includes(awayLast) || s.includes(awayTeam.toLowerCase())) return 'away';
    return null;
  };

  const homeMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'home');
  const awayMl = mlContracts.find(c => matchTeam(c.subtitle || '') === 'away');

  const markets = [
    { key: 'moneyline' as const, label: 'Moneyline', count: mlContracts.length },
    { key: 'spread' as const, label: 'Spread', count: spreadContracts.length },
    { key: 'total' as const, label: 'Total', count: totalContracts.length },
  ];

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
          <ProbabilityChart
            history={history}
            homeTeam={homeTeam}
            awayTeam={awayTeam}
            fairLines={fairLines}
            platform={platform}
          />
        </div>
        {/* Legend */}
        <div style={{ padding: '8px 16px', borderTop: `1px solid ${P.cardBorder}`, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 16, height: 2, background: platformConfig.color, borderRadius: 1 }} />
            <span style={{ fontSize: 10, color: P.textSecondary }}>{homeTeam} ({platform})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 16, height: 2, background: '#ef4444', borderRadius: 1 }} />
            <span style={{ fontSize: 10, color: P.textSecondary }}>{awayTeam} ({platform})</span>
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
          <button
            key={m.key}
            onClick={() => setActiveMarket(m.key)}
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
        {/* Column Headers */}
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
              <ContractRow
                label={homeTeam}
                yesCents={homeMl.yes_price}
                noCents={homeMl.no_price}
                fairCents={fairHomeCents}
                subtitle="Win"
              />
            )}
            {awayMl && (
              <ContractRow
                label={awayTeam}
                yesCents={awayMl.yes_price}
                noCents={awayMl.no_price}
                fairCents={fairAwayCents}
                subtitle="Win"
              />
            )}
            {!homeMl && !awayMl && (
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
                .map((c, i) => (
                  <ContractRow
                    key={i}
                    label={c.subtitle || c.event_title}
                    yesCents={c.yes_price}
                    noCents={c.no_price}
                  />
                ))
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
                .sort((a, b) => Math.abs((a.yes_price ?? 50) - 50) - Math.abs((b.yes_price ?? 50) - 50))
                .map((c, i) => (
                  <ContractRow
                    key={i}
                    label={c.subtitle || c.event_title}
                    yesCents={c.yes_price}
                    noCents={c.no_price}
                  />
                ))
            ) : (
              <div style={{ padding: 24, textAlign: 'center', color: P.textMuted, fontSize: 13 }}>
                No total contracts available
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
