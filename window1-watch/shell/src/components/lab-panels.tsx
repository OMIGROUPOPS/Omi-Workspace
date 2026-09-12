import type { LoadedGame, Receipt } from '@/lib/tune-tape';
type Row = Record<string, any>;
export const display = (v: unknown) => v == null ? 'STORE SILENT' : typeof v === 'number' && !Number.isInteger(v) ? v.toFixed(2) : String(v);
export function Source({ value, field, game, bid = false }: { value: unknown; field: string; game: LoadedGame; bid?: boolean }) {
  return <span className={bid ? 'terminal-bid' : undefined} title={`${field}\nRaw: ${String(value ?? 'STORE SILENT')}\nOS ${game.face.provenance.os_sha256}\nTrace ${game.face.provenance.trace_sha256}`}>{display(value)}</span>;
}
export function LabSide({ game, receipt, side }: { game: LoadedGame; receipt: Receipt | null; side: string }) {
  const d = receipt?.legs[side] as Row | undefined, p = d?.pool_cascade, selected = p?.layers?.[p?.selected_layer];
  const src = (value: unknown, field: string, bid = false) => <Source value={value} field={`OS ${receipt?.receipt} · legs.${side}.${field}`} game={game} bid={bid} />;
  return <section className="lab-side" aria-label={`${side} sentence and book`}>
    <h2>{side} / Sentence</h2>
    <table><thead><tr><th>P now</th><th>Q floor</th><th>X minutes to bell</th></tr></thead><tbody><tr>
      <td>{src(p?.current_last_cents, 'pool_cascade.current_last_cents')}</td>
      <td>{src(selected?.floors?.q50?.level_cents, 'selected.floors.q50.level_cents')}</td>
      <td>{src(selected?.floors?.q50?.minutes_to_bell, 'selected.floors.q50.minutes_to_bell')}</td>
    </tr></tbody></table>
    <p title={receipt?.display.legs[side]?.sentence}>Author {src(p?.selected_layer, 'pool_cascade.selected_layer')} / {src(p?.status, 'pool_cascade.status')}</p>
    <p>Role {src(p?.roles?.current_role, 'pool_cascade.roles.current_role')} / first bind {src(p?.roles?.first_bind, 'pool_cascade.roles.first_bind')}</p>
    <table><thead><tr><th>Members</th><th>ESS</th><th>Weight sum</th></tr></thead><tbody><tr><td>{src(selected?.member_count, 'selected.member_count')}</td><td>{src(selected?.ess, 'selected.ess')}</td><td>{src(selected?.weight_sum, 'selected.weight_sum')}</td></tr></tbody></table>
    <p>Q range {src(selected?.floors?.q25?.level_cents,'selected.floors.q25.level_cents')} — {src(selected?.floors?.q75?.level_cents,'selected.floors.q75.level_cents')}¢</p>
    <details><summary>Exact sentence and pool layers</summary><p>{receipt?.display.legs[side]?.sentence ?? 'STORE SILENT'}</p><pre>{JSON.stringify(p ?? null,null,2)}</pre></details>
    <h2>{side} / Five-level book</h2>
    <div className="book-scroll"><table><thead><tr><th>Bid size</th><th>Bid</th><th>Ask</th><th>Ask size</th><th>Maker ±</th></tr></thead><tbody>
      {Array.from({length:5},(_,i)=><tr key={i}><td title="Depth size absent from compact face">—</td><td>{src(i===0?d?.bid:null,'bid; deeper levels not stored')}</td><td>{src(i===0?d?.ask:null,'ask; deeper levels not stored')}</td><td title="Depth size absent from compact face">—</td><td title="Maker residual absent from compact face">—</td></tr>)}
    </tbody></table></div>
    <p className="terminal-muted">Depth sizes / maker residual: STORE SILENT. Missing is not zero.</p>
    <p>Last {src(d?.last,'last')} / running low {src(d?.running_low,'running_low')}¢</p>
    <p>Our bid <Source value={receipt?.display.legs[side]?.rest_label} field={`OS ${receipt?.receipt} display.legs.${side}.rest_label`} game={game} bid /></p>
    <h2>{side} / Pool members and weights</h2>
    <p className="terminal-muted">STORE SILENT — this trace stores counts and weight sums, not individual member rows. Nothing reconstructed.</p>
  </section>;
}
export function LabBidLog({game,receiptIndex,onReceipt}:{game:LoadedGame;receiptIndex:number|null;onReceipt:(n:number)=>void}) {
  const actions=[...game.face.render.bid_actions,...(game.face.render.supersessions??[])].filter(a=>receiptIndex!=null&&a.receipt_index<=receiptIndex).sort((a,b)=>b.receipt_index-a.receipt_index);
  return <section aria-label="Bid actions and reasons"><h2>Bid actions / reasons / supersessions</h2><div className="terminal-log"><table><thead><tr><th>Side</th><th>Action</th><th>Reason</th><th>Receipt</th></tr></thead><tbody>{actions.map(a=><tr key={a.id}><td>{a.leg}</td><td className="terminal-bid"><button onClick={()=>onReceipt(a.receipt_index)} title={a.details_lines.join('\n')}>{a.card_lines[0]}</button></td><td title={a.details_lines.join('\n')}>{a.card_lines[1]}</td><td><Source value={a.receipt_index} field={`render.bid_actions ${a.id}`} game={game}/></td></tr>)}</tbody></table></div></section>;
}
