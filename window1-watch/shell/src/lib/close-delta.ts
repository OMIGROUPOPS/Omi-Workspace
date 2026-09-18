import type {Grade} from './tune-tape';
// Reading of the stored W1 close-delta ruler. The builder wrote every number
// (grade.handoff_close_result, grade.close_delta_grade); this only signs and
// labels them. No cent is added, subtracted or compared against a cutoff here.
const RULE='Credited per-leg corrected W1 close minus fill; unfilled value zero. Numeric mark, not a letter.';
export type CloseDeltaReading = {mark:string; status:string; rule:string; builder_written:boolean};
export const signedCents = (value:number|null|undefined) =>
  typeof value==='number'&&Number.isFinite(value) ? `${value>0?'+':''}${Number(value.toFixed(2))}¢` : 'no data here';
export function closeDeltaReading(grade:Grade|null|undefined):CloseDeltaReading|null {
  const result=grade?.handoff_close_result; if(!grade||!result)return null;
  const stored=grade.close_delta_grade;
  if(stored)return {mark:signedCents(stored.score_cents),status:stored.status.toLowerCase(),rule:(stored as {rule?:string}).rule??RULE,builder_written:true};
  // Grades built before the builder wrote close_delta_grade still store the same ruler value.
  return {mark:signedCents(result.filled_leg_close_delta_cents),
    status:grade.OUTCOME?.valid_pair_completed?'pair complete':'pair incomplete',
    rule:RULE,builder_written:false};
}
// Header mark: the floor-only letter is inapplicable (N/A) exactly where the close-delta ruler applies.
export function headlineGrade(grade:Grade|null|undefined):string {
  const letter=grade?.display.letter??'—';
  return letter==='N/A' ? closeDeltaReading(grade)?.mark??letter : letter;
}
