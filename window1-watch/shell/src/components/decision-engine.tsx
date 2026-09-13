import type { LoadedGame, PressureRow } from '@/lib/tune-tape';
const none='no data here';
export function pressureAt(game:LoadedGame,minutes:number,index:number|null) {
  return game.pressure?.rows.slice().reverse().find(r=>r.minutes_to_bell>=minutes&&index!=null&&r.receipt_index<=index);
}
export function executionAt(game:LoadedGame,side:string,index:number|null) {
  return game.pressure?.executions?.slice().reverse().find(r=>r.side===side&&index!=null&&r.receipt_index<=index);
}
function source(row:PressureRow|undefined,field:string) {
  return `${field}\nLast recorded receipt ${row?.receipt??none}\n${row?.clock_label??none}\nStage SHA ${row?.stage_sha256??none}`;
}
export function SideReadings({game,side,row,index,onReceipt}:{game:LoadedGame;side:string;row:PressureRow|undefined;index:number|null;onReceipt:(n:number)=>void}) {
  const leg=row?.legs[side], d=leg?.display, order=executionAt(game,side,index);
  return <div className="engine-side-readings">
    <button className="engine-secured" onClick={()=>{if(order?.origin_receipt_index!=null)onReceipt(order.origin_receipt_index)}} title={order?`${order.source}\nCall at ${order.origin_clock}; ${order.status.toLowerCase()} at ${order.clock}\n${order.floor_line??''}`:none}>
      <span><small>Bid-setting call</small><b>{order?.q??none}</b></span><span className="engine-secured-arrow">→</span><span><small>{order?.status??'No bid yet'}</small><b>{order?.value??'none'}</b></span>
    </button>
    <div className="engine-side-clock">{order?.status==='Filled'?<>Trade {order.print} · {order.clock}<br/>{order.floor_line}</>:order?.clock??'No bid placed at this point'}</div>
    <details className="engine-sensor"><summary title={source(row,leg?.values.contracts.source??none)}><span>TRADED VOLUME <i>watched</i></span><b>{leg?.values.contracts.text??none}</b><small>{leg?.values.prints.text??none}</small></summary><p>Recorded trade contracts and prints. Volume is watched separately from price; it does not set this bid.<br/>{leg?.values.contracts.source}</p></details>
    <details className="engine-sensor"><summary title={source(row,leg?.values.bid_depth.source??none)}><span>FIVE-LEVEL SIZE <i>recorded</i></span><div className="engine-depth-values"><b>{leg?.values.bid_depth.text.replace(' contracts','')??none}</b><small>bid / ask</small><b>{leg?.values.ask_depth.text.replace(' contracts','')??none}</b></div>{d?.bid_depth_fraction!=null?<div className="engine-depth-bar"><i style={{width:`${d.bid_depth_fraction*100}%`}}/></div>:null}</summary><p>Displayed contract size, not buying probability or proof of refill. Top sizes: {leg?.values.top_bid.text??none} / {leg?.values.top_ask.text??none}.<br/>{leg?.values.bid_depth.source}</p></details>
    <div className="engine-book" title={source(row,'row.reads.books; spread = ask minus bid, written by display builder')}><span>Book <b>{d?.book??none}</b></span><span>Spread <b>{d?.spread??none}</b></span></div>
  </div>;
}
export function DecisionEngine({game,row,index,clock,onReceipt}:{game:LoadedGame;row:PressureRow|undefined;index:number|null;clock:string;onReceipt:(n:number)=>void}) {
  const engine=row?.engine;
  return <aside className="decision-engine" aria-label="Decision engine" data-decision-engine>
    <header>DECISION ENGINE<small>{clock}</small></header>
    <details className="engine-pool"><summary title={source(row,engine?.source??none)}><b>{engine?.pool??none}</b><span>Both first prices + same clock</span><small>{engine?.first_prices??none} · {engine?.first_clock??none}</small></summary><p>One pair library, filtered per side. These first-price comparisons and each side's current reading form the call. Recording another variable does not mean it authored the price.</p></details>
    <div className="engine-fork" aria-hidden="true"><i/><i/></div>
    <div className="engine-label">CALL NOW <span>separate from a filled bid</span></div>
    <div className="engine-twins">{game.face.legs.map(side=>{const d=row?.legs[side]?.display;return <details key={side}><summary title={source(row,`${d?.source??none}\n${JSON.stringify(d?.raw??{})}`)}><small>{side} · {d?.role??none}</small><b>{d?.q??none}</b><small>by {d?.deadline??none}</small><span>{d?.count??none}</span><small>{d?.status==='price-setting forecast'?d.author:d?.status??none}</small></summary><p>{d?.status??none}<br/>Middle half: {d?.band??none}<br/>{d?.effective??none} effective games<br/>{Object.values(d?.raw??{}).join(' · ')}</p></details>})}</div>
    <div className="engine-monitor">
      <div className="engine-label">MOVE + VOLUME <span>{engine?.step_role??none}</span></div>
      <div className="engine-factors" title={source(row,'pool_cascade.likelihood_factors; median k_price and k_volume')}><span>Price match</span><b>{engine?.price_factor??none}</b><span>Volume match</span><b>{engine?.volume_factor??none}</b></div>
      <small>{engine?.factor_scope??none}<br/>{engine?.factor_interval??none}</small>
      <div className="engine-effective">{game.face.legs.map(side=><span key={side} title={source(row,'pool_cascade.sides.'+side+'.layers.STEP-FORECAST')}><b>{side} {row?.legs[side]?.display?.step_effective??'—'}</b><small>{row?.legs[side]?.display?.step_status??none}</small></span>)}</div>
      <small title={source(row,`Last-move agreement in the movement monitor, not confidence in the price-setting call. ${engine?.validity_reason??none}`)}>Last-move agreement · {engine?.validity??'not rated'}</small>
    </div>
    <div className="engine-execution"><div className="engine-label">BID-SETTING CALL → SECURED</div><div>{game.face.legs.map(side=>{const order=executionAt(game,side,index);return <button key={side} onClick={()=>{if(order?.origin_receipt_index!=null)onReceipt(order.origin_receipt_index)}} title={order?`${order.source}\n${order.origin_clock} → ${order.clock}`:none}><small>{side} · {order?.status==='Filled'?'filled':order?.status==='Standing bid'?'resting':'no bid'}</small><b>{order?.q??'—'} → {order?.status==='Filled'?order.value:'not filled'}</b></button>})}</div><small>Book + pair checks apply before posting</small></div>
    <p className="engine-carried" title={source(row,engine?.source??none)}>Last recorded receipt · {row?.clock_label??none}</p>
  </aside>;
}
