// Grok's atlas tokens, fonts, line weights and layout; only the data/clock are generalized.
import { memo, useMemo, useRef, type CSSProperties, type RefObject } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { SILENT, type LoadedGame, type Frame } from "@/lib/tune-tape";
type Props = { game: LoadedGame; frame: number; side: string; onReceipt: (index: number) => void };
const price = (v: unknown) => (v == null ? SILENT : `${v}¢`);
function ChartTip({
  active,
  payload,
  current,
}: {
  active?: boolean;
  payload?: { payload: Frame }[];
  current: RefObject<Frame>;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  if (row.minutesToBell < current.current.minutesToBell) return null;
  if (
    row.receipt_index != null &&
    current.current.receipt_index != null &&
    row.receipt_index > current.current.receipt_index
  )
    return null;
  return (
    <div className="rounded-md border border-border bg-raised px-3 py-2 text-xs text-fg">
      <p>{row.clock_label}</p>
      <p>
        First book {price(row.firstBid)} / {price(row.firstAsk)} · last {price(row.firstLast)}
      </p>
      <p>
        Second book {price(row.secondBid)} / {price(row.secondAsk)} · last {price(row.secondLast)}
      </p>
    </div>
  );
}
export const TuneChart = memo(function TuneChart({ game, frame, side, onReceipt }: Props) {
  const first = side === game.face.legs[0],
    prefix = first ? "first" : "second",
    stroke = first ? "var(--color-alt)" : "var(--color-gas)";
  const now = game.frames[frame],
    data = game.frames.slice(now.pre_first_tick ? 0 : game.face.render.play_start_frame),
    axis = now.pre_first_tick ? game.face.render.inspection_axis : game.face.render.axis;
  const last = first ? now.firstLast : now.secondLast,
    rest = first ? now.firstRest : now.secondRest,
    atBell = frame === game.frames.length - 1,
    miss = game.face.render.misses.find((m) => m.leg === side);
  const current = useRef(now);
  current.current = now;
  // The path is static. A source-clock clip reveals only the causal portion, while
  // hover/click reject unrevealed points. No per-receipt Recharts reconciliation.
  const plot = useMemo(
    () => (
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 16, right: 8, left: 0, bottom: 0 }}
          onClick={(state) => {
            const r = state?.activePayload?.[0]?.payload as Frame | undefined;
            if (
              r?.receipt_index != null &&
              r.minutesToBell >= current.current.minutesToBell &&
              current.current.receipt_index != null &&
              r.receipt_index <= current.current.receipt_index
            )
              onReceipt(r.receipt_index);
          }}
        >
          <CartesianGrid stroke="var(--color-border)" vertical={false} />
          <XAxis
            dataKey="minutesToBell"
            type="number"
            domain={[axis.end_minutes_to_bell, axis.start_minutes_to_bell]}
            reversed
            ticks={axis.ticks}
            stroke="var(--color-subtle)"
            tick={{ fill: "var(--color-subtle)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={22}
          />
          <YAxis
            domain={axis.price_domain ?? undefined}
            ticks={axis.price_ticks}
            stroke="var(--color-subtle)"
            tick={{ fill: "var(--color-subtle)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}¢`}
            width={36}
          />
          <Tooltip content={<ChartTip current={current} />} />
          {game.face.render.checkpoints.map((c) => (
            <ReferenceLine
              key={c.minutesToBell}
              x={c.minutesToBell}
              stroke="var(--color-border)"
              strokeDasharray="2 6"
            />
          ))}
          <Area
            type="stepAfter"
            dataKey={`${prefix}Band`}
            stroke="none"
            fill={stroke}
            fillOpacity={0.12}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey={`${prefix}Q10`}
            stroke={stroke}
            strokeWidth={1}
            strokeOpacity={0.35}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey={`${prefix}Bid`}
            stroke="var(--color-muted)"
            strokeWidth={1.4}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey={`${prefix}Ask`}
            stroke="var(--color-muted)"
            strokeWidth={1.4}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey={`${prefix}Last`}
            stroke={stroke}
            strokeWidth={2.4}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            className="rest-history"
            type="stepAfter"
            dataKey={`${prefix}Rest`}
            stroke={stroke}
            strokeWidth={2.4}
            strokeDasharray="6 5"
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    ),
    [game, side, now.pre_first_tick, onReceipt],
  );
  return (
    <section className="px-4 py-5 sm:px-5">
      <header className="mb-3 flex items-end justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl leading-none" style={{ color: stroke }}>
            {side}
          </h2>
          <p className="mt-2 text-xs text-muted">
            Grey = book. Bright = last trade. Dashed = our bid. Shade = where lookalikes went from
            here (25–75%).
          </p>
        </div>
        <div className="text-right tabular-nums">
          <p className="font-display text-3xl leading-none">{price(last)}</p>
          <p className="mt-1 text-xs text-muted">our bid {rest == null ? "none" : price(rest)}</p>
        </div>
      </header>
      <div
        className="tune-history relative h-64 w-full sm:h-72"
        data-rest-miss={atBell && Boolean(miss)}
        style={
          {
            "--replay-remaining": now.plot_remaining,
            "--replay-progress": now.plot_progress,
          } as CSSProperties
        }
      >
        {plot}
        <div className="tune-playhead pointer-events-none absolute bottom-[30px] top-4 border-l border-dashed border-muted" />
        {game.face.render.fill_events
          .filter(
            (f) =>
              f.leg === side && now.receipt_index != null && f.receipt_index <= now.receipt_index,
          )
          .map((f) => {
            const x = now.pre_first_tick ? f.inspection_progress : f.plot_progress;
            const y = now.pre_first_tick ? f.inspection_price : f.plot_price;
            if (y == null || x < 0 || x > 1) return null;
            return (
              <button
                key={f.receipt_index}
                aria-label={f.label}
                title={f.label}
                onClick={() => onReceipt(f.receipt_index)}
                className="fill-burst absolute z-10 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-fg"
                style={{
                  background: stroke,
                  left: `calc(36px + (100% - 44px) * ${x})`,
                  top: `calc(16px + (100% - 46px) * ${y})`,
                }}
              >
                <span
                  className="absolute bottom-4 left-1/2 -translate-x-1/2 whitespace-nowrap text-[11px]"
                  style={{ color: stroke }}
                >
                  {f.label}
                </span>
              </button>
            );
          })}
      </div>
      {atBell && miss ? <p className="text-xs text-muted">{miss.label}</p> : null}
    </section>
  );
});
