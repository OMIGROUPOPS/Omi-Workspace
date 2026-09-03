import { beatAtHours, engagementAt, tickNear, type Beat } from "@/lib/tape";
import { cn } from "@/lib/utils";

type Props = { hours: number };

function WatchDial({ beat, hours }: { beat: Beat; hours: number }) {
  const tick = tickNear(hours);
  const rest = tick.altRest;
  const frozen = engagementAt(hours).frozen;
  const angle = rest == null ? -90 : -90 + rest * 2.7;
  const timeFrac = hours / 68;
  const r = 54;
  const cx = 70;
  const cy = 70;
  const rad = (deg: number) => (deg * Math.PI) / 180;
  const hx = cx + Math.cos(rad(angle)) * 38;
  const hy = cy + Math.sin(rad(angle)) * 38;
  const arc = 2 * Math.PI * r * (1 - timeFrac);

  return (
    <svg viewBox="0 0 140 148" className="h-full w-full" aria-hidden>
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="var(--color-raised)"
        stroke="var(--color-border-strong)"
      />
      <circle
        cx={cx}
        cy={cy}
        r={r - 6}
        fill="none"
        stroke="var(--color-border)"
        strokeWidth="8"
      />
      <circle
        cx={cx}
        cy={cy}
        r={r - 6}
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth="8"
        strokeDasharray={`${2 * Math.PI * (r - 6)}`}
        strokeDashoffset={arc}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
      />
      {[0, 25, 50, 75, 100].map((c) => {
        const a = rad(-90 + c * 2.7);
        const x1 = cx + Math.cos(a) * 42;
        const y1 = cy + Math.sin(a) * 42;
        const x2 = cx + Math.cos(a) * 48;
        const y2 = cy + Math.sin(a) * 48;
        return (
          <line
            key={c}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="var(--color-subtle)"
            strokeWidth="1.4"
          />
        );
      })}
      <line
        x1={cx}
        y1={cy}
        x2={hx}
        y2={hy}
        stroke="var(--color-rest)"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <circle cx={cx} cy={cy} r="4" fill="var(--color-fg)" />
      <text
        x={cx}
        y={136}
        textAnchor="middle"
        fill="var(--color-muted)"
        fontSize="11"
        fontFamily="Figtree, sans-serif"
      >
        {rest == null ? "no bid yet" : frozen ? `stuck ${rest}¢` : `bid ${rest}¢`}
      </text>
      <text
        x={cx}
        y={12}
        textAnchor="middle"
        fill="var(--color-subtle)"
        fontSize="10"
        fontFamily="Figtree, sans-serif"
      >
        {beat.hand === "idle" ? "hand still" : beat.hand}
      </text>
    </svg>
  );
}

function Figure({ beat }: { beat: Beat }) {
  const brainFill =
    beat.brain === "blank"
      ? "var(--color-raised)"
      : beat.brain === "guess"
        ? "var(--color-subtle)"
        : "var(--color-accent)";
  const heartClass =
    beat.heart === "hard" || beat.heart === "steady" ? "heart-beat" : "";
  const organFill = beat.pileAlive
    ? "var(--color-good)"
    : "var(--color-surface)";
  const organStroke = beat.pileAlive
    ? "var(--color-good)"
    : "var(--color-rest)";

  return (
    <svg viewBox="0 0 240 300" className="mx-auto h-full max-h-80 w-full">
      <text x="120" y="16" textAnchor="middle" fontSize="11" fill="var(--color-muted)">
        brain
      </text>
      <path
        d="M120 28 C120 28 132 46 138 68 C142 86 140 100 120 110 C100 100 98 86 102 68 C108 46 120 28 120 28"
        fill={brainFill}
        stroke="var(--color-fg)"
        strokeWidth="2"
      />
      <ellipse
        cx="120"
        cy="92"
        rx="32"
        ry="38"
        fill="none"
        stroke="var(--color-fg)"
        strokeWidth="2.2"
      />
      <ellipse cx="108" cy="88" rx="5" ry="3.5" fill="var(--color-fg)" />
      <ellipse cx="132" cy="88" rx="5" ry="3.5" fill="var(--color-fg)" />
      <path
        d="M120 130 v22"
        stroke="var(--color-fg)"
        strokeWidth="2.4"
        className={beat.heart !== "still" ? "blood-run" : undefined}
      />
      <path
        d="M92 164 C72 184 64 210 72 236"
        fill="none"
        stroke="var(--color-blood)"
        strokeWidth="2.2"
        className={
          beat.hand === "posting" || beat.hand === "pulling"
            ? "blood-run"
            : undefined
        }
      />
      <path
        d="M148 164 C168 184 176 210 168 236"
        fill="none"
        stroke="var(--color-blood)"
        strokeWidth="2.2"
        className={
          beat.hand === "posting" || beat.hand === "pulling"
            ? "blood-run"
            : undefined
        }
      />
      <rect
        x="94"
        y="148"
        width="52"
        height="70"
        rx="18"
        fill="var(--color-bg)"
        stroke="var(--color-fg)"
        strokeWidth="2"
      />
      <g className={heartClass}>
        <path
          d="M120 184 c-1-10-14-10-14 0 c0 10 14 18 14 18 c0 0 14-8 14-18 c0-10-13-10-14 0"
          fill="var(--color-rest)"
        />
      </g>
      <text x="120" y="176" textAnchor="middle" fontSize="9" fill="var(--color-muted)">
        heart
      </text>
      <circle cx="104" cy="214" r="7" fill={organFill} stroke={organStroke} strokeWidth="2" />
      <circle cx="120" cy="222" r="7" fill={organFill} stroke={organStroke} strokeWidth="2" />
      <circle cx="136" cy="214" r="7" fill={organFill} stroke={organStroke} strokeWidth="2" />
      <path d="M96 160 L52 192 L40 250" fill="none" stroke="var(--color-fg)" strokeWidth="2.2" />
      <path d="M144 160 L188 192 L200 250" fill="none" stroke="var(--color-fg)" strokeWidth="2.2" />
      <circle
        cx="40"
        cy="258"
        r="14"
        fill={beat.hand === "idle" ? "var(--color-surface)" : "var(--color-rest)"}
        stroke="var(--color-fg)"
        strokeWidth="2"
      />
      <circle
        cx="200"
        cy="258"
        r="14"
        fill={beat.gasRest == null ? "var(--color-surface)" : "var(--color-gas)"}
        stroke="var(--color-fg)"
        strokeWidth="2"
      />
      <text x="40" y="262" textAnchor="middle" fontSize="10" fill="var(--color-fg)">
        {beat.altRest ?? "—"}
      </text>
      <text x="200" y="262" textAnchor="middle" fontSize="10" fill="var(--color-fg)">
        {beat.gasRest ?? "—"}
      </text>
      <text x="40" y="286" textAnchor="middle" fontSize="10" fill="var(--color-muted)">
        ALT hand
      </text>
      <text x="200" y="286" textAnchor="middle" fontSize="10" fill="var(--color-muted)">
        GAS hand
      </text>
      <text x="120" y="248" textAnchor="middle" fontSize="10" fill="var(--color-muted)">
        leftover endings
      </text>
    </svg>
  );
}

