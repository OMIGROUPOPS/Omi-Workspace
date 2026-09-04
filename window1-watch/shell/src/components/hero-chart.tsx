import {
  Area,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { visibleTicks, WINDOW_HOURS_TOTAL } from "@/lib/tape";

type Props = { hours: number };

export function HeroChart({ hours }: Props) {
  const data = visibleTicks(hours);

  return (
    <div className="h-[340px] w-full sm:h-[420px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 12, left: 4, bottom: 4 }}>
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
            ticks={[30, 40, 50, 60, 70]}
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
            labelFormatter={(l) => `${Number(l).toFixed(1)}h in`}
          />
          <ReferenceLine
            x={hours}
            stroke="var(--color-muted)"
            strokeDasharray="2 4"
          />
          <Area
            type="stepAfter"
            dataKey="altLookalikeBand"
            name="ALT where lookalikes went from here (25–75%)"
            stroke="none"
            fill="var(--color-alt)"
            fillOpacity={0.10}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Area
            type="stepAfter"
            dataKey="gasLookalikeBand"
            name="GAS where lookalikes went from here (25–75%)"
            stroke="none"
            fill="var(--color-gas)"
            fillOpacity={0.10}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey="altLookalikeQ10"
            name="ALT lookalike q10"
            stroke="var(--color-alt)"
            strokeWidth={1}
            strokeOpacity={0.35}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey="gasLookalikeQ10"
            name="GAS lookalike q10"
            stroke="var(--color-gas)"
            strokeWidth={1}
            strokeOpacity={0.35}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="altLast"
            name="ALT last"
            stroke="var(--color-alt)"
            strokeWidth={2.2}
            dot={(props) => {
              if (props.index !== data.length - 1) {
                return <g key={`alt-empty-${props.index}`} />;
              }
              return (
                <circle
                  key={`alt-${props.index}`}
                  cx={props.cx}
                  cy={props.cy}
                  r={3.5}
                  fill="var(--color-alt)"
                />
              );
            }}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="gasLast"
            name="GAS last"
            stroke="var(--color-gas)"
            strokeWidth={2.2}
            dot={(props) => {
              if (props.index !== data.length - 1) {
                return <g key={`gas-empty-${props.index}`} />;
              }
              return (
                <circle
                  key={`gas-${props.index}`}
                  cx={props.cx}
                  cy={props.cy}
                  r={3.5}
                  fill="var(--color-gas)"
                />
              );
            }}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey="altRest"
            name="ALT rest"
            stroke="var(--color-alt)"
            strokeWidth={1.8}
            strokeDasharray="6 5"
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="stepAfter"
            dataKey="gasRest"
            name="GAS rest"
            stroke="var(--color-gas)"
            strokeWidth={1.8}
            strokeDasharray="2 5"
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
