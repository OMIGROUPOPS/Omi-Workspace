// src/lib/tape.ts — Window-1 Watch data layer.
// SAME EXPORTS the shell components already import. Every value comes from data/altgas.face.json
// (contract: window1-watch/FIELDS.md, produced by export_watch.mjs + build_face_data.mjs from the OS trace
// and the custody tapes). No anchors, no mirrors, no synthetic spread, no hand-written beats.
// A value with no store is null. Text is assembled only from stored fields and numbers.

export type Side = "ALT" | "GAS";

export type Beat = {
  id: string;
  hours: number;
  title: string;
  whatHappened: string;
  whyTheBidMoved: string;
  cited: string;
  altRest: number | null;
  gasRest: number | null;
  survivors: number;
  brain: "blank" | "guess" | "writing" | "holding";
  heart: "still" | "weak" | "steady" | "hard";
  pileAlive: boolean;
  hand: "idle" | "posting" | "pulling" | "holding";
  sentence: string;
};

export type Tick = {
  hours: number;
  hoursLeft: number;
  altLast: number | null;
  altBid: number | null;
  altAsk: number | null;
  altRest: number | null;
  gasLast: number | null;
  gasBid: number | null;
  gasAsk: number | null;
  gasRest: number | null;
};

// ---- face.json shapes (as written by build_face_data.mjs; see FIELDS.md) ----
type TapeRow = { t: number; bid: number | null; ask: number | null; last: number | null };
type Sentence = {
  status?: string | null; P?: number | null; Q?: number | null; X?: number | null;
  q_author?: string | null; x_author?: string | null; plain_sentence?: string | null;
};
type LegState = {
  bid?: number | null; ask?: number | null; running_low?: number | null; survivors?: number | null;
  sentence?: Sentence | null;
  action?: { name?: string | null; target_cents?: number | null; reason?: string | null } | null;
  rest?: { action?: string | null; cents?: number | null; lane?: string | null; mode?: string | null } | null;
  print?: { cents?: number | null } | null;
  fill?: { cents?: number | null } | null;
};
type OsRow = { t: number; receipt?: string | null; kind?: string | null; legs: Partial<Record<Side, LegState>> };
export type FaceData = {
  provenance?: { event_id?: string; trace_sha256?: string; os_sha256?: string };
  bell?: { t?: number; source?: string };
  tape: Partial<Record<Side, TapeRow[]>>;
  os: OsRow[];
};

// ---- live state (filled by initTape; arrays are mutated in place so existing imports see the data) ----
export let WINDOW_HOURS_TOTAL = 0;
export const TICKS: Tick[] = [];
export const BEATS: Beat[] = [];
export let PROVENANCE: FaceData["provenance"] = {};
let OS: OsRow[] = [];
let READY = false;
export function isReady() { return READY; }

const r1 = (n: number) => Math.round(n * 10) / 10;
const cents = (v: number | null | undefined) => (v === null || v === undefined ? "STORE SILENT" : `${v}¢`);
const firstClause = (s: string | null | undefined, max = 160) => {
  if (!s) return "";
  const cut = s.indexOf("[");
  const head = cut > 0 ? s.slice(0, cut).trim() : s;
  return head.length > max ? head.slice(0, max - 1) + "…" : head;
};

// rest state per leg as the OS wrote it: set on PLACE_REST/REPRICE_REST, cleared on FILL_EVENT for that leg.
// (No stand-down action exists in the export — FIELDS.md marks it STORE SILENT — so a rest persists until fill or bell.)
function restTimeline(side: Side): Array<{ t: number; rest: number | null }> {
  const out: Array<{ t: number; rest: number | null }> = [];
  let rest: number | null = null;
  for (const row of OS) {
    const leg = row.legs?.[side];
    if (!leg) continue;
    const a = String(leg.rest?.action ?? "").toUpperCase();
    if ((a === "PLACE_REST" || a === "REPRICE_REST") && typeof leg.rest?.cents === "number") rest = leg.rest.cents;
    if (String(row.kind ?? "").toUpperCase().includes("FILL") && leg.fill && typeof leg.fill.cents === "number") rest = null;
    out.push({ t: row.t, rest });
  }
  return out;
}
function restAt(timeline: Array<{ t: number; rest: number | null }>, hours: number): number | null {
  let rest: number | null = null;
  for (const p of timeline) { if (p.t <= hours + 1e-9) rest = p.rest; else break; }
  return rest;
}
function lastAtOrBefore(rows: TapeRow[], hours: number): TapeRow | null {
  let best: TapeRow | null = null;
  for (const row of rows) { if (row.t <= hours + 1e-9) best = row; else break; }
  return best;
}

