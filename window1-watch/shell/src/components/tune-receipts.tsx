import { memo } from "react";
import type { Receipt } from "@/lib/tune-tape";

// Static across playback: do not reconcile a thousand receipt buttons every tick.
export const TuneReceipts = memo(function TuneReceipts({
  receipts,
  onInspect,
}: {
  receipts: Receipt[];
  onInspect: (index: number) => void;
}) {
  return (
    <section className="rounded-md border border-border p-4">
      <h2 className="font-display text-2xl">OS receipts</h2>
      <p className="mt-1 text-xs text-muted">
        Includes receipts before the first traded pair. Click any receipt for its complete decision.
      </p>
      <div className="mt-3 max-h-64 overflow-y-auto">
        {receipts.map((r) => (
          <button
            key={r.receipt_id ?? r.index}
            onClick={() => onInspect(r.index)}
            className="block w-full border-b border-border py-2 text-left text-xs hover:bg-raised"
          >
            <span className="text-muted">{r.clock_label}</span> · {r.title}
          </button>
        ))}
      </div>
    </section>
  );
});
