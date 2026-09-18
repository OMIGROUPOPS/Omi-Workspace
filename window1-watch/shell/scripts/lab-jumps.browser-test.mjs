import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';
// Usage: node scripts/lab-jumps.browser-test.mjs [base-url] [output-dir]
// Drives First bid / First fill / Bell on the two named handoff checks and
// compares every outcome-card number with the stored grade. Screenshots at Bell.
const base=(process.argv[2]??'http://127.0.0.1:8080').replace(/\/$/,''),output=process.argv[3]??'C:/tmp/lab_jumps_20260918';
fs.mkdirSync(output,{recursive:true});
const data=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../data');
const stored=name=>{const file=path.join(data,name);return JSON.parse(fs.existsSync(file)?fs.readFileSync(file):gunzipSync(fs.readFileSync(file+'.gz')))};
const signed=n=>`${n>0?'+':''}${n}¢`;
// Use the already installed browser; do not download another runtime.
const browser=await chromium.launch({headless:true,channel:'msedge'});
const page=await browser.newPage({viewport:{width:1500,height:1050}}),errors=[],report=[];
page.on('pageerror',e=>errors.push(e.message));
try{
  for(const event of ['KXATPMATCH-26JUL12ALTGAS','KXATPCHALLENGERMATCH-26JUL14LAJSVA']){
    const grade=stored(event+'.grade.json'),face=stored(event+'.face.json'),close=grade.handoff_close_result,short=event.split('-').at(-1).slice(7);
    assert(close,'Named check must store the realized-close ruler');
    const fills=face.render.fill_events.map(f=>f.receipt_index),last=(face.timeline?.receipt_storage==='columns'?face.os[0]:face.os).length-1;
    await page.goto(`${base}/?tab=lab&event=${event}`);
    const jump=id=>page.locator(`[data-jump="${id}"]`);
    await jump('bell').waitFor({timeout:90000});
    // No landmark may fall into the verified-chunk loading pause.
    const landed=async id=>{const started=Date.now();await jump(id).click();await page.locator(`[data-jump="${id}"][aria-current="true"]`).waitFor({timeout:5000});
      assert.equal(await page.getByText('Loading and verifying this part of the recorded timeline').count(),0,`${id} landed on a pending chunk`);return Date.now()-started};
    const timings={};
    timings.first_bid=await landed('first-bid');
    assert.match(await jump('first-bid').getAttribute('title'),/receipt \d+/);
    assert.equal(await page.locator('[data-bell-outcome]').count(),0,'Outcome card belongs to the bell only');
    const bidTables=await page.locator('[data-reach-table]').evaluateAll(nodes=>nodes.map(n=>({side:n.dataset.reachTable,kind:n.dataset.bidChoices??'faller',header:n.querySelector('header').innerText,rows:[...n.querySelectorAll('tbody tr')].map(r=>[...r.cells].map(c=>c.innerText))})));
    const riser=bidTables.find(t=>t.kind==='riser');
    assert(riser,'First bid must show the riser\'s candidate levels');
    assert.equal(riser.rows.filter(r=>r[3]==='chosen').length,1,'Exactly one riser candidate is the stored licensed entry');
    assert.equal(riser.rows.at(-1)[0],'wait');
    await page.screenshot({path:`${output}/${short}-first-bid.png`,fullPage:true});
    timings.first_fill=await landed('first-fill');
    assert.equal(await jump('first-fill').getAttribute('title').then(t=>Number(t.match(/receipt (\d+)/)[1])),Math.min(...fills));
    timings.bell=await landed('bell');
    assert.equal(await jump('bell').getAttribute('title').then(t=>Number(t.match(/receipt (\d+)/)[1])),last);
    const card=page.locator('[data-bell-outcome]');await card.waitFor();
    const legs=await card.locator('[data-bell-legs] tbody tr').evaluateAll(rows=>rows.map(r=>[...r.cells].map(c=>c.innerText)));
    assert.deepEqual(legs,face.legs.map(side=>{const l=close.legs[side],f=grade.OUTCOME.legs[side];
      return [side,f.filled?`${f.cents}¢${f.valid_span_fill===false?' · not credited':''}`:'no fill',`${l.close_cents}¢`,signed(l.close_delta_cents)]}));
    const pair=await card.locator('[data-bell-pair] dd').allInnerTexts();
    assert.deepEqual(pair.slice(0,3),[close.pair_fill_sum_cents==null?'pair incomplete':`${close.pair_fill_sum_cents}¢`,`${close.pair_close_sum_cents}¢`,close.pair_delta_cents==null?'pair incomplete':signed(close.pair_delta_cents)]);
    const mark=await card.locator('[data-bell-grade] b').innerText(),header=await page.locator('[data-grade-letter]').innerText();
    assert.equal(mark,signed(grade.close_delta_grade?.score_cents??close.filled_leg_close_delta_cents));
    assert.notEqual(mark,'N/A');assert.notEqual(header,'N/A');
    if(!grade.LETTER.hard_failures?.length)assert.equal(header,mark);
    await card.scrollIntoViewIfNeeded();
    await page.screenshot({path:`${output}/${short}-bell.png`,fullPage:true});
    await card.screenshot({path:`${output}/${short}-bell-card.png`});
    report.push({event,timings_ms:timings,first_bid_tables:bidTables,bell:{legs,pair,mark,header,builder_written_grade:grade.close_delta_grade!=null}});
  }
  assert.deepEqual(errors,[]);
  fs.writeFileSync(`${output}/REPORT.json`,JSON.stringify({base,report},null,1));
  console.log(JSON.stringify(report.map(r=>({event:r.event,timings_ms:r.timings_ms,bell:r.bell})),null,1));
}finally{await browser.close()}
