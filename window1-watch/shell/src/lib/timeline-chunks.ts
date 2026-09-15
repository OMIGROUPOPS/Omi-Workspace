import type {BidAction,FaceData,Receipt} from './tune-tape';
export type Timeline = {schema:string;event:string;os_sha256:string;trace_sha256:string;
 receipt_columns:string[];marker_columns:string[];tick_storage:string;receipt_storage?:string;marker_storage?:string;
 chunks:{first:number;last:number;url:string;sha256_uncompressed:string;bytes_uncompressed:number}[]};
const pending=new WeakMap<FaceData,Map<string,Promise<void>>>();
function assign(row:Record<string,any>,field:string,value:unknown){
 const keys=field.split('.');let target=row;
 for(const k of keys.slice(0,-1))target=target[k]??={};
 target[keys.at(-1)!]=value;
}
export function decodeTimelinePreview(face:FaceData){
 const t=face.timeline;if(!t)return;
 if(t.schema!=='face-timeline-v1'||t.event!==face.provenance.event_id||t.os_sha256!==face.provenance.os_sha256||t.trace_sha256!==face.provenance.trace_sha256)throw new Error('Timeline binding mismatch');
 const transpose=(columns:unknown[][])=>(columns[0]??[]).map((_,i)=>columns.map(c=>c[i]));
 const receiptValues=face.os as unknown as unknown[][];
 face.os=(t.receipt_storage==='columns'?transpose(receiptValues):receiptValues).map(values=>{
  const row:Record<string,any>={legs:{},timeline_pending:true};
  t.receipt_columns.forEach((key,i)=>assign(row,key,values[i]));
  return row as Receipt;
 });
 for(const group of ['bid_actions','supersessions'] as const){
  const storedRows=(face.render[group]??[]) as unknown as unknown[][];
  const rows=t.marker_storage==='columns'?transpose(storedRows):storedRows;
  face.render[group]=rows.map((values,i)=>{
   const row:Record<string,any>={id:`timeline:${group}:${i}`,timeline_pending:true,details_lines:[],hover_lines:[]};
   t.marker_columns.forEach((key,j)=>assign(row,key,values[j]));
   for(const mode of ['play','inspection'])if(row.markers?.[mode])row.markers[mode].label=row.label;
   return row as BidAction;
  });
 }
 const columns=face.render.ticks;
 face.render.ticks=(columns[0]??[]).map((_,i)=>columns.map(c=>c[i]));
}
export async function loadTimelineReceipt(face:FaceData,index:number,signal?:AbortSignal){
 const t=face.timeline;if(!t||!face.os[index]?.timeline_pending)return;
 const d=t.chunks.find(c=>c.first<=index&&c.last>=index);
 if(!d||d.url!==`/data/${t.event}.timeline/${d.first}.json`)throw new Error('Missing timeline chunk');
 let map=pending.get(face);if(!map){map=new Map();pending.set(face,map)}
 if(!map.has(d.url)){
  const request=(async()=>{
   // A scrub can change callers while the same chunk is in flight. The shared
   // verified fetch completes; aborted callers simply do not update their view.
   const r=await fetch(d.url,{cache:'no-cache'});if(!r.ok)throw new Error(`Timeline HTTP ${r.status}`);
   const bytes=await r.arrayBuffer();
   const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('');
   if(hash!==d.sha256_uncompressed||bytes.byteLength!==d.bytes_uncompressed)throw new Error('Timeline hash mismatch');
   const c=JSON.parse(new TextDecoder().decode(bytes));
   for(const k of ['schema','event','os_sha256','trace_sha256'] as const)if(c[k]!==t[k])throw new Error('Timeline provenance mismatch');
   if(c.first!==d.first||c.last!==d.last||c.os.length!==d.last-d.first+1)throw new Error('Timeline range mismatch');
   const decode=(v:any):any=>v&&typeof v==='object'?('$ref'in v?c.dictionary[v.$ref]:Array.isArray(v)?v.map(decode):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]))):v;
   const rows=c.os.map(decode) as Receipt[];
   rows.forEach((row,i)=>{if(row.index!==d.first+i)throw new Error('Timeline receipt index mismatch')});
   rows.forEach(row=>{face.os[row.index]=row});
   for(const group of ['bid_actions','supersessions'] as const)for(const item of c.actions[group]){
    const action=item.value as BidAction;
    if(action.receipt_index<d.first||action.receipt_index>d.last||item.index>=face.render[group]!.length)throw new Error('Timeline action index mismatch');
    action.bid_detail_source=face.bid_card_details;action.details_lines??=[];action.hover_lines??=[];
    face.render[group]![item.index]=action;
   }
  })();
  map.set(d.url,request);request.catch(()=>map!.delete(d.url));
 }
 await map.get(d.url);
 if(signal?.aborted)throw new DOMException('Aborted','AbortError');
}
