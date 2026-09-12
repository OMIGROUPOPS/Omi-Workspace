import { useEffect, useRef, useState } from "react";
import { SILENT, type Frame, type LoadedGame } from "@/lib/tune-tape";

// Canvas pixel placement only: the builder stores every gap, bar geometry and hover string.
export function OracleGap({ game, side, now, color }: {
  game: LoadedGame; side: string; now: Frame; color: string;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const audit = game.oracle, series = audit?.legs[side], summary = game.face.oracle?.legs[side];
  const progressIndex = now.pre_first_tick ? 3 : 2;
  useEffect(() => {
    const element = canvas.current;
    if (!element || !audit || !series) return;
    const draw = () => {
      const width = element.clientWidth, height = element.clientHeight, scale = window.devicePixelRatio;
      element.width = width * scale; element.height = height * scale;
      const ctx = element.getContext("2d"); if (!ctx) return;
      ctx.scale(scale, scale); ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = "#777777"; ctx.globalAlpha = 0.4;
      ctx.beginPath(); ctx.moveTo(36, height / 2); ctx.lineTo(width - 8, height / 2); ctx.stroke();
      ctx.globalAlpha = 0.8;
      audit.ticks.forEach((tick, i) => {
        const value = series.values[i];
        if (value[1] == null || value[2] == null) return;
        ctx.fillStyle = value[1] > 0 ? "#d0d0d0" : "#858585";
        const x = 36 + (width - 44) * tick[progressIndex];
        const next = audit.ticks[i + 1]?.[progressIndex] ?? tick[progressIndex];
        ctx.fillRect(x, 8 + (height - 16) * value[2], Math.max(1, (next - tick[progressIndex]) * (width - 44)), (height - 16) * (value[3] ?? 0));
      });
    };
    const observer = new ResizeObserver(draw); observer.observe(element); draw();
    return () => observer.disconnect();
  }, [audit, series, progressIndex]);
  const pick = (x: number) => {
    if (!audit || !canvas.current) return;
    const progress = (x - canvas.current.getBoundingClientRect().left - 36) / (canvas.current.clientWidth - 44);
    let lo = 0, hi = audit.ticks.length;
    while (lo < hi) { const mid = (lo + hi) >>> 1; if (audit.ticks[mid][progressIndex] <= progress) lo = mid + 1; else hi = mid; }
    const i = Math.max(0, lo - 1);
    setHover(audit.ticks[i][1] >= now.minutesToBell ? i : null);
  };
  const profile = hover != null && series ? series.profiles[series.values[hover][0]] : null;
  return <div className="mt-2" aria-label={`${side} sentence gap strip`}>
    <p className="text-xs text-muted">Sentence gap · above zero: too high · below zero: too low · amber: fill</p>
    {!audit || !series ? <p className="text-xs text-muted">{game.oracle_status ?? SILENT}</p> :
      <div className="relative h-20" onMouseLeave={() => setHover(null)}>
        <canvas ref={canvas} className="h-full w-full" style={{ clipPath: `inset(0 calc(8px + (100% - 44px) * ${now.plot_remaining}) 0 0)` }} onMouseMove={e => pick(e.clientX)} aria-label={`${side} signed Q minus perfect sentence; hover to inspect each receipt`} />
        <span className="pointer-events-none absolute left-0 top-1/2 -translate-y-1/2 text-xs text-muted">0¢</span>
        {summary?.fill_points.filter(f => f.y != null && audit.ticks[f.index]?.[1] >= now.minutesToBell).map(f =>
          <button key={f.receipt} title={f.label} aria-label={f.label}
            onMouseEnter={() => setHover(f.index)} onFocus={() => setHover(f.index)} onBlur={() => setHover(null)}
            className="absolute -translate-x-1/2 -translate-y-1/2 text-sm" style={{ color,
              left: `calc(36px + (100% - 44px) * ${now.pre_first_tick ? f.inspection_progress : f.progress})`,
              top: `calc(8px + (100% - 16px) * ${f.y})`, width:6,height:6,backgroundColor:color,borderRadius:'50%' }} />)}
        {profile && hover != null ? <div role="tooltip" className="pointer-events-none absolute bottom-full left-10 z-30 rounded border border-border bg-raised p-2 text-xs text-fg shadow-lg">
          <p>{audit.ticks[hover][5]}</p>{profile.lines.map((line, i) => <p key={i}>{line}</p>)}
        </div> : null}
      </div>}
  </div>;
}
