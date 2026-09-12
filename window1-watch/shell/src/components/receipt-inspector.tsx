import { useEffect, useState } from "react";
import { loadReceipt, SILENT, type Receipt } from "@/lib/tune-tape";
// Branches are mounted on demand. No schema whitelist, array truncation or transformation.
function Tree({name,value}:{name:string;value:unknown}) {
  const [open,setOpen]=useState(false);
  if(value==null || typeof value!=="object") return <p title={name+" · exact stored value"}><span className="terminal-muted">{name}: </span>{value==null?SILENT:String(value)}</p>;
  return <details onToggle={e=>setOpen(e.currentTarget.open)}><summary>{name}</summary>{open?Object.entries(value).map(([k,v])=><Tree key={k} name={k} value={v}/>):null}</details>;
}
export function ReceiptInspector({receipt,onClose}:{receipt:Receipt|null;onClose?:()=>void}) {
  const [data,setData]=useState<Awaited<ReturnType<typeof loadReceipt>>|null>(null),[error,setError]=useState<string|null>(null);
  useEffect(()=>{setData(null);setError(null);if(!receipt?.detail_url)return;const c=new AbortController();loadReceipt(receipt.detail_url,c.signal).then(setData).catch(e=>{if(e.name!=="AbortError")setError(String(e))});return()=>c.abort()},[receipt]);
  return <section className="terminal-inspector" aria-label="Full receipt inspector">
    <h2>Receipt inspector / fixed panel</h2>
    <p title={receipt?.detail_url??SILENT}>{receipt?.receipt??"Select a receipt"}</p>
    {onClose?<button onClick={onClose}>Follow current receipt</button>:null}
    {!receipt?<p className="terminal-muted">Select a tape receipt, action or gap to inspect.</p>:<>
      <Tree name="Compact receipt · stored in face" value={receipt}/>
      {error?<p className="terminal-muted">STORE SILENT — full stage unavailable here. Local LAB serves its original stage file. {error}</p>:data?<>
        <Tree name="Decision index" value={data.inspector}/><Tree name="Source and provenance" value={data.source}/><Tree name="Full stage · every stored field" value={data.row}/>
      </>:receipt.detail_url?<p>Loading original stage…</p>:<p>STORE SILENT — no stage link.</p>}
    </>}
  </section>;
}
