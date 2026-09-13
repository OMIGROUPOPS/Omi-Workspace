import type { LoadedGame, PressureRow } from '@/lib/tune-tape';

export function LabPressure({game,row}:{game:LoadedGame;row:PressureRow|undefined}) {
  // Exact receipt state, carried openly. No resampling/likelihood/pressure model
  // runs in the face, and no later receipt can enter this replay position.
  const steps=[['Aggressive trades','Who hit the book',['taker_flow']],['Maker response','Added / pulled / refilled',['maker_residual','refill_ratio']],['Price response','Held / slipped / recovered',[]],['Partner response','Followed / diverged',[]]] as const;
  return <section className="lab-pressure" aria-label="Pressure chain" data-pressure-chain>
    <header><span>PRESSURE CHAIN</span><small>Recorded where available · not installed price setters</small></header>
    <div className="pressure-chain-grid">{steps.map(([label,gloss,keys])=><details key={label}><summary><b>{label}</b><small>{gloss}</small><span>no data here</span></summary><div>{game.face.legs.map(side=><p key={side}><b>{side}</b> {keys.map(key=>row?.legs[side]?.values[key]?.text??'no data here').join(' · ')||'No synchronized response interval in this replay.'}</p>)}<p>No exact game / receipt / span-bound measurement. Library recovery is not a measurement for this loaded game; snapshot size is not refill.</p></div></details>)}</div>
    <div className="pressure-chain-foot"><span title={`${row?.pair.source??''}\nStage ${row?.stage_sha256??'missing'}`}>{row?.pair.text??'no data here'} · snapshot, not a response</span><span>More recorded fields in Details</span></div>
  </section>;
}
