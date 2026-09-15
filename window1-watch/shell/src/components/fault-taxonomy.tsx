import {useEffect,useState} from 'react';
import type {Game} from '@/lib/tune-tape';
export type FaultRecord={schema:string;event:string;header:string;classes:string[];known_span:boolean;provenance:{os_sha256:string;trace_sha256:string;face_sha256:string};credit:{pair_completed:boolean|null;pair_sum:number|null;captured_cents:number|null;best_capturable_cents:number|null;safety_excluded:boolean;note:string};sides:{leg:string;classes:string[];A:Record<string,any>[];B:Record<string,any>|null;C:Record<string,any>[];D:Record<string,any>|null;E:Record<string,any>|null}[]};
export function useFaultTaxonomy(entry:Game|undefined){
 const [fault,setFault]=useState<FaultRecord|null>(null);
 useEffect(()=>{setFault(null);if(!entry)return;const abort=new AbortController();
  fetch(`/data/tune-expansion/faults/${entry.event}.json`,{signal:abort.signal,cache:'no-cache'}).then(async r=>r.ok&&r.headers.get('content-type')?.includes('application/json')?r.json():null).then((value:FaultRecord|null)=>{
   if(value?.schema==='TUNE_FAULT_TAXONOMY_V1'&&value.event===entry.event&&value.provenance.os_sha256===entry.os_sha&&value.provenance.trace_sha256===entry.trace_sha)setFault(value);
  }).catch(e=>{if(e.name!=='AbortError')console.warn('Fault audit unavailable',entry.event)});return()=>abort.abort();
 },[entry?.event,entry?.os_sha,entry?.trace_sha]);
 return fault;
}
export function FaultBanner({fault}:{fault:FaultRecord|null}){
 if(!fault)return null;
 return <section className="fault-audit" data-fault-event={fault.event} aria-label="Fault classification">
  <details><summary><small>REPLAY FAULTS · KNOWN AFTERWARD</small> <strong>{fault.header}</strong></summary>
   <p>{fault.credit.note} Labels can overlap; they explain failed sides, not successfully filled partners. No label means no failed side, not a perfect sentence.</p>
   {fault.sides.map(side=><div key={side.leg}><b>{side.leg}</b>
    {side.A.length?<p>A · First offending bid {side.A[0].bid_cents}¢; recorded floor {side.A[0].recorded_floor_cents??'unknown'}¢; floor minus placement {side.A[0].floor_minus_placement_minutes?.toFixed(2)??'unknown'} min (negative = floor came first); call then {side.A[0].Q_at_placement??'unknown'}¢.</p>:null}
    {side.B?<p>B · First eligible call {side.B.Q}¢; floor {side.B.floor}¢; pool of {side.B.member_count} games; effective count {side.B.ess.toFixed(2)}. Role {side.B.role_at_call}; realized {side.B.realized_role??'unknown'}.</p>:null}
    {side.C.length?<p>C · Stored safety failure. This side's fill receives no credit.</p>:null}
    {side.D?<p>D · {side.D.positive_prints} positive prints; this tour's bottom-decile cutoff is fewer than {side.D.N}.</p>:null}
    {side.E?<p>E · {side.E.reason}</p>:null}
   </div>)}
   <a href={`/data/tune-expansion/faults/${fault.event}.json`} target="_blank" rel="noreferrer">All evidence, placements and top-five pool members</a>
  </details>
 </section>;
}
