import { useEffect, useRef, useState } from 'react';
import { frameForReceipt, type Game, type LoadedGame, type Receipt } from '@/lib/tune-tape';
import { bellTime, plain, cents, replayClock } from '@/lib/reading-view';
import { DecisionEngine, SideReadings, pressureAt } from './decision-engine';
import { ReadingChart } from './reading-chart';
import { LabPressure } from './lab-pressure';
import { TuneChart } from './tune-chart';
import { TunePlayback } from './tune-playback';
import { TuneHud } from './tune-scene';
import { LabSide, LabBidLog } from './lab-panels';
import { TuneReceipts } from './tune-receipts';
import { ReceiptInspector } from './receipt-inspector';
import '../lab-reading.css';
import '../lab-engine.css';

export function LabReading({game,games,event,frame,receipt,receiptIndex,playing,inspected,onEvent,onFrame,onPlaying,onReceipt,onInspect,onCloseInspector,onImport}: {
  game:LoadedGame; games:Game[]; event:string|null; frame:number; receipt:Receipt|null; receiptIndex:number|null; playing:boolean; inspected:number|null;
  onEvent:(event:string)=>void; onFrame:(n:number)=>void; onPlaying:(p:boolean)=>void; onReceipt:(n:number)=>void;
  onInspect:(n:number)=>void; onCloseInspector:()=>void; onImport:(file:File)=>void;
}) {
  const [details,setDetails]=useState(false), detailPanel=useRef<HTMLElement>(null);
  const now=game.frames[frame], axis=game.face.render.axis, checkpoint=game.face.render.checkpoints[now.checkpoint_index];
  const outcome=game.grade?.OUTCOME;
  const pressure=pressureAt(game,now.minutesToBell,receiptIndex);
  useEffect(()=>{setDetails(false)},[event]);
  function inspect(index:number){setDetails(true);onInspect(index);requestAnimationFrame(()=>detailPanel.current?.scrollIntoView({block:'start',behavior:'smooth'}))}
  function jump(direction:number){
    const next=direction>0?game.face.os.find(r=>receiptIndex==null||r.index>receiptIndex):[...game.face.os].reverse().find(r=>receiptIndex!=null&&r.index<receiptIndex);
    if(next){onFrame(frameForReceipt(game.frames,next));onReceipt(next.index)}onPlaying(false);
  }
  function seek(minutes:number){
    const next=game.frames.findIndex((r,i)=>i>=game.face.render.play_start_frame&&r.minutesToBell<=minutes);
    onFrame(next<0?game.frames.length-1:next);onPlaying(false);
  }
  const markers=[
    ...game.face.legs.flatMap(side=>{const floor=game.face.truth?.legs[side];return floor?.status==='OK'&&floor.minutes_to_bell!=null?[{id:`${side}-floor`,label:`${side} recorded floor · ${replayClock(floor.minutes_to_bell)} (known afterward)`,progress:floor.markers.play.display_progress,minutes:floor.minutes_to_bell,fill:false,receipt_index:null}]:[]}),
    ...game.face.render.fill_events.map(f=>({id:`${f.leg}-fill`,label:`${f.label} · ${replayClock(f.minutesToBell)}${f.minutesToBell<now.minutesToBell?' (later in replay)':''}`,progress:f.plot_progress,minutes:f.minutesToBell,fill:true,receipt_index:f.receipt_index})),
  ];
  return <>
    <div className="reading-stage">
      <header className="reading-game-header">
        <label className="reading-game-label"><span className="sr-only">Game</span><select id="load-game" aria-label="Load game" value={event??''} onChange={e=>onEvent(e.target.value)}>{games.map(g=><option key={g.event} value={g.event}>{g.event===event?game.face.legs.join(' vs '):g.event.split('-').at(-1)?.slice(7)}</option>)}</select></label>
        <div className="engine-ruler" title={`Recorded floors · hindsight only\nTruth ${game.face.truth?.table_commit}\nRow ${game.face.truth?.row_sha256}`}><small>RECORDED FLOORS · KNOWN AFTERWARD</small><div>{game.face.legs.map(side=><span key={side} title={game.face.truth?.legs[side]?.line}>{side} <b>{cents(game.face.truth?.legs[side]?.floor_cents)}</b></span>)}</div><small>{plain(game.face.truth?.pair.compact_line)}</small></div>
        <div className="reading-result" title={`Final grade (known afterward)\n${game.grade?.display.governing??'No grade here'}\nOS ${game.face.provenance.os_sha256}\nTrace ${game.face.provenance.trace_sha256}`}>
          <span data-grade-letter className="reading-grade">{game.grade?.display.letter??'—'}</span>
          <p><span>FINAL PAIR</span><br/><b>{!outcome?'No result':outcome.pair_completed&&outcome.pair_sum!=null?`${outcome.pair_sum}¢`:'Incomplete'}</b><br/><em>{outcome?.captured_cents??'—'} of {outcome?.best_capturable_cents??'—'}¢ captured</em></p>
        </div>
        <button className="reading-details-button" aria-expanded={details} aria-controls="reading-details" onClick={()=>setDetails(v=>!v)}>Details {details?'−':'+'}</button>
      </header>
      <div className="engine-instrument">
        {game.face.legs.map((side,i)=><div className={`engine-wing engine-wing-${i}`} key={side}><ReadingChart game={game} frame={frame} side={side} receipt={receipt} onReceipt={inspect}/><SideReadings game={game} side={side} row={pressure} index={receiptIndex} onReceipt={inspect}/></div>)}
        <DecisionEngine game={game} row={pressure} index={receiptIndex} clock={replayClock(now.minutesToBell)} onReceipt={inspect}/>
      </div>
      <div className="engine-legend"><span className="key-tape">Tape · rises / falls</span><span className="key-call">Current call</span><span className="key-bid">Our bid / fill</span><span className="key-floor">Recorded floor</span><span className="key-perfect">Perfect sentence</span></div>
      <LabPressure game={game} row={pressure}/>
      <div className="reading-transport">
        <div className="reading-transport-buttons"><button aria-label="Previous receipt" onClick={()=>jump(-1)}>Prev</button><button disabled={now.pre_first_tick} onClick={()=>onPlaying(!playing)}>{playing?'Pause':'Play'}</button><button aria-label="Next receipt" onClick={()=>jump(1)}>Next</button></div>
        <div className="reading-timeline">
          <div className="reading-timeline-track" aria-hidden="true"/>
          {markers.map(m=><button key={m.id} data-timeline-event={m.id} className={`reading-timeline-mark ${m.fill?'is-fill':'is-floor'}`} style={{left:`${m.progress*100}%`}} title={m.label} aria-label={m.label} onClick={()=>{if(m.receipt_index!=null){onFrame(frameForReceipt(game.frames,game.face.os[m.receipt_index]));onReceipt(m.receipt_index);onPlaying(false)}else seek(m.minutes)}}><span/></button>)}
          <input id="gate-jump" aria-label="Replay time to bell" aria-valuetext={`${bellTime(now.minutesToBell)} to bell`} type="range" min={-axis.start_minutes_to_bell} max={-axis.end_minutes_to_bell} step="any" value={Math.max(-axis.start_minutes_to_bell,-now.minutesToBell)} onChange={e=>seek(-Number(e.target.value))}/>
          <span className="reading-timeline-start">first tick</span><span className="reading-timeline-end">bell</span>
        </div>
        <span className="reading-time" title={`${now.minutesToBell} minutes to bell · stored tape clock`}>{replayClock(now.minutesToBell)}</span>
      </div>
      <p className="reading-ruler-note" title={`OS ${game.face.provenance.os_sha256}\nTrace ${game.face.provenance.trace_sha256}`}>Floor, perfect sentence &amp; final grade: hindsight, not machine inputs. <span>OS {game.face.provenance.os_sha256?.slice(0,8)} · trace {game.face.provenance.trace_sha256?.slice(0,8)}</span></p>
    </div>
    {details?<section id="reading-details" className="reading-details-panel" ref={detailPanel} aria-label="Replay details">
      <header><h2>Details · every recorded field</h2><button onClick={()=>setDetails(false)}>Close details</button></header>
      <p className="terminal-provenance">Event {game.face.provenance.event_id} · OS {game.face.provenance.os_sha256}<br/>Trace {game.face.provenance.trace_sha256} · Bell source {game.face.bell.source}</p>
      <p>{plain(game.face.truth?.pair.compact_line)}</p>
      <label>Load a prepared replay <input type="file" accept=".json" onChange={e=>{const f=e.target.files?.[0];if(f)onImport(f)}}/></label>
      <p>Prepared library or tune replay only. This browser does not run the engine or place orders.</p>
      <TunePlayback game={game} frame={frame} receiptIndex={receiptIndex} playing={playing} onFrame={onFrame} onPlaying={onPlaying} onReceipt={onReceipt}/>
      <div className="reading-details-grid"><div>{game.face.legs.map(side=><LabSide key={side} game={game} receipt={receipt} side={side}/>)}<LabBidLog game={game} receiptIndex={receiptIndex} onReceipt={inspect}/><TuneReceipts receipts={game.face.os} onInspect={inspect}/></div>
      <div><TuneHud game={game} receipt={receipt} bench={checkpoint?.bench??null}/><ReceiptInspector receipt={inspected==null?receipt:game.face.os[inspected]} onClose={onCloseInspector}/></div></div>
      <details><summary>Book lines, pool bands and sentence gap</summary>{game.face.legs.map(side=><TuneChart key={side} game={game} frame={frame} side={side} onReceipt={inspect}/>)}</details>
      <p className="terminal-muted">/ choose game · [ ] switch game · G timeline · Space play/pause · arrows previous/next receipt</p>
    </section>:null}
  </>;
}