export function initTape(face: FaceData) {
  OS = Array.isArray(face.os) ? [...face.os].sort((a, b) => a.t - b.t) : [];
  PROVENANCE = face.provenance ?? {};
  const alt = (face.tape?.ALT ?? []).slice().sort((a, b) => a.t - b.t);
  const gas = (face.tape?.GAS ?? []).slice().sort((a, b) => a.t - b.t);
  WINDOW_HOURS_TOTAL = typeof face.bell?.t === "number" ? face.bell.t
    : Math.max(alt.at(-1)?.t ?? 0, gas.at(-1)?.t ?? 0, OS.at(-1)?.t ?? 0);

  const altRests = restTimeline("ALT");
  const gasRests = restTimeline("GAS");

  // time grid = every change point on either tape + every OS receipt, so nothing the OS did falls between samples
  const times = new Set<number>([0, WINDOW_HOURS_TOTAL]);
  for (const r of alt) times.add(r.t);
  for (const r of gas) times.add(r.t);
  for (const r of OS) times.add(r.t);

  TICKS.length = 0;
  for (const h of [...times].filter((t) => t >= 0 && t <= WINDOW_HOURS_TOTAL).sort((a, b) => a - b)) {
    const a = lastAtOrBefore(alt, h), g = lastAtOrBefore(gas, h);
    TICKS.push({
      hours: h,
      hoursLeft: Math.max(0, WINDOW_HOURS_TOTAL - h),
      altLast: a?.last ?? null, altBid: a?.bid ?? null, altAsk: a?.ask ?? null, altRest: restAt(altRests, h),
      gasLast: g?.last ?? null, gasBid: g?.bid ?? null, gasAsk: g?.ask ?? null, gasRest: restAt(gasRests, h),
    });
  }

  // beats: one per OS receipt where something the face shows changed — sentence status, Q, survivors, rest, fill
  BEATS.length = 0;
  let prev: Record<Side, { status: string; q: number | null; surv: number | null; rest: number | null }> = {
    ALT: { status: "", q: null, surv: null, rest: null }, GAS: { status: "", q: null, surv: null, rest: null },
  };
  let altRest: number | null = null, gasRest: number | null = null;
  OS.forEach((row, i) => {
    const changes: string[] = [];
    const lines: string[] = [];
    const why: string[] = [];
    const cited: string[] = [];
    let posted = false, filled = false;
    for (const side of ["ALT", "GAS"] as Side[]) {
      const leg = row.legs?.[side]; if (!leg) continue;
      const s = leg.sentence ?? {};
      const status = String(s.status ?? "");
      const q = typeof s.Q === "number" ? s.Q : null;
      const surv = typeof leg.survivors === "number" ? leg.survivors : null;
      const a = String(leg.rest?.action ?? "").toUpperCase();
      const isFill = String(row.kind ?? "").toUpperCase().includes("FILL") && typeof leg.fill?.cents === "number";
      if (a === "PLACE_REST" || a === "REPRICE_REST") {
        posted = true;
        if (side === "ALT") altRest = leg.rest?.cents ?? null; else gasRest = leg.rest?.cents ?? null;
        changes.push(`${side} ${a === "PLACE_REST" ? "rest" : "reprice"} ${cents(leg.rest?.cents)}`);
        why.push(`${side} ${a} ${cents(leg.rest?.cents)} via ${leg.rest?.lane ?? "STORE SILENT"} (${leg.rest?.mode ?? "STORE SILENT"})`);
      }
      if (isFill) {
        filled = true;
        if (side === "ALT") altRest = null; else gasRest = null;
        changes.push(`${side} filled ${cents(leg.fill?.cents)}`);
        why.push(`${side} FILL_EVENT at ${cents(leg.fill?.cents)}`);
      }
      if (status && status !== prev[side].status) changes.push(`${side} sentence ${status}`);
      if (q !== prev[side].q && q !== null) changes.push(`${side} Q ${cents(prev[side].q)} → ${cents(q)}`);
      if (surv !== prev[side].surv && surv !== null) changes.push(`${side} leftovers ${prev[side].surv ?? "?"} → ${surv}`);
      if (status === "RESOLVED" || s.plain_sentence) {
        lines.push(`${side}: ${firstClause(s.plain_sentence) || status} (P ${cents(s.P)} · Q ${cents(s.Q)} · X ${s.X ?? "STORE SILENT"})`);
      } else if (status) {
        lines.push(`${side}: ${status}`);
      }
      if (s.q_author || s.x_author) cited.push(`${side} Q by ${s.q_author ?? "STORE SILENT"}, X by ${s.x_author ?? "STORE SILENT"}`);
      prev[side] = { status, q, surv, rest: side === "ALT" ? altRest : gasRest };
    }
    if (changes.length === 0 && i !== 0) return;

    const altLeg = row.legs?.ALT, gasLeg = row.legs?.GAS;
    const altStatus = String(altLeg?.sentence?.status ?? "");
    const altSurv = typeof altLeg?.survivors === "number" ? altLeg.survivors : 0;
    const qAuthor = String(altLeg?.sentence?.q_author ?? gasLeg?.sentence?.q_author ?? "");
    const brain: Beat["brain"] = !altStatus || altStatus === "INSUFFICIENT_EVIDENCE" ? "blank"
      : qAuthor.includes("REWEIGHTED") ? "writing" : qAuthor.includes("PRIOR") ? "guess" : "holding";
    const hand: Beat["hand"] = posted ? "posting" : (altRest !== null || gasRest !== null) ? "holding" : "idle";
    const heart: Beat["heart"] = filled ? "hard" : posted ? "steady" : (altRest !== null && gasRest !== null) ? "steady" : (altRest !== null || gasRest !== null) ? "weak" : "still";

    BEATS.push({
      id: row.receipt ? String(row.receipt) : `os-${i}`,
      hours: r1(row.t),
      title: `${String(row.kind ?? "OS").replace(/_/g, " ").toLowerCase()} · ${changes[0] ?? "receipt"}`,
      whatHappened: changes.join(" · ") || "receipt with no change on either leg",
      whyTheBidMoved: why.join(" · ") || "no PLACE/REPRICE on this receipt",
      cited: cited.join(" · ") || "STORE SILENT",
      altRest, gasRest,
      survivors: altSurv,
      brain, heart,
      pileAlive: altSurv > 0,
      hand,
      sentence: lines.join("  |  ") || "STORE SILENT",
    });
  });
  if (BEATS.length === 0) {
    BEATS.push({ id: "none", hours: 0, title: "no OS receipts", whatHappened: "STORE SILENT", whyTheBidMoved: "STORE SILENT", cited: "STORE SILENT",
      altRest: null, gasRest: null, survivors: 0, brain: "blank", heart: "still", pileAlive: false, hand: "idle", sentence: "STORE SILENT" });
  }
  READY = true;
}

