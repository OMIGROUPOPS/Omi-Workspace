import {
  Area,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { visibleTicks, WINDOW_HOURS_TOTAL } from "@/lib/tape";

type Props = {
  hours: number;
  side: "ALT" | "GAS";
};

function ChartTip({
  active,
  payload,
  label,
  side,
}: {
  active?: boolean;
  payload?: Array<{ dataKey?: string; value?: number | [number, number] }>;
  label?: number;
  side: "ALT" | "GAS";
}) {
  if (!active || !payload?.length) return null;
  const row = Object.fromEntries(
    payload.map((p) => [String(p.dataKey), p.value]),
  );
  const prefix = side === "ALT" ? "alt" : "gas";
  const band = row[`${prefix}LookalikeBand`];
  return (
    <div className="rounded-md border border-border bg-raised px-3 py-2 text-xs text-fg">
      <p className="mb-1 text-muted">{Number(label).toFixed(1)}h into the window</p>
      <p>Best bid {row[`${prefix}Bid`]}¢</p>
      <p>Best ask {row[`${prefix}Ask`]}¢</p>
      <p>Last trade {row[`${prefix}Last`]}¢</p>
      <p>
        Our bid{" "}
        {row[`${prefix}Rest`] != null ? `${row[`${prefix}Rest`]}¢` : "none yet"}
      </p>
      {Array.isArray(band) ? <p>Lookalikes 25–75% {band[0]}–{band[1]}¢</p> : null}
      {row[`${prefix}LookalikeQ10`] != null ? <p>Lookalike q10 {row[`${prefix}LookalikeQ10`]}¢</p> : null}
    </div>
  );
}

export function AtlasChart({ hours, side }: Props) {
  const data = visibleTicks(hours);
  const isAlt = side === "ALT";
  const lastKey = isAlt ? "altLast" : "gasLast";
  const bidKey = isAlt ? "altBid" : "gasBid";
  const askKey = isAlt ? "altAsk" : "gasAsk";
  const restKey = isAlt ? "altRest" : "gasRest";
  const bandKey = isAlt ? "altLookalikeBand" : "gasLookalikeBand";
  const q10Key = isAlt ? "altLookalikeQ10" : "gasLookalikeQ10";
  const stroke = isAlt ? "var(--color-alt)" : "var(--color-gas)";
  const now = data[data.length - 1];
  const last = now ? (isAlt ? now.altLast : now.gasLast) : null;
  const rest = now ? (isAlt ? now.altRest : now.gasRest) : null;
  const name = isAlt ? "ALT — this player" : "GAS — the other player";

  return (
    <section className="px-4 py-5 sm:px-5">
      <header className="mb-3 flex items-end justify-between gap-3">
        <div>
          <h2
            className="font-display text-2xl leading-none"
            style={{ color: stroke }}
          >
            {name}
          </h2>
          <p className="mt-2 text-sm text-muted">
            Grey = best bid and best ask. Bright = last trade. Dashed = our bid. Shade = where lookalikes went from here (25–75%).
          </p>
        </div>
        <div className="text-right tabular-nums">
          <p className="font-display text-3xl leading-none">{last}¢</p>
          <p className="mt-1 text-xs text-muted">
            our bid {rest == null ? "—" : `${rest}¢`}
          </p>
        </div>
      </header>
      <div className="h-72 w-full sm:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="var(--color-border)" vertical={false} />
            <XAxis
              dataKey="hours"
              type="number"
              domain={[0, WINDOW_HOURS_TOTAL]}
              ticks={[0, 12, 24, 36, 48, 60, 68]}
              tickFormatter={(v) => `${v}h`}
              stroke="var(--color-subtle)"
              tick={{ fill: "var(--color-subtle)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={["dataMin - 2", "dataMax + 2"]}
              ticks={[30, 45, 60, 75]}
              stroke="var(--color-subtle)"
              tick={{ fill: "var(--color-subtle)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}¢`}
              width={36}
            />
            <Tooltip
              content={<ChartTip side={side} />}
              cursor={{ stroke: "var(--color-border-strong)" }}
            />
            <ReferenceLine x={hours} stroke="var(--color-muted)" strokeDasharray="2 4" />
            <Area
              type="stepAfter"
              dataKey={bandKey}
              name="where lookalikes went from here (25–75%)"
              stroke="none"
              fill={stroke}
              fillOpacity={0.12}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="stepAfter"
              dataKey={q10Key}
              name="Lookalike q10"
              stroke={stroke}
              strokeWidth={1}
              strokeOpacity={0.35}
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey={bidKey}
              name="Best bid"
              stroke="var(--color-muted)"
              strokeWidth={1.4}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey={askKey}
              name="Best ask"
              stroke="var(--color-muted)"
              strokeWidth={1.4}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey={lastKey}
              name="Last trade"
              stroke={stroke}
              strokeWidth={2.4}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="stepAfter"
              dataKey={restKey}
              name="Our bid"
              stroke={stroke}
              strokeWidth={2.4}
              strokeDasharray="6 5"
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
