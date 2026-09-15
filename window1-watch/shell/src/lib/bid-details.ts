export type BidDetailSource = {
  schema: string; event: string; os_sha256: string; trace_sha256: string;
  detail_url?: string; sha256_uncompressed?: string; action_count: number;
  chunks?: {group:string;first:number;last:number;detail_url:string;sha256_uncompressed:string;bytes_uncompressed:number}[];
};
type FullAction = {id: string; details_lines: string[]; [key: string]: unknown};
const cache = new Map<string, Promise<Map<string, FullAction>>>();

// Called only by an opened details toggle. No startup fetch or unverified fallback.
export async function loadBidDetail(source: BidDetailSource, id: string, detailKey?: string): Promise<FullAction> {
  const chunked=source.schema==='bid-card-details-v2';
  const lookup=(detailKey??(id.startsWith('timeline:')?id.slice('timeline:'.length):'')).split(':');
  const memberIndex=Number(lookup[1]);
  const chunk=chunked?source.chunks?.find(c=>c.group===lookup[0]&&c.first<=memberIndex&&c.last>=memberIndex):undefined;
  const selected=chunked?chunk:source;
  const expected=chunked&&chunk?`/data/${source.event}.bid-details/${chunk.group}-${chunk.first}.json`:`/data/${source.event}.bid-details.json`;
  if ((!chunked&&source.schema !== 'bid-card-details-v1') || !/^[A-Z0-9-]+$/.test(source.event) || !selected?.detail_url || selected.detail_url!==expected)
    throw new Error('Invalid bid-detail path');
  const key = selected.detail_url + ':' + selected.sha256_uncompressed;
  if (!cache.has(key)) {
    // Keep only the most recently inspected game; large audits must not accumulate.
    cache.clear();
    const request = (async () => {
      const response = await fetch(selected.detail_url!, {cache: 'no-cache'});
      if (!response.ok) throw new Error(`Bid details: HTTP ${response.status}`);
      const bytes = await response.arrayBuffer();
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)))
        .map(n => n.toString(16).padStart(2, '0')).join('');
      if (hash !== selected.sha256_uncompressed) throw new Error('Bid-detail hash mismatch');
      const data = JSON.parse(new TextDecoder().decode(bytes));
      for (const field of ['schema', 'event', 'os_sha256', 'trace_sha256'] as const)
        if (data[field] !== source[field]) throw new Error(`Bid-detail provenance mismatch: ${field}`);
      const rows: FullAction[] = chunked?data.actions:[...data.actions.bid_actions, ...data.actions.supersessions];
      const index = new Map(rows.map(row => [row.id, row]));
      if (rows.length !== (chunk?chunk.last-chunk.first+1:source.action_count) || index.size !== rows.length) throw new Error('Bid-detail count mismatch');
      if(chunk){if(data.group!==chunk.group||data.first!==chunk.first)throw new Error('Bid-detail range mismatch');rows.forEach((row,i)=>index.set(`timeline:${chunk.group}:${chunk.first+i}`,row));}
      else for(const group of ['bid_actions','supersessions'])data.actions[group].forEach((row:FullAction,i:number)=>index.set(`timeline:${group}:${i}`,row));
      return index;
    })();
    cache.set(key, request);
    request.catch(() => cache.delete(key));
  }
  const index = await cache.get(key)!;
  const action = index.get(id);
  if (!action) throw new Error('Bid detail missing for this action');
  return action;
}
