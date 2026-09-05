// All content is builder-authored. Details are inline on line one and closed by default.
export function FourLineCard({
  lines,
  details,
  color,
}: {
  lines: string[];
  details: string[];
  color?: string;
}) {
  return (
    <div className="four-line-card relative">
      <div className="card-lines overflow-x-auto text-xs leading-5">
        {lines.map((line, i) => (
          <p
            key={i}
            data-card-line
            className={`whitespace-nowrap ${i === 0 ? "pr-20 font-medium" : ""}`}
            style={i === 0 ? { color } : undefined}
          >
            {line}
          </p>
        ))}
      </div>
      <details className="raw-card-details">
        <summary className="absolute right-0 top-0 cursor-pointer list-none bg-raised pl-2 text-[11px] leading-5 text-muted [&::-webkit-details-marker]:hidden">
          details ▸
        </summary>
        <div className="mt-2 max-h-64 space-y-2 overflow-auto border-t border-border pt-2 text-[11px] leading-relaxed text-muted">
          {details.map((line, i) => (
            <p key={i} className="break-words">
              {line}
            </p>
          ))}
        </div>
      </details>
    </div>
  );
}
