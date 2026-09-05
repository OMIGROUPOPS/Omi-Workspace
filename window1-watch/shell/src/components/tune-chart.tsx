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
import { BidActionMarkers } from "./bid-action-markers";
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
      {(row.hover_lines ?? [SILENT]).map((line, i) => (
        <p key={i}>{line}</p>
      ))}
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
  const recordedFloor = game.face.truth?.legs[side];
  const rulerMarker = recordedFloor?.markers[now.pre_first_tick ? "inspection" : "play"];
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
          {recordedFloor?.status === "OK" && recordedFloor.floor_cents != null ? (
            <ReferenceLine
              className="recorded-floor-line"
              y={recordedFloor.floor_cents}
              stroke={stroke}
              strokeOpacity={0.5}
              strokeWidth={1.5}
            />
          ) : null}
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
          <p className="mt-1 text-xs text-muted">{game.face.render.marker_legend}</p>
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
        {rulerMarker?.price != null ? (
          <span
            role="img"
            aria-label={rulerMarker.hover_note}
            title={rulerMarker.hover_note}
            data-boundary={rulerMarker.boundary}
            className="recorded-floor-flag pointer-events-auto absolute z-10 -translate-x-1/2 -translate-y-full rounded bg-bg/90 px-1 text-lg leading-none"
            style={{
              color: stroke,
              left: `calc(36px + (100% - 44px) * ${rulerMarker.display_progress})`,
              top: `calc(16px + (100% - 46px) * ${rulerMarker.price})`,
            }}
          >
            {rulerMarker.glyph}
          </span>
        ) : null}
        {rulerMarker?.price != null ? (
          <p
            className="recorded-floor-label pointer-events-none absolute left-[40px] z-10 translate-y-[3px] rounded bg-bg/85 px-1 text-[11px]"
            style={{ color: stroke, top: `calc(16px + (100% - 46px) * ${rulerMarker.price})` }}
          >
            {recordedFloor?.chart_label}
          </p>
        ) : null}
        <div className="tune-playhead pointer-events-none absolute bottom-[30px] top-4 border-l border-dashed border-muted" />
        <BidActionMarkers
          actions={game.face.render.bid_actions ?? []}
          now={now}
          side={side}
          color={stroke}
          onReceipt={onReceipt}
        />
      </div>
      {atBell && miss ? <p className="text-xs text-muted">{miss.label}</p> : null}
    </section>
  );
});
