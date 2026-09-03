import {
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TICKS, WINDOW_HOURS_TOTAL, engagementAt } from "@/lib/tape";

type Props = { hours: number };

export function Gun({ hours }: Props) {
  const g = engagementAt(hours);

  return (
    <section className="rounded-xl bg-surface p-4 shadow-[var(--shadow-border)] sm:p-5">
      <header className="mb-4 max-w-3xl">
        <p className="text-xs uppercase tracking-[0.16em] text-rest">
          What the slope is saying
        </p>
        <h2 className="mt-1 font-display text-2xl leading-tight text-fg">
          {g.headline}
        </h2>
        <p className="mt-2 text-sm text-muted">{g.body}</p>
      </header>

      <div className="grid gap-3 sm:grid-cols-4">
        <Stat
          label="ALT tape since we sat"
          value={fmtDelta(g.altTapeSinceSit)}
          hint="last trade vs 58¢"
        />
        <Stat
          label="ALT bid changes"
          value={String(g.altBidChanges)}
          hint="both from cheap endings dying"
        />
        <Stat
          label="GAS tape since we sat"
          value={fmtDelta(g.gasTapeSinceSit)}
          hint="last trade vs 42¢"
        />
        <Stat
          label="Hours the ALT bid has sat"
          value={g.hoursHeld.toFixed(0)}
          hint={g.frozen ? "no reseat on the climb" : "not locked yet"}
        />
      </div>

      <div className="mt-5 h-56 w-full">
        <p className="mb-2 text-sm text-muted">
          One picture. ALT last trade rises. GAS last trade falls. The two
          dashed bids stay flat.
        </p>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={TICKS} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
            <XAxis
              dataKey="hours"
              type="number"
              domain={[0, WINDOW_HOURS_TOTAL]}
              ticks={[0, 17, 34, 51, 68]}
              tickFormatter={(v) => (v === 0 ? "opens" : v === 68 ? "bell" : `${v}h`)}
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
              contentStyle={{
                background: "var(--color-raised)",
                border: "1px solid var(--color-border)",
                borderRadius: 8,
                color: "var(--color-fg)",
                fontSize: 12,
              }}
              formatter={(value, name) => [`${value}¢`, String(name)]}
              labelFormatter={(l) => `${Number(l).toFixed(1)} hours in`}
            />
            <ReferenceLine
              x={hours}
              stroke="var(--color-accent)"
              strokeDasharray="3 4"
            />
            <Line
              type="monotone"
              dataKey="altLast"
              name="ALT last trade"
              stroke="var(--color-alt)"
              strokeWidth={2.6}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="gasLast"
              name="GAS last trade"
              stroke="var(--color-gas)"
              strokeWidth={2.6}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="altRest"
              name="ALT bid"
              stroke="var(--color-rest)"
              strokeWidth={2.4}
              strokeDasharray="7 5"
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="gasRest"
              name="GAS bid"
              stroke="var(--color-gas)"
              strokeWidth={2}
              strokeDasharray="2 5"
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

function fmtDelta(n: number) {
  if (n === 0) return "0¢";
  return `${n > 0 ? "+" : ""}${n}¢`;
}

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-md bg-raised p-3">
      <p className="text-xs text-subtle">{label}</p>
      <p className="mt-1 font-display text-2xl tabular-nums leading-none text-fg">
        {value}
      </p>
      <p className="mt-2 text-xs text-muted">{hint}</p>
    </div>
  );
}
