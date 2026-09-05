import { useEffect, useRef, useState } from "react";
import { loadReceipt, SILENT, type Receipt } from "@/lib/tune-tape";
// Each branch mounts on demand. No truncation, array cap, schema whitelist or numerical transform.
function Tree({ name, value }: { name: string; value: unknown }) {
  const [open, setOpen] = useState(false);
  if (value === null || value === undefined)
    return (
      <p className="break-words py-1">
        <span className="text-muted">{name}: </span>
        {SILENT}
      </p>
    );
  if (typeof value !== "object")
    return (
      <p className="break-words py-1">
        <span className="text-muted">{name}: </span>
        {String(value)}
      </p>
    );
  const entries = Object.entries(value);
  if (!entries.length)
    return (
      <p className="py-1 text-muted">
        {name}: {Array.isArray(value) ? "[]" : "{}"}
      </p>
    );
  return (
    <details
      onToggle={(e) => setOpen(e.currentTarget.open)}
      className="border-l border-border pl-3"
    >
      <summary className="cursor-pointer py-1 text-accent">{name}</summary>
      {open ? entries.map(([key, v]) => <Tree key={key} name={key} value={v} />) : null}
    </details>
  );
}
export function ReceiptInspector({
  receipt,
  onClose,
}: {
  receipt: Receipt | null;
  onClose: () => void;
}) {
  const [data, setData] = useState<Awaited<ReturnType<typeof loadReceipt>> | null>(null),
    [error, setError] = useState<string | null>(null);
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    setData(null);
    setError(null);
    if (!receipt?.detail_url) return;
    const controller = new AbortController();
    loadReceipt(receipt.detail_url, controller.signal)
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setError(String(e));
      });
    return () => controller.abort();
  }, [receipt]);
  useEffect(() => {
    if (!receipt) return;
    const previous = document.activeElement as HTMLElement | null;
    panel.current?.focus();
    const listener = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "Tab" && panel.current) {
        const elements = Array.from(
          panel.current.querySelectorAll<HTMLElement>('button,a,summary,[tabindex="0"]'),
        );
        const first = elements[0],
          last = elements.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", listener);
    return () => {
      document.removeEventListener("keydown", listener);
      previous?.focus();
    };
  }, [receipt, onClose]);
  if (!receipt) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/60" onClick={onClose}>
      <div
        ref={panel}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label="Full receipt inspector"
        onClick={(e) => e.stopPropagation()}
        className="absolute inset-y-0 right-0 w-full max-w-3xl overflow-auto border-l border-border bg-bg p-5 text-xs text-fg shadow-2xl"
      >
        <header className="sticky top-0 z-10 bg-bg pb-4">
          <div className="flex justify-between gap-4">
            <h2 className="font-display text-3xl">Every single thing</h2>
            <button className="rounded border border-border px-3 py-2" onClick={onClose}>
              Close inspector
            </button>
          </div>
          <p className="mt-2 break-all text-muted">
            {receipt.receipt ?? SILENT} · {receipt.clock_label}
          </p>
        </header>
        {error ? (
          <p role="alert">STORE SILENT — {error}</p>
        ) : !data ? (
          <p>Loading this receipt only…</p>
        ) : (
          <>
            <h3 className="font-display text-xl">Decision index — as stored</h3>
            <pre className="my-3 whitespace-pre-wrap break-words rounded bg-raised p-3">
              {JSON.stringify(data.inspector, null, 2)}
            </pre>
            <h3 className="mb-3 font-display text-xl">Full stage · every original field</h3>
            <Tree name="source" value={data.source} />
            <Tree name="row" value={data.row} />
          </>
        )}
      </div>
    </div>
  );
}
