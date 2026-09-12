import { useCallback, useEffect, useRef, useState } from "react";
import { loadGameIndex, loadTuneGame } from "@/lib/tape";
import { frameForReceipt, type Game, type LoadedGame } from "@/lib/tune-tape";
import { LabReading } from "./lab-reading";
import { DeskPanel } from "./desk-panel";
import { ScoreboardPanel } from "./scoreboard-panel";
import "../tune-motion.css";
import "../terminal.css";
type Tab="lab"|"desk"|"scoreboard";
export function TuneTest() {
  const importedUrls=useRef<string[]>([]);
  useEffect(()=>()=>importedUrls.current.forEach(url=>URL.revokeObjectURL(url)),[]);
  const [games,setGames]=useState<Game[]>([]),[event,setEvent]=useState<string|null>(null),[game,setGame]=useState<LoadedGame|null>(null);
  const [tab,setTab]=useState<Tab>(()=>{const t=new URLSearchParams(location.search).get("tab");return t==="desk"||t==="scoreboard"?t:"lab"});
  const [error,setError]=useState<string|null>(null),[frame,setFrame]=useState(0),[playing,setPlaying]=useState(false),[inspected,setInspected]=useState<number|null>(null),[selectedReceipt,setSelectedReceipt]=useState<number|null>(null);
  useEffect(()=>{const c=new AbortController();loadGameIndex(c.signal).then(i=>{setGames(i.games);setEvent(new URLSearchParams(location.search).get("event")??i.games.find(g=>g.event.endsWith("ALTGAS"))?.event??i.games[0]?.event??null)}).catch(e=>{if(e.name!=="AbortError")setError(String(e))});return()=>c.abort()},[]);
  useEffect(()=>{if(!event||!games.length)return;const c=new AbortController();setGame(null);setPlaying(false);setInspected(null);setSelectedReceipt(null);setError(null);const entry=games.find(g=>g.event===event);
    if(!entry){setError("Unknown stored event: "+event);return}
    loadTuneGame(entry.url,c.signal).then(g=>{setGame(g);const raw=new URLSearchParams(location.search).get("gate");const gate=raw==null?null:Number(raw);setFrame(g.face.render.checkpoints.find(p=>p.minutesToBell===gate)?.frame??g.face.render.play_start_frame);(window as unknown as {TUNE_DATA:LoadedGame}).TUNE_DATA=g;const u=new URL(location.href);u.searchParams.set("event",event);history.replaceState(null,"",u)}).catch(e=>{if(e.name!=="AbortError")setError(String(e))});return()=>c.abort();
  },[event,games]);
  useEffect(()=>{if(!playing||!game||tab!=="lab")return;const timer=setTimeout(()=>{const index=selectedReceipt??game.frames[frame]?.receipt_index;const next=game.face.os.find(r=>index==null||r.index>index);if(next){setFrame(frameForReceipt(game.frames,next));setSelectedReceipt(next.index)}else{setPlaying(false);setFrame(game.frames.length-1)}},700);return()=>clearTimeout(timer)},[playing,game,frame,selectedReceipt,tab]);
  const selectFrame=useCallback((n:number)=>{setFrame(n);setSelectedReceipt(null);setInspected(null)},[]);
  const inspect=useCallback((n:number)=>{setInspected(n);setPlaying(false)},[]);
  const closeInspector=useCallback(()=>setInspected(null),[]);
  const changeTab=(t:Tab)=>{setTab(t);setPlaying(false);const u=new URL(location.href);u.searchParams.set("tab",t);history.replaceState(null,"",u)};
  const now=game?.frames[frame],receiptIndex=selectedReceipt??now?.receipt_index??null,receipt=game&&receiptIndex!=null?game.face.os[receiptIndex]:null;
  useEffect(()=>{if(!game||!now)return;const u=new URL(location.href);const gate=game.face.render.checkpoints.find(c=>c.frame===frame);if(gate)u.searchParams.set("gate",String(gate.minutesToBell));else u.searchParams.delete("gate");history.replaceState(null,"",u)},[frame,game]);
  useEffect(()=>{const key=(e:KeyboardEvent)=>{if(e.ctrlKey||e.metaKey||e.altKey||(e.target instanceof HTMLElement&&e.target.closest("input,select,textarea,button,summary,[contenteditable]")))return;
    if(e.key==="/"){e.preventDefault();document.getElementById("load-game")?.focus()}
    if(e.key.toLowerCase()==="g"){e.preventDefault();document.getElementById("gate-jump")?.focus()}
    if(e.key===" "&&tab==="lab"&&now&&!now.pre_first_tick){e.preventDefault();setPlaying(p=>!p)}
    if((e.key==="["||e.key==="]")&&games.length){const i=games.findIndex(g=>g.event===event);setEvent(games[(i+(e.key==="]"?1:-1)+games.length)%games.length].event)}
    if(e.key==="Escape")setInspected(null);
    if((e.key==="ArrowLeft"||e.key==="ArrowRight")&&game&&tab==="lab"){e.preventDefault();const next=e.key==="ArrowRight"?game.face.os.find(r=>receiptIndex==null||r.index>receiptIndex):[...game.face.os].reverse().find(r=>receiptIndex!=null&&r.index<receiptIndex);if(next){setFrame(frameForReceipt(game.frames,next));setSelectedReceipt(next.index);setInspected(null);setPlaying(false)}}
  };document.addEventListener("keydown",key);return()=>document.removeEventListener("keydown",key)},[tab,now,game,games,event,receiptIndex]);
  async function importFace(file:File){
    let url:string|undefined;
    try {
      const raw=JSON.parse(await file.text());
      if(raw.version!==2||!/^KX[A-Z0-9-]+$/.test(raw.provenance?.event_id))throw Error("Choose a built .face.json with an event and OS/trace provenance");
      if(/SEALED|HOLDOUT|LIVE_PAPER/.test(JSON.stringify(raw.provenance)))throw Error("This source class is excluded from LAB imports");
      if(!raw.provenance.os_sha256||!raw.provenance.trace_sha256)throw Error("Missing OS or trace binding");
      url=URL.createObjectURL(file);const imported=await loadTuneGame(url);
      const reviewed=games.some(g=>g.event===raw.provenance.event_id)&&imported.grade_status==="OK";
      if(!reviewed&&!["LIBRARY","TUNE_SAMPLE"].includes(raw.provenance.source_class??raw.provenance.cohort))throw Error("Unreviewed import needs explicit LIBRARY or TUNE_SAMPLE provenance");
      const entry:Game={event:raw.provenance.event_id,category:raw.category??null,os_sha:raw.provenance.os_sha256,trace_sha:raw.provenance.trace_sha256,url,version:raw.version};
      importedUrls.current.push(url);setGames(previous=>[...previous.filter(g=>g.event!==entry.event),entry]);setEvent(entry.event);setError(null);
    }catch(e){if(url)URL.revokeObjectURL(url);setError(String(e))}
  }
  return <main className={`terminal ${tab==="lab"?"reading-terminal":""}`}>
    <header className="terminal-header"><strong>WINDOW-1 WATCH</strong><nav aria-label="Terminal tabs">{(["lab","desk","scoreboard"] as Tab[]).map(t=><button key={t} aria-current={tab===t?"page":undefined} onClick={()=>changeTab(t)}>{t.toUpperCase()}</button>)}</nav><span className={tab==="desk"?"terminal-fault":"terminal-muted"}>{tab==="desk"?"PAPER / DISCONNECTED":"STORED REPLAY / NO ORDERS"}</span></header>
    {tab!=="lab"?<div className="terminal-tickers" aria-label="Game ticker strip">{games.map(g=><button key={g.event} title={g.event+" · OS "+g.os_sha} onClick={()=>{changeTab("lab");setEvent(g.event)}}>{g.event.split("-").at(-1)}</button>)}</div>:null}
    {tab==="lab"?<>
      {games.find(g=>g.event===event)?.url.startsWith("blob:")?<p className="terminal-muted">LOCAL PREPARED FACE / this file selection lasts until refresh; optional grade and oracle must match its hashes.</p>:null}
      {error?<p role="alert" className="terminal-fault">No data here — {error}</p>:null}
      {!game&&!error?<p>Loading verified face/grade/oracle…</p>:null}
      {game&&now?<LabReading game={game} games={games} event={event} frame={frame} receipt={receipt} receiptIndex={receiptIndex} playing={playing} inspected={inspected} onEvent={setEvent} onFrame={selectFrame} onPlaying={setPlaying} onReceipt={setSelectedReceipt} onInspect={inspect} onCloseInspector={closeInspector} onImport={file=>void importFace(file)}/>:null}
    </>:tab==="desk"?<DeskPanel/>:<ScoreboardPanel onGame={e=>{changeTab("lab");setEvent(e)}}/>}
    {tab!=="lab"?<footer>/ game search · [ ] switch game · G gate · Space play/pause · arrows receipt · Escape current inspector · LAB is research, not an order terminal</footer>:null}
  </main>;
}
