import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AtlasChart } from "@/components/atlas-chart";
import { OsBody } from "@/components/os-body";
import { Playback } from "@/components/playback";
import {
  PROVENANCE,
  WINDOW_HOURS_TOTAL,
  beatAtHours,
  engagementAt,
  hoursRemaining,
  isReady,
  loadTape,
} from "@/lib/tape";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  const [hours, setHours] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [ready, setReady] = useState(isReady());
  const [loadError, setLoadError] = useState<string | null>(null);

  // Data is the OS: everything below reads data/altgas.face.json (see FIELDS.md). Nothing renders until it is loaded.
  useEffect(() => {
    if (ready) return;
    loadTape()
      .then(() => setReady(true))
      .catch((e) => setLoadError(String(e)));
  }, [ready]);

  useEffect(() => {
    if (!playing) return;
    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setPlaying(false);
      return;
    }
    const id = window.setInterval(() => {
      setHours((h) => {
        const next = h + 0.5;
        if (next >= WINDOW_HOURS_TOTAL) {
          setPlaying(false);
          return WINDOW_HOURS_TOTAL;
        }
        return next;
      });
    }, 140);
    return () => window.clearInterval(id);
  }, [playing]);

  if (!ready) {
    return (
      <main className="min-h-dvh bg-bg px-4 py-6 text-fg sm:px-8 sm:py-10">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">
          {loadError ? `STORE SILENT — ${loadError}` : "Window-1 Watch · loading data/altgas.face.json"}
        </p>
      </main>
    );
  }
  const beat = beatAtHours(hours);
  const gun = engagementAt(hours);
  const left = hoursRemaining(hours);

  return (
    <main className="min-h-dvh bg-bg px-4 py-6 text-fg sm:px-8 sm:py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-muted">
              Window-1 Watch · {PROVENANCE?.event_id ?? "STORE SILENT"} · OS {PROVENANCE?.os_sha256?.slice(0, 8) ?? "STORE SILENT"} · trace {PROVENANCE?.trace_sha256?.slice(0, 8) ?? "STORE SILENT"}
            </p>
            <h1 className="mt-2 font-display text-5xl leading-none tracking-tight sm:text-6xl">
              <span className="text-alt">ALT</span>
              <span className="text-fg"> vs </span>
              <span className="text-gas">GAS</span>
            </h1>
          </div>
          <p className="font-display text-3xl tabular-nums text-fg sm:text-4xl">
            {left.toFixed(1)}h
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1fr_240px] lg:items-end">
          <h2 className="font-display text-4xl leading-[1.05] tracking-tight sm:text-5xl">
            {gun.headline}
          </h2>
          <div className="border-l border-border pl-4 text-sm">
            <p className="text-xs uppercase tracking-[0.16em] text-muted">
              {beat.title} · {beat.hours}h
            </p>
            <p className="mt-2 text-muted">{beat.sentence}</p>
          </div>
        </div>

        <section className="overflow-hidden rounded-md border border-border">
          <Playback
            hours={hours}
            playing={playing}
            onHours={setHours}
            onPlaying={setPlaying}
          />
          <div className="flex flex-wrap gap-x-5 gap-y-2 border-t border-border px-4 pt-4 text-xs text-muted">
            <Legend color="var(--color-muted)" label="Best bid / best ask" />
            <Legend color="var(--color-alt)" label="ALT last trade" thick />
            <Legend color="var(--color-gas)" label="GAS last trade" thick />
            <Legend color="var(--color-alt)" label="Our bid" dashed />
            <Legend color="var(--color-muted)" label="where lookalikes went from here (25–75%)" band />
          </div>
          <AtlasChart hours={hours} side="ALT" />
          <div className="border-t border-border">
            <AtlasChart hours={hours} side="GAS" />
          </div>
        </section>

        <OsBody hours={hours} />
      </div>
    </main>
  );
}

function Legend({
  color,
  label,
  dashed,
  thick,
  band,
}: {
  color: string;
  label: string;
  dashed?: boolean;
  thick?: boolean;
  band?: boolean;
}) {
  return (
    <span className="inline-flex items-center gap-2">
      <svg width="22" height="8" aria-hidden>
        {band ? <rect x="0" y="1" width="22" height="6" fill={color} opacity="0.22" /> : null}
        <line
          x1="0"
          y1="4"
          x2="22"
          y2="4"
          stroke={color}
          strokeWidth={band ? 0 : thick ? 3 : 1.6}
          strokeDasharray={dashed ? "4 3" : undefined}
        />
      </svg>
      {label}
    </span>
  );
}
