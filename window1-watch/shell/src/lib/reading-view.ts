import type { BidAction, Receipt } from './tune-tape';

// Display formatting only. Q, X, authorship, grade and ruler values are never recomputed.
export const plain = (value: string | null | undefined) => value?.replaceAll('STORE SILENT', 'no data here') ?? 'no data here';
export const cents = (value: number | null | undefined) => value == null ? 'no data here' : `${value}¢`;
export function replayClock(minutes:number|null|undefined) {
  if(minutes==null||!Number.isFinite(minutes))return 'no time recorded';
  const rounded=Math.round(Math.abs(minutes));
  return `T ${minutes<0?'+':'-'} ${Math.floor(rounded/60)}hr ${rounded%60} min`;
}
export function bellTime(minutes: number | null | undefined) {
  if (minutes == null || !Number.isFinite(minutes)) return 'no time recorded';
  const rounded = Math.round(Math.abs(minutes));
  return `${minutes < 0 ? '−' : ''}${Math.floor(rounded / 60)}:${String(rounded % 60).padStart(2, '0')}`;
}
export type Sentence = { status?: string; P?: number | null; Q?: number | null; X?: number | null };
export function readingSentence(sentence?: Sentence) {
  if (!sentence || sentence.Q == null) return 'No forecast here yet.';
  if (sentence.status !== 'RESOLVED') return 'Not enough evidence for a new bid.';
  return `Believes ${cents(sentence.Q)} by ${bellTime(sentence.X)} to the bell.`;
}
export function sentenceFor(receipt: Receipt | null, side: string): Sentence | undefined {
  return (receipt?.legs[side] as { sentence?: Sentence } | undefined)?.sentence;
}
export type ReadingAction = BidAction & {
  marker_cents?: number | null;
  minutes_to_bell?: number;
  sentence?: Sentence;
  bid_accountability?: { assumption?: { Q?: number; X_minutes_to_bell?: number; member_count?: number }; renewal?: { status?: string } };
};
// Existing plain-English bid cards remain authoritative. Only the supersession
// card needs a jargon-free front; the original tokens stay in its Details.
export function readingCard(action: ReadingAction): string[] {
  if (action.kind !== 'SUPERSESSION') return action.card_lines.map(plain);
  const assumption = action.bid_accountability?.assumption;
  const status = action.bid_accountability?.renewal?.status;
  const renewal = status === 'PENDING' ? 'promise pending' : status === 'FULFILLED' ? 'promise reached' : status === 'MISSED_AT_DEADLINE' ? 'deadline missed' : 'no renewal data here';
  return [
    plain(action.card_lines[0]), plain(action.card_lines[1]),
    assumption ? `Believed: ${cents(assumption.Q)} by ${bellTime(assumption.X_minutes_to_bell)} to bell · ${renewal}` : 'No promise recorded here.',
    `${assumption?.member_count == null ? 'No pool count here' : `Pool of ${assumption.member_count} games`} · ${bellTime(action.minutes_to_bell)} to bell`,
  ];
}
