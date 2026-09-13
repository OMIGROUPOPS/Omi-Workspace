import type { LoadedGame } from '@/lib/tune-tape';

export function LabPressure({game, minutesToBell}:{game:LoadedGame;minutesToBell:number}) {
  // Exact receipt state, carried openly. No resampling/likelihood/pressure model
  // runs in the face, and no later receipt can enter this replay position.
  const row=game.pressure?.rows.slice().reverse().find(r=>r.minutes_to_bell>=minutesToBell);
  return <section className="lab-pressure" aria-label="Pressure chain" data-pressure-chain>
    <header><span>What the machine read</span><span>{row?`Last recorded receipt · ${row.clock_label}`:game.pressure_status??'no data here'}</span></header>
    {game.face.legs.map(side=><div className="lab-pressure-side" key={side}>
      <strong>{side}</strong>
      {row?.legs[side]?.cards.map(card=><details key={card.label}>
        <summary title={`${card.keys.map(key=>row.legs[side].values[key].source??row.legs[side].values[key].reason).join('\n')}\n${card.source??''}\n${row.clock_label} · stage ${row.stage_sha256}`}><small>{card.label}</small><span>{card.text}</span></summary>
        <div className="lab-pressure-popover">
          {card.keys.map(key=>{const v=row.legs[side].values[key];return <p key={key} title={`${v.source??'No joined source'}\nReader epoch ${v.source_epoch??'unknown'}\nStage SHA ${row.stage_sha256}`}><b>{v.label}</b>: {v.text}{v.reason?<small>{v.reason}</small>:null}</p>})}
          {card.note?<p>{card.note}<small>{card.raw_layer} · {card.source}</small></p>:null}
          <p className="terminal-muted">Receipt {row.receipt_index} · {row.clock_label}<br/>Trace {game.pressure?.provenance.trace_sha256}<br/>Stage {row.stage_sha256}</p>
        </div>
      </details>)??<span>no data here</span>}
    </div>)}
    <footer><span title={row?.pair.source}>{row?.pair.text??'no data here'}</span><span>Observed volume / depth ≠ a proved reason for the call</span></footer>
  </section>;
}
