// Public fee schedule effective 2026-07-07, audited 2026-09-16; evidence and
// historical series changes: arb-executor/analysis/tennis_fees_20260916/.
// One integer-cent contract per leg in these benches. Entry fees only: marking
// to W1 close is NOT an executed exit and carries no invented exit fee.
import assert from 'node:assert/strict';
const makerSeries=new Set(['KXATPMATCH','KXWTAMATCH']);
const zeroMakerSeries=new Set(['KXATPCHALLENGERMATCH','KXWTACHALLENGERMATCH','KXITFMATCH']);
export function entryFee({event,price,quantity=1,execution='MAKER',epoch=null}){
 const series=event?.split('-')[0],known=makerSeries.has(series)||zeroMakerSeries.has(series);
 if(!known||!Number.isInteger(price)||price<=0||price>=100||!Number.isInteger(quantity)||quantity<=0)return {status:'UNKNOWN',series,direct_cents:null,nondirect_cents:null};
 if(makerSeries.has(series)&&Number.isFinite(epoch)&&epoch<Date.parse('2025-11-15T08:00:00Z')/1000)return {status:'HISTORICAL_RATE_UNVERIFIED',series,direct_cents:null,nondirect_cents:null};
 assert(['MAKER','TAKER_ASK'].includes(execution),'UNKNOWN_EXECUTION_ROUTE');
 // Integer rational arithmetic, hundredths of a cent: 0.0175/0.07 dollars
 // times p(1-p), with p=price/100, converted to dollars/10,000 units.
 const coefficient=execution==='TAKER_ASK'?700:makerSeries.has(series)?175:0;
 const numerator=BigInt(coefficient)*BigInt(quantity)*BigInt(price)*BigInt(100-price),denominator=10000n;
 const direct=Number((numerator+denominator-1n)/denominator)/100;
 const nonDenominator=denominator*100n,nondirect=Number((numerator+nonDenominator-1n)/nonDenominator);
 return {status:'SCHEDULE_ESTIMATE',series,execution,quantity,direct_cents:direct,nondirect_cents:nondirect,
  schedule:'https://kalshi.com/docs/kalshi-fee-schedule.pdf',rounding:'https://docs.kalshi.com/getting_started/fee_rounding',rate_model:coefficient===0?'ZERO_MAKER':execution==='MAKER'?'0.0175*C*p*(1-p) dollars':'0.07*C*p*(1-p) dollars',account_precision_unverified:true};
}
const sum=a=>a.some(v=>v===null)?null:Math.round(a.reduce((s,v)=>s+v,0)*100)/100;
export function feeRestatement(row,fills=[]){
 const legs=row.legs.map(l=>{const f=fills.find(f=>(f.leg??f.id)===l.id),fee=l.filled===false?{status:'UNFILLED',direct_cents:0,nondirect_cents:0}:l.filled===null?{status:'UNKNOWN',direct_cents:null,nondirect_cents:null}:entryFee({event:row.event,price:l.fill_cents,epoch:l.fill_epoch,execution:f?.execution??'MAKER'});
  return {...l,fee,entry_fee_cents:fee.direct_cents,entry_fee_nondirect_cents:fee.nondirect_cents,
   net_value_cents:l.value_cents===null||fee.direct_cents===null?null:Math.round((l.value_cents-fee.direct_cents)*100)/100,
   net_value_nondirect_cents:l.value_cents===null||fee.nondirect_cents===null?null:Math.round((l.value_cents-fee.nondirect_cents)*100)/100};});
 return {...row,legs,entry_fee_cents:sum(legs.map(l=>l.entry_fee_cents)),entry_fee_nondirect_cents:sum(legs.map(l=>l.entry_fee_nondirect_cents)),net_value_cents:sum(legs.map(l=>l.net_value_cents)),net_value_nondirect_cents:sum(legs.map(l=>l.net_value_nondirect_cents)),fee_basis:'One-contract entry-fee schedule estimate; direct and non-direct precision scenarios, no account rebate/FCM charge inferred. Gross W1 mark retained; no invented exit.'};
}
