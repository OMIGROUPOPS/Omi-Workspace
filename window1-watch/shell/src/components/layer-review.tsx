import {useEffect,useState} from 'react';
import './layer-review.css';

type Status='PASS'|'FAIL'|'UNKNOWN';
type Layer='MACRO'|'MICRO'|'MICRO-MICRO';
type Review={key:string;label:string;clock:string;receipt:string|null;cells:Record<Layer,Record<'WHAT'|'WHY'|'HOW',string>>;
  legs:Record<string,{close:number|null;recorded_floor:number|null;role_right:boolean|null;micro:{remaining_floor_cents:number|null;floor_inside_band:boolean|null;later_band_print_by_deadline:boolean|null;missing_reason:string|null}}>};
type Funnel=Record<Layer,Status>&{exit:{layer:Layer|'ALL_THREE';status:Status;reason:string}};
type Arm={label:string;reviews:Review[];funnel:{first_callable:Funnel;last_before_outcomes:Funnel};fills_before_first_pair_callable:string[]};
type RecordData={schema:string;event:string;named_only:boolean;provenance:{D_os_sha256:string;D_trace_sha256:string;mirror_projection_sha256:string};arms:Record<string,Arm>};
const layers:Layer[]=['MACRO','MICRO','MICRO-MICRO'];
const statusText=(v:Status|boolean|null)=>v===true||v==='PASS'?'passed':v===false||v==='FAIL'?'not passed':'not known';
const exitText=(f:Funnel)=>f.exit.layer==='ALL_THREE'?'All three checks passed':`${f.exit.layer}: ${f.exit.status==='UNKNOWN'?'not enough recorded evidence':'first check not passed'}`;
const price=(v:number|null)=>v==null?'no data here':`${v}¢`;

