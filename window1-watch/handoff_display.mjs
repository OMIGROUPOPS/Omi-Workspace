// Display labels only. The OS supplies both destinations and entry permissions.
import {entryFee} from './attribution/tennis_fees.mjs';
const cents = v => Number.isFinite(v) ? `${v}¢` : 'no data here';
export function handoffDisplay(belief) {
  const p = belief?.entry_license, h = belief?.handoff ?? p;
  if (!h) return null;
  const kind = h.destination_kind === 'W1_CLOSE' ? 'close' : h.destination_kind === 'REMAINING_FLOOR' ? 'floor' : null;
  const choice = p?.pair_entry, table = choice?.level_table;
  const number = value => Number.isFinite(value) ? new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(value) : 'no data here';
  const levelTable = table?.map(row=>({level:`${number(row.level_cents)}¢`,
    reach:Number.isFinite(row.probability)?`${number(row.probability*100)}%`:'no data here',
    discount:`${number(row.pair_discount_cents)}¢`,expected:`${number(row.expected_pair_discount_cents)}¢`,
    choice:row.level_cents===choice.chosen_level_cents?(p.allowed?'chosen':'best · waiting'):row.eligible?'alternative':'blocked',
    licensed:p.allowed&&row.level_cents===choice.chosen_level_cents,
    source:`Raw probability ${row.raw_probability}; calibrated ${row.probability}; discount ${row.pair_discount_cents}; expected ${row.expected_pair_discount_cents}; ${row.blocked_reason??'eligible'}; endpoint clipped ${row.calibration_endpoint_clipped}`}));
  return {
    destination_kind: h.destination_kind,
    destination_cents: h.destination_cents,
    entry_cents: p?.allowed === true ? p.entry_cents : null,
    destination_line: `Destination: ${cents(h.destination_cents)}${kind ? ` ${kind}` : ''}`,
    entry_line: p?.allowed === true ? `Entry: ${cents(p.entry_cents)} licensed` : `Entry: none${p?.waiting_reason === 'already filled' ? ' — already filled' : ' — waiting'}`,
    reason_line: table ? p.allowed ? `Reason: ${number(p.entry_cents)}¢ has the greatest estimated pair discount (${number(choice.chosen_expected_discount_cents)}¢); maker-only and under par.`
      : `Reason: waiting — ${p.waiting_reason??'no data here'}.` : `Reason: ${p?.written_reason ?? 'no data here'}`,
    ...(table?{level_table:levelTable,raw_reason:p.written_reason,
      reach_note:`Positive print before bell · ${number(choice.reach?.calibration_training_games)} earlier calibration games · latest calibration T−${number(choice.reach?.calibration_gate_minutes)}m. Discount is against pair destinations, not realized closes.`,
      reach_provenance:JSON.stringify(choice.reach)}:{}),
    source: 'row.layers.micro.context.beliefs: handoff and entry_license; permission is not a fill or standing-order claim',
  };
}
export function handoffApplicability(face) {
  const sides = face.legs.filter(side => face.os.some(r => r.legs?.[side]?.sentence?.handoff?.destination_kind === 'W1_CLOSE'));
  if (!sides.length) return null;
  return {status:'INAPPLICABLE', close_forecast_sides:sides,
    line:`Handoff experiment · floor-only grade inapplicable to ${sides.join(' / ')}'s close forecast.`,
    reason:'A close destination is not a remaining-floor forecast. The headline grade is the corrected W1 close-delta mark; the old floor-only letter remains diagnostic.',
    source:'Stored sentence.handoff.destination_kind = W1_CLOSE'};
}
export function labelHandoffGrade(grade, applicability) {
  if (!applicability) return grade;
  grade.applicability = applicability;
  grade.floor_only_diagnostic = {LETTER:grade.LETTER, display:grade.display};
  const safetyFailure = grade.LETTER.hard_failures.length > 0;
  const independentFailures = Object.entries(grade.LETTER.section_grades ?? {}).filter(([name,s])=>name!=='MICRO'&&s.letter==='F').map(([name])=>name);
  const knownFailure = safetyFailure || independentFailures.length > 0;
  grade.MICRO = {...grade.MICRO, applicability};
  grade.LETTER = {...grade.LETTER, letter:knownFailure?'F':'N/A',
    section_grades:{...grade.LETTER.section_grades, MICRO:{...grade.LETTER.section_grades?.MICRO,letter:'N/A',applicability}},
    governing_section:safetyFailure?grade.LETTER.governing_section:independentFailures.length?`${independentFailures.join(' · ')}; floor-only MICRO inapplicable`:applicability.line};
  grade.display = {...grade.display, letter:knownFailure?'F':'N/A', label:applicability.line,
    governing:grade.LETTER.governing_section,
    sections:grade.display.sections.map(s => s.name === 'MICRO' ? {...s,mark:'—',
      line:applicability.line, hover_lines:[applicability.reason, 'Legacy floor calculations are retained as inapplicable diagnostics, not a score.']} : s)};
  return grade;
}
export function handoffCloseResult(grade, rulers) {
  const truth = rulers.effective_truth, row = truth?.effective_row ?? {};
  const legs = Object.fromEntries(Object.entries(grade.OUTCOME.legs).map(([id, fill]) => {
    const prefix = Object.keys(row).find(key => /^leg[A-Z]$/.test(key) && row[key] === id);
    const raw = prefix ? row[`${prefix}_close_c`] : null;
    const close = raw !== null && raw !== undefined && raw !== '' && Number.isFinite(Number(raw)) ? Number(raw) : null;
    const credited = fill.filled && fill.valid_span_fill;
    const fee=credited?entryFee({event:grade.event,price:fill.cents,epoch:fill.fill_epoch}):{direct_cents:0,nondirect_cents:0,status:'UNFILLED'};
    const delta=credited?close===null?null:close-fill.cents:0;
    return [id, {close_cents:close, close_source_column:prefix ? `${prefix}_close_c` : null,
      credited_fill_cents:credited ? fill.cents : null,
      close_delta_cents:delta,fee,
      net_direct_cents:Number.isFinite(delta)&&Number.isFinite(fee.direct_cents)?delta-fee.direct_cents:null,
      net_nondirect_cents:Number.isFinite(delta)&&Number.isFinite(fee.nondirect_cents)?delta-fee.nondirect_cents:null}];
  }));
  const values = Object.values(legs), closes = values.map(leg => leg.close_cents);
  const sum = xs => xs.every(Number.isFinite) ? xs.reduce((a,b)=>a+b,0) : null;
  const closeSum = sum(closes), filledDelta = sum(values.map(leg=>leg.close_delta_cents));
  const cost = grade.OUTCOME.valid_pair_completed ? sum(values.map(leg=>leg.credited_fill_cents)) : null;
  const delta = closeSum !== null && cost !== null ? closeSum - cost : null;
  const signed = value => Number.isFinite(value) ? `${value > 0 ? '+' : ''}${value}¢` : 'no data here';
  return {role:'RULER — realized W1 closes, not a forecast or OS input', legs,
    pair_close_sum_cents:closeSum, pair_fill_sum_cents:cost, pair_delta_cents:delta,
    filled_leg_close_delta_cents:filledDelta,
    net_direct_cents:sum(values.map(v=>v.net_direct_cents)),net_nondirect_cents:sum(values.map(v=>v.net_nondirect_cents)),
    line:delta !== null ? `W1 closes ${closes.join(' + ')} = ${closeSum}¢ · pair cost ${cost}¢ · ${signed(delta)} vs closes`
      : `W1 closes ${cents(closeSum)} · pair incomplete · filled-leg close-delta ${signed(filledDelta)}`,
    provenance:{truth_commit:truth?.table_commit,corrections_commit:truth?.corrections_commit,row_sha256:truth?.row_sha256}};
}
export function labelCloseDeltaGrade(grade){
  const r=grade.handoff_close_result;if(!r)return;
  const fmt=n=>Number.isFinite(n)?`${n>0?'+':''}${Number(n.toFixed(2))}¢`:'no data here';
  const complete=grade.OUTCOME.valid_pair_completed,failures=grade.LETTER.hard_failures??[];
  const score=fmt(r.filled_leg_close_delta_cents),status=failures.length?'SAFETY FAILURE':complete?'PAIR COMPLETE':'PAIR INCOMPLETE';
  grade.close_delta_grade={kind:'NUMERIC_W1_CLOSE_DELTA',score_cents:r.filled_leg_close_delta_cents,status,letter_assigned:false,
    label:`${score} · ${status.toLowerCase()}`,safety_failures:failures,
    rule:'Credited per-leg corrected W1 close minus fill; unfilled value zero. Numeric mark, not a new letter or certification. Fees separate.'};
  grade.display={...grade.display,letter:failures.length?'F':score,label:'W1 close-delta grade',governing:`${status}. ${r.line}`,
    ruler_line:r.line,ruler_hover_lines:[r.role,JSON.stringify(r.provenance)],
    sections:[...Object.entries(r.legs).map(([id,l])=>({name:id,mark:l.credited_fill_cents!==null&&l.close_delta_cents>0?'✓':'!',
      line:`${id}: close ${l.close_cents??'unknown'}¢ − fill ${l.credited_fill_cents??'none'}${l.credited_fill_cents!==null?'¢':''} = ${fmt(l.close_delta_cents)}`,
      hover_lines:[l.credited_fill_cents===null?'Unfilled contributes zero; not a completed pair.':`Corrected close column ${l.close_source_column}`,JSON.stringify(l.fee)]})),
      {name:'PAIR',mark:complete&&r.pair_delta_cents>0?'✓':'!',line:r.line,hover_lines:[status]},
      {name:'FEES',mark:'—',line:`After entry fees: ${fmt(r.net_direct_cents)} / ${fmt(r.net_nondirect_cents)}`,hover_lines:['Direct / non-direct fee rounding; account precision unknown. No invented exit fee.']},
      {name:'SAFETY',mark:failures.length?'!':'✓',line:failures.length?failures.join(' · '):'No recorded safety failure',hover_lines:['Performance mark, not Gate-1 certification.']} ]};
}
