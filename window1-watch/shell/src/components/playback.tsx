import { BEATS, WINDOW_HOURS_TOTAL, beatAtHours, hoursRemaining } from "@/lib/tape";
import { Button } from "@/components/ui/button";

type Props = {
  hours: number;
  playing: boolean;
  onHours: (h: number) => void;
  onPlaying: (p: boolean) => void;
};

export function Playback({ hours, playing, onHours, onPlaying }: Props) {
  const beat = beatAtHours(hours);
  const idx = BEATS.findIndex((b) => b.id === beat.id);

  function jump(delta: number) {
    const next = Math.min(BEATS.length - 1, Math.max(0, idx + delta));
    onHours(BEATS[next].hours);
    onPlaying(false);
  }

  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-border px-3 py-3">
      <Button
        variant="outline"
        className="border-accent text-fg"
        onClick={() => onPlaying(!playing)}
      >
        {playing ? "Pause" : "Play"}
      </Button>
      <Button variant="outline" onClick={() => jump(-1)}>
        Prev
      </Button>
      <Button variant="outline" onClick={() => jump(1)}>
        Next
      </Button>
      <div className="min-w-0 flex-1 px-3">
        <label className="sr-only" htmlFor="window-scrub">
          Hours through the window
        </label>
        <input
          id="window-scrub"
          type="range"
          min={0}
          max={WINDOW_HOURS_TOTAL}
          step={0.5}
          value={hours}
          onChange={(e) => {
            onPlaying(false);
            onHours(Number(e.target.value));
          }}
          className="h-11 w-full"
        />
      </div>
      <p className="w-16 text-right text-sm tabular-nums text-fg">
        {hoursRemaining(hours).toFixed(1)}h
      </p>
    </div>
  );
}
