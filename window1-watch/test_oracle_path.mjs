import assert from "node:assert/strict";
import test from "node:test";
import { buildOraclePath, remainingFloors } from "./oracle_path.mjs";
import { readGradePrints } from "./grade_prints.mjs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

test("strict future: corrected span, equal-time print, bell, empty tail", () => {
  const prints = [{epoch: 1,price: 1},{epoch: 3,price: 9},{epoch: 4,price: 10},
    {epoch: 4,price: 11},{epoch: 8,price: 12},{epoch: 9,price: 0},{epoch: 10,price: 0}];
  assert.deepEqual(remainingFloors(prints, [1,2,3,4,8,9,10],2,8,9), [null,9,10,12,null,null,null]);
});
function fixture() {
  return { legs: ["A","B"], provenance: {event_id:"TEST"},
    bell: {timestamp_epoch:10,t:10/3600}, first_tick: {epoch:2},
    truth: {status:"OK",span_start_epoch:1,span_end_epoch:10,bell_epoch:10},
    render: {inspection_axis:{start_minutes_to_bell:1}}, os: [
      {kind:"DECISION_STAGE",receipt:"start",t:2/3600,index:0,legs:{A:{sentence:{Q:8,q_author:"POOL_BASE"},
        pool_cascade:{selected_layer:"BASE",layers:{BASE:{ess:12},"STEP-FORECAST":{ess:99}}}},B:{sentence:{Q:null}}}},
      {kind:"FILL_EVENT",receipt:"fill",t:4/3600,index:1,legs:{A:{fill:{cents:8}}}},
      {kind:"DECISION_STAGE",receipt:"end",t:5/3600,index:2,legs:{A:{sentence:{Q:null}},B:{sentence:{Q:7}}}},
    ] };
}
test("all receipts, author ESS, exact renewal, signed fill gap, null Q, no OS mutation", () => {
  const face=fixture(), before=JSON.stringify(face);
  const input={prints:{provenance:{sha256:"tape"},legs:{A:[{epoch:4,price:7},{epoch:7,price:9}],B:[{epoch:6,price:6}]},
    receipts:[{epoch:4,receipt:"fill"}]},bookReceipts:[{epoch:3,receipt:"book"},{epoch:3.5,receipt:"unchanged-book"}],
    accountability:[{kind:"BID_RENEWAL",phase:"TICK",tick_receipt:"book",timestamp_epoch:3,leg_id:"A",status:"PENDING"}]};
  const {summary,detail}=buildOraclePath(face,input);
  assert.equal(detail.ticks.length,5); // duplicate fill identity counted once
  const profiles=detail.legs.A.values.map(v=>detail.legs.A.profiles[v[0]]);
  assert.equal(profiles[1].ess,12); assert.equal(profiles[1].renewal_status,"PENDING");
  assert.equal(profiles[2].renewal_status,null); assert.equal(profiles[3].gap,-1);
  assert.equal(profiles[4].Q,null); assert.equal(profiles[4].gap,null);
  assert.equal(summary.legs.A.at_fill_gap_cents,-1);
  assert.equal(summary.legs.A.comparable_receipts,4);
  assert.equal(summary.legs.A.mean_absolute_gap_cents,1);
  assert.equal(JSON.stringify(face),before);
});
test("unverified span stays silent", () => {
  const f=fixture();f.truth.status="STORE_SILENT";f.truth.reason="NO_FORMATION";
  const result=buildOraclePath(f,{prints:{provenance:{}},bookReceipts:[]});
  assert.equal(result.detail,null);assert.match(result.summary.legs.A.hud_line,/NO_FORMATION/);
});
test("no comparable receipt has null statistics, not fabricated zero error", () => {
  const result=buildOraclePath(fixture(),{prints:{provenance:{},legs:{A:[],B:[]}},bookReceipts:[]});
  assert.equal(result.summary.legs.A.mean_absolute_gap_cents,null);
  assert.equal(result.summary.legs.A.widest_absolute_gap_cents,null);
});
test("zero-size/non-true prints remain receipt positions but never floor witnesses", async () => {
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),"oracle-test-"));
  try {
    const file=path.join(dir,"prints.jsonl"), common={ticker:"TEST-A",exchange_ts:"2026-01-01T00:00:00Z",true_print:true};
    await fs.writeFile(file,[{...common,price_cents:1,size:0,receipt_id:"zero"},
      {...common,price_cents:2,size:1,true_print:false,receipt_id:"book"},
      {...common,price_cents:3,size:1,receipt_id:"real"}].map(JSON.stringify).join("\n"));
    const result=await readGradePrints(file,[{event:"TEST",legs:["A"]}],{includeReceipts:true});
    assert.equal(result.TEST.receipts.length,3);assert.equal(result.TEST.legs.A.length,1);
    assert.equal(result.TEST.legs.A[0].price,3);
  } finally { await fs.rm(dir,{recursive:true}); }
});
