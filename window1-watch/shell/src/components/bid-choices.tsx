import type { BidChoices } from '@/lib/tune-tape';
// Riser twin of the faller's reach table: same section, same table styling.
// Every cell is a builder-written string from the stored licensing receipt.
export function RiserBidChoices({side,choices,provenance}:{side:string;choices:BidChoices;provenance:(field:string)=>string}) {
  return <section className="engine-reach-table" data-reach-table={side} data-bid-choices="riser" aria-label={`${side} bid choices`}>
    <header>{choices.header}</header>
    <table><thead><tr>{choices.columns.map(c=><th key={c}>{c}</th>)}</tr></thead><tbody>{choices.rows.map(r=><tr key={r.cells[0]} data-licensed={r.licensed} title={provenance(r.source)}>{r.cells.map((cell,i)=><td key={i}>{cell}</td>)}</tr>)}</tbody></table>
    <small title={choices.source}>{choices.note}</small>
    {choices.raw_reason?<details><summary>Full licensing reason</summary><p>{choices.raw_reason}</p></details>:null}
  </section>;
}
