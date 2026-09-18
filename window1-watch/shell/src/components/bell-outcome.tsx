import { useEffect, useRef } from 'react';
import type { LoadedGame } from '@/lib/tune-tape';
import { closeDeltaReading, signedCents } from '@/lib/close-delta';
import { cents } from '@/lib/reading-view';
import '../lab-jumps.css';
const none='no data here';
// Shown on the final receipt. Hindsight only: realized W1 closes and credited
// fills from the stored grade. Never a machine input, never recomputed here.
export function BellOutcome({game}:{game:LoadedGame}) {
  const card=useRef<HTMLElement>(null);
  useEffect(()=>{card.current?.scrollIntoView({block:'nearest',behavior:'smooth'})},[]);
  const grade=game.grade, outcome=grade?.OUTCOME, result=grade?.handoff_close_result, reading=closeDeltaReading(grade);
  const fees=grade?.close_delta_grade?grade.display.sections.find(s=>s.name==='FEES'):null;
  return <section className="bell-outcome" data-bell-outcome ref={card} aria-label="Bell outcome"
    title={result?`${result.role}\n${JSON.stringify(result.provenance)}`:game.grade_status}>
    <header><b>BELL · OUTCOME</b><small>final receipt · known afterward, not a machine input</small></header>
    {!grade?<p>{none} — {game.grade_status}</p>:<div className="bell-outcome-grid">
      <table data-bell-legs><thead><tr><th>Side</th><th>Fill</th><th>W1 close</th><th>Close − fill</th></tr></thead><tbody>{game.face.legs.map(side=>{
        const fill=outcome?.legs?.[side], leg=result?.legs[side];
        return <tr key={side} data-credited={leg?.credited_fill_cents!=null}><td>{side}</td>
          <td title={fill?.reason??undefined}>{!fill?none:!fill.filled?'no fill':`${cents(fill.cents)}${fill.valid_span_fill===false?' · not credited':''}`}</td>
          <td>{leg?cents(leg.close_cents):none}</td><td>{leg?signedCents(leg.close_delta_cents):none}</td></tr>})}</tbody></table>
      <dl data-bell-pair>
        <div><dt>Pair cost</dt><dd>{result?.pair_fill_sum_cents!=null?cents(result.pair_fill_sum_cents):outcome?.pair_completed&&outcome.pair_sum!=null?cents(outcome.pair_sum):'pair incomplete'}</dd></div>
        <div><dt>Closes' sum</dt><dd>{result?cents(result.pair_close_sum_cents):none}</dd></div>
        <div><dt>Pair vs closes</dt><dd>{result?result.pair_delta_cents!=null?signedCents(result.pair_delta_cents):'pair incomplete':none}</dd></div>
        {fees?<div><dt>Fees</dt><dd>{fees.line}</dd></div>:null}
      </dl>
      <div className="bell-outcome-grade" data-bell-grade title={reading?.rule}>
        <small>GRADE · W1 CLOSE-DELTA RULER</small>
        <b>{reading?.mark??grade.display.letter}</b>
        <span>{reading?reading.status:`floor-ruler letter · ${none} on the close-delta ruler for this replay`}</span>
      </div>
    </div>}
    {result?<p className="bell-outcome-line">{result.line}</p>:null}
  </section>;
}
