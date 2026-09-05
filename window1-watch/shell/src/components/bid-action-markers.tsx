import { useEffect, useRef, useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";
import { type BidAction, type Frame } from "@/lib/tune-tape";

// Only selection and pixel placement happen here. Every label/hover line is stored.
export function BidActionMarkers({
  actions,
  now,
  side,
  color,
  onReceipt,
}: {
  actions: BidAction[];
  now: Frame;
  side: string;
  color: string;
  onReceipt: (index: number) => void;
}) {
  const [hover, setHover] = useState<{ action: BidAction; left: number; top: number } | null>(null);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelHide = () => {
    if (hideTimer.current) clearTimeout(hideTimer.current);
  };
  const hide = () => {
    cancelHide();
    hideTimer.current = setTimeout(() => setHover(null), 200);
  };
  useEffect(() => () => cancelHide(), []);
  useEffect(() => setHover(null), [now.receipt_index]);
  const show = (action: BidAction, element: HTMLElement) => {
    cancelHide();
    const box = element.getBoundingClientRect();
    setHover({ action, left: Math.max(8, Math.min(box.left, window.innerWidth - 488)), top: 8 });
  };
  return (
    <>
      {actions
        .filter(
          (a) =>
            a.leg === side && now.receipt_index != null && a.receipt_index <= now.receipt_index,
        )
        .map((a) => {
          const point = a.markers[now.pre_first_tick ? "inspection" : "play"];
          if (point?.price == null) return null;
          const style = {
            color,
            left: `calc(36px + (100% - 44px) * ${point.display_progress})`,
            top: `calc(16px + (100% - 46px) * ${point.price})`,
          } as CSSProperties;
          return (
            <div key={a.id} className="absolute z-10" style={style}>
              <button
                aria-label={point.label}
                data-action-id={a.id}
                data-action-kind={a.kind}
                data-boundary={point.boundary}
                style={{ left: a.stack_offset_px }}
                onMouseEnter={(e) => show(a, e.currentTarget)}
                onMouseLeave={hide}
                onFocus={(e) => show(a, e.currentTarget)}
                onBlur={hide}
                onKeyDown={(e) => {
                  if (e.key === "Escape") setHover(null);
                }}
                onClick={() => onReceipt(a.receipt_index)}
                className={`bid-action-marker absolute flex h-6 w-6 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-sm bg-bg/85 text-base leading-none outline-offset-2 hover:outline hover:outline-1 ${a.fill ? "fill-burst" : ""}`}
              >
                {a.glyph}
              </button>
              {a.fill ? (
                <div
                  className="fill-label-card absolute bottom-4 w-[280px] max-w-[70vw] rounded border border-border bg-bg/95 p-2 text-[11px] text-fg shadow-md"
                  style={{
                    left: point.display_progress > 0.6 ? "auto" : "-24px",
                    right: point.display_progress > 0.6 ? "-12px" : "auto",
                  }}
                >
                  <p className="font-medium leading-snug" style={{ color }}>
                    {a.fill.summary}
                  </p>
                  <p className="mt-1 text-muted">{a.fill.floor_line}</p>
                  <p className="mt-1 text-muted">{a.fill.placing_sentence_lines[0]}</p>
                  <details className="mt-1">
                    <summary className="cursor-pointer">Sentence that placed the rest</summary>
                    <div className="mt-1 max-h-40 space-y-1 overflow-auto break-words text-muted">
                      {a.fill.placing_sentence_lines.map((line, i) => (
                        <p key={i}>{line}</p>
                      ))}
                    </div>
                  </details>
                </div>
              ) : null}
            </div>
          );
        })}
      {hover
        ? createPortal(
            <div
              role="tooltip"
              tabIndex={0}
              onMouseEnter={cancelHide}
              onMouseLeave={hide}
              onFocus={cancelHide}
              onBlur={hide}
              onKeyDown={(e) => {
                if (e.key === "Escape") setHover(null);
              }}
              className="bid-action-tooltip fixed z-50 max-h-[calc(100vh-16px)] w-[472px] max-w-[calc(100vw-16px)] space-y-2 overflow-auto rounded-md border border-border bg-raised p-3 text-xs leading-relaxed text-fg shadow-lg"
              style={{ left: hover.left, top: hover.top }}
            >
              {hover.action.hover_lines.map((line, i) => (
                <p key={i} className="break-words">
                  {line}
                </p>
              ))}
            </div>,
            document.body,
          )
        : null}
    </>
  );
}