export async function loadTape(url = "/data/altgas.face.json"): Promise<FaceData> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`face data ${url}: ${res.status}`);
  const face = (await res.json()) as FaceData;
  initTape(face);
  return face;
}

// ---- API the components call (unchanged names) ----
export function visibleTicks(hours: number): Tick[] {
  const rows = TICKS.filter((t) => t.hours <= hours + 0.01);
  return rows.length > 0 ? rows : TICKS.slice(0, 1);
}
export function hoursRemaining(hours: number) { return Math.max(0, WINDOW_HOURS_TOTAL - hours); }
export function beatAtHours(hours: number): Beat {
  let current = BEATS[0];
  for (const beat of BEATS) if (hours + 0.01 >= beat.hours) current = beat;
  return current;
}
export function tickNear(hours: number): Tick {
  let best = TICKS[0], dist = Infinity;
  for (const tick of TICKS) { const d = Math.abs(tick.hours - hours); if (d < dist) { dist = d; best = tick; } }
  return best;
}

export type Engagement = {
  altLast: number | null; gasLast: number | null; altRest: number | null; gasRest: number | null;
  altBidChanges: number; gasBidChanges: number; altTapeSinceSit: number; gasTapeSinceSit: number;
  hoursHeld: number; frozen: boolean; headline: string; body: string;
};

