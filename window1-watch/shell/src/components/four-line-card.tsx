// All content is builder-authored. Details are inline on line one and closed by default.
import {useState} from 'react';
import {loadBidDetail} from '@/lib/bid-details';
import type {BidAction} from '@/lib/tune-tape';
export function FourLineCard({
  lines,
  details,
  color,
  action,
}: {
  lines: string[];
  details: string[];
  color?: string;
  action?: BidAction;
}) {
  const [loaded, setLoaded] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  async function openDetails(open: boolean) {
    if (!open || !action?.bid_detail_source || loaded || loading) return;
    setLoading(true); setError(null);
    try { setLoaded((await loadBidDetail(action.bid_detail_source, action.id, action.bid_detail_key)).details_lines); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setLoading(false); }
  }
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
      <details className="raw-card-details" onToggle={e => void openDetails(e.currentTarget.open)}>
        <summary className="absolute right-0 top-0 cursor-pointer list-none bg-raised pl-2 text-[11px] leading-5 text-muted [&::-webkit-details-marker]:hidden">
          details ▸
        </summary>
        <div className="mt-2 max-h-64 space-y-2 overflow-auto border-t border-border pt-2 text-[11px] leading-relaxed text-muted">
          {loading ? <p>Loading recorded bid details…</p> : null}
          {error ? <p role="alert">No verified details here: {error}</p> : null}
          {[...details, ...(loaded ?? [])].map((line, i) => (
            <p key={i} className="break-words">
              {line}
            </p>
          ))}
        </div>
      </details>
    </div>
  );
}