export function LayerReview({event,chartTrace}:{event:string;chartTrace:string|null|undefined}) {
  const [data,setData]=useState<RecordData|null>(null),[error,setError]=useState<string|null>(null);
  const [arm,setArm]=useState('D'),[checkpoint,setCheckpoint]=useState('first-callable');
  useEffect(()=>{
    setData(null);setError(null);setArm('D');setCheckpoint('first-callable');
    const abort=new AbortController();
    (async()=>{
      const indexResponse=await fetch('/data/layer-review/index.json',{signal:abort.signal,cache:'no-cache'});
      if(!indexResponse.ok||!indexResponse.headers.get('content-type')?.includes('json'))throw new Error('Review data is not available here yet.');
      const index=await indexResponse.json(),entry=index.games?.find((g:{event:string})=>g.event===event);
      if(!entry)throw new Error('This game is outside the frozen 100 and the additional ALT/GAS check; no D/mirror review was run for it.');
      if(entry.url!==`/data/layer-review/${event}.json`)throw new Error('Review URL does not match this game.');
      const response=await fetch(entry.url,{signal:abort.signal,cache:'no-cache'});
      if(!response.ok)throw new Error('The game review could not be loaded.');
      const bytes=await response.arrayBuffer(),hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
      if(hash!==entry.sha256)throw new Error('Review hash does not match its index; no cells are shown.');
      const value=JSON.parse(new TextDecoder().decode(bytes)) as RecordData;
      if(value.schema!=='NINE_CELL_GAME_REVIEW_V1'||value.event!==event)throw new Error('Review belongs to another game or contract.');
      if(!abort.signal.aborted)setData(value);
    })().catch(e=>{if(e.name!=='AbortError'&&!abort.signal.aborted)setError(e.message)});
    return()=>abort.abort();
  },[event]);
  const policy=data?.arms[arm],card=policy?.reviews.find(r=>r.key===checkpoint)??policy?.reviews[0];
  return <section className="layer-review" aria-label="Three-layer game review" data-layer-review-event={event}>
    <header><div><small>GAME REVIEW · KNOWN AFTERWARD</small><h2>WHAT / WHY / HOW</h2></div>
      {data&&policy?<div className="layer-review-controls">
        <label>Policy <select aria-label="Review policy" value={arm} onChange={e=>{setArm(e.target.value);setCheckpoint('first-callable')}}>{Object.entries(data.arms).map(([key,value])=><option value={key} key={key}>{value.label}</option>)}</select></label>
        <label>Receipt <select aria-label="Review checkpoint" value={card?.key} onChange={e=>setCheckpoint(e.target.value)}>{policy.reviews.map(r=><option value={r.key} key={r.key}>{r.label} · {r.clock}</option>)}</select></label>
      </div>:null}
    </header>
    {!data?<p role="status">{error??'Loading the recorded review…'}</p>:<>
      <p className="layer-review-scope">Independent policy review—not a switch to the charts above. Mirror-reserve is a bench result, not installed.{data.named_only?' ALT/GAS is an extra named check, outside the 100-game totals.':''}</p>
      {chartTrace!==data.provenance.D_trace_sha256?<p className="layer-review-scope">The loaded chart uses a different trace; these cells explicitly review D and mirror-reserve.</p>:null}
      {policy&&card?<>
        <p className="layer-review-clock" title={card.receipt??'No matching saved receipt'}>{card.label} · <strong>{card.clock}</strong></p>
        <div className="layer-review-grid"><table><thead><tr><th scope="col">Layer</th><th scope="col">WHAT</th><th scope="col">WHY</th><th scope="col">HOW</th></tr></thead><tbody>
          {layers.map(layer=><tr key={layer}><th scope="row">{layer}</th>{(['WHAT','WHY','HOW'] as const).map(question=><td data-question={question} key={question}>{card.cells[layer][question]}</td>)}</tr>)}
        </tbody></table></div>
        <div className="layer-review-funnel" aria-label="Game funnel">
          <p><b>First callable:</b> {exitText(policy.funnel.first_callable)}<br/>{policy.funnel.first_callable.exit.reason}</p>
          <p><b>Last before each outcome:</b> {exitText(policy.funnel.last_before_outcomes)}<br/>{policy.funnel.last_before_outcomes.exit.reason}</p>
        </div>
        <details><summary>Checks, corrected rulers and receipt evidence</summary>
          <p>Both sides must pass each step. MICRO tests the strictly later floor against the stored middle-half range, plus a later positive print in that range by the saved deadline. The close is a separate ruler. MICRO-MICRO requires a credited fill strictly below close during that side’s permitted policy window, not a newly imposed deadline rule.</p>
          {Object.entries(card.legs).map(([side,l])=><p key={side}><b>{side}</b> · corrected close {price(l.close)} · full-span floor {price(l.recorded_floor)} · later floor {price(l.micro.remaining_floor_cents)} · direction {statusText(l.role_right)} · floor in range {statusText(l.micro.floor_inside_band)} · later print by deadline {statusText(l.micro.later_band_print_by_deadline)}{l.micro.missing_reason?` · ${l.micro.missing_reason}`:''}</p>)}
          {policy.fills_before_first_pair_callable.length?<p>Already filled before the first joint call: {policy.fills_before_first_pair_callable.join(', ')}; this funnel is a fixed-checkpoint review, not an asserted causal sequence.</p>:null}
          <p>D OS {data.provenance.D_os_sha256} · trace {data.provenance.D_trace_sha256}<br/>Mirror result {data.provenance.mirror_projection_sha256}</p>
          <a href={`/data/layer-review/${event}.json`} target="_blank" rel="noreferrer">Full game review and bid permissions</a>{' · '}
          <a href="/data/layer-review/REPORT.json" target="_blank" rel="noreferrer">All 100 games and funnel</a>{' · '}
          <a href="/data/layer-review/CONTRACT.json" target="_blank" rel="noreferrer">Review definitions</a>
        </details>
      </>:null}
    </>}
  </section>;
}