const LAYERS = [
  { id: "macro", label: "Big picture", hint: "the whole match shape" },
  { id: "micro", label: "Leftover endings", hint: "what can still happen" },
  { id: "print", label: "Last print", hint: "what just traded" },
  { id: "decide", label: "Decision", hint: "post, pull, or hold" },
  { id: "hand", label: "The bid", hint: "posts, pulls — or freezes" },
];

function layerIndex(beat: Beat) {
  if (beat.hand === "posting" || beat.hand === "pulling") return 4;
  if (beat.brain === "blank" && beat.hand === "holding") return 4;
  if (beat.brain === "writing") return 3;
  if (!beat.pileAlive) return 1;
  if (beat.brain === "guess") return 0;
  return 2;
}

export function OsBody({ hours }: Props) {
  const beat = beatAtHours(hours);
  const active = layerIndex(beat);

  return (
    <section className="rounded-md border border-border p-4 sm:p-5">
      <header className="mb-4 max-w-3xl">
        <h2 className="font-display text-2xl text-fg">How the OS feels</h2>
        <p className="mt-2 text-sm text-muted">
          Brain writes a sentence. The bid is that sentence as an order. If
          the sentence does not change, the bid must not move. Leftover
          endings are the futures still legal. The hands are ALT and GAS
          rests.
        </p>
      </header>
      <div className="grid items-stretch gap-4 lg:grid-cols-[160px_1fr_200px]">
        <div className="rounded-lg bg-raised p-2">
          <WatchDial beat={beat} hours={hours} />
        </div>
        <div className="rounded-lg bg-raised px-2 pt-2">
          <Figure beat={beat} />
        </div>
        <ol className="flex flex-col justify-center gap-2">
          {LAYERS.map((layer, i) => (
            <li
              key={layer.id}
              className={cn(
                "rounded-md border px-3 py-2 transition-colors duration-200",
                i === active
                  ? "border-border-strong bg-raised text-fg"
                  : "border-transparent text-muted",
              )}
              style={{ marginLeft: `${i * 10}px` }}
            >
              <p className="text-sm font-medium">{layer.label}</p>
              <p className="text-xs text-subtle">{layer.hint}</p>
            </li>
          ))}
        </ol>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Fact
          label="Brain — the sentence"
          hint="What the OS believes should happen. Not a quote."
          value={beat.sentence}
        />
        <Fact
          label="Why the bid moved — or didn't"
          hint="The reason the hand posted, pulled, or froze."
          value={beat.whyTheBidMoved}
        />
        <Fact
          label="What it pointed at"
          hint="The evidence it cited: a library, a leftover pile, or a print. Not the live bid/ask."
          value={beat.cited}
        />
      </div>
    </section>
  );
}

function Fact({
  label,
  hint,
  value,
}: {
  label: string;
  hint: string;
  value: string;
}) {
  return (
    <div className="rounded-md bg-raised p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-subtle">{label}</p>
      <p className="mt-1 text-xs text-muted">{hint}</p>
      <p className="mt-2 text-sm text-fg">{value}</p>
    </div>
  );
}
