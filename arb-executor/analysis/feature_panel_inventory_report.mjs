// Presentation-only concatenation of hash-verified public results.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'feature_panel_inventory_v2');
const read=(dir,name)=>JSON.parse(readFileSync(resolve(root,dir,name)));
const main=read('ATP_MAIN','LINEAGE_COVERAGE.json'),chall=read('ATP_CHALL_PASS1','LINEAGE_COVERAGE.json');
const lines=['# Eleven-block screen — operator publication','',
  'MAIN: both full screens deterministic; unchanged FIRST parity exact. CHALL: completed pass 1, determinism pending; second pass remains running. This is GATE-SIM, not receipt-cadence proof. No engine edits or replay.','',
  '## Lineage coverage first','',
  'Percent of PRIMARY side/gate receipts with a recorded feature. Columns are April / May / June / July. Numeric zero counts as observed. Unknown WS availability is not zero. Counts, sources and per-feature leakage exclusions are in each LINEAGE_COVERAGE.json. CHALL coverage belongs to its completed first pass.','',
  '| Field | MAIN Apr | May | Jun | Jul | CHALL Apr | May | Jun | Jul |',
  '|---|---:|---:|---:|---:|---:|---:|---:|---:|'];
for(const field of main.fields){
  const values=[main,chall].flatMap(tour=>['04','05','06','07'].map(month=>{
    const r=tour.coverage_by_month.find(r=>r.field===field.name&&r.month===`2026-${month}`);
    return r.unknown_receipts===r.eligible_receipts?'unknown':(100*r.available_share).toFixed(1);
  }));
  lines.push(`| ${field.name} | ${values.join(' | ')} |`);
}
lines.push('','Bell-source publication clocks are unverified and excluded as predictors. Observed wake is left-censored when capture begins awake. Cadence is causal-prefix, not full-span. Quote velocities are quote-price changes, not measured consumption. API direction is authoritative; arithmetic-only never fills flow. Maker residuals fail closed on uncertain ordering/consumed-side attribution; zero-execution refill is missing. Queue is displayed depth at unchanged FIRST Q, not queue priority. WS is deferred, not recovered. June freezes both member universe and learned parameters and cannot select finalists.','');
for(const dir of ['ATP_MAIN','ATP_CHALL_PASS1']) lines.push(readFileSync(resolve(root,dir,'SUMMARY.md'),'utf8'));
lines.push('## Astra’s verdict','',
  'REJECT promotion of any block into the OS on this screen. MAIN is verified and has no qualifying side/gate cell. CHALL pass 1 also has none, but its scientific verdict remains provisional until the second pass agrees. MAIN C1/C2 move average floor error by about one-thousandth of a cent; the full eleven-block fit falls back to FIRST. The observed flow and maker readings should be visible as readings, not represented as authors. Missing May books, nearly absent refill denominators and June/July open interest, plus deferred WS, mean “all inventory recovered” would be false. This rejects this learned likelihood test, not the usefulness of book behavior in principle. It does not identify an irreducible tape ceiling; FIRST’s attained errors are measured performance, not a floor on possible error. No full-cadence finalist is authorized.','',
  '## LAB integration','',
  'Five compact, face/OS/trace-bound pressure assets read the existing local decision stages. All decision stages are present: GIUBAR 246, LAJSVA 135, URSPAL 1216, ALTGAS 169, DANPRA 118. Volume, print counts, displayed book sizes, pair midpoint sum and selected-pool call are stored values. API flow, maker pressure/refill, queue-at-Q and open interest have no exact joined source in these named replays and display “no data here”. Library averages are never substituted. Carried state is explicitly labeled “Last recorded receipt”. Grades, oracle and engine bytes stay unchanged.');
writeFileSync(resolve(root,'OPERATOR_REPORT.md'),lines.join('\n')+'\n');
console.log(resolve(root,'OPERATOR_REPORT.md'));
