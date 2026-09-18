import type {FaceData} from './tune-tape';
import {loadTimelineReceipt} from './timeline-chunks';
// Three stored landmarks of one replay. Indices only: nothing here reads a
// price or decides anything. A landmark the replay never reached is null.
export type JumpTargets = {firstBid:number|null; firstFill:number|null; bell:number|null};
const earliest = (indices:number[]) => indices.length ? Math.min(...indices) : null;
export function jumpTargets(face:FaceData):JumpTargets {
  return {
    firstBid: earliest(face.render.bid_actions.filter(a=>a.kind==='PLACE'&&Number.isInteger(a.receipt_index)).map(a=>a.receipt_index)),
    firstFill: earliest(face.render.fill_events.map(f=>f.receipt_index).filter(Number.isInteger)),
    bell: face.os.length ? face.os.length-1 : null,
  };
}
// Warm the verified renewal chunks holding the three landmarks so a jump lands
// without the loading pause. Same hash-checked loader as a scrub; a failed
// preload is silent here and is reported by the normal path if the user jumps.
export function preloadJumpTargets(face:FaceData, signal?:AbortSignal):Promise<boolean> {
  const indices=[...new Set(Object.values(jumpTargets(face)).filter((i):i is number=>i!=null&&face.os[i]?.timeline_pending===true))];
  if(!indices.length)return Promise.resolve(false);
  return Promise.all(indices.map(i=>loadTimelineReceipt(face,i,signal))).then(()=>true,()=>false);
}
