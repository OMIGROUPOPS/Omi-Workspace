import { useCallback, useEffect, useState } from "react";
import { loadGameIndex, loadTuneGame } from "@/lib/tape";
import { frameForReceipt, SILENT, type Game, type LoadedGame } from "@/lib/tune-tape";
import { TuneChart } from "./tune-chart";
import { TunePlayback } from "./tune-playback";
import { TuneHud, TuneScene } from "./tune-scene";
import { ReceiptInspector } from "./receipt-inspector";
import { TuneReceipts } from "./tune-receipts";
import "../tune-motion.css";
export function TuneTest() {
  const [games, setGames] = useState<Game[]>([]),
    [event, setEvent] = useState<string | null>(null),
    [game, setGame] = useState<LoadedGame | null>(null);
  const [error, setError] = useState<string | null>(null),
    [frame, setFrame] = useState(0),
    [playing, setPlaying] = useState(false),
    [inspected, setInspected] = useState<number | null>(null),
    [selectedReceipt, setSelectedReceipt] = useState<number | null>(null);
  useEffect(() => {
    const c = new AbortController();
    loadGameIndex(c.signal)
      .then((index) => {
        setGames(index.games);
        setEvent(
          new URLSearchParams(window.location.search).get("event") ??
            index.games.find((g) => g.version === 2)?.event ??
            null,
        );
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(String(e));
      });
    return () => c.abort();
  }, []);
  useEffect(() => {
    if (!event || !games.length) return;
    const c = new AbortController();
    setGame(null);
    setPlaying(false);
    setInspected(null);
    setError(null);
    const entry = games.find((g) => g.event === event);
    if (!entry) {
      setError(`Unknown event: ${event}`);
      return;
    }
    loadTuneGame(entry.url, c.signal)
      .then((loaded) => {
        setGame(loaded);
        const gate = Number(new URLSearchParams(window.location.search).get("gate"));
        setFrame(
          loaded.face.render.checkpoints.find((p) => p.minutesToBell === gate)?.frame ??
            loaded.face.render.play_start_frame,
        );
        const url = new URL(window.location.href);
        url.searchParams.set("event", event);
        window.history.replaceState(null, "", url);
        (window as unknown as { TUNE_DATA: LoadedGame }).TUNE_DATA = loaded;
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(String(e));
      });
    return () => c.abort();
  }, [event, games]);
  useEffect(() => {
    if (!playing || !game) return;
    const timer = window.setTimeout(() => {
      const index = selectedReceipt ?? game.frames[frame]?.receipt_index;
      const next = game.face.os.find((r) => index == null || r.index > index);
      if (next) {
        setFrame(frameForReceipt(game.frames, next));
        setSelectedReceipt(next.index);
      } else {
        setPlaying(false);
        setFrame(game.frames.length - 1);
      }
    }, 700);
    return () => clearTimeout(timer);
  }, [playing, game, frame, selectedReceipt]);
  const inspect = useCallback((index: number) => {
      setInspected(index);
      setPlaying(false);
    }, []),
    closeInspector = useCallback(() => setInspected(null), []);
  const selectFrame = useCallback((index: number) => {
    setFrame(index);
    setSelectedReceipt(null);
    setInspected(null);
  }, []);
  useEffect(() => setSelectedReceipt(null), [event]);
  const now = game?.frames[frame],
    receiptIndex = selectedReceipt ?? now?.receipt_index ?? null,
    receipt = game && receiptIndex != null ? game.face.os[receiptIndex] : null;
  const checkpoint = game && now ? game.face.render.checkpoints[now.checkpoint_index] : null;
  const exactCheckpoint = checkpoint?.frame === frame ? checkpoint : null;
  return (
    <main className="min-h-dvh bg-bg px-4 py-6 text-fg sm:px-8 sm:py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-5">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-muted">
              Window-1 Watch · TUNE TEST
            </p>
            <h1 className="mt-2 font-display text-5xl leading-none tracking-tight sm:text-6xl">
              <span className="text-alt">{game?.face.legs[0] ?? SILENT}</span>
              <span> vs </span>
              <span className="text-gas">{game?.face.legs[1] ?? SILENT}</span>
            </h1>
          </div>
          <div>
            <label
              className="block text-xs uppercase tracking-[0.14em] text-muted"
              htmlFor="load-game"
            >
              Load game
            </label>
            <select
              id="load-game"
              value={event ?? ""}
              onChange={(e) => setEvent(e.target.value)}
              className="mt-2 max-w-full rounded border border-border bg-raised p-2 text-xs"
            >
              <option value="" disabled>
                Select stored game
              </option>
              {games.map((g) => (
                <option key={g.event} value={g.event}>
                  {g.event}
                </option>
              ))}
            </select>
            <p className="mt-2 text-right font-display text-2xl tabular-nums">
              {now?.clock_label ?? SILENT}
            </p>
          </div>
        </header>
        {error ? (
          <p role="alert" className="rounded border border-border p-4">
            STORE SILENT — {error}
          </p>
        ) : null}
        {!game && !error ? <p className="text-sm text-muted">Loading stored face data…</p> : null}
        {game && now ? (
          <>
            <div
              aria-label="Provenance"
              className="break-all border-y border-border py-2 font-mono text-xs text-muted"
            >
              event {game.face.provenance.event_id ?? SILENT} · OS{" "}
              {game.face.provenance.os_sha256 ?? SILENT}
              <br />
              trace {game.face.provenance.trace_sha256 ?? SILENT} · bench{" "}
              {game.face.provenance.bench_sha256 ?? SILENT}
              <br />
              bell source {game.face.bell.source ?? SILENT} ·{" "}
              {game.face.bench.label ?? "Bench: STORE SILENT"}
            </div>
            {game.face.bench.clock_status === "CLOCK_MISMATCH_STORE_SILENT" ? (
              <p role="status" className="border border-border p-3 text-xs text-muted">
                STORE SILENT — bench clock differs from this trace by{" "}
                {game.face.bench.clock_delta_seconds} seconds. No aligned bench ESS, VALIDITY or
                role is shown.
              </p>
            ) : null}
            <TuneHud game={game} receipt={receipt} bench={checkpoint?.bench ?? null} />
            {now.pre_first_tick ? (
              <p role="status" className="rounded-md border border-rest bg-surface p-3 text-sm">
                PRE-FIRST-TICK INSPECTION — this is not a playable checkpoint. The first real pair
                tick is {game.face.first_tick.clock_label}. Only stored pre-roll tape and receipts
                are shown.
              </p>
            ) : null}
            <section className="overflow-hidden rounded-md border border-border">
              <TunePlayback
                game={game}
                frame={frame}
                receiptIndex={receiptIndex}
                playing={playing}
                onFrame={selectFrame}
                onPlaying={setPlaying}
                onReceipt={setSelectedReceipt}
              />
              {game.face.legs.map((l) => (
                <div key={l} className="border-t border-border">
                  <TuneChart game={game} frame={frame} side={l} onReceipt={inspect} />
                </div>
              ))}
            </section>
            <TuneScene
              game={game}
              receipt={receipt}
              bench={checkpoint?.bench ?? null}
              checkpoint={exactCheckpoint?.label ?? null}
              onInspect={() => receipt && inspect(receipt.index)}
            />
            <TuneReceipts receipts={game.face.os} onInspect={inspect} />
            <ReceiptInspector
              receipt={inspected == null ? null : game.face.os[inspected]}
              onClose={closeInspector}
            />
          </>
        ) : null}
      </div>
    </main>
  );
}
