import { SILENT, type LoadedGame, type Receipt, type Bench } from "@/lib/tune-tape";
const shown = (v: unknown) => (v == null ? SILENT : String(v));
export function TuneHud({
  game,
  receipt,
  bench,
}: {
  game: LoadedGame;
  receipt: Receipt | null;
  bench: Bench | null;
}) {
  const d = receipt?.display;
  return (
    <section
      aria-label="Tune test HUD"
      className="sticky top-0 z-20 rounded-md border border-border bg-bg/95 p-3 backdrop-blur-sm"
    >
      <div aria-label="FLOOR · RECORDED" className="mb-3 border-b border-border pb-3">
        <div className="flex flex-wrap items-center justify-between gap-1">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">FLOOR · RECORDED</p>
          <p className="text-[10px] uppercase tracking-[0.1em] text-muted">
            RULER — NOT AN OS INPUT
          </p>
        </div>
        {game.face.truth ? (
          <>
            <div className="mt-1 flex flex-wrap gap-x-6 gap-y-1 text-xs tabular-nums">
              {game.face.legs.map((leg, i) => (
                <p key={leg} className={i === 0 ? "text-alt" : "text-gas"}>
                  {game.face.truth?.legs[leg]?.line ?? SILENT}
                </p>
              ))}
            </div>
            <p className="mt-1 text-xs tabular-nums">
              {game.face.truth.pair.compact_line}
            </p>
            <details className="mt-1 text-[10px] text-muted">
              <summary>Recorded ruler source</summary>
              <p className="break-all">
                W1_GROUND_TRUTH_TABLE.csv @ {game.face.truth.table_commit} · row sha256{" "}
                {game.face.truth.row_sha256 ?? SILENT}
              </p>
            </details>
          </>
        ) : (
          <p className="mt-1 text-xs">
            STORE SILENT — recorded truth has not been built for this face
          </p>
        )}
      </div>
      <div className="grid gap-3 lg:grid-cols-[2fr_1fr_1fr_1fr]">
        <div className="min-w-0">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Brain · sentence</p>
          {game.face.legs.map((l, i) => (
            <p
              key={l}
              title={d?.legs[l]?.sentence}
              className={`truncate text-xs ${i === 0 ? "text-alt" : "text-gas"}`}
            >
              {l}: {d?.legs[l]?.sentence ?? SILENT}
            </p>
          ))}
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Pile · OS members</p>
          {game.face.legs.map((l, i) => (
            <div key={l} className="text-xs">
              <span>
                {l} {d?.legs[l]?.member_label ?? SILENT}
              </span>
              <div className="h-1 bg-raised">
                {d?.legs[l]?.member_percent != null ? (
                  <div
                    className={`h-1 ${i === 0 ? "bg-alt" : "bg-gas"}`}
                    style={{ width: `${d.legs[l].member_percent}%` }}
                  />
                ) : null}
              </div>
            </div>
          ))}
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Heart · pair exposure</p>
          <p className={`text-sm tabular-nums ${d?.above_par ? "text-blood" : "text-fg"}`}>
            {d?.pair_label ?? SILENT}
          </p>
          <div className="h-1 bg-raised">
            {d?.pair_percent != null ? (
              <div
                className={`h-1 ${d.above_par ? "bg-blood" : "bg-good"}`}
                style={{ width: `${d.pair_percent}%` }}
              />
            ) : null}
          </div>
          <p className="text-xs text-muted">
            Hands:{" "}
            {game.face.legs.map((l) => `${l} ${d?.legs[l]?.rest_label ?? SILENT}`).join(" · ")}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Validity · bench only</p>
          <p className="text-xs tabular-nums">{bench?.validity.label ?? SILENT}</p>
          <div className="mt-1 h-1 bg-raised">
            {bench?.validity.meter_percent != null ? (
              <div className="h-1 bg-good" style={{ width: `${bench.validity.meter_percent}%` }} />
            ) : null}
          </div>
          {bench ? <p className="text-xs text-muted">as of {bench.minutes_to_bell}m</p> : null}
        </div>
      </div>
    </section>
  );
}
export function TuneScene({
  game,
  receipt,
  bench,
  checkpoint,
  onInspect,
}: {
  game: LoadedGame;
  receipt: Receipt | null;
  bench: Bench | null;
  checkpoint: string | null;
  onInspect: () => void;
}) {
  return (
    <section
      className="scene-card rounded-md border border-border bg-surface p-4"
      key={checkpoint ?? receipt?.receipt_id ?? "silent"}
      aria-label="Checkpoint scene"
      data-receipt-id={receipt?.receipt_id}
      data-receipt-index={receipt?.index}
    >
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-muted">
            {checkpoint ? `Checkpoint ${checkpoint}` : "OS receipt"}
          </p>
          <h2 className="font-display text-2xl">{receipt?.title ?? SILENT}</h2>
          <p className="text-xs text-muted">OS snapshot: {receipt?.clock_label ?? SILENT}</p>
        </div>
        <button
          className="rounded border border-border px-3 py-2 text-xs"
          onClick={onInspect}
          disabled={!receipt?.detail_url}
        >
          Inspect receipt
        </button>
      </header>
      <div className="mt-3 grid gap-4 sm:grid-cols-2">
        {game.face.legs.map((l, i) => {
          const d = receipt?.display.legs[l];
          return (
            <div key={l} className="min-w-0 rounded-md bg-raised p-3">
              <h3 className={`font-display text-xl ${i === 0 ? "text-alt" : "text-gas"}`}>{l}</h3>
              <p className="mt-1 text-xs text-muted">Saw: {d?.saw ?? SILENT}</p>
              <p className="mt-2 text-xs">{d?.belief ?? SILENT}</p>
              <details className="mt-1 text-xs">
                <summary>Sentence and authors</summary>
                <p className="break-words py-2">{d?.sentence ?? SILENT}</p>
                <p className="break-words text-muted">{d?.authors ?? SILENT}</p>
              </details>
              <p className="mt-2 text-xs">OS family: {d?.family ?? SILENT}</p>
              <p className="text-xs">Bench role: {bench?.roles[l] ?? SILENT}</p>
              <p className="mt-2 break-words text-xs text-muted">Hands: {d?.hand_line ?? SILENT}</p>
              <p className="mt-2 text-xs text-muted">{d?.band_line ?? SILENT}</p>
            </div>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-muted">
        {receipt?.display.fills ?? SILENT} · pair {receipt?.display.pair_label ?? SILENT}
      </p>
      {bench ? (
        <details className="mt-3 text-xs">
          <summary>Bench pools: ESS and family calls · {game.face.bench.label ?? SILENT}</summary>
          <div className="overflow-x-auto">
            <table className="mt-2 w-full text-left">
              <thead>
                <tr>
                  <th>Rule</th>
                  <th>Raw ESS</th>
                  {game.face.legs.map((l) => (
                    <th key={l}>{l} family / usable ESS</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(bench.rules).map(([rule, r]) => (
                  <tr key={rule}>
                    <td className="py-1">{rule}</td>
                    <td>{r.label}</td>
                    {game.face.legs.map((l) => (
                      <td key={l}>
                        {r.sides[l]?.family ?? r.sides[l]?.status ?? SILENT} /{" "}
                        {shown(r.sides[l]?.ess)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      ) : (
        <p className="mt-3 text-xs text-muted">Bench ESS, VALIDITY and roles: STORE SILENT</p>
      )}
    </section>
  );
}
