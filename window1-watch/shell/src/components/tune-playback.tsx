import { Button } from "@/components/ui/button";
import { frameForReceipt, type LoadedGame } from "@/lib/tune-tape";
type Props = {
  game: LoadedGame;
  frame: number;
  receiptIndex: number | null;
  playing: boolean;
  onFrame: (n: number) => void;
  onPlaying: (p: boolean) => void;
  onReceipt: (n: number) => void;
};
export function TunePlayback({
  game,
  frame,
  receiptIndex,
  playing,
  onFrame,
  onPlaying,
  onReceipt,
}: Props) {
  const now = game.frames[frame],
    current = receiptIndex;
  function jump(direction: number) {
    const next =
      direction > 0
        ? game.face.os.find((r) => current === null || r.index > current)
        : [...game.face.os].reverse().find((r) => current !== null && r.index < current);
    if (next) {
      onFrame(frameForReceipt(game.frames, next));
      onReceipt(next.index);
    }
    onPlaying(false);
  }
  function checkpoint() {
    const next = game.face.render.checkpoints.find((c) => c.minutesToBell < now.minutesToBell);
    onFrame(next ? next.frame : game.frames.length - 1);
    onPlaying(false);
  }
  return (
    <div className="border-t border-border px-3 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <Button variant="outline" disabled={now.pre_first_tick} onClick={() => onPlaying(!playing)}>
          {playing ? "Pause" : "Play"}
        </Button>
        <Button variant="outline" onClick={() => jump(-1)}>
          Prev
        </Button>
        <Button variant="outline" onClick={() => jump(1)}>
          Next
        </Button>
        <Button variant="outline" onClick={checkpoint}>
          Next checkpoint
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            onPlaying(false);
            onFrame(game.face.render.play_start_frame);
          }}
        >
          First real tick
        </Button>
        <p className="ml-auto text-sm tabular-nums">{now.clock_label}</p>
      </div>
      <label className="sr-only" htmlFor="tune-scrub">
        Replay receipt and tape frames
      </label>
      <input
        id="tune-scrub"
        disabled={now.pre_first_tick}
        className="h-11 w-full"
        type="range"
        min={game.face.render.play_start_frame}
        max={game.frames.length - 1}
        step={1}
        value={now.pre_first_tick ? game.face.render.play_start_frame : frame}
        onChange={(e) => {
          onPlaying(false);
          onFrame(Number(e.target.value));
        }}
      />
      <div className="flex flex-wrap gap-2" aria-label="Atlas checkpoints">
        {game.face.render.checkpoints
          .filter((c) => c.playable)
          .map((c) => (
            <button
              key={c.minutesToBell}
              className={`checkpoint-flag rounded border px-2 py-1 text-xs tabular-nums ${frame === c.frame ? "border-accent text-fg" : "border-border text-muted"}`}
              onClick={() => {
                onPlaying(false);
                onFrame(c.frame);
              }}
              aria-label={`Checkpoint ${c.minutesToBell} minutes to bell`}
            >
              ⚑ {c.label}
            </button>
          ))}
      </div>
      {game.face.render.checkpoints.some((c) => !c.playable) ? (
        <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted">
          Before first pair tick — inspect only:
          {game.face.render.checkpoints
            .filter((c) => !c.playable)
            .map((c) => (
              <button
                key={c.minutesToBell}
                onClick={() => {
                  onPlaying(false);
                  onFrame(c.frame);
                }}
                aria-label={`Checkpoint ${c.minutesToBell} minutes to bell`}
                className="rounded border border-border px-2 py-1"
              >
                {c.label}
              </button>
            ))}
        </div>
      ) : null}
    </div>
  );
}
