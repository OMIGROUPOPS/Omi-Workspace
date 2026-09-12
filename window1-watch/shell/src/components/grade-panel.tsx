import type { LoadedGame } from "@/lib/tune-tape";

export function GradePanel({ game }: { game: LoadedGame }) {
  const grade = game.grade;
  return (
    <div aria-label="Grade card" className="mb-3 border-b border-border pb-3">
      <div className="flex items-start gap-4">
        <div className="shrink-0">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Grade</p>
          <p
            data-grade-letter
            className={`font-display text-5xl leading-none ${grade?.LETTER.letter === "F" ? "text-blood" : "text-fg"}`}
          >
            {grade?.display.letter ?? "—"}
          </p>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[10px] text-muted">{grade?.display.label ?? game.grade_status}</p>
          {grade?.display.sections.map((s) => (
            <p
              key={s.name}
              data-grade-section={s.name}
              title={s.hover_lines.join("\n")}
              className="truncate text-xs tabular-nums"
            >
              <span className="text-muted">{s.name}</span> · {s.line}
            </p>
          ))}
          {grade?.display.diagnostic_line ? (
            <p className="mt-1 truncate text-[10px] text-muted" title={grade.display.diagnostic_hover_lines?.join("\n")}>
              {grade.display.diagnostic_line}
            </p>
          ) : null}
          {grade ? (
            <p className="mt-1 truncate text-[10px] text-muted" title={grade.display.governing}>
              Governing: {grade.display.governing} ·{" "}
              <a
                className="underline"
                href={`/data/${grade.event}.grade.json`}
                target="_blank"
                rel="noreferrer"
              >
                full grade JSON
              </a>
            </p>
          ) : null}
          {grade?.display.ruler_line ? (
            <p className="mt-1 text-[10px] text-muted" title={grade.display.ruler_hover_lines?.join("\n")}>
              {grade.display.ruler_line}
            </p>
          ) : null}
        </div>
        <div className="hidden w-44 shrink-0 sm:block">
          <History game={game} />
        </div>
      </div>
      <div className="mt-2 sm:hidden">
        <History game={game} />
      </div>
    </div>
  );
}

function History({ game }: { game: LoadedGame }) {
  const view = game.history_view;
  return (
    <div aria-label="Grade history">
      <p className="text-[10px] uppercase tracking-[0.1em] text-muted">History · commit order</p>
      {view && game.history?.length ? (
        <div className="overflow-x-auto">
          <svg
            width={view.width}
            height={view.height}
            role="img"
            aria-label="Grade history by OS commit order"
            className="text-muted"
          >
            {view.labels.map((l) => (
              <text
                key={l.letter}
                x="1"
                y={l.y}
                dominantBaseline="middle"
                fill="currentColor"
                fontSize="9"
              >
                {l.letter}
              </text>
            ))}
            {game.history.map((h) => (
              <circle
                key={`${h.url}:${h.revision}`}
                data-grade-history-dot
                cx={h.x}
                cy={h.y}
                r="4"
                tabIndex={0}
                fill="currentColor"
                className={h.letter === "F" ? "text-blood" : "text-alt"}
                aria-label={h.hover_lines.join(" · ")}
              >
                <title>{h.hover_lines.join("\n")}</title>
              </circle>
            ))}
          </svg>
        </div>
      ) : (
        <p className="text-xs">STORE SILENT — no history</p>
      )}
    </div>
  );
}