export function engagementAt(hours: number): Engagement {
  const now = tickNear(hours);
  let altBidChanges = 0, gasBidChanges = 0, altSitAt: number | null = null, gasSitAt: number | null = null, fills: string[] = [];
  for (const row of OS) {
    if (row.t > hours + 1e-9) break;
    for (const side of ["ALT", "GAS"] as Side[]) {
      const leg = row.legs?.[side]; if (!leg) continue;
      const a = String(leg.rest?.action ?? "").toUpperCase();
      if (a === "PLACE_REST" || a === "REPRICE_REST") { if (side === "ALT") { altBidChanges++; altSitAt = row.t; } else { gasBidChanges++; gasSitAt = row.t; } }
      if (String(row.kind ?? "").toUpperCase().includes("FILL") && typeof leg.fill?.cents === "number") fills.push(`${side} ${leg.fill.cents}¢ at ${r1(row.t)}h`);
    }
  }
  const altTapeSinceSit = now.altRest !== null && now.altLast !== null ? now.altLast - now.altRest : 0;
  const gasTapeSinceSit = now.gasRest !== null && now.gasLast !== null ? now.gasLast - now.gasRest : 0;
  const hoursHeld = now.altRest !== null && altSitAt !== null ? Math.max(0, hours - altSitAt) : 0;
  const frozen = now.altRest !== null && hoursHeld > 1;

  // headline and body are numbers from the data, not narrative
  let headline: string, body: string;
  if (now.altRest === null && now.gasRest === null && fills.length === 0) {
    headline = "No bid on the book.";
    body = `ALT last ${cents(now.altLast)} · GAS last ${cents(now.gasLast)}. No PLACE_REST yet on either leg.`;
  } else {
    const parts: string[] = [];
    if (now.altRest !== null) parts.push(`ALT rest ${now.altRest}¢, tape ${cents(now.altLast)}, ${altTapeSinceSit >= 0 ? "+" : ""}${altTapeSinceSit}¢ from the rest, held ${r1(hoursHeld)}h`);
    if (now.gasRest !== null) parts.push(`GAS rest ${now.gasRest}¢, tape ${cents(now.gasLast)}, ${gasTapeSinceSit >= 0 ? "+" : ""}${gasTapeSinceSit}¢ from the rest`);
    if (fills.length) parts.push(`filled: ${fills.join(", ")}`);
    headline = frozen ? `ALT rest unchanged ${r1(hoursHeld)}h while the tape is ${cents(now.altLast)}.` : fills.length ? `Filled: ${fills[fills.length - 1]}.` : "Rest on the book.";
    body = `${parts.join(" · ")} · bid changes so far: ALT ${altBidChanges}, GAS ${gasBidChanges}.`;
  }
  return { altLast: now.altLast, gasLast: now.gasLast, altRest: now.altRest, gasRest: now.gasRest, altBidChanges, gasBidChanges, altTapeSinceSit, gasTapeSinceSit, hoursHeld, frozen, headline, body };
}
